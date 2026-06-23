"""Security-focused API tests."""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from app.main import create_app  # noqa: E402
from app.services.learner import get_learner_service  # noqa: E402
from schemas.learners import LearnerRole  # noqa: E402


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def auth_headers(
    learner_id: str = "learner-test-1",
    role: str = "learner",
    *,
    child_mode: bool = False,
    age: int | None = None,
) -> dict[str, str]:
    headers = {"X-Learner-Id": learner_id, "X-Role": role}
    if child_mode:
        headers["X-Child-Mode"] = "1"
    if age is not None:
        headers["X-Age"] = str(age)
    return headers


@pytest.mark.asyncio
async def test_admin_audit_requires_admin(client: AsyncClient) -> None:
    resp = await client.get("/v1/admin/audit/gateway", headers=auth_headers(role="learner"))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_audit_allowed_for_admin(client: AsyncClient) -> None:
    await get_learner_service().set_role("learner-test-1", LearnerRole.ADMIN)
    resp = await client.get(
        "/v1/admin/audit/gateway",
        headers=auth_headers(role="learner"),
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_child_mode_auto_from_age(client: AsyncClient) -> None:
    resp = await client.get("/v1/learners/me", headers=auth_headers(age=10))
    assert resp.status_code == 200
    assert resp.json()["child_mode"] is True


@pytest.mark.asyncio
async def test_affective_memory_blocked_in_child_mode(client: AsyncClient) -> None:
    resp = await client.post(
        "/v1/memory",
        headers=auth_headers(child_mode=True),
        json={
            "learner_id": "learner-test-1",
            "type": "affective",
            "content": "Feeling frustrated today.",
            "provenance": {"kind": "system", "id": "test", "agent": "pytest"},
        },
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "policy_violation"


@pytest.mark.asyncio
async def test_pii_redacted_on_memory_write(client: AsyncClient) -> None:
    resp = await client.post(
        "/v1/memory",
        headers=auth_headers(),
        json={
            "learner_id": "learner-test-1",
            "type": "episodic",
            "content": "Contact me at alice@example.com please.",
            "provenance": {"kind": "system", "id": "test", "agent": "pytest"},
        },
    )
    assert resp.status_code == 200
    assert "[EMAIL]" in resp.json()["content"]
    assert "alice@example.com" not in resp.json()["content"]
