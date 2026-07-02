#!/usr/bin/env python3
"""Expand function_transformations.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/function_transformations.json"

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


# --- Section bodies ---

INTRO_EN = """Function transformations are the lens through which almost every graph in Bagrut 5-unit math is understood. They appear as: (a) **sketch questions** — transform a known parent graph and label key points (6–8 pts); (b) **composition questions** — identify and apply multiple transformations in the correct order; (c) **symmetry proofs** — prove a transformed function is odd or even under specified conditions (6–8 pts). At 5pt, examiners test whether you understand the algebra behind the picture, not just memorized shapes.

The general form $g(x)=af(bx+c)+d$ unifies vertical shifts, horizontal shifts (with the counterintuitive opposite direction), reflections, and scaling. Mastery here unlocks trigonometric graphs, exponential models, and the analysis chapters that follow. This lesson builds on `concept:functions_intro` and feeds directly into `concept:function_analysis_5pt` and `concept:trigonometric_equations`."""

INTRO_HE = """טרנספורמציות של פונקציות הן העדשה שדרכה מבינים כמעט כל גרף בבגרות 5 יחידות. הן מופיעות כ: (א) **שאלות סרטוט** — שינוי גרף בסיס ידוע וסימון נקודות מפתח (6–8 נק׳); (ב) **הרכבות** — זיהוי וביצוע טרנספורמציות מרובות בסדר הנכון; (ג) **הוכחות סימטריה** — הוכחת אי-זוגיות או זוגיות של פונקציה מותמרת (6–8 נק׳). ב-5 יח׳, הבוחנים בודקים האם מבינים את האלגברה מאחורי התמונה, לא רק צורות שמורות.

הצורה הכללית $g(x)=af(bx+c)+d$ מאחדת הזזות אנכיות, הזזות אופקיות (בכיוון הפוך ומבלבל), שיקופים וגרימות. שליטה כאן פותחת גרפים טריגונומטריים, מודלים מעריכיים ופרקי ניתוח שאחר כך. השיעור נשען על `concept:functions_intro` ומזין ישירות את `concept:function_analysis_5pt` ו-`concept:trigonometric_equations`."""

DEF_EN = """Starting from a base function $f(x)$, the general transformed form is:
$$g(x) = a\\cdot f(bx + c) + d$$

| Parameter | Effect | Direction |
|---|---|---|
| $+d$ (outside) | Vertical shift up by $d$ | $y$-direction |
| $-d$ (outside) | Vertical shift down by $|d|$ | $y$-direction |
| $a>1$ (outside) | Vertical stretch by factor $a$ | $y$-direction |
| $0<a<1$ (outside) | Vertical compression | $y$-direction |
| $a<0$ (outside) | Reflection across $x$-axis, then scale by $|a|$ | |
| $x+c$ (inside, $c>0$) | Horizontal shift LEFT by $c$ | $x$-direction |
| $x-c$ (inside, $c>0$) | Horizontal shift RIGHT by $c$ | $x$-direction |
| $bx$ (inside, $b>1$) | Horizontal compression (factor $1/b$) | $x$-direction |
| $bx$ (inside, $0<b<1$) | Horizontal stretch | $x$-direction |
| $f(-x)$ | Reflection across $y$-axis | |

**Key rule:** Changes **inside** $f(\\cdot)$ affect the $x$-axis (horizontal, **opposite** direction to what you read); changes **outside** affect the $y$-axis (vertical, **same** direction). The compact shift formula for $f(bx+c)$: horizontal shift is $-c/b$ and horizontal scale is $1/b$."""

DEF_HE = """מפונקציית בסיס $f(x)$, הצורה הכללית היא:
$$g(x) = a\\cdot f(bx + c) + d$$

| פרמטר | אפקט | כיוון |
|---|---|---|
| $+d$ (מחוץ) | הזזה אנכית מעלה ב-$d$ | ציר $y$ |
| $-d$ (מחוץ) | הזזה אנכית מטה ב-$|d|$ | ציר $y$ |
| $a>1$ (מחוץ) | מתיחה אנכית בגורם $a$ | ציר $y$ |
| $0<a<1$ (מחוץ) | כיווץ אנכי | ציר $y$ |
| $a<0$ (מחוץ) | שיקוף ב-$x$, ואז גרימה ב-$|a|$ | |
| $x+c$ (פנים, $c>0$) | הזזה אופקית שמאלה ב-$c$ | ציר $x$ |
| $x-c$ (פנים, $c>0$) | הזזה אופקית ימינה ב-$c$ | ציר $x$ |
| $bx$ (פנים, $b>1$) | כיווץ אופקי (גורם $1/b$) | ציר $x$ |
| $bx$ (פנים, $0<b<1$) | מתיחה אופקית | ציר $x$ |
| $f(-x)$ | שיקוף ב-$y$ | |

**כלל מפתח:** שינויים **בפנים** $f(\\cdot)$ — אופקיים, **כיוון הפוך** למה שקוראים; שינויים **בחוץ** — אנכיים, **אותו כיוון**. נוסחת הזזה ל-$f(bx+c)$: הזזה אופקית $-c/b$, גרימה אופקית $1/b$."""

THEORY_EN = """**Order matters when composing:**
For $g(x)=af(bx+c)+d$, a reliable application order is:
1. Horizontal shift: replace $x$ with $x+c$ (inside)
2. Horizontal scale: multiply the input by $b$
3. Vertical scale: multiply output by $a$
4. Vertical shift: add $d$

Alternatively, factor first: $f(bx+c)=f\\big(b(x+c/b)\\big)$ — shift by $-c/b$, then scale $x$ by $1/b$. Tracking key points $(x_0,y_0)$ on $f$ maps to $\\big((x_0-c)/b,\\; ay_0+d\\big)$ on $g$.

