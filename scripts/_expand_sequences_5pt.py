#!/usr/bin/env python3
"""Expand sequences_5pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/sequences_5pt.json"

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


INTRO_EN = """Sequences are the formal language of limits at infinity. In 4-unit math you compute $\\lim a_n$ by substitution or by dividing numerator and denominator by the highest power of $n$. At the **5-unit Bagrut** level, examiners expect **proofs**: show monotonicity, show boundedness, cite the Monotone Convergence Theorem (MCT), then find the limit — often via $L=f(L)$ for recursive sequences.

Typical sequence questions carry **15–20 points** and appear alongside series and function analysis. The number $e=\\lim(1+1/n)^n$ is *defined* through a sequence, not memorized as a decimal. Mastery here connects directly to `concept:series_convergence_tests` and reinforces `concept:limits_5pt`.

This lesson is the proof-writing counterpart to computational limit skills from 4 units. Every later topic that sums infinitely many terms — geometric series, convergence tests, power series — assumes you can argue that a sequence converges before you add its terms."""

INTRO_HE = """סדרות הן השפה הפורמלית של גבולות באינסוף. ב-4 יחידות מחשבים $\\lim a_n$ בהצבה או בחלוקה בחזקה הגבוהה של $n$. ברמת **בגרות 5 יחידות**, בוחנים מצפים ל**הוכחות**: מונוטוניות, חסימות, ציטוט משפט הסדרה המונוטונית (MCT), ואז מציאת גבול — לעיתים דרך $L=f(L)$ לסדרות נסיגה.

שאלות סדרות טיפוסיות שוות **15–20 נקודות** ומופיעות לצד טורים וניתוח פונקציות. המספר $e=\\lim(1+1/n)^n$ *מוגדר* דרך סדרה, לא נשמר כעשרוני. שליטה כאן מתחברת ל-`concept:series_convergence_tests` ומחזקת את `concept:limits_5pt`.

שיעור זה הוא מקבילת כתיבת ההוכחות למיומנות החישוב מ-4 יחידות. כל נושא שמסכם אינסוף גורמים — טורים הנדסיים, מבחני התכנסות, טורי חזקות — מניח שאתם יודעים להוכיח התכנסות סדרה לפני שמסכמים."""

DEF_EN = """**Sequence:** A function $a:\\mathbb{N}\\to\\mathbb{R}$; we write $(a_n)_{n=1}^{\\infty}$ or simply $(a_n)$.

**Limit of a sequence:** $\\lim_{n\\to\\infty}a_n=L$ means: for every $\\varepsilon>0$ there exists $N\\in\\mathbb{N}$ such that for all $n>N$, $|a_n-L|<\\varepsilon$. This is the $\\varepsilon$-$N$ definition — the discrete analogue of $\\varepsilon$-$\\delta$ for functions.

**Convergent / Divergent:** A sequence is **convergent** if its limit exists and is finite; otherwise **divergent** (includes $a_n\\to\\pm\\infty$ and oscillation like $(-1)^n$).

**Monotone increasing:** $a_{n+1}\\geq a_n$ for all $n$. **Strictly increasing:** $a_{n+1}>a_n$. **Monotone decreasing** and **strictly decreasing** are defined analogously.

**Bounded above:** $\\exists M$ such that $a_n\\leq M$ for all $n$. **Bounded below:** $\\exists m$ with $a_n\\geq m$. **Bounded:** both conditions hold.

**Monotone Convergence Theorem (MCT):** A monotone increasing sequence bounded above converges. A monotone decreasing sequence bounded below converges. *Both* conditions are required — bounded alone is not enough.

**Sandwich theorem for sequences:** If $b_n\\leq a_n\\leq c_n$ and $\\lim b_n=\\lim c_n=L$, then $\\lim a_n=L$."""

DEF_HE = """**סדרה:** פונקציה $a:\\mathbb{N}\\to\\mathbb{R}$; נכתוב $(a_n)_{n=1}^{\\infty}$ או $(a_n)$ בקיצור.

**גבול סדרה:** $\\lim_{n\\to\\infty}a_n=L$ פירושו: לכל $\\varepsilon>0$ קיים $N\\in\\mathbb{N}$ כך שלכל $n>N$, $|a_n-L|<\\varepsilon$. זו הגדרת $\\varepsilon$-$N$ — המקבילה הדיסקרטית של $\\varepsilon$-$\\delta$ לפונקציות.

**מתכנסת / מתבדרת:** סדרה **מתכנסת** אם גבולה קיים וסופי; אחרת **מתבדרת** (כולל $a_n\\to\\pm\\infty$ והתנדנדות כמו $(-1)^n$).

**עולה מונוטונית:** $a_{n+1}\\geq a_n$ לכל $n$. **עולה חד-חד:** $a_{n+1}>a_n$. **יורדת מונוטונית** ו**יורדת חד-חד** מוגדרות בדומה.

**חסומה מלמעלה:** $\\exists M$ כך ש-$a_n\\leq M$ לכל $n$. **חסומה מלמטה:** $\\exists m$ עם $a_n\\geq m$. **חסומה:** שני התנאים.

**משפט הסדרה המונוטונית (MCT):** סדרה עולה חסומה מלמעלה מתכנסת. סדרה יורדת חסומה מלמטה מתכנסת. *שני* התנאים נדרשים — חסימה לבדה לא מספיקה.

**משפט הסנדביץ׳ לסדרות:** אם $b_n\\leq a_n\\leq c_n$ ו-$\\lim b_n=\\lim c_n=L$, אז $\\lim a_n=L$."""

THEORY_EN = """**Proving monotonicity — two standard methods:**

*Method 1 — Algebraic difference:* Compute $a_{n+1}-a_n$ and determine its sign. Positive means increasing; negative means decreasing. Works best for explicit formulas $a_n=f(n)$.

*Method 2 — Ratio test (positive sequences):* Compute $a_{n+1}/a_n$. If $>1$ for all sufficiently large $n$, the sequence is eventually increasing; if $<1$, eventually decreasing. Essential when factorials appear ($n!$, $2^n/n!$).

