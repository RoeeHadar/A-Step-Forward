"""Adaptive CAT diagnostic engine."""

from __future__ import annotations

from dataclasses import dataclass

START_DIFFICULTY = 5.0
QUESTIONS_TARGET = 18


@dataclass
class Response:
    item_id: str
    topic: str
    difficulty: float
    correct: bool
    chosen: str


def next_difficulty(current: float, was_correct: bool) -> float:
    if was_correct:
        return min(10.0, current + 1.0)
    return max(1.0, current - 1.0)


def confidence_converged(responses: list[Response]) -> bool:
    if len(responses) < 4:
        return False
    last = [r.correct for r in responses[-4:]]
    return all(last) or not any(last)


def should_stop(responses: list[Response]) -> bool:
    return len(responses) >= QUESTIONS_TARGET or confidence_converged(responses)


def estimate_mastery(responses: list[Response]) -> float:
    if not responses:
        return 0.5
    num = sum(r.difficulty * int(r.correct) for r in responses)
    den = sum(r.difficulty for r in responses)
    return round(num / den, 4) if den else 0.5


def estimate_mastery_by_topic(responses: list[Response]) -> dict[str, float]:
    by_topic: dict[str, list[Response]] = {}
    for response in responses:
        by_topic.setdefault(response.topic, []).append(response)
    return {topic: estimate_mastery(topic_responses) for topic, topic_responses in by_topic.items()}
