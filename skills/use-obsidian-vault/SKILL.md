---
name: use-obsidian-vault
description: How to use the obsidian-vault/ dev knowledge base for curriculum expansion, sub-agent coordination, and research linking. Read BEFORE editing vault notes or syncing concept/expansion dashboards.
---

# Use Obsidian Vault

## When to use

- Curriculum expansion batches (`skills/expand-lessons-cursor`)
- Linking research gaps to KG concepts before JSON authoring
- Coordinating Cursor sub-agents (streams 07, 21–23)
- Staging Goren/Geva lesson prose before JSON export
- Recording QA findings from `.cursor/qa-loop/`

## Vault location

```
obsidian-vault/          # Open this folder as an Obsidian vault
├── CLAUDE.md            # Read every session
├── _active-context.md   # Working memory — update start/end of session
├── concepts/            # 156 concept hub notes (generated)
├── curriculum/          # Expansion queue, kg-workflow, drafts, Goren/Geva checklist
├── coordination/        # Stream brief summaries
├── templates/           # concept-note, lesson-draft
└── SETUP.md             # Full research + activation checklist
```

## MCP access (Cursor)

Primary server: **`asf-obsidian`** in `%USERPROFILE%\.cursor\mcp.json` (Windows global config — shows Settings toggles).

Install/repair:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-cursor-obsidian-mcp.ps1
```

Launcher: `scripts/mcp-obsidian-vault.cmd` → MCPVault over `obsidian-vault/`.

Project `.cursor/mcp.json` also lists `obsidian` plus other dev servers; on Windows those may not show toggles — use global `asf-obsidian` for vault work.

Typical tools: search notes, read/write/patch, manage tags/frontmatter, vault stats.

Fallback without MCP: use repo filesystem tools on `obsidian-vault/`.

Enable steps: `obsidian-vault/MCP-ENABLE.md`. Optional secondary: `obsidian-rest` when Obsidian app + Local REST API is running — see `obsidian-vault/SETUP.md`.

## Sync commands

```bash
# After editing content/knowledge-graph/*.yaml
node scripts/build-kg-json.mjs

# Regenerate concept notes from kg-data.json (safe — preserves Expansion notes section)
node scripts/sync-obsidian-concepts.mjs

# Refresh expansion queue dashboard
node scripts/sync-obsidian-expansion.mjs

# Shorthand (package.json)
pnpm vault:build-kg
pnpm vault:sync-concepts
pnpm vault:sync
```

Run `vault:build-kg` after any YAML KG change, then `vault:sync-concepts`. Run expansion sync after `--mark` or queue shifts.

## Concept note frontmatter

```yaml
concept_id: fractions_and_ratios
expansion_status: todo   # todo | in-progress | done | qa-gap | failed
subject: math
points_levels: [3pt, 4pt]
lesson_json: scripts/seed_data/lessons/fractions_and_ratios.json
```

Update `expansion_status` when starting/finishing work. Mirror `--mark` in `cursor-expansion-queue.mjs`.

**`data_completeness`** (set by sync):

| Value | Meaning |
|-------|---------|
| `full` | KG has skill_atoms + level_scope |
| `kg-sparse` | Lesson linked but KG metadata empty — run `pnpm vault:build-kg` + sync |
| `syllabus-only` | No resolvable lesson — add alias in `concept-aliases.ts` or author lesson |

## Lesson authoring workflow

1. Read `concepts/<concept_id>.md` + repo `skills/author-lesson/SKILL.md`
2. Optional: draft in `curriculum/drafts/<concept_id>.md` using `obsidian-vault/templates/lesson-draft.md`
3. Export to `scripts/seed_data/lessons/<concept_id>.json`
4. Validate: `node scripts/seed-lessons.mjs --dry-run` + `node scripts/audit-lesson-depth.mjs --strict --phase=4`
5. Mark: `node scripts/cursor-expansion-queue.mjs --mark <concept_id>`
6. Sync vault: `node scripts/sync-obsidian-expansion.mjs`

## Goren/Geva staging

Follow `obsidian-vault/curriculum/goren-geva-checklist.md` (from brief `22-content-writer.md`). Vault drafts are **not** shippable until exported to JSON.

## Coordination

- Update `_active-context.md` at session start/end
- Link stream work to `coordination/streams/<NN>-*.md`
- Do not duplicate full brief text — wikilink to `.cursor/subagent-briefs/`

## QA integration

Add findings under `## QA feedback` in concept notes. Source reports: `.cursor/qa-loop/` (index at `obsidian-vault/qa/README.md`).

## Pitfalls

- **JSON is source of truth** for lessons — vault markdown is staging/coordination
- Re-running concept sync **preserves** content below `## Expansion notes` but overwrites generated sections
- Do not store secrets or env values in vault notes
- Groq CI expansion is deprecated — use Cursor Composer per `expand-lessons-cursor`

## Optional external skill

```bash
npx skills add https://github.com/bitbonsai/mcpvault --skill obsidian
```

Routes MCP vs git backup workflows for vault-only operations.

## Related skills

- `expand-lessons-cursor` — bulk JSON expansion policy
- `author-lesson` — lesson JSON schema
- `expand-lesson-theory` — theory depth without breaking schema
- `coordinator-dispatch` — multi-agent round dispatch
