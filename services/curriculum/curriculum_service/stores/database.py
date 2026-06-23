"""Async SQLAlchemy engine/session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..settings import CurriculumSettings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: CurriculumSettings | None = None):
    global _engine, _session_factory
    if _engine is None:
        cfg = settings or CurriculumSettings()
        _engine = create_async_engine(cfg.database_url, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_session_factory(settings: CurriculumSettings | None = None) -> async_sessionmaker[AsyncSession]:
    get_engine(settings)
    assert _session_factory is not None
    return _session_factory


async def session_scope(settings: CurriculumSettings | None = None) -> AsyncIterator[AsyncSession]:
    factory = get_session_factory(settings)
    async with factory() as session:
        yield session
