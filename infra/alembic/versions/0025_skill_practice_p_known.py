"""Add skill_practice.p_known (per-atom BKT posterior).

Revision ID: 0025_skill_practice_p_known
Revises: 0024_kg_chunks_rag
Create Date: 2026-11-10

AS-53 (Phase 4 C5b), from the AS-51 proposal (migration-proposal-p_known.sql).
NULL means no BKT history; readers fall back to the successes/attempts ratio.
Written only when MASTERY_MODEL=bkt (apps/web/src/lib/neon-db.ts
applyPracticeMasteryUpdate and markAtomPracticed).

No backfill: skill_practice stores only counts (attempts, successes), so the
attempt order is lost and a replay is impossible. Additive and nullable, so
existing rows and the flag-off write path are untouched.
"""

from __future__ import annotations

from alembic import op

revision = "0025_skill_practice_p_known"
down_revision = "0024_kg_chunks_rag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE skill_practice ADD COLUMN IF NOT EXISTS p_known NUMERIC")


def downgrade() -> None:
    op.execute("ALTER TABLE skill_practice DROP COLUMN IF EXISTS p_known")
