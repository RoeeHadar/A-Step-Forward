#!/usr/bin/env python3
"""Expand equations_linear.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/equations_linear.json"

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


INTRO_EN = """A **linear equation** states that two linear expressions are equal. The unknown appears only to the first power — no squares, no products like $xy$, no variables in denominators. That simplicity is deceptive: linear equations model pricing, travel times, mixing problems, age puzzles, and countless exam word problems on the Bagrut 3–4 unit track.

**Solving** means finding every value of the unknown that makes both sides equal. For one variable you usually get a single number; for two variables you get a line (infinitely many ordered pairs); for a **system** of two equations you typically get one point where two lines meet.

**Golden rule:** whatever operation you perform on one side of the equals sign, perform the **same** operation on the other side. Add $7$ to both sides, multiply both sides by $4$, distribute into brackets — always symmetrically. This balance principle is the foundation of every technique in this lesson."""

INTRO_HE = """**משוואה לינארית** קובעת ששני ביטויים לינאריים שווים. המשתנה מופיע רק בחזקה ראשונה — בלי ריבועים, בלי מכפלות כמו $xy$, ובלי משתנים במכנים. הפשטות הזו מטעה: משוואות לינאריות מדגמות תמחור, זמני נסיעה, בעיות ערבוב, חידות גיל ושפע בעיות מילוליות בבגרות 3–4 יחידות.

**פתרון** פירושו מציאת כל ערך של המשתנה שגורם לשני הצדדים להיות שווים. במשתנה אחד בדרך כלל מתקבל מספר יחיד; בשני משתנים — ישר (אינסוף זוגות סדורים); ב**מערכת** של שתי משוואות — בדרך כלל נקודה אחת שבה שני ישרים נחתכים.

**כלל הזהב:** כל פעולה שמבצעים בצד אחד של סימן השוויון, מבצעים **אותה פעולה** בצד השני. מוסיפים $7$ לשני הצדדים, מכפילים ב-$4$, מפזרים לתוך סוגריים — תמיד באופן סימטרי. עקרון האיזון הזה הוא הבסיס לכל שיטה בשיעור."""

DEF_EN = """**Linear equation in one variable** has the form $ax+b=c$ where $a\\ne0$. Isolating $x$ gives the closed form $x=(c-b)/a$. Every such equation has exactly **one** solution unless you reduce to $0=0$ (all $x$ work) or $0=k$ with $k\\ne0$ (no solution).

**Linear equation in two variables** $ax+by=c$ does not have one answer — its graph is a straight line, so there are infinitely many $(x,y)$ pairs satisfying it.

**System of two linear equations:**
$$\\begin{cases} a_1x+b_1y=c_1 \\\\ a_2x+b_2y=c_2 \\end{cases}$$
Geometrically you ask where two lines meet. Algebraically you use **substitution** (express one variable, plug into the other) or **elimination** (add/subtract equations to remove one variable). A third view is **graphical** — plot both lines and read the intersection.

**Solution types for a system:**
| Outcome | Algebra | Geometry |
|---|---|---|
| Unique | one $(x,y)$ | intersecting lines |
| None | contradiction like $0=5$ | parallel lines |
| Infinite | identity like $0=0$ | coincident lines |

Always **define variables** in word problems before writing equations."""

DEF_HE = """**משוואה לינארית במשתנה אחד** בצורה $ax+b=c$ כאשר $a\\ne0$. בידוד $x$ נותן $x=(c-b)/a$. לכל משוואה כזו יש **פתרון יחיד** אלא אם מצטמצמים ל-$0=0$ (כל $x$ מתאים) או ל-$0=k$ עם $k\\ne0$ (אין פתרון).

**משוואה לינארית בשני משתנים** $ax+by=c$ אין לה תשובה אחת — הגרף שלה ישר, ולכן יש אינסוף זוגות $(x,y)$ שמקיימים אותה.

**מערכת של שתי משוואות לינאריות:**
$$\\begin{cases} a_1x+b_1y=c_1 \\\\ a_2x+b_2y=c_2 \\end{cases}$$
גיאומטרית שואלים היכן שני ישרים נחתכים. אלגברית משתמשים ב**הצבה** (בודדים משתנה ומציבים בשנייה) או **חיסור-חיבור** (מוסיפים/מחסרים משוואות כדי להסיר משתנה). תצוגה שלישית — **גרפית**: משרטטים שני ישרים וקוראים את נקודת החיתוך.

**סוגי פתרון למערכת:**
| תוצאה | אלגברה | גיאומטריה |
|---|---|---|
| יחיד | $(x,y)$ אחד | ישרים נחתכים |
| ללא | סתירה כמו $0=5$ | ישרים מקבילים |
| אינסוף | זהות כמו $0=0$ | ישרים חופפים |

