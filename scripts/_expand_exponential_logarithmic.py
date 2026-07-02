#!/usr/bin/env python3
"""Expand exponential_logarithmic.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/exponential_logarithmic.json"

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


INTRO = {
    "body_en_md": """Exponential and logarithmic functions are the **inverse pair** at the heart of 5-unit Bagrut math. The exponential $a^x$ models growth and decay — compound interest, radioactive half-life, population dynamics, Newton cooling — while $\\log_a x$ "undoes" exponentiation and turns multiplicative relationships into additive ones you can solve with algebra.

The natural base $e = \\lim_{n\\to\\infty}(1+1/n)^n \\approx 2.718$ arises in calculus because $(e^x)' = e^x$ and $\\ln x$ integrates to $1/x$. At the **5pt level**, exam writers expect you to: solve exponential and logarithmic equations (often 12–16 points combined), investigate graphs of $e^x$, $\\ln x$, and composites like $x\\ln x$, apply the growth/decay model $N(t)=N_0 e^{kt}$, and prove the landmark limit $\\lim_{x\\to\\infty} x^n/e^x = 0$, which shows exponential growth eventually dominates any polynomial.

This lesson connects directly to `concept:functions_exponential`, `concept:logarithms`, and later `concept:function_analysis_5pt`. Master the inverse identities $e^{\\ln x}=x$ and $\\ln(e^x)=x$ first — every equation-solving technique builds on them.""",
    "body_he_md": """פונקציות אקספוננציאליות ולוגריתמיות הן **זוג הפכיים** במרכז מתמטיקת 5 יחידות בבגרות. האקספוננציאל $a^x$ מדגם גדילה ודעיכה — ריבית דריבית, מחצית חיים רדיואקטיבית, דינמיקת אוכלוסייה, קירור ניוטון — בעוד $\\log_a x$ "מבטל" העלאה בחזקה והופך יחסים מכפליים ליחסים חיבוריים שפותרים באלגברה.

הבסיס הטבעי $e = \\lim_{n\\to\\infty}(1+1/n)^n \\approx 2.718$ עולה בחשבון כי $(e^x)' = e^x$ ו-$\\ln x$ מתאינטגר ל-$1/x$. ב**רמת 5 יח׳**, הבחינה מצפה: פתרון משוואות אקספוננציאליות ולוגריתמיות (לעיתים 12–16 נקודות יחד), חקירת גרפים של $e^x$, $\\ln x$ ורכיבות כמו $x\\ln x$, יישום מודל $N(t)=N_0 e^{kt}$, והוכחת הגבול $\\lim_{x\\to\\infty} x^n/e^x = 0$ — האקספוננציאל גובר בסוף על כל פולינום.

השיעור מחובר ל-`concept:functions_exponential`, `concept:logarithms` ול-`concept:function_analysis_5pt`. שלטו קודם בזהויות ההפכיות $e^{\\ln x}=x$ ו-$\\ln(e^x)=x$ — כל טכניקת פתרון משוואות נשענת עליהן.""",
}

DEFINITION = {
    "body_en_md": """**Exponential $a^x$** ($a>0$, $a\\neq 1$):
- Identity values: $a^0=1$, $a^1=a$.
- Laws: $a^{x+y}=a^x a^y$, $a^{x-y}=a^x/a^y$, $(a^x)^y=a^{xy}$.
- Monotonicity: strictly increasing if $a>1$; strictly decreasing if $0<a<1$.
- Graph: domain $\\mathbb{R}$, range $(0,\\infty)$, passes through $(0,1)$, horizontal asymptote $y=0$ as $x\\to-\\infty$ when $a>1$.

**Natural exponential:** $e^x$ with base $e\\approx 2.718$; derivative $(e^x)'=e^x$; inverse is $\\ln x$.

**Logarithm $\\log_a x$** ($a>0$, $a\\neq 1$): defined by $\\log_a x = c \\Leftrightarrow a^c = x$ for $x>0$.
- Product: $\\log_a(xy)=\\log_a x+\\log_a y$
- Quotient: $\\log_a(x/y)=\\log_a x-\\log_a y$
- Power: $\\log_a(x^r)=r\\log_a x$
- **Change of base:** $\\log_a x = \\dfrac{\\ln x}{\\ln a}$

Graph: domain $(0,\\infty)$, range $\\mathbb{R}$, passes through $(1,0)$, vertical asymptote $x=0$.

**Inverse pair (use constantly):** $\\ln(e^x)=x$ for all $x$; $e^{\\ln x}=x$ for $x>0$.

**Growth/decay model:** $N(t)=N_0 e^{kt}$. If $k>0$, exponential growth; if $k<0$, decay. Half-life: $t_{1/2}=\\ln 2/|k|$.""",
    "body_he_md": """**אקספוננציאל $a^x$** ($a>0$, $a\\neq 1$):
- ערכי זהות: $a^0=1$, $a^1=a$.
- חוקים: $a^{x+y}=a^x a^y$, $a^{x-y}=a^x/a^y$, $(a^x)^y=a^{xy}$.
- מונוטוניות: עולה ל-$a>1$; יורדת ל-$0<a<1$.
- גרף: תחום $\\mathbb{R}$, טווח $(0,\\infty)$, עובר ב-$(0,1)$, אסימטוטה $y=0$ כש-$x\\to-\\infty$ ל-$a>1$.

**אקספוננציאל טבעי:** $e^x$ עם בסיס $e\\approx 2.718$; נגזרת $(e^x)'=e^x$; ההפכי $\\ln x$.

**לוגריתם $\\log_a x$** ($a>0$, $a\\neq 1$): מוגדר $\\log_a x = c \\Leftrightarrow a^c = x$ עבור $x>0$.
- כפל: $\\log_a(xy)=\\log_a x+\\log_a y$
- חילוק: $\\log_a(x/y)=\\log_a x-\\log_a y$
- חזקה: $\\log_a(x^r)=r\\log_a x$
- **החלפת בסיס:** $\\log_a x = \\dfrac{\\ln x}{\\ln a}$

