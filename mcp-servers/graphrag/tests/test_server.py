"""Unit tests for the GraphRAG MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from schemas.errors import NotFoundError
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

from graphrag_mcp.errors import invoke, raise_tool_error
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
    assert {
        "kg.search",
        "kg.walk",
        "kg.hybrid",
        "kg.personalized",
        "kg.related_concepts",
        "kg.prereqs",
        "kg.next_topics",
        "kg.explain_path",
    } <= names


@pytest.mark.asyncio
async def test_kg_search_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool("kg.search", {"inp": KGSearchInput(query="fractions").model_dump(mode="json")})
    mock_svc.search.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_walk_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "kg.walk", {"inp": KGWalkInput(seed_node_ids=["concept-1"]).model_dump(mode="json")}
    )
    mock_svc.walk.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_hybrid_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool("kg.hybrid", {"inp": KGHybridInput(query="fractions").model_dump(mode="json")})
    mock_svc.hybrid.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_personalized_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "kg.personalized",
        {"inp": KGPersonalizedInput(learner_id="learner-1", query="fractions").model_dump(mode="json")},
    )
    mock_svc.personalized.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_related_concepts_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "kg.related_concepts", {"inp": KGConceptInput(concept_id="concept-1").model_dump(mode="json")}
    )
    mock_svc.related_concepts.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_prereqs_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool("kg.prereqs", {"inp": KGConceptInput(concept_id="concept-1").model_dump(mode="json")})
    mock_svc.prereqs.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_next_topics_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "kg.next_topics",
        {"inp": KGNextTopicsInput(concept_id="concept-1", learner_id="learner-1").model_dump(mode="json")},
    )
    mock_svc.next_topics.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_explain_path_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "kg.explain_path",
        {"inp": KGExplainPathInput(src="concept-1", dst="concept-2").model_dump(mode="json")},
    )
    mock_svc.explain_path.assert_awaited_once()


@pytest.mark.asyncio
async def test_kg_search_maps_app_error(mcp_server, mock_svc: MagicMock) -> None:
    mock_svc.search.side_effect = NotFoundError("graph empty")
    with pytest.raises(ToolError, match="not_found"):
        await mcp_server.call_tool("kg.search", {"inp": KGSearchInput(query="fractions").model_dump(mode="json")})


def test_raise_tool_error_branches() -> None:
    with pytest.raises(ToolError, match="not_found"):
        try:
            raise NotFoundError("missing")
        except Exception as exc:
            raise_tool_error(exc)


@pytest.mark.asyncio
async def test_invoke_maps_service_error() -> None:
    async def _fail() -> None:
        raise NotFoundError("missing")

    with pytest.raises(ToolError, match="not_found"):
        await invoke(_fail())


def test_create_server_boots(mock_svc: MagicMock) -> None:
    assert create_server(svc=mock_svc).name == "graphrag"


def test_main_invokes_run(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_server = MagicMock()
    monkeypatch.setattr("graphrag_mcp.server.create_server", lambda **_: mock_server)
    from graphrag_mcp.server import main

    main()
    mock_server.run.assert_called_once()
