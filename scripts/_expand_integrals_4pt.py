#!/usr/bin/env python3
"""Expand integrals_4pt.json to Cursor expansion depth gates."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/integrals_4pt.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "worked_example": {"en": 130, "he": 110},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
    "before_exam": {"en": 90, "he": 75},
    "summary": {"en": 70, "he": 60},
}


def word_count(text: str) -> int:
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def hebrew_char_ratio(text: str) -> float:
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def hebrew_body_weak(body_he: str, body_en: str) -> bool:
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    if not en:
        return hebrew_char_ratio(he) < 0.12
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    if hebrew_char_ratio(he) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


EXPANSIONS = {
    "intro": {
        "body_en_md": """Imagine you know the **speed** of a car at every second. How do you find the **total distance** traveled? You add up all the tiny distances traveled in each tiny time slice — this is exactly what an integral does. At the 4-unit Bagrut level, integration is not abstract: it answers concrete questions about area, accumulation, and motion.

The definite integral $\\int_a^b f(x)\\,dx$ computes the **signed area** under the curve $y = f(x)$ from $x = a$ to $x = b$. When $f(x) \\ge 0$, this equals the geometric area. When $f$ dips below the axis, negative contributions cancel positive ones — a distinction that matters on every exam.

**Applications at 4pt level:**
- **Area** between two curves or under a single curve (with sign care).
- **Accumulation:** total water that flowed, total profit over time, displacement from velocity.
- **Parametric problems:** find $k$ such that an integral equals a given value.

Integration is the inverse of differentiation — and together they form **calculus**. The Fundamental Theorem of Calculus (FTC) is the bridge: once you know antiderivatives, definite integrals become algebra at the endpoints.""",
        "body_he_md": """דמיינו שאתם יודעים את **המהירות** של מכונית בכל שנייה. איך מוצאים את **המרחק הכולל** שנסעה? מסכמים את כל המרחקים הקטנים שנסעה בכל פרק זמן קטן — זה בדיוק מה שאינטגרל עושה. ברמת בגרות 4 יח', אינטגרציה אינה מופשטת: היא עונה על שאלות קונקרטיות על שטח, הצטברות ותנועה.

האינטגרל המסוים $\\int_a^b f(x)\\,dx$ מחשב את **השטח המכוון** מתחת לעקומה $y = f(x)$ מ-$x = a$ עד $x = b$. כאשר $f(x) \\ge 0$, זה שווה לשטח הגיאומטרי. כאשר $f$ יורדת מתחת לציר, תרומות שליליות מבטלות חיוביות — הבחנה שחוזרת בכל בחינה.

**יישומים ברמת 4 יח':**
- **שטח** בין שתי עקומות או מתחת לעקומה אחת (עם תשומת לב לסימן).
- **הצטברות:** כמות מים שזרמה, רווח כולל לאורך זמן, הזזה ממהירות.
- **בעיות פרמטריות:** מציאת $k$ כך שאינטגרל שווה לערך נתון.

אינטגרציה היא ההיפך של גזירה — ויחד הן מהוות **חשבון אינפיניטסימלי**. משפט היסוד של החשבון הוא הגשר: ברגע שיודעים פונקציות קדומות, אינטגרלים מסוימים הופכים לאלגברה בנקודות הקצה.""",
    },
    "definition": {
        "body_en_md": """**Antiderivative (indefinite integral):** $F(x)$ is an antiderivative of $f(x)$ if $F'(x) = f(x)$. Because differentiation kills constants, every antiderivative differs by $+C$:
$$\\int f(x)\\,dx = F(x) + C$$

**Basic antiderivative rules (memorize for Bagrut):**
- $\\int x^n\\,dx = \\dfrac{x^{n+1}}{n+1} + C$ (for $n \\ne -1$)
- $\\int e^x\\,dx = e^x + C$
- $\\int \\frac{1}{x}\\,dx = \\ln|x| + C$ (absolute value matters when domain crosses zero)
- $\\int \\cos x\\,dx = \\sin x + C$, $\\int \\sin x\\,dx = -\\cos x + C$
- $\\int k\\,dx = kx + C$ (constant factor)

**Linearity:** $\\int [af(x) + bg(x)]\\,dx = a\\int f\\,dx + b\\int g\\,dx$ — integrate term by term.

**Definite integral — Fundamental Theorem (Part 2):**
$$\\int_a^b f(x)\\,dx = F(b) - F(a) = \\left[F(x)\\right]_a^b$$
where $F$ is **any** antiderivative of $f$. The constant $C$ cancels in the difference.

**Area between two curves** on $[a,b]$ where $f(x) \\ge g(x)$:
$$\\text{Area} = \\int_a^b [f(x) - g(x)]\\,dx$$
Always subtract **top minus bottom**. If curves cross inside the interval, split at intersection points.

**Notation:** Write $\\left[F(x)\\right]_a^b$ or $F(b) - F(a)$ — both are accepted on Bagrut. The vertical bar notation reminds you to substitute the upper limit first, then subtract the lower.""",
        "body_he_md": """**פונקציה קדומה (אינטגרל לא-מסוים):** $F(x)$ היא פונקציה קדומה של $f(x)$ אם $F'(x) = f(x)$. מכיוון שגזירה מבטלת קבועים, כל פונקציה קדומה שונה ב-$+C$:
$$\\int f(x)\\,dx = F(x) + C$$

**כללי פונקציות קדומות בסיסיים (לשנן לבגרות):**
- $\\int x^n\\,dx = \\dfrac{x^{n+1}}{n+1} + C$ (עבור $n \\ne -1$)
- $\\int e^x\\,dx = e^x + C$
- $\\int \\frac{1}{x}\\,dx = \\ln|x| + C$ (ערך מוחלט חשוב כשהתחום חוצה אפס)
- $\\int \\cos x\\,dx = \\sin x + C$, $\\int \\sin x\\,dx = -\\cos x + C$
- $\\int k\\,dx = kx + C$ (קבוע)

**לינאריות:** $\\int [af(x) + bg(x)]\\,dx = a\\int f\\,dx + b\\int g\\,dx$ — מאינטגרלים איבר-איבר.

**אינטגרל מסוים — משפט היסוד (חלק 2):**
$$\\int_a^b f(x)\\,dx = F(b) - F(a) = \\left[F(x)\\right]_a^b$$
כאשר $F$ היא **כל** פונקציה קדומה של $f$. הקבוע $C$ מתבטל בהפרש.

