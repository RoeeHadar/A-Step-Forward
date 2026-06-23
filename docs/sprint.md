# Current Sprint

> Loaded into agent context by the `agentStart` hook. Keep tight.

## Phase 0 (this sprint, owner: Opus)

- [x] Master plan + architecture + AGENTS + CONTRIBUTING.
- [x] Cursor config: rules, mcp.json, hooks.json, sub-agent briefs.
- [x] Project skills authored.
- [x] Memory service foundation: schemas, stores, hygiene (PII, importance, decay, consolidation, conflict resolution, compression, compaction, verification, dreaming), retrieval (hybrid + policy), audit.
- [x] GraphRAG foundation: ontology, ingestion pipeline skeleton, service surface.
- [x] Agent framework: base classes, registry, Tutor stub, orchestrator with declarative router.
- [x] MCP server stubs: memory, graphrag, curriculum, progress.
- [x] FastAPI gateway scaffold with `/healthz`, `/v1/chat` (SSE), `/v1/memory`, `/v1/graphrag`.
- [x] Frontend scaffold: Next.js 15, Tailwind v4, shadcn ready, package.json, layout, landing.
- [x] docker-compose: Postgres+pgvector, Redis, Neo4j, Langfuse, MinIO, Mailhog, OTel.
- [x] ADRs for record-keeping and memory architecture.

## Phase 1 (next sprint, owner: sub-agents)

- Frontend implements pages from `01-frontend.md`.
- Backend implements full route set from `02-backend-api.md`.
- Agents 03 fills `run()` for Tutor + Q&A + Coach, plus full eval suites.
- Memory 04 swaps in real Postgres/pgvector implementation, full PII (Presidio), real importance LLM-judge.
- GraphRAG 05 wires Neo4j + real extraction pipeline.
- MCP 06 swaps stdio for the official MCP SDK transport.
- Infra 09 wires CI/CD and migrations.
- Security 10 implements Clerk verification, RBAC, audit tables.
