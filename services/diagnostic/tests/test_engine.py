"""Unit tests for CAT diagnostic engine."""

from diagnostic_service.engine import (
    Response,
    confidence_converged,
    estimate_mastery,
    estimate_mastery_by_topic,
    next_difficulty,
    should_stop,
)


def test_next_difficulty_steps() -> None:
    assert next_difficulty(5.0, True) == 6.0
    assert next_difficulty(5.0, False) == 4.0
    assert next_difficulty(10.0, True) == 10.0
    assert next_difficulty(1.0, False) == 1.0


def test_confidence_converged() -> None:
    responses = [
        Response("1", "algebra", 5.0, True, "A"),
        Response("2", "algebra", 6.0, True, "B"),
        Response("3", "algebra", 7.0, True, "C"),
        Response("4", "algebra", 8.0, True, "D"),
    ]
    assert confidence_converged(responses)


def test_estimate_mastery_weighted() -> None:
    responses = [
        Response("1", "algebra", 10.0, True, "A"),
        Response("2", "algebra", 2.0, False, "B"),
    ]
    score = estimate_mastery(responses)
    assert 0.0 < score < 1.0


def test_should_stop_at_target() -> None:
    responses = [
        Response(str(i), "algebra", 5.0, i % 2 == 0, "A") for i in range(18)
    ]
    assert should_stop(responses)


def test_estimate_mastery_by_topic() -> None:
    responses = [
        Response("1", "algebra", 8.0, True, "A"),
        Response("2", "physics", 4.0, False, "B"),
    ]
    by_topic = estimate_mastery_by_topic(responses)
    assert "algebra" in by_topic
    assert "physics" in by_topic
