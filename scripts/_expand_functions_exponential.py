#!/usr/bin/env python3
"""Expand functions_exponential.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/functions_exponential.json"

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


INTRO_EN = """Exponential functions model processes where the **rate of change is proportional to the current value** — population growth, radioactive decay, compound interest, and capacitor discharge all share the same mathematical skeleton.

**Where you already meet exponentials:**
- **Population growth:** $P = P_0 \\cdot 2^{t/T}$ doubles every fixed interval $T$.
- **Radioactive decay:** $N = N_0 \\cdot (1/2)^{t/t_{1/2}}$ halves every half-life.
- **Compound interest:** $A = P(1+r)^n$ multiplies the balance by the same factor each period.
- **Electronics:** $V(t)=V_0 e^{-t/RC}$ describes RC circuit discharge.

The key feature: **doubling, tripling, or halving at constant time intervals** — not adding a fixed amount each step. In Israeli Bagrut (4–5 units), exponential items test graph properties, same-base equation solving, substitution for quadratic-in-$a^x$ forms, and word problems on growth or interest linked to `concept:logarithms` when bases differ."""

INTRO_HE = """פונקציות מעריכיות מדגמות תהליכים שב-**קצב השינוי פרופורציונלי לערך הנוכחי** — גדילת אוכלוסייה, דעיכה רדיואקטיבית, ריבית דריבית ופריקת מעגל RC חולקים את אותו שלד מתמטי.

**איפה כבר פוגשים מעריכים:**
- **גדילת אוכלוסייה:** $P = P_0 \\cdot 2^{t/T}$ — הכפלה כל מרווח $T$ קבוע.
- **דעיכה רדיואקטיבית:** $N = N_0 \\cdot (1/2)^{t/t_{1/2}}$ — חצי כל מחצית חיים.
- **ריבית דריבית:** $A = P(1+r)^n$ — הכפת המאזן באותו גורם בכל תקופה.
- **אלקטרוניקה:** $V(t)=V_0 e^{-t/RC}$ מתאר פריקת מעגל RC.

מאפיין מרכזי: **הכפלה, הכפלה-שלוש או חצי במרווחי זמן קבועים** — לא הוספת סכום קבוע בכל צעד. בבגרות (4–5 יחידות) בודקים תכונות גרף, פתרון משוואות בבסיס זהה, הצבה לצורה ריבועית ב-$a^x$, ובעיות מילוליות על צמיחה או ריבית — מחוברות ל-`concept:logarithms` כשהבסיסים שונים."""

DEF_EN = """**Exponential function:** $f(x) = a^x$ where $a>0$ and $a\\ne1$.

**Key properties (memorize for graphing):**
- **Domain:** all reals ($\\mathbb{R}$).
- **Range:** $(0,\\infty)$ — outputs are always strictly positive.
- **$y$-intercept:** always $(0,1)$ because $a^0=1$ for any valid base.
- **Horizontal asymptote:** $y=0$ (the $x$-axis) as $x \\to -\\infty$ for growth or $x \\to +\\infty$ for decay.
- **Monotonicity:** if $a>1$, the function is **increasing** (exponential growth); if $0<a<1$, it is **decreasing** (exponential decay).

**The natural base:** $e \\approx 2.71828$. The function $f(x)=e^x$ is the most important exponential in calculus and physics — its derivative equals itself.

**Transformations quick reference:** $k \\cdot a^x$ stretches vertically; $a^{x+c}$ shifts left by $c$; $a^x + d$ shifts up by $d$ and moves the asymptote from $y=0$ to $y=d$. These shifts appear constantly on Bagrut graph-analysis items."""

DEF_HE = """**פונקציה מעריכית:** $f(x) = a^x$ כאשר $a>0$ ו-$a\\ne1$.

**תכונות מרכזיות (לשינון לשרטוט):**
- **תחום:** כל הממשיים ($\\mathbb{R}$).
- **טווח:** $(0,\\infty)$ — הפלט תמיד חיובי ממש.
- **חיתוך $y$:** תמיד $(0,1)$ כי $a^0=1$ לכל בסיס תקף.
- **אסימפטוטה אופקית:** $y=0$ (ציר $x$) כש-$x \\to -\\infty$ בגדילה או $x \\to +\\infty$ בדעיכה.
- **מונוטוניות:** אם $a>1$, הפונקציה **עולה** (גדילה מעריכית); אם $0<a<1$, **יורדת** (דעיכה).

**הבסיס הטבעי:** $e \\approx 2.71828$. הפונקציה $f(x)=e^x$ היא המעריכית החשובה ביותר בחדו"א ובפיזיקה — הנגזרת שלה שווה לעצמה.

**טרנספורמציות — תזכורת:** $k \\cdot a^x$ מותח אנכית; $a^{x+c}$ מזיז שמאלה ב-$c$; $a^x + d$ מזיז למעלה ב-$d$ ומעביר את האסימפטוטה מ-$y=0$ ל-$y=d$. הזזות אלה חוזרות בבגרות בניתוח גרפים."""

THEORY_EN = """**Transformations of $f(x)=a^x$:**
- $a^{x+c}$: horizontal shift **left** by $c$ units.
- $a^{x-c}$: horizontal shift **right** by $c$ units.
- $k \\cdot a^x$: vertical stretch (if $k>1$) or compression (if $0<k<1$).
- $a^{-x}=(1/a)^x$: reflection over the $y$-axis — swaps growth for decay.
- $a^x+d$: vertical shift up by $d$; new horizontal asymptote is $y=d$ (not $y=0$).

