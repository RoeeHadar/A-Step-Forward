#!/usr/bin/env python3
"""Expand function_analysis_4pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/function_analysis_4pt.json"

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


INTRO_EN = """The first derivative $f'(x)$ is the **instantaneous rate of change** — it tells you whether the graph rises, falls, or levels off at each point. On the Israeli 4-unit Bagrut track, **חקירת פונקציה** built on $f'$ alone is one of the highest-value question types: a typical paper includes a multi-part investigation worth **12–18 points** covering monotonicity, local extrema, and sometimes absolute extrema on a closed interval.

The sign of $f'(x)$ encodes everything you need at this level:
- $f'(x) > 0$: the function is **increasing** (positive slope).
- $f'(x) < 0$: the function is **decreasing** (negative slope).
- $f'(x) = 0$: a **critical point** — possibly a local maximum or minimum, but you must verify with a sign chart.

Unlike the 5-unit track, you are not required to use $f''$ for concavity here. The **first derivative test** — watching $f'$ change from $+$ to $-$ or $-$ to $+$ — is your primary classification tool. Master the sign chart workflow in this lesson and every polynomial, product, and simple rational investigation becomes routine."""

INTRO_HE = """הנגזרת הראשונה $f'(x)$ היא **קצב השינוי המיידי** — היא אומרת האם הגרף עולה, יורד או מתייצב בכל נקודה. במסלול 4 יחידות בבגרות, **חקירת פונקציה** המבוססת על $f'$ בלבד היא אחת משאלות הערך הגבוה: מבחן טיפוסי כולל חקירה רב-חלקית בשווי **12–18 נקודות** — מונוטוניות, קיצון מקומי, ולעיתים קיצון אבסולוטי בקטע סגור.

סימן $f'(x)$ מקודד את כל מה שצריך ברמה זו:
- $f'(x) > 0$: הפונקציה **עולה** (שיפוע חיובי).
- $f'(x) < 0$: הפונקציה **יורדת** (שיפוע שלילי).
- $f'(x) = 0$: **נקודה קריטית** — אולי מקסימום או מינימום מקומי, אך חובה לאמת בטבלת סימנים.

בניגוד ל-5 יחידות, אין חובה להשתמש ב-$f''$ לקמירות. **מבחן הנגזרת הראשונה** — מעקב אחר $f'$ שעוברת מ-$+$ ל-$-$ או מ-$-$ ל-$+$ — הוא כלי הסיווג העיקרי. שלטו בזרימת טבלת הסימנים בשיעור זה, וכל חקירת פולינום, מכפלה או רציונלית פשוטה תהפוך לשגרה."""

DEF_EN = """**Power rule:** $(x^n)' = n x^{n-1}$ for any real exponent $n$ where the expression is defined.

**Sum and difference:** $(f \\pm g)' = f' \\pm g'$ — differentiate term by term.

**Constant multiple:** $(cf)' = c f'$ — pull constants outside the derivative.

**Product rule:** $(fg)' = f'g + fg'$. Identify which factor is $f$ and which is $g$ before applying; a common 4pt pattern is $x^n e^x$.

**Chain rule:** $(f(g(x)))' = f'(g(x)) \\cdot g'(x)$. Essential for $\\ln(g(x))$ and composite powers.

**Standard derivatives to memorize:**
- $(e^x)' = e^x$
- $(\\ln x)' = \\dfrac{1}{x}$ for $x > 0$
- $(\\sin x)' = \\cos x$, $(\\cos x)' = -\\sin x$

**Critical points:** values of $x$ in the domain where $f'(x) = 0$ **or** $f'(x)$ is undefined (e.g., denominator zero in a rational $f'$).

**First derivative test:** at a critical point $x_0$ inside the domain:
- $f'$ changes from $+$ to $-$: **local maximum** at $(x_0, f(x_0))$.
- $f'$ changes from $-$ to $+$: **local minimum** at $(x_0, f(x_0))$.
- No sign change: **not an extremum** (often an inflection-like flat spot at 4pt level)."""

DEF_HE = """**כלל חזקה:** $(x^n)' = n x^{n-1}$ לכל מעריך ממשי $n$ שבו הביטוי מוגדר.

**סכום והפרש:** $(f \\pm g)' = f' \\pm g'$ — גוזרים איבר-איבר.

**כפל בקבוע:** $(cf)' = c f'$ — מוציאים קבועים מחוץ לנגזרת.

**כלל מכפלה:** $(fg)' = f'g + fg'$. זהו את $f$ ו-$g$ לפני היישום; דפוס נפוץ ב-4 יח' הוא $x^n e^x$.

**כלל שרשרת:** $(f(g(x)))' = f'(g(x)) \\cdot g'(x)$. חיוני ל-$\\ln(g(x))$ ולחזקות מורכבות.

**נגזרות סטנדרטיות לשינון:**
- $(e^x)' = e^x$
- $(\\ln x)' = \\dfrac{1}{x}$ עבור $x > 0$
- $(\\sin x)' = \\cos x$, $(\\cos x)' = -\\sin x$

**נקודות קריטיות:** ערכי $x$ בתחום שבהם $f'(x) = 0$ **או** $f'(x)$ לא מוגדרת (למשל מכנה אפס ב-$f'$ רציונלית).

**מבחן הנגזרת הראשונה:** בנקודה קריטית $x_0$ בתוך התחום:
- $f'$ עוברת מ-$+$ ל-$-$: **מקסימום מקומי** ב-$(x_0, f(x_0))$.
- $f'$ עוברת מ-$-$ ל-$+$: **מינימום מקומי** ב-$(x_0, f(x_0))$.
- אין שינוי סימן: **לא קיצון** (לעיתים נקודה שטוחה דמוית פיתול ברמת 4 יח')."""

