# CI/CD

GitHub Actions under `.github/workflows/`.

## Workflows

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `lint-test.yml` | PR + push to `main` | Ruff, mypy (infra), pytest, ESLint, tsc, vitest; Alembic upgrade |
| `evals.yml` | Changes under `prompts/`, `packages/agents/`, `evals/` | Touched-prompt/agent evals |
| `deploy-web.yml` | Push to `main` (web paths) | Vercel staging deploy |
| `deploy-api.yml` | Push to `main` (api paths) | Fly.io `asf-api` staging + migrations |
| `deploy-workers.yml` | Push to `main` (workers paths) | Fly.io `asf-workers` staging |
| `deploy-prod.yml` | Manual (`workflow_dispatch`, input `promote`) | Production promote; gated on green evals |

## Environments

- **staging** — auto-deploy from `main` when path filters match
- **production** — manual promote via `deploy-prod.yml`; requires last `evals.yml` run on `main` to be green

## Required GitHub secrets

| Secret | Used by |
| --- | --- |
| `DOPPLER_TOKEN` | All deploy workflows (env sync) |
| `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | Web deploy |
| `FLY_API_TOKEN` | API + workers deploy |
| `STAGING_DATABASE_URL` | Staging migrations |
| `PRODUCTION_DATABASE_URL` | Production migrations |

Configure GitHub **environments** (`staging`, `production`) with required reviewers for production.

## Fly.io apps

Configs in `infra/fly/`:

- `asf-api.toml` — FastAPI gateway
- `asf-memory.toml`, `asf-graphrag.toml`, `asf-orchestrator.toml` — services (Phase 1+)
- `asf-workers.toml` — Celery worker + beat + dreamer pool

Health checks: `/healthz` (liveness), `/readyz` (readiness) on HTTP services.

## Promotion checklist

See `skills/deploy/SKILL.md`:

1. `evals.yml` green on `main`
2. Shadow online evals stable 24h (Phase 4+)
3. Sentry error rate below threshold
4. Run `deploy-prod.yml` with reviewer approval
