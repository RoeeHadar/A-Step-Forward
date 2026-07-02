#!/usr/bin/env python3
"""Expand quadratic_model_fitting.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/quadratic_model_fitting.json"

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
        "body_en_md": """When real-world data curves instead of lying on a straight line, a **quadratic model** $y = ax^2 + bx + c$ is often the simplest accurate choice. The graph is a parabola: one turn (maximum or minimum), smooth symmetry, and only three parameters to determine. That makes quadratics the workhorse of introductory modeling in physics, economics, and engineering.

**Three fitting methods you must know:**
1. **Exact fit through 3 points** — substitute each point into $y=ax^2+bx+c$ and solve the resulting $3\\times3$ linear system for $a$, $b$, $c$.
2. **Vertex form** — when the vertex $(h,k)$ is given (or read from context), write $y=a(x-h)^2+k$ and use one extra point to find $a$.
3. **Regression (least squares)** — when you have more than three noisy data points, minimize $\\sum(y_i - ax_i^2 - bx_i - c)^2$ (calculator or software).

**Where it appears:** projectile height vs. horizontal distance, revenue vs. price (concave down), bridge arches, and any symmetric "hump" or "dip" pattern. On Israeli Bagrut (4–5 units) and engineering entrance exams, you are expected to pick the right method from the wording, set up equations cleanly, and **verify** by back-substitution.""",
        "body_he_md": """כשנתונים אמיתיים **עקומים** במקום לשכב על קו ישר, **מודל ריבועי** $y = ax^2 + bx + c$ הוא לעיתים קרובות הבחירה הפשוטה והמדויקת ביותר. הגרף הוא פרבולה: פיתול אחד (מקסימום או מינימום), סימטריה חלקה, ורק שלושה פרמטרים לקביעה. לכן ריבועיות הן עמוד השדרה של מודלים בסיסיים בפיזיקה, כלכלת מיקרו והנדסה.

**שלוש שיטות התאמה שחובה לדעת:**
1. **התאמה מדויקת דרך 3 נקודות** — מציבים כל נקודה ב-$y=ax^2+bx+c$ ופותרים מערכת לינארית $3\\times3$ עבור $a$, $b$, $c$.
2. **צורת קודקוד** — כשהקודקוד $(h,k)$ נתון (או נקרא מההקשר), כותבים $y=a(x-h)^2+k$ ומשתמשים בנקודה נוספת אחת למציאת $a$.
3. **רגרסיה (ריבועים פחותים)** — כשיש יותר משלוש נקודות עם רעש, ממזערים $\\sum(y_i - ax_i^2 - bx_i - c)^2$ (מחשבון או תוכנה).

**היכן זה מופיע:** גובה קליע מול מרחק אופקי, הכנסה מול מחיר (קעור למטה), קשתות גשר, וכל דפוס סימטרי של "גב" או "שקע". בבגרות (4–5 יחידות) ובמבחני כניסה להנדסה, מצפים שתבחרו שיטה לפי ניסוח השאלה, תציבו משוואות בצורה מסודרת, ו**תאמתו** בהצבה חוזרת.""",
    },
    "definition": {
        "body_en_md": """A **quadratic model** is any function of the form $f(x)=ax^2+bx+c$ with $a\\ne0$. Fitting means finding $a$, $b$, $c$ so the parabola matches given information.

**Three-point exact fit:** Given distinct $x$-values $(x_1,y_1)$, $(x_2,y_2)$, $(x_3,y_3)$, substitute into $y=ax^2+bx+c$:
$$\\begin{cases} ax_1^2 + bx_1 + c = y_1 \\\\ ax_2^2 + bx_2 + c = y_2 \\\\ ax_3^2 + bx_3 + c = y_3 \\end{cases}$$
This is a **linear** system in the unknowns $a$, $b$, $c$ (coefficients involve powers of $x$). When $x_i$ are distinct, the system has a **unique** solution — the Vandermonde determinant is non-zero.

**Vertex form:** If the vertex $(h,k)$ is known:
$$y = a(x-h)^2 + k.$$
Only $a$ is unknown; one additional point determines it. Expand to standard form when the question asks for $ax^2+bx+c$.

**Intercept form:** If $x$-intercepts (roots) $r_1$, $r_2$ are known:
$$y = a(x-r_1)(x-r_2).$$
One extra point fixes $a$. Useful when the graph crosses the $x$-axis at known values.

**Key formulas from standard form:**
- Axis of symmetry: $x = -\\dfrac{b}{2a}$
- Vertex $y$-coordinate: $y = c - \\dfrac{b^2}{4a}$
- Opens upward if $a>0$ (minimum); downward if $a<0$ (maximum).""",
        "body_he_md": """**מודל ריבועי** הוא כל פונקציה מהצורה $f(x)=ax^2+bx+c$ עם $a\\ne0$. **התאמה** פירושה מציאת $a$, $b$, $c$ כך שהפרבולה תואמת מידע נתון.

**התאמה מדויקת דרך 3 נקודות:** נתונים $x$ שונים $(x_1,y_1)$, $(x_2,y_2)$, $(x_3,y_3)$, מציבים ב-$y=ax^2+bx+c$:
$$\\begin{cases} ax_1^2 + bx_1 + c = y_1 \\\\ ax_2^2 + bx_2 + c = y_2 \\\\ ax_3^2 + bx_3 + c = y_3 \\end{cases}$$
זו מערכת **לינארית** באלמונים $a$, $b$, $c$ (המקדמים כוללים חזקות של $x$). כש-$x_i$ שונים, יש **פתרון יחיד** — דטרמיננטת ואנדרמונד שונה מאפס.

**צורת קודקוד:** אם הקודקוד $(h,k)$ ידוע:
$$y = a(x-h)^2 + k.$$
רק $a$ לא ידוע; נקודה נוספת אחת קובעת אותו. מפתחים לצורה $ax^2+bx+c$ כשהשאלה דורשת.

**צורת שורשים:** אם נקודות חיתוך עם ציר $x$ (שורשים) $r_1$, $r_2$ ידועות:
$$y = a(x-r_1)(x-r_2).$$
נקודה נוספת אחת קובעת את $a$. שימושי כשהגרף חותך את ציר $x$ בערכים ידועים.

