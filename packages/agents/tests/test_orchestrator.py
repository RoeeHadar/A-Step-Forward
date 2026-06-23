"""Unit tests for the orchestrator agent and declarative router."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from schemas.agents import AgentName

from agents.base.agent import AgentContext
from agents.base.prompts import load_prompt
from agents.system.orchestrator import DeclarativeRouter, OrchestratorAgent, OrchestratorInput
from agents.system.orchestrator.budget import BUDGET


@pytest.fixture
def router() -> DeclarativeRouter:
    return DeclarativeRouter()


@pytest.fixture
def ctx() -> AgentContext:
    return AgentContext(learner_id="learner-1", session_id="sess-1", turn_id="turn-1")


def test_orchestrator_prompt_loads() -> None:
    text = load_prompt("orchestrator", "v1")
    assert "Orchestrator" in text
    assert "OrchestratorOutput" in text


def test_budget_within_slo() -> None:
    assert BUDGET.max_latency_ms <= 2_000
    assert BUDGET.max_cost_usd <= 0.02


@pytest.mark.asyncio
async def test_orchestrator_agent_routes_explanation(ctx: AgentContext) -> None:
    agent = OrchestratorAgent()
    result = await agent(
        OrchestratorInput(learner_id="learner-1", message="Why is the sky blue?"),
        ctx,
    )
    assert result.output.decision.selected_agents == [AgentName.QA_EXPLAINER]
    assert result.output.router_mode == "declarative"


def test_router_lesson_intent(router: DeclarativeRouter) -> None:
    decision = router.route(
        OrchestratorInput(learner_id="learner-1", message="Walk me through this lesson step by step.")
    )
    assert decision.selected_agents == [AgentName.TUTOR]
