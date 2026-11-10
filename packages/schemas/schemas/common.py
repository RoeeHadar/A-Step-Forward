from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import (
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    WrapValidator,
    model_validator,
)

from ._dynamic import FlexibleModel, flexible_model

# AS-113: the pre-AS-90 (3b7d2774) constrained aliases, used only by the AS-112
# entry-point request models (schemas.*.*Body / *Payload), not by shared models.
IDStr = Annotated[str, StringConstraints(min_length=1, max_length=128)]
ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]


def _datetime_keep_input(value: Any, handler: Any) -> Any:
    parsed = handler(value)
    return value if isinstance(value, str) else parsed.isoformat()


# AS-120: validated (and advertised) as the ref `datetime`, but the accepted value is
# kept as the ISO string the tip's str-typed shared models expect.
DateTimeStr = Annotated[datetime, WrapValidator(_datetime_keep_input)]


class Provenance(FlexibleModel):
    kind: str | None = None
    source: str | None = None
    agent: str | None = None
    timestamp: str | None = None
    # AS-90: fields read in production (was model_extra fallback).
    id: Any = None
    model: str | None = None


class Citation(FlexibleModel):
    title: str | None = None
    url: str | None = None
    agent: str | None = None
    # AS-90: fields read in production (was model_extra fallback).
    quote: str | None = None
    score: float | None = None
    source_id: str | None = None
    source_kind: str | None = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model


# ---------------------------------------------------------------------------
# AS-119: entry-point request models for the remaining pre-AS-90 bounds (3b7d2774).
# Same pattern as AS-112/113: these subclasses are used only where untrusted input
# enters (FastAPI bodies, MCP tool signatures, LLM output). The shared models, their
# defaults and the frozen AS90_DECLARED registry stay unchanged. Instances are still
# the base type, so the services are unchanged.


class ProvenanceBody(Provenance):
    """Provenance inside memory write bodies (3b7d2774 common.py:15-32)."""

    kind: Literal[
        "chat",
        "lesson",
        "assessment",
        "upload",
        "agent_reflection",
        "system",
        "import",
        "verification",
    ]
    id: IDStr | None = None

    # AS-120: ref types of model_version / ts (3b7d2774 common.py:31-32). They are not
    # declared on the shared Provenance (frozen AS90_DECLARED registry), so on the tip
    # they arrive as extras. They are checked here and stay extras, so the stored and
    # returned provenance is unchanged; the schema advertises the ref types.
    @model_validator(mode="before")
    @classmethod
    def _as120_ref_types(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for name, adapter in _PROVENANCE_REF_TYPES.items():
                if name in data:
                    try:
                        adapter.validate_python(data[name])
                    except ValueError as exc:
                        raise ValueError(f"provenance.{name}: {exc}") from None
        return data

    model_config = ConfigDict(
        json_schema_extra=lambda schema: schema["properties"].update(
            {
                "model_version": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "ts": {"type": "string", "format": "date-time"},
            }
        )
    )


_PROVENANCE_REF_TYPES: dict[str, TypeAdapter[Any]] = {
    "model_version": TypeAdapter(str | None),
    "ts": TypeAdapter(datetime),
}
