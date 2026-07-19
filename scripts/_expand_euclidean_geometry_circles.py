#!/usr/bin/env python3
"""Expand euclidean_geometry_circles.json per .cursor/skills/expand-lessons-cursor/SKILL.md."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/euclidean_geometry_circles.json"

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
        "body_en_md": """The circle is perhaps the most symmetric shape in Euclidean geometry. Every point on the circumference is the same distance from the centre, and that single fact generates a web of angle and length theorems that appear throughout the Israeli Bagrut — especially in 4–5 unit geometry proofs and multi-step calculation items.

**What this lesson covers:**
- **Central vs. inscribed angles** on the same arc, including the semicircle corollary ($90°$).
- **Chord properties:** perpendicular from centre bisects a chord; equal chords are equidistant from the centre.
- **Tangent–radius perpendicularity** and equal tangent lengths from an external point.
- **Tangent–chord angle theorem** (alternate segment).
- **Power of a point** for intersecting chords, secants, and tangents.
- **Cyclic quadrilaterals** and opposite-angle supplements.

Bagrut items rarely test one theorem in isolation. You will combine angle facts with right triangles (Pythagoras), sometimes with similarity. The method guide at the end maps problem wording to the correct theorem — learn to read the diagram before reaching for a formula.""",
        "body_he_md": """המעגל הוא אולי הצורה הסימטרית ביותר בגאומטריה אוקלידית. כל נקודה על ההיקף נמצאת באותו מרחק מהמרכז, והעובדה הזו יוצרת רשת של משפטי זוויות ואורכים שמופיעים לאורך הבגרות — במיוחד בהוכחות גאומטריה ב-4–5 יחידות ובשאלות חישוב רב-שלביות.

**מה השיעור מכסה:**
- **זוויות מרכזיות מול חסומות** על אותה קשת, כולל מסקנת חצי-המעגל ($90°$).
- **תכונות מיתר:** ניצב ממרכז מחלק מיתר; מיתרים שווים במרחק שווה מהמרכז.
- **משיק מאונך לרדיוס** ואורכי משיקים שווים מנקודה חיצונית.
- **משפט זווית משיק–מיתר** (הקטע הנגדי).
- **עוצמת נקודה** למיתרים חוצים, חותכים ומשיקים.
- **מרובעים חסומים** וזוויות נגדיות משלימות.

בבגרות לעיתים נדרשים כמה משפטים יחד — זוויות עם משולשים ישרי-זווית (פיתגורס), לפעמים עם דמיון. מדריך השיטה בסוף ממפה ניסוח בעיה למשפט הנכון — למדו לקרוא את השרטוט לפני שמושכים נוסחה.""",
    },
    "definition": {
        "body_en_md": """**Circle:** set of points at fixed distance $r$ (radius) from centre $O$.

**Central angle** $\\angle AOB$: vertex at the centre; its measure equals the measure of arc $AB$ (in degrees).

**Inscribed angle** $\\angle ACB$: vertex $C$ on the circle. On the same arc $AB$:
$$\\angle ACB = \\frac{1}{2}\\angle AOB$$

**Chord:** segment with both endpoints on the circle.
- Perpendicular from $O$ to chord **bisects** the chord.
- **Equal chords** $\\Rightarrow$ equal distance from $O$.

**Tangent:** line touching the circle at exactly one point $T$. Then $OT \\perp$ tangent at $T$.

**Tangent from external point $P$:** the two tangent segments $PA$ and $PB$ have **equal length**.

**Tangent–chord angle:** angle between tangent at $A$ and chord $AB$ equals the inscribed angle in the **alternate** segment (on the opposite side of $AB$).

**Power of a point $P$:**
- Chords $AB$, $CD$ intersect inside at $P$: $PA\\cdot PB = PC\\cdot PD$.
- Secants from outside: same product rule on whole secant segments.
- Tangent $PT$ and secant $PAB$: $PT^2 = PA\\cdot PB$.

**Cyclic quadrilateral:** all four vertices on one circle. Opposite angles are supplementary: $\\angle A + \\angle C = 180°$, $\\angle B + \\angle D = 180°$.""",
        "body_he_md": """**מעגל:** קבוצת נקודות במרחק קבוע $r$ (רדיוס) ממרכז $O$.

**זווית מרכזית** $\\angle AOB$: קודקוד במרכז; גודלה שווה לגודל קשת $AB$ (במעלות).

**זווית חסומה** $\\angle ACB$: קודקוד $C$ על המעגל. על אותה קשת $AB$:
$$\\angle ACB = \\frac{1}{2}\\angle AOB$$

**מיתר:** קטע ששני קצותיו על המעגל.
- ניצב מ-$O$ למיתר **מחלק** את המיתר.
- **מיתרים שווים** $\\Rightarrow$ מרחק שווה מ-$O$.

**משיק:** ישר הנוגע במעגל בנקודה אחת $T$. אז $OT \\perp$ למשיק ב-$T$.

**משיק מנקודה חיצונית $P$:** שני קטעי המשיק $PA$ ו-$PB$ **שווים** באורכם.

**זווית משיק–מיתר:** הזווית בין משיק ב-$A$ למיתר $AB$ שווה לזווית החסומה ב**קטע הנגדי** (בצד השני של $AB$).

**עוצמת נקודה $P$:**
- מיתרים $AB$, $CD$ נחתכים בפנים ב-$P$: $PA\\cdot PB = PC\\cdot PD$.
- חותכים מבחוץ: אותו כלל על קטעי החוצה המלאים.
- משיק $PT$ וחוצה $PAB$: $PT^2 = PA\\cdot PB$.

**מרובע חסום:** כל ארבע הקודקודים על מעגל אחד. זוויות נגדיות משלימות: $\\angle A + \\angle C = 180°$, $\\angle B + \\angle D = 180°$.""",
    },
    "theory": {
        "body_en_md": """### Inscribed angle theorem
An inscribed angle equals half the central angle subtending the **same arc**.

**Proof sketch (centre inside the angle):** Draw diameter $AD$ from vertex $A$. Use isosceles triangles ($OA=OB=OC=r$) and exterior angles: each half contributes $\\angle OAB$ or $\\angle OAC$, so $\\angle BOC = 2\\angle BAC$.

**Corollaries:**
- All inscribed angles on the same arc are equal.
- Angle in a semicircle: diameter $AB$ $\\Rightarrow$ $\\angle ACB = 90°$ for any $C$ on the circle.

### Tangent–chord theorem
Angle between tangent at $A$ and chord $AB$ equals inscribed angle $\\angle ACB$ where $C$ lies on the arc **not** containing the angle between tangent and chord (alternate segment).

### Intersecting chords angle
Two chords meet inside: inscribed angle equals half the sum of the two intercepted arcs.

### Cyclic quadrilateral theorem
In cyclic $ABCD$: $\\angle A + \\angle C = 180°$. **Converse:** if opposite angles of a quadrilateral sum to $180°$, the quadrilateral is cyclic.

### Power of a point — why the products match
Similar triangles from equal inscribed angles on the same arc prove $PA\\cdot PB = PC\\cdot PD$ for intersecting chords; the external secant and tangent cases follow from the same similarity pattern or from right triangles with tangents.

