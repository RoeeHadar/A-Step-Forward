#!/usr/bin/env python3
"""Expand definite_integrals.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/definite_integrals.json"

INTRO = {
    "body_en_md": """How do we measure the area under a curve $y = f(x)$ over $[a, b]$ when the curve is not a straight line? We approximate with **rectangles** of width $\\Delta x$ and height $f(x_i^*)$, sum the areas, and take the limit:

$$\\int_a^b f(x) \\, dx = \\lim_{n \\to \\infty} \\sum_{i=1}^n f(x_i^*) \\Delta x.$$

This is the **Riemann definition**. The result is always a **number** — the signed area (positive above the $x$-axis, negative below). Unlike the indefinite integral $\\int f \\, dx = F(x) + C$, which is a family of functions, the definite integral $\\int_a^b f \\, dx$ is a single value with **no** $+C$.

The **Fundamental Theorem of Calculus (FTC)** turns this geometric limit into a practical recipe: find any antiderivative $F$ with $F'=f$, then compute $F(b)-F(a)$. On Bagrut questionnaires 581 and 807, FTC Part 2 is the main tool for evaluating integrals; substitution with changed limits appears on 5-unit papers; FTC Part 1 shows up when differentiating integrals whose upper limit is a function of $x$.

**Three ideas to keep separate:** signed net area ($\\int f\\,dx$), geometric (unsigned) area ($\\int |f|\\,dx$), and the swap-limits rule ($\\int_a^b f = -\\int_b^a f$). Confusing these three causes most lost points on exam day.""",
    "body_he_md": """איך מודדים שטח מתחת לעקומה $y=f(x)$ על $[a,b]$ כשהעקומה אינה קו ישר? מקרבים ב**מלבנים** ברוחב $\\Delta x$ וגובה $f(x_i^*)$, מסכמים את השטחים ולוקחים גבול:

$$\\int_a^b f(x)\\,dx=\\lim_{n\\to\\infty}\\sum_{i=1}^n f(x_i^*)\\Delta x.$$

זוהי **הגדרת רימן**. התוצאה תמיד **מספר** — שטח עם סימן (חיובי מעל ציר $x$, שלילי מתחת). **בניגוד** לאינטגרל הלא מסוים $\\int f\\,dx=F(x)+C$, שהוא משפחת פונקציות, האינטגרל המסוים $\\int_a^b f\\,dx$ הוא ערך בודד **בלי** $+C$.

**משפט היסוד של החשבון (FTC)** הופך את הגבול הגיאומטרי למתכון מעשי: מוצאים קדומה $F$ עם $F'=f$, ואז מחשבים $F(b)-F(a)$. בבגרות (שאלוני 581/807), FTC חלק 2 הוא הכלי המרכזי לחישוב אינטגרלים; הצבה עם שינוי גבולות מופיעה בשאלוני 5 יחידות; FTC חלק 1 מופיע כשגוזרים אינטגרל שהגבול העליון שלו הוא פונקציה של $x$.

**שלושה רעיונות להפריד:** שטח נטו עם סימן ($\\int f\\,dx$), שטח גיאומטרי ($\\int|f|\\,dx$), וכלל החלפת גבולות ($\\int_a^b f=-\\int_b^a f$). בלבול ביניהם גורם לרוב איבוד הנקודות בבחינה.""",
}

DEFINITION = {
    "body_en_md": """**Definite integral (Riemann sum):**
$$\\displaystyle\\int_a^b f(x)\\,dx = \\lim_{n\\to\\infty}\\sum_{i=1}^n f(x_i^*)\\Delta x$$
The output is a **number** — signed net area under $y=f(x)$ on $[a,b]$.

