#!/usr/bin/env python3
"""Expand equations_quadratic.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/equations_quadratic.json"

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


INTRO_EN = """**Quadratic equations** appear whenever a quantity depends on the **square** of an unknown — area of a rectangle, height of a projectile, profit curves, and countless geometry problems on the Bagrut algebra track. Standard form is $ax^2+bx+c=0$ with $a\\ne0$; your job is to find every real $x$ that satisfies the equation or to decide that none exist.

**Where you meet them:**
- **Geometry:** A rectangle with perimeter 20 m and area 24 m² leads to $x(10-x)=24$, a quadratic in the width.
- **Kinematics:** Setting $h(t)=0$ for a parabola $h(t)=-4t^2+16t+5$ asks when the object lands.
- **Economics:** Break-even occurs when revenue minus cost equals zero — often a quadratic in price or units sold.

This lesson builds three complementary tools: **factoring** (fast when $\\Delta$ is a perfect square), the **quadratic formula** (always works), and the **discriminant** $\\Delta=b^2-4ac$ (predicts how many real roots before you compute them). Mastering when to use each saves time and prevents lost solutions on exam papers."""

INTRO_HE = """**משוואות ריבועיות** מופיעות whenever כמות תלויה ב**ריבוע** של נעלם — שטח מלבן, גובה קליע, עקומות רווח, ואינספור בעיות גאומטריה במסלול האלגברה בבגרות. הצורה הסטנדרטית היא $ax^2+bx+c=0$ עם $a\\ne0$; המשימה שלכם היא למצוא כל $x$ ממשי שמקיים את המשוואה, או להחליט שאין כאלה.

**איפה פוגשים אותן:**
- **גאומטריה:** מלבן עם היקף 20 מ' ושטח 24 מ\"ר מוביל ל-$x(10-x)=24$, משוואה ריבועית ברוחב.
- **קינמטיקה:** הצבת $h(t)=0$ בפרבולה $h(t)=-4t^2+16t+5$ שואלת מתי הגוף נוחת.
- **כלכלה:** נקודת איזון כשהכנסה פחות עלות שווה לאפס — לעיתים ריבועית במחיר או ביחידות.

בשיעור זה בונים שלושה כלים משלימים: **פירוק לגורמים** (מהיר כש-$\\Delta$ ריבוע שלם), **נוסחת השורשים** (תמיד עובדת), וה**דיסקרימיננטה** $\\Delta=b^2-4ac$ (מנבאת כמה שורשים ממשיים לפני החישוב). שליטה בבחירת השיטה חוסכת זמן ומונעת איבוד פתרונות בבחינה."""

# Fix Hebrew intro - remove accidental English "whenever"
INTRO_HE = INTRO_HE.replace("whenever ", "בכל פעם ש")

DEF_EN = """A **quadratic equation** in one variable has degree 2. In **standard form** everything sits on one side and the right side is zero:

$$ax^2 + bx + c = 0, \\quad a \\neq 0$$

**Coefficients:**
- $a$ — leading coefficient of $x^2$ (must not be zero; otherwise the equation is linear, not quadratic).
- $b$ — coefficient of the linear term $x$.
- $c$ — constant term (free term).

**Discriminant** (determines the nature of roots before solving):
$$\\Delta = b^2 - 4ac$$

| $\\Delta$ | Real solutions |
|-----------|----------------|
| $\\Delta > 0$ | Two distinct real roots |
| $\\Delta = 0$ | One repeated (double) root |
| $\\Delta < 0$ | No real roots (complex roots exist) |

**Quadratic formula** (Vieta's companion — gives explicit roots):
$$x = \\frac{-b \\pm \\sqrt{\\Delta}}{2a}$$

The $\\pm$ is essential: it produces **both** roots in one line of algebra. Before applying any method, **rearrange** so the equation equals zero — hidden terms on the right side cause sign errors that propagate through $\\Delta$ and the formula."""

DEF_HE = """**משוואה ריבועית** במשתנה אחד היא מדרגה 2. ב**צורה סטנדרטית** הכל בצד אחד והצד הימני אפס:

$$ax^2 + bx + c = 0, \\quad a \\neq 0$$

**מקדמים:**
- $a$ — מקדם $x^2$ (חייב להיות שונה מאפס; אחרת המשוואה לינארית, לא ריבועית).
- $b$ — מקדם האיבר $x$.
- $c$ — האיבר החופשי (קבוע).

**דיסקרימיננטה** (קובעת את אופי השורשים לפני הפתרון):
$$\\Delta = b^2 - 4ac$$

| $\\Delta$ | פתרונות ממשיים |
|-----------|----------------|
| $\\Delta > 0$ | שני שורשים ממשיים שונים |
| $\\Delta = 0$ | שורש כפול אחד |
| $\\Delta < 0$ | אין שורשים ממשיים (קיימים מרוכבים) |

**נוסחת השורשים:**
$$x = \\frac{-b \\pm \\sqrt{\\Delta}}{2a}$$

ה-$\\pm$ חיוני: הוא מייצר **שני** שורשים בשורת אלגברה אחת. לפני כל שיטה, **ארגנו** כך שהמשוואה שווה לאפס — איברים נסתרים בצד הימני גורמים לשגיאות סימן ב-$\\Delta$ ובנוסחה."""

THEORY_EN = """Choose a method using structure, not habit. The same decision tree works on every Bagrut item.

**Method 1 — Factoring (zero-product property):**
Rewrite as $(px+q)(rx+s)=0$, then $px+q=0$ or $rx+s=0$.
*Best when:* $\\Delta$ is a perfect square and $a,b,c$ are small integers.
Example pattern: $x^2+bx+c$ — find integers with product $c$ and sum $b$.

**Method 2 — Quadratic formula:**
$$x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}$$
*Best when:* factoring is not obvious, coefficients are fractions, or the stem says "use the formula."

