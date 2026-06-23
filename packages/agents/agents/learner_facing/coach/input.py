"""Coach agent input schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class CoachInput(BaseModel):
    learner_id: str
    message: str
    skill_id: str | None = None
    mode: Literal["drill", "review", "warmup"] = "drill"
