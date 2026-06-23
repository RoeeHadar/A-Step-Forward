"""KG Builder tool references."""

from __future__ import annotations

from agents.base.tools import mcp_tool
from schemas.agents import ToolRef

TOOLS: list[ToolRef] = [
    mcp_tool("graphrag", "kg.extract_entities"),
    mcp_tool("graphrag", "kg.write_triples"),
    mcp_tool("memory", "memory.search"),
]
