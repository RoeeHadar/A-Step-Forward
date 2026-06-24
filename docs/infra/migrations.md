# Database migrations

Alembic runs against **Postgres 16 + pgvector** using **SQLAlchemy 2.0 async** (`asyncpg`).

## Config

- `infra/alembic.ini` — script location, default local DSN
- `infra/alembic/env.py` — async runner + union metadata from:
  - `memory_service.stores.models` (memory tables)
  - `app.stores.models` (gateway tables)
- `DATABASE_URL` env var overrides the ini DSN (CI, Doppler, Fly secrets)

## Commands

```bash
# Apply all migrations (local compose Postgres must be up)
make migrate

# Autogenerate from ORM diffs (review carefully!)
make migrate-revision msg="feat(memory): add column"

# Manual revision
uv run alembic -c infra/alembic.ini revision -m "describe change"
```

## Versions

| Revision | Description |
| --- | --- |
| `0001` | Extensions: `vector`, `pgcrypto`, `pg_trgm` |
| `0002_memory` | Memory tables + audit_memory_events |
| `0003_gateway` | gateway_users, gateway_sessions, audit_gateway_events |
| `0004_curriculum` | curriculum_courses, concepts, lessons |
| `0005_kg_chunks` | kg_chunks + HNSW index |
| `0006_kg_chunks_384` | kg_chunks embedding dim 384 (sentence-transformers) |
| `0007_memory_events` | memory_events chat-turn audit log |

## Rules (see `skills/db-migrations/SKILL.md`)

- One concern per migration; descriptive slug
- pgvector columns need HNSW/IVFFlat indexes in the same or follow-up migration
- Destructive drops gated by env; ship two-phase (code stops using → migration drops)
- Always provide a working `downgrade()`

## CI

`lint-test.yml` runs `alembic upgrade head` against a ephemeral pgvector service before pytest.

Deploy workflows run migrations against staging/production **before or immediately after** the app deploy — never skip when schema changes ship in the same release.
