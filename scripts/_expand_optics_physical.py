#!/usr/bin/env python3
"""Expand optics_physical.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/optics_physical.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "worked_example": {"en": 130, "he": 110},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
    "before_exam": {"en": 90, "he": 75},
    "summary": {"en": 70, "he": 60},
}


def word_count(text):
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def hebrew_char_ratio(text):
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def hebrew_body_weak(body_he, body_en):
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    if hebrew_char_ratio(he) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


PATCHES = {
    "we1_en": """**Given:** Monochromatic light with $\\lambda = 600$ nm passes through a double slit with separation $d = 0.2$ mm. The screen is at distance $L = 2$ m. Find the fringe spacing $\\Delta y$ between adjacent bright fringes.

This is the standard Bagrut setup: identify $\\Delta y = \\lambda L/d$ before substituting numbers.

### Move 1: Convert all lengths to meters
$\\lambda = 600 \\times 10^{-9}$ m, $d = 0.2 \\times 10^{-3}$ m, $L = 2$ m. Never mix mm and m in the same fraction without converting first.

### Move 2: Apply fringe-spacing formula
$$\\Delta y = \\frac{\\lambda L}{d} = \\frac{600 \\times 10^{-9} \\cdot 2}{0.2 \\times 10^{-3}} = \\frac{1.2 \\times 10^{-6}}{2 \\times 10^{-4}} = 6 \\times 10^{-3}\\text{ m}.$$

### Move 3: Convert to millimeters
$\\Delta y = 6$ mm. Visible fringes in a classroom demo are typically a few millimeters apart — this answer is physically reasonable.

### Move 4: Optional prediction
If $d$ were halved to $0.1$ mm with the same $\\lambda$ and $L$, spacing would double to $12$ mm because $\\Delta y \\propto 1/d$.

**Why this order matters:** Write the formula first, then units — graders look for $\\Delta y = \\lambda L/d$ even when arithmetic is correct.

**Answer:** $\\Delta y = 6$ mm.

**Self-check:** If you double $d$, spacing halves to 3 mm — proportional reasoning confirms the formula direction.""",

    "we1_he": """**נתון:** אור מונוכרומטי עם $\\lambda = 600$ nm עובר דרך סדק כפול עם מרחק $d = 0.2$ mm. המסך במרחק $L = 2$ m. מצאו את מרווח הפסים $\\Delta y$ בין פסים בהירים סמוכים.

זו תצורת בגרות קלאסית: זיהוי $\\Delta y = \\lambda L/d$ לפני הצבת מספרים.

### צעד 1: המרת כל האורכים למטרים
$\\lambda = 600 \\times 10^{-9}$ m, $d = 0.2 \\times 10^{-3}$ m, $L = 2$ m. אל תערבבו mm ו-m באותו שבר בלי המרה.

### צעד 2: יישום נוסחת מרווח הפסים
$$\\Delta y = \\frac{\\lambda L}{d} = \\frac{600 \\times 10^{-9} \\cdot 2}{0.2 \\times 10^{-3}} = \\frac{1.2 \\times 10^{-6}}{2 \\times 10^{-4}} = 6 \\times 10^{-3}\\text{ m}.$$

### צעד 3: המרה למילימטרים
$\\Delta y = 6$ mm. פסים נראים בניסוי כיתתי — בדרך כלל מרווח של כמה מילימטרים; התשובה סבירה פיזית.

### צעד 4: חיזוי (אופציונלי)
אם $d$ היה מתחצה ל-$0.1$ mm, המרווח היה מתכפה ל-12 mm כי $\\Delta y \\propto 1/d$.

**למה הסדר חשוב:** כתבו קודם את הנוסחה, אחר כך יחידות — הבודקים מחפשים $\\Delta y = \\lambda L/d$ גם כשהחשבון נכון.

**תשובה:** $\\Delta y = 6$ mm.

**בדיקה עצמית:** אם מכפילים $d$, המרווח יחצה ל-3 mm — יחסיות מאשרת את כיוון הנוסחה.""",

    "cp1_en": """Use $\\Delta y = \\lambda L/d$ with consistent SI units.

**Step 1:** $\\lambda = 500 \\times 10^{-9}$ m, $d = 0.5 \\times 10^{-3}$ m, $L = 1$ m.

**Step 2:** $\\Delta y = (500 \\times 10^{-9})(1)/(0.5 \\times 10^{-3}) = 500 \\times 10^{-9}/5 \\times 10^{-4} = 10^{-3}$ m.

**Step 3:** $\\Delta y = 1$ mm.

**Check:** Larger $\\lambda$ or $L$ increases spacing; larger $d$ decreases it — all match the formula. **Answer:** $1$ mm.""",

    "cp1_he": """השתמשו ב-$\\Delta y = \\lambda L/d$ עם יחידות SI עקביות.

**שלב 1:** $\\lambda = 500 \\times 10^{-9}$ m, $d = 0.5 \\times 10^{-3}$ m, $L = 1$ m.

**שלב 2:** $\\Delta y = (500 \\times 10^{-9})(1)/(0.5 \\times 10^{-3}) = 10^{-3}$ m.

**שלב 3:** $\\Delta y = 1$ mm.