בבעיות מילוליות — **הגדירו משתנים** לפני כתיבת המשוואות."""

THEORY_EN = """Use a fixed pipeline for **one-variable** equations:
1. **Expand** brackets with the distributive law.
2. **Collect** all $x$-terms on one side and constants on the other (flip signs when moving).
3. **Divide** by the coefficient of $x$.
4. **Check** by substituting back into the **original** equation.

For **fractions**, multiply **every term** on both sides by the LCD — a classic Bagrut trap is multiplying only some terms.

**Systems — Substitution** works when one equation is already solved for a variable or easy to isolate:
- Solve $y=24-x$ from $x+y=24$.
- Substitute into the second equation to get one equation in $x$ only.

**Systems — Elimination** works when coefficients match or can be matched by scaling:
- Multiply equations so one variable has equal (or opposite) coefficients.
- Add or subtract to eliminate that variable.
- Back-substitute to find the second unknown.

**Checking systems:** plug $(x,y)$ into **both** originals. **Word problems:** translate phrases — "sum" $\\to$ addition, "difference" $\\to$ subtraction, "times as old" $\\to$ multiplication — then solve and answer in context with units."""

THEORY_HE = """עבור משוואה ב**משתנה אחד**, השתמשו בתהליך קבוע:
1. **פתחו** סוגריים לפי חוק הפילוג.
2. **אספו** את כל איברי $x$ לצד אחד וקבועים לצד השני (הפכו סימן בהזזה).
3. **חלקו** במקדם של $x$.
4. **בדקו** בהצבה חזרה ל**משוואה המקורית**.

עבור **שברים**, כפלו **כל איבר** בשני הצדדים במכנה משותף — מלכודת בגרות קלאסית היא כפל רק בחלק מהאיברים.

**מערכות — הצבה** מתאימה כשמשוואה אחת כבר מבודדת משתנה או קל לבודד:
- פתרו $y=24-x$ מ-$x+y=24$.
- הציבו במשוואה השנייה לקבלת משוואה ב-$x$ בלבד.

**מערכות — חיסור-חיבור** כשמקדמים שווים או ניתנים לשיוויון:
- כפלו משוואות כך שמקדם משתנה אחד יהיה שווה (או מנוגד).
- חברו או חסרו כדי להסיר את המשתנה.
- הציבו חזרה למציאת המשתנה השני.

**בדיקת מערכות:** הציבו $(x,y)$ ב**שתי** המשוואות המקוריות. **בעיות מילוליות:** "סכום" $\\to$ חיבור, "הפרש" $\\to$ חיסור, "פי גיל" $\\to$ כפל — ואז ענו בהקשר עם יחידות."""

WE1_EN = """**Solve:** $3(x-2)+5 = 2x+9$.

### Move 1 — Expand brackets
Apply the distributive law on the left: $3(x-2)+5 = 3x-6+5 = 3x-1$.
Both sides are now linear without nested parentheses: $3x-1=2x+9$.
If brackets appear on both sides in other problems, expand **every** bracket before collecting terms — never combine $3(x-2)$ with $2x$ while parentheses remain.

### Move 2 — Collect variable terms
Subtract $2x$ from both sides: $x-1=9$.
Add $1$ to both sides: $x=10$.
Watch signs carefully: moving $-1$ to the right becomes $+1$. A common Bagrut slip is adding instead of subtracting when crossing the equals sign.

### Move 3 — Verify in the original equation
Left side: $3(10-2)+5 = 3(8)+5 = 24+5 = 29$.
Right side: $2(10)+9 = 20+9 = 29$.
Both sides match, so $x=10$ is confirmed. Always substitute into the **original** equation — not an intermediate step — because early arithmetic errors can hide until the final check."""

WE1_HE = """**פתרו:** $3(x-2)+5 = 2x+9$.

### צעד 1 — פתיחת סוגריים
מפזרים בצד שמאל לפי חוק הפילוג: $3(x-2)+5 = 3x-6+5 = 3x-1$.
שני הצדדים לינאריים ללא סוגריים מקוננים: $3x-1=2x+9$.
אם יש סוגריים בשני הצדדים בבעיות אחרות, פתחו **כל** סוגריים לפני איסוף — אל תשלבו $3(x-2)$ עם $2x$ כל עוד הסוגריים קיימים.

### צעד 2 — איסוף איברי משתנה
מחסרים $2x$ משני הצדדים: $x-1=9$.
מוסיפים $1$ לשני הצדדים: $x=10$.
שימו לב לסימנים: הזזת $-1$ ימינה הופכת ל-$+1$. טעות נפוצה בבגרות היא חיבור במקום חיסור במעבר מעל סימן השוויון.

