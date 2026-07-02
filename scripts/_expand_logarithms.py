#!/usr/bin/env python3
"""Expand logarithms.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/logarithms.json"

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

EXPAND_KINDS = {
    "intro",
    "definition",
    "theory",
    "worked_example",
    "pitfall",
    "why_matters",
    "method_guide",
    "before_exam",
    "summary",
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


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he) -> tuple[str, str]:
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


SECTIONS = {
    "intro": {
        "body_en_md": """A **logarithm** answers the question: "To what power must I raise the base to get this number?" It is the **inverse of an exponential** — if $b^c = a$, then $\\log_b a = c$. That single equivalence drives every evaluation, simplification, and equation in this lesson.

**Where logarithms appear beyond the classroom:**
- **Chemistry:** pH $= -\\log_{10}[\\text{H}^+]$ compresses huge concentration ranges into manageable numbers.
- **Earth science:** the Richter scale uses $\\log_{10}$ of seismic amplitude — each whole-number step is ten times stronger shaking.
- **Acoustics:** decibels are logarithmic ratios of sound intensity; doubling loudness is not a linear jump on the scale.
- **Physics:** radioactive decay and half-life models use $\\ln$ inside exponential decay laws.

In Israeli Bagrut (4–5 units), logarithms appear in function analysis, equation solving, and compound-growth word problems linked to `concept:functions_exponential`. Exam items reward knowing log laws, checking domain before solving, and using change of base when bases differ.""",
        "body_he_md": """**לוגריתם** עונה על השאלה: "באיזו חזקה צריך להרים את הבסיס כדי לקבל את המספר?" הוא **ההפכי של פונקציה מעריכית** — אם $b^c = a$, אז $\\log_b a = c$. ההומכה הזו מניעה כל חישוב, פישוט ומשוואה בשיעור.

**איפה לוגריתמים מופיעים מחוץ לכיתה:**
- **כימיה:** pH $= -\\log_{10}[\\text{H}^+]$ דוחס טווחי ריכוז עצומים למספרים נוחים.
- **מדעי כדור הארץ:** סקלת ריכטר משתמשת ב-$\\log_{10}$ של עוצמת רעידות — כל שלם נוסף מייצג רעידה פי עשרה חזקה יותר.
- **אקוסטיקה:** דציבלים הם יחסים לוגריתמיים של עוצמת קול; הכפלת עוצמה לא מתורגמת לינארית על המדד.
- **פיזיקה:** דעיכה מעריכית וזמן מחצית חיים משתמשים ב-$\\ln$ בתוך חוקי דעיכה.

בבגרות (4–5 יחידות), לוגריתמים מופיעים בניתוח פונקציות, פתרון משוואות ובעיות צמיחה מחוברות ל-`concept:functions_exponential`. בבחינה מעריכים שליטה בחוקי לוג, בדיקת תחום לפני פתרון, והחלפת בסיס כשהבסיסים שונים.""",
    },
    "definition": {
        "body_en_md": """The logarithm is defined by the equivalence between exponentiation and "undoing" it:

$$\\boxed{\\log_b a = c \\quad\\Longleftrightarrow\\quad b^c = a}$$

Read left to right: "$\\log_b a$ is the exponent you raise $b$ to in order to get $a$." Read right to left: "If $b^c = a$, then the log base $b$ of $a$ equals $c$." This two-way reading is what makes evaluation and equation solving feel like the same skill.

**Conditions (always check):** $b > 0$, $b \\neq 1$, and $a > 0$. The argument $a$ must be positive because no real power of a positive base $b$ produces a negative or zero result.

**Special values (memorize):**
- $\\log_b 1 = 0$ because $b^0 = 1$ for any valid base.
- $\\log_b b = 1$ because $b^1 = b$.
- **Inverse pair:** $b^{\\log_b x} = x$ and $\\log_b(b^x) = x$ for $x > 0$.

**Common bases on exams:**
- $\\log = \\log_{10}$ (common logarithm; calculator LOG key).
- $\\ln = \\log_e$ where $e \\approx 2.71828$ (natural logarithm; calculator LN key).

**Key idea:** Evaluation means rewriting as an exponential question: $\\log_2 8 = ?$ becomes "$2^? = 8$" → answer $3$.""",
        "body_he_md": """הלוגריתם מוגדר בהומכה בין העלאה בחזקה ל"ביטול" שלה:

$$\\boxed{\\log_b a = c \\quad\\Longleftrightarrow\\quad b^c = a}$$

משמאל לימין: "$\\log_b a$ הוא המעריך שמעלים בו את $b$ כדי לקבל $a$." מימין לשמאל: "אם $b^c = a$, אז הלוגריתם בבסיס $b$ של $a$ שווה $c$." קריאה דו-כיוונית זו היא מה שגורם לחישוב ופתרון משוואות להרגיש כמו אותה מיומנות.

**תנאים (תמיד לבדוק):** $b > 0$, $b \\neq 1$, ו-$a > 0$. הארגומנט $a$ חייב להיות חיובי — אין חזקה ממשית של בסיס חיובי $b$ שנותנת אפס או שלילי.

**ערכים מיוחדים (לשינון):**
- $\\log_b 1 = 0$ כי $b^0 = 1$ לכל בסיס תקף.
- $\\log_b b = 1$ כי $b^1 = b$.
- **זוג הפכיים:** $b^{\\log_b x} = x$ ו-$\\log_b(b^x) = x$ עבור $x > 0$.

**בסיסים נפוצים בבחינה:**
- $\\log = \\log_{10}$ (לוגריתם עשרוני; מקש LOG במחשבון).
- $\\ln = \\log_e$ כאשר $e \\approx 2.71828$ (לוגריתם טבעי; מקש LN).

**רעיון מפתח:** חישוב = שאלה מעריכית: $\\log_2 8 = ?$ הופך ל-"$2^? = 8$" → תשובה $3$.""",
    },
    "theory": {
        "body_en_md": """The three log laws mirror exponent laws. Each requires **positive arguments** ($x, y > 0$).

| Law | Formula | Derived from |
|---|---|---|
| **Product** | $\\log_b(xy) = \\log_b x + \\log_b y$ | $b^{m+n} = b^m \\cdot b^n$ |
| **Quotient** | $\\log_b(x/y) = \\log_b x - \\log_b y$ | $b^{m-n} = b^m/b^n$ |
| **Power** | $\\log_b(x^k) = k\\log_b x$ | $(b^m)^k = b^{mk}$ |

**Change of base** lets you evaluate or simplify logs when the base is awkward:
$$\\log_b a = \\frac{\\ln a}{\\ln b} = \\frac{\\log a}{\\log b}$$
The argument goes in the **numerator**, the base in the **denominator** — reversing this is a top exam error.

**Critical warning:** $\\log_b(x+y) \\neq \\log_b x + \\log_b y$. Only **products** inside the log split into a **sum** of logs; sums stay inside.

**The log function $f(x) = \\log_b x$:**
- Domain: $x > 0$; Range: all real numbers $\\mathbb{R}$.
- x-intercept: $(1, 0)$ because $\\log_b 1 = 0$.
- Vertical asymptote: $x = 0$ (the y-axis).
- Monotonicity: increasing when $b > 1$; decreasing when $0 < b < 1$.

