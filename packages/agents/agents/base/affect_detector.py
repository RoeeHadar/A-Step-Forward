"""Detect emotional signals in learner messages and emit adaptation notes."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class AffectSignal(StrEnum):
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    DESPAIR = "despair"
    BORED = "bored"
    ENGAGED = "engaged"
    CELEBRATING = "celebrating"
    NEUTRAL = "neutral"


# Heuristic patterns — extend with LLM classification later
_PATTERNS: list[tuple[AffectSignal, list[str]]] = [
    (AffectSignal.DESPAIR, [
        r"i can'?t do this", r"i'?m stupid", r"i'?ll never", r"\bgive up\b",
        r"אני מוותר", r"אני טיפש", r"לא אצליח", r"לוותר",
    ]),
    (AffectSignal.FRUSTRATED, [
        r"this (is|makes no) sense", r"i don'?t understand",
        r"confus(ed|ing)", r"why (does|is|do|am) (this|it|i)",
        r"(so|really) hard", r"not working",
        r"לא מבין", r"מבולבל", r"קשה לי", r"לא הגיוני",
    ]),
    (AffectSignal.CONFUSED, [
        r"what (do you mean|does that mean)", r"\bhuh\b", r"\bsorry\b",
        r"can you (explain|clarify|repeat)", r"not sure",
        r"מה זה אומר", r"לא בטוח", r"הסבר שוב",
    ]),
    (AffectSignal.CELEBRATING, [
        r"\bi get it\b", r"\bi understand\b", r"\bgot it\b", r"makes sense",
        r"(yes|yay|great|awesome|perfect|finally)",
        r"הבנתי", r"מגניב", r"\bכן\b", r"מעולה",  # noqa: RUF001
    ]),
    (AffectSignal.ENGAGED, [
        r"(interesting|tell me more|what about|how does|why does)",
        r"מעניין", r"ספר לי עוד", r"מה עוד",
    ]),
    (AffectSignal.BORED, [
        r"(boring|this is easy|too easy|i (already )?know this)",
        r"משעמם", r"קל מדי", r"כבר יודע",
    ]),
]


@dataclass
class AffectResult:
    signal: AffectSignal
    confidence: float  # 0-1, heuristic


def detect_affect(message: str) -> AffectResult:
    """Scan ``message`` for heuristic affect signals.

    Returns the first matching signal with confidence 0.7, or NEUTRAL with 1.0.
    DESPAIR and FRUSTRATED patterns are checked before CONFUSED so stronger
    signals take precedence.
    """
    lower = message.lower()
    for signal, patterns in _PATTERNS:
        for pat in patterns:
            if re.search(pat, lower):
                return AffectResult(signal=signal, confidence=0.7)
    return AffectResult(signal=AffectSignal.NEUTRAL, confidence=1.0)
