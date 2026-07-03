#!/usr/bin/env python3
"""Expand optimization_related_rates.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/optimization_related_rates.json"

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


INTRO_EN = """When two or more quantities are linked by an equation, their **rates of change with respect to time** are linked too. **Related rates** problems use implicit differentiation with respect to $t$: treat each changing quantity as a function of time, differentiate the connecting equation with the chain rule, and solve for the unknown rate at a specific instant.

Classic setups include a ladder sliding down a wall, oil spreading in a circle, water draining from a cone, or two vehicles moving apart. The algebra is always the same pattern: diagram, variables, constraint equation, differentiate w.r.t. $t$, substitute known values, solve.

University Calc 1 exams grade the **setup** heavily — a wrong diagram or early substitution usually cannot be recovered. This topic builds directly on `concept:implicit_differentiation` and pairs with `concept:optimization_problems`; both demand disciplined variable management and fluent chain-rule use. Master the eight-step checklist in this lesson and you can transfer the template to any new geometry or physics context."""

INTRO_HE = """כאשר שני גדלים או יותר קשורים במשוואה, גם **קצבי השינוי שלהם לפי הזמן** קשורים. בעיות **קצבי שינוי מקושרים** משתמשות בגזירה סמויה לפי $t$: מתייחסים לכל גודל משתנה כפונקציה של זמן, גוזרים את משוואת הקישור בכלל השרשרת, ופותרים את הקצב הלא ידוע ברגע נתון.

תרחישים קלאסיים: סולם מחליק על קיר, כתם שמן מתפשט, מים מתנקזים מחרוט, או שני כלי רכב מתרחקים. האלגברה תמיד באותה תבנית: תרשים, משתנים, משוואת קישור, גזירה לפי $t$, הצבת ערכים ידועים, פתרון.

בבחינות חשבון 1 באוניברסיטה נבדקת **ההכנה** בכובד — תרשים שגוי או הצבה מוקדמת כמעט בלתי ניתנים לתיקון. נושא זה נשען ישירות על `concept:implicit_differentiation` ומשתלב עם `concept:optimization_problems`; שניהם דורשים ניהול משתנים ממושמע ושליטה בכלל השרשרת. שליטה ברשימת השמונה צעדים בשיעור זה מאפשרת העברה לכל הקשר גיאומטרי או פיזיקלי חדש."""

DEF_EN = """**General procedure for related rates:**

1. **Draw and label** a diagram at a general instant — not a frozen snapshot with numbers only.
2. **Identify** every quantity that changes with time; write them as functions of $t$ (e.g., $x(t)$, $r(t)$, $h(t)$).
3. **Write an algebraic equation** relating the variables — from geometry (Pythagoras, similar triangles, area/volume formulas) or physics.
4. **Differentiate both sides with respect to $t$** using the chain rule on every variable that depends on $t$.
5. **Substitute known values** — positions and rates — at the specific instant asked in the problem.
6. **Solve algebraically** for the unknown rate; include correct units and interpret the sign.

**Chain rule in action (time differentiation):**
$$\\frac{d}{dt}[f(x)] = f'(x)\\cdot\\frac{dx}{dt}, \\qquad \\frac{d}{dt}[x^2] = 2x\\frac{dx}{dt}.$$

**Golden rule:** Do **NOT** plug in constant numerical values for variables **before** differentiating. Early substitution freezes a variable and kills its derivative — the most common fatal error on related-rates exams."""

DEF_HE = """**נוהל כללי לקצבי שינוי מקושרים:**

1. **ציירו וסמנו** תרשים ברגע כללי — לא תמונה קפואה עם מספרים בלבד.
2. **זהו** כל גודל שמשתנה עם הזמן; כתבו אותם כפונקציות של $t$ (למשל $x(t)$, $r(t)$, $h(t)$).
3. **כתבו משוואה אלגברית** המקשרת את המשתנים — מגיאומטריה (פיתגורס, משולשים דומים, נוסחאות שטח/נפח) או מפיזיקה.
4. **גזרו שני הצדדים לפי $t$** עם כלל השרשרת על כל משתנה שתלוי ב-$t$.
5. **הציבו ערכים ידועים** — מיקומים וקצבים — ברגע הספציפי שבשאלה.
6. **פתרו אלגברית** את הקצב הלא ידוע; ציינו יחידות נכונות ופרשו את הסימן.

**כלל שרשרת בגזירה לפי זמן:**
$$\\frac{d}{dt}[f(x)] = f'(x)\\cdot\\frac{dx}{dt}, \\qquad \\frac{d}{dt}[x^2] = 2x\\frac{dx}{dt}.$$

**כלל זהב:** **אל** תציבו ערכים מספריים קבועים **לפני** הגזירה. הצבה מוקדמת קופאת משתנה ומאפסת את הנגזרת שלו — הטעות ההרסנית הנפוצה ביותר בבחינות קצבי שינוי."""

THEORY_EN = """**Common geometric formulas and their time derivatives:**

**Pythagorean theorem** (ladder, kite string, distance between moving objects):
$$a^2+b^2=c^2 \\implies 2a\\frac{da}{dt}+2b\\frac{db}{dt}=2c\\frac{dc}{dt}.$$

**Circle area:** $A=\\pi r^2 \\implies \\dfrac{dA}{dt}=2\\pi r\\dfrac{dr}{dt}$.

**Sphere volume:** $V=\\dfrac{4}{3}\\pi r^3 \\implies \\dfrac{dV}{dt}=4\\pi r^2\\dfrac{dr}{dt}$.

**Cone volume:** $V=\\dfrac{1}{3}\\pi r^2 h$. When the cone is similar at every height ($r/h$ constant), substitute $r=kh$ **first** to get $V$ as a function of $h$ alone, then differentiate.

**Product rule for changing dimensions:** If $A=lw$ with both $l$ and $w$ changing,
$$\\frac{dA}{dt}=l\\frac{dw}{dt}+w\\frac{dl}{dt}.$$

**Similar triangles** often reduce two changing variables to one before differentiation — essential in conical tank and shadow problems.

**Sign interpretation:** A negative rate means the quantity is decreasing; always check whether the answer matches the physical story (water level dropping, volume shrinking, etc.).

