"""Progress routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from schemas.progress import ProgressSummary

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user
from ..services.progress_svc import get_progress_service

router = APIRouter(prefix="/v1/progress", tags=["progress"])


@router.get("", response_model=ProgressSummary)
async def get_progress(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_progress_service),
    _=Depends(per_user("progress.get", per_min=120)),
) -> ProgressSummary:
    return await svc.snapshot(ctx)
