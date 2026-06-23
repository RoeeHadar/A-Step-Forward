"""Async database engine and session factory for the memory service."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ..settings import MemorySettings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: MemorySettings | None = None) -> AsyncEngine:
    global _engine, _session_factory
    if _engine is None:
        cfg = settings or MemorySettings()
        _engine = create_async_engine(cfg.database_url, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_session_factory(settings: MemorySettings | None = None) -> async_sessionmaker[AsyncSession]:
    get_engine(settings)
    assert _session_factory is not None
    return _session_factory


@asynccontextmanager
async def session_scope(settings: MemorySettings | None = None) -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory(settings)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
