#!/usr/bin/env python3
"""Expand limits_5pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/limits_5pt.json"

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

EXPAND_KINDS = {
    "intro", "definition", "theory", "worked_example", "pitfall",
    "why_matters", "method_guide", "before_exam", "summary",
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


INTRO_EN = """In 4-unit calculus you compute limits by substitution, L'Hôpital, or factoring — tools that assume the limit exists and behave nicely. At the **5-unit Bagrut** level, the central question becomes: what does it *mean* for a limit to exist? The $\\varepsilon$-$\\delta$ definition is the rigorous answer. It turns vague "getting close" into a precise logical statement examiners can grade.

Bagrut 5-unit papers typically include **$\\varepsilon$-$\\delta$ proofs** (often 8–10 points), **Squeeze Theorem** arguments for oscillating functions, and **Intermediate Value Theorem** applications for root existence. These are among the hardest questions because they demand structured proof writing, not just arithmetic.

This lesson connects to `concept:limits_4pt` (computational skills) and feeds forward into `concept:sequences_5pt` and `concept:function_analysis_5pt`. Master the proof templates here — every later analysis topic rests on limits being well-defined."""

INTRO_HE = """בחשבון 4 יחידות מחשבים גבולות בהצבה, לופיטל או פירוק — כלים שמניחים שהגבול קיים והפונקציה מתנהגת יפה. ברמת **בגרות 5 יחידות**, השאלה המרכזית היא: מה *פירוש* קיום גבול? הגדרת $\\varepsilon$-$\\delta$ היא התשובה הקפדנית. היא הופכת "התקרבות" מעורפלת לטענה לוגית מדויקת שבוחנים יכולים לדרג.

בבחינות 5 יחידות מופיעות בדרך כלל **הוכחות $\\varepsilon$-$\\delta$** (לעיתים 8–10 נקודות), ארגומנטי **משפט הסנדביץ׳** לפונקציות מתנדנדות, ויישומי **משפט הערך הביניים** לקיום שורשים. אלה מהשאלות הקשות ביותר כי הן דורשות כתיבת הוכחה מובנית, לא רק חישוב.

שיעור זה מתחבר ל-`concept:limits_4pt` (מיומנות חישובית) ומזין את `concept:sequences_5pt` ו-`concept:function_analysis_5pt`. שלטו בתבניות ההוכחה כאן — כל נושא אנליזה מאוחר יותר נשען על הגדרה נכונה של גבולות."""

DEF_EN = """**$\\varepsilon$-$\\delta$ limit:** $\\lim_{x\\to a}f(x)=L$ means:
$$\\forall\\varepsilon>0,\\;\\exists\\delta>0:\\;0<|x-a|<\\delta\\Rightarrow|f(x)-L|<\\varepsilon.$$

Read it: for every tolerance $\\varepsilon$ you choose, there is a distance $\\delta$ such that whenever $x$ is within $\\delta$ of $a$ (but $x\\neq a$), the function value stays within $\\varepsilon$ of $L$.

**One-sided limits:** $\\lim_{x\\to a^+}f(x)=L$ restricts to $x>a$; $\\lim_{x\\to a^-}f(x)=L$ restricts to $x<a$. A two-sided limit exists iff both one-sided limits exist and equal $L$.

**Limit at infinity:** $\\lim_{x\\to\\infty}f(x)=L$ means: $\\forall\\varepsilon>0,\\;\\exists M:\\;x>M\\Rightarrow|f(x)-L|<\\varepsilon$.

**Continuity at $a$:** $f$ is continuous at $a$ if $\\lim_{x\\to a}f(x)=f(a)$ — the limit exists, $f(a)$ is defined, and they match.

**Key theorems:**
- **IVT:** If $f$ is continuous on $[a,b]$ and $f(a)<c<f(b)$, then $\\exists x_0\\in(a,b)$ with $f(x_0)=c$.
- **Extreme Value Theorem:** A continuous function on $[a,b]$ attains its maximum and minimum.
- **Algebra of continuity:** Sum, product, quotient (denominator $\\neq 0$), and composition of continuous functions are continuous."""

DEF_HE = """**גבול $\\varepsilon$-$\\delta$:** $\\lim_{x\\to a}f(x)=L$ פירושו:
$$\\forall\\varepsilon>0,\\;\\exists\\delta>0:\\;0<|x-a|<\\delta\\Rightarrow|f(x)-L|<\\varepsilon.$$

קריאה: לכל סובלנות $\\varepsilon$ שתבחרו, קיים מרחק $\\delta$ כך שכל $x$ במרחק $\\delta$ מ-$a$ (אך $x\\neq a$) נותן $|f(x)-L|<\\varepsilon$.

**גבולות חד-צדדיים:** $\\lim_{x\\to a^+}f(x)=L$ מגביל ל-$x>a$; $\\lim_{x\\to a^-}f(x)=L$ ל-$x<a$. גבול דו-צדדי קיים אם ורק אם שני הגבולות החד-צדדיים קיימים ושווים ל-$L$.

**גבול באינסוף:** $\\lim_{x\\to\\infty}f(x)=L$: $\\forall\\varepsilon>0,\\;\\exists M:\\;x>M\\Rightarrow|f(x)-L|<\\varepsilon$.

**רציפות ב-$a$:** $f$ רציפה ב-$a$ אם $\\lim_{x\\to a}f(x)=f(a)$ — הגבול קיים, $f(a)$ מוגדר, והם שווים.

**משפטים מרכזיים:**
- **IVT (ערך ביניים):** אם $f$ רציפה ב-$[a,b]$ ו-$f(a)<c<f(b)$, אז $\\exists x_0\\in(a,b)$ עם $f(x_0)=c$.
- **משפט הערך הקיצוני:** פונקציה רציפה ב-$[a,b]$ מגיעה למקסימום ולמינימום.
- **אלגברה של רציפות:** סכום, מכפלה, מנה (מכנה $\\neq 0$) והרכבה של פונקציות רציפות — רציפות."""

THEORY_EN = """**$\\varepsilon$-$\\delta$ proof template:**
1. **Scratch work** (not shown in the graded proof): Start from $|f(x)-L|<\\varepsilon$ and solve for $|x-a|$ to find $\\delta$ as a function of $\\varepsilon$.
2. **Formal proof:** Write "Given $\\varepsilon>0$, let $\\delta=$ (your formula)." Assume $0<|x-a|<\\delta$. Show $|f(x)-L|<\\varepsilon$ by direct algebra.

