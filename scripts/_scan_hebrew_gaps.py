#!/usr/bin/env python3
"""Scan lesson files for Hebrew gaps — mirrors lesson-reader.tsx fallback logic."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts/seed_data/lessons"
CURRICULUM_PATH = ROOT / "apps/web/src/lib/curriculum-categories.ts"

PRIORITY_CATS = [
    "high_school_math_3pt",
    "high_school_math_4pt",
    "high_school_math_5pt",
    "hs_physics",
    "makhina",
]

MIN_HE_RATIO = 0.65
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def get_priority_concepts() -> set[str]:
    text = CURRICULUM_PATH.read_text(encoding="utf-8")
    concepts: set[str] = set()
    const_map = {
        "high_school_math_3pt": "MATH_3PT_CONCEPTS",
        "high_school_math_4pt": "MATH_4PT_CONCEPTS",
        "high_school_math_5pt": "MATH_5PT_CONCEPTS",
        "hs_physics": "HS_PHYSICS_CONCEPTS",
        "makhina": "MAKHINA_CONCEPTS",
    }
    for cat_id in PRIORITY_CATS:
        m = re.search(rf"const {const_map[cat_id]} = \[(.*?)\];", text, re.DOTALL)
        if m:
            for c in re.findall(r"'([a-z][a-z0-9_]*)'", m.group(1)):
                concepts.add(c)
    return concepts


def is_stub(d: dict) -> bool:
    sections = d.get("sections", [])
    if not sections:
        return True
    en = sections[0].get("body_en_md", sections[0].get("body_en", ""))
    return "Coming soon" in str(en) and not d.get("questions")


def has_hebrew(text: str) -> bool:
    return bool(HEBREW_RE.search(str(text)))


def effective_he(en: str, he: str) -> str:
    """What the UI would show for Hebrew (with truncation fallback)."""
    en = str(en or "").strip()
    he = str(he or "").strip()
    if not he:
        return ""
    if not has_hebrew(he):
        return ""
    if en and len(he) / len(en) < MIN_HE_RATIO:
        return ""
    return he


def resolve_section_he(section: dict) -> str:
    """Effective Hebrew for a section (top-level — no truncation ratio check in UI)."""
    en = section.get("body_en_md", "")
    he = section.get("body_he_md", "")
    he = str(he or "").strip()
    en = str(en or "").strip()
    if not he or not en:
        return he if has_hebrew(he) else ""
    if he == en or not has_hebrew(he):
        return ""
    return he


def resolve_level_he(section: dict, level_data: dict) -> str:
    """Effective Hebrew for a body_by_level variant."""
    parent_he = resolve_section_he(section)
    en = level_data.get("body_en_md", "")
    he = level_data.get("body_he_md", "")
    eff = effective_he(en, he)
    return eff if eff else parent_he


def scan_lesson(path: Path, concept_id: str) -> dict:
    if not path.exists():
        return {"concept_id": concept_id, "status": "missing_file"}
    d = json.loads(path.read_text(encoding="utf-8-sig"))
    if is_stub(d):
        return {"concept_id": concept_id, "status": "stub"}
    issues = []
    title_he = d.get("title_he", "")
    if not title_he or not str(title_he).strip():
        issues.append({"type": "title_he", "detail": "missing/empty"})
    for si, sec in enumerate(d.get("sections", [])):
        parent_eff = resolve_section_he(sec)
        parent_en = sec.get("body_en_md", "")
        if not parent_eff and parent_en.strip():
            issues.append({"type": "section", "index": si, "kind": sec.get("kind"), "problem": "no_hebrew"})
        for level, lv in (sec.get("body_by_level") or {}).items():
            en2 = lv.get("body_en_md", "")
            if not en2.strip():
                continue
            eff = resolve_level_he(sec, lv)
            if not eff:
                issues.append(
                    {
                        "type": "body_by_level",
                        "section": si,
                        "level": level,
                        "problem": "no_effective_hebrew",
                    }
                )
    if issues:
        return {
            "concept_id": concept_id,
            "status": "issues",
            "issues": issues,
            "issue_count": len(issues),
        }
    return {"concept_id": concept_id, "status": "ok"}


def main() -> None:
    concepts = get_priority_concepts()
    results = [scan_lesson(LESSONS_DIR / f"{cid}.json", cid) for cid in sorted(concepts)]
    problematic = [r for r in results if r["status"] == "issues"]
    missing = [r for r in results if r["status"] == "missing_file"]
    ok = [r for r in results if r["status"] == "ok"]

    print(f"Priority concepts: {len(concepts)}")
    print(f"OK: {len(ok)}, Issues: {len(problematic)}, Missing: {len(missing)}")
    print()
    for r in sorted(problematic, key=lambda x: -x["issue_count"]):
        print(f"{r['concept_id']}: {r['issue_count']} issues")
        for iss in r["issues"]:
            print(f"  {iss}")
    if missing:
        print("\n=== MISSING FILES ===")
        for r in missing:
            print(r["concept_id"])


if __name__ == "__main__":
    main()
