from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleModel, flexible_model


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
