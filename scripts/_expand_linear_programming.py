#!/usr/bin/env python3
"""Expand linear_programming.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/linear_programming.json"

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


INTRO_EN = """A bakery can make cakes and cookies. It has limited flour, sugar, and oven time. The baker wants to **maximize profit**. How many of each should be made?

This is a **linear programming (LP)** problem — one of the most practically important mathematical tools in industry. On the Israeli **4-unit Bagrut** track, LP questions typically appear as a multi-part problem worth **10–15 points**: set up variables and constraints from a word problem, graph the feasible region, list corner points, and evaluate the objective function.

Real-world uses include:
- **Airlines** assigning planes to routes under capacity limits.
- **Factories** planning production under labor and material constraints.
- **Farmers** choosing crop mixes under land and water limits.

The key insight: when constraints and the objective are all **linear**, the optimal value always occurs at a **corner (vertex)** of the feasible region. You never need to search the interior — only finitely many corners must be checked."""

INTRO_HE = """מאפייה יכולה לאפות עוגות ועוגיות. יש לה כמות מוגבלת של קמח, סוכר וזמן תנור. הקונדיטור רוצה **למקסם רווח**. כמה מכל אחד לייצר?

זוהי בעיית **תכנות לינארי (LP)** — אחד הכלים המתמטיים החשובים ביותר בתעשייה. במסלול **4 יחידות בבגרות**, שאלות LP מופיעות לרוב כבעיה רב-חלקית בשווי **10–15 נקודות**: הגדרת משתנים ואילוצים מבעיית מילים, שרטוט אזור הכדאיות, רישום קודקודים וחישוב פונקציית המטרה.

שימושים בעולם האמיתי:
- **חברות תעופה** מקצות מטוסים לטיסות תחת מגבלות קיבולת.
- **מפעלים** מתכננים ייצור תחת מגבלות עבודה וחומרים.
- **חקלאים** בוחרים תערובת גידולים תחת מגבלות קרקע ומים.

תובנת המפתח: כשהאילוצים ופונקציית המטרה **לינאריים**, הערך האופטימלי תמיד מתרחש ב**קודקוד (פינה)** של אזור הכדאיות. אין צורך לחפש בפנים — מספיק לבדוק מספר סופי של פינות."""

DEF_EN = """**Decision variables:** the quantities to determine (e.g., $x$ = units of product A, $y$ = units of product B). Always define what each variable represents in words before writing equations.

**Objective function:** the linear expression to maximize or minimize:
$$z = ax + by$$
Coefficients $a$ and $b$ come from profit, cost, or benefit per unit.

**Constraints:** linear inequalities restricting the variables:
$$c_1 x + d_1 y \\le e_1, \\quad c_2 x + d_2 y \\le e_2, \\quad x \\ge 0, \\quad y \\ge 0$$
Each constraint is a half-plane; the feasible region is their **intersection**.

**Feasible region:** all $(x, y)$ satisfying every constraint simultaneously — a convex polygon (often in the first quadrant).

**Corner Point Theorem:** if an optimal solution exists and the feasible region is bounded, it occurs at a **vertex** where two boundary lines meet. Interior points cannot beat a corner.

**Standard method:**
1. Graph all constraints and shade the feasible side.
2. Find every corner (solve pairs of boundary equations; include axis intercepts).
3. Evaluate $z$ at each corner.
4. Report the best value and the corner achieving it."""

DEF_HE = """**משתני החלטה:** הכמויות לקביעה (למשל, $x$ = יחידות מוצר א, $y$ = יחידות מוצר ב). תמיד הגדירו במילים מה כל משתנה מייצג לפני כתיבת משוואות.

**פונקציית מטרה:** הביטוי הלינארי למיקסום או מינימיזציה:
$$z = ax + by$$
המקדמים $a$ ו-$b$ באים מרווח, עלות או תועלת ליחידה.

**אילוצים:** אי-שוויונות לינאריים המגבילים את המשתנים:
$$c_1 x + d_1 y \\le e_1, \\quad c_2 x + d_2 y \\le e_2, \\quad x \\ge 0, \\quad y \\ge 0$$
כל אילוץ הוא חצי מישור; אזור הכדאיות הוא **חיתוכם**.

**אזור הכדאיות:** כל $(x, y)$ המקיימים את כל האילוצים — מצולע קמור (לעיתים ברביע הראשון).

**משפט נקודות הקודקוד:** אם פתרון אופטימלי קיים והאזור סגור, הוא מתרחש ב**קודקוד** שבו שני קווי גבול נפגשים. נקודות פנימיות לא יכולות להכות פינה.

**שיטה סטנדרטית:**
1. שרטוט כל האילוצים והצללת הצד הכדאי.
2. מציאת כל פינה (פתרון זוגות משוואות גבול; כולל חיתוכי צירים).
3. חישוב $z$ בכל פינה.
4. דיווח על הערך הטוב והפינה שמשיגה אותו."""

THEORY_EN = """**Graphing a linear inequality — three steps:**
1. Replace $\\le$ or $\\ge$ with $=$ and draw the boundary line (solid for $\\le/\\ge$, dashed only if strict — Bagrut uses non-strict).
2. Pick a test point not on the line; $(0,0)$ works unless the line passes through the origin.
3. If the test point satisfies the inequality, shade that side; otherwise shade the opposite side.

**Non-negativity:** $x \\ge 0$ keeps you right of the $y$-axis; $y \\ge 0$ above the $x$-axis. Together they restrict to the **first quadrant** — a very common Bagrut setup.

**Finding all corner points systematically:**
- List every boundary line (including $x=0$ and $y=0$ when non-negativity applies).
- For each pair of lines, solve the $2 \\times 2$ system for the intersection.
- **Feasibility check:** substitute each candidate into **every** constraint; discard points that fail any inequality.
- Record only vertices of the feasible polygon.

