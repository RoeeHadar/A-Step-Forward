"""Ingestion pipeline — chunk → embed → extract → resolve → write → verify."""

from __future__ import annotations

from schemas.graph import KGChunk, KGNode

from ..api import GraphRAGService
from ..settings import GraphRAGSettings
from ..stores.neo4j_store import Neo4jStore
from .chunker import SemanticChunker
from .embedder import Embedder
from .extractor import Extractor
from .resolver import EntityResolver
from .types import IngestionResult, RawDocument
from .verifier import Verifier
from .writer import GraphWriter


class IngestionPipeline:
    """Wires ingestion stages end-to-end."""

    def __init__(
        self,
        service: GraphRAGService,
        *,
        settings: GraphRAGSettings | None = None,
        neo4j_store: Neo4jStore | None = None,
    ) -> None:
        self.service = service
        self.settings = settings or GraphRAGSettings()
        self.chunker = SemanticChunker(self.settings)
        self.embedder = Embedder(self.settings)
        self.extractor = Extractor(self.settings)
        self.resolver = EntityResolver(self.settings, store=neo4j_store)
        self.writer = GraphWriter(service, store=neo4j_store)
        self.verifier = Verifier(sample_rate=self.settings.verification_sample_rate)
        self._seed_resolver_index()

    def _seed_resolver_index(self) -> None:
        nodes: dict[str, KGNode] = {}
        raw_nodes = getattr(self.service, "_nodes", None)
        if isinstance(raw_nodes, dict):
            nodes = raw_nodes
        self.resolver.seed_memory(nodes)

    async def chunk(self, doc: RawDocument) -> list[KGChunk]:
        parts = self.chunker.split(doc.text)
        chunks: list[KGChunk] = []
        for part in parts:
            text = part.text
            if part.heading:
                text = f"## {part.heading}\n\n{text}"
            chunks.append(
                KGChunk(
                    id=f"{doc.id}:chunk:{part.ordinal}",
                    document_id=doc.id,
                    ordinal=part.ordinal,
                    text=text,
                    heading=part.heading,
                    token_count=part.token_count,
                    provenance=doc.source,
                )
            )
        return chunks

    async def embed(self, chunks: list[KGChunk]) -> list[KGChunk]:
        vectors = await self.embedder.embed_texts([c.text for c in chunks])
        enriched: list[KGChunk] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            enriched.append(chunk.model_copy(update={"embedding": vector}))
        return enriched

    async def extract(self, chunks: list[KGChunk], doc: RawDocument):
        from schemas.graph import Extraction

        if not chunks:
            return Extraction(entities=[], relations=[], claims=[], confidence=0.0, notes="low_confidence")
        return await self.extractor.extract([c.text for c in chunks])

    async def resolve_and_write(
        self,
        extraction,
        doc: RawDocument,
        *,
        chunks: list[KGChunk],
    ) -> IngestionResult:
        await self.writer.write_document_resource(doc)
        chunk_ids = [c.id for c in chunks]
        for chunk in chunks:
            if hasattr(self.service, "upsert_chunk"):
                await self.service.upsert_chunk(chunk)  # type: ignore[attr-defined]

        resolved = await self.resolver.resolve(extraction.entities)
        nodes_written, edges_written, pending_review = await self.writer.write_extraction(
            extraction,
            resolved,
            doc=doc,
            chunk_ids=chunk_ids,
        )
        await self.verifier.verify(extraction)
        return IngestionResult(
            document_id=doc.id,
            chunks=len(chunks),
            nodes_written=nodes_written + 1,
            edges_written=edges_written,
            pending_review=pending_review,
        )

    async def run(self, doc: RawDocument) -> IngestionResult:
        chunks = await self.chunk(doc)
        chunks = await self.embed(chunks)
        extraction = await self.extract(chunks, doc)
        return await self.resolve_and_write(extraction, doc, chunks=chunks)