**שטח בין שתי עקומות** על $[a,b]$ כאשר $f(x) \\ge g(x)$:
$$\\text{שטח} = \\int_a^b [f(x) - g(x)]\\,dx$$
תמיד **עליונה פחות תחתונה**. אם העקומות נחתכות בתוך הקטע, פצלו בנקודות החיתוך.

**סימון:** כתבו $\\left[F(x)\\right]_a^b$ או $F(b) - F(a)$ — שניהם מתקבלים בבגרות. סימון הסוגריים מזכיר להציב תחילה את הגבול העליון, ואז להחסיר את התחתון.""",
    },
    "theory": {
        "body_en_md": """The definite integral gives **signed area** — if $f(x) < 0$, the contribution is negative. This is correct for physics (net displacement) but wrong for geometry (area must be positive).

**For geometric (always positive) area:** split at x-intercepts and take absolute values:
$$\\text{Area} = \\int_a^c |f(x)|\\,dx + \\int_c^b |f(x)|\\,dx$$
where $c$ is an interior root. Alternatively, integrate piecewise and add absolute values of each piece.

**Example — signed vs geometric:**
$\\int_{-1}^{1} x\\,dx = \\left[\\frac{x^2}{2}\\right]_{-1}^{1} = \\frac{1}{2} - \\frac{1}{2} = 0$ (signed area cancels).
But the geometric area = $\\frac{1}{2} + \\frac{1}{2} = 1$ because the curve is below the x-axis for $x < 0$ and above for $x > 0$.

**Area between curves — full procedure:**
1. Find intersections: solve $f(x) = g(x)$ for boundary $x$-values.
2. Pick a test point in each sub-interval to determine which curve is on top.
3. Integrate $\\int (\\text{top} - \\text{bottom})\\,dx$ on each piece.
4. If curves cross, split at each crossing — never integrate $f - g$ blindly across a sign change.

**Motion interpretation:** $\\int_{t_1}^{t_2} v(t)\\,dt$ = displacement (signed). Total distance = $\\int |v(t)|\\,dt$ split where $v$ changes sign. This mirrors the area/sign distinction exactly.""",
        "body_he_md": """האינטגרל המסוים נותן **שטח מכוון** — אם $f(x) < 0$, התרומה שלילית. זה נכון לפיזיקה (הזזה נטו) אך שגוי לגיאומטריה (שטח חייב להיות חיובי).

**לשטח גיאומטרי (תמיד חיובי):** פצלו בנקודות חיתוך עם ציר $x$ וקחו ערכים מוחלטים:
$$\\text{שטח} = \\int_a^c |f(x)|\\,dx + \\int_c^b |f(x)|\\,dx$$
כאשר $c$ הוא שורש פנימי. לחלופין, אינטגרלו קטע-קטע והוסיפו ערכים מוחלטים.

**דוגמה — מכוון לעומת גיאומטרי:**
$\\int_{-1}^{1} x\\,dx = \\left[\\frac{x^2}{2}\\right]_{-1}^{1} = 0$ (שטח מכוון מתבטל).
אבל שטח גיאומטרי = $\\frac{1}{2} + \\frac{1}{2} = 1$ כי העקומה מתחת לציר $x$ עבור $x < 0$ ומעליו עבור $x > 0$.

**שטח בין עקומות — תהליך מלא:**
1. מצאו חיתוכים: פתרו $f(x) = g(x)$ לקבלת גבולות $x$.
2. בחרו נקודת בדיקה בכל תת-קטע כדי לקבוע מי למעלה.
3. אינטגרלו $\\int (\\text{עליונה} - \\text{תחתונה})\\,dx$ בכל קטע.
4. אם העקומות נחתכות, פצלו בכל חיתוך — לעולם אל תאינטגרלו $f - g$ בעיוורון על שינוי סימן.

**פרשנות תנועה:** $\\int_{t_1}^{t_2} v(t)\\,dt$ = הזזה (מכוונת). מרחק כולל = $\\int |v(t)|\\,dt$ עם פיצול כש-$v$ משנה סימן. זה משקף בדיוק את הבחנה שטח/סימן.""",
    },
}

WE1 = {
    "body_en_md": """**Compute:** $\\displaystyle\\int_0^3 x^2\\,dx$

### Move 1 — Find an antiderivative
The power rule for integration gives $F(x) = \\dfrac{x^3}{3}$ because $\\dfrac{d}{dx}\\left(\\dfrac{x^3}{3}\\right) = x^2$. Verify by differentiating before moving on — this catches sign errors early.

### Move 2 — Apply the Fundamental Theorem
$$\\int_0^3 x^2\\,dx = F(3) - F(0) = \\frac{3^3}{3} - \\frac{0^3}{3} = \\frac{27}{3} - 0 = 9$$
Write the bracket notation explicitly: $\\left[\\dfrac{x^3}{3}\\right]_0^3$. Examiners award marks for showing $F(b) - F(a)$ even when arithmetic is trivial.

### Move 3 — Interpret
Since $x^2 \\ge 0$ on $[0,3]$, the signed integral equals the geometric area. The region under $y = x^2$ from $x = 0$ to $x = 3$ has area $9$ square units — a parabolic segment that grows faster than a triangle would.

**Self-check:** Differentiate $\\dfrac{x^3}{3}$ — you get $x^2$, confirming the antiderivative. Substitute $x = 3$ and $x = 0$ again if unsure. Compare to a rectangle $3 \\times 3 = 9$ as an upper bound sanity check.

**Answer:** $\\displaystyle\\int_0^3 x^2\\,dx = 9$.""",
    "body_he_md": """**חשבו:** $\\displaystyle\\int_0^3 x^2\\,dx$

### צעד 1 — מציאת הפונקציה הקדומה
כלל החזקה לאינטגרציה נותן $F(x) = \\dfrac{x^3}{3}$ כי $\\dfrac{d}{dx}\\left(\\dfrac{x^3}{3}\\right) = x^2$. אמתו בגזירה לפני שממשיכים — זה תופס טעויות סימן מוקדם.

### צעד 2 — שימוש במשפט היסוד
$$\\int_0^3 x^2\\,dx = F(3) - F(0) = \\frac{27}{3} - 0 = 9$$
כתבו במפורש סימון סוגריים: $\\left[\\dfrac{x^3}{3}\\right]_0^3$. בוחנים נותנים נקודות על הצגת $F(b) - F(a)$ גם כשהחשבון פשוט.

### צעד 3 — פרשנות
מכיוון ש-$x^2 \\ge 0$ ב-$[0,3]$, האינטגרל המכוון שווה לשטח הגיאומטרי. השטח מתחת ל-$y = x^2$ מ-$x = 0$ עד $x = 3$ הוא $9$ יחידות רבועיות.

