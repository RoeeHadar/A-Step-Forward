"""Curriculum schema tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas.curriculum import Assessment, AssessmentType, Question, QuestionType
from schemas.curriculum_seed import load_seed_course

ROOT = Path(__file__).resolve().parents[3]
SEED_DIR = ROOT / "infra" / "seeds" / "courses" / "foundations-of-math"


def test_mcq_requires_choices() -> None:
    with pytest.raises(ValidationError):
        Question(id="q1", stem="Pick one", type=QuestionType.MCQ)


def test_load_foundations_of_math_seed() -> None:
    bundle = load_seed_course(SEED_DIR)
    course = bundle.course
    assert course.id == "foundations-of-math"
    assert len(course.units) == 3
    assert sum(len(unit.lessons) for unit in course.units) == 9
    assert sum(len(unit.assessments) for unit in course.units) == 3
    assert len(course.resources) == 5
    assert len(bundle.concepts) == 8
    lesson_ids = [lesson.id for unit in course.units for lesson in unit.lessons]
    assert "lesson-fractions-intro" in lesson_ids


def test_assessment_type_enum() -> None:
    assessment = Assessment(
        id="a1",
        type=AssessmentType.QUIZ,
        title="Quiz",
        rubric="Full credit for correct answers.",
    )
    assert assessment.type == AssessmentType.QUIZ
