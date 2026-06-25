"""Clerk JWT auth edge cases (JWKS fetch failures, malformed tokens)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _clerk_staging_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate Clerk env so other API tests keep header-auth defaults."""
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("CLERK_JWKS_URL", "https://clerk.example/.well-known/jwks.json")
    monkeypatch.setenv("CLERK_ISSUER", "https://clerk.example")
    from app.core.settings import get_settings

    get_settings.cache_clear()
    yield  # type: ignore[misc]
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _clear_jwks_cache() -> None:
    import app.core.auth as auth_mod

    auth_mod._jwks_cache = None
    auth_mod._jwks_fetched_at = 0.0
    yield
    auth_mod._jwks_cache = None
    auth_mod._jwks_fetched_at = 0.0


@pytest.fixture
def app():
    with patch("app.main.warmup_clerk_jwks", new=AsyncMock()):
        from app.main import create_app

        return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_malformed_bearer_returns_401_not_500(client: AsyncClient) -> None:
    mock_jwks = {"keys": [{"kty": "RSA", "kid": "k1", "n": "abc", "e": "AQAB"}]}
    with patch("app.core.auth._fetch_jwks", AsyncMock(return_value=mock_jwks)):
        resp = await client.get(
            "/v1/learners/me",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "auth_error"


@pytest.mark.asyncio
async def test_jwks_fetch_failure_returns_401_not_500(client: AsyncClient) -> None:
    request = httpx.Request("GET", "https://clerk.example/.well-known/jwks.json")
    http_error = httpx.HTTPStatusError(
        "not found", request=request, response=httpx.Response(404, request=request)
    )

    async def _fail_get(*_args: object, **_kwargs: object) -> None:
        raise http_error

    mock_client = AsyncMock()
    mock_client.get = _fail_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.core.auth.httpx.AsyncClient", return_value=mock_client):
        resp = await client.get(
            "/v1/onboarding/status",
            headers={"Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.e30.sig"},
        )
    assert resp.status_code == 401
    assert "JWKS" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_health_alias(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