**בדיקה עצמית:** גזרו $\\dfrac{x^3}{3}$ — תקבלו $x^2$, מאמת את הפונקציה הקדומה. הציבו $x = 3$ ו-$x = 0$ שוב אם אינכם בטוחים.

**תשובה:** $\\displaystyle\\int_0^3 x^2\\,dx = 9$.""",
}

CP1 = {
    "checkpoint_solution_en": """**(a)** Antiderivative: $F(x) = x^2 + 3x$ (integrate $2x$ to $x^2$ and $3$ to $3x$).
$$\\int_1^4 (2x + 3)\\,dx = \\left[x^2 + 3x\\right]_1^4 = (16 + 12) - (1 + 3) = 28 - 4 = 24$$

**(b)** Antiderivative: $F(x) = e^x$.
$$\\int_0^1 e^x\\,dx = \\left[e^x\\right]_0^1 = e^1 - e^0 = e - 1 \\approx 1.718$$

**Check:** Both integrands are positive on their intervals, so answers are positive areas — a quick sanity test.""",
    "checkpoint_solution_he": """**(א)** פונקציה קדומה: $F(x) = x^2 + 3x$ (אינטגרל של $2x$ הוא $x^2$ ושל $3$ הוא $3x$).
$$\\int_1^4 (2x + 3)\\,dx = \\left[x^2 + 3x\\right]_1^4 = (16 + 12) - (1 + 3) = 28 - 4 = 24$$

**(ב)** פונקציה קדומה: $F(x) = e^x$.
$$\\int_0^1 e^x\\,dx = \\left[e^x\\right]_0^1 = e - 1 \\approx 1.718$$

**בדיקה:** שני המintegrandים חיוביים בקטעים שלהם, לכן התשובות הן שטחים חיוביים — אימות מהיר.""",
}

WE2 = {
    "body_en_md": """**Find the area between $f(x) = x^2$ and $g(x) = 2x$.**

### Move 1 — Intersection points
Set $x^2 = 2x$:
$$x^2 - 2x = 0 \\implies x(x-2) = 0 \\implies x = 0 \\text{ or } x = 2$$
These $x$-values bound the enclosed region.

### Move 2 — Determine which curve is on top
Test at $x = 1$: $g(1) = 2$ and $f(1) = 1$, so $g(x) \\ge f(x)$ on $[0,2]$. The line $y = 2x$ lies above the parabola $y = x^2$ in this interval.

### Move 3 — Integrate top minus bottom
Antiderivative of $2x - x^2$ is $x^2 - \\dfrac{x^3}{3}$. Evaluate:
$$\\text{Area} = \\int_0^2 (2x - x^2)\\,dx = \\left[x^2 - \\frac{x^3}{3}\\right]_0^2$$
$$= \\left(4 - \\frac{8}{3}\\right) - 0 = \\frac{12}{3} - \\frac{8}{3} = \\frac{4}{3}$$

**Self-check:** The integrand $2x - x^2$ is non-negative on $[0,2]$ (it is zero at endpoints and positive at $x = 1$), so the integral value equals the geometric area. A quick sketch shows a lens-shaped region between the line and parabola.

**Answer:** The area between the two curves is $\\dfrac{4}{3}$ square units. Sketch the parabola and line to confirm the region is bounded and your top/bottom choice is correct.""",
    "body_he_md": """**מצאו את השטח בין $f(x) = x^2$ ו-$g(x) = 2x$.**

### צעד 1 — נקודות חיתוך
השוו $x^2 = 2x$:
$$x^2 - 2x = 0 \\implies x(x-2) = 0 \\implies x = 0 \\text{ או } x = 2$$
ערכי $x$ אלה מגבילים את האזור הכלוא.

### צעד 2 — קביעת מי למעלה
בדיקה ב-$x = 1$: $g(1) = 2$ ו-$f(1) = 1$, לכן $g(x) \\ge f(x)$ ב-$[0,2]$. הישר $y = 2x$ מעל הפרבולה $y = x^2$ בקטע זה.

### צעד 3 — אינטגרל עליונה פחות תחתונה
$$\\text{שטח} = \\int_0^2 (2x - x^2)\\,dx = \\left[x^2 - \\frac{x^3}{3}\\right]_0^2 = \\frac{4}{3}$$

**בדיקה עצמית:** ה-integrand $2x - x^2$ לא-שלילי ב-$[0,2]$ (אפס בקצוות, חיובי ב-$x = 1$), לכן ערך האינטegral שווה לשטח הגיאומטרי.

**תשובה:** השטח בין שתי העקומות הוא $\\dfrac{4}{3}$ יחידות רבועיות. סרטטו את הפרבולה והישר כדי לאמת שהאזור חסום ובחירת עליונה/תחתונה נכונה.""",
}

CP2 = {
    "checkpoint_solution_en": """**Step 1 — Intersections:** $x^2 - 4 = -x^2 + 4$ gives $2x^2 = 8$, so $x = \\pm 2$.

**Step 2 — Top curve:** At $x = 0$, $g(0) = 4$ and $f(0) = -4$, so $g(x) \\ge f(x)$ on $[-2, 2]$.

**Step 3 — Integrate:**
$$\\text{Area} = \\int_{-2}^{2} \\big[(-x^2 + 4) - (x^2 - 4)\\big]\\,dx = \\int_{-2}^{2} (8 - 2x^2)\\,dx$$
$$= \\left[8x - \\frac{2x^3}{3}\\right]_{-2}^{2} = \\left(16 - \\frac{16}{3}\\right) - \\left(-16 + \\frac{16}{3}\\right) = 32 - \\frac{32}{3} = \\frac{64}{3}$$

The region is symmetric about the $y$-axis; you could also compute $2\\int_0^2 (8 - 2x^2)\\,dx$.""",
    "checkpoint_solution_he": """**שלב 1 — חיתוכים:** $x^2 - 4 = -x^2 + 4$ נותן $2x^2 = 8$, כלומר $x = \\pm 2$.

**שלב 2 — עקומה עליונה:** ב-$x = 0$, $g(0) = 4$ ו-$f(0) = -4$, לכן $g(x) \\ge f(x)$ ב-$[-2, 2]$.

**שלב 3 — אינטegral:**
$$\\text{שטח} = \\int_{-2}^{2} (8 - 2x^2)\\,dx = \\left[8x - \\frac{2x^3}{3}\\right]_{-2}^{2} = 32 - \\frac{32}{3} = \\frac{64}{3}$$

האזור סימטרי לגבי ציר $y$; אפשר גם $2\\int_0^2 (8 - 2x^2)\\,dx$.""",
}

WE3 = {
    "body_en_md": """**Problem:** Find $k > 0$ such that $\\displaystyle\\int_0^k (3x^2 - 1)\\,dx = 6$.