**בדיקה:** $\\lambda$ או $L$ גדולים יותר מגדילים מרווח; $d$ גדול מקטין — תואם לנוסחה. **תשובה:** $1$ mm.""",

    "we2_en": """**Same setup as Example 1:** $\\lambda = 600$ nm, $d = 0.2$ mm, $L = 2$ m. Find the position of the **3rd bright fringe** ($m = 3$) from the central maximum.

Bright fringes sit at $y_m = m\\lambda L/d$. You can compute directly or use $y_3 = 3\\Delta y$ from Example 1.

### Move 1: Write the fringe-position formula
$$y_m = \\frac{m\\lambda L}{d}.$$

### Move 2: Substitute $m = 3$
$$y_3 = \\frac{3 \\times 600 \\times 10^{-9} \\times 2}{0.2 \\times 10^{-3}} = \\frac{3.6 \\times 10^{-6}}{2 \\times 10^{-4}} = 0.018\\text{ m}.$$

### Move 3: Verify with spacing
From Example 1, $\\Delta y = 6$ mm, so $y_3 = 3 \\times 6\\text{ mm} = 18$ mm ✓. Both methods must agree — if they do not, recheck $m$ or units.

### Move 4: Interpret the result
The third bright fringe lies $18$ mm from the central maximum, on either side of center (symmetry of the pattern).

**Exam tip:** Central fringe is $m = 0$; first side fringe is $m = 1$, not $m = 0$ again.

**Answer:** $y_3 = 18$ mm.

**Extension:** The 4th bright fringe would sit at $y_4 = 4 \\times 6 = 24$ mm — each order adds one $\\Delta y$.""",

    "we2_he": """**אותה תצורה כדוגמה 1:** $\\lambda = 600$ nm, $d = 0.2$ mm, $L = 2$ m. מצאו את מיקום **הפס הבהיר השלישי** ($m = 3$) מהמקסימום המרכזי.

פסים בהירים ב-$y_m = m\\lambda L/d$. אפשר לחשב ישירות או $y_3 = 3\\Delta y$ מדוגמה 1.

### צעד 1: כתיבת נוסחת מיקום הפס
$$y_m = \\frac{m\\lambda L}{d}.$$

### צעד 2: הצבה עם $m = 3$
$$y_3 = \\frac{3 \\times 600 \\times 10^{-9} \\times 2}{0.2 \\times 10^{-3}} = 0.018\\text{ m}.$$

### צעד 3: אימות דרך מרווח
מדוגמה 1, $\\Delta y = 6$ mm, ולכן $y_3 = 3 \\times 6\\text{ mm} = 18$ mm ✓. שתי השיטות חייבות להתאים — אם לא, בדקו $m$ או יחידות.

### צעד 4: פרשנות
הפס הבהיר השלישי נמצא $18$ mm מהמרכז, משני צדי המקסימום (סימטריה של הדפוס).

**טיפ לבחינה:** הפס המרכזי הוא $m = 0$; הפס הצדדי הראשון הוא $m = 1$.

**תשובה:** $y_3 = 18$ mm.

**הרחבה:** הפס הבהיר הרביעי ב-$y_4 = 4 \\times 6 = 24$ mm — כל סדר מוסיף $\\Delta y$ אחד.""",

    "cp2_en": """A bright fringe means $y_m = m\\lambda L/d$. If the problem says \"bright fringe at $y = 4$ mm\" without an order, assume the **first** side fringe ($m = 1$) unless stated otherwise.

**Step 1:** $y_1 = 4 \\times 10^{-3}$ m, $d = 0.1 \\times 10^{-3}$ m, $L = 0.5$ m.

**Step 2:** $\\lambda = y_1 d / L = (4 \\times 10^{-3})(0.1 \\times 10^{-3})/0.5$.

**Step 3:** $\\lambda = 4 \\times 10^{-7}$ m $= 800$ nm.

**Check:** Substitute back: $y_1 = \\lambda L/d = (8 \\times 10^{-7})(0.5)/(10^{-4}) = 4$ mm ✓. **Answer:** $800$ nm.""",

    "cp2_he": """פס בהיר מקיים $y_m = m\\lambda L/d$. אם נאמר \"פס בהיר ב-$y = 4$ mm\" ללא סדר — הניחו **ראשון** ($m = 1$) אלא אם צוין אחרת.

**שלב 1:** $y_1 = 4 \\times 10^{-3}$ m, $d = 0.1 \\times 10^{-3}$ m, $L = 0.5$ m.

**שלב 2:** $\\lambda = y_1 d / L = (4 \\times 10^{-3})(0.1 \\times 10^{-3})/0.5$.

**שלב 3:** $\\lambda = 8 \\times 10^{-7}$ m $= 800$ nm.

**בדיקה:** $y_1 = \\lambda L/d = 4$ mm ✓. **תשובה:** $800$ nm.""",

    "we3_en": """**A soap film** ($n = 1.33$) in air reflects white light. Find the **minimum thickness** for **constructive** reflection of green light, $\\lambda = 532$ nm (in air).

Thin-film reflection always starts with phase-shift counting, then the optical path $2nt$.

### Move 1: Count phase shifts (air | soap | air)
- Outer reflection (air → film, higher $n$): **180° shift**.
- Inner reflection (film → air, lower $n$): **no shift**.
- Net: **one shift** → constructive when $2nt = (m + \\tfrac{1}{2})\\lambda$.

