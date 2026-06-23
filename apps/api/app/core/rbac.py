"""RBAC dependency factory and per-row policy helpers.

Roles: learner, educator, admin, parent (PLAN.md §10).
Never trust client-supplied learner_id for reads — always filter by AuthCtx.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends

from schemas.errors import ForbiddenError, PolicyViolation
from schemas.learners import LearnerRole

from .audit import log_gateway_audit
from .auth import AuthCtx, require_learner

VALID_ROLES = frozenset(r.value for r in LearnerRole)


def require_role(*roles: str) -> Callable[..., Any]:
    """FastAPI dependency factory — caller must hold one of `roles`."""

    allowed = frozenset(roles)

    async def _dep(ctx: AuthCtx = Depends(require_learner)) -> AuthCtx:
        if ctx.role not in allowed:
            await log_gateway_audit(
                action="rbac.denied",
                learner_id=ctx.learner_id,
                route="rbac",
                metadata={"required_roles": sorted(allowed), "actual_role": ctx.role},
            )
            raise ForbiddenError(f"requires one of: {', '.join(sorted(allowed))}")
        return ctx

    return _dep


require_admin = require_role(LearnerRole.ADMIN.value, LearnerRole.EDUCATOR.value)
require_educator = require_role(LearnerRole.EDUCATOR.value, LearnerRole.ADMIN.value)
require_parent = require_role(LearnerRole.PARENT.value, LearnerRole.ADMIN.value)


def is_staff(role: str) -> bool:
    return role in (LearnerRole.ADMIN.value, LearnerRole.EDUCATOR.value)


def assert_learner_row_access(
    ctx: AuthCtx,
    target_learner_id: str,
    *,
    parent_child_ids: set[str] | None = None,
) -> None:
    """Enforce per-row policy: learners see only their rows; staff see all."""
    if is_staff(ctx.role):
        return
    if ctx.role == LearnerRole.PARENT.value:
        allowed = parent_child_ids or set()
        if target_learner_id not in allowed:
            raise PolicyViolation("parent may only access linked child profiles")
        return
    if ctx.learner_id != target_learner_id:
        raise PolicyViolation("cannot access another learner's data")


def enforce_learner_id(ctx: AuthCtx, body_learner_id: str) -> str:
    """Return the authorized learner_id, rejecting cross-tenant body overrides."""
    assert_learner_row_access(ctx, body_learner_id)
    if not is_staff(ctx.role) and ctx.role != LearnerRole.PARENT.value:
        return ctx.learner_id
    return body_learner_id
