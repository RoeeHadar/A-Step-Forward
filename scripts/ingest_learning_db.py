#!/usr/bin/env python3
"""Ingest Learning Database PDFs into content_sections and bagrut_exams.

Usage:
    uv run python scripts/ingest_learning_db.py --db-url $DATABASE_URL \\
        --source "Learning Database/" --storage-bucket $R2_BUCKET_NAME

    uv run python scripts/ingest_learning_db.py --watch  # monitor for changes

Bagrut folders (path contains "Bagrut") are uploaded as raw PDFs.
All other PDFs are parsed into chapter sections (Markdown + KaTeX heuristics).
Idempotent by (subject, source_file, chunk_index) / (subject, source_file).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

CHAPTER_MARKERS = re.compile(
    r"^(?:פרק|יחידה|פרק\s+\d+|יחידה\s+\d+|Chapter\s+\d+|Unit\s+\d+)",
    re.MULTILINE | re.IGNORECASE,
)
MATH_INLINE = re.compile(r"(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)")
MATH_DISPLAY = re.compile(r"\$\$([\s\S]+?)\$\$")
BAGRUT_YEAR = re.compile(r"(20\d{2})")


@dataclass
class IngestStats:
    processed: int = 0
    sections: int = 0
    bagrut: int = 0
    skipped: int = 0
    failed: list[dict[str, str]] = field(default_factory=list)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug[:80] or "subject"


def _subject_from_path(source_root: Path, pdf_path: Path) -> str:
    rel = pdf_path.relative_to(source_root)
    parts = list(rel.parts[:-1])
    if not parts:
        return "general"
    return _slugify(parts[0])


def _grade_from_path(pdf_path: Path) -> str | None:
    path_lower = str(pdf_path).lower()
    for token, grade in (
        ("7th grade", "7th"),
        ("8th grade", "8th"),
        ("9th grade", "9th"),
        ("10th grade", "10th"),
        ("11th grade", "11th"),
        ("12th grade", "12th"),
        ("middle school", "middle"),
        ("university", "university"),
        ("calculus", "university"),
        ("physics 1", "university"),
        ("physics 2", "university"),
    ):
        if token in path_lower:
            return grade
    return None


def _is_bagrut(path: Path) -> bool:
    return "bagrut" in str(path).lower()


def _exam_type_from_path(path: Path) -> str:
    parts = [p for p in path.parts if "bagrut" not in p.lower()]
    for part in reversed(parts):
        if "bagrut" in part.lower():
            continue
        if part.lower().endswith(".pdf"):
            continue
        return _slugify(part)
    return "general"


def _display_name(filename: str) -> str:
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    return stem.strip() or filename


def _extract_year(filename: str) -> int | None:
    match = BAGRUT_YEAR.search(filename)
    if match:
        return int(match.group(1))
    return None


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def _extract_pdf_text(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (page_num, text) pairs. Tries pdfplumber then PyMuPDF."""
    pages: list[tuple[int, str]] = []
    try:
        import pdfplumber  # type: ignore[import-untyped]

        with pdfplumber.open(pdf_path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                pages.append((idx, text))
        if any(t.strip() for _, t in pages):
            return pages
    except Exception:
        pass

    try:
        import fitz  # type: ignore[import-untyped]  # PyMuPDF

        doc = fitz.open(pdf_path)
        for idx in range(len(doc)):
            text = doc[idx].get_text("text") or ""
            pages.append((idx + 1, text))
        doc.close()
    except Exception as exc:
        raise RuntimeError(f"PDF extract failed: {exc}") from exc
    return pages


def _split_chapters(pages: list[tuple[int, str]]) -> list[dict[str, Any]]:
    """Split PDF pages into chapters using Hebrew/English heading markers."""
    full_text = "\n\n".join(text for _, text in pages if text.strip())
    if not full_text.strip():
        return [{"title": "תוכן", "body_md": "", "page_start": 1, "page_end": len(pages)}]

    chapters: list[dict[str, Any]] = []
    current_title = "מבוא"
    current_lines: list[str] = []
    page_start = 1

    def flush(end_page: int) -> None:
        nonlocal current_lines, current_title, page_start
        body = "\n".join(current_lines).strip()
        if body or len(chapters) == 0:
            chapters.append(
                {
                    "title": current_title,
                    "body_md": _text_to_markdown(body),
                    "page_start": page_start,
                    "page_end": end_page,
                }
            )
        current_lines = []

    for page_num, page_text in pages:
        for line in page_text.splitlines():
            stripped = line.strip()
            if stripped and CHAPTER_MARKERS.match(stripped):
                if current_lines:
                    flush(page_num)
                current_title = stripped
                page_start = page_num
            elif stripped:
                current_lines.append(stripped)

    flush(pages[-1][0] if pages else 1)

    if len(chapters) == 1 and len(chapters[0]["body_md"]) < 100:
        # Fallback: one section per ~8 pages
        chapters = []
        chunk_size = 8
        for i in range(0, len(pages), chunk_size):
            chunk = pages[i : i + chunk_size]
            body = "\n\n".join(t for _, t in chunk if t.strip())
            chapters.append(
                {
                    "title": f"חלק {len(chapters) + 1}",
                    "body_md": _text_to_markdown(body),
                    "page_start": chunk[0][0],
                    "page_end": chunk[-1][0],
                }
            )
    return chapters


def _text_to_markdown(text: str) -> str:
    """Light heuristics: preserve math-like tokens as inline LaTeX."""
    if not text.strip():
        return ""
    # Wrap common math patterns
    text = re.sub(r"([=+\-*/^₀₁₂₃₄₅₆₇₈₉√∫∑∂∞≤≥≠±])", r" $\1$ ", text)
    text = MATH_DISPLAY.sub(r"$$\1$$", text)
    text = MATH_INLINE.sub(r"$\1$", text)
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    return "\n\n".join(paragraphs)


async def _upload_pdf(
    pdf_path: Path,
    *,
    bucket: str | None,
    public_dir: Path,
) -> str:
    """Upload to R2/S3 or copy to public dir. Returns public URL path."""
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
    dest_name = f"{digest}_{pdf_path.name}"
    public_dir.mkdir(parents=True, exist_ok=True)
    dest = public_dir / dest_name
    if not dest.exists():
        shutil.copy2(pdf_path, dest)
    local_url = f"/content/bagrut/{dest_name}"

    if not bucket:
        return local_url

    endpoint = os.environ.get("S3_ENDPOINT") or os.environ.get("R2_ENDPOINT")
    access_key = os.environ.get("S3_ACCESS_KEY") or os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("S3_SECRET_KEY") or os.environ.get("R2_SECRET_ACCESS_KEY")
    public_base = os.environ.get("R2_PUBLIC_URL") or os.environ.get("S3_PUBLIC_URL")

    if not all([endpoint, access_key, secret_key]):
        return local_url

    try:
        import boto3  # type: ignore[import-untyped]

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=os.environ.get("S3_REGION", "auto"),
        )
        key = f"bagrut/{dest_name}"
        client.upload_file(str(pdf_path), bucket, key, ExtraArgs={"ContentType": "application/pdf"})
        if public_base:
            return f"{public_base.rstrip('/')}/{key}"
    except Exception:
        pass
    return local_url


