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
    tags: list[str] = Field(default_factory=list)
    provenance: Provenance = Field(default_factory=Provenance)


class MemoryUpdateInput(FlexibleModel):
    learner_id: str = ""
    type: MemoryType = MemoryType.SEMANTIC
    content: str = ""


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
