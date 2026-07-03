# A Step Forward — Obsidian Dev Vault

Standing instructions for any AI agent (Cursor Composer, Claude Code) working with this vault.

## Purpose

This vault is the **curriculum intelligence and coordination layer** for the A Step Forward monorepo. It is NOT the source of truth for shippable artifacts.

| Layer | Source of truth | This vault holds |
|-------|-----------------|------------------|
| Lessons | `scripts/seed_data/lessons/*.json` | Status, gaps, Goren/Geva drafts, wikilinks |
| Knowledge graph | `apps/web/src/lib/kg-data.json` | Concept hub notes in `concepts/` |
| Agent prompts | `prompts/<agent>/vN.md` | Eval links, change rationale |
| Learner memory | Neon Postgres | N/A (product runtime only) |
| Sub-agent briefs | `.cursor/subagent-briefs/` | Dispatch status, round summaries |
| Research | `research/*.md` (repo root) | Linked excerpts + gap annotations |

## Session start protocol

1. Read `_active-context.md` for current sprint focus.
2. If doing curriculum work, read `curriculum/expansion-queue.md` (regenerate via `node scripts/sync-obsidian-expansion.mjs`).
3. Read the relevant project skill under `skills/` in the **repo** (not this vault).
4. For concept work, open `concepts/<concept_id>.md` before editing lesson JSON.

## Universal rules

- **Bilingual**: Hebrew default for learner-facing prose; math always LTR in `$...$` / `$$...$$`.
- **No external links** in learner-facing content (product policy).
- **JSON lessons ship** — vault markdown is staging/coordination unless explicitly exported.
- **Mark expansion progress** via `node scripts/cursor-expansion-queue.mjs --mark <id>` after validating JSON.
- **Commit vault + repo together** when concept status or coordination notes change.

## Key repo paths

```
PLAN.md                          # Master plan
AGENTS.md                        # Runtime + Cursor agent index
skills/use-obsidian-vault/       # Vault workflow skill
scripts/cursor-expansion-queue.mjs
scripts/seed_data/lessons/       # 207 lesson JSON files
apps/web/src/lib/kg-data.json    # 140 concepts
research/                        # Bagrut/university research reports
.cursor/subagent-briefs/         # Sub-agent tickets
evals/agents/                    # Per-agent eval suites
```

## MCP tools

Cursor should use the **`asf-obsidian`** MCP server (`scripts/mcp-obsidian-vault.cmd` → MCPVault) for vault read/write/search. Enable via `obsidian-vault/MCP-ENABLE.md`. Fallback: repo filesystem tools on `obsidian-vault/`.

## Related skills (repo)

- `skills/use-obsidian-vault/SKILL.md` — vault operations
- `skills/expand-lessons-cursor/SKILL.md` — bulk lesson expansion
- `skills/author-lesson/SKILL.md` — lesson JSON schema
- `skills/coordinator-dispatch/SKILL.md` — multi-agent coordination
