#!/usr/bin/env python3
"""Expand combinatorics.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/combinatorics.json"

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


INTRO_EN = """How many ways can 3 students be chosen from a class of 30? How many distinct 4-digit PIN codes are possible if digits may repeat? Listing every option is impractical — we need **systematic counting formulas**.

**Combinatorics** answers "how many?" without enumerating every case. It underpins probability (counting favorable outcomes), algebra (binomial expansion), and computer science (password strength, network routing). On the Israeli Bagrut 4–5 unit track you will use:

- **Permutations** — ordered arrangements where position matters (lines, rankings, codes without repetition).
- **Combinations** — unordered selections where only membership matters (committees, hands of cards, subsets).
- **Pascal's triangle and the binomial theorem** — connect counting to polynomial expansion and row-sum identities.

The single most important exam skill is the **decision question**: does order matter? A committee of three is a combination; assigning president, secretary, and treasurer from the same three people is a permutation. Master that distinction first, then the formulas become straightforward applications of the multiplication principle and factorial cancellation."""

INTRO_HE = """כמה דרכים לבחור 3 תלמידים מכיתה של 30? כמה קודי PIN בני 4 ספרות שונים אפשריים אם ספרות יכולות לחזור? רשימת כל האפשרויות אינה מעשית — נדרשות **נוסחאות ספירה שיטתיות**.

**קומבינטוריקה** עונה על "כמה?" בלי לפרט כל מקרה. היא תומכת בהסתברות (ספירת תוצאות רצויות), באלגברה (פתיחת בינום) ובמדעי המחשב (חוזק סיסמאות, ניתוב). במסלול בגרות 4–5 יחידות תשתמשו ב:

- **תמורות** — סידורים מסודרים שבהם המיקום חשוב (שורות, דירוגים, קודים ללא חזרות).
- **צירופים** — בחירות לא מסודרות שבהן רק החברות בקבוצה חשובה (ועדות, ידות קלפים, תת-קבוצות).
- **משולש פסקל ומשפט הבינום** — מקשרים ספירה לפתיחת פולינומים ולזהויות סכום-שורה.

המיומנות החשובה ביותר לבחינה היא **שאלת ההחלטה**: האם סדר חשוב? ועדה של שלושה — צירוף; מינוי יו"ר, מזכיר וגזבר מאותם שלושה — תמורה. שלטו בהבחנה זו קודם, ואז הנוסחאות הופכות ליישום ישיר של עקרון הכפל וביטול עצרות."""

DEF_EN = """**Fundamental Counting Principle (multiplication):** If task 1 can be done in $m$ ways and task 2 independently in $n$ ways, the combined process has $m\\times n$ ways. Extend to $k$ stages: multiply the choices at each stage.

**Factorial:** $n! = n(n-1)(n-2)\\cdots 2\\cdot 1$. By convention $0!=1$ (one way to arrange nothing). Factorials count **permutations of all $n$ distinct objects**: $n!=P(n,n)$.

**Permutation (ordered, no repetition):** Arrange $r$ items chosen from $n$ distinct objects where order matters:
$$P(n,r)=\\frac{n!}{(n-r)!}=n(n-1)\\cdots(n-r+1).$$

**Combination (unordered, no repetition):** Choose $r$ items from $n$ where order does not matter:
$$\\binom{n}{r}=C(n,r)=\\frac{n!}{r!(n-r)!}.$$

**Key properties of binomial coefficients:**
- $\\binom{n}{0}=\\binom{n}{n}=1$ (empty set or full set).
- $\\binom{n}{r}=\\binom{n}{n-r}$ (symmetry — choosing $r$ to keep equals choosing $n-r$ to leave out).
- $\\binom{n}{r}+\\binom{n}{r+1}=\\binom{n+1}{r+1}$ (Pascal's identity — builds the triangle).
- Row sum: $\\sum_{k=0}^n\\binom{n}{k}=2^n$ (every subset of an $n$-element set).

**Relationship:** $P(n,r)=r!\\cdot\\binom{n}{r}$ — permuting the $r$ chosen items gives all ordered arrangements."""

DEF_HE = """**עקרון הספירה (כפל):** אם משימה 1 ניתנת ב-$m$ דרכים ומשימה 2 ב-$n$ דרכים (בלתי תלויות), יש $m\\times n$ דרכים לשתיהן. מרחיבים ל-$k$ שלבים: מכפילים את מספר האפשרויות בכל שלב.

**עצרת:** $n!=n(n-1)\\cdots 2\\cdot 1$. לפי מוסכמה $0!=1$ (דרך אחת לסדר כלום). עצרת סופרת **תמורות של כל $n$ אובייקטים שונים**: $n!=P(n,n)$.

**תמורה (מסודר, ללא חזרות):** סידור $r$ פריטים מתוך $n$ שונים כשסדר חשוב:
$$P(n,r)=\\frac{n!}{(n-r)!}=n(n-1)\\cdots(n-r+1).$$

**צירוף (לא מסודר, ללא חזרות):** בחירת $r$ פריטים מתוך $n$ כשסדר לא חשוב:
$$\\binom{n}{r}=C(n,r)=\\frac{n!}{r!(n-r)!}.$$

**תכונות מקדמי הבינום:**
- $\\binom{n}{0}=\\binom{n}{n}=1$ (קבוצה ריקה או מלאה).
- $\\binom{n}{r}=\\binom{n}{n-r}$ (סימטריה — בחירת $r$ לשמירה שווה לבחירת $n-r$ להוצאה).
- $\\binom{n}{r}+\\binom{n}{r+1}=\\binom{n+1}{r+1}$ (זהות פסקל — בונה את המשולש).
- סכום שורה: $\\sum_{k=0}^n\\binom{n}{k}=2^n$ (כל תת-קבוצה של קבוצה בגודל $n$).

**קשר:** $P(n,r)=r!\\cdot\\binom{n}{r}$ — תמורות של $r$ הנבחרים נותנות את כל הסידורים המסודרים."""

THEORY_EN = """**Pascal's triangle:** Row $n$ (starting from row $0$) lists $\\binom{n}{0},\\binom{n}{1},\\ldots,\\binom{n}{n}$.

```
Row 0:      1
Row 1:     1 1
Row 2:    1 2 1
Row 3:   1 3 3 1
Row 4:  1 4 6 4 1
```

Each interior entry equals the sum of the two entries directly above it — this is Pascal's identity in table form. Symmetry is visible: row $n$ reads the same left-to-right and right-to-left.

**Binomial theorem:** For any real $a,b$ and non-negative integer $n$,
$$(a+b)^n=\\sum_{k=0}^n\\binom{n}{k}a^{n-k}b^k.$$
Term $k$ (counting from $k=0$) has binomial coefficient $\\binom{n}{k}$, power $n-k$ on $a$, and power $k$ on $b$. To find a specific power of $x$ in $(c+dx)^n$, set $k$ so the $x$-exponent matches.

**Row-sum identities (Bagrut favorites):**
- **All positive:** $\\sum_{k=0}^n\\binom{n}{k}=2^n$ — substitute $a=b=1$ in the binomial theorem (count all subsets).
- **Alternating:** $\\sum_{k=0}^n(-1)^k\\binom{n}{k}=0$ for $n\\ge1$ — substitute $a=1$, $b=-1$.
- **Even vs odd:** $\\sum_{k\\text{ even}}\\binom{n}{k}=\\sum_{k\\text{ odd}}\\binom{n}{k}=2^{n-1}$ for $n\\ge1$.

**Counting with repetition:** If order matters and each of $r$ positions can be any of $n$ symbols (repetition allowed), there are $n^r$ codes. If order does not matter with repetition, use **stars and bars** (5-unit extension) — not on the 4-unit core, but good to know exists.

**Strategy for restricted counting:** Split into disjoint cases ("exactly $k$ women") or use the **complement** (total minus unwanted). Both paths should agree — use the shorter one on exams."""