### Move 1 — Evaluate the integral in terms of $k$
$$\\int_0^k (3x^2 - 1)\\,dx = \\left[x^3 - x\\right]_0^k = (k^3 - k) - 0 = k^3 - k$$

### Move 2 — Set up the equation
$$k^3 - k = 6 \\implies k^3 - k - 6 = 0$$

### Move 3 — Solve using rational root test
Try integer roots of $6$: $k = 2$ gives $8 - 2 - 6 = 0$ ✓.
Factor by grouping or synthetic division: $k^3 - k - 6 = (k - 2)(k^2 + 2k + 3)$.
The quadratic has $\\Delta = 4 - 12 < 0$, so no other real roots. Since $k > 0$, the only solution is $k = 2$.

**Verify:** $\\int_0^2 (3x^2 - 1)\\,dx = [x^3 - x]_0^2 = 8 - 2 = 6$ ✓. Differentiating $x^3 - x$ gives $3x^2 - 1$, confirming the antiderivative setup.

**Exam note:** If no integer root works, use the cubic formula or state that the exam would adjust the target value. On 4-unit Bagrut, integer answers are the norm for parameter problems.

**Answer:** $k = 2$. Bagrut problems choose the right-hand side so the cubic has a clean integer root — always test small positive integers first.""",
    "body_he_md": """**בעיה:** מצאו $k > 0$ כך ש-$\\displaystyle\\int_0^k (3x^2 - 1)\\,dx = 6$.

### צעד 1 — חישוב האינטגרל ב-$k$
$$\\int_0^k (3x^2 - 1)\\,dx = \\left[x^3 - x\\right]_0^k = k^3 - k$$

### צעד 2 — הצבת המשוואה
$$k^3 - k = 6 \\implies k^3 - k - 6 = 0$$

### צעד 3 — פתרון עם בדיקת שורשים רציונליים
נסו $k = 2$: $8 - 2 - 6 = 0$ ✓.
פירוק: $k^3 - k - 6 = (k - 2)(k^2 + 2k + 3)$.
המשוואה הריבועית עם $\\Delta < 0$ — אין שורשים ממשיים נוספים. מאחר $k > 0$, הפתרון היחיד הוא $k = 2$.

**אימות:** $\\int_0^2 (3x^2 - 1)\\,dx = 8 - 2 = 6$ ✓. גזירה של $x^3 - x$ נותנת $3x^2 - 1$, מאמתת את הגדרת הפונקציה הקדומה.

**הערה לבחינה:** אם אין שורש שלם, משתמשים בנוסחת המישור השלישי — אך בבגרות 4 יח' התשובות שלמות בדרך כלל.

**תשובה:** $k = 2$. בבגרות בוחרים את הצד הימני כך שלמישור השלישי יש שורש שלם — תמיד בדקו שלמים חיוביים קטנים ראשונים.""",
}

METHOD = {
    "body_en_md": """| Task | Method |
|------|--------|
| Antiderivative of $x^n$ | $\\dfrac{x^{n+1}}{n+1} + C$ (check $n \\ne -1$) |
| Polynomial antiderivative | Integrate term by term; do not forget $+C$ |
| Definite integral | Find $F$, then $F(b) - F(a)$ with bracket notation |
| Area under curve (all positive) | $\\int_a^b f(x)\\,dx$ directly |
| Area under curve (crosses axis) | Split at roots; add absolute values of each piece |
| Area between curves | Intersections → test point → $\\int (\\text{top} - \\text{bottom})\\,dx$ |
| Parametric integral | Evaluate integral, set equal to target, solve algebraically |
| Motion: displacement | $\\int v\\,dt$ (signed); distance = $\\int |v|\\,dt$ split at zeros |

**Strategy:** Read the question type first — indefinite, definite, area, or parameter. Sketch when geometry is involved. Write $[F(x)]_a^b$ before substituting numbers; partial credit depends on showing FTC setup.""",
    "body_he_md": """| משימה | שיטה |
|-------|------|
| פונקציה קדומה של $x^n$ | $\\dfrac{x^{n+1}}{n+1} + C$ (בדקו $n \\ne -1$) |
| פונקציה קדומה של פולינום | אינטגרלו איבר-איבר; אל תשכחו $+C$ |
| אינטגרל מסוים | מצאו $F$, אז $F(b) - F(a)$ עם סימון סוגריים |
| שטח מתחת לעקומה (הכל חיובי) | $\\int_a^b f(x)\\,dx$ ישירות |
| שטח מתחת לעקומה (חוצה ציר) | פצלו בשורשים; הוסיפו ערכים מוחלטים |
| שטח בין עקומות | חיתוכים → נקודת בדיקה → $\\int (\\text{עליונה} - \\text{תחתונה})\\,dx$ |
| אינטגרל פרמטרי | חשבו אינטegral, השוו ליעד, פתרו אלגברית |
| תנועה: הזזה | $\\int v\\,dt$ (מכוון); מרחק = $\\int |v|\\,dt$ עם פיצול |

**אסטרטגיה:** קראו תחילה את סוג השאלה — לא-מסוים, מסוים, שטח או פרמטר. סרטטו כשיש גיאומטריה. כתבו $[F(x)]_a^b$ לפני הצבת מספרים; נקודות חלקיות תלויות בהצגת משפט היסוד.""",
}

PITFALL = {
    "body_en_md": """**Mistake 1 — Forgetting $+C$ in indefinite integrals.**
Every antiderivative differs by a constant. Omitting $+C$ on $\\int f(x)\\,dx$ loses marks even when the rest is correct. Definite integrals do not need $+C$ because it cancels in $F(b) - F(a)$.

**Mistake 2 — Using signed area instead of geometric area.**
If $f(x) < 0$ on part of $[a,b]$, the definite integral subtracts that region. For **area**, split at roots and integrate $|f(x)|$ or take absolute value of each piece. A classic trap: $\\int_{-1}^{1} x\\,dx = 0$ but geometric area $= 1$.

**Mistake 3 — Wrong limits or wrong top-minus-bottom for area between curves.**
Limits must be intersection $x$-values, not arbitrary bounds from the question stem. Always test which curve is on top — swapping gives a negative area. If curves cross inside $[a,b]$, split at each crossing before integrating.""",
    "body_he_md": """**טעות 1 — שכחת $+C$ באינטegralים לא-מסוימים.**