| Situation | Key relation |
|-----------|--------------|
| Inscribed vs. central | inscribed $= \\frac{1}{2}$ central |
| Semicircle | inscribed $= 90°$ |
| Cyclic quad | opposite angles $= 180°$ |
| Chords/secants at $P$ | $PA\\cdot PB = PC\\cdot PD$ |
| Tangent + secant | $PT^2 = PA\\cdot PB$ |""",
        "body_he_md": """### משפט הזווית החסומה
זווית חסומה שווה למחצית הזווית המרכזית הנשענת על **אותה קשת**.

**שרטוט הוכחה (מרכז בתוך הזווית):** שרטטו קוטר $AD$ מקודקוד $A$. השתמשו במשולשים שווי-שוקיים ($OA=OB=OC=r$) ובזוויות חיצוניות: כל חצי תורם $\\angle OAB$ או $\\angle OAC$, ולכן $\\angle BOC = 2\\angle BAC$.

**מסקנות:**
- כל הזוויות החסומות על אותה קשת שוות.
- זווית בחצי-מעגל: קוטר $AB$ $\\Rightarrow$ $\\angle ACB = 90°$ לכל $C$ על המעגל.

### משפט משיק–מיתר
הזווית בין משיק ב-$A$ למיתר $AB$ שווה לזווית החסומה $\\angle ACB$ כאשר $C$ על הקשת **שלא** מכילה את הזווית בין המשיק למיתר (קטע נגדי).

### זווית בין מיתרים חוצים
שני מיתרים נפגשים בפנים: זווית חסומה שווה למחצית סכום שתי הקשתות הנחתכות.

### משפט מרובע חסום
במרובע חסום $ABCD$: $\\angle A + \\angle C = 180°$. **הפוך:** אם זוויות נגדיות במרובע מסתכמות ל-$180°$, המרובע חסום.

### עוצמת נקודה — למה המכפלות שוות
משולשים דומים מזוויות חסומות שוות על אותה קשת מוכיחים $PA\\cdot PB = PC\\cdot PD$ למיתרים חוצים; מקרי חוצה חיצוני ומשיק נובעים מאותו דפוס דמיון או ממשולשים ישרי-זווית עם משיקים.

| מצב | קשר מרכזי |
|-----|-----------|
| חסומה מול מרכזית | חסומה $= \\frac{1}{2}$ מרכזית |
| חצי-מעגל | חסומה $= 90°$ |
| מרובע חסום | נגדיות $= 180°$ |
| מיתרים/חותכים ב-$P$ | $PA\\cdot PB = PC\\cdot PD$ |
| משיק + חוצה | $PT^2 = PA\\cdot PB$ |""",
    },
    "worked_example_1": {
        "body_en_md": """**Given:** Circle with centre $O$. Central angle $\\angle AOB = 80°$. Point $C$ is on the **major** arc (not containing the $80°$ arc). Find inscribed angle $\\angle ACB$.

This is the baseline inscribed-angle item: identify which arc the inscribed angle subtends, then halve the matching central angle.

### Move 1: Identify the arc
$\\angle ACB$ is an inscribed angle with vertex on the circle. It subtends minor arc $AB$, because $C$ sits on the major arc and "looks at" the shorter arc between $A$ and $B$.

### Move 2: Match the central angle
Central angle $\\angle AOB = 80°$ subtends the same minor arc $AB$.

### Move 3: Apply the theorem
$$\\angle ACB = \\frac{1}{2}\\angle AOB = \\frac{80°}{2} = 40°$$

**Answer:** $\\angle ACB = 40°$.

**Note:** Any point on the major arc gives the same $40°$ — all inscribed angles on one arc are equal. If $C$ were on minor arc $AB$, the inscribed angle would subtend the **major** arc and equal $\\frac{1}{2}(360°-80°)=140°$.

**Bagrut check:** Always mark minor vs. major arc before halving; swapping arcs is the most common $40°$ vs. $140°$ error.""",
        "body_he_md": """**נתון:** מעגל עם מרכז $O$. זווית מרכזית $\\angle AOB = 80°$. נקודה $C$ על **הקשת הגדולה** (לא על קשת ה-$80°$). מצאו זווית חסומה $\\angle ACB$.

זו שאלת בסיס לזווית חסומה: זיהוי איזו קשת הזווית החסומה נשענת עליה, ואז חצי מהזווית המרכזית המתאימה.

### צעד 1: זיהוי הקשת
$\\angle ACB$ היא זווית חסומה שקודקודה על המעגל. היא נשענת על הקשת הקטנה $AB$, כי $C$ על הקשת הגדולה ו"רואה" את הקשת הקצרה בין $A$ ל-$B$.

### צעד 2: התאמת הזווית המרכזית
הזווית המרכזית $\\angle AOB = 80°$ נשענת על אותה קשת קטנה $AB$.

### צעד 3: יישום המשפט
$$\\angle ACB = \\frac{1}{2}\\angle AOB = \\frac{80°}{2} = 40°$$

**תשובה:** $\\angle ACB = 40°$.

**הערה:** כל נקודה על הקשת הגדולה נותנת $40°$ — כל הזוויות החסומות על קשת אחת שוות. אם $C$ הייתה על הקשת הקטנה $AB$, הזווית החסומה הייתה נשענת על **הקשת הגדולה** ושווה $\\frac{1}{2}(360°-80°)=140°$.

**בדיקת בגרות:** סמנו תמיד קשת קטנה מול גדולה לפני החלוקה ב-2; החלפת קשתות — הטעות הנפוצה ביותר בין $40°$ ל-$140°$.""",
    },
    "worked_example_2": {
        "body_en_md": """**Given:** Chords $AB$ and $CD$ intersect inside a circle at point $P$. $PA = 4$, $PB = 6$, $PC = 3$. Find $PD$.

Power-of-a-point for intersecting chords converts four segment lengths into one unknown — no angle chasing required.

### Move 1: Name segments from $P$
On chord $AB$: segments are $PA=4$ and $PB=6$. On chord $CD$: known $PC=3$, unknown $PD$.

### Move 2: Write the product equation
Intersecting chords theorem:
$$PA\\cdot PB = PC\\cdot PD$$
$$4 \\times 6 = 3 \\times PD$$

### Move 3: Solve
$$24 = 3\\cdot PD \\Rightarrow PD = 8$$

**Answer:** $PD = 8$.

**Full chord check:** $CD = PC + PD = 3 + 8 = 11$. Verify: $4\\times6 = 24$ and $3\\times8 = 24$ ✓.

**Common mistake:** Using whole chord lengths ($AB=10$) instead of segments from $P$. The formula always uses distances **from the intersection point** along each line.

**Exam tip:** Label $P$ on your diagram and write $PA$, $PB$, $PC$, $PD$ before multiplying — Bagrut partial credit often awards the correct setup.""",
        "body_he_md": """**נתון:** מיתרים $AB$ ו-$CD$ נחתכים בתוך מעגל בנקודה $P$. $PA = 4$, $PB = 6$, $PC = 3$. מצאו $PD$.