**Strategy:** Before applying laws, confirm every log argument is positive. When simplifying, combine logs with the **same base** only. For equations with different bases, take $\\ln$ of both sides or convert with change of base.""",
        "body_he_md": """שלושת חוקי הלוגריתם משקפים את חוקי החזקות. כל אחד דורש **ארגומנטים חיוביים** ($x, y > 0$).

| חוק | נוסחה | נגזר מ- |
|---|---|---|
| **כפל** | $\\log_b(xy) = \\log_b x + \\log_b y$ | $b^{m+n} = b^m \\cdot b^n$ |
| **חילוק** | $\\log_b(x/y) = \\log_b x - \\log_b y$ | $b^{m-n} = b^m/b^n$ |
| **חזקה** | $\\log_b(x^k) = k\\log_b x$ | $(b^m)^k = b^{mk}$ |

**החלפת בסיס** מאפשרת חישוב כשהבסיס לא נוח:
$$\\log_b a = \\frac{\\ln a}{\\ln b} = \\frac{\\log a}{\\log b}$$
הארגומנט ב**מונה**, הבסיס ב**מכנה** — היפוך זה טעות שכיחה בבחינה.

**אזהרה קריטית:** $\\log_b(x+y) \\neq \\log_b x + \\log_b y$. רק **מכפלה** בתוך הלוג מתפצלת ל**סכום**; סכום נשאר בפנים.

**פונקציה לוגריתמית $f(x) = \\log_b x$:**
- תחום: $x > 0$; טווח: כל הממשיים $\\mathbb{R}$.
- חיתוך $x$: $(1, 0)$ כי $\\log_b 1 = 0$.
- אסymptote אנכי: $x = 0$.
- מונוטוניות: עולה כש-$b > 1$; יורדת כש-$0 < b < 1$.

**אסטרטגיה:** לפני יישום חוקים — ודאו שכל ארגומנט לוג חיובי. בפישוט, מאחדים לוגים עם **אותו בסיס** בלבד. במשוואות עם בסיסים שונים — $\\ln$ משני האגפים או החלפת בסיס.""",
    },
    "worked_example_1": {
        "body_en_md": """**Part A — Evaluate:** $\\log_2 8 + \\log_3(1/9)$.

This combines direct evaluation with the power law inside a log. No calculator needed if you recognize perfect powers.

### Move 1: Evaluate $\\log_2 8$
Ask "$2^? = 8$". Since $2^3 = 8$, we get $\\log_2 8 = 3$.

### Move 2: Evaluate $\\log_3(1/9)$
Rewrite $1/9 = 3^{-2}$, so $\\log_3(1/9) = \\log_3 3^{-2} = -2$ by the power law.

### Move 3: Add the results
$3 + (-2) = 1$.

**Part B — Simplify:** $\\log_5 10 + \\log_5 2.5$.

### Move 4: Apply the product law (same base)
$\\log_5 10 + \\log_5 2.5 = \\log_5(10 \\times 2.5) = \\log_5 25$.

### Move 5: Evaluate $\\log_5 25$
$5^2 = 25$, so the sum equals $2$.

**Why this structure matters:** Part A mixes evaluation with the power law on a fraction; Part B shows that sums of logs with the **same base** collapse to a single log before evaluation. Both skills appear on Bagrut items.

**Answer:** Part A $= 1$; Part B $= 2$.""",
        "body_he_md": """**חלק א — חישוב:** $\\log_2 8 + \\log_3(1/9)$.

שילוב של חישוב ישיר עם חוק החזקה בתוך לוג. לא נדרש מחשבון אם מזהים חזקות שלמות.

### צעד 1: חישוב $\\log_2 8$
שואלים "$2^? = 8$". מכיוון ש-$2^3 = 8$, מתקבל $\\log_2 8 = 3$.

### צעד 2: חישוב $\\log_3(1/9)$
כותבים $1/9 = 3^{-2}$, ולכן $\\log_3(1/9) = \\log_3 3^{-2} = -2$ לפי חוק החזקה.

### צעד 3: חיבור התוצאות
$3 + (-2) = 1$.

**חלק ב — פישוט:** $\\log_5 10 + \\log_5 2.5$.

### צעד 4: יישום חוק הכפל (אותו בסיס)
$\\log_5 10 + \\log_5 2.5 = \\log_5(10 \\times 2.5) = \\log_5 25$.

### צעד 5: חישוב $\\log_5 25$
$5^2 = 25$, ולכן הסכום שווה $2$.

**למה המבנה חשוב:** חלק א משלב חישוב עם חוק חזקה על שבר; חלק ב מראה שסכומי לוגים עם **אותו בסיס** מתכווצים ללוג אחד לפני חישוב. שני הכישורים מופיעים בבגרות.

**תשובה:** חלק א $= 1$; חלק ב $= 2$.""",
    },
    "worked_example_2": {
        "body_en_md": """**Solve:** $\\log_2 x + \\log_2(x-2) = 3$.

Log equations always start with **domain** — arguments must be positive before any algebra. This example is a classic Bagrut pattern: two logs with the same base sum to a constant, producing a quadratic after conversion.

### Move 1: Domain restrictions
$x > 0$ and $x - 2 > 0$, so combined domain is $x > 2$.

### Move 2: Combine logs (product law, same base)
$\\log_2 x + \\log_2(x-2) = \\log_2[x(x-2)] = 3$.

### Move 3: Convert to exponential form
$x(x-2) = 2^3 = 8$.

### Move 4: Expand and solve the quadratic
$x^2 - 2x - 8 = 0 \\Rightarrow (x-4)(x+2) = 0$, so $x = 4$ or $x = -2$.

### Move 5: Filter against domain
$x = -2 < 2$ is **rejected** (would make $\\log_2 x$ undefined). $x = 4 > 2$ ✓.

**Why domain comes first:** Without $x > 2$, combining logs is invalid algebra. Even if algebra produces $x = -2$, it must be discarded because the original logs do not exist there.

**Answer:** $x = 4$. Always re-check: $\\log_2 4 + \\log_2 2 = 2 + 1 = 3$ ✓.""",
        "body_he_md": """**פתרון:** $\\log_2 x + \\log_2(x-2) = 3$.

משוואות לוג מתחילות ב**תחום** — הארגומנטים חייבים להיות חיוביים לפני כל שלב אלגברי. זו דוגמה קלאסית בבגרות: שני לוגים באותו בסיס שסכומם קבוע, ומשוואה ריבועית אחרי המרה.

### צעד 1: הגבלות תחום
$x > 0$ וגם $x - 2 > 0$, לכן התחום המשולב: $x > 2$.

### צעד 2: איחוד לוגים (חוק כפל, אותו בסיס)
$\\log_2 x + \\log_2(x-2) = \\log_2[x(x-2)] = 3$.

### צעד 3: מעבר לצורה מעריכית
$x(x-2) = 2^3 = 8$.

### צעד 4: פתיחה ופתרון משוואה ריבועית
$x^2 - 2x - 8 = 0 \\Rightarrow (x-4)(x+2) = 0$, כלומר $x = 4$ או $x = -2$.

