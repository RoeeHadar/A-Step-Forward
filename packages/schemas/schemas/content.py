"""Public free-tier content browsing schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SubjectSummary(BaseModel):
    subject: str
    section_count: int = 0
    sample_grade: str | None = None


class ContentSection(BaseModel):
    subject: str
    grade: str | None = None
    title: str
    body_md: str
    page_start: int | None = None
    page_end: int | None = None
    chunk_index: int | None = None


class ContentSectionsPage(BaseModel):
    items: list[ContentSection]
    total: int
    page: int
    page_size: int


class BagrutExam(BaseModel):
    display_name: str
    file_url: str
    year: int | None = None
    exam_type: str


class BagrutExamList(BaseModel):
    items: list[BagrutExam]
