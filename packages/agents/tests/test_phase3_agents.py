"""Unit tests for Phase-3 system agents."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents import AGENT_FACTORIES, IMPLEMENTED_AGENTS, PHASE3_AGENTS
from agents.base.agent import AgentContext
from agents.base.prompts import load_prompt
from agents.system.content_curator import ContentCuratorAgent, ContentCuratorInput
from agents.system.kg_builder import KGBuilderAgent, KGBuilderInput
from agents.system.research import ResearchAgent, ResearchInput
from schemas.agents import AgentName


@pytest.fixture
def ctx() -> AgentContext:
    return AgentContext(learner_id="learner-1", session_id="sess-1", turn_id="turn-1")


def test_phase3_registered() -> None:
    assert PHASE3_AGENTS <= IMPLEMENTED_AGENTS
    for name in PHASE3_AGENTS:
        assert name in AGENT_FACTORIES


@pytest.mark.asyncio
async def test_research_returns_citations(ctx: AgentContext) -> None:
    agent = ResearchAgent()
    result = await agent(
        ResearchInput(learner_id="learner-1", message="Find sources on neural networks."),
        ctx,
    )
    assert result.output.report
    assert result.output.citations
    assert result.citations == result.output.citations


@pytest.mark.asyncio
async def test_content_curator_returns_resources(ctx: AgentContext) -> None:
    agent = ContentCuratorAgent()
    result = await agent(
        ContentCuratorInput(
            learner_id="learner-1",
            message="Curate resources for photosynthesis.",
        ),
        ctx,
    )
    assert result.output.reply
    assert result.output.resources
    assert result.output.resources[0].title


@pytest.mark.asyncio
async def test_kg_builder_returns_job(ctx: AgentContext) -> None:
    agent = KGBuilderAgent()
    result = await agent(
        KGBuilderInput(learner_id="learner-1", message="Extract entities from chapter 3."),
        ctx,
    )
    assert result.output.reply
    assert result.output.entities_extracted > 0
    assert result.output.relations_extracted > 0
    assert result.output.job_id


@pytest.mark.parametrize("agent_name", ["research", "content_curator", "kg_builder"])
def test_phase3_prompts_load(agent_name: str) -> None:
    text = load_prompt(agent_name, "v1")
    assert "output schema" in text.lower()


def test_research_tools_match_registry() -> None:
    from agents import AGENT_REGISTRY

    manifest = AGENT_REGISTRY[AgentName.RESEARCH]
    tool_names = {t.name for t in manifest.tools}
    assert tool_names == {
        "memory.search",
        "kg.retrieve_chunks",
        "kg.related_concepts",
        "web.search",
    }
