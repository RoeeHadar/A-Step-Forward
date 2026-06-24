"""Q&A Explainer agent — cited answers to ad-hoc questions."""

from __future__ import annotations

from schemas.agents import AgentName
from schemas.common import Citation

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.prompts import load_prompt
from .budget import BUDGET
from .input import QAExplainerInput
from .memory_policy import MEMORY_POLICY
from .output import QAExplainerOutput
from .tools import TOOLS


class QAExplainerAgent(Agent[QAExplainerInput, QAExplainerOutput]):
    prompt_version = "v1"
    tools = TOOLS
    memory_policy = MEMORY_POLICY
    budget = BUDGET

    def __init__(self) -> None:
        manifest = AGENT_REGISTRY[AgentName.QA_EXPLAINER]
        super().__init__(manifest=manifest)
        self._system_prompt = load_prompt("qa_explainer", self.prompt_version)

    def _build_system_prompt(self, ctx: AgentContext) -> str:
        """Build the system prompt with hydrated memory and adaptation note."""
        parts = [self._system_prompt]

        hydrated = ctx.extra.get("hydrated_memory")
        if hydrated and hydrated.summary:
            parts.append(hydrated.summary)

        adaptation = ctx.extra.get("adaptation")
        if adaptation:
            parts.append(f"## Adaptation note for this turn\n{adaptation}")

        return "\n\n".join(parts)

    def _format_user_message(self, inp: QAExplainerInput) -> str:
        parts = [f"Question: {inp.message}"]
        if inp.topic:
            parts.append(f"Topic hint: {inp.topic}")
        parts.append("Respond with JSON matching QAExplainerOutput.")
        return "\n".join(parts)

    def _stub_output(self, inp: QAExplainerInput) -> QAExplainerOutput:
        preview = inp.message.strip()[:160]
        return QAExplainerOutput(
            answer=(
                f"Here's a concise explanation for your question: \"{preview}\". "
                "In general, start from the core definition, then connect it to a concrete example."
            ),
            citations=[
                Citation(
                    source_kind="lesson",
                    source_id="lesson-stub-fractions",
                    quote="Fractions represent parts of a whole.",
                    score=0.75,
                )
            ],
            confidence=0.75,
            follow_up_questions=["Would you like a simpler analogy or a worked example?"],
        )

    async def run(self, inp: QAExplainerInput, ctx: AgentContext) -> AgentResult[QAExplainerOutput]:
        response = await complete_turn(
            self.llm,
            system=self._build_system_prompt(ctx),
            user_message=self._format_user_message(inp),
            trace_name=f"qa_explainer:{ctx.turn_id}",
            max_output_tokens=self.budget.max_output_tokens,
        )
        output = parse_output(response, QAExplainerOutput, self._stub_output(inp))
        return AgentResult(
            output=output,
            citations=output.citations,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
