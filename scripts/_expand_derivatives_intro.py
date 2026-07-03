#!/usr/bin/env python3
"""Expand derivatives_intro.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/derivatives_intro.json"


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he):
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


SECTION_PATCHES = {
    "intro": {
        "body_en_md": """Every time you ask *how fast is something changing right now?* you are asking for a derivative. Average rate of change over an interval uses a secant line; the derivative is what that rate becomes when the interval shrinks to a single instant.

**Where derivatives appear in real problems:**
- **Physics:** velocity $v(t)=x'(t)$ and acceleration $a(t)=v'(t)$ connect motion to calculus directly.
- **Economics:** marginal cost and marginal revenue are derivatives of cost and revenue functions.
- **Engineering:** heat flow, electrical current, and signal slopes in control systems all use $f'(x)$.
- **Exams (Bagrut 5-unit / Calc 1):** function investigation — monotonicity, extrema, concavity, tangent lines — is entirely derivative-driven.

The derivative is the central concept of differential calculus. Integrals, differential equations, and optimization all assume you understand the limit definition and its geometric meaning as the slope of the tangent line.""",
        "body_he_md": """בכל פעם שאתם שואלים *כמה מהר משתנה משהו עכשיו?* אתם שואלים על נגזרת. קצב שינוי ממוצע על קטע משתמש בקו סקנטה; הנגזרת היא מה שקצב זה הופך כשהקטע מתכווץ לרגע בודד.

**איפה נגזרות מופיעות בבעיות אמיתיות:**
- **פיזיקה:** מהירות $v(t)=x'(t)$ ותאוצה $a(t)=v'(t)$ מחברות תנועה לחשבון.
- **כלכלה:** עלות שולית והכנסה שולית הן נגזרות של פונקציות עלות והכנסה.
- **הנדסה:** זרימת חום, זרם חשמלי ושיפועי אותות במערכות בקרה משתמשים ב-$f'(x)$.
- **בחינות (בגרות 5 יחידות / חדו״א 1):** חקירת פונקציה — מונוטוניות, קיצון, קעירות, קווי משיק — כולה מבוססת נגזרות.

הנגזרת היא המושג המרכזי בחשבון דיפרנציאלי. אינטגרלים, משוואות דיפרנציאליות ואופטימיזציה מניחים הבנה של הגדרת הגבול ומשמעותה הגיאומטרית כשיפוע המשיק.""",
    },
    "definition": {
        "body_en_md": """Let $f$ be defined on an open interval containing $a$. The **derivative of $f$ at $a$** is
$$f'(a) = \\lim_{h \\to 0} \\frac{f(a+h)-f(a)}{h}$$
provided this limit exists. If it does, $f$ is **differentiable** at $a$.

**Equivalent form (using $x \\to a$):**
$$f'(a) = \\lim_{x \\to a} \\frac{f(x)-f(a)}{x-a}$$

**Geometric meaning:** The difference quotient $\\dfrac{f(a+h)-f(a)}{h}$ is the slope of the **secant line** through $(a,f(a))$ and $(a+h,f(a+h))$. As $h\\to 0$, the secant approaches the **tangent line** at $a$, whose slope is $f'(a)$.

**Physical meaning:** If $f(t)$ is position, the difference quotient is average velocity over a short interval; the derivative is **instantaneous velocity** at time $a$.

**Notation (all equivalent):** $f'(x)$, $\\dfrac{dy}{dx}$, $\\dot{f}$ (physics), $D_x f$, $\\dfrac{df}{dx}$.

**Existence:** The limit must be the same whether $h\\to 0^+$ or $h\\to 0^-$. Different left- and right-hand limits mean the derivative does not exist — the classic example is $|x|$ at $0$.""",
        "body_he_md": """תהי $f$ מוגדרת בסביבה פתוחה של $a$. **הנגזרת של $f$ ב-$a$** היא
$$f'(a) = \\lim_{h \\to 0} \\frac{f(a+h)-f(a)}{h}$$
בתנאי שהגבול קיים. אם קיים, $f$ נקראת **גזירה** ב-$a$.

**צורה שקולה:**
$$f'(a) = \\lim_{x \\to a} \\frac{f(x)-f(a)}{x-a}$$

**משמעות גיאומטרית:** מנת ההפרש $\\dfrac{f(a+h)-f(a)}{h}$ היא שיפוע **קו הסקנטה** דרך $(a,f(a))$ ו-$(a+h,f(a+h))$. כאשר $h\\to 0$, הסקנטה מתקרבת ל**קו המשיק** ב-$a$, שיפועו $f'(a)$.

**משמעות פיזיקלית:** אם $f(t)$ הוא מיקום, מנת ההפרש היא מהירות ממוצעת על קטע קצר; הנגזרת היא **מהירות רגעית** בזמן $a$.

**סימונים (שווים):** $f'(x)$, $\\dfrac{dy}{dx}$, $\\dot{f}$ (פיזיקה), $D_x f$, $\\dfrac{df}{dx}$.

**קיום:** הגבול חייב להיות זהה בין $h\\to 0^+$ ל-$h\\to 0^-$. גבולות חד-צדדיים שונים פירושם שהנגזרת אינה קיימת — $|x|$ ב-$0$ היא הדוגמה הקלאסית.""",
    },
    "theory": {
        "body_en_md": """**Differentiability implies continuity:** If $f$ is differentiable at $a$, then $f$ is continuous at $a$. Proof sketch: $\\lim_{x\\to a}[f(x)-f(a)]=\\lim_{x\\to a}\\frac{f(x)-f(a)}{x-a}\\cdot(x-a)=f'(a)\\cdot 0=0$. The converse is **false** — $|x|$ is continuous at $0$ but not differentiable there because left- and right-hand slopes differ.

**The tangent line equation:** Once you know $f'(a)$, the tangent line at $(a, f(a))$ is
$$y = f(a) + f'(a)(x-a).$$
This is point-slope form: slope $f'(a)$ through the point on the curve.

**Sign of $f'$ and function behavior:**
- $f'(x) > 0$ on an interval $\\Rightarrow$ $f$ is **increasing** there.
- $f'(x) < 0$ on an interval $\\Rightarrow$ $f$ is **decreasing** there.
- $f'(a) = 0$ $\\Rightarrow$ $a$ is a **critical point** (possible local extremum).

**When is a function NOT differentiable?**
- **Corners** (e.g. $|x|$ at $0$): one-sided secant slopes disagree.
- **Cusps:** slope blows up to $\\pm\\infty$.
- **Vertical tangents:** the limit of the difference quotient is infinite.
- **Discontinuities:** if $f$ is not continuous at $a$, it cannot be differentiable there.

