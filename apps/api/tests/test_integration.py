"""Integration tests for Phase-1 API routes."""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from app.main import create_app  # noqa: E402
from memory_service.api import get_memory_service  # noqa: E402

from .fake_memory import FakeMemoryService  # noqa: E402


@pytest.fixture
def app():
    application = create_app()
    fake = FakeMemoryService()
    application.dependency_overrides[get_memory_service] = lambda: fake
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def auth_headers(learner_id: str = "learner-test-1", role: str = "learner") -> dict[str, str]:
    return {"X-Learner-Id": learner_id, "X-Role": role}


@pytest.mark.asyncio
async def test_healthz(client: AsyncClient) -> None:
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_rbac_missing_auth(client: AsyncClient) -> None:
    resp = await client.get("/v1/learners/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_learners_me(client: AsyncClient) -> None:
    resp = await client.get("/v1/learners/me", headers=auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "learner-test-1"
    assert body["role"] == "learner"


@pytest.mark.asyncio
async def test_agents_list(client: AsyncClient) -> None:
    resp = await client.get("/v1/agents", headers=auth_headers())
    assert resp.status_code == 200
    agents = resp.json()
    assert len(agents) >= 1
    assert any(a["name"] == "tutor" for a in agents)


@pytest.mark.asyncio
async def test_lesson_detail(client: AsyncClient) -> None:
    resp = await client.get("/v1/lessons/lesson-fractions-intro", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["title"] == "Introduction to Fractions"


@pytest.mark.asyncio
async def test_progress(client: AsyncClient) -> None:
    resp = await client.get("/v1/progress", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["learner_id"] == "learner-test-1"


@pytest.mark.asyncio
async def test_chat_sse(client: AsyncClient) -> None:
    resp = await client.post(
        "/v1/chat",
        headers=auth_headers(),
        json={"learner_id": "other-learner", "message": "Explain fractions briefly."},
    )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "event:" in resp.text
    assert "done" in resp.text or "token" in resp.text


@pytest.mark.asyncio
async def test_memory_crud(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/v1/memory",
        headers=auth_headers(),
        json={
            "learner_id": "ignored-should-be-overwritten",
            "type": "episodic",
            "content": "Integration test memory row.",
            "provenance": {"kind": "system", "id": "test", "agent": "pytest"},
        },
    )
    assert create_resp.status_code == 200
    memory_id = create_resp.json()["id"]
    assert create_resp.json()["learner_id"] == "learner-test-1"

    list_resp = await client.get("/v1/memory", headers=auth_headers())
    assert list_resp.status_code == 200
    assert any(row["id"] == memory_id for row in list_resp.json())

    patch_resp = await client.patch(
        f"/v1/memory/{memory_id}",
        headers=auth_headers(),
        json={"content": "Updated integration memory.", "reason": "learner correction"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["content"] == "Updated integration memory."

    delete_resp = await client.delete(f"/v1/memory/{memory_id}", headers=auth_headers())
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] is True


@pytest.mark.asyncio
async def test_memory_isolation_rbac(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/v1/memory",
        headers=auth_headers("learner-a"),
        json={
            "learner_id": "learner-a",
            "type": "episodic",
            "content": "Private to learner A.",
            "provenance": {"kind": "system", "id": "test", "agent": "pytest"},
        },
    )
    memory_id = create_resp.json()["id"]

    other_list = await client.get("/v1/memory", headers=auth_headers("learner-b"))
    assert all(row["id"] != memory_id for row in other_list.json())
