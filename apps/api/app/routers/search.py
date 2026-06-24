"""Public hybrid GraphRAG search (graceful degradation when DB/Neo4j unavailable)."""

from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter(prefix="/v1/search", tags=["search"])


@router.get("")
async def hybrid_search(q: str = Query(..., min_length=1), top_k: int = Query(5, ge=1, le=50)):
    """
    Hybrid GraphRAG search: vector similarity (pgvector) + KG walk (Neo4j).
    Falls back to vector-only if Neo4j is unavailable.
    """
    try:
        from services.graphrag.retrieval import hybrid_search as _hybrid

        results = await _hybrid(q, top_k=top_k)
        return {"results": results, "warning": None}
    except ImportError:
        return {
            "results": [],
            "warning": "GraphRAG service not available. Set NEO4J_URI and DATABASE_URL.",
        }
    except Exception as exc:
        return {
            "results": [],
            "warning": f"GraphRAG unavailable: {str(exc)[:120]}",
        }
