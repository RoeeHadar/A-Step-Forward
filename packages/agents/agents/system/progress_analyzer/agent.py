"""Progress Analyzer agent — gaps, at-risk signals, interventions."""

from __future__ import annotations

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import ProgressAnalyzerInput
from .memory_policy import MEMORY_POLICY
from .output import ProgressAnalyzerOutput
from .tools import TOOLS


class ProgressAnalyzerAgent(Agent[ProgressAnalyzerInput, ProgressAnalyzerOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.PROGRESS_ANALYZER]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("progress_analyzer", self.prompt_version)

    def _format_user_message(self, inp: ProgressAnalyzerInput) -> str:
        return "\n".join(
            [
                f"Analysis request: {inp.message}",
                "Respond with JSON matching ProgressAnalyzerOutput.",
            ]
        )

    def _stub_output(self, inp: ProgressAnalyzerInput) -> ProgressAnalyzerOutput:
        _ = inp
        return ProgressAnalyzerOutput(
            reply=(
                "You're making steady progress overall. The biggest gap right now is applying "
                "concepts under time pressure; targeted drills should help."
            ),
            gaps=["Application under time pressure", "Connecting prerequisites to new topics"],
            at_risk=False,
            interventions=[
                "Schedule 3 short Coach drills this week",
                "Review prerequisite concepts before the next lesson",
            ],
            rationale="offline stub: progress snapshot without provider configured.",
        )

    async def run(
        self, inp: ProgressAnalyzerInput, ctx: AgentContext
    ) -> AgentResult[ProgressAnalyzerOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"progress_analyzer:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, ProgressAnalyzerOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
