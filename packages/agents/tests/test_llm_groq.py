"""Tests for the Groq-backed :class:`agents.base.llm.LLM` wrapper.

These tests **never** touch the real Groq API. Every test injects an
``AsyncMock``-based fake client into the :class:`LLM` constructor, so the
suite runs offline / in CI without a ``GROQ_API_KEY``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.llm import LLM, STUB_PREFIX, LLMRequest  # noqa: E402
from agents.base.llm_settings import LLMSettings  # noqa: E402


def _settings(*, api_key: str | None = "test-key", max_retries: int = 3) -> LLMSettings:
    """Build an :class:`LLMSettings` that bypasses the local ``.env`` file."""
    return LLMSettings.model_construct(
        groq_api_key=api_key,
        groq_base_url="https://api.groq.com/openai/v1",
        llm_default_model="llama-3.3-70b-versatile",
        llm_cheap_model="llama-3.1-8b-instant",
        llm_timeout_seconds=30.0,
        llm_max_retries=max_retries,
        llm_retry_base_delay=0.0,  # snappy tests
    )


def _completion(
    text: str,
    *,
    prompt_tokens: int = 12,
    completion_tokens: int = 7,
) -> SimpleNamespace:
    return SimpleNamespace(
        model="llama-3.3-70b-versatile",
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))],
        usage=SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
    )


def _rate_limit_error() -> Exception:
    from groq import RateLimitError

    response = httpx.Response(
        status_code=429,
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )
    return RateLimitError(message="rate limited", response=response, body={})


def _stub_request(user: str = "Explain fractions please") -> LLMRequest:
    return LLMRequest(
        system="You are a Socratic tutor.",
        messages=[{"role": "user", "content": user}],
        metadata={"trace_name": "tutor:test"},
    )


@pytest.mark.asyncio
async def test_complete_returns_stub_when_no_api_key() -> None:
    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(api_key=None))
    response = await llm.complete(_stub_request())

    assert response.text.startswith(STUB_PREFIX)
    assert "Explain fractions" in response.text
    assert "GROQ_API_KEY" in response.text
    assert response.model_used == "llama-3.3-70b-versatile"


@pytest.mark.asyncio
async def test_complete_calls_groq_and_populates_tokens() -> None:
    completion = _completion("Hello, learner!", prompt_tokens=21, completion_tokens=9)
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=AsyncMock(return_value=completion)),
        )
    )
    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(), client=client)
    response = await llm.complete(_stub_request())

    assert response.text == "Hello, learner!"
    assert response.input_tokens == 21
    assert response.output_tokens == 9
    assert response.model_used == "llama-3.3-70b-versatile"
    assert response.latency_ms >= 0

    call = client.chat.completions.create.await_args
    assert call.kwargs["model"] == "llama-3.3-70b-versatile"
    assert call.kwargs["messages"][0]["role"] == "system"
    assert call.kwargs["messages"][-1]["role"] == "user"


@pytest.mark.asyncio
async def test_complete_retries_on_rate_limit_then_succeeds() -> None:
    completion = _completion("Recovered after retry.")
    create = AsyncMock(side_effect=[_rate_limit_error(), _rate_limit_error(), completion])
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(max_retries=3), client=client)
    response = await llm.complete(_stub_request())

    assert response.text == "Recovered after retry."
    assert create.await_count == 3


@pytest.mark.asyncio
async def test_complete_gives_up_after_max_retries() -> None:
    from groq import RateLimitError

    create = AsyncMock(side_effect=[_rate_limit_error(), _rate_limit_error(), _rate_limit_error()])
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(max_retries=3), client=client)
    with pytest.raises(RateLimitError):
        await llm.complete(_stub_request())

    assert create.await_count == 3


@pytest.mark.asyncio
async def test_complete_does_not_retry_on_400() -> None:
    """400-class errors are programmer errors — surface them, do not retry."""
    from groq import BadRequestError

    response = httpx.Response(
        status_code=400,
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )
    err = BadRequestError(message="bad request", response=response, body={})

    create = AsyncMock(side_effect=err)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(), client=client)
    with pytest.raises(BadRequestError):
        await llm.complete(_stub_request())

    assert create.await_count == 1


@pytest.mark.asyncio
async def test_astream_yields_tokens() -> None:
    async def fake_stream():
        chunks = [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Hello"))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=", "))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="world!"))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None))]),
        ]
        for c in chunks:
            yield c

    create = AsyncMock(return_value=fake_stream())
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(), client=client)

    pieces = [token async for token in llm.astream(_stub_request())]
    assert pieces == ["Hello", ", ", "world!"]
    assert create.await_args.kwargs["stream"] is True


@pytest.mark.asyncio
async def test_astream_falls_back_to_stub_without_key() -> None:
    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(api_key=None))
    pieces = [token async for token in llm.astream(_stub_request("What is photosynthesis?"))]

    assert len(pieces) == 1
    assert pieces[0].startswith(STUB_PREFIX)
    assert "photosynthesis" in pieces[0]
