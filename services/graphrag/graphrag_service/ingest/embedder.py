"""Embedding client for GraphRAG chunks."""

from __future__ import annotations

import hashlib
import os

import httpx
import structlog

from ..settings import GraphRAGSettings

log = structlog.get_logger(__name__)


class Embedder:
    def __init__(self, settings: GraphRAGSettings) -> None:
        self.settings = settings
        self._api_key = os.getenv("VOYAGE_API_KEY", "")

    def _deterministic(self, text: str) -> list[float]:
        """Offline fallback: stable pseudo-embedding from text hash."""
        dim = self.settings.embedding_dim
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for i in range(dim):
            b = digest[i % len(digest)]
            values.append((b / 255.0) * 2.0 - 1.0)
        return values

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self._api_key:
            log.warning("embedder.offline_mode", reason="VOYAGE_API_KEY not set")
            return [self._deterministic(t) for t in texts]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"input": texts, "model": self.settings.embedding_model},
            )
            response.raise_for_status()
            data = response.json()["data"]
            return [row["embedding"] for row in data]
