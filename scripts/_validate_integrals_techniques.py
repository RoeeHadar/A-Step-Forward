#!/usr/bin/env python3
import json, re
from pathlib import Path

p = Path("scripts/seed_data/lessons/integrals_techniques.json")
d = json.loads(p.read_text("utf-8"))

def wc(t):
    s = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", t or "")
    s = re.sub(r"\$[^$\n]+\$", " MATH ", s)
    s = re.sub(r"[#*_`>\[\]()]", " ", s)
    return len([w for w in s.split() if w])

MIN = {
    "intro": (110, 90), "definition": (130, 110), "theory": (160, 130),
    "pitfall": (100, 85), "why_matters": (90, 75), "method_guide": (100, 85),
    "before_exam": (90, 75), "summary": (70, 60),
}
issues = []
for sec in d["sections"]:
    k = sec.get("kind")
    if k in MIN:
        en, he = wc(sec.get("body_en_md")), wc(sec.get("body_he_md"))
        if en < MIN[k][0]: issues.append(f"{k} EN {en}")
        if he < MIN[k][1]: issues.append(f"{k} HE {he}")
    elif k == "worked_example":
        en, he = wc(sec.get("body_en_md")), wc(sec.get("body_he_md"))
        if en < 130: issues.append(f"we{sec.get('example_number')} EN {en}")
        if he < 110: issues.append(f"we{sec.get('example_number')} HE {he}")

for q in d["questions"]:
    for lang in ("en", "he"):
        w = wc(q.get(f"explanation_{lang}"))
        if w < 80 or w > 150:
            issues.append(f"Q{q['ord']} {lang} {w}")

text = p.read_text("utf-8")
corrupt = [
    "אינטegral", "אינtegrand", "פnימית", "אספu", "תכננu", "גzור",
    "הכpלה", "פיתagoras", "ערbבu", "חצi", "Identify the rule from this lesson",
]
for c in corrupt:
    if c in text:
        issues.append(f"corrupt: {c}")

print("Issues:", len(issues))
for i in issues:
    print(" ", i)
if not issues:
    print("ALL GATES PASS")
