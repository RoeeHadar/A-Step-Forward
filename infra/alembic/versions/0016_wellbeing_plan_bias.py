"""Add wellbeing_plan_bias and plan adjustment audit columns (ADR-0008 PR2).

Revision ID: 0016_wellbeing_plan_bias
Revises: 0015_plan_schema_version
Create Date: 2026-07-11
"""

from __future__ import annotations

from alembic import op


revision = "0016_wellbeing_plan_bias"
down_revision = "0015_plan_schema_version"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE learner_profiles
            ADD COLUMN IF NOT EXISTS wellbeing_plan_bias JSONB DEFAULT NULL
        """
    )
    op.execute(
        """
        ALTER TABLE learning_plans
            ADD COLUMN IF NOT EXISTS plan_adjustment_kind TEXT DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS plan_last_adjusted_at TIMESTAMPTZ DEFAULT NULL
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE learning_plans
            DROP COLUMN IF EXISTS plan_last_adjusted_at,
            DROP COLUMN IF EXISTS plan_adjustment_kind
        """
    )
    op.execute(
        """
        ALTER TABLE learner_profiles
            DROP COLUMN IF EXISTS wellbeing_plan_bias
        """
    )
