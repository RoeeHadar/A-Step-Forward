"""GraphRAG routes — thin proxy over GraphRAGService."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from graphrag_service.api import get_graphrag_service
from schemas.graph import KGHybridInput, KGSearchInput, KGSearchResult

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1/graphrag", tags=["graphrag"])


@router.post("/search", response_model=list[KGSearchResult])
async def search(
    body: KGSearchInput,
    _ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_graphrag_service),
    _=Depends(per_user("graphrag.search", per_min=120)),
) -> list[KGSearchResult]:
    return await svc.search(body)


@router.post("/hybrid", response_model=list[KGSearchResult])
async def hybrid(
    body: KGHybridInput,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_graphrag_service),
    _=Depends(per_user("graphrag.hybrid", per_min=120)),
) -> list[KGSearchResult]:
    body = body.model_copy(update={"learner_id": ctx.learner_id})
    return await svc.hybrid(body)
