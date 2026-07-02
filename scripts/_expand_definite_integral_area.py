#!/usr/bin/env python3
"""Expand definite_integral_area.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/definite_integral_area.json"

INTRO = {
    "body_en_md": """Imagine approximating the area under a curve $y=f(x)$ on $[a,b]$ using $n$ thin rectangles of width $\\Delta x = (b-a)/n$. As $n\\to\\infty$ the sum of rectangle areas converges to a limit — the **definite integral** $\\int_a^b f(x)\\,dx$.

This is the **Riemann integral**, defined as:
$$\\int_a^b f(x)\\,dx = \\lim_{n\\to\\infty}\\sum_{i=1}^n f(x_i^*)\\Delta x$$

**Key insight:** The geometric definition would be nearly impossible to compute for every function. The **Fundamental Theorem of Calculus (FTC)** provides the shortcut: find an antiderivative $F$ with $F'=f$, then evaluate $F(b)-F(a)$.

**Why this lesson matters:** Calc 1 and Bagrut 5-unit exams treat definite integrals as the bridge between geometry (area), physics (work, displacement), and algebra (antiderivatives). You will use FTC Part 2 on nearly every area problem, FTC Part 1 when differentiating integrals with variable limits, and the area-between-curves algorithm on multi-step word problems.

**Three vocabulary words to keep straight:** *signed area* (can be negative), *unsigned geometric area* (always $\\ge 0$, needs $|f|$), and *area between curves* (integrate top minus bottom after finding intersections). Confusing these three is the number-one source of lost points.""",
    "body_he_md": """דמיינו קירוב השטח מתחת לעקומה $y=f(x)$ על $[a,b]$ באמצעות $n$ מלבנים צרים ברוחב $\\Delta x=(b-a)/n$. כאשר $n\\to\\infty$ סכום שטחי המלבנים מתכנס לגבול — **האינטגרל המסוים** $\\int_a^b f(x)\\,dx$.

זהו **אינטגרל רימן**:
$$\\int_a^b f(x)\\,dx=\\lim_{n\\to\\infty}\\sum_{i=1}^n f(x_i^*)\\Delta x$$

**תובנה מרכזית:** ההגדרה הגיאומטרית קשה לחישוב עבור כל פונקציה. **משפט היסוד של החשבון (FTC)** מספק קיצור: מצאו קדומה $F$ עם $F'=f$, ואז חשבו $F(b)-F(a)$.

**למה השיעור הזה חשוב:** בחדו״א 1 ובבגרות 5 יחידות האינטגרל המסוים מחבר גיאומטריה (שטח), פיזיקה (עבודה, תזוזה) ואלגברה (קדומות). FTC חלק 2 מופיע בכמעט כל בעיית שטח; FTC חלק 1 כשגוזרים אינטגרל עם גבול משתנה; אלגוריתם שטח בין עקומות בבעיות רב-שלביות.

**שלושה מונחים להפריד:** *שטח עם סימן* (יכול להיות שלילי), *שטח גיאומטרי* (תמיד $\\ge 0$, דורש $|f|$), ו*שטח בין עקומות* (אינטגרל של עליון פחות תחתון אחרי מציאת חיתוכים). בלבול ביניהם — מקור מספר 1 לאיבוד נקודות.""",
}

DEFINITION = {
    "body_en_md": """**FTC Part 1 (Derivative of an integral):**
If $f$ is continuous on $[a,b]$, then the function
$$G(x) = \\int_a^x f(t)\\,dt$$
is differentiable on $(a,b)$ and $G'(x) = f(x)$.

*In words: differentiation undoes integration.* When the upper limit is a function $g(x)$ instead of $x$, the chain rule gives $\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt = f(g(x))\\cdot g'(x)$.

