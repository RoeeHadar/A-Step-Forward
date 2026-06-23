"""Seed authoring schemas and loader for YAML/Markdown curriculum files."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .curriculum import (
    Assessment,
    Concept,
    Course,
    Lesson,
    Level,
    Modality,
    Objective,
    Resource,
    Unit,
)

_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)", re.DOTALL)


class CourseMeta(BaseModel):
    """Top-level course.yaml metadata."""

    id: str
    title: str
    level: Level
    summary: str
    prerequisites: list[str] = Field(default_factory=list)
    units: list[str]


class UnitMeta(BaseModel):
    """unit.yaml inside a unit folder."""

    id: str
    title: str
    summary: str
    objectives: list[Objective] = Field(default_factory=list)
    lessons: list[str]
    assessments: list[str] = Field(default_factory=list)


class LessonFrontmatter(BaseModel):
    id: str
    title: str
    modality: Modality
    objectives: list[Objective] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    est_minutes: int = 15


class ConceptsCatalog(BaseModel):
    concepts: list[Concept]


class SeedBundle(BaseModel):
    """Fully resolved seed content ready for persistence + KG projection."""

    course: Course
    concepts: list[Concept] = Field(default_factory=list)


def parse_lesson_markdown(text: str) -> tuple[LessonFrontmatter, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        msg = "lesson markdown must begin with YAML frontmatter delimited by ---"
        raise ValueError(msg)
    frontmatter = LessonFrontmatter.model_validate(yaml.safe_load(match.group(1)) or {})
    body_md = match.group(2).lstrip("\n")
    return frontmatter, body_md


def _read_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"expected mapping in {path}"
        raise ValueError(msg)
    return data


def load_seed_course(course_dir: Path) -> SeedBundle:
    """Load and assemble a course from infra/seeds/courses/<course-id>/."""

    if not course_dir.is_dir():
        msg = f"seed course directory not found: {course_dir}"
        raise FileNotFoundError(msg)

    meta = CourseMeta.model_validate(_read_yaml(course_dir / "course.yaml"))
    concepts_path = course_dir / "concepts.yaml"
    concepts: list[Concept] = []
    if concepts_path.exists():
        concepts = ConceptsCatalog.model_validate(_read_yaml(concepts_path)).concepts

    resources: list[Resource] = []
    resources_dir = course_dir / "resources"
    if resources_dir.is_dir():
        for resource_path in sorted(resources_dir.glob("*.yaml")):
            resources.append(Resource.model_validate(_read_yaml(resource_path)))

    units: list[Unit] = []
    units_root = course_dir / "units"
    for unit_id in meta.units:
        unit_dir = units_root / unit_id
        unit_meta = UnitMeta.model_validate(_read_yaml(unit_dir / "unit.yaml"))

        lessons: list[Lesson] = []
        lessons_dir = unit_dir / "lessons"
        for lesson_id in unit_meta.lessons:
            lesson_path = lessons_dir / f"{lesson_id}.md"
            frontmatter, body_md = parse_lesson_markdown(lesson_path.read_text(encoding="utf-8"))
            lessons.append(
                Lesson(
                    id=frontmatter.id,
                    title=frontmatter.title,
                    body_md=body_md,
                    modality=frontmatter.modality,
                    objectives=frontmatter.objectives,
                    concepts=frontmatter.concepts,
                    resources=frontmatter.resources,
                    est_minutes=frontmatter.est_minutes,
                )
            )

        assessments: list[Assessment] = []
        assessments_dir = unit_dir / "assessments"
        for assessment_id in unit_meta.assessments:
            assessment_path = assessments_dir / f"{assessment_id}.yaml"
            assessments.append(Assessment.model_validate(_read_yaml(assessment_path)))

        units.append(
            Unit(
                id=unit_meta.id,
                title=unit_meta.title,
                summary=unit_meta.summary,
                objectives=unit_meta.objectives,
                lessons=lessons,
                assessments=assessments,
            )
        )

    course = Course(
        id=meta.id,
        title=meta.title,
        level=meta.level,
        summary=meta.summary,
        prerequisites=meta.prerequisites,
        units=units,
        resources=resources,
    )
    return SeedBundle(course=course, concepts=concepts)