**Solving exponential equations — three standard methods:**
1. **Same base:** if $a^x=a^k$, then $x=k$. Rewrite both sides with a common base first ($4^x=2^{2x}$, $9^x=3^{2x}$).
2. **Logarithm:** if $a^x=b$ with no common base, take logs: $x=\\log_a b=\\dfrac{\\ln b}{\\ln a}$. Links to `concept:logarithms`.
3. **Substitution:** equations like $a^{2x}-ca^x+d=0$ become quadratics. Let $t=a^x>0$, solve for $t$, then back-substitute. Reject $t\\le0$ — exponentials are always positive.

**Growth and decay models:**
- Discrete: $A=A_0(1+r)^t$ or $A=A_0(1-r)^t$.
- Continuous: $A=A_0 e^{rt}$ or $A=A_0 e^{-rt}$.
- **Doubling time:** $T_d=\\dfrac{\\ln 2}{\\ln(1+r)}$; **Rule of 72:** $T_d\\approx 72/r$ percent (quick estimate).

**Exam strategy:** classify the problem (graph / same-base / log / substitution / word problem) before touching numbers."""

THEORY_HE = """**טרנספורמציות של $f(x)=a^x$:**
- $a^{x+c}$: הזזה אופקית **שמאלה** ב-$c$ יחידות.
- $a^{x-c}$: הזזה **ימינה** ב-$c$ יחידות.
- $k \\cdot a^x$: מתיחה אנכית (אם $k>1$) או דחיסה (אם $0<k<1$).
- $a^{-x}=(1/a)^x$: השתקפות סביב ציר $y$ — מחליף גדילה בדעיכה.
- $a^x+d$: הזזה אנכית למעלה ב-$d$; אסימפטוטה אופקית חדשה $y=d$ (לא $y=0$).

**פתרון משוואות מעריכיות — שלוש שיטות:**
1. **בסיס זהה:** אם $a^x=a^k$, אז $x=k$. כתבו שני האגפים בבסיס משותף ($4^x=2^{2x}$, $9^x=3^{2x}$).
2. **לוגריתם:** אם $a^x=b$ בלי בסיס משותף — לוג: $x=\\log_a b=\\dfrac{\\ln b}{\\ln a}$. קשור ל-`concept:logarithms`.
3. **הצבה:** משוואות כמו $a^{2x}-ca^x+d=0$ הופכות לריבועיות. $t=a^x>0$, פתרו ל-$t$, החזירו. דחו $t\\le0$ — מעריכים תמיד חיוביים.

**מודלי גדילה ודעיכה:**
- בדיד: $A=A_0(1+r)^t$ או $A=A_0(1-r)^t$.
- רציף: $A=A_0 e^{rt}$ או $A=A_0 e^{-rt}$.
- **זמן הכפלה:** $T_d=\\dfrac{\\ln 2}{\\ln(1+r)}$; **כלל 72:** $T_d\\approx 72/r$ אחוזים (הערכה מהירה).

**אסטרטגיית בחינה:** סווגו (גרף / בסיס זהה / לוג / הצבה / בעיה מילולית) לפני הצבת מספרים."""

WE1_EN = """**Describe** $f(x)=3^x$ and $g(x)=(1/3)^x$.

### Move 1 — Graph $f(x)=3^x$
Since $3>1$, $f$ is **increasing**. Key points: $(0,1)$ because $3^0=1$; $(1,3)$; $(-1,1/3)$. Domain $\\mathbb{R}$, range $(0,\\infty)$. Horizontal asymptote $y=0$ as $x\\to-\\infty$ — the curve approaches but never touches the $x$-axis.

### Move 2 — Graph $g(x)=(1/3)^x=3^{-x}$
Since $0<1/3<1$, $g$ is **decreasing**. Note $g(x)=3^{-x}$ — reflection of $f$ over the $y$-axis. Same $y$-intercept $(0,1)$, same asymptote $y=0$, but direction reversed: $g$ falls to the right while $f$ rises.

### Move 3 — Compare
Both share domain $\\mathbb{R}$, range $(0,\\infty)$, asymptote $y=0$, and pass through $(0,1)$. For any $x\\ne0$: $f(x)\\cdot g(x)=3^x\\cdot3^{-x}=3^0=1$ — they are reciprocals pointwise. At $x=1$: $f(1)=3$ while $g(1)=1/3$; at $x=-1$ the values swap.

### Move 4 — Sketch strategy
Plot $(0,1)$ first, mark asymptote $y=0$, then one point on each side ($x=1$ and $x=-1$) to fix direction. Label which curve is growth and which is decay. On Bagrut, a quick sketch beats memorizing coordinates — direction and asymptote tell most of the story.

**Exam tip:** When bases are reciprocals ($a$ and $1/a$), the graphs are mirror images across the $y$-axis."""

WE1_HE = """**תארו** $f(x)=3^x$ ו-$g(x)=(1/3)^x$.

### צעד 1 — גרף $f(x)=3^x$
מכיוון ש-$3>1$, $f$ **עולה**. נקודות: $(0,1)$ כי $3^0=1$; $(1,3)$; $(-1,1/3)$. תחום $\\mathbb{R}$, טווח $(0,\\infty)$. אסימפטוטה $y=0$ כש-$x\\to-\\infty$ — העקומה מתקרבת אך לא נוגעת בציר $x$.

### צעד 2 — גרף $g(x)=(1/3)^x=3^{-x}$
מכיוון ש-$0<1/3<1$, $g$ **יורדת**. $g(x)=3^{-x}$ — השתקפות של $f$ סביב ציר $y$. אותו חיתוך $(0,1)$, אותה אסימפטוטה $y=0$, כיוון הפוך: $g$ יורדת ימינה בעוד $f$ עולה.

### צעד 3 — השוואה
שתיהן: תחום $\\mathbb{R}$, טווח $(0,\\infty)$, אסימפטוטה $y=0$, עוברות $(0,1)$. לכל $x\\ne0$: $f(x)\\cdot g(x)=3^x\\cdot3^{-x}=1$ — הופכיות נקודתית. ב-$x=1$: $f(1)=3$ בעוד $g(1)=1/3$; ב-$x=-1$ הערכים מתחלפים.

