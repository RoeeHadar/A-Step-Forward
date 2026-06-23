"""Base Agent class.

All runtime agents extend this class. The base wires the per-turn lifecycle:

1. `pre()` — safety, memory hydration, context compaction.
2. `run()` — agent-specific work (overridden in subclasses).
3. `post()` — safety output filter, memory writes, audit, telemetry.

Sub-agent 03 fills in the real LangGraph state machine in `run()` for each
agent; the base here gives a stable structure they can rely on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from schemas.agents import AgentManifest, AgentName

from .llm import LLM
from .safety import SafetyModeration

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)


@dataclass
class AgentContext:
    """Per-turn context (filled in by the orchestrator)."""

    learner_id: str
    session_id: str
    turn_id: str
    locale: str = "en"
    child_mode: bool = False
    pinned_memory_ids: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult(Generic[O]):
    output: O
    citations: list[Any] = field(default_factory=list)
    tool_trace: list[Any] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0


class Agent(Generic[I, O]):
    """Base for all runtime agents."""

    name: AgentName
    manifest: AgentManifest
    llm: LLM
    safety: SafetyModeration

    def __init__(self, *, manifest: AgentManifest, llm: LLM | None = None, safety: SafetyModeration | None = None) -> None:
        self.manifest = manifest
        self.name = manifest.name
        self.llm = llm or LLM(model=manifest.primary_model, fallback_model=manifest.fallback_model)
        self.safety = safety or SafetyModeration()

    # ----- lifecycle (do NOT override unless you know what you're doing) -----

    async def __call__(self, inp: I, ctx: AgentContext) -> AgentResult[O]:
        await self.pre(inp, ctx)
        result = await self.run(inp, ctx)
        await self.post(inp, result, ctx)
        return result

    async def pre(self, inp: I, ctx: AgentContext) -> None:
        await self.safety.pre(text=str(inp), agent=self.name, child_mode=ctx.child_mode)

    async def post(self, inp: I, result: AgentResult[O], ctx: AgentContext) -> None:
        await self.safety.post(text=str(result.output), agent=self.name, child_mode=ctx.child_mode)

    # ----- override in subclasses -----

    async def run(self, inp: I, ctx: AgentContext) -> AgentResult[O]:  # pragma: no cover
        raise NotImplementedError("Agent.run must be implemented by subclasses.")