**Estimating derivatives:** On a graph, the derivative at a point is the slope of the tangent you would draw by eye — steeper means larger $|f'(a)|$.""",
        "body_he_md": """**גזירות גוררת רציפות:** אם $f$ גזירה ב-$a$, אז $f$ רציפה ב-$a$. רעיון ההוכחה: $\\lim_{x\\to a}[f(x)-f(a)]=f'(a)\\cdot 0=0$. ההפך **אינו נכון** — $|x|$ רציפה ב-$0$ אך לא גזירה שם כי שיפועי הסקנטה החד-צדדיים שונים.

**משוואת המשיק:** כאשר $f'(a)$ ידועה, קו המשיק ב-$(a, f(a))$ הוא
$$y = f(a) + f'(a)(x-a).$$
זו צורת נקודה-שיפוע: שיפוע $f'(a)$ דרך הנקודה על העקומה.

**סימן $f'$ והתנהגות הפונקציה:**
- $f'(x) > 0$ בקטע $\\Rightarrow$ $f$ **עולה** שם.
- $f'(x) < 0$ בקטע $\\Rightarrow$ $f$ **יורדת** שם.
- $f'(a) = 0$ $\\Rightarrow$ $a$ **נקודה קריטית** (אפשר קיצון מקומי).

**מתי פונקציה אינה גזירה?**
- **פינות** (למשל $|x|$ ב-$0$): שיפועי סקנטה חד-צדדיים שונים.
- **קאספים:** השיפוע שואג ל-$\\pm\\infty$.
- **משיקים אנכיים:** גבול מנת ההפרש אינסופי.
- **אי-רציפויות:** אם $f$ לא רציפה ב-$a$, היא לא גזירה שם.

**אומדן נגזרות:** בגרף, הנגזרת בנקודה היא שיפוע המשיק שמשרטטים בעין — שיפוע תלול יותר $\\Rightarrow$ $|f'(a)|$ גדול יותר.""",
    },
}