### צעד 5: סינון לפי תחום
$x = -2 < 2$ **נפסל** (הופך את $\\log_2 x$ ללא מוגדר). $x = 4 > 2$ ✓.

**למה תחום קודם:** בלי $x > 2$, איחוד לוגים הוא אלגברה לא חוקית. גם אם האלגברה מייצרת $x = -2$, חייבים לפסול — הלוגים המקוריים לא קיימים שם.

**תשובה:** $x = 4$. בדיקה: $\\log_2 4 + \\log_2 2 = 2 + 1 = 3$ ✓.""",
    },
    "worked_example_3": {
        "body_en_md": """**Solve:** $2^{x+1} = 5^x$.

When bases differ and cannot be matched, take a logarithm of both sides — usually $\\ln$. This type links directly to `concept:functions_exponential` and appears when growth rates with different bases must be compared.

### Move 1: Take $\\ln$ of both sides
$\\ln(2^{x+1}) = \\ln(5^x)$.

### Move 2: Apply the power law on each side
$(x+1)\\ln 2 = x\\ln 5$.

### Move 3: Expand and collect $x$ terms
$x\\ln 2 + \\ln 2 = x\\ln 5$.

### Move 4: Isolate $x$
$\\ln 2 = x(\\ln 5 - \\ln 2) = x\\ln\\frac{5}{2}$. Factor $x$ on the right; the left side is the constant $\\ln 2$ from the exponential setup.

### Move 5: Solve and approximate
$$x = \\frac{\\ln 2}{\\ln(5/2)} \\approx \\frac{0.693}{0.916} \\approx 0.756.$$

**Strategy note:** When $a^{f(x)} = b^{g(x)}$ and bases cannot be unified, $\\ln$ both sides is the standard Bagrut approach. Collect all $x$ terms on one side before dividing by the coefficient.

**Answer:** $x \\approx 0.756$. **Verify:** $2^{1.756} \\approx 3.38$ and $5^{0.756} \\approx 3.38$ ✓.""",
        "body_he_md": """**פתרון:** $2^{x+1} = 5^x$.

כשהבסיסים שונים ולא ניתן לאחד, לוקחים לוגריתם משני האגפים — בדרך כלל $\\ln$. סוג זה קשור ל-`concept:functions_exponential` ומופיע כשמשווים קצבי צמיחה עם בסיסים שונים.

### צעד 1: $\\ln$ משני האגפים
$\\ln(2^{x+1}) = \\ln(5^x)$.

### צעד 2: יישום חוק החזקה בכל צד
$(x+1)\\ln 2 = x\\ln 5$.

### צעד 3: פתיחה ואיסוף איברי $x$
$x\\ln 2 + \\ln 2 = x\\ln 5$.

### צעד 4: בידוד $x$
$\\ln 2 = x(\\ln 5 - \\ln 2) = x\\ln\\frac{5}{2}$. מוציאים גורם $x$ מימין; בצד שמאל קבוע $\\ln 2$ מההכנה המעריכית.

### צעד 5: פתרון וקירוב
$$x = \\frac{\\ln 2}{\\ln(5/2)} \\approx \\frac{0.693}{0.916} \\approx 0.756.$$

**הערת אסטרטגיה:** כש-$a^{f(x)} = b^{g(x)}$ והבסיסים לא ניתנים לאיחוד, $\\ln$ משני האגפים הוא הגישה הסטנדרטית בבגרות. אספו את כל איברי $x$ לצד אחד לפני חילוק במקדם.

**תשובה:** $x \\approx 0.756$. **בדיקה:** $2^{1.756} \\approx 3.38$ ו-$5^{0.756} \\approx 3.38$ ✓ — שני האגפים תואמים.""",
    },
    "method_guide": {
        "body_en_md": """| Type | Method |
|---|---|
| Evaluate $\\log_b a$ | Ask: $b^? = a$; convert to exponential form |
| Simplify log expression | Apply product / quotient / power laws (same base) |
| Solve $\\log_b(\\text{expr}) = c$ | **Domain first!** Then rewrite as $\\text{expr} = b^c$ |
| Solve exponential $a^{f(x)} = b^{g(x)}$ | Take $\\ln$ both sides; use power law; isolate $x$ |
| Different bases in one expression | Change-of-base: $\\log_b a = \\ln a / \\ln b$ |
| Domain of $\\log$ function | Argument $> 0$ only; write inequality before graphing |

**When to use:** Read the problem type first — evaluation, simplification, log equation, or exponential equation — then pick the matching row. Only substitute numbers after the structural step is chosen.

**Exam tip:** Write "domain:" as your first line on every log equation. Graders and you both catch invalid roots early.""",
        "body_he_md": """| סוג | שיטה |
|---|---|
| חישוב $\\log_b a$ | שואלים: $b^? = a$; מעבר לצורה מעריכית |
| פישוט ביטוי לוג | חוקי כפל / חילוק / חזקה (אותו בסיס) |
| $\\log_b(\\text{ביטוי}) = c$ | **תחום קודם!** ואז $\\text{ביטוי} = b^c$ |
| משוואה מעריכית $a^{f(x)} = b^{g(x)}$ | $\\ln$ משני האגפים; חוק חזקה; בידוד $x$ |
| בסיסים שונים בביטוי אחד | החלפת בסיס: $\\log_b a = \\ln a / \\ln b$ |
| תחום של פונקציית $\\log$ | ארגומנט $> 0$ בלבד; כתבו אי-שוויון לפני גרף |

**מתי להשתמש:** קראו קודם את סוג הבעיה — חישוב, פישוט, משוואה לוגריתמית או מעריכית — ובחרו את השורה המתאימה. רק אחרי בחירת המבנה מציבים מספרים.

**טיפ לבחינה:** כתבו "תחום:" כשורה ראשונה בכל משוואת לוג. כך תופסים שורשים לא תקפים מוקדם — גם אתם וגם הבודק.""",
    },
    "pitfall": {
        "body_en_md": """1. **Log of a sum ≠ sum of logs.** $\\log(x+y) \\neq \\log x + \\log y$ — this is false! Only the **product** of arguments splits: $\\log(xy) = \\log x + \\log y$.

2. **Skipping domain check.** Always verify that every log argument is positive **before** solving and **after** finding candidates. Extraneous roots from quadratics are common.

3. **Forgetting $\\log_b b = 1$.** Students sometimes write $\\log_5 5 = 5$. The log asks "to what power?" — the answer is $1$, not the base itself.

4. **Wrong change-of-base direction.** $\\log_b a = \\ln a / \\ln b$, **not** $\\ln b / \\ln a$. Argument on top, base on bottom.

5. **Applying power law incorrectly on negatives.** $\\log(x^2)$ over all reals requires $2\\log|x|$ for domain reasons; in Bagrut with $x > 0$ given, $2\\log x$ is fine.

6. **Distributing log over addition in equations.** $\\log(a) + \\log(b) = \\log(ab)$ only when both logs share the same base and both arguments are positive.""",
        "body_he_md": """1. **לוג של סכום ≠ סכום לוגים.** $\\log(x+y) \\neq \\log x + \\log y$ — זה שגוי! רק **מכפלה** של ארגומנטים מתפצלת: $\\log(xy) = \\log x + \\log y$.

