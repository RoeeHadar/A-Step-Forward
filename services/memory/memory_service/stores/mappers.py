"""Convert between Pydantic MemoryRecord and SQLAlchemy rows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from schemas.common import Provenance
from schemas.memory import MemoryRecord, MemoryType

from .models import MemoryColumnsMixin


def table_for_type(memory_type: MemoryType) -> type[MemoryColumnsMixin]:
    from .models import (
        AffectiveMemory,
        ContextMemory,
        EpisodicMemory,
        ProceduralMemory,
        ReflectiveMemory,
        SemanticMemory,
        SourceMemory,
    )

    mapping: dict[MemoryType, type[MemoryColumnsMixin]] = {
        MemoryType.EPISODIC: EpisodicMemory,
        MemoryType.SEMANTIC: SemanticMemory,
        MemoryType.PROCEDURAL: ProceduralMemory,
        MemoryType.AFFECTIVE: AffectiveMemory,
        MemoryType.CONTEXT: ContextMemory,
        MemoryType.REFLECTIVE: ReflectiveMemory,
        MemoryType.SOURCE: SourceMemory,
    }
    if memory_type not in mapping:
        raise ValueError(f"Memory type {memory_type!r} is not persisted")
    return mapping[memory_type]


def type_for_table(table: type[MemoryColumnsMixin]) -> MemoryType:
    from .models import (
        AffectiveMemory,
        ContextMemory,
        EpisodicMemory,
        ProceduralMemory,
        ReflectiveMemory,
        SemanticMemory,
        SourceMemory,
    )

    mapping = {
        EpisodicMemory: MemoryType.EPISODIC,
        SemanticMemory: MemoryType.SEMANTIC,
        ProceduralMemory: MemoryType.PROCEDURAL,
        AffectiveMemory: MemoryType.AFFECTIVE,
        ContextMemory: MemoryType.CONTEXT,
        ReflectiveMemory: MemoryType.REFLECTIVE,
        SourceMemory: MemoryType.SOURCE,
    }
    return mapping[table]


def record_to_row(record: MemoryRecord, *, embedding: list[float] | None = None) -> MemoryColumnsMixin:
    table = table_for_type(record.type)
    return table(
        id=record.id,
        learner_id=record.learner_id,
        content=record.content,
        summary=record.summary,
        tags=record.tags,
        embedding=embedding,
        salience=record.salience,
        confidence=record.confidence,
        valence=record.valence,
        decay_tau_days=record.decay_tau_days,
        last_accessed_at=record.last_accessed_at,
        access_count=record.access_count,
        superseded_by=record.superseded_by,
        superseded_at=record.superseded_at,
        provenance=record.provenance.model_dump(mode="json"),
        kg_node_ids=record.kg_node_ids,
        created_at=record.created_at,
        updated_at=record.updated_at,
        archived_at=record.archived_at,
        deleted_at=record.deleted_at,
        expires_at=record.expires_at,
    )


def row_to_record(row: MemoryColumnsMixin, memory_type: MemoryType) -> MemoryRecord:
    provenance_raw: dict[str, Any] = row.provenance
    return MemoryRecord(
        id=row.id,
        learner_id=row.learner_id,
        type=memory_type,
        content=row.content,
        summary=row.summary,
        tags=list(row.tags or []),
        salience=row.salience,
        confidence=row.confidence,
        valence=row.valence,
        decay_tau_days=row.decay_tau_days,
        last_accessed_at=_ensure_utc(row.last_accessed_at),
        access_count=row.access_count,
        superseded_by=row.superseded_by,
        superseded_at=_ensure_utc(row.superseded_at) if row.superseded_at else None,
        provenance=Provenance.model_validate(provenance_raw),
        kg_node_ids=list(row.kg_node_ids or []),
        created_at=_ensure_utc(row.created_at),
        updated_at=_ensure_utc(row.updated_at),
        archived_at=_ensure_utc(row.archived_at) if row.archived_at else None,
        deleted_at=_ensure_utc(row.deleted_at) if row.deleted_at else None,
        expires_at=_ensure_utc(row.expires_at) if row.expires_at else None,
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
