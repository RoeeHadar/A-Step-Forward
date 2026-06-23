"""GraphRAG MCP tool handlers."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from schemas.graph import (
    KGConceptInput,
    KGExplainPathInput,
    KGHybridInput,
    KGNextTopicsInput,
    KGNode,
    KGPath,
    KGPersonalizedInput,
    KGSearchInput,
    KGSearchResult,
    KGWalkInput,
)

from graphrag_mcp.errors import invoke
from graphrag_service.api import GraphRAGService, get_graphrag_service


def register_graphrag_tools(mcp: FastMCP, *, svc: GraphRAGService | None = None) -> GraphRAGService:
    """Register all kg.* tools on the given FastMCP instance."""
    service = svc or get_graphrag_service()

    @mcp.tool(name="kg.search", description="Search the knowledge graph by natural-language query.")
    async def kg_search(inp: KGSearchInput) -> list[KGSearchResult]:
        return await invoke(service.search(inp))

    @mcp.tool(name="kg.walk", description="Walk the graph from seed nodes with optional edge-type filter.")
    async def kg_walk(inp: KGWalkInput) -> list[KGPath]:
        return await invoke(service.walk(inp))

    @mcp.tool(name="kg.hybrid", description="Hybrid retrieval: vector seed, graph walk, and rerank.")
    async def kg_hybrid(inp: KGHybridInput) -> list[KGSearchResult]:
        return await invoke(service.hybrid(inp))

    @mcp.tool(name="kg.personalized", description="Hybrid search biased toward a learner's subgraph.")
    async def kg_personalized(inp: KGPersonalizedInput) -> list[KGSearchResult]:
        return await invoke(service.personalized(learner_id=inp.learner_id, query=inp.query, k=inp.k))

    @mcp.tool(name="kg.related_concepts", description="List concepts directly related to a given concept.")
    async def kg_related_concepts(inp: KGConceptInput) -> list[KGNode]:
        return await invoke(service.related_concepts(inp.concept_id))

    @mcp.tool(name="kg.prereqs", description="List prerequisite concepts for a given concept.")
    async def kg_prereqs(inp: KGConceptInput) -> list[KGNode]:
        return await invoke(service.prereqs(inp.concept_id))

    @mcp.tool(name="kg.next_topics", description="Suggest next topics for a learner from a concept.")
    async def kg_next_topics(inp: KGNextTopicsInput) -> list[KGNode]:
        return await invoke(service.next_topics(concept_id=inp.concept_id, learner_id=inp.learner_id))

    @mcp.tool(name="kg.explain_path", description="Return the shortest justified path between two graph nodes.")
    async def kg_explain_path(inp: KGExplainPathInput) -> KGPath | None:
        return await invoke(service.explain_path(inp.src, inp.dst))

    return service
