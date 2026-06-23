"""Memory schemas — shared between the Memory Service, agents, MCP, and API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from ._compat import StrEnum
from .common import Citation, ConfidenceScore, IDStr, Provenance


class MemoryType(StrEnum):
    """The eight memory types. See PLAN.md §5.1."""

    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    AFFECTIVE = "affective"
    CONTEXT = "context"
    REFLECTIVE = "reflective"
    SOURCE = "source"


class MemoryAccessPolicy(BaseModel):
    """Per-agent policy declaring which memory types may be read/written."""

    read: set[MemoryType] = Field(default_factory=set)
    write: set[MemoryType] = Field(default_factory=set)


class MemoryRecord(BaseModel):
    """Persisted memory row (the contract returned by reads)."""

    id: IDStr
    learner_id: IDStr
    type: MemoryType
    content: str
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)

    salience: ConfidenceScore = 0.5
    confidence: ConfidenceScore = 0.5
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    decay_tau_days: float = 14.0
    last_accessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0

    superseded_by: IDStr | None = None
    superseded_at: datetime | None = None

    provenance: Provenance
    kg_node_ids: list[IDStr] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: datetime | None = None
    deleted_at: datetime | None = None
    expires_at: datetime | None = None


class MemoryWriteInput(BaseModel):
    """Input passed to MemoryService.write() and the memory.write MCP tool."""

    learner_id: IDStr
    type: MemoryType
    content: str = Field(min_length=1, max_length=20_000)
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    valence: float | None = Field(default=None, ge=-1.0, le=1.0)
    importance_hint: ConfidenceScore | None = None
    expires_at: datetime | None = None
    provenance: Provenance


class MemorySearchInput(BaseModel):
    """Input for hybrid memory retrieval."""

    learner_id: IDStr
    query: str = Field(min_length=1, max_length=2000)
    types: set[MemoryType] | None = None
    k: int = Field(default=10, ge=1, le=200)
    agent_id: str
    include_archived: bool = False
    min_strength: ConfidenceScore = 0.0


class MemorySearchResult(BaseModel):
    """A ranked retrieval result."""

    record: MemoryRecord
    score: ConfidenceScore
    components: dict[str, float] = Field(default_factory=dict)
    citation: Citation | None = None


class MemoryUpdateInput(BaseModel):
    """Patch a memory (e.g., learner correction)."""

    content: str | None = None
    summary: str | None = None
    tags: list[str] | None = None
    salience: ConfidenceScore | None = None
    confidence: ConfidenceScore | None = None
    reason: str = Field(min_length=1, max_length=500)


class MemoryConflict(BaseModel):
    """Conflict between an incoming and existing memory."""

    incoming: MemoryRecord
    existing: MemoryRecord
    resolution: Literal["incoming_supersedes", "existing_supersedes", "kept_both_for_review"]
    rationale: str


class MemoryHealthReport(BaseModel):
    """Emitted by the Dreamer after a consolidation pass."""

    learner_id: IDStr
    window_start: datetime
    window_end: datetime
    items_reviewed: int
    items_promoted: int
    items_archived: int
    items_merged: int
    conflicts_resolved: int
    conflicts_pending: int
    coverage_gaps: list[str] = Field(default_factory=list)
    drift_notes: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompactionInput(BaseModel):
    """Inputs to context-window compaction (orchestrator helper)."""

    messages: list[dict]
    pinned_memory_ids: list[IDStr] = Field(default_factory=list)
    target_tokens: int = Field(ge=512)


class CompactionOutput(BaseModel):
    """Output of context-window compaction."""

    messages: list[dict]
    compacted_summary: str
    kept_verbatim_count: int
    estimated_tokens: int


