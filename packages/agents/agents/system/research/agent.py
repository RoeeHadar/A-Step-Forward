"""Research agent — deep cited research via web, RAG, and KG."""

from __future__ import annotations

from schemas.agents import AgentName
from schemas.common import Citation

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import ResearchInput
from .memory_policy import MEMORY_POLICY
from .output import ResearchOutput
from .tools import TOOLS


class ResearchAgent(Agent[ResearchInput, ResearchOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.RESEARCH]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("research", self.prompt_version)

    def _format_user_message(self, inp: ResearchInput) -> str:
        return "\n".join(
            [
                f"Research request: {inp.message}",
                f"Depth: {inp.depth}",
                "Respond with JSON matching ResearchOutput.",
            ]
        )

    def _stub_output(self, inp: ResearchInput) -> ResearchOutput:
        topic = inp.message.strip()[:120]
        return ResearchOutput(
            report=(
                f"Research summary (offline stub) for: {topic}. "
                "Key themes would be synthesized from memory search, KG chunks, "
                "related concepts, and vetted web sources."
            ),
            citations=[
                Citation(
                    source_kind="resource",
                    source_id="stub-research-source-1",
                    quote="Representative excerpt supporting the synthesis.",
                    score=0.82,
                )
            ],
            sources_consulted=3,
            confidence=0.75,
            rationale="offline stub: no LLM provider configured.",
        )

    async def run(self, inp: ResearchInput, ctx: AgentContext) -> AgentResult[ResearchOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"research:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, ResearchOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            citations=output.citations,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
