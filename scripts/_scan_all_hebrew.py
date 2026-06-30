#!/usr/bin/env python3
"""Full scan of all curriculum concept lessons for Hebrew gaps."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts/seed_data/lessons"
CURRICULUM_PATH = ROOT / "apps/web/src/lib/curriculum-categories.ts"

MIN_HE_RATIO = 0.65
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def get_all_concepts() -> set[str]:
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


def effective_level_he(en: str, he: str) -> str:
    en = str(en or "").strip()
    he = str(he or "").strip()
    if not he or not has_hebrew(he):
        return ""
    if en and he == en:
        return ""
    if en and len(he) / len(en) < MIN_HE_RATIO:
        return ""
    return he


def resolve_section_he(section: dict) -> str:
    he = str(section.get("body_he_md", "") or "").strip()
    en = str(section.get("body_en_md", "") or "").strip()
    if not he or not en:
        return he if has_hebrew(he) else ""
    if he == en or not has_hebrew(he):
        return ""
    return he


def scan(path: Path, cid: str) -> str | None:
    if not path.exists():
        return "missing"
    d = json.loads(path.read_text(encoding="utf-8-sig"))
    if is_stub(d):
        return "stub"
    if not str(d.get("title_he", "")).strip():
        return "title_he"
    for sec in d.get("sections", []):
        parent = resolve_section_he(sec)
        en = sec.get("body_en_md", "")
        if en.strip() and not parent:
            return f"section:{sec.get('kind')}"
        for lv in (sec.get("body_by_level") or {}).values():
            en2 = lv.get("body_en_md", "")
            if not en2.strip():
                continue
            eff = effective_level_he(en2, lv.get("body_he_md", ""))
            if not eff and not parent:
                return f"level+section:{sec.get('kind')}"
    return None


def main() -> None:
    concepts = get_all_concepts()
    issues = []
    missing = []
    stubs = []
    ok = 0
    for cid in sorted(concepts):
        problem = scan(LESSONS_DIR / f"{cid}.json", cid)
        if problem == "missing":
            missing.append(cid)
        elif problem == "stub":
            stubs.append(cid)
        elif problem:
            issues.append((cid, problem))
        else:
            ok += 1
    print(f"Total: {len(concepts)}, OK: {ok}, Issues: {len(issues)}, Missing: {len(missing)}, Stubs: {len(stubs)}")
    for cid, p in issues:
        print(f"  {cid}: {p}")
    if missing:
        print(f"\nMissing ({len(missing)}):")
        for cid in missing:
            print(f"  {cid}")


if __name__ == "__main__":
    main()