WORKED_EXAMPLES = [
    {
        "body_en_md": """**Given:** $f(x) = x^2$. Find $f'(x)$ using the limit definition.

### Move 1: Write the difference quotient.
$$\\frac{f(x+h)-f(x)}{h} = \\frac{(x+h)^2 - x^2}{h}$$

### Move 2: Expand the numerator — cancel $x^2$.
$$(x+h)^2 - x^2 = x^2 + 2xh + h^2 - x^2 = 2xh + h^2$$

### Move 3: Factor out $h$ and cancel ($h \\ne 0$ inside the limit).
$$\\frac{2xh + h^2}{h} = \\frac{h(2x+h)}{h} = 2x + h$$

### Move 4: Take the limit as $h \\to 0$.
$$f'(x) = \\lim_{h \\to 0}(2x + h) = 2x$$

**Answer:** $\\boxed{f'(x) = 2x}$ ✓

**Check at $x=3$:** $f'(3)=6$, so the tangent to $y=x^2$ at $(3,9)$ has slope $6$. This matches the power-rule preview you will use later — but here every algebra step is visible.

**Why this example matters:** Polynomial derivatives from the definition always follow the same four-step template. Once you can do $x^2$, the same logic extends to $x^3$, $x^2-3x$, and any polynomial on a Bagrut or Calc 1 exam. Examiners award partial credit for correct difference-quotient setup even if later algebra slips. Label each move clearly on the exam page so the grader can follow your reasoning.""",
        "body_he_md": """**נתון:** $f(x) = x^2$. מצאו את $f'(x)$ מהגדרת הגבול.

### צעד 1: כתבו את מנת ההפרש.
$$\\frac{f(x+h)-f(x)}{h} = \\frac{(x+h)^2 - x^2}{h}$$

### צעד 2: פתחו את המונה — צמצמו $x^2$.
$$(x+h)^2 - x^2 = x^2 + 2xh + h^2 - x^2 = 2xh + h^2$$

### צעד 3: פצלו $h$ וצמצמו ($h \\ne 0$ בתוך הגבול).
$$\\frac{2xh + h^2}{h} = \\frac{h(2x+h)}{h} = 2x + h$$

### צעד 4: חשבו את הגבול כאשר $h \\to 0$.
$$f'(x) = \\lim_{h \\to 0}(2x + h) = 2x$$

**תשובה:** $\\boxed{f'(x) = 2x}$ ✓

**בדיקה ב-$x=3$:** $f'(3)=6$, כלומר המשיק ל-$y=x^2$ ב-$(3,9)$ בשיפוע 6. זה תואם את כלל החזקה שתלמדו בהמשך — אך כאן כל שלב האלגברה גלוי.

**למה הדוגמה חשובה:** נגזרות פולינומים מהגדרה תמיד עוקבות אחרי אותו תבנית של ארבעה צעדים. ברגע שיודעים $x^2$, אותה לוגיקה מתרחבת ל-$x^3$, $x^2-3x$ ולכל פולינום בבגרות או בחדו״א 1. בוחנים נותנים נקודות חלקיות על הצבה נכונה של מנת ההפרש. סמנו כל צעד בבירור בעמוד הבחינה — זה מקל על הבודק לעקוב אחרי החשיבה שלכם. אל תדלגו על שלב הפישוט.""",
    },
    {
        "body_en_md": """**Given:** $f(x) = \\sqrt{x}$, $x > 0$. Find $f'(x)$ from the definition. Radical functions produce $0/0$ until you rationalize — this is a standard exam pattern.

### Move 1: Set up the difference quotient — this gives $0/0$.
$$\\frac{\\sqrt{x+h}-\\sqrt{x}}{h}$$

### Move 2: Rationalize by multiplying top and bottom by the conjugate.
$$\\frac{\\sqrt{x+h}-\\sqrt{x}}{h} \\cdot \\frac{\\sqrt{x+h}+\\sqrt{x}}{\\sqrt{x+h}+\\sqrt{x}} = \\frac{(x+h)-x}{h(\\sqrt{x+h}+\\sqrt{x})} = \\frac{h}{h(\\sqrt{x+h}+\\sqrt{x})}$$

### Move 3: Cancel $h$ ($h \\ne 0$).
$$= \\frac{1}{\\sqrt{x+h}+\\sqrt{x}}$$

### Move 4: Take the limit — the denominator approaches $2\\sqrt{x}$.
$$f'(x) = \\lim_{h\\to 0}\\frac{1}{\\sqrt{x+h}+\\sqrt{x}} = \\frac{1}{2\\sqrt{x}}$$

**Answer:** $\\boxed{f'(x) = \\dfrac{1}{2\\sqrt{x}}}$ ✓

**Key technique:** Rationalizing the conjugate removes the indeterminate $0/0$ form. This same trick appears whenever a square root sits in the numerator of a difference quotient.

**Domain note:** We require $x>0$ so that $\\sqrt{x}$ and $\\sqrt{x+h}$ are real for small $h$. The answer $f'(x)=\\frac{1}{2\\sqrt{x}}$ is valid on the same domain. Compare with the power rule on $x^{1/2}$, which gives the identical formula once you have proven it from this definition. This rationalization technique is reusable for any square-root function on an exam. Never substitute $h=0$ before simplifying the quotient. Write the conjugate explicitly in your exam work.""",
        "body_he_md": """**נתון:** $f(x) = \\sqrt{x}$, $x > 0$. מצאו $f'(x)$ מהגדרה. פונקציות שורש יוצרות $0/0$ עד רציונליזציה — זה דפוס בחינה סטנדרטי.

### צעד 1: הציבו את מנת ההפרש — מתקבל $0/0$.
$$\\frac{\\sqrt{x+h}-\\sqrt{x}}{h}$$

### צעד 2: רציונליזציה — הכפלה בצמוד למונה ולמכנה.
$$\\frac{\\sqrt{x+h}-\\sqrt{x}}{h} \\cdot \\frac{\\sqrt{x+h}+\\sqrt{x}}{\\sqrt{x+h}+\\sqrt{x}} = \\frac{h}{h(\\sqrt{x+h}+\\sqrt{x})}$$

### צעד 3: צמצמו $h$ ($h \\ne 0$).
$$= \\frac{1}{\\sqrt{x+h}+\\sqrt{x}}$$

### צעד 4: חשבו את הגבול — המכנה שואג ל-$2\\sqrt{x}$.
$$f'(x) = \\lim_{h\\to 0}\\frac{1}{\\sqrt{x+h}+\\sqrt{x}} = \\frac{1}{2\\sqrt{x}}$$

**תשובה:** $\\boxed{f'(x) = \\dfrac{1}{2\\sqrt{x}}}$ ✓

**טכניקה מרכזית:** רציונליזציה בצמוד מסירה את צורת $0/0$ הבלתי-קבועה. אותו טריק חוזר בכל פעם ששורש מופיע במונה של מנת הפרש.

**הערת תחום:** דורשים $x>0$ כדי ש-$\\sqrt{x}$ ו-$\\sqrt{x+h}$ יהיו ממשיים. התשובה $f'(x)=\\frac{1}{2\\sqrt{x}}$ תקפה באותו תחום. השוו לכלל החזקה על $x^{1/2}$, שנותן את אותה נוסחה לאחר הוכחה מההגדרה כאן. טכניקת הרציונליזציה חוזרת בכל פונקציית שורש בבחינה. לעולם אל תציבו $h=0$ לפני פישוט מנת ההפרש. כתבו את הצמוד במפורש בעבודת הבחינה.""",
    },
    {
        "body_en_md": """**Given:** $f(x) = \\sin x$. Prove $f'(x) = \\cos x$ using the limit definition and the fundamental trigonometric limits.

**Preliminary limits (required knowledge):**
$$\\lim_{h\\to 0}\\frac{\\sin h}{h} = 1, \\qquad \\lim_{h\\to 0}\\frac{\\cos h - 1}{h} = 0$$

### Move 1: Write the difference quotient.
$$\\frac{\\sin(x+h)-\\sin x}{h}$$

### Move 2: Apply the angle-addition identity $\\sin(x+h)=\\sin x\\cos h + \\cos x\\sin h$.
$$= \\frac{\\sin x\\cos h + \\cos x\\sin h - \\sin x}{h}$$

### Move 3: Group terms to expose the two standard limits.
$$= \\sin x\\cdot\\frac{\\cos h-1}{h} + \\cos x\\cdot\\frac{\\sin h}{h}$$

### Move 4: Evaluate each limit separately.
$$f'(x) = \\sin x \\cdot 0 + \\cos x \\cdot 1 = \\cos x$$

**Answer:** $\\boxed{(\\sin x)' = \\cos x}$ ✓

**Takeaway:** Trigonometric derivatives from definition always reduce to $\\frac{\\sin h}{h}$ and $\\frac{\\cos h-1}{h}$. Memorize those two limits — they are non-negotiable on Bagrut 5-unit and Calc 1 exams.

**Connection:** The identity $\\cos h - 1 = -2\\sin^2(h/2)$ explains why $\\frac{\\cos h-1}{h}\\to 0$ — the numerator is order $h^2$, so dividing by $h$ still gives zero. The same proof template works for $\\cos x$, yielding $-\\sin x$. On exams, write both preliminary limits at the top before starting the algebra steps.""",
        "body_he_md": """**נתון:** $f(x) = \\sin x$. הוכיחו $f'(x) = \\cos x$ מהגדרת הגבול ומגבולות טריגונומטריים.

**גבולות קדומים (ידע נדרש):**
$$\\lim_{h\\to 0}\\frac{\\sin h}{h} = 1, \\qquad \\lim_{h\\to 0}\\frac{\\cos h - 1}{h} = 0$$

### צעד 1: כתבו את מנת ההפרש.
$$\\frac{\\sin(x+h)-\\sin x}{h}$$

### צעד 2: נוסחת סכום: $\\sin(x+h) = \\sin x\\cos h + \\cos x\\sin h$.
$$= \\frac{\\sin x\\cos h + \\cos x\\sin h - \\sin x}{h}$$

### צעד 3: קיבוץ לחשיפת שני הגבולות הסטנדרטיים.
$$= \\sin x\\cdot\\frac{\\cos h-1}{h} + \\cos x\\cdot\\frac{\\sin h}{h}$$

### צעד 4: חישוב כל גבול בנפרד.
$$f'(x) = \\sin x \\cdot 0 + \\cos x \\cdot 1 = \\cos x$$

**תשובה:** $\\boxed{(\\sin x)' = \\cos x}$ ✓

**מסקנה:** גזירת פונקציות טריגונומטריות מהגדרה תמיד מצמצמת ל-$\\frac{\\sin h}{h}$ ו-$\\frac{\\cos h-1}{h}$. שיננו את שני הגבולות — הם חובה בבגרות 5 יחידות ובחדו״א 1.

**קשר:** הזהות $\\cos h - 1 = -2\\sin^2(h/2)$ מסבירה מדוע $\\frac{\\cos h-1}{h}\\to 0$ — המונה מסדר $h^2$, ולכן חלוקה ב-$h$ עדיין נותנת אפס. אותה תבנית הוכחה עובדת גם עבור $\\cos x$ ונותנת $-\\sin x$. בבחינה, כתבו את שני הגבולות הקדומים בראש הפתרון לפני שלבי האלגברה.""",
    },
]

