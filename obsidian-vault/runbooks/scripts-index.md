# Scripts Index

Canonical vs deprecated scripts for curriculum and vault maintenance. Update when adding new tooling.

## Canonical — use these

| Script | Purpose |
|--------|---------|
| `scripts/cursor-expansion-queue.mjs` | Priority queue for Cursor lesson expansion |
| `scripts/seed-lessons.mjs` | Validate + upsert lessons to Neon |
| `scripts/audit-lesson-depth.mjs` | Depth gate enforcement |
| `scripts/build-kg-json.mjs` | Compile `content/knowledge-graph/*.yaml` → `kg-data.json` |
| `scripts/sync-obsidian-concepts.mjs` | Regenerate vault concept notes from KG |
| `scripts/sync-obsidian-expansion.mjs` | Mirror expansion queue to vault markdown |
| `scripts/mcp-obsidian-vault.mjs` | Cursor MCP launcher (Windows-safe, no npx) |
| `scripts/mcp-obsidian-vault.cmd` | Windows wrapper for MCP launcher |
| `scripts/install-cursor-obsidian-mcp.ps1` | Write global `asf-obsidian` to `%USERPROFILE%\.cursor\mcp.json` |
| `pnpm vault:build-kg` | Compile KG YAML → `kg-data.json` |
| `pnpm vault:sync` | Run both obsidian sync scripts |
| `pnpm mcp:install-obsidian` | Install/repair global Obsidian MCP config |
| `scripts/update_index.py` | Regenerate lesson index bundles |

## Deprecated — do not use

| Script | Replacement |
|--------|-------------|
| `scripts/expand-lessons-substantive.mjs` | Cursor Composer (`skills/expand-lessons-cursor`) |
| `.github/workflows/expand-lessons-substantive.yml` | Guardrail only; policy is Cursor |

## Experimental / scratch (untracked)

| Pattern | Status |
|---------|--------|
| `scripts/_builders*.py` | Scratch — do not run in CI |
| `scripts/_gen_lessons.py` | Scratch |
| `scripts/_translate_lessons_he.py` | Scratch |
| `audit*.txt`, `_hebrew_gaps_scan.json` | Audit outputs — regenerate, do not commit |

## Lesson writers (domain-specific generators)

| Script | Domain |
|--------|--------|
| `scripts/write_probability_lessons.py` | Probability |
| `scripts/write_makhina_lessons.py` | מכינה |
| `scripts/generate_all_lessons.py` | Batch generation (verify before use) |

## Ingest

| Script | Input |
|--------|-------|
| `scripts/ingest_learning_db.py` | `Learning Database/` PDFs → `content_sections` |