THEORY_HE = """**משולש פסקל:** שורה $n$ (מ-$0$) מציגה $\\binom{n}{0},\\binom{n}{1},\\ldots,\\binom{n}{n}$.

```
שורה 0:      1
שורה 1:     1 1
שורה 2:    1 2 1
שורה 3:   1 3 3 1
שורה 4:  1 4 6 4 1
```

כל ערך פנימי שווה לסכום שני הערכים מעליו — זו זהות פסקל בטבלה. סימטריה נראית: שורה $n$ זהה משמאל לימין ומימין לשמאל.

**משפט הבינום:** לכל $a,b$ ממשיים ו-$n$ שלם לא-שלילי,
$$(a+b)^n=\\sum_{k=0}^n\\binom{n}{k}a^{n-k}b^k.$$
איבר $k$ (מ-$0$) נושא מקדם $\\binom{n}{k}$, חזקה $n-k$ על $a$ וחזקה $k$ על $b$. למציאת חזקה מסוימת של $x$ ב-$(c+dx)^n$, בוחרים $k$ כך שמעריך $x$ מתאים.

**זהויות סכום-שורה (מועדפות בבגרות):**
- **כולם חיוביים:** $\\sum_{k=0}^n\\binom{n}{k}=2^n$ — הצבה $a=b=1$ (ספירת כל תת-הקבוצות).
- **סימנים מתחלפים:** $\\sum_{k=0}^n(-1)^k\\binom{n}{k}=0$ ל-$n\\ge1$ — הצבה $a=1$, $b=-1$.
- **זוגי מול אי-זוגי:** $\\sum_{k\\text{ זוגי}}\\binom{n}{k}=\\sum_{k\\text{ אי-זוגי}}\\binom{n}{k}=2^{n-1}$ ל-$n\\ge1$.

**ספירה עם חזרות:** אם סדר חשוב וכל אחת מ-$r$ המקומות יכולה להיות כל אחד מ-$n$ סמלים, יש $n^r$ קודים. אם סדר לא חשוב עם חזרות — **כוכבים ופסים** (הרחבה ל-5 יחידות).

**אסטרטגיה לספירה עם אילוצים:** פיצול למקרים זרים ("בדיוק $k$ נשים") או **משלים** (סך הכל פחות לא רצוי). שני המסלולים צריכים להסכים — בבחינה בחרו את הקצר."""

WE1_EN = """**Problem:** A committee of 3 must be chosen from 8 people.
(a) How many ways if order doesn't matter?
(b) How many ways if the first chosen is president, second is secretary, third is treasurer?

This single setup illustrates the permutation–combination fork: same people, different counting rules.

### Move 1 — Read the wording carefully
"Committee" with no roles → **combination**. Named sequential roles → **permutation** (each assignment is a distinct outcome).

### Move 2 — Part (a): combination
$$\\binom{8}{3}=\\frac{8!}{3!\\cdot5!}=\\frac{8\\times7\\times6}{3\\times2\\times1}=56.$$
Cancel before multiplying fully: $8\\times7\\times6/6=56$.

### Move 3 — Part (b): permutation
$$P(8,3)=\\frac{8!}{5!}=8\\times7\\times6=336.$$
Three distinct slots → multiply three descending factors.

### Move 4 — Verify the relationship
$P(8,3)=3!\\cdot\\binom{8}{3}=6\\times56=336$ ✓. Every unordered trio generates $3!=6$ orderings.

**Bagrut link:** Mixed items often ask (a) then (b) on the same stem — write "C" or "P" before calculating to avoid automatic $P(n,r)$ on committee problems."""

WE1_HE = """**בעיה:** יש לבחור ועדה של 3 מתוך 8 אנשים.
(א) כמה דרכים אם סדר לא חשוב?
(ב) כמה דרכים אם הראשון שנבחר הוא יו"ר, השני מזכיר והשלישי גזבר?

אותה תרחיש מדגים את מזלג תמורה–צירוף: אותם אנשים, כללי ספירה שונים.

### צעד 1 — קריאה מדויקת של הניסוח
"ועדה" ללא תפקידים → **צירוף**. תפקידים רציפים → **תמורה** (כל שיבוץ הוא תוצאה שונה).

### צעד 2 — סעיף (א): צירוף
$$\\binom{8}{3}=\\frac{8!}{3!\\cdot5!}=\\frac{8\\times7\\times6}{3\\times2\\times1}=56.$$
מצמצמים לפני כפל מלא: $8\\times7\\times6/6=56$.

### צעד 3 — סעיף (ב): תמורה
$$P(8,3)=\\frac{8!}{5!}=8\\times7\\times6=336.$$
שלושה תפקידים שונים → מכפילים שלושה גורמים יורדים.

### צעד 4 — אימות הקשר
$P(8,3)=3!\\cdot\\binom{8}{3}=6\\times56=336$ ✓. כל שלישייה לא מסודרת יוצרת $3!=6$ סידורים.

**קשר לבגרות:** פריטים משולבים שואלים (א) ואז (ב) על אותו גזע — כתבו "C" או "P" לפני החישוב כדי לא להשתמש אוטומטית ב-$P(n,r)$ בבעיות ועדה."""

WE2_EN = """**Expand** $(2x-3)^4$ using the binomial theorem.

Binomial expansion is bookkeeping: identify $a=2x$, $b=-3$, $n=4$, then sum terms for $k=0,1,2,3,4$.

### Move 1 — Set up the general term
$$(2x-3)^4=\\sum_{k=0}^{4}\\binom{4}{k}(2x)^{4-k}(-3)^k.$$

### Move 2 — Build a table (reduces sign errors)

| $k$ | $\\binom{4}{k}$ | $(2x)^{4-k}$ | $(-3)^k$ | Term |
|---|---|---|---|---|
| $0$ | $1$ | $16x^4$ | $1$ | $16x^4$ |
| $1$ | $4$ | $8x^3$ | $-3$ | $-96x^3$ |
| $2$ | $6$ | $4x^2$ | $9$ | $216x^2$ |
| $3$ | $4$ | $2x$ | $-27$ | $-216x$ |
| $4$ | $1$ | $1$ | $81$ | $81$ |

### Move 3 — Combine
**Result:** $16x^4-96x^3+216x^2-216x+81$.

### Move 4 — Spot-check
Signs alternate when $b<0$ and $n$ is even → first and last terms positive ✓. Row 4 of Pascal: $1,4,6,4,1$ matches coefficients before powers.

**Exam note:** For "coefficient of $x^r$" only, compute the single $k$ where the $x$-power matches — no need for the full expansion."""

