# Enable Obsidian MCP in Cursor

Project `.cursor/mcp.json` is loaded by Cursor (check logs: `project-0-A Step Forward...-obsidian`), but **on Windows the Settings toggles often only appear for the global config** at `%USERPROFILE%\.cursor\mcp.json`.

This repo installs **global** MCP config automatically via `scripts/install-cursor-obsidian-mcp.ps1`.

## Quick enable (2 minutes)

### 1. Open **Cursor Settings** (not VS Code settings)

| Wrong | Right |
|-------|-------|
| `Ctrl+,` (Editor settings) | **`Ctrl+Shift+J`** (Cursor Settings) |

Or: Command Palette → **"Cursor Settings"**

### 2. Go to **Tools & MCP**

- Turn **ON** the master switch **"Enable MCP servers"** (if present)
- Look for server **`asf-obsidian`**
- If it is under a **Disabled** list, click it → **Enable**
- Toggle should turn **green**

### 3. Restart Cursor completely

Quit Cursor (File → Exit), reopen the repo folder:

`A Step Forward - AI Teaching Website` (repo root, not `obsidian-vault/`)

### 4. Verify in Agent chat

- Open **Composer** in **Agent** mode (`Ctrl+I`)
- Type `@` → **Tools** → look for **asf-obsidian** tools

## If `asf-obsidian` still does not appear — add manually

1. **Cursor Settings** (`Ctrl+Shift+J`) → **Tools & MCP**
2. Click **+ Add New MCP Server**
3. Fill in:

| Field | Value |
|-------|-------|
| Name | `asf-obsidian` |
| Type | `stdio` |
| Command | `node` |
| Args | full path to `scripts\mcp-obsidian-vault.mjs` (one arg; do **not** wrap in `cmd /c`) |

Example arg (adjust if your clone path differs):

```
C:\Users\roeeh\OneDrive\Desktop\Desktop\Cursor\A Step Forward - AI Teaching Website\scripts\mcp-obsidian-vault.mjs
```

**Why not `cmd /c`?** Paths with spaces (`A Step Forward`) get split by `cmd` unless carefully quoted — Cursor then tries to run `...\Desktop\A` and fails. Separate `node` + argv is space-safe.

4. Save → Enable → restart Cursor

## Test launcher manually

From repo root in PowerShell:

```powershell
pnpm install
node .\scripts\mcp-obsidian-vault.mjs
```

You should see no error (process waits for MCP input). Press `Ctrl+C` to stop.

Check log after Cursor tries to connect:

`obsidian-vault\.mcp-startup.log`

## Project vs global config

| File | Purpose |
|------|---------|
| `%USERPROFILE%\.cursor\mcp.json` | **Shows toggles in Settings** — `asf-obsidian` |
| `.cursor/mcp.json` (repo) | Team-shared servers (filesystem, github, …) — may not show toggles on Windows |

## Still stuck?

1. Output panel (`Ctrl+Shift+U`) → channel **MCP** or **MCP Logs**
2. Confirm workspace folder is repo root (status bar path ends with `A Step Forward - AI Teaching Website`)
3. Re-run: `powershell -ExecutionPolicy Bypass -File scripts/install-cursor-obsidian-mcp.ps1`
