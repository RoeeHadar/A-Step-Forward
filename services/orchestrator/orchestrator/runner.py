"""Orchestrator runner — entry point for the API gateway.

The runner exposes two surfaces:

- :meth:`OrchestratorRunner.stream` — async generator of :class:`ChatChunk`
  used by the FastAPI SSE endpoint. For agents that implement
  ``astream_reply`` (the Tutor today) tokens are forwarded as they arrive
  from the LLM; other agents fall back to the LangGraph-based dispatch.
- :meth:`OrchestratorRunner.handle` — convenience wrapper that buffers the
  stream into a list, used by batch callers and tests.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from memory_service.api import get_memory_service
from schemas.agents import AgentName, ChatChunk, ChatRequest, RouteDecision

from agents import AGENT_FACTORIES
from agents.base.agent import AgentContext
from agents.system.orchestrator import (
    OrchestratorAgent,
    OrchestratorInput,
    build_agent_summaries,
)

from .episodic import persist_episodic_turn
from .graph import build_graph, new_context
from .invoke import AGENT_DISPATCH, invoke_registered_agent

if TYPE_CHECKING:
    from memory_service.api import MemoryService

logger = logging.getLogger(__name__)

# Agents that implement ``astream_reply`` and should get the streaming path.
STREAMING_AGENTS: frozenset[AgentName] = frozenset({AgentName.TUTOR})


class OrchestratorRunner:
    def __init__(self, memory_service: MemoryService | None = None) -> None:
        self._graph = build_graph()
        self._memory = memory_service or get_memory_service()

    async def handle(
        self,
        request: ChatRequest,
        *,
        child_mode: bool = False,
        age: int | None = None,
    ) -> list[ChatChunk]:
        chunks: list[ChatChunk] = []
        async for chunk in self.stream(request, child_mode=child_mode, age=age):
            chunks.append(chunk)
        return chunks

    async def stream(
        self,
        request: ChatRequest,
        *,
        child_mode: bool = False,
        age: int | None = None,
    ) -> AsyncIterator[ChatChunk]:
        ctx = new_context(
            request,
            child_mode=child_mode,
            age=age,
            memory_api=self._memory,
        )
        decision = await self._route(request, ctx)

        if decision is None or not decision.selected_agents:
            yield ChatChunk(
                kind="error",
                agent=AgentName.ORCHESTRATOR,
                text="Routing failed.",
            )
            yield ChatChunk(kind="done", agent=AgentName.ORCHESTRATOR)
            return

        selected = decision.selected_agents[0]
        chunks: list[ChatChunk] = []

        if selected in STREAMING_AGENTS:
            async for chunk in self._stream_agent(selected, request, ctx):
                chunks.append(chunk)
                yield chunk
        else:
            async for chunk in self._fallback_dispatch(selected, request, ctx):
                chunks.append(chunk)
                yield chunk

        await persist_episodic_turn(
            self._memory,
            request=request,
            ctx=ctx,
            agent=selected,
            chunks=chunks,
            child_mode=ctx.child_mode,
        )

    async def _route(self, request: ChatRequest, ctx: AgentContext) -> RouteDecision | None:
        try:
            orchestrator = OrchestratorAgent()
            result = await orchestrator(
                OrchestratorInput(
                    learner_id=request.learner_id,
                    message=request.message,
                    requested_agent=request.requested_agent,
                    session_id=request.session_id,
                    locale=request.locale,
                    available_agents=build_agent_summaries(),
                ),
                ctx,
            )
        except Exception:
            logger.exception("orchestrator.route_failed")
            return None
        return result.output.decision

    async def _stream_agent(
        self,
        selected: AgentName,
        request: ChatRequest,
        ctx: AgentContext,
    ) -> AsyncIterator[ChatChunk]:
        factory = AGENT_FACTORIES.get(selected)
        dispatch = AGENT_DISPATCH.get(selected)
        if factory is None or dispatch is None:
            async for chunk in self._fallback_dispatch(selected, request, ctx):
                yield chunk
            return

        agent = factory()
        if not hasattr(agent, "astream_reply"):
            chunks = await invoke_registered_agent(selected, agent, request, ctx)
            for chunk in chunks:
                yield chunk
            return

        inp = dispatch.build_input(request)
        emitted = False
        try:
            async for chunk in agent.astream_reply(inp, ctx):
                emitted = True
                yield chunk
        except Exception:
            logger.exception("orchestrator.stream_failed", extra={"agent": selected.value})
            yield ChatChunk(
                kind="error",
                agent=selected,
                text="The streaming agent hit an error. Please try again.",
            )

        if not emitted:
            chunks = await invoke_registered_agent(selected, agent, request, ctx)
            for chunk in chunks:
                yield chunk
            return

        yield ChatChunk(kind="done", agent=selected)

    async def _fallback_dispatch(
        self,
        selected: AgentName,
        request: ChatRequest,
        ctx: AgentContext,
    ) -> AsyncIterator[ChatChunk]:
        factory = AGENT_FACTORIES.get(selected)
        if factory is None:
            yield ChatChunk(
                kind="token",
                agent=selected,
                text=(
                    f"The {selected.value.replace('_', ' ')} agent is registered but not "
                    "implemented yet."
                ),
            )
            yield ChatChunk(kind="done", agent=selected)
            return

        if selected not in AGENT_DISPATCH:
            yield ChatChunk(
                kind="token",
                agent=selected,
                text=f"[stub] Agent '{selected.value}' invoked successfully.",
            )
            yield ChatChunk(kind="done", agent=selected)
            return

        agent = factory()
        chunks = await invoke_registered_agent(selected, agent, request, ctx)
        for chunk in chunks:
            yield chunk
