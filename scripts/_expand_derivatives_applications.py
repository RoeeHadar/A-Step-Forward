#!/usr/bin/env python3
"""Expand derivatives_applications.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/derivatives_applications.json"


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he):
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


SECTION_PATCHES = {
    "intro": {
        "body_en_md": """Once you can compute $f'(x)$, the derivative becomes a **shape detector** for graphs and a **decision engine** for optimization. The sign of $f'$ tells you where a function rises or falls; the sign of $f''$ tells you whether the graph bends upward like a bowl or downward like a hill. Together, $f'$ and $f''$ answer the questions examiners love: *Where are the peaks and valleys? Where does the curve change bend? What is the best choice under a constraint?*

**The six signals every investigator uses:**
- $f'(x) > 0$: $f$ is **increasing** on that interval.
- $f'(x) < 0$: $f$ is **decreasing**.
- $f'(x) = 0$: a **critical point** — a candidate for local max or min.
- $f''(x) > 0$: **concave up** (holds water; tangent slopes increase).
- $f''(x) < 0$: **concave down** (sheds water; tangent slopes decrease).
- $f''$ changes sign at $x_0$: an **inflection point** where concavity switches.

In the Bagrut 4- and 5-unit exams, **function investigation** ($\\text{חקירת פונקציה}$) is the single most common derivative application: find critical points, classify them, locate inflection, sketch asymptotes, and connect the graph to the sign tables. **Optimization word problems** — fencing, boxes, revenue — appear almost every year. Mastering these patterns turns derivative rules into full exam points.""",
        "body_he_md": """ברגע שיודעים לחשב $f'(x)$, הנגזרת הופכת ל**גלאי צורה** של גרפים ול**מנוע החלטות** באופטימיזציה. סימן $f'$ אומר איפה הפונקציה עולה או יורדת; סימן $f''$ אומר אם הגרף כפוף כלפי מעלה כמו קערה או כלפי מטה כמו גבעה. יחד, $f'$ ו-$f''$ עונים על השאלות שבוחני הבגרות אוהבים: *איפה שיאים ושפלים? איפה העקומה משנה כיוון כיפוף? מה הבחירה הטובה ביותר תחת אילוץ?*

**ששת האותות שכל חוקר פונקציה משתמש בהם:**
- $f'(x) > 0$: $f$ **עולה** בקטע.
- $f'(x) < 0$: $f$ **יורדת**.
- $f'(x) = 0$: **נקודה קריטית** — מועמדת למקסימום או מינימום מקומי.
- $f''(x) > 0$: **קעורה כלפי מעלה** (שקערורית; שיפוע המשיק גדל).
- $f''(x) < 0$: **קעורה כלפי מטה** (קמורה; שיפוע המשיק קטן).
- $f''$ משנה סימן ב-$x_0$: **נקודת פיתול** שבה הקעירות מתהפכת.

בבגרות 4 ו-5 יחידות, **חקירת פונקציה** היא היישום הנפוץ ביותר של נגזרות: נקודות קיצון, סיווג, פיתול, אסימפטוטות ושרטוט. **בעיות אופטימיזציה** — גדר, קופסאות, הכנסה — מופיעות כמעט בכל שנה. שליטה בדפוסים האלה הופכת כללי גזירה לנקודות מלאות בבחינה.""",
    },
    "definition": {
        "body_en_md": """**Critical point:** A number $x_0$ in the domain where $f'(x_0) = 0$ **or** $f'(x_0)$ does not exist (corner, cusp, vertical tangent). Critical points are *candidates* for local extrema — you must still classify them with a sign table or derivative test.

**Local maximum:** $f(x_0) \\ge f(x)$ for all $x$ in some open interval around $x_0$. The graph is highest in a neighborhood, not necessarily over the entire domain.

**Local minimum:** $f(x_0) \\le f(x)$ for all $x$ near $x_0$.

**Absolute (global) maximum/minimum:** The largest or smallest value of $f$ over the entire domain, or over a closed interval $[a,b]$. On a closed interval, compare **all critical points inside $(a,b)$ AND the endpoints** $f(a)$, $f(b)$.

**Inflection point:** A point where concavity changes — equivalently, where $f''$ changes sign at $x_0$. Solving $f''(x_0)=0$ alone is **not enough**; you must verify the sign flip.

**Second derivative test** (when $f'(x_0)=0$):
- $f''(x_0) > 0$ $\\Rightarrow$ **local minimum** (concave up, bowl shape).
- $f''(x_0) < 0$ $\\Rightarrow$ **local maximum** (concave down, hill shape).
- $f''(x_0) = 0$: **inconclusive** — switch to the first derivative test.

**First derivative test:** Examine the sign of $f'$ immediately left and right of $x_0$.
- Sign change $+ \\to -$: **local maximum**.
- Sign change $- \\to +$: **local minimum**.
- No sign change: **not an extremum** (e.g., $f(x)=x^3$ at $x=0$).""",
        "body_he_md": """**נקודה קריטית:** מספר $x_0$ בתחום שבו $f'(x_0) = 0$ **או** $f'(x_0)$ לא קיימת (פינה, קאספ, משיק אנכי). נקודות קריטיות הן *מועמדות* לקיצון מקומי — חובה לסווג אותן בטבלת סימנים או במבחן נגזרות.

**מקסימום מקומי:** $f(x_0) \\ge f(x)$ לכל $x$ בסביבה פתוחה של $x_0$. הגרף הגבוה ביותר בשכונה, לא בהכרח על כל התחום.

**מינימום מקומי:** $f(x_0) \\le f(x)$ לכל $x$ קרוב ל-$x_0$.

**מקסימום/מינימום מוחלט (גלובלי):** הערך הגדול ביותר או הקטן ביותר של $f$ על כל התחום, או על קטע סגור $[a,b]$. בקטע סגור, השוו **כל נקודות הקיצון בתוך $(a,b)$ וגם את הקצוות** $f(a)$, $f(b)$.

**נקודת פיתול:** נקודה שבה הקעירות משתנה — כלומר $f''$ משנה סימן ב-$x_0$. פתרון $f''(x_0)=0$ **לבדו אינו מספיק**; חובה לאמת שינוי סימן.

**מבחן נגזרת שנייה** (כאשר $f'(x_0)=0$):
- $f''(x_0) > 0$ $\\Rightarrow$ **מינימום מקומי** (קעורה כלפי מעלה, צורת קערה).
- $f''(x_0) < 0$ $\\Rightarrow$ **מקסימום מקומי** (קעורה כלפי מטה, צורת גבעה).
- $f''(x_0) = 0$: **לא חד-משמעי** — עברו למבחן נגזרת ראשונה.

**מבחן נגזרת ראשונה:** בדקו את סימן $f'$ משמאל ומימין ל-$x_0$.
- שינוי סימן $+ \\to -$: **מקסימום מקומי**.
- שינוי סימן $- \\to +$: **מינימום מקומי**.
- ללא שינוי סימן: **לא קיצון** (למשל $f(x)=x^3$ ב-$x=0$).""",
    },
    "theory": {
        "body_en_md": """### Pattern A: Function Investigation (חקירת פונקציה)

This is the full exam workflow for sketching $y=f(x)$:

1. **Domain** — exclude division-by-zero, even roots of negatives, log restrictions.
2. **$f'(x)=0$** (and points where $f'$ is undefined) $\\Rightarrow$ critical points.
3. **Sign table for $f'$** — mark each interval as increasing ($+$) or decreasing ($-$); classify max/min by sign changes ($+\\to-$ max, $-\\to+$ min).
4. **$f''(x)=0$** $\\Rightarrow$ inflection candidates; verify $f''$ actually changes sign.
5. **Asymptotes** — vertical ($x=a$ where $f\\to\\pm\\infty$), horizontal ($y=L$ as $x\\to\\pm\\infty$), oblique (polynomial long division for rational functions).
6. **Intercepts and special values**, then **sketch** connecting all information.

### Pattern B: Optimization Word Problems

1. Read carefully; **draw and label** the geometry or situation.
2. Introduce one variable $x$ and write the quantity to optimize $Q(x)$ using a **constraint** to eliminate extra variables.
3. State the **domain** (physical meaning: lengths $>0$, etc.).
4. Solve $Q'(x)=0$, classify with $Q''$ or a sign table.
5. **Check endpoints** of the domain — the optimum may occur at a boundary.
6. Answer in context with **units**.

### Pattern C: Absolute Extrema on Closed Interval $[a,b]$

1. Find all critical points in $(a,b)$.
2. Evaluate $f$ at each critical point **and** at $a$ and $b$.
3. Largest value $=$ absolute max; smallest $=$ absolute min. Ties are allowed at multiple points.

### Tangent Line Equation

The tangent to $y=f(x)$ at $(a,f(a))$ has slope $f'(a)$:
$$y - f(a) = f'(a)(x - a).$$
This connects derivative applications to linear approximation and rate-of-change problems.""",
        "body_he_md": """### דפוס א': חקירת פונקציה

זהו תהליך הבחינה המלא לשרטוט $y=f(x)$:

1. **תחום** — הוציאו חלוקה באפס, שורשים זוגיים של שליליים, הגבלות לוגריתם.
2. **$f'(x)=0$** (ונקודות שבהן $f'$ לא מוגדרת) $\\Rightarrow$ נקודות קיצון מועמדות.
3. **טבלת סימנים של $f'$** — סמנו כל קטע כעולה ($+$) או יורדת ($-$); סווגו מקס/מין לפי שינוי סימן ($+\\to-$ מקס, $-\\to+$ מין).
4. **$f''(x)=0$** $\\Rightarrow$ מועמדות לפיתול; אמתו ש-$f''$ באמת משנה סימן.
5. **אסימפטוטות** — אנכית ($x=a$ כש-$f\\to\\pm\\infty$), אופקית ($y=L$ כש-$x\\to\\pm\\infty$), אלכסונית (חלוקת פולינומים לפונקציות רציונליות).
6. **חיתוכים וערכים מיוחדים**, ואז **שרטוט** שמחבר את כל המידע.

