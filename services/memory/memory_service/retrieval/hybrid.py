"""Hybrid retrieval: BM25 + dense + KG-walk + rerank.

Phase 0 is a naive in-memory keyword-match scorer so the rest of the system can
plug in. Sub-agent 04 swaps the implementation to pgvector dense + Postgres FTS
+ KG walks + Cohere/Voyage rerank.
"""

from __future__ import annotations

from schemas.memory import (
    MemoryRecord,
    MemorySearchInput,
    MemorySearchResult,
)

from ..hygiene.decay import strength_now
from ..stores.repository import MemoryRepository


def _lexical_overlap(query: str, text: str) -> float:
    q = {w for w in query.lower().split() if len(w) > 2}
    t = {w for w in text.lower().split() if len(w) > 2}
    if not q or not t:
        return 0.0
    return len(q & t) / max(1, len(q))


async def hybrid_search(repo: MemoryRepository, input: MemorySearchInput) -> list[MemorySearchResult]:
    rows: list[MemoryRecord] = []
    for r in await repo.iter_for_learner(input.learner_id):
        if input.types and r.type not in input.types:
            continue
        if not input.include_archived and (r.archived_at or r.deleted_at):
            continue
        if r.superseded_by:
            continue
        rows.append(r)

    # AS-110: k / min_strength are AS-90 fields (None when unset, e.g. the GET /v1/memory?q=
    # route builds MemorySearchInput without min_strength); use the pre-AS-90 defaults.
    min_strength = input.min_strength if input.min_strength is not None else 0.0
    k = input.k if input.k is not None else 10
    results: list[MemorySearchResult] = []
    for r in rows:
        lex = _lexical_overlap(input.query, r.content)
        recency = strength_now(r)
        score = 0.55 * lex + 0.25 * recency + 0.20 * r.confidence
        if score < min_strength:
            continue
        results.append(
            MemorySearchResult(
                record=r,
                score=score,
                components={"lexical": lex, "recency": recency, "confidence": r.confidence},
            )
        )

    results.sort(key=lambda x: x.score, reverse=True)
    return results[:k]
