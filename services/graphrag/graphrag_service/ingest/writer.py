"""Write resolved entities/relations to Neo4j with provenance."""

from __future__ import annotations

import uuid

from schemas.common import Provenance
from schemas.graph import EdgeKind, Extraction, KGChunk, KGEdge, KGNode, NodeKind

from ..api import GraphRAGService
from ..stores.neo4j_store import Neo4jStore
from .resolver import ResolvedEntity
from .types import RawDocument


class GraphWriter:
    def __init__(self, service: GraphRAGService, store: Neo4jStore | None = None) -> None:
        self.service = service
        self.store = store

    async def write_document_resource(self, doc: RawDocument) -> KGNode:
        node = KGNode(
            id=f"resource:{doc.id}",
            kind=NodeKind.RESOURCE,
            canonical_name=doc.title,
            summary=doc.text[:500],
            provenance=doc.source,
            pending_review=False,
        )
        await self.service.upsert_node(node)
        return node

    async def write_chunks(self, chunks: list[KGChunk]) -> int:
        count = 0
        for chunk in chunks:
            if hasattr(self.service, "upsert_chunk"):
                await self.service.upsert_chunk(chunk)  # type: ignore[attr-defined]
            count += 1
        return count

    async def write_extraction(
        self,
        extraction: Extraction,
        resolved: list[ResolvedEntity],
        *,
        doc: RawDocument,
        chunk_ids: list[str],
    ) -> tuple[int, int, int]:
        name_to_node = {r.entity.name: r.node for r in resolved}
        nodes_written = 0
        edges_written = 0
        pending_review = 0

        for item in resolved:
            node = item.node
            if not item.linked:
                node.provenance = doc.source
                await self.service.upsert_node(node)
                nodes_written += 1
                if node.pending_review:
                    pending_review += 1

        for relation in extraction.relations:
            src = name_to_node.get(relation.src_name)
            dst = name_to_node.get(relation.dst_name)
            if src is None or dst is None:
                continue
            edge = KGEdge(
                id=f"edge:{uuid.uuid4().hex[:12]}",
                kind=relation.kind,
                src=src.id,
                dst=dst.id,
                weight=relation.weight,
                provenance=doc.source,
                properties={"confidence": relation.confidence},
            )
            await self.service.upsert_edge(edge)
            edges_written += 1

        # Provenance edges from entities to source chunks.
        for chunk_id in chunk_ids[:1]:
            chunk_node = KGNode(
                id=chunk_id,
                kind=NodeKind.RESOURCE,
                canonical_name=f"Chunk {chunk_id}",
                summary=None,
                provenance=doc.source,
            )
            await self.service.upsert_node(chunk_node)
            for item in resolved:
                edge = KGEdge(
                    id=f"prov:{uuid.uuid4().hex[:12]}",
                    kind=EdgeKind.DERIVED_FROM,
                    src=item.node.id,
                    dst=chunk_id,
                    provenance=Provenance(kind="import", id=doc.id),
                    properties={"chunk_id": chunk_id},
                )
                await self.service.upsert_edge(edge)
                edges_written += 1

        return nodes_written, edges_written, pending_review
