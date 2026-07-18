"""Internal question-item store (RAG bank) for verified, retrievable questions.

Adds ``question_items`` — the canonical store of composite (multi-part) questions
used to (a) populate lessons' baked-in ``questions[]`` offline and (b) power the
educator-only on-the-fly quiz/test builder. Retrieval is structured-filter-first
(concept / skill-atom / difficulty / level) with an optional pgvector semantic
fallback, so the ``embedding`` column is nullable and populated offline.

Design notes:
- Items are composite: a shared ``stem_en`` / ``stem_he`` plus an ordered
  ``parts`` array (>= 1). A single-part question is the degenerate one-part case.
- ``license`` / ``source`` / ``display_publicly`` enforce the source-tier policy
  (MoE Meyda verbatim + answer keys; everything else generated / style-only).
- ``verification_status`` gates graded retrieval and baking: only ``auto_verified``
  or ``human_verified`` items are eligible.
- ``parameter_spec`` / ``answer_formula`` enable deterministic parameterized
  re-generation so an educator can vary numbers without an LLM guessing the answer.

Revision ID: 0018_question_store
Revises: 0017_merge_plan_wellbeing_heads
Create Date: 2026-07-18
"""

from __future__ import annotations

from alembic import op

revision = "0018_question_store"
down_revision = "0017_merge_plan_wellbeing_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector is created in 0001_init; keep this idempotent for fresh DBs.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS question_items (
            id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            concept_id          TEXT NOT NULL,
            extra_concept_ids   TEXT[] NOT NULL DEFAULT '{}',
            subject             TEXT NOT NULL,
            level               TEXT NOT NULL,
            math_track          TEXT[] NOT NULL DEFAULT '{}',
            points_level        TEXT,
            kind                TEXT NOT NULL,
            difficulty          TEXT NOT NULL,
            stem_en             TEXT NOT NULL DEFAULT '',
            stem_he             TEXT NOT NULL DEFAULT '',
            parts               JSONB NOT NULL DEFAULT '[]'::jsonb,
            skill_atoms         JSONB NOT NULL DEFAULT '[]'::jsonb,
            answer_payload      JSONB,
            est_seconds         INT,
            source              TEXT NOT NULL DEFAULT 'generated',
            source_ref          TEXT,
            license             TEXT NOT NULL DEFAULT 'generated-original',
            provenance          JSONB,
            display_publicly    BOOLEAN NOT NULL DEFAULT FALSE,
            verification_status TEXT NOT NULL DEFAULT 'unverified',
            verification        JSONB,
            parameter_spec      JSONB,
            answer_formula      JSONB,
            embedding           vector(1024),
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )

    # Structured-filter-first retrieval: concept + difficulty is the hot path.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qi_concept_diff ON question_items (concept_id, difficulty)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qi_subject_level ON question_items (subject, level)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qi_verification ON question_items (verification_status)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_qi_source ON question_items (source)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qi_skill_atoms ON question_items USING GIN (skill_atoms)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qi_extra_concepts ON question_items USING GIN (extra_concept_ids)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qi_math_track ON question_items USING GIN (math_track)"
    )
    # Semantic fallback for natural-language educator queries; embeddings are
    # populated offline, so the index simply ignores NULL rows.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_qi_embedding_hnsw
        ON question_items USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_qi_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_qi_math_track")
    op.execute("DROP INDEX IF EXISTS ix_qi_extra_concepts")
    op.execute("DROP INDEX IF EXISTS ix_qi_skill_atoms")
    op.execute("DROP INDEX IF EXISTS ix_qi_source")
    op.execute("DROP INDEX IF EXISTS ix_qi_verification")
    op.execute("DROP INDEX IF EXISTS ix_qi_subject_level")
    op.execute("DROP INDEX IF EXISTS ix_qi_concept_diff")
    op.execute("DROP TABLE IF EXISTS question_items")
