"""Research agent output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import Citation


class ResearchOutput(BaseModel):
    report: str
    citations: list[Citation] = Field(default_factory=list)
    sources_consulted: int = 0
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    rationale: str = ""