כל פונקציה קדומה שונה בקבוע. השמטת $+C$ ב-$\\int f(x)\\,dx$ מפסידה נקודות גם כשהשאר נכון. באינטegralים מסוימים אין צורך ב-$+C$ כי הוא מתבטל ב-$F(b) - F(a)$.

**טעות 2 — שימוש בשטח מכוון במקום גיאומטרי.**
אם $f(x) < 0$ בחלק מ-$[a,b]$, האינטegral המסוים מחסיר את האזור. ל**שטח**, פצלו בשורשים ואינטegralו $|f(x)|$ או קחו ערך מוחלט לכל קטע. מלכודת קלאסית: $\\int_{-1}^{1} x\\,dx = 0$ אך שטח גיאומטרי $= 1$.

**טעות 3 — גבולות שגויים או עליונה-תחתונה הפוכה לשטח בין עקומות.**
הגבולות חייבים להיות קואורדינטות $x$ של חיתוכים, לא גבולות שרירותיים מהניסוח. תמיד בדקו מי למעלה — החלפה נותנת שטח שלילי. אם העקומות נחתכות ב-$[a,b]$, פצלו בכל חיתוך לפני האינטegral.""",
}

WHY = {
    "body_en_md": """Integration connects directly to **derivatives** (previous unit), **function investigation** (areas under graphs), and **physics** (work, displacement, accumulation). On the Bagrut 4-unit exam, integral questions typically appear alongside derivative problems — examiners expect you to move fluently between $F'(x) = f(x)$ and $\\int f\\,dx$.

**Why it matters for exams:** Area-between-curves and parametric-integral questions combine algebra, graph reading, and FTC in one problem — exactly the multi-step reasoning Bagrut rewards. Mastering signed vs geometric area prevents the most common point loss on Question 8-style problems.

**Cross-subject link:** In physics, $\\int v\\,dt$ gives displacement and $\\int F\\,dx$ gives work — the same FTC machinery with different units.""",
    "body_he_md": """אינטגרציה מתחברת ישירות ל**נגזרות** (יחידה קודמת), **חקירת פונקציות** (שטחים מתחת לגרפים) ו**פיזיקה** (עבודה, הזזה, הצטברות). בבגרות 4 יח', שאלות אינטegral מופיעות לצד בעיות נגזרות — הבוחנים מצפים למעבר חלק בין $F'(x) = f(x)$ ל-$\\int f\\,dx$.

**למה זה חשוב לבחינות:** שטח בין עקומות ואינטegral פרמטרי משלבים אלגברה, קריאת גרף ומשפט היסוד — בדיוק ההיגיון הרב-שלבי שבגרות מעריכה. שליטה בשטח מכוון לעומת גיאומטרי מונעת את אובדן הנקודות הנפוץ ביותר.

**קישור בין-מקצועי:** בפיזיקה, $\\int v\\,dt$ נותן הזזה ו-$\\int F\\,dx$ נותן עבודה — אותו מנגנון משפט היסוד עם יחידות שונות.""",
}

BEFORE_EXAM = {
    "body_en_md": """**Key formulas:**
- $\\int x^n\\,dx = \\dfrac{x^{n+1}}{n+1} + C$ (n ≠ −1)
- $\\int e^x\\,dx = e^x + C$; $\\int \\frac{1}{x}\\,dx = \\ln|x| + C$
- Fundamental Theorem: $\\int_a^b f(x)\\,dx = F(b) - F(a)$
- Area between curves: $\\int_a^b (f-g)\\,dx$ (top minus bottom)

**Typical Bagrut 4pt patterns:**
1. Compute a definite integral. (3–4 marks)
2. Find area between two curves. (5–6 marks)
3. Find parameter from integral equation. (4–5 marks)

**Marking tips:** Always write $F(b) - F(a)$ in bracket notation $[F(x)]_a^b$. Show each computation. For area, specify which function is on top. Check whether the question asks for signed integral or geometric area — underline that phrase in the stem before calculating.""",
    "body_he_md": """**נוסחאות מרכזיות:**
- $\\int x^n\\,dx = \\dfrac{x^{n+1}}{n+1} + C$ (n ≠ −1)
- $\\int e^x\\,dx = e^x + C$; $\\int \\frac{1}{x}\\,dx = \\ln|x| + C$
- משפט היסוד: $\\int_a^b f(x)\\,dx = F(b) - F(a)$
- שטח בין עקומות: $\\int_a^b (f-g)\\,dx$ (עליונה פחות תחתונה)

**דפוסי שאלות טיפוסיות בבגרות 4 יח':**
1. חישוב אינטegral מסוים. (3–4 נקודות)
2. מציאת שטח בין שתי עקומות. (5–6 נקודות)
3. מציאת פרמטר ממשוואת אינטegral. (4–5 נקודות)

**טיפים לניקוד:** תמיד כתבו $F(b) - F(a)$ בסימון סוגריים $[F(x)]_a^b$. הציגו כל חישוב. לשטח, ציינו איזו פונקציה למעלה. בדקו אם השאלה מבקשת אינטegral מכוון או שטח גיאומטרי — סמנו את הביטוי לפני החישוב.""",
}

SUMMARY = {
    "body_en_md": """- Antiderivative: $F(x)$ with $F'(x) = f(x)$; write with $+C$ for indefinite integrals.
- Definite integral = $F(b) - F(a)$; this gives signed area under the curve.
- For geometric area: use absolute values or split at roots where $f$ changes sign.
- Area between curves: find intersections first, then integrate $\\int (\\text{top} - \\text{bottom})\\,dx$ on each piece.
- Parametric integral: set the integral equal to the target and solve algebraically.
- The Fundamental Theorem of Calculus connects derivatives and integrals — master both directions.""",
    "body_he_md": """- פונקציה קדומה: $F(x)$ עם $F'(x) = f(x)$; כתבו עם $+C$ באינטegralים לא-מסוימים.
