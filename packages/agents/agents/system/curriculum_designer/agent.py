"""Curriculum Designer agent — personalized learning paths."""

from __future__ import annotations

from uuid import uuid4

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import CurriculumDesignerInput
from .memory_policy import MEMORY_POLICY
from .output import CurriculumDesignerOutput
from .tools import TOOLS


class CurriculumDesignerAgent(Agent[CurriculumDesignerInput, CurriculumDesignerOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.CURRICULUM_DESIGNER]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("curriculum_designer", self.prompt_version)

    def _format_user_message(self, inp: CurriculumDesignerInput) -> str:
        parts = [f"Learner request: {inp.message}"]
        if inp.goal:
            parts.append(f"Goal: {inp.goal}")
        if inp.subject:
            parts.append(f"Subject: {inp.subject}")
        parts.append("Respond with JSON matching CurriculumDesignerOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: CurriculumDesignerInput) -> CurriculumDesignerOutput:
        subject = inp.subject or "your focus area"
        return CurriculumDesignerOutput(
            reply=(
                f"I drafted a learning path for {subject}. We'll start with foundations, "
                "then build to applied practice over a few weeks."
            ),
            path_id=f"path-{uuid4()}",
            milestones=[
                "Core concepts and vocabulary",
                "Guided practice with feedback",
                "Applied project or assessment",
            ],
            estimated_weeks=4,
            rationale="offline stub: scaffolded path without provider configured.",
        )

    async def run(
        self, inp: CurriculumDesignerInput, ctx: AgentContext
    ) -> AgentResult[CurriculumDesignerOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"curriculum_designer:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, CurriculumDesignerOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
