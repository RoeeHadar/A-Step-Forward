"""Content Curator input schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ContentCuratorInput(BaseModel):
    learner_id: str
    message: str
    concept_ids: list[str] = Field(default_factory=list)
