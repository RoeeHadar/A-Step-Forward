#!/usr/bin/env python3
"""Fix Hebrew gaps in lesson JSON: top-level sections + body_by_level fallbacks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts/seed_data/lessons"
CURRICULUM_PATH = ROOT / "apps/web/src/lib/curriculum-categories.ts"
TRANSLATIONS_PATH = ROOT / "scripts/_hebrew_section_translations.json"

HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
MIN_HE_RATIO = 0.65  # matches lesson-reader.tsx


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_all_concept_ids() -> set[str]:
    text = CURRICULUM_PATH.read_text(encoding="utf-8")
    concepts: set[str] = set()
    for block in re.findall(r"const [A-Z_0-9]+ = \[(.*?)\];", text, re.DOTALL):
        for c in re.findall(r"'([a-z][a-z0-9_]*)'", block):
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


def body_he_needs_fix(en: str, he: str) -> bool:
    en = str(en or "").strip()
    he = str(he or "").strip()
    if not en:
        return False
    if not he:
        return True
    if he == en:
        return True
    if not has_hebrew(he):
        return True
    if len(he) / len(en) < MIN_HE_RATIO:
        return True
    return False


def fix_section_he(section: dict, he_override: str | None = None) -> bool:
    """Fix top-level body_he_md. Returns True if changed."""
    en = section.get("body_en_md", section.get("body_en", ""))
    he = section.get("body_he_md", section.get("body_he", ""))
    if he_override and body_he_needs_fix(en, he):
        section["body_he_md"] = he_override
        return True
    return False


def fix_body_by_level(section: dict) -> int:
    """Clear bad body_by_level Hebrew so UI falls back to parent body_he_md."""
    changed = 0
    parent_he = section.get("body_he_md", "")
    parent_en = section.get("body_en_md", "")
    parent_he_ok = parent_he.strip() and not body_he_needs_fix(parent_en, parent_he)

    for level_data in (section.get("body_by_level") or {}).values():
        en = level_data.get("body_en_md", "")
        he = level_data.get("body_he_md", "")
        if not en.strip():
            continue
        if body_he_needs_fix(en, he):
            if parent_he_ok:
                level_data["body_he_md"] = ""
                changed += 1
            elif he.strip() == en.strip() or not has_hebrew(he):
                # Parent also bad — copy parent if we have override elsewhere
                level_data["body_he_md"] = ""
                changed += 1
    return changed


def apply_translations(d: dict, translations: dict[str, list[str]]) -> bool:
    cid = d.get("concept_id", "")
    if cid not in translations:
        return False
    he_bodies = translations[cid]
    sections = d.get("sections", [])
    if len(he_bodies) != len(sections):
        return False
    changed = False
    for i, he in enumerate(he_bodies):
        en = sections[i].get("body_en_md", "")
        current = sections[i].get("body_he_md", "")
        if body_he_needs_fix(en, current):
            sections[i]["body_he_md"] = he
            changed = True
    return changed


def main() -> None:
    translations: dict[str, list[str]] = {}
    if TRANSLATIONS_PATH.exists():
        translations = load_json(TRANSLATIONS_PATH)

    concept_ids = get_all_concept_ids()
    stats = {"files_updated": 0, "top_level": 0, "by_level": 0, "skipped_stub": 0, "missing": 0}

    for cid in sorted(concept_ids):
        path = LESSONS_DIR / f"{cid}.json"
        if not path.exists():
            stats["missing"] += 1
            continue
        d = load_json(path)
        if is_stub(d):
            stats["skipped_stub"] += 1
            continue

        file_changed = False
        if apply_translations(d, translations):
            stats["top_level"] += 1
            file_changed = True

        for sec in d.get("sections", []):
            en = sec.get("body_en_md", "")
            he = sec.get("body_he_md", "")
            if body_he_needs_fix(en, he) and not apply_translations({"concept_id": cid, "sections": [sec]}, translations):
                pass  # no translation available — leave for manual fix

            n = fix_body_by_level(sec)
            if n:
                stats["by_level"] += n
                file_changed = True

        if file_changed:
            save_json(path, d)
            stats["files_updated"] += 1
            print(f"Updated {cid}")

    print(f"\nDone: {stats}")


if __name__ == "__main__":
    main()
