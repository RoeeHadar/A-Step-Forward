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


class KGEdge(FlexibleModel):
    source_id: str = ""
    target_id: str = ""
    kind: EdgeKind | str = EdgeKind.RELATED_TO


class KGChunk(FlexibleModel):
    id: str = ""
    text: str = ""


class KGPath(FlexibleModel):
    nodes: list[KGNode] = Field(default_factory=list)
    edges: list[KGEdge] = Field(default_factory=list)


class Extraction(FlexibleModel):
    nodes: list[KGNode] = Field(default_factory=list)
    edges: list[KGEdge] = Field(default_factory=list)


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
