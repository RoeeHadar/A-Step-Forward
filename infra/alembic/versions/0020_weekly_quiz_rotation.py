"""Weekly-quiz retake rotation (ADR-0010 Stream B, anti-gaming).

Adds a ``rotation`` dimension to ``weekly_quizzes_ai`` so each weekly-gate retake
gets its own cached quiz and therefore FRESH generated items — a learner can't
memorize answer positions from a previous attempt. ``rotation`` = the number of
gate attempts already recorded for the plan week; reloads within a rotation stay
cached (no extra LLM calls).

Design notes:
- The cache uniqueness moves from ``(user_id, week_start, plan_id, week_num, locale)``
  to ``(..., rotation)``. Existing rows default to ``rotation = 0``.
- The web app also performs this idempotent DDL lazily on the first weekly-quiz load
  and degrades gracefully when the column is absent, so shipping the code before this
  migration runs is safe. This migration is the canonical, tracked version.

Revision ID: 0020_weekly_quiz_rotation
Revises: 0019_test_attempts
Create Date: 2026-07-19
"""

from __future__ import annotations

from alembic import op

revision = "0020_weekly_quiz_rotation"
down_revision = "0019_test_attempts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure the (lazily-created) cache table exists before altering it.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS weekly_quizzes_ai (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id     TEXT NOT NULL,
            week_start  DATE NOT NULL,
            plan_id     TEXT,
            week_num    INT,
            locale      TEXT NOT NULL DEFAULT 'he',
            questions   JSONB NOT NULL,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS rotation INT NOT NULL DEFAULT 0"
    )
    op.execute("DROP INDEX IF EXISTS weekly_quizzes_ai_user_week_plan_locale_idx")
    op.execute(
        "ALTER TABLE weekly_quizzes_ai DROP CONSTRAINT IF EXISTS weekly_quizzes_ai_user_id_week_start_key"
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS weekly_quizzes_ai_user_week_plan_locale_rot_idx
        ON weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale, rotation)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS weekly_quizzes_ai_user_week_plan_locale_rot_idx")
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS weekly_quizzes_ai_user_week_plan_locale_idx
        ON weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale)
        """
    )
    op.execute("ALTER TABLE weekly_quizzes_ai DROP COLUMN IF EXISTS rotation")
