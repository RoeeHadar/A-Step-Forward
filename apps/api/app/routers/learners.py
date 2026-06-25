"""Learner profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from learner_model_service.api import get_learner_model_service
from schemas.learner_model import StudentModel
from schemas.learners import LearnerProfile

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user
from ..services.learner import get_learner_service

router = APIRouter(prefix="/v1/learners", tags=["learners"])


@router.get("/me", response_model=LearnerProfile)
async def get_me(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learner_service),
    _=Depends(per_user("learners.me", per_min=120)),
) -> LearnerProfile:
    return await svc.get_or_create(ctx)


@router.get("/me/model", response_model=StudentModel)
async def get_my_model(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learner_model_service),
    _=Depends(per_user("learners.me.model", per_min=60)),
) -> StudentModel:
    return await svc.get_student_model(ctx.learner_id)
