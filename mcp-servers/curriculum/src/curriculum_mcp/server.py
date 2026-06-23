"""Curriculum MCP server — Python MCP SDK (stdio)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from curriculum_mcp.tools import register_curriculum_tools
from curriculum_service.api import CurriculumService


def create_server(*, svc: CurriculumService | None = None) -> FastMCP:
    mcp = FastMCP(
        "curriculum",
        instructions="Curriculum MCP. Browse courses, lessons, and personalized learning paths.",
    )
    register_curriculum_tools(mcp, svc=svc)
    return mcp


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
