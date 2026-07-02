#!/usr/bin/env python3
"""Expand functions_intro.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/functions_intro.json"

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


SECTION_BODIES = {
    "intro": {
        "body_en_md": """A **function** is a rule that assigns to each input exactly one output. Think of it as a machine: you feed in a number $x$, the function applies its rule, and out comes a single value $f(x)$. If one input could produce two different outputs, the rule is **not** a function — that violates the core definition.

**Real-life examples:**
- Each student's ID number maps to exactly one final grade (a function).
- A vending machine: press button A3 → receive one specific snack (a function).
- **Not** a function: one ID number linked to two different official grades in the same course.

Functions are the central object of study from algebra through calculus. Every graph you sketch, every equation you solve, and every physics formula you use can be viewed through the lens of "input → output." In Israeli Bagrut (3–4 units), function questions test domain restrictions, evaluation $f(a)$, composition $f(g(x))$, and the vertical line test on graphs. Mastering notation and domain rules here unlocks `concept:functions_linear`, `concept:analytic_geometry`, and later calculus topics.""",
        "body_he_md": """**פונקציה** היא כלל שמשייך לכל קלט בדיוק פלט אחד. דמיינו מכונה: מזינים מספר $x$, הפונקציה מפעילה את הכלל, ויוצא ערך יחיד $f(x)$. אם קלט אחד יכול לייצר שני פלטים שונים — זו **לא** פונקציה, כי זה סותר את ההגדרה.

**דוגמאות מהחיים:**
- מספר ת.ז. של תלמיד → ציון סופי יחיד (פונקציה).
- מכונת ממכר: לוחצים על כפתור A3 → מקבלים חטיף ספציפי אחד (פונקציה).
- **לא** פונקציה: ת.ז. אחת המקושרת לשני ציונים רשמיים שונים באותו קורס.

פונקציות הן האובייקט המרכזי בלימוד מעבר לאלגברה ועד חדו"א. כל גרף, כל משוואה וכל נוסחה בפיזיקה ניתנים לראייה כ"קלט → פלט". בבגרות (3–4 יחידות) בודקים הגבלות תחום, חישוב $f(a)$, הרכבה $f(g(x))$ ומבחן הישר האנכי על גרפים. שליטה בסימון ובכללי תחום כאן פותחת את `concept:functions_linear`, `concept:analytic_geometry` ונושאי חדו"א בהמשך.""",
    },
    "definition": {
        "body_en_md": """**Function:** A relation $f: A \\to B$ assigns to each element $x \\in A$ exactly one value $f(x) \\in B$. The set $A$ is the **domain**; $B$ is the **codomain** (the target set). The **range** is the set of values actually produced: $\\{f(x) : x \\in A\\}$.

**Domain restrictions for algebraic functions:**
- **Denominator:** set every denominator equal to zero and exclude those $x$-values. For $\\dfrac{1}{x-5}$, exclude $x=5$.
- **Even roots (square root, fourth root):** the expression under the root must be $\\ge 0$. For $\\sqrt{x-4}$, require $x-4 \\ge 0$.
- **Combined:** both rules apply simultaneously — find the intersection of allowed values.

**Notation:** $f(x)$ reads "the value of $f$ at $x$." The symbol $f(3)$ means substitute $x=3$ into the formula. $f(a+1)$ means replace **every** $x$ with $(a+1)$ — not add $1$ to $f(x)$.

**Vertical Line Test:** A graph in the $xy$-plane represents a function if and only if every vertical line $x=c$ intersects the graph **at most once**. Circles and sideways parabolas fail this test because one $x$ maps to two $y$-values.

**Table and arrow diagrams:** A table of $(x, f(x))$ pairs defines a function when no $x$ repeats with different $f(x)$ values. Arrow diagrams from domain to range must have exactly one arrow leaving each input.""",
        "body_he_md": """**פונקציה:** יחס $f: A \\to B$ משייך לכל $x \\in A$ בדיוק ערך אחד $f(x) \\in B$. הקבוצה $A$ היא **התחום**; $B$ היא **קבוצת היעד**. **הטווח** הוא קבוצת הערכים שבפועל מתקבלים: $\\{f(x) : x \\in A\\}$.

**הגבלות תחום בפונקציות אלגבריות:**
- **מכנה:** משווים כל מכנה לאפס ומוציאים את ערכי $x$ האלה. ב-$\\dfrac{1}{x-5}$ מוציאים $x=5$.
- **שורש זוגי (ריבועי, רביעי):** הביטוי תחת השורש חייב להיות $\\ge 0$. ב-$\\sqrt{x-4}$ נדרש $x-4 \\ge 0$.
- **משולב:** שני הכללים יחד — מוצאים את חיתוך הערכים המותרים.

**סימון:** $f(x)$ פירושו "ערך $f$ ב-$x$." הסימן $f(3)$ אומר להציב $x=3$ בנוסחה. $f(a+1)$ פירושו להחליף **כל** $x$ ב-$(a+1)$ — לא להוסיף $1$ ל-$f(x)$.

**מבחן הישר האנכי:** גרף במישור $xy$ מייצג פונקציה אמ"מ כל ישר אנכי $x=c$ חותך את הגרף **לכל היותר פעם אחת**. מעגלים ופרבולות שוכבות נכשלים כי $x$ אחד מתאים לשני ערכי $y$.

**טבלאות ודיאגרמות חצים:** טבלת זוגות $(x, f(x))$ מגדירה פונקציה כשאין $x$ שחוזר עם $f(x)$ שונה. בדיאגרמת חצים מן התחום לטווח — מכל קלט יוצא בדיוק חץ אחד.""",
    },
    "theory": {
        "body_en_md": """Beyond evaluation, functions combine through **arithmetic** and **composition**.

**Arithmetic on functions** (shared domain required):
$$(f+g)(x)=f(x)+g(x), \\quad (f-g)(x)=f(x)-g(x),$$
$$(f\\cdot g)(x)=f(x)\\cdot g(x), \\quad \\left(\\frac{f}{g}\\right)(x)=\\frac{f(x)}{g(x)} \\text{ where } g(x)\\ne0.$$

**Composition:** $(f\\circ g)(x)=f(g(x))$ — apply $g$ first, then feed the result into $f$. Order matters: $(f\\circ g)(x) \\ne (g\\circ f)(x)$ in general. Read "$f$ composed with $g$" as "start with $g$."

