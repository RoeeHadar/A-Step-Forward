"""Knowledge-graph cross-subject edges + first-class skill_atoms + richer
question answer payloads.

The 0013 schema embedded the KG inside `apps/web/src/lib/kg-data.json` and
treated skill atoms as opaque strings inside ``lesson_questions.skill_atoms``
and ``lessons.agent_hints.skill_atoms_unlocked``. To enable:

- Cross-subject learning paths (calculus → physics kinematics, vectors →
  forces, trig → waves, statistics → quantum, etc.) the Curriculum Designer
  agent has to traverse, and
- Skill-atom mastery rollups that the Coach and Progress Analyzer agents
  use to derive root-cause diagnoses ("you keep missing area scaling
  because your `area_scale_factor` atom is at 30% mastery")

we promote both to first-class tables and add cross-subject edges.

Adds:

- ``kg_edges`` — directed (src_concept → dst_concept) edges with a typed
  relation (`prereq`, `applies_to`, `generalizes`, `models`, `tooling_for`)
  and a weight in [0, 1] so the planner can prefer strong links.
- ``skill_atoms`` — one canonical row per atom (id = string used in
  lesson_questions.skill_atoms[]), with subject + difficulty + parent atom.
- ``lesson_skill_atoms`` — many-to-many between lessons and skill atoms
  (covering what the lesson teaches AND what its questions exercise).
- ``answer_payload`` JSONB on ``lesson_questions`` — flexible per-kind
  correct-answer structure for the new kinds (`mcq_multi`, `true_false`,
  `short_answer`, `match`, `ordering`, `derivation`). The legacy
  `correct_index` / `correct_answer` columns are kept for backward
  compat with existing `mcq` / `numeric` rows.

Revision ID: 0014_kg_skill_graph
Revises: 0013_lessons
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op


revision = "0014_kg_skill_graph"
down_revision = "0013_lessons"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS kg_edges (
            id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            src_concept  TEXT NOT NULL,
            dst_concept  TEXT NOT NULL,
            relation     TEXT NOT NULL DEFAULT 'prereq',
            weight       REAL NOT NULL DEFAULT 1.0,
            note         TEXT,
            created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (src_concept, dst_concept, relation)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_kg_edges_src ON kg_edges (src_concept)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_kg_edges_dst ON kg_edges (dst_concept)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS skill_atoms (
            id            TEXT PRIMARY KEY,
            subject       TEXT NOT NULL,
            difficulty    TEXT NOT NULL DEFAULT 'medium',
            parent_atom   TEXT REFERENCES skill_atoms(id) ON DELETE SET NULL,
            display_en    TEXT,
            display_he    TEXT,
            description   TEXT,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_skill_atoms_subject ON skill_atoms (subject)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_skill_atoms (
            lesson_id   UUID NOT NULL REFERENCES lessons(id)  ON DELETE CASCADE,
            skill_atom  TEXT NOT NULL REFERENCES skill_atoms(id) ON DELETE CASCADE,
            role        TEXT NOT NULL DEFAULT 'teaches',
            PRIMARY KEY (lesson_id, skill_atom, role)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_skill_atoms_lesson ON lesson_skill_atoms (lesson_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_skill_atoms_atom ON lesson_skill_atoms (skill_atom)"
    )

    op.execute(
        """
        ALTER TABLE lesson_questions
            ADD COLUMN IF NOT EXISTS answer_payload JSONB
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE lesson_questions DROP COLUMN IF EXISTS answer_payload")
    op.execute("DROP TABLE IF EXISTS lesson_skill_atoms")
    op.execute("DROP TABLE IF EXISTS skill_atoms")
    op.execute("DROP TABLE IF EXISTS kg_edges")
