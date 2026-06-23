"""Shared text-similarity helpers for hygiene (consolidation, conflict detection)."""

from __future__ import annotations

import math
import re
from collections.abc import Iterable

_TOKEN_RE = re.compile(r"[a-z0-9']+")
_NEGATION_RE = re.compile(r"\b(not|never|no longer|doesn't|don't|dislikes|hates|avoid)\b")
_PREFERENCE_RE = re.compile(
    r"\b(?:prefers?|likes?|enjoys?|struggles? with|finds? .+ (?:hard|difficult))\b",
    re.IGNORECASE,
)


def tokenize(text: str) -> set[str]:
    return {m.group(0) for m in _TOKEN_RE.finditer(text.lower()) if len(m.group(0)) > 2}


def jaccard_similarity(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def cosine_similarity_vectors(a: Iterable[float], b: Iterable[float]) -> float:
    av = list(a)
    bv = list(b)
    if len(av) != len(bv) or not av:
        return 0.0
    dot = sum(x * y for x, y in zip(av, bv))
    na = math.sqrt(sum(x * x for x in av))
    nb = math.sqrt(sum(y * y for y in bv))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def has_negation(text: str) -> bool:
    return bool(_NEGATION_RE.search(text.lower()))


def expresses_preference(text: str) -> bool:
    return bool(_PREFERENCE_RE.search(text))


def likely_contradiction(a: str, b: str, *, min_overlap: float = 0.35) -> bool:
    """Heuristic contradiction: high topical overlap with negation asymmetry."""
    overlap = jaccard_similarity(a, b)
    if overlap < min_overlap:
        return False
    neg_a, neg_b = has_negation(a), has_negation(b)
    if neg_a != neg_b:
        return True
    if expresses_preference(a) and expresses_preference(b) and overlap >= 0.5:
        # Same topic, both preference statements — flag for review if content diverges.
        ta, tb = tokenize(a), tokenize(b)
        shared = ta & tb
        unique_a = ta - tb
        unique_b = tb - ta
        if unique_a and unique_b and len(shared) >= 2:
            return True
    return False
