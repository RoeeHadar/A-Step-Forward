#!/usr/bin/env python3
"""Expand mechanics_makhina.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/mechanics_makhina.json"

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


DEF_EN = """### Kinematics (constant acceleration)
For motion along a line with constant acceleration $a$:
$$v = v_0 + at, \\quad x = x_0 + v_0 t + \\tfrac{1}{2}at^2, \\quad v^2 = v_0^2 + 2a(x-x_0).$$

**Variables:** $x_0, v_0$ = initial position and velocity; $v$ = velocity at time $t$; $a$ = (constant) acceleration. These three equations are equivalent — choose the one that omits your unknown.

**Strategy table:**

| Known | Unknown | Best equation |
|---|---|---|
| $v_0, a, t$ | $v$ or $x$ | $v=v_0+at$ or $x=x_0+v_0 t+\\tfrac{1}{2}at^2$ |
| $v_0, v, a$ | $x$ | $v^2=v_0^2+2a(x-x_0)$ (no time needed) |
| $v_0, v, t$ | $x$ | $x=x_0+\\tfrac{v_0+v}{2}t$ (average velocity) |

### Newton's Second Law (vector form)
$$\\boxed{\\sum \\vec{F} = m\\vec{a}}$$
Sum of all **external** forces on the object = mass × acceleration. Always decompose into components: $\\sum F_x = ma_x$, $\\sum F_y = ma_y$. Draw the FBD before writing any equation.

### Work-Energy Theorem
$$W_{\\text{net}} = \\Delta KE = \\tfrac{1}{2}mv^2 - \\tfrac{1}{2}mv_0^2.$$
Net work done on an object equals the change in its kinetic energy. Include work by friction ($W_f = -f_k d$) when surfaces are rough.

### Conservation of Mechanical Energy (no friction)
$$KE_i + PE_i = KE_f + PE_f \\quad \\Rightarrow \\quad \\tfrac{1}{2}mv_i^2 + mgh_i = \\tfrac{1}{2}mv_f^2 + mgh_f.$$
Valid only when non-conservative forces (friction, applied push) do zero net work.

### Conservation of Momentum
$$\\vec{p}_{\\text{total}} = \\sum m_i \\vec{v}_i = \\text{const} \\quad \\text{(when } \\sum \\vec{F}_{\\text{ext}} = 0\\text{)}.$$
Internal forces (tension, normal between colliding bodies) never change total momentum."""

DEF_HE = """### קינמטיקה (תאוצה קבועה)
לתנועה לאורך קו עם תאוצה קבועה $a$:
$$v = v_0 + at, \\quad x = x_0 + v_0 t + \\tfrac{1}{2}at^2, \\quad v^2 = v_0^2 + 2a(x-x_0).$$

**משתנים:** $x_0, v_0$ = מיקום ומהירות התחלתיים; $v$ = מהירות בזמן $t$; $a$ = תאוצה (קבועה). שלוש המשוואות שקולות — בחרו את זו שמדלגת על הנעלם.

**טבלת אסטרטגיה:**

| ידוע | לא ידוע | משוואה מומלצת |
|---|---|---|
| $v_0, a, t$ | $v$ או $x$ | $v=v_0+at$ או $x=x_0+v_0 t+\\tfrac{1}{2}at^2$ |
| $v_0, v, a$ | $x$ | $v^2=v_0^2+2a(x-x_0)$ (ללא זמן) |
| $v_0, v, t$ | $x$ | $x=x_0+\\tfrac{v_0+v}{2}t$ (מהירות ממוצעת) |

### החוק השני של ניוטון (בוקטורים)
$$\\boxed{\\sum \\vec{F} = m\\vec{a}}$$
סכום כל הכוחות **החיצוניים** על הגוף = מסה × תאוצה. תמיד פרקו לרכיבים: $\\sum F_x = ma_x$, $\\sum F_y = ma_y$. ציירו FBD לפני כתיבת משוואה.

### משפט עבודה-אנרגיה
$$W_{\\text{נטו}} = \\Delta KE = \\tfrac{1}{2}mv^2 - \\tfrac{1}{2}mv_0^2.$$
עבודה נטו על גוף שווה לשינוי באנרגיה הקינטית. כללו עבודת חיכוך ($W_f = -f_k d$) כשיש חיכוך.

### שימור אנרגיה מכנית (ללא חיכוך)
$$KE_i + PE_i = KE_f + PE_f \\quad \\Rightarrow \\quad \\tfrac{1}{2}mv_i^2 + mgh_i = \\tfrac{1}{2}mv_f^2 + mgh_f.$$
תקף רק כשכוחות לא-שמרוריות (חיכוך, דחיפה) לא מבצעות עבודה נטו.

### שימור תנע
$$\\vec{p}_{\\text{כולל}} = \\sum m_i\\vec{v}_i = \\text{קבוע} \\quad (\\sum\\vec{F}_{\\text{חיצוני}}=0).$$
כוחות פנימיים (מתח, נורמלי בין גופים מתנגשים) לא משנים תנע כולל."""

WE1_EN = """**Given:** A car decelerates from $v_0 = 25$ m/s at $a = -5$ m/s² (braking). Find the stopping distance.

