"""Alter kg_chunks.embedding to 384 dimensions (sentence-transformers).

Revision ID: 0006_kg_chunks_384
Revises: 0005_kg_chunks
Create Date: 2026-06-24

Table was verified empty before this migration; drop+recreate is safe.
See ADR-0005 for embedding model choice.
"""

from __future__ import annotations

from alembic import op

revision = "0006_kg_chunks_384"
down_revision = "0005_kg_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS kg_chunks_embedding_hnsw_idx")
    op.execute("DROP INDEX IF EXISTS kg_chunks_document_id_idx")
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
        """
        CREATE INDEX IF NOT EXISTS kg_chunks_embedding_hnsw_idx
        ON kg_chunks USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS kg_chunks_embedding_hnsw_idx")
    op.execute("DROP INDEX IF EXISTS kg_chunks_document_id_idx")
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
            embedding vector(1024) NOT NULL,
            provenance JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS kg_chunks_document_id_idx ON kg_chunks (document_id)")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS kg_chunks_embedding_hnsw_idx
        ON kg_chunks USING hnsw (embedding vector_cosine_ops)
        """
    )