WE2_HE = """**פתחו** $(2x-3)^4$ באמצעות משפט הבינום.

פתיחת בינום היא ניהול רישום: מזהים $a=2x$, $b=-3$, $n=4$, ומסכמים איברים ל-$k=0,1,2,3,4$.

### צעד 1 — הגדרת האיבר הכללי
$$(2x-3)^4=\\sum_{k=0}^{4}\\binom{4}{k}(2x)^{4-k}(-3)^k.$$

### צעד 2 — בניית טבלה (מפחיתה טעויות סימן)

| $k$ | $\\binom{4}{k}$ | $(2x)^{4-k}$ | $(-3)^k$ | איבר |
|---|---|---|---|---|
| $0$ | $1$ | $16x^4$ | $1$ | $16x^4$ |
| $1$ | $4$ | $8x^3$ | $-3$ | $-96x^3$ |
| $2$ | $6$ | $4x^2$ | $9$ | $216x^2$ |
| $3$ | $4$ | $2x$ | $-27$ | $-216x$ |
| $4$ | $1$ | $1$ | $81$ | $81$ |

### צעד 3 — צירוף
**תוצאה:** $16x^4-96x^3+216x^2-216x+81$.

### צעד 4 — בדיקה מהירה
סימנים מתחלפים כש-$b<0$ ו-$n$ זוגי → איבר ראשון ואחרון חיוביים ✓. שורה 4 בפסקל: $1,4,6,4,1$ תואמת מקדמים לפני חזקות.

**הערת בחינה:** ל"מקדם $x^r$" בלבד, מחשבים את $k$ היחיד שבו חזקת $x$ מתאימה — אין צורך בפתיחה מלאה."""

WE3_EN = """**Problem:** From 4 men and 5 women, how many committees of 4 can be formed with **at least 2 women**?

"At least 2" invites two standard approaches: **direct case split** or **complement**. Pick the one with fewer cases.

### Move 1 — Direct: exactly 2, 3, or 4 women
Cases are disjoint and cover "at least 2":

- Exactly 2 women: $\\binom{5}{2}\\binom{4}{2}=10\\times6=60$.
- Exactly 3 women: $\\binom{5}{3}\\binom{4}{1}=10\\times4=40$.
- Exactly 4 women: $\\binom{5}{4}\\binom{4}{0}=5\\times1=5$.

**Total (direct):** $60+40+5=105$.

### Move 2 — Complement check
Total committees from 9 people: $\\binom{9}{4}=126$.

Unwanted (fewer than 2 women = 0 or 1 woman):
- 0 women: $\\binom{5}{0}\\binom{4}{4}=1$.
- 1 woman: $\\binom{5}{1}\\binom{4}{3}=5\\times4=20$.

**Complement:** $126-1-20=105$ ✓.

### Move 3 — Why both methods agree
Direct and complement partition the same sample space — agreement confirms no missing or double-counted case.

**Exam strategy:** For "at least $k$", compare counting unwanted cases vs listing wanted cases. Here complement uses two subtractions; direct uses three additions — similar effort, but complement is safer when "at least" means many cases."""

WE3_HE = """**בעיה:** מ-4 גברים ו-5 נשים, כמה ועדות של 4 ניתן להרכיב עם **לפחות 2 נשים**?

"לפחות 2" מזמין שתי גישות: **פיצול ישיר** או **משלים**. בחרו את זו עם פחות מקרים.

### צעד 1 — ישיר: בדיוק 2, 3 או 4 נשים
המקרים זרים ומכסים "לפחות 2":

- בדיוק 2 נשים: $\\binom{5}{2}\\binom{4}{2}=10\\times6=60$.
- בדיוק 3 נשים: $\\binom{5}{3}\\binom{4}{1}=10\\times4=40$.
- בדיוק 4 נשים: $\\binom{5}{4}\\binom{4}{0}=5\\times1=5$.

**סה"כ (ישיר):** $60+40+5=105$.

### צעד 2 — בדיקת משלים
כל הוועדות מ-9 אנשים: $\\binom{9}{4}=126$.

לא רצוי (פחות מ-2 נשים = 0 או 1):
- 0 נשים: $\\binom{5}{0}\\binom{4}{4}=1$.
- 1 אישה: $\\binom{5}{1}\\binom{4}{3}=5\\times4=20$.

**משלים:** $126-1-20=105$ ✓.

### צעד 3 — למה שתי השיטות מסכימות
ישיר ומשלים מחלקים את אותו מרחב מדגם — הסכמה מאשרת שאין מקרה חסר או ספירה כפולה.

**אסטרטגיית בחינה:** ב"לפחות $k$", השוו ספירת לא-רצוי מול רשימת רצוי. כאן משלים — שתי חיסורים; ישיר — שלוש חיבורים — מאמץ דומה, אך משלים בטוח יותר כש"לפחות" פירושו הרבה מקרים."""

CHK1_EN = """How many 3-digit numbers from digits $\\{1,2,3,4,5\\}$?

**Part (a) — digits can repeat:** Each of 3 positions has 5 choices independently.
$$5\\times5\\times5=5^3=125.$$

**Part (b) — no repetition:** First digit 5 ways, second 4, third 3 — order matters.
$$P(5,3)=5\\times4\\times3=60.$$

**Check:** With repetition allowed, count exceeds without repetition ($125>60$) ✓. **Answers:** (a) $125$; (b) $60$."""

CHK1_HE = """כמה מספרים בני 3 ספרות מהספרות $\\{1,2,3,4,5\\}$?

**סעיף (א) — עם חזרות:** לכל אחת מ-3 הספרות 5 אפשרויות.
$$5\\times5\\times5=5^3=125.$$

**סעיף (ב) — ללא חזרות:** ספרה ראשונה 5, שנייה 4, שלישית 3 — סדר חשוב.
$$P(5,3)=5\\times4\\times3=60.$$

**בדיקה:** עם חזרות הספירה גדולה יותר ($125>60$) ✓. **תשובות:** (א) $125$; (ב) $60$."""

CHK2_EN = """Find the coefficient of $x^2$ in $(1+2x)^5$.

**Step 1:** General term $\\binom{5}{k}(1)^{5-k}(2x)^k$. Need $x^2$ → $k=2$.

**Step 2:** $\\binom{5}{2}(1)^3(2x)^2=10\\times1\\times4x^2=40x^2$.

**Step 3:** Coefficient is $40$ (not $40x^2$ — read the question).

**Verify:** Middle terms of row 5 are $10,10$; power $(2x)^2$ contributes factor $4$ → $10\\times4=40$ ✓."""

CHK2_HE = """מצאו את המקדם של $x^2$ בפיתוח $(1+2x)^5$.

**שלב 1:** איבר כללי $\\binom{5}{k}(1)^{5-k}(2x)^k$. צריך $x^2$ → $k=2$.

**שלב 2:** $\\binom{5}{2}(1)^3(2x)^2=10\\times1\\times4x^2=40x^2$.

**שלב 3:** המקדם הוא $40$ (לא $40x^2$ — קראו את השאלה).

**אימות:** איברי אמצע בשורה 5 הם $10,10$; $(2x)^2$ תורם גורם $4$ → $10\\times4=40$ ✓."""

METHOD_EN = """| Situation | Formula | Decision cue |
|---|---|---|
| Order matters, no repetition | $P(n,r)=n!/(n-r)!$ | Line, ranking, distinct roles |
| Order irrelevant, no repetition | $\\binom{n}{r}=n!/[r!(n-r)!]$ | Committee, subset, hand |
| With repetition, order matters | $n^r$ | PIN, multi-digit with repeats |
| With repetition, order irrelevant | Stars and bars (5-unit) | Identical items into bins |
| "At least $k$" | Complement or case split | Compare # of unwanted cases |
| Binomial term $k$ | $\\binom{n}{k}a^{n-k}b^k$ | Match power of $x$ to find $k$ |

**Workflow:** (1) Does order matter? → P vs C. (2) Can items repeat? → multiply principle vs $n^r$. (3) Any restriction? → split or complement. (4) Write formula before plugging numbers.

**When to use:** On Bagrut items, underline keywords ("committee", "president", "with repetition") before touching the calculator — wrong formula with correct arithmetic still scores zero."""

