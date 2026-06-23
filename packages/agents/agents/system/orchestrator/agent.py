"""Orchestrator agent — routes user intent to the correct runtime agent(s)."""

from __future__ import annotations

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import AgentSummary, OrchestratorInput
from .memory_policy import MEMORY_POLICY
from .output import OrchestratorOutput
from .router import DeclarativeRouter
from .tools import TOOLS


class OrchestratorAgent(Agent[OrchestratorInput, OrchestratorOutput]):
    """Classifies intent and selects one or more agents from the registry."""

    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.ORCHESTRATOR]
        super().__init__(manifest=manifest)
        self._declarative_router = DeclarativeRouter()
        self._system_prompt = load_prompt("orchestrator", self.prompt_version)

    async def run(self, inp: OrchestratorInput, ctx: AgentContext) -> AgentResult[OrchestratorOutput]:
        # Phase 1: declarative routing (fast, offline-testable). LLM routing can
        # use self._system_prompt when ambiguous cases need disambiguation.
        _ = (self._system_prompt, ctx)
        decision = self._declarative_router.route(inp)
        output = OrchestratorOutput(
            decision=decision,
            confidence=1.0,
            router_mode="declarative",
        )
        return AgentResult(output=output)


def build_agent_summaries() -> list[AgentSummary]:
    """Summaries of all registered agents for routing context."""
    return [
        AgentSummary(name=name, description=manifest.description)
        for name, manifest in AGENT_REGISTRY.items()
        if name != AgentName.ORCHESTRATOR
    ]


__all__ = [
    "OrchestratorAgent",
    "OrchestratorInput",
    "OrchestratorOutput",
    "DeclarativeRouter",
    "build_agent_summaries",
]
