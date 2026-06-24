"""Entity resolution — link extracted entities to existing KG nodes."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz
from schemas.graph import Entity, KGNode, NodeKind

from ..settings import GraphRAGSettings
from ..stores.neo4j_store import Neo4jStore


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "unknown"


@dataclass(frozen=True)
class ResolvedEntity:
    entity: Entity
    node: KGNode
    linked: bool
    score: float


class EntityResolver:
    def __init__(self, settings: GraphRAGSettings, store: Neo4jStore | None = None) -> None:
        self.settings = settings
        self.store = store
        self._memory_nodes: dict[str, KGNode] = {}

    def seed_memory(self, nodes: dict[str, KGNode]) -> None:
        self._memory_nodes = nodes

    async def resolve(self, entities: list[Entity]) -> list[ResolvedEntity]:
        resolved: list[ResolvedEntity] = []
        for entity in entities:
            resolved.append(await self._resolve_one(entity))
        return resolved

    async def _resolve_one(self, entity: Entity) -> ResolvedEntity:
        best: KGNode | None = None
        best_score = 0.0
        candidates = await self._candidates(entity.kind)
        for node in candidates:
            score = max(
                fuzz.token_sort_ratio(entity.name.lower(), node.canonical_name.lower()) / 100.0,
                max(
                    (fuzz.token_sort_ratio(entity.name.lower(), alias.lower()) / 100.0 for alias in node.aliases),
                    default=0.0,
                ),
            )
            if score > best_score:
                best_score = score
                best = node

        if best is not None and best_score >= self.settings.entity_link_threshold:
            return ResolvedEntity(entity=entity, node=best, linked=True, score=best_score)

        node_id = f"{entity.kind.value.lower()}:{_slug(entity.name)}"
        pending = entity.confidence < 0.6
        node = KGNode(
            id=node_id,
            kind=entity.kind,
            canonical_name=entity.name,
            aliases=entity.aliases,
            summary=entity.description,
            pending_review=pending,
        )
        return ResolvedEntity(entity=entity, node=node, linked=False, score=entity.confidence)

    async def _candidates(self, kind: NodeKind) -> list[KGNode]:
        if self.store is not None:
            return await self.store.find_nodes_by_names([], kinds=[kind])
        return [n for n in self._memory_nodes.values() if n.kind == kind]