**Method 3 — Completing the square:**
Rewrite $x^2+bx+c=0$ as $(x+p)^2=q$, then $x+p=\\pm\\sqrt{q}$.
*Best when:* $a=1$ and $b$ is even; also the proof behind the formula.

**Workflow every time:**
1. Move all terms to one side ($=0$).
2. Identify $a,b,c$ (watch signs!).
3. Compute $\\Delta$ if unsure about method or if the question is parametric.
4. Solve, then **substitute back** to verify.

**Parametric problems** ($k$, $m$): translate words like "two distinct roots" into $\\Delta>0$, "one repeated root" into $\\Delta=0$, "no real roots" into $\\Delta<0$, then solve the inequality for the parameter."""

THEORY_HE = """בחרו שיטה לפי מבנה, לא לפי הרגל. אותו עץ החלטות עובד בכל שאלת בגרות.

**שיטה 1 — פירוק לגורמים (תכונת אפס-מכפלה):**
כותבים $(px+q)(rx+s)=0$, ואז $px+q=0$ או $rx+s=0$.
*מתאים כש:* $\\Delta$ ריבוע שלם ו-$a,b,c$ שלמים קטנים.
דפוס: $x^2+bx+c$ — מוצאים שלמים שמכפלתם $c$ וסכומם $b$.

**שיטה 2 — נוסחת השורשים:**
$$x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}$$
*מתאים כש:* פירוק לא ברור, מקדמים שבריים, או שהניסוח דורש "השתמשו בנוסחה".

**שיטה 3 — השלמה לריבוע:**
כותבים $x^2+bx+c=0$ כ-$(x+p)^2=q$, ואז $x+p=\\pm\\sqrt{q}$.
*מתאים כש:* $a=1$ ו-$b$ זוגי; גם הבסיס להוכחת הנוסחה.

**תהליך בכל פעם:**
1. העבירו הכל לצד אחד ($=0$).
2. זיהו $a,b,c$ (שימו לב לסימנים!).
3. חשבו $\\Delta$ אם לא בטוחים בשיטה או בשאלה פרמטרית.
4. פתרו, ואז **הציבו חזרה** לאימות.

**בעיות פרמטריות** ($k$, $m$): "שני שורשים שונים" $\\Rightarrow$ $\\Delta>0$; "שורש כפול" $\\Rightarrow$ $\\Delta=0$; "אין שורשים ממשיים" $\\Rightarrow$ $\\Delta<0$; ואז פותרים את האי-שוויון."""

WE1_EN = """**Solve:** $x^2 - 5x + 6 = 0$

This is a classic trinomial with $a=1$. Factoring is faster than the formula because the constant $6$ has small integer factors.

### Move 1
Confirm standard form: right side is already $0$. Identify $a=1$, $b=-5$, $c=6$. Quick discriminant check: $\\Delta=25-24=1>0$, so two distinct real roots — factoring should work cleanly.

### Move 2
Find integers $p,q$ with $p\\cdot q=6$ and $p+q=-5$. Both numbers must have the same sign (product positive, sum negative).
Try $p=-2$, $q=-3$: $(-2)(-3)=6$ ✓ and $-2+(-3)=-5$ ✓.

### Move 3
Write the factored form using those numbers as roots:
$$x^2 - 5x + 6 = (x - 2)(x - 3) = 0$$

### Move 4
Apply the zero-product property — if a product equals zero, at least one factor is zero:
$$x - 2 = 0 \\implies x = 2, \\quad x - 3 = 0 \\implies x = 3$$

**Check by substitution:** $f(2)=4-10+6=0$ ✓; $f(3)=9-15+6=0$ ✓. Both roots satisfy the original equation.

**Answer:** $x=2$ or $x=3$. On an exam, show the integer search explicitly — it earns method marks even before the final factors."""

WE1_HE = """**פתרו:** $x^2 - 5x + 6 = 0$

זו חוליה קלאסית עם $a=1$. פירוק מהיר יותר מהנוסחה כי הקבוע $6$ מתפרק לשלמים קטנים ונוחים.

### צעד 1
אימות צורה סטנדרטית: הצד הימני כבר $0$. זיהוי $a=1$, $b=-5$, $c=6$. בדיקת $\\Delta$ מהירה: $\\Delta=25-24=1>0$ — שני שורשים ממשיים שונים, פירוק אמור לעבוד.

### צעד 2
מוצאים שלמים $p,q$ עם $p\\cdot q=6$ ו-$p+q=-5$. שני המספרים באותו סימן (מכפלה חיובית, סכום שלילי).
ניסיון $p=-2$, $q=-3$: $(-2)(-3)=6$ ✓ ו-$-2+(-3)=-5$ ✓.

### צעד 3
כותבים צורה מפורקת לפי השורשים:
$$x^2 - 5x + 6 = (x - 2)(x - 3) = 0$$

### צעד 4
תכונת אפס-מכפלה — אם מכפלה שווה לאפס, לפחות גורם אחד אפס:
$$x - 2 = 0 \\implies x = 2, \\quad x - 3 = 0 \\implies x = 3$$

**בדיקה בהצבה:** $f(2)=0$ ✓; $f(3)=0$ ✓. שני השורשים מקיימים את המשוואה המקורית.

**תשובה:** $x=2$ או $x=3$. בבחינה, הציגו את חיפוש השלמים במפורש — נקודות על השיטה והחישוב."""

WE2_EN = """**Solve:** $3x^2 - x - 2 = 0$

When $a\\ne1$, factoring by trial is slower; the quadratic formula is reliable. We still compute $\\Delta$ first to confirm two real roots exist.

