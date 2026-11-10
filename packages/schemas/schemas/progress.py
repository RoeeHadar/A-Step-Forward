from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model
from .common import ConfidenceScore, IDStr


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


class KnowledgeGaps(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    gaps: list[Any] | None = None
    learner_id: Any = None


class MasteryEntry(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    concept_id: str | None = None
    concept_title: str | None = None
    score: float | None = None


class ProgressSummary(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    learner_id: Any = None
    mastery: list[Any] | None = None
    next_review_at: Any = None
    streak_days: int | None = None


class StreakInfo(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    learner_id: Any = None
    next_review_at: Any = None
    streak_days: int | None = None


class UpdateMasteryResult(FlexibleModel):
    """AS-90: declared (was flexible_model(); fields read/set in production)."""

    entry: Any = None
    updated: bool | None = None


# ---------------------------------------------------------------------------
# AS-119: entry-point request models for the remaining pre-AS-90 bounds (3b7d2774).
# Same pattern as AS-112/113: these subclasses are used only where untrusted input
# enters (FastAPI bodies, MCP tool signatures, LLM output). The shared models, their
# defaults and the frozen AS90_DECLARED registry stay unchanged. Instances are still
# the base type, so the services are unchanged.


class LearnerRefBody(__getattr__("LearnerRefInput")):
    """progress.snapshot / gaps / streak MCP input (3b7d2774 progress.py:31-32)."""

    learner_id: IDStr


class UpdateMasteryBody(__getattr__("UpdateMasteryInput")):
    """progress.update_mastery MCP input (3b7d2774 progress.py:35-38)."""

    learner_id: IDStr
    concept_id: IDStr
    score: ConfidenceScore
