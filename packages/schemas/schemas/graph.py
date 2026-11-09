from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model
from .common import ConfidenceScore, IDStr


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
    # AS-112: typed (was Any) so dicts are coerced to Entity/Relation instead of
    # reaching the resolver/writer raw. Default stays None (AS90_DECLARED).
    entities: list[Entity] | None = None
    notes: Any = None
    relations: list[Relation] | None = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


class Entity(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    confidence: float | None = None
    kind: Any = None
    name: Any = None
    # AS-116: pre-AS-90 fields, same types and defaults as 3b7d2774 graph.py:101-102.
    # ingest/resolver.py:72-73 reads them; undeclared, they came from the AS-90
    # fallback. Not in AS90_DECLARED: the registry stays frozen, and aliases has
    # a non-None default (like Relation.weight).
    aliases: list[str] = Field(default_factory=list)
    description: str | None = None


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
    # AS-112: read by ingest/writer.py:68 but never declared (AS-90 runtime guard).
    # None == the old model_extra fallback; the writer applies the pre-AS-90 1.0.
    # Not in AS90_DECLARED.
    weight: float | None = None


# ---------------------------------------------------------------------------
# AS-112: entry-point request models. The fields below were required before AS-90
# (3b7d2774 schemas); AS-90 declared them `= None` on the shared models, so an
# omitted field reached the service and crashed (500) instead of a 422. These
# subclasses are used only where untrusted input enters (FastAPI bodies, MCP tool
# signatures, LLM output); they restore the requirement without changing the
# shared models' defaults, the frozen AS90_DECLARED registry or any emitted
# output. Instances are still the base type, so services are unchanged.


class KGSearchBody(KGSearchInput):
    """POST /v1/graphrag/search body and MCP kg.search input (pre-AS-90: query required)."""

    query: str
    # AS-113: pre-AS-90 bound (3b7d2774 graph.py:67).
    k: int = Field(default=10, ge=1, le=200)


class KGHybridBody(KGHybridInput):
    """POST /v1/graphrag/hybrid body and MCP kg.hybrid input (pre-AS-90: query required)."""

    query: str
    # AS-113: pre-AS-90 type (3b7d2774 graph.py:82); k/depth had no bounds there.
    learner_id: IDStr | None = None


class KGWalkBody(KGWalkInput):
    """MCP kg.walk input (pre-AS-90: seed_node_ids required)."""

    # AS-113: pre-AS-90 types and bounds (3b7d2774 graph.py:72-75).
    seed_node_ids: list[IDStr]
    depth: int = Field(default=2, ge=1, le=4)
    limit: int = Field(default=50, ge=1, le=500)


class EntityPayload(Entity):
    """An entity in the LLM extraction JSON (pre-AS-90: name, kind required)."""

    name: str
    kind: NodeKind
    # AS-113: pre-AS-90 type, bound and default (3b7d2774 graph.py:103).
    confidence: ConfidenceScore = 0.5


class RelationPayload(Relation):
    """A relation in the LLM extraction JSON (pre-AS-90: src_name, dst_name, kind required)."""

    src_name: str
    dst_name: str
    kind: EdgeKind
    # AS-113: pre-AS-90 type, bound and default (3b7d2774 graph.py:111).
    confidence: ConfidenceScore = 0.5


class ClaimPayload(__getattr__("Claim")):
    """AS-119: a claim in the LLM extraction JSON (3b7d2774 graph.py:114-117)."""

    statement: str
    supporting_chunk_id: IDStr
    confidence: ConfidenceScore = 0.5


class ExtractionPayload(Extraction):
    """LLM extraction JSON (pre-AS-90: entities, relations required). Unknown kinds or
    missing names are rejected with a ValidationError, as before AS-90."""

    entities: list[EntityPayload]
    relations: list[RelationPayload]
    # AS-113: pre-AS-90 type, bound and default (3b7d2774 graph.py:124).
    confidence: ConfidenceScore = 0.5
    # AS-119: pre-AS-90 type and default (3b7d2774 graph.py:122). Claims are validated
    # and become Claim models instead of staying raw dicts.
    claims: list[ClaimPayload] = Field(default_factory=list)


Extraction.model_rebuild()


# ---------------------------------------------------------------------------
# AS-119: entry-point request models for the remaining pre-AS-90 bounds (3b7d2774).
# Same pattern as AS-112/113: these subclasses are used only where untrusted input
# enters (FastAPI bodies, MCP tool signatures, LLM output). The shared models, their
# defaults and the frozen AS90_DECLARED registry stay unchanged. Instances are still
# the base type, so the services are unchanged.


class KGConceptBody(__getattr__("KGConceptInput")):
    """kg.related_concepts / kg.prereqs MCP input (3b7d2774 graph.py:131-132)."""

    concept_id: IDStr


class KGNextTopicsBody(__getattr__("KGNextTopicsInput")):
    """kg.next_topics MCP input (3b7d2774 graph.py:135-137)."""

    concept_id: IDStr
    learner_id: IDStr


class KGExplainPathBody(__getattr__("KGExplainPathInput")):
    """kg.explain_path MCP input (3b7d2774 graph.py:140-142)."""

    src: IDStr
    dst: IDStr


class KGPersonalizedBody(__getattr__("KGPersonalizedInput")):
    """kg.personalized MCP input (3b7d2774 graph.py:145-148)."""

    learner_id: IDStr
    query: str = Field(min_length=1, max_length=2000)
    k: int = Field(default=10, ge=1, le=200)
