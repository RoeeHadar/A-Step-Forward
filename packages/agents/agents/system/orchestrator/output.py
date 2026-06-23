"""Orchestrator output schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from schemas.agents import RouteDecision


class OrchestratorOutput(BaseModel):
    decision: RouteDecision
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    router_mode: Literal["declarative", "llm"] = "declarative"