### דפוס ב': בעיות אופטימיזציה

1. קראו בעיון; **שרטטו וסמנו** את הגיאומטריה או המצב.
2. הגדירו משתנה $x$ אחד וכתבו את הגודל לאופטימיזציה $Q(x)$ תוך שימוש ב**אילוץ** להסרת משתנים נוספים.
3. ציינו את **התחום** (משמעות פיזית: אורכים $>0$ וכו').
4. פתרו $Q'(x)=0$, סווגו עם $Q''$ או טבלת סימנים.
5. **בדקו קצוות** התחום — הקיצון עלול להיות בגבול.
6. ענו בהקשר עם **יחידות**.

### דפוס ג': קיצון מוחלט על קטע סגור $[a,b]$

1. מצאו כל נקודות קיצון ב-$(a,b)$.
2. חשבו $f$ בכל נקודת קיצון **וגם** ב-$a$ וב-$b$.
3. הערך הגדול ביותר $=$ מקסימום מוחלט; הקטן ביותר $=$ מינימום מוחלט. תיקו מותר בכמה נקודות.

### משוואת משיק

המשיק ל-$y=f(x)$ ב-$(a,f(a))$ בשיפוע $f'(a)$:
$$y - f(a) = f'(a)(x - a).$$
זה מחבר יישומי נגזרות לאומדן לינארי ולבעיות קצב שינוי.""",
    },
    "method_guide": {
        "body_en_md": """| Goal | Method | Key formula / step |
|---|---|---|
| Find critical points | Solve $f'(x)=0$; check where $f'$ undefined | Also include domain boundaries if relevant |
| Classify max/min | 1st derivative test (sign change) or 2nd derivative test | $f''>0$ at critical pt $\\Rightarrow$ min; $f''<0$ $\\Rightarrow$ max |
| Absolute max/min on $[a,b]$ | Evaluate $f$ at all critical pts in $(a,b)$ **and** at $a,b$ | Compare all values — do not skip endpoints |
| Inflection point | Solve $f''=0$, then verify sign change of $f''$ | $f''=0$ without sign change is NOT inflection |
| Optimization word problem | One variable $Q(x)$ via constraint | $Q'=0$, classify, check domain endpoints |
| Tangent line | Point-slope form | $y-f(a)=f'(a)(x-a)$ |
| Concavity | Sign of $f''$ | $f''>0$: concave up; $f''<0$: concave down |

**Sign table template (exam-ready):**

1. Mark critical points, inflection candidates, and domain holes on a number line.
2. Pick one test value in each open interval; compute the sign of $f'$ (or $f''$).
3. Read off increasing/decreasing (or concavity); classify extrema: $+\\to-$ gives max, $-\\to+$ gives min.

**When to use which test:** Second derivative is faster when $f''$ is easy to compute and nonzero at the critical point. First derivative test is mandatory when $f''(x_0)=0$ or when $f'$ fails to exist.""",
        "body_he_md": """| מטרה | שיטה | נוסחה / צעד מרכזי |
|---|---|---|
| נקודות קיצון | פתרו $f'(x)=0$; בדקו היכן $f'$ לא מוגדרת | כללו גבולות תחום אם רלוונטי |
| סיווג מקס/מין | מבחן נגזרת ראשונה (שינוי סימן) או שנייה | $f''>0$ בנקודה $\\Rightarrow$ מין; $f''<0$ $\\Rightarrow$ מקס |
| מקס/מין מוחלט על $[a,b]$ | חשבו $f$ בכל נקודות קיצון ב-$(a,b)$ **וגם** ב-$a,b$ | השוו את כל הערכים — אל תדלגו על קצוות |
| נקודת פיתול | פתרו $f''=0$, ואז אמתו שינוי סימן של $f''$ | $f''=0$ בלי שינוי סימן — לא פיתול |
| בעיית אופטימיזציה | משתנה $Q(x)$ אחד דרך אילוץ | $Q'=0$, סיווג, בדיקת קצוות תחום |
| משוואת משיק | צורת נקודה-שיפוע | $y-f(a)=f'(a)(x-a)$ |
| קעירות | סימן $f''$ | $f''>0$: שקערורית; $f''<0$: קמורה |

**תבנית טבלת סימנים (מוכנה לבחינה):**

1. סמנו נקודות קיצון, מועמדות לפיתול וחורים בתחום על ציר המספרים.
2. בחרו ערך בדיקה אחד בכל קטע פתוח; חשבו סימן $f'$ (או $f''$).
3. קראו עולה/יורדת (או קעירות); סווגו קיצון: $+\\to-$ נותן מקס, $-\\to+$ נותן מין.

**מתי להשתמש באיזה מבחן:** נגזרת שנייה מהירה כש-$f''$ קל לחישוב ושונה מאפס בנקודה. נגזרת ראשונה חובה כש-$f''(x_0)=0$ או כש-$f'$ לא קיימת.""",
    },
    "pitfall": {
        "body_en_md": """1. **Forgetting endpoints on closed intervals.** On $[a,b]$, the absolute maximum might occur at $x=a$ or $x=b$, not at any critical point. Always build a comparison table: critical values plus $f(a)$ and $f(b)$.

2. **Treating $f''(x_0)=0$ as automatic inflection.** You must verify a sign change. Example: $f(x)=x^4$ has $f''(0)=0$ but concavity is up on both sides — no inflection at $0$.

3. **Assuming every critical point is an extremum.** If $f'$ does not change sign (e.g., $f(x)=x^3$ at $x=0$), the point is neither max nor min — it is a horizontal inflection.

4. **Using the second derivative test when $f''(x_0)=0$.** The test is inconclusive. Switch to the first derivative sign table immediately.

5. **Ignoring domain restrictions in optimization.** A critical point outside the physical domain (negative length, $x=0$ when length must be positive) must be discarded. Also check whether the optimum sits at a domain endpoint.

6. **Sign table errors near asymptotes.** Test values must lie in the correct branch of the domain; picking $x=0$ when the domain excludes $0$ gives a wrong sign.""",
        "body_he_md": """1. **שכחת קצוות בקטעים סגורים.** ב-$[a,b]$, המקסימום המוחלט עלול להיות ב-$x=a$ או $x=b$, לא בנקודת קיצון. בנו תמיד טבלת השוואה: ערכי קיצון בתוספת $f(a)$ ו-$f(b)$.

2. **התייחסות ל-$f''(x_0)=0$ כפיתול אוטומטי.** חובה לאמת שינוי סימן. דוגמה: $f(x)=x^4$ נותן $f''(0)=0$ אך הקעירות כלפי מעלה משני הצדדים — אין פיתול ב-$0$.

3. **הנחה שכל נקודה קריטית היא קיצון.** אם $f'$ לא משנה סימן (למשל $f(x)=x^3$ ב-$x=0$), אין מקסימום ולא מינימום — זו נקודת פיתול אופקית.

4. **שימוש במבחן נגזרת שנייה כש-$f''(x_0)=0$.** המבחן לא חד-משמעי. עברו מיד לטבלת סימנים של הנגזרת הראשונה.

5. **התעלמות מהגבלות תחום באופטימיזציה.** נקודת קיצון מחוץ לתחום הפיזי (אורך שלילי, $x=0$ כשאורך חייב להיות חיובי) יש לפסול. בדקו גם אם הקיצון בקצה התחום.

6. **שגיאות טבלת סימנים ליד אסימפטוטות.** ערכי בדיקה חייבים להיות בענף הנכון של התחום; בחירת $x=0$ כשהתחום מוציא $0$ נותנת סימן שגוי.""",
    },
    "why_matters": {
        "body_en_md": """Derivative applications bridge pure calculus to every quantitative field on the platform and on Bagrut exams.

**You will use this to unlock:**
- `concept:work_energy` **Work & Energy** — force from potential energy is $F = -\\dfrac{dU}{dx}$; equilibrium occurs where $U'(x)=0$.
- `concept:optimization_word_problems` **Optimization** — the same $Q'=0$ pattern appears in economics, geometry, and engineering.
- `concept:differential_equations_intro` **Differential Equations** — slope fields and stability analysis start from $f'$ and $f''$ sign information.

**Builds on:**
- `concept:derivatives_rules` **Derivative Rules** — you must compute $f'$ and $f''$ reliably before any investigation.

**Why it matters for exams:** Bagrut 4- and 5-unit papers routinely allocate 20–30 points to function investigation and optimization combined. Examiners reward complete sign tables, endpoint checks, and labeled sketches — not just isolated answers. University Calc 1 expects the same rigor with more complex functions.""",
        "body_he_md": """יישומי נגזרות מחברים חשבון טהור לכל תחום כמותי בפלטפורמה ולבחינות הבגרות.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:work_energy` **עבודה ואנרגיה** — כוח מאנרגיה פוטנציאלית הוא $F = -\\dfrac{dU}{dx}$; שיווי משקל מתרחש כש-$U'(x)=0$.
- `concept:optimization_word_problems` **אופטימיזציה** — אותו דפוס $Q'=0$ מופיע בכלכלה, גיאומטריה והנדסה.
- `concept:differential_equations_intro` **משוואות דיפרנציאליות** — שדות שיפוע וניתוח יציבות מתחילים ממידע על סימן $f'$ ו-$f''$.

**מבוסס על:**
- `concept:derivatives_rules` **כללי גזירה** — חובה לחשב $f'$ ו-$f''$ בצורה אמינה לפני כל חקירה.

**למה זה חשוב לבחינות:** בבגרות 4 ו-5 יחידות מוקדשות שגרתית 20–30 נקודות לחקירת פונקציה ואופטימיזציה יחד. בוחנים מעריכים טבלאות סימנים מלאות, בדיקת קצוות ושרטוט מתויג — לא רק תשובות בודדות. בחדו״א 1 נדרשת אותה קפדנות עם פונקציות מורכבות יותר.""",
    },
    "before_exam": {
        "body_en_md": """**Function investigation checklist:**
1. Domain — list every restriction before differentiating.
2. $f'=0$ and undefined points $\\Rightarrow$ critical points.
3. Sign table for $f'$: increasing/decreasing; classify max/min ($+\\to-$, $-\\to+$).
4. $f''=0$ $\\Rightarrow$ inflection candidates; **verify sign change**.
5. Asymptotes: vertical, horizontal, oblique (long division for rationals).
6. Intercepts, special values, then sketch with labels.

**Optimization checklist:**
1. Draw; define one variable; write $Q(x)$; state domain with units.
2. $Q'(x)=0$; solve and classify ($Q''$ or sign table).
3. Evaluate at **domain endpoints** — boundary may win.
4. Final sentence with context and units.

**Red flags before submitting:**
- Did you evaluate $f(a)$ and $f(b)$ for absolute extrema?
- Is $f''=0$ confirmed as inflection by a sign change?
- Did you discard critical points outside the physical domain?""",
        "body_he_md": """**רשימת בדיקה לחקירת פונקציה:**
1. תחום — רשמו כל הגבלה לפני גזירה.
2. $f'=0$ ונקודות לא מוגדרות $\\Rightarrow$ נקודות קיצון.
3. טבלת סימנים $f'$: עולה/יורדת; סיווג מקס/מין ($+\\to-$, $-\\to+$).
4. $f''=0$ $\\Rightarrow$ מועמדות לפיתול; **אמתו שינוי סימן**.
5. אסימפטוטות: אנכית, אופקית, אלכסונית (חלוקה לרציונליות).
6. חיתוכים, ערכים מיוחדים, ואז שרטוט מתויג.

**רשימת בדיקה לאופטימיזציה:**
1. שרטוט; משתנה אחד; כתבו $Q(x)$; ציינו תחום עם יחידות.
2. $Q'(x)=0$; פתרו וסווגו ($Q''$ או טבלת סימנים).
3. חשבו ב**קצוות התחום** — הגבול עלול לנצח.
4. משפט סיום עם הקשר ויחידות.

**דגלים אדומים לפני הגשה:**
- חישבתם $f(a)$ ו-$f(b)$ לקיצון מוחלט?
- $f''=0$ אומת כפיתול בשינוי סימן?
- פסלתם נקודות קיצון מחוץ לתחום הפיזי?""",
    },
    "summary": {
        "body_en_md": """- $f'>0$: increasing; $f'<0$: decreasing; $f'=0$: critical point (candidate for extrema).
- **First derivative test:** sign change of $f'$ classifies local max ($+\\to-$) and min ($-\\to+$).
- **Second derivative test:** at $f'(x_0)=0$, $f''(x_0)>0$ $\\Rightarrow$ local min; $f''(x_0)<0$ $\\Rightarrow$ local max; $f''=0$ $\\Rightarrow$ use first test.
- **Inflection:** $f''$ changes sign — not merely $f''=0$.
- **Absolute extrema on $[a,b]$:** evaluate at all critical points in $(a,b)$ **and** at endpoints $a,b$.
- **Optimization:** express $Q$ in one variable via constraint, find domain, solve $Q'=0$, classify, check endpoints, answer with units.
- **Tangent line:** $y-f(a)=f'(a)(x-a)$.""",
        "body_he_md": """- $f'>0$: עולה; $f'<0$: יורדת; $f'=0$: נקודה קריטית (מועמדת לקיצון).
- **מבחן נגזרת ראשונה:** שינוי סימן של $f'$ מסווג מקס מקומי ($+\\to-$) ומין ($-\\to+$).
- **מבחן נגזרת שנייה:** ב-$f'(x_0)=0$, $f''(x_0)>0$ $\\Rightarrow$ מין מקומי; $f''(x_0)<0$ $\\Rightarrow$ מקס; $f''=0$ $\\Rightarrow$ עברו למבחן ראשון.
- **פיתול:** $f''$ משנה סימן — לא רק $f''=0$.
- **קיצון מוחלט על $[a,b]$:** חשבו בכל נקודות הקיצון ב-$(a,b)$ **וגם** בקצוות $a,b$.
- **אופטימיזציה:** ביטוי $Q$ במשתנה אחד דרך אילוץ, מציאת תחום, $Q'=0$, סיווג, בדיקת קצוות, תשובה עם יחידות.
- **משיק:** $y-f(a)=f'(a)(x-a)$.""",
    },
}

