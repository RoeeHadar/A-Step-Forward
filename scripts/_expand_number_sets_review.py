#!/usr/bin/env python3
"""Expand number_sets_review.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/number_sets_review.json"

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


INTRO_EN = """Before limits, derivatives, and integrals, calculus assumes you know **which numbers exist** and **what properties they satisfy**. The chain $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$ is not decorative — each inclusion marks a genuine extension: naturals for counting, integers for subtraction, rationals for exact division, reals for continuous motion and convergence.

**Why this review matters now:** In Calc 1 you will meet sequences whose limits are irrational, functions defined only on dense subsets of $\\mathbb{R}$, and proofs that rely on the **Archimedean property** or **completeness**. You cannot argue \"there is a number between $a$ and $b$\" unless you know $\\mathbb{Q}$ is dense in $\\mathbb{R}$. You cannot dismiss a diagonal listing of reals unless you understand **uncountability**.

**What we cover:** precise definitions of the four main sets, decimal tests for rationality, the classic proof that $\\sqrt{2}\\notin\\mathbb{Q}$, density of rationals, closure properties ($\\mathbb{Q}$ closed under $+,-,\\times$), and the contrast between **countable** sets ($\\mathbb{N},\\mathbb{Z},\\mathbb{Q}$) and the **uncountable** continuum $\\mathbb{R}$. This lesson connects forward to `concept:limits_intro` and `concept:continuity_uniform`."""

INTRO_HE = """לפני גבולות, נגזרות ואינטגרלים, חדו\"א מניחה שאתם יודעים **אילו מספרים קיימים** ו**אילו תכונות יש להם**. השרשרת $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$ אינה קישוט — כל הכללה מסמנת הרחבה אמיתית: טבעיים לספירה, שלמים לחיסור, רציונליים לחלוקה מדויקת, ממשיים לתנועה רציפה והתכנסות.

**למה הסקירה חשובה עכשיו:** בחדו\"א 1 תפגשו סדרות שהגבול שלהן אי-רציונלי, פונקציות על תת-קבוצות צפופות של $\\mathbb{R}$, והוכחות שמסתמכות על **תכונת ארכימדס** או **שלמות**. לא ניתן לטעון \"יש מספר בין $a$ ל-$b$\" בלי לדעת ש-$\\mathbb{Q}$ צפוף ב-$\\mathbb{R}$. לא ניתן לדחות רשימה אלכסונית של ממשיים בלי להבין **אי-ספירות**.

**מה נלמד:** הגדרות מדויקות של ארבע הקבוצות, בדיקות עשרוניות לרציונליות, הוכחת $\\sqrt{2}\\notin\\mathbb{Q}$, צפיפות הרציונליים, סגירות $\\mathbb{Q}$ תחת $+,-,\\times$, והניגוד בין קבוצות **ספירות** ($\\mathbb{N},\\mathbb{Z},\\mathbb{Q}$) לרצף **אי-ספיר** $\\mathbb{R}$. השיעור מקשר קדימה ל-`concept:limits_intro` ו-`concept:continuity_uniform`."""

DEF_EN = """**Natural numbers** $\\mathbb{N}=\\{1,2,3,\\ldots\\}$ (some authors include $0$). Used for counting discrete objects. Not closed under subtraction: $2-5\\notin\\mathbb{N}$.

**Integers** $\\mathbb{Z}=\\{\\ldots,-2,-1,0,1,2,\\ldots\\}$. Closed under $+,-,\\times$ but **not** under division: $1\\div 2\\notin\\mathbb{Z}$.

**Rationals** $\\mathbb{Q}=\\left\\{\\dfrac{p}{q}: p,q\\in\\mathbb{Z},\\, q\\neq 0\\right\\}$. Every integer is rational ($n=\\dfrac{n}{1}$). Closed under $+,-,\\times$, and division by non-zero rationals. A number is rational iff its decimal expansion **terminates** or **repeats** eventually.

**Reals** $\\mathbb{R}$: all points on the continuous number line — rationals plus **irrationals** $\\mathbb{R}\\setminus\\mathbb{Q}$ such as $\\sqrt{2}$, $\\pi$, $e$. Irrationals have infinite non-repeating decimals.

**Nested inclusions:** $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$. Each step adds numbers needed for a new operation or for analysis.

**Perfect-square test:** $\\sqrt{p}\\in\\mathbb{Q}$ if and only if $p$ is a perfect square (for positive integer $p$). Thus $\\sqrt{4}=2\\in\\mathbb{Q}$ but $\\sqrt{2}\\notin\\mathbb{Q}$. When in doubt, simplify the radical first."""

DEF_HE = """**מספרים טבעיים** $\\mathbb{N}=\\{1,2,3,\\ldots\\}$ (לעיתים כוללים $0$). לספירה של אובייקטים בדידים. לא סגורים לחיסור: $2-5\\notin\\mathbb{N}$.

**שלמים** $\\mathbb{Z}=\\{\\ldots,-2,-1,0,1,2,\\ldots\\}$. סגורים תחת $+,-,\\times$ אך **לא** תחת חילוק: $1\\div 2\\notin\\mathbb{Z}$.

**רציונליים** $\\mathbb{Q}=\\left\\{\\dfrac{p}{q}: p,q\\in\\mathbb{Z},\\, q\\neq 0\\right\\}$. כל שלם רציונלי ($n=\\dfrac{n}{1}$). סגורים תחת $+,-,\\times$ וחילוק ברציונלי שונה מאפס. מספר רציונלי אם ורק אם הייצוג העשרוני **מסתיים** או **חוזר** בסופו.

**ממשיים** $\\mathbb{R}$: כל הנקודות על ציר המספרים הרציף — רציונליים ו**אי-רציונליים** $\\mathbb{R}\\setminus\\mathbb{Q}$ כמו $\\sqrt{2}$, $\\pi$, $e$. לאי-רציונליים עשרוני אינסופי לא-מחזורי.

**הכללות:** $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$. כל שלב מוסיף מספרים הנדרשים לפעולה חדשה או לניתוח.

**בדיקת ריבוע מושלם:** $\\sqrt{p}\\in\\mathbb{Q}$ אם ורק אם $p$ ריבוע מושלם (ל-$p$ שלם חיובי). לכן $\\sqrt{4}=2\\in\\mathbb{Q}$ אך $\\sqrt{2}\\notin\\mathbb{Q}$."""

THEORY_EN = """**Countability:** A set is **countably infinite** if it can be placed in one-to-one correspondence with $\\mathbb{N}$. Surprisingly, $|\\mathbb{N}|=|\\mathbb{Z}|=|\\mathbb{Q}|$ even though $\\mathbb{Q}$ seems \"much larger.\" Cantor's diagonal traversal of positive rationals $p/q$ in a grid proves $\\mathbb{Q}^+$ is countable; extend to all of $\\mathbb{Q}$ by listing positive then negative fractions.

