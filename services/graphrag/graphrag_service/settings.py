"""GraphRAG settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class GraphRAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "astepforward"
    neo4j_database: str = "neo4j"

    database_url: str = "postgresql+asyncpg://astepforward:astepforward@localhost:5432/astepforward"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    chunk_tokens: int = 600
    chunk_overlap: int = 50

    rerank_model: str = "rerank-2"
    extraction_model: str = "claude-sonnet-4-5"
    entity_link_threshold: float = 0.85

    use_neo4j: bool = False
    use_postgres_chunks: bool = False
    snapshot_bucket: str = "astepforward-kg-snapshots"
    snapshot_prefix: str = "snapshots/"
    verification_sample_rate: float = 0.1
