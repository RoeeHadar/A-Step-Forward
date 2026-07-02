#!/usr/bin/env python3
"""Expand factoring.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/factoring.json"

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


SECTION_BODIES = {
    "intro": {
        "body_en_md": """**Factoring** is the reverse of expanding: you rewrite a polynomial as a **product** of simpler factors. If expanding distributes a product across a sum, factoring collects common structure back into parentheses. That skill is not a side topic — it is the engine behind solving quadratic equations, simplifying rational expressions, finding function zeros, and clearing denominators before calculus.

**Why factor in practice:**
- **Solve equations:** $x^2-5x+6=0$ becomes $(x-2)(x-3)=0$, so $x=2$ or $x=3$ by the zero-product property.
- **Simplify fractions:** $\\dfrac{x^2-4}{x-2}=\\dfrac{(x-2)(x+2)}{x-2}=x+2$ for $x\\ne2$.
- **Find zeros:** A factored form shows every $x$-value that makes the expression zero at a glance.
- **Analyze graphs:** Multiplicity of linear factors tells you whether the graph crosses or touches the axis.

In Israeli Bagrut (3–4 units), factoring appears inside quadratic equations, rational-function simplification, and word problems that reduce to polynomials. Exam items reward a **systematic order** (GCF first, then pattern recognition) and **complete** factoring — stopping at $(x^2-4)$ when $(x-2)(x+2)$ is possible costs points.""",
        "body_he_md": """**פירוק לגורמים** הוא ההפך של פתיחת סוגריים: כותבים פולינום כ**מכפלה** של גורמים פשוטים יותר. אם פתיחה מפזרת מכפלה על סכום, פירוק אוסף מבנה משותף חזרה לתוך סוגריים. זו לא נושא צד — זה המנוע מאחורי פתרון משוואות ריבועיות, פישוט ביטויים רציונליים, מציאת שורשים של פונקציות וניקוי מכנים לפני חדו"א.

**למה לפרק בפועל:**
- **פתרון משוואות:** $x^2-5x+6=0$ הופך ל-$(x-2)(x-3)=0$, ולכן $x=2$ או $x=3$ לפי תכונת אפס-מכפלה.
- **פישוט שברים:** $\\dfrac{x^2-4}{x-2}=\\dfrac{(x-2)(x+2)}{x-2}=x+2$ עבור $x\\ne2$.
- **מציאת אפסים:** צורה מפורקת מראה מיד כל $x$ שהופך את הביטוי לאפס.
- **ניתוח גרפים:** ריבוי של גורמים לינאריים קובע אם הגרף חוצה או נוגע בציר.

בבגרות (3–4 יחידות), פירוק מופיע בתוך משוואות ריבועיות, פישוט פונקציות רציונליות ובעיות מילוליות שמצטמצמות לפולינומים. בבחינה מעריכים **סדר שיטתי** (גורם משותף קודם, ואז זיהוי דפוס) ופירוק **מלא** — לעצור ב-$(x^2-4)$ כשאפשר $(x-2)(x+2)$ עולה בניקוד.""",
    },
    "definition": {
        "body_en_md": """Factoring means writing an expression as a product of irreducible (over the reals) factors. The toolkit below covers every pattern on the Bagrut algebra track:

**1. Greatest Common Factor (GCF):** Pull out the largest shared numerical and variable factor.
$$6x^3+9x^2=3x^2(2x+3).$$
Always do this first — it often reveals a hidden pattern underneath.

**2. Difference of squares:** $a^2-b^2=(a-b)(a+b)$.
Example: $x^2-16=(x-4)(x+4)$. **Sum** of squares $a^2+b^2$ does **not** factor over $\\mathbb{R}$.

**3. Perfect square trinomials:**
$$a^2+2ab+b^2=(a+b)^2, \\quad a^2-2ab+b^2=(a-b)^2.$$
Check: middle term is exactly twice the product of square roots.

**4. Trinomial $x^2+bx+c$:** Find integers $p,q$ with $pq=c$ and $p+q=b$.
$$x^2+5x+6=(x+2)(x+3) \\quad (2\\times3=6,\\ 2+3=5).$$

**5. Trinomial $ax^2+bx+c$ ($a\\ne1$):** Use the **$ac$ method** (split middle term, then group) or trial factors of $a$ and $c$.

**6. Grouping (four or more terms):** Pair terms and factor each pair.
$$xy+xz+y^2+yz = x(y+z)+y(y+z)=(x+y)(y+z).$$

**7. Sum/difference of cubes:**
$$a^3-b^3=(a-b)(a^2+ab+b^2), \\quad a^3+b^3=(a+b)(a^2-ab+b^2).$$""",
        "body_he_md": """פירוק פירושו כתיבת ביטוי כמכפלה של גורמים שאינם ניתנים לפירוק נוסף (על הממשיים). ערכת הכלים הבאה מכסה כל דפוס במסלול האלגברה בבגרות:

**1. גורם משותף מקסימלי (GCF):** מוציאים את הגורם המספרי והמשתנה המשותף הגדול ביותר.
$$6x^3+9x^2=3x^2(2x+3).$$
תמיד עושים זאת ראשון — לעיתים נחשף דפוס מוסתר מתחת.

**2. הפרש ריבועים:** $a^2-b^2=(a-b)(a+b)$.
דוגמה: $x^2-16=(x-4)(x+4)$. **סכום** ריבועים $a^2+b^2$ **לא** מתפרק על $\\mathbb{R}$.

**3. חוליית ריבוע מושלם:**
$$a^2+2ab+b^2=(a+b)^2, \\quad a^2-2ab+b^2=(a-b)^2.$$
בדיקה: האיבר האמצעי שווה בדיוק לפי שני מכפלת שורשי הריבועים.

