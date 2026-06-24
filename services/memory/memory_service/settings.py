"""Memory service settings (env-bound)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class MemorySettings(BaseSettings):
    """Bound to environment variables; see .env.example."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://astepforward:astepforward@localhost:5432/astepforward"
    redis_url: str = "redis://localhost:6379/0"

    embedding_model: str = "voyage-3-large"
    embedding_dim: int = 1024
    rerank_model: str = "rerank-2"

    decay_tau_days: float = 14.0
    consolidation_dup_cosine: float = 0.92
    kg_promote_salience: float = 0.7
    context_compact_ratio: float = 0.8
    archive_threshold: float = 0.05

    dream_cron: str = "0 3 * * *"
    dream_window_hours: int = 24
    micro_dream_min_session_minutes: int = 30

    presidio_enabled: bool = True
    llm_judge_enabled: bool = False

    groq_api_key: str | None = None
    llm_default_model: str = "llama-3.3-70b-versatile"

    compaction_verbatim_turns: int = 6
    verification_min_salience: float = 0.6
    verification_max_age_days: int = 60

    encryption_key_b64: str = "change-me-base64-32-bytes"
