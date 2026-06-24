"""Ingestion pipeline tests."""

from __future__ import annotations

import asyncio

from schemas.common import Provenance
from schemas.graph import EdgeKind, KGEdge, KGNode, NodeKind

from graphrag_service.default_service import DefaultGraphRAGService
from graphrag_service.ingest.pipeline import IngestionPipeline, RawDocument


def test_pipeline_ingests_document() -> None:
    async def _run() -> None:
        svc = DefaultGraphRAGService()
        division = KGNode(
            id="concept:division",
            kind=NodeKind.CONCEPT,
            canonical_name="Division",
            summary="Splitting into equal groups.",
        )
        await svc.upsert_node(division)

        pipeline = IngestionPipeline(svc)
        doc = RawDocument(
            id="fractions-intro",
            title="Intro to Fractions",
            text=(
                "# Fractions\n\n"
                "Fractions represent parts of a whole. "
                "Division is required before understanding fractions.\n\n"
                "Equivalent fractions name the same amount."
            ),
            source=Provenance(kind="import", id="fractions-intro"),
        )
        result = await pipeline.run(doc)
        assert result.chunks >= 1
        assert result.nodes_written >= 1
        assert result.document_id == "fractions-intro"

    asyncio.run(_run())


def test_prereq_path_still_works() -> None:
    async def _run() -> None:
        svc = DefaultGraphRAGService()
        fractions = KGNode(id="c:fractions", kind=NodeKind.CONCEPT, canonical_name="Fractions")
        division = KGNode(id="c:division", kind=NodeKind.CONCEPT, canonical_name="Division")
        await svc.upsert_node(fractions)
        await svc.upsert_node(division)
        await svc.upsert_edge(
            KGEdge(id="e1", kind=EdgeKind.PREREQUISITE_OF, src="c:division", dst="c:fractions")
        )
        path = await svc.explain_path("c:division", "c:fractions")
        assert path is not None

    asyncio.run(_run())
