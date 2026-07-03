# A Step Forward — Obsidian Dev Vault

Standing instructions for any AI agent (Cursor Composer, Claude Code) working on this project.

## Primary reliance

**This vault is the main operational knowledge base for the monorepo.** Read vault notes before improvising architecture, curriculum sequencing, or product behavior.

| Priority | Read |
|----------|------|
| 1 | [[_active-context|Active context]] — current sprint |
| 2 | [[Home|Home]] — dashboards + links |
| 3 | [[curriculum/learning-path-architecture|Learning path & GraphRAG]] — how suggestions work |
| 4 | [[product/plan-and-memory|Plan & memory]] — shipped product rules |
| 5 | Repo `PLAN.md`, `AGENTS.md`, relevant `skills/` |

Shippable code lives in the repo; **this vault explains why and how** — KG topology, golden-path intent, agent rules, expansion status, coordination.

## Purpose

| Layer | Source of truth | This vault holds |
|-------|-----------------|------------------|
| Lessons | `scripts/seed_data/lessons/*.json` | Status, gaps, Goren/Geva drafts, wikilinks |
| Knowledge graph | `content/knowledge-graph/*.yaml` → `kg-data.json` | Concept hub notes in `concepts/` |
| Cross-subject edges | `apps/web/src/lib/kg-cross-edges.json` | [[curriculum/cross-subject-edges|Authoring runbook]] |
| Learning paths | `learning-plan.ts` + `neon-db.ts` | [[curriculum/learning-path-architecture|Architecture + gaps]] |
| Agent prompts | `prompts/<agent>/vN.md` | Eval links, change rationale |
| Learner memory | Neon Postgres | [[product/plan-and-memory|Product surface docs]] |
| Sub-agent briefs | `.cursor/subagent-briefs/` | [[coordination/streams/|Stream summaries]] |
| Research | `research/*.md` (repo root) | Linked excerpts + gap annotations |

## Session start protocol

1. Read [[_active-context|_active-context.md]] (or [[Home|Home]]).
2. For curriculum / KG / paths: [[curriculum/learning-path-architecture|learning-path-architecture]], [[curriculum/kg-workflow|kg-workflow]], [[curriculum/expansion-dashboard|expansion-dashboard]].
3. For frontend / plan / memory: [[product/plan-and-memory|plan-and-memory]], [[coordination/streams/01-frontend|01-frontend]].
4. Read the relevant project skill under `skills/` in the **repo**.
5. For concept work, open `concepts/<concept_id>.md` before editing lesson JSON.

## Universal rules

- **Bilingual**: Hebrew default for learner-facing prose; math always LTR in `$...$` / `$$...$$`.
- **No external links** in learner-facing content (product policy).
- **JSON lessons ship** — vault markdown is staging/coordination unless explicitly exported.
- **Plan changes**: template-only via Tutor sidebar — see [[product/plan-and-memory|plan-and-memory]].
- **Mark expansion progress** via `node scripts/cursor-expansion-queue.mjs --mark <id>` after validating JSON.
- **Commit vault + repo together** when architecture or coordination notes change.

## Key repo paths

```
PLAN.md                          # Master plan
ARCHITECTURE.md                  # Component map
AGENTS.md                        # Runtime + Cursor agent index
skills/use-obsidian-vault/       # Vault workflow skill
skills/use-learning-plan/        # Path planner contract
skills/cross-subject-kg/         # Edge authoring
apps/web/src/lib/learning-plan.ts
apps/web/src/lib/kg-cross-edges.json
apps/web/src/lib/concept-scope.ts
scripts/seed_data/lessons/       # 207 lesson JSON files
content/knowledge-graph/         # KG YAML source
.cursor/subagent-briefs/         # Sub-agent tickets
```

## MCP tools

Cursor should use the **`asf-obsidian`** MCP server (`scripts/mcp-obsidian-vault.cmd` → MCPVault) for vault read/write/search. Enable via [[MCP-ENABLE|MCP-ENABLE.md]]. Fallback: repo filesystem tools on `obsidian-vault/`.

## Related skills (repo)

- `skills/use-obsidian-vault/SKILL.md` — vault operations
- `skills/use-learning-plan/SKILL.md` — path planner
- `skills/cross-subject-kg/SKILL.md` — cross-subject edges
- `skills/expand-lessons-cursor/SKILL.md` — bulk lesson expansion
- `skills/coordinator-dispatch/SKILL.md` — multi-agent coordination
