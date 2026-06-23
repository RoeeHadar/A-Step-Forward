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

### Round 2 acceptance (Release Captain enforces)

End-to-end deployed website + public GitHub repo + shareable demo. See
`.cursor/subagent-briefs/11-release-captain-resume.md` Phase A → D.