**4. חוליה $x^2+bx+c$:** מוצאים שלמים $p,q$ כך ש-$pq=c$ ו-$p+q=b$.
$$x^2+5x+6=(x+2)(x+3) \\quad (2\\times3=6,\\ 2+3=5).$$

**5. חוליה $ax^2+bx+c$ ($a\\ne1$):** שיטת **$ac$** (פיצול האיבר האמצעי ואז קיבוץ) או ניסוי גורמים של $a$ ו-$c$.

**6. קיבוץ (ארבעה איברים ומעלה):** מקבצים זוגות ומוציאים גורם מכל זוג.
$$xy+xz+y^2+yz = x(y+z)+y(y+z)=(x+y)(y+z).$$

**7. סכום/הפרש קוביות:**
$$a^3-b^3=(a-b)(a^2+ab+b^2), \\quad a^3+b^3=(a+b)(a^2-ab+b^2).$$""",
    },
    "theory": {
        "body_en_md": """Use the same **decision tree** on every problem — exam speed comes from recognizing structure, not guessing formulas.

**Step 1 — GCF always first.** Factor out negatives if it makes the remaining leading coefficient positive. Example: $-2x^2+8=-2(x^2-4)$.

**Step 2 — Count terms after GCF:**
| Terms | Try first |
|---|---|
| 2 | Difference of squares $a^2-b^2$; sum/difference of cubes $a^3\\pm b^3$ |
| 3 | Perfect square $(a\\pm b)^2$; trinomial $x^2+bx+c$ or $ax^2+bx+c$ |
| 4+ | Grouping in pairs |

**Step 3 — Factor each piece completely.** After $(x^2-4)$, ask: is $x^2-4$ itself a difference of squares? Stop only when every factor is prime over the reals.

**Step 4 — Verify by expanding.** One quick FOIL or distributive check catches sign errors before you submit.

**The $ac$ method for $ax^2+bx+c$ ($a\\ne1$):**
1. Compute $ac$.
2. Find integers $p,q$ with $pq=ac$ and $p+q=b$.
3. Rewrite $bx=px+qx$ and group: $(ax^2+px)+(qx+c)$.
4. Factor each group; the binomial in parentheses should match.

**Sign discipline in trinomials:** For $x^2-7x+12$, both $p,q$ are negative because $c>0$ and $b<0$. For $x^2+x-12$, one factor is positive and one negative because $c<0$.

**Link to equations:** Once factored, set each factor equal to zero. Incomplete factoring means you lose roots — a common Bagrut deduction.""",
        "body_he_md": """השתמשו באותו **עץ החלטות** בכל בעיה — מהירות בבחינה מגיעה מזיהוי מבנה, לא מניחוש נוסחאות.

**שלב 1 — גורם משותף תמיד ראשון.** הוציאו מינוס אם זה הופך את המקדם המוביל לחיובי. דוגמה: $-2x^2+8=-2(x^2-4)$.

**שלב 2 — ספרו איברים אחרי GCF:**
| איברים | נסו קודם |
|---|---|
| 2 | הפרש ריבועים $a^2-b^2$; סכום/הפרש קוביות $a^3\\pm b^3$ |
| 3 | ריבוע מושלם $(a\\pm b)^2$; חוליה $x^2+bx+c$ או $ax^2+bx+c$ |
| 4+ | קיבוץ בזוגות |

**שלב 3 — פרקו כל חלק עד הסוף.** אחרי $(x^2-4)$, שאלו: האם $x^2-4$ עצמו הפרש ריבועים? עצרו רק כשכל גורם ראשי על הממשיים.

**שלב 4 — אימות בפתיחה.** בדיקת FOIL או פיזור מהירה תופסת טעויות סימן לפני הגשה.

**שיטת $ac$ עבור $ax^2+bx+c$ ($a\\ne1$):**
1. חשבו $ac$.
2. מצאו שלמים $p,q$ כך ש-$pq=ac$ ו-$p+q=b$.
3. כתבו $bx=px+qx$ וקבצו: $(ax^2+px)+(qx+c)$.
4. הוציאו גורם מכל קבוצה; הביטוי בסוגריים צריך להתאים.

**משמעת סימנים בחוליות:** ב-$x^2-7x+12$, שני $p,q$ שליליים כי $c>0$ ו-$b<0$. ב-$x^2+x-12$, גורם אחד חיובי ואחד שלילי כי $c<0$.

**קשר למשוואות:** אחרי פירוק, שוו כל גורם לאפס. פירוק חלקי = איבוד שורשים — ניכוי שכיח בבגרות.""",
    },
}

WE1_EN = """**Factor** $3x^3-12x$ completely.

This is a classic two-step item: GCF first, then difference of squares inside the parentheses. Skipping GCF leaves a harder trinomial path that does not exist here.

### Move 1: Extract the GCF
Both terms share $3x$: $3x^3-12x=3x(x^2-4)$. The GCF includes the **lowest** power of $x$ common to both terms ($x^1$) and the largest numerical divisor ($3$).

### Move 2: Difference of squares inside
$x^2-4=(x-2)(x+2)$ because $4=2^2$. Recognize $a=x$, $b=2$ in $a^2-b^2$.

### Move 3: Write the complete product
**Result:** $3x(x-2)(x+2)$.

### Move 4: Verify by expanding
$3x(x-2)(x+2)=3x(x^2-4)=3x^3-12x$ ✓.

**Why order matters:** If you tried to factor $x^2-4$ before pulling out $3x$, you would still succeed — but on $6x^3-24x$, missing the GCF of $6x$ first makes the numbers unnecessarily large and invites arithmetic slips.

**Bagrut link:** This exact pattern — GCF then difference of squares — appears inside rational simplification items where you must cancel **common factors** only after full factoring."""

WE1_HE = """**פרקו** $3x^3-12x$ לגמרי.

זו דוגמה דו-שלבית קלאסית: גורם משותף קודם, ואז הפרש ריבועים בתוך הסוגריים. דילוג על GCF מוביל למסלול חוליה שלא קיים כאן.

