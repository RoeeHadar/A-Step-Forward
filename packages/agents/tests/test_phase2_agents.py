"""Unit tests for Phase-2 system agents."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.agent import AgentContext
from agents.base.prompts import load_prompt
from agents.system.assessment_generator import AssessmentGeneratorAgent, AssessmentGeneratorInput
from agents.system.curriculum_designer import CurriculumDesignerAgent, CurriculumDesignerInput
from agents.system.grader import GraderAgent, GraderInput
from agents.system.progress_analyzer import ProgressAnalyzerAgent, ProgressAnalyzerInput


@pytest.fixture
def ctx() -> AgentContext:
    return AgentContext(learner_id="learner-1", session_id="sess-1", turn_id="turn-1")


@pytest.mark.asyncio
async def test_curriculum_designer_returns_path(ctx: AgentContext) -> None:
    agent = CurriculumDesignerAgent()
    result = await agent(
        CurriculumDesignerInput(
            learner_id="learner-1",
            message="Build me a learning path for algebra.",
            subject="algebra",
        ),
        ctx,
    )
    assert result.output.reply
    assert result.output.path_id
    assert len(result.output.milestones) >= 2


@pytest.mark.asyncio
async def test_assessment_generator_returns_assessment(ctx: AgentContext) -> None:
    agent = AssessmentGeneratorAgent()
    result = await agent(
        AssessmentGeneratorInput(
            learner_id="learner-1",
            message="Quiz me on fractions.",
            format="quiz",
        ),
        ctx,
    )
    assert result.output.assessment_id
    assert result.output.item_count >= 1
    assert result.output.format == "quiz"


@pytest.mark.asyncio
async def test_grader_returns_scores(ctx: AgentContext) -> None:
    agent = GraderAgent()
    result = await agent(
        GraderInput(
            learner_id="learner-1",
            message="Grade my submission.",
            submission="The answer is 42 because...",
        ),
        ctx,
    )
    assert result.output.reply
    assert result.output.score is not None
    assert result.output.rubric_scores


@pytest.mark.asyncio
async def test_progress_analyzer_returns_gaps(ctx: AgentContext) -> None:
    agent = ProgressAnalyzerAgent()
    result = await agent(
        ProgressAnalyzerInput(learner_id="learner-1", message="Where am I in my progress?"),
        ctx,
    )
    assert result.output.reply
    assert result.output.gaps
    assert result.output.interventions


@pytest.mark.parametrize(
    "agent_name",
    ["curriculum_designer", "assessment_generator", "grader", "progress_analyzer"],
)
def test_phase2_prompts_load(agent_name: str) -> None:
    text = load_prompt(agent_name, "v1")
    assert "output schema" in text.lower()
