"""Content Curator output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CuratedResource(BaseModel):
    resource_id: str
    title: str
    url: str = ""
    quality_score: float = Field(default=0.8, ge=0.0, le=1.0)
    concept_ids: list[str] = Field(default_factory=list)


class ContentCuratorOutput(BaseModel):
    reply: str
    resources: list[CuratedResource] = Field(default_factory=list)
    rationale: str = ""