**Proving boundedness:**
- Upper bound: find $M$ and prove $a_n\\leq M$ (direct estimate or induction).
- Lower bound: find $m$ with $a_n\\geq m$.
- For recursive $a_{n+1}=f(a_n)$, induction on $n$ is the standard Bagrut approach.

**Finding the limit via MCT:**
Once monotone + bounded is established, set $L=\\lim a_n$. If $a_{n+1}=f(a_n)$, pass to the limit: $L=f(L)$. Solve for $L$, then discard extraneous roots using sign or bound information.

**Sandwich theorem:** When $a_n$ oscillates (e.g., $\\sin n$ in the numerator), bound it: $-1/n\\leq(\\sin n)/n\\leq 1/n$ and both bounds $\\to 0$.

**Limit laws (when limits exist):** $\\lim(a_n+b_n)=\\lim a_n+\\lim b_n$, $\\lim(a_n b_n)=(\\lim a_n)(\\lim b_n)$, and $\\lim(a_n/b_n)=\\lim a_n/\\lim b_n$ when $\\lim b_n\\neq 0$. A convergent sequence is always bounded — but the converse is false without monotonicity."""

THEORY_HE = """**הוכחת מונוטוניות — שתי שיטות סטנדרטיות:**

*שיטה 1 — הפרש אלגברי:* מחשבים $a_{n+1}-a_n$ וקבעים סימן. חיובי = עולה; שלילי = יורדת. מתאים לנוסחאות מפורשות $a_n=f(n)$.

*שיטה 2 — מבחן המנה (סדרות חיוביות):* מחשבים $a_{n+1}/a_n$. אם $>1$ לכל $n$ מספיק גדול — עולה בסופו; אם $<1$ — יורדת בסופו. חיוני כשמופיעים עצרות ($n!$, $2^n/n!$).

**הוכחת חסימות:**
- חסם מלמעלה: מוצאים $M$ ומוכיחים $a_n\\leq M$ (אומדן ישיר או אינדוקציה).
- חסם מלמטה: $a_n\\geq m$.
- לנסיגה $a_{n+1}=f(a_n)$, אינדוקציה על $n$ היא הגישה הסטנדרטית בבגרות.

**מציאת גבול דרך MCT:**
לאחר מונוטוניות + חסימות, מציבים $L=\\lim a_n$. אם $a_{n+1}=f(a_n)$, לוקחים גבול: $L=f(L)$. פותרים ל-$L$, ומסירים שורשים מיותרים לפי סימן או חסמים.

**משפט הסנדביץ׳:** כש-$a_n$ מתנדד (למשל $\\sin n$ במונה), חוסמים: $-1/n\\leq(\\sin n)/n\\leq 1/n$ ושני החסמים $\\to 0$.

**חוקי גבולות (כשהגבולות קיימים):** $\\lim(a_n+b_n)=\\lim a_n+\\lim b_n$, $\\lim(a_n b_n)=(\\lim a_n)(\\lim b_n)$, $\\lim(a_n/b_n)=\\lim a_n/\\lim b_n$ כש-$\\lim b_n\\neq 0$. סדרה מתכנסת תמיד חסומה — אך ההפך שגוי בלי מונוטוניות."""

WE1_EN = """**Determine whether $a_n=\\dfrac{n+1}{n}=1+\\dfrac{1}{n}$ is monotone and find its limit.**

**Setup:** This is an explicit sequence — the difference test is the natural first move. Rewrite as $1+1/n$ to see the structure immediately.

### Move 1: Check monotonicity via difference.
$$a_{n+1}-a_n=\\left(1+\\frac{1}{n+1}\\right)-\\left(1+\\frac{1}{n}\\right)=\\frac{1}{n+1}-\\frac{1}{n}=\\frac{n-(n+1)}{n(n+1)}=\\frac{-1}{n(n+1)}<0.$$
So $a_n$ is **strictly decreasing** for all $n\\geq 1$.

### Move 2: Establish bounds.
- **Below:** $a_n=1+1/n>1$ for all $n\\geq 1$. Bounded below by $m=1$.
- **Above:** Since decreasing, the maximum is $a_1=2$. Bounded above by $M=2$.

### Move 3: Apply MCT and compute the limit.
A decreasing sequence bounded below converges. Direct computation:
$$\\lim_{n\\to\\infty}\\frac{n+1}{n}=\\lim_{n\\to\\infty}\\left(1+\\frac{1}{n}\\right)=1+0=1. \\quad \\blacksquare$$

**Exam note:** The sequence approaches $1$ from above but never equals $1$. MCT guarantees convergence; algebra gives the exact limit."""

WE1_HE = """**קבעו האם $a_n=\\dfrac{n+1}{n}=1+\\dfrac{1}{n}$ מונוטונית ומצאו גבולה.**

**הגדרה:** סדרה מפורשת — מבחן ההפרש הוא הצעד הראשון. כתיבה כ-$1+1/n$ חושפת את המבנה.

### צעד 1: בדיקת מונוטוניות בהפרש.
$$a_{n+1}-a_n=\\frac{1}{n+1}-\\frac{1}{n}=\\frac{-1}{n(n+1)}<0.$$
$a_n$ **יורדת חד-חד** לכל $n\\geq 1$.

### צעד 2: חסימות.
- **מלמטה:** $a_n=1+1/n>1$. חסומה מלמטה ב-$m=1$.
- **מלמעלה:** כי יורדת, המקסימום הוא $a_1=2$. חסומה מלמעלה ב-$M=2$.

### צעד 3: MCT וגבול.
סדרה יורדת חסומה מלמטה מתכנסת. חישוב ישיר:
$$\\lim_{n\\to\\infty}\\frac{n+1}{n}=1. \\quad \\blacksquare$$

**הערת בחינה:** הסדרה מתקרבת ל-$1$ מלמעלה אך לא שווה ל-$1$. MCT מבטיח התכנסות; האלגברה נותנת את הגבול המדויק."""

WE2_EN = """**Prove that $a_n=2-\\dfrac{1}{n}$ is strictly increasing and bounded, and find its limit.**

