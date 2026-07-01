#!/usr/bin/env python3
"""Scan lesson JSON for LaTeX escaping issues."""
from __future__ import annotations

import json
import re
from pathlib import Path

LESSONS = Path(__file__).resolve().parents[1] / "scripts" / "seed_data" / "lessons"


def scan_text(text: str) -> list[str]:
    issues = []
    if not text:
        return issues
    # After JSON parse, KaTeX needs single backslash commands: \lim not \\lim
    if "\\\\lim" in text or "\\\\to" in text or "\\\\frac" in text or "\\\\sin" in text:
        issues.append("double-backslash-commands")
    # Missing backslash entirely
    if re.search(r"\$\s*lim_", text):
        issues.append("bare-lim-in-math")
    if re.search(r"(?<![\\$])\\text\{", text):
        issues.append("text-cmd")
    # Broken \text without backslash
    if re.search(r"(?<![\\a-z])text\{", text, re.I):
        issues.append("bare-text-cmd")
    return issues


def main() -> None:
    double_bs = 0
    samples: list[str] = []
    for fp in sorted(LESSONS.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8-sig"))
        for s in data.get("sections", []):
            for key in ("body_en_md", "body_he_md", "checkpoint_solution_en", "checkpoint_solution_he"):
                t = s.get(key) or ""
                iss = scan_text(t)
                if "double-backslash-commands" in iss:
                    double_bs += 1
                    if len(samples) < 3:
                        idx = t.find("\\\\lim")
                        if idx == -1:
                            idx = t.find("\\\\frac")
                        samples.append(f"{fp.name}:{key} -> {t[max(0, idx - 10): idx + 40]!r}")
            for ex in s.get("exercises") or []:
                for key in ("body_en", "body_he", "solution_en", "solution_he"):
                    t = ex.get(key) or ""
                    if "\\\\lim" in t or "\\\\frac" in t:
                        double_bs += 1

    d = json.loads((LESSONS / "limits.json").read_text(encoding="utf-8-sig"))
    he = next(s["body_he_md"] for s in d["sections"] if s.get("kind") == "definition")

    print("double-backslash field hits:", double_bs)
    print("definition snippet:", repr(he[180:280]))
    print("backslash count before lim:", he[he.find("lim") - 3 : he.find("lim") + 8])
    for s in samples:
        print("sample:", s)


if __name__ == "__main__":
    main()
