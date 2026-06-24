"""Neo4j-backed GraphRAG service."""

from __future__ import annotations

from schemas.graph import (
    KGChunk,
    KGEdge,
    KGHybridInput,
    KGNode,
    KGPath,
    KGSearchInput,
    KGSearchResult,
    KGWalkInput,
)

from .ingest.embedder import Embedder
from .retrieval import queries
from .settings import GraphRAGSettings
from .stores.chunk_repository import ChunkRepository
from .stores.neo4j_store import Neo4jStore


class Neo4jGraphRAGService:
    def __init__(self, settings: GraphRAGSettings | None = None) -> None:
        self.settings = settings or GraphRAGSettings()
        self._neo4j = Neo4jStore(self.settings)
        self._chunks = ChunkRepository(self.settings)
        self._embedder = Embedder(self.settings)
        self._connected = False
        self._local_nodes: dict[str, KGNode] = {}
        self._local_edges: dict[str, KGEdge] = {}

    async def _ensure_connected(self) -> None:
        if self._connected:
            return
        if self.settings.use_neo4j:
            await self._neo4j.connect()
        await self._chunks.connect()
        self._connected = True

    async def close(self) -> None:
        if self.settings.use_neo4j:
            await self._neo4j.close()
        await self._chunks.close()
        self._connected = False

    async def upsert_node(self, node: KGNode) -> KGNode:
        await self._ensure_connected()
        if self.settings.use_neo4j:
            return await self._neo4j.upsert_node(node)
        self._local_nodes[node.id] = node
        return node

    async def upsert_edge(self, edge: KGEdge) -> KGEdge:
        await self._ensure_connected()
        if self.settings.use_neo4j:
            return await self._neo4j.upsert_edge(edge)
        self._local_edges[edge.id] = edge
        return edge

    async def upsert_chunk(self, chunk: KGChunk) -> KGChunk:
        await self._ensure_connected()
        return await self._chunks.upsert(chunk)

    async def search(self, input: KGSearchInput) -> list[KGSearchResult]:
        await self._ensure_connected()
        return await queries.local_search(self._neo4j, self._chunks, self._embedder, input)

    async def walk(self, input: KGWalkInput) -> list[KGPath]:
        await self._ensure_connected()
        return await queries.graph_walk(self._neo4j, input)

    async def hybrid(self, input: KGHybridInput) -> list[KGSearchResult]:
        await self._ensure_connected()
        return await queries.hybrid_search(self._neo4j, self._chunks, self._embedder, input)

    async def personalized(self, *, learner_id: str, query: str, k: int = 10) -> list[KGSearchResult]:
        await self._ensure_connected()
        return await queries.personalized_search(
            self._neo4j,
            self._chunks,
            self._embedder,
            learner_id=learner_id,
            query=query,
            k=k,
        )

    async def related_concepts(self, concept_id: str) -> list[KGNode]:
        await self._ensure_connected()
        return await self._neo4j.related_concepts(concept_id)

    async def prereqs(self, concept_id: str) -> list[KGNode]:
        await self._ensure_connected()
        return await self._neo4j.prereqs(concept_id)

    async def next_topics(self, *, concept_id: str, learner_id: str) -> list[KGNode]:
        await self._ensure_connected()
        return await self._neo4j.next_topics(concept_id=concept_id, learner_id=learner_id)

    async def explain_path(self, src: str, dst: str) -> KGPath | None:
        await self._ensure_connected()
        return await self._neo4j.shortest_path(src, dst)
