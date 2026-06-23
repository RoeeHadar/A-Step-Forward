"""KG Builder agent — entity/relation extraction into the knowledge graph."""

from __future__ import annotations

import uuid

from schemas.agents import AgentName

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import KGBuilderInput
from .memory_policy import MEMORY_POLICY
from .output import KGBuilderOutput
from .tools import TOOLS


class KGBuilderAgent(Agent[KGBuilderInput, KGBuilderOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.KG_BUILDER]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("kg_builder", self.prompt_version)

    def _format_user_message(self, inp: KGBuilderInput) -> str:
        parts = [f"Extraction request: {inp.message}"]
        if inp.source_id:
            parts.append(f"Source ID: {inp.source_id}")
        parts.append("Respond with JSON matching KGBuilderOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: KGBuilderInput) -> KGBuilderOutput:
        _ = inp
        return KGBuilderOutput(
            reply="KG extraction queued (offline stub). Entities and relations would be written via MCP tools.",
            entities_extracted=8,
            relations_extracted=12,
            job_id=f"kg-job-stub-{uuid.uuid4().hex[:8]}",
            rationale="offline stub: no LLM provider configured.",
        )

    async def run(self, inp: KGBuilderInput, ctx: AgentContext) -> AgentResult[KGBuilderOutput]:
        response = await complete_turn(
            self.llm,
            system=self._system_prompt,
            user_message=self._format_user_message(inp),
            trace_name=f"kg_builder:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, KGBuilderOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
