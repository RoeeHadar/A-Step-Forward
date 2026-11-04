"""AS-89: schemas.learner_model mastery helpers must be real functions, not dynamic models."""

from __future__ import annotations

import inspect

from schemas.learner_model import classify_mastery, self_score_to_mastery


def test_helpers_are_functions() -> None:
    assert inspect.isfunction(self_score_to_mastery)
    assert inspect.isfunction(classify_mastery)


def test_self_score_to_mastery_range_and_clamp() -> None:
    assert self_score_to_mastery(1) == 0.1
    assert self_score_to_mastery(10) == 0.9
    assert self_score_to_mastery(0) == 0.1
    assert self_score_to_mastery(42) == 0.9


def test_classify_mastery_buckets() -> None:
    weak, dev, strong = classify_mastery({"a": 0.1, "b": 0.4, "c": 0.7, "d": 0.71})
    assert (weak, dev, strong) == (["a"], ["b", "c"], ["d"])
