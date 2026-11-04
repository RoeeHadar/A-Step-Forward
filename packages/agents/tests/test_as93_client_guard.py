"""AS-93: every runtime LLM call goes through the guarded LLM client + resolve_model;
case-insensitive LLM_PROVIDER; failover only on retriable errors; max_output_tokens=0 kept.

Fake clients only (AsyncMock); real groq SDK exception classes; no network, no keys.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[3]
for p in ("packages/schemas", "packages/agents", "services/learning_path", "services/learner_model",
          "services/memory", "services/graphrag"):
    sys.path.insert(0, str(ROOT / p))

import groq  # noqa: E402
from agents.base.llm import LLM, LLMRequest, resolve_model  # noqa: E402
from agents.base.llm_settings import LLMSettings  # noqa: E402

GROQ_IDS = {"llama-3.3-70b-versatile", "llama-3.1-8b-instant"}


def _settings(provider: str = "groq") -> LLMSettings:
    return LLMSettings.model_construct(
        groq_api_key="test-key", llm_provider=provider,
        llm_timeout_seconds=1.0, llm_max_retries=1, llm_retry_base_delay=0.0,
    )


def _done(text: str = "ok") -> SimpleNamespace:
    return SimpleNamespace(model="m", choices=[SimpleNamespace(message=SimpleNamespace(content=text))], usage=None)


def _client(*effects) -> SimpleNamespace:
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=AsyncMock(side_effect=list(effects)))))


def _req(max_output_tokens: int | None = 16) -> LLMRequest:
    return LLMRequest(system="s", messages=[{"role": "user", "content": "q"}], max_output_tokens=max_output_tokens)


@pytest.fixture
def no_raw_http(monkeypatch):
    """Any direct httpx POST (the pre-AS-93 path) is recorded and fails the call."""
    posts: list[str] = []

    async def _post(self, url, *a, **k):
        posts.append(str(url))
        raise AssertionError(f"direct HTTP LLM call to {url}")

    monkeypatch.setattr(httpx.AsyncClient, "post", _post)
    return posts


# ----- clause 2: in-scope direct calls now use the guarded client -----

@pytest.mark.asyncio
async def test_quiz_generator_uses_guarded_client(no_raw_http) -> None:
    from learning_path_service import quiz_generator as qg

    items = [{"topic": "algebra", "stem": "2+2?", "choices": ["1", "2", "3", "4"], "correct": "D", "difficulty": 3}]
    client = _client(_done(json.dumps(items)))
    llm = LLM(model=qg.GROQ_MODEL, settings=_settings(), client=client)
    out = await qg.generate_via_llm(["algebra"], "math", 1, llm=llm)
    assert no_raw_http == []
    assert client.chat.completions.create.await_args.kwargs["model"] in GROQ_IDS
    assert [i.stem for i in out] == ["2+2?"]


@pytest.mark.asyncio
async def test_memory_dream_helper_uses_guarded_client(no_raw_http) -> None:
    from memory_service.hygiene.llm_helper import dream_llm_complete

    client = _client(_done(" insight "))
    llm = LLM(model="llama-3.3-70b-versatile", settings=_settings(), client=client)
    assert await dream_llm_complete("p", llm=llm) == "insight"
    assert no_raw_http == []
    assert client.chat.completions.create.await_args.kwargs["model"] in GROQ_IDS


@pytest.mark.asyncio
async def test_graphrag_extractor_uses_guarded_client(no_raw_http) -> None:
    from graphrag_service.ingest.extractor import Extractor
    from graphrag_service.settings import GraphRAGSettings

    body = {"entities": [], "relations": [], "claims": [], "confidence": 0.9, "notes": ""}
    client = _client(_done(json.dumps(body)))
    settings = GraphRAGSettings()
    llm = LLM(model=settings.extraction_model, settings=_settings(), client=client)
    ex = Extractor(settings, llm=llm)
    out = await ex.extract(["# Fractions"])
    assert no_raw_http == []
    # manifest-style id claude-sonnet-4-5 is resolved to a Groq id, never sent raw
    assert client.chat.completions.create.await_args.kwargs["model"] in GROQ_IDS
    assert out.confidence == 0.9


# ----- clause 3: case-insensitive LLM_PROVIDER -----

@pytest.mark.parametrize("provider", ["GROQ", " Groq ", "groq"])
def test_provider_case_insensitive(provider: str) -> None:
    assert resolve_model("claude-sonnet-4-5", provider) == "llama-3.3-70b-versatile"


@pytest.mark.parametrize("provider", ["openai", "OpenAI", "anthropic", ""])
def test_other_providers_still_raise(provider: str) -> None:
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        resolve_model("claude-sonnet-4-5", provider)


# ----- clause 4: failover only on retriable errors -----

_REQ = httpx.Request("POST", "http://fake.invalid/chat/completions")


def _status(cls, code: int):
    return cls(f"http {code}", response=httpx.Response(code, request=_REQ), body=None)


RETRIABLE = {
    "timeout": lambda: groq.APITimeoutError(request=_REQ),
    "connection": lambda: groq.APIConnectionError(request=_REQ),
    "429": lambda: _status(groq.RateLimitError, 429),
    "500": lambda: _status(groq.InternalServerError, 500),
    "503": lambda: _status(groq.InternalServerError, 503),
}
NON_RETRIABLE = {
    "400": lambda: _status(groq.BadRequestError, 400),
    "401": lambda: _status(groq.AuthenticationError, 401),
    "403": lambda: _status(groq.PermissionDeniedError, 403),
}


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", sorted(RETRIABLE))
async def test_failover_fires_on_retriable(kind: str) -> None:
    client = _client(RETRIABLE[kind](), _done())
    llm = LLM(model="claude-sonnet-4-5", fallback_model="gpt-5-mini", settings=_settings(), client=client)
    assert (await llm.complete(_req())).text == "ok"
    assert [c.kwargs["model"] for c in client.chat.completions.create.await_args_list] == [
        "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", sorted(NON_RETRIABLE))
async def test_failover_does_not_fire_on_client_errors(kind: str) -> None:
    exc = NON_RETRIABLE[kind]()
    client = _client(exc, _done())
    llm = LLM(model="claude-sonnet-4-5", fallback_model="gpt-5-mini", settings=_settings(), client=client)
    with pytest.raises(type(exc)):
        await llm.complete(_req())
    assert client.chat.completions.create.await_count == 1


# ----- clause 5: max_output_tokens=0 is kept -----

@pytest.mark.asyncio
async def test_zero_max_output_tokens_not_replaced() -> None:
    client = _client(_done())
    await LLM(model="claude-haiku-4-5", settings=_settings(), client=client).complete(_req(0))
    assert client.chat.completions.create.await_args.kwargs["max_tokens"] == 0


@pytest.mark.asyncio
async def test_none_max_output_tokens_still_defaults() -> None:
    client = _client(_done())
    await LLM(model="claude-haiku-4-5", settings=_settings(), client=client).complete(_req(None))
    assert client.chat.completions.create.await_args.kwargs["max_tokens"] == 4_000