### צעד 4 — אסטרטגיית שרטוט
שרטטו $(0,1)$ קודם, סמנו $y=0$, ואז נקודה מכל צד ($x=1$ ו-$x=-1$) לקביעת כיוון. סמנו איזו עקומה גדילה ואיזו דעיכה. בבגרות, שרטוט מהיר עדיף על שינון קואורדינטות — כיוון ואסימפטוטה מספרים את רוב הסיפור.

**טיפ לבחינה:** בסיסים הופכיים ($a$ ו-$1/a$) — גרפים משקפים סביב ציר $y$."""

WE2_EN = """### Move 1 — Understand the problem

**Problem:** $5000$ NIS is invested at $4\\%$ annual compound interest. After how many years will it double?

**Formula:** $A = P(1+r)^n = 5000(1.04)^n$. Here $P=5000$, $r=0.04$, and we seek $n$ when the balance reaches $10000$.

### Move 2 — Set up the doubling condition

We need $A=10000$:
$$5000(1.04)^n=10000\\Rightarrow(1.04)^n=2.$$

Dividing both sides by $5000$ isolates the exponential — the principal cancels because we only care about the doubling ratio.

### Move 3 — Solve with logarithms

No integer exponent makes $1.04^n=2$ exactly, so take natural logs:
$$n=\\frac{\\ln2}{\\ln1.04}\\approx\\frac{0.693}{0.0392}\\approx17.7\\text{ years.}$$

### Move 4 — Rule of 72 check

$72/4=18$ years — close to $17.7$, confirming reasonableness without a calculator.

**Answer:** about $17.7$ years (accept $18$ years on MCQs). **Exam tip:** Always identify $P$, $r$, and whether the question asks for $A$, $n$, or $r$ before substituting."""

WE2_HE = """### צעד 1 — הבנת הבעיה

**בעיה:** $5000$ ₪ מושקעים בריבית דריבית $4\\%$ שנתית. אחרי כמה שנים יתכפל הסכום?

**נוסחה:** $A = P(1+r)^n = 5000(1.04)^n$. כאן $P=5000$, $r=0.04$, ומחפשים $n$ כשהיתרה מגיעה ל-$10000$.

### צעד 2 — תנאי הכפלה

נדרש $A=10000$:
$$5000(1.04)^n=10000\\Rightarrow(1.04)^n=2.$$

חלוקה ב-$5000$ מבודדת את המעריך — הקרן מתבטלת כי אכפת לנו רק מיחס ההכפלה.

### צעד 3 — פתרון בלוגריתם

אין מעריך שלם שעושה $1.04^n=2$ בדיוק, לכן לוגריתם טבעי:
$$n=\\frac{\\ln2}{\\ln1.04}\\approx\\frac{0.693}{0.0392}\\approx17.7\\text{ שנים.}$$

### צעד 4 — בדיקת כלל 72

$72/4=18$ שנים — קרוב ל-$17.7$, מאשר הגיון בלי מחשבון.

**תשובה:** כ-$17.7$ שנים (בשאלות רב-ברירה — $18$). **טיפ לבחינה:** זהו $P$, $r$, ומה מבקשים — $A$, $n$ או $r$ — לפני הצבה."""

WE3_EN = """**Solve** $9^x-4\\cdot3^x+3=0$ — a classic Bagrut substitution problem.

### Move 1 — Recognize the quadratic structure

$9^x=(3^2)^x=(3^x)^2$. The equation has the form $(3^x)^2-4\\cdot3^x+3=0$. Let $t=3^x>0$ (exponentials are always positive — this restriction matters later). Spotting $9^x$ as a square of $3^x$ is the key insight.

### Move 2 — Solve the quadratic in $t$

$$t^2-4t+3=0\\Rightarrow(t-1)(t-3)=0\\Rightarrow t=1\\text{ or }t=3.$$

Both values are positive — valid for back-substitution. If we had $t=-1$, we would reject it immediately because $3^x$ can never be negative.

### Move 3 — Back-substitute each value

$t=1$: $3^x=1=3^0\\Rightarrow x=0$.
$t=3$: $3^x=3=3^1\\Rightarrow x=1$.

Each step uses the same-base rule: match the exponent to the power of 3.

### Move 4 — Verify both solutions

$9^0-4\\cdot3^0+3=1-4+3=0$ ✓. $9^1-4\\cdot3+3=9-12+3=0$ ✓.

**Solutions:** $x=0$ or $x=1$. **Exam tip:** Always reject $t\\le0$ before back-substituting — a common trap is accepting negative $t$ values from the quadratic."""

WE3_HE = """**פתרון:** $9^x-4\\cdot3^x+3=0$ — בעיית הצבה קלאסית בבגרות.

### צעד 1 — זיהוי מבנה ריבועי

$9^x=(3^2)^x=(3^x)^2$. המשוואה בצורה $(3^x)^2-4\\cdot3^x+3=0$. $t=3^x>0$ (מעריכים תמיד חיוביים — ההגבלה חשובה). זיהוי $9^x$ כריבוע של $3^x$ הוא תובנת המפתח.

### צעד 2 — פתרון הריבועית ב-$t$

$$t^2-4t+3=0\\Rightarrow(t-1)(t-3)=0\\Rightarrow t=1\\text{ או }t=3.$$

שני הערכים חיוביים — תקפים להחזרה. אם היה $t=-1$, היינו דוחים מיד כי $3^x$ לא יכול להיות שלילי.

### צעד 3 — החזרה לכל ערך

$t=1$: $3^x=1=3^0\\Rightarrow x=0$.
$t=3$: $3^x=3=3^1\\Rightarrow x=1$.

