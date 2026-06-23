"""Unit tests for the progress MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from schemas.progress import (
    KnowledgeGaps,
    LearnerRefInput,
    ProgressSummary,
    StreakInfo,
    UpdateMasteryInput,
    UpdateMasteryResult,
)

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
