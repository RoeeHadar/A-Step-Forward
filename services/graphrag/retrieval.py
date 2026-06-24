"""
Hybrid GraphRAG retrieval: pgvector similarity + Neo4j KG walk.
Falls back to vector-only if Neo4j is unavailable.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any


def _asyncpg_dsn(database_url: str) -> str:
    """Normalize SQLAlchemy-style URLs for asyncpg."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


async def hybrid_search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Vector-seed the top_k chunks from pgvector, then optionally walk Neo4j."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return []

    results = await _vector_search(query, top_k, database_url)

    neo4j_uri = os.getenv("NEO4J_URI")
    if neo4j_uri and results:
        try:
            results = await _kg_enrich(results, neo4j_uri)
        except Exception:
            pass

    return results


async def _vector_search(query: str, top_k: int, database_url: str) -> list[dict[str, Any]]:
    """Search kg_chunks table by embedding similarity."""
    try:
        import asyncpg
        from sentence_transformers import SentenceTransformer

        def _encode() -> list[float]:
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            vector = model.encode(query, normalize_embeddings=True)
            return vector.tolist()

        embedding = await asyncio.to_thread(_encode)
        dsn = _asyncpg_dsn(database_url)

        conn = await asyncpg.connect(dsn)
        try:
            rows = await conn.fetch(
                """
                SELECT id, text, document_id, heading, provenance,
                       1 - (embedding <=> $1::vector) AS score
                FROM kg_chunks
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                str(embedding),
                top_k,
            )
            out: list[dict[str, Any]] = []
            for row in rows:
                provenance_raw = row["provenance"]
                provenance: dict[str, Any] = {}
                if provenance_raw:
                    if isinstance(provenance_raw, str):
                        provenance = json.loads(provenance_raw)
                    elif isinstance(provenance_raw, dict):
                        provenance = provenance_raw
                out.append(
                    {
                        "id": row["id"],
                        "content": row["text"],
                        "subject": provenance.get("subject"),
                        "source_url": row["document_id"],
                        "heading": row["heading"],
                        "score": float(row["score"]),
                    }
                )
            return out
        finally:
            await conn.close()
    except Exception:
        return []


async def _kg_enrich(results: list[dict[str, Any]], neo4j_uri: str) -> list[dict[str, Any]]:
    """Stub: KG walk enrichment. Returns results unchanged."""
    _ = neo4j_uri
    return results