עוצמת נקודה למיתרים חוצים ממירה ארבעה אורכי קטעים לנעלם אחד — בלי רדיפת זוויות.

### צעד 1: שמות קטעים מ-$P$
על מיתר $AB$: הקטעים $PA=4$ ו-$PB=6$. על מיתר $CD$: ידוע $PC=3$, לא ידוע $PD$.

### צעד 2: כתיבת משוואת המכפלות
משפט מיתרים חוצים:
$$PA\\cdot PB = PC\\cdot PD$$
$$4 \\times 6 = 3 \\times PD$$

### צעד 3: פתרון
$$24 = 3\\cdot PD \\Rightarrow PD = 8$$

**תשובה:** $PD = 8$.

**בדיקת מיתר מלא:** $CD = PC + PD = 3 + 8 = 11$. אימות: $4\\times6 = 24$ ו-$3\\times8 = 24$ ✓.

**טעות נפוצה:** שימוש באורכי מיתר שלמים ($AB=10$) במקום קטעים מ-$P$. הנוסחה תמיד משתמשת במרחקים **מנקודת החיתוך** לאורך כל ישר.

**טיפ לבחינה:** סמנו $P$ בשרטוט וכתבו $PA$, $PB$, $PC$, $PD$ לפני הכפל — בבגרות לעיתים נותנים נקודות על ההכנה הנכונה.""",
    },
    "worked_example_3": {
        "body_en_md": """**Given:** External point $P$ is $10\\;\\text{cm}$ from centre $O$ of a circle with radius $r = 6\\;\\text{cm}$. Find: (a) length of tangent $PT$ from $P$; (b) angle $\\angle OPT$.

Combines tangent $\\perp$ radius (right triangle) with basic טריגונומטריה — a standard 4–5 unit composite item.

### Move 1: Right triangle at tangency
Let $T$ be the point of tangency. $OT \\perp PT$, so $\\triangle OPT$ is right-angled at $T$ with hypotenuse $OP=10$ and leg $OT=r=6$.

### Move 2: Tangent length (a)
$$PT^2 + OT^2 = OP^2$$
$$PT^2 + 36 = 100 \\Rightarrow PT^2 = 64 \\Rightarrow PT = 8\\;\\text{cm}$$

### Move 3: Angle at $P$ (b)
In right $\\triangle OPT$: $\\cos(\\angle OPT) = \\dfrac{PT}{OP} = \\dfrac{8}{10} = 0.8$.
$$\\angle OPT \\approx 36.87° \\approx 37°$$

**Answer:** (a) $PT = 8\\;\\text{cm}$; (b) $\\angle OPT \\approx 37°$.

**Reminder:** Both tangents from $P$ have length $8\\;\\text{cm}$. The angle between them uses symmetry: each makes $\\approx 37°$ with $OP$.