OTHER_SECTIONS = {
    "pitfall": {
        "body_en_md": """1. **Forgetting the limit.** Writing $f'(x) = \\frac{f(x+h)-f(x)}{h}$ without taking $h\\to 0$ gives a secant slope, not a derivative. The limit is the entire point of the definition.

2. **Canceling $h$ without justification.** It is valid to cancel $h\\ne 0$ inside a limit because you approach $0$ but never substitute $h=0$ into the original $0/0$ form.

3. **Confusing secant with tangent.** The difference quotient is a secant slope over a finite step $h$. Only the limit as $h\\to 0$ produces the tangent slope $f'(a)$.

4. **Wrong tangent line formula.** The tangent at $x=a$ passes through $(a,f(a))$: $y=f(a)+f'(a)(x-a)$. Writing $y=f'(a)x$ ignores the intercept and fails almost every exam check.

5. **Assuming differentiability from continuity.** $f(x)=|x|$ is continuous at $0$ but not differentiable there — left slope $-1$, right slope $+1$. Continuity is necessary but not sufficient for differentiability.""",
        "body_he_md": """1. **שכחת הגבול.** כתיבת $f'(x)=\\frac{f(x+h)-f(x)}{h}$ ללא $h\\to 0$ נותנת שיפוע סקנטה, לא נגזרת. הגבול הוא כל הנקודה בהגדרה.

2. **צמצום $h$ ללא הצדקה.** מותר לצמצם $h\\ne 0$ בתוך גבול כי ניגשים ל-$0$ אך לא מציבים $h=0$ בצורת $0/0$ המקורית.

3. **בלבול סקנטה ומשיק.** מנת ההפרש היא שיפוע סקנטה על צעד סופי $h$. רק הגבול כאשר $h\\to 0$ נותן שיפוע משיק $f'(a)$.

4. **נוסחת משיק שגויה.** המשיק ב-$x=a$ עובר דרך $(a,f(a))$: $y=f(a)+f'(a)(x-a)$. כתיבת $y=f'(a)x$ מתעלמת מהחיתוך ונכשלת כמעט בכל בדיקת בחינה.

5. **הנחת גזירות מרציפות.** $f(x)=|x|$ רציפה ב-$0$ אך לא גזירה — שיפוע שמאלי $-1$, ימני $+1$. רציפות הכרחית אך לא מספיקה לגזירות.""",
    },
    "why_matters": {
        "body_en_md": """The derivative is the gateway from algebra to analysis — it turns static functions into dynamic models of change.

**You will use this to unlock on A Step Forward:**
- `concept:kinematics_1d` **Kinematics in 1D** — instantaneous velocity is $dx/dt$.
- `concept:newton_laws` **Newton's Laws** — $F = m\\, dv/dt$ links force to acceleration.
- `concept:derivatives_rules` **Derivative Rules** — the fast computation layer built on this definition.

**Builds on:**
- `concept:continuity` **Continuity** — differentiability requires continuity at the point.

**Why exams care:** Bagrut 5-unit and university Calc 1 routinely ask for derivatives *from first principles* on polynomial, radical, and rational functions. Examiners deduct marks for skipping the limit step or using rules when the question says \"from the definition.\" Master the definition here and every later technique has a solid foundation.""",
        "body_he_md": """הנגזרת היא השער מאלגברה לניתוח — היא הופכת פונקציות סטטיות למודלים דינמיים של שינוי.

**תשתמשו בזה להתקדם ב-A Step Forward:**
- `concept:kinematics_1d` **קינמטיקה בממד אחד** — מהירות רגעית היא $dx/dt$.
- `concept:newton_laws` **חוקי ניוטון** — $F = m\\, dv/dt$ מקשר כוח לתאוצה.
- `concept:derivatives_rules` **כללי גזירה** — שכבת החישוב המהירה שנשענת על ההגדרה כאן.

**מבוסס על:**
- `concept:continuity` **רציפות** — גזירות דורשת רציפות בנקודה.

**למה בחינות אכפת:** בבגרות 5 יחידות ובחדו״א 1 מבקשים לעיתים קרובות נגזרות *מהגדרה* על פולינומים, שורשים ופונקציות רציונליות. מורידים נקודות על דילוג על שלב הגבול או שימוש בכללים כשהשאלה אומרת \"מהגדרה\". שליטה בהגדרה כאן נותנת בסיס לכל טכניקה מאוחרת.""",
    },
    "before_exam": {
        "body_en_md": """**Notation table:**

| Notation | Meaning |
|----------|---------|
| $f'(x)$ | Lagrange notation |
| $\\dfrac{dy}{dx}$ | Leibniz notation |
| $\\dot{f}$ | Newton / physics notation |
| $D_x f$ | Operator notation |

**Key formula:**
$$f'(a) = \\lim_{h\\to 0}\\frac{f(a+h)-f(a)}{h} = \\lim_{x\\to a}\\frac{f(x)-f(a)}{x-a}$$

**Tangent line at $(a, f(a))$:**
$$y = f(a) + f'(a)(x-a)$$

**Trigonometric limits you must know:**
$$\\lim_{h\\to 0}\\frac{\\sin h}{h}=1, \\qquad \\lim_{h\\to 0}\\frac{\\cos h-1}{h}=0$$

**What examiners look for:**
- Correct setup of the difference quotient before any algebra.
- Simplification that removes $h$ from the denominator before taking the limit.
- Explicit statement $h\\to 0$ — not substitution of $h=0$ into $0/0$.
- Tangent line written through the correct point $(a,f(a))$.""",
        "body_he_md": """**טבלת סימונים:**

| סימון | משמעות |
|-------|--------|
| $f'(x)$ | סימון לגראנז' |
| $\\dfrac{dy}{dx}$ | סימון לייבניץ |
| $\\dot{f}$ | סימון ניוטון / פיזיקה |
| $D_x f$ | סימון אופרטורי |

**נוסחה מרכזית:**
$$f'(a) = \\lim_{h\\to 0}\\frac{f(a+h)-f(a)}{h} = \\lim_{x\\to a}\\frac{f(x)-f(a)}{x-a}$$

**קו משיק ב-$(a, f(a))$:**
$$y = f(a) + f'(a)(x-a)$$

**גבולות טריגונומטריים שיש לזכור:**
$$\\lim_{h\\to 0}\\frac{\\sin h}{h}=1, \\qquad \\lim_{h\\to 0}\\frac{\\cos h-1}{h}=0$$

**מה הבוחנים מחפשים:**
- הצבה נכונה של מנת ההפרש לפני כל אלגברה.
- פישוט שמסיר $h$ מהמכנה לפני חישוב הגבול.
- הצהרה מפורשת $h\\to 0$ — לא הצבה $h=0$ ב-$0/0$.
- משוואת משיק דרך הנקודה הנכונה $(a,f(a))$.""",
    },
    "summary": {
        "body_en_md": """- The derivative $f'(a) = \\lim_{h\\to 0}\\frac{f(a+h)-f(a)}{h}$ is the instantaneous rate of change and the slope of the tangent line at $a$.
- Differentiability implies continuity; the converse is false ($|x|$ at $0$ is the standard counterexample).
- Computing from the definition requires algebraic tools: expanding polynomials, rationalizing radicals, combining fractions, or invoking trigonometric limits.
- Tangent line: $y = f(a) + f'(a)(x-a)$ — always through the point on the curve.
- Use the limit definition when an exam says \"from first principles\"; otherwise differentiation rules (next lesson) are far faster.""",
        "body_he_md": """- הנגזרת $f'(a)=\\lim_{h\\to 0}\\frac{f(a+h)-f(a)}{h}$ היא קצב השינוי הרגעי ושיפוע המשיק ב-$a$.
- גזירות גוררת רציפות; ההפך אינו נכון ($|x|$ ב-$0$ היא דוגמת הנגד הסטנדרטית).
- חישוב מהגדרה דורש כלי אלגברה: פיתוח פולינומים, רציונליזציה, איחוד שברים, או גבולות טריגונומטריים.
- משוואת משיק: $y = f(a) + f'(a)(x-a)$ — תמיד דרך הנקודה על העקומה.
- השתמשו בהגדרת הגבול כשבבחינה כתוב \"מהגדרה\"; אחרת כללי הגזירה (השיעור הבא) מהירים הרבה יותר.""",
    },
    "method_guide": {
        "body_en_md": """| Situation | Use | Reason |
|-----------|-----|--------|
| Asked explicitly to use the definition | Limit definition | Exam instruction — rules forbidden |
| Proving a derivative formula | Limit definition | Rigorous justification required |
| Polynomial, exponential, trig at a point | Differentiation rules (later) | Much faster once proven |
| Absolute value / piecewise at a point | One-sided limit definition | Rules may not apply at corners |
| Composition $f(g(x))$ | Chain rule | Avoid messy nested limits |

**Definition workflow (exam-proof):**
1. Write $\\dfrac{f(x+h)-f(x)}{h}$ (or the $x\\to a$ form).
2. Simplify algebraically until $h$ cancels from numerator and denominator.
3. Take the limit as $h\\to 0$.
4. State the result in standard notation.

**Tangent line summary:**
$$y - f(a) = f'(a)(x-a)$$

**When in doubt:** if the question says \"from first principles\" or \"using the definition\", you MUST use the limit. Otherwise, use the rules.""",
        "body_he_md": """| מצב | שיטה | סיבה |
|-----|------|------|
| נדרש במפורש להשתמש בהגדרה | גבול הגדרה | הוראת בחינה — אסור כללים |
| הוכחת נוסחת נגזרת | גבול הגדרה | דרושה הוכחה פורמלית |
| פולינום / מעריכי / טריגו בנקודה | כללי גזירה (בהמשך) | הרבה יותר מהיר לאחר הוכחה |
| ערך מוחלט / חלקים בנקודה | גבול חד-צדדי | כללים לא חלים בפינות |
| הרכבה $f(g(x))$ | כלל השרשרת | הימנעות מגבולות מקוננים |

**תהליך מהגדרה (עמיד בבחינה):**
1. כתבו $\\dfrac{f(x+h)-f(x)}{h}$.
2. פשטו אלגברית עד ש-$h$ מתבטל.
3. חשבו גבול $h\\to 0$.
4. הציגו בנוסח סטנדרטי.

**משוואת המשיק:**
$$y - f(a) = f'(a)(x-a)$$

**בספק:** אם כתוב \"מהגדרה\" — חייבים גבול. אחרת — כללים.""",
    },
}

