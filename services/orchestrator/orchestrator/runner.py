"""Orchestrator runner — LangGraph entry point for the API gateway."""

from __future__ import annotations

from collections.abc import AsyncIterator

from schemas.agents import ChatChunk, ChatRequest

from .graph import build_graph, new_context


class OrchestratorRunner:
    def __init__(self) -> None:
        self._graph = build_graph()

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
        ctx = new_context(request, child_mode=child_mode, age=age)
        initial: dict[str, object] = {
            "request": request,
            "ctx": ctx,
            "decision": None,
            "chunks": [],
        }
        async for update in self._graph.astream(initial, stream_mode="updates"):
            for node_output in update.values():
                if not isinstance(node_output, dict):
                    continue
                for chunk in node_output.get("chunks", []):
                    if isinstance(chunk, ChatChunk):
                        yield chunk
