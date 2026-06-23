"""Tool helpers — references and call/result shapes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from schemas.agents import ToolRef


def mcp_tool(server: str, name: str) -> ToolRef:
    """Reference to a tool exposed by an MCP server."""
    return ToolRef(transport="mcp", server=server, name=name)


def local_tool(name: str) -> ToolRef:
    """Reference to a local Python function tool (used sparingly)."""
    return ToolRef(transport="local", server=None, name=name)


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    server: str | None = None


@dataclass
class ToolResult:
    call: ToolCall
    output: Any | None = None
    error: str | None = None
    latency_ms: int = 0