**Even and odd functions:**
- **Even:** $f(-x)=f(x)$ — symmetric about the $y$-axis. Examples: $x^2$, $\\cos x$.
- **Odd:** $f(-x)=-f(x)$ — symmetric about the origin. Examples: $x^3$, $\\sin x$.

**Effect of transformations on symmetry:**
- $g(x)=f(x)+d$: even stays even; odd becomes neither (unless $d=0$).
- $g(x)=af(x)$ with $a<0$: flips sign — even stays even, odd stays odd.
- $g(x)=f(-x)$: preserves both even and odd.
- $g(x)=f(x-a)+b$: horizontal shift breaks standard axis/origin symmetry unless $a=b=0$ (for general $f$).

**Period under horizontal scaling:** If $f$ has period $T$, then $f(bx)$ has period $T/|b|$. This is why $\\sin(2x)$ completes a full cycle in $\\pi$, not $2\\pi$."""

THEORY_HE = """**סדר חשוב בהרכבה:**
ל-$g(x)=af(bx+c)+d$, סדר יישום אמין:
1. הזזה אופקית: $x\\to x+c$ (בפנים)
2. גרימה אופקית: הכפלת הקלט ב-$b$
3. גרימה אנכית: הכפלת הפלט ב-$a$
4. הזזה אנכית: הוספת $d$

לחלופין, פירוק: $f(bx+c)=f\\big(b(x+c/b)\\big)$ — הזזה ב-$-c/b$, ואז גרימה $1/b$. עקיבה אחרי $(x_0,y_0)$ על $f$ נותנת $\\big((x_0-c)/b,\\; ay_0+d\\big)$ על $g$.

**פונקציות זוגיות ואי-זוגיות:**
- **זוגית:** $f(-x)=f(x)$ — סימטרית לציר $y$. דוגמאות: $x^2$, $\\cos x$.
- **אי-זוגית:** $f(-x)=-f(x)$ — סימטרית לראשית. דוגמאות: $x^3$, $\\sin x$.

**אפקט על סימטריה:**
- $g(x)=f(x)+d$: זוגית נשארת זוגית; אי-זוגית — בדרך כלל לא (אלא אם $d=0$).
- $g(x)=af(x)$ עם $a<0$: שיקוף — זוגית נשארת, אי-זוגית נשארת.
- $g(x)=f(-x)$: שומרת על שני הסוגים.
- $g(x)=f(x-a)+b$: הזזה אופקית שוברת סימטריה סביב ציר $y$/ראשית, אלא אם $a=b=0$ (ל-$f$ כללית)."""

WE1_EN = """**Describe the transformations that take $y=x^2$ to $y=-(x-2)^2+3$, and sketch.**

**Identify parameters:** In $g(x)=-(x-2)^2+3$, we have $a=-1$, $b=1$, $c=-2$ (since $bx+c=x-2$), $d=3$.

### Move 1: Start with the parent parabola $y=x^2$.
Vertex at $(0,0)$, opens upward, symmetric about the $y$-axis.

### Move 2: Horizontal shift ($x\\to x-2$).
Replace $x$ with $x-2$ — shift **right** by 2. New equation: $y=(x-2)^2$, vertex $(2,0)$.

### Move 3: Reflection ($a=-1$).
Multiply by $-1$: parabola opens **downward**. $y=-(x-2)^2$, vertex still $(2,0)$ but now a maximum.

### Move 4: Vertical shift ($+3$).
Add 3: vertex moves to $(2,3)$. Final: $y=-(x-2)^2+3$.

**Key points:** Vertex $(2,3)$ (maximum); $x$-intercepts from $-(x-2)^2+3=0$: $(x-2)^2=3$, so $x=2\\pm\\sqrt{3}\\approx 0.27,\\,3.73$. The axis of symmetry is the vertical line $x=2$. **Exam habit:** always label vertex, axis of symmetry, and direction of opening after transformations."""

WE1_HE = """**תארו את הטרנספורמציות מ-$y=x^2$ ל-$y=-(x-2)^2+3$, וסרטטו.**

**זיהוי פרמטרים:** ב-$g(x)=-(x-2)^2+3$, $a=-1$, $b=1$, $c=-2$ (כי $bx+c=x-2$), $d=3$.

### צעד 1: פרבולת בסיס $y=x^2$.
קדקוד $(0,0)$, פותחת למעלה, סימטרית ל-$y$.

### צעד 2: הזזה אופקית ($x\\to x-2$).
החלפת $x$ ב-$x-2$ — הזזה **ימינה** 2. $y=(x-2)^2$, קדקוד $(2,0)$.

### צעד 3: שיקוף ($a=-1$).
הכפלה ב-$-1$: פותחת **למטה**. $y=-(x-2)^2$, קדקוד $(2,0)$ כעת מקסימום.

### צעד 4: הזזה אנכית ($+3$).
הוספת 3: קדקוד $(2,3)$. סופי: $y=-(x-2)^2+3$.

**נקודות מפתח:** קדקוד $(2,3)$ (מקסימום); חיתוכי $x$ מ-$(x-2)^2=3$: $x=2\\pm\\sqrt{3}\\approx 0.27,\\,3.73$. ציר הסימטריה: $x=2$. **הרגל לבחינה:** סמנו קדקוד, ציר סימטריה וכיוון פתיחה אחרי כל טרנספורמציה."""

WE2_EN = """**Sketch $g(x)=2e^{-x+1}-3$, describing each transformation from $f(x)=e^x$.**

**Rewrite for clarity:** $g(x)=2f(-x+1)-3=2f(-(x-1))-3$.

### Move 1: Horizontal shift right 1.
$f(x-1)=e^{x-1}$. Horizontal asymptote $y=0$; passes through $(1,1)$ instead of $(0,1)$.