**Uncountability of $\\mathbb{R}$:** No listing $x_1,x_2,x_3,\\ldots$ can exhaust $[0,1]$. Cantor's diagonal argument constructs a real whose $n$-th decimal digit differs from the $n$-th digit of $x_n$, so it is missing from the list. Hence $|\\mathbb{R}|>|\\mathbb{N}|$.

**Density of $\\mathbb{Q}$ in $\\mathbb{R}$:** For any $a<b$ in $\\mathbb{R}$, there exists $r\\in\\mathbb{Q}$ with $a<r<b$. Proof sketch: pick $n\\in\\mathbb{N}$ with $1/n<b-a$, set $m=\\lfloor na\\rfloor+1$, then $r=m/n$ works. Irrationals are also dense — between any two reals there are infinitely many of each kind.

**Closure facts used in proofs:**
- $\\mathbb{Q}$ closed under $+,-,\\times$ and division (non-zero divisor).
- If $r\\in\\mathbb{Q}$ and $x\\notin\\mathbb{Q}$, then $r+x\\notin\\mathbb{Q}$ and (for $r\\neq 0$) $rx\\notin\\mathbb{Q}$.
- Sum of two irrationals **may** be rational ($\\sqrt{2}+(-\\sqrt{2})=0$) — do not assume closure.

**Completeness (preview):** Every non-empty subset of $\\mathbb{R}$ bounded above has a **least upper bound** in $\\mathbb{R}$ — a property $\\mathbb{Q}$ lacks ($\\sqrt{2}$ is not in $\\mathbb{Q}$ though it is an upper bound of rationals below it). This underpins limits and the Intermediate Value Theorem."""

THEORY_HE = """**ספירות:** קבוצה **ספירה** אם ניתן להעמיד אותה בהתאמה חד-חד-ערכית עם $\\mathbb{N}$. באופן מפתיע, $|\\mathbb{N}|=|\\mathbb{Z}|=|\\mathbb{Q}|$ למרות ש-$\\mathbb{Q}$ נראית \"גדולה הרבה יותר\". מעבר אלכסוני של קנטור על רציונליים חיוביים $p/q$ ברשת מוכיח ש-$\\mathbb{Q}^+$ ספירה; מרחיבים לכל $\\mathbb{Q}$.

**אי-ספירות $\\mathbb{R}$:** אין רשימה $x_1,x_2,x_3,\\ldots$ שמכסה את $[0,1]$. הוכחת האלכסון של קנטור בונה ממשי שהספרה $n$-ית שלו שונה מהספרה $n$-ית של $x_n$, ולכן חסר מהרשימה. מכאן $|\\mathbb{R}|>|\\mathbb{N}|$.

**צפיפות $\\mathbb{Q}$ ב-$\\mathbb{R}$:** לכל $a<b$ ב-$\\mathbb{R}$, קיים $r\\in\\mathbb{Q}$ עם $a<r<b$. בוחרים $n\\in\\mathbb{N}$ עם $1/n<b-a$, מגדירים $m=\\lfloor na\\rfloor+1$, ואז $r=m/n$ מתאים. גם אי-רציונליים צפופים — בין כל שני ממשיים יש אינסוף מכל סוג.

**עובדות סגירות להוכחות:**
- $\\mathbb{Q}$ סגורה תחת $+,-,\\times$ וחילוק (מחלק $\\neq 0$).
- אם $r\\in\\mathbb{Q}$ ו-$x\\notin\\mathbb{Q}$, אז $r+x\\notin\\mathbb{Q}$ ו (ל-$r\\neq 0$) $rx\\notin\\mathbb{Q}$.
- סכום שני אי-רציונליים **עלול** להיות רציונלי ($\\sqrt{2}+(-\\sqrt{2})=0$) — אל תניחו סגירות.

**שלמות (תצוגה מקדימה):** לכל תת-קבוצה לא-ריקה חסומה מלעיל ב-$\\mathbb{R}$ יש **חסם עליון מינימלי** ב-$\\mathbb{R}$ — תכונה ש-$\\mathbb{Q}$ חסרה ($\\sqrt{2}\\notin\\mathbb{Q}$ למרות שהוא חסם של רציונליים מתחתיו). זה תומך בגבולות ובמשפט הערך הביניים."""

WE1_EN = """**Classify** $-3,\\, 0.5,\\, \\sqrt{4},\\, \\pi$ into $\\mathbb{N},\\mathbb{Z},\\mathbb{Q},\\mathbb{R}$.

Classification problems test whether you check **membership in the smallest correct set** and whether you simplify radicals before deciding rationality.

### Move 1: Simplify where possible
$\\sqrt{4}=2$. The table uses simplified values — never classify $\\sqrt{4}$ as irrational without simplifying.

### Move 2: Build the membership table
| Number | Value | $\\mathbb{N}$? | $\\mathbb{Z}$? | $\\mathbb{Q}$? | $\\mathbb{R}$? |
|---|---|---|---|---|---|
| $-3$ | $-3$ | No | Yes | Yes | Yes |
| $0.5$ | $1/2$ | No | No | Yes | Yes |
| $\\sqrt{4}$ | $2$ | Yes | Yes | Yes | Yes |
| $\\pi$ | $\\approx 3.14\\ldots$ | No | No | No | Yes |

### Move 3: Explain each borderline case
$-3\\in\\mathbb{Z}$ but not $\\mathbb{N}$ (negative). $0.5=\\dfrac{1}{2}\\in\\mathbb{Q}$ but not $\\mathbb{Z}$. $\\pi$ is in $\\mathbb{R}\\setminus\\mathbb{Q}$ — infinite non-repeating decimal.

**Check:** Every number listed is at least in $\\mathbb{R}$. If you ever mark \"No\" for $\\mathbb{R}$, re-read the definition — all these are real."""

