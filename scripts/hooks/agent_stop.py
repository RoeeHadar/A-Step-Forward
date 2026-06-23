"""Cursor `agentStop` hook.

Appends a small session record to docs/sessions/<YYYY-MM-DD>.md and bumps the
MEMORY_SNAPSHOT.md "last session" pointer.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    summary = (payload.get("summary") or "").strip() or "(no summary provided)"
    agent = payload.get("agent") or "unknown"
    duration_s = payload.get("duration_s")
    today = dt.date.today().isoformat()
    sessions_dir = ROOT / "docs" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    out = sessions_dir / f"{today}.md"
    entry = (
        f"\n### {dt.datetime.now().strftime('%H:%M:%S')} — {agent}"
        + (f" — {duration_s:.0f}s\n" if isinstance(duration_s, (int, float)) else "\n")
        + f"{summary}\n"
    )
    if not out.exists():
        out.write_text(f"# Sessions — {today}\n", encoding="utf-8")
    with out.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    snapshot = ROOT / "MEMORY_SNAPSHOT.md"
    if snapshot.exists():
        text = snapshot.read_text(encoding="utf-8")
        marker = "<!-- LAST_SESSION -->"
        line = f"{marker}\nLast session: {today} ({agent})\n{marker}"
        if marker in text:
            head, _, _ = text.partition(marker)
            tail_split = text.split(marker)
            text = head + line + (tail_split[2] if len(tail_split) > 2 else "")
        else:
            text += f"\n\n{line}\n"
        snapshot.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
