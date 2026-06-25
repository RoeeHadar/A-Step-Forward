"""Unit tests for quiz scoring and plan adaptation logic."""

from __future__ import annotations

import pytest

from schemas.learning_path import QuizAnswerItem, QuizOption, StoredQuizItem


def _make_item(item_id: str, topic: str, correct: str = "B") -> StoredQuizItem:
    return StoredQuizItem(
        id=item_id,
        topic=topic,
        subject="math",
        difficulty=5.0,
        stem=f"Question about {topic}?",
        options=[
            QuizOption(key="A", text="Wrong answer"),
            QuizOption(key="B", text="Correct answer"),
            QuizOption(key="C", text="Another wrong answer"),
            QuizOption(key="D", text="Yet another wrong answer"),
        ],
        correct=correct,
        source="bank",
    )


def _score(items, answers):
    from learning_path_service.stores.quiz_repository import _score_answers

    answer_list = [
        QuizAnswerItem(item_id=item_id, chosen=chosen)
        for item_id, chosen in answers.items()
    ]
    return _score_answers(items, answer_list)


class TestScoreAnswers:
    def test_perfect_score(self):
        items = [_make_item("q1", "algebra"), _make_item("q2", "algebra")]
        overall, per_topic, weak = _score(items, {"q1": "B", "q2": "B"})
        assert overall == 1.0
        assert per_topic["algebra"] == 1.0
        assert weak == []

    def test_zero_score(self):
        items = [_make_item("q1", "calculus"), _make_item("q2", "calculus")]
        overall, per_topic, weak = _score(items, {"q1": "A", "q2": "A"})
        assert overall == 0.0
        assert per_topic["calculus"] == 0.0
        assert "calculus" in weak

    def test_partial_score(self):
        items = [
            _make_item("q1", "geometry"),
            _make_item("q2", "geometry"),
            _make_item("q3", "geometry"),
            _make_item("q4", "geometry"),
        ]
        # 2 correct out of 4
        overall, per_topic, weak = _score(items, {"q1": "B", "q2": "B", "q3": "A", "q4": "A"})
        assert overall == pytest.approx(0.5)
        assert per_topic["geometry"] == pytest.approx(0.5)
        # 0.5 >= 0.4 threshold, so not weak
        assert weak == []

    def test_multiple_topics(self):
        items = [
            _make_item("q1", "algebra"),
            _make_item("q2", "algebra"),
            _make_item("q3", "calculus"),
            _make_item("q4", "calculus"),
        ]
        # algebra: 1/2 correct, calculus: 0/2 correct
        overall, per_topic, weak = _score(
            items, {"q1": "B", "q2": "A", "q3": "A", "q4": "C"}
        )
        assert per_topic["algebra"] == pytest.approx(0.5)
        assert per_topic["calculus"] == 0.0
        assert "calculus" in weak
        assert "algebra" not in weak

    def test_missing_answer_counts_as_wrong(self):
        items = [_make_item("q1", "trigonometry"), _make_item("q2", "trigonometry")]
        # Only q1 answered
        overall, per_topic, weak = _score(items, {"q1": "B"})
        assert per_topic["trigonometry"] == pytest.approx(0.5)

    def test_empty_items(self):
        overall, per_topic, weak = _score([], {})
        assert overall == 0.0
        assert per_topic == {}
        assert weak == []

    def test_correct_key_case_insensitive(self):
        items = [_make_item("q1", "vectors", correct="B")]
        overall, per_topic, weak = _score(items, {"q1": "b"})
        assert overall == 1.0

    def test_adapt_trigger_threshold(self):
        """More than 2 weak concepts → plan should be adapted."""
        topics = ["algebra", "calculus", "geometry", "trigonometry"]
        items = [_make_item(f"q{i}", topic) for i, topic in enumerate(topics)]
        # All wrong → all 4 topics weak
        overall, per_topic, weak = _score(
            items, {f"q{i}": "A" for i in range(len(topics))}
        )
        assert len(weak) > 2  # triggers adapt_trigger_min


class TestBankItemConversion:
    def test_valid_conversion(self):
        from learning_path_service.quiz_generator import _bank_row_to_stored_item

        class FakeRow(dict):
            pass

        row = FakeRow(
            id="abc-123",
            topic="linear_equations",
            subject="math",
            difficulty=4.0,
            stem="Which of these is a linear equation?",
            options={
                "choices": ["y=x²", "y=2x+3", "y=1/x", "y=√x"],
                "correct": "B",
            },
        )
        item = _bank_row_to_stored_item(row)
        assert item is not None
        assert item.correct == "B"
        assert item.options[1].key == "B"
        assert item.options[1].text == "y=2x+3"

    def test_invalid_row_returns_none(self):
        from learning_path_service.quiz_generator import _bank_row_to_stored_item

        row = {"id": "x", "topic": "t", "subject": "s", "difficulty": 1.0, "stem": "", "options": {}}
        result = _bank_row_to_stored_item(row)
        assert result is None
