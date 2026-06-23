"""Unit tests for memory store mappers (no database required)."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "memory"))

from schemas.common import Provenance
from schemas.memory import MemoryRecord, MemoryType

from memory_service.stores.mappers import record_to_row, row_to_record, table_for_type


def test_record_roundtrip_semantic() -> None:
    record = MemoryRecord(
        id=str(uuid4()),
        learner_id="learner-1",
        type=MemoryType.SEMANTIC,
        content="Learner enjoys geometry puzzles.",
        tags=["math", "geometry"],
        provenance=Provenance(kind="chat", id="turn-1", agent="tutor", model="claude-sonnet-4-5"),
    )
    row = record_to_row(record)
    assert table_for_type(MemoryType.SEMANTIC).__tablename__ == "semantic_memories"
    restored = row_to_record(row, MemoryType.SEMANTIC)
    assert restored.id == record.id
    assert restored.content == record.content
    assert restored.tags == record.tags
    assert restored.provenance.agent == "tutor"


def test_all_persisted_types_map_to_tables() -> None:
    expected = {
        MemoryType.EPISODIC: "episodic_memories",
        MemoryType.SEMANTIC: "semantic_memories",
        MemoryType.PROCEDURAL: "procedural_memories",
        MemoryType.AFFECTIVE: "affective_memories",
        MemoryType.CONTEXT: "context_memories",
        MemoryType.REFLECTIVE: "reflective_memories",
        MemoryType.SOURCE: "source_memories",
    }
    for memory_type, table_name in expected.items():
        assert table_for_type(memory_type).__tablename__ == table_name