### Move 2: Minimum order
For smallest nonzero $t$, use $m = 0$: $2nt = \\lambda/2$.

### Move 3: Solve for $t$
$$t = \\frac{\\lambda}{4n} = \\frac{532}{4 \\times 1.33} = \\frac{532}{5.32} \\approx 100\\text{ nm}.$$

**Why $m = 0$ is allowed here:** One net phase shift means the $m = 0$ condition gives $t = \\lambda/(4n) > 0$, not zero thickness.

**Answer:** $t \\approx 100$ nm.

**Physical picture:** This quarter-wave thickness is why soap films first show weak reflection at the top of a bubble before colors appear lower down where $t$ is larger.""",

    "we3_he": """**פילם סבון** ($n = 1.33$) באוויר מחזיר אור לבן. מצאו את **עובי המינימום** להחזרה **מסדרת** של אור ירוק, $\\lambda = 532$ nm (באוויר).

הפרעה בפילם דק מתחילה בספירת הסטות פאזה, ואז מסלול אופטי $2nt$.

### צעד 1: ספירת הסטות (אוויר | סבון | אוויר)
- החזרה חיצונית (אוויר → פילם, $n$ גבוה): **הסטה 180°**.
- החזרה פנימית (פילם → אוויר, $n$ נמוך): **ללא הסטה**.
- נטו: **הסטה אחת** → מסדרת כש-$2nt = (m + \\tfrac{1}{2})\\lambda$.

### צעד 2: סדר מינימלי
לעובי לא-אפסי קטן ביותר, $m = 0$: $2nt = \\lambda/2$.

### צעד 3: פתרון עבור $t$
$$t = \\frac{\\lambda}{4n} = \\frac{532}{4 \\times 1.33} \\approx 100\\text{ nm}.$$

**למה $m = 0$ מותר:** הסטה נטו אחת נותנת $t = \\lambda/(4n) > 0$, לא עובי אפס.

**תשובה:** $t \\approx 100$ nm.

