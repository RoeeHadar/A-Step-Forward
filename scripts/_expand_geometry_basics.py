#!/usr/bin/env python3
"""Expand geometry_basics.json per .cursor/skills/expand-lessons-cursor/SKILL.md."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/geometry_basics.json"

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


INTRO_EN = """Architects design buildings with exact angles. Engineers verify that bridges stay level. Carpenters cut wood at precise angles so pieces fit together. GPS navigation, robotics, and even video-game graphics all rely on the same angle rules you will master in this lesson.

In Israeli high-school geometry (Bagrut 3 units), **angle relationships** appear in nearly every proof and calculation question. You do not need advanced algebra — you need to recognize patterns and apply four core rules automatically:

- Angles on a straight line sum to $180°$.
- Parallel lines cut by a transversal create equal and supplementary angle pairs.
- The interior angles of any triangle sum to $180°$.
- An exterior angle of a triangle equals the sum of the two non-adjacent interior angles.

Once these four rules become reflexes, most geometry problems on the exam unlock in two or three steps. This lesson builds that fluency from the ground up."""

INTRO_HE = """אדריכלים מתכננים מבנים עם זוויות מדויקות. מהנדסים בודקים שגשרים נשארים ישרים. נגרים חותכים עץ בזוויות מדויקות כדי שהחלקים יתאימו. ניווט GPS, רובוטיקה ואפילו גרפיקה במשחקי מחשב — כולם נשענים על אותם כללי זוויות שתשלטו בהם בשיעור זה.

בגיאומטריה של תיכון (בגרות 3 יחידות), **יחסי זוויות** מופיעים כמעט בכל שאלת הוכחה וחישוב. אין צורך באלגברה מתקדמת — צריך לזהות דפוסים וליישם ארבעה כללים מרכזיים באופן אוטומטי:

- זוויות על קו ישר מסתכמות ל-$180°$.
- קווים מקבילים הנחתכים על ידי חותכת יוצרים זוגות זוויות שוות ומשלימות.
- זוויות פנימיות בכל משולש מסתכמות ל-$180°$.
- זווית חיצונית של משולש שווה לסכום שתי הזוויות הפנימיות שאינן סמוכות.

ברגע שארבעת הכללים האלה הופכים לרפלקס, רוב שאלות הגאומטריה בבחינה נפתחות בשניים-שלושה צעדים. השיעור בונה את השטף הזה מהיסוד."""

DEF_EN = """**Angles on a straight line:** Any two adjacent angles that form a straight line are **supplementary** — they sum to $180°$. This is the most basic angle rule and appears inside almost every diagram.

**Vertically opposite angles:** When two lines cross, the angles opposite each other at the intersection are **equal**. Each pair shares no common side.

**Parallel lines and a transversal** (8 angles formed at two intersections):
- **Corresponding angles** (same position at each intersection): **equal** when lines are parallel. Look for the "F-shape."
- **Alternate interior angles** (between the parallels, on opposite sides of the transversal): **equal**. Look for the "Z-shape."
- **Co-interior angles** (between the parallels, on the same side): **supplementary** — they sum to $180°$. Also called same-side interior or consecutive interior angles.

**Triangle angle sum:**
$$\\angle A + \\angle B + \\angle C = 180°$$
This holds for every triangle — acute, right, or obtuse.

**Exterior angle theorem:**
An exterior angle of a triangle equals the sum of the two **non-adjacent** interior angles:
$$\\angle_{\\text{ext}} = \\angle A + \\angle B$$
where $A$ and $B$ are the two vertices not on the extended side.

**Quadrilateral angle sum:** Split any quadrilateral by a diagonal into two triangles → interior angles sum to $360°$."""

DEF_HE = """**זוויות על קו ישר:** שתי זוויות סמוכות שיוצרות קו ישר הן **משלימות** — מסתכמות ל-$180°$. זהו כלל הזוויות הבסיסי ביותר ומופיע כמעט בכל דיאגרמה.

**זוויות קודקודיות:** כאשר שני קווים מצטלבים, הזוויות הנגדיות זו לזו בנקודת החיתוך **שוות**. לכל זוג אין צלע משותפת.

**קווים מקבילים וחותכת** (8 זוויות בשתי נקודות חיתוך):
- **זוויות מתאימות** (אותו מיקום בכל חיתוך): **שוות** כשהקווים מקבילים. חפשו צורת F.
- **זוויות מתחלפות פנימיות** (בין המקבילים, בצדדים מנוגדים של החותכת): **שוות**. חפשו צורת Z.
- **זוויות חד-צדיות פנימיות** (בין המקבילים, באותו צד): **משלימות** — מסתכמות ל-$180°$. נקראות גם זוויות פנימיות עוקבות.

**סכום זוויות משולש:**
$$\\angle A + \\angle B + \\angle C = 180°$$
נכון לכל משולש — חד-זוויתי, ישר-זוויתי או קהה-זוויתי.

**משפט הזווית החיצונית:**
זווית חיצונית של משולש שווה לסכום שתי הזוויות הפנימיות **שאינן סמוכות**:
$$\\angle_{\\text{ext}} = \\angle A + \\angle B$$
כאשר $A$ ו-$B$ הם שני הקודקודים שלא על הצלע המוארכת.

**סכום זוויות מרובע:** פיצול מרובע באלכסון לשני משולשים → זוויות פנימיות מסתכמות ל-$360°$."""

THEORY_EN = """When a transversal crosses two parallel lines, it creates **8 angles** — four at each intersection. A reliable labeling scheme prevents confusion on the Bagrut.

### Labeling the 8 angles

At the **top** intersection (where the transversal meets the upper parallel), label going clockwise: $\\angle 1$ (upper-left), $\\angle 2$ (upper-right), $\\angle 3$ (lower-right at top), $\\angle 4$ (lower-left at top). At the **bottom** intersection: $\\angle 5, 6, 7, 8$ in the same pattern.

