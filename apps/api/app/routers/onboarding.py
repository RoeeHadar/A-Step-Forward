"""Onboarding routes — learner profile creation and status."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from learner_model_service.api import get_learner_model_service
from schemas.learner_model import LearnerProfileInput

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1/onboarding", tags=["onboarding"])


@router.post("/submit")
async def submit_onboarding(
    body: LearnerProfileInput,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learner_model_service),
    _=Depends(per_user("onboarding.submit", per_min=10)),
) -> dict:
    await svc.create_profile(ctx.learner_id, body)
    return {"ok": True}


@router.get("/status")
async def onboarding_status(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learner_model_service),
    _=Depends(per_user("onboarding.status", per_min=60)),
) -> dict:
    profile = await svc.get_profile(ctx.learner_id)
    return {"complete": profile is not None}