**Equality of functions:** $f=g$ if and only if they share the same domain and $f(x)=g(x)$ for every $x$ in that domain. Two formulas that look different may define the same function after simplification.

**Evaluating $f(a+1)$ vs. $f(x)+1$:** For $f(x)=x^2$, we have $f(x+1)=(x+1)^2=x^2+2x+1$, but $f(x)+1=x^2+1$. These differ by $2x$ — a classic exam trap.

**Finding inputs from outputs:** To solve $f(x)=c$, set the formula equal to $c$ and solve for $x$. For $f(x)=x^2$, the equation $x^2=25$ gives $x=\\pm5$ because squaring is not one-to-one.

**Range analysis:** For simple functions, describe all possible outputs. $f(x)=x^2$ has range $[0,\\infty)$ on $\\mathbb{R}$. $|x|$ also outputs non-negative values. Rational functions require analyzing asymptotes and excluded values.

**Inverse preview:** Functions $f$ and $g$ are inverses when $f(g(x))=x$ and $g(f(x))=x$ on their domains — composition returning the identity.""",
        "body_he_md": """מעבר להצבה, פונקציות משתלבות ב**חשבון** וב**הרכבה**.

**פעולות חשבון על פונקציות** (נדרש תחום משותף):
$$(f+g)(x)=f(x)+g(x), \\quad (f-g)(x)=f(x)-g(x),$$
$$(f\\cdot g)(x)=f(x)\\cdot g(x), \\quad \\left(\\frac{f}{g}\\right)(x)=\\frac{f(x)}{g(x)} \\text{ כאשר } g(x)\\ne0.$$

**הרכבה:** $(f\\circ g)(x)=f(g(x))$ — מפעילים קודם $g$, ואז מזינים את התוצאה ל-$f$. הסדר חשוב: $(f\\circ g)(x) \\ne (g\\circ f)(x)$ בדרך כלל. "$f$ מורכבת עם $g$" = "מתחילים מ-$g$."

**שוויון פונקציות:** $f=g$ אמ"מ יש להן אותו תחום ו-$f(x)=g(x)$ לכל $x$ בתחום. שתי נוסחאות שנראות שונה עלולות להגדיר אותה פונקציה אחרי פישוט.

**$f(a+1)$ לעומת $f(x)+1$:** עבור $f(x)=x^2$, מתקבל $f(x+1)=(x+1)^2=x^2+2x+1$, אבל $f(x)+1=x^2+1$. ההפרש הוא $2x$ — מלכודת בחינה קלאסית.

**מציאת קלט מתוצאה:** לפתרון $f(x)=c$ משווים את הנוסחה ל-$c$ ופותרים עבור $x$. ב-$f(x)=x^2$, המשוואה $x^2=25$ נותנת $x=\\pm5$ כי העלאה בריבוע אינה חד-חד-ערכית.

**ניתוח טווח:** בפונקציות פשוטות מתארים את כל הפלטים האפשריים. ל-$f(x)=x^2$ הטווח הוא $[0,\\infty)$ על $\\mathbb{R}$. גם $|x|$ מוציא ערכים לא-שליליים. בפונקציות רציונליות בודקים אסימптוטות וערכים מוחרגים.

**תצוגה מקדימה של הופכיות:** $f$ ו-$g$ הופכיות כאשר $f(g(x))=x$ ו-$g(f(x))=x$ בתחומן — הרכבה שמחזירה את פונקציית הזהות.""",
    },
}

WE1_EN = """**Given** $f(x)=\\dfrac{x+1}{x-3}$.

This rational function combines domain analysis (denominator) with direct evaluation and substitution of expressions for $x$.

### Move 1: Find the domain
The denominator $x-3$ cannot be zero, so $x \\ne 3$. Domain: $\\mathbb{R}\\setminus\\{3\\}$ — all real numbers except $3$.

### Move 2: Evaluate $f(0)$
Substitute $x=0$: $f(0)=\\dfrac{0+1}{0-3}=\\dfrac{1}{-3}=-\\dfrac{1}{3}$.

### Move 3: Evaluate $f(5)$
$f(5)=\\dfrac{5+1}{5-3}=\\dfrac{6}{2}=3$. Quick check: $5$ is in the domain because $5 \\ne 3$ ✓.

### Move 4: Evaluate $f(a^2)$
Replace $x$ with $a^2$ everywhere: $f(a^2)=\\dfrac{a^2+1}{a^2-3}$. This is valid when $a^2 \\ne 3$, i.e. $a \\ne \\pm\\sqrt{3}$.

### Move 5: Quick domain sanity check
Pick a value in the domain, e.g. $x=1$: $f(1)=\\dfrac{2}{-2}=-1$ ✓. Pick the excluded value: $f(3)$ would divide by zero — undefined ✓.

**Strategy note:** When the input is an expression (not just a number), substitute the entire expression into **every** $x$ in the formula — numerator and denominator. On Bagrut, domain questions often hide inside evaluation items: always check whether your $x$-value is allowed before computing. Rational functions like this appear again when sketching graphs with vertical asymptotes at excluded $x$-values."""

WE1_HE = """**נתון** $f(x)=\\dfrac{x+1}{x-3}$.

פונקציה רציונלית זו משלבת ניתוח תחום (מכנה) עם הצבה ישירה והצבת ביטויים במקום $x$.

### צעד 1: מציאת התחום
המכנה $x-3$ לא יכול להיות אפס, לכן $x \\ne 3$. תחום: $\\mathbb{R}\\setminus\\{3\\}$ — כל הממשיים חוץ מ-$3$.

### צעד 2: חישוב $f(0)$
מציבים $x=0$: $f(0)=\\dfrac{0+1}{0-3}=\\dfrac{1}{-3}=-\\dfrac{1}{3}$.

### צעד 3: חישוב $f(5)$
$f(5)=\\dfrac{5+1}{5-3}=\\dfrac{6}{2}=3$. בדיקה: $5$ בתחום כי $5 \\ne 3$ ✓.

### צעד 4: חישוב $f(a^2)$
מחליפים $x$ ב-$a^2$ בכל מקום: $f(a^2)=\\dfrac{a^2+1}{a^2-3}$. תקף כאשר $a^2 \\ne 3$, כלומר $a \\ne \\pm\\sqrt{3}$.

### צעד 5: בדיקת תחום מהירה
בוחרים ערך בתחום, למשל $x=1$: $f(1)=\\dfrac{2}{-2}=-1$ ✓. בערך המוחרג: $f(3)$ יחלק באפס — לא מוגדר ✓.

