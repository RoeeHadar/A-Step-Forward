"""Grader tool references."""

from __future__ import annotations

from agents.base.tools import mcp_tool
from schemas.agents import ToolRef

TOOLS: list[ToolRef] = [
    mcp_tool("memory", "memory.search"),
    mcp_tool("curriculum", "curriculum.get_rubric"),
    mcp_tool("curriculum", "curriculum.get_objectives"),
]
