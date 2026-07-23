"""Add lesson_booking_settings for Google Calendar + private contact secrets.

Revision ID: 0023_lesson_booking_settings
Revises: 0022_lesson_bookings
Create Date: 2026-07-23
"""

from __future__ import annotations

from alembic import op

revision = "0023_lesson_booking_settings"
down_revision = "0022_lesson_bookings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_booking_settings (
            id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
            calendar_id TEXT NOT NULL DEFAULT 'primary',
            google_refresh_token_enc TEXT,
            google_channel_id TEXT,
            google_resource_id TEXT,
            google_channel_expiration TIMESTAMPTZ,
            busy_cache JSONB NOT NULL DEFAULT '[]'::jsonb,
            busy_cache_from TIMESTAMPTZ,
            busy_cache_to TIMESTAMPTZ,
            busy_cache_updated_at TIMESTAMPTZ,
            phone_enc TEXT,
            address_enc TEXT,
            meeting_link TEXT,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "INSERT INTO lesson_booking_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS lesson_booking_settings")
