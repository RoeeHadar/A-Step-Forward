"""Progress Analyzer output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProgressAnalyzerOutput(BaseModel):
    reply: str
    gaps: list[str] = Field(default_factory=list)
    at_risk: bool = False
    interventions: list[str] = Field(default_factory=list)
    rationale: str = ""
