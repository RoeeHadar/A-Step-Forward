"""Periodic verification of high-stakes semantic memories."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from schemas.memory import MemoryRecord, MemoryType

from ..settings import MemorySettings
from ..stores.repository import MemoryRepository


def needs_verification(
    record: MemoryRecord,
    *,
    min_salience: float = 0.6,
    max_age_days: int = 60,
) -> bool:
    if record.type not in {MemoryType.SEMANTIC, MemoryType.PROCEDURAL}:
        return False
    if record.deleted_at or record.archived_at or record.superseded_by:
        return False
    if record.salience < min_salience:
        return False
    age = datetime.now(timezone.utc) - (record.last_accessed_at or record.created_at)
    return age > timedelta(days=max_age_days)


def verification_prompt(record: MemoryRecord) -> str:
    return f"I think this is still true: \"{record.content}\" — is that correct?"


async def collect_verification_candidates(
    repo: MemoryRepository,
    *,
    learner_id: str,
    settings: MemorySettings | None = None,
    limit: int = 5,
) -> list[MemoryRecord]:
    cfg = settings or MemorySettings()
    records = await repo.list_by_types(learner_id, {MemoryType.SEMANTIC, MemoryType.PROCEDURAL})
    candidates = [
        r
        for r in records
        if needs_verification(
            r,
            min_salience=cfg.verification_min_salience,
            max_age_days=cfg.verification_max_age_days,
        )
    ]
    candidates.sort(key=lambda r: r.salience, reverse=True)
    return candidates[:limit]
