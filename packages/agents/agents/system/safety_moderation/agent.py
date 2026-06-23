"""Safety / Moderation runtime agent."""

from __future__ import annotations

from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.llm import LLM, LLMRequest


class SafetyModerationInput(BaseModel):
    text: str
    phase: Literal["pre", "post"] = "pre"
    target_agent: AgentName = AgentName.TUTOR
    child_mode: bool = False


class SafetyModerationOutput(BaseModel):
    categories: list[str] = Field(default_factory=lambda: ["safe"])
    severity: Literal["low", "medium", "high"] = "low"
    rationale: str = ""
    redirect: str | None = None


def _load_system_prompt() -> str:
    repo_root = Path(__file__).resolve().parents[5]
    prompt_path = repo_root / "prompts" / "safety_moderation" / "v1.md"
    if prompt_path.is_file():
        return prompt_path.read_text(encoding="utf-8")
    return "You are the Safety / Moderation classifier. Return JSON only."


class SafetyModerationAgent(Agent[SafetyModerationInput, SafetyModerationOutput]):
    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.SAFETY_MODERATION]
        super().__init__(
            manifest=manifest,
            llm=LLM(model=manifest.primary_model, fallback_model=manifest.fallback_model),
        )

    async def pre(self, inp: SafetyModerationInput, ctx: AgentContext) -> None:
        return None

    async def post(
        self,
        inp: SafetyModerationInput,
        result: AgentResult[SafetyModerationOutput],
        ctx: AgentContext,
    ) -> None:
        return None

    async def run(
        self,
        inp: SafetyModerationInput,
        ctx: AgentContext,
    ) -> AgentResult[SafetyModerationOutput]:
        user_content = (
            f"Phase: {inp.phase}\n"
            f"Child mode: {inp.child_mode}\n"
            f"Target agent: {inp.target_agent.value}\n"
            f"Text:\n{inp.text}"
        )
        response = await self.llm.complete(
            LLMRequest(
                system=_load_system_prompt(),
                messages=[{"role": "user", "content": user_content}],
                temperature=0.0,
                max_output_tokens=512,
                structured_schema=SafetyModerationOutput.model_json_schema(),
                metadata={"trace_name": f"safety_moderation:{ctx.turn_id or uuid4()}"},
            )
        )
        out = self._parse_output(response.text, inp)
        return AgentResult(output=out)

    def _parse_output(self, raw: str, inp: SafetyModerationInput) -> SafetyModerationOutput:
        import json

        try:
            data = json.loads(raw)
            return SafetyModerationOutput.model_validate(data)
        except Exception:
            return SafetyModerationOutput(
                categories=["safe"],
                severity="low",
                rationale="classifier unavailable; rules-only path",
            )


def create_safety_moderation_agent() -> SafetyModerationAgent:
    return SafetyModerationAgent()