CHECKPOINT_PATCHES = [
    {
        "checkpoint_solution_en": """**Step 1:** Expand the cube using the binomial formula:
$$(x+h)^3 = x^3 + 3x^2h + 3xh^2 + h^3$$

**Step 2:** Form the numerator $(x+h)^3 - x^3$ — the $x^3$ terms cancel:
$$3x^2h + 3xh^2 + h^3$$

**Step 3:** Divide by $h$ (valid for $h\\ne 0$ inside the limit):
$$3x^2 + 3xh + h^2$$

**Step 4:** Take the limit as $h\\to 0$ — the terms with $h$ vanish:
$$f'(x) = \\lim_{h\\to 0}(3x^2+3xh+h^2) = 3x^2$$

**Answer:** $f'(x) = 3x^2$ ✓

**Pattern:** For $f(x)=x^n$, the definition always yields $f'(x)=nx^{n-1}$. Here $n=3$ gives $3x^2$, confirming the power rule you will prove once and reuse.""",
        "checkpoint_solution_he": """**שלב 1:** פיתוח הבינום:
$$(x+h)^3 = x^3 + 3x^2h + 3xh^2 + h^3$$

**שלב 2:** מונה $(x+h)^3 - x^3$ — איברי $x^3$ מתבטלים:
$$3x^2h + 3xh^2 + h^3$$

**שלב 3:** חלוקה ב-$h$ (מותר ל-$h\\ne 0$ בתוך הגבול):
$$3x^2 + 3xh + h^2$$

**שלב 4:** גבול $h\\to 0$ — איברים עם $h$ נעלמים:
$$f'(x) = 3x^2$$

**תשובה:** $f'(x) = 3x^2$ ✓

**דפוס:** עבור $f(x)=x^n$, ההגדרה תמיד נותנת $f'(x)=nx^{n-1}$. כאן $n=3$ נותן $3x^2$, מאשר את כלל החזקה.""",
    },
    {
        "checkpoint_solution_en": """**Step 1:** Write the difference quotient and combine into one fraction:
$$\\frac{f(x+h)-f(x)}{h} = \\frac{\\frac{1}{x+h}-\\frac{1}{x}}{h} = \\frac{x-(x+h)}{hx(x+h)} = \\frac{-h}{hx(x+h)}$$

**Step 2:** Cancel $h$ ($h\\ne 0$):
$$= \\frac{-1}{x(x+h)}$$

**Step 3:** Take the limit as $h\\to 0$ — the denominator becomes $x^2$:
$$f'(x) = \\lim_{h\\to 0}\\frac{-1}{x(x+h)} = -\\frac{1}{x^2}$$

**Answer:** $f'(x) = -\\dfrac{1}{x^2}$ ✓

**Check:** This matches the power rule on $x^{-1}$: derivative is $-1\\cdot x^{-2}=-1/x^2$. Domain requires $x\\ne 0$.""",
        "checkpoint_solution_he": """**שלב 1:** מנת ההפרש ואיחוד לשבר אחד:
$$\\frac{\\frac{1}{x+h}-\\frac{1}{x}}{h} = \\frac{-h}{hx(x+h)}$$

**שלב 2:** צמצום $h$ ($h\\ne 0$):
$$= \\frac{-1}{x(x+h)}$$

**שלב 3:** גבול $h\\to 0$ — המכנה שואג ל-$x^2$:
$$f'(x) = -\\frac{1}{x^2}$$

**תשובה:** $f'(x) = -\\dfrac{1}{x^2}$ ✓

**בדיקה:** תואם כלל החזקה על $x^{-1}$: נגזרת $-x^{-2}=-1/x^2$. תחום: $x\\ne 0$.""",
    },
]

