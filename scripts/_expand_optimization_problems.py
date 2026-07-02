#!/usr/bin/env python3
"""Expand optimization_problems.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/optimization_problems.json"

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


INTRO_EN = """Optimization means finding the **best** value of a quantity — maximum profit, minimum cost, shortest time, largest area. Calculus turns these questions into a repeatable algorithm: model the situation as a function, find where its derivative vanishes, and verify whether that critical point is a maximum or minimum.

**Two problem families dominate university Calc 1:**
1. **Pure calculus** — extrema of a given $f(x)$ on an interval or the whole line, using the first or second derivative test.
2. **Applied word problems** — translate geometry, physics, or economics into a single-variable objective function using a constraint equation.

Real applications appear everywhere: engineers minimize material while meeting strength specs; economists maximize revenue under price constraints; physicists use Fermat's principle (light takes the path of least time). On exams, applied problems often carry more points because setup — not just differentiation — is graded.

This lesson builds on `concept:derivatives_applications` and feeds into `concept:integrals_applications` (area/volume optimization) and `concept:uni_derivative_applications`. The five-step framework here is the template every later optimization topic reuses."""

INTRO_HE = """אופטימיזציה פירושה מציאת הערך **הטוב ביותר** של גודל — רווח מרבי, עלות מינימלית, זמן קצר ביותר, שטח גדול ביותר. חשבון דיפרנציאלי הופך שאלות אלה לאלגוריתם חוזר: ממדלים את המצב כפונקציה, מוצאים היכן הנגזרת מתאפסת, ומוודאים אם נקודת הקריטיות היא מקסימום או מינימום.

**שני משפחות בעיות שולטות בחשבון אוניברסיטאי 1:**
1. **חשבון טהור** — קיצונים של $f(x)$ נתונה על קטע או על כל הישר, באמצעות מבחן הנגזרת הראשונה או השנייה.
2. **בעיות מילוליות שימושיות** — תרגום גיאומטריה, פיזיקה או כלכלה לפונקציית מטרה במשתנה יחיד בעזרת משוואת אילוץ.

יישומים אמיתיים בכל מקום: מהנדסים ממזערים חומר תוך עמידה בדרישות חוזק; כלכלנים ממקסמים הכנסה תחת אילוצי מחיר; פיזיקאים משתמשים בעקרון פרמה (אור בוחר מסלול זמן מינימלי). בבחינות, בעיות שימושיות לרוב שוות יותר נקודות כי גם ההכנה — לא רק הגזירה — נבדקת.

שיעור זה נשען על `concept:derivatives_applications` ומזין את `concept:integrals_applications` (אופטימיזציה של שטח/נפח) ו-`concept:uni_derivative_applications`. מסגרת חמשת הצעדים כאן היא התבנית שכל נושא אופטימיזציה מאוחר יותר חוזר עליה."""

DEF_EN = """**Critical point:** $x=c$ is a critical point of $f$ if $f'(c)=0$ or $f'(c)$ does not exist. Critical points are *candidates* for local extrema — they are not automatically maxima or minima.

**First Derivative Test:** Examine the sign of $f'$ on each side of $c$.
- If $f'$ changes from $+$ to $-$ at $c$ $\\Rightarrow$ $f$ has a **local maximum** at $c$.
- If $f'$ changes from $-$ to $+$ at $c$ $\\Rightarrow$ $f$ has a **local minimum** at $c$.
- If $f'$ does not change sign $\\Rightarrow$ **neither** (often an inflection point).

**Second Derivative Test:** When $f'(c)=0$ and $f''$ is easy to compute:
- $f''(c)>0$ $\\Rightarrow$ **local minimum** (concave up, holds water).
- $f''(c)<0$ $\\Rightarrow$ **local maximum** (concave down).
- $f''(c)=0$ $\\Rightarrow$ **inconclusive** — fall back to the first derivative test.

**Extreme Value Theorem (EVT):** If $f$ is continuous on the closed interval $[a,b]$, then $f$ attains both an absolute maximum and an absolute minimum on $[a,b]$. To find them, evaluate $f$ at every critical point in $(a,b)$ **and** at the endpoints $a$ and $b$, then compare.

**Objective function** (applied problems): the quantity $Q(x)$ you want to maximize or minimize, written in terms of a single variable after using the constraint to eliminate others."""

DEF_HE = """**נקודה קריטית:** $x=c$ קריטית עבור $f$ אם $f'(c)=0$ או $f'(c)$ לא קיימת. נקודות קריטיות הן *מועמדות* לקיצון מקומי — לא בהכרח מקסימום או מינימום.

**מבחן הנגזרת הראשונה:** בדקו את סימן $f'$ משני צדי $c$.
- אם $f'$ עובר מ-$+$ ל-$-$ ב-$c$ $\\Rightarrow$ **מקסימום מקומי**.
- אם $f'$ עובר מ-$-$ ל-$+$ ב-$c$ $\\Rightarrow$ **מינימום מקומי**.
- אם $f'$ לא משנה סימן $\\Rightarrow$ **לא קיצון** (לעיתים נקודת פיתול).

**מבחן הנגזרת השנייה:** כש-$f'(c)=0$ ו-$f''$ נוחה לחישוב:
- $f''(c)>0$ $\\Rightarrow$ **מינימום מקומי** (קעורה כלפי מעלה).
- $f''(c)<0$ $\\Rightarrow$ **מקסימום מקומי** (קעורה כלפי מטה).
- $f''(c)=0$ $\\Rightarrow$ **אין מסקנה** — חזרו למבחן הראשון.

**משפט הערכים הקיצוניים (EVT):** אם $f$ רציפה על $[a,b]$, אז $f$ מגיעה למקסימום ולמינימום מוחלטים על $[a,b]$. למציאתם, חשבו $f$ בכל נקודה קריטית ב-$(a,b)$ **וגם** בקצוות $a,b$, והשוו.

**פונקציית מטרה** (בעיות שימושיות): הגודל $Q(x)$ שרוצים למקסם או למזער, כתוב במשתנה יחיד לאחר שימוש באילוץ לאלימינציה."""

THEORY_EN = """**Standard 5-step framework for applied optimization:**

