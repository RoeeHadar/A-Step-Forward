"""Chat route — Server-Sent Events stream of orchestrator chunks."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from schemas.agents import ChatRequest

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1", tags=["chat"])


def _get_runner():
    from orchestrator.runner import OrchestratorRunner

    return OrchestratorRunner()


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
        async for chunk in runner.stream(
            body,
            child_mode=ctx.child_mode,
            age=ctx.age,
        ):
            payload = json.dumps(chunk.model_dump(), default=str)
            yield f"event: {chunk.kind}\ndata: {payload}\n\n".encode()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
