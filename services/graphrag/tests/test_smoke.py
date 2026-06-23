"""Phase-0 smoke test for GraphRAG."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

from schemas.common import Provenance
from schemas.graph import EdgeKind, KGEdge, KGNode, NodeKind

from graphrag_service.default_service import DefaultGraphRAGService
from graphrag_service.ingest.pipeline import IngestionPipeline, RawDocument


async def main() -> None:
    svc = DefaultGraphRAGService()

    fractions = KGNode(id="c:fractions", kind=NodeKind.CONCEPT, canonical_name="Fractions", summary="Parts of a whole.")
    division = KGNode(id="c:division", kind=NodeKind.CONCEPT, canonical_name="Division", summary="Splitting into equal parts.")
    await svc.upsert_node(fractions)
    await svc.upsert_node(division)
    await svc.upsert_edge(KGEdge(id="e:div_pre_frac", kind=EdgeKind.PREREQUISITE_OF, src="c:division", dst="c:fractions"))

    prereqs = await svc.prereqs("c:fractions")
    assert prereqs and prereqs[0].canonical_name == "Division"
    print("prereqs ok:", [n.canonical_name for n in prereqs])

    path = await svc.explain_path("c:division", "c:fractions")
    assert path is not None and len(path.nodes) == 2
    print("explain_path ok:", [n.canonical_name for n in path.nodes])

    pipeline = IngestionPipeline(svc)
    result = await pipeline.run(
        RawDocument(
            id="doc1",
            title="Intro to Fractions",
            text="Fractions represent parts of a whole. " * 50,
            source=Provenance(kind="import", id="doc1"),
        )
    )
    print("ingest ok:", result)


if __name__ == "__main__":
    asyncio.run(main())
