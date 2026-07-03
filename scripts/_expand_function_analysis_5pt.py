#!/usr/bin/env python3
"""Expand function_analysis_5pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/function_analysis_5pt.json"

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


INTRO_EN = """Calculus gives us two derivative tools that together paint a complete picture of any smooth function. The first derivative $f'$ measures **rate of change** — where the graph rises, falls, or levels off. The second derivative $f''$ measures the **rate of that rate** — whether the curve bends upward (concave up) or downward (concave down).

In the Israeli 5-unit Bagrut, **חקירת פונקציה** (complete function investigation) is the flagship multi-part question: every paper includes at least one full investigation worth **25–30 points**. Examiners expect an explicit eight-step checklist — domain, roots, sign, asymptotes, monotonicity via $f'$, extrema, convexity via $f''$, and inflection points — with sign tables shown for both derivatives.

Mastering this lesson means more than memorizing rules. You must chain algebraic simplification, limit evaluation, and graphical interpretation into one coherent report. The three worked examples progress from a clean polynomial ($x^3-3x$) through a product-with-exponential ($xe^{-x}$) to a rational function with asymptotes ($x^2/(x^2-1)$). That ladder mirrors what appears on actual exams."""

INTRO_HE = """חשבון דיפרנציאלי מספק שני כלי נגזרת שיחד מציירים תמונה שלמה של כל פונקציה חלקה. הנגזרת הראשונה $f'$ מודדת **קצב שינוי** — היכן הגרף עולה, יורד או מתייצב. הנגזרת השנייה $f''$ מודדת **קצב של קצב** — האם העקומה כפופה למעלה (קמורה) או למטה (קעורה).

בבגרות 5 יחידות, **חקירת פונקציה מלאה** היא שאלת הדגל הרב-חלקית: בכל מבחן לפחות חקירה אחת בשווי **25–30 נקודות**. בוחנים מצפים לרשימת שמונה צעדים מפורשת — תחום, שורשים, סימן, אסימפטוטות, מונוטוניות דרך $f'$, קיצונות, קמירות דרך $f''$ ונקודות פיתול — עם טבלאות סימנים לשתי הנגזרות.

שליטה בשיעור אינה שינון כללים בלבד. צריך לשרשר פישוט אלגברי, חישוב גבולות ופרשנות גрафית לדוח אחד קוהרנטי. שלוש הדוגמאות הפתורות מתקדמות מפולינום נקי ($x^3-3x$) דרך מכפלה עם אקספוננט ($xe^{-x}$) לפונקציה רציונלית עם אסימפטוטות ($x^2/(x^2-1)$). סולם זה משקף את מה שמופיע בבחינות אמיתיות."""

DEF_EN = """**Step 1 — Domain:** Find all $x$ where $f(x)$ is defined. Exclude division by zero, even roots of negative numbers, and logarithms of non-positive arguments.

**Step 2 — Roots ($x$-intercepts):** Solve $f(x)=0$. Factor when possible; use the quadratic formula or numerical methods otherwise.

**Step 3 — Sign:** Build a sign table using roots and domain gaps. Determine intervals where $f(x)>0$ and $f(x)<0$.

**Step 4 — Asymptotes:**
- **Vertical:** $x=a$ if $\\lim_{x\\to a}|f(x)|=\\infty$ (denominator zero, numerator nonzero).
- **Horizontal:** $\\lim_{x\\to\\pm\\infty}f(x)=L$ gives $y=L$.
- **Oblique:** If deg(numerator) = deg(denominator)+1, perform long division; remainder $\\to 0$ gives $y=mx+b$.

**Step 5 — Monotonicity via $f'$:** Differentiate, find where $f'=0$ or undefined, sign-table $f'$. Where $f'>0$: increasing; where $f'<0$: decreasing.

**Step 6 — Local extrema:** At $x_0$ where $f'$ changes sign: local max if $+\\to-$, local min if $-\\to+$. Confirm with $f''(x_0)$ when convenient.

**Step 7 — Convexity via $f''$:** Sign-table $f''$. Where $f''>0$: concave up; where $f''<0$: concave down.

**Step 8 — Inflection points:** Points where $f''$ **changes sign** and $f$ is defined. $f''(x_0)=0$ alone is not enough."""

DEF_HE = """**צעד 1 — תחום הגדרה:** כל $x$ שבו $f(x)$ מוגדרת. הוציאו חלוקה באפס, שורש זוגי של מספר שלילי, ולוגריתם של ערך לא חיובי.

**צעד 2 — שורשים:** פתרון $f(x)=0$. פירוק לגורמים כשאפשר; נוסחת שורשים או שיטות אחרות אחרת.

**צעד 3 — סימן:** בנו טבלת סימנים לפי שורשים ורווחים בתחום. קבעו קטעים שבהם $f(x)>0$ ו-$f(x)<0$.

**צעד 4 — אסימפטוטות:**
- **אנכית:** $x=a$ אם $\\lim_{x\\to a}|f(x)|=\\infty$ (מכנה אפס, מונה לא אפס).
- **אופקית:** $\\lim_{x\\to\\pm\\infty}f(x)=L$ נותן $y=L$.
- **אלכסונית:** אם מעלה המונה = מעלה המכנה+1, חלקו פולינומים; שארית $\\to 0$ נותנת $y=mx+b$.

**צעד 5 — מונוטוניות דרך $f'$:** גזרו, מצאו $f'=0$ / לא מוגדרת, טבלת סימנים. $f'>0$: עולה; $f'<0$: יורדת.

**צעד 6 — קיצונות מקומיות:** ב-$x_0$ שבו $f'$ מחליפה סימן: מקסימום אם $+\\to-$; מינימום אם $-\\to+$. אשרו עם $f''(x_0)$ כשנוח.

