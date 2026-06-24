"""Cursor `beforeShellExecution` hook.

Blocks dangerous shell commands before they execute. Reads the hook payload
from stdin (JSON) and exits non-zero (with a message) to block.

Cursor hook contract (best-effort, may evolve):
  stdin:  {"command": "...", "cwd": "...", "agent": "..."}
  stdout: a message displayed to the agent if exit != 0
  exit:   0 = allow, non-zero = block
"""

from __future__ import annotations

import json
import re
import sys

DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\brm\s+-rf?\s+(/|~|\$HOME|\*)"),
        "Refusing recursive force-delete of root/home/wildcards.",
    ),
    (
        re.compile(r"\bgit\s+push\s+.*--force(-with-lease)?\b.*\b(main|master|prod|release)\b"),
        "Refusing force-push to a protected branch.",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\s+origin/(main|master|prod|release)"),
        "Refusing hard reset against protected branch.",
    ),
    (re.compile(r"\bdrop\s+database\b", re.IGNORECASE), "Refusing DROP DATABASE."),
    (
        re.compile(r"\btruncate\s+table\s+\w+\s*;?\s*$", re.IGNORECASE),
        "Refusing TRUNCATE without explicit WHERE/confirmation.",
    ),
    (re.compile(r"\bkubectl\s+delete\b"), "Refusing raw kubectl delete; use a reviewed manifest."),
    (re.compile(r"\bdd\s+if=.*\s+of=/dev/"), "Refusing dd to /dev/*."),
    (re.compile(r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;\s*:"), "Refusing fork bomb."),
    (
        re.compile(r"curl\s+.*\|\s*(sudo\s+)?(bash|sh|zsh)\b"),
        "Refusing curl|bash style remote execution.",
    ),
    (re.compile(r"\bchmod\s+-R\s+777\b"), "Refusing world-writable chmod -R 777."),
]


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    command: str = (payload.get("command") or "").strip()
    if not command:
        return 0
    for pat, reason in DANGEROUS_PATTERNS:
        if pat.search(command):
            sys.stdout.write(f"[before_shell] BLOCKED: {reason}\nCommand was: {command}\n")
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
