"""Progress MCP tool handlers."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from schemas.progress import (
    KnowledgeGaps,
    LearnerRefBody,
    ProgressSummary,
    StreakInfo,
    UpdateMasteryBody,
    UpdateMasteryResult,
)

from progress_mcp.errors import invoke
from progress_mcp.facade import ProgressFacade, get_progress_facade


def register_progress_tools(
    mcp: FastMCP,
    *,
    facade: ProgressFacade | None = None,
) -> ProgressFacade:
    service = facade or get_progress_facade()

    @mcp.tool(name="progress.snapshot", description="Return the current mastery summary for a learner.")
    async def progress_snapshot(inp: LearnerRefBody) -> ProgressSummary:
        return await invoke(service.snapshot(inp.learner_id))

    @mcp.tool(name="progress.gaps", description="Return identified knowledge gaps for a learner.")
    async def progress_gaps(inp: LearnerRefBody) -> KnowledgeGaps:
        return await invoke(service.gaps(inp.learner_id))

    @mcp.tool(name="progress.streak", description="Return study streak and next review time for a learner.")
    async def progress_streak(inp: LearnerRefBody) -> StreakInfo:
        return await invoke(service.streak(inp.learner_id))

    @mcp.tool(name="progress.update_mastery", description="Update mastery score for a learner and concept.")
    async def progress_update_mastery(inp: UpdateMasteryBody) -> UpdateMasteryResult:
        return await invoke(service.update_mastery(inp))

    return service
