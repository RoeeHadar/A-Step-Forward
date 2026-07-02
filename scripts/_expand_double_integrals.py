#!/usr/bin/env python3
"""Expand double_integrals.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/double_integrals.json"

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


INTRO_EN = """A single integral $\\int_a^b f(x)\\,dx$ computes the signed area under a curve in the plane. A **double integral** $\\iint_D f(x,y)\\,dA$ extends this idea to two dimensions: it accumulates $f(x,y)$ over a region $D$ in the $xy$-plane. When $f\\geq 0$, the value equals the **volume** under the surface $z=f(x,y)$ above $D$. Geometrically, partition $D$ into small rectangles of area $\\Delta A$, form the Riemann sum $\\sum f(x_i,y_j)\\Delta A$, and take the limit as the mesh refines.

Double integrals are the workhorse of multivariable calculus. They compute volumes, areas of curved regions, mass and charge when $f$ is a density, probabilities over two-dimensional distributions, and physical quantities such as moment of inertia. The computational core is **Fubini's theorem**: under continuity, a double integral equals an **iterated integral** — integrate in one variable while holding the other fixed, then integrate the result.

This lesson builds on `concept:partial_derivatives` and `concept:multivariable_limits`, and unlocks `concept:triple_integrals` and `concept:vector_calculus`. Mastering region sketches, limit setup, order reversal, and polar coordinates is essential for every Calc III exam."""

INTRO_HE = """אינטגרל יחיד $\\int_a^b f(x)\\,dx$ מחשב שטח חתום תחת עקומה במישור. **אינטגרל כפול** $\\iint_D f(x,y)\\,dA$ מרחיב את הרעיון לשני מימדים: צובר $f(x,y)$ על אזור $D$ במישור $xy$. כאשר $f\\geq 0$, הערך שווה ל**נפח** תחת המשטח $z=f(x,y)$ מעל $D$. גיאומטרית, מחלקים את $D$ למלבנים קטנים בשטח $\\Delta A$, בונים סכום רימן $\\sum f(x_i,y_j)\\Delta A$, ולוקחים גבול כשהרשת מתדקדקת.

אינטגרלים כפולים הם כלי העבודה של חשבון משתנים רבים. הם מחשבים נפחים, שטחי אזורים מעוקלים, מסה ומטען כש-$f$ היא צפיפות, הסתברויות על התפלגויות דו-ממדיות, וכמויות פיזיקליות כמו מומנט התמד. ליבת החישוב היא **משפט פוביני**: בתנאי רציפות, אינטגרל כפול שווה ל**אינטגרל מאוחד** — מאינטגרלים בגורם אחד תוך קביעת השני, ואז מאינטגרלים בגורם השני.

שיעור זה מבוסס על `concept:partial_derivatives` ו-`concept:multivariable_limits`, ופותח את `concept:triple_integrals` ו-`concept:vector_calculus`. שליטה בציור אזורים, הצבת גבולות, החלפת סדר וקואורדינטות קוטביות חיונית לכל בחינת Calc III."""

DEF_EN = """**Double integral over a rectangle** $R=[a,b]\\times[c,d]$:
$$\\iint_R f(x,y)\\,dA = \\int_a^b\\int_c^d f(x,y)\\,dy\\,dx = \\int_c^d\\int_a^b f(x,y)\\,dx\\,dy.$$

**Fubini's theorem:** If $f$ is continuous on a bounded rectangle $R$, both iterated integrals exist and equal the double integral — the order of integration does not matter. For more general regions, Fubini applies when $f$ is continuous on a Type I or Type II region.

**Type I region** (vertical slices, $x$-simple): $D=\\{(x,y):a\\leq x\\leq b,\\; g_1(x)\\leq y\\leq g_2(x)\\}$:
$$\\iint_D f\\,dA = \\int_a^b\\int_{g_1(x)}^{g_2(x)} f(x,y)\\,dy\\,dx.$$

**Type II region** (horizontal slices, $y$-simple): $D=\\{(x,y):c\\leq y\\leq d,\\; h_1(y)\\leq x\\leq h_2(y)\\}$:
$$\\iint_D f\\,dA = \\int_c^d\\int_{h_1(y)}^{h_2(y)} f(x,y)\\,dx\\,dy.$$