### צעד 3 — אימות במשוואה המקורית
צד שמאל: $3(10-2)+5 = 3(8)+5 = 24+5 = 29$.
צד ימין: $2(10)+9 = 20+9 = 29$.
שני הצדדים שווים, ולכן $x=10$ מאושר. תמיד מציבים ב**משוואה המקורית** — לא בשלב ביניים — כי טעויות מוקדמות עלולות להתחבא עד הבדיקה הסופית."""

CHK1_EN = """The LCD of denominators $2$ and $4$ is $4$. Multiply **every** term on both sides by $4$ — including the right-hand constant:
$$4\\cdot\\frac{x+1}{2} - 4\\cdot\\frac{x-3}{4} = 4\\cdot 3.$$
This clears fractions: $2(x+1)-(x-3)=12$. Expand carefully: $2x+2-x+3=12$, so $x+5=12$ and $x=7$.
**Check:** at $x=7$, left side $=\\frac{8}{2}-\\frac{4}{4}=4-1=3$, matching the right side. Skipping the constant term when multiplying by the LCD is the most common error on this problem type."""

CHK1_HE = """מכנה משותף של $2$ ו-$4$ הוא $4$. כופלים **כל איבר** בשני הצדדים ב-$4$ — כולל הקבוע בימין:
$$4\\cdot\\frac{x+1}{2} - 4\\cdot\\frac{x-3}{4} = 4\\cdot 3.$$
מתקבל $2(x+1)-(x-3)=12$. פתיחה בזהירות: $2x+2-x+3=12$, כלומר $x+5=12$ ו-$x=7$.
**בדיקה:** ב-$x=7$, צד שמאל $=\\frac{8}{2}-\\frac{4}{4}=4-1=3$, תואם לימין. דילוג על הקבוע בכפל ב-LCD הוא הטעות הנפוצה ביותר בסוג זה."""

WE2_EN = """### Move 1 — Translate the words

**Problem:** Two numbers sum to $24$. Three times the first equals twice the second plus $12$. Find the numbers.

Let $x$ = first number, $y$ = second number.
Equations: $x+y=24$ and $3x=2y+12$.

### Move 2 — Substitution

From the sum equation: $y=24-x$.
Substitute into the second: $3x=2(24-x)+12=48-2x+12=60-2x$.
Add $2x$ to both sides: $5x=60$, so $x=12$.
Then $y=24-12=12$.
This method reduced a two-variable system to a single linear equation in $x$ — the core substitution pattern for Bagrut word problems.

### Move 3 — Verify both conditions

Sum: $12+12=24$ ✓. Ratio condition: $3(12)=36$ and $2(12)+12=24+12=36$ ✓.
**Answer:** Both numbers are $12$. Equal numbers are allowed — read the wording carefully; "two numbers" does not require them to be different.

**Exam note:** Always state both values in the answer sentence, not just the algebra. On Bagrut word problems, graders look for a complete sentence with units or context — algebra alone earns partial credit at best.

### Move 4 — Why substitution beat elimination here

The sum equation gives $y=24-x$ immediately — no coefficient scaling needed. Elimination would require multiplying one equation first; substitution saved a step and reduced arithmetic risk."""

WE2_HE = """### צעד 1 — תרגום המילים

**בעיה:** סכום שני מספרים הוא $24$. פי שלושה מהראשון שווה לפי שתיים מהשני פלוס $12$. מצאו את המספרים.

נסמן $x$ = המספר הראשון, $y$ = השני.
משוואות: $x+y=24$ ו-$3x=2y+12$.

### צעד 2 — הצבה

ממשוואת הסכום: $y=24-x$.
מציבים בשנייה: $3x=2(24-x)+12=48-2x+12=60-2x$.
מוסיפים $2x$ לשני הצדדים: $5x=60$, כלומר $x=12$.
אז $y=24-12=12$.
שיטה זו מצמצמת מערכת בשני משתנים למשוואה לינארית אחת ב-$x$ — דפוס ההצבה המרכזי בבעיות מילוליות בבגרות.

### צעד 3 — אימות שני התנאים

סכום: $12+12=24$ ✓. תנאי היחס: $3(12)=36$ ו-$2(12)+12=36$ ✓.
**תשובה:** שני המספרים הם $12$. מספרים שווים מותרים — "שני מספרים" לא דורש הבדלה.

**הערת בחינה:** ציינו את שני הערכים במשפט התשובה, לא רק באלגברה. בבגרות, בודקים משפט שלם עם הקשר — אלגברה בלבד מזכה בניקוד חלקי.

### צעד 4 — למה הצבה עדיפה כאן

משוואת הסכום נותנת $y=24-x$ מיד — בלי כפל מקדמים. חיסור-חיבור היה דורש הכפלה; הצבה חסכה צעד והפחיתה סיכון לטעות חישוב."""

CHK2_EN = """### Move 1 — Choose substitution

The second equation $x-y=1$ isolates $x$ in one step: $x=y+1$. Substitution is faster here than elimination because no coefficient matching is needed.

