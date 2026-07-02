#!/usr/bin/env python3
"""Expand function_basics_uni.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/function_basics_uni.json"

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


def main():
    with open(TARGET, encoding="utf-8") as f:
        data = json.load(f)

    # --- sections ---
    for sec in data["sections"]:
        sid = sec.get("id", sec.get("kind", ""))
        kind = sec["kind"]

        if sid == "intro" or (kind == "intro" and sid == "intro"):
            sec["body_en_md"] = """A **function** $f:A\\to B$ assigns to each element $a\\in A$ (the **domain**) exactly one element $f(a)\\in B$ (the **codomain**). The defining phrase is **exactly one**: every input has one output, but the same output may arise from several inputs. This is the set-theoretic foundation used throughout calculus, linear algebra, and real analysis at Israeli universities.

**Notation and diagrams:** Write $f:A\\to B$ to record domain and codomain explicitly — they are part of the definition, not optional labels. Arrow diagrams from $A$ to $B$ must show exactly one arrow leaving each point in $A$. Tables of pairs $(a,f(a))$ define a function only when no $a$ appears twice with different outputs.

**Why university courses start here:** Before limits, derivatives, or integrals, you must know when a rule is a function, when it is one-to-one, and when every target value is hit. These properties determine whether an inverse exists, whether a composition is well-defined, and whether a transformation is invertible in linear algebra. Master this lesson and `concept:uni_limits`, `concept:uni_derivatives`, and `concept:la_matrices` all build on the same vocabulary."""
            sec["body_he_md"] = """**פונקציה** $f:A\\to B$ משייכת לכל $a\\in A$ (**תחום**) בדיוק אלמנט אחד $f(a)\\in B$ (**קוד-תחום**). הביטוי המכריע: **בדיוק אחד** — לכל קלט פלט יחיד, אך אותו פלט עלול לצמוח מכמה קלטים. זו יסוד תורת הקבוצות בחדו"א, אלגברה לינארית ואנליזה ממשית באוניברסיטאות בישראל.

**סימון ודיאגרמות:** כותבים $f:A\\to B$ כדי לרשום תחום וקוד-תחום במפורש — הם חלק מההגדרה, לא תוויות אופציונליות. בדיאגרמת חצים מ-$A$ ל-$B$ יוצא בדיוק חץ אחד מכל נקודה ב-$A$. טבלת זוגות $(a,f(a))$ מגדירה פונקציה רק כשאין $a$ שחוזר עם פלטים שונים.

**למה קורסים מתחילים כאן:** לפני גבולות, נגזרות או אינטגרלים חייבים לדעת מתי כלל הוא פונקציה, מתי חד-חד-ערכית ומתי כל ערך יעד מושג. תכונות אלה קובעות אם קיימת פונקציה הפוכה, אם הרכבה מוגדרת היטב, ואם טרנספורמציה הפיכה באלגברה לינארית. שליטה בשיעור זה פותחת את `concept:uni_limits`, `concept:uni_derivatives` ו-`concept:la_matrices`."""

        elif sid == "definition":
            sec["body_en_md"] = """**Injective (one-to-one, 1-1):** $f(a_1)=f(a_2) \\Rightarrow a_1=a_2$. Equivalently: distinct inputs produce distinct outputs. To **disprove** injectivity, exhibit $a_1\\neq a_2$ with $f(a_1)=f(a_2)$.

**Surjective (onto):** $\\forall b\\in B,\\; \\exists a\\in A: f(a)=b$. Every element of the codomain $B$ is an output of some input. To **disprove** surjectivity, find $b\\in B$ with no preimage in $A$.

**Bijective:** both injective and surjective. A bijection pairs elements of $A$ and $B$ perfectly — no element is left out and no two inputs collide.

**Range (image):** $f(A)=\\{f(a):a\\in A\\}\\subseteq B$. Surjective $\\Leftrightarrow$ range $= B$. The range can be strictly smaller than the codomain when $f$ is not onto.

**Inverse function $f^{-1}$:** exists as a function $B\\to A$ **if and only if** $f$ is bijective. If bijective, define $f^{-1}(b)=a$ where $f(a)=b$ (exists by surjection; unique by injection).

**Finite-set intuition:** For finite sets, $|A|=|B|$ is necessary for a bijection. A bijection between $\\mathbb{N}$ and $\\mathbb{Z}$ shows infinite sets can have the same "size" despite looking different."""
            sec["body_he_md"] = """**חד-חד-ערכית (1-1):** $f(a_1)=f(a_2) \\Rightarrow a_1=a_2$. במילים: קלטים שונים → פלטים שונים. **להפרכה:** מצאו $a_1\\neq a_2$ עם $f(a_1)=f(a_2)$.

**על-ביות (onto):** $\\forall b\\in B,\\; \\exists a\\in A: f(a)=b$. כל אלמנט בקוד-תחום $B$ הוא פלט של קלט כלשהו. **להפרכה:** מצאו $b\\in B$ ללא מקור (preimage) ב-$A$.

**ביעיה:** חד-חד-ערכית ועל-ביות יחד. ביעיה יוצרת התאמה מושלמת בין $A$ ל-$B$ — אין אלמנט מוחרג ואין התנגשות בין קלטים.

**תמונה (range):** $f(A)=\\{f(a):a\\in A\\}\\subseteq B$. על $\\Leftrightarrow$ תמונה $= B$. התמונה עלולה להיות קטנה מקוד-תחום כש-$f$ אינה על.

**פונקציה הפוכה $f^{-1}$:** קיימת כפונקציה $B\\to A$ **אמ\"מ** $f$ ביעיה. אז $f^{-1}(b)=a$ כאשר $f(a)=b$ (קיים מ\"על\"; יחיד מ\"חד-חד-ערכית\").

