"""LLM provider settings.

Loaded via ``pydantic-settings`` so feature code never reaches for
``os.getenv`` (see ``.cursor/rules/20-python-style.mdc``).

The defaults below assume Groq Cloud (https://console.groq.com) as the primary
provider — see ``docs/adr/0004-llm-provider-groq.md``. When ``groq_api_key`` is
unset the LLM wrapper returns a deterministic offline stub so the demo still
works.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Environment-driven LLM configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com/openai/v1"

    llm_default_model: str = "llama-3.3-70b-versatile"
    llm_cheap_model: str = "llama-3.1-8b-instant"

    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    llm_retry_base_delay: float = 0.5


@lru_cache(maxsize=1)
def get_llm_settings() -> LLMSettings:
    return LLMSettings()