**הערת אסטרטגיה:** כשהקלט הוא ביטוי (לא רק מספר), מציבים את כל הביטוי ב**כל** $x$ בנוסחה — מונה ומכנה. בבגרות, שאלות תחום לעיתים מוסתרות בתוך הצבות — תמיד בודקים אם ערך $x$ מותר לפני החישוב. פונקציות רציונליות כמו זו חוזרות בשרטוט גרפים עם אסימптוטות אנכיות בערכי $x$ מוחרגים."""

WE2_EN = """**Given** $f(x)=2x+1$ and $g(x)=x^2-3$.

Composition tests whether you apply the **inner** function first and respect order. These are simple formulas on purpose — the exam tests **process**, not heavy algebra.

### Move 1: Compute $(f\\circ g)(x)$
$(f\\circ g)(x)=f(g(x))$. First find $g(x)=x^2-3$, then plug into $f$:
$$f(x^2-3)=2(x^2-3)+1=2x^2-6+1=2x^2-5.$$

### Move 2: Compute $(g\\circ f)(x)$
$(g\\circ f)(x)=g(f(x))$. First $f(x)=2x+1$, then:
$$g(2x+1)=(2x+1)^2-3=4x^2+4x+1-3=4x^2+4x-2.$$

### Move 3: Compare the formulas side by side
$(f\\circ g)(x)=2x^2-5$ is quadratic with no $x$ term. $(g\\circ f)(x)=4x^2+4x-2$ has a linear term — clearly different polynomials.

### Move 4: Compare at $x=3$
$(f\\circ g)(3)=f(6)=13$ but $(g\\circ f)(3)=g(7)=46$. Different numbers confirm non-commutativity.

### Move 5: Verify at $x=1$
For $(f\\circ g)(1)$: $g(1)=-2$, then $f(-2)=2(-2)+1=-3$. For $(g\\circ f)(1)$: $f(1)=3$, then $g(3)=6$. Again, different results.

**Why order matters:** $(f\\circ g)$ means "do $g$ then $f$" — read the circle notation from **right to left** in the input pipeline. Exam items often ask for a numeric value like $(f\\circ g)(3)$: compute $g(3)$ first, then apply $f$ to that result. Composition is a prerequisite for inverse functions and for chaining transformations in `concept:function_transformations`."""

WE2_HE = """**נתון** $f(x)=2x+1$ ו-$g(x)=x^2-3$.

הרכבה בודקת אם מפעילים קודם את הפונקציה **הפנימית** ומכבדים את הסדר. הנוסחאות פשוטות בכוונה — הבחינה בודקת **תהליך**, לא אלגברה כבדה.

### צעד 1: חישוב $(f\\circ g)(x)$
$(f\\circ g)(x)=f(g(x))$. קודם $g(x)=x^2-3$, ואז מציבים ב-$f$:
$$f(x^2-3)=2(x^2-3)+1=2x^2-6+1=2x^2-5.$$

### צעד 2: חישוב $(g\\circ f)(x)$
$(g\\circ f)(x)=g(f(x))$. קודם $f(x)=2x+1$, ואז:
$$g(2x+1)=(2x+1)^2-3=4x^2+4x+1-3=4x^2+4x-2.$$

### צעד 3: השוואת הנוסחאות
$(f\\circ g)(x)=2x^2-5$ — ריבועית בלי איבר $x$. $(g\\circ f)(x)=4x^2+4x-2$ — יש איבר לינארי; פולינומים שונים בבירור.

### צעד 4: השוואה ב-$x=3$
$(f\\circ g)(3)=f(6)=13$ אבל $(g\\circ f)(3)=g(7)=46$. מספרים שונים מאשרים שהסדר אינו ניתן להחלפה.

### צעד 5: אימות ב-$x=1$
עבור $(f\\circ g)(1)$: $g(1)=-2$, ואז $f(-2)=-3$. עבור $(g\\circ f)(1)$: $f(1)=3$, ואז $g(3)=6$. שוב תוצאות שונות.

**למה הסדר חשוב:** $(f\\circ g)$ = "קודם $g$ ואז $f$" — קוראים את סימון העיגול מ**ימין לשמאל** בשרשרת הקלט. בבחינה לעיתים מבקשים ערך מספרי כמו $(f\\circ g)(3)$: מחשבים $g(3)$ קודם, ואז $f$ על התוצאה. הרכבה היא תנאי מוקדם לפונקציות הופכיות ולשרשראות טרנספורמציות ב-`concept:function_transformations`."""

WE3_EN = """**Given** $f(x)=x^2-3x+2$ and $g(x)=2x-1$. Find all $x$ such that $f(g(x))=0$.

This exam-level item chains composition with solving a quadratic — a standard Bagrut pattern. The key insight: solve the **outer** equation first in a temporary variable, then back-substitute through the inner function.

### Move 1: Set up the composition equation
$f(g(x))=0$ means: compute $g(x)$, plug into $f$, and set the result to zero. Let $u=g(x)=2x-1$. Then $f(u)=u^2-3u+2=0$.

### Move 2: Solve $f(u)=0$
$$u^2-3u+2=(u-1)(u-2)=0 \\Rightarrow u=1 \\text{ or } u=2.$$
Factor the quadratic — both roots are needed before back-substitution.

### Move 3: Back-substitute Case A
$g(x)=1 \\Rightarrow 2x-1=1 \\Rightarrow 2x=2 \\Rightarrow x=1$.

### Move 4: Back-substitute Case B
$g(x)=2 \\Rightarrow 2x-1=2 \\Rightarrow 2x=3 \\Rightarrow x=\\dfrac{3}{2}$.

### Move 5: Verify both solutions
$f(g(1))=f(1)=1-3+2=0$ ✓. $f(g(3/2))=f(2)=4-6+2=0$ ✓. Both branches produce valid zeros.

**Solutions:** $x=1$ or $x=\\dfrac{3}{2}$. Always check both branches — missing one root is a common partial-credit loss on Bagrut composition problems. This same "outer quadratic, inner linear" structure appears when finding where composed graphs cross the $x$-axis."""

WE3_HE = """**נתון** $f(x)=x^2-3x+2$ ו-$g(x)=2x-1$. מצאו את כל $x$ כך ש-$f(g(x))=0$.

