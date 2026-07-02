#!/usr/bin/env python3
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

for sec in data["sections"]:
    he = sec.get("body_he_md", "")
    he = he.replace("בתנאי טמפרatura קבועה", "שהתנגדותו קבועה")
    he = he.replace("אסטרategיה", "אסטרategיה")
    sec["body_he_md"] = he

for sec in data["sections"]:
    kind = sec.get("kind")
    if kind == "definition":
        sec["body_en_md"] += (
            "\n\n**Conductors vs. insulators:** Metals obey Ohm's law well at room "
            "temperature; resistance increases with temperature for most conductors. "
            "In Bagrut problems, assume ohmic behavior unless stated otherwise.\n\n"
            "**Choosing the right power formula:** Use $P = I^2R$ when you know the "
            "current through a specific resistor; $P = V^2/R$ when you know the voltage "
            "across it; $P = IV$ only when both $I$ and $V$ refer to the same element."
        )
        sec["body_he_md"] += (
            "\n\n**מוליכים מול מבודדים:** מתכות מצייתות היטב לחוק אוהם "
            "כשהטemperatura יציבה; ההתנגדות עולה עם עלייה בטemperatura. "
            "בבגרות, הניחו התנהגות אומית אלא אם נאמר אחרת.\n\n"
            "**בחירת נוסחת הספק:** $P = I^2R$ כשיודעים זרם בנגד ספציפי; "
            "$P = V^2/R$ כשיודעים מתח עליו; $P = IV$ רק כששניהם שייכים לאותו רכיב."
        )
    elif kind == "worked_example":
        sec["body_en_md"] += (
            "\n\n**Physical picture:** Trace the current path from the battery's positive "
            "terminal, through each resistor, and back to the negative terminal. "
            "Each step uses either series rules (same $I$) or parallel rules (same $V$)."
        )
        sec["body_he_md"] += (
            "\n\n**תמונה פיזיקלית:** עקבו אחר מסלול הזרם מקוטב חיובי הסוללה, "
            "דרך כל נגד, ובחזרה לקוטב השלילי. כל שלב משתמש בכללי טור (אותו $I$) "
            "או מקביל (אותו $V$)."
        )
    elif kind == "why_matters":
        sec["body_en_md"] += (
            "\n\n**Real-world connection:** Every electronic device — from LED bulbs "
            "to electric cars — relies on the circuit principles in this lesson. "
            "Mastering $V=IR$ and power formulas is the foundation for "
            "`concept:kirchhoff_laws` and eventually AC circuit analysis."
        )
        sec["body_he_md"] += (
            "\n\n**קשר לעולם האמיתי:** כל מכשיר אלקטרוני — מנורות LED "
            "ועד רכבים חשמליים — מסתמך על עקרונות המעגל בשיעור זה. "
            "שליטה ב-$V=IR$ ובנוסחאות הספק היא הבסיס ל-`concept:kirchhoff_laws` "
            "ולניתוח מעגלי זרם חילופין."
        )
    elif kind == "before_exam":
        sec["body_en_md"] += (
            "\n\n### Common Bagrut question types\n"
            "- Single-loop Ohm's law (find $I$, $R$, or $V$)\n"
            "- Series/parallel simplification with backward substitution\n"
            "- Internal resistance and terminal voltage\n"
            "- Wheatstone bridge balance condition\n"
            "- Power dissipation in one or all resistors\n\n"
            "**Time management:** Spend 2 minutes drawing and labeling before "
            "writing any equation. Setup errors cost more points than arithmetic slips."
        )
        sec["body_he_md"] += (
            "\n\n### סוגי שאלות נפוצים בבגרות\n"
            "- לולאה בודדת — חוק אוהם (מציאת $I$, $R$, או $V$)\n"
            "- פישוט טור/מקביל עם הצבה אחורה\n"
            "- התנגדות פנימית ומתח מסוף\n"
            "- תנאי איזון גשר ווטסטון\n"
            "- הספק בנגד אחד או בכולם\n\n"
            "**ניהול זמן:** הקדישו 2 דקות לשרטוט ותיוג לפני כתיבת משוואה. "
            "שגיאות הכנה עולות יותר נקודות מטעויות חשבון."
        )
    elif kind == "summary":
        sec["body_en_md"] += (
            "\n\n**Method summary:** For any circuit, ask: Can I simplify to "
            "series/parallel? If yes, find $R_{\\text{eq}}$ and work backward. "
            "If no, use Kirchhoff's laws. Always verify with KVL and power balance."
        )
        sec["body_he_md"] += (
            "\n\n**סיכום שיטה:** לכל מעגל, שאלו: האם ניתן לפשט לטור/מקביל? "
            "אם כן — מצאו $R_{\\text{שקול}}$ וחזרו אחורה. אם לא — חוקי קירכהוף. "
            "תמיד אמתו עם KVL ואיזון הספק."
        )

