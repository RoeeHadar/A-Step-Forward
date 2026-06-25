"""Add bookings table for private lesson requests.

Revision ID: 0009_bookings
Revises: 0008_content_sections
Create Date: 2026-06-25
"""

from __future__ import annotations

from alembic import op

revision = "0009_bookings"
down_revision = "0008_content_sections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            date DATE NOT NULL,
            time TIME NOT NULL,
            duration_h NUMERIC(3,1) NOT NULL,
            subject TEXT NOT NULL,
            notes TEXT,
            price_ils INT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS bookings")
