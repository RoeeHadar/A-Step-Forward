"""Apply Neo4j KG ontology constraints and indexes.

Usage:
    uv run python services/graphrag/scripts/apply_schema.py
    uv run python services/graphrag/scripts/apply_schema.py --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

from graphrag_service.ontology import (  # noqa: E402
    CYPHER_CONSTRAINTS,
    CYPHER_FULLTEXT_INDEXES,
    CYPHER_INDEXES,
)
from graphrag_service.settings import GraphRAGSettings  # noqa: E402
from graphrag_service.stores.neo4j_store import Neo4jStore  # noqa: E402


async def apply_schema(*, dry_run: bool = False) -> None:
    settings = GraphRAGSettings()
    statements = [*CYPHER_CONSTRAINTS, *CYPHER_INDEXES, *CYPHER_FULLTEXT_INDEXES]
    if dry_run:
        for stmt in statements:
            print(stmt)
        print(f"\n{len(statements)} statements (dry run)")
        return

    store = Neo4jStore(settings)
    await store.connect()
    try:
        applied = await store.apply_schema(statements)
        print(f"Applied {applied} schema statements to {settings.neo4j_uri}")
    finally:
        await store.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Neo4j KG ontology schema.")
    parser.add_argument("--dry-run", action="store_true", help="Print Cypher without executing.")
    args = parser.parse_args()
    asyncio.run(apply_schema(dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
