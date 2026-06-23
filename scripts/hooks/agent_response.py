"""Cursor `agentResponse` hook.

Appends an audit line per agent response to data/agent_responses.jsonl. Used
later for cost dashboards and regression tracking against the offline evals.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data"
OUT_FILE = OUT_DIR / "agent_responses.jsonl"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    record = {
        "ts": time.time(),
        "agent": payload.get("agent"),
        "model": payload.get("model"),
        "input_tokens": payload.get("input_tokens"),
        "output_tokens": payload.get("output_tokens"),
        "latency_ms": payload.get("latency_ms"),
        "trace_id": payload.get("trace_id"),
        "stream": payload.get("stream"),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