2. **דילוג על בדיקת תחום.** ודאו שכל ארגומנט לוג חיובי **לפני** הפתרון ו**אחרי** מציאת מועמדים. שורשים זרים ממשוואות ריבועיות שכיחים.

3. **שכחת $\\log_b b = 1$.** לפעמים כותבים $\\log_5 5 = 5$. הלוג שואל "באיזו חזקה?" — התשובה $1$, לא הבסיס עצמו.

4. **כיוון שגוי בהחלפת בסיס.** $\\log_b a = \\ln a / \\ln b$, **לא** $\\ln b / \\ln a$. ארגומנט במונה, בסיס במכנה.

5. **יישום שגוי של חוק חזקה על שליליים.** $\\log(x^2)$ על כל הממשיים דורש $2\\log|x|$ מסיבות תחום; בבגרות עם $x > 0$ נתון, $2\\log x$ תקין.

6. **פיזור לוג על חיבור במשוואות.** $\\log(a) + \\log(b) = \\log(ab)$ רק כששני הלוגים באותו בסיס ושני הארגומנטים חיוביים.""",
    },
    "why_matters": {
        "body_en_md": """Logarithms compress enormous ranges — from atomic concentrations to earthquake energy — into numbers humans can compare. That same compression appears in finance (compound interest solved with logs), biology (population doubling times), and the link to `concept:modern_physics_intro` where exponential decay and the photoelectric effect rely on log-linear graphs.

**You will use this to unlock:**
- `concept:modern_physics_intro` **Quantum Physics Basics (Photoelectric Effect)** (tooling_for)

