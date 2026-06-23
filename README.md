# A Step Forward — AI Learning Center

An AI-native learning platform with a roster of specialized agents (Tutor, Mentor, Coach, Reviewer, Assessment, Research, …) that teach, assess, remember and evolve with each learner. Powered by a **multi-layered, self-healing memory system** and **GraphRAG** over a personal knowledge graph.

> Status: **Phase 0 — Foundation laid by Opus.** Implementation is delegated to Composer 2.5 / Cursor Auto sub-agents per `.cursor/subagent-briefs/`.

## Read these first

1. [`PLAN.md`](./PLAN.md) — the master plan (vision, architecture, stack, agents, memory, MCPs, hooks, skills, roadmap).
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md) — system architecture detail and data flows.
3. [`AGENTS.md`](./AGENTS.md) — the agent roster and contracts.
4. [`CONTRIBUTING.md`](./CONTRIBUTING.md) — how sub-agents should pick up and ship work.
5. `.cursor/subagent-briefs/` — one brief per work stream; the Composer 2.5 starter prompt is inside each.

## Repo layout (monorepo)

```
apps/web         — Next.js 15 frontend
apps/api         — FastAPI gateway
services/        — memory, graphrag, orchestrator, workers
packages/        — agents, schemas, ui
mcp-servers/     — memory, graphrag, curriculum, progress
prompts/         — versioned agent prompts
evals/           — promptfoo + DeepEval suites
infra/           — docker-compose, alembic migrations, k8s
skills/          — project-level Cursor skills for sub-agents
.cursor/         — rules, hooks, mcp.json, sub-agent briefs
docs/            — ADRs, sessions, design docs
```

## Local dev

See **[docs/infra/local-dev.md](docs/infra/local-dev.md)** for the full stack (Compose, migrations, ports).

```bash
cp .env.example .env.local
make up && make migrate
# Backend
cd apps/api && uv sync && uv run uvicorn app.main:app --reload
# Frontend
cd apps/web && pnpm install && pnpm dev
```

## Tech stack at a glance

* **Frontend** — Next.js 15 (App Router), TypeScript, Tailwind v4, shadcn/ui, Vercel AI SDK, TanStack Query, Zustand, Clerk.
* **Backend** — FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic, Celery/Arq.
* **Data** — Postgres 16 + pgvector, Redis, Neo4j, S3-compatible object storage.
* **AI** — LangGraph orchestration; Claude (primary), GPT (fallback), Gemini (multimodal); Voyage embeddings; Cohere/Voyage rerank; Langfuse traces; promptfoo + DeepEval.
* **Cursor** — Composer 2.5 / Auto sub-agents driven by `.cursor/subagent-briefs/`, with project skills under `skills/`.

## License

TBD.