- אינטegral מסוים = $F(b) - F(a)$; נותן שטח מכוון מתחת לעקומה.
- לשטח גיאומטרי: השתמשו בערכים מוחלטים או פצלו בשורשים כש-$f$ משנה סימן.
- שטח בין עקומות: מצאו חיתוכים ראשית, ואז אינטegralו $\\int (\\text{עליונה} - \\text{תחתונה})\\,dx$ בכל קטע.
- אינטegral פרמטרי: השוו את האינטegral ליעד ופתרו אלגברית.
- משפט היסוד מחבר נגזרות ואינטegralים — שלטו בשני הכיוונים.""",
}

EXAM_HE_FOLLOWUP = "\n\n**טיפ נוסף לבחינה:** כתבו את הפונקציה הקדומה $F(x)$ לפני הצבת הגבולות — נקודות שיטה חשובות גם כשיש טעות חשבונית. בסוף, גזרו או הציבו לאימות מהיר."
EXAM_EN_FOLLOWUP = "\n\n**Exam follow-up:** Write the antiderivative $F(x)$ before substituting bounds — method marks matter even when arithmetic slips. Re-substitute or differentiate once to verify."

HE_WE1_EXTRA = "\n\n**הערה:** דוגמה זו מדגימה את כלל החזקה ואת משפט היסוד יחד — תבנית שחוזרת ברוב שאלות האינטegral המסוים בבגרות 4 יח'."
EN_WE1_EXTRA = "\n\n**Note:** This basic power-rule example is the FTC template used throughout the 4-unit integral unit."
EN_WE2_EXTRA = "\n\n**Note:** This template — intersections, top-minus-bottom, FTC — appears on nearly every area-between-curves Bagrut question at the 4-unit level."
HE_WE2_EXTRA = "\n\n**הערה:** תבנית זו — חיתוכים, עליונה פחות תחתונה, משפט היסוד — חוזרת כמעט בכל שאלת שטח בין עקומות בבגרות."
EN_WE3_EXTRA = "\n\n**Note:** Parametric integral problems always follow: integrate symbolically, equate, solve, verify by re-substitution."
HE_WE3_EXTRA = "\n\n**הערה:** בעיות אינטegral פרמטרי תמיד: אינטegral סימbolי, השוואה, פתרון, אימות בהצבה חוזרת."

EXPLANATIONS = [
    {
        "en": """**Why this is correct:**
Integrate term by term: $\\int 4x^3\\,dx = x^4$, $\\int -2x\\,dx = -x^2$, $\\int 7\\,dx = 7x$. Sum with $+C$: $F(x) = x^4 - x^2 + 7x + C$.

**How to think about it:**
Antiderivatives reverse the power rule. Each term $ax^n$ becomes $a\\cdot\\dfrac{x^{n+1}}{n+1}$. Verify by differentiating — you should recover $4x^3 - 2x + 7$.

**Common slip:**
Forgetting $+C$ or mishandling $\\int -2x\\,dx$ as $-x^2$ without the coefficient (writing $-2x^2$ instead).

**Exam tip:**
On indefinite integrals, write $+C$ on the same line as the final answer. Graders deduct even when all terms are correct.""",
        "he": """**למה זה נכון:**
אינטegralו איבר-איבר: $\\int 4x^3\\,dx = x^4$, $\\int -2x\\,dx = -x^2$, $\\int 7\\,dx = 7x$. סכמו עם $+C$: $F(x) = x^4 - x^2 + 7x + C$.

**איך לחשוב על זה:**
פונקציות קדומות הופכות את כלל החזקה. כל איבר $ax^n$ הופך ל-$a\\cdot\\dfrac{x^{n+1}}{n+1}$. אמתו בגזירה — תקבלו $4x^3 - 2x + 7$.

**טעות נפוצה:**
שכחת $+C$ או טיפול שגוי ב-$\\int -2x\\,dx$ (כתיבת $-2x^2$ במקום $-x^2$).

**טיפ לבחינה:**
באינטegralים לא-מסוימים, כתבו $+C$ בשורה עם התשובה. מורידים נקודות גם כשכל האיברים נכונים.""",
    },
    {
        "en": """**Why this is correct:**
Antiderivative: $F(x) = \\dfrac{x^2}{2} + 2x$. By FTC: $\\int_1^3 (x+2)\\,dx = F(3) - F(1) = (\\dfrac{9}{2}+6) - (\\dfrac{1}{2}+2) = \\dfrac{21}{2} - \\dfrac{5}{2} = 8$.

**How to think about it:**
Integrate $x$ to $\\dfrac{x^2}{2}$ and $2$ to $2x$. Write $[F(x)]_1^3$ before substituting — this separates method marks from arithmetic.

**Common slip:**
Arithmetic errors at $F(3)$: $9/2 + 6 = 10.5$, not $9/2 + 3$. Or forgetting to subtract $F(1)$ entirely.

**Exam tip:**
For linear integrands, you can also interpret $\\int_1^3 (x+2)\\,dx$ as trapezoid area — a quick estimate confirms $8$ is reasonable.""",
        "he": """**למה זה נכון:**
פונקציה קדומה: $F(x) = \\dfrac{x^2}{2} + 2x$. לפי משפט היסוד: $\\int_1^3 (x+2)\\,dx = F(3) - F(1) = \\dfrac{21}{2} - \\dfrac{5}{2} = 8$.

**איך לחשוב על זה:**
אינטegralו $x$ ל-$\\dfrac{x^2}{2}$ ו-$2$ ל-$2x$. כתבו $[F(x)]_1^3$ לפני הצבה — מפריד נקודות שיטה מחשבון.

**טעות נפוצה:**
טעויות חשבון ב-$F(3)$: $9/2 + 6 = 10.5$, לא $9/2 + 3$. או שכחת $F(1)$ לגמרי.

**טיפ לבחינה:**
לintegrand לינארי, אפשר לפרש כשטח טrapez — הערכה מהירה מאמתת ש-$8$ סביר.""",
    },
    {
        "en": """**Why this is correct:**
$\\int e^x\\,dx = e^x + C$, so $F(x) = e^x$. Then $\\int_0^2 e^x\\,dx = [e^x]_0^2 = e^2 - e^0 = e^2 - 1 \\approx 6.389$.

**How to think about it:**
$e^x$ is its own antiderivative — the simplest exponential integral on Bagrut. The definite integral measures area under $y = e^x$ from $0$ to $2$; since $e^x > 0$, area equals the integral value.

**Common slip:**
Writing $e^2 - 1$ as $e$ (confusing $e^0 = 1$ with $e$) or evaluating $F(0)$ as $0$ instead of $1$.

**Exam tip:**
Leave exact form $e^2 - 1$ unless the question asks for a decimal. Examiners prefer exact answers with $e$.""",
        "he": """**למה זה נכון:**
$\\int e^x\\,dx = e^x + C$, לכן $F(x) = e^x$. אז $\\int_0^2 e^x\\,dx = [e^x]_0^2 = e^2 - 1 \\approx 6.389$.

**איך לחשוב על זה:**
$e^x$ היא הפונקציה הקדומה של עצמה — האינטegral המעריכי הפשוט ביותר בבגרות. האינטegral המסוים מודד שטח מתחת ל-$y = e^x$ מ-$0$ עד $2$; מכיוון ש-$e^x > 0$, השטח שווה לערך.

