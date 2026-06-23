"""Unit tests for the progress MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from schemas.errors import NotFoundError
from schemas.progress import (
    KnowledgeGaps,
    LearnerRefInput,
    ProgressSummary,
    StreakInfo,
    UpdateMasteryInput,
    UpdateMasteryResult,
)

from progress_mcp.errors import invoke, raise_tool_error
from progress_mcp.facade import StubProgressFacade, get_progress_facade
from progress_mcp.server import create_server


@pytest.fixture
def mock_facade() -> MagicMock:
    facade = MagicMock()
    facade.snapshot = AsyncMock(return_value=ProgressSummary(learner_id="learner-1", mastery=[]))
    facade.gaps = AsyncMock(return_value=KnowledgeGaps(learner_id="learner-1", gaps=[]))
    facade.streak = AsyncMock(
        return_value=StreakInfo(learner_id="learner-1", streak_days=3, next_review_at=None)
    )
    facade.update_mastery = AsyncMock(return_value=UpdateMasteryResult(updated=True))
    return facade


@pytest.fixture
def mcp_server(mock_facade: MagicMock):
    return create_server(facade=mock_facade)


@pytest.mark.asyncio
async def test_list_tools_registers_progress_tools(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    names = {tool.name for tool in tools}
    expected = {
        "progress.snapshot",
        "progress.gaps",
        "progress.streak",
        "progress.update_mastery",
    }
    assert expected <= names


@pytest.mark.asyncio
async def test_progress_snapshot(mcp_server, mock_facade: MagicMock) -> None:
    inp = LearnerRefInput(learner_id="learner-1")
    await mcp_server.call_tool("progress.snapshot", {"inp": inp.model_dump(mode="json")})
    mock_facade.snapshot.assert_awaited_once_with("learner-1")


@pytest.mark.asyncio
async def test_progress_gaps(mcp_server, mock_facade: MagicMock) -> None:
    inp = LearnerRefInput(learner_id="learner-1")
    await mcp_server.call_tool("progress.gaps", {"inp": inp.model_dump(mode="json")})
    mock_facade.gaps.assert_awaited_once_with("learner-1")


@pytest.mark.asyncio
async def test_progress_streak(mcp_server, mock_facade: MagicMock) -> None:
    inp = LearnerRefInput(learner_id="learner-1")
    await mcp_server.call_tool("progress.streak", {"inp": inp.model_dump(mode="json")})
    mock_facade.streak.assert_awaited_once_with("learner-1")


@pytest.mark.asyncio
async def test_progress_update_mastery(mcp_server, mock_facade: MagicMock) -> None:
    inp = UpdateMasteryInput(learner_id="learner-1", concept_id="concept-1", score=0.8)
    await mcp_server.call_tool("progress.update_mastery", {"inp": inp.model_dump(mode="json")})
    mock_facade.update_mastery.assert_awaited_once()


def test_create_server_boots(mock_facade: MagicMock) -> None:
    server = create_server(facade=mock_facade)
    assert server.name == "progress"


@pytest.mark.asyncio
async def test_progress_snapshot_maps_app_error(mcp_server, mock_facade: MagicMock) -> None:
    mock_facade.snapshot.side_effect = NotFoundError("learner missing")
    with pytest.raises(ToolError, match="not_found"):
        await mcp_server.call_tool(
            "progress.snapshot", {"inp": LearnerRefInput(learner_id="learner-1").model_dump(mode="json")}
        )


@pytest.mark.asyncio
async def test_stub_facade_defaults() -> None:
    facade = StubProgressFacade()
    snapshot = await facade.snapshot("learner-1")
    assert snapshot.learner_id == "learner-1"
    gaps = await facade.gaps("learner-1")
    assert gaps.gaps == []
    streak = await facade.streak("learner-1")
    assert streak.streak_days == 0
    result = await facade.update_mastery(
        UpdateMasteryInput(learner_id="learner-1", concept_id="c1", score=0.5)
    )
    assert result.updated is True
    assert get_progress_facade() is not None


@pytest.mark.asyncio
async def test_invoke_maps_service_error() -> None:
    async def _fail() -> None:
        raise NotFoundError("missing")

    with pytest.raises(ToolError, match="not_found"):
        await invoke(_fail())


def test_main_invokes_run(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_server = MagicMock()
    monkeypatch.setattr("progress_mcp.server.create_server", lambda **_: mock_server)
    from progress_mcp.server import main

    main()
    mock_server.run.assert_called_once()
