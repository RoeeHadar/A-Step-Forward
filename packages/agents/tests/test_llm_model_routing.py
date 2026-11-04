"""AS-91: manifest model ids must reach a client that serves them.

The only configured provider is Groq (ADR-0004), so manifest ids such as
``claude-sonnet-4-5`` / ``gpt-5-mini`` are mapped to Groq ids, and an unknown
id raises instead of being sent. Fake clients only, no network.
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

from agents import AGENT_REGISTRY  # noqa: E402
from agents.base.llm import LLM, LLMRequest  # noqa: E402
from agents.base.llm_settings import LLMSettings  # noqa: E402

GROQ_IDS = {"llama-3.3-70b-versatile", "llama-3.1-8b-instant"}


def _settings(provider: str = "groq") -> LLMSettings:
    return LLMSettings.model_construct(
        groq_api_key="test-key",
        llm_provider=provider,
        llm_timeout_seconds=1.0,
        llm_max_retries=1,
        llm_retry_base_delay=0.0,
    )


def _client() -> SimpleNamespace:
    done = SimpleNamespace(model="x", choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))], usage=None)
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(return_value=done))))


def _req() -> LLMRequest:
    return LLMRequest(system="s", messages=[{"role": "user", "content": "q"}], max_output_tokens=16)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("manifest_id", "groq_id"),
    [
        ("claude-opus-4-8", "llama-3.3-70b-versatile"),
        ("claude-sonnet-4-5", "llama-3.3-70b-versatile"),
        ("claude-haiku-4-5", "llama-3.1-8b-instant"),
        ("gpt-5-mini", "llama-3.1-8b-instant"),
        ("llama-3.3-70b-versatile", "llama-3.3-70b-versatile"),
    ],
)
async def test_manifest_ids_map_to_groq_ids(manifest_id: str, groq_id: str) -> None:
    client = _client()
    await LLM(model=manifest_id, settings=_settings(), client=client).complete(_req())
    assert client.chat.completions.create.await_args.kwargs["model"] == groq_id


@pytest.mark.asyncio
async def test_every_registered_agent_sends_a_groq_id() -> None:
    for name, manifest in AGENT_REGISTRY.items():
        client = _client()
        await LLM(model=manifest.primary_model, settings=_settings(), client=client).complete(_req())
        assert client.chat.completions.create.await_args.kwargs["model"] in GROQ_IDS, name


@pytest.mark.asyncio
async def test_unknown_model_raises_and_sends_nothing() -> None:
    client = _client()
    with pytest.raises(ValueError, match="no-such-model"):
        await LLM(model="no-such-model", settings=_settings(), client=client).complete(_req())
    client.chat.completions.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_unknown_provider_raises() -> None:
    client = _client()
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        await LLM(model="claude-sonnet-4-5", settings=_settings("anthropic"), client=client).complete(_req())
    client.chat.completions.create.assert_not_awaited()
