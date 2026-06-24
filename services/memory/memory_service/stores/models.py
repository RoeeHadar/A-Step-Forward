"""SQLAlchemy ORM models for persisted memory types.

Each non-working memory type has its own table (PLAN.md §5.1). Working memory
is ephemeral and is not stored here.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MemoryColumnsMixin:
    """Shared columns across all persisted memory tables."""

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)

    salience: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
    valence: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    decay_tau_days: Mapped[float] = mapped_column(Float, nullable=False, server_default="14.0")
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    superseded_by: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    kg_node_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def _memory_indexes(table_name: str) -> list[Index]:
    return [
        Index(f"ix_{table_name}_learner_created", "learner_id", "created_at"),
        Index(f"ix_{table_name}_learner_not_deleted", "learner_id", "deleted_at"),
    ]


class EpisodicMemory(Base, MemoryColumnsMixin):
    __tablename__ = "episodic_memories"
    __table_args__ = (
        *_memory_indexes("episodic_memories"),
        Index(
            "ix_episodic_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class SemanticMemory(Base, MemoryColumnsMixin):
    __tablename__ = "semantic_memories"
    __table_args__ = (
        *_memory_indexes("semantic_memories"),
        Index(
            "ix_semantic_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class ProceduralMemory(Base, MemoryColumnsMixin):
    __tablename__ = "procedural_memories"
    __table_args__ = (
        *_memory_indexes("procedural_memories"),
        Index(
            "ix_procedural_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class AffectiveMemory(Base, MemoryColumnsMixin):
    __tablename__ = "affective_memories"
    __table_args__ = (
        *_memory_indexes("affective_memories"),
        Index(
            "ix_affective_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class ContextMemory(Base, MemoryColumnsMixin):
    __tablename__ = "context_memories"
    __table_args__ = (
        *_memory_indexes("context_memories"),
        Index(
            "ix_context_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class ReflectiveMemory(Base, MemoryColumnsMixin):
    __tablename__ = "reflective_memories"
    __table_args__ = (
        *_memory_indexes("reflective_memories"),
        Index(
            "ix_reflective_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class SourceMemory(Base, MemoryColumnsMixin):
    __tablename__ = "source_memories"
    __table_args__ = (
        *_memory_indexes("source_memories"),
        Index(
            "ix_source_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class MemoryEvent(Base):
    """Lightweight chat-turn event log (stream I persistence)."""

    __tablename__ = "memory_events"
    __table_args__ = (Index("idx_memory_events_learner_id", "learner_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(Text, nullable=False)
    agent: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="chat_turn")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AuditMemoryEvent(Base):
    __tablename__ = "audit_memory_events"
    __table_args__ = (Index("ix_audit_memory_events_learner_ts", "learner_id", "ts"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    agent_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    learner_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    memory_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")


MEMORY_TABLES: tuple[type[Base], ...] = (
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    AffectiveMemory,
    ContextMemory,
    ReflectiveMemory,
    SourceMemory,
)