### Move 1: Identify knowns and unknowns
$v_0 = 25$ m/s, $a = -5$ m/s², $v_f = 0$ (stopped). We want displacement $x$ (stopping distance). Time is not asked for, so avoid equations involving $t$.

### Move 2: Choose the time-free kinematic equation
We know $v_0$, $v_f$, and $a$ — and want $x$. The equation $v_f^2 = v_0^2 + 2ax$ eliminates time entirely and is the standard choice for braking problems.

### Move 3: Substitute and solve
$$0 = 25^2 + 2(-5)x = 625 - 10x.$$
$$x = \\frac{625}{10} = 62.5 \\text{ m}.$$

### Move 4: Dimensional check
$\\frac{(\\text{m/s})^2}{\\text{m/s}^2} = \\text{m}$. ✓ The units are consistent.

**Answer:** The stopping distance is $\\boxed{62.5}$ m.

**Physical insight:** Doubling speed quadruples stopping distance (since $x \\propto v_0^2$). This quadratic dependence is why speed limits matter far more than most drivers realize — a car at 50 m/s needs four times the stopping distance of one at 25 m/s."""

WE1_HE = """**נתון:** מכונית מאיטה מ-$v_0=25$ מ\"ש עם $a=-5$ מ\"ש² (בלימה). מצאו מרחק עצירה.

### צעד 1: זהו נתונים ונעלם
$v_0=25$ מ\"ש, $a=-5$ מ\"ש², $v_f=0$ (עצירה). רוצים את ההעתק $x$ (מרחק עצירה). הזמן לא נדרש — הימנעו ממשוואות עם $t$.

### צעד 2: בחרו משוואה קינמטית ללא זמן
ידועים $v_0$, $v_f$, $a$ — רוצים $x$. המשוואה $v_f^2=v_0^2+2ax$ מדלגת על זמן לחלוטין — הבחירה הסטנדרטית בבעיות בלימה.

