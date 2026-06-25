# Current Sprint

> Loaded into agent context by the `agentStart` hook. Keep tight.

## Round 1 — Phase 0 (DONE, owner: Opus)

Foundation laid: master plan, architecture, AGENTS, rules, hooks, skills, all
service skeletons (memory, GraphRAG, agents, orchestrator, MCPs, API, frontend,
infra). See git log on `main`. All Phase-0 smoke tests green.

## Round 2 — Phase 1/2 (NOW, owner: stream sub-agents)

Per-stream **resume briefs** at `.cursor/subagent-briefs/NN-<stream>-resume.md`
are the paste-and-go prompts. Locked decisions in `RESUME-README.md` are
project policy — sub-agents do not ask the user.

### Where each stream is right now

| # | Stream | State | Tip branch |
| - | ------ | ----- | ---------- |
| 01 | Frontend | 9-branch stack covering all Phase-1 pages; nothing merged | `feat/frontend/09-educator-admin` |
| 02 | Backend / API | Phase-1 routes on `main` (chat SSE, memory CRUD, GraphRAG search); Phase-2 to go | `main` |
| 03 | Agents | 6 Phase-2 agents on `main`; Phase-3 (research/kg_builder/content_curator) preserved on `wip/agents-phase3-snapshot` | `main` + WIP |
| 04 | Memory | Phase-0 hygiene + retrieval scaffolds on `main`; Phase-2 (Postgres + Voyage + Presidio + Dreamer) to go | `main` |
| 05 | GraphRAG | 4-branch stack: ontology, ingestion, retrieval, MCP+evals; nothing merged | `feat/graphrag/04-mcp-evals` |
| 06 | MCP servers | 4-branch stack (memory, graphrag, curriculum, progress) on `mcp-stack-base`; nothing merged | `feat/mcp/04-progress` |
| 07 | Curriculum | Service skeleton on `main`; Phase-1 course content + seeder to go | `main` |
| 08 | Evals & QA | 8 agent eval folders + orchestrator routing test + qa citation test on `main`; Phase-3 evals on WIP | `main` |
| 09 | Infra / DevOps | docker-compose, alembic, 6 deploy workflow files, Makefile on `main`; workspace stabilization on WIP | `main` + WIP |
| 10 | Security / Safety | Only `safety_moderation` eval YAMLs (80 lines); rest to do | `feat/security/10-safety-hardening` |
| 11 | **Release Captain** | NEW this round — coordinates merges, deploys, launch | — |

## Round 3 — Active (2026-06-25, from supervisor)

### Implementation status (session fix/coordinator-round3)

| Priority | Status | Notes |
| -------- | ------ | ----- |
| P0 Chat cold-start | **Done** | 55s timeout, fire-and-forget warmup + 2s grace, waking banner after 3s |
| P1 Content pipeline | **Done (code)** | Migrations 0008/0009, `scripts/ingest_learning_db.py`, `/v1/subjects/*`, `/learn/*` UI — run `make ingest` to populate |
| P2 Booking `/book` | **Done** | Form + `POST /api/book` → Resend email or `bookings` table via API |
| P3 Free/Premium UI | **Done** | Public `/learn`, Premium badge on chat + tutor CTA on subject pages |
| P4 Branch triage | **Done** | See below |
| P5 Prior missions | **Ongoing** | Memory/GraphRAG/MCP/evals unchanged this session |

### Branch triage (2026-06-25)

| Branch | Ahead of main | Action |
| ------ | ------------- | ------ |
| `feat/agents/03-phase3-system-agents` | 1 commit (Research, KG Builder, Content Curator) | **Open PR** — material value not on main |
| `feat/mcp/05-server-improvements` | 1 commit (typed errors, tool expansions, tests) | **Open PR** — cherry-pick or merge |
| `chore/infra/workspace-stabilization` | 1 commit (pyproject/ruff/alembic) | Review vs main; likely partial merge |
| `release/phase-1-integration` | Stale (main 3+ commits ahead) | **Archive** — integration complete on main |
| `feat/curriculum/openstax-ingest` | Not on remote | **Superseded** by Learning Database pipeline (P1) |
| `feat/frontend/chat-cold-start-fix` | Not on remote | **Superseded** by P0 fix on `fix/coordinator-round3` |
| `feat/frontend/hebrew-rtl-default` | Not on remote | RTL defaults already on main — no action |
| `feat/frontend/visual-polish` | Not on remote | Visual polish already on main — no action |

### New priorities dispatched

| Priority | Task | Brief |
| -------- | ---- | ----- |
| P0 | Fix chat — AI agent unreachable (mock fallback is showing) | `12-coordinator-directive.md §P0` |
| P1 | Content pipeline: Learning Database (76 PDFs) → Postgres + website | `12-coordinator-directive.md §P1` |
| P2 | Private lesson booking page (`/book`) | `12-coordinator-directive.md §P2` |
| P3 | Free vs Premium tier structure | `12-coordinator-directive.md §P3` |
| P4 | In-flight branch triage | `12-coordinator-directive.md §P4` |
| P5 | Continue previous missions (memory, GraphRAG, MCP, evals, security) | `12-coordinator-directive.md §P5` |

**User constraints**: No key rotation yet. Learning Database folder is `.gitignore`d (PDFs). No payment integration now (Premium tier is free structurally). Bagrut tests are drag-and-drop PDF viewer only.

### Round 2 acceptance (Release Captain enforces)

End-to-end deployed website + public GitHub repo + shareable demo. See
`.cursor/subagent-briefs/11-release-captain-resume.md` Phase A → D.

## Round 4 tasks dispatched (2026-06-25 13:41)

See .cursor/subagent-briefs/13-coordinator-directive.md for the full directive.

| Priority | Task |
| --- | --- |
| P0 | Merge ix/coordinator-round3 ? main once Vercel preview is green |
| P1 | Triage 3 diverged in-flight branches; delete superseded ones |
| P2 | Verify content DB migrations on Neon; document ingest command |
| P3 | Verify chat works with real AI response post-deploy |
| P4 | Batch-merge safe Dependabot PRs (8 open) |
| P5 | Add Resend API key instructions to BLOCKED.md |
| P6 | Continue memory, GraphRAG, security, evals missions |

**Build post-mortem logged**: ESLint unused-var + ESM transpilePackages rules now in skills/add-a-frontend-page/SKILL.md.