**Objective as parallel lines:** $z = ax + by$ is a family of parallel lines. Moving the line in the direction that improves $z$, the last feasible point touched is a corner — this is the geometric proof of the Corner Point Theorem.

**Unbounded regions:** if the feasible set extends to infinity, a **maximum** may not exist (the objective can grow without bound). A **minimum** may still exist at a corner. Always check whether the region is closed before claiming a maximum."""

THEORY_HE = """**שרטוט אי-שוויון לינארי — שלושה צעדים:**
1. החליפו $\\le$ או $\\ge$ ב-$=$ ושרטטו את קו הגבול.
2. בחרו נקודת בדיקה שאינה על הקו; $(0,0)$ מתאימה אלא אם הקו עובר בראשית.
3. אם נקודת הבדיקה מקיימת את האי-שוויון, הצלו את הצד הזה; אחרת את הצד השני.

**אי-שליליות:** $x \\ge 0$ משאיר אותנו מימין לציר $y$; $y \\ge 0$ מעל ציר $x$. יחד — **רביע ראשון**, תבנית נפוצה מאוד בבגרות.

**מציאת כל נקודות הקודקוד בשיטה:**
- רשמו כל קו גבול (כולל $x=0$ ו-$y=0$ כשיש אי-שליליות).
- לכל זוג קווים, פתרו מערכת $2 \\times 2$ לחיתוך.
- **בדיקת כדאיות:** הציבו כל מועמד ב**כל** האילוצים; השליכו נקודות שלא עומדות באף אי-שוויון.
- שמרו רק קודקודים של המצולע הכדאי.

**מטרה כקווים מקבילים:** $z = ax + by$ היא משפחת קווים מקבילים. כשמזיזים את הקו לכיוון שמשפר $z$, הנקודה הכדאית האחרונה שנוגעים בה היא פינה — זה ההוכחה הגיאומטרית למשפט הקודקוד.

**אזורים לא חסומים:** אם האזור הכדאי נמשך לאינסוף, **מקסימום** עלול לא להתקיים. **מינימום** עדיין עשוי להיות בפינה. תמיד בדקו אם האזור סגור לפני טענת מקסימום."""

WE1_EN = """**Maximize** $z = 2x + 3y$ subject to:
$$x + y \\le 4, \\quad x \\ge 0, \\quad y \\ge 0$$

This is the standard warm-up: one slanted constraint plus the first quadrant.

### Move 1: Graph the feasible region
The line $x + y = 4$ has intercepts $(4,0)$ and $(0,4)$. Test $(0,0)$ in $x+y \\le 4$: $0 \\le 4$ ✓ — shade toward the origin (below the line). Combine with $x,y \\ge 0$ to get a right triangle.

### Move 2: List corner points
- $(0, 0)$: origin.
- $(4, 0)$: $x$-intercept of $x + y = 4$.
- $(0, 4)$: $y$-intercept of $x + y = 4$.

### Move 3: Evaluate $z$ at each corner

| Point | $z = 2x + 3y$ |
|-------|---------------|
| $(0, 0)$ | $0$ |
| $(4, 0)$ | $8$ |
| $(0, 4)$ | $12$ |

### Move 4: Choose the maximum
$z = 12$ at $(0, 4)$ — the corner on the $y$-axis, where the coefficient of $y$ in the objective (3) is larger than that of $x$ (2).

**Answer:** Maximum $z = 12$ at $(0, 4)$.

**Bagrut note:** When maximizing $ax + by$, the optimum often lies on the axis of the variable with the larger coefficient — but always verify by evaluating every corner."""

WE1_HE = """**מקסמו** $z = 2x + 3y$ בכפוף ל:
$$x + y \\le 4, \\quad x \\ge 0, \\quad y \\ge 0$$

זהו חימום סטנדרטי: אילוץ אלכסוני אחד בתוספת הרביע הראשון.

### צעד 1: שרטוט אזור הכדאיות
הקו $x + y = 4$ חותך ב-$(4,0)$ ו-$(0,4)$. בדיקת $(0,0)$ ב-$x+y \\le 4$: $0 \\le 4$ ✓ — מצלים לכיוון הראשית (מתחת לקו). יחד עם $x,y \\ge 0$ מתקבל משולש ישר-זווית.

### צעד 2: רשימת נקודות קודקוד
- $(0, 0)$: ראשית.
- $(4, 0)$: חיתוך $x$ של $x + y = 4$.
- $(0, 4)$: חיתוך $y$ של $x + y = 4$.

### צעד 3: חישוב $z$ בכל פינה

| נקודה | $z = 2x + 3y$ |
|-------|---------------|
| $(0, 0)$ | $0$ |
| $(4, 0)$ | $8$ |
| $(0, 4)$ | $12$ |

### צעד 4: בחירת המקסימום
$z = 12$ ב-$(0, 4)$ — הפינה על ציר $y$, שם מקדם $y$ במטרה (3) גדול ממקדם $x$ (2).

**תשובה:** מקסימום $z = 12$ בנקודה $(0, 4)$.

**הערת בגרות:** במיקסום $ax + by$, האופטימום לעיתים על ציר המשתנה עם המקדם הגדול — אך תמיד אמתו בחישוב כל הפינות."""

WE2_EN = """**Problem:** A factory makes tables ($x$) and chairs ($y$).
- Each table: 4 work hours, 3 kg wood.
- Each chair: 2 work hours, 5 kg wood.
- Available: 40 hours, 45 kg wood.
- Profit: 200₪/table, 150₪/chair. **Maximize profit.**

### Move 1: Set up the LP
$$\\text{Maximize: } z = 200x + 150y$$
$$4x + 2y \\le 40 \\implies 2x + y \\le 20$$
$$3x + 5y \\le 45, \\quad x, y \\ge 0$$