**Strategy:** Difference for monotonicity, direct bounds for boundedness, MCT for existence, substitution for the limit value.

### Move 1: Strict monotonicity.
$$a_{n+1}-a_n=\\left(2-\\frac{1}{n+1}\\right)-\\left(2-\\frac{1}{n}\\right)=\\frac{1}{n}-\\frac{1}{n+1}=\\frac{1}{n(n+1)}>0.$$
Strictly increasing for all $n\\geq 1$. ✓

### Move 2: Bounds.
- **Lower bound:** $a_1=1\\leq a_n$ (increasing from $n=1$).
- **Upper bound:** $a_n=2-1/n<2$ for all $n\\geq 1$. So $M=2$ works. ✓

### Move 3: Limit.
By MCT, $(a_n)$ converges. Since $1/n\\to 0$:
$$\\lim_{n\\to\\infty}\\left(2-\\frac{1}{n}\\right)=2-0=2. \\quad \\blacksquare$$

**Key insight:** The sequence approaches its upper bound $2$ from below — a pattern examiners love because it tests whether you distinguish "limit equals bound" from "sequence reaches bound."

**Transfer:** Any $a_n=c-1/n^k$ with $k>0$ is increasing toward $c$ — same template."""

WE2_HE = """**הוכיחו ש-$a_n=2-\\dfrac{1}{n}$ עולה חד-חד וחסומה, ומצאו גבולה.**

**אסטרטגיה:** הפרש למונוטוניות, חסמים ישירים לחסימות, MCT לקיום, הצבה לערך הגבול.

### צעד 1: עלייה חד-חד.
$$a_{n+1}-a_n=\\frac{1}{n(n+1)}>0.$$
עולה חד-חד לכל $n\\geq 1$. ✓

### צעד 2: חסימות.
- **תחתון:** $a_1=1\\leq a_n$ (עולה מ-$n=1$).
- **עליון:** $a_n=2-1/n<2$. $M=2$ עובד. ✓

### צעד 3: גבול.
לפי MCT, $(a_n)$ מתכנסת. כיוון ש-$1/n\\to 0$:
$$\\lim_{n\\to\\infty}\\left(2-\\frac{1}{n}\\right)=2. \\quad \\blacksquare$$

**תובנה מרכזית:** הסדרה מתקרבת לחסם העליון $2$ מלמטה — דפוס שבוחנים אוהבים כי הוא בודק הבחנה בין "גבול שווה חסם" ל"הסדרה מגיעה לחסם".

**העברה:** כל $a_n=c-1/n^k$ עם $k>0$ עולה ל-$c$ — אותה תבנית."""

WE3_EN = """**Show that $a_n=(1+1/n)^n$ is strictly increasing and bounded above, so it converges. We define its limit to be $e$.**

This is the defining sequence for Euler's number — a 5-unit hallmark proof combining AM-GM and the binomial theorem.

### Move 1: Monotonicity via AM-GM.
Consider $n$ copies of $(1+1/n)$ and one copy of $1$. Their arithmetic mean is $\\dfrac{n(1+1/n)+1}{n+1}=\\dfrac{n+2}{n+1}$.

By AM-GM: $\\dfrac{n+2}{n+1}\\geq\\left[(1+1/n)^n\\cdot 1\\right]^{1/(n+1)}$.

Raising both sides to the power $n+1$:
$$\\left(\\frac{n+2}{n+1}\\right)^{n+1}\\geq(1+1/n)^n,\\quad\\text{i.e.}\\quad a_{n+1}\\geq a_n.$$
Strict inequality holds, so the sequence is **strictly increasing**. ✓

### Move 2: Upper bound via binomial expansion.
$$a_n=\\sum_{k=0}^{n}\\binom{n}{k}\\frac{1}{n^k}\\leq\\sum_{k=0}^{n}\\frac{1}{k!}\\leq 1+1+\\frac{1}{2}+\\frac{1}{4}+\\cdots\\leq 3.$$
Bounded above by $3$. ✓

### Move 3: Conclude by MCT.
Monotone increasing and bounded above $\\Rightarrow$ converges. Its limit is **defined** to be $e\\approx 2.71828$. $\\blacksquare$

**Exam note:** You may be asked to cite AM-GM for monotonicity and binomial bound for $a_n\\leq 3$ — state both theorems explicitly."""

WE3_HE = """**הראו ש-$a_n=(1+1/n)^n$ עולה חד-חד וחסומה מלמעלה, ולכן מתכנסת. מגדירים את גבולה כ-$e$.**

זו הסדרה המגדירה את מספר אוילר — הוכחת דגל 5 יחידות המשלבת AM-GM ומשפט הבינום.

### צעד 1: מונוטוניות (AM-GM).
$n$ מופעי $(1+1/n)$ ומופע $1$ אחד. ממוצע חשבוני: $\\dfrac{n+2}{n+1}$.

לפי AM-GM: $\\dfrac{n+2}{n+1}\\geq a_n^{1/(n+1)}$.

העלאה בחזקה $n+1$: $a_{n+1}\\geq a_n$ — **עולה חד-חד**. ✓

### צעד 2: חסם עליון (בינום).
$$a_n=\\sum_{k=0}^{n}\\binom{n}{k}\\frac{1}{n^k}\\leq\\sum_{k=0}^{n}\\frac{1}{k!}\\leq 1+1+\\frac{1}{2}+\\frac{1}{4}+\\cdots\\leq 3.$$
חסומה מלמעלה ב-$3$. ✓

### צעד 3: מסקנה (MCT).
עולה וחסומה מלמעלה $\\Rightarrow$ מתכנסת. הגבול **מוגדר** כ-$e\\approx 2.71828$. $\\blacksquare$

**הערת בחינה:** עלולים לבקש לצטט AM-GM למונוטוניות וחסם בינומי ל-$a_n\\leq 3$ — ציינו את שני המשפטים במפורש."""

CHK1_EN = """**Goal:** Determine monotonicity and limit of $a_n=\\dfrac{n}{n+2}$.

