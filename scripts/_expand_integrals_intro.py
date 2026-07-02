#!/usr/bin/env python3
"""Expand integrals_intro.json — substantive bilingual content per expand-lessons-cursor."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/integrals_intro.json"


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


lesson = {
    "concept_id": "integrals_intro",
    "subject": "calculus_1",
    "level": "university",
    "math_track": ["calc1", "5pt"],
    "title_en": "Introduction to Integration",
    "title_he": "מבוא לאינטגרציה",
    "summary_en": "Antiderivatives, indefinite integrals, and basic integration rules. The connection between differentiation and integration (FTC). Power rule, constant rule, basic trig and exponential integrals.",
    "summary_he": "נגזרות הפוכות, אינטגרלים לא מסויימים, וכללי אינטגרציה בסיסיים. הקשר בין גזירה ואינטגרציה (משפט יסודי החשבון). כלל החזקה, פונקציות טריגו ומעריכי.",
    "sections": [
        {
            "kind": "intro",
            "title_en": "The Reverse of Differentiation",
            "title_he": "ההפוך של גזירה",
            "body_en_md": """Differentiation answers: *given $f(x)$, find $f'(x)$.* **Integration** answers the reverse question: *given $f'(x)$, find $f(x)$.*

Example: we know $\\frac{d}{dx}(x^2) = 2x$. So an **antiderivative** of $2x$ is $x^2$. But also $x^2+5$, $x^2-7$, and $x^2+C$ for any constant $C$ — all have derivative $2x$. The antiderivative is therefore a **family** of functions, not a single curve.

**Why integration matters across the curriculum:**
- **Geometry:** compute signed area under a curve and between curves.
- **Physics:** recover position from velocity, velocity from acceleration; work $W=\\int F\\,dx$.
- **Differential equations:** integration is the first tool for solving $\\frac{dy}{dx}=g(x)$.
- **Exams (Bagrut 5-unit / Calc 1):** every FTC problem, initial-value problem, and area question starts here.

If you can differentiate confidently, you already know half of integration — the other half is recognizing which rule reverses each derivative pattern and remembering the constant $+C$.""",
            "body_he_md": """גזירה עונה על השאלה: *בהינתן $f(x)$, מצא $f'(x)$.* **אינטגרציה** עונה על ההפוך: *בהינתן $f'(x)$, מצא $f(x)$.*

דוגמה: $\\frac{d}{dx}(x^2)=2x$, ולכן **נגזרת הפוכה** של $2x$ היא $x^2$. אבל גם $x^2+5$, $x^2-7$ ו-$x^2+C$ לכל קבוע $C$ — לכולן נגזרת $2x$. הנגזרת ההפוכה היא **משפחה** של פונקציות, לא עקומה בודדת.

**למה אינטגרציה חשובה בכל המסלול:**
- **גיאומטריה:** חישוב שטח עם סימן מתחת לעקומה ובין עקומות.
- **פיזיקה:** שחזור מיקום ממהירות, מהירות מתאוצה; עבודה $W=\\int F\\,dx$.
- **משוואות דיפרנציאליות:** אינטגרציה היא הכלי הראשון לפתרון $\\frac{dy}{dx}=g(x)$.
- **בחינות (בגרות 5 יחידות / חדו״א 1):** כל שאלת FTC, בעיית ערך התחלתי ושטח מתחילה כאן.

אם אתם יודעים לגזור בביטחון — כבר יודעים חצי מאינטגרציה. החצי השני: לזהות איזה כלל הופך כל דפוס נגזרת, ולזכור את הקבוע $+C$.""",
        },
        {
            "kind": "definition",
            "title_en": "Antiderivative and Indefinite Integral",
            "title_he": "נגזרת הפוכה ואינטגרל לא מסויים",
            "body_en_md": """**Antiderivative:** A function $F(x)$ is an antiderivative of $f(x)$ on an interval if $F'(x)=f(x)$ for every $x$ in that interval.

**Indefinite integral:** The collection of all antiderivatives is written
$$\\int f(x)\\,dx = F(x) + C,$$
where $F'(x)=f(x)$ and $C$ is an arbitrary constant called the **constant of integration**.

**Why $+C$ is mandatory:** Differentiating any constant gives zero, so you cannot recover the vertical shift from the derivative alone. On exams, omitting $+C$ on an indefinite integral is an automatic deduction.

**Fundamental Theorem of Calculus (Part 2):** If $F'(x)=f(x)$ on $[a,b]$, then
$$\\int_a^b f(x)\\,dx = F(b) - F(a).$$
This connects antiderivatives to **definite** integrals (signed net area).

**Evaluation notation:** $[F(x)]_a^b = F(b)-F(a)$. Example: $[x^2]_0^3 = 9-0=9$.

**Terminology:** $\\int f(x)\\,dx$ is *indefinite* (function + $C$); $\\int_a^b f(x)\\,dx$ is *definite* (a number).

**Uniqueness up to a constant:** If $F$ and $G$ are both antiderivatives of $f$ on an interval, then $G(x)=F(x)+C$ for some constant $C$. That is why we write one representative plus $+C$ rather than listing infinitely many functions.""",
            "body_he_md": """**נגזרת הפוכה:** הפונקציה $F(x)$ היא נגזרת הפוכה של $f(x)$ בקטע אם $F'(x)=f(x)$ לכל $x$ בקטע.

**אינטגרל לא מסויים:** כל הנגזרות ההפוכות מסומנות
$$\\int f(x)\\,dx = F(x) + C,$$
כאשר $F'(x)=f(x)$ ו-$C$ הוא קבוע שרירותי — **קבוע האינטגרציה**.

**למה $+C$ חובה:** נגזרת של כל קבוע היא אפס, ולכן אי אפשר לשחזר את ההזזה האנכית מהנגזרת בלבד. בבחינות, השמטת $+C$ באינטגרל לא מסויים מורידה נקודות.

**משפט יסודי החשבון (חלק 2):** אם $F'(x)=f(x)$ ב-$[a,b]$, אז
$$\\int_a^b f(x)\\,dx = F(b) - F(a).$$
זה מחבר נגזרות הפוכות ל**אינטגרלים מסוימים** (שטח נטו עם סימן).

**סימון חישוב:** $[F(x)]_a^b = F(b)-F(a)$. דוגמה: $[x^2]_0^3 = 9-0=9$.

**טרמינולוגיה:** $\\int f(x)\\,dx$ *לא מסוים* (פונקציה + $C$); $\\int_a^b f(x)\\,dx$ *מסוים* (מספר).

**ייחוד עד קבוע:** אם $F$ ו-$G$ שתיהן נגזרות הפוכות של $f$ בקטע, אז $G(x)=F(x)+C$ עבור קבוע $C$ כלשהו. לכן כותבים נציג אחד ו-$+C$ במקום רשימה אינסופית של פונקציות.""",
        },
        {
            "kind": "theory",
            "title_en": "Basic Integration Rules",
            "title_he": "כללי אינטגרציה בסיסיים",
            "body_en_md": """Every basic integration rule is the reverse of a differentiation rule you already know.

**Power rule** ($n\\ne-1$):
$$\\int x^n\\,dx = \\frac{x^{n+1}}{n+1}+C.$$
*Reverse of* $\\frac{d}{dx}(x^{n+1})=(n+1)x^n$.

**Reciprocal (exception $n=-1$):**
$$\\int \\frac{1}{x}\\,dx = \\ln|x|+C.$$
The absolute value ensures the domain matches the derivative of $\\ln|x|$.

**Exponential:**
$$\\int e^x\\,dx = e^x+C, \\qquad \\int a^x\\,dx = \\frac{a^x}{\\ln a}+C \\quad (a>0, a\\ne 1).$$

