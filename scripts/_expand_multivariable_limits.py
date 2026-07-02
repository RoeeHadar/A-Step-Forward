#!/usr/bin/env python3
"""Expand multivariable_limits.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/multivariable_limits.json"

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


INTRO_EN = """In single-variable calculus, $\\lim_{x\\to a}f(x)$ requires the value to be the same whether $x$ approaches $a$ from the left or right — just **two paths**. For functions $f(x,y)$, the point $(x,y)$ can approach $(a,b)$ along **infinitely many curves**: horizontal and vertical lines, diagonals $y=mx$, parabolas $y=kx^2$, spirals, and more. The limit exists only if the same value is obtained along **every possible path**.

This asymmetry shapes how you work: **disproving** a limit is often easier than **proving** one. Find two paths with different limiting values and you are done — the limit does not exist (DNE). Proving existence requires the full $\\varepsilon$-$\\delta$ definition, the squeeze theorem, or a polar/substitution argument that removes path dependence.

Multivariable limits gate everything that follows in Calc III: partial derivatives, directional derivatives, differentiability, and chain rules all assume you can reason about approach paths. A function can look well-behaved along every axis yet fail to have a limit because a curved path reveals hidden oscillation or blow-up. This lesson builds on `concept:limits_intro` and unlocks `concept:partial_derivatives`."""

INTRO_HE = """בחדו\"א חד-משתנה, גבול $\\lim_{x\\to a}f(x)$ דורש ערך זהה בגישה משמאל ומימין — **שני נתיבים** בלבד. עבור $f(x,y)$, הנקודה $(x,y)$ יכולה לגשת ל-$(a,b)$ לאורך **אינסוף עקומות**: קווים אופקיים ואנכיים, אלכסונים $y=mx$, פרבולות $y=kx^2$, ספירלות ועוד. הגבול קיים רק אם **אותו ערך** מתקבל לאורך **כל נתיב אפשרי**.

א-סימטריה הזו קובעת את אופן העבודה: **שלילת** קיום גבול לעתים קלה יותר מ**הוכחת** קיום. מצאו שני נתיבים עם ערכי גבול שונים — והגבול **לא קיים** (DNE). הוכחת קיום דורשת הגדרת $\\varepsilon$-$\\delta$, משפט הסנדוויץ', או הצבה בקואורדינטות קוטביות שמסירה תלות בנתיב.

גבולות ממשתנים רבים פותחים את כל חשבון III: נגזרות חלקיות, נגזרות כיווניות, גזירות וכלל השרשרת — כולם מניחים יכולת לנתח נתיבי גישה. פונקציה יכולה להיראות \"טובה\" על כל ציר ועדיין להיכשל בגבול כי נתיב מעוקל חושף תנודה או התפוצצות נסתרת. שיעור זה מבוסס על `concept:limits_intro` ופותח את `concept:partial_derivatives`."""

DEF_EN = """**Definition ($\\varepsilon$-$\\delta$):** $\\lim_{(x,y)\\to(a,b)} f(x,y) = L$ if:
$$\\forall\\varepsilon>0\\;\\exists\\delta>0:\\;0<\\sqrt{(x-a)^2+(y-b)^2}<\\delta\\Rightarrow|f(x,y)-L|<\\varepsilon.$$

The quantity $\\sqrt{(x-a)^2+(y-b)^2}$ is the **Euclidean distance** from $(x,y)$ to $(a,b)$. Unlike the single-variable case, you cannot test only two sides — you must control $f$ in the entire deleted disk around $(a,b)$.

**Limit Does Not Exist (DNE):** If there exist two paths $C_1$ and $C_2$ both approaching $(a,b)$ along which $f$ tends to **different values** (or one blows up), the limit does not exist. One counterexample path is enough to disprove existence.

**Continuity:** $f$ is continuous at $(a,b)$ if $\\lim_{(x,y)\\to(a,b)}f(x,y)=f(a,b)$. Polynomials are continuous everywhere; rational functions are continuous wherever the denominator is nonzero.

**Path notation:** A path can be written as $(x(t),y(t))\\to(a,b)$ as $t\\to 0$, or implicitly as $y=g(x)$ with $x\\to a$. Both describe the same idea: approach $(a,b)$ along a curve, not just along axes."""

DEF_HE = """**הגדרה ($\\varepsilon$-$\\delta$):** $\\lim_{(x,y)\\to(a,b)} f(x,y) = L$ אם:
$$\\forall\\varepsilon>0\\;\\exists\\delta>0:\\;0<\\sqrt{(x-a)^2+(y-b)^2}<\\delta\\Rightarrow|f(x,y)-L|<\\varepsilon.$$

הכמות $\\sqrt{(x-a)^2+(y-b)^2}$ היא **מרחק אוקלידי** מ-$(x,y)$ ל-$(a,b)$. בניגוד לחד-משתנה, אי אפשר לבדוק רק שני צדדים — צריך לשלוט ב-$f$ בכל הדיסקה החסרה סביב $(a,b)$.

**גבול לא קיים (DNE):** אם קיימים שני נתיבים $C_1,C_2$ המתכנסים ל-$(a,b)$ לאורכם $f$ שואפת ל**ערכים שונים** (או אחד מתפוצץ), הגבול לא קיים. נתיב נגדי אחד מספיק לשלילה.

**רציפות:** $f$ רציפה ב-$(a,b)$ אם $\\lim_{(x,y)\\to(a,b)}f(x,y)=f(a,b)$. פולינומים רציפים בכל מקום; פונקציות רציונליות רציפות היכן שהמכנה $\\neq 0$.

**סימון נתיב:** נתיב $(x(t),y(t))\\to(a,b)$ כש-$t\\to 0$, או $y=g(x)$ עם $x\\to a$ — שני תיאורים של אותה רעיון: גישה ל-$(a,b)$ לאורך עקומה, לא רק על צירים."""