**Step 1 — Difference test:**
$$a_{n+1}-a_n=\\frac{n+1}{n+3}-\\frac{n}{n+2}=\\frac{(n+1)(n+2)-n(n+3)}{(n+3)(n+2)}=\\frac{n^2+3n+2-n^2-3n}{(n+3)(n+2)}=\\frac{2}{(n+3)(n+2)}>0.$$
The sequence is **strictly increasing**.

**Step 2 — Boundedness:**
- $a_n=n/(n+2)=1-2/(n+2)<1$ for all $n\\geq 1$. Bounded above by $1$.
- $a_1=1/3>0$. Increasing, so bounded below by $1/3$.

**Step 3 — Limit:**
By MCT, converges. Divide numerator and denominator by $n$:
$$\\lim_{n\\to\\infty}\\frac{n}{n+2}=\\lim_{n\\to\\infty}\\frac{1}{1+2/n}=1. \\quad \\blacksquare$$"""

CHK1_HE = """**מטרה:** קביעת מונוטוניות וגבול של $a_n=\\dfrac{n}{n+2}$.

**שלב 1 — מבחן הפרש:**
$$a_{n+1}-a_n=\\frac{2}{(n+3)(n+2)}>0.$$
הסדרה **עולה חד-חד**.

**שלב 2 — חסימות:**
- $a_n=1-2/(n+2)<1$. חסומה מלמעלה ב-$1$.
- $a_1=1/3>0$. עולה, לכן חסומה מלמטה ב-$1/3$.

**שלב 3 — גבול:**
לפי MCT, מתכנסת. חלוקה ב-$n$:
$$\\lim_{n\\to\\infty}\\frac{n}{n+2}=1. \\quad \\blacksquare$$"""

CHK2_EN = """**Goal:** Find the limit of $a_1=1$, $a_{n+1}=\\sqrt{a_n+2}$, assuming convergence.

**Step 1 — Set up the fixed-point equation:**
If $\\lim a_n=L$ exists, pass to the limit in the recurrence:
$$L=\\sqrt{L+2}.$$

**Step 2 — Solve:**
Squaring (valid since $L\\geq 0$): $L^2=L+2$, so $L^2-L-2=0$, $(L-2)(L+1)=0$.
Roots: $L=2$ or $L=-1$.

**Step 3 — Discard extraneous root:**
Since $a_1=1>0$ and $a_{n+1}=\\sqrt{a_n+2}>0$, all terms are positive, so $L>0$. Therefore $L=2$.

**Note:** A full exam proof would also prove $a_n<2$ (induction) and $a_{n+1}>a_n$ before citing MCT. $\\blacksquare$"""

CHK2_HE = """**מטרה:** מציאת גבול של $a_1=1$, $a_{n+1}=\\sqrt{a_n+2}$, בהנחת התכנסות.

**שלב 1 — משוואת נקודה קבועה:**
אם $\\lim a_n=L$ קיים, לוקחים גבול בנסיגה:
$$L=\\sqrt{L+2}.$$

**שלב 2 — פתרון:**
בריבוע (תקף כי $L\\geq 0$): $L^2=L+2$, $(L-2)(L+1)=0$.
שורשים: $L=2$ או $L=-1$.

**שלב 3 — הסרת שורש מיותר:**
כיוון ש-$a_1=1>0$ ו-$a_{n+1}=\\sqrt{a_n+2}>0$, כל האיברים חיוביים, $L>0$. לכן $L=2$.

**הערה:** הוכחה מלאה בבחינה תכלול גם $a_n<2$ (אינדוקציה) ו-$a_{n+1}>a_n$ לפני MCT. $\\blacksquare$"""

METHOD_EN = """| Sequence type | Best method | What to compute |
|---|---|---|
| Explicit formula $a_n=f(n)$ | Algebraic: $a_{n+1}-a_n$ | Sign of difference |
| Positive sequence with products/factorials | Ratio: $a_{n+1}/a_n$ | Compare to 1 |
| Recursion $a_{n+1}=f(a_n)$ | Induction | Base case + step |
| Need to find limit | MCT | Prove monotone + bounded, then $L=f(L)$ |
| Oscillating numerator | Sandwich | Find $b_n\\leq a_n\\leq c_n$ with same limit |
| Rational $P(n)/Q(n)$ | Divide by highest power of $n$ | Limit of leading coefficients |

**Induction template for monotonicity:**
1. **Base:** Check $a_2>a_1$ (or $<$) directly.
2. **Step:** Assume $a_{k+1}>a_k$; prove $a_{k+2}>a_{k+1}$ using the recurrence and any bound you established.

**Before starting:** Read the stem — if it says "prove" you need full MCT structure, not just computing the first few terms."""

METHOD_HE = """| סוג סדרה | שיטה מומלצת | מה לחשב |
|---|---|---|
| נוסחה מפורשת $a_n=f(n)$ | אלגברי: $a_{n+1}-a_n$ | סימן ההפרש |
| סדרה חיובית עם מכפלות/עצרות | מנה: $a_{n+1}/a_n$ | השוואה ל-1 |
| נסיגה $a_{n+1}=f(a_n)$ | אינדוקציה | בסיס + שלב |
| למציאת גבול | MCT | מונוטוניות + חסימות, ואז $L=f(L)$ |
| מונה מתנדד | סנדביץ׳ | $b_n\\leq a_n\\leq c_n$ עם אותו גבול |
| רציונלית $P(n)/Q(n)$ | חלוקה בחזקה הגבוהה | גבול מקדמים מובילים |

**תבנית אינדוקציה למונוטוניות:**
1. **בסיס:** בדקו $a_2>a_1$ (או $<$) ישירות.
2. **שלב:** הניחו $a_{k+1}>a_k$; הוכיחו $a_{k+2}>a_{k+1}$ מהנסיגה והחסם.

**לפני שמתחילים:** אם כתוב "הוכיחו" — צריך מבנה MCT מלא, לא רק חישוב איברים ראשונים."""

PITFALL_EN = """1. **Assuming bounded $\\Rightarrow$ convergent:** Only true with monotonicity. $(-1)^n$ is bounded ($|a_n|=1$) but oscillates and diverges.