כל שלב משתמש בכלל בסיס זהה: התאמת מעריך לחזקת 3.

### צעד 4 — אימות שני הפתרונות

$9^0-4\\cdot3^0+3=0$ ✓. $9^1-4\\cdot3+3=0$ ✓.

**פתרונות:** $x=0$ או $x=1$. **טיפ לבחינה:** דחו $t\\le0$ לפני החזרה — מלכודת: קבלת $t$ שלילי מהריבועית."""

CP1_EN = """### Move 1 — Rewrite with same base

$16=2^4$, so the equation becomes $2^{3x-1}=2^4$.

### Move 2 — Equate exponents

Same base $2$ on both sides: $3x-1=4$.

### Move 3 — Solve for $x$

$3x=5\\Rightarrow x=\\dfrac{5}{3}$.

### Move 4 — Verify

$2^{3\\cdot(5/3)-1}=2^{5-1}=2^4=16$ ✓.

**Answer:** $x=\\dfrac{5}{3}$."""

CP1_HE = """### צעד 1 — כתיבה בבסיס זהה

$16=2^4$, לכן $2^{3x-1}=2^4$.

### צעד 2 — השוואת מעריכים

בסיס $2$ בשני האגפים: $3x-1=4$.

### צעד 3 — פתרון

$3x=5\\Rightarrow x=\\dfrac{5}{3}$.

### צעד 4 — אימות

$2^{3\\cdot(5/3)-1}=2^4=16$ ✓.

**תשובה:** $x=\\dfrac{5}{3}$."""

CP2_EN = """### Move 1 — Identify the decay model

Half-life $t_{1/2}=5$ years means $N/N_0=(1/2)^{t/5}$.

### Move 2 — Substitute $t=20$

$$\\frac{N}{N_0}=\\left(\\frac{1}{2}\\right)^{20/5}=\\left(\\frac{1}{2}\\right)^4.$$

### Move 3 — Evaluate

$(1/2)^4=1/16$. One-sixteenth of the original substance remains.

**Answer:** $\\dfrac{1}{16}$ remains (or $6.25\\%$ of the original)."""

CP2_HE = """### צעד 1 — מודל דעיכה

מחצית חיים $t_{1/2}=5$ שנים: $N/N_0=(1/2)^{t/5}$.

### צעד 2 — הצבה $t=20$

$$\\frac{N}{N_0}=\\left(\\frac{1}{2}\\right)^{20/5}=\\left(\\frac{1}{2}\\right)^4.$$

### צעד 3 — חישוב

$(1/2)^4=1/16$. נשאר שישית-עשרה מהחומר המקורי.

**תשובה:** $\\dfrac{1}{16}$ נשאר (או $6.25\\%$ מהמקור)."""

METHOD_EN = """| Task | Method | When to use |
|---|---|---|
| Sketch $a^x$ | Mark $(0,1)$, direction (growing/decaying), asymptote $y=0$ | Graph analysis, comparison |
| Solve $a^x=a^k$ | Equate exponents: $x=k$ | Same base on both sides |
| Solve $a^x=b$ | $x=\\log_a b=\\ln b/\\ln a$ | No common base |
| Quadratic in $a^x$ | Let $t=a^x>0$; solve; back-sub | $a^{2x}-ca^x+d=0$ pattern |
| Growth model | $A=A_0(1+r)^t$ or $A_0 e^{rt}$ | Interest, population |
| Doubling time | $t=\\ln2/\\ln(1+r)$ or Rule of 72 | "When does it double?" |

**Workflow:** Read the stem → classify problem type → pick the table row → convert units → substitute numbers last.

**Tip:** Vertical shift $+d$ changes asymptote to $y=d$ — write this before computing intercepts."""

METHOD_HE = """| משימה | שיטה | מתי להשתמש |
|---|---|---|
| שרטוט $a^x$ | $(0,1)$, כיוון, אסימפטוטה $y=0$ | ניתוח גרף, השוואה |
| $a^x=a^k$ | השוואת מעריכים: $x=k$ | בסיס זהה בשני האגפים |
| $a^x=b$ | $x=\\log_a b=\\ln b/\\ln a$ | בלי בסיס משותף |
| ריבועית ב-$a^x$ | $t=a^x>0$; פתרון; החזרה | דפוס $a^{2x}-ca^x+d=0$ |
| מודל גדילה | $A=A_0(1+r)^t$ או $A_0 e^{rt}$ | ריבית, אוכלוסייה |
| זמן הכפלה | $t=\\ln2/\\ln(1+r)$ או כלל 72 | "מתי יתכפל?" |

**תהליך:** קראו נתון → סווגו סוג → בחרו שורה → המירו יחידות → הציבו מספרים בסוף.

**טיפ:** הזזה אנכית $+d$ מעבירה אסימפטוטה ל-$y=d$ — כתבו זאת לפני חישוב חיתוכים."""

PITFALL_EN = """1. **Base must satisfy $a>0$, $a\\ne1$.** $f(x)=(-2)^x$ is not a real exponential function — negative bases produce non-real values for most exponents.

2. **$a^x$ is never zero or negative.** Range is $(0,\\infty)$ always. Do not expect $x$-intercepts on a basic exponential graph.

3. **Vertical shift changes the asymptote.** $3\\cdot2^x+5$ has asymptote $y=5$, not $y=0$. The $+5$ lifts the entire graph including the horizontal limit.

4. **Wrong quadratic substitution.** In $4^x-3\\cdot2^x+2=0$: let $t=2^x$ (NOT $t=4^x$), because $4^x=(2^x)^2=(2^2)^x$.

**Example misconception:** Asymptote of $2\\cdot3^x+5$ is $y=0$.