**נוסחאות מרכזיות מצורה סטנדרטית:**
- ציר סימטריה: $x = -\\dfrac{b}{2a}$
- קואורדינטת $y$ של הקודקוד: $y = c - \\dfrac{b^2}{4a}$
- פותחת למעלה אם $a>0$ (מינימום); למטה אם $a<0$ (מקסימום).""",
    },
    "theory": {
        "body_en_md": """Use a **decision tree** before crunching numbers — exam items reward recognizing structure.

### Step-by-step: three-point system
1. **Write one equation per point** in $y=ax^2+bx+c$.
2. **Eliminate $c$ first** — subtract the equation from $(0,y_0)$ if available, or subtract equation 1 from 2 and 3. You get two equations in $a$ and $b$ only.
3. **Solve the $2\\times2$ system** for $a$ and $b$ (substitution or elimination).
4. **Back-substitute** into any original equation to find $c$.
5. **Write the final model** and substitute **all** given points to verify.

### When vertex form is faster
If the problem states "maximum height", "minimum value", or gives vertex coordinates, start with $y=a(x-h)^2+k$. You avoid a full $3\\times3$ system. Expand only if standard form is required.

### Intercept form shortcut
Given roots $r_1$, $r_2$ and one other point, write $y=a(x-r_1)(x-r_2)$. This is common in bridge/arch problems where the base width gives both intercepts.

### Regression (least squares)
For $n>3$ points that do not lie exactly on one parabola, minimize the sum of squared vertical errors. On Bagrut you typically use a calculator; the result is a **best-fit** parabola, not an exact pass-through.

### Sign of $a$ from context
- **Projectile / revenue / arch opening downward:** expect $a<0$ (maximum).
- **Cost bowl / energy well:** expect $a>0$ (minimum).
A wrong sign often means a sign error in vertex-form expansion — check $(x-h)^2 = x^2 - 2hx + h^2$.""",
        "body_he_md": """השתמשו ב**עץ החלטות** לפני חישוב — בבחינה מעריכים זיהוי מבנה.

### שלב-אחר-שלב: מערכת 3 נקודות
1. **כתבו משוואה לכל נקודה** ב-$y=ax^2+bx+c$.
2. **בטלו $c$ קודם** — חסרו את משוואת $(0,y_0)$ אם קיימת, או חסרו משוואה 1 מ-2 ו-3. מתקבלות שתי משוואות ב-$a$ ו-$b$ בלבד.
3. **פתרו מערכת $2\\times2$** ל-$a$ ו-$b$ (הצבה או חיסור).
4. **הציבו חזרה** לכל משוואה מקורית למציאת $c$.
5. **כתבו את המודל הסופי** והציבו **כל** הנקודות לאימות.

### מתי צורת קודקוד מהירה יותר
אם השאלה מציינת "גובה מקסימלי", "ערך מינימלי", או נותנת קואורדינטות קודקוד — התחילו ב-$y=a(x-h)^2+k$. נמנעים ממערכת $3\\times3$ מלאה. מפתחים רק אם נדרשת צורה סטנדרטית.

### קיצור דרך — צורת שורשים
נתונים שורשים $r_1$, $r_2$ ונקודה נוספת: $y=a(x-r_1)(x-r_2)$. נפוץ בגשרים/קשתות כש**רוחב הבסיס** נותן שני חיתוכים.

### רגרסיה (ריבועים פחותים)
ל-$n>3$ נקודות שלא על פרבולה אחת בדיוק — ממזערים סכום ריבועי השגיאות האנכיות. בבגרות משתמשים במחשבון; התוצאה **התאמה מיטבית**, לא מעבר מדויק.

### סימן $a$ מההקשר
- **קליע / הכנסה / קשת פתוחה למטה:** צפו $a<0$ (מקסימום).
- **עלות / באגן אנרגיה:** צפו $a>0$ (מינימום).
סימן שגוי לעיתים מגיע מטעות בפיתוח $(x-h)^2 = x^2 - 2hx + h^2$.""",
    },
    "worked_example_1": {
        "body_en_md": """**Find** $y = ax^2 + bx + c$ through $(0,1)$, $(1,2)$, $(2,7)$.

Three distinct $x$-values → unique parabola. Strategy: use $(0,1)$ to get $c$ immediately, then a $2\\times2$ system.

### Move 1: Substitute $(0,1)$
$0 + 0 + c = 1 \\Rightarrow c = 1$. Now only $a$ and $b$ remain unknown.

### Move 2: Equations from $(1,2)$ and $(2,7)$
From $(1,2)$: $a + b + 1 = 2 \\Rightarrow a + b = 1$ ... (i)

From $(2,7)$: $4a + 2b + 1 = 7 \\Rightarrow 4a + 2b = 6 \\Rightarrow 2a + b = 3$ ... (ii)

### Move 3: Eliminate $b$
(ii) − (i): $(2a+b) - (a+b) = 3 - 1 \\Rightarrow a = 2$.

From (i): $b = 1 - 2 = -1$.

### Move 4: Write and verify
**Answer:** $y = 2x^2 - x + 1$.

**Check:** $(0,1)$: $1$ ✓. $(1,2)$: $2-1+1=2$ ✓. $(2,7)$: $8-2+1=7$ ✓.

**Exam note:** Always eliminate $c$ first when a point has $x=0$ — it saves an entire unknown instantly.

**Alternative check:** The second differences of equally spaced $y$-values are constant for quadratics: $7-2=5$, $2-1=1$, difference $4=2a$, confirming $a=2$ without full elimination.""",
        "body_he_md": """**מצאו** $y = ax^2 + bx + c$ דרך $(0,1)$, $(1,2)$, $(2,7)$.

שלוש $x$ שונות → פרבולה יחידה. אסטרטגיה: $(0,1)$ נותן $c$ מיד, ואז מערכת $2\\times2$.

### צעד 1: הצבת $(0,1)$
$0 + 0 + c = 1 \\Rightarrow c = 1$. נשארו רק $a$ ו-$b$.

### צעד 2: משוואות מ-$(1,2)$ ו-$(2,7)$
מ-$(1,2)$: $a + b + 1 = 2 \\Rightarrow a + b = 1$ ... (i)

מ-$(2,7)$: $4a + 2b + 1 = 7 \\Rightarrow 4a + 2b = 6 \\Rightarrow 2a + b = 3$ ... (ii)

### צעד 3: ביטול $b$
(ii) − (i): $(2a+b) - (a+b) = 3 - 1 \\Rightarrow a = 2$.

מ-(i): $b = 1 - 2 = -1$.

