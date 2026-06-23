"""Q&A Explainer output schema."""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import Citation


class QAExplainerOutput(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    follow_up_questions: list[str] = Field(default_factory=list)
