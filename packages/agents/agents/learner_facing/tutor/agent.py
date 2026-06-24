"""Tutor agent — adaptive Socratic lessons."""

from __future__ import annotations

from collections.abc import AsyncIterator

from schemas.agents import AgentName, ChatChunk

from ...__init__ import AGENT_REGISTRY
from ...base.agent import Agent, AgentContext, AgentResult
from ...base.agent_helpers import complete_turn, parse_output
from ...base.llm import STUB_PREFIX, LLMRequest
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

    def _format_user_message(self, inp: TutorInput) -> str:
        parts = [f"Learner message: {inp.message}"]
        if inp.lesson_id:
            parts.append(f"Active lesson_id: {inp.lesson_id}")
        parts.append("Respond with JSON matching TutorOutput.")
        return "\n".join(parts)

    def _format_streaming_message(self, inp: TutorInput) -> str:
        """Conversational variant used for token streaming."""
        parts = [f"Learner message: {inp.message}"]
        if inp.lesson_id:
            parts.append(f"Active lesson_id: {inp.lesson_id}")
        parts.append(
            "Reply directly as conversational tutoring text. Do NOT wrap the "
            "reply in JSON, code fences, or backticks."
        )
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
            system=self._build_system_prompt(ctx),
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

    async def astream_reply(
        self, inp: TutorInput, ctx: AgentContext
    ) -> AsyncIterator[ChatChunk]:
        """Stream the Tutor's reply as per-token SSE chunks."""
        await self.pre(inp, ctx)

        request = LLMRequest(
            system=self._build_system_prompt(ctx),
            messages=[{"role": "user", "content": self._format_streaming_message(inp)}],
            max_output_tokens=self.budget.max_output_tokens,
            metadata={"trace_name": f"tutor:{ctx.turn_id}"},
            cache_system=True,
        )

        accumulated: list[str] = []
        async for token in self.llm.astream(request):
            if not token:
                continue
            if not accumulated and token.startswith(STUB_PREFIX):
                fallback = self._stub_output(inp).reply
                accumulated.append(fallback)
                yield ChatChunk(kind="token", agent=self.name, text=fallback)
                break
            accumulated.append(token)
            yield ChatChunk(kind="token", agent=self.name, text=token)

        if not accumulated:
            fallback = self._stub_output(inp).reply
            accumulated.append(fallback)
            yield ChatChunk(kind="token", agent=self.name, text=fallback)

        await self.safety.post(
            text="".join(accumulated), agent=self.name, child_mode=ctx.child_mode
        )