**אינטואיציה על קבוצות סופיות:** בקבוצות סופיות, $|A|=|B|$ נדרש לביעיה. ביעיה בין $\\mathbb{N}$ ל-$\\mathbb{Z}$ מראה שקבוצות אינסופיות יכולות להיות \"באותו גודל\" למרות מראה שונה."""

        elif sid == "theory":
            sec["body_en_md"] = """**Test for injectivity (direct proof):** Assume $f(a_1)=f(a_2)$ and algebraically derive $a_1=a_2$. This is the standard university proof template.

**Test for non-injectivity (counterexample):** Find explicit $a_1\\neq a_2$ with $f(a_1)=f(a_2)$. One counterexample suffices — no general proof needed.

**Test for surjectivity:** Given arbitrary $b\\in B$, solve $f(a)=b$ for $a$ and verify $a\\in A$. Constructing the preimage explicitly is required; saying "clearly surjective" earns no credit.

**Horizontal line test (graphs):** $f:\\mathbb{R}\\to\\mathbb{R}$ is injective iff every horizontal line $y=c$ intersects the graph at **most once**. Two intersections mean two inputs share an output.

**Composition rules:** If $f:A\\to B$ and $g:B\\to C$, then $g\\circ f:A\\to C$. If both $f$ and $g$ are injective, so is $g\\circ f$. If both are surjective, so is $g\\circ f$. Bijections compose to bijections.

**Important partial result:** If $g\\circ f$ is injective, then $f$ is injective (but $g$ need not be). If $g\\circ f$ is surjective, then $g$ is surjective (but $f$ need not be). These appear frequently on university problem sets.

**Restricting the domain:** A function failing injectivity on all of $\\mathbb{R}$ may become injective on a smaller interval — e.g. $x^2$ on $[0,\\infty)$. Domain restriction is a standard technique before defining inverses."""
            sec["body_he_md"] = """**בדיקת חד-חד-ערכיות (הוכחה ישירה):** ניחוש $f(a_1)=f(a_2)$ וגזירה אלגברית של $a_1=a_2$. זו תבנית ההוכחה הסטנדרטית באוניברסיטה.

**בדיקת \"לא חד-חד-ערכית\" (דוגמה נגדית):** מצאו $a_1\\neq a_2$ עם $f(a_1)=f(a_2)$ במפורש. דוגמה נגדית אחת מספיקה — אין צורך בהוכחה כללית.

**בדיקת על-ביות:** נתון $b\\in B$ כלשהו — פתרו $f(a)=b$ עבור $a$ וודאו $a\\in A$. בניית המקור (preimage) במפורש נדרשת; \"ברור שעל\" לא מזכה בנקודות.

**בדיקת קו אופקי (גרפים):** $f:\\mathbb{R}\\to\\mathbb{R}$ חד-חד-ערכית אמ\"מ כל קו אופקי $y=c$ חותך את הגרף **לכל היותר פעם אחת**. שני חיתוכים = שני קלטים, פלט אחד.

**כללי הרכבה:** אם $f:A\\to B$ ו-$g:B\\to C$, אז $g\\circ f:A\\to C$. אם $f$ ו-$g$ חד-חד-ערכיות — גם $g\\circ f$. אם שתיהן על — גם $g\\circ f$. ביעיות מורכבות לביעיה.

**תוצאה חלקית חשובה:** אם $g\\circ f$ חד-חד-ערכית, אז $f$ חד-חד-ערכית (אך $g$ לא בהכרח). אם $g\\circ f$ על — אז $g$ על (אך $f$ לא בהכרח). מופיע לעיתים קרובות בתרגילי בית.

**הגבלת תחום:** פונקציה שאינה חד-חד-ערכית על $\\mathbb{R}$ עלולה להיות כזו על קטע קטן — למשל $x^2$ על $[0,\\infty)$. הגבלת תחום היא טכניקה סטנדרטית לפני הגדרת הפיכה."""

        elif sid == "worked_example_1":
            sec["body_en_md"] = """**Question:** Is $f(x)=x^2$ injective on $\\mathbb{R}$? On $[0,\\infty)$?

This classic example shows that **domain matters** — the same formula can be injective or not depending on where it is defined.

### Move 1: Test on $\\mathbb{R}$
Compute $f(2)=4$ and $f(-2)=4$. We have $2\\neq -2$ but $f(2)=f(-2)$. **Not injective** on $\\mathbb{R}$. Graphically, the horizontal line $y=4$ hits the parabola twice.

### Move 2: Set up injectivity proof on $[0,\\infty)$
Suppose $a,b\\ge 0$ and $f(a)=f(b)$, so $a^2=b^2$. Then $(a-b)(a+b)=0$, hence $a-b=0$ or $a+b=0$.

### Move 3: Use non-negativity
Since $a,b\\ge 0$, we have $a+b\\ge 0$. The case $a+b=0$ forces $a=b=0$. The case $a-b=0$ gives $a=b$. In all cases $a=b$. **Injective** on $[0,\\infty)$ ✓

### Move 4: Horizontal line test confirmation
On $[0,\\infty)$ the parabola branch is strictly increasing — every horizontal line meets it at most once.

**Takeaway:** Restricting domain to where $f$ is monotone is the standard fix before defining $f^{-1}(y)=\\sqrt{y}$."""
            sec["body_he_md"] = """**שאלה:** האם $f(x)=x^2$ חד-חד-ערכית ב-$\\mathbb{R}$? ב-$[0,\\infty)$?

דוגמה קלאסית שמראה ש**התחום קובע** — אותה נוסחה יכולה להיות חד-חד-ערכית או לא, תלוי היכן היא מוגדרת.

### צעד 1: בדיקה על $\\mathbb{R}$
$f(2)=4$ ו-$f(-2)=4$. יש $2\\neq -2$ אך $f(2)=f(-2)$. **לא חד-חד-ערכית** על $\\mathbb{R}$. גרפית, הקו $y=4$ חותך את הפרבולה פעמיים.

### צעד 2: הכנת הוכחת חד-חד-ערכיות על $[0,\\infty)$
נניח $a,b\\ge 0$ ו-$f(a)=f(b)$, כלומר $a^2=b^2$. אז $(a-b)(a+b)=0$, לכן $a-b=0$ או $a+b=0$.

### צעד 3: שימוש באי-שליליות
מ-$a,b\\ge 0$ מתקבל $a+b\\ge 0$. במקרה $a+b=0$ — $a=b=0$. במקרה $a-b=0$ — $a=b$. בכל המקרים $a=b$. **חד-חד-ערכית** על $[0,\\infty)$ ✓

### צעד 4: אישור בבדיקת קו אופקי
על $[0,\\infty)$ ענף הפרבולה עולה במונוטוניות — כל קו אופקי פוגע לכל היותר פעם אחת.

**מסקנה:** הגבלת תחום לאזור מונוטוני היא התיקון הסטנדרטי לפני הגדרת $f^{-1}(y)=\\sqrt{y}$."""

        elif sid == "checkpoint_1":
            sec["checkpoint_solution_en"] = """**Question:** Is $f(x)=x^3$ injective on $\\mathbb{R}$?

**Step 1:** Set up the injectivity assumption. Suppose $f(a)=f(b)$, so $a^3=b^3$.

**Step 2:** Take cube roots. For real numbers, the cube root is unique: $a^3=b^3 \\Rightarrow a=b$. Unlike squares, odd powers preserve sign and are one-to-one on all of $\\mathbb{R}$.

**Step 3:** Graph check. The graph of $y=x^3$ passes the horizontal line test everywhere — it is strictly increasing, so no horizontal line hits twice.

**Step 4:** Contrast with $x^2$. Odd-degree polynomials like $x^3$ behave differently from even powers; do not assume the parabola pattern applies.

**Answer:** Yes — $f(x)=x^3$ is injective on $\\mathbb{R}$."""
            sec["checkpoint_solution_he"] = """**שאלה:** האם $f(x)=x^3$ חד-חד-ערכית ב-$\\mathbb{R}$?

**שלב 1:** ניחוש חד-חד-ערכיות. נניח $f(a)=f(b)$, כלומר $a^3=b^3$.

**שלב 2:** שורש שלישי. בממשיים השורש השלישי יחיד: $a^3=b^3 \\Rightarrow a=b$. בניגוד לריבוע, חזקות אי-זוגיות שומרות סימן וחד-חד-ערכיות על $\\mathbb{R}$.

**שלב 3:** בדיקת גרף. $y=x^3$ עוברת בדיקת קו אופקי בכל מקום — עולה במונוטוניות, אין קו שפוגע פעמיים.

**שלב 4:** השוואה ל-$x^2$. פולינומים ממעלה אי-זוגית מתנהגים אחרת מחזקות זוגיות; אל תניחו דפוס פרבולה.

**תשובה:** כן — $f(x)=x^3$ חד-חד-ערכית על $\\mathbb{R}$."""

        elif sid == "worked_example_2":
            sec["body_en_md"] = """**Prove** $f(x)=2x+1$ is bijective as a function $\\mathbb{R}\\to\\mathbb{R}$.

Linear functions with nonzero slope are the cleanest bijection examples — both proofs are short algebraic arguments.

### Move 1: Prove injectivity
Suppose $f(a)=f(b)$. Then $2a+1=2b+1$. Subtract 1: $2a=2b$. Divide by 2: $a=b$. **Injective** ✓

### Move 2: Prove surjectivity
Let $y\\in\\mathbb{R}$ be arbitrary (any target in the codomain). We need $x\\in\\mathbb{R}$ with $2x+1=y$. Solve: $x=\\dfrac{y-1}{2}$, which is a real number for every real $y$. **Surjective** ✓

### Move 3: State bijectivity
Since both properties hold, $f$ is **bijective** $\\mathbb{R}\\to\\mathbb{R}$.

### Move 4: Write the inverse explicitly
Solve $y=2x+1$ for $x$: $f^{-1}(y)=\\dfrac{y-1}{2}$. Verify: $f(f^{-1}(y))=2\\cdot\\dfrac{y-1}{2}+1=y$ ✓

**Pattern:** For $f(x)=mx+b$ with $m\\neq 0$, bijectivity on $\\mathbb{R}$ is automatic. Slope zero ($f(x)=b$ constant) fails injectivity unless the domain is a single point."""
            sec["body_he_md"] = """**הוכיחו** ש-$f(x)=2x+1$ היא ביעיה כפונקציה $\\mathbb{R}\\to\\mathbb{R}$.

פונקציות לינאריות עם שיפוע לא-אפס הן דוגמאות הביעיה הפשוטות — שתי ההוכחות קצרות ואלגבריות.

### צעד 1: הוכחת חד-חד-ערכיות
נניח $f(a)=f(b)$. אז $2a+1=2b+1$. חיסור 1: $2a=2b$. חלוקה ב-2: $a=b$. **חד-חד-ערכית** ✓

### צעד 2: הוכחת על-ביות
יהי $y\\in\\mathbb{R}$ כלשהו (כל יעד בקוד-תחום). נדרש $x\\in\\mathbb{R}$ עם $2x+1=y$. פתרון: $x=\\dfrac{y-1}{2}$ — מספר ממשי לכל $y$ ממשי. **על** ✓

### צעד 3: מסקנת ביעיה
מאחר ששתי התכונות מתקיימות, $f$ **ביעיה** $\\mathbb{R}\\to\\mathbb{R}$.

### צעד 4: כתיבת ההופכה במפורש
פתרון $y=2x+1$ עבור $x$: $f^{-1}(y)=\\dfrac{y-1}{2}$. אימות: $f(f^{-1}(y))=y$ ✓

**דפוס:** עבור $f(x)=mx+b$ עם $m\\neq 0$, ביעיה על $\\mathbb{R}$ אוטומטית. שיפוע אפס ($f(x)=b$ קבוע) נכשל בחד-חד-ערכיות אלא אם התחום נקודה בודדת."""

        elif sid == "checkpoint_2":
            sec["checkpoint_solution_en"] = """**Question:** Is $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x)=x^2$, surjective?

**Step 1:** Recall surjectivity means every $y\\in\\mathbb{R}$ must be an output. We need a counterexample: some $y\\in\\mathbb{R}$ with no $x$ satisfying $x^2=y$.

**Step 2:** Observe the range. For every real $x$, $x^2\\ge 0$. So $f(x)$ is never negative.

**Step 3:** Choose $y=-1\\in\\mathbb{R}$. The equation $x^2=-1$ has no real solution. Therefore $y=-1$ is in the codomain but not in the range.

**Step 4:** Note the codomain mismatch. If we had declared $f:\\mathbb{R}\\to[0,\\infty)$ instead, the function **would** be surjective onto its codomain — codomain choice matters.

**Answer:** No — not surjective to $\\mathbb{R}$ because negative values are never outputs."""
            sec["checkpoint_solution_he"] = """**שאלה:** האם $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x)=x^2$, על-ביות?

**שלב 1:** על-ביות = כל $y\\in\\mathbb{R}$ חייב להיות פלט. נדרשת דוגמה נגדית: $y\\in\\mathbb{R}$ שאין $x$ עם $x^2=y$.

**שלב 2:** שימו לב לתמונה. לכל $x$ ממשי, $x^2\\ge 0$. לכן $f(x)$ לעולם לא שלילי.

**שלב 3:** בוחרים $y=-1\\in\\mathbb{R}$. המשוואה $x^2=-1$ אין לה פתרון ממשי. לכן $y=-1$ בקוד-תחום אך לא בתמונה.

**שלב 4:** בחירת קוד-תחום. אם היינו מגדירים $f:\\mathbb{R}\\to[0,\\infty)$ — **כן** הייתה על לקוד-תחום שלה. הבחירה בקוד-תחום קובעת.

**תשובה:** לא — לא על ל-$\\mathbb{R}$ כי ערכים שליליים אינם פלטים."""

        elif sid == "worked_example_3":
            sec["body_en_md"] = """**Construct a bijection** $f:\\mathbb{N}\\to\\mathbb{Z}$ — showing $|\\mathbb{N}|=|\\mathbb{Z}|$ despite one set being "half the integers."

Define:
$$f(n)=\\begin{cases}\\dfrac{n}{2} & \\text{if } n \\text{ even}\\\\-\\dfrac{n-1}{2} & \\text{if } n \\text{ odd}\\end{cases}$$

Mapping: $1\\mapsto 0$, $2\\mapsto 1$, $3\\mapsto -1$, $4\\mapsto 2$, $5\\mapsto -2$, $\\ldots$

### Move 1: Partition the outputs
Even $n$ map to $\\{1,2,3,\\ldots\\}$ (positive integers). Odd $n$ map to $\\{0,-1,-2,\\ldots\\}$ (non-positive integers). The two output sets are disjoint and cover all of $\\mathbb{Z}$.

### Move 2: Injectivity within each branch
On even inputs: $n/2$ is strictly increasing. On odd inputs: $-(n-1)/2$ is strictly decreasing in magnitude. No collision between branches.

### Move 3: Surjectivity — positive $k$
For any $k>0$, take $n=2k$ (even). Then $f(2k)=k$ ✓

### Move 4: Surjectivity — non-positive $k$
For $k=0$: $f(1)=0$. For $k<0$: take $n=1-2k$ (odd). Then $f(1-2k)=-(1-2k-1)/2=-k=|k|$ ✓

**Conclusion:** $f$ is bijective. This "zigzag" pairing is the standard proof that $\\mathbb{N}$ and $\\mathbb{Z}$ have the same cardinality."""
            sec["body_he_md"] = """**בנו ביעיה** $f:\\mathbb{N}\\to\\mathbb{Z}$ — מראה ש-$|\\mathbb{N}|=|\\mathbb{Z}|$ למרות שאחת \"חצי מהשלמים\".

הגדרה:
$$f(n)=\\begin{cases}\\dfrac{n}{2} & n \\text{ זוגי}\\\\-\\dfrac{n-1}{2} & n \\text{ אי-זוגי}\\end{cases}$$

מיפוי: $1\\mapsto 0$, $2\\mapsto 1$, $3\\mapsto -1$, $4\\mapsto 2$, $5\\mapsto -2$, $\\ldots$

### צעד 1: חלוקת הפלטים
$n$ זוגי → $\\{1,2,3,\\ldots\\}$ (שלמים חיוביים). $n$ אי-זוגי → $\\{0,-1,-2,\\ldots\\}$ (לא-חיוביים). שתי קבוצות הפלט נפרדות ומכסות את $\\mathbb{Z}$.

### צעד 2: חד-חד-ערכיות בכל ענף
על קלטים זוגיים: $n/2$ עולה במונוטוניות. על אי-זוגיים: $-(n-1)/2$ יורד בגודל. אין התנגשות בין הענפים.

### צעד 3: על-ביות — $k$ חיובי
לכל $k>0$, $n=2k$ (זוגי). אז $f(2k)=k$ ✓

### צעד 4: על-ביות — $k$ לא-חיובי
ל-$k=0$: $f(1)=0$. ל-$k<0$: $n=1-2k$ (אי-זוגי). אז $f(1-2k)=-k=|k|$ ✓

**מסקנה:** $f$ ביעיה. \"שזירת זיג-זג\" זו ההוכחה הסטנדרטית ש-$\\mathbb{N}$ ו-$\\mathbb{Z}$ באותו עוצמה."""

        elif sid == "method_guide":
            sec["body_en_md"] = """| Claim | Method |
|---|---|
| Prove injective | Assume $f(a)=f(b)$; derive $a=b$ algebraically |
| Disprove injective | Exhibit $a\\neq b$ with $f(a)=f(b)$ |
| Prove surjective | Given $b\\in B$, construct $a\\in A$ with $f(a)=b$ explicitly |
| Disprove surjective | Find $b\\in B$ with no preimage in $A$ |
| Prove bijective | Prove both injective **and** surjective separately |
| Find inverse | Solve $y=f(x)$ for $x$; verify $f(f^{-1}(y))=y$ |

**When to use:** Read the claim first — injectivity, surjectivity, or both — then pick the matching row. For graph problems, use the horizontal line test before algebra.

**Exam tip:** University graders expect **two separate proofs** for bijectivity, not one vague paragraph. Label "Injective:" and "Surjective:" clearly. For inverses, always verify composition both ways."""
            sec["body_he_md"] = """| טענה | שיטה |
|---|---|
| חד-חד-ערכית | ניחוש $f(a)=f(b)$; גזירה $a=b$ |
| לא ח\"ח | מצא $a\\neq b$ עם $f(a)=f(b)$ |
| על | נתון $b$, בנה $a$ עם $f(a)=b$ במפורש |
| לא על | מצא $b$ ללא מקור ב-$A$ |
| ביעיה | הוכח ח\"ח **ו**-על בנפרד |
| הפוכה | פתור $y=f(x)$ ל-$x$; אמת $f(f^{-1}(y))=y$ |

**מתי להשתמש:** קראו את הטענה — ח\"ח, על, או שניהם — ובחרו שורה. בבעיות גרף, בדיקת קו אופקי לפני אלגברה.

**טיפ לבחינה:** בודקים באוניברסיטה מצפים ל**שתי הוכחות נפרדות** לביעיה. סמנו \"חד-חד-ערכית:\" ו-\"על:\" בבירור. להפוכה — אמתו הרכבה בשני הכיוונים."""

        elif sid == "pitfall":
            sec["body_en_md"] = """1. **Domain matters for injectivity.** $f(x)=x^2$ is NOT injective on $\\mathbb{R}$ but IS injective on $[0,\\infty)$. Always state the domain before claiming 1-1.

2. **Codomain matters for surjectivity.** $f(x)=e^x$ is surjective $\\mathbb{R}\\to\\mathbb{R}^+$ but NOT $\\mathbb{R}\\to\\mathbb{R}$ (negative targets unreachable). The same formula changes status with codomain.

3. **Bijective $\\neq$ inverse is obvious.** You must prove both injectivity and surjectivity separately. Writing $f^{-1}$ without proof earns partial credit at best.

4. **Range vs codomain:** $f(A)$ (image/range) can be strictly smaller than $B$. Surjective means range $= B$, not merely range $\\subseteq B$.

5. **Not a function:** A relation assigning two outputs to one input violates the definition — check tables and graphs with the vertical line test first."""
            sec["body_he_md"] = """1. **תחום קובע לחד-חד-ערכיות.** $f(x)=x^2$ **לא** חד-חד-ערכית על $\\mathbb{R}$ אך **כן** על $[0,\\infty)$. תמיד ציינו תחום לפני טענת ח\"ח.

2. **קוד-תחום קובע לעל-ביות.** $f(x)=e^x$ על $\\mathbb{R}\\to\\mathbb{R}^+$ אך **לא** $\\mathbb{R}\\to\\mathbb{R}$ (יעדים שליליים בלתי-נגישים). אותה נוסחה — סטטוס שונה.

3. **ביעיה $\\neq$ הפוכה ברורה.** חייבים להוכיח ח\"ח ועל בנפרד. כתיבת $f^{-1}$ בלי הוכחה — נקודות חלקיות לכל היותר.

4. **תמונה מול קוד-תחום:** $f(A)$ עלולה להיות קטנה מ-$B$. על = תמונה $= B$, לא רק $\\subseteq$.

5. **לא פונקציה:** יחס עם שני פלטים לקלט אחד — בדקו טבלאות וגרפים במבחן הישר האנכי."""

        elif sid == "why_matters":
            sec["body_en_md"] = """Injectivity, surjectivity, and bijectivity are not abstract set-theory trivia — they gate every advanced topic in your calculus and algebra sequence.

**Calculus:** A function must be bijective on an interval to have a differentiable inverse (Inverse Function Theorem). $f(x)=\\sin x$ requires domain restriction to $[-\\pi/2,\\pi/2]$ before $\\arcsin$ is defined.

**Linear algebra:** Invertible matrices correspond to bijective linear transformations. Kernel trivial ($\\{0\\}$) = injective; image equals codomain = surjective.

**Analysis:** Bijections between $\\mathbb{N}$ and $\\mathbb{Z}$ (and later $\\mathbb{Q}$) build cardinality arguments used in real analysis proofs.

On university exams, these definitions appear in proof questions worth 15–20 points — often as the first step before limits or continuity arguments."""
            sec["body_he_md"] = """חד-חד-ערכיות, על-ביות וביעיה אינן טריוויה תורת-קבוצות — הן שער לכל נושא מתקדם בחדו\"א ובאלגברה.

**חדו\"א:** פונקציה חייבת להיות ביעיה על קטע כדי שיהיה לה הופכית גזירה (משפט הפונקציה ההפוכה). $f(x)=\\sin x$ דורשת הגבלה ל-$[-\\pi/2,\\pi/2]$ לפני $\\arcsin$.

**אלגברה לינארית:** מטריצות הפיכות = טרנספורמציות לינאריות בייקטיבית. גרעין טריביאלי = ח\"ח; תמונה = קוד-תחום = על.

**אנליזה:** ביעיות בין $\\mathbb{N}$ ל-$\\mathbb{Z}$ (ואחר כך $\\mathbb{Q}$) בונות арגומנטים של עוצמה בבחינות אנליזה.

בבחינות אוניברסיטה, ההגדרות מופיעות בשאלות הוכחה של 15–20 נקודות — לעיתים כשלב ראשון לפני גבולות או רציפות."""

        elif sid == "before_exam":
            sec["body_en_md"] = """**Quick reference card — injectivity, surjectivity, bijectivity:**

- **Injective (1-1):** $f(a)=f(b)\\Rightarrow a=b$. Disprove with $a\\neq b$, $f(a)=f(b)$. Graph: horizontal line test.
- **Surjective (onto):** $\\forall b\\in B,\\; \\exists a\\in A: f(a)=b$. Disprove with $b\\in B$ having no preimage.
- **Bijective:** both properties. Inverse $f^{-1}:B\\to A$ exists **iff** bijective.
- **Range vs codomain:** $f(A)=\\{f(a):a\\in A\\}$. Surjective $\\Leftrightarrow$ range $= B$.
- **Always write** $f:A\\to B$ — domain and codomain are part of the definition.

**Composition shortcuts:** $g\\circ f$ injective $\\Rightarrow$ $f$ injective. $g\\circ f$ surjective $\\Rightarrow$ $g$ surjective.

**Last review drill:** Prove $f(x)=3x-2$ is bijective $\\mathbb{R}\\to\\mathbb{R}$ from memory in under 3 minutes — injectivity first, then surjective with $x=(y+2)/3$. Say each definition out loud once before the exam."""
            sec["body_he_md"] = """**כרטיס עזר — חד-חד-ערכיות, על-ביות, ביעיה:**

- **חד-חד-ערכית (1-1):** $f(a)=f(b)\\Rightarrow a=b$. הפרכה: $a\\neq b$, $f(a)=f(b)$. גרף: בדיקת קו אופקי.
- **על-ביות:** $\\forall b\\in B,\\; \\exists a\\in A: f(a)=b$. הפרכה: $b\\in B$ ללא מקור.
- **ביעיה:** שתי התכונות. $f^{-1}:B\\to A$ קיימת **אמ\"מ** ביעיה.
- **תמונה מול קוד-תחום:** $f(A)=\\{f(a):a\\in A\\}$. על $\\Leftrightarrow$ תמונה $= B$.
- **תמיד כתבו** $f:A\\to B$ — תחום וקוד-תחום חלק מההגדרה.

**קיצורי דרך בהרכבה:** $g\\circ f$ ח\"ח $\\Rightarrow$ $f$ ח\"ח. $g\\circ f$ על $\\Rightarrow$ $g$ על.

**תרגיל חזרה:** הוכיחו $f(x)=3x-2$ ביעיה $\\mathbb{R}\\to\\mathbb{R}$ מהזיכרון תוך 3 דקות — קודם ח\"ח, אחר כך על עם $x=(y+2)/3$. אמרו כל הגדרה בקול לפני הבחינה."""

        elif sid == "summary":
            sec["body_en_md"] = """- A function assigns exactly one output to each input in its domain.
- **Injective:** distinct inputs → distinct outputs; horizontal line test passes.
- **Surjective:** every codomain element is hit; range equals codomain.
- **Bijective:** perfect pairing; inverse function exists and is unique.
- **Domain restriction** can turn a non-injective function into an injective one (e.g. $x^2$ on $[0,\\infty)$).
- **Composition:** bijections compose to bijections; $g\\circ f$ injective $\\Rightarrow$ $f$ injective.

**Takeaway:** Before any proof, write $f:A\\to B$ explicitly and decide which property — injectivity, surjectivity, or both — the question asks for."""
            sec["body_he_md"] = """- פונקציה משייכת בדיוק פלט אחד לכל קלט בתחום.
- **חד-חד-ערכית:** קלטים שונים → פלטים שונים; בדיקת קו אופקי.
- **על:** כל אלמנט קוד-תחום מושג; תמונה = קוד-תחום.
- **ביעיה:** התאמה מושלמת; הפוכה קיימת ויחידה.
- **הגבלת תחום** יכולה להפוך לא-ח\"ח לח\"ח (למשל $x^2$ על $[0,\\infty)$).
- **הרכבה:** ביעיות מורכבות לביעיה; $g\\circ f$ ח\"ח $\\Rightarrow$ $f$ ח\"ח.

**מסקנה:** לפני כל הוכחה — כתבו $f:A\\to B$ והחליטו איזו תכונה נדרשת."""

    # --- question explanations ---
    expl_data = [
        # q1 MCQ x^2 restriction
        fmt_expl(
            "Both $(-\\infty,0]$ and $[0,\\infty)$ make $x^2$ injective because $x^2$ is strictly decreasing on $(-\\infty,0]$ and strictly increasing on $[0,\\infty)$. On each interval, equal outputs force equal inputs. Option D (both B and C) captures that either half-axis restriction works.",
            "Ask: on which domain is $x^2$ monotone (one-direction)? Parabola branches are monotone on each side of the vertex. $\\mathbb{R}$ fails because $2$ and $-2$ both map to $4$.",
            "Choosing only $[0,\\infty)$ misses that $(-\\infty,0]$ also works — the left branch is one-to-one too. Picking $\\mathbb{R}$ ignores the classic $f(2)=f(-2)$ counterexample.",
            "When a question offers 'both B and C', verify each option independently before selecting the combined answer. Draw the parabola and mark both monotone branches.",
            "גם $(-\\infty,0]$ וגם $[0,\\infty)$ הופכות את $x^2$ לחד-חד-ערכית — $x^2$ יורדת במונוטוניות על $(-\\infty,0]$ ועולה על $[0,\\infty)$. בכל קטע, שוויון פלטים מכריח שוויון קלטים. אפשרות ד (גם ב וגם ג) נכונה.",
            "שאלו: באיזה תחום $x^2$ מונוטונית? ענפי הפרבולה מונוטוניים בכל צד מהקודקוד. $\\mathbb{R}$ נכשל — $2$ ו-$-2$ שניהם $\\mapsto 4$.",
            "בחירה רק ב-$[0,\\infty)$ מפספסת ש-$(-\\infty,0]$ גם עובד. $\\mathbb{R}$ מתעלם מ-$f(2)=f(-2)$.",
            "כשיש 'גם ב וגם ג' — אמתו כל אפשרות בנפרד. שרטטו פרבולה וסמנו שני ענפים מונוטוניים.",
        ),
        # q2 3x-5 injective
        fmt_expl(
            "Yes. Assume $3a-5=3b-5$. Add 5 to both sides: $3a=3b$. Divide by 3: $a=b$. Linear functions $f(x)=mx+b$ with $m\\neq 0$ are always injective on $\\mathbb{R}$ because the equation $ma=mb$ has only the solution $a=b$.",
            "Injectivity proof template: start from $f(a)=f(b)$, simplify using algebra, reach $a=b$. For lines, one subtraction and one division finish the proof.",
            "Saying 'yes because it is a line' without the algebra loses proof marks. Another error: dividing by 3 before adding 5, leaving $a-5/3=b-5/3$ incorrectly.",
            "Any $f(x)=mx+b$, $m\\neq 0$, is bijective $\\mathbb{R}\\to\\mathbb{R}$ — memorize this pattern for quick checks, but still show two lines of algebra on exams.",
            "כן. $3a-5=3b-5 \\Rightarrow 3a=3b \\Rightarrow a=b$. פונקציות $f(x)=mx+b$ עם $m\\neq 0$ תמיד חד-חד-ערכיות על $\\mathbb{R}$ — המקדם $m$ אינו מתאפס, לכן המשוואה $ma=mb$ מכריחה $a=b$.",
            "תבנית הוכחה: $f(a)=f(b)$, פישוט אלגברי, $a=b$. בפונקציות לינאריות — חיסור קבוע וחלוקה במקדם מסיימים את ההוכחה בשורה אחת.",
            "כתיבת 'כן כי זה קו' בלי אלגברה — איבוד נקודות הוכחה. טעות נוספת: חלוקה ב-3 לפני חיבור 5, מה שמשאיר $a-5/3=b-5/3$ שלא מוכיח $a=b$.",
            "כל $f(x)=mx+b$ עם $m\\neq 0$ היא ביעיה על $\\mathbb{R}$ — זכרו לבדיקה מהירה, אך בבחינה הראו לפחות שתי שורות אלגברה עם סימון 'חד-חד-ערכית'.",
        ),
        # q3 sqrt domain surjective to R
        fmt_expl(
            "Domain is $[0,\\infty)$ because $\\sqrt{x}$ requires $x\\ge 0$. The range is also $[0,\\infty)$ — square root never outputs a negative number. Since $[0,\\infty)\\neq\\mathbb{R}$, the function is **not** surjective to $\\mathbb{R}$: e.g. $y=-1$ has no preimage.",
            "Separate two questions: (1) domain = allowed inputs; (2) surjectivity to $\\mathbb{R}$ = can every real number be an output? Non-negative outputs cannot cover negative targets.",
            "Answering 'yes surjective' by confusing codomain $\\mathbb{R}$ with range $[0,\\infty)$. Another slip: domain $(-\\infty,\\infty)$ ignoring the root restriction.",
            "Always compute range before deciding surjectivity. If the question says '$\\to\\mathbb{R}$' but range excludes negatives, answer 'not surjective' with a specific counterexample like $y=-1$.",
            "תחום $[0,\\infty)$ כי $\\sqrt{x}$ דורש $x\\ge 0$. תמונה (range) היא $[0,\\infty)$ — שורש ריבועי לעולם לא מוציא מספר שלילי. מאחר ש-$[0,\\infty)\\neq\\mathbb{R}$, הפונקציה **לא** על-ביות ל-$\\mathbb{R}$: למשל $y=-1$ אין לו מקור.",
            "הפרידו שני חלקים: (1) תחום = קלטים מותרים; (2) על-ביות ל-$\\mathbb{R}$ = האם כל מספר ממשי הוא פלט? פלטים לא-שליליים לא יכולים לכסות יעדים שליליים בקוד-תחום.",
            "תשובת 'כן על' מבלבלת בין קוד-תחום $\\mathbb{R}$ לבין תמונה $[0,\\infty)$. טעות נוספת: כתיבת תחום $(-\\infty,\\infty)$ בלי לשים לב להגבלת השורש.",
            "תמיד חשבו תמונה לפני החלטה על על-ביות. אם השאלה אומרת '$\\to\\mathbb{R}$' אך התמונה מוציאה רק לא-שליליים — ענו 'לא על' עם דוגמה נגדית ספציפית כמו $y=-1$.",
        ),
        # q4 finite set bijection
        fmt_expl(
            "Yes — bijective. The map sends 1→a, 2→b, 3→c. Each input has a distinct output (injective), and every element of {a,b,c} is hit (surjective). With equal-size finite sets, one property often implies the other, but state both on exams.",
            "For small finite sets, draw arrow diagrams. Injective = no two arrows share a target from different sources. Surjective = every target has an incoming arrow.",
            "Saying 'yes' without checking that all three targets are distinct. If f(2)=f(1), it fails injectivity even if all targets are covered.",
            "Equal domain and codomain sizes: if injective, automatically surjective (and vice versa). Still verify explicitly — exam rubrics reward labeled checks.",
            "כן — ביעיה. 1→a, 2→b, 3→c. קלטים שונים → פלטים שונים (ח\"ח); כל {a,b,c} מושג (על). בקבוצות סופיות שוות גודל, תכונה אחת לעיתים מרמזת על השנייה.",
            "בקבוצות קטנות — דיאגרמת חצים. ח\"ח = אין שני חצים לאותו מקור. על = לכל יעד יש חץ נכנס.",
            "'כן' בלי לבדוק שלושה יעדים שונים. אם f(2)=f(1) — לא ח\"ח.",
            "גודל שווה: ח\"ח $\\Rightarrow$ על. עדיין אמתו במפורש — בודקים נותנים נקודות על סימון.",
        ),
        # q5 |x| not injective
        fmt_expl(
            "No. $f(1)=|1|=1$ and $f(-1)=|-1|=1$, but $1\\neq -1$. Two distinct inputs share the same output, violating injectivity. The horizontal line $y=1$ hits the V-graph twice.",
            "Absolute value reflects negative inputs to positive outputs — classic symmetry breaking injectivity on all of $\\mathbb{R}$. Restrict to $[0,\\infty)$ if you need injectivity.",
            "Answering 'yes' because $|x|$ is a function (it is!) — injectivity is a separate question. Confusing 'function' with 'one-to-one'.",
            "For $|x|$, always test $x=1$ and $x=-1$ first — fastest counterexample on any exam. Mention the horizontal line test for graph credit.",
            "לא. $f(1)=|1|=1$ ו-$f(-1)=|-1|=1$, אך $1\\neq -1$. שני קלטים שונים חולקים אותו פלט — זו הפרכה ישירה לחד-חד-ערכיות. הקו האופקי $y=1$ חותך את גרף ה-V פעמיים.",
            "ערך מוחלט משקף קלטים שליליים לפלטים חיוביים — סימטריה קלאסית ששוברת חד-חד-ערכיות על כל $\\mathbb{R}$. הגבילו ל-$[0,\\infty)$ אם נדרשת ח\"ח.",
            "תשובת 'כן' כי $|x|$ היא פונקציה (נכון!) — אך ח\"ח שאלה נפרדת. בלבול בין 'פונקציה' ל'חד-חד-ערכית' הוא מלכודת נפוצה.",
            "ב-$|x|$, בדקו תמיד $x=1$ ו-$x=-1$ קודם — דוגמה נגדית מהירה ביותר בכל בחינה. ציינו בדיקת קו אופקי לקבלת נקודות על חלק גרפי.",
        ),
        # q6 x^3+1 bijective
        fmt_expl(
            "Injective: $a^3+1=b^3+1 \\Rightarrow a^3=b^3 \\Rightarrow a=b$ (cube root unique on $\\mathbb{R}$). Surjective: given $y\\in\\mathbb{R}$, solve $y=x^3+1$ to get $x=(y-1)^{1/3}\\in\\mathbb{R}$. Both hold, so bijective with inverse $f^{-1}(y)=(y-1)^{1/3}$.",
            "Bijection = two proofs. Odd-degree polynomials like $x^3+1$ are typically bijective $\\mathbb{R}\\to\\mathbb{R}$ because they are strictly increasing. Verify surjectivity by explicit preimage construction.",
            "Proving only injectivity and stopping. Or writing inverse without showing surjectivity. Some students claim $x^3+1$ fails surjectivity — it does not on $\\mathbb{R}$.",
            "Template for 'prove bijective': label Injective and Surjective sections. For cubics, cite strict monotonicity as a shortcut after establishing $f'(x)=3x^2\\ge 0$ with equality only at 0.",
            "ח\"ח: $a^3+1=b^3+1 \\Rightarrow a^3=b^3 \\Rightarrow a=b$ (שורש שלישי יחיד בממשיים). על: לכל $y\\in\\mathbb{R}$, $x=(y-1)^{1/3}\\in\\mathbb{R}$. שתי התכונות מתקיימות — ביעיה, עם $f^{-1}(y)=(y-1)^{1/3}$.",
            "ביעיה = שתי הוכחות נפרדות. פולינומים ממעלה אי-זוגית כמו $x^3+1$ בדרך כלל ביעיים על $\\mathbb{R}$ כי הם עולים במונוטוניות. על-ביות = בניית מקור במפורש.",
            "הוכחת ח\"ח בלבד והפסקה — איבוד נקודות. כתיבת הפוכה בלי הוכחת על. חלק טוענים ש-$x^3+1$ לא על — שגוי על $\\mathbb{R}$.",
            "תבנית 'הוכח ביעיה': סמנו 'חד-חד-ערכית:' ו-'על:'. במעגלות — מונוטוניות מ-$f'(x)=3x^2\\ge 0$ (שוויון רק ב-0) כקיצור.",
        ),
        # q7 sin x range
        fmt_expl(
            "The range (image) of $f(x)=\\sin x$ on $\\mathbb{R}$ is $[-1,1]$. Sine oscillates between $-1$ and $1$ and attains every value in between by continuity (Intermediate Value Theorem on each period). It never exceeds 1 or goes below $-1$.",
            "Range question = 'what outputs are possible?' not 'what is the domain?' Sine is defined on all $\\mathbb{R}$ but outputs only in $[-1,1]$. So it is NOT surjective to $\\mathbb{R}$.",
            "Writing $\\mathbb{R}$ as the range. Or $[0,1]$ forgetting negative values. Some confuse range with period $2\\pi$.",
            "Memorize: $\\sin x, \\cos x$ have range $[-1,1]$; $e^x$ has range $(0,\\infty)$; $x^2$ has range $[0,\\infty)$ on $\\mathbb{R}$. These four appear on every calculus midterm.",
            "תמונת $f(x)=\\sin x$ על $\\mathbb{R}$ היא $[-1,1]$. הסינוס מתנדנד בין $-1$ ל-$1$ ומגיע לכל ערך ביניהם (רציפות + IVT על כל מחזור). הוא לעולם לא חורג מגבולות אלה.",
            "שאלת תמונה = 'אילו פלטים אפשריים?' — לא 'מה התחום?'. סינוס מוגדר על כל $\\mathbb{R}$ אך מוציא רק ב-$[-1,1]$. לכן **לא** על-ביות ל-$\\mathbb{R}$.",
            "כתיבת $\\mathbb{R}$ כתמונה — טעות. או $[0,1]$ בלי ערכים שליליים. חלק מבלבלים תמונה עם מחזור $2\\pi$.",
            "שיננו: $\\sin x,\\cos x$ → $[-1,1]$; $e^x$ → $(0,\\infty)$; $x^2$ על $\\mathbb{R}$ → $[0,\\infty)$. ארבעת אלה בכל מבחן חדו\"א.",
        ),
        # q8 e^x surjective to R+
        fmt_expl(
            "Yes. The codomain is $\\mathbb{R}^+=(0,\\infty)$, not all of $\\mathbb{R}$. For every $y>0$, choose $x=\\ln y$. Then $e^x=e^{\\ln y}=y$. Every positive target has a real preimage — $f$ is surjective onto its declared codomain.",
            "Read the codomain in the function declaration $f:\\mathbb{R}\\to\\mathbb{R}^+$. Surjectivity is relative to **that** $B$, not to all reals. Exponential outputs are always positive.",
            "Answering 'no' because $e^x$ never equals $-5$ — true, but $-5\\notin\\mathbb{R}^+$. The codomain excludes negatives by design. Do not change the codomain mid-problem.",
            "Pair $e^x$ with $\\ln x$: domain $(0,\\infty)$, range $\\mathbb{R}$ — inverse pair. Writing $x=\\ln y$ shows you understand log as inverse exponential.",
            "כן. קוד-תחום $\\mathbb{R}^+=(0,\\infty)$, לא כל $\\mathbb{R}$. לכל $y>0$, $x=\\ln y\\in\\mathbb{R}$ ו-$e^x=e^{\\ln y}=y$. כל יעד חיובי בקוד-תחום מקבל מקור ממשי — $f$ על-ביות לקוד-תחום המוצהר.",
            "קראו את הקוד-תחום בהגדרה $f:\\mathbb{R}\\to\\mathbb{R}^+$. על-ביות יחסית ל-$B$ **הזה**, לא לכל הממשיים. פלטי מעריך תמיד חיוביים.",
            "תשובת 'לא' כי $e^x$ לא שווה $-5$ — נכון, אך $-5\\notin\\mathbb{R}^+$. הקוד-תחום מוציא שליליים בכוונה. אל תשנו קוד-תחום באמצע השאלה.",
            "זוג $e^x$ ו-$\\ln x$: תחום $(0,\\infty)$, תמונה $\\mathbb{R}$ — זוג הפיכות. כתיבת $x=\\ln y$ מראה שהבנתם לוג כהופכית של מעריך.",
        ),
    ]

    for i, q in enumerate(data["questions"]):
        if i < len(expl_data):
            q["explanation_en"], q["explanation_he"] = expl_data[i]

    # --- validate ---
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in MIN:
            en_min, he_min = MIN[kind]
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"{sec.get('id', kind)} EN: {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{sec.get('id', kind)} HE: {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{sec.get('id', kind)}: weak Hebrew")
        if kind == "worked_example":
            en_min, he_min = MIN["worked_example"]
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"{sec.get('id', kind)} EN: {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{sec.get('id', kind)} HE: {he_w} < {he_min}")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"q{q.get('ord')} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)

    with open(TARGET, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote", TARGET)
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr)
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    print("seed-lessons dry-run OK")


if __name__ == "__main__":
    main()
