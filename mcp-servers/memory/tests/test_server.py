"""Unit tests for the memory MCP server."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import BaseModel, ValidationError
from schemas.common import Provenance
from schemas.errors import NotFoundError, ValidationFailed
from schemas.memory import (
    CompactionInput,
    CompactionOutput,
    LearnerOnlyInput,
    MemoryHealthReport,
    MemoryRecord,
    MemorySearchInput,
    MemorySearchResult,
    MemoryTimelineInput,
    MemoryType,
    MemoryUpdateInput,
    MemoryUpdateToolInput,
    MemoryWriteInput,
    MemoryWriteToolInput,
    MemoryDeleteToolInput,
)

from memory_mcp.errors import invoke, raise_tool_error
from memory_mcp.server import create_server


def _sample_record() -> MemoryRecord:
    return MemoryRecord(
        id="mem-1",
        learner_id="learner-1",
        type=MemoryType.EPISODIC,
        content="Worked example of long division.",
        provenance=Provenance(kind="chat", id="turn-1", agent="tutor"),
    )


@pytest.fixture
def mock_svc() -> MagicMock:
    svc = MagicMock()
    svc.write = AsyncMock(return_value=_sample_record())
    svc.search = AsyncMock(return_value=[MemorySearchResult(record=_sample_record(), score=0.9)])
    svc.timeline = AsyncMock(return_value=[_sample_record()])
    svc.update = AsyncMock(return_value=_sample_record())
    svc.delete = AsyncMock(return_value=None)
    svc.dream_now = AsyncMock(
        return_value=MemoryHealthReport(
            learner_id="learner-1",
            window_start=datetime.now(timezone.utc),
            window_end=datetime.now(timezone.utc),
            items_reviewed=0,
            items_promoted=0,
            items_archived=0,
            items_merged=0,
            conflicts_resolved=0,
            conflicts_pending=0,
        )
    )
    svc.consolidate = AsyncMock(return_value=2)
    return svc


@pytest.fixture
def mcp_server(mock_svc: MagicMock):
    return create_server(svc=mock_svc)


@pytest.mark.asyncio
async def test_list_tools_registers_all_memory_tools(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    names = {tool.name for tool in tools}
    assert {
        "memory.write",
        "memory.search",
        "memory.timeline",
        "memory.update",
        "memory.delete",
        "memory.dream_now",
        "memory.consolidate",
        "memory.compact_context",
    } <= names


@pytest.mark.asyncio
async def test_memory_write_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    write_inp = MemoryWriteInput(
        learner_id="learner-1",
        type=MemoryType.EPISODIC,
        content="hello",
        provenance=Provenance(kind="chat", id="t1", agent="tutor"),
    )
    await mcp_server.call_tool(
        "memory.write",
        {"inp": MemoryWriteToolInput(agent_id="tutor", input=write_inp).model_dump(mode="json")},
    )
    mock_svc.write.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_search_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    search_inp = MemorySearchInput(learner_id="learner-1", query="division", agent_id="tutor")
    await mcp_server.call_tool("memory.search", {"inp": search_inp.model_dump(mode="json")})
    mock_svc.search.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_timeline_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "memory.timeline", {"inp": MemoryTimelineInput(learner_id="learner-1").model_dump(mode="json")}
    )
    mock_svc.timeline.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_update_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    update_inp = MemoryUpdateToolInput(
        memory_id="mem-1",
        learner_id="learner-1",
        agent_id="tutor",
        patch=MemoryUpdateInput(content="corrected", reason="learner fix"),
    )
    await mcp_server.call_tool("memory.update", {"inp": update_inp.model_dump(mode="json")})
    mock_svc.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_delete_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    delete_inp = MemoryDeleteToolInput(memory_id="mem-1", learner_id="learner-1", agent_id="tutor")
    await mcp_server.call_tool("memory.delete", {"inp": delete_inp.model_dump(mode="json")})
    mock_svc.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_dream_now_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "memory.dream_now", {"inp": LearnerOnlyInput(learner_id="learner-1").model_dump(mode="json")}
    )
    mock_svc.dream_now.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_consolidate_happy_path(mcp_server, mock_svc: MagicMock) -> None:
    await mcp_server.call_tool(
        "memory.consolidate", {"inp": LearnerOnlyInput(learner_id="learner-1").model_dump(mode="json")}
    )
    mock_svc.consolidate.assert_awaited_once()


@pytest.mark.asyncio
async def test_memory_compact_context_happy_path(mcp_server) -> None:
    compact_out = CompactionOutput(
        messages=[{"role": "user", "content": "hi"}],
        compacted_summary="summary",
        kept_verbatim_count=1,
        estimated_tokens=100,
    )
    with patch("memory_mcp.tools.memory.compact_context", AsyncMock(return_value=compact_out)):
        await mcp_server.call_tool(
            "memory.compact_context",
            {
                "inp": CompactionInput(
                    messages=[{"role": "user", "content": "hello"}],
                    target_tokens=512,
                ).model_dump(mode="json")
            },
        )


@pytest.mark.asyncio
async def test_memory_write_maps_app_error(mcp_server, mock_svc: MagicMock) -> None:
    mock_svc.write.side_effect = NotFoundError("missing memory")
    write_inp = MemoryWriteInput(
        learner_id="learner-1",
        type=MemoryType.EPISODIC,
        content="hello",
        provenance=Provenance(kind="chat", id="t1", agent="tutor"),
    )
    with pytest.raises(ToolError, match="not_found"):
        await mcp_server.call_tool(
            "memory.write",
            {"inp": MemoryWriteToolInput(agent_id="tutor", input=write_inp).model_dump(mode="json")},
        )


def test_raise_tool_error_branches() -> None:
    with pytest.raises(ToolError, match="already mapped"):
        try:
            raise ToolError("already mapped")
        except Exception as exc:
            raise_tool_error(exc)

    class _M(BaseModel):
        x: int

    with pytest.raises(ToolError, match="validation_failed"):
        try:
            _M(x="bad")
        except ValidationError as exc:
            raise_tool_error(exc)

    with pytest.raises(ToolError, match="internal_error"):
        try:
            raise RuntimeError("boom")
        except Exception as exc:
            raise_tool_error(exc)

    with pytest.raises(ToolError, match="validation_failed: bad"):
        try:
            raise ValidationFailed("bad")
        except Exception as exc:
            raise_tool_error(exc)


@pytest.mark.asyncio
async def test_invoke_maps_service_error() -> None:
    async def _fail() -> None:
        raise NotFoundError("nope")

    with pytest.raises(ToolError, match="not_found"):
        await invoke(_fail())


def test_create_server_boots(mock_svc: MagicMock) -> None:
    assert create_server(svc=mock_svc).name == "memory"


def test_main_invokes_run(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_server = MagicMock()
    monkeypatch.setattr("memory_mcp.server.create_server", lambda **_: mock_server)
    from memory_mcp.server import main

    main()
    mock_server.run.assert_called_once()