WORKED_EXAMPLES = [
    {
        "body_en_md": """**Find the local extrema of** $f(x) = x^3 - 6x^2 + 9x + 1$.

### Move 1: Compute $f'(x)$ and factor completely.
$$f'(x) = 3x^2 - 12x + 9 = 3(x^2 - 4x + 3) = 3(x-1)(x-3).$$
Factoring before solving saves sign-table errors on the exam.

### Move 2: Critical points — set $f'(x)=0$.
$$x = 1 \\quad \\text{or} \\quad x = 3.$$

### Move 3: Build the sign table for $f'$.
| Interval | $f'$ sign | $f$ behavior |
|---|---|---|
| $(-\\infty,1)$ | $+$ | increasing |
| $(1,3)$ | $-$ | decreasing |
| $(3,\\infty)$ | $+$ | increasing |

Test values: $x=0$ gives $f'(0)=9>0$; $x=2$ gives $f'(2)=-3<0$; $x=4$ gives $f'(4)=9>0$.

### Move 4: Classify and compute function values.
- $x=1$: sign change $+ \\to -$ $\\Rightarrow$ **local maximum**. $f(1) = 1-6+9+1 = 5$.
- $x=3$: sign change $- \\to +$ $\\Rightarrow$ **local minimum**. $f(3) = 27-54+27+1 = 1$.

**Answer:** Local max $(1,5)$; local min $(3,1)$. No absolute extrema on $\\mathbb{R}$ since $f\\to-\\infty$ as $x\\to-\\infty$.""",
        "body_he_md": """**מצאו קיצונות מקומיים של** $f(x) = x^3-6x^2+9x+1$.

### צעד 1: חשבו $f'(x)$ ופרקו לגורמים.
$$f'(x) = 3x^2-12x+9 = 3(x-1)(x-3).$$
פירוק לגורמים לפני פתרון מונע שגיאות בטבלת הסימנים בבחינה.

### צעד 2: נקודות קיצון — $f'(x)=0$.
$$x = 1 \\quad \\text{או} \\quad x = 3.$$

### צעד 3: בנו טבלת סימנים של $f'$.
| קטע | סימן $f'$ | התנהגות $f$ |
|---|---|---|
| $(-\\infty,1)$ | $+$ | עולה |
| $(1,3)$ | $-$ | יורדת |
| $(3,\\infty)$ | $+$ | עולה |

ערכי בדיקה: $x=0$ נותן $f'(0)=9>0$; $x=2$ נותן $f'(2)=-3<0$; $x=4$ נותן $f'(4)=9>0$.

### צעד 4: סיווג וחישוב ערכי הפונקציה.
- $x=1$: שינוי סימן $+ \\to -$ $\\Rightarrow$ **מקסימום מקומי**. $f(1) = 5$.
- $x=3$: שינוי סימן $- \\to +$ $\\Rightarrow$ **מינימום מקומי**. $f(3) = 1$.

**תשובה:** מקס מקומי $(1,5)$; מין מקומי $(3,1)$. אין קיצון מוחלט על $\\mathbb{R}$ כי $f\\to-\\infty$ כש-$x\\to-\\infty$. בבחינה, טבלת הסימנים חייבת להופיע לפני הסיווג — בוחנים מעניקים נקודות חלקיות עליה גם כשיש טעות חישוב בסוף.""",
    },
    {
        "body_en_md": """**Problem:** A farmer has 100 m of fencing. She builds a rectangular pen along a barn wall (one side needs no fence). Maximize the enclosed area.

### Move 1: Draw and label. Let $x$ = side perpendicular to the barn, $y$ = side parallel to the barn.

### Move 2: Write the constraint from the fence length.
Only two sides of length $x$ and one of length $y$ use fencing:
$$2x + y = 100 \\Rightarrow y = 100 - 2x.$$

### Move 3: Area as a function of one variable.
$$A(x) = x \\cdot y = x(100-2x) = 100x - 2x^2.$$
**Domain:** $x>0$ and $y=100-2x>0$, so $0 < x < 50$.

### Move 4: Find critical points — $A'(x)=0$.
$$A'(x) = 100 - 4x = 0 \\Rightarrow x = 25.$$

### Move 5: Classify with the second derivative.
$$A''(x) = -4 < 0 \\quad \\text{for all } x \\Rightarrow \\text{ concave down} \\Rightarrow \\text{ maximum at } x=25.$$

### Move 6: Answer with units and context.
$$x = 25\\text{ m}, \\quad y = 50\\text{ m}, \\quad A_{\\max} = 25 \\times 50 = 1250\\text{ m}^2.$$
Check endpoints: as $x\\to 0^+$ or $x\\to 50^-$, area $\\to 0$, confirming the interior critical point is optimal.""",
        "body_he_md": """**בעיה:** לחקלאית יש 100 מ' גדר. היא בונה משתלה מלבנית לאורך קיר האורווה (צד אחד ללא גדר). מקסימום שטח.

### צעד 1: שרטוט וסימון. $x$ = צלע מאונכת לקיר, $y$ = צלע מקבילה.

### צעד 2: כתבו את האילוץ מאורך הגדר.
רק שתי צלעות באורך $x$ וצלע אחת באורך $y$ משתמשות בגדר:
$$2x + y = 100 \\Rightarrow y = 100 - 2x.$$

### צעד 3: שטח כפונקציה של משתנה אחד.
$$A(x) = x(100-2x) = 100x - 2x^2.$$
**תחום:** $x>0$ ו-$y=100-2x>0$, כלומר $0 < x < 50$.

### צעד 4: נקודות קיצון — $A'(x)=0$.
$$A'(x) = 100 - 4x = 0 \\Rightarrow x = 25.$$

### צעד 5: סיווג בנגזרת שנייה.
$$A''(x) = -4 < 0 \\Rightarrow \\text{קמורה} \\Rightarrow \\text{מקסימום ב-} x=25.$$

### צעד 6: תשובה עם יחידות והקשר.
$$x = 25\\text{ מ'}, \\quad y = 50\\text{ מ'}, \\quad A_{\\max} = 1250\\text{ מ\"ר}.$$
בדיקת קצוות: כש-$x\\to 0^+$ או $x\\to 50^-$, השטח $\\to 0$, מאשר שהקיצון הפנימי הוא האופטימלי. בבגרות, כתבו את האילוץ $2x+y=100$ לפני גזירת $A(x)$ — זה מרוויח נקודות שיטה.""",
    },
    {
        "body_en_md": """**Investigate** $f(x) = \\dfrac{x^2}{x-1}$ and sketch (Bagrut 5-unit level).

### Move 1: Domain.
$x \\ne 1$, so domain is $(-\\infty,1) \\cup (1,\\infty)$.

### Move 2: Asymptotes.
- **Vertical:** $x = 1$ (denominator zero).
- **Oblique:** polynomial division: $\\dfrac{x^2}{x-1} = x+1 + \\dfrac{1}{x-1}$. As $x\\to\\pm\\infty$, remainder $\\to 0$, so $y = x+1$ is the oblique asymptote.

### Move 3: First derivative.
$$f'(x) = \\frac{2x(x-1) - x^2}{(x-1)^2} = \\frac{x^2-2x}{(x-1)^2} = \\frac{x(x-2)}{(x-1)^2}.$$

### Move 4: Critical points — $f'(x)=0$ (numerator zero; denominator $\\ne 0$).
$x = 0$ and $x = 2$.

### Move 5: Sign table for $f'$.
| Interval | $f'$ sign | behavior |
|---|---|---|
| $(-\\infty,0)$ | $+$ | increasing |
| $(0,1)$ | $-$ | decreasing |
| $(1,2)$ | $-$ | decreasing |
| $(2,\\infty)$ | $+$ | increasing |

- $x=0$: $+\\to-$ $\\Rightarrow$ local max, $f(0)=0$.
- $x=2$: $-\\to+$ $\\Rightarrow$ local min, $f(2)=4$.

### Move 6: Second derivative and concavity.
$$f''(x) = \\frac{2}{(x-1)^3}.$$
$f''>0$ for $x>1$ (concave up); $f''<0$ for $x<1$ (concave down). No inflection — concavity jumps at the vertical asymptote $x=1$, not at a domain point.""",
        "body_he_md": """**חקרו** $f(x) = \\dfrac{x^2}{x-1}$ ושרטטו (רמת בגרות 5 יחידות).

### צעד 1: תחום.
$x \\ne 1$, כלומר $(-\\infty,1) \\cup (1,\\infty)$.

### צעד 2: אסימפטוטות.
- **אנכית:** $x = 1$ (מכנה מתאפס).
- **אלכסונית:** חלוקת פולינומים: $\\dfrac{x^2}{x-1} = x+1 + \\dfrac{1}{x-1}$. כש-$x\\to\\pm\\infty$, השארית $\\to 0$, כלומר $y = x+1$.

### צעד 3: נגזרת ראשונה.
$$f'(x) = \\frac{x(x-2)}{(x-1)^2}.$$

### צעד 4: נקודות קיצון — $f'(x)=0$.
$x = 0$ ו-$x = 2$.

### צעד 5: טבלת סימנים של $f'$.
| קטע | סימן $f'$ | התנהגות |
|---|---|---|
| $(-\\infty,0)$ | $+$ | עולה |
| $(0,1)$ | $-$ | יורדת |
| $(1,2)$ | $-$ | יורדת |
| $(2,\\infty)$ | $+$ | עולה |

- $x=0$: $+\\to-$ $\\Rightarrow$ מקס מקומי, $f(0)=0$.
- $x=2$: $-\\to+$ $\\Rightarrow$ מין מקומי, $f(2)=4$.

### צעד 6: נגזרת שנייה וקעירות.
$$f''(x) = \\frac{2}{(x-1)^3}.$$
$f''>0$ ל-$x>1$ (שקערורית); $f''<0$ ל-$x<1$ (קמורה). אין פיתול — הקעירות קופצת באסימפטוטה $x=1$, לא בנקודה בתחום. בבחינת 5 יחידות, חובה לסמן אסימפטוטה אלכסונית $y=x+1$ לפני שרטוט העקומה.""",
    },
]

