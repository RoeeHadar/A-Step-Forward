"""Coach agent output schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CoachOutput(BaseModel):
    reply: str
    drill_type: Literal["recall", "application", "mixed"]
    difficulty: Literal["easier", "same", "harder"]
    next_review_hint: str | None = None
    rationale: str = ""
    reps_completed: int = Field(default=0, ge=0)
