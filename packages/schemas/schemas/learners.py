"""Learner profile schemas."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from ._compat import StrEnum
from .common import IDStr


class LearnerRole(StrEnum):
    LEARNER = "learner"
    EDUCATOR = "educator"
    ADMIN = "admin"
    PARENT = "parent"


class LearnerProfile(BaseModel):
    """Current learner profile returned by GET /v1/learners/me."""

    id: IDStr
    clerk_user_id: IDStr | None = None
    display_name: str
    email: str | None = None
    age: int | None = Field(default=None, ge=0, le=120)
    child_mode: bool = False
    locale: str = "en"
    role: LearnerRole = LearnerRole.LEARNER
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
