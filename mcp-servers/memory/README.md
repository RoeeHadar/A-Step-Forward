# memory MCP

MCP server exposing the Memory Service. Same tool surface used by agents at
runtime and by Cursor during development (registered in `.cursor/mcp.json`).

## Tools

| Tool                       | Purpose                                                       |
| -------------------------- | ------------------------------------------------------------- |
| `memory.write`             | Persist a new memory.                                         |
| `memory.search`            | Hybrid retrieval + policy filter.                             |
| `memory.timeline`          | Episodic timeline view.                                       |
| `memory.update`            | Patch (correction). Reason required.                          |
| `memory.delete`            | Soft or hard delete.                                          |
| `memory.dream_now`         | Trigger a dreaming pass (admin/internal).                     |
| `memory.consolidate`       | Force consolidation pass.                                     |
| `memory.compact_context`   | Compact a conversation to a target token budget.              |

## Run

```bash
python -m memory_mcp.server
```

Uses the official Python MCP SDK (stdio transport). Registered in `.cursor/mcp.json` as `memory-project`.
