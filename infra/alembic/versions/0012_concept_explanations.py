"""In-house concept explanations adapted from public CC-licensed sources.

Stores scraped + adapted content per (concept_id, language) so the /learn
section renders explanations natively instead of linking out.

Revision ID: 0012_concept_explanations
Revises: 0011_onboarding_extras
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op

revision = "0012_concept_explanations"
down_revision = "0011_onboarding_extras"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS concept_explanations (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            concept_id  TEXT NOT NULL,
            language    TEXT NOT NULL,
            title       TEXT NOT NULL,
            body_md     TEXT NOT NULL,
            body_html   TEXT,
            summary     TEXT,
            image_url   TEXT,
            source      TEXT NOT NULL,
            source_url  TEXT NOT NULL,
            source_lang TEXT NOT NULL,
            license     TEXT NOT NULL,
            attribution TEXT NOT NULL,
            fetched_at  TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (concept_id, language, source)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_concept_explanations_concept ON concept_explanations (concept_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_concept_explanations_lang ON concept_explanations (language)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS concept_explanations")
