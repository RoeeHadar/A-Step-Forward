"""Unified LLM client.

All agents go through this wrapper instead of instantiating provider SDKs
directly. It centralizes:

- model routing (primary + cheap fallback)
- retries + timeouts (3 attempts, exponential backoff on 429/5xx)
- token + latency accounting
- offline stub when no provider is configured (keeps the demo usable)
- streaming via :meth:`LLM.astream` for SSE callers

The primary provider is **Groq Cloud** (Llama 3.x via an OpenAI-compatible API).
Groq's free tier requires no credit card; see
``docs/adr/0004-llm-provider-groq.md`` and ``BLOCKED.md`` §5c for setup.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from .llm_settings import LLMSettings, get_llm_settings

logger = logging.getLogger(__name__)

STUB_PREFIX = "[stub LLM response"


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


def _build_openai_messages(request: LLMRequest) -> list[dict[str, Any]]:
    """Convert an :class:`LLMRequest` into OpenAI-style chat messages.

    Groq exposes an OpenAI-compatible API at ``/openai/v1`` so the same
    payload shape works there. The system prompt is prepended first; user /
    assistant turns are passed through unchanged.
    """
    messages: list[dict[str, Any]] = []
    if request.system:
        messages.append({"role": "system", "content": request.system})
    for msg in request.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        messages.append({"role": role, "content": content})
    return messages


def _first_question(messages: list[dict]) -> str:
    """Pull the latest user message verbatim for the offline stub."""
    for msg in reversed(messages):
        if msg.get("role") == "user" and msg.get("content"):
            return str(msg["content"]).strip()
    return ""


def _stub_response(request: LLMRequest, model: str, agent_label: str) -> LLMResponse:
    """Deterministic, helpful response used when ``GROQ_API_KEY`` is missing.

    Includes the user's question + agent name so the deployed demo still looks
    reasonable while operators add the (free) Groq key. Prefixed with
    ``STUB_PREFIX`` so callers like ``agent_helpers.is_stub_llm_response`` can
    detect and fall back to their own deterministic outputs.
    """
    question = _first_question(request.messages) or "your question"
    short = question[:160]
    text = (
        f"{STUB_PREFIX} | {agent_label}] I'd love to dig into "
        f"\"{short}\". To enable real AI responses, set GROQ_API_KEY in the "
        "deployment env vars (free at console.groq.com — no credit card needed)."
    )
    return LLMResponse(text=text, model_used=model, latency_ms=0)


def _is_retriable_status(status: int) -> bool:
    return status == 429 or 500 <= status < 600


def _is_retriable_exception(exc: BaseException) -> bool:
    """Match transient Groq SDK errors (rate limits, 5xx, network blips)."""
    try:
        from groq import (
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
            RateLimitError,
        )
    except Exception:  # pragma: no cover - SDK always present in deps
        return False

    if isinstance(exc, RateLimitError | APITimeoutError | APIConnectionError | InternalServerError):
        return True

    status = getattr(exc, "status_code", None)
    if isinstance(status, int) and _is_retriable_status(status):
        return True
    return False


class LLM:
    """Thin async wrapper around the Groq SDK with retry + streaming support.

    Parameters
    ----------
    model:
        Primary model id (e.g. ``llama-3.3-70b-versatile``).
    fallback_model:
        Cheap model used if the primary repeatedly fails. Currently both share
        the same retry budget; full failover lands in Phase-2 work.
    settings:
        Optional :class:`LLMSettings` override (tests inject mocks here).
    client:
        Optional pre-built ``groq.AsyncGroq`` client (tests inject mocks here).
    """

    def __init__(
        self,
        *,
        model: str,
        fallback_model: str | None = None,
        settings: LLMSettings | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.fallback_model = fallback_model
        self._settings = settings or get_llm_settings()
        self._client = client
        self._client_lock = asyncio.Lock()

    # ----- public API -----

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Non-streaming chat completion. Returns a populated :class:`LLMResponse`.

        Falls back to a deterministic stub (prefixed with ``STUB_PREFIX``) when
        no Groq API key is configured so offline tests + the deployed demo
        keep working.
        """
        agent_label = str(request.metadata.get("trace_name") or self.model)
        if not self._settings.resolved_api_key:
            return _stub_response(request, self.model, agent_label)

        client = await self._get_client()
        params: dict[str, Any] = {
            "model": self.model,
            "messages": _build_openai_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
        }
        started = time.perf_counter()
        completion = await self._call_with_retry(
            lambda: client.chat.completions.create(**params),
            label=f"groq.complete:{agent_label}",
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        return self._completion_to_response(completion, latency_ms=latency_ms)

    async def astream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Yield token-sized text chunks for SSE streaming consumers.

        Yields the deterministic stub as a single chunk when no API key is set
        so the orchestrator's streaming path always produces output.
        """
        agent_label = str(request.metadata.get("trace_name") or self.model)
        if not self._settings.resolved_api_key:
            yield _stub_response(request, self.model, agent_label).text
            return

        client = await self._get_client()
        params: dict[str, Any] = {
            "model": self.model,
            "messages": _build_openai_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
            "stream": True,
        }
        stream = await self._call_with_retry(
            lambda: client.chat.completions.create(**params),
            label=f"groq.astream:{agent_label}",
        )
        async for chunk in stream:
            for choice in getattr(chunk, "choices", []) or []:
                delta = getattr(choice, "delta", None)
                text = getattr(delta, "content", None) if delta is not None else None
                if text:
                    yield text

    # ----- internals -----

    async def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        async with self._client_lock:
            if self._client is None:
                from groq import AsyncGroq

                self._client = AsyncGroq(
                    api_key=self._settings.resolved_api_key,
                    base_url=self._settings.resolved_base_url,
                    timeout=self._settings.llm_timeout_seconds,
                    max_retries=0,  # we own retries below
                )
        return self._client

    async def _call_with_retry(self, fn: Any, *, label: str) -> Any:
        """Run ``fn()`` up to ``llm_max_retries`` times with exponential backoff.

        Retries on Groq 429 / 5xx / connection-timeout exceptions. Anything
        else (e.g. 400 bad request, auth errors) propagates immediately so
        callers see real bugs.
        """
        attempts = max(1, self._settings.llm_max_retries)
        base = self._settings.llm_retry_base_delay
        last_exc: BaseException | None = None
        for attempt in range(1, attempts + 1):
            try:
                return await fn()
            except Exception as exc:
                last_exc = exc
                if not _is_retriable_exception(exc) or attempt >= attempts:
                    raise
                delay = base * (2 ** (attempt - 1)) + random.uniform(0, base / 2)
                logger.warning(
                    "llm.retry",
                    extra={
                        "label": label,
                        "attempt": attempt,
                        "max_attempts": attempts,
                        "delay_s": round(delay, 3),
                        "error": exc.__class__.__name__,
                    },
                )
                await asyncio.sleep(delay)
        assert last_exc is not None  # pragma: no cover — defensive
        raise last_exc

    def _completion_to_response(self, completion: Any, *, latency_ms: int) -> LLMResponse:
        text = ""
        choices = getattr(completion, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            text = getattr(message, "content", None) or ""

        usage = getattr(completion, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        model_used = getattr(completion, "model", None) or self.model

        return LLMResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_used=str(model_used),
            latency_ms=latency_ms,
            raw=completion,
        )
