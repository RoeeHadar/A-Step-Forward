"""Assessment Generator output schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AssessmentGeneratorOutput(BaseModel):
    reply: str
    assessment_id: str
    item_count: int = Field(default=5, ge=1)
    format: Literal["quiz", "exercise", "project"]
    rationale: str = ""
