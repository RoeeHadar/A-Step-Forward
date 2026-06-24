#!/usr/bin/env python3
"""Idempotent GraphRAG ingestion for Phase-1 curriculum seeds.

Ingests markdown lesson files into pgvector (kg_chunks) and Neo4j (Concept/Lesson
nodes). Re-runnable after seed updates — upserts by chunk id and MERGE in Neo4j.

Usage:
    uv run python scripts/ingest_graphrag.py
    uv run python scripts/ingest_graphrag.py --course foundations-of-math
    uv run python scripts/ingest_graphrag.py --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

DEFAULT_COURSE = "foundations-of-math"
SEEDS_ROOT = ROOT / "infra" / "seeds" / "courses"


def _configure_env() -> None:
    """Enable Postgres chunks + Neo4j when credentials are present."""
    os.environ.setdefault("HF_HUB_DISABLE_SSL", "1")
    os.environ.setdefault("USE_POSTGRES_CHUNKS", "true")
    os.environ.setdefault("USE_NEO4J", "true")
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://astepforward:astepforward@localhost:5432/astepforward",
    )
    # AuraDB Free uses the instance id as username/database (not neo4j/neo4j).
    uri = os.environ.get("NEO4J_URI", "")
    if uri and "databases.neo4j.io" in uri and "NEO4J_USER" not in os.environ:
        instance_id = uri.split("://")[1].split(".")[0]
        os.environ.setdefault("NEO4J_USER", instance_id)
        os.environ.setdefault("NEO4J_DATABASE", instance_id)


def _discover_lessons(course_dir: Path) -> list[Path]:
    return sorted(course_dir.glob("**/*.md"))


async def ingest_course(
    course: str,
    *,
    dry_run: bool = False,
    apply_schema: bool = True,
) -> dict[str, int]:
    from graphrag_service.api import get_graphrag_service
    from graphrag_service.ingest.pipeline import IngestionPipeline
    from graphrag_service.ingest.sources import load_document
    from graphrag_service.ontology import (
        CYPHER_CONSTRAINTS,
        CYPHER_FULLTEXT_INDEXES,
        CYPHER_INDEXES,
    )
    from graphrag_service.settings import GraphRAGSettings
    from graphrag_service.stores.neo4j_store import Neo4jStore

    course_dir = SEEDS_ROOT / course
    if not course_dir.is_dir():
        raise FileNotFoundError(f"Course seed directory not found: {course_dir}")

    lessons = _discover_lessons(course_dir)
    if dry_run:
        print(f"[dry-run] Would ingest {len(lessons)} lesson files from {course_dir}")
        for path in lessons:
            print(f"  - {path.relative_to(ROOT)}")
        return {"lessons": len(lessons), "chunks": 0, "nodes": 0, "edges": 0}

    settings = GraphRAGSettings()
    service = get_graphrag_service()
    neo4j_store: Neo4jStore | None = None
    if settings.use_neo4j:
        neo4j_store = Neo4jStore(settings)
        await neo4j_store.connect()
        if apply_schema:
            statements = [*CYPHER_CONSTRAINTS, *CYPHER_INDEXES, *CYPHER_FULLTEXT_INDEXES]
            applied = await neo4j_store.apply_schema(statements)
            print(f"Applied {applied} Neo4j schema statements")

    pipeline = IngestionPipeline(service, settings=settings, neo4j_store=neo4j_store)

    totals = {"lessons": 0, "chunks": 0, "nodes": 0, "edges": 0, "pending_review": 0}
    for path in lessons:
        doc = load_document(path)
        result = await pipeline.run(doc)
        lesson_nodes, lesson_edges = await pipeline.writer.write_lesson_graph(doc)
        totals["lessons"] += 1
        totals["chunks"] += result.chunks
        totals["nodes"] += result.nodes_written + lesson_nodes
        totals["edges"] += result.edges_written + lesson_edges
        totals["pending_review"] += result.pending_review
        print(
            f"ingested {path.name}: chunks={result.chunks}, "
            f"nodes={result.nodes_written + lesson_nodes}, "
            f"edges={result.edges_written + lesson_edges}"
        )

    if hasattr(service, "close"):
        await service.close()  # type: ignore[attr-defined]
    if neo4j_store is not None:
        await neo4j_store.close()

    print(
        f"\nDone: {totals['lessons']} lessons, {totals['chunks']} chunks, "
        f"{totals['nodes']} nodes, {totals['edges']} edges "
        f"({totals['pending_review']} pending review)"
    )
    return totals


def main() -> int:
    _configure_env()
    parser = argparse.ArgumentParser(description="Ingest curriculum seeds into GraphRAG.")
    parser.add_argument(
        "--course",
        default=DEFAULT_COURSE,
        help=f"Course slug under infra/seeds/courses/ (default: {DEFAULT_COURSE})",
    )
    parser.add_argument("--dry-run", action="store_true", help="List files without ingesting.")
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip Neo4j constraint/index apply (faster re-runs).",
    )
    args = parser.parse_args()
    asyncio.run(
        ingest_course(
            args.course,
            dry_run=args.dry_run,
            apply_schema=not args.skip_schema,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