**Trigonometric (most common on exams):**
- $\\int \\sin x\\,dx = -\\cos x+C$ (reverse of $(\\cos x)'=-\\sin x$).
- $\\int \\cos x\\,dx = \\sin x+C$.
- $\\int \\sec^2 x\\,dx = \\tan x+C$.

**Linearity** — integrate term by term:
$$\\int [f(x)\\pm g(x)]\\,dx = \\int f\\,dx \\pm \\int g\\,dx, \\qquad \\int kf(x)\\,dx = k\\int f(x)\\,dx.$$

**Verification habit:** differentiate your answer. If you recover the integrand, the algebra is correct. This 10-second check catches sign errors and forgotten $+C$ before you submit.""",
            "body_he_md": """כל כלל אינטגרציה בסיסי הוא היפוך של כלל גזירה שכבר מכירים.

**כלל החזקה** ($n\\ne-1$):
$$\\int x^n\\,dx = \\frac{x^{n+1}}{n+1}+C.$$
*היפוך של* $\\frac{d}{dx}(x^{n+1})=(n+1)x^n$.

**הדדי (חריג $n=-1$):**
$$\\int \\frac{1}{x}\\,dx = \\ln|x|+C.$$
ערך מוחלט מבטיח שהתחום תואם לנגזרת $\\ln|x|$.

**מעריכי:**
$$\\int e^x\\,dx = e^x+C, \\qquad \\int a^x\\,dx = \\frac{a^x}{\\ln a}+C \\quad (a>0, a\\ne 1).$$

**טריגונומטרי (נפוץ בבחינות):**
- $\\int \\sin x\\,dx = -\\cos x+C$ (היפוך $(\\cos x)'=-\\sin x$).
- $\\int \\cos x\\,dx = \\sin x+C$.
- $\\int \\sec^2 x\\,dx = \\tan x+C$.

**ליניאריות** — אינטגרל איבר-איבר:
$$\\int [f(x)\\pm g(x)]\\,dx = \\int f\\,dx \\pm \\int g\\,dx, \\qquad \\int kf(x)\\,dx = k\\int f(x)\\,dx.$$

**הרגל אימות:** גזרו את התשובה. אם חוזרים לפונקציה המקורית — האלגברה נכונה. בדיקה של 10 שניות תופסת שגיאות סימן ו-$+C$ חסר לפני הגשה.""",
        },
        {
            "kind": "worked_example",
            "difficulty": "easy",
            "example_number": 1,
            "title_en": "Worked Example 1 — Basic Antiderivatives",
            "title_he": "דוגמה פתורה 1 — נגזרות הפוכות בסיסיות",
            "body_en_md": """**Find** $\\int (3x^2 + 2x - 5)\\,dx$.

### Move 1: Apply the power rule to each term separately.
Linearity lets us integrate term by term:
$$\\int 3x^2\\,dx = 3\\cdot\\frac{x^3}{3} = x^3.$$
$$\\int 2x\\,dx = 2\\cdot\\frac{x^2}{2} = x^2.$$
$$\\int (-5)\\,dx = -5x.$$

### Move 2: Combine and add the constant of integration.
$$\\int (3x^2+2x-5)\\,dx = x^3+x^2-5x+C.$$

### Move 3: Verify by differentiating.
$$\\frac{d}{dx}(x^3+x^2-5x+C) = 3x^2+2x-5. \\checkmark$$

**Answer:** $\\boxed{x^3+x^2-5x+C}$""",
            "body_he_md": """**מצאו** $\\int (3x^2 + 2x - 5)\\,dx$.

### צעד 1: כלל החזקה לכל איבר בנפרד.
ליניאריות מאפשרת אינטגרציה איבר-איבר:
$$\\int 3x^2\\,dx = 3\\cdot\\frac{x^3}{3} = x^3.$$
$$\\int 2x\\,dx = 2\\cdot\\frac{x^2}{2} = x^2.$$
$$\\int (-5)\\,dx = -5x.$$

### צעד 2: חיבור והוספת קבוע האינטגרציה.
$$\\int (3x^2+2x-5)\\,dx = x^3+x^2-5x+C.$$

### צעד 3: אימות בגזירה.
$$\\frac{d}{dx}(x^3+x^2-5x+C) = 3x^2+2x-5. \\checkmark$$

**תשובה:** $\\boxed{x^3+x^2-5x+C}$""",
        },
        {
            "kind": "checkpoint",
            "title_en": "Stop & Practice",
            "title_he": "עצור ותרגל",
            "body_en_md": "Find: (a) $\\int \\frac{1}{x^2}\\,dx$, (b) $\\int \\sqrt{x}\\,dx$, (c) $\\int (e^x + \\cos x)\\,dx$.",
            "body_he_md": "מצאו: (א) $\\int x^{-2}\\,dx$, (ב) $\\int \\sqrt{x}\\,dx$, (ג) $\\int(e^x+\\cos x)\\,dx$.",
            "checkpoint_solution_en": """**(a)** Rewrite $\\frac{1}{x^2}=x^{-2}$. Power rule ($n=-2\\ne-1$):
$$\\int x^{-2}\\,dx = \\frac{x^{-1}}{-1}+C = -\\frac{1}{x}+C.$$

**(b)** Rewrite $\\sqrt{x}=x^{1/2}$:
$$\\int x^{1/2}\\,dx = \\frac{x^{3/2}}{3/2}+C = \\frac{2}{3}x^{3/2}+C.$$

**(c)** Use standard rules term by term:
$$\\int(e^x+\\cos x)\\,dx = e^x+\\sin x+C.$$

**Check:** Differentiate each answer — you should recover the integrand.""",
            "checkpoint_solution_he": """**(א)** כתיבה $x^{-2}$. כלל חזקה ($n=-2\\ne-1$):
$$\\int x^{-2}\\,dx = \\frac{x^{-1}}{-1}+C = -\\frac{1}{x}+C.$$

**(ב)** כתיבה $x^{1/2}$:
$$\\int x^{1/2}\\,dx = \\frac{x^{3/2}}{3/2}+C = \\frac{2}{3}x^{3/2}+C.$$

**(ג)** כללים סטנדרטיים איבר-איבר:
$$\\int(e^x+\\cos x)\\,dx = e^x+\\sin x+C.$$

**בדיקה:** גזרו כל תשובה — אמורה לחזור הפונקציה המקורית.""",
        },
        {
            "kind": "worked_example",
            "difficulty": "medium",
            "example_number": 2,
            "title_en": "Worked Example 2 — Definite Integral (FTC)",
            "title_he": "דוגמה פתורה 2 — אינטגרל מסויים (FTC)",
            "body_en_md": """**Evaluate** $\\int_1^3 (x^2-4x+3)\\,dx$.

### Move 1: Find an antiderivative (no $+C$ needed for definite integrals).
$$F(x) = \\frac{x^3}{3}-2x^2+3x.$$

### Move 2: Apply FTC — evaluate at the upper and lower limits.
$$F(3) = \\frac{27}{3}-2(9)+3(3) = 9-18+9 = 0.$$
$$F(1) = \\frac{1}{3}-2(1)+3(1) = \\frac{1}{3}-2+3 = \\frac{4}{3}.$$

### Move 3: Subtract lower from upper.
$$\\int_1^3(x^2-4x+3)\\,dx = F(3)-F(1) = 0-\\frac{4}{3} = -\\frac{4}{3}.$$

**Interpretation:** The negative value means the curve $y=x^2-4x+3$ lies **below** the $x$-axis on $[1,3]$ — the net signed area is $-\\frac{4}{3}$ square units.""",
            "body_he_md": """**חשבו** $\\int_1^3 (x^2-4x+3)\\,dx$.

### צעד 1: מציאת נגזרת הפוכה (בלי $+C$ באינטגרל מסוים).
$$F(x) = \\frac{x^3}{3}-2x^2+3x.$$

### צעד 2: יישום FTC — חישוב בגבולות.
$$F(3) = \\frac{27}{3}-2(9)+3(3) = 9-18+9 = 0.$$
$$F(1) = \\frac{1}{3}-2+3 = \\frac{4}{3}.$$

### צעד 3: חיסור תחתון מעליון.
$$\\int_1^3(x^2-4x+3)\\,dx = 0-\\frac{4}{3} = -\\frac{4}{3}.$$

**פרשנות:** הערך השלילי אומר שהעקומה $y=x^2-4x+3$ **מתחת** לציר $x$ ב-$[1,3]$ — השטח הנטו עם סימן הוא $-\\frac{4}{3}$ יחידות ריבוע.""",
        },
        {
            "kind": "checkpoint",
            "title_en": "Stop & Practice",
            "title_he": "עצור ותרגל",
            "body_en_md": "Evaluate $\\int_0^\\pi \\sin x\\,dx$ and explain why $\\int_0^{2\\pi}\\sin x\\,dx=0$.",
            "body_he_md": "חשבו $\\int_0^\\pi\\sin x\\,dx$ והסבירו מדוע $\\int_0^{2\\pi}\\sin x\\,dx=0$.",
            "checkpoint_solution_en": """**First integral:**
$$\\int_0^\\pi \\sin x\\,dx = [-\\cos x]_0^\\pi = (-\\cos\\pi)-(-\\cos 0) = -(-1)-(-1) = 1+1 = 2.$$

**Second integral:**
$$\\int_0^{2\\pi}\\sin x\\,dx = [-\\cos x]_0^{2\\pi} = (-1)-(-1) = 0.$$

**Explanation:** On $[0,\\pi]$, $\\sin x\\ge 0$ — the graph is above the axis, contributing $+2$ signed area. On $[\\pi,2\\pi]$, $\\sin x\\le 0$ — the graph is below the axis, contributing $-2$. Equal magnitudes, opposite signs → net zero. This is why \"area under one arch\" and \"area over a full period\" are different questions.""",
            "checkpoint_solution_he": """**אינטגרל ראשון:**
$$\\int_0^\\pi \\sin x\\,dx = [-\\cos x]_0^\\pi = 1+1 = 2.$$

**אינטגרל שני:**
$$\\int_0^{2\\pi}\\sin x\\,dx = [-\\cos x]_0^{2\\pi} = 0.$$

**הסבר:** ב-$[0,\\pi]$, $\\sin x\\ge 0$ — העקומה מעל הציר, תורם $+2$ שטח עם סימן. ב-$[\\pi,2\\pi]$, $\\sin x\\le 0$ — מתחת לציר, תורם $-2$. גודל שווה, סימן הפוך → סכום אפס. לכן \"שטח תחת קשת אחת\" ו\"שטח על מחזור שלם\" הן שאלות שונות.""",
        },
        {
            "kind": "worked_example",
            "difficulty": "hard",
            "example_number": 3,
            "title_en": "Worked Example 3 — Initial Value Problem (Exam Level)",
            "title_he": "דוגמה פתורה 3 — בעיית ערך התחלתי (רמת בחינה)",
            "body_en_md": """**Given:** $f''(x) = 6x-2$, $f'(0)=1$, $f(0)=3$. Find $f(x)$.

### Move 1: Integrate $f''$ to get $f'$, then use the first initial condition.
$$f'(x) = \\int(6x-2)\\,dx = 3x^2-2x+C_1.$$
Use $f'(0)=1$: $1=0-0+C_1\\Rightarrow C_1=1$.
$$f'(x) = 3x^2-2x+1.$$

### Move 2: Integrate $f'$ to get $f$, then use the second initial condition.
$$f(x) = \\int(3x^2-2x+1)\\,dx = x^3-x^2+x+C_2.$$
Use $f(0)=3$: $3=0-0+0+C_2\\Rightarrow C_2=3$.

### Move 3: Verify both conditions.
$f'(0)=1$ ✓, $f(0)=3$ ✓.

**Result:** $\\boxed{f(x) = x^3-x^2+x+3}$""",
            "body_he_md": """**נתון:** $f''(x) = 6x-2$, $f'(0)=1$, $f(0)=3$. מצאו $f(x)$.

### צעד 1: אינטגרציה של $f''$ לקבלת $f'$, שימוש בתנאי ראשון.
$$f'(x) = \\int(6x-2)\\,dx = 3x^2-2x+C_1.$$
מ-$f'(0)=1$: $C_1=1$, ולכן $f'(x) = 3x^2-2x+1$.

### צעד 2: אינטגרציה של $f'$ לקבלת $f$, שימוש בתנאי שני.
$$f(x) = \\int(3x^2-2x+1)\\,dx = x^3-x^2+x+C_2.$$
מ-$f(0)=3$: $C_2=3$.

### צעד 3: אימות שני התנאים.
$f'(0)=1$ ✓, $f(0)=3$ ✓.

**תוצאה:** $\\boxed{f(x) = x^3-x^2+x+3}$""",
        },
        {
            "kind": "method_guide",
            "title_en": "Method Guide — Integration",
            "title_he": "מדריך שיטה — אינטגרציה",
            "body_en_md": """| Task | Steps | Key reminder |
|------|-------|--------------|
| Indefinite integral | Identify type → apply rule → add $+C$ → differentiate to verify | Never skip $+C$ |
| Definite integral (FTC) | Find $F(x)$ → compute $F(b)-F(a)$ | $+C$ cancels — not needed |
| Initial value problem | Integrate → use condition → repeat for each derivative order | Label $C_1, C_2$ clearly |
| Fraction/radical integrand | Rewrite as $x^n$ first | $1/x^2=x^{-2}$, $\\sqrt{x}=x^{1/2}$ |

**Indefinite integral workflow:**
1. Simplify the integrand (split fractions, rewrite radicals).
2. Apply linearity — integrate each term.
3. Match each term to a table rule.
4. Add $+C$ once at the end.
5. Differentiate to verify.

**Definite integral workflow:**
1. Find any antiderivative $F$.
2. Evaluate $F(b)-F(a)$ carefully — bracket notation $[F(x)]_a^b$ helps avoid sign errors.

**Quick reference table:**

| Integrand | Antiderivative |
|---|---|
| $x^n$ ($n\\ne-1$) | $x^{n+1}/(n+1)+C$ |
| $1/x$ | $\\ln|x|+C$ |
| $e^x$ | $e^x+C$ |
| $\\sin x$ | $-\\cos x+C$ |
| $\\cos x$ | $\\sin x+C$ |
| $\\sec^2 x$ | $\\tan x+C$ |""",
            "body_he_md": """| משימה | צעדים | תזכורת |
|------|-------|--------|
| אינטגרל לא מסויים | זיהוי סוג → כלל → $+C$ → גזירה לאימות | אל תדלגו על $+C$ |
| אינטגרל מסוים (FTC) | מצא $F(x)$ → חשב $F(b)-F(a)$ | $+C$ מתבטל |
| בעיית ערך התחלתי | אינטגרל → תנאי → חזרה לכל נגזרת | סמנו $C_1, C_2$ |
| שבר/שורש | כתיבה כ-$x^n$ קודם | $1/x^2=x^{-2}$, $\\sqrt{x}=x^{1/2}$ |

**תהליך לא מסויים:**
1. פישוט הפונקציה התחתית (פיצול שברים, שורשים).
2. ליניאריות — אינטגרל לכל איבר.
3. התאמה לכלל בטבלה.
4. $+C$ פעם אחת בסוף.
5. גזירה לאימות.

**תהליך מסויים:**
1. מצא נגזרת הפוכה $F$.
2. חשב $F(b)-F(a)$ בזהירות — סימון $[F(x)]_a^b$ מונע שגיאות סימן.

**טבלת עזר:**

| פונקציה | אינטגרל |
|---|---|
| $x^n$ ($n\\ne-1$) | $x^{n+1}/(n+1)+C$ |
| $1/x$ | $\\ln|x|+C$ |
| $e^x$ | $e^x+C$ |
| $\\sin x$ | $-\\cos x+C$ |
| $\\cos x$ | $\\sin x+C$ |
| $\\sec^2 x$ | $\\tan x+C$ |""",
        },
        {
            "kind": "exercise_set",
            "title_en": "Practice Exercises",
            "title_he": "תרגילים",
            "body_en_md": "Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.",
            "body_he_md": "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.",
            "exercises": [
                {
                    "id": "e1",
                    "difficulty": "easy",
                    "body_en": "$\\int(4x^3-3x+1)\\,dx$",
                    "body_he": "$\\int(4x^3-3x+1)\\,dx$",
                    "solution_en": "Power rule on each term: $\\int 4x^3=x^4$, $\\int(-3x)=-\\frac{3x^2}{2}$, $\\int 1=x$. **Answer:** $x^4-\\frac{3x^2}{2}+x+C$. Verify: $(x^4-\\frac{3x^2}{2}+x+C)'=4x^3-3x+1$ ✓",
                    "solution_he": "כלל חזקה: $\\int 4x^3=x^4$, $\\int(-3x)=-\\frac{3x^2}{2}$, $\\int 1=x$. **תשובה:** $x^4-\\frac{3x^2}{2}+x+C$. אימות: $(x^4-\\frac{3x^2}{2}+x+C)'=4x^3-3x+1$ ✓",
                },
                {
                    "id": "e2",
                    "difficulty": "easy",
                    "body_en": "$\\int(\\sin x+e^x)\\,dx$",
                    "body_he": "$\\int(\\sin x+e^x)\\,dx$",
                    "solution_en": "Standard rules: $\\int\\sin x=-\\cos x$, $\\int e^x=e^x$. **Answer:** $-\\cos x+e^x+C$.",
                    "solution_he": "כללים סטנדרטיים: $\\int\\sin x=-\\cos x$, $\\int e^x=e^x$. **תשובה:** $-\\cos x+e^x+C$.",
                },
                {
                    "id": "e3",
                    "difficulty": "easy",
                    "body_en": "Evaluate $\\int_0^2 x^3\\,dx$.",
                    "body_he": "חשבו $\\int_0^2 x^3\\,dx$.",
                    "solution_en": "Antiderivative: $x^4/4$. FTC: $[x^4/4]_0^2=16/4-0=4$.",
                    "solution_he": "נגזרת הפוכה: $x^4/4$. FTC: $[x^4/4]_0^2=16/4=4$.",
                },
                {
                    "id": "e4",
                    "difficulty": "easy",
                    "body_en": "$\\int\\left(\\frac{1}{x^3}+\\sqrt[3]{x}\\right)dx$",
                    "body_he": "$\\int(x^{-3}+x^{1/3})\\,dx$",
                    "solution_en": "Rewrite: $x^{-3}+x^{1/3}$. $\\int x^{-3}=-x^{-2}/2$, $\\int x^{1/3}=\\frac{3x^{4/3}}{4}$. **Answer:** $-\\frac{1}{2x^2}+\\frac{3x^{4/3}}{4}+C$.",
                    "solution_he": "כתיבה: $x^{-3}+x^{1/3}$. $\\int x^{-3}=-x^{-2}/2$, $\\int x^{1/3}=\\frac{3x^{4/3}}{4}$. **תשובה:** $-\\frac{1}{2x^2}+\\frac{3x^{4/3}}{4}+C$.",
                },
                {
                    "id": "e5",
                    "difficulty": "medium",
                    "body_en": "$\\int\\frac{x^2+x-1}{x^2}\\,dx$ (split the fraction first).",
                    "body_he": "$\\int(x^2+x-1)/x^2\\,dx$ (פצלו ראשה).",
                    "solution_en": "Split: $\\frac{x^2+x-1}{x^2}=1+\\frac{1}{x}-x^{-2}$. Integrate: $x+\\ln|x|+\\frac{1}{x}+C$. (Note: $\\int x^{-2}=-x^{-1}=1/x$ with sign.)",
                    "solution_he": "פיצול: $1+\\frac{1}{x}-x^{-2}$. אינטגרל: $x+\\ln|x|+\\frac{1}{x}+C$.",
                },
                {
                    "id": "e6",
                    "difficulty": "medium",
                    "body_en": "Find $f(x)$ if $f'(x)=3e^x-2\\sin x$ and $f(0)=1$.",
                    "body_he": "מצאו $f$ אם $f'=3e^x-2\\sin x$, $f(0)=1$.",
                    "solution_en": "Integrate: $f(x)=3e^x+2\\cos x+C$. Use $f(0)=1$: $3+2+C=1\\Rightarrow C=-4$. **Answer:** $f(x)=3e^x+2\\cos x-4$.",
                    "solution_he": "אינטגרל: $f(x)=3e^x+2\\cos x+C$. מ-$f(0)=1$: $C=-4$. **תשובה:** $f(x)=3e^x+2\\cos x-4$.",
                },
                {
                    "id": "e7",
                    "difficulty": "medium",
                    "body_en": "Evaluate $\\int_{-1}^1(x^3+x)\\,dx$ (use symmetry).",
                    "body_he": "חשבו $\\int_{-1}^1(x^3+x)\\,dx$ (השתמשו בסימטריה).",
                    "solution_en": "$f(x)=x^3+x$ is **odd**: $f(-x)=-f(x)$. For odd $f$ on symmetric $[-a,a]$: $\\int_{-a}^a f=0$. **Answer:** $0$.",
                    "solution_he": "$f(x)=x^3+x$ **אי-זוגית**: $f(-x)=-f(x)$. על $[-a,a]$: $\\int_{-a}^a f=0$. **תשובה:** $0$.",
                },
                {
                    "id": "e8",
                    "difficulty": "medium",
                    "body_en": "$\\int_0^{\\pi/2}(\\sin x+2\\cos x)\\,dx$",
                    "body_he": "$\\int_0^{\\pi/2}(\\sin x+2\\cos x)\\,dx$",
                    "solution_en": "Antiderivative: $-\\cos x+2\\sin x$. At $\\pi/2$: $0+2=2$. At $0$: $-1+0=-1$. Difference: $2-(-1)=3$.",
                    "solution_he": "נגזרת הפוכה: $-\\cos x+2\\sin x$. ב-$\\pi/2$: $2$. ב-$0$: $-1$. הפרש: $3$.",
                },
                {
                    "id": "e9",
                    "difficulty": "medium",
                    "body_en": "If $f''(x)=\\cos x$ and $f'(0)=0$, $f(0)=1$, find $f(x)$.",
                    "body_he": "$f''=\\cos x$, $f'(0)=0$, $f(0)=1$. מצאו $f$.",
                    "solution_en": "$f'(x)=\\sin x+C_1$; $f'(0)=0\\Rightarrow C_1=0$. $f(x)=-\\cos x+C_2$; $f(0)=-1+C_2=1\\Rightarrow C_2=2$. **Answer:** $f(x)=2-\\cos x$.",
                    "solution_he": "$f'(x)=\\sin x$; $f(x)=-\\cos x+C_2$; $f(0)=1\\Rightarrow C_2=2$. **תשובה:** $f(x)=2-\\cos x$.",
                },
                {
                    "id": "e10",
                    "difficulty": "hard",
                    "body_en": "$\\int\\frac{2x+1}{\\sqrt{x}}\\,dx$ (split and simplify).",
                    "body_he": "$\\int(2x+1)/\\sqrt{x}\\,dx$.",
                    "solution_en": "Rewrite: $\\frac{2x+1}{\\sqrt{x}}=2x^{1/2}+x^{-1/2}$. Integrate: $\\frac{4x^{3/2}}{3}+2\\sqrt{x}+C$.",
                    "solution_he": "כתיבה: $2x^{1/2}+x^{-1/2}$. אינטגרל: $\\frac{4x^{3/2}}{3}+2\\sqrt{x}+C$.",
                },
                {
                    "id": "e11",
                    "difficulty": "hard",
                    "body_en": "Show that $\\int_a^b f(x)\\,dx = -\\int_b^a f(x)\\,dx$.",
                    "body_he": "הראו ש-$\\int_a^b f=-\\int_b^a f$.",
                    "solution_en": "By FTC: $\\int_a^b f=F(b)-F(a)$. Also $-\\int_b^a f=-(F(a)-F(b))=F(b)-F(a)$. Equal. ✓",
                    "solution_he": "לפי FTC: $\\int_a^b f=F(b)-F(a)$. $-\\int_b^a f=-(F(a)-F(b))=F(b)-F(a)$. שווים. ✓",
                },
                {
                    "id": "e12",
                    "difficulty": "hard",
                    "body_en": "Find the total area (not signed) between $y=x^2-1$ and the $x$-axis on $[-2,2]$.",
                    "body_he": "שטח כולל (לא עם סימן) בין $y=x^2-1$ לציר $x$ על $[-2,2]$.",
                    "solution_en": "Zeros at $x=\\pm1$. Split: positive on $[-2,-1]\\cup[1,2]$, negative on $[-1,1]$. Total area $=\\frac{8}{3}$ (vs. net signed $=0$).",
                    "solution_he": "אפסים ב-$x=\\pm1$. פיצול: חיובי ב-$[-2,-1]\\cup[1,2]$, שלילי ב-$[-1,1]$. שטח כולל $=\\frac{8}{3}$ (נטו עם סימן $=0$).",
                },
                {
                    "id": "e13",
                    "difficulty": "hard",
                    "body_en": "The velocity of a particle is $v(t)=t^2-4$ m/s. Find the displacement from $t=0$ to $t=3$ and the total distance traveled.",
                    "body_he": "$v(t)=t^2-4$ מ\"ש. מצאו העתק ומרחק כולל בין $t=0$ ל-$t=3$.",
                    "solution_en": "Displacement: $\\int_0^3(t^2-4)\\,dt=[t^3/3-4t]_0^3=9-12=-3$ m. Zero at $t=2$. Total distance $=|\\int_0^2|+|\\int_2^3|=16/3+1/3=17/3$ m.",
                    "solution_he": "העתק: $\\int_0^3=-3$ מ'. אפס ב-$t=2$. מרחק כולל: $16/3+1/3=17/3$ מ'.",
                },
            ],
        },
        {
            "kind": "pitfall",
            "title_en": "Common Pitfalls",
            "title_he": "מלכודות נפוצות",
            "body_en_md": """1. **Forgetting $+C$ on indefinite integrals.** Every antiderivative family needs the constant. Examiners deduct even when the algebra is otherwise perfect.

2. **Applying the power rule when $n=-1$.** $\\int x^{-1}\\,dx=\\ln|x|+C$, NOT $\\frac{x^0}{0}$ (which is undefined). When you see $\\frac{1}{x}$, reach for $\\ln|x|$ immediately.

3. **Confusing signed area with total area.** $\\int_a^b f(x)\\,dx$ gives **net signed** area. Regions below the axis contribute negative values. For total (unsigned) area, split at zeros and integrate absolute values.

4. **Sign errors on trig integrals.** $\\int\\sin x=-\\cos x+C$ — the minus is easy to drop. Differentiate your answer to catch this instantly.

5. **Skipping verification.** Ten seconds of differentiation after every indefinite integral prevents most lost points.

**Fix habit:** After each problem, ask \"which pitfall almost got me?\" — that metacognition is worth exam points.""",
            "body_he_md": """1. **שכחת $+C$ באינטגרל לא מסויים.** כל משפחת נגזרות הפוכות דורשת קבוע. בודקים מורידים נקודות גם כשהאלגברה נכונה.

2. **כלל חזקה כש-$n=-1$.** $\\int x^{-1}=\\ln|x|+C$, **לא** $\\frac{x^0}{0}$ (לא מוגדר). כשמופיע $\\frac{1}{x}$ — $\\ln|x|$ מיד.

3. **בלבול שטח עם סימן מול שטח כולל.** $\\int_a^b f$ נותן שטח **נטו עם סימן**. אזורים מתחת לציר תורמים שלילי. לשטח כולל — פצלו באפסים ואינטגרל של ערך מוחלט.

4. **שגיאות סימן בטריגו.** $\\int\\sin x=-\\cos x+C$ — קל לשכוח מינוס. גזירה תופסת מיד.

5. **דילוג על אימות.** 10 שניות גזירה אחרי כל אינטגרל לא מסויים מונעות רוב האיבוד.

**הרגל תיקון:** אחרי כל תרגיל, שאלו \"איזו מלכודת כמעט תפסה אותי?\" — המטא-קוגניציה שווה נקודות.""",
        },
        {
            "id": "why_matters",
            "kind": "why_matters",
            "title_en": "Why it matters",
            "title_he": "למה זה חשוב",
            "body_en_md": """Integration is the **second pillar of calculus** — without it, derivatives alone cannot answer \"how much total change accumulated?\" Every area, volume, work, and displacement problem in physics and engineering eventually reduces to an integral.

**You will use this to unlock on A Step Forward:**
- `concept:work_energy` **Work & Energy** — $W=\\int F\\,dx$ generalizes force times distance.
- `concept:kinematics_1d` **Kinematics in 1D** — $x(t)=\\int v\\,dt$ recovers position from velocity.
- `concept:integrals_techniques` **Integration Techniques** — substitution, parts, partial fractions build on these rules.

**Builds on:**
- `concept:derivatives_intro` **Derivatives — Introduction & Basic Rules**

**Why exams care:** Bagrut 5-unit and Calc 1 courses reward *transfer* — recognizing which rule applies from the problem structure alone. Master the table here and you have the vocabulary for every technique chapter that follows.""",
            "body_he_md": """אינטגרציה היא **עמוד השדרה השני של החשבון** — בלי אותה, נגזרות לבד לא עונות על \"כמה שינוי מצטבר?\" כל שטח, נפח, עבודה והעתק בפיזיקה והנדסה מצטמצם לאינטגרל.

**תשתמשו בזה להתקדם ב-A Step Forward:**
- `concept:work_energy` **עבודה ואנרגיה** — $W=\\int F\\,dx$ מכליל כוח כפול מרחק.
- `concept:kinematics_1d` **קינמטיקה בממד אחד** — $x(t)=\\int v\\,dt$ משחזר מיקום ממהירות.
- `concept:integrals_techniques` **שיטות אינטגרציה** — הצבה, חלקים, שברים חלקיים נשענים על הכללים כאן.

**מבוסס על:**
- `concept:derivatives_intro` **נגזרות — מבוא וכללים בסיסיים**

**למה בחינות אכפת:** בבגרות 5 יחידות ובחדו״א 1 מעריכים *העברה* — זיהוי הכלל הנכון ממבנה השאלה. שליטה בטבלה כאן = אוצר מילים לכל פרק הטכניקות שאחרי.""",
        },
        {
            "kind": "before_exam",
            "title_en": "Before the Exam",
            "title_he": "לפני הבחינה",
            "body_en_md": """**Quick reference:**
$$\\int x^n\\,dx = \\frac{x^{n+1}}{n+1}+C \\quad (n\\ne-1).$$
$$\\int \\frac{1}{x}\\,dx = \\ln|x|+C.$$
$$\\int e^x\\,dx = e^x+C. \\quad \\int e^{ax}\\,dx = \\frac{e^{ax}}{a}+C.$$

**FTC:** $\\int_a^b f(x)\\,dx = F(b)-F(a)$ where $F'=f$.

**Checklist before submitting:**
- [ ] Power rule: divide by the **new** exponent, not the old one.
- [ ] $+C$ on every indefinite integral answer line.
- [ ] Differentiate once to verify indefinite answers.
- [ ] For definite integrals: bracket notation $[F(x)]_a^b$ written clearly.
- [ ] Distinguish displacement (signed integral) from total distance (split at zeros).

**Last review:** Recite the trig table ($\\sin\\to-\\cos$, $\\cos\\to\\sin$), then solve one checkpoint and one initial-value problem without notes.""",
            "body_he_md": """**עזר מהיר:**
$$\\int x^n=\\frac{x^{n+1}}{n+1}+C \\quad (n\\ne-1).$$
$$\\int \\frac{1}{x}=\\ln|x|+C.$$
$$\\int e^x=e^x+C. \\quad \\int e^{ax}=\\frac{e^{ax}}{a}+C.$$

**FTC:** $\\int_a^b f=F(b)-F(a)$ כאשר $F'=f$.

**רשימה לפני הגשה:**
- [ ] כלל חזקה: חלקו בחזקה **החדשה**, לא הישנה.
- [ ] $+C$ בכל שורת תשובה לא מסוימת.
- [ ] גזירה פעם אחת לאימות.
- [ ] באינטגרל מסוים: סימון $[F(x)]_a^b$ ברור.
- [ ] הבחנה בין העתק (עם סימן) למרחק כולל (פיצול באפסים).

**חזרה אחרונה:** חזרו טבלת טריגו ($\\sin\\to-\\cos$, $\\cos\\to\\sin$), ופתרו checkpoint ובעיית ערך התחלתי בלי רשימות.""",
        },
        {
            "kind": "summary",
            "title_en": "Take-away",
            "title_he": "סיכום",
            "body_en_md": """- Integration reverses differentiation: given $f'$, find $f$.
- $\\int f(x)\\,dx = F(x)+C$ where $F'(x)=f(x)$; the $+C$ captures all vertical shifts.
- **FTC Part 2:** $\\int_a^b f(x)\\,dx = F(b)-F(a)$ connects antiderivatives to signed net area.
- **Core rules:** power ($n\\ne-1$), $\\ln|x|$ for $1/x$, $e^x$ unchanged, $\\sin\\to-\\cos$, $\\cos\\to\\sin$.
- **Always verify** by differentiating your antiderivative.

**Takeaway:** Read the integrand first — polynomial, reciprocal, exponential, or trig? The rule follows from the structure, not from habit.""",
            "body_he_md": """- אינטגרציה הופכת גזירה: בהינתן $f'$, מצא $f$.
- $\\int f=F+C$ כאשר $F'=f$; $+C$ תופס את כל ההזזות האנכיות.
- **FTC חלק 2:** $\\int_a^b f=F(b)-F(a)$ מחבר נגזרות הפוכות לשטח נטו.
- **כללים מרכזיים:** חזקה ($n\\ne-1$), $\\ln|x|$ ל-$1/x$, $e^x$ ללא שינוי, $\\sin\\to-\\cos$, $\\cos\\to\\sin$.
- **תמיד אמתו** בגזירת הנגזרת ההפוכה.

**מסקנה:** קראו קודם את הפונקציה — פולינום, הדדי, מעריכי או טריגו? הכלל נגזר מהמבנה, לא מהרגל.""",
        },
    ],
    "agent_hints": {
        "key_insights": [
            "Integration is the reverse of differentiation — check by differentiating your answer.",
            "Power rule: add 1 to exponent, divide by new exponent. Exception: n=-1 gives ln|x|.",
            "FTC: definite integral = antiderivative at upper limit minus lower limit.",
            "Signed area vs total area: for total area, split at zeros.",
        ],
        "common_misconceptions": [
            {
                "wrong": "Applying power rule to 1/x giving x^0/0",
                "correction": "For n=-1: integral of 1/x = ln|x|+C, not x^0/0 (which is undefined).",
                "detect_phrase_en": "integral 1/x power rule",
                "detect_phrase_he": "אינטגרל 1/x כלל חזקה",
            }
        ],
        "skill_atoms_unlocked": [
            "antiderivative",
            "power_rule_integration",
            "fundamental_theorem",
            "integration_trig",
            "integration_exp",
        ],
        "tutor_pacing_hint": "Start with polynomial integrals. Then FTC with definite integrals. Then initial value problems.",
        "next_recommended": ["integrals_techniques", "definite_integrals"],
    },
    "questions": [],
    "est_minutes": 40,
    "author": "cursor-claude-2026",
    "version": 1,
    "level_focus": None,
    "skill_atom_bank": None,
}