THEORY_EN = """**Strategy 1 — Disprove (path test):** To show the limit DNE, find two paths giving different limits:
- Try axes first: $y=0$ and $x=0$.
- Try lines through the origin: $y=mx$. If the limit depends on slope $m$, DNE.
- Try parabolas: $y=kx^2$ or $x=ky^2$ — often catches cases where all lines agree.

**Strategy 2 — Prove (squeeze theorem):** To show $\\lim f=L$, bound $|f(x,y)-L|\\leq g(r)$ where $r=\\sqrt{x^2+y^2}\\to 0$. If $g(r)\\to 0$, then $f\\to L$. The key inequality $x^2/(x^2+y^2)\\leq 1$ appears in nearly every squeeze proof at the origin.

**Strategy 3 — Polar coordinates:** Substitute $x=r\\cos\\theta$, $y=r\\sin\\theta$. As $(x,y)\\to(0,0)$, require $r\\to 0^+$. If the simplified expression tends to a value **independent of $\\theta$**, the limit exists. If it still depends on $\\theta$ after $r\\to 0$, DNE — polar coordinates detected path dependence in one step.

**Strategy 4 — $\\varepsilon$-$\\delta$ (rigorous proof):** After conjecturing $L$ via squeeze or polar, choose $\\delta=\\varepsilon$ (or similar) using $|f-L|\\leq r$ or $|f-L|\\leq |y|$. This is the university-level capstone for existence proofs.

**When paths agree but limit may still DNE:** Agreement along finitely many paths proves nothing. Only a uniform bound (squeeze, polar independence, or $\\varepsilon$-$\\delta$) establishes existence."""

THEORY_HE = """**אסטרטגיה 1 — שלילה (מבחן נתיבים):** להראות DNE, מצאו שני נתיבים עם גבולות שונים:
- נסו צירים: $y=0$ ו-$x=0$.
- ישרים דרך המקור: $y=mx$. אם הגבול תלוי ב-$m$ — DNE.
- פרבולות: $y=kx^2$ או $x=ky^2$ — לעיתים תופסות מה שהישרים מפספסים.

**אסטרטגיה 2 — הוכחה (squeeze):** להראות $\\lim f=L$, חסמו $|f(x,y)-L|\\leq g(r)$ כאשר $r=\\sqrt{x^2+y^2}\\to 0$. אם $g(r)\\to 0$, אז $f\\to L$. האי-שוויון $x^2/(x^2+y^2)\\leq 1$ מופיע כמעט בכל הוכחת squeeze במקור.

**אסטרטגיה 3 — קואורדינטות קוטביות:** $x=r\\cos\\theta$, $y=r\\sin\\theta$. כש-$(x,y)\\to(0,0)$, דרשו $r\\to 0^+$. אם הביטוי המפושט שואף לערך **בלתי-תלוי ב-$\\theta$**, הגבול קיים. אם עדיין תלוי ב-$\\theta$ אחרי $r\\to 0$ — DNE.

**אסטרטגיה 4 — $\\varepsilon$-$\\delta$ (הוכחה קפדנית):** אחרי ניחוש $L$ ב-squeeze או קוטביות, בחרו $\\delta=\\varepsilon$ (או דומה) בעזרת $|f-L|\\leq r$ או $|f-L|\\leq |y|$.

**כשהנתיבים מסכימים אך הגבול עדיין עלול לא להתקיים:** הסכמה על מספר סופי של נתיבים לא מוכיחה כלום. רק חסם אחיד (squeeze, אי-תלות ב-$\\theta$, או $\\varepsilon$-$\\delta$) מבסס קיום."""

WE1_EN = """**Problem:** Show $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2-y^2}{x^2+y^2}$ does not exist.

The path test is the fastest tool when the numerator and denominator share the same degree.

### Move 1 — Path $y=0$ (along the $x$-axis)
Set $y=0$ and let $x\\to 0$:
$$f(x,0)=\\frac{x^2-0}{x^2+0}=\\frac{x^2}{x^2}=1\\quad(x\\neq 0).$$
So along this path the limit is $1$.

### Move 2 — Path $x=0$ (along the $y$-axis)
Set $x=0$ and let $y\\to 0$:
$$f(0,y)=\\frac{0-y^2}{0+y^2}=\\frac{-y^2}{y^2}=-1\\quad(y\\neq 0).$$
So along this path the limit is $-1$.

### Move 3 — Conclude DNE
Since $1\\neq -1$, two different paths yield different limiting values. Therefore **the limit does not exist (DNE)**.

**Why axes first:** For rational functions symmetric in $x^2$ and $y^2$, the coordinate axes often split the numerator into opposite signs immediately — no algebra beyond substitution.

**Exam link:** You only need **one pair** of disagreeing paths. State both paths, both limits, and the inequality explicitly."""

WE1_HE = """**בעיה:** הראו ש-$\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2-y^2}{x^2+y^2}$ לא קיים.

מבחן הנתיבים הוא הכלי המהיר כשהמונה והמכנה מאותו דרגה.

### צעד 1 — נתיב $y=0$ (לאורך ציר $x$)
נקבע $y=0$ ו-$x\\to 0$:
$$f(x,0)=\\frac{x^2}{x^2}=1\\quad(x\\neq 0).$$
לאורך נתיב זה הגבול הוא $1$.

### צעד 2 — נתיב $x=0$ (לאורך ציר $y$)
נקבע $x=0$ ו-$y\\to 0$:
$$f(0,y)=\\frac{-y^2}{y^2}=-1\\quad(y\\neq 0).$$
לאורך נתיב זה הגבול הוא $-1$.

### צעד 3 — מסקנה DNE
מכיוון ש-$1\\neq -1$, שני נתיבים שונים נותנים ערכי גבול שונים. לכן **הגבול לא קיים (DNE)**.

**למה צירים קודם:** לפונקציות רציונליות סימטריות ב-$x^2$ ו-$y^2$, צירי הקואורדינטות לעיתים מפצלים את המונה לסימנים מנוגדים מיד.

**קשר לבחינה:** מספיק **זוג אחד** של נתיבים שלא מסכימים. ציינו את שני הנתיבים, שני הגבולות, ואת אי-השוויון במפורש."""

