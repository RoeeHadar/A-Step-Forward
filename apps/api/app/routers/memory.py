"""Memory routes — thin proxy over MemoryService."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from memory_service.api import get_memory_service
from schemas.memory import (
    MemoryRecord,
    MemorySearchInput,
    MemorySearchResult,
    MemoryUpdateInput,
    MemoryWriteInput,
)

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1/memory", tags=["memory"])


@router.get("", response_model=list[MemoryRecord])
async def list_memories(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_memory_service),
    q: str | None = Query(default=None, description="Optional search query"),
    k: int = Query(default=100, ge=1, le=200),
    _=Depends(per_user("memory.list", per_min=120)),
) -> list[MemoryRecord]:
    if q:
        results = await svc.search(
            MemorySearchInput(
                learner_id=ctx.learner_id,
                query=q,
                k=k,
                agent_id="user:memory_inspector",
            )
        )
        return [r.record for r in results]
    return await svc.timeline(learner_id=ctx.learner_id, k=k)


@router.post("", response_model=MemoryRecord)
async def create(
    body: MemoryWriteInput,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_memory_service),
    _=Depends(per_user("memory.create", per_min=60)),
) -> MemoryRecord:
    if body.learner_id != ctx.learner_id:
        body = body.model_copy(update={"learner_id": ctx.learner_id})
    return await svc.write(body, agent_id="user:memory_inspector", child_mode=ctx.child_mode)


@router.post("/search", response_model=list[MemorySearchResult])
async def search(
    body: MemorySearchInput,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_memory_service),
    _=Depends(per_user("memory.search", per_min=120)),
) -> list[MemorySearchResult]:
    if body.learner_id != ctx.learner_id:
        body = body.model_copy(update={"learner_id": ctx.learner_id})
    return await svc.search(body)


@router.get("/timeline", response_model=list[MemoryRecord])
async def timeline(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_memory_service),
    k: int = 100,
    _=Depends(per_user("memory.timeline", per_min=120)),
) -> list[MemoryRecord]:
    return await svc.timeline(learner_id=ctx.learner_id, k=k)


@router.patch("/{memory_id}", response_model=MemoryRecord)
async def update(
    memory_id: str,
    patch: MemoryUpdateInput,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_memory_service),
    _=Depends(per_user("memory.update", per_min=60)),
) -> MemoryRecord:
    return await svc.update(memory_id, patch, learner_id=ctx.learner_id, agent_id="user:memory_inspector")


@router.delete("/{memory_id}")
async def delete(
    memory_id: str,
    hard: bool = False,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_memory_service),
    _=Depends(per_user("memory.delete", per_min=60)),
) -> dict[str, bool]:
    await svc.delete(memory_id, learner_id=ctx.learner_id, agent_id="user:memory_inspector", hard=hard)
    return {"deleted": True}
