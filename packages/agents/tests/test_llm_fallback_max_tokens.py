"""AS-92: one failover to fallback_model (resolved to a Groq id), and max_tokens never null.

Fake clients only (AsyncMock); no network, no keys.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.llm import LLM, LLMRequest  # noqa: E402
from agents.base.llm_settings import LLMSettings  # noqa: E402


def _settings() -> LLMSettings:
    return LLMSettings.model_construct(
        groq_api_key="test-key", llm_provider="groq",
        llm_timeout_seconds=1.0, llm_max_retries=1, llm_retry_base_delay=0.0,
    )


def _done() -> SimpleNamespace:
    return SimpleNamespace(model="m", choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))], usage=None)


async def _stream():
    yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="hi"))])


def _client(*effects) -> SimpleNamespace:
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(side_effect=list(effects)))))


def _req(max_output_tokens: int | None = 16) -> LLMRequest:
    return LLMRequest(system="s", messages=[{"role": "user", "content": "q"}], max_output_tokens=max_output_tokens)


def _sent(client) -> list[str]:
    return [c.kwargs["model"] for c in client.chat.completions.create.await_args_list]


@pytest.mark.asyncio
async def test_complete_fails_over_once_to_resolved_fallback() -> None:
    client = _client(RuntimeError("primary down"), _done())
    llm = LLM(model="claude-sonnet-4-5", fallback_model="gpt-5-mini", settings=_settings(), client=client)
    resp = await llm.complete(_req())
    assert resp.text == "ok"
    # primary resolved to its Groq id, fallback resolved too: never a non-Groq id on the wire
    assert _sent(client) == ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


@pytest.mark.asyncio
async def test_astream_fails_over_once_to_resolved_fallback() -> None:
    client = _client(RuntimeError("primary down"), _stream())
    llm = LLM(model="claude-opus-4-8", fallback_model="claude-haiku-4-5", settings=_settings(), client=client)
    chunks = [c async for c in llm.astream(_req())]
    assert chunks == ["hi"]
    assert _sent(client) == ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


@pytest.mark.asyncio
async def test_fallback_failure_reraises_after_exactly_one_failover() -> None:
    client = _client(RuntimeError("primary down"), RuntimeError("fallback down"), _done())
    llm = LLM(model="claude-sonnet-4-5", fallback_model="gpt-5-mini", settings=_settings(), client=client)
    with pytest.raises(RuntimeError, match="fallback down"):
        await llm.complete(_req())
    assert client.chat.completions.create.await_count == 2


@pytest.mark.asyncio
async def test_no_fallback_reraises_primary_error() -> None:
    client = _client(RuntimeError("primary down"), _done())
    llm = LLM(model="claude-sonnet-4-5", settings=_settings(), client=client)
    with pytest.raises(RuntimeError, match="primary down"):
        await llm.complete(_req())
    assert client.chat.completions.create.await_count == 1


@pytest.mark.asyncio
async def test_unknown_fallback_id_raises_and_is_not_sent() -> None:
    client = _client(RuntimeError("primary down"), _done())
    llm = LLM(model="claude-sonnet-4-5", fallback_model="no-such-model", settings=_settings(), client=client)
    with pytest.raises(ValueError, match="no-such-model"):
        await llm.complete(_req())
    assert _sent(client) == ["llama-3.3-70b-versatile"]


@pytest.mark.asyncio
async def test_null_max_output_tokens_sends_default() -> None:
    client = _client(_done())
    await LLM(model="claude-haiku-4-5", settings=_settings(), client=client).complete(_req(None))
    assert client.chat.completions.create.await_args.kwargs["max_tokens"] == 4_000
