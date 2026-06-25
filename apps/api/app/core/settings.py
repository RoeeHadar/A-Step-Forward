"""API settings."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "https://a-step-forward-waij.vercel.app",
]
# Matches all Vercel preview deploys for our project (e.g.
# `a-step-forward-waij-git-<branch>-<team>.vercel.app`). Starlette's
# CORSMiddleware accepts a regex alongside the exact-match list.
_DEFAULT_CORS_ORIGIN_REGEX: str = r"https://([a-z0-9-]+\.)*vercel\.app"


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_name: str = "a-step-forward"
    log_level: str = "INFO"
    rate_limit_enabled: bool = True
    dev_allow_role_headers: bool = False

    cors_origins: list[str] = list(_DEFAULT_CORS_ORIGINS)
    cors_origin_regex: str | None = _DEFAULT_CORS_ORIGIN_REGEX

    clerk_jwks_url: str | None = None
    clerk_issuer: str | None = None
    clerk_audience: str | None = None
    clerk_publishable_key: str | None = None
    clerk_secret_key: str | None = None

    database_url: str = "postgresql+asyncpg://astepforward:astepforward@localhost:5432/astepforward"
    redis_url: str = "redis://localhost:6379/0"
    neo4j_uri: str = "bolt://localhost:7687"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    sentry_dsn: str | None = None
    otel_exporter_otlp_endpoint: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str | None = None

    groq_api_key: str | None = None
    llm_default_model: str = "llama-3.3-70b-versatile"
    llm_cheap_model: str = "llama-3.1-8b-instant"

    admin_key: str = ""  # if set, POST /v1/admin/* requires X-Admin-Key header
    booking_api_secret: str = ""  # if set, POST /v1/bookings requires X-Booking-Secret

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: Any) -> Any:
        """Accept JSON arrays *or* comma-separated strings from the environment.

        Render currently exposes ``CORS_ORIGINS`` as a single URL (no JSON
        brackets), which would otherwise crash pydantic-settings on boot.
        """
        if value is None or value == "":
            return list(_DEFAULT_CORS_ORIGINS)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                except json.JSONDecodeError:
                    parsed = None
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> APISettings:
    return APISettings()
