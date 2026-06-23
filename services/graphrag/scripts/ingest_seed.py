"""Run seed corpus ingestion."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

from graphrag_service.api import get_graphrag_service  # noqa: E402
from graphrag_service.ingest.pipeline import IngestionPipeline  # noqa: E402
from graphrag_service.ingest.sources import load_document  # noqa: E402
from graphrag_service.settings import GraphRAGSettings  # noqa: E402


async def ingest_dir(corpus_dir: Path) -> None:
    settings = GraphRAGSettings()
    service = get_graphrag_service()
    neo4j_store = None
    if settings.use_neo4j:
        from graphrag_service.stores.neo4j_store import Neo4jStore

        neo4j_store = Neo4jStore(settings)
        await neo4j_store.connect()

    pipeline = IngestionPipeline(service, settings=settings, neo4j_store=neo4j_store)
    for path in sorted(corpus_dir.glob("*")):
        if path.is_file():
            doc = load_document(path)
            result = await pipeline.run(doc)
            print(f"ingested {path.name}: {result}")

    if hasattr(service, "close"):
        await service.close()  # type: ignore[attr-defined]
    if neo4j_store is not None:
        await neo4j_store.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest GraphRAG seed corpus.")
    parser.add_argument(
        "--corpus",
        default=str(ROOT / "services" / "graphrag" / "fixtures" / "seed_corpus"),
    )
    args = parser.parse_args()
    asyncio.run(ingest_dir(Path(args.corpus)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
