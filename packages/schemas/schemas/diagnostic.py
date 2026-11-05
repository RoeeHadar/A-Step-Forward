from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


class DiagnosticOption(FlexibleModel):
    id: str = ""
    text: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    key: Any = None


class DiagnosticQuestion(FlexibleModel):
    id: str = ""
    prompt: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    difficulty: Any = None
    options: Any = None
    stem: Any = None
    subject: Any = None
    topic: Any = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


class DiagnosticAnswerResponse(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    complete: bool | None = None
    question: Any = None
    question_number: Any = None
    results: dict[str, Any] | None = None
    total_estimate: Any = None


class DiagnosticSessionState(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    completed_at: Any = None
    current_question: Any = None
    learner_id: Any = None
    question_idx: Any = None
    results: Any = None
    session_id: Any = None
    status: Any = None
    topics: Any = None
    total_estimate: Any = None


class DiagnosticStartResponse(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    question: Any = None
    question_number: int | None = None
    session_id: Any = None
    total_estimate: Any = None


class DiagnosticStartRequest(FlexibleModel):
    """AS-90: declared (was flexible_model(); body.topics read in diagnostic service)."""

    topics: Any = None


class DiagnosticAnswerRequest(FlexibleModel):
    """AS-90: declared (was flexible_model(); body.item_id/chosen read in diagnostic service)."""

    chosen: Any = None
    item_id: Any = None