# Question explanations (80-150 words each)
q1_en, q1_he = fmt_expl(
    "The power rule for integration adds 1 to the exponent and divides by the new exponent: $\\int x^4\\,dx = x^5/5+C$. Option A matches exactly.",
    "Indefinite integrals of polynomials always use the reverse power rule — increase exponent, divide by it, add $+C$ once at the end.",
    "Option B ($4x^3+C$) is the **derivative** of $x^4$, not its antiderivative — a classic direction confusion. Option C forgot to divide by 5; Option D multiplied by 5 instead.",
    "On MCQ items, differentiate each option mentally: only the correct one returns $x^4$ when differentiated.",
    "כלל החזקה: $\\int x^4\\,dx = x^5/5+C$. אפשרות א' תואמת בדיוק.",
    "אינטגרל לא מסויים של פולינום: העלאת חזקה, חלוקה בה, $+C$ פעם בסוף.",
    "אפשרות ב' ($4x^3+C$) היא **נגזרת** של $x^4$, לא נגזרת הפוכה — בלבול כיוון קלאסי. ג' שכח חלוקה ב-5; ד' כפל ב-5.",
    "ברב-ברירה, גזרו כל אפשרות: רק הנכונה מחזירה $x^4$.",
)

q2_en, q2_he = fmt_expl(
    "Rewrite $\\sqrt{x}=x^{1/2}$ and $1/x^2=x^{-2}$. Antiderivative: $2x^{3/2}/3+1/x$. FTC from 1 to 4: $(16/3+1/4)-(2/3+1)=47/12$.",
    "Definite integrals with mixed radicals and negative powers require rewriting as $x^n$ first, then FTC — no $+C$ needed because it cancels.",
    "Sign error on $\\int x^{-2}$: it gives $-1/x$, not $+1/x$. Arithmetic slips when combining fractions at the bounds are common.",
    "Write $[F(x)]_1^4$ explicitly on your paper — graders award partial credit for correct antiderivative even if final arithmetic fails.",
    "כתיבה $\\sqrt{x}=x^{1/2}$, $1/x^2=x^{-2}$. נגזרת הפוכה: $2x^{3/2}/3+1/x$. FTC מ-1 ל-4: $(16/3+1/4)-(2/3+1)=47/12$.",
    "אינטגרל מסויים עם שורשים וחזקות שליליות — כתיבה כ-$x^n$ קודם, אז FTC; $+C$ מתבטל.",
    "שגיאת סימן ב-$\\int x^{-2}$: $-1/x$, לא $+1/x$. טעויות חיבור שברים בגבולות נפוצות.",
    "כתבו $[F(x)]_1^4$ במפורש — ניקוד חלקי לנגזרת הפוכה נכונה גם אם החישוב הסופי נכשל.",
)

