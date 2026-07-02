#!/usr/bin/env python3
"""Expand inner_product_gram_schmidt.json — bilingual MIN_WORDS + 80-word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/inner_product_gram_schmidt.json"

MIN = {
    "intro": (110, 90),
    "definition": (130, 110),
    "theory": (160, 130),
    "worked_example": (130, 110),
    "pitfall": (100, 85),
    "why_matters": (90, 75),
    "method_guide": (100, 85),
    "before_exam": (90, 75),
    "summary": (70, 60),
}


def wc(text: str) -> int:
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def he_ratio(text: str) -> float:
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def he_weak(he: str, en: str) -> bool:
    he, en = (he or "").strip(), (en or "").strip()
    if not he:
        return True
    if wc(he) / max(wc(en), 1) < 0.55:
        return True
    if he_ratio(he) < 0.15 and wc(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he):
    en = (
        f"**Why this is correct:**\n{why_en}\n\n"
        f"**How to think about it:**\n{how_en}\n\n"
        f"**Common slip:**\n{slip_en}\n\n"
        f"**Exam tip:**\n{tip_en}"
    )
    he = (
        f"**למה זה נכון:**\n{why_he}\n\n"
        f"**איך לחשוב על זה:**\n{how_he}\n\n"
        f"**טעות נפוצה:**\n{slip_he}\n\n"
        f"**טיפ לבחינה:**\n{tip_he}"
    )
    return en, he


# Content loaded from companion module to keep this file manageable
from _expand_inner_product_gram_schmidt_content import (
    SECTION_BODIES,
    CHECKPOINTS,
    EXPLANATIONS,
    EXERCISE_SET_BODY,
    EXERCISE_SOLUTIONS,
)


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    kind_map = {
        "intro": "intro",
        "definition": "definition",
        "theory": "theory",
        "method_guide": "method_guide",
        "pitfall": "pitfall",
        "why_matters": "why_matters",
        "before_exam": "before_exam",
        "summary": "summary",
    }
    we_idx = 0
    cp_idx = 0
    for s in data["sections"]:
        k = s["kind"]
        if k in kind_map:
            key = kind_map[k]
            s["body_en_md"] = SECTION_BODIES[key]["body_en_md"]
            s["body_he_md"] = SECTION_BODIES[key]["body_he_md"]
        elif k == "worked_example":
            we_idx += 1
            key = f"worked_example_{we_idx}"
            s["body_en_md"] = SECTION_BODIES[key]["body_en_md"]
            s["body_he_md"] = SECTION_BODIES[key]["body_he_md"]
        elif k == "checkpoint":
            sol = CHECKPOINTS[cp_idx]
            s["checkpoint_solution_en"] = sol["checkpoint_solution_en"]
            s["checkpoint_solution_he"] = sol["checkpoint_solution_he"]
            cp_idx += 1

    for i, q in enumerate(data["questions"]):
        q["explanation_en"], q["explanation_he"] = EXPLANATIONS[i]

    for s in data["sections"]:
        if s["kind"] == "exercise_set":
            s["body_en_md"] = EXERCISE_SET_BODY["body_en_md"]
            s["body_he_md"] = EXERCISE_SET_BODY["body_he_md"]
            for ex in s.get("exercises", []):
                sol = EXERCISE_SOLUTIONS.get(ex["id"])
                if sol:
                    ex["solution_en"] = sol["solution_en"]
                    ex["solution_he"] = sol["solution_he"]

    data["version"] = 2
    data["author"] = "cursor-claude-2026"

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    errs = []
    for s in data["sections"]:
        k = s["kind"]
        if k not in MIN:
            continue
        en_min, he_min = MIN[k]
        en, he = wc(s["body_en_md"]), wc(s["body_he_md"])
        if en < en_min:
            errs.append(f"{k}: en={en}<{en_min}")
        if he < he_min:
            errs.append(f"{k}: he={he}<{he_min}")
        if he_weak(s["body_he_md"], s["body_en_md"]):
            errs.append(f"{k}: he-weak")

    for q in data["questions"]:
        en, he = wc(q["explanation_en"]), wc(q["explanation_he"])
        if en < 80:
            errs.append(f"q{q['ord']}: expl-en={en}<80")
        if he < 80:
            errs.append(f"q{q['ord']}: expl-he={he}<80")
        if en > 150:
            errs.append(f"q{q['ord']}: expl-en={en}>150")
        if he > 150:
            errs.append(f"q{q['ord']}: expl-he={he}>150")
        if he_weak(q["explanation_he"], q["explanation_en"]):
            errs.append(f"q{q['ord']}: expl-he-weak")

    if errs:
        print("VALIDATION ERRORS:")
        for e in errs:
            print(" ", e)
        raise SystemExit(1)

    print("Section + explanation validation OK")
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit(r.returncode)
    print("seed-lessons --dry-run OK")


if __name__ == "__main__":
    main()
