"""Map service exceptions to MCP tool errors."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import TypeVar

from mcp.server.fastmcp.exceptions import ToolError
from pydantic import ValidationError

from schemas.errors import AppError

T = TypeVar("T")


def raise_tool_error(exc: Exception) -> None:
    if isinstance(exc, ToolError):
        raise exc
    if isinstance(exc, AppError):
        raise ToolError(f"{exc.code}: {exc.message}") from exc
    if isinstance(exc, ValidationError):
        raise ToolError(f"validation_failed: {exc}") from exc
    raise ToolError(f"internal_error: {exc}") from exc


async def invoke(awaitable: Awaitable[T]) -> T:
    try:
        return await awaitable
    except Exception as exc:
        raise_tool_error(exc)
        raise AssertionError("unreachable")
