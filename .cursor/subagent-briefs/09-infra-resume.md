# 09 — Infra / DevOps — Resume Brief (Round 2)

## Current state

A lot has landed on `main`:
- `infra/docker-compose.yml` (Postgres+pgvector, Redis, Neo4j, Langfuse, MinIO, Mailhog, OTel collector).
- Alembic: `0001_init.py`, `0002_core_tables.py`, `0002_curriculum.py`, `0002_gateway_tables.py`, `0002_memory_tables.py` (kg_chunks lives on the graphrag branch awaiting merge).
- Workflows: `lint-test.yml`, `evals.yml`, `deploy-api.yml`, `deploy-web.yml`, `deploy-workers.yml`, `deploy-prod.yml`.
- `docs/infra/local-dev.md`, `docs/infra/migrations.md`.
- `Makefile` with `up/down/dev/migrate/seed/evals/lint/fmt/test/smoke`.

In-flight on `wip/agents-phase3-snapshot`: workspace stabilization — `pyproject.toml` cleanups across all packages, ruff scoping fix, **deletion of `0002_core_tables.py`** (consolidated into per-service migrations), `scripts/fix-workspace-sources.ps1`, `uv.lock`. **You own deciding what to land from this.**

## What's left

1. **Land the workspace stabilization** from `wip/agents-phase3-snapshot` cleanly on `main` via a dedicated branch `chore/infra/workspace-stabilization`. Do NOT bundle Phase-3 agent code — only:
   - `pyproject.toml` edits across packages/services/api/workers/mcp-servers/orchestrator/graphrag/curriculum/memory.
   - Root `pyproject.toml` ruff scope changes + `[tool.uv]` python version.
   - `infra/alembic/env.py` change.
   - Drop `0002_core_tables.py` if it's superseded by the per-service migrations (validate by running `alembic upgrade head` on a fresh DB — every per-service 0002 must depend on `0001_init`).
   - `Makefile` adjustments.
   - `scripts/fix-workspace-sources.ps1`.
   - `uv.lock`.
   - `tests/test_infra.py` updates.
   - `.github/workflows/lint-test.yml` tweaks.
2. **Alembic dependency graph**: with multiple `0002_*.py` migrations, ensure they're independent or have explicit `down_revision` chains. Document in `docs/infra/migrations.md`. Add a `make migrate-check` that runs `alembic upgrade head` + `downgrade base` on a fresh DB.
3. **Cloud provisioning** (Terraform or shell-scripted):
   - Neon Postgres project + branch.
   - Upstash Redis.
   - Neo4j AuraDB Free.
   - Cloudflare R2 bucket.
   - Doppler project + configs (`dev`, `staging`, `prod`).
4. **Fly.io apps**: `asf-api`, `asf-workers`, `asf-mcp-memory`, `asf-mcp-graphrag`, `asf-mcp-curriculum`, `asf-mcp-progress`, `asf-langfuse`. Each with a `fly.toml`, healthcheck, deploy from GH Actions.
5. **Vercel project** for `apps/web`: env via Doppler GitHub Action; preview on PR; prod on merge to `main`.
6. **Secrets**: Doppler service tokens stored as GH Actions secrets; never raw secrets in `.env*`.
7. **Observability stack**: Langfuse + Sentry + OTel collector exporting to Honeycomb/Tempo (free tier).
8. **Backup/restore**: nightly Neon snapshot + a documented restore drill.

## Locked decisions

- Hosting/managed-DB choices as in `RESUME-README.md`.
- License: MIT.
- One Fly region (`iad`) until traffic justifies more.
- Doppler is the single secret source of truth.
- Migrations: every service has its own Alembic head; root `alembic upgrade head` runs all in order.

## Done when

- Workspace stabilization branch merged.
- `make smoke` clean on a fresh checkout.
- All Fly apps + Vercel project exist with healthy preview deploys.
- Doppler provisioned with dev/staging/prod configs.
- Deploy workflows green on `main` push.
- Restore drill documented and rehearsed.

## Required reading

- `PLAN.md` §10, §12, §15; `ARCHITECTURE.md` §8.
- `skills/{deploy,db-migrations}/SKILL.md`.
- `.cursor/rules/{50,60}-*.mdc`.
- `.cursor/subagent-briefs/09-infra.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Infra/DevOps sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/09-infra-resume.md
  3. .cursor/subagent-briefs/09-infra.md
  4. PLAN.md §10, §12, §15; ARCHITECTURE.md §8
  5. skills/{deploy,db-migrations}/SKILL.md
  6. .cursor/rules/{50,60}-*.mdc

Then, in this order:
  A. git checkout wip/agents-phase3-snapshot ; identify the infra-only edits
     (pyproject.toml across packages, ruff scoping, env.py, alembic 0002_core_tables
     deletion, Makefile, scripts/fix-workspace-sources.ps1, uv.lock, lint-test.yml,
     tests/test_infra.py). Cherry-pick / re-author them on a fresh branch
     chore/infra/workspace-stabilization off main. DO NOT bring Phase-3 agent code.
  B. Validate alembic upgrade head + downgrade base on a fresh Postgres docker.
     Document the multi-head graph in docs/infra/migrations.md. Add a
     make migrate-check.
  C. Provision Neon, Upstash, Neo4j AuraDB, Cloudflare R2, Doppler (dev/staging/prod).
  D. Create Fly apps: asf-api, asf-workers, asf-mcp-* (4), asf-langfuse. Add
     infra/fly/*.toml + healthchecks.
  E. Configure Vercel project for apps/web with Doppler-injected env.
  F. Wire deploy-*.yml workflows to use Doppler tokens from GH secrets.
  G. Stand up observability (Langfuse + Sentry + OTel exporting to a free
     backend) and a backup/restore drill.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. review-bugbot on each. review-security on secret-handling PRs.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: every part of the system can be deployed end-to-end with one
push to main; Release Captain takes it from green CI to live URL.
```