**תמונה פיזיקלית:** עובי \"רבע גל\" זה מסביר למה בראש הבועה החזרה חלשה לפני שמופיעים צבעים למטה, שם $t$ גדול יותר.""",

    "method_en": """| Problem type | First step | Key formula |
|---|---|---|
| Fringe spacing | Convert to meters; identify $L$, $d$, $\\lambda$ | $\\Delta y = \\lambda L/d$ |
| Fringe position | Assign correct order $m$ (bright vs dark) | $y_m = m\\lambda L/d$ or dark: $(m+\\tfrac{1}{2})\\lambda L/d$ |
| Find $\\lambda$ from data | Invert spacing or position formula | $\\lambda = \\Delta y \\cdot d/L$ |
| Thin film thickness | Count phase shifts at each reflection | Constructive/destructive per net shifts |
| Single-slit spread | Identify slit width $a$ | First minimum: $a\\sin\\theta = \\lambda$ |

**Double-slit workflow:** (1) List given quantities in SI. (2) Decide whether the question asks spacing, position, or $\\lambda$. (3) Check small-angle validity ($L \\gg d$). (4) Substitute and verify units.

**Thin-film workflow:** (1) Sketch layers (air/film/glass). (2) Mark $\\lambda/2$ shifts at higher-$n$ reflections. (3) Write $2nt$ condition. (4) Use smallest valid $m$.

**Exam tip:** On combined problems, separate double-slit arithmetic from phase-shift reasoning — mixing them early causes wrong $m$ values.""",

    "method_he": """| סוג בעיה | צעד ראשון | נוסחה מרכזית |
|---|---|---|
| מרווח פסים | המרה למטרים; זיהוי $L$, $d$, $\\lambda$ | $\\Delta y = \\lambda L/d$ |
| מיקום פס | קביעת סדר $m$ (בהיר/כהה) | $y_m = m\\lambda L/d$ או כהה: $(m+\\tfrac{1}{2})\\lambda L/d$ |
| מציאת $\\lambda$ | היפוך נוסחת מרווח/מיקום | $\\lambda = \\Delta y \\cdot d/L$ |
| עובי פילם דק | ספירת הסטות בהחזרות | מסדרת/הרסנית לפי נטו |
| עקיפת סדק יחיד | זיהוי רוחב $a$ | מינימום ראשון: $a\\sin\\theta = \\lambda$ |

**סדק כפול:** (1) רשימת נתונים ב-SI. (2) האם שואלים מרווח, מיקום או $\\lambda$? (3) בדיקת זווית קטנה ($L \\gg d$). (4) הצבה ואימות יחידות.

**פילם דק:** (1) סקיצת שכבות. (2) סימון הסטות $\\lambda/2$. (3) כתיבת תנאי $2nt$. (4) $m$ מינימלי תקף.

**טיפ לבחינה:** הפרידו חשבון סדק כפול מספירת הסטות — ערבוב מוקדם גורם ל-$m$ שגוי.""",

    "pitfall_en": """1. **Forgetting $n$ in thin film:** The round-trip **optical path** inside the film is $2nt$, not $2t$. Light slows in the medium; each pass adds $nt$, not $t$.

2. **Phase-shift confusion:** Only reflections at a **higher-$n$** side of the interface get a $\\lambda/2$ shift. Drawing the layer stack prevents swapping constructive and destructive conditions.

3. **Wrong fringe order:** The central bright fringe is $m = 0$. The first dark fringe beside center uses $m = 0$ in $d\\sin\\theta = (m + \\tfrac{1}{2})\\lambda$, not $m = 1$ for bright formulas.

4. **Large-angle misuse:** $y_m = m\\lambda L/d$ assumes $\\sin\\theta \\approx y/L$. If $d$ is not much smaller than $L$, use $d\\sin\\theta = m\\lambda$ instead.

5. **Unit inconsistency:** Mixing mm for $d$ with meters for $L$ without conversion is the top arithmetic error on Bagrut optics items.

**Example misconception:** Thin film path difference is $2t$ not $2nt$.

**Fix:** Always multiply geometric thickness by $n$ for optical path: $2nt$.""",

    "pitfall_he": """1. **שכחת $n$ בפילם דק:** מסלול אופטי הלוך-חזור הוא $2nt$, לא $2t$. האור מאט במדיום; כל מעבר תורם $nt$, לא $t$.

2. **בלבול בהסטות פאזה:** רק החזרה מצד **$n$ גבוה יותר** נותנת הסטה של $\\lambda/2$. סקיצת שכבות מונעת החלפה בין מסדרת להרסנית.

3. **סדר פס שגוי:** הפס המרכזי הבהיר הוא $m = 0$. הפס הכהה הראשון ליד המרכז משתמש ב-$m = 0$ ב-$d\\sin\\theta = (m + \\tfrac{1}{2})\\lambda$, לא $m = 1$ של נוסחת בהיר.

4. **שימוש בקירוב זווית קטנה שלא במקום:** $y_m = m\\lambda L/d$ דורש $\\sin\\theta \\approx y/L$. אם $d$ לא קטן בהרבה מ-$L$, השתמשו ב-$d\\sin\\theta = m\\lambda$.

5. **יחידות לא עקביות:** ערבוב mm ל-$d$ עם מטרים ל-$L$ בלי המרה — טעות החשבון הנפוצה ביותר.

**דוגמת טעות:** מסלול בפילם דק הוא $2t$ ולא $2nt$.

**תיקון:** תמיד הכפילו עובי גיאומטרי ב-$n$: $2nt$.""",

    "before_en": """- **Double slit:** $\\Delta y = \\lambda L/d$; bright at $y_m = m\\lambda L/d$; dark uses half-integer path difference on angle form.
- **Thin film:** Sketch layers → count $\\lambda/2$ shifts → write $2nt$ condition → pick smallest valid $m$.
- **Single slit:** First minimum $a\\sin\\theta = \\lambda$; wider slit → narrower central spot.
- **Polarization:** Transverse wave; polarizer blocks one component — qualitative only on most Bagrut items.
- **Units:** Convert mm ↔ m before any division; keep $\\lambda$ in meters when using SI formulas.

**Last review:** Derive $\\Delta y$ from $d\\sin\\theta = m\\lambda$ once aloud, then solve one checkpoint without notes.""",

    "before_he": """- **סדק כפול:** $\\Delta y = \\lambda L/d$; בהיר ב-$y_m = m\\lambda L/d$; כהה — הפרש חצי-שלם בצורת זווית.
- **פילם דק:** סקיצה → ספירת הסטות $\\lambda/2$ → תנאי $2nt$ → $m$ מינימלי תקף.
- **סדק יחיד:** מינימום ראשון $a\\sin\\theta = \\lambda$; סדק רחב → כתם מרכזי צר.
- **קיטוב:** גל רוחבי; מקטין חוסם רכיב — איכותי ברוב שאלות הבגרות.
- **יחידות:** המירו mm ↔ m לפני חילוק; $\\lambda$ במטרים בנוסחאות SI.

**חזרה אחרונה:** גזרו $\\Delta y$ מ-$d\\sin\\theta = m\\lambda$ פעם אחת בקול, ואז פתרו checkpoint בלי רשימות.""",

    "summary_en": """- **Interference:** Path difference $m\\lambda$ → constructive; $(m + \\tfrac{1}{2})\\lambda$ → destructive (before counting extra phase shifts).
- **Double slit:** $\\Delta y = \\lambda L/d$ links wavelength, geometry, and what you measure on the screen.
- **Thin film:** Optical path $2nt$ plus reflection phase shifts determine reflected color and antireflection design.
- **Diffraction:** $\\lambda/a$ sets angular spread; complements interference when openings are small.
- **Polarization:** Confirms light is transverse; connects to glare reduction.

**Takeaway:** Read the problem — slits, film layers, or single aperture — then pick the matching row in the method guide before calculating.""",

    "summary_he": """- **הפרעה:** הפרש מסלול $m\\lambda$ → מסדרת; $(m + \\tfrac{1}{2})\\lambda$ → הרסנית (לפני הסטות נוספות).
- **סדק כפול:** $\\Delta y = \\lambda L/d$ מקשר אורך גל, גיאומטריה ומדידה על המסך.
- **פילם דק:** מסלול $2nt$ והסטות פאזה קובעים צבע בהחזרה וציפוי אנטי-רפלקטיבי.
- **עקיפה:** $\\lambda/a$ קובע פיזור זוויתי; משלימה הפרעה כשפתחים קטנים.
- **קיטוב:** מאשר שהאור רוחבי; קשור להפחתת סנוור.

**מסקנה:** קראו את השאלה — סדקים, שכבות או פתח יחיד — ובחרו שורה במדריך השיטה לפני חישוב.""",

    "why_en": """Physical optics is where **wave physics meets everyday light**. The same $\\lambda$ you measure in a double-slit lab also explains oil-slick colors and camera lens coatings. Mastering $\\Delta y = \\lambda L/d$ and thin-film phase rules prepares you for photoelectric effect and quantum optics in `concept:modern_physics_intro`.

**You will use this to unlock:**
- `concept:modern_physics_intro` **Quantum Physics Basics** (prerequisite)

**Builds on:**
- `concept:waves_basics` **Mechanical Waves** — superposition, path difference
- `concept:optics_geometric` **Geometric Optics** — rays fail when $\\lambda$ is not negligible

**Why it matters for exams:** Bagrut rewards multi-step problems combining unit conversion, correct fringe order, and phase-shift reasoning — not formula recall alone.""",

    "why_he": """אופטיקה גלית היא המקום שבו **פיזיקת גלים פוגשת אור יומיומי**. אותו $\\lambda$ שנמדד בניסוי סדק כפול מסביר גם צבעי שמן על מים וציפויי עדשות. שליטה ב-$\\Delta y = \\lambda L/d$ ובכללי הסטות בפילם דק מכינה לאפקט פוטואלקטרי ולאופטיקה קוונטית ב-`concept:modern_physics_intro`.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:modern_physics_intro` **מבוא לפיזיקה קוונטית** (דרישת קדם)

**מבוסס על:**
- `concept:waves_basics` **גלים מכניים** — חפיפה, הפרש מסלול
- `concept:optics_geometric` **אופטיקה גיאומטרית** — קרניים נכשלות כש-$\\lambda$ לא זניח

**למה זה חשוב לבחינות:** הבגרות מעריכה שילוב המרת יחידות, סדר פס נכון וספירת הסטות — לא רק שינון נוסחאות.""",
}