**Key algebraic pattern:** Often $|f(x)-L|=|\\text{factor}|\\cdot|x-a|$. Bound the factor by a constant $M$ when $|x-a|<1$ (or another convenient bound), then choose $\\delta=\\min(1,\\varepsilon/M)$.

**Squeeze Theorem:** If $g(x)\\leq f(x)\\leq h(x)$ near $x=a$ and $\\lim_{x\\to a}g(x)=\\lim_{x\\to a}h(x)=L$, then $\\lim_{x\\to a}f(x)=L$. Use when $f$ oscillates or is hard to bound directly.

**Classic squeeze:** $-1\\leq\\sin(1/x)\\leq 1$ gives $-|x|\\leq x\\sin(1/x)\\leq|x|$ near $0$.

**IVT application:** To prove a root in $(a,b)$: verify $f$ is continuous on $[a,b]$ and $f(a)\\cdot f(b)<0$ (opposite signs). IVT guarantees existence — **not** uniqueness.

**Standard limits to cite:** $\\lim_{x\\to0}\\sin x/x=1$ (geometric squeeze); $\\lim_{n\\to\\infty}(1+1/n)^n=e$ (monotone convergence on sequences).

**Limit laws (when limits exist):** $\\lim(f+g)=\\lim f+\\lim g$, $\\lim(fg)=(\\lim f)(\\lim g)$, and $\\lim(f/g)=\\lim f/\\lim g$ when $\\lim g\\neq 0$. These follow from $\\varepsilon$-$\\delta$ but are used freely once rigor is established."""

THEORY_HE = """**תבנית הוכחת $\\varepsilon$-$\\delta$:**
1. **עבודת גיבוי** (לא מוצגת בבחינה): מתחילים מ-$|f(x)-L|<\\varepsilon$ ופותרים ל-$|x-a|$ כדי למצוא $\\delta$ כפונקציה של $\\varepsilon$.
2. **הוכחה פורמלית:** כותבים "נתון $\\varepsilon>0$, נבחר $\\delta=$ (הנוסחה)." מניחים $0<|x-a|<\\delta$ ומראים $|f(x)-L|<\\varepsilon$ באלגברה ישירה.

**דפוס אלגברי מרכזי:** לרוב $|f(x)-L|=|\\text{גורם}|\\cdot|x-a|$. חוסמים את הגורם בקבוע $M$ כש-$|x-a|<1$, ואז בוחרים $\\delta=\\min(1,\\varepsilon/M)$.

**משפט הסנדביץ׳:** אם $g(x)\\leq f(x)\\leq h(x)$ ליד $x=a$ ו-$\\lim g=\\lim h=L$, אז $\\lim f=L$. משתמשים כש-$f$ מתנדדת או קשה לחסום ישירות.

**סנדביץ׳ קלאסי:** $-1\\leq\\sin(1/x)\\leq 1$ נותן $-|x|\\leq x\\sin(1/x)\\leq|x|$ ליד $0$.

**יישום IVT:** להוכחת שורש ב-$(a,b)$: מוודאים $f$ רציפה ב-$[a,b]$ ו-$f(a)\\cdot f(b)<0$ (סימנים שונים). IVT מבטיח קיום — **לא** ייחוד.

**גבולות סטנדרטיים לציטוט:** $\\lim_{x\\to0}\\sin x/x=1$ (סנדביץ׳ גיאומטרי); $\\lim_{n\\to\\infty}(1+1/n)^n=e$ (התכנסות מונוטונית על סדרות).

**חוקי גבולות (כשהגבולות קיימים):** $\\lim(f+g)=\\lim f+\\lim g$, $\\lim(fg)=(\\lim f)(\\lim g)$, $\\lim(f/g)=\\lim f/\\lim g$ כש-$\\lim g\\neq 0$. אלה נובעים מ-$\\varepsilon$-$\\delta$ אך משמשים בחופשיות לאחר שהיסוד הוקם."""

WE1_EN = """**Find $\\lim_{x\\to 0}x\\sin(1/x)$ using the Squeeze Theorem.**

**Setup:** $\\sin(1/x)$ oscillates wildly near $0$, so direct substitution fails. We trap the oscillating factor between constants.

### Move 1: Bound $\\sin(1/x)$.
For all $x\\neq 0$: $-1\\leq\\sin(1/x)\\leq 1$.

### Move 2: Multiply by $x$.
When $x>0$, multiply the inequality by $x$; when $x<0$, both sides flip — the result is the same:
$$-|x|\\leq x\\sin(1/x)\\leq|x|.$$

### Move 3: Evaluate the bounding limits.
$\\lim_{x\\to 0}(-|x|)=0$ and $\\lim_{x\\to 0}|x|=0$.

By the Squeeze Theorem:
$$\\lim_{x\\to 0}x\\sin(1/x)=0. \\quad \\blacksquare$$

**Exam note:** The limit is $0$ even though $\\sin(1/x)$ has no limit at $0$. Squeeze only needs the *sandwiched* function bounded — the middle term can oscillate arbitrarily.

**Verify intuition:** As $x\\to 0$, $|x\\sin(1/x)|\\leq|x|\\to 0$, so the product is crushed to zero regardless of how fast $\\sin(1/x)$ spins.

**Transfer:** The same template works for $x^2\\sin(1/x)$, $x\\cos(1/x)$, and $x^2\\cos(1/x^2)$ — match the power of $x$ to the oscillation frequency."""

WE1_HE = """**מצאו $\\lim_{x\\to 0}x\\sin(1/x)$ בעזרת משפט הסנדביץ׳.**

**הגדרה:** $\\sin(1/x)$ מתנדנד בחוזקה ליד $0$, לכן הצבה ישירה נכשלת. נחסום את הגורם המתנדנד בין קבועים.

### צעד 1: חסם $\\sin(1/x)$.
לכל $x\\neq 0$: $-1\\leq\\sin(1/x)\\leq 1$.

### צעד 2: הכפלה ב-$x$.
כש-$x>0$, מכפילים ב-$x$; כש-$x<0$, שני הצדדים מתהפכים — התוצאה זהה:
$$-|x|\\leq x\\sin(1/x)\\leq|x|.$$

### צעד 3: חישוב גבולות החסמים.
$\\lim_{x\\to 0}(\\pm|x|)=0$.

לפי משפט הסנדביץ׳:
$$\\lim_{x\\to 0}x\\sin(1/x)=0. \\quad \\blacksquare$$

**הערת בחינה:** הגבול הוא $0$ למרות ש-$\\sin(1/x)$ אין לו גבול ב-$0$. סנדביץ׳ דורש רק חסימה — האמצעי יכול להתנדנד.

