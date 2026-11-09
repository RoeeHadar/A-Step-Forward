"""GraphRAG retrieval query builders."""

from __future__ import annotations

from schemas.graph import (
    KGHybridInput,
    KGNode,
    KGPath,
    KGSearchInput,
    KGSearchResult,
    KGWalkInput,
    NodeKind,
)

from ..stores.chunk_repository import ChunkRepository
from ..stores.neo4j_store import Neo4jStore
from ..ingest.embedder import Embedder


async def local_search(
    store: Neo4jStore,
    chunks: ChunkRepository,
    embedder: Embedder,
    input: KGSearchInput,
) -> list[KGSearchResult]:
    k = input.k if input.k is not None else 10  # AS-110: AS-90 field, pre-AS-90 default 10
    query_embedding = (await embedder.embed_texts([input.query]))[0]
    chunk_hits = await chunks.vector_search(query_embedding, k=k)
    if chunk_hits:
        return [
            KGSearchResult(
                node=KGNode(
                    id=f"chunk:{chunk.id}",
                    kind=NodeKind.RESOURCE,
                    canonical_name=chunk.heading or f"Chunk {chunk.ordinal}",
                    summary=chunk.text[:240],
                ),
                score=score,
                snippet=chunk.text[:240],
            )
            for chunk, score in chunk_hits
        ]
    hits = await store.fulltext_search(input.query, k=k, kinds=input.kinds)
    return [
        KGSearchResult(node=node, score=score, snippet=node.summary)
        for node, score in hits
    ]


async def graph_walk(store: Neo4jStore, input: KGWalkInput) -> list[KGPath]:
    return await store.walk(
        input.seed_node_ids,
        # AS-110: depth / limit are AS-90 fields (None when unset); pre-AS-90 defaults 2 / 50.
        depth=input.depth if input.depth is not None else 2,
        edge_kinds=input.edge_kinds,
        limit=input.limit if input.limit is not None else 50,
    )


async def hybrid_search(
    store: Neo4jStore,
    chunks: ChunkRepository,
    embedder: Embedder,
    input: KGHybridInput,
) -> list[KGSearchResult]:
    # AS-110: k / depth are AS-90 fields (None when unset); pre-AS-90 defaults 10 / 2.
    k = input.k if input.k is not None else 10
    depth = input.depth if input.depth is not None else 2
    seeds = await local_search(
        store,
        chunks,
        embedder,
        KGSearchInput(query=input.query, k=k),
    )
    seed_ids = [s.node.id for s in seeds if not s.node.id.startswith("chunk:")]
    if not seed_ids:
        return seeds

    paths = await store.walk(seed_ids, depth=depth, limit=k * 3)
    seen: set[str] = {s.node.id for s in seeds}
    merged = list(seeds)
    for path in paths:
        for node in path.nodes:
            if node.id in seen:
                continue
            seen.add(node.id)
            merged.append(KGSearchResult(node=node, score=0.55, snippet=node.summary))
    merged.sort(key=lambda r: r.score, reverse=True)
    return merged[:k]


async def personalized_search(
    store: Neo4jStore,
    chunks: ChunkRepository,
    embedder: Embedder,
    *,
    learner_id: str,
    query: str,
    k: int,
) -> list[KGSearchResult]:
    base = await hybrid_search(
        store,
        chunks,
        embedder,
        KGHybridInput(query=query, k=k, depth=2, learner_id=learner_id),
    )
    touch = await store.learner_touching_nodes(learner_id)
    if not touch:
        return base

    boosted: list[KGSearchResult] = []
    for row in base:
        boost = 0.22 if row.node.id in touch else 0.0
        boosted.append(
            KGSearchResult(
                node=row.node,
                score=min(1.0, row.score + boost),
                snippet=row.snippet,
            )
        )
    boosted.sort(key=lambda r: r.score, reverse=True)
    return boosted[:k]
