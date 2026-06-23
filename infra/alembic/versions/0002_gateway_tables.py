"""Gateway-owned tables: users, sessions, audit events.

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_gateway"
down_revision = "0002_memory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gateway_users",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("clerk_user_id", sa.String(length=128), nullable=True),
        sa.Column("display_name", sa.String(length=256), nullable=False, server_default="Learner"),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="learner"),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("child_mode", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("locale", sa.String(length=16), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_gateway_users_clerk_user_id", "gateway_users", ["clerk_user_id"], unique=True)

    op.create_table(
        "gateway_sessions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("learner_id", sa.String(length=128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_gateway_sessions_learner_id", "gateway_sessions", ["learner_id"])

    op.create_table(
        "audit_gateway_events",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("learner_id", sa.String(length=128), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("route", sa.String(length=256), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_gateway_events_learner_id", "audit_gateway_events", ["learner_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_gateway_events_learner_id", table_name="audit_gateway_events")
    op.drop_table("audit_gateway_events")
    op.drop_index("ix_gateway_sessions_learner_id", table_name="gateway_sessions")
    op.drop_table("gateway_sessions")
    op.drop_index("ix_gateway_users_clerk_user_id", table_name="gateway_users")
    op.drop_table("gateway_users")
