"""Memory tables — seven persisted types + audit log.

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

MEMORY_TABLE_NAMES = (
    "episodic_memories",
    "semantic_memories",
    "procedural_memories",
    "affective_memories",
    "context_memories",
    "reflective_memories",
    "source_memories",
)


def _memory_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("learner_id", sa.String(length=128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "tags",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.Column("salience", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("valence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("decay_tau_days", sa.Float(), nullable=False, server_default="14.0"),
        sa.Column(
            "last_accessed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("access_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("superseded_by", sa.String(length=128), nullable=True),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provenance", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column(
            "kg_node_ids",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    for table_name in MEMORY_TABLE_NAMES:
        op.create_table(table_name, *_memory_columns())
        op.create_index(f"ix_{table_name}_learner_id", table_name, ["learner_id"])
        op.create_index(f"ix_{table_name}_superseded_by", table_name, ["superseded_by"])
        op.create_index(
            f"ix_{table_name}_learner_created",
            table_name,
            ["learner_id", "created_at"],
        )
        op.create_index(
            f"ix_{table_name}_learner_not_deleted",
            table_name,
            ["learner_id", "deleted_at"],
        )
        # HNSW index for cosine similarity search on embeddings.
        op.execute(
            f"""
            CREATE INDEX ix_{table_name}_embedding_hnsw
            ON {table_name}
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
            """
        )

    op.create_table(
        "audit_memory_events",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=True),
        sa.Column("learner_id", sa.String(length=128), nullable=True),
        sa.Column("memory_id", sa.String(length=128), nullable=True),
        sa.Column(
            "payload",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_index("ix_audit_memory_events_action", "audit_memory_events", ["action"])
    op.create_index("ix_audit_memory_events_learner_id", "audit_memory_events", ["learner_id"])
    op.create_index("ix_audit_memory_events_memory_id", "audit_memory_events", ["memory_id"])
    op.create_index(
        "ix_audit_memory_events_learner_ts",
        "audit_memory_events",
        ["learner_id", "ts"],
    )


def downgrade() -> None:
    op.drop_table("audit_memory_events")
    for table_name in reversed(MEMORY_TABLE_NAMES):
        op.drop_table(table_name)