### Equal angle pairs (parallel lines assumed)

| Relationship | Equal pairs |
|---|---|
| Corresponding | $\\angle 1=\\angle 5$, $\\angle 2=\\angle 6$, $\\angle 3=\\angle 7$, $\\angle 4=\\angle 8$ |
| Alternate interior | $\\angle 3=\\angle 6$, $\\angle 4=\\angle 5$ |
| Vertically opposite | $\\angle 1=\\angle 3$, $\\angle 2=\\angle 4$; $\\angle 5=\\angle 7$, $\\angle 6=\\angle 8$ |

### Supplementary pairs

- **On a straight line:** $\\angle 1 + \\angle 2 = 180°$ (and similarly at every linear pair).
- **Co-interior (same side):** $\\angle 3 + \\angle 5 = 180°$, $\\angle 4 + \\angle 6 = 180°$.

### Strategy for complex diagrams

1. Mark every known angle on the diagram.
2. Use vertically opposite angles and straight-line sums at each intersection.
3. Apply triangle angle sum if a triangle appears.
4. Use parallel-line rules last — they propagate values across the whole figure.

**Key insight:** Once you know one angle in a parallel-line figure, you can derive all eight. The acute and obtuse values alternate around each intersection."""

THEORY_HE = """כאשר חותכת חוצה שני קווים מקבילים, נוצרות **8 זוויות** — ארבע בכל נקודת חיתוך. סימון עקבי מונע בלבול בבגרות.

### סימון 8 הזוויות

ב**חיתוך העליון** (החותכת פוגשת את המקביל העליון), סמנו עם כיוון השעון: $\\angle 1$ (שמאל-עליון), $\\angle 2$ (ימין-עליון), $\\angle 3$ (ימין-תחתון למעלה), $\\angle 4$ (שמאל-תחתון למעלה). ב**חיתוך התחתון**: $\\angle 5, 6, 7, 8$ באותו דפוס.

### זוגות שווים (בהנחה שהקווים מקבילים)

| יחס | זוגות שווים |
|---|---|
| מתאימות | $\\angle 1=\\angle 5$, $\\angle 2=\\angle 6$, $\\angle 3=\\angle 7$, $\\angle 4=\\angle 8$ |
| מתחלפות פנימיות | $\\angle 3=\\angle 6$, $\\angle 4=\\angle 5$ |
| קודקודיות | $\\angle 1=\\angle 3$, $\\angle 2=\\angle 4$; $\\angle 5=\\angle 7$, $\\angle 6=\\angle 8$ |

### זוגות משלימות

- **על קו ישר:** $\\angle 1 + \\angle 2 = 180°$ (וכן בכל זוג לינארי).
- **חד-צדיות פנימיות (אותו צד):** $\\angle 3 + \\angle 5 = 180°$, $\\angle 4 + \\angle 6 = 180°$.

### אסטרטגיה לדיאגרמות מורכבות

1. סמנו כל זווית ידועה על הציור.
2. השתמשו בקודקודיות ובסכום על קו ישר בכל חיתוך.
3. יישמו סכום זוויות משולש אם מופיע משולש.
4. השתמשו בכללי קווים מקבילים אחרון — הם מפיצים ערכים על כל הציור.

**תובנה מרכזית:** ברגע שיודעים זווית אחת בציור עם מקבילים, אפשר לגזור את כל שמונה. הערכים החדים והקהים מתחלפים סביב כל חיתוך."""

WE1_EN = """**Problem:** A triangle has angles $50°$ and $70°$. Find the third angle and classify the triangle.

### Move 1: Write the triangle angle-sum formula
The interior angles of any triangle always sum to $180°$:
$$\\angle A + \\angle B + \\angle C = 180°$$

### Move 2: Substitute the known angles
$$50° + 70° + \\angle C = 180°$$
$$120° + \\angle C = 180°$$

### Move 3: Solve for the unknown angle
$$\\angle C = 180° - 120° = 60°$$

### Move 4: Classify the triangle
All three angles ($50°$, $70°$, $60°$) are less than $90°$, so the triangle is **acute** (all angles acute).

**Check:** $50° + 70° + 60° = 180°$ ✓

**Why this method:** The angle-sum rule is the first tool for any triangle with two known angles. On the Bagrut, you often must both compute the missing angle and name the triangle type — do not stop after the arithmetic.

**Exam tip:** After finding $\\angle C = 60°$, scan all three angles against $90°$ before writing "acute," "right," or "obtuse."

**Answer:** Third angle $= 60°$; acute triangle."""

WE1_HE = """**בעיה:** למשולש זוויות $50°$ ו-$70°$. מצאו את הזווית השלישית וסווגו את המשולש.

### צעד 1: כתיבת נוסחת סכום זוויות המשולש
זוויות פנימיות בכל משולש מסתכמות תמיד ל-$180°$:
$$\\angle A + \\angle B + \\angle C = 180°$$

### צעד 2: הצבת הזוויות הידועות
$$50° + 70° + \\angle C = 180°$$
$$120° + \\angle C = 180°$$

### צעד 3: פתרון לזווית החסרה
$$\\angle C = 180° - 120° = 60°$$

### צעד 4: סיווג המשולש
כל שלוש הזוויות ($50°$, $70°$, $60°$) קטנות מ-$90°$, לכן המשולש **חד-זוויתי** (כל הזוויות חדות).

**בדיקה:** $50° + 70° + 60° = 180°$ ✓

**למה השיטה:** כלל סכום הזוויות הוא הכלי הראשון בכל משולש עם שתי זוויות ידועות. בבגרות, לעיתים צריך גם לחשב את הזווית החסרה וגם לציין את סוג המשולש — אל תעצרו אחרי החישוב.

**טיפ לבחינה:** אחרי $\\angle C = 60°$, השוו את שלוש הזוויות ל-$90°$ לפני שכותבים "חד-זוויתי", "ישר-זוויתי" או "קהה-זוויתי".

