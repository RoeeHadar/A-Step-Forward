"""Grader input schema."""

from __future__ import annotations

from pydantic import BaseModel


class GraderInput(BaseModel):
    learner_id: str
    message: str
    submission: str | None = None
    rubric_id: str | None = None
