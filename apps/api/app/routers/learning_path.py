"""Learning path API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from learning_path_service.api import get_learning_path_service
from schemas.learning_path import (
    LearningPlan,
    PlanWeek,
    QuizStartResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from schemas.errors import NotFoundError

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1/learners/me/plans", tags=["learning-path"])


@router.post("/generate", response_model=LearningPlan)
async def generate_plan(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learning_path_service),
    _=Depends(per_user("learning_path.generate", per_min=10)),
) -> LearningPlan:
    return await svc.generate_plan(ctx.learner_id)


@router.get("/current", response_model=LearningPlan)
async def get_current_plan(
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learning_path_service),
    _=Depends(per_user("learning_path.current", per_min=60)),
) -> LearningPlan:
    plan = await svc.get_current_plan(ctx.learner_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="No active learning plan")
    return plan


@router.get("/{plan_id}/weeks/{week_num}", response_model=PlanWeek)
async def get_plan_week(
    plan_id: str,
    week_num: int,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learning_path_service),
    _=Depends(per_user("learning_path.week", per_min=60)),
) -> PlanWeek:
    try:
        return await svc.get_week(ctx.learner_id, plan_id, week_num)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{plan_id}/weeks/{week_num}/quiz", response_model=QuizStartResponse)
async def start_week_quiz(
    plan_id: str,
    week_num: int,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learning_path_service),
    _=Depends(per_user("learning_path.quiz.start", per_min=10)),
) -> QuizStartResponse:
    try:
        return await svc.start_quiz(ctx.learner_id, plan_id, week_num)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{plan_id}/weeks/{week_num}/quiz/submit", response_model=QuizSubmitResponse)
async def submit_week_quiz(
    plan_id: str,
    week_num: int,
    body: QuizSubmitRequest,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_learning_path_service),
    _=Depends(per_user("learning_path.quiz.submit", per_min=10)),
) -> QuizSubmitResponse:
    # quiz_id is embedded in the URL; resolve it from the week
    try:
        quiz = await svc.start_quiz(ctx.learner_id, plan_id, week_num)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        return await svc.submit_quiz(ctx.learner_id, quiz.quiz_id, body.answers)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