**צעד 7 — קמירות דרך $f''$:** טבלת סימנים ל-$f''$. $f''>0$: קמורה; $f''<0$: קעורה.

**צעד 8 — נקודות פיתול:** היכן $f''$ **מחליפה סימן** ו-$f$ מוגדרת. $f''(x_0)=0$ לבדו אינו מספיק."""

THEORY_EN = """**Critical derivative rules for investigation:**

- $(x^n)' = nx^{n-1}$; $(e^x)' = e^x$; $(e^{f(x)})' = f'(x)e^{f(x)}$
- $(\\ln x)' = 1/x$; $(\\ln f(x))' = f'(x)/f(x)$
- $(\\sin x)' = \\cos x$; $(\\cos x)' = -\\sin x$
- **Product:** $(fg)' = f'g + fg'$ — essential for $xe^{-x}$, $x\\ln x$
- **Quotient:** $(f/g)' = (f'g - fg')/g^2$ — essential for rational functions
- **Chain:** $(f(g(x)))' = f'(g(x))\\cdot g'(x)$

**Asymptotes of rational $f(x)=P(x)/Q(x)$:**
- deg $P$ = deg $Q$: horizontal at $y =$ ratio of leading coefficients.
- deg $P$ = deg $Q$ + 1: oblique asymptote via long division.
- Vertical: roots of $Q$ not cancelled by common factors with $P$.

**Second derivative test (shortcut at critical points):**
- $f'(x_0)=0$, $f''(x_0)>0$ $\\Rightarrow$ local **minimum**.
- $f'(x_0)=0$, $f''(x_0)<0$ $\\Rightarrow$ local **maximum**.
- $f'(x_0)=0$, $f''(x_0)=0$ $\\Rightarrow$ **inconclusive** — use first derivative sign change.

**Sign-table discipline:** Always test one sample point per interval. For $f''$ of rational functions, track powers of denominators carefully — $(x^2-1)^3$ and $(x^2-1)^2$ behave differently.

**Connecting $f'$ and $f''$ on one sketch:** Rising + concave up means accelerating increase; rising + concave down means slowing increase approaching a peak. This visual language helps verify extrema before writing coordinates."""

THEORY_HE = """**כללי נגזרת קריטיים לחקירה:**

- $(x^n)' = nx^{n-1}$; $(e^x)' = e^x$; $(e^{f(x)})' = f'(x)e^{f(x)}$
- $(\\ln x)' = 1/x$; $(\\ln f(x))' = f'(x)/f(x)$
- $(\\sin x)' = \\cos x$; $(\\cos x)' = -\\sin x$
- **מכפלה:** $(fg)' = f'g + fg'$ — חיוני ל-$xe^{-x}$, $x\\ln x$
- **מנה:** $(f/g)' = (f'g - fg')/g^2$ — חיוני לפונקציות רציונליות
- **שרשרת:** $(f(g(x)))' = f'(g(x))\\cdot g'(x)$

**אסימפטוטות של $f=P/Q$ רציונלית:**
- $\\deg P = \\deg Q$: אופקית ב-$y =$ יחס המקדמים המובילים.
- $\\deg P = \\deg Q + 1$: אלכסונית בחלוקת פולינומים.
- אנכית: שורשי $Q$ שלא מתבטלים בגורם משותף עם $P$.

**מבחן הנגזרת השנייה (קיצור בנקודות קריטיות):**
- $f'(x_0)=0$, $f''(x_0)>0$ $\\Rightarrow$ **מינימום** מקומי.
- $f'(x_0)=0$, $f''(x_0)<0$ $\\Rightarrow$ **מקסימום** מקומי.
- $f'(x_0)=0$, $f''(x_0)=0$ $\\Rightarrow$ **לא מכריע** — השתמשו בשינוי סימן $f'$.

**משמעת טבלת סימנים:** תמיד בדקו נקודת דוגמה בכל קטע. ב-$f''$ של פונקציות רציונליות, עקבו בזהירות אחרי חזקות המכנה — $(x^2-1)^3$ ו-$(x^2-1)^2$ מתנהגות אחרת.

**חיבור $f'$ ו-$f''$ בשרטוט אחד:** עולה + קמורה = עלייה מאיצה; עולה + קעורה = עלייה מאטה לקראת פסגה. שפה ויזואלית זו עוזרת לאמת קיצונים לפני כתיבת קואורדינטות."""

WE1_EN = """**Investigate $f(x) = x^3 - 3x$ completely.**

### Move 1: Domain
$f$ is a polynomial — defined on $\\mathbb{R}$. No restrictions.

### Move 2: Roots
$$x^3-3x = x(x^2-3) = 0 \\Rightarrow x = 0,\\, \\pm\\sqrt{3}$$

### Move 3: Sign table
Test intervals: $f<0$ on $(-\\infty,-\\sqrt{3})$, $f>0$ on $(-\\sqrt{3},0)$, $f<0$ on $(0,\\sqrt{3})$, $f>0$ on $(\\sqrt{3},\\infty)$.

### Move 4: Asymptotes
Polynomial — no vertical, horizontal, or oblique asymptotes.

### Move 5: Monotonicity
$$f'(x) = 3x^2-3 = 3(x-1)(x+1)$$
Zeros at $x=\\pm 1$. Sign: $f'>0$ on $(-\\infty,-1)$ and $(1,\\infty)$; $f'<0$ on $(-1,1)$.

### Move 6: Extrema
$x=-1$: $f'$ changes $+\\to-$ $\\Rightarrow$ local max, $f(-1)=2$. $x=1$: $-\\to+$ $\\Rightarrow$ local min, $f(1)=-2$.

### Move 7: Convexity
$f''(x)=6x$. Concave up ($f''>0$) for $x>0$; concave down for $x<0$.

### Move 8: Inflection
$f''=0$ at $x=0$ with sign change $\\Rightarrow$ inflection at $(0,0)$.

**Sketch note:** The graph crosses the origin, peaks at $(-1,2)$, dips at $(1,-2)$, and changes curvature at the origin."""