שאלה ברמת בחינה שמשרשרת הרכבה עם פתרון ריבועית — דפוס סטנדרטי בבגרות. התובנה המרכזית: פותרים קודם את משוואת **החיצונית** במשתנה זמני, ואז מציבים חזרה דרך הפונקציה הפנימית.

### צעד 1: הצבת משוואת ההרכבה
$f(g(x))=0$ פירושו: מחשבים $g(x)$, מציבים ב-$f$, ומשווים לאפס. נסמן $u=g(x)=2x-1$. אז $f(u)=u^2-3u+2=0$.

### צעד 2: פתרון $f(u)=0$
$$u^2-3u+2=(u-1)(u-2)=0 \\Rightarrow u=1 \\text{ או } u=2.$$
מפרקים את הריבועית — שני השורשים נדרשים לפני הצבה חוזרת.

### צעד 3: הצבה חוזרת — מקרה א
$g(x)=1 \\Rightarrow 2x-1=1 \\Rightarrow 2x=2 \\Rightarrow x=1$.

### צעד 4: הצבה חוזרת — מקרה ב
$g(x)=2 \\Rightarrow 2x-1=2 \\Rightarrow 2x=3 \\Rightarrow x=\\dfrac{3}{2}$.

### צעד 5: אימות שני הפתרונות
$f(g(1))=f(1)=1-3+2=0$ ✓. $f(g(3/2))=f(2)=4-6+2=0$ ✓. שני הענפים נותנים אפסים תקפים.

**פתרונות:** $x=1$ או $x=\\dfrac{3}{2}$. תמיד בודקים את שני הענפים — החמצת שורש אחד גורמת לאיבוד נקודות חלקיות. אותו מבנה "ריבועית חיצונית, לינארית פנימית" מופיע כשמחפשים היכן גרפים מורכבים חוצים את ציר $x$."""

CP1_EN = """We need the domain of $g(x)=\\sqrt{5-2x}$.

**Step 1:** Identify the restriction. A square root requires the radicand (expression underneath) to be non-negative:
$$5-2x \\ge 0.$$

**Step 2:** Solve the inequality:
$$5 \\ge 2x \\Rightarrow x \\le \\dfrac{5}{2}.$$

**Step 3:** Write the domain in interval notation: $(-\\infty, \\dfrac{5}{2}]$. The endpoint $\\dfrac{5}{2}$ is included because $\\sqrt{5-2\\cdot(5/2)}=\\sqrt{0}=0$ is defined.

**Check:** Try $x=0$: $\\sqrt{5}$ ✓. Try $x=3$: $\\sqrt{-1}$ ✗ — confirms values above $5/2$ are excluded.

**Answer:** Domain is $(-\\infty, \\dfrac{5}{2}]$.""" 

CP1_HE = """נדרש תחום $g(x)=\\sqrt{5-2x}$.

**שלב 1:** מזהים את ההגבלה. שורש ריבועי דורש שהביטוי תחתיו יהיה לא-שלילי:
$$5-2x \\ge 0.$$

**שלב 2:** פותרים את אי-השוויון:
$$5 \\ge 2x \\Rightarrow x \\le \\dfrac{5}{2}.$$

**שלב 3:** כותבים תחום בסימון קטע: $(-\\infty, \\dfrac{5}{2}]$. נקודת הקצה $\\dfrac{5}{2}$ כלולה כי $\\sqrt{5-2\\cdot(5/2)}=\\sqrt{0}=0$ מוגדר.

**בדיקה:** $x=0$: $\\sqrt{5}$ ✓. $x=3$: $\\sqrt{-1}$ ✗ — מאשר שערכים מעל $5/2$ מוחרגים.

**תשובה:** התחום הוא $(-\\infty, \\dfrac{5}{2}]$."""

CP2_EN = """Find $(f\\circ g)(5)$ where $f(x)=\\sqrt{x}$ and $g(x)=x+4$.

**Step 1:** Apply the inner function first. $(f\\circ g)(5)=f(g(5))$.

**Step 2:** Compute $g(5)=5+4=9$.

**Step 3:** Feed the result into $f$: $f(9)=\\sqrt{9}=3$.

**Why not $f(5)$ first?** Composition order is fixed: $g$ runs before $f$. Swapping gives $(g\\circ f)(5)=g(\\sqrt{5})=\\sqrt{5}+4 \\ne 3$.

**Domain check:** $g(5)=9 \\ge 0$, so $\\sqrt{9}$ is defined ✓.

**Answer:** $(f\\circ g)(5)=3$."""

CP2_HE = """מצאו $(f\\circ g)(5)$ כאשר $f(x)=\\sqrt{x}$ ו-$g(x)=x+4$.

**שלב 1:** מפעילים קודם את הפונקציה הפנימית. $(f\\circ g)(5)=f(g(5))$.

**שלב 2:** $g(5)=5+4=9$.

**שלב 3:** מזינים ל-$f$: $f(9)=\\sqrt{9}=3$.

**למה לא $f(5)$ קודם?** סדר ההרכבה קבוע: $g$ לפני $f$. החלפה נותנת $(g\\circ f)(5)=g(\\sqrt{5})=\\sqrt{5}+4 \\ne 3$.

**בדיקת תחום:** $g(5)=9 \\ge 0$, לכן $\\sqrt{9}$ מוגדר ✓.

**תשובה:** $(f\\circ g)(5)=3$."""

METHOD_EN = """| Task | Action |
|---|---|
| Find domain | Denominator $\\ne 0$; radicand $\\ge 0$ under even roots |
| Evaluate $f(a)$ | Substitute $x=a$ into every $x$ in the formula |
| Solve $f(x)=c$ | Set formula equal to $c$; solve for $x$ |
| Compose $f\\circ g$ | Compute $g(x)$ first, then plug into $f$ |
| Vertical line test | Each $x$ has at most one $y$ on the graph |
| Find range | Collect all output values; analyze min/max or behavior |
| Check if relation is a function | No repeated $x$ with different $y$ in table or graph |

**When to use:** Read the problem type first — domain, evaluation, inverse output, composition, or graph test — then pick the matching row. Only substitute numbers after the structural step is chosen.

