#!/usr/bin/env python3
"""Expand combinatorics_5pt.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/combinatorics_5pt.json"

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


INTRO_EN = """Combinatorics at the **5-unit Bagrut** level goes beyond basic permutations and combinations. You will face multi-step counting with **restrictions** (digits, adjacency, required members), **inclusion–exclusion** for unions of sets, **circular arrangements**, and **combinatorial proofs** of binomial identities.

These topics typically appear as a dedicated question block worth **20–28 points**. Examiners reward a clear **strategy statement** ("complement", "block method", "case split") before arithmetic — not just a final number. Partial credit is common when the setup is correct even if arithmetic slips.

The three pillars of this lesson are:

1. **Inclusion–exclusion** — count $|A \\cup B \\cup C|$ without double-counting overlaps; essential for "divisible by 2 or 3" and survey problems.
2. **Advanced placement** — non-adjacent seating, multiset permutations ($n!/(n_1!\\cdots n_k!)$), and digit problems with leading-zero rules.
3. **Combinatorial identities** — prove $\\sum_{k=0}^n\\binom{n}{k}=2^n$ by counting subsets twice; connect to the binomial theorem at $x=1$.

Master the **decision fork** first: complement vs direct count, linear vs circular, ordered vs unordered. Then the formulas become reliable tools rather than guesswork."""

INTRO_HE = """**קומבינטוריקה ברמת בגרות 5 יחידות** חורגת מתמורות וצירופים בסיסיים. תתמודדו עם ספירה רב-שלבית עם **אילוצים** (ספרות, שכנות, חברים נדרשים), **הכלה–אי-הכלה** לאיחודי קבוצות, **סידורים מעגליים** ו**הוכחות קומבינטוריות** של זהויות בינומיות.

נושאים אלה מופיעים בדרך כלל כבлок שאלה ייעודי בשווי **20–28 נקודות**. בוחנים מעריכים **הצהרת אסטרטגיה** ברורה ("משלים", "שיטת בלוק", "פיצול מקרים") לפני החשבון — לא רק מספר סופי. נקודות חלקיות נפוצות כשההגדרה נכונה גם אם יש טעות חשבונית.

שלושת עמודי השיעור:

1. **הכלה–אי-הכלה** — ספירת $|A \\cup B \\cup C|$ בלי ספירה כפולה; חיוני ל"מתחלק ב-2 או ב-3" ולסקרים.
2. **מיקום מתקדם** — ישיבה ללא שכנים, תמורות מולטינומיאל ($n!/(n_1!\\cdots n_k!)$), ובעיות ספרות עם כלל אפס מוביל.
3. **זהויות קומבינטוריות** — הוכחת $\\sum_{k=0}^n\\binom{n}{k}=2^n$ בספירה כפולה; קשר לבינום ניוטון ב-$x=1$.

שלטו קודם ב**מזלג ההחלטה**: משלים מול ספירה ישירה, ליניארי מול מעגלי, מסודר מול לא מסודר. אז הנוסחאות הופכות לכלים אמינים ולא לניחוש."""

DEF_EN = """**Permutations (ordered, no repetition):**
- $n$ distinct objects in a row: $n!$
- Choose and arrange $r$ from $n$: $P(n,r)=\\dfrac{n!}{(n-r)!}$
- With identical elements (multiset): $\\dfrac{n!}{n_1!\\,n_2!\\cdots n_k!}$
- Circular (fix one person): $(n-1)!$

**Combinations (unordered, no repetition):**
$$\\binom{n}{r}=\\dfrac{n!}{r!(n-r)!}, \\quad \\binom{n}{r}=\\binom{n}{n-r} \\text{ (symmetry)}$$

**Inclusion–Exclusion Principle:**
$$|A \\cup B| = |A| + |B| - |A \\cap B|$$
$$|A \\cup B \\cup C| = |A|+|B|+|C| - |A \\cap B| - |A \\cap C| - |B \\cap C| + |A \\cap B \\cap C|$$
Generally: add single sets, subtract pairwise intersections, add triple intersection, and so on (alternating signs).

**Binomial theorem:** $(1+x)^n=\\sum_{k=0}^n\\binom{n}{k}x^k$. Setting $x=1$: $\\sum_{k=0}^n\\binom{n}{k}=2^n$.

**Pascal's identity:** $\\binom{n}{k}+\\binom{n}{k+1}=\\binom{n+1}{k+1}$.

**Adjacent-pair block:** Treat two people who must (or must not) sit together as one unit; multiply internal order by $2$ when the block can flip (AB vs BA).

**Digit-counting rule:** For $k$-digit numbers, the leading digit has at most 9 choices (1–9); later positions may include 0 once it is not already used. Always count position-by-position rather than applying $P(10,k)$ blindly."""

DEF_HE = """**תמורות (מסודר, ללא חזרה):**
- $n$ אובייקטים שונים בשורה: $n!$
- בחירה וסידור של $r$ מ-$n$: $P(n,r)=\\dfrac{n!}{(n-r)!}$
- עם איברים זהים (מולטיסט): $\\dfrac{n!}{n_1!\\,n_2!\\cdots n_k!}$
- מעגלי (קביעת אדם אחד): $(n-1)!$

**צירופים (לא מסודר, ללא חזרה):**
$$\\binom{n}{r}=\\dfrac{n!}{r!(n-r)!}, \\quad \\binom{n}{r}=\\binom{n}{n-r} \\text{ (סימטריה)}$$

**עיקרון ההכלה–אי-הכלה:**
$$|A \\cup B| = |A| + |B| - |A \\cap B|$$
$$|A \\cup B \\cup C| = |A|+|B|+|C| - |A \\cap B| - |A \\cap C| - |B \\cap C| + |A \\cap B \\cap C|$$
בכלליות: מוסיפים קבוצות בודדות, מחסרים חיתוכים זוגיים, מוסיפים חיתוך משולש — סימנים מתחלפים.