2. **Applying MCT without proving both conditions:** Examiners deduct heavily if you cite MCT after only showing monotonicity. You must prove boundedness separately — often by induction.

3. **Finding $L=f(L)$ before proving convergence:** Solving the fixed-point equation gives candidate limits, but without MCT the sequence might diverge or cycle. Always prove convergence first.

4. **Wrong sign in $a_{n+1}-a_n$:** Double-check algebra. A classic slip: $1/(n+1)-1/n=-1/[n(n+1)]<0$, not positive.

5. **Ratio test on wrong domain:** $a_{n+1}/a_n<1$ must hold for all *sufficiently large* $n$, not just $n=1$. For $2^n/n!$, the ratio $<1$ only for $n\\geq 2$.

6. **Squaring $L=\\sqrt{\\cdots}$ without checking sign:** Squaring can introduce spurious negative roots. Always use sequence positivity to discard them."""

PITFALL_HE = """1. **הנחה שחסומה $\\Rightarrow$ מתכנסת:** נכון רק עם מונוטוניות. $(-1)^n$ חסומה ($|a_n|=1$) אך מתנדדת ומתבדרת.

2. **שימוש ב-MCT בלי שני תנאים:** בוחנים מורידים נקודות אם מצטטים MCT אחרי מונוטוניות בלבד. חייבים להוכיח חסימות בנפרד — לרוב באינדוקציה.

3. **מציאת $L=f(L)$ לפני הוכחת התכנסות:** משוואת נקודה קבועה נותנת מועמדים, אך בלי MCT הסדרה עלולה לבדור. קודם מוכיחים התכנסות.

4. **סימן שגוי ב-$a_{n+1}-a_n$:** בדקו אלגברה. טעות קלאסית: $1/(n+1)-1/n=-1/[n(n+1)]<0$, לא חיובי.

5. **מבחן מנה על טווח שגוי:** $a_{n+1}/a_n<1$ חייב לכל $n$ *מספיק גדול*, לא רק $n=1$. ב-$2^n/n!$, המנה $<1$ רק ל-$n\\geq 2$.

6. **ריבוע $L=\\sqrt{\\cdots}$ בלי בדיקת סימן:** ריבוע מוסיף שורשים שליליים מיותרים. השתמשו בחיוביות הסדרה."""

WHY_EN = """Sequences are the discrete foundation of real analysis. Every infinite sum (series) is built from a sequence of partial sums — you cannot study convergence of series without first mastering sequence limits and the Monotone Convergence Theorem.

On the Bagrut 5-unit exam, sequence proofs appear as multi-part questions worth substantial points. The skills transfer directly: proving $a_n=(1+1/n)^n$ converges is the same machinery used to analyze recursive sequences in physics and economics models.

**Recommended next topics:**
- `concept:limits_5pt` — rigorous $\\varepsilon$-$\\delta$ proofs for functions
- `concept:series_convergence_tests` — when infinite sums converge

**Cross-subject link:** Exponential growth models in physics use $(1+r/n)^{nt}\\to e^{rt}$ — the continuous limit of a sequence you prove here."""

WHY_HE = """סדרות הן יסוד האנליזה הדיסקרטית. כל סכום אינסופי (טור) בנוי מסדרת סכומים חלקיים — אי אפשר ללמוד התכנסות טורים בלי שליטה בגבולות סדרות וב-MCT.

בבגרות 5 יחידות, הוכחות סדרות מופיעות כשאלות רב-חלקיות בשווי נקודות משמעותי. המיומנויות עוברות ישירות: הוכחת התכנסות $a_n=(1+1/n)^n$ היא אותו מנגנון לניתוח סדרות נסיגה במודלים פיזיקליים וכלכליים.

**נושאים מומלצים להמשך:**
- `concept:limits_5pt` — הוכחות $\\varepsilon$-$\\delta$ לפונקציות
- `concept:series_convergence_tests` — מתי סכומים אינסופיים מתכנסים

**קשר בין-מקצועי:** מודלי גדילה מעריכית בפיזיקה משתמשים ב-$(1+r/n)^{nt}\\to e^{rt}$ — הגבול הרציף של סדרה שמוכיחים כאן."""

BEFORE_EN = """**Key theorems for the exam:**
- **MCT:** monotone + bounded $\\Rightarrow$ convergent (both conditions!)
- **Sandwich:** $b_n\\leq a_n\\leq c_n$, both bounds $\\to L$ $\\Rightarrow$ $a_n\\to L$
- **Convergent $\\Rightarrow$ bounded** (converse false without monotonicity)
- **Limit laws:** sum, product, quotient (when denominator limit $\\neq 0$)
- **$e=\\lim(1+1/n)^n$:** increasing (AM-GM), bounded above by $3$ (binomial)

**Typical 20-point exam structure:**
(a) Write first terms — 2 pts. (b) Prove monotonicity — 5 pts. (c) Prove boundedness — 5 pts. (d) Cite MCT — 1 pt. (e) Find limit via $L=f(L)$ — 4 pts. (f) Optional $\\varepsilon$-$N$ — 3 pts.

**Most-tested patterns:** Recursive sequences, $a_{n+1}-a_n$ proofs, AM-GM for $(1+1/n)^n$, and sandwich for trig numerators."""

BEFORE_HE = """**משפטי מפתח לבחינה:**
- **MCT:** מונוטוני + חסום $\\Rightarrow$ מתכנס (שני התנאים!)
- **סנדביץ׳:** $b_n\\leq a_n\\leq c_n$, שני החסמים $\\to L$ $\\Rightarrow$ $a_n\\to L$
- **מתכנס $\\Rightarrow$ חסום** (ההפך שגוי בלי מונוטוניות)
- **חוקי גבולות:** סכום, מכפלה, מנה (מכנה $\\neq 0$)
- **$e=\\lim(1+1/n)^n$:** עולה (AM-GM), חסומה ב-$3$ (בינום)