**FTC Part 2 (Evaluation):**
If $F$ is any antiderivative of $f$ (i.e., $F'=f$) on $[a,b]$, then
$$\\int_a^b f(x)\\,dx = F(b) - F(a) = \\Big[F(x)\\Big]_a^b.$$

The constant $+C$ never appears in definite integrals because it cancels in $F(b)-F(a)$.

**Signed area:** $\\int_a^b f(x)\\,dx$ counts area above the axis as positive and below as negative. Example: $\\int_0^{2\\pi}\\sin x\\,dx=0$ even though the geometric area under one arch is $2$.

**Unsigned area (geometric area):** $\\displaystyle\\int_a^b |f(x)|\\,dx$ — always non-negative. Use this when the question says "total area" or "area enclosed."

**Area between two curves** ($f\\geq g$ on $[a,b]$):
$$A = \\int_a^b [f(x)-g(x)]\\,dx$$
Sketch the region, find intersections, determine which function is on top in each subinterval, then integrate (top − bottom).""",
    "body_he_md": """**FTC חלק 1 (נגזרת של אינטגרל):**
אם $f$ רציפה על $[a,b]$, אז
$$G(x)=\\int_a^x f(t)\\,dt$$
גזירה על $(a,b)$ ו-$G'(x)=f(x)$.

*במילים:* גזירה מבטלת אינטגרציה. כשהגבול העליון הוא $g(x)$ במקום $x$, כלל השרשרת נותן $\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt = f(g(x))\\cdot g'(x)$.

**FTC חלק 2 (חישוב):**
אם $F'=f$ על $[a,b]$:
$$\\int_a^b f(x)\\,dx = F(b)-F(a)=\\Big[F(x)\\Big]_a^b.$$

הקבוע $+C$ לא מופיע באינטגרל מסוים כי הוא מתבטל ב-$F(b)-F(a)$.

**שטח עם סימן:** $\\int_a^b f(x)\\,dx$ סופר שטח מעל הציר כחיובי ומתחת כשלילי. דוגמה: $\\int_0^{2\\pi}\\sin x\\,dx=0$ למרות שהשטח הגיאומטרי תחת קשת אחת הוא $2$.

**שטח גיאומטרי:** $\\int_a^b|f(x)|\\,dx$ — תמיד אי-שלילי. השתמשו כשהשאלה אומרת "שטח כולל" או "שטח סגור".

**שטח בין עקומות** ($f\\geq g$ על $[a,b]$):
$$A=\\int_a^b[f(x)-g(x)]\\,dx$$
שרטטו, מצאו חיתוכים, קבעו מי למעלה בכל תת-קטע, ואז אינטגרל (עליון − תחתון).""",
}

THEORY = {
    "body_en_md": """The definite integral satisfies algebraic rules that mirror how areas combine on the number line. Master these before tackling multi-part exam problems.

**Linearity:**
$$\\int_a^b[cf(x)+g(x)]\\,dx = c\\int_a^b f(x)\\,dx + \\int_a^b g(x)\\,dx$$

**Interval splitting:** For any $c$ between $a$ and $b$,
$$\\int_a^b f(x)\\,dx = \\int_a^c f(x)\\,dx + \\int_c^b f(x)\\,dx$$
This is essential when $f$ changes sign or when the "top" curve switches on a subinterval.

**Reversing limits:** $\\int_b^a f\\,dx = -\\int_a^b f\\,dx$. Swapping limits introduces a minus sign — watch for this in symmetry arguments.

**Comparison:** If $f\\leq g$ on $[a,b]$, then $\\int_a^b f\\,dx\\leq\\int_a^b g\\,dx$.

**FTC Part 1 with chain rule (Leibniz rule):** When both limits depend on $x$,
$$\\frac{d}{dx}\\int_{g(x)}^{h(x)} f(t)\\,dt = f(h(x))h'(x) - f(g(x))g'(x)$$

**Area between curves — when which is on top changes:** Split the interval at every intersection point. On each piece, integrate (upper − lower). Never assume one curve stays on top across the whole interval without checking a test point.

**Exam strategy:** For any area problem, draw a quick sketch, mark intersections, shade the region, and label which function is above. Thirty seconds of setup prevents the most common sign and limit errors.

**Average value (exam bonus):** The mean of $f$ on $[a,b]$ is $\\frac{1}{b-a}\\int_a^b f(x)\\,dx$. This connects FTC to statistics and appears on some Calc 1 finals as a short follow-up part.""",
    "body_he_md": """לאינטגרל המסוים תכונות אלגבריות שמשקפות איך שטחים מתחברים על ציר המספרים. שלטו בהן לפני בעיות בחינה רב-שלביות.

**ליניאריות:**
$$\\int_a^b[cf(x)+g(x)]\\,dx = c\\int_a^b f\\,dx+\\int_a^b g\\,dx$$

**פיצול קטע:** לכל $c$ בין $a$ ל-$b$,
$$\\int_a^b f\\,dx=\\int_a^c f\\,dx+\\int_c^b f\\,dx$$
חיוני כש-$f$ משנה סימן או כשהעקומה "העליונה" מתחלפת בתת-קטע.

**היפוך גבולות:** $\\int_b^a f\\,dx=-\\int_a^b f\\,dx$. החלפת גבולות מוסיפה מינוס — שימו לב בטיעוני סימטריה.

**השוואה:** $f\\leq g$ על $[a,b]\\Rightarrow\\int_a^b f\\,dx\\leq\\int_a^b g\\,dx$.

**FTC 1 עם שרשרת (כלל לייבניץ):** כששני הגבולות תלויים ב-$x$,
$$\\frac{d}{dx}\\int_{g(x)}^{h(x)} f(t)\\,dt=f(h(x))h'(x)-f(g(x))g'(x)$$

**שטח בין עקומות — כשה"עליון" מתחלף:** פצלו בכל נקודת חיתוך. בכל חלק — אינטגרל (עליון − תחתון). אל תניחו שעקומה אחת נשארת למעלה בלי לבדוק נקודת בדיקה.

**אסטרטגיה לבחינה:** בכל בעיית שטח — שרטוט מהיר, סימון חיתוכים, הצללה, וסימון מי למעלה. 30 שניות הכנה מונעות את שגיאות הסימן והגבולות הנפוצות ביותר.

**ערך ממוצע (בונוס בבחינה):** הממוצע של $f$ ב-$[a,b]$ הוא $\\frac{1}{b-a}\\int_a^b f(x)\\,dx$. זה מקשר FTC לסטטיסטיקה ומופיע בחלקים קצרים בבחינות גמר.""",
}

WE1 = {
    "body_en_md": """**Given:** $\\displaystyle\\int_0^2 x^2\\,dx$.

This is the canonical FTC Part 2 problem — find an antiderivative, evaluate at the bounds, subtract. No $+C$ is needed.

### Move 1: Find an antiderivative of $x^2$.
$$F(x) = \\frac{x^3}{3}$$
Check: $\\frac{d}{dx}(x^3/3)=x^2$ ✓

### Move 2: Apply FTC Part 2 with bracket notation.
$$\\int_0^2 x^2\\,dx = \\left[\\frac{x^3}{3}\\right]_0^2 = F(2) - F(0) = \\frac{2^3}{3} - \\frac{0^3}{3} = \\frac{8}{3} - 0 = \\frac{8}{3}$$

**Answer:** $\\boxed{\\dfrac{8}{3}}$ ✓

**Geometric interpretation:** The area under the parabola $y=x^2$ from $x=0$ to $x=2$ is exactly $8/3$ square units. Since $x^2\\ge 0$ on $[0,2]$, signed area equals geometric area here.

**Exam note:** Power-rule antiderivatives appear on every Calc 1 test. Write $F(x)$ explicitly before substituting limits — graders award partial credit for correct setup even if arithmetic slips at the end.

**Quick check:** $\\frac{8}{3}\\approx 2.67$ is less than the rectangle $2\\times 4=8$ that overestimates the area — a reasonable sanity bound for any parabola-under-line comparison.""",
    "body_he_md": """**נתון:** $\\displaystyle\\int_0^2 x^2\\,dx$.

זו בעיית FTC חלק 2 קלאסית — מצאו קדומה, חשבו בגבולות, חסרו. אין צורך ב-$+C$.

### צעד 1: קדומה של $x^2$.
$$F(x)=\\frac{x^3}{3}$$
בדיקה: $\\frac{d}{dx}(x^3/3)=x^2$ ✓

### צעד 2: יישום FTC חלק 2 עם סימון סוגריים.
$$\\int_0^2 x^2\\,dx=\\left[\\frac{x^3}{3}\\right]_0^2=F(2)-F(0)=\\frac{8}{3}-0=\\frac{8}{3}$$

**תשובה:** $\\boxed{\\dfrac{8}{3}}$ ✓

**פרשנות גיאומטרית:** השטח מתחת לפרבולה $y=x^2$ מ-$x=0$ עד $x=2$ הוא בדיוק $8/3$ יחידות ריבוע. מכיוון ש-$x^2\\ge 0$ ב-$[0,2]$, שטח עם סימן שווה לשטח גיאומטרי.

**הערה לבחינה:** קדומות לפי כלל החזקה מופיעות בכל בחינת חדו״א 1. כתבו $F(x)$ במפורש לפני הצבת גבולות — בודקים נותנים ניקוד חלקי על הגדרה נכונה.

**בדיקה מהירה:** $\\frac{8}{3}\\approx 2.67$ קטן מהמלבן $2\\times 4=8$ שמעריך יתר על המידה — גבול סביר לשטח תחת כל פרבולה.""",
}

WE2 = {
    "body_en_md": """**Given:** Find the area enclosed between $y=x^2$ and $y=x$.

Area-between-curves problems follow a fixed four-step pipeline: intersections → test point → set up integral → FTC.

### Move 1: Find intersection points.
$$x^2 = x \\implies x^2-x=0 \\implies x(x-1)=0 \\implies x=0 \\text{ or } x=1$$

### Move 2: Determine which curve is on top on $(0,1)$.
At $x=1/2$: $y=x$ gives $1/2$; $y=x^2$ gives $1/4$. So $x\\geq x^2$ on $[0,1]$ — the line is above the parabola. ✓

### Move 3: Set up and evaluate the integral.
$$A = \\int_0^1 (x - x^2)\\,dx = \\left[\\frac{x^2}{2}-\\frac{x^3}{3}\\right]_0^1 = \\left(\\frac{1}{2}-\\frac{1}{3}\\right)-0 = \\frac{1}{6}$$

**Answer:** $\\boxed{A = \\dfrac{1}{6}}$ sq. units ✓

**Why test a point?** Intersections alone do not tell you which curve is upper — always plug in a value between the intersection $x$-coordinates.

**Exam tip:** Label the shaded region on your sketch. Bagrut and Calc 1 rubrics expect you to show the integrand $(\\text{top}-\\text{bottom})$ before evaluating.

**Symmetry shortcut:** If both curves are even functions and the region is symmetric about the $y$-axis, compute $2\\int_0^1(x-x^2)\\,dx$ to save time.""",
    "body_he_md": """**נתון:** מצאו את השטח הסגור בין $y=x^2$ ו-$y=x$.

בעיות שטח בין עקומות עוקבות אחר צינור קבוע: חיתוכים → נקודת בדיקה → הגדרת אינטגרל → FTC.

### צעד 1: נקודות חיתוך.
$$x^2=x\\Rightarrow x(x-1)=0\\Rightarrow x=0 \\text{ או } x=1$$

### צעד 2: מי למעלה על $(0,1)$?
ב-$x=1/2$: $y=x$ נותן $1/2$; $y=x^2$ נותן $1/4$. לכן $x\\ge x^2$ ב-$[0,1]$ — הישר מעל הפרבולה. ✓

### צעד 3: הגדרה וחישוב.
$$A=\\int_0^1(x-x^2)\\,dx=\\left[\\frac{x^2}{2}-\\frac{x^3}{3}\\right]_0^1=\\frac{1}{2}-\\frac{1}{3}=\\frac{1}{6}$$

**תשובה:** $\\boxed{\\dfrac{1}{6}}$ יחידות ריבוע ✓

**למה לבדוק נקודה?** חיתוכים בלבד לא אומרים מי למעלה — תמיד הציבו ערך בין קואורדינטות החיתוך.

**טיפ לבחינה:** סמנו את האזור המוצלל בשרטוט. מחווני בגרות וחדו״א מצפים להציג את האינטגרנד (עליון − תחתון) לפני החישוב.

**קיצור סימטריה:** אם שתי העקומות זוגיות והאזור סימטרי לציר $y$, חשבו $2\\int_0^1(x-x^2)\\,dx$ לחיסכון זמן.""",
}

WE3 = {
    "body_en_md": """**Given:** $\\displaystyle\\int_0^1|x^2-x|\\,dx$ — geometric (unsigned) area.

Absolute-value integrals require finding where the expression inside changes sign, then removing the bars piecewise.

### Move 1: Find zeros of $x^2-x$.
$$x^2-x = x(x-1) = 0 \\implies x=0 \\text{ or } x=1$$

### Move 2: Determine sign on $(0,1)$.
At $x=1/2$: $x^2-x = 1/4-1/2 = -1/4 < 0$. So $x^2-x < 0$ on $(0,1)$, meaning $|x^2-x| = -(x^2-x) = x-x^2$ there.

### Move 3: Remove the absolute value and integrate.
$$\\int_0^1|x^2-x|\\,dx = \\int_0^1(x-x^2)\\,dx$$

*(Both endpoints are zeros, so no interior split is needed on $[0,1]$.)*

### Move 4: Evaluate with FTC.
$$\\int_0^1(x-x^2)\\,dx = \\left[\\frac{x^2}{2}-\\frac{x^3}{3}\\right]_0^1 = \\frac{1}{2}-\\frac{1}{3} = \\frac{1}{6}$$

**Answer:** $\\boxed{\\dfrac{1}{6}}$ ✓

**Extended case:** For $\\int_0^2|x^2-x|\\,dx$, note $x^2-x>0$ on $(1,2)$. Split at $x=1$ and integrate each piece with the correct sign.

**Exam note:** Questions asking for "total area enclosed" almost always need $|f|$ or splitting at zeros — a negative FTC result signals you forgot this step.

**Triangle estimate:** On $[0,1]$, $x-x^2\\le 1/4$ at the peak, so area $<1/4$ — confirming $1/6$ is plausible.""",
    "body_he_md": """**נתון:** $\\displaystyle\\int_0^1|x^2-x|\\,dx$ — שטח גיאומטרי (ללא סימן).

אינטגרלים עם ערך מוחלט דורשים מציאת נקודות שינוי סימן, ואז הסרת הערך המוחלט בחלקים.

### צעד 1: אפסים של $x^2-x$.
$$x^2-x=x(x-1)=0\\Rightarrow x=0,1$$

### צעד 2: סימן על $(0,1)$.
ב-$x=1/2$: $-1/4<0$. לכן $x^2-x<0$ ב-$(0,1)$, כלומר $|x^2-x|=x-x^2$.

### צעד 3: הסרת ערך מוחלט ואינטגרציה.
$$\\int_0^1|x^2-x|\\,dx=\\int_0^1(x-x^2)\\,dx$$

*(שני הקצוות הם אפסים — אין צורך בפיצול פנימי ב-$[0,1]$.)*

### צעד 4: חישוב עם FTC.
$$\\left[\\frac{x^2}{2}-\\frac{x^3}{3}\\right]_0^1=\\frac{1}{2}-\\frac{1}{3}=\\frac{1}{6}$$

**תשובה:** $\\boxed{\\dfrac{1}{6}}$ ✓

**הרחבה:** עבור $\\int_0^2|x^2-x|\\,dx$, שימו לב ש-$x^2-x>0$ ב-$(1,2)$. פצלו ב-$x=1$.

**הערה לבחינה:** שאלות על "שטח כולל סגור" כמעט תמיד דורשות $|f|$ או פיצול באפסים — תוצאה שלילית מ-FTC מסמנת ששכחתם את הצעד.

**הערכת משולש:** ב-$[0,1]$, $x-x^2\\le 1/4$ בראש — שטח $<1/4$, ולכן $1/6$ סביר.""",
}

CHECKPOINT1_EN = """**Step 1 — Antiderivative:** An antiderivative of $\\cos x$ is $F(x)=\\sin x$ (since $\\frac{d}{dx}\\sin x=\\cos x$).

**Step 2 — Apply FTC Part 2:**
$$\\int_0^{\\pi/2}\\cos x\\,dx = [\\sin x]_0^{\\pi/2} = \\sin(\\pi/2)-\\sin(0) = 1-0 = 1.$$

**Interpretation:** On $[0,\\pi/2]$, $\\cos x\\ge 0$, so the signed integral equals the geometric area under one quarter-period of cosine — exactly $1$ square unit.

**Check:** $\\sin(\\pi/2)=1$ and $\\sin(0)=0$ are standard unit-circle values you should know without a calculator."""

CHECKPOINT1_HE = """**צעד 1 — קדומה:** קדומה של $\\cos x$ היא $F(x)=\\sin x$ (כי $\\frac{d}{dx}\\sin x=\\cos x$).

**צעד 2 — יישום FTC חלק 2:**
$$\\int_0^{\\pi/2}\\cos x\\,dx=[\\sin x]_0^{\\pi/2}=\\sin(\\pi/2)-\\sin(0)=1-0=1.$$

**פרשנות:** ב-$[0,\\pi/2]$, $\\cos x\\ge 0$, ולכן האינטגרל עם סימן שווה לשטח הגיאומטרי תחת רבע מחזור של קוסינוס — בדיוק $1$ יחידה ריבוע.

**בדיקה:** $\\sin(\\pi/2)=1$ ו-$\\sin(0)=0$ — ערכי מעגל יחידה שכדאי לדעת בעל פה."""

CHECKPOINT2_EN = """**Step 1 — Intersections:** $x=x^3\\Rightarrow x^3-x=0\\Rightarrow x(x^2-1)=0$, so $x=0,\\pm 1$.

**Step 2 — Which is on top?**
- On $(-1,0)$: at $x=-1/2$, $x^3=-1/8$ and $x=-1/2$, so $x^3>x$ (cubic is above).
- On $(0,1)$: at $x=1/2$, $x=1/2>x^3=1/8$, so $x>x^3$ (line is above).

**Step 3 — Set up and evaluate:**
$$A=\\int_{-1}^0(x^3-x)\\,dx+\\int_0^1(x-x^3)\\,dx.$$

By symmetry of the odd integrand setup, each piece equals $1/4$, so $A=1/2$.

**Alternative (symmetry):** $A=2\\int_0^1(x-x^3)\\,dx=2\\left[\\frac{x^2}{2}-\\frac{x^4}{4}\\right]_0^1=2\\cdot\\frac{1}{4}=\\frac{1}{2}$."""

CHECKPOINT2_HE = """**צעד 1 — חיתוכים:** $x=x^3\\Rightarrow x(x^2-1)=0$, ולכן $x=0,\\pm 1$.

**צעד 2 — מי למעלה?**
- ב-$(-1,0)$: ב-$x=-1/2$, $x^3>x$ (שלישית למעלה).
- ב-$(0,1)$: ב-$x=1/2$, $x>x^3$ (ישר למעלה).

**צעד 3 — הגדרה וחישוב:**
$$A=\\int_{-1}^0(x^3-x)\\,dx+\\int_0^1(x-x^3)\\,dx.$$

לפי סימטריה, כל חלק שווה $1/4$, ולכן $A=1/2$.

**דרך חלופית (סימטריה):** $A=2\\int_0^1(x-x^3)\\,dx=2\\left[\\frac{x^2}{2}-\\frac{x^4}{4}\\right]_0^1=\\frac{1}{2}$."""

METHOD = {
    "body_en_md": """Use this checklist for every area problem on exams — the order matters.

**Computing $\\int_a^b f(x)\\,dx$ (signed area):**
1. Find antiderivative $F$ with $F'=f$.
2. Evaluate $F(b)-F(a)$ using bracket notation $[F(x)]_a^b$.
3. Interpret: negative means net area below the axis.

**Unsigned area $\\int_a^b|f(x)|\\,dx$:**
1. Find all zeros of $f$ in $[a,b]$.
2. On each subinterval, determine the sign of $f$ (test one point).
3. Replace $|f|$ with $+f$ where $f>0$ and $-f$ where $f<0$.
4. Integrate each piece and sum.

**Area between curves $y=f(x)$ and $y=g(x)$:**
1. Find all intersections: solve $f(x)=g(x)$.
2. On each subinterval, determine which is on top (test point).
3. $A=\\int_a^b|f(x)-g(x)|\\,dx$ — split and integrate (top − bottom).

**FTC Part 1 (differentiation of integrals):**
$$\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt = f(g(x))\\cdot g'(x)$$
Do not forget the chain-rule factor $g'(x)$ when the upper limit is not plain $x$.""",
    "body_he_md": """השתמשו ברשימה זו בכל בעיית שטח בבחינה — הסדר חשוב.

**חישוב $\\int_a^b f(x)\\,dx$ (שטח עם סימן):**
1. מצאו קדומה $F$ עם $F'=f$.
2. חשבו $F(b)-F(a)$ עם סימון $[F(x)]_a^b$.
3. פרשנות: שלילי = שטח נטו מתחת לציר.

**שטח גיאומטרי $\\int_a^b|f(x)|\\,dx$:**
1. מצאו אפסי $f$ ב-$[a,b]$.
2. בכל תת-קטע, קבעו סימן (נקודת בדיקה).
3. החליפו $|f|$ ב-$+f$ כש-$f>0$ וב-$-f$ כש-$f<0$.
4. אינטגרציה על כל חלק וסיכום.

**שטח בין עקומות $y=f(x)$ ו-$y=g(x)$:**
1. מצאו חיתוכים: $f(x)=g(x)$.
2. בכל תת-קטע, קבעו מי למעלה (נקודת בדיקה).
3. $A=\\int_a^b|f-g|\\,dx$ — פיצול ואינטגרל (עליון − תחתון).

**FTC חלק 1 (גזירת אינטגרל):**
$$\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt=f(g(x))\\cdot g'(x)$$
אל תשכחו את גורם השרשרת $g'(x)$ כשהגבול העליון אינו $x$ פשוט.""",
}