WE1_HE = """**חקרו לחלוטין את $f(x) = x^3 - 3x$.**

### צעד 1: תחום
$f$ פולינום — מוגדרת על $\\mathbb{R}$. אין הגבלות.

### צעד 2: שורשים
$$x^3-3x = x(x^2-3) = 0 \\Rightarrow x = 0,\\, \\pm\\sqrt{3}$$

### צעד 3: טבלת סימן
$f<0$ ב-$(-\\infty,-\\sqrt{3})$, $f>0$ ב-$(-\\sqrt{3},0)$, $f<0$ ב-$(0,\\sqrt{3})$, $f>0$ ב-$(\\sqrt{3},\\infty)$.

### צעד 4: אסימפטוטות
פולינום — אין אסימפטוטות.

### צעד 5: מונוטוניות
$$f'(x) = 3x^2-3 = 3(x-1)(x+1)$$
אפסים ב-$x=\\pm 1$. $f'>0$ ב-$(-\\infty,-1)$ וב-$(1,\\infty)$; $f'<0$ ב-$(-1,1)$.

### צעד 6: קיצונות
$x=-1$: $f'$ מ-$+\\to-$ $\\Rightarrow$ מקסימום מקומי, $f(-1)=2$. $x=1$: $-\\to+$ $\\Rightarrow$ מינימום, $f(1)=-2$.

### צעד 7: קמירות
$f''(x)=6x$. קמורה ($f''>0$) ל-$x>0$; קעורה ל-$x<0$.

### צעד 8: פיתול
$f''=0$ ב-$x=0$ עם שינוי סימן $\\Rightarrow$ פיתול ב-$(0,0)$.

**הערת שרטוט:** הגרף חוצה את הראשית, פסגה ב-$(-1,2)$, שקע ב-$(1,-2)$, ומשנה קמירות במקור."""

WE2_EN = """**Investigate $f(x) = xe^{-x}$ completely.**

### Move 1: Domain
$\\mathbb{R}$ — exponential is always positive.

### Move 2: Roots
$xe^{-x}=0 \\Rightarrow x=0$ (since $e^{-x}>0$ for all $x$).

### Move 3: Sign
$f(x)>0$ for $x>0$; $f(x)<0$ for $x<0$.

### Move 4: Asymptotes
As $x\\to+\\infty$: $xe^{-x}\\to 0$ (exponential wins) $\\Rightarrow$ horizontal $y=0$.
As $x\\to-\\infty$: $xe^{-x}\\to-\\infty$ — no horizontal asymptote on the left.

### Move 5: Monotonicity
$$f'(x) = e^{-x}(1-x)$$
Since $e^{-x}>0$: $f'>0$ iff $x<1$. Increasing on $(-\\infty,1)$; decreasing on $(1,\\infty)$.

### Move 6: Extrema
$f'(1)=0$, sign change $+\\to-$ $\\Rightarrow$ **local maximum** at $(1, e^{-1})=(1, 1/e)$.

### Move 7: Convexity
$$f''(x) = e^{-x}(x-2)$$
$f''>0$ for $x>2$ (concave up); $f''<0$ for $x<2$ (concave down).

### Move 8: Inflection
$f''=0$ at $x=2$ with sign change $\\Rightarrow$ inflection at $(2, 2e^{-2})=(2, 2/e^2)$.

**Key insight:** $e^{-x}$ is always positive, so every sign decision reduces to the linear factor in $f'$ or $f''$."""

WE2_HE = """**חקרו לחלוטין את $f(x) = xe^{-x}$.**

### צעד 1: תחום
$\\mathbb{R}$ — האקספוננט תמיד חיובי.

### צעד 2: שורשים
$xe^{-x}=0 \\Rightarrow x=0$ (כי $e^{-x}>0$ לכל $x$).

### צעד 3: סימן
$f(x)>0$ ל-$x>0$; $f(x)<0$ ל-$x<0$.

### צעד 4: אסימפטוטות
כ-$x\\to+\\infty$: $xe^{-x}\\to 0$ $\\Rightarrow$ אופקית $y=0$.
כ-$x\\to-\\infty$: $xe^{-x}\\to-\\infty$ — אין אסימפטוטה אופקית משמאל.

### צעד 5: מונוטוניות
$$f'(x) = e^{-x}(1-x)$$
מכיוון $e^{-x}>0$: $f'>0$ אם ורק אם $x<1$. עולה ב-$(-\\infty,1)$; יורדת ב-$(1,\\infty)$.

### צעד 6: קיצון
$f'(1)=0$, שינוי $+\\to-$ $\\Rightarrow$ **מקסימום מקומי** ב-$(1, 1/e)$.

### צעד 7: קמירות
$$f''(x) = e^{-x}(x-2)$$
$f''>0$ ל-$x>2$ (קמורה); $f''<0$ ל-$x<2$ (קעורה).

### צעד 8: פיתול
$f''=0$ ב-$x=2$ עם שינוי סימן $\\Rightarrow$ פיתול ב-$(2, 2/e^2)$.

**תובנה:** $e^{-x}$ תמיד חיובי, כך שכל החלטת סימן מצטמצמת לגורם הלינארי ב-$f'$ או $f''$."""