THEORY_EN = """**Complete function analysis at 4pt level — seven core steps:**

1. **Domain:** State where $f$ is defined. Exclude division by zero and invalid logarithm arguments.

2. **Compute $f'(x)$:** Apply power, product, chain, and standard derivative rules. Simplify and factor when possible — factored $f'$ makes the sign chart faster.

3. **Find critical points:** Solve $f'(x) = 0$ and note where $f'$ is undefined. These $x$-values partition the domain into test intervals.

4. **Build the sign chart of $f'$:** Pick one test point per interval. Record the sign of $f'$ and the arrow behavior of $f$ ($\\nearrow$ increasing, $\\searrow$ decreasing).

5. **Read monotonicity:** Increasing where $f' > 0$; decreasing where $f' < 0$. Write intervals in set notation.

6. **Classify extrema:** At each critical point, read the sign change of $f'$. $+ \\to -$ means local max; $- \\to +$ means local min.

7. **Compute $f(x_0)$ at extrema:** Examiners require the full coordinate $(x_0, f(x_0))$, not just the $x$-value.

**Sign chart template:**
$$x: \\quad (-\\infty,\\, x_1) \\quad x_1 \\quad (x_1,\\, x_2) \\quad x_2 \\quad (x_2,\\, +\\infty)$$
$$f': \\quad + \\quad 0 \\quad - \\quad 0 \\quad +$$
$$f: \\quad \\nearrow \\quad \\max \\quad \\searrow \\quad \\min \\quad \\nearrow$$

**Absolute extrema on $[a,b]$:** After finding local candidates inside $(a,b)$, evaluate $f$ at each critical point **and** at both endpoints $a$ and $b$, then compare all values."""

THEORY_HE = """**חקירת פונקציה מלאה ברמת 4 יח' — שבעה צעדים מרכזיים:**

1. **תחום:** ציינו היכן $f$ מוגדרת. הוציאו חלוקה באפס וארגומנטים לא חוקיים של לוגריתם.

2. **חשבו $f'(x)$:** יישמו כללי חזקה, מכפלה, שרשרת ונגזרות סטנדרטיות. פשטו ופרקו כשאפשר — $f'$ מפורקת מזרזת את טבלת הסימנים.

3. **מצאו נקודות קריטיות:** פתרו $f'(x) = 0$ וסמנו היכן $f'$ לא מוגדרת. ערכי $x$ אלה מחלקים את התחום לקטעי בדיקה.

4. **בנו טבלת סימנים של $f'$:** בחרו נקודת בדיקה אחת בכל קטע. רשמו סימן $f'$ והתנהגות $f$ ($\\nearrow$ עולה, $\\searrow$ יורדת).

5. **קראו מונוטוניות:** עולה כש-$f' > 0$; יורדת כש-$f' < 0$. כתבו קטעים בסימון קבוצות.

6. **סווגו קיצון:** בכל נקודה קריטית, קראו שינוי סימן $f'$. $+ \\to -$ = מקסימום מקומי; $- \\to +$ = מינימום מקומי.

7. **חשבו $f(x_0)$ בקיצון:** בוחנים דורשים קואורדינטה מלאה $(x_0, f(x_0))$, לא רק $x$.

**תבנית טבלת סימנים:**
$$x: \\quad (-\\infty,\\, x_1) \\quad x_1 \\quad (x_1,\\, x_2) \\quad x_2 \\quad (x_2,\\, +\\infty)$$
$$f': \\quad + \\quad 0 \\quad - \\quad 0 \\quad +$$
$$f: \\quad \\nearrow \\quad \\max \\quad \\searrow \\quad \\min \\quad \\nearrow$$

**קיצון אבסולוטי ב-$[a,b]$:** אחרי מציאת מועמדים מקומיים בתוך $(a,b)$, חשבו $f$ בכל נקודה קריטית **וגם** בקצוות $a$ ו-$b$, והשוו את כל הערכים."""

WE1_EN = """**Find the monotone intervals and local extrema of $f(x) = x^3 - 3x^2$.**

This cubic is the standard 4pt warm-up: one local max and one local min, with a clear factored derivative.

### Move 1: Differentiate and factor
$$f'(x) = 3x^2 - 6x = 3x(x - 2).$$
Factoring immediately exposes the roots $x = 0$ and $x = 2$.

### Move 2: Critical points
$$f'(x) = 0 \\implies 3x(x-2) = 0 \\implies x = 0 \\text{ or } x = 2.$$
Both lie in the domain $\\mathbb{R}$.

### Move 3: Sign chart

| Interval | Test | $f'$ | $f$ |
|----------|------|------|-----|
| $(-\\infty, 0)$ | $x=-1$ | $3(-1)(-3)=9>0$ | increasing |
| $(0, 2)$ | $x=1$ | $3(1)(-1)=-3<0$ | decreasing |
| $(2, +\\infty)$ | $x=3$ | $3(3)(1)=9>0$ | increasing |

### Move 4: Classify and compute values
- $x=0$: $f'$ changes $+ \\to -$ → **local maximum**. $f(0) = 0$. Point: $(0, 0)$.
- $x=2$: $f'$ changes $- \\to +$ → **local minimum**. $f(2) = 8-12 = -4$. Point: $(2, -4)$.

**Answer:** Increasing on $(-\\infty, 0) \\cup (2, +\\infty)$; decreasing on $(0, 2)$. Local max $(0,0)$; local min $(2,-4)$.

**Bagrut note:** Always draw the sign chart on your exam paper — graders award method marks even if a final interval is miswritten."""

WE1_HE = """**מצאו את קטעי המונוטוניות ונקודות הקיצון המקומיות של $f(x) = x^3 - 3x^2$.**

מעוקבית זו היא חימום סטנדרטי ב-4 יח': מקסימום מקומי אחד ומינימום מקומי אחד, עם נגזרת מפורקת ברורה.

### צעד 1: גזירה ופירוק
$$f'(x) = 3x^2 - 6x = 3x(x - 2).$$
הפירוק חושף מיד את השורשים $x = 0$ ו-$x = 2$.

### צעד 2: נקודות קריטיות
$$f'(x) = 0 \\implies 3x(x-2) = 0 \\implies x = 0 \\text{ או } x = 2.$$
שניהן בתחום $\\mathbb{R}$.

### צעד 3: טבלת סימנים

| קטע | בדיקה | $f'$ | $f$ |
|-----|-------|------|-----|
| $(-\\infty, 0)$ | $x=-1$ | $9>0$ | עולה |
| $(0, 2)$ | $x=1$ | $-3<0$ | יורדת |
| $(2, +\\infty)$ | $x=3$ | $9>0$ | עולה |

### צעד 4: סיווג וחישוב ערכים
- $x=0$: $f'$ עוברת $+ \\to -$ → **מקסימום מקומי**. $f(0) = 0$. נקודה: $(0, 0)$.
- $x=2$: $f'$ עוברת $- \\to +$ → **מינימום מקומי**. $f(2) = -4$. נקודה: $(2, -4)$.

**תשובה:** עולה ב-$(-\\infty, 0) \\cup (2, +\\infty)$; יורדת ב-$(0, 2)$. מקס $(0,0)$; מין $(2,-4)$.

**הערת בגרות:** תמיד ציירו טבלת סימנים — מעניקים נקודות שיטה גם אם קטע סופי שגוי."""