גרף: תחום $(0,\\infty)$, טווח $\\mathbb{R}$, עובר ב-$(1,0)$, אסימטוטה $x=0$.

**זוג הפכיים (שימוש תדיר):** $\\ln(e^x)=x$ לכל $x$; $e^{\\ln x}=x$ ל-$x>0$.

**מודל גדילה/דעיכה:** $N(t)=N_0 e^{kt}$. $k>0$ — גדילה; $k<0$ — דעיכה. מחצית חיים: $t_{1/2}=\\ln 2/|k|$.""",
}

THEORY = {
    "body_en_md": """**Type 1 — Same base:** $a^{f(x)}=a^{g(x)}$. Because $a^x$ is injective (one-to-one), equate exponents: $f(x)=g(x)$. This is the fastest path when both sides share a base like $2$, $3$, or $e$.

**Type 2 — Exponential equals constant:** $a^x=b$. Take $\\log_a$ of both sides: $x=\\log_a b = \\ln b/\\ln a$. When bases differ in $a^{f(x)}=b^{g(x)}$, take $\\ln$ of both sides and use the power law to collect $x$ terms.

**Type 3 — Log equals constant:** $\\log_a f(x)=c$ means $f(x)=a^c$. **Domain first:** every log argument must stay positive throughout.

**Type 4 — Sum of logs:** Combine with product/quotient laws, convert to exponential form, solve the resulting polynomial or quadratic. Always filter solutions against the domain.

**Quadratic substitution patterns:**
- $e^{2x}-ke^x+c=0$: let $u=e^x>0$, solve quadratic in $u$, then $x=\\ln u$.
- $\\ln^2 x - k\\ln x + c=0$: let $t=\\ln x$, solve quadratic; negative $t$ is allowed ($x\\in(0,1)$).
- $4^x-2^{x+1}-8=0$: rewrite $4^x=(2^x)^2$ and $2^{x+1}=2\\cdot 2^x$, then let $u=2^x$.

**The key limit (5pt proof):** $\\lim_{x\\to\\infty}\\dfrac{x^n}{e^x}=0$ for any fixed integer $n\\geq 1$. As $x\\to\\infty$, numerator and denominator both $\\to\\infty$ ($\\infty/\\infty$). Apply L'Hôpital $n$ times: each pass reduces the power of $x$ by 1 until the numerator is the constant $n!$ while $e^x\\to\\infty$, giving limit $0$. This justifies comparing growth rates in function analysis.""",
    "body_he_md": """**סוג 1 — אותו בסיס:** $a^{f(x)}=a^{g(x)}$. כי $a^x$ חד-ערכית, משווים מעריכים: $f(x)=g(x)$. זו הדרך המהירה כששני האגפים חולקים בסיס כמו $2$, $3$ או $e$.

**סוג 2 — אקספוננציאל שווה קבוע:** $a^x=b$. לוקחים $\\log_a$ משני האגפים: $x=\\log_a b = \\ln b/\\ln a$. כשהבסיסים שונים ב-$a^{f(x)}=b^{g(x)}$, $\\ln$ משני האגפים וחוק החזקה לאיסוף איברי $x$.

**סוג 3 — לוג שווה קבוע:** $\\log_a f(x)=c$ פירושו $f(x)=a^c$. **תחום קודם:** כל ארגומנט לוג חייב להישאר חיובי.

**סוג 4 — סכום לוגים:** מאחדים בחוקי כפל/חילוק, עוברים לצורה מעריכית, פותרים פולינום או ריבועית. תמיד מסננים לפי תחום.

**דפוסי הצבה ריבועית:**
- $e^{2x}-ke^x+c=0$: $u=e^x>0$, ריבועית ב-$u$, ואז $x=\\ln u$.
- $\\ln^2 x - k\\ln x + c=0$: $t=\\ln x$, ריבועית; $t$ שלילי מותר ($x\\in(0,1)$).
- $4^x-2^{x+1}-8=0$: $4^x=(2^x)^2$ ו-$2^{x+1}=2\\cdot 2^x$, ואז $u=2^x$.

**הגבול המפתח (הוכחת 5 יח׳):** $\\lim_{x\\to\\infty}\\dfrac{x^n}{e^x}=0$ לכל שלם $n\\geq 1$. כש-$x\\to\\infty$, מונה ומכנה $\\to\\infty$ ($\\infty/\\infty$). לופיטל $n$ פעמים: כל יישום מפחית חזקת $x$ ב-1 עד שהמונה הוא $n!$ ו-$e^x\\to\\infty$, ולכן הגבול $0$. זה מצדיק השוואת קצבי גדילה בחקירת פונקציות.""",
}

WE1 = {
    "body_en_md": """**Solve $2^{x+1} = 32$.**

When both sides of an exponential equation can be written with the **same base**, use injectivity: equal bases imply equal exponents. No logarithms are needed if you recognize $32$ as a power of $2$. This is the simplest and most reliable path on Bagrut when bases match.

### Move 1: Rewrite the right side as a power of $2$
$$32 = 2^5.$$
Memorizing $2^5=32$ and $2^{10}=1024$ saves time on Bagrut items.

### Move 2: Equate exponents (injectivity of $2^x$)
Since $2^a = 2^b \\Leftrightarrow a = b$:
$$x + 1 = 5 \\Rightarrow x = 4.$$

### Move 3: Verify
Substitute back: $2^{4+1} = 2^5 = 32$ ✓.

**Why this method:** Base-matching is faster and less error-prone than taking logs. Always scan whether the constant side is a perfect power of the base before reaching for $\\ln$. On Bagrut, this pattern often appears as the first step in a longer combined item.

**Answer:** $x = 4$.""",
    "body_he_md": """**פתרו $2^{x+1} = 32$.**

כששני אגפי משוואה אקספוננציאלית ניתנים לכתיבה ב**אותו בסיס**, משתמשים בחד-ערכיות: בסיסים שווים ⇒ מעריכים שווים. לא נדרשים לוגריתמים אם מזהים $32$ כחזקה של $2$. זו הדרך הפשוטה והאמינה ביותר בבגרות כשהבסיסים תואמים.

### צעד 1: כתיבת הצד הימני כחזקה של $2$
$$32 = 2^5.$$
שינון $2^5=32$ ו-$2^{10}=1024$ חוסך זמן בבחינת הבגרות.

### צעד 2: השוואת מעריכים (חד-ערכיות של $2^x$)
מכיוון ש-$2^a = 2^b \\Leftrightarrow a = b$:
$$x + 1 = 5 \\Rightarrow x = 4.$$

### צעד 3: בדיקה
הצבה: $2^{4+1} = 2^5 = 32$ ✓.

**למה השיטה:** התאמת בסיס מהירה ופחות מועדת לטעויות מ-$\\ln$. תמיד בדקו אם הצד הקבוע הוא חזקה שלמה של הבסיס לפני לוגריתם. בבגרות, דפוס זה מופיע לעיתים כשלב ראשון בפריט ארוך ומשולב יותר.

**תשובה:** $x = 4$.""",
}