### Move 2: Find all corner points
- $(0, 0)$: origin.
- $(10, 0)$: from $2x + y = 20$ with $y = 0$. Check wood: $3(10) = 30 \\le 45$ ✓.
- $(0, 9)$: from $3x + 5y = 45$ with $x = 0$. Check hours: $2(0)+9 = 9 \\le 20$ ✓.
- Intersection of $2x+y=20$ and $3x+5y=45$:
  - $y = 20 - 2x$ → $3x + 5(20-2x) = 45$ → $-7x = -55$ → $x = 55/7$, $y = 30/7$.

### Move 3: Evaluate $z$ at each corner

| Corner | $z = 200x + 150y$ |
|--------|-------------------|
| $(0,0)$ | $0$ |
| $(10,0)$ | $2000$ |
| $(0,9)$ | $1350$ |
| $(55/7, 30/7)$ | $15500/7 \\approx 2214$ |

**Answer:** Maximum profit ≈ **2214₪** at $x = 55/7 \\approx 7.86$ tables, $y = 30/7 \\approx 4.29$ chairs.

*Integer note:* In practice, check nearby integer points: $(8,4)$ gives $z = 2200$ and is feasible — close to the LP optimum."""

WE2_HE = """**בעיה:** מפעל מייצר שולחנות ($x$) וכסאות ($y$).
- כל שולחן: 4 שעות עבודה, 3 ק\"ג עץ.
- כל כסא: 2 שעות, 5 ק\"ג עץ.
- זמינות: 40 שעות, 45 ק\"ג עץ.
- רווח: 200₪/שולחן, 150₪/כסא. **מקסמו רווח.**

### צעד 1: הגדרת התכנות
$$\\text{מקסמו: } z = 200x + 150y$$
$$2x + y \\le 20, \\quad 3x + 5y \\le 45, \\quad x, y \\ge 0$$

### צעד 2: מציאת כל נקודות הקודקוד
- $(0, 0)$: ראשית.
- $(10, 0)$: מ-$2x + y = 20$ עם $y = 0$. בדיקת עץ: $30 \\le 45$ ✓.
- $(0, 9)$: מ-$3x + 5y = 45$ עם $x = 0$. בדיקת שעות: $9 \\le 20$ ✓.
- חיתוך $2x+y=20$ ו-$3x+5y=45$:
  - $y = 20 - 2x$ → $3x + 100 - 10x = 45$ → $x = 55/7$, $y = 30/7$.

### צעד 3: חישוב $z$ בכל פינה

| פינה | $z$ |
|------|-----|
| $(0,0)$ | $0$ |
| $(10,0)$ | $2000$ |
| $(0,9)$ | $1350$ |
| $(55/7, 30/7)$ | $15500/7 \\approx 2214$ |

**תשובה:** מקסימום רווח $\\approx$ **2214₪** ב-$x \\approx 7.86$, $y \\approx 4.29$.

*הערת שלמים:* בפועל בדקו נקודות שלמות קרובות: $(8,4)$ נותן $z = 2200$ וכדאית — קרוב לאופטימום."""

WE3_EN = """**Problem:** Maximize $z = 5x + 4y$ subject to:
$$6x + 4y \\le 24, \\quad x + 2y \\le 6, \\quad x, y \\ge 0$$

Classic Bagrut 4pt: two slanted constraints plus the first quadrant.

### Move 1: Simplify constraints
- $6x + 4y \\le 24 \\implies 3x + 2y \\le 12$
- $x + 2y \\le 6$

### Move 2: Find every corner
*Corner A:* $(0, 0)$.

*Corner B:* $x = 0$ in $x+2y=6$: $y = 3$ → $(0, 3)$. Check $3x+2y = 6 \\le 12$ ✓.

*Corner C:* $y = 0$ in $3x+2y=12$: $x = 4$ → $(4, 0)$. Check $x+2y = 4 \\le 6$ ✓.

*Corner D:* Intersection of $3x+2y=12$ and $x+2y=6$:
$$(3x+2y) - (x+2y) = 6 \\implies 2x = 6 \\implies x = 3, \\quad y = 3/2$$
Point $(3, 3/2)$. Verify both constraints: $3(3)+2(1.5)=12$ ✓, $3+3=6$ ✓.

### Move 3: Evaluate $z$

| Corner | $z = 5x + 4y$ |
|--------|---------------|
| $(0, 0)$ | $0$ |
| $(0, 3)$ | $12$ |
| $(4, 0)$ | $20$ |
| $(3, 1.5)$ | $21$ |

**Answer:** Maximum $z = 21$ at $(3, 1.5)$.

**Bagrut note:** After finding an intersection algebraically, always substitute back into **both** original constraints — Corner B from $3x+2y=12$ alone would give $(0,6)$, which fails $x+2y \\le 6$."""

WE3_HE = """**בעיה:** מקסמו $z = 5x + 4y$ בכפוף ל:
$$6x + 4y \\le 24, \\quad x + 2y \\le 6, \\quad x, y \\ge 0$$

קלאסי בבגרות 4 יח': שני אילוצים אלכסוניים בתוספת הרביע הראשון.

### צעד 1: פישוט אילוצים
- $3x + 2y \\le 12$
- $x + 2y \\le 6$

### צעד 2: מציאת כל הפינות
*פינה א:* $(0, 0)$.

*פינה ב:* $x = 0$ ב-$x+2y=6$: $y = 3$ → $(0, 3)$. בדיקה: $3x+2y = 6 \\le 12$ ✓.

*פינה ג:* $y = 0$ ב-$3x+2y=12$: $x = 4$ → $(4, 0)$. בדיקה: $x+2y = 4 \\le 6$ ✓.

