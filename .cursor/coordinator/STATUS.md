# A Step Forward — Coordinator Status

Last updated: 2026-06-24T13:35:00Z by Coordinator session c9ee2952

## Acceptance checklist (per RESUME-README.md end-state)

- [x] `apps/web` deployed to Vercel — https://a-step-forward-waij.vercel.app
- [x] `/` returns 200 — verified 13:35Z (smoke after fed6cc1)
- [ ] Learner sign-up works — placeholder Clerk keys; user task §5b BLOCKED.md
- [ ] Learner can chat with Tutor and get a real response — needs Render API live + `GROQ_API_KEY` §5c
- [>] `apps/api` deployed to Render — **BLOCKED**: `https://asf-api.onrender.com/` returns `{"mensaje":"hola"}` (wrong app); `/healthz` 404
- [ ] `/healthz` 200 — pending correct Render service deploy
- [ ] `/readyz` 200 — pending Render + DB connectivity
- [ ] `/v1/chat` streams Tutor reply — pending Render + Groq key
- [x] Memory writes wired — `cef3a43` persists episodic row per chat turn via `MemoryService.write()` in orchestrator `stream()`
- [ ] Memory visible on live `/memory` — pending Render chat + Clerk sign-in
- [ ] Dreamer cron runs — not deployed
- [>] GraphRAG seeded with foundations-of-math — `kg_chunks` table exists; no ingestion yet
- [ ] CI green — needs audit on latest pushes (cef3a43, fed6cc1)
- [x] Public GitHub repo — https://github.com/RoeeHadar/A-Step-Forward
- [x] Polished README, LICENSE, SECURITY.md, ADR-0004 (Groq)
- [ ] Demo GIF — placeholder only

Legend: `[x]` done · `[>]` in progress · `[ ]` not started

## This session

- **Waited on frontend sub-agent** (`6dd13fd2`) — crashed with `resource_exhausted`; integrated surviving work manually as `fed6cc1`
- **Dispatched**: Memory persistence sub-agent (`8da852bd`) — wired episodic writes + integration test
- **Integrated commits**:
  - `cef3a43` — `feat(memory): wire episodic writes into orchestrator stream`
  - `fed6cc1` — `feat(frontend): polish empty states and Vercel env helper` (+ pyproject.toml uv fix)
- **Render polling** (3× over ~3 min): `/healthz` consistently 404; root returns unrelated JSON app
- **Live smoke** (post-push `fed6cc1`):
  - `/` → 200
  - `/api/health` → 200
  - `/sign-in` → 200
  - `/lessons/lesson-whole-numbers` → 200
  - `https://asf-api.onrender.com/healthz` → 404
- **Blocked**: Render service not our FastAPI app (see BLOCKED.md §5a note added this session)

## Next session priorities

1. **Human**: Deploy Render Blueprint from repo (or rename service if subdomain taken); confirm `/healthz` → `{"status":"ok"}`. Set env vars + `GROQ_API_KEY`.
2. **Human**: Run `scripts/vercel-set-env.ps1` with `VERCEL_TOKEN` to set `NEXT_PUBLIC_API_BASE_URL` to actual Render URL.
3. **Dispatch GraphRAG ingestion** (`05-graphrag-resume.md`) — seed `foundations-of-math` into `kg_chunks` with free HuggingFace embeddings.
4. **CI audit** — fix any red jobs on `cef3a43`/`fed6cc1`.

## Hands-off until manager check-in

true — natural checkpoint reached (memory stream done; backend blocked on human Render deploy)