QUESTION_EXPLS = [
    fmt_expl(
        "For a linear function $f(x)=5x+3$, the difference quotient simplifies immediately: $\\frac{5(x+h)+3-(5x+3)}{h}=\\frac{5h}{h}=5$. No $h$ remains, so the limit as $h\\to 0$ is still $5$. This shows that lines have constant slope — the derivative of a linear function is its slope coefficient.",
        "Start from the definition every time, even when the answer seems obvious. Expand $f(x+h)$, subtract $f(x)$, and cancel $h$ before taking the limit.",
        "Stopping at $\\frac{5h}{h}$ without stating $\\lim_{h\\to 0}5=5$, or claiming the derivative depends on $x$ when the function is linear.",
        "Bagrut 5-unit \"from definition\" questions on lines are quick marks — write the full difference quotient setup even for easy functions to show the examiner you know the process.",
        "עבור $f(x)=5x+3$, מנת ההפרש מתפשטת מיד: $\\frac{5h}{h}=5$. לא נשאר $h$, ולכן הגבול הוא $5$. זה מראה שלקווים ישרים יש שיפוע קבוע — נגזרת של פונקציה לינארית היא מקדם השיפוע.",
        "התחילו מההגדרה בכל פעם, גם כשהתשובה נראית ברורה. פתחו $f(x+h)$, חסרו $f(x)$, וצמצמו $h$ לפני הגבול.",
        "עצירה ב-$\\frac{5h}{h}$ בלי לכתוב $\\lim_{h\\to 0}5=5$, או טענה שהנגזרת תלויה ב-$x$ כשהפונקציה לינארית.",
        "שאלות \"מהגדרה\" על קווים בבגרות 5 יחידות — נקודות מהירות. כתבו את מנת ההפרש המלאה גם בפונקציות קלות.",
    ),
    fmt_expl(
        "Expand $(x+h)^2-3(x+h)$ and subtract $x^2-3x$. The $x^2$ terms cancel, leaving $2xh+h^2-3h$. Dividing by $h$ gives $2x+h-3$, and the limit as $h\\to 0$ yields $f'(x)=2x-3$. This is the power rule plus the constant multiple rule, verified from scratch.",
        "Treat each term separately: differentiate $x^2$ to get $2x$ and $-3x$ to get $-3$. The definition should produce the same result — use that as a self-check.",
        "Forgetting the $-3h$ term when expanding $-3(x+h)$, or leaving $h$ in the final answer instead of taking the limit.",
        "Polynomial derivatives from definition always follow the same pattern: expand, cancel $x^2$ (or highest power), factor $h$, limit. Practice until the four steps are automatic.",
        "פתיחת $(x+h)^2-3(x+h)$ וחיסור $x^2-3x$ מבטלת את $x^2$ ומשאירה $2xh+h^2-3h$. חלוקה ב-$h$ נותנת $2x+h-3$, והגבול $f'(x)=2x-3$.",
        "טפלו בכל איבר בנפרד: נגזרת $x^2$ היא $2x$ ושל $-3x$ היא $-3$. ההגדרה צריכה לתת אותה תוצאה — השתמשו בזה לבדיקה.",
        "שכחת איבר $-3h$ בפתיחת $-3(x+h)$, או השארת $h$ בתשובה הסופית.",
        "נגזרות פולינומים מהגדרה תמיד באותו דפוס: פיתוח, ביטול חזקה עליונה, פיצול $h$, גבול. תרגלו עד שהארבעה צעדים אוטומטיים.",
    ),
    fmt_expl(
        "First find $f'(x)=2x$ from the definition (or recall from this lesson). At $x=1$: $f(1)=1^2=1$ and $f'(1)=2(1)=2$. The tangent line through $(1,1)$ with slope $2$ is $y-1=2(x-1)$, which simplifies to $y=2x-1$.",
        "Tangent line problems require two ingredients: the point $(a,f(a))$ on the curve and the slope $f'(a)$. Never use only the derivative value without the point.",
        "Writing $y=2x$ (passes through origin, not through $(1,1)$) or using $f'(x)=2x$ as the tangent equation instead of point-slope form.",
        "On exams, always write $y-f(a)=f'(a)(x-a)$ first, then simplify. Examiners often give partial credit for correct setup even if algebra slips later.",
        "קודם $f'(x)=2x$. ב-$x=1$: $f(1)=1$ ו-$f'(1)=2$. המשיק דרך $(1,1)$ בשיפוע $2$ הוא $y-1=2(x-1)$, כלומר $y=2x-1$.",
        "בעיות משיק דורשות שני מרכיבים: הנקודה $(a,f(a))$ על העקומה והשיפוע $f'(a)$. לעולם אל תשתמשו רק בערך הנגזרת בלי הנקודה.",
        "כתיבת $y=2x$ (עובר במקור, לא ב-$(1,1)$) או שימוש ב-$f'(x)=2x$ כמשוואת המשיק.",
        "בבחינות, כתבו תמיד $y-f(a)=f'(a)(x-a)$ קודם, ואז פשטו. בוחנים נותנים לעיתים נקודות חלקיות על הצבה נכונה.",
    ),
    fmt_expl(
        "At $x=0$, the left-hand difference quotient approaches $-1$ (slope of $-x$ for $x<0$) and the right-hand approaches $+1$ (slope of $+x$ for $x>0$). Since these one-sided limits differ, the two-sided limit does not exist, so $f'(0)$ is undefined. For $x\\ne 0$, $|x|$ is smooth and $f'(x)=\\pm 1$ depending on sign.",
        "For piecewise or absolute-value functions, compute left-hand and right-hand limits of the difference quotient separately. Different values mean no derivative at that point.",
        "Saying $|x|$ is not differentiable \"because of the corner\" without computing the one-sided limits, or claiming non-differentiability everywhere instead of only at $x=0$.",
        "Bagrut questions on $|x|$ often ask you to sketch $f$ and $f'$ on the same axes — remember $f'$ is undefined at $0$ but equals $+1$ for $x>0$ and $-1$ for $x<0$.",
        "ב-$x=0$, גבול שמאלי של מנת ההפרש שואג ל-$-1$ וימני ל-$+1$. כיוון שהם שונים, הגבול הדו-צדדי אינו קיים ו-$f'(0)$ לא מוגדר. ל-$x\\ne 0$, $|x|$ חלקה ו-$f'(x)=\\pm 1$.",
        "בפונקציות חלקיות או עם ערך מוחלט, חשבו גבולות חד-צדדיים של מנת ההפרש בנפרד. ערכים שונים = אין נגזרת.",
        "אמירה ש-$|x|$ לא גזירה \"בגלל הפינה\" בלי חישוב גבולות חד-צדדיים, או טענה על אי-גזירות בכל מקום במקום רק ב-$0$.",
        "שאלות בגרות על $|x|$ מבקשות לעיתים לשרטט $f$ ו-$f'$ — זכרו: $f'$ לא מוגדר ב-$0$, שווה $+1$ ל-$x>0$ ו-$-1$ ל-$x<0$.",
    ),
    fmt_expl(
        "Let $g(x)=cf(x)$. The difference quotient is $\\frac{c f(x+h)-cf(x)}{h}=c\\cdot\\frac{f(x+h)-f(x)}{h}$. Since the limit of a constant times a function equals the constant times the limit, $\\lim_{h\\to 0}c\\cdot\\frac{f(x+h)-f(x)}{h}=c\\cdot f'(x)$. This is the constant multiple rule, proved rigorously from the definition.",
        "Factor the constant $c$ outside the limit. The definition applies to $f$; multiplying by $c$ just scales every difference quotient by $c$.",
        "Dropping the constant $c$ during simplification, or trying to use the product rule (which is not yet proven) instead of factoring.",
        "Proof questions on exams expect you to cite $\\lim(cf)=c\\lim f$. Write that limit law explicitly — one line of justification earns full marks.",
        "עבור $g(x)=cf(x)$, מנת ההפרש היא $c\\cdot\\frac{f(x+h)-f(x)}{h}$. מחוק הגבול: $\\lim c\\cdot(\\cdots)=c\\cdot f'(x)$. זה כלל כפל בקבוע, מוכח מההגדרה. ההוכחה לא דורשת שום כלל גזירה נוסף — רק פירוק גורם וחוק גבול בסיסי.",
        "הוציאו את הקבוע $c$ מחוץ לגבול. ההגדרה חלה על $f$; הכפלה ב-$c$ מכפילה כל מנת הפרש באותו מספר.",
        "השמטת $c$ בפישוט, או ניסיון להשתמש בכלל המכפלה (עדיין לא מוכח) במקום פירוק.",
        "שאלות הוכחה מצפות לציטוט $\\lim(cf)=c\\lim f$. כתבו את חוק הגבול במפורש — שורה אחת מצדיקה את כל הנקודות. זהו אחד משלושת כללי הליניאריות שתוכיחו מהגדרה.",
    ),
    fmt_expl(
        "Using the $x\\to a$ form: $f(2)=2^3-2(2)=8-4=4$. The difference quotient $\\frac{x^3-2x-4}{x-2}$ factors as $\\frac{(x-2)(x^2+2x+2)}{x-2}=x^2+2x+2$ for $x\\ne 2$. As $x\\to 2$, this gives $4+4+2=10$, so $f'(2)=10$.",
        "When finding $f'(a)$ at a specific point, the $x\\to a$ form often avoids expanding $(x+h)^3$. Factor the numerator — if $(x-a)$ is a factor, cancel it before the limit.",
        "Substituting $x=2$ into the unfactored fraction (gives $0/0$), or forgetting to compute $f(a)$ first when using the $x\\to a$ form.",
        "For $f'(a)$ at a specific number, try polynomial division or factoring before expanding the full cube — it saves time under exam pressure.",
        "בצורת $x\\to a$: $f(2)=4$. מנת ההפרש $\\frac{x^3-2x-4}{x-2}$ מתפרקת ל-$x^2+2x+2$, וכאשר $x\\to 2$ מתקבל $10$, כלומר $f'(2)=10$.",
        "כשמחפשים $f'(a)$ בנקודה ספציפית, צורת $x\\to a$ לעיתים חוסכת פיתוח $(x+h)^3$. פצלו את המונה — אם $(x-a)$ גורם, צמצמו לפני הגבול.",
        "הצבה $x=2$ בשבר לפני פירוק ($0/0$), או שכחת חישוב $f(a)$ בצורת $x\\to a$.",
        "עבור $f'(a)$ במספר ספציפי, נסו חלוקת פולינומים או פירוק לפני פיתוח מלא — חוסך זמן בלחץ בחינה.",
    ),
    fmt_expl(
        "Combine the fractions: $\\frac{\\frac{1}{x+h+1}-\\frac{1}{x+1}}{h}=\\frac{(x+1)-(x+h+1)}{h(x+h+1)(x+1)}=\\frac{-h}{h(x+h+1)(x+1)}$. Cancel $h$ to get $\\frac{-1}{(x+h+1)(x+1)}$, and as $h\\to 0$ the limit is $-\\frac{1}{(x+1)^2}$.",
        "For rational functions, always combine into a single fraction before canceling $h$. The numerator should become a polynomial times $h$ — if it does not, recheck your algebra.",
        "Sign errors when subtracting fractions (getting $+h$ instead of $-h$ in the numerator), or forgetting to square the denominator in the final answer.",
        "The pattern $\\frac{1}{g(x+h)}-\\frac{1}{g(x)}$ always produces a factor of $h$ in the numerator after combining — look for it before taking the limit.",
        "איחוד שברים: $\\frac{\\frac{1}{x+h+1}-\\frac{1}{x+1}}{h}=\\frac{-h}{h(x+h+1)(x+1)}$. צמצום $h$ נותן $\\frac{-1}{(x+h+1)(x+1)}$, והגבול $-\\frac{1}{(x+1)^2}$. זה אותו דפוס כמו $\\frac{1}{x}$ בדוגמת התרגול — רק עם $x+1$ במקום $x$.",
        "בפונקציות רציונליות, אחדו לשבר אחד לפני צמצום $h$. המונה צריך להפוך לפולינום כפול $h$ — אם לא, בדקו שוב את סימן המונה.",
        "שגיאות סימן בחיסור שברים, או שכחת בריבוע המכנה בתשובה הסופית.",
        "הדפוס $\\frac{1}{g(x+h)}-\\frac{1}{g(x)}$ תמיד מייצר גורם $h$ במונה — חפשו אותו לפני הגבול. בבחינה, כתבו את שלב איחוד השברים במפורש.",
    ),
    fmt_expl(
        "Rationalize the numerator: multiply by $\\frac{\\sqrt{2(x+h)+1}+\\sqrt{2x+1}}{\\sqrt{2(x+h)+1}+\\sqrt{2x+1}}$ to get $\\frac{2(x+h+1)-2x-1}{h(\\sqrt{2x+2h+1}+\\sqrt{2x+1})}=\\frac{2h}{h(\\sqrt{2x+2h+1}+\\sqrt{2x+1})}$. Cancel $h$ and take the limit: $\\frac{2}{2\\sqrt{2x+1}}=\\frac{1}{\\sqrt{2x+1}}$.",
        "When the function is $\\sqrt{ax+b}$, rationalize using the conjugate — the $a$ in front of $x$ becomes a factor in the numerator after simplification. Track that factor carefully.",
        "Forgetting the chain-rule effect: the inner coefficient $2$ from $\\sqrt{2x+1}$ must appear in the numerator before canceling $h$, or the final answer will be off by a factor of 2.",
        "Compare with $\\sqrt{x}$ from Worked Example 2: the extra factor of 2 from the inner function $2x+1$ is exactly what the chain rule will formalize in the next lesson.",
        "רציונליזציה: הכפלה בצמוד נותנת $\\frac{2h}{h(\\sqrt{2x+2h+1}+\\sqrt{2x+1})}$. צמצום $h$ וגבול: $\\frac{2}{2\\sqrt{2x+1}}=\\frac{1}{\\sqrt{2x+1}}$. המקדם $2$ במונה מגיע מפיתוח $(2x+2h+1)-(2x+1)=2h$.",
        "כשהפונקציה $\\sqrt{ax+b}$, רציונליזציה בצמוד — המקדם $a$ לפני $x$ הופך לגורם במונה. עקבו אחריו בקפידה לפני צמצום $h$.",
        "שכחת השפעת כלל השרשרת: המקדם $2$ מ-$\\sqrt{2x+1}$ חייב להופיע במונה לפני צמצום $h$, אחרת התשובה תהיה שגויה בגורם $2$.",
        "השוו ל-$\\sqrt{x}$ מדוגמה 2: הגורם $2$ הנוסף מ-$2x+1$ הוא בדיוק מה שכלל השרשרת ינסח בשיעור הבא. בבחינה, רשמו את שלב הרציונליזציה במלואו.",
    ),
]


