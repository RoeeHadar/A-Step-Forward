"""Unit tests for Phase-1 learner-facing agents."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.agent import AgentContext
from agents.base.prompts import load_prompt
from agents.learner_facing.coach import CoachAgent, CoachInput
from agents.learner_facing.qa_explainer import QAExplainerAgent, QAExplainerInput
from agents.learner_facing.tutor import TutorAgent, TutorInput


@pytest.fixture
def ctx() -> AgentContext:
    return AgentContext(learner_id="learner-1", session_id="sess-1", turn_id="turn-1")


@pytest.mark.asyncio
async def test_tutor_returns_socratic_reply(ctx: AgentContext) -> None:
    agent = TutorAgent()
    result = await agent(TutorInput(learner_id="learner-1", message="Explain fractions."), ctx)
    assert result.output.reply
    assert result.output.next_step == "continue"
    assert "Let's explore" in result.output.reply or "worked example" in result.output.reply


@pytest.mark.asyncio
async def test_qa_explainer_returns_cited_answer(ctx: AgentContext) -> None:
    agent = QAExplainerAgent()
    result = await agent(
        QAExplainerInput(learner_id="learner-1", message="Why is the sky blue?"),
        ctx,
    )
    assert result.output.answer
    assert len(result.output.citations) >= 1
    assert result.citations == result.output.citations


@pytest.mark.asyncio
async def test_coach_returns_practice_reply(ctx: AgentContext) -> None:
    agent = CoachAgent()
    result = await agent(
        CoachInput(learner_id="learner-1", message="Drill me on multiplication tables."),
        ctx,
    )
    assert result.output.reply
    assert result.output.drill_type in {"recall", "application", "mixed"}
    assert result.output.reps_completed >= 1


@pytest.mark.parametrize(
    ("agent_name", "version"),
    [
        ("tutor", "v1"),
        ("qa_explainer", "v1"),
        ("coach", "v1"),
    ],
)
def test_phase1_prompts_load(agent_name: str, version: str) -> None:
    text = load_prompt(agent_name, version)
    assert "output schema" in text.lower()
