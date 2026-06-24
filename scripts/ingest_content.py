#!/usr/bin/env python3
"""Ingest OpenStax STEM textbook content into kg_chunks (Neon/pgvector).

Fetches public OpenStax web pages, parses sections into curriculum Lesson objects,
chunks text (≤800 tokens), embeds with sentence-transformers/all-MiniLM-L6-v2 (384-dim),
and idempotently upserts rows into ``kg_chunks``.

Usage:
    uv run python scripts/ingest_content.py --dry-run
    uv run python scripts/ingest_content.py --books precalculus-2e introductory-statistics
    uv run python scripts/ingest_content.py --parse-only --export-lessons out.json

Requires ``DATABASE_URL`` (or ``postgresql+asyncpg://...``) for DB writes.
Apply Alembic migration ``0006_kg_chunks_384`` before first ingest (384-dim embeddings).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import ssl
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

from schemas.curriculum import BloomsLevel, Lesson, Modality, Objective  # noqa: E402

OPENSTAX_BASE = "https://openstax.org"
CMS_API = f"{OPENSTAX_BASE}/apps/cms/api/v2/pages/"
LICENSE = "CC BY 4.0"
MAX_CHUNK_TOKENS = 800
CHUNK_OVERLAP_TOKENS = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

DEFAULT_BOOKS = ("precalculus-2e", "introductory-statistics")

SKIP_PAGE_SLUGS = frozenset(
    {
        "preface",
        "index",
        "answer-key",
        "try-it",
        "review-exercises",
        "chapter-review",
        "practice-test",
        "key-terms",
        "key-equations",
        "key-concepts",
    }
)

SECTION_SLUG_RE = re.compile(r"^(\d+)-(\d+)-([a-z][a-z0-9-]*)$")
EMBEDDED_SECTION_RE = re.compile(r"\b(\d+-\d+-[a-z][a-z0-9-]*)\b")

BOOK_CONFIG: dict[str, dict[str, str]] = {
    "precalculus-2e": {
        "title": "Precalculus 2e",
        "subject": "precalculus",
        "level": "intermediate",
    },
    "introductory-statistics": {
        "title": "Introductory Statistics",
        "subject": "statistics",
        "level": "intermediate",
    },
}


@dataclass
class ParsedPage:
    slug: str
    title: str
    body_md: str
    source_url: str
    objectives: list[str] = field(default_factory=list)


@dataclass
class TextChunk:
    chunk_idx: int
    text: str
    heading: str | None
    token_count: int


class _MainContentParser(HTMLParser):
    """Extract readable text from OpenStax REX HTML."""

    _SKIP_TAGS = frozenset({"script", "style", "nav", "footer", "header", "noscript"})

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._blocks: list[str] = []
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "p", "li", "td", "th", "blockquote"}:
            self._flush()
            if tag.startswith("h"):
                level = int(tag[1])
                self._buffer.append("#" * level + " ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "p", "li", "td", "th", "blockquote", "div", "section"}:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self._buffer.append(unescape(text))

    def _flush(self) -> None:
        if not self._buffer:
            return
        line = " ".join(self._buffer).strip()
        self._buffer.clear()
        if line:
            self._blocks.append(line)

    def text(self) -> str:
        self._flush()
        return "\n\n".join(self._blocks)


def _configure_ssl() -> bool:
    """Return httpx verify flag; allow insecure fetches on dev Windows hosts."""
    if os.environ.get("OPENSTAX_INSECURE_SSL", "").lower() in {"1", "true", "yes"}:
        os.environ.setdefault("HF_HUB_DISABLE_SSL", "1")
        try:
            ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore[method-assign]
        except Exception:
            pass
        return False
    return True


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "item"


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _page_url(book_slug: str, page_slug: str) -> str:
    return f"{OPENSTAX_BASE}/books/{book_slug}/pages/{page_slug}"


def _is_section_slug(slug: str) -> bool:
    match = SECTION_SLUG_RE.match(slug)
    if not match:
        return False
    chapter = int(match.group(1))
    section = int(match.group(2))
    tail = match.group(3)
    if chapter < 1 or chapter > 20 or section < 1 or section > 40:
        return False
    if re.search(r"[0-9]{4,}", tail):
        return False
    return slug not in SKIP_PAGE_SLUGS


def _extract_section_slugs_from_html(html: str) -> list[str]:
    candidates = {slug.lower() for slug in EMBEDDED_SECTION_RE.findall(html)}
    valid = [slug for slug in sorted(candidates) if _is_section_slug(slug)]
    return valid


def _extract_objectives(body: str) -> list[str]:
    objectives: list[str] = []
    section_match = re.search(
        r"in this section, you will:\s*(.+?)(?:\n\n|\Z)",
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        return objectives
    block = section_match.group(1)
    for line in block.splitlines():
        cleaned = re.sub(r"^[-*•]\s*", "", line.strip())
        if cleaned and len(cleaned) > 8:
            objectives.append(cleaned)
    return objectives[:6]


def _html_to_text(html: str) -> str:
    parser = _MainContentParser()
    parser.feed(html)
    return parser.text()


def _extract_title(html: str, fallback: str) -> str:
    match = re.search(r"<title>([^<]+)</title>", html, flags=re.IGNORECASE)
    if not match:
        return fallback
    title = unescape(match.group(1)).strip()
    title = re.sub(r"\s*[-|]\s*OpenStax\s*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^Precalculus 2e\s+", "", title)
    title = re.sub(r"^Introductory Statistics\s+", "", title)
    return title.strip() or fallback


def _chunk_text(text: str, *, max_tokens: int = MAX_CHUNK_TOKENS) -> list[TextChunk]:
    """Split text into ≤max_tokens segments with light overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paragraphs:
        return []

    chunks: list[TextChunk] = []
    current: list[str] = []
    current_tokens = 0
    chunk_idx = 0
    heading: str | None = None

    def flush() -> None:
        nonlocal chunk_idx, current, current_tokens
        if not current:
            return
        body = "\n\n".join(current)
        chunks.append(
            TextChunk(
                chunk_idx=chunk_idx,
                text=body,
                heading=heading,
                token_count=_estimate_tokens(body),
            )
        )
        chunk_idx += 1
        if CHUNK_OVERLAP_TOKENS > 0 and current:
            overlap = current[-1]
            current = [overlap]
            current_tokens = _estimate_tokens(overlap)
        else:
            current = []
            current_tokens = 0

    for para in paragraphs:
        if para.startswith("#"):
            heading = para.lstrip("#").strip()
        para_tokens = _estimate_tokens(para)
        if para_tokens > max_tokens:
            flush()
            words = para.split()
            window: list[str] = []
            window_tokens = 0
            for word in words:
                word_tokens = _estimate_tokens(word + " ")
                if window_tokens + word_tokens > max_tokens and window:
                    body = " ".join(window)
                    chunks.append(
                        TextChunk(
                            chunk_idx=chunk_idx,
                            text=body,
                            heading=heading,
                            token_count=_estimate_tokens(body),
                        )
                    )
                    chunk_idx += 1
                    window = window[-max(1, CHUNK_OVERLAP_TOKENS // 4) :]
                    window_tokens = _estimate_tokens(" ".join(window))
                window.append(word)
                window_tokens += word_tokens
            if window:
                current = [" ".join(window)]
                current_tokens = _estimate_tokens(current[0])
            continue

        if current_tokens + para_tokens > max_tokens and current:
            flush()
        current.append(para)
        current_tokens += para_tokens

    flush()
    return chunks


def _make_chunk_id(source_url: str, chunk_idx: int) -> str:
    digest = hashlib.sha256(f"{source_url}\0{chunk_idx}".encode()).hexdigest()
    return f"osx-{digest[:24]}"


def _concept_id(book_slug: str, page_slug: str) -> str:
    return f"concept-{_slugify(book_slug)}-{_slugify(page_slug)}"


def _lesson_id(book_slug: str, page_slug: str) -> str:
    return f"lesson-{_slugify(book_slug)}-{_slugify(page_slug)}"


def _objectives_from_statements(
    statements: list[str],
    *,
    concept_id: str,
    page_slug: str,
) -> list[Objective]:
    if len(statements) < 2:
        statements = [
            f"Explain the main ideas in {page_slug.replace('-', ' ')}.",
            f"Apply concepts from {page_slug.replace('-', ' ')} to practice problems.",
        ]
    objectives: list[Objective] = []
    blooms_cycle = [BloomsLevel.UNDERSTAND, BloomsLevel.APPLY, BloomsLevel.ANALYZE, BloomsLevel.REMEMBER]
    for idx, statement in enumerate(statements[:4]):
        objectives.append(
            Objective(
                id=f"obj-{_slugify(page_slug)}-{idx + 1}",
                statement=statement.rstrip("."),
                blooms_level=blooms_cycle[idx % len(blooms_cycle)],
                concepts=[concept_id],
            )
        )
    return objectives if len(objectives) >= 2 else [
        *objectives,
        Objective(
            id=f"obj-{_slugify(page_slug)}-fallback",
            statement=f"Apply ideas from {page_slug.replace('-', ' ')}.",
            blooms_level=BloomsLevel.APPLY,
            concepts=[concept_id],
        ),
    ]


def page_to_lesson(page: ParsedPage, book_slug: str, book_cfg: dict[str, str]) -> Lesson:
    concept_id = _concept_id(book_slug, page.slug)
    objectives = _objectives_from_statements(
        page.objectives,
        concept_id=concept_id,
        page_slug=page.slug,
    )
    est_minutes = min(180, max(10, 8 + _estimate_tokens(page.body_md) // 120))
    return Lesson(
        id=_lesson_id(book_slug, page.slug),
        title=page.title,
        body_md=page.body_md,
        modality=Modality.READING,
        objectives=objectives,
        concepts=[concept_id],
        resources=[],
        est_minutes=est_minutes,
    )


async def fetch_text(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url, follow_redirects=True)
    response.raise_for_status()
    return response.text


async def resolve_book(client: httpx.AsyncClient, book_slug: str) -> dict[str, Any]:
    response = await client.get(CMS_API, params={"slug": book_slug, "fields": "title"})
    response.raise_for_status()
    payload = response.json()
    items = payload.get("items") or []
    if not items:
        msg = f"OpenStax book not found: {book_slug}"
        raise ValueError(msg)
    return items[0]


def _book_index_url(book_slug: str) -> str:
    """First chapter page used by REX to embed the full book TOC."""
    if book_slug == "precalculus-2e":
        return _page_url(book_slug, "1-introduction-to-functions")
    return _page_url(book_slug, "1-introduction")


async def discover_book_pages(client: httpx.AsyncClient, book_slug: str) -> list[str]:
    """Discover section slugs embedded in OpenStax REX book HTML."""
    index_url = _book_index_url(book_slug)
    html = await fetch_text(client, index_url)
    slugs = _extract_section_slugs_from_html(html)
    if not slugs:
        # Fallback: try alternate index pages.
        for seed in ("preface", "1-introduction", "1-introduction-to-functions"):
            try:
                page_html = await fetch_text(client, _page_url(book_slug, seed))
            except httpx.HTTPError:
                continue
            slugs = _extract_section_slugs_from_html(page_html)
            if slugs:
                break
    return slugs


def parse_page_html(*, book_slug: str, page_slug: str, html: str) -> ParsedPage | None:
    title = _extract_title(html, fallback=page_slug.replace("-", " ").title())
    body = _html_to_text(html)
    if len(body) < 200:
        return None
    objectives = _extract_objectives(body)
    source_url = _page_url(book_slug, page_slug)
    body_md = f"# {title}\n\n{body}\n\n---\n\n*Source: [{source_url}]({source_url}) · License: {LICENSE}*"
    return ParsedPage(
        slug=page_slug,
        title=title,
        body_md=body_md,
        source_url=source_url,
        objectives=objectives,
    )


async def embed_texts(texts: list[str]) -> list[list[float]]:
    from graphrag_service.ingest.embedder import Embedder
    from graphrag_service.settings import GraphRAGSettings

    settings = GraphRAGSettings(
        embedding_model=EMBEDDING_MODEL,
        embedding_dim=EMBEDDING_DIM,
    )
    embedder = Embedder(settings)
    return await embedder.embed_texts(texts)


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


async def upsert_chunks(
    *,
    database_url: str,
    rows: list[dict[str, Any]],
) -> int:
    if not rows:
        return 0

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(_normalize_database_url(database_url), pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    written = 0
    async with sessionmaker() as session:
        for row in rows:
            await session.execute(
                text(
                    """
                    INSERT INTO kg_chunks
                        (id, document_id, ordinal, text, heading, token_count, embedding, provenance, created_at)
                    VALUES
                        (:id, :document_id, :ordinal, :text, :heading, :token_count,
                         CAST(:embedding AS vector), CAST(:provenance AS jsonb), :created_at)
                    ON CONFLICT (id) DO UPDATE SET
                        document_id = EXCLUDED.document_id,
                        ordinal = EXCLUDED.ordinal,
                        text = EXCLUDED.text,
                        heading = EXCLUDED.heading,
                        token_count = EXCLUDED.token_count,
                        embedding = EXCLUDED.embedding,
                        provenance = EXCLUDED.provenance
                    """
                ),
                row,
            )
            written += 1
        await session.commit()
    await engine.dispose()
    return written


async def ingest_book(
    client: httpx.AsyncClient,
    book_slug: str,
    *,
    dry_run: bool = False,
    parse_only: bool = False,
    database_url: str | None,
    max_pages: int | None,
) -> dict[str, Any]:
    book_cfg = BOOK_CONFIG.get(book_slug, {"title": book_slug, "subject": book_slug, "level": "intermediate"})
    meta = await resolve_book(client, book_slug)
    print(f"[openstax] {book_slug}: {meta.get('title', book_cfg.get('title', book_slug))}")

    page_slugs = await discover_book_pages(client, book_slug)
    if max_pages is not None:
        page_slugs = page_slugs[:max_pages]
    print(f"[openstax] discovered {len(page_slugs)} content pages")

    if dry_run:
        return {
            "book_slug": book_slug,
            "pages": len(page_slugs),
            "lessons": 0,
            "chunks": 0,
            "chunks_written": 0,
            "lesson_objects": [],
        }

    lessons: list[Lesson] = []
    chunk_rows: list[dict[str, Any]] = []
    total_chunks = 0

    for page_slug in page_slugs:
        html = await fetch_text(client, _page_url(book_slug, page_slug))
        parsed = parse_page_html(book_slug=book_slug, page_slug=page_slug, html=html)
        if parsed is None:
            continue
        lesson = page_to_lesson(parsed, book_slug, book_cfg)
        lessons.append(lesson)

        chunks = _chunk_text(parsed.body_md)
        total_chunks += len(chunks)
        if dry_run or parse_only or not database_url:
            continue

        embeddings = await embed_texts([c.text for c in chunks])
        now = datetime.now(UTC)
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            provenance = {
                "kind": "import",
                "source_url": parsed.source_url,
                "license": LICENSE,
                "subject": book_cfg["subject"],
                "chunk_idx": chunk.chunk_idx,
                "book_slug": book_slug,
                "page_slug": page_slug,
                "model": EMBEDDING_MODEL,
            }
            chunk_rows.append(
                {
                    "id": _make_chunk_id(parsed.source_url, chunk.chunk_idx),
                    "document_id": parsed.source_url,
                    "ordinal": chunk.chunk_idx,
                    "text": chunk.text,
                    "heading": chunk.heading or parsed.title,
                    "token_count": chunk.token_count,
                    "embedding": str(embedding),
                    "provenance": json.dumps(provenance),
                    "created_at": now,
                }
            )

    written = 0
    if chunk_rows and database_url and not dry_run and not parse_only:
        written = await upsert_chunks(database_url=database_url, rows=chunk_rows)

    return {
        "book_slug": book_slug,
        "pages": len(page_slugs),
        "lessons": len(lessons),
        "chunks": total_chunks,
        "chunks_written": written,
        "lesson_objects": lessons,
    }


def _lessons_to_seed_payload(lessons: list[Lesson], book_slug: str, book_cfg: dict[str, str]) -> list[dict]:
    unit_id = f"openstax-{book_cfg['subject']}"
    unit_title = book_cfg["title"]
    course_id = f"openstax-{book_cfg['subject']}"
    out: list[dict] = []
    for lesson in lessons:
        payload = lesson.model_dump(mode="json")
        payload["course_id"] = course_id
        payload["course_title"] = book_cfg["title"]
        payload["unit_id"] = unit_id
        payload["unit_title"] = unit_title
        out.append(payload)
    return out


async def run_ingest(args: argparse.Namespace) -> dict[str, Any]:
    verify = _configure_ssl()
    timeout = httpx.Timeout(60.0, connect=30.0)
    limits = httpx.Limits(max_connections=8, max_keepalive_connections=4)

    database_url = os.environ.get("DATABASE_URL")
    if not args.dry_run and not args.parse_only and not database_url:
        print("[warn] DATABASE_URL not set — parsing only (no DB writes).")

    totals = {"books": 0, "lessons": 0, "chunks": 0, "chunks_written": 0}
    all_lessons: list[dict] = []

    async with httpx.AsyncClient(verify=verify, timeout=timeout, limits=limits) as client:
        for book_slug in args.books:
            result = await ingest_book(
                client,
                book_slug,
                dry_run=args.dry_run,
                parse_only=args.parse_only or not database_url,
                database_url=database_url,
                max_pages=args.max_pages,
            )
            totals["books"] += 1
            totals["lessons"] += result["lessons"]
            totals["chunks"] += result["chunks"]
            totals["chunks_written"] += result["chunks_written"]
            book_cfg = BOOK_CONFIG.get(book_slug, {"title": book_slug, "subject": book_slug})
            all_lessons.extend(
                _lessons_to_seed_payload(result["lesson_objects"], book_slug, book_cfg)
            )
            print(
                f"[done] {book_slug}: lessons={result['lessons']} chunks={result['chunks']} "
                f"written={result['chunks_written']}"
            )

    if args.export_lessons:
        export_path = Path(args.export_lessons)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(all_lessons, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[export] wrote {len(all_lessons)} lessons to {export_path}")

    return totals


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest OpenStax STEM content into kg_chunks.")
    parser.add_argument(
        "--books",
        nargs="+",
        default=list(DEFAULT_BOOKS),
        help=f"OpenStax book slugs (default: {' '.join(DEFAULT_BOOKS)})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Discover pages without fetch/embed/DB.")
    parser.add_argument(
        "--parse-only",
        action="store_true",
        help="Fetch and parse; skip embeddings and DB writes.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit pages per book (useful for dev smoke runs).",
    )
    parser.add_argument(
        "--export-lessons",
        metavar="PATH",
        default="",
        help="Write parsed Lesson objects as JSON array.",
    )
    args = parser.parse_args()
    totals = asyncio.run(run_ingest(args))
    print(
        f"\nSummary: books={totals['books']} lessons={totals['lessons']} "
        f"chunks={totals['chunks']} db_rows={totals['chunks_written']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
