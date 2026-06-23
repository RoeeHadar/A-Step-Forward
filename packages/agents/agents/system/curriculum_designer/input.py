"""Curriculum Designer input schema."""

from __future__ import annotations

from pydantic import BaseModel


class CurriculumDesignerInput(BaseModel):
    learner_id: str
    message: str
    goal: str | None = None
    subject: str | None = None
