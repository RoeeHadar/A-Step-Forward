"""Alembic env — async SQLAlchemy 2.0 + autogenerate against union metadata."""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig
from urllib.parse import parse_qs, urlparse, urlunparse

from alembic import context
from sqlalchemy import MetaData, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _parse_database_url(raw: str) -> tuple[str, dict]:
    """Return (clean_url_for_asyncpg, connect_args).

    Neon exposes: postgresql://user:pass@host/db?sslmode=require&channel_binding=require
    asyncpg:
      - needs the scheme postgresql+asyncpg://
      - does NOT accept sslmode/channel_binding as URL query params
      - needs ssl passed as a connect_arg: {"ssl": True}
    """
    # Rewrite scheme to asyncpg
    if raw.startswith("postgres://"):
        raw = "postgresql+asyncpg://" + raw[len("postgres://"):]
    elif raw.startswith("postgresql://"):
        raw = "postgresql+asyncpg://" + raw[len("postgresql://"):]

    parsed = urlparse(raw)
    params = parse_qs(parsed.query, keep_blank_values=True)

    sslmode = params.pop("sslmode", ["disable"])[0]
    params.pop("channel_binding", None)  # not understood by asyncpg

    # Rebuild URL without problematic params
    remaining = "&".join(f"{k}={v[0]}" for k, v in params.items())
    clean_url = urlunparse(parsed._replace(query=remaining))

    connect_args: dict = {}
    if sslmode in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = True  # asyncpg accepts True for SSL with default ctx

    return clean_url, connect_args


# Resolve DATABASE_URL from env (CI, Doppler, local .env.local) with alembic.ini fallback.
_raw_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url") or ""
_DATABASE_URL, _CONNECT_ARGS = _parse_database_url(_raw_url) if _raw_url else ("", {})


def _combine_metadata(*bases: type[DeclarativeBase]) -> MetaData:
    combined = MetaData()
    for base in bases:
        for table in base.metadata.tables.values():
            table.to_metadata(combined)
    return combined


def _load_target_metadata() -> MetaData:
    from app.stores.models import Base as GatewayBase
    from curriculum_service.stores.models import Base as CurriculumBase
    from memory_service.stores.models import Base as MemoryBase

    return _combine_metadata(MemoryBase, GatewayBase, CurriculumBase)


target_metadata = _load_target_metadata()


def run_migrations_offline() -> None:
    context.configure(
        url=_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(
        _DATABASE_URL,
        connect_args=_CONNECT_ARGS,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