WE3_EN = """**Investigate $f(x) = \\dfrac{x^2}{x^2-1}$ completely.**

### Move 1: Domain
$x^2-1\\neq 0 \\Rightarrow x\\neq\\pm 1$. Domain: $\\mathbb{R}\\setminus\\{-1,1\\}$.

### Move 2: Roots
$x^2=0 \\Rightarrow x=0$ (denominator nonzero at $x=0$).

### Move 3: Sign
Numerator $x^2\\geq 0$. Denominator $(x-1)(x+1)$ positive for $|x|>1$, negative for $|x|<1$. So $f\\geq 0$ for $|x|>1$; $f\\leq 0$ for $|x|<1$.

### Move 4: Asymptotes
Vertical at $x=\\pm 1$ (denom $=0$, numer $\\neq 0$). Horizontal: $\\lim_{x\\to\\pm\\infty}\\frac{x^2}{x^2-1}=1$ $\\Rightarrow$ $y=1$.

### Move 5: Monotonicity
$$f'(x) = \\frac{-2x}{(x^2-1)^2}$$
$f'=0$ at $x=0$. Increasing for $x<0$ (in domain); decreasing for $x>0$.

### Move 6: Extrema
$f'(0)=0$, $+\\to-$ $\\Rightarrow$ **local maximum** at $(0,0)$.

### Move 7: Convexity
$$f''(x) = \\frac{6x^2+2}{(x^2-1)^3}$$
Numerator always positive. $f''>0$ for $|x|>1$; $f''<0$ for $|x|<1$.

### Move 8: Inflection
No inflection — $f''$ cannot change sign without crossing $x=\\pm 1$ where $f$ is undefined.

**Sketch note:** Two branches above $y=1$ for $|x|>1$, a dip at $(0,0)$ between vertical asymptotes at $x=\\pm 1$."""

WE3_HE = """**חקרו לחלוטין את $f(x) = \\dfrac{x^2}{x^2-1}$.**

### צעד 1: תחום
$x^2-1\\neq 0 \\Rightarrow x\\neq\\pm 1$. תחום: $\\mathbb{R}\\setminus\\{-1,1\\}$.

### צעד 2: שורשים
$x^2=0 \\Rightarrow x=0$ (מכנה לא אפס ב-$x=0$).

### צעד 3: סימן
מונה $x^2\\geq 0$. מכנה $(x-1)(x+1)$ חיובי ל-$|x|>1$, שלילי ל-$|x|<1$. לכן $f\\geq 0$ ל-$|x|>1$; $f\\leq 0$ ל-$|x|<1$.

### צעד 4: אסימפטוטות
אנכיות ב-$x=\\pm 1$. אופקית: $\\lim_{x\\to\\pm\\infty}\\frac{x^2}{x^2-1}=1$ $\\Rightarrow$ $y=1$.

### צעד 5: מונוטוניות
$$f'(x) = \\frac{-2x}{(x^2-1)^2}$$
$f'=0$ ב-$x=0$. עולה ל-$x<0$ (בתחום); יורדת ל-$x>0$.

### צעד 6: קיצון
$f'(0)=0$, $+\\to-$ $\\Rightarrow$ **מקסימום מקומי** ב-$(0,0)$.

### צעד 7: קמירות
$$f''(x) = \\frac{6x^2+2}{(x^2-1)^3}$$
מונה תמיד חיובי. $f''>0$ ל-$|x|>1$; $f''<0$ ל-$|x|<1$.

### צעד 8: פיתול
אין פיתול — $f''$ לא יכולה להחליף סימן בלי לחצות $x=\\pm 1$ שבהם $f$ לא מוגדרת.

**הערת שרטוט:** שני ענפים מעל $y=1$ ל-$|x|>1$, שקע ב-$(0,0)$ בין אסימפטוטות $x=\\pm 1$."""

CHK1_EN = """$$f'(x)=3x^2-12x+9=3(x-1)(x-3)$$
Critical points: $x=1$ and $x=3$.

Sign of $f'$: positive on $(-\\infty,1)$, negative on $(1,3)$, positive on $(3,\\infty)$.

- $x=1$: $f'$ changes $+\\to-$ $\\Rightarrow$ **local maximum**, $f(1)=1-6+9=4$.
- $x=3$: $f'$ changes $-\\to+$ $\\Rightarrow$ **local minimum**, $f(3)=27-54+9=0$.

Verify with $f''(x)=6x-12$: $f''(1)=-6<0$ (max), $f''(3)=6>0$ (min). ✓"""

CHK1_HE = """$$f'(x)=3x^2-12x+9=3(x-1)(x-3)$$
נקודות קריטיות: $x=1$ ו-$x=3$.

סימן $f'$: חיובי ב-$(-\\infty,1)$, שלילי ב-$(1,3)$, חיובי ב-$(3,\\infty)$.

- $x=1$: $f'$ מ-$+\\to-$ $\\Rightarrow$ **מקסימום מקומי**, $f(1)=4$.
- $x=3$: $f'$ מ-$-\\to+$ $\\Rightarrow$ **מינימום מקומי**, $f(3)=0$.

אימות: $f''(1)=-6<0$ (מקסימום), $f''(3)=6>0$ (מינימום). ✓"""

CHK2_EN = """$$f''(x) = e^{-x}(x-2)$$
At $x=1$: $f''(1)=e^{-1}(1-2)=-e^{-1}<0$.

Since $f'(1)=0$ and $f''(1)<0$, the second derivative test confirms a **local maximum** at $x=1$.

Cross-check: $f'(x)=e^{-x}(1-x)>0$ for $x<1$ and $<0$ for $x>1$ — first derivative test agrees. ✓"""

CHK2_HE = """$$f''(x) = e^{-x}(x-2)$$
ב-$x=1$: $f''(1)=e^{-1}(1-2)=-1/e<0$.

מכיוון $f'(1)=0$ ו-$f''(1)<0$, מבחן הנגזרת השנייה מאשר **מקסימום מקומי** ב-$x=1$.

בדיקה צולבת: $f'(x)=e^{-x}(1-x)>0$ ל-$x<1$ ו-$<0$ ל-$x>1$ — מבחן ראשון מסכים. ✓"""

