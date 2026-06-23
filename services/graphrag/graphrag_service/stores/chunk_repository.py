"""pgvector-backed chunk repository for GraphRAG."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any

import structlog
from schemas.graph import KGChunk

from ..settings import GraphRAGSettings

log = structlog.get_logger(__name__)


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class ChunkRepository:
    """Stores and retrieves KG chunks.

    Uses Postgres+pgvector when available; falls back to an in-memory dict so
    unit tests and offline dev stay usable without a running database.
    """

    def __init__(self, settings: GraphRAGSettings) -> None:
        self.settings = settings
        self._memory: dict[str, KGChunk] = {}
        self._engine: Any | None = None
        self._sessionmaker: Any | None = None
        self._use_postgres = settings.use_postgres_chunks

    async def connect(self) -> None:
        if not self._use_postgres:
            return
        if self._engine is not None:
            return
        try:
            from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

            self._engine = create_async_engine(self.settings.database_url, pool_pre_ping=True)
            self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
            log.info("chunk_repository.connected")
        except Exception as exc:
            log.warning("chunk_repository.postgres_unavailable", error=str(exc))
            self._use_postgres = False

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    async def upsert(self, chunk: KGChunk) -> KGChunk:
        if not self._use_postgres or self._sessionmaker is None:
            self._memory[chunk.id] = chunk
            return chunk

        from sqlalchemy import text

        embedding = chunk.embedding or [0.0] * self.settings.embedding_dim
        provenance = chunk.provenance.model_dump(mode="json") if chunk.provenance else None
        async with self._sessionmaker() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO kg_chunks
                        (id, document_id, ordinal, text, heading, token_count, embedding, provenance, created_at)
                    VALUES
                        (:id, :document_id, :ordinal, :text, :heading, :token_count, :embedding, :provenance, :created_at)
                    ON CONFLICT (id) DO UPDATE SET
                        text = EXCLUDED.text,
                        heading = EXCLUDED.heading,
                        token_count = EXCLUDED.token_count,
                        embedding = EXCLUDED.embedding,
                        provenance = EXCLUDED.provenance
                    """
                ),
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "ordinal": chunk.ordinal,
                    "text": chunk.text,
                    "heading": chunk.heading,
                    "token_count": chunk.token_count,
                    "embedding": str(embedding),
                    "provenance": json.dumps(provenance) if provenance else None,
                    "created_at": chunk.created_at,
                },
            )
            await session.commit()
        return chunk

    async def vector_search(
        self,
        query_embedding: list[float],
        *,
        k: int = 10,
        document_id: str | None = None,
    ) -> list[tuple[KGChunk, float]]:
        if not self._use_postgres or self._sessionmaker is None:
            scored = [
                (chunk, _cosine(query_embedding, chunk.embedding or []))
                for chunk in self._memory.values()
                if document_id is None or chunk.document_id == document_id
            ]
            scored.sort(key=lambda row: row[1], reverse=True)
            return scored[:k]

        from sqlalchemy import text

        params: dict[str, Any] = {
            "embedding": str(query_embedding),
            "k": k,
        }
        doc_filter = ""
        if document_id is not None:
            doc_filter = "AND document_id = :document_id"
            params["document_id"] = document_id

        async with self._sessionmaker() as session:
            result = await session.execute(
                text(
                    f"""
                    SELECT id, document_id, ordinal, text, heading, token_count, provenance, created_at,
                           1 - (embedding <=> :embedding::vector) AS score
                    FROM kg_chunks
                    WHERE TRUE {doc_filter}
                    ORDER BY embedding <=> :embedding::vector
                    LIMIT :k
                    """
                ),
                params,
            )
            rows = result.mappings().all()

        out: list[tuple[KGChunk, float]] = []
        for row in rows:
            provenance_raw = row["provenance"]
            provenance = json.loads(provenance_raw) if isinstance(provenance_raw, str) else provenance_raw
            chunk = KGChunk(
                id=row["id"],
                document_id=row["document_id"],
                ordinal=row["ordinal"],
                text=row["text"],
                heading=row["heading"],
                token_count=row["token_count"],
                embedding=None,
                provenance=provenance,  # type: ignore[arg-type]
                created_at=row["created_at"] or datetime.now(timezone.utc),
            )
            out.append((chunk, float(row["score"])))
        return out

    async def get_by_document(self, document_id: str) -> list[KGChunk]:
        if not self._use_postgres or self._sessionmaker is None:
            rows = [c for c in self._memory.values() if c.document_id == document_id]
            return sorted(rows, key=lambda c: c.ordinal)

        from sqlalchemy import text

        async with self._sessionmaker() as session:
            result = await session.execute(
                text(
                    """
                    SELECT id, document_id, ordinal, text, heading, token_count, provenance, created_at
                    FROM kg_chunks
                    WHERE document_id = :document_id
                    ORDER BY ordinal
                    """
                ),
                {"document_id": document_id},
            )
            rows = result.mappings().all()

        chunks: list[KGChunk] = []
        for row in rows:
            provenance_raw = row["provenance"]
            provenance = json.loads(provenance_raw) if isinstance(provenance_raw, str) else provenance_raw
            chunks.append(
                KGChunk(
                    id=row["id"],
                    document_id=row["document_id"],
                    ordinal=row["ordinal"],
                    text=row["text"],
                    heading=row["heading"],
                    token_count=row["token_count"],
                    provenance=provenance,  # type: ignore[arg-type]
                    created_at=row["created_at"] or datetime.now(timezone.utc),
                )
            )
        return chunks
