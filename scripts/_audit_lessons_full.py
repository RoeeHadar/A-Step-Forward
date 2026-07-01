#!/usr/bin/env python3
"""Full teacher audit for Goren/Geva lesson JSON + curriculum alignment."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
INDEX_PATH = ROOT / "apps" / "web" / "src" / "lib" / "lessons-index.generated.json"
ALIASES_PATH = ROOT / "apps" / "web" / "src" / "lib" / "concept-aliases.ts"

REQUIRED_KINDS = [
    "intro",
    "definition",
    "theory",
    "worked_example",
    "checkpoint",
    "method_guide",
    "exercise_set",
    "pitfall",
    "before_exam",
    "summary",
]

HE = re.compile(r"[\u0590-\u05FF]")
LATEX = re.compile(r"\$[^$]+\$|\\\(|\\\)|\\\[|\\\]")


def strip_latex(text: str) -> str:
    return LATEX.sub(" ", text)


def prose_hebrew_ratio(text: str) -> float:
    prose = strip_latex(text)
    he = len(HE.findall(prose))
    en = len(re.findall(r"[A-Za-z]", prose))
    total = he + en
    return he / total if total else 0.0


def has_hebrew(text: str) -> bool:
    return bool(HE.search(text or ""))


def load_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    if not ALIASES_PATH.exists():
        return aliases
    raw = ALIASES_PATH.read_text(encoding="utf-8")
    for m in re.finditer(r"^\s+(\w+):\s*'([^']+)'", raw, re.M):
        aliases[m.group(1)] = m.group(2)
    return aliases


def load_curriculum_concept_ids() -> set[str]:
    cat_path = ROOT / "apps" / "web" / "src" / "lib" / "curriculum-categories.ts"
    raw = cat_path.read_text(encoding="utf-8")
    return set(re.findall(r"'([a-z0-9_]+)'", raw)) - {
        "math",
        "physics",
        "en",
        "he",
        "3pt",
        "4pt",
        "5pt",
    }


def audit() -> dict[str, list]:
    issues: dict[str, list] = defaultdict(list)
    files = sorted(LESSONS_DIR.glob("*.json"))
    aliases = load_aliases()

    for fp in files:
        name = fp.name
        try:
            data = json.loads(fp.read_text(encoding="utf-8-sig"))
        except Exception as e:
            issues["parse_err"].append((name, str(e)))
            continue

        cid = data.get("concept_id") or fp.stem
        sections = data.get("sections") or []

        body_en = sum(len(s.get("body_en_md") or s.get("body_en") or "") for s in sections)
        body_he = sum(len(s.get("body_he_md") or s.get("body_he") or "") for s in sections)

        if not sections or body_en < 300:
            issues["empty"].append((name, len(sections), body_en))
            continue

        kinds = [s.get("kind") for s in sections]
        if "worked_example" not in kinds:
            issues["old_format"].append(name)

        missing = [k for k in REQUIRED_KINDS if k not in kinds]
        if missing:
            issues["missing_sections"].append((name, missing))

        if sum(1 for k in kinds if k == "worked_example") < 3:
            issues["few_worked_examples"].append(name)

        if sum(1 for k in kinds if k == "checkpoint") < 2:
            issues["few_checkpoints"].append(name)

        ex_count = max((len(s.get("exercises") or []) for s in sections if s.get("kind") == "exercise_set"), default=0)
        if ex_count < 8:
            issues["few_exercises"].append((name, ex_count))

        title_he = (data.get("title_he") or "").strip()
        title_en = (data.get("title_en") or "").strip()
        if not title_he:
            issues["no_title_he"].append(name)
        elif title_he == title_en and len(title_en) > 10:
            issues["title_copy"].append(name)
        elif not has_hebrew(title_he):
            issues["title_he_no_hebrew"].append(name)

        if body_he < 400:
            issues["low_hebrew"].append((name, body_he))

        for i, s in enumerate(sections):
            en = (s.get("body_en_md") or s.get("body_en") or "").strip()
            he = (s.get("body_he_md") or s.get("body_he") or "").strip()
            kind = s.get("kind")

            if kind in {"intro", "definition", "theory", "pitfall", "before_exam", "summary", "method_guide", "worked_example"}:
                if len(en) > 60 and has_hebrew(en) and prose_hebrew_ratio(en) > 0.45:
                    issues["he_in_en_body"].append((name, i, kind))
                if len(he) > 60:
                    if not has_hebrew(he):
                        issues["he_body_missing_hebrew"].append((name, i, kind))
                    elif he == en and len(en) > 120:
                        issues["he_body_copy_of_en"].append((name, i, kind))
                    elif prose_hebrew_ratio(he) < 0.12 and len(he) > 150:
                        issues["he_body_too_english"].append((name, i, kind))

            if kind == "checkpoint":
                for field in ("checkpoint_solution_en", "checkpoint_solution_he"):
                    val = s.get(field) or ""
                    if len(val) < 20:
                        issues["checkpoint_missing_solution"].append((name, i, field))
                    elif field.endswith("_he") and not has_hebrew(val):
                        issues["checkpoint_he_solution"].append((name, i))
                    elif field.endswith("_en") and has_hebrew(val) and prose_hebrew_ratio(val) > 0.5:
                        issues["checkpoint_en_solution"].append((name, i))

            if kind == "exercise_set":
                for j, ex in enumerate(s.get("exercises") or []):
                    be, bh = ex.get("body_en", ""), ex.get("body_he", "")
                    se, sh = ex.get("solution_en", ""), ex.get("solution_he", "")
                    if len(bh) > 30 and not has_hebrew(bh):
                        issues["exercise_no_hebrew"].append((name, j))
                    if len(be) > 30 and bh == be and has_hebrew(be) is False:
                        issues["exercise_he_copy"].append((name, j))

    # Curriculum alignment
    seed_ids = {fp.stem for fp in files}
    with INDEX_PATH.open(encoding="utf-8") as f:
        index_ids = {e["id"] for e in json.load(f)}

    issues["seed_not_in_index"] = sorted(seed_ids - index_ids)
    issues["index_not_in_seed"] = sorted(index_ids - seed_ids)

    # Load concept_ids from curriculum categories more precisely
    cat_raw = (ROOT / "apps" / "web" / "src" / "lib" / "curriculum-categories.ts").read_text(encoding="utf-8")
    curriculum_ids: set[str] = set()
    in_concept_ids = False
    for line in cat_raw.splitlines():
        if "concept_ids:" in line and "[" in line:
            in_concept_ids = True
        if in_concept_ids:
            curriculum_ids.update(re.findall(r"'([a-z][a-z0-9_]*)'", line))
            if "]," in line or line.strip().endswith("],"):
                in_concept_ids = False

    aliases_rev = {v: k for k, v in aliases.items()}
    resolved_seed = set()
    for sid in seed_ids:
        resolved_seed.add(sid)
        if sid in aliases_rev:
            resolved_seed.add(aliases_rev[sid])

    orphan_lessons = []
    for sid in sorted(seed_ids):
        if sid not in curriculum_ids and sid not in aliases.values():
            # lesson exists but no syllabus slot — flag only if not aliased target
            if not any(a == sid for a in aliases.values()):
                orphan_lessons.append(sid)
    issues["orphan_lessons"] = orphan_lessons[:30]  # cap report

    return issues


def main() -> int:
    issues = audit()
    total_files = len(list(LESSONS_DIR.glob("*.json")))
    blocking = [
        "parse_err",
        "empty",
        "old_format",
        "missing_sections",
        "few_worked_examples",
        "few_checkpoints",
        "few_exercises",
        "no_title_he",
        "he_body_missing_hebrew",
        "he_body_copy_of_en",
        "low_hebrew",
        "checkpoint_missing_solution",
        "exercise_no_hebrew",
    ]

    print(f"TOTAL FILES: {total_files}")
    fail = False
    for key in sorted(issues.keys()):
        vals = issues[key]
        print(f"\n=== {key} ({len(vals)}) ===")
        for x in vals[:15]:
            print(f"  {x!r}")
        if len(vals) > 15:
            print(f"  ... +{len(vals) - 15} more")
        if key in blocking and vals:
            fail = True

    if fail:
        print("\nAUDIT: FAIL — blocking issues found")
        return 1
    print("\nAUDIT: PASS — no blocking issues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
