"""Phase-1 smoke test for orchestrator + Tutor, Q&A Explainer, Coach."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))
sys.path.insert(0, str(ROOT / "services" / "orchestrator"))

from schemas.agents import AgentName, ChatRequest

from orchestrator.runner import OrchestratorRunner


async def main() -> None:
    runner = OrchestratorRunner()

    chunks = await runner.handle(
        ChatRequest(learner_id="learner-1", message="Can you explain why fractions matter?")
    )
    assert chunks[0].agent == AgentName.QA_EXPLAINER
    assert any(c.kind == "citation" for c in chunks)
    assert any(c.kind == "token" and c.text for c in chunks)
    print("qa route ok:", chunks[0].agent)

    chunks = await runner.handle(
        ChatRequest(learner_id="learner-1", message="I want to practice multiplication drills.")
    )
    assert chunks[0].agent == AgentName.COACH or any(c.agent == AgentName.COACH for c in chunks)
    token = next(c for c in chunks if c.kind == "token")
    assert token.text and "practice" in token.text.lower()
    print("coach route ok:", token.agent)

    chunks = await runner.handle(
        ChatRequest(
            learner_id="learner-1",
            message="Tutor me through this lesson.",
            requested_agent=AgentName.TUTOR,
        )
    )
    token = next(c for c in chunks if c.kind == "token")
    assert token.agent == AgentName.TUTOR
    assert token.text and ("explore" in token.text.lower() or "example" in token.text.lower())
    print("tutor route ok:", token.agent)


if __name__ == "__main__":
    asyncio.run(main())