**Fundamental Theorem of Calculus, Part 2 (evaluation):**
$$\\boxed{\\int_a^b f(x)\\,dx = F(b) - F(a) = \\Big[F(x)\\Big]_a^b}$$
where $F$ is **any** antiderivative of $f$ ($F'=f$), provided $f$ is continuous on $[a,b]$. The constant $+C$ never appears because $(F(b)+C)-(F(a)+C)=F(b)-F(a)$.

**FTC, Part 1 (differentiation of an integral):**
If $g(x)=\\int_a^x f(t)\\,dt$ and $f$ is continuous, then $g'(x)=f(x)$. With a composite upper limit $u=g(x)$:
$$\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt = f(g(x))\\cdot g'(x).$$

**Key properties (use these before computing):**
- $\\int_a^a f = 0$.
- $\\int_a^b f = -\\int_b^a f$ (swap limits = flip sign).
- $\\int_a^b f + \\int_b^c f = \\int_a^c f$ (additivity on intervals).
- Linearity: $\\int(\\alpha f + \\beta g) = \\alpha\\int f + \\beta\\int g$.

**Signed vs. geometric area:** $\\int_0^{2\\pi}\\sin x\\,dx=0$ (cancellation), but the geometric area under one arch is $2$. For total area, integrate $|f|$ or split at zeros.""",
    "body_he_md": """**אינטגרל מסוים (סכום רימן):**
$$\\displaystyle\\int_a^b f(x)\\,dx=\\lim_{n\\to\\infty}\\sum_{i=1}^n f(x_i^*)\\Delta x$$
התוצאה היא **מספר** — שטח נטו עם סימן מתחת ל-$y=f(x)$ על $[a,b]$.

**משפט היסוד של החשבון, חלק 2 (חישוב):**
$$\\boxed{\\int_a^b f(x)\\,dx=F(b)-F(a)=\\Big[F(x)\\Big]_a^b}$$
כאשר $F$ היא קדומה **כלשהי** של $f$ ($F'=f$), בתנאי ש-$f$ רציפה על $[a,b]$. הקבוע $+C$ לא מופיע כי $(F(b)+C)-(F(a)+C)=F(b)-F(a)$.

**FTC, חלק 1 (גזירת אינטגרל):**
אם $g(x)=\\int_a^x f(t)\\,dt$ ו-$f$ רציפה, אז $g'(x)=f(x)$. עם גבול עליון מורכב $u=g(x)$:
$$\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt=f(g(x))\\cdot g'(x).$$

**תכונות מפתח (השתמשו לפני חישוב):**
- $\\int_a^a f=0$.
- $\\int_a^b f=-\\int_b^a f$ (החלפת גבולות = היפוך סימן).
- $\\int_a^b f+\\int_b^c f=\\int_a^c f$ (תוספתיות על קטעים).
- ליניאריות: $\\int(\\alpha f+\\beta g)=\\alpha\\int f+\\beta\\int g$.

**שטח עם סימן מול גיאומטרי:** $\\int_0^{2\\pi}\\sin x\\,dx=0$ (ביטול), אך השטח הגיאומטרי תחת קשת אחת הוא $2$. לשטח כולל — אינטגרל של $|f|$ או פיצול באפסים.""",
}

THEORY = {
    "body_en_md": """### Using FTC Part 2 (the evaluation recipe)

1. Find an antiderivative $F$ of $f$ (from your integral table or prior rules).
2. Evaluate $F(b)-F(a)$ using bracket notation $[F(x)]_a^b$.
3. Do **not** add $+C$ — it cancels in the difference.

Example: $\\int_0^2 3x^2\\,dx = [x^3]_0^2 = 8 - 0 = 8$.

### Substitution in definite integrals (two valid approaches)

When $u=g(x)$, you may either:
- **Approach 1:** Change limits with $u$: lower $=g(a)$, upper $=g(b)$, integrate in $u$, no back-substitution.
- **Approach 2:** Integrate in $u$, back-substitute to $x$, then evaluate at original limits.

Both give the same answer — pick whichever avoids algebra errors. **Never mix:** do not evaluate at original $x$-limits after changing to $u$-limits.

### FTC Part 1 and the chain rule

$$\\frac{d}{dx}\\int_a^x f(t)\\,dt = f(x).$$
For a composite upper limit: $\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt = f(g(x))\\cdot g'(x)$.

When **both** limits vary: $\\frac{d}{dx}\\int_{g(x)}^{h(x)} f(t)\\,dt = f(h(x))h'(x)-f(g(x))g'(x)$ (Leibniz rule).

### Absolute-value integrands

Find where the expression inside $| \\cdot |$ equals zero, split the interval, replace the bars with the correct signed expression on each piece, then sum the definite integrals. FTC requires smoothness; $|x-1|$ is not differentiable at $x=1$.""",
    "body_he_md": """### שימוש ב-FTC חלק 2 (מתכון החישוב)

1. מוצאים קדומה $F$ של $f$ (מטבלת האינטגרלים או כללים קודמים).
2. מחשבים $F(b)-F(a)$ בסימון $[F(x)]_a^b$.
3. **אין** $+C$ — הוא מתבטל בהפרש.

דוגמה: $\\int_0^2 3x^2\\,dx=[x^3]_0^2=8-0=8$.

### הצבה באינטגרלים מסוימים (שתי גישות תקפות)

כש-$u=g(x)$, אפשר:
- **גישה 1:** שינוי גבולות עם $u$: תחתון $=g(a)$, עליון $=g(b)$, אינטגרציה ב-$u$, ללא חזרה ל-$x$.
- **גישה 2:** אינטגרציה ב-$u$, חזרה ל-$x$, ואז הערכה בגבולות המקוריים.

שתיהן נותנות אותה תשובה — בחרו את הנוחה. **אל תערבבו:** אל תציבו גבולות $x$ מקוריים אחרי מעבר ל-$u$.

### FTC חלק 1 וכלל השרשרת

$$\\frac{d}{dx}\\int_a^x f(t)\\,dt=f(x).$$
לגבול עליון מורכב: $\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt=f(g(x))\\cdot g'(x)$.

כש**שני** הגבולות משתנים: $\\frac{d}{dx}\\int_{g(x)}^{h(x)} f(t)\\,dt=f(h(x))h'(x)-f(g(x))g'(x)$ (כלל לייבניץ).

### אינטגרנד עם ערך מוחלט

מצאו היכן הביטוי בתוך $| \\cdot |$ מתאפס, פצלו את הקטע, החליפו את הערך המוחלט בביטוי עם הסימן הנכון בכל חלק, וסכמו. FTC דורש חלקות; $|x-1|$ לא גזירה ב-$x=1$.""",
}

WE1 = {
    "body_en_md": """**Compute** $\\displaystyle\\int_{-1}^{2}(3x^2 - 2x)\\,dx$.

This is a standard FTC Part 2 problem: antiderivative, bracket notation, upper minus lower. No $+C$.

### Move 1: Find antiderivative.
$$F(x) = x^3 - x^2.$$
Check: $\\frac{d}{dx}(x^3-x^2)=3x^2-2x$ ✓

### Move 2: Evaluate at upper limit $x=2$.
$$F(2) = 8 - 4 = 4.$$

### Move 3: Evaluate at lower limit $x=-1$.
$$F(-1) = (-1)^3 - (-1)^2 = -1 - 1 = -2.$$

### Move 4: Subtract (upper minus lower).
$$\\int_{-1}^{2}(3x^2-2x)\\,dx = F(2) - F(-1) = 4 - (-2) = 6.$$

**Answer:** $\\boxed{6}$ ✓

**Check:** $+C$ would not affect the answer: $(F(b)+C)-(F(a)+C)=F(b)-F(a)$. Watch the sign of $F(-1)$ — $(-1)^2=1$, not $-1$.

**Geometric check:** On $[-1,2]$, the integrand $3x^2-2x$ is a parabola opening upward with roots at $0$ and $2/3$; the net signed area can be positive even when part of the graph dips below the axis near $x=0$.

**Exam note:** Write $[x^3-x^2]_{-1}^{2}$ before substituting numbers; graders award partial credit for correct setup. Bagrut MCQ options often differ only by sign — always compute $F(b)-F(a)$, never $F(a)-F(b)$.""",
    "body_he_md": """**חשבו** $\\displaystyle\\int_{-1}^{2}(3x^2-2x)\\,dx$.

זו בעיית FTC חלק 2 סטנדרטית: קדומה, סימון סוגריים, עליון פחות תחתון. בלי $+C$.

### צעד 1: מציאת קדומה.
$$F(x)=x^3-x^2.$$
בדיקה: $\\frac{d}{dx}(x^3-x^2)=3x^2-2x$ ✓

### צעד 2: הערכה בגבול עליון $x=2$.
$$F(2)=8-4=4.$$

### צעד 3: הערכה בגבול תחתון $x=-1$.
$$F(-1)=(-1)^3-(-1)^2=-1-1=-2.$$

### צעד 4: חיסור (עליון פחות תחתון).
$$\\int_{-1}^{2}(3x^2-2x)\\,dx=F(2)-F(-1)=4-(-2)=6.$$

**תשובה:** $\\boxed{6}$ ✓

**בדיקה:** $+C$ לא משפיע: $(F(b)+C)-(F(a)+C)=F(b)-F(a)$. שימו לב לסימן של $F(-1)$ — $(-1)^2=1$, לא $-1$.

**בדיקה גיאומטרית:** ב-$[-1,2]$, האינטגרנד $3x^2-2x$ הוא פרבולה פונה למעלה עם שורשים ב-$0$ וב-$2/3$; השטח הנטו עם סימן יכול להיות חיובי גם כשחלק מהגרף יורד מתחת לציר ליד $x=0$.

**הערה לבחינה:** כתבו $[x^3-x^2]_{-1}^{2}$ לפני הצבת מספרים — בודקים נותנים ניקוד חלקי על הגדרה נכונה. אפשרויות בגרות לעיתים קרובות נבדלות רק בסימן — תמיד $F(b)-F(a)$, לעולם לא $F(a)-F(b)$.""",
}

WE2 = {
    "body_en_md": """**Compute** $I = \\displaystyle\\int_0^1 2x\\sqrt{x^2+1}\\,dx$ using substitution.

The factor $2x\\,dx$ matches the derivative of $x^2+1$ — a classic $u$-substitution with limit change.

### Move 1: Choose substitution.
Let $u = x^2 + 1$, so $du = 2x\\,dx$. The entire integrand becomes $\\sqrt{u}\\,du$.

### Move 2: Change limits with $u$.
- $x = 0 \\Rightarrow u = 0^2 + 1 = 1$.
- $x = 1 \\Rightarrow u = 1^2 + 1 = 2$.

### Move 3: Rewrite integral in $u$.
$$I = \\int_1^2 \\sqrt{u}\\,du = \\int_1^2 u^{1/2}\\,du.$$

### Move 4: Integrate with FTC Part 2.
$$I = \\left[\\frac{2}{3}u^{3/2}\\right]_1^2 = \\frac{2}{3}(2^{3/2} - 1^{3/2}) = \\frac{2}{3}(2\\sqrt{2}-1).$$

**Answer:** $\\boxed{\\dfrac{2}{3}(2\\sqrt{2}-1) \\approx 1.219}$ ✓

**Why change limits?** You avoid back-substituting $u=x^2+1$ before evaluation — one fewer place for sign errors.

**Numerical check:** $2\\sqrt{2}\\approx 2.828$, so $I\\approx \\frac{2}{3}(1.828)\\approx 1.22$ — a positive value, as expected since the integrand is non-negative on $[0,1]$.

**Exam tip:** Always write both old and new limits in the margin when using Approach 1. On 5-unit Bagrut papers, substitution with $\\sqrt{u}$ after $u=x^2+1$ is a recurring pattern — recognize $2x\\,dx$ as $du$ immediately.""",
    "body_he_md": """**חשבו** $I=\\displaystyle\\int_0^1 2x\\sqrt{x^2+1}\\,dx$ באמצעות הצבה.

הגורם $2x\\,dx$ תואם לנגזרת של $x^2+1$ — הצבה קלאסית עם שינוי גבולות.

### צעד 1: בחירת הצבה.
נגדיר $u=x^2+1$, ולכן $du=2x\\,dx$. כל האינטגרנד הופך ל-$\\sqrt{u}\\,du$.

### צעד 2: שינוי גבולות עם $u$.
- $x=0 \\Rightarrow u=1$.
- $x=1 \\Rightarrow u=2$.

### צעד 3: כתיבה מחדש ב-$u$.
$$I=\\int_1^2\\sqrt{u}\\,du=\\int_1^2 u^{1/2}\\,du.$$

### צעד 4: אינטגרציה עם FTC חלק 2.
$$I=\\left[\\frac{2}{3}u^{3/2}\\right]_1^2=\\frac{2}{3}(2\\sqrt{2}-1).$$

**תשובה:** $\\boxed{\\dfrac{2}{3}(2\\sqrt{2}-1)\\approx 1.219}$ ✓

**למה לשנות גבולות?** נמנעים מחזרה ל-$x$ לפני הערכה — פחות מקום לשגיאות סימן.

**בדיקה מספרית:** $2\\sqrt{2}\\approx 2.828$, ולכן $I\\approx 1.22$ — ערך חיובי, כצפוי כי האינטגרנד אי-שלילי ב-$[0,1]$.

**טיפ לבחינה:** כתבו תמיד גבולות ישנים וחדשים בשוליים כשמשתמשים בגישה 1. בבגרות 5 יחידות, הצבה עם $\\sqrt{u}$ אחרי $u=x^2+1$ חוזרת — זהו $2x\\,dx$ כ-$du$ מיד.""",
}

WE3 = {
    "body_en_md": """**Part (a):** If $g(x) = \\int_0^{x^2} \\sin(t^2)\\,dt$, find $g'(x)$.

### Move 1: Recognize FTC Part 1 with composite upper limit.
The upper limit is $u=x^2$, not plain $x$ — chain rule is mandatory.

### Move 2: Apply the chain rule.
$$g'(x) = \\frac{d}{dx}\\int_0^{x^2} \\sin(t^2)\\,dt = \\sin((x^2)^2) \\cdot 2x = 2x\\sin(x^4).$$

**Part (b):** Compute $\\displaystyle\\int_0^2 |x - 1|\\,dx$.

### Move 1: Remove absolute value by splitting at $x=1$.
$$\\int_0^2 |x-1|\\,dx = \\int_0^1 (1-x)\\,dx + \\int_1^2 (x-1)\\,dx.$$

### Move 2: Evaluate each piece with FTC.
$$\\int_0^1 (1-x)\\,dx = \\left[x - \\frac{x^2}{2}\\right]_0^1 = 1 - \\frac{1}{2} = \\frac{1}{2}.$$
$$\\int_1^2 (x-1)\\,dx = \\left[\\frac{x^2}{2} - x\\right]_1^2 = (2-2) - \\left(\\tfrac{1}{2}-1\\right) = \\frac{1}{2}.$$

### Move 3: Add.
$$\\int_0^2 |x-1|\\,dx = \\frac{1}{2} + \\frac{1}{2} = 1.$$

**Geometric interpretation (b):** The graph of $y=|x-1|$ is a V-shape with vertex at $(1,0)$; the two triangular pieces each have area $1/2$, confirming total area $1$.

**Exam note:** Do not try to integrate $\\sin(t^2)$ in part (a) — it has no elementary antiderivative (Fresnel integrals). FTC Part 1 is the intended one-line shortcut. Part (b) tests whether you split absolute values before applying FTC.""",
    "body_he_md": """**חלק (א):** אם $g(x)=\\int_0^{x^2}\\sin(t^2)\\,dt$, מצאו $g'(x)$.

### צעד 1: זיהוי FTC חלק 1 עם גבול עליון מורכב.
הגבול העליון הוא $u=x^2$, לא $x$ פשוט — כלל שרשרת חובה.

### צעד 2: יישום כלל השרשרת.
$$g'(x)=\\frac{d}{dx}\\int_0^{x^2}\\sin(t^2)\\,dt=\\sin((x^2)^2)\\cdot 2x=2x\\sin(x^4).$$

**חלק (ב):** חשבו $\\displaystyle\\int_0^2|x-1|\\,dx$.

### צעד 1: הסרת ערך מוחלט בפיצול ב-$x=1$.
$$\\int_0^2|x-1|\\,dx=\\int_0^1(1-x)\\,dx+\\int_1^2(x-1)\\,dx.$$

### צעד 2: חישוב כל חלק עם FTC.
$$\\int_0^1(1-x)\\,dx=\\left[x-\\frac{x^2}{2}\\right]_0^1=\\frac{1}{2}.$$
$$\\int_1^2(x-1)\\,dx=\\left[\\frac{x^2}{2}-x\\right]_1^2=\\frac{1}{2}.$$

### צעד 3: סכום.
$$\\int_0^2|x-1|\\,dx=1.$$

**פרשנות גיאומטרית (ב):** גרף $y=|x-1|$ הוא צורת V עם קודקוד ב-$(1,0)$; שני המשולשים בשטח $1/2$ כל אחד, ומאשרים שטח כולל $1$.

**הערה לבחינה:** אל תנסו לאינטגרל $\\sin(t^2)$ בחלק (א) — אין קדומה אלמנטרית (אינטגרלי פרנל). FTC חלק 1 הוא קיצור בשורה אחת. חלק (ב) בודק פיצול ערך מוחלט לפני FTC.""",
}

CHECKPOINT1_EN = """**(a) $\\displaystyle\\int_0^\\pi \\sin x\\,dx$**

**Step 1 — Antiderivative:** An antiderivative of $\\sin x$ is $F(x)=-\\cos x$ (since $\\frac{d}{dx}(-\\cos x)=\\sin x$).

**Step 2 — Apply FTC Part 2:**
$$\\int_0^\\pi \\sin x\\,dx = [-\\cos x]_0^\\pi = (-\\cos\\pi) - (-\\cos 0) = -(-1) - (-1) = 1 + 1 = 2.$$

On $[0,\\pi]$, $\\sin x\\ge 0$, so signed area equals geometric area under one arch.

**(b) $\\displaystyle\\int_1^e \\frac{1}{x}\\,dx$**

**Step 1 — Antiderivative:** $F(x)=\\ln x$ (valid since $x>0$ on $[1,e]$).

**Step 2 — Evaluate:**
$$[\\ln x]_1^e = \\ln e - \\ln 1 = 1 - 0 = 1.$$

This is the defining integral linking the natural logarithm to the number $e$."""

CHECKPOINT1_HE = """**(א) $\\displaystyle\\int_0^\\pi \\sin x\\,dx$**

**צעד 1 — קדומה:** קדומה של $\\sin x$ היא $F(x)=-\\cos x$ (כי $\\frac{d}{dx}(-\\cos x)=\\sin x$).

**צעד 2 — יישום FTC חלק 2:**
$$\\int_0^\\pi \\sin x\\,dx=[-\\cos x]_0^\\pi=(-\\cos\\pi)-(-\\cos 0)=1+1=2.$$

ב-$[0,\\pi]$, $\\sin x\\ge 0$, ולכן שטח עם סימן שווה לשטח גיאומטרי תחת קשת אחת.

**(ב) $\\displaystyle\\int_1^e \\frac{1}{x}\\,dx$**

**צעד 1 — קדומה:** $F(x)=\\ln x$ (תקף כי $x>0$ ב-$[1,e]$).

**צעד 2 — חישוב:**
$$[\\ln x]_1^e=\\ln e-\\ln 1=1-0=1.$$

זה האינטגרל המגדיר שמקשר את הלוגריתם הטבעי למספר $e$."""

CHECKPOINT2_EN = """**Problem:** $\\displaystyle\\int_1^e \\frac{\\ln x}{x}\\,dx$ using substitution.

**Step 1 — Choose $u=\\ln x$, so $du=\\frac{dx}{x}$.** The integrand $\\frac{\\ln x}{x}\\,dx$ becomes $u\\,du$ exactly.

**Step 2 — Change limits:**
- $x=1 \\Rightarrow u=\\ln 1=0$.
- $x=e \\Rightarrow u=\\ln e=1$.

**Step 3 — Integrate in $u$:**
$$\\int_0^1 u\\,du = \\left[\\frac{u^2}{2}\\right]_0^1 = \\frac{1}{2} - 0 = \\frac{1}{2}.$$

**Check:** Back-substitution gives $\\left[\\frac{(\\ln x)^2}{2}\\right]_1^e = \\frac{1}{2}-0 = \\frac{1}{2}$ — same answer. **Exam tip:** When $du/dx$ appears as a factor in the integrand, substitution with changed limits is usually fastest."""

CHECKPOINT2_HE = """**בעיה:** $\\displaystyle\\int_1^e \\frac{\\ln x}{x}\\,dx$ באמצעות הצבה.

**צעד 1 — בוחרים $u=\\ln x$, ולכן $du=\\frac{dx}{x}$.** האינטגרנד $\\frac{\\ln x}{x}\\,dx$ הופך ל-$u\\,du$ בדיוק.

**צעד 2 — שינוי גבולות:**
- $x=1 \\Rightarrow u=0$.
- $x=e \\Rightarrow u=1$.

**צעד 3 — אינטגרציה ב-$u$:**
$$\\int_0^1 u\\,du=\\left[\\frac{u^2}{2}\\right]_0^1=\\frac{1}{2}.$$

**בדיקה:** חזרה ל-$x$ נותנת $\\left[\\frac{(\\ln x)^2}{2}\\right]_1^e=\\frac{1}{2}$ — אותה תשובה. **טיפ לבחינה:** כש-$du/dx$ מופיע כגורם באינטגרנד, הצבה עם שינוי גבולות בדרך כלל הכי מהירה."""

METHOD = {
    "body_en_md": """| Problem type | Method | Key rule |
|---|---|---|
| Basic definite integral | Antiderivative + FTC Part 2 | $[F(x)]_a^b = F(b)-F(a)$, no $+C$ |
| With substitution | Change limits OR back-substitute | Never mix the two approaches |
| Absolute value integrand | Split at zero crossing | $\\int|f|=$ sum of signed pieces |
| Odd/even on $[-a,a]$ | Symmetry shortcut | Odd: $0$; Even: $2\\int_0^a f$ |
| Derivative of integral (FTC 1) | FTC Part 1 + chain rule | $f(g(x))\\cdot g'(x)$ |
| Reversed limits | Swap-limits property | $\\int_a^b f = -\\int_b^a f$ |
| Split/merge intervals | Additivity | $\\int_a^c + \\int_c^b = \\int_a^b$ |

**Decision tree (use before computing):**
1. Is there a substitution? → Change limits with $u$ or back-substitute — pick one.
2. Is there an absolute value? → Find zeros, split, remove bars piecewise.
3. Does the problem ask for a derivative of an integral? → FTC Part 1; circle the upper limit.
4. Are limits reversed ($a>b$)? → Flip sign first, or integrate and accept a negative result.

**Exam habit:** Write $[F(x)]_a^b$ explicitly, then substitute numbers on the next line — setup earns partial credit on Bagrut and Calc 1 rubrics.""",
    "body_he_md": """| סוג בעיה | שיטה | כלל מפתח |
|---|---|---|
| אינטגרל בסיסי | קדומה + FTC חלק 2 | $[F(x)]_a^b=F(b)-F(a)$, בלי $+C$ |
| עם הצבה | שינוי גבולות או חזרה | לא לערבב שתי הגישות |
| אינטגרנד עם ערך מוחלט | פיצול באפס | $\\int|f|=$ סכום חלקים עם סימן |
| אי-זוגי/זוגי על $[-a,a]$ | קיצור סימטריה | אי-זוגי: $0$; זוגי: $2\\int_0^a f$ |
| נגזרת של אינטגרל (FTC 1) | FTC חלק 1 + שרשרת | $f(g(x))\\cdot g'(x)$ |
| גבולות הפוכים | תכונת החלפה | $\\int_a^b f=-\\int_b^a f$ |
| פיצול/מיזוג קטעים | תוספתיות | $\\int_a^c+\\int_c^b=\\int_a^b$ |

**עץ החלטות (לפני חישוב):**
1. יש הצבה? → שנה גבולות עם $u$ או חזור — בחר אחת.
2. יש ערך מוחלט? → מצא אפסים, פצל, הסר ערך מוחלט בחלקים.
3. השאלה מבקשת נגזרת של אינטגרל? → FTC חלק 1; סמן את הגבול העליון.
4. הגבולות הפוכים ($a>b$)? → הפוך סימן קודם, או קבל תוצאה שלילית.

**הרגל לבחינה:** כתבו $[F(x)]_a^b$ במפורש, ואז הציבו מספרים בשורה הבאה — הגדרה מזכה בניקוד חלקי בבגרות וחדו״א.""",
}

PITFALL = {
    "body_en_md": """These five mistakes appear repeatedly on Bagrut 581/807 and 5-unit papers. Recognize them before they cost points.

1. **Adding $+C$ to a definite integral.** A definite integral is a number. Even if you write $F(x)+C$, it cancels: $(F(b)+C)-(F(a)+C)=F(b)-F(a)$. Examiners deduct for unnecessary $+C$ because it signals confusion with indefinite integrals.

2. **Forgetting to change limits in substitution.** When you switch to $u$, either evaluate at new $u$-limits or back-substitute to $x$ before using original limits. Mixing the two (integrate in $u$ but plug in $x$-values) is the most common substitution error.

3. **Reversed evaluation $F(a)-F(b)$.** Always **upper minus lower**: $F(b)-F(a)$. Reversing gives the negative of the correct answer — a sign error that looks like a "fixable" arithmetic slip but reflects wrong FTC notation.

4. **Signed vs. geometric area.** $\\int_0^{2\\pi}\\sin x\\,dx=0$ due to cancellation, but geometric area under one arch is $2$. Read whether the question asks for "net area" or "total area enclosed."

5. **FTC Part 1 without chain rule.** $\\frac{d}{dx}\\int_0^{x^2}f(t)\\,dt=f(x^2)\\cdot 2x$, not just $f(x^2)$. The derivative of the upper limit is part of the answer.""",
    "body_he_md": """חמש הטעויות האלה חוזרות שוב ושוב בבגרות 581/807 ובשאלוני 5 יחידות. זהו אותן לפני שהן עולות בנקודות.

1. **הוספת $+C$ לאינטגרל מסוים.** אינטגרל מסוים הוא מספר. גם אם כותבים $F(x)+C$, הוא מתבטל: $(F(b)+C)-(F(a)+C)=F(b)-F(a)$. בודקים מורידים נקודות על $+C$ מיותר — סימן לבלבול עם אינטגרל לא מסוים.

2. **שכחת שינוי גבולות בהצבה.** כשעוברים ל-$u$, מעריכים בגבולות $u$ חדשים **או** חוזרים ל-$x$ לפני גבולות מקוריים. ערבוב (אינטגרציה ב-$u$ עם הצבת $x$) — הטעות הנפוצה ביותר בהצבה.

3. **הערכה הפוכה $F(a)-F(b)$.** תמיד **עליון פחות תחתון**: $F(b)-F(a)$. היפוך נותן את שלילי התשובה — נראה כמו טעות חשבון אך משקף סימון FTC שגוי.

4. **שטח עם סימן מול גיאומטרי.** $\\int_0^{2\\pi}\\sin x\\,dx=0$ בגלל ביטול, אך שטח גיאומטרי תחת קשת אחת הוא $2$. קראו אם השאלה מבקשת "שטח נטו" או "שטח כולל סגור".

5. **FTC חלק 1 ללא כלל שרשרת.** $\\frac{d}{dx}\\int_0^{x^2}f(t)\\,dt=f(x^2)\\cdot 2x$, לא רק $f(x^2)$. נגזרת הגבול העליון חלק מהתשובה.""",
}

WHY = {
    "body_en_md": """Definite integrals are not an isolated topic — they connect directly to your learning path on A Step Forward and to real quantitative reasoning.

**You will use this to unlock:**
- `concept:integrals_applications` **Integral Applications (Volumes & Optimization)** — areas, volumes of revolution, and accumulation problems all start with $\\int_a^b f\\,dx$.
- `concept:torque` **Torque & Static Equilibrium** — work integrals and moment calculations use the same FTC evaluation machinery.

**Builds on:**
- `concept:integrals_intro` **Indefinite Integrals** — antiderivatives and $+C$ are the prerequisite; definite integrals drop the constant.

**Why it matters for exams:** Bagrut and university courses reward *transfer* — applying FTC, substitution, and absolute-value splitting in a new context. When you study, always ask: "Is this signed area, geometric area, or a derivative-of-integral problem?" That classification picks the method.""",
    "body_he_md": """אינטגרלים מסוימים אינם נושא מבודד — הם מחוברים ישירות למסלול הלימוד שלך ב-A Step Forward ולחשיבה כמותית אמיתית.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:integrals_applications` **יישומי אינטגרלים (נפחים ובעיות קיצון)** — שטחים, נפחי סיבוב ובעיות הצטברות מתחילים ב-$\\int_a^b f\\,dx$.
- `concept:torque` **מומנט ושיווי משקל סטטי** — אינטגרלים של עבודה וחישובי מומנט משתמשים באותו מנגנון FTC.

**מבוסס על:**
- `concept:integrals_intro` **אינטגרל כללי (לא מסוים)** — קדומות ו-$+C$ הם התנאי; באינטגרל מסוים מסירים את הקבוע.

**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים *העברה* — יישום FTC, הצבה ופיצול ערך מוחלט בהקשר חדש. בזמן לימוד, שאלו: "האם זה שטח עם סימן, שטח גיאומטרי, או בעיית נגזרת של אינטגרל?" — הסיווג בוחר את השיטה.""",
}

BEFORE_EXAM = {
    "body_en_md": """**Must-know formulas:**
- $\\int_a^b f = F(b)-F(a)$ — upper minus lower, **no** $+C$.
- Substitution: change limits with $u$, **or** back-substitute before evaluating — never both.
- FTC Part 1: $\\frac{d}{dx}\\int_a^x f(t)\\,dt = f(x)$; chain rule when upper limit is $g(x)$.
- Splitting: $\\int_a^b f = \\int_a^c f + \\int_c^b f$.

**Strategy for Bagrut questions:**
1. Identify the antiderivative (know your table: power, trig, $1/x$, $e^x$).
2. Write bracket notation $[F(x)]_a^b$ explicitly before numbers.
3. For substitution: write old limits and new $u$-limits side by side.
4. For absolute values: find where expression $=0$, split there, integrate each piece.

**Common Bagrut patterns:** area under curve (watch sign below axis), FTC Part 1 with $x^2$ upper limit, substitution with $\\ln x$ or $e^{x^2}$ factor, reversed limits ($\\int_2^0$).

**Memorize:** $\\int_0^\\pi\\sin x\\,dx=2$, $\\int_0^{\\pi/2}\\cos x\\,dx=1$, $\\int_1^e\\frac{1}{x}\\,dx=1$.""",
    "body_he_md": """**נוסחאות חובה:**
- $\\int_a^b f=F(b)-F(a)$ — עליון פחות תחתון, **בלי** $+C$.
- הצבה: שנה גבולות עם $u$, **או** חזור לפני הערכה — לעולם לא שניהם.
- FTC חלק 1: $\\frac{d}{dx}\\int_a^x f(t)\\,dt=f(x)$; כלל שרשרת כשהגבול העליון $g(x)$.
- פיצול: $\\int_a^b f=\\int_a^c f+\\int_c^b f$.

**אסטרטגיה לשאלות בגרות:**
1. זהו קדומה (דעו טבלה: חזקה, טrig, $1/x$, $e^x$).
2. כתבו $[F(x)]_a^b$ במפורש לפני מספרים.
3. להצבה: כתבו גבולות ישנים ו-$u$ חדשים זה לצד זה.
4. לערכים מוחלטים: מצאו היכן הביטוי $=0$, פצלו, חשבו כל חלק.

**דפוסים נפוצים בבגרות:** שטח מתחת לעקומה (שימו לב לסימן מתחת לציר), FTC חלק 1 עם גבול $x^2$, הצבה עם $\\ln x$ או גורם $e^{x^2}$, גבולות הפוכים ($\\int_2^0$).

**לזכור:** $\\int_0^\\pi\\sin x\\,dx=2$, $\\int_0^{\\pi/2}\\cos x\\,dx=1$, $\\int_1^e\\frac{1}{x}\\,dx=1$.""",
}

SUMMARY = {
    "body_en_md": """- $\\int_a^b f\\,dx$ is a **number** (signed net area), not a function family.
- **FTC Part 2:** $\\int_a^b f = F(b)-F(a)$ for any antiderivative $F$ — no $+C$.
- **Substitution:** change limits with $u$ **or** back-substitute before evaluation — pick one approach.
- **Properties:** linearity, swap-limits-flips-sign, splitting at intermediate points.
- **FTC Part 1:** $\\frac{d}{dx}\\int_a^x f(t)\\,dt = f(x)$; add chain rule when the upper limit is $g(x)$.
- **Absolute values:** split at zeros; FTC requires continuity/smoothness on each piece.
- **Takeaway:** Classify the problem first (evaluate, substitute, differentiate, or split) — then the method follows.""",
    "body_he_md": """- $\\int_a^b f\\,dx$ הוא **מספר** (שטח נטו עם סימן), לא משפחת פונקציות.
- **FTC חלק 2:** $\\int_a^b f=F(b)-F(a)$ לכל קדומה $F$ — בלי $+C$.
- **הצבה:** שנה גבולות עם $u$ **או** חזור לפני הערכה — בחר גישה אחת.
- **תכונות:** ליניאריות, החלפת גבולות = היפוך סימן, פיצול בנקודות ביניים.
- **FTC חלק 1:** $\\frac{d}{dx}\\int_a^x f(t)\\,dt=f(x)$; הוסיפו שרשרת כשהגבול העליון $g(x)$.
- **ערכים מוחלטים:** פיצול באפסים; FTC דורש רציפות/חלקות בכל חלק.
- **מסקנה:** סווגו את הבעיה קודם (חישוב, הצבה, גזירה, או פיצול) — ואז השיטה נובעת.""",
}

EXPLANATIONS = [
    {
        "en": """**Why this is correct:**
Apply FTC Part 2 to $\\int_0^3 x^2\\,dx$. Antiderivative: $F(x)=x^3/3$. Then $[x^3/3]_0^3 = 27/3 - 0 = 9$.

**How to think about it:**
Power-rule antiderivative, then bracket notation with upper minus lower. On $[0,3]$, $x^2\\ge 0$, so the answer is positive signed area under the parabola.

**Common slip:**
Forgetting to divide by 3 ($x^2\\to x^3/3$, not $x^3$). Another error: evaluating $F(0)$ incorrectly or writing $F(0)-F(3)$ instead of $F(3)-F(0)$.

**Exam tip:**
$\\int_0^3 x^2\\,dx=9$ is a standard warm-up. Write $[x^3/3]_0^3$ before substituting — partial credit for setup on Bagrut rubrics.""",
        "he": """**למה זה נכון:**
יישום FTC חלק 2 על $\\int_0^3 x^2\\,dx$. קדומה: $F(x)=x^3/3$. אז $[x^3/3]_0^3=27/3-0=9$.

**איך לחשוב על זה:**
קדומה לפי כלל החזקה, ואז סימון סוגריים עם עליון פחות תחתון. ב-$[0,3]$, $x^2\\ge 0$, ולכן התשובה שטח חיובי מתחת לפרבולה.

**טעות נפוצה:**
שכחת חלוקה ב-3 ($x^2\\to x^3/3$, לא $x^3$). טעות נוספת: $F(0)-F(3)$ במקום $F(3)-F(0)$.

**טיפ לבחינה:**
$\\int_0^3 x^2\\,dx=9$ — חימום סטנדרטי. כתבו $[x^3/3]_0^3$ לפני הצבה — ניקוד חלקי על הגדרה במחוון בגרות. ודאו שהתשובה חיובית כשהאינטגרנד אי-שלילי על כל הקטע.""",
    },
    {
        "en": """**Why this is correct:**
$\\int_0^\\pi \\sin x\\,dx = [-\\cos x]_0^\\pi = (-\\cos\\pi)-(-\\cos 0) = -(-1)-(-1) = 1+1 = 2$. On $[0,\\pi]$, sine is non-negative, so signed area equals geometric area under one arch.

**How to think about it:**
Antiderivative of $\\sin x$ is $-\\cos x$ (watch the minus sign). Unit-circle values: $\\cos\\pi=-1$, $\\cos 0=1$. Bracket notation keeps the two substitutions organized.

**Common slip:**
Sign error on the antiderivative ($+\\cos x$ instead of $-\\cos x$). Confusing $\\int_0^\\pi\\sin x\\,dx=2$ with $\\int_0^{2\\pi}\\sin x\\,dx=0$ (full-period cancellation).

**Exam tip:**
When the interval is exactly one arch of sine, the answer is $2$ — memorize alongside $\\int_0^{\\pi/2}\\cos x\\,dx=1$. These appear as quick-check questions on 581/807.""",
        "he": """**למה זה נכון:**
$\\int_0^\\pi \\sin x\\,dx=[-\\cos x]_0^\\pi=(-\\cos\\pi)-(-\\cos 0)=1+1=2$. ב-$[0,\\pi]$, סינוס אי-שלילי, ולכן שטח עם סימן שווה לשטח גיאומטרי תחת קשת אחת.

**איך לחשוב על זה:**
קדומה של $\\sin x$ היא $-\\cos x$ (שימו לב למינוס). ערכי מעגל יחידה: $\\cos\\pi=-1$, $\\cos 0=1$. סימון סוגריים מארגן את שתי ההצבות.

**טעות נפוצה:**
שגיאת סימן בקדומה ($+\\cos x$). בלבול בין $\\int_0^\\pi\\sin x\\,dx=2$ ל-$\\int_0^{2\\pi}\\sin x\\,dx=0$ (ביטול במחזור שלם).

**טיפ לבחינה:**
כשהקטע הוא קשת אחת של סינוס, התשובה $2$ — לזכור לצד $\\int_0^{\\pi/2}\\cos x\\,dx=1$. מופיע בשאלות מהירות ב-581/807.""",
    },
    {
        "en": """**Why this is correct:**
$[x^3-x^2]_{-1}^{2} = (8-4)-((-1)^3-(-1)^2) = 4-(-1-1) = 4+2 = 6$. FTC Part 2 with antiderivative $F(x)=x^3-x^2$.

**How to think about it:**
Integrate term by term, then evaluate at upper ($x=2$) and lower ($x=-1$) limits. Careful arithmetic at $x=-1$: $(-1)^3=-1$ but $(-1)^2=+1$.

**Common slip:**
Computing $F(-1)$ as $+2$ instead of $-2$ (sign error on $(-1)^3$). Choosing wrong MCQ option by reversing subtraction ($F(-1)-F(2)=-6$).

**Exam tip:**
This exact integral appears in the lesson worked example. Write $F(2)$ and $F(-1)$ on separate lines before subtracting — examiners reward visible FTC setup.""",
        "he": """**למה זה נכון:**
$[x^3-x^2]_{-1}^{2}=(8-4)-((-1)^3-(-1)^2)=4-(-2)=6$. FTC חלק 2 עם קדומה $F(x)=x^3-x^2$.

**איך לחשוב על זה:**
אינטגרציה איבר-איבר, ואז הערכה בגבול עליון ($x=2$) ותחתון ($x=-1$). חשבון זהיר ב-$x=-1$: $(-1)^3=-1$ אך $(-1)^2=+1$.

**טעות נפוצה:**
חישוב $F(-1)$ כ-$+2$ במקום $-2$ (שגיאת סימן ב-$(-1)^3$). בחירת תשובה שגויה מהיפוך חיסור ($-6$).

**טיפ לבחינה:**
אינטגרל זה מופיע בדוגמה הפתורה בשיעור. כתבו $F(2)$ ו-$F(-1)$ בשורות נפרדות לפני חיסור — בודקים מעריכים הגדרת FTC גלויה. באפשרויות MCQ, $6$ הוא התשובה היחידה עם סימן נכון.""",
    },
    {
        "en": """**Why this is correct:**
Let $u=\\ln x$, $du=dx/x$. Limits: $x=1\\Rightarrow u=0$; $x=e\\Rightarrow u=1$. Then $\\int_0^1 u\\,du = [u^2/2]_0^1 = 1/2$.

**How to think about it:**
The factor $1/x$ is exactly $du$ when $u=\\ln x$ — a perfect substitution. Change limits with $u$ to avoid back-substitution.

**Common slip:**
Forgetting to change limits and evaluating $u^2/2$ at $x=1$ and $x=e$ instead of $u=0$ and $u=1$. Integrating $\\ln x$ directly without substitution (much harder).

**Exam tip:**
$\\int_1^e \\frac{\\ln x}{x}\\,dx$ is a standard 5-unit substitution template. Write $u=\\ln x$ and both limit pairs in the first line of your solution.""",
        "he": """**למה זה נכון:**
נגדיר $u=\\ln x$, $du=dx/x$. גבולות: $x=1\\Rightarrow u=0$; $x=e\\Rightarrow u=1$. אז $\\int_0^1 u\\,du=[u^2/2]_0^1=1/2$.

**איך לחשוב על זה:**
הגורם $1/x$ הוא בדיוק $du$ כש-$u=\\ln x$ — הצבה מושלמת. שינוי גבולות עם $u$ נמנע מחזרה ל-$x$.

**טעות נפוצה:**
שכחת שינוי גבולות והצבת $x=1,e$ במקום $u=0,1$. אינטגרציה ישירה של $\\ln x$ בלי הצבה (קשה הרבה יותר).

**טיפ לבחינה:**
$\\int_1^e \\frac{\\ln x}{x}\\,dx$ — תבנית הצבה סטנדרטית ל-5 יחידות. כתבו $u=\\ln x$ ושני זוגות גבולות בשורה הראשונה. התשובה $1/2$ קטנה מ-1 — סביר לפונקציה שגדלה לאט ב-$[1,e]$.""",
    },
    {
        "en": """**Why this is correct:**
$\\int_2^0(x+1)\\,dx = -\\int_0^2(x+1)\\,dx$ by the swap-limits rule. Antiderivative $F(x)=x^2/2+x$. Then $-[F(2)-F(0)] = -[(2+2)-0] = -4$.

**How to think about it:**
When the lower limit exceeds the upper limit, the integral is negative of the reversed-order integral. Alternatively compute directly: $[x^2/2+x]_2^0 = 0-4 = -4$.

**Common slip:**
Ignoring reversed limits and getting $+4$ (option A). Forgetting the swap rule and treating $\\int_2^0$ as $\\int_0^2$.

**Exam tip:**
Bagrut questions deliberately use $\\int_b^a$ with $b>a$ to test the property $\\int_a^b f = -\\int_b^a f$. Circle the limits before computing.""",
        "he": """**למה זה נכון:**
$\\int_2^0(x+1)\\,dx=-\\int_0^2(x+1)\\,dx$ לפי כלל החלפת גבולות. קדומה $F(x)=x^2/2+x$. אז $-[F(2)-F(0)]=-4$.

**איך לחשוב על זה:**
כשהגבול התחתון גדול מהעליון, האינטגרל הוא שלילי של האינטגרל בסדר הפוך. חלופה: $[x^2/2+x]_2^0=0-4=-4$.

**טעות נפוצה:**
התעלמות מגבולות הפוכים וקבלת $+4$. התייחסות ל-$\\int_2^0$ כאל $\\int_0^2$.

**טיפ לבחינה:**
שאלות בגרות משתמשות ב-$\\int_b^a$ עם $b>a$ כדי לבדוק $\\int_a^b f=-\\int_b^a f$. סמנו את הגבולות לפני חישוב. חלופה: חשבו ישירות $[F(x)]_2^0=F(0)-F(2)$ — אותה תוצאה $-4$ בלי שלב ביניים. תשובה חיובית $+4$ כמעט תמיד שגויה כאן.""",
    },
    {
        "en": """**Why this is correct:**
By FTC Part 1, if $g(x)=\\int_0^x t^2\\sin t\\,dt$, then $g'(x)=x^2\\sin x$. The upper limit is plain $x$, so no extra chain-rule factor is needed.

**How to think about it:**
FTC Part 1: differentiate the upper limit by substituting it into the integrand. Here $f(t)=t^2\\sin t$ and the limit is $x$, giving $x^2\\sin x$. Do not try to integrate $t^2\\sin t$ — that requires integration by parts and is not the point.

**Common slip:**
Adding a spurious $2x$ factor as if the upper limit were $x^2$. Attempting to evaluate the integral first (integration by parts) instead of differentiating directly.

**Exam tip:**
When the upper limit is plain $x$ and the lower is a constant, the derivative equals $f(x)$ in one line — full credit. Contrast with $\\int_0^{x^2}$ where you need $2x$.""",
        "he": """**למה זה נכון:**
לפי FTC חלק 1, אם $g(x)=\\int_0^x t^2\\sin t\\,dt$, אז $g'(x)=x^2\\sin x$. הגבול העליון הוא $x$ פשוט — אין גורם שרשרת נוסף.

**איך לחשוב על זה:**
FTC חלק 1: גזרו את הגבול העליון והציבו באינטגרנד. כאן $f(t)=t^2\\sin t$ והגבול $x$, ולכן $x^2\\sin x$. אל תנסו לאינטegrate $t^2\\sin t$ — זו לא המטרה.

**טעות נפוצה:**
הוספת $2x$ מיותר כאילו הגבול $x^2$. ניסיון לחשב את האינטגרל (אינטגרציה בחלקים) במקום לגזור ישירות.

**טיפ לבחינה:**
גבול עליון $x$ ותחתון קבוע → הנגזרת $f(x)$ בשורה אחת. השוו ל-$\\int_0^{x^2}$ שבו צריך $2x$.""",
    },
    {
        "en": """**Why this is correct:**
Antiderivative of $\\cos x$ is $\\sin x$. $[\\sin x]_0^\\pi = \\sin\\pi - \\sin 0 = 0 - 0 = 0$. The cosine arch above and below the axis on $[0,\\pi]$ contributes equal signed areas that cancel.

**How to think about it:**
Unlike $\\int_0^\\pi \\sin x\\,dx=2$, cosine on $[0,\\pi]$ is positive on $[0,\\pi/2)$ and negative on $(\\pi/2,\\pi]$, giving net zero. Do not confuse the two standard integrals.

**Common slip:**
Answering $2$ by copying the sine result. Sign error: antiderivative of $\\cos x$ is $+\\sin x$, not $-\\sin x$.

**Exam tip:**
Pair $\\int_0^\\pi\\sin x\\,dx=2$ with $\\int_0^\\pi\\cos x\\,dx=0$ in your review sheet — examiners love testing whether you know both.""",
        "he": """**למה זה נכון:**
קדומה של $\\cos x$ היא $\\sin x$. $[\\sin x]_0^\\pi=\\sin\\pi-\\sin 0=0$. קשת הקוסינוס מעל ומתחת לציר ב-$[0,\\pi]$ תורמת שטחים שמתבטלים.

**איך לחשוב על זה:**
בניגוד ל-$\\int_0^\\pi\\sin x\\,dx=2$, קוסינוס ב-$[0,\\pi]$ חיובי ב-$[0,\\pi/2)$ ושלילי ב-$(\\pi/2,\\pi]$, ולכן נטו $0$. אל תערבבו בין שני האינטגרלים הסטנדרטיים.

**טעות נפוצה:**
תשובה $2$ מהעתקת תוצאת הסינוס. שגיאת סימן: קדומה של $\\cos x$ היא $+\\sin x$.

**טיפ לבחינה:**
שלבו $\\int_0^\\pi\\sin x\\,dx=2$ עם $\\int_0^\\pi\\cos x\\,dx=0$ בדף חזרה — בודקים בודקים אם יודעים את שניהם. זכרו: קוסינוס משנה סימן באמצע הקטע, סינוס לא.""",
    },
    {
        "en": """**Why this is correct:**
$x^{-1/2}$ has antiderivative $2\\sqrt{x}$ (power rule with $n=-1/2$). $[2\\sqrt{x}]_1^4 = 2(2)-2(1) = 4-2 = 2$.

**How to think about it:**
Rewrite $1/\\sqrt{x}=x^{-1/2}$, integrate to $\\frac{x^{1/2}}{1/2}=2x^{1/2}=2\\sqrt{x}$, then FTC. On $[1,4]$, the integrand is positive, so the answer is positive.

**Common slip:**
Using $\\ln x$ (wrong — that is for $1/x$, not $1/\\sqrt{x}$). Forgetting the factor of 2 from the power rule ($n=-1/2\\Rightarrow$ divide by $1/2$).

**Exam tip:**
$\\int_1^4 x^{-1/2}\\,dx=2$ is a quick power-rule definite integral. Estimate: average height about $1/\\sqrt{2.5}\\approx 0.63$ times width 3 gives roughly 2 — sanity check passed.""",
        "he": """**למה זה נכון:**
ל-$x^{-1/2}$ קדומה $2\\sqrt{x}$ (כלל חזקה עם $n=-1/2$). $[2\\sqrt{x}]_1^4=2(2)-2(1)=2$.

**איך לחשוב על זה:**
כתבו $1/\\sqrt{x}=x^{-1/2}$, אינטegrate ל-$2\\sqrt{x}$, ואז FTC. ב-$[1,4]$, האינטגרנד חיובי, ולכן התשובה חיובית.

**טעות נפוצה:**
שימוש ב-$\\ln x$ (שגוי — זה ל-$1/x$, לא $1/\\sqrt{x}$). שכחת גורם 2 מכלל החזקה (חלוקה ב-$1/2$).

**טיפ לבחינה:**
$\\int_1^4 x^{-1/2}\\,dx=2$ — אינטגרל מהיר לפי כלל חזקה. הערכה: גובה ממוצע $\\approx 0.63$ כפול רוחב 3 $\\approx 2$ — בדיקת שפיות. אל תשתמשו ב-$\\ln x$ — זה שייך רק ל-$1/x$.""",
    },
]


def word_count(text: str) -> int:
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
    he_chars = len(re.findall(r"[\u0590-\u05FF]", he))
    lat = len(re.findall(r"[a-zA-Z]{3,}", he))
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

    data["version"] = 2
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
