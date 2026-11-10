"""Shared pytest fixtures for API tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# AS-99: make the workspace members importable from source (same convention as
# services/graphrag/tests/conftest.py), so the API tests collect without relying
# on every member being installed into the active venv.
_ROOT = Path(__file__).resolve().parents[3]
for _rel in (
    "packages/schemas",
    "packages/agents",
    "services/memory",
    "services/graphrag",
    "services/orchestrator",
    "services/curriculum",
    "services/learner_model",
    "services/diagnostic",
    "services/learning_path",
    "apps/api",
):
    _p = str(_ROOT / _rel)
    if _p not in sys.path:
        sys.path.insert(0, _p)


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
