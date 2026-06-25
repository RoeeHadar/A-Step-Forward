"""Core weekly plan generation logic."""

from __future__ import annotations

from schemas.learner_model import StudentModel

WEAK_THRESHOLD = 0.4
NUM_WEEKS = 4
MIN_CONCEPTS_PER_WEEK = 3
MAX_CONCEPTS_PER_WEEK = 5

PHYSICS_HINTS = frozenset(
    {
        "kinematics",
        "dynamics",
        "electricity",
        "magnetism",
        "waves",
        "optics",
        "nuclear",
        "momentum",
        "energy",
        "newton",
        "rotation",
    }
)


def humanize_concept_id(concept_id: str) -> str:
    return concept_id.replace("_", " ").replace("-", " ").strip().title()


def infer_subject(concept_id: str, subjects: list[str]) -> str:
    if not subjects:
        return "math"
    if len(subjects) == 1:
        return subjects[0]
    lower = concept_id.lower()
    if any(hint in lower for hint in PHYSICS_HINTS):
        return "physics" if "physics" in subjects else subjects[0]
    return "math" if "math" in subjects else subjects[0]


def collect_weak_worklist(
    student: StudentModel,
    prerequisite_map: dict[str, list[str]],
    *,
    weak_threshold: float = WEAK_THRESHOLD,
) -> set[str]:
    mastery = dict(student.mastery)
    weak: set[str] = set(student.weak)
    for concept_id, score in mastery.items():
        if score < weak_threshold:
            weak.add(concept_id)

    worklist: set[str] = set(weak)
    for concept in weak:
        for prereq in prerequisite_map.get(concept, []):
            if mastery.get(prereq, 0.5) < weak_threshold:
                worklist.add(prereq)

    if not worklist:
        if student.profile and student.profile.self_scores:
            worklist = set(student.profile.self_scores.keys())
        elif student.profile and student.profile.subjects:
            worklist = {f"{student.profile.subjects[0]}_basics"}

    return worklist


def _depth(
    concept: str,
    prereq_map: dict[str, list[str]],
    universe: set[str],
    memo: dict[str, int],
    visiting: set[str] | None = None,
) -> int:
    if visiting is None:
        visiting = set()
    if concept in memo:
        return memo[concept]
    if concept in visiting:
        memo[concept] = 0
        return 0
    visiting.add(concept)
    prereqs = [p for p in prereq_map.get(concept, []) if p in universe]
    if not prereqs:
        memo[concept] = 0
        visiting.remove(concept)
        return 0
    value = max(_depth(p, prereq_map, universe, memo, visiting) for p in prereqs) + 1
    visiting.remove(concept)
    memo[concept] = value
    return value


def sort_by_prerequisite_depth(
    concepts: set[str],
    prerequisite_map: dict[str, list[str]],
) -> list[str]:
    """Roots (fewer prerequisites) first so learners study foundations before branches."""
    memo: dict[str, int] = {}
    return sorted(concepts, key=lambda c: (_depth(c, prerequisite_map, concepts, memo), c))


def chunk_into_weeks(
    concepts: list[str],
    *,
    num_weeks: int = NUM_WEEKS,
    min_per_week: int = MIN_CONCEPTS_PER_WEEK,
    max_per_week: int = MAX_CONCEPTS_PER_WEEK,
) -> list[list[str]]:
    if not concepts:
        return [[] for _ in range(num_weeks)]

    weeks: list[list[str]] = [[] for _ in range(num_weeks)]
    week_idx = 0
    for concept in concepts:
        placed = False
        for _ in range(len(weeks)):
            if len(weeks[week_idx]) < max_per_week:
                weeks[week_idx].append(concept)
                placed = True
                week_idx = (week_idx + 1) % len(weeks)
                break
            week_idx = (week_idx + 1) % len(weeks)
        if not placed:
            weeks.append([concept])

    while len(weeks) < num_weeks:
        weeks.append([])

    return weeks


def build_week_concept_groups(
    student: StudentModel,
    prerequisite_map: dict[str, list[str]],
    *,
    num_weeks: int = NUM_WEEKS,
    weak_threshold: float = WEAK_THRESHOLD,
) -> list[list[str]]:
    worklist = collect_weak_worklist(student, prerequisite_map, weak_threshold=weak_threshold)
    ordered = sort_by_prerequisite_depth(worklist, prerequisite_map)
    return chunk_into_weeks(ordered, num_weeks=num_weeks)
