"""Research agent citation contract tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))
sys.path.insert(0, str(ROOT / "services" / "orchestrator"))

from agents.base.agent import AgentContext
from agents.system.research import ResearchAgent, ResearchInput
from schemas.agents import AgentName, ChatChunk
from orchestrator.invoke import _research_chunks


@pytest.fixture
def ctx() -> AgentContext:
    return AgentContext(learner_id="learner-1", session_id="sess-1", turn_id="turn-1")


@pytest.mark.asyncio
async def test_research_stub_includes_citations(ctx: AgentContext) -> None:
    agent = ResearchAgent()
    result = await agent(
        ResearchInput(learner_id="learner-1", message="Literature review on transformers."),
        ctx,
    )
    assert len(result.output.citations) >= 1
    c0 = result.output.citations[0]
    assert c0.source_id
    assert c0.quote


def test_research_chunks_emit_citation_before_token(ctx: AgentContext) -> None:
    agent = ResearchAgent()
    import asyncio

    result = asyncio.run(
        agent(
            ResearchInput(learner_id="learner-1", message="Cite papers on RL."),
            ctx,
        )
    )
    chunks = _research_chunks(result)
    kinds = [c.kind for c in chunks]
    assert kinds[0] == "citation"
    assert chunks[-1].kind == "token"
    assert chunks[-1].agent == AgentName.RESEARCH
    assert all(c.agent == AgentName.RESEARCH for c in chunks)

