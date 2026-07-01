#!/usr/bin/env python3
"""Final teacher sign-off audit — practical checks only."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
HE = re.compile(r"[\u0590-\u05FF]")

REQUIRED = {
    "intro", "definition", "theory", "worked_example", "checkpoint",
    "method_guide", "exercise_set", "pitfall", "before_exam", "summary",
}


def main() -> int:
    fails: list[str] = []
    files = sorted(LESSONS_DIR.glob("*.json"))
    for fp in files:
        data = json.loads(fp.read_text(encoding="utf-8-sig"))
        name = fp.name
        sections = data.get("sections") or []
        kinds_list = [s.get("kind") for s in sections]
        kinds = set(kinds_list)

        if len(sections) < 12:
            fails.append(f"{name}: only {len(sections)} sections")
        if kinds & REQUIRED != REQUIRED:
            fails.append(f"{name}: missing kinds {sorted(REQUIRED - kinds)}")
        if sum(1 for k in kinds_list if k == "worked_example") < 3:
            fails.append(f"{name}: <3 worked examples")
        if sum(1 for k in kinds_list if k == "checkpoint") < 2:
            fails.append(f"{name}: <2 checkpoints")
        ex = max((len(s.get("exercises") or []) for s in sections if s.get("kind") == "exercise_set"), default=0)
        if ex < 8:
            fails.append(f"{name}: only {ex} exercises")

        body_en = sum(len(s.get("body_en_md") or "") for s in sections)
        body_he = sum(len(s.get("body_he_md") or s.get("body_he") or "") for s in sections)
        if body_en < 300:
            fails.append(f"{name}: empty/low EN content ({body_en})")
        if body_he < 300:
            fails.append(f"{name}: empty/low HE content ({body_he})")

        if not HE.search(data.get("title_he") or ""):
            fails.append(f"{name}: title_he not Hebrew")

        for i, s in enumerate(sections):
            en = (s.get("body_en_md") or "").strip()
            he = (s.get("body_he_md") or s.get("body_he") or "").strip()
            if len(en) > 250 and he == en:
                fails.append(f"{name}: section[{i}] HE is copy of EN")
            if s.get("kind") in {"intro", "theory", "pitfall", "summary", "before_exam", "method_guide"}:
                if len(en) > 100 and not HE.search(he):
                    fails.append(f"{name}: section[{i}] {s.get('kind')} missing Hebrew prose")

    print(f"Checked {len(files)} lessons")
    if fails:
        print(f"FAIL ({len(fails)} issues):")
        for f in fails[:30]:
            print(f"  - {f}")
        if len(fails) > 30:
            print(f"  ... +{len(fails)-30} more")
        return 1
    print("PASS — all lessons meet Goren/Geva + bilingual requirements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