1. **Draw and label:** Sketch the situation; name every variable with units.
2. **Objective function:** Write what you maximize or minimize ($A$, $V$, $C$, $R$, etc.) in terms of the variables.
3. **Constraint equation:** Capture the given relationship — perimeter fixed, volume fixed, wire length fixed, etc.
4. **Reduce to one variable:** Solve the constraint for one variable and substitute into the objective.
5. **Optimize and answer:** Find critical points in the **physical domain**, classify max/min, state the answer with units and context.

**Choosing the test:**
- **Second derivative test** — fastest when $f''$ is a simple constant or easy polynomial.
- **First derivative test** — always valid; essential when $f''(c)=0$ or $f''$ is messy.
- **Closed interval comparison** — mandatory on $[a,b]$: list critical points plus endpoints.

**Domain discipline:** In applied problems, variables must satisfy physical constraints ($x>0$, $2x<L$, etc.). A critical point outside the domain is discarded even if the algebra is correct.

**Closed vs. open intervals:** On a closed interval, absolute extrema may occur at endpoints even when interior critical points exist. Never stop after finding $f'(x)=0$ without comparing all candidate values.

**Sign of the answer:** Revenue and area problems usually seek maxima ($f''<0$); cost and distance problems usually seek minima ($f''>0$). If the second derivative sign contradicts the question wording, re-check the setup."""

THEORY_HE = """**מסגרת חמשת הצעדים לבעיות אופטימיזציה שימושיות:**