### צעד 1: הוצאת GCF
לשני האיברים משותף $3x$: $3x^3-12x=3x(x^2-4)$. GCF כולל את **החזקה הנמוכה** של $x$ ($x^1$) ואת המחלק המספרי הגדול ביותר ($3$).

### צעד 2: הפרש ריבועים בפנים
$x^2-4=(x-2)(x+2)$ כי $4=2^2$. מזהים $a=x$, $b=2$ ב-$a^2-b^2$.

### צעד 3: כתיבת המכפלה המלאה
**תוצאה:** $3x(x-2)(x+2)$.

### צעד 4: אימות בפתיחה
$3x(x-2)(x+2)=3x(x^2-4)=3x^3-12x$ ✓.

**למה הסדר חשוב:** גם אם מפרקים $x^2-4$ לפני $3x$, עדיין מצליחים — אבל ב-$6x^3-24x$, דילוג על GCF של $6x$ מנפח מספרים ומזמין טעויות חישוב.

**קשר לבגרות:** אותו דפוס — GCF ואז הפרש ריבועים — מופיע בפישוט ביטויים רציונליים, שם מצמצמים **גורמים משותפים** רק אחרי פירוק מלא."""

WE2_EN = """**Factor** $6x^2+11x-10$ using the $ac$ method.

Leading coefficient $a=6\\ne1$, so the "two numbers that multiply to $c$" shortcut applies to $ac$, not $c$ alone.

### Move 1: Compute $ac$
$ac=6\\times(-10)=-60$. Need integers $p,q$ with $pq=-60$ and $p+q=11$.

### Move 2: Find $p$ and $q$
Try factor pairs of $60$: $15$ and $-4$ work because $15+(-4)=11$ and $15\\times(-4)=-60$ ✓. List pairs systematically: $(1,-60)$, $(2,-30)$, $(3,-20)$, $(4,-15)$, $(5,-12)$, $(6,-10)$ — stop when sum equals $11$.

### Move 3: Split the middle term
$6x^2+11x-10=6x^2+15x-4x-10$.

### Move 4: Group and factor
$3x(2x+5)-2(2x+5)=(3x-2)(2x+5)$.

### Move 5: Verify
$(3x-2)(2x+5)=6x^2+15x-4x-10=6x^2+11x-10$ ✓.

**Exam note:** If grouping fails (binomials do not match), your $p,q$ pair is wrong — re-list factor pairs of $|ac|$ before changing method.

**Alternative check:** Substitute $x=1$ into original and factored forms — both should give $7$. Quick numeric sanity checks catch sign swaps under time pressure."""

WE2_HE = """**פרקו** $6x^2+11x-10$ בשיטת $ac$.

מקדם מוביל $a=6\\ne1$, ולכן קיצור "שני מספרים שמכפלתם $c$" חל על $ac$, לא על $c$ בלבד.

### צעד 1: חישוב $ac$
$ac=6\\times(-10)=-60$. צריך שלמים $p,q$ עם $pq=-60$ ו-$p+q=11$.

### צעד 2: מציאת $p$ ו-$q$
זוגות גורמים של $60$: $15$ ו-$-4$ מתאימים כי $15+(-4)=11$ ו-$15\\times(-4)=-60$ ✓. רשימו זוגות שיטתית: $(1,-60)$, $(2,-30)$, $(3,-20)$, $(4,-15)$, $(5,-12)$, $(6,-10)$ — עצרו כשהסכום $11$.

### צעד 3: פיצול האיבר האמצעי
$6x^2+11x-10=6x^2+15x-4x-10$.

### צעד 4: קיבוץ והוצאת גורם
$3x(2x+5)-2(2x+5)=(3x-2)(2x+5)$.

### צעד 5: אימות
$(3x-2)(2x+5)=6x^2+15x-4x-10=6x^2+11x-10$ ✓.

**הערת בחינה:** אם הקיבוץ נכשל (הביטויים בסוגריים לא תואמים), זוג $p,q$ שגוי — חזרו לרשימת גורמי $|ac|$ לפני החלפת שיטה.

**בדיקה חלופית:** הציבו $x=1$ בביטוי המקורי ובמפורק — שניהם צריכים לתת $7$. בדיקה מספרית מהירה תופסת החלפות סימן תחת לחץ."""

WE3_EN = """**Factor** $x^3-8$ and recognize when to stop.

Two-term expressions after GCF often hide difference/sum of cubes — not just difference of squares.

### Move 1: Identify the pattern
$8=2^3$, so $x^3-8=a^3-b^3$ with $a=x$, $b=2$.

### Move 2: Apply the cube formula
$$a^3-b^3=(a-b)(a^2+ab+b^2) \\Rightarrow x^3-8=(x-2)(x^2+2x+4).$$

### Move 3: Verify
$(x-2)(x^2+2x+4)=x^3+2x^2+4x-2x^2-4x-8=x^3-8$ ✓.

### Move 4: Can we factor further?
$x^2+2x+4$ has discriminant $4-16=-12<0$ — **no real factors**. Stop here for Bagrut reals. The quadratic factor is irreducible; do not attempt difference of squares on it.

**Bonus — $8x^3+27$:** $a=2x$, $b=3$ gives $(2x+3)(4x^2-6x+9)$. The quadratic factor is again irreducible over $\\mathbb{R}$.

**Strategy:** Cubes appear when the constant is a perfect cube ($1,8,27,64,\\ldots$) and powers are multiples of $3$.

**Exam context:** Difference-of-cubes items often follow a GCF step — e.g. $2x^3-54=2(x^3-27)$ — so always scan for a numerical factor before declaring "two terms, use cubes."""