*פינה ד:* חיתוך $3x+2y=12$ ו-$x+2y=6$:
$$2x = 6 \\implies x = 3, \\quad y = 3/2$$
נקודה $(3, 3/2)$. אימות: $12$ ✓ ו-$6$ ✓.

### צעד 3: חישוב $z$

| פינה | $z$ |
|------|-----|
| $(0, 0)$ | $0$ |
| $(0, 3)$ | $12$ |
| $(4, 0)$ | $20$ |
| $(3, 1.5)$ | $21$ |

**תשובה:** מקסימום $z = 21$ ב-$(3, 1.5)$.

**הערת בגרות:** אחרי מציאת חיתוך אלגברית, הציבו ב**שני** האילוצים — חיתוך $3x+2y=12$ בלבד עם $x=0$ נותן $(0,6)$, שלא עומד ב-$x+2y \\le 6$."""

CHK1_EN = """**Setup:** Minimize $z = x + 2y$ subject to $x + y \\ge 3$, $x \\ge 0$, $y \\ge 0$.

### Move 1: Graph
The line $x + y = 3$ has intercepts $(3,0)$ and $(0,3)$. Test $(0,0)$ in $x+y \\ge 3$: fails — shade the side **away** from the origin (above/right of the line). Non-negativity keeps us in the first quadrant.

### Move 2: Corner points on the boundary
The feasible region is unbounded above, but corners on the constraint boundary are:
- $(3, 0)$: where $x+y=3$ meets the $x$-axis.
- $(0, 3)$: where $x+y=3$ meets the $y$-axis.

### Move 3: Evaluate $z$
- $z(3, 0) = 3 + 0 = 3$
- $z(0, 3) = 0 + 6 = 6$

### Move 4: Minimum
$z = 3$ at $(3, 0)$ — the corner with smaller $y$-coefficient contribution when minimizing.

**Answer:** Minimum $z = 3$ at $(3, 0)$."""

CHK1_HE = """**הגדרה:** מינימיזו $z = x + 2y$ בכפוף ל-$x + y \\ge 3$, $x \\ge 0$, $y \\ge 0$.

### צעד 1: שרטוט
הקו $x + y = 3$ חותך ב-$(3,0)$ ו-$(0,3)$. בדיקת $(0,0)$ ב-$x+y \\ge 3$: נכשל — מצלים **הרחק** מהראשית (מעל/ימין לקו). אי-שליליות שומרות על הרביע הראשון.

### צעד 2: פינות על הגבול
האזור לא חסום למעלה, אך פינות על קו האילוץ:
- $(3, 0)$: חיתוך $x+y=3$ עם ציר $x$.
- $(0, 3)$: חיתוך $x+y=3$ עם ציר $y$.

### צעד 3: חישוב $z$
- $z(3, 0) = 3$
- $z(0, 3) = 6$

### צעד 4: מינימום
$z = 3$ ב-$(3, 0)$ — הפינה עם תרומה קטנה יותר ממקדם $y$.

**תשובה:** מינימום $z = 3$ ב-$(3, 0)$."""

CHK2_EN = """**Setup:** Maximize $z = 50x + 80y$ with $x + y \\le 10$, $x \\le 6$, $y \\le 8$, $x,y \\ge 0$.

### Move 1: Identify boundary lines
Four constraints form a rectangle-like region: $x+y=10$, $x=6$, $y=8$, and the axes.

### Move 2: Find all corners
- $(0,0)$, $(6,0)$, $(0,8)$
- $(6,4)$: $x=6$ meets $x+y=10$ → $y=4$. Check $y \\le 8$ ✓.
- $(2,8)$: $y=8$ meets $x+y=10$ → $x=2$. Check $x \\le 6$ ✓.

### Move 3: Evaluate $z = 50x + 80y$

| Corner | $z$ |
|--------|-----|
| $(0,0)$ | $0$ |
| $(6,0)$ | $300$ |
| $(6,4)$ | $620$ |
| $(2,8)$ | $740$ |
| $(0,8)$ | $640$ |

**Answer:** Maximum profit $z = 740$ at $(2, 8)$ — product B has higher profit per unit (80 vs 50)."""

CHK2_HE = """**הגדרה:** מקסמו $z = 50x + 80y$ עם $x + y \\le 10$, $x \\le 6$, $y \\le 8$, $x,y \\ge 0$.

### צעד 1: קווי גבול
ארבעה אילוצים יוצרים אזור דמוי מלבן: $x+y=10$, $x=6$, $y=8$, והצירים.

### צעד 2: כל הפינות
- $(0,0)$, $(6,0)$, $(0,8)$
- $(6,4)$: $x=6$ עם $x+y=10$ → $y=4$. בדיקה: $y \\le 8$ ✓.
- $(2,8)$: $y=8$ עם $x+y=10$ → $x=2$. בדיקה: $x \\le 6$ ✓.

### צעד 3: חישוב $z = 50x + 80y$

| פינה | $z$ |
|------|-----|
| $(0,0)$ | $0$ |
| $(6,0)$ | $300$ |
| $(6,4)$ | $620$ |
| $(2,8)$ | $740$ |
| $(0,8)$ | $640$ |

**תשובה:** רווח מקסימלי $z = 740$ ב-$(2, 8)$ — מוצר B עם רווח גבוה יותר ליחידה (80 לעומת 50)."""

METHOD_EN = """| Step | Action | Exam marks |
|------|--------|------------|
| 1 | Define variables in words | 1–2 pts |
| 2 | Write objective $z = ax + by$ (max or min) | 1–2 pts |
| 3 | Translate each resource limit into an inequality | 2–3 pts |
| 4 | Graph each constraint; shade feasible side | 2–3 pts |
| 5 | Identify feasible region (overlap of shaded areas) | 1 pt |
| 6 | List all corner points algebraically | 2–3 pts |
| 7 | Evaluate $z$ at every corner in a table | 2 pts |
| 8 | State optimal value + point; interpret in context | 1–2 pts |

