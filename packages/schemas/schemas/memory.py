from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model
from .common import Provenance


class MemoryType(StrEnum):
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
    salience: float | None = None
    confidence: float | None = None
    decay_tau_days: float | None = None
    provenance: Provenance = Field(default_factory=Provenance)
    expires_at: str | None = None


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


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
