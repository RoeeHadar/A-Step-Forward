"""Typed exceptions used across services. Mapped to HTTP by FastAPI handlers."""

from __future__ import annotations


class AppError(Exception):
    """Base application error."""

    code: str = "app_error"
    http_status: int = 500

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
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
