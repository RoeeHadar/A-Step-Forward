"""Hierarchical compression / summarization."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pydantic import BaseModel, Field
from schemas._compat import StrEnum
from schemas.common import Provenance
from schemas.memory import MemoryRecord, MemoryType

from ..stores.repository import MemoryRepository


class SummaryLayer(StrEnum):
    VERBATIM = "verbatim"
    DAILY = "daily"
    WEEKLY = "weekly"
    LIFETIME = "lifetime"


class HierarchicalSummary(BaseModel):
    learner_id: str
    layer: SummaryLayer
    window_start: datetime
    window_end: datetime
    facts: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    refreshed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def layer_for_age(created_at: datetime, *, now: datetime | None = None) -> SummaryLayer:
    now = now or datetime.now(timezone.utc)
    age = now - created_at
    if age < timedelta(days=1):
        return SummaryLayer.VERBATIM
    if age < timedelta(days=30):
        return SummaryLayer.DAILY
    if age < timedelta(days=365):
        return SummaryLayer.WEEKLY
    return SummaryLayer.LIFETIME


def build_summary_from_records(
    records: list[MemoryRecord],
    *,
    learner_id: str,
    layer: SummaryLayer,
    window_start: datetime,
    window_end: datetime,
) -> HierarchicalSummary:
    facts: list[str] = []
    decisions: list[str] = []
    open_questions: list[str] = []

    for record in records:
        text = record.content.strip()
        if not text:
            continue
        lower = text.lower()
        if "?" in text:
            open_questions.append(text)
        elif any(kw in lower for kw in ("decided", "will use", "plan to", "chose")):
            decisions.append(text)
        else:
            facts.append(text)

    return HierarchicalSummary(
        learner_id=learner_id,
        layer=layer,
        window_start=window_start,
        window_end=window_end,
        facts=facts[:50],
        decisions=decisions[:20],
        open_questions=open_questions[:20],
    )


def summary_to_memory_record(summary: HierarchicalSummary) -> MemoryRecord:
    body = {
        "facts": summary.facts,
        "decisions": summary.decisions,
        "open_questions": summary.open_questions,
    }
    import json

    content = json.dumps(body, ensure_ascii=False)
    return MemoryRecord(
        id=str(uuid4()),
        learner_id=summary.learner_id,
        type=MemoryType.REFLECTIVE,
        content=content,
        summary=f"Hierarchical {summary.layer.value} digest",
        tags=[f"hierarchical:{summary.layer.value}"],
        salience=0.55,
        confidence=0.6,
        provenance=Provenance(kind="agent_reflection", id=summary.layer.value, agent="memory_steward", model="none"),
        created_at=summary.refreshed_at,
        updated_at=summary.refreshed_at,
    )


async def refresh_layer_summary(
    repo: MemoryRepository,
    *,
    learner_id: str,
    layer: SummaryLayer,
    now: datetime | None = None,
) -> MemoryRecord | None:
    """Build and persist a hierarchical summary for the given layer window."""
    now = now or datetime.now(timezone.utc)
    if layer == SummaryLayer.VERBATIM:
        window_start = now - timedelta(hours=24)
    elif layer == SummaryLayer.DAILY:
        window_start = now - timedelta(days=30)
    elif layer == SummaryLayer.WEEKLY:
        window_start = now - timedelta(days=365)
    else:
        window_start = datetime(1970, 1, 1, tzinfo=timezone.utc)

    episodic = await repo.list_by_types(learner_id, {MemoryType.EPISODIC})
    in_window = [r for r in episodic if window_start <= r.created_at <= now and not r.archived_at]
    if not in_window:
        return None

    summary = build_summary_from_records(
        in_window,
        learner_id=learner_id,
        layer=layer,
        window_start=window_start,
        window_end=now,
    )
    record = summary_to_memory_record(summary)
    return await repo.upsert(record)