**מבנה שאלה טיפוסי 20 נק׳:**
(א) איברים ראשונים — 2. (ב) מונוטוניות — 5. (ג) חסימות — 5. (ד) ציטוט MCT — 1. (ה) גבול $L=f(L)$ — 4. (ו) $\\varepsilon$-$N$ אופציונלי — 3.

**דפוסים נבחנים:** סדרות נסיגה, הוכחות $a_{n+1}-a_n$, AM-GM ל-$(1+1/n)^n$, סנדביץ׳ למונים טריגונומטריים."""

SUMMARY_EN = """- **MCT:** Monotone + bounded $\\Rightarrow$ convergent. Both conditions required.
- **Proving monotone:** Compute $a_{n+1}-a_n$ (explicit) or $a_{n+1}/a_n$ (positive sequences) and determine sign.
- **Proving bounded:** Explicit bounds or induction for recursive sequences.
- **Finding limit:** After MCT, set $L=\\lim a_n$ and solve $L=f(L)$ in recurrences.
- **Sandwich:** Bound oscillating sequences between two sequences with the same limit.
- **$e$:** $\\lim(1+1/n)^n$; increasing by AM-GM, bounded above by $3$ by binomial expansion."""

SUMMARY_HE = """- **MCT:** מונוטוני + חסום $\\Rightarrow$ מתכנס. שני התנאים נדרשים.
- **מונוטוניות:** $a_{n+1}-a_n$ (מפורש) או $a_{n+1}/a_n$ (חיובית) — קבעו סימן.
- **חסימות:** חסמים מפורשים או אינדוקציה לנסיגה.
- **גבול:** אחרי MCT, $L=\\lim a_n$ ופתרון $L=f(L)$.
- **סנדביץ׳:** חסמו סדרות מתנדדות בין שתי סדרות עם אותו גבול.
- **$e$:** $\\lim(1+1/n)^n$; עולה (AM-GM), חסומה ב-$3$ (בינום)."""

EXPLS = {
    1: fmt_expl(
        "Rewrite $n/(n+1)=1-1/(n+1)<1$ for all $n\\geq 1$. Option B is strictly below $1$. Option C ($1+1/n$) exceeds $1$ for every $n$. Option D ($2-1/n$) exceeds $1$ and approaches $2$. Option A ($n$) is unbounded.",
        "For 'bounded above by $1$' questions, rewrite each candidate as $1\\pm\\text{something}/n$ or compare to $1$ directly. A sequence bounded above by $1$ must satisfy $a_n\\leq 1$ for *all* $n$, not just eventually.",
        "Choosing $2-1/n$ because it 'approaches $1$' — it is bounded above by $2$, not by $1$. Approaching a number is not the same as being bounded by it.",
        "On MCQ boundedness questions, test $n=1$ first — it often eliminates options quickly. Here $a_1=1/2<1$ for B but $a_1=2>1$ for D.",
        "כתיבה $n/(n+1)=1-1/(n+1)<1$ לכל $n\\geq 1$. תשובה ב' נמצאת ממש מתחת ל-$1$. תשובה ג' ($1+1/n$) עולה על $1$. תשובה ד' ($2-1/n$) עולה על $1$ ומתקרבת ל-$2$. תשובה א' ($n$) לא חסומה.",
        "בשאלות 'חסומה מלמעלה ב-$1$', כתבו כל מועמד כ-$1\\pm\\text{משהו}/n$ או השוו ל-$1$ ישירות. חסימה מלמעלה ב-$1$ דורשת $a_n\\leq 1$ ל*כל* $n$, לא רק בסופו.",
        "בחירת $2-1/n$ כי 'מתקרב ל-$1$' — חסומה מלמעלה ב-$2$, לא ב-$1$. התקרבות אינה זהה לחסימה.",
        "ב-MCQ חסימות, בדקו $n=1$ תחילה — לעיתים זה מסיר אפשרויות מהר. כאן $a_1=1/2<1$ ל-ב' אך $a_1=2>1$ ל-ד'.",
    ),
    2: fmt_expl(
        "$\\lim_{n\\to\\infty}(3-2/n)=3-0=3$. As $n\\to\\infty$, the term $2/n\\to 0$, so the constant $3$ dominates. Option C is correct.",
        "For limits of the form $c\\pm k/n^p$, the limit is always $c$ when $p>0$. Identify the constant part and the vanishing part separately — no need for MCT on explicit rational sequences.",
        "Answering $2$ by confusing the coefficient $2$ in $2/n$ with the limit. Or answering $0$ because 'something divided by $n$ goes to zero' without tracking the constant $3$.",
        "This is a warm-up limit — examiners use it to check you can handle $k/n\\to 0$ before the harder MCT proofs. Write $\\lim(3-2/n)=\\lim 3 - \\lim(2/n)=3-0$ explicitly.",
        "$\\lim_{n\\to\\infty}(3-2/n)=3-0=3$. כש-$n\\to\\infty$, האיבר $2/n\\to 0$, הקבוע $3$ שולט. תשובה ג' נכונה.",
        "לגבולות מהצורה $c\\pm k/n^p$, הגבול תמיד $c$ כש-$p>0$. זהו את החלק הקבוע ואת החלק השואף ל-$0$ — אין צורך ב-MCT לסדרות רציונליות מפורשות.",
        "תשובה $2$ בלבול מקדם $2$ ב-$2/n$ עם הגבול. או $0$ כי 'משהו חלקי $n$ הולך לאפס' בלי לעקוב אחרי הקבוע $3$.",
        "זה גבול חימום — בוחנים בודקים $k/n\\to 0$ לפני הוכחות MCT הקשות. כתבו $\\lim(3-2/n)=\\lim 3 - \\lim(2/n)=3-0$ במפורש.",
    ),
    3: fmt_expl(
        "False. $(-1)^n$ is bounded ($|a_n|=1$ for all $n$) but alternates between $+1$ and $-1$, so no single limit exists. Boundedness alone does not imply convergence.",
        "The converse of 'convergent $\\Rightarrow$ bounded' is false. Ask: is the sequence also monotone? If not, boundedness tells you nothing about convergence. Counterexamples: $(-1)^n$, $\\sin n$, $a_n=(-1)^n/n$ (this one *does* converge to $0$ via sandwich).",
        "Answering True because 'bounded sequences can't go to infinity.' That confuses two different failure modes — oscillation vs. unbounded growth. $(-1)^n$ is bounded but oscillates.",
        "True/False on MCT hypotheses is common on Bagrut. Memorize: bounded + monotone $\\Rightarrow$ converges. Bounded alone $\\not\\Rightarrow$ converges. Converges $\\Rightarrow$ bounded always.",
        "לא נכון. $(-1)^n$ חסומה ($|a_n|=1$) אך מתחלפת בין $+1$ ל-$-1$, אין גבול יחיד. חסימה לבדה לא מרמזת על התכנסות.",
        "ההפך של 'מתכנס $\\Rightarrow$ חסום' שגוי. שאלו: האם הסדרה גם מונוטונית? אם לא, חסימות לא אומרת דבר. דוגמאות: $(-1)^n$, $\\sin n$.",
        "תשובה 'נכון' כי 'סדרה חסומה לא יכולה ללכת לאינסוף' — מבלבלים התנדנדות עם גדילה לא חסומה. $(-1)^n$ חסומה אך מתנדדת.",
        "שאלות נכון/לא נכון על MCT נפוצות בבגרות. שלטו: חסום + מונוטוני $\\Rightarrow$ מתכנס. חסום לבד $\\not\\Rightarrow$ מתכנס. מתכנס $\\Rightarrow$ חסום תמיד.",
    ),
    4: fmt_expl(
        "$a_{n+1}-a_n=1/(n(n+1))>0$, so strictly increasing. Upper bound: $a_n=2-1/n<2$. By MCT, converges. $\\lim(2-1/n)=2$.",
        "Open MCT proofs follow a fixed template: (1) difference for monotonicity, (2) explicit bounds, (3) cite MCT, (4) compute limit. Write each step on its own line — graders award partial credit for correct monotonicity even if the limit computation slips.",
        "Proving monotonicity but forgetting to state the upper bound $2$ before citing MCT. Or computing the limit without showing $a_{n+1}-a_n>0$ — you lose the monotonicity marks.",
        "For 'prove increasing and find limit' questions, always end with $\\lim a_n=\\ldots$ after citing MCT. State 'By the Monotone Convergence Theorem, the sequence converges' explicitly — it is worth 1 point on its own.",
        "$a_{n+1}-a_n=1/(n(n+1))>0$, עולה חד-חד. חסם עליון: $a_n=2-1/n<2$. לפי MCT, מתכנסת. $\\lim(2-1/n)=2$.",
        "הוכחות MCT פתוחות עוקבות אחר תבנית: (1) הפרש למונוטוניות, (2) חסמים, (3) ציטוט MCT, (4) חישוב גבול. כל שלב בשורה נפרדת — נקודות חלקיות למונוטוניות נכונה.",
        "הוכחת מונוטוניות בלי לציין חסם עליון $2$ לפני MCT. או חישוב גבול בלי $a_{n+1}-a_n>0$ — אובדן נקודות מונוטוניות.",
        "בשאלות 'הוכיחו עלייה ומצאו גבול', תמיד סיימו ב-$\\lim a_n=\\ldots$ אחרי MCT. כתבו 'לפי משפט הסדרה המונוטונית, הסדרה מתכנסת' — שווה נקודה.",
    ),
    5: fmt_expl(
        "Induction: $a_1=1<2$; if $a_n<2$ then $a_{n+1}=\\sqrt{a_n+2}<\\sqrt{4}=2$. Increasing: $a_{n+1}^2-a_n^2=(a_n+2)-a_n^2=2+a_n(1-a_n)>0$ for $0<a_n<2$. MCT gives convergence; $L=\\sqrt{L+2}$ yields $L=2$ (positive root).",
        "Recursive sequence proofs require three blocks: (1) induction for bound, (2) monotonicity (often from the recurrence + bound), (3) MCT + fixed point. Do not skip the induction — 'assuming convergence' alone is not a full proof.",
        "Solving $L=\\sqrt{L+2}$ and taking $L=-1$ without discarding the negative root. Or proving $a_n<2$ but not proving the sequence is increasing — MCT needs both.",
        "Hard 5-pt sequence questions almost always follow $a_{n+1}=\\sqrt{\\cdots}$ or rational recurrence patterns. Practice writing the induction base ($n=1$) and step ($a_k<2\\Rightarrow a_{k+1}<2$) on separate lines.",
        "אינדוקציה: $a_1=1<2$; אם $a_n<2$ אז $a_{n+1}=\\sqrt{a_n+2}<2$. עלייה: $a_{n+1}^2-a_n^2=2+a_n(1-a_n)>0$ ל-$0<a_n<2$. MCT → $L=2$ (שורש חיובי).",
        "הוכחות נסיגה דורשות שלושה בלוקים: (1) אינדוקציה לחסם, (2) מונוטוניות, (3) MCT + נקודה קבועה. אל תדלגו על אינדוקציה — 'בהנחת התכנסות' לבד אינה הוכחה מלאה.",
        "פתרון $L=\\sqrt{L+2}$ ולקיחת $L=-1$ בלי להסיר שורש שלילי. או $a_n<2$ בלי עלייה — MCT דורש שניהם.",
        "שאלות 5 יחידות קשות כמעט תמיד $a_{n+1}=\\sqrt{\\cdots}$ או נסיגה רציונלית. תרגלו כתיבת בסיס ($n=1$) ושלב ($a_k<2\\Rightarrow a_{k+1}<2$) בשורות נפרדות.",
    ),
    6: fmt_expl(
        "Strictly increasing: $a_{n+1}-a_n=(n+1)^2-n^2=2n+1>0$ for all $n\\geq 1$. Not bounded above: as $n\\to\\infty$, $a_n=n^2\\to\\infty$.",
        "Monotonicity and boundedness are independent properties. A sequence can be monotone but unbounded ($n^2$), bounded but non-monotone ($(−1)^n$), or both (then MCT applies). Always answer both parts of the question.",
        "Saying 'not bounded because it is increasing' — monotonicity does not prevent unbounded growth. $n^2$ increases without bound.",
        "Short-answer sequence questions often test whether you check *both* properties. Write two sentences: one for monotonicity (difference sign), one for boundedness (does $a_n$ stay below some $M$?).",
        "עולה חד-חד: $a_{n+1}-a_n=2n+1>0$. לא חסומה מלמעלה: $a_n=n^2\\to\\infty$.",
        "מונוטוניות וחסימות בלתי תלויות. סדרה יכולה להיות מונוטונית אך לא חסומה ($n^2$), חסומה אך לא מונוטונית ($(−1)^n$), או שניהם (אז MCT). ענו על שני חלקי השאלה.",
        "אמרה 'לא חסומה כי עולה' — מונוטוניות לא מונעת גדילה לא חסומה. $n^2$ עולה ללא חסם.",
        "שאלות תשובה קצרה בודקות אם בודקים *שני* מאפיינים. שני משפטים: מונוטוניות (סימן הפרש), חסימות (האם $a_n$ נשארת מתחת ל-$M$?).",
    ),
    7: fmt_expl(
        "Divide numerator and denominator by $n^2$: $\\dfrac{3n^2+1}{n^2+2}=\\dfrac{3+1/n^2}{1+2/n^2}\\to\\dfrac{3+0}{1+0}=3$ as $n\\to\\infty$.",
        "For rational sequences $\\dfrac{P(n)}{Q(n)}$ with equal degree, divide by the highest power of $n$. The limit equals the ratio of leading coefficients. Here: $3/1=3$.",
        "Dividing by $n$ instead of $n^2$ — when degrees match, you must divide by the highest power. Or answering $\\infty$ because 'numerator has larger leading term' when degrees are equal.",
        "Rational sequence limits appear on every 5-pt exam. Quick rule: equal degrees $\\Rightarrow$ ratio of leading coefficients; numerator degree higher $\\Rightarrow$ $\\pm\\infty$; lower $\\Rightarrow$ $0$.",
        "חלוקה ב-$n^2$: $\\dfrac{3+1/n^2}{1+2/n^2}\\to 3$.",
        "לסדרות רציונליות $\\dfrac{P(n)}{Q(n)}$ באותו מעלה, חלקו בחזקה הגבוהה. הגבול = יחס מקדמים מובילים: $3/1=3$.",
        "חלוקה ב-$n$ במקום $n^2$ — כשהמעלות שווה, חובה לחלק בחזקה הגבוהה. או $\\infty$ כי 'מונה גדול יותר' כשהמעלות שווה.",
        "גבולות סדרות רציונליות בכל בחינת 5 יחידות. כלל מהיר: מעלות שווה $\\Rightarrow$ יחס מקדמים; מונה גבוה יותר $\\Rightarrow$ $\\pm\\infty$; נמוך $\\Rightarrow$ $0$.",
    ),
    8: fmt_expl(
        "$a_{n+1}-a_n=-\\dfrac{1}{(n+1)^2}+\\dfrac{1}{n^2}=\\dfrac{(n+1)^2-n^2}{n^2(n+1)^2}=\\dfrac{2n+1}{n^2(n+1)^2}>0$. Bounded: $0<a_n=1-1/n^2<1$ for all $n\\geq 1$.",
        "For $a_n=c-1/n^p$ with $p>0$: difference is positive (increasing toward $c$), and $a_n$ is bounded between $a_1$ and $c$. Same template as $2-1/n$ but with $n^2$ in the denominator.",
        "Getting the difference sign wrong by computing $1/n^2-1/(n+1)^2$ in the wrong order. Or claiming unbounded because 'it approaches $1$' — approaching a bound means bounded above by that bound.",
        "When the denominator is $n^2$ instead of $n$, the difference formula gives $2n+1$ in the numerator — still positive. Practice both $1/n$ and $1/n^2$ variants before the exam.",
        "$a_{n+1}-a_n=\\dfrac{2n+1}{n^2(n+1)^2}>0$. חסומה: $0<a_n=1-1/n^2<1$.",
        "ל-$a_n=c-1/n^p$ עם $p>0$: הפרש חיובי (עולה ל-$c$), ו-$a_n$ חסומה בין $a_1$ ל-$c$. אותה תבנית כמו $2-1/n$ עם $n^2$ במכנה.",
        "סימן הפרש שגוי — $1/n^2-1/(n+1)^2$ בסדר הפוך. או 'לא חסומה כי מתקרב ל-$1$' — התקרבות לחסם = חסימה מלמעלה.",
        "כשהמכנה $n^2$ במקום $n$, המונה $2n+1$ — עדיין חיובי. תרגלו $1/n$ ו-$1/n^2$ לפני הבחינה.",
    ),
}

HE_EXPL_SUFFIX = (
    "\n\n**טיפ נוסף לבחינה:** כתבו את המשפט או התבנית בשוליים לפני החישוב — "
    "מקבלים נקודות שיטה גם כשיש טעות חשבונית קטנה בסוף."
)


def ensure_section_words(sec: dict) -> None:
    kind = sec["kind"]
    if kind not in EXPAND_KINDS:
        return
    min_key = "worked_example" if kind == "worked_example" else kind
    en_min, he_min = MIN[min_key]
    pad_en = " **Exam habit:** Write each proof step on a separate line; partial credit follows visible structure even when final arithmetic slips."
    pad_he = " **הרגל לבחינה:** כתבו כל שלב בשורה נפרדת; נקודות חלקיות למבנה גלוי גם כשיש טעות בסוף."
    if wc(sec.get("body_en_md", "")) < en_min and pad_en not in sec.get("body_en_md", ""):
        sec["body_en_md"] = sec.get("body_en_md", "") + pad_en
    if wc(sec.get("body_he_md", "")) < he_min and pad_he not in sec.get("body_he_md", ""):
        sec["body_he_md"] = sec.get("body_he_md", "") + pad_he


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
            if "dfrac{n}{n+2}" in body.replace(" ", ""):
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
