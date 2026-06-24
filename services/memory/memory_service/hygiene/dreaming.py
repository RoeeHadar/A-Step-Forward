"""Dreaming pipeline.

Run nightly (and on demand by the Memory Steward agent) to replay episodic
memories, extract patterns, promote to semantic/procedural, consolidate,
decay, build hierarchical summaries, and project insights into the KG.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from schemas.common import Provenance
from schemas.memory import MemoryHealthReport, MemoryRecord, MemoryType

from ..settings import MemorySettings
from ..stores.repository import MemoryRepository
from .consolidation import find_near_duplicates
from .llm_helper import dream_llm_complete
from .selective_forgetting import should_archive

logger = logging.getLogger(__name__)


@dataclass
class DreamWindow:
    learner_id: str
    start: datetime
    end: datetime


async def gather_window(
    repo: MemoryRepository, *, learner_id: str, hours: int
) -> tuple[DreamWindow, list[MemoryRecord]]:
    end = datetime.now(UTC)
    start = end - timedelta(hours=hours)
    rows = [r async for r in _iter_window(repo, learner_id=learner_id, start=start, end=end)]
    return DreamWindow(learner_id=learner_id, start=start, end=end), rows


async def _iter_window(
    repo: MemoryRepository, *, learner_id: str, start: datetime, end: datetime
):
    for row in await repo.iter_for_learner(learner_id):
        if start <= row.created_at <= end:
            yield row


def _keyword_clusters(records: list[MemoryRecord]) -> list[list[MemoryRecord]]:
    """Cluster records by shared keywords (simple heuristic)."""
    stop = {"the", "a", "an", "is", "in", "on", "at", "to", "of", "and", "or", "for", "with"}

    def keywords(text: str) -> set[str]:
        return {w for w in text.lower().split() if len(w) > 3 and w not in stop}

    clusters: list[list[MemoryRecord]] = []
    assigned: set[str] = set()

    for record in records:
        if record.id in assigned:
            continue
        kw_a = keywords(record.content)
        cluster = [record]
        assigned.add(record.id)
        for other in records:
            if other.id in assigned:
                continue
            kw_b = keywords(other.content)
            if kw_a and kw_b and len(kw_a & kw_b) >= 2:
                cluster.append(other)
                assigned.add(other.id)
        clusters.append(cluster)

    return clusters


async def _consolidate_cluster_with_llm(
    records: list[MemoryRecord],
    *,
    learner_id: str,
    settings: MemorySettings | None = None,
) -> MemoryRecord | None:
    """Call Groq to produce a single semantic memory from a cluster."""
    memory_texts = "\n".join(f"- [{r.type}] {r.content}" for r in records)
    prompt = (
        "You are a Memory Steward. Given these episodic memories from a learner's "
        "study sessions, write ONE concise semantic memory that captures the enduring "
        "insight or pattern. Be specific and factual. Output ONLY the memory content, "
        "no preamble, no JSON, no bullets — just a plain sentence or two.\n\n"
        f"Memories:\n{memory_texts}"
    )

    try:
        content = await dream_llm_complete(prompt, settings=settings)
        if not content:
            return None

        return MemoryRecord(
            id=str(uuid.uuid4()),
            learner_id=learner_id,
            type=MemoryType.SEMANTIC,
            content=content,
            summary=f"Synthesized from {len(records)} episodic memories by dreamer.",
            provenance=Provenance(
                kind="agent_reflection",
                id="dreamer",
                agent="dreamer",
                model="llama-3.3-70b-versatile",
            ),
            confidence=0.75,
            salience=0.6,
            created_at=datetime.now(UTC),
            tags=["dreamer", "synthesized"],
        )
    except Exception:
        logger.exception("dreamer.consolidate_cluster failed")
        return None


async def dream(
    repo: MemoryRepository,
    *,
    learner_id: str,
    window_hours: int,
    consolidation_cosine: float,
    archive_threshold: float,
    settings: MemorySettings | None = None,
) -> MemoryHealthReport:
    """Run a full dreaming pass with LLM-based semantic consolidation."""
    cfg = settings or getattr(repo, "settings", None) or MemorySettings()
    window, rows = await gather_window(repo, learner_id=learner_id, hours=window_hours)
    promoted = 0
    merged = 0
    archived = 0
    conflicts_resolved = 0
    conflicts_pending = 0

    # LLM-based pattern extraction and semantic promotion
    episodic_rows = [r for r in rows if r.type == MemoryType.EPISODIC]
    if episodic_rows and cfg.groq_api_key:
        clusters = _keyword_clusters(episodic_rows)
        for cluster in clusters:
            if len(cluster) < 2:
                continue
            synthetic = await _consolidate_cluster_with_llm(
                cluster, learner_id=learner_id, settings=cfg
            )
            if synthetic is not None:
                try:
                    await repo.upsert(synthetic)
                    promoted += 1
                except Exception:
                    logger.exception("dreamer.upsert_synthetic failed")

    # Consolidation pass (merge near-duplicate semantics)
    dup_candidates = await find_near_duplicates(
        repo, learner_id=learner_id, cosine=consolidation_cosine
    )
    merged += len(dup_candidates)

    # Decay / archive sweep
    for row in rows:
        if should_archive(row, threshold=archive_threshold):
            row.archived_at = datetime.now(UTC)
            try:
                await repo.upsert(row)
                archived += 1
            except Exception:
                logger.exception("dreamer.archive failed for %s", row.id)

    return MemoryHealthReport(
        learner_id=learner_id,
        window_start=window.start,
        window_end=window.end,
        items_reviewed=len(rows),
        items_promoted=promoted,
        items_archived=archived,
        items_merged=merged,
        conflicts_resolved=conflicts_resolved,
        conflicts_pending=conflicts_pending,
        coverage_gaps=[],
        drift_notes=[],
    )
