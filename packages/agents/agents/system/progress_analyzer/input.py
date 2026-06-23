"""Progress Analyzer input schema."""

from __future__ import annotations

from pydantic import BaseModel


class ProgressAnalyzerInput(BaseModel):
    learner_id: str
    message: str
