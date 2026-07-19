---
name: build-an-mcp-server
description: How to build a new MCP server under mcp-servers/ using the Python MCP SDK, sharing Pydantic schemas with the rest of the project. Read BEFORE creating or modifying any MCP server.
---

# Build an MCP Server

## When to use
Creating a new server in `mcp-servers/<name>/` or adding/changing a tool on an existing one.

## Layout
```
mcp-servers/<name>/
  pyproject.toml
  README.md
  src/<name>_mcp/
    __init__.py
    server.py        # `python -m <name>_mcp.server` entrypoint
    tools/
      __init__.py
      <tool>.py
  tests/
    test_server.py
```

## Tool definition
- Inputs/outputs are Pydantic models from `packages/schemas/`. Share, don't duplicate.
- Descriptions are short, LLM-friendly, action-verb-first.
- Failure modes: return typed errors with `code` + `message`; never raise raw.
- All side effects go through the corresponding `services/<svc>` API; the MCP is a thin facade.

## Server skeleton
```python
from mcp.server import Server
from mcp.types import Tool
from schemas.memory import MemorySearchInput, MemoryRecord

app = Server("memory")

@app.tool(name="memory.search", description="Search learner memories (hybrid retrieval).")
async def memory_search(inp: MemorySearchInput) -> list[MemoryRecord]:
    ...
```

## Register with Cursor
- Add the server to `.cursor/mcp.json` (project-level) with the right `command`, `cwd`, `env`.

## Tests
- Unit test each tool's happy/sad paths.
- Smoke test that `python -m <name>_mcp.server` boots.

## Pitfalls
- Tool descriptions matter — they're what agents see. Keep them tight.
- Don't add chatty tools (e.g., "list everything"); prefer paginated/scoped tools.
- Don't expose raw DB writes; always go through the service layer.