WE2_EN = """**Problem:** Compute $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2y}{x^2+y^2}$.

Path tests suggest $0$, but agreement on finitely many paths is not a proof — use squeeze.

### Move 1 — Quick path checks (motivation only)
- $y=0$: $0/(x^2)=0$.
- $y=x$: $x^3/(2x^2)=x/2\\to 0$.
- $y=x^2$: $x^4/(x^2+x^4)=x^2/(1+x^2)\\to 0$.
All tested paths give $0$, suggesting $L=0$.

### Move 2 — Build the squeeze bound
Since $x^2\\leq x^2+y^2$, we have $\\dfrac{x^2}{x^2+y^2}\\leq 1$. Therefore:
$$\\left|\\frac{x^2y}{x^2+y^2}\\right|=\\frac{x^2}{x^2+y^2}|y|\\leq |y|.$$

### Move 3 — Apply squeeze as $(x,y)\\to(0,0)$
As $(x,y)\\to(0,0)$, $|y|\\to 0$. So:
$$0\\leq\\left|\\frac{x^2y}{x^2+y^2}\\right|\\leq |y|\\to 0.$$

**Conclusion:** $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2y}{x^2+y^2}=0$.

**Template:** For expressions with $x^2y/(x^2+y^2)$-type structure, the factor $x^2/(x^2+y^2)\\leq 1$ converts the problem to showing $|y|\\to 0$ or $|x|\\to 0$.

**Sanity check:** The numerator is degree 3 while the denominator is degree 2 — one extra power of $r$ should vanish at the origin, consistent with limit $0$."""

WE2_HE = """**בעיה:** חשבו $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2y}{x^2+y^2}$.

בדיקות נתיבים מציעות $0$, אך הסכמה על מספר סופי של נתיבים אינה הוכחה — השתמשו ב-squeeze.

### צעד 1 — בדיקות נתיב מהירות (מוטיבציה בלבד)
- $y=0$: $0$.
- $y=x$: $x/2\\to 0$.
- $y=x^2$: $x^2/(1+x^2)\\to 0$.
כל הנתיבים שנבדקו נותנים $0$, מציעים $L=0$.

### צעד 2 — בניית חסם squeeze
מכיוון ש-$x^2\\leq x^2+y^2$, מתקיים $\\dfrac{x^2}{x^2+y^2}\\leq 1$. לכן:
$$\\left|\\frac{x^2y}{x^2+y^2}\\right|\\leq |y|.$$

### צעד 3 — יישום squeeze כש-$(x,y)\\to(0,0)$
כש-$(x,y)\\to(0,0)$, $|y|\\to 0$. אז:
$$0\\leq\\left|\\frac{x^2y}{x^2+y^2}\\right|\\leq |y|\\to 0.$$

**מסקנה:** $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2y}{x^2+y^2}=0$.

**תבנית:** לביטויים מסוג $x^2y/(x^2+y^2)$, הגורם $x^2/(x^2+y^2)\\leq 1$ ממיר את הבעיה להראות $|y|\\to 0$.

**בדיקה:** המונה בדרגה 3 והמכנה בדרגה 2 — כוח $r$ נוסף אחד אמור להיעלם במקור, עקבי עם גבול $0$."""

WE3_EN = """**Problem:** Use polar coordinates to show $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2-y^2}{x^2+y^2}$ does not exist.

This is the same function as Worked Example 1, now analyzed via polar form — revealing $\\theta$-dependence instantly.

### Move 1 — Substitute polar coordinates
Let $x=r\\cos\\theta$, $y=r\\sin\\theta$ with $r\\to 0^+$:
$$f=\\frac{r^2\\cos^2\\theta-r^2\\sin^2\\theta}{r^2\\cos^2\\theta+r^2\\sin^2\\theta}=\\frac{r^2(\\cos^2\\theta-\\sin^2\\theta)}{r^2}=\\cos^2\\theta-\\sin^2\\theta=\\cos(2\\theta).$$

### Move 2 — Observe $r$-cancellation and $\\theta$-dependence
The $r^2$ factors cancel completely. As $r\\to 0$, the value of $f$ **does not approach a single number** — it equals $\\cos(2\\theta)$, which depends on the approach direction $\\theta$.

### Move 3 — Exhibit two directions with different values
- Along $\\theta=0$ (positive $x$-axis): $f\\to\\cos 0=1$.
- Along $\\theta=\\pi/2$ (positive $y$-axis): $f\\to\\cos\\pi=-1$.

Since $1\\neq -1$, **the limit DNE**.

### Move 4 — Geometric interpretation
Level sets of $f$ are constant-$\\theta$ rays from the origin. The function is literally $\\cos(2\\theta)$ on every circle — it jumps as you rotate, so no single $L$ works for all approach directions.

**Key lesson:** When polar substitution eliminates $r$ entirely, check $\\theta$-dependence immediately. If $f=f(\\theta)$ with $r$ gone, DNE unless $f$ is constant in $\\theta$."""

WE3_HE = """**בעיה:** השתמשו בקואורדינטות קוטביות להראות ש-$\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^2-y^2}{x^2+y^2}$ לא קיים.

אותה פונקציה כמו דוגמה 1, כעת בניתוח קוטבי — חושף תלות ב-$\\theta$ מיד.

### צעד 1 — הצבה בקואורדינטות קוטביות
נקבע $x=r\\cos\\theta$, $y=r\\sin\\theta$ עם $r\\to 0^+$:
$$f=\\frac{r^2(\\cos^2\\theta-\\sin^2\\theta)}{r^2}=\\cos^2\\theta-\\sin^2\\theta=\\cos(2\\theta).$$

### צעד 2 — ביטול $r$ ותלות ב-$\\theta$
גורמי $r^2$ מתבטלים לחלוטין. כש-$r\\to 0$, ערך $f$ **לא שואף למספר יחיד** — הוא שווה ל-$\\cos(2\\theta)$, שתלוי בכיוון הגישה $\\theta$.

### צעד 3 — שני כיוונים עם ערכים שונים
- לאורך $\\theta=0$ (ציר $x$ חיובי): $f\\to\\cos 0=1$.
- לאורך $\\theta=\\pi/2$ (ציר $y$ חיובי): $f\\to\\cos\\pi=-1$.

מכיוון ש-$1\\neq -1$, **הגבול DNE**.

### צעד 4 — פרשנות גיאומטרית
קבוצות הגובה של $f$ הן קרני $\\theta$ קבוע מהמקור. הפונקציה היא $\\cos(2\\theta)$ על כל מעגל — היא קופצת ברotation, ולכן אין $L$ יחיד לכל כיווני הגישה.

**מסקנה:** כשהצבה קוטבית מבטלת את $r$ לגמרי, בדקו תלות ב-$\\theta$ מיד. אם $f=f(\\theta)$ ו-$r$ נעלם — DNE אלא אם $f$ קבוע ב-$\\theta$."""