**Workflow reminder:** Write the general formula, differentiate symbolically, **then** substitute numbers at the instant requested.

**Exam strategy:** On timed tests, spend the first two minutes on the diagram and variable list. Most lost points come from wrong linking equations (using diameter instead of radius, or height vs. slant height), not from algebra after the setup is correct."""

THEORY_HE = """**נוסחאות גיאומטריות שכיחות ונגזרותיהן לפי זמן:**

**משפט פיתגורס** (סולם, מחרוזת עפיפון, מרחק בין גופים נעים):
$$a^2+b^2=c^2 \\implies 2a\\frac{da}{dt}+2b\\frac{db}{dt}=2c\\frac{dc}{dt}.$$

**שטח מעגל:** $A=\\pi r^2 \\implies \\dfrac{dA}{dt}=2\\pi r\\dfrac{dr}{dt}$.

**נפח כדור:** $V=\\dfrac{4}{3}\\pi r^3 \\implies \\dfrac{dV}{dt}=4\\pi r^2\\dfrac{dr}{dt}$.

**נפח חרוט:** $V=\\dfrac{1}{3}\\pi r^2 h$. כשהחרוט דומה בכל גובה ($r/h$ קבוע), הציבו $r=kh$ **קודם** כדי לקבל $V$ כפונקציה של $h$ בלבד, ואז גזרו.

**כלל מכפלה לממדים משתנים:** אם $A=lw$ וגם $l$ וגם $w$ משתנים,
$$\\frac{dA}{dt}=l\\frac{dw}{dt}+w\\frac{dl}{dt}.$$

**משולשים דומים** מצמצמים לעיתים שני משתנים לאחד לפני הגזירה — חיוני במיכלי חרוט ובבעיות צל.

**פרשנות סימן:** קצב שלילי פירושו שהגודל קטן; תמיד בדקו שהתשובה תואמת את הסיפור הפיזיקלי (מפלס מים יורד, נפח מתכווץ).

**תזכורת:** כתבו נוסחה כללית, גזרו סמלית, **ואז** הציבו מספרים ברגע המבוקש.

**אסטרטגיית בחינה:** בבחינה עם זמן מוגבל, השקיעו שתי דקות ראשונות בתרשים וברשימת משתנים. רוב הנקודות האבודות נובעות ממשוואות קישור שגויות (קוטר במקום רדיוס, או גובה במקום אורך אלכסון), לא מאלגברה אחרי הכנה נכונה."""

WE1_EN = """**Problem:** A 10 m ladder leans against a wall. The foot slides away from the wall at 2 m/s. How fast is the top sliding down when the foot is 6 m from the wall?

**Strategy:** Pythagoras links $x$ (foot distance) and $y$ (top height) with fixed ladder length. Differentiate before substituting $x=6$.

### Move 1: Label variables
Let $x$ = horizontal distance of foot from wall, $y$ = height of top. Given $\\dfrac{dx}{dt}=2$ m/s. Find $\\dfrac{dy}{dt}$ when $x=6$ m.

### Move 2: Constraint equation
$$x^2+y^2=100 \\qquad (\\text{ladder length}=10).$$

### Move 3: Differentiate w.r.t. $t$
$$2x\\frac{dx}{dt}+2y\\frac{dy}{dt}=0.$$

### Move 4: Find $y$ at the instant
$$y=\\sqrt{100-36}=\\sqrt{64}=8\\text{ m}.$$

### Move 5: Substitute and solve
$$2(6)(2)+2(8)\\frac{dy}{dt}=0 \\implies 24+16\\frac{dy}{dt}=0 \\implies \\frac{dy}{dt}=-\\frac{3}{2}\\text{ m/s}.$$

**Answer:** The top slides down at $1.5$ m/s. The negative sign confirms downward motion. ✓

**Exam note:** Students often forget to compute $y$ from Pythagoras before substituting — without $y=8$, the equation has two unknowns."""

WE1_HE = """**בעיה:** סולם באורך 10 מ' נשען על קיר. הקצה התחתון מחליק מהקיר בקצב 2 מ'/שנ'. כמה מהר יורד הקצה העליון כאשר הקצה התחתון נמצא 6 מ' מהקיר?

**אסטרטגיה:** פיתגורס מקשר $x$ (מרחק מהקיר) ו-$y$ (גובה) עם אורך סולם קבוע. גזרו לפני הצבת $x=6$.

### צעד 1: סימון משתנים
נסמן $x$ = מרחק אופקי של הקצה התחתון מהקיר, $y$ = גובה הקצה העליון. נתון $\\dfrac{dx}{dt}=2$ מ'/שנ'. מצאו $\\dfrac{dy}{dt}$ כאשר $x=6$ מ'.

### צעד 2: משוואת קישור
$$x^2+y^2=100 \\qquad (\\text{אורך סולם}=10).$$

### צעד 3: גזירה לפי $t$
$$2x\\frac{dx}{dt}+2y\\frac{dy}{dt}=0.$$