WE1_HE = """**סווגו** את $-3,\\, 0.5,\\, \\sqrt{4},\\, \\pi$ ל-$\\mathbb{N},\\mathbb{Z},\\mathbb{Q},\\mathbb{R}$.

שאלות סיווג בודקות אם אתם בודקים **שייכות לקבוצה המינימלית הנכונה** ואם מפשטים שורשים לפני קביעת רציונליות.

### צעד 1: פישוט במידת הצורך
$\\sqrt{4}=2$. הטבלה משתמשת בערכים מפושטים — לעולם אל תסווגו $\\sqrt{4}$ כאי-רציונלי בלי לפשט.

### צעד 2: בניית טבלת השייכות
| מספר | ערך | $\\mathbb{N}$? | $\\mathbb{Z}$? | $\\mathbb{Q}$? | $\\mathbb{R}$? |
|---|---|---|---|---|---|
| $-3$ | $-3$ | לא | כן | כן | כן |
| $0.5$ | $1/2$ | לא | לא | כן | כן |
| $\\sqrt{4}$ | $2$ | כן | כן | כן | כן |
| $\\pi$ | $\\approx 3.14\\ldots$ | לא | לא | לא | כן |

### צעד 3: הסבר מקרי גבול
$-3\\in\\mathbb{Z}$ אך לא $\\mathbb{N}$ (שלילי). $0.5=\\dfrac{1}{2}\\in\\mathbb{Q}$ אך לא $\\mathbb{Z}$. $\\pi\\in\\mathbb{R}\\setminus\\mathbb{Q}$ — עשרוני אינסופי לא-מחזורי.

**בדיקה:** כל מספר ברשימה לפחות ב-$\\mathbb{R}$. אם סימנתם \"לא\" ל-$\\mathbb{R}$, קראו שוב את ההגדרה."""

WE2_EN = """**Claim:** $\\sqrt{2}\\notin\\mathbb{Q}$.

This is the template irrationality proof used on university problem sets and in real-analysis courses. Master every logical step — you will reuse it for $\\sqrt{3}$, $\\sqrt{5}$, and $2^{1/3}$.

### Move 1: Assume rational in lowest terms
Suppose $\\sqrt{2}=\\dfrac{p}{q}$ with $p,q\\in\\mathbb{Z}^+$, $\\gcd(p,q)=1$ (fraction fully reduced).

### Move 2: Clear denominators and deduce parity of $p$
Square both sides: $2=\\dfrac{p^2}{q^2}$, so $p^2=2q^2$. Thus $p^2$ is even, hence $p$ is even. Write $p=2k$.

### Move 3: Substitute and deduce parity of $q$
$(2k)^2=2q^2 \\Rightarrow 4k^2=2q^2 \\Rightarrow q^2=2k^2$. So $q^2$ is even, hence $q$ is even.

### Move 4: Contradiction
If both $p$ and $q$ are even, $\\gcd(p,q)\\ge 2$, contradicting lowest terms. Therefore $\\sqrt{2}\\notin\\mathbb{Q}$. $\\square$

**Key idea:** Squaring transfers the factor $2$ from outside the root to both numerator and denominator parity. The \"lowest terms\" hypothesis is essential — without it, the contradiction disappears."""

WE2_HE = """**טענה:** $\\sqrt{2}\\notin\\mathbb{Q}$.

זו תבנית ההוכחה לאי-רציונליות בקורסי חדו\"א ואנליזה. שלטו בכל שלב — תשתמשו בה ל-$\\sqrt{3}$, $\\sqrt{5}$ ו-$2^{1/3}$.

### צעד 1: הנחה רציונלית בצמצום מרבי
נניח $\\sqrt{2}=\\dfrac{p}{q}$ עם $p,q\\in\\mathbb{Z}^+$, $\\gcd(p,q)=1$.

### צעד 2: העלאה בריבוע וזוגיות $p$
בריבוע: $2=\\dfrac{p^2}{q^2}$, כלומר $p^2=2q^2$. לכן $p^2$ זוגי, ו-$p$ זוגי. נכתוב $p=2k$.

### צעד 3: הצבה וזוגיות $q$
$(2k)^2=2q^2 \\Rightarrow 4k^2=2q^2 \\Rightarrow q^2=2k^2$. לכן $q^2$ זוגי, ו-$q$ זוגי.

### צעד 4: סתירה
אם $p$ ו-$q$ שניהם זוגיים, $\\gcd(p,q)\\ge 2$, בסתירה לצמצום מרבי. לכן $\\sqrt{2}\\notin\\mathbb{Q}$. $\\square$

**רעיון מרכזי:** העלאה בריבוע מעבירה את הגורם $2$ לזוגיות של $p$ ו-$q$. הנחת \"צמצום מרבי\" חיונית — בלעדיה הסתירה נעלמת."""

WE3_EN = """**Theorem:** For any $a,b\\in\\mathbb{R}$ with $a<b$, there exists $r\\in\\mathbb{Q}$ with $a<r<b$.

Density explains why limits can be approached through rationals — a central idea when you later define continuity and prove that $\\mathbb{Q}$ is **not** closed (e.g. $\\sqrt{2}$ is a limit of rationals but not rational).

### Move 1: Use the Archimedean property
Since $b-a>0$, there exists $n\\in\\mathbb{N}$ with $n>\\dfrac{1}{b-a}$, equivalently $\\dfrac{1}{n}<b-a$.

### Move 2: Choose an integer just above $na$
Let $m=\\lfloor na\\rfloor+1$. Then $m-1\\le na<m$, so $a<\\dfrac{m}{n}$.

### Move 3: Show the rational is below $b$
We have $m\\le na+1$. Since $1\\le n(b-a)$, we get $na+1\\le n(a+(b-a))=nb$, hence $\\dfrac{m}{n}<b$.

### Move 4: Conclude
$r=\\dfrac{m}{n}\\in\\mathbb{Q}$ satisfies $a<r<b$. $\\square$

**Exam use:** To find an explicit rational between two irrationals, pick any $n$ with $1/n$ smaller than the gap, then compute $m=\\lfloor na\\rfloor+1$. Example: between $\\sqrt{2}$ and $\\sqrt{3}$, $n=4$ gives $m=\\lfloor 4\\cdot 1.414\\rfloor+1=6$, so $r=\\dfrac{6}{4}=\\dfrac{3}{2}$ works."""

WE3_HE = """**משפט:** לכל $a,b\\in\\mathbb{R}$ עם $a<b$, קיים $r\\in\\mathbb{Q}$ עם $a<r<b$.

צפיפות מסבירה למה ניתן להתקרב לגבולות דרך רציונליים — רעיון מרכזי בהגדרת רציפות ובהוכחה ש-$\\mathbb{Q}$ **לא** סגורה (למשל $\\sqrt{2}$ גבול של רציונליים אך לא רציונלי).

### צעד 1: תכונת ארכימדס
כיוון ש-$b-a>0$, קיים $n\\in\\mathbb{N}$ עם $n>\\dfrac{1}{b-a}$, כלומר $\\dfrac{1}{n}<b-a$.

### צעד 2: בחירת שלם מעל $na$
$m=\\lfloor na\\rfloor+1$. אז $m-1\\le na<m$, ולכן $a<\\dfrac{m}{n}$.

### צעד 3: הרציונלי מתחת ל-$b$
$m\\le na+1$. כיוון ש-$1\\le n(b-a)$, מתקבל $na+1\\le nb$, ולכן $\\dfrac{m}{n}<b$.

### צעד 4: מסקנה
$r=\\dfrac{m}{n}\\in\\mathbb{Q}$ מקיים $a<r<b$. $\\square$

**שימוש בבחינה:** למציאת רציונלי מפורש בין שני אי-רציונליים — בחרו $n$ עם $1/n$ קטן מהמרווח, וחשבו $m=\\lfloor na\\rfloor+1$. דוגמה: בין $\\sqrt{2}$ ל-$\\sqrt{3}$, $n=4$ נותן $m=6$, ו-$r=\\dfrac{3}{2}$ מתאים."""

