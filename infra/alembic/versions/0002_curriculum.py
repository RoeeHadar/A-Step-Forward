"""Create curriculum tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_curriculum"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "curriculum_courses",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("prerequisites", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "curriculum_concepts",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("course_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("prerequisites", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_curriculum_concepts_course_id", "curriculum_concepts", ["course_id"])
    op.create_table(
        "curriculum_lessons",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("course_id", sa.String(length=128), nullable=False),
        sa.Column("unit_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("concepts", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("est_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_curriculum_lessons_course_id", "curriculum_lessons", ["course_id"])
    op.create_index("ix_curriculum_lessons_unit_id", "curriculum_lessons", ["unit_id"])


def downgrade() -> None:
    op.drop_index("ix_curriculum_lessons_unit_id", table_name="curriculum_lessons")
    op.drop_index("ix_curriculum_lessons_course_id", table_name="curriculum_lessons")
    op.drop_table("curriculum_lessons")
    op.drop_index("ix_curriculum_concepts_course_id", table_name="curriculum_concepts")
    op.drop_table("curriculum_concepts")
    op.drop_table("curriculum_courses")
