"""KG Builder output schema."""

from __future__ import annotations

from pydantic import BaseModel


class KGBuilderOutput(BaseModel):
    reply: str
    entities_extracted: int = 0
    relations_extracted: int = 0
    job_id: str = ""
    rationale: str = ""