WE2_EN = """**Find all local extrema of $f(x) = x^4 - 8x^2$.**

Even-degree polynomials can have multiple extrema. Here the derivative factors cleanly into four linear terms.

### Move 1: Differentiate and factor completely
$$f'(x) = 4x^3 - 16x = 4x(x^2 - 4) = 4x(x-2)(x+2).$$
Critical points: $x = -2,\\ 0,\\ 2$.

### Move 2: Sign chart via factor signs

| Interval | $4x$ | $(x-2)$ | $(x+2)$ | $f'$ | $f$ |
|----------|------|---------|---------|------|-----|
| $x < -2$ | $-$ | $-$ | $-$ | $-$ | ↘ |
| $-2 < x < 0$ | $-$ | $-$ | $+$ | $+$ | ↗ |
| $0 < x < 2$ | $+$ | $-$ | $+$ | $-$ | ↘ |
| $x > 2$ | $+$ | $+$ | $+$ | $+$ | ↗ |

### Move 3: Classify each critical point
- $x = -2$: $- \\to +$ → **local minimum**. $f(-2) = 16 - 32 = -16$.
- $x = 0$: $+ \\to -$ → **local maximum**. $f(0) = 0$.
- $x = 2$: $- \\to +$ → **local minimum**. $f(2) = -16$.

### Move 4: Symmetry check
$f(x) = f(-x)$ (even function), so extrema at $\\pm 2$ share the same $y$-value — a quick sanity check.

**Answer:** Local max at $(0, 0)$; local minima at $(-2, -16)$ and $(2, -16)$.

**Bagrut note:** When $f'$ factors into many linear terms, track each factor's sign separately rather than plugging test points blindly."""

WE2_HE = """**מצאו את כל נקודות הקיצון המקומיות של $f(x) = x^4 - 8x^2$.**

פולינומים במעלה זוגית יכולים להחזיק מספר קיצונות. כאן הנגזרת מתפרקת לשלושה גורמים לינאריים.

### צעד 1: גזירה ופירוק מלא
$$f'(x) = 4x^3 - 16x = 4x(x-2)(x+2).$$
נקודות קריטיות: $x = -2,\\ 0,\\ 2$.

### צעד 2: טבלת סימנים לפי גורמים

| קטע | $4x$ | $(x-2)$ | $(x+2)$ | $f'$ | $f$ |
|-----|------|---------|---------|------|-----|
| $x < -2$ | $-$ | $-$ | $-$ | $-$ | ↘ |
| $-2 < x < 0$ | $-$ | $-$ | $+$ | $+$ | ↗ |
| $0 < x < 2$ | $+$ | $-$ | $+$ | $-$ | ↘ |
| $x > 2$ | $+$ | $+$ | $+$ | $+$ | ↗ |

### צעד 3: סיווג כל נקודה קריטית
- $x = -2$: $- \\to +$ → **מינימום מקומי**. $f(-2) = -16$.
- $x = 0$: $+ \\to -$ → **מקסימום מקומי**. $f(0) = 0$.
- $x = 2$: $- \\to +$ → **מינימום מקומי**. $f(2) = -16$.

### צעד 4: בדיקת סימטריה
$f(x) = f(-x)$ (פונקציה זוגית), לכן קיצון ב-$\\pm 2$ חולק אותו $y$ — בדיקת הגיון מהירה.

**תשובה:** מקס מקומי ב-$(0, 0)$; מינימומים ב-$(-2, -16)$ וב-$(2, -16)$.

**הערת בגרות:** כש-$f'$ מתפרקת לגורמים לינאריים רבים, עקבו אחר סימן כל גורם בנפרד."""

WE3_EN = """**Analyze $f(x) = xe^x$: find the unique critical point, classify it, and state monotone intervals.**

Product-rule problems with exponentials appear on nearly every 4pt Bagrut. The key insight: $e^x > 0$ always, so only the bracket factor sets the sign of $f'$.

### Move 1: Product rule
$$f'(x) = (x)' \\cdot e^x + x \\cdot (e^x)' = e^x + xe^x = e^x(1 + x).$$

### Move 2: Critical points
$$f'(x) = 0 \\implies e^x(1+x) = 0.$$
Since $e^x > 0$ for all $x$, we need $1 + x = 0 \\implies x = -1$ — the **only** critical point.

### Move 3: Sign analysis without a full chart
Because $e^x > 0$, the sign of $f'(x)$ matches the sign of $(1+x)$:
- $x < -1$: $1+x < 0$ → $f' < 0$ → **decreasing**.
- $x > -1$: $1+x > 0$ → $f' > 0$ → **increasing**.

### Move 4: Classify and evaluate
$f'$ changes $- \\to +$ at $x = -1$: **local (and global) minimum**.
$$f(-1) = (-1) \\cdot e^{-1} = -\\frac{1}{e} \\approx -0.368.$$

**Answer:** Unique critical point $x = -1$ (local min at $(-1, -1/e)$). Decreasing on $(-\\infty, -1)$; increasing on $(-1, +\\infty)$.

**Bagrut note:** State explicitly that $e^x > 0$ when you cancel it — examiners expect this justification."""