WE3_HE = """**פרקו** $x^3-8$ ודעו מתי לעצור.

ביטויים דו-איבריים אחרי GCF לעיתים מסתירים הפרש/סכום קוביות — לא רק הפרש ריבועים.

### צעד 1: זיהוי הדפוס
$8=2^3$, ולכן $x^3-8=a^3-b^3$ עם $a=x$, $b=2$.

### צעד 2: יישום נוסחת הקוביה
$$a^3-b^3=(a-b)(a^2+ab+b^2) \\Rightarrow x^3-8=(x-2)(x^2+2x+4).$$

### צעד 3: אימות
$(x-2)(x^2+2x+4)=x^3+2x^2+4x-2x^2-4x-8=x^3-8$ ✓.

### צעד 4: האם ניתן לפרק עוד?
ל-$x^2+2x+4$ דיסקרiminant $4-16=-12<0$ — **אין גורמים ממשיים**. עוצרים כאן בבגרות על הממשיים. הגורם הריבועי לא מתפרק; אל תנסו הפרש ריבועים עליו.

**בונוס — $8x^3+27$:** $a=2x$, $b=3$ נותן $(2x+3)(4x^2-6x+9)$. הגורם הריבועי שוב לא מתפרק על $\\mathbb{R}$.

**אסטרטגיה:** קוביות מופיעות כשקבוע הוא קוביה מושלמת ($1,8,27,64,\\ldots$) והחזקות כפולות של $3$.

**הקשר לבחינה:** פריטי הפרש קוביות לעיתים באים אחרי GCF — למשל $2x^3-54=2(x^3-27)$ — ולכן תמיד סרקו גורם מספרי לפני "שני איברים, קוביות"."""

CHK1_EN = """Trinomial $x^2-7x+12$ with positive constant and negative middle term → both factors are negative.

**Step 1:** Need $p,q$ with $pq=12$ and $p+q=-7$.

**Step 2:** Factor pairs of $12$: $(-3,-4)$ works because $(-3)+(-4)=-7$ and $(-3)(-4)=12$ ✓.

**Step 3:** Write factors $(x-3)(x-4)$.

**Step 4:** Verify: $(x-3)(x-4)=x^2-7x+12$ ✓. **Answer:** $(x-3)(x-4)$."""

CHK1_HE = """חוליה $x^2-7x+12$ עם קבוע חיובי ואיבר אמצעי שלילי → שני הגורמים שליליים.

**שלב 1:** צריך $p,q$ עם $pq=12$ ו-$p+q=-7$.

**שלב 2:** זוגות גורמים של $12$: $(-3,-4)$ מתאים כי $(-3)+(-4)=-7$ ו-$(-3)(-4)=12$ ✓.

**שלב 3:** כותבים $(x-3)(x-4)$.

**שלב 4:** אימות: $(x-3)(x-4)=x^2-7x+12$ ✓. **תשובה:** $(x-3)(x-4)$."""

CHK2_EN = """Equation $x^2+x-12=0$ — factor, then zero-product property.

**Step 1:** Find $p,q$ with $pq=-12$ and $p+q=1$. Pair $(4,-3)$ works: $4+(-3)=1$, $4\\times(-3)=-12$.

**Step 2:** Factor: $(x+4)(x-3)=0$.

**Step 3:** Set each factor to zero: $x+4=0$ gives $x=-4$; $x-3=0$ gives $x=3$.

**Check:** $(-4)^2+(-4)-12=0$ and $3^2+3-12=0$ ✓. **Answer:** $x=-4$ or $x=3$."""

CHK2_HE = """משוואה $x^2+x-12=0$ — פירוק, ואז תכונת אפס-מכפלה.

**שלב 1:** מוצאים $p,q$ עם $pq=-12$ ו-$p+q=1$. הזוג $(4,-3)$ מתאים: $4+(-3)=1$, $4\\times(-3)=-12$.

**שלב 2:** פירוק: $(x+4)(x-3)=0$.

**שלב 3:** שוו כל גורם לאפס: $x+4=0$ נותן $x=-4$; $x-3=0$ נותן $x=3$.

**בדיקה:** $(-4)^2+(-4)-12=0$ ו-$3^2+3-12=0$ ✓. **תשובה:** $x=-4$ או $x=3$."""

METHOD_EN = """| Step | Question to ask |
|---|---|
| 1 | Is there a GCF (including a leading minus)? |
| 2 | How many terms remain? |
| 2a (two terms) | $a^2-b^2$? $a^3\\pm b^3$? |
| 2b (three terms) | Perfect square? $x^2+bx+c$? $ax^2+bx+c$? |
| 2c (four+) | Can I group into two pairs with a common binomial? |
| 3 | Does any factor factor further? |
| 4 | Expand to verify |

**When to use:** Read the expression shape **before** plugging numbers. On Bagrut items, write "GCF" as your first line even when you think there is none — that habit prevents half-factored answers.

**Exam tip:** For $x^4-1$, difference of squares applies twice: $(x^2-1)(x^2+1)=(x-1)(x+1)(x^2+1)$. The last factor is irreducible over $\\mathbb{R}$."""

METHOD_HE = """| שלב | שאלה לשאול |
|---|---|
| 1 | האם יש GCF (כולל מינוס מוביל)? |
| 2 | כמה איברים נשארו? |
| 2א (שני איברים) | $a^2-b^2$? $a^3\\pm b^3$? |
| 2ב (שלושה) | ריבוע מושלם? $x^2+bx+c$? $ax^2+bx+c$? |
| 2ג (ארבעה+) | האם ניתן לקבץ לשני זוגות עם ביטוי משותף? |
| 3 | האם גורם כלשהו מתפרק עוד? |
| 4 | פתיחה לאימות |

**מתי להשתמש:** קראו את **צורת** הביטוי לפני הצבת מספרים. בבגרות, כתבו "GCF" כשורה ראשונה גם כשחושבים שאין — הרגל זה מונע תשובות מפורקות חלקית.

**טיפ לבחינה:** ב-$x^4-1$, הפרש ריבועים פעמיים: $(x^2-1)(x^2+1)=(x-1)(x+1)(x^2+1)$. הגורם האחרון לא מתפרק על $\\mathbb{R}$."""

