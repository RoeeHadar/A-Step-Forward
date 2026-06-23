"""Unified LLM client.

All agents go through this wrapper instead of instantiating provider SDKs
directly. It centralizes:

- model routing (primary + fallback)
- retries + timeouts
- prompt caching (Anthropic) when enabled
- structured output (via `instructor`)
- tracing (Langfuse)
- cost + token accounting against per-agent budgets

Sub-agent 03 implements the provider calls; Opus ships the surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMRequest:
    system: str
    messages: list[dict]
    temperature: float = 0.2
    max_output_tokens: int = 4_000
    tools: list[dict] = field(default_factory=list)
    structured_schema: dict | None = None
    cache_system: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    text: str
    tool_calls: list[dict] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    model_used: str | None = None
    latency_ms: int = 0
    raw: Any | None = None


class LLM:
    def __init__(self, *, model: str, fallback_model: str | None = None) -> None:
        self.model = model
        self.fallback_model = fallback_model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Phase-0 stub. Sub-agent 03 implements provider calls (Anthropic
        primary, OpenAI fallback) with retries + tracing + budget enforcement.
        Returns a deterministic placeholder so smoke tests stay offline.
        """
        text = "[stub LLM response — provider not configured]"
        return LLMResponse(text=text, model_used=self.model, raw=None)
