"""Learner model service settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class LearnerModelSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://astepforward:astepforward@localhost:5432/astepforward"
