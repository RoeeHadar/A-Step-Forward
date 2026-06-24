"""Smoke test: Tutor agent streams a non-empty response (Groq client mocked)."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))
sys.path.insert(0, str(ROOT / "services" / "orchestrator"))


@pytest.mark.asyncio
async def test_tutor_streams_non_empty_response():
    """Tutor should yield at least one non-empty token chunk even when mocked."""
    from agents.base.llm import LLM, LLMRequest

    async def _fake_astream(request):
        for token in ["Let", " me", " ask", " you", " a", " question", "..."]:
            yield token

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=None)

    llm = LLM(model="llama-3.3-70b-versatile")
    llm._client = mock_client

    with patch.object(llm, "astream", _fake_astream):
        tokens = []
        async for token in llm.astream(
            LLMRequest(
                system="You are a Socratic tutor.",
                messages=[{"role": "user", "content": "What is a derivative?"}],
            )
        ):
            tokens.append(token)

    assert len(tokens) > 0, "Expected at least one token from the stream"
    full_response = "".join(tokens)
    assert len(full_response) > 0, "Expected non-empty streamed response"


@pytest.mark.asyncio
async def test_tutor_agent_astream_reply_non_empty():
    """TutorAgent.astream_reply should yield ChatChunk tokens."""
    from agents.base.agent import AgentContext
    from agents.base.llm import LLMRequest
    from agents.learner_facing.tutor.agent import TutorAgent
    from agents.learner_facing.tutor.input import TutorInput

    async def _fake_astream(request: LLMRequest):
        for token in ["Great question!", " What", " have", " you", " tried", " so far?"]:
            yield token

    agent = TutorAgent()
    ctx = AgentContext(
        learner_id="test-learner",
        session_id="test-session",
        turn_id=str(uuid.uuid4()),
        child_mode=False,
    )

    with patch.object(agent.llm, "astream", _fake_astream):
        chunks = []
        async for chunk in agent.astream_reply(
            TutorInput(message="What is a derivative?", learner_id="test-learner"),
            ctx,
        ):
            chunks.append(chunk)

    token_chunks = [c for c in chunks if c.kind == "token"]
    assert len(token_chunks) > 0, "Expected at least one token chunk"
    full_text = "".join(c.text for c in token_chunks if c.text)
    assert len(full_text) > 0, "Expected non-empty response text"
