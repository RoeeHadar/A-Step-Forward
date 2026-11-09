"""AS-96: opt-in guard for scripts that call a real LLM (Groq) outside the app clients.

Such a script refuses to run unless ALLOW_REAL_LLM=1 is set explicitly, the same
opt-in that the test suites keep unset. JS twin: scripts/lib/llm-script-guard.mjs.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping

LLM_OPT_IN_ENV = "ALLOW_REAL_LLM"
LLM_GUARD_EXIT_CODE = 3


def real_llm_allowed(env: Mapping[str, str] | None = None) -> bool:
    """True only when ALLOW_REAL_LLM is exactly "1"."""
    env = os.environ if env is None else env
    return env.get(LLM_OPT_IN_ENV, "").strip() == "1"


def require_real_llm_opt_in(script: str, *, why: str = "calls a real LLM (Groq)") -> None:
    """Print a clear message and exit nonzero when the opt-in is missing."""
    if real_llm_allowed():
        return
    print(
        f"[llm-guard] {script} {why} and is refused by default. "
        f"Set {LLM_OPT_IN_ENV}=1 to opt in explicitly (AS-96).",
        file=sys.stderr,
    )
    raise SystemExit(LLM_GUARD_EXIT_CODE)