CHK1_EN = """Show $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{xy}{x^2+y^2}$ does not exist by testing $y=0$ and $y=x$.

**Step 1 — Path $y=0$:** Set $y=0$:
$$\\frac{xy}{x^2+y^2}=\\frac{0}{x^2}=0\\quad(x\\neq 0).$$
Limit along this path $=0$.

**Step 2 — Path $y=x$:** Substitute $y=x$:
$$\\frac{x\\cdot x}{x^2+x^2}=\\frac{x^2}{2x^2}=\\frac{1}{2}\\quad(x\\neq 0).$$
Limit along this path $=\\tfrac{1}{2}$.

**Step 3 — Conclude:** $0\\neq\\tfrac{1}{2}$, so the limits along these two paths disagree. **The limit DNE.**

**Check:** The diagonal path $y=x$ is the standard second test after axes — it catches many $xy$-type numerators that vanish on both axes individually."""

CHK1_HE = """הראו ש-$\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{xy}{x^2+y^2}$ לא קיים על ידי בדיקת $y=0$ ו-$y=x$.

**שלב 1 — נתיב $y=0$:** נקבע $y=0$:
$$\\frac{xy}{x^2+y^2}=0\\quad(x\\neq 0).$$
גבול לאורך נתיב זה $=0$.

**שלב 2 — נתיב $y=x$:** נציב $y=x$:
$$\\frac{x^2}{2x^2}=\\frac{1}{2}\\quad(x\\neq 0).$$
גבול לאורך נתיב זה $=\\tfrac{1}{2}$.

**שלב 3 — מסקנה:** $0\\neq\\tfrac{1}{2}$, הגבולות לאורך שני הנתיבים שונים. **הגבול DNE.**

**בדיקה:** הנתיב $y=x$ הוא הבדיקה הסטנדרטית השנייה אחרי הצירים — תופס מונים מסוג $xy$ שמתאפסים על כל ציר בנפרד."""

CHK2_EN = """Use the squeeze theorem to show $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^3}{x^2+y^2}=0$.

**Step 1 — Bound the fraction:** Since $x^2\\leq x^2+y^2$:
$$\\left|\\frac{x^3}{x^2+y^2}\\right|=|x|\\cdot\\frac{x^2}{x^2+y^2}\\leq |x|.$$

**Step 2 — Apply squeeze:** As $(x,y)\\to(0,0)$, $|x|\\to 0$. Therefore:
$$0\\leq\\left|\\frac{x^3}{x^2+y^2}\\right|\\leq |x|\\to 0.$$

**Step 3 — Conclude:** By the squeeze theorem, $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^3}{x^2+y^2}=0$.

**Alternative:** Polar form gives $f=r\\cos^3\\theta$, so $|f|\\leq r\\to 0$ — same conclusion, different route.

**Check:** Degree of numerator exceeds denominator by one power of $r$ — expect limit $0$ at the origin."""

CHK2_HE = """השתמשו במשפט הסנדוויץ' להראות ש-$\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^3}{x^2+y^2}=0$.

**שלב 1 — חסימת השבר:** מכיוון ש-$x^2\\leq x^2+y^2$:
$$\\left|\\frac{x^3}{x^2+y^2}\\right|\\leq |x|.$$

**שלב 2 — יישום squeeze:** כש-$(x,y)\\to(0,0)$, $|x|\\to 0$. לכן:
$$0\\leq\\left|\\frac{x^3}{x^2+y^2}\\right|\\leq |x|\\to 0.$$

**שלב 3 — מסקנה:** לפי משפט הסנדוויץ', $\\displaystyle\\lim_{(x,y)\\to(0,0)}\\frac{x^3}{x^2+y^2}=0$.

**חלופה:** בקוטביות $f=r\\cos^3\\theta$, $|f|\\leq r\\to 0$ — אותה מסקנה.

**בדיקה:** דרגת המונה גבוהה מהמכנה בכוח $r$ אחד — מצפים לגבול $0$ במקור."""

METHOD_EN = """| Goal | Strategy | When to use |
|---|---|---|
| Show **DNE** | Path test | Try $y=0$, $x=0$, $y=mx$, $y=kx^2$ |
| Show **limit = L** | Squeeze | Bound $|f-L|\\leq g(r)\\to 0$ |
| Show **limit = L** | Polar coords | $x=r\\cos\\theta$, $y=r\\sin\\theta$; check $\\theta$ independence |
| **Rigorous proof** | $\\varepsilon$-$\\delta$ | After conjecturing $L$ via squeeze |

**DNE path selection (in order):**
1. Axes ($y=0$, $x=0$).
2. Lines $y=mx$ — vary slope $m$.
3. Parabolas $y=kx^2$ or $x=ky^2$.
4. Polar — if $f=f(\\theta)$ after $r\\to 0$, DNE unless constant.

**Squeeze template:**
$$|f(x,y)-L|\\leq M\\cdot r^k\\to 0\\quad(r=\\sqrt{x^2+y^2},\\;k>0).$$

**Workflow:** Read the stem — "show DNE" → path test first; "compute" or "show = 0" → try squeeze or polar."""

METHOD_HE = """| מטרה | אסטרטגיה | מתי |
|---|---|---|
| הראה **DNE** | מבחן נתיבים | $y=0$, $x=0$, $y=mx$, $y=kx^2$ |
| הראה **גבול = L** | Squeeze | $|f-L|\\leq g(r)\\to 0$ |
| הראה **גבול = L** | קואורדינטות קוטביות | בדוק אי-תלות ב-$\\theta$ |
| **הוכחה קפדנית** | $\\varepsilon$-$\\delta$ | אחרי ניחוש $L$ |

**בחירת נתיבים (בסדר):**
1. צירים ($y=0$, $x=0$).
2. ישרים $y=mx$ — שנה $m$.
3. פרבולות $y=kx^2$.
4. קוטביות — אם $f=f(\\theta)$ אחרי $r\\to 0$, DNE.

**תבנית squeeze:**
$$|f(x,y)-L|\\leq M\\cdot r^k\\to 0.$$

**תהליך:** \"הראה DNE\" → נתיבים קודם; \"חשב\" או \"= 0\" → squeeze או קוטביות."""