WE3_HE = """**חקירו $f(x) = xe^x$: מצאו את הנקודה הקריטית היחידה, סווגו אותה וציינו קטעי מונוטוניות.**

בעיות כלל מכפלה עם אקספוננט מופיעות בכמעט כל בגרות 4 יח'. התובנה: $e^x > 0$ תמיד, ולכן רק גורם הסוגריים קובע סימן $f'$.

### צעד 1: כלל מכפלה
$$f'(x) = e^x + xe^x = e^x(1 + x).$$

### צעד 2: נקודות קריטיות
$$f'(x) = 0 \\implies e^x(1+x) = 0.$$
מאחר ש-$e^x > 0$ לכל $x$, נדרש $1 + x = 0 \\implies x = -1$ — הנקודה הקריטית **היחידה**.

### צעד 3: ניתוח סימן בלי טבלה מלאה
מכיוון $e^x > 0$, סימן $f'(x)$ = סימן $(1+x)$:
- $x < -1$: $f' < 0$ → **יורדת**.
- $x > -1$: $f' > 0$ → **עולה**.

### צעד 4: סיווג וחישוב
$f'$ עוברת $- \\to +$ ב-$x = -1$: **מינימום מקומי (וגם גלובלי)**.
$$f(-1) = -\\frac{1}{e} \\approx -0.368.$$

**תשובה:** נקודה קריטית יחידה $x = -1$ (מין ב-$(-1, -1/e)$). יורדת ב-$(-\\infty, -1)$; עולה ב-$(-1, +\\infty)$.

**הערת בגרות:** ציינו במפורש ש-$e^x > 0$ כשמבטלים אותו — בוחנים מצפים לנימוק."""

CHK1_EN = """Differentiate: $f'(x) = 3x^2 - 6 = 3(x^2 - 2)$.

Set $f'(x) = 0$: $x^2 = 2 \\implies x = \\pm\\sqrt{2}$.

**Sign chart:**
- For $x < -\\sqrt{2}$: pick $x = -2$, $f'(-2) = 12 - 6 = 6 > 0$ (increasing).
- For $-\\sqrt{2} < x < \\sqrt{2}$: pick $x = 0$, $f'(0) = -6 < 0$ (decreasing).
- For $x > \\sqrt{2}$: pick $x = 2$, $f'(2) = 6 > 0$ (increasing).

**Classification:**
- $x = -\\sqrt{2}$: $+ \\to -$ → **local maximum**. $f(-\\sqrt{2}) = -2\\sqrt{2} + 6\\sqrt{2} + 5 = 4\\sqrt{2} + 5$.
- $x = \\sqrt{2}$: $- \\to +$ → **local minimum**. $f(\\sqrt{2}) = 2\\sqrt{2} - 6\\sqrt{2} + 5 = 5 - 4\\sqrt{2}$.

**Answer:** Local max at $(-\\sqrt{2},\\, 4\\sqrt{2}+5)$; local min at $(\\sqrt{2},\\, 5-4\\sqrt{2})$."""

CHK1_HE = """גזירה: $f'(x) = 3x^2 - 6 = 3(x^2 - 2)$.

$f'(x) = 0$: $x^2 = 2 \\implies x = \\pm\\sqrt{2}$.

**טבלת סימנים:**
- $x < -\\sqrt{2}$: $x = -2$, $f'(-2) = 6 > 0$ (עולה).
- $-\\sqrt{2} < x < \\sqrt{2}$: $x = 0$, $f'(0) = -6 < 0$ (יורדת).
- $x > \\sqrt{2}$: $x = 2$, $f'(2) = 6 > 0$ (עולה).

**סיווג:**
- $x = -\\sqrt{2}$: $+ \\to -$ → **מקסימום מקומי**. $f(-\\sqrt{2}) = 4\\sqrt{2} + 5$.
- $x = \\sqrt{2}$: $- \\to +$ → **מינימום מקומי**. $f(\\sqrt{2}) = 5 - 4\\sqrt{2}$.

**תשובה:** מקס ב-$(-\\sqrt{2},\\, 4\\sqrt{2}+5)$; מין ב-$(\\sqrt{2},\\, 5-4\\sqrt{2})$."""

CHK2_EN = """Differentiate: $g'(x) = 3x^2 - 6x - 9 = 3(x^2 - 2x - 3) = 3(x-3)(x+1)$.

Critical points: $x = 3$ and $x = -1$.

**Sign chart:**
- $x < -1$: test $x = -2$, $g'(-2) = 12+12-9 = 15 > 0$ (increasing).
- $-1 < x < 3$: test $x = 0$, $g'(0) = -9 < 0$ (decreasing).
- $x > 3$: test $x = 4$, $g'(4) = 48-24-9 = 15 > 0$ (increasing).

**Classification:**
- $x = -1$: $+ \\to -$ → **local maximum**. $g(-1) = -1 - 3 + 9 + 2 = 7$.
- $x = 3$: $- \\to +$ → **local minimum**. $g(3) = 27 - 27 - 27 + 2 = -25$.

**Answer:** Local max at $(-1, 7)$; local min at $(3, -25)$."""

CHK2_HE = """גזירה: $g'(x) = 3x^2 - 6x - 9 = 3(x-3)(x+1)$.

נקודות קריטיות: $x = 3$ ו-$x = -1$.

**טבלת סימנים:**
- $x < -1$: $x = -2$, $g'(-2) = 15 > 0$ (עולה).
- $-1 < x < 3$: $x = 0$, $g'(0) = -9 < 0$ (יורדת).
- $x > 3$: $x = 4$, $g'(4) = 15 > 0$ (עולה).

**סיווג:**
- $x = -1$: $+ \\to -$ → **מקסימום מקומי**. $g(-1) = 7$.
- $x = 3$: $- \\to +$ → **מינימום מקומי**. $g(3) = -25$.

**תשובה:** מקס ב-$(-1, 7)$; מין ב-$(3, -25)$."""

METHOD_EN = """| Step | Action | Exam marks |
|------|--------|------------|
| 1 | State domain | 1 pt |
| 2 | Compute and simplify $f'(x)$ | 2 pts |
| 3 | Solve $f'(x)=0$; note undefined points | 2 pts |
| 4 | Build sign chart of $f'$ | 3 pts |
| 5 | Write increasing/decreasing intervals | 2 pts |
| 6 | Classify each critical point (max/min) | 2 pts |
| 7 | Compute $f(x_0)$ at extrema | 2 pts |
| 8 | For $[a,b]$: compare critical + endpoint values | 2 pts |

**Derivative shortcuts:**
- $(x^n)' = nx^{n-1}$
- $(e^x)' = e^x$; $(\\ln x)' = 1/x$
- Product: $(fg)' = f'g + fg'$
- Chain: outer derivative $\\times$ inner derivative

**Decision workflow:** (1) Differentiate and factor $f'$. (2) Find critical points. (3) One test point per interval. (4) Read sign changes for extrema. (5) Never skip computing $f(x_0)$.

**Exam tip:** Label your sign chart rows as $x$, $f'$, $f$ — graders look for this structure before reading your conclusions."""