async def _upsert_section(
    session: Any,
    *,
    subject: str,
    grade: str | None,
    source_file: str,
    chunk_index: int,
    title: str,
    body_md: str,
    page_start: int | None,
    page_end: int | None,
) -> None:
    from sqlalchemy import text

    await session.execute(
        text(
            """
            INSERT INTO content_sections
                (subject, grade, source_file, chunk_index, title, body_md,
                 page_start, page_end, updated_at)
            VALUES
                (:subject, :grade, :source_file, :chunk_index, :title, :body_md,
                 :page_start, :page_end, NOW())
            ON CONFLICT (subject, source_file, chunk_index) DO UPDATE SET
                grade = EXCLUDED.grade,
                title = EXCLUDED.title,
                body_md = EXCLUDED.body_md,
                page_start = EXCLUDED.page_start,
                page_end = EXCLUDED.page_end,
                updated_at = NOW()
            """
        ),
        {
            "subject": subject,
            "grade": grade,
            "source_file": source_file,
            "chunk_index": chunk_index,
            "title": title,
            "body_md": body_md,
            "page_start": page_start,
            "page_end": page_end,
        },
    )


async def _upsert_bagrut(
    session: Any,
    *,
    subject: str,
    exam_type: str,
    year: int | None,
    source_file: str,
    display_name: str,
    file_url: str,
) -> None:
    from sqlalchemy import text

    await session.execute(
        text(
            """
            INSERT INTO bagrut_exams
                (subject, exam_type, year, source_file, display_name, file_url)
            VALUES
                (:subject, :exam_type, :year, :source_file, :display_name, :file_url)
            ON CONFLICT (subject, source_file) DO UPDATE SET
                exam_type = EXCLUDED.exam_type,
                year = EXCLUDED.year,
                display_name = EXCLUDED.display_name,
                file_url = EXCLUDED.file_url
            """
        ),
        {
            "subject": subject,
            "exam_type": exam_type,
            "year": year,
            "source_file": source_file,
            "display_name": display_name,
            "file_url": file_url,
        },
    )


