"""Onboarding extras + chat memory.

Adds:
- next_test_date / final_goal_date / mental_state / personality_profile to learner_profiles
- chat_turns table for cross-session memory persistence
- external_resources table for curated 3rd-party content per subject

Revision ID: 0011_onboarding_extras
Revises: 0010_learner_model
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op

revision = "0011_onboarding_extras"
down_revision = "0010_learner_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS next_test_date DATE")
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS next_test_name TEXT")
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS final_goal_date DATE")
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS mental_state JSONB")
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS personality_profile JSONB")
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS weak_concepts TEXT[]")
    op.execute("ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS strong_concepts TEXT[]")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_turns (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id  TEXT NOT NULL,
            agent       TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            session_id  TEXT,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_turns_learner_time ON chat_turns (learner_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_turns_session ON chat_turns (session_id, created_at)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS external_resources (
            id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subject      TEXT NOT NULL,
            concept_id   TEXT,
            title        TEXT NOT NULL,
            url          TEXT NOT NULL,
            source       TEXT NOT NULL,
            language     TEXT NOT NULL DEFAULT 'en',
            description  TEXT,
            sort_order   INT NOT NULL DEFAULT 0,
            created_at   TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (subject, url)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_external_resources_subject ON external_resources (subject)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS external_resources")
    op.execute("DROP TABLE IF EXISTS chat_turns")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS strong_concepts")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS weak_concepts")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS personality_profile")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS mental_state")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS final_goal_date")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS next_test_name")
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS next_test_date")