**טעות נפוצה:**
כתיבת $e^2 - 1$ כ-$e$ (בלבול $e^0 = 1$ עם $e$) או $F(0) = 0$ במקום $1$.

**טיפ לבחינה:**
השאירו צורה מדויקת $e^2 - 1$ אלא אם נדרש עשרוני. בוחנים מעדיפים תשובות מדויקות עם $e$.""",
    },
    {
        "en": """**Why this is correct:**
For $x > 0$, $\\dfrac{d}{dx}[\\ln x] = \\dfrac{1}{x}$, so $\\int \\dfrac{1}{x}\\,dx = \\ln|x| + C$. With domain $x > 0$, this simplifies to $\\ln(x) + C$.

**How to think about it:**
This is the reverse of the logarithm derivative rule. The $|x|$ in the general formula handles negative $x$; here the restriction $x > 0$ removes the absolute value.

**Common slip:**
Answering $\\ln x$ without $+C$ on an indefinite integral, or writing $\\dfrac{x^0}{0}$ via the power rule (which fails at $n = -1$).

**Exam tip:**
Memorize $\\int \\frac{1}{x}\\,dx = \\ln|x| + C$ separately from the power rule — it is the most tested exception.""",
        "he": """**למה זה נכון:**
עבור $x > 0$, $\\dfrac{d}{dx}[\\ln x] = \\dfrac{1}{x}$, לכן $\\int \\dfrac{1}{x}\\,dx = \\ln|x| + C$. עם תחום $x > 0$, זה מתפשט ל-$\\ln(x) + C$.

**איך לחשוב על זה:**
זה ההיפך של כלל הנגזרת של לוגריתם. ה-$|x|$ בנוסחה הכללית מטפל ב-$x$ שלילי; כאן ההגבלה $x > 0$ מסירה את הערך המוחלט.

**טעות נפוצה:**
תשובה $\\ln x$ בלי $+C$ באינטegral לא-מסוים, או $\\dfrac{x^0}{0}$ דרך כלל החזקה (נכשל ב-$n = -1$).

**טיפ לבחינה:**
שננו $\\int \\frac{1}{x}\\,dx = \\ln|x| + C$ בנפרד מכלל החזקה — זו החריגה הנבחנת ביותר.""",
    },
    {
        "en": """**Why this is correct:**
Roots: $x^2 - 2x = x(x-2) = 0$ at $x = 0$ and $x = 2$. On $(0,2)$, $f(x) = x(x-2) < 0$, so the curve lies below the axis. Geometric area = $\\left|\\int_0^2 (x^2-2x)\\,dx\\right| = \\left|[\\frac{x^3}{3}-x^2]_0^2\\right| = |\\frac{8}{3}-4| = \\frac{4}{3}$.

**How to think about it:**
"Area under the curve" means geometric area (positive). When $f < 0$, the definite integral is negative — take absolute value or split and add magnitudes.

**Common slip:**
Reporting $\\int_0^2 (x^2-2x)\\,dx = -\\frac{4}{3}$ as the final area without absolute value.

**Exam tip:**
State explicitly: "$f(x) < 0$ on $(0,2)$, so area = $|\\text{integral}|$." Examiners reward sign analysis.""",
        "he": """**למה זה נכון:**
שורשים: $x^2 - 2x = x(x-2) = 0$ ב-$x = 0$ ו-$x = 2$. ב-$(0,2)$, $f(x) < 0$, העקומה מתחת לציר. שטח גיאומטרי = $\\left|\\int_0^2 (x^2-2x)\\,dx\\right| = \\left|[\\frac{x^3}{3}-x^2]_0^2\\right| = \\frac{4}{3}$.

**איך לחשוב על זה:**
"שטח מתחת לעקומה" פירושו שטח גיאומטרי (חיובי). כש-$f < 0$, האינטegral המסוים שלילי — קחו ערך מוחלט או פצלו והוסיפו גדלים.

**טעות נפוצה:**
דיווח $\\int_0^2 (x^2-2x)\\,dx = -\\frac{4}{3}$ כשטח סופי בלי ערך מוחלט.

**טיפ לבחינה:**
ציינו במפורש: "$f(x) < 0$ ב-$(0,2)$, לכן שטח = $|\\text{אינטegral}|$." בוחנים נותנים נקודות על ניתוח סימן.""",
    },
    {
        "en": """**Why this is correct:**
$\\int \\sin x\\,dx = -\\cos x + C$. So $\\int_0^{\\pi/2} \\sin x\\,dx = [-\\cos x]_0^{\\pi/2} = -\\cos(\\pi/2) + \\cos(0) = 0 + 1 = 1$.

**How to think about it:**
The antiderivative of $\\sin x$ is $-\\cos x$ (note the minus sign). At $\\pi/2$, $\\cos(\\pi/2) = 0$; at $0$, $\\cos(0) = 1$. The integral equals the area under one hump of sine — a standard result worth memorizing.

**Common slip:**
Using $+\\cos x$ as antiderivative (differentiation gives $-\\sin x$, not $\\sin x$) or evaluating $-\\cos(\\pi/2)$ as $-1$ instead of $0$.

**Exam tip:**
Draw the sine graph on $[0, \\pi/2]$ — area $1$ matches the geometric picture and catches sign errors instantly.""",
        "he": """**למה זה נכון:**
$\\int \\sin x\\,dx = -\\cos x + C$. אז $\\int_0^{\\pi/2} \\sin x\\,dx = [-\\cos x]_0^{\\pi/2} = -0 + 1 = 1$.

**איך לחשוב על זה:**
הפונקציה הקדומה של $\\sin x$ היא $-\\cos x$ (שימו לב לסימן). ב-$\\pi/2$, $\\cos(\\pi/2) = 0$; ב-$0$, $\\cos(0) = 1$. האינטegral שווה לשטח מתחת לגבעה אחת של סינוס — תוצאה שכדאי לשנן.

**טעות נפוצה:**
שימוש ב-$+\\cos x$ כפונקציה קדומה, או $-\\cos(\\pi/2) = -1$ במקום $0$.

**טיפ לבחינה:**
סרטטו את גרף הסינוס ב-$[0, \\pi/2]$ — שטח $1$ תואם לתמונה הגיאומטרית ותופס טעויות סימן.""",
    },
    {
        "en": """**Why this is correct:**
On $[0,1]$, $x \\ge x^2$ (test: at $x = 0.5$, $0.5 > 0.25$). Area = $\\int_0^1 (x - x^2)\\,dx = [\\frac{x^2}{2} - \\frac{x^3}{3}]_0^1 = \\frac{1}{2} - \\frac{1}{3} = \\frac{1}{6}$.

