"""Memory MCP tool handlers."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from schemas.memory import (
    CompactionBody,
    CompactionOutput,
    LearnerOnlyBody,
    MemoryConsolidateResult,
    MemoryDeleteResult,
    MemoryDeleteToolBody,
    MemoryHealthReport,
    MemoryRecord,
    MemorySearchBody,
    MemorySearchResult,
    MemoryTimelineBody,
    MemoryUpdateToolBody,
    MemoryWriteToolBody,
)

from memory_mcp.errors import invoke
from memory_service.api import MemoryService, get_memory_service
from memory_service.hygiene.compaction import compact_context


def register_memory_tools(mcp: FastMCP, *, svc: MemoryService | None = None) -> MemoryService:
    """Register all memory.* tools on the given FastMCP instance.

    AS-112: memory.search and memory.compact_context take the *Body input models, so
    FastMCP's argument validation rejects a missing agent_id / messages / target_tokens
    again (pre-AS-90).
    """
    service = svc or get_memory_service()

    @mcp.tool(name="memory.write", description="Persist a new memory for a learner.")
    async def memory_write(inp: MemoryWriteToolBody) -> MemoryRecord:
        return await invoke(service.write(inp.input, agent_id=inp.agent_id))

    @mcp.tool(name="memory.search", description="Search learner memories with hybrid retrieval and policy filtering.")
    async def memory_search(inp: MemorySearchBody) -> list[MemorySearchResult]:
        return await invoke(service.search(inp))

    @mcp.tool(name="memory.timeline", description="List episodic memories for a learner within a time window.")
    async def memory_timeline(inp: MemoryTimelineBody) -> list[MemoryRecord]:
        return await invoke(
            service.timeline(learner_id=inp.learner_id, since=inp.since, until=inp.until, k=inp.k)
        )

    @mcp.tool(name="memory.update", description="Patch a memory after a learner correction. Reason required in patch.")
    async def memory_update(inp: MemoryUpdateToolBody) -> MemoryRecord:
        return await invoke(
            service.update(inp.memory_id, inp.patch, learner_id=inp.learner_id, agent_id=inp.agent_id)
        )

    @mcp.tool(name="memory.delete", description="Soft-delete a memory, or hard-delete on learner request.")
    async def memory_delete(inp: MemoryDeleteToolBody) -> MemoryDeleteResult:
        await invoke(
            service.delete(inp.memory_id, learner_id=inp.learner_id, agent_id=inp.agent_id, hard=inp.hard)
        )
        return MemoryDeleteResult(deleted=True)

    @mcp.tool(name="memory.dream_now", description="Trigger a dreaming pass for a learner (admin/internal).")
    async def memory_dream_now(inp: LearnerOnlyBody) -> MemoryHealthReport:
        return await invoke(service.dream_now(learner_id=inp.learner_id))

    @mcp.tool(name="memory.consolidate", description="Force a consolidation pass for a learner.")
    async def memory_consolidate(inp: LearnerOnlyBody) -> MemoryConsolidateResult:
        count = await invoke(service.consolidate(learner_id=inp.learner_id))
        return MemoryConsolidateResult(merged_or_candidates=count)

    @mcp.tool(
        name="memory.compact_context",
        description="Compact a conversation transcript to fit a target token budget.",
    )
    async def memory_compact_context(inp: CompactionBody) -> CompactionOutput:
        return await invoke(compact_context(inp))

    return service
