"""Cursor `agentStart` hook.

Emits a small JSON blob with the latest memory snapshot, sprint goals and the
active sub-agent brief (if any). Cursor surfaces this back to the agent.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_text(p: Path, limit: int = 8000) -> str:
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        return text if len(text) <= limit else text[:limit] + "\n…(truncated)"
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def detect_active_brief() -> str:
    brief = os.environ.get("ACTIVE_SUBAGENT_BRIEF")
    if brief:
        return read_text(ROOT / ".cursor" / "subagent-briefs" / brief)
    return ""


def main() -> int:
    snapshot = read_text(ROOT / "MEMORY_SNAPSHOT.md")
    sprint = read_text(ROOT / "docs" / "sprint.md")
    brief = detect_active_brief()
    payload = {
        "context": [
            {"name": "MEMORY_SNAPSHOT.md", "content": snapshot},
            {"name": "docs/sprint.md", "content": sprint},
            {"name": "active_subagent_brief", "content": brief},
        ],
    }
    sys.stdout.write(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
