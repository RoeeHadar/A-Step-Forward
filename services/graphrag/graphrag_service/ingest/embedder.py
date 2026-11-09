"""Embedding client for GraphRAG chunks."""

from __future__ import annotations

import asyncio
import hashlib
import os
import ssl

import structlog

from ..settings import GraphRAGSettings

log = structlog.get_logger(__name__)

_ST_PREFIX = "sentence-transformers/"


def _allow_insecure_hub_downloads() -> None:
    """Best-effort SSL bypass for HuggingFace Hub on Windows dev machines."""
    os.environ.setdefault("HF_HUB_DISABLE_SSL", "1")
    try:
        ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore[method-assign]
    except Exception:
        pass
    try:
        import httpx

        _orig_init = httpx.Client.__init__

        def _patched_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            kwargs["verify"] = False
            _orig_init(self, *args, **kwargs)

        httpx.Client.__init__ = _patched_init  # type: ignore[method-assign]
    except Exception:
        pass


class Embedder:
    def __init__(self, settings: GraphRAGSettings) -> None:
        self.settings = settings
        self._st_model: object | None = None

    @property
    def _uses_sentence_transformers(self) -> bool:
        return self.settings.embedding_model.startswith(_ST_PREFIX)

    def _load_st_model(self) -> object:
        if self._st_model is None:
            _allow_insecure_hub_downloads()
            from sentence_transformers import SentenceTransformer

            model_name = self.settings.embedding_model.removeprefix(_ST_PREFIX)
            self._st_model = SentenceTransformer(model_name)
            log.info("embedder.sentence_transformers_loaded", model=model_name)
        return self._st_model

    def _deterministic(self, text: str) -> list[float]:
        """Offline fallback: stable pseudo-embedding from text hash."""
        dim = self.settings.embedding_dim
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for i in range(dim):
            b = digest[i % len(digest)]
            values.append((b / 255.0) * 2.0 - 1.0)
        return values

    def _embed_sentence_transformers(self, texts: list[str]) -> list[list[float]]:
        model = self._load_st_model()
        encode = getattr(model, "encode")
        vectors = encode(texts, normalize_embeddings=True)
        return [row.tolist() for row in vectors]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if self._uses_sentence_transformers:
            try:
                return await asyncio.to_thread(self._embed_sentence_transformers, texts)
            except Exception as exc:
                log.warning("embedder.sentence_transformers_failed", error=str(exc))
                return [self._deterministic(t) for t in texts]

        # AS-97: no hosted embedding API here. ADR-0004 hard constraint #1 rules out
        # Voyage (paid), so the old Voyage branch is gone; a non sentence-transformers
        # model gets the same offline hash fallback a missing VOYAGE_API_KEY used to.
        log.warning(
            "embedder.offline_mode",
            reason="embedding_model is not sentence-transformers/*; no hosted embedder (ADR-0004)",
            model=self.settings.embedding_model,
        )
        return [self._deterministic(t) for t in texts]