def word_count(text):
    import re
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in SECTION_PATCHES:
            sec.update(SECTION_PATCHES[kind])
        if kind in OTHER_SECTIONS:
            sec.update(OTHER_SECTIONS[kind])

    we_idx = 0
    cp_idx = 0
    for sec in data["sections"]:
        if sec.get("kind") == "worked_example" and we_idx < len(WORKED_EXAMPLES):
            sec.update(WORKED_EXAMPLES[we_idx])
            we_idx += 1
        if sec.get("kind") == "checkpoint" and cp_idx < len(CHECKPOINT_PATCHES):
            sec.update(CHECKPOINT_PATCHES[cp_idx])
            cp_idx += 1

    for i, q in enumerate(data["questions"]):
        en, he = QUESTION_EXPLS[i]
        q["explanation_en"] = en
        q["explanation_he"] = he

    # Clean template filler from exercise solutions e5-e11
    for ex in data["sections"][-3]["exercises"] if False else []:
        pass
    for sec in data["sections"]:
        if sec.get("kind") != "exercise_set":
            continue
        for ex in sec.get("exercises", []):
            for key in ("solution_en", "solution_he"):
                if ex.get(key) and "Identify the rule from this lesson" in ex[key]:
                    ex[key] = ex[key].replace(
                        "**Solution path:** Identify the rule from this lesson, then apply it.\n\n", ""
                    ).replace(
                        "**דרך פתרון:** זהו את הכלל מהשיעור, ואז יישמו.\n\n", ""
                    ).replace(
                        "\n\n**Check:** Re-substitute or verify units and signs before moving on.", ""
                    ).replace(
                        "\n\n**בדיקה:** החליפו בחזרה או וודאו יחידות וסימן.", ""
                    )

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

    issues = []
    from importlib.util import spec_from_loader, module_from_spec
    # validate word counts inline
    MIN = {
        "intro": (110, 90), "definition": (130, 110), "theory": (160, 130),
        "worked_example": (130, 110), "pitfall": (100, 85), "why_matters": (90, 75),
        "method_guide": (100, 85), "before_exam": (90, 75), "summary": (70, 60),
    }
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN:
            en, he = word_count(sec.get("body_en_md", "")), word_count(sec.get("body_he_md", ""))
            mn, mh = MIN[kind]
            if en < mn:
                issues.append(f"{kind} EN: {en} < {mn}")
            if he < mh:
                issues.append(f"{kind} HE: {he} < {mh}")
    for q in data["questions"]:
        en, he = word_count(q["explanation_en"]), word_count(q["explanation_he"])
        if en < 80 or en > 150:
            issues.append(f"Q{q['ord']} EN: {en}")
        if he < 80 or he > 150:
            issues.append(f"Q{q['ord']} HE: {he}")

    if issues:
        print("ISSUES:")
        for i in issues:
            print(" ", i)
        raise SystemExit(1)

    print("Depth gates OK")
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit(r.returncode)
    print("seed-lessons --dry-run OK")


if __name__ == "__main__":
    main()
