"""One-shot curriculum seeder for the `foundations-of-math` course.

Reads `infra/seeds/courses/<course>/` via `schemas.curriculum_seed.load_seed_course`,
then upserts the course → concepts → lessons into the curriculum tables on the
Postgres pointed at by `DATABASE_URL` (asyncpg).

Idempotent: re-runs replace the course's concepts and lessons before
re-inserting, so partial states never linger.

Usage:
    DATABASE_URL=postgresql+asyncpg://... \
        python scripts/seed_curriculum.py [--course foundations-of-math]
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "curriculum"))

from schemas.curriculum_seed import load_seed_course  # noqa: E402

from curriculum_service.settings import CurriculumSettings  # noqa: E402
from curriculum_service.stores.database import session_scope  # noqa: E402
from curriculum_service.stores.repository import CurriculumRepository  # noqa: E402


def _enqueue_graphrag_ingest(course_id: str) -> str:
    """Best-effort enqueue a GraphRAG ingest task. Never fatal."""

    try:
        from celery import Celery  # type: ignore[import-not-found]

        broker = os.getenv("CELERY_BROKER_URL")
        if not broker:
            return "skipped (no CELERY_BROKER_URL)"
        app = Celery("asf-seed", broker=broker)
        result = app.send_task("workers.jobs.kg_ingest.ingest_curriculum", args=[course_id])
        return result.id
    except Exception as exc:
        return f"skipped ({exc.__class__.__name__}: {exc})"


async def _seed(course_id: str) -> int:
    seed_dir = ROOT / "infra" / "seeds" / "courses" / course_id
    if not seed_dir.is_dir():
        print(f"[seed] seed directory not found: {seed_dir}", file=sys.stderr)
        return 2

    bundle = load_seed_course(seed_dir)

    settings = CurriculumSettings()
    repo = CurriculumRepository(settings)
    course = await repo.upsert_seed(bundle)

    async with session_scope(settings) as session:
        from sqlalchemy import func, select

        from curriculum_service.stores.models import (
            CurriculumConcept,
            CurriculumCourse,
            CurriculumLessonIndex,
        )

        course_count = (await session.execute(select(func.count()).select_from(CurriculumCourse))).scalar_one()
        concept_count = (await session.execute(select(func.count()).select_from(CurriculumConcept))).scalar_one()
        lesson_count = (await session.execute(select(func.count()).select_from(CurriculumLessonIndex))).scalar_one()

    seeded_lessons = sum(len(unit.lessons) for unit in course.units)
    print(
        f"[seed] upserted course '{course.id}': "
        f"{len(course.units)} units, {seeded_lessons} lessons, {len(bundle.concepts)} concepts"
    )
    print(
        f"[seed] db row counts: courses={course_count} "
        f"concepts={concept_count} lessons={lesson_count}"
    )
    print(f"[seed] graphrag ingest task: {_enqueue_graphrag_ingest(course.id)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--course",
        default="foundations-of-math",
        help="Course directory under infra/seeds/courses/.",
    )
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        print(
            "[seed] DATABASE_URL is not set. "
            "Set it to a postgresql+asyncpg://... URL before running.",
            file=sys.stderr,
        )
        return 2

    return asyncio.run(_seed(args.course))


if __name__ == "__main__":
    sys.exit(main())
