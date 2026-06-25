"""Content sections and Bagrut exam persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_subjects(session: AsyncSession) -> list[dict[str, Any]]:
    result = await session.execute(
        text(
            """
            SELECT s.subject,
                   COALESCE(cs.cnt, 0)::int AS section_count,
                   cs.sample_grade
            FROM (
                SELECT DISTINCT subject FROM content_sections
                UNION
                SELECT DISTINCT subject FROM bagrut_exams
            ) s
            LEFT JOIN (
                SELECT subject, COUNT(*)::int AS cnt, MAX(grade) AS sample_grade
                FROM content_sections
                GROUP BY subject
            ) cs ON s.subject = cs.subject
            ORDER BY s.subject
            """
        )
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


async def list_sections(
    session: AsyncSession,
    *,
    subject: str,
) -> list[dict[str, Any]]:
    result = await session.execute(
        text(
            """
            SELECT id, subject, grade, source_file, chunk_index, title, title_en, tier
            FROM content_sections
            WHERE subject = :subject
            ORDER BY chunk_index
            """
        ),
        {"subject": subject},
    )
    return [dict(r) for r in result.mappings().all()]


async def get_section(
    session: AsyncSession,
    *,
    subject: str,
    chunk_index: int,
) -> dict[str, Any] | None:
    result = await session.execute(
        text(
            """
            SELECT id, subject, grade, source_file, chunk_index, title, title_en,
                   body_md, body_html, page_start, page_end, tier
            FROM content_sections
            WHERE subject = :subject AND chunk_index = :chunk_index
            """
        ),
        {"subject": subject, "chunk_index": chunk_index},
    )
    row = result.mappings().first()
    return dict(row) if row else None


async def list_bagrut_exams(
    session: AsyncSession,
    *,
    subject: str,
) -> list[dict[str, Any]]:
    result = await session.execute(
        text(
            """
            SELECT id, subject, exam_type, year, source_file, display_name, file_url
            FROM bagrut_exams
            WHERE subject = :subject
            ORDER BY year DESC NULLS LAST, display_name
            """
        ),
        {"subject": subject},
    )
    return [dict(r) for r in result.mappings().all()]


async def get_content_status(session: AsyncSession) -> dict[str, Any]:
    sections = await session.execute(text("SELECT COUNT(*)::int AS n FROM content_sections"))
    bagrut = await session.execute(text("SELECT COUNT(*)::int AS n FROM bagrut_exams"))
    status = await session.execute(
        text("SELECT last_ingest_at, failed_files FROM content_ingest_status WHERE id = 1")
    )
    status_row = status.mappings().first()
    failed: list[Any] = []
    last_ingest: str | None = None
    if status_row:
        raw_failed = status_row.get("failed_files")
        if isinstance(raw_failed, str):
            failed = json.loads(raw_failed)
        elif isinstance(raw_failed, list):
            failed = raw_failed
        ts = status_row.get("last_ingest_at")
        if ts is not None:
            last_ingest = ts.isoformat()
    return {
        "total_sections": sections.scalar_one(),
        "total_bagrut_exams": bagrut.scalar_one(),
        "last_ingest_at": last_ingest,
        "failed_files": failed,
    }


async def insert_booking(
    session: AsyncSession,
    *,
    name: str,
    email: str,
    phone: str | None,
    date: str,
    time: str,
    duration_h: float,
    subject: str,
    notes: str | None,
    price_ils: int,
) -> str:
    result = await session.execute(
        text(
            """
            INSERT INTO bookings
                (name, email, phone, date, time, duration_h, subject, notes, price_ils)
            VALUES
                (:name, :email, :phone, CAST(:date AS date), CAST(:time AS time),
                 :duration_h, :subject, :notes, :price_ils)
            RETURNING id::text
            """
        ),
        {
            "name": name,
            "email": email,
            "phone": phone,
            "date": date,
            "time": time,
            "duration_h": duration_h,
            "subject": subject,
            "notes": notes,
            "price_ils": price_ils,
        },
    )
    await session.commit()
    return str(result.scalar_one())


async def update_ingest_status(
    session: AsyncSession,
    *,
    failed_files: list[dict[str, str]],
) -> None:
    await session.execute(
        text(
            """
            UPDATE content_ingest_status
            SET last_ingest_at = :ts, failed_files = CAST(:failed AS jsonb)
            WHERE id = 1
            """
        ),
        {
            "ts": datetime.now(UTC),
            "failed": json.dumps(failed_files),
        },
    )
    await session.commit()