**Shading shortcut:** Test $(0,0)$ unless it lies on a boundary line. For $x \\ge 0$, $y \\ge 0$, start in the first quadrant.

**Feasibility rule:** Every intersection candidate must satisfy **all** constraints — one failed check disqualifies the point.

**Decision workflow:** Word problem → equations → graph → corners → table → answer with units (₪, kg, hours).

**Exam tip:** Number corners on your graph as A, B, C… and mirror that in your evaluation table — graders match labels to algebra."""

METHOD_HE = """| שלב | פעולה | נקודות |
|-----|-------|--------|
| 1 | הגדירו משתנים במילים | 1–2 נק' |
| 2 | כתבו מטרה $z = ax + by$ (מקס/מין) | 1–2 נק' |
| 3 | תרגמו כל מגבלת משאב לאי-שוויון | 2–3 נק' |
| 4 | שרטטו כל אילוץ; הצלו צד כדאי | 2–3 נק' |
| 5 | זיהו אזור כדאיות (חפיפת הצללות) | 1 נק' |
| 6 | רשמו כל קודקוד אלגברית | 2–3 נק' |
| 7 | חשבו $z$ בכל פינה בטבלה | 2 נק' |
| 8 | ציינו ערך אופטימלי + נקודה; פרשו בהקשר | 1–2 נק' |

**קיצור הצללה:** בדקו $(0,0)$ אלא אם על קו גבול. ל-$x,y \\ge 0$ — התחילו ברביע הראשון.

**כלל כדאיות:** כל מועמד חיתוך חייב לעמוד ב**כל** האילוצים — כישלון אחד פוסל את הנקודה.

**זרימת עבודה:** בעיית מילים → משוואות → גרף → פינות → טבלה → תשובה עם יחידות.

**טיפ לבחינה:** סמנו פינות A, B, C… בגרף ובטבלה — בוחנים מקשרים תוויות לאלגברה."""

PITFALL_EN = """**Mistake 1 — Missing a corner point.**
Every vertex comes from an intersection of exactly two active boundary lines. Systematically pair **all** constraint boundaries — including $x=0$ and $y=0$. A missing corner means a wrong optimum.

**Mistake 2 — Not verifying feasibility.**
After solving two equations, substitute the candidate into **every** inequality. Example: the intersection of $3x+2y=12$ with $x=0$ gives $(0,6)$, but if $x+2y \\le 6$ is also a constraint, that point fails. Only feasible corners count.

**Mistake 3 — Shading the wrong half-plane.**
Use the origin test: plug $(0,0)$ into the inequality. If true, shade toward the origin; if false, shade away. For $\\ge$ constraints, the feasible side is opposite to $\\le$ — double-check before drawing the polygon.

**Mistake 4 — Confusing maximize with minimize direction.**
When minimizing, pick the **smallest** $z$ among corners, not the largest. Students who habitually choose the maximum from practice max problems lose easy marks on min problems."""

PITFALL_HE = """**טעות 1 — פספוס נקודת קודקוד.**
כל קודקוד נובע מחיתוך של בדיוק שני קווי גבול פעילים. זוגו **כל** הגבולות — כולל $x=0$ ו-$y=0$. פינה חסרה = אופטימום שגוי.

**טעות 2 — אי-אימות כדאיות.**
אחרי פתרון שתי משוואות, הציבו ב**כל** האי-שוויונות. דוגמה: חיתוך $3x+2y=12$ עם $x=0$ נותן $(0,6)$, אך אם $x+2y \\le 6$ קיים — הנקודה נכשלת. רק פינות כדאיות נספרות.

**טעות 3 — הצללת חצי מישור שגוי.**
בדיקת ראשית: $(0,0)$ באי-שוויון. אם נכון — הצללה לכיוון הראשית; אחרת — הרחק. ב-$\\ge$ הצד הכדאי הפוך מ-$\\le$ — בדקו לפני שרטוט.

**טעות 4 — בלבול מקסימום ומינימום.**
במינימיזציה, בחרו את $z$ **הקטן** ביותר בין הפינות, לא הגדול. תלמידים שרגילים למקסימום מפסידים נקודות קלות בשאלות מינימום."""

WHY_EN = """Linear programming connects **analytic geometry** (graphing lines and regions) with **optimization** — a pattern that repeats in economics, engineering, and university operations research.

On the 4-unit Bagrut, LP rewards structured problem-solving: translate words to math, visualize the feasible region, and finish with a clear numerical answer. These same skills appear in **linear regression** (fitting lines to data) and **systems of inequalities** from earlier units.

Beyond exams, LP explains how airlines, logistics firms, and even school schedulers allocate scarce resources. Understanding why the optimum sits at a corner builds intuition for more advanced topics like the simplex algorithm at university level."""

WHY_HE = """תכנות לינארי מחבר **גאומטריה אנליטית** (שרטוט קווים ואזורים) עם **אופטימיזציה** — דפוס שחוזר בכלכלה, הנדסה ומחקר ביצועים באוניברסיטה.

בבגרות 4 יח', LP מעריך פתרון מובנה: תרגום מילים למתמטיקה, הצגה גרפית של אזור כדאי, וסיום בתשובה מספרית ברורה. כישורים אלה מופיעים גם ב**רגרסיה לינארית** וב**מערכות אי-שוויונות** מיחידות קודמות.