### Move 1
Identify coefficients carefully — signs matter on the exam:
$$a=3, \\quad b=-1, \\quad c=-2$$
The negative $c$ makes $-4ac$ **positive** because $-4(3)(-2)=+24$.

### Move 2
Compute the discriminant in a separate line (examiners expect this):
$$\\Delta = (-1)^2 - 4(3)(-2) = 1 + 24 = 25$$
Since $\\Delta=25>0$ and $25=5^2$, two distinct real roots exist. Factoring as $(3x+2)(x-1)=0$ would also work, but we follow the formula path.

### Move 3
Substitute into the quadratic formula — note $-b=+1$ and $\\sqrt{\\Delta}=5$:
$$x = \\frac{-(-1) \\pm \\sqrt{25}}{2(3)} = \\frac{1 \\pm 5}{6}$$

### Move 4
Evaluate **both** branches of $\\pm$ explicitly:
$$x_1 = \\frac{1+5}{6} = 1, \\quad x_2 = \\frac{1-5}{6} = -\\frac{2}{3}$$

**Check:** $3(1)^2-1-2=0$ ✓. For $x=-\\frac{2}{3}$: $3(\\frac{4}{9})+\\frac{2}{3}-2=\\frac{4}{3}+\\frac{2}{3}-2=0$ ✓

**Answer:** $x=1$ or $x=-\\dfrac{2}{3}$. Always show the $\\pm$ split — skipping it loses a root and marks."""

WE2_HE = """**פתרו:** $3x^2 - x - 2 = 0$

כש-$a\\ne1$, פירוק בניסוי איטי יותר; נוסחת השורשים אמינה. עדיין מחשבים $\\Delta$ קודם לאימות שני שורשים ממשיים.

### צעד 1
זיהוי מקדמים בקפידה — סימנים קובעים בבחינה:
$$a=3, \\quad b=-1, \\quad c=-2$$
ה-$c$ השלילי הופך את $-4ac$ ל**חיובי** כי $-4(3)(-2)=+24$.

### צעד 2
חישוב דיסקרימיננטה בשורה נפרדת (הבוחנים מצפים):
$$\\Delta = (-1)^2 - 4(3)(-2) = 1 + 24 = 25$$
מאחר ש-$\\Delta=25>0$ ו-$25=5^2$, קיימים שני שורשים. פירוק $(3x+2)(x-1)=0$ גם אפשרי, אך נלך בנוסחה.

### צעד 3
הצבה בנוסחת השורשים — שימו לב $-b=+1$ ו-$\\sqrt{\\Delta}=5$:
$$x = \\frac{-(-1) \\pm \\sqrt{25}}{2(3)} = \\frac{1 \\pm 5}{6}$$

### צעד 4
חישוב **שני** ענפי $\\pm$ במפורש:
$$x_1 = \\frac{1+5}{6} = 1, \\quad x_2 = \\frac{1-5}{6} = -\\frac{2}{3}$$

**בדיקה:** $3(1)^2-1-2=0$ ✓. עבור $x=-\\frac{2}{3}$: $3(\\frac{4}{9})+\\frac{2}{3}-2=0$ ✓

**תשובה:** $x=1$ או $x=-\\dfrac{2}{3}$. הציגו פיצול $\\pm$ במפורש — השמטה מאבדת שורש ונקודות חשובות."""

WE3_EN = """**Problem:** For which values of $k$ does $x^2 - kx + 9 = 0$ have two distinct real roots?

Parametric questions test whether you translate words into discriminant conditions **before** solving for $x$.

### Move 1
Identify coefficients in terms of $k$: $a=1$, $b=-k$, $c=9$. Write $\\Delta$ symbolically:
$$\\Delta = (-k)^2 - 4(1)(9) = k^2 - 36$$
Note $(-k)^2=k^2$ — a common simplification.

### Move 2
Translate "two **distinct** real roots" into a strict inequality. Distinct means $\\Delta>0$, not $\\Delta\\ge0$ (which would include the double-root case $\\Delta=0$):
$$k^2 - 36 > 0 \\implies k^2 > 36$$

### Move 3
Solve the inequality on the number line. Since $k^2>36$ means $k$ is farther from zero than 6:
$$|k| > 6 \\implies k < -6 \\text{ or } k > 6$$

**Boundary checks (always verify endpoints on Bagrut):**
- $k=6$: $\\Delta=36-36=0$ → one repeated root — **not** two distinct. Excluded. ✓
- $k=7$: $\\Delta=49-36=13>0$ → two distinct roots. Included. ✓
- $k=5$: $\\Delta=25-36=-11<0$ → no real roots. Excluded. ✓

**Answer:** $k<-6$ or $k>6$. Write the final set in interval notation or on a number line for full credit."""

WE3_HE = """**בעיה:** עבור אילו ערכי $k$ יש ל-$x^2 - kx + 9 = 0$ שני שורשים ממשיים שונים?

שאלות פרמטריות בודקות אם מתרגמים מילים לתנאי על $\\Delta$ **לפני** פתרון ל-$x$.

### צעד 1
זיהוי מקדמים ב-$k$: $a=1$, $b=-k$, $c=9$. כתיבת $\\Delta$ סימבולית:
$$\\Delta = (-k)^2 - 4(1)(9) = k^2 - 36$$
שימו לב $(-k)^2=k^2$ — פישוט נפוץ.

### צעד 2
תרגום "שני שורשים **שונים**" לאי-שוויון קפדני. שונים $\\Rightarrow$ $\\Delta>0$, לא $\\Delta\\ge0$ (שכולל $\\Delta=0$ — שורש כפול):
$$k^2 - 36 > 0 \\implies k^2 > 36$$

### צעד 3
פתרון על ציר המספרים. $k^2>36$ פירושו $|k|>6$:
$$k < -6 \\text{ או } k > 6$$

