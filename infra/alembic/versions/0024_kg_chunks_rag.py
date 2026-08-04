"""Recreate kg_chunks as a bilingual hybrid-RAG store (dense + lexical).

Revision ID: 0024_kg_chunks_rag
Revises: 0023_lesson_booking_settings
Create Date: 2026-08-04

Phase 2 (RAG foundation). We reuse `kg_chunks` (rather than a separate
`rag_chunks`) as the single vector+lexical store for learner-facing retrieval.

The embedding model is `nvidia/nv-embedqa-e5-v5` (NVIDIA NIM, multilingual E5,
**1024-dim**, asymmetric passage/query) — a hosted, stateless embedding used for
BOTH offline ingestion and query-time. This avoids in-process model loading on
Vercel (bundle-size / cold-start) and guarantees ingest/query model parity. If
the embedding API is unavailable at query time, retrieval degrades to the
lexical channel (pg_trgm + tsvector), so `embedding` is nullable.

`kg_chunks` previously held `embedding vector(384)` (migration 0006) for an
unused GraphRAG path and is empty in every environment, so a drop+recreate is
safe — same precedent and assumption as 0006. Downgrade restores the 0006 shape.

Columns:
  id            : deterministic "{source_type}:{source_doc_id}:{lang}:{ordinal}"
  document_id   : back-compat mirror of source_doc_id
  source_type   : 'lesson' | 'question' | 'kg_concept' | 'exam_style' | 'mock_exam'
  source_doc_id : source document identity (e.g. lesson concept_id / file base)
  concept_id    : NULLABLE KG concept link (~217 lessons are non-KG track variants)
  lang          : 'en' | 'he'  (one row per language)
  ordinal       : chunk index within (source_doc_id, lang)
  heading       : section/heading label
  text          : chunk text (embedded + lexically indexed)
  token_count   : approx tokens
  content_hash  : sha256 of normalized text for idempotent, cost-aware re-embed
  embedding     : vector(1024), NULLABLE (lexical-only rows allowed)
  provenance    : JSONB source metadata
  tsv           : generated to_tsvector('simple', text) — 'simple' works for HE+EN
"""

from __future__ import annotations

from alembic import op

revision = "0024_kg_chunks_rag"
down_revision = "0023_lesson_booking_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Safe dimension migration. kg_chunks was vector(384) (0006) for an unused
    # GraphRAG path and is empty in every environment. Rather than an
    # unconditional DROP, we only recreate when the embedding dimension differs
    # from 1024 AND the table is empty. If it somehow holds rows at the wrong
    # dimension we RAISE instead of destroying data — the operator must migrate
    # it deliberately. This makes the migration safe to run via CI against prod.
    op.execute(
        """
        DO $$
        DECLARE
            emb_dim integer;
            row_n bigint;
        BEGIN
            IF to_regclass('public.kg_chunks') IS NOT NULL THEN
                SELECT a.atttypmod INTO emb_dim
                FROM pg_attribute a
                JOIN pg_class c ON c.oid = a.attrelid
                WHERE c.relname = 'kg_chunks'
                  AND a.attname = 'embedding'
                  AND NOT a.attisdropped;
                IF emb_dim IS DISTINCT FROM 1024 THEN
                    EXECUTE 'SELECT count(*) FROM kg_chunks' INTO row_n;
                    IF row_n > 0 THEN
                        RAISE EXCEPTION
                          'kg_chunks has % row(s) at embedding dim % (expected 1024); refusing to drop non-empty table. Migrate data deliberately.',
                          row_n, emb_dim;
                    END IF;
                    DROP TABLE kg_chunks;
                END IF;
            END IF;
        END $$;
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS kg_chunks (
            id VARCHAR(160) PRIMARY KEY,
            document_id VARCHAR(128) NOT NULL,
            source_type VARCHAR(32) NOT NULL,
            source_doc_id VARCHAR(128) NOT NULL,
            concept_id VARCHAR(128),
            lang VARCHAR(8) NOT NULL,
            ordinal INTEGER NOT NULL,
            heading VARCHAR(512),
            text TEXT NOT NULL,
            token_count INTEGER,
            content_hash VARCHAR(64),
            embedding vector(1024),
            provenance JSONB,
            tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(text, ''))) STORED,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )

    # Belt-and-suspenders for a pre-existing 1024 table that lacks RAG columns.
    op.execute("ALTER TABLE kg_chunks ADD COLUMN IF NOT EXISTS source_type VARCHAR(32)")
    op.execute("ALTER TABLE kg_chunks ADD COLUMN IF NOT EXISTS source_doc_id VARCHAR(128)")
    op.execute("ALTER TABLE kg_chunks ADD COLUMN IF NOT EXISTS concept_id VARCHAR(128)")
    op.execute("ALTER TABLE kg_chunks ADD COLUMN IF NOT EXISTS lang VARCHAR(8)")
    op.execute("ALTER TABLE kg_chunks ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64)")
    op.execute(
        "ALTER TABLE kg_chunks ADD COLUMN IF NOT EXISTS tsv tsvector "
        "GENERATED ALWAYS AS (to_tsvector('simple', coalesce(text, ''))) STORED"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS kg_chunks_embedding_hnsw_idx ON kg_chunks USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_tsv_idx ON kg_chunks USING gin (tsv)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS kg_chunks_text_trgm_idx ON kg_chunks USING gin (text gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS kg_chunks_source_idx ON kg_chunks (source_type, source_doc_id)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_concept_id_idx ON kg_chunks (concept_id)")
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_lang_idx ON kg_chunks (lang)")
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_content_hash_idx ON kg_chunks (content_hash)")
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_document_id_idx ON kg_chunks (document_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS kg_chunks")
    op.execute(
        """
        CREATE TABLE kg_chunks (
            id VARCHAR(128) PRIMARY KEY,
            document_id VARCHAR(128) NOT NULL,
            ordinal INTEGER NOT NULL,
            text TEXT NOT NULL,
            heading VARCHAR(512),
            token_count INTEGER,
            embedding vector(384) NOT NULL,
            provenance JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_document_id_idx ON kg_chunks (document_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS kg_chunks_embedding_hnsw_idx ON kg_chunks USING hnsw (embedding vector_cosine_ops)"
    )
