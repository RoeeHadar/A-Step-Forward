"""Assessment Generator input schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AssessmentGeneratorInput(BaseModel):
    learner_id: str
    message: str
    objectives: list[str] = Field(default_factory=list)
    format: Literal["quiz", "exercise", "project"] = "quiz"
