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
    r"^(?:פרק|יחידה|פרק\s+\d+|יחידה\s+\d+|Chapter\s+\d+|Unit\s+\d+|חלק\s+\S+)",
    re.MULTILINE | re.IGNORECASE,
)
MATH_INLINE = re.compile(r"(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)")
MATH_DISPLAY = re.compile(r"\$\$([\s\S]+?)\$\$")
BAGRUT_YEAR = re.compile(r"(20\d{2})")

# Hebrew character ranges in Unicode (Hebrew block + alphabetic presentation forms)
HEBREW_CHAR = re.compile(r"[\u0590-\u05FF\uFB1D-\uFB4F]")
# Run of Hebrew chars (and Hebrew punctuation like maqaf U+05BE) plus combining marks
HEBREW_RUN = re.compile(r"[\u0590-\u05FF\uFB1D-\uFB4F\u05BE'\"·\.,;:!?\-\u2013\u2014]+")
# Detect a line that's predominantly Hebrew (more Hebrew chars than Latin)
def _is_hebrew_line(line: str) -> bool:
    hebrew = len(HEBREW_CHAR.findall(line))
    latin = sum(1 for c in line if c.isascii() and c.isalpha())
    return hebrew > latin and hebrew > 0


# Common short Hebrew tokens used to detect logical order. These appear
# only when the text is in correct (logical) order — never in visual order.
_COMMON_HE_TOKENS = (
    " של ", " את ", " על ", " אם ", " כי ", " לא ", " זה ",
    " גם ", " או ", " רק ", " יש ", " לפי ", " אך ", " כל ",
    "ה", "ב", "ל", "כ",  # very common prefixes — used in the bigram check below
)
# More-specific multi-char Hebrew words that almost never collide with reversed text
_HEBREW_LOGICAL_WORDS = [
    " של ", " את ", " על ", " אם ", " כי ", " לא ", " זה ",
    " גם ", " או ", " רק ", " יש ", " לפי ", " אך ", " כל ",
    " ולכן ", " מאוד ", " כמו ", " הוא ", " היא ", " היה ",
]


def _count_logical_signals(text: str) -> int:
    """How many recognizable common Hebrew words appear in `text`?
    Higher = more likely to already be in logical order."""
    n = 0
    pad = f" {text} "  # pad so boundary chars match
    for word in _HEBREW_LOGICAL_WORDS:
        i = 0
        while (i := pad.find(word, i)) != -1:
            n += 1
            i += len(word)
    return n


def _fix_visual_order_hebrew(text: str) -> str:
    """Convert Hebrew text from visual (PDF-display) order to logical
    (storage / read) order — but ONLY if it actually appears to be in
    visual order. Modern PyMuPDF (≥1.18) returns logical order for most
    PDFs; older extractors and pdfplumber's text path often return visual
    order. We auto-detect per-line by counting common Hebrew words
    pre/post reversal; if reversal would expose more recognizable words,
    we apply it. Otherwise the line is left untouched.

    Mixed-direction quirks:
    - Inside a Hebrew run we re-reverse Latin/digit tokens so e.g. ``(1744)``
      survives a reversal pass.
    - Lines whose body is predominantly Latin/numeric are never touched.
    """
    if not text:
        return text

    def _reverse_with_latin_correction(line: str) -> str:
        reversed_line = line[::-1]
        return re.sub(
            r"[A-Za-z0-9_]+(?:[.,;:!?][A-Za-z0-9_]+)*",
            lambda m: m.group(0)[::-1],
            reversed_line,
        )

    out: list[str] = []
    for line in text.split("\n"):
        if not _is_hebrew_line(line):
            out.append(line)
            continue
        reversed_line = _reverse_with_latin_correction(line)
        # Only flip if reversal yields strictly more recognizable Hebrew.
        if _count_logical_signals(reversed_line) > _count_logical_signals(line):
            out.append(reversed_line)
        else:
            out.append(line)
    return "\n".join(out)


