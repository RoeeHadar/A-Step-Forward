"""Citation accuracy checks for Q&A Explainer (offline stub mode)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.agent import AgentContext
from agents.learner_facing.qa_explainer import QAExplainerAgent, QAExplainerInput


@pytest.mark.asyncio
async def test_answer_includes_structured_citations() -> None:
    agent = QAExplainerAgent()
    ctx = AgentContext(learner_id="learner-1", session_id="s", turn_id="t")
    result = await agent(
        QAExplainerInput(learner_id="learner-1", message="What is a fraction?"),
        ctx,
    )
    assert result.output.citations
    citation = result.output.citations[0]
    assert citation.source_kind
    assert citation.source_id
    assert citation.score is not None
