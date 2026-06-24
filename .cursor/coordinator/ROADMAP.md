# Coordinator Roadmap

Priority-ordered list of streams to close out, with dependencies. The Coordinator picks the next 1–3 parallel-safe items each session.

## P0 — Critical path to a working demo

### A. Backend live on Render
- **Owner stream**: `02-backend-api`
- **State**: Dockerfile + `render.yaml` shipped. User created the Render Blueprint at ~15:22 UTC+3 with all env vars set. **Render is currently building.**
- **Done when**: `https://asf-api.onrender.com/healthz` returns 200 + `/v1/chat` streams real Groq tokens after `GROQ_API_KEY` is set.
- **Dispatch**: poll the URL every 60s for up to 10 min. When live, set `NEXT_PUBLIC_API_BASE_URL=https://asf-api.onrender.com` on Vercel (via API, in flight by frontend sub-agent), trigger empty-commit redeploy, smoke `/v1/lessons/lesson-whole-numbers` from the live frontend. If Render fails the build, debug the Dockerfile (most likely: `uv sync --frozen --package asf-api` step; the `uv.lock` may be stale).
- **Coord**: this is the SINGLE highest-priority item. Without backend, only lessons render (via the snapshot fallback shipped by the curriculum sub-agent).

### B. Memory persistence end-to-end
- **Owner stream**: `04-memory`
- **Brief**: `.cursor/subagent-briefs/04-memory-resume.md`
- **State**: tables exist in Neon (`semantic_memories`, `episodic_memories`, etc.). `MemoryService` exists. No writes actually happen during a chat turn.
- **Done when**:
  1. Sending a chat message produces a row in `episodic_memories`.
  2. Visiting `/memory` on the live site shows ≥1 row for the signed-in learner.
  3. The Note-Taker agent writes structured semantic memories after long sessions (or a worker batches this).
- **Dispatch**: Composer 2.5, 1 sub-agent. Tell it to read brief 04, wire `MemoryService.write()` into the orchestrator's `runner.stream`, add an integration test, and verify against Neon.

### C. Groq key + final chat smoke
- **Owner stream**: `11-release-captain` (you, via the manager)
- **State**: Groq provider shipped (see ADR-0004). `GROQ_API_KEY` not yet set on Render.
- **Done when**: user adds `GROQ_API_KEY=gsk_...` in the Render dashboard. Live chat returns Llama-3.3-70B text within ~3s.
- **Coord**: this is a 2-min human action. Document very clearly in `BLOCKED.md §5c` (already done by Groq sub-agent). When the user reports the key is set, smoke `/v1/chat`.

## P1 — Quality bar

### D. GraphRAG hybrid retrieval against seeded corpus
- **Owner stream**: `05-graphrag`
- **Brief**: `.cursor/subagent-briefs/05-graphrag-resume.md`
- **State**: `kg_chunks` table exists, GraphRAG service has retrieval modes (bm25/dense/hybrid/rerank), Neo4j AuraDB credentials set. Corpus is NOT yet chunked + embedded.
- **Done when**: ingesting the `foundations-of-math` markdown into `kg_chunks` (1024-dim embeddings via Voyage AI — but Voyage isn't free; **substitute** with HuggingFace `sentence-transformers/all-mpnet-base-v2` (768d) or any local/free embedding; document via ADR). `kg.hybrid` MCP tool returns ranked chunks for a query like "what is a fraction".
- **Dispatch**: Composer 2.5. Coordinator drafts the prompt; emphasize **no paid embedding APIs**.

### E. CI green across the board
- **Owner stream**: `09-infra` + `08-evals-qa`
- **State**: `.github/workflows/` has lint-test, deploy-web, deploy-api, evals. Latest pushes may have broken some jobs.
- **Done when**: latest commit on `main` shows all required checks green in `gh pr checks` (or `gh run list --limit 5`).
- **Dispatch**: Composer 2.5 to fix any red CI runs. Re-rebase if needed.

### F. Workers + Dreamer cron
- **Owner stream**: `04-memory` (Dreamer agent) + `09-infra` (Render Cron Job)
- **State**: `services/workers/` exists with `dreaming.py`, `decay.py`, `kg_ingest.py`. Not deployed.
- **Done when**: a Render Cron Job (`asf-workers`) runs `python -m workers.jobs.dreaming` nightly. (Alternative: GitHub Actions cron — free, doesn't need Render Background Workers which require paid tier.)
- **Dispatch**: Composer 2.5. Strongly prefer **GitHub Actions cron** over Render Background Workers (free tier limitation).

## P2 — Polish

### G. Demo screenshot + README polish
- **Owner stream**: `01-frontend` + `11-release-captain`
- **Done when**: README hero shows a real screenshot of the live site (not just the placeholder generated earlier).

### H. Educator + Admin pages functional
- **State**: `apps/web/src/app/(app)/educator/page.tsx` and `admin/page.tsx` exist as stubs.
- **Done when**: empty-state UI is acceptable (these are post-launch features).

### I. Evals threshold gates
- **Owner stream**: `08-evals-qa`
- **Done when**: at least the Tutor agent has `evals/agents/tutor/capability.yaml` + `safety.yaml` + `thresholds.yaml` and they run green in CI against the new Groq LLM (use mocked responses where possible to avoid spending free-tier quota in CI).

## Dependency graph

```
A (backend) ──┬─→ B (memory)
              ├─→ C (chat smoke)
              ├─→ D (graphrag hybrid)
              └─→ F (workers)
                       │
B + D ─────────────────┴─→ E (CI green) → G (polish) + I (eval gates) → DONE
```

`H` is independent and low priority.

## Notes for the Coordinator

- The most recent commits on `main` are from concurrent sub-agents (LLM, Curriculum, Frontend). Always `git pull --rebase` before starting any local work.
- The `pyproject.toml` workspace has a malformed `[tool.uv]` block (`python = "3.11"`) that confuses newer `uv` versions. If you need `uv` for migrations or testing, use the `.venv-infra/` venv that the manager already populated with pip-installed deps.
- Docker Desktop is running (WSL2 installed). You can use `docker run --rm postgres:16 psql "<url>" -c "<sql>"` for any Postgres operations.
- The frontend has a robust fallback path — when the backend is unreachable, lessons render from `apps/web/src/lib/seed-lessons.generated.json`. Don't rip out the fallback when wiring the live backend; keep both.
