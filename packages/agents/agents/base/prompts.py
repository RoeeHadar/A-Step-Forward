"""Load versioned system prompts from the repo `prompts/` tree."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]


@lru_cache(maxsize=64)
def load_prompt(agent_name: str, version: str = "v1") -> str:
    """Return the contents of `prompts/<agent_name>/<version>.md`."""
    path = _REPO_ROOT / "prompts" / agent_name / f"{version}.md"
    if not path.is_file():
        msg = f"Prompt not found: {path.relative_to(_REPO_ROOT)}"
        raise FileNotFoundError(msg)
    return path.read_text(encoding="utf-8")