### צעד 3: הציבו ופתרו
$$0=25^2+2(-5)x=625-10x.$$
$$x=\\frac{625}{10}=62.5\\text{ מ'}.$$

### צעד 4: בדיקת מימדים
$\\frac{(\\text{מ/ש})^2}{\\text{מ/ש}^2}=\\text{מ'}$. ✓ היחידות עקביות.

**תשובה:** מרחק העצירה הוא $\\boxed{62.5}$ מ'.

**תובנה פיזיקלית:** הכפלת מהירות מכפילה את מרחק העצירה בארבע ($x\\propto v_0^2$). תלות ריבועית זו מסבירה מדוע הגבלות מהירות קריטיות — מכונית ב-50 מ\"ש צריכה פי ארבעה מרחק עצירה מ-25 מ\"ש."""

WE2_EN = """**Given:** Block A ($m_A = 4$ kg) sits on a frictionless table. It is connected by a massless string over a pulley to block B ($m_B = 2$ kg) hanging vertically. Find the acceleration of the system and the tension $T$ in the string. Take $g = 10$ m/s².

### Move 1: Draw separate FBDs for each block
- Block A (horizontal): tension $T$ to the right is the only horizontal force; normal and weight cancel vertically.
- Block B (vertical): weight $m_B g = 20$ N down, tension $T$ up.

### Move 2: Apply Newton's second law to each body
Let $a$ be the common acceleration magnitude (A moves right, B moves down — connected by an inextensible string).
- Block A: $\\sum F_x = T = m_A a$ → $T = 4a$.
- Block B: $\\sum F_y = m_B g - T = m_B a$ → $20 - T = 2a$.

### Move 3: Solve the simultaneous equations
Substitute $T = 4a$ into the B equation:
$$20 - 4a = 2a \\implies 20 = 6a \\implies a = \\frac{20}{6} = \\frac{10}{3} \\approx 3.33 \\text{ m/s}^2.$$

### Move 4: Find tension
$$T = 4a = 4 \\times \\frac{10}{3} = \\frac{40}{3} \\approx 13.3 \\text{ N}.$$

**Check:** For block B: net force $= 20 - 13.3 = 6.7$ N $= m_B a = 2 \\times 3.33$. ✓

**Key insight:** The lighter hanging mass drives the system — its weight provides the net force that accelerates both blocks. Tension is always less than the hanging weight when the system accelerates."""

WE2_HE = """**נתון:** גוש A ($m_A=4$ ק\"ג) על שולחן חלק. מחובר בחוט דרך גלגלת לגוש B ($m_B=2$ ק\"ג) התלוי אנכית. מצאו תאוצת המערכת ומתח $T$ בחוט. $g=10$ מ\"ש².

### צעד 1: ציירו FBD נפרד לכל גוש
- גוש A (אופקי): מתח $T$ ימינה — הכוח האופקי היחיד; נורמלי ומשקל מתבטלים אנכית.
- גוש B (אנכי): משקל $m_B g=20$ N כלפי מטה, מתח $T$ כלפי מעלה.

### צעד 2: יישמו חוק שני של ניוטון לכל גוף
תהי $a$ תאוצה משותפת (A ימינה, B למטה — מחוברים בחוט בלתי-מתכווץ).
- גוש A: $\\sum F_x = T = m_A a$ → $T=4a$.
- גוש B: $\\sum F_y = m_B g - T = m_B a$ → $20-T=2a$.

### צעד 3: פתרו את המשוואות
הציבו $T=4a$:
$$20-4a=2a \\Rightarrow 20=6a \\Rightarrow a=\\frac{10}{3}\\approx3.33\\text{ מ\"ש}^2.$$

### צעד 4: מצאו מתח
$$T=4\\times\\frac{10}{3}=\\frac{40}{3}\\approx13.3\\text{ N}.$$

**בדיקה:** לגוש B: כוח שקול $=20-13.3=6.7$ N $=m_B a=2\\times3.33$. ✓

**תובנה:** המסה התלויה הקלה מניעה את המערכת — משקלה מספק את הכוח השקול שמאיץ את שני הגושים. המתח תמיד קטן ממשקל הגוש התלוי כשהמערכת מאיצה."""

WE3_EN = """**Given:** A block of mass $m$ slides from rest at the top of a frictionless quarter-circle ramp of radius $R$. Find its speed at the bottom using energy conservation.

### Move 1: Define reference height
Set $h = 0$ at the bottom of the ramp. At the top, the block is at height $h = R$ (the radius of the quarter circle equals the vertical drop).

### Move 2: Write the energy conservation equation
Since the ramp is frictionless, no mechanical energy is lost to heat:
$$KE_i + PE_i = KE_f + PE_f.$$
At the top: $v_i = 0$ (starts from rest), $h_i = R$.
At the bottom: $h_f = 0$.
$$\\frac{1}{2}mv_i^2 + mgR = \\frac{1}{2}mv_f^2 + 0.$$

### Move 3: Substitute initial conditions
With $v_i = 0$, gravitational PE converts entirely to kinetic energy:
$$mgR = \\frac{1}{2}mv_f^2.$$

### Move 4: Solve — mass cancels
Just like free-fall, the result is independent of mass:
$$v_f^2 = 2gR \\implies \\boxed{v_f = \\sqrt{2gR}}.$$

### Move 5: Physical interpretation
This is exactly the speed gained by an object falling a vertical height $R$ from rest. The shape of the path (quarter circle, straight incline, spiral) does not matter — only the height change matters for frictionless problems. This is the power of energy methods over force methods.

**Note:** If the ramp were not frictionless, subtract the work done by friction: $\\frac{1}{2}mv_f^2 = mgR - f \\cdot s$, where $s$ = arc length of the path."""

WE3_HE = """**נתון:** גוש ממסה $m$ גולש ממנוחה מראש רמפת רבע-עיגול חלקה ברדיוס $R$. מצאו מהירותו בתחתית בעזרת שימור אנרגיה.

### צעד 1: הגדירו גובה ייחוס
נציב $h=0$ בתחתית. בראש, הגוש בגובה $h=R$ (רדיוס רבע העיגול שווה לירידה האנכית).

### צעד 2: כתבו משוואת שימור אנרגיה
מאחר שהרמפה חלקה, אין אובדן אנרגיה מכנית לחום:
$$KE_i + PE_i = KE_f + PE_f.$$
בראש: $v_i=0$, $h_i=R$. בתחתית: $h_f=0$.
$$\\frac{1}{2}mv_i^2 + mgR = \\frac{1}{2}mv_f^2.$$

### צעד 3: הציבו תנאי התחלה
עם $v_i=0$, אנרגיה פוטנציאלית כבידתית מתהפכת לחלוטין לאנרגיה קינטית:
$$mgR = \\frac{1}{2}mv_f^2.$$

### צעד 4: פתרו — המסה מתצמצמת
כמו בנפילה חופשית, התוצאה בלתי-תלויה במסה:
$$v_f^2=2gR \\Rightarrow \\boxed{v_f=\\sqrt{2gR}}.$$

### צעד 5: פרשנות פיזיקלית
זוהי בדיוק המהירות שמשיגה גוף בנפילה חופשית מגובה $R$. צורת המסלול (רבע עיגול, מדרון ישר, ספירלה) לא משנה — רק הפרש הגבהים משנה בבעיות ללא חיכוך. זוהי עוצמת שיטות האנרגיה.

**הערה:** אם הרמפה לא חלקה, חסרו את עבודת החיכוך: $\\frac{1}{2}mv_f^2 = mgR - f \\cdot s$, כאשר $s$ = אורך הקשת."""

CHK1_EN = """**(a) Time to maximum height**

At the peak, vertical velocity is zero. Using $v = v_0 - gt$ (taking upward as positive, $g = 10$ m/s² downward):
$$0 = 20 - 10t \\implies t = \\frac{20}{10} = \\boxed{2 \\text{ s}}.$$

**(b) Maximum height**

Method 1 — kinematics: $h = v_0 t - \\tfrac{1}{2}gt^2 = 20(2) - \\tfrac{1}{2}(10)(4) = 40 - 20 = \\boxed{20 \\text{ m}}$.

Method 2 — time-free: $v^2 = v_0^2 - 2gh \\Rightarrow 0 = 400 - 20h \\Rightarrow h = 20$ m. Both methods agree. ✓

**Check:** The ball returns to ground in $4$ s total (symmetry), and lands at $-20$ m/s — equal and opposite to the launch speed."""

CHK1_HE = """**(א) זמן עד גובה מקסימלי**

בשיא, מהירות אנכית אפס. $v = v_0 - gt$ (מעלה חיובי, $g=10$ מ\"ש²):
$$0 = 20 - 10t \\Rightarrow t = \\boxed{2 \\text{ ש'}}.$$

**(ב) גובה מקסימלי**

שיטה 1 — קינמטיקה: $h = v_0 t - \\tfrac{1}{2}gt^2 = 40 - 20 = \\boxed{20 \\text{ מ'}}$.

שיטה 2 — ללא זמן: $v^2 = v_0^2 - 2gh \\Rightarrow h = 20$ מ'. שתי השיטות מסכימות. ✓

**בדיקה:** הכדור חוזר לקרקע ב-$4$ ש' (סימטריה), ונוחת ב-$-20$ מ\"ש — שווה ונגדי למהירות השיגור."""

CHK2_EN = """**Method 1 — Kinematics along the incline**

Acceleration down a frictionless incline: $a = g\\sin30° = 10 \\times 0.5 = 5$ m/s².
From rest over distance $s = 4$ m: $v^2 = v_0^2 + 2as = 0 + 2(5)(4) = 40$.
$$v = \\sqrt{40} = 2\\sqrt{10} \\approx \\boxed{6.32 \\text{ m/s}}.$$

**Method 2 — Energy conservation**

Vertical height drop: $h = s\\sin30° = 4 \\times 0.5 = 2$ m.
$\\tfrac{1}{2}mv^2 = mgh \\Rightarrow v = \\sqrt{2gh} = \\sqrt{2(10)(2)} = \\sqrt{40}$. Same answer. ✓

**Why both work:** On a frictionless surface, the path length along the incline and the vertical drop contain the same physics — energy methods ignore the path shape entirely."""

CHK2_HE = """**שיטה 1 — קינמטיקה לאורך המדרון**

תאוצה במדרון חלק: $a = g\\sin30° = 5$ מ\"ש².
ממנוחה על מרחק $s=4$ מ': $v^2 = 2(5)(4) = 40$.
$$v = \\sqrt{40} = 2\\sqrt{10} \\approx \\boxed{6.32 \\text{ מ/ש}}.$$

**שיטה 2 — שימור אנרגיה**

ירידה אנכית: $h = s\\sin30° = 2$ מ'.
$\\tfrac{1}{2}mv^2 = mgh \\Rightarrow v = \\sqrt{2gh} = \\sqrt{40}$. אותה תשובה. ✓

**למה שתיהן עובדות:** במשטח חלק, אורך המסלול והירידה האנכית מכילים את אותה פיזיקה — שיטות אנרגיה מתעלמות מצורת המסלול."""

PITFALL_HE = """1. **כוחות חסרים ב-FBD.** תמיד בדקו: משקל, נורמלי, חיכוך, כוחות מופעלים, מתח. כבידה תמיד פועלת אלא אם צוין אחרת.

2. **מוסכמת סימנים שגויה.** הגדירו כיוון חיובי בתחילה והיצמדו לו. אם הגדרתם למטה חיובי, $a=+g$ בנפילה חופשית וכתבו $mg - N = ma$.

3. **שימוש באנרגיה כשנדרש מתח או כוח.** אנרגיה נותנת מהירויות, לא כוחות פנימיים. למתח, השתמשו בחוק שני לכל גוף בנפרד.

4. **אי-כליאת חיכוך בבעיות אנרגיה.** אם יש חיכוך, $KE_i+PE_i\\neq KE_f+PE_f$. כללו $-f_k d$ (עבודת חיכוך שלילית).

5. **בלבול מסה ומשקל.** $m$ ב-ק\"ג; $W=mg$ ב-N. כתיבת '$F=5$ ק\"ג' היא שגיאה — כוח תמיד בניווטון."""

WHY_EN = """Classical mechanics is the gateway to every university physics course — from oscillations and waves to electromagnetism and thermodynamics. The problem-solving framework you build here (FBD → equations → solve → check) repeats in every subsequent topic.

**You will use this to unlock:**
- `concept:uni_kinematics` **University Kinematics** — rigorous vector treatment and multi-body systems.
- `concept:uni_work_energy` **Work & Energy** — energy methods as an alternative to force analysis.
- `concept:uni_newtonian_mechanics` **Newtonian Mechanics** — the full vector formalism expected in first-year physics.

**Why it matters for exams:** Makhina (preparatory) physics exams reward systematic methodology over memorized formulas. Examiners deduct heavily for missing FBDs or wrong sign conventions. When you study, always ask: \"Can I solve this with both force and energy methods?\" That dual approach is what separates strong students from average ones."""

WHY_HE = """מכניקה קלאסית היא שער לכל קורס פיזיקה אוניברסיטאי — מתנודות וגלים לאלקטרומגנטיות ותרמודינמיקה. מסגרת פתרון הבעיות שתבנו כאן (FBD → משוואות → פתרון → בדיקה) חוזרת בכל נושא המשך.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:uni_kinematics` **קינמטיקה אוניברסיטאית** — טיפול וקטורי קפדני ומערכות מרובות גופים.
- `concept:uni_work_energy` **עבודה ואנרגיה** — שיטות אנרגיה כחלופה לניתוח כוחות.
- `concept:uni_newtonian_mechanics` **מכניקה ניוטונית** — הפורמליזם הווקטורי המלא בשנה א'.

**למה זה חשוב לבחינות:** בחינות מכינה מעריכות מתודולוגיה שיטתית על פני שינון נוסחאות. בוחנים מורידים נקודות על FBD חסר או סימנים שגויים. בזמן לימוד, שאלו: \"האם אוכל לפתור גם בכוחות וגם באנרגיה?\" גישה כפולה זו מפרידה בין תלמידים חזקים לחלשים."""

BEFORE_HE = """### נוסחאות חיוניות
- קינמטיקה: $v=v_0+at$; $x=v_0t+\\frac{1}{2}at^2$; $v^2=v_0^2+2ax$
- חוק שני: $\\sum F=ma$ (לפי רכיב)
- משקל: $W=mg$; נורמלי במדרון: $N=mg\\cos\\theta$
- חיכוך: $f_k=\\mu_k N$; $f_s\\leq\\mu_s N$
- אנרגיה קינטית: $\\frac{1}{2}mv^2$; פוטנציאלית: $mgh$
- שימור אנרגיה (ללא חיכוך): $\\frac{1}{2}mv_i^2+mgh_i=\\frac{1}{2}mv_f^2+mgh_f$
- תנע: $p=mv$; $\\sum p=\\text{קבוע}$ (מערכת מבודדת)

### תבניות שאלות אופייניות
1. **קינמטיקה:** נתונים 3 מתוך $\\{v_0,v,a,t,x\\}$ — מצאו את הרביעי או החמישי.
2. **FBD + ניוטון:** ציירו, תייגו, כתבו $\\sum F=ma$ לכל כיוון.
3. **שימור אנרגיה:** זהו $h_i, h_f, v_i, v_f$; כתבו ופתרו.
4. **מדרון עם חיכוך:** פרקו כוחות, יישמו $F=ma$ לאורך המדרון.
5. **מערכת מרובת גופים:** משוואה אחת לכל גוף, פתרו במקביל.

### קriterion ניקוד
- FBD: 30% כוחות נכונים, 30% תיוג, 40% משוואות.
- אנרגיה: 40% איברי אנרגיה, 40% אלגebra, 20% תשובה."""

SUMMARY_EN = """- **Kinematics (const $a$):** $v=v_0+at$; $x=v_0t+\\frac{1}{2}at^2$; $v^2=v_0^2+2ax$. Choose the equation that omits your unknown.
- **Newton's 2nd:** $\\sum\\vec{F}=m\\vec{a}$ — always draw FBD first, then apply per component.
- **Incline:** $a=g(\\sin\\theta-\\mu_k\\cos\\theta)$ (with friction, sliding down). Resolve weight into $mg\\sin\\theta$ (parallel) and $mg\\cos\\theta$ (perpendicular).
- **Energy conservation:** $KE_i+PE_i=KE_f+PE_f$ (frictionless only). Mass cancels in speed-from-height problems.
- **Work-energy theorem:** $W_{\\text{net}}=\\Delta KE$. Include $-f_k d$ when friction is present.
- **Energy with friction:** $\\frac{1}{2}mv_f^2=\\frac{1}{2}mv_i^2+mgh_i-mgh_f-f_k d$.
- **Momentum:** $p=mv$; conserved when $\\sum F_{\\text{ext}}=0$. Internal forces never change total momentum.
- **Problem-solving protocol:** Read → FBD → coordinates → equations → solve → dimensional check."""

SUMMARY_HE = """- **קינמטיקה (תאוצה קבועה):** $v=v_0+at$; $x=v_0t+\\frac{1}{2}at^2$; $v^2=v_0^2+2ax$. בחרו משוואה שמדלגת על הנעלם.
- **חוק שני:** $\\sum\\vec{F}=m\\vec{a}$ — תמיד ציירו FBD קודם, ואז לפי רכיבים.
- **מדרון:** $a=g(\\sin\\theta-\\mu_k\\cos\\theta)$ (עם חיכוך, בירידה). פרקו משקל ל-$mg\\sin\\theta$ (מקביל) ו-$mg\\cos\\theta$ (ניצב).
- **שימור אנרגיה:** $KE_i+PE_i=KE_f+PE_f$ (רק ללא חיכוך). מסה מתצמצמת בבעיות מהירות-מגובה.
- **משפט עבודה-אנרגיה:** $W_{\\text{נטו}}=\\Delta KE$. כללו $-f_k d$ כשיש חיכוך.
- **אנרגיה עם חיכוך:** $\\frac{1}{2}mv_f^2=\\frac{1}{2}mv_i^2+mgh_i-mgh_f-f_k d$.
- **תנע:** $p=mv$; נשמר כש-$\\sum F_{\\text{חיצוני}}=0$. כוחות פנימיים לא משנים תנע כולל.
- **פרוטוקול פתרון:** קריאה → FBD → קואורדינטות → משוואות → פתרון → בדיקת מימדים."""

EXPLS = {
    1: fmt_expl(
        "The train starts from rest ($v_0 = 0$), so the displacement equation simplifies to $x = \\tfrac{1}{2}at^2$. Substituting $a = 2$ m/s² and $t = 10$ s gives $x = \\tfrac{1}{2}(2)(100) = 100$ m.",
        "When an object starts from rest, only two of the four kinematic variables matter: acceleration and time. The $\\tfrac{1}{2}at^2$ form is the direct path — no need for the velocity equation first.",
        "Using $x = v_0 t + \\tfrac{1}{2}at^2$ but forgetting that $v_0 = 0$, leading to an extra term. Another trap: using $v = v_0 + at$ to find velocity (20 m/s) and stopping there without computing distance.",
        "Always list knowns before choosing an equation. If $v_0 = 0$, write it explicitly — examiners often set this up to test whether you recognize the simplified form.",
        "הרכבת מתחילה ממנוחה ($v_0=0$), לכן $x=\\tfrac{1}{2}at^2$. הצבה: $a=2$ מ\"ש², $t=10$ ש' → $x=\\tfrac{1}{2}(2)(100)=100$ מ'.",
        "כשגוף מתחיל ממנוחה, רק תאוצה וזמן קובעים. $\\tfrac{1}{2}at^2$ הוא הנתיב הישיר — אין צורך למצוא מהירות קודם.",
        "שימוש ב-$x=v_0 t+\\tfrac{1}{2}at^2$ בלי לזכור ש-$v_0=0$, או עצירה אחרי מציאת $v=20$ מ\"ש בלי לחשב מרחק.",
        "רשמו נתונים לפני בחירת משוואה. אם $v_0=0$, כתבו במפורש — בוחנים בודקים אם מזהים את הצורה הפשוטה. בדקו: $v=at=20$ מ\"ש ואז $x=100$ מ'.",
    ),
    2: fmt_expl(
        "Newton's second law in scalar form: $a = F/m$. With net force $F = 30$ N and mass $m = 10$ kg, $a = 30/10 = 3$ m/s². The frictionless floor means the normal force and weight cancel vertically — only the horizontal push matters.",
        "This is the simplest application of $\\sum F = ma$: one net force, one acceleration. Identify the direction of motion, confirm no opposing friction, then divide force by mass.",
        "Dividing mass by force ($10/30$) instead of force by mass. Another error: subtracting weight ($mg = 100$ N) from the applied force even though the floor supports the box vertically.",
        "Always state units in your answer: m/s² for acceleration, not m/s (that's velocity). A quick sanity check: 30 N on 10 kg should give a modest acceleration — 3 m/s² is reasonable.",
        "חוק שני בסקalar: $a=F/m$. כוח שקול $F=30$ N, מסה $m=10$ ק\"ג → $a=30/10=3$ מ\"ש². רצפה חלקה = נורמלי ומשקל מתבטלים אנכית.",
        "יישום פשוט של $\\sum F=ma$: כוח שקול אחד, תאוצה אחת. וודאו שאין חיכוך, וחלקו כוח במסה.",
        "חילוק מסה בכוח ($10/30$) במקום כוח במסה. או חיסור משקל ($mg=100$ N) מהכוח למרות שהרצפה תומכת בגוף.",
        "ציינו יחידות: מ\"ש² לתאוצה, לא מ\"ש. בדיקת שפיות: 30 N על 10 ק\"ג → תאוצה מתונה — 3 מ\"ש² הגיוני.",
    ),
    3: fmt_expl(
        "Gravitational potential energy is $PE = mgh$. With $m = 2$ kg, $g = 10$ m/s², and $h = 5$ m: $PE = 2 \\times 10 \\times 5 = 100$ J. The reference level (ground) is implicit — only height differences matter.",
        "PE depends on vertical height above your chosen zero level. Here the ground is the reference, so $h = 5$ m is measured directly. Mass, gravity, and height all multiply together.",
        "Using $PE = \\tfrac{1}{2}mv^2$ (kinetic energy formula) instead of $mgh$. Another trap: forgetting that $g = 10$ m/s² (not 9.8) as specified in the problem.",
        "PE problems on makhina exams often give $g = 10$ for clean arithmetic. Always check whether the problem states $g = 10$ or $g = 9.8$ before substituting.",
        "אנרגיה פוטנציאלית כבידתית: $PE=mgh$. $m=2$ ק\"ג, $g=10$ מ\"ש², $h=5$ מ' → $PE=2\\times10\\times5=100$ J. רמת ייחוס (קרקע) מרומזת — רק הפרשי גובה משנים.",
        "PE תלוי בגובה אנכי מעל רמת האפס שבחרתם. כאן הקרקע = ייחוס, $h=5$ מ'. שלושת הגורמים — מסה, כבידה וגובה — מוכפלים יחד.",
        "שימוש ב-$PE=\\tfrac{1}{2}mv^2$ (נוסחת KE) במקום $mgh$. או שכחת $g=10$ כפי שצוין בנתון.",
        "במכינה נותנים לעיתים $g=10$ לחישוב נקי. בדקו $g$ לפני הצבה. אימות יחידות: ק\"ג × מ/ש² × מ' = J.",
    ),
    4: fmt_expl(
        "Kinetic energy is $KE = \\tfrac{1}{2}mv^2$. With $m = 3$ kg and $v = 4$ m/s: $KE = \\tfrac{1}{2}(3)(16) = 24$ J. The object is already moving, so we use the speed directly — no need for acceleration or displacement.",
        "KE depends on speed squared, so doubling velocity quadruples kinetic energy. Here $v = 4$ m/s gives $v^2 = 16$, which is the value to substitute (not $v$ itself).",
        "Forgetting the $\\tfrac{1}{2}$ factor, giving $3 \\times 16 = 48$ J. Another error: using $v = 4$ instead of $v^2 = 16$ in the formula, yielding $KE = 6$ J.",
        "Write the formula first, then substitute: $KE = \\tfrac{1}{2}mv^2$. Square the velocity before multiplying — this catches the most common arithmetic error on exam papers.",
        "אנרגיה קינטית: $KE=\\tfrac{1}{2}mv^2$. $m=3$ ק\"ג, $v=4$ מ\"ש → $KE=\\tfrac{1}{2}(3)(16)=24$ J. הגוף כבר בתנועה — משתמשים במהירות ישירות.",
        "KE תלוי בריבוע המהירות — הכפלת מהירות מכפילה KE פי ארבעה. כאן $v^2=16$, לא $v=4$.",
        "שכחת $\\tfrac{1}{2}$, קיבלו 48 J. או שימוש ב-$v=4$ במקום $v^2=16$, קיבלו 6 J.",
        "כתבו נוסחה, הציבו: $KE=\\tfrac{1}{2}mv^2$. הריבוע לפני הכפל. אם קיבלתם 48 — שכחתם $\\tfrac{1}{2}$; אם 6 — שכחתם לרבע.",
    ),
    5: fmt_expl(
        "On a 37° incline with $\\mu_k = 0.25$: normal force $N = mg\\cos37° = 5(10)(0.8) = 40$ N. Kinetic friction $f_k = \\mu_k N = 10$ N. Net force down slope: $ma = mg\\sin37° - f_k = 30 - 10 = 20$ N. Acceleration: $a = 20/5 = 4$ m/s².",
        "Always resolve weight first: $mg\\sin\\theta$ parallel to the slope (driving motion), $mg\\cos\\theta$ perpendicular (determines normal force). Friction opposes motion and depends on $N$, not on $\\sin\\theta$ directly.",
        "Using $f_k = \\mu_k mg\\sin\\theta$ instead of $\\mu_k N = \\mu_k mg\\cos\\theta$. This is the single most common incline error — friction is perpendicular to the surface, so it depends on the normal force.",
        "Draw a triangle with $\\sin37° = 0.6$ and $\\cos37° = 0.8$ on your exam paper. Label parallel and perpendicular components before writing $F = ma$.",
        "במדרון 37° עם $\\mu_k=0.25$: $N=mg\\cos37°=5\\times10\\times0.8=40$ N. $f_k=\\mu_k N=10$ N. כוח שקול: $ma=mg\\sin37°-f_k=30-10=20$ N. $a=20/5=4$ מ\"ש².",
        "פרקו משקל תחילה: $mg\\sin\\theta$ מקביל למדרון (מניע תנועה), $mg\\cos\\theta$ ניצב (קובע N). חיכוך נגד תנועה ותלוי ב-N, לא ב-$\\sin\\theta$ ישירות.",
        "$f_k=\\mu_k mg\\sin\\theta$ במקום $\\mu_k mg\\cos\\theta$ — הטעות הנפוצה ביותר במדרונות. חיכוך תמיד תלוי בכוח הנורמלי $N$.",
        "שרטטו משולש עם $\\sin37°=0.6$, $\\cos37°=0.8$. תייגו רכיבים לפני $F=ma$. נוסחה מהירה: $a=g(\\sin\\theta-\\mu_k\\cos\\theta)=4$ מ\"ש².",
    ),
    6: fmt_expl(
        "Energy conservation: initial PE converts to final KE. $mgh = \\tfrac{1}{2}mv^2$, so $v = \\sqrt{2gh} = \\sqrt{2(10)(5)} = \\sqrt{100} = 10$ m/s. Mass cancels — the speed depends only on height and gravity.",
        "For free-fall (or any frictionless drop), you never need the mass. Set $PE_i = KE_f$, cancel $m$, and solve for $v$. The 0.2 kg mass in the problem is a distractor.",
        "Using $v = 2gh = 100$ (forgetting the square root) or $v = gh = 50$. Another trap: using $v = \\sqrt{gh}$ instead of $\\sqrt{2gh}$ — missing the factor of 2 from the $\\tfrac{1}{2}$ in KE.",
        "Memorize $v = \\sqrt{2gh}$ for frictionless drops. Verify: a 5 m drop with $g = 10$ gives $v = 10$ m/s — exactly one second of free-fall speed.",
        "שימור אנרגיה: $mgh=\\tfrac{1}{2}mv^2$ → $v=\\sqrt{2gh}=\\sqrt{2\\times10\\times5}=\\sqrt{100}=10$ מ\"ש. מסה מתצמצמת — מהירות תלויה רק בגובה וכבידה.",
        "בנפילה חופשית (ללא חיכוך) לא צריך מסה כלל. $PE_i=KE_f$, צמצמו $m$, פתרו. 0.2 ק\"ג בנתון = מסיח — התוצאה זהה לכל מסה.",
        "$v=2gh=100$ (בלי שורש), או $v=\\sqrt{gh}$ (חסר גורם 2 מה-$\\tfrac{1}{2}$ ב-KE). שני מסלולים שגויים נפוצים.",
        "שיננו $v=\\sqrt{2gh}$ לנפילה חופשית. אימות: 5 מ' עם $g=10$ → $v=10$ מ\"ש. מסה מתצמצמת תמיד.",
    ),
    7: fmt_expl(
        "Treat both blocks as one system: total mass $m_1 + m_2 = 8$ kg. Net horizontal force $F = 16$ N gives $a = F/(m_1+m_2) = 16/8 = 2$ m/s². Tension on block 2: $T = m_2 a = 5(2) = 10$ N — the string pulls block 2 forward.",
        "For acceleration, you can use either the system approach ($a = F_{\\text{net}}/m_{\\text{total}}$) or individual FBDs. For tension, you must analyze one block separately — the system method gives $a$ but not $T$.",
        "Computing $a = F/m_1 = 16/3$ (using only the pulled block's mass). For tension, writing $T = F = 16$ N (confusing applied force with string tension).",
        "After finding $a$, always verify on the second block: $T$ should equal $m_2 a$ if you analyze block 2, or $F - T = m_1 a$ if you analyze block 1. Both must give the same $T$.",
        "שני גושים כמערכת אחת: $m_1+m_2=3+5=8$ ק\"ג. $a=F/(m_1+m_2)=16/8=2$ מ\"ש². מתח על גוש 2: $T=m_2 a=5\\times2=10$ N.",
        "לתאוצה — גישת מערכת ($a=F_{\\text{net}}/m_{\\text{כולל}}$). למתח — FBD לגוש בודד. שיטת מערכת נותנת $a$ בלבד, לא $T$.",
        "$a=F/m_1=16/3$ (רק מסת הגוש הנמשך). $T=F=16$ N (בלבול כוח מופעל עם מתח בחוט).",
        "אחרי $a$, אמתו: $F-T=m_1 a$ → $16-10=6=3\\times2$. ✓ מתח 10 N עקבי עם $a=2$ מ\"ש². שתי שיטות — מערכת ו-FBD.",
    ),
    8: fmt_expl(
        "(a) Deceleration: $a = -F/m = -6000/1200 = -5$ m/s² (negative = slowing down). (b) Stopping distance: use $v^2 = v_0^2 + 2ax$ with $v = 0$: $0 = 400 - 10x$, so $x = 40$ m.",
        "Part (a) is direct Newton's second law. Part (b) is kinematics — once you have $a$, use the time-free equation since final velocity is zero. The negative sign in $a$ is already encoded in the equation.",
        "For part (b), using $x = v_0 t$ without finding time first. Or getting $a = +5$ (missing the negative sign) and obtaining a negative distance. Another trap: using $x = \\tfrac{1}{2}at^2$ without first computing $t$.",
        "Braking problems almost always use $v^2 = v_0^2 + 2ax$. With $v_f = 0$, this simplifies to $x = v_0^2/(2|a|)$. Plug in numbers only after setting up the symbolic equation.",
        "(א) $a=-F/m=-6000/1200=-5$ מ\"ש² (שלילי = האטה). (ב) $v^2=v_0^2+2ax$ עם $v=0$: $0=400+2(-5)x$ → $x=40$ מ'.",
        "(א) חוק שני ישיר — כוח חיכוך = כוח שקול. (ב) קינמטיקה — משוואה ללא זמן כי $v_f=0$. הסימן השלילי ב-$a$ כבר במשוואה.",
        "$x=v_0 t$ בלי למצוא $t$ קודם. $a=+5$ (חסר סימן) → מרחק שלילי. $\\tfrac{1}{2}at^2$ בלי חישוב $t$.",
        "בלימה — $v^2=v_0^2+2ax$. עם $v_f=0$: $x=v_0^2/(2|a|)=400/10=40$ מ'. שיננו נוסחה זו.",
    ),
}


def validate(data):
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind not in MIN:
            continue
        min_en, min_he = MIN[kind]
        en, he = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        if en < min_en:
            errors.append(f"{kind} EN short: {en}<{min_en}")
        if he < min_he:
            errors.append(f"{kind} HE short: {he}<{min_he}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"{kind} HE weak")
    for q in data["questions"]:
        en, he = wc(q.get("explanation_en", "")), wc(q.get("explanation_he", ""))
        if en < 80 or en > 150:
            errors.append(f"Q{q['ord']} EN: {en} words (need 80-150)")
        if he < 80 or he > 150:
            errors.append(f"Q{q['ord']} HE: {he} words (need 80-150)")
    return errors


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "definition":
            sec["body_en_md"] = DEF_EN
            sec["body_he_md"] = DEF_HE
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
            if "thrown upward" in body or "נזרק כלפי מעלה" in sec.get("body_he_md", ""):
                sec["checkpoint_solution_en"] = CHK1_EN
                sec["checkpoint_solution_he"] = CHK1_HE
            else:
                sec["checkpoint_solution_en"] = CHK2_EN
                sec["checkpoint_solution_he"] = CHK2_HE
        elif kind == "pitfall":
            sec["body_he_md"] = PITFALL_HE
        elif kind == "why_matters":
            sec["body_en_md"] = WHY_EN
            sec["body_he_md"] = WHY_HE
        elif kind == "before_exam":
            sec["body_he_md"] = BEFORE_HE
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY_EN
            sec["body_he_md"] = SUMMARY_HE

    for q in data["questions"]:
        if q["ord"] in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[q["ord"]]

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