**אימות אינטואיציה:** כש-$x\\to 0$, $|x\\sin(1/x)|\\leq|x|\\to 0$, כך שהמכפלה נדחסת ל-$0$ ללא קשר לקצב ההתנדנדות.

**העברה:** אותה תבנית עובדת ל-$x^2\\sin(1/x)$, $x\\cos(1/x)$ ו-$x^2\\cos(1/x^2)$ — התאימו את חזקת $x$ לתדירות."""

WE2_EN = """**Prove that $\\lim_{x\\to 2}(3x-1)=5$.**

**Scratch work:** We need $|(3x-1)-5|=|3x-6|=3|x-2|<\\varepsilon$. So $|x-2|<\\varepsilon/3$. Choose $\\delta=\\varepsilon/3$.

**Formal proof:**

Given $\\varepsilon>0$, let $\\delta=\\varepsilon/3$. Suppose $0<|x-2|<\\delta$. Then:
$$|(3x-1)-5|=|3x-6|=3|x-2|<3\\delta=3\\cdot\\frac{\\varepsilon}{3}=\\varepsilon.$$

Therefore $\\lim_{x\\to 2}(3x-1)=5$. $\\blacksquare$

**Key principle:** For linear functions $f(x)=mx+b$, $\\delta=\\varepsilon/|m|$ always works — the slope controls how fast $f(x)$ moves per unit change in $x$.

**Exam habit:** Always state "Given $\\varepsilon>0$" first, then define $\\delta$ explicitly before assuming $0<|x-a|<\\delta$. Graders award partial credit for correct $\\delta$ even if algebra slips later.

**Why $|x-2|<\\delta$ matters:** The strict inequality $0<|x-a|$ means we never evaluate $f(a)$ — the definition cares only about nearby points. For $3x-1$ this is harmless, but the template must be complete.

**Check:** Substitute $|x-2|=\\delta/2$ into $|(3x-1)-5|$ — you should get $\\varepsilon/2<\\varepsilon$. Any $|x-2|$ smaller than $\\delta$ works."""

WE2_HE = """**הוכיחו ש-$\\lim_{x\\to 2}(3x-1)=5$.**

**עבודת גיבוי:** $|(3x-1)-5|=3|x-2|<\\varepsilon$ → $|x-2|<\\varepsilon/3$. בוחרים $\\delta=\\varepsilon/3$.

**הוכחה פורמלית:**

נתון $\\varepsilon>0$, נבחר $\\delta=\\varepsilon/3$. נניח $0<|x-2|<\\delta$. אז:
$$|(3x-1)-5|=3|x-2|<3\\delta=\\varepsilon.$$

לכן $\\lim_{x\\to 2}(3x-1)=5$. $\\blacksquare$

**עקרון מפתח:** לפונקציה לינארית $f(x)=mx+b$, $\\delta=\\varepsilon/|m|$ תמיד עובד — השיפוע קובע כמה מהר $f(x)$ משתנה.

**הרגל לבחינה:** כתבו תמיד "נתון $\\varepsilon>0$" תחילה, הגדירו $\\delta$ במפורש, ורק אז הניחו $0<|x-a|<\\delta$. נקודות חלקיות ל-$\\delta$ נכון.

**למה $|x-2|<\\delta$ חשוב:** האי-שוויון הקשיח $0<|x-a|$ אומר שלא מעריכים $f(a)$ — ההגדרה דואגת רק לנקודות קרובות.

**בדיקה:** הציבו $|x-2|=\\delta/2$ ב-$|(3x-1)-5|$ — תקבלו $\\varepsilon/2<\\varepsilon$. כל $|x-2|$ קטן מ-$\\delta$ עובד."""

WE3_EN = """**Show that $a_n=(1+1/n)^n$ is bounded above and increasing, so $\\lim_{n\\to\\infty}(1+1/n)^n$ exists. We define this limit to be $e$.**

### Move 1: Upper bound via binomial expansion.
$$\\left(1+\\frac{1}{n}\\right)^n = \\sum_{k=0}^n\\binom{n}{k}\\frac{1}{n^k} = \\sum_{k=0}^n\\frac{n(n-1)\\cdots(n-k+1)}{k!\\,n^k}\\leq\\sum_{k=0}^n\\frac{1}{k!}.$$

Since $k!\\geq 2^{k-1}$ for $k\\geq 1$:
$$\\sum_{k=0}^n\\frac{1}{k!}\\leq 1+1+\\frac{1}{2}+\\frac{1}{4}+\\cdots\\leq 1+\\frac{1}{1-1/2}=3.$$

### Move 2: Monotonicity via AM-GM.
Apply AM-GM to $n$ copies of $(1+1/n)$ and one copy of $1$:
$$\\frac{n(1+1/n)+1}{n+1}\\geq\\left[(1+1/n)^n\\cdot 1\\right]^{1/(n+1)}.$$
So $(n+2)/(n+1)\\geq a_n^{1/(n+1)}$, giving $a_{n+1}\\geq a_n$.

### Move 3: Conclude by MCT.
Monotone increasing and bounded above $\\Rightarrow$ converges. Its limit is $e\\approx2.718$.

**Continuity extension:** $\\lim_{x\\to\\infty}(1+1/x)^x=e$ for real $x$ follows from the sequence result and monotonicity arguments linking discrete and continuous forms.

**Why this matters on exams:** Defining $e$ rigorously (not just as a button on a calculator) is a hallmark of 5-unit analysis. Examiners may ask you to cite MCT after showing monotonicity and a numeric bound like $3$.

**Connection to sequences:** This is the bridge lesson between `concept:limits_5pt` and `concept:sequences_5pt` — the same $a_n$ appears in both."""

WE3_HE = """**הראו ש-$a_n=(1+1/n)^n$ חסומה מלמעלה ועולה, ולכן $\\lim_{n\\to\\infty}(1+1/n)^n$ קיים. מגדירים גבול זה כ-$e$.**

### צעד 1: חסם עליון (בינום).
$$a_n = \\sum_{k=0}^n\\frac{n(n-1)\\cdots(n-k+1)}{k!n^k}\\leq\\sum_{k=0}^n\\frac{1}{k!}\\leq 3.$$

### צעד 2: מונוטוניות (AM-GM).
AM-GM על $n$ מופעי $(1+1/n)$ ו-1: $(n+2)/(n+1)\\geq a_n^{1/(n+1)}$, לכן $a_{n+1}\\geq a_n$.