WE2 = {
    "body_en_md": """**Solve $\\log_2(x) + \\log_2(x-2) = 3$.**

Log equations always start with **domain** — arguments must be positive before any algebra. This is a classic 5pt pattern: two logs with the same base summing to a constant, producing a quadratic after conversion to exponential form.

### Move 1: Domain restrictions
$x > 0$ and $x - 2 > 0$, so combined domain is $x > 2$.

### Move 2: Combine logs (product law, same base)
$$\\log_2 x + \\log_2(x-2) = \\log_2[x(x-2)] = 3.$$

### Move 3: Convert to exponential form
$$x(x-2) = 2^3 = 8.$$

### Move 4: Expand and solve the quadratic
$$x^2 - 2x - 8 = 0 \\Rightarrow (x-4)(x+2) = 0 \\Rightarrow x = 4 \\text{ or } x = -2.$$

### Move 5: Filter against domain
$x = -2 < 2$ is **rejected** ($\\log_2 x$ undefined). $x = 4 > 2$ ✓.

**Why domain comes first:** Without $x > 2$, combining logs is invalid. Even if algebra produces $x = -2$, discard it — the original logs do not exist there. Re-checking $\\log_2 4 + \\log_2 2 = 2 + 1 = 3$ confirms the survivor.

**Answer:** $x = 4$. Verify: $\\log_2 4 + \\log_2 2 = 2 + 1 = 3$ ✓.""",
    "body_he_md": """**פתרו $\\log_2(x) + \\log_2(x-2) = 3$.**

משוואות לוג מתחילות ב**תחום** — הארגומנטים חיוביים לפני כל אלגברה. דפוס קלאסי ב-5 יח׳: שני לוגים באותו בסיס שסכומם קבוע, וריבועית אחרי המרה לצורה מעריכית.

### צעד 1: הגבלות תחום
$x > 0$ וגם $x - 2 > 0$, לכן התחום המשולב: $x > 2$.

### צעד 2: איחוד לוגים (חוק כפל, אותו בסיס)
$$\\log_2 x + \\log_2(x-2) = \\log_2[x(x-2)] = 3.$$

### צעד 3: מעבר לצורה מעריכית
$$x(x-2) = 2^3 = 8.$$

### צעד 4: פתיחה ופתרון ריבועית
$$x^2 - 2x - 8 = 0 \\Rightarrow (x-4)(x+2) = 0 \\Rightarrow x = 4 \\text{ או } x = -2.$$

### צעד 5: סינון לפי תחום
$x = -2 < 2$ **נפסל** ($\\log_2 x$ לא מוגדר). $x = 4 > 2$ ✓.

**למה תחום קודם:** בלי $x > 2$, איחוד לוגים לא חוקי. גם אם האלגברה מייצרת $x = -2$, פוסלים — הלוגים המקוריים לא קיימים שם. בדיקה חוזרת: $\\log_2 4 + \\log_2 2 = 2 + 1 = 3$ מאשרת את השורש.

**תשובה:** $x = 4$. בדיקה: $\\log_2 4 + \\log_2 2 = 2 + 1 = 3$ ✓.""",
}

