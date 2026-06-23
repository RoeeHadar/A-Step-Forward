"""Phase-3 smoke test for research, content curator, and kg builder routes."""

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

    cases: list[tuple[str, AgentName, str]] = [
        ("Find research papers on neural networks.", AgentName.RESEARCH, "research"),
        ("Find reading list materials for fractions.", AgentName.CONTENT_CURATOR, "resource"),
        ("Extract entities from this lesson upload.", AgentName.KG_BUILDER, "extraction"),
    ]

    for message, expected_agent, keyword in cases:
        chunks = await runner.handle(ChatRequest(learner_id="learner-1", message=message))
        if expected_agent == AgentName.RESEARCH:
            citation = next(c for c in chunks if c.kind == "citation")
            assert citation.agent == AgentName.RESEARCH
            token = next(c for c in chunks if c.kind == "token")
        else:
            token = next(c for c in chunks if c.kind == "token")
        assert token.agent == expected_agent, (message, token.agent)
        assert token.text and keyword in token.text.lower(), token.text[:120]
        print(f"{expected_agent.value} route ok")


if __name__ == "__main__":
    asyncio.run(main())
