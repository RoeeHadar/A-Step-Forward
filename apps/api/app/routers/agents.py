"""Agent listing route."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from agents import AGENT_REGISTRY
from schemas.agents import AgentManifest

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1/agents", tags=["agents"])


@router.get("", response_model=list[AgentManifest])
async def list_agents(
    ctx: AuthCtx = Depends(require_learner),
    _=Depends(per_user("agents.list", per_min=120)),
) -> list[AgentManifest]:
    _ = ctx
    return list(AGENT_REGISTRY.values())