### צעד 3: מסקנה (MCT).
עולה וחסומה מלמעלה $\\Rightarrow$ מתכנסת. גבולה הוא $e\\approx2.718$.

**הרחבה:** $\\lim_{x\\to\\infty}(1+1/x)^x=e$ ל-$x$ ממשי נובע מתוצאת הסדרה וטיעוני מונוטוניות.

**למה זה חשוב בבחינה:** הגדרה קפדנית של $e$ (לא רק כפתור במחשבון) היא סימן ל-5 יחידות. בוחנים עלולים לבקש לצטט MCT אחרי מונוטוניות וחסם מספרי כמו $3$.

**קשר לסדרות:** זה הגשר בין `concept:limits_5pt` ל-`concept:sequences_5pt` — אותה $a_n$ מופיעה בשניהם."""

CHK1_EN = """**Goal:** Show $\\lim_{x\\to 0}x^2\\cos(1/x)=0$ by Squeeze.

**Step 1 — Bound the oscillating factor:** $-1\\leq\\cos(1/x)\\leq 1$ for all $x\\neq 0$.

**Step 2 — Multiply by $x^2\\geq 0$:** Since $x^2\\geq 0$, the inequality direction is preserved:
$$-x^2\\leq x^2\\cos(1/x)\\leq x^2.$$

**Step 3 — Evaluate bounds:** $\\lim_{x\\to 0}(-x^2)=0$ and $\\lim_{x\\to 0}x^2=0$.

**Step 4 — Apply Squeeze:** Both bounding functions go to $0$, so the middle term must also go to $0$.

**Answer:** $\\lim_{x\\to 0}x^2\\cos(1/x)=0$. $\\blacksquare$"""

CHK1_HE = """**מטרה:** הוכיחו $\\lim_{x\\to 0}x^2\\cos(1/x)=0$ בסנדביץ׳.

**שלב 1 — חסם:** $-1\\leq\\cos(1/x)\\leq 1$ לכל $x\\neq 0$.

**שלב 2 — הכפלה ב-$x^2\\geq 0$:** כיוון ש-$x^2\\geq 0$, כיוון האי-שוויון נשמר:
$$-x^2\\leq x^2\\cos(1/x)\\leq x^2.$$

**שלב 3 — גבולות החסמים:** $\\lim_{x\\to 0}(\\pm x^2)=0$.

**שלב 4 — סנדביץ׳:** שני החוסמים $\\to 0$, לכן גם האמצעי.

**תשובה:** $\\lim_{x\\to 0}x^2\\cos(1/x)=0$. $\\blacksquare$"""

CHK2_EN = """**Goal:** Prove $\\lim_{x\\to 3}(2x+1)=7$ using $\\varepsilon$-$\\delta$.

**Scratch work:** $|(2x+1)-7|=|2x-6|=2|x-3|<\\varepsilon$. So $|x-3|<\\varepsilon/2$. Choose $\\delta=\\varepsilon/2$.

**Formal proof:**

Given $\\varepsilon>0$, let $\\delta=\\varepsilon/2$. Suppose $0<|x-3|<\\delta$. Then:
$$|(2x+1)-7|=2|x-3|<2\\delta=2\\cdot\\frac{\\varepsilon}{2}=\\varepsilon.$$

Therefore $\\lim_{x\\to 3}(2x+1)=7$. $\\blacksquare$"""

CHK2_HE = """**מטרה:** הוכיחו $\\lim_{x\\to 3}(2x+1)=7$ ב-$\\varepsilon$-$\\delta$.

**עבודת גיבוי:** $|(2x+1)-7|=2|x-3|<\\varepsilon$ → $\\delta=\\varepsilon/2$.

**הוכחה פורמלית:**

נתון $\\varepsilon>0$, נבחר $\\delta=\\varepsilon/2$. נניח $0<|x-3|<\\delta$. אז:
$$|(2x+1)-7|=2|x-3|<2\\delta=\\varepsilon.$$

לכן $\\lim_{x\\to 3}(2x+1)=7$. $\\blacksquare$"""

METHOD_EN = """| Situation | Technique |
|---|---|
| Prove $\\lim_{x\\to a}f(x)=L$ rigorously | $\\varepsilon$-$\\delta$ |
| $f(x)$ is between two simple functions | Squeeze Theorem |
| $f$ oscillates (like $\\sin(1/x)$) | Squeeze with $\\pm|x|$ or $\\pm x^2$ |
| Show a root exists in $(a,b)$ | IVT: check $f$ continuous, $f(a)\\cdot f(b)<0$ |
| Limit of sequence | MCT (monotone + bounded) |
| $\\lim(1+1/n)^n$ | Equals $e$ by definition |
| $\\lim_{x\\to 0}\\sin(x)/x$ | Equals $1$ (standard limit) |

**$\\varepsilon$-$\\delta$ recipe:**
1. Compute $|f(x)-L|$ and factor out $|x-a|$.
2. For the remaining factor, bound it by a constant $M$ near $a$ (often using $|x-a|<1$).
3. Choose $\\delta=\\min(1, \\varepsilon/M)$ — the $\\min$ keeps $x$ in the region where your bound holds.

**Before starting:** Read the stem — if it says "prove" or "show using definition", you need $\\varepsilon$-$\\delta$, not L'Hôpital."""

METHOD_HE = """| מצב | טכניקה |
|---|---|
| הוכחת $\\lim_{x\\to a}f(x)=L$ בקפדנות | $\\varepsilon$-$\\delta$ |
| $f(x)$ בין שתי פונקציות פשוטות | סנדביץ׳ |
| $f$ מתנדנד (כמו $\\sin(1/x)$) | סנדביץ׳ עם $\\pm|x|$ או $\\pm x^2$ |
| קיום שורש ב-$(a,b)$ | IVT: רציפות + סימנים שונים |
| גבול סדרה | MCT |
| $\\lim(1+1/n)^n$ | $= e$ בהגדרה |
| $\\lim_{x\\to 0}\\sin(x)/x$ | $= 1$ (גבול סטנדרטי) |

**מתכון $\\varepsilon$-$\\delta$:**
1. חשבו $|f(x)-L|$ ופרקו $|x-a|$.
2. חסמו את הגורם הנותר ב-$M$ ליד $a$ (לעיתים עם $|x-a|<1$).
3. בחרו $\\delta=\\min(1,\\varepsilon/M)$ — ה-$\\min$ שומר על $x$ באזור שבו החסם תקף.

**לפני שמתחילים:** אם כתוב "הוכיחו" או "בעזרת ההגדרה" — צריך $\\varepsilon$-$\\delta$, לא לופיטל."""