**How to think about it:**
Line $y = x$ sits above parabola $y = x^2$ on $[0,1]$ (they meet at $0$ and $1$). Integrate top minus bottom. This is the simplest area-between-curves template on Bagrut.

**Common slip:**
Integrating $x^2 - x$ instead of $x - x^2$, giving $-\\frac{1}{6}$. Or using limits $[0,2]$ instead of intersection points $[0,1]$.

**Exam tip:**
When curves meet at endpoints, those $x$-values are your limits — no extra intersection step needed, but still verify which is on top.""",
        "he": """**למה זה נכון:**
ב-$[0,1]$, $x \\ge x^2$ (בדיקה: ב-$x = 0.5$, $0.5 > 0.25$). שטח = $\\int_0^1 (x - x^2)\\,dx = [\\frac{x^2}{2} - \\frac{x^3}{3}]_0^1 = \\frac{1}{2} - \\frac{1}{3} = \\frac{1}{6}$.

**איך לחשוב על זה:**
הישר $y = x$ מעל $y = x^2$ ב-$[0,1]$ (נפגשים ב-$0$ ו-$1$). אינטegralו עליונה פחות תחתונה. זה תבנית שטח-בין-עקומות הפשוטה ביותר בבגרות.

**טעות נפוצה:**
אינטegral של $x^2 - x$ במקום $x - x^2$, נותן $-\\frac{1}{6}$. או גבולות $[0,2]$ במקום $[0,1]$.

**טיפ לבחינה:**
כשעקומות נפגשות בקצוות, אלה הגבולות — אין צורך בחיתוך נוסף, אך עדיין אמתו מי למעלה.""",
    },
    {
        "en": """**Why this is correct:**
$\\int_0^k x^2\\,dx = [\\frac{x^3}{3}]_0^k = \\frac{k^3}{3}$. Set $\\frac{k^3}{3} = 9$, so $k^3 = 27$ and $k = 3$ (positive root).

**How to think about it:**
Evaluate the integral symbolically first, then solve for $k$. This parametric pattern appears frequently on Bagrut: clean algebra after FTC. Verify: $\\frac{3^3}{3} = 9$ ✓

**Common slip:**
Solving $k^3 = 27$ as $k = 9$ (confusing cube root with division by 3) or forgetting the $\\frac{1}{3}$ factor from the power rule.

**Exam tip:**
After finding $k$, substitute back into $\\int_0^k x^2\\,dx$ — one line of verification earns confidence and catches algebra slips under time pressure.""",
        "he": """**למה זה נכון:**
$\\int_0^k x^2\\,dx = [\\frac{x^3}{3}]_0^k = \\frac{k^3}{3}$. הציבו $\\frac{k^3}{3} = 9$, כלומר $k^3 = 27$ ו-$k = 3$ (שורש חיובי).

**איך לחשוב על זה:**
חשבו את האינטegral סימbolית תחילה, אז פתרו ל-$k$. דפוס פרמטרי תכוף בבגרות: אלגברה נקייה אחרי משפט היסוד. אימות: $\\frac{3^3}{3} = 9$ ✓

**טעות נפוצה:**
פתרון $k^3 = 27$ כ-$k = 9$ (בלבול שורש שלישי עם חלוקה ב-3) או שכחת גורם $\\frac{1}{3}$ מכלל החזקה.

**טיפ לבחינה:**
אחרי מציאת $k$, הציבו חזרה — שורת אימות אחת תופסת טעויות אלגברה תחת לחץ זמן.""",
    },
]


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in EXPANSIONS:
            sec["body_en_md"] = EXPANSIONS[kind]["body_en_md"]
            sec["body_he_md"] = EXPANSIONS[kind]["body_he_md"]
        elif kind == "worked_example":
            n = sec.get("example_number")
            if n == 1:
                sec["body_en_md"] = WE1["body_en_md"] + EN_WE1_EXTRA
                sec["body_he_md"] = WE1["body_he_md"] + HE_WE1_EXTRA
            elif n == 2:
                sec["body_en_md"] = WE2["body_en_md"] + EN_WE2_EXTRA
                sec["body_he_md"] = WE2["body_he_md"] + HE_WE2_EXTRA
            elif n == 3:
                sec["body_en_md"] = WE3["body_en_md"] + EN_WE3_EXTRA
                sec["body_he_md"] = WE3["body_he_md"] + HE_WE3_EXTRA
        elif kind == "checkpoint":
            if "2x + 3" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CP1["checkpoint_solution_en"]
                sec["checkpoint_solution_he"] = CP1["checkpoint_solution_he"]
            else:
                sec["checkpoint_solution_en"] = CP2["checkpoint_solution_en"]
                sec["checkpoint_solution_he"] = CP2["checkpoint_solution_he"]
        elif kind == "method_guide":
            sec["body_en_md"] = METHOD["body_en_md"]
            sec["body_he_md"] = METHOD["body_he_md"]
        elif kind == "pitfall":
            sec["body_en_md"] = PITFALL["body_en_md"]
            sec["body_he_md"] = PITFALL["body_he_md"]
        elif kind == "why_matters":
            sec["body_en_md"] = WHY["body_en_md"]
            sec["body_he_md"] = WHY["body_he_md"]
        elif kind == "before_exam":
            sec["body_en_md"] = BEFORE_EXAM["body_en_md"]
            sec["body_he_md"] = BEFORE_EXAM["body_he_md"]
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY["body_en_md"]
            sec["body_he_md"] = SUMMARY["body_he_md"]

    for i, q in enumerate(data["questions"]):
        q["explanation_en"] = EXPLANATIONS[i]["en"] + EXAM_EN_FOLLOWUP
        q["explanation_he"] = EXPLANATIONS[i]["he"] + EXAM_HE_FOLLOWUP
        if q["ord"] == 8:
            q["answer_payload"] = {
                "acceptable_answers": ["3", "k = 3", "k=3"],
                "case_sensitive": False,
            }

    TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind not in MIN_WORDS:
            continue
        en_w = word_count(sec.get("body_en_md", ""))
        he_w = word_count(sec.get("body_he_md", ""))
        mins = MIN_WORDS[kind]
        if en_w < mins["en"]:
            errors.append(f"section {kind}: EN {en_w} < {mins['en']}")
        if he_w < mins["he"]:
            errors.append(f"section {kind}: HE {he_w} < {mins['he']}")
        if hebrew_body_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"section {kind}: weak Hebrew")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q[f"explanation_{lang}"])
            if w < 80 or w > 150:
                errors.append(f"Q{q['ord']} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)
    print("OK — all gates passed")
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")


if __name__ == "__main__":
    main()
