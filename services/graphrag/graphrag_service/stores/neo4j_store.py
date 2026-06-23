"""Neo4j store for the knowledge graph."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import structlog
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from schemas.graph import EdgeKind, KGEdge, KGNode, KGPath, NodeKind

from ..settings import GraphRAGSettings

log = structlog.get_logger(__name__)


def _serialize_provenance(provenance: Any) -> str | None:
    if provenance is None:
        return None
    if hasattr(provenance, "model_dump"):
        return json.dumps(provenance.model_dump(mode="json"))
    return json.dumps(provenance)


def _parse_provenance(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        return json.loads(raw)
    if isinstance(raw, dict):
        return raw
    return None


def _record_to_node(record: dict[str, Any]) -> KGNode:
    props = dict(record)
    kind = NodeKind(props.pop("kind"))
    aliases = props.pop("aliases", []) or []
    if isinstance(aliases, str):
        aliases = json.loads(aliases)
    properties = props.pop("properties", {}) or {}
    if isinstance(properties, str):
        properties = json.loads(properties)
    provenance_raw = props.pop("provenance", None)
    provenance = _parse_provenance(provenance_raw)
    created_at = props.pop("created_at", None)
    return KGNode(
        id=props.pop("id"),
        kind=kind,
        canonical_name=props.pop("canonical_name"),
        aliases=list(aliases),
        summary=props.pop("summary", None),
        properties={str(k): v for k, v in properties.items()},
        provenance=provenance,  # type: ignore[arg-type]
        pending_review=bool(props.pop("pending_review", False)),
        created_at=created_at or datetime.now(timezone.utc),
    )


def _record_to_edge(record: dict[str, Any]) -> KGEdge:
    props = dict(record)
    kind = EdgeKind(props.pop("kind"))
    properties = props.pop("properties", {}) or {}
    if isinstance(properties, str):
        properties = json.loads(properties)
    provenance_raw = props.pop("provenance", None)
    provenance = _parse_provenance(provenance_raw)
    return KGEdge(
        id=props.pop("id"),
        kind=kind,
        src=props.pop("src"),
        dst=props.pop("dst"),
        weight=float(props.pop("weight", 1.0)),
        properties={str(k): v for k, v in properties.items()},
        provenance=provenance,  # type: ignore[arg-type]
    )


class Neo4jStore:
    """Async Neo4j access for KG nodes, edges, and graph queries."""

    def __init__(self, settings: GraphRAGSettings) -> None:
        self.settings = settings
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        if self._driver is not None:
            return
        self._driver = AsyncGraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password),
        )
        await self._driver.verify_connectivity()
        log.info("neo4j.connected", uri=self.settings.neo4j_uri)

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    def _session(self) -> AsyncSession:
        if self._driver is None:
            raise RuntimeError("Neo4jStore.connect() must be called first")
        return self._driver.session(database=self.settings.neo4j_database)

    async def apply_schema(self, statements: list[str]) -> int:
        applied = 0
        async with self._session() as session:
            for stmt in statements:
                await session.run(stmt)
                applied += 1
        return applied

    async def upsert_node(self, node: KGNode) -> KGNode:
        label = node.kind.value
        cypher = f"""
        MERGE (n:{label} {{id: $id}})
        SET n.kind = $kind,
            n.canonical_name = $canonical_name,
            n.aliases = $aliases,
            n.summary = $summary,
            n.properties = $properties,
            n.provenance = $provenance,
            n.pending_review = $pending_review,
            n.created_at = datetime($created_at)
        RETURN n {{ .* , elementId: elementId(n) }} AS node
        """
        params = {
            "id": node.id,
            "kind": node.kind.value,
            "canonical_name": node.canonical_name,
            "aliases": json.dumps(node.aliases),
            "summary": node.summary,
            "properties": json.dumps(node.properties),
            "provenance": _serialize_provenance(node.provenance),
            "pending_review": node.pending_review,
            "created_at": node.created_at.isoformat(),
        }
        async with self._session() as session:
            await session.run(cypher, params)
        return node

    async def upsert_edge(self, edge: KGEdge) -> KGEdge:
        rel = edge.kind.value
        cypher = f"""
        MATCH (src {{id: $src_id}})
        MATCH (dst {{id: $dst_id}})
        MERGE (src)-[r:{rel} {{id: $id}}]->(dst)
        SET r.kind = $kind,
            r.weight = $weight,
            r.properties = $properties,
            r.provenance = $provenance,
            r.chunk_id = $chunk_id
        RETURN r {{ .* }} AS edge
        """
        chunk_id = edge.properties.get("chunk_id") if edge.properties else None
        params = {
            "id": edge.id,
            "kind": edge.kind.value,
            "src_id": edge.src,
            "dst_id": edge.dst,
            "weight": edge.weight,
            "properties": json.dumps(edge.properties),
            "provenance": _serialize_provenance(edge.provenance),
            "chunk_id": chunk_id,
        }
        async with self._session() as session:
            await session.run(cypher, params)
        return edge

    async def get_node(self, node_id: str) -> KGNode | None:
        cypher = """
        MATCH (n {id: $id})
        RETURN n { .* } AS node
        LIMIT 1
        """
        async with self._session() as session:
            result = await session.run(cypher, {"id": node_id})
            record = await result.single()
            if record is None:
                return None
            return _record_to_node(dict(record["node"]))

    async def find_nodes_by_names(
        self,
        names: list[str],
        *,
        kinds: list[NodeKind] | None = None,
    ) -> list[KGNode]:
        if names:
            lowered = [n.lower() for n in names]
            kind_filter = ""
            params: dict[str, Any] = {"names": lowered}
            if kinds:
                kind_filter = "AND n.kind IN $kinds"
                params["kinds"] = [k.value for k in kinds]
            cypher = f"""
            MATCH (n)
            WHERE toLower(n.canonical_name) IN $names {kind_filter}
            RETURN n {{ .* }} AS node
            """
            async with self._session() as session:
                result = await session.run(cypher, params)
                rows = await result.data()
            return [_record_to_node(dict(row["node"])) for row in rows]
        return await self.list_nodes(kinds=kinds)

    async def list_nodes(
        self,
        *,
        kinds: list[NodeKind] | None = None,
        limit: int = 500,
    ) -> list[KGNode]:
        kind_filter = ""
        params: dict[str, Any] = {"limit": limit}
        if kinds:
            kind_filter = "WHERE n.kind IN $kinds"
            params["kinds"] = [k.value for k in kinds]
        cypher = f"""
        MATCH (n)
        {kind_filter}
        RETURN n {{ .* }} AS node
        LIMIT $limit
        """
        async with self._session() as session:
            result = await session.run(cypher, params)
            rows = await result.data()
        return [_record_to_node(dict(row["node"])) for row in rows]

    async def fulltext_search(
        self,
        query: str,
        *,
        k: int,
        kinds: list[NodeKind] | None = None,
    ) -> list[tuple[KGNode, float]]:
        index = "concept_search"
        if kinds and NodeKind.RESOURCE in kinds and len(kinds) == 1:
            index = "resource_search"
        cypher = f"""
        CALL db.index.fulltext.queryNodes('{index}', $query)
        YIELD node, score
        RETURN node {{ .* }} AS node, score
        ORDER BY score DESC
        LIMIT $k
        """
        try:
            async with self._session() as session:
                result = await session.run(cypher, {"query": query, "k": k})
                rows = await result.data()
            return [(_record_to_node(dict(row["node"])), float(row["score"])) for row in rows]
        except Exception:
            # Fallback when fulltext index is unavailable.
            return await self._substring_search(query, k=k, kinds=kinds)

    async def _substring_search(
        self,
        query: str,
        *,
        k: int,
        kinds: list[NodeKind] | None = None,
    ) -> list[tuple[KGNode, float]]:
        q = query.lower()
        kind_filter = ""
        params: dict[str, Any] = {"k": k}
        if kinds:
            kind_filter = "AND n.kind IN $kinds"
            params["kinds"] = [kind.value for kind in kinds]
        cypher = f"""
        MATCH (n)
        WHERE toLower(n.canonical_name) CONTAINS $q
           OR any(a IN coalesce(n.aliases, []) WHERE toLower(a) CONTAINS $q)
           {kind_filter}
        RETURN n {{ .* }} AS node
        LIMIT $k
        """
        params["q"] = q
        async with self._session() as session:
            result = await session.run(cypher, params)
            rows = await result.data()
        return [(_record_to_node(dict(row["node"])), 0.6) for row in rows]

    async def walk(
        self,
        seed_node_ids: list[str],
        *,
        depth: int,
        edge_kinds: list[EdgeKind] | None = None,
        limit: int = 50,
    ) -> list[KGPath]:
        rel_filter = ""
        params: dict[str, Any] = {
            "seeds": seed_node_ids,
            "depth": depth,
            "limit": limit,
        }
        if edge_kinds:
            rel_filter = "WHERE ALL(r IN relationships(p) WHERE type(r) IN $edge_kinds)"
            params["edge_kinds"] = [ek.value for ek in edge_kinds]
        cypher = f"""
        UNWIND $seeds AS seed_id
        MATCH (start {{id: seed_id}})
        CALL {{
            WITH start
            MATCH p = (start)-[*1..$depth]-(n)
            RETURN p
            LIMIT $limit
        }}
        WITH p
        {rel_filter}
        RETURN p
        LIMIT $limit
        """
        paths: list[KGPath] = []
        async with self._session() as session:
            result = await session.run(cypher, params)
            async for record in result:
                path = record["p"]
                nodes = [_record_to_node(dict(n)) for n in path.nodes]
                edges: list[KGEdge] = []
                for rel in path.relationships:
                    edges.append(
                        KGEdge(
                            id=str(rel.element_id),
                            kind=EdgeKind(rel.type),
                            src=rel.start_node["id"],
                            dst=rel.end_node["id"],
                            weight=float(rel.get("weight", 1.0)),
                            properties=dict(rel),
                        )
                    )
                paths.append(KGPath(nodes=nodes, edges=edges, score=0.5))
        return paths

    async def shortest_path(self, src: str, dst: str) -> KGPath | None:
        cypher = """
        MATCH (a {id: $src}), (b {id: $dst})
        MATCH p = shortestPath((a)-[*..6]-(b))
        RETURN p
        LIMIT 1
        """
        async with self._session() as session:
            result = await session.run(cypher, {"src": src, "dst": dst})
            record = await result.single()
            if record is None:
                return None
            path = record["p"]
            nodes = [_record_to_node(dict(n)) for n in path.nodes]
            edges: list[KGEdge] = []
            for rel in path.relationships:
                edges.append(
                    KGEdge(
                        id=str(rel.element_id),
                        kind=EdgeKind(rel.type),
                        src=rel.start_node["id"],
                        dst=rel.end_node["id"],
                        weight=float(rel.get("weight", 1.0)),
                        properties=dict(rel),
                    )
                )
            return KGPath(nodes=nodes, edges=edges, score=0.7)

    async def related_concepts(self, concept_id: str) -> list[KGNode]:
        cypher = """
        MATCH (c:Concept {id: $id})-[r]-(n:Concept)
        WHERE type(r) IN ['PREREQUISITE_OF', 'TEACHES', 'COVERS', 'OPPOSES', 'REQUIRES']
        RETURN DISTINCT n { .* } AS node
        """
        async with self._session() as session:
            result = await session.run(cypher, {"id": concept_id})
            rows = await result.data()
        return [_record_to_node(dict(row["node"])) for row in rows]

    async def prereqs(self, concept_id: str) -> list[KGNode]:
        cypher = """
        MATCH (pre:Concept)-[:PREREQUISITE_OF]->(c:Concept {id: $id})
        RETURN pre { .* } AS node
        ORDER BY pre.canonical_name
        """
        async with self._session() as session:
            result = await session.run(cypher, {"id": concept_id})
            rows = await result.data()
        return [_record_to_node(dict(row["node"])) for row in rows]

    async def learner_touching_nodes(self, learner_id: str) -> set[str]:
        cypher = """
        MATCH (l:Learner {id: $learner_id})-[r]-(n)
        RETURN DISTINCT n.id AS id
        """
        async with self._session() as session:
            result = await session.run(cypher, {"learner_id": learner_id})
            rows = await result.data()
        return {str(row["id"]) for row in rows}

    async def next_topics(self, *, concept_id: str, learner_id: str) -> list[KGNode]:
        cypher = """
        MATCH (c:Concept {id: $concept_id})<-[:PREREQUISITE_OF]-(next:Concept)
        OPTIONAL MATCH (l:Learner {id: $learner_id})-[m:MASTERS]->(next)
        WITH next, coalesce(m.score, 0.0) AS mastery
        WHERE mastery < 0.7
        RETURN next { .* } AS node
        ORDER BY next.canonical_name
        """
        async with self._session() as session:
            result = await session.run(
                cypher,
                {"concept_id": concept_id, "learner_id": learner_id},
            )
            rows = await result.data()
        return [_record_to_node(dict(row["node"])) for row in rows]