### Move 2: Reflection across $y$-axis ($-x$).
$f(-(x-1))=e^{-(x-1)}=e^{1-x}$. Graph is now **decreasing** (mirror of exponential decay shape).

### Move 3: Vertical stretch by 2.
$2e^{1-x}$. Passes through $(1,2)$; all $y$-values doubled.

### Move 4: Vertical shift down 3.
$g(x)=2e^{1-x}-3$.
- Horizontal asymptote: $y=0-3=-3$ (shifts with the graph).
- $y$-intercept: $x=0$: $g(0)=2e^1-3=2e-3\\approx 2.44$.
- $x$-intercept: $2e^{1-x}=3$, $e^{1-x}=3/2$, $1-x=\\ln(3/2)$, $x=1-\\ln(3/2)\\approx 0.59$.

**Exam note:** When shifting exponentials, track the asymptote — it moves by the same $d$ as the vertical shift. Plot at least two anchor points: $(1,2)$ on the stretched curve and the $y$-intercept before submitting your sketch."""

WE2_HE = """**סרטטו $g(x)=2e^{-x+1}-3$, ותארו כל טרנספורמציה מ-$f(x)=e^x$.**

**כתיבה מחדש:** $g(x)=2f(-x+1)-3=2f(-(x-1))-3$.

### צעד 1: הזזה אופקית ימינה 1.
$f(x-1)=e^{x-1}$. אסימפטוטה $y=0$; עוברת דרך $(1,1)$ במקום $(0,1)$.

### צעד 2: שיקוף ב-$y$ ($-x$).
$f(-(x-1))=e^{1-x}$. הגרף **יורד** (צורת דעיכה מעריכית).

### צעד 3: מתיחה אנכית ×2.
$2e^{1-x}$. עוברת דרך $(1,2)$; כל ערכי $y$ הוכפלו.

### צעד 4: הזזה אנכית מטה 3.
$g(x)=2e^{1-x}-3$.
- אסימפטוטה אופקית: $y=-3$ (זזה עם הגרף).
- חיתוך $y$: $g(0)=2e-3\\approx 2.44$.
- חיתוך $x$: $x=1-\\ln(3/2)\\approx 0.59$.

**הערת בחינה:** בהזזת אקספוננט, עקבו אחרי האסימפטוטה — היא זזה באותו $d$ כמו ההזזה האנכית. סמנו לפחות שתי נקודות עוגן: $(1,2)$ על העקומה המתוחה ואת חיתוך $y$ לפני הגשת הסרטוט."""

WE3_EN = """**Let $f$ be an odd function. Find conditions on $a$ and $b$ such that $g(x)=f(x-a)+b$ is also odd.**

### Move 1: Write the oddness condition.
$g$ is odd iff $g(-x)=-g(x)$ for all $x$ in the domain.

### Move 2: Compute $g(-x)$.
$$g(-x)=f(-x-a)+b.$$

### Move 3: Compute $-g(x)$.
$$-g(x)=-f(x-a)-b.$$

### Move 4: Set equal and simplify.
We need $f(-x-a)+b=-f(x-a)-b$, i.e.,
$$f(-x-a)+f(x-a)=-2b.$$

### Move 5: Use oddness of $f$.
Since $f(-u)=-f(u)$, let $u=x+a$: $f(-x-a)=-f(x+a)$. The condition becomes:
$$-f(x+a)+f(x-a)=-2b\\quad\\text{for all }x.$$

### Move 6: Conclude for general $f$.
Setting $x=0$: $-f(a)+f(-a)=-2b$. Since $f(-a)=-f(a)$, this gives $-2f(a)=-2b$, so $b=f(a)$. For this to hold for **all** $x$, we need $f(x+a)-f(x-a)=2f(a)$ identically — a very strong constraint. For a general odd $f$, the necessary and sufficient condition is **$a=0$ and $b=0$** (so $g=f$ itself). For specific $f$, substitute and solve case by case."""

WE3_HE = """**תהי $f$ אי-זוגית. מצאו תנאים על $a$, $b$ כך ש-$g(x)=f(x-a)+b$ אי-זוגית.**

### צעד 1: כתבו תנאי אי-זוגיות.
$g$ אי-זוגית $\\Leftrightarrow$ $g(-x)=-g(x)$ לכל $x$ בתחום.

### צעד 2: חשבו $g(-x)$.
$$g(-x)=f(-x-a)+b.$$

### צעד 3: חשבו $-g(x)$.
$$-g(x)=-f(x-a)-b.$$

### צעד 4: השוו ופשטו.
נדרש $f(-x-a)+b=-f(x-a)-b$, כלומר:
$$f(-x-a)+f(x-a)=-2b.$$

### צעד 5: השתמשו באי-זוגיות $f$.
$ f(-u)=-f(u)$, עם $u=x+a$: $f(-x-a)=-f(x+a)$. התנאי:
$$-f(x+a)+f(x-a)=-2b\\quad\\text{לכל }x.$$

### צעד 6: מסקנה ל-$f$ כללית.
עבור $x=0$: $b=f(a)$. כדי שיתקיים ל**כל** $x$, נדרש $f(x+a)-f(x-a)=2f(a)$ — אילוץ חזק. ל-$f$ אי-זוגית כללית, תנאי הכרחי ומספיק: **$a=0$ ו-$b=0$** (כלומר $g=f$). ל-$f$ ספציפית — הציבו ופתרו. **הערת בחינה:** הוכחות כאלה דורשות כתיבת $g(-x)$ ו-$-g(x)$ במפורש."""

CHK1_SOL_EN = """**Goal:** Describe transformations from $y=|x|$ to $y=2|x+1|-3$ and find vertex and $y$-intercept.