METHOD_HE = """| שלב | פעולה | נקודות |
|-----|-------|--------|
| 1 | ציינו תחום | 1 נק' |
| 2 | חשבו ופשטו $f'(x)$ | 2 נק' |
| 3 | פתרו $f'(x)=0$; סמנו לא מוגדר | 2 נק' |
| 4 | בנו טבלת סימנים של $f'$ | 3 נק' |
| 5 | כתבו קטעי עלייה/ירידה | 2 נק' |
| 6 | סווגו כל נקודה קריטית | 2 נק' |
| 7 | חשבו $f(x_0)$ בקיצון | 2 נק' |
| 8 | ב-$[a,b]$: השוו קריטיות + קצוות | 2 נק' |

**קיצורי נגזרת:**
- $(x^n)' = nx^{n-1}$
- $(e^x)' = e^x$; $(\\ln x)' = 1/x$
- מכפלה: $(fg)' = f'g + fg'$
- שרשרת: נגזרת חיצונית $\\times$ פנימית

**זרימת עבודה:** (1) גזרו ופרקו $f'$. (2) מצאו קריטיות. (3) נקודת בדיקה בכל קטע. (4) קראו שינויי סימן. (5) אל תדלגו על $f(x_0)$.

**טיפ לבחינה:** סמנו שורות טבלה $x$, $f'$, $f$ — בוחנים מחפשים מבנה זה לפני המסקנות."""

PITFALL_EN = """**Mistake 1 — Treating every critical point as an extremum.**
When $f'(x_0) = 0$, the tangent is horizontal, but without a sign change there is no local max or min. Example: $f(x) = x^3$ has $f'(0) = 0$ but no extremum at $x = 0$.

**Mistake 2 — Skipping the sign chart.**
Listing critical points without interval testing loses most method marks. Always pick one test value per interval and record $f'$ sign explicitly.

**Mistake 3 — Reporting only the $x$-coordinate of an extremum.**
Bagrut questions ask for the **point** $(x_0, f(x_0))$. Computing $f(x_0)$ is a separate scoring step.

**Mistake 4 — Sign errors with negative test points.**
When testing $x = -1$ in $f'(x) = 3x(x-2)$, compute carefully: $3(-1)(-3) = 9 > 0$, not negative.

**Mistake 5 — Forgetting endpoints on closed intervals.**
Absolute max/min on $[a,b]$ requires evaluating $f(a)$ and $f(b)$ in addition to interior critical points."""

PITFALL_HE = """**טעות 1 — סיווג כל נקודה קריטית כקיצון.**
כש-$f'(x_0) = 0$, המשיק אופקי, אך בלי שינוי סימן אין מקסימום או מינימום. דוגמה: $f(x) = x^3$ עם $f'(0) = 0$ אך ללא קיצון ב-$x = 0$.

**טעות 2 — דילוג על טבלת סימנים.**
רשימת קריטיות בלי בדיקת קטעים מאבדת רוב נקודות השיטה. תמיד בחרו ערך בדיקה בכל קטע ורשמו סימן $f'$ במפורש.

**טעות 3 — דיווח רק על קואורדינטת $x$.**
שאלות בגרות מבקשות **נקודה** $(x_0, f(x_0))$. חישוב $f(x_0)$ הוא שלב ניקוד נפרד.

**טעות 4 — טעויות סימן בנקודות בדיקה שליליות.**
בבדיקת $x = -1$ ב-$f'(x) = 3x(x-2)$: $3(-1)(-3) = 9 > 0$, לא שלילי.

**טעות 5 — שכחת קצוות בקטע סגור.**
קיצון אבסולוטי ב-$[a,b]$ דורש חישוב $f(a)$ ו-$f(b)$ בנוסף לקריטיות פנימיות."""

WHY_EN = """Function analysis via $f'$ is the operational heart of differential calculus at 4 units. Every optimization word problem, every graph-sketching task, and every "find the maximum area" question reduces to: differentiate, find where the derivative vanishes, and classify with a sign chart.

**Recommended next topics:**
- `concept:optimization_word_problems` — modeling real scenarios then applying the same $f'$ workflow
- `concept:integrals_applications` — areas under curves whose shape you determined here

**Why it matters for exams:** Bagrut 4pt papers typically dedicate 12–18 points to monotonicity and extrema. Partial credit flows from labeled steps — a perfect derivative with a missing sign chart still loses 3–4 marks."""

WHY_HE = """חקירת פונקציה דרך $f'$ היא לב החשבון הדיפרנציאלי ב-4 יחידות. כל בעיית אופטימיזציה מילולית, כל שרטוט גרף, וכל "מצא שטח מקסימלי" מתמצים ל: גזור, מצא היכן הנגזרת מתאפסת, וסווג בטבלת סימנים.

**נושאים מומלצים להמשך:**
- `concept:optimization_word_problems` — מידול תרחישים ויישום אותה זרימת $f'$
- `concept:integrals_applications` — שטחים מתחת לעקומות שצורתן נקבעה כאן

**למה זה חשוב לבחינות:** בבגרות 4 יח' מוקדשות בדרך כלל 12–18 נקודות למונוטוניות וקיצון. נקודות חלקיות זורמות משלבים מתויגים — נגזרת מושלמת בלי טבלת סימנים עדיין מאבדת 3–4 נקודות."""

