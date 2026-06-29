"""Adaptive level metadata for lessons, questions, and diagnostics.

Adds:
1. ``lessons.level_focus`` (JSONB) — per-level focus blocks (3pt/4pt/5pt/hs_physics)
   describing what depth is required at each Bagrut level.
2. ``lesson_questions.points_level_min`` (TEXT) — minimum Bagrut level for which
   a question is appropriate. NULL = all levels see this question.
3. ``lesson_questions.answer_payload`` (JSONB) — structured payload for complex
   answer types (matching, ordering, derivation steps). Was missing from 0013.
4. ``lessons.skill_atom_bank`` (JSONB) — per-(skill_atom, level) pre-generated
   question bank for targeted practice.
5. ``diagnostic_items.points_levels`` (TEXT[]) — which Bagrut levels this
   diagnostic item should be shown to. NULL = show to all.

Revision ID: 0016_adaptive_levels
Revises: 0015_persona_agent_notes
Create Date: 2026-06-27
"""

from __future__ import annotations

from alembic import op

revision = "0016_adaptive_levels"
down_revision = "0015_persona_agent_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. lessons: add level_focus and skill_atom_bank columns
    op.execute(
        """
        ALTER TABLE lessons
            ADD COLUMN IF NOT EXISTS level_focus      JSONB,
            ADD COLUMN IF NOT EXISTS skill_atom_bank  JSONB
        """
    )

    # 2. lesson_questions: add points_level_min and answer_payload
    op.execute(
        """
        ALTER TABLE lesson_questions
            ADD COLUMN IF NOT EXISTS points_level_min TEXT,
            ADD COLUMN IF NOT EXISTS answer_payload   JSONB
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_lq_level_min ON lesson_questions (points_level_min)")

    # 3. diagnostic_items: add points_levels array column
    op.execute(
        """
        ALTER TABLE diagnostic_items
            ADD COLUMN IF NOT EXISTS points_levels TEXT[]
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_diag_points_levels ON diagnostic_items USING GIN (points_levels)"
    )

    # 4. Backfill diagnostic_items.points_levels from the topic/difficulty heuristic:
    #    Items tagged "calculus" → 5pt only.
    #    Items tagged "linear"/"statistics"/"probability" at easy → 3pt and up.
    #    Everything else: leave NULL (all levels).
    op.execute(
        """
        UPDATE diagnostic_items
        SET points_levels = ARRAY['5pt']
        WHERE topic ILIKE '%calculus%'
           OR topic ILIKE '%derivative%'
           OR topic ILIKE '%integral%'
           OR topic ILIKE '%limit%'
        """
    )
    op.execute(
        """
        UPDATE diagnostic_items
        SET points_levels = ARRAY['3pt', '4pt', '5pt']
        WHERE topic ILIKE '%linear%'
           OR topic ILIKE '%fraction%'
           OR topic ILIKE '%ratio%'
           OR topic ILIKE '%percent%'
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_diag_points_levels")
    op.execute("ALTER TABLE diagnostic_items DROP COLUMN IF EXISTS points_levels")
    op.execute("DROP INDEX IF EXISTS ix_lq_level_min")
    op.execute(
        """
        ALTER TABLE lesson_questions
            DROP COLUMN IF EXISTS points_level_min,
            DROP COLUMN IF EXISTS answer_payload
        """
    )
    op.execute(
        """
        ALTER TABLE lessons
            DROP COLUMN IF EXISTS level_focus,
            DROP COLUMN IF EXISTS skill_atom_bank
        """
    )
