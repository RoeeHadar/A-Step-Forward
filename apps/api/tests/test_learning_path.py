"""Tests for learning path API routes."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from app.main import create_app  # noqa: E402
from schemas.learning_path import LearningPlan, PlanConcept, PlanWeek  # noqa: E402


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def auth_headers() -> dict[str, str]:
    return {"X-Learner-Id": "learner-test-1", "X-Role": "learner"}


@pytest.mark.asyncio
async def test_generate_plan_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/v1/learners/me/plans/generate")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_generate_plan(client: AsyncClient) -> None:
    sample = LearningPlan(
        id="plan-1",
        learner_id="learner-test-1",
        goal="Pass Bagrut",
        start_date="2026-06-01",
        weeks=[
            PlanWeek(
                id="week-1",
                plan_id="plan-1",
                week_number=1,
                status="active",
                concepts=[
                    PlanConcept(
                        concept_id="algebra_basics",
                        name="Algebra Basics",
                        subject="math",
                        mastery=0.3,
                    )
                ],
            )
        ],
    )
    with patch(
        "app.routers.learning_path.get_learning_path_service",
        return_value=AsyncMock(generate_plan=AsyncMock(return_value=sample)),
    ):
        resp = await client.post("/v1/learners/me/plans/generate", headers=auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["goal"] == "Pass Bagrut"
    assert body["weeks"][0]["concepts"][0]["concept_id"] == "algebra_basics"