CHK1_EN = """**Classify** $\\sqrt{9}$ and $\\sqrt{5}$.

### Step 1: Simplify $\\sqrt{9}$
$\\sqrt{9}=3$. Since $3\\in\\mathbb{N}$, it also lies in $\\mathbb{Z}$, $\\mathbb{Q}$, and $\\mathbb{R}$.

### Step 2: Analyze $\\sqrt{5}$
$5$ is not a perfect square, so $\\sqrt{5}$ cannot equal $\\dfrac{p}{q}$ in lowest terms (standard contradiction proof applies). Therefore $\\sqrt{5}\\in\\mathbb{R}\\setminus\\mathbb{Q}$.

### Step 3: Summary table
| Number | $\\mathbb{N}$ | $\\mathbb{Z}$ | $\\mathbb{Q}$ | $\\mathbb{R}$ |
|---|---|---|---|---|
| $\\sqrt{9}=3$ | Yes | Yes | Yes | Yes |
| $\\sqrt{5}$ | No | No | No | Yes |

**Answer:** $\\sqrt{9}$ is rational (in fact natural); $\\sqrt{5}$ is irrational but real."""

CHK1_HE = """**סווגו** $\\sqrt{9}$ ו-$\\sqrt{5}$.

### שלב 1: פישוט $\\sqrt{9}$
$\\sqrt{9}=3$. כיוון ש-$3\\in\\mathbb{N}$, הוא גם ב-$\\mathbb{Z}$, $\\mathbb{Q}$ ו-$\\mathbb{R}$.

### שלב 2: ניתוח $\\sqrt{5}$
$5$ אינו ריבוע מושלם, ולכן $\\sqrt{5}\\notin\\mathbb{Q}$ (הוכחת סתירה סטנדרטית). לכן $\\sqrt{5}\\in\\mathbb{R}\\setminus\\mathbb{Q}$.

### שלב 3: טבלת סיכום
| מספר | $\\mathbb{N}$ | $\\mathbb{Z}$ | $\\mathbb{Q}$ | $\\mathbb{R}$ |
|---|---|---|---|---|
| $\\sqrt{9}=3$ | כן | כן | כן | כן |
| $\\sqrt{5}$ | לא | לא | לא | כן |

**תשובה:** $\\sqrt{9}$ רציונלי (אף טבעי); $\\sqrt{5}$ אי-רציונלי אך ממשי."""

CHK2_EN = """**Classify** $0.\\overline{3}=0.3333\\ldots$

### Step 1: Recognise repeating decimal
A decimal that repeats a single block forever is rational. Here the block is $3$.

### Step 2: Convert to fraction (verify)
Let $x=0.\\overline{3}$. Then $10x=3.\\overline{3}=3+x$, so $9x=3$ and $x=\\dfrac{1}{3}$.

### Step 3: Place in number sets
$\\dfrac{1}{3}\\in\\mathbb{Q}$. It is not an integer (not in $\\mathbb{Z}$ or $\\mathbb{N}$) but is certainly in $\\mathbb{R}$.

**Answer:** $0.\\overline{3}$ is **rational**; $0.\\overline{3}=\\dfrac{1}{3}\\in\\mathbb{Q}\\subset\\mathbb{R}$."""

CHK2_HE = """**סווגו** $0.\\overline{3}=0.3333\\ldots$

### שלב 1: זיהוי עשרוני מחזורי
עשרוני שחוזר על בלוק לנצח הוא רציונלי. כאן הבלוק הוא $3$.

### שלב 2: המרה לשבר (אימות)
יהי $x=0.\\overline{3}$. אז $10x=3.\\overline{3}=3+x$, ולכן $9x=3$ ו-$x=\\dfrac{1}{3}$.

### שלב 3: שייכות לקבוצות
$\\dfrac{1}{3}\\in\\mathbb{Q}$. לא שלם (לא ב-$\\mathbb{Z}$ או $\\mathbb{N}$) אך בוודאי ב-$\\mathbb{R}$.

**תשובה:** $0.\\overline{3}$ **רציונלי**; $0.\\overline{3}=\\dfrac{1}{3}\\in\\mathbb{Q}\\subset\\mathbb{R}$."""

METHOD_EN = """| Task | Approach |
|---|---|
| Classify a number | Simplify radicals/decimals; check $\\mathbb{N}\\to\\mathbb{Z}\\to\\mathbb{Q}\\to\\mathbb{R}$ in order |
| Prove irrational | Assume $\\sqrt{n}=p/q$ in lowest terms; square; deduce common factor; contradict |
| Find rational between $a,b$ | Pick $n$ with $1/n<b-a$; set $r=(\\lfloor na\\rfloor+1)/n$ |
| Repeating decimal to $p/q$ | Let $x$ = decimal; multiply by $10^k$ to shift period; subtract to eliminate tail |
| Show $|\\mathbb{N}|=|\\mathbb{Z}|$ | Bijection: $1\\mapsto 0,\\,2\\mapsto 1,\\,3\\mapsto -1,\\,4\\mapsto 2,\\ldots$ |
| Cantor diagonal | Assume list of reals; change $n$-th digit of $x_n$ to build missing number |

**When to use:** Read the problem type first — classification, irrationality proof, density, or cardinality — then open the matching row. Substitute numbers only after the structural method is chosen.

**Exam tip:** For MCQs, eliminate options that are clearly rational ($\\sqrt{9}$, $0.\\overline{3}$) before attacking harder irrationals like $\\pi$."""