### צעד 4: כתיבה ואימות
**תשובה:** $y = 2x^2 - x + 1$.

**בדיקה:** $(0,1)$: $1$ ✓. $(1,2)$: $2-1+1=2$ ✓. $(2,7)$: $8-2+1=7$ ✓.

**הערת בחינה:** תמיד בטלו $c$ קודם כשיש נקודה עם $x=0$ — חוסך אלמון שלם מיד.

**בדיקה חלופית:** הפרשי $y$ שווים לריבועיות: $7-2=5$, $2-1=1$, הפרש $4=2a$, מאשר $a=2$ בלי חיסור מלא.""",
    },
    "worked_example_2": {
        "body_en_md": """**A parabola has vertex $(2, -3)$ and passes through $(4, 5)$. Find its equation.**

Vertex given → vertex form is the direct path. Only one unknown ($a$) after writing the template.

### Move 1: Write vertex form
$y = a(x-2)^2 - 3$. The vertex $(2,-3)$ is built in: at $x=2$, the squared term vanishes and $y=-3$.

### Move 2: Substitute $(4, 5)$ to find $a$
$5 = a(4-2)^2 - 3 = a(2)^2 - 3 = 4a - 3$

$4a = 8 \\Rightarrow a = 2$

### Move 3: Expand to standard form (if needed)
$y = 2(x-2)^2 - 3 = 2(x^2 - 4x + 4) - 3 = 2x^2 - 8x + 8 - 3 = 2x^2 - 8x + 5$

### Move 4: Verify
At $x=2$: $y = 2(4)-16+5 = -3$ ✓. At $x=4$: $y = 2(16)-32+5 = 5$ ✓.

**Why vertex form wins here:** A three-point system would work but wastes time and invites arithmetic errors. You would need to pick three points including the vertex and one extra — more algebra for the same answer.

**Bagrut pattern:** "Vertex at … and passes through …" almost always means vertex form — underline the vertex coordinates before writing any equation. Expand to standard form only when the question explicitly asks for $a$, $b$, and $c$ separately.""",
        "body_he_md": """**לפרבולה קודקוד $(2, -3)$ והיא עוברת ב-$(4, 5)$. מצאו משוואה.**

קודקוד נתון → צורת קודקוד היא הנתיב הישיר. רק אלמון אחד ($a$) אחרי כתיבת התבנית.

### צעד 1: כתיבת צורת קודקוד
$y = a(x-2)^2 - 3$. הקודקוד $(2,-3)$ מובנה: ב-$x=2$ האיבר בריבוע מתאפס ו-$y=-3$.

### צעד 2: הצבת $(4, 5)$ למציאת $a$
$5 = a(4-2)^2 - 3 = a(2)^2 - 3 = 4a - 3$

$4a = 8 \\Rightarrow a = 2$

### צעד 3: פיתוח לצורה סטנדרטית (אם נדרש)
$y = 2(x-2)^2 - 3 = 2(x^2 - 4x + 4) - 3 = 2x^2 - 8x + 8 - 3 = 2x^2 - 8x + 5$

### צעד 4: אימות
ב-$x=2$: $y = 2(4)-16+5 = -3$ ✓. ב-$x=4$: $y = 2(16)-32+5 = 5$ ✓.

**למה צורת קודקוד מנצחת:** מערכת 3 נקודות תעבוד אבל מבזבזת זמן ומזמינה טעויות. הייתם צריכים לבחור שלוש נקודות כולל קודקוד ועוד אחת — יותר אלגברה לאותה תשובה.

**דפוס בגרות:** "קודקוד ב… ועוברת ב…" כמעט תמיד ⇒ צורת קודקוד — סמנו קואורדינטות קודקוד לפני כתיבת משוואה. פתחו לצורה סטנדרטית רק כשמבקשים במפורש $a$, $b$, $c$.""",
    },
    "worked_example_3": {
        "body_en_md": """**A ball is launched from ground level $(0,0)$, reaches maximum height 20 m at $x=30$ m, and lands at $x=60$ m. Find the quadratic model.**

This is a symmetric projectile: launch and landing at $y=0$, peak at the midpoint $x=30$. Vertex form captures the physics directly.

### Move 1: Identify the vertex
Maximum height 20 m at $x=30$ m → vertex $(30, 20)$. Parabola opens downward ($a<0$).

Vertex form: $y = a(x-30)^2 + 20$.

### Move 2: Use launch point $(0,0)$ to find $a$
$0 = a(0-30)^2 + 20 = 900a + 20$

$900a = -20 \\Rightarrow a = -\\dfrac{1}{45}$

### Move 3: Write the model
$y = -\\dfrac{1}{45}(x-30)^2 + 20$

### Move 4: Verify landing at $x=60$
$y = -\\dfrac{1}{45}(60-30)^2 + 20 = -\\dfrac{900}{45} + 20 = -20 + 20 = 0$ ✓

**Physics insight:** Symmetry means the peak lies halfway between zeros. If landing were unknown, one zero plus vertex still determines the model.

**Units reminder:** Keep meters consistent; $a$ has units $1/\\text{m}$ when $x$ is horizontal distance. On Bagrut, state the final equation and verify both boundary points.""",
        "body_he_md": """**כדור משוגר מגובה אפס $(0,0)$, מגיע לגובה מקסימלי 20 מ' ב-$x=30$ מ', ונוחת ב-$x=60$ מ'. מצאו מודל ריבועי.**

זה קליע סימטרי: שיגור ונחיתה ב-$y=0$, שיא באמצע $x=30$. צורת קודקוד תופסת את הפיזיקה ישירות.

### צעד 1: זיהוי הקודקוד
גובה מקסימלי 20 מ' ב-$x=30$ מ' → קודקוד $(30, 20)$. פרבולה פתוחה למטה ($a<0$).

צורת קודקוד: $y = a(x-30)^2 + 20$.

### צעד 2: נקודת שיגור $(0,0)$ למציאת $a$
$0 = a(0-30)^2 + 20 = 900a + 20$

$900a = -20 \\Rightarrow a = -\\dfrac{1}{45}$

### צעד 3: כתיבת המודל
$y = -\\dfrac{1}{45}(x-30)^2 + 20$

### צעד 4: אימות נחיתה ב-$x=60$
$y = -\\dfrac{1}{45}(60-30)^2 + 20 = -\\dfrac{900}{45} + 20 = -20 + 20 = 0$ ✓