PITFALL_EN = """1. **Skipping GCF.** On $6x^3-3x^2-9x$, factoring the trinomial first wastes time. Pull $3x$ first: $3x(2x^2-x-3)$.

2. **Incomplete factoring.** $(x^2-4)$ is not finished — write $(x-2)(x+2)$. Examiners mark "not fully factored" even when partially correct.

3. **Sum of squares.** $a^2+b^2$ does **not** factor over $\\mathbb{R}$. Only $a^2-b^2=(a-b)(a+b)$.

4. **Sign errors in trinomials.** For $x^2-7x+12$, both signs inside parentheses are minus: $(x-3)(x-4)$, not $(x+3)(x+4)$.

5. **Wrong $ac$ pair.** If grouping leaves mismatched binomials, your $p,q$ for $ax^2+bx+c$ are wrong — do not force the algebra.

6. **Stopping at one difference of squares.** $x^4-1=(x^2-1)(x^2+1)$ still factors further to $(x-1)(x+1)(x^2+1)$.

**Fix habit:** After factoring, ask "Can any parenthesis be factored again?" and expand once to confirm."""

PITFALL_HE = """1. **דילוג על GCF.** ב-$6x^3-3x^2-9x$, פירוק החוליה קודם מבזבז זמן. הוציאו $3x$ קודם: $3x(2x^2-x-3)$.

2. **פירוק לא שלם.** $(x^2-4)$ לא סופי — כתבו $(x-2)(x+2)$. בודקים מורידים ניקוד על "לא מפורק לגמרי" גם כשחלק נכון.

3. **סכום ריבועים.** $a^2+b^2$ **לא** מתפרק על $\\mathbb{R}$. רק $a^2-b^2=(a-b)(a+b)$.

4. **שגיאות סימן בחוליות.** ב-$x^2-7x+12$, שני הסימנים בתוך הסוגריים שליליים: $(x-3)(x-4)$, לא $(x+3)(x+4)$.

5. **זוג $ac$ שגוי.** אם הקיבוץ נותן ביטויים לא תואמים, $p,q$ שגויים — אל תכפו את האלגברה.

6. **עצירה אחרי הפרש ריבועים אחד.** $x^4-1=(x^2-1)(x^2+1)$ עדיין מתפרק ל-$(x-1)(x+1)(x^2+1)$.

**הרגל תיקון:** אחרי פירוק, שאלו "האם סוגריים כלשהם מתפרקים שוב?" ופתחו פעם אחת לאימות."""

WHY_EN = """Factoring is the bridge between polynomial **form** and **behavior**. You cannot solve $ax^2+bx+c=0$ efficiently by guesswork once coefficients grow — factoring (or the quadratic formula derived from completing the square) is the standard path. The same skill simplifies rational expressions before limits in `concept:limits_intro` and appears inside optimization setups in `concept:equations_quadratic`.

**Recommended next topics:**
- `concept:equations_quadratic` **Quadratic Equations** — zero-product property after factoring
- `concept:algebra_basics` **Algebra Basics** — prerequisite fluency with signs and distribution

**Why it matters for exams:** Bagrut algebra rewards *complete* factoring under time pressure. A problem worth 5 points often splits into 1 point for GCF, 2 for correct pattern, 1 for signs, 1 for verification."""

WHY_HE = """פירוק הוא הגשר בין **צורה** פולינומית ל**התנהגות**. לא פותרים $ax^2+bx+c=0$ ביעילות בניחושים כשהמקדמים גדלים — פירוק (או נוסחת השורשים) הוא המסלול הסטנדרטי. אותה מיומנות מפשטת ביטויים רציונליים לפני גבולות ב-`concept:limits_intro` ומופיעה בהכנות לאופטימיזציה ב-`concept:equations_quadratic`.

**נושאים מומלצים להמשך:**
- `concept:equations_quadratic` **משוואות ריבועיות** — תכונת אפס-מכפלה אחרי פירוק
- `concept:algebra_basics` **יסודות האלגברה** — שליטה בסימנים ובפיזור

**למה זה חשוב לבחינות:** אלגברה בבגרות מעריכה פירוק **מלא** תחת לחץ זמן. בעיה של 5 נקודות לעיתים מתחלקת: נקודה על GCF, 2 על דפוס נכון, 1 על סימנים, 1 על אימות."""

BEFORE_EN = """**Formula card:**
- GCF first — always
- $a^2-b^2=(a-b)(a+b)$
- $a^2\\pm2ab+b^2=(a\\pm b)^2$
- $a^3-b^3=(a-b)(a^2+ab+b^2)$; $a^3+b^3=(a+b)(a^2-ab+b^2)$
- Trinomial $x^2+bx+c$: find $p,q$ with $pq=c$, $p+q=b$
- $ax^2+bx+c$: $ac$ method + grouping

**Exam patterns:**
- Factor completely (watch for nested difference of squares)
- Solve by factoring → zero-product property
- Simplify rational expressions by canceling **common factors** only

**Last review:** Factor $x^2-7x+12$ and $6x^2+11x-10$ from memory, then expand your answers once. Time target: under 90 seconds each with full written steps.

**Night-before checklist:** Can you state $a^3-b^3$ and $a^3+b^3$ without looking? Can you explain why $a^2+b^2$ does not factor? If yes, you are exam-ready on pattern recognition."""

