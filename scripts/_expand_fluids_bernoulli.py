#!/usr/bin/env python3
"""Generate expanded fluids_bernoulli.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/fluids_bernoulli.json"
OUT = SRC

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
    if not en:
        return hebrew_char_ratio(he) < 0.12
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    if hebrew_char_ratio(he) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


EXPLANATIONS = {
    1: {
        "en": (
            "Bernoulli's equation for a horizontal pipe ($h$ constant) reduces to "
            "$P + \\frac{1}{2}\\rho v^2 = \\text{const}$. The three terms trade off: "
            "where speed $v$ increases, static pressure $P$ must decrease to keep the "
            "sum fixed. Option \"higher\" reverses the physics — students often think "
            "fast flow \"pushes harder.\" \"Unchanged\" ignores energy conversion; "
            "\"zero\" is nonsensical unless the fluid stops entirely. "
            "This inverse relation drives airplane lift, Venturi meters, and atomizers. "
            "Sanity check: narrow a garden hose — water speeds up and the stream feels "
            "less \"pushy\" sideways. **Exam tip:** write the horizontal form first, "
            "circle which variable grows, then deduce pressure. **Answer:** lower."
        ),
        "he": (
            "משוואת ברנולי בצינור אופקי ($h$ קבוע) מתצמצמת ל-"
            "$P + \\frac{1}{2}\\rho v^2 = \\text{const}$. שלושת האיברים מתמחרים: "
            "כשמהירות $v$ גדלה, לחץ סטטי $P$ חייב לרדת כדי לשמור על הסכום. "
            "האפשרות \"גבוה יותר\" הופכת את הפיזיקה — תלמידים חושבים שזרימה מהירה "
            "\"דוחפת חזק יותר.\" \"ללא שינוי\" מתעלם מהמרת אנרגיה; "
            "\"אפס\" לא הגיוני אלא אם הנוזל נעצר לגמרי. "
            "הקשר ההפוך הזה מניע עילוי מטוסים, מדי ונטורי ואטומייזרים. "
            "בדיקת הגיון: צמצמו צינור השקיה — המים מאיצים והזרם פחות \"דוחף\" לצד. "
            "**טיפ לבחינה:** כתבו את הצורה האופקית, סמנו מה גדל, ואז הסיקו לחץ. "
            "**תשובה:** נמוך יותר."
        ),
    },
    2: {
        "en": (
            "Torricelli's theorem gives exit speed from a draining tank: "
            "$v = \\sqrt{2gH}$. Substituting $H = 3.2$ m and $g = 10$ m/s$^2$: "
            "$v = \\sqrt{2(10)(3.2)} = \\sqrt{64} = 8$ m/s. "
            "This equals the speed of an object dropped freely from height $H$ — "
            "potential energy per unit volume $\\rho g H$ converts entirely to "
            "kinetic $\\frac{1}{2}\\rho v^2$. Common errors: using $v = gH$ "
            "(wrong dimensions), forgetting the square root, or using $H$ in cm "
            "without converting. If you got 6.4 m/s you multiplied $2gH$ without "
            "the root. **Exam tip:** always check units — m/s requires "
            "$\\sqrt{\\text{m}/\\text{s}^2 \\times \\text{m}}$. **Answer:** 8 m/s."
        ),
        "he": (
            "משפט טוריצ'לי נותן מהירות יציאה ממיכל מנקז: $v = \\sqrt{2gH}$. "
            "הצבה: $H = 3.2$ m, $g = 10$ m/s$^2$: "
            "$v = \\sqrt{2(10)(3.2)} = \\sqrt{64} = 8$ m/s. "
            "זה שווה למהירות גוף שנפל חופשית מגובה $H$ — "
            "אנרגיה פוטנציאלית $\\rho g H$ מתמרת לגמרי לקינטית "
            "$\\frac{1}{2}\\rho v^2$. טעויות נפוצות: $v = gH$ (יחידות שגויות), "
            "שכחת שורש, או $H$ בס\"מ בלי המרה. "
            "אם קיבלתם 6.4 m/s — כפלתם $2gH$ בלי שורש. "
            "הגזירה מניחה מיכל גדול ($v_{\\text{פני}} \\approx 0$) "
            "ולחץ אטמוספרי בחור. השוו לנפילה חופשית מ-3.2 m. "
            "**טיפ לבחינה:** בדקו יחידות — m/s דורש "
            "$\\sqrt{\\text{m}/\\text{s}^2 \\times \\text{m}}$. **תשובה:** 8 m/s."
        ),
    },
    3: {
        "en": (
            "Continuity conserves volume flow rate: $A_1 v_1 = A_2 v_2$. "
            "Areas scale with radius squared: $A = \\pi r^2$, so "
            "$A_1/A_2 = (r_1/r_2)^2 = (4/2)^2 = 4$. "
            "Therefore $v_2 = v_1 \\times (A_1/A_2) = 3 \\times 4 = 12$ m/s. "
            "Students often use the linear ratio $r_1/r_2 = 2$ and get 6 m/s — "
            "forgetting area is two-dimensional. Another slip: dividing instead "
            "of multiplying when the pipe narrows. "
            "Sanity check: smaller cross-section means faster flow, so 12 > 3. "
            "Apply continuity before Bernoulli in every pipe problem. "
            "The area ratio $(4/2)^2 = 4$ is the key step — not the radius ratio 2. "
            "If the pipe widened instead, $v_2$ would be slower than $v_1$. "
            "**Exam tip:** write $A_1 v_1 = A_2 v_2$ and convert radii to areas first. "
            "**Answer:** 12 m/s."
        ),
        "he": (
            "משוואת הרציפות שומרת על ספיקת נפח: $A_1 v_1 = A_2 v_2$. "
            "שטחים פרופורצionalי לרדיוס בריבוע: $A = \\pi r^2$, ולכן "
            "$A_1/A_2 = (r_1/r_2)^2 = (4/2)^2 = 4$. "
            "מכאן $v_2 = v_1 \\times (A_1/A_2) = 3 \\times 4 = 12$ m/s. "
            "תלמידים משתמשים לעיתים ביחס לינארי $r_1/r_2 = 2$ ומקבלים 6 m/s — "
            "שכחו שהשטח דו-ממדי. טעות נוספת: חלוקה במקום כפל כשהצינור מצטמצם. "
            "בדיקת הגיון: חתך קטן יותר = זרימה מהירה יותר, ולכן 12 > 3. "
            "הפעילו רציפות לפני ברנולי בכל בעיית צינור. "
            "יחס השטח $(4/2)^2 = 4$ הוא הצעד המפתח — לא יחס הרדיוס 2. "
            "**טיפ לבחינה:** כתבו $A_1 v_1 = A_2 v_2$ והמירו רדיוסים לשטחים קודם. "
            "**תשובה:** 12 m/s."
        ),
    },
    4: {
        "en": (
            "Torricelli applies when a large tank drains through a small hole: "
            "$v = \\sqrt{2gH}$. With $H = 8$ m and $g = 10$ m/s$^2$ (standard exam "
            "value): $v = \\sqrt{2(10)(8)} = \\sqrt{160} \\approx 12.65$ m/s, "
            "often rounded to 12.6 m/s. The derivation assumes $v_1 \\approx 0$ at "
            "the free surface (large tank) and $P_1 = P_2 = P_{\\text{atm}}$ at the hole. "
            "If you got 80 m/s you forgot the square root. If you got 16 m/s you "
            "used $v = 2gH$ without the root. "
            "Compare to free fall: an object dropped 8 m also hits 12.6 m/s. "
            "The derivation cancels atmospheric pressure at both points. "
            "Do not use $v = 2gH$ — that gives 160 m/s, wrong by a factor of $\\sqrt{2gH}$. "
            "**Exam tip:** label $H$ as height above the hole, not tank depth below ground. "
            "**Answer:** $\\approx 12.6$ m/s."
        ),
        "he": (
            "טוריצ'לי חל כשמיכל גדול מתנקז דרך חור קטן: $v = \\sqrt{2gH}$. "
            "עם $H = 8$ m ו-$g = 10$ m/s$^2$: "
            "$v = \\sqrt{2(10)(8)} = \\sqrt{160} \\approx 12.65$ m/s, "
            "לעיתים מעוגל ל-12.6 m/s. הגזירה מניחה $v_1 \\approx 0$ בפני המים "
            "(מיכל גדול) ו-$P_1 = P_2 = P_{\\text{atm}}$ בחור. "
            "אם קיבלתם 80 m/s — שכחתם שורש. אם 16 m/s — השתמשתם ב-$v = 2gH$. "
            "השוו לנפילה חופשית: גוף מ-8 m גם מגיע ל-12.6 m/s. "
            "הגזירה מבטלת לחץ אטמוספרי בשני הנקודות. "
            "אל תשתמשו ב-$v = 2gH$ — זה נותן 160 m/s, שגוי. "
            "**טיפ לבחינה:** $H$ = גובה מעל החור, לא עומק המיכל מתחת לקרקע. "
            "**תשובה:** $\\approx 12.6$ m/s."
        ),
    },
    5: {
        "en": (
            "Flow rate $Q$ (m$^3$/s) equals cross-sectional area times velocity: "
            "$Q = Av$, so $v = Q/A$. Substituting $Q = 0.05$ m$^3$/s and "
            "$A = 0.01$ m$^2$: $v = 0.05/0.01 = 5$ m/s. "
            "This is the simplest continuity application — no narrowing, just "
            "relating bulk flow to local speed. "
            "Common errors: multiplying $Q \\times A$ instead of dividing, "
            "or using diameter instead of area. "
            "Units check: (m$^3$/s)/(m$^2$) = m/s ✓. "
            "Once you know $v$, Bernoulli can give pressure at any point along the pipe. "
            "**Exam tip:** $Q = Av$ is continuity for a single section — "
            "memorize it alongside $A_1 v_1 = A_2 v_2$. **Answer:** 5 m/s."
        ),
        "he": (
            "ספיקה $Q$ (m$^3$/s) שווה שטח כפול מהירות: $Q = Av$, ולכן $v = Q/A$. "
            "הצבה: $Q = 0.05$ m$^3$/s, $A = 0.01$ m$^2$: $v = 0.05/0.01 = 5$ m/s. "
            "זה היישום הפשוט ביותר של רציפות — בלי צמצום, רק קשר בין ספיקה למהירות. "
            "טעויות נפוצות: כפל $Q \\times A$ במקום חלוקה, "
            "או שימוש בקוטר במקום שטח. "
            "בדיקת יחידות: (m$^3$/s)/(m$^2$) = m/s ✓. "
            "ברגע שידוע $v$, ברנולי נותן לחץ בכל נקודה בצינור. "
            "**טיפ לבחינה:** $Q = Av$ היא רציפות לחתך בודד — "
            "שננו לצד $A_1 v_1 = A_2 v_2$. **תשובה:** 5 m/s."
        ),
    },
    6: {
        "en": (
            "Bernoulli's equation $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ "
            "expresses energy conservation per unit volume along a streamline. "
            "$P$ is **static pressure** — the force fluid exerts when not moving. "
            "$\\frac{1}{2}\\rho v^2$ is **dynamic pressure**, kinetic energy per unit "
            "volume (sometimes called velocity head). "
            "$\\rho g h$ is **gravitational potential energy** per unit volume "
            "(elevation head). All three are in pascals (N/m$^2$) when $\\rho$ is kg/m$^3$. "
            "Students confuse dynamic pressure with total pressure, or forget "
            "$h$ is height above a reference. "
            "**Exam tip:** label each term with its physical name before substituting numbers. "
            "**Answer:** the full equation with all three terms identified."
        ),
        "he": (
            "משוואת ברנולי $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ "
            "מבטאת שימור אנרגיה לנפח יחידה על קו זרימה. "
            "$P$ הוא **לחץ סטטי** — הכוח שהנוזל מפעיל כשאינו נע. "
            "$\\frac{1}{2}\\rho v^2$ הוא **לחץ דינמי**, אנרגיה קינטית לנפח יחידה. "
            "$\\rho g h$ הוא **אנרגיה פוטנציאלית כבידתית** לנפח יחידה (גובה). "
            "שלושתם ב-pascal (N/m$^2$) כש-$\\rho$ ב-kg/m$^3$. "
            "תלמידים מבלבלים לחץ דינמי עם לחץ כולל, או שוכחים ש-$h$ הוא גובה מעל ייחוס. "
            "**טיפ לבחינה:** סמנו כל איבר בשם הפיזיקלי שלו לפני הצבת מספרים. "
            "**תשובה:** המשוואה המלאה עם זיהוי שלושת האיברים."
        ),
    },
    7: {
        "en": (
            "A Venturi meter combines continuity and Bernoulli in two clear steps. "
            "First find velocity ratio: $A_2 = A_1/4$ so $v_2 = 4v_1$ (continuity). "
            "Horizontal pipe: $\\Delta P = P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2)$ "
            "$= \\frac{1}{2}(1000)(16v_1^2 - v_1^2) = 7500 v_1^2 = 10000$ Pa. "
            "So $v_1 = \\sqrt{10000/7500} = \\sqrt{4/3} \\approx 1.155$ m/s. "
            "Flow rate: $Q = A_1 v_1 = 0.02 \\times 1.155 \\approx 0.0231$ m$^3$/s. "
            "If you got $Q = 0.1$ you used $v_2$ instead of $v_1$ for $Q = Av$. "
            "Another trap: using $\\Delta P = \\frac{1}{2}\\rho(v_1^2 - v_2^2)$ "
            "with wrong sign — throat has lower $P$, so $P_1 > P_2$. "
            "The factor $16v_1^2 - v_1^2 = 15v_1^2$ comes from $v_2 = 4v_1$. "
            "**Exam tip:** always compute $v_1$ from $\\Delta P$, then $Q = A_1 v_1$. "
            "**Answer:** $Q \\approx 0.023$ m$^3$/s."
        ),
        "he": (
            "מד ונטורי משלב רציפות וברנולי בשני שלבים ברורים. "
            "קודם יחס מהירויות: $A_2 = A_1/4$ ולכן $v_2 = 4v_1$ (רציפות). "
            "צינור אופקי: $\\Delta P = \\frac{1}{2}\\rho(v_2^2 - v_1^2) "
            "= \\frac{1}{2}(1000)(16v_1^2 - v_1^2) = 7500 v_1^2 = 10000$ Pa. "
            "מכאן $v_1 = \\sqrt{10000/7500} = \\sqrt{4/3} \\approx 1.155$ m/s. "
            "ספיקה: $Q = A_1 v_1 = 0.02 \\times 1.155 \\approx 0.0231$ m$^3$/s. "
            "אם קיבלתם $Q = 0.1$ — השתמשתם ב-$v_2$ במקום $v_1$ ל-$Q = Av$. "
            "מלכודת נוספת: סימן שגוי ב-$\\Delta P$ — בצוואר $P$ נמוך יותר, "
            "ולכן $P_1 > P_2$. "
            "הגורם $16v_1^2 - v_1^2 = 15v_1^2$ נובע מ-$v_2 = 4v_1$. "
            "זכרו: $A_2 = A_1/4$ מכפיל את $v_2$ פי 4, לא פי 2. "
            "**טיפ לבחינה:** חשבו $v_1$ מ-$\\Delta P$, ואז $Q = A_1 v_1$. "
            "**תשובה:** $Q \\approx 0.023$ m$^3$/s."
        ),
    },
    8: {
        "en": (
            "Airplane lift follows from Bernoulli pressure difference. "
            "Faster flow over the curved upper surface ($v_2 = 80$ m/s) creates "
            "lower pressure than the slower underside ($v_1 = 60$ m/s). "
            "$\\Delta P = \\frac{1}{2}\\rho(v_2^2 - v_1^2) "
            "= \\frac{1}{2}(1.2)(6400 - 3600) = 0.6 \\times 2800 = 1680$ Pa. "
            "Lift force: $F = \\Delta P \\times A = 1680 \\times 20 = 33600$ N "
            "$\\approx 33.6$ kN. Note $v_2 > v_1$ so $\\Delta P > 0$ (upward push). "
            "Real wings also use angle of attack; Bernoulli is a simplified model. "
            "If you subtracted velocities instead of squaring, you get wrong $\\Delta P$. "
            "The force direction is upward because $P_{\\text{bottom}} > P_{\\text{top}}$. "
            "33.6 kN is reasonable for a small aircraft wing section at cruise speed. "
            "**Exam tip:** lift = pressure difference $\\times$ wing area, not $\\rho v$. "
            "**Answer:** $\\approx 33.6$ kN."
        ),
        "he": (
            "עילוי מטוס נובע מהפרש לחצים בברנולי. "
            "זרימה מהירה יותר מעל הכנף ($v_2 = 80$ m/s) יוצרת "
            "לחץ נמוך יותר מהתחתית ($v_1 = 60$ m/s). "
            "$\\Delta P = \\frac{1}{2}\\rho(v_2^2 - v_1^2) "
            "= \\frac{1}{2}(1.2)(6400 - 3600) = 0.6 \\times 2800 = 1680$ Pa. "
            "כוח עילוי: $F = \\Delta P \\times A = 1680 \\times 20 = 33600$ N "
            "$\\approx 33.6$ kN. שימו לב: $v_2 > v_1$ ולכן $\\Delta P > 0$ (דחיפה כלפי מעלה). "
            "כנפיים אמיתיות משתמשות גם בזווית התקפה; ברנולי הוא מודל מפושט. "
            "אם חיסרתם מהירויות במקום בריבוע — $\\Delta P$ שגוי. "
            "כיוון הכוח כלפי מעלה כי $P_{\\text{תחתון}} > P_{\\text{עליון}}$. "
            "33.6 kN סביר לקטע כנף קטן במהירות שיוט. "
            "**טיפ לבחינה:** עילוי = הפרש לחץ $\\times$ שטח כנף, לא $\\rho v$. "
            "**תשובה:** $\\approx 33.6$ kN."
        ),
    },
}

SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "Why does an airplane wing generate lift? Why does squeezing a perfume "
            "atomizer pull liquid up the tube? The answer lies in **Bernoulli's "
            "principle**: in steady ideal flow, **faster motion means lower static "
            "pressure**. When air races over a curved wing top, pressure drops and "
            "the higher pressure below pushes the wing upward.\n\n"
            "Combined with the **continuity equation** ($A_1 v_1 = A_2 v_2$), "
            "Bernoulli's equation describes steady fluid flow in pipes, nozzles, "
            "and around objects. Every term in "
            "$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ "
            "represents energy per unit volume along a streamline.\n\n"
            "**Exam topics:**\n"
            "- Continuity equation and flow rate $Q = Av$\n"
            "- Bernoulli's equation (horizontal and with height change)\n"
            "- Venturi meter, Torricelli's theorem\n"
            "- Applications: airplane lift, atomizers, carburetors, pitot tubes"
        ),
        "body_he_md": (
            "מדוע כנף מטוס מייצרת עילוי? מדוע לחיצה על אטומייזר בושם "
            "מושכת נוזל למעלה בצינור? התשובה ב**עיקרון ברנולי**: "
            "בזרימה יציבה אידיאלית, **תנועה מהירה יותר = לחץ סטטי נמוך יותר**. "
            "כשאוויר עובר מהר מעל גב כנף מעוקל, הלחץ יורד והלחץ הגבוה יותר "
            "מלמטה דוחף את הכנף כלפי מעלה.\n\n"
            "יחד עם **משוואת הרציפות** ($A_1 v_1 = A_2 v_2$), "
            "משוואת ברנולי מתארת זרימת נוזל יציבה בצינורות, "
            "בזרבובים וסביב גופים. כל איבר ב-"
            "$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ "
            "מייצג אנרגיה לנפח יחידה על קו זרימה.\n\n"
            "**נושאי בחינה:**\n"
            "- משוואת רציפות וספיקה $Q = Av$\n"
            "- משוואת ברנולי (אופקית ועם שינוי גובה)\n"
            "- מד ונטורי, משפט טוריצ'לי\n"
            "- יישומים: עילוי, אטומייזר, קרבורטור, צינור פיטו"
        ),
    },
    "definition": {
        "body_en_md": (
            "**Continuity equation** (incompressible fluid, area $A$, velocity $v$):\n"
            "$$A_1 v_1 = A_2 v_2 \\quad (\\text{flow rate } Q = Av = \\text{const})$$\n\n"
            "Volume entering a pipe segment per second must equal volume leaving — "
            "fluid cannot accumulate in a rigid pipe. Narrower cross-section "
            "forces faster flow.\n\n"
            "**Bernoulli's equation** (along a streamline, ideal fluid):\n"
            "$$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$$\n\n"
            "Between two points:\n"
            "$$P_1 + \\frac{1}{2}\\rho v_1^2 + \\rho g h_1 = "
            "P_2 + \\frac{1}{2}\\rho v_2^2 + \\rho g h_2$$\n\n"
            "$P$ = static pressure; $\\frac{1}{2}\\rho v^2$ = dynamic pressure; "
            "$\\rho g h$ = gravitational head. All in pascals.\n\n"
            "**Torricelli's theorem** (fluid draining from large tank, hole at depth $H$):\n"
            "$$v = \\sqrt{2gH}$$\n\n"
            "Exit speed equals free-fall speed from height $H$.\n\n"
            "**Venturi effect** (horizontal pipe, $h_1 = h_2$):\n"
            "$$P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2)$$\n\n"
            "Pressure drop measures the velocity increase — basis of Venturi meters.\n\n"
            "**Units reminder:** $P$ in pascals (Pa), $v$ in m/s, $h$ in m, "
            "$\\rho$ in kg/m$^3$. Flow rate $Q$ in m$^3$/s. "
            "Convert cm$^2$ to m$^2$ and kPa to Pa before substituting."
        ),
        "body_he_md": (
            "**משוואת רציפות** (נוזל בלתי דחיס, שטח $A$, מהירות $v$):\n"
            "$$A_1 v_1 = A_2 v_2 \\quad (\\text{ספיקה } Q = Av = \\text{const})$$\n\n"
            "נפח הנכנס לקטע צינור בשנייה חייב להיות שווה לנפח היוצא — "
            "נוזל לא יכול להצטבר בצינור קשיח. חתך צר יותר "
            "מאלץ זרימה מהירה יותר.\n\n"
            "**משוואת ברנולי** (על קו זרימה, נוזל אידיאלי):\n"
            "$$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$$\n\n"
            "בין שתי נקודות:\n"
            "$$P_1 + \\frac{1}{2}\\rho v_1^2 + \\rho g h_1 = "
            "P_2 + \\frac{1}{2}\\rho v_2^2 + \\rho g h_2$$\n\n"
            "$P$ = לחץ סטטי; $\\frac{1}{2}\\rho v^2$ = לחץ דינמי; "
            "$\\rho g h$ = גובה הידראולי. הכל ב-pascal.\n\n"
            "**משפט טוריצ'לי** (ניקוז ממיכל גדול, חור בעומק $H$):\n"
            "$$v = \\sqrt{2gH}$$\n\n"
            "מהירות יציאה שווה למהירות נפילה חופשית מגובה $H$.\n\n"
            "**אפקט ונטורי** (צינור אופקי, $h_1 = h_2$):\n"
            "$$P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2)$$\n\n"
            "ירידת לחץ מודדת את עליית המהירות — בסיס למדי ונטורי.\n\n"
            "**תזכורת יחידות:** $P$ ב-pascal (Pa), $v$ ב-m/s, $h$ ב-m, "
            "$\\rho$ ב-kg/m$^3$. ספיקה $Q$ ב-m$^3$/s. "
            "המירו cm$^2$ ל-m$^2$ ו-kPa ל-Pa לפני ההצבה."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Deriving Bernoulli from Work-Energy\n"
            "For an ideal fluid (incompressible, inviscid, steady flow), consider a "
            "fluid element of volume $V$ moving along a streamline between points 1 "
            "and 2. Pressure forces do work; gravity does work; kinetic energy changes:\n"
            "$$W_{\\text{pressure}} + W_{\\text{gravity}} = \\Delta E_k$$\n"
            "$$(P_1 - P_2)V + \\rho Vg(h_1 - h_2) = "
            "\\frac{1}{2}\\rho V(v_2^2 - v_1^2)$$\n"
            "Divide by $V$:\n"
            "$$P_1 + \\rho g h_1 + \\frac{1}{2}\\rho v_1^2 = "
            "P_2 + \\rho g h_2 + \\frac{1}{2}\\rho v_2^2$$\n\n"
            "### Assumptions (exam traps if violated)\n"
            "Bernoulli's equation is valid only for:\n"
            "- **Steady** (not turbulent) flow\n"
            "- **Incompressible** fluid ($\\rho$ = const)\n"
            "- **Inviscid** (no viscosity — no energy lost to friction)\n"
            "- Along a **single streamline** (not across streamlines)\n\n"
            "### Torricelli's theorem derivation\n"
            "Apply Bernoulli between tank surface (large, $v_1 \\approx 0$, "
            "$P_1 = P_{\\text{atm}}$, $h_1 = H$) and hole "
            "($P_2 = P_{\\text{atm}}$, $h_2 = 0$):\n"
            "$$P_{\\text{atm}} + \\rho g H = P_{\\text{atm}} + "
            "\\frac{1}{2}\\rho v_2^2 \\Rightarrow v_2 = \\sqrt{2gH}$$\n\n"
            "### Physical intuition\n"
            "Energy converts between pressure, motion, and height — but the total "
            "per unit volume stays constant. Speed up at constant height → pressure drops.\n\n"
            "### Connecting to hydrostatics\n"
            "When $v = 0$, Bernoulli reduces to $P_1 + \\rho g h_1 = P_2 + \\rho g h_2$ — "
            "the same pressure-height relation from `concept:fluids_hydrostatics`. "
            "Dynamic pressure adds to the story when the fluid moves."
        ),
        "body_he_md": (
            "### גזירת ברנולי מעבודה-אנרגיה\n"
            "לנוזל אידיאלי (בלתי דחיס, ללא צמיגות, זרימה יציבה), "
            "שקלו אלמנט נוזל בנפח $V$ הנע על קו זרימה בין נקודות 1 ו-2. "
            "כוחות לחץ מבצעים עבודה; כבידה מבצעת עבודה; אנרגיה קינטית משתנה:\n"
            "$$W_{\\text{לחץ}} + W_{\\text{כבידה}} = \\Delta E_k$$\n"
            "$$(P_1 - P_2)V + \\rho Vg(h_1 - h_2) = "
            "\\frac{1}{2}\\rho V(v_2^2 - v_1^2)$$\n"
            "חלוקה ב-$V$:\n"
            "$$P_1 + \\rho g h_1 + \\frac{1}{2}\\rho v_1^2 = "
            "P_2 + \\rho g h_2 + \\frac{1}{2}\\rho v_2^2$$\n\n"
            "### הנחות (מלכודות בחינה אם מופרות)\n"
            "משוואת ברנולי תקפה רק עבור:\n"
            "- זרימה **יציבה** (לא טורבולנטית)\n"
            "- נוזל **בלתי דחיס** ($\\rho = \\text{const}$)\n"
            "- ללא **צמיגות** (אין אובדן אנרגיה לחיכוך)\n"
            "- על **קו זרימה יחיד** (לא בין קווי זרימה)\n\n"
            "### גזירת משפט טוריצ'לי\n"
            "ברנולי בין פני המיכל (גדול, $v_1 \\approx 0$, "
            "$P_1 = P_{\\text{atm}}$, $h_1 = H$) לחור "
            "($P_2 = P_{\\text{atm}}$, $h_2 = 0$):\n"
            "$$P_{\\text{atm}} + \\rho g H = P_{\\text{atm}} + "
            "\\frac{1}{2}\\rho v_2^2 \\Rightarrow v_2 = \\sqrt{2gH}$$\n\n"
            "### אינטואיציה פיזיקלית\n"
            "אנרגיה מתמרת בין לחץ, תנועה וגובה — "
            "אך הסכום לנפח יחידה נשאר קבוע. האצה בגובה קבוע → לחץ יורד.\n\n"
            "### קשר להידroסטטיקה\n"
            "כש-$v = 0$, ברנולי מתצמצם ל-$P_1 + \\rho g h_1 = P_2 + \\rho g h_2$ — "
            "אותו קשר לחץ-גובה מ-`concept:fluids_hydrostatics`. "
            "לחץ דינמי מוסיף לתמונה כשהנוזל נע."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** Water flows in a pipe. The cross-section narrows from "
            "$A_1 = 40\\;\\text{cm}^2$ to $A_2 = 10\\;\\text{cm}^2$. "
            "At the wide section, $v_1 = 2\\;\\text{m/s}$. Find $v_2$ and flow rate $Q$.\n\n"
            "### Move 1: Apply continuity\n"
            "$$A_1 v_1 = A_2 v_2 \\quad \\Rightarrow \\quad "
            "v_2 = \\frac{A_1 v_1}{A_2} = \\frac{40 \\times 2}{10} = 8\\;\\text{m/s}$$\n\n"
            "### Move 2: Find flow rate\n"
            "$$Q = A_1 v_1 = 40 \\times 10^{-4} \\times 2 = 8 \\times 10^{-3}\\;\\text{m}^3/\\text{s}$$\n\n"
            "### Move 3: Verify and interpret\n"
            "The pipe narrows by factor 4, so speed quadruples — 8 m/s is four times 2 m/s ✓. "
            "Flow rate is the same at both sections: "
            "$Q = A_2 v_2 = 10 \\times 10^{-4} \\times 8 = 8 \\times 10^{-3}$ m$^3$/s ✓. "
            "Always convert cm$^2$ to m$^2$ before multiplying. "
            "This problem uses only continuity — no Bernoulli needed yet.\n\n"
            "### Move 4: Exam tip\n"
            "When a problem gives areas and one velocity, continuity alone gives the other. "
            "Save Bernoulli for pressure questions. "
            "The narrowing ratio $A_1/A_2 = 4$ directly gives the speed ratio. "
            "**Answer:** $v_2 = 8$ m/s; $Q = 8 \\times 10^{-3}$ m$^3$/s."
        ),
        "body_he_md": (
            "**נתון:** מים זורמים בצינור. החתך מצטמצם מ-"
            "$A_1 = 40\\;\\text{cm}^2$ ל-$A_2 = 10\\;\\text{cm}^2$. "
            "בחלק הרחב, $v_1 = 2\\;\\text{m/s}$. מצאו $v_2$ וספיקה $Q$.\n\n"
            "### צעד 1: הפעלת רציפות\n"
            "$$A_1 v_1 = A_2 v_2 \\quad \\Rightarrow \\quad "
            "v_2 = \\frac{A_1 v_1}{A_2} = \\frac{40 \\times 2}{10} = 8\\;\\text{m/s}$$\n\n"
            "### צעד 2: מציאת ספיקה\n"
            "$$Q = A_1 v_1 = 40 \\times 10^{-4} \\times 2 = 8 \\times 10^{-3}\\;\\text{m}^3/\\text{s}$$\n\n"
            "### צעד 3: אימות ופרשנות\n"
            "הצינור מצטמצם פי 4, ולכן המהירות מוכפלת פי 4 — 8 m/s הוא פי 4 מ-2 m/s ✓. "
            "הספיקה זהה בשני החתכים: "
            "$Q = A_2 v_2 = 10 \\times 10^{-4} \\times 8 = 8 \\times 10^{-3}$ m$^3$/s ✓. "
            "המירו תמיד cm$^2$ ל-m$^2$ לפני הכפל. "
            "בעיה זו משתמשת רק ברציפות — עדיין לא צריך ברנולי.\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "כשנותנים שטחים ומהירות אחת, רציפות לבדה נותנת את השנייה. "
            "שמרו ברנולי לשאלות לחץ. "
            "יחס הצמצום $A_1/A_2 = 4$ נותן ישירות את יחס המהירות. "
            "**תשובה:** $v_2 = 8$ m/s; $Q = 8 \\times 10^{-3}$ m$^3$/s."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A horizontal Venturi meter has pipe area "
            "$A_1 = 50\\;\\text{cm}^2$ and throat area $A_2 = 10\\;\\text{cm}^2$. "
            "Water ($\\rho = 1000$ kg/m$^3$) flows at "
            "$Q = 0.02\\;\\text{m}^3/\\text{s}$. Find pressure difference $P_1 - P_2$.\n\n"
            "### Move 1: Find velocities from continuity\n"
            "$$v_1 = Q/A_1 = 0.02/(50 \\times 10^{-4}) = 4\\;\\text{m/s}$$\n"
            "$$v_2 = Q/A_2 = 0.02/(10 \\times 10^{-4}) = 20\\;\\text{m/s}$$\n\n"
            "### Move 2: Apply Bernoulli (horizontal, same height)\n"
            "$$P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2) "
            "= \\frac{1}{2}(1000)(400 - 16) = 192000\\;\\text{Pa} = 192\\;\\text{kPa}$$\n\n"
            "### Move 3: Verify\n"
            "Throat is 5× narrower → $v_2 = 5 v_1$ ✓ (20 = 5×4). "
            "Large $\\Delta P$ is typical for Venturi meters measuring flow. "
            "The wide section has higher pressure; the throat has higher speed.\n\n"
            "### Move 4: Exam tip\n"
            "Venturi problems always need two steps: (1) continuity for $v_1, v_2$ from $Q$, "
            "(2) Bernoulli for $\\Delta P$. Never skip step 1. "
            "The pressure drop of 192 kPa confirms significant speed increase at the throat. "
            "This is a standard two-equation pipeline: continuity then Bernoulli. "
            "Always label wide section as point 1 and throat as point 2. "
            "**Answer:** $P_1 - P_2 = 192$ kPa."
        ),
        "body_he_md": (
            "**נתון:** מד ונטורי אופקי: שטח צינור "
            "$A_1 = 50\\;\\text{cm}^2$, שטח צוואר $A_2 = 10\\;\\text{cm}^2$. "
            "מים ($\\rho = 1000$ kg/m$^3$) זורמים ב-"
            "$Q = 0.02\\;\\text{m}^3/\\text{s}$. מצאו הפרש לחץ $P_1 - P_2$.\n\n"
            "### צעד 1: מהירויות מרציפות\n"
            "$$v_1 = Q/A_1 = 0.02/(50 \\times 10^{-4}) = 4\\;\\text{m/s}$$\n"
            "$$v_2 = Q/A_2 = 0.02/(10 \\times 10^{-4}) = 20\\;\\text{m/s}$$\n\n"
            "### צעד 2: ברנולי (אופקי, אותו גובה)\n"
            "$$P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2) "
            "= \\frac{1}{2}(1000)(400 - 16) = 192000\\;\\text{Pa} = 192\\;\\text{kPa}$$\n\n"
            "### צעד 3: אימות\n"
            "הצוואר צר פי 5 → $v_2 = 5 v_1$ ✓ (20 = 5×4). "
            "$\\Delta P$ גדול אופייני למדי ונטורי. "
            "החלק הרחב בלחץ גבוה יותר; הצוואר במהירות גבוהה יותר.\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "בעיות ונטורי דורשות שני שלבים: (1) רציפות ל-$v_1, v_2$ מ-$Q$, "
            "(2) ברנולי ל-$\\Delta P$. לעולם אל תדלגו על שלב 1. "
            "ירידת לחץ של 192 kPa מאשרת עליית מהירות משמעותית בצוואר. "
            "זהו pipeline סטנדרטי: רציפות ואז ברנולי. "
            "**תשובה:** $P_1 - P_2 = 192$ kPa."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** Water flows in a pipe. At point 1: "
            "$P_1 = 2 \\times 10^5\\;\\text{Pa}$, $v_1 = 2\\;\\text{m/s}$, $h_1 = 0$. "
            "At point 2: $A_2 = A_1/2$, $h_2 = 3\\;\\text{m}$. Find $P_2$ "
            "($\\rho = 1000$ kg/m$^3$, $g = 10$ m/s$^2$).\n\n"
            "### Move 1: Continuity gives $v_2$\n"
            "$A_2 = A_1/2 \\Rightarrow v_2 = 2v_1 = 4\\;\\text{m/s}$\n\n"
            "### Move 2: Full Bernoulli from point 1 to 2\n"
            "$$P_2 = P_1 + \\frac{1}{2}\\rho v_1^2 + \\rho g h_1 "
            "- \\frac{1}{2}\\rho v_2^2 - \\rho g h_2$$\n"
            "$$= 2 \\times 10^5 + \\frac{1}{2}(1000)(4) + 0 "
            "- \\frac{1}{2}(1000)(16) - (1000)(10)(3)$$\n"
            "$$= 200000 + 2000 - 8000 - 30000 = 164000\\;\\text{Pa} = 1.64 \\times 10^5\\;\\text{Pa}$$\n\n"
            "### Move 3: Interpret\n"
            "Pressure drops because of both speed increase (Bernoulli) and climbing 3 m "
            "(hydrostatic). Each effect subtracts from $P_2$. "
            "Dynamic pressure loss: $\\frac{1}{2}(1000)(16-4) = 6000$ Pa. "
            "Hydrostatic loss: $1000 \\times 10 \\times 3 = 30000$ Pa.\n\n"
            "### Move 4: Exam tip\n"
            "When height AND area both change, use full Bernoulli — do not drop the "
            "$\\rho g h$ terms. Label $h$ positive upward from your reference. "
            "Total pressure drop: 36000 Pa from both dynamic and hydrostatic effects. "
            "This combined problem tests whether you keep all three Bernoulli terms. "
            "**Answer:** $P_2 = 164$ kPa."
        ),
        "body_he_md": (
            "**נתון:** מים בצינור. בנקודה 1: "
            "$P_1 = 2 \\times 10^5\\;\\text{Pa}$, $v_1 = 2\\;\\text{m/s}$, $h_1 = 0$. "
            "בנקודה 2: $A_2 = A_1/2$, $h_2 = 3\\;\\text{m}$. מצאו $P_2$ "
            "($\\rho = 1000$ kg/m$^3$, $g = 10$ m/s$^2$).\n\n"
            "### צעד 1: רציפות נותנת $v_2$\n"
            "$A_2 = A_1/2 \\Rightarrow v_2 = 2v_1 = 4\\;\\text{m/s}$\n\n"
            "### צעד 2: ברנולי מלא מנקודה 1 ל-2\n"
            "$$P_2 = P_1 + \\frac{1}{2}\\rho v_1^2 + \\rho g h_1 "
            "- \\frac{1}{2}\\rho v_2^2 - \\rho g h_2$$\n"
            "$$= 2 \\times 10^5 + \\frac{1}{2}(1000)(4) + 0 "
            "- \\frac{1}{2}(1000)(16) - (1000)(10)(3)$$\n"
            "$$= 200000 + 2000 - 8000 - 30000 = 164000\\;\\text{Pa} = 1.64 \\times 10^5\\;\\text{Pa}$$\n\n"
            "### צעד 3: פרשנות\n"
            "הלחץ יורד בגלל האצה (ברנולי) ועליה ב-3 m (הידroסטטי). "
            "כל אפקט מוריד מ-$P_2$. "
            "אובדן לחץ דינמי: $\\frac{1}{2}(1000)(16-4) = 6000$ Pa. "
            "אובדן הידroסטטי: $1000 \\times 10 \\times 3 = 30000$ Pa.\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "כשגובה ושטח שניהם משתנים, השתמשו בברנולי מלא — "
            "אל תוותרו על איברי $\\rho g h$. סמנו $h$ חיובי כלפי מעלה מהייחוס. "
            "ירידת לחץ כוללת: 36000 Pa מאפקטים דינמיים והידroסטטיים. "
            "בעיה משולבת זו בודקת אם שמרתם את שלושת איברי ברנולי. "
            "**תשובה:** $P_2 = 164$ kPa."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Problem Type | Method |\n"
            "|---|---|\n"
            "| Find $v_2$ from $v_1$ (pipe) | Continuity: $v_2 = v_1 A_1/A_2$ |\n"
            "| Find $P_2$ (same height) | Bernoulli: $P_2 = P_1 + \\frac{1}{2}\\rho(v_1^2 - v_2^2)$ |\n"
            "| Find $P_2$ (different heights) | Full Bernoulli with all three terms |\n"
            "| Speed from tank drain | Torricelli: $v = \\sqrt{2gH}$ |\n"
            "| Venturi meter | Continuity for $v_1, v_2$, then Bernoulli for $\\Delta P$ or $Q$ |\n"
            "| Lift on wing | $\\Delta P = \\frac{1}{2}\\rho(v_{\\text{top}}^2 - v_{\\text{bottom}}^2)$; "
            "$F = \\Delta P \\times A$ |\n\n"
            "**When to use:** Identify problem type first — continuity always before Bernoulli "
            "when areas change. Convert all areas to m$^2$ and pressures to Pa before substituting. "
            "**Tip:** Draw a diagram labelling points 1 and 2 with $P$, $v$, $h$ at each."
        ),
        "body_he_md": (
            "| סוג בעיה | שיטה |\n"
            "|---|---|\n"
            "| $v_2$ מ-$v_1$ (צינור) | רציפות: $v_2 = v_1 A_1/A_2$ |\n"
            "| $P_2$ (אותו גובה) | ברנולי: $P_2 = P_1 + \\frac{1}{2}\\rho(v_1^2 - v_2^2)$ |\n"
            "| $P_2$ (גובה שונה) | ברנולי מלא עם שלושת האיברים |\n"
            "| מיכל מנקז | טוריצ'לי: $v = \\sqrt{2gH}$ |\n"
            "| מד ונטורי | רציפות ל-$v_1, v_2$, ואז ברנולי ל-$\\Delta P$ או $Q$ |\n"
            "| עילוי כנף | $\\Delta P = \\frac{1}{2}\\rho(v_{\\text{עליון}}^2 - v_{\\text{תחתון}}^2)$; "
            "$F = \\Delta P \\times A$ |\n\n"
            "**מתי להשתמש:** זהו סוג בעיה קודם — רציפות תמיד לפני ברנולי "
            "כשהשטחים משתנים. המירו שטחים ל-m$^2$ ולחצים ל-Pa לפני הצבה. "
            "**טיפ:** שרטטו דיאגרמה עם נקודות 1 ו-2 ו-$P$, $v$, $h$ בכל נקודה."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Bernoulli only along a streamline.** Do not apply it across streamlines "
            "or in turbulent flow — the energy balance breaks down.\n\n"
            "2. **Continuity before Bernoulli.** Always find both velocities using "
            "$A_1 v_1 = A_2 v_2$ first, then apply Bernoulli for pressures.\n\n"
            "3. **Faster flow → lower pressure** (not higher). This is counterintuitive "
            "but correct for ideal fluids — the dynamic term $\\frac{1}{2}\\rho v^2$ "
            "steals from static $P$.\n\n"
            "4. **Torricelli assumes a large tank** ($v_1 \\approx 0$ at the free surface). "
            "If the tank is small, you must account for the falling surface speed.\n\n"
            "5. **Area vs radius.** Continuity uses cross-sectional area. "
            "Halving the radius quarters the area — and quadruples the speed.\n\n"
            "**Example misconception:** Higher velocity means higher pressure.\n\n"
            "**Fix:** The opposite is true: higher velocity means lower static pressure (Bernoulli)."
        ),
        "body_he_md": (
            "1. **ברנולי רק על קו זרימה** — אל תחילו בין קווי זרימה "
            "או בזרימה טורבולנטית; מאזן האנרגיה נשבר.\n\n"
            "2. **תחילה רציפות, אחר כך ברנולי** — מצאו תמיד שתי מהירויות "
            "ב-$A_1 v_1 = A_2 v_2$, ואז ברנולי ללחצים.\n\n"
            "3. **זרימה מהירה → לחץ נמוך** (לא גבוה). זה נגד אינטואיציה "
            "אך נכון לנוזלים אידיאליים — האיבר הדינמי "
            "$\\frac{1}{2}\\rho v^2$ \"גונב\" מהלחץ הסטטי $P$.\n\n"
            "4. **טוריצ'לי מניח מיכל גדול** ($v_1 \\approx 0$ בפני המים). "
            "במיכל קטן חייבים לחשב את מהירות ירידת פני המים.\n\n"
            "5. **שטח מול רדיוס.** רציפות משתמשת בשטח חתך. "
            "חציית הרדיוס מרבעת את השטח — ומכפילה פי 4 את המהירות.\n\n"
            "**טעות נפוצה:** מהירות גבוהה = לחץ גבוה.\n\n"
            "**תיקון:** ההפך נכון: מהירות גבוהה = לחץ סטטי נמוך (ברנולי)."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Bernoulli's equation connects **hydrostatics** (`concept:fluids_hydrostatics`) "
            "to full fluid dynamics — pressure, motion, and height trade off along every "
            "streamline. It reuses **work-energy** ideas from mechanics "
            "(`concept:work_energy_conservation`) but applied per unit volume of fluid.\n\n"
            "Engineers use Venturi meters to measure flow in pipelines; pilots rely on "
            "lift from pressure differences; doctors measure blood flow with similar devices. "
            "In university physics it bridges Mechanics II and Thermodynamics "
            "(`concept:uni_fluids`).\n\n"
            "**Why it matters for exams:** Bagrut and university courses test whether you "
            "can chain continuity → Bernoulli → interpret the result physically, not just "
            "plug numbers. Always ask: \"Does faster flow mean higher or lower pressure?\""
        ),
        "body_he_md": (
            "משוואת ברנולי מחברת **הידroסטטיקה** (`concept:fluids_hydrostatics`) "
            "לדינמיקת נוזלים מלאה — לחץ, תנועה וגובה מתמחרים על כל קו זרימה. "
            "היא משתמשת ברעיונות **עבודה-אנרגיה** ממכניקה "
            "(`concept:work_energy_conservation`) אך לנפח יחידה של נוזל.\n\n"
            "מהנדסים משתמשים במדי ונטורי למדידת ספיקה; טייסים סומכים על עילוי "
            "מהפרשי לחץ; רופאים מודדים זרימת דם במכשירים דומים. "
            "בפיזיקה אוניברסיטאית זה מגשר בין מכניקה II לתרמודינמיקה "
            "(`concept:uni_fluids`).\n\n"
            "**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה בודקים אם אתם יכולים "
            "לשרשר רציפות → ברנולי → לפרש פיזיקלית, לא רק להציב מספרים. "
            "שאלו תמיד: \"זרימה מהירה = לחץ גבוה או נמוך?\""
        ),
    },
    "before_exam": {
        "body_en_md": (
            "- **Continuity:** $A_1 v_1 = A_2 v_2$; $Q = Av$\n"
            "- **Bernoulli:** $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$\n"
            "- **Torricelli:** $v = \\sqrt{2gH}$\n"
            "- **Venturi (horizontal):** $P_1-P_2 = \\frac{1}{2}\\rho(v_2^2-v_1^2)$\n"
            "- **Lift:** $F = \\Delta P \\times A = \\frac{1}{2}\\rho(v_2^2-v_1^2)A$\n\n"
            "**Quick checklist:** (1) Convert all areas to m$^2$, pressures to Pa. "
            "(2) Continuity first if areas differ. (3) Bernoulli second for pressures. "
            "(4) Check: faster flow → lower $P$ at same height. "
            "(5) Torricelli: large tank, hole at depth $H$, both at $P_{\\text{atm}}$. "
            "(6) Lift: faster air above wing → lower pressure → upward force.\n\n"
            "**Last review:** Say each formula out loud once, then solve one checkpoint "
            "without looking. Remember: continuity first, Bernoulli second."
        ),
        "body_he_md": (
            "- **רציפות:** $A_1 v_1 = A_2 v_2$; $Q = Av$\n"
            "- **ברנולי:** $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$\n"
            "- **טוריצ'לי:** $v = \\sqrt{2gH}$\n"
            "- **ונטורי (אופקי):** $P_1-P_2 = \\frac{1}{2}\\rho(v_2^2-v_1^2)$\n"
            "- **עילוי:** $F = \\Delta P \\times A = \\frac{1}{2}\\rho(v_2^2-v_1^2)A$\n\n"
            "**רשימת בדיקה:** (1) המירו שטחים ל-m$^2$, לחצים ל-Pa. "
            "(2) רציפות קודם אם השטחים שונים. (3) ברנולי אחר כך ללחצים. "
            "(4) בדקו: זרימה מהירה → $P$ נמוך באותו גובה. "
            "(5) טוריצ'לי: מיכל גדול, חור בעומק $H$, שניהם ב-$P_{\\text{atm}}$.\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint "
            "אחד בלי להסתכל. זכרו: רציפות קודם, ברנולי אחר כך."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Continuity:** $A_1 v_1 = A_2 v_2$ — flow rate conserved in rigid pipes\n"
            "- **Bernoulli:** $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ "
            "— energy per unit volume along a streamline\n"
            "- **Key insight:** Fast flow → low pressure; slow flow → high pressure\n"
            "- **Torricelli:** $v = \\sqrt{2gH}$ — draining tank exit speed\n"
            "- **Applications:** Venturi meter, airplane lift, atomizer, pitot tube\n\n"
            "**Takeaway:** Identify problem type, apply continuity for velocities, "
            "then Bernoulli for pressures. Always check units and physical direction. "
            "The counterintuitive rule — fast flow means low pressure — appears on "
            "nearly every fluids exam."
        ),
        "body_he_md": (
            "- **רציפות:** $A_1 v_1 = A_2 v_2$ — ספיקה נשמרת בצינורות קשיחים\n"
            "- **ברנולי:** $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ "
            "— אנרגיה לנפח יחידה על קו זרימה\n"
            "- **תובנה מרכזית:** מהיר → לחץ נמוך; איטי → לחץ גבוה\n"
            "- **טוריצ'לי:** $v = \\sqrt{2gH}$ — מהירות יציאה ממיכל מנקז\n"
            "- **יישומים:** מד ונטורי, עילוי מטוס, אטומייזר, צינור פיטו\n\n"
            "**מסקנה:** זהו סוג בעיה, הפעילו רציפות למהירויות, "
            "ואז ברנולי ללחצים. בדקו תמיד יחידות וכיוון פיזיקלי. "
            "הכלל הנגד אינטואיציה — זרימה מהירה = לחץ נמוך — "
            "מופיע כמעט בכל בחינת נוזלים."
        ),
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "Torricelli's theorem applies: $v = \\sqrt{2gH}$.\n\n"
            "Substituting $H = 5$ m and $g = 10$ m/s$^2$:\n"
            "$$v = \\sqrt{2(10)(5)} = \\sqrt{100} = 10\\;\\text{m/s}$$\n\n"
            "**Check:** Units are m/s ✓. Compare to free fall from 5 m — same result. "
            "Assumes large tank ($v_{\\text{surface}} \\approx 0$) and atmospheric pressure "
            "at the hole. **Answer:** 10 m/s."
        ),
        "checkpoint_solution_he": (
            "משפט טוריצ'לי: $v = \\sqrt{2gH}$.\n\n"
            "הצבה: $H = 5$ m, $g = 10$ m/s$^2$:\n"
            "$$v = \\sqrt{2(10)(5)} = \\sqrt{100} = 10\\;\\text{m/s}$$\n\n"
            "**בדיקה:** יחידות m/s ✓. השוו לנפילה חופשית מ-5 m — אותה תוצאה. "
            "מניח מיכל גדול ($v_{\\text{פני}} \\approx 0$) ולחץ אטמוספרי בחור. "
            "**תשובה:** 10 m/s."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "### Move 1: Continuity\n"
            "$$v_2 = v_1 \\frac{A_1}{A_2} = 1 \\times \\frac{20}{5} = 4\\;\\text{m/s}$$\n\n"
            "### Move 2: Bernoulli (horizontal, $\\rho = 1000$ kg/m$^3$)\n"
            "$$P_2 = P_1 + \\frac{1}{2}\\rho(v_1^2 - v_2^2) "
            "= 300000 + \\frac{1}{2}(1000)(1 - 16) = 300000 - 7500 = 292500\\;\\text{Pa}$$\n\n"
            "**Check:** $P_2 < P_1$ because $v_2 > v_1$ — faster flow, lower pressure ✓. "
            "**Answer:** $P_2 = 292.5$ kPa."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: רציפות\n"
            "$$v_2 = v_1 \\frac{A_1}{A_2} = 1 \\times \\frac{20}{5} = 4\\;\\text{m/s}$$\n\n"
            "### צעד 2: ברנולי (אופקי, $\\rho = 1000$ kg/m$^3$)\n"
            "$$P_2 = P_1 + \\frac{1}{2}\\rho(v_1^2 - v_2^2) "
            "= 300000 + \\frac{1}{2}(1000)(1 - 16) = 300000 - 7500 = 292500\\;\\text{Pa}$$\n\n"
            "**בדיקה:** $P_2 < P_1$ כי $v_2 > v_1$ — זרימה מהירה, לחץ נמוך ✓. "
            "**תשובה:** $P_2 = 292.5$ kPa."
        ),
    },
}


def main():
    orig = json.loads(SRC.read_text(encoding="utf-8"))
    lesson = dict(orig)
    lesson["version"] = 2
    lesson["summary_en"] = (
        "Bernoulli's principle links faster flow to lower pressure. "
        "Master continuity, Bernoulli's equation, Torricelli's theorem, "
        "and Venturi applications for university fluid dynamics."
    )
    lesson["summary_he"] = (
        "עיקרון ברנולי מקשר זרימה מהירה ללחץ נמוך. "
        "שליטה ברציפות, משוואת ברנולי, משפט טוריצ'לי "
        "ויישומי ונטורי לדינמיקת נוזלים אוניברסיטאית."
    )

    for sec in lesson["sections"]:
        sid = sec.get("id", "")
        kind = sec["kind"]

        if kind in SECTION_BODIES:
            sec["body_en_md"] = SECTION_BODIES[kind]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[kind]["body_he_md"]
        elif sid in ("worked_example_1", "worked_example_2", "worked_example_3"):
            sec["body_en_md"] = SECTION_BODIES[sid]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[sid]["body_he_md"]
        elif sid in CHECKPOINTS:
            sec.update(CHECKPOINTS[sid])

    for q in lesson["questions"]:
        exp = EXPLANATIONS[q["ord"]]
        q["explanation_en"] = exp["en"]
        q["explanation_he"] = exp["he"]

    errors = []
    for sec in lesson["sections"]:
        kind = sec["kind"]
        sid = sec.get("id", "")
        key = kind if kind in SECTION_BODIES else sid if sid in SECTION_BODIES else None
        if key and key in MIN_WORDS:
            mw = MIN_WORDS[key if key in MIN_WORDS else kind]
        elif kind in MIN_WORDS:
            mw = MIN_WORDS[kind]
        else:
            continue
        for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
            wc = word_count(sec.get(field, ""))
            need = mw[lang]
            if wc < need:
                errors.append(f"{sec.get('id', kind)} {lang}: {wc} < {need}")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{sec.get('id', kind)}: hebrew_body_weak")

    for q in lesson["questions"]:
        for lang, field in [("en", "explanation_en"), ("he", "explanation_he")]:
            wc = word_count(q.get(field, ""))
            if wc < 80 or wc > 150:
                errors.append(f"Q{q['ord']} {lang}: {wc} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)

    OUT.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print("Running seed-lessons --dry-run...")
    subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