EXPLANATIONS = {
    1: {
        "en": """**Why this is correct:**
Fringe spacing follows $\\Delta y = \\lambda L/d$, which is **directly proportional to $L$**. Tripling the screen distance triples the spacing between adjacent bright fringes — option \"Triples.\"

**How to think about it:**
Before calculating, identify which symbol the question changes. Here only $L$ scales; $\\lambda$ and $d$ stay fixed, so the ratio $\\Delta y \\propto L$ is immediate. This is a proportionality check, not a full numeric problem.

**Common slip:**
Students invert the relationship and pick \"Thirds\" because they confuse \"farther screen\" with \"fringe closer together.\" Another trap: \"Unchanged\" — treating $L$ as irrelevant even though it appears explicitly in the formula.

**Exam tip:**
Bagrut MCQs often test proportional reasoning without numbers. Write $\\Delta y \\propto L/d$ on scratch paper and circle the variable that changed.""",
        "he": """**למה זה נכון:**
מרווח הפסים $\\Delta y = \\lambda L/d$ — **יחס ישר ל-$L$**. הכפלת מרחק המסך פי 3 מכפילה את המרווח בין פסים בהירים סמוכים — \"מוכפל פי 3\".

**איך לחשוב על זה:**
לפני חישוב, זהו איזה סמל משתנה. כאן רק $L$ — $\\lambda$ ו-$d$ קבועים, ולכן $\\Delta y \\propto L$ מיד. זו בדיקת יחס, לא חישוב מלא.

**טעות נפוצה:**
היפוך היחס ובחירת \"פי 1/3\" — בלבול \"מסך רחוק\" עם \"פס קרוב\". מלכודת נוספת: \"ללא שינוי\" — התעלמות מ-$L$ למרות שהוא בנוסחה.

**טיפ לבחינה:**
שאלות בגרות בודקות יחסים בלי מספרים. כתבו $\\Delta y \\propto L/d$ וסמנו את המשתנה שהשתנה.""",
    },
    2: {
        "en": """**Why this is correct:**
Apply $\\Delta y = \\lambda L/d$ with SI units: $\\lambda = 450 \\times 10^{-9}$ m, $L = 1.5$ m, $d = 0.3 \\times 10^{-3}$ m. Then $\\Delta y = (450 \\times 10^{-9})(1.5)/(3 \\times 10^{-4}) = 2.25 \\times 10^{-3}$ m $= 2.25$ mm.

**How to think about it:**
Convert **all** lengths before dividing. A quick estimate: numerator $\\sim 10^{-6}$, denominator $\\sim 10^{-4}$, giving millimeter-scale spacing — reasonable for visible light lab setups.

**Common slip:**
Using $d = 0.3$ mm directly without $10^{-3}$, yielding an answer off by $10^3$. Another error: multiplying $\\lambda$ and $d$ instead of dividing by $d$.

**Exam tip:**
After computing $\\Delta y$, compare to typical values (1–10 mm). If you get meters or micrometers, re-check unit conversion first.""",
        "he": """**למה זה נכון:**
יישום $\\Delta y = \\lambda L/d$ ב-SI: $\\lambda = 450 \\times 10^{-9}$ m, $L = 1.5$ m, $d = 0.3 \\times 10^{-3}$ m. מתקבל $\\Delta y = 2.25 \\times 10^{-3}$ m $= 2.25$ mm.

**איך לחשוב על זה:**
המירו **כל** האורכים לפני חילוק. הערכה: מונה $\\sim 10^{-6}$, מכנה $\\sim 10^{-4}$ — מרווח במילימטרים, סביר בניסוי.

**טעות נפוצה:**
שימוש ב-$d = 0.3$ mm בלי $10^{-3}$ — תשובה שגויה ב-$10^3$. טעות נוספת: כפל $\\lambda$ ב-$d$ במקום חילוק ב-$d$.

**טיפ לבחינה:**
אחרי חישוב $\\Delta y$, השוו ל-1–10 mm. אם יצאו מטרים — בדקו המרת יחידות. כתבו הנוסחה על הטיוטה לפני מספרים.""",
    },
    3: {
        "en": """**Why this is correct:**
Rearrange $\\Delta y = \\lambda L/d$ to $\\lambda = \\Delta y \\cdot d/L$. With $\\Delta y = 2$ mm $= 2 \\times 10^{-3}$ m, $d = 0.4$ mm $= 4 \\times 10^{-4}$ m, $L = 2$ m: $\\lambda = (2 \\times 10^{-3})(4 \\times 10^{-4})/2 = 4 \\times 10^{-7}$ m $= 400$ nm — visible violet/blue light.

**How to think about it:**
When $\\lambda$ is unknown, isolate it algebraically before numbers. Larger measured spacing with fixed $d$ and $L$ implies longer wavelength.

**Common slip:**
Inverting to $\\lambda = \\Delta y \\cdot L/d$ (swapping $d$ and $L$). Another mistake: leaving $\\Delta y$ in mm while $L$ is in meters without converting.

**Exam tip:**
Always express final $\\lambda$ in nm for visible-light problems — graders expect $400$–$700$ nm range as a sanity check.""",
        "he": """**למה זה נכון:**
מ-$\\Delta y = \\lambda L/d$ מתקבל $\\lambda = \\Delta y \\cdot d/L$. עם $\\Delta y = 2 \\times 10^{-3}$ m, $d = 4 \\times 10^{-4}$ m, $L = 2$ m: $\\lambda = 4 \\times 10^{-7}$ m $= 400$ nm — אור נראה.

**איך לחשוב על זה:**
כש-$\\lambda$ לא ידוע — בודדו אלגברית לפני מספרים. מרווח גדול יותר עם $d$ ו-$L$ קבועים ⇒ אורך גל ארוך יותר.

**טעות נפוצה:**
$\\lambda = \\Delta y \\cdot L/d$ — החלפת $d$ ו-$L$. השארת $\\Delta y$ ב-mm בלי המרה.

**טיפ לבחינה:**
הציגו $\\lambda$ ב-nm — טווח 400–700 nm. חזרו על $\\lambda = \\Delta y \\cdot d/L$ לפני הצבה; בדקו שהתוצאה בטווח הנראה.""",
    },
    4: {
        "en": """**Why this is correct:**
From $\\Delta y = \\lambda L/d$, spacing is **inversely proportional to $d$**. Doubling slit separation halves $\\Delta y$ while $\\lambda$ and $L$ stay fixed.

**How to think about it:**
Physically, wider slit spacing reduces the path-difference gradient across the screen, squeezing fringes closer. Write the proportionality, then apply the factor of 2 to $d$.

**Common slip:**
Assuming fringes spread when slits move apart (choosing \"Triples\" or \"Unchanged\"). Students sometimes double $\\Delta y$ instead of halving it.

**Exam tip:**
Proportionality questions appear every year. Memorize $\\Delta y \\propto 1/d$ alongside the full formula — it saves time on MCQs.""",
        "he": """**למה זה נכון:**
מ-$\\Delta y = \\lambda L/d$ המרווח **יחסי הפוך ל-$d$**. הכפלת מרחק הסדקים מחצה את $\\Delta y$ כש-$\\lambda$ ו-$L$ קבועים.

**איך לחשוב על זה:**
מבחינה פיזית, סדקים רחוקים יותר מקטינים את שיפוע הפרש המסלול — פסים צפופים יותר. כתבו יחסיות והחילו הכפלה ב-2 על $d$.

**טעות נפוצה:**
הנחה שפסים מתרחקים כשמרחיבים סדקים. לפעמים מכפילים $\\Delta y$ במקום לחלק.

**טיפ לבחינה:**
שאלות יחסיות חוזרות מדי שנה. $\\Delta y \\propto 1/d$ — כש-$d$ גדל, הפסים **צפופים** יותר. כתבו את היחס לפני בחירה.""",
    },
    5: {
        "en": """**Why this is correct:**
At **near-zero thickness**, the soap film reflects weakly and appears **dark** (nearly black): the single $\\lambda/2$ phase shift from the top reflection makes reflected waves from front and back nearly **destructive** across visible wavelengths. There is no single \"color\" at minimum thickness — color bands appear only where thickness matches constructive conditions for specific $\\lambda$.

**How to think about it:**
Thin-film color is a **local thickness map**, not a pigment. Ask: what interference condition applies at the thinnest top of the bubble before picking a wavelength.

**Common slip:**
Naming one visible color (e.g., \"green\") for zero thickness. Another error: ignoring phase shifts and using $2nt = m\\lambda$ for air-film-air constructive at $t \\to 0$.

**Exam tip:**
Qualitative thin-film questions reward the phrase \"destructive at minimum thickness\" — link it explicitly to one net $\\lambda/2$ shift.""",
        "he": """**למה זה נכון:**
ב**עובי קרוב לאפס**, בועת סבון נראית **כהה (כמעט שחורה)**: הסטת $\\lambda/2$ מההחזרה העליונה גורמת להרסנית כמעט לכל אורכי הגל הנראים. אין \"צבע\" אחד בעובי מינימלי — פסים צבעוניים מופיעים רק כשהעובי מתאים למסדרת עבור $\\lambda$ מסוים.

**איך לחשוב על זה:**
צבע בפילם דק הוא **מפת עובי**, לא pigment. שאלו: איזה תנאי הפרעה בקצה הדק של הבועה?

**טעות נפוצה:**
בחירת צבע נראה אחד (ירוק) בעובי אפס. התעלמות מהסטות ושימוש ב-$2nt = m\\lambda$ ב-$t \\to 0$.

**טיפ לבחינה:**
שאלות איכותיות מעריכות \"הרסנית בעובי מינימלי\" — קשר מפורש להסטה $\\lambda/2$ נטו.""",
    },
    6: {
        "en": """**Why this is correct:**
Oil on air ($n = 1.45$) has **one net phase shift** → constructive reflection: $2nt = (m + \\tfrac{1}{2})\\lambda$, so $\\lambda = 2nt/(m + \\tfrac{1}{2})$. For $t = 150$ nm: $m = 0$ gives $\\lambda = 870$ nm (infrared); $m = 1$ gives $\\lambda = 290$ nm (ultraviolet). **No visible wavelengths** ($400$–$700$ nm) satisfy constructive reflection at this thickness.

**How to think about it:**
Compute $\\lambda$ for successive $m$ and check whether results fall in the visible band. Do not assume $m = 0$ is always the answer the question wants — here it proves absence of visible color.

**Common slip:**
Reporting $870$ nm as \"visible red\" or stopping at $m = 0$ without scanning $m = 1$. Forgetting the $(m + \\tfrac{1}{2})$ factor for air-film-air constructive reflection.

**Exam tip:**
When a problem asks \"for what visible $\\lambda$...\", always compare your answers to $400$–$700$ nm and state clearly if none qualify.""",
        "he": """**למה זה נכון:**
שמן באוויר ($n = 1.45$) — **הסטה נטו אחת** → מסדרת: $2nt = (m + \\tfrac{1}{2})\\lambda$, כלומר $\\lambda = 2nt/(m + \\tfrac{1}{2})$. ל-$t = 150$ nm: $m = 0$ נותן $\\lambda = 870$ nm (IR); $m = 1$ נותן $\\lambda = 290$ nm (UV). **אין אורכי גל נראים** (400–700 nm).

**איך לחשוב על זה:**
חשבו $\\lambda$ ל-$m$ עוקבים ובדקו אם בטווח הנראה. $m = 0$ לא תמיד התשובה — כאן הוא מוכיח שאין צבע נראה.

**טעות נפוצה:**
דיווח 870 nm כ\"אדום נראה\". עצירה ב-$m = 0$ בלי $m = 1$. שכחת $(m + \\tfrac{1}{2})$.

**טיפ לבחינה:**
כששואלים \"לאיזה $\\lambda$ נראה...\" — השוו ל-400–700 nm וציינו אם אין התאמה.""",
    },
    7: {
        "en": """**Why this is correct:**
An antireflection coating minimizes **reflected** intensity. For air | coating ($n = 1.38$) | glass ($n = 1.5$), the Bagrut model uses **one net $\\lambda/2$ phase shift**, so reflected waves cancel when $2nt = (m + \\tfrac{1}{2})\\lambda$. With design $\\lambda = 550$ nm and $m = 0$: $t = \\lambda/(4n) = 550/(4 \\times 1.38) \\approx 99.6$ nm — a classic quarter-wave MgF$_2$ thickness.

**How to think about it:**
State the goal (less reflection = **destructive** interference) before algebra. Quarter-wave coatings always appear as $\\lambda/(4n)$ when one net shift applies.

**Common slip:**
Using $2nt = m\\lambda$ for constructive reflection — that **increases** glare. Another error: using $\\lambda$ inside the film instead of the design wavelength in air.

**Exam tip:**
Label each interface with \"shift\" or \"no shift,\" then write \"destructive → min reflection\" — graders award the setup even if arithmetic slips slightly.""",
        "he": """**למה זה נכון:**
ציפוי אנטי-רפלקטיבי ממזער **החזרה**. לאוויר | ציפוי ($n = 1.38$) | זכוכית ($n = 1.5$), במודל הבגרות **הסטה נטו $\\lambda/2$ אחת**, ולכן $2nt = (m + \\tfrac{1}{2})\\lambda$ להרסנית. עם $\\lambda = 550$ nm ו-$m = 0$: $t = \\lambda/(4n) \\approx 99.6$ nm — עובי \"רבע גל\".

**איך לחשוב על זה:**
הגדירו מטרה (פחות החזרה = **הרסנית**) לפני אלגברה. $t = \\lambda/(4n)$ — תוצאה לשינון.

**טעות נפוצה:**
$2nt = m\\lambda$ למסדרת — **מגביר** סנוור. שימוש ב-$\\lambda$ בתוך הפילם במקום באוויר.

**טיפ לבחינה:**
סמנו \"הרסנית → מינימום החזרה\" לפני $m$. $\\lambda/(4n)$ — זיהוי מיידי של ציפוי רבע-גל.""",
    },
    8: {
        "en": """**Why this is correct:**
$\\Delta y = \\lambda L/d$ shows spacing is **proportional to $L$**. Halving $L$ halves $\\Delta y$: new spacing $= 3\\text{ mm}/2 = 1.5$ mm.

**How to think about it:**
Treat this as scaling: if $\\Delta y_1 = 3$ mm at $L_1$, then $\\Delta y_2 = \\Delta y_1 \\cdot (L_2/L_1) = 3 \\times (1/2)$. No need to know $\\lambda$ or $d$ explicitly.

**Common slip:**
Doubling spacing when $L$ decreases (confusing \"closer screen\" with \"wider fringes\"). Another error: thinking only $d$ affects spacing and leaving answer at 3 mm.

**Exam tip:**
Two-step problems often give one spacing and change a single variable. Set up a ratio before opening the calculator.""",
        "he": """**למה זה נכון:**
$\\Delta y = \\lambda L/d$ — המרווח **יחסי ל-$L$**. חציית $L$ מחצה את $\\Delta y$: מרווח חדש $= 3/2 = 1.5$ mm.

**איך לחשוב על זה:**
scaling: $\\Delta y_2 = \\Delta y_1 \\cdot (L_2/L_1) = 3 \\times (1/2)$. לא חייבים $\\lambda$ או $d$ — רק היחס בין מרחקי מסך. ככל שהמסך קרוב, הפסים צמודים יותר.

**טעות נפוצה:**
הכפלת מרווח כש-$L$ קטן — בלבול \"מסך קרוב\" עם \"פסים רחוקים\". השארת 3 mm מתעלמת מ-$L$ בנוסחה.

**טיפ לבחינה:**
$\\Delta y_2/\\Delta y_1 = L_2/L_1$ — כתבו את היחס לפני מחשבון. כש-$L$ קטן, הפסים **קרובים** יותר למרכז.""",
    },
}


