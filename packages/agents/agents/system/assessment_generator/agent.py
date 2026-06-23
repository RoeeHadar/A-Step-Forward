"""Assessment Generator agent — quizzes, exercises, and projects."""

from __future__ import annotations

from uuid import uuid4

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import AssessmentGeneratorInput
from .memory_policy import MEMORY_POLICY
from .output import AssessmentGeneratorOutput
from .tools import TOOLS


class AssessmentGeneratorAgent(Agent[AssessmentGeneratorInput, AssessmentGeneratorOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.ASSESSMENT_GENERATOR]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("assessment_generator", self.prompt_version)

    def _format_user_message(self, inp: AssessmentGeneratorInput) -> str:
        parts = [
            f"Learner request: {inp.message}",
            f"Desired format: {inp.format}",
        ]
        if inp.objectives:
            parts.append("Objectives: " + "; ".join(inp.objectives))
        parts.append("Respond with JSON matching AssessmentGeneratorOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: AssessmentGeneratorInput) -> AssessmentGeneratorOutput:
        count = 10 if inp.format == "quiz" else 3
        return AssessmentGeneratorOutput(
            reply=(
                f"I prepared a {inp.format} with {count} items aligned to your request. "
                "Ready when you are — we'll adjust difficulty from your first responses."
            ),
            assessment_id=f"assessment-{uuid4()}",
            item_count=count,
            format=inp.format,
            rationale="offline stub: assessment scaffold without provider configured.",
        )

    async def run(
        self, inp: AssessmentGeneratorInput, ctx: AgentContext
    ) -> AgentResult[AssessmentGeneratorOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"assessment_generator:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, AssessmentGeneratorOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