**Exam tip:** For combined restrictions (root **and** denominator), solve each inequality separately, then take the **intersection**. Write domain in interval notation with correct open/closed endpoints."""

METHOD_HE = """| משימה | פעולה |
|---|---|
| מציאת תחום | מכנה $\\ne 0$; תחת שורש זוגי $\\ge 0$ |
| חישוב $f(a)$ | הצב $x=a$ בכל $x$ בנוסחה |
| פתרון $f(x)=c$ | השווה ל-$c$; פתור עבור $x$ |
| הרכבה $f\\circ g$ | חשב $g(x)$ קודם, הצב ב-$f$ |
| מבחן ישר אנכי | לכל $x$ לכל היותר $y$ אחד על הגרף |
| מציאת טווח | אסוף כל ערכי הפלט; נתח מינ./מקס. |
| בדיקה אם יחס הוא פונקציה | אין $x$ חוזר עם $y$ שונה בטבלה או בגרף |

**מתי להשתמש:** קראו קודם את סוג הבעיה — תחום, הצבה, מציאת קלט מתוצאה, הרכבה או בדיקת גרף — ובחרו את השורה המתאימה. רק אחרי בחירת המבנה מציבים מספרים.

**טיפ לבחינה:** בהגבלות משולבות (שורש **וגם** מכנה) — פותרים כל אי-שוויון בנפרד, ואז **חיתוך**. כתבו תחום בסימון קטע עם נקודות קצה פתוחות/סגורות נכון."""

PITFALL_EN = """1. **Confusing $f(x+1)$ with $f(x)+1$.** In $f(x)=x^2$: $f(x+1)=(x+1)^2=x^2+2x+1$, but $f(x)+1=x^2+1$. The $+1$ inside the parentheses replaces $x$; outside adds to the output.

2. **Domain sign errors under roots.** For $\\sqrt{2-x}$: require $2-x \\ge 0$, so $x \\le 2$ — **not** $x \\ge 2$. Students often flip the inequality direction.

3. **Not every graph is a function.** A circle fails the vertical line test because one $x$ gives two $y$-values. Sideways parabolas $x=y^2$ also fail.

4. **Composition order reversed.** $(f\\circ g)(x)=f(g(x))$ means $g$ first. Writing $g(f(x))$ when asked for $f\\circ g$ is a full wrong answer even if arithmetic is correct.

5. **Forgetting domain when evaluating.** $f(3)$ for $f(x)=1/(x-3)$ is undefined — always verify the input lies in the domain before computing.

**Fix habit:** Before evaluating, ask: "Is this $x$ allowed?" Before composing, ask: "Which function runs first?" """

PITFALL_HE = """1. **בלבול $f(x+1)$ עם $f(x)+1$.** ב-$f(x)=x^2$: $f(x+1)=(x+1)^2=x^2+2x+1$, אבל $f(x)+1=x^2+1$. ה-$+1$ **בתוך** הסוגריים מחליף את $x$; **מחוץ** מוסיף לפלט.

2. **טעויות סימן בתחום תחת שורש.** ב-$\\sqrt{2-x}$: נדרש $2-x \\ge 0$, לכן $x \\le 2$ — **לא** $x \\ge 2$. תלמידים לעיתים הופכים את כיוון אי-השוויון.

3. **לא כל גרף הוא פונקציה.** מעגל נכשל במבחן הישר האנכי כי $x$ אחד נותן שני ערכי $y$. גם פרבולות שוכבות $x=y^2$ נכשלות.

4. **היפוך סדר הרכבה.** $(f\\circ g)(x)=f(g(x))$ = קודם $g$. כתיבת $g(f(x))$ כשמבקשים $f\\circ g$ = תשובה שגויה לגמרי גם אם החשבון נכון.

5. **שכחת תחום בהצבה.** $f(3)$ עבור $f(x)=1/(x-3)$ לא מוגדר — תמיד בודקים שהקלט בתחום לפני חישוב.

**הרגל תיקון:** לפני הצבה — "האם $x$ הזה מותר?" לפני הרכבה — "איזו פונקציה רצה קודם?" """

BEFORE_EXAM_EN = """- **Domain checklist:** denominator $\\ne 0$; expression under even root $\\ge 0$; combine with intersection.
- **Evaluate $f(a)$:** substitute $x=a$ everywhere in the formula — not just the first $x$ you see.
- **Composition $f\\circ g$:** inner function $g$ first, then outer $f$. For numbers: compute $g(\\text{value})$ then apply $f$.
- **Vertical line test:** graph is a function iff every vertical line hits at most once.
- **Range:** list or describe all possible outputs; $x^2$ on $\\mathbb{R}$ gives $[0,\\infty)$.
- **Solve $f(x)=c$:** set equal and solve; watch for $\\pm$ when inverting squares.

**Last review:** Say each rule out loud once, then solve one checkpoint without looking at notes."""

BEFORE_EXAM_HE = """- **רשימת תחום:** מכנה $\\ne 0$; תחת שורש זוגי $\\ge 0$; מצאו חיתוך.
- **הצבה $f(a)$:** הציבו $x=a$ בכל מקום בנוסחה — לא רק ב-$x$ הראשון.
- **הרכבה $f\\circ g$:** פנימית $g$ קודם, חיצונית $f$ אחר כך. במספרים: $g(\\text{ערך})$ ואז $f$.
- **מבחן ישר אנכי:** גרף הוא פונקציה אמ"מ כל ישר אנכי חותך לכל היותר פעם.
- **טווח:** רשימת כל הפלטים; $x^2$ על $\\mathbb{R}$ נותן $[0,\\infty)$.
- **פתרון $f(x)=c$:** השוו ופתרו; שימו לב ל-$\\pm$ בהפיכת ריבוע.

**חזרה אחרונה:** אמרו כל כלל בקול, ואז פתרו checkpoint אחד בלי להסתכל."""

SUMMARY_EN = """- A **function** assigns each input exactly one output.
- **Domain:** all valid inputs; **Range:** all actual outputs.
- Evaluate $f(a)$ by substituting $x=a$ into the entire formula.
- **Composition:** $(f\\circ g)(x)=f(g(x))$ — apply $g$ first; order matters.
- **Vertical line test:** at most one $y$ per $x$ on a graph.
- Domain rules: denominator $\\ne 0$; radicand $\\ge 0$ under even roots.