PITFALL = {
    "body_en_md": """These five mistakes appear repeatedly on Calc 1 and Bagrut 5-unit exams. Recognize them before they cost points.

1. **Signed vs. unsigned area.** $\\int_0^{2\\pi}\\sin x\\,dx = 0$, but the geometric area under one arch is $2$, and the total over $[0,2\\pi]$ is $4$. Always read whether the question asks for "net area" or "total area enclosed."

2. **Forgetting intersection points.** For area between curves, you cannot set up the integral without knowing where the curves cross. Skipping this step leads to wrong limits and wrong integrands.

3. **Wrong order of subtraction.** Area = $\\int$(top − bottom). Reversing gives a negative answer that you may incorrectly "fix" by dropping the minus sign instead of swapping the curves.

4. **Not splitting at sign changes.** $\\int_0^2|x^2-x|\\,dx$ requires splitting at $x=1$ where $x^2-x$ changes sign. A single FTC pass over the whole interval gives signed cancellation, not geometric area.

5. **FTC Part 1 without chain rule.** $\\frac{d}{dx}\\int_0^{x^2}f(t)\\,dt = f(x^2)\\cdot 2x$, NOT just $f(x^2)$. The derivative of the upper limit is part of the answer.""",
    "body_he_md": """חמש הטעויות האלה חוזרות שוב ושוב בבחינות חדו״א 1 ובגרות 5 יחידות. זהו אותן לפני שהן עולות בנקודות.

1. **שטח עם סימן מול גיאומטרי.** $\\int_0^{2\\pi}\\sin x\\,dx=0$, אבל השטח הגיאומטרי תחת קשת אחת הוא $2$, והכולל על $[0,2\\pi]$ הוא $4$. קראו בקפידה אם השאלה מבקשת "שטח נטו" או "שטח כולל סגור".

2. **שכחת נקודות חיתוך.** בשטח בין עקומות אי אפשר להגדיר אינטגרל בלי לדעת היכן העקומות נחתכות. דילוג על הצעד מוביל לגבולות ואינטגרנד שגויים.

3. **סדר חיסור שגוי.** שטח = $\\int$(עליון − תחתון). היפוך נותן שלילי שאולי "מתקנים" בלי להחליף עקומות.

4. **אי-פיצול בנקודות שינוי סימן.** $\\int_0^2|x^2-x|\\,dx$ דורש פיצול ב-$x=1$. FTC אחד על כל הקטע נותן ביטול סימני, לא שטח גיאומטרי.

5. **FTC 1 ללא כלל שרשרת.** $\\frac{d}{dx}\\int_0^{x^2}f(t)dt=f(x^2)\\cdot 2x$, לא רק $f(x^2)$. נגזרת הגבול העליון חלק מהתשובה.""",
}