CHECKPOINT_PATCHES = [
    {
        "checkpoint_solution_en": """**Step 1:** Differentiate.
$$f'(x) = 3x^2 - 3 = 3(x^2-1) = 3(x-1)(x+1) = 0 \\Rightarrow x = -1, \\; 1.$$
Both critical points lie inside $[-2,2]$.

**Step 2:** Build the comparison table (critical points **and** endpoints).
| $x$ | $f(x)$ |
|---|---|
| $-2$ | $-8+6+2 = 0$ |
| $-1$ | $-1+3+2 = 4$ |
| $1$ | $1-3+2 = 0$ |
| $2$ | $8-6+2 = 4$ |

**Step 3:** Read off absolute extrema.
- **Absolute maximum** $= 4$ at $x=-1$ and $x=2$ (tie allowed).
- **Absolute minimum** $= 0$ at $x=-2$ and $x=1$.

**Why endpoints matter:** $f'(2)=9\\ne 0$, yet $x=2$ achieves the same maximum as the critical point $x=-1$. Skipping endpoints would miss half the answer.""",
        "checkpoint_solution_he": """**שלב 1:** גזירה.
$$f'(x) = 3x^2-3 = 3(x-1)(x+1) = 0 \\Rightarrow x = -1, \\; 1.$$
שתי הנקודות בתוך $[-2,2]$.

**שלב 2:** טבלת השוואה (נקודות קיצון **וגם** קצוות).
| $x$ | $f(x)$ |
|---|---|
| $-2$ | $0$ |
| $-1$ | $4$ |
| $1$ | $0$ |
| $2$ | $4$ |

**שלב 3:** קיצון מוחלט.
- **מקסימום מוחלט** $= 4$ ב-$x=-1$ ו-$x=2$ (תיקו מותר).
- **מינימום מוחלט** $= 0$ ב-$x=-2$ ו-$x=1$.

**למה קצוות חשובים:** $f'(2)=9\\ne 0$, ובכל זאת $x=2$ משיג את אותו מקסימום כמו $x=-1$. דילוג על קצוות מפספס חצי מהתשובה.""",
    },
    {
        "checkpoint_solution_en": """**Step 1:** Revenue $R(x) = x \\cdot p = x(200-2x) = 200x - 2x^2$. Price positive requires $p=200-2x>0$, so $0 < x < 100$.

**Step 2:** Critical point.
$$R'(x) = 200 - 4x = 0 \\Rightarrow x = 50.$$

**Step 3:** Classify.
$$R''(x) = -4 < 0 \\Rightarrow \\text{maximum at } x = 50.$$

**Step 4:** Compute maximum revenue.
$$R(50) = 50 \\times (200 - 100) = 50 \\times 100 = 5000 \\text{ shekels/day}.$$

**Check endpoints:** $R(0)=0$ and $R(100)=0$, confirming the interior critical point gives the peak. Always state both the optimal quantity and the revenue value.""",
        "checkpoint_solution_he": """**שלב 1:** הכנסה $R(x) = x(200-2x) = 200x-2x^2$. מחיר חיובי דורש $0 < x < 100$.

**שלב 2:** נקודת קיצון.
$$R'(x) = 200-4x = 0 \\Rightarrow x = 50.$$

**שלב 3:** סיווג.
$$R''(x) = -4 < 0 \\Rightarrow \\text{מקסימום ב-} x = 50.$$

**שלב 4:** הכנסה מקסימלית.
$$R(50) = 50 \\times 100 = 5000 \\text{ ש\"ח ליום}.$$

**בדיקת קצוות:** $R(0)=0$ ו-$R(100)=0$, מאשר שהקיצון הפנימי הוא השיא. ציינו גם כמות אופטימלית וגם ערך ההכנסה.""",
    },
]