**Takeaway:** You should now recognize whether a problem asks for domain, evaluation, composition, or graph analysis — and pick the method before substituting numbers."""

SUMMARY_HE = """- **פונקציה** משייכת לכל קלט בדיוק פלט אחד.
- **תחום:** כל הקלטים הכשרים; **טווח:** כל הפלטים בפועל.
- $f(a)$: הצב $x=a$ בכל הנוסחה.
- **הרכבה:** $(f\\circ g)(x)=f(g(x))$ — קודם $g$; הסדר חשוב.
- **מבחן ישר אנכי:** לכל $x$ לכל היותר $y$ אחד.
- כללי תחום: מכנה $\\ne 0$; תחת שורש זוגי $\\ge 0$.

**מסקנה:** כעת תזהו אם השאלה על תחום, הצבה, הרכבה או ניתוח גרף — ותבחרו שיטה לפני הצבת מספרים."""

WHY_MATTERS_EN = """Functions are the language of every advanced math and physics course on A Step Forward. Without solid domain, evaluation, and composition skills, later topics — linear and quadratic graphs, trigonometric models, calculus limits — all become harder than they need to be.

**You will use this to unlock:**
- `concept:analytic_geometry` **Analytic Geometry — Advanced (Conic Sections)** (prereq)
- `concept:functions_linear` **Linear Functions** (direct next step)
- `concept:function_transformations` **Function Transformations**

**Builds on:** `concept:equations_linear` and `concept:algebra_basics` — solving $f(x)=c$ is solving an equation.

**Why it matters for exams:** Bagrut 3–4 unit papers routinely mix domain, evaluation, and composition in one multi-part question. University calculus assumes you can compose functions and read $f(g(x))$ without hesitation. When you study, ask: "Where else did I see input → output thinking?" — kinematics, probability tables, and graph sketches all use the same function framework."""

WHY_MATTERS_HE = """פונקציות הן שפת כל קורס מתמטיקה ופיזיקה מתקדם ב-A Step Forward. בלי שליטה בתחום, הצבה והרכבה — נושאים מאוחרים כמו גרפים לינאריים וריבועיים, מודלים טריגונומטריים וגבולות בחדו"א נהיים קשים יותר מהצורך.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:analytic_geometry` **גיאומטריה אנליטית — מתקדם (חתכי חרוט)** (prereq)
- `concept:functions_linear` **פונקציות לינאריות** (הצעד הבא)
- `concept:function_transformations` **טרנספורמציות של פונקציות**

**מבוסס על:** `concept:equations_linear` ו-`concept:algebra_basics` — פתרון $f(x)=c$ הוא פתרון משוואה.

**למה זה חשוב לבחינות:** בבגרות 3–4 יחידות משלבים לעיתים תחום, הצבה והרכבה בשאלה אחת רב-סעיפית. בחדו"א באוניברסיטה מניחים שאתם קוראים $f(g(x))$ בלי היסוס. בזמן לימוד שאלו: "איפה עוד ראיתי חשיבה של קלט → פלט?" — קינמטיקה, טבלאות הסתברות ושרטוטי גרף משתמשים באותו מסגרת פונקציה."""

