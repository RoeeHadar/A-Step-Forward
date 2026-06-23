"""Tutor agent output schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TutorOutput(BaseModel):
    reply: str
    next_step: Literal["continue", "assess", "next_lesson", "rest"]
    rationale: str = ""
    pinned_memory_writes: list[str] = Field(default_factory=list)
