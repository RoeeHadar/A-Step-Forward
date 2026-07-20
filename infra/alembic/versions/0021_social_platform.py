"""Social identity, notifications, teacher-student links, friendships.

Revision ID: 0021_social_platform
Revises: 0020_weekly_quiz_rotation
Create Date: 2026-07-20
"""

from __future__ import annotations

from alembic import op

revision = "0021_social_platform"
down_revision = "0020_weekly_quiz_rotation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS app_users (
            clerk_user_id   TEXT PRIMARY KEY,
            role            TEXT NOT NULL CHECK (role IN ('learner', 'educator')),
            username        TEXT NOT NULL,
            real_name       TEXT NOT NULL,
            nickname        TEXT,
            about_me        TEXT,
            profile_complete BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_app_users_username_lower ON app_users (lower(username))"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_app_users_real_name ON app_users (lower(real_name))")
    op.execute("CREATE INDEX IF NOT EXISTS ix_app_users_role ON app_users (role)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id     TEXT NOT NULL,
            kind        TEXT NOT NULL,
            title       TEXT NOT NULL,
            body        TEXT NOT NULL DEFAULT '',
            payload     JSONB NOT NULL DEFAULT '{}'::jsonb,
            href        TEXT,
            read_at     TIMESTAMPTZ,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_user ON notifications (user_id, created_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS teacher_student_links (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            teacher_id    TEXT NOT NULL REFERENCES app_users(clerk_user_id),
            student_id    TEXT NOT NULL REFERENCES app_users(clerk_user_id),
            status        TEXT NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending', 'accepted', 'declined', 'revoked')),
            initiated_by  TEXT NOT NULL,
            message       TEXT,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            responded_at  TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_ts_links_teacher ON teacher_student_links (teacher_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_ts_links_student ON teacher_student_links (student_id, status)"
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_ts_one_active_teacher
        ON teacher_student_links (student_id)
        WHERE status IN ('pending', 'accepted')
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS friendships (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            requester_id  TEXT NOT NULL REFERENCES app_users(clerk_user_id),
            addressee_id  TEXT NOT NULL REFERENCES app_users(clerk_user_id),
            status        TEXT NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending', 'accepted', 'declined', 'revoked')),
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            responded_at  TIMESTAMPTZ,
            CHECK (requester_id <> addressee_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_friendships_requester ON friendships (requester_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_friendships_addressee ON friendships (addressee_id, status)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS teacher_notes (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            teacher_id    TEXT NOT NULL,
            student_id    TEXT NOT NULL,
            kind          TEXT NOT NULL DEFAULT 'note',
            content       TEXT NOT NULL,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_teacher_notes_student ON teacher_notes (student_id, created_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS teacher_audit_log (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            teacher_id    TEXT NOT NULL,
            student_id    TEXT NOT NULL,
            action        TEXT NOT NULL,
            reason        TEXT,
            payload       JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_teacher_audit_student ON teacher_audit_log (student_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS teacher_audit_log")
    op.execute("DROP TABLE IF EXISTS teacher_notes")
    op.execute("DROP TABLE IF EXISTS friendships")
    op.execute("DROP TABLE IF EXISTS teacher_student_links")
    op.execute("DROP TABLE IF EXISTS notifications")
    op.execute("DROP TABLE IF EXISTS app_users")
