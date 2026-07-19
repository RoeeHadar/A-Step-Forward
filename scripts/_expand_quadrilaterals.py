#!/usr/bin/env python3
"""Expand quadrilaterals.json per .cursor/skills/expand-lessons-cursor/SKILL.md."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/quadrilaterals.json"

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
        "body_en_md": """A **quadrilateral** is any polygon with exactly four sides. In Israeli high-school geometry (Bagrut 4–5 units), quadrilaterals are a central topic because they combine **classification**, **proof technique**, and **area computation** in a single family of shapes.

The types form a **hierarchy** — not every parallelogram is a rectangle, but every rectangle is a parallelogram. Two independent chains meet at the square:

**Hierarchy (most specific → most general):**
Square → Rectangle → Parallelogram → General Quadrilateral
Square → Rhombus → Parallelogram → General Quadrilateral

**What this lesson covers:**
- Properties of parallelogram, rhombus, rectangle, square, trapezoid, and kite
- Five sufficient conditions to prove a parallelogram (any one suffices)
- Area formulas and the trapezoid **midline theorem**
- Proof strategies using congruent triangles (SAS, ASA, SSS)
- The angle-sum theorem: interior angles of any quadrilateral total $360°$

**Exam relevance:** Bagrut geometry frequently asks you to classify a shape, prove it belongs to a special type, or compute area using the correct formula. Master the hierarchy first — it tells you which properties you may assume.""",
        "body_he_md": """**מרובע** הוא מצולע עם בדיוק ארבע צלעות. בגיאומטריה של תיכון (בגרות 4–5 יחידות), מרובעים הם נושא מרכזי כי הם משלבים **סיווג**, **טכניקת הוכחה** ו**חישוב שטח** במשפחת צורות אחת.

הסוגים מהווים **היררכיה** — לא כל מקבילית היא מלבן, אבל כל מלבן הוא מקבילית. שני שרשrals נפגשים בריבוע:

**היררכיה (ספציפי → כללי):**
ריבוע → מלבן → מקבילית → מרובע כללי
ריבוע → מעויין → מקבילית → מרובע כללי

