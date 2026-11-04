"""AS-100: a non-Groq LLM_BASE_URL / GROQ_BASE_URL raises with 0 requests (fake client)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.llm import LLM, LLMRequest  # noqa: E402
from agents.base.llm_settings import LLMSettings  # noqa: E402

GROQ = "https://api.groq.com/openai/v1"


class FakeCompletions:
    def __init__(self) -> None:
        self.calls = 0

    async def create(self, **params):
        self.calls += 1
        if params.get("stream"):
            async def gen():
                delta = SimpleNamespace(content="ok")
                yield SimpleNamespace(choices=[SimpleNamespace(delta=delta)])
            return gen()
        return SimpleNamespace(
            model=params["model"],
            choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))],
            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        )


def _llm(**urls: str) -> tuple[LLM, FakeCompletions]:
    settings = LLMSettings.model_construct(
        groq_api_key="placeholder", llm_max_retries=1, llm_retry_base_delay=0.0, **urls
    )
    comp = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=comp))
    return LLM(model="llama-3.3-70b-versatile", settings=settings, client=client), comp


def _req() -> LLMRequest:
    return LLMRequest(system="s", messages=[{"role": "user", "content": "q"}])


BAD = [
    {"llm_base_url": "https://integrate.api.nvidia.com/v1"},
    {"llm_base_url": "http://localhost:11434/v1"},
    {"llm_base_url": "http://api.groq.com/openai/v1"},
    {"llm_base_url": "https://api.groq.com.evil.example/openai/v1"},
    {"llm_base_url": GROQ, "groq_base_url": "https://api.together.xyz/v1"},
    {"llm_base_url": "", "groq_base_url": "https://api.together.xyz/v1"},
]


@pytest.mark.asyncio
@pytest.mark.parametrize("urls", BAD)
async def test_non_groq_base_url_raises_with_zero_requests(urls: dict) -> None:
    llm, comp = _llm(**urls)
    with pytest.raises(ValueError, match="base URL"):
        await llm.complete(_req())
    with pytest.raises(ValueError, match="base URL"):
        async for _ in llm.astream(_req()):
            pass
    assert comp.calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("url", [GROQ, GROQ + "/", f' "{GROQ}/" '])
async def test_canonical_groq_url_accepted(url: str) -> None:
    llm, comp = _llm(llm_base_url=url, groq_base_url=url)
    resp = await llm.complete(_req())
    assert resp.text == "ok"
    assert comp.calls == 1
