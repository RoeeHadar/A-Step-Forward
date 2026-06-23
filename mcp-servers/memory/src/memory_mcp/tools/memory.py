"""Memory MCP tool handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from schemas.memory import (
    CompactionInput,
    CompactionOutput,
    LearnerOnlyInput,
    MemoryConsolidateResult,
    MemoryDeleteResult,
    MemoryDeleteToolInput,
    MemoryHealthReport,
    MemoryRecord,
    MemorySearchInput,
    MemorySearchResult,
    MemoryTimelineInput,
    MemoryUpdateToolInput,
    MemoryWriteToolInput,
)

from memory_mcp.errors import raise_tool_error
from memory_service.api import MemoryService, get_memory_service
from memory_service.hygiene.compaction import compact_context

if TYPE_CHECKING:
    pass


def register_memory_tools(mcp: FastMCP, *, svc: MemoryService | None = None) -> MemoryService:
    """Register all memory.* tools on the given FastMCP instance."""
    service = svc or get_memory_service()

    @mcp.tool(name="memory.write", description="Persist a new memory for a learner.")
    async def memory_write(inp: MemoryWriteToolInput) -> MemoryRecord:
        try:
            return await service.write(inp.input, agent_id=inp.agent_id)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="memory.search", description="Search learner memories with hybrid retrieval and policy filtering.")
    async def memory_search(inp: MemorySearchInput) -> list[MemorySearchResult]:
        try:
            return await service.search(inp)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="memory.timeline", description="List episodic memories for a learner within a time window.")
    async def memory_timeline(inp: MemoryTimelineInput) -> list[MemoryRecord]:
        try:
            return await service.timeline(
                learner_id=inp.learner_id,
                since=inp.since,
                until=inp.until,
                k=inp.k,
            )
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="memory.update", description="Patch a memory after a learner correction. Reason required in patch.")
    async def memory_update(inp: MemoryUpdateToolInput) -> MemoryRecord:
        try:
            return await service.update(
                inp.memory_id,
                inp.patch,
                learner_id=inp.learner_id,
                agent_id=inp.agent_id,
            )
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="memory.delete", description="Soft-delete a memory, or hard-delete on learner request.")
    async def memory_delete(inp: MemoryDeleteToolInput) -> MemoryDeleteResult:
        try:
            await service.delete(
                inp.memory_id,
                learner_id=inp.learner_id,
                agent_id=inp.agent_id,
                hard=inp.hard,
            )
            return MemoryDeleteResult(deleted=True)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="memory.dream_now", description="Trigger a dreaming pass for a learner (admin/internal).")
    async def memory_dream_now(inp: LearnerOnlyInput) -> MemoryHealthReport:
        try:
            return await service.dream_now(learner_id=inp.learner_id)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(name="memory.consolidate", description="Force a consolidation pass for a learner.")
    async def memory_consolidate(inp: LearnerOnlyInput) -> MemoryConsolidateResult:
        try:
            count = await service.consolidate(learner_id=inp.learner_id)
            return MemoryConsolidateResult(merged_or_candidates=count)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    @mcp.tool(
        name="memory.compact_context",
        description="Compact a conversation transcript to fit a target token budget.",
    )
    async def memory_compact_context(inp: CompactionInput) -> CompactionOutput:
        try:
            return await compact_context(inp)
        except Exception as exc:
            raise_tool_error(exc)
            raise AssertionError("unreachable")

    return service