q3_en, q3_he = fmt_expl(
    "Apply power rule term by term: $\\int 4x^3=x^4$, $\\int(-3x)=-\\frac{3x^2}{2}$, $\\int 1=x$. Combine: $x^4-\\frac{3x^2}{2}+x+C$.",
    "Linearity lets you integrate polynomials one term at a time — treat constants and coefficients separately before adding $+C$ once.",
    "Forgetting $+C$, or dividing $4x^3$ incorrectly (getting $x^3$ instead of $x^4$), are the two most common slips.",
    "Differentiate your answer in the margin — if you get $4x^3-3x+1$ back, the integral is correct regardless of how you formatted it.",
    "כלל חזקה איבר-איבר: $\\int 4x^3=x^4$, $\\int(-3x)=-\\frac{3x^2}{2}$, $\\int 1=x$. סיכום: $x^4-\\frac{3x^2}{2}+x+C$.",
    "ליניאריות מאפשרת אינטגרל פולינום איבר-איבר — קבועים ומקדמים בנפרד, $+C$ פעם בסוף.",
    "שכחת $+C$, או חלוקה שגויה של $4x^3$ (קבלת $x^3$ במקום $x^4$) — שתי הטעויות הנפוצות.",
    "גזרו את התשובה בשוליים — אם חוזר $4x^3-3x+1$, האינטגרל נכון.",
)