# Fix Hebrew typos with correct words
for sec in data["sections"]:
    he = sec.get("body_he_md", "")
    he = he.replace("אסטרategיה", "אסטרategיה")
    he = re.sub(
        r"כשהט[^\s]+ יציבה; ההתנגדות עולה עם עלייה בט[^\s]+\.",
        "כשהטemperatura יציבה; ההתנגדות עולה עם עלייה בטemperatura.",
        he,
    )
    he = he.replace(
        "כשהטemperatura יציבה; ההתנגדות עולה עם עלייה בטemperatura.",
        "כשהטemperatura יציבה; ההתנגדות עולה עם עלייה בטemperatura.",
    )
    sec["body_he_md"] = he

# Use proper Hebrew for temperature and strategy
for sec in data["sections"]:
    he = sec.get("body_he_md", "")
    he = he.replace("אסטרategיה", "אסטרategיה")
    he = he.replace(
        "כשהטemperatura יציבה; ההתנגדות עולה עם עלייה בטemperatura.",
        "כשהטemperatura יציבה; ההתנגדות עולה עם עלייה בטemperatura.",
    )
    sec["body_he_md"] = he

extras = {
    4: (
        "\n\n**Self-check:** The equivalent $1\\,\\Omega$ is less than the "
        "smallest resistor ($2\\,\\Omega$) — always true for parallel combinations.",
        "\n\n**בדיקה עצמית:** השקול $1\\,\\Omega$ קטן מהנגד הקטן ביותר "
        "($2\\,\\Omega$) — תמיד נכון במקביל.",
    ),
    5: (
        "\n\n**Verify:** The series pair and parallel branch both connect across "
        "the full 18 V source — parallel branches always share source voltage.",
        "\n\n**אימות:** זוג הטור והענף המקביל מחוברים שניהם ל-18 V — "
        "ענפים מקבילים תמיד חולקים מתח מקור.",
    ),
    6: (
        "\n\n**Physical meaning:** The 2 V drop ($12-10$) occurs across internal "
        "resistance: $Ir = 2 \\times 1 = 2$ V. The battery loses this voltage internally.",
        "\n\n**משמעות פיזיקלית:** ירידת 2 V ($12-10$) על ההתנגדות הפנימית: "
        "$Ir = 2$ V. הסוללה מאבדת מתח זה בפנים.",
    ),
}
for q in data["questions"]:
    if q["ord"] in extras:
        en, he = extras[q["ord"]]
        q["explanation_en"] += en
        q["explanation_he"] += he

# Final clean Hebrew
STRATEGY = "\u05d0\u05e1\u05d8\u05e8\u05d8\u05d2\u05d9\u05d4"  # אסטרategיה
TEMP = "\u05d8\u05de\u05e4\u05e8\u05d8\u05d5\u05e8\u05d4"  # טemperatura
for sec in data["sections"]:
    he = sec.get("body_he_md", "")
    he = he.replace("אסטרategיה", STRATEGY)
    he = he.replace("כשהטemperatura יציבה", f"כש{TEMP} יציבה")
    he = he.replace("עלייה בטemperatura", f"עלייה ב{TEMP}")
    sec["body_he_md"] = he

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Pass 2 complete")
for sec in data["sections"]:
    k = sec.get("kind")
    if k in ("definition", "worked_example", "why_matters", "before_exam", "summary"):
        print(f"  {k}: EN={wc(sec.get('body_en_md',''))} HE={wc(sec.get('body_he_md',''))}")
for q in data["questions"]:
    print(f"  Q{q['ord']}: EN={wc(q['explanation_en'])} HE={wc(q['explanation_he'])}")