### Move 2 — Substitute into the first equation

Replace $x$ in $2x+3y=13$:
$$2(y+1)+3y=13 \\Rightarrow 2y+2+3y=13 \\Rightarrow 5y+2=13 \\Rightarrow 5y=11 \\Rightarrow y=\\frac{11}{5}.$$

### Move 3 — Back-substitute for $x$

$x=y+1=\\frac{11}{5}+1=\\frac{16}{5}$.

### Move 4 — Verify in both originals

$2(\\frac{16}{5})+3(\\frac{11}{5})=\\frac{32+33}{5}=13$ ✓ and $\\frac{16}{5}-\\frac{11}{5}=1$ ✓.

**Answer:** $x=\\dfrac{16}{5}$, $y=\\dfrac{11}{5}$."""

CHK2_HE = """### צעד 1 — בחירת הצבה

המשוואה השנייה $x-y=1$ מבודדת $x$ בצעד אחד: $x=y+1$. הצבה מהירה כאן מחיסור-חיבור כי אין צורך לשוות מקדמים.

### צעד 2 — הצבה במשוואה הראשונה

מחליפים $x$ ב-$2x+3y=13$:
$$2(y+1)+3y=13 \\Rightarrow 2y+2+3y=13 \\Rightarrow 5y+2=13 \\Rightarrow 5y=11 \\Rightarrow y=\\frac{11}{5}.$$

### צעד 3 — החזרה ל-$x$

$x=y+1=\\frac{11}{5}+1=\\frac{16}{5}$.

### צעד 4 — אימות בשתי המקוריות

$2(\\frac{16}{5})+3(\\frac{11}{5})=\\frac{32+33}{5}=13$ ✓ ו-$\\frac{16}{5}-\\frac{11}{5}=1$ ✓.

**תשובה:** $x=\\dfrac{16}{5}$, $y=\\dfrac{11}{5}$."""

WE3_EN = """**Given system depending on $k$:**
$$\\begin{cases} kx+2y=4 \\\\ 3x+y=k \\end{cases}$$

For which $k$ does the system have: (a) unique solution, (b) no solution, (c) infinitely many?

### Move 1 — Eliminate $y$
Multiply the second equation by $-2$: $-6x-2y=-2k$.
Add to the first: $(k-6)x=4-2k=2(2-k)$.

### Move 2 — Case $k\\ne6$
Divide by $k-6$: unique $x=\\frac{2(2-k)}{k-6}$. Back-substitute for $y$. **Unique solution.**

### Move 3 — Case $k=6$
Left side becomes $0\\cdot x=0$; right side $2(2-6)=-8\\ne0$. Contradiction $0=-8$. **No solution.**

### Move 4 — Infinite solutions?
Need $0=0$, requiring $2-k=0$ so $k=2$, **and** the lines must coincide ($k=6$ from the second equation). These conditions cannot hold together. **No value of $k$ gives infinitely many solutions.**

**Summary:** $k\\ne6$ → unique solution; $k=6$ → no solution; never infinite for this system.

**Bagrut tip:** When analyzing parametric systems, always separate the cases $k\\ne6$ and $k=6$ before drawing conclusions."""

WE3_HE = """**מערכת עם פרמטר $k$:**
$$\\begin{cases} kx+2y=4 \\\\ 3x+y=k \\end{cases}$$

לאילו $k$ יש: (א) פתרון יחיד, (ב) ללא פתרון, (ג) אינסוף פתרונות?

### צעד 1 — חיסול $y$
מכפילים את המשוואה השנייה ב-$-2$: $-6x-2y=-2k$.
מחברים לראשונה: $(k-6)x=4-2k=2(2-k)$.

### צעד 2 — מקרה $k\\ne6$
מחלקים ב-$k-6$: $x$ יחיד. מציבים חזרה ל-$y$. **פתרון יחיד.**

### צעד 3 — מקרה $k=6$
הצד שמאל $0\\cdot x=0$; הימני $2(2-6)=-8\\ne0$. סתירה $0=-8$. **ללא פתרון.**

### צעד 4 — אינסוף פתרונות?
נדרש $0=0$, כלומר $k=2$, **וגם** שהישרים חופפים ($k=6$ מהמשוואה השנייה). התנאים לא מתקיימים יחד. **אין $k$ עם אינסוף פתרונות.**

**סיכום:** $k\\ne6$ → פתרון יחיד; $k=6$ → ללא פתרון; לעולם לא אינסוף במערכת זו.

**טיפ בגרות:** בניתוח מערכות עם פרמטר, הפרידו תמיד בין $k\\ne6$ ל-$k=6$ לפני מסקנות."""

METHOD_EN = """**One variable — four-step loop:**
1. Expand all brackets.
2. Move variable terms left, constants right (flip signs).
3. Divide by the coefficient.
4. Substitute back to check.

