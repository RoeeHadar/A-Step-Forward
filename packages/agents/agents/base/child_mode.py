"""COPPA-aware child mode policy helpers."""

from __future__ import annotations

import re

COPPA_AGE_THRESHOLD = 13

# Stricter blocked patterns when child_mode is active.
_CHILD_BLOCKED_PATTERNS = [
    re.compile(r"\b(porn|sexual|sex|drug|cocaine|heroin|marijuana)\b", re.IGNORECASE),
    re.compile(r"\b(graphic violence|gore|suicide method)\b", re.IGNORECASE),
    re.compile(r"\b(nude|naked|onlyfans)\b", re.IGNORECASE),
]


def resolve_child_mode(*, age: int | None, child_mode_flag: bool) -> bool:
    """True when COPPA child mode applies (explicit flag or age under 13)."""
    if child_mode_flag:
        return True
    return age is not None and age < COPPA_AGE_THRESHOLD


def child_mode_violation(text: str) -> bool:
    return any(pat.search(text) for pat in _CHILD_BLOCKED_PATTERNS)


def block_third_party_trackers() -> bool:
    """Child mode disables third-party analytics/tracking in the frontend."""
    return True
