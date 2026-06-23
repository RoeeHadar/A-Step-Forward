---
name: db-migrations
description: How to author and run Alembic migrations safely against Postgres+pgvector. Read BEFORE adding/changing any DB schema.
---

# DB Migrations

## Tools
- SQLAlchemy 2.0 async + Alembic.
- pgvector extension created in `infra/alembic/versions/0001_init.py`.

## Workflow
```bash
# autogenerate from model diffs
uv run alembic -c infra/alembic.ini revision --autogenerate -m "feat(memory): add semantic_memories"
# review, edit carefully
uv run alembic -c infra/alembic.ini upgrade head
```

## Rules
- One concern per migration; descriptive name.
- Backfills go in separate data migrations, not schema migrations.
- For pgvector columns:
  ```python
  from pgvector.sqlalchemy import Vector
  Column("embedding", Vector(1024), nullable=False)
  ```
  Always add an `ivfflat` or `hnsw` index in the same migration (or a follow-up `CONCURRENTLY` migration if the table is hot).
- For destructive changes (drop column/table), gate by env (`DROP_ALLOWED=true`) and ship two-phase: code stops using → migration drops.
- Always provide a working `downgrade()`.

## Pitfalls
- Don't `op.execute("RAW SQL")` without comments.
- Don't autogenerate without reviewing — Alembic misses enum changes and index renames.
- Don't add unique constraints on existing data without a backfill.