WHY = {
    "body_en_md": """Definite integrals are the computational engine behind half of first-semester calculus and much of introductory physics.

**In your learning path:** This lesson builds directly on antiderivatives (`integrals_intro`) and feeds into applications of integration, differential equations, and probability (where $\\int f(x)\\,dx$ computes areas under density curves).

**Why it matters for exams:** Bagrut 5-unit and university Calc 1 papers routinely combine FTC evaluation, area between curves, and absolute-value splitting in a single multi-part question worth 15–20 points. Examiners reward a clear sketch and labeled integrand, not just a final number.

**Transfer skill:** The "find intersections → test point → integrate difference" pipeline applies whenever you compare two changing quantities — not only in math, but also in economics (surplus) and physics (work between force curves).""",
    "body_he_md": """אינטגרלים מסוימים הם מנוע החישוב מאחורי חצי מחדו״א 1 וחלק ניכר מפיזיקה בסיסית.

**במסלול הלימוד:** השיעור בונה ישירות על קדומות (`integrals_intro`) ומזין יישומי אינטגרציה, משוואות דיפרנציאליות והסתברות (שם $\\int f\\,dx$ מחשב שטח תחת עקומת צפיפות).

**למה זה חשוב לבחינות:** בבגרות 5 יחידות ובחדו״א 1 משלבים שגרה FTC, שטח בין עקומות ופיצול ערך מוחלט בשאלה רב-שלבית של 15–20 נקודות. בודקים מעריכים שרטוט ברור ואינטגרנד מתויג, לא רק מספר סופי.

**מיומנות העברה:** הצינור "חיתוכים → נקודת בדיקה → אינטגרל של הפרש" חל בכל השוואה בין שתי כמויות משתנות — לא רק במתמטיקה, אלא גם בכלכלה (עודף) ובפיזיקה (עבודה בין עקומות כוח).""",
}