**מה השיעור מכסה:**
- תכונות מקבילית, מעויין, מלבן, ריבוע, טרפז ודלתון
- חמישה תנאים מספיקים להוכחת מקבילית (כל אחד מספיק)
- נוסחאות שטח ו**משפט קו האמצע** בטרפז
- אסטרategיות הוכחה עם משולשים חופפים (זצ"ז, ז"ז"ז, צ"צ"צ)
- משפט סכום זוויות: זוויות פנימיות בכל מרובע = $360°$

**רלוונטיות לבחינה:** בבגרות מבקשים לסווג צורה, להוכיח שהיא מסוג מיוחד, או לחשב שטח. שלטו בהיררכיה קודם — היא אומרת אילו תכונות מותר להניח.""",
    },
    "definition": {
        "body_en_md": """Each special quadrilateral has defining properties. Use this table as a reference during proofs and area problems. Remember: a property listed for a **more specific** shape also holds for shapes above it in the hierarchy (e.g., a square has all rectangle properties).

| Shape | Defining properties |
|---|---|
| **Parallelogram** | Opposite sides parallel and equal; opposite angles equal; consecutive angles supplementary; diagonals bisect each other |
| **Rhombus** | All four sides equal; diagonals bisect each other at right angles; each diagonal bisects the vertex angles |
| **Rectangle** | All four angles are $90°$; diagonals are equal in length and bisect each other |
| **Square** | All sides equal **and** all angles $90°$; diagonals equal, perpendicular, and bisect vertex angles |
| **Trapezoid** | Exactly one pair of parallel sides (the **bases**); isosceles trapezoid: the two non-parallel legs are equal |
| **Kite** | Two pairs of consecutive equal sides; one diagonal is the perpendicular bisector of the other |

**Five sufficient conditions for a parallelogram** (proving any one is enough):
1. Both pairs of opposite sides are equal
2. Both pairs of opposite sides are parallel
3. One pair of opposite sides is both parallel **and** equal
4. The diagonals bisect each other
5. Both pairs of opposite angles are equal

**Angle rules in any parallelogram:** Opposite angles are equal; consecutive angles sum to $180°$. The sum of all four interior angles in **any** quadrilateral is always $360°$.""",
        "body_he_md": """לכל מרובע מיוחד יש תכונות מגדירות. השתמשו בטבלה הזו בזמן הוכחות ובעיות שטח. זכרו: תכונה של צורה **ספציפית** נכונה גם לצורות מעליה בהיררכיה (למשל, לריבוע כל תכונות המלבן).

| צורה | תכונות מגדירות |
|---|---|
| **מקבילית** | צלעות נגדיות מקבילות ושוות; זוויות נגדיות שוות; זוויות עוקבות משלימות; אלכסונים מחצים זה את זה |
| **מעויין** | ארבע צלעות שוות; אלכסונים מאונכים ומחצים; כל אלכסון מחלק זוויות קודקוד |
| **מלבן** | ארבע זוויות ישרות ($90°$); אלכסונים שווים באורך ומחצים |
| **ריבוע** | כל הצלעות שוות **וגם** כל הזוויות $90°$; אלכסונים שווים, מאונכים ומחלקים זוויות |
| **טרפז** | זוג אחד בלבד של צלעות מקבילות (**בסיסים**); טרפז שווה-שוקיים: שתי השוקיים שוות |
| **דלתון** | שני זוגות של צלעות עוקבות שוות; אלכסון אחד מאונך ומחצה את השני |

**חמישה תנאים מספיקים למקבילית** (הוכחת אחד מהם מספיקה):
1. שני זוגות צלעות נגדיות שוות
2. שני זוגות צלעות נגדיות מקבילות
3. זוג אחד — מקביל **וגם** שווה
4. האלכסונים מחצים זה את זה
5. שני זוגות זוויות נגדיות שוות

**כללי זוויות במקבילית:** נגדיות שוות; עוקבות מסתכמות ל-$180°$. סכום ארבע הזוויות ב**כל** מרובע = $360°$.""",
    },
    "theory": {
        "body_en_md": """### Area formulas

Each quadrilateral type has its own area formula. Pick the one that matches the givens in the problem — do not use rhombus diagonal formula on a general parallelogram unless you know the diagonals.

| Shape | Area formula | Notes |
|---|---|---|
| Parallelogram | $A = b \\times h$ | $h$ is **perpendicular** height, not a slanted side |
| Rectangle | $A = l \\times w$ | Special case of parallelogram |
| Square | $A = s^2$ | Side squared |
| Rhombus | $A = \\dfrac{d_1 \\times d_2}{2}$ | Uses diagonals; also $A = bh$ if base and height known |
| Trapezoid | $A = \\dfrac{a+b}{2} \\times h$ | $a,b$ are parallel bases; $h$ is perpendicular distance between them |

### Midline theorem (trapezoid)

The segment connecting the midpoints of the two **legs** of a trapezoid is parallel to the bases and equals their average:
$$MN = \\frac{a + b}{2}$$
This midline length equals the trapezoid's "average base," which is why the area formula $\\frac{a+b}{2} \\times h$ works.

### Midline theorem (triangle — used in Varignon proofs)

In any triangle, the segment connecting midpoints of two sides is parallel to the third side and equals half its length:
$$MN = \\frac{c}{2}$$

### Angle-sum theorem

Draw one diagonal to split any quadrilateral into two triangles. Each triangle contributes $180°$, so:
$$\\angle A + \\angle B + \\angle C + \\angle D = 360°$$
This holds for **every** quadrilateral, not just parallelograms.""",
        "body_he_md": """### נוסחאות שטח

לכל סוג מרובע נוסחת שטח משלו. בחרו את הנוסחה שמתאימה לנתונים — אל תשתמשו בנוסחת אלכסוני מעויין על מקבילית כללית אלא אם האלכסונים ידועים.

| צורה | נוסחת שטח | הערות |
|---|---|---|
| מקבילית | $A = b \\times h$ | $h$ הוא גובה **ניצב**, לא צלע אלכסונית |
| מלבן | $A = l \\times w$ | מקרה מיוחד של מקבילית |
| ריבוע | $A = s^2$ | ריבוע הצלע |
| מעויין | $A = \\dfrac{d_1 \\times d_2}{2}$ | אלכסונים; גם $A = bh$ אם בסיס וגובה ידועים |
| טרפז | $A = \\dfrac{a+b}{2} \\times h$ | $a,b$ בסיסים מקבילים; $h$ מרחק ניצב ביניהם |

### משפט קו האמצע (טרפז)

הקטע המחבר אמצעי שתי **השוקיים** של טרפז מקביל לבסיסים ושווה לממוצע שלהם:
$$MN = \\frac{a + b}{2}$$
אורך קו האמצע שווה ל"בסיס הממוצע" של הטרפז — ולכן נוסחת השטח $\\frac{a+b}{2} \\times h$ עובדת.

### משפט קו האמצע (משולש — להוכחות וריניון)

בכל משולש, הקטע בין אמצעי שתי צלעות מקביל לצלע השלישית ושווה לחציה:
$$MN = \\frac{c}{2}$$

### משפט סכום זוויות

שרטטו אלכסון אחד — המרובע מתפצל לשני משולשים. כל משולש תורם $180°$:
$$\\angle A + \\angle B + \\angle C + \\angle D = 360°$$
זה נכון ל**כל** מרובע, לא רק למקבילית.""",
    },
    "worked_example_1": {
        "body_en_md": """**Given:** Parallelogram ABCD with $AB = 5$, $BC = 8$, and $\\angle A = 60°$. Find:
(a) $CD$, $AD$
(b) $\\angle B$, $\\angle C$, $\\angle D$

### Move 1: Use opposite-side equality (parallelogram property)
In any parallelogram, opposite sides are equal:
$$CD = AB = 5, \\qquad AD = BC = 8$$

### Move 2: Opposite angles are equal
$\\angle C$ is opposite $\\angle A$, so:
$$\\angle C = \\angle A = 60°$$

### Move 3: Consecutive angles are supplementary
Adjacent angles in a parallelogram sum to $180°$:
$$\\angle B = 180° - 60° = 120°, \\qquad \\angle D = 180° - 60° = 120°$$

### Move 4: Verify the angle sum
$60° + 120° + 60° + 120° = 360°$ ✓ — consistent with the quadrilateral angle-sum theorem.

**Why this method:** Once you identify a parallelogram, you never need extra givens for side and angle relations — the defining properties do the work. On the Bagrut, side-length questions often give only two adjacent sides; opposite sides follow automatically.

**Exam tip:** Sketch ABCD with labeled vertices before computing. Mislabeling which angles are opposite causes most errors in this type of problem.

**Answer:** (a) $CD = 5$, $AD = 8$; (b) $\\angle B = \\angle D = 120°$, $\\angle C = 60°$.""",
        "body_he_md": """**נתון:** מקבילית ABCD עם $AB = 5$, $BC = 8$, $\\angle A = 60°$. מצאו:
(א) $CD$, $AD$
(ב) $\\angle B$, $\\angle C$, $\\angle D$

### צעד 1: שוויון צלעות נגדיות
בכל מקבילית, צלעות נגדיות שוות:
$$CD = AB = 5, \\qquad AD = BC = 8$$

### צעד 2: זוויות נגדיות שוות
$\\angle C$ נגדית ל-$\\angle A$:
$$\\angle C = \\angle A = 60°$$

### צעד 3: זוויות עוקבות משלימות
זוויות סמוכות במקבילית מסתכמות ל-$180°$:
$$\\angle B = 180° - 60° = 120°, \\qquad \\angle D = 180° - 60° = 120°$$

### צעד 4: אימות סכום זוויות
$60° + 120° + 60° + 120° = 360°$ ✓ — עקבי עם משפט סכום הזוויות.

**למה השיטה:** ברגע שזיהיתם מקבילית, אין צורך בנתונים נוספים — התכונות המגדירות עושות את העבודה. בבגרות, שאלות אורך צלעות לעיתים נותנות רק שתי צלעות סמוכות; הנגדיות נגזרות אוטומטית.

**טיפ לבחינה:** שרטטו ABCD עם קודקודים מסומנים לפני החישוב. סימון שגוי של נגדיות גורם לרוב הטעויות.

**תשובה:** (א) $CD = 5$, $AD = 8$; (ב) $\\angle B = \\angle D = 120°$, $\\angle C = 60°$.""",
    },
    "worked_example_2": {
        "body_en_md": """**Given:** In quadrilateral ABCD, $AB \\parallel CD$ and $AB = CD$. **Prove:** ABCD is a parallelogram.

### Move 1: Choose the right sufficient condition
Condition 3 applies directly: one pair of opposite sides is both parallel and equal. We will confirm this by showing the other pair is also parallel and equal.

### Move 2: Draw diagonal AC and set up congruent triangles
Consider $\\triangle ABC$ and $\\triangle CDA$:
- $AB = CD$ (given)
- $\\angle BAC = \\angle DCA$ (alternate interior angles, since $AB \\parallel CD$)
- $AC = AC$ (common side)

### Move 3: Apply SAS congruence
By SAS: $\\triangle ABC \\cong \\triangle CDA$.

### Move 4: Read off the remaining equalities
From congruence:
- $BC = AD$ (corresponding sides)
- $\\angle BCA = \\angle DAC$ (corresponding angles), so $BC \\parallel AD$

Both pairs of opposite sides are equal (and parallel) → ABCD is a parallelogram. ∎

**Exam tip:** When one pair is parallel and equal, diagonal AC almost always creates the SAS pair you need. State every reason (alternate interior, common side, SAS).""",
        "body_he_md": """**נתון:** במרובע ABCD, $AB \\parallel CD$ ו-$AB = CD$. **להוכיח:** ABCD מקבילית.

### צעד 1: בחירת תנאי מספיק
תנאי 3 חל ישירות: זוג אחד של צלעות נגדיות מקביל ושווה. נאשר שהזוג השני גם מקביל ושווה.

### צעד 2: שרטוט אלכסון AC והכנת משולשים חופפים
שקלו $\\triangle ABC$ ו-$\\triangle CDA$:
- $AB = CD$ (נתון)
- $\\angle BAC = \\angle DCA$ (זוויות מתחלפות, כי $AB \\parallel CD$)
- $AC = AC$ (צלע משותפת)

### צעד 3: יישום חפיפה זצ"ז
לפי זצ"ז: $\\triangle ABC \\cong \\triangle CDA$.

### צעד 4: קריאת השוויונות
מחפיפה:
- $BC = AD$ (צלעות מתאימות)
- $\\angle BCA = \\angle DAC$ (זוויות מתאימות), לכן $BC \\parallel AD$

שני זוגות צלעות נגדיות שוות (ומקבילות) → ABCD מקבילית. ■

**טיפ לבחינה:** כשזוג אחד מקביל ושווה, אלכסון AC כמעט תמיד יוצר את זוג הזצ"ז. ציינו כל נימוק (מתחלפות, משותף, זצ"ז).""",
    },
    "worked_example_3": {
        "body_en_md": """**Given:** Trapezoid ABCD with $AB \\parallel CD$, $AB = 18$, $CD = 10$. M is the midpoint of AD; N is the midpoint of BC.