METHOD_HE = """| משימה | גישה |
|---|---|
| סיווג מספר | פשטו שורשים/עשרוניים; בדקו $\\mathbb{N}\\to\\mathbb{Z}\\to\\mathbb{Q}\\to\\mathbb{R}$ לפי סדר |
| הוכחת אי-רציונליות | הניחו $\\sqrt{n}=p/q$ בצמצום; ריבוע; גורם משותף; סתירה |
| רציונלי בין $a,b$ | בחרו $n$ עם $1/n<b-a$; $r=(\\lfloor na\\rfloor+1)/n$ |
| עשרוני מחזורי ל-$p/q$ | $x$ = העשרוני; כפלו ב-$10^k$; חיסור להסרת זנב |
| $|\\mathbb{N}|=|\\mathbb{Z}|$ | חד-חד: $1\\mapsto 0,\\,2\\mapsto 1,\\,3\\mapsto -1,\\ldots$ |
| אלכסון קנטור | הניחו רשימת ממשיים; שנה ספרה $n$ של $x_n$ |

**מתי להשתמש:** קראו קודם את סוג הבעיה — סיווג, הוכחת אי-רציונליות, צפיפות או עוצמה — ואז בחרו שורה. הציבו מספרים רק אחרי בחירת השיטה.

**טיפ לבחינה:** בשאלות רב-ברירה, שללו אפשרויות רציונליות ברורות ($\\sqrt{9}$, $0.\\overline{3}$) לפני התקפה על $\\pi$ ודומיו."""

PITFALL_EN = """1. **$\\sqrt{4}$ is rational, $\\sqrt{2}$ is not** — always simplify the radicand before deciding. The perfect-square test applies to the integer under the root.

2. **Repeating decimal $\\Leftrightarrow$ rational.** Use $10^k x - x$ to convert. Students forget that $0.999\\ldots = 1$ is rational, not a special case.

3. **Irrational + irrational may be rational.** $\\sqrt{2}+(-\\sqrt{2})=0$. Never claim \"sum of irrationals is irrational\" without hypotheses.

4. **$\\mathbb{Q}$ is countable yet dense.** \"Small\" cardinality does not mean numbers are sparse on the line — between any two reals lie infinitely many rationals.

5. **Confusing density with completeness.** Rationals are dense in $\\mathbb{R}$ but $\\mathbb{Q}$ is not complete — limits of rational sequences may leave $\\mathbb{Q}$ (e.g. $\\sqrt{2}$).

**Fix habit:** After each answer, name the **smallest** set containing your number and cite one sentence of justification."""

PITFALL_HE = """1. **$\\sqrt{4}$ רציונלי, $\\sqrt{2}$ לא** — תמיד פשטו את מה שתחת השורש. בדיקת ריבוע מושלם חלה על השלם שמתחת לשורש.

2. **עשרוני מחזורי $\\Leftrightarrow$ רציונלי.** השתמשו ב-$10^k x - x$. תלמידים שוכחים ש-$0.999\\ldots = 1$ רציונלי.

3. **אי-רציונלי + אי-רציונלי עלול להיות רציונלי.** $\\sqrt{2}+(-\\sqrt{2})=0$. אל תטענו \"סכום אי-רציונליים אי-רציונלי\" בלי הנחות.

4. **$\\mathbb{Q}$ ספירה אך צפופה.** עוצמה \"קטנה\" לא אומרת שהמספרים דלילים על הציר — בין כל שני ממשיים אינסוף רציונליים.

5. **בלבול צפיפות ושלמות.** רציונליים צפופים ב-$\\mathbb{R}$ אך $\\mathbb{Q}$ לא שלמה — גבולות של סדרות רציונליות עלולים לצאת מ-$\\mathbb{Q}$ (למשל $\\sqrt{2}$).

**הרגל תיקון:** אחרי כל תשובה, ציינו את הקבוצה **הקטנה** ביותר שמכילה את המספר ומשפט הצדקה אחד."""

WHY_EN = """Number-set fluency is the silent prerequisite for all of Calc 1. When you write $\\lim_{n\\to\\infty}(1+\\tfrac{1}{n})^n=e$, you rely on $e\\in\\mathbb{R}\\setminus\\mathbb{Q}$. When you approximate $\\pi$ with rationals, you use **density**. When a proof says \"choose a rational $\\delta$\", it is this lesson in action.

**Links in the KG:** `concept:limits_intro` needs the Archimedean property; `concept:continuity_uniform` needs completeness of $\\mathbb{R}$; `concept:sequences_limits` contrasts Cauchy sequences in $\\mathbb{Q}$ vs $\\mathbb{R}$.

**Real-world angle:** Computers store rationals (floating point) but model continuous quantities (time, distance) as reals — understanding the gap prevents naive \"the computer value equals the true value\" errors in numerical analysis courses."""

WHY_HE = """שליטה בקבוצות מספרים היא תנאי מוקדם שקט לכל חדו\"א 1. כשכותבים $\\lim_{n\\to\\infty}(1+\\tfrac{1}{n})^n=e$, מסתמכים על $e\\in\\mathbb{R}\\setminus\\mathbb{Q}$. כשמקרבים $\\pi$ ברציונליים, משתמשים ב**צפיפות**. כשהוכחה אומרת \"בחרו $\\delta$ רציונלי\", זה השיעור הזה בפעולה.

**קשרים בגרף:** `concept:limits_intro` דורש ארכימדס; `concept:continuity_uniform` דורש שלמות $\\mathbb{R}$; `concept:sequences_limits` משווה סדרות קושי ב-$\\mathbb{Q}$ לעומת $\\mathbb{R}$.

**זווית יישומית:** מחשבים מאחסנים רציונליים (נקודה צפה) אך מודלים כמויות רציפות (זמן, מרחק) כממשיים — הבנת הפער מונעת \"ערך המחשב = הערך האמיתי\" בקורסי ניתוח מספרי."""

BEFORE_EN = """**Must-know chain:** $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$.

**Quick tests:**
- $\\sqrt{p}\\in\\mathbb{Q}$ iff $p$ is a perfect square (positive integer $p$).
- Terminating or repeating decimal $\\Leftrightarrow$ rational.
- $\\sqrt{2}$ irrational: proof by contradiction in lowest terms.
- $\\mathbb{Q}$ dense in $\\mathbb{R}$: Archimedean property $\\Rightarrow$ $m/n$ between $a$ and $b$.
- $|\\mathbb{N}|=|\\mathbb{Q}|$ countable; $|\\mathbb{R}|$ uncountable (Cantor diagonal).

**60-second drill:** Classify $\\sqrt{25}$, $0.\\overline{6}$, $\\sqrt{7}$; give one rational between $1.4$ and $1.5$.

**Last review:** Draw the nested-set diagram, place three examples in each region, then prove \"rational + irrational is irrational\" from memory."""