**תשובה:** הזווית השלישית $= 60°$; משולש חד-זוויתי."""

WE2_EN = """**Problem:** Two parallel lines are cut by a transversal. One of the angles formed is $65°$. Find all 8 angles.

### Move 1: Assign the given angle
Call the given angle $\\angle 1 = 65°$ (upper-left at the top intersection).

### Move 2: Vertically opposite at the top
$\\angle 3 = \\angle 1 = 65°$ (lower-right at the top intersection — directly opposite).

### Move 3: Supplementary angles on a straight line at the top
$\\angle 2 = 180° - 65° = 115°$ (upper-right at top).
$\\angle 4 = \\angle 2 = 115°$ (lower-left at top — vertically opposite to $\\angle 2$).

### Move 4: Corresponding angles at the bottom intersection
Because the lines are parallel:
$\\angle 5 = \\angle 1 = 65°$, $\\angle 6 = \\angle 2 = 115°$, $\\angle 7 = \\angle 3 = 65°$, $\\angle 8 = \\angle 4 = 115°$.

**Summary:**
- Angles $= 65°$: $\\angle 1, \\angle 3, \\angle 5, \\angle 7$ (four acute angles)
- Angles $= 115°$: $\\angle 2, \\angle 4, \\angle 6, \\angle 8$ (four obtuse angles)

**Check:** Every adjacent pair on a line sums to $180°$: $65° + 115° = 180°$ ✓

**Why this method:** Label one intersection completely before jumping to the second. Corresponding angles then copy the pattern to the other intersection in one step.

**Exam tip:** State which rule you use ("corresponding angles → equal") — graders award partial credit for correct reasoning even if a label is wrong."""

WE2_HE = """**בעיה:** שני קווים מקבילים נחתכים על ידי חותכת. אחת הזוויות היא $65°$. מצאו את כל 8 הזוויות.

### צעד 1: שימת הזווית הנתונה
$\\angle 1 = 65°$ (שמאל-עליון בחיתוך העליון).

### צעד 2: קודקודיות בחיתוך העליון
$\\angle 3 = \\angle 1 = 65°$ (ימין-תחתון בחיתוך העליון — נגדית ישירה).

### צעד 3: זוגות משלימות על קו ישר בחיתוך העליון
$\\angle 2 = 180° - 65° = 115°$ (ימין-עליון).
$\\angle 4 = \\angle 2 = 115°$ (שמאל-תחתון — קודקודית ל-$\\angle 2$).

### צעד 4: זוויות מתאימות בחיתוך התחתון
הקווים מקבילים, לכן:
$\\angle 5 = \\angle 1 = 65°$, $\\angle 6 = \\angle 2 = 115°$, $\\angle 7 = \\angle 3 = 65°$, $\\angle 8 = \\angle 4 = 115°$.

**סיכום:**
- זוויות $= 65°$: $\\angle 1, \\angle 3, \\angle 5, \\angle 7$ (ארבע חדות)
- זוויות $= 115°$: $\\angle 2, \\angle 4, \\angle 6, \\angle 8$ (ארבע קהות)

**בדיקה:** כל זוג סמוך על קו מסתכם ל-$180°$: $65° + 115° = 180°$ ✓

**למה השיטה:** סמנו חיתוך אחד לגמרי לפני המעבר לשני. זוויות מתאימות מעתיקות את הדפוס לחיתוך השני בצעד אחד.

**טיפ לבחינה:** ציינו איזה כלל השתמשתם ("זוויות מתאימות → שוות") — בודקים נותנים ניקוד חלקי על נימוק נכון גם אם הסימון שגוי."""

WE3_EN = """**Problem:** In triangle $ABC$: $\\angle A = 40°$, $\\angle B = 75°$. Side $BC$ is extended to point $D$.
(a) Find $\\angle C$ (interior angle at $C$).
(b) Find $\\angle ACD$ (exterior angle at $C$).
(c) Verify using the exterior angle theorem.

### Move 1: Interior angle $\\angle C$ via triangle sum
$$\\angle A + \\angle B + \\angle C = 180°$$
$$40° + 75° + \\angle C = 180°$$
$$\\angle C = 180° - 115° = 65°$$

### Move 2: Exterior angle $\\angle ACD$ via supplementary angles
$\\angle ACB$ and $\\angle ACD$ form a straight line at $C$:
$$\\angle ACD = 180° - \\angle C = 180° - 65° = 115°$$

### Move 3: Verify with the exterior angle theorem
The exterior angle at $C$ should equal the sum of the two non-adjacent interior angles ($\\angle A$ and $\\angle B$):
$$\\angle ACD = \\angle A + \\angle B = 40° + 75° = 115° \\checkmark$$

**Why both methods agree:** The exterior angle theorem is not magic — it follows from triangle sum plus supplementary angles. Bagrut questions often ask you to compute both ways to prove you understand the link.

**Common slip:** Using $\\angle C$ (adjacent interior) instead of $\\angle A + \\angle B$ in the exterior angle theorem.

**Answer:** (a) $65°$, (b) $115°$, (c) Verified."""

WE3_HE = """**בעיה:** במשולש $ABC$: $\\angle A = 40°$, $\\angle B = 75°$. הצלע $BC$ מוארכת לנקודה $D$.
(א) מצאו $\\angle C$ (זווית פנימית ב-$C$).
(ב) מצאו $\\angle ACD$ (זווית חיצונית ב-$C$).
(ג) אמתו בעזרת משפט הזווית החיצונית.

### צעד 1: זווית פנימית $\\angle C$ דרך סכום זוויות המשולש
$$\\angle A + \\angle B + \\angle C = 180°$$
$$40° + 75° + \\angle C = 180°$$
$$\\angle C = 180° - 115° = 65°$$