METHOD_HE = """| מצב | נוסחה | רמז להחלטה |
|---|---|---|
| סדר חשוב, ללא חזרה | $P(n,r)=n!/(n-r)!$ | שורה, דירוג, תפקידים |
| סדר לא חשוב, ללא חזרה | $\\binom{n}{r}=n!/[r!(n-r)!]$ | ועדה, תת-קבוצה, יד |
| עם חזרה, סדר חשוב | $n^r$ | PIN, ספרות עם חזרות |
| עם חזרה, סדר לא חשוב | כוכבים ופסים (5 יח') | פריטים זהים לתאים |
| "לפחות $k$" | משלים או פיצול | השוו מספר מקרים לא רצויים |
| איבר $k$ בבינום | $\\binom{n}{k}a^{n-k}b^k$ | התאמת חזקת $x$ ל-$k$ |

**תהליך:** (1) האם סדר חשוב? → P מול C. (2) האם יש חזרות? → כפל מול $n^r$. (3) אילוץ? → פיצול או משלים. (4) כתבו נוסחה לפני מספרים.

**מתי להשתמש:** בבגרות, סמנו מילות מפתח ("ועדה", "יו\"ר", "עם חזרות") לפני מחשבון — נוסחה שגויה עם חשבון נכון = אפס נקודות."""

PITFALL_EN = """1. **Permutation vs. combination.** "Stand in a line", "rank 1st–3rd", "president/secretary" → order matters → $P(n,r)$. "Committee", "choose a team", "select books" → order irrelevant → $\\binom{n}{r}$. When unsure, ask: "Does swapping two chosen people create a new outcome?"

2. **$0!=1$, not $0$.** Empty product convention; appears in $\\binom{n}{0}=n!/(0!\\cdot n!)=1$.

3. **Double counting with identical items.** Arranging the letters in "BANANA" is not $6!$ — divide by $3!$ (three A's) and $2!$ (two N's): $6!/(3!\\cdot2!)=60$.

4. **"At least" without a plan.** Do not guess cases. Either list all valid counts (2, 3, 4 women…) or subtract unwanted from total. Verify both routes when time allows.

5. **Binomial sign errors.** When $b$ is negative, $(-3)^k$ alternates. Track $k$ in a table — do not expand mentally under exam pressure.

**Example misconception:** Using $P(8,3)=336$ for an unordered committee of 3 from 8.

**Fix:** Committee → $\\binom{8}{3}=56$. Only multiply by $3!$ when roles distinguish the same people."""

PITFALL_HE = """1. **תמורה מול צירוף.** "לעמוד בשורה", "דירוג 1–3", "יו\"ר/מזכיר" → סדר חשוב → $P(n,r)$. "ועדה", "לבחור קבוצה", "לבחור ספרים" → סדר לא חשוב → $\\binom{n}{r}$. כשלא בטוחים: "האם החלפת שני נבחרים יוצרת תוצאה חדשה?"

2. **$0!=1$, לא $0$.** מוסכמת מכפלה ריקה; מופיע ב-$\\binom{n}{0}=1$.

3. **ספירה כפולה עם איברים זהים.** סידור אותיות ב-"BANANA" אינו $6!$ — מחלקים ב-$3!$ (שלוש A) ו-$2!$ (שתי N): $6!/(3!\\cdot2!)=60$.

4. **"לפחות" בלי תוכנית.** אל תנחשו מקרים. רשימת כל הספירות התקפות או חיסור לא-רצוי מהסך. אמתו שני מסלולים כשיש זמן.

5. **טעויות סימן בבינום.** כש-$b$ שלילי, $(-3)^k$ מתחלף. עקבו אחר $k$ בטבלה — אל תפתחו בראש תחת לחץ.

**דוגמת טעות:** שימוש ב-$P(8,3)=336$ לועדה לא מסודרת של 3 מ-8.

**תיקון:** ועדה → $\\binom{8}{3}=56$. מכפילים ב-$3!$ רק כשתפקידים מבדילים בין אותם אנשים."""

WHY_EN = """Combinatorics is the counting engine behind **probability** — every "favorable over total" fraction starts with accurate counting of equally likely outcomes. It also feeds **algebra** through the binomial theorem and connects to **sequences** via Pascal's triangle patterns.

**You will use this to unlock:**
- `concept:probability_basic` **Basic Probability** (prereq) — sample spaces, classical probability, conditional events.
- `concept:probability_conditional_bayes` — counting compound events efficiently.

**Builds on:** arithmetic, factorial notation, and basic algebra manipulation from earlier units.

**Why it matters for exams:** Bagrut 4–5 unit papers mix standalone counting items with probability and binomial-expansion questions. Transfer skill — recognizing "committee vs line" or "coefficient of $x^k$" — separates full credit from partial. When studying, always ask: "Which counting template fits this wording?" """

WHY_HE = """קומבינטוריקה היא מנוע הספירה מאחורי **הסתברות** — כל שבר "רצוי על סך הכל" מתחיל בספירה מדויקת של תוצאות שווי-סיכוי. היא גם מזינה **אלגברה** דרך משפט הבינום ומתחברת ל**סדרות** דרך דפוסי משולש פסקל.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:probability_basic` **הסתברות בסיסית** (prereq) — מרחבי מדגם, הסתברות קלאסית, מאורעות מורכבים.
- `concept:probability_conditional_bayes` — ספירה יעילה של מאורעות מורכבים.

**מבוסס על:** חשבון, סימון עצרת ומניפולציה אלגברית בסיסית מיחידות קודמות.

**למה זה חשוב לבחינות:** שאלות בגרות 4–5 יחידות משלבות ספירה עצמאית עם הסתברות ופתיחת בינום. מיומנות העברה — זיהוי "ועדה מול שורה" או "מקדם $x^k$" — מפרידה בין ניקוד מלא לחלקי. בלימוד, שאלו תמיד: "איזה תבנית ספירה מתאימה לניסוח?" """

BEFORE_EN = """**Core formulas (say each once aloud before entering the exam room):**
- $P(n,r)=\\dfrac{n!}{(n-r)!}$ — ordered arrangements, no repetition.
- $\\binom{n}{r}=\\dfrac{n!}{r!(n-r)!}$ — unordered selections, no repetition.
- With repetition when order matters: $n^r$ (each of $r$ slots has $n$ choices).
- Binomial general term: $\\binom{n}{k}a^{n-k}b^k$ — match $k$ to the required power of $x$.
- Row sum identity: $\\sum_{k=0}^n\\binom{n}{k}=2^n$ (count all subsets).
- Pascal's identity: $\\binom{n}{k}+\\binom{n}{k+1}=\\binom{n+1}{k+1}$.

**Decision checklist (write on scrap paper):** Does order matter? Can items repeat? Any "at least/at most" restriction → complement or case split?

**Last review:** Solve one checkpoint (3-digit counting with and without repetition + one binomial coefficient) without notes. Time target: 4 minutes total. If both are correct, you are ready."""

