# Cron jobs (GitHub Actions)

Background memory hygiene jobs run on GitHub Actions schedules instead of Render/Fly Celery beat (workers on paid plans only). Each workflow can also be triggered manually.

## Workflows

| Workflow | File | Schedule (UTC) | Command |
| --- | --- | --- | --- |
| Dreaming (Memory Steward) | `.github/workflows/cron-dreaming.yml` | Daily **03:00** | `python -m workers.jobs.dreaming` |
| Decay sweep | `.github/workflows/cron-decay.yml` | Weekly **Sun 04:00** | `python -m workers.jobs.decay` |

Both workflows expose **`workflow_dispatch`** for on-demand runs from the GitHub Actions UI.

## Required GitHub secrets

Configure these in the repository (or sync from Doppler):

| Secret | Purpose |
| --- | --- |
| `DATABASE_URL` | Postgres connection string (`postgresql+asyncpg://…`) |
| `REDIS_URL` | Redis for caching / broker (future Celery parity) |
| `NEO4J_URI` | AuraDB / Neo4j bolt URI for KG projection |
| `NEO4J_PASSWORD` | Neo4j credentials |
| `GROQ_API_KEY` | LLM calls during dreaming (when Phase-2 pipeline is wired) |

Never commit secret values. Workflows reference `${{ secrets.* }}` only.

## Manual trigger

1. Open **Actions** in GitHub.
2. Select **Cron — Dreaming (nightly)** or **Cron — Decay sweep (weekly)**.
3. Click **Run workflow** → choose branch (`main`) → **Run workflow**.

## Local dry-run

Jobs default to **dry-run** when `DATABASE_URL` is unset, or when `--dry-run` is passed. No database writes occur in dry-run mode.

```bash
# From repo root after editable installs:
pip install -e packages/schemas -e services/memory -e services/graphrag -e services/workers

python -m workers.jobs.dreaming --dry-run
python -m workers.jobs.decay --dry-run
```

With `DATABASE_URL` set, omit `--dry-run` to execute against the configured database.

## Operational notes

- Dreaming fans out `dream_now` per active learner (Phase-0 stub returns 0 learners until the learners table query is implemented).
- Decay runs `decay_sweep(learner_id=None)` across all stored memories.
- Celery beat schedule in `services/workers/workers/celery_app.py` remains the reference schedule for Fly worker deployments; GitHub cron is the production path until workers are on a paid Fly plan.