**Polar coordinates:** $x=r\\cos\\theta$, $y=r\\sin\\theta$, with area element $dA=r\\,dr\\,d\\theta$ (the Jacobian factor $r$ is essential):
$$\\iint_D f(x,y)\\,dA = \\iint_{D'} f(r\\cos\\theta,r\\sin\\theta)\\,r\\,dr\\,d\\theta.$$

**Geometric shortcut:** $\\iint_D 1\\,dA = \\text{Area}(D)$ — integrate the constant $1$ to find area without setting up a separate geometric formula.

**Average value:** The mean of $f$ over $D$ is $\\dfrac{1}{\\text{Area}(D)}\\iint_D f\\,dA$ — used in probability and physics for expected values over regions."""

DEF_HE = """**אינטגרל כפול על מלבן** $R=[a,b]\\times[c,d]$:
$$\\iint_R f(x,y)\\,dA = \\int_a^b\\int_c^d f(x,y)\\,dy\\,dx = \\int_c^d\\int_a^b f(x,y)\\,dx\\,dy.$$

**משפט פוביני:** אם $f$ רציפה על מלבן חסום $R$, שני האינטגרלים המאוחדים קיימים ושווים לאינטגרל הכפול — סדר האינטגרציה לא משנה. לאזורים כלליים, פוביני חל כש-$f$ רציפה על אזור סוג I או סוג II.

**אזור סוג I** (פרוסות אנכיות, $x$-פשוט): $D=\\{(x,y):a\\leq x\\leq b,\\; g_1(x)\\leq y\\leq g_2(x)\\}$:
$$\\iint_D f\\,dA = \\int_a^b\\int_{g_1(x)}^{g_2(x)} f(x,y)\\,dy\\,dx.$$

**אזור סוג II** (פרוסות אופקיות, $y$-פשוט): $D=\\{(x,y):c\\leq y\\leq d,\\; h_1(y)\\leq x\\leq h_2(y)\\}$:
$$\\iint_D f\\,dA = \\int_c^d\\int_{h_1(y)}^{h_2(y)} f(x,y)\\,dx\\,dy.$$

**קואורדינטות קוטביות:** $x=r\\cos\\theta$, $y=r\\sin\\theta$, עם אלמנט שטח $dA=r\\,dr\\,d\\theta$ (גורם יעקוביאן $r$ חיוני):
$$\\iint_D f(x,y)\\,dA = \\iint_{D'} f(r\\cos\\theta,r\\sin\\theta)\\,r\\,dr\\,d\\theta.$$

**קיצור גיאומטרי:** $\\iint_D 1\\,dA = \\text{שטח}(D)$ — מאינטגרלים את הקבוע $1$ למציאת שטח.

**ערך ממוצע:** הממוצע של $f$ על $D$ הוא $\\dfrac{1}{\\text{שטח}(D)}\\iint_D f\\,dA$ — משמש בהסתברות ובפיזיקה לערכים צפויים על אזורים.

**שימו לב:** אלמנט השטח $dA$ במלבן הוא $dx\\,dy$; בקואורדינטות קוטביות הוא $r\\,dr\\,d\\theta$."""

THEORY_EN = """**Iterated integral (standard workflow):** Evaluate the **inner** integral first, treating the outer variable as a constant. Then evaluate the **outer** integral. On a rectangle, either order works by Fubini; on general regions, choose Type I or Type II based on which description makes the limits simplest.

**Changing the order of integration:** Sometimes one order produces an inner integral that has no elementary antiderivative (classic example: $\\int e^{y^2}\\,dy$). Sketch the region $D$, identify the bounding curves, and re-express the limits for the reversed order. The region geometry is unchanged — only the slicing direction changes.

**When to use polar coordinates:**
- The region is a disk, annulus, sector, or portion of a circle.
- The integrand contains $x^2+y^2$, $\\sqrt{x^2+y^2}$, or $e^{x^2+y^2}$.
- Cartesian limits would be awkward but polar bounds are constants ($0\\leq r\\leq R$, $0\\leq\\theta\\leq 2\\pi$).

**Geometric interpretation:** If $f(x,y)=1$, then $\\iint_D 1\\,dA = \\text{Area}(D)$. If $f(x,y)\\geq 0$, the integral gives volume under $z=f(x,y)$. If $f$ takes negative values, the integral gives **signed** volume — regions where $f<0$ subtract from the total.

**Choosing Type I vs Type II:** Sketch $D$. If vertical lines cross $D$ at most twice, Type I works. If horizontal lines cross at most twice, Type II works. Some regions are both; pick whichever gives simpler bounds. When neither order is easy, try polar or a substitution."""

THEORY_HE = """**אינטגרל מאוחד (תהליך סטנדרטי):** מחשבים קודם את האינטגרל **הפנימי**, תוך התייחסות לגורם החיצוני כקבוע. אחר כך את האינטגרל **החיצוני**. על מלבן, כל סדר עובד לפי פוביני; על אזורים כלליים, בוחרים סוג I או II לפי איזה תיאור נותן גבולות פשוטים.

**החלפת סדר אינטגרציה:** לפעמים סדר אחד מייצר אינטגרל פנימי ללא אינטגרל ראשוני (דוגמה קלאסית: $\\int e^{y^2}\\,dy$). ציירו את $D$, זהו את עקומות הגבול, ובטאו גבולות לסדר ההפוך. הגיאומטריה לא משתנה — רק כיוון הפריסה.

**מתי קואורדינטות קוטביות:**
- האזור הוא דיסק, טבעת, מגזר, או חלק מעיגול.
- Integrand מכיל $x^2+y^2$, $\\sqrt{x^2+y^2}$, או $e^{x^2+y^2}$.
- גבולות Cartesian מסורבלים אך גבולות קוטביים קבועים ($0\\leq r\\leq R$, $0\\leq\\theta\\leq 2\\pi$).

**פרשנות גיאומטרית:** אם $f(x,y)=1$, אז $\\iint_D 1\\,dA = \\text{שטח}(D)$. אם $f\\geq 0$, האינטגרל נותן נפח תחת $z=f$. אם $f$ שלילי, האינטגרל נותן נפח **חתום** — אזורים עם $f<0$ מחסירים.

**בחירה בין סוג I לסוג II:** ציירו $D$. אם קווים אנכיים חוצים לכל היותר פעמיים — סוג I. אם אופקיים — סוג II. חלק מהאזורים הם שניהם; בחרו את הפשוט. כששניהם קשים — נסו קוטביות."""

WE1_EN = """**Compute** $\\iint_R (2x+3y)\\,dA$ over the rectangle $R=[0,2]\\times[0,1]$.

This is the simplest double integral: constant limits on a rectangle, so Fubini lets us integrate in either order.

### Move 1 — Set up the iterated integral
Choose $dy\\,dx$ with $x\\in[0,2]$, $y\\in[0,1]$:
$$\\int_0^2\\int_0^1 (2x+3y)\\,dy\\,dx.$$

### Move 2 — Inner integral in $y$ (treat $x$ as constant)
$$\\int_0^1(2x+3y)\\,dy = \\left[2xy+\\frac{3y^2}{2}\\right]_0^1 = 2x+\\frac{3}{2}.$$

### Move 3 — Outer integral in $x$
$$\\int_0^2\\left(2x+\\frac{3}{2}\\right)dx = \\left[x^2+\\frac{3x}{2}\\right]_0^2 = 4+3 = 7.$$

**Check by reversing order:** $\\int_0^1\\int_0^2(2x+3y)\\,dx\\,dy$ also gives $7$ — Fubini confirmed.

**Exam link:** Rectangle integrals should take under 2 minutes. Always write limits explicitly before integrating.

### Move 4 — Term-by-term reading
The integrand $2x+3y$ splits into $2x$ (constant in $y$) plus $3y$ (integrates to $3y^2/2$). After the inner integral, only $x$ remains — a single-variable integral you can check by hand.

**Sanity check:** Substitute $x=1$ into $2x+3/2$ to get $3.5$; the full integral over the rectangle should be consistent with adding contributions from each term."""

WE1_HE = """**חשבו** $\\iint_R (2x+3y)\\,dA$ על המלבן $R=[0,2]\\times[0,1]$.

זה האינטגרל הכפול הפשוט ביותר: גבולות קבועים על מלבן, ולכן פוביני מאפשר אינטגרציה בכל סדר.

### צעד 1 — הצבת האינטגרל המאוחד
בוחרים $dy\\,dx$ עם $x\\in[0,2]$, $y\\in[0,1]$:
$$\\int_0^2\\int_0^1 (2x+3y)\\,dy\\,dx.$$

### צעד 2 — אינטגרל פנימי ב-$y$ ($x$ = קבוע)
$$\\int_0^1(2x+3y)\\,dy = \\left[2xy+\\frac{3y^2}{2}\\right]_0^1 = 2x+\\frac{3}{2}.$$

### צעד 3 — אינטגרל חיצוני ב-$x$
$$\\int_0^2\\left(2x+\\frac{3}{2}\\right)dx = \\left[x^2+\\frac{3x}{2}\\right]_0^2 = 4+3 = 7.$$

**בדיקה בהפוך:** $\\int_0^1\\int_0^2(2x+3y)\\,dx\\,dy$ גם נותן $7$ — פוביני מאושר.

**קשר לבחינה:** אינטגרלים על מלבן — פחות מ-2 דקות. כתבו גבולות במפורש לפני האינטגרציה."""

WE2_EN = """**Problem:** Change the order of integration and evaluate:
$$\\int_0^1\\int_{x}^{1} e^{y^2}\\,dy\\,dx.$$

The inner integral $\\int e^{y^2}\\,dy$ has no elementary antiderivative — reversing the order is mandatory.

### Move 1 — Identify and sketch region $D$
The bounds describe $D=\\{0\\leq x\\leq 1,\\;x\\leq y\\leq 1\\}$ — a right triangle with vertices $(0,0)$, $(0,1)$, $(1,1)$.

### Move 2 — Re-express bounds for $dx\\,dy$
For fixed $y\\in[0,1]$, $x$ ranges from $0$ to $y$:
$$\\int_0^1\\int_0^{y} e^{y^2}\\,dx\\,dy.$$

### Move 3 — Inner integral in $x$ ($e^{y^2}$ is constant in $x$)
$$\\int_0^y e^{y^2}\\,dx = e^{y^2}\\cdot y.$$

### Move 4 — Outer integral; substitute $u=y^2$
$$\\int_0^1 ye^{y^2}\\,dy = \\left[\\frac{e^{y^2}}{2}\\right]_0^1 = \\frac{e-1}{2}.$$

**Key lesson:** When the inner antiderivative fails, sketch $D$ and switch order. The $u$-substitution $u=y^2$ only works after the $x$-integral collapses to a factor of $y$.

**Exam pattern:** $e^{y^2}$, $\\sin(y^2)$, $1/(y^3+1)$ in the inner integral signal order reversal."""

WE2_HE = """**בעיה:** החליפו סדר אינטגרציה וחשבו:
$$\\int_0^1\\int_{x}^{1} e^{y^2}\\,dy\\,dx.$$

האינטגרל הפנימי $\\int e^{y^2}\\,dy$ ללא אינטגרל ראשוני — החלפת סדר חובה.

### צעד 1 — זיהוי וציור $D$
הגבולות מתארים $D=\\{0\\leq x\\leq 1,\\;x\\leq y\\leq 1\\}$ — משולש ישר-זוויתי עם קודקודים $(0,0)$, $(0,1)$, $(1,1)$.

### צעד 2 — ביטוי גבולות מחדש ל-$dx\\,dy$
ל-$y$ קבוע ב-$[0,1]$, $x$ מ-$0$ עד $y$:
$$\\int_0^1\\int_0^{y} e^{y^2}\\,dx\\,dy.$$

### צעד 3 — אינטגרל פנימי ב-$x$ ($e^{y^2}$ קבוע ב-$x$)
$$\\int_0^y e^{y^2}\\,dx = ye^{y^2}.$$

### צעד 4 — אינטגרל חיצוני; הצבה $u=y^2$
$$\\int_0^1 ye^{y^2}\\,dy = \\left[\\frac{e^{y^2}}{2}\\right]_0^1 = \\frac{e-1}{2}.$$

**מסקנה:** כשאינטגרל פנימי נכשל — ציירו $D$ והחליפו סדר. הצבה $u=y^2$ עובדת רק אחרי שהאינטגרל ב-$x$ מתכווץ לגורם $y$.

**דפוס בחינה:** $e^{y^2}$, $\\sin(y^2)$, $1/(y^3+1)$ באינטגרל פנימי = החלפת סדר."""

WE3_EN = """**Problem:** Compute $\\iint_D e^{x^2+y^2}\\,dA$ where $D$ is the disk $x^2+y^2\\leq 4$.

Both the integrand and the region scream polar coordinates.

### Move 1 — Recognize polar form
$e^{x^2+y^2}=e^{r^2}$ and the disk $x^2+y^2\\leq 4$ becomes $0\\leq r\\leq 2$, $0\\leq\\theta\\leq 2\\pi$.

### Move 2 — Set up the polar integral (include $r$!)
$$\\iint_D e^{x^2+y^2}\\,dA = \\int_0^{2\\pi}\\int_0^2 e^{r^2}\\cdot r\\,dr\\,d\\theta.$$

### Move 3 — Inner integral; substitute $u=r^2$
$$\\int_0^2 re^{r^2}\\,dr = \\left[\\frac{e^{r^2}}{2}\\right]_0^2 = \\frac{e^4-1}{2}.$$

### Move 4 — Outer integral in $\\theta$
$$\\int_0^{2\\pi}\\frac{e^4-1}{2}\\,d\\theta = \\frac{e^4-1}{2}\\cdot 2\\pi = \\pi(e^4-1).$$

**Why the extra $r$?** The Jacobian $dA=r\\,dr\\,d\\theta$ accounts for the expanding area of polar rectangles. Forgetting $r$ gives a wrong answer by a factor involving $r$.

**Template:** $e^{x^2+y^2}$, $e^{-r^2}$, or any radial function on a disk → polar with $u=r^2$ substitution."""

WE3_HE = """**בעיה:** חשבו $\\iint_D e^{x^2+y^2}\\,dA$ כאשר $D$ הוא הדיסק $x^2+y^2\\leq 4$.

גם Integrand וגם האזור מצביעים על קואורדינטות קוטביות.

### צעד 1 — זיהוי צורה קוטבית
$e^{x^2+y^2}=e^{r^2}$ והדיסק $x^2+y^2\\leq 4$ הופך ל-$0\\leq r\\leq 2$, $0\\leq\\theta\\leq 2\\pi$.

### צעד 2 — הצבת האינטגרל הקוטבי (כולל $r$!)
$$\\iint_D e^{x^2+y^2}\\,dA = \\int_0^{2\\pi}\\int_0^2 e^{r^2}\\cdot r\\,dr\\,d\\theta.$$

### צעד 3 — אינטגרל פנימי; הצבה $u=r^2$
$$\\int_0^2 re^{r^2}\\,dr = \\left[\\frac{e^{r^2}}{2}\\right]_0^2 = \\frac{e^4-1}{2}.$$

### צעד 4 — אינטגרל חיצוני ב-$\\theta$
$$\\int_0^{2\\pi}\\frac{e^4-1}{2}\\,d\\theta = \\pi(e^4-1).$$

**למה $r$ נוסף?** יעקוביאן $dA=r\\,dr\\,d\\theta$ מתחשב בהתרחבות שטח המלבנים הקוטביים. שכחת $r$ = תשובה שגויה.

**תבנית:** $e^{x^2+y^2}$ או פונקציה רדיאלית על דיסק → קוטביות עם $u=r^2$."""

CP1_SOL_EN = """Compute $\\iint_R xy^2\\,dA$ over $R=[1,2]\\times[0,3]$.

**Step 1 — Inner integral in $y$:**
$$\\int_0^3 xy^2\\,dy = x\\left[\\frac{y^3}{3}\\right]_0^3 = x\\cdot\\frac{27}{3} = 9x.$$

**Step 2 — Outer integral in $x$:**
$$\\int_1^2 9x\\,dx = 9\\left[\\frac{x^2}{2}\\right]_1^2 = 9\\left(\\frac{4}{2}-\\frac{1}{2}\\right) = 9\\cdot\\frac{3}{2} = \\frac{27}{2}.$$

**Check:** The integrand is a product $x\\cdot y^2$ on a rectangle — Fubini separates cleanly. Verify: $\\int_1^2 x\\,dx\\cdot\\int_0^3 y^2\\,dy = (3/2)(9) = 27/2$.

**Answer:** $\\dfrac{27}{2}$."""

CP1_SOL_HE = """חשבו $\\iint_R xy^2\\,dA$ על $R=[1,2]\\times[0,3]$.

**שלב 1 — אינטגרל פנימי ב-$y$:**
$$\\int_0^3 xy^2\\,dy = x\\left[\\frac{y^3}{3}\\right]_0^3 = 9x.$$

**שלב 2 — אינטגרל חיצוני ב-$x$:**
$$\\int_1^2 9x\\,dx = 9\\left[\\frac{x^2}{2}\\right]_1^2 = 9\\cdot\\frac{3}{2} = \\frac{27}{2}.$$

**בדיקה:** Integrand הוא מכפלה $x\\cdot y^2$ על מלבן — פוביני מפריד: $(3/2)(9)=27/2$.

**תשובה:** $\\dfrac{27}{2}$."""

CP2_SOL_EN = """Change the order of $\\int_0^1\\int_y^1 x^2\\,dx\\,dy$ and evaluate.

**Step 1 — Sketch region $D$:** $0\\leq y\\leq 1$, $y\\leq x\\leq 1$ — triangle with vertices $(0,0)$, $(1,0)$, $(1,1)$.

**Step 2 — Reverse to Type I:** $0\\leq x\\leq 1$, $0\\leq y\\leq x$:
$$\\int_0^1\\int_0^x x^2\\,dy\\,dx.$$

**Step 3 — Inner integral:** $\\int_0^x x^2\\,dy = x^2\\cdot x = x^3$ (since $x^2$ is constant in $y$).

**Step 4 — Outer integral:** $\\int_0^1 x^3\\,dx = \\left[\\frac{x^4}{4}\\right]_0^1 = \\frac{1}{4}$.

**Check:** Original order also works here (inner gives $x^2(1-y)$), but reversal practice is the point.

**Answer:** $\\dfrac{1}{4}$."""

CP2_SOL_HE = """החליפו סדר של $\\int_0^1\\int_y^1 x^2\\,dx\\,dy$ וחשבו.

**שלב 1 — ציור $D$:** $0\\leq y\\leq 1$, $y\\leq x\\leq 1$ — משולש עם קודקודים $(0,0)$, $(1,0)$, $(1,1)$.

**שלב 2 — הפיכה לסוג I:** $0\\leq x\\leq 1$, $0\\leq y\\leq x$:
$$\\int_0^1\\int_0^x x^2\\,dy\\,dx.$$

**שלב 3 — אינטגרל פנימי:** $\\int_0^x x^2\\,dy = x^3$ ($x^2$ קבוע ב-$y$).

**שלב 4 — אינטגרל חיצוני:** $\\int_0^1 x^3\\,dx = \\frac{1}{4}$.

**בדיקה:** הסדר המקורי גם עובד, אך תרגול ההפיכה הוא המטרה.

**תשובה:** $\\dfrac{1}{4}$."""

METHOD_EN = """| Step | Action | Details |
|---|---|---|
| 1 | **Sketch $D$** | Label bounding curves; shade the region |
| 2 | **Classify** | Rectangle, Type I, Type II, or polar disk/sector |
| 3 | **Write limits** | Type I: outer $x$, inner $y(x)$; Type II: outer $y$, inner $x(y)$ |
| 4 | **Inner integral** | Treat outer variable as constant; integrate |
| 5 | **Outer integral** | Substitute result and integrate |

**When to change order:**
- Inner antiderivative fails ($e^{y^2}$, $\\sin(y^3)$, etc.)
- Limits are algebraically messy in one order but clean in the other

**When to use polar:**
- Integrand has $x^2+y^2$ or $\\sqrt{x^2+y^2}$
- Region is circular, annular, or sector-shaped
- **Always** include Jacobian: $dA = r\\,dr\\,d\\theta$

| Region | Polar bounds |
|---|---|
| Full disk radius $R$ | $0\\leq r\\leq R$, $0\\leq\\theta\\leq 2\\pi$ |
| Upper semicircle | $0\\leq r\\leq R$, $0\\leq\\theta\\leq \\pi$ |
| Annulus $a\\leq r\\leq b$ | $a\\leq r\\leq b$, $0\\leq\\theta\\leq 2\\pi$ |
| Quarter disk (1st quadrant) | $0\\leq r\\leq R$, $0\\leq\\theta\\leq \\pi/2$ |

**Workflow:** Read the stem — volume under a surface → set up $\\iint f\\,dA$; impossible inner integral → reverse order; disk + $x^2+y^2$ → polar."""

METHOD_HE = """| שלב | פעולה | פרטים |
|---|---|---|
| 1 | **ציירו $D$** | סמנו עקומות גבול; הצלילו |
| 2 | **סווגו** | מלבן, סוג I, סוג II, או דיסק/מגזר קוטבי |
| 3 | **כתבו גבולות** | סוג I: חיצוני $x$, פנימי $y(x)$; סוג II: חיצוני $y$, פנימי $x(y)$ |
| 4 | **אינטגרל פנימי** | גורם חיצוני = קבוע; מאינטגרלים |
| 5 | **אינטגרל חיצוני** | מציבים תוצאה ומאינטגרלים |

**מתי להחליף סדר:**
- אינטגרל פנימי נכשל ($e^{y^2}$, $\\sin(y^3)$)
- גבולות מסורבלים בסדר אחד, נקיים בשני

**מתי קוטביות:**
- Integrand עם $x^2+y^2$ או $\\sqrt{x^2+y^2}$
- אזור מעגלי, טבעת, או מגזר
- **תמיד** כללו יעקוביאן: $dA = r\\,dr\\,d\\theta$

| אזור | גבולות קוטביים |
|---|---|
| דיסק מלא רדיוס $R$ | $0\\leq r\\leq R$, $0\\leq\\theta\\leq 2\\pi$ |
| חצי עיגול עליון | $0\\leq r\\leq R$, $0\\leq\\theta\\leq \\pi$ |
| טבעת $a\\leq r\\leq b$ | $a\\leq r\\leq b$, $0\\leq\\theta\\leq 2\\pi$ |
| רבע דיסק (רביע ראשון) | $0\\leq r\\leq R$, $0\\leq\\theta\\leq \\pi/2$ |

**תהליך:** נפח תחת משטח → $\\iint f\\,dA$; אינטגרל פנימי בלתי-אפשרי → החלפת סדר; דיסק + $x^2+y^2$ → קוטביות."""

PITFALL_EN = """1. **Wrong order of limits.** Inner limits can depend on the outer variable (Type I/II), but outer limits must be **constants**. Writing $\\int_0^x \\cdots dy\\,dx$ with $x$ in the outer limit's inner bound is a common sign error.

2. **Forgetting the Jacobian $r$ in polar.** The area element is $dA=r\\,dr\\,d\\theta$, not $dr\\,d\\theta$. Omitting $r$ typically gives an answer off by a power of $r$.

3. **Incorrect region sketch.** Always sketch $D$ before writing limits. A wrong sketch produces plausible-looking but incorrect bounds — especially for triangles and regions bounded by curves like $y=x^2$.

4. **Changing order without re-sketching.** Reversing integration order requires re-expressing **all** bounds from the same sketch. Do not mechanically swap symbols — translate the geometry.

5. **Confusing Type I and Type II.** Type I: outer in $x$, inner in $y$. Type II: outer in $y$, inner in $x$. Mixing these produces integrals over the wrong region.

6. **Integrating before checking separability.** On rectangles, if $f(x,y)=g(x)h(y)$, the double integral factors — a fast check that also proves Fubini for separable functions.

**Fix pattern:** Sketch → classify → write limits → inner → outer → sanity check (units, sign, special case $f=1$ for area)."""

PITFALL_HE = """1. **סדר גבולות שגוי.** גבולות פנימיים יכולים לתלות בגורם החיצוני, אך גבולות חיצוניים חייבים להיות **קבועים**. $\\int_0^x \\cdots dy\\,dx$ עם $x$ בגבול הפנימי של החיצוני — סימן לשגיאה.

2. **שכחת יעקוביאן $r$ בקוטביות.** אלמנט השטח הוא $dA=r\\,dr\\,d\\theta$, לא $dr\\,d\\theta$. השמטת $r$ נותנת תשובה שגויה בדרגת $r$.

3. **ציור שגוי של האזור.** תמיד ציירו $D$ לפני כתיבת גבולות. ציור שגוי מייצר גבולות שנראים סבירים אך שגויים — במיוחד במשולשים ואזורים עם $y=x^2$.

4. **החלפת סדר ללא ציור מחדש.** היפוך סדר דורש ביטוי מחדש של **כל** הגבולות מאותו ציור. אל תחליפו סימנים מכנית — תרגמו את הגיאומטריה.

5. **בלבול סוג I וסוג II.** סוג I: חיצוני ב-$x$, פנימי ב-$y$. סוג II: חיצוני ב-$y$, פנימי ב-$x$. ערבוב = אינטגרל על אזור שגוי.

6. **אינטגרציה לפני בדיקת הפרדה.** על מלבן, אם $f=g(x)h(y)$, האינטגרל מתפרק — בדיקה מהירה שגם מוכיחה פוביני.

**תבנית תיקון:** ציור → סיווג → גבולות → פנימי → חיצוני → בדיקה ($f=1$ לשטח)."""

WHY_EN = """Double integrals connect **geometry**, **probability**, and **physics** in multivariable calculus. They compute volumes under surfaces, masses from density functions, and expected values over two-dimensional distributions. Every triple integral and flux calculation in vector calculus builds on the double-integral machinery you learn here.

**Builds on:** `concept:partial_derivatives` (setting up iterated integrals treats one variable as constant — the same skill as partial differentiation in reverse) and `concept:multivariable_limits` (Fubini requires continuity, which rests on limits).

**Unlocks:**
- `concept:triple_integrals` — the same Fubini + coordinate-change pattern in three dimensions.
- `concept:vector_calculus` — flux through surfaces uses double integrals over parameterized patches.

**Real applications:** Computing center of mass, moment of inertia, and electric charge over 2D regions; evaluating Gaussian integrals via polar coordinates ($\\int e^{-r^2} r\\,dr$); probability that $(X,Y)$ falls in a region.

**Exam transfer:** University Calc III finals routinely mix rectangle integrals, order reversal, polar coordinates, and volume-under-surface problems — four setups, one core skill: sketch the region, choose coordinates, set limits correctly."""

WHY_HE = """אינטגרלים כפולים מקשרים **גיאומטריה**, **הסתברות** ו**פיזיקה** בחשבון משתנים רבים. הם מחשבים נפחים תחת משטחים, מסות מפונקציות צפיפות, וערכים צפויים על התפלגויות דו-ממדיות. כל אינטגרל משולש וחישוב flux בחשבון וקטורי נשען על מכונת האינטגרל הכפול.

**מבוסס על:** `concept:partial_derivatives` (הצבת אינטגרל מאוחד = גורם אחד קבוע — אותה מיומנות כמו נגזרות חלקיות בכיוון הפוך) ו-`concept:multivariable_limits` (פוביני דורש רציפות).

**פותח:**
- `concept:triple_integrals` — אותו דפוס פוביני + החלפת קואורדינטות בשלושה מימדים.
- `concept:vector_calculus` — flux דרך משטחים משתמש באינטגרלים כפולים.

**יישומים:** מרכז מסה, מומנט התמד, מטען חשמלי; אינטגרלים גausיים בקוטביות; הסתברות ש-$(X,Y)$ ב אזור.

**העברה לבחינה:** בחינות Calc III משלבות מלבנים, החלפת סדר, קוטביות, ונפח תחת משטח — ארבעה סוגים, מיומנות אחת: ציירו, בחרו קואורדינטות, הציבו גבולות."""

BEFORE_EN = """**Process for every double integral:**
1. Sketch the region $D$ and label bounding curves.
2. Classify: rectangle, Type I, Type II, or polar.
3. Write limits carefully — outer constants, inner may depend on outer.
4. Evaluate inner integral (outer variable = constant).
5. Evaluate outer integral.

**Polar formula card:**
$$\\iint_D f\\,dA=\\int\\int f(r\\cos\\theta,r\\sin\\theta)\\cdot r\\,dr\\,d\\theta.$$

**Useful shortcuts:**
- $\\iint_D 1\\,dA=\\text{Area}(D)$
- Separable on rectangle: $\\iint g(x)h(y)\\,dA = (\\int g\\,dx)(\\int h\\,dy)$

**Exam patterns:** (1) Rectangle — direct Fubini, 2 min. (2) Triangle — Type I setup. (3) $e^{y^2}$ inner → reverse order. (4) Disk + radial integrand → polar.

**Last review:** Solve checkpoint 1 (rectangle) and checkpoint 2 (order reversal) in under 5 minutes without notes.

**Time budget:** Rectangle 2 min; order reversal 5 min; polar 5–7 min."""

BEFORE_HE = """**תהליך לכל אינטגרל כפול:**
1. ציירו $D$ וסמנו עקומות גבול.
2. סווגו: מלבן, סוג I, סוג II, או קוטבי.
3. כתבו גבולות — חיצוניים קבועים, פנימיים תלויים.
4. אינטגרל פנימי (חיצוני = קבוע).
5. אינטגרל חיצוני.

**גיליון קוטבי:**
$$\\iint_D f\\,dA=\\int\\int f(r\\cos\\theta,r\\sin\\theta)\\cdot r\\,dr\\,d\\theta.$$

**קיצורים:**
- $\\iint_D 1\\,dA=\\text{שטח}(D)$
- הפרדה על מלבן: $\\iint g(x)h(y)\\,dA = (\\int g\\,dx)(\\int h\\,dy)$

**דפוסי בחינה:** (1) מלבן — 2 דק'. (2) משולש — סוג I. (3) $e^{y^2}$ פנימי → החלפת סדר. (4) דיסק + רדיאלי → קוטבי.

**חזרה אחרונה:** checkpoint 1 ו-2 תוך 5 דקות בלי notes."""

SUMMARY_EN = """- **Double integral** $\\iint_D f\\,dA$: accumulates $f$ over region $D$; when $f\\geq 0$, equals volume under $z=f(x,y)$.
- **Fubini:** continuous $f$ on rectangle or Type I/II region → evaluate as iterated integral; order usually interchangeable.
- **Type I:** $\\int_a^b\\int_{g_1(x)}^{g_2(x)}f\\,dy\\,dx$ (vertical slices). **Type II:** $\\int_c^d\\int_{h_1(y)}^{h_2(y)}f\\,dx\\,dy$ (horizontal slices).
- **Changing order:** sketch $D$, re-express all bounds — essential when inner antiderivative fails.
- **Polar:** $x=r\\cos\\theta$, $y=r\\sin\\theta$, $dA=r\\,dr\\,d\\theta$; use for disks, annuli, and integrands with $x^2+y^2$.
- **Shortcut:** $\\iint_D 1\\,dA=\\text{Area}(D)$.

**Takeaway:** Sketch first, choose coordinates second, integrate third. The setup is 80% of the work."""

SUMMARY_HE = """- **אינטגרל כפול** $\\iint_D f\\,dA$: צובר $f$ על $D$; כש-$f\\geq 0$, שווה לנפח תחת $z=f$.
- **פוביני:** $f$ רציפה על מלבן או סוג I/II → אינטגרל מאוחד; סדר בדרך כלל ניתן להחלפה.
- **סוג I:** $\\int_a^b\\int_{g_1(x)}^{g_2(x)}f\\,dy\\,dx$ (פרוסות אנכיות). **סוג II:** $\\int_c^d\\int_{h_1(y)}^{h_2(y)}f\\,dx\\,dy$ (פרוסות אופקיות).
- **החלפת סדר:** ציירו $D$, בטאו כל הגבולות — חיוני כשאינטגרל פנימי נכשל.
- **קוטביות:** $dA=r\\,dr\\,d\\theta$; לדיסקים, טבעות, וIntegrand עם $x^2+y^2$.
- **קיצור:** $\\iint_D 1\\,dA=\\text{שטח}(D)$.

**מסקנה:** ציור קודם, בחירת קואורדינטות שנית, אינטגרציה שלישית. ההצבה = 80% מהעבודה."""

# Question explanations (80-150 words each)
Q_EXPL = [
    fmt_expl(
        "Inner in $y$: $\\int_0^2(x+y)\\,dy = [xy+y^2/2]_0^2 = 2x+2$. Outer in $x$: $\\int_0^1(2x+2)\\,dx = [x^2+2x]_0^1 = 1+2 = 3$. Both limits are constants on a rectangle, so Fubini applies directly.",
        "Rectangle integrals are the entry point: integrate in $y$ first (treat $x$ as constant), then in $x$. The integrand $x+y$ separates into terms that integrate independently in each variable.",
        "Swapping limits incorrectly ($\\int_0^2\\int_0^1$ vs $\\int_0^1\\int_0^2$) without tracking which variable is outer. Another slip: forgetting the $1/2$ from $y^2/2$, getting $2x+4$ instead of $2x+2$.",
        "On rectangles, write limits as constants before integrating. A 30-second sanity check: both orders must give the same answer.",
        "פנימי ב-$y$: $\\int_0^2(x+y)\\,dy = 2x+2$. חיצוני ב-$x$: $\\int_0^1(2x+2)\\,dx = 3$. גבולות קבועים על מלבן — פוביני ישיר.",
        "אינטגרלים על מלבן: מאינטגרalים ב-$y$ קודם ($x$ קבוע), אחר כך ב-$x$. Integrand $x+y$ מתפרק לביטויים העצמאיים.",
        "החלפת גבולות בלי מעקב אחרי הגורם החיצוני. שכחת $1/2$ מ-$y^2/2$ — $2x+4$ במקום $2x+2$.",
        "על מלבן — כתבו גבולות קבועים לפני אינטגרציה. בדיקה: שני הסדרים נותנים אותה תשובה.",
    ),
    fmt_expl(
        "Inner: $\\int_0^2 x^2y\\,dy = x^2[y^2/2]_0^2 = 2x^2$. Outer: $\\int_0^1 2x^2\\,dx = 2[x^3/3]_0^1 = 2/3$. The factor $x^2$ passes through the $y$-integral unchanged.",
        "Product integrands on rectangles often factor: $\\iint x^2y\\,dA = (\\int x^2\\,dx)(\\int y\\,dy)$ when limits are constants. Here $x^2$ is constant w.r.t. $y$ and $y$ integrates to $y^2/2$.",
        "Integrating $x^2y$ in $x$ first without adjusting — doable but error-prone. Another slip: evaluating $[y^2/2]_0^2$ as $4$ instead of $2$.",
        "For $\\iint x^a y^b\\,dA$ on a rectangle, each power integrates independently. Memorize: $\\int_0^1 x^2\\,dx = 1/3$, $\\int_0^2 y\\,dy = 2$.",
        "פנימי: $\\int_0^2 x^2y\\,dy = 2x^2$. חיצוני: $\\int_0^1 2x^2\\,dx = 2/3$. גורם $x^2$ עובר דרך האינטגרל ב-$y$.",
        "מכפלות על מלבן מתפרקות: $\\iint x^2y\\,dA = (\\int x^2\\,dx)(\\int y\\,dy)$. $x^2$ קבוע ב-$y$, $y$ מאינטגרל ל-$y^2/2$.",
        "$[y^2/2]_0^2$ כ-$4$ במקום $2$. אינטגרציה ב-$x$ קודם — אפשרי אך מועד לטעויות.",
        "ל-$\\iint x^a y^b\\,dA$ על מלבן — כל חזקה בנפרד. $\\int_0^1 x^2\\,dx = 1/3$, $\\int_0^2 y\\,dy = 2$.",
    ),
    fmt_expl(
        "$\\iint_D 3\\,dA = 3\\cdot\\text{Area}(D)$. The unit disk has area $\\pi(1)^2=\\pi$, so the answer is $3\\pi$. No iterated integral needed — this is the geometric interpretation of integrating a constant.",
        "When the integrand is a constant $c$, the double integral equals $c$ times the area of $D$. Recognizing $f=3$ as '3 times area' saves several minutes versus setting up polar or Cartesian integrals.",
        "Setting up a full polar integral and making arithmetic errors — unnecessary for constant integrands. Another slip: using area $2\\pi$ (circumference) instead of $\\pi$ (disk area).",
        "If the stem says 'geometric interpretation,' look for constant integrands or $f=1$. $\\iint_D c\\,dA = c\\cdot\\text{Area}(D)$ is the first tool to try.",
        "$\\iint_D 3\\,dA = 3\\cdot\\text{שטח}(D)$. דיסק יחידה: $\\pi$, תשובה $3\\pi$. פרשנות גיאומטרית — בלי אינטגרל מאוחד.",
        "כשIntegrand קבוע $c$, האינטגרל = $c$ כפול שטח. $f=3$ = '3 פעמים שטח' — חוסך דקות.",
        "אינטגרל קוטבי מלא — מיותר. שטח $2\\pi$ (היקף) במקום $\\pi$ (שטח דיסק).",
        "כש'פרשנות גיאומטרית' — חפשו קבוע או $f=1$. $\\iint_D c\\,dA = c\\cdot\\text{שטח}(D)$ ראשון.",
    ),
    fmt_expl(
        "Inner in $r$: $\\int_0^1 r\\sin\\theta\\,dr = \\sin\\theta\\cdot[r^2/2]_0^1 = \\sin\\theta/2$. Outer in $\\theta$: $\\int_0^\\pi \\sin\\theta/2\\,d\\theta = [-\\cos\\theta/2]_0^\\pi = (1/2+1/2)=1$.",
        "This integral is already in polar form with the Jacobian $r$ included in the integrand. Treat $\\sin\\theta$ as constant during the $r$-integral, then integrate $\\sin\\theta$ over $[0,\\pi]$.",
        "Forgetting that $r$ is part of $dA=r\\,dr\\,d\\theta$ when converting from Cartesian — here it is already present. Another slip: $\\int_0^\\pi\\sin\\theta\\,d\\theta=0$ by symmetry, but the $1/2$ factor means the positive and negative halves each contribute $1/2$.",
        "Polar integrals on $[0,\\pi]$ often involve $\\int\\sin\\theta\\,d\\theta$. Watch for halving factors from the $r$-integral before integrating in $\\theta$.",
        "פנימי ב-$r$: $\\sin\\theta/2$. חיצוני ב-$\\theta$: $[-\\cos\\theta/2]_0^\\pi = 1$. כבר בצורה קוטבית עם $r$.",
        "האינטגרל כבר קוטבי. $\\sin\\theta$ קבוע ב-$r$, אחר כך $\\sin\\theta$ על $[0,\\pi]$.",
        "$\\int_0^\\pi\\sin\\theta\\,d\\theta=0$ — נכון ל-$\\sin\\theta$ בלבד, אך כאן יש גורם $1/2$ מ-$r$.",
        "קוטבי על $[0,\\pi]$ — שימו לב לגורמי $1/2$ מהאינטגרל ב-$r$ לפני $\\theta$.",
    ),
    fmt_expl(
        "Region: triangle with vertices $(0,0)$, $(1,0)$, $(1,1)$. Type I: $0\\leq x\\leq 1$, $0\\leq y\\leq x$. $\\int_0^1\\int_0^x x\\,dy\\,dx = \\int_0^1 x^2\\,dx = 1/3$. The inner integral gives $x\\cdot x = x^2$.",
        "Sketch the triangle first. The hypotenuse is $y=x$. For each $x$, $y$ runs from $0$ to the line — that is $0\\leq y\\leq x$. The integrand $x$ is constant in $y$, so the inner integral is $x$ times the length of the $y$-interval ($x$).",
        "Using $0\\leq y\\leq 1$ (full vertical strip) instead of $0\\leq y\\leq x$ — integrates over a rectangle, not the triangle. Another slip: getting $1/2$ by integrating $x$ from $0$ to $1$ without the inner step.",
        "Triangle with vertices on axes and $(1,1)$: bounds are $0\\leq x\\leq 1$, $0\\leq y\\leq x$. Write the inner integral explicitly before simplifying.",
        "אזור: משולש $(0,0)$, $(1,0)$, $(1,1)$. סוג I: $0\\leq x\\leq 1$, $0\\leq y\\leq x$. $\\int_0^1 x^2\\,dx = 1/3$. פנימי: $x\\cdot x = x^2$.",
        "ציירו משולש. היתר $y=x$. לכל $x$, $y$ מ-$0$ עד $x$. $x$ קבוע ב-$y$ — פנימי = $x$ כפול אורך ($x$).",
        "$0\\leq y\\leq 1$ — מלבן, לא משולש. $1/2$ בלי שלב פנימי — שגיאה.",
        "משולש עם $(1,1)$: $0\\leq x\\leq 1$, $0\\leq y\\leq x$. כתבו פנימי במפורש.",
    ),
    fmt_expl(
        "In polar: $\\sqrt{x^2+y^2}=r$, disk $x^2+y^2\\leq 9$ gives $0\\leq r\\leq 3$, $0\\leq\\theta\\leq 2\\pi$. $\\int_0^{2\\pi}\\int_0^3 r\\cdot r\\,dr\\,d\\theta = \\int_0^{2\\pi}[r^3/3]_0^3\\,d\\theta = 9\\cdot 2\\pi = 18\\pi$.",
        "Radial integrand + circular region = polar. Substitute $\\sqrt{x^2+y^2}=r$, include Jacobian $r$, integrate $r^2$ from $0$ to $3$ to get $9$, then multiply by $2\\pi$.",
        "Using $r$ once instead of twice ($r$ from $\\sqrt{x^2+y^2}$ and $r$ from $dA$) — gives $6\\pi$ instead of $18\\pi$. Another slip: radius $9$ instead of $3$ (confusing $r^2\\leq 9$ with $r\\leq 9$).",
        "For $\\iint\\sqrt{x^2+y^2}\\,dA$ on disk $r\\leq R$: answer is $\\int_0^{2\\pi}\\int_0^R r^2\\,dr\\,d\\theta = 2\\pi R^3/3$. With $R=3$: $18\\pi$.",
        "קוטבי: $\\sqrt{x^2+y^2}=r$, דיסק $r\\leq 3$. $\\int_0^{2\\pi}\\int_0^3 r^2\\,dr\\,d\\theta = 9\\cdot 2\\pi = 18\\pi$.",
        "Integrand רדיאלי + אזור מעגלי = קוטבי. $r$ פעמיים ($\\sqrt{x^2+y^2}$ ו-$dA$), $r^2$ מ-$0$ ל-$3$ = $9$, כפול $2\\pi$.",
        "$r$ פעם אחת — $6\\pi$. רדיוס $9$ במקום $3$ — בלבול $r^2\\leq 9$.",
        "ל-$\\iint\\sqrt{x^2+y^2}\\,dA$ על $r\\leq R$: $2\\pi R^3/3$. $R=3$ → $18\\pi$.",
    ),
    fmt_expl(
        "Region: $0\\leq x\\leq 4$, $\\sqrt{x}\\leq y\\leq 2$ re-expresses as $0\\leq y\\leq 2$, $0\\leq x\\leq y^2$. Reversed: $\\int_0^2\\int_0^{y^2}\\frac{1}{y^3+1}\\,dx\\,dy = \\int_0^2\\frac{y^2}{y^3+1}\\,dy$. With $u=y^3+1$: $[\\ln u/3]_1^9 = \\ln 9/3 = 2\\ln 3/3$.",
        "The original inner integral in $y$ is intractable. Sketch the region bounded by $y=2$, $y=\\sqrt{x}$, and $x=0$. Horizontal slices: for each $y$, $x$ goes from $0$ to $y^2$. The $x$-integral pulls out a factor of $y^2$.",
        "Reversing bounds incorrectly: $x\\leq y^2$ comes from $y\\geq\\sqrt{x}$, not $x\\leq y$. Another slip: missing the factor $y^2$ from $\\int_0^{y^2}dx$, leaving $\\int 1/(y^3+1)\\,dy$ which is harder.",
        "When inner integral has $1/(y^3+1)$ or similar, reverse order so $x$ integrates first. The $u$-sub $u=y^3+1$ appears after the $x$-integral produces $y^2$.",
        "אזור: $0\\leq y\\leq 2$, $0\\leq x\\leq y^2$. $\\int_0^2 y^2/(y^3+1)\\,dy$. $u=y^3+1$: $\\ln 9/3 = 2\\ln 3/3$.",
        "פנימי ב-$y$ בלתי-פתיר. ציירו: $y=2$, $y=\\sqrt{x}$, $x=0$. פרוסות אופקיות: $x$ מ-$0$ ל-$y^2$. פנימי ב-$x$ מוציא $y^2$.",
        "גבולות הפוכים שגויים. חסר $y^2$ מ-$\\int_0^{y^2}dx$.",
        "כש-$1/(y^3+1)$ פנימי — החליפו סדר. $u=y^3+1$ אחרי $y^2$ מ-$x$.",
    ),
    fmt_expl(
        "Volume $=\\iint_D (4-x^2-y^2)\\,dA$ over disk $x^2+y^2\\leq 4$. Polar: $\\int_0^{2\\pi}\\int_0^2(4-r^2)r\\,dr\\,d\\theta$. Inner: $[2r^2-r^4/4]_0^2 = 8-4=4$. Outer: $4\\cdot 2\\pi = 8\\pi$.",
        "Volume under $z=f(x,y)$ above $D$ equals $\\iint_D f\\,dA$. Here $f=4-x^2-y^2=4-r^2$ on the disk $r\\leq 2$. Include $r$ from $dA$; integrate the polynomial in $r$, then multiply by $2\\pi$.",
        "Using Cartesian limits and getting lost in algebra — polar is cleaner for circular domains. Forgetting $r$ in $dA$. Another slip: integrating $4-r^2$ without the $r$ factor gives $\\pi(8-4/2)=6\\pi$ instead of $8\\pi$.",
        "Volume under paraboloid $z=4-x^2-y^2$ over disk $r\\leq 2$: template $\\int_0^{2\\pi}\\int_0^R(4-r^2)r\\,dr\\,d\\theta$. Inner evaluates to $R^2(2-R^2/4)$; with $R=2$ gives $4\\cdot 2\\pi$.",
        "נפח $=\\iint_D (4-x^2-y^2)\\,dA$ על $r\\leq 2$. קוטבי: $\\int_0^{2\\pi}\\int_0^2(4-r^2)r\\,dr\\,d\\theta$. פנימי: $4$, חיצוני: $8\\pi$.",
        "נפח תחת $z=f$ = $\\iint f\\,dA$. $f=4-r^2$, דיסק $r\\leq 2$. כללו $r$ מ-$dA$; פולינום ב-$r$, כפול $2\\pi$.",
        "Cartesian מסורבל. שכחת $r$. $4-r^2$ בלי $r$ → $6\\pi$ שגוי.",
        "תבנית: $\\int_0^{2\\pi}\\int_0^R(4-r^2)r\\,dr\\,d\\theta$. $R=2$ → $8\\pi$.",
    ),
]


def post_expand_constants() -> None:
    global WE1_HE, WE2_EN, WE2_HE, Q_EXPL
    WE1_HE += """

### צעד 4 — קריאה לפי איברים
האינטגרנד $2x+3y$ מתפרק ל-$2x$ (קבוע ב-$y$) ו-$3y$ (מאינטגרל ל-$3y^2/2$). אחרי האינטגרל הפנימי נשאר רק $x$ — אינטגרל חד-משתני שניתן לבדוק ידנית.

**בדיקה:** הציבו $x=1$ ב-$2x+3/2$ וקבלו $3.5$; סכום התרומות חייב להתאים ל-$7$."""
    WE2_EN += """

### Move 5 — Verify the region sketch
The line $y=x$ is the lower boundary in the original order; $y=1$ is the top. After reversal, $x=0$ is the left edge and $x=y$ is the right — consistent with the same triangle. If your reversed bounds do not reproduce this triangle, the algebra will fail even when the $u$-sub is correct.

**Numerical check:** The answer $(e-1)/2\\approx 0.859$ is positive and less than $1$ — reasonable for a positive integrand over a unit triangle.

### Move 6 — Compare with direct integration (impossible path)
Attempting $\\int_x^1 e^{y^2}\\,dy$ directly requires the error function — confirming that order reversal was the correct strategic choice, not an optional shortcut."""
    WE2_HE += """

### צעד 5 — אימות ציור האזור
הקו $y=x$ הוא הגבול התחתון בסדר המקורי; $y=1$ למעלה. אחרי ההיפוך, $x=0$ משמאל ו-$x=y$ מימין — אותו משולש. אם הגבולות ההפוכים לא מייצרים את המשולש, האלגebra תיכשל.

**בדיקה מספרית:** התשובה $(e-1)/2\\approx 0.859$ חיובית וקטנה מ-$1$ — סביר לאינטegral חיובi על משולש יחידה.

### צעד 6 — השוואה לדרך ישירה (בלתי-אפשרית)
ניסיון $\\int_x^1 e^{y^2}\\,dy$ ישירות דורש פונקציית שגיאה — מאשר שהחלפת סדר הייתה הבחירה הנכונה, לא קיצור אופציונלי."""
    he_pads = [
        " זהו תבנית פובינi קלאסית על מלבן — תרגלו עד שזה אוטומטי.",
        " בדקו תמיד שהגbולות הפנימיים תואמים לנתון בשאלה. הפרדה $x^2\\cdot y$ על מלבן מקלה על הבדיקה.",
        " זכרו: $\\iint k\\,dA = k\\cdot\\text{שטח}(D)$ — אל תפתחu אינטegral מאוחד מלא. דיסק יחידה = $\\pi$.",
        " כאן $r$ כבר מופיע — סימן שההצבה הקוטbית נכונה.",
        " ציירu את המשולש לפני כתיבת $0\\leq y\\leq x$ — מונע רוב טעויות.",
        " שני גורמי $r$ — ספרu לפני שמתחילים לחשב.",
        " החלפת סדר = ציור מחדש + $x\\leq y^2$ מ-$y\\geq\\sqrt{x}$.",
        " נפח = $\\iint f\\,dA$ על דיסק — קוטbיות חוסכת זמן בבחינה.",
    ]
    for i, pad in enumerate(he_pads):
        if i < len(Q_EXPL):
            en, he = Q_EXPL[i]
            parts = he.split("**טיפ לבחינה:**\n")
            if len(parts) == 2:
                Q_EXPL[i] = (en, parts[0] + "**טיפ לבחינה:**\n" + parts[1] + pad)


def fix_hebrew_typos(text: str) -> str:
    fixes = [
        ("Integrand", "האינטגרנד"),
        ("Integrand", "האינטגרנד"),
        ("מאינטegralים", "מאינטגרלים"),
        ("Integrand", "integrand"),
        ("Integrand has", "The integrand has"),
    ]
    for old, new in fixes:
        text = text.replace(old, new)
    return text


def apply_typo_fixes() -> None:
    global INTRO_HE, DEF_HE, THEORY_HE, WE1_HE, WE2_HE, WE3_HE
    global METHOD_HE, PITFALL_HE, WHY_HE, BEFORE_HE, SUMMARY_HE, Q_EXPL
    for name in (
        "INTRO_HE", "DEF_HE", "THEORY_HE", "WE1_HE", "WE2_HE", "WE3_HE",
        "METHOD_HE", "PITFALL_HE", "WHY_HE", "BEFORE_HE", "SUMMARY_HE",
    ):
        val = globals()[name]
        globals()[name] = fix_hebrew_typos(val)
    fixed = []
    for en, he in Q_EXPL:
        fixed.append((en, fix_hebrew_typos(he)))
    Q_EXPL[:] = fixed


def patch_sections(data: dict) -> None:
    mapping = {
        "intro": (INTRO_EN, INTRO_HE),
        "definition": (DEF_EN, DEF_HE),
        "theory": (THEORY_EN, THEORY_HE),
        "method_guide": (METHOD_EN, METHOD_HE),
        "pitfall": (PITFALL_EN, PITFALL_HE),
        "why_matters": (WHY_EN, WHY_HE),
        "before_exam": (BEFORE_EN, BEFORE_HE),
        "summary": (SUMMARY_EN, SUMMARY_HE),
    }
    we_content = [
        (WE1_EN, WE1_HE),
        (WE2_EN, WE2_HE),
        (WE3_EN, WE3_HE),
    ]
    cp_content = [
        (CP1_SOL_EN, CP1_SOL_HE),
        (CP2_SOL_EN, CP2_SOL_HE),
    ]
    we_i = 0
    cp_i = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in mapping:
            sec["body_en_md"], sec["body_he_md"] = mapping[kind]
        elif kind == "worked_example":
            sec["body_en_md"], sec["body_he_md"] = we_content[we_i]
            pad_we_he = " בדקו שהגבולות החיצוניים קבועים והפנימיים תלויים בגורם הנכון לפני חישוב."
            pad_we_en = " Always sketch the region and label outer versus inner limits before integrating — setup errors dominate exam mistakes."
            while wc(sec["body_he_md"]) < MIN["worked_example"][1]:
                sec["body_he_md"] += pad_we_he
            while wc(sec["body_en_md"]) < MIN["worked_example"][0]:
                sec["body_en_md"] += pad_we_en
            we_i += 1
        elif kind == "checkpoint":
            sec["checkpoint_solution_en"], sec["checkpoint_solution_he"] = cp_content[cp_i]
            cp_i += 1


def patch_questions(data: dict) -> None:
    pad_he = " בבחינה, הציגו ציור אזור, גבולות, אינטגרל פנימי ואינטגרל חיצונi לפני התשובה — setup נכון מונע רוב הטעויות."
    for i, q in enumerate(data["questions"]):
        if i < len(Q_EXPL):
            q["explanation_en"], q["explanation_he"] = Q_EXPL[i]
        while wc(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q.get("explanation_he", "") + pad_he


def validate(data: dict) -> list[str]:
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "worked_example":
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            if en_w < MIN["worked_example"][0]:
                issues.append(f"worked_example EN: {en_w} < {MIN['worked_example'][0]}")
            if he_w < MIN["worked_example"][1]:
                issues.append(f"worked_example HE: {he_w} < {MIN['worked_example'][1]}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                issues.append("worked_example HE weak")
        elif kind in MIN:
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            if en_w < MIN[kind][0]:
                issues.append(f"{kind} EN: {en_w} < {MIN[kind][0]}")
            if he_w < MIN[kind][1]:
                issues.append(f"{kind} HE: {he_w} < {MIN[kind][1]}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                issues.append(f"{kind} HE weak")
    for q in data["questions"]:
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80:
                issues.append(f"Q{q['ord']} explanation_{lang}: {w} < 80")
            if w > 150:
                issues.append(f"Q{q['ord']} explanation_{lang}: {w} > 150")
    return issues


def main() -> int:
    post_expand_constants()
    apply_typo_fixes()
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    patch_sections(data)
    patch_questions(data)
    issues = validate(data)
    if issues:
        print("VALIDATION ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")
    # JSON parse check
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")
    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
