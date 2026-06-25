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

## Round 4 — Done (2026-06-25)

See `.cursor/subagent-briefs/13-coordinator-directive.md`.

| Priority | Status | Notes |
| -------- | ------ | ----- |
| P0 Merge Round 3 | **Done** | PR #15 + #16 merged; Render `/healthz` + `/readyz` green |
| P1 Branch triage | **Done** | [P1 audit](9b067447-50a5-43e9-9fed-fb992c6a878b): agents/MCP archived (already on main); infra branch surgical port only |
| P2 Content infra | **Blocked on Neon migrate** | `/v1/subjects` 500 until 0008/0009 applied — `migrate-neon.yml` added |
| P3 Chat verify | **API up** | healthz/readyz/warmup OK; live chat needs signed-in browser test |
| P4 Dependabot | **In progress** | Batch GH Actions PR (#5–#9) |
| P5 Resend | **Done** | Instructions in `BLOCKED.md` §2 item 6 |
| P6 Ongoing missions | **Ongoing** | Memory Postgres, GraphRAG context wiring, RBAC tests, real eval gates |

### Phase A (adaptive learning) — in flight

Branch `feat/adaptive-learning/phase-a`:
- Migration `0010_learner_model.py` (9 tables)
- KG YAML: math/physics high-school + university
- `scripts/seed_knowledge_graph.py` + `make seed-kg`
- CI workflow `migrate-neon.yml` (runs Alembic on Neon when migrations change)

**Next after Neon confirms 0010:** dispatch Backend (02) for LearnerModelService + onboarding API (A3+A4). **Do not start Phase B** until then.

**Deleted branches (2026-06-25):** `release/phase-1-integration`, `fix/coordinator-round3`, `fix/render-api-startup` (remote); `feat/curriculum/openstax-ingest`, `feat/frontend/chat-cold-start-fix` (local, 0-ahead / never on remote).

**Archived (do not merge/rebase):** `feat/agents/03-phase3-system-agents`, `feat/mcp/05-server-improvements`, `wip/agents-phase3-snapshot`. **Surgical port only:** `chore/infra/workspace-stabilization` (Alembic/uv slices from `9820532`, not whole branch).

**Build post-mortem:** ESLint unused-var + ESM `transpilePackages` rules in `skills/add-a-frontend-page/SKILL.md`.

## Adaptive learning system dispatched (2026-06-25)

See .cursor/subagent-briefs/14-adaptive-learning-architecture.md for the full architectural brief.

### New phases
| Phase | Focus | Key deliverable |
|-------|-------|-----------------|
| A | Data foundations | 0010_learner_model migration + prerequisite KG YAML + LearnerModelService |
| B | Diagnostic engine | Adaptive CAT, question bank, /diagnostic page |
| C | Planning engine | Weekly plan generator, /plan page |
| D | End-of-week quiz | Quiz service + time-limited /quiz page |
| E | Agent upgrades | Tutor v2 prompt, mastery injection, error diagnosis |

### Sequencing constraints
- Phase A migrations must land on Neon BEFORE B or C begin
- Tutor v2 ships only after eval-gated
- Nothing in /learn or /book is touched
