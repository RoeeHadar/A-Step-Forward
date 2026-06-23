"""Seed the curriculum store + enqueue a GraphRAG ingestion."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "curriculum"))

from schemas.curriculum_seed import load_seed_course  # noqa: E402
from curriculum_service.api import get_curriculum_service  # noqa: E402


def _enqueue_graphrag_ingest(course_id: str) -> str:
    try:
        from celery import Celery

        broker = __import__("os").getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
        app = Celery("asf-seed", broker=broker)
        result = app.send_task("workers.jobs.kg_ingest.ingest_curriculum", args=[course_id])
        return result.id
    except Exception as exc:  # pragma: no cover - broker optional in local dev
        return f"skipped ({exc})"


async def _seed(course_id: str) -> int:
    seed_dir = ROOT / "infra" / "seeds" / "courses" / course_id
    bundle = load_seed_course(seed_dir)
    svc = get_curriculum_service()
    course = await svc.upsert_seed(bundle)
    task_id = _enqueue_graphrag_ingest(course.id)
    lesson_count = sum(len(unit.lessons) for unit in course.units)
    print(
        f"[seed] upserted course '{course.id}' "
        f"({len(course.units)} units, {lesson_count} lessons, {len(bundle.concepts)} concepts)"
    )
    print(f"[seed] queued GraphRAG ingest task: {task_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed curriculum into Postgres + queue KG ingest.")
    parser.add_argument("--course", default="foundations-of-math")
    args = parser.parse_args()
    return asyncio.run(_seed(args.course))


if __name__ == "__main__":
    sys.exit(main())
