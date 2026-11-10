"""AS-111: the real seed loader (restored from 3b7d2774) and the guarded Course.level reads.

* ``load_seed_course`` on the repo's own seed data (infra/seeds/courses, files only)
  returns the full course tree, as on the ref: 1 course, 3 units, 9 lessons, 8 concepts.
  Loading and walking it records no AS-90 fallback hits.
* The three Course.level reads the AS-110 sweep flagged (curriculum
  stores/repository.py course row insert + upsert, scripts/export_seed_lessons.py) no
  longer crash on a course without a level (built without validation); with a level
  they write the enum value as before.

Fakes only: the repository runs on a recording AsyncSession stand-in; no DB, no network.
"""

from __future__ import annotations

import asyncio
import enum
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _rel in ("packages/schemas", "services/curriculum"):
    _p = str(_ROOT / _rel)
    if _p not in sys.path:
        sys.path.insert(0, _p)

SEED_DIR = _ROOT / "infra" / "seeds" / "courses" / "foundations-of-math"


def _hits(request):
    try:
        return request.getfixturevalue("as90_fallback_hits")
    except pytest.FixtureLookupError:
        return None


def _new_hits(hits, before):
    if hits is None:
        return []
    return sorted(
        f"{c}.{f} {loc}" for (c, f, loc), n in hits.items() if before.get((c, f, loc)) != n
    )


# ------------------------------------------------------------------ seed loader


def test_seed_loader_returns_the_course_tree(request) -> None:
    from schemas.curriculum_seed import load_seed_course

    hits = _hits(request)
    before = dict(hits) if hits is not None else {}
    bundle = load_seed_course(SEED_DIR)
    course = bundle.course
    units = [(u.id, [lesson.id for lesson in u.lessons]) for u in course.units]
    objectives = sum(len(lesson.objectives) for u in course.units for lesson in u.lessons)
    assert (course.id, course.title, course.level.value) == (
        "foundations-of-math",
        "Foundations of Math",
        "beginner",
    )
    assert len(units) == 3
    assert sum(len(ls) for _, ls in units) == 9
    assert len(bundle.concepts) == 8
    assert objectives >= 18  # every ref Lesson needs >= 2 objectives
    assert "lesson-intro-decimals" in {i for _, ls in units for i in ls}
    assert _new_hits(hits, before) == []


def test_seed_loader_rejects_a_missing_dir(tmp_path: Path) -> None:
    from schemas.curriculum_seed import load_seed_course

    with pytest.raises(FileNotFoundError):
        load_seed_course(tmp_path / "missing")


# ------------------------------------------------------- Course.level read sites


class _Level(enum.StrEnum):  # stand-in on trees whose Level is not an enum (the base stub)
    BEGINNER = "beginner"


def _beginner():
    import schemas.curriculum as cur

    level = getattr(cur, "Level", None)
    if isinstance(level, type) and issubclass(level, enum.Enum):
        return level.BEGINNER
    return _Level.BEGINNER


def _course(**level):
    from schemas.curriculum import Course

    if level.get("level") == "BEGINNER":
        level = {"level": _beginner()}

    return Course.model_construct(
        id="course-as111",
        title="T",
        summary="S",
        prerequisites=[],
        units=[],
        resources=[],
        **level,
    )


class _Session:
    def __init__(self) -> None:
        self.stmts: list = []

    async def execute(self, stmt):
        self.stmts.append(stmt)

    async def commit(self):
        return None


def _upsert_course_row(course):
    from curriculum_service.settings import CurriculumSettings
    from curriculum_service.stores.repository import CurriculumRepository
    from sqlalchemy.dialects import postgresql

    session = _Session()
    repo = CurriculumRepository(CurriculumSettings(), session=session)
    asyncio.run(repo.upsert_seed(SimpleNamespace(course=course, concepts=[])))
    stmt = session.stmts[2]  # delete lessons, delete concepts, then the course row
    inserted = stmt.compile(dialect=postgresql.dialect()).params["level"]
    on_conflict = dict(stmt._post_values_clause.update_values_to_set)["level"]
    return inserted, on_conflict


LEVELS = [
    pytest.param({}, None, id="level-missing"),
    pytest.param({"level": None}, None, id="level-None"),
    pytest.param({"level": "BEGINNER"}, "beginner", id="level-beginner"),
]


@pytest.mark.parametrize(("level", "expected"), LEVELS)
def test_repository_course_row_insert_level(level, expected) -> None:
    """stores/repository.py:52 (insert ... values level=)."""
    assert _upsert_course_row(_course(**level))[0] == expected


@pytest.mark.parametrize(("level", "expected"), LEVELS)
def test_repository_course_row_on_conflict_level(level, expected) -> None:
    """stores/repository.py:62 (on_conflict_do_update set_ level)."""
    assert _upsert_course_row(_course(**level))[1] == expected


def _load_export_script():
    spec = importlib.util.spec_from_file_location(
        "as111_export_seed_lessons", _ROOT / "scripts" / "export_seed_lessons.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize(("level", "expected"), LEVELS)
def test_export_script_level(monkeypatch, tmp_path, level, expected) -> None:
    """scripts/export_seed_lessons.py:51 (snapshot course.level)."""
    mod = _load_export_script()
    monkeypatch.setattr(
        mod, "load_seed_course", lambda _d: SimpleNamespace(course=_course(**level), concepts=[])
    )
    out = tmp_path / "snapshot.json"
    monkeypatch.setattr(sys, "argv", ["export_seed_lessons.py", "--out", str(out)])
    assert mod.main() == 0
    assert json.loads(out.read_text())["course"]["level"] == expected


def test_export_script_on_the_real_seed(request, monkeypatch, tmp_path) -> None:
    hits = _hits(request)
    before = dict(hits) if hits is not None else {}
    mod = _load_export_script()
    out = tmp_path / "snapshot.json"
    monkeypatch.setattr(sys, "argv", ["export_seed_lessons.py", "--out", str(out)])
    assert mod.main() == 0
    snap = json.loads(out.read_text())
    assert snap["course"]["level"] == "beginner"
    assert len(snap["course"]["units"]) == 3 and len(snap["lessons"]) == 9
    assert _new_hits(hits, before) == []


def test_repository_upsert_of_the_real_seed(request) -> None:
    from schemas.curriculum_seed import load_seed_course

    hits = _hits(request)
    before = dict(hits) if hits is not None else {}
    bundle = load_seed_course(SEED_DIR)
    from curriculum_service.settings import CurriculumSettings
    from curriculum_service.stores.repository import CurriculumRepository

    session = _Session()
    course = asyncio.run(
        CurriculumRepository(CurriculumSettings(), session=session).upsert_seed(bundle)
    )
    assert course.id == "foundations-of-math"
    # 2 deletes + course row + 8 concepts + 9 lesson-index rows
    assert len(session.stmts) == 2 + 1 + 8 + 9
    assert _new_hits(hits, before) == []