**(a) Find MN.**

### Move 1: Apply the trapezoid midline theorem
$$MN = \\frac{AB + CD}{2} = \\frac{18 + 10}{2} = 14$$

**(b) If the height is $h = 6$, find the area.**

### Move 2: Trapezoid area formula
$$A = \\frac{AB + CD}{2} \\times h = 14 \\times 6 = 84$$

Notice that the midline length (14) times height gives the area directly — this is not a coincidence.

**(c) M₁N₁ is the midline of the upper half (between CD and MN). Find M₁N₁.**

### Move 3: Apply midline theorem again on the smaller trapezoid
The upper trapezoid has bases $CD = 10$ and $MN = 14$:
$$M_1N_1 = \\frac{CD + MN}{2} = \\frac{10 + 14}{2} = 12$$

**Why this works:** Each time you take a midline, you average the two parallel sides of that trapezoid layer.

**Answer:** (a) $MN = 14$; (b) $A = 84$; (c) $M_1N_1 = 12$.""",
        "body_he_md": """**נתון:** טרפז ABCD עם $AB \\parallel CD$, $AB = 18$, $CD = 10$. M אמצע AD; N אמצע BC.

**(א) מצאו MN.**

### צעד 1: משפט קו האמצע בטרפז
$$MN = \\frac{AB + CD}{2} = \\frac{18 + 10}{2} = 14$$

**(ב) אם הגובה $h = 6$, מצאו שטח.**

### צעד 2: נוסחת שטח טרפז
$$A = \\frac{AB + CD}{2} \\times h = 14 \\times 6 = 84$$

שימו לב: אורך קו האמצע (14) כפול גובה = שטח — זו לא צירוף מקרים.

**(ג) M₁N₁ הוא קו האמצע של החצי העליון (בין CD ל-MN). מצאו M₁N₁.**

### צעד 3: משפט קו האמצע שוב על הטרפז הקטן
לטרפז העליון בסיסים $CD = 10$ ו-$MN = 14$:
$$M_1N_1 = \\frac{CD + MN}{2} = \\frac{10 + 14}{2} = 12$$

**למה זה עובד:** בכל פעם שמחשבים קו אמצע, ממצעים את שני הצלעות המקבילות של שכבת הטרפז.

**תשובה:** (א) $MN = 14$; (ב) $A = 84$; (ג) $M_1N_1 = 12$.""",
    },
    "method_guide": {
        "body_en_md": """Use this table as a **decision tree** before starting any quadrilateral problem.

| Task | Approach | Key theorem |
|---|---|---|
| Prove parallelogram | Pick one of 5 sufficient conditions; use congruent triangles | SAS on triangles sharing a diagonal |
| Prove rhombus | Show all 4 sides equal, or parallelogram + adjacent sides equal | Distance formula or congruence |
| Prove rectangle | Parallelogram + one right angle, **or** parallelogram + equal diagonals | Right angle propagates to all four |
| Find angle in parallelogram | Opposite = equal; consecutive = supplementary ($180°$) | No calculation needed beyond $180° - \\theta$ |
| Area of parallelogram | $A = b \\times h$ (perpendicular height!) | Do not confuse slant side with height |
| Area of rhombus | $A = d_1 d_2 / 2$ when diagonals given | Diagonals must be perpendicular (always true in rhombus) |
| Area of trapezoid | $A = (a+b)/2 \\times h$ | $a,b$ are the **parallel** sides only |
| Midline length | Average of the two parallel bases | Works for trapezoids, not arbitrary quadrilaterals |
| Angle sum | Split by diagonal → two triangles → $360°$ | Holds for every quadrilateral |

**When to use:** Read the problem once, name the shape type, then open the matching row. If the problem says "prove," identify which sufficient condition fits the givens before writing anything.""",
        "body_he_md": """הטבלה הזו היא **עץ החלטות** לפני כל בעיית מרובע.

| משימה | גישה | משפט מפתח |
|---|---|---|
| הוכח מקבילית | בחרו אחד מ-5 תנאים; משולשים חופפים | זצ"ז על משולשים עם אלכסון משותף |
| הוכח מעויין | 4 צלעות שוות, או מקבילית + צלעות סמוכות שוות | נוסחת מרחק או חפיפה |
| הוכח מלבן | מקבילית + זווית ישרה, **או** מקבילית + אלכסונים שווים | זווית ישרה מתפשטת לכל ארבע |
| זווית במקבילית | נגדיות = שוות; עוקבות = משלימות ($180°$) | $180° - \\theta$ בלבד |
| שטח מקבילית | $A = b \\times h$ (גובה ניצב!) | אל תבלבלו צלע אלכסונית עם גובה |
| שטח מעויין | $A = d_1 d_2 / 2$ כשאלכסונים נתונים | אלכסונים תמיד מאונכים במעויין |
| שטח טרפז | $A = (a+b)/2 \\times h$ | $a,b$ הם הצלעות **המקבילות** בלבד |
| אורך קו אמצע | ממוצע שני הבסיסים המקבילים | לטרפזים, לא לכל מרובע |
| סכום זוויות | פיצול באלכסון → שני משולשים → $360°$ | נכון לכל מרובע |

**מתי להשתמש:** קראו את השאלה, זהו את סוג הצורה, ופתחו את השורה המתאימה. אם כתוב "הוכיח" — זהו איזה תנאי מספיק מתאים לנתונים לפני שכותבים.""",
    },
    "pitfall": {
        "body_en_md": """1. **Reversing the hierarchy.** Not every parallelogram is a rectangle — you need all four angles to be $90°$. But every rectangle **is** a parallelogram, so you may use parallelogram properties on a rectangle.

