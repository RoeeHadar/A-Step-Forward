"""Research agent input schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchInput(BaseModel):
    learner_id: str
    message: str
    depth: str = Field(default="standard", description="brief | standard | deep")
