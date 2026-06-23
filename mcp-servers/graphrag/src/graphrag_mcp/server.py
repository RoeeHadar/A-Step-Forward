"""GraphRAG MCP server (stdio).

Exposes the KG retrieval surface defined in PLAN.md §6 and brief 06.
Uses the official Python MCP SDK.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from graphrag_mcp.tools import register_graphrag_tools
from graphrag_service.api import GraphRAGService


def create_server(*, svc: GraphRAGService | None = None) -> FastMCP:
    mcp = FastMCP(
        "graphrag",
        instructions=(
            "Knowledge graph MCP. Use for concept search, graph walks, prerequisites, "
            "next topics, and path explanations."
        ),
    )
    register_graphrag_tools(mcp, svc=svc)
    return mcp


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
