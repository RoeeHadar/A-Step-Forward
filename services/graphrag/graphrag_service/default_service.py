"""Reference (in-memory) GraphRAG service.

Phase-0 skeleton — keeps the surface usable while sub-agent 05 implements the
Neo4j-backed pipeline. Stores nodes/edges in dicts so smoke tests work without
a running database.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from schemas.graph import (
    KGChunk,
    KGEdge,
    KGHybridInput,
    KGNode,
    KGPath,
    KGSearchInput,
    KGSearchResult,
    KGWalkInput,
    NodeKind,
)

from .settings import GraphRAGSettings


class DefaultGraphRAGService:
    def __init__(self, settings: GraphRAGSettings | None = None) -> None:
        self.settings = settings or GraphRAGSettings()
        self._nodes: dict[str, KGNode] = {}
        self._edges: dict[str, KGEdge] = {}
        self._chunks: dict[str, Any] = {}
        self._out: dict[str, set[str]] = defaultdict(set)
        self._in: dict[str, set[str]] = defaultdict(set)

    # ----- writes -----

    async def upsert_node(self, node: KGNode) -> KGNode:
        self._nodes[node.id] = node
        return node

    async def upsert_edge(self, edge: KGEdge) -> KGEdge:
        self._edges[edge.id] = edge
        self._out[edge.src].add(edge.id)
        self._in[edge.dst].add(edge.id)
        return edge

    async def upsert_chunk(self, chunk: KGChunk) -> KGChunk:
        self._chunks[chunk.id] = chunk
        return chunk

    # ----- reads -----

    async def search(self, input: KGSearchInput) -> list[KGSearchResult]:
        q_tokens = {t for t in input.query.lower().split() if len(t) > 2}
        results: list[KGSearchResult] = []
        for node in self._nodes.values():
            if input.kinds and node.kind not in input.kinds:
                continue
            name_lower = node.canonical_name.lower()
            hay = " ".join([node.canonical_name, *node.aliases, node.summary or ""]).lower()
            hay_tokens = set(hay.split())
            overlap = len(q_tokens & hay_tokens)
            contains = input.query.lower() in hay
            name_overlap = len(q_tokens & set(name_lower.split()))
            if overlap == 0 and not contains and name_overlap == 0:
                continue
            score = 0.45 + min(0.35, overlap * 0.12) + min(0.25, name_overlap * 0.15)
            if contains:
                score = max(score, 0.75)
            if name_lower in input.query.lower() or input.query.lower() in name_lower:
                score = max(score, 0.9)
            if node.kind in {NodeKind.CONCEPT, NodeKind.SKILL, NodeKind.TOPIC, NodeKind.MISCONCEPTION}:
                score = min(0.72, score + 0.08)
            if node.kind == NodeKind.RESOURCE and node.id.startswith("resource:"):
                score = max(0.0, score - 0.2)
            score = min(0.72, score)
            results.append(KGSearchResult(node=node, score=score, snippet=node.summary))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[: input.k]

    async def walk(self, input: KGWalkInput) -> list[KGPath]:
        paths: list[KGPath] = []
        for seed in input.seed_node_ids:
            visited_nodes: list[KGNode] = []
            visited_edges: list[KGEdge] = []
            frontier = [seed]
            for _ in range(input.depth):
                next_frontier: list[str] = []
                for nid in frontier:
                    node = self._nodes.get(nid)
                    if node and node not in visited_nodes:
                        visited_nodes.append(node)
                    for eid in self._out.get(nid, set()):
                        e = self._edges[eid]
                        if input.edge_kinds and e.kind not in input.edge_kinds:
                            continue
                        visited_edges.append(e)
                        next_frontier.append(e.dst)
                frontier = next_frontier
            paths.append(KGPath(nodes=visited_nodes, edges=visited_edges))
        return paths[: input.limit]

    async def hybrid(self, input: KGHybridInput) -> list[KGSearchResult]:
        seeds = await self.search(KGSearchInput(query=input.query, k=input.k))
        seed_ids = [s.node.id for s in seeds if not s.node.id.startswith("resource:")]
        if not seed_ids:
            return seeds
        paths = await self.walk(
            KGWalkInput(seed_node_ids=seed_ids, depth=input.depth, limit=input.k * 3)
        )
        seen = {s.node.id for s in seeds}
        merged = list(seeds)
        for path in paths:
            for node in path.nodes:
                if node.id in seen:
                    continue
                seen.add(node.id)
                merged.append(KGSearchResult(node=node, score=0.55, snippet=node.summary))
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged[: input.k]

    async def personalized(self, *, learner_id: str, query: str, k: int = 10) -> list[KGSearchResult]:
        base = await self.hybrid(KGHybridInput(query=query, k=k, depth=2, learner_id=learner_id))
        touch: set[str] = set()
        learner_node = f"learner:{learner_id}"
        for eid in self._out.get(learner_node, set()) | self._in.get(learner_node, set()):
            e = self._edges[eid]
            touch.add(e.src)
            touch.add(e.dst)
        boosted: list[tuple[float, KGSearchResult]] = []
        for row in base:
            raw_score = row.score + (0.25 if row.node.id in touch else 0.0)
            boosted.append(
                (
                    raw_score,
                    KGSearchResult(
                        node=row.node,
                        score=min(1.0, max(0.0, raw_score)),
                        snippet=row.snippet,
                    ),
                )
            )
        boosted.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in boosted[:k]]

    async def related_concepts(self, concept_id: str) -> list[KGNode]:
        nodes: list[KGNode] = []
        for eid in self._out.get(concept_id, set()):
            e = self._edges[eid]
            n = self._nodes.get(e.dst)
            if n is not None:
                nodes.append(n)
        return nodes

    async def prereqs(self, concept_id: str) -> list[KGNode]:
        out: list[KGNode] = []
        for eid in self._in.get(concept_id, set()):
            e = self._edges[eid]
            if e.kind.value == "PREREQUISITE_OF":
                n = self._nodes.get(e.src)
                if n is not None:
                    out.append(n)
        return out

    async def next_topics(self, *, concept_id: str, learner_id: str) -> list[KGNode]:
        _ = learner_id
        return await self.related_concepts(concept_id)

    async def explain_path(self, src: str, dst: str) -> KGPath | None:
        # Phase-0 BFS over outgoing edges.
        from collections import deque

        seen: dict[str, str | None] = {src: None}
        edge_in: dict[str, KGEdge] = {}
        q: deque[str] = deque([src])
        while q:
            cur = q.popleft()
            if cur == dst:
                # reconstruct
                nodes: list[KGNode] = []
                edges: list[KGEdge] = []
                node = cur
                while node is not None:
                    n = self._nodes.get(node)
                    if n:
                        nodes.append(n)
                    parent = seen[node]
                    if parent is not None:
                        edges.append(edge_in[node])
                    node = parent
                nodes.reverse()
                edges.reverse()
                return KGPath(nodes=nodes, edges=edges, score=0.5)
            for eid in self._out.get(cur, set()):
                e = self._edges[eid]
                if e.dst not in seen:
                    seen[e.dst] = cur
                    edge_in[e.dst] = e
                    q.append(e.dst)
        return None