BEFORE_EXAM = {
    "body_en_md": """**FTC Part 2 (evaluation):**
$$\\int_a^b f(x)\\,dx = F(b)-F(a) = \\Big[F(x)\\Big]_a^b$$

**FTC Part 1 (differentiation):**
$$\\frac{d}{dx}\\int_a^{g(x)}f(t)\\,dt = f(g(x))\\cdot g'(x)$$

**Leibniz (both limits vary):**
$$\\frac{d}{dx}\\int_{g(x)}^{h(x)} f(t)\\,dt = f(h)h'-f(g)g'$$

**Area algorithms:**
- Unsigned: find zeros → split → remove $|\\cdot|$ with correct sign → sum pieces.
- Between curves: find intersections → test point → integrate (top − bottom).

**Exam tip:** For area problems, always sketch the region — a 30-second drawing prevents major sign and limit errors.

**Common definite integrals to memorize:**
$$\\int_0^1 x^n\\,dx=\\frac{1}{n+1}, \\quad \\int_0^\\pi\\sin x\\,dx=2, \\quad \\int_0^{\\pi/2}\\cos x\\,dx=1$$

**Last review:** Say each formula out loud once, then solve one checkpoint without looking.

**Time management:** FTC evaluation problems should take under 3 minutes; area-between-curves with a sketch, under 8 minutes on a typical exam.""",
    "body_he_md": """**FTC 2 (חישוב):**
$$\\int_a^b f(x)\\,dx=F(b)-F(a)=\\Big[F(x)\\Big]_a^b$$

**FTC 1 (גזירה):**
$$\\frac{d}{dx}\\int_a^{g(x)}f(t)\\,dt=f(g(x))\\cdot g'(x)$$

**לייבניץ (שני גבולות משתנים):**
$$\\frac{d}{dx}\\int_{g(x)}^{h(x)} f(t)\\,dt=f(h)h'-f(g)g'$$

**אלגוריתמי שטח:**
- גיאומטרי: אפסים → פיצול → הסרת $|\\cdot|$ → סיכום.
- בין עקומות: חיתוכים → נקודת בדיקה → $\\int$(עליון − תחתון).

**טיפ לבחינה:** סרטטו תמיד את האזור — 30 שניות מונעות טעויות סימן וגבולות.

**אינטגרלים נפוצים לזכור:**
$$\\int_0^1 x^n\\,dx=\\frac{1}{n+1}, \\quad \\int_0^\\pi\\sin x\\,dx=2, \\quad \\int_0^{\\pi/2}\\cos x\\,dx=1$$

**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint אחד בלי להסתכל.

**ניהול זמן:** חישוב FTC — פחות מ-3 דקות; שטח בין עקומות עם שרטוט — פחות מ-8 דקות בבחינה טיפוסית.""",
}

