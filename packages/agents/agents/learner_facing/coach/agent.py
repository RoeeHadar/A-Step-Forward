"""Coach agent — drills, practice, and FSRS-scheduled reviews."""

from __future__ import annotations

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.memory_hydrator import HydratedMemory
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import CoachInput
from .memory_policy import MEMORY_POLICY
from .output import CoachOutput
from .tools import TOOLS


class CoachAgent(Agent[CoachInput, CoachOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.COACH]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("coach", self.prompt_version)

    def _build_system_prompt(self, ctx: AgentContext) -> str:
        hydrated: HydratedMemory | None = ctx.extra.get("hydrated_memory")
        if hydrated and hydrated.summary:
            return f"{self._system_prompt}\n\n{hydrated.summary}"
        return self._system_prompt

    def _format_user_message(self, inp: CoachInput) -> str:
        parts = [
            f"Learner message: {inp.message}",
            f"Practice mode: {inp.mode}",
        ]
        if inp.skill_id:
            parts.append(f"Skill focus: {inp.skill_id}")
        parts.append("Respond with JSON matching CoachOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: CoachInput) -> CoachOutput:
        preview = inp.message.strip()[:120]
        return CoachOutput(
            reply=(
                f"Great — let's practice. Based on \"{preview}\", try this: "
                "answer without looking at notes, then I'll give targeted feedback."
            ),
            drill_type="recall" if inp.mode == "review" else "mixed",
            difficulty="same",
            next_review_hint="Review again in 1 day if you miss more than one step.",
            rationale="offline stub: short practice loop without provider configured.",
            reps_completed=1,
        )

    async def run(self, inp: CoachInput, ctx: AgentContext) -> AgentResult[CoachOutput]:
        response = await complete_turn(
            self.llm,
            system=self._build_system_prompt(ctx),
            user_message=self._format_user_message(inp),
            trace_name=f"coach:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, CoachOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
