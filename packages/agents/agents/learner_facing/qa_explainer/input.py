"""Q&A Explainer input schema."""

from __future__ import annotations

from pydantic import BaseModel


class QAExplainerInput(BaseModel):
    learner_id: str
    message: str
    topic: str | None = None
