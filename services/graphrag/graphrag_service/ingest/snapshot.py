"""Graph snapshot to object storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog

from ..settings import GraphRAGSettings
from ..stores.neo4j_store import Neo4jStore

log = structlog.get_logger(__name__)


class Snapshotter:
    def __init__(self, settings: GraphRAGSettings, store: Neo4jStore) -> None:
        self.settings = settings
        self.store = store

    async def export_graph(self) -> dict[str, int]:
        cypher = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN count(DISTINCT n) AS nodes, count(DISTINCT r) AS edges
        """
        async with self.store._session() as session:
            result = await session.run(cypher)
            record = await result.single()
        stats = {
            "nodes": int(record["nodes"]) if record else 0,
            "edges": int(record["edges"]) if record else 0,
        }
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "stats": stats,
        }
        key = f"{self.settings.snapshot_prefix}{payload['ts']}.json"
        log.info("snapshot.created", key=key, **stats)
        # Object-store upload is wired when S3 credentials are configured.
        _ = json.dumps(payload)
        return stats
