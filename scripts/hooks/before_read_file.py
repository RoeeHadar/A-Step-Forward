"""Cursor `beforeReadFile` hook.

If the agent is about to read a secrets-bearing file, redact the contents and
return a sanitized copy. Returns an alternative content payload.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SECRET_PATHS = ("/.env", "\\.env", "/secrets/", "\\secrets\\")
PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"
)
ENV_LINE_RE = re.compile(r"^([A-Z0-9_]+)\s*=\s*(.+)$")


def redact_env(text: str) -> str:
    out = []
    for line in text.splitlines():
        if line.strip().startswith("#") or not line.strip():
            out.append(line)
            continue
        m = ENV_LINE_RE.match(line)
        if not m:
            out.append(line)
            continue
        key, val = m.group(1), m.group(2)
        if not val or val.startswith('"' ) and val.endswith('"') and len(val) <= 2:
            out.append(line)
            continue
        out.append(f"{key}=***REDACTED***")
    return "\n".join(out)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    path = (payload.get("path") or "").replace("\\", "/").lower()
    if not path:
        return 0
    is_secret_path = any(s.replace("\\", "/").lower() in path for s in SECRET_PATHS) and ".env.example" not in path
    if not is_secret_path:
        return 0
    p = Path(payload["path"])
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    text = PRIVATE_KEY_RE.sub("-----PRIVATE KEY REDACTED-----", text)
    text = redact_env(text)
    sys.stdout.write(json.dumps({"content": text, "redacted": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
