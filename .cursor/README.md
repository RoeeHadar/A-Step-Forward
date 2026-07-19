# Cursor layout (canonical)

This file documents what Cursor auto-loads vs what is project documentation.

```text
repo-root/
├── AGENTS.md                 # Auto-loaded agent instructions (KEEP AT ROOT)
├── PLAN.md                   # Project plan — referenced, not auto-discovered
├── ARCHITECTURE.md           # Architecture — referenced, not auto-discovered
├── MEMORY_SNAPSHOT.md        # Injected by agentStart hook
│
├── packages/agents/          # PRODUCT runtime agents (NOT Cursor IDE config)
├── prompts/                  # PRODUCT runtime prompts
│
└── .cursor/
    ├── agents/               # Cursor-native custom subagents (auto-discovered)
    ├── skills/               # Project Agent Skills (auto-discovered)
    ├── rules/                # Always/globs rules (*.mdc)
    ├── hooks.json            # Hook config
    ├── hooks/                # Hook scripts
    ├── mcp.json              # Project MCP servers
    ├── subagent-briefs/      # Ticket/brief docs (NOT auto-discovered — read by agents/)
    ├── coordinator/          # Coordinator mandate/status (docs)
    └── qa-loop/              # QA simulation artifacts (docs)
```

## Do not confuse

| Path | Role |
|------|------|
| `.cursor/agents/` | Cursor IDE subagents (YAML frontmatter + prompt) |
| `.cursor/subagent-briefs/` | Human/dispatch tickets; pointed to by agents |
| `.cursor/skills/` | Cursor Agent Skills |
| `packages/agents/` | In-product Tutor/Mentor/… runtime code |
| Root `AGENTS.md` | Index for both worlds — must stay at repo root |
