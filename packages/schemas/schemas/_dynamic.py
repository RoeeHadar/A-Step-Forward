from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class FlexibleError(Exception):
    def __init__(self, message: str = "", **kwargs: Any) -> None:
        super().__init__(message)
        self.message = message
        self.extra = kwargs


class FlexibleEnum(StrEnum):
    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            return str.__new__(cls, value)
        return None


def flexible_model(name: str) -> type[FlexibleModel]:
    return type(name, (FlexibleModel,), {"__annotations__": {}})


def flexible_error(name: str) -> type[FlexibleError]:
    return type(name, (FlexibleError,), {})


def default_field(default: Any = None):
    return Field(default=default)
