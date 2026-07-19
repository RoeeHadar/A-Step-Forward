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


def check_lesson_math(path: Path) -> None:
    """Warn (non-blocking) if an edited lesson JSON has broken math notation.

    The blocking gate lives in CI (`audit-lesson-math.mjs --strict`); this just
    gives fast feedback while authoring so notation is fixed before commit.
    """
    parts = path.as_posix()
    if "scripts/seed_data/lessons/" not in parts or path.suffix != ".json":
        return
    if not shutil.which("node"):
        return
    concept = path.stem
    try:
        res = subprocess.run(
            ["node", "scripts/audit-lesson-math.mjs", f"--only={concept}", "--strict"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception:
        return
    if res.returncode != 0:
        sys.stderr.write(
            f"[math-notation] '{concept}' has broken math — run `node scripts/fix-lesson-math.mjs` "
            f"and fix the rest before commit (CI will block it):\n{res.stdout[-1500:]}\n"
        )


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
        check_lesson_math(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