**Systems — pick your tool:**
| Method | Best when |
|---|---|
| Substitution | One equation already has $y=\\ldots$ or $x=\\ldots$ |
| Elimination | Coefficients are equal/opposite after one multiply |
| Graph | Visual check or estimating intersection |

**Outcome recognition:**
- Different slopes → one intersection (unique).
- Same slope, different intercepts → parallel (none).
- Same line twice → infinite solutions.

**Word problems:** Read twice, define variables with words ("let $a$ = adult tickets"), write two independent equations, solve, then answer the **question asked** — not just $(x,y)$."""

METHOD_HE = """**משתנה אחד — ארבעה שלבים:**
1. פתחו את כל הסוגריים.
2. העבירו איברי משתנה לצד אחד, קבועים לשני (הפכו סימן).
3. חלקו במקדם.
4. הציבו חזרה לבדיקה.

**מערכות — בחרו כלי:**
| שיטה | מתי |
|---|---|
| הצבה | משוואה אחת כבר $y=\\ldots$ או $x=\\ldots$ |
| חיסור-חיבור | מקדמים שווים/מנוגדים אחרי כפל אחד |
| גרף | בדיקה ויזואלית או הערכת חיתוך |

**זיהוי תוצאה:**
- שיפועים שונים → חיתוך יחיד.
- אותו שיפוע, חותכים שונים → מקבילים, ללא פתרון.
- אותו ישר פעמיים → אינסוף פתרונות.

**בעיות מילוליות:** קראו פעמיים, הגדירו משתנים במילים, כתבו שתי משוואות בלתי תלויות, פתרו, וענו על **השאלה שנשאלה** — לא רק $(x,y)$."""

PITFALL_EN = """1. **Sign errors when moving terms.** $3x+5=2$ becomes $3x=2-5=-3$, **not** $3x=7$. Flip the sign every time you cross the equals sign.

2. **Incomplete clearing of fractions.** In $\\frac{x}{2}+1=5$, multiply **both** terms on the left by $2$, not just $\\frac{x}{2}$.

3. **Skipping the check.** Substituting back catches arithmetic slips and sign mistakes before you move on.

4. **Confusing "no solution" with "all $x$ work".** $0=5$ means none; $0=0$ means every $x$ satisfies the reduced equation.

5. **Word-problem setup errors.** "Three times the first" is $3x$, not $x+3$. Write what the sentence says, then verify units.

**Fix habit:** After solving, ask "which pitfall could have fooled me?" — that metacognition saves points on Bagrut Section A."""

PITFALL_HE = """1. **שגיאות סימן בהזזת איברים.** $3x+5=2$ הופך ל-$3x=2-5=-3$, **לא** ל-$3x=7$. הפכו סימן בכל מעבר מעל סימן השוויון.

2. **ניקוי שברים חלקי.** ב-$\\frac{x}{2}+1=5$, כפלו **את שני** האיברים בצד שמאל ב-$2$, לא רק את $\\frac{x}{2}$.

3. **דילוג על בדיקה.** הצבה חזרה תופסת טעויות חישוב וסימן לפני שממשיכים.

4. **בלבול "ללא פתרון" עם "כל $x$ מתאים".** $0=5$ = אין; $0=0$ = כל $x$ מקיים את המשוואה המצומצמת.

5. **טעויות הגדרה בבעיות מילוליות.** "פי שלושה מהראשון" = $3x$, לא $x+3$. כתבו מה שהמשפט אומר, ואמתו יחידות.

**הרגל תיקון:** אחרי פתרון, שאלו "איזו מלכודת הייתה עלולה לבלבל אותי?" — המטא-קוגניציה הזו מצילה נקודות בבגרות."""

WHY_EN = """Linear equations are the **algebraic backbone** of the entire high-school math path. Every linear function graph, every rate problem, and every introductory optimization question eventually reduces to solving $ax+b=c$ or a $2\\times2$ system.

**Recommended next topics on A Step Forward:**
- `concept:algebra_basics` — reinforces manipulation fluency before quadratics.
- `concept:functions_linear` — connects solutions to graphs, slope, and intercept.

**Why exams care:** Bagrut rewards *transfer* — the same "define variables → write equations → solve → interpret" loop appears inside geometry, trigonometry word problems, and physics kinematics. Master this lesson once and you reuse the template everywhere."""

WHY_HE = """משוואות לינאריות הן **עמוד השדרה האלגברי** של כל מסלול המתמטיקה בתיכון. כל גרף של פונקציה לינארית, כל בעיית קצב, וכל שאלת אופטימיזציה בסיסית מצטמצמות בסופו של דבר לפתרון $ax+b=c$ או מערכת $2\\times2$.

**נושאים מומלצים להמשך ב-A Step Forward:**
- `concept:algebra_basics` — מחזק שליטה בטרם ריבועיות.
- `concept:functions_linear` — מחבר פתרונות לגרפים, שיפוע וחותך.