2. **Rhombus ≠ square.** A rhombus has equal sides but not necessarily right angles. Only when a rhombus also has one right angle does it become a square.

3. **Confusing area formulas.** Rhombus with diagonals: $A = d_1 d_2 / 2$. General parallelogram: $A = b \\times h$. Using the wrong formula gives a wrong answer even if arithmetic is correct.

4. **Midline theorem scope.** In a trapezoid, midline = average of **parallel bases**. In a triangle, midline = half the third side. Do not apply the trapezoid formula to a general quadrilateral.

5. **Proofs without reasons.** On the Bagrut, every logical step needs a stated reason (alternate interior angles, SAS, definition of parallelogram). A correct conclusion with missing justifications loses most of the points.""",
        "body_he_md": """1. **היפוך ההיררכיה.** לא כל מקבילית היא מלבן — צריך ארבע זוויות ישרות. אבל כל מלבן **הוא** מקבילית, ולכן מותר להשתמש בתכונות מקבילית על מלבן.

2. **מעויין ≠ ריבוע.** למעויין צלעות שוות אבל לא בהכרח זוויות ישרות. רק כשלמעויין יש גם זווית ישרה אחת — הוא הופך לריבוע.

3. **בלבול נוסחאות שטח.** מעויין עם אלכסונים: $A = d_1 d_2 / 2$. מקבילית כללית: $A = b \\times h$. נוסחה שגויה = תשובה שגויה גם אם החשבון נכון.

4. **היקף משפט קו האמצע.** בטרפז, קו אמצע = ממוצע **הבסיסים המקבילים**. במשולש, קו אמצע = חצי הצלע השלישית. אל תיישמו נוסחת טרפז על מרובע כללי.