METHOD_EN = """| Step | What to find | How |
|---|---|---|
| 1 Domain | Where defined | Denominators $\\neq 0$; even roots require non-negative argument |
| 2 Roots | $f(x)=0$ | Factor or quadratic formula |
| 3 Sign | $f>0$ or $f<0$ | Sign table with roots & domain gaps |
| 4 Asymptotes | Vertical, horizontal, oblique | Limits at domain gaps and $\\pm\\infty$ |
| 5 Monotonicity | Increasing/decreasing | Compute $f'$, find zeros, sign table |
| 6 Extrema | Local max/min | Where $f'=0$ or undef and $f'$ changes sign |
| 7 Convexity | Concave up/down | Compute $f''$, sign table |
| 8 Inflection | Shape changes | $f''=0$ AND changes sign |

**Exam workflow:** Write separate sign tables for $f$, $f'$, and $f''$. Label every critical value on the $x$-axis before sketching. For rational functions, mark vertical asymptotes as dashed lines and never connect branches across them."""

METHOD_HE = """| צעד | מה למצוא | איך |
|---|---|---|
| 1 תחום | היכן מוגדרת | מכנים $\\neq 0$; שורשים זוגיים $\\geq 0$ |
| 2 שורשים | $f(x)=0$ | פירוק / נוסחת שורשים |
| 3 סימן | $f>0$ או $<0$ | טבלת סימנים |
| 4 אסימפטוטות | אנכית, אופקית, אלכסונית | גבולות בנקודות וב-$\\pm\\infty$ |
| 5 מונוטוניות | עולה/יורדת | $f'$, אפסים, טבלת סימנים |
| 6 קיצונות | מקסימום/מינימום | שינוי סימן $f'$ |
| 7 קמירות | קמור/קעור | $f''$, טבלת סימנים |
| 8 פיתול | שינוי צורה | $f''=0$ ומחליפה סימן |

**זרימת עבודה בבחינה:** כתבו טבלאות סימנים נפרדות ל-$f$, $f'$ ו-$f''$. סמנו כל ערך קריטי על ציר $x$ לפני שרטוט. בפונקציות רציונליות, סמנו אסימפטוטות אנכיות בקו מקווקו ואל תחברו ענפים."""

PITFALL_EN = """1. **Treating $f'(x_0)=0$ as an extremum without a sign change.** A horizontal tangent alone does not guarantee a peak or valley — check both sides of $f'$.

2. **Calling $f''(x_0)=0$ an inflection point.** For $f(x)=x^4$, $f''(0)=0$ but no sign change — it is a local minimum, not an inflection.

3. **Forgetting vertical asymptotes when differentiating.** $f'$ is undefined at vertical asymptotes; exclude those $x$-values from monotonicity intervals.

4. **Assuming a horizontal asymptote $y=L$ means $f$ never crosses $L$.** A function can cross its horizontal asymptote at finite $x$.

5. **Sign errors on $f''$ of rationals.** Powers matter: $(x^2-1)^3$ changes sign at $x=\\pm 1$; $(x^2-1)^2$ does not.

6. **Guessing oblique asymptotes.** Always perform polynomial long division — do not eyeball the slope."""

PITFALL_HE = """1. **סיווג $f'(x_0)=0$ כקיצון ללא שינוי סימן.** משיק אופקי לבדו לא מבטיח פסגה או עמק — בדקו את $f'$ משני הצדדים.

2. **קריאה ל-$f''(x_0)=0$ נקודת פיתול.** עבור $f(x)=x^4$, $f''(0)=0$ אך אין שינוי סימן — זה מינימום מקומי, לא פיתול.

3. **שכחת אסימפטוטות אנכיות בגזירה.** $f'$ לא מוגדרת באסימפטוטות; הוציאו ערכים אלה מקטעי מונוטוניות.

4. **הנחה שאסימפטוטה $y=L$ אומרת ש-$f$ לא חוצה אותה.** פונקציה יכולה לחצות אסימפטוטה אופקית ב-$x$ סופי.

5. **טעויות סימן ב-$f''$ רציונלית.** חזקות חשובות: $(x^2-1)^3$ מחליפה סימן; $(x^2-1)^2$ לא.

6. **ניחוש אסימפטוטות אלכסוניות.** תמיד חלקו פולינומים — אל תנחשו שיפוע."""

WHY_EN = """Complete function investigation is the bridge between pure calculus and every applied topic in the 5-unit track. Optimization problems reuse the same $f'$ and $f''$ machinery; integral applications ask you to sketch regions bounded by functions you must first analyze.

**Recommended next topics:**
- `concept:optimization_problems` — word problems that find max/min after modeling
- `concept:integrals_applications` — volumes and areas built on graphs you sketch here

**Why it matters for exams:** Bagrut graders award partial credit per checklist step. Missing a sign table costs more points than a single algebra slip. University courses expect the same eight-step report with rigorous justification."""

WHY_HE = """חקירת פונקציה מלאה היא הגשר בין חשבון טהור לכל נושא שימושי במסלול 5 יחידות. בעיות קיצון משתמשות באותה מכונת $f'$ ו-$f''$; יישומי אינטגרלים דורשים לשרטט אזורים שמוגבלים בפונקציות שצריך קודם לחקור.

**נושאים מומלצים להמשך:**
- `concept:optimization_problems` — בעיות מילוליות למציאת מקסימום/מינימום
- `concept:integrals_applications` — נפחים ושטחים על גרפים ששרטטתם כאן

**למה זה חשוב לבחינות:** בבגרות נותנים נקודות חלקיות לכל צעד ברשימה. היעדר טבלת סימנים עולה בנקודות יותר מטעות אלגברה בודדת. בקורסים אוניברסיטאיים מצפים לאותו דוח שמונה צעדים עם נימוק מלא."""

