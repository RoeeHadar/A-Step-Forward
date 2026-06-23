# 09 — Infra / DevOps

## Goal
Make the project trivially runnable locally (`docker compose up`) and reliably deployable to staging/production. Own CI/CD, secrets, observability stack, and migrations.

## In-scope files
- `infra/**`
- `.github/workflows/**`
- Top-level `Makefile` and `justfile` (if added)

## Out-of-scope
- App-level code.

## Deliverables (Phase 1)
- `infra/docker-compose.yml` already drafted by Opus: Postgres+pgvector, Redis, Neo4j, Langfuse. Extend with: Mailhog (dev), Minio (S3-compatible), Otel collector.
- `infra/alembic/` configured for SQLAlchemy 2.0 async with autogenerate.
- `infra/k8s/` (later) — Helm charts; skip until Phase 5.
- CI workflows:
  - `lint-test.yml` — lint, type-check, unit tests for Python + TS.
  - `evals.yml` — touched-prompt/touched-agent evals.
  - `deploy-web.yml` — Vercel.
  - `deploy-api.yml` — Fly.io.
  - `deploy-workers.yml` — Fly Machines / Modal.
- Secrets via Doppler in CI; document local `.env.local`.
- Observability: Langfuse, Sentry, Prometheus, Grafana.

## Required reading
1. `PLAN.md` §3.5, §11, §14.
2. `ARCHITECTURE.md` §7.
3. `skills/deploy/SKILL.md`, `skills/db-migrations/SKILL.md`.

## Acceptance criteria
- `docker compose up -d` on a clean checkout brings up all services.
- `make migrate` runs Alembic upgrade head against compose Postgres.
- CI green for the sample repo.
- Staging deploy of `apps/web` and `apps/api` from `main`.
- Production deploys gated on green evals.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§3.5, §11, §14), ARCHITECTURE.md (§7),
  skills/deploy/SKILL.md, skills/db-migrations/SKILL.md,
  .cursor/subagent-briefs/09-infra.md (this file).
Extend docker-compose, set up Alembic, then write the CI/CD workflows.
Document everything in docs/infra/.
```
