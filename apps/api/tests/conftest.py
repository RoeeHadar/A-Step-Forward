"""Shared pytest fixtures for API tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _default_test_env(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Use header auth unless a test module opts into Clerk JWT (``test_auth_clerk``)."""
    if request.node.fspath.basename == "test_auth_clerk.py":
        yield  # type: ignore[misc]
        return
    monkeypatch.setenv("CLERK_JWKS_URL", "")
    monkeypatch.setenv("CLERK_ISSUER", "")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    from app.core.settings import get_settings

    get_settings.cache_clear()
    yield  # type: ignore[misc]
    get_settings.cache_clear()