**למה בחינות אכפת:** בבגרות מעריכים *העברה* — אותו לולאה "הגדר משתנים → כתוב משוואות → פתור → פרש" חוזרת בגיאומטריה, טריגונומטריה מילולית וקינמטיקה בפיזיקה. שליטה בשיעור הזה = תבנית לכל השאר."""

BEFORE_EN = """**One-variable checklist:**
1. Expand brackets completely.
2. Collect like terms; flip signs when moving.
3. Isolate the variable; watch dividing by zero.
4. Substitute into the **original** equation.

**System checklist:**
1. Label equations (1) and (2).
2. Choose substitution vs elimination deliberately.
3. Solve for one variable, back-substitute for the other.
4. Verify in **both** originals.

**Word problems:** Underline numbers and relationships; define variables in a box; answer with units ("80 adult tickets").

**Last-minute review:** Solve one fraction equation and one $2\\times2$ system without notes — if both check, you are exam-ready."""

BEFORE_HE = """**רשימת משתנה אחד:**
1. פתחו סוגריים לגמרי.
2. אספו איברים דומים; הפכו סימן בהזזה.
3. בודדו משתנה; שימו לב לחלוקה באפס.
4. הציבו ב**משוואה המקורית**.

**רשימת מערכת:**
1. סמנו משוואות (1) ו-(2).
2. בחרו הצבה או חיסור-חיבור במודע.
3. פתרו משתנה אחד, הציבו חזרה לשני.
4. אמתו ב**שתי** המקוריות.

**בעיות מילוליות:** הדגישו מספרים ויחסים; הגדירו משתנים; ענו עם יחידות ("80 כרטיסי מבוגר").

**חזרה אחרונה:** פתרו משוואת שבר ומערכת $2\\times2$ בלי רשימות — אם שתיהן עוברות בדיקה, אתם מוכנים."""

SUMMARY_EN = """- **One variable:** $ax+b=c \\Rightarrow x=(c-b)/a$ after balancing both sides.
- **Two variables:** one equation = a line; need a system for a unique point.
- **Methods:** substitution when isolation is easy; elimination when coefficients align.
- **Always check** by substituting into original equation(s).
- **Word problems:** translate → define → solve → interpret with units.

**Takeaway:** Read the problem type first — the method follows from the structure, not from habit."""

SUMMARY_HE = """- **משתנה אחד:** $ax+b=c \\Rightarrow x=(c-b)/a$ אחרי איזון שני הצדדים.
- **שני משתנים:** משוואה אחת = ישר; צריך מערכת לנקודה יחידה.
- **שיטות:** הצבה כשבידוד קל; חיסור-חיבור כשמקדמים מתיישרים.
- **תמיד בדקו** בהצבה למשוואה/ות המקורית.
- **בעיות מילוליות:** תרגמו → הגדירו → פתרו → פרשו עם יחידות.

