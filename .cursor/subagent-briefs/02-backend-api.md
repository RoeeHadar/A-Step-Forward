# 02 — Backend / API Gateway

## Goal
Build the FastAPI gateway in `apps/api`: auth, schema validation, rate limiting, telemetry, and HTTP/SSE routes that the frontend uses to talk to the Orchestrator, Memory Service, GraphRAG, and Curriculum/Progress services. Generate TypeScript types into `packages/schemas/ts/` from Pydantic models.

## In-scope files
- `apps/api/**`
- `packages/schemas/**` (Pydantic + generated TS)
- `infra/alembic/**` (DB migrations relevant to gateway-owned tables: users, sessions, audit)

## Out-of-scope
- Memory tables (04-memory) and GraphRAG (05-graphrag).
- Agent logic (03-agents).
- Frontend (01-frontend).

## Routes (Phase 1)
- `POST /v1/chat` (SSE) — stream agent reply; body = `ChatRequest`.
- `GET  /v1/agents` — list available agents.
- `GET  /v1/learners/me` — current learner profile.
- `GET  /v1/lessons/{id}` — lesson detail.
- `GET  /v1/progress` — current mastery summary.
- `GET/POST/PATCH/DELETE /v1/memory` — proxied to Memory Service.
- `POST /v1/graphrag/search` — proxied to GraphRAG.
- `GET /healthz`, `GET /readyz`, `GET /metrics`.

## Contracts
- Auth: Clerk JWT verification middleware. Inject `learner_id`, `role` into request context.
- All inputs/outputs are Pydantic models in `packages/schemas/`.
- Rate limit per (`learner_id`, `route`) via Redis sliding window.
- Errors: `packages/schemas/errors.py` exception handlers.
- OpenAPI tags: `chat`, `agents`, `learners`, `lessons`, `progress`, `memory`, `graphrag`, `admin`.

## Required reading
1. `PLAN.md` §3.2, §10, §11.
2. `ARCHITECTURE.md` §1–3.
3. `.cursor/rules/20-python-style.mdc`, `40-memory-rules.mdc`, `50-security.mdc`, `60-testing.mdc`.
4. `skills/add-a-backend-endpoint/SKILL.md`, `skills/db-migrations/SKILL.md`.

## Acceptance criteria
- `uv run uvicorn app.main:app --reload` works against docker-compose.
- All routes documented in OpenAPI; types codegen runs into `packages/schemas/ts/`.
- 100% of routes have auth dependency declared.
- Integration tests cover chat SSE + memory CRUD + RBAC denials.
- Sentry + Langfuse + OpenTelemetry wired.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§3.2, §10, §11), ARCHITECTURE.md (§1–3),
  .cursor/rules/20-python-style.mdc, 40-memory-rules.mdc, 50-security.mdc, 60-testing.mdc,
  skills/add-a-backend-endpoint/SKILL.md, skills/db-migrations/SKILL.md,
  .cursor/subagent-briefs/02-backend-api.md (this file).
Then implement Phase 1 routes per the brief.
Open one PR per route group. Run review-bugbot before each PR.
```
