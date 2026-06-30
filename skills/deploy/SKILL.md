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
- **Neon migrations**: `.github/workflows/migrate-neon.yml` runs `alembic upgrade head` on push to `main` when `infra/alembic/**` changes (uses `secrets.DATABASE_URL`). Also `workflow_dispatch` for manual runs. Render does **not** auto-migrate — without this, new routes like `/v1/subjects` 500 until tables exist.
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

## MANDATORY: Post-push Vercel check (every agent, every push to main)

After **every** `git push` to `main`, you MUST:

1. **Wait for CI** — poll until the `Deploy Web (Vercel)` workflow completes:
   ```powershell
   gh run list --limit 3 --json status,conclusion,name | ConvertFrom-Json | Where-Object { $_.name -match "Deploy|Lint" }
   ```
   Wait up to 5 minutes, re-polling every 30 seconds.

2. **Check the result** — if `conclusion` is `failure`:
   - Fetch the error: `gh run view <run_id> --log-failed`
   - Fix the root cause immediately (ESLint, TypeScript, ruff)
   - Push the fix and repeat from step 1

3. **Smoke test the live URL** — once CI is green, hit the canonical URL:
   ```powershell
   $urls = @("/", "/sign-in", "/app", "/learn")
   foreach ($path in $urls) {
     $r = Invoke-WebRequest -Uri "https://a-step-forward-waij.vercel.app$path" -UseBasicParsing -MaximumRedirection 5 -ErrorAction SilentlyContinue
     Write-Host "$($r.StatusCode) $path"
   }
   ```
   Any non-2xx/3xx → roll back: `git revert HEAD --no-edit; git push`

4. **Never leave a broken build.** A failing CI on `main` blocks all other agents. Fix it before ending your task.

## Most common CI failures (quick fixes)

| Error | Fix |
|-------|-----|
| `'X' is defined but never used` (ESLint) | Remove unused import in the flagged file |
| `Found N errors` (Ruff) | Check if new `.py` file is in an excluded path; if not, fix lint or add path to `extend-exclude` in `pyproject.toml` |
| `Type error: Property 'X' does not exist` | Run `npx tsc --noEmit` locally, fix type errors |
| `Cannot find module` | Check import paths and `tsconfig.json` paths |
| Build size / memory limit | Check for accidentally imported large assets |

## Pitfalls
- Don't pin a model in production without a fallback route in `agents/base/llm.py`.
- Don't bypass migration gates ("just one quick fix"); follow the checklist.
- Don't ship a prompt or agent change without an eval baseline promotion PR.
- Don't assume green CI means Render will boot — verify the **API import smoke** step and Docker `CMD` match.
- **Don't end your task without a green CI.** Check `gh run list` before finishing.