### צעד 4: מציאת $y$ ברגע הנתון
$$y=\\sqrt{100-36}=\\sqrt{64}=8\\text{ מ'}$$

### צעד 5: הצבה ופתרון
$$2(6)(2)+2(8)\\frac{dy}{dt}=0 \\implies 24+16\\frac{dy}{dt}=0 \\implies \\frac{dy}{dt}=-\\frac{3}{2}\\text{ מ'/שנ'.}$$

**תשובה:** הקצה העליון יורד ב-$1.5$ מ'/שנ'. הסימן השלילי מאשר תנועה כלפי מטה. ✓

**הערת בחינה:** תלמידים לעיתים שוכחים לחשב $y$ מפיתגורס לפני ההצבה — בלי $y=8$ יש שני לא ידועים במשוואה."""

WE2_EN = """**Problem:** A circular oil spill grows so that $\\dfrac{dA}{dt}=50\\text{ m}^2/\\text{min}$. How fast is the radius growing when $r=10$ m?

### Move 1: Variables
$r$ = radius, $A$ = area. Given $\\dfrac{dA}{dt}=50$. Find $\\dfrac{dr}{dt}$ when $r=10$.

### Move 2: Relating equation
$$A = \\pi r^2.$$

### Move 3: Differentiate
$$\\frac{dA}{dt} = 2\\pi r\\frac{dr}{dt}.$$

### Move 4: Substitute at $r=10$
$$50 = 2\\pi(10)\\frac{dr}{dt} = 20\\pi\\frac{dr}{dt}.$$

### Move 5: Solve
$$\\frac{dr}{dt} = \\frac{50}{20\\pi} = \\frac{5}{2\\pi} \\approx 0.796\\text{ m/min}.$$

**Answer:** The radius grows at about $0.796$ m/min when $r=10$ m. ✓

**Transfer:** Any \"area rate given, find radius rate\" problem uses the same $A=\\pi r^2$ chain rule — watch units (m²/min vs m/min).

**Verify:** At $r=10$ m, a small increase in radius produces area growth proportional to circumference $2\\pi r$ — the factor $2\\pi r$ in $dA/dt$ matches that intuition. If your answer has the wrong power of $r$, re-check the chain rule step by step."""

WE2_HE = """**בעיה:** כתם שמן עגול מתרחב כך ש-$\\dfrac{dA}{dt}=50\\text{ מ}^2/\\text{דק}$. כמה מהר גדל הרדיוס כאשר $r=10$ מ'?

### צעד 1: משתנים
$r$ = רדיוס, $A$ = שטח. נתון $\\dfrac{dA}{dt}=50$. מצאו $\\dfrac{dr}{dt}$ כאשר $r=10$.

### צעד 2: משוואת קישור
$$A = \\pi r^2.$$

### צעד 3: גזירה
$$\\frac{dA}{dt} = 2\\pi r\\frac{dr}{dt}.$$

### צעד 4: הצבה ב-$r=10$
$$50 = 2\\pi(10)\\frac{dr}{dt} = 20\\pi\\frac{dr}{dt}.$$

### צעד 5: פתרון
$$\\frac{dr}{dt} = \\frac{50}{20\\pi} = \\frac{5}{2\\pi} \\approx 0.796\\text{ מ'/דק'.}$$

**תשובה:** הרדיוס גדל בכ-$0.796$ מ'/דק' כאשר $r=10$ מ'. ✓

**העברה:** כל בעיית \"נתון קצב שטח, מצא קצב רדיוס\" משתמשת באותו כלל שרשרת על $A=\\pi r^2$ — שימו לב ליחידות (מ²/דק' מול מ'/דק').

**אימות:** ב-$r=10$ מ', גידול קטן ברדיוס מייצר גידול שטח פרופורציונלי להיקף $2\\pi r$ — הגורם $2\\pi r$ ב-$dA/dt$ תואם את האינטואיציה. אם התשובה בחזקה שגויה של $r$, בדקו מחדש את כלל השרשרת."""

WE3_EN = """**Problem:** Water drains from a conical tank (vertex down) of height 12 m and top radius 4 m at $\\dfrac{dV}{dt}=-2\\text{ m}^3/\\text{min}$. Find $\\dfrac{dh}{dt}$ when $h=6$ m.

### Move 1: Similar triangles
At water height $h$, surface radius $r$ satisfies $r/h=4/12=1/3$, so $r=h/3$.

### Move 2: Volume in one variable
$$V = \\frac{1}{3}\\pi r^2 h = \\frac{1}{3}\\pi\\left(\\frac{h}{3}\\right)^2 h = \\frac{\\pi h^3}{27}.$$

### Move 3: Differentiate
$$\\frac{dV}{dt} = \\frac{\\pi\\cdot 3h^2}{27}\\frac{dh}{dt} = \\frac{\\pi h^2}{9}\\frac{dh}{dt}.$$

### Move 4: Substitute $h=6$, $dV/dt=-2$
$$-2 = \\frac{\\pi(36)}{9}\\frac{dh}{dt} = 4\\pi\\frac{dh}{dt}.$$

### Move 5: Solve
$$\\frac{dh}{dt} = \\frac{-2}{4\\pi} = -\\frac{1}{2\\pi} \\approx -0.159\\text{ m/min}.$$

**Answer:** The water level drops at $1/(2\\pi)$ m/min when $h=6$ m. ✓

**Pattern:** Conical tank problems always need similar-triangle reduction **before** differentiation — differentiating $V=\\pi r^2 h/3$ with both $r$ and $h$ changing adds unnecessary product-rule complexity.

**Physical check:** $dh/dt<0$ matches draining water; the magnitude $1/(2\\pi)$ m/min is modest because the cross-section area at $h=6$ is still large, so the level drops slowly relative to volume flow."""

WE3_HE = """**בעיה:** מים מתנקזים ממיכל חרוטי (קודקוד למטה) בגובה 12 מ' ורדיוס עליון 4 מ', בקצב $\\dfrac{dV}{dt}=-2\\text{ מ}^3/\\text{דק}$. מצאו $\\dfrac{dh}{dt}$ כאשר $h=6$ מ'.

### צעד 1: משולשים דומים
בגובה מים $h$, רדיוס פני השטח $r$ מקיים $r/h=4/12=1/3$, לכן $r=h/3$.

### צעד 2: נפח במשתנה אחד
$$V = \\frac{1}{3}\\pi r^2 h = \\frac{1}{3}\\pi\\left(\\frac{h}{3}\\right)^2 h = \\frac{\\pi h^3}{27}.$$

### צעד 3: גזירה
$$\\frac{dV}{dt} = \\frac{\\pi\\cdot 3h^2}{27}\\frac{dh}{dt} = \\frac{\\pi h^2}{9}\\frac{dh}{dt}.$$

### צעד 4: הצבה $h=6$, $dV/dt=-2$
$$-2 = \\frac{\\pi(36)}{9}\\frac{dh}{dt} = 4\\pi\\frac{dh}{dt}.$$

### צעד 5: פתרון
$$\\frac{dh}{dt} = \\frac{-2}{4\\pi} = -\\frac{1}{2\\pi} \\approx -0.159\\text{ מ'/דק'.}$$

**תשובה:** מפלס המים יורד ב-$1/(2\\pi)$ מ'/דק' כאשר $h=6$ מ'. ✓

**דפוס:** בעיות מיכל חרוטי דורשות תמיד צמצום משולשים דומים **לפני** הגזירה — גזירה של $V=\\pi r^2 h/3$ כשגם $r$ וגם $h$ משתנים מוסיפה מורכבות מיותרת.

**בדיקה פיזיקלית:** $dh/dt<0$ תואם ניקוז מים; הגודל $1/(2\\pi)$ מ'/דק' מתון כי שטח החתך ב-$h=6$ עדיין גדול, ולכן המפלס יורד לאט יחסית לזרימת הנפח."""

CHK1_EN = """**Goal:** Ladder 13 m; foot slides at 1 m/s. Find top descent rate when foot is 5 m from wall.

### Move 1: Pythagoras constraint
$$x^2+y^2=169.$$

### Move 2: Differentiate
$$2x\\frac{dx}{dt}+2y\\frac{dy}{dt}=0.$$

### Move 3: Find $y$ when $x=5$
$$y=\\sqrt{169-25}=\\sqrt{144}=12\\text{ m}.$$

### Move 4: Substitute
$$2(5)(1)+2(12)\\frac{dy}{dt}=0 \\implies 10+24\\frac{dy}{dt}=0 \\implies \\frac{dy}{dt}=-\\frac{5}{12}\\text{ m/s}.$$

**Answer:** Top descends at $5/12 \\approx 0.417$ m/s. ✓"""

CHK1_HE = """**מטרה:** סולם 13 מ'; קצה תחתון מחליק ב-1 מ'/שנ'. מצאו קצב ירידת הקצה העליון כשהקצה תחתון ב-5 מ' מהקיר.

### צעד 1: אילוץ פיתגורס
$$x^2+y^2=169.$$

### צעד 2: גזירה
$$2x\\frac{dx}{dt}+2y\\frac{dy}{dt}=0.$$

### צעד 3: מציאת $y$ כאשר $x=5$
$$y=\\sqrt{169-25}=\\sqrt{144}=12\\text{ מ'}$$

### צעד 4: הצבה
$$2(5)(1)+2(12)\\frac{dy}{dt}=0 \\implies 10+24\\frac{dy}{dt}=0 \\implies \\frac{dy}{dt}=-\\frac{5}{12}\\text{ מ'/שנ'.}$$

**תשובה:** הקצה העליון יורד ב-$5/12 \\approx 0.417$ מ'/שנ'. ✓"""

CHK2_EN = """**Goal:** Spherical balloon inflated at $dV/dt=100\\text{ cm}^3/\\text{s}$. Find $dr/dt$ when $r=5$ cm.

### Move 1: Volume formula
$$V=\\frac{4}{3}\\pi r^3.$$

### Move 2: Differentiate
$$\\frac{dV}{dt}=4\\pi r^2\\frac{dr}{dt}.$$

### Move 3: Substitute $r=5$, $dV/dt=100$
$$100=4\\pi(25)\\frac{dr}{dt}=100\\pi\\frac{dr}{dt}.$$

### Move 4: Solve
$$\\frac{dr}{dt}=\\frac{100}{100\\pi}=\\frac{1}{\\pi}\\approx 0.318\\text{ cm/s}.$$

**Answer:** Radius grows at $1/\\pi \\approx 0.318$ cm/s when $r=5$ cm. ✓"""

CHK2_HE = """**מטרה:** בלון כדורי מתנפח ב-$dV/dt=100\\text{ סמ}^3/\\text{שנ}$. מצאו $dr/dt$ כאשר $r=5$ ס\"מ.

### צעד 1: נוסחת נפח
$$V=\\frac{4}{3}\\pi r^3.$$

### צעד 2: גזירה
$$\\frac{dV}{dt}=4\\pi r^2\\frac{dr}{dt}.$$

### צעד 3: הצבה $r=5$, $dV/dt=100$
$$100=4\\pi(25)\\frac{dr}{dt}=100\\pi\\frac{dr}{dt}.$$

### צעד 4: פתרון
$$\\frac{dr}{dt}=\\frac{100}{100\\pi}=\\frac{1}{\\pi}\\approx 0.318\\text{ ס\"מ/שנ'.}$$

**תשובה:** הרדיוס גדל ב-$1/\\pi \\approx 0.318$ ס\"מ/שנ' כאשר $r=5$ ס\"מ. ✓"""

METHOD_EN = """| Geometry | Relating equation | After differentiating w.r.t. $t$ |
|---|---|---|
| Circle area | $A=\\pi r^2$ | $dA/dt=2\\pi r\\cdot dr/dt$ |
| Sphere volume | $V=4\\pi r^3/3$ | $dV/dt=4\\pi r^2\\cdot dr/dt$ |
| Cylinder volume | $V=\\pi r^2 h$ | $dV/dt=\\pi r^2\\cdot dh/dt$ if $r$ fixed |
| Cone (similar) | $r=kh$, $V=\\pi h^3 k^2/3$ | differentiate single-variable $V(h)$ |
| Pythagoras | $a^2+b^2=c^2$ | $2a\\dot a+2b\\dot b=2c\\dot c$ |

**Eight-step checklist:**
1. Read carefully — list every changing quantity.
2. Draw a general diagram (not a specific-number snapshot).
3. Label variables algebraically.
4. Write the geometric/physical linking equation.
5. Reduce variables if constrained (similar triangles).
6. Differentiate both sides w.r.t. $t$.
7. Substitute known positions and rates at the instant.
8. Solve, interpret sign, state units."""

METHOD_HE = """| גיאומטריה | משוואת קישור | אחרי גזירה לפי $t$ |
|---|---|---|
| שטח מעגל | $A=\\pi r^2$ | $dA/dt=2\\pi r\\cdot dr/dt$ |
| נפח כדור | $V=4\\pi r^3/3$ | $dV/dt=4\\pi r^2\\cdot dr/dt$ |
| נפח גליל | $V=\\pi r^2 h$ | $dV/dt=\\pi r^2\\cdot dh/dt$ אם $r$ קבוע |
| חרוט (דומה) | $r=kh$, $V=\\pi h^3 k^2/3$ | גזירה של $V(h)$ במשתנה אחד |
| פיתגורס | $a^2+b^2=c^2$ | $2a\\dot a+2b\\dot b=2c\\dot c$ |

**רשימת שמונה צעדים:**
1. קראו בעיון — רשימת כל הגדלים המשתנים.
2. ציירו תרשים כללי (לא תמונה עם מספרים ספציפיים).
3. סמנו משתנים אלגברית.
4. כתבו משוואת קישור גיאומטרית/פיזיקלית.
5. צמצמו משתנים אם יש אילוץ (משולשים דומים).
6. גזרו שני הצדדים לפי $t$.
7. הציבו מיקומים וקצבים ידועים ברגע הנתון.
8. פתרו, פרשו סימן, ציינו יחידות."""

PITFALL_EN = """1. **Substituting specific values BEFORE differentiating.** Plugging $x=6$ into $x^2+y^2=100$ before differentiation makes $y$ a constant and gives $\\dfrac{dy}{dt}=0$ — wrong. Always differentiate the general equation first, then substitute.

2. **Forgetting the chain rule.** $\\dfrac{d}{dt}[r^2]=2r\\dfrac{dr}{dt}$, not $2r$. Every variable that depends on $t$ picks up a $\\dot{x}$ factor.

3. **Wrong sign.** Draining water gives $\\dfrac{dV}{dt}<0$; a sliding ladder top moving down gives $\\dfrac{dy}{dt}<0$. If your sign contradicts the physical story, re-check the setup.

4. **Not reducing variables in cone problems.** Differentiating $V=\\pi r^2 h/3$ with both $r$ and $h$ changing requires product rule; similar triangles give $V(h)$ in one variable — simpler and less error-prone.

5. **Unit inconsistency.** Mixing cm with m, or minutes with seconds, produces answers off by powers of 10. Convert everything before the final arithmetic."""

PITFALL_HE = """1. **הצבת ערכים ספציפיים לפני הגזירה.** הצבת $x=6$ ב-$x^2+y^2=100$ לפני הגזירה הופכת $y$ לקבוע ונותנת $\\dfrac{dy}{dt}=0$ — שגוי. תמיד גזרו את המשוואה הכללית קודם, ואז הציבו.

2. **שכחת כלל השרשרת.** $\\dfrac{d}{dt}[r^2]=2r\\dfrac{dr}{dt}$, לא $2r$. כל משתנה שתלוי ב-$t$ מקבל גורם $\\dot{x}$.

3. **סימן שגוי.** ניקוז מים נותן $\\dfrac{dV}{dt}<0$; סולם שיורד נותן $\\dfrac{dy}{dt}<0$. אם הסימן סותר את הסיפור הפיזיקלי, בדקו מחדש את ההכנה.

4. **אי-צמצום משתנים בבעיות חרוט.** גזירת $V=\\pi r^2 h/3$ כשגם $r$ וגם $h$ משתנים דורשת כלל מכפלה; משולשים דומים נותנים $V(h)$ — פשוט ופחות טעויות.

5. **אי-עקביות יחידות.** ערבוב ס\"מ עם מ', או דקות עם שניות, מייצר תשובות שגויות בחזקות של 10. המירו הכל לפני החישוב הסופי."""

WHY_EN = """Related rates is the bridge between static geometry and dynamic modeling. The same chain-rule logic appears in physics (velocity components), economics (marginal rates), and engineering (flow rates in pipes and tanks).

**Exam transfer:** Bagrut 5-unit and university Calc 1 both test whether you can set up — not just compute. A clean diagram and correct constraint equation often earn partial credit even when arithmetic slips.

**Knowledge graph links:** This lesson connects to `concept:implicit_differentiation` (differentiate w.r.t. $t$), `concept:derivatives_chain_rule`, and `concept:optimization_problems` (both need careful variable reduction). Mastery here makes `concept:uni_derivatives` applied sections much faster."""

WHY_HE = """קצבי שינוי מקושרים הם הגשר בין גיאומטריה סטática לבין מידול דינמי. אותה לוגיקת כלל שרשרת מופיעה בפיזיקה (רכיבי מהירות), בכלכלה (קצבים שוליים) ובהנדסה (קצבי זרימה בצינורות ובמיכים).

**העברה לבחינות:** בבגרות 5 יחידות ובחשבון 1 באוניברסיטה בודקים אם אתם יודעים **להכין** — לא רק לחשב. תרשים נקי ומשוואת קישור נכונה לעיתים מזכים נקודות חלקיות גם כשיש טעות חישוב.

**קשרים בגרף הידע:** שיעור זה מחובר ל-`concept:implicit_differentiation` (גזירה לפי $t$), ל-`concept:derivatives_chain_rule`, ול-`concept:optimization_problems` (שניהם דורשים צמצום משתנים זהיר). שליטה כאן מאיצה מאוד את החלקים השימושיים ב-`concept:uni_derivatives`."""

BEFORE_EN = """**Golden rule:** Never substitute specific numerical values before differentiating w.r.t. $t$.

**Process:**
1. Draw diagram and label all variables.
2. Write the linking equation (geometry or physics).
3. Reduce to one variable if similar triangles apply.
4. Differentiate both sides w.r.t. $t$.
5. Substitute known positions and rates at the instant.
6. Solve for the unknown rate; check sign and units.

**Formulas to recall:**
- $dA/dt=2\\pi r\\cdot dr/dt$ (circle area)
- $dV/dt=4\\pi r^2\\cdot dr/dt$ (sphere volume)
- Cone: substitute $r=kh$ first, then differentiate $V(h)$
- Pythagoras: $2a\\dot{a}+2b\\dot{b}=2c\\dot{c}$

**Last review:** Solve one ladder and one cone checkpoint without notes, timing yourself under 8 minutes each."""

BEFORE_HE = """**כלל זהב:** לעולם אל תציבו ערכים מספריים ספציפיים לפני גזירה לפי $t$.

**תהליך:**
1. ציירו תרשים וסמנו משתנים.
2. כתבו משוואת קישור (גיאומטריה או פיזיקה).
3. צמצמו למשתנה אחד אם יש משולשים דומים.
4. גזרו שני הצדדים לפי $t$.
5. הציבו מיקומים וקצבים ידועים ברגע הנתון.
6. פתרו את הקצב הלא ידוע; בדקו סימן ויחידות.

**נוסחאות לזכירה:**
- $dA/dt=2\\pi r\\cdot dr/dt$ (שטח מעגל)
- $dV/dt=4\\pi r^2\\cdot dr/dt$ (נפח כדור)
- חרוט: הציבו $r=kh$ קודם, ואז גזרו $V(h)$
- פיתגורס: $2a\\dot{a}+2b\\dot{b}=2c\\dot{c}$

**חזרה אחרונה:** פתרו checkpoint אחד של סולם ואחד של חרוט בלי רשימות, בפחות מ-8 דקות כל אחד."""

SUMMARY_EN = """- **Related rates** = implicit differentiation w.r.t. $t$: find one rate from another using a linking equation.
- Always differentiate **before** substituting specific numerical values.
- Use geometry (Pythagoras, similar triangles, area/volume formulas) to relate quantities.
- For cones: reduce to one variable with $r/h=\\text{const}$ before differentiating.
- Check signs: negative rate means decreasing; verify against the physical story.
- State final answers with correct units and interpret the sign physically."""

SUMMARY_HE = """- **קצבי שינוי מקושרים** = גזירה סמויה לפי $t$: מציאת קצב אחד מתוך אחר באמצעות משוואת קישור.
- תמיד גזרו **לפני** הצבת ערכים מספריים ספציפיים.
- השתמשו בגיאומטריה (פיתגורס, משולשים דומים, נוסחאות שטח/נפח) לקישור.
- לחרוטים: צמצמו למשתנה אחד עם $r/h=\\text{קבוע}$ לפני הגזירה.
- בדקו סימנים: קצב שלילי = קטן; אמתו מול הסיפור הפיזיקלי.
- ציינו תשובות סופיות עם יחידות נכונות."""

EXPLS = {
    1: fmt_expl(
        "Start with $A=\\pi r^2$. Differentiate: $\\dfrac{dA}{dt}=2\\pi r\\dfrac{dr}{dt}$. Given $r=5$ cm and $\\dfrac{dr}{dt}=3$ cm/s: $\\dfrac{dA}{dt}=2\\pi(5)(3)=30\\pi\\approx 94.25$ cm²/s.",
        "Circle-area related rates always follow $A=\\pi r^2$. Identify which rate is known ($dr/dt$) and which is sought ($dA/dt$), differentiate first, then plug in $r=5$.",
        "Using $dA/dt=2\\pi r$ without the $dr/dt$ factor — forgetting chain rule — or substituting $r=5$ into $A$ before differentiating.",
        "Write $dA/dt=2\\pi r\\,dr/dt$ on your formula sheet. On exams, circle problems are quick points if you never skip the chain rule.",
        "מתחילים ב-$A=\\pi r^2$. גזירה: $\\dfrac{dA}{dt}=2\\pi r\\dfrac{dr}{dt}$. נתון $r=5$ ס\"מ ו-$\\dfrac{dr}{dt}=3$ ס\"מ/שנ': $\\dfrac{dA}{dt}=2\\pi(5)(3)=30\\pi\\approx 94.25$ ס\"מ²/שנ'.",
        "קצבי שינוי של שטח מעגל תמיד עוברים דרך $A=\\pi r^2$. זהו איזה קצב ידוע ($dr/dt$) ואיזה מבוקש ($dA/dt$), גזרו קודם, ואז הציבו $r=5$.",
        "שימוש ב-$dA/dt=2\\pi r$ בלי גורם $dr/dt$ — שכחת כלל שרשרת — או הצבת $r=5$ ב-$A$ לפני הגזירה.",
        "כתבו $dA/dt=2\\pi r\\,dr/dt$ בדף נוסחאות. בבחינה, בעיות מעגל הן נקודות מהירות אם לא מדלגים על כלל השרשרת.",
    ),
    2: fmt_expl(
        "Use $V=\\dfrac{4}{3}\\pi r^3$, so $\\dfrac{dV}{dt}=4\\pi r^2\\dfrac{dr}{dt}$. With $\\dfrac{dV}{dt}=-8$ and $r=2$: $-8=4\\pi(4)\\dfrac{dr}{dt}=16\\pi\\dfrac{dr}{dt}$, giving $\\dfrac{dr}{dt}=-\\dfrac{1}{2\\pi}$ cm/s.",
        "Volume shrinking means $dV/dt<0$. The negative answer for $dr/dt$ confirms the radius is also decreasing — signs should align with the physical story.",
        "Dropping the negative sign on $dV/dt$, or using $dV/dt=4\\pi r$ instead of $4\\pi r^2\\,dr/dt$.",
        "When volume decreases, both $dV/dt$ and usually $dr/dt$ are negative. State the sign explicitly — graders check physical interpretation.",
        "משתמשים ב-$V=\\dfrac{4}{3}\\pi r^3$, לכן $\\dfrac{dV}{dt}=4\\pi r^2\\dfrac{dr}{dt}$. עם $\\dfrac{dV}{dt}=-8$ ו-$r=2$: $-8=16\\pi\\dfrac{dr}{dt}$, ולכן $\\dfrac{dr}{dt}=-\\dfrac{1}{2\\pi}$ ס\"מ/שנ'.",
        "נפח מתכווץ אומר $dV/dt<0$. התשובה השלילית ל-$dr/dt$ מאשרת שגם הרדיוס קטן — הסימנים צריכים להתאים לסיפור הפיזיקלי.",
        "השמטת הסימן השלילי ב-$dV/dt$, או שימוש ב-$dV/dt=4\\pi r$ במקום $4\\pi r^2\\,dr/dt$.",
        "כשנפח קטן, גם $dV/dt$ וגם $dr/dt$ שליליים בדרך כלל. ציינו סימן במפורש — בוחנים בודקים פרשנות פיזיקלית. אם קיבלתם $dr/dt$ חיובי, חזרו לניסוח השאלה.",
    ),
    3: fmt_expl(
        "Let $a$ = north distance, $b$ = east distance, $c$ = separation. After 1 h: $a=60$, $b=80$, $c=100$. From $a^2+b^2=c^2$, differentiate: $2a\\dfrac{da}{dt}+2b\\dfrac{db}{dt}=2c\\dfrac{dc}{dt}$. Substitute: $7200+12800=200\\dfrac{dc}{dt}$, so $\\dfrac{dc}{dt}=100$ km/h.",
        "Right-angle motion is a Pythagoras template. Draw the triangle, label legs and hypotenuse, differentiate before substituting positions at $t=1$ h.",
        "Substituting $a=60$, $b=80$ into $a^2+b^2=c^2$ before differentiating — this freezes the legs and gives $dc/dt=0$.",
        "For moving-object distance problems, always differentiate $a^2+b^2=c^2$ first. The 3-4-5 triangle ($60$-$80$-$100$) is a common exam shortcut after 1 hour.",
        "נסמן $a$ = מרחק צפונה, $b$ = מרחק מזרחה, $c$ = מרחק ביניהן. לאחר שעה: $a=60$, $b=80$, $c=100$. מ-$a^2+b^2=c^2$, גזירה: $2a\\dfrac{da}{dt}+2b\\dfrac{db}{dt}=2c\\dfrac{dc}{dt}$. הצבה: $7200+12800=200\\dfrac{dc}{dt}$, כלומר $\\dfrac{dc}{dt}=100$ קמ\"ש.",
        "תנועה בזווית ישרה היא תבנית פיתגורס. שרטטו משולש, סמנו ניצבים ויתר, גזרו לפני הצבת מיקומים ב-$t=1$ שעה.",
        "הצבת $a=60$, $b=80$ ב-$a^2+b^2=c^2$ לפני הגזירה — זה קופא את הניצבים ונותן $dc/dt=0$.",
        "בבעיות מרחק בין גופים נעים, תמיד גזרו $a^2+b^2=c^2$ קודם. משולש 3-4-5 ($60$-$80$-$100$) הוא קיצור נפוץ בבחינה אחרי שעה.",
    ),
    4: fmt_expl(
        "Ladder length 5 m: $x^2+y^2=25$. When $x=3$, $y=4$. Differentiate: $2x\\dfrac{dx}{dt}+2y\\dfrac{dy}{dt}=0$. With $\\dfrac{dx}{dt}=1$: $6+8\\dfrac{dy}{dt}=0$, so $\\dfrac{dy}{dt}=-\\dfrac{3}{4}$ m/s.",
        "Classic ladder: find the missing leg with Pythagoras **after** differentiating the general equation but **before** final substitution. The negative $dy/dt$ means the top moves down.",
        "Forgetting to compute $y=4$ from $x=3$, or reporting $3/4$ without the negative sign even though the top slides down.",
        "Ladder problems appear on almost every Calc 1 exam. Memorize the pattern: Pythagoras → differentiate → find missing leg → substitute.",
        "אורך סולם 5 מ': $x^2+y^2=25$. כאשר $x=3$, $y=4$. גזירה: $2x\\dfrac{dx}{dt}+2y\\dfrac{dy}{dt}=0$. עם $\\dfrac{dx}{dt}=1$: $6+8\\dfrac{dy}{dt}=0$, כלומר $\\dfrac{dy}{dt}=-\\dfrac{3}{4}$ מ'/שנ'.",
        "סולם קלאסי: מצאו את הניצב החסר בפיתגורס **אחרי** גזירת המשוואה הכללית אך **לפני** ההצבה הסופית. $dy/dt$ שלילי פירושו שהקצה העליון יורד.",
        "שכחת חישוב $y=4$ מ-$x=3$, או דיווח $3/4$ בלי סימן שלילי למרות שהקצה העליון יורד.",
        "בעיות סולם מופיעות כמעט בכל בחינת חשבון 1. שימרו תבנית: פיתגורס → גזירה → ניצב חסר → הצבה.",
    ),
    5: fmt_expl(
        "Cylinder: $V=\\pi r^2 h=9\\pi h$ with $r=3$ fixed. So $\\dfrac{dV}{dt}=9\\pi\\dfrac{dh}{dt}$. Given $\\dfrac{dV}{dt}=2$ m³/min: $2=9\\pi\\dfrac{dh}{dt}$, hence $\\dfrac{dh}{dt}=\\dfrac{2}{9\\pi}\\approx 0.071$ m/min.",
        "Fixed-radius cylinder problems reduce to a linear volume-height relation. Only $h$ changes, so differentiation is straightforward — no product rule needed.",
        "Differentiating $V=\\pi r^2 h$ as if $r$ also changes, or using $dV/dt=2\\pi r\\,dr/dt$ (circle area formula) instead of the cylinder volume derivative.",
        "When radius is constant, write $V=(\\pi r^2)h$ and treat $\\pi r^2$ as a constant coefficient. This avoids unnecessary product-rule steps.",
        "גליל: $V=\\pi r^2 h=9\\pi h$ עם $r=3$ קבוע. לכן $\\dfrac{dV}{dt}=9\\pi\\dfrac{dh}{dt}$. נתון $\\dfrac{dV}{dt}=2$ מ³/דק': $2=9\\pi\\dfrac{dh}{dt}$, ולכן $\\dfrac{dh}{dt}=\\dfrac{2}{9\\pi}\\approx 0.071$ מ'/דק'.",
        "בגליל ברדיוס קבוע, $V$ תלוי לינארית ב-$h$. רק $h$ משתנה — הגזירה פשוטה, בלי כלל מכפלה.",
        "גזירת $V=\\pi r^2 h$ כאילו גם $r$ משתנה, או שימוש ב-$dV/dt=2\\pi r\\,dr/dt$ (נוסחת שטח מעגל) במקום נגזרת נפח גליל.",
        "כשהרדיוס קבוע, כתבו $V=(\\pi r^2)h$ והתייחסו ל-$\\pi r^2$ כקבוע. זה חוסך שלבי כלל מכפלה מיותרים. בדקו ש-$dh/dt$ חיובי כשמים נכנסים למיכל.",
    ),
    6: fmt_expl(
        "Given $r=2h$, volume $V=\\dfrac{\\pi r^2 h}{3}=\\dfrac{4\\pi h^3}{3}$. Differentiate: $\\dfrac{dV}{dt}=4\\pi h^2\\dfrac{dh}{dt}$. At $h=3$ with $\\dfrac{dV}{dt}=5$: $5=36\\pi\\dfrac{dh}{dt}$, so $\\dfrac{dh}{dt}=\\dfrac{5}{36\\pi}\\approx 0.044$ m/min.",
        "Sand-pile and similar-cone problems require substituting the linear $r$-$h$ relation **before** differentiating. This gives $V$ as a single-variable function of $h$.",
        "Differentiating $V=\\pi r^2 h/3$ directly with both $r=2h$ and $h$ changing without reducing first — leads to product-rule errors.",
        "When the problem states $r=kh$ always, your first algebraic move is $V(h)$ — not $dV/dt$ with two independent rates.",
        "נתון $r=2h$, נפח $V=\\dfrac{\\pi r^2 h}{3}=\\dfrac{4\\pi h^3}{3}$. גזירה: $\\dfrac{dV}{dt}=4\\pi h^2\\dfrac{dh}{dt}$. ב-$h=3$ עם $\\dfrac{dV}{dt}=5$: $5=36\\pi\\dfrac{dh}{dt}$, כלומר $\\dfrac{dh}{dt}=\\dfrac{5}{36\\pi}\\approx 0.044$ מ'/דק'.",
        "גל חול וחרוטים דומים דורשים הצבת יחס $r$-$h$ **לפני** הגזירה. כך מקבלים $V$ כפונקציה של $h$ בלבד.",
        "גזירה ישירה של $V=\\pi r^2 h/3$ כשגם $r=2h$ וגם $h$ משתנים בלי צמצום קודם — מובילה לטעויות כלל מכפלה.",
        "כשהניסוח אומר $r=kh$ תמיד, הצעד האלגברי הראשון הוא $V(h)$ — לא $dV/dt$ עם שני קצבים בלתי תלויים.",
    ),
    7: fmt_expl(
        "Let $x$ = horizontal distance, $L$ = string length, fixed height 100 m: $L^2=x^2+100^2$. When $L=150$, $x=50\\sqrt{5}$. Differentiate: $2L\\dfrac{dL}{dt}=2x\\dfrac{dx}{dt}$, so $\\dfrac{dL}{dt}=\\dfrac{x\\,dx/dt}{L}=\\dfrac{5\\sqrt{5}}{3}\\approx 3.73$ m/s.",
        "Kite/string problems are Pythagoras with a fixed vertical leg. Differentiate the general equation, then compute $x$ from the given string length before the final substitution.",
        "Using $dL/dt=dx/dt$ directly, or forgetting to find $x=50\\sqrt{5}$ from $L=150$ and height 100.",
        "For string problems, write $L^2=x^2+h^2$ with $h$ constant so $\\dfrac{dL}{dt}=\\dfrac{x}{L}\\dfrac{dx}{dt}$ — a formula worth memorizing.",
        "נסמן $x$ = מרחק אופקי, $L$ = אורך מחרוזת, גובה קבוע 100 מ': $L^2=x^2+100^2$. כאשר $L=150$, $x=50\\sqrt{5}$. גזירה: $2L\\dfrac{dL}{dt}=2x\\dfrac{dx}{dt}$, כלומר $\\dfrac{dL}{dt}=\\dfrac{x\\,dx/dt}{L}=\\dfrac{5\\sqrt{5}}{3}\\approx 3.73$ מ'/שנ'.",
        "בעיות עפיפון/מחרוזת הן פיתגורס עם ניצב אנכי קבוע. גזרו את המשוואה הכללית, ואז חשבו $x$ מאורך המחרוזת לפני ההצבה.",
        "שימוש ב-$dL/dt=dx/dt$ ישירות, או שכחת מציאת $x=50\\sqrt{5}$ מ-$L=150$ וגובה 100.",
        "בבעיות מחרוזת, כתבו $L^2=x^2+h^2$ עם $h$ קבוע כדי לקבל $\\dfrac{dL}{dt}=\\dfrac{x}{L}\\dfrac{dx}{dt}$ — נוסחה שכדאי לשמור.",
    ),
    8: fmt_expl(
        "Area $A=lw$. Product rule: $\\dfrac{dA}{dt}=l\\dfrac{dw}{dt}+w\\dfrac{dl}{dt}$. With $l=10$, $w=6$, $\\dfrac{dl}{dt}=4$, $\\dfrac{dw}{dt}=-2$: $\\dfrac{dA}{dt}=10(-2)+6(4)=-20+24=4$ cm²/s.",
        "When **both** dimensions change, you need the full product rule — not just one term. Width decreasing ($dw/dt<0$) partially cancels length increasing.",
        "Using $dA/dt=(dl/dt)(dw/dt)$ or only one term of the product rule; also dropping the negative on $dw/dt=-2$.",
        "Rectangle area rate is a classic product-rule checkpoint. Write both terms before plugging numbers — exam rubrics often award partial credit for the correct formula.",
        "שטח $A=lw$. כלל מכפלה: $\\dfrac{dA}{dt}=l\\dfrac{dw}{dt}+w\\dfrac{dl}{dt}$. עם $l=10$, $w=6$, $\\dfrac{dl}{dt}=4$, $\\dfrac{dw}{dt}=-2$: $\\dfrac{dA}{dt}=10(-2)+6(4)=-20+24=4$ ס\"מ²/שנ'.",
        "כש**שני** הממדים משתנים, צריך כלל מכפלה מלא — לא איבר אחד בלבד. רוחב קטן ($dw/dt<0$) מבטל חלקית את גידול האורך.",
        "שימוש ב-$dA/dt=(dl/dt)(dw/dt)$ או רק באיבר אחד של כלל המכפלה; גם השמטת השלילי ב-$dw/dt=-2$.",
        "קצב שינוי שטח מלבן הוא checkpoint קלאסי של כלל מכפלה. כתבו שני האיברים לפני הצבת מספרים — לעיתים יש נקודות חלקיות על הנוסחה הנכונה.",
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
            if "13 m" in body or "13 מ" in body:
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