QUESTION_EXPLS = [
    fmt_expl(
        "The second derivative test applies when $f'(x_0)=0$. Here $f'(2)=0$ and $f''(2)=5>0$, so the graph is concave upward at $x=2$. A horizontal tangent with $f''>0$ indicates a local minimum.",
        "Confirm $f'(x_0)=0$ first. Then read $f''(x_0)$: positive $\\Rightarrow$ min; negative $\\Rightarrow$ max. If $f''=0$, use the first derivative sign table instead.",
        "Confusing signs: $f''>0$ gives a minimum, not a maximum. Do not call it inflection — that requires $f''$ to change sign.",
        "On Bagrut MCQs, memorize $f''>0 \\Rightarrow$ min and $f''<0 \\Rightarrow$ max. If $f''=0$, reject second-derivative answers and use the first test.",
        "מבחן הנגזרת השנייה חל כש-$f'(x_0)=0$. כאן $f'(2)=0$ ו-$f''(2)=5>0$, כלומר הגרף קעור כלפי מעלה (צורת קערה) ב-$x=2$. לפי המבחן, משיק אופקי עם נגזרת שנייה חיובית מציין מינימום מקומי — הפונקציה יורדת לפני $x=2$ ועולה אחריו.",
        "אשרו תחילה $f'(x_0)=0$ (נקודה קריטית). קראו את סימן $f''(x_0)$: חיובי $\\Rightarrow$ קעורה למעלה $\\Rightarrow$ מין; שלילי $\\Rightarrow$ קעורה למטה $\\Rightarrow$ מקס. אם $f''=0$, המבחן השני נכשל וצריך טבלת סימנים של $f'$.",
        "בלבול סימנים: $f''>0$ נותן מינימום, לא מקסימום. אל תקראו לנקודה פיתול — פיתול דורש שינוי סימן של $f''$, לא רק ערך חיובי.",
        "בשאלות רב-ברירה בבגרות, רשמו $f''>0 \\Rightarrow$ מין ו-$f''<0 \\Rightarrow$ מקס. אם $f''=0$, פסלו מיד את תשובת הנגזרת השנייה ועברו למבחן הראשון.",
    ),
    fmt_expl(
        "Differentiate: $f'(x)=3(x-1)(x-3)$, so critical points are $x=1$ and $x=3$. Sign table: $f'>0$ on $(-\\infty,1)$, $f'<0$ on $(1,3)$, $f'>0$ on $(3,\\infty)$. So $x=1$ is a local max ($f=5$) and $x=3$ is a local min ($f=1$).",
        "Factor $f'$, mark roots on a number line, test one value per interval, classify by sign changes. Compute $f(x_0)$ at each extremum — rubrics want coordinates.",
        "At $x=1$, $f''(1)=0$, so the second test is inconclusive — use the sign table. Another slip: listing critical points without classifying.",
        "This cubic is Worked Example 1. Draw the sign table on exams — partial credit is common even when final arithmetic slips.",
        "גזירה: $f'(x)=3(x-1)(x-3)$, נקודות קיצון $x=1$ ו-$x=3$. טבלת סימנים: $f'>0$ ב-$(-\\infty,1)$, $f'<0$ ב-$(1,3)$, $f'>0$ ב-$(3,\\infty)$. לכן $x=1$ מקס מקומי עם $f(1)=5$, ו-$x=3$ מין מקומי עם $f(3)=1$.",
        "עקבו אחרי דפוס החקירה: פרקו $f'$ לגורמים, סמנו שורשים על ציר, בדקו ערך אחד בכל קטע, סווגו לפי שינוי סימן. חשבו $f(x_0)$ בכל קיצון — רובריקה דורשת נקודות, לא רק $x$.",
        "שימוש במבחן שנייה בלי בדיקה: $f''(1)=0$, המבחן לא חד-משמעי ב-$x=1$. טבלת הסימנים (מבחן ראשון) אמינה כאן. טעות נוספת: דיווח נקודות קיצון בלי סיווג.",
        "הפולינום הזה מופיע בדוגמה 1. בבחינה, שרטטו טבלת סימנים גם אם נראה לכם שאתם יודעים — נקודות חלקיות על הטבלה נפוצות.",
    ),
    fmt_expl(
        "Critical points satisfy $f'(x)=0$. Here $f'(x)=6x^2-6x-12=6(x-2)(x+1)=0$, giving $x=2$ and $x=-1$. These are the only candidates where the tangent is horizontal. Note: the question asks for critical points, not classified extrema — classification requires a sign table or second derivative test as a follow-up step.",
        "Always factor $f'$ completely before solving. The factored form $6(x-2)(x+1)$ makes the roots immediate and prepares you for the sign table in the next question. Verify by expanding: $6(x^2-x-2)=6x^2-6x-12$ ✓.",
        "Stopping after $f'=0$ without factoring, missing $x=-1$ when only solving numerically, or confusing critical points with inflection points (which come from $f''$). Also, do not classify yet unless asked.",
        "Bagrut short-answer items often split 'find critical points' and 'classify' into two sub-questions. Answer exactly what is asked — list $x=2$ and $x=-1$ here; save classification for the next part.",
        "נקודות קיצון מקיימות $f'(x)=0$. כאן $f'(x)=6(x-2)(x+1)=0$, כלומר $x=2$ ו-$x=-1$. אלו המועמדות היחידות למשיק אופקי. שימו לב: השאלה מבקשת נקודות קיצון, לא קיצון מסווג — סיווג דורש טבלת סימנים או מבחן שנייה בשלב הבא.",
        "פרקו $f'$ לגורמים לפני פתרון. הצורה $6(x-2)(x+1)$ נותנת שורשים מיד ומכינה לטבלת הסימנים בשאלה הבאה. אימות: $6(x^2-x-2)=6x^2-6x-12$ ✓.",
        "עצירה אחרי $f'=0$ בלי פירוק, פספוס $x=-1$, או בלבול בין נקודות קיצון לנקודות פיתול (שמגיעות מ-$f''$). אל תסווגו אם לא נשאל.",
        "שאלות בגרות קצרות לעיתים מפרידות 'מציאת נקודות קיצון' ו'סיווג' לשני סעיפים. ענו בדיוק על מה שנשאל — רשימת $x=2$ ו-$x=-1$ כאן.",
    ),
    fmt_expl(
        "Compute $f''(x)=12x-6$. At $x=2$: $f''(2)=18>0$ $\\Rightarrow$ local min. At $x=-1$: $f''(-1)=-18<0$ $\\Rightarrow$ local max. Both follow from the second derivative test with $f'=0$ at each point.",
        "When $f''(x_0)\\ne 0$, plug in each critical point: positive $\\Rightarrow$ min; negative $\\Rightarrow$ max. Cross-check: $f'=6(x-2)(x+1)$ gives $+\\to-$ at $x=-1$ and $-\\to+$ at $x=2$.",
        "Reversing the conclusion ($f''>0$ called max). Applying the test without confirming $f'(x_0)=0$ first.",
        "Use a compact table ($x_0$, $f''$, conclusion) — examiners want the sign of $f''$, not a full recomputation of $f'$.",
        "חישוב $f''(x)=12x-6$. ב-$x=2$: $f''(2)=18>0$, לפי מבחן הנגזרת השנייה (עם $f'(2)=0$ מהחלק הקודם), $x=2$ מינימום מקומי. ב-$x=-1$: $f''(-1)=-18<0$, כלומר $x=-1$ מקסימום מקומי.",
        "מבחן הנגזרת השנייה מהיר כש-$f''(x_0)\\ne 0$: הציבו כל נקודת קיצון וקראו סימן. חיובי $\\Rightarrow$ מין; שלילי $\\Rightarrow$ מקס. אימות: מ-$f'=6(x-2)(x+1)$: $+\\to-$ ב-$x=-1$ (מקס), $-\\to+$ ב-$x=2$ (מין) — שתי השיטות מסכימות.",
        "יישום המבחן בלי לוודא $f'(x_0)=0$. היפוך המסקנה ($f''>0$ נקרא מקס). אם $f''=0$, המבחן לא חד-משמעי — כאן $\\pm 18$, המבחן תקף.",
        "בסיווג שתי נקודות, טבלה קומפקטית ($x_0$, $f''(x_0)$, מסקנה) מרוויחה נקודות מהר. בוחנים מחפשים סימן $f''$, לא חישוב מחדש של $f'$.",
    ),
    fmt_expl(
        "The tangent line formula is $y-f(a)=f'(a)(x-a)$. Here $a=1$: $f(1)=1+3=4$, $f'(x)=2x+3$ so $f'(1)=5$. Substituting: $y-4=5(x-1)$, which simplifies to $y=5x-1$. The tangent touches the curve at $(1,4)$ with slope $5$.",
        "Tangent problems always need two ingredients: the point $(a,f(a))$ and the slope $f'(a)$. Compute $f(a)$ first (the $y$-coordinate), then $f'(a)$ (the slope). Expand $y-f(a)=f'(a)(x-a)$ to slope-intercept form if the rubric asks for it.",
        "Using $f'(a)$ as the $y$-intercept instead of the slope — writing $y=5x+4$ instead of $y=5x-1$. Another error: forgetting to evaluate $f(1)$ and plugging $x=1$ into $f'(x)$ only.",
        "Bagrut often accepts point-slope form $y-4=5(x-1)$ without simplification. If time is short, write point-slope and move on — but verify $f(1)$ and $f'(1)$ are correct before submitting.",
        "נוסחת המשיק: $y-f(a)=f'(a)(x-a)$. כאן $a=1$: $f(1)=4$, $f'(x)=2x+3$ ולכן $f'(1)=5$. הצבה: $y-4=5(x-1)$, כלומר $y=5x-1$. המשיק נוגע בעקומה ב-$(1,4)$ בשיפוע $5$.",
        "בבעיות משיק תמיד צריך שני מרכיבים: הנקודה $(a,f(a))$ והשיפוע $f'(a)$. חשבו $f(a)$ תחילה, אחר כך $f'(a)$. פתחו $y-f(a)=f'(a)(x-a)$ לצורת שיפוע-חיתוך אם נדרש.",
        "שימוש ב-$f'(a)$ כחיתוך $y$ במקום שיפוע — $y=5x+4$ במקום $y=5x-1$. שגיאה נוספת: שכחת $f(1)$ והצבת $x=1$ רק ב-$f'$.",
        "בבגרות לעיתים מקבלים צורת נקודה-שיפוע $y-4=5(x-1)$ בלי פישוט. אם הזמן קצר, כתבו נקודה-שיפוע — אבל וודאו $f(1)$ ו-$f'(1)$ נכונים.",
    ),
    fmt_expl(
        "Concave up means $f''(x)>0$. Here $f''(x)=12x^2-16$. Solve $12x^2-16>0$, i.e., $x^2>4/3$, so $|x|>2/\\sqrt{3}\\approx 1.15$. The function is concave up on $(-\\infty,-2/\\sqrt{3})\\cup(2/\\sqrt{3},\\infty)$ — two separate intervals symmetric about the origin.",
        "For concavity, set up the inequality $f''(x)>0$ (up) or $f''(x)<0$ (down). Factor when possible: $12x^2-16=4(3x^2-4)$, so the boundary is $x=\\pm\\sqrt{4/3}=\\pm 2/\\sqrt{3}$. Plot these on a number line and test one value in each region.",
        "Reversing the inequality ($f''<0$ for concave up). Giving only positive $x$ and forgetting the symmetric negative interval. Also, writing $x>2/\\sqrt{3}$ without the union with $(-\\infty,-2/\\sqrt{3})$ loses half the marks.",
        "Concavity questions on Bagrut often use even functions ($x^4$, $x^2$ terms), producing symmetric intervals. If your answer is not symmetric for an even $f''$, recheck the algebra.",
        "קעורה כלפי מעלה פירושה $f''(x)>0$. כאן $f''(x)=12x^2-16$. פתרון $x^2>4/3$, כלומר $|x|>2/\\sqrt{3}\\approx 1.15$. הפונקציה שקערורית על $(-\\infty,-2/\\sqrt{3})\\cup(2/\\sqrt{3},\\infty)$ — שני קטעים סימטריים.",
        "לקעירות, הגדירו $f''(x)>0$ (למעלה) או $f''(x)<0$ (למטה). פירוק: $12x^2-16=4(3x^2-4)$, הגבול $x=\\pm 2/\\sqrt{3}$. סמנו על ציר ובדקו ערך בכל אזור.",
        "היפוך אי-שוויון ($f''<0$ לשקערורית). מתן רק $x$ חיובי ושכחת הקטע השלילי הסימטרי. כתיבת $x>2/\\sqrt{3}$ בלי איחוד עם $(-\\infty,-2/\\sqrt{3})$ מאבדת חצי נקודות.",
        "שאלות קעירות בבגרות לעיתים עם פונקציות זוגיות, ונותנות קטעים סימטריים. אם התשובה לא סימטרית ל-$f''$ זוגית, בדקו שוב.",
    ),
    fmt_expl(
        "Let cut $=x$. Base $(12-2x)^2$, height $x$, so $V(x)=x(12-2x)^2$ on $0<x<6$. $V'=4(6-x)(6-3x)=0$ gives $x=2$ (interior max) and $x=6$ (volume 0). $V(2)=128$ cm³.",
        "Label cut $x$, write all dimensions in terms of $x$, state domain ($x>0$, $12-2x>0$), then $V'=0$. Discard endpoints with zero volume.",
        "Forgetting the factor 2 on each base side. Taking $x=6$ (zero volume). Skipping the domain loses method marks.",
        "Draw the net with cut $x$ labeled before writing $V(x)$ — setup marks are separate from the derivative step.",
        "יהי $x$ גודל הגזירה. בסיס $(12-2x)\\times(12-2x)$, גובה $x$, לכן $V(x)=x(12-2x)^2$. תחום: $0<x<6$. $V'=4(6-x)(6-3x)=0$ נותן $x=2$ (פנימי) ו-$x=6$ (קצה, נפח 0). $V(2)=128$ ס\"מ³ מקסימום.",
        "גיאומטריה באופטימיזציה: סמנו גזירה $x$, ביטוי כל ממד ב-$x$, כתבו נפח, הגדירו תחום ($x>0$, $12-2x>0$). אחרי $V'=0$, פסלו קצוות עם נפח 0 ואמתו $V''(2)<0$ או השוו קצוות.",
        "שימוש בהיקף במקום שלושה ממדים נכון — שכחת גורם 2 בכל צלע בסיס. $x=6$ כתשובה (נפח 0). אי-ציון תחום לפני גזירה מאבד נקודות שיטה.",
        "בעיות קופסה מגיליון הן קלאסика בבגרות. שרטטו פריסה עם $x$ לפני כתיבת $V(x)$ — בוחנים נותנים נקודות על ההכנה בנפרד.",
    ),
    fmt_expl(
        "Inflection requires $f''$ to change sign. Here $f''=12(x-1)(x+1)$, zeros at $x=\\pm 1$. $f''<0$ on $(-1,1)$, $f''>0$ outside — both show sign changes. Inflection points: $(1,-5)$ and $(-1,-5)$.",
        "Find $f''=0$ candidates, build a sign table for $f''$, then compute $f(x_0)$. Report coordinates, not just $x$-values.",
        "Listing $x=\\pm 1$ without verifying sign change ($x^4$ is the classic trap). Confusing inflection with critical points ($f'=0$).",
        "When $f''=12(x-1)(x+1)$, the sign table is immediate. Write 'sign change confirmed' for full reasoning marks.",
        "פיתול דורש שינוי סימן של $f''$. כאן $f''=12(x-1)(x+1)$, אפסים ב-$x=\\pm 1$. בדיקת סימן: $f''<0$ ב-$(-1,1)$, $f''>0$ מחוץ. שני $x=\\pm 1$ מראים שינוי סימן אמיתי, נקודות פיתול: $(1,-5)$ ו-$(-1,-5)$.",
        "תהליך: מצאו $f''=0$, בנו טבלת סימנים ל-$f''$ (לא $f'$). רק נקודות שבהן $f''$ חוצה אפס מתאימות. חשבו $f(x_0)$ — בבגרות מדווחים נקודות פיתול כקואורדinates.",
        "רישום $x=\\pm 1$ מ-$f''=0$ בלי אימות שינוי סימן — פונקציות כמו $x^4$ מלכדות. בלבול פיתול ($f''$) עם נקודות קיצון ($f'$). שכחת $f(\\pm 1)=-5$.",
        "כש-$f''$ מתפרק ל-$12(x-1)(x+1)$, טבלת הסימנים מיידית: שלילי בין $-1$ ל-$1$, חיובי מחוץ. כתבו 'שינוי סימן אומת' ליד כל מועמד.",
    ),
]