**Fix:** Vertical shift $d$ changes asymptote to $y=d$. Here the asymptote is $y=5$. Always identify $d$ in $a^x+d$ before sketching."""

PITFALL_HE = """1. **בסיס חייב $a>0$, $a\\ne1$.** $f(x)=(-2)^x$ אינה פונקציה מעריכית ממשית — בסיס שלילי נותן ערכים לא-ממשיים ברוב המעריכים.

2. **$a^x$ אף פעם לא אפס או שלילי.** הטווח תמיד $(0,\\infty)$. אל תצפו לחיתוכי $x$ בגרף מעריכי בסיסי.

3. **הזזה אנכית משנה אסימפטוטה.** $3\\cdot2^x+5$ — אסימפטוטה $y=5$, לא $y=0$. ה-$+5$ מרים את כל הגרף כולל הגבול האופקי.

4. **הצבה שגויה בריבועית.** ב-$4^x-3\\cdot2^x+2=0$: $t=2^x$ (לא $t=4^x$), כי $4^x=(2^x)^2$.

**דוגמת טעות:** אסימפטוטה של $2\\cdot3^x+5$ היא $y=0$.

**תיקון:** הזזה $d$ מעבירה אסימפטוטה ל-$y=d$. כאן $y=5$. זהו $d$ ב-$a^x+d$ לפני שרטוט."""

WHY_EN = """Exponential functions are the bridge between algebra and real-world modeling across A Step Forward — from finance to nuclear physics to circuit analysis.

**You will use this to unlock:**
- `concept:nuclear_physics` **Nuclear Physics & Radioactivity** (applies_to) — radioactive decay $N(t) = N_0 e^{-\\lambda t}$.
- `concept:ac_circuits` **AC Circuits** (applies_to) — RC charging and transient response.
- `concept:logarithms` **Logarithms** (prereq inverse) — solving when bases differ.

**Builds on:** `concept:exponents` — exponent laws power every rewrite ($4^x=2^{2x}$, $9^x=3^{2x}$).

