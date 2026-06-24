# Scripts

Utility scripts for local development, seeding, and content ingestion.

## OpenStax content ingest (`ingest_content.py`)

Stream K — scrapes public OpenStax textbook pages, chunks section text, embeds with
**sentence-transformers/all-MiniLM-L6-v2** (384 dimensions, no API key), and upserts into
Postgres `kg_chunks` on Neon.

### Prerequisites

1. Python env via `uv` (monorepo root).
2. **`DATABASE_URL`** — Postgres connection string (e.g. Neon). The script accepts
   `postgresql://` or `postgresql+asyncpg://` forms.
3. **Alembic migration `0006_kg_chunks_384`** — ensures `kg_chunks.embedding` is
   `vector(384)` for MiniLM. If your database was created with `0005_kg_chunks` only
   (1024-dim), apply:

   ```bash
   uv run alembic -c infra/alembic/alembic.ini upgrade head
   ```

   Migration file: `infra/alembic/versions/0006_kg_chunks_384.py` (drops/recreates
   `kg_chunks` when empty; see ADR-0005).

4. Optional: `OPENSTAX_INSECURE_SSL=1` on Windows dev machines with TLS interception
   (also enables HuggingFace Hub model download fallback used by the embedder).

### Default books

- `precalculus-2e`
- `introductory-statistics`

### Usage

```bash
# Discover + parse only (no DB)
uv run python scripts/ingest_content.py --parse-only --max-pages 3

# Full ingest (requires DATABASE_URL)
export DATABASE_URL="postgresql://..."
uv run python scripts/ingest_content.py

# Specific books
uv run python scripts/ingest_content.py --books precalculus-2e introductory-statistics

# Export parsed Lesson JSON for frontend seeds
uv run python scripts/ingest_content.py --parse-only --max-pages 5 \
  --export-lessons /tmp/openstax-lessons.json
```

### Idempotency

Each chunk id is `sha256(source_url + chunk_idx)` (prefixed `osx-`). Re-running the
script upserts on `kg_chunks.id` without duplicates.

### Chunk metadata (`provenance` JSONB)

Every row includes:

| Field | Value |
| --- | --- |
| `source_url` | Canonical OpenStax page URL |
| `license` | `CC BY 4.0` |
| `subject` | e.g. `precalculus`, `statistics` |
| `chunk_idx` | Ordinal within the source page |
| `book_slug` / `page_slug` | OpenStax identifiers |
| `model` | `sentence-transformers/all-MiniLM-L6-v2` |

### Verify ingest (Neon)

```sql
SELECT COUNT(*), provenance->>'subject' AS subject
FROM kg_chunks
GROUP BY provenance->>'subject';
```

## Other scripts

| Script | Purpose |
| --- | --- |
| `seed_curriculum.py` | Load YAML/Markdown seeds into Postgres |
| `ingest_graphrag.py` | GraphRAG pipeline for local seed markdown |
| `export_seed_lessons.py` | Regenerate `apps/web/src/lib/seed-lessons.generated.json` |
| `asf_curriculum.py` | Educator CLI for curriculum authoring |
