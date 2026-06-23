"""API settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_name: str = "a-step-forward"
    log_level: str = "INFO"
    rate_limit_enabled: bool = True
    dev_allow_role_headers: bool = False

    cors_origins: list[str] = ["http://localhost:3000"]

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


@lru_cache
def get_settings() -> APISettings:
    return APISettings()
