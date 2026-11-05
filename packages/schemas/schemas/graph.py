from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model


class NodeKind(StrEnum):
    CONCEPT = "concept"
    LESSON = "lesson"
    QUESTION = "question"
    SOURCE = "source"


class EdgeKind(StrEnum):
    RELATED_TO = "related_to"
    PREREQUISITE = "prerequisite"
    COVERS = "covers"


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


class Relation(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    confidence: float | None = None
    dst_name: str | None = None
    kind: Any = None
    src_name: str | None = None