PITFALL_EN = """1. **Checking a few paths and concluding the limit exists.** Finitely many agreeing paths prove nothing — only squeeze, polar independence, or $\\varepsilon$-$\\delta$ establishes existence.

2. **Forgetting parabolic paths.** When all lines $y=mx$ give the same value, try $y=kx^2$ before claiming the limit exists — many classic DNE examples hide behind parabolas.

3. **Misreading polar results.** If $f=\\cos(2\\theta)$ after substitution, the limit DNE even though $r\\to 0$. Independence from $\\theta$ is required, not just vanishing $r$.

4. **Weak squeeze bounds.** $|f|\\leq 1$ does not help unless the bound also $\\to 0$. You need $|f-L|\\leq g(r)$ with $g(r)\\to 0$.

5. **Confusing separate continuity with joint continuity.** A function continuous in $x$ for each fixed $y$ (and vice versa) can still fail to have a limit at $(0,0)$.

**Fix pattern:** After path tests, ask: "Am I trying to prove or disprove?" Disprove needs one pair of disagreeing paths; prove needs a uniform bound."""

PITFALL_HE = """1. **בדיקת מספר נתיבים והסקה שהגבול קיים.** הסכמה על מספר סופי לא מוכיחה — רק squeeze, אי-תלות ב-$\\theta$, או $\\varepsilon$-$\\delta$.

2. **שכחת נתיבים פרבוליים.** כשכל $y=mx$ מסכימים — נסו $y=kx^2$ לפני טענת קיום.

3. **קריאה שגויה של תוצאה קוטbית.** אם $f=\\cos(2\\theta)$ אחרי הצבה — DNE גם כש-$r\\to 0$. נדרשת אי-תלות ב-$\\theta$.

4. **חסמי squeeze חלשים.** $|f|\\leq 1$ לא עוזר אלא אם גם $\\to 0$. צריך $|f-L|\\leq g(r)$ עם $g(r)\\to 0$.

5. **בלבול רציפות נפרדת מול משותפת.** פונקציה רציפה ב-$x$ לכל $y$ קבוע (ולהפך) יכולה להיכשל בגבול ב-$(0,0)$.

**תבנית תיקון:** אחרי בדיקות נתיבים, שאלו: \"מוכיחים או שוללים?\" שלילה = זוג נתיבים; הוכחה = חסם אחיד."""

WHY_EN = """Multivariable limits are the foundation of **differentiability** and **partial derivatives** — you cannot define $f_x(a,b)$ unless the function behaves consistently as you approach $(a,b)$ from every direction. Every optimization algorithm in machine learning assumes smooth local behavior that starts with limits existing.

**Builds on:** `concept:limits_intro` — the $\\varepsilon$-$\\delta$ idea and squeeze theorem from single-variable calculus carry over, but paths replace left/right limits.

**Unlocks:**
- `concept:partial_derivatives` — partials are limits along axis directions only; full differentiability requires more.
- `concept:optimization_problems` — critical points require limits and continuity on open sets.

**Real applications:** Temperature fields $T(x,y)$ must be continuous for heat-equation models; discontinuities signal phase boundaries or shocks. Path-dependent limits explain why numerical PDE solvers fail near singularities.

**Exam transfer:** University Calc III finals mix "show DNE by paths", "prove limit = 0 by squeeze", and "polar coordinates" on the same exam — three tools, one topic."""

WHY_HE = """גבולות ממשתנים רבים הם הבסיס ל**גזירות** ו**נגזרות חלקיות** — אי אפשר להגדיר $f_x(a,b)$ אלא אם הפונקציה מתנהגת בעקביות בגישה ל-$(a,b)$ מכל כיוון. כל אלגוריתם אופטימיזציה בלמידת מכונה מניח התנהגות חלקה מקומית שמתחילה בקיום גבולות.

**מבוסס על:** `concept:limits_intro` — רעיון $\\varepsilon$-$\\delta$ ומשפט squeeze מחד-משתנה עוברים, אך נתיבים מחליפים גבולות שמאל/ימין.

**פותח:**
- `concept:partial_derivatives` — נגזרות חלקיות הן גבולות לאורך צירים בלבד; גזירות מלאה דורשת יותר.
- `concept:optimization_problems` — נקודות קריטיות דורשות גבולות ורציפות.

**יישומים:** שדות טמפרטורה $T(x,y)$ חייבים להיות רציפים למודלים של משוואות חום; אי-רציפות מסמנת גבולות פאזה. גבולות תלויי-נתיב מסבירים כשלים של פותרי PDE ליד נקודות סינגularity.

**העברה לבחינה:** בחינות Calc III משלבות \"הראה DNE\", \"הוכח = 0 ב-squeeze\", \"קואורדינטות קוטביות\" — שלושה כלים, נושא אחד."""

BEFORE_EN = """**Formula card (recite once):**
- DNE: two paths, two different limits — done.
- Squeeze: $|f-L|\\leq g(r)\\to 0$ with $r=\\sqrt{x^2+y^2}$.
- Polar: $x=r\\cos\\theta$, $y=r\\sin\\theta$; need $\\theta$-independence after $r\\to 0$.
- Key bound: $x^2/(x^2+y^2)\\leq 1$, $y^2/(x^2+y^2)\\leq 1$.

**Exam patterns:** (1) Axes → DNE in 30 seconds. (2) Squeeze with $|y|$ or $|x|$ bound. (3) Polar → if $f=f(\\theta)$, write DNE immediately.

**Path order:** axes → $y=mx$ → $y=kx^2$ → polar.

**Last review:** Solve checkpoint 1 (path DNE) and checkpoint 2 (squeeze) in under 5 minutes without notes.

**Time budget:** Path-test DNE items should take under 90 seconds; squeeze proofs under 3 minutes."""