BEFORE_HE = """**כרטיס נוסחאות:**
- GCF קודם — תמיד
- $a^2-b^2=(a-b)(a+b)$
- $a^2\\pm2ab+b^2=(a\\pm b)^2$
- $a^3-b^3=(a-b)(a^2+ab+b^2)$; $a^3+b^3=(a+b)(a^2-ab+b^2)$
- חוליה $x^2+bx+c$: $p,q$ עם $pq=c$, $p+q=b$
- $ax^2+bx+c$: שיטת $ac$ + קיבוץ

**דפוסי בחינה:**
- פירוק מלא (שימו לב להפרש ריבועים מקונן)
- פתרון בפירוק → אפס-מכפלה
- פישוט ביטויים רציונליים — מצמצמים רק **גורמים משותפים**

**חזרה אחרונה:** פרקו $x^2-7x+12$ ו-$6x^2+11x-10$ בעל פה, ואז פתחו פעם אחת. יעד זמן: פחות מ-90 שניות לכל אחד עם צעדים כתובים."""

SUMMARY_EN = """- **Order:** GCF → count terms → pattern (squares, cubes, trinomial, grouping) → factor again → verify.
- **Key formulas:** $a^2-b^2=(a-b)(a+b)$; perfect squares $(a\\pm b)^2$; cube formulas $a^3\\pm b^3$.
- **Trinomials:** $x^2+bx+c$ uses product/sum of two numbers; $ax^2+bx+c$ uses $ac$ split + grouping.
- **Equations:** factor completely, then set each factor to zero.

**Takeaway:** From the expression alone — term count, signs, perfect-square hints — you should name the method before doing arithmetic. That recognition is what separates fluent Bagrut algebra from slow trial-and-error."""

SUMMARY_HE = """- **סדר:** GCF → ספירת איברים → דפוס (ריבועים, קוביות, חוליה, קיבוץ) → פירוק נוסף → אימות.
- **נוסחאות מפתח:** $a^2-b^2=(a-b)(a+b)$; ריבועים מושלמים $(a\\pm b)^2$; נוסחאות קוביות $a^3\\pm b^3$.
- **חוליות:** $x^2+bx+c$ — מכפלה/סכום של שני מספרים; $ax^2+bx+c$ — פיצול $ac$ + קיבוץ.
- **משוואות:** פירוק מלא, ואז שוו כל גורם לאפס.

**מסקנה:** מהביטוי בלבד — מספר איברים, סימנים, רמזי ריבוע מושלם — תוכלו לקרוא את השיטה לפני חישוב. זיהוי זה מפריד בין אלגברה שוטפת בבגרות לניסוי וטעייה איטי."""