EXPLANATIONS = [
    fmt_expl(
        "The domain excludes values that make the denominator zero. For $f(x)=\\dfrac{1}{x-5}$, set $x-5=0$, giving $x=5$. Every other real number is valid input, so the domain is $\\mathbb{R}\\setminus\\{5\\}$.",
        "Start every rational-function domain problem by listing restrictions: denominators $\\ne 0$, radicands $\\ge 0$. Here only the denominator applies. The answer is 'all reals except 5' — not 'all reals' and not 'only $x>5$'.",
        "Choosing $\\mathbb{R}$ ignores the hole at $x=5$. Choosing $x>5$ or $x<5$ treats the domain as one-sided when both sides except $5$ work. Another error: writing $x \\ne -5$ from misreading $x-5$.",
        "On Bagrut, domain answers in interval/set notation must match exactly. Quick check: substitute a value near the excluded point — $f(4.9)$ should work, $f(5)$ should not.",
        "התחום מוציא ערכים שהופכים את המכנה לאפס. ב-$f(x)=\\dfrac{1}{x-5}$ משווים $x-5=0$ ומקבלים $x=5$. כל שאר הממשיים תקפים, לכן התחום $\\mathbb{R}\\setminus\\{5\\}$.",
        "בכל בעיית תחום של פונקציה רציונלית — רשימת הגבלות: מכנים $\\ne 0$, תחת שורש $\\ge 0$. כאן רק המכנה רלוונטי. התשובה: 'כל הממשיים חוץ מ-5' — לא 'כל הממשיים' ולא 'רק $x>5$'.",
        "בחירה ב-$\\mathbb{R}$ מתעלמת מהחור ב-$x=5$. בחירה ב-$x>5$ או $x<5$ מתייחסת לתחום חד-צדדי כששני הצדדים חוץ מ-5 תקפים. טעות נוספת: $x \\ne -5$ מקריאה שגויה.",
        "בבגרות, תשובת תחום בסימון קטע/קבוצה חייבת להתאים בדיוק. בדיקה: הציבו ליד הנקודה המוחרגת — $f(4.9)$ עובד, $f(5)$ לא.",
    ),
    fmt_expl(
        "Substitute directly: $f(2)=3(2)-5=6-5=1$ and $f(-1)=3(-1)-5=-3-5=-8$. Function evaluation means replacing every $x$ in the formula with the given number.",
        "Read $f(2)$ as 'the output when the input is 2.' Write the formula, replace $x$ with 2, follow order of operations. Do both parts separately — exam items often ask for two values in one question.",
        "Arithmetic slips: $3(-1)=3$ instead of $-3$, or $6-5=1$ computed as $11$. Another error: reporting only one of the two requested values.",
        "After computing, verify by mental check: $f(2)=1$ means input 2 gives output 1. If your $f(-1)$ is positive, re-check the negative multiplication.",
        "הצבה ישירה: $f(2)=3(2)-5=6-5=1$ ו-$f(-1)=3(-1)-5=-3-5=-8$. חישוב ערך פונקציה = החלפת כל $x$ במספר הנתון.",
        "קראו $f(2)$ כ'פלט כשהקלט 2'. כתבו נוסחה, החליפו $x$ ב-2, סדר פעולות. כל חלק בנפרד — בבחינה לעיתים שני ערכים בשאלה אחת.",
        "טעויות חישוב: $3(-1)=3$ במקום $-3$, או $6-5=11$. טעות נוספת: דיווח על ערך אחד בלבד.",
        "אחרי החישוב — $f(2)=1$ אומר קלט 2 נותן פלט 1. אם $f(-1)$ יצא חיובי, בדקו שוב כפל במינוס.",
    ),
    fmt_expl(
        "Under a square root, the radicand must be non-negative: $x-4 \\ge 0$, so $x \\ge 4$. Domain in interval notation: $[4, \\infty)$ — closed at 4 because $\\sqrt{0}$ is defined.",
        "Identify the restriction type first: this is a root problem, not a denominator problem. Solve the inequality, then express as an interval. The boundary $x=4$ is included.",
        "Writing $(4, \\infty)$ excludes 4 incorrectly. Writing $x \\le 4$ flips the inequality. Some students answer '4' alone instead of the full interval.",
        "Test endpoints: $x=4$ gives $\\sqrt{0}=0$ ✓; $x=3$ gives $\\sqrt{-1}$ ✗. One test confirms direction and bracket type.",
        "תחת שורש ריבועי הביטוי חייב להיות לא-שלילי: $x-4 \\ge 0$, לכן $x \\ge 4$. תחום: $[4, \\infty)$ — סגור ב-4 כי $\\sqrt{0}$ מוגדר. זהו סוג מגבלה שונה ממכנה — כאן אין חלוקה, רק דרישת שורש.",
        "זיהו סוג הגבלה: בעיית שורש, לא מכנה. פתרו אי-שוויון, ביטוי כקטע. נקודת $x=4$ כלולה כי $\\sqrt{0}=0$ מוגדר.",
        "כתיבת $(4, \\infty)$ מוציאה את 4 בטעות. $x \\le 4$ הופך כיוון. חלק עונים '4' בלבד במקום הקטע המלא.",
        "בדיקת קצוות: $x=4$ → $\\sqrt{0}=0$ ✓; $x=3$ → $\\sqrt{-1}$ ✗. בדיקה אחת מאשרת כיוון וסוג סוגר. בבגרות, כתבו תמיד קטע מלא — לא רק אי-שוויון.",
    ),
    fmt_expl(
        "A function requires each input to map to exactly one output. The set $\\{(1,2),(2,2),(3,5)\\}$ has distinct first coordinates (1, 2, 3) each paired with a single second coordinate — even though $y=2$ repeats, different $x$-values sharing the same $y$ is allowed.",
        "Check the **first** coordinate (inputs) for repeats with different outputs. Repeating outputs ($y=2$ twice) is fine; repeating inputs with different outputs is not. Tables and arrow diagrams use the same rule.",
        "Students reject the set because $y=2$ appears twice — but that is permitted. The failure case would be $(1,2)$ and $(1,5)$ in the same set.",
        "Bagrut sometimes uses arrow diagrams: one arrow per domain element. If every student ID has exactly one grade arrow, it is a function.",
        "פונקציה דורשת שכל קלט מתאים לפלט יחיד. ב-$\\{(1,2),(2,2),(3,5)\\}$ הקואורדינטות הראשונות (1, 2, 3) שונות, כל אחת עם קואורדינטה שנייה אחת — גם אם $y=2$ חוזר, $x$ שונים עם אותו $y$ מותר.",
        "בדקו חזרות בקואורדינטה **ראשונה** (קלטים). חזרה על פלט ($y=2$ פעמיים) מותרת; חזרה על קלט עם פלטים שונים — לא. אותו כלל בטבלאות וחצים.",
        "תלמידים דוחים כי $y=2$ מופיע פעמיים — אבל זה מותר. כישלון = $(1,2)$ ו-$(1,5)$ באותה קבוצה.",
        "בבגרות לעיתים דיאגרמת חצים: חץ אחד לכל איבר בתחום. אם לכל ת.ז. יש חץ ציון אחד — זו פונקציה.",
    ),
    fmt_expl(
        "Set $x^2=25$ and solve: $x=5$ or $x=-5$, written $x=\\pm 5$. Both satisfy $f(x)=25$ because $(-5)^2=25$ and $5^2=25$.",
        "Solving $f(x)=c$ means inverting the function rule. For squares, expect two solutions unless $c<0$ (no real solution). Always check both roots by squaring.",
        "Giving only $x=5$ and forgetting $-5$ is the most common loss. Another error: $x=\\pm 25$ from dividing instead of taking square roots.",
        "When $f(x)=x^2$ and $c>0$, write $\\pm\\sqrt{c}$ immediately. On Bagrut, partial credit often requires both roots explicitly.",
        "משווים $x^2=25$: $x=5$ או $x=-5$, כלומר $x=\\pm 5$. שניהם מקיימים $f(x)=25$ כי $(-5)^2=25$ ו-$5^2=25$. אל תשכחו את השורש השלילי — זו מלכודת נפוצה בבגרות.",
        "פתרון $f(x)=c$ = היפוך כלל הפונקציה. בריבוע — שני פתרונות אלא אם $c<0$. בדקו שני שורשים בהעלאה בריבוע.",
        "מתן $x=5$ בלבד בלי $-5$ — איבוד נפוץ. טעות: $x=\\pm 25$ מחילוק במקום שורש.",
        "כש-$f(x)=x^2$ ו-$c>0$, כתבו $\\pm\\sqrt{c}$ מיד. בבגרות — נקודות חלקיות דורשות שני שורשים במפורש. בדיקה: $(-5)^2=25$ ✓.",
    ),
    fmt_expl(
        "Factor the denominator: $x^2-4=(x-2)(x+2)$. Set each factor to zero: $x \\ne 2$ and $x \\ne -2$. Domain: $\\mathbb{R}\\setminus\\{-2, 2\\}$.",
        "Denominator restrictions come from zeros of the bottom polynomial. Factor when possible to find **all** excluded values — unfactored form hides both holes at $\\pm 2$.",
        "Missing $x=-2$ after only excluding $x=2$ is typical. Some write $x \\ne 4$ from confusing $x^2-4$ with $x-4$.",
        "List exclusions in increasing order: $-2, 2$. Verify: $f(0)=-1/4$ works; $f(2)$ and $f(-2)$ are undefined.",
        "מפרקים מכנה: $x^2-4=(x-2)(x+2)$. כל גורם לאפס: $x \\ne 2$ ו-$x \\ne -2$. תחום: $\\mathbb{R}\\setminus\\{-2, 2\\}$. שני החורים חיוניים — לא מספיק להוציא רק $x=2$.",
        "הגבלות מכנה מגיעות מאפסים של הפולינום למטה. פירוק חושף **כל** הערכים המוחרגים — בלי פירוק מפספסים $\\pm 2$.",
        "החמצת $x=-2$ אחרי $x \\ne 2$ בלבד — טיפוסי. חלק כותבים $x \\ne 4$ מבלבול $x^2-4$ עם $x-4$.",
        "רשימת החרגות בסדר עולה: $-2, 2$. אימות: $f(0)=-1/4$ עובד; $f(2)$ ו-$f(-2)$ לא מוגדרים. בבחינה — כתבו $\\mathbb{R}\\setminus\\{-2,2\\}$ במפורש.",
    ),
    fmt_expl(
        "$(f\\circ g)(3)$: first $g(3)=3^2=9$, then $f(9)=2(9)-3=15$. $(g\\circ f)(3)$: first $f(3)=2(3)-3=3$, then $g(3)=3^2=9$. Different order → different results.",
        "Composition is a two-step pipeline. For $(f\\circ g)(3)$, always compute the **inner** function at 3 first. Write intermediate values to avoid swapping order.",
        "Computing $f(3)$ first when asked for $(f\\circ g)(3)$ is the classic error. Another mistake: adding $f(3)+g(3)$ instead of composing.",
        "Label steps: 'Step 1: $g(3)=...$' then 'Step 2: $f(...)=...$'. Examiners award method marks for showing the inner value even if final arithmetic slips.",
        "$(f\\circ g)(3)$: קודם $g(3)=3^2=9$, אז $f(9)=2(9)-3=15$. $(g\\circ f)(3)$: קודם $f(3)=3$, אז $g(3)=9$. סדר שונה → תוצאות שונות.",
        "הרכבה = צינור דו-שלבי. ב-$(f\\circ g)(3)$ מחשבים **פנימית** ב-3 קודם. כתבו ערכים ביניים כדי לא להחליף סדר.",
        "חישוב $f(3)$ קודם כשמבקשים $(f\\circ g)(3)$ — טעות קלאסית. טעות נוספת: $f(3)+g(3)$ במקום הרכבה.",
        "סמנו שלבים: 'שלב 1: $g(3)=...$' ואז 'שלב 2: $f(...)=...$'. בודקים נותנים נקודות על ערך ביניים גם אם החשבון הסופי טועה.",
    ),
    fmt_expl(
        "Replace $x$ with $(a-2)$ everywhere: $f(a-2)=3(a-2)+1=3a-6+1=3a-5$. Distribute the 3 before combining constants.",
        "$f(a-2)$ means the input is the entire expression $a-2$, not 'subtract 2 from the answer.' Parentheses tell you what replaces $x$.",
        "Writing $3a-2+1=3a-1$ by distributing incorrectly (multiplying only the first term). Another error: $f(a-2)=f(a)-2$ treating $-2$ as output shift.",
        "Compare with $f(x)+1=3x+2$ to see the difference. On Bagrut, algebraic inputs test whether you substitute into the **rule**, not just numbers.",
        "מחליפים $x$ ב-$(a-2)$ בכל מקום: $f(a-2)=3(a-2)+1=3a-6+1=3a-5$. הפיצו 3 לפני איחוד קבועים. זה שונה מ-$f(a)-2$ — המינוס 2 **בתוך** הסוגריים, לא על התוצאה.",
        "$f(a-2)$ = הקלט הוא כל הביטוי $a-2$, לא 'חיסור 2 מהתשובה'. סוגריים אומרים מה מחליף $x$.",
        "כתיבת $3a-1$ מפיזור שגוי (כפל רק באיבר ראשון). טעות: $f(a-2)=f(a)-2$ כהזזת פלט.",
        "השוו ל-$f(x)+1=3x+2$ לראות הפרש. בבגרות, קלט אלגברי בודק הצבה ב**כלל**, לא רק במספרים. כתבו את הביטוי המלא לפני פישוט.",
    ),
]


