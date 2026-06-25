"""Add content_sections and bagrut_exams tables for Learning Database pipeline.

Revision ID: 0008_content_sections
Revises: 0007_memory_events
Create Date: 2026-06-25
"""

from __future__ import annotations

from alembic import op

revision = "0008_content_sections"
down_revision = "0007_memory_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS content_sections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subject TEXT NOT NULL,
            grade TEXT,
            source_file TEXT NOT NULL,
            chunk_index INT NOT NULL,
            title TEXT NOT NULL,
            title_en TEXT,
            body_md TEXT NOT NULL,
            body_html TEXT,
            page_start INT,
            page_end INT,
            tier TEXT NOT NULL DEFAULT 'free',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (subject, source_file, chunk_index)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_content_sections_subject
        ON content_sections(subject)
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bagrut_exams (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subject TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            year INT,
            source_file TEXT NOT NULL,
            display_name TEXT NOT NULL,
            file_url TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (subject, source_file)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_bagrut_exams_subject
        ON bagrut_exams(subject)
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS content_ingest_status (
            id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
            last_ingest_at TIMESTAMPTZ,
            failed_files JSONB DEFAULT '[]'::jsonb
        )
        """
    )
    op.execute(
        """
        INSERT INTO content_ingest_status (id) VALUES (1)
        ON CONFLICT (id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS content_ingest_status")
    op.execute("DROP INDEX IF EXISTS idx_bagrut_exams_subject")
    op.execute("DROP TABLE IF EXISTS bagrut_exams")
    op.execute("DROP INDEX IF EXISTS idx_content_sections_subject")
    op.execute("DROP TABLE IF EXISTS content_sections")
