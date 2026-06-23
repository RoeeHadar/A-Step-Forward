"""SQLAlchemy ORM models for curriculum content."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CurriculumCourse(Base):
    __tablename__ = "curriculum_courses"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class CurriculumConcept(Base):
    __tablename__ = "curriculum_concepts"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    prerequisites: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class CurriculumLessonIndex(Base):
    __tablename__ = "curriculum_lessons"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    unit_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    concepts: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    est_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="15")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