q4_en, q4_he = fmt_expl(
    "Standard antiderivatives: $\\int\\sin x=-\\cos x$ and $\\int e^x=e^x$. Sum with linearity: $-\\cos x+e^x+C$.",
    "Mixed trig-exponential integrands are handled term by term — no substitution needed at this level. Match each term to the table.",
    "Sign error on sine ($+\\cos x$ instead of $-\\cos x$) is the #1 trig integration mistake. Differentiate to catch it instantly.",
    "When sine and exponential appear together, write each antiderivative on a separate line before combining — prevents sign mix-ups.",
    "נגזרות הפוכות סטנדרטיות: $\\int\\sin x=-\\cos x$, $\\int e^x=e^x$. סכום: $-\\cos x+e^x+C$.",
    "פונקציה תחתית מעורבת טריגו-מעריכית — איבר-איבר, בלי הצבה ברמה זו. התאמה לטבלה.",
    "שגיאת סימן בסינוס ($+\\cos x$ במקום $-\\cos x$) — טעות #1. גזירה תופסת מיד.",
    "כשסינוס ומעריכי יחד — כתבו כל נגזרת הפוכה בשורה נפרדת לפני חיבור.",
)

q5_en, q5_he = fmt_expl(
    "Antiderivative of $x^3$ is $x^4/4$. FTC: $[x^4/4]_0^2 = 16/4 - 0 = 4$.",
    "Definite integrals of pure power functions are the fastest FTC drills — find $F$, plug in bounds, subtract.",
    "Using $x^3$ as the antiderivative (differentiating instead of integrating), or evaluating $F(0)$ incorrectly, gives wrong answers.",
    "For $\\int_0^2 x^3\\,dx$, sanity check: the function is positive on $[0,2]$, so the result must be positive — $4>0$ ✓.",
    "נגזרת הפוכה של $x^3$: $x^4/4$. FTC: $[x^4/4]_0^2=16/4=4$.",
    "אינטגרל מסויים של חזקה טהורה — FTC מהיר: מצא $F$, הצב גבולות, חסר.",
    "שימוש ב-$x^3$ כנגזרת הפוכה (גזירה במקום אינטגרל), או חישוב שגוי של $F(0)$.",
    "בדיקת שפיות: הפונקציה חיובית ב-$[0,2]$, התוצאה חייבת להיות חיובית — $4>0$ ✓.",
)

