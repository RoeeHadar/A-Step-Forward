"""Importance scoring — heuristic features with optional LLM-judge hook."""

from __future__ import annotations

import re

from ..settings import MemorySettings

_KEYWORDS_HIGH = (
    "goal",
    "midterm",
    "exam",
    "deadline",
    "important",
    "remember",
    "favorite",
    "prefer",
    "struggle",
    "stuck",
    "misconception",
    "mastered",
    "breakthrough",
)
_EMOTION_MARKERS = ("frustrated", "excited", "anxious", "confident", "bored", "motivated")
_EXPLICIT_IMPORTANCE = re.compile(r"\b(?:important|remember this|don't forget|key point)\b", re.IGNORECASE)


def heuristic_score(text: str) -> float:
    text_lower = text.lower()
    keyword_hits = sum(1 for kw in _KEYWORDS_HIGH if kw in text_lower)
    emotion_hits = sum(1 for kw in _EMOTION_MARKERS if kw in text_lower)
    explicit = 0.15 if _EXPLICIT_IMPORTANCE.search(text) else 0.0
    length_bonus = min(len(text) / 800.0, 0.25)
    question_bonus = 0.05 if "?" in text else 0.0
    raw = 0.25 + 0.08 * keyword_hits + 0.05 * emotion_hits + length_bonus + explicit + question_bonus
    return min(1.0, max(0.05, raw))


def decay_tau_for_importance(importance: float, *, base_tau: float) -> float:
    """Higher-importance memories decay more slowly."""
    return max(3.0, base_tau * (1.0 + importance))


async def llm_judge_score(text: str) -> float | None:
    """Optional LLM-judge stage. Returns None when disabled or unavailable."""
    # Wired to packages/agents LLM helper in a follow-up; hygiene stays offline-testable.
    _ = text
    return None


async def score_importance(
    text: str,
    *,
    hint: float | None = None,
    settings: MemorySettings | None = None,
) -> float:
    cfg = settings or MemorySettings()
    base = heuristic_score(text)
    if hint is not None:
        base = 0.6 * base + 0.4 * min(1.0, max(0.0, hint))
    if cfg.llm_judge_enabled:
        judged = await llm_judge_score(text)
        if judged is not None:
            base = 0.7 * base + 0.3 * judged
    return round(min(1.0, max(0.05, base)), 4)
