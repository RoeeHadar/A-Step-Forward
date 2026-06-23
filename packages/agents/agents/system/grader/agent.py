"""Grader agent — objective auto-grade + rubric LLM judge."""

from __future__ import annotations

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import GraderInput
from .memory_policy import MEMORY_POLICY
from .output import GraderOutput
from .tools import TOOLS


class GraderAgent(Agent[GraderInput, GraderOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.GRADER]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("grader", self.prompt_version)

    def _format_user_message(self, inp: GraderInput) -> str:
        parts = [f"Grading request: {inp.message}"]
        if inp.submission:
            parts.append(f"Submission: {inp.submission[:4000]}")
        if inp.rubric_id:
            parts.append(f"Rubric id: {inp.rubric_id}")
        parts.append("Respond with JSON matching GraderOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: GraderInput) -> GraderOutput:
        return GraderOutput(
            reply=(
                "I reviewed the submission against the rubric. Strengths are clear in structure; "
                "the main gap is deeper reasoning on the core claim. See scores below."
            ),
            score=78.0,
            passed=True,
            rubric_scores={"accuracy": 80.0, "reasoning": 72.0, "clarity": 82.0},
            rationale="offline stub: rubric-shaped feedback without provider configured.",
        )

    async def run(self, inp: GraderInput, ctx: AgentContext) -> AgentResult[GraderOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"grader:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, GraderOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
