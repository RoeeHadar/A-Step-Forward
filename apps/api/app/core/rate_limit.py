"""Per-learner sliding-window rate limiting via Redis."""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends, Request
from redis.asyncio import Redis

from schemas.errors import RateLimited

from .auth import AuthCtx, require_learner
from .settings import get_settings


async def _get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def check_rate_limit(key: str, *, limit: int, window_sec: int = 60) -> None:
    """Sliding window counter. Raises RateLimited when exceeded."""
    settings = get_settings()
    if not settings.rate_limit_enabled or settings.app_env == "test":
        return
    redis = await _get_redis()
    try:
        now = time.time()
        window_start = now - window_sec
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window_sec + 1)
        _, _, count, _ = await pipe.execute()
        if int(count) > limit:
            raise RateLimited(f"rate limit exceeded for {key}")
    finally:
        await redis.aclose()


def per_user(
    route_key: str,
    *,
    per_min: int = 60,
) -> Callable[..., Coroutine[Any, Any, None]]:
    """FastAPI dependency factory: limit requests per (learner_id, route)."""

    async def _rate_limit(
        request: Request,
        ctx: AuthCtx = Depends(require_learner),
    ) -> None:
        settings = get_settings()
        key_parts = [ctx.learner_id, route_key]
        if not settings.clerk_jwks_url and request.client is not None:
            key_parts.insert(0, request.client.host)
        key = f"rl:{':'.join(key_parts)}"
        await check_rate_limit(key, limit=per_min, window_sec=60)

    return _rate_limit