async def _update_status(session: Any, failed: list[dict[str, str]]) -> None:
    from sqlalchemy import text

    await session.execute(
        text(
            """
            UPDATE content_ingest_status
            SET last_ingest_at = :ts, failed_files = CAST(:failed AS jsonb)
            WHERE id = 1
            """
        ),
        {"ts": datetime.now(UTC), "failed": json.dumps(failed)},
    )


async def ingest_file(
    pdf_path: Path,
    *,
    source_root: Path,
    session: Any,
    bucket: str | None,
    public_dir: Path,
    stats: IngestStats,
) -> None:
    subject = _subject_from_path(source_root, pdf_path)
    source_file = pdf_path.name
    grade = _grade_from_path(pdf_path)

    if _is_bagrut(pdf_path):
        file_url = await _upload_pdf(pdf_path, bucket=bucket, public_dir=public_dir)
        await _upsert_bagrut(
            session,
            subject=subject,
            exam_type=_exam_type_from_path(pdf_path),
            year=_extract_year(source_file),
            source_file=source_file,
            display_name=_display_name(source_file),
            file_url=file_url,
        )
        stats.bagrut += 1
        stats.processed += 1
        return

    pages = _extract_pdf_text(pdf_path)
    if not any(t.strip() for _, t in pages):
        stats.skipped += 1
        stats.failed.append({"file": str(pdf_path), "reason": "no extractable text"})
        return

    chapters = _split_chapters(pages)
    for idx, chapter in enumerate(chapters):
        body = chapter["body_md"]
        if not body.strip():
            continue
        await _upsert_section(
            session,
            subject=subject,
            grade=grade,
            source_file=source_file,
            chunk_index=idx,
            title=chapter["title"],
            body_md=body,
            page_start=chapter.get("page_start"),
            page_end=chapter.get("page_end"),
        )
        stats.sections += 1

    stats.processed += 1


async def run_ingest(args: argparse.Namespace) -> IngestStats:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    source_root = Path(args.source).resolve()
    if not source_root.is_dir():
        print(f"[error] source not found: {source_root}")
        return IngestStats(failed=[{"file": str(source_root), "reason": "not a directory"}])

    db_url = args.db_url or os.environ.get("DATABASE_URL")
    if not db_url:
        print("[error] --db-url or DATABASE_URL required")
        return IngestStats(failed=[{"file": "", "reason": "no database url"}])

    public_dir = ROOT / "apps" / "web" / "public" / "content" / "bagrut"
    stats = IngestStats()
    pdfs = sorted(source_root.rglob("*.pdf"))

    engine = create_async_engine(_normalize_database_url(db_url), pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        for pdf_path in pdfs:
            try:
                await ingest_file(
                    pdf_path,
                    source_root=source_root,
                    session=session,
                    bucket=args.storage_bucket or os.environ.get("R2_BUCKET_NAME"),
                    public_dir=public_dir,
                    stats=stats,
                )
                print(f"[ok] {pdf_path.relative_to(source_root)}")
            except Exception as exc:
                stats.failed.append({"file": str(pdf_path), "reason": str(exc)})
                print(f"[fail] {pdf_path}: {exc}")

        await _update_status(session, stats.failed)
        await session.commit()

    await engine.dispose()
    return stats


def _watch(source: Path, db_url: str, bucket: str | None) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("[error] watchdog not installed — run: uv pip install watchdog")
        sys.exit(1)

    class Handler(FileSystemEventHandler):
        def on_created(self, event: Any) -> None:
            if event.is_directory or not str(event.src_path).lower().endswith(".pdf"):
                return
            print(f"[watch] new file: {event.src_path}")
            asyncio.run(
                run_ingest(
                    argparse.Namespace(
                        source=str(source),
                        db_url=db_url,
                        storage_bucket=bucket,
                    )
                )
            )

        def on_modified(self, event: Any) -> None:
            self.on_created(event)

    observer = Observer()
    observer.schedule(Handler(), str(source), recursive=True)
    observer.start()
    print(f"[watch] monitoring {source} — Ctrl+C to stop")
    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Learning Database PDFs.")
    parser.add_argument("--source", default="Learning Database/", help="Root folder of PDFs")
    parser.add_argument("--db-url", default="", help="Postgres URL (or DATABASE_URL env)")
    parser.add_argument("--storage-bucket", default="", help="R2/S3 bucket for Bagrut PDFs")
    parser.add_argument("--watch", action="store_true", help="Watch folder for new/changed PDFs")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    db_url = args.db_url or os.environ.get("DATABASE_URL", "")

    if args.watch:
        _watch(source, db_url, args.storage_bucket or None)
        return 0

    stats = asyncio.run(run_ingest(args))
    print(
        f"\nSummary: processed={stats.processed} sections={stats.sections} "
        f"bagrut={stats.bagrut} skipped={stats.skipped} failed={len(stats.failed)}"
    )
    return 0 if not stats.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