BEFORE_HE = """**נוסחאות ליבה (אמרו כל אחת פעם לפני כניסה לחדר הבחינה):**
- $P(n,r)=\\dfrac{n!}{(n-r)!}$ — סידורים מסודרים, ללא חזרה.
- $\\binom{n}{r}=\\dfrac{n!}{r!(n-r)!}$ — בחירות לא מסודרות, ללא חזרה.
- עם חזרה כשסדר חשוב: $n^r$ (לכל אחד מ-$r$ המקומות $n$ אפשרויות).
- איבר כללי בבינום: $\\binom{n}{k}a^{n-k}b^k$ — התאימו $k$ לחזקת $x$ הנדרשת.
- זהות סכום שורה: $\\sum_{k=0}^n\\binom{n}{k}=2^n$ (ספירת כל תת-הקבוצות).
- זהות פסקל: $\\binom{n}{k}+\\binom{n}{k+1}=\\binom{n+1}{k+1}$.

**צ'ק-ליסט (כתבו על טיוטה):** האם סדר חשוב? האם יש חזרות? אילוץ "לפחות/לכל היותר" → משלים או פיצול?

**חזרה אחרונה:** פתרו checkpoint אחד (ספרות תלת-ספרתיות עם ובלי חזרות + מקדם בינום) בלי notes. יעד: 4 דקות. אם שניהם נכונים — אתם מוכנים."""

SUMMARY_EN = """- **Multiplication principle** chains independent choices; **factorials** count full permutations.
- **Order matters** → $P(n,r)$; **order irrelevant** → $\\binom{n}{r}$; **repetition allowed** → $n^r$.
- **Pascal's triangle** encodes $\\binom{n}{k}$; each entry sums the two above.
- **Binomial theorem:** $(a+b)^n=\\sum\\binom{n}{k}a^{n-k}b^k$; row sums give $2^n$.
- **Restricted counting:** case-split or complement — verify both when possible.

**Takeaway:** Read the problem words before the formula. "Committee" and "president" look similar but live on opposite sides of the counting fork."""

SUMMARY_HE = """- **עקרון הכפל** משרשר בחירות בלתי תלויות; **עצרות** סופרות תמורות מלאות.
- **סדר חשוב** → $P(n,r)$; **סדר לא** → $\\binom{n}{r}$; **חזרה מותרת** → $n^r$.
- **משולש פסקל** מקודד $\\binom{n}{k}$; כל ערך = סכום שני מעליו.
- **משפט הבינום:** $(a+b)^n=\\sum\\binom{n}{k}a^{n-k}b^k$; סכומי שורה נותנים $2^n$.
- **ספירה עם אילוצים:** פיצול או משלים — אמתו שניהם כשאפשר.

**מסקנה:** קראו את הניסוח לפני הנוסחה. "ועדה" ו-"יו\"ר" נראים דומים אך נמצאים בצדדים מנוגדים של מזלג הספירה."""