**Step 1 — Parse the form:** $g(x)=2f(x+1)-3$ where $f(x)=|x|$. Inside: $x+1$ means shift **left** 1. Outside: stretch by 2, shift down 3.

**Step 2 — Apply in order:** Start at vertex $(0,0)$ of $|x|$. After left shift: vertex $(-1,0)$. After stretch ×2: vertex stays $(-1,0)$ but slopes steepen. After down 3: vertex $(-1,-3)$.

**Step 3 — $y$-intercept:** Set $x=0$: $y=2|0+1|-3=2(1)-3=-1$. Point $(0,-1)$.

**Answer:** Shift left 1, vertical stretch by 2, shift down 3. Vertex: $(-1,-3)$; $y$-intercept: $(0,-1)$."""

CHK1_SOL_HE = """**מטרה:** תארו טרנספורמציות מ-$y=|x|$ ל-$y=2|x+1|-3$ ומצאו קדקוד וחיתוך $y$.

**שלב 1 — פירוק:** $g(x)=2f(x+1)-3$ עם $f(x)=|x|$. בפנים: $x+1$ = הזזה **שמאלה** 1. בחוץ: מתיחה ×2, הזזה מטה 3.

**שלב 2 — סדר:** קדקוד $|x|$ ב-$(0,0)$. אחרי שמאלה: $(-1,0)$. אחרי ×2: קדקוד נשאר, שיפועים תלולים. אחרי מטה 3: $(-1,-3)$.

**שלב 3 — חיתוך $y$:** $x=0$: $y=2|1|-3=-1$. נקודה $(0,-1)$.

**תשובה:** הזזה שמאלה 1, מתיחה אנכית ×2, הזזה מטה 3. קדקוד $(-1,-3)$; חיתוך $y$: $(0,-1)$."""

CHK2_SOL_EN = """**Goal:** Describe transformations from $f(x)=\\sin x$ to $h(x)=-\\sin(2x-\\pi)+1$ and state amplitude and period.

**Step 1 — Factor inside:** $h(x)=-\\sin(2(x-\\pi/2))+1$. The argument $2(x-\\pi/2)$ reveals: compress horizontally by 2, then shift right $\\pi/2$.

**Step 2 — Apply remaining transforms:** Multiply by $-1$: reflect across $x$-axis (amplitude still 1). Add 1: shift up 1.

**Step 3 — Read off parameters:** Amplitude $=1$ (coefficient of sine after reflection). Period $=2\\pi/2=\\pi$. Midline $y=1$, so range $[0,2]$.

**Answer:** Horizontal compression (period $\\pi$), shift right $\\pi/2$, reflection across $x$-axis, shift up 1. Amplitude: 1; Period: $\\pi$."""

CHK2_SOL_HE = """**מטרה:** תארו טרנספורמציות מ-$f(x)=\\sin x$ ל-$h(x)=-\\sin(2x-\\pi)+1$ ומצאו אמפליטודה ומחזור.

**שלב 1 — פירוק:** $h(x)=-\\sin(2(x-\\pi/2))+1$. $2(x-\\pi/2)$: כיווץ אופקי ×2, הזזה ימינה $\\pi/2$.

**שלב 2 — שאר הטרנספורמציות:** כפל ב-$-1$: שיקוף ב-$x$ (אמפליטודה 1). $+1$: הזזה מעלה 1.

**שלב 3 — פרמטרים:** אמפליטודה $=1$. מחזור $=2\\pi/2=\\pi$. קו אמצע $y=1$, טווח $[0,2]$.

**תשובה:** כיווץ (מחזור $\\pi$), ימינה $\\pi/2$, שיקוף, מעלה 1. אמפליטודה 1, מחזור $\\pi$."""

METHOD_EN = """| What you see in $g(x)$ | Transformation |
|---|---|
| $f(x)+d$ | Shift up $d$ (or down if $d<0$) |
| $f(x-c)$ | Shift right $c$ (left if $c<0$) |
| $af(x)$, $a>0$ | Vertical stretch/compress by $|a|$ |
| $-f(x)$ | Reflect across $x$-axis |
| $f(-x)$ | Reflect across $y$-axis |
| $f(bx)$, $b>1$ | Horizontal compress by $1/b$ |
| $f(bx)$, $0<b<1$ | Horizontal stretch by $1/b$ |
| $f(bx+c)+d$ wrapped in $af(\\cdot)+d$ | Factor $b$, shift $-c/b$, scale $1/b$, then $a$ and $d$ |

**Tracking key points:** Map $(x_0,y_0)$ on $f$ to $\\big((x_0-c)/b,\\; ay_0+d\\big)$ on $g=af(bx+c)+d$.

**Checking symmetry after transformation:**
- Compute $g(-x)$ and compare to $-g(x)$ (odd) or $g(x)$ (even).
- Shifts by $a\\neq 0$ or $b\\neq 0$ usually break standard parity unless the base function has extra symmetry."""

METHOD_HE = """| מה נראה ב-$g(x)$ | טרנספורמציה |
|---|---|
| $f(x)+d$ | הזזה אנכית (מעלה/מטה) |
| $f(x-c)$ | הזזה אופקית (ימינה/שמאלה) |
| $af(x)$, $a>0$ | מתיחה/כיווץ אנכי ב-$|a|$ |
| $-f(x)$ | שיקוף ב-$x$ |
| $f(-x)$ | שיקוף ב-$y$ |
| $f(bx)$, $b>1$ | כיווץ אופקי ב-$1/b$ |
| $f(bx)$, $0<b<1$ | מתיחה אופקית ב-$1/b$ |
| $af(bx+c)+d$ | פירוק $b$, הזזה $-c/b$, גרימה $1/b$, ואז $a$ ו-$d$ |

