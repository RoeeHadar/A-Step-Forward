"""Orchestrator input schema."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.agents import AgentName


class AgentSummary(BaseModel):
    """Lightweight agent descriptor for routing context."""

    name: AgentName
    description: str


class OrchestratorInput(BaseModel):
    learner_id: str
    message: str
    requested_agent: AgentName | None = None
    session_id: str | None = None
    locale: str = "en"
    available_agents: list[AgentSummary] = Field(default_factory=list)
