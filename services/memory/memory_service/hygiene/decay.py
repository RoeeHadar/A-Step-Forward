"""Decay & reinforcement.

Effective strength is `salience × exp(-(now - last_accessed) / tau_days)` with
each access reinforcing salience and refreshing `last_accessed`. Memories with
strength below `archive_threshold` are archived (not deleted) by the
`decay_sweep` worker.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from schemas.memory import MemoryRecord

SECONDS_PER_DAY = 86_400.0


def strength_now(record: MemoryRecord, *, now: datetime | None = None) -> float:
    """Compute effective memory strength at `now`."""
    now = now or datetime.now(timezone.utc)
    last = record.last_accessed_at or record.created_at
    elapsed_days = max(0.0, (now - last).total_seconds() / SECONDS_PER_DAY)
    tau = max(0.5, float(record.decay_tau_days))
    return float(record.salience) * math.exp(-elapsed_days / tau)


def reinforce(record: MemoryRecord, *, delta: float = 0.05) -> MemoryRecord:
    """Increase salience and refresh last_accessed_at upon access."""
    record.salience = min(1.0, record.salience + delta)
    record.access_count += 1
    record.last_accessed_at = datetime.now(timezone.utc)
    return record
