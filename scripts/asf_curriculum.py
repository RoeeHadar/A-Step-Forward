"""Educator-facing curriculum authoring CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "infra" / "seeds" / "courses"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"[asf curriculum] wrote {path.relative_to(ROOT)}")


def cmd_new_course(args: argparse.Namespace) -> int:
    course_dir = SEEDS / args.course_id
    if course_dir.exists():
        print(f"[asf curriculum] course already exists: {course_dir}")
        return 1
    _write(
        course_dir / "course.yaml",
        "\n".join(
            [
                f"id: {args.course_id}",
                f"title: {args.title}",
                f"level: {args.level}",
                "summary: TODO — describe this course.",
                "prerequisites: []",
                "units: []",
                "",
            ]
        ),
    )
    _write(course_dir / "concepts.yaml", "concepts: []\n")
    (course_dir / "resources").mkdir(parents=True, exist_ok=True)
    (course_dir / "units").mkdir(parents=True, exist_ok=True)
    return 0


def cmd_new_unit(args: argparse.Namespace) -> int:
    unit_dir = SEEDS / args.course_id / "units" / args.unit_id
    if unit_dir.exists():
        print(f"[asf curriculum] unit already exists: {unit_dir}")
        return 1
    _write(
        unit_dir / "unit.yaml",
        "\n".join(
            [
                f"id: {args.unit_id}",
                f"title: {args.title}",
                "summary: TODO — describe this unit.",
                "objectives: []",
                "lessons: []",
                "assessments: []",
                "",
            ]
        ),
    )
    (unit_dir / "lessons").mkdir(parents=True, exist_ok=True)
    (unit_dir / "assessments").mkdir(parents=True, exist_ok=True)

    course_yaml = SEEDS / args.course_id / "course.yaml"
    if course_yaml.exists():
        text = course_yaml.read_text(encoding="utf-8")
        if "units:" in text and args.unit_id not in text:
            updated = text.rstrip() + f"\n  - {args.unit_id}\n"
            course_yaml.write_text(updated, encoding="utf-8")
            print(f"[asf curriculum] appended unit to {course_yaml.relative_to(ROOT)}")
    return 0


def cmd_new_lesson(args: argparse.Namespace) -> int:
    lesson_path = (
        SEEDS / args.course_id / "units" / args.unit_id / "lessons" / f"{args.lesson_id}.md"
    )
    if lesson_path.exists():
        print(f"[asf curriculum] lesson already exists: {lesson_path}")
        return 1
    _write(
        lesson_path,
        "\n".join(
            [
                "---",
                f"id: {args.lesson_id}",
                f"title: {args.title}",
                f"modality: {args.modality}",
                "est_minutes: 15",
                "objectives:",
                "  - id: obj-todo-1",
                "    statement: TODO — first objective.",
                "    blooms_level: understand",
                "    concepts: [concept-todo]",
                "  - id: obj-todo-2",
                "    statement: TODO — second objective.",
                "    blooms_level: apply",
                "    concepts: [concept-todo]",
                "concepts: [concept-todo]",
                "resources: []",
                "---",
                f"# {args.title}",
                "",
                "TODO — lesson body in Markdown.",
                "",
            ]
        ),
    )

    unit_yaml = SEEDS / args.course_id / "units" / args.unit_id / "unit.yaml"
    if unit_yaml.exists():
        text = unit_yaml.read_text(encoding="utf-8")
        if "lessons:" in text and args.lesson_id not in text:
            updated = text.rstrip() + f"\n  - {args.lesson_id}\n"
            unit_yaml.write_text(updated, encoding="utf-8")
            print(f"[asf curriculum] appended lesson to {unit_yaml.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="asf curriculum", description="Curriculum authoring CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    new_course = sub.add_parser("new-course", help="Scaffold a new course directory")
    new_course.add_argument("course_id")
    new_course.add_argument("title")
    new_course.add_argument(
        "--level", default="beginner", choices=["beginner", "intermediate", "advanced"]
    )
    new_course.set_defaults(func=cmd_new_course)

    new_unit = sub.add_parser("new-unit", help="Scaffold a new unit under a course")
    new_unit.add_argument("course_id")
    new_unit.add_argument("unit_id")
    new_unit.add_argument("title")
    new_unit.set_defaults(func=cmd_new_unit)

    new_lesson = sub.add_parser("new-lesson", help="Scaffold a new lesson markdown file")
    new_lesson.add_argument("course_id")
    new_lesson.add_argument("unit_id")
    new_lesson.add_argument("lesson_id")
    new_lesson.add_argument("title")
    new_lesson.add_argument(
        "--modality",
        default="reading",
        choices=["reading", "interactive", "video", "project", "discussion"],
    )
    new_lesson.set_defaults(func=cmd_new_lesson)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
