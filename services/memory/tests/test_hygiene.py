"""Unit tests for memory hygiene (no Postgres required)."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "memory"))

from schemas.common import Provenance
from schemas.memory import MemoryRecord, MemoryType

from memory_service.hygiene.compaction import compact_context
from memory_service.hygiene.conflict_resolution import resolve_conflicts
from memory_service.hygiene.consolidation import DuplicateCandidate, find_near_duplicates, merge
from memory_service.hygiene.decay import reinforce, strength_now
from memory_service.hygiene.importance import decay_tau_for_importance, score_importance
from memory_service.hygiene.pii import redact
from memory_service.hygiene.text_similarity import jaccard_similarity, likely_contradiction
from memory_service.hygiene.verification import needs_verification, verification_prompt
from schemas.memory import CompactionInput


class InMemoryRepo:
    def __init__(self) -> None:
        self.rows: dict[str, MemoryRecord] = {}

    async def upsert(self, record: MemoryRecord, *, embedding: list[float] | None = None) -> MemoryRecord:
        self.rows[record.id] = record
        return record

    async def list_by_types(self, learner_id: str, types: set[MemoryType]) -> list[MemoryRecord]:
        return [r for r in self.rows.values() if r.learner_id == learner_id and r.type in types]


def _record(content: str, *, memory_type: MemoryType = MemoryType.SEMANTIC, learner_id: str = "l1") -> MemoryRecord:
    return MemoryRecord(
        id=str(uuid4()),
        learner_id=learner_id,
        type=memory_type,
        content=content,
        provenance=Provenance(kind="chat", id="t1", agent="tutor", model="test"),
    )


@pytest.mark.asyncio
async def test_pii_redacts_email_phone_ssn() -> None:
    raw = "Contact me at alice@school.edu or 555-123-4567. SSN 123-45-6789."
    cleaned = await redact(raw)
    assert "alice@school.edu" not in cleaned
    assert "123-45-6789" not in cleaned
    assert "[EMAIL]" in cleaned
    assert "[SSN]" in cleaned


@pytest.mark.asyncio
async def test_importance_boosted_by_hint_and_keywords() -> None:
    low = await score_importance("ok")
    high = await score_importance("Important: learner goal for midterm exam", hint=0.9)
    assert high > low
    assert decay_tau_for_importance(high, base_tau=14.0) > decay_tau_for_importance(low, base_tau=14.0)


def test_contradiction_heuristic() -> None:
    a = "Learner prefers visual explanations for geometry."
    b = "Learner does not prefer visual explanations for geometry."
    assert likely_contradiction(a, b)
    assert jaccard_similarity(a, b) > 0.3


@pytest.mark.asyncio
async def test_conflict_resolution_supersedes_loser() -> None:
    repo = InMemoryRepo()
    existing = _record("Learner prefers reading definitions first.")
    existing.confidence = 0.4
    existing.created_at = datetime.now(timezone.utc) - timedelta(days=30)
    await repo.upsert(existing)

    incoming = _record("Learner does not prefer reading definitions first.")
    incoming.confidence = 0.85
    conflict = await resolve_conflicts(repo, incoming)
    assert conflict is not None
    assert existing.superseded_by == incoming.id or incoming.superseded_by == existing.id


@pytest.mark.asyncio
async def test_consolidation_merges_near_duplicates() -> None:
    repo = InMemoryRepo()
    a = _record("Learner enjoys geometry puzzles and visual proofs.")
    b = _record("Learner enjoys geometry puzzles and likes visual proofs.")
    await repo.upsert(a)
    await repo.upsert(b)

    dups = await find_near_duplicates(repo, learner_id="l1", cosine=0.5)
    assert len(dups) >= 1
    merged = await merge(repo, dups[0])
    loser = dups[0].b if merged.id == dups[0].a.id else dups[0].a
    assert loser.superseded_by == merged.id
    assert "geometry" in merged.tags or merged.summary


def test_decay_strength_decreases_with_age() -> None:
    record = _record("old fact")
    record.salience = 0.8
    record.last_accessed_at = datetime.now(timezone.utc) - timedelta(days=60)
    old_strength = strength_now(record)
    reinforced = reinforce(record)
    new_strength = strength_now(reinforced)
    assert old_strength < record.salience
    assert new_strength >= old_strength


def test_verification_flags_stale_high_salience() -> None:
    record = _record("Learner is allergic to peanuts.")
    record.salience = 0.9
    record.last_accessed_at = datetime.now(timezone.utc) - timedelta(days=90)
    assert needs_verification(record)
    assert "still true" in verification_prompt(record)


@pytest.mark.asyncio
async def test_compaction_keeps_last_k_verbatim() -> None:
    messages = [{"role": "user", "content": f"message {i} " + ("x" * 200)} for i in range(20)]
    result = await compact_context(CompactionInput(messages=messages, target_tokens=512))
    assert result.kept_verbatim_count <= 6
    assert result.compacted_summary
    assert result.messages[0]["role"] == "system"
    assert result.estimated_tokens <= 512 or len(result.messages) < len(messages)
