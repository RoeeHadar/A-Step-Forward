"""SQLAlchemy ORM models for adaptive learner tables (migration 0010)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LearnerProfileRow(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    grade_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    points_group: Mapped[str | None] = mapped_column(String(16), nullable=True)
    subjects: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    hours_per_week: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    preferred_style: Mapped[str | None] = mapped_column(String(32), nullable=True)
    attention_span: Mapped[int | None] = mapped_column(Integer, nullable=True)
    self_scores: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    background_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConceptMasteryRow(Base):
    __tablename__ = "concept_mastery"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(String(128), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    data_points: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MasterySnapshotRow(Base):
    __tablename__ = "mastery_snapshots"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    scores: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