# Common control glyphs that PDF extraction emits as artifacts
# U+2212 (minus sign), U+00A0 (nbsp), zero-width chars, BOM
ARTIFACT_CHARS = re.compile(r"[\u200B-\u200F\u202A-\u202E\uFEFF\u00AD]")
# Stray bullets at line starts (often from list markers / page-break dashes)
STRAY_BULLETS = re.compile(r"^\s*[\u2212\u2013\u2014•▪◦∙·]\s*", re.MULTILINE)
# Page-number-only lines like "12" or "- 12 -"
PAGE_NUMBER_LINE = re.compile(r"^\s*[\u2212\u2013\u2014\-]?\s*\d{1,3}\s*[\u2212\u2013\u2014\-]?\s*$", re.MULTILINE)
# Multiple blank lines collapsed
MULTI_BLANK = re.compile(r"\n{3,}")


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


def _normalize_database_url(url: str) -> tuple[str, dict]:
    """Strip asyncpg-incompatible query params; return (clean_url, connect_args)."""
    from urllib.parse import parse_qs, urlparse, urlunparse

    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    sslmode = params.pop("sslmode", ["disable"])[0]
    params.pop("channel_binding", None)
    remaining = "&".join(f"{k}={v[0]}" for k, v in params.items())
    clean = urlunparse(parsed._replace(query=remaining))
    connect_args = {"ssl": True} if sslmode in ("require", "verify-ca", "verify-full") else {}
    return clean, connect_args