### צעד 2: זווית חיצונית $\\angle ACD$ דרך זוויות משלימות
$\\angle ACB$ ו-$\\angle ACD$ יוצרות קו ישר ב-$C$:
$$\\angle ACD = 180° - \\angle C = 180° - 65° = 115°$$

### צעד 3: אימות במשפט הזווית החיצונית
הזווית החיצונית ב-$C$ שווה לסכום שתי הזוויות הפנימיות שאינן סמוכות ($\\angle A$ ו-$\\angle B$):
$$\\angle ACD = \\angle A + \\angle B = 40° + 75° = 115° \\checkmark$$

**למה שתי השיטות מתאימות:** משפט הזווית החיצונית נגזר מסכום זוויות המשולש ומזוויות משלימות. בבגרות לעיתים מבקשים לחשב בשתי דרכים כדי להוכיח הבנה.

**טעות נפוצה:** שימוש ב-$\\angle C$ (פנימית סמוכה) במקום $\\angle A + \\angle B$ במשפט הזווית החיצונית.

**תשובות:** (א) $65°$, (ב) $115°$, (ג) מאומת."""

CHK1_EN = """**Step 1 — Find the third angle**

Using the triangle angle-sum rule:
$$\\angle C = 180° - 35° - 85° = 60°$$

**Step 2 — Classify the triangle**

Compare each angle to $90°$:
- $\\angle A = 35° < 90°$ (acute)
- $\\angle B = 85° < 90°$ (acute)
- $\\angle C = 60° < 90°$ (acute)

All three angles are less than $90°$, so the triangle is **acute**.

**Check:** $35° + 85° + 60° = 180°$ ✓

**Common slip:** Stopping at $60°$ without classifying, or calling it obtuse because $85°$ is "close to" $90°$. Only an angle **greater than** $90°$ makes a triangle obtuse."""

CHK1_HE = """**שלב 1 — מציאת הזווית השלישית**

לפי כלל סכום זוויות המשולש:
$$\\angle C = 180° - 35° - 85° = 60°$$

**שלב 2 — סיווג המשולש**

השוו כל זווית ל-$90°$:
- $\\angle A = 35° < 90°$ (חדה)
- $\\angle B = 85° < 90°$ (חדה)
- $\\angle C = 60° < 90°$ (חדה)

כל שלוש הזוויות קטנות מ-$90°$, לכן המשולש **חד-זוויתי**.

**בדיקה:** $35° + 85° + 60° = 180°$ ✓

**טעות נפוצה:** לעצור ב-$60°$ בלי לסווג, או לקרוא "קהה-זוויתי" כי $85°$ "קרוב ל-$90°$". רק זווית **גדולה מ-$90°$** הופכת משולש לקהה-זוויתי."""

CHK2_EN = """Given: parallel lines cut by a transversal, one angle $= 110°$.

**(a) Co-interior angle (same side, between parallels)**

Co-interior angles on the same side of the transversal are **supplementary**:
$$\\text{Co-interior} = 180° - 110° = 70°$$

**(b) Alternate interior angle**

Alternate interior angles (between the parallels, opposite sides) are **equal**:
$$\\text{Alternate interior} = 110°$$

**Why the answers differ:** Co-interior and alternate interior are different relationships — one sums to $180°$, the other copies the value. Always identify which sides of the transversal the angles lie on before choosing a rule.

**Check:** $110° + 70° = 180°$ ✓ (co-interior pair). Alternate interior $= 110°$ matches the given angle ✓"""

CHK2_HE = """נתון: קווים מקבילים וחותכת, זווית אחת $= 110°$.

**(א) זווית חד-צדית פנימית (אותו צד, בין המקבילים)**

זוויות חד-צדיות פנימיות באותו צד של החותכת **משלימות**:
$$\\text{חד-צדית פנימית} = 180° - 110° = 70°$$

**(ב) זווית מתחלפת פנימית**

זוויות מתחלפות פנימיות (בין המקבילים, בצדדים מנוגדים) **שוות**:
$$\\text{מתחלפת פנימית} = 110°$$

**למה התשובות שונות:** חד-צדית פנימית ומתחלפת פנימית הן יחסים שונים — אחת מסתכמת ל-$180°$, השנייה מעתיקה את הערך. זהו תמיד באיזה צד של החותכת הזוויות לפני בחירת כלל.

**בדיקה:** $110° + 70° = 180°$ ✓ (זוג חד-צדיות). מתחלפת פנימית $= 110°$ תואמת לנתון ✓"""

METHOD_EN = """Use this table as a **decision tree** before starting any angle problem.

| Situation | Rule | What to write on the exam |
|---|---|---|
| Two angles on a straight line | Sum $= 180°$ | "$\\angle_1 + \\angle_2 = 180°$ (supplementary)" |
| Two lines cross | Vertically opposite angles equal | "$\\angle_1 = \\angle_3$ (vertically opposite)" |
| Triangle — find missing interior angle | $\\angle A + \\angle B + \\angle C = 180°$ | State the formula, substitute, solve |
| Triangle — exterior angle | $\\angle_{\\text{ext}} = \\angle A + \\angle B$ (non-adjacent) | Name the two remote interior angles |
| Parallel lines — corresponding | Equal (F-shape) | "$\\angle 1 = \\angle 5$ (corresponding)" |
| Parallel lines — alternate interior | Equal (Z-shape) | "$\\angle 3 = \\angle 6$ (alternate interior)" |
| Parallel lines — co-interior | Sum $= 180°$ (same side) | "$\\angle 3 + \\angle 5 = 180°$ (co-interior)" |
| Angles with variables | Write equation, then solve | Always show the sum rule before algebra |

**Strategy for complex diagrams:**
1. Mark all known angles with a colored pencil or clear labels.
2. Apply vertically opposite and straight-line rules at each intersection.
3. Use triangle sum wherever a triangle appears.
4. Apply parallel-line rules last to propagate values across the figure.