**בדיקת גבולות (תמיד בבגרות):**
- $k=6$: $\\Delta=0$ → שורש כפול — **לא** שניים שונים. לא נכלל. ✓
- $k=7$: $\\Delta=13>0$ → שני שורשים. נכלל. ✓
- $k=5$: $\\Delta=-11<0$ → אין שורשים ממשיים. לא נכלל. ✓

**תשובה:** $k<-6$ או $k>6$. כתבו את קבוצת הפתרון בציר או בסימון קטעים לניקוד מלא בבחינה."""

CHK1_EN = """**Checkpoint:** $x^2 - 7x + 12 = 0$

Standard form is already satisfied ($=0$ on the right). We need two integers whose product is $c=12$ and sum is $b=-7$. Since the product is positive and sum negative, both integers are negative.

Try $p=-3$, $q=-4$: $(-3)(-4)=12$ ✓ and $-3+(-4)=-7$ ✓.

Factor: $x^2-7x+12=(x-3)(x-4)=0$. Zero-product gives $x=3$ or $x=4$.

**Verify:** $3^2-7(3)+12=9-21+12=0$ ✓; $4^2-7(4)+12=16-28+12=0$ ✓. Both roots check."""

CHK1_HE = """**תרגול:** $x^2 - 7x + 12 = 0$

הצורה הסטנדרטית כבר מתקיימת. דרושים שני שלמים שמכפלתם $c=12$ וסכומם $b=-7$. המכפלה חיובית והסכום שלילי — שני השלמים שליליים.

ניסיון $p=-3$, $q=-4$: $(-3)(-4)=12$ ✓ ו-$-3+(-4)=-7$ ✓.

פירוק: $x^2-7x+12=(x-3)(x-4)=0$. אפס-מכפלה: $x=3$ או $x=4$.

**אימות:** $3^2-7(3)+12=0$ ✓; $4^2-7(4)+12=0$ ✓. שני השורשים נכונים."""

CHK2_EN = """**Checkpoint:** $2x^2 + 5x - 3 = 0$

Identify $a=2$, $b=5$, $c=-3$. The negative constant makes $-4ac$ positive: $-4(2)(-3)=+24$.

Discriminant: $\\Delta=b^2-4ac=25+24=49=7^2$. Two distinct real roots expected.

Quadratic formula: $x=\\dfrac{-5\\pm\\sqrt{49}}{4}=\\dfrac{-5\\pm7}{4}$.

So $x_1=\\dfrac{-5+7}{4}=\\dfrac{2}{4}=\\dfrac{1}{2}$ and $x_2=\\dfrac{-5-7}{4}=\\dfrac{-12}{4}=-3$.

**Check:** $2(\\frac{1}{2})^2+5(\\frac{1}{2})-3=\\frac{1}{2}+\\frac{5}{2}-3=0$ ✓"""

CHK2_HE = """**תרגול:** $2x^2 + 5x - 3 = 0$

זיהוי $a=2$, $b=5$, $c=-3$. הקבוע השלילי הופך את $-4ac$ לחיובי: $-4(2)(-3)=+24$.

דיסקרימיננטה: $\\Delta=25+24=49=7^2$. צפו לשני שורשים ממשיים שונים.

נוסחת שורשים: $x=\\dfrac{-5\\pm7}{4}$.

לכן $x_1=\\dfrac{1}{2}$ ו-$x_2=-3$.

**בדיקה:** $2(\\frac{1}{2})^2+5(\\frac{1}{2})-3=0$ ✓"""

METHOD_EN = """| Situation | Recommended method | Why |
|-----------|-------------------|-----|
| $\\Delta$ perfect square, integer $a,b,c$ | Factoring | Fastest; shows structure examiners like |
| $\\Delta$ not a perfect square | Quadratic formula | Guaranteed correct roots |
| Stem says "use the formula" | Quadratic formula | Method marks depend on it |
| $a=1$, even $b$ | Completing the square or factoring | Clean arithmetic |
| Parameter $k$ / "how many roots" | Discriminant conditions | Avoid solving full equation |
| Equation like $x^2=4x$ | Factor after moving to $=0$ | Never divide by $x$ |

**Decision shortcut:** compute $\\Delta$ first when unsure — it tells you *how many* roots and whether factoring is likely ($\\Delta$ a perfect square).

**Always:** rearrange to $ax^2+bx+c=0$ before any method. Write $a,b,c$ on your exam paper — partial credit often requires visible identification."""

METHOD_HE = """| מצב | שיטה מומלצת | למה |
|-----|-------------|-----|
| $\\Delta$ ריבוע שלם, $a,b,c$ שלמים | פירוק לגורמים | הכי מהיר; מראה מבנה |
| $\\Delta$ לא ריבוע שלם | נוסחת השורשים | שורשים נכונים בוודאות |
| הניסוח דורש "השתמשו בנוסחה" | נוסחת השורשים | נקודות על השיטה |
| $a=1$, $b$ זוגי | השלמה לריבוע או פירוק | חישוב נקי |
| פרמטר $k$ / "כמה שורשים" | תנאי על $\\Delta$ | בלי לפתור את כל המשוואה |
| משוואה כמו $x^2=4x$ | פירוק אחרי $=0$ | לעולם אל תחלקו ב-$x$ |

**קיצור דרך:** חשבו $\\Delta$ כשלא בטוחים — הוא אומר *כמה* שורשים ואם פירוק סביר ($\\Delta$ ריבוע שלם).

**תמיד:** ארגנו ל-$ax^2+bx+c=0$ לפני כל שיטה. כתבו $a,b,c$ בדף — נקודות ביניים דורשות זיהוי גלוי."""

PITFALL_EN = """**Mistake 1 — Dividing both sides by $x$.**
If $x^2=4x$, dividing by $x$ gives $x=4$ and **loses** $x=0$. Always move to standard form: $x^2-4x=0\\Rightarrow x(x-4)=0$.