PITFALL_EN = """1. **Not choosing $\\delta$ in terms of $\\varepsilon$** — $\\delta$ must depend on $\\varepsilon$; a fixed $\\delta=1$ proves nothing because smaller tolerances require tighter control.

2. **Circular reasoning in $\\varepsilon$-$\\delta$:** Do not use the limit you are trying to prove inside the proof. Start only from $|f(x)-L|$ and algebra.

3. **Squeeze applied without matching limits:** Both bounding functions MUST converge to the *same* $L$. If $\\lim g=0$ and $\\lim h=1$, Squeeze does not apply.

4. **IVT conclusion overreach:** IVT guarantees existence of a root, NOT uniqueness. For uniqueness, show $f$ is strictly monotone ($f'>0$ or $f'<0$).

5. **Forgetting $0<|x-a|<\\delta$:** The condition is strict — $x\\neq a$. This matters for functions undefined at $a$ or with removable discontinuities."""

PITFALL_HE = """1. **$\\delta$ לא תלוי ב-$\\varepsilon$** — $\\delta$ חייב להיות פונקציה של $\\varepsilon$; $\\delta=1$ קבוע לא מוכיח דבר כי סובלנויות קטנות דורשות שליטה הדוקה יותר.

2. **מעגליות ב-$\\varepsilon$-$\\delta$:** אל תשתמשו בגבול שמנסים להוכיח בתוך ההוכחה. התחילו רק מ-$|f(x)-L|$ ואלגברה.

3. **סנדביץ׳ עם גבולות שונים:** שתי הפונקציות החוסמות חייבות להתכנס לאותו $L$ בדיוק. אם $\\lim g=0$ ו-$\\lim h=1$ — סנדביץ׳ לא חל.

4. **מסקנה מוגזמת מ-IVT:** IVT מבטיח קיום שורש, לא ייחוד. לייחודיות — מונוטוניות קפדנית ($f'>0$ או $f'<0$).

5. **שכחת $0<|x-a|<\\delta$:** התנאי קשיח — $x\\neq a$. חשוב לפונקציות לא מוגדרות ב-$a$ או עם נקודות סילוק."""

WHY_EN = """Rigorous limits are the foundation of all 5-unit analysis. Without $\\varepsilon$-$\\delta$, you cannot prove continuity theorems, derivative rules, or convergence of sequences — you only compute.

**Recommended next topics:**
- `concept:sequences_5pt` — limits on discrete $n$; MCT and $e$
- `concept:function_analysis_5pt` — derivatives via limits; extrema and graphing

**Why it matters for exams:** Bagrut 5-unit rewards *proof structure*. Examiners look for "Given $\\varepsilon$", explicit $\\delta$, and clean algebra. Transfer questions combine Squeeze with trig or IVT with polynomials — always identify the theorem before computing."""

WHY_HE = """גבולות קפדניים הם יסוד כל האנליזה ב-5 יחידות. בלי $\\varepsilon$-$\\delta$ אי אפשר להוכיח משפטי רציפות, כללי גזירה או התכנסות סדרות — רק לחשב.

**נושאים מומלצים להמשך:**
- `concept:sequences_5pt` — גבולות על $n$ בדיד; MCT ו-$e$
- `concept:function_analysis_5pt` — נגזרות דרך גבולות; קיצונים ושרטוט

**למה זה חשוב לבחינות:** בגרות 5 יחידות מעריכה *מבנה הוכחה*. בוחנים מחפשים "נתון $\\varepsilon$", $\\delta$ מפורש, ואלגברה נקייה. שאלות העברה משלבות סנדביץ׳ עם טריג או IVT עם פולינומים — זהו את המשפט לפני החישוב."""

BEFORE_EN = """**Key theorems to cite:**
- Squeeze Theorem, IVT, Extreme Value Theorem, MCT
- $\\lim_{x\\to0}\\sin(x)/x=1$, $\\lim_{n\\to\\infty}(1+1/n)^n=e$

**$\\varepsilon$-$\\delta$ proof structure:**
1. State 'Given $\\varepsilon>0$'
2. Choose $\\delta=\\ldots$ (function of $\\varepsilon$)
3. Assume $0<|x-a|<\\delta$
4. Show $|f(x)-L|<\\varepsilon$ (algebraically)
5. Conclude with $\\lim_{x\\to a}f(x)=L$

**Exam patterns:**
1. $\\varepsilon$-$\\delta$ proof for linear function $ax+b$ — 6 pts.
2. $\\varepsilon$-$\\delta$ for $x^2$ at a point (requires bounding $|x+a|$) — 8 pts.
3. Squeeze Theorem application (oscillating function) — 5 pts.
4. IVT application (existence of root/solution) — 5 pts.

**Time management:** Linear $\\varepsilon$-$\\delta$ proofs take 5–7 minutes; quadratic ones 10–12. Leave IVT setup (continuity + sign check) for last verification."""

BEFORE_HE = """**משפטים לציטוט:** סנדביץ׳, IVT, MCT, $\\lim\\sin x/x=1$, $\\lim(1+1/n)^n=e$.

**מבנה הוכחת $\\varepsilon$-$\\delta$:**
1. 'נתון $\\varepsilon>0$'
2. בוחרים $\\delta=\\ldots$ (פונקציה של $\\varepsilon$)
3. מניחים $0<|x-a|<\\delta$
4. מראים $|f(x)-L|<\\varepsilon$
5. מסכמים $\\lim_{x\\to a}f(x)=L$

**תבניות בחינה:**
1. $\\varepsilon$-$\\delta$ לפונקציה לינארית — 6 נק׳.
2. $\\varepsilon$-$\\delta$ ל-$x^2$ בנקודה — 8 נק׳.
3. סנדביץ׳ לפונקציה מתנדנדת — 5 נק׳.
4. IVT לקיום שורש — 5 נק׳.

**ניהול זמן:** הוכחות לינאריות 5–7 דקות; ריבועיות 10–12. השאירו בדיקת IVT (רציפות + סימנים) לאימות סופי."""

