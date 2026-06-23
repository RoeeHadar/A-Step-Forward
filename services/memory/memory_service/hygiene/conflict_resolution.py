"""Conflict resolution — version contradictions via superseded_by, never overwrite."""

from __future__ import annotations

from datetime import datetime, timezone

from schemas.memory import MemoryConflict, MemoryRecord, MemoryType

from ..settings import MemorySettings
from ..stores.repository import MemoryRepository
from .text_similarity import jaccard_similarity, likely_contradiction


_CONFLICT_TYPES = {MemoryType.SEMANTIC, MemoryType.PROCEDURAL}


def resolution_score(record: MemoryRecord, *, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    age_days = max(0.0, (now - record.created_at).total_seconds() / 86_400.0)
    recency = 1.0 / (1.0 + age_days / 30.0)
    user_trust = 1.0 if record.provenance.kind in {"verification", "chat"} else 0.85
    return record.confidence * recency * user_trust


async def find_contradiction(
    repo: MemoryRepository,
    incoming: MemoryRecord,
    *,
    settings: MemorySettings | None = None,
) -> MemoryRecord | None:
    if incoming.type not in _CONFLICT_TYPES:
        return None

    cfg = settings or MemorySettings()
    candidates = await repo.list_by_types(incoming.learner_id, _CONFLICT_TYPES)
    best: MemoryRecord | None = None
    best_overlap = 0.0

    for existing in candidates:
        if existing.id == incoming.id or existing.superseded_by:
            continue
        if existing.type != incoming.type:
            continue
        overlap = jaccard_similarity(incoming.content, existing.content)
        if overlap < 0.25 and not likely_contradiction(incoming.content, existing.content):
            continue
        if likely_contradiction(incoming.content, existing.content) or overlap >= cfg.consolidation_dup_cosine:
            if overlap > best_overlap:
                best = existing
                best_overlap = overlap

    if best is None:
        return None
    if likely_contradiction(incoming.content, best.content):
        return best
    return None


async def resolve_conflicts(
    repo: MemoryRepository,
    incoming: MemoryRecord,
    *,
    settings: MemorySettings | None = None,
) -> MemoryConflict | None:
    existing = await find_contradiction(repo, incoming, settings=settings)
    if existing is None:
        return None

    now = datetime.now(timezone.utc)
    incoming_score = resolution_score(incoming, now=now)
    existing_score = resolution_score(existing, now=now)

    if incoming_score >= existing_score:
        existing.superseded_by = incoming.id
        existing.superseded_at = now
        await repo.upsert(existing)
        resolution = "incoming_supersedes"
        rationale = "Incoming memory has higher recency × confidence × trust."
    else:
        incoming.superseded_by = existing.id
        incoming.superseded_at = now
        resolution = "existing_supersedes"
        rationale = "Existing memory has higher recency × confidence × trust."

    return MemoryConflict(
        incoming=incoming,
        existing=existing,
        resolution=resolution,  # type: ignore[arg-type]
        rationale=rationale,
    )