BEFORE_HE = """**שרשרת חובה:** $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$.

**בדיקות מהירות:**
- $\\sqrt{p}\\in\\mathbb{Q}$ אם ורק אם $p$ ריבוע מושלם.
- עשרוני מסתיים או מחזורי $\\Leftrightarrow$ רציונלי.
- $\\sqrt{2}$ אי-רציונלי: הוכחת סתירה בצמצום מרבי.
- $\\mathbb{Q}$ צפוף ב-$\\mathbb{R}$: ארכימדס $\\Rightarrow$ $m/n$ בין $a$ ל-$b$.
- $|\\mathbb{N}|=|\\mathbb{Q}|$ ספירות; $|\\mathbb{R}|$ אי-ספיר (אלכסון קנטור).

**תרגול 60 שניות:** סווגו $\\sqrt{25}$, $0.\\overline{6}$, $\\sqrt{7}$; תנו רציונלי אחד בין $1.4$ ל-$1.5$.

**חזרה אחרונה:** ציירו דיאגרמת הכללה, הציבו שלוש דוגמאות בכל אזור, והוכיחו \"רציונלי + אי-רציונלי = אי-רציונלי\" מהזיכרון."""

SUMMARY_EN = """- **Hierarchy:** $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$; each step adds numbers for new operations or analysis.
- **Irrationals** $\\mathbb{R}\\setminus\\mathbb{Q}$: non-terminating, non-repeating decimals; $\\sqrt{p}$ rational iff $p$ perfect square.
- **Proof template:** assume $\\sqrt{n}=p/q$ lowest terms $\\Rightarrow$ contradiction on gcd.
- **Density:** between any two reals lies a rational (and an irrational).
- **Cardinality:** $\\mathbb{N},\\mathbb{Z},\\mathbb{Q}$ countable; $\\mathbb{R}$ uncountable.
- **Closure:** $\\mathbb{Q}$ closed under field operations; rational $\\pm$ irrational is irrational (non-zero rational times irrational is irrational).

**Takeaway:** From the problem wording alone, you should know whether to classify, convert a decimal, prove irrationality, exhibit a rational between two numbers, or invoke countability."""

SUMMARY_HE = """- **היררכיה:** $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}\\subset\\mathbb{R}$; כל שלב מוסיף מספרים לפעולות או לניתוח.
- **אי-רציונליים** $\\mathbb{R}\\setminus\\mathbb{Q}$: עשרוני אינסופי לא-מחזורי; $\\sqrt{p}$ רציונלי אם ורק אם $p$ ריבוע מושלם.
- **תבנית הוכחה:** הניחו $\\sqrt{n}=p/q$ בצמצום $\\Rightarrow$ סתירה על $\\gcd$.
- **צפיפות:** בין כל שני ממשיים יש רציונלי (ואי-רציונלי).
- **עוצמה:** $\\mathbb{N},\\mathbb{Z},\\mathbb{Q}$ ספירות; $\\mathbb{R}$ אי-ספיר.
- **סגירות:** $\\mathbb{Q}$ סגורה לפעולות שדה; רציונלי $\\pm$ אי-רציונלי = אי-רציונלי.

**מסקנה:** מניסוח השאלה בלבד תדעו אם לסווג, להמיר עשרוני, להוכיח אי-רציונליות, למצוא רציונלי בין מספרים, או לעורר עוצמה."""

