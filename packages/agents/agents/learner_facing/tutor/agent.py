"""Tutor agent — adaptive Socratic lessons."""

from __future__ import annotations

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import TutorInput
from .memory_policy import MEMORY_POLICY
from .output import TutorOutput
from .tools import TOOLS


class TutorAgent(Agent[TutorInput, TutorOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.TUTOR]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("tutor", self.prompt_version)

    def _format_user_message(self, inp: TutorInput) -> str:
        parts = [f"Learner message: {inp.message}"]
        if inp.lesson_id:
            parts.append(f"Active lesson_id: {inp.lesson_id}")
        parts.append("Respond with JSON matching TutorOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: TutorInput) -> TutorOutput:
        preview = inp.message.strip()[:120]
        return TutorOutput(
            reply=(
                f"Let's explore that together. You asked about: \"{preview}\". "
                "Would you like a worked example first, or should I ask you a guiding question?"
            ),
            next_step="continue",
            rationale="offline stub: Socratic opening without provider configured.",
        )

    async def run(self, inp: TutorInput, ctx: AgentContext) -> AgentResult[TutorOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"tutor:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, TutorOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
