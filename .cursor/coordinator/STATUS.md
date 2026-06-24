# A Step Forward — Coordinator Status

Last updated: 2026-06-24T12:44:00Z by Manager (Opus)
Session: bootstrap (pre-Coordinator)

## Acceptance checklist (per RESUME-README.md end-state)

- [x] `apps/web` deployed to Vercel — https://a-step-forward-waij.vercel.app
- [x] `/` returns 200 — verified at 12:30Z
- [ ] Learner sign-up works — placeholder Clerk keys; user task to swap in real Dev keys
- [ ] Learner can chat with Tutor and get a real response — Groq provider shipped (ADR-0004), needs `GROQ_API_KEY` set on Render
- [>] `apps/api` deployed to Render — Dockerfile + render.yaml shipped; **build in progress** at https://asf-api.onrender.com (~15:22 UTC+3 start)
- [ ] `/healthz` 200 — pending Render build success
- [ ] `/readyz` 200 — pending; also needs Postgres+Redis+Neo4j ping checks
- [ ] `/v1/chat` streams Tutor reply — pending Render + Groq key
- [ ] Memory writes persist — `MemoryService` exists but not wired into `runner.stream`
- [ ] Dreamer cron runs — `services/workers/jobs/dreaming.py` exists, not deployed
- [>] GraphRAG seeded with foundations-of-math — `kg_chunks` table created; no ingestion yet
- [ ] CI green — last few pushes may have broken jobs; needs audit
- [x] Public GitHub repo — https://github.com/RoeeHadar/A-Step-Forward
- [x] Polished README — done in earlier round (hero, badges, agent matrix)
- [x] LICENSE — MIT
- [x] SECURITY.md — done
- [x] ADRs index — `docs/adr/README.md` + ADR-0004 (Groq) committed
- [ ] Demo GIF — placeholder image only

Legend: `[x]` done · `[>]` in progress · `[ ]` not started

## This session (Manager bootstrap)

- Read PLAN.md, AGENTS.md, RESUME-README.md, and the four resume briefs (01, 02, 04, 05, 11).
- Verified DB state: 16 tables in Neon, 1 course / 8 concepts / 9 lessons seeded.
- Verified live site: `/`, `/api/health`, `/sign-in`, `/sign-up` all 200.
- Dispatched 3 parallel Composer 2.5 sub-agents (curriculum, Groq LLM, frontend wiring). 2 of 3 done at time of writing.
- Wrote this MANDATE / ROADMAP / STATUS infrastructure.

## Open sub-agent
- Frontend wiring (`6dd13fd2-bb9e-4471-843c-42d1aeb2baba`) — still running as of 12:44Z. Tasks: set `NEXT_PUBLIC_API_BASE_URL` on Vercel, fix CORS, polish empty states, run e2e smoke.

## Next session priorities (Coordinator picks up here)

1. **Integrate frontend-wiring sub-agent** when it returns.
2. **Poll Render for backend health** (`A` in ROADMAP). If green within 10 min → smoke `/v1/lessons/...` from live frontend; if red → debug Dockerfile and push fix.
3. **Dispatch Memory persistence sub-agent** (`B`) in parallel with Render polling — disjoint files (it touches `services/orchestrator/`, `services/memory/`, `packages/agents/agents/learner_facing/note_taker/`).
4. **Dispatch GraphRAG ingestion sub-agent** (`D`) only after Memory persistence is in flight or done, to avoid `services/` conflicts.

## Hands-off until manager check-in
true — Coordinator will return on natural checkpoint (2 streams done, blocker hit, or end-state reached).