EXPLS = {
    1: fmt_expl(
        "$\\pi$ is a classic irrational — its decimal never repeats. The other options simplify to rationals: $0.\\overline{3}=\\tfrac{1}{3}$, $\\sqrt{9}=3$, and $-7=\\tfrac{-7}{1}$.",
        "For \"which is irrational\" MCQs, test each option: can it be written as $\\tfrac{p}{q}$? Repeating decimals and perfect-square roots are rational traps — eliminate them first.",
        "Choosing $\\sqrt{9}$ because it \"looks like a root\" without simplifying to $3$. Or picking $0.\\overline{3}$ thinking infinite decimals are always irrational.",
        "Write $\\sqrt{n}$ checklist: if $n$ is a perfect square, the root is rational. Keep a short list: $4,9,16,25$ rational; $2,3,5,7$ irrational.",
        "$\\pi$ אי-רציונלי קלאסי — העשרוני שלו לא חוזר. שאר האפשרויות רציונליות: $0.\\overline{3}=\\tfrac{1}{3}$, $\\sqrt{9}=3$, $-7=\\tfrac{-7}{1}$.",
        "ב\"איזה אי-רציונלי\" — בדקו כל אפשרות: האם ניתן לכתוב $\\tfrac{p}{q}$? עשרוניים מחזוריים ושורשי ריבוע מושלם הם מלכודות רציונליות — שללו קודם.",
        "בחירת $\\sqrt{9}$ כי \"נראה שורש\" בלי לפשט ל-$3$. או $0.\\overline{3}$ כי \"עשרוני אינסופי = אי-רציונלי\".",
        "רשימת $\\sqrt{n}$: אם $n$ ריבוע מושלם — רציונלי. $4,9,16,25$ רציונליים; $2,3,5,7$ אי-רציונליים.",
    ),
    2: fmt_expl(
        "$\\sqrt{16}=4\\in\\mathbb{Z}\\subset\\mathbb{Q}$. The question asks about rationality — every integer is rational because $n=\\tfrac{n}{1}$.",
        "Apply the perfect-square test immediately: $16=4^2$, so the root is an integer. Integers are a subset of rationals, so the answer is yes without a full irrationality proof.",
        "Answering \"no\" because square roots \"look irrational.\" Another error: stopping at $\\sqrt{16}=4$ without stating membership in $\\mathbb{Q}$.",
        "When $\\sqrt{n}$ is an integer, mention both $\\mathbb{Z}$ and $\\mathbb{Q}$ — exam rubrics often want the explicit chain $4\\in\\mathbb{Z}\\subset\\mathbb{Q}$.",
        "$\\sqrt{16}=4\\in\\mathbb{Z}\\subset\\mathbb{Q}$. השאלה על רציונליות — כל שלם רציונלי כי $n=\\tfrac{n}{1}$. בדיקת ריבוע מושלם: $16=4^2$.",
        "החילו מיד בדיקת ריבוע מושלם: $16=4^2$, השורש שלם. שלמים $\\subset$ רציונליים — התשובה כן בלי הוכחת אי-רציונליות. כתבו את השרשרת $4\\in\\mathbb{Z}\\subset\\mathbb{Q}$.",
        "תשובה \"לא\" כי שורש \"נראה אי-רציונלי\". או עצירה ב-$\\sqrt{16}=4$ בלי $\\mathbb{Q}$. או בלבול בין $\\sqrt{16}$ ל-$\\sqrt{15}$.",
        "כש-$\\sqrt{n}$ שלם, ציינו $\\mathbb{Z}$ ו-$\\mathbb{Q}$ — בבחינות רוצים $4\\in\\mathbb{Z}\\subset\\mathbb{Q}$. זהו ריבוע מושלם לפני שורש.",
    ),
    3: fmt_expl(
        "Let $x=0.\\overline{12}$. Since the period has length $2$, multiply by $100$: $100x=12.\\overline{12}=12+x$. Then $99x=12$, so $x=\\tfrac{12}{99}=\\tfrac{4}{33}$ in lowest terms.",
        "For repeating decimals, let $x$ equal the number, multiply by $10^k$ where $k$ is the period length, subtract $x$ to kill the tail, solve linear equation. Always reduce $\\gcd$ at the end.",
        "Using $10x$ instead of $100x$ for a two-digit period — leaves part of the repeat. Or forgetting to simplify $\\tfrac{12}{99}$ to $\\tfrac{4}{33}$.",
        "State the period length before choosing the multiplier — exam graders deduct if you pick $10^k$ without justification. Verify by dividing $4\\div 33$ on a calculator.",
        "יהי $x=0.\\overline{12}$. תקופה באורך $2$, כפלו ב-$100$: $100x=12+x$, $99x=12$, $x=\\tfrac{4}{33}$ בצמצום. זה מאשר שעשרוני מחזורי שווה רציונלי — כלל מרכזי מהשיעור.",
        "בעשרוני מחזורי — $x$ = המספר, כפלו ב-$10^k$ (אורך תקופה), חיסור, פתרו משוואה. צמצמו $\\gcd$ בסוף. אמתו בהחלפת $x$ חזרה לעשרוני.",
        "שימוש ב-$10x$ במקום $100x$ לתקופה בת שני ספרות — נשאר חלק מהחזרה. או שכחת צמצום $\\tfrac{12}{99}$ ל-$\\tfrac{4}{33}$.",
        "ציינו אורך תקופה לפני הכפל — בדקו ב-$4\\div 33$ במחשבון. בבחינה, כתבו את $100x-x$ במפורש.",
    ),
    4: fmt_expl(
        "True. Every integer $n$ equals $\\tfrac{n}{1}$ with denominator $1\\neq 0$, so $n\\in\\mathbb{Q}$ by definition of rationals.",
        "This is a one-line definition check — do not over-prove. The inclusion $\\mathbb{Z}\\subset\\mathbb{Q}$ is built into the definition $\\mathbb{Q}=\\{p/q: q\\neq 0\\}$ with $q=1$.",
        "Answering false, confusing \"integer\" with \"natural.\" Negative integers are still rational. Another slip: thinking $\\tfrac{1}{1}$ is the only valid form.",
        "Memorise $\\mathbb{Z}\\subset\\mathbb{Q}$ as a subset relation — many later closure proofs start by writing integers as rationals with denominator $1$.",
        "נכון. כל שלם $n$ שווה $\\tfrac{n}{1}$, ולכן $n\\in\\mathbb{Q}$ לפי ההגדרה. זה מיישם $\\mathbb{Z}\\subset\\mathbb{Q}$ — כלל בסיסי בשרשרת $\\mathbb{N}\\subset\\mathbb{Z}\\subset\\mathbb{Q}$.",
        "בדיקת הגדרה בשורה — אל תוכיחו יותר מדי. $\\mathbb{Z}\\subset\\mathbb{Q}$ מובנה בהגדרה עם $q=1$. שליליים, אפס וחיוביים — כולם רציונליים.",
        "תשובה \"שגוי\", בלבול שלם/טבעי. שלמים שליליים גם רציונליים ($-7=\\tfrac{-7}{1}$). או חשיבה שרק $\\tfrac{1}{1}$ תקף.",
        "שיננו $\\mathbb{Z}\\subset\\mathbb{Q}$ — הוכחות סגירות מתחילות ב-$n=\\tfrac{n}{1}$. בשאלות נכון/שגוי, צטטו הגדרת $\\mathbb{Q}$ במשפט אחד.",
    ),
    5: fmt_expl(
        "$-\\sqrt{2}+\\sqrt{2}=0$, and $0=\\tfrac{0}{1}\\in\\mathbb{Q}$. The sum of two irrationals can be rational — here they cancel exactly.",
        "Simplify the expression **before** deciding rationality. Do not assume each term's type determines the sum's type — only the simplified value matters.",
        "Answering \"no, irrational\" because both terms involve $\\sqrt{2}$. Students forget that opposites cancel to zero, which is rational.",
        "Always combine like terms first on mixed rational/irrational sums — a zero or integer result immediately settles the question.",
        "$-\\sqrt{2}+\\sqrt{2}=0=\\tfrac{0}{1}\\in\\mathbb{Q}$. סכום שני אי-רציונליים יכול להיות רציונלי — כאן ביטול מלא. $0$ הוא שלם וגם רציונלי.",
        "פשטו **לפני** קביעת רציונליות. אל תניחו שסוג האיברים קובע את סוג הסכום — רק הערך המפושט. איברים מנוגדים מתבטלים לחלוטין.",
        "תשובה \"לא\" כי שני האיברים עם $\\sqrt{2}$. שוכחים ש-$0$ רציונלי. או שלא מחברים לפני הסיווג.",
        "אחדו איברים דומים קודם — תוצאה $0$ או שלם מסיימת מיד. זכרו: $\\sqrt{2}+(-\\sqrt{2})$ מופיע בשיעור כדוגמה לסגירה חלקית.",
    ),
    6: fmt_expl(
        "Any explicit rational strictly between the bounds works. For example $r=\\tfrac{3}{2}=1.5$ lies between $\\sqrt{2}\\approx 1.414$ and $\\sqrt{3}\\approx 1.732$.",
        "You do not need the full Archimedean proof on exams — often picking a simple fraction like $\\tfrac{3}{2}$, $\\tfrac{5}{3}$, or $\\tfrac{7}{5}$ between the given approximations suffices. Verify with decimals.",
        "Giving a number outside the interval (e.g. $1.3$ or $1.8$) by mis-comparing decimals. Or claiming no rational exists because both endpoints are irrational.",
        "When endpoints are decimal approximations, pick a fraction with small denominator whose decimal you know — $\\tfrac{3}{2}=1.5$ is a standard choice between $1.414$ and $1.732$.",
        "כל רציונלי מפורש בין החסמים מתאים. למשל $r=\\tfrac{3}{2}=1.5$ בין $\\sqrt{2}\\approx 1.414$ ל-$\\sqrt{3}\\approx 1.732$. צפיפות $\\mathbb{Q}$ מבטיחה שיש אינסוף כאלה.",
        "לא חייבים הוכחת ארכימדס מלאה — לעיתים $\\tfrac{3}{2}$, $\\tfrac{5}{3}$ בין הקירובים מספיק. אמתו בעשרוניים: $1.414<1.5<1.732$.",
        "מספר מחוץ לקטע ($1.3$ או $1.8$). או \"אין רציונלי\" כי הקצוות אי-רציונליים — טעות: צפיפות $\\mathbb{Q}$ לא תלויה בכך.",
        "כשיש קירובים — בחרו שבר עם מכנה קטן שמוכר ($\\tfrac{3}{2}=1.5$) בין $1.414$ ל-$1.732$. אפשר גם $\\tfrac{5}{3}$ או $\\tfrac{7}{5}$.",
    ),
    7: fmt_expl(
        "Assume $\\sqrt{3}=\\tfrac{p}{q}$ in lowest terms. Then $3q^2=p^2$, so $p^2$ divisible by $3$ implies $p=3k$. Substituting gives $q^2=3k^2$, so $q$ divisible by $3$ — contradicting $\\gcd(p,q)=1$.",
        "Mirror the $\\sqrt{2}$ proof: square, deduce prime divides $p$, write $p=pk$, substitute, deduce same prime divides $q$, contradict lowest terms. Replace $2$ with $3$ throughout.",
        "Stopping after showing $p$ divisible by $3$ without substituting back to force $q$ divisible by $3$. Or forgetting to state \"lowest terms\" at the start.",
        "On exams, write \"Assume $\\gcd(p,q)=1$\" in the first line — without it the proof is incomplete even if algebra is correct.",
        "נניח $\\sqrt{3}=\\tfrac{p}{q}$ בצמצום. $3q^2=p^2$ $\\Rightarrow$ $p=3k$ $\\Rightarrow$ $q^2=3k^2$ $\\Rightarrow$ $q$ מתחלק ב-$3$ — סתירה ל-$\\gcd=1$. $\\square$",
        "שיקפו הוכחת $\\sqrt{2}$: ריבוע, מסקנה על $p$, הצבה $p=3k$, מסקנה על $q$, סתירה. החליפו $2$ ב-$3$ בכל שלב.",
        "עצירה אחרי \"$p$ מתחלק ב-$3$\" בלי להמשיך ל-$q$. או בלי \"צמצום מרבי\" — אז הסתירה לא נסגרת.",
        "כתבו \"$\\gcd(p,q)=1$\" בשורה ראשונה — בלי זה ההוכחה לא שלמה. בחדו\"א 1 מצפים לניסוח מלא כמו ב-$\\sqrt{2}$.",
    ),
    8: fmt_expl(
        "Write $r=\\tfrac{a}{b}$ and $s=\\tfrac{c}{d}$ with integers, $b,d\\neq 0$. Then $r+s=\\tfrac{ad+bc}{bd}$ — numerator and denominator are integers, denominator non-zero, so the sum is rational.",
        "Closure of $\\mathbb{Q}$ under addition is a direct definition exercise: express both numbers as fractions, add with common denominator, cite integer arithmetic. Same pattern works for $r-s$, $rs$, and $r/s$ ($s\\neq 0$).",
        "Adding numerators and denominators separately: $\\tfrac{a}{b}+\\tfrac{c}{d}\\neq\\tfrac{a+c}{b+d}$. Or claiming the denominator could be zero without checking $b,d\\neq 0$.",
        "Memorise the four closure formulas — addition is $\\tfrac{ad+bc}{bd}$. One line each is enough on university problem sets if definitions are cited.",
        "כתבו $r=\\tfrac{a}{b}$, $s=\\tfrac{c}{d}$ עם $b,d\\neq 0$. אז $r+s=\\tfrac{ad+bc}{bd}$ — מונה ומכנה שלמים, מכנה $\\neq 0$, ולכן $r+s\\in\\mathbb{Q}$.",
        "סגירות $\\mathbb{Q}$ לחיבור: שני שברים, מכנה משותף, חשבון שלמים. אותו דפוס לחיסור, כפל וחילוק (מחלק $\\neq 0$).",
        "חיבור מונים ומכנים בנפרד: $\\tfrac{a+c}{b+d}$ — שגוי. או שכחת $b,d\\neq 0$. או טענה ש-$bd=0$ בלי בדיקה.",
        "שיננו $\\tfrac{ad+bc}{bd}$ — שורה אחת מספיקה אם מצטטים הגדרת $\\mathbb{Q}$. זו הוכחת סגירות בסיסית בקורס.",
    ),
}


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

    data["summary_en"] = (
        "Review $\\mathbb{N},\\mathbb{Z},\\mathbb{Q},\\mathbb{R}$: classification, irrationality proofs, "
        "density of $\\mathbb{Q}$, countability vs uncountability, and closure properties for Calc 1."
    )
    data["summary_he"] = (
        "סקירת $\\mathbb{N},\\mathbb{Z},\\mathbb{Q},\\mathbb{R}$: סיווג, הוכחות אי-רציונליות, "
        "צפיפות $\\mathbb{Q}$, ספירות מול אי-ספירות, ותכונות סגירות לחדו\"א 1."
    )

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
            if "sqrt{9}" in sec.get("body_en_md", ""):
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

    data["agent_hints"]["key_insights"] = [
        "$\\sqrt{p}$ is rational iff $p$ is a perfect square.",
        "Proof of irrationality: assume rational $\\rightarrow$ contradiction on $\\gcd$.",
        "$\\mathbb{Q}$ is countable (same cardinality as $\\mathbb{N}$); $\\mathbb{R}$ is not.",
    ]

    answer_fixes = {
        2: ["yes", "Yes", "4", "$\\sqrt{16}=4\\in\\mathbb{Q}$"],
        3: ["4/33", "$4/33$", "Let $x=0.\\overline{12}$. $100x=12.\\overline{12}=12+x$. $99x=12$. $x=12/99=4/33$"],
        4: ["true", "True", "yes", "$n/1\\in\\mathbb{Q}$"],
        5: ["yes", "Yes", "0", "$=0\\in\\mathbb{Q}$"],
        6: ["3/2", "$3/2$", "1.5", "$3/2=1.5$"],
        7: ["Assume $\\sqrt{3}=p/q$, gcd=1. $3q^2=p^2$ $\\rightarrow$ $p=3k$ $\\rightarrow$ $q^2=3k^2$ $\\rightarrow$ $q$ divisible by 3. Contradiction."],
        8: ["$(ad+bc)/(bd)$", "$r+s=(ad+bc)/(bd)$", "$r=a/b$, $s=c/d$. $r+s=(ad+bc)/(bd)$"],
    }
    atom_map = {
        1: ["number_classification"],
        2: ["number_classification"],
        3: ["number_classification"],
        4: ["number_classification"],
        5: ["number_classification"],
        6: ["density_Q_in_R"],
        7: ["irrationality_proof"],
        8: ["number_classification"],
    }

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]
        if ord_ in answer_fixes and q["kind"] == "short_answer":
            q["answer_payload"]["acceptable_answers"] = answer_fixes[ord_]
        if ord_ in atom_map:
            q["skill_atoms"] = atom_map[ord_]

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
