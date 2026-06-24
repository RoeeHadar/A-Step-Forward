"""Public API for the GraphRAG service.

Stable surface for the rest of the project. Sub-agent 05 plugs in the real
Neo4j-backed implementation.
"""

from __future__ import annotations

from typing import Protocol

from schemas.graph import (
    KGEdge,
    KGHybridInput,
    KGNode,
    KGPath,
    KGSearchInput,
    KGSearchResult,
    KGWalkInput,
)

from .settings import GraphRAGSettings


class GraphRAGService(Protocol):
    settings: GraphRAGSettings

    async def search(self, input: KGSearchInput) -> list[KGSearchResult]: ...
    async def walk(self, input: KGWalkInput) -> list[KGPath]: ...
    async def hybrid(self, input: KGHybridInput) -> list[KGSearchResult]: ...
    async def personalized(self, *, learner_id: str, query: str, k: int = 10) -> list[KGSearchResult]: ...
    async def related_concepts(self, concept_id: str) -> list[KGNode]: ...
    async def prereqs(self, concept_id: str) -> list[KGNode]: ...
    async def next_topics(self, *, concept_id: str, learner_id: str) -> list[KGNode]: ...
    async def explain_path(self, src: str, dst: str) -> KGPath | None: ...

    # ingestion
    async def upsert_node(self, node: KGNode) -> KGNode: ...
    async def upsert_edge(self, edge: KGEdge) -> KGEdge: ...


def get_graphrag_service() -> GraphRAGService:
    settings = GraphRAGSettings()
    if settings.use_neo4j or settings.use_postgres_chunks:
        from .neo4j_service import Neo4jGraphRAGService

        return Neo4jGraphRAGService(settings)
    from .default_service import DefaultGraphRAGService

    return DefaultGraphRAGService(settings)