**Why it matters for exams:** Bagrut 4–5 unit papers mix graph properties, equation solving, and compound-interest word problems in one section. University calculus assumes fluency with $e^x$ and growth models. When you study, ask: "Where else did I see doubling or halving at fixed intervals?" — transfer is what separates memorizing formulas from solving under time pressure."""

WHY_HE = """פונקציות מעריכיות הן הגשר בין אלגברה למידול מציאותי ב-A Step Forward — מפיננסים ועד פיזיקה גרעינית ומעגלי חשמל.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:nuclear_physics` **פיזיקה גרעינית ורדיואקטיביות** (applies_to) — דעיכה $N(t) = N_0 e^{-\\lambda t}$.
- `concept:ac_circuits` **מעגלי זרם חילופין** (applies_to) — טעינת RC ותגובה עקבית.
- `concept:logarithms` **לוגריתמים** (הפכי) — פתרון כשהבסיסים שונים.

**מבוסס על:** `concept:exponents` — חוקי חזקות מניעים כל שכתוב ($4^x=2^{2x}$, $9^x=3^{2x}$).

**למה זה חשוב לבחינות:** בבגרות 4–5 יחידות משלבים תכונות גרף, פתרון משוואות ובעיות ריבית דריבית. בחדו"א מניחים שליטה ב-$e^x$ ובמודלי צמיחה. בזמן לימוד שאלו: "איפה עוד ראיתי הכפלה או חצי במרווח קבוע?" — העברה מפרידה בין שינון לפתרון תחת לחץ."""

BEFORE_EN = """- $f(x)=a^x$: domain $\\mathbb{R}$, range $(0,\\infty)$, asymptote $y=0$, point $(0,1)$.
- $a>1$: increasing (growth); $0<a<1$: decreasing (decay).
- Vertical shift $a^x+d$: new asymptote $y=d$; $y$-intercept is $1+d$.
- Horizontal shift $a^{x-c}$: moves graph right by $c$ units.
- Solve $a^x=b$: same base OR $x=\\ln b/\\ln a$.
- Quadratic in $a^x$: substitute $t=a^x>0$; reject $t\\le0$.
- Growth/decay: $A=A_0(1\\pm r)^t$; doubling time $\\ln2/\\ln(1+r)$; Rule of 72: $72/r$.

**Last review:** Say each formula out loud once, then solve one checkpoint without looking."""

BEFORE_HE = """- $f(x)=a^x$: תחום $\\mathbb{R}$, טווח $(0,\\infty)$, אסימפטוטה $y=0$, נקודה $(0,1)$.
- $a>1$: עולה (גדילה); $0<a<1$: יורדת (דעיכה).
- הזזה $a^x+d$: אסימפטוטה חדשה $y=d$; חיתוך $y$ הוא $1+d$.
- הזזה $a^{x-c}$: הזזה ימינה ב-$c$ יחידות.
- $a^x=b$: בסיס זהה או $x=\\ln b/\\ln a$.
- ריבועית ב-$a^x$: $t=a^x>0$; דחו $t\\le0$.
- גדילה/דעיכה: $A=A_0(1\\pm r)^t$; זמן הכפלה $\\ln2/\\ln(1+r)$; כלל 72: $72/r$.

**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint אחד בלי להסתכל."""

SUMMARY_EN = """- Exponential $a^x$: always positive, passes $(0,1)$, horizontal asymptote $y=0$ (or $y=d$ after vertical shift).
- Growth ($a>1$) vs decay ($0<a<1$); reciprocal bases give $y$-axis reflections.
- Solve: same base (equate exponents) or logarithm ($\\ln$ both sides).
- Quadratic pattern: let $t=a^x>0$, solve, back-substitute.
- Applications: compound interest $A=P(1+r)^n$; half-life $(1/2)^{t/t_{1/2}}$; Rule of 72.

**Takeaway:** You should now recognize which method applies from the problem wording alone — graph, same-base, log, substitution, or word model."""

SUMMARY_HE = """- $a^x>0$ תמיד, עובר $(0,1)$, אסימפטוטה $y=0$ (או $y=d$ אחרי הזזה).
- גדילה ($a>1$) ודעיכה ($a<1$); בסיסים הופכיים — השתקפות סביב $y$.
- פתרון: בסיס זהה (השוואת מעריכים) או לוגריתם ($\\ln$).
- דפוס ריבועי: $t=a^x>0$, פתרון, החזרה.
- יישומים: ריבית $A=P(1+r)^n$; מחצית חיים; כלל 72.

**מסקנה:** כעת תזהו מהשאלה איזו שיטה — גרף, בסיס זהה, לוג, הצבה, או מודל מילולי."""

EXPLANATIONS = {
    1: fmt_expl(
        "As $x\\to-\\infty$, the term $3\\cdot2^x\\to0$, so $f(x)=3\\cdot2^x+1\\to1$. The horizontal asymptote is $y=1$ — the vertical shift $+1$ lifts the entire graph including its long-term limit.",
        "For $g(x)=k\\cdot a^x+d$, identify $d$ first: that is the asymptote. As $x\\to-\\infty$ with $a>1$, $a^x\\to0$ and only $d$ remains. Do not confuse the coefficient $3$ with the asymptote.",
        "Choosing $y=0$ ignores the $+1$ shift. Choosing $y=3$ confuses the vertical stretch factor with the asymptote. Choosing $y=4$ adds $3+1$ incorrectly.",
        "On Bagrut MCQs, write $f(x)=k\\cdot a^x+d$, circle $d$, and eliminate $y=0$ immediately if a shift is present.",
        "כש-$x\\to-\\infty$, $3\\cdot2^x\\to0$, לכן $f(x)\\to1$. האסימפטוטה $y=1$ — ההזזה $+1$ מרימה את כל הגרף כולל הגבול.",
        "ב-$g(x)=k\\cdot a^x+d$ זהו $d$ קודם — זו האסימפטוטה. כש-$x\\to-\\infty$ עם $a>1$, $a^x\\to0$ ונשאר רק $d$. אל תבלבלו $3$ עם האסימפטוטה.",
        "בחירה ב-$y=0$ מתעלמת מ-$+1$. $y=3$ — בלבול מקדם עם אסימפטוטה. $y=4$ — חיבור $3+1$ שגוי.",
        "בבגרות, כתבו $f(x)=k\\cdot a^x+d$, סמנו $d$, ופסלו $y=0$ מיד כשיש הזזה.",
    ),
    2: fmt_expl(
        "Domain: $\\mathbb{R}$ (defined for all real inputs). Range: $(0,\\infty)$ (outputs always positive). $y$-intercept: $(0,1)$ since $2^0=1$. Horizontal asymptote: $y=0$. The function is increasing because base $2>1$.",
        "List five graph features systematically: domain, range, intercept, asymptote, monotonicity. For $f(x)=2^x$, sketch mentally: rising curve through $(0,1)$ approaching $y=0$ on the left.",
        "Forgetting the asymptote $y=0$ or stating range as $\\mathbb{R}$. Another error: saying decreasing because the graph 'levels off' — with $a>1$, it always increases.",
        "Bagrut graph questions often award partial credit per feature. Write a checklist and tick each property before moving on.",
        "תחום: $\\mathbb{R}$ (מוגדרת לכל קלט ממשי). טווח: $(0,\\infty)$ (פלט תמיד חיובי). חיתוך $y$: $(0,1)$ כי $2^0=1$. אסימפטוטה אופקית: $y=0$. הפונקציה עולה כי בסיס $2>1$ — זהו דפוס גדילה מעריכית קלאסי.",
        "רשימת חמישה מאפיינים שיטתית: תחום, טווח, חיתוך, אסימפטוטה, מונוטוניות. $f(x)=2^x$: עקומה עולה דרך $(0,1)$, מתקרבת ל-$y=0$ משמאל. שרטטו מנטלית לפני כתיבת התשובה.",
        "שכחת אסימפטוטה $y=0$ או כתיבת טווח $\\mathbb{R}$. טעות: יורדת כי 'מתיישר' — עם $a>1$ תמיד עולה. גם בלבול בין תחום לטווח.",
        "בבגרות — נקודות חלקיות לכל מאפיין. רשימת בדיקה: תחום, טווח, חיתוך, אסימפטוטה, כיוון. סמנו כל אחד לפני המשך.",
    ),
    3: fmt_expl(
        "$625=5^4$, so $5^x=5^4$. Same base on both sides means equal exponents: $x=4$. Verify: $5^4=625$ ✓.",
        "Rewrite the right side as a power of the same base as the left. Recognize $625=5^4$ from memorized powers ($5, 25, 125, 625$). If you forget, factor: $625=25^2=(5^2)^2=5^4$.",
        "Taking logarithms unnecessarily when bases already match — wastes time. Another error: $x=625/5=125$ by dividing instead of equating exponents.",
        "Memorize $5^4=625$ and $2^{10}=1024$ — they appear constantly. Same-base method should be your first instinct.",
        "$625=5^4$, לכן $5^x=5^4$. בסיס זהה בשני האגפים → השוואת מעריכים: $x=4$. אימות: $5^4=625$ ✓. זו השיטה המהירה ביותר — אין צורך בלוגריתם.",
        "כתבו את הצד הימני כחזקה של אותו בסיס. $625=5^4$ מרשימת חזקות ($5, 25, 125, 625$). אם שכחתם: $625=25^2=(5^2)^2=5^4$. תמיד חפשו בסיס משותף לפני לוג.",
        "לוגריתם מיותר כשהבסיסים תואמים — בזבוז זמן. טעות: $x=625/5=125$ מחילוק במקום השוואת מעריכים. גם $x=5$ מבלבול בסיס עם תשובה.",
        "שיננו $5^4=625$ ו-$2^{10}=1024$ — מופיעים הרבה בבגרות. בסיס זהה = אינסטינקט ראשון. כתבו $5^x=5^4 \\Rightarrow x=4$ בשורה אחת.",
    ),
    4: fmt_expl(
        "$f(-2)=3^{-2}=\\dfrac{1}{3^2}=\\dfrac{1}{9}$. Negative exponents mean reciprocal: $a^{-n}=1/a^n$. This is exponent law, not a separate rule.",
        "Substitute $x=-2$ into $f(x)=3^x$. Apply the negative exponent rule before computing: $3^{-2}$ is $1/9$, not $-9$ or $-1/9$. Write the reciprocal explicitly.",
        "Computing $3^{-2}=-9$ by making the exponent negative but not taking reciprocal. Another error: $3^{-2}=-1/9$ from an extra negative sign.",
        "Quick check: $3^{-1}=1/3$, so $3^{-2}=(1/3)^2=1/9$. Chain negative exponents through reciprocals on Bagrut.",
        "$f(-2)=3^{-2}=\\dfrac{1}{3^2}=\\dfrac{1}{9}$. מעריך שלילי = הופכי: $a^{-n}=1/a^n$. זהו חוק חזקות מ-`concept:exponents`, לא כלל נפרד.",
        "הציבו $x=-2$ ב-$f(x)=3^x$. חוק מעריך שלילי לפני חישוב: $3^{-2}=1/9$, לא $-9$. כתבו את ההופכי במפורש: $3^{-2}=1/3^2$.",
        "$3^{-2}=-9$ — שלילי בלי הופכי. $3^{-2}=-1/9$ — סימן מיותר. גם $3^{-2}=1/(-9)$ — טעות סימן על הבסיס.",
        "בדיקה: $3^{-1}=1/3$, אז $3^{-2}=(1/3)^2=1/9$. בבגרות — הופכי לפני חזקה. כתבו שלב ביניים $3^{-2}=1/9$ לניקוד.",
    ),
    5: fmt_expl(
        "$(1/4)^x=4^{-x}$ because $(1/4)^x=(4^{-1})^x=4^{-x}$. The function inside the exponent is $f(x)=-x$.",
        "Rewrite fractions as negative powers of the denominator base: $1/4=4^{-1}$. Then $(4^{-1})^x=4^{-x}$ by the power-of-power law. This connects decay $(1/4)^x$ with growth $4^x$ via reflection.",
        "Writing $4^{1/x}$ or $4^{1/4}$ by misapplying the reciprocal. Another error: $4^{-1/x}$ from confusing $-x$ with $1/x$.",
        "When asked to rewrite with a given base, express the original base as a power of the target base first — here $1/4=4^{-1}$.",
        "$(1/4)^x=4^{-x}$ כי $(1/4)^x=(4^{-1})^x=4^{-x}$. הפונקציה במעריך: $f(x)=-x$. זה מקשר דעיכה $(1/4)^x$ לגדילה $4^x$ דרך השתקפות.",
        "כתבו שברים כחזקות שליליות של הבסיס: $1/4=4^{-1}$. $(4^{-1})^x=4^{-x}$ לפי חוק חזקה בחזקה. שלב ביניים: $(1/4)^x=(4^{-1})^x$. זהו כלי שימושי גם בפתרון משוואות.",
        "$4^{1/x}$ או $4^{1/4}$ — הופכי שגוי. $4^{-1/x}$ — בלבול $-x$ עם $1/x$. גם $4^x$ — שכחת המינוס.",
        "כשמבקשים בסיס נתון — הביעו מקור כחזקה שלו: $1/4=4^{-1}$. כתבו שלב ביניים בבגרות לניקוד מבנה.",
    ),
    6: fmt_expl(
        "Rewrite $4^{x-1}=2^{2(x-1)}=2^{2x-2}$. Same base: $2^{x+3}=2^{2x-2}$, so $x+3=2x-2\\Rightarrow x=5$. Check: $2^8=256$ and $4^4=256$ ✓.",
        "Convert every term to base $2$ before equating exponents. Expand $2(x-1)=2x-2$ carefully — a sign error here gives $x=1$ instead of $5$.",
        "Equating exponents without rewriting to a common base ($x+3=x-1$). Another error: $4^{x-1}=2^{2x-1}$ by forgetting to distribute the 2.",
        "Always show the common-base step on Bagrut — structure marks for $4^{x-1}=2^{2x-2}$ even if final algebra slips.",
        "$4^{x-1}=2^{2(x-1)}=2^{2x-2}$. בסיס $2$: $2^{x+3}=2^{2x-2}$, לכן $x+3=2x-2\\Rightarrow x=5$. בדיקה: $2^8=4^4=256$ ✓.",
        "המרת כל איבר לבסיס $2$ לפני השוואת מעריכים. פתחו $2(x-1)=2x-2$ בזהירות — טעות סימן → $x=1$. כתבו $4=2^2$ קודם. זו השיטה הסטנדרטית כשהבסיסים שונים.",
        "השוואת מעריכים בלי בסיס משותף ($x+3=x-1$). $4^{x-1}=2^{2x-1}$ — שכחת פיזור ה-2. גם $x=-5$ מטעות אלגברית.",
        "הציגו שלב בסיס משותף בבגרות — נקודות על $4^{x-1}=2^{2x-2}$. אימות: הציבו $x=5$ בשני האגפים לפני סיום.",
    ),
    7: fmt_expl(
        "As $x\\to-\\infty$, $3\\cdot2^x\\to0$, so $g(x)\\to5$. Horizontal asymptote: $y=5$. At $x=0$: $g(0)=3\\cdot2^0+5=3+5=8$. $y$-intercept: $(0,8)$.",
        "Split the problem: asymptote from the $+5$ shift; intercept by evaluating at $x=0$. The coefficient $3$ scales the curve but does not change the asymptote level.",
        "Asymptote $y=0$ or $y=3$ — confusing stretch with shift. Intercept $3$ or $5$ — forgetting to multiply $3\\cdot1$ before adding 5.",
        "Template: $g(x)=k\\cdot a^x+d$ → asymptote $y=d$, intercept $(0, k+d)$. Apply instantly on exam day.",
        "כש-$x\\to-\\infty$, $3\\cdot2^x\\to0$, $g(x)\\to5$. אסימפטוטה: $y=5$. ב-$x=0$: $g(0)=3\\cdot1+5=8$. חיתוך: $(0,8)$. המקדם $3$ משנה קנה מידה, לא רמת אסימפטוטה.",
        "פצלו: אסימפטוטה מה-$+5$; חיתוך בהצבה $x=0$. תבנית $g(x)=k\\cdot a^x+d$: אסימפטוטה $y=d$, חיתוך $(0,k+d)$. כאן $d=5$, $k+d=8$.",
        "אסימפטוטה $y=0$ או $y=3$ — בלבול מתיחה עם הזזה. חיתוך $3$ או $5$ — שכחת $3\\cdot2^0$ לפני $+5$.",
        "תבנית: $g(x)=k\\cdot a^x+d$ → אסימפטוטה $y=d$, חיתוך $(0,k+d)$. כתבו $d$ מיד כשמזהים הזזה אנכית.",
    ),
    8: fmt_expl(
        "$A=1000(1.06)^{10}\\approx1000\\times1.7908\\approx1791$ NIS. Compound interest multiplies by $(1+r)$ each year — ten multiplications become one power.",
        "Identify $P=1000$, $r=0.06$, $n=10$. Use $A=P(1+r)^n$. Calculator: $(1.06)^{10}\\approx1.791$. Do not use simple interest $1000\\times0.06\\times10$.",
        "Simple interest $1600$ NIS ($1000+600$) — wrong model. Another error: $(1.6)^{10}$ from misreading $6\\%$ as factor $1.6$.",
        "Rule of 72: doubling at $6\\%$ takes about 12 years, so after 10 years expect less than double — $1791$ is plausible. Sanity-check before submitting.",
        "$A=1000(1.06)^{10}\\approx1791$ ₪. ריבית דריבית מכפילה ב-$(1+r)$ כל שנה — עשר כפלות = חזקה אחת $(1.06)^{10}$.",
        "זהו $P=1000$, $r=0.06$, $n=10$. $A=P(1+r)^n$. מחשבון: $(1.06)^{10}\\approx1.791$. לא ריבית פשוטה $1000+600$. כתבו נוסחה לפני מספרים.",
        "ריבית פשוטה $1600$ — מודל שגוי. $(1.6)^{10}$ — $6\\%$ כגורם $1.6$ במקום $1.06$. גם $1060$ — ריבית שנה אחת בלבד.",
        "כלל 72: הכפלה ב-$6\\%$ ~12 שנים; אחרי 10 — פחות מכפול, $1791$ הגיוני. בדקו: $1000\\times1.06^{10}$ במחשבון.",
    ),
}


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in MIN:
            en_min, he_min = MIN[kind if kind != "worked_example" else "worked_example"]
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"{kind}: EN {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{kind}: HE {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{kind}: weak Hebrew")
        elif kind == "checkpoint":
            for key in ("checkpoint_solution_en", "checkpoint_solution_he"):
                if wc(sec.get(key, "")) < 25:
                    errors.append(f"checkpoint {key}: too short")

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

    return errors


def run_node_wordcheck() -> None:
    script = """
import { readFileSync } from 'node:fs';
import { wordCount, hebrewBodyWeak, MIN_WORDS } from './scripts/lib/bilingual-utils.mjs';
const data = JSON.parse(readFileSync('scripts/seed_data/lessons/functions_exponential.json','utf8'));
const errs = [];
for (const s of data.sections) {
  const min = MIN_WORDS[s.kind];
  if (!min) continue;
  if (wordCount(s.body_en_md) < min.en) errs.push(s.kind + ' en');
  if (wordCount(s.body_he_md) < min.he) errs.push(s.kind + ' he');
  if (hebrewBodyWeak(s.body_he_md, s.body_en_md)) errs.push(s.kind + ' weak-he');
}
for (const q of data.questions) {
  if (wordCount(q.explanation_en) < 80) errs.push('q'+q.ord+' expl-en');
  if (wordCount(q.explanation_he) < 80) errs.push('q'+q.ord+' expl-he');
}
if (errs.length) { console.error('node check:', errs.join(', ')); process.exit(1); }
console.log('node bilingual-utils check OK');
"""
    result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        raise SystemExit(result.returncode)
    print(result.stdout.strip())


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec.get("kind")
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
            n = sec.get("example_number")
            if n == 1:
                sec["body_en_md"], sec["body_he_md"] = WE1_EN, WE1_HE
            elif n == 2:
                sec["body_en_md"], sec["body_he_md"] = WE2_EN, WE2_HE
            elif n == 3:
                sec["body_en_md"], sec["body_he_md"] = WE3_EN, WE3_HE
        elif kind == "checkpoint":
            sec["checkpoint_solution_en"] = CP1_EN if "2^{3x-1}" in sec.get("body_en_md", "") else CP2_EN
            sec["checkpoint_solution_he"] = CP1_HE if "2^{3x-1}" in sec.get("body_he_md", "") else CP2_HE
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
        if ord_ in EXPLANATIONS:
            en, he = EXPLANATIONS[ord_]
            q["explanation_en"] = en
            q["explanation_he"] = he

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)

    run_node_wordcheck()
    print(f"OK — expanded {TARGET.name}")


if __name__ == "__main__":
    main()