**When to use:** Read the problem once, identify which rows apply, then work systematically — never guess an angle without citing a rule."""

METHOD_HE = """הטבלה הזו היא **עץ החלטות** לפני כל בעיית זוויות.

| מצב | כלל | מה לכתוב בבחינה |
|---|---|---|
| שתי זוויות על קו ישר | סכום $= 180°$ | "$\\angle_1 + \\angle_2 = 180°$ (משלימות)" |
| שני קווים מצטלבים | קודקודיות שוות | "$\\angle_1 = \\angle_3$ (קודקודיות)" |
| משולש — זווית פנימית חסרה | $\\angle A + \\angle B + \\angle C = 180°$ | כתבו נוסחה, הציבו, פתרו |
| משולש — זווית חיצונית | $\\angle_{\\text{ext}} = \\angle A + \\angle B$ (לא סמוכות) | ציינו שתי הפנימיות הרחוקות |
| מקבילים — מתאימות | שוות (צורת F) | "$\\angle 1 = \\angle 5$ (מתאימות)" |
| מקבילים — מתחלפות פנימיות | שוות (צורת Z) | "$\\angle 3 = \\angle 6$ (מתחלפות)" |
| מקבילים — חד-צדיות פנימיות | סכום $= 180°$ (אותו צד) | "$\\angle 3 + \\angle 5 = 180°$ (חד-צדיות)" |
| זוויות עם משתנים | כתבו משוואה, ואז פתרו | הציגו כלל סכום לפני האלגברה |

**אסטרטגיה לדיאגרמות מורכבות:**
1. סמנו כל זווית ידועה בעיפרון צבעוני או תוויות ברורות.
2. יישמו קודקודיות וסכום על קו ישר בכל חיתוך.
3. השתמשו בסכום זוויות משולש בכל מקום שמופיע משולש.
4. יישמו כללי מקבילים אחרון להפצת ערכים על כל הציור.

**מתי להשתמש:** קראו את השאלה פעם, זהו אילו שורות חלות, ועבדו שיטתית — לעולם אל תנחשו זווית בלי לצטט כלל."""

PITFALL_EN = """**Mistake 1 — Mixing up co-interior and alternate interior angles.**
Alternate interior angles lie **between** the parallels on **opposite** sides of the transversal — they are **equal**. Co-interior angles lie between the parallels on the **same** side — they are **supplementary** (sum to $180°$). Before applying a rule, trace both angles on the diagram and note which side of the transversal each lies on.

**Mistake 2 — Using the exterior angle theorem backwards.**
The exterior angle equals the sum of the two **non-adjacent** interior angles — the ones at the other two vertices. It does **not** equal the adjacent interior angle at the same vertex. If the exterior angle is $110°$, the adjacent interior is $180° - 110° = 70°$, not $110°$.

**Mistake 3 — Forgetting the angle-sum equation when variables appear.**
If angles contain expressions like $2x$ and $x + 30°$, write the full equation ($180°$ for a triangle, $360°$ for a quadrilateral) before solving. Students who guess numeric values without setting up the equation often pick distractors that look plausible.

**Mistake 4 — Stopping after finding one angle in a parallel-line figure.**
Bagrut questions frequently ask for **all eight** angles or for a specific angle on the far intersection. Complete the top intersection first (vertically opposite + supplementary), then copy via corresponding angles."""

PITFALL_HE = """**טעות 1 — בלבול בין זוויות חד-צדיות פנימיות לזוויות מתחלפות פנימיות.**
זוויות מתחלפות פנימיות נמצאות **בין** המקבילים ב**צדדים מנוגדים** של החותכת — הן **שוות**. זוויות חד-צדיות פנימיות נמצאות בין המקבילים ב**אותו צד** — הן **משלימות** (סכום $180°$). לפני יישום כלל, עקבו אחרי שתי הזוויות על הציור ושימו לב באיזה צד של החותכת כל אחת.

**טעות 2 — שימוש במשפט הזווית החיצונית לאחור.**
הזווית החיצונית שווה לסכום שתי הזוויות הפנימיות **שאינן סמוכות** — אלה בשני הקודקודים האחרים. היא **לא** שווה לזווית הפנימית הסמוכה באותו קודקוד. אם הזווית החיצונית $110°$, הפנימית הסמוכה היא $180° - 110° = 70°$, לא $110°$.

**טעות 3 — שכחת משוואת סכום הזוויות כשמופיעים משתנים.**
אם זוויות מכילות ביטויים כמו $2x$ ו-$x + 30°$, כתבו את המשוואה המלאה ($180°$ למשולש, $360°$ למרובע) לפני הפתרון. תלמידים שניחושים ערכים בלי להקים משוואה לעיתים בוחרים מסיחים שנראים סבירים.

**טעות 4 — עצירה אחרי מציאת זווית אחת בציור עם מקבילים.**
שאלות בבגרות לעיתים מבקשות **את כל 8 הזוויות** או זווית ספציפית בחיתוך הרחוק. השלימו קודם את החיתוך העליון (קודקודיות + משלימות), ואז העתיקו דרך זוויות מתאימות."""

WHY_EN = """Geometry basics are not an isolated topic — they are the **foundation** for every subsequent geometry unit on A Step Forward and on the Bagrut exam.

**You will use this to unlock:**
- `concept:triangles_congruence` **Triangle Congruence & Similarity** (prerequisite) — proofs rely on angle rules you learn here.
- `concept:analytic_geometry` **Analytic Geometry** (prerequisite) — slope and parallel-line conditions connect directly to angle relationships.