WE3 = {
    "body_en_md": """**Prove that $\\lim_{x\\to\\infty}\\dfrac{x^n}{e^x}=0$ for any fixed integer $n\\geq 1$.**

This limit is a **5pt signature result**: exponential growth eventually beats any polynomial. The proof uses L'Hôpital's rule repeatedly on the $\\infty/\\infty$ form.

### Move 1: Identify the indeterminate form
As $x\\to\\infty$: $x^n\\to\\infty$ and $e^x\\to\\infty$, so the expression is $\\infty/\\infty$.

### Move 2: Apply L'Hôpital $n$ times
Each differentiation reduces the power of $x$ in the numerator by 1 while the denominator stays $e^x$:
$$\\lim_{x\\to\\infty}\\frac{x^n}{e^x} \\stackrel{\\text{L'H}}{=} \\lim_{x\\to\\infty}\\frac{nx^{n-1}}{e^x} \\stackrel{\\text{L'H}}{=} \\cdots \\stackrel{\\text{L'H}}{=} \\lim_{x\\to\\infty}\\frac{n!}{e^x}.$$

### Move 3: Evaluate the final limit
Since $e^x\\to\\infty$, we have $\\dfrac{n!}{e^x}\\to 0$. $\\blacksquare$

**Conclusion:** No matter how large the degree $n$, $e^x$ grows faster. This supports comparing $e^x$ vs. $x^n$ in function analysis and justifies neglecting polynomial terms in long-run growth models.

**Exam note:** State the form ($\\infty/\\infty$), show at least two L'Hôpital steps explicitly, then write the constant-over-exponential conclusion.""",
    "body_he_md": """**הוכיחו $\\lim_{x\\to\\infty}\\dfrac{x^n}{e^x}=0$ לכל שלם $n\\geq 1$.**

הגבול הזה הוא **תוצאת חתימה ב-5 יח׳**: גדילה אקספוננציאלית גוברת בסוף על כל פולינום. ההוכחה משתמשת בכלל לופיטל שוב ושוב על צורת $\\infty/\\infty$.

### צעד 1: זיהוי צורה לא קבועה
כש-$x\\to\\infty$: $x^n\\to\\infty$ ו-$e^x\\to\\infty$, כלומר $\\infty/\\infty$.

### צעד 2: יישום לופיטל $n$ פעמים
כל גזירה מפחיתה חזקת $x$ במונה ב-1 בעוד המכנה נשאר $e^x$:
$$\\lim_{x\\to\\infty}\\frac{x^n}{e^x} \\stackrel{\\text{L'H}}{=} \\lim_{x\\to\\infty}\\frac{nx^{n-1}}{e^x} \\stackrel{\\text{L'H}}{=} \\cdots \\stackrel{\\text{L'H}}{=} \\lim_{x\\to\\infty}\\frac{n!}{e^x}.$$

### צעד 3: חישוב הגבול הסופי
מכיוון ש-$e^x\\to\\infty$, מתקבל $\\dfrac{n!}{e^x}\\to 0$. $\\blacksquare$

**מסקנה:** לא משנה כמה גדולה מעלת $n$, $e^x$ גדל מהר יותר. זה תומך בהשוואת $e^x$ מול $x^n$ בחקירת פונקציות ובהזנחת איברי פולינום במודלי גדילה ארוכי טווח.

**הערת בחינה:** ציינו את הצורה ($\\infty/\\infty$), הראו לפחות שני שלבי לופיטל במפורש, ואז כתבו מסקנת קבוע חלקי אקספוננציאל.""",
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": "Both sides share base $3$, so use injectivity after rewriting $27$ as a power of $3$.\n\n**Step 1:** $27 = 3^3$.\n\n**Step 2:** Equate exponents: $2x - 1 = 3$.\n\n**Step 3:** Solve: $2x = 4 \\Rightarrow x = 2$.\n\n**Check:** $3^{2\\cdot2 - 1} = 3^3 = 27$ ✓. **Answer:** $x = 2$.",
        "checkpoint_solution_he": "שני האגפים בבסיס $3$, ולכן משתמשים בחד-ערכיות אחרי כתיבת $27$ כחזקה של $3$.\n\n**שלב 1:** $27 = 3^3$.\n\n**שלב 2:** השוואת מעריכים: $2x - 1 = 3$.\n\n**שלב 3:** פתרון: $2x = 4 \\Rightarrow x = 2$.\n\n**בדיקה:** $3^{2\\cdot2 - 1} = 3^3 = 27$ ✓. **תשובה:** $x = 2$.",
    },
    {
        "checkpoint_solution_en": "Two natural logs summed — combine with the product law, then convert to exponential form. Domain is critical.\n\n**Domain:** $x + 1 > 0$ and $x - 1 > 0$, so $x > 1$.\n\n**Step 1:** $\\ln[(x+1)(x-1)] = \\ln 3$.\n\n**Step 2:** $(x+1)(x-1) = 3$, so $x^2 - 1 = 3$ and $x^2 = 4$.\n\n**Step 3:** $x = 2$ or $x = -2$; reject $x = -2$ since $x > 1$.\n\n**Check:** $\\ln 3 + \\ln 1 = \\ln 3$ ✓. **Answer:** $x = 2$.",
        "checkpoint_solution_he": "שני לוגים טבעיים בסכום — מאחדים בחוק כפל, ואז מעבר לצורה מעריכית. התחום קריטי.\n\n**תחום:** $x + 1 > 0$ ו-$x - 1 > 0$, לכן $x > 1$.\n\n**שלב 1:** $\\ln[(x+1)(x-1)] = \\ln 3$.\n\n**שלב 2:** $(x+1)(x-1) = 3$, כלומר $x^2 - 1 = 3$ ו-$x^2 = 4$.\n\n**שלב 3:** $x = 2$ או $x = -2$; פוסלים $x = -2$ כי $x > 1$.\n\n**בדיקה:** $\\ln 3 + \\ln 1 = \\ln 3$ ✓. **תשובה:** $x = 2$.",
    },
]

METHOD_GUIDE = {
    "body_en_md": """| Equation type | Method |\n|---|---|\n| $a^{f(x)}=a^{g(x)}$ | Set $f(x)=g(x)$ (injectivity) |\n| $a^x=b$ | $x=\\log_a b=\\ln b/\\ln a$ |\n| $\\log_a f(x)=c$ | $f(x)=a^c$; check domain first |\n| Sum of logs $=\\log$ or constant | Combine with product law, then equate |\n| $e^{2x}-ke^x+c=0$ | Let $u=e^x$; solve quadratic; $x=\\ln u$ |\n| $\\log^2 x - k\\log x + c=0$ | Let $t=\\log x$; solve quadratic |\n| Inequality $a^x>b$ | Same steps; flip inequality if $0<a<1$ |\n| Limit $x^n/e^x$ as $x\\to\\infty$ | L'Hôpital $n$ times → $n!/e^x\\to 0$ |\n\n**When to use:** Read the problem type first — base matching beats logarithms when possible. For log equations, write **domain** as line 1. For mixed-base exponentials, take $\\ln$ of both sides.\n\n**Exam tip:** On combined 12–16 pt items, graders award structure marks for domain statement, law application, and final verification even if arithmetic slips.""",
    "body_he_md": """| סוג משוואה | שיטה |\n|---|---|\n| $a^{f(x)}=a^{g(x)}$ | $f(x)=g(x)$ (חד-ערכיות) |\n| $a^x=b$ | $x=\\log_a b=\\ln b/\\ln a$ |\n| $\\log_a f(x)=c$ | $f(x)=a^c$; תחום קודם |\n| סכום לוגים = לוג/קבוע | איחוד בחוק כפל, ואז שוויון |\n| $e^{2x}-ke^x+c=0$ | $u=e^x$; ריבועית; $x=\\ln u$ |\n| $\\log^2 x - k\\log x + c=0$ | $t=\\log x$; ריבועית |\n| אי-שוויון $a^x>b$ | אותם שלבים; היפוך אם $0<a<1$ |\n| גבול $x^n/e^x$ כש-$x\\to\\infty$ | לופיטל $n$ פעמים → $n!/e^x\\to 0$ |\n\n**מתי להשתמש:** קראו קודם את סוג הבעיה — התאמת בסיס עדיפה על לוגריתם כשאפשר. במשוואות לוג, כתבו **תחום** בשורה 1. באקספוננציאל עם בסיסים שונים — $\\ln$ משני האגפים.\n\n**טיפ לבחינה:** בפריטים משולבים של 12–16 נק׳, הבודקים נותנים נקודות מבנה על הצהרת תחום, יישום חוק ואימות סופי גם אם יש טעות חישוב.""",
}