BEFORE_HE = """**גיליון נוסחאות (אמרו פעם אחת):**
- DNE: שני נתיבים, שני גבולות שונים — סיום.
- Squeeze: $|f-L|\\leq g(r)\\to 0$ עם $r=\\sqrt{x^2+y^2}$.
- קוטביות: $x=r\\cos\\theta$, $y=r\\sin\\theta$; נדרשת אי-תלות ב-$\\theta$.
- חסם מפתח: $x^2/(x^2+y^2)\\leq 1$.

**דפוסי בחינה:** (1) צירים → DNE ב-30 שניות. (2) Squeeze עם $|y|$ או $|x|$. (3) קוטביות → $f=f(\\theta)$ → DNE מיד.

**סדר נתיבים:** צירים → $y=mx$ → $y=kx^2$ → קוטביות.

**חזרה אחרונה:** פתרו checkpoint 1 ו-2 תוך 5 דקות בלי notes."""

SUMMARY_EN = """- **Multivariable limits** require the same value along every path — infinitely many possibilities.
- **DNE:** find two paths with different limits (axes → lines → parabolas).
- **Existence:** squeeze — bound $|f-L|\\leq g(r)\\to 0$.
- **Polar:** $x=r\\cos\\theta$, $y=r\\sin\\theta$; $\\theta$-independence after $r\\to 0$ means limit exists.
- **Key inequality:** $x^2/(x^2+y^2)\\leq 1$ is the main bounding tool.
- **$\\varepsilon$-$\\delta$:** formal proof after conjecturing $L$.

**Takeaway:** Disproving is easy (one path pair); proving requires a uniform bound — squeeze, polar, or $\\varepsilon$-$\\delta$."""

SUMMARY_HE = """- **גבולות ממשתנים רבים:** ערך זהה לאורך כל נתיב — אינסוף אפשרויות.
- **DNE:** שני נתיבים עם ערכים שונים (צירים → ישרים → פרבולות).
- **קיום:** squeeze — $|f-L|\\leq g(r)\\to 0$.
- **קוטביות:** אי-תלות ב-$\\theta$ אחרי $r\\to 0$ = גבול קיים.
- **אי-שוויון:** $x^2/(x^2+y^2)\\leq 1$ — כלי החסימה העיקרי.
- **$\\varepsilon$-$\\delta$:** הוכחה פורמלית אחרי ניחוש $L$.

**מסקנה:** שלילה קלה (זוג נתיבים); הוכחה דורשת חסם אחיד — squeeze, קוטביות, או $\\varepsilon$-$\\delta$."""

