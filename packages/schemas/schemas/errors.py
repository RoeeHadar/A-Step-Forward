"""Typed exceptions used across services. Mapped to HTTP by FastAPI handlers.

AS-99: ``code`` / ``http_status`` / ``to_dict`` and the ForbiddenError, PolicyViolation,
UpstreamError and BudgetExceeded classes are restored from the original module
(1516f4d4). The 01c27b73 stub dropped them, so apps/api's AppError handler raised
AttributeError (HTTP 500 instead of 401/403/404/...) and ForbiddenError/PolicyViolation
were not AppError subclasses at all. AppError still derives from FlexibleError.
"""

from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleError


class AppError(FlexibleError):
    """Base application error."""

    code: str = "app_error"
    http_status: int = 500

    def __init__(self, message: str = "", *, code: str | None = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        if code:
            self.code = code

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class AuthError(AppError):
    code = "auth_error"
    http_status = 401


class ForbiddenError(AppError):
    code = "forbidden"
    http_status = 403


class NotFoundError(AppError):
    code = "not_found"
    http_status = 404


class ValidationFailed(AppError):
    code = "validation_failed"
    http_status = 422


class PolicyViolation(AppError):
    """Memory access policy / RBAC / child-mode violation."""

    code = "policy_violation"
    http_status = 403


class RateLimited(AppError):
    code = "rate_limited"
    http_status = 429


class UpstreamError(AppError):
    """Failure in an LLM provider, MCP, or external API."""

    code = "upstream_error"
    http_status = 502


class BudgetExceeded(AppError):
    code = "budget_exceeded"
    http_status = 402


def __getattr__(name: str) -> Any:
    # Unknown error names still resolve (stub behaviour), now as AppError subclasses.
    error = type(name, (AppError,), {})
    globals()[name] = error
    return error
