# Obsidian Integration — Research & Setup

Prepared: 2026-07-02. This document records evaluated tools and how to activate the vault.

---

## 1. Architecture decision

**Primary MCP: MCPVault (`@bitbonsai/mcpvault`)** — filesystem-based, no Obsidian app required.

| Criterion | MCPVault | obsidian-native-mcp | cyanheads/obsidian-mcp-server |
|-----------|----------|---------------------|-------------------------------|
| Obsidian app required | No | No | Yes (+ Local REST API plugin) |
| Safe frontmatter | AST-aware (gray-matter) | Real YAML parser | REST API plugin |
| Concurrency safety | Path sandbox | Cryptographic hash preconditions | Atomic PATCH by heading |
| Cursor dev workflow | Excellent | Excellent | Good when Obsidian open |
| Dataview / Omnisearch | No (filesystem only) | No | Yes (via REST API) |
| npm package | `@bitbonsai/mcpvault` | `obsidian-native-mcp` | `obsidian-mcp-server` |
| 2026 activity | Very active (v0.11+) | Active | Active (v3.2.8) |

**Optional secondary MCP** (enable when Obsidian app is open for Dataview/Omnisearch):

- `obsidian-mcp-server` (cyanheads) + [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin

**Not chosen as primary:**

- `mcp-obsidian` (MarkusPfundstein) — REST-only; revived May 2026 but fewer tools than cyanheads
- `obsidian-mcp-tools` — archived; plugin-based semantic search
- Official filesystem MCP alone — no frontmatter-safe writes

---

## 2. MCP servers in this project

### Dev-time (`.cursor/mcp.json`)

| Server | Role |
|--------|------|
| `obsidian` | **NEW** — vault read/write/search via `scripts/mcp-obsidian-vault.mjs` |
| `filesystem` | Whole repo file access |
| `memory-project` | Dev/QA introspection of learner memory |
| `graphrag-project` | KG hybrid search during dev |
| `curriculum-project` | Lesson/path tools against Neon |
| `progress-project` | Mastery/planner introspection |
| `github`, `postgres`, `context7`, `shadcn`, `playwright`, `fetch`, `sequential-thinking` | Existing dev tooling |

### Runtime (in-product)

Configured by orchestrator — `mcp-servers/{memory,graphrag,curriculum,progress}`. The Obsidian vault is **build-time only**, not learner-facing.

---

## 3. Skills evaluated

### Installed in repo

| Skill | Path | Purpose |
|-------|------|---------|
| **use-obsidian-vault** | `skills/use-obsidian-vault/SKILL.md` | Project-specific vault workflows |

### Recommended external (optional install)

```bash
npx skills add https://github.com/bitbonsai/mcpvault --skill obsidian
```

Routes MCP vs git sync vs Obsidian CLI per operation. Useful if you also use Claude Code against the same vault.

### Patterns borrowed (not installed)

| Project | Useful pattern |
|---------|----------------|
| [devbrain](https://github.com/himanshusanecha/devbrain) | Git branch-scoped context notes + handoffs |
| [obsidian-claude-code-blueprint](https://github.com/mhenze-exaring/obsidian-claude-code-ai-assistant-blueprint) | PARA vault + Dataview task queries |
| Karpathy LLM wiki | Markdown-as-substrate for agent memory |

Future: branch-scoped `_active-context.md` per git branch (DevBrain-style).

---

## 4. Obsidian plugins (install manually in app)

Install via Settings → Community plugins. Recommended stack for this project:

| Plugin | Purpose for ASF |
|--------|-----------------|
| **Dataview** | Query `concepts/` by `expansion_status`, subject, Bagrut level |
| **Templater** | Instantiate [[templates/concept-note|concept]] and [[templates/lesson-draft|lesson draft]] |
| **Kanban** | Visual expansion batch board |
| **Periodic Notes** | Daily coordination logs |
| **Calendar** | Daily note navigation |
| **Git** | Vault version control (optional; repo git covers monorepo) |
| **Local REST API** | Only if enabling secondary MCP (cyanheads) |

Optional later:

- **Smart Connections** — semantic search over vault (complements MCPVault BM25)
- **Omnisearch** — better search when using REST API MCP

### Example Dataview query (expansion dashboard)

```dataview
TABLE expansion_status, subject, points_levels
FROM "concepts"
WHERE expansion_status != "done"
SORT expansion_status ASC
```

---

## 5. Vault layout

```
obsidian-vault/
├── CLAUDE.md                 # Agent constitution
├── _active-context.md        # Working memory / sprint focus
├── SETUP.md                  # This file
├── concepts/                 # 140 concept hub notes (generated)
├── curriculum/
│   ├── expansion-queue.md    # Generated queue dashboard
│   ├── expansion-dashboard.md # Dataview queries (requires Dataview plugin)
│   ├── goren-geva-checklist.md
│   └── drafts/               # Lesson staging markdown
├── coordination/streams/       # Brief summaries + wikilinks
├── research/README.md        # Index to repo research/
├── runbooks/scripts-index.md
├── templates/                # Templater-ready stubs
└── qa/README.md              # Index to .cursor/qa-loop/
```

---

## 6. Activation checklist

### A. Open vault in Obsidian

1. Obsidian → Open folder as vault → select `obsidian-vault/` inside this repo
2. Install plugins from §4 (minimum: Dataview + Templater)

### B. Enable MCP in Cursor

**Important (Windows):** Project `.cursor/mcp.json` servers often **do not show toggles** in Settings. Use the **global** config instead:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-cursor-obsidian-mcp.ps1
```

This writes `%USERPROFILE%\.cursor\mcp.json` with server **`asf-obsidian`**.

Full steps: see **`MCP-ENABLE.md`** in this folder.

1. Open **Cursor Settings** with **`Ctrl+Shift+J`** (not `Ctrl+,` editor settings)
2. **Tools & MCP** → enable master **Enable MCP servers** if off
3. Find **`asf-obsidian`** (check **Disabled** list if missing) → toggle **on** (green)
4. **Quit Cursor completely** and reopen the repo root folder
5. In Composer **Agent mode**, type `@` → **Tools** → look for **asf-obsidian** / mcpvault tools

**Windows / OneDrive note:** This repo path contains spaces. The MCP uses `scripts/mcp-obsidian-vault.cmd` (quoted paths) — do not switch back to bare `npx` or unquoted `node` args.

If `asf-obsidian` shows a red error:
- Open **Output** → dropdown **MCP** (or check `obsidian-vault/.mcp-startup.log` after toggling)
- Run manually: `scripts\mcp-obsidian-vault.cmd` from repo root (Ctrl+C to stop)
- Ensure `pnpm install` completed (`node_modules/@bitbonsai/mcpvault` exists)

### C. Sync generated content

```bash
node scripts/sync-obsidian-concepts.mjs
node scripts/sync-obsidian-expansion.mjs
```

Re-run after KG changes or expansion progress updates.

### D. Optional — secondary REST MCP

1. Install **Local REST API** plugin in Obsidian
2. Copy API key from plugin settings
3. Uncomment `obsidian-rest` block in `.cursor/mcp.json`
4. Set `OBSIDIAN_API_KEY` in Cursor env

### E. Optional — MCPVault community skill

```bash
npx skills add https://github.com/bitbonsai/mcpvault --skill obsidian
```

---

## 7. Workflow integration

```
cursor-expansion-queue.mjs --next 10
        ↓
concepts/<id>.md (read gaps, research links)
        ↓
curriculum/drafts/<id>.md (optional Goren/Geva staging)
        ↓
scripts/seed_data/lessons/<id>.json (source of truth)
        ↓
audit-lesson-depth.mjs --strict
        ↓
cursor-expansion-queue.mjs --mark <id>
        ↓
sync-obsidian-expansion.mjs (refresh dashboard)
```

---

## 8. What stays outside the vault

- `scripts/seed_data/lessons/*.json` — shippable corpus
- `evals/**` — CI gates
- `prompts/**` — versioned runtime prompts
- Neon learner memory — product data
- `kg-data.json` — code dependency (vault mirrors, doesn't replace)

---

## 9. Security notes

- Vault may contain curriculum strategy and QA findings — treat as private repo content
- MCPVault sandboxes to vault path; `.obsidian/` excluded by default
- Do not store secrets, `.env` values, or Neon credentials in vault notes
- Postgres MCP in `.cursor/mcp.json` already requires `DATABASE_URL_SYNC` — same rules apply

---

## 10. References

- [MCPVault](https://github.com/bitbonsai/mcpvault) · [mcpvault.org](https://mcpvault.org)
- [obsidian-native-mcp](https://github.com/usrivastava92/obsidian-native-mcp)
- [cyanheads/obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server)
- [Obsidian MCP comparison (ChatForest, 2026)](https://chatforest.com/reviews/obsidian-mcp-servers/)
- [DevBrain](https://github.com/himanshusanecha/devbrain)
- Project: `skills/use-obsidian-vault/SKILL.md`, `AGENTS.md`
