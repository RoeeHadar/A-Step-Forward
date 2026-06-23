# 02 — Backend / API — Resume Brief (Round 2)

## Current state

Phase-1 routes shipped (commit `1516f4d feat(api): phase-1 gateway routes, auth, and observability`). Clerk auth wiring and production-auth docs added (`200b6bf docs(infra): document Clerk production auth requirements`).

What's on `main`:
- `apps/api/app/main.py` with lifespan + exception handlers.
- Routers: `health`, `chat` (SSE), `memory` (CRUD), `graphrag` (search + hybrid).
- `core/auth.py` Clerk-aware shim, `core/exception_handlers.py`.
- `pyproject.toml` workspace-wired to `schemas`, `memory-service`, `graphrag-service`, `agents`, `orchestrator`.
- `docs/infra/local-dev.md`, `docs/infra/migrations.md`.

## What's left (Phase 2)

1. **Real Clerk JWT verification**: JWKS cache, role injection, per-row policy helpers in `apps/api/app/core/{auth.py,rbac.py}` — coordinate with stream 10.
2. **Missing routes** (from original brief):
   - `GET /v1/agents` — list available agents (from `AGENT_REGISTRY`).
   - `GET /v1/learners/me` — current learner profile.
   - `GET /v1/lessons/{id}` — proxy to Curriculum Service.
   - `GET /v1/progress` — proxy to Progress Service.
   - `GET /healthz`, `/readyz`, `/metrics` — confirm + extend `/readyz` to ping Postgres, Redis, Neo4j.
3. **Rate limiting**: Redis sliding-window middleware per `(learner_id, route)`. Defaults in `core/rate_limit.py`.
4. **Schema codegen** to TypeScript: emit `packages/schemas/ts/` from Pydantic via `datamodel-code-generator` or a small Pydantic→TS pass. Coordinate with stream 01 (frontend reads from this).
5. **OpenTelemetry + Langfuse**: traces with `learner_id`, `route`, `agent` attributes.
6. **Integration tests**: chat SSE, memory CRUD, RBAC denials, rate-limit headers. Use docker-compose services.
7. **Sentry**: error reporting.
8. **Fly.io app**: `infra/fly/asf-api.toml`, healthcheck wired, deploy workflow already exists at `.github/workflows/deploy-api.yml`.

## Locked decisions

- Auth: Clerk only. Never trust client-supplied `learner_id` for reads.
- Errors: typed in `packages/schemas/errors.py`; handlers map to HTTP.
- DB: SQLAlchemy 2.0 async via the service repositories — no raw SQL in routes.
- Streaming: SSE only (no WebSocket for chat) — easier to scale on Fly + Vercel edge.
- Observability: Langfuse self-hosted on Fly + Sentry + OTel collector.

## Done when

- Every route in the original brief is implemented + has an integration test.
- `/readyz` returns 200 only when Postgres + Redis + Neo4j are reachable.
- Clerk JWT verified; RBAC denials covered by tests.
- Rate limit middleware live with sensible defaults.
- `packages/schemas/ts/` codegen runs in CI and frontend consumes it.
- API deploys via `.github/workflows/deploy-api.yml` to Fly.io staging.

## Required reading

- `PLAN.md` §3.2, §10, §11.
- `ARCHITECTURE.md` §1–3.
- `.cursor/rules/20-python-style.mdc`, `40-memory-rules.mdc`, `50-security.mdc`, `60-testing.mdc`.
- `skills/add-a-backend-endpoint/SKILL.md`, `skills/db-migrations/SKILL.md`.
- `.cursor/subagent-briefs/02-backend-api.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Backend/API sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/02-backend-api-resume.md
  3. .cursor/subagent-briefs/02-backend-api.md
  4. PLAN.md §3.2, §10, §11; ARCHITECTURE.md §1–3
  5. skills/add-a-backend-endpoint/SKILL.md, skills/db-migrations/SKILL.md
  6. .cursor/rules/{20,40,50,60}-*.mdc

Then implement Phase 2 in this order, one PR per step:
  1. Real Clerk JWT verification + RBAC + per-row policy helpers
  2. Routes: /v1/agents, /v1/learners/me, /v1/lessons/{id}, /v1/progress
  3. /readyz checks against Postgres + Redis + Neo4j
  4. Redis sliding-window rate limiting per (learner_id, route)
  5. Pydantic → TypeScript codegen into packages/schemas/ts/
  6. OpenTelemetry + Langfuse + Sentry wiring
  7. Integration tests (use docker-compose)
  8. Fly.io config under infra/fly/asf-api.toml; ensure deploy-api.yml is green

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. review-bugbot on each. review-security on auth PRs.
  - Coordinate by writing comments on PRs (or ADRs); do not block on the user.

Final goal: API deployed to Fly staging, all routes live, SSE chat works against
the frontend, ready for Release Captain to promote to prod.
```