PITFALL = {
    "body_en_md": """1. **Forgetting domain on log equations** — every argument must stay $>0$. Write inequalities before combining logs; reject algebraically valid roots that violate them.

2. **Applying $\\ln$ to negative or zero** — $\\ln(-2)$ is undefined in the reals. If your quadratic gives $x=-1$ inside $\\log(x+3)$, discard it.

3. **$\\ln(a+b)\\neq\\ln a+\\ln b$** — the product law splits $\\ln(ab)$, not sums. This is the #1 law confusion on Bagrut.

4. **Power law vs. coefficient** — $\\log_a(x^r)=r\\log_a x$ applies to **powers inside** the argument, not to $\\log_a(rx)$.

5. **Quadratic substitution sign errors** — $u=e^x$ must be $>0$ always; reject negative $u$. But $t=\\ln x$ **can** be negative when $x\\in(0,1)$.

6. **L'Hôpital without $\\infty/\\infty$** — verify the form before differentiating; for $x^n/e^x$ as $x\\to\\infty$, state it explicitly.""",
    "body_he_md": """1. **שכחת תחום במשוואות לוג** — כל ארגומנט חייב להישאר $>0$. כתבו אי-שוויונות לפני איחוד; פסלו שורשים אלגבריים שמפרים אותם.

2. **$\ln$ על שלילי או אפס** — $\\ln(-2)$ לא מוגדר בממשיים. אם הריבועית נותנת $x=-1$ בתוך $\\log(x+3)$, פסלו.

3. **$\\ln(a+b)\\neq\\ln a+\\ln b$** — חוק הכפל מפצל $\\ln(ab)$, לא סכומים. זו טעות החוק #1 בבגרות.

4. **חוק חזקה מול מקדם** — $\\log_a(x^r)=r\\log_a x$ חל על **חזקות בפנים**, לא על $\\log_a(rx)$.

5. **טעויות סימן בהצבה ריבועית** — $u=e^x$ חייב $>0$ תמיד; $u$ שלילי נפסל. אבל $t=\\ln x$ **יכול** להיות שלילי כש-$x\\in(0,1)$.

6. **לופיטל בלי $\\infty/\\infty$** — ודאו את הצורה לפני גזירה; עבור $x^n/e^x$ כש-$x\\to\\infty$, ציינו במפורש.""",
}

WHY_MATTERS = {
    "body_en_md": """Exponential and logarithmic functions are not an isolated chapter — they are the language of **rates, scaling, and inversion** across the 5pt curriculum.

**Recommended next topics:**
- `concept:function_analysis_5pt` — investigate $e^x$, $\\ln x$, $x\\ln x$, and compare growth using $x^n/e^x\\to 0$.
- `concept:limits_5pt` — L'Hôpital proofs and asymptotic dominance.

**Why it matters for exams:** Bagrut rewards *transfer* — solving a cooling problem with $N(t)=N_0 e^{kt}$, then switching to a pure equation or limit in the same exam. When studying, ask: "Is this base-matching, log laws, substitution, or a limit proof?" Pattern recognition saves time under pressure.""",
    "body_he_md": """פונקציות אקספוננציאליות ולוגריתמיות אינן פרק מבודד — הן שפת **קצבים, קנה מידה והיפוך** בכל תוכנית 5 יח׳.

**נושאים מומלצים להמשך:**
- `concept:function_analysis_5pt` — חקירת $e^x$, $\\ln x$, $x\\ln x$, והשוואת גדילה עם $x^n/e^x\\to 0$.
- `concept:limits_5pt` — הוכחות לופיטל ודומיננטיות אסימטוטית.

**למה זה חשוב לבחינות:** בבגרות מעריכים *העברה* — פתרון בעיית קירור עם $N(t)=N_0 e^{kt}$, ואז מעבר למשוואה טהורה או גבול באותה בחינה. בלימוד, שאלו: "האם זו התאמת בסיס, חוקי לוג, הצבה, או הוכחת גבול?" זיהוי דפוס חוסך זמן תחת לחץ.""",
}

BEFORE_EXAM = {
    "body_en_md": """**Key formulas:**
- Log laws: product, quotient, power, change of base
- Inverse pair: $e^{\\ln x}=x$, $\\ln(e^x)=x$
- Derivatives: $(e^x)'=e^x$, $(\\ln x)'=1/x$
- Limit: $\\lim_{x\\to\\infty}x^n/e^x=0$ (L'Hôpital $n$ times)
- Growth/decay: $N(t)=N_0 e^{kt}$; half-life $t_{1/2}=\\ln2/|k|$

**Exam question types (5pt):**
1. Solve exponential equation (base match or $\\ln$) — ~4 pts
2. Solve logarithmic equation with domain check — ~6 pts
3. Quadratic in $e^x$ or $\\log x$ — ~8 pts
4. Application (growth/decay/half-life) — ~8 pts
5. Limit with $e^x$ (L'Hôpital) — ~6 pts

**Last-minute checklist:** domain line, verify roots, state indeterminate form before L'Hôpital.""",
    "body_he_md": """**נוסחאות מפתח:**
- חוקי לוג: כפל, חילוק, חזקה, החלפת בסיס
- זוג הפכיים: $e^{\\ln x}=x$, $\\ln(e^x)=x$
- נגזרות: $(e^x)'=e^x$, $(\\ln x)'=1/x$
- גבול: $\\lim x^n/e^x=0$ (לופיטל $n$ פעמים)
- גדילה/דעיכה: $N(t)=N_0 e^{kt}$; $t_{1/2}=\\ln2/|k|$

**סוגי שאלות (5 יח׳):**
1. משוואה אקספוננציאלית (התאמת בסיס או $\\ln$) — ~4 נק׳
2. משוואה לוגריתמית + תחום — ~6 נק׳
3. ריבועית ב-$e^x$ או $\\log x$ — ~8 נק׳
4. יישום (גדילה/דעיכה/מחצית חיים) — ~8 נק׳
5. גבול עם $e^x$ (לופיטל) — ~6 נק׳

**צ'ק-ליסט אחרון:** שורת תחום, אימות שורשים, ציון צורה לפני לופיטל.""",
}