BEFORE_EN = """**Derivative rules (must be automatic):**
- Power: $(x^n)' = nx^{n-1}$
- Product: $(fg)' = f'g + fg'$
- Chain: $(f(g))' = f'(g) \\cdot g'$
- $(e^x)' = e^x$; $(\\ln x)' = 1/x$

**Analysis checklist:** Find $f'$ → solve $f'=0$ → sign chart → classify → compute $f$-values.

**Typical Bagrut 4pt patterns:**
1. Find and classify all local extrema with coordinates. (5–6 marks)
2. Determine intervals of increase/decrease. (3 marks)
3. Absolute max/min on a closed interval $[a,b]$. (4 marks)
4. Optimize a word problem using derivatives. (6–8 marks)

**Marking tips:** Show each derivative rule used. Draw the sign chart with three rows ($x$, $f'$, $f$). State conclusions in words: "$f$ is increasing on $(-\\infty, 0)$." """

BEFORE_HE = """**כללי נגזרת (חייבים להיות אוטומטיים):**
- חזקה: $(x^n)' = nx^{n-1}$
- מכפלה: $(fg)' = f'g + fg'$
- שרשרת: $(f(g))' = f'(g) \\cdot g'$
- $(e^x)' = e^x$; $(\\ln x)' = 1/x$

**רשימת חקירה:** מצאו $f'$ → פתרו $f'=0$ → טבלת סימנים → סיווג → ערכי $f$.

**דפוסי בגרות 4 יח' טיפוסיים:**
1. מציאת וסיווג כל הקיצון עם קואורדינטות. (5–6 נק')
2. קביעת קטעי עלייה/ירידה. (3 נק')
3. מקס/מין אבסולוטי בקטע סגור $[a,b]$. (4 נק')
4. אופטימיזציה של בעיית מילים. (6–8 נק')

**טיפים לניקוד:** הראו כל כלל נגזרת. ציירו טבלת סימנים עם שלוש שורות ($x$, $f'$, $f$). נסחו מסקנות במילים: "f עולה ב-$(-\\infty, 0)$." """

SUMMARY_EN = """**Core workflow:** Differentiate → find critical points → sign chart → classify extrema → compute $f(x_0)$.

- $f' > 0$: increasing; $f' < 0$: decreasing; $f' = 0$: critical point (verify sign change).
- $+ \\to -$: local maximum; $- \\to +$: local minimum; no change: not an extremum.
- Always state extrema as full coordinates $(x_0, f(x_0))$.
- On $[a,b]$: compare $f$ at critical points **and** endpoints for absolute extrema.
- For $e^x$ factors: factor out the positive exponential before sign analysis.

**Before submitting:** Re-read your sign chart — one wrong interval sign cascades into wrong monotonicity and wrong extrema classification."""

SUMMARY_HE = """**זרימה מרכזית:** גזירה → נקודות קריטיות → טבלת סימנים → סיווג קיצון → חישוב $f(x_0)$.

- $f' > 0$: עולה; $f' < 0$: יורדת; $f' = 0$: נקודה קריטית (אמתו שינוי סימן).
- $+ \\to -$: מקסימום מקומי; $- \\to +$: מינימום מקומי; ללא שינוי: לא קיצון.
- תמיד ציינו קיצון כקואורדינטות $(x_0, f(x_0))$.
- ב-$[a,b]$: השוו $f$ בקריטיות **ובקצוות** לקיצון אבסולוטי.
- בגורמי $e^x$: הוציאו את האקספוננט החיובי לפני ניתוח סימן.

**לפני הגשה:** קראו שוב טבלת סימנים — סימן שגוי בקטע אחד גורם למונוטוניות וסיווג שגויים."""