SUMMARY = {
    "body_en_md": """- The definite integral $\\int_a^b f(x)\\,dx$ measures **signed net area**; use $\\int|f|\\,dx$ for unsigned geometric area.
- **FTC Part 2:** $\\int_a^b f\\,dx = F(b)-F(a)$ — antiderivatives compute definite integrals without Riemann sums.
- **FTC Part 1:** $\\frac{d}{dx}\\int_a^{g(x)}f(t)\\,dt=f(g(x))g'(x)$ — differentiation undoes integration; include the chain rule.
- **Area between curves:** find intersections, test which function is on top, integrate (top − bottom) on each subinterval.
- **Absolute values:** split at zeros, remove bars with correct sign on each piece, then sum.
- Always sketch the region and label the integrand before evaluating — setup earns partial credit on exams.""",
    "body_he_md": """- האינטגרל המסוים $\\int_a^b f\\,dx$ מודד **שטח נטו עם סימן**; השתמשו ב-$\\int|f|\\,dx$ לשטח גיאומטרי.
- **FTC 2:** $F(b)-F(a)$ — קדומות מחשבות אינטגרלים מסוימים בלי סכומי רימן.
- **FTC 1:** $\\frac{d}{dx}\\int_a^{g(x)}f(t)dt=f(g(x))g'(x)$ — גזירה מבטלת אינטגרציה; כלול כלל שרשרת.
- **שטח בין עקומות:** חיתוכים, בדיקת מי למעלה, אינטגרל (עליון − תחתון) בכל תת-קטע.
- **ערכים מוחלטים:** פיצול באפסים, הסרת ערך מוחלט עם סימן נכון, סיכום.
- שרטטו תמיד והציגו אינטגרנד לפני חישוב — הגדרה מזכה בניקוד חלקי בבחינות.""",
}

