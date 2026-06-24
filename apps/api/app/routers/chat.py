"""Chat route — Server-Sent Events stream of orchestrator chunks."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from memory_service.event_writer import persist_memory_event
from schemas.agents import AgentName, ChatChunk, ChatRequest

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1", tags=["chat"])


@router.get("/warmup")
async def warmup() -> dict[str, str]:
    from datetime import datetime

    return {"status": "warm", "ts": datetime.now().isoformat()}


def _get_runner():
    from orchestrator.runner import OrchestratorRunner

    return OrchestratorRunner()


def _build_event_content(*, user_message: str, agent: AgentName, response: str) -> str:
    return f"User: {user_message}\n\nAgent ({agent.value}): {response}"


def _extract_response_text(chunks: list[ChatChunk]) -> str:
    parts = [chunk.text for chunk in chunks if chunk.kind == "token" and chunk.text]
    return " ".join(parts).strip()


def _resolve_agent(chunks: list[ChatChunk]) -> AgentName:
    for chunk in reversed(chunks):
        if chunk.agent is not None:
            return chunk.agent
    return AgentName.ORCHESTRATOR


def _schedule_memory_event(
    *,
    learner_id: str,
    user_message: str,
    chunks: list[ChatChunk],
) -> None:
    response = _extract_response_text(chunks)
    if not response:
        return

    agent = _resolve_agent(chunks)
    content = _build_event_content(user_message=user_message, agent=agent, response=response)

    async def _write() -> None:
        await persist_memory_event(
            learner_id=learner_id,
            agent=agent.value,
            content=content,
            event_type="chat_turn",
        )

    task = asyncio.create_task(_write())

    def _retrieve_task_result(finished: asyncio.Task[None]) -> None:
        if not finished.cancelled():
            finished.exception()

    task.add_done_callback(_retrieve_task_result)


@router.post("/chat")
async def chat(
    body: ChatRequest,
    ctx: AuthCtx = Depends(require_learner),
    runner=Depends(_get_runner),
    _=Depends(per_user("chat.post", per_min=30)),
) -> StreamingResponse:
    if body.learner_id != ctx.learner_id:
        body = body.model_copy(update={"learner_id": ctx.learner_id})

    async def event_stream() -> AsyncIterator[bytes]:
        chunks: list[ChatChunk] = []
        try:
            async for chunk in runner.stream(
                body,
                child_mode=ctx.child_mode,
                age=ctx.age,
            ):
                chunks.append(chunk)
                payload = json.dumps(chunk.model_dump(), default=str)
                yield f"event: {chunk.kind}\ndata: {payload}\n\n".encode()
        finally:
            _schedule_memory_event(
                learner_id=body.learner_id,
                user_message=body.message,
                chunks=chunks,
            )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