EXPLS = {
    1: fmt_expl(
        "Choosing 2 books from 7 without regard to order is a combination: $\\binom{7}{2}=\\frac{7\\times6}{2}=21$. Option $42$ is $P(7,2)$ — ordered selection on a shelf. $14=2\\times7$ doubles one factor incorrectly; $7$ counts single books, not pairs.",
        "Underline \"choose\" — no ranking, no shelf order. Compute $\\binom{n}{r}$ with cancellation: $7\\times6/2$ before touching a calculator. Ask: would swapping the two books change the outcome? No → combination.",
        "Using $P(7,2)=42$ because \"2 books\" sounds like arranging. Or computing $7+7+7=21$ by flawed repeated addition instead of $\\binom{7}{2}$. Both confuse ordered and unordered counting.",
        "On MCQ combinatorics, list the four options and identify which formula produced each wrong answer — that catches permutation/combination swaps instantly and saves rework on later parts.",
        "בחירת 2 ספרים מ-7 ללא התחשבות בסדר היא צירוף: $\\binom{7}{2}=\\frac{7\\times6}{2}=21$. $42$ הוא $P(7,2)$ — בחירה מסודרת על מדף. $14$ מכפיל גורם אחד בטעות; $7$ סופר ספרים בודדים, לא זוגות.",
        "סמנו \"לבחור\" — אין דירוג, אין סדר על מדף. חשבו $\\binom{n}{r}$ עם צמצום: $7\\times6/2$ לפני מחשבון. שאלו: האם החלפת שני הספרים משנה את התוצאה? לא → צירוף.",
        "שימוש ב-$P(7,2)=42$ כי \"2 ספרים\" נשמע כמו סידור. או $7+7+7=21$ במקום $\\binom{7}{2}$ — שני אלה מערבבים ספירה מסודרת ולא מסודרת.",
        "ב-MCQ קומבינטוריקה, רשמו את ארבע התשובות וזהו איזו נוסחה ייצרה כל שגיאה — תופס החלפות P/C מיד וחוסך זמן בסעיפים הבאים.",
    ),
    2: fmt_expl(
        "Five distinct people in a line — every ordering is different. All 5 are used, order matters: $5!=5\\times4\\times3\\times2\\times1=120$. No one is left out; each position is a distinct slot in the row.",
        "\"Stand in a line\" = full permutation of 5. This is $P(5,5)=5!$, not $\\binom{5}{5}=1$ (which would ignore order entirely). The factorial counts all bijections from positions to people.",
        "Answering $1$ by treating it as one unordered group, or $5$ by counting people instead of arrangements. Another slip: using $P(5,1)=5$ and stopping — that picks only one person for one spot.",
        "Full-line problems are the fastest points on the exam — recognize $n!$ immediately when all $n$ distinct objects are arranged in a sequence with no restrictions.",
        "חמישה אנשים שונים בשורה — כל סידור שונה. כולם בשימוש, סדר חשוב: $5!=5\\times4\\times3\\times2\\times1=120$. אף אחד לא נשאר בחוץ; כל מקום הוא תפקיד נפרד בשורה.",
        "\"לעמוד בשורה\" = תמורה מלאה של 5. זה $P(5,5)=5!$, לא $\\binom{5}{5}=1$ (מתעלם מסדר). העצרת סופרת את כל ההתאמות בין מקומות לאנשים.",
        "תשובה $1$ כקבוצה לא מסודרת, או $5$ כספירת אנשים במקום סידורים. טעות נוספת: $P(5,1)=5$ — בוחרים רק אדם אחד למקום אחד.",
        "בעיות שורה מלאה — נקודות מהירות בבחינה; זיהו $n!$ מיד כשכל $n$ אובייקטים שונים מסודרים ברצף ללא אילוצים.",
    ),
    3: fmt_expl(
        "$\\binom{7}{2}=\\frac{7!}{2!\\cdot5!}=\\frac{7\\times6}{2\\times1}=21$. Symmetry check: $\\binom{7}{5}=21$ too — choosing 2 to keep equals leaving 5 out. Both routes confirm the same count.",
        "Apply the combination formula directly. Cancel $5!$ from numerator and denominator before multiplying to keep numbers small. Write the shortcut $\\binom{n}{r}=\\frac{n(n-1)\\cdots(n-r+1)}{r!}$ on your formula sheet.",
        "Getting $42$ from $7\\times6$ without dividing by $2!$ — that is $P(7,2)$, not $\\binom{7}{2}$. Or $7+7+7=21$ by incorrect reasoning that happens to match but will fail on other numbers.",
        "Always write $\\binom{n}{r}=\\frac{n(n-1)\\cdots(n-r+1)}{r!}$ as a shortcut — faster and less error-prone than full factorials on Bagrut. Verify with symmetry $\\binom{n}{r}=\\binom{n}{n-r}$ when $r$ is large.",
        "$\\binom{7}{2}=\\frac{7!}{2!\\cdot5!}=\\frac{7\\times6}{2\\times1}=21$. בדיקת סימטריה: $\\binom{7}{5}=21$ — בחירת 2 לשמירה שווה להשארת 5. שני המסלולים מאשרים אותה ספירה.",
        "יישמו נוסחת צירוף ישירות. צמצמו $5!$ לפני כפל — מספרים קטנים יותר. כתבו קיצור $\\binom{n}{r}=\\frac{n(n-1)\\cdots(n-r+1)}{r!}$ על דף הנוסחאות.",
        "$42$ מ-$7\\times6$ בלי חלוקה ב-$2!$ — זה $P(7,2)$, לא $\\binom{7}{2}$. או $7+7+7=21$ בטעות שמקרית נכונה אך תיכשל במספרים אחרים.",
        "כתבו $\\binom{n}{r}=\\frac{n(n-1)\\cdots}{r!}$ — מהיר ובטוח יותר מעצרות מלאות בבגרות. אמתו עם סימטריה $\\binom{n}{r}=\\binom{n}{n-r}$ כש-$r$ גדול.",
    ),
    4: fmt_expl(
        "Two-letter codes from 4 letters without repetition — order matters (AB $\\ne$ BA) and no letter repeats: $P(4,2)=4\\times3=12$. Each code is a sequence of distinct letters from $\\{A,B,C,D\\}$.",
        "First position: 4 choices. Second: 3 remaining. Multiplication principle gives $4\\times3$, equivalent to $P(4,2)$. If order did not matter, identical letters would collapse to one outcome — but codes differ by position.",
        "Using $\\binom{4}{2}=6$ which ignores order (treats AB and BA as one pair), or $4^2=16$ which allows repeated letters like AA. Both misread the \"no repetition\" and \"code\" constraints.",
        "Code and password stems almost always mean order matters — ask about repetition separately; here \"no repetition\" closes the $n^r$ path. On Bagrut, circle \"code\" and \"without repetition\" before calculating.",
        "קודים דו-אותיים מ-4 אותיות ללא חזרות — סדר חשוב (AB $\\ne$ BA) ואין אות חוזרת: $P(4,2)=4\\times3=12$. כל קוד הוא רצף של אותיות שונות מ-$\\{A,B,C,D\\}$.",
        "מקום ראשון: 4 אפשרויות. שני: 3 שנותרו. עקרון כפל → $4\\times3$, שווה ל-$P(4,2)$. אם סדר לא היה חשוב, AB ו-BA היו נספרים פעם אחת — אך קודים נבדלים במיקום.",
        "$\\binom{4}{2}=6$ מתעלם מסדר (AB ו-BA זוג אחד), או $4^2=16$ עם חזרות כמו AA. שניהם מפרשים שגוי את \"ללא חזרות\" ו\"קוד\".",
        "קודים וסיסמאות — סדר כמעט תמיד חשוב; \"ללא חזרות\" סוגר את מסלול $n^r$. בבגרות, הקיפו \"קוד\" ו\"ללא חזרות\" לפני החישוב.",
    ),
    5: fmt_expl(
        "$(1+x)^3$ has row 3 of Pascal: coefficients $1,3,3,1$. Expansion: $1+3x+3x^2+x^3$. Alternatively apply $\\sum_{k=0}^3\\binom{3}{k}(1)^{3-k}x^k$ term by term for $k=0,1,2,3$.",
        "Small $n$ — read coefficients straight from Pascal's triangle row 3. For $(a+b)^n$ with $a=1$, each term is $\\binom{n}{k}x^k$. Powers of $x$ ascend from $0$ to $3$; coefficients are symmetric.",
        "Writing $1-3x+3x^2-x^3$ with wrong signs (confusing $(1+x)^3$ with $(1-x)^3$), or stopping at $1+3x$ (missing higher powers). Another slip: omitting the constant term $1$.",
        "Memorize rows 0–4 of Pascal ($1;1,1;1,2,1;1,3,3,1;1,4,6,4,1$) — they cover most 4-unit binomial items without full expansion. Substitute $a=1,b=x$ mentally to read off coefficients.",
        "$(1+x)^3$ — שורה 3 בפסקל: מקדמים $1,3,3,1$. פיתוח: $1+3x+3x^2+x^3$. לחלופין $\\sum_{k=0}^3\\binom{3}{k}(1)^{3-k}x^k$ לכל $k=0,1,2,3$.",
        "$n$ קטן — קראו מקדמים ישירות משורה 3. עם $a=1$, כל איבר $\\binom{n}{k}x^k$. חזקות $x$ עולות מ-0 ל-3; מקדמים סימטריים.",
        "כתיבת $1-3x+3x^2-x^3$ (בלבול עם $(1-x)^3$), או עצירה ב-$1+3x$. טעות נוספת: השמטת האיבר הקבוע $1$.",
        "שננו שורות 0–4 בפסקל — מכסות רוב פריטי הבינום ב-4 יחידות. הציבו $a=1,b=x$ בראש כדי לקרוא מקדמים.",
    ),
    6: fmt_expl(
        "Seat 4 of 10 in a row — order matters, no one sits twice: $P(10,4)=10\\times9\\times8\\times7=5040$. The first chair, second chair, third, and fourth are distinguishable positions.",
        "Four distinct chairs in sequence → multiply four descending factors starting at 10. Not $\\binom{10}{4}=210$ (that would be an unordered group of 4). The phrase \"seated in a row\" is the decisive cue for permutation.",
        "Using $\\binom{10}{4}$ because \"choose 4 students\" appears in the stem — ignore \"seated in a row\" at your peril. Or computing $10/4$ or $10-4=6$ by arithmetic guesswork without a counting model.",
        "Highlight positional words (row, line, first chair) in the margin — they override generic \"choose\" language every time. Write $P(10,4)$ before multiplying to lock in the correct template.",
        "4 מ-10 בשורה — סדר חשוב, אף אחד לא יושב פעמיים: $P(10,4)=10\\times9\\times8\\times7=5040$. כיסא ראשון, שני, שלישי ורביעי הם מקומות נבדלים.",
        "ארבעה כיסאות ברצף → מכפילים ארבעה גורמים יורדים מ-10. לא $\\binom{10}{4}=210$ (קבוצה לא מסודרת). \"מושבים בשורה\" הוא הרמז המכריע לתמורה.",
        "$\\binom{10}{4}$ כי \"לבחור 4\" — התעלמות מ\"בשורה\". או $10/4$ או $10-4=6$ בניחוש חשבוני בלי מודל ספירה.",
        "סמנו מילים מיקומיות (שורה, כיסא ראשון) — הן גוברות על \"לבחור\". כתבו $P(10,4)$ לפני הכפל כדי לנעול את התבנית הנכונה.",
    ),
    7: fmt_expl(
        "Each topping is in or out — 8 independent yes/no choices: $2^8=256$ pizzas, including the plain pizza with no toppings ($\\binom{8}{0}=1$). Every subset of the 8 toppings corresponds to exactly one pizza.",
        "Subsets of an 8-element set: $\\sum_{k=0}^8\\binom{8}{k}=2^8$ by the binomial theorem with $a=b=1$. The question says \"any subset\", so count all $2^8$, not just non-empty ($2^8-1=255$).",
        "Using $8!=40320$ (ordering toppings on a list) or $\\binom{8}{4}=70$ (exactly half the toppings). Or forgetting the empty subset when the problem allows \"no toppings\" — that costs one valid pizza.",
        "Pizza/subset problems map directly to row-sum identity — write $2^n$ first, then check whether empty set is allowed. If the menu says \"choose any combination including none\", answer is $2^n$, not $2^n-1$.",
        "כל תוספת בפנים או לא — 8 בחירות בינאריות עצמאיות: $2^8=256$ פיצות, כולל פיצה ריקה ללא תוספות ($\\binom{8}{0}=1$). כל תת-קבוצה של 8 התוספות = פיצה אחת.",
        "תת-קבוצות של 8: $\\sum_{k=0}^8\\binom{8}{k}=2^8$ לפי משפט הבינום עם $a=b=1$. \"כל תת-קבוצה\" = כל $2^8$, לא רק לא-ריקות ($2^8-1=255$).",
        "$8!$ (סדר תוספות) או $\\binom{8}{4}=70$ (בדיוק חצי). שכחת תת-קבוצה ריקה כש\"ללא תוספות\" מותר — מפסידים פיצה אחת.",
        "בעיות תוספות/תת-קבוצות → $2^n$; בדקו אם ריקה מותרת. אם \"כל שילוב כולל ללא תוספות\" — $2^n$, לא $2^n-1$.",
    ),
    8: fmt_expl(
        "$n=6$ (even) → the unique middle term is at $k=3$: $\\binom{6}{3}x^3y^3=20x^3y^3$. For even $n$, $\\binom{n}{n/2}$ is the central coefficient; here $\\binom{6}{3}=20$.",
        "For $(x+y)^n$ with even $n$, the unique middle term has $k=n/2=3$. Compute $\\binom{6}{3}=\\frac{6\\times5\\times4}{3\\times2\\times1}=20$ — do not assume $k=3$ without checking $n$ first.",
        "Using $\\binom{6}{2}=15$ or $\\binom{6}{4}=15$ (one position off from center). Or reporting $15x^3y^3$ from misreading \"middle\" as \"second term\" ($k=1$). Odd $n$ would give two middle terms — not the case here.",
        "Binomial middle-term questions: write $k=n/2$ for even $n$, then one line of arithmetic. Odd $n$ has two distinct middle terms at $k=(n-1)/2$ and $k=(n+1)/2$ — read $n$ parity before starting.",
        "$n=6$ (זוגי) → איבר אמצעי יחיד ב-$k=3$: $\\binom{6}{3}x^3y^3=20x^3y^3$. ל-$n$ זוגי, $\\binom{n}{n/2}$ הוא מקדם האמצע; כאן $\\binom{6}{3}=20$.",
        "ב-$(x+y)^n$ עם $n$ זוגי, $k=n/2=3$. חשבו $\\binom{6}{3}=\\frac{6\\times5\\times4}{3\\times2\\times1}=20$ — אל תניחו $k=3$ בלי לבדוק $n$ קודם.",
        "$\\binom{6}{2}=15$ או $\\binom{6}{4}=15$ — מיקום אחד מהמרכז. או $15x^3y^3$ מ\"איבר שני\" ($k=1$). ל-$n$ אי-זוגי יש שני איברי אמצע — לא כאן.",
        "שאלות איבר אמצעי: $k=n/2$ ל-$n$ זוגי, ואז שורת חישוב. ל-$n$ אי-זוגי — שני איברים ב-$k=(n-1)/2$ ו-$k=(n+1)/2$; בדקו זוגיות לפני התחלה.",
    ),
}