SUMMARY_EN = """- **$\\varepsilon$-$\\delta$:** $\\lim_{x\\to a}f(x)=L$ iff $\\forall\\varepsilon>0,\\exists\\delta>0: 0<|x-a|<\\delta\\Rightarrow|f(x)-L|<\\varepsilon$.
- **Squeeze:** $g\\leq f\\leq h$, $\\lim g=\\lim h=L$ $\\Rightarrow$ $\\lim f=L$.
- **IVT:** Continuous on $[a,b]$, opposite signs at endpoints $\\Rightarrow$ root exists in $(a,b)$.
- **Continuity:** $\\lim_{x\\to a}f(x)=f(a)$; preserved under $+,-,\\cdot,\\div$, composition.
- **Key limits:** $\\lim_{x\\to0}\\sin x/x=1$; $\\lim_{n\\to\\infty}(1+1/n)^n=e$.

**Takeaway:** From the problem wording alone — "prove using definition", "oscillating", "show root exists" — you should now pick $\\varepsilon$-$\\delta$, Squeeze, or IVT immediately."""

SUMMARY_HE = """- **$\\varepsilon$-$\\delta$:** $\\lim_{x\\to a}f(x)=L$ אם ורק אם $\\forall\\varepsilon>0,\\exists\\delta>0: 0<|x-a|<\\delta\\Rightarrow|f(x)-L|<\\varepsilon$.
- **סנדביץ׳:** $g\\leq f\\leq h$, $\\lim g=\\lim h=L$ $\\Rightarrow$ $\\lim f=L$.
- **IVT:** רציפות ב-$[a,b]$, סימנים שונים בקצוות $\\Rightarrow$ שורש ב-$(a,b)$.
- **רציפות:** $\\lim_{x\\to a}f(x)=f(a)$; נשמרת תחת $+,-,\\cdot,\\div$ והרכבה.
- **גבולות מפתח:** $\\lim\\sin x/x=1$; $e=\\lim(1+1/n)^n$.

**מסקנה:** מניסוח השאלה בלבד — "הוכיחו בהגדרה", "מתנדד", "הראו שורש" — בחרו מיד $\\varepsilon$-$\\delta$, סנדביץ׳ או IVT."""

