"""Durable test/quiz attempt archive + week-gate signal (ADR-0009).

Adds ``test_attempts`` — one row per graded quiz/test a learner takes. Powers:
- the week-gate signal (``score`` vs ``pass_threshold``, ``passed``, ``weak_concepts``),
  used to drive remediation under the soft-override policy, and
- the Tests archive UI: past tests with the learner's ``answers`` vs the correct
  answers snapshotted in ``questions``, plus a ``feedback`` slot for future
  Reviewer notes.

Design notes:
- ``questions`` snapshots the graded items (stem / options / correct / topic) at
  submit time so the archive is stable even if the source quiz/lesson changes
  (decoupled from the concurrent lesson rewrite).
- ``kind`` distinguishes weekly-gate quizzes from other assessment types.
- The web app also creates this table lazily and degrades gracefully when it is
  absent, so shipping the code before this migration runs is safe.

Revision ID: 0019_test_attempts
Revises: 0018_question_store
Create Date: 2026-07-19
"""

from __future__ import annotations

from alembic import op

revision = "0019_test_attempts"
down_revision = "0018_question_store"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS test_attempts (
            id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id     TEXT NOT NULL,
            kind           TEXT NOT NULL DEFAULT 'weekly_gate',
            plan_id        TEXT,
            week_num       INT,
            quiz_id        TEXT,
            locale         TEXT NOT NULL DEFAULT 'he',
            score          DOUBLE PRECISION NOT NULL DEFAULT 0,
            passed         BOOLEAN NOT NULL DEFAULT FALSE,
            pass_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.75,
            per_topic      JSONB NOT NULL DEFAULT '{}'::jsonb,
            weak_concepts  TEXT[] NOT NULL DEFAULT '{}',
            questions      JSONB NOT NULL DEFAULT '[]'::jsonb,
            answers        JSONB NOT NULL DEFAULT '[]'::jsonb,
            feedback       JSONB,
            created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_test_attempts_learner ON test_attempts (learner_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_test_attempts_plan_week ON test_attempts (learner_id, plan_id, week_num)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_test_attempts_kind ON test_attempts (learner_id, kind)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_test_attempts_kind")
    op.execute("DROP INDEX IF EXISTS ix_test_attempts_plan_week")
    op.execute("DROP INDEX IF EXISTS ix_test_attempts_learner")
    op.execute("DROP TABLE IF EXISTS test_attempts")