SUMMARY = {
    "body_en_md": """- **Exponential $a^x$:** Domain $\\mathbb{R}$, range $(0,\\infty)$, passes $(0,1)$; injective — equal bases ⇒ equal exponents.
- **Logarithm $\\log_a x$:** Inverse of $a^x$; product, quotient, power, change-of-base laws; domain $(0,\\infty)$.
- **Natural pair $e^x$, $\\ln x$:** $(e^x)'=e^x$, $(\\ln x)'=1/x$; $e^{\\ln x}=x$, $\\ln(e^x)=x$.
- **Solving:** Base match, $\\ln$ both sides, log laws + exponential conversion, quadratic substitution; **always check domain**.
- **Key limit:** $\\lim_{x\\to\\infty}x^n/e^x=0$ — L'Hôpital $n$ times.
- **Applications:** $N(t)=N_0 e^{kt}$; half-life $t_{1/2}=\\ln2/|k|$.

**Takeaway:** Name the problem type from the decision table before calculating — structure earns exam marks.""",
    "body_he_md": """- **$a^x$:** תחום $\\mathbb{R}$, טווח $(0,\\infty)$, עובר $(0,1)$; חד-ערכית — בסיסים שווים ⇒ מעריכים שווים.
- **$\\log_a x$:** הפוכה של $a^x$; חוקי כפל, חילוק, חזקה, החלפת בסיס; תחום $(0,\\infty)$.
- **זוג $e^x$, $\\ln x$:** $(e^x)'=e^x$, $(\\ln x)'=1/x$; $e^{\\ln x}=x$, $\\ln(e^x)=x$.
- **פתרון:** התאמת בסיס, $\\ln$ משני האגפים, חוקי לוג + מעבר למעריך, הצבה ריבועית; **תמיד בדיקת תחום**.
- **גבול מפתח:** $\\lim x^n/e^x=0$ — לופיטל $n$ פעמים.
- **יישומים:** $N(t)=N_0 e^{kt}$; $t_{1/2}=\\ln2/|k|$.

**מסקנה:** זהו סוג הבעיה מטבלת ההחלטה לפני חישוב — מבנה מרוויח נקודות בבחינה.""",
}