**תובנה פיזיקלית:** סימטריה ⇒ השיא באמצע בין אפסים. אם נחיתה לא ידועה, אפס אחד + קודקוד עדיין קובעים את המודל.

**יחידות:** שמרו על מטרים עקביים; ל-$a$ יחידות $1/\\text{מ'}$ כש-$x$ הוא מרחק אופקי. בבגרות, כתבו משוואה סופית ואמתו שתי נקודות הגבול.""",
    },
    "method_guide": {
        "body_en_md": """| Given information | Best method | Unknowns |
|---|---|---|
| 3 exact points (distinct $x$) | Substitute into $y=ax^2+bx+c$ → $3\\times3$ system | $a$, $b$, $c$ |
| Vertex $(h,k)$ + 1 point | $y=a(x-h)^2+k$ | $a$ only |
| $x$-intercepts $r_1$, $r_2$ + 1 point | $y=a(x-r_1)(x-r_2)$ | $a$ only |
| Maximum/minimum value + 1 point | Vertex form (opens down for max, up for min) | $a$ only |
| $n>3$ noisy data points | Least-squares regression (calculator) | best-fit $a$, $b$, $c$ |

**Workflow:** Read the problem → pick the row → set up equations → solve → **substitute all given points back**.

**When to expand:** Bagrut often asks for $ax^2+bx+c$ even when you found vertex form. Expand carefully: $(x-h)^2 = x^2 - 2hx + h^2$.

**Verification habit:** One wrong sign in expansion can pass two of three points but fail the third — always check every constraint.""",
        "body_he_md": """| מידע נתון | שיטה מומלצת | אלמונים |
|---|---|---|
| 3 נקודות מדויקות ($x$ שונים) | הצבה ב-$y=ax^2+bx+c$ → מערכת $3\\times3$ | $a$, $b$, $c$ |
| קודקוד $(h,k)$ + נקודה | $y=a(x-h)^2+k$ | רק $a$ |
| חיתוכי $x$ $r_1$, $r_2$ + נקודה | $y=a(x-r_1)(x-r_2)$ | רק $a$ |
| מקסימום/מינימום + נקודה | צורת קודקוד (למטה למקס', למעלה למינ') | רק $a$ |
| $n>3$ נקודות עם רעש | רגרסיה ריבועים פחותים (מחשבון) | $a$, $b$, $c$ מיטביים |

**זרימת עבודה:** קראו שאלה → בחרו שורה → הציבו משוואות → פתרו → **הציבו חזרה כל הנקודות**.

**מתי לפתח:** בבגרות לעיתים דורשים $ax^2+bx+c$ גם אחרי צורת קודקוד. פתחו בזהירות: $(x-h)^2 = x^2 - 2hx + h^2$.

**הרגל אימות:** סימן שגוי בפיתוח יכול לעבור שתי נקודות ולהיכשל בשלישית — תמיד בדקו כל אילוץ.""",
    },
    "pitfall": {
        "body_en_md": """1. **Skipping verification.** After finding $a$, $b$, $c$, substitute **every** given point. Partial checks miss sign errors that cost full credit on Bagrut.

2. **Wrong axis formula.** The axis of symmetry is $x = -\\dfrac{b}{2a}$, **not** $+\\dfrac{b}{2a}$. This comes from completing the square — the minus sign is structural, not optional.

3. **Sign errors expanding $(x-h)^2$.** Remember $(x-h)^2 = x^2 - 2hx + h^2$. A common mistake: writing $+2hx$ instead of $-2hx$, which flips the middle coefficient.

4. **Using regression for exact 3-point data.** When exactly three points are given and the question asks for a parabola through them, solve the linear system — do not run least squares (which may not pass through all three).

5. **Ignoring context for sign of $a$.** Maximum height / revenue → $a<0$. Minimum cost / energy → $a>0$. If your $a$ contradicts the story, re-check expansion.

**Example misconception:** Writing vertex $x$-coordinate as $b/(2a)$ instead of $-b/(2a)$.

**Fix:** Complete the square once on paper before the exam until the minus is automatic.""",
        "body_he_md": """1. **דילוג על אימות.** אחרי מציאת $a$, $b$, $c$, הציבו **כל** נקודה. בדיקות חלקיות מפספסות טעויות סימן שעולות בניקוד מלא בבגרות.

2. **נוסחת ציר שגויה.** ציר הסימטריה הוא $x = -\\dfrac{b}{2a}$, **לא** $+\\dfrac{b}{2a}$. זה מגיע מהשלמה לריבוע — המינוס מבני, לא אופציונלי.

3. **טעויות סימן בפיתוח $(x-h)^2$.** זכרו $(x-h)^2 = x^2 - 2hx + h^2$. טעות שכיחה: כתיבת $+2hx$ במקום $-2hx$, מה שהופך את המקדם האמצעי.

4. **רגרסיה ל-3 נקודות מדויקות.** כשנתונות בדיוק שלוש נקודות והשאלה דורשת פרבולה דרכן — פתרו מערכת לינארית; אל תריצו ריבועים פחותים (שאולי לא יעברו בשלוש).

5. **התעלמות מהקשר לסימן $a$.** גובה מקסימלי / הכנסה → $a<0$. עלות מינימלית / אנרגיה → $a>0$. אם $a$ סותר את הסיפור — בדקו פיתוח.

**דוגמה לטעות נפוצה:** כתיבת קואורדינטת $x$ של קודקוד כ-$b/(2a)$ במקום $-b/(2a)$.

**תיקון:** השלימו לריבוע פעם אחת על נייר לפני בחינה עד שהמינוס אוטומטי.""",
    },
    "why_matters": {
        "body_en_md": """Quadratic model fitting is the bridge between **pure algebra** and **applied modeling**. The same three-parameter family describes a cannonball's arc, a company's profit curve, and the shape of a suspension bridge cable (locally parabolic).

On A Step Forward, this lesson connects forward to optimization (finding max/min revenue), backward to solving systems of linear equations, and sideways to physics (projectile motion) and statistics (regression). When an agent or tutor cites `lesson:quadratic_model_fitting`, they expect you to **choose a method from context**, not memorize one algorithm.

**Why it matters for exams:** Bagrut and university entrance tests rarely say "solve a $3\\times3$ system." They wrap the math in a story — arch, ball, profit — and reward students who translate words into the right form (standard, vertex, or intercept) before calculating.""",
        "body_he_md": """התאמת מודל ריבועי היא הגשר בין **אלגברה טהורה** ל**מודלים יישומיים**. אותה משפחה של שלושה פרמטרים מתארת קשת של תותח, עקומת רווח של חברה, וצורת כבל גשר (בקירוב פרבולי מקומי).

ב-A Step Forward, שיעור זה מתחבר קדימה לאופטימיזציה (מקסימום/מינימום הכנסה), אחורה לפתרון מערכות משוואות לינאריות, וצידית לפיזיקה (תנועה קליעית) וסטטיסטיקה (רגרסיה). כשסוכן או מורה מצטטים `lesson:quadratic_model_fitting`, הם מצפים **לבחור שיטה לפי הקשר**, לא לשנן אלגוריתם אחד.

**למה זה חשוב לבחינות:** בבגרות ומבחני כניסה לעיתים רחוקות כותבים "פתרו מערכת $3\\times3$". הם עוטפים את החומר המתמטי בסיפור — קשת, כדור, רווח — ומעריכים תלמידים שמתרגמים מילים לצורה הנכונה (סטנדרטית, קודקוד, או שורשים) לפני חישוב.""",
    },
    "before_exam": {
        "body_en_md": """**Quick reference — memorize the decision, not just formulas:**

- **3 points (distinct $x$)** → $y=ax^2+bx+c$, eliminate $c$ first if $x=0$ is among them
- **Vertex $(h,k)$ known** → $y=a(x-h)^2+k$, one substitution for $a$
- **Two $x$-intercepts** → $y=a(x-r_1)(x-r_2)$, one substitution for $a$
- **Axis of symmetry:** $x=-b/(2a)$
- **Vertex $y$:** $c - b^2/(4a)$
- **$a>0$:** opens up (minimum); **$a<0$:** opens down (maximum)
- **Always verify** by substituting all given points

**Last review:** Pick one checkpoint from this lesson, cover the solution, and solve it timed in under 4 minutes. Say the method name aloud before writing equations.""",
        "body_he_md": """**עזר זיכרון — שיננו את ההחלטה, לא רק נוסחאות:**

- **3 נקודות ($x$ שונים)** → $y=ax^2+bx+c$, בטלו $c$ קודם אם $x=0$ ביניהן
- **קודקוד $(h,k)$ ידוע** → $y=a(x-h)^2+k$, הצבה אחת ל-$a$
- **שני חיתוכי $x$** → $y=a(x-r_1)(x-r_2)$, הצבה אחת ל-$a$
- **ציר סימטריה:** $x=-b/(2a)$
- **$y$ של קודקוד:** $c - b^2/(4a)$
- **$a>0$:** פותחת למעלה (מינימום); **$a<0$:** למטה (מקסימום)
- **תמיד אמתו** בהצבת כל הנקודות

**חזרה אחרונה:** בחרו checkpoint מהשיעור, כסו פתרון, ופתרו בזמן תחת 4 דקות. אמרו את שם השיטה בקול לפני כתיבת משוואות.""",
    },
    "summary": {
        "body_en_md": """- **Standard form:** $y=ax^2+bx+c$ — three unknowns, need three independent equations (usually three points).
- **Three-point fit:** substitute → linear $3\\times3$ system → eliminate $c$ first when possible.
- **Vertex form:** $y=a(x-h)^2+k$ — fastest when vertex or max/min is given.
- **Intercept form:** $y=a(x-r_1)(x-r_2)$ — fastest when roots are given.
- **Axis:** $x=-b/(2a)$; **vertex $y$:** $c-b^2/(4a)$.
- **Regression:** for $n>3$ noisy points; calculator on Bagrut.
- **Always verify** all constraints after solving.

**Takeaway:** Read the problem once for **structure** (points? vertex? roots?), pick the matching method, then compute.""",
        "body_he_md": """- **צורה סטנדרטית:** $y=ax^2+bx+c$ — שלושה אלמונים, צריך שלוש משוואות בלתי תלויות (בדרך כלל שלוש נקודות).
- **התאמת 3 נקודות:** הצבה → מערכת $3\\times3$ לינארית → ביטול $c$ קודם כשאפשר.
- **צורת קודקוד:** $y=a(x-h)^2+k$ — הכי מהיר כשקודקוד או מקס'/מינ' נתונים.
- **צורת שורשים:** $y=a(x-r_1)(x-r_2)$ — הכי מהיר כשנתונים שורשים.
- **ציר:** $x=-b/(2a)$; **$y$ קודקוד:** $c-b^2/(4a)$.
- **רגרסיה:** ל-$n>3$ נקודות עם רעש; מחשבון בבגרות.
- **תמיד אמתו** כל האילוצים אחרי הפתרון.

**מסקנה:** קראו שאלה פעם אחת ל**מבנה** (נקודות? קודקוד? שורשים?), בחרו שיטה מתאימה, ואז חשבו.""",
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": """Find $y=ax^2+bx+c$ through $(0,3)$, $(1,4)$, $(-1,6)$.

**Step 1:** From $(0,3)$: $c=3$ immediately.

**Step 2:** From $(1,4)$: $a+b+3=4 \\Rightarrow a+b=1$ ... (i)

From $(-1,6)$: $a-b+3=6 \\Rightarrow a-b=3$ ... (ii)

**Step 3:** Add (i) and (ii): $2a=4 \\Rightarrow a=2$. From (i): $b=-1$.

**Step 4:** **Answer:** $y=2x^2-x+3$.

**Verify:** $(0,3)$: $3$ ✓. $(1,4)$: $2-1+3=4$ ✓. $(-1,6)$: $2+1+3=6$ ✓.""",
        "checkpoint_solution_he": """מצאו $y=ax^2+bx+c$ דרך $(0,3)$, $(1,4)$, $(-1,6)$.

**שלב 1:** מ-$(0,3)$: $c=3$ מיד.

**שלב 2:** מ-$(1,4)$: $a+b+3=4 \\Rightarrow a+b=1$ ... (i)

מ-$(-1,6)$: $a-b+3=6 \\Rightarrow a-b=3$ ... (ii)

**שלב 3:** חיבור (i)+(ii): $2a=4 \\Rightarrow a=2$. מ-(i): $b=-1$.

**שלב 4:** **תשובה:** $y=2x^2-x+3$.

**אימות:** $(0,3)$: $3$ ✓. $(1,4)$: $2-1+3=4$ ✓. $(-1,6)$: $2+1+3=6$ ✓.""",
    },
    "checkpoint_2": {
        "checkpoint_solution_en": """Vertex $(-1,4)$, passes through $(1,-4)$.

**Step 1:** Vertex form: $y=a(x+1)^2+4$ (because $h=-1$).

**Step 2:** Substitute $(1,-4)$: $-4=a(1+1)^2+4=4a+4 \\Rightarrow 4a=-8 \\Rightarrow a=-2$.

**Step 3:** Expand: $y=-2(x+1)^2+4=-2(x^2+2x+1)+4=-2x^2-4x+2$.

**Verify:** At $x=-1$: $y=4$ ✓. At $x=1$: $y=-2-4+2=-4$ ✓.""",
        "checkpoint_solution_he": """קודקוד $(-1,4)$, עוברת ב-$(1,-4)$.

**שלב 1:** צורת קודקוד: $y=a(x+1)^2+4$ (כי $h=-1$).

**שלב 2:** הצבת $(1,-4)$: $-4=a(1+1)^2+4=4a+4 \\Rightarrow 4a=-8 \\Rightarrow a=-2$.

**שלב 3:** פיתוח: $y=-2(x+1)^2+4=-2(x^2+2x+1)+4=-2x^2-4x+2$.

**אימות:** ב-$x=-1$: $y=4$ ✓. ב-$x=1$: $y=-2-4+2=-4$ ✓.""",
    },
}

QUESTION_EXPLANATIONS = [
    # q1 mcq - vertex form find a
    fmt_expl(
        "Write vertex form $y=a(x-3)^2+7$. Substitute $(5,3)$: $3=a(5-3)^2+7=4a+7$, so $4a=-4$ and $a=-1$. The parabola opens downward because the point $(5,3)$ lies below the vertex $y=7$.",
        "When vertex $(h,k)$ is given, never start with a full $3\\times3$ system — write $y=a(x-h)^2+k$ first. The only unknown is $a$. Check that $a$'s sign matches the geometry: below vertex on both sides of a maximum means $a<0$.",
        "Choosing $a=1$ or $a=2$ from sign confusion — students forget that $(5-3)^2=4$, not $2$, or drop the $+7$ when isolating $a$.",
        "On Bagrut vertex-form items, write $y=a(x-h)^2+k$ as line 1 before substituting. One clean substitution often earns full credit even if expansion later slips.",
        "כותבים $y=a(x-3)^2+7$. מציבים $(5,3)$: $3=a(5-3)^2+7=4a+7$, ולכן $4a=-4$ ו-$a=-1$. הפרבולה פתוחה למטה כי $(5,3)$ מתחת לקודקוד $y=7$.",
        "כשקודקוד $(h,k)$ נתון, אל תתחילו במערכת $3\\times3$ — כתבו $y=a(x-h)^2+k$. האלמון היחיד הוא $a$. ודאו שסימן $a$ תואם גיאומטריה: מתחת לקודקוד במקסימום ⇒ $a<0$.",
        "בחירת $a=1$ או $a=2$ מבלבול סימנים — שוכחים $(5-3)^2=4$, או מפספסים $+7$ בבידוד $a$.",
        "בפריטי קודקוד בבגרות, כתבו $y=a(x-h)^2+k$ בשורה 1 לפני הצבה. הצבה נקייה אחת לעיתים מספיקה לניקוד מלא.",
    ),
    # q2 - three points (0,0), (1,3), (2,8)
    fmt_expl(
        "From $(0,0)$: $c=0$. From $(1,3)$: $a+b=3$. From $(2,8)$: $4a+2b=8 \\Rightarrow 2a+b=4$. Subtract: $a=1$, $b=2$. Model: $y=x^2+2x$. Check all three points.",
        "A point at $x=0$ gives $c$ for free — always use it first. The remaining two equations form a $2\\times2$ system. Elimination is faster than matrices on timed exams.",
        "Arithmetic slip in subtracting equations: $(2a+b)-(a+b)=a$, not $2a$. Or forgetting $c=0$ and carrying an extra unknown.",
        "Write $c$ from the $y$-intercept before any elimination — exam rubrics often award partial credit for correct setup even if $a$ or $b$ is wrong.",
        "מ-$(0,0)$: $c=0$. מ-$(1,3)$: $a+b=3$. מ-$(2,8)$: $4a+2b=8 \\Rightarrow 2a+b=4$. חיסור: $a=1$, $b=2$. מודל: $y=x^2+2x$. בדקו שלוש נקודות.",
        "נקודה ב-$x=0$ נותנת $c$ חינם — תמיד השתמשו בה קודם. שתי משוואות נותרות = $2\\times2$. חיסור מהיר יותר ממטריצות בזמן מוגבל.",
        "טעות חיסור: $(2a+b)-(a+b)=a$, לא $2a$. או שכחת $c=0$ והשארת אלמון מיותר.",
        "כתבו $c$ מחיתוך $y$ לפני חיסור — בבגרות לעיתים נקודות על הצבה נכונה גם אם $a$ או $b$ שגויים.",
    ),
    # q3 - vertex (1,3) through (0,5)
    fmt_expl(
        "Vertex form: $y=a(x-1)^2+3$. At $(0,5)$: $5=a(0-1)^2+3=a+3$, so $a=2$. Expanded: $y=2(x-1)^2+3=2x^2-4x+5$. Both vertex and point satisfy the equation.",
        "Vertex coordinates plug directly into $y=a(x-h)^2+k$ — here $h=1$, $k=3$. One point outside the vertex determines $a$. Expand only if the answer format requires $ax^2+bx+c$.",
        "Using $(x+1)$ instead of $(x-1)$ when $h=1$, or expanding $(x-1)^2$ as $x^2+2x+1$ instead of $x^2-2x+1$.",
        "After finding $a$, verify at the vertex: substitute $x=1$ — the $(x-1)^2$ term must vanish and $y$ must equal $3$.",
        "צורת קודקוד: $y=a(x-1)^2+3$. ב-$(0,5)$: $5=a(0-1)^2+3=a+3$, ולכן $a=2$. מפורק: $y=2(x-1)^2+3=2x^2-4x+5$. קודקוד ונקודה מתקיימים.",
        "קואורדינטות קודקוד נכנסות ישירות ל-$y=a(x-h)^2+k$ — כאן $h=1$, $k=3$. נקודה אחת קובעת $a$. פתחו רק אם נדרש $ax^2+bx+c$.",
        "שימוש ב-$(x+1)$ במקום $(x-1)$ כש-$h=1$, או פיתוח $(x-1)^2$ כ-$x^2+2x+1$ במקום $x^2-2x+1$.",
        "אחרי מציאת $a$, אמתו בקודקוד: $x=1$ — איבר $(x-1)^2$ מתאפס ו-$y=3$.",
    ),
    # q4 - intercepts 1,5 through (3,4) find a
    fmt_expl(
        "Intercept form: $y=a(x-1)(x-5)$. At $(3,4)$: $4=a(3-1)(3-5)=a(2)(-2)=-4a$, so $a=-1$. The parabola opens downward, consistent with roots at $1$ and $5$ and a point above the $x$-axis between them.",
        "When both $x$-intercepts are given, intercept form has only one unknown. The factor $(x-r_i)$ is zero at each root — do not expand until you need standard form.",
        "Sign error: $(3-5)=-2$, not $+2$, giving $a=+1$ instead of $-1$. Or using $(x+1)(x+5)$ instead of $(x-1)(x-5)$.",
        "Between two roots, a downward parabola lies above the axis; if your $a$ is positive, the point $(3,4)$ would be below — quick sanity check.",
        "צורת שורשים: $y=a(x-1)(x-5)$. ב-$(3,4)$: $4=a(3-1)(3-5)=a(2)(-2)=-4a$, ולכן $a=-1$. פרבולה למטה, עקבי עם שורשים $1$ ו-$5$ ונקודה מעל הציר ביניהם.",
        "כששני חיתוכי $x$ נתונים, צורת שורשים עם אלמון יחיד. $(x-r_i)$ מתאפס בכל שורש — אל תפתחו עד שצריך צורה סטנדרטית.",
        "טעות סימן: $(3-5)=-2$, לא $+2$, נותן $a=+1$ במקום $-1$. או $(x+1)(x+5)$ במקום $(x-1)(x-5)$.",
        "בין שני שורשים, פרבולה למטה מעל הציר; אם $a$ חיובי, $(3,4)$ היה מתחת — בדיקת sanity מהירה.",
    ),
    # q5 - expand 3(x-2)^2-1
    fmt_expl(
        "Expand: $y=3(x-2)^2-1=3(x^2-4x+4)-1=3x^2-12x+12-1=3x^2-12x+11$. Distribute the $3$ across all terms inside the parentheses before combining constants.",
        "Vertex-to-standard expansion is a sub-skill of model fitting — Bagrut often asks for $a$, $b$, $c$ after you found vertex form. Expand $(x-h)^2$ carefully: middle term is $-2hx$.",
        "Forgetting to multiply $3$ by the constant $4$ inside, getting $3x^2-12x+4-1$ instead of $+12-1$. Or leaving $(x-2)^2$ unexpanded.",
        "Quick check: vertex should be at $x=2$. In standard form, axis $x=-b/(2a)=12/6=2$ ✓ — catches expansion errors instantly.",
        "פיתוח: $y=3(x-2)^2-1=3(x^2-4x+4)-1=3x^2-12x+12-1=3x^2-12x+11$. הפיצו $3$ על כל האיברים בסוגריים לפני איחוד קבועים — קודם $3\\times x^2$, $3\\times(-4x)$, $3\\times 4$, ורק אז חיסור $1$.",
        "פיתוח קודקוד→סטנדרטי הוא מיומנות משנה בהתאמה — בבגרות לעיתים דורשים $a,b,c$ אחרי צורת קודקוד. $(x-h)^2$: איבר אמצעי $-2hx$. כתבו $(x-2)^2=x^2-4x+4$ בשורה נפרדת לפני הכפלה ב-$3$.",
        "שכחת $3\\times4=12$ בפנים, קיבלו $3x^2-12x+4-1$ במקום $+12-1$. או השארת $(x-2)^2$ לא מפורק. טעות נוספת: $3(x^2-4x+4)-1=3x^2-12x+11$ ולא $3x^2-12x+3$.",
        "בדיקה: קודקוד ב-$x=2$. בצורה סטנדרטית ציר $x=-b/(2a)=12/6=2$ ✓ — תופס טעויות פיתוח מיד. הציבו $x=2$ ב-$3x^2-12x+11$ וקבלו $-1$ כמו בצורת קודקוד.",
    ),
    # q6 - three points (-1,6), (0,2), (1,0)
    fmt_expl(
        "From $(0,2)$: $c=2$. From $(-1,6)$: $a-b+2=6 \\Rightarrow a-b=4$. From $(1,0)$: $a+b+2=0 \\Rightarrow a+b=-2$. Add: $2a=2 \\Rightarrow a=1$, $b=-3$. Answer: $y=x^2-3x+2$.",
        "Symmetric $x$-values around zero simplify elimination: $a-b$ and $a+b$ add cleanly to $2a$. Always label equations (i), (ii) to avoid mixing signs when subtracting.",
        "Sign error on $(-1,6)$: $(-1)^2=1$ but $b(-1)=-b$, not $+b$. Or subtracting equations in the wrong order.",
        "Verify at $x=0$ first — if your $c$ is wrong, every subsequent step fails. One substitution catches the error before you solve for $a$ and $b$.",
        "מ-$(0,2)$: $c=2$. מ-$(-1,6)$: $a-b+2=6 \\Rightarrow a-b=4$. מ-$(1,0)$: $a+b+2=0 \\Rightarrow a+b=-2$. חיבור: $2a=2 \\Rightarrow a=1$, $b=-3$. תשובה: $y=x^2-3x+2$.",
        "$x$ סימטריים סביב אפס מפשטים חיסור: $a-b$ ו-$a+b$ נותנים $2a$ בחיבור. סמנו (i), (ii) כדי לא לבלבל סימנים.",
        "טעות ב-$(-1,6)$: $(-1)^2=1$ אבל $b(-1)=-b$, לא $+b$. או חיסור משוואות בסדר שגוי.",
        "אמתו $x=0$ קודם — $c$ שגוי מקלקל הכל. הצבה אחת תופסת לפני פתרון $a$ ו-$b$.",
    ),
    # q7 - max 8 at x=3, y-intercept 5
    fmt_expl(
        "Maximum at $x=3$ with value $8$ → vertex $(3,8)$, opens down. $y=a(x-3)^2+8$. Y-intercept $(0,5)$: $5=9a+8 \\Rightarrow a=-1/3$. Equation: $y=-\\frac{1}{3}(x-3)^2+8$.",
        "Words 'maximum' tell you vertex form and $a<0$ before calculating. Y-intercept means substitute $x=0$. Do not confuse the maximum **value** $8$ with the $y$-intercept $5$.",
        "Using $a=+1/3$ (wrong sign for maximum) or writing vertex as $(8,3)$ by swapping coordinates.",
        "Check: at $x=3$, $y$ must equal $8$ exactly. At $x=0$, $y$ must equal $5$. Two substitutions, two constraints — fast verification.",
        "מקסימום 8 ב-$x=3$ → קודקוד $(3,8)$, פתוחה למטה. $y=a(x-3)^2+8$. חיתוך $y$ ב-$(0,5)$: $5=9a+8 \\Rightarrow a=-1/3$. משוואה: $y=-\\frac{1}{3}(x-3)^2+8$.",
        "מילה 'מקסימום' ⇒ צורת קודקוד ו-$a<0$ לפני חישוב. חיתוך $y$ ⇒ $x=0$. אל תבלבלו ערך מקסימום $8$ עם חיתוך $y$ שהוא $5$.",
        "$a=+1/3$ (סימן שגוי למקסימום) או קודקוד $(8,3)$ מהחלפת קואורדינטות.",
        "בדיקה: $x=3$ ⇒ $y=8$ בדיוק. $x=0$ ⇒ $y=5$. שתי הצבות, שני אילוצים — אימות מהיר.",
    ),
    # q8 - revenue R(x)=-2x^2+80x
    fmt_expl(
        "Standard form $R(x)=-2x^2+80x$ has $a=-2$, $b=80$. Vertex at $x=-b/(2a)=-80/(2\\times(-2))=20$. Maximum revenue $R(20)=-2(400)+1600=800$.",
        "When the model is already given in $ax^2+bx+c$, read off $a$ and $b$ — no fitting needed. Maximum/minimum is at the vertex; formula $x=-b/(2a)$ applies directly. Revenue problems use the vertex $x$ as optimal price.",
        "Using $x=+80/(2\\times(-2))=-20$ (missing minus in axis formula) or evaluating at $x=80$ instead of the vertex.",
        "Since $a=-2<0$, a maximum exists — sanity check before reporting. Bagrut word problems often ask for both the optimal $x$ **and** the maximum value; answer both.",
        "צורה $R(x)=-2x^2+80x$: $a=-2$, $b=80$. קודקוד ב-$x=-b/(2a)=-80/(2\\times(-2))=20$. הכנסה מקסימלית $R(20)=-2(400)+1600=800$.",
        "כשהמודל כבר ב-$ax^2+bx+c$, קראו $a$ ו-$b$ — אין התאמה. מקס'/מינ' בקודקוד; $x=-b/(2a)$ ישירות. בהכנסה, $x$ של קודקוד = מחיר מיטבי.",
        "$x=+80/(2\\times(-2))=-20$ (חסר מינוס בנוסחת ציר) או הצבה ב-$x=80$ במקום קודקוד.",
        "$a=-2<0$ ⇒ מקסימום קיים — sanity לפני דיווח. בבגרות לעיתים דורשים גם $x$ מיטבי **וגם** ערך מקסימלי; ענו על שניהם.",
    ),
]


def main():
    with open(TARGET, encoding="utf-8") as f:
        lesson = json.load(f)

    lesson["summary_en"] = (
        "Fit quadratic models $y=ax^2+bx+c$ from data using three-point systems, "
        "vertex form, intercept form, or least-squares regression — with full verification."
    )
    lesson["summary_he"] = (
        "התאמת מודלים ריבועיים $y=ax^2+bx+c$ מנתונים: מערכת 3 נקודות, "
        "צורת קודקוד, צורת שורשים, או רגרסיה — עם אימות מלא."
    )

    for section in lesson["sections"]:
        sid = section.get("id", "")
        kind = section.get("kind", "")

        if kind == "worked_example":
            key = sid
            if key in SECTION_BODIES:
                section["body_en_md"] = SECTION_BODIES[key]["body_en_md"]
                section["body_he_md"] = SECTION_BODIES[key]["body_he_md"]
        elif kind in SECTION_BODIES:
            section["body_en_md"] = SECTION_BODIES[kind]["body_en_md"]
            section["body_he_md"] = SECTION_BODIES[kind]["body_he_md"]

        if sid in CHECKPOINTS:
            section.update(CHECKPOINTS[sid])

    # Fix exercise Hebrew solutions (remove template filler)
    for section in lesson["sections"]:
        if section.get("kind") != "exercise_set":
            continue
        for ex in section.get("exercises", []):
            he = ex.get("solution_he", "")
            if "זהו את הכלל מהשיעור" in he or "עבדו שלב-שלב — אל תדלגו" in he:
                en = ex.get("solution_en", "")
                # Keep math from EN, wrap in Hebrew structure
                math_part = en.replace("**Solution path:** Identify the rule from this lesson, then apply it.\n\n", "")
                math_part = math_part.replace("**Solution path:** Work step by step — do not skip the setup.\n\n", "")
                math_part = math_part.replace("**Check:** Re-substitute or verify units and signs before moving on.", "")
                math_part = math_part.strip()
                ex["solution_he"] = f"**פתרון:**\n\n{math_part}\n\n**בדיקה:** הציבו חזרה את כל הנקודות הנתונות."

    # Apply question explanations
    for i, q in enumerate(lesson["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            exp_en, exp_he = QUESTION_EXPLANATIONS[i]
            q["explanation_en"] = exp_en
            q["explanation_he"] = exp_he

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Validate word counts
    errors = []
    for section in lesson["sections"]:
        kind = section.get("kind", "")
        if kind not in MIN:
            continue
        en_min, he_min = MIN[kind]
        en_w = wc(section.get("body_en_md", ""))
        he_w = wc(section.get("body_he_md", ""))
        if en_w < en_min:
            errors.append(f"{section.get('id', kind)} EN: {en_w} < {en_min}")
        if he_w < he_min:
            errors.append(f"{section.get('id', kind)} HE: {he_w} < {he_min}")
        if he_weak(section.get("body_he_md", ""), section.get("body_en_md", "")):
            errors.append(f"{section.get('id', kind)} HE weak")

    for i, q in enumerate(lesson["questions"]):
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"q{i+1} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("All section and explanation word counts OK")

    print("Running seed-lessons --dry-run...")
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
    print("Done.")


if __name__ == "__main__":
    main()
