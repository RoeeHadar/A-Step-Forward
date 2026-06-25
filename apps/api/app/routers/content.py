"""Public content browsing routes (free tier — no auth)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.content import (
    BagrutExam,
    ContentSection,
    ContentSectionsPage,
    SubjectSummary,
)

from ..core.db import get_db
from ..stores import content_store

router = APIRouter(prefix="/v1/content", tags=["content"])


@router.get(
    "/subjects",
    response_model=list[SubjectSummary],
    summary="List content subjects",
    description="Distinct subjects from textbook sections and Bagrut exams (public, no auth).",
)
async def list_subjects(session=Depends(get_db)) -> list[SubjectSummary]:
    rows = await content_store.list_subjects(session)
    return [SubjectSummary.model_validate(r) for r in rows]


@router.get(
    "/subjects/{subject}/sections",
    response_model=ContentSectionsPage,
    summary="List textbook sections for a subject",
    description="Paginated sections with markdown body. Optional grade filter.",
)
async def list_sections(
    subject: str,
    grade: str | None = Query(default=None, description="Filter by grade level"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session=Depends(get_db),
) -> ContentSectionsPage:
    rows, total = await content_store.list_sections(
        session,
        subject=subject,
        grade=grade,
        page=page,
        page_size=page_size,
    )
    return ContentSectionsPage(
        items=[ContentSection.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/subjects/{subject}/sections/{chunk_index}",
    response_model=ContentSection,
    summary="Get a single textbook section",
    description="Full section detail by chunk index (public, no auth).",
)
async def get_section(
    subject: str,
    chunk_index: int,
    session=Depends(get_db),
) -> ContentSection:
    row = await content_store.get_section(session, subject=subject, chunk_index=chunk_index)
    if row is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return ContentSection(
        subject=row["subject"],
        grade=row.get("grade"),
        title=row["title"],
        body_md=row["body_md"],
        page_start=row.get("page_start"),
        page_end=row.get("page_end"),
        chunk_index=row.get("chunk_index"),
    )


@router.get(
    "/subjects/{subject}/bagrut",
    response_model=list[BagrutExam],
    summary="List Bagrut exams for a subject",
    description="Bagrut exam PDF metadata for the subject (public, no auth).",
)
async def list_bagrut(subject: str, session=Depends(get_db)) -> list[BagrutExam]:
    rows = await content_store.list_bagrut_exams(session, subject=subject)
    return [
        BagrutExam(
            display_name=r["display_name"],
            file_url=r["file_url"],
            year=r.get("year"),
            exam_type=r["exam_type"],
        )
        for r in rows
    ]
