#!/usr/bin/env python3
"""Fix common UTF-8 mojibake in English fields (em-dash, quotes)."""
from __future__ import annotations

import json
from pathlib import Path

LESSONS_DIR = Path(__file__).resolve().parents[1] / "scripts" / "seed_data" / "lessons"

REPLACEMENTS = [
    ("â€\x9d", "—"),
    ("â€\x99", "'"),
    ('â€"', "—"),
    ("â€”", "—"),
    ("â€˜", "'"),
    ("â€™", "'"),
    ("Ã—", "×"),
    ("Â°", "°"),
]


def fix_text(s: str) -> str:
    for old, new in REPLACEMENTS:
        s = s.replace(old, new)
    return s


def walk(obj) -> int:
    changed = 0
    if isinstance(obj, str):
        return 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                fixed = fix_text(v)
                if fixed != v:
                    obj[k] = fixed
                    changed += 1
            else:
                changed += walk(v)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                fixed = fix_text(item)
                if fixed != item:
                    obj[i] = fixed
                    changed += 1
            else:
                changed += walk(item)
    return changed


def main() -> None:
    n_files = 0
    for fp in sorted(LESSONS_DIR.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8-sig"))
        if walk(data):
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            n_files += 1
    print(f"Fixed English mojibake in {n_files} files")


if __name__ == "__main__":
    main()
