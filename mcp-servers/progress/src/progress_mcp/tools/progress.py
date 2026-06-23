"""Progress MCP tool handlers."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from schemas.progress import (
    KnowledgeGaps,
    LearnerRefInput,
    ProgressSummary,
    StreakInfo,
    UpdateMasteryInput,
    UpdateMasteryResult,
)

from progress_mcp.errors import raise_tool_error
from progress_mcp.facade import ProgressFacade, get_progress_facade


def register_progress_tools(
    mcp: FastMCP,
    *,
    facade: ProgressFacade | None = None,
) -> ProgressFacade:
    service = facade or get_progress_facade()

    @mcp.tool(name="progress.snapshot", description="Return the current mastery summary for a learner.")
    async def progress_snapshot(inp: LearnerRefInput) -> ProgressSummary:
        try:
            return await service.snapshot(inp.learner_id)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="progress.gaps", description="Return identified knowledge gaps for a learner.")
    async def progress_gaps(inp: LearnerRefInput) -> KnowledgeGaps:
        try:
            return await service.gaps(inp.learner_id)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="progress.streak", description="Return study streak and next review time for a learner.")
    async def progress_streak(inp: LearnerRefInput) -> StreakInfo:
        try:
            return await service.streak(inp.learner_id)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="progress.update_mastery", description="Update mastery score for a learner and concept.")
    async def progress_update_mastery(inp: UpdateMasteryInput) -> UpdateMasteryResult:
        try:
            return await service.update_mastery(inp)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    return service