BEFORE_EN = """**Every 5pt Bagrut paper has at least one full function investigation worth 25–30 pts.**

**Points allocation (typical):**
- Domain + roots + sign: 4 pts
- Asymptotes: 4 pts
- Monotonicity ($f'$ sign table): 6 pts
- Extrema with values: 4 pts
- Convexity ($f''$ sign table): 4 pts
- Inflection points: 3 pts
- Graph sketch: 5 pts

**Most-tested function types:**
- Rational $P(x)/Q(x)$ (vertical + horizontal asymptotes)
- Exponential $e^{g(x)}$ or $xe^{-x}$
- Logarithmic $\\ln(g(x))$
- Degree-4 polynomials (with inflection)

**Graph sketch tip:** Label ALL key points (intercepts, extrema, inflection), draw asymptotes as dashed lines, show behavior at $\\pm\\infty$."""

BEFORE_HE = """**כל בחינת בגרות 5 יח׳ כוללת חקירה מלאה בשווי 25–30 נקודות.**

**הקצאת נקודות (טיפוסית):**
- תחום + שורשים + סימן: 4 נק׳
- אסימפטוטות: 4 נק׳
- מונוטוניות (טבלת $f'$): 6 נק׳
- קיצונות עם ערכים: 4 נק׳
- קמירות (טבלת $f''$): 4 נק׳
- נקודות פיתול: 3 נק׳
- שרטוט גרף: 5 נק׳

**סוגי פונקציות נפוצים:**
- רציונלית $P/Q$ (עם אסימפטוטות)
- אקספוננציאלית $e^{g(x)}$ או $xe^{-x}$
- לוגריתמית $\\ln(g(x))$
- פולינום ממעלה 4 (עם פיתול)

**טיפ שרטוט:** סמנו כל נקודה מפתח, אסימפטוטות בקו מקווקו, התנהגות ב-$\\pm\\infty$."""

SUMMARY_EN = """**8-step checklist:** Domain $\\to$ Roots $\\to$ Sign $\\to$ Asymptotes $\\to$ Monotonicity ($f'$) $\\to$ Extrema $\\to$ Convexity ($f''$) $\\to$ Inflection.

- **$f'>0$:** increasing; **$f'<0$:** decreasing; **sign change:** extremum.
- **$f''>0$:** concave up; **$f''<0$:** concave down; **sign change:** inflection.
- **Always** write sign tables for $f'$ and $f''$ — graders check them before the sketch.
- Rational functions: vertical (denom $=0$), horizontal, and possibly oblique asymptotes.

**Before submitting:** Re-read your sign tables — one wrong interval sign often cascades into a wrong sketch."""

SUMMARY_HE = """**8 צעדים:** תחום $\\to$ שורשים $\\to$ סימן $\\to$ אסימפטוטות $\\to$ מונוטוניות ($f'$) $\\to$ קיצונות $\\to$ קמירות ($f''$) $\\to$ פיתול.

- **$f'>0$:** עולה; **$f'<0$:** יורדת; **שינוי סימן:** קיצון.
- **$f''>0$:** קמורה; **$f''<0$:** קעורה; **שינוי סימן:** פיתול.
- **תמיד** כתבו טבלאות סימנים ל-$f'$ ו-$f''$ — בוחנים בודקים לפני השרטוט.
- פונקציה רציונלית: אסימפטוטות אנכיות, אופקיות ואולי אלכסוניות.

**לפני הגשה:** קראו שוב טבלאות סימנים — סימן שגוי בקטע אחד גורם לשרטוט שגוי."""

