from __future__ import annotations

from enum import StrEnum
from typing import Any
from datetime import datetime, timezone

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model
from .common import Provenance


class MemoryType(StrEnum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    AFFECTIVE = "affective"
    CONTEXT = "context"
    REFLECTIVE = "reflective"
    SOURCE = "source"


class MemoryAccessPolicy(FlexibleModel):
    read: set[MemoryType] = Field(default_factory=set)
    write: set[MemoryType] = Field(default_factory=set)


class MemoryRecord(FlexibleModel):
    id: str = ""
    learner_id: str = ""
    type: MemoryType = MemoryType.SEMANTIC
    content: str = ""
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    valence: float = 0.0
    # AS-99: defaults restored to the memory table contract (0002_memory_tables:
    # NOT NULL, server_default 0.5 / 0.5 / 14.0; original schema 1516f4d4). None broke
    # consolidation.resolution_key and decay.strength_now.
    salience: float = 0.5
    confidence: float = 0.5
    decay_tau_days: float = 14.0
    provenance: Provenance = Field(default_factory=Provenance)
    expires_at: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: datetime | None = None
    deleted_at: datetime | None = None
    # AS-90: fields read in production (was model_extra fallback).
    access_count: Any = None
    kg_node_ids: Any = None
    superseded_at: Any = None
    superseded_by: Any = None


class MemoryUpdateInput(FlexibleModel):
    learner_id: str = ""
    type: MemoryType = MemoryType.SEMANTIC
    content: str = ""
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    valence: float | None = None
    importance_hint: float | None = None
    provenance: Provenance = Field(default_factory=Provenance)
    expires_at: str | None = None


class MemoryWriteInput(MemoryUpdateInput):
    pass


class MemorySearchInput(FlexibleModel):
    learner_id: str = ""
    query: str = ""
    types: list[MemoryType] = Field(default_factory=list)
    # AS-90: fields read in production (was model_extra fallback).
    agent_id: str | None = None
    k: Any = None
    min_strength: float | None = None
    # AS-110: read in production but never declared (AS-90 runtime guard hit once the
    # read path is exercised). None default == what the model_extra fallback returned;
    # not in AS90_DECLARED (input-only model, never serialized).
    include_archived: Any = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


class CompactionInput(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    messages: list[Any] | None = None
    pinned_memory_ids: Any = None
    target_tokens: Any = None


class CompactionOutput(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    compacted_summary: Any = None
    estimated_tokens: Any = None
    kept_verbatim_count: Any = None
    messages: Any = None


class MemoryConflict(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    existing: Any = None
    incoming: Any = None
    rationale: Any = None
    resolution: Any = None


class MemoryConsolidateResult(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    merged_or_candidates: Any = None


class MemoryDeleteResult(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    deleted: bool | None = None


class MemoryHealthReport(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    conflicts_pending: Any = None
    conflicts_resolved: Any = None
    coverage_gaps: list[Any] | None = None
    drift_notes: list[Any] | None = None
    items_archived: Any = None
    items_merged: Any = None
    items_promoted: Any = None
    items_reviewed: Any = None
    learner_id: Any = None
    window_end: Any = None
    window_start: Any = None


class MemorySearchResult(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    components: dict[str, Any] | None = None
    record: Any = None
    score: Any = None


# ---------------------------------------------------------------------------
# AS-112: entry-point request models. The fields below were required before AS-90
# (3b7d2774 schemas); AS-90 declared them `= None` on the shared models, so an
# omitted field reached the service and crashed (500) instead of a 422. These
# subclasses are used only where untrusted input enters (FastAPI bodies, MCP tool
# signatures, LLM output); they restore the requirement without changing the
# shared models' defaults, the frozen AS90_DECLARED registry or any emitted
# output. Instances are still the base type, so services are unchanged.


class MemorySearchBody(MemorySearchInput):
    """POST /v1/memory/search body and MCP memory.search input (pre-AS-90: agent_id
    required). Internal callers keep using MemorySearchInput."""

    agent_id: str


class CompactionBody(CompactionInput):
    """MCP memory.compact_context input (pre-AS-90: messages, target_tokens required)."""

    messages: list[dict[str, Any]]
    target_tokens: int
