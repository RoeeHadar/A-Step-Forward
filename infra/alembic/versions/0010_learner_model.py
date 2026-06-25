"""Adaptive learning — learner profiles, mastery, plans, diagnostics.

Revision ID: 0010_learner_model
Revises: 0009_bookings
Create Date: 2026-06-25
"""

from __future__ import annotations

from alembic import op

revision = "0010_learner_model"
down_revision = "0009_bookings"
branch_labels = None
depends_on = None

# asyncpg (Alembic async) rejects multiple statements per op.execute — one per call.


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS learner_profiles (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id       TEXT NOT NULL UNIQUE,
            goal             TEXT NOT NULL,
            grade_level      TEXT,
            points_group     TEXT,
            subjects         TEXT[] NOT NULL,
            hours_per_week   NUMERIC(4,1) NOT NULL,
            preferred_style  TEXT,
            attention_span   INT,
            self_scores      JSONB,
            background_notes TEXT,
            created_at       TIMESTAMPTZ DEFAULT NOW(),
            updated_at       TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS concept_mastery (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id    TEXT NOT NULL,
            concept_id    TEXT NOT NULL,
            score         NUMERIC(5,4) NOT NULL,
            data_points   INT NOT NULL DEFAULT 1,
            last_activity TIMESTAMPTZ DEFAULT NOW(),
            created_at    TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (learner_id, concept_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_concept_mastery_learner ON concept_mastery (learner_id)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS mastery_snapshots (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id  TEXT NOT NULL,
            week_start  DATE NOT NULL,
            scores      JSONB NOT NULL,
            created_at  TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (learner_id, week_start)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS diagnostic_sessions (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id    TEXT NOT NULL,
            status        TEXT NOT NULL DEFAULT 'active',
            topics        TEXT[] NOT NULL,
            question_idx  INT NOT NULL DEFAULT 0,
            results       JSONB,
            created_at    TIMESTAMPTZ DEFAULT NOW(),
            completed_at  TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_diagnostic_sessions_learner ON diagnostic_sessions (learner_id)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS diagnostic_items (
            id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            topic          TEXT NOT NULL,
            subject        TEXT NOT NULL,
            difficulty     NUMERIC(3,1) NOT NULL,
            bloom_level    TEXT NOT NULL,
            stem           TEXT NOT NULL,
            options        JSONB NOT NULL,
            explanation    TEXT,
            source_concept TEXT NOT NULL,
            created_at     TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_diagnostic_items_topic ON diagnostic_items (topic, subject)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS learning_plans (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id    TEXT NOT NULL UNIQUE,
            goal          TEXT NOT NULL,
            start_date    DATE NOT NULL,
            end_date      DATE,
            status        TEXT NOT NULL DEFAULT 'active',
            created_at    TIMESTAMPTZ DEFAULT NOW(),
            updated_at    TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS plan_weeks (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            plan_id       UUID NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
            week_number   INT NOT NULL,
            concepts      TEXT[] NOT NULL,
            content_ids   UUID[],
            quiz_due_at   TIMESTAMPTZ,
            status        TEXT NOT NULL DEFAULT 'upcoming',
            UNIQUE (plan_id, week_number)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS weekly_quizzes (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            week_id       UUID NOT NULL REFERENCES plan_weeks(id) ON DELETE CASCADE,
            learner_id    TEXT NOT NULL,
            items         JSONB NOT NULL,
            time_limit_s  INT NOT NULL DEFAULT 1800,
            started_at    TIMESTAMPTZ,
            submitted_at  TIMESTAMPTZ,
            score         NUMERIC(5,4),
            per_topic     JSONB,
            status        TEXT NOT NULL DEFAULT 'pending'
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_responses (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            quiz_id       UUID NOT NULL,
            quiz_type     TEXT NOT NULL,
            item_id       UUID NOT NULL REFERENCES diagnostic_items(id),
            chosen        TEXT NOT NULL,
            correct       BOOLEAN NOT NULL,
            time_spent_s  INT,
            created_at    TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_quiz_responses_quiz ON quiz_responses (quiz_id, quiz_type)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS quiz_responses")
    op.execute("DROP TABLE IF EXISTS weekly_quizzes")
    op.execute("DROP TABLE IF EXISTS plan_weeks")
    op.execute("DROP TABLE IF EXISTS learning_plans")
    op.execute("DROP TABLE IF EXISTS diagnostic_items")
    op.execute("DROP TABLE IF EXISTS diagnostic_sessions")
    op.execute("DROP TABLE IF EXISTS mastery_snapshots")
    op.execute("DROP TABLE IF EXISTS concept_mastery")
    op.execute("DROP TABLE IF EXISTS learner_profiles")
