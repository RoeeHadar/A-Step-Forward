"""Auth dependencies — Clerk JWT verification with local dev fallback."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Header, HTTPException
from jose import JWTError, jwt
from jose.exceptions import JWKError
from schemas.errors import AuthError
from schemas.learners import LearnerRole

from .settings import get_settings

_DEPLOYED_ENVS = frozenset({"production", "staging", "preview"})
_LOCAL_ENVS = frozenset({"local", "test", "development"})


@dataclass
class AuthCtx:
    learner_id: str
    role: str = LearnerRole.LEARNER.value
    clerk_user_id: str | None = None
    age: int | None = None
    child_mode: bool = False


_jwks_cache: dict[str, Any] | None = None
_jwks_fetched_at: float = 0.0
_JWKS_TTL_SEC = 3600


def validate_auth_config() -> None:
    """Fail fast when deployed without Clerk JWKS."""
    settings = get_settings()
    if settings.app_env in _DEPLOYED_ENVS and not settings.clerk_jwks_url:
        raise RuntimeError(
            "CLERK_JWKS_URL is required when APP_ENV is production, staging, or preview"
        )


async def _fetch_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_fetched_at
    settings = get_settings()
    if not settings.clerk_jwks_url:
        raise AuthError("Clerk JWKS URL not configured")
    now = time.time()
    if _jwks_cache and (now - _jwks_fetched_at) < _JWKS_TTL_SEC:
        return _jwks_cache
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.clerk_jwks_url)
            resp.raise_for_status()
            try:
                _jwks_cache = resp.json()
            except ValueError as exc:
                raise AuthError("invalid Clerk JWKS response") from exc
            _jwks_fetched_at = now
            return _jwks_cache
    except httpx.HTTPError as exc:
        raise AuthError("unable to fetch Clerk JWKS; check CLERK_JWKS_URL") from exc


async def warmup_clerk_jwks() -> None:
    """Best-effort JWKS prefetch.

    We intentionally do NOT crash the process if the warmup fails — a
    misconfigured ``CLERK_JWKS_URL`` (typo, leading whitespace, network
    blip, Clerk outage) used to take the entire API down at boot,
    masking every other endpoint. Now we log the failure and let the
    process come up; per-request auth still rejects requests cleanly
    via ``_verify_clerk_token`` if the URL really is bad.
    """
    import logging

    settings = get_settings()
    if not settings.clerk_jwks_url:
        return
    try:
        await _fetch_jwks()
    except Exception as exc:  # noqa: BLE001 — must never propagate at boot
        logging.getLogger(__name__).warning(
            "Clerk JWKS warmup failed (will retry on first auth): %s", exc
        )


async def check_clerk_jwks() -> bool:
    settings = get_settings()
    if not settings.clerk_jwks_url:
        return True
    try:
        await _fetch_jwks()
        return True
    except (AuthError, httpx.HTTPError):
        return False


def _child_fields_from_claims(claims: dict[str, Any]) -> tuple[int | None, bool]:
    metadata = claims.get("public_metadata") or {}
    if not isinstance(metadata, dict):
        return None, False
    age_raw = metadata.get("age")
    age = int(age_raw) if age_raw is not None else None
    child_mode = bool(metadata.get("child_mode", False))
    if age is not None and age < 13:
        child_mode = True
    return age, child_mode


async def _resolve_server_role(*, learner_id: str, clerk_user_id: str | None) -> str:
    """RBAC roles come from server-side profile storage, never from client JWT metadata."""
    from ..services.learner import get_learner_service

    profile = await get_learner_service().get_or_create(
        AuthCtx(learner_id=learner_id, clerk_user_id=clerk_user_id, role=LearnerRole.LEARNER.value)
    )
    return profile.role.value


async def _verify_clerk_token(authorization: str | None) -> AuthCtx:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthError("missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    settings = get_settings()
    jwks = await _fetch_jwks()

    decode_options: dict[str, bool] = {"verify_aud": bool(settings.clerk_audience)}
    decode_kwargs: dict[str, Any] = {
        "algorithms": ["RS256"],
        "options": decode_options,
    }
    if settings.clerk_audience:
        decode_kwargs["audience"] = settings.clerk_audience
    if settings.clerk_issuer:
        decode_kwargs["issuer"] = settings.clerk_issuer

    try:
        claims = jwt.decode(token, jwks, **decode_kwargs)
    except (JWTError, JWKError) as exc:
        raise AuthError("invalid token") from exc

    sub = claims.get("sub")
    if not sub:
        raise AuthError("token missing subject")

    age, child_mode = _child_fields_from_claims(claims)
    learner_id = str(sub)
    role = await _resolve_server_role(learner_id=learner_id, clerk_user_id=learner_id)
    return AuthCtx(
        learner_id=learner_id,
        role=role,
        clerk_user_id=learner_id,
        age=age,
        child_mode=child_mode,
    )


async def require_learner(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_learner_id: str | None = Header(default=None, alias="X-Learner-Id"),
    x_role: str | None = Header(default=None, alias="X-Role"),
    x_child_mode: str | None = Header(default=None, alias="X-Child-Mode"),
    x_age: str | None = Header(default=None, alias="X-Age"),
) -> AuthCtx:
    settings = get_settings()
    if settings.app_env in _DEPLOYED_ENVS and not settings.clerk_jwks_url:
        raise AuthError("Clerk JWT auth required in deployed environments")

    if settings.clerk_jwks_url:
        return await _verify_clerk_token(authorization)

    if settings.app_env not in _LOCAL_ENVS:
        raise AuthError("header auth is only allowed in local/test environments")

    if not x_learner_id:
        raise HTTPException(
            status_code=401, detail="missing learner id (dev: set X-Learner-Id header)"
        )

    age = int(x_age) if x_age and x_age.isdigit() else None
    child_mode = x_child_mode == "1" or (age is not None and age < 13)
    role = x_role or LearnerRole.LEARNER.value
    if role != LearnerRole.LEARNER.value and not settings.dev_allow_role_headers:
        role = LearnerRole.LEARNER.value

    role = await _resolve_server_role(learner_id=x_learner_id, clerk_user_id=x_learner_id)
    return AuthCtx(
        learner_id=x_learner_id,
        role=role,
        clerk_user_id=x_learner_id,
        age=age,
        child_mode=child_mode,
    )