**מסקנה:** קראו קודם את סוג הבעיה — השיטה הנכונה נגזרת מהמבנה, לא מהרגל, לא מזיכרון."""

EXPLS = {
    1: fmt_expl(
        "Add $7$ to both sides of $4x-7=13$ to get $4x=20$, then divide by $4$: $x=5$. Each step preserves equality because the same operation hits both sides.",
        "One-variable linear equations follow the balance principle: undo operations in reverse order of how they wrap $x$ — first remove the constant subtracted from $x$, then divide by the coefficient.",
        "Getting $x=6$ by adding $7+13$ without isolating $4x$ first, or dividing before moving the $-7$ term.",
        "On multiple-choice items, plug each option back into the original equation — the correct one makes both sides equal in one substitution.",
        "מוסיפים $7$ לשני צדי $4x-7=13$ ומקבלים $4x=20$, מחלקים ב-$4$: $x=5$. כל צעד שומר על שוויון כי אותה פעולה בשני הצדדים.",
        "משוואה לינארית במשתנה אחד עובדת לפי איזון: מבטלים פעולות בסדר הפוך — קודם מסירים קבוע, אחר כך מחלקים במקדם.",
        "לקבל $x=6$ מחיבור $7+13$ בלי לבודד $4x$ קודם, או לחלק לפני הזזת $-7$.",
        "בשאלות רב-ברירה, הציבו כל אפשרות במשוואה המקורית — הנכונה משווה את שני הצדדים בבדיקה אחת.",
    ),
    2: fmt_expl(
        "Subtract $2x$ from both sides: $5x-2x-3=12$, so $3x=15$ and $x=5$. Moving all $x$-terms to one side and constants to the other is the standard collection step.",
        "When the same variable appears on both sides, treat it like combining like terms — you are asking how many $x$'s remain after canceling the overlap.",
        "Leaving $3x=15-2x$ and stopping, or sign error when moving $-3$ across the equals sign.",
        "After finding $x$, spend five seconds substituting into the original $5x-3=2x+12$ — Bagrut partial credit often requires a visible check.",
        "מחסרים $2x$ משני הצדדים: $5x-2x-3=12$, כלומר $3x=15$ ו-$x=5$. איסוף כל איברי $x$ לצד אחד וקבועים לשני הוא הצעד הסטנדרטי.",
        "כשאותו משתנה בשני הצדדים, מתייחסים לזה כאל איברים דומים — כמה $x$ נשארים אחרי ביטול החפיפה.",
        "להשאיר $3x=15-2x$ ולעצור, או שגיאת סימן בהזזת $-3$ מעל סימן השוויון.",
        "אחרי מציאת $x$, הציבו ב-$5x-3=2x+12$ — בבגרות לעיתים נדרשת בדיקה גלויה לניקוד חלקי, גם כשהתשובה הסופית נראית ברורה לחלוטין.",
    ),
    3: fmt_expl(
        "Expand: $2x+8=3x-3$. Subtract $2x$: $8=3x-3$. Add $3$: $11=3x$, so $x=11$. Distributive law on the left and right must be applied before collecting terms.",
        "Equations with brackets on both sides demand expansion first — you cannot combine $2(x+4)$ with $3x$ until the parentheses are gone.",
        "Expanding only one side, or getting $x=-11$ by subtracting $8$ from the wrong side.",
        "If distribution feels heavy, expand both sides on scratch paper and circle matching $x$-terms — symmetry prevents one-sided mistakes.",
        "פתיחה: $2x+8=3x-3$. מחסרים $2x$: $8=3x-3$. מוסיפים $3$: $11=3x$, כלומר $x=11$. חוק הפילוג בשני הצדדים לפני איסוף.",
        "משוואות עם סוגריים בשני הצדדים דורשות פתיחה קודם — אי אפשר לשלב $2(x+4)$ עם $3x$ לפני שהסוגריים נעלמו.",
        "פתיחה של צד אחד בלבד, או $x=-11$ מחיסור $8$ מהצד הלא נכון.",
        "אם הפילוג כבד, פתחו שני צדדים על טיוטה והקיפו איברי $x$ תואמים — סימטריה מונעת טעויות חד-צדדיות.",
    ),
    4: fmt_expl(
        "Subtract $1$ from both sides: $\\frac{x}{3}=4$. Multiply by $3$: $x=12$. Clearing fractions means multiplying every term by the denominator, not just the fraction.",
        "When $x$ sits inside a denominator of $3$, think 'undo division by 3' as the last step — first isolate the fractional term, then multiply.",
        "Multiplying only $\\frac{x}{3}$ by $3$ but forgetting the $+1$ term, yielding $x=15$ incorrectly.",
        "Fraction equations appear often in Section B — write the LCD prominently at the top of your work so graders see you cleared all terms.",
        "מחסרים $1$ משני הצדדים: $\\frac{x}{3}=4$. מכפילים ב-$3$: $x=12$. ניקוי שברים = כפל **כל** איבר במכנה, לא רק השבר.",
        "כש-$x$ בתוך מכנה $3$, חשבו 'לבטל חלוקה ב-3' כצעד אחרון — קודם בודדים את האיבר השברי, אחר כך מכפילים.",
        "כפל רק $\\frac{x}{3}$ ב-$3$ ושכחת $+1$, וקבלת $x=15$ שגוי.",
        "משוואות שבר תכופות בפרק B — כתבו מכנה משותף בראש העבודה כדי שהבודק יראה שניקיתם הכל.",
    ),
    5: fmt_expl(
        "Adding the equations eliminates $y$: $(x+y)+(x-y)=7+3$, so $2x=10$ and $x=5$. Then $y=7-5=2$. Elimination works when coefficients of one variable are opposites.",
        "When you see $+y$ and $-y$ with the same magnitude, addition is faster than substitution — one step removes an entire variable.",
        "Subtracting instead of adding and getting $2y=4$, or finding $x$ but forgetting to compute $y$ when the question asks for both.",
        "Always write $(x,y)$ as an ordered pair in the answer line — some rubrics deduct if only one coordinate is stated.",
        "חיבור המשוואות מבטל $y$: $(x+y)+(x-y)=7+3$, כלומר $2x=10$ ו-$x=5$. אז $y=7-5=2$. חיסור-חיבור עובד כשמקדמי משתנה אחד מנוגדים.",
        "כשיש $+y$ ו-$-y$ באותה גודל, חיבור מהיר מהצבה — צעד אחד מסיר משתנה שלם.",
        "חיסור במקום חיבור ו-$2y=4$, או מציאת $x$ בלי $y$ כששואלים על שניהם.",
        "כתבו $(x,y)$ כזוג סדור בתשובה — לעיתים מורידים נקודות אם מציינים קואורדינטה אחת בלבד, גם כשהחישוב עצמו נכון לחלוטין.",
    ),
    6: fmt_expl(
        "Let $a$ = adult tickets, $c$ = child tickets. System: $a+c=180$ and $40a+25c=5700$. From the first, $a=180-c$. Substitute: $40(180-c)+25c=5700$, simplify to $-15c=-1500$, so $c=100$ and $a=80$.",
        "Ticket/revenue word problems always give two facts — a count equation and a money equation. Define variables with words, then write the system before any arithmetic.",
        "Using $40+25=65$ per ticket incorrectly, or swapping adult and child counts in the revenue line.",
        "Quick sanity check: $80\\times40+100\\times25=3200+2500=5700$ — if revenue fails, re-read which price attaches to which variable.",
        "נסמן $a$ = כרטיסי מבוגר, $c$ = ילדים. מערכת: $a+c=180$ ו-$40a+25c=5700$. מראשונה $a=180-c$. הצבה: $40(180-c)+25c=5700$, מתקבל $-15c=-1500$, כלומר $c=100$ ו-$a=80$.",
        "בעיות כרטיסים/הכנסה נותנות שני נתונים — משוואת כמות ומשוואת כסף. הגדירו משתנים במילים, כתבו מערכת לפני חישוב.",
        "שימוש שגוי ב-$40+25=65$ לכרטיס, או החלפת מבוגר/ילד בשורת ההכנסה.",
        "בדיקת שפיות: $80\\times40+100\\times25=5700$ — אם ההכנסה לא מתאימה, קראו מחדש איזה מחיר שייך לאיזה משתנה.",
    ),
    7: fmt_expl(
        "LCD is $6$. Multiply every term: $2(2x+1)-(x-2)=6$. Expand: $4x+2-x+2=6$, so $3x+4=6$, $3x=2$, $x=\\frac{2}{3}$. Both fractions must be cleared simultaneously.",
        "When denominators differ ($3$ and $6$), pick the larger LCD once and apply it to the constant on the right as well — the equals sign means both sides scale together.",
        "Forgetting to distribute the $2$ in $2(2x+1)$, or dropping the $(x-2)$ sign when subtracting the second fraction.",
        "Fraction answers like $\\frac{2}{3}$ are common — do not round unless the stem asks; exact form shows you cleared fractions algebraically.",
        "מכנה משותף $6$. כופלים כל איבר: $2(2x+1)-(x-2)=6$. פתיחה: $4x+2-x+2=6$, כלומר $3x=2$ ו-$x=\\frac{2}{3}$. יש לנקות את שני השברים יחד.",
        "כשמכנים שונים ($3$ ו-$6$), בוחרים LCD אחד ומיישמים גם על הקבוע בימין — שני הצדדים מתכפלים יחד.",
        "שכחת פילוג $2$ ב-$2(2x+1)$, או סימן שגוי ב-$(x-2)$ בחיסור השבר השני.",
        "תשובות שבר כמו $\\frac{2}{3}$ נפוצות — אל תעגלו אלא אם נדרש; צורה מדויקת מראה ניקוי אלגברי.",
    ),
    8: fmt_expl(
        "Let larger number be $x$, smaller be $y$. Equations: $x-y=8$ and $x+y=34$. Add: $2x=42$, $x=21$. Subtract in the second: $y=13$. Verify: $21-13=8$ and $21+13=34$.",
        "'Difference' and 'sum' language maps directly to subtraction and addition equations — two sentences give you a ready-made $2\\times2$ system without extra setup.",
        "Writing $x+y=8$ instead of $x-y=8$, or solving for $x$ only when the question asks for both numbers.",
        "Adding the two equations is the fastest move here — when coefficients of $y$ are $+1$ and $-1$, elimination beats substitution every time.",
        "נסמן $x$ גדול, $y$ קטן. משוואות: $x-y=8$ ו-$x+y=34$. חיבור: $2x=42$, $x=21$. מהשנייה $y=13$. אימות: $21-13=8$ ו-$21+13=34$.",
        "ניסוח 'הפרש' ו'סכום' מתורגם ישירות לחיסור וחיבור — שני משפטים נותנים מערכת $2\\times2$ מוכנה.",
        "כתיבת $x+y=8$ במקום $x-y=8$, או פתרון $x$ בלבד כששואלים על שני המספרים.",
        "חיבור שתי המשוואות הוא הצעד המהיר — כשמקדמי $y$ הם $+1$ ו-$-1$, חיסור-חיבור עדיף על הצבה וחוסך זמן בבחינה.",
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
            if "dfrac" in sec.get("body_en_md", "") or "frac" in sec.get("body_en_md", ""):
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
        elif sec.get("id") == "why_matters" or kind == "why_matters":
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