def apply_patches(data):
    for sec in data["sections"]:
        k = sec.get("kind")
        if k == "worked_example":
            n = sec.get("example_number")
            if n == 1:
                sec["body_en_md"] = PATCHES["we1_en"]
                sec["body_he_md"] = PATCHES["we1_he"]
            elif n == 2:
                sec["body_en_md"] = PATCHES["we2_en"]
                sec["body_he_md"] = PATCHES["we2_he"]
            elif n == 3:
                sec["body_en_md"] = PATCHES["we3_en"]
                sec["body_he_md"] = PATCHES["we3_he"]
        elif k == "checkpoint":
            if "0.5" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = PATCHES["cp1_en"]
                sec["checkpoint_solution_he"] = PATCHES["cp1_he"]
            elif "Bright fringe" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = PATCHES["cp2_en"]
                sec["checkpoint_solution_he"] = PATCHES["cp2_he"]
        elif k == "method_guide":
            sec["body_en_md"] = PATCHES["method_en"]
            sec["body_he_md"] = PATCHES["method_he"]
        elif k == "pitfall":
            sec["body_en_md"] = PATCHES["pitfall_en"]
            sec["body_he_md"] = PATCHES["pitfall_he"]
        elif k == "before_exam":
            sec["body_en_md"] = PATCHES["before_en"]
            sec["body_he_md"] = PATCHES["before_he"]
        elif k == "summary":
            sec["body_en_md"] = PATCHES["summary_en"]
            sec["body_he_md"] = PATCHES["summary_he"]
        elif k == "why_matters":
            sec["body_en_md"] = PATCHES["why_en"]
            sec["body_he_md"] = PATCHES["why_he"]

    for q in data["questions"]:
        ord_ = q.get("ord")
        if ord_ in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_]["he"]


def validate(data):
    errors = []
    for sec in data["sections"]:
        k = sec.get("kind")
        if k not in MIN_WORDS:
            continue
        mw = MIN_WORDS[k]
        en_w = word_count(sec.get("body_en_md", ""))
        he_w = word_count(sec.get("body_he_md", ""))
        if en_w < mw["en"]:
            errors.append(f"{k}: EN {en_w} < {mw['en']}")
        if he_w < mw["he"]:
            errors.append(f"{k}: HE {he_w} < {mw['he']}")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{k}: weak Hebrew body")
    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"Q{q.get('ord')} expl_{lang}: {w} words (need 80-150)")
    return errors


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    apply_patches(data)
    errors = validate(data)
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(" ", e)
        sys.exit(1)
    print(f"Wrote {TARGET.name} — all depth gates pass")


if __name__ == "__main__":
    main()