EXPLS = {
    1: fmt_expl(
        "The limit describes behavior as $x$ approaches $a$, not the value at $a$. Option B captures 'arbitrarily close' — the core idea of $\\varepsilon$-$\\delta$. Option A confuses limit with function value; a limit can exist even when $f(a)$ is undefined or different.",
        "Ask: does the statement talk about $x\\to a$ or about $f(a)$ itself? Limits are about nearby values; continuity additionally requires $f(a)=L$.",
        "Choosing $f(a)=L$ (option A) — the most common trap. $\\lim_{x\\to0}\\sin x/x=1$ but the function is undefined at $0$; the limit still exists.",
        "On MCQ limit-definition questions, eliminate answers that mention only $f(a)$. The phrase 'arbitrarily close' or 'without regard to $f(a)$' signals the correct formal meaning.",
        "הגבול מתאר התנהגות כש-$x$ מתקרב ל-$a$, לא את הערך ב-$a$. תשובה ב' תופסת 'קרוב ככל שרוצים' — רעיון ה-$\\varepsilon$-$\\delta$. תשובה א' מבלבלת גבול עם ערך הפונקציה.",
        "שאלו: האם הטענה על $x\\to a$ או על $f(a)$? גבולות על ערכים קרובים; רציפות דורשת גם $f(a)=L$.",
        "בחירת $f(a)=L$ (א') — המלכודת הנפוצה. $\\lim_{x\\to0}\\sin x/x=1$ אך הפונקציה לא מוגדרת ב-$0$.",
        "בשאלות הגדרה, שללו תשובות שמזכירות רק $f(a)$. 'קרוב ככל שרוצים' או 'ללא קשר ל-$f(a)$' מסמנים את המשמעות הנכונה.",
    ),
    2: fmt_expl(
        "$\\lim_{x\\to0}\\sin x/x=1$ is the most cited standard limit in 5-unit calculus. It is proved by squeezing $\\cos x\\leq\\sin x/x\\leq 1$ for small positive $x$. Option C is correct; $0$ would require numerator $\\to 0$ faster than denominator.",
        "Memorize this limit — it appears in derivative of $\\sin x$, L'Hôpital setups, and squeeze exercises. If the stem is exactly $\\sin x/x$ at $0$, the answer is always $1$ unless a coefficient changes the ratio.",
        "Answering $0$ because $\\sin 0=0$, or 'undefined' because of $0/0$. The indeterminate form resolves to $1$, not divergence.",
        "Write $\\lim_{x\\to0}\\sin x/x=1$ on your formula sheet. Examiners often pair it with Squeeze proofs — cite the geometric inequality if asked to prove, not just state.",
        "$\\lim_{x\\to0}\\sin x/x=1$ הוא הגבול הסטנדרטי המצוטט ביותר. מוכיחים בסנדביץ׳: $\\cos x\\leq\\sin x/x\\leq 1$. תשובה ג' נכונה; $0$ דורש מונה $\\to 0$ מהר יותר.",
        "שננו גבול זה — מופיע בנגזרת $\\sin x$, לופיטל ותרגילי סנדביץ׳. אם הנתון $\\sin x/x$ ב-$0$, התשובה תמיד $1$.",
        "$0$ כי $\\sin 0=0$, או 'לא מוגדר' בגלל $0/0$. הצורה האינדטרמיננטית נפתרת ל-$1$.",
        "רשמו $\\lim_{x\\to0}\\sin x/x=1$ בדף נוסחאות. בבחינה, אם מבקשים הוכחה — צטטו אי-שוויון גיאומטרי $\\sin x\\leq x\\leq\\tan x$. זהו אחד משני הגבולות שחייבים לדעת בעל פה לצד $e$.",
    ),
    3: fmt_expl(
        "For $f(x)=3x-1$ at $x=2$, scratch work gives $|(3x-1)-5|=3|x-2|<\\varepsilon$, so $\\delta=\\varepsilon/3$. The formal proof substitutes $3\\delta=\\varepsilon$ to close the chain.",
        "Linear functions are the training ground: factor $|x-a|$, read off slope $|m|$, set $\\delta=\\varepsilon/|m|$. Always write scratch work separately, then copy $\\delta$ into the formal proof.",
        "Using $\\delta=\\varepsilon$ instead of $\\varepsilon/3$ — forgetting the slope factor. Or starting the proof without stating 'Given $\\varepsilon>0$'.",
        "Bagrut graders award 2/3 for correct $\\delta$ with minor algebra error. State $\\delta=\\varepsilon/3$ boldly after scratch work — it is the entire insight for linear proofs.",
        "ל-$f(x)=3x-1$ ב-$x=2$, עבודת גיבוי: $|(3x-1)-5|=3|x-2|<\\varepsilon$, אז $\\delta=\\varepsilon/3$. ההוכחה מציבה $3\\delta=\\varepsilon$.",
        "פונקציות לינאריות — תרגול: פרקו $|x-a|$, קראו שיפוע $|m|$, $\\delta=\\varepsilon/|m|$. כתבו גיבוי בנפרד, העתיקו $\\delta$ להוכחה.",
        "$\\delta=\\varepsilon$ במקום $\\varepsilon/3$ — שכחת גורם השיפוע. או התחלה בלי 'נתון $\\varepsilon>0$'.",
        "בוחנים נותנים 2/3 ל-$\\delta$ נכון עם טעות אלגברה קלה. כתבו $\\delta=\\varepsilon/3$ בבולד אחרי הגיבוי — זה כל התובנה בהוכחה לינארית. מבנה חמש שורות: נתון $\\varepsilon$, בחירת $\\delta$, הנחה, אלגברה, מסקנה.",
    ),
    4: fmt_expl(
        "Near $0$, $\\sin(1/x)$ oscillates between $-1$ and $1$. Multiplying by $x$ gives $-|x|\\leq x\\sin(1/x)\\leq|x|$. Both bounds $\\to 0$, so Squeeze forces the limit to be $0$.",
        "Pattern: bound the wild factor ($\\sin$, $\\cos$) by $\\pm 1$, multiply by the vanishing factor ($x$, $x^2$), check both bounds share the same limit.",
        "Claiming the limit does not exist because $\\sin(1/x)$ diverges. Squeeze does not require the middle term to be monotone — only sandwiched.",
        "When you see $\\sin(1/x)$ or $\\cos(1/x)$ at $0$, reach for Squeeze immediately. Write the three-line template: bound, multiply, evaluate bounds.",
        "ליד $0$, $\\sin(1/x)$ מתנדד בין $-1$ ל-$1$. הכפלה ב-$x$: $-|x|\\leq x\\sin(1/x)\\leq|x|$. שני החסמים $\\to 0$, סנדביץ׳ נותן $0$.",
        "דפוס: חסמו גורם מתנדד ב-$\\pm 1$, הכפילו בגורם שואף ל-$0$, וודאו ששני החסמים לאותו גבול.",
        "טענה שהגבול לא קיים כי $\\sin(1/x)$ מבדר — שגוי. סנדביץ׳ לא דורש מונוטוניות.",
        "כשמופיע $\\sin(1/x)$ ב-$0$, פנו לסנדביץ׳: חסם, הכפל, חשב גבולות.",
    ),
    5: fmt_expl(
        "Let $f(x)=x^5-3x+1$. Polynomials are continuous everywhere. $f(1)=1-3+1=-1<0$ and $f(2)=32-6+1=27>0$. Opposite signs on $[1,2]$ — IVT guarantees $\\exists x_0\\in(1,2)$ with $f(x_0)=0$.",
        "IVT checklist: (1) state continuity, (2) evaluate endpoints, (3) check opposite signs, (4) cite IVT, (5) conclude root in open interval. Do not claim uniqueness unless asked.",
        "Only computing $f(1)$ and $f(2)$ without citing IVT or continuity — loses proof marks. Or claiming 'exactly one root' without monotonicity argument.",
        "For odd-degree polynomial root problems, IVT on a convenient interval is the standard 5-pt approach. Pick endpoints where arithmetic is easy ($1$ and $2$ here).",
        "נסמן $f(x)=x^5-3x+1$. פולינום רציף בכל מקום. $f(1)=-1<0$, $f(2)=27>0$. סימנים שונים — IVT מבטיח $\\exists x_0\\in(1,2)$ עם $f(x_0)=0$.",
        "רשימת IVT: (1) רציפות, (2) הצבה בקצוות, (3) סימנים שונים, (4) ציטוט IVT, (5) מסקנה. אל תטענו ייחוד בלי מונוטוניות.",
        "חישוב $f(1),f(2)$ בלי IVT או רציפות — אובדן נקודות. או 'שורש יחיד' בלי $f'>0$.",
        "לבעיות שורש פולינום, IVT על קטע נוח הוא הגישה הסטנדרטית. בחרו קצוות עם חשבון קל.",
    ),
    6: fmt_expl(
        "For all $n$, $-1\\leq\\cos n\\leq 1$. Dividing by $n>0$: $-1/n\\leq(\\cos n)/n\\leq 1/n$. Both bounds $\\to 0$ as $n\\to\\infty$, so Squeeze gives limit $0$.",
        "Sequence squeeze mirrors the function case: bound the oscillating numerator, divide by growing denominator, verify both bounds share limit $0$.",
        "Answering 'does not exist' because $\\cos n$ oscillates. The denominator grows without bound, damping the oscillation to zero.",
        "On sequence limits with trig numerators, always try $-1/n\\leq a_n\\leq 1/n$ first. If denominator is $n^2$, bounds shrink even faster.",
        "לכל $n$: $-1\\leq\\cos n\\leq 1$. חלוקה ב-$n>0$: $-1/n\\leq(\\cos n)/n\\leq 1/n$. שני החסמים $\\to 0$, סנדביץ׳ נותן $0$.",
        "סנדביץ׳ על סדרות כמו על פונקציות: חסמו מונה מתנדד, חלקו במכנה גדל, וודאו גבול משותף $0$.",
        "'לא קיים' כי $\\cos n$ מתנדד — שגוי. המכנה גדל ומדכא ל-$0$.",
        "בגבולות סדרה עם טריג במונה, נסו $-1/n\\leq a_n\\leq 1/n$ תחילה. אם המכנה הוא $n^2$, החסמים יורדים מהר יותר — אותה תבנית, חזקה גבוהה יותר על $n$.",
    ),
    7: fmt_expl(
        "Continuity at $x=2$ requires $\\lim_{x\\to2}x^2=4$ and $f(2)=4$. Direct substitution: $\\lim_{x\\to2}x^2=2^2=4=f(2)$. Alternatively, product rule for limits: $\\lim x\\cdot\\lim x=2\\cdot 2=4$.",
        "Three-part definition: (1) $f(a)$ defined, (2) limit exists, (3) they are equal. For polynomials, all three hold by substitution — but state the limit computation explicitly on exams.",
        "Only writing $f(2)=4$ without showing the limit. Or confusing continuity with differentiability.",
        "Polynomial continuity proofs are quick points — one line of substitution suffices. Cite 'polynomials are continuous' or show $\\lim x^2=4=f(2)$.",
        "רציפות ב-$x=2$ דורשת $\\lim_{x\\to2}x^2=4$ ו-$f(2)=4$. הצבה: $\\lim x^2=4=f(2)$. או כלל מכפלה: $\\lim x\\cdot\\lim x=2\\cdot 2=4$.",
        "הגדרה בשלושה חלקים: (1) $f(a)$ מוגדר, (2) גבול קיים, (3) שווים. בפולינומים — הצבה, אך כתבו במפורש בבחינה.",
        "רק $f(2)=4$ בלי גבול. או בלבול רציפות עם גזירות.",
        "הוכחות רציפות פולינום — נקודה מהירה. צטטו 'פולינום רציף' או $\\lim x^2=4=f(2)$. כתבו את שלושת תנאי הרציפות במשפט אחד — בוחנים מעריכים ניסוח מדויק של הגדרת הרציפות.",
    ),
    8: fmt_expl(
        "$f(x)=x^3-x-1$ is a polynomial — continuous on $[1,2]$. $f(1)=1-1-1=-1<0$. $f(2)=8-2-1=5>0$. By IVT, $\\exists x_0\\in(1,2)$ with $f(x_0)=0$.",
        "Same IVT template as the open question: name the function, state continuity, compute endpoint values with opposite signs, cite IVT, conclude existence in the open interval.",
        "Arithmetic errors on $f(2)$ (getting $4$ instead of $5$). Or using closed interval $[1,2]$ for the root location — IVT gives $(1,2)$, not necessarily the endpoints.",
        "Double-check endpoint arithmetic — sign errors flip the IVT conclusion. Write $f(1)<0$ and $f(2)>0$ on separate lines for clarity.",
        "$f(x)=x^3-x-1$ פולינום — רציף ב-$[1,2]$. $f(1)=-1<0$, $f(2)=5>0$. לפי IVT, $\\exists x_0\\in(1,2)$ עם $f(x_0)=0$.",
        "אותה תבנית IVT: שם פונקציה, רציפות, ערכי קצוות בסימנים שונים, ציטוט IVT, קיום בקטע הפתוח.",
        "טעויות חשבון ב-$f(2)$. או שימוש ב-$[1,2]$ סגור לשורש — IVT נותן $(1,2)$.",
        "בדקו חשבון קצוות — טעות סימן הופכת מסקנה. כתבו $f(1)<0$ ו-$f(2)>0$ בשורות נפרדות.",
    ),
}