EXPLS = {
    1: fmt_expl(
        "Along $y=0$: $f=x/(x^2+0)=1/x$, which blows up to $\\pm\\infty$ as $x\\to 0^\\pm$ — not a finite limit. Along $x=0$: $f=0/(0+y^2)=0$. One path diverges while another tends to $0$; the multivariable limit cannot exist.",
        "DNE problems start with axes. Here the $x$-axis path produces $1/x$ — immediate red flag. You do not need the blow-up to be $\\pm\\infty$ vs a finite number; any two **different behaviors** (including $\\infty$ vs $0$) disprove existence.",
        "Stopping after $y=0$ gives $0$ by incorrectly setting $y=0$ in the numerator only, or claiming both paths give $0$. Another slip: thinking $\\infty$ 'does not count' — it absolutely shows DNE.",
        "When $x$ is linear in the numerator and quadratic in the denominator, test $y=0$ first — you often get $1/x$. Write both path limits and 'therefore DNE.'",
        "נתיב $y=0$: $f=x/x^2=1/x$, מתפוצץ ל-$\\pm\\infty$ — לא גבול סופי. נתיב $x=0$: $f=0$. נתיב אחד מתפוצץ ואחד שואף ל-$0$; הגבול לא יכול להתקיים.",
        "בעיות DNE מתחילות בצירים. כאן ציר $x$ נותן $1/x$ — דגל אדום. לא צריך $\\infty$ מול מספר סופי; כל שני **התנהגויות שונות** (כולל $\\infty$ מול $0$) שוללות קיום.",
        "עצירה אחרי $y=0$ עם $0$ בטעות, או טענה ששני הנתיבים נותנים $0$. $\\infty$ בהחלט מראה DNE.",
        "כש-$x$ לiniari במונה וריבועי במכנה, בדקו $y=0$ קודם — לעיתים $1/x$. כתבו 'נתיב 1: $\\infty$; נתיב 2: $0$; DNE.'",
    ),
    2: fmt_expl(
        "The function $x^2+y$ is a polynomial — continuous everywhere. For polynomials, $\\lim_{(x,y)\\to(a,b)} p(x,y)=p(a,b)$ by substitution: $2^2+3=4+3=7$. Since the limit equals $f(2,3)=7$, the function is continuous at $(2,3)$.",
        "Not every limit requires path tests or squeeze. Off the origin, polynomials and other elementary functions are continuous — just plug in the target point. The limit question is really 'evaluate at $(2,3)$.'",
        "Applying path tests or polar coordinates to a simple polynomial — wasted time. Another slip: computing $2+3=5$ by forgetting to square $x$.",
        "If the function is a polynomial and the point is in the domain, the answer is direct substitution — 10-second problem. Save path tests for rational functions with $(0,0)$ in the denominator.",
        "הפונקציה $x^2+y$ היא פולינום — רציפה בכל מקום. לפולינומים, $\\lim p(x,y)=p(a,b)$ בהצבה: $2^2+3=7$. הגבול שווה $f(2,3)=7$, הפונקציה רציפה ב-$(2,3)$.",
        "לא כל גבול דורש נתיבים או squeeze. מחוץ למקור, פולינומים רציפים — פשוט הציבו. השאלה היא 'חשבו ב-$(2,3)$.'",
        "יישום נתיבים או קוטביות על פולינום פשוט — בזבוז זמן. שגיאה: $2+3=5$ בלי לעצב את $x$.",
        "אם הפונקציה פולינום והנקודה בתחום — הצבה ישירה, 10 שניות. שמרו נתיבים לפונקציות רציונליות עם $(0,0)$ במכנה.",
    ),
    3: fmt_expl(
        "Along $y=0$: $f=x^2/(x^2+0)=x^2/x^2=1$. Along $y=x$: $f=x^2/(x^2+x^2)=x^2/(2x^2)=1/2$. Since $1\\neq 1/2$, two paths give different finite limits — the multivariable limit DNE.",
        "After axes, test $y=x$ (diagonal). The numerator $x^2$ is unchanged, but the denominator doubles — halving the ratio. This is the standard second path for $x^2/(x^2+y^2)$-type functions.",
        "Concluding the limit is $1$ after only testing $y=0$. Or getting $1/2$ on $y=x$ but not comparing to the axis value. Another slip: simplifying $x^2/2x^2$ as $2$ instead of $1/2$.",
        "For $x^2/(x^2+y^2)$, axes give $1$ and $0$; diagonal gives $1/2$. Always report both path limits and the inequality $L_1\\neq L_2$ explicitly for full credit.",
        "נתיב $y=0$: $f=x^2/x^2=1$. נתיב $y=x$: $f=x^2/(2x^2)=1/2$. מכיוון ש-$1\\neq 1/2$, שני נתיבים עם גבולות סופיים שונים — DNE.",
        "אחרי צירים, בדקו $y=x$. המונה $x^2$ זהה, המכנה מכפל — חוצה את היחס. נתיב שני סטנדרטי ל-$x^2/(x^2+y^2)$.",
        "מסקנה שהגבול $1$ אחרי $y=0$ בלבד. או $1/2$ ב-$y=x$ בלי השוואה. $x^2/2x^2$ כ-$2$ במקום $1/2$.",
        "ל-$x^2/(x^2+y^2)$, צירים נותנים $1$ ו-$0$; אלכסון $1/2$. דווחו $L_1\\neq L_2$ במפורש.",
    ),
    4: fmt_expl(
        "Set $x^2+y^2=r^2$. Then $f=r^2\\ln(r^2)=2r^2\\ln r$. As $r\\to 0^+$, standard calculus gives $r^p\\ln r\\to 0$ for any $p>0$. Here $p=2$, so the limit is $0$. The result is independent of $\\theta$ — consistent with existence.",
        "This function depends only on $r=\\sqrt{x^2+y^2}$, not on direction — polar coordinates collapse it to a single-variable limit in $r$. Recognize $r^2\\ln(r^2)$ as $2r^2\\ln r$ and apply the log-vanishing rule.",
        "Leaving the answer as $\\ln 0$ (undefined). Or claiming DNE because $\\ln r\\to -\\infty$ while forgetting the $r^2$ factor tames it. Another slip: not converting $r^2\\ln(r^2)$ to $2r^2\\ln r$.",
        "Memorize: $r^p\\ln r\\to 0$ as $r\\to 0^+$ for $p>0$. This appears on every Calc III exam involving $\\ln(x^2+y^2)$ at the origin.",
        "נקבע $x^2+y^2=r^2$. אז $f=r^2\\ln(r^2)=2r^2\\ln r$. כש-$r\\to 0^+$, $r^p\\ln r\\to 0$ לכל $p>0$. כאן $p=2$, הגבול $0$. התוצאה בלתי-תלויה ב-$\\theta$.",
        "הפונקציה תלויה רק ב-$r$, לא בכיוון — קוטביות מצמצמות לגבול חד-משתנה. $r^2\\ln(r^2)=2r^2\\ln r$ וכלל היעלמות הלוג.",
        "תשובה $\\ln 0$. או DNE כי $\\ln r\\to -\\infty$ בלי גורם $r^2$. לא המרת $r^2\\ln(r^2)$ ל-$2r^2\\ln r$.",
        "שמרו: $r^p\\ln r\\to 0$ ל-$p>0$. מופיע בכל בחינה עם $\\ln(x^2+y^2)$ במקור.",
    ),
    5: fmt_expl(
        "Bound: $|xy^2/(x^2+y^2)|=|x|\\cdot y^2/(x^2+y^2)\\leq |x|$ since $y^2/(x^2+y^2)\\leq 1$. As $(x,y)\\to(0,0)$, $|x|\\to 0$. By squeeze, the limit is $0$.",
        "Squeeze problems at the origin use $x^2/(x^2+y^2)\\leq 1$ or $y^2/(x^2+y^2)\\leq 1$ to peel off a factor and leave $|x|$ or $|y|$ that vanishes. Identify which part of the numerator to bound.",
        "Using $|xy^2/(x^2+y^2)|\\leq |xy^2|$ without dividing by the denominator — the bound does not go to $0$. Or concluding DNE because path tests give $0$ (path agreement does not prove existence, but squeeze does).",
        "Template: $|x^a y^b/(x^2+y^2)|\\leq |x|^{a-2}|y|^b$ or similar when $a\\geq 2$. Practice writing the bound in one line before applying squeeze.",
        "חסם: $|xy^2/(x^2+y^2)|\\leq |x|$ כי $y^2/(x^2+y^2)\\leq 1$. כש-$(x,y)\\to(0,0)$, $|x|\\to 0$, ולפי משפט הסנדוויץ' הגבול $=0$.",
        "בעיות squeeze במקור משתמשות ב-$x^2/(x^2+y^2)\\leq 1$ לקילוף גורם ולהשאיר $|x|$ או $|y|$ שנעלם. זיהו איזה חלק מהמונה לחסום וכתבו את שרשרת האי-שוויונות במפורש.",
        "$|xy^2/(x^2+y^2)|\\leq |xy^2|$ בלי חלוקה במכנה — החסם לא שואף ל-$0$. DNE כי נתיבים נותנים $0$ (הסכמה לא מוכיחה, squeeze כן).",
        "תבנית: $|x^a y^b/(x^2+y^2)|\\leq |x|^{a-2}|y|^b$ כש-$a\\geq 2$. כתבו חסם בשורה אחת לפני יישום squeeze — חוסך זמן בבחינה.",
    ),
    6: fmt_expl(
        "By AM-GM, $|xy|\\leq (x^2+y^2)/2$. So $|xy/\\sqrt{x^2+y^2}|=|xy|/r\\leq (x^2+y^2)/(2r)=r/2\\to 0$ as $r\\to 0$. Squeeze gives limit $0$.",
        "The denominator is $r$, not $r^2$ — one degree lower than typical rational functions. AM-GM converts $|xy|$ to $r^2/2$, leaving a factor of $r$ after dividing by $r$.",
        "Bounding by $|x|$ or $|y|$ alone without AM-GM — too weak here because the denominator is only $\\sqrt{x^2+y^2}$, not $x^2+y^2$. Another slip: getting limit $1$ from an incorrect polar substitution.",
        "When the denominator is $\\sqrt{x^2+y^2}=r$, try AM-GM on $|xy|$ first. Polar gives $f=r\\cos\\theta\\sin\\theta$, bounded by $r/2$ — quick alternative.",
        "לפי AM-GM, $|xy|\\leq (x^2+y^2)/2$. לכן $|xy|/\\sqrt{x^2+y^2}\\leq r/2\\to 0$ כש-$r\\to 0$. לפי משפט הסנדוויץ', הגבול $=0$.",
        "המכנה $r$, לא $r^2$ — דרגה נמוכה יותר מבעיות squeeze טיפוסיות. AM-GM ממיר $|xy|$ ל-$r^2/2$, ואחרי חלוקה ב-$r$ נשאר $r/2\\to 0$.",
        "חסימה ב-$|x|$ בלבד בלי AM-GM — חלש כי המכנה הוא $\\sqrt{x^2+y^2}$ בלבד. גבול $1$ בטעות מהצבה קוטbית שגויה.",
        "כשהמכנה $\\sqrt{x^2+y^2}=r$, נסו AM-GM על $|xy|$ קודם. חלופה: קוטביות נותנת $f=r\\cos\\theta\\sin\\theta$ שחסום על ידי $r/2$.",
    ),
    7: fmt_expl(
        "Polar: $f=r^3(\\cos^3\\theta+\\sin^3\\theta)/r^2=r(\\cos^3\\theta+\\sin^3\\theta)$. Since $|\\cos^3\\theta+\\sin^3\\theta|\\leq 2$, we have $|f|\\leq 2r\\to 0$. Limit $=0$, independent of $\\theta$.",
        "After polar substitution, look for a factor of $r$ remaining. Here one power of $r$ survives, and the $\\theta$-part is bounded — so $f\\to 0$ regardless of direction.",
        "Getting $f=\\cos^3\\theta+\\sin^3\\theta$ without the $r$ factor — then incorrectly claiming DNE. Or forgetting to cancel $r^3/r^2=r$.",
        "When polar gives $f=r\\cdot g(\\theta)$ with $g$ bounded, limit is always $0$. When $r$ cancels entirely, check if $g(\\theta)$ is constant — if not, DNE.",
        "קואורדינטות קוטביות: $f=r^3(\\cos^3\\theta+\\sin^3\\theta)/r^2=r(\\cos^3\\theta+\\sin^3\\theta)$. מכיוון ש-$|\\cos^3\\theta+\\sin^3\\theta|\\leq 2$, מתקיים $|f|\\leq 2r\\to 0$. הגבול $=0$, בלתי-תלוי ב-$\\theta$.",
        "אחרי הצבה קוטbית, חפשו גורם $r$ שנשאר. כאן כוח $r$ אחד נשאר, והחלק ב-$\\theta$ חסום — לכן $f\\to 0$ בכל כיוון.",
        "$f=\\cos^3\\theta+\\sin^3\\theta$ בלי גורם $r$ — DNE בטעות. שכחת לצמצם $r^3/r^2=r$.",
        "כש-$f=r\\cdot g(\\theta)$ ו-$g$ חסום — הגבול תמיד $0$. כש-$r$ מתבטל לגמרי — בדקו אם $g(\\theta)$ קבוע; אם לא, DNE.",
    ),
    8: fmt_expl(
        "Along $y=mx$: $f=2x\\cdot mx/(x^2+m^2x^2)=2m/(1+m^2)$. This depends on $m$ — e.g. $m=0$ gives $0$, $m=1$ gives $1$. Different slopes, different limits, so DNE.",
        "The family $y=mx$ turns the two-variable limit into a one-parameter limit in $m$. If the result still contains $m$, the original limit DNE. Test $m=0$ and $m=1$ for concrete numbers.",
        "Testing only $m=0$ and $m=1$ without explaining the general formula $2m/(1+m^2)$. Or claiming DNE from axes alone (both axes give $0$ here — lines are needed).",
        "When axes agree at $0$, escalate to $y=mx$. If the answer is $2m/(1+m^2)$, write 'depends on $m$' and give two numeric examples — that is a complete DNE proof.",
        "על $y=mx$: $f=2m/(1+m^2)$. תלוי ב-$m$ — $m=0$ נותן $0$, $m=1$ נותן $1$. שיפועים שונים, גבולות שונים, DNE.",
        "משפחת $y=mx$ הופכת גבול דו-משתנה לגבול בפרמטר $m$. אם התוצאה עדיין מכילה $m$ — DNE. בדקו $m=0$ ו-$m=1$.",
        "רק $m=0$ ו-$m=1$ בלי הנוסחה הכללית. DNE מהצירים (שניהם $0$ — צריך ישרים).",
        "כשצירים מסכימים ב-$0$, עברו ל-$y=mx$. אם $2m/(1+m^2)$ — 'תלוי ב-$m$' + שני דוגמאות = הוכחת DNE מלאה.",
    ),
}


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in MIN:
            en_min, he_min = MIN[kind]
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"{kind} en {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{kind} he {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{kind}: weak Hebrew body")
    for q in data["questions"]:
        for lang in ("en", "he"):
            expl = q.get(f"explanation_{lang}", "")
            w = wc(expl)
            if w < 80:
                errors.append(f"q{q['ord']} expl-{lang} {w} < 80")
            if w > 150:
                errors.append(f"q{q['ord']} expl-{lang} {w} > 150")
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
            if "xy" in sec.get("body_en_md", "") and "x^2+y^2" in sec.get("body_en_md", ""):
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
    print(f"Wrote {TARGET}")

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