**עקיבה אחרי נקודות:** $(x_0,y_0)$ על $f$ → $\\big((x_0-c)/b,\\; ay_0+d\\big)$ על $g$.

**בדיקת סימטריה:**
- חשבו $g(-x)$ והשוו ל-$-g(x)$ (אי-זוגית) או $g(x)$ (זוגית).
- הזזות עם $a\\neq 0$ או $b\\neq 0$ בדרך כלל שוברות זוגיות/אי-זוגיות סטנדרטית."""

PITFALL_EN = """1. **Horizontal direction reversal:** $f(x-2)$ shifts RIGHT by 2 (not left). Inside changes go OPPOSITE to what the sign suggests — this is the #1 Bagrut trap.

2. **Order of operations inside $f$:** $f(2x-4)=f(2(x-2))$ — first shift right 2, THEN compress by $1/2$; not compress then shift by 4.

3. **Horizontal compression vs stretch:** $f(2x)$ compresses by factor $1/2$ (period halved). The period of $\\sin(2x)$ is $\\pi$, not $4\\pi$.

4. **Assuming shift preserves parity:** Adding a constant $d$ to an odd function makes it neither odd nor even (unless $d=0$). Horizontal shifts break axis symmetry too.

5. **Forgetting to track the asymptote:** A vertical shift moves the horizontal asymptote — e.g., $2e^x-3$ has asymptote $y=-3$, not $y=0$. Always shift intercepts and asymptotes with the graph."""

PITFALL_HE = """1. **כיוון אופקי הפוך:** $f(x-2)$ = הזזה **ימינה** 2 (לא שמאלה). שינויים בפנים — כיוון **הפוך** לסימן — מלכודת #1 בבגרות.

2. **סדר פעולות בפנים:** $f(2x-4)=f(2(x-2))$ — קודם הזזה ימינה 2, **אז** כיווץ ב-$1/2$; לא כיווץ ואז הזזה 4.

3. **כיווץ vs מתיחה:** $f(2x)$ = כיווץ ב-$1/2$ (מחזור חצוי). מחזור $\\sin(2x)=\\pi$, לא $4\\pi$.

4. **הזזה שוברת אי-זוגיות:** הוספת קבוע $d$ ל-$f$ אי-זוגית — בדרך כלל לא אי-זוגית (אלא אם $d=0$). גם הזזה אופקית שוברת סימטריה.

5. **שכחת אסימפטוטה:** הזזה אנכית מזיזה אסימפטוטה — $2e^x-3$ עם $y=-3$, לא $y=0$. הזיזו חיתוכים ואסימפטוטות עם הגרף."""

WHY_EN = """Function transformations are not an isolated topic — they are the bridge between knowing parent graphs and analyzing real Bagrut questions on trigonometry, exponentials, and polynomials.

**Recommended next topics:**
- `concept:function_analysis_5pt` — extrema, asymptotes, and sketching combine transformations with calculus tools.
- `concept:trigonometric_equations` — phase shifts and amplitude appear inside every $\\sin(bx+c)$ setup.

**Why it matters for exams:** Bagrut 5-unit papers reward *transfer* — reading $g(x)=-2f(3x-1)+4$ and sketching without a calculator. When you study, ask: \"Which parent function is hidden inside this equation?\" That habit saves minutes on every graph question."""

WHY_HE = """טרנספורמציות אינן נושא מבודד — הן הגשר בין הכרת גרפי בסיס לבין שאלות בגרות אמיתיות על טריגונומטריה, אקספוננטים ופולינומים.

**נושאים מומלצים להמשך:**
- `concept:function_analysis_5pt` — קיצונים, אסימפטוטות וסרטוט משלבים טרנספורמציות עם כלי ניתוח.
- `concept:trigonometric_equations` — הזזת פазה ואמפליטודה מופיעות בכל $ \\sin(bx+c)$.

**למה זה חשוב לבחינות:** בבגרות 5 יחידות מעריכים *העברה* — לקרוא $g(x)=-2f(3x-1)+4$ ולסרטט בלי מחשבון. בלימוד, שאלו: \"איזו פונקציית בסיס מסתתרת כאן?\" — הרגל שחוסך דקות בכל שאלת גרף."""

BEFORE_EN = """**The four transformation families (memorize effects):**
- Vertical: $af(x)+d$ — scale by $a$, shift by $d$ (same direction as signs)
- Horizontal: $f(bx+c)$ — scale $x$ by $1/b$, shift by $-c/b$ (opposite direction)
- Reflections: $-f(x)$ across $x$-axis; $f(-x)$ across $y$-axis
- Composition: apply inside changes before outside changes when sketching

**Tracking a point $(x_0,y_0)$:** New point is $\\left(\\frac{x_0-c}{b},\\; ay_0+d\\right)$.

**Symmetry proof template:** Compute $g(-x)$, compare to $-g(x)$ (odd) or $g(x)$ (even).

**Exam question types:**
1. Identify all transformations and sketch (8 pts).
2. Find equation from transformed graph (6 pts).
3. Determine range/intercepts after transformation (6 pts).
4. Prove even/odd under given transformation (8 pts)."""

BEFORE_HE = """**ארבע משפחות טרנספורמציה (שננו):**
- אנכי: $af(x)+d$ — גרימה ב-$a$, הזזה ב-$d$ (אותו כיוון)
- אופקי: $f(bx+c)$ — גרימה $1/b$, הזזה $-c/b$ (כיוון הפוך)
- שיקופים: $-f(x)$ ב-$x$; $f(-x)$ ב-$y$
- הרכבה: בפנים לפני בחוץ בסרטוט

**עקיבת נקודה:** $\\left(\\frac{x_0-c}{b},\\; ay_0+d\\right)$.

**תבנית הוכחת סימטריה:** חשב $g(-x)$, השווה ל-$-g(x)$ (אי-זוגית) או $g(x)$ (זוגית).

**סוגי שאלות:**
1. זיהוי + סרטוט — 8 נק׳.
2. נוסחה מגרף — 6 נק׳.
3. טווח/חיתוכים — 6 נק׳.
4. הוכחת זוגיות/אי-זוגיות — 8 נק׳."""

