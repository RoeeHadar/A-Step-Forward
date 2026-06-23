"""Tutor agent input schema."""

from __future__ import annotations

from pydantic import BaseModel


class TutorInput(BaseModel):
    learner_id: str
    message: str
    lesson_id: str | None = None
