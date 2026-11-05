"""AS-90 r1: serialize a response exactly as on base 5d1d9b63.

``response_model_exclude_unset`` would also drop pre-AS-90 defaults (see
items/AS-90/asf-coder.md per-site table), so these routes return the
response_model instance dumped with only *unset AS-90-declared* fields omitted.
``response_model`` stays on each route, so OpenAPI is unchanged.
"""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse
from schemas._as90_compat import dump_base_compat


def base_compat_response(content: Any) -> JSONResponse:
    return JSONResponse(content=dump_base_compat(content, by_alias=True))