def word_count(text):
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def clean_exercise_solutions(data):
    for sec in data["sections"]:
        if sec.get("kind") != "exercise_set":
            continue
        for ex in sec.get("exercises", []):
            for key in ("solution_en", "solution_he"):
                val = ex.get(key, "")
                if not val:
                    continue
                val = val.replace(
                    "**Solution path:** Work step by step — do not skip the setup.\n\n", ""
                ).replace(
                    "**Solution path:** Identify the rule from this lesson, then apply it.\n\n", ""
                ).replace(
                    "**דרך פתרון:** עבדו שלב-שלב — אל תדלגו על ההכנה.\n\n", ""
                ).replace(
                    "**דרך פתרון:** זהו את הכלל מהשיעור, ואז יישמו.\n\n", ""
                ).replace(
                    "\n\n**Check:** Re-substitute or verify units and signs before moving on.", ""
                ).replace(
                    "\n\n**בדיקה:** החליפו בחזרה או וודאו יחידות וסימן.", ""
                )
                ex[key] = val


def fix_answer_payloads(data):
    fixes = {
        3: ["x = 2, x = -1", "x=-1, x=2", "-1 and 2"],
        4: ["f''(2)=18>0 local min, f''(-1)=-18<0 local max", "local min at 2, local max at -1"],
        5: ["y = 5x - 1", "y=5x-1", "y-4=5(x-1)"],
        6: ["|x| > 2/sqrt(3)", "(-inf,-2/sqrt(3)) union (2/sqrt(3),inf)"],
        7: ["x = 2", "128 cm^3", "128"],
        8: ["(1,-5) and (-1,-5)", "x=1 and x=-1 inflection"],
    }
    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in fixes and q.get("answer_payload"):
            q["answer_payload"]["acceptable_answers"] = fixes[ord_]


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in SECTION_PATCHES:
            sec.update(SECTION_PATCHES[kind])

    we_idx = 0
    cp_idx = 0
    for sec in data["sections"]:
        if sec.get("kind") == "worked_example" and we_idx < len(WORKED_EXAMPLES):
            sec.update(WORKED_EXAMPLES[we_idx])
            we_idx += 1
        if sec.get("kind") == "checkpoint" and cp_idx < len(CHECKPOINT_PATCHES):
            sec.update(CHECKPOINT_PATCHES[cp_idx])
            cp_idx += 1

    for i, q in enumerate(data["questions"]):
        en, he = QUESTION_EXPLS[i]
        q["explanation_en"] = en
        q["explanation_he"] = he

    clean_exercise_solutions(data)
    fix_answer_payloads(data)

    # Remove stray body_he field from first checkpoint if present
    for sec in data["sections"]:
        if sec.get("kind") == "checkpoint" and "body_he" in sec:
            del sec["body_he"]

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

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
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN:
            en = word_count(sec.get("body_en_md", ""))
            he = word_count(sec.get("body_he_md", ""))
            mn, mh = MIN[kind]
            if en < mn:
                issues.append(f"{kind} EN: {en} < {mn}")
            if he < mh:
                issues.append(f"{kind} HE: {he} < {mh}")

    for q in data["questions"]:
        en = word_count(q["explanation_en"])
        he = word_count(q["explanation_he"])
        if en < 80 or en > 150:
            issues.append(f"Q{q['ord']} EN: {en}")
        if he < 80 or he > 150:
            issues.append(f"Q{q['ord']} HE: {he}")

    if issues:
        print("ISSUES:")
        for issue in issues:
            print(" ", issue)
        raise SystemExit(1)

    print("Depth gates OK")
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit(r.returncode)
    print("seed-lessons --dry-run OK")


if __name__ == "__main__":
    main()