5. **הוכחות בלי נימוקים.** בבגרות, כל שלב לוגי דורש נימוק (זוויות מתחלפות, זצ"ז, הגדרת מקבילית). מסקנה נכונה בלי נימוקים — מאבדת רוב הנקודות.""",
    },
    "why_matters": {
        "body_en_md": """Quadrilateral geometry sits at the crossroads of several topics in the knowledge graph. Proving a parallelogram relies on **triangle congruence** (`concept:triangles_congruence`) — the same SAS and ASA tools you use throughout Euclidean geometry. Area formulas connect directly to **area and perimeter** (`concept:geometry_area_perimeter`) and appear in composite-figure problems on the Bagrut.

The midline theorem bridges quadrilaterals and **triangles**: Varignon's theorem (midpoints of a parallelogram's sides form a parallelogram) is proved entirely with triangle midlines. In coordinate geometry (`concept:analytic_geometry`), you verify "is this a parallelogram?" by checking opposite sides have equal slope and length.

**Why it matters for exams:** Bagrut 4–5 unit geometry often chains a proof (show ABCD is a parallelogram) with a follow-up calculation (find area or angle). Recognizing which sufficient condition to use saves minutes under time pressure.""",
        "body_he_md": """גיאומטריית מרובעים נמצאת בצומת של כמה נושאים. הוכחת מקבילית מסתמכת על **חפיפת משולשים** (`concept:triangles_congruence`) — אותם כלי זצ"ז וז"ז"ז בכל הגיאומטריה האוקלידית. נוסחאות שטח מתחברות ל**שטח והיקף** (`concept:geometry_area_perimeter`) ומופיעות בצורות מורכבות בבגרות.

משפט קו האמצע מגשר בין מרובעים ל**משולשים**: משפט וריניון (אמצעי צלעות מקבילית יוצרים מקבילית) מוכח כולו עם קווי אמצע במשולשים. בגיאומטריה אנליטית (`concept:analytic_geometry`), בודקים "האם זו מקבילית?" לפי שיפוע ואורך של צלעות נגדיות.

**למה זה חשוב לבחינות:** בבגרות 4–5 יחידות, שאלות גיאומטריה לעיתים משלבות הוכחה (הראה ש-ABCD מקבילית) עם חישוב (מצא שטח או זווית). זיהוי התנאי המספיק הנכון חוסך דקות בלחץ זמן.""",
    },
    "before_exam": {
        "body_en_md": """**Quick reference checklist:**

- **Parallelogram:** 5 sufficient conditions (any one proves it)
- **Rhombus:** 4 equal sides; diagonals perpendicular (not necessarily equal!)
- **Rectangle:** parallelogram + one right angle, or equal diagonals
- **Square:** rectangle + equal sides (or rhombus + right angle)
- **Trapezoid area:** $A = (a+b)h/2$
- **Rhombus area:** $A = d_1 d_2 / 2$
- **Midline (trapezoid):** $MN = (a+b)/2$
- **Angle sum:** any quadrilateral → $360°$

**Last review:** Draw the hierarchy diagram from memory. Then solve one checkpoint (rhombus diagonals → side and area) without looking at notes. State a reason for every step in a proof outline.""",
        "body_he_md": """**רשימת בדיקה מהירה:**

- **מקבילית:** 5 תנאים מספיקים (כל אחד מוכיח)
- **מעויין:** 4 צלעות שוות; אלכסונים מאונכים (לא בהכרח שווים!)
- **מלבן:** מקבילית + זווית ישרה, או אלכסונים שווים
- **ריבוע:** מלבן + צלעות שוות (או מעויין + זווית ישרה)
- **שטח טרפז:** $A = (a+b)h/2$
- **שטח מעויין:** $A = d_1 d_2 / 2$
- **קו אמצע (טרפז):** $MN = (a+b)/2$
- **סכום זוויות:** כל מרובע → $360°$

**חזרה אחרונה:** שרטטו את דיאגרמת ההיררכיה מהזיכרון. פתרו checkpoint אחד (אלכסוני מעויין → צלע ושטח) בלי רשימות. ציינו נימוק לכל שלב בהוכחה.""",
    },
    "summary": {
        "body_en_md": """- **Parallelogram:** opposite sides parallel/equal; diagonals bisect; opposite angles equal, consecutive supplementary
- **Rhombus:** 4 equal sides; diagonals perpendicular and bisect angles
- **Rectangle:** 4 right angles; equal diagonals
- **Square:** rhombus + rectangle combined
- **Trapezoid area:** $(a+b)/2 \\times h$; **midline:** $(a+b)/2$
- **Proofs:** pick one of 5 sufficient conditions; use congruent triangles with a diagonal
- **Angle sum:** always $360°$ in any quadrilateral

**Takeaway:** Classify the shape first, then choose the property or formula that matches. On proofs, write the sufficient condition number you are using before starting.""",
        "body_he_md": """- **מקבילית:** צלעות נגדיות מקבילות/שוות; אלכסונים מחצים; נגדיות שוות, עוקבות משלימות
- **מעויין:** 4 צלעות שוות; אלכסונים מאונכים ומחלקים זוויות
- **מלבן:** 4 זוויות ישרות; אלכסונים שווים
- **ריבוע:** מעויין + מלבן יחד
- **שטח טרפז:** $(a+b)/2 \\times h$; **קו אמצע:** $(a+b)/2$
- **הוכחות:** בחרו אחד מ-5 תנאים; משולשים חופפים עם אלכסון
- **סכום זוויות:** תמיד $360°$ בכל מרובע

**מסקנה:** סווגו את הצורה קודם, ואז בחרו תכונה או נוסחה. בהוכחות, כתבו את מספר התנאי המספיק לפני שמתחילים.""",
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": """**(a) Side length**

The diagonals of a rhombus are perpendicular bisectors of each other. Half-diagonals: $5$ and $12$.

Using the right triangle formed by half a diagonal, half the other diagonal, and a side:
$$\\text{side} = \\sqrt{5^2 + 12^2} = \\sqrt{25 + 144} = \\sqrt{169} = 13$$

**(b) Area**

Rhombus area from diagonals:
$$A = \\frac{d_1 \\times d_2}{2} = \\frac{10 \\times 24}{2} = 120$$

**Verify:** With side 13 and height related to the diagonals, the area is consistent.

**Common slip:** Using $10 + 24$ instead of $(10 \\times 24)/2$, or forgetting to halve the diagonals for the side calculation.""",
        "checkpoint_solution_he": """**(א) אורך צלע**

אלכסוני מעויין מאונכים ומחצים זה את זה. חצי-אלכסונים: $5$ ו-$12$.

במשולש ישר-זווית שנוצר מחצי אלכסון, חצי אלכסון שני, וצלע:
$$\\text{צלע} = \\sqrt{5^2 + 12^2} = \\sqrt{25 + 144} = \\sqrt{169} = 13$$

**(ב) שטח**

שטח מעויין מאלכסונים:
$$A = \\frac{d_1 \\times d_2}{2} = \\frac{10 \\times 24}{2} = 120$$

**אימות:** עם צלע 13, השטח עקבי.

**טעות נפוצה:** שימוש ב-$10 + 24$ במקום $(10 \\times 24)/2$, או שכחת לחלק אלכסונים לפני חישוב הצלע.""",
    },
    "checkpoint_2": {
        "checkpoint_solution_en": """Trapezoid area averages the two parallel bases, then multiplies by the perpendicular height:

$$A = \\frac{a + b}{2} \\times h = \\frac{6 + 10}{2} \\times 4 = 8 \\times 4 = 32$$

**Why this formula works:** The midline of the trapezoid has length $(6+10)/2 = 8$, and the area equals midline $\\times$ height — the same as a rectangle of width 8 and height 4.

**Common slip:** Using non-parallel sides (the legs) instead of the parallel bases 6 and 10, or using a slanted side as height instead of the perpendicular $h = 4$.

**Check:** The result $32$ is less than the enclosing rectangle $10 \\times 4 = 40$ ✓.""",
        "checkpoint_solution_he": """שטח טרפז = ממוצע שני הבסיסים המקבילים כפול הגובה הניצב:

$$A = \\frac{a + b}{2} \\times h = \\frac{6 + 10}{2} \\times 4 = 8 \\times 4 = 32$$

**למה הנוסחה עובדת:** קו האמצע באורך $(6+10)/2 = 8$, והשטח = קו אמצע $\\times$ גובה — כמו מלבן רוחב 8 וגובה 4.

**טעות נפוצה:** שימוש בשוקיים (לא מקבילות) במקום בסיסים 6 ו-10, או שימוש בצלע אלכסונית כגובה במקום $h = 4$ הניצב.

**בדיקה:** $32$ קטן מהמלבן $10 \\times 4 = 40$ ✓.""",
    },
}

EXPLS = {
    1: fmt_expl(
        "In a parallelogram, opposite angles are equal and consecutive angles are supplementary. If one angle is $70°$, its opposite is $70°$ and each adjacent angle is $110°$. The four angles are $70°, 110°, 70°, 110°$. The other three angles are one opposite ($70°$) and two consecutive ($110°$ each) — option 70°, 110°, 110°.",
        "Label the given angle first. In any parallelogram, one angle determines all four. Sketch the shape and mark opposite and consecutive pairs before reading the options.",
        "Option 70°, 110°, 70° treats consecutive angles as opposite. Option 70°, 70°, 70° ignores supplementary angles. All 90° would mean a rectangle.",
        "Compute all four angles before matching options. Bagrut distractors often use correct arithmetic on the wrong angle pair.",
        "במקבילית, זוויות נגדיות שוות ועוקבות משלימות ($180°$). אם זווית אחת $70°$, הנגדית גם $70°$. כל סמוכה: $180° - 70° = 110°$. ארבע הזוויות: $70°, 110°, 70°, 110°$. השאלה מבקשת שלוש אחרות: נגדית ($70°$) ושתי סמוכות ($110°$ כל אחת) — תואם 70°, 110°, 110°.",
        "סמנו את הזווית הנתונה. במקבילית, זווית אחת מספיקה למצוא את כולן. שרטטו וסמנו זוגות נגדיים ועוקבים לפני קריאת התשובות.",
        "70°, 110°, 70° מחליף את הדפוס — מתייחס לשתי זוויות כנגדיות כשהן עוקבות. 70°, 70°, 70° מתעלם מכלל המשלימות. כולן 90° = מלבן, לא מקבילית כללית.",
        "בשאלות זוויות רב-ברירה, חשבו את ארבע הזוויות קודם. מסיחים בבגרות לעיתים נותנים חשבון נכון על זוג זוויות שגוי.",
    ),
    2: fmt_expl(
        "In parallelogram ABCD, $\\angle A = 75°$. Opposite angles are equal, so $\\angle C = 75°$. Consecutive angles are supplementary: $\\angle B = \\angle D = 180° - 75° = 105°$. The three other angles are $75°$, $105°$, and $105°$.",
        "Parallelogram angle problems require only two rules: opposite equal, consecutive supplementary. Label the vertices in order around the shape so you do not confuse which angles are opposite.",
        "A common error is computing $180° - 75° = 105°$ once and forgetting that **both** consecutive angles equal $105°$. Another slip: giving $75°$ for all angles (that would require a rhombus with all equal angles — impossible unless $90°$).",
        "Write the four angles in vertex order (A, B, C, D) and verify they sum to $360°$ before submitting. This catches most angle mistakes instantly.",
        "במקבילית ABCD, $\\angle A = 75°$. נגדיות שוות: $\\angle C = 75°$. עוקבות משלימות: $\\angle B = \\angle D = 180° - 75° = 105°$. שלוש הזוויות האחרות: $75°$, $105°$, $105°$.",
        "בעיות זוויות במקבילית דורשות שני כללים: נגדיות שוות, עוקבות משלימות. סמנו קודקודים לפי סדר כדי לא לבלבל נגדיות.",
        "טעות נפוצה: לחשב $105°$ פעם אחת ולשכוח ש**שתי** הזוויות העוקבות שוות ל-$105°$. טעות נוספת: $75°$ לכולן (דורש מעויין עם זוויות שוות — בלתי אפשרי אלא אם $90°$).",
        "כתבו ארבע זוויות לפי סדר קודקודים (A, B, C, D) ובדקו סכום $360°$ לפני הגשה.",
    ),
    3: fmt_expl(
        "A rectangle has four right angles, so the diagonal forms a right triangle with legs $l = 12$ and $w = 5$. By the Pythagorean theorem: $d = \\sqrt{12^2 + 5^2} = \\sqrt{144 + 25} = \\sqrt{169} = 13$.",
        "Rectangle diagonal problems always reduce to a right triangle. Identify the two legs (length and width), apply $d = \\sqrt{l^2 + w^2}$, and check that the result is longer than either leg.",
        "Students sometimes add $12 + 5 = 17$ instead of using Pythagoras. Another slip: computing $12 \\times 5 = 60$ (that is area, not diagonal). Option 17 is a classic Bagrut distractor.",
        "Recognize the 5–12–13 Pythagorean triple — it appears frequently on Israeli exams. Memorizing common triples (3–4–5, 5–12–13, 8–15–17) saves time.",
        "למלבן ארבע זוויות ישרות, האלכסון יוצר משולש ישר-זווית עם ניצבים $l = 12$ ו-$w = 5$. לפי משפט פיתagoras: $d = \\sqrt{12^2 + 5^2} = \\sqrt{144 + 25} = \\sqrt{169} = 13$.",
        "אלכסון במלבן תמיד מצטמצם למשולש ישר-זווית. זהו שני ניצבים (אורך ורוחב), יישמו $d = \\sqrt{l^2 + w^2}$, ובדקו שהתוצאה ארוכה מכל ניצב — אלכסון תמיד ארוך מהצלעות.",
        "לפעמים מחברים $12 + 5 = 17$ במקום משפט פיתagoras. טעות נוספת: $12 \\times 5 = 60$ (זה שטח, לא אלכסון). 17 הוא מסיח קלאסי בבגרות כי הוא סכום הצלעות.",
        "זיהו שלישייה 5–12–13 — מופיעה הרבה בבגרות. שינון שלישיות נפוצות (3–4–5, 5–12–13, 8–15–17) חוסך זמן יקר בבחינה. הציגו את שלבי החישוב לניקוד חלקי.",
    ),
    4: fmt_expl(
        "The area of a rhombus equals half the product of its diagonals: $A = \\frac{d_1 \\times d_2}{2} = \\frac{6 \\times 8}{2} = \\frac{48}{2} = 24$ square units.",
        "When a rhombus problem gives both diagonals, go directly to $A = d_1 d_2 / 2$. The diagonals are always perpendicular in a rhombus, which is why this formula works. Do not try to find side length first unless asked.",
        "The most common error is forgetting the $\\frac{1}{2}$ factor: $6 \\times 8 = 48$ instead of 24. Another slip: using $6 + 8 = 14$ (adding instead of multiplying and halving).",
        "If only one diagonal and the side are given, use the right triangle from half-diagonals to find the other diagonal, then apply the area formula. But when both diagonals are stated, one step suffices.",
        "שטח מעויין = חצי מכפלת האלכסונים: $A = \\frac{d_1 \\times d_2}{2} = \\frac{6 \\times 8}{2} = \\frac{48}{2} = 24$ יחידות ריבוע.",
        "כשניתנים שני אלכסונים, ישר ל-$A = d_1 d_2 / 2$. אלכסוני מעויין תמיד מאונכים — ולכן הנוסחה עובדת. אל תחפשו צלע אלא אם השאלה מבקשת במפורש.",
        "הטעות הנפוצה: שכחת $\\frac{1}{2}$ — $6 \\times 8 = 48$ במקום 24. טעות נוספת: $6 + 8 = 14$ (חיבור במקום מכפלה וחלוקה ב-2).",
        "אם נתון אלכסון אחד וצלע — מצאו אלכסון שני ממשולש ישר-זווית. כששני אלכסונים נתונים — שלב אחד מספיק לחישוב שטח המעויין.",
    ),
    5: fmt_expl(
        "Trapezoid area uses the average of the two parallel bases times the height: $A = \\frac{a + b}{2} \\times h = \\frac{7 + 13}{2} \\times 5 = \\frac{20}{2} \\times 5 = 10 \\times 5 = 50$ square units.",
        "Identify the two parallel sides (bases) first — they are 7 and 13. The height 5 is the perpendicular distance between them. The formula averages the bases, then multiplies by height — think of it as a rectangle with width equal to the midline.",
        "Common errors: using non-parallel legs instead of bases, forgetting the $\\frac{1}{2}$ in $(a+b)/2$, or multiplying $7 \\times 13 = 91$ (that is not the trapezoid formula). Another slip: adding $7 + 13 + 5 = 25$ (mixing perimeter with area).",
        "Quick check: the average base is 10, times height 5 gives 50. The answer should be less than the larger base times height ($13 \\times 5 = 65$) ✓.",
        "שטח טרפז = ממוצע שני בסיסים מקבילים כפול גובה: $A = \\frac{a + b}{2} \\times h = \\frac{7 + 13}{2} \\times 5 = \\frac{20}{2} \\times 5 = 10 \\times 5 = 50$.",
        "זהו קודם את שני הצלעות המקבילות (7 ו-13). הגובה 5 הוא המרחק הניצב ביניהן. הנוסחה ממצעת בסיסים ומכפילה בגובה — כמו מלבן שרוחבו = קו אמצע.",
        "טעויות: שימוש בשוקיים במקום בסיסים, שכחת $\\frac{1}{2}$, או $7 \\times 13 = 91$ (לא נוסחת טרפז). טעות נוספת: $7 + 13 + 5 = 25$ (ערבוב היקף ושטח).",
        "בדיקה מהירה: בסיס ממוצע 10, כפול 5 = 50. התשובה קטנה מ-$13 \\times 5 = 65$ ✓.",
    ),
    6: fmt_expl(
        "Let $O$ be the diagonal intersection. Given $AO = CO$ and $BO = DO$, in $\\triangle AOB$ and $\\triangle COD$ we have $AO = CO$, $BO = DO$, and $\\angle AOB = \\angle COD$ (vertical). By SAS, $AB = CD$. Similarly $\\triangle AOD \\cong \\triangle COB$ gives $AD = BC$. Both opposite pairs equal → parallelogram.",
        "This is sufficient condition 4. The proof uses two congruent triangle pairs from the diagonals. Label $O$ and mark vertical angles before writing SAS.",
        "Proving parallelism without congruence skips required reasoning. Using SSA instead of SAS is invalid.",
        "State the condition at the top: 'Diagonals bisect → parallelogram (condition 4).' Then write SAS with all three parts.",
        "יהי $O$ חיתוך האלכסונים. נתון: $AO = CO$ ו-$BO = DO$. ב-$\\triangle AOB$ ו-$\\triangle COD$: $AO = CO$, $BO = DO$, $\\angle AOB = \\angle COD$ (זוויות קודקודיות). לפי זצ\"ז: $AB = CD$. כמו כן $\\triangle AOD \\cong \\triangle COB$ → $AD = BC$. שני זוגות צלעות נגדיות שוות → מקבילית (תנאי מספיק 1).",
        "זה תנאי מספיק 4 (אלכסונים מחצים). ההוכחה תמיד משתמשת בשני זוגות משולשים חופפים. סמנו $O$ וזוויות קודקודיות לפני כתיבת זצ\"ז — שלושה חלקים: צלע, זווית, צלע.",
        "לפעמים מנסים להוכיח מקבילות ישירות בלי חפיפה — מדלגים על הנימוק הנדרש. טעות נוספת: שימוש ב-SSA (לא מבחן חפיפה תקף). חובה לכתוב שני זוגות חפיפה.",
        "בהוכחות בגרות, כתבו למעלה: 'מוכיחים שאלכסונים מחצים → מקבילית (תנאי 4).' ואז זצ\"ז עם שלושה חלקים מפורשים. ציינו 'זוויות קודקודיות' ו'צלעות מתאימות'.",
    ),
    7: fmt_expl(
        "In rectangle ABCD, sides $AB = 24$ and $BC = 10$ are perpendicular. The diagonal forms a right triangle: $d = \\sqrt{24^2 + 10^2} = \\sqrt{576 + 100} = \\sqrt{676} = 26$.",
        "A rectangle is a special parallelogram with four right angles, so the diagonal is always the hypotenuse of a right triangle with legs equal to the sides. Check: $26 > 24$ and $26 > 10$ ✓.",
        "Adding $24 + 10 = 34$ is wrong (perimeter thinking). Computing $24 \\times 10 = 240$ gives area, not diagonal. Some students use $24 - 10 = 14$ — subtraction has no geometric meaning here.",
        "Note that $24^2 + 10^2 = 676 = 26^2$ — not a small Pythagorean triple, so you must compute carefully. Show $\\sqrt{576 + 100}$ in your work for partial credit.",
        "במלבן ABCD, $AB = 24$ ו-$BC = 10$ ניצבים. האלכסון = יתר במשולש ישר-זווית: $d = \\sqrt{24^2 + 10^2} = \\sqrt{576 + 100} = \\sqrt{676} = 26$.",
        "מלבן הוא מקבילית עם ארבע זוויות ישרות, ולכן האלכסון תמיד יתר במשולש ישר-זווית. בדיקה: $26 > 24$ ו-$26 > 10$ — האלכסון חייב להיות ארוך מכל אחד מהניצבים.",
        "$24 + 10 = 34$ שגוי (חשיבת היקף). $24 \\times 10 = 240$ = שטח, לא אלכסון. $24 - 10 = 14$ — חיסור ללא משמעות גיאומטרית כאן.",
        "$676 = 26^2$ — לא שלישייה קטנה, חשבו בזהירות. הציגו $\\sqrt{576 + 100}$ בעבודה לניקוד חלקי בבגרות בגיאומטריה.",
    ),
    8: fmt_expl(
        "The trapezoid midline equals the average of the two parallel bases: $MN = \\frac{a + b}{2}$. Given $MN = 15$ and one base $a = 12$: $15 = \\frac{12 + b}{2}$. Multiply both sides by 2: $30 = 12 + b$, so $b = 18$.",
        "Midline problems are algebra problems once you write the formula. Identify which sides are the parallel bases (not the legs). Substitute the known midline and one base, then solve for the unknown.",
        "A common error is using $15 - 12 = 3$ (subtracting instead of using the average formula). Another slip: computing $15 \\times 2 = 30$ but forgetting to subtract 12, giving $b = 30$ instead of 18.",
        "Verify: $\\frac{12 + 18}{2} = 15$ ✓. Always substitute your answer back into the midline formula on the Bagrut — it takes five seconds and catches algebra errors.",
        "קו אמצע טרפז = ממוצע שני בסיסים: $MN = \\frac{a + b}{2}$. נתון $MN = 15$ ובסיס $a = 12$: $15 = \\frac{12 + b}{2}$. כפל ב-2: $30 = 12 + b$, לכן $b = 18$.",
        "בעיות קו אמצע = חישוב אלגebraי אחרי כתיבת הנוסחה. זהו קודם את שני הבסיסים המקבילים (לא השוקיים). הציבו את קו האמצע והבסיס הידוע, ופתרו משוואה לינארית.",
        "טעות: $15 - 12 = 3$ (חיסור במקום נוסחת ממוצע). טעות נוספת: $15 \\times 2 = 30$ בלי חיסור 12 → $b = 30$ במקום 18. זכרו: קו אמצע = ממוצע, לא הפרש.",
        "אימות: $\\frac{12 + 18}{2} = 15$ ✓. החזירו תמיד לנוסחת קו האמצע — תופס טעויות חישוב בבחינה. בדיקה זו לוקחת חמש שניות ושווה את הנקודות.",
    ),
}

ACCEPTABLE_ANSWERS = {
    2: [
        "$\\angle C = 75°$ (opposite); $\\angle B = \\angle D = 105°$ (supplementary)",
        "75, 105, 105",
        "105",
    ],
    3: ["13", "$d = 13$", "$d=\\sqrt{169}=13$"],
    4: ["24", "$A = 24$", "$A=(6\\times8)/2=24$"],
    5: ["50", "$A=50$", "$A=(7+13)/2\\times5=50$"],
    6: [
        "Let O be intersection. $AO=CO$, $BO=DO$. In $\\triangle AOB$ and $\\triangle COD$: $AO=CO$, $BO=DO$, $\\angle AOB=\\angle COD$ (vertical). By SAS: $\\triangle AOB\\cong\\triangle COD$. So $AB=CD$. Similarly $AD=BC$. Both pairs of opposite sides equal → parallelogram. ∎",
        "parallelogram",
    ],
    7: ["26", "$d=26$", "$d=\\sqrt{676}=26$"],
    8: ["18", "$b=18$", "$15=(12+b)/2 \\Rightarrow b=18$"],
}

EXERCISE_FIXES = {
    "e1": {
        "solution_en": "Opposite angles equal: $\\angle C = 75°$. Consecutive supplementary: $\\angle B = \\angle D = 180° - 75° = 105°$.",
        "solution_he": "נגדיות שוות: $\\angle C=75°$. עוקבות משלימות: $\\angle B=\\angle D=180°-75°=105°$.",
    },
    "e2": {
        "solution_en": "Right triangle with legs 12 and 5: $d=\\sqrt{12^2+5^2}=\\sqrt{169}=13$.",
        "solution_he": "משולש ישר-זווית: $d=\\sqrt{12^2+5^2}=\\sqrt{169}=13$.",
    },
    "e3": {
        "solution_en": "Rhombus area from diagonals: $A=(6\\times8)/2=24$.",
        "solution_he": "שטח מעויין: $A=(6\\times8)/2=24$.",
    },
    "e4": {
        "solution_en": "Trapezoid area: $A=(7+13)/2\\times5=10\\times5=50$.",
        "solution_he": "שטח טרפז: $A=(7+13)/2\\times5=50$.",
    },
    "e5": {
        "solution_en": "Let O be intersection. $AO=CO$, $BO=DO$. In $\\triangle AOB$ and $\\triangle COD$: $AO=CO$, $BO=DO$, $\\angle AOB=\\angle COD$ (vertical). By SAS: $\\triangle AOB\\cong\\triangle COD$. So $AB=CD$. Similarly $AD=BC$. Both pairs of opposite sides equal → parallelogram. ∎",
        "solution_he": "יהי $O$ חיתוך האלכסונים. ב-$\\triangle AOB$ ו-$\\triangle COD$: $AO=CO$, $BO=DO$, $\\angle AOB=\\angle COD$ (קודקודיות). לפי זצ\"ז: $AB=CD$. כמו כן $AD=BC$ → מקבילית. ■",
    },
    "e6": {
        "solution_en": "Rectangle diagonal: $d=\\sqrt{24^2+10^2}=\\sqrt{676}=26$.",
        "solution_he": "אלכסון מלבן: $d=\\sqrt{24^2+10^2}=\\sqrt{676}=26$.",
    },
    "e7": {
        "solution_en": "Midline $MN=(a+b)/2$: $15=(12+b)/2 \\Rightarrow 30=12+b \\Rightarrow b=18$.",
        "solution_he": "קו אמצע: $15=(12+b)/2 \\Rightarrow b=18$.",
    },
    "e8": {
        "solution_en": "Let M,N,P,Q be midpoints of AB,BC,CD,DA. In triangle ABD, MQ is the midline parallel to BD and MQ=BD/2. In triangle BCD, NP is the midline parallel to BD and NP=BD/2. So MQ∥NP and MQ=NP → MNPQ is a parallelogram. ∎",
        "solution_he": "MQ ו-NP שניהם קווי אמצע במשולשים שונים, שניהם מקבילים ל-BD ושווים לו בחצי. לכן MQ∥NP ו-MQ=NP → MNPQ מקבילית (וריניון). ■",
    },
    "e9": {
        "solution_en": "Drop perpendiculars from D,C to AB. Base excess on each side $=(14-6)/2=4$. Height $=\\sqrt{5^2-4^2}=3$. Area $=(14+6)/2\\times3=30$.",
        "solution_he": "הורידו ניצבות מ-D,C ל-AB. עודף בסיס בכל צד $=(14-6)/2=4$. גובה $=\\sqrt{5^2-4^2}=3$. שטח $=(14+6)/2\\times3=30$.",
    },
    "e10": {
        "solution_en": "$\\angle A + \\angle D = 180°$ means $AB \\parallel CD$ (co-interior angles). So ABCD is a trapezoid. $AB=CD$ means the legs are equal — this is an isosceles trapezoid by definition. ∎",
        "solution_he": "$\\angle A+\\angle D=180°$ → $AB\\parallel CD$ (זוויות חד-צדדיות). $AB=CD$ (שוקיים שווים). לפי הגדרה → טרפז שווה-שוקיים. ■",
    },
    "e11": {
        "solution_en": "Side = $s$. BM=$s/2$. Triangle ABM: base AB=$s$, height BM=$s/2$. Area $= s\\cdot s/2 / 2 = s^2/4$. Total square area = $s^2$; subtract $\\triangle ABM$; remaining AMCD area = $3s^2/4$.",
        "solution_he": "צלע $=s$, BM=$s/2$. שטח $\\triangle ABM = s\\cdot(s/2)/2 = s^2/4$. שטח הריבוע $s^2$; נשאר AMCD $= 3s^2/4$.",
    },
    "e12": {
        "solution_en": "In triangles △APO and △CQO: AO=CO (diagonals bisect), ∠AOP=∠COQ (vertical angles), ∠OAP=∠OCQ (alternate interior, AB∥CD). By ASA: △APO≅△CQO. Therefore PO=OQ. ∎",
        "solution_he": "ב-$\\triangle APO$ ו-$\\triangle CQO$: $AO=CO$, $\\angle AOP=\\angle COQ$ (קודקודיות), $\\angle OAP=\\angle OCQ$ (מתחלפות). לפי ז\"ז\"ז: $\\triangle APO\\cong\\triangle CQO$ → $PO=OQ$. ■",
    },
    "e13": {
        "solution_en": "Draw diagonal AC, splitting ABCD into triangles ABC and ACD. Sum of angles in △ABC = 180°. Sum in △ACD = 180°. Total = 360°. These triangles together cover all 4 angles of the quadrilateral. ∎",
        "solution_he": "אלכסון AC מפצל את ABCD ל-$\\triangle ABC$ ו-$\\triangle ACD$. סכום זוויות בכל משולש $180°$. סה\"כ $180°+180°=360°$ — מכסה את כל ארבע הזוויות. ■",
    },
}


def validate(data: dict) -> list[str]:
    errs = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        sid = sec.get("id", kind)
        if kind in MIN:
            en_min, he_min = MIN[kind]
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errs.append(f"{sid}: EN {en_w} < {en_min}")
            if he_w < he_min:
                errs.append(f"{sid}: HE {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errs.append(f"{sid}: weak Hebrew body")
    for q in data["questions"]:
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80:
                errs.append(f"q{q['ord']} expl_{lang}: {w} < 80 words")
            if w > 150:
                errs.append(f"q{q['ord']} expl_{lang}: {w} > 150 words")
    return errs


def main() -> None:
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    data["summary_en"] = (
        "Quadrilaterals — properties, proofs, and area formulas for parallelograms, "
        "rhombus, rectangle, square, and trapezoid, including the midline theorem and "
        "five sufficient conditions for parallelogram proofs."
    )
    data["summary_he"] = (
        "מרובעים — תכונות, הוכחות ונוסחאות שטח למקבילית, מעויין, מלבן, ריבוע וטרפז, "
        "כולל משפט קו האמצע וחמישה תנאים מספיקים להוכחת מקבילית."
    )

    for sec in data["sections"]:
        sid = sec.get("id")
        kind = sec.get("kind")
        if sid in SECTION_BODIES:
            sec.update(SECTION_BODIES[sid])
        elif kind in SECTION_BODIES:
            sec.update(SECTION_BODIES[kind])
        if sid in CHECKPOINTS:
            sec.update(CHECKPOINTS[sid])

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]
        if ord_ in ACCEPTABLE_ANSWERS:
            q["answer_payload"]["acceptable_answers"] = ACCEPTABLE_ANSWERS[ord_]

    ex_sec = next(s for s in data["sections"] if s.get("kind") == "exercise_set")
    for ex in ex_sec.get("exercises", []):
        if ex["id"] in EXERCISE_FIXES:
            ex.update(EXERCISE_FIXES[ex["id"]])

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