q6_en, q6_he = fmt_expl(
    "Rewrite $x^{-3}+x^{1/3}$. Power rule: $\\int x^{-3}=-x^{-2}/2$, $\\int x^{1/3}=\\frac{3x^{4/3}}{4}$. Answer: $-\\frac{1}{2x^2}+\\frac{3x^{4/3}}{4}+C$.",
    "Fractions and radicals must become $x^n$ before applying the power rule — identify the exponent, then add 1 and divide.",
    "Applying power rule to $x^{-3}$ without dividing by the new exponent $-2$, or mishandling the cube root ($x^{1/3}\\to x^{4/3}/4$, not $x^{4/3}/3$).",
    "When exponents are fractional, write the new exponent explicitly: $1/3+1=4/3$, divide by $4/3$ which equals multiply by $3/4$.",
    "כתיבה $x^{-3}+x^{1/3}$. כלל חזקה: $\\int x^{-3}=-x^{-2}/2$, $\\int x^{1/3}=\\frac{3x^{4/3}}{4}$. תשובה: $-\\frac{1}{2x^2}+\\frac{3x^{4/3}}{4}+C$.",
    "שברים ושורשים חייבים להיות $x^n$ לפני כלל החזקה — זיהוי חזקה, הוספת 1, חלוקה.",
    "כלל חזקה על $x^{-3}$ בלי חלוקה ב-$-2$, או טיפול שגוי בשורש ($x^{1/3}\\to x^{4/3}/4$, לא $/3$).",
    "בחזקות שבריות, כתבו במפורש: $1/3+1=4/3$, חלקו ב-$4/3$ = כפלו ב-$3/4$.",
)

