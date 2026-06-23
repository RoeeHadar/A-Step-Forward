"""Memory MCP server — Python MCP SDK (stdio).

Exposes the tool surface defined in PLAN.md §7 and
.cursor/subagent-briefs/06-mcp-servers.md.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from memory_mcp.tools import register_memory_tools
from memory_service.api import MemoryService


def create_server(*, svc: MemoryService | None = None) -> FastMCP:
    """Build the memory MCP server, optionally injecting a service for tests."""
    mcp = FastMCP(
        "memory",
        instructions=(
            "Memory service MCP. Use for learner memory writes, hybrid search, "
            "timeline views, corrections, and context compaction."
        ),
    )
    register_memory_tools(mcp, svc=svc)
    return mcp


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
