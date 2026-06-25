"""Unit tests for learning path plan generation."""

from schemas.learner_model import AdaptiveLearnerProfile, StudentModel

from learning_path_service.engine import (
    chunk_into_weeks,
    collect_weak_worklist,
    infer_subject,
    sort_by_prerequisite_depth,
    build_week_concept_groups,
)


def _student(
    mastery: dict[str, float],
    *,
    subjects: list[str] = ["math"],
    weak: list[str] | None = None,
) -> StudentModel:
    profile = AdaptiveLearnerProfile(
        learner_id="l1",
        goal="Pass Bagrut 5pt Math",
        subjects=subjects,
        hours_per_week=5,
    )
    return StudentModel(
        learner_id="l1",
        profile=profile,
        mastery=mastery,
        weak=weak or [c for c, s in mastery.items() if s < 0.4],
        developing=[c for c, s in mastery.items() if 0.4 <= s <= 0.7],
        strong=[c for c, s in mastery.items() if s > 0.7],
    )


def test_collect_weak_includes_weak_prerequisites() -> None:
    student = _student({"limits": 0.2, "algebra_basics": 0.3, "functions_intro": 0.8})
    prereq_map = {
        "limits": ["functions_intro", "algebra_basics"],
        "functions_intro": ["algebra_basics"],
    }
    worklist = collect_weak_worklist(student, prereq_map)
    assert "limits" in worklist
    assert "algebra_basics" in worklist
    assert "functions_intro" not in worklist


def test_sort_roots_before_branches() -> None:
    concepts = {"limits", "algebra_basics", "functions_intro"}
    prereq_map = {
        "limits": ["functions_intro"],
        "functions_intro": ["algebra_basics"],
        "algebra_basics": [],
    }
    ordered = sort_by_prerequisite_depth(concepts, prereq_map)
    assert ordered.index("algebra_basics") < ordered.index("functions_intro")
    assert ordered.index("functions_intro") < ordered.index("limits")


def test_chunk_into_four_weeks() -> None:
    concepts = [f"concept_{i}" for i in range(12)]
    weeks = chunk_into_weeks(concepts, num_weeks=4)
    assert len(weeks) >= 4
    assert sum(len(w) for w in weeks) == 12


def test_chunk_overflow_adds_extra_week() -> None:
    concepts = [f"concept_{i}" for i in range(25)]
    weeks = chunk_into_weeks(concepts, num_weeks=4, max_per_week=5)
    assert sum(len(w) for w in weeks) == 25


def test_build_week_groups_from_student() -> None:
    student = _student(
        {"limits": 0.2, "derivatives_intro": 0.35, "algebra_basics": 0.25},
        weak=["limits", "derivatives_intro", "algebra_basics"],
    )
    prereq_map = {
        "limits": ["algebra_basics"],
        "derivatives_intro": ["limits"],
        "algebra_basics": [],
    }
    weeks = build_week_concept_groups(student, prereq_map, num_weeks=4)
    assert len(weeks) == 4
    flat = [c for week in weeks for c in week]
    assert "algebra_basics" in flat
    assert flat.index("algebra_basics") < flat.index("limits")


def test_infer_subject_physics_hint() -> None:
    assert infer_subject("kinematics_basics", ["math", "physics"]) == "physics"
    assert infer_subject("algebra_basics", ["math", "physics"]) == "math"