**בינום ניוטון:** $(1+x)^n=\\sum_{k=0}^n\\binom{n}{k}x^k$. ל-$x=1$: $\\sum_{k=0}^n\\binom{n}{k}=2^n$.

**זהות פסקל:** $\\binom{n}{k}+\\binom{n}{k+1}=\\binom{n+1}{k+1}$.

**בלוק שכנים:** שני אנשים שחייבים (או לא יכולים) לשבת יחד — יחידה אחת; מכפילים ב-$2$ לסדר פנימי (AB מול BA).

**כלל ספירת ספרות:** במספרים בני $k$ ספרות, הספרה המובילה — לכל היותר 9 (1–9); מקומות מאוחרים יכולים לכלול 0 אם לא בשימוש. ספרו מיקום-אחר-מיקום, לא $P(10,k)$ בלי מחשבה."""

THEORY_EN = """**Strategy for "at least one" problems:**
Count the **complement** — instead of "at least one with property $P$", compute: (total) $-$ (none with $P$). Example: 4-letter words over $\\{a,b,c\\}$ with at least one $a$: total $3^4=81$, none with $a$ is $2^4=16$, answer $81-16=65$.

**Non-adjacent placement (linear):**
To place $k$ restricted objects among $n$ positions so no two of the $k$ are adjacent:
1. Arrange the remaining $n-k$ objects: $(n-k)!$ ways.
2. This creates $n-k+1$ gaps (including ends).
3. Choose $k$ gaps: $\\binom{n-k+1}{k}$.
4. Arrange the $k$ objects: $k!$.
Combined: $\\binom{n-k+1}{k}\\cdot k!$ for linear arrangements.

**Circular arrangement with restrictions:**
Total circular permutations of $n$ people: $(n-1)!$. For "A and B NOT adjacent": count total minus adjacent (treat A,B as block → $(n-2)!\\times 2$ internal orders).

**Inclusion–exclusion workflow:**
1. Define sets $A_i$ clearly (e.g., $A$ = divisible by 2, $B$ = divisible by 3).
2. Compute each $|A_i|$ and relevant intersections ($|A \\cap B|$ = divisible by $\\text{lcm}(2,3)=6$).
3. Apply the formula; verify $|A \\cup B| \\leq |U|$ (universe size).

