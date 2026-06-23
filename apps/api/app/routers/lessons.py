"""Lesson routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from schemas.curriculum import Lesson

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user
from ..services.curriculum import get_curriculum_service

router = APIRouter(prefix="/v1/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=Lesson)
async def get_lesson(
    lesson_id: str,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_curriculum_service),
    _=Depends(per_user("lessons.get", per_min=120)),
) -> Lesson:
    _ = ctx
    return await svc.get_lesson(lesson_id)