EXERCISE_SOLS = {
    "e1": (
        "**Step 1:** \"Stand in a line\" — all 5 distinct people, order matters, no one left out.\n\n**Step 2:** Full permutation: $5!=5\\times4\\times3\\times2\\times1=120$.\n\n**Check:** $P(5,5)=5!$ — not $\\binom{5}{5}=1$, which would ignore order.",
        "**שלב 1:** \"לעמוד בשורה\" — 5 אנשים שונים, סדר חשוב, כולם בשימוש.\n\n**שלב 2:** תמורה מלאה: $5!=5\\times4\\times3\\times2\\times1=120$.\n\n**בדיקה:** $P(5,5)=5!$ — לא $\\binom{5}{5}=1$ שמתעלם מסדר.",
    ),
    "e2": (
        "**Step 1:** Combination — order of the two books does not matter.\n\n**Step 2:** $\\binom{7}{2}=\\frac{7\\times6}{2\\times1}=21$.\n\n**Check:** Symmetry $\\binom{7}{5}=21$ confirms the count.",
        "**שלב 1:** צירוף — סדר שני הספרים לא חשוב.\n\n**שלב 2:** $\\binom{7}{2}=\\frac{7\\times6}{2\\times1}=21$.\n\n**בדיקה:** סימטריה $\\binom{7}{5}=21$ מאשרת.",
    ),
    "e3": (
        "**Step 1:** Two-letter code — order matters (AB $\\ne$ BA), no repetition.\n\n**Step 2:** $P(4,2)=4\\times3=12$.\n\n**Check:** Not $\\binom{4}{2}=6$ (unordered) or $4^2=16$ (repetition allowed).",
        "**שלב 1:** קוד דו-אותי — סדר חשוב (AB $\\ne$ BA), ללא חזרות.\n\n**שלב 2:** $P(4,2)=4\\times3=12$.\n\n**בדיקה:** לא $\\binom{4}{2}=6$ (לא מסודר) ולא $4^2=16$ (עם חזרות).",
    ),
    "e4": (
        "**Step 1:** Row 3 of Pascal's triangle: $1,3,3,1$.\n\n**Step 2:** $(1+x)^3=1+3x+3x^2+x^3$.\n\n**Check:** Coefficients symmetric; constant term $1=\\binom{3}{0}$.",
        "**שלב 1:** שורה 3 בפסקל: $1,3,3,1$.\n\n**שלב 2:** $(1+x)^3=1+3x+3x^2+x^3$.\n\n**בדיקה:** מקדמים סימטריים; איבר קבוע $1=\\binom{3}{0}$.",
    ),
    "e5": (
        "**Step 1:** \"Seated in a row\" — four distinct chairs, order matters.\n\n**Step 2:** Choose and arrange 4 of 10: $P(10,4)=10\\times9\\times8\\times7=5040$.\n\n**Check:** Not $\\binom{10}{4}=210$ — that ignores seating order.",
        "**שלב 1:** \"מושבים בשורה\" — ארבעה כיסאות נבדלים, סדר חשוב.\n\n**שלב 2:** בוחרים ומסדרים 4 מ-10: $P(10,4)=10\\times9\\times8\\times7=5040$.\n\n**בדיקה:** לא $\\binom{10}{4}=210$ — מתעלם מסדר הישיבה.",
    ),
    "e6": (
        "**Step 1:** Each of 8 toppings is in or out — independent binary choices.\n\n**Step 2:** All subsets: $2^8=256$, including the plain pizza with no toppings.\n\n**Check:** Row-sum identity $\\sum_{k=0}^8\\binom{8}{k}=2^8$.",
        "**שלב 1:** כל אחת מ-8 התוספות בפנים או לא — בחירות בינאריות עצמאיות.\n\n**שלב 2:** כל תת-קבוצות: $2^8=256$, כולל פיצה ריקה ללא תוספות.\n\n**בדיקה:** זהות סכום שורה $\\sum_{k=0}^8\\binom{8}{k}=2^8$.",
    ),
    "e7": (
        "**Step 1:** $n=6$ is even — unique middle term at $k=n/2=3$.\n\n**Step 2:** $\\binom{6}{3}x^3y^3=20x^3y^3$.\n\n**Check:** $\\binom{6}{3}=\\frac{6\\times5\\times4}{6}=20$ — largest coefficient in row 6.",
        "**שלב 1:** $n=6$ זוגי — איבר אמצעי יחיד ב-$k=n/2=3$.\n\n**שלב 2:** $\\binom{6}{3}x^3y^3=20x^3y^3$.\n\n**בדיקה:** $\\binom{6}{3}=\\frac{6\\times5\\times4}{6}=20$ — המקדם הגדול ביותר בשורה 6.",
    ),
    "e8": (
        "**Step 1:** Write $\\binom{n}{n-r}$ using the formula.\n\n**Step 2:** $\\binom{n}{n-r}=\\frac{n!}{(n-r)!(n-(n-r))!}=\\frac{n!}{(n-r)!\\,r!}=\\binom{n}{r}$. ✓\n\n**Check:** Choosing $r$ to keep equals choosing $n-r$ to leave out.",
        "**שלב 1:** כתבו $\\binom{n}{n-r}$ לפי הנוסחה.\n\n**שלב 2:** $\\binom{n}{n-r}=\\frac{n!}{(n-r)!(n-(n-r))!}=\\frac{n!}{(n-r)!\\,r!}=\\binom{n}{r}$. ✓\n\n**בדיקה:** בחירת $r$ לשמירה שווה להשארת $n-r$.",
    ),
    "e9": (
        "**Step 1:** Fix person $A$ in the committee — one slot taken.\n\n**Step 2:** Choose 2 more from the remaining 5: $\\binom{5}{2}=10$.\n\n**Check:** Total committees $\\binom{6}{3}=20$; half include $A$ when no restriction on $A$.",
        "**שלב 1:** קבעו את $A$ בוועדה — מקום אחד תפוס.\n\n**שלב 2:** בחרו עוד 2 מ-5 הנותרים: $\\binom{5}{2}=10$.\n\n**בדיקה:** סה\"כ ועדות $\\binom{6}{3}=20$; מחצית כוללות את $A$.",
    ),
    "e10": (
        "**Step 1:** General term $\\binom{7}{k}2^{7-k}(3x)^k$. Need $x^3$ → $k=3$.\n\n**Step 2:** $\\binom{7}{3}2^4(3x)^3=35\\times16\\times27x^3=15120x^3$.\n\n**Check:** Coefficient $35\\times16\\times27=15120$; verify $k$ by matching $x$-power.",
        "**שלב 1:** איבר כללי $\\binom{7}{k}2^{7-k}(3x)^k$. צריך $x^3$ → $k=3$.\n\n**שלב 2:** $\\binom{7}{3}2^4(3x)^3=35\\times16\\times27x^3=15120x^3$.\n\n**בדיקה:** מקדם $35\\times16\\times27=15120$; אמתו $k$ לפי חזקת $x$.",
    ),
    "e11": (
        "**Step 1:** Apply binomial theorem with $a=1$, $b=1$.\n\n**Step 2:** $(1+1)^n=\\sum_{k=0}^n\\binom{n}{k}1^{n-k}1^k=\\sum_{k=0}^n\\binom{n}{k}=2^n$. ✓\n\n**Check:** Counts all subsets of an $n$-element set — each element in or out.",
        "**שלב 1:** הציבו $a=1$, $b=1$ במשפט הבינום.\n\n**שלב 2:** $(1+1)^n=\\sum_{k=0}^n\\binom{n}{k}=2^n$. ✓\n\n**בדיקה:** סופר כל תת-קבוצות של $n$ איברים — כל איבר בפנים או בחוץ.",
    ),
    "e12": (
        "**Step 1:** Split into two independent choices: aces and non-aces.\n\n**Step 2:** $\\binom{4}{2}\\times\\binom{48}{3}=6\\times17296=103776$.\n\n**Check:** Multiplication principle — choose 2 of 4 aces AND 3 of 48 others.",
        "**שלב 1:** פיצול לשתי בחירות עצמאיות: אסים ולא-אסים.\n\n**שלב 2:** $\\binom{4}{2}\\times\\binom{48}{3}=6\\times17296=103776$.\n\n**בדיקה:** עקרון כפל — 2 מ-4 אסים וגם 3 מ-48 אחרים.",
    ),
    "e13": (
        "**Step 1:** Write both binomial coefficients with factorials.\n\n**Step 2:** $\\binom{n}{k}+\\binom{n}{k+1}=\\frac{n!}{k!(n-k)!}+\\frac{n!}{(k+1)!(n-k-1)!}$\n\n**Step 3:** Common denominator $(k+1)!(n-k)!$:\n$\\frac{n!(k+1)+n!(n-k)}{(k+1)!(n-k)!}=\\frac{(n+1)!}{(k+1)!(n-k)!}=\\binom{n+1}{k+1}$. ✓",
        "**שלב 1:** כתבו שני מקדמי הבינום עם עצרות.\n\n**שלב 2:** $\\binom{n}{k}+\\binom{n}{k+1}=\\frac{n!}{k!(n-k)!}+\\frac{n!}{(k+1)!(n-k-1)!}$\n\n**שלב 3:** מכנה משותף $(k+1)!(n-k)!$:\n$\\frac{n!(k+1)+n!(n-k)}{(k+1)!(n-k)!}=\\binom{n+1}{k+1}$. ✓",
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
        "Counting principles: permutations, combinations, Pascal's triangle, "
        "binomial coefficient properties, and the binomial theorem — with decision-first strategy."
    )
    data["summary_he"] = (
        "עקרונות ספירה: תמורות, צירופים, משולש פסקל, תכונות מקדם הבינום "
        "ומשפט הבינום — עם אסטרטגיית החלטה קודם."
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
            if "3-digit" in sec.get("body_en_md", "") or "3 ספרות" in sec.get("body_he_md", ""):
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
        elif kind == "exercise_set":
            for ex in sec.get("exercises", []):
                eid = ex.get("id")
                if eid in EXERCISE_SOLS:
                    ex["solution_en"], ex["solution_he"] = EXERCISE_SOLS[eid]

    fixes = {
        2: ["120", "$120$"],
        3: ["21", "$21$"],
        4: ["12", "$12$", "P(4,2)=12"],
        5: ["$1+3x+3x^2+x^3$", "1+3x+3x^2+x^3"],
        6: ["5040", "$5040$", "P(10,4)=5040"],
        7: ["256", "$256$", "2^8=256"],
        8: ["$20x^3y^3$", "20x^3y^3", "20"],
    }
    atom_map = {
        1: ["combinations"],
        2: ["permutations"],
        3: ["combinations"],
        4: ["permutations"],
        5: ["binomial_theorem", "pascals_triangle"],
        6: ["permutations"],
        7: ["combinations", "pascals_triangle"],
        8: ["binomial_theorem", "pascals_triangle"],
    }
    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]
        if ord_ in fixes and q["kind"] == "short_answer":
            q["answer_payload"]["acceptable_answers"] = fixes[ord_]
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