1. **ציירו וסמנו:** שרטטו את המצב; קראו שם לכל משתנה עם יחידות.
2. **פונקציית מטרה:** כתבו מה ממקסמים או ממנימים ($A$, $V$, $C$, $R$ וכו') לפי המשתנים.
3. **משוואת אילוץ:** תפסו את הקשר הנתון — היקף קבוע, נפח קבוע, אורך חוט קבוע וכו'.
4. **צמצום למשתנה אחד:** פתרו את האילוץ למשתנה אחד והציבו בפונקציית המטרה.
5. **אופטימיזציה ותשובה:** מצאו נקודות קריטיות ב**תחום הפיזי**, סווגו מקס/מין, ציינו תשובה עם יחידות והקשר.

**בחירת המבחן:**
- **מבחן נגזרת שנייה** — הכי מהיר כש-$f''$ קבוע פשוט או פולינום נוח.
- **מבחן נגזרת ראשונה** — תמיד תקף; חיוני כש-$f''(c)=0$ או $f''$ מסורבל.
- **השוואה על קטע סגור** — חובה על $[a,b]$: רשימת קריטיות + קצוות.

**משמעת תחום:** בבעיות שימושיות, משתנים חייבים לקיים אילוצים פיזיים ($x>0$, $2x<L$). נקודה קריטית מחוץ לתחום נזרקת גם אם האלגברה נכונה.

**קטע סגור מול פתוח:** על קטע סגור, קיצון מוחלט עשוי להיות בקצוות גם כשיש קריטיות פנימיות. לעולם אל תעצרו אחרי $f'(x)=0$ בלי להשוות כל הערכים.

**סימן התשובה:** בעיות הכנסה ושטח בדרך כלל מחפשות מקסימום ($f''<0$); עלות ומרחק — מינימום ($f''>0$). אם סימן $f''$ סותר את ניסוח השאלה, בדקו מחדש את ההכנה."""

WE1_EN = """**Given:** $f(x)=x^2-4x+3$ on the closed interval $[0,5]$. Find the absolute maximum and minimum.

**Strategy:** On a closed interval, EVT guarantees extrema exist. Candidates are interior critical points ($f'=0$) and endpoints.

### Move 1: Find critical points
$$f'(x)=2x-4=0 \\implies x=2$$
Check $x=2 \\in (0,5)$ — yes, it is an interior critical point.

### Move 2: Build a candidate table
| $x$ | $f(x)$ |
|-----|--------|
| $0$ (endpoint) | $0-0+3=3$ |
| $2$ (critical) | $4-8+3=-1$ |
| $5$ (endpoint) | $25-20+3=8$ |

### Move 3: Compare and conclude
- **Absolute maximum:** $f(5)=8$ at $x=5$ (endpoint — not at the critical point!).
- **Absolute minimum:** $f(2)=-1$ at $x=2$.

**Answer:** Maximum value $8$ at $x=5$; minimum value $-1$ at $x=2$. ✓

**Exam note:** Students often report $x=2$ as the maximum because it is the only critical point. Always evaluate endpoints on closed intervals.

**Verify with calculus:** $f''(x)=2>0$ confirms $x=2$ is a local minimum, not a maximum — the absolute maximum occurs at the right endpoint because the parabola opens upward and continues increasing toward $x=5$ on this interval."""

WE1_HE = """**נתון:** $f(x)=x^2-4x+3$ על הקטע הסגור $[0,5]$. מצאו מקסימום ומינימום מוחלטים.

**אסטרטגיה:** על קטע סגור, EVT מבטיח קיום קיצונים. המועמדים: נקודות קריטיות פנימיות ($f'=0$) וקצוות.

### צעד 1: נקודות קריטיות
$$f'(x)=2x-4=0 \\Rightarrow x=2$$
בודקים $x=2 \\in (0,5)$ — כן, נקודה קריטית פנימית.

### צעד 2: טבלת מועמדים
| $x$ | $f(x)$ |
|-----|--------|
| $0$ (קצה) | $3$ |
| $2$ (קריטית) | $-1$ |
| $5$ (קצה) | $8$ |

### צעד 3: השוואה ומסקנה
- **מקסימום מוחלט:** $f(5)=8$ ב-$x=5$ (קצה — לא בקריטית!).
- **מינימום מוחלט:** $f(2)=-1$ ב-$x=2$.

**תשובה:** מקסימום $8$ ב-$x=5$; מינימום $-1$ ב-$x=2$. ✓

**הערת בחינה:** תלמידים לעיתים מדווחים $x=2$ כמקסימום כי זו הקריטית היחידה. תמיד חשבו קצוות על קטע סגור.

**אימות:** $f''(x)=2>0$ מאשר $x=2$ כמינימום מקומי, לא מקסימום — המקסימום המוחלט בקצה הימני כי הפרבולה פונה למעלה ועולה לכיוון $x=5$."""

WE2_EN = """**Given:** A rectangle has fixed perimeter $P$ meters. Find dimensions that maximize the area.

### Move 1: Variables and diagram
Let width $=x$ and length $=y$. Both must be positive. Sketch the rectangle and label each side before writing equations — clarity here prevents swapped variables later.

### Move 2: Constraint (perimeter fixed)
$$2x+2y=P \\implies y=\\frac{P}{2}-x$$
Domain: $0<x<P/2$ so that $y>0$.

### Move 3: Objective function
$$A(x)=x\\cdot y=x\\left(\\frac{P}{2}-x\\right)=\\frac{P}{2}x-x^2$$

### Move 4: Critical point
$$A'(x)=\\frac{P}{2}-2x=0 \\implies x=\\frac{P}{4}$$

### Move 5: Verify maximum
$$A''(x)=-2<0 \\Rightarrow \\text{local maximum at }x=P/4$$
Since $A''$ is constant and negative, the critical point is a maximum on the entire domain $(0,P/2)$.

### Move 6: Second dimension and optimal area
$$y=\\frac{P}{2}-\\frac{P}{4}=\\frac{P}{4}, \\quad A_{\\max}=\\left(\\frac{P}{4}\\right)^2=\\frac{P^2}{16}$$

**Answer:** Both sides equal $P/4$ — the optimal shape is a **square**. Maximum area $P^2/16$. ✓

**Transfer:** Any "fixed perimeter, maximize area" problem reduces to this template — symmetry often yields equal dimensions.

**Why a square?** Among all rectangles with the same perimeter, equal sides spread the perimeter evenly and maximize the product $x(P/2-x)$, which is a symmetric quadratic opening downward on the feasible domain $0<x<P/2$."""

WE2_HE = """**נתון:** למלבן היקף קבוע $P$ מ'. מצאו ממדים שממקסמים שטח.

### צעד 1: משתנים ותרשים
רוחב $=x$, אורך $=y$. שניהם חיוביים. שרטטו מלבן וסמנו כל צלע לפני כתיבת משוואות — בהירות כאן מונעת החלפת משתנים בהמשך.

### צעד 2: אילוץ (היקף קבוע)
$$2x+2y=P \\Rightarrow y=\\frac{P}{2}-x$$
תחום: $0<x<P/2$ כדי ש-$y>0$.

### צעד 3: פונקציית מטרה
$$A(x)=x\\cdot y=x\\left(\\frac{P}{2}-x\\right)=\\frac{P}{2}x-x^2$$

### צעד 4: נקודה קריטית
$$A'(x)=\\frac{P}{2}-2x=0 \\Rightarrow x=\\frac{P}{4}$$

### צעד 5: אימות מקסימום
$$A''(x)=-2<0 \\Rightarrow \\text{מקסימום מקומי ב-}x=P/4$$
כיוון $A''$ קבועה ושלילית, הנקודה הקריטית היא מקסימום על כל התחום $(0,P/2)$.

### צעד 6: ממד שני ושטח מיטבי
$$y=\\frac{P}{4}, \\quad A_{\\max}=\\frac{P^2}{16}$$

**תשובה:** שני הצלעות $P/4$ — הצורה המיטבית היא **ריבוע**. שטח מרבי $P^2/16$. ✓

**העברה:** כל בעיית "היקף קבוע, שטח מרבי" נופלת לתבנית זו — לעיתים סימטריה נותנת ממדים שווים.

**למה ריבוע?** בין כל המלבנים עם אותו היקף, צלעות שוות מפזרות את ההיקף באופן שווה וממקסמות את המכפלה $x(P/2-x)$ — פרבולה סימטרית הפונה למטה על התחום $0<x<P/2$."""

WE3_EN = """**Given:** A farmer has 400 m of fence to enclose a rectangular field against a river (no fence on the river side). Find dimensions that maximize enclosed area.

### Move 1: Label the diagram
Side parallel to river (unfenced) $=y$. Each side perpendicular to river $=x$.

### Move 2: Constraint (fence budget)
$$2x+y=400 \\implies y=400-2x$$
Domain: $0<x<200$ (so $y>0$).

### Move 3: Area objective
$$A(x)=x(400-2x)=400x-2x^2$$

### Move 4: Critical point
$$A'(x)=400-4x=0 \\implies x=100$$

### Move 5: Confirm maximum
$$A''(x)=-4<0 \\Rightarrow \\text{maximum at }x=100$$

### Move 6: Remaining dimension and max area
$$y=400-2(100)=200, \\quad A_{\\max}=100\\times 200=20{,}000\\text{ m}^2$$

**Answer:** Width $100$ m (perpendicular to river), length $200$ m (parallel). Maximum area $20{,}000$ m$^2$. ✓

**Pattern:** For one-sided fence problems, the unfenced side is typically **twice** the fenced perpendicular sides when fence is split equally among the three fenced segments.

**Check domain:** At $x=100$, $y=200>0$; as $x\\to 0^+$ or $x\\to 200^-$, area $\\to 0$, confirming the interior critical point gives the global maximum on the feasible region."""

WE3_HE = """**נתון:** לחקלאי 400 מ' גדר לגידור שדה מלבני לאורך נהר (ללא גדר בצד הנהר). מצאו ממדים שממקסמים שטח.

### צעד 1: סימון תרשים
צד מקביל לנהר (ללא גדר) $=y$. כל צד ניצב לנהר $=x$.

### צעד 2: אילוץ (תקציב גדר)
$$2x+y=400 \\Rightarrow y=400-2x$$
תחום: $0<x<200$ (כדי ש-$y>0$).

### צעד 3: פונקציית שטח
$$A(x)=x(400-2x)=400x-2x^2$$

### צעד 4: נקודה קריטית
$$A'(x)=400-4x=0 \\Rightarrow x=100$$

### צעד 5: אימות מקסימום
$$A''(x)=-4<0 \\Rightarrow \\text{מקסימום ב-}x=100$$

### צעד 6: ממד נותר ושטח מרבי
$$y=200, \\quad A_{\\max}=20{,}000\\text{ מ'}^2$$

**תשובה:** רוחב $100$ מ' (ניצב לנהר), אורך $200$ מ' (מקביל). שטח מרבי $20{,}000$ מ'². ✓

**דפוס:** בבעיות גדר חד-צדדית, הצד ללא גדר לרוב **כפול** מהצלעות הניצבות המגודרות כשהגדר מתחלקת שווה בין שלושת הקטעים.

**בדיקת תחום:** ב-$x=100$, $y=200>0$; כש-$x\\to 0^+$ או $x\\to 200^-$, השטח $\\to 0$, מה שמאשר שהקריטית הפנימית נותנת מקסימום גלובלי על האזור האפשרי."""

CHK1_EN = """**Goal:** Absolute extrema of $g(x)=x^3-3x$ on $[-2,3]$.

### Move 1: Critical points
$$g'(x)=3x^2-3=3(x-1)(x+1)=0 \\Rightarrow x=-1,\\; x=1$$
Both lie in $(-2,3)$.

### Move 2: Evaluate all candidates
| $x$ | $g(x)$ |
|-----|--------|
| $-2$ (endpoint) | $(-8)+6=-2$ |
| $-1$ (critical) | $-1+3=2$ |
| $1$ (critical) | $1-3=-2$ |
| $3$ (endpoint) | $27-9=18$ |

### Move 3: Conclude
- **Absolute maximum:** $g(3)=18$ at $x=3$.
- **Absolute minimum:** $-2$ (tied at $x=-2$ and $x=1$).

**Answer:** Max $18$ at $x=3$; min $-2$ at $x=-2$ and $x=1$. ✓"""

CHK1_HE = """**מטרה:** קיצונים מוחלטים של $g(x)=x^3-3x$ על $[-2,3]$.

### צעד 1: נקודות קריטיות
$$g'(x)=3x^2-3=0 \\Rightarrow x=-1,\\; x=1$$
שתיהן ב-$(-2,3)$.

### צעד 2: הערכה בכל המועמדים
| $x$ | $g(x)$ |
|-----|--------|
| $-2$ (קצה) | $-2$ |
| $-1$ (קריטית) | $2$ |
| $1$ (קריטית) | $-2$ |
| $3$ (קצה) | $18$ |

### צעד 3: מסקנה
- **מקסימום מוחלט:** $g(3)=18$ ב-$x=3$.
- **מינימום מוחלט:** $-2$ (שוויון ב-$x=-2$ ו-$x=1$).

**תשובה:** מקסימום $18$ ב-$x=3$; מינימום $-2$ ב-$x=-2$ ו-$x=1$. ✓"""

CHK2_EN = """**Goal:** Minimize surface area of open box (square base, no top) with volume $V=32$ cm$^3$.

### Move 1: Variables
Base side $=x$, height $=h$. Volume constraint: $x^2h=32 \\Rightarrow h=32/x^2$.

### Move 2: Surface area (no top)
$$A(x)=x^2+4xh=x^2+\\frac{128}{x}$$

### Move 3: Critical point
$$A'(x)=2x-\\frac{128}{x^2}=0 \\Rightarrow 2x^3=128 \\Rightarrow x^3=64 \\Rightarrow x=4$$
Domain: $x>0$.

### Move 4: Height and minimum area
$$h=\\frac{32}{16}=2\\text{ cm}, \\quad A_{\\min}=16+32=48\\text{ cm}^2$$

**Answer:** Base $4$ cm $\\times$ $4$ cm, height $2$ cm. Minimum surface area $48$ cm$^2$. ✓"""

CHK2_HE = """**מטרה:** מזער שטח פנים של קופסה פתוחה (בסיס ריבועי, ללא מכסה) עם נפח $V=32$ ס\"מ³.

### צעד 1: משתנים
צלע בסיס $=x$, גובה $=h$. אילוץ נפח: $x^2h=32 \\Rightarrow h=32/x^2$.

### צעד 2: שטח פנים (ללא מכסה)
$$A(x)=x^2+4xh=x^2+\\frac{128}{x}$$

### צעד 3: נקודה קריטית
$$A'(x)=2x-\\frac{128}{x^2}=0 \\Rightarrow x^3=64 \\Rightarrow x=4$$
תחום: $x>0$.

### צעד 4: גובה ושטח מינימלי
$$h=2\\text{ ס\"מ}, \\quad A_{\\min}=48\\text{ ס\"מ}^2$$

**תשובה:** בסיס $4\\times 4$ ס\"מ, גובה $2$ ס\"מ. שטח מינימלי $48$ ס\"מ². ✓"""

METHOD_EN = """| Test | How it works | When to use | Limitation |
|------|-------------|-------------|------------|
| **First derivative** | Sign of $f'$ on each side of $c$ | Always works; required when $f''(c)=0$ | Needs interval sign analysis |
| **Second derivative** | Sign of $f''(c)$ at critical point | Quick for polynomials and rational setups | Inconclusive if $f''(c)=0$ |
| **Endpoint comparison** | Evaluate $f$ at all critical points + $a,b$ | Closed interval absolute extrema | Only applies on bounded domains |

**Applied optimization decision tree:**
1. Define variables with units and draw a diagram.
2. Write the constraint equation from the problem statement.
3. Write the objective function $Q$ (what to max/min).
4. Eliminate one variable using the constraint.
5. State the domain of $Q(x)$ from physical constraints.
6. Solve $Q'(x)=0$; discard roots outside the domain.
7. Classify: second derivative test, first derivative test, or endpoint table.
8. Answer the question — state optimal dimensions **and** the optimal value with units.

**Speed tip:** If $Q(x)$ is a downward-opening parabola ($Q''<0$ constant), the unique critical point is automatically a maximum."""

METHOD_HE = """| מבחן | עיקרון | מתי להשתמש | מגבלה |
|------|--------|------------|-------|
| **נגזרת ראשונה** | סימן $f'$ משני צדי $c$ | תמיד; חובה כש-$f''(c)=0$ | דורש ניתוח סימנים |
| **נגזרת שנייה** | סימן $f''(c)$ בנקודה קריטית | מהיר לפולינומים | אין מסקנה אם $f''(c)=0$ |
| **השוואת קצוות** | $f$ בכל קריטית + $a,b$ | קיצון מוחלט על קטע סגור | רק על תחום חסום |

**עץ החלטות לאופטימיזציה שימושית:**
1. הגדירו משתנים עם יחידות ושרטטו תרשים.
2. כתבו משוואת אילוץ מהניסוח.
3. כתבו פונקציית מטרה $Q$ (מה למקסם/למזער).
4. בצעו אלימינציה באמצעות האילוץ.
5. ציינו תחום $Q(x)$ מאילוצים פיזיים.
6. פתרו $Q'(x)=0$; זרקו שורשים מחוץ לתחום.
7. סווגו: מבחן שני, ראשון, או טבלת קצוות.
8. ענו — ממדים מיטביים **וגם** ערך מיטבי עם יחידות.

**טיפ מהירות:** אם $Q(x)$ פרבולה פונה למטה ($Q''<0$ קבוע), הקריטית היחידה היא אוטומטית מקסימום."""

PITFALL_EN = """1. **Not checking endpoints.** On $[a,b]$, the absolute extremum may occur at $a$ or $b$, not at an interior critical point. Always build a table: every critical point in $(a,b)$ plus both endpoints.

2. **Ignoring the physical domain.** In applied problems, $x$ must be positive, lengths must fit the available material, etc. Algebra may produce $x=-3$ or $x=500$ — discard values outside the feasible region before classifying.

3. **Assuming every critical point is a maximum.** The question asks for a maximum, but $f'(x)=0$ only identifies candidates. Use $f''$ or a sign chart to confirm direction.

4. **Skipping the constraint in two-variable setups.** Writing $A=xy$ without substituting $y=\\frac{P}{2}-x$ leaves two variables — differentiation cannot proceed until you reduce to one.

5. **Stopping at $f'(x)=0$ without solving.** Writing $f'(x)=2x-4$ is not an answer. Set equal to zero and solve: $x=2$. Examiners deduct for incomplete final steps.

6. **Forgetting units in the answer.** "Maximum area is $8$" loses points — write "$8$ m$^2$" or state dimensions explicitly."""

PITFALL_HE = """1. **אי-בדיקת קצוות.** על $[a,b]$, הקיצון המוחלט עשוי להיות ב-$a$ או $b$, לא בקריטית פנימית. בנו טבלה: כל קריטית ב-$(a,b)$ ושני הקצוות.

2. **התעלמות מהתחום הפיזי.** בבעיות שימושיות, $x$ חייב להיות חיובי, אורכים חייבים להתאים לחומר. אלגברה עלולה לתת $x=-3$ — זרקו ערכים מחוץ לאזור האפשרי.

3. **הנחה שכל קריטית היא מקסימום.** $f'(x)=0$ מזהה מועמדים בלבד. השתמשו ב-$f''$ או טבלת סימנים.

4. **דילוג על האילוץ.** כתיבת $A=xy$ בלי הצבת $y=\\frac{P}{2}-x$ משאירה שני משתנים — אי אפשר לגזור עד צמצום.

5. **עצירה ב-$f'(x)=0$ בלי פתרון.** $f'(x)=2x-4$ אינו תשובה — השוו לאפס: $x=2$.

6. **שכחת יחידות.** "שטח מרבי $8$" מאבד נקודות — כתבו "$8$ מ'²" או ציינו ממדים."""

WHY_EN = """Optimization is the bridge between abstract calculus and real decision-making. Every time an engineer sizes a beam, a retailer sets inventory, or a GPS router picks a path, someone solved (or approximated) an optimization problem — often starting with the same derivative tests you learn here.

**Connections in the knowledge graph:**
- `concept:derivatives_applications` — sign charts and derivative tests are prerequisites.
- `concept:integrals_applications` — area between curves and volumes of revolution extend optimization to integral setups.
- `concept:uni_derivative_applications` — university mechanics (least action, equilibrium) reuses Lagrange-style thinking.

**Exam transfer:** Bagrut and Calc 1 finals reward *setup quality*. A correct derivative with a wrong constraint earns partial credit at best. Drawing the diagram and naming variables before differentiating is how top scorers organize multi-step problems under time pressure."""

WHY_HE = """אופטימיזציה היא הגשר בין חשבון מופשט לקבלת החלטות אמיתית. בכל פעם שמהנדס מגדיר קורה, קמעונאי קובע מלאי, או ניווט GPS בוחר מסלול — מישהו פתר (או קירב) בעיית אופטימיזציה, לעיתים עם אותם מבחני נגזרת שלומדים כאן.

**קשרים בגרף הידע:**
- `concept:derivatives_applications` — טבלאות סימן ומבחני נגזרת הם תנאי קדם.
- `concept:integrals_applications` — שטח בין עקומות ונפחי סיבוב מרחיבים אופטימיזציה להכנות אינטגרליות.
- `concept:uni_derivative_applications` — מכניקה אוניברסיטאית (פעולה מינימלית, שיווי משקל) חוזרת על חשיבה דומה.

**העברה לבחינה:** בבגרות ובמבחני חשבון 1 מעריכים *איכות הכנה*. נגזרת נכונה עם אילוץ שגוי — לכל היותר נקודות חלקיות. שרטוט תרשים ומתן שמות למשתנים לפני גזירה — כך מצטיינים מארגנים בעיות רב-שלביות תחת לחץ זמן."""

BEFORE_EN = """**Absolute extrema on $[a,b]$ — exam checklist:**
1. Find all $x$ in $(a,b)$ where $f'(x)=0$ or $f'(x)$ DNE.
2. Evaluate $f(x)$ at each critical point and at endpoints $a$, $b$.
3. Largest value = absolute max; smallest = absolute min. Report location(s).

**Second derivative test — one-line rules:**
- $f'(c)=0$, $f''(c)>0$ → local **min**.
- $f'(c)=0$, $f''(c)<0$ → local **max**.
- $f''(c)=0$ → **inconclusive**; use first derivative test.

**Applied optimization — before you submit:**
- [ ] Diagram drawn with variables labeled.
- [ ] Constraint equation written and used to eliminate a variable.
- [ ] Objective function in one variable with domain stated.
- [ ] Critical point(s) found; domain violations discarded.
- [ ] Max/min verified (sign of $f''$ or candidate table).
- [ ] Answer includes optimal dimensions **and** optimal value with units.

**Time management:** Spend roughly equal time on setup and calculus — a rushed diagram causes the most lost points."""

BEFORE_HE = """**קיצונים מוחלטים על $[a,b]$ — רשימת בחינה:**
1. מצאו כל $x$ ב-$(a,b)$ שבהם $f'(x)=0$ או $f'(x)$ לא קיימת.
2. חשבו $f(x)$ בכל קריטית ובקצוות $a,b$.
3. הגדול ביותר = מקסימום מוחלט; הקטן = מינימום. ציינו מיקום.

**מבחן נגזרת שנייה — כללים:**
- $f'(c)=0$, $f''(c)>0$ → **מינימום** מקומי.
- $f'(c)=0$, $f''(c)<0$ → **מקסימום** מקומי.
- $f''(c)=0$ → **אין מסקנה**; מבחן ראשון.

**אופטימיזציה שימושית — לפני הגשה:**
- [ ] תרשים עם משתנים.
- [ ] משוואת אילוץ ואלימינציה.
- [ ] פונקציית מטרה במשתנה אחד + תחום.
- [ ] נקודות קריטיות; שורשים מחוץ לתחום נזרקו.
- [ ] מקס/מין אומת (סימן $f''$ או טבלה).
- [ ] תשובה: ממדים **וגם** ערך עם יחידות.

**ניהול זמן:** הקדישו זמן דומה להכנה ולחשבון — תרשים מהיר גורם לאובדן הנקודות הגדול ביותר."""

SUMMARY_EN = """- **Critical points** ($f'=0$ or DNE) are candidates for extrema — always verify max vs. min.
- **First derivative test:** sign change of $f'$ at $c$ classifies local extrema.
- **Second derivative test:** $f''(c)>0$ → min, $f''(c)<0$ → max; $f''(c)=0$ → inconclusive.
- **Absolute extrema on $[a,b]$:** compare all interior critical points with endpoints $a$ and $b$.
- **Applied optimization:** diagram → constraint → objective → one variable → differentiate → test → answer with units.
- The final answer must state both optimal dimensions and the optimal numerical value."""

SUMMARY_HE = """- **נקודות קריטיות** ($f'=0$ או לא קיימת) הן מועמדות — תמיד אמתו מקסימום מול מינימום.
- **מבחן נגזרת ראשונה:** שינוי סימן $f'$ ב-$c$ מסווג קיצון מקומי.
- **מבחן נגזרת שנייה:** $f''(c)>0$ → מין, $f''(c)<0$ → מקס; $f''(c)=0$ → אין מסקנה.
- **קיצון מוחלט על $[a,b]$:** השוו קריטיות פנימיות עם קצוות $a,b$.
- **אופטימיזציה שימושית:** תרשים → אילוץ → מטרה → משתנה אחד → גזירה → מבחן → תשובה עם יחידות.
- התשובה הסופית חייבת לכלול ממדים מיטביים וערך מספרי מיטבי."""

EXPLS = {
    1: fmt_expl(
        "Differentiate: $f'(x)=3x^2-12x+9=3(x-1)(x-3)=0$ gives $x=1$ and $x=3$. Second derivative $f''(x)=6x-12$: at $x=1$, $f''(1)=-6<0$ so local max with $f(1)=4$; at $x=3$, $f''(3)=6>0$ so local min with $f(3)=0$.",
        "For polynomial extrema: factor $f'$ if possible, solve for critical points, then apply the second derivative test when $f''$ is easy. A sign chart for $f'$ confirms the classification.",
        "Classifying using $f'$ sign at only one side of the critical point, or reporting critical points without values $f(1)=4$ and $f(3)=0$.",
        "On Bagrut function investigation, always state both the $x$-location and the function value at each extremum. Examiners deduct for missing $f(c)$.",
        "גזירה: $f'(x)=3x^2-12x+9=3(x-1)(x-3)=0$ נותן $x=1$ ו-$x=3$. נגזרת שנייה $f''(x)=6x-12$: ב-$x=1$, $f''(1)=-6<0$ — מקסימום מקומי $f(1)=4$; ב-$x=3$, $f''(3)=6>0$ — מינימום $f(3)=0$.",
        "לקיצוני פולינום: פירקו $f'$ אם אפשר, מצאו קריטיות, והפעילו מבחן נגזרת שנייה כש-$f''$ נוח. טבלת סימנים של $f'$ מאשרת.",
        "סיווג לפי סימן $f'$ מצד אחד בלבד, או דיווח על קריטיות בלי ערכים $f(1)=4$ ו-$f(3)=0$.",
        "בחקירת פונקציה בבגרות, ציינו מיקום $x$ וערך $f(c)$ בכל קיצון. בוחנים מורידים נקודות על $f(c)$ חסר.",
    ),
    2: fmt_expl(
        "On $[-2,2]$: $f'(x)=3x^2-3=0$ gives $x=\\pm 1$. Evaluate: $f(-2)=-2$, $f(-1)=2$, $f(1)=-2$, $f(2)=2$. Maximum value is $2$ (at $x=-1$ and $x=2$); minimum is $-2$ (at $x=-2$ and $x=1$).",
        "Closed-interval absolute extrema require a candidate table: all critical points inside the interval plus both endpoints. Never assume the interior critical point wins.",
        "Using only $x=\\pm 1$ and forgetting endpoints $f(-2)$ and $f(2)$, or reporting $x=-1$ as the only maximum location when $f(2)=2$ ties.",
        "Draw a quick table with four rows — endpoints first, then critical points. Ties are common on cubic functions; list all locations where the extremum value occurs.",
        "על $[-2,2]$: $f'(x)=3x^2-3=0$ נותן $x=\\pm 1$. הערכה: $f(-2)=-2$, $f(-1)=2$, $f(1)=-2$, $f(2)=2$. מקסימום $2$ (ב-$x=-1$ ו-$x=2$); מינימום $-2$ (ב-$x=-2$ ו-$x=1$).",
        "קיצון מוחלט על קטע סגור דורש טבלת מועמדים: כל קריטית בתוך הקטע ושני הקצוות. אל תניחו שהקריטית הפנימית מנצחת.",
        "שימוש רק ב-$x=\\pm 1$ ושכחת קצוות $f(-2)$ ו-$f(2)$, או דיווח $x=-1$ כמיקום מקסימום יחיד כש-$f(2)=2$ שווה.",
        "שרטטו טבלה עם ארבע שורות — קצוות תחילה, אחר כך קריטיות. שוויון נפוץ בפונקציות מעוקביות; רשמו כל מיקום של ערך הקיצון.",
    ),
    3: fmt_expl(
        "For $f(x)=x+1/x$ on $x>0$: $f'(x)=1-1/x^2=0$ gives $x=\\pm 1$; only $x=1$ is in the domain. $f''(1)=2>0$ confirms a minimum. $f(1)=1+1=2$.",
        "When the domain restricts $x>0$, discard negative roots from $f'(x)=0$ before testing. The AM-GM intuition ($x+1/x\\geq 2$) supports the calculus answer.",
        "Accepting $x=-1$ despite $x>0$ in the stem, or stopping at $x=1$ without computing $f(1)=2$.",
        "Classic minimization template: set derivative to zero, apply domain filter, verify with $f''>0$, state the minimum value — not just the $x$-coordinate.",
        "עבור $f(x)=x+1/x$ ב-$x>0$: $f'(x)=1-1/x^2=0$ נותן $x=\\pm 1$; רק $x=1$ בתחום. $f''(1)=2>0$ מאשר מינימום. $f(1)=2$.",
        "כשהתחום מגביל $x>0$, זרקו שורשים שליליים לפני המבחן. אינטואיציית AM-GM ($x+1/x\\geq 2$) תומכת בתשובה. זו תבנית קלאסית בבחינות.",
        "קבלת $x=-1$ למרות $x>0$ בניסוח, או עצירה ב-$x=1$ בלי $f(1)=2$.",
        "תבנית מינימום קלאסית: נגזרת לאפס, סינון תחום, $f''>0$, ציון ערך מינימלי — לא רק קואורדינטת $x$. כתבו את שלושת השלבים בבחינה.",
    ),
    4: fmt_expl(
        "$f'(x)=e^x-1=0$ gives $x=0$. Since $f''(x)=e^x>0$ for all $x$, the graph is always concave up and $x=0$ is a global minimum with $f(0)=e^0-0=1$.",
        "Exponential-minus-linear functions have at most one critical point. When $f''=e^x>0$ everywhere, the second derivative test at the sole critical point immediately gives a minimum.",
        "Saying 'inconclusive' because $f'(0)=0$, or forgetting that $e^x>0$ means $f''(0)=1>0$.",
        "For $e^x$ minus a polynomial, $f''=e^x$ is always positive — cite this once and skip the first derivative test entirely.",
        "$f'(x)=e^x-1=0$ נותן $x=0$. כיוון $f''(x)=e^x>0$ לכל $x$, הגרף תמיד קעור למעלה ו-$x=0$ מינימום גלובלי עם $f(0)=1$.",
        "פונקציות מעריכית פחות לינארית יש לכל היותר קריטית אחת. כש-$f''=e^x>0$ בכל מקום, מבחן שני בקריטית היחידה נותן מיד מינימום — אין צורך בטבלת סימנים.",
        "לומר 'אין מסקנה' כי $f'(0)=0$, או שכחה ש-$e^x>0$ אומר $f''(0)=1>0$.",
        "ל-$e^x$ פחות פולינום, $f''=e^x$ תמיד חיובי — צטטו פעם אחת ודלגו על מבחן ראשון. זו שאלה מהירה של נקודה אחת בבחינה.",
    ),
    5: fmt_expl(
        "Let $x$ = wire for square, $L-x$ for circle. Square side $x/4$, area $x^2/16$. Circle radius $(L-x)/(2\\pi)$, area $(L-x)^2/(4\\pi)$. Total $A(x)=x^2/16+(L-x)^2/(4\\pi)$. Setting $A'=0$: $x/8-(L-x)/(2\\pi)=0$ gives $x=4L/(\\pi+4)$. $A''>0$ confirms minimum.",
        "Wire-partition problems: express each shape's area in terms of its allocated length, sum for total area, differentiate once. The $\\pi$ in the circle perimeter $2\\pi r$ is the usual algebra trap.",
        "Using radius $L-x$ instead of $(L-x)/(2\\pi)$, or maximizing when the question asks to minimize total area.",
        "Write the circle area as $\\pi r^2$ with $r=(L-x)/(2\\pi)$ explicitly — graders check the perimeter-to-radius step before the derivative.",
        "נסמן $x$ = חוט לריבוע, $L-x$ למעגל. צלע ריבוע $x/4$, שטח $x^2/16$. רדיוס $(L-x)/(2\\pi)$, שטח $(L-x)^2/(4\\pi)$. סה\"כ $A(x)=x^2/16+(L-x)^2/(4\\pi)$. $A'=0$ נותן $x=4L/(\\pi+4)$. $A''>0$ — מינימום.",
        "בעיות חלוקת חוט: ביטוי שטח כל צורה לפי אורך שהוקצה, סכום, גזירה. $\\pi$ בהיקף מעגל $2\\pi r$ — מלכודת אלגברה נפוצה.",
        "שימוש ברדיוס $L-x$ במקום $(L-x)/(2\\pi)$, או מקסימום כשמבקשים מינימום שטח.",
        "כתבו שטח מעגל $\\pi r^2$ עם $r=(L-x)/(2\\pi)$ במפורש — בוחנים בודקים מעבר מהיקף לרדיוס לפני הנגזרת.",
    ),
    6: fmt_expl(
        "Minimize distance by minimizing $D^2=x^2+(2x+1)^2=5x^2+4x+1$ (same minimizer, no square root). $D'=10x+4=0$ gives $x=-2/5$, $y=1/5$. Point $(-2/5,1/5)$; distance $\\sqrt{1/25+4/25}=1/\\sqrt{5}$.",
        "Distance-to-line problems: substitute the line equation into the distance formula, square to remove the root, differentiate the quadratic. The closest point always exists for a non-vertical line.",
        "Differentiating $\\sqrt{5x^2+4x+1}$ directly (messy chain rule) instead of squaring first, or finding $x$ but not computing $y=2x+1$.",
        "Squaring distance is standard on exams — state 'minimize $D^2$ since $D\\geq 0$' for one method point before differentiating.",
        "ממזערים מרחק ע\"י $D^2=x^2+(2x+1)^2=5x^2+4x+1$. $D'=10x+4=0$ נותן $x=-2/5$, $y=1/5$. נקודה $(-2/5,1/5)$; מרחק $1/\\sqrt{5}$.",
        "מרחק לישר: הציבו משוואת הישר, רבעו להסרת שורש, גזרו את הריבוע. הנקודה הקרובה תמיד קיימת לישר לא אנכי. זו תבנית חוזרת בבחינות אוניברסיטאיות.",
        "גזירה ישירה של $\\sqrt{5x^2+4x+1}$ במקום ריבוע, או מציאת $x$ בלי $y=2x+1$.",
        "ריבוע מרחק הוא סטנדרט — כתבו 'ממזערים $D^2$ כי $D\\geq 0$' לנקודת שיטה לפני גזירה. ציינו גם את המרחק הסופי.",
    ),
    7: fmt_expl(
        "Volume $V=\\pi r^2 h=1000$ gives $h=1000/(\\pi r^2)$. Surface $A=2\\pi r^2+2\\pi rh=2\\pi r^2+2000/r$. $A'=4\\pi r-2000/r^2=0$ yields $r^3=500/\\pi$, so $r=(500/\\pi)^{1/3}$ and $h=2r$. Optimal cans have height equal to diameter.",
        "Cylinder surface area has two parts: $2\\pi r^2$ (top and bottom) plus $2\\pi rh$ (side). Substitute the volume constraint before differentiating — never treat $h$ as independent.",
        "Using $A=\\pi r^2+2\\pi rh$ (forgetting both circular ends) or leaving $h$ and $r$ as two variables without substitution.",
        "The $h=2r$ result is worth memorizing: for fixed volume, minimum surface area occurs when height equals diameter. Check $A''>0$ at your critical $r$.",
        "נפח $V=\\pi r^2 h=1000$ נותן $h=1000/(\\pi r^2)$. שטח $A=2\\pi r^2+2000/r$. $A'=4\\pi r-2000/r^2=0$ נותן $r^3=500/\\pi$, $r=(500/\\pi)^{1/3}$, $h=2r$. פחיות מיטביות: גובה = קוטר.",
        "שטח גליל: $2\\pi r^2$ (שני בסיסים) + $2\\pi rh$ (צד). הציבו אילוץ נפח לפני גזירה — $h$ לא בלתי תלוי. זו בעיה קלאסית בחשבון 1.",
        "שימוש ב-$A=\\pi r^2+2\\pi rh$ (שכחת בסיס תחתון) או השארת $h$ ו-$r$ בלי הצבה.",
        "תוצאת $h=2r$ שווה לזכור: לנפח קבוע, שטח מינימלי כשגובה = קוטר. בדקו $A''>0$ ב-$r$ הקריטי.",
    ),
    8: fmt_expl(
        "Inscribed rectangle with half-sides $x,y$ on a circle of radius $R$: constraint $x^2+y^2=R^2$, area $A=4xy$. Substitute $y=\\sqrt{R^2-x^2}$ and maximize $A^2=16x^2(R^2-x^2)$. Symmetry gives $x=y=R/\\sqrt{2}$ — a square with side $R\\sqrt{2}$.",
        "Circle-inscription problems use the Pythagorean relation from the radius as diagonal half-length. Maximizing $A^2$ avoids square roots while preserving the maximizer.",
        "Maximizing $x+y$ instead of $xy$, or forgetting the factor of 4 when converting half-sides to full rectangle dimensions.",
        "When the answer is a square inscribed in a circle, side length is always $R\\sqrt{2}$ — quick sanity check on multiple-choice exams.",
        "מלבן חרוט עם חצי-צלעות $x,y$ בעיגול רדיוס $R$: $x^2+y^2=R^2$, שטח $A=4xy$. הצבה $y=\\sqrt{R^2-x^2}$, מקסימום $A^2=16x^2(R^2-x^2)$. סימטריה: $x=y=R/\\sqrt{2}$ — ריבוע צלע $R\\sqrt{2}$.",
        "חריטה בעיגול: יחס פיתגורס מהרדיוס כחצי אלכסון. מקסימום $A^2$ נמנע משורשים ושומר על המקסימום. תוצאת הריבוע היא תבנית מוכרת.",
        "מקסימום $x+y$ במקום $xy$, או שכחת גורם 4 בהמרה מחצי-צלעות למלבן מלא.",
        "כשהתשובה ריבוע חרוט בעיגול, צלע = $R\\sqrt{2}$ — בדיקת sanity מהירה בבחינה. כתבו גם את שתי הצלעות $R/\\sqrt{2}$.",
    ),
}


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in MIN:
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            min_en, min_he = MIN[kind]
            if en_w < min_en:
                errors.append(f"{kind} en {en_w} < {min_en}")
            if he_w < min_he:
                errors.append(f"{kind} he {he_w} < {min_he}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{kind}: weak Hebrew body")
    for q in data["questions"]:
        ew = wc(q.get("explanation_en", ""))
        hw = wc(q.get("explanation_he", ""))
        if ew < 80:
            errors.append(f"q{q['ord']} expl-en {ew} < 80")
        if ew > 150:
            errors.append(f"q{q['ord']} expl-en {ew} > 150")
        if hw < 80:
            errors.append(f"q{q['ord']} expl-he {hw} < 80")
        if hw > 150:
            errors.append(f"q{q['ord']} expl-he {hw} > 150")
        if he_weak(q.get("explanation_he", ""), q.get("explanation_en", "")):
            errors.append(f"q{q['ord']}: weak Hebrew expl")
    return errors


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec["body_en_md"] = INTRO_EN
            sec["body_he_md"] = INTRO_HE
        elif kind == "definition":
            sec["body_en_md"] = DEF_EN
            sec["body_he_md"] = DEF_HE
        elif kind == "theory":
            sec["body_en_md"] = THEORY_EN
            sec["body_he_md"] = THEORY_HE
        elif kind == "worked_example":
            n = sec.get("example_number", 1)
            if n == 1:
                sec["body_en_md"], sec["body_he_md"] = WE1_EN, WE1_HE
            elif n == 2:
                sec["body_en_md"], sec["body_he_md"] = WE2_EN, WE2_HE
            elif n == 3:
                sec["body_en_md"], sec["body_he_md"] = WE3_EN, WE3_HE
        elif kind == "checkpoint":
            body = sec.get("body_en_md", "")
            if "g(x)" in body:
                sec["checkpoint_solution_en"] = CHK1_EN
                sec["checkpoint_solution_he"] = CHK1_HE
            else:
                sec["checkpoint_solution_en"] = CHK2_EN
                sec["checkpoint_solution_he"] = CHK2_HE
        elif kind == "method_guide":
            sec["body_en_md"] = METHOD_EN
            sec["body_he_md"] = METHOD_HE
        elif kind == "pitfall":
            sec["body_en_md"] = PITFALL_EN
            sec["body_he_md"] = PITFALL_HE
        elif kind == "why_matters":
            sec["body_en_md"] = WHY_EN
            sec["body_he_md"] = WHY_HE
        elif kind == "before_exam":
            sec["body_en_md"] = BEFORE_EN
            sec["body_he_md"] = BEFORE_HE
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY_EN
            sec["body_he_md"] = SUMMARY_HE

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]

    errs = validate(data)
    if errs:
        print("Validation errors:")
        for e in errs:
            print(" ", e)
        raise SystemExit(1)

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET} — validation passed")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
