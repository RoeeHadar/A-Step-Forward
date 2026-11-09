from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from ._dynamic import FlexibleModel, flexible_model

# AS-113: the pre-AS-90 (3b7d2774) constrained aliases, used only by the AS-112
# entry-point request models (schemas.*.*Body / *Payload), not by shared models.
IDStr = Annotated[str, StringConstraints(min_length=1, max_length=128)]
ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]


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