EXPLS = {
    1: fmt_expl(
        "The second derivative test states: if $f'(x_0)=0$ and $f''(x_0)>0$, the graph is concave up at $x_0$, so $f$ has a local minimum there. If $f''(x_0)<0$, it is a local maximum.",
        "At any critical point, compute $f''$ first when it is easy. Positive means 'holds water' (minimum); negative means 'spills water' (maximum). Only use the first derivative test when $f''(x_0)=0$.",
        "Confusing minimum with maximum by flipping the $f''$ sign, or choosing 'inflection point' because $f'(x_0)=0$ without checking $f''$.",
        "On MCQ items about the second derivative test, draw a tiny sketch: concave up $\\Uparrow$ for min, concave down $\\Downarrow$ for max. Saves re-deriving every time.",
        "מבחן הנגזרת השנייה: אם $f'(x_0)=0$ ו-$f''(x_0)>0$, הגרף קמור למעלה ב-$x_0$ — מינימום מקומי. אם $f''(x_0)<0$ — מקסימום מקומי.",
        "בכל נקודה קריטית, חשבו $f''$ תחילה כשזה נוח. חיובי = 'מחזיק מים' (מינימום); שלילי = 'שופך' (מקסימום). השתמשו במבחן ראשון רק כש-$f''(x_0)=0$.",
        "בלבול מינימום עם מקסימום בהפיכת סימן $f''$, או בחירת 'פיתול' כי $f'(x_0)=0$ בלי לבדוק $f''$.",
        "בשאלות רב-ברירה על מבחן שני, שרטטו סקיצה: קמור למעלה למינימום, קעור למטה למקסימום. חוסך גזירה מחדש.",
    ),
    2: fmt_expl(
        "For $f(x)=xe^{-x}$, product rule gives $f'(x)=e^{-x}+x(-e^{-x})=e^{-x}(1-x)$. Since $e^{-x}>0$ always, $f'>0$ exactly when $1-x>0$, i.e., $x<1$.",
        "When $f'$ has a positive exponential factor, ignore it for the sign analysis — only the bracket $(1-x)$ matters. Test $x=0$ ($f'>0$) and $x=2$ ($f'<0$) to confirm.",
        "Answering '$x>1$' (decreasing region) instead of '$x<1$' (increasing), or using '$x>0$' because the root is at $x=0$.",
        "Exponential-times-polynomial functions almost always have $e^{g(x)}>0$. Factor it out immediately — exam time saved on every such question.",
        "עבור $f(x)=xe^{-x}$, כלל המכפלה נותן $f'(x)=e^{-x}(1-x)$. מכיוון $e^{-x}>0$ תמיד, $f'>0$ בדיוק כש-$1-x>0$, כלומר $x<1$.",
        "כש-$f'$ כולל גורם אקספוננציאלי חיובי, התעלמו ממנו בניתוח סימן — רק הסוגר $(1-x)$ קובע. בדקו $x=0$ ($f'>0$) ו-$x=2$ ($f'<0$).",
        "תשובה '$x>1$' (אזור יורד) במקום '$x<1$' (עולה), או '$x>0$' כי השורש ב-$x=0$.",
        "פונקציות אקספוננט כפול פולינום: $e^{g(x)}>0$ כמעט תמיד. פתחו גורם מיד — חוסך זמן בכל שאלה כזו.",
    ),
    3: fmt_expl(
        "Complete investigation of $f(x)=x^3-3x$: domain $\\mathbb{R}$; roots $0,\\pm\\sqrt{3}$; no asymptotes; $f'=3(x-1)(x+1)$ gives max $(-1,2)$ and min $(1,-2)$; $f''=6x$ gives inflection at $(0,0)$.",
        "Follow the eight steps in order without skipping. Polynomial investigations are the template — if you can do this cleanly, rational and exponential versions differ only in steps 1, 4, and derivative algebra.",
        "Stopping after finding extrema without inflection analysis, or forgetting that $f''=0$ at $x=0$ is an inflection because $f''$ changes from negative to positive.",
        "On open-ended Bagrut investigations, write 'Step 5: Monotonicity' headers exactly as graders expect. Partial credit is awarded per labeled step.",
        "חקירה מלאה של $f(x)=x^3-3x$: תחום $\\mathbb{R}$; שורשים $0,\\pm\\sqrt{3}$; אין אסימפטוטות; $f'=3(x-1)(x+1)$ נותן מקס $(-1,2)$ ומין $(1,-2)$; $f''=6x$ נותן פיתול ב-$(0,0)$.",
        "עקבו אחר שמונה הצעדים בסדר בלי לדלג. חקירת פולינום היא התבנית — אם עושים זאת נקי, גרסאות רציונליות ואקספוננציאליות שונות רק בצעדים 1, 4 ואלגברת הנגזרות.",
        "עצירה אחרי קיצונות בלי ניתוח פיתול, או שכחה ש-$f''=0$ ב-$x=0$ הוא פיתול כי $f''$ עוברת משלילי לחיובי.",
        "בחקירות פתוחות בבגרות, כתבו כותרות 'צעד 5: מונוטוניות' כפי שבוחנים מצפים. נקודות חלקיות לכל צעד מתויג.",
    ),
    4: fmt_expl(
        "False. $f''(x_0)=0$ is necessary but not sufficient for an inflection point. For $f(x)=x^4$, $f''(0)=0$ but $f''$ stays non-negative on both sides — no sign change, so $x=0$ is a local minimum, not an inflection.",
        "Inflection requires $f''$ to change sign across $x_0$. Build a mini sign table for $f''$ near the candidate. If both sides have the same sign, it is not an inflection even when $f''(x_0)=0$.",
        "Answering True because 'second derivative zero means inflection' — the most common conceptual error on 5pt exams.",
        "Counterexample $f(x)=x^4$ at $x=0$ is worth memorizing. Examiners use it explicitly in true/false items.",
        "לא נכון. $f''(x_0)=0$ נחוץ אך לא מספיק לפיתול. עבור $f(x)=x^4$, $f''(0)=0$ אך $f''$ נשארת לא שלילית משני הצדדים — אין שינוי סימן, לכן $x=0$ מינימום מקומי, לא פיתול.",
        "פיתול דורש ש-$f''$ תחליף סימן ב-$x_0$. בנו טבלת סימנים קטנה ל-$f''$ ליד המועמד. אם שני הצדדים באותו סימן — אין פיתול גם כש-$f''(x_0)=0$.",
        "תשובה 'נכון' כי 'נגזרת שנייה אפס = פיתול' — הטעות המושגית הנפוצה ביותר ב-5 יח'.",
        "דוגמת נגד $f(x)=x^4$ ב-$x=0$ שווה לשינון. בוחנים משתמשים בה במפורש בשאלות נכון/לא.",
    ),
    5: fmt_expl(
        "Domain $x\\neq\\pm 1$. Vertical asymptotes $x=\\pm 1$; horizontal $y=1$. $f'(x)=-2x/(x^2-1)^2$: zero at $x=0$, sign change $+\\to-$ gives local max $(0,0)$. Denominator squared keeps $f'$ sign analysis simple.",
        "Rational investigations combine domain gaps, asymptotes, and careful interval splitting. Never include $x=\\pm 1$ in monotonicity intervals. The squared denominator in $f'$ means only the numerator $-2x$ sets the sign.",
        "Missing horizontal asymptote $y=1$, or reporting a minimum at $(0,0)$ instead of maximum, or forgetting domain restrictions when listing intervals.",
        "For $x^2/(x^2-1)$, the graph lies below $y=1$ for large $|x|$ but crosses at $x=0$. Label both the asymptote and the local max on your sketch.",
        "תחום $x\\neq\\pm 1$. אסימפטוטות אנכיות $x=\\pm 1$; אופקית $y=1$. $f'(x)=-2x/(x^2-1)^2$: אפס ב-$x=0$, שינוי $+\\to-$ נותן מקס $(0,0)$. מכנה בריבוע מפשט ניתוח סימן.",
        "חקירות רציונליות משלבות רווחים בתחום, אסימפטוטות ופיצול קטעים. אל תכללו $x=\\pm 1$ בקטעי מונוטוניות. המכנה בריבוע ב-$f'$ אומר שרק המונה $-2x$ קובע סימן.",
        "החמצת אסימפטוטה $y=1$, דיווח מינימום במקום מקסימום ב-$(0,0)$, או שכחת הגבלות תחום ברשימת קטעים.",
        "ב-$x^2/(x^2-1)$, הגרף מתחת ל-$y=1$ ל-$|x|$ גדול אך חוצה ב-$x=0$. סמנו גם אסימפטוטה וגם מקסימום מקומי.",
    ),
    6: fmt_expl(
        "The denominator $x^2-4=(x-2)(x+2)$ must not vanish, so $x\\neq\\pm 2$. Domain: all reals except $-2$ and $2$, written $\\mathbb{R}\\setminus\\{-2,2\\}$.",
        "Domain is always step 1. Factor denominators to expose vertical asymptote locations immediately — those same values become gaps in every later sign table.",
        "Writing $x\\neq 4$ from $x^2-4=0$, or forgetting that both $+2$ and $-2$ are excluded.",
        "State domain in set notation on Bagrut papers. Graders deduct for '$x\\neq 2$' when both roots of $x^2-4$ matter.",
        "המכנה $x^2-4=(x-2)(x+2)$ לא מתאפס, לכן $x\\neq\\pm 2$. תחום: כל הממשיים מלבד $-2$ ו-$2$, $\\mathbb{R}\\setminus\\{-2,2\\}$.",
        "תחום תמיד צעד 1. פרקו מכנים לחשיפת אסימפטוטות אנכיות — אותם ערכים הופכים לרווחים בכל טבלת סימנים בהמשך.",
        "כתיבה $x\\neq 4$ מ-$x^2-4=0$, או שכחה שגם $+2$ וגם $-2$ מוחרגים.",
        "נסחו תחום בסימון קבוצות בבגרות. מורידים נקודות על '$x\\neq 2$' כששני שורשי $x^2-4$ רלוונטיים. רשמו גם את האסימפטוטות $x=\\pm 2$ כבר בשלב התחום.",
    ),
    7: fmt_expl(
        "$f'(x)=3x^2-3=3(x-1)(x+1)$. Critical points $x=\\pm 1$. $f''(x)=6x$: $f''(-1)=-6<0$ gives local max $(-1,2)$; $f''(1)=6>0$ gives local min $(1,-2)$.",
        "For cubics, factor $f'$ when possible, then apply the second derivative test at each critical point. Cross-check with first derivative sign change: $+\\to-$ at $-1$, $-\\to+$ at $1$.",
        "Reporting only $x$-coordinates without $f$-values, or classifying both points as maxima because $f'=0$ at both.",
        "Always state extrema as coordinate pairs $(x, f(x))$ on Bagrut — '$x=-1$ is a max' alone loses the value point.",
        "$f'(x)=3x^2-3=3(x-1)(x+1)$. נקודות קריטיות $x=\\pm 1$. $f''(x)=6x$: $f''(-1)=-6<0$ נותן מקס $(-1,2)$; $f''(1)=6>0$ נותן מין $(1,-2)$.",
        "במעוקביות, פרקו $f'$ כשאפשר, והפעילו מבחן שני בכל קריטית. אמתו בשינוי סימן $f'$: $+\\to-$ ב-$-1$, $-\\to+$ ב-$1$.",
        "דיווח רק על $x$ בלי ערכי $f$, או סיווג שתי הנקודות כמקסימום כי $f'=0$ בשתיהן.",
        "תמיד ציינו קיצונים כזוגות $(x, f(x))$ בבגרות — '$x=-1$ מקסימום' לבד מאבד נקודת ערך.",
    ),
    8: fmt_expl(
        "$\\lim_{x\\to\\infty}\\frac{3x+1}{x-2}=\\lim\\frac{3+1/x}{1-2/x}=3$. Degrees equal, so horizontal asymptote is $y=3$ (ratio of leading coefficients). Same limit as $x\\to-\\infty$.",
        "For rational functions where numerator and denominator have the same degree, divide top and bottom by the highest power of $x$, or read the leading-coefficient ratio directly.",
        "Using $y=3x$ (confusing oblique with horizontal), or evaluating only at $x\\to+\\infty$ and missing that both directions give $y=3$.",
        "Quick rule: deg top = deg bottom $\\Rightarrow$ horizontal at coefficient ratio. deg top = deg bottom + 1 $\\Rightarrow$ oblique. Write this on your formula sheet.",
        "$\\lim_{x\\to\\infty}\\frac{3x+1}{x-2}=\\lim\\frac{3+1/x}{1-2/x}=3$. מעלות שוות, אסימפטוטה אופקית $y=3$ (יחס מקדמים). אותו גבול כ-$x\\to-\\infty$.",
        "בפונקציה רציונלית שמעלות שוות, חלקו במעלה הגבוהה של $x$, או קראו ישירות יחס מקדמים מובילים.",
        "שימוש ב-$y=3x$ (בלבול אלכסונית עם אופקית), או חישוב רק ל-$x\\to+\\infty$.",
        "כלל מהיר: מעלה מונה = מעלה מכנה $\\Rightarrow$ אופקית ביחס מקדמים. מעלה מונה = מעלה מכנה+1 $\\Rightarrow$ אלכסונית. רשמו בדף נוסחאות ובדקו גם $x\\to-\\infty$.",
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
            if "6x^2" in body or "6x²" in body:
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
