"""Export the foundations-of-math seed as a JSON snapshot for the frontend.

Reads `infra/seeds/courses/<course>/` via `schemas.curriculum_seed.load_seed_course`
and writes a flat JSON snapshot to `apps/web/src/lib/seed-lessons.generated.json`.
The web app uses the snapshot as the offline fallback for `/lessons/<lessonId>`
so the live demo stays usable even when the backend is unreachable.

Re-run after editing the YAML/Markdown seeds:

    python scripts/export_seed_lessons.py [--course foundations-of-math]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))

from schemas.curriculum_seed import load_seed_course  # noqa: E402

OUTPUT = ROOT / "apps" / "web" / "src" / "lib" / "seed-lessons.generated.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course", default="foundations-of-math")
    parser.add_argument("--out", default=str(OUTPUT))
    args = parser.parse_args()

    seed_dir = ROOT / "infra" / "seeds" / "courses" / args.course
    bundle = load_seed_course(seed_dir)

    lessons: list[dict] = []
    for unit in bundle.course.units:
        for lesson in unit.lessons:
            payload = lesson.model_dump(mode="json")
            payload["course_id"] = bundle.course.id
            payload["course_title"] = bundle.course.title
            payload["unit_id"] = unit.id
            payload["unit_title"] = unit.title
            lessons.append(payload)

    snapshot = {
        "course": {
            "id": bundle.course.id,
            "title": bundle.course.title,
            "level": bundle.course.level.value,
            "summary": bundle.course.summary,
            "units": [
                {
                    "id": unit.id,
                    "title": unit.title,
                    "summary": unit.summary,
                    "lesson_ids": [lesson.id for lesson in unit.lessons],
                }
                for unit in bundle.course.units
            ],
        },
        "lessons": lessons,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[export] wrote {len(lessons)} lessons to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