**Why exams care:** Bagrut 3-unit geometry rewards *transfer* — applying angle rules inside composite figures that also involve algebra, isosceles triangles, or quadrilaterals. When you study, always ask: "Which of the four core rules applies here?" That habit saves time under exam pressure."""

WHY_HE = """יסודות הגאומטריה אינם נושא מבודד — הם **היסוד** לכל יחידת גאומטריה הבאה ב-A Step Forward ובבחינת הבגרות.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:triangles_congruence` **חפיפה ודמיון משולשים** (דרישת קדם) — הוכחות נשענות על כללי זוויות שתלמדו כאן.
- `concept:analytic_geometry` **גיאומטריה אנליטית** (דרישת קדם) — שיפוע ותנאי מקבילות קשורים ישירות ליחסי זוויות.

**למה בחינות אכפת:** בגיאומטריה 3 יחידות בבגרות מעריכים *העברה* — יישום כללי זוויות בציורים מורכבים שמשלבים אלגברה, משולשים שווה-שוקיים או מרובעים. בזמן לימוד, שאלו תמיד: "איזה מארבעת הכללים המרכזיים חל כאן?" ההרגל הזה חוסך זמן תחת לחץ."""

BEFORE_EN = """**Key rules — formula card:**
- Straight line: $\\angle_1 + \\angle_2 = 180°$
- Vertically opposite: equal
- Triangle sum: $\\angle A + \\angle B + \\angle C = 180°$
- Exterior angle: $\\angle_{\\text{ext}} = \\angle A + \\angle B$ (non-adjacent interiors)
- Parallel lines — corresponding $=$ equal, alternate interior $=$ equal, co-interior $= 180°$
- Quadrilateral: sum of interior angles $= 360°$

**Typical Bagrut 3-unit patterns:**
1. Find a missing angle in a triangle (2–3 marks).
2. Parallel lines — find several angles given one (3–4 marks).
3. Algebraic angle equation in a triangle or parallel-line figure (4–5 marks).

**Marking tips:** Label angles clearly on the diagram. Show which rule you used (e.g., "alternate interior → equal"). Verify with a sum check before moving on.

**Last-minute review:** Solve one triangle problem and one parallel-line problem from memory — if both pass a $180°$ check, you are ready."""

BEFORE_HE = """**כללים מרכזיים — כרטיס נוסחאות:**
- קו ישר: $\\angle_1 + \\angle_2 = 180°$
- קודקודיות: שוות
- סכום משולש: $\\angle A + \\angle B + \\angle C = 180°$
- זווית חיצונית: $\\angle_{\\text{ext}} = \\angle A + \\angle B$ (פנימיות לא סמוכות)
- מקבילים — מתאימות $=$ שוות, מתחלפות פנימיות $=$ שוות, חד-צדיות $= 180°$
- מרובע: סכום זוויות פנימיות $= 360°$

**דפוסי שאלות טיפוסיות בבגרות 3 יח':**
1. מציאת זווית חסרה במשולש (2–3 נקודות).
2. קווים מקבילים — מציאת מספר זוויות בהינתן אחת (3–4 נקודות).
3. משוואה אלגברית עם זוויות במשולש או בציור עם מקבילים (4–5 נקודות).

**טיפים לניקוד:** סמנו זוויות בבירור על הציור. הראו איזה כלל השתמשתם (למשל, "מתחלפות פנימיות → שוות"). אמתו בבדיקת סכום לפני שממשיכים.

**חזרה אחרונה:** פתרו בעיית משולש אחת ובעיית מקבילים אחת מהזיכרון — אם שתיהן עוברות בדיקת $180°$, אתם מוכנים."""

SUMMARY_EN = """- **Straight line:** adjacent angles sum to $180°$. **Vertically opposite** angles are equal.
- **Triangle:** interior angles sum to $180°$. **Exterior angle** $=$ sum of two non-adjacent interior angles.
- **Parallel lines + transversal:** corresponding equal, alternate interior equal, co-interior supplementary ($180°$).
- **Algebraic angle problems:** write the sum equation first ($180°$ or $360°$), then solve for the variable.
- **Quadrilateral:** interior angles sum to $360°$ (split into two triangles).
- **Strategy:** mark known angles → vertically opposite / straight line → triangle sum → parallel-line rules.

**Takeaway:** Name the rule before every step. On the Bagrut, reasoning earns partial credit even when a final number is wrong."""

SUMMARY_HE = """- **קו ישר:** זוויות סמוכות מסתכמות ל-$180°$. **קודקודיות** שוות.
- **משולש:** זוויות פנימיות מסתכמות ל-$180°$. **זווית חיצונית** $=$ סכום שתי פנימיות לא סמוכות.
- **מקבילים + חותכת:** מתאימות שוות, מתחלפות פנימיות שוות, חד-צדיות משלימות ($180°$).
- **בעיות אלגבריות:** כתבו קודם משוואת סכום ($180°$ או $360°$), ואז פתרו למשתנה.
- **מרובע:** זוויות פנימיות מסתכמות ל-$360°$ (פיצול לשני משולשים).
- **אסטרטגיה:** סמנו ידועות → קודקודיות / קו ישר → סכום משולש → כללי מקבילים.

**מסקנה:** ציינו את הכלל לפני כל צעד. בבגרות, הנימוק מזכה בניקוד חלקי גם כשהמספר הסופי שגוי."""

EXPLS = {
    1: fmt_expl(
        "The third angle is $180° - 45° - 90° = 45°$. With angles $45°$, $90°$, and $45°$, the triangle has one right angle and two equal acute angles — it is a **right-angled isosceles** triangle.",
        "Start with the triangle angle-sum rule: all three interior angles must total $180°$. Subtract the two givens. Then compare the three results: a $90°$ angle means 'right-angled'; two equal sides' opposite angles ($45°$ each) mean 'isosceles.'",
        "Finding $45°$ but forgetting to classify, or calling it 'equilateral' because two angles match. Equilateral requires all three equal ($60°$ each).",
        "Bagrut short-answer items often require both the numeric angle and the triangle name — write both on the answer line to avoid losing a mark.",
        "הזווית השלישית: $180° - 45° - 90° = 45°$. עם זוויות $45°$, $90°$ ו-$45°$, יש זווית ישרה אחת ושתי חדות שוות — **משולש ישר-זוויתי שווה-שוקיים**.",
        "התחילו בכלל סכום זוויות המשולש: שלוש הפנימיות חייבות להסתכם ל-$180°$. חסרו את שתי הנתונים. השוו את שלוש התוצאות: $90°$ = ישר-זוויתי; שתי זוויות שוות ($45°$) = שווה-שוקיים.",
        "מציאת $45°$ בלי סיווג, או קריאה 'שווה-צלעות' כי שתי זוויות שוות. שווה-צלעות דורש שלוש שוות ($60°$ כל אחת).",
        "בשאלות תשובה קצרה בבגרות לעיתים נדרש גם המספר וגם שם המשולש — כתבו את שניהם בשורת התשובה.",
    ),
    2: fmt_expl(
        "Angles on a straight line sum to $180°$: $3x + (x + 20°) = 180°$, so $4x + 20 = 180$, $4x = 160$, $x = 40$. The angles are $3(40) = 120°$ and $40 + 20 = 60°$. Check: $120° + 60° = 180°$ ✓",
        "When angles on a line contain variables, write one equation using the $180°$ rule before any arithmetic. Collect like terms ($3x + x = 4x$), isolate $x$, then substitute back into **both** original expressions.",
        "Getting $x = 40$ but reporting only one angle, or arithmetic error: $4x = 140$ instead of $160$. Always verify both angles sum to $180°$.",
        "Show the equation $3x + x + 20 = 180$ explicitly — graders award marks for setup even if the final $x$ has a minor slip.",
        "זוויות על קו ישר מסתכמות ל-$180°$: $3x + (x + 20°) = 180°$, כלומר $4x + 20 = 180$, $4x = 160$, $x = 40$. הזוויות: $3(40) = 120°$ ו-$40 + 20 = 60°$. בדיקה: $120° + 60° = 180°$ ✓",
        "כשזוויות על קו מכילות משתנים, כתבו משוואה אחת לפי כלל $180°$ לפני חישוב. אספו איברים דומים ($3x + x = 4x$), בודדו $x$, והציבו חזרה ב**שני** הביטויים המקוריים.",
        "מציאת $x = 40$ בלי לדווח על שתי הזוויות, או שגיאה: $4x = 140$ במקום $160$. תמיד וודאו שהסכום $180°$.",
        "הציגו במפורש $3x + x + 20 = 180$ — בודקים נותנים נקודות על ההקמה גם אם $x$ הסופי טעה במעט.",
    ),
    3: fmt_expl(
        "When two lines cross, vertically opposite angles are equal ($130°$ opposite $130°$) and adjacent angles on a straight line are supplementary ($180° - 130° = 50°$). The four angles are $130°, 50°, 130°, 50°$.",
        "At any intersection of two lines, you always get two distinct values that alternate: one obtuse, one acute (unless all are $90°$). Find the supplement first, then copy via vertically opposite.",
        "Reporting three different values, or giving $130°, 130°, 130°$ by treating all angles as vertically opposite to the first.",
        "Sketch the crossing lines and label one angle before computing — visual structure prevents mixing adjacent and opposite pairs.",
        "כששני קווים מצטלבים, קודקודיות שוות ($130°$ מול $130°$) וסמוכות על קו ישר משלימות ($180° - 130° = 50°$). ארבע הזוויות: $130°, 50°, 130°, 50°$.",
        "בכל חיתוך של שני קווים מתקבלות שתי ערכים מתחלפים: קהה וחדה (אלא אם כולן $90°$). מצאו קודם את המשלימה, ואז העתיקו בקודקודיות.",
        "דיווח על שלוש ערכים שונים, או $130°, 130°, 130°$ מתייחס לכל הזוויות כקודקודיות.",
        "שרטטו קווים מצטלבים וסמנו זווית אחת לפני חישוב — מבנה ויזואלי מונע בלבול בין סמוכות לנגדיות.",
    ),
    4: fmt_expl(
        "By the exterior angle theorem, the two non-adjacent interior angles sum to $110°$. One is $50°$, so the other is $110° - 50° = 60°$. The adjacent interior angle at the vertex is $180° - 110° = 70°$ (supplementary to the exterior angle).",
        "Split the problem: (1) use exterior angle theorem for the two remote interiors; (2) use straight-line supplementary rule for the angle at the vertex where the exterior angle sits.",
        "Using $110°$ as the adjacent interior angle instead of $70°$, or subtracting $50°$ from $180°$ instead of from $110°$.",
        "Draw the triangle with the side extended — mark which angle is exterior and which two interiors are 'remote.' The theorem never uses the adjacent interior.",
        "לפי משפט הזווית החיצונית, שתי הפנימיות הלא-סמוכות מסתכמות ל-$110°$. אחת $50°$, לכן השנייה $110° - 50° = 60°$. הפנימית הסמוכה בקודקוד: $180° - 110° = 70°$ (משלימה לחיצונית).",
        "פצלו: (1) משפט זווית חיצונית לשתי הרחוקות; (2) כלל משלימות על קו ישר לזווית בקודקוד שבו יושבת החיצונית.",
        "שימוש ב-$110°$ כפנימית סמוכה במקום $70°$, או חיסור $50°$ מ-$180°$ במקום מ-$110°$.",
        "שרטטו משולש עם צלע מוארכת — סמנו איזו זווית חיצונית ואילו שתי פנימיות 'רחוקות'. המשפט לא משתמש בפנימית הסמוכה.",
    ),
    5: fmt_expl(
        "Given one angle $72°$, vertically opposite and supplementary rules at the top intersection give $72°$ and $108°$. Corresponding angles copy these to the bottom intersection. Result: four angles of $72°$ (acute) and four of $108°$ (obtuse).",
        "In any parallel-line figure, only **two** distinct angle values appear — one acute, one obtuse. Find both at one intersection, then propagate via corresponding (or alternate interior) angles.",
        "Listing six different values, or forgetting that vertically opposite duplicates each value (four of each type, not two).",
        "Write 'acute: 72° (×4), obtuse: 108° (×4)' rather than listing all eight with possible labeling errors — the pattern matters more than individual numbers.",
        "נתונה זווית $72°$; קודקודיות ומשלימות בחיתוך העליון נותנות $72°$ ו-$108°$. זוויות מתאימות מעתיקות לחיתוך התחתון. תוצאה: ארבע $72°$ (חדות) וארבע $108°$ (קהות).",
        "בכל ציור עם מקבילים מופיעים רק **שני** ערכים — חד וקהה. מצאו שניהם בחיתוך אחד, והפיצו בזוויות מתאימות (או מתחלפות פנימיות).",
        "רשימת שישה ערכים שונים, או שכחה שקודקודיות מכפילה כל ערך (ארבע מכל סוג, לא שתיים).",
        "כתבו 'חדות: 72° (×4), קהות: 108° (×4)' במקום לרשום שמונה עם טעויות סימון — הדפוס חשוב יותר מהמספרים.",
    ),
    6: fmt_expl(
        "Triangle sum: $2x + (x + 30°) + (x - 10°) = 180°$, so $4x + 20 = 180$, $4x = 160$, $x = 40$. Angles: $P = 80°$, $Q = 70°$, $R = 30°$. Check: $80 + 70 + 30 = 180°$ ✓",
        "Write all three angle expressions on the left side of $= 180°$ before simplifying. Combine like terms carefully: $2x + x + x = 4x$, and $30 - 10 = 20$.",
        "Sign error on $(x - 10°)$ becoming $+10$, yielding $x = 30$ and wrong angles. Or finding $x$ but not substituting into all three expressions.",
        "After solving, always substitute $x$ back into **each** angle formula and verify the sum — one arithmetic check catches most errors.",
        "סכום משולש: $2x + (x + 30°) + (x - 10°) = 180°$, כלומר $4x + 20 = 180$, $4x = 160$, $x = 40$. זוויות: $P = 80°$, $Q = 70°$, $R = 30°$. בדיקה: $80 + 70 + 30 = 180°$ ✓",
        "כתבו את שלוש הביטויים בצד שמאל של $= 180°$ לפני פישוט. אספו בזהירות: $2x + x + x = 4x$, ו-$30 - 10 = 20$.",
        "שגיאת סימן ב-$(x - 10°)$ הופכת ל-$+10$, ו-$x = 30$ עם זוויות שגויות. או מציאת $x$ בלי הצבה בכל שלוש הנוסחאות.",
        "אחרי הפתרון, הציבו $x$ ב**כל** נוסחת זווית ואמתו סכום — בדיקה אחת תופסת רוב השגיאות.",
    ),
    7: fmt_expl(
        "Co-interior angles on the same side of a transversal are supplementary: $(3x + 10) + (2x - 5) = 180$. So $5x + 5 = 180$, $5x = 175$, $x = 35$. Angles: $3(35) + 10 = 115°$ and $2(35) - 5 = 65°$. Check: $115 + 65 = 180°$ ✓",
        "Identify the relationship first — 'co-interior' means **sum to 180°**, not equal. Set up one addition equation, solve for $x$, then evaluate both expressions.",
        "Setting the angles **equal** ($3x + 10 = 2x - 5$) as if they were alternate interior — a very common Bagrut trap when the question says 'co-interior.'",
        "Underline the words 'co-interior' or 'same side' in the stem before writing any equation — the relationship word determines whether you add to $180°$ or set equal.",
        "זוויות חד-צדיות פנימיות באותו צד **משלימות**: $(3x + 10) + (2x - 5) = 180$. כלומר $5x + 5 = 180$, $5x = 175$, $x = 35$. זוויות: $115°$ ו-$65°$. בדיקה: $115 + 65 = 180°$ ✓",
        "זהו קודם את היחס — 'חד-צדיות' פירושו **סכום $180°$**, לא שוויון. הקימו משוואת חיבור, פתרו $x$, והעריכו שני הביטויים.",
        "השוואת הזוויות (**שוות**) כאילו מתחלפות פנימיות — מלכודת נפוצה בבגרות כשכתוב 'חד-צדיות'.",
        "הדגישו 'חד-צדיות' או 'אותו צד' בניסוח לפני כתיבת משוואה — מילת היחס קובעת חיבור ל-$180°$ או השוואה.",
    ),
    8: fmt_expl(
        "In an isosceles triangle, the two base angles are equal. Both base angles $= 55°$. Apex angle $= 180° - 55° - 55° = 70°$. All three angles: $55°, 55°, 70°$.",
        "Identify which angle is given: base or apex. If a **base** angle is given, copy it to the other base angle, then subtract both from $180°$. If the apex is given, subtract twice the base from $180°$.",
        "Using $180 - 55 = 125°$ for the apex (subtracting only once), or assuming all angles equal because the triangle is 'isosceles.'",
        "Sketch the triangle with equal sides marked (hash marks) — visual symmetry confirms which two angles must match before you calculate.",
        "במשולש שווה-שוקיים, שתי זוויות הבסיס שוות. שתיהן $= 55°$. זווית קודקוד $= 180° - 55° - 55° = 70°$. כל הזוויות: $55°, 55°, 70°$.",
        "זהו איזו זווית נתונה: בסיס או קודקוד. אם **בסיס** נתון, העתיקו לבסיס השני, וחסרו שניהם מ-$180°$. אם קודקוד נתון, חסרו פעמיים בסיס.",
        "שימוש ב-$180 - 55 = 125°$ לקודקוד (חיסור פעם אחת בלבד), או הנחה שכל הזוויות שוות כי 'שווה-שוקיים'.",
        "שרטטו משולש עם סימון צלעות שוות — סימטריה ויזואלית מאשרת אילו שתי זוויות חייבות להיות שוות לפני החישוב.",
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
            if "triangle" in sec.get("body_en_md", "").lower():
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