**Verify:** $6^2 + 8^2 = 36 + 64 = 100 = 10^2$ ✓. Never use $OP - r = 4$ as tangent length — that ignores the right angle at $T$.""",
        "body_he_md": """**נתון:** נקודה חיצונית $P$ במרחק $10\\;\\text{ס\"מ}$ ממרכז $O$ של מעגל ברדיוס $r = 6\\;\\text{ס\"מ}$. מצאו: (א) אורך משיק $PT$ מ-$P$; (ב) זווית $\\angle OPT$.

משלב משיק $\\perp$ רדיוס (משולש ישר-זווית) עם טריגונומטריה בסיסית — פריט מורכב טיפוסי ב-4–5 יחידות.

### צעד 1: משולש ישר-זווית בנקודת השקה
תהי $T$ נקודת ההשקה. $OT \\perp PT$, ולכן $\\triangle OPT$ ישר-זוויתי ב-$T$ עם יתר $OP=10$ ורגל $OT=r=6$.

### צעד 2: אורך משיק (א)
$$PT^2 + OT^2 = OP^2$$
$$PT^2 + 36 = 100 \\Rightarrow PT^2 = 64 \\Rightarrow PT = 8\\;\\text{ס\"מ}$$

### צעד 3: זווית ב-$P$ (ב)
ב-$\\triangle OPT$ ישר-זוויתי: $\\cos(\\angle OPT) = \\dfrac{PT}{OP} = \\dfrac{8}{10} = 0.8$.
$$\\angle OPT \\approx 36.87° \\approx 37°$$

**תשובה:** (א) $PT = 8\\;\\text{ס\"מ}$; (ב) $\\angle OPT \\approx 37°$.

**תזכורת:** שני המשיקים מ-$P$ באורך $8\\;\\text{ס\"מ}$. הזווית ביניהם משתמשת בסימטריה: כל אחד עושה $\\approx 37°$ עם $OP$.

**אימות:** $6^2 + 8^2 = 36 + 64 = 100 = 10^2$ ✓. לעולם אל תשתמשו ב-$OP - r = 4$ כאורך משיק — זה מתעלם מהזווית הישרה ב-$T$.""",
    },
    "method_guide": {
        "body_en_md": """**Decision flow for circle problems:**

1. **Read the diagram** — mark centre $O$, radii, tangency points, and whether angles are central or inscribed.
2. **Angle question?** Same arc $\\Rightarrow$ inscribed $= \\frac{1}{2}$ central. Diameter present $\\Rightarrow$ check for $90°$ in semicircle.
3. **Length with tangent?** Draw radius to tangency; use $OT \\perp PT$ and Pythagoras.
4. **Products of segments?** Power of a point — label all four segments from intersection $P$.
5. **Four vertices on a circle?** Cyclic quad $\\Rightarrow$ opposite angles sum to $180°$.

| Situation | Theorem |
|---|---|
| Angle at centre vs. circumference | Inscribed $= \\frac{1}{2}$ central |
| Angle in semicircle | $= 90°$ |
| Intersecting chords inside | $PA\\cdot PB = PC\\cdot PD$ |
| Two secants from external point | $PA\\cdot PB = PC\\cdot PD$ |
| Tangent from external point | $PT^2 = PA\\cdot PB$ |
| Cyclic quadrilateral | Opposite angles $= 180°$ |
| Tangent $\\perp$ radius | $OT \\perp PT$ |
| Tangent–chord angle | $=$ inscribed angle in alternate segment |

**When stuck:** Add one radius or diameter — it often creates an isosceles or right triangle you can use.""",
        "body_he_md": """**זרימת החלטות לבעיות מעגל:**

1. **קראו את השרטוט** — סמנו מרכז $O$, רדיוסים, נקודות השקה, ואם זוויות מרכזיות או חסומות.
2. **שאלת זווית?** אותה קשת $\\Rightarrow$ חסומה $= \\frac{1}{2}$ מרכזית. יש קוטר $\\Rightarrow$ בדקו $90°$ בחצי-מעגל.
3. **אורך עם משיק?** שרטטו רדיוס לנקודת השקה; השתמשו ב-$OT \\perp PT$ ובפיתגורס.
4. **מכפלות קטעים?** עוצמת נקודה — סמנו ארבעה קטעים מנקודת החיתוך $P$.
5. **ארבע קודקודים על מעגל?** מרובע חסום $\\Rightarrow$ נגדיות מסתכמות ל-$180°$.

| מצב | משפט |
|---|---|
| זווית מרכז מול היקף | חסומה $= \\frac{1}{2}$ מרכזית |
| זווית בחצי-מעגל | $= 90°$ |
| מיתרים חוצים בפנים | $PA\\cdot PB = PC\\cdot PD$ |
| שני חותכים מבחוץ | $PA\\cdot PB = PC\\cdot PD$ |
| משיק מבחוץ | $PT^2 = PA\\cdot PB$ |
| מרובע חסום | נגדיות $= 180°$ |
| משיק $\\perp$ רדיוס | $OT \\perp PT$ |
| זווית משיק–מיתר | $=$ חסומה בקטע נגדי |

**כשתקועים:** הוסיפו רדיוס או קוטר — לעיתים נוצר משולש שווה-שוקיים או ישר-זוויתי.""",
    },
    "pitfall": {
        "body_en_md": """1. **Inscribed angle is half the central angle, not equal.** Students write $\\angle ACB = \\angle AOB$ and get double the correct value. Always ask: "Which arc does the inscribed angle subtend?"

2. **Power of a point uses segments from $P$, not full chord lengths.** For intersecting chords, $PA$ and $PB$ are the two pieces of one chord starting at $P$ — not $AB$ as a whole.

3. **Angle in a semicircle is $90°$, not $180°$.** The **arc** subtended by a diameter is $180°$; the **inscribed** angle on that arc is half: $90°$.

4. **Cyclic quadrilateral: opposite angles sum to $180°$, not adjacent.** Adjacent angles in any quadrilateral can be anything; only opposite pairs in a cyclic quad are supplementary.

5. **Major vs. minor arc confusion.** If the inscribed vertex lies on the minor arc, it subtends the major arc — the angle can exceed $90°$.

**Fix habit:** After every angle answer, trace the arc with your finger on the diagram and confirm you halved the correct central angle.""",
        "body_he_md": """1. **זווית חסומה = חצי מרכזית, לא שווה.** תלמידים כותבים $\\angle ACB = \\angle AOB$ ומקבלים כפול מהנכון. שאלו תמיד: "על איזו קשת הזווית החסומה נשענת?"

2. **עוצמת נקודה משתמשת בקטעים מ-$P$, לא באורכי מיתר שלמים.** במיתרים חוצים, $PA$ ו-$PB$ הם שני חלקי אותו מיתר מ-$P$ — לא $AB$ כולו.

3. **זווית בחצי-מעגל = $90°$, לא $180°$.** **הקשת** על קוטר היא $180°$; **הזווית החסומה** עליה היא חצי: $90°$.

4. **מרובע חסום: נגדיות מסתכמות ל-$180°$, לא שכנות.** זוויות שכנות בכל מרובע יכולות להיות כל ערך; רק זוגות נגדיים במרובע חסום משלימים.

5. **בלבול קשת קטנה מול גדולה.** אם קודקוד חסום על הקשת הקטנה, הוא נשען על הקשת הגדולה — הזווית יכולה לעלות על $90°$.

**הרגל תיקון:** אחרי כל תשובת זווית, עקבו אחרי הקשת בשרטוט וודאו שחילקתם ב-2 את הזווית המרכזית הנכונה.""",
    },
    "why_matters": {
        "body_en_md": """Circle theorems are the bridge between pure angle chasing and applied geometry on the Bagrut. Optics (lenses), navigation (bearing arcs), and engineering drawings all rely on circular symmetry — but in exam terms, circles unlock **proof chains**: one inscribed angle leads to a cyclic quad, which fixes a tangent angle, which feeds a power-of-a-point length.

**Cross-links on A Step Forward:**
- **Triangles & Pythagoras:** tangent problems always produce a right triangle.
- **Trigonometry:** inscribed angles connect to arc measures used in radian work later.
- **Quadrilaterals:** proving a shape is cyclic is a common step in 5-unit proof questions.

When you master the method guide table, you stop re-deriving facts under time pressure — you **recognize** the problem type and deploy the correct theorem in one move.""",
        "body_he_md": """משפטי מעגל הם הגשר בין רדיפת זוויות טהורה לגאומטריה יישומית בבגרות. אופטיקה (עדשות), ניווט (קשתות כיוון) ושרטוטים הנדסיים מסתמכים על סימטריה מעגלית — אבל בבחינה, מעגלים פותחים **שרשראות הוכחה**: זווית חסומה אחת מובילה למרובע חסום, שקובע זווית משיק, שנכנסת לעוצמת נקודה.

**קשרים במסלול A Step Forward:**
- **משולשים ופיתגורס:** בעיות משיק תמיד יוצרות משולש ישר-זוויתי.
- **טריגונומטריה:** זוויות חסומות מתחברות למידות קשת בעבודה ברדיאנים בהמשך.
- **מרובעים:** הוכחה שצורה חסומה — שלב שכיח בשאלות הוכחה ב-5 יחידות.

כששולטים בטבלת מדריך השיטה, מפסיקים לגזור מחדש תחת לחץ — **מזהים** סוג בעיה ומפעילים את המשפט הנכון במהלך אחד.""",
    },
    "before_exam": {
        "body_en_md": """**Rapid review checklist:**
- Inscribed angle $= \\frac{1}{2}$ central angle (same arc).
- Angle in semicircle (diameter as chord) $= 90°$.
- Perpendicular from centre bisects chord; half-chord + distance $=$ radius via Pythagoras.
- Intersecting chords / secants: $PA\\cdot PB = PC\\cdot PD$.
- Tangent from outside: $PT^2 = PA\\cdot PB$; tangent $\\perp$ radius at $T$.
- Cyclic quad: $\\angle A + \\angle C = 180°$ (opposite pairs).
- Tangent–chord angle $=$ inscribed angle in alternate segment.

**Last 5 minutes:** Say each bullet once aloud, then solve checkpoint 1 without notes. If you hesitate on power of a point, redo worked example 2 — setup matters more than arithmetic speed.""",
        "body_he_md": """**רשימת חזרה מהירה:**
- זווית חסומה $= \\frac{1}{2}$ זווית מרכזית (אותה קשת).
- זווית בחצי-מעגל (קוטר כמיתר) $= 90°$.
- ניצב ממרכז מחלק מיתר; חצי-מיתר + מרחק $=$ רדיוס בפיתגורס.
- מיתרים/חותכים חוצים: $PA\\cdot PB = PC\\cdot PD$.
- משיק מבחוץ: $PT^2 = PA\\cdot PB$; משיק $\\perp$ רדיוס ב-$T$.
- מרובע חסום: $\\angle A + \\angle C = 180°$ (זוגות נגדיים).
- זווית משיק–מיתר $=$ חסומה בקטע נגדי.

**5 דקות אחרונות:** אמרו כל נקודה בקול, ואז פתרו checkpoint 1 בלי רשימות. אם נתקעים בעוצמת נקודה — חזרו לדוגמה 2; ההכנה חשובה יותר ממהירות החשבון.""",
    },
    "summary": {
        "body_en_md": """**Core toolkit:**
- **Inscribed angle** $= \\frac{1}{2}$ central angle on the same arc; semicircle $\\Rightarrow 90°$.
- **Chords:** centre perpendicular bisects; equal chords $\\Leftrightarrow$ equal distance from centre.
- **Tangents:** $OT \\perp PT$; equal tangent lengths from an external point; $PT^2 = PA\\cdot PB$ with secants.
- **Power of a point:** $PA\\cdot PB = PC\\cdot PD$ for chords or secants through $P$.
- **Cyclic quadrilateral:** opposite angles supplementary; tangent–chord $=$ alternate-segment inscribed angle.

**Takeaway:** Read the diagram first — the correct theorem is usually visible once radii and arcs are marked. You should now match problem wording to a row in the method guide without hesitation.""",
        "body_he_md": """**ערכת ליבה:**
- **זווית חסומה** $= \\frac{1}{2}$ מרכזית על אותה קשת; חצי-מעגל $\\Rightarrow 90°$.
- **מיתרים:** ניצב ממרכז מחלק; מיתרים שווים $\\Leftrightarrow$ מרחק שווה ממרכז.
- **משיקים:** $OT \\perp PT$; אורכי משיקים שווים מבחוץ; $PT^2 = PA\\cdot PB$ עם חותך.
- **עוצמת נקודה:** $PA\\cdot PB = PC\\cdot PD$ למיתרים או חותכים דרך $P$.
- **מרובע חסום:** נגדיות משלימות; משיק–מיתר $=$ חסומה בקטע נגדי.

**מסקנה:** קראו את השרטוט קודם — המשפט הנכון בדרך כלל נראה ברגע שמסמנים רדיוסים וקשתות. כעת תוכלו להתאים ניסוח בעיה לשורה במדריך השיטה בלי היסוס.""",
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": """$AB$ is a diameter, so $\\angle ACB = 90°$ by the angle-in-a-semicircle theorem (central angle on diameter $= 180°$, inscribed $= \\frac{1}{2}\\cdot 180° = 90°$).

In $\\triangle ABC$, angle sum $= 180°$:
$$\\angle ABC = 180° - \\angle ACB - \\angle BAC = 180° - 90° - 35° = 55°$$

**Answer:** $\\angle ABC = 55°$.

**Check:** Acute angles $35°$ and $55°$ with right angle $90°$ sum to $180°$ ✓.""",
        "checkpoint_solution_he": """$AB$ הוא קוטר, ולכן $\\angle ACB = 90°$ לפי משפט זווית בחצי-מעגל (זווית מרכזית על קוטר $= 180°$, חסומה $= \\frac{1}{2}\\cdot 180° = 90°$).

ב-$\\triangle ABC$, סכום זוויות $= 180°$:
$$\\angle ABC = 180° - \\angle ACB - \\angle BAC = 180° - 90° - 35° = 55°$$

**תשובה:** $\\angle ABC = 55°$.

**בדיקה:** זוויות $35°$ ו-$55°$ עם $90°$ מסתכמות ל-$180°$ ✓.""",
    },
    "checkpoint_2": {
        "checkpoint_solution_en": """In cyclic quadrilateral $ABCD$, opposite angles are supplementary:
$$\\angle A + \\angle C = 180°$$
$$110° + \\angle C = 180° \\Rightarrow \\angle C = 70°$$

**Answer:** $\\angle C = 70°$.

**Verify:** If $\\angle B + \\angle D = 180°$ as well, the quadrilateral is consistent with being cyclic. A common error is subtracting from $360°$ or pairing adjacent angles instead of opposites.""",
        "checkpoint_solution_he": """במרובע חסום $ABCD$, זוויות נגדיות משלימות:
$$\\angle A + \\angle C = 180°$$
$$110° + \\angle C = 180° \\Rightarrow \\angle C = 70°$$

**תשובה:** $\\angle C = 70°$.

**אימות:** גם $\\angle B + \\angle D = 180°$ במרובע חסום. טעות נפוצה: חיסור מ-$360°$ או שימוש בזוגות שכנות במקום נגדיות.""",
    },
}

EXPLS = {
    1: fmt_expl(
        "In a cyclic quadrilateral, opposite angles are supplementary. So $70° + x = 180°$ gives $x = 110°$. Option $70°$ repeats the given angle (adjacent, not opposite). $140°$ and $180°$ come from doubling or mis-adding.",
        "Scan for 'cyclic' or four points on a circle — that triggers opposite-angle sums. Label vertices in order $ABCD$ so 'opposite' means $A$ vs. $C$ and $B$ vs. $D$.",
        "Choosing $70°$ by symmetry, or adding $70° + 70° = 140°$ as if angles were equal. Adjacent angles in a cyclic quad are generally not equal.",
        "On MCQ cyclic-quad items, the wrong options often include the given angle and its double — eliminate those before calculating $180° - 70°$.",
        "במרובע חסום זוויות נגדיות משלימות. לכן $70° + x = 180°$ נותן $x = 110°$. $70°$ חוזר על הזווית הנתונה (שכנה, לא נגדית). $140°$ ו-$180°$ מגיעים מהכפלה או חיבור שגוי.",
        "חפשו 'חסום' או ארבע נקודות על מעגל — זה מפעיל סכום נגדיות. סמנו קודקודים $ABCD$ כדי ש'נגדית' תהיה $A$ מול $C$.",
        "בחירת $70°$ בגלל סימטריה, או $70° + 70° = 140°$ כאילו הזוויות שוות. שכנות במרובע חסום בדרך כלל לא שוות.",
        "בשאלות אמריקאיות על מרובע חסום, מסיחים לעיתים כוללים את הזווית הנתונה וכפולה — פסלו לפני $180° - 70°$.",
    ),
    2: fmt_expl(
        "The inscribed angle theorem: inscribed $= \\frac{1}{2}$ central on the same arc. Central $120°$ $\\Rightarrow$ inscribed $= 60°$.",
        "Identify whether the question gives central and asks inscribed (halve) or the reverse (double). Here 'central $120°$' and 'inscribed on same arc' $\\Rightarrow$ divide by 2.",
        "Answering $120°$ (confusing the two types) or $240°$ (doubling instead of halving). Also using major-arc central $240°$ when the inscribed vertex is on the major arc subtending the minor $120°$ arc.",
        "Write 'inscribed = ½ central' on your formula sheet margin — Bagrut geometry sections often stack three angle questions in a row; the pattern repeats.",
        "משפט הזווית החסומה: חסומה $= \\frac{1}{2}$ מרכזית על אותה קשת. מרכזית $120°$ $\\Rightarrow$ חסומה $= 60°$.",
        "זהו אם נותנים מרכזית ומבקשים חסומה (חלקו ב-2) או להפך (הכפילו). כאן 'מרכזית $120°$' ו'חסומה על אותה קשת' $\\Rightarrow$ חלקו ב-2.",
        "תשובה $120°$ (בלבול בין הסוגים) או $240°$ (הכפלה במקום חלוקה). גם שימוש במרכזית $240°$ על הקשת הגדולה כשהקודקוד על הקשת הגדולה הנשען על קשת $120°$ קטנה.",
        "כתבו 'חסומה = ½ מרכזית' בשוליים — בגאומטריה בבגרות לעיתים שלוש שאלות זווית ברצף; הדפוס חוזר.",
    ),
    3: fmt_expl(
        "Perpendicular from centre bisects chord: half-chord $= 8\\;\\text{cm}$. Right triangle with legs $8$ and $6$ gives $r = \\sqrt{64+36} = 10\\;\\text{cm}$.",
        "Chord + distance from centre $\\Rightarrow$ draw the perpendicular radius to the chord — it creates a right triangle with hypotenuse $r$, legs $6$ and half-chord.",
        "Using full chord $16$ with $6$ in Pythagoras without halving first. Or subtracting $16 - 6 = 10$ by luck without the right triangle justification.",
        "Always halve the chord before Pythagoras. Bagrut diagrams sometimes omit the right-angle mark at the foot of the perpendicular — add it yourself.",
        "ניצב ממרכז מחלק מיתר: חצי-מיתר $= 8\\;\\text{ס\"מ}$. משולש ישר-זוויתי עם רגלות $8$ ו-$6$ נותן $r = \\sqrt{64+36} = \\sqrt{100} = 10\\;\\text{ס\"מ}$ — זה הרדיוס המבוקש.",
        "מיתר + מרחק ממרכז $\\Rightarrow$ שרטטו ניצב ממרכז למיתר — נוצר משולש ישר-זוויתי עם יתר $r$, רגלות $6$ (מרחק) ו-$8$ (חצי-מיתר). זהו המסלול הסטנדרטי בבגרות.",
        "שימוש במיתר $16$ מלא עם $6$ בפיתגורס בלי חלוקה ל-$8$ קודם. או $16 - 6 = 10$ במזל בלי הנמקת משולש ישר-זוויתי וניצב ממרכז.",
        "תמיד חלקו מיתר לפני פיתגורס. בשרטוטי בגרות לפעמים חסר סימן זווית ישרה ברגל הניצב — הוסיפו אותו בעצמכם וסמנו חצי-מיתר במפורש.",
    ),
    4: fmt_expl(
        "Opposite angles in cyclic $PQRS$: $\\angle P + \\angle R = 180°$. So $\\angle R = 180° - 85° = 95°$.",
        "Letter order $PQRS$ around the quadrilateral: opposite of $P$ is $R$, opposite of $Q$ is $S$. Supplementary pairs are $(P,R)$ and $(Q,S)$.",
        "Subtracting from $360°$ or pairing $P$ with $Q$ (adjacent). Also answering $85°$ assuming all angles equal.",
        "Underline the vertex letters in cyclic-quad word problems — opposite is two letters apart in the cyclic order.",
        "נגדיות במרובע חסום $PQRS$: $\\angle P + \\angle R = 180°$. לכן $\\angle R = 180° - 85° = 95°$ — זו הזווית הנגדית ל-$\\angle P$, לא שכנה.",
        "סדר אותיות $PQRS$ סביב המרובע: נגדית ל-$P$ היא $R$, ל-$Q$ היא $S$. זוגות משלימים: $(P,R)$ ו-$(Q,S)$. סמנו את המרובע בכיוון השעון לפני חישוב.",
        "חיסור מ-$360°$ או זיווג $P$ עם $Q$ (שכנות). גם $85°$ בהנחה שכל הזוויות שוות — במרובע חסום רק נגדיות משלימות, לא שכנות.",
        "הדגישו אותיות קודקודים בשרטוט — נגדית היא שתי אותיות הלאה בסדר המעגלי. בבגרות, כתבו במפורש $\\angle P + \\angle R = 180°$ לפני הציבור.",
    ),
    5: fmt_expl(
        "Tangent $\\perp$ radius at $T$: $\\triangle OPT$ is right at $T$. $r^2 = OP^2 - PT^2 = 169 - 144 = 25$, so $r = 5\\;\\text{cm}$.",
        "External point + tangent length + distance to centre $\\Rightarrow$ Pythagoras with $OP$ as hypotenuse, $PT$ and $r$ as legs. Never use $OP - PT$.",
        "Using $13 - 12 = 1$ or adding $13 + 12$. Forgetting the right angle at tangency and treating $OP$ as a leg.",
        "Memorize the 5-12-13 triple — it appears often with tangent problems. Check $5^2 + 12^2 = 13^2$ before submitting.",
        "משיק $\\perp$ רדיוס ב-$T$: $\\triangle OPT$ ישר-זוויתי ב-$T$. $r^2 = OP^2 - PT^2 = 169 - 144 = 25$, ולכן $r = 5\\;\\text{ס\"מ}$. זהו הרדיוס, לא המרחק $OP$.",
        "נקודה חיצונית + אורך משיק + מרחק למרכז $\\Rightarrow$ פיתגורס עם $OP$ כיתר, $PT$ ו-$r$ כרגליים. שרטטו $OT \\perp PT$ לפני כתיבת המשוואה — לעולם לא $OP - PT$.",
        "שימוש ב-$13 - 12 = 1$ או חיבור $13 + 12$ במקום ריבועים. שכחת זווית ישרה בנקודת השקה וטיפול ב-$OP$ כרגל במקום יתר.",
        "שיננו שלישייה 5-12-13 — מופיעה הרבה עם משיקים. בדקו $5^2 + 12^2 = 13^2$ לפני הגשה; הציבה חוזרת מ-$r$ ל-$PT$ מאמתת את התשובה.",
    ),
    6: fmt_expl(
        "Intersecting chords: $PA\\cdot PB = PC\\cdot PD$. Here $3\\times 9 = 27 = 4\\times PD$, so $PD = 6.75$. Full chord $CD = 4 + 6.75 = 10.75\\;\\text{cm}$.",
        "Label intersection $P$ and write all four segments. Multiply the two pieces of one chord, set equal to product on the other chord, solve for the unknown fourth segment.",
        "Using $AB = 12$ instead of segments $3$ and $9$. Or finding $PD$ but forgetting the question also asks for $CD = PC + PD$.",
        "When a question asks for two lengths, box both answers — partial answers lose points even if $PD$ is correct.",
        "מיתרים חוצים: $PA\\cdot PB = PC\\cdot PD$. כאן $3\\times 9 = 27 = 4\\times PD$, ולכן $PD = 6.75$. מיתר מלא $CD = PC + PD = 4 + 6.75 = 10.75\\;\\text{ס\"מ}$.",
        "סמנו חיתוך $P$ וכתבו ארבעה קטעים: $PA$, $PB$, $PC$, $PD$. הכפילו שני חלקי מיתר אחד, שוו למכפלה במיתר השני, ואז פתרו לקטע הרביעי.",
        "שימוש ב-$AB = 12$ במקום קטעים $3$ ו-$9$ מ-$P$. מציאת $PD$ בלבד בלי $CD = PC + PD$ כשהשאלה מבקשת גם את אורך המיתר $CD$.",
        "כשמבקשים שני אורכים, סמנו שניהם בבירור — תשובה חלקית מורידה נקודות גם אם $PD$ נכון. אימות: $3\\times9 = 4\\times6.75 = 27$.",
    ),
    7: fmt_expl(
        "Inscribed angle $40°$ on arc $BC$ $\\Rightarrow$ central angle on same arc $= 2\\times 40° = 80°$. Arc measure in degrees equals central angle, so arc $BC = 80°$.",
        "Going from inscribed to arc/central requires **doubling**, not halving. The question asks for arc as central angle measure — they are equal numerically.",
        "Answering $40°$ (leaving inscribed unchanged) or $20°$ (halving again). Confusing arc length in cm with arc measure in degrees.",
        "Keywords 'arc in degrees' or 'central angle' signal double the inscribed angle. Draw a quick central angle at $O$ to avoid direction errors.",
        "זווית חסומה $40°$ על קשת $BC$ $\\Rightarrow$ מרכזית על אותה קשת $= 2\\times 40° = 80°$. מידת קשת במעלות שווה לזווית מרכזית, ולכן קשת $BC = 80°$.",
        "מחסומה לקשת/מרכזית צריך **הכפלה**, לא חלוקה. השאלה מבקשת קשת כמידת מרכזית — מספרית הן שוות.",
        "תשובה $40°$ (השארת חסומה) או $20°$ (חלוקה נוספת). בלבול אורך קשת בס\"מ עם מידה במעלות.",
        "מילות מפתח 'קשת במעלות' או 'זווית מרכזית' מצביעות על הכפלה. שרטטו מרכזית ב-$O$ למניעת טעויות.",
    ),
    8: fmt_expl(
        "Let $\\angle BAC$ and $\\angle BDC$ be inscribed on the same arc $BC$. Each equals $\\frac{1}{2}\\angle BOC$ for the same central angle, so $\\angle BAC = \\angle BDC$.",
        "Proof template: name both inscribed angles, identify the shared arc, invoke inscribed $= \\frac{1}{2}$ central once — both equal the same half, hence equal.",
        "Proving with arc lengths in cm or claiming angles are equal 'because they look the same' without citing the theorem. Using different arcs for the two angles.",
        "One-line proofs earn partial credit if they state the theorem explicitly: 'Inscribed angles on arc $BC$ equal half $\\angle BOC$.' Practice writing that sentence under timed conditions.",
        "תהיינה $\\angle BAC$ ו-$\\angle BDC$ חסומות על אותה קשת $BC$. כל אחת $= \\frac{1}{2}\\angle BOC$ לאותה מרכזית, ולכן $\\angle BAC = \\angle BDC$.",
        "תבנית הוכחה: שמות שתי חסומות, קשת משותפת, חסומה $= \\frac{1}{2}$ מרכזית פעם אחת — שתיהן שוות לאותו חצי.",
        "הוכחה עם אורכי קשת בס\"מ או 'נראות שוות' בלי משפט. שימוש בקשתות שונות לשתי הזוויות.",
        "הוכחה בשורה אחת עם ציטוט המשפט מרוויחה נקודות: 'חסומות על קשת $BC$ = חצי $\\angle BOC$.' תרגלו כתיבה בזמן מוגבל.",
    ),
}

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Solution:** Central angle $120°$ subtends the same arc as the inscribed angle. By the inscribed angle theorem, inscribed $= \\frac{1}{2} \\times 120° = 60°$.\n\n**Check:** Doubling back gives $2 \\times 60° = 120°$ ✓.",
        "solution_he": "**פתרון:** זווית מרכזית $120°$ נשענת על אותה קשת כמו הזווית החסומה. לפי משפט הזווית החסומה: חסומה $= \\frac{1}{2} \\times 120° = 60°$.\n\n**בדיקה:** הכפלה חזרה: $2 \\times 60° = 120°$ ✓.",
    },
    "e2": {
        "solution_en": "**Solution:** Perpendicular from centre bisects chord: half-chord $= 8\\;\\text{cm}$. Right triangle with legs $8$ and $6$:\n$$r = \\sqrt{8^2 + 6^2} = \\sqrt{100} = 10\\;\\text{cm}$$\n\n**Check:** $8^2 + 6^2 = 10^2$ ✓.",
        "solution_he": "**פתרון:** ניצב ממרכז מחלק מיתר: חצי-מיתר $= 8\\;\\text{ס\"מ}$. משולש ישר-זוויתי עם רגלות $8$ ו-$6$:\n$$r = \\sqrt{8^2 + 6^2} = \\sqrt{100} = 10\\;\\text{ס\"מ}$$\n\n**בדיקה:** $8^2 + 6^2 = 10^2$ ✓.",
    },
    "e3": {
        "solution_en": "**Solution:** Opposite angles in cyclic $PQRS$ are supplementary:\n$$\\angle P + \\angle R = 180° \\Rightarrow \\angle R = 180° - 85° = 95°$$\n\n**Check:** $85° + 95° = 180°$ ✓.",
        "solution_he": "**פתרון:** במרובע חסום זוויות נגדיות משלימות:\n$$\\angle P + \\angle R = 180° \\Rightarrow \\angle R = 180° - 85° = 95°$$\n\n**בדיקה:** $85° + 95° = 180°$ ✓.",
    },
    "e4": {
        "solution_en": "**Solution:** Tangent $\\perp$ radius at $T$, so $\\triangle OPT$ is right at $T$:\n$$r = \\sqrt{PO^2 - PT^2} = \\sqrt{169 - 144} = 5\\;\\text{cm}$$\n\n**Check:** $5^2 + 12^2 = 13^2$ ✓.",
        "solution_he": "**פתרון:** משיק $\\perp$ רדיוס ב-$T$, ולכן $\\triangle OPT$ ישר-זוויתי ב-$T$:\n$$r = \\sqrt{PO^2 - PT^2} = \\sqrt{169 - 144} = 5\\;\\text{ס\"מ}$$\n\n**בדיקה:** $5^2 + 12^2 = 13^2$ ✓.",
    },
    "e5": {
        "solution_en": "**Solution:** Intersecting chords — power of a point:\n$$PA \\cdot PB = PC \\cdot PD \\Rightarrow 3 \\times 9 = 4 \\times PD \\Rightarrow PD = 6.75$$\nFull chord: $CD = PC + PD = 4 + 6.75 = 10.75\\;\\text{cm}$.\n\n**Check:** $27 = 4 \\times 6.75$ ✓.",
        "solution_he": "**פתרון:** מיתרים חוצים — עוצמת נקודה:\n$$PA \\cdot PB = PC \\cdot PD \\Rightarrow 3 \\times 9 = 4 \\times PD \\Rightarrow PD = 6.75$$\nמיתר מלא: $CD = PC + PD = 4 + 6.75 = 10.75\\;\\text{ס\"מ}$.\n\n**בדיקה:** $27 = 4 \\times 6.75$ ✓.",
    },
    "e6": {
        "solution_en": "**Solution:** Inscribed angle $40°$ on arc $BC$ $\\Rightarrow$ central angle $= 2 \\times 40° = 80°$. Arc measure in degrees equals the central angle, so arc $BC = 80°$.\n\n**Check:** Halving $80°$ returns $40°$ ✓.",
        "solution_he": "**פתרון:** זווית חסומה $40°$ על קשת $BC$ $\\Rightarrow$ מרכזית $= 2 \\times 40° = 80°$. מידת קשת במעלות שווה לזווית מרכזית, ולכן קשת $BC = 80°$.\n\n**בדיקה:** חלוקת $80°$ ב-2 מחזירה $40°$ ✓.",
    },
    "e7": {
        "solution_en": "**Proof:** Let $\\angle BAC$ and $\\angle BDC$ be inscribed on the same arc $BC$. Each equals $\\frac{1}{2}\\angle BOC$ for the same central angle, so $\\angle BAC = \\angle BDC$.\n\n**Check:** Both angles reference arc $BC$ and the same central angle ✓.",
        "solution_he": "**הוכחה:** תהיינה $\\angle BAC$ ו-$\\angle BDC$ חסומות על אותה קשת $BC$. כל אחת $= \\frac{1}{2}\\angle BOC$ לאותה מרכזית, ולכן $\\angle BAC = \\angle BDC$.\n\n**בדיקה:** שתי הזוויות נשענות על קשת $BC$ ועל אותה מרכזית ✓.",
    },
    "e8": {
        "solution_en": "**Solution:** Cyclic quadrilateral — opposite angles supplementary:\n$$3x + (x + 60°) = 180° \\Rightarrow 4x = 120° \\Rightarrow x = 30°$$\nSo $\\angle A = 90°$ and $\\angle C = 90°$.\n\n**Check:** $90° + 90° = 180°$ ✓.",
        "solution_he": "**פתרון:** מרובע חסום — נגדיות משלימות:\n$$3x + (x + 60°) = 180° \\Rightarrow 4x = 120° \\Rightarrow x = 30°$$\nלכן $\\angle A = 90°$ ו-$\\angle C = 90°$.\n\n**בדיקה:** $90° + 90° = 180°$ ✓.",
    },
    "e9": {
        "solution_en": "**Solution:** External secants — power of a point:\n$$PA \\cdot PB = PC \\cdot PD \\Rightarrow 5 \\times 12 = 4 \\times PD \\Rightarrow PD = 15$$\n\n**Check:** $60 = 4 \\times 15$ ✓.",
        "solution_he": "**פתרון:** חותכים חיצוניים — עוצמת נקודה:\n$$PA \\cdot PB = PC \\cdot PD \\Rightarrow 5 \\times 12 = 4 \\times PD \\Rightarrow PD = 15$$\n\n**בדיקה:** $60 = 4 \\times 15$ ✓.",
    },
    "e10": {
        "solution_en": "**Proof (centre inside angle):** Draw diameter $AD$ from vertex $A$. Isosceles triangles give $\\angle BOD = 2\\angle OAB$ and $\\angle COD = 2\\angle OAC$. Summing: $\\angle BOC = 2(\\angle OAB + \\angle OAC) = 2\\angle BAC$.\n\n**Check:** Each half-angle doubles to the central angle ✓.",
        "solution_he": "**הוכחה (מרכז בתוך הזווית):** שרטטו קוטר $AD$ מקודקוד $A$. משולשים שווי-שוקיים נותנים $\\angle BOD = 2\\angle OAB$ ו-$\\angle COD = 2\\angle OAC$. סיכום: $\\angle BOC = 2(\\angle OAB + \\angle OAC) = 2\\angle BAC$.\n\n**בדיקה:** כל חצי-זווית מוכפל לזווית מרכזית ✓.",
    },
    "e11": {
        "solution_en": "**Solution:** Perpendicular from centre bisects chord: half-chord $= 4$. Distance from centre:\n$$d = \\sqrt{r^2 - 4^2} = \\sqrt{25 - 16} = 3$$\n\n**Check:** $3^2 + 4^2 = 5^2$ ✓.",
        "solution_he": "**פתרון:** ניצב ממרכז מחלק מיתר: חצי-מיתר $= 4$. מרחק מהמרכז:\n$$d = \\sqrt{r^2 - 4^2} = \\sqrt{25 - 16} = 3$$\n\n**בדיקה:** $3^2 + 4^2 = 5^2$ ✓.",
    },
    "e12": {
        "solution_en": "**Solution:** Tangent–chord angle theorem: angle between tangent and chord $= 30°$ equals the inscribed angle in the alternate segment. That inscribed angle subtends arc $AB$, so central angle on arc $AB = 2 \\times 30° = 60°$.\n\n**Check:** Halving $60°$ returns the tangent–chord angle ✓.",
        "solution_he": "**פתרון:** משפט זווית משיק–מיתר: הזווית בין משיק למיתר $= 30°$ שווה לזווית החסומה בקטע הנגדי. הזווית החסומה נשענת על קשת $AB$, ולכן מרכזית על קשת $AB = 2 \\times 30° = 60°$.\n\n**בדיקה:** חלוקת $60°$ ב-2 מחזירה את זווית המשיק–מיתר ✓.",
    },
    "e13": {
        "solution_en": "**Proof:** A rectangle has four right angles ($90°$). By the angle-in-a-semicircle theorem, each diagonal is a diameter of the circumscribed circle. Both diagonals of a rectangle are equal, so all four vertices lie on one circle with that diameter.\n\n**Check:** Opposite angles sum to $180°$ — the rectangle is cyclic ✓.",
        "solution_he": "**הוכחה:** למלבן ארבע זוויות ישרות ($90°$). לפי משפט זווית בחצי-מעגל, כל אלכסון הוא קוטר של מעגל חסום. שני אלכסוני מלבן שווים, ולכן כל ארבע הקודקודים על מעגל אחד.\n\n**בדיקה:** נגדיות מסתכמות ל-$180°$ — המלבן חסום ✓.",
    },
}

QUESTION_ANSWERS = {
    2: ["60°", "60", "Inscribed = half central = 60°"],
    3: ["10\\;\\text{cm}", "10 cm", "10"],
    4: ["95°", "95"],
    5: ["5\\;\\text{cm}", "5 cm", "5"],
    6: ["6.75", "PD = 6.75", "CD = 10.75", "10.75"],
    7: ["80°", "80"],
    8: [
        "Both inscribed angles subtend the same arc. By the inscribed angle theorem, each equals half the central angle of that arc. So both equal the same value.",
        "Each equals half the central angle on arc BC",
    ],
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
        "Euclidean circle geometry: inscribed and central angles, chord and tangent theorems, "
        "power of a point, tangent–chord angles, and cyclic quadrilaterals — with Bagrut-style proofs and calculations."
    )
    data["summary_he"] = (
        "גאומטריית מעגל אוקלידית: זוויות חסומות ומרכזיות, משפטי מיתר ומשיק, "
        "עוצמת נקודה, זוויות משיק–מיתר ומרובעים חסומים — עם הוכחות וחישובים בסגנון בגרות."
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

    for sec in data["sections"]:
        if sec.get("kind") == "exercise_set":
            for ex in sec.get("exercises", []):
                eid = ex.get("id")
                if eid in EXERCISE_SOLUTIONS:
                    ex.update(EXERCISE_SOLUTIONS[eid])

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]
        if ord_ in QUESTION_ANSWERS:
            payload = q.setdefault("answer_payload", {})
            payload["acceptable_answers"] = QUESTION_ANSWERS[ord_]
            payload["case_sensitive"] = False

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