EXPLS = {
    1: fmt_expl(
        "Apply the power rule term by term: $(3x^4)' = 12x^3$, $(-2x^3)' = -6x^2$, $(x)' = 1$, and the constant $-5$ vanishes. Summing gives $f'(x) = 12x^3 - 6x^2 + 1$.",
        "Polynomial differentiation is the foundation — differentiate each term independently using $(x^n)' = nx^{n-1}$, then combine. There is no product or chain rule here because each term is a simple power.",
        "Forgetting that the derivative of a constant is zero, or mishandling the coefficient: $(3x^4)' = 3 \\cdot 4x^3 = 12x^3$, not $3x^3$.",
        "On Bagrut, write each term's derivative on a separate line before combining — partial credit is awarded for correct individual terms even if the final sum has an arithmetic slip.",
        "יישום כלל חזקה איבר-איבר: $(3x^4)' = 12x^3$, $(-2x^3)' = -6x^2$, $(x)' = 1$, והקבוע $-5$ נעלם. הסכום: $f'(x) = 12x^3 - 6x^2 + 1$.",
        "גזירת פולינום היא הבסיס — גוזרים כל איבר בנפרד ב-$(x^n)' = nx^{n-1}$ ומחברים. אין כלל מכפלה או שרשרת כי כל איבר הוא חזקה פשוטה.",
        "שכחה שנגזרת קבוע היא אפס, או טיפול שגוי במקדם: $(3x^4)' = 12x^3$, לא $3x^3$.",
        "בבגרות, כתבו נגזרת כל איבר בשורה נפרדת לפני חיבור — נקודות חלקיות לכל איבר נכון גם אם הסכום הסופי שגוי.",
    ),
    2: fmt_expl(
        "$f'(x) = 3x^2 - 12 = 3(x^2 - 4) = 3(x-2)(x+2)$. Setting $f' = 0$ gives $x = \\pm 2$. Both are critical points in the domain $\\mathbb{R}$.",
        "Critical points come from $f'(x) = 0$ or undefined. Here $f'$ is a polynomial, so only zeros matter. Factor completely before solving — difference of squares reveals both roots.",
        "Finding only $x = 2$ and missing $x = -2$, or confusing critical points with extrema (classification requires a sign chart later).",
        "When $f'(x) = 3(x^2 - 4)$, the factor $3$ never vanishes — only $x = \\pm 2$ matter. Write this explicitly to show you understand which factors contribute.",
        "$f'(x) = 3x^2 - 12 = 3(x-2)(x+2)$. $f' = 0$ נותן $x = \\pm 2$. שתיהן נקודות קריטיות ב-$\\mathbb{R}$, שכן $f'$ מוגדרת בכל מקום ומתאפסת בדיוק בשני ערכים אלה.",
        "נקודות קריטיות מ-$f'(x) = 0$ או לא מוגדר. כאן $f'$ פולינום, אז רק אפסים. פרקו לגמרי לפני פתרון — הפרש ריבועים $x^2-4$ חושף שני שורשים. זכרו: מציאת קריטיות היא רק שלב ביניים; סיווג מקסימום/מינימום דורש טבלת סימנים בשלב הבא.",
        "מציאת רק $x = 2$ והחמצת $x = -2$, או בלבול קריטיות עם קיצון (סיווג דורש טבלת סימנים).",
        "כש-$f'(x) = 3(x^2 - 4)$, הגורם $3$ לא מתאפס — רק $x = \\pm 2$ רלוונטיים. כתבו זאת במפורש כדי להראות שאתם מבינים אילו גורמים תורמים לפתרון.",
    ),
    3: fmt_expl(
        "Product rule with $f = x^2$ and $g = e^x$: $f'(x) = (2x)(e^x) + (x^2)(e^x) = xe^x(2 + x)$. Factoring $xe^x$ is the cleanest final form.",
        "Label the factors before applying $(fg)' = f'g + fg'$. For $x^n e^x$ problems, always factor $e^x$ afterward — it is positive everywhere and will drop out during sign analysis later.",
        "Applying the power rule to the whole product ($2xe^x$ only) and forgetting the $x^2 e^x$ term from differentiating $e^x$.",
        "After product rule, factor completely. Examiners prefer $xe^x(2+x)$ over the unfactored sum — it signals readiness for the sign chart in the next part.",
        "כלל מכפלה עם $f = x^2$ ו-$g = e^x$: $f'(x) = (2x)(e^x) + (x^2)(e^x) = 2xe^x + x^2 e^x = xe^x(2 + x)$. פירוק $xe^x$ הוא הצורה הנקייה והמועדפת לשלב הבא של חקירת הפונקציה.",
        "סמנו גורמים לפני $(fg)' = f'g + fg'$. בבעיות $x^n e^x$, תמיד פרקו $e^x$ אחרי היישום — הוא חיובי בכל $x$ ולכן ייעלם בניתוח סימן של $f'$ בשלב המונוטוניות. כתבו את שני האיברים לפני הפירוק.",
        "יישום כלל חזקה על כל המכפלה ($2xe^x$ בלבד) בלי האיבר $x^2 e^x$ מגזירת $e^x$ — זו הטעות הנפוצה ביותר בכלל מכפלה.",
        "אחרי כלל מכפלה, פרקו לגמרי. בוחנים מעדיפים $xe^x(2+x)$ על פני הסכום הלא מפורק — מסמן מוכנות לטבלת סימנים בחלק הבא של השאלה.",
    ),
    4: fmt_expl(
        "$f'(x) = 2x + 4$. At $x = 1$: $f'(1) = 6 > 0$, so $f$ is **increasing**. At $x = -3$: $f'(-3) = -2 < 0$, so $f$ is **decreasing**.",
        "To test monotonicity at a specific point, substitute into $f'$ — no sign chart needed for isolated points. Positive derivative means rising; negative means falling.",
        "Using the original function values ($f(1)$ vs $f(-3)$) instead of the derivative, or evaluating $f'(x)$ at the wrong points.",
        "This question type appears early in Bagrut investigations as a quick check. Compute $f'$ once, then two substitutions — under 30 seconds if fluent.",
        "$f'(x) = 2x + 4$. ב-$x = 1$: $f'(1) = 2 + 4 = 6 > 0$ — הפונקציה **עולה** בנקודה זו. ב-$x = -3$: $f'(-3) = -6 + 4 = -2 < 0$ — הפונקציה **יורדת** בנקודה זו. הסימן של הנגזרת קובע את כיוון העלייה/ירידה.",
        "לבדיקת מונוטוניות בנקודה ספציפית, הציבו ישירות ב-$f'$ — אין צורך בטבלת סימנים מלאה. נגזרת חיובית פירושה שהגרף עולה; שלילית — יורד. אל תשוו ערכי $f$ בנקודות שונות — זה בודק ערכים, לא כיוון.",
        "שימוש בערכי הפונקציה המקורית ($f(1)$ לעומת $f(-3)$) במקום הנגזרת, או הצבה בנקודות שגויות לאחר חישוב $f'$.",
        "סוג שאלה זה מופיע מוקדם בחקירות בגרות כבדיקה מהירה. חשבו $f'$ פעם אחת, שתי הצבות — פחות מ-30 שניות אם הכללים אוטומטיים.",
    ),
    5: fmt_expl(
        "$f'(x) = 6x^2 - 18x + 12 = 6(x-1)(x-2)$. Critical points: $x = 1, 2$. Sign change $+ \\to -$ at $x = 1$: local max, $f(1) = 2$. Sign change $- \\to +$ at $x = 2$: local min, $f(2) = 1$.",
        "Factor the quadratic derivative completely, build a three-interval sign chart, then read sign changes. Always compute $f(x_0)$ — the question asks for extrema, not just critical $x$-values.",
        "Swapping max and min (claiming $x = 1$ is a minimum), or stopping at critical points without computing $f(1) = 2$ and $f(2) = 1$.",
        "Verify by evaluating $f'$ at $x = 0$ (positive, between the roots from the left) and $x = 1.5$ (negative, between the roots) — two quick checks confirm the chart.",
        "$f'(x) = 6x^2 - 18x + 12 = 6(x-1)(x-2)$. נקודות קריטיות: $x = 1, 2$. שינוי סימן $+ \\to -$ ב-$x = 1$: **מקסימום מקומי**, $f(1) = 2 - 9 + 12 - 3 = 2$. שינוי $- \\to +$ ב-$x = 2$: **מינימום מקומי**, $f(2) = 16 - 36 + 24 - 3 = 1$.",
        "פרקו נגזרת ריבועית לגורמים, בנו טבלת סימנים עם שלושה קטעים ($(-\\infty,1)$, $(1,2)$, $(2,+\\infty)$), וקראו שינויי סימן בכל קריטית. תמיד חשבו $f(x_0)$ — השאלה מבקשת קיצון עם קואורדינטות, לא רק ערכי $x$.",
        "החלפת מקס ומין (טעות נפוצה כש-$x=1$ קטן מ-$x=2$), או עצירה בנקודות קריטיות בלי לחשב $f(1) = 2$ ו-$f(2) = 1$.",
        "אמתו ב-$f'(0) = 12 > 0$ (חיובי) ו-$f'(1.5) = -1.5 < 0$ (שלילי) — שתי בדיקות מהירות מאשרות את טבלת הסימנים לפני הגשה.",
    ),
    6: fmt_expl(
        "$f'(x) = x^2 - 4x + 3 = (x-1)(x-3)$. Critical: $x = 1, 3$. Increasing on $(-\\infty, 1) \\cup (3, +\\infty)$; decreasing on $(1, 3)$. Local max at $(1, 7/3)$; local min at $(3, 1)$.",
        "After factoring $f'$, the sign chart follows the same template as every cubic investigation. Compute $f(1) = 1/3 - 2 + 3 + 1 = 7/3$ and $f(3) = 9/3 - 18 + 9 + 1 = 1$ carefully — fraction arithmetic errors are common.",
        "Writing increasing interval as $(1, 3)$ instead of decreasing, or arithmetic slips in $f(1)$: $1/3 - 2 + 3 + 1 \\neq 7/3$ if you forget to convert $2$ to $6/3$.",
        "When the leading coefficient of $f'$ is positive (here $x^2$), the parabola $f'$ opens upward: positive outside the roots, negative between. Use this as a quick check.",
        "$f'(x) = (x-1)(x-3)$. קריטיות: $x = 1, 3$. עולה ב-$(-\\infty, 1) \\cup (3, +\\infty)$; יורדת ב-$(1, 3)$. מקס ב-$(1, 7/3)$; מין ב-$(3, 1)$.",
        "אחרי פירוק $f'$, טבלת הסימנים זהה לכל חקירת מעוקבית. חשבו $f(1) = 7/3$ ו-$f(3) = 1$ בזהירות — טעויות בשברים נפוצות.",
        "כתיבת $(1, 3)$ כעולה במקום יורדת, או טעויות ב-$f(1)$: $1/3 - 2 + 3 + 1$ דורש המרת $2$ ל-$6/3$.",
        "כשמקדם מוביל ב-$f'$ חיובי, פרבולת $f'$ פתוחה למעלה: חיובי מחוץ לשורשים, שלילי ביניהם. בדיקה מהירה.",
    ),
    7: fmt_expl(
        "$f'(x) = 1 - 4/x^2 = (x^2 - 4)/x^2$. Setting numerator zero: $x = \\pm 2$ (denominator $x^2 > 0$ for $x \\neq 0$). At $x = 2$: local min, $f(2) = 4$. At $x = -2$: local max, $f(-2) = -4$.",
        "For $f(x) = x + 4/x$, differentiate using $(1/x)' = -1/x^2$. The squared denominator in $f'$ is always positive, so only the numerator $x^2 - 4$ sets the sign. Split analysis: $x > 0$ branch and $x < 0$ branch.",
        "Forgetting domain restriction $x \\neq 0$, or treating $x = 2$ as a maximum because $f(2) = 4$ 'looks big' without checking the sign change ($- \\to +$ means minimum).",
        "Rational functions like $x + a/x$ appear frequently on 4pt exams. Memorize $f'(x) = 1 - a/x^2$ to save differentiation time.",
        "$f'(x) = 1 - 4/x^2 = (x^2 - 4)/x^2$. מונה אפס: $x = \\pm 2$ (מכנה $x^2 > 0$ לכל $x \\neq 0$). ב-$x = 2$: שינוי $- \\to +$ → **מינימום מקומי**, $f(2) = 2 + 2 = 4$. ב-$x = -2$: שינוי $+ \\to -$ → **מקסימום מקומי**, $f(-2) = -2 - 2 = -4$.",
        "ב-$f(x) = x + 4/x$, גזרו עם $(1/x)' = -1/x^2$. מכנה בריבוע ב-$f'$ תמיד חיובי ($x^2 > 0$), ולכן רק מונה $x^2 - 4$ קובע סימן. בדקו בנפרד את הענף $x > 0$ (מינימום ב-$x=2$) ואת $x < 0$ (מקסימום ב-$x=-2$).",
        "שכחת הגבלת תחום $x \\neq 0$, או סיווג $x = 2$ כמקסימום כי $f(2) = 4$ 'נראה גדול' בלי לבדוק שינוי סימן ($- \\to +$ = מינימום, לא מקסימום).",
        "פונקציות מהצורה $x + a/x$ מופיעות לעיתים קרובות ב-4 יח'. שיננו $f'(x) = 1 - a/x^2$ כדי לחסוך זמן גזירה בבחינה.",
    ),
    8: fmt_expl(
        "$f'(x) = -2x + 6 = 0 \\implies x = 3$ (critical point inside $[0, 5]$). Evaluate: $f(0) = -5$, $f(3) = 4$, $f(5) = 0$. The largest value is $4$ at $x = 3$ — absolute maximum.",
        "Closed-interval extrema require the **candidates theorem**: compare $f$ at all critical points inside the interval and at both endpoints. The derivative finds interior candidates; endpoints must never be skipped.",
        "Reporting $x = 3$ as the answer without comparing $f(0)$ and $f(5)$, or assuming the critical point is automatically the maximum without evaluating all three values.",
        "Draw a small table: $x$ | $0$ | $3$ | $5$; $f(x)$ | $-5$ | $4$ | $0$. Circle the largest — this format earns full marks on Bagrut interval problems.",
        "$f'(x) = -2x + 6 = 0 \\implies x = 3$ (קריטית ב-$[0, 5]$). $f(0) = -5$, $f(3) = 4$, $f(5) = 0$. הגדול ביותר: $4$ ב-$x = 3$ — מקסימום אבסולוטי.",
        "קיצון בקטע סגור דורש **משפט המועמדים**: השוו $f$ בכל קריטית פנימית ובשני הקצוות. הנגזרת מוצאת מועמדים פנימיים; קצוות אסור לדלג.",
        "תשובה $x = 3$ בלי השוואת $f(0)$ ו-$f(5)$, או הנחה שהקריטית היא אוטומטית מקסימום.",
        "ציירו טבלה: $x$ | $0$ | $3$ | $5$; $f(x)$ | $-5$ | $4$ | $0$. הקיפו את הגדול — פורמט זה מניב ניקוד מלא.",
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
            if "6x + 5" in body or "6x+5" in body:
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
