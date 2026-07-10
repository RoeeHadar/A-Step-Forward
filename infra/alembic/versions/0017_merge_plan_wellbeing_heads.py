"""Merge alembic heads: adaptive_levels + wellbeing_plan_bias branches.

Revision ID: 0017_merge_plan_wellbeing_heads
Revises: 0016_adaptive_levels, 0016_wellbeing_plan_bias
Create Date: 2026-07-11
"""

from __future__ import annotations

from alembic import op


revision = "0017_merge_plan_wellbeing_heads"
down_revision = ("0016_adaptive_levels", "0016_wellbeing_plan_bias")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