EXPLANATIONS = [
    {
        "en": """**Why this is correct:**
Apply FTC Part 2 to $\\int_1^3(x^2-1)\\,dx$. Antiderivative: $F(x)=x^3/3-x$. Then $F(3)=9-3=6$ and $F(1)=1/3-1=-2/3$, so the integral equals $6-(-2/3)=20/3$.

**How to think about it:**
Integrate term by term using the power rule, then evaluate at bounds. Bracket notation $[x^3/3-x]_1^3$ keeps upper and lower substitutions organized.

**Common slip:**
Arithmetic errors when subtracting $F(1)$ — especially $1/3-1=-2/3$, not $+2/3$. Another error: forgetting that definite integrals need no $+C$.

**Exam tip:**
After computing, estimate: on $[1,3]$, $x^2-1\\ge 0$, so the answer must be positive. $20/3\\approx 6.7$ is reasonable.""",
        "he": """**למה זה נכון:**
יישום FTC חלק 2 על $\\int_1^3(x^2-1)\\,dx$. קדומה: $F(x)=x^3/3-x$. אז $F(3)=6$ ו-$F(1)=-2/3$, והאינטגרל שווה $6-(-2/3)=20/3$.

**איך לחשוב על זה:**
אינטגרציה איבר-איבר לפי כלל החזקה, ואז הצבה בגבולות. סימון $[x^3/3-x]_1^3$ מארגן את ההצבות.

**טעות נפוצה:**
שגיאות חשבון בחיסור $F(1)$ — במיוחד $1/3-1=-2/3$, לא $+2/3$. טעות נוספת: $+C$ מיותר באינטגרל מסוים.

**טיפ לבחינה:**
אחרי החישוב, העריכו: ב-$[1,3]$, $x^2-1\\ge 0$, ולכן התשובה חייבת להיות חיובית. $20/3\\approx 6.7$ סביר. כתבו $[F(x)]_a^b$ לפני הצבת מספרים — בודקים מעניקים ניקוד על ההגדרה.""",
    },
    {
        "en": """**Why this is correct:**
$\\int_0^\\pi\\sin x\\,dx=[-\\cos x]_0^\\pi=(-\\cos\\pi)-(-\\cos 0)=1+1=2$. On $[0,\\pi]$, sine is non-negative, so signed area equals geometric area.

**How to think about it:**
Antiderivative of $\\sin x$ is $-\\cos x$ (watch the minus sign). Unit-circle values: $\\cos\\pi=-1$, $\\cos 0=1$.

**Common slip:**
Sign error on the antiderivative ($+\\cos x$ instead of $-\\cos x$). Confusing $\\int_0^\\pi\\sin x\\,dx=2$ with $\\int_0^{2\\pi}\\sin x\\,dx=0$.

**Exam tip:**
When the interval is exactly one arch of sine, the answer is $2$ — a standard result worth memorizing alongside $\\int_0^{\\pi/2}\\cos x\\,dx=1$.""",
        "he": """**למה זה נכון:**
$\\int_0^\\pi\\sin x\\,dx=[-\\cos x]_0^\\pi=(-\\cos\\pi)-(-\\cos 0)=1+1=2$. ב-$[0,\\pi]$, סינוס אי-שלילי, ולכן שטח עם סימן שווה לשטח גיאומטרי תחת קשת אחת.

**איך לחשוב על זה:**
קדומה של $\\sin x$ היא $-\\cos x$ (שימו לב למינוס — זו הטעות הנפוצה). ערכי מעגל יחידה: $\\cos\\pi=-1$, $\\cos 0=1$. הציבו בגבולות העליון והתחתון לפי סימון $[-\\cos x]_0^\\pi$.

**טעות נפוצה:**
שגיאת סימן בקדומה ($+\\cos x$ במקום $-\\cos x$). בלבול בין $\\int_0^\\pi\\sin x\\,dx=2$ (קשת אחת) ל-$\\int_0^{2\\pi}\\sin x\\,dx=0$ (מחזור שלם עם ביטול סימני).

**טיפ לבחינה:**
כשהקטע הוא בדיוק קשת אחת של סינוס, התשובה $2$ — תוצאה סטנדרטית לזכור לצד $\\int_0^{\\pi/2}\\cos x\\,dx=1$. אל תערבבו עם מחזור שלם.""",
    },
    {
        "en": """**Why this is correct:**
$\\int_1^e\\frac{1}{x}\\,dx=[\\ln x]_1^e=\\ln e-\\ln 1=1-0=1$. This is the defining integral for the natural logarithm.

**How to think about it:**
$1/x$ is the one power that does NOT use the power rule — its antiderivative is $\\ln|x|$. On $[1,e]$, $x>0$, so $\\ln|x|=\\ln x$.

**Common slip:**
Applying $\\int x^n\\,dx$ with $n=-1$ (division by zero). Forgetting that $\\ln 1=0$, not $1$.

**Exam tip:**
$\\int_1^e\\frac{1}{x}\\,dx=1$ appears frequently as a quick-check question. Link it mentally to: log grows from 0 to 1 as $x$ goes from 1 to $e$.""",
        "he": """**למה זה נכון:**
$\\int_1^e\\frac{1}{x}\\,dx=[\\ln x]_1^e=\\ln e-\\ln 1=1-0=1$. זה האינטגרל המגדיר של הלוגריתם הטבעי — הקשר בין $e$ לבין $\\ln$.

**איך לחשוב על זה:**
$1/x$ הוא המקרה $n=-1$ שבו **אסור** להשתמש בכלל החזקה — קדומתו $\\ln|x|$. ב-$[1,e]$, $x>0$, ולכן $\\ln|x|=\\ln x$ ללא ערך מוחלט. זהו אחד משלושת האינטגרלים שכדאי לזכור בעל פה.

**טעות נפוצה:**
שימוש ב-$\\int x^n\\,dx$ עם $n=-1$ (חלוקה באפס). שכחה ש-$\\ln 1=0$ ולא $1$. כתיבת $\\ln e=0$ במקום $1$.

**טיפ לבחינה:**
$\\int_1^e\\frac{1}{x}\\,dx=1$ מופיע לעיתים קרובות. קשרו בראש: לוג גדל מ-0 ל-1 כש-$x$ מ-1 ל-$e$. זכרו $\\ln e=1$, $\\ln 1=0$.""",
    },
    {
        "en": """**Why this is correct:**
By FTC Part 1, if $G(x)=\\int_0^x\\sin(t^2)\\,dt$, then $G'(x)=\\sin(x^2)$. The upper limit is $x$, so no extra chain-rule factor is needed.

**How to think about it:**
FTC Part 1 says "differentiate the upper limit by substituting it into the integrand." Here the integrand is $\\sin(t^2)$ and the limit is $x$, giving $\\sin(x^2)$.

**Common slip:**
Trying to integrate $\\sin(t^2)$ first (it has no elementary antiderivative — Fresnel integrals). Adding a spurious factor of $2x$ as if the limit were $x^2$.

**Exam tip:**
When the upper limit is plain $x$ and the lower limit is a constant, the derivative is simply $f(x)$ — one line of work, full credit.""",
        "he": """**למה זה נכון:**
לפי FTC חלק 1, אם $G(x)=\\int_0^x\\sin(t^2)\\,dt$, אז $G'(x)=\\sin(x^2)$. הגבול העליון הוא $x$ — אין צורך בגורם שרשרת נוסף.

**איך לחשוב על זה:**
FTC חלק 1: גזרו את הגבול העליון והציבו במקום $t$ באינטגרנד. כאן $f(t)=\\sin(t^2)$ והגבול $x$, ולכן $G'(x)=\\sin(x^2)$. זה שונה מגבול $x^2$ שבו היינו צריכים $2x$.

**טעות נפוצה:**
ניסיון לאינטגרל $\\sin(t^2)$ — אין קדומה אלמנטרית (אינטגרלי פרנל). הוספת $2x$ מיותר כאילו הגבול $x^2$ במקום $x$.

**טיפ לבחינה:**
גבול עליון $x$ ותחתון קבוע → הנגזרת $f(x)$ בשורה אחת. אל תנסו לאינטגרל — זו מלכודת מכוונת בבחינות חדו״א 1.""",
    },
    {
        "en": """**Why this is correct:**
Intersections: $x^2=4\\Rightarrow x=\\pm 2$. On $[-2,2]$, the line $y=4$ is above $y=x^2$. Area: $A=\\int_{-2}^2(4-x^2)\\,dx=[4x-x^3/3]_{-2}^2=(8-8/3)-(-8+8/3)=32/3$.

**How to think about it:**
Horizontal line vs. parabola — find where they meet, confirm which is on top (test $x=0$: $4>0$), integrate (top − bottom). Symmetry lets you compute $2\\int_0^2(4-x^2)\\,dx$ as a check.

**Common slip:**
Using limits $[0,2]$ only and missing the symmetric half. Integrating $x^2-4$ instead of $4-x^2$ (wrong order).

**Exam tip:**
Parabola-under-line problems are standard Calc 1 fare. Write the intersection $x$-values as limits before antidifferentiating — setup is half the grade.""",
        "he": """**למה זה נכון:**
חיתוכים: $x^2=4\\Rightarrow x=\\pm 2$. ב-$[-2,2]$, הישר $y=4$ מעל $y=x^2$. $A=\\int_{-2}^2(4-x^2)\\,dx=[4x-x^3/3]_{-2}^2=32/3$.

**איך לחשוב על זה:**
ישר אופקי מול פרבולה — מצאו חיתוכים, בדקו מי למעלה (ב-$x=0$: $4>0$), הגדירו $\\int$(עליון − תחתון). סימטריה סביב ציר $y$ מאפשרת $2\\int_0^2(4-x^2)\\,dx$ כבדיקה מהירה.

**טעות נפוצה:**
גבולות $[0,2]$ בלבד — מפספסים חצי מהשטח הסימטרי. אינטגרל של $x^2-4$ במקום $4-x^2$ (סדר הפוך).

**טיפ לבחינה:**
כתבו קואורדינטות חיתוך כגבולות לפני קדומה — ההגדרה שווה חצי מהציון. $32/3\\approx 10.7$ — סביר לשטח בין פרבולה לישר $y=4$.""",
    },
    {
        "en": """**Why this is correct:**
Split at $x=1$ where $|x-1|$ changes: $\\int_0^1(1-x)\\,dx+\\int_1^2(x-1)\\,dx$. First piece: $[x-x^2/2]_0^1=1/2$. Second: $[x^2/2-x]_1^2=1/2$. Total $=1$.

**How to think about it:**
Absolute value of linear function → one breakpoint at the zero ($x=1$). On each side, replace $|x-1|$ with the expression without bars (check sign with a test point).

**Common slip:**
Integrating $|x-1|$ directly without splitting — FTC on $|x-1|$ fails because the integrand is not smooth at $x=1$. Another error: wrong expressions $(x-1)$ on both sides.

**Exam tip:**
$\\int_0^2|x-1|\\,dx=1$ is a classic "draw the V-shape" problem. Sketching $y=|x-1|$ shows two triangles of area $1/2$ each — geometric confirmation.""",
        "he": """**למה זה נכון:**
פיצול ב-$x=1$: $\\int_0^1(1-x)\\,dx+\\int_1^2(x-1)\\,dx$. חלק ראשון: $1/2$. שני: $1/2$. סה״כ $=1$.

**איך לחשוב על זה:**
ערך מוחלט של פונקציה לינארית → נקודת שבירה אחת באפס ($x=1$). בכל צד — החלפת $|x-1|$ בביטוי ללא ערך מוחלט (בדיקת סימן).

**טעות נפוצה:**
אינטגרל ישיר על $|x-1|$ בלי פיצול — הפונקציה לא חלקה ב-$x=1$. ביטוי שגוי בשני הצדדים.

**טיפ לבחינה:**
$\\int_0^2|x-1|\\,dx=1$ — בעיית "צייר V". השרטוט מראה שני משולשים בשטח $1/2$ — אימות גיאומטרי.""",
    },
    {
        "en": """**Why this is correct:**
$\\frac{d}{dx}\\int_1^{x^2}\\cos(t)\\,dt=\\cos(x^2)\\cdot 2x=2x\\cos(x^2)$ by FTC Part 1 plus chain rule. Substitute upper limit $x^2$ into $\\cos(t)$, then multiply by $\\frac{d}{dx}(x^2)=2x$.

**How to think about it:**
Template: $\\frac{d}{dx}\\int_a^{g(x)}f(t)\\,dt=f(g(x))\\cdot g'(x)$. Here $g(x)=x^2$, $f(t)=\\cos t$, so $f(g(x))=\\cos(x^2)$ and $g'(x)=2x$.

**Common slip:**
Forgetting the $2x$ factor — the most common FTC Part 1 error. Writing $\\cos(x^2)$ alone earns partial credit at best.

**Exam tip:**
Circle the upper limit before differentiating. If it is not plain $x$, chain rule is mandatory — examiners deliberately use $x^2$, $2x$, or $\\sin x$ as limits.""",
        "he": """**למה זה נכון:**
$\\frac{d}{dx}\\int_1^{x^2}\\cos(t)\\,dt=\\cos(x^2)\\cdot 2x=2x\\cos(x^2)$ לפי FTC חלק 1 ושרשרת. הציבו $x^2$ ב-$\\cos(t)$, הכפילו ב-$\\frac{d}{dx}(x^2)=2x$.

**איך לחשוב על זה:**
תבנית: $\\frac{d}{dx}\\int_a^{g(x)}f(t)\\,dt=f(g(x))\\cdot g'(x)$. כאן $g(x)=x^2$, $f(t)=\\cos t$, ולכן $f(g(x))=\\cos(x^2)$ ו-$g'(x)=2x$. הגבול התחתון $1$ הוא קבוע — אין תרומה נוספת.

**טעות נפוצה:**
שכחת $2x$ — הטעות הנפוצה ביותר ב-FTC 1. כתיבת $\\cos(x^2)$ בלבד מזכה בניקוד חלקי לכל היותר. בלבול עם $\\int_0^{x^2}$ שבו אין חיסור מגבול תחתון.

**טיפ לבחינה:**
סמנו את הגבול העליון לפני גזירה. אם אינו $x$ פשוט — שרשרת חובה. כתבו $f(g(x))\\cdot g'(x)$ לפני הצבה — בודקים מצפים לראות את שני הגורמים.""",
    },
    {
        "en": """**Why this is correct:**
Intersection: $\\sin x=\\cos x\\Rightarrow x=\\pi/4$ on $[0,\\pi/2]$. On $[0,\\pi/4]$: $\\cos x\\ge\\sin x$; on $[\\pi/4,\\pi/2]$: $\\sin x\\ge\\cos x$. $A=\\int_0^{\\pi/4}(\\cos x-\\sin x)dx+\\int_{\\pi/4}^{\\pi/2}(\\sin x-\\cos x)dx=2(\\sqrt{2}-1)$.

**How to think about it:**
Trig area problems require splitting at the angle where the curves cross. Antiderivatives: $\\int(\\cos x-\\sin x)dx=\\sin x+\\cos x$.

**Common slip:**
Using one integral over the whole interval without splitting — the wrong curve becomes "top." Evaluating $\\sin x=\\cos x$ at $x=0$ (only $\\pi/4$ is in $(0,\\pi/2)$).

**Exam tip:**
$2(\\sqrt{2}-1)\\approx 0.83$ is less than 1 — reasonable for the lens-shaped region between sine and cosine on a quarter period. Sketch both curves to see the swap at $45°$.""",
        "he": """**למה זה נכון:**
חיתוך: $\\sin x=\\cos x\\Rightarrow x=\\pi/4$ ב-$[0,\\pi/2]$. ב-$[0,\\pi/4]$: $\\cos x\\ge\\sin x$; ב-$[\\pi/4,\\pi/2]$: $\\sin x\\ge\\cos x$. $A=2(\\sqrt{2}-1)$.

**איך לחשוב על זה:**
בעיות שטח טריגונומטריות דורשות פיצול בזווית החיתוך. קדומה: $\\int(\\cos x-\\sin x)dx=\\sin x+\\cos x$.

**טעות נפוצה:**
אינטגרל אחד על כל הקטע בלי פיצול — העקומה ה"עליונה" שגויה. חיתוך ב-$x=0$ (רק $\\pi/4$ ב-$(0,\\pi/2)$).

**טיפ לבחינה:**
$2(\\sqrt{2}-1)\\approx 0.83$ — סביר לאזור עדשה בין סינוס לקוסינוס. שרטטו — החלפה ב-$45°$. פצלו ב-$\\pi/4$ לפני חישוב — אינטגרל אחד על כל הקטע נותן סימן שגוי.""",
    },
]


