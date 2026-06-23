"""Curriculum Designer output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CurriculumDesignerOutput(BaseModel):
    reply: str
    path_id: str
    milestones: list[str] = Field(default_factory=list)
    estimated_weeks: int = Field(default=4, ge=1)
    rationale: str = ""
