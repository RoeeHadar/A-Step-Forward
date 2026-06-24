"""Add memory_events table for lightweight chat-turn audit log.

Revision ID: 0007_memory_events
Revises: 0006_kg_chunks_384
Create Date: 2026-06-24
"""

from __future__ import annotations

from alembic import op

revision = "0007_memory_events"
down_revision = "0006_kg_chunks_384"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id TEXT NOT NULL,
            agent TEXT NOT NULL,
            content TEXT NOT NULL,
            event_type TEXT NOT NULL DEFAULT 'chat_turn',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_memory_events_learner_id
        ON memory_events(learner_id)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_memory_events_learner_id")
    op.execute("DROP TABLE IF EXISTS memory_events")
