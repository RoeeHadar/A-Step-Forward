"""Adaptive diagnostic assessment routes."""

from __future__ import annotations

from diagnostic_service.api import get_diagnostic_service
from fastapi import APIRouter, Depends

from schemas.diagnostic import (
    DiagnosticAnswerRequest,
    DiagnosticAnswerResponse,
    DiagnosticSessionState,
    DiagnosticStartRequest,
    DiagnosticStartResponse,
)

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1/diagnostic", tags=["diagnostic"])


@router.post("/start", response_model=DiagnosticStartResponse)
async def start_diagnostic(
    body: DiagnosticStartRequest,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_diagnostic_service),
    _=Depends(per_user("diagnostic.start", per_min=10)),
) -> DiagnosticStartResponse:
    return await svc.start(ctx.learner_id, body)


@router.post("/{session_id}/answer", response_model=DiagnosticAnswerResponse)
async def answer_diagnostic(
    session_id: str,
    body: DiagnosticAnswerRequest,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_diagnostic_service),
    _=Depends(per_user("diagnostic.answer", per_min=120)),
) -> DiagnosticAnswerResponse:
    return await svc.answer(ctx.learner_id, session_id, body)


@router.get("/{session_id}", response_model=DiagnosticSessionState)
async def get_diagnostic_session(
    session_id: str,
    ctx: AuthCtx = Depends(require_learner),
    svc=Depends(get_diagnostic_service),
    _=Depends(per_user("diagnostic.get", per_min=60)),
) -> DiagnosticSessionState:
    return await svc.get_session(ctx.learner_id, session_id)
