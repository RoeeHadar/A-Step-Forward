"""Core tables — memory + gateway (autogenerate baseline for sub-agents).

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_MEMORY_COLUMNS = [
    sa.Column("id", sa.String(length=128), nullable=False),
    sa.Column("learner_id", sa.String(length=128), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("summary", sa.Text(), nullable=True),
    sa.Column(
        "tags",
        postgresql.JSONB(astext_type=sa.Text()),
        server_default="[]",
        nullable=False,
    ),
    sa.Column("embedding", Vector(1024), nullable=True),
    sa.Column("salience", sa.Float(), server_default="0.5", nullable=False),
    sa.Column("confidence", sa.Float(), server_default="0.5", nullable=False),
    sa.Column("valence", sa.Float(), server_default="0.0", nullable=False),
    sa.Column("decay_tau_days", sa.Float(), server_default="14.0", nullable=False),
    sa.Column(
        "last_accessed_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    ),
    sa.Column("access_count", sa.Integer(), server_default="0", nullable=False),
    sa.Column("superseded_by", sa.String(length=128), nullable=True),
    sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("provenance", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column(
        "kg_node_ids",
        postgresql.JSONB(astext_type=sa.Text()),
        server_default="[]",
        nullable=False,
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    ),
    sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
]


def _create_memory_table(name: str) -> None:
    op.create_table(
        name,
        *_MEMORY_COLUMNS,
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(f"ix_{name}_learner_id", name, ["learner_id"], unique=False)
    op.create_index(f"ix_{name}_superseded_by", name, ["superseded_by"], unique=False)
    op.create_index(f"ix_{name}_learner_created", name, ["learner_id", "created_at"], unique=False)
    op.create_index(
        f"ix_{name}_learner_not_deleted", name, ["learner_id", "deleted_at"], unique=False
    )
    # HNSW index for cosine similarity search on embeddings.
    op.create_index(
        f"ix_{name}_embedding_hnsw",
        name,
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def upgrade() -> None:
    for table in (
        "episodic_memories",
        "semantic_memories",
        "procedural_memories",
        "affective_memories",
        "context_memories",
        "reflective_memories",
        "source_memories",
    ):
        _create_memory_table(table)

    op.create_table(
        "audit_memory_events",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=True),
        sa.Column("learner_id", sa.String(length=128), nullable=True),
        sa.Column("memory_id", sa.String(length=128), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_memory_events_action", "audit_memory_events", ["action"], unique=False
    )
    op.create_index(
        "ix_audit_memory_events_learner_id", "audit_memory_events", ["learner_id"], unique=False
    )
    op.create_index(
        "ix_audit_memory_events_memory_id", "audit_memory_events", ["memory_id"], unique=False
    )
    op.create_index(
        "ix_audit_memory_events_learner_ts",
        "audit_memory_events",
        ["learner_id", "ts"],
        unique=False,
    )

    op.create_table(
        "gateway_users",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("clerk_user_id", sa.String(length=128), nullable=True),
        sa.Column("display_name", sa.String(length=256), server_default="Learner", nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("role", sa.String(length=32), server_default="learner", nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("child_mode", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("locale", sa.String(length=16), server_default="en", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gateway_users_clerk_user_id", "gateway_users", ["clerk_user_id"], unique=True
    )

    op.create_table(
        "gateway_sessions",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("learner_id", sa.String(length=128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gateway_sessions_learner_id", "gateway_sessions", ["learner_id"], unique=False
    )

    op.create_table(
        "audit_gateway_events",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("learner_id", sa.String(length=128), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("route", sa.String(length=256), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_gateway_events_learner_id", "audit_gateway_events", ["learner_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_audit_gateway_events_learner_id", table_name="audit_gateway_events")
    op.drop_table("audit_gateway_events")
    op.drop_index("ix_gateway_sessions_learner_id", table_name="gateway_sessions")
    op.drop_table("gateway_sessions")
    op.drop_index("ix_gateway_users_clerk_user_id", table_name="gateway_users")
    op.drop_table("gateway_users")

    op.drop_index("ix_audit_memory_events_learner_ts", table_name="audit_memory_events")
    op.drop_index("ix_audit_memory_events_memory_id", table_name="audit_memory_events")
    op.drop_index("ix_audit_memory_events_learner_id", table_name="audit_memory_events")
    op.drop_index("ix_audit_memory_events_action", table_name="audit_memory_events")
    op.drop_table("audit_memory_events")

    for table in reversed(
        (
            "source_memories",
            "reflective_memories",
            "context_memories",
            "affective_memories",
            "procedural_memories",
            "semantic_memories",
            "episodic_memories",
        )
    ):
        op.drop_index(f"ix_{table}_embedding_hnsw", table_name=table)
        op.drop_index(f"ix_{table}_learner_not_deleted", table_name=table)
        op.drop_index(f"ix_{table}_learner_created", table_name=table)
        op.drop_index(f"ix_{table}_superseded_by", table_name=table)
        op.drop_index(f"ix_{table}_learner_id", table_name=table)
        op.drop_table(table)
