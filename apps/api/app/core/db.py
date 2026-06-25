"""Async database session factory."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.settings import get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _normalize_url(url: str) -> tuple[str, dict]:
    """Rewrite a Neon/postgres URL so asyncpg accepts it.

    asyncpg does not understand sslmode/channel_binding query params.
    Strip them out and return ssl=True as a connect_arg instead.
    """
    parsed = urlparse(url)

    # Ensure asyncpg dialect
    scheme = parsed.scheme
    if scheme in ("postgresql", "postgres"):
        scheme = "postgresql+asyncpg"

    params = parse_qs(parsed.query, keep_blank_values=True)
    needs_ssl = params.pop("sslmode", None) is not None
    params.pop("channel_binding", None)

    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse((scheme, parsed.netloc, parsed.path, parsed.params, clean_query, ""))

    connect_args: dict = {}
    if needs_ssl:
        connect_args["ssl"] = True

    return clean_url, connect_args


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        clean_url, connect_args = _normalize_url(settings.database_url)
        _engine = create_async_engine(clean_url, connect_args=connect_args, pool_pre_ping=True)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def check_postgres() -> bool:
    try:
        from sqlalchemy import text

        async with session_scope() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def database_url_configured() -> bool:
    """True when DATABASE_URL is explicitly set (Neon / production)."""
    return bool(os.environ.get("DATABASE_URL", "").strip())


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency — yields an async SQLAlchemy session."""
    async with session_scope() as session:
        yield session
