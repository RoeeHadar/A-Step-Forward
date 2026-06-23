"""Initial migration — enable extensions and create core tables (placeholder).

Sub-agent 09-infra fills the tables (users, learners, sessions, memory_*,
curriculum_*, audit_*, kg_chunks, etc.) using SQLAlchemy metadata. This file
ships only the extension setup so dev environments come up clean.

Revision ID: 0001
Revises:
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
    op.execute("DROP EXTENSION IF EXISTS vector")
