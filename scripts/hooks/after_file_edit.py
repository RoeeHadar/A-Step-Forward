"""Cursor `afterFileEdit` hook: format & lint changed files.

Best-effort, non-blocking. Honors which tools are available on the system.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=False, capture_output=True, timeout=10)
    except Exception:
        pass


def format_python(path: Path) -> None:
    if shutil.which("ruff"):
        run(["ruff", "format", str(path)])
        run(["ruff", "check", "--fix", "--exit-zero", str(path)])


def format_ts(path: Path) -> None:
    if shutil.which("pnpm"):
        run(["pnpm", "exec", "prettier", "--write", "--log-level", "warn", str(path)])
        run(["pnpm", "exec", "eslint", "--fix", "--no-error-on-unmatched-pattern", str(path)])
    elif shutil.which("npx"):
        run(["npx", "--yes", "prettier", "--write", "--log-level", "warn", str(path)])


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    files = payload.get("files") or ([payload["path"]] if "path" in payload else [])
    for f in files:
        p = Path(f)
        if not p.exists():
            continue
        if p.suffix in {".py"}:
            format_python(p)
        elif p.suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".md", ".css"}:
            format_ts(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
