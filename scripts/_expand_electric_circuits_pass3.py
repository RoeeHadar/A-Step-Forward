#!/usr/bin/env python3
"""Pass 3: dedupe and fix short Hebrew explanations."""
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "scripts/seed_data/lessons/electric_circuits.json"


def wc(text):
    if not text:
        return 0
    s = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    s = re.sub(r"\$[^$\n]+\$", " MATH ", s)
    s = re.sub(r"[#*_`>\[\]()]", " ", s)
    return len([w for w in s.split() if w])


data = json.loads(OUT.read_text(encoding="utf-8"))

# Dedupe why_matters duplicate paragraphs
for sec in data["sections"]:
    if sec.get("kind") == "why_matters":
        for lang in ("body_en_md", "body_he_md"):
            body = sec[lang]
            marker_en = "**Real-world connection:**"
            marker_he = "**קשר לעולם האמיתי:**"
            marker = marker_en if lang == "body_en_md" else marker_he
            if body.count(marker) > 1:
                idx = body.find(marker)
                idx2 = body.find(marker, idx + 1)
                sec[lang] = body[:idx2].rstrip()

    if sec.get("kind") == "before_exam":
        for lang in ("body_en_md", "body_he_md"):
            body = sec[lang]
            marker_en = "### Common Bagrut question types"
            marker_he = "### סוגי שאלות נפוצים"
            marker = marker_en if lang == "body_en_md" else marker_he
            if body.count(marker) > 1:
                idx = body.find(marker)
                idx2 = body.find(marker, idx + 1)
                sec[lang] = body[:idx2].rstrip()

    if sec.get("kind") == "summary":
        for lang in ("body_en_md", "body_he_md"):
            body = sec[lang]
            marker_en = "**Method summary:**"
            marker_he = "**סיכום שיטה:**"
            marker = marker_en if lang == "body_en_md" else marker_he
            if body.count(marker) > 1:
                idx = body.find(marker)
                idx2 = body.find(marker, idx + 1)
                sec[lang] = body[:idx2].rstrip()

    if sec.get("kind") == "definition":
        for lang in ("body_en_md", "body_he_md"):
            body = sec[lang]
            for marker in ("**Conductors vs. insulators:**", "**מוליכים מול מבודדים:**"):
                if body.count(marker) > 1:
                    idx = body.find(marker)
                    idx2 = body.find(marker, idx + 1)
                    sec[lang] = body[:idx2].rstrip()

    if sec.get("kind") == "worked_example":
        for lang in ("body_en_md", "body_he_md"):
            body = sec[lang]
            marker_en = "**Physical picture:**"
            marker_he = "**תמונה פיזיקלית:**"
            marker = marker_en if lang == "body_en_md" else marker_he
            if body.count(marker) > 1:
                idx = body.find(marker)
                idx2 = body.find(marker, idx + 1)
                sec[lang] = body[:idx2].rstrip()

# Fix Q1 typo
for q in data["questions"]:
    if q["ord"] == 1:
        q["explanation_he"] = q["explanation_he"].replace("יזרום ל מתח", "יזרום למתח")

# Expand short Hebrew explanations
he_extra = {
    2: " יחידות: וואט = אמפר² × אוהם. בדקו: $P=VI=20\\times2=40$ W ✓.",
    3: " בדקו: $V=IR=0.5\\times240=120$ V ✓. אל תחלקו $P/V$ לקבלת $R$.",
    4: " זרם כולל יחלק בין הענפים לפי $I_i=V/R_i$ כשמתח המקור ידוע.",
    7: " זרם בזוג המקביל: $I_{\\parallel}=V/R_{\\parallel}=24/3=8$ A (שני ענפים של 4 A).",
}
for q in data["questions"]:
    if q["ord"] in he_extra and wc(q["explanation_he"]) < 80:
        q["explanation_he"] += he_extra[q["ord"]]

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Pass 3 complete")
for q in data["questions"]:
    en, he = wc(q["explanation_en"]), wc(q["explanation_he"])
    flag = "" if 80 <= en <= 150 and 80 <= he <= 150 else " !"
    print(f"  Q{q['ord']}: EN={en} HE={he}{flag}")