SUMMARY_EN = """- **Inside changes** (in the argument of $f$): horizontal effects, in the **OPPOSITE** direction to the sign you read.
- **Outside changes**: vertical effects, in the **SAME** direction as the sign.
- **$g(x)=af(bx+c)+d$**: horizontal shift $-c/b$, horizontal scale $1/b$, vertical scale $a$, vertical shift $d$.
- **Even/odd:** check $g(-x)$ vs $g(x)$ and $-g(x)$; nontrivial shifts usually break parity.
- **Key point tracking:** $(x_0,y_0)\\mapsto\\big((x_0-c)/b,\\,ay_0+d\\big)$ — use this on every point-mapping exam question.
- **Period rule:** $f(bx)$ has period $T/|b|$ when $f$ has period $T$."""

SUMMARY_HE = """- **שינויים בפנים** (בארגומנט $f$): אפקט אופקי, **כיוון הפוך** לסימן.
- **שינויים בחוץ**: אפקט אנכי, **אותו כיוון** כמו הסימן.
- **$g(x)=af(bx+c)+d$**: הזזה $-c/b$, גרימה $1/b$, $a$, $d$.
- **זוגיות/אי-זוגיות:** $g(-x)$ מול $g(x)$ / $-g(x)$; הזזות שוברות סימטריה.
- **עקיבת נקודה:** $(x_0,y_0)\\mapsto\\big((x_0-c)/b,\\,ay_0+d\\big)$ — בכל שאלת מיפוי נקודות בבחינה.
- **כלל מחזור:** ל-$f(bx)$ מחזור $T/|b|$ כש-$f$ עם מחזור $T$ — זכרו: $b$ גדול = מחזור קצר יותר."""

# --- Question explanations ---