def word_count(text: str) -> int:
    import re
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def hebrew_body_weak(body_he: str, body_en: str) -> bool:
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    he_chars = len(__import__("re").findall(r"[\u0590-\u05FF]", he))
    lat = len(__import__("re").findall(r"[a-zA-Z]{3,}", he))
    ratio = he_chars / (he_chars + lat + 1)
    if word_count(he) / max(word_count(en), 1) < 0.55:
        return True
    if ratio < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


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


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    we_idx = 0
    cp_idx = 0

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec["body_en_md"] = INTRO["body_en_md"]
            sec["body_he_md"] = INTRO["body_he_md"]
        elif kind == "definition":
            sec["body_en_md"] = DEFINITION["body_en_md"]
            sec["body_he_md"] = DEFINITION["body_he_md"]
        elif kind == "theory":
            sec["body_en_md"] = THEORY["body_en_md"]
            sec["body_he_md"] = THEORY["body_he_md"]
        elif kind == "worked_example":
            src = [WE1, WE2, WE3][we_idx]
            sec["body_en_md"] = src["body_en_md"]
            sec["body_he_md"] = src["body_he_md"]
            we_idx += 1
        elif kind == "checkpoint":
            if cp_idx == 0:
                sec["checkpoint_solution_en"] = CHECKPOINT1_EN
                sec["checkpoint_solution_he"] = CHECKPOINT1_HE
            else:
                sec["checkpoint_solution_en"] = CHECKPOINT2_EN
                sec["checkpoint_solution_he"] = CHECKPOINT2_HE
            cp_idx += 1
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
        q["explanation_en"] = EXPLANATIONS[i]["en"]
        q["explanation_he"] = EXPLANATIONS[i]["he"]

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
        sys.exit(1)
    print("OK — all gates passed")
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")

    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