EXPLANATIONS = {
    1: fmt_expl(
        "Rewrite $32 = 2^5$. Since $2^{x+1} = 2^5$ and $2^x$ is injective, equate exponents: $x+1=5$, so $x=4$. Option $x=4$ is correct.",
        "Scan whether the constant side is a perfect power of the base before taking logs. Here both sides are powers of $2$, so injectivity gives a one-step solution.",
        "Taking $\\log_2$ unnecessarily and making algebra errors, or solving $x+1=5$ as $x=6$. Option $x=3$ comes from $2^{x+1}=2^4$ misread.",
        "Memorize $2^5=32$ and $2^6=64$ — they appear in nearly every Bagrut exponential set. Always substitute back to verify.",
        "כותבים $32 = 2^5$. מכיוון ש-$2^{x+1} = 2^5$ ו-$2^x$ חד-ערכית, משווים מעריכים: $x+1=5$, ולכן $x=4$. אפשרות $x=4$ נכונה.",
        "בדקו אם הצד הקבוע הוא חזקה של הבסיס לפני לוגריתם. כאן שני האגפים חזקות של $2$, וחד-ערכיות נותנת פתרון בשלב אחד.",
        "לקיחת $\\log_2$ מיותרת וטעויות אלגברה, או $x+1=5$ → $x=6$. אפשרות $x=3$ מ-$2^{x+1}=2^4$ שגוי.",
        "שיננו $2^5=32$ ו-$2^6=64$ — הן חוזרות בכל סט אקספוננציאלי בבגרות. תמיד הציבו בחזרה לאימות.",
    ),
    2: fmt_expl(
        "The product law states $\\log_a(xy)=\\log_a x+\\log_a y$. The equation $\\log_a(xy)=\\log_a x+\\log_a y$ is the **product law**, not power, quotient, or change of base.",
        "Match the structure: **sum of logs** on one side corresponds to **log of a product**. Quotient law would involve subtraction; power law has a coefficient on the log.",
        "Choosing 'power law' because of exponents elsewhere in the problem, or 'change of base' whenever $\\ln$ appears — read the exact formula.",
        "On vocabulary items, rewrite each law in words: product → multiplication inside, quotient → division, power → exponent becomes coefficient.",
        "חוק הכפל קובע $\\log_a(xy)=\\log_a x+\\log_a y$. המשוואה $\\log_a(xy)=\\log_a x+\\log_a y$ היא **חוק המכפלה**, לא חזקה, מנה או החלפת בסיס.",
        "התאימו מבנה: **סכום לוגים** בצד אחד = **לוג של מכפלה**. חוק מנה — חיסור; חוק חזקה — מקדם על הלוג.",
        "בחירת 'חוק חזקה' בגלל חזקות במקום אחר, או 'החלפת בסיס' כש-$\\ln$ מופיע — קראו את הנוסחה המדויקת.",
        "בפריטי מינוח, נסחו כל חוק במילים: כפל → מכפלה בפנים, מנה → חילוק, חזקה → מעריך הופך למקדם.",
    ),
    3: fmt_expl(
        "Domain: $x>2$. Product law gives $\\log_2[x(x-2)]=3$, so $x(x-2)=8$, $x^2-2x-8=0$, $(x-4)(x+2)=0$. Only $x=4$ satisfies $x>2$.",
        "Start with domain, combine logs of the same base, convert to exponential ($=2^3$), solve quadratic, filter roots. This four-step template covers most 5pt log equations.",
        "Accepting $x=-2$ without domain check, or writing $\\log_2 x + \\log_2(x-2)=\\log_2(2x-2)$ by falsely adding arguments.",
        "Write 'domain: $x>2$' as line 1 — Bagrut rubrics award points even if the quadratic is wrong but domain is stated.",
        "תחום: $x>2$. חוק כפל: $\\log_2[x(x-2)]=3$, לכן $x(x-2)=8$, $x^2-2x-8=0$, $(x-4)(x+2)=0$. רק $x=4$ מקיים $x>2$.",
        "התחילו בתחום, איחדו לוגים באותו בסיס, עברו למעריך ($=2^3$), פתרו ריבועית, סננו שורשים. תבנית ארבע-שלבית זו מכסה רוב משוואות הלוג ב-5 יח׳.",
        "קבלת $x=-2$ בלי בדיקת תחום, או $\\log_2 x + \\log_2(x-2)=\\log_2(2x-2)$ — חיבור שגוי של ארגומנטים.",
        "כתבו 'תחום: $x>2$' בשורה 1 — בבגרות נותנים נקודות גם אם הריבועית שגויה אך התחום מצוין.",
    ),
    4: fmt_expl(
        "False. The correct product law is $\\ln(a\\cdot b)=\\ln a+\\ln b$. There is **no** log law that splits $\\ln(a+b)$ into a sum of logs. Counterexample: $\\ln(1+1)=\\ln 2\\neq 0=\\ln 1+\\ln 1$.",
        "Ask: is the operation inside the log **multiplication** or **addition**? Only multiplication splits into a sum of logs. Test with $a=b=1$: $\\ln(2)\\neq 0$.",
        "Students who recently practiced product law over-apply it to sums — a very common Bagrut trap in true/false items.",
        "If you see $\\ln(a+b)$ on an exam, leave it as is or use numerical estimation — never expand into $\\ln a+\\ln b$.",
        "לא נכון. חוק הכפל הנכון: $\\ln(a\\cdot b)=\\ln a+\\ln b$. **אין** חוק שמפצל $\\ln(a+b)$ לסכום לוגים. דוגמת נגד: $\\ln(1+1)=\\ln 2\\neq 0=\\ln 1+\\ln 1$.",
        "שאלו: הפעולה בתוך הלוג היא **כפל** או **חיבור**? רק כפל מתפצל לסכום. בדקו $a=b=1$: $\\ln(2)\\neq 0$ — זו בדיקה מהירה בכל שאלת נכון/לא נכון.",
        "תלמידים שתרגלו חוק כפל מיישמים אותו על סכומים — מלכודת נפוצה בשאלות נכון/לא נכון בבגרות 5 יח׳.",
        "אם רואים $\\ln(a+b)$ בבחינה — השאירו כמו שזה; לעולם אל תפתחו ל-$\\ln a+\\ln b$. כתבו דוגמת נגד $\\ln 2\\neq 0$ לקבלת נקודות הסבר.",
    ),
    5: fmt_expl(
        "As $x\\to\\infty$, $x^3/e^x$ is $\\infty/\\infty$. L'Hôpital three times: $3x^2/e^x \\to 6x/e^x \\to 6/e^x \\to 0$.",
        "Each L'Hôpital pass lowers the power of $x$ by 1 while $e^x$ stays. After $n$ passes for $x^n$, the numerator becomes $n!$ — a constant over an exploding exponential.",
        "Stopping after one L'Hôpital ($3x^2/e^x$ still $\\to\\infty$), or differentiating $e^x$ incorrectly. Some forget to state the indeterminate form.",
        "Show at least two explicit L'Hôpital steps on Bagrut — graders want the pattern, not just the final $0$.",
        "כש-$x\\to\\infty$, $x^3/e^x$ הוא $\\infty/\\infty$. לופיטל שלוש פעמים: $3x^2/e^x \\to 6x/e^x \\to 6/e^x \\to 0$.",
        "כל יישום לופיטל מוריד חזקת $x$ ב-1 בעוד $e^x$ נשאר. אחרי $n$ יישומים ל-$x^n$, המונה $n!$ — קבוע על אקספוננציאל שמתפוצץ.",
        "עצירה אחרי לופיטל אחד ($3x^2/e^x$ עדיין $\\to\\infty$), או גזירה שגויה של $e^x$. חלק שוכחים לציין צורה לא קבועה.",
        "הראו לפחות שני שלבי לופיטל מפורשים בבגרות — הבודקים רוצים את הדפוס, לא רק $0$ סופי.",
    ),
    6: fmt_expl(
        "Rewrite $64=2^6$. Since $2^{3x}=2^6$, injectivity gives $3x=6$, so $x=2$. Check: $2^{3\\cdot2}=2^6=64$.",
        "Same-base exponential: express the constant as a power of the base, then equate exponents. Faster than taking $\\log_2$ of both sides.",
        "Dividing $64$ by $2$ repeatedly instead of recognizing $2^6$, or solving $3x=6$ as $x=3$. Verify: $2^{6}=64$ ✓.",
        "Short-answer items expect the final value $x=2$ plus one line of reasoning — do not skip the base rewrite.",
        "כותבים $64=2^6$. מכיוון ש-$2^{3x}=2^6$, חד-ערכיות נותנת $3x=6$, ולכן $x=2$. בדיקה: $2^{3\\cdot2}=2^6=64$.",
        "אקספוננציאל באותו בסיס: כתבו הקבוע כחזקה של הבסיס, והשוו מעריכים. מהיר מ-$\\log_2$ משני האגפים — שלב אחד בלבד.",
        "חלוקת $64$ ב-$2$ שוב ושוב במקום $2^6$, או $3x=6$ → $x=3$. אימות: $2^{6}=64$ ✓. לפעמים שוכחים לבדוק.",
        "בתשובה קצרה — ערך סופי $x=2$ ושורת נימוק; אל תדלגו על כתיבת הבסיס. כתבו 'מכיוון ש-$2^{3x}=2^6$' לפני $x=2$.",
    ),
    7: fmt_expl(
        "By definition, $\\log_3 27 = c$ means $3^c = 27$. Since $3^3 = 27$, the answer is $3$. Verify: $3^3=27$ ✓.",
        "Convert log to exponential language: \"What power of $3$ gives $27$?\" Chain: $3\\to 9\\to 27$ in three multiplications.",
        "Answering $9$ (confusing with $\\sqrt{81}$) or $27/3=9$. Another error: using change of base when direct evaluation works.",
        "Memorize $3^4=81$, $3^3=27$ alongside powers of $2$ — they appear in combined log/exponential sections.",
        "לפי הגדרה, $\\log_3 27 = c$ פירושו $3^c = 27$. מכיוון ש-$3^3 = 27$, התשובה $3$. אימות: $3^3=27$ ✓.",
        "המירו לוג לשפה מעריכית: \"איזו חזקה של $3$ נותנת $27$?\" שרשרת: $3\\to 9\\to 27$ בשלושה כפלים. אין צורך במחשבון.",
        "תשובה $9$ (בלבול עם $\\sqrt{81}$) או $27/3=9$. טעות: החלפת בסיס כשחישוב ישיר מספיק — בזבוז זמן.",
        "שיננו $3^4=81$, $3^3=27$ יחד עם חזקות $2$ — הן מופיעות בפרקים משולבים. כתבו את שרשרת החזקות על הטיוטה.",
    ),
    8: fmt_expl(
        "$e^{\\ln 5}=5$ because $\\ln$ and $e^x$ are inverse functions: $\\ln$ undoes $e^x$, so composing them returns the original positive argument.",
        "When you see $e^{\\ln(\\text{something})}$, the answer is that **something** (provided it is $>0$). Similarly $\\ln(e^x)=x$ for all real $x$.",
        "Treating $\\ln 5$ as a factor to multiply: $e\\cdot\\ln 5$, or evaluating $\\ln 5$ on a calculator and rounding unnecessarily.",
        "Inverse-function simplifications are free points — recognize them before launching into log laws or change of base.",
        "$e^{\\ln 5}=5$ כי $\\ln$ ו-$e^x$ הם פונקציות הפוכות: $\\ln$ מבטל $e^x$, ולכן הרכבה מחזירה את הארגומנט החיובי המקורי.",
        "כש-$e^{\\ln(\\text{משהו})}$, התשובה היא **אותו משהו** (אם $>0$). כך $\\ln(e^x)=x$ לכל $x$ ממשי — שני כיווני ההפיכות שווים בחשיבות.",
        "טיפול ב-$\\ln 5$ כגורם לכפל: $e\\cdot\\ln 5$, או חישוב מחשבון מיותר. לפעמים כותבים $e^{1.609}$ במקום $5$.",
        "פישוטי הפיכות הם נקודות חינם — זהו אותם לפני חוקי לוג או החלפת בסיס. בבגרות, $e^{\\ln k}=k$ מופיע ליד משוואות מורכבות.",
    ),
}


