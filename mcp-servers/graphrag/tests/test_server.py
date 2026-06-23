"""Unit tests for the GraphRAG MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
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
    NodeKind,
)

from graphrag_mcp.server import create_server


def _sample_node() -> KGNode:
    return KGNode(id="concept-1", kind=NodeKind.CONCEPT, canonical_name="Fractions")


@pytest.fixture
def mock_svc() -> MagicMock:
    node = _sample_node()
    svc = MagicMock()
    svc.search = AsyncMock(return_value=[KGSearchResult(node=node, score=0.8)])
    svc.walk = AsyncMock(return_value=[KGPath(nodes=[node], edges=[])])
    svc.hybrid = AsyncMock(return_value=[KGSearchResult(node=node, score=0.75)])
    svc.personalized = AsyncMock(return_value=[KGSearchResult(node=node, score=0.7)])
    svc.related_concepts = AsyncMock(return_value=[node])
    svc.prereqs = AsyncMock(return_value=[node])
    svc.next_topics = AsyncMock(return_value=[node])
    svc.explain_path = AsyncMock(return_value=KGPath(nodes=[node], edges=[]))
    return svc


@pytest.fixture
def mcp_server(mock_svc: MagicMock):
    return create_server(svc=mock_svc)


@pytest.mark.asyncio
async def test_list_tools_registers_all_kg_tools(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    names = {tool.name for tool in tools}
    expected = {
        "kg.search",
        "kg.walk",
        "kg.hybrid",
        "kg.personalized",
        "kg.related_concepts",
        "kg.prereqs",
        "kg.next_topics",
        "kg.explain_path",
    }
    assert expected <= names


@pytest.mark.asyncio
async def test_kg_search_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGSearchInput(query="fractions")
    await mcp_server.call_tool("kg.search", {"inp": inp.model_dump(mode="json")})
    mock_svc.search.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_walk_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGWalkInput(seed_node_ids=["concept-1"])
    await mcp_server.call_tool("kg.walk", {"inp": inp.model_dump(mode="json")})
    mock_svc.walk.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_hybrid_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGHybridInput(query="fractions")
    await mcp_server.call_tool("kg.hybrid", {"inp": inp.model_dump(mode="json")})
    mock_svc.hybrid.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_personalized_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGPersonalizedInput(learner_id="learner-1", query="fractions")
    await mcp_server.call_tool("kg.personalized", {"inp": inp.model_dump(mode="json")})
    mock_svc.personalized.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_related_concepts_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGConceptInput(concept_id="concept-1")
    await mcp_server.call_tool("kg.related_concepts", {"inp": inp.model_dump(mode="json")})
    mock_svc.related_concepts.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_prereqs_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGConceptInput(concept_id="concept-1")
    await mcp_server.call_tool("kg.prereqs", {"inp": inp.model_dump(mode="json")})
    mock_svc.prereqs.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_next_topics_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGNextTopicsInput(concept_id="concept-1", learner_id="learner-1")
    await mcp_server.call_tool("kg.next_topics", {"inp": inp.model_dump(mode="json")})
    mock_svc.next_topics.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_explain_path_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = KGExplainPathInput(src="concept-1", dst="concept-2")
    await mcp_server.call_tool("kg.explain_path", {"inp": inp.model_dump(mode="json")})
    mock_svc.explain_path.assert_awaited_once()


def test_create_server_boots(mock_svc: MagicMock) -> None:
    server = create_server(svc=mock_svc)
    assert server.name == "graphrag"
