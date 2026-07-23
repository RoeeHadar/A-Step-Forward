"""Add lesson_bookings table for Book-a-Lesson (web Neon-direct).

Revision ID: 0022_lesson_bookings
Revises: 0021_social_platform
Create Date: 2026-07-23
"""

from __future__ import annotations

from alembic import op

revision = "0022_lesson_bookings"
down_revision = "0021_social_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_bookings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            public_token TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'submitted'
              CHECK (status IN (
                'submitted', 'proposal_sent', 'pick_pending',
                'confirmed', 'rejected', 'cancelled', 'expired'
              )),
            requester_name TEXT NOT NULL,
            requester_email TEXT NOT NULL,
            requester_phone TEXT NOT NULL,
            locale TEXT NOT NULL DEFAULT 'he',
            clerk_user_id TEXT,
            booking_for_other BOOLEAN NOT NULL DEFAULT FALSE,
            learner_name TEXT NOT NULL,
            learner_grade TEXT,
            modality TEXT NOT NULL CHECK (modality IN ('online', 'haifa')),
            subjects TEXT[] NOT NULL,
            level_band TEXT NOT NULL
              CHECK (level_band IN ('middle_school', 'bagrut', 'university', 'other')),
            university_name TEXT,
            university_course TEXT,
            goal_text TEXT NOT NULL,
            notes TEXT,
            duration_h NUMERIC(3,1) NOT NULL,
            price_ils INT NOT NULL,
            preferred_start TIMESTAMPTZ NOT NULL,
            preferred_end TIMESTAMPTZ NOT NULL,
            proposed_windows JSONB NOT NULL DEFAULT '[]'::jsonb,
            selected_window JSONB,
            share_dossier BOOLEAN NOT NULL DEFAULT FALSE,
            dossier_snapshot JSONB,
            gcal_event_id TEXT,
            meeting_link TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_bookings_created ON lesson_bookings (created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_bookings_clerk ON lesson_bookings (clerk_user_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_bookings_status ON lesson_bookings (status, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS lesson_bookings")