def _clean_page_text(raw: str) -> str:
    """Strip control-char artifacts and stray bullets/page-numbers; collapse blanks."""
    if not raw:
        return ""
    text = ARTIFACT_CHARS.sub("", raw)
    text = STRAY_BULLETS.sub("", text)
    text = PAGE_NUMBER_LINE.sub("", text)
    text = MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def _extract_pdf_text(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (page_num, text) pairs in **logical (storage) order** with cleanup.

    PyMuPDF returns RTL text in visual order — we apply `_fix_visual_order_hebrew`
    to restore logical order. Tries PyMuPDF first, falls back to pdfplumber.
    """
    pages: list[tuple[int, str]] = []

    try:
        import fitz  # type: ignore[import-untyped]  # PyMuPDF

        doc = fitz.open(pdf_path)
        for idx in range(len(doc)):
            raw = doc[idx].get_text("text") or ""
            cleaned = _clean_page_text(raw)
            fixed = _fix_visual_order_hebrew(cleaned)
            pages.append((idx + 1, fixed))
        doc.close()
        if any(t.strip() for _, t in pages):
            return pages
    except Exception:
        pass

    try:
        import pdfplumber  # type: ignore[import-untyped]

        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                raw = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                cleaned = _clean_page_text(raw)
                fixed = _fix_visual_order_hebrew(cleaned)
                pages.append((idx, fixed))
    except Exception as exc:
        raise RuntimeError(f"PDF extract failed: {exc}") from exc
    return pages


# Heading detectors used during section splitting
# Numbered headings: "1.", "1.1", "1.1.1", with optional dot
NUMBERED_HEADING = re.compile(r"^\s*\d+(?:\.\d+){0,3}\.?\s+\S")
# Hebrew chapter markers anywhere on the line (not just start) to catch "פרק 3"
HEBREW_CHAPTER_LINE = re.compile(r"^(?:פרק|יחידה|חלק)\s+\S+", re.MULTILINE)
# A short title-looking line: < 90 chars, no period, mostly letters
def _looks_like_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) > 90:
        return False
    if line.endswith(("...", ".", ":", ";")) and not CHAPTER_MARKERS.match(line):
        return False
    # Heading-y if matches markers or has heading-like structure
    if CHAPTER_MARKERS.match(line) or HEBREW_CHAPTER_LINE.match(line):
        return True
    if NUMBERED_HEADING.match(line) and not line[-1].isdigit():
        return True
    return False


def _split_chapters(pages: list[tuple[int, str]]) -> list[dict[str, Any]]:
    """Split PDF pages into chapters using Hebrew/English heading markers.

    Strategy:
    1. Walk lines; promote any line that looks like a heading to a section boundary.
    2. Title the section after that heading.
    3. If no headings detected → chunk every ~5 pages and synthesise a title
       from the first non-trivial sentence of the chunk.
    4. Drop sections shorter than 200 chars (likely covers, TOCs, page-numbers).
    """
    if not pages:
        return []

    chapters: list[dict[str, Any]] = []
    current_title = "מבוא"
    current_lines: list[str] = []
    page_start = pages[0][0]

    def flush(end_page: int) -> None:
        nonlocal current_lines, current_title, page_start
        body = "\n".join(current_lines).strip()
        if body:
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
            if not stripped:
                # Preserve paragraph breaks
                if current_lines and current_lines[-1] != "":
                    current_lines.append("")
                continue
            if _looks_like_heading(stripped):
                # Flush previous section if it has substantive content
                if current_lines and any(line.strip() for line in current_lines):
                    flush(page_num)
                current_title = stripped
                page_start = page_num
            else:
                current_lines.append(stripped)

    flush(pages[-1][0])

    # Drop tiny chapters (likely covers / TOC / glyph noise)
    chapters = [c for c in chapters if len(c["body_md"]) >= 200]

    # Fallback: no real chapters found — chunk by pages with synthesised titles
    if not chapters:
        chunk_size = 5
        for i in range(0, len(pages), chunk_size):
            chunk = pages[i : i + chunk_size]
            body_raw = "\n\n".join(t for _, t in chunk if t.strip())
            if not body_raw.strip():
                continue
            chapters.append(
                {
                    "title": _synthesise_title(body_raw, len(chapters) + 1),
                    "body_md": _text_to_markdown(body_raw),
                    "page_start": chunk[0][0],
                    "page_end": chunk[-1][0],
                }
            )

    return chapters


def _synthesise_title(body: str, idx: int) -> str:
    """Pick the first short, sentence-like line from body; fallback to numbered."""
    for line in body.split("\n"):
        s = line.strip()
        if 8 <= len(s) <= 80 and not s[-1].isdigit():
            return s
    return f"חלק {idx}"


# Mathematical-looking single-character / short-token patterns that should be kept inline
MATH_SHORT_TOKEN = re.compile(r"(?<!\$)\b([a-zA-Z](?:_?\d)?(?:\^?\d)?)\b(?!\$)")


def _detect_math_blocks(text: str) -> str:
    """Promote equations to display math when they look like standalone formulas."""
    # Lines that are mostly math symbols (>= 50% of non-space chars) become $$...$$
    out_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            out_lines.append(line)
            continue
        non_space = [c for c in stripped if not c.isspace()]
        if not non_space:
            out_lines.append(line)
            continue
        math_chars = sum(
            1
            for c in non_space
            if c in "=+-*/^√∫∑∂∞≤≥≠±·x÷±αβγδεζηθικλμνξπρστυφχψω∀∃∈∉⊂⊃⊆⊇U∩"  # noqa: RUF001
            or c.isdigit()
            or (c.isalpha() and c.isascii() and len(non_space) < 25)
        )
        if math_chars / len(non_space) > 0.55 and 3 <= len(stripped) <= 100:
            out_lines.append(f"$${stripped}$$")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def _text_to_markdown(text: str) -> str:
    """Produce readable Markdown with paragraph breaks, bullet lists, and math."""
    if not text.strip():
        return ""

    # Detect and wrap display math first
    text = _detect_math_blocks(text)

    # Existing math markers
    text = MATH_DISPLAY.sub(r"$$\1$$", text)
    text = MATH_INLINE.sub(r"$\1$", text)

    # Convert numbered/bulleted list items into proper Markdown
    text = re.sub(r"(?m)^\s*(\d+)[\)\.]\s+", r"\1. ", text)
    text = re.sub(r"(?m)^\s*[•·◦∙▪]\s+", r"- ", text)

    # Collapse single-line wraps inside a paragraph: a line that doesn't end
    # with punctuation joined to the next non-empty line.
    # This turns the "wall of text from PDF wrap" into proper paragraphs.
    lines = text.split("\n")
    merged: list[str] = []
    for line in lines:
        if (
            merged
            and merged[-1]
            and not merged[-1].endswith((".", ":", "?", "!", "؟", "—", ";"))
            and not merged[-1].startswith(("$$", "- ", "* "))
            and not line.startswith(("$$", "#", "- ", "* "))
            and not re.match(r"^\s*\d+\.", line)
            and line.strip()
        ):
            merged[-1] = merged[-1] + " " + line.strip()
        else:
            merged.append(line)
    text = "\n".join(merged)

    # Promote heading-y lines to Markdown headings
    promoted: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if _looks_like_heading(stripped) and len(stripped) < 80:
            promoted.append(f"### {stripped}")
        else:
            promoted.append(line)
    text = "\n".join(promoted)

    # Paragraph normalisation
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


def _log(msg: str) -> None:
    """Print safely even on Windows terminals with non-UTF8 code pages."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="replace").decode("ascii", errors="replace"))


def _extract_with_timeout(pdf_path: Path, timeout_sec: int = 30) -> list[tuple[int, str]]:
    """Run _extract_pdf_text in a thread with a timeout. Returns [] on timeout."""
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(_extract_pdf_text, pdf_path)
        try:
            return future.result(timeout=timeout_sec)
        except concurrent.futures.TimeoutError:
            return []


async def run_ingest_export(args: argparse.Namespace) -> IngestStats:
    """Offline mode: extract PDFs → JSON + copy Bagrut PDFs. No DB required.

    Writes incrementally so progress is preserved even if interrupted.
    Applies a 30-second timeout per PDF to skip hang-prone scanned files.
    """
    source_root = Path(args.source).resolve()
    if not source_root.is_dir():
        _log(f"[error] source not found: {source_root}")
        return IngestStats(failed=[{"file": str(source_root), "reason": "not a directory"}])

    export_path = Path(args.export_json)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    public_dir = ROOT / "apps" / "web" / "public" / "content" / "bagrut"

    # Load existing export if present (resume from where we left off).
    # IMPORTANT: dedup key is (subject, source_file), NOT just source_file —
    # the same PDF often lives under multiple subject folders (e.g. Physics 1,
    # Physics High School/10th grade, Physics Pre-University) and must be
    # ingested separately into each subject's content_sections.
    if export_path.exists():
        try:
            existing = json.loads(export_path.read_text(encoding="utf-8"))
            sections: list[dict] = existing.get("sections", [])
            bagrut_rows: list[dict] = existing.get("bagrut", [])
            done_keys: set[tuple[str, str]] = {
                (r["subject"], r["source_file"]) for r in sections
            } | {(r["subject"], r["source_file"]) for r in bagrut_rows}
            _log(
                f"[resume] found existing export with {len(sections)} sections, "
                f"{len(bagrut_rows)} bagrut rows, {len(done_keys)} unique (subject,file) keys"
            )
        except Exception:
            sections, bagrut_rows, done_keys = [], [], set()
    else:
        sections, bagrut_rows, done_keys = [], [], set()

    stats = IngestStats()

    def _flush() -> None:
        payload = {"sections": sections, "bagrut": bagrut_rows, "stats": {
            "processed": stats.processed, "sections": stats.sections,
            "bagrut": stats.bagrut, "skipped": stats.skipped,
        }}
        export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for pdf_path in sorted(source_root.rglob("*.pdf")):
        rel = pdf_path.relative_to(source_root)
        source_file = pdf_path.name
        subject = _subject_from_path(source_root, pdf_path)
        grade = _grade_from_path(pdf_path)
        dedup_key = (subject, source_file)

        if dedup_key in done_keys:
            _log(f"[skip-done] {rel}")
            stats.processed += 1
            continue

        if _is_bagrut(pdf_path):
            digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
            dest_name = f"{digest}_{pdf_path.name}"
            public_dir.mkdir(parents=True, exist_ok=True)
            dest = public_dir / dest_name
            if not dest.exists():
                shutil.copy2(pdf_path, dest)
            bagrut_rows.append({
                "subject": subject,
                "exam_type": _exam_type_from_path(pdf_path),
                "year": _extract_year(source_file),
                "source_file": source_file,
                "display_name": _display_name(source_file),
                "file_url": f"/content/bagrut/{dest_name}",
            })
            done_keys.add(dedup_key)
            stats.bagrut += 1
            stats.processed += 1
            _log(f"[bagrut] {rel}")
            _flush()
            continue

        pages = _extract_with_timeout(pdf_path, timeout_sec=30)

        # Fallback for scanned / font-encoded PDFs that yield no text.
        # We can't reliably host the raw PDFs on Vercel (some exceed the
        # 50 MB single-file limit and the total would balloon the bundle),
        # so we emit a single placeholder section so the lesson is at
        # least discoverable in the Learn nav. Full content will arrive
        # once we either OCR these PDFs or move them to object storage.
        has_text = bool(pages) and any(t.strip() for _, t in pages)
        if not has_text:
            display = _display_name(source_file)
            placeholder_md = (
                f"### {display}\n\n"
                f"החומר עבור נושא זה מבוסס על קובץ PDF שעדיין לא ניתן לחילוץ "
                f"טקסט אוטומטי (PDF סרוק / מקודד בפונט מוטמע).\n\n"
                f"החומר יתווסף בקרוב לאחר שלב ה-OCR. בינתיים, ניתן לפנות למורה "
                f"או לבחור שיעור אחר באותו נושא.\n"
            )
            sections.append({
                "subject": subject,
                "grade": grade,
                "source_file": source_file,
                "chunk_index": 0,
                "title": display,
                "body_md": placeholder_md,
                "page_start": None,
                "page_end": None,
            })
            stats.sections += 1
            done_keys.add(dedup_key)
            stats.processed += 1
            _flush()
            _log(f"[placeholder] {rel}: no extractable text — added placeholder")
            continue

        chapters = _split_chapters(pages)
        chunk_count = 0
        for idx, chapter in enumerate(chapters):
            body = chapter["body_md"]
            if not body.strip():
                continue
            sections.append({
                "subject": subject,
                "grade": grade,
                "source_file": source_file,
                "chunk_index": idx,
                "title": chapter["title"],
                "body_md": body,
                "page_start": chapter.get("page_start"),
                "page_end": chapter.get("page_end"),
            })
            stats.sections += 1
            chunk_count += 1

        done_keys.add(dedup_key)
        stats.processed += 1
        _flush()
        _log(f"[ok] {rel} — {chunk_count} chunks")

    _log(f"\n[export] wrote {len(sections)} sections + {len(bagrut_rows)} bagrut rows → {export_path}")
    return stats


async def run_ingest(args: argparse.Namespace) -> IngestStats:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    source_root = Path(args.source).resolve()
    if not source_root.is_dir():
        _log(f"[error] source not found: {source_root}")
        return IngestStats(failed=[{"file": str(source_root), "reason": "not a directory"}])

    db_url = args.db_url or os.environ.get("DATABASE_URL")
    if not db_url:
        _log("[error] --db-url or DATABASE_URL required")
        return IngestStats(failed=[{"file": "", "reason": "no database url"}])

    public_dir = ROOT / "apps" / "web" / "public" / "content" / "bagrut"
    stats = IngestStats()
    pdfs = sorted(source_root.rglob("*.pdf"))

    clean_url, connect_args = _normalize_database_url(db_url)
    engine = create_async_engine(clean_url, connect_args=connect_args, pool_pre_ping=True)
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
                _log(f"[ok] {pdf_path.relative_to(source_root)}")
            except Exception as exc:
                stats.failed.append({"file": str(pdf_path), "reason": str(exc)})
                _log(f"[fail] {pdf_path.name}: {exc}")

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
    # asyncpg + SSL on Windows requires SelectorEventLoop (not the default ProactorEventLoop)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    parser = argparse.ArgumentParser(description="Ingest Learning Database PDFs.")
    parser.add_argument("--source", default="Learning Database/", help="Root folder of PDFs")
    parser.add_argument("--db-url", default="", help="Postgres URL (or DATABASE_URL env)")
    parser.add_argument("--storage-bucket", default="", help="R2/S3 bucket for Bagrut PDFs")
    parser.add_argument("--watch", action="store_true", help="Watch folder for new/changed PDFs")
    parser.add_argument(
        "--export-json",
        default="",
        metavar="PATH",
        help="Offline mode: extract PDFs to JSON (no DB needed). Use seed-content workflow to import.",
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    db_url = args.db_url or os.environ.get("DATABASE_URL", "")

    if args.watch:
        _watch(source, db_url, args.storage_bucket or None)
        return 0

    if args.export_json:
        stats = asyncio.run(run_ingest_export(args))
    else:
        stats = asyncio.run(run_ingest(args))

    _log(
        f"\nSummary: processed={stats.processed} sections={stats.sections} "
        f"bagrut={stats.bagrut} skipped={stats.skipped} failed={len(stats.failed)}"
    )
    return 0 if not stats.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
