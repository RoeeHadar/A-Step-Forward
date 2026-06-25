---
name: deploy
description: How to deploy apps/web (Vercel), apps/api + services (Fly.io), workers (Fly Machines / Modal). Read BEFORE editing CI/CD or shipping a release.
---

# Deploy

## Environments
- `local` — docker compose.
- `staging` — auto-deployed from `main`.
- `prod` — manual promote, gated on green evals.

## Frontend (Vercel)
- `apps/web` linked to Vercel project.
- Env vars via Vercel dashboard or `vercel env pull`.
- Preview deploys per PR.
- `next.config.mjs` sets standalone output + security headers (mirrored by `middleware.ts`).

## Backend / services (Fly.io)
- One Fly app per service: `asf-api`, `asf-memory`, `asf-graphrag`, `asf-orchestrator`.
- `infra/fly/<app>.toml` per app.
- Health checks: `/healthz` for liveness, `/readyz` for readiness.
- Secrets via `fly secrets set ...` (sourced from Doppler).
- Rolling deploys; auto-rollback on health-check fail.

## Backend (Render — primary for solo/staging)
- Service: `asf-api` via `render.yaml` + `apps/api/Dockerfile`.
- **Start command**: `uvicorn app.main:app` with `PYTHONPATH=/app/apps/api` (see Dockerfile). Do not use `apps.api.app.main` — fragile without package `__init__.py` files.
- **Pre-push gate**: `uv run --package asf-api python -c "from app.main import app"`. CI runs this as "API import smoke". A green root `pytest` does **not** prove the API boots.
- **Optional Pydantic types**: `EmailStr` needs `email-validator>=2.0` in `apps/api` deps (and `uv lock`), or use `Field(pattern=...)` on `str`. Missing dep crashes startup when FastAPI generates schemas.
- Free tier cold-starts ~15s; frontend warm-up + 55s timeout handle this (see ADR-001).

## Workers (Fly Machines or Modal)
- Celery beat + worker pools; one machine per pool.
- Dreamer pool gets larger memory.
- Modal for occasional heavy GPU jobs (if added later).

## Migrations
- `make migrate` runs Alembic against the target env.
- CI gates: never deploy if migrations are pending and not in the same release.

## Promotion checklist
1. `evals.yml` green for last commit on `main`.
2. Shadow online evals stable for 24h.
3. Sentry error rate < threshold.
4. `gh workflow run deploy-prod.yml` with reviewer approval.

## Pitfalls
- Don't pin a model in production without a fallback route in `agents/base/llm.py`.
- Don't bypass migration gates ("just one quick fix"); follow the checklist.
- Don't ship a prompt or agent change without an eval baseline promotion PR.
- Don't assume green CI means Render will boot — verify the **API import smoke** step and Docker `CMD` match.
