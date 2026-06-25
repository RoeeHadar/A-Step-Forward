"""Async SQLAlchemy engine/session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import parse_qs, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..settings import LearnerModelSettings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _normalize_url(url: str) -> tuple[str, dict]:
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    sslmode = params.pop("sslmode", ["disable"])[0]
    params.pop("channel_binding", None)
    remaining = "&".join(f"{k}={v[0]}" for k, v in params.items())
    clean = urlunparse(parsed._replace(query=remaining))
    connect_args = {"ssl": True} if sslmode in ("require", "verify-ca", "verify-full") else {}
    return clean, connect_args


def get_engine(settings: LearnerModelSettings | None = None):
    global _engine, _session_factory
    if _engine is None:
        cfg = settings or LearnerModelSettings()
        url, connect_args = _normalize_url(cfg.database_url)
        _engine = create_async_engine(url, connect_args=connect_args, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_session_factory(settings: LearnerModelSettings | None = None) -> async_sessionmaker[AsyncSession]:
    get_engine(settings)
    assert _session_factory is not None
    return _session_factory


@asynccontextmanager
async def session_scope(settings: LearnerModelSettings | None = None) -> AsyncIterator[AsyncSession]:
    factory = get_session_factory(settings)
    async with factory() as session:
        yield session
