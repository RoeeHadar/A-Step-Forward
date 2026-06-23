"""Map service exceptions to MCP tool errors."""

from __future__ import annotations

from mcp.server.fastmcp.exceptions import ToolError
from pydantic import ValidationError

from schemas.errors import AppError


def raise_tool_error(exc: Exception) -> None:
    """Convert an application exception into an MCP ToolError."""
    if isinstance(exc, ToolError):
        raise exc
    if isinstance(exc, AppError):
        raise ToolError(f"{exc.code}: {exc.message}") from exc
    if isinstance(exc, ValidationError):
        raise ToolError(f"validation_failed: {exc}") from exc
    raise ToolError(f"internal_error: {exc}") from exc
