"""Diagnostic assessment schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DiagnosticStartRequest(BaseModel):
    topics: list[str] = Field(default_factory=list, min_length=0, max_length=20)


class DiagnosticOption(BaseModel):
    key: str
    text: str


class DiagnosticQuestion(BaseModel):
    id: str
    topic: str
    subject: str
    difficulty: float
    stem: str
    options: list[DiagnosticOption]


class DiagnosticStartResponse(BaseModel):
    session_id: str
    question: DiagnosticQuestion
    question_number: int
    total_estimate: int = 18


class DiagnosticAnswerRequest(BaseModel):
    item_id: str
    chosen: str = Field(min_length=1, max_length=8)


class DiagnosticSessionState(BaseModel):
    session_id: str
    learner_id: str
    status: str
    topics: list[str]
    question_idx: int
    total_estimate: int = 18
    current_question: DiagnosticQuestion | None = None
    results: dict[str, Any] | None = None
    completed_at: datetime | None = None


class DiagnosticAnswerResponse(BaseModel):
    complete: bool = False
    question: DiagnosticQuestion | None = None
    question_number: int | None = None
    total_estimate: int = 18
    results: dict[str, Any] | None = None
