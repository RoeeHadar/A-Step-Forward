"""AI-authored bilingual lessons + per-skill practice tracking.

Adds:
- ``lessons`` — one row per knowledge-graph concept, with bilingual sections
  and an ``agent_hints`` JSON blob consumed by runtime agents (Tutor, Coach,
  Memory Steward, Progress Analyzer).
- ``lesson_questions`` — 6+ questions per lesson, bilingual, with explicit
  rubrics for open-ended items so the Grader agent can score them.
- ``skill_practice`` — per-(learner, skill_atom) attempts / successes /
  last_practiced, used by the Coach to choose drill candidates.
- ``math_track`` column on ``lessons`` so a single canonical math lesson can
  surface across `/learn/high_school_math_3_points` / 4 / 5 tiles.

Revision ID: 0013_lessons
Revises: 0012_concept_explanations
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op

revision = "0013_lessons"
down_revision = "0012_concept_explanations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS lessons (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            concept_id    TEXT NOT NULL UNIQUE,
            subject       TEXT NOT NULL,
            level         TEXT NOT NULL,
            math_track    TEXT[] NOT NULL DEFAULT '{}',
            title_en      TEXT NOT NULL,
            title_he      TEXT NOT NULL,
            summary_en    TEXT NOT NULL,
            summary_he    TEXT NOT NULL,
            sections      JSONB NOT NULL,
            agent_hints   JSONB NOT NULL,
            est_minutes   INT  NOT NULL DEFAULT 15,
            author        TEXT NOT NULL DEFAULT 'cursor-claude-2026',
            version       INT  NOT NULL DEFAULT 1,
            created_at    TIMESTAMPTZ DEFAULT NOW(),
            updated_at    TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_lessons_subject_level ON lessons (subject, level)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_lessons_math_track ON lessons USING GIN (math_track)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_questions (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lesson_id       UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            ord             INT  NOT NULL,
            kind            TEXT NOT NULL,
            difficulty      TEXT NOT NULL,
            stem_en         TEXT NOT NULL,
            stem_he         TEXT NOT NULL,
            options_en      JSONB,
            options_he      JSONB,
            correct_index   INT,
            correct_answer  TEXT,
            rubric_en       TEXT,
            rubric_he       TEXT,
            explanation_en  TEXT NOT NULL,
            explanation_he  TEXT NOT NULL,
            skill_atoms     JSONB NOT NULL DEFAULT '[]'::jsonb,
            UNIQUE (lesson_id, ord)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_questions_lesson ON lesson_questions (lesson_id)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS skill_practice (
            learner_id      TEXT NOT NULL,
            skill_atom      TEXT NOT NULL,
            attempts        INT  NOT NULL DEFAULT 0,
            successes       INT  NOT NULL DEFAULT 0,
            last_practiced  TIMESTAMPTZ DEFAULT NOW(),
            PRIMARY KEY (learner_id, skill_atom)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_skill_practice_learner ON skill_practice (learner_id, last_practiced DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS skill_practice")
    op.execute("DROP TABLE IF EXISTS lesson_questions")
    op.execute("DROP TABLE IF EXISTS lessons")