def apply(data: dict) -> None:
    we_num = 0
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec.update(INTRO)
        elif kind == "definition":
            sec.update(DEFINITION)
        elif kind == "theory":
            sec.update(THEORY)
        elif kind == "worked_example":
            we_num += 1
            patch = {1: WE1, 2: WE2, 3: WE3}[we_num]
            sec["body_en_md"] = patch["body_en_md"]
            sec["body_he_md"] = patch["body_he_md"]
        elif kind == "checkpoint" and cp_idx < len(CHECKPOINTS):
            sec.update(CHECKPOINTS[cp_idx])
            cp_idx += 1
        elif kind == "method_guide":
            sec.update(METHOD_GUIDE)
        elif kind == "pitfall":
            sec.update(PITFALL)
        elif kind == "why_matters":
            sec.update(WHY_MATTERS)
        elif kind == "before_exam":
            sec.update(BEFORE_EXAM)
        elif kind == "summary":
            sec.update(SUMMARY)

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            en, he = EXPLANATIONS[ord_]
            q["explanation_en"] = en
            q["explanation_he"] = he


def validate(data: dict) -> list[str]:
    errors = []
    expand_kinds = set(MIN) | {"worked_example"}
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind not in expand_kinds:
            continue
        min_key = "worked_example" if kind == "worked_example" else kind
        en_min, he_min = MIN[min_key]
        en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        label = f"{kind}" + (f" ex{sec.get('example_number')}" if kind == "worked_example" else "")
        if en_w < en_min:
            errors.append(f"{label}: EN {en_w} < {en_min}")
        if he_w < he_min:
            errors.append(f"{label}: HE {he_w} < {he_min}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"{label}: weak Hebrew")

    for q in data["questions"]:
        ew, hw = wc(q.get("explanation_en", "")), wc(q.get("explanation_he", ""))
        if ew < 80 or ew > 150:
            errors.append(f"q{q['ord']} expl-en {ew} words")
        if hw < 80 or hw > 150:
            errors.append(f"q{q['ord']} expl-he {hw} words")
        if he_weak(q.get("explanation_he", ""), q.get("explanation_en", "")):
            errors.append(f"q{q['ord']} expl-he weak")

    return errors


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    apply(data)

    errors = validate(data)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        sys.exit(1)

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET.name}")

    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    if r.returncode != 0:
        sys.exit(r.returncode)
    if "207/207" not in r.stdout and "207" not in r.stdout:
        print("WARNING: expected 207/207 in dry-run output")
    print("OK — depth gates passed; seed-lessons dry-run passed.")


if __name__ == "__main__":
    main()