**Mistake 2 — Dropping the $\\pm$ in the formula.**
$x=\\dfrac{-b\\pm\\sqrt{\\Delta}}{2a}$ has two roots. Using only $+$ or only $-$ yields half the solution set — a common 2-mark loss.

**Mistake 3 — Sign error in $\\Delta$ when $c<0$.**
$\\Delta=b^2-4ac$. If $a=2$ and $c=-3$, then $-4ac=-4(2)(-3)=+24$, not $-24$. Write the multiplication explicitly.

**Mistake 4 — Confusing $\\Delta=0$ with "no solutions".**
$\\Delta=0$ means **one repeated** real root, not zero roots. Only $\\Delta<0$ means no real solutions."""

PITFALL_HE = """**טעות 1 — חלוקה ב-$x$.**
אם $x^2=4x$, חלוקה ב-$x$ נותנת $x=4$ ו**מאבדת** $x=0$. תמיד עברו לצורה סטנדרטית: $x^2-4x=0\\Rightarrow x(x-4)=0$.

**טעות 2 — השמטת $\\pm$ בנוסחה.**
$x=\\dfrac{-b\\pm\\sqrt{\\Delta}}{2a}$ נותן שני שורשים. שימוש רק ב-$+$ או רק ב-$-$ — איבוד חצי מהפתרונות.

**טעות 3 — שגיאת סימן ב-$\\Delta$ כש-$c<0$.**
$\\Delta=b^2-4ac$. אם $a=2$ ו-$c=-3$, אז $-4ac=-4(2)(-3)=+24$, לא $-24$. כתבו את הכפל במפורש.

**טעות 4 — בלבול $\\Delta=0$ עם "אין פתרונות".**
$\\Delta=0$ פירושו **שורש כפול** ממשי אחד, לא אפס שורשים. רק $\\Delta<0$ אומר שאין פתרונות ממשיים."""

WHY_EN = """Quadratic equations are the **bridge** between linear algebra and higher topics on A Step Forward: parabola graphs, optimization, complex numbers ($\\Delta<0$), and physics kinematics all assume you can solve $ax^2+bx+c=0$ reliably.

**Exam transfer:** Bagrut 3–4 units rarely ask "solve this" in isolation — they embed quadratics inside word problems, rational equations, and parameter questions. The discriminant shortcut separates students who merely memorize the formula from those who **predict** solution counts before calculating.

**Downstream connections:** Factoring skills from the prior lesson feed directly into Method 1 here; completing the square previews vertex form $y=a(x-h)^2+k$ in functions; parametric $\\Delta$ conditions reappear in analytic geometry (tangent lines to parabolas). Treat every quadratic as practice for structured reasoning, not rote substitution."""

WHY_HE = """משוואות ריבועיות הן **גשר** בין אלגברה לינארית לנושאים מתקדמים ב-A Step Forward: גרפי פרבולות, אופטימיזציה, מספרים מרוכבים ($\\Delta<0$), וקינמטיקה בפיזיקה — כולם מניחים שאתם יודעים לפתור $ax^2+bx+c=0$ באמינות.

**העברה בבחינה:** בבגרות 3–4 יחידות seldom שואלים "פתרו" בבידוד — משבצים ריבועיות בתוך בעיות מילוליות, משוואות רציונליות ושאלות פרמטר. קיצור הדרך של $\\Delta$ מפריד בין מי שזוכר נוסחה לבין מי ש**מנבא** כמה פתרונות לפני החישוב.

**קשרים בהמשך:** פירוק מהשיעור הקודם מזין ישירות לשיטה 1; השלמה לריבוע מכינה לצורת קודקוד $y=a(x-h)^2+k$; תנאי $\\Delta$ פרמטריים חוזרים בגאומטריה אנליטית. התייחסו לכל ריבועית כאימון לחשיבה מסודרת, לא להצבה מכנית."""

WHY_HE = WHY_HE.replace("seldom ", "לעיתים רחוקות ")

BEFORE_EN = """**Essential formulas (write these on your formula sheet):**
- Standard form: $ax^2+bx+c=0$ with $a\\ne0$
- Discriminant: $\\Delta=b^2-4ac$
- Roots: $x=\\dfrac{-b\\pm\\sqrt{\\Delta}}{2a}$
- Count: $\\Delta>0\\Rightarrow2$; $\\Delta=0\\Rightarrow1$ (double); $\\Delta<0\\Rightarrow0$ real

**Typical Bagrut 3pt patterns:**
1. **Direct solve** — show $a,b,c$, $\\Delta$, formula, both roots. (4–5 marks)
2. **Repeated root** — find $k$ where $\\Delta=0$. (3–4 marks)
3. **Word problem** — define variable, build equation, solve, reject invalid roots (negative length). (5–6 marks)
4. **Rational equation** — clear denominators first, then quadratic. (5 marks)

**Marking tips:** Label each step. Show $\\pm$ split explicitly. Substitute one root back. State final answer in context (units, "width = 5 m")."""

BEFORE_HE = """**נוסחאות חיוניות (רשמו בדף נוסחאות):**
- צורה סטנדרטית: $ax^2+bx+c=0$ עם $a\\ne0$
- דיסקרימיננטה: $\\Delta=b^2-4ac$
- שורשים: $x=\\dfrac{-b\\pm\\sqrt{\\Delta}}{2a}$
- ספירה: $\\Delta>0\\Rightarrow2$; $\\Delta=0\\Rightarrow1$ (כפול); $\\Delta<0\\Rightarrow0$ ממשיים

