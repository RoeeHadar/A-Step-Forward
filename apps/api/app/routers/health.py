"""Liveness / readiness / metrics."""

from __future__ import annotations

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from ..core.auth import check_clerk_jwks
from ..core.db import check_postgres
from ..core.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health")
async def health() -> dict[str, str]:
    """Alias for load balancers and smoke scripts that probe ``/health``."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz() -> dict[str, str | bool]:
    settings = get_settings()
    checks: dict[str, bool] = {
        "postgres": await check_postgres(),
        "clerk_jwks": await check_clerk_jwks(),
    }
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        pong = await redis.ping()
        checks["redis"] = bool(pong)
        await redis.aclose()
    except Exception:
        checks["redis"] = False
    ready = all(checks.values())
    return {"status": "ready" if ready else "degraded", **checks}


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
