"""ORM models for learning plans and weekly quizzes."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LearningPlanRow(Base):
    __tablename__ = "learning_plans"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PlanWeekRow(Base):
    __tablename__ = "plan_weeks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    plan_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    concepts: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    content_ids: Mapped[list[UUID] | None] = mapped_column(ARRAY(PGUUID(as_uuid=True)), nullable=True)
    quiz_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="upcoming")


class WeeklyQuizRow(Base):
    __tablename__ = "weekly_quizzes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    week_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    time_limit_s: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1800")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    per_topic: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="pending")