**Combinatorial proof template:**
Interpret LHS and RHS as two ways to count the same set. For $\\sum\\binom{n}{k}=2^n$: LHS sums subsets by size; RHS counts binary include/exclude choices per element."""

THEORY_HE = """**אסטרטגיה ל"לפחות אחד":**
ספרו את **המשלים** — במקום "לפחות אחד עם תכונה $P$", חשבו: (סה"כ) $-$ (אף אחד עם $P$). דוגמה: מילים באורך 4 על $\\{a,b,c\\}$ עם לפחות $a$ אחד: סה"כ $3^4=81$, ללא $a$ הוא $2^4=16$, תשובה $81-16=65$.

**מיקום ללא שכנים (ליניארי):**
למקם $k$ אובייקטים מוגבלים ב-$n$ מקומות כך שאין שני מה-$k$ שכנים:
1. סדרו את $n-k$ האחרים: $(n-k)!$ דרכים.
2. נוצרים $n-k+1$ פערים (כולל קצוות).
3. בחרו $k$ פערים: $\\binom{n-k+1}{k}$.
4. סדרו את $k$ האובייקטים: $k!$.
ביחד: $\\binom{n-k+1}{k}\\cdot k!$ לסידור ליניארי.

**סידור מעגלי עם אילוצים:**
סה"כ תמורות מעגליות של $n$ אנשים: $(n-1)!$. ל"A ו-B לא שכנים": סה"כ פחות שכנים (A,B כבלוק → $(n-2)!\\times 2$ סדר פנימי).

**תהליך הכלה–אי-הכלה:**
1. הגדירו קבוצות $A_i$ בבירור (למשל $A$ = מתחלק ב-2, $B$ = מתחלק ב-3).
2. חשבו $|A_i|$ וחיתוכים ($|A \\cap B|$ = מתחלק ב-$\\text{lcm}(2,3)=6$).
3. יישמו הנוסחה; אמתו $|A \\cup B| \\leq |U|$.

**תבנית הוכחה קומבינטורית:**
פרשו צד שמאל וימין כשני אופנים לספור אותה קבוצה. ל-$\\sum\\binom{n}{k}=2^n$: שמאל מסכם תת-קבוצות לפי גודל; ימין סופר בחירות בינאריות להכניס/לא להכניס לכל איבר."""

WE1_EN = """**How many 4-digit numbers (1000–9999) have no repeated digits?**

Digit problems require tracking **position-by-position** choices and the **leading-zero rule**: the thousands digit cannot be 0.

### Move 1 — Thousands digit
Must be 1–9 (no leading zero): **9 choices**.

### Move 2 — Hundreds digit
Any digit except the one already used; 0 is now available: **9 choices**.

### Move 3 — Tens digit
8 digits remain unused: **8 choices**.

### Move 4 — Units digit
7 digits remain: **7 choices**.

**Total:**
$$9 \\times 9 \\times 8 \\times 7 = 4536.$$

**Sanity check:** $9\\times9\\times8\\times7 < 9\\times9\\times9\\times9 = 6561$ (all 4-digit numbers with repetition) ✓. Also $4536 > P(9,4)=3024$ because we allow 0 in later positions after fixing a non-zero thousands digit.

**Bagrut note:** Examiners often add parity or divisibility constraints — split into cases on the restricted digit (usually units) before multiplying the remaining position counts."""

WE1_HE = """**כמה מספרים בני 4 ספרות (1000–9999) ללא ספרה חוזרת?**

בעיות ספרות דורשות מעקב **מיקום-אחר-מיקום** ו**כלל אפס מוביל**: ספרת האלפים לא יכולה להיות 0.

### צעד 1 — ספרת אלפים
חייבת להיות 1–9 (ללא אפס מוביל): **9 אפשרויות**.

### צעד 2 — ספרת מאות
כל ספרה מלבד זו שכבר נבחרה; 0 זמין כעת: **9 אפשרויות**.

### צעד 3 — ספרת עשרות
8 ספרות נותרו: **8 אפשרויות**.

### צעד 4 — ספרת אחדות
7 ספרות נותרו: **7 אפשרויות**.

**סה"כ:**
$$9 \\times 9 \\times 8 \\times 7 = 4536.$$

**בדיקה:** $4536 < 6561$ (כל המספרים עם חזרות) ✓. גם $4536 > P(9,4)=3024$ כי מאפשרים 0 במקומות מאוחרים אחרי אלפים לא-אפס.

**הערת בגרות:** לעיתים מוסיפים אילוץ זוגיות או חלוקה — פצלו למקרים לפי הספרה המוגבלת (בדרך כלל אחדות) לפני הכפלת שאר המקומות."""

WE2_EN = """**In how many ways can 8 people sit at a round table so that persons A and B are NOT adjacent?**

Circular seating uses $(n-1)!$; "NOT adjacent" is best handled by **complement** (total minus adjacent).

### Move 1 — Total circular arrangements
Fix one person to break rotational symmetry: $(8-1)! = 7! = 5040$.

### Move 2 — Count adjacent (A and B together)
Treat A and B as a single block → 7 "units" at a round table: $(7-1)! = 6! = 720$.
Within the block, A and B can swap: $\\times 2$.
Adjacent count: $720 \\times 2 = 1440$.

### Move 3 — Complement
$$5040 - 1440 = 3600.$$

**Why complement wins:** Direct counting of non-adjacent pairs requires inclusion–exclusion over many pairs — complement uses one subtraction. Always verify: $3600 < 5040$ ✓.

**Linear variant:** In a row (not circular), total is $n!$ and adjacent block gives $(n-1)!\\times 2$ — same block logic, different total formula. Label "round table" vs "row" before starting."""

WE2_HE = """**בכמה דרכים יכולים 8 אנשים לשבת בשולחן עגול כך ש-A ו-B לא ישכנו?**

ישיבה מעגלית משתמשת ב-$(n-1)!$; "לא שכנים" מטופלת הכי טוב ב**משלים** (סה"כ פחות שכנים).

### צעד 1 — סה"כ סידורים מעגליים
קבעו אדם אחד לשבירת סימטריה: $(8-1)! = 7! = 5040$.

### צעד 2 — ספירת שכנים (A ו-B יחד)
A ו-B כבלוק אחד → 7 "יחידות": $(7-1)! = 6! = 720$.
בתוך הבלוק, A ו-B יכולים להחליף: $\\times 2$.
ספירת שכנים: $720 \\times 2 = 1440$.

### צעד 3 — משלים
$$5040 - 1440 = 3600.$$

**למה משלים:** ספירה ישירה של לא-שכנים דורשת הכלה–אי-הכלה על זוגות רבים — משלים משתמש בחיסור אחד. אמתו: $3600 < 5040$ ✓.

**גרסה ליניארית:** בשורה (לא מעגלי), סה"כ $n!$ ובלוק שכנים $(n-1)!\\times 2$ — אותה לוגיקת בלוק, נוסחת סה"כ שונה. סמנו "שולחן עגול" מול "שורה" לפני התחלה."""

WE3_EN = """**Prove combinatorially that $\\displaystyle\\binom{n}{0}+\\binom{n}{1}+\\cdots+\\binom{n}{n}=2^n$.**

A combinatorial proof shows both sides count the **same set** in two different ways.

**Left-hand side interpretation:**
$\\binom{n}{k}$ counts $k$-element subsets of a set $S$ with $|S|=n$.
Summing over $k=0,1,\\ldots,n$ counts **all subsets** of $S$ — every size from empty set ($k=0$) to full set ($k=n$).

**Right-hand side interpretation:**
For each of the $n$ elements, independently decide: include (1) or exclude (0).
This gives $2$ choices per element, $n$ independent decisions:
$$\\underbrace{2\\times2\\times\\cdots\\times2}_{n\\text{ times}} = 2^n \\text{ distinct subsets.}$$

**Conclusion:** Both sides count all subsets of an $n$-element set, so they are equal. $\\blacksquare$

**Algebraic proof (bonus):** Set $x=1$ in $(1+x)^n=\\sum_{k=0}^n\\binom{n}{k}x^k$ to get $2^n=\\sum\\binom{n}{k}$.

**Related identity:** Setting $x=-1$ gives $\\sum(-1)^k\\binom{n}{k}=0$ for $n\\ge 1$ — alternating subsets cancel, a second standard Bagrut proof.

**Exam wording:** When the rubric says "combinatorial proof", both interpretations must appear in words — do not stop at "both sides count subsets" without explaining the $2^n$ binary-choice argument."""

WE3_HE = """**הוכיחו קומבינטורית ש-$\\displaystyle\\binom{n}{0}+\\binom{n}{1}+\\cdots+\\binom{n}{n}=2^n$.**

הוכחה קומבינטורית מראה ששני הצדדים סופרים **אותה קבוצה** בשתי דרכים.

**פרשנות צד שמאל:**
$\\binom{n}{k}$ סופר תת-קבוצות בגודל $k$ של קבוצה $S$ עם $|S|=n$.
סכימה על $k=0,1,\\ldots,n$ סופרת **כל תת-הקבוצות** של $S$ — מקבוצה ריקה ($k=0$) עד מלאה ($k=n$).

**פרשנות צד ימין:**
לכל אחד מ-$n$ האיברים, החלטה עצמאית: להכניס (1) או לא (0).
$2$ אפשרויות לכל איבר, $n$ החלטות בלתי-תלויות:
$$\\underbrace{2\\times2\\times\\cdots\\times2}_{n\\text{ פעמים}} = 2^n \\text{ תת-קבוצות שונות.}$$

**מסקנה:** שני הצדדים סופרים את כל תת-הקבוצות, לכן שווים. $\\blacksquare$

**הוכחה אלגברית (בונוס):** הציבו $x=1$ ב-$(1+x)^n=\\sum_{k=0}^n\\binom{n}{k}x^k$.

**זהות קשורה:** $x=-1$ נותן $\\sum(-1)^k\\binom{n}{k}=0$ ל-$n\\ge 1$ — תת-קבוצות עם סימנים מתחלפים מתקזזות, הוכחה סטנדרטית נוספת בבגרות.

**ניסוח בחינה:** כשהרubric דורש "הוכחה קומבינטורית", שתי הפרשנויות חייבות להופיע במילים — אל תעצרו ב"שני הצדדים סופרים תת-קבוצות" בלי להסביר את טיעון $2^n$."""

CHK1_EN = """How many 3-digit numbers (100–999) are **even** and have **no repeated digits**?

**Case 1 — Units digit = 0:**
Hundreds: 9 choices (1–9). Tens: 8 remaining. Units fixed at 0.
Count: $9 \\times 8 = 72$.

**Case 2 — Units digit $\\in \\{2,4,6,8\\}$ (4 choices, not 0):**
Hundreds: 8 choices (exclude 0 and the units digit). Tens: 8 remaining (0 is available if not used).
Count per units choice: $8 \\times 8 = 64$. Total: $4 \\times 64 = 256$.

**Total:** $72 + 256 = 328$.

**Check:** Splitting on units digit avoids double-counting and handles the leading-zero constraint correctly."""

CHK1_HE = """כמה מספרים בני 3 ספרות (100–999) **זוגיים** ו**ללא ספרה חוזרת**?

**מקרה 1 — ספרת אחדות = 0:**
מאות: 9 אפשרויות (1–9). עשרות: 8 שנותרו. אחדות קבועה 0.
ספירה: $9 \\times 8 = 72$.

**מקרה 2 — ספרת אחדות $\\in \\{2,4,6,8\\}$ (4 בחירות, לא 0):**
מאות: 8 (ללא 0 וללא ספרת האחדות). עשרות: 8 שנותרו (0 זמין אם לא בשימוש).
לכל בחירת אחדות: $8 \\times 8 = 64$. סה"כ: $4 \\times 64 = 256$.

**סה"כ:** $72 + 256 = 328$.

**בדיקה:** פיצול לפי ספרת אחדות מונע ספירה כפולה ומטפל נכון באפס מוביל."""

CHK2_EN = """In how many ways can 6 people sit in a **row** so that C and D are NOT adjacent?

**Step 1 — Total linear arrangements:** $6! = 720$.

**Step 2 — C and D adjacent (block method):**
Treat C,D as one block → 5 units to arrange: $5! = 120$.
Internal order within block: $\\times 2$ (CD or DC).
Adjacent count: $120 \\times 2 = 240$.

**Step 3 — Complement:**
$$720 - 240 = 480.$$

**Note:** Linear (not circular) uses $n!$, not $(n-1)!$. The block method is identical to the round-table case but without fixing rotation."""

CHK2_HE = """בכמה דרכים יכולים 6 אנשים לשבת **בשורה** כך ש-C ו-D לא ישכנו?

**שלב 1 — סה"כ סידורים ליניאריים:** $6! = 720$.

**שלב 2 — C ו-D שכנים (שיטת בלוק):**
C,D כבלוק אחד → 5 יחידות: $5! = 120$.
סדר פנימי: $\\times 2$ (CD או DC).
ספירת שכנים: $120 \\times 2 = 240$.

**שלב 3 — משלים:**
$$720 - 240 = 480.$$

**הערה:** ליניארי (לא מעגלי) משתמש ב-$n!$, לא $(n-1)!$. שיטת הבלוק זהה למעגלי אך בלי קביעת סיבוב."""

METHOD_EN = """| Problem type | Method | Key formula |
|---|---|---|
| All arrangements of $n$ distinct objects | Linear or circular | $n!$ or $(n-1)!$ |
| Choose $r$ from $n$ ordered | Permutation | $P(n,r)=n!/(n-r)!$ |
| Choose $r$ from $n$ unordered | Combination | $\\binom{n}{r}$ |
| 'At least one' / 'at most' | Complement | (total) $-$ (none / too many) |
| Two specific NOT adjacent | Complement + block | (total) $-$ (block $\\times 2$) |
| Two specific MUST be adjacent | Block method | $(n-1)!\\times 2$ circular; $5!\\times 2$ linear |
| Non-adjacent placement of $k$ in $n$ | Gap method | $\\binom{n-k+1}{k}\\cdot k!$ |
| Letters with repetition | Multinomial | $n!/n_1!\\cdots n_k!$ |
| Divisible by $a$ or $b$ | Inclusion–exclusion | $|A|+|B|-|A\\cap B|$ |
| Prove $\\sum\\binom{n}{k}=2^n$ | Double counting | Subsets by size vs binary choices |

**Workflow:** (1) Linear or circular? (2) Ordered or unordered? (3) Restriction → complement, block, or case split. (4) Write the formula before plugging numbers."""

METHOD_HE = """| סוג בעיה | שיטה | נוסחה |
|---|---|---|
| $n$ אובייקטים שונים | ליניארי / מעגלי | $n!$ / $(n-1)!$ |
| $r$ מ-$n$ מסודר | תמורה | $P(n,r)=n!/(n-r)!$ |
| $r$ מ-$n$ לא מסודר | צירוף | $\\binom{n}{r}$ |
| 'לפחות אחד' / 'לכל היותר' | משלים | (סה"כ) $-$ (אף אחד) |
| שניים ספציפיים לא שכנים | משלים + בלוק | (סה"כ) $-$ (בלוק $\\times 2$) |
| שניים חייבים להיות שכנים | בלוק | $(n-1)!\\times 2$ מעגלי |
| $k$ ללא שכן ב-$n$ | פערים | $\\binom{n-k+1}{k}\\cdot k!$ |
| אותיות עם חזרות | מולטינומיאל | $n!/n_1!\\cdots n_k!$ |
| מתחלק ב-$a$ או $b$ | הכלה–אי-הכלה | $|A|+|B|-|A\\cap B|$ |
| הוכחת $\\sum\\binom{n}{k}=2^n$ | ספירה כפולה | גודל מול בינארי |

**תהליך:** (1) ליניארי או מעגלי? (2) מסודר או לא? (3) אילוץ → משלים, בלוק או פיצול. (4) כתבו נוסחה לפני מספרים."""

PITFALL_EN = """1. **Leading-zero restriction:** In $k$-digit numbers, the first digit cannot be 0. Thousands digit has only 9 choices (1–9), not 10.

2. **Block internal order:** When treating A and B as one unit, multiply by $2$ for AB vs BA. Forgetting this gives half the correct adjacent count.

3. **Circular vs linear:** Round table → $(n-1)!$, not $n!$. Row seating → $n!$. Mixing these is the most common 5-unit combinatorics error.

4. **Inclusion–exclusion sign:** $|A \\cup B|=|A|+|B|-|A \\cap B|$ — **subtract** the intersection. Adding it double-counts elements in both sets.

5. **"At least one" trap:** Do not enumerate all cases manually when complement is shorter. Total minus "none" is almost always faster.

6. **Multiset division:** Arranging AABBB is $5!/(2!\\cdot 3!)=10$, not $5!=120$. Divide by factorials of identical letter counts.

**Example misconception:** Using $P(10,4)=5040$ for an unordered committee.

**Fix:** Committee → $\\binom{10}{4}$. Use $P(n,r)$ only when order or distinct roles matter."""

PITFALL_HE = """1. **אפס מוביל:** במספרים בני $k$ ספרות, הספרה הראשונה לא יכולה להיות 0. ספרת אלפים — 9 אפשרויות (1–9), לא 10.

2. **סדר פנימי בבלוק:** כש-A ו-B יחידה אחת, הכפילו ב-$2$ ל-AB מול BA. שכחה נותנת חצי מהספירה הנכונה.

3. **מעגלי מול ליניארי:** שולחן עגול → $(n-1)!$, לא $n!$. שורה → $n!$. ערבוב — הטעות הנפוצה ביותר ב-5 יחידות.

4. **סימן בהכלה–אי-הכלה:** $|A \\cup B|=|A|+|B|-|A \\cap B|$ — **מחסרים** חיתוך. חיבור מוסיף ספירה כפולה.

5. **מלכודת "לפחות אחד":** אל תפרטו כל המקרים ידנית כשמשלים קצר יותר. סה"כ פחות "אף אחד" — כמעט תמיד מהיר.

6. **חלוקת מולטיסט:** סידור AABBB הוא $5!/(2!\\cdot 3!)=10$, לא $5!=120$. חלקו בעצרות של אותיות זהות.

**דוגמת טעות:** $P(10,4)$ לועדה לא מסודרת.

**תיקון:** ועדה → $\\binom{10}{4}$. $P(n,r)$ רק כשסדר או תפקידים נבדלים."""

WHY_EN = """Advanced combinatorics is the bridge between **counting** and **probability at 5 units** — every "favorable outcomes over total" fraction depends on accurate restricted counting. Inclusion–exclusion appears in survey problems that feed directly into conditional probability.

**Recommended next topics:**
- `concept:probability_5pt` — compound events, conditional probability, Bayes at the 5-unit level.

**Builds on:** basic permutations, combinations, factorials, and the binomial theorem from earlier units.

**Why it matters for exams:** Bagrut 5-unit papers combine digit-counting (6–8 pts), circular seating with restrictions (8 pts), inclusion–exclusion (8 pts), and combinatorial identity proofs (4–6 pts). Transfer — recognizing "complement vs direct" or "block method" — separates full credit from partial. When studying, always label your strategy before calculating."""

WHY_HE = """קומבינטוריקה מתקדמת היא הגשר בין **ספירה** ל**הסתברות ב-5 יחידות** — כל שבר "תוצאות רצויות על סך הכל" תלוי בספירה מדויקת עם אילוצים. הכלה–אי-הכלה מופיעה בסקרים שמזינים ישירות הסתברות מותנית.

**נושאים מומלצים להמשך:**
- `concept:probability_5pt` — מאורעות מורכבים, הסתברות מותנית, בייס ברמת 5 יחידות.

**מבוסס על:** תמורות, צירופים, עצרות ומשפט הבינום מיחידות קודמות.

**למה זה חשוב לבחינות:** בגרות 5 יחידות משלבת ספירת ספרות (6–8 נק'), ישיבה מעגלית עם אילוצים (8 נק'), הכלה–אי-הכלה (8 נק') והוכחות זהות (4–6 נק'). העברה — זיהוי "משלים מול ישיר" או "שיטת בלוק" — מפרידה בין ניקוד מלא לחלקי. בלימוד, תייגו אסטרטגיה לפני חישוב."""

BEFORE_EN = """**Key formulas (recite before the exam):**
- $P(n,r)=n!/(n-r)!$; $\\binom{n}{r}=n!/[r!(n-r)!]$
- Circular: $(n-1)!$; multiset: $n!/n_1!\\cdots n_k!$
- Inclusion–exclusion: $|A \\cup B|=|A|+|B|-|A \\cap B|$
- Block (adjacent pair): $(n-1)!\\times 2$ circular; $(n-2)!\\times 2$ linear for $n$ people
- Pascal: $\\binom{n}{k}+\\binom{n}{k+1}=\\binom{n+1}{k+1}$
- Row sum: $\\sum\\binom{n}{k}=2^n$; alternating: $\\sum(-1)^k\\binom{n}{k}=0$ for $n\\ge 1$

**Exam patterns (5-unit):**
1. Digit counting with no repetition + parity/divisibility (6–8 pts).
2. Circular/linear seating — adjacent or NOT adjacent (8 pts).
3. Inclusion–exclusion with 2–3 sets (8 pts).
4. Committee with required/forbidden members (6 pts).
5. Combinatorial identity proof — write full bijection argument (4–6 pts).

**Last review:** One digit problem + one circular NOT-adjacent + one inclusion–exclusion — 8 minutes, no notes."""

BEFORE_HE = """**נוסחאות מפתח (חזרו לפני הבחינה):**
- $P(n,r)=n!/(n-r)!$; $\\binom{n}{r}=n!/[r!(n-r)!]$
- מעגלי: $(n-1)!$; מולטיסט: $n!/n_1!\\cdots n_k!$
- הכלה–אי-הכלה: $|A \\cup B|=|A|+|B|-|A \\cap B|$
- בלוק (זוג שכנים): $(n-1)!\\times 2$ מעגלי
- פסקל: $\\binom{n}{k}+\\binom{n}{k+1}=\\binom{n+1}{k+1}$
- סכום שורה: $\\sum\\binom{n}{k}=2^n$

**סוגי שאלות (5 יח'):**
1. ספירת ספרות ללא חזרות + זוגיות/חלוקה (6–8 נק').
2. ישיבה מעגלית/ליניארית — שכנים או לא (8 נק').
3. הכלה–אי-הכלה עם 2–3 קבוצות (8 נק').
4. ועדה עם חברים נדרשים/אסורים (6 נק').
5. הוכחת זהות קומבינטורית — הצדקה מלאה (4–6 נק').

**חזרה אחרונה:** בעיית ספרות + מעגלי לא-שכנים + הכלה–אי-הכלה — 8 דקות, בלי notes."""

SUMMARY_EN = """- **Permutations:** $n!$ linear, $(n-1)!$ circular; $P(n,r)$ for partial ordered selection; multinomial $n!/n_1!\\cdots n_k!$ for identical elements.
- **Combinations:** $\\binom{n}{r}$; symmetry $\\binom{n}{r}=\\binom{n}{n-r}$; Pascal's identity.
- **Inclusion–exclusion:** $|A \\cup B|=|A|+|B|-|A \\cap B|$; extend to three sets with alternating signs.
- **Non-adjacent:** complement method — (total) $-$ (adjacent as block $\\times 2$).
- **Binomial identity:** $\\sum_{k=0}^n\\binom{n}{k}=2^n$ — count all subsets combinatorially or via $x=1$ in binomial theorem.

**Takeaway:** State your strategy (complement, block, case split) before arithmetic. Examiners at 5 units grade the setup, not just the final number."""

SUMMARY_HE = """- **תמורות:** $n!$ ליניארי, $(n-1)!$ מעגלי; $P(n,r)$ לבחירה מסודרת חלקית; מולטינומיאל $n!/n_1!\\cdots n_k!$.
- **צירופים:** $\\binom{n}{r}$; סימטריה $\\binom{n}{r}=\\binom{n}{n-r}$; זהות פסקל.
- **הכלה–אי-הכלה:** $|A \\cup B|=|A|+|B|-|A \\cap B|$; הרחבה לשלוש קבוצות.
- **ללא שכן:** משלים — (סה"כ) $-$ (שכנים כבלוק $\\times 2$).
- **זהות בינום:** $\\sum\\binom{n}{k}=2^n$ — ספירת תת-קבוצות או $x=1$ בבינום.

**מסקנה:** הצהירו אסטרטגיה (משלים, בלוק, פיצול) לפני חשבון. ב-5 יחידות מעריכים את ההגדרה, לא רק המספר."""

EXPLS = {
    1: fmt_expl(
        "Thousands digit: 9 choices (1–9). Hundreds: 9 (0 available). Tens: 8. Units: 7. Product $9\\times9\\times8\\times7=4536$. Option 3024 is $P(9,4)$ without the leading-zero rule.",
        "Work position by position. Thousands cannot be 0; later positions may include 0. Multiply descending counts after the first digit.",
        "Using $10\\times9\\times8\\times7=5040$ (0 in thousands) or $9\\times8\\times7\\times6=3024$ as $P(9,4)$ without allowing 0 in positions 2–4.",
        "On digit MCQs, compute the thousands digit separately — write '9 choices, no 0' before continuing.",
        "אלפים: 9 (1–9). מאות: 9 (0 זמין). עשרות: 8. אחדות: 7. $9\\times9\\times8\\times7=4536$. 3024 הוא $P(9,4)$ בלי אפס מוביל.",
        "עבדו מיקום-אחר-מיקום. אלפים לא 0; אחר כך 0 מותר במקומות 2–4. הכפילו ספירות יורדות — אל $\\binom{10}{4}$.",
        "$10\\times9\\times8\\times7=5040$ (0 באלפים) או $9\\times8\\times7\\times6=3024$ — שתיהן מפספסות את מבנה אפס מוביל.",
        "ב-MCQ ספרות, חשבו אלפים בנפרד על טיוטה — '9, ללא 0' לפני המשך. שורה אחת מונעת 5040 ו-3024.",
    ),
    2: fmt_expl(
        "Circular seating of 8: total $(8-1)!=7!=5040$. A and B adjacent — block method: 7 units at round table $\\to (7-1)!=6!=720$, times 2 for AB/BA $=1440$. Complement: $5040-1440=3600$.",
        "Label 'circular' and 'NOT adjacent' first. Circular $\\to (n-1)!$. NOT adjacent $\\to complement (total minus adjacent). Adjacent count uses block: treat pair as one unit, multiply internal order by 2. Never use $8!$ for a round table.",
        "Using $8!=40320$ (linear, not circular). Or counting non-adjacent directly without block/complement — leads to overcounting. Another slip: block count $6!$ without $\\times 2$ gives 720, then $5040-720=4320$.",
        "For round-table NOT-adjacent problems, write three lines on scrap: (1) total $(n-1)!$, (2) adjacent $(n-2)!\\times 2$, (3) subtract. This template works for every such Bagrut item.",
        "ישיבה מעגלית של 8: סה\"כ $(8-1)!=7!=5040$. A ו-B שכנים — בלוק: 7 יחידות $\\to 6!=720$, $\\times 2$ ל-AB/BA $=1440$. משלים: $5040-1440=3600$.",
        "סמנו 'מעגלי' ו'לא שכנים'. מעגלי $\\to (n-1)!$. לא שכנים $\\to משלים. שכנים — בלוק, $\\times 2$. אל $8!$ לשולחן עגול.",
        "$8!=40320$ (ליניארי). או ספירה ישירה של לא-שכנים — ספירה כפולה. טעות: בלוק $6!$ בלי $\\times 2$ → $5040-720=4320$.",
        "בבעיות מעגלי לא-שכנים, כתבו: (1) סה\"כ $(n-1)!$, (2) שכנים $(n-2)!\\times 2$, (3) חיסור. תבנית לכל שאלת בגרות כזו.",
    ),
    3: fmt_expl(
        "LHS sums $\\binom{n}{k}$ over all subset sizes — all subsets of an $n$-element set. RHS: each element independently in or out gives $2^n$ binary choices. Same set, two counts.",
        "Structure: (1) define the set, (2) count by size (LHS), (3) count by binary choices (RHS), (4) conclude equality.",
        "Algebraic proof via $x=1$ when combinatorial proof is requested — partial credit only. Or omit the binary-choice argument.",
        "Write both interpretations even if short on time — method marks are most of proof questions.",
        "שמאל מסכם $\\binom{n}{k}$ לפי גודל — כל תת-קבוצות של $n$ איברים. ימין: לכל איבר החלטה בפנים/בחוץ → $2^n$ אפשרויות. אותה קבוצה, שתי ספירות.",
        "מבנה: (1) הגדרת קבוצה $S$, (2) ספירה לפי גודל (שמאל), (3) בחירות בינאריות לכל איבר (ימין), (4) מסקנה על שוויון.",
        "הוכחה אלגברית ב-$x=1$ כשמבקשים קומבינטורית — נקודות חלקיות בלבד. גם תיאור ללא $2^n$.",
        "כתבו שתי פרשנויות במילים — נקודות שיטה רוב שאלות ההוכחה ב-5 יחידות.",
    ),
    4: fmt_expl(
        "6 people at a round table: fix one person to break rotational symmetry. Remaining 5 can be arranged in $5!=120$ ways. Option 720 is $6!$ — that counts linear arrangements or treats every rotation as distinct.",
        "Circular permutation formula: $(n-1)!$. Ask: 'If everyone shifts one seat clockwise, is that a new arrangement?' At a round table, no — so divide by $n$. Fixing one person is equivalent to dividing $n!$ by $n$.",
        "Answering 720 ($6!$) by applying linear permutation formula. Or 360 ($6!/2$) by incorrect symmetry argument. Or 24 ($4!$) from arithmetic error.",
        "Circle the word 'round' or 'circular' in the stem — it triggers $(n-1)!$ immediately. Write $6-1=5$, then $5!=120$ before looking at answer choices.",
        "6 אנשים בשולחן עגול: קבעו אחד לשבירת סימטריה. 5 הנותרים — $5!=120$. 720 הוא $6!$ — סידורים ליניאריים או כל סיבוב נפרד.",
        "תמורה מעגלית: $(n-1)!$. שאלו: 'הזזה במקום אחד — סידור חדש?' בשולחן עגול, לא — לכן $(n-1)!$.",
        "720 ($6!$) — נוסחת ליניארי. או 360 ($6!/2$) — טיעון סימטריה שגוי. או 24 ($4!$) — טעות חשבונית.",
        "הקיפו 'עגול' — מפעיל $(n-1)!$. כתבו $6-1=5$, $5!=120$ לפני התשובות.",
    ),
    5: fmt_expl(
        "True. $\\binom{10}{3}=\\frac{10\\times9\\times8}{3\\times2\\times1}=120$ and $\\binom{10}{7}=\\frac{10\\times9\\times8\\times7\\times6\\times5\\times4}{7\\times6\\times5\\times4\\times3\\times2\\times1}=120$. By symmetry $\\binom{n}{r}=\\binom{n}{n-r}$: choosing 3 to include equals choosing 7 to exclude.",
        "Symmetry identity: every $r$-element subset pairs with its $(n-r)$-element complement. For $n=10$, $r=3$ and $n-r=7$ — same count. Verify by computing both or citing symmetry directly.",
        "Computing only one side and guessing, or believing the statement is false because 3 and 7 look different. Some students compute $\\binom{10}{7}$ incorrectly as 720 by using $P(10,7)$.",
        "Symmetry $\\binom{n}{r}=\\binom{n}{n-r}$ saves work on Bagrut: if one coefficient is hard, compute the smaller $r$. For committees, 'choose 3 from 10' and 'choose 7 from 10' are identical questions.",
        "נכון. $\\binom{10}{3}=120$ ו-$\\binom{10}{7}=120$. לפי סימטריה $\\binom{n}{r}=\\binom{n}{n-r}$: בחירת 3 לכלול = בחירת 7 להוציא.",
        "זהות סימטריה: כל תת-קבוצה בגודל $r$ מתאימה למשלימה בגודל $n-r$. ל-$n=10$, $r=3$ ו-$7$ — אותה ספירה.",
        "חישוב צד אחד וניחוש, או אמונה שהטענה שגויה כי 3 ו-7 נראים שונים. חישוב $\\binom{10}{7}$ כ-720 ב-$P(10,7)$.",
        "סימטריה $\\binom{n}{r}=\\binom{n}{n-r}$ חוסכת עבודה: אם $r$ גדול, חשבו $n-r$. 'בחר 3 מ-10' = 'בחר 7 מ-10'.",
    ),
    6: fmt_expl(
        "Five distinct people in a row — every ordering is different. All 5 are used, order matters: $5!=5\\times4\\times3\\times2\\times1=120$. This is a full linear permutation with no restrictions.",
        "Full line of $n$ distinct people $\\to n!$. No one is left out; each position is a distinct slot. This is $P(5,5)=5!$, not $\\binom{5}{5}=1$ which would ignore order entirely.",
        "Answering 1 by treating it as one unordered group, or 5 by counting people instead of arrangements. Using $P(5,1)=5$ picks only one person for one spot.",
        "Full-line problems are the fastest points — recognize $n!$ immediately when all $n$ distinct objects are arranged in a sequence with no restrictions. No formula sheet lookup needed.",
        "חמישה אנשים שונים בשורה — כל סידור שונה. כולם בשימוש, סדר חשוב: $5!=5\\times4\\times3\\times2\\times1=120$. תמורה ליניארית מלאה ללא אילוצים — כל מקום תפקיד נפרד.",
        "שורה של $n$ אנשים שונים $\\to n!$. זה $P(5,5)=5!$, לא $\\binom{5}{5}=1$ שמתעלם מסדר לגמרי.",
        "תשובה 1 כקבוצה לא מסודרת, או 5 כספירת אנשים במקום סידורים. $P(5,1)=5$ — רק מקום אחד.",
        "בעיות שורה מלאה — נקודות מהירות; זיהו $n!$ מיד כשכל $n$ מסודרים ברצף ללא אילוצים.",
    ),
    7: fmt_expl(
        "Choosing 3 from 10 without regard to order: $\\binom{10}{3}=\\frac{10\\times9\\times8}{3\\times2\\times1}=120$. Committee members have no distinct roles — swapping two members does not create a new committee.",
        "Keyword 'committee' with no president/secretary $\\to$ combination. Cancel before multiplying: $10\\times9\\times8/6=120$. Symmetry check: $\\binom{10}{7}=120$ too.",
        "Using $P(10,3)=720$ because 'choose 3' sounds like arranging. Or $10\\times9\\times8=720$ without dividing by $3!$. Both count ordered selections.",
        "Write $\\binom{n}{r}$ before computing whenever the stem says committee, team, or group without roles. One letter 'C' on scrap paper prevents the permutation trap.",
        "בחירת 3 מ-10 ללא סדר: $\\binom{10}{3}=\\frac{10\\times9\\times8}{3\\times2\\times1}=120$. אין תפקידים — החלפת שני חברים לא יוצרת ועדה חדשה.",
        "מילת מפתח 'ועדה' ללא יו\"ר/מזכיר $\\to$ צירוף. צמצום: $10\\times9\\times8/6=120$. בדיקת סימטריה: $\\binom{10}{7}=120$ גם כן.",
        "$P(10,3)=720$ כי 'בחר 3' נשמע כמו סידור. או $10\\times9\\times8$ בלי חלוקה ב-$3!$ — שניהם ספירה מסודרת.",
        "כתבו $\\binom{n}{r}$ כש'ועדה' או 'קבוצה' ללא תפקידים. 'C' על טיוטה מונע מלכודת תמורה — שווה נקודות שיטה בבגרות 5 יחידות.",
    ),
    8: fmt_expl(
        "Arranging letters AABBB (5 letters: 2 A's identical, 3 B's identical): $\\frac{5!}{2!\\cdot3!}=\\frac{120}{12}=10$. Divide by factorials of identical letter counts to avoid overcounting swaps of indistinguishable letters.",
        "Multiset formula: total permutations $n!$ divided by $n_1!\\cdots n_k!$ for each group of identical items. Here $n=5$, $n_A=2$, $n_B=3$. If all letters were distinct, answer would be $5!=120$.",
        "Answering 120 ($5!$) by ignoring identical letters, or 20 ($5!/3!$) by dividing only for the three B's but not the two A's. Or $\\binom{5}{2}=10$ by choosing positions for A's — that works too but must be justified.",
        "For multiset arrangements, list letter counts first: '2A, 3B $\\to 5!/(2!\\cdot3!)$.' This template covers all anagram problems on the 5-unit exam.",
        "סידור AABBB (5 אותיות: 2 A זהות, 3 B זהות): $\\frac{5!}{2!\\cdot3!}=\\frac{120}{12}=10$. חלקו בעצרות של אותיות זהות.",
        "נוסחת מולטיסט: $n!$ חלקי $n_1!\\cdots n_k!$. כאן $n=5$, $n_A=2$, $n_B=3$. אם כולן שונות — $5!=120$.",
        "120 ($5!$) — התעלמות מזהות. או 20 ($5!/3!$) — חלוקה רק ל-B. $\\binom{5}{2}=10$ — בחירת מקומות ל-A — גם תקף.",
        "בסידורי מולטיסט, רשמו: '2A, 3B $\\to 5!/(2!\\cdot3!)$.' תבנית לכל בעיות אנגרמה ב-5 יחידות.",
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
            if "even" in body.lower() or "זוגיים" in sec.get("body_he_md", ""):
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
