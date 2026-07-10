"""Add plan_schema_version to learning_plans for unified planner migration gate.

Revision ID: 0015_plan_schema_version
Revises: 0014_kg_skill_graph
Create Date: 2026-07-11
"""

from __future__ import annotations

from alembic import op


revision = "0015_plan_schema_version"
down_revision = "0014_kg_skill_graph"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE learning_plans
            ADD COLUMN IF NOT EXISTS plan_schema_version INT NOT NULL DEFAULT 1
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE learning_plans
            DROP COLUMN IF EXISTS plan_schema_version
        """
    )