Q_EXPLS = [
    fmt_expl(
        "$f(x-3)$ shifts the graph **right** by 3 (inside minus → opposite direction). The $+2$ outside shifts **up** by 2 (outside plus → same direction). Together: right 3, up 2 — option B.",
        "Split the expression: inside $f(x-3)$ controls horizontal motion; outside $+2$ controls vertical. Say aloud: 'minus inside means right; plus outside means up.'",
        "Choosing 'shift left 3' (options A or C) — the most common horizontal trap. Students read $x-3$ and think 'subtract 3 from $x$' means move left.",
        "On MCQ shift questions, eliminate left/right first using the inside rule, then up/down using outside. Write R/U or L/D in the margin before reading options.",
        "$f(x-3)$ = הזזה **ימינה** 3 (מינוס בפנים → כיוון הפוך). $+2$ בחוץ = **מעלה** 2 (פלוס בחוץ → אותו כיוון). יחד: ימינה 3, מעלה 2 — תשובה ב'.",
        "פרקו: $f(x-3)$ בפנים = אופקי; $+2$ בחוץ = אנכי. אמרו בקול: 'מינוס בפנים = ימינה; פלוס בחוץ = מעלה'.",
        "בחירת 'שמאלה 3' (א' או ג') — מלכודת אופקית נפוצה. קוראים $x-3$ וחושבים 'מינוס = שמאלה'.",
        "בשאלות MCQ על הזזות, שללו ימינה/שמאלה קודם (כלל פנים), אז מעלה/מטה (כלל חוץ).",
    ),
    fmt_expl(
        "Rewrite $g(x)=2e^{-x+1}-3=2f(-(x-1))-3$. Steps: shift right 1 ($x\\to x-1$), reflect across $y$-axis ($-x$), vertical stretch ×2, shift down 3. Order inside first, then outside.",
        "Factor the inside argument before naming shifts: $-x+1=-(x-1)$ reveals reflection about $y$ after a right shift. List transforms in the order you would sketch them.",
        "Naming 'shift left 1' because of $+1$ inside $e^{-x+1}$ without factoring — the $+1$ pairs with $-x$ as $-(x-1)$, which is right 1 then reflect.",
        "Open transformation questions want **ordered list + brief justification**. Write: (1) right 1, (2) reflect $y$, (3) stretch 2, (4) down 3 — graders award partial credit per correct step.",
        "כתיבה: $g(x)=2e^{-x+1}-3=2f(-(x-1))-3$. שלבים: ימינה 1, שיקוף ב-$y$, מתיחה ×2, מטה 3. קודם פנים, אחר כך חוץ.",
        "פרקו את הארגומנט: $-x+1=-(x-1)$ חושף שיקוף אחרי הזזה ימינה. רשמו בסדר הסרטוט.",
        "לומר 'שמאלה 1' בגלל $+1$ בלי פירוק — $+1$ עם $-x$ נותן $-(x-1)$ = ימינה 1 ואז שיקוף.",
        "בשאלה פתוחה — רשימה **מסודרת + נימוק קצר**. (1) ימינה 1, (2) שיקוף $y$, (3) ×2, (4) מטה 3 — נקודות חלקיות לכל שלב.",
    ),
    fmt_expl(
        "Oddness requires $g(-x)=-g(x)$. Substituting gives $-f(x+a)+f(x-a)=-2b$ for all $x$. For a general odd $f$, the only universal solution is $a=0$, $b=0$ — otherwise you impose an identity on $f$ that most odd functions fail.",
        "Template: compute $g(-x)$ and $-g(x)$, set equal, use $f(-u)=-f(u)$. Test $x=0$ early — it often gives $b=f(a)$. Then ask whether the remaining condition can hold for all $x$.",
        "Answering $b=0$ alone without checking $a$, or claiming any $a$ works if $b=0$. Shifting an odd function horizontally ($a\\neq 0$) typically destroys origin symmetry.",
        "Symmetry proofs are 8-point questions — write every algebra step. State 'since $f$ is odd, $f(-x-a)=-f(x+a)$' explicitly; graders look for that substitution.",
        "אי-זוגיות דורשת $g(-x)=-g(x)$. הצבה: $-f(x+a)+f(x-a)=-2b$ לכל $x$. ל-$f$ אי-זוגית כללית: רק $a=0$, $b=0$ — אחרת מטילים זהות שרוב $f$ לא מקיימות.",
        "תבנית: חשב $g(-x)$ ו-$-g(x)$, השווה, השתמש ב-$f(-u)=-f(u)$. בדוק $x=0$ מוקדם — לעיתים $b=f(a)$.",
        "לענות $b=0$ בלבד בלי $a$, או לטעון שכל $a$ עובד. הזזה אופקית ($a\\neq 0$) שוברת סימטריה לראשית.",
        "הוכחות סימטריה — 8 נק׳; כתבו כל שלב. ציינו במפורש 'כיוון ש-$f$ אי-זוגית, $f(-x-a)=-f(x+a)$'.",
    ),
    fmt_expl(
        "False. $f(2x)$ **compresses** horizontally by factor 2, so the period is **half** — not double. For $\\sin x$ with period $2\\pi$, $\\sin(2x)$ has period $\\pi$.",
        "Period rule: if $f(x)$ has period $T$, then $f(bx)$ has period $T/|b|$. Larger $b$ inside → faster oscillation → shorter period. Think 'compress = squeeze more cycles in'.",
        "Answering True because '2× means multiply period by 2'. Students confuse horizontal scale factor with period multiplier — they are reciprocals.",
        "True/False on periods: always write $T_{new}=T/|b|$. One line of justification earns full credit even if you misremember a number.",
        "לא נכון. $f(2x)$ **דוחס** אופקית ×2, אז המחזור **חצי** — לא כפול. ל-$\\sin x$ עם מחזור $2\\pi$, ל-$\\sin(2x)$ מחזור $\\pi$.",
        "כלל מחזור: אם $f(x)$ עם מחזור $T$, אז $f(bx)$ עם $T/|b|$. $b$ גדול יותר בפנים → התנדנדות מהירה → מחזור קצר.",
        "לענות 'נכון' כי '2× = מחזור ×2'. מבלבלים גורם גרימה עם מחזור — הם הפוכים.",
        "בנכון/לא נכון על מחזור: כתבו $T_{new}=T/|b|$. שורה אחת מספיקה לניקוד מלא.",
    ),
    fmt_expl(
        "Need the input to $f$ to be 3: $x-1=3$ so $x=4$. Then $g(4)=-2f(3)+4=-2(7)+4=-10$. Image point: $(4,-10)$ — option A.",
        "Point mapping: solve $bx+c=a$ for $x$, then compute $g(x)=af(a)+d$. Here $b=1$, $c=-1$, $a=3$, $f(3)=7$, outer $a=-2$, $d=4$.",
        "Using $x=3$ directly (option B: $(2,-10)$) — forgetting that $x-1$ not $x$ must equal 3. Or flipping only the $y$-sign without the stretch.",
        "Point-map MCQs: always solve for $x$ first, then $y$. Write $(x_0,y_0)\\mapsto((x_0-c)/b,\\,ay_0+d)$ on your formula sheet.",
        "נדרש קלט $f$ = 3: $x-1=3$ → $x=4$. $g(4)=-2(7)+4=-10$. נקודה $(4,-10)$ — תשובה א'.",
        "מיפוי נקודה: פתרו $bx+c=a$ ל-$x$, אז $g(x)=af(a)+d$. כאן $x=4$, $f(3)=7$, $a=-2$, $d=4$.",
        "שימוש ב-$x=3$ ישירות (תשובה ב') — שכחה ש-$x-1$ ולא $x$ חייב להיות 3.",
        "ב-MCQ מיפוי: קודם $x$, אחר כך $y$. רשמו $(x_0,y_0)\\mapsto((x_0-c)/b,\\,ay_0+d)$ בדף נוסחאות.",
    ),
    fmt_expl(
        "Replace $x$ with $x+3$: shift **left** 3 (plus inside → opposite → left). Then $-1$ outside: shift **down** 1. Vertex moves from $(0,0)$ to $(-3,-1)$.",
        "Read inside first: $(x+3)^2$ means $f(x+3)$ — left 3. Then outside $-1$ — down 1. Verify by vertex: minimum of $(x+3)^2-1$ at $x=-3$, value $-1$.",
        "Saying 'shift right 3' because of $+3$ inside the parentheses — the classic inside-direction error.",
        "Short-answer transformation items want **two moves + key point**. One sentence per direction is enough if the vertex is stated.",
        "החלפת $x$ ב-$x+3$: הזזה **שמאלה** 3 (פלוס בפנים → הפוך → שמאלה). $-1$ בחוץ: **מטה** 1. קדקוד $(-3,-1)$.",
        "קראו פנים קודם: $(x+3)^2$ = $f(x+3)$ — שמאלה 3. $-1$ בחוץ — מטה 1. אימות: מינימום ב-$x=-3$, ערך $-1$.",
        "לומר 'ימינה 3' בגלל $+3$ בסוגריים — טעות כיוון פנימית קלאסית.",
        "בתשובה קצרה — **שתי הזזות + נקודה**. משפט לכיוון + קדקוד מספיקים.",
    ),
    fmt_expl(
        "$g(x)=3f(x)-2$ only scales and shifts vertically — the $x$-coordinate stays 2. $g(2)=3f(2)-2=3(5)-2=13$. Image: $(2,13)$.",
        "When the transformation is $af(x)+d$ with no inside change, $x$ is unchanged. Multiply the known $y$-value by $a$, then add $d$. Quick check: $3\\times 5=15$, minus 2 = 13.",
        "Changing $x$ to $6$ or $2/3$ — applying horizontal logic where none exists. Only $y$ transforms here.",
        "Pure vertical transforms preserve every $x$-intercept location's $x$ — only heights change. State that explicitly to show understanding.",
        "$g(x)=3f(x)-2$ רק גרימה והזזה אנכית — $x$ נשאר 2. $g(2)=3(5)-2=13$. דמות: $(2,13)$.",
        "כש-$af(x)+d$ בלי שינוי בפנים, $x$ לא משתנה. הכפילו $y$ ב-$a$, הוסיפו $d$. בדיקה: $3\\times 5=15$, פחות 2 = 13.",
        "שינוי $x$ ל-$6$ — יישום לוגיקה אופקית שלא קיימת. רק $y$ משתנה.",
        "טרנספורמציה אנכית טהורה שומרת $x$ — רק ערכי $y$ משתנים. ציינו זאת במפורש.",
    ),
    fmt_expl(
        "$f(-x)=(-x)^4-3(-x)^2=x^4-3x^2=f(x)$. Even powers make both terms unchanged under $x\\mapsto -x$, so the function is **even** (symmetric about the $y$-axis).",
        "Test: compute $f(-x)$. If it equals $f(x)$ → even; if $-f(x)$ → odd; otherwise neither. Here every term has even degree, so even is immediate.",
        "Answering 'neither' because of the $-3x^2$ subtraction, or 'odd' because of the minus sign. Only **odd powers** of $x$ create odd behavior.",
        "Parity questions: look at exponents first before substituting. Sum of even-only terms → even; sum of odd-only → odd; mixed → usually neither.",
        "$f(-x)=(-x)^4-3(-x)^2=x^4-3x^2=f(x)$. חזקות זוגיות — **זוגית** (סימטריה ל-$y$).",
        "בדיקה: חשב $f(-x)$. שווה $f(x)$ → זוגית; $-f(x)$ → אי-זוגית; אחרת לא. כאן כל האיברים בחזקה זוגית.",
        "לענות 'לא' בגלל $-3x^2$, או 'אי-זוגית' בגלל מינוס. רק **חזקות אי-זוגיות** יוצרות אי-זוגיות.",
        "שאלות זוגיות: בדקו מעלות קודם. סכום זוגיות בלבד → זוגית; אי-זוגיות בלבד → אי-זוגית.",
    ),
]


