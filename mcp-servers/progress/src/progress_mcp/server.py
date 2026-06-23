"""Progress MCP server — Python MCP SDK (stdio)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from progress_mcp.facade import ProgressFacade
from progress_mcp.tools import register_progress_tools


def create_server(*, facade: ProgressFacade | None = None) -> FastMCP:
    mcp = FastMCP(
        "progress",
        instructions="Progress MCP. Read mastery snapshots, gaps, streaks, and update mastery scores.",
    )
    register_progress_tools(mcp, facade=facade)
    return mcp


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
