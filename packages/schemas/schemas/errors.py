from __future__ import annotations

from typing import Any

from ._dynamic import FlexibleError, flexible_error


class AppError(FlexibleError):
    pass


class NotFoundError(AppError):
    pass


class ValidationFailed(AppError):
    pass


class AuthError(AppError):
    pass


class RateLimited(AppError):
    pass


def __getattr__(name: str) -> Any:
    error = flexible_error(name)
    globals()[name] = error
    return error
