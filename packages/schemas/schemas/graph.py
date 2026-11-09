from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model


class NodeKind(StrEnum):
    # AS-99: restored to the original GraphRAG ontology (1516f4d4). The 01c27b73 stub
    # dropped the members and lowercased the values the graphrag ingest writer,
    # retrieval queries, default service and Neo4j store use (RESOURCE, SKILL, TOPIC,
    # MISCONCEPTION, LEARNER, ...), so ingest raised AttributeError.
    LEARNER = "Learner"
    CONCEPT = "Concept"
    SKILL = "Skill"
    TOPIC = "Topic"
    COURSE = "Course"
    LESSON = "Lesson"
    RESOURCE = "Resource"
    ASSESSMENT = "Assessment"
    QUESTION = "Question"
    MISCONCEPTION = "Misconception"
    GOAL = "Goal"
    EVENT = "Event"
    AGENT = "Agent"
    # Kept from the 01c27b73 stub for compatibility (no readers).
    SOURCE = "source"


class EdgeKind(StrEnum):
    # AS-99: restored (1516f4d4); default_service compares e.kind.value == "PREREQUISITE_OF".
    PREREQUISITE_OF = "PREREQUISITE_OF"
    TEACHES = "TEACHES"
    COVERS = "COVERS"
    MASTERS = "MASTERS"
    STUDIED = "STUDIED"
    TESTS = "TESTS"
    OPPOSES = "OPPOSES"
    REQUIRES = "REQUIRES"
    MENTIONS = "MENTIONS"
    DERIVED_FROM = "DERIVED_FROM"
    # Kept from the 01c27b73 stub for compatibility (RELATED_TO is the KGEdge default).
    RELATED_TO = "related_to"
    PREREQUISITE = "prerequisite"


class KGNode(FlexibleModel):
    id: str = ""
    kind: NodeKind | str = NodeKind.CONCEPT
    # AS-90: fields read in production (was model_extra fallback).
    aliases: Any = None
    canonical_name: Any = None
    created_at: Any = None
    pending_review: Any = None
    properties: Any = None
    provenance: Any = None
    summary: Any = None


class KGEdge(FlexibleModel):
    source_id: str = ""
    target_id: str = ""
    kind: EdgeKind | str = EdgeKind.RELATED_TO
    # AS-90: fields read in production (was model_extra fallback).
    dst: Any = None
    id: Any = None
    properties: Any = None
    provenance: Any = None
    src: Any = None
    weight: Any = None


class KGChunk(FlexibleModel):
    id: str = ""
    text: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    created_at: Any = None
    document_id: Any = None
    embedding: Any = None
    heading: Any = None
    ordinal: Any = None
    provenance: Any = None
    token_count: Any = None


class KGPath(FlexibleModel):
    nodes: list[KGNode] = Field(default_factory=list)
    edges: list[KGEdge] = Field(default_factory=list)
    # AS-90: fields read in production (was model_extra fallback).
    score: float | None = None


class Extraction(FlexibleModel):
    nodes: list[KGNode] = Field(default_factory=list)
    edges: list[KGEdge] = Field(default_factory=list)
    # AS-90: fields read in production (was model_extra fallback).
    claims: list[Any] | None = None
    confidence: Any = None
    entities: Any = None
    notes: Any = None
    relations: Any = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


class Entity(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    confidence: float | None = None
    kind: Any = None
    name: Any = None


class KGHybridInput(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    depth: int | None = None
    k: Any = None
    learner_id: Any = None
    query: Any = None


class KGSearchInput(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    k: Any = None
    query: Any = None
    # AS-110: read in production but never declared (AS-90 runtime guard hit once the
    # read path is exercised). None default == what the model_extra fallback returned;
    # not in AS90_DECLARED (input-only model, never serialized).
    kinds: Any = None


class KGSearchResult(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    node: Any = None
    score: Any = None
    snippet: Any = None


class KGWalkInput(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    depth: Any = None
    limit: Any = None
    seed_node_ids: Any = None
    # AS-110: read in production but never declared (AS-90 runtime guard hit once the
    # read path is exercised). None default == what the model_extra fallback returned;
    # not in AS90_DECLARED (input-only model, never serialized).
    edge_kinds: Any = None


class Relation(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    confidence: float | None = None
    dst_name: str | None = None
    kind: Any = None
    src_name: str | None = None