**Why it matters for exams:** Bagrut and university courses reward *transfer* — applying log laws in a new context (word problem, graph, mixed-base equation). When you study, always ask: "Which law matches the structure?" not "Which numbers do I plug in?" """,
        "body_he_md": """לוגריתמים דוחסים טווחים עצומים — מריכוז אטומי לאנרגיית רעידות — למספרים שניתן להשוות. אותה דחיסה מופיעה בפיננסים (ריבית דריבית עם לוגים), בביולוגיה (זמן כפילות של אוכלוסייה), ובקשר ל-`concept:modern_physics_intro` שבו דעיכה מעריכית ואפקט פוטואלקטרי משתמשים בגרפים לוג-לינאריים.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:modern_physics_intro` **מבוא לפיזיקה קוונטית (אפקט פוטואלקטרי)** (tooling_for)

**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים *העברה* — יישום חוקי לוג בהקשר חדש (בעיה מילולית, גרף, משוואה עם בסיסים מעורבים). בזמן לימוד, שאלו: "איזה חוק מתאים למבנה?" ולא "אילו מספרים להציב?" """,
    },
    "before_exam": {
        "body_en_md": """**Formula card:**
- $\\log_b a = c \\Leftrightarrow b^c = a$
- $\\log_b(xy) = \\log_b x + \\log_b y$
- $\\log_b(x/y) = \\log_b x - \\log_b y$
- $\\log_b(x^k) = k\\log_b x$
- $\\log_b a = \\ln a/\\ln b$
- Domain: every log argument must be $> 0$

**Exam patterns:**
- Simplify or evaluate using laws (watch for same base)
- Solve log equations (domain first, filter roots)
- Solve exponential equations ($\\ln$ both sides)
- Analyze $y = \\log_b x$ (intercept, asymptote, monotonicity)

**Last review:** Say each formula once aloud, then solve one checkpoint without notes. Time yourself — a standard log-equation item should take under three minutes once domain checks are automatic. Bring a formula card to the exam but aim to recall domain rules from memory.""",
        "body_he_md": """**כרטיס נוסחאות:**
- $\\log_b a = c \\Leftrightarrow b^c = a$
- $\\log_b(xy) = \\log_b x + \\log_b y$
- $\\log_b(x/y) = \\log_b x - \\log_b y$
- $\\log_b(x^k) = k\\log_b x$
- $\\log_b a = \\ln a/\\ln b$
- תחום: כל ארגומנט לוג חייב להיות $> 0$

**דפוסי בחינה:**
- פישוט או חישוב בחוקי לוג (שימו לב לאותו בסיס)
- משוואות לוג (תחום קודם, סינון שורשים)
- משוואות מעריכיות ($\\ln$ משני האגפים)
- ניתוח $y = \\log_b x$ (חיתוך, אסymptote, מונוטוניות)

**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו נקודת ביקורת בלי רשימות. מדדו זמן — פריט משוואת לוג סטנדרטי צריך להימשך פחות משלוש דקות כשבדיקת תחום אוטומטית.""",
    },
    "summary": {
        "body_en_md": """- **Definition:** $\\log_b a = c \\Leftrightarrow b^c = a$ (conditions: $b>0$, $b\\neq1$, $a>0$)
- **Product:** $\\log_b(xy) = \\log_b x + \\log_b y$
- **Quotient:** $\\log_b(x/y) = \\log_b x - \\log_b y$
- **Power:** $\\log_b(x^k) = k\\log_b x$
- **Change of base:** $\\log_b a = \\ln a/\\ln b$
- **Equation solving:** Domain first → combine or take $\\ln$ → exponentiate → verify roots

**Takeaway:** From the problem wording alone, you should recognize evaluation vs simplification vs log equation vs exponential equation — and write "domain" before any algebra on logs. The three laws plus change of base cover nearly every Bagrut log item.""",
        "body_he_md": """- **הגדרה:** $\\log_b a = c \\Leftrightarrow b^c = a$ (תנאים: $b>0$, $b\\neq1$, $a>0$)
- **כפל:** $\\log_b(xy) = \\log_b x + \\log_b y$
- **חילוק:** $\\log_b(x/y) = \\log_b x - \\log_b y$
- **חזקה:** $\\log_b(x^k) = k\\log_b x$
- **החלפת בסיס:** $\\log_b a = \\ln a/\\ln b$
- **פתרון משוואות:** תחום קודם → איחוד או $\\ln$ → מעבר למעריך → אימות שורשים

**מסקנה:** מניסוח השאלה בלבד, תזהו חישוב מול פישוט מול משוואת לוג מול משוואה מעריכית — ותכתבו "תחום" לפני כל שלב אלגברי על לוגים.""",
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": """All logs share base $4$, so apply laws directly without change of base.

**Step 1:** $\\log_4 16 = 2$ because $4^2 = 16$.

**Step 2:** $\\log_4 4 = 1$ because $4^1 = 4$.

**Step 3:** $\\log_4 8 = \\log_4(4^{3/2}) = 3/2$ (since $4^{3/2} = (2^2)^{3/2} = 2^3 = 8$).

**Step 4:** Sum: $2 + 1 - 3/2 = 3/2$.

**Check:** $4^{3/2} = 8$ confirms the third term. **Answer:** $3/2$.""",
        "checkpoint_solution_he": """כל הלוגים בבסיס $4$, ולכן מיישמים חוקים ישירות בלי החלפת בסיס.

**שלב 1:** $\\log_4 16 = 2$ כי $4^2 = 16$.

**שלב 2:** $\\log_4 4 = 1$ כי $4^1 = 4$.

**שלב 3:** $\\log_4 8 = \\log_4(4^{3/2}) = 3/2$ (כי $4^{3/2} = (2^2)^{3/2} = 2^3 = 8$).

**שלב 4:** סכום: $2 + 1 - 3/2 = 3/2$.

**בדיקה:** $4^{3/2} = 8$ מאשר את האיבר השלישי. **תשובה:** $3/2$.""",
    },
    "checkpoint_2": {
        "checkpoint_solution_en": """Single log equals a constant — convert to exponential form after checking domain.

**Domain:** $2x + 1 > 0$ always satisfied once we find $x$ (we verify at the end).

**Step 1:** $\\log_3(2x+1) = 2$ means $2x + 1 = 3^2 = 9$.

**Step 2:** $2x = 8 \\Rightarrow x = 4$.

**Check:** $\\log_3(2\\cdot4 + 1) = \\log_3 9 = 2$ ✓. Argument $9 > 0$ ✓. **Answer:** $x = 4$.""",
        "checkpoint_solution_he": """לוג בודד שווה לקבוע — מעבר לצורה מעריכית אחרי בדיקת תחום.

**תחום:** $2x + 1 > 0$ — נבדוק בסוף לאחר מציאת $x$.

**שלב 1:** $\\log_3(2x+1) = 2$ פירושו $2x + 1 = 3^2 = 9$.

**שלב 2:** $2x = 8 \\Rightarrow x = 4$.

**בדיקה:** $\\log_3(2\\cdot4 + 1) = \\log_3 9 = 2$ ✓. ארגומנט $9 > 0$ ✓. **תשובה:** $x = 4$.""",
    },
}

EXERCISES = {
    "e1": {
        "solution_en": "**Solution:**\n\nAsk \"$3^? = 81$\". Since $3^4 = 81$, we have $\\log_3 81 = 4$.\n\n**Check:** $3^4 = 81$ ✓. This is pure definition — no laws needed.",
        "solution_he": "**פתרון:**\n\nשואלים \"$3^? = 81$\". מכיוון ש-$3^4 = 81$, מתקבל $\\log_3 81 = 4$.\n\n**בדיקה:** $3^4 = 81$ ✓. זה הגדרה טהורה — לא נדרשים חוקים.",
    },
    "e2": {
        "solution_en": "**Solution:**\n\nAny positive base to power $0$ equals $1$: $5^0 = 1$, so $\\log_5 1 = 0$.\n\n**Check:** Special value $\\log_b 1 = 0$ for all valid bases.",
        "solution_he": "**פתרון:**\n\nכל בסיס חיובי בחזקה $0$ שווה $1$: $5^0 = 1$, ולכן $\\log_5 1 = 0$.\n\n**בדיקה:** ערך מיוחד $\\log_b 1 = 0$ לכל בסיס תקף.",
    },
    "e3": {
        "solution_en": "**Solution:**\n\nSame base → quotient law: $\\log_2 32 - \\log_2 8 = \\log_2(32/8) = \\log_2 4 = 2$.\n\n**Check:** $32/8 = 4 = 2^2$ ✓.",
        "solution_he": "**פתרון:**\n\nאותו בסיס → חוק חילוק: $\\log_2 32 - \\log_2 8 = \\log_2(32/8) = \\log_2 4 = 2$.\n\n**בדיקה:** $32/8 = 4 = 2^2$ ✓.",
    },
    "e4": {
        "solution_en": "**Solution:**\n\nLog requires positive argument: $5 - x > 0 \\Rightarrow x < 5$.\n\n**Check:** At $x = 4$, $\\log_3 1 = 0$ is defined; at $x = 5$, argument is $0$ — excluded.",
        "solution_he": "**פתרון:**\n\nלוג דורש ארגומנט חיובי: $5 - x > 0 \\Rightarrow x < 5$.\n\n**בדיקה:** ב-$x = 4$, $\\log_3 1 = 0$ מוגדר; ב-$x = 5$, הארגומנט $0$ — לא בתחום.",
    },
    "e5": {
        "solution_en": "**Solution path:** Domain: $x^2 - 4 > 0$ → $|x| > 2$. Convert: $x^2 - 4 = 5^1 = 5$, so $x^2 = 9$ and $x = \\pm 3$. Both satisfy $|x| > 2$.\n\n**Check:** $\\log_5(9-4) = \\log_5 5 = 1$ ✓ for both roots.",
        "solution_he": "**דרך פתרון:** תחום: $x^2 - 4 > 0$ → $|x| > 2$. מעבר: $x^2 - 4 = 5$, כלומר $x^2 = 9$ ו-$x = \\pm 3$. שניהם מקיימים $|x| > 2$.\n\n**בדיקה:** $\\log_5(9-4) = \\log_5 5 = 1$ ✓ לשני השורשים.",
    },
    "e6": {
        "solution_en": "**Solution path:** Power law then product/quotient: $3\\log_2 a = \\log_2 a^3$, $\\log_2 c^2 = 2\\log_2 c$, combine: $\\log_2 a^3 - \\log_2 b + 2\\log_2 c = \\log_2\\frac{a^3 c^2}{b}$.\n\n**Check:** Requires $a, b, c > 0$.",
        "solution_he": "**דרך פתרון:** חוק חזקה ואז כפל/חילוק: $3\\log_2 a = \\log_2 a^3$, $\\log_2 c^2 = 2\\log_2 c$, איחוד: $\\log_2 a^3 - \\log_2 b + 2\\log_2 c = \\log_2\\frac{a^3 c^2}{b}$.\n\n**בדיקה:** דורש $a, b, c > 0$.",
    },
    "e7": {
        "solution_en": "**Solution path:** Domain: $x > 1$. Product law: $\\log[(x+2)(x-1)] = 1$, so $(x+2)(x-1) = 10^1 = 10$. Expand: $x^2 + x - 12 = 0$, factors $(x+4)(x-3) = 0$. $x = 3$ valid; $x = -4$ rejected (domain).\n\n**Check:** $(3+2)(3-1) = 10$ ✓.",
        "solution_he": "**דרך פתרון:** תחום: $x > 1$. חוק כפל: $\\log[(x+2)(x-1)] = 1$, לכן $(x+2)(x-1) = 10$. פיתוח: $x^2 + x - 12 = 0$, $(x+4)(x-3) = 0$. $x = 3$ תקף; $x = -4$ נפסל (תחום).\n\n**בדיקה:** $(3+2)(3-1) = 10$ ✓.",
    },
    "e8": {
        "solution_en": "**Solution path:** Change of base: $\\log_7 50 = \\ln 50 / \\ln 7 \\approx 3.912 / 1.946 \\approx 2.01$.\n\n**Check:** $7^{2.01} \\approx 50$ on calculator ✓.",
        "solution_he": "**דרך פתרון:** החלפת בסיס: $\\log_7 50 = \\ln 50 / \\ln 7 \\approx 3.912 / 1.946 \\approx 2.01$.\n\n**בדיקה:** $7^{2.01} \\approx 50$ במחשבון ✓.",
    },
    "e9": {
        "solution_en": "**Solution path:** Take $\\ln$: $2x\\ln 3 = (x+1)\\ln 7$. Collect: $x(2\\ln 3 - \\ln 7) = \\ln 7$, so $x = \\ln 7 / (2\\ln 3 - \\ln 7) \\approx 1.946 / 0.253 \\approx 7.69$.\n\n**Check:** Substitute back — both sides match approximately ✓.",
        "solution_he": "**דרך פתרון:** $\\ln$ משני האגפים: $2x\\ln 3 = (x+1)\\ln 7$. איסוף: $x(2\\ln 3 - \\ln 7) = \\ln 7$, כלומר $x = \\ln 7 / (2\\ln 3 - \\ln 7) \\approx 7.69$.\n\n**בדיקה:** הצבה חוזרת — שני האגפים תואמים בקירוב ✓.",
    },
    "e10": {
        "solution_en": "**Solution path:** Work from outside in. $\\log_3(\\log_2 x) = 1$ means $\\log_2 x = 3^1 = 3$, so $x = 2^3 = 8$.\n\n**Check:** $\\log_2 8 = 3$, then $\\log_3 3 = 1$ ✓. Domain: $x > 0$ satisfied.",
        "solution_he": "**דרך פתרון:** מבחוץ פנימה. $\\log_3(\\log_2 x) = 1$ פירושו $\\log_2 x = 3$, ולכן $x = 2^3 = 8$.\n\n**בדיקה:** $\\log_2 8 = 3$, ואז $\\log_3 3 = 1$ ✓. תחום: $x > 0$ מתקיים.",
    },
    "e11": {
        "solution_en": "**Solution path:** Model: $3^{t/5} = 100$ (100× original). Take $\\ln$: $(t/5)\\ln 3 = \\ln 100$, so $t = 5\\ln 100 / \\ln 3 = 5 \\times 4.605 / 1.099 \\approx 20.95$ hours.\n\n**Check:** $3^{20.95/5} \\approx 3^{4.19} \\approx 100$ ✓.",
        "solution_he": "**דרך פתרון:** מודל: $3^{t/5} = 100$ (פי 100 מהמקור). $\\ln$: $(t/5)\\ln 3 = \\ln 100$, כלומר $t = 5\\ln 100 / \\ln 3 \\approx 20.95$ שעות.\n\n**בדיקה:** $3^{20.95/5} \\approx 100$ ✓.",
    },
    "e12": {
        "solution_en": "**Solution path:** Change of base on each factor: $\\log_a b \\cdot \\log_b c = (\\ln b/\\ln a)(\\ln c/\\ln b) = \\ln c/\\ln a = \\log_a c$. The intermediate $\\ln b$ terms cancel.\n\n**Check:** This is the **chain rule for logs** — memorize as a shortcut.",
        "solution_he": "**דרך פתרון:** החלפת בסיס: $\\log_a b \\cdot \\log_b c = (\\ln b/\\ln a)(\\ln c/\\ln b) = \\ln c/\\ln a = \\log_a c$. האיברים $\\ln b$ מתבטלים.\n\n**בדיקה:** זה **כלל השרשרת ללוגים** — שימושי לשינון.",
    },
    "e13": {
        "solution_en": "**Solution path:** Convert both to base $2$ using change of base: $\\log_4 x = \\log_2 x / 2$, $\\log_8 x = \\log_2 x / 3$. Let $u = \\log_2 x$: $u/2 + u/3 = 5$, so $5u/6 = 5$ and $u = 6$. Thus $x = 2^6 = 64$.\n\n**Check:** $\\log_4 64 = 3$, $\\log_8 64 = 2$, sum $= 5$ ✓.",
        "solution_he": "**דרך פתרון:** המרה לבסיס $2$: $\\log_4 x = \\log_2 x / 2$, $\\log_8 x = \\log_2 x / 3$. נסמן $u = \\log_2 x$: $u/2 + u/3 = 5$, כלומר $u = 6$ ו-$x = 2^6 = 64$.\n\n**בדיקה:** $\\log_4 64 = 3$, $\\log_8 64 = 2$, סכום $= 5$ ✓.",
    },
}

EXPLANATIONS = {
    "q1": fmt_expl(
        "Evaluate each term separately: $\\log_2 8 = 3$ because $2^3 = 8$, and $\\log_3(1/9) = \\log_3 3^{-2} = -2$ by the power law. The sum is $3 + (-2) = 1$, matching option $1$.",
        "For sums of logs with the same base, you would combine first — but here bases differ ($2$ and $3$), so evaluate each term independently. Rewrite fractions as negative powers before applying the power law.",
        "Adding exponents instead of log values ($3 + 2 = 5$), or forgetting that $\\log_3(1/9)$ is negative. Option $0$ comes from treating $1/9$ as if it were $9$.",
        "On Bagrut MCQs with mixed bases, evaluate each log separately on scratch paper before looking at choices — distractors often mirror common sign errors.",
        "$\\log_2 8 = 3$ כי $2^3 = 8$, ו-$\\log_3(1/9) = \\log_3 3^{-2} = -2$ לפי חוק החזקה. הסכום $3 + (-2) = 1$, תואם לאפשרות $1$.",
        "בסכום לוגים עם אותו בסיס היינו מאחדים — אך כאן בסיסים שונים ($2$ ו-$3$), ולכן מחשבים כל איבר בנפרד. כתבו שברים כחזקות שליליות לפני חוק החזקה.",
        "חיבור מעריכים במקום ערכי לוג ($3+2=5$), או שכחת שהערך של $\\log_3(1/9)$ שלילי. אפשרות $0$ נובעת מטיפול ב-$1/9$ כאילו $9$.",
        "בשאלות בגרות עם בסיסים מעורבים — חשבו כל לוג בנפרד על טיוטה לפני בחירה; מסיחים משקפים טעויות סימן.",
    ),
    "q2": fmt_expl(
        "By definition, $\\log_3 81 = c$ means $3^c = 81$. Since $3^4 = 81$, the answer is $4$. No log laws are needed — this is pure equivalence.",
        "Rewrite the question as an exponential: \"What power of $3$ gives $81$?\" Recognize $81 = 3^4$ from memorized powers of $3$ ($3, 9, 27, 81$).",
        "Writing $3 \\times 81$ or dividing $81/3$ instead of finding an exponent. Another error: answering $3$ by confusing base with result.",
        "Memorize $3^4 = 81$ and $2^6 = 64$ — they appear constantly in Bagrut log evaluation items and save calculator time.",
        "לפי הגדרה, $\\log_3 81 = c$ פירושו $3^c = 81$. מכיוון ש-$3^4 = 81$, התשובה $4$. לא נדרשים חוקי לוג — רק ההומכה.",
        "כתבו את השאלה כמעריך: \"איזו חזקה של $3$ נותנת $81$?\" זהו $81 = 3^4$ מרשימת חזקות $3$ ($3, 9, 27, 81$). אם לא זוכרים — פירקו $81 = 3 \\cdot 27 = 3 \\cdot 3^3$.",
        "כתיבת $3 \\times 81$ או חילוק $81/3$ במקום חיפוש מעריך. טעות נוספת: תשובה $3$ — בלבול בסיס עם תוצאה, או $9$ מ-$\\sqrt{81}$.",
        "שיננו $3^4 = 81$ ו-$2^6 = 64$ — הן חוזרות בבגרות וחוסכות זמן מחשבון. כתבו את השרשרת $3 \\to 9 \\to 27 \\to 81$ על טיוטה.",
    ),
    "q3": fmt_expl(
        "$\\log_5 1 = 0$ because $5^0 = 1$ for any valid base $b > 0$, $b \\neq 1$. This is the special value $\\log_b 1 = 0$.",
        "Ask: \"To what power must I raise $5$ to get $1$?\" Only exponent $0$ produces $1$. This rule applies to every log regardless of base.",
        "Answering $1$ by confusing the **result** with the **argument**, or writing $\\log_5 1 = 5$ by confusing base with output.",
        "The three special values — $\\log_b 1 = 0$, $\\log_b b = 1$, $\\log_b(b^k) = k$ — should be reflexes before any calculation on exam day.",
        "$\\log_5 1 = 0$ כי $5^0 = 1$ לכל בסיס תקף $b > 0$, $b \\neq 1$. זה הערך המיוחד $\\log_b 1 = 0$.",
        "שאלו: \"באיזו חזקה מעלים $5$ כדי לקבל $1$?\" רק מעריך $0$ נותן $1$. הכלל תקף לכל בסיס — $\\log_{100} 1 = 0$ גם כן.",
        "תשובה $1$ — בלבול **תוצאה** עם **ארגומנט**, או $\\log_5 1 = 5$ — בלבול בסיס עם פלט. לפעמים כותבים $\\log 1 = 1$.",
        "שלושת הערכים המיוחדים — $\\log_b 1 = 0$, $\\log_b b = 1$, $\\log_b(b^k) = k$ — צריכים להיות שליפה אוטומטית לפני כל חישוב בבחינה.",
    ),
    "q4": fmt_expl(
        "Same base $2$ → quotient law: $\\log_2 32 - \\log_2 8 = \\log_2(32/8) = \\log_2 4 = 2$. Since $2^2 = 4$, the simplified value is $2$.",
        "When you see subtraction of logs with identical bases, merge into a single log of a quotient **before** evaluating. Check that $32/8 = 4$ is a power of the base.",
        "Subtracting the log values numerically without combining ($5 - 3 = 2$ by luck here, but wrong method). Or applying the product law instead of quotient.",
        "Always write the intermediate step $\\log_b x - \\log_b y = \\log_b(x/y)$ on Bagrut — structure marks are awarded even if final arithmetic slips.",
        "אותו בסיס $2$ → חוק חילוק: $\\log_2 32 - \\log_2 8 = \\log_2(32/8) = \\log_2 4 = 2$. מכיוון ש-$2^2 = 4$, הערך $2$.",
        "כשמחסרים לוגים עם בסיס זהה, מאחדים ללוג של מנה **לפני** חישוב. ודאו ש-$32/8 = 4$ הוא חזקה של הבסיס — כאן $4 = 2^2$.",
        "חיסור ערכי לוג בלי איחוד (כאן $5-3=2$ במקרה, אך השיטה שגויה). או שימוש בחוק כפל במקום חילוק — $\\log(32 \\cdot 8)$.",
        "כתבו תמיד $\\log_b x - \\log_b y = \\log_b(x/y)$ בבגרות — נקודות מבנה גם אם החשב הסופי טועה. זהו אחד משלושת חוקי הלוג המרכזיים.",
    ),
    "q5": fmt_expl(
        "The argument $5 - x$ must be positive: $5 - x > 0 \\Rightarrow x < 5$. Domain is all real numbers strictly less than $5$; $x = 5$ is excluded because $\\log_3 0$ is undefined.",
        "Domain questions never require laws — only the inequality \"argument $> 0$\". Write it immediately; graphically, the vertical asymptote of $\\log_3(5-x)$ is at $x = 5$.",
        "Writing $x > 5$ by flipping the inequality sign incorrectly, or giving $x \\leq 5$ and including the endpoint where the log blows up.",
        "Domain answers on Bagrut are often one-line — practice writing $5-x>0$ in under ten seconds so you do not lose easy points on harder items.",
        "הארגומנט $5 - x$ חייב להיות חיובי: $5 - x > 0 \\Rightarrow x < 5$. התחום: כל הממשיים הקטנים מ-$5$; $x = 5$ לא כלול כי $\\log_3 0$ לא מוגדר.",
        "שאלות תחום לא דורשות חוקים — רק \"ארגומנט $> 0$\". כתבו מיד; בגרף, האסymptote של $\\log_3(5-x)$ ב-$x = 5$. נקודת חיתוך: $(4, 0)$.",
        "כתיבת $x > 5$ מהיפוך שגוי של סימן, או $x \\leq 5$ שכולל נקודת קצה שבה הלוג לא מוגדר. גם $x \\neq 5$ בלי לציין כיוון.",
        "תשובות תחום בבגרות לעיתים בשורה אחת — תרגלו $5-x>0$ בפחות מעשר שניות. זהו צעד חובה לפני כל ניתוח גרף של פונקציית לוג.",
    ),
    "q6": fmt_expl(
        "Convert: $\\log_5(x^2-4) = 1$ means $x^2 - 4 = 5^1 = 5$, so $x^2 = 9$ and $x = \\pm 3$. Domain requires $x^2 - 4 > 0$, i.e. $|x| > 2$; both $3$ and $-3$ satisfy this.",
        "Single log equals constant → exponential form. Then check domain **before and after** — here both roots work, unlike typical quadratic traps where one root fails.",
        "Taking $\\pm 3$ without domain check (sometimes one root fails). Or writing only $x = 3$ and dropping $-3$ without verifying.",
        "When $\\log_b(\\text{quadratic}) = c$, always sketch the domain $|x| > 2$-style inequality first — it tells you how many roots can survive.",
        "מעבר: $\\log_5(x^2-4) = 1$ פירושו $x^2 - 4 = 5$, כלומר $x^2 = 9$ ו-$x = \\pm 3$. תחום: $x^2 - 4 > 0$, כלומר $|x| > 2$; גם $3$ וגם $-3$ תקפים.",
        "לוג בודד שווה קבוע → צורה מעריכית. בדקו תחום **לפני ואחרי** — כאן שני השורשים עובדים, בניגוד למלכודות ריבועיות.",
        "לקיחת $\\pm 3$ בלי בדיקת תחום (לפעמים שורש אחד נפסל). או רק $x = 3$ בלי $-3$.",
        "כש-$\\log_b(\\text{ריבועית}) = c$, סרטטו תחום $|x| > 2$ קודם — זה מראה כמה שורשים ישרדו.",
    ),
    "q7": fmt_expl(
        "Apply power law: $3\\log_2 a = \\log_2 a^3$ and $\\log_2 c^2 = 2\\log_2 c$. Combine: $\\log_2 a^3 - \\log_2 b + 2\\log_2 c = \\log_2\\frac{a^3 c^2}{b}$.",
        "Move coefficients into exponents first, then merge with product and quotient laws. All operations require the same base $2$ and positive arguments $a, b, c$.",
        "Adding exponents across different bases, or writing $\\log_2(a^3 - b + c^2)$ by treating the expression as one argument. Coefficients must become powers **before** combining.",
        "On simplification items, list each law you use on a separate line — Bagrut graders look for power law → quotient law structure.",
        "חוק חזקה: $3\\log_2 a = \\log_2 a^3$ ו-$\\log_2 c^2 = 2\\log_2 c$. איחוד: $\\log_2 a^3 - \\log_2 b + 2\\log_2 c = \\log_2\\frac{a^3 c^2}{b}$.",
        "העבירו מקדמים למעריכים קודם, ואז אחדו בחוקי כפל/חילוק. כל הפעולות דורשות בסיס $2$ וארגומנטים חיוביים $a, b, c$ — אלו תנאי השימוש בחוקים.",
        "חיבור מעריכים על בסיסים שונים, או $\\log_2(a^3 - b + c^2)$ — מתייחסים לביטוי כארגומנט אחד. מקדמים חייבים להפוך לחזקות **לפני** איחוד.",
        "בפריטי פישוט, רשמו כל חוק בשורה — בבגרות מחפשים מבנה חוק חזקה → חוק חילוק. התוצאה הסופית $\\log_2\\frac{a^3 c^2}{b}$ היא לוג יחיד.",
    ),
    "q8": fmt_expl(
        "Domain: $x > 1$. Product law gives $\\log[(x+2)(x-1)] = 1$, so $(x+2)(x-1) = 10$. Solving $x^2 + x - 12 = 0$ yields $x = 3$ or $x = -4$; only $x = 3$ satisfies $x > 1$.",
        "Two logs summed → merge to one log of a product, then convert to exponential ($= 10^1$). Domain from **both** arguments: $x+2 > 0$ and $x-1 > 0$, combined to $x > 1$.",
        "Accepting $x = -4$ without domain check (makes $x-1$ negative). Or setting $(x+2)+(x-1) = 10$ by falsely distributing log over addition.",
        "Classic Bagrut trap: always write domain as the **stricter** of all argument inequalities — here $x > 1$ beats $x > -2$.",
        "תחום: $x > 1$. חוק כפל: $\\log[(x+2)(x-1)] = 1$, לכן $(x+2)(x-1) = 10$. פתרון $x^2 + x - 12 = 0$ נותן $x = 3$ או $x = -4$; רק $x = 3$ מקיים $x > 1$.",
        "שני לוגים בסכום → איחוד ללוג של מכפלה, ואז מעבר למעריך ($= 10^1$). תחום מ**שני** הארגומנטים: $x+2 > 0$ ו-$x-1 > 0$, משולב ל-$x > 1$.",
        "קבלת $x = -4$ בלי בדיקת תחום (הופך $x-1$ לשלילי). או $(x+2)+(x-1) = 10$ — פיזור שגוי של לוג על חיבור.",
        "מלכודת בגרות קלאסית: כתבו תחום כ**המחמיר** מכל אי-השוויונות — כאן $x > 1$ ולא רק $x > -2$.",
    ),
}

SUMMARY_HE = (
    "לוגריתמים הם **ההפכיים** של פונקציות מעריכיות ומופיעים בכל תחום: "
    "pH בכימיה, סקלת ריכטר לרעידות אדמה, דציבלים לצליל, ודעיכה מעריכית בפיזיקה."
)


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        sid = sec.get("id", kind)
        if kind not in EXPAND_KINDS:
            if kind == "checkpoint":
                for key in ("checkpoint_solution_en", "checkpoint_solution_he"):
                    if wc(sec.get(key, "")) < 25:
                        errors.append(f"{sid}: {key} too short ({wc(sec.get(key, ''))} words)")
            continue
        min_key = "worked_example" if kind == "worked_example" else kind
        en_min, he_min = MIN[min_key]
        en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        if en_w < en_min:
            errors.append(f"{sid}: EN {en_w} < {en_min}")
        if he_w < he_min:
            errors.append(f"{sid}: HE {he_w} < {he_min}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"{sid}: weak Hebrew")

    for q in data["questions"]:
        ew, hw = wc(q.get("explanation_en", "")), wc(q.get("explanation_he", ""))
        if ew < 80:
            errors.append(f"q{q['ord']} expl-en {ew} < 80")
        if ew > 150:
            errors.append(f"q{q['ord']} expl-en {ew} > 150")
        if hw < 80:
            errors.append(f"q{q['ord']} expl-he {hw} < 80")
        if hw > 150:
            errors.append(f"q{q['ord']} expl-he {hw} > 150")

    return errors


def run_node_wordcheck() -> None:
    script = """
import { readFileSync } from 'node:fs';
import { wordCount, hebrewBodyWeak, MIN_WORDS } from './scripts/lib/bilingual-utils.mjs';
const data = JSON.parse(readFileSync('scripts/seed_data/lessons/logarithms.json','utf8'));
const errs = [];
for (const s of data.sections) {
  const min = MIN_WORDS[s.kind];
  if (!min) continue;
  if (wordCount(s.body_en_md) < min.en) errs.push(s.id + ' en');
  if (wordCount(s.body_he_md) < min.he) errs.push(s.id + ' he');
  if (hebrewBodyWeak(s.body_he_md, s.body_en_md)) errs.push(s.id + ' weak-he');
}
for (const q of data.questions) {
  if (wordCount(q.explanation_en) < 80) errs.push('q'+q.ord+' expl-en');
  if (wordCount(q.explanation_he) < 80) errs.push('q'+q.ord+' expl-he');
}
if (errs.length) { console.error('node check:', errs.join(', ')); process.exit(1); }
console.log('node bilingual-utils check OK');
"""
    result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        raise SystemExit(result.returncode)
    print(result.stdout.strip())


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    data["summary_he"] = SUMMARY_HE

    for sec in data["sections"]:
        sid = sec.get("id", sec["kind"])
        if sid in SECTIONS:
            sec["body_en_md"] = SECTIONS[sid]["body_en_md"]
            sec["body_he_md"] = SECTIONS[sid]["body_he_md"]
        if sid in CHECKPOINTS:
            sec["checkpoint_solution_en"] = CHECKPOINTS[sid]["checkpoint_solution_en"]
            sec["checkpoint_solution_he"] = CHECKPOINTS[sid]["checkpoint_solution_he"]

    ex_sec = next(s for s in data["sections"] if s["kind"] == "exercise_set")
    for ex in ex_sec["exercises"]:
        eid = ex["id"]
        if eid in EXERCISES:
            ex["solution_en"] = EXERCISES[eid]["solution_en"]
            ex["solution_he"] = EXERCISES[eid]["solution_he"]

    for q in data["questions"]:
        qid = q.get("id") or f"q{q['ord']}"
        key = qid if qid in EXPLANATIONS else f"q{q['ord']}"
        if key in EXPLANATIONS:
            en, he = EXPLANATIONS[key]
            q["explanation_en"] = en
            q["explanation_he"] = he

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)

    run_node_wordcheck()
    print(f"OK — expanded {TARGET.name}")


if __name__ == "__main__":
    main()