q7_en, q7_he = fmt_expl(
    "Split $\\frac{x^2+x-1}{x^2}=1+\\frac{1}{x}-x^{-2}$. Integrate: $x+\\ln|x|+\\frac{1}{x}+C$. Note $\\int x^{-2}=-x^{-1}=1/x$.",
    "When the numerator and denominator share a power, **divide term by term** before integrating — never integrate a complex fraction directly at this level.",
    "Using power rule on $1/x$ (getting $x^0/0$), or sign error on $\\int x^{-2}$ (getting $-1/x$ instead of $+1/x$).",
    "After splitting, label each term's rule: constant $\\to x$, reciprocal $\\to \\ln|x|$, negative power $\\to power rule. This prevents mixing rules.",
    "פיצול $\\frac{x^2+x-1}{x^2}=1+\\frac{1}{x}-x^{-2}$. אינטגרל: $x+\\ln|x|+\\frac{1}{x}+C$. שימו לב $\\int x^{-2}=-x^{-1}=1/x$.",
    "כשמונה ומכנה חולקים חזקה — **חלוקה איבר-איבר** לפני אינטגרל, לא אינטגרל שבר ישיר.",
    "כלל חזקה על $1/x$ ($x^0/0$), או סימן שגוי ב-$\\int x^{-2}$ ($-1/x$ במקום $+1/x$).",
    "אחרי פיצול, סמנו כלל לכל איבר: קבוע $\\to x$, הדדי $\\to \\ln|x|$, חזקה שלילית $\\to כלל חזקה.",
)

