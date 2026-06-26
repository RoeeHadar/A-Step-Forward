"""Per-learner persona + per-(learner, agent) cumulative notes + bilingual
diagnostic items.

Three independent additions, packed into one migration because they all
serve the same Round 9 goal — give every runtime agent durable, per-user
context (a CLAUDE.md-style learner persona) plus a private, additive
scratchpad (agent notes), and make the starting diagnostic bilingual so
brand-new Israeli learners see Hebrew on first contact.

Adds:

1. ``learner_profiles.learner_persona`` (TEXT, nullable). Free-form,
   markdown-friendly CLAUDE.md-style summary of how the learner thinks,
   talks, and learns. All runtime agents read it on every turn; the
   Memory Steward (or any agent allowed to) appends/rewrites it. Never
   exposes PII; PII is stripped before write.

2. ``learner_agent_notes`` — per-(learner, agent) cumulative, additive
   notes that survive across chat sessions. This is the agent-private
   memory channel: each agent (tutor, mentor, coach, …) has its OWN
   scratchpad about THIS learner that no other agent reads. Indexed for
   "give me the top N most-important most-recent notes for (learner,
   agent)" which is what the chat route loads into context per turn.

3. ``diagnostic_items.stem_he`` + ``options_he`` + ``explanation_he`` —
   bilingual variants. The existing EN columns stay as-is for backwards
   compat; if the HE column is NULL, the UI falls back to EN.

Revision ID: 0015_learner_persona_and_agent_notes
Revises: 0014_kg_skill_graph
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op


revision = "0015_learner_persona_and_agent_notes"
down_revision = "0014_kg_skill_graph"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. learner_persona on learner_profiles
    op.execute(
        "ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS learner_persona TEXT"
    )
    op.execute(
        "ALTER TABLE learner_profiles "
        "ADD COLUMN IF NOT EXISTS learner_persona_updated_at TIMESTAMPTZ"
    )

    # 2. Per-(learner, agent) cumulative notes
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS learner_agent_notes (
            id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id         TEXT NOT NULL,
            agent              TEXT NOT NULL,
            kind               TEXT NOT NULL DEFAULT 'observation',
            content            TEXT NOT NULL,
            importance         INT  NOT NULL DEFAULT 3,
            related_concept_id TEXT,
            source_turn_id     UUID,
            superseded_by      UUID REFERENCES learner_agent_notes(id) ON DELETE SET NULL,
            archived_at        TIMESTAMPTZ,
            last_referenced_at TIMESTAMPTZ,
            created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lan_learner_agent_time "
        "ON learner_agent_notes (learner_id, agent, created_at DESC) "
        "WHERE archived_at IS NULL AND superseded_by IS NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lan_learner_agent_importance "
        "ON learner_agent_notes (learner_id, agent, importance DESC, created_at DESC) "
        "WHERE archived_at IS NULL AND superseded_by IS NULL"
    )

    # 3. Bilingual diagnostic items
    op.execute(
        "ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS stem_he TEXT"
    )
    op.execute(
        "ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS options_he JSONB"
    )
    op.execute(
        "ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS explanation_he TEXT"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE diagnostic_items DROP COLUMN IF EXISTS explanation_he")
    op.execute("ALTER TABLE diagnostic_items DROP COLUMN IF EXISTS options_he")
    op.execute("ALTER TABLE diagnostic_items DROP COLUMN IF EXISTS stem_he")
    op.execute("DROP TABLE IF EXISTS learner_agent_notes")
    op.execute(
        "ALTER TABLE learner_profiles DROP COLUMN IF EXISTS learner_persona_updated_at"
    )
    op.execute("ALTER TABLE learner_profiles DROP COLUMN IF EXISTS learner_persona")
