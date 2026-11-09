"""Integration tests for /v1/lessons/* — verifies seed payloads flow through.

The minimal FastAPI app built here mounts only the lessons router so the suite
can run independently of unrelated routers (agents/chat/etc.).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from schemas.curriculum import Course, Lesson  # noqa: E402
from schemas.curriculum_seed import load_seed_course  # noqa: E402
from schemas.errors import NotFoundError  # noqa: E402

from app.core.exception_handlers import register_exception_handlers  # noqa: E402
from app.routers import lessons as lessons_router  # noqa: E402
from app.services.curriculum import (  # noqa: E402
    CurriculumService,
    get_curriculum_service,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_DIR = REPO_ROOT / "infra" / "seeds" / "courses" / "foundations-of-math"


def _flatten_lessons(course: Course) -> Iterable[Lesson]:
    for unit in course.units:
        for lesson in unit.lessons:
            yield lesson


class FakeCurriculumService(CurriculumService):
    """In-memory CurriculumService loaded from the foundations-of-math seed."""

    def __init__(self) -> None:
        bundle = load_seed_course(SEED_DIR)
        self._course = bundle.course
        self._lessons: dict[str, Lesson] = {
            lesson.id: lesson for lesson in _flatten_lessons(bundle.course)
        }

    async def list_courses(self):
        return [self._course]

    async def get_course(self, course_id: str) -> Course:
        if course_id != self._course.id:
            raise NotFoundError(f"course not found: {course_id}")
        return self._course

    async def get_lesson(self, lesson_id: str) -> Lesson:
        lesson = self._lessons.get(lesson_id)
        if lesson is None:
            raise NotFoundError(f"lesson not found: {lesson_id}")
        return lesson


def _build_app(fake: FakeCurriculumService) -> FastAPI:
    application = FastAPI(title="lessons-tests")
    register_exception_handlers(application)
    application.include_router(lessons_router.router)
    application.dependency_overrides[get_curriculum_service] = lambda: fake
    return application


@pytest.fixture
def fake_curriculum() -> FakeCurriculumService:
    return FakeCurriculumService()


@pytest.fixture
def app(fake_curriculum: FakeCurriculumService) -> FastAPI:
    return _build_app(fake_curriculum)


@pytest.fixture
async def client(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _headers(learner_id: str = "learner-test-1") -> dict[str, str]:
    return {"X-Learner-Id": learner_id, "X-Role": "learner"}


@pytest.mark.asyncio
async def test_get_intro_decimals_matches_seed(
    client: AsyncClient, fake_curriculum: FakeCurriculumService
) -> None:
    resp = await client.get("/v1/lessons/lesson-intro-decimals", headers=_headers())
    assert resp.status_code == 200, resp.text
    body = resp.json()

    expected = await fake_curriculum.get_lesson("lesson-intro-decimals")
    assert body["id"] == expected.id == "lesson-intro-decimals"
    assert body["title"] == "Introduction to Decimals"
    assert body["modality"] == "reading"
    assert body["body_md"].startswith("# Introduction to Decimals")
    assert "decimal point" in body["body_md"]
    assert any(obj["id"] == "obj-dec-place" for obj in body["objectives"])


@pytest.mark.asyncio
async def test_get_unknown_lesson_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/v1/lessons/does-not-exist", headers=_headers())
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "not_found"


@pytest.mark.asyncio
async def test_get_lesson_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/v1/lessons/lesson-intro-decimals")
    assert resp.status_code == 401