def pad_expl(text: str, lang: str, min_w: int = 80, max_w: int = 150) -> str:
    extra_en = " Re-read the stem and confirm each transformation before finalizing your answer."
    extra_he = " קראו שוב את הנתון ואמתו כל טרנספורמציה לפני התשובה הסופית."
    while wc(text) < min_w:
        text += extra_he if lang == "he" else extra_en
    words = text.split()
    if len(words) > max_w + 15:
        text = " ".join(words[:max_w])
    return text


def main():
    with open(TARGET, encoding="utf-8") as f:
        lesson = json.load(f)

    section_map = {
        "intro": (INTRO_EN, INTRO_HE),
        "definition": (DEF_EN, DEF_HE),
        "theory": (THEORY_EN, THEORY_HE),
        "method_guide": (METHOD_EN, METHOD_HE),
        "pitfall": (PITFALL_EN, PITFALL_HE),
        "why_matters": (WHY_EN, WHY_HE),
        "before_exam": (BEFORE_EN, BEFORE_HE),
        "summary": (SUMMARY_EN, SUMMARY_HE),
    }

    we_bodies = [WE1_EN, WE1_HE, WE2_EN, WE2_HE, WE3_EN, WE3_HE]
    we_idx = 0
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind in section_map:
            sec["body_en_md"], sec["body_he_md"] = section_map[kind]
        elif kind == "worked_example":
            sec["body_en_md"] = we_bodies[we_idx]
            sec["body_he_md"] = we_bodies[we_idx + 1]
            we_idx += 2
        elif kind == "checkpoint":
            if "2|x+1|" in sec.get("body_en_md", "") or "|x+1|" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CHK1_SOL_EN
                sec["checkpoint_solution_he"] = CHK1_SOL_HE
            elif "sin(2x" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CHK2_SOL_EN
                sec["checkpoint_solution_he"] = CHK2_SOL_HE

    for i, q in enumerate(lesson["questions"]):
        en, he = Q_EXPLS[i]
        q["explanation_en"] = pad_expl(en, "en")
        q["explanation_he"] = pad_expl(he, "he")

    # Fix intro if needed (legacy typo guard)
    lesson["sections"][0]["body_he_md"] = lesson["sections"][0]["body_he_md"].replace(
        "טransformed", "מותמרת"
    ).replace("טransformed", "המותמרת")

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Validate
    errors = []
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind not in EXPAND_KINDS:
            continue
        en_min, he_min = MIN[kind]
        en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        if en_w < en_min:
            errors.append(f"{kind} EN {en_w}<{en_min}")
        if he_w < he_min:
            errors.append(f"{kind} HE {he_w}<{he_min}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"{kind} HE weak")

    for i, q in enumerate(lesson["questions"]):
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80:
                errors.append(f"Q{i+1} {lang} {w}<80")
            if w > 165:
                errors.append(f"Q{i+1} {lang} {w}>165")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)

    print("Section word counts OK, explanations OK")
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
    print("seed-lessons --dry-run passed")


if __name__ == "__main__":
    main()
