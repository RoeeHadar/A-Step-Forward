# Cron jobs

Background memory hygiene runs on **Vercel** (primary for the web app) with **GitHub Actions** backstops for manual triggers.

## Vercel schedules (`apps/web/vercel.json`)

| Endpoint | Schedule (UTC) | Purpose |
| --- | --- | --- |
| `GET /api/cron/dream-memory?limit=50` | Monday **00:00** | Lightweight note dedupe/cap per learner (no LLM) |
| `GET /api/cron/consolidate-memory?limit=25` | Monday **02:00** | Heavy LLM persona consolidation sweep |

Both routes require `CRON_SECRET` via `Authorization: Bearer` (Vercel cron) or `x-cron-secret`.

## GitHub Actions backstops

| Workflow | File | Trigger |
| --- | --- | --- |
| Dream sweep (manual) | `.github/workflows/cron-dream-memory.yml` | `workflow_dispatch` → calls live `WEB_BASE_URL` |
| Consolidate (manual) | `.github/workflows/cron-consolidate-memory.yml` | `workflow_dispatch` (if present) |
| Dreaming (Python worker) | `.github/workflows/cron-dreaming.yml` | Daily 03:00 UTC — Render/worker path |
| Decay sweep | `.github/workflows/cron-decay.yml` | Weekly Sun 04:00 UTC |

## Required secrets

| Secret | Where | Purpose |
| --- | --- | --- |
| `CRON_SECRET` | Vercel + GitHub | Auth for `/api/cron/*` on the Next.js app |
| `DATABASE_URL` | Vercel + GitHub | Neon Postgres |
| `GROQ_API_KEY` | Vercel | LLM for consolidation + chat |
| `WEB_BASE_URL` | GitHub | Production URL for manual cron backstop (`https://a-step-forward-waij.vercel.app`) |

Wire Vercel env (including `CRON_SECRET`) via:

```pwsh
gh workflow run wire-vercel-env.yml
```

Never commit secret values.

## Local dry-run

Dream/consolidate cron handlers return `401` without `CRON_SECRET`. Set it in `apps/web/.env.local` and call:

```bash
curl -H "x-cron-secret: $CRON_SECRET" "http://localhost:3000/api/cron/dream-memory?limit=5"
```

Python worker jobs (`workers.jobs.dreaming`, `workers.jobs.decay`) still support `--dry-run` when `DATABASE_URL` is unset — see legacy notes in repo `services/workers/`.
