"""Content Curator agent — find and rank learning resources."""

from __future__ import annotations

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import ContentCuratorInput
from .memory_policy import MEMORY_POLICY
from .output import ContentCuratorOutput, CuratedResource
from .tools import TOOLS


class ContentCuratorAgent(Agent[ContentCuratorInput, ContentCuratorOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.CONTENT_CURATOR]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("content_curator", self.prompt_version)

    def _format_user_message(self, inp: ContentCuratorInput) -> str:
        parts = [f"Curation request: {inp.message}"]
        if inp.concept_ids:
            parts.append(f"Concept IDs: {', '.join(inp.concept_ids)}")
        parts.append("Respond with JSON matching ContentCuratorOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: ContentCuratorInput) -> ContentCuratorOutput:
        topic = inp.message.strip()[:100]
        concepts = inp.concept_ids or ["concept-stub-general"]
        return ContentCuratorOutput(
            reply=(
                f"Curated starter resources (offline stub) for: {topic}. "
                "Ranked for clarity and age-appropriate coverage."
            ),
            resources=[
                CuratedResource(
                    resource_id="resource-stub-1",
                    title="Introductory overview (stub)",
                    url="https://example.edu/stub-overview",
                    quality_score=0.88,
                    concept_ids=concepts[:3],
                )
            ],
            rationale="offline stub: no LLM provider configured.",
        )

    async def run(
        self, inp: ContentCuratorInput, ctx: AgentContext
    ) -> AgentResult[ContentCuratorOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"content_curator:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, ContentCuratorOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
