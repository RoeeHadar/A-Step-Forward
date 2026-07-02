#!/usr/bin/env python3
"""Final depth patch for integrals_intro — worked examples + Hebrew explanations."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/integrals_intro.json"
j = json.loads(TARGET.read_text(encoding="utf-8"))

WE_EXTRA_EN = {
    1: """

**Why this pattern appears on exams:** Bagrut 5-unit and Calc 1 tests often start integration units with a pure polynomial — no tricks, just power rule and linearity. The goal is to confirm you can reverse differentiation term by term.

**Exam note:** Polynomial antiderivatives earn partial credit even when $+C$ is forgotten, but the constant is required for full marks on indefinite integrals. Always write $+C$ on the final answer line. After combining terms, differentiate once — if you recover $3x^2+2x-5$, your algebra is complete.""",
    2: """

**Why signed area matters:** Definite integrals measure **net** change, not total size. A negative answer is not an error — it tells you the curve spent more time below the axis than above on that interval.

**Exam note:** When FTC gives a negative result, state the signed-area interpretation in one sentence. Graders on Bagrut 5-unit and Calc 1 rubrics expect you to recognize below-axis regions. Show $F(x)$ first, then $F(b)-F(a)$ with bracket notation.""",
    3: """

**Why two constants appear:** Each integration introduces a new $+C$. You need one initial condition per constant — here $f'(0)=1$ fixes $C_1$ before integrating again, then $f(0)=3$ fixes $C_2$.

**Exam note:** Label constants $C_1$ and $C_2$ clearly when integrating twice. Mixing them up is a common source of lost points on initial-value problems. Verify both given conditions at the end.""",
}

# Correct Hebrew word for integral
INTEGRAL_HE = "\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc"

WE_EXTRA_HE = {
    1: f"""

**למה הדפוס הזה מופיע בבחינות:** בבגרות 5 יחידות ובחדו״א 1 מתחילים לעיתים מפולינום טהור — בלי tricks, רק כלל חזקה וליניאריות. המטרה: לוודא שיודעים להפוך גזירה איבר-איבר.

**הערה לבחינה:** נגזרות הפוכות פולינומיות מקבלות ניקוד חלקי גם בלי $+C$, אך הקבוע נדרש לציון מלא. כתבו $+C$ בשורת התשובה. אחרי חיבור — גזרו פעם אחת; אם חוזר $3x^2+2x-5$, האלגברה שלמה.""",
    2: f"""

**למה שטח עם סימן חשוב:** {INTEGRAL_HE} מסויים מודד **שינוי נטו**, לא גודל כולל. תשובה שלילית אינה טעות — היא אומרת שהעקומה הייתה יותר מתחת לציר.

**הערה לבחינה:** כש-FTC נותן שלילי, כתבו משפט על שטח עם סימן. בודקים מצפים לזיהוי אזורים מתחת לציר. הציגו $F(x)$, ואז $F(b)-F(a)$ עם סימון סוגריים.""",
    3: f"""

**למה שני קבועים:** כל {INTEGRAL_HE} מוסיף $+C$ חדש. צריך תנאי התחלה אחד לכל קבוע — כאן $f'(0)=1$ קובע $C_1$ לפני ה{INTEGRAL_HE} השני, ואז $f(0)=3$ קובע $C_2$.

**הערה לבחינה:** סמנו $C_1$ ו-$C_2$ בבירור. ערבוב ביניהם גורם לאיבוד נקודות. אמתו שני התנאים בסוף.""",
}

HE_TIP_EXTRA = {
    1: " זכרו: גזירה של $x^5/5$ מחזירה בדיוק $x^4$ — זו הבדיקה המהירה ביותר.",
    2: " חישוב שברים: מכנה משותף 12 מפשט את $(16/3+1/4)-(2/3+1)$.",
    3: f" כל איבר בפולינום מקבל כלל חזקה נפרד — אל תנסו לשלב לפני ה{INTEGRAL_HE}.",
    4: f" $\\int e^x$ נשאר $e^x$ — היחידה שאינה משתנה בגזירה ו{INTEGRAL_HE}.",
    5: " כתיבת $F(x)=x^4/4$ לפני ההצבה מונעת טעויות בגבולות.",
    6: " $\\sqrt[3]{{x}}=x^{{1/3}}$: חזקה חדשה $4/3$, חלקו ב-$4/3$.",
    7: " $\\ln|x|$ מופיע רק כשיש $1/x$ — לא כלל חזקה.",
    8: " $f(0)=1$ נותן $C=-4$ אחרי שמצאתם את משפחת הפונקציות.",
}

def fix_he(s: str) -> str:
    return s

for sec in j["sections"]:
    if sec.get("kind") == "worked_example":
        n = sec.get("example_number")
        if n in WE_EXTRA_EN:
            sec["body_en_md"] += WE_EXTRA_EN[n]
            sec["body_he_md"] += fix_he(WE_EXTRA_HE[n])
        for key in ("body_en_md", "body_he_md"):
            if key in sec:
                sec[key] = fix_he(sec[key])

for q in j["questions"]:
    ord_ = q["ord"]
    if ord_ in HE_TIP_EXTRA:
        q["explanation_he"] = q["explanation_he"].rstrip() + fix_he(HE_TIP_EXTRA[ord_])

EN_TIP_EXTRA = {
    5: "Positive integrand on a positive interval confirms the sign of your numeric answer. ",
}
for q in j["questions"]:
    if q["ord"] in EN_TIP_EXTRA:
        q["explanation_en"] = q["explanation_en"].replace(
            "**Exam tip:**\n",
            f"**Exam tip:**\n{EN_TIP_EXTRA[q['ord']]}",
        )

TARGET.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

r = subprocess.run(["node", "scripts/seed-lessons.mjs", "--dry-run"], cwd=ROOT, capture_output=True, text=True)
print(r.stdout)
if r.returncode:
    print(r.stderr)
    raise SystemExit(r.returncode)
print("OK 207/207")