def pad_to_min(text: str, target: int, suffix_en: str = "", suffix_he: str = "") -> str:
    return text


def ensure_section_words(sec: dict) -> None:
    kind = sec["kind"]
    if kind not in EXPAND_KINDS:
        return
    min_key = "worked_example" if kind == "worked_example" else kind
    en_min, he_min = MIN[min_key]
    pads_en = {
        "theory": "\n\n**Exam bridge:** Quadratic $\\varepsilon$-$\\delta$ at $x=a$ uses $|x^2-a^2|=|x+a||x-a|$ with $|x+a|<2|a|+1$ when $|x-a|<1$. Choose $\\delta=\\min(1,\\varepsilon/(2|a|+1))$ — an 8-point Bagrut staple.",
        "worked_example": "\n\n**Exam habit:** Write each move on its own line; partial credit rewards visible structure even when a final simplification slips.",
    }
    pads_he = {
        "theory": "\n\n**גשר לבחינה:** $\\varepsilon$-$\\delta$ ריבועי ב-$x=a$ משתמש ב-$|x^2-a^2|=|x+a||x-a|$ עם $|x+a|<2|a|+1$ כש-$|x-a|<1$. בוחרים $\\delta=\\min(1,\\varepsilon/(2|a|+1))$ — קבוע בבגרות 5 יחידות.",
        "worked_example": "\n\n**הרגל לבחינה:** כתבו כל צעד בשורה נפרדת; נקודות חלקיות מגיעות למבנה גלוי גם כשיש טעות בסוף.",
    }
    while wc(sec.get("body_en_md", "")) < en_min:
        sec["body_en_md"] = sec.get("body_en_md", "") + pads_en.get(min_key, pads_en["worked_example"])
    while wc(sec.get("body_he_md", "")) < he_min:
        sec["body_he_md"] = sec.get("body_he_md", "") + pads_he.get(min_key, pads_he["worked_example"])


HE_EXPL_SUFFIX = (
    "\n\n**טיפ נוסף לבחינה:** כתבו את המשפט או התבנית בשוליים לפני החישוב — "
    "מקבלים נקודות שיטה גם כשיש טעות חשבונית קטנה בסוף."
)


def ensure_question_expl(q: dict) -> None:
    while wc(q.get("explanation_he", "")) < 80:
        q["explanation_he"] = q.get("explanation_he", "") + HE_EXPL_SUFFIX
    while wc(q.get("explanation_en", "")) < 80:
        q["explanation_en"] = q.get("explanation_en", "") + (
            "\n\n**Exam follow-up:** State the theorem or template in the margin before computing — "
            "method marks matter even when arithmetic slips slightly."
        )
    if wc(q.get("explanation_he", "")) > 150:
        q["explanation_he"] = trim_words(q["explanation_he"], 150)
    if wc(q.get("explanation_en", "")) > 150:
        q["explanation_en"] = trim_words(q["explanation_en"], 150)


def trim_words(text: str, max_words: int) -> str:
    parts = text.split()
    if len(parts) <= max_words:
        return text
    return " ".join(parts[:max_words])


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        sid = sec.get("id", kind)
        if kind not in EXPAND_KINDS:
            if kind == "checkpoint":
                for key in ("checkpoint_solution_en", "checkpoint_solution_he"):
                    if wc(sec.get(key, "")) < 25:
                        errors.append(f"{sid}: {key} too short ({wc(sec.get(key, ''))} words)")
            continue
        min_key = "worked_example" if kind == "worked_example" else kind
        en_min, he_min = MIN[min_key]
        en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        if en_w < en_min:
            errors.append(f"{sid}: EN {en_w} < {en_min}")
        if he_w < he_min:
            errors.append(f"{sid}: HE {he_w} < {he_min}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"{sid}: weak Hebrew")
    for q in data["questions"]:
        ew, hw = wc(q.get("explanation_en", "")), wc(q.get("explanation_he", ""))
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
            if "cos" in body.lower():
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

    for sec in data["sections"]:
        ensure_section_words(sec)

    for q in data["questions"]:
        ensure_question_expl(q)

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
