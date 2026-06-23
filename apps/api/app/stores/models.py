"""Gateway-owned SQLAlchemy models (users, sessions, audit)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GatewayUser(Base):
    __tablename__ = "gateway_users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    clerk_user_id: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(256), default="Learner")
    email: Mapped[str | None] = mapped_column(String(320))
    role: Mapped[str] = mapped_column(String(32), default="learner")
    age: Mapped[int | None] = mapped_column()
    child_mode: Mapped[bool] = mapped_column(default=False)
    locale: Mapped[str] = mapped_column(String(16), default="en")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class GatewaySession(Base):
    __tablename__ = "gateway_sessions"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    learner_id: Mapped[str] = mapped_column(String(128), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditGatewayEvent(Base):
    __tablename__ = "audit_gateway_events"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    learner_id: Mapped[str | None] = mapped_column(String(128), index=True)
    action: Mapped[str] = mapped_column(String(64))
    route: Mapped[str] = mapped_column(String(256))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
