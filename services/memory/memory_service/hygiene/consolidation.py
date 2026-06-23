"""Consolidation — merge near-duplicate memories with provenance preserved."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from schemas.memory import MemoryRecord, MemoryType

from ..stores.repository import MemoryRepository
from .text_similarity import cosine_similarity_vectors, jaccard_similarity, likely_contradiction


@dataclass
class DuplicateCandidate:
    a: MemoryRecord
    b: MemoryRecord
    cosine: float


def _similarity(a: MemoryRecord, b: MemoryRecord, *, embedding_a: list[float] | None, embedding_b: list[float] | None) -> float:
    if embedding_a is not None and embedding_b is not None:
        return cosine_similarity_vectors(embedding_a, embedding_b)
    return jaccard_similarity(a.content, b.content)


async def find_near_duplicates(
    repo: MemoryRepository,
    *,
    learner_id: str,
    cosine: float,
    memory_types: set[MemoryType] | None = None,
) -> list[DuplicateCandidate]:
    types = memory_types or {MemoryType.SEMANTIC, MemoryType.PROCEDURAL}
    records = await repo.list_by_types(learner_id, types)
    active = [r for r in records if not r.superseded_by and not r.archived_at]

    embeddings: dict[str, list[float] | None] = {}
    for record in active:
        embeddings[record.id] = await _fetch_embedding(repo, record)

    seen: set[tuple[str, str]] = set()
    candidates: list[DuplicateCandidate] = []

    for i, a in enumerate(active):
        for b in active[i + 1 :]:
            if a.type != b.type:
                continue
            pair = tuple(sorted((a.id, b.id)))
            if pair in seen:
                continue
            sim = _similarity(a, b, embedding_a=embeddings[a.id], embedding_b=embeddings[b.id])
            if sim >= cosine and not likely_contradiction(a.content, b.content):
                seen.add(pair)
                candidates.append(DuplicateCandidate(a=a, b=b, cosine=sim))
    return candidates


async def merge(repo: MemoryRepository, candidate: DuplicateCandidate) -> MemoryRecord:
    """Merge `b` into `a` (canonical). `b` is marked superseded; provenance retained in summary."""
    canonical, duplicate = candidate.a, candidate.b
    if resolution_key(duplicate) > resolution_key(canonical):
        canonical, duplicate = duplicate, canonical

    merged_tags = sorted(set(canonical.tags) | set(duplicate.tags))
    provenance_note = (
        f"Merged from {duplicate.id} (agent={duplicate.provenance.agent}, "
        f"kind={duplicate.provenance.kind}) at {datetime.now(timezone.utc).isoformat()}"
    )
    summary_parts = [p for p in (canonical.summary, duplicate.summary, provenance_note) if p]
    canonical.summary = " | ".join(summary_parts)
    canonical.tags = merged_tags
    canonical.salience = min(1.0, max(canonical.salience, duplicate.salience))
    canonical.confidence = min(1.0, (canonical.confidence + duplicate.confidence) / 2.0 + 0.05)
    canonical.access_count += duplicate.access_count
    canonical.updated_at = datetime.now(timezone.utc)

    duplicate.superseded_by = canonical.id
    duplicate.superseded_at = datetime.now(timezone.utc)

    await repo.upsert(canonical)
    await repo.upsert(duplicate)
    return canonical


def resolution_key(record: MemoryRecord) -> float:
    return record.salience * record.confidence


async def consolidate_learner(
    repo: MemoryRepository,
    *,
    learner_id: str,
    cosine: float,
) -> int:
    dups = await find_near_duplicates(repo, learner_id=learner_id, cosine=cosine)
    for candidate in dups:
        await merge(repo, candidate)
    return len(dups)


async def _fetch_embedding(repo: MemoryRepository, record: MemoryRecord) -> list[float] | None:
    getter = getattr(repo, "get_embedding", None)
    if callable(getter):
        return await getter(record.id, memory_type=record.type)

    from ..stores.type_repositories import repo_for_type

    session = getattr(repo, "_external_session", None)
    if session is not None:
        return await repo_for_type(session, record.type).get_embedding(record.id)

    settings = getattr(repo, "settings", None)
    if settings is None:
        return None

    from ..stores.database import session_scope

    async with session_scope(settings) as scoped:
        return await repo_for_type(scoped, record.type).get_embedding(record.id)
