"""Routing eval matrix for the orchestrator declarative router."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from schemas.agents import AgentName

from agents.system.orchestrator import DeclarativeRouter, OrchestratorInput

ROUTER = DeclarativeRouter()

ROUTING_CASES: list[tuple[str, AgentName]] = [
    ("Can you explain why fractions matter?", AgentName.QA_EXPLAINER),
    ("Give me a quiz on long division.", AgentName.ASSESSMENT_GENERATOR),
    ("I want to practice multiplication drills.", AgentName.COACH),
    ("Help me set a study goal for finals.", AgentName.MENTOR),
    ("Review my essay on climate change.", AgentName.REVIEWER),
    ("Summarize today's lesson into notes.", AgentName.NOTE_TAKER),
    ("Find research papers on neural networks.", AgentName.RESEARCH),
    ("Find reading list materials for fractions.", AgentName.CONTENT_CURATOR),
    ("Extract entities from this lesson upload.", AgentName.KG_BUILDER),
    ("Where am I in my learning path?", AgentName.PROGRESS_ANALYZER),
    ("Teach me a lesson on photosynthesis.", AgentName.TUTOR),
    ("Hello, I'm not sure what to do.", AgentName.TUTOR),
]


@pytest.mark.parametrize(("message", "expected"), ROUTING_CASES)
def test_declarative_routing(message: str, expected: AgentName) -> None:
    decision = ROUTER.route(OrchestratorInput(learner_id="learner-1", message=message))
    assert decision.selected_agents == [expected]


def test_explicit_agent_override() -> None:
    decision = ROUTER.route(
        OrchestratorInput(
            learner_id="learner-1",
            message="Explain gravity.",
            requested_agent=AgentName.TUTOR,
        )
    )
    assert decision.selected_agents == [AgentName.TUTOR]
    assert "explicit" in decision.rationale
