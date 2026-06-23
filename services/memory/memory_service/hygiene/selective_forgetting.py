"""Selective forgetting — archive weak memories; hard delete only on request."""

from __future__ import annotations

from schemas.memory import MemoryRecord

from ..stores.repository import MemoryRepository
from .decay import strength_now


def should_archive(record: MemoryRecord, *, threshold: float) -> bool:
    if record.deleted_at or record.archived_at or record.superseded_by:
        return False
    return strength_now(record) < threshold


async def run_forgetting_sweep(
    repo: MemoryRepository,
    *,
    learner_id: str | None,
    threshold: float,
) -> int:
    """Archive all memories below effective-strength threshold."""
    return await repo.archive_below_threshold(learner_id=learner_id, threshold=threshold)
