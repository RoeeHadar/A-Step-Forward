#!/usr/bin/env python3
"""Idempotent Neo4j seed for prerequisite knowledge-graph YAML files.

Reads `content/knowledge-graph/*.yaml` and MERGEs Concept nodes plus
PREREQUISITE_OF edges. Safe to re-run after YAML updates.

Usage:
    uv run python scripts/seed_knowledge_graph.py
    uv run python scripts/seed_knowledge_graph.py --dry-run
    make seed-kg
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
KG_ROOT = ROOT / "content" / "knowledge-graph"

sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))


def _configure_env() -> None:
    os.environ.setdefault("USE_NEO4J", "true")
    uri = os.environ.get("NEO4J_URI", "")
    if uri and "databases.neo4j.io" in uri and "NEO4J_USER" not in os.environ:
        instance_id = uri.split("://")[1].split(".")[0]
        os.environ.setdefault("NEO4J_USER", instance_id)
        os.environ.setdefault("NEO4J_DATABASE", instance_id)


def _node_id(concept_id: str) -> str:
    return f"c:{concept_id}"


def _load_graph_files() -> list[dict]:
    graphs: list[dict] = []
    for path in sorted(KG_ROOT.glob("*.yaml")):
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data or "concepts" not in data:
            continue
        data["_source"] = path.name
        graphs.append(data)
    return graphs


async def seed(*, dry_run: bool = False) -> dict[str, int]:
    from graphrag_service.ontology import (
        CYPHER_CONSTRAINTS,
        CYPHER_FULLTEXT_INDEXES,
        CYPHER_INDEXES,
    )
    from graphrag_service.settings import GraphRAGSettings
    from graphrag_service.stores.neo4j_store import Neo4jStore
    from schemas.graph import EdgeKind, KGEdge, KGNode, NodeKind

    graphs = _load_graph_files()
    if not graphs:
        raise FileNotFoundError(f"No YAML files found under {KG_ROOT}")

    concept_count = 0
    edge_count = 0
    files = len(graphs)

    if dry_run:
        for graph in graphs:
            subject = graph.get("subject", "unknown")
            level = graph.get("level", "unknown")
            concepts = graph["concepts"]
            print(f"[dry-run] {graph['_source']}: {len(concepts)} concepts ({subject}/{level})")
            concept_count += len(concepts)
            for c in concepts:
                edge_count += len(c.get("prerequisites") or [])
        return {"files": files, "concepts": concept_count, "edges": edge_count}

    settings = GraphRAGSettings()
    if not settings.use_neo4j:
        raise RuntimeError("USE_NEO4J must be true and NEO4J_URI set")

    store = Neo4jStore(settings)
    await store.apply_schema(CYPHER_CONSTRAINTS + CYPHER_INDEXES + CYPHER_FULLTEXT_INDEXES)

    for graph in graphs:
        subject = str(graph.get("subject", "unknown"))
        level = str(graph.get("level", "unknown"))
        for concept in graph["concepts"]:
            cid = str(concept["id"])
            node = KGNode(
                id=_node_id(cid),
                kind=NodeKind.CONCEPT,
                canonical_name=cid,
                summary=str(concept.get("name", cid)),
                properties={
                    "name": str(concept.get("name", cid)),
                    "name_he": str(concept.get("name_he", "")),
                    "subject": subject,
                    "level": level,
                },
            )
            await store.upsert_node(node)
            concept_count += 1

        for concept in graph["concepts"]:
            dst_id = _node_id(str(concept["id"]))
            for prereq in concept.get("prerequisites") or []:
                src_id = _node_id(str(prereq))
                edge = KGEdge(
                    id=f"e:{prereq}_pre_{concept['id']}",
                    kind=EdgeKind.PREREQUISITE_OF,
                    src=src_id,
                    dst=dst_id,
                    weight=1.0,
                )
                await store.upsert_edge(edge)
                edge_count += 1

    await store.close()
    return {"files": files, "concepts": concept_count, "edges": edge_count}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Neo4j prerequisite graph from YAML")
    parser.add_argument("--dry-run", action="store_true", help="Print counts without writing")
    args = parser.parse_args()

    _configure_env()
    stats = asyncio.run(seed(dry_run=args.dry_run))
    print(
        f"seed_knowledge_graph: {stats['files']} files, "
        f"{stats['concepts']} concepts, {stats['edges']} prerequisite edges"
    )


if __name__ == "__main__":
    main()
