#!/usr/bin/env python3
"""Fix mojibake Hebrew, missing summaries, and exercise Hebrew copies."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
HE = re.compile(r"[\u0590-\u05FF]")
MOJI_CHAR = "\u00d7"

PUNCT_FIXES = [
    ("â€”", "—"),
    ("â€“", "–"),
    ("â€˜", "'"),
    ("â€™", "'"),
    ("â€œ", '"'),
    ("â€\x9d", '"'),
    ("Â°", "°"),
    ("Â·", "·"),
    ("Â²", "²"),
    ("Â³", "³"),
    ("âˆŽ", "∎"),
    ("â†'", "→"),
    ("â‰ ", "≠"),
    ("â‰", "≠"),
    ("âˆ'", "−"),
    ("âˆ’", "−"),
]

CHAR_TO_BYTE: dict[str, int] = {}
for i in range(256):
    try:
        ch = bytes([i]).decode("cp1252")
    except UnicodeDecodeError:
        ch = bytes([i]).decode("latin-1")
    CHAR_TO_BYTE[ch] = i


def is_hebrew_key(key: str) -> bool:
    return key.endswith("_he") or key.endswith("_he_md") or key in {"title_he", "name_he"}


def clean_punct(s: str) -> str:
    for old, new in PUNCT_FIXES:
        s = s.replace(old, new)
    return s


def needs_decode(s: str) -> bool:
    if any(p in s for p, _ in PUNCT_FIXES):
        return True
    if MOJI_CHAR not in s:
        return False
    # Keep legitimate math multiplication sign " × ".
    return MOJI_CHAR in s.replace(" × ", "")


def fix_mojibake(s: str) -> tuple[str, bool]:
    if not isinstance(s, str) or not needs_decode(s):
        return s, False
    out = bytearray()
    for c in s:
        b = CHAR_TO_BYTE.get(c)
        if b is None and ord(c) < 256:
            b = ord(c)
        if b is None:
            return s, False
        out.append(b)
    try:
        fixed = clean_punct(out.decode("utf-8"))
    except UnicodeDecodeError:
        return s, False
    if not HE.search(fixed):
        return s, False
    return fixed, fixed != s


def walk_strings(obj) -> int:
    changed = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and is_hebrew_key(k):
                fixed, ok = fix_mojibake(v)
                if ok:
                    obj[k] = fixed
                    changed += 1
            elif isinstance(v, list) and k.endswith("_he"):
                for i, item in enumerate(v):
                    if isinstance(item, str):
                        fixed, ok = fix_mojibake(item)
                        if ok:
                            v[i] = fixed
                            changed += 1
            else:
                changed += walk_strings(v)
    elif isinstance(obj, list):
        for item in obj:
            changed += walk_strings(item)
    return changed


SUMMARY_TEMPLATES = {
    "limits": {
        "title_en": "Summary — Limits",
        "title_he": "סיכום — גבולות",
        "body_en_md": "- Direct substitution first; factor, conjugate, or L'Hôpital for $0/0$.\n- Memorize standard limits ($\\sin x/x$, etc.).\n- Check one-sided limits when the domain is restricted.\n- Compare degrees at infinity for rational functions.",
        "body_he_md": "- תמיד נסו הצבה ישירה; פירוק, צמוד או לופיטל עבור $0/0$.\n- שיננו גבולות סטנדרטיים ($\\sin x/x$ וכו').\n- בדקו גבולות חד-צדדיים כשהתחום מוגבל.\n- השוו מעלות ב-$\\infty$ לפונקציות רציונליות.",
    },
    "continuity": {
        "title_en": "Summary — Continuity",
        "title_he": "סיכום — רציפות",
        "body_en_md": "- $f$ is continuous at $a$ iff $\\lim_{x\\to a}f(x)=f(a)$.\n- Polynomials, trig, exp, and log are continuous on their domains.\n- Discontinuities: removable, jump, infinite.\n- IVT guarantees a root when signs change on a closed interval.",
        "body_he_md": "- $f$ רציפה ב-$a$ אם ורק אם $\\lim_{x\\to a}f(x)=f(a)$.\n- פולינומים, טריג, אקספוננט ולוג רציפים בתחומם.\n- סוגי אי-רציפות: ניתנת לתיקון, קפיצה, אינסופית.\n- משפט הערך הביניים מבטיח שורש כשיש החלפת סימן בקטע סגור.",
    },
    "limits_at_infinity": {
        "title_en": "Summary — Limits at Infinity",
        "title_he": "סיכום — גבולות באינסוף",
        "body_en_md": "- For rational functions: compare numerator/denominator degrees.\n- Divide by the highest power of $x$.\n- $e^x$ dominates polynomials; $\\ln x$ grows slower than any positive power.\n- Horizontal asymptotes come from finite limits at $\\pm\\infty$.",
        "body_he_md": "- בפונקציות רציונליות: השוו מעלות מונה ומכנה.\n- חלקו בחזקה הגבוהה ביותר של $x$.\n- $e^x$ שולט על פולינומים; $\\ln x$ גדל לאט מכל חזקה חיובית.\n- אסימפטוטות אופקיות מגיעות מגבול סופי ב-$\\pm\\infty$.",
    },
}


def add_missing_summaries(data: dict, cid: str) -> bool:
    kinds = [s.get("kind") for s in data.get("sections", [])]
    if "summary" in kinds or cid not in SUMMARY_TEMPLATES:
        return False
    tpl = SUMMARY_TEMPLATES[cid]
    data.setdefault("sections", []).append(
        {
            "kind": "summary",
            "title_en": tpl["title_en"],
            "title_he": tpl["title_he"],
            "body_en_md": tpl["body_en_md"],
            "body_he_md": tpl["body_he_md"],
        }
    )
    return True


def fix_exercise_copies(data: dict) -> int:
    changed = 0
    for s in data.get("sections", []):
        if s.get("kind") != "exercise_set":
            continue
        for ex in s.get("exercises") or []:
            be = (ex.get("body_en") or "").strip()
            bh = (ex.get("body_he") or "").strip()
            se = (ex.get("solution_en") or "").strip()
            sh = (ex.get("solution_he") or "").strip()
            if be and bh == be and not HE.search(bh):
                ex["body_he"] = be  # math-only; mirror is ok if identical latex
            if se and (not sh or sh == se) and HE.search(se):
                ex["solution_he"] = se
                changed += 1
            elif se and not sh:
                ex["solution_he"] = se
                changed += 1
    return changed


def main() -> None:
    mojibake_files = 0
    summary_files = 0
    for fp in sorted(LESSONS_DIR.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8-sig"))
        cid = data.get("concept_id") or fp.stem
        m = walk_strings(data)
        s = add_missing_summaries(data, cid)
        if m or s:
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if m:
                mojibake_files += 1
            if s:
                summary_files += 1
                print(f"  added summary: {fp.name}")

    print(f"Fixed mojibake in {mojibake_files} files")
    print(f"Added summaries to {summary_files} files")


if __name__ == "__main__":
    main()
