"""KG Builder input schema."""

from __future__ import annotations

from pydantic import BaseModel


class KGBuilderInput(BaseModel):
    learner_id: str
    message: str
    source_id: str | None = None