EXPLS = {
    1: fmt_expl(
        "Difference of squares: $x^2-9=(x-3)(x+3)$ because $9=3^2$. Option $(x-3)^2$ would expand to $x^2-6x+9$, which has a middle term this expression lacks.",
        "Two terms, minus sign, both perfect squares → try $a^2-b^2$ before anything else. Rewrite $9=3^2$ to see $a=x$, $b=3$.",
        "Choosing $(x-3)^2$ by seeing matching $3$'s without checking the middle term. Or leaving $x^2-3^2$ unexpanded — that is equivalent but not factored.",
        "On MCQ factoring items, expand your chosen answer mentally in 3 seconds: if the middle term does not match, eliminate immediately.",
        "הפרש ריבועים: $x^2-9=(x-3)(x+3)$ כי $9=3^2$. $(x-3)^2$ היה נפתח ל-$x^2-6x+9$ — עם איבר אמצעי שחסר כאן.",
        "שני איברים, מינוס, שניהם ריבועים מושלמים → נסו $a^2-b^2$ לפני כל דבר. כתבו $9=3^2$ כדי לראות $a=x$, $b=3$.",
        "בחירת $(x-3)^2$ כי רואים $3$ תואם בלי לבדוק איבר אמצעי. או השארת $x^2-3^2$ בלי פירוק — שקivalent אבל לא מפורק.",
        "בשאלות אמריקאיות, פתחו את התשובה הנבחרת בראש ב-3 שניות: אם האיבר האמצעי לא תואם — פסלו מיד.",
    ),
    2: fmt_expl(
        "Both terms share $3x$: $6x^2+9x=3x(2x+3)$. The GCF includes the variable factor $x$ to the **lowest** power appearing in every term.",
        "Two terms with no minus between squares → GCF before any other method. List numerical GCF ($3$) and variable GCF ($x$) separately, then multiply.",
        "Factoring only $3$ and leaving $x$ inside: $3(2x^2+3x)$ is not wrong algebraically but misses the full GCF — always take the highest common power of each variable.",
        "When every term contains $x$, the factored answer should start with $x$ times something unless a common factor cancels later.",
        "לשני האיברים משותף $3x$: $6x^2+9x=3x(2x+3)$. GCF כולל את $x$ ב**החזקה הנמוכה** ביותר שמופיעה בכל איבר.",
        "שני איברים בלי הפרש ריבועים → GCF לפני כל שיטה. רשמו GCF מספרי ($3$) ו-GCF משתנה ($x$) בנפרד, ואז הכפילו.",
        "הוצאת רק $3$ והשארת $x$ בפנים: $3(2x^2+3x)$ אלגברית תקין אבל לא GCF מלא — תמיד לקחו את החזקה המשותפת הגבוהה.",
        "כשכל איבר מכיל $x$, התשובה צריכה להתחיל ב-$x$ כפול משהו — אלא אם גורם משותף מתבטל מאוחר יותר.",
    ),
    3: fmt_expl(
        "$x^2-16=(x-4)(x+4)$ by difference of squares with $a=x$, $b=4$. Constant $16=4^2$ confirms the pattern.",
        "Two terms, subtraction, perfect square constant → difference of squares. Identify $a$ as the square root of the $x$-term coefficient (here $1$) times $x$.",
        "Writing $(x-4)^2$ which expands to $x^2-8x+16$ — wrong middle term. Or $(x-8)(x+2)$ where $8\\times2\\ne16$.",
        "For $x^2-k$, check whether $k$ is a perfect square on your formula sheet list ($1,4,9,16,25,\\ldots$) before trying trinomial factoring.",
        "$x^2-16=(x-4)(x+4)$ לפי הפרש ריבועים עם $a=x$, $b=4$. הקבוע $16=4^2$ מאשר את הדפוס.",
        "שני איברים, חיסור, קבוע ריבוע מושלם → הפרש ריבועים. $a$ הוא שורש המקדם של $x$ (כאן $1$) כפול $x$. אם $k$ לא ריבוע מושלם, זו לא הפרש ריבועים.",
        "כתיבת $(x-4)^2$ שנפתח ל-$x^2-8x+16$ — איבר אמצעי שגוי. או $(x-8)(x+2)$ שבו $8\\times2\\ne16$. $(x-4)^2$ נותן $-8x$ שלא קיים במקור.",
        "ב-$x^2-k$, בדקו אם $k$ ריבוע מושלם ($1,4,9,16,25,\\ldots$) לפני חוליה. בבגרות, רשימו $4^2=16$ בשוליים — מונע בלבול עם $x^2-7x+12$.",
    ),
    4: fmt_expl(
        "$x^2+6x+9=(x+3)^2$ is a perfect square trinomial: $a=x$, $b=3$, and $6x=2\\cdot x\\cdot 3$.",
        "Three terms, first and last are squares, middle is twice the product → $(a+b)^2$. Verify $2ab$ before writing the binomial.",
        "Factoring as $(x+3)(x+3)$ is equivalent but write $(x+3)^2$ when recognized — exam rubrics prefer standard perfect-square form.",
        "If the constant is $9$ and middle coefficient is $6$, suspect $(x+3)^2$ immediately; if middle were $-6$, it would be $(x-3)^2$.",
        "$x^2+6x+9=(x+3)^2$ — חוליית ריבוע מושלם: $a=x$, $b=3$, ו-$6x=2\\cdot x\\cdot 3$.",
        "שלושה איברים, ראשון ואחרון ריבועים, אמצעי פי שניים מכפלה → $(a+b)^2$. אמתו $2\\sqrt{x^2}\\cdot\\sqrt{9}=6x$ לפני כתיבת הסוגריים.",
        "פירוק ל-$(x+3)(x+3)$ שקול אבל כתבו $(x+3)^2$ כשמזהים. או $(x+9)(x+1)$ שסכום $10$, לא $6$ — בדקו סכום ומכפלה.",
        "כשהקבוע $9$ והאמצעי $6$, כתבו $(x+3)^2$ מיד — חוסך זמן לעומת חיפוש $p,q$ בחוליה. אם האמצעי $-6$, זה $(x-3)^2$.",
    ),
    5: fmt_expl(
        "Need $p,q$ with $pq=-10$ and $p+q=3$. Pair $(5,-2)$ works: $5+(-2)=3$, $5\\times(-2)=-10$. So $x^2+3x-10=(x+5)(x-2)$.",
        "Negative constant $c$ means factors have opposite signs; positive $b$ means the larger factor is positive. List factor pairs of $|c|$ systematically.",
        "Using $(x-5)(x+2)$ which gives $x^2-3x-10$ — signs reversed. Or $(x+10)(x-1)$ where product is $-10$ but sum is $9$.",
        "For $x^2+bx+c$ with $c<0$, always one plus and one minus inside parentheses; let the bigger absolute factor carry the sign of $b$.",
        "צריך $p,q$ עם $pq=-10$ ו-$p+q=3$. הזוג $(5,-2)$ מתאים: $5+(-2)=3$, $5\\times(-2)=-10$. לכן $x^2+3x-10=(x+5)(x-2)$.",
        "קבוע שלילי $c$ → גורמים בסימנים מנוגדים; $b$ חיובי → הגורם הגדול חיובי. רשימו זוגות גורמים של $|c|$ שיטתית.",
        "שימוש ב-$(x-5)(x+2)$ שנותן $x^2-3x-10$ — סימנים הפוכים. או $(x+10)(x-1)$ שמכפלה $-10$ אבל סכום $9$.",
        "ב-$x^2+bx+c$ עם $c<0$, תמיד פלוס ומינוס בסוגריים; הגורם עם ערך מוחלט גדול יותר נושא את סימן $b$.",
    ),
    6: fmt_expl(
        "$ac=2\\times3=6$. Choose $p=6$, $q=1$ because $6+1=7$ and $6\\times1=6$. Split: $2x^2+6x+x+3=2x(x+3)+(x+3)=(2x+1)(x+3)$.",
        "Leading coefficient $a\\ne1$ → $ac$ method, not product/sum of $c$ alone. After split, grouping must produce the **same** binomial in both groups.",
        "Stopping at $2x(x+3)+(x+3)$ without extracting $(x+3)$. Or picking $p=2$, $q=3$ which sum to $5$, not $7$.",
        "Write $ac$ and list factor pairs on the margin before splitting — Bagrut partial credit often awards the correct split even if grouping arithmetic slips.",
        "$ac=2\\times3=6$. בוחרים $p=6$, $q=1$ כי $6+1=7$ ו-$6\\times1=6$. פיצול: $2x^2+6x+x+3=2x(x+3)+(x+3)=(2x+1)(x+3)$.",
        "מקדם מוביל $a\\ne1$ → שיטת $ac$, לא מכפלה/סכום של $c$ בלבד. אחרי פיצול, הקיבוץ חייב לייצר **אותו** ביטוי בשני הקבוצות.",
        "עצירה ב-$2x(x+3)+(x+3)$ בלי הוצאת $(x+3)$. או בחירת $p=2$, $q=3$ שסכומם $5$, לא $7$.",
        "כתבו $ac$ ורשימת זוגות גורמים בשוליים לפני פיצול — בבגרות לעיתים נותנים נקודות על פיצול נכון גם אם הקיבוץ מחליק.",
    ),
    7: fmt_expl(
        "$27=3^3$, so $x^3-27=(x-3)(x^2+3x+9)$ by $a^3-b^3=(a-b)(a^2+ab+b^2)$ with $a=x$, $b=3$.",
        "Two terms, subtraction, perfect cube constant → difference of cubes, **not** difference of squares ($x^6-27$ would need squares first). Match power $3$ on the variable.",
        "Applying difference of squares to $x^3-27$ or forgetting the middle term $+3x$ in the quadratic factor $(x^2+3x+9)$.",
        "Memorize cube patterns with small bases ($2^3=8$, $3^3=27$) — they appear more often than larger cubes on 3–4 unit exams.",
        "$27=3^3$, ולכן $x^3-27=(x-3)(x^2+3x+9)$ לפי $a^3-b^3=(a-b)(a^2+ab+b^2)$ עם $a=x$, $b=3$.",
        "שני איברים, חיסור, קבוע קוביה מושלמת → הפרש קוביות, **לא** הפרש ריבועים. חזקה $3$ על $x$ ו-$27=3^3$ מאשרים את הדפוס.",
        "יישום $(x-3)(x+3)$ על $x^3-27$ — שגוי. או שכחת $+3x$ בגורם $(x^2+3x+9)$ — הנוסחה דורשת שלושה איברים בגורם הריבועי.",
        "שיננו $2^3=8$, $3^3=27$. ב-$x^3-k$, בדקו אם $k$ קוביה מושלמת ($1,8,27,64$) לפני כל שיטה — כתבו הנוסחה המלאה לפני הגשה.",
    ),
    8: fmt_expl(
        "$4x^2-12x+9=(2x-3)^2$ because $a=2x$, $b=3$, and $-12x=-2\\cdot2x\\cdot3$. First and last terms are squares $(2x)^2$ and $3^2$.",
        "Three terms with $a^2$ coefficient $\\ne1$ can still be perfect squares — take square roots of **each** term including coefficients: $\\sqrt{4x^2}=2x$.",
        "Factoring as $(2x+3)^2$ which gives $+12x$ middle term. Or trinomial guess $(4x-1)(x-9)$ without checking expansion.",
        "When the leading term has a coefficient, fold it inside $a$ in $(a\\pm b)^2$ — write $(2x)^2$ not $(4x^2)$ as the square root step.",
        "$4x^2-12x+9=(2x-3)^2$ כי $a=2x$, $b=3$, ו-$-12x=-2\\cdot2x\\cdot3$. האיבר הראשון והאחרון ריבועים $(2x)^2$ ו-$3^2$.",
        "שלושה איברים עם מקדם $a^2\\ne1$ עדיין יכולים להיות ריבוע מושלם — $\\sqrt{4x^2}=2x$, $\\sqrt{9}=3$, והאמצעי $-12x=-2\\cdot2x\\cdot3$.",
        "כתיבת $(2x+3)^2$ במקום $(2x-3)^2$ — סימן האיבר האמצעי קובע מינוס. או ניחוש חוליה ארוך $(4x-1)(x-9)$ בלי פתיחה.",
        "ב-$4x^2-12x+9$, זיהוי $(2x-3)^2$ חוסך זמן — המספרים $4,12,9$ קשורים ל-$2$ ו-$3$. כתבו $(2x)^2$ בשלב השורש, לא $(4x^2)$.",
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
        "Factoring techniques: GCF, difference of squares, perfect square trinomials, "
        "trinomials $ax^2+bx+c$, grouping, and sum/difference of cubes — with systematic order and full verification."
    )
    data["summary_he"] = (
        "שיטות פירוק: גורם משותף, הפרש ריבועים, ריבוע מושלם, חוליות $ax^2+bx+c$, "
        "קיבוץ, וסכום/הפרש קוביות — בסדר שיטתי ועם אימות מלא."
    )

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in SECTION_BODIES:
            sec["body_en_md"] = SECTION_BODIES[kind]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[kind]["body_he_md"]
        elif kind == "worked_example":
            n = sec.get("example_number", 1)
            if n == 1:
                sec["body_en_md"], sec["body_he_md"] = WE1_EN, WE1_HE
            elif n == 2:
                sec["body_en_md"], sec["body_he_md"] = WE2_EN, WE2_HE
            elif n == 3:
                sec["body_en_md"], sec["body_he_md"] = WE3_EN, WE3_HE
        elif kind == "checkpoint":
            if "x^2-7x+12" in sec.get("body_en_md", ""):
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

    # Fix short_answer acceptable_answers
    fixes = {
        2: ["$3x(2x+3)$", "3x(2x+3)"],
        3: ["$(x-4)(x+4)$", "(x-4)(x+4)", "x-4)(x+4"],
        4: ["$(x+3)^2$", "(x+3)^2"],
        5: ["$(x+5)(x-2)$", "(x+5)(x-2)"],
        6: ["$(2x+1)(x+3)$", "(2x+1)(x+3)", "2x+1)(x+3)"],
        7: ["$(x-3)(x^2+3x+9)$", "(x-3)(x^2+3x+9)"],
        8: ["$(2x-3)^2$", "(2x-3)^2"],
    }
    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]
        if ord_ in fixes and q["kind"] == "short_answer":
            q["answer_payload"]["acceptable_answers"] = fixes[ord_]

    # Fix skill_atoms on questions 2-8 (remove incorrect difference_of_squares where not applicable)
    atom_map = {
        1: ["difference_of_squares"],
        2: ["gcf_factoring"],
        3: ["difference_of_squares"],
        4: ["perfect_square_trinomial"],
        5: ["trinomial_factoring"],
        6: ["trinomial_factoring"],
        7: ["sum_difference_cubes"],
        8: ["perfect_square_trinomial"],
    }
    for q in data["questions"]:
        if q["ord"] in atom_map:
            q["skill_atoms"] = atom_map[q["ord"]]

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