q8_en, q8_he = fmt_expl(
    "Integrate: $f(x)=3e^x+2\\cos x+C$. Use $f(0)=1$: $3(1)+2(1)+C=1$, so $5+C=1$ and $C=-4$. Result: $f(x)=3e^x+2\\cos x-4$.",
    "Initial-value problems: integrate first, **then** plug in the condition to solve for $C$. The condition applies to the function, not the derivative.",
    "Sign error on $\\int(-2\\sin x)$ — it gives $+2\\cos x$, not $-2\\cos x$. Forgetting to use $f(0)=1$ after finding the family.",
    "Always verify both conditions at the end: $f'(0)$ should match the derivative condition and $f(0)$ the function condition — catches algebra slips.",
    "אינטגרל: $f(x)=3e^x+2\\cos x+C$. מ-$f(0)=1$: $3+2+C=1$, $C=-4$. תוצאה: $f(x)=3e^x+2\\cos x-4$.",
    "בעיות ערך התחלתי: אינטגרל קודם, **אז** הצבת תנאי ל-$C$. התנאי על הפונקציה, לא על הנגזרת.",
    "סימן שגוי ב-$\\int(-2\\sin x)$ — $+2\\cos x$, לא $-2\\cos x$. שכחת $f(0)=1$ אחרי מציאת המשפחה.",
    "אמתו שני תנאים בסוף: $f'(0)$ ו-$f(0)$ — תופס טעויות אלגברה.",
)

explanations = [q1_en, q1_he, q2_en, q2_he, q3_en, q3_he, q4_en, q4_he,
                q5_en, q5_he, q6_en, q6_he, q7_en, q7_he, q8_en, q8_he]

lesson["questions"] = [
    {
        "ord": 1,
        "kind": "mcq",
        "difficulty": "easy",
        "stem_en": "$\\int x^4\\,dx =$",
        "stem_he": "$\\int x^4\\,dx=$",
        "options_en": ["$x^5/5+C$", "$4x^3+C$", "$x^5+C$", "$5x^5+C$"],
        "options_he": ["$x^5/5+C$", "$4x^3+C$", "$x^5+C$", "$5x^5+C$"],
        "correct_index": 0,
        "explanation_en": q1_en,
        "explanation_he": q1_he,
        "skill_atoms": ["power_rule_integration"],
    },
    {
        "ord": 2,
        "kind": "open",
        "difficulty": "medium",
        "stem_en": "Evaluate $\\int_1^4\\left(\\sqrt{x}-\\frac{1}{x^2}\\right)dx$.",
        "stem_he": "חשבו $\\int_1^4(\\sqrt{x}-1/x^2)\\,dx$.",
        "rubric_en": "$[2x^{3/2}/3+1/x]_1^4=(16/3+1/4)-(2/3+1)=47/12$.",
        "rubric_he": "$47/12$.",
        "explanation_en": q2_en,
        "explanation_he": q2_he,
        "skill_atoms": ["power_rule_integration", "fundamental_theorem"],
    },
    {
        "ord": 3,
        "kind": "short_answer",
        "difficulty": "easy",
        "stem_en": "$\\int(4x^3-3x+1)\\,dx$",
        "stem_he": "$\\int(4x^3-3x+1)\\,dx$",
        "answer_payload": {
            "acceptable_answers": [
                "x^4-\\frac{3x^2}{2}+x+C",
                "$x^4-\\frac{3x^2}{2}+x+C$",
                "x^4 - 3x^2/2 + x + C",
            ],
            "case_sensitive": False,
        },
        "explanation_en": q3_en,
        "explanation_he": q3_he,
        "skill_atoms": ["antiderivative", "power_rule_integration"],
    },
    {
        "ord": 4,
        "kind": "short_answer",
        "difficulty": "easy",
        "stem_en": "$\\int(\\sin x+e^x)\\,dx$",
        "stem_he": "$\\int(\\sin x+e^x)\\,dx$",
        "answer_payload": {
            "acceptable_answers": [
                "-\\cos x+e^x+C",
                "$-\\cos x+e^x+C$",
                "e^x - cos x + C",
            ],
            "case_sensitive": False,
        },
        "explanation_en": q4_en,
        "explanation_he": q4_he,
        "skill_atoms": ["antiderivative", "integration_trig", "integration_exp"],
    },
    {
        "ord": 5,
        "kind": "short_answer",
        "difficulty": "easy",
        "stem_en": "Evaluate $\\int_0^2 x^3\\,dx$.",
        "stem_he": "חשבו $\\int_0^2 x^3\\,dx$.",
        "answer_payload": {
            "acceptable_answers": ["4", "$4$", "16/4"],
            "case_sensitive": False,
        },
        "explanation_en": q5_en,
        "explanation_he": q5_he,
        "skill_atoms": ["power_rule_integration", "fundamental_theorem"],
    },
    {
        "ord": 6,
        "kind": "short_answer",
        "difficulty": "easy",
        "stem_en": "$\\int\\left(\\frac{1}{x^3}+\\sqrt[3]{x}\\right)dx$",
        "stem_he": "$\\int(x^{-3}+x^{1/3})\\,dx$",
        "answer_payload": {
            "acceptable_answers": [
                "-x^{-2}/2+\\frac{3x^{4/3}}{4}+C",
                "-1/(2x^2)+\\frac{3}{4}x^{4/3}+C",
                "-1/2x^2 + 3x^(4/3)/4 + C",
            ],
            "case_sensitive": False,
        },
        "explanation_en": q6_en,
        "explanation_he": q6_he,
        "skill_atoms": ["antiderivative", "power_rule_integration"],
    },
    {
        "ord": 7,
        "kind": "short_answer",
        "difficulty": "medium",
        "stem_en": "$\\int\\frac{x^2+x-1}{x^2}\\,dx$ (split the fraction first).",
        "stem_he": "$\\int(x^2+x-1)/x^2\\,dx$ (פצלו ראשה).",
        "answer_payload": {
            "acceptable_answers": [
                "x+\\ln|x|+1/x+C",
                "x + ln|x| + 1/x + C",
                "$x+\\ln|x|+\\frac{1}{x}+C$",
            ],
            "case_sensitive": False,
        },
        "explanation_en": q7_en,
        "explanation_he": q7_he,
        "skill_atoms": ["antiderivative", "power_rule_integration"],
    },
    {
        "ord": 8,
        "kind": "short_answer",
        "difficulty": "medium",
        "stem_en": "Find $f(x)$ if $f'(x)=3e^x-2\\sin x$ and $f(0)=1$.",
        "stem_he": "מצאו $f$ אם $f'=3e^x-2\\sin x$, $f(0)=1$.",
        "answer_payload": {
            "acceptable_answers": [
                "3e^x+2\\cos x-4",
                "3e^x + 2cos x - 4",
                "$3e^x+2\\cos x-4$",
            ],
            "case_sensitive": False,
        },
        "explanation_en": q8_en,
        "explanation_he": q8_he,
        "skill_atoms": ["antiderivative", "integration_trig", "integration_exp"],
    },
]

# Fix typos in Hebrew method_guide title
for sec in lesson["sections"]:
    if sec.get("kind") == "method_guide":
        sec["title_he"] = "מדריך שיטה — אינטגרציה"
        break

TARGET.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {TARGET}")

# Validate JSON parse
json.loads(TARGET.read_text(encoding="utf-8"))
print("JSON parse OK")

# Run seed dry-run
result = subprocess.run(
    ["node", "scripts/seed-lessons.mjs", "--dry-run"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    raise SystemExit(result.returncode)
print("seed-lessons --dry-run passed")