מעבר לבחינות, LP מסביר כיצד חברות תעופה, לוגיסטיקה ואפילו מתזמני בתי ספר מקצים משאבים מוגבלים. הבנה למה האופטימום בפינה בונה אינטואיציה לנושאים מתקדמים כמו שיטת הסימפлекс באוניברסיטה."""

BEFORE_EN = """**Key steps:**
1. Define variables with units.
2. Write $z = ax + by$ (state max or min).
3. List all constraints as linear inequalities.
4. Graph each line; shade the feasible half-plane.
5. Mark the feasible polygon.
6. Find every corner (solve $2 \\times 2$ systems).
7. Build a table: corner → $z$ value.
8. Pick the best corner; answer in context (₪, litres, etc.).

**Corner Point Theorem:** Optimal value (when it exists on a bounded region) is **always** at a vertex.

**Typical Bagrut 4pt patterns:**
1. Word problem setup (3–4 marks).
2. Graph feasible region (3 marks).
3. Corner table + optimal value (4–5 marks).

**Marking tips:** Label constraint lines on the graph. Show feasibility checks for intersection points. Box the final answer with units."""

BEFORE_HE = """**שלבי מפתח:**
1. הגדירו משתנים עם יחידות.
2. כתבו $z = ax + by$ (ציינו מקס/מין).
3. רשמו כל האילוצים כאי-שוויונות לינאריים.
4. שרטטו כל קו; הצלו חצי מישור כדאי.
5. סמנו את המצולע הכדאי.
6. מצאו כל פינה (פתרון מערכות $2 \\times 2$).
7. בנו טבלה: פינה → ערך $z$.
8. בחרו את הפינה הטובה; ענו בהקשר (₪, ליטר וכו').

**משפט הקודקוד:** הערך האופטימלי (כשקיים באזור חסום) **תמיד** בקודקוד.

**דפוסי בגרות 4 יח':**
1. הגדרה מבעיית מילים (3–4 נק').
2. שרטוט אזור כדאיות (3 נק').
3. טבלת פינות + ערך אופטימלי (4–5 נק').

**טיפים לניקוד:** סמנו קווי אילוץ בגרף. הציגו בדיקות כדאיות לנקודות חיתוך. הקיפו תשובה סופית עם יחידות."""

SUMMARY_EN = """- **Linear programming** maximizes or minimizes $z = ax + by$ subject to linear constraints.
- The **feasible region** is the intersection of half-planes — usually a convex polygon.
- **Corner Point Theorem:** the optimal value (when it exists on a bounded region) occurs at a vertex.
- **Method:** graph constraints → list all corners → evaluate $z$ in a table → pick the best.
- **Word problems:** define variables, build constraints from resource limits, verify corner feasibility, interpret the answer with units.
- **Watch for:** wrong shading, missing corners, unverified intersections, and confusing min with max."""

SUMMARY_HE = """- **תכנות לינארי** ממקסם או ממזער $z = ax + by$ בכפוף לאילוצים לינאריים.
- **אזור הכדאיות** הוא חיתוך של חצאי מישורים — לרוב מצולע קמור.
- **משפט הקודקוד:** הערך האופטימלי (כשקיים באזור חסום) מתרחש בקודקוד.
- **שיטה:** שרטוט אילוצים → רישום כל הפינות → חישוב $z$ בטבלה → בחירת הטוב.
- **בעיות מילים:** הגדירו משתנים, בנו אילוצים ממגבלות משאב, אמתו כדאיות פינות, פרשו תשובה עם יחידות.
- **שימו לב:** הצללה שגויה, פינות חסרות, חיתוכים לא מאומתים, ובלבול מין/מקס."""

EXPLS = {
    1: fmt_expl(
        "The feasible triangle has corners $(0,0)$, $(5,0)$, and $(0,10)$ from $2x+y=10$ with $x,y \\ge 0$. Evaluating $z = x+y$: values are $0$, $5$, and $10$. Maximum $z = 10$ at $(0,10)$.",
        "Graph $2x+y=10$ with intercepts $(5,0)$ and $(0,10)$. Shade below the line in the first quadrant. The Corner Point Theorem says check only vertices — here three corners suffice.",
        "Using $(0,0)$ as the maximum because it is simplest, or stopping after finding $(5,0)$ with $z=5$ without checking $(0,10)$.",
        "Draw intercepts first — for $2x+y=10$, they are always corners. A quick table of three rows earns full marks on easy Bagrut LP parts.",
        "המשולש הכדאי: פינות $(0,0)$, $(5,0)$, $(0,10)$ מ-$2x+y=10$ עם $x,y \\ge 0$. $z = x+y$: $0$, $5$, $10$. מקסימום $z = 10$ ב-$(0,10)$.",
        "שרטטו $2x+y=10$ עם חיתוכים $(5,0)$ ו-$(0,10)$. הצלילו מתחת לקו ברביע הראשון. משפט הקודקוד: בדקו רק קודקודים — כאן שלוש פינות מספיקות.",
        "בחירת $(0,0)$ כמקסימום כי היא הפשוטה, או עצירה ב-$(5,0)$ עם $z=5$ בלי לבדוק $(0,10)$.",
        "שרטטו חיתוכים תחילה — ל-$2x+y=10$ הם תמיד פינות. טבלה של שלוש שורות מניבה ניקוד מלא בחלקים קלים.",
    ),
    2: fmt_expl(
        "Boundary corners on $x+y=4$ in the first quadrant: $(4,0)$ and $(0,4)$. $z(4,0)=12$ and $z(0,4)=8$. Minimum is $8$ at $(0,4)$.",
        "For $\\ge$ constraints, feasible region lies **above** the boundary line. Only corners on the line segment between axis intercepts matter for a minimization with bounded feasible set along that edge.",
        "Minimizing but picking the larger value $12$ at $(4,0)$, or forgetting that $(0,0)$ fails $x+y \\ge 4$ and is not feasible.",
        "On min problems, underline the word **minimize** and circle the smallest $z$ in your table — examiners report this as the top LP error.",
        "פינות על $x+y=4$ ברביע הראשון: $(4,0)$ ו-$(0,4)$. $z(4,0)=3\\cdot4+2\\cdot0=12$ ו-$z(0,4)=3\\cdot0+2\\cdot4=8$. מינימום $z=8$ ב-$(0,4)$ — הערך הקטן מבין שתי הפינות הכדאיות על קו הגבול.",
        "ב-$\\ge$, האזור הכדאי **מעל** קו הגבול (הצללה הרחק מהראשית). רק פינות על הקטע בין חיתוכי הצירים $(4,0)$ ו-$(0,4)$ רלוונטיות; $(0,0)$ אינה כדאית כי $0+0<4$. השוו $z$ בכל פינה כדאית ובחרו את הקטן.",
        "מינימיזציה אך בחירת $12$ ב-$(4,0)$ כי המספר גדול יותר, או שכחה ש-$(0,0)$ לא כדאית ולכן אינה נכללת בטבלה.",
        "בשאלות מין, הדגישו **מינימום** והקיפו את $z$ הקטן בטבלה — בוחנים מדווחים שזו הטעות הנפוצה ביותר ב-LP.",
    ),
    3: fmt_expl(
        "Corners from pairwise intersections: $(1,2)$ from $x=1$ and $y=2$; $(1,5)$ from $x=1$ and $x+y=6$; $(4,2)$ from $y=2$ and $x+y=6$. All three satisfy $x+y \\le 6$.",
        "With vertical ($x=1$) and horizontal ($y=2$) constraints, corners come from crossing these with the slanted line $x+y=6$. List each pair systematically.",
        "Missing $(1,5)$ or $(4,2)$, or including $(6,0)$ which fails $x \\ge 1$.",
        "When constraints include $x \\ge k$ and $y \\ge m$, draw the vertical and horizontal lines first — corners often involve them.",
        "פינות מחיתוכים: $(1,2)$ מ-$x=1$ ו-$y=2$; $(1,5)$ מ-$x=1$ ו-$x+y=6$; $(4,2)$ מ-$y=2$ ו-$x+y=6$. שלושתן עומדות ב-$x+y \\le 6$.",
        "עם אילוצים אנכיים ($x=1$) ואופקיים ($y=2$), פינות נוצרות מחיתוכם עם $x+y=6$. רשמו כל זוג בשיטתיות.",
        "החמצת $(1,5)$ או $(4,2)$, או הכללת $(6,0)$ שלא עומד ב-$x \\ge 1$.",
        "כשיש $x \\ge k$ ו-$y \\ge m$, שרטטו קווים אנכיים/אופקיים תחילה — פינות לרוב כוללות אותם.",
    ),
    4: fmt_expl(
        "Check each constraint: $2+3=5 \\le 6$ ✓; $x=2 \\ge 0$ ✓; $y=3 \\ge 0$ ✓; $2(2)+3=7 \\le 8$ ✓. All pass — $(2,3)$ is feasible.",
        "Feasibility testing is independent of optimization: substitute the point into every inequality. One failure means the point lies outside the region.",
        "Checking only $x+y \\le 6$ and forgetting $2x+y \\le 8$, which would incorrectly accept points like $(3,3)$.",
        "On Bagrut, feasibility sub-questions are quick marks — write each substitution on its own line with ✓ or ✗.",
        "בדיקת כל אילוץ בנפרד: $x+y$: $2+3=5 \\le 6$ ✓; אי-שליליות: $x=2 \\ge 0$ ✓, $y=3 \\ge 0$ ✓; אילוץ שלישי: $2(2)+3=7 \\le 8$ ✓. כל ארבעת הבדיקות עוברות — $(2,3)$ נמצאת בתוך אזור הכדאיות.",
        "בדיקת כדאיות נפרדת מאופטימיזציה: הציבו את הנקודה בכל אי-שוויון, אחד-אחד. כישלון באילוץ אחד מספיק כדי להסיק שהנקודה מחוץ למצולע. אין צורך לשרטט גרף לשאלה כזו — רק חישוב.",
        "בדיקה רק של $x+y \\le 6$ והתעלמות מ-$2x+y \\le 8$ — טעות שמקבלת בטעות נקודות כמו $(3,3)$ שעוברות את האילוץ הראשון אך נכשלות בשלישי.",
        "שאלות כדאיות בבגרות = נקודות מהירות — כתבו כל הצבה בשורה נפרדת עם ✓ או ✗; המבנה הזה מניב ניקוד מלא גם כשהתשובה הסופית היא רק 'כן'.",
    ),
    5: fmt_expl(
        "Corners: $(0,0)$, $(4,0)$, $(4,4)$, $(2,6)$, $(0,6)$. Values of $z=3x+5y$: $0, 12, 32, 36, 30$. Maximum $z=36$ at $(2,6)$ where the $y$-coefficient (5) pulls the optimum toward higher $y$.",
        "Three upper-bound constraints ($x \\le 4$, $y \\le 6$, $x+y \\le 8$) create a pentagon. Find corners from each pair of active boundaries, then verify all constraints.",
        "Missing $(2,6)$ — the intersection of $y=6$ and $x+y=8$ — which is often the true optimum when $y$ has the larger coefficient.",
        "When $z=3x+5y$ and $y$ has the bigger coefficient, scan corners with large $y$ first as a sanity check, but still evaluate all.",
        "פינות: $(0,0)$, $(4,0)$, $(4,4)$, $(2,6)$, $(0,6)$. $z=3x+5y$: $0, 12, 32, 36, 30$. מקסימום $z=36$ ב-$(2,6)$ — מקדם $y$ (5) גדול ממקדם $x$ (3), ולכן האופטימום נמשך לפינה עם $y$ גבוה יחסית.",
        "שלושה גבולות עליונים ($x \\le 4$, $y \\le 6$, $x+y \\le 8$) יוצרים מחומש בפינה הראשונה. מצאו פינות מכל זוג קווי גבול פעיל — למשל $y=6$ עם $x+y=8$ נותן $(2,6)$ — ואמתו שכל אילוץ מתקיים.",
        "החמצת $(2,6)$ — חיתוך $y=6$ ו-$x+y=8$ — שהיא לעיתים קרובות האופטימום האמיתי כשמקדם $y$ במטרה גדול.",
        "כש-$y$ עם מקדם גדול במטרה, בדקו קודם פינות עם $y$ גבוה כבדיקת הגיון — אך חובה לחשב $z$ בכל הפינות בטבלה מסודרת.",
    ),
    6: fmt_expl(
        "Objective $z=300x+500y$. Corners from $x=20$, $y=10$, and $x+y=100$: $(20,10)$, $(90,10)$, $(20,80)$. Values: $11000$, $32000$, $46000$. Maximum $46000$ at $(20,80)$ — corn's higher profit (500 vs 300) dominates.",
        "Lower-bound constraints ($x \\ge 20$, $y \\ge 10$) shift the region away from the origin. Corners lie where these vertical/horizontal lines meet the upper bound $x+y=100$.",
        "Choosing $(90,10)$ because $x$ is larger, ignoring that corn earns 500₪/acre vs wheat's 300₪/acre.",
        "In word problems, circle the profit coefficients before graphing — they predict which corner wins before you calculate.",
        "מטרה $z=300x+500y$. פינות מ-$x=20$, $y=10$, $x+y=100$: $(20,10)$, $(90,10)$, $(20,80)$. ערכים: $11000$, $32000$, $46000$. מקסימום $46000$ ב-$(20,80)$ — תירס עם רווח גבוה יותר.",
        "אילוצי תחתון ($x \\ge 20$, $y \\ge 10$) מזיזים את האזור מהראשית. פינות בחיתוך קווים אלה עם $x+y=100$.",
        "בחירת $(90,10)$ כי $x$ גדול, התעלמות מ-500₪/דונם תירס לעומת 300₪ חיטה.",
        "בבעיות מילים, הדגישו מקדמי רווח לפני שרטוט — הם חוזים איזו פינה תנצח.",
    ),
    7: fmt_expl(
        "Intersection of $x+y=4$ and $2x+y=6$: subtract to get $x=2$, $y=2$. Other corners: $(0,6)$ from $2x+y=6$ with $x=0$, and $(4,0)$ from $x+y=4$ with $y=0$. Values $z=18, 10, 8$. Minimum $z=8$ at $(4,0)$.",
        "Two $\\ge$ constraints create an unbounded feasible region above both lines, but the minimum still occurs at a corner on the boundary — here $(4,0)$ wins because $x$ has the smaller coefficient in $z=2x+3y$.",
        "Picking $(2,2)$ with $z=10$ because it looks like the 'center,' or maximizing instead of minimizing.",
        "For min with $z=2x+3y$, compare corners on the $x$-axis first — lower $y$ helps when minimizing.",
        "חיתוך $x+y=4$ ו-$2x+y=6$: $x=2$, $y=2$. פינות נוספות: $(0,6)$, $(4,0)$. $z$: $18, 10, 8$. מינימום $z=8$ ב-$(4,0)$.",
        "שני $\\ge$ יוצרים אזור לא חסום, אך המינימום עדיין בפינה — $(4,0)$ מנצחת כי מקדם $x$ קטן יותר ב-$z=2x+3y$.",
        "בחירת $(2,2)$ עם $z=10$ כי נראית 'מרכז', או מקסימום במקום מינימום.",
        "במין עם $z=2x+3y$, השוו פינות על ציר $x$ — $y$ נמוך עוזר במינימום.",
    ),
    8: fmt_expl(
        "The objective $z=ax+by$ is a family of parallel lines with slope $-a/b$. Moving the line in the direction that improves $z$, the last feasible point is always a vertex of the convex polygon. No interior or edge-midpoint can beat a corner.",
        "Geometric proof: if a point inside the polygon were optimal, you could move along the objective's gradient direction while staying feasible and improve $z$ — contradiction. Convexity ensures the last touch point is a vertex.",
        "Saying 'because corners are the easiest to calculate' without explaining parallel lines or convexity — Bagrut proof questions need the geometric argument.",
        "Use the phrase 'parallel lines moving in the direction of improvement' — it matches the official 4pt marking rubric for LP explanation questions.",
        "המטרה $z=ax+by$ היא משפחת קווים מקבילים. כשמזיזים בכיוון שמשפר $z$, הנקודה הכדאית האחרונה היא תמיד קודקוד. אין נקודה פנימית שיכולה להכות פינה.",
        "הוכחה גיאומטרית: אם נקודה פנימית הייתה אופטימלית, אפשר היה לזוז בכיוון שמשפר את $z$ ולהישאר כדאיים — סתירה. קמירות המצולע מבטיחה שהמגע האחרון הוא בקודקוד.",
        "לומר 'כי קל לחשב פינות' בלי קווים מקבילים או קמירות — שאלות הוכחה דורשות טיעון גיאומטרי.",
        "השתמשו ב'קווים מקבילים בכיוון שיפור' — זהו הניסוח שמצפים ממנו בבגרות 4 יח' בשאלות הסבר.",
    ),
}


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in MIN:
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            min_en, min_he = MIN[kind]
            if en_w < min_en:
                errors.append(f"{kind} en {en_w} < {min_en}")
            if he_w < min_he:
                errors.append(f"{kind} he {he_w} < {min_he}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{kind}: weak Hebrew body")
    for q in data["questions"]:
        ew = wc(q.get("explanation_en", ""))
        hw = wc(q.get("explanation_he", ""))
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
            if "x + 2y" in body and "Minimize" in body:
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