def apply():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in SECTION_BODIES:
            sec["body_en_md"] = SECTION_BODIES[kind]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[kind]["body_he_md"]

        if kind == "worked_example":
            n = sec.get("example_number")
            if n == 1:
                sec["body_en_md"] = WE1_EN
                sec["body_he_md"] = WE1_HE
            elif n == 2:
                sec["body_en_md"] = WE2_EN
                sec["body_he_md"] = WE2_HE
            elif n == 3:
                sec["body_en_md"] = WE3_EN
                sec["body_he_md"] = WE3_HE

        if kind == "checkpoint":
            if "5-2x" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CP1_EN
                sec["checkpoint_solution_he"] = CP1_HE
            elif "f\\circ g" in sec.get("body_en_md", "") or "f(g" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CP2_EN
                sec["checkpoint_solution_he"] = CP2_HE

        if kind == "method_guide":
            sec["body_en_md"] = METHOD_EN
            sec["body_he_md"] = METHOD_HE

        if kind == "pitfall":
            sec["body_en_md"] = PITFALL_EN
            sec["body_he_md"] = PITFALL_HE

        if kind == "why_matters":
            sec["body_en_md"] = WHY_MATTERS_EN
            sec["body_he_md"] = WHY_MATTERS_HE

        if kind == "before_exam":
            sec["body_en_md"] = BEFORE_EXAM_EN
            sec["body_he_md"] = BEFORE_EXAM_HE

        if kind == "summary":
            sec["body_en_md"] = SUMMARY_EN
            sec["body_he_md"] = SUMMARY_HE

    for i, q in enumerate(data["questions"]):
        if i < len(EXPLANATIONS):
            q["explanation_en"], q["explanation_he"] = EXPLANATIONS[i]

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")


def validate():
    issues = []
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind not in MIN:
            continue
        en_min, he_min = MIN[kind]
        en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        if en_w < en_min:
            issues.append(f"section {kind}: EN {en_w} < {en_min}")
        if he_w < he_min:
            issues.append(f"section {kind}: HE {he_w} < {he_min}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            issues.append(f"section {kind}: weak Hebrew")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                issues.append(f"Q{q['ord']} expl_{lang}: {w} words (want 80-150)")

    if issues:
        print("VALIDATION ISSUES:")
        for i in issues:
            print(f"  - {i}")
        return False
    print("All depth gates passed.")
    return True


if __name__ == "__main__":
    apply()
    ok = validate()
    r = subprocess.run(
        ["node", str(ROOT / "scripts/seed-lessons.mjs"), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr)
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    if not ok:
        raise SystemExit(1)
