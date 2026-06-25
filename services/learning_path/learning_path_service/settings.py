"""Learning path service settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class LearningPathSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://astepforward:astepforward@localhost:5432/astepforward"
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"
    mastery_weak_threshold: float = 0.4
    adapt_weak_concept_min: int = 3
