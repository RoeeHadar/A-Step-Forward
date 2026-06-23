"""Common reusable types."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

IDStr = Annotated[str, StringConstraints(min_length=1, max_length=128)]
Timestamp = Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]
ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]


class Provenance(BaseModel):
    """Where a piece of data came from."""

    kind: Literal[
        "chat",
        "lesson",
        "assessment",
        "upload",
        "agent_reflection",
        "system",
        "import",
        "verification",
    ]
    id: IDStr | None = None
    agent: str | None = None
    model: str | None = None
    model_version: str | None = None
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Citation(BaseModel):
    """Citation an agent attaches to a claim or generated answer."""

    source_kind: Literal["memory", "kg_node", "kg_chunk", "lesson", "resource", "web"]
    source_id: IDStr
    quote: str | None = None
    score: ConfidenceScore | None = None
