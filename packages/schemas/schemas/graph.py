"""Knowledge graph schemas (GraphRAG)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from ._compat import StrEnum
from .common import ConfidenceScore, IDStr, Provenance


class NodeKind(StrEnum):
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


class EdgeKind(StrEnum):
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


class KGNode(BaseModel):
    id: IDStr
    kind: NodeKind
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    summary: str | None = None
    properties: dict[str, str | int | float | bool] = Field(default_factory=dict)
    provenance: Provenance | None = None
    pending_review: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KGEdge(BaseModel):
    id: IDStr
    kind: EdgeKind
    src: IDStr
    dst: IDStr
    weight: float = 1.0
    properties: dict[str, str | int | float | bool] = Field(default_factory=dict)
    provenance: Provenance | None = None


class KGSearchInput(BaseModel):
    query: str
    k: int = Field(default=10, ge=1, le=200)
    kinds: list[NodeKind] | None = None


class KGWalkInput(BaseModel):
    seed_node_ids: list[IDStr]
    depth: int = Field(default=2, ge=1, le=4)
    edge_kinds: list[EdgeKind] | None = None
    limit: int = Field(default=50, ge=1, le=500)


class KGHybridInput(BaseModel):
    query: str
    k: int = 10
    depth: int = 2
    learner_id: IDStr | None = None


class KGPath(BaseModel):
    nodes: list[KGNode]
    edges: list[KGEdge]
    score: ConfidenceScore = 0.5


class KGSearchResult(BaseModel):
    node: KGNode
    score: ConfidenceScore
    snippet: str | None = None


# Entity extraction (LLM-side)
class Entity(BaseModel):
    name: str
    kind: NodeKind
    aliases: list[str] = Field(default_factory=list)
    description: str | None = None
    confidence: ConfidenceScore = 0.5


class Relation(BaseModel):
    src_name: str
    dst_name: str
    kind: EdgeKind
    weight: float = 1.0
    confidence: ConfidenceScore = 0.5


class Claim(BaseModel):
    statement: str
    supporting_chunk_id: IDStr
    confidence: ConfidenceScore = 0.5


class Extraction(BaseModel):
    entities: list[Entity]
    relations: list[Relation]
    claims: list[Claim] = Field(default_factory=list)
    confidence: ConfidenceScore = 0.5
    notes: Literal["", "low_confidence", "pending_review"] = ""


