"""Phase-2 smoke test for assessment, curriculum, grader, and progress routes."""

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
        ("Give me a quiz on long division.", AgentName.ASSESSMENT_GENERATOR, "quiz"),
        ("Build me a curriculum for introductory physics.", AgentName.CURRICULUM_DESIGNER, "path"),
        ("Grade my essay with the rubric.", AgentName.GRADER, "rubric"),
        ("Where am I in my progress?", AgentName.PROGRESS_ANALYZER, "progress"),
    ]

    for message, expected_agent, keyword in cases:
        chunks = await runner.handle(ChatRequest(learner_id="learner-1", message=message))
        token = next(c for c in chunks if c.kind == "token")
        assert token.agent == expected_agent, (message, token.agent)
        assert token.text and keyword in token.text.lower(), token.text[:80]
        print(f"{expected_agent.value} route ok")


if __name__ == "__main__":
    asyncio.run(main())
