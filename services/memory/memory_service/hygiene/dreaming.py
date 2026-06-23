"""Dreaming pipeline.

Run nightly (and on demand by the Memory Steward agent) to replay episodic
memories, extract patterns, promote to semantic/procedural, consolidate,
decay, build hierarchical summaries, and project insights into the KG.

This module defines the **stages** and orchestrates them; the actual LLM
calls and KG writes are filled in by sub-agent 04 in coordination with 05.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from schemas.memory import MemoryHealthReport, MemoryRecord

from ..stores.repository import MemoryRepository
from .consolidation import find_near_duplicates
from .selective_forgetting import should_archive


@dataclass
class DreamWindow:
    learner_id: str
    start: datetime
    end: datetime


async def gather_window(repo: MemoryRepository, *, learner_id: str, hours: int) -> tuple[DreamWindow, list[MemoryRecord]]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    rows = [r async for r in _iter_window(repo, learner_id=learner_id, start=start, end=end)]
    return DreamWindow(learner_id=learner_id, start=start, end=end), rows


async def _iter_window(repo: MemoryRepository, *, learner_id: str, start: datetime, end: datetime):
    for row in await repo.iter_for_learner(learner_id):
        if start <= row.created_at <= end:
            yield row


async def dream(
    repo: MemoryRepository,
    *,
    learner_id: str,
    window_hours: int,
    consolidation_cosine: float,
    archive_threshold: float,
) -> MemoryHealthReport:
    """Run a full dreaming pass.

    Phase 0 wires the stages with safe defaults; sub-agent 04 plugs in:

    - clustering (KG-assisted)
    - LLM pattern extraction (Claude + instructor)
    - semantic/procedural/reflective writes
    - KG projection (delegating to KG Builder agent)
    - hierarchical summary refresh
    """

    window, rows = await gather_window(repo, learner_id=learner_id, hours=window_hours)
    promoted = 0  # sub-agent 04: count semantic/procedural promotions
    merged = 0  # sub-agent 04: count merges from consolidation
    archived = 0
    conflicts_resolved = 0
    conflicts_pending = 0

    # Consolidation pass.
    dup_candidates = await find_near_duplicates(repo, learner_id=learner_id, cosine=consolidation_cosine)
    merged += len(dup_candidates)

    # Decay / archive sweep.
    for row in rows:
        if should_archive(row, threshold=archive_threshold):
            row.archived_at = datetime.now(timezone.utc)
            await repo.upsert(row)
            archived += 1

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
