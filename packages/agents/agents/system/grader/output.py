"""Grader output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GraderOutput(BaseModel):
    reply: str
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    passed: bool | None = None
    rubric_scores: dict[str, float] = Field(default_factory=dict)
    rationale: str = ""