**דפוסי בגרות 3 יח':**
1. **פתרון ישיר** — הציגו $a,b,c$, $\\Delta$, נוסחה, שני שורשים. (4–5 נק')
2. **שורש כפול** — מציאת $k$ כש-$\\Delta=0$. (3–4 נק')
3. **בעיית מילים** — הגדרת משתנה, בניית משוואה, פתרון, דחיית שורשים לא הגיוניים. (5–6 נק')
4. **משוואה רציונלית** — ניקוי מכנים קודם, ואז ריבועית. (5 נק')

**טיפים לניקוד:** תייגו כל שלב. הציגו פיצול $\\pm$ במפורש. הציבו שורש אחד חזרה. נסחו תשובה סופית בהקשר (יחידות, "רוחב = 5 מ'")."""

SUMMARY_EN = """**Key takeaways:**
- Always rearrange to $ax^2+bx+c=0$ before solving.
- Discriminant $\\Delta=b^2-4ac$ predicts root count: positive → 2, zero → 1 double, negative → none (real).
- **Factoring:** find two numbers with product $ac$ and sum $b$ (when $a=1$, product $c$).
- **Formula:** $x=\\dfrac{-b\\pm\\sqrt{\\Delta}}{2a}$ — never omit $\\pm$.
- **Parameters:** translate root conditions into inequalities on $\\Delta$.
- **Word problems:** define $x$, build equation, solve, interpret — reject impossible values.
- Never divide by $x$; factor to keep all solutions."""

SUMMARY_HE = """**עיקרי הדברים:**
- תמיד ארגנו ל-$ax^2+bx+c=0$ לפני פתרון.
- דיסקרימיננטה $\\Delta=b^2-4ac$ מנבאת מספר שורשים: חיובי → 2, אפס → כפול 1, שלילי → אין (ממשיים).
- **פירוק:** שני מספרים שמכפלתם $ac$ וסכומם $b$ (כש-$a=1$, מכפלה $c$).
- **נוסחה:** $x=\\dfrac{-b\\pm\\sqrt{\\Delta}}{2a}$ — לעולם אל תשמיטו $\\pm$.
- **פרמטרים:** תנאי שורשים → אי-שוויונות על $\\Delta$.
- **בעיות מילים:** הגדרת $x$, בניית משוואה, פתרון, פרשנות — דחיית ערכים בלתי-אפשריים.
- לעולם אל תחלקו ב-$x$; פרקו כדי לשמור כל הפתרונות."""

EXPLS = {
    1: fmt_expl(
        "The expression $x^2-9$ is a difference of squares: $x^2-9=(x-3)(x+3)$. Setting the product to zero gives $x=3$ or $x=-3$. Both satisfy the original equation since $3^2=9$ and $(-3)^2=9$.",
        "Recognize $a^2-b^2$ before reaching for the formula — when $c$ is negative and $b=0$, factoring is one step. Check: no middle term means sum/product search is unnecessary.",
        "Answering only $x=3$ and forgetting $-3$, or dividing $x^2=9$ by $x$ and losing a root. Also writing $(x-3)^2$ instead of difference of squares.",
        "On Bagrut, difference-of-squares items appear without the label — scan for perfect-square first and last terms with opposite signs on $c$.",
        "הביטוי $x^2-9$ הוא הפרש ריבועים: $(x-3)(x+3)$. אפס-מכפלה נותן $x=3$ או $x=-3$. שניהם מקיימים את המשוואה כי $3^2=9$ ו-$(-3)^2=9$.",
        "זיהו $a^2-b^2$ לפני נוסחת השורשים — כש-$c$ שלילי ו-$b=0$, פירוק בשלב אחד. אין איבר אמצעי, אז אין חיפוש סכום/מכפלה.",
        "תשובה רק $x=3$ בלי $-3$, או חלוקה ב-$x$ באיבוד שורש. גם כתיבת $(x-3)^2$ במקום הפרש ריבועים.",
        "בבגרות, הפרש ריבועים מופיע בלי תווית — חפשו ריבועים בראש ובסוף עם $c$ שלילי.",
    ),
    2: fmt_expl(
        "Here $x^2+6x+9=(x+3)^2$ is a perfect square trinomial because $6=2\\cdot3$ and $9=3^2$. So $(x+3)^2=0$ gives the repeated root $x=-3$ only once — graphically the parabola touches the $x$-axis at one point.",
        "When $\\Delta=0$, expect a perfect square factorization. Verify middle term: twice product of square roots of first and last terms.",
        "Giving two different answers $\\pm3$ — a double root is a **single** value. Or using formula without noticing $\\Delta=36-36=0$.",
        "Repeated-root questions often ask 'how many solutions' — answer one, and state it is repeated. Show $\\Delta=0$ for full marks.",
        "כאן $x^2+6x+9=(x+3)^2$ — ריבוע מושלם כי $6=2\\cdot3$ ו-$9=3^2$. לכן $(x+3)^2=0$ נותן שורש כפול $x=-3$ פעם אחת — הפרבולה נוגעת בציר $x$ בנקודה אחת.",
        "כש-$\\Delta=0$, צפו לריבוע מושלם. אמתו איבר אמצעי: פי שתיים מכפלת שורשי האיברים הראשון והאחרון.",
        "מתן $\\pm3$ כשני פתרונות שונים — שורש כפול הוא **ערך יחיד**. או שימוש בנוסחה בלי $\\Delta=0$.",
        "שאלות שורש כפול שואלות 'כמה פתרונות' — תשובה: אחד, חוזר. הציגו $\\Delta=0$ לניקוד מלא.",
    ),
    3: fmt_expl(
        "With $a=5$, $b=-3$, $c=1$: $\\Delta=(-3)^2-4(5)(1)=9-20=-11<0$. Negative discriminant means the parabola never crosses the $x$-axis, so there are **no real** solutions (complex roots exist but are outside Bagrut 3pt scope).",
        "Discriminant-only questions test whether you compute $-4ac$ with correct signs — here $c>0$ makes $-4ac$ negative, pulling $\\Delta$ below $b^2$.",
        "Answering 'one solution' because the equation 'looks simple', or arithmetic error $9-20=11$ without the minus sign.",
        "State both the numeric $\\Delta$ and the conclusion ('no real solutions'). Examiners award separate marks for calculation vs interpretation.",
        "עם $a=5$, $b=-3$, $c=1$: $\\Delta=9-20=-11<0$. דיסקרימיננטה שלילית — הפרבולה לא חוצה את ציר $x$, **אין** פתרונות ממשיים.",
        "שאלות דיסקרימיננטה בודקות $-4ac$ עם סימנים נכונים — כאן $c>0$ מושך את $\\Delta$ מתחת ל-$b^2$. זכרו: $\\Delta<0$ אומר אין חיתוך עם ציר $x$.",
        "תשובה 'פתרון אחד' כי המשוואה 'פשוטה', או $9-20=11$ בלי מינוס — שגיאת חישוב נפוצה.",
        "ציינו $\\Delta$ מספרי ומסקנה ('אין פתרונות ממשיים'). נקודות נפרדות לחישוב ולפרשנות בבגרות.",
    ),
    4: fmt_expl(
        "Move to standard form: $x^2-4x=0$, factor $x(x-4)=0$, so $x=0$ or $x=4$. The stem explicitly warns against dividing by $x$ because that cancels the $x=0$ root — a classic trap testing the zero-product property.",
        "Any equation with $x$ on both sides should be rearranged first. Factoring out GCF $x$ is cleaner than the formula when $c=0$.",
        "Dividing by $x$ to get $x=4$ only. Or expanding incorrectly after moving terms.",
        "When you see 'do not divide by $x$', examiners are targeting the lost-root error — always factor after $=0$.",
        "עברו לצורה סטנדרטית: $x^2-4x=0$, פירוק $x(x-4)=0$, לכן $x=0$ או $x=4$. הניסוח מזהיר מפני חלוקה ב-$x$ שמאבדת את $x=0$ — מלכודת קלאסית.",
        "משוואה עם $x$ בשני הצדדים — ארגנו קודם ל-$=0$. הוצאת GCF $x$ נקייה יותר מהנוסחה כש-$c=0$.",
        "חלוקה ב-$x$ וקבלת רק $x=4$. או פירוק שגוי אחרי העברת איברים — בדקו שני שורשים בהצבה.",
        "כשכתוב 'אל תחלקו ב-$x$', המטרה איבוד שורש $x=0$ — תמיד פרקו אחרי $=0$ ואז השתמשו באפס-מכפלה.",
    ),
    5: fmt_expl(
        "Here $a=1$, $b=-3$, $c=-4$. $\\Delta=9+16=25$, so $x=\\dfrac{3\\pm5}{2}$: $x_1=4$, $x_2=-1$. You could factor as $(x-4)(x+1)=0$, but the stem requires the formula — show $a,b,c$, $\\Delta$, and both $\\pm$ branches.",
        "Negatives in $b$ and $c$ flip signs in $\\Delta$: $-4(1)(-4)=+16$. Substitute both roots into $x^2-3x-4$ to verify.",
        "Sign error on $b$ in the formula (using $+3$ instead of $-3$ in the numerator). Or stopping after one root.",
        "Formula questions on Bagrut: write the full template even if factoring is faster — method marks require visible $\\Delta$ and $\\pm$ split.",
        "כאן $a=1$, $b=-3$, $c=-4$. $\\Delta=25$, $x=\\dfrac{3\\pm5}{2}$: $x_1=4$, $x_2=-1$. אפשר $(x-4)(x+1)=0$, אך הניסוח דורש נוסחה — הציגו $a,b,c$, $\\Delta$, ושני ענפי $\\pm$.",
        "מינוסים ב-$b$ ו-$c$ משנים סימנים ב-$\\Delta$: $-4(1)(-4)=+16$. הציבו שני השורשים ב-$x^2-3x-4$.",
        "שגיאת סימן על $b$ בנוסחה. או עצירה אחרי שורש אחד.",
        "שאלות נוסחה: כתבו תבנית מלאה גם אם פירוק מהיר — נקודות על $\\Delta$ ופיצול $\\pm$.",
    ),
    6: fmt_expl(
        "$4x^2-12x+9=(2x-3)^2$ is a perfect square with $a=2x$, $b=3$. So $\\Delta=144-144=0$ and $x=\\dfrac{12}{8}=\\dfrac{3}{2}$ is the **only** root (repeated). Leading coefficient $4$ still allows perfect-square recognition via $(2x)^2$ and $3^2$.",
        "When $\\Delta=0$, try factoring as a square before the formula — here $(2x-3)^2$ is immediate. Formula gives the same single value.",
        "Reporting two different roots from $\\pm$ when $\\sqrt{\\Delta}=0$ — both branches coincide. Or forgetting to simplify $\\frac{12}{8}$.",
        "Repeated roots with $a\\ne1$: take square roots of **coefficients** too ($\\sqrt{4x^2}=2x$). Show $\\Delta=0$ explicitly.",
        "$4x^2-12x+9=(2x-3)^2$ — ריבוע מושלם עם $a=2x$, $b=3$. $\\Delta=0$ ו-$x=\\dfrac{3}{2}$ הוא **השורש היחיד** (כפול).",
        "כש-$\\Delta=0$, נסו ריבוע מושלם — $(2x-3)^2$ מיידי. הנוסחה נותנת אותו ערך יחיד $x=\\frac{3}{2}$.",
        "שני שורשים שונים מ-$\\pm$ כש-$\\sqrt{\\Delta}=0$ — שני הענפים זהים. או $\\frac{12}{8}$ בלי צמצום ל-$\\frac{3}{2}$.",
        "שורש כפול עם $a\\ne1$: שורשים גם על **מקדמים** ($\\sqrt{4x^2}=2x$). הציגו $\\Delta=0$ וציינו 'שורש כפול' במפורש בבחינה.",
    ),
    7: fmt_expl(
        "Let width $x$ m, length $x+3$ m. Area: $x(x+3)=40\\Rightarrow x^2+3x-40=0$. $\\Delta=9+160=169$, $x=\\dfrac{-3+13}{2}=5$ (reject negative width). Dimensions: width 5 m, length 8 m. Check: $5\\times8=40$ ✓.",
        "Word problems: define variable, draw a sketch, build equation from geometry relations, solve, then **reject** non-physical roots (negative length). Only the positive root makes sense.",
        "Using perimeter instead of area, or accepting $x=-8$ without rejection. Arithmetic slip on $\\Delta=9+160$.",
        "Always write 'width = …, length = …' with units. Substitute into the **original** word relation, not just the quadratic.",
        "רוחב $x$ מ', אורך $x+3$ מ'. שטח: $x(x+3)=40\\Rightarrow x^2+3x-40=0$. $\\Delta=169$, $x=5$ (דוחים רוחב שלילי). רוחב 5 מ', אורך 8 מ'. בדיקה: $5\\times8=40$ ✓.",
        "בעיות מילים: הגדרת משתנה, סקיצה, משוואה מיחסים, פתרון, **דחייה** של שורשים לא-פיזיים (אורך שלילי).",
        "שימוש בהיקף במקום שטח, או $x=-8$ בלי דחייה. טעות ב-$\\Delta=9+160=169$ — חיבור $b^2$ עם $-4ac$.",
        "כתבו 'רוחב = …, אורך = …' עם יחידות. הציבו ב**יחס המילולי** המקורי $x(x+3)=40$ לאימות סופי.",
    ),
    8: fmt_expl(
        "Multiply by $6x(x+1)$: $6(x+1)+6x=5x(x+1)\\Rightarrow 12x+6=5x^2+5x\\Rightarrow 5x^2-7x-6=0$. $\\Delta=49+120=169$, $x=\\dfrac{7\\pm13}{10}$, so $x=2$ or $x=-\\dfrac{3}{5}$. Check denominators: both avoid $x=0,-1$.",
        "Rational equations → clear denominators → quadratic. **Domain restriction:** exclude values that zero any denominator before and after — discard roots that violate domain.",
        "Clearing denominators incorrectly, or accepting $x=0$ which zeros the original denominators. Sign errors on $-7x-6$.",
        "After solving, state 'both roots valid' or list excluded values. Bagrut often adds one extraneous root — verify in original equation.",
        "כפל ב-$6x(x+1)$: $12x+6=5x^2+5x\\Rightarrow 5x^2-7x-6=0$. $\\Delta=169$, $x=\\dfrac{7\\pm13}{10}$, $x=2$ או $x=-\\dfrac{3}{5}$. בדיקת מכנים: שניהם לא $0$ או $-1$.",
        "משוואות רציונליות → ניקוי מכנים → ריבועית. **תחום:** הוציאו ערכים שמאפסים מכנה — דחו שורשים שמפרים את התחום.",
        "ניקוי מכנים שגוי, או $x=0$ שמאפס מכנים במשוואה המקורית. שגיאות סימן ב-$5x^2-7x-6$ אחרי הרחבה.",
        "אחרי פתרון, ציינו 'שני השורשים תקינים' או רשימת ערכים אסורים. בדקו הצבה במשוואה המקורית עם השברים.",
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
        "Quadratic equations: standard form, discriminant, factoring, quadratic formula, "
        "parametric root conditions, and word-problem setup with verification."
    )
    data["summary_he"] = (
        "משוואות ריבועיות: צורה סטנדרטית, דיסקרימיננטה, פירוק, נוסחת שורשים, "
        "תנאי שורשים פרמטריים, ובניית בעיות מילוליות עם אימות."
    )

    section_map = {
        "intro": (INTRO_EN, INTRO_HE),
        "definition": (DEF_EN, DEF_HE),
        "theory": (THEORY_EN, THEORY_HE),
        "method_guide": (METHOD_EN, METHOD_HE),
        "pitfall": (PITFALL_EN, PITFALL_HE),
        "before_exam": (BEFORE_EN, BEFORE_HE),
        "summary": (SUMMARY_EN, SUMMARY_HE),
    }

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in section_map:
            sec["body_en_md"], sec["body_he_md"] = section_map[kind]
        elif kind == "worked_example":
            n = sec.get("example_number", 1)
            if n == 1:
                sec["body_en_md"], sec["body_he_md"] = WE1_EN, WE1_HE
            elif n == 2:
                sec["body_en_md"], sec["body_he_md"] = WE2_EN, WE2_HE
            elif n == 3:
                sec["body_en_md"], sec["body_he_md"] = WE3_EN, WE3_HE
        elif kind == "checkpoint":
            if "x^2 - 7x + 12" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CHK1_EN
                sec["checkpoint_solution_he"] = CHK1_HE
            else:
                sec["checkpoint_solution_en"] = CHK2_EN
                sec["checkpoint_solution_he"] = CHK2_HE
        elif kind == "why_matters":
            sec["body_en_md"], sec["body_he_md"] = WHY_EN, WHY_HE

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
    print("All depth gates OK; seed-lessons dry-run passed.")


if __name__ == "__main__":
    main()
