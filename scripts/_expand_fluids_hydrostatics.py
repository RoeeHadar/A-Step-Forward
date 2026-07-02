#!/usr/bin/env python3
"""Generate expanded fluids_hydrostatics.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/fluids_hydrostatics.json"
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


SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "Why does a diver feel more pressure at depth? Why does a ship float while a coin sinks? "
            "**Fluid statics** answers these questions with just a few elegant principles — no motion "
            "required. Every scuba instructor, civil engineer, and medical student relies on the same "
            "formulas: pressure grows with depth, Pascal multiplies force in hydraulics, and Archimedes "
            "explains why objects float or sink.\n\n"
            "These concepts appear throughout high-school physics, Bagrut exams, and university "
            "engineering entrance tests. Master them here and they carry directly into "
            "`concept:fluids_bernoulli` when fluids start moving.\n\n"
            "**Key topics:**\n"
            "- Pressure definition and depth dependence ($P = P_0 + \\rho g h$)\n"
            "- Pascal's principle and hydraulic machines\n"
            "- Archimedes' principle, buoyancy, and floating conditions\n"
            "- Measuring density by weighing in air vs. fluid"
        ),
        "body_he_md": (
            "מדוע צולל חש ללחץ גדול יותר בעומק? מדוע ספינה צפה בעוד מטבע שוקע? "
            "**סטטיקת נוזלים** עונה על שאלות אלו עם מספר עקרונות אלגנטיים — בלי צורך בתנועה. "
            "כל מדריך צלילה, מהנדס אזרחי וסטודנט לרפואה מסתמך על אותן נוסחאות: לחץ גדל עם עומק, "
            "פסקל מכפיל כוח במכונות הידראוליות, וארכימדס מסביר מדוע גופים צפים או שוקעים.\n\n"
            "נושאים אלו מופיעים בפיזיקה תיכונית, בבגרות ובמבחני כניסה להנדסה. "
            "שליטה כאן ממשיכה ישירות ל-`concept:fluids_bernoulli` כשהנוזלים מתחילים לזוז.\n\n"
            "**נושאים עיקריים:**\n"
            "- הגדרת לחץ ותלות בעומק ($P = P_0 + \\rho g h$)\n"
            "- עיקרון פסקל ומכונות הידראוליות\n"
            "- עיקרון ארכימדס, ציפה ותנאי ציפה\n"
            "- מדידת צפיפות בשקילה באוויר לעומת בנוזל"
        ),
    },
    "definition": {
        "body_en_md": (
            "**Pressure** is force per unit area:\n"
            "$$P = \\frac{F}{A}$$\n"
            "Unit: pascal (Pa = N/m$^2$). One atmosphere $\\approx 10^5$ Pa.\n\n"
            "**Absolute pressure at depth $h$** in a fluid of density $\\rho$:\n"
            "$$P = P_0 + \\rho g h$$\n"
            "where $P_0$ is surface pressure (usually atmospheric). "
            "$\\rho g h$ alone is **gauge pressure** — the extra pressure above atmosphere.\n\n"
            "**Pascal's principle:** Pressure applied to an enclosed fluid transmits undiminished "
            "to every part of the fluid and container walls:\n"
            "$$P_1 = P_2 \\quad \\Rightarrow \\quad \\frac{F_1}{A_1} = \\frac{F_2}{A_2}$$\n\n"
            "**Archimedes' principle:** A submerged body experiences buoyant force equal to the "
            "weight of displaced fluid:\n"
            "$$F_b = \\rho_{\\text{fluid}} \\cdot V_{\\text{displaced}} \\cdot g$$\n\n"
            "**Floating condition:** A body floats when $\\rho_{\\text{body}} < \\rho_{\\text{fluid}}$; "
            "fraction submerged $= \\rho_{\\text{body}}/\\rho_{\\text{fluid}}$. "
            "Convert cm$^2$ to m$^2$ before substituting into force formulas.\n\n"
            "**Useful reference values:** $\\rho_{\\text{water}} = 1000$ kg/m$^3$; "
            "$\\rho_{\\text{seawater}} \\approx 1025$ kg/m$^3$; "
            "$g \\approx 10$ m/s$^2$ on Bagrut exams. "
            "One meter of water column adds roughly $10^4$ Pa of gauge pressure."
        ),
        "body_he_md": (
            "**לחץ** הוא כוח ליחידת שטח:\n"
            "$$P = \\frac{F}{A}$$\n"
            "יחידה: pascal (Pa = N/m$^2$). אטמוספירה אחת $\\approx 10^5$ Pa.\n\n"
            "**לחץ מוחלט בעומק $h$** בנוזל צפיפות $\\rho$:\n"
            "$$P = P_0 + \\rho g h$$\n"
            "כאשר $P_0$ הוא לחץ פני השטח (בדרך כלל אטמוספרי). "
            "$\\rho g h$ לבדו הוא **לחץ מד** — הלחץ הנוסף מעל האטמוספירה.\n\n"
            "**עיקרון פסקל:** לחץ המופעל על נוזל סגור מועבר ללא הקטנה לכל חלקי הנוזל ודפנות המיכל:\n"
            "$$P_1 = P_2 \\quad \\Rightarrow \\quad \\frac{F_1}{A_1} = \\frac{F_2}{A_2}$$\n\n"
            "**עיקרון ארכימדס:** גוף שקוע חווה כוח ציפה השווה למשקל הנוזל שהוצב:\n"
            "$$F_b = \\rho_{\\text{נוזל}} \\cdot V_{\\text{שקוע}} \\cdot g$$\n\n"
            "**תנאי ציפה:** גוף צף כש-$\\rho_{\\text{גוף}} < \\rho_{\\text{נוזל}}$; "
            "שבר שקוע $= \\rho_{\\text{גוף}}/\\rho_{\\text{נוזל}}$. "
            "המירו cm$^2$ ל-m$^2$ לפני הצבה בנוסחאות כוח.\n\n"
            "**ערכי ייחוס שימושיים:** $\\rho_{\\text{מים}} = 1000$ kg/m$^3$; "
            "$\\rho_{\\text{מי ים}} \\approx 1025$ kg/m$^3$; "
            "$g \\approx 10$ m/s$^2$ בבחינות בגרות. "
            "מטר מים אחד מוסיף בערך $10^4$ Pa של לחץ מד."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Pressure is isotropic\n"
            "At any point in a fluid at rest, pressure acts equally in all directions. "
            "This is Pascal's observation — you cannot \"push\" a fluid sideways without "
            "it pushing back uniformly.\n\n"
            "### Deriving $P = P_0 + \\rho g h$\n"
            "Consider a horizontal slice of fluid at depth $h$, area $A$, thickness $dh$. "
            "Weight of slice $= \\rho A\\,dh \\cdot g$. Vertical force balance on the slice:\n"
            "$$dP = \\rho g\\,dh \\quad \\Rightarrow \\quad P = P_0 + \\rho g h$$\n"
            "Pressure increases **linearly** with depth — double the depth, double the gauge pressure.\n\n"
            "### Floating, sinking, neutral buoyancy\n"
            "- Body **floats** if $\\rho_{\\text{body}} < \\rho_{\\text{fluid}}$; "
            "fraction submerged $= \\rho_{\\text{body}}/\\rho_{\\text{fluid}}$.\n"
            "- Body **sinks** if $\\rho_{\\text{body}} > \\rho_{\\text{fluid}}$.\n"
            "- **Neutral buoyancy** when densities match — the body hovers at any depth.\n\n"
            "### Hydraulic press and energy conservation\n"
            "Pascal multiplies force: small piston, large piston. But the large piston moves "
            "a shorter distance — work in equals work out:\n"
            "$$F_1 d_1 = F_2 d_2$$\n"
            "You trade distance for force, exactly like a lever.\n\n"
            "### Manometers and pressure measurement\n"
            "A U-tube manometer compares pressures via fluid height difference: "
            "$\\rho_1 g h_1 = \\rho_2 g h_2$ at equilibrium. "
            "This connects hydrostatics to laboratory and engineering instrumentation."
        ),
        "body_he_md": (
            "### לחץ הוא איזוטропי\n"
            "בכל נקודה בנוזל במנוחה, לחץ פועל שווה בכל הכיוונים. "
            "זו תצפית פסקל — אי אפשר \"לדחוף\" נוזל לצד בלי שהוא דוחף בחזרה באחידות.\n\n"
            "### גזירת $P = P_0 + \\rho g h$\n"
            "שקלו פרוסה אופקית של נוזל בעומק $h$, שטח $A$, עובי $dh$. "
            "משקל הפרוסה $= \\rho A\\,dh \\cdot g$. איזון כוחות אנכי על הפרוסה:\n"
            "$$dP = \\rho g\\,dh \\quad \\Rightarrow \\quad P = P_0 + \\rho g h$$\n"
            "הלחץ גדל **לינארית** עם העומק — כפל העומק, כפל לחץ המד.\n\n"
            "### ציפה, שקיעה, ציפה נייטרלית\n"
            "- גוף **צף** אם $\\rho_{\\text{גוף}} < \\rho_{\\text{נוזל}}$; "
            "שבר שקוע $= \\rho_{\\text{גוף}}/\\rho_{\\text{נוזל}}$.\n"
            "- גוף **שוקע** אם $\\rho_{\\text{גוף}} > \\rho_{\\text{נוזל}}$.\n"
            "- **ציפה נייטרלית** כשהצפיפויות שוות — הגוף רחף בכל עומק.\n\n"
            "### פרס הידראולי ושימור אנרגיה\n"
            "פסקל מכפיל כוח: בוכנה קטנה, בוכנה גדולה. אך הבוכנה הגדולה נעה מרחק קצר יותר — "
            "עבודה נכנסת שווה עבודה יוצאת:\n"
            "$$F_1 d_1 = F_2 d_2$$\n"
            "מחליפים מרחק בכוח, בדיוק כמו מנוף.\n\n"
            "### מנומטרים ומדידת לחץ\n"
            "מנומטר U משווה לחצים דרך הפרש גובה נוזל: "
            "$\\rho_1 g h_1 = \\rho_2 g h_2$ בשיווי משקל. "
            "זה מחבר סטטיקת נוזלים למכשירי מעבדה והנדסה."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A diver is at $h = 20\\;\\text{m}$ below the surface of seawater "
            "($\\rho = 1025\\;\\text{kg/m}^3$, $P_0 = 1.01\\times10^5\\;\\text{Pa}$, $g = 10$). "
            "Find total (absolute) pressure.\n\n"
            "### Move 1: Identify formula\n"
            "Absolute pressure: $P = P_0 + \\rho g h$.\n\n"
            "### Move 2: Substitute\n"
            "$$P = 1.01\\times10^5 + 1025(10)(20) = 1.01\\times10^5 + 2.05\\times10^5 "
            "= 3.06\\times10^5\\;\\text{Pa}$$\n\n"
            "### Move 3: Interpret\n"
            "Gauge pressure alone is $2.05\\times10^5$ Pa $\\approx 2$ atm extra. "
            "Total $\\approx 3$ atm — roughly triple surface pressure. "
            "Divers must equalize ears because $\\Delta P$ is enormous.\n\n"
            "### Move 4: Exam tip\n"
            "Always clarify whether the question asks for absolute or gauge pressure. "
            "Bagrut problems usually want absolute ($P_0 + \\rho g h$). "
            "If only gauge were asked, the answer would be $2.05\\times10^5$ Pa — "
            "roughly double surface pressure from 20 m of seawater alone. "
            "Note that seawater ($\\rho = 1025$) adds slightly more pressure than fresh water "
            "at the same depth — about 2.5% extra per meter. "
            "**Answer:** $P \\approx 3.06\\times10^5$ Pa $\\approx 3$ atm."
        ),
        "body_he_md": (
            "**נתון:** צולל בעומק $h = 20\\;\\text{m}$ מתחת לפני ים "
            "($\\rho = 1025\\;\\text{kg/m}^3$, $P_0 = 1.01\\times10^5\\;\\text{Pa}$, $g = 10$). "
            "מצאו לחץ מוחלט.\n\n"
            "### צעד 1: זיהוי נוסחה\n"
            "לחץ מוחלט: $P = P_0 + \\rho g h$.\n\n"
            "### צעד 2: הצבה\n"
            "$$P = 1.01\\times10^5 + 1025(10)(20) = 1.01\\times10^5 + 2.05\\times10^5 "
            "= 3.06\\times10^5\\;\\text{Pa}$$\n\n"
            "### צעד 3: פרשנות\n"
            "לחץ המד לבדו הוא $2.05\\times10^5$ Pa $\\approx 2$ atm נוספים. "
            "סה\"כ $\\approx 3$ atm — כפול-שלושה מלחץ פני השטח. "
            "צוללים חייבים לאזן אוזניים כי $\\Delta P$ עצום.\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "הבהירו תמיד אם השאלה מבקשת לחץ מוחלט או מד. "
            "בבגרות בדרך כלל רוצים מוחלט ($P_0 + \\rho g h$). "
            "אם היו מבקשים מד בלבד, התשובה הייתה $2.05\\times10^5$ Pa — "
            "בערך כפול לחץ פני השטח מ-20 m מי ים. "
            "שימו לב שמי ים ($\\rho = 1025$) מוסיפים מעט יותר לחץ ממים מתוקים "
            "באותו עומק — בערך 2.5% נוספים לכל מטר. "
            "**תשובה:** $P \\approx 3.06\\times10^5$ Pa $\\approx 3$ atm."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A wooden block ($\\rho_w = 600\\;\\text{kg/m}^3$, $V = 0.5\\;\\text{m}^3$) "
            "floats in water ($\\rho_f = 1000\\;\\text{kg/m}^3$). Find: (a) fraction submerged, "
            "(b) buoyant force.\n\n"
            "### Move 1: Fraction submerged\n"
            "At equilibrium, weight of displaced water equals block weight:\n"
            "$$f = \\frac{\\rho_w}{\\rho_f} = \\frac{600}{1000} = 0.6 \\quad (60\\% \\text{ submerged})$$\n"
            "So 40% sticks above the surface.\n\n"
            "### Move 2: Buoyant force\n"
            "For a floating object, $F_b = mg$ exactly:\n"
            "$$F_b = \\rho_w V g = 600(0.5)(10) = 3000\\;\\text{N}$$\n\n"
            "### Move 3: Cross-check with Archimedes\n"
            "Submerged volume $V_{\\text{sub}} = 0.6 \\times 0.5 = 0.3\\;\\text{m}^3$:\n"
            "$$F_b = \\rho_f V_{\\text{sub}} g = 1000(0.3)(10) = 3000\\;\\text{N}$$ ✓\n\n"
            "### Move 4: Exam tip\n"
            "Two routes always agree for floating bodies: $F_b = mg$ or $F_b = \\rho_f V_{\\text{sub}} g$. "
            "Use whichever is faster. The block displaces exactly 0.3 m$^3$ of water — "
            "60% of its total volume — to support its full weight. "
            "If the block were pushed deeper, buoyancy would not change until more volume "
            "submerges; for a floating body, only the submerged portion matters. "
            "Always state whether the question asks for submerged or above-water fraction. "
            "**Answer:** 60% submerged; $F_b = 3000$ N."
        ),
        "body_he_md": (
            "**נתון:** גוש עץ ($\\rho_w = 600\\;\\text{kg/m}^3$, $V = 0.5\\;\\text{m}^3$) "
            "צף במים ($\\rho_f = 1000\\;\\text{kg/m}^3$). מצאו: (א) שבר שקוע, (ב) כוח ציפה.\n\n"
            "### צעד 1: שבר שקוע\n"
            "בשיווי משקל, משקל המים שהוצב שווה למשקל הגוש:\n"
            "$$f = \\frac{\\rho_w}{\\rho_f} = \\frac{600}{1000} = 0.6 \\quad (60\\% \\text{ שקוע})$$\n"
            "כלומר 40% מעל פני המים.\n\n"
            "### צעד 2: כוח ציפה\n"
            "לגוף צף, $F_b = mg$ בדיוק:\n"
            "$$F_b = \\rho_w V g = 600(0.5)(10) = 3000\\;\\text{N}$$\n\n"
            "### צעד 3: בדיקה עם ארכימדס\n"
            "נפח שקוע $V_{\\text{שקוע}} = 0.6 \\times 0.5 = 0.3\\;\\text{m}^3$:\n"
            "$$F_b = \\rho_f V_{\\text{שקוע}} g = 1000(0.3)(10) = 3000\\;\\text{N}$$ ✓\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "שני מסלולים תמיד מסכימים לגוף צף: $F_b = mg$ או $F_b = \\rho_f V_{\\text{שקוע}} g$. "
            "השתמשו במהיר יותר. הגוש מוצב בדיוק 0.3 m$^3$ מים — "
            "60% מנפחו הכולל — כדי לתמוך במשקלו המלא. "
            "40% הנראים מעל המים הם המשלים: $1 - 0.6 = 0.4$. "
            "ציינו תמיד אם השאלה מבקשת שבר שקוע או מעל. "
            "**תשובה:** 60% שקוע; $F_b = 3000$ N."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** A block ($m = 2\\;\\text{kg}$, $V = 2.5\\times10^{-3}\\;\\text{m}^3$) is placed "
            "in a container with water ($\\rho_1 = 1000$) on the bottom and oil ($\\rho_2 = 800\\;\\text{kg/m}^3$) "
            "on top. Find where it settles.\n\n"
            "### Move 1: Block density\n"
            "$$\\rho_{\\text{block}} = \\frac{m}{V} = \\frac{2}{2.5\\times10^{-3}} = 800\\;\\text{kg/m}^3$$\n"
            "This exactly matches oil density.\n\n"
            "### Move 2: Compare with each fluid\n"
            "Block denser than oil? No — equal. Denser than water? No — lighter. "
            "The block cannot sink in water; it floats at the oil–water interface.\n\n"
            "### Move 3: Neutral buoyancy in oil\n"
            "In oil alone: $F_b = \\rho_2 V g = 800(2.5\\times10^{-3})(10) = 20\\;\\text{N} = mg$ ✓. "
            "The block is **neutrally buoyant** in oil — it hovers wherever placed in the oil layer.\n\n"
            "### Move 4: Exam tip\n"
            "Two-fluid problems: compute $\\rho_{\\text{block}}$ first, then compare to each layer. "
            "Equal density means neutral buoyancy — a classic Bagrut trap. "
            "It sits entirely in the oil layer, not sinking into water below. "
            "**Answer:** $\\rho_{\\text{block}} = 800$ kg/m$^3$; neutrally buoyant in oil at the interface."
        ),
        "body_he_md": (
            "**נתון:** גוש ($m = 2\\;\\text{kg}$, $V = 2.5\\times10^{-3}\\;\\text{m}^3$) "
            "במיכל עם מים ($\\rho_1 = 1000$) למטה ושמן ($\\rho_2 = 800\\;\\text{kg/m}^3$) למעלה. "
            "מצאו היכן הוא מתייצב.\n\n"
            "### צעד 1: צפיפות הגוש\n"
            "$$\\rho_{\\text{גוף}} = \\frac{m}{V} = \\frac{2}{2.5\\times10^{-3}} = 800\\;\\text{kg/m}^3$$\n"
            "זהה בדיוק לצפיפות השמן.\n\n"
            "### צעד 2: השוואה לכל נוזל\n"
            "הגוש כבד משמן? לא — שווה. כבד ממים? לא — קל יותר. "
            "הגוש לא יכול לשקוע במים; הוא צף בגבול שמן–מים.\n\n"
            "### צעד 3: ציפה נייטרלית בשמן\n"
            "בשמן בלבד: $F_b = \\rho_2 V g = 800(2.5\\times10^{-3})(10) = 20\\;\\text{N} = mg$ ✓. "
            "הגוש **צף נייטרלית** בשמן — רחף בכל מקום בשכבת השמן.\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "בעיות שני נוזלים: חשבו $\\rho_{\\text{גוף}}$ קודם, והשוו לכל שכבה. "
            "צפיפות שווה = ציפה נייטרלית — מלכודת בגרות קלאסית. "
            "הוא שוהה לחלוטין בשכבת השמן, לא שוקע למים למטה. "
            "**תשובה:** $\\rho_{\\text{גוף}} = 800$ kg/m$^3$; ציפה נייטרלית בשמן בממשק."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Problem Type | Method |\n"
            "|---|---|\n"
            "| Pressure at depth | $P = P_0 + \\rho g h$ (absolute) |\n"
            "| Hydraulic device | $F_1/A_1 = F_2/A_2$ (Pascal); check $F_1 d_1 = F_2 d_2$ for work |\n"
            "| Object floats — fraction submerged | $f = \\rho_{\\text{object}}/\\rho_{\\text{fluid}}$ |\n"
            "| Object floats — buoyant force | $F_b = mg$ (equilibrium) |\n"
            "| Density from weighing in/out of water | $\\rho = W_{\\text{air}}\\rho_f/(W_{\\text{air}} - W_{\\text{water}})$ |\n"
            "| Two-fluid interface | Compute $\\rho_{\\text{body}}$, compare to each layer |\n"
            "| Force on submerged wall | $F = P_{\\text{avg}} \\cdot A$ where $P_{\\text{avg}} = \\rho g H/2$ |\n\n"
            "**When to use:** Read the problem type first — match a row, then substitute numbers. "
            "Convert cm$^2$ to m$^2$ and clarify absolute vs. gauge pressure before calculating."
        ),
        "body_he_md": (
            "| סוג בעיה | שיטה |\n"
            "|---|---|\n"
            "| לחץ בעומק | $P = P_0 + \\rho g h$ (מוחלט) |\n"
            "| מכשיר הידראולי | $F_1/A_1 = F_2/A_2$ (פסקל); בדקו $F_1 d_1 = F_2 d_2$ לעבודה |\n"
            "| גוף צף — שבר שקוע | $f = \\rho_{\\text{גוף}}/\\rho_{\\text{נוזל}}$ |\n"
            "| גוף צף — כוח ציפה | $F_b = mg$ (שיווי משקל) |\n"
            "| צפיפות משקילה באוויר/מים | $\\rho = W_{\\text{אוויר}}\\rho_f/(W_{\\text{אוויר}} - W_{\\text{מים}})$ |\n"
            "| ממשק שני נוזלים | חשבו $\\rho_{\\text{גוף}}$, השוו לכל שכבה |\n"
            "| כוח על קיר שקוע | $F = P_{\\text{ממ}} \\cdot A$ כאשר $P_{\\text{ממ}} = \\rho g H/2$ |\n\n"
            "**מתי להשתמש:** קראו קודם את סוג הבעיה — התאימו שורה, ואז הציבו מספרים. "
            "המירו cm$^2$ ל-m$^2$ והבהירו לחץ מוחלט לעומת מד לפני החישוב."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **$\\rho g h$ is gauge pressure, not absolute.** Add $P_0 \\approx 10^5$ Pa for total pressure. "
            "Bagrut stems often say \"total pressure\" — read carefully.\n\n"
            "2. **Buoyancy uses displaced (submerged) volume, not total volume.** "
            "A half-submerged block uses $V/2$, not $V$, in Archimedes' formula.\n\n"
            "3. **Floating means $F_b = mg$ exactly — not \"less buoyancy.\"** "
            "A floating ship has enormous buoyant force equal to its full weight.\n\n"
            "4. **Pascal's principle conserves energy.** A hydraulic press multiplies force "
            "but the output piston moves a shorter distance: $F_1 d_1 = F_2 d_2$.\n\n"
            "**Example misconception:** \"A lighter object has more buoyancy.\"\n\n"
            "**Fix:** Buoyancy depends on displaced fluid volume, not object weight. "
            "A large light balloon displaces more air than a small heavy coin."
        ),
        "body_he_md": (
            "1. **$\\rho g h$ הוא לחץ מד, לא מוחלט.** הוסיפו $P_0 \\approx 10^5$ Pa ללחץ כולל. "
            "ניסוחי בגרות לעיתים אומרים \"לחץ כולל\" — קראו בעיון.\n\n"
            "2. **ציפה משתמשת בנפח מוצב (שקוע), לא נפח כולל.** "
            "גוש שחציו שקוע משתמש ב-$V/2$, לא $V$, בנוסחת ארכימדס.\n\n"
            "3. **ציפה פירושה $F_b = mg$ בדיוק — לא \"פחות ציפה.\"** "
            "ספינה צפה חווה כוח ציפה עצום השווה למשקלה המלא.\n\n"
            "4. **עיקרון פסקל שומר אנרגיה.** פרס הידראולי מכפיל כוח "
            "אך הבוכנה היוצאת נעה מרחק קצר יותר: $F_1 d_1 = F_2 d_2$.\n\n"
            "**אמונה שגויה לדוגמה:** \"גוף קל יותר = ציפה גדולה יותר.\"\n\n"
            "**תיקון:** ציפה תלויה בנפח הנוזל שהוצב, לא במשקל הגוף. "
            "בלון גדול וקל מוצב יותר אוויר ממטבע קטן וכבד."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Fluid statics connects directly to **`concept:fluids_bernoulli`** — when fluids move, "
            "static pressure becomes one term in Bernoulli's energy equation. "
            "It also underpins **`concept:work_energy`** (hydraulic work) and "
            "**`concept:uni_thermodynamics`** (pressure–volume work in gases).\n\n"
            "Real applications span scuba diving safety, ship design, hydraulic brakes, "
            "IV drip pressure, and barometric altitude measurement.\n\n"
            "**Why it matters for exams:** Bagrut physics rewards recognizing whether a problem "
            "is static (this lesson) or dynamic (Bernoulli). Always ask: \"Is the fluid moving?\" "
            "Hydrostatics also appears in chemistry (barometers) and biology (blood pressure). "
            "Pressure–depth problems are quick exam points when you know $P = P_0 + \\rho g h$."
        ),
        "body_he_md": (
            "סטטיקת נוזלים מתחברת ישירות ל-**`concept:fluids_bernoulli`** — כשנוזלים נעים, "
            "לחץ סטטי הופך לאיבר אחד במשוואת האנרגיה של ברנולי. "
            "היא גם תומכת ב-**`concept:work_energy`** (עבודה הידראולית) "
            "וב-**`concept:uni_thermodynamics`** (עבודת לחץ–נפח בגazים).\n\n"
            "יישומים אמיתיים: בטיחות צלילה, תכנון ספינות, בלמים הידראוליים, "
            "לחץ טיפות IV, ומדידת גובה ברומטרית.\n\n"
            "**למה זה חשוב לבחינות:** בגרות בפיזיקה מתגמלת זיהוי האם הבעיה "
            "סטטית (שיעור זה) או דינמית (ברנולי). שאלו תמיד: \"האם הנוזל נע?\" "
            "סטטיקת נוזלים מופיעה גם בכימיה (ברומטרים) ובביולוגיה (לחץ דם)."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "- $P = F/A$ [Pa]; $P_{\\text{abs}} = P_0 + \\rho g h$; gauge $= \\rho g h$\n"
            "- Pascal: $F_1/A_1 = F_2/A_2$; energy: $F_1 d_1 = F_2 d_2$\n"
            "- Archimedes: $F_b = \\rho_{\\text{fluid}} V_{\\text{sub}} g$\n"
            "- Float: $\\rho_{\\text{body}} < \\rho_{\\text{fluid}}$; fraction sub $= \\rho_b/\\rho_f$\n"
            "- Density from weighing: $\\rho_b = \\rho_f W_{\\text{air}}/(W_{\\text{air}} - W_{\\text{fluid}})$\n"
            "- $\\rho_{\\text{water}} = 1000$ kg/m$^3$; $P_{\\text{atm}} \\approx 10^5$ Pa\n"
            "- Manometer: $\\rho_1 h_1 = \\rho_2 h_2$ at balance\n"
            "- Suspended object: $T = W - F_b$ (tension supports remainder)\n"
            "- Iceberg: fraction above $= 1 - \\rho_{\\text{ice}}/\\rho_{\\text{sea}}$\n"
            "- Force on wall: $F = \\frac{1}{2}\\rho g H \\cdot A$ (average pressure)\n\n"
            "**Last review:** Say each formula aloud once, then solve one checkpoint without looking. "
            "Draw free-body diagrams for every buoyancy problem. "
            "Check absolute vs. gauge pressure before every calculation. "
            "Convert cm$^2$ to m$^2$ in hydraulic problems. "
            "Label submerged vs. above fractions carefully on floating-body questions."
        ),
        "body_he_md": (
            "- $P = F/A$ [Pa]; $P_{\\text{מוחלט}} = P_0 + \\rho g h$; מד $= \\rho g h$\n"
            "- פסקל: $F_1/A_1 = F_2/A_2$; אנרגיה: $F_1 d_1 = F_2 d_2$\n"
            "- ארכימדס: $F_b = \\rho_f V_{\\text{שקוע}} g$\n"
            "- ציפה: $\\rho_{\\text{גוף}} < \\rho_{\\text{נוזל}}$; שבר שקוע $= \\rho_b/\\rho_f$\n"
            "- צפיפות משקילה: $\\rho_b = \\rho_f W_{\\text{אוויר}}/(W_{\\text{אוויר}} - W_{\\text{נוזל}})$\n"
            "- $\\rho_{\\text{מים}} = 1000$ kg/m$^3$; $P_{\\text{atm}} \\approx 10^5$ Pa\n"
            "- מנומטר: $\\rho_1 h_1 = \\rho_2 h_2$ באיזון\n"
            "- גוף תלוי: $T = W - F_b$ (מתח תומך בשארית)\n"
            "- קרחון: שבר מעל $= 1 - \\rho_{\\text{קרח}}/\\rho_{\\text{ים}}$\n"
            "- כוח על קיר: $F = \\frac{1}{2}\\rho g H \\cdot A$ (לחץ ממוצע)\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint אחד בלי להסתכל. "
            "שרטטו דיאגרמות כוח לכל בעיית ציפה. "
            "בדקו לחץ מוחלט לעומת מד לפני כל חישוב."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Pressure:** $P = F/A$; increases linearly with depth: $P = P_0 + \\rho g h$\n"
            "- **Pascal:** pressure transmitted equally; $F_1/A_1 = F_2/A_2$; work conserved\n"
            "- **Archimedes:** $F_b = \\rho_f V_{\\text{sub}} g$; floating body has $F_b = mg$\n"
            "- **Floating fraction:** submerged $= \\rho_{\\text{body}}/\\rho_{\\text{fluid}}$\n"
            "- **Density trick:** weigh in air and in water to find $\\rho_b$\n\n"
            "**Takeaway:** Identify the problem type first — pressure, hydraulics, or buoyancy — "
            "then pick the matching formula. Static fluids are the foundation for Bernoulli. "
            "When in doubt, draw a free-body diagram and label all forces."
        ),
        "body_he_md": (
            "- **לחץ:** $P = F/A$; גדל לינארית עם עומק: $P = P_0 + \\rho g h$\n"
            "- **פסקל:** לחץ מועבר שווה; $F_1/A_1 = F_2/A_2$; עבודה נשמרת\n"
            "- **ארכימדס:** $F_b = \\rho_f V_{\\text{שקוע}} g$; גוף צף: $F_b = mg$\n"
            "- **שבר שקוע:** $= \\rho_{\\text{גוף}}/\\rho_{\\text{נוזל}}$\n"
            "- **טריק צפיפות:** שקילה באוויר ובמים למציאת $\\rho_b$\n\n"
            "**מסקנה:** זהו קודם סוג בעיה — לחץ, הידראוליקה או ציפה — "
            "ואז בחרו נוסחה מתאימה. נוזלים סטטיים הם הבסיס לברנולי. "
            "בספק, שרטטו דיאגרמת כוחות וסמנו את כל הכוחות."
        ),
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "### Move 1: Apply Pascal's principle\n"
            "Pressure is equal on both pistons: $F_1/A_1 = F_2/A_2$.\n\n"
            "### Move 2: Solve for $F_2$\n"
            "$$F_2 = F_1 \\frac{A_2}{A_1} = 200 \\times \\frac{400}{10} = 200 \\times 40 = 8000\\;\\text{N}$$\n\n"
            "**Check:** Area ratio is 40, so force multiplies by 40 ✓. "
            "The small piston moves 40× farther — energy is conserved. "
            "**Answer:** $F_2 = 8000$ N."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: הפעלת עיקרון פסקל\n"
            "לחץ שווה בשתי הבוכנות: $F_1/A_1 = F_2/A_2$.\n\n"
            "### צעד 2: פתרון עבור $F_2$\n"
            "$$F_2 = F_1 \\frac{A_2}{A_1} = 200 \\times \\frac{400}{10} = 200 \\times 40 = 8000\\;\\text{N}$$\n\n"
            "**בדיקה:** יחס שטחים 40, ולכן הכוח מוכפל ב-40 ✓. "
            "הבוכנה הקטנה נעה פי 40 יותר — אנרגיה נשמרת. "
            "**תשובה:** $F_2 = 8000$ N."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "### Move 1: Buoyant force from weight difference\n"
            "$$F_b = W_{\\text{air}} - W_{\\text{water}} = 50 - 35 = 15\\;\\text{N}$$\n\n"
            "### Move 2: Find volume from Archimedes\n"
            "$$V = \\frac{F_b}{\\rho_f g} = \\frac{15}{1000 \\times 10} = 1.5\\times10^{-3}\\;\\text{m}^3$$\n\n"
            "### Move 3: Density\n"
            "Mass $m = W/g = 50/10 = 5$ kg. "
            "$$\\rho = \\frac{m}{V} = \\frac{5}{1.5\\times10^{-3}} \\approx 3333\\;\\text{kg/m}^3$$\n\n"
            "**Check:** Metal density $\\approx 3000$–$8000$ kg/m$^3$ ✓. "
            "**Answer:** $\\rho \\approx 3333$ kg/m$^3$."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: כוח ציפה מהפרש משקלים\n"
            "$$F_b = W_{\\text{אוויר}} - W_{\\text{מים}} = 50 - 35 = 15\\;\\text{N}$$\n\n"
            "### צעד 2: נפח מארכימדס\n"
            "$$V = \\frac{F_b}{\\rho_f g} = \\frac{15}{1000 \\times 10} = 1.5\\times10^{-3}\\;\\text{m}^3$$\n\n"
            "### צעד 3: צפיפות\n"
            "מסה $m = W/g = 50/10 = 5$ kg. "
            "$$\\rho = \\frac{m}{V} = \\frac{5}{1.5\\times10^{-3}} \\approx 3333\\;\\text{kg/m}^3$$\n\n"
            "**בדיקה:** צפיפות מתכת $\\approx 3000$–$8000$ kg/m$^3$ ✓. "
            "**תשובה:** $\\rho \\approx 3333$ kg/m$^3$."
        ),
    },
}

EXPLANATIONS = {
    1: {
        "en": (
            "For a floating object, the fraction **submerged** equals the density ratio "
            "$\\rho_{\\text{block}}/\\rho_{\\text{water}} = 600/1000 = 0.6$ (60%). "
            "The question asks for the fraction **above** the surface: $1 - 0.6 = 0.4$ (40%). "
            "Option \"60%\" is the submerged fraction — the most common exam slip. "
            "\"50%\" would mean equal densities; \"600%\" is nonsensical. "
            "Always read whether the stem asks \"above\" or \"below\" the waterline. "
            "Sanity check: a less dense block ($600 < 1000$) must float with most of its volume "
            "under water, so less than half sticks out. "
            "The density ratio method avoids calculating actual volumes — "
            "only the ratio matters for floating bodies at equilibrium. "
            "**Exam tip:** compute submerged first, then subtract from 1. **Answer:** 40%."
        ),
        "he": (
            "לגוף צף, השבר **השקוע** שווה ליחס הצפיפויות "
            "$\\rho_{\\text{גוף}}/\\rho_{\\text{מים}} = 600/1000 = 0.6$ (60%). "
            "השאלה מבקשת את השבר **מעל** פני המים: $1 - 0.6 = 0.4$ (40%). "
            "האפשרות \"60%\" היא השבר השקוע — הטעות הנפוצה ביותר בבחינה. "
            "\"50%\" היה אומר צפיפויות שוות; \"600%\" לא הגיוני. "
            "קראו תמיד אם הניסוח מבקש \"מעל\" או \"מתחת\" לקו המים. "
            "בדיקת הגיון: גוש פחות צפוף ($600 < 1000$) חייב לצוף עם רוב נפחו מתחת למים, "
            "ולכן פחות מחצי בולט. "
            "שיטת יחס הצפיפויות חוסכת חישוב נפחים — "
            "רק היחס חשוב לגופים צפים בשיווי משקל. "
            "**טיפ לבחינה:** חשבו שקוע קודם, ואז חסרו מ-1. **תשובה:** 40%."
        ),
    },
    2: {
        "en": (
            "Absolute pressure at depth uses $P = P_0 + \\rho g h$. "
            "With $P_0 = 10^5$ Pa, $\\rho = 1000$ kg/m$^3$, $g = 10$ m/s$^2$, $h = 15$ m:\n"
            "$P = 10^5 + 1000(10)(15) = 10^5 + 1.5\\times10^5 = 2.5\\times10^5$ Pa. "
            "Common errors: forgetting $P_0$ (gives $1.5\\times10^5$ Pa — gauge only), "
            "using $h$ in cm without converting, or reporting kPa without converting back. "
            "Gauge pressure alone is $1.5\\times10^5$ Pa; absolute adds one atmosphere. "
            "Sanity check: 15 m of water adds roughly 1.5 atm to surface pressure. "
            "Each 10 m of water contributes about $10^5$ Pa of gauge pressure — "
            "a useful rule of thumb for quick estimates on timed exams. "
            "**Exam tip:** label \"absolute\" vs. \"gauge\" before substituting. "
            "**Answer:** $2.5\\times10^5$ Pa."
        ),
        "he": (
            "לחץ מוחלט בעומק משתמש ב-$P = P_0 + \\rho g h$. "
            "עם $P_0 = 10^5$ Pa, $\\rho = 1000$ kg/m$^3$, $g = 10$ m/s$^2$, $h = 15$ m:\n"
            "$P = 10^5 + 1000(10)(15) = 10^5 + 1.5\\times10^5 = 2.5\\times10^5$ Pa. "
            "טעויות נפוצות: שכחת $P_0$ (נותן $1.5\\times10^5$ Pa — מד בלבד), "
            "שימוש ב-$h$ ב-cm בלי המרה, או דיווח ב-kPa בלי המרה חזרה. "
            "לחץ מד לבד הוא $1.5\\times10^5$ Pa; מוחלט מוסיף אטמוספירה. "
            "בעומק 15 m, לחץ המד מוסיף בערך 1.5 atm ללחץ פני השטח. "
            "כל 10 m מים תורמים בערך $10^5$ Pa של לחץ מד — "
            "כלל אצבע שימושי להערכות מהירות בבחינות. "
            "**טיפ לבחינה:** סמנו \"מוחלט\" לעומת \"מד\" לפני הצבה. "
            "**תשובה:** $2.5\\times10^5$ Pa."
        ),
    },
    3: {
        "en": (
            "Pressure at depth: $P = P_0 + \\rho g h$. "
            "Substituting $P_0 = 10^5$ Pa, $\\rho = 1000$ kg/m$^3$, $g = 10$, $h = 10$ m:\n"
            "$P = 10^5 + 1000(10)(10) = 10^5 + 10^6 = 2\\times10^5$ Pa. "
            "Wait — $1000 \\times 10 \\times 10 = 10^5$, not $10^6$. "
            "So $P = 10^5 + 10^5 = 2\\times10^5$ Pa. "
            "Students who get $10^6$ Pa added an extra zero. "
            "Another slip: using gauge only ($10^5$ Pa) when absolute is required. "
            "At 10 m depth, gauge pressure equals one atmosphere — a useful benchmark. "
            "Remember: $\\rho g h = 1000 \\times 10 \\times 10 = 10^5$ Pa per 10 m column. "
            "This pattern repeats for any depth — just scale linearly with $h$. "
            "**Exam tip:** write $\\rho g h$ separately before adding $P_0$. "
            "**Answer:** $2\\times10^5$ Pa."
        ),
        "he": (
            "לחץ בעומק: $P = P_0 + \\rho g h$. "
            "הצבה: $P_0 = 10^5$ Pa, $\\rho = 1000$ kg/m$^3$, $g = 10$, $h = 10$ m:\n"
            "$P = 10^5 + 1000(10)(10) = 10^5 + 10^5 = 2\\times10^5$ Pa. "
            "תלמידים שמקבלים $10^6$ Pa הוסיפו אפס מיותר. "
            "טעות נוספת: שימוש במד בלבד ($10^5$ Pa) כשצריך מוחלט. "
            "בעומק 10 m, לחץ המד שווה לאטמוספירה אחת — נקודת ייחוס שימושית. "
            "זכרו: $\\rho g h = 1000 \\times 10 \\times 10 = 10^5$ Pa לכל 10 m. "
            "הדפוס חוזר לכל עומק — קנה מידה לינארי עם $h$. "
            "בעומק 10 m, לחץ המד שווה בדיוק לאטמוספירה אחת — "
            "נקודת ייחוס שימושית להשוואות מהירות. "
            "**טיפ לבחינה:** כתבו $\\rho g h$ בנפרד לפני הוספת $P_0$. "
            "**תשובה:** $2\\times10^5$ Pa."
        ),
    },
    4: {
        "en": (
            "Pascal's principle: equal pressure on both pistons means $F_1/A_1 = F_2/A_2$. "
            "Area ratio $A_2/A_1 = 50/5 = 10$, so $F_2 = F_1 \\times 10 = 200 \\times 10 = 2000$ N. "
            "Units work because both areas are in cm$^2$ — the ratio is dimensionless. "
            "Common errors: inverting the ratio ($F_2 = 200/10 = 20$ N), "
            "or converting areas incorrectly. "
            "Sanity check: the larger piston should produce a larger force — 2000 N > 200 N ✓. "
            "The small piston must move 10× farther to conserve energy. "
            "This is a force multiplier of 10 — typical for car hydraulic jacks. "
            "If both areas were in m$^2$, the ratio would be identical. "
            "**Exam tip:** write the area ratio first, then multiply the input force. "
            "**Answer:** 2000 N."
        ),
        "he": (
            "עיקרון פסקל: לחץ שווה בשתי הבוכנות פירושו $F_1/A_1 = F_2/A_2$. "
            "יחס שטחים $A_2/A_1 = 50/5 = 10$, ולכן $F_2 = F_1 \\times 10 = 200 \\times 10 = 2000$ N. "
            "יחידות תקינות כי שני השטחים ב-cm$^2$ — היחס חסר ממד. "
            "טעויות נפוצות: היפוך היחס ($F_2 = 200/10 = 20$ N), "
            "או המרת שטחים שגויה. "
            "בדיקת הגיון: הבוכנה הגדולה צריכה לייצר כוח גדול יותר — 2000 N > 200 N ✓. "
            "הבוכנה הקטנה חייבת לנוע פי 10 יותר לשימור אנרגיה. "
            "זה מכפיל כוח של 10 — אופייני למגבהי רכב הידראוליים. "
            "אם שני השטחים היו ב-m$^2$, היחס היה זהה. "
            "**טיפ לבחינה:** כתבו קודם יחס שטחים, ואז הכפילו את כוח הקלט. "
            "**תשובה:** 2000 N."
        ),
    },
    5: {
        "en": (
            "For a floating object, fraction submerged equals density ratio: "
            "$f = \\rho_{\\text{block}}/\\rho_{\\text{water}} = 500/1000 = 0.5$ (50%). "
            "This comes from equilibrium: $\\rho_b V g = \\rho_f f V g$, so $f = \\rho_b/\\rho_f$. "
            "The block is half underwater and half above — equal densities would mean fully submerged "
            "at the surface, but $500 < 1000$ so it floats. "
            "Common slip: reporting fraction above (also 50% here, but not always!). "
            "Another error: using mass ratio instead of density ratio. "
            "Wood at 500 kg/m$^3$ is exactly half as dense as water — "
            "so exactly half its volume must submerge to displace enough water. "
            "**Exam tip:** if $\\rho_b = \\rho_f/2$, exactly half the volume submerges. "
            "**Answer:** 50% submerged (0.5)."
        ),
        "he": (
            "לגוף צף, שבר שקוע שווה ליחס צפיפויות: "
            "$f = \\rho_{\\text{גוף}}/\\rho_{\\text{מים}} = 500/1000 = 0.5$ (50%). "
            "זה נובע משיווי משקל: $\\rho_b V g = \\rho_f f V g$, ולכן $f = \\rho_b/\\rho_f$. "
            "הגוש חציו מתחת למים וחציו מעל — צפיפויות שוות היו אומרות שקיעה מלאה "
            "בפני השטח, אך $500 < 1000$ ולכן הוא צף. "
            "טעות נפוצה: דיווח שבר מעל (גם 50% כאן, אך לא תמיד!). "
            "טעות נוספת: שימוש ביחס מסות במקום צפיפויות. "
            "עץ ב-500 kg/m$^3$ הוא בדיוק חצי צפוף ממים — "
            "ולכן בדיוק חצי נפחו חייב לשקוע כדי להוציב מספיק מים. "
            "**טיפ לבחינה:** אם $\\rho_b = \\rho_f/2$, בדיוק חצי הנפח שקוע. "
            "**תשובה:** 50% שקוע (0.5)."
        ),
    },
    6: {
        "en": (
            "Fully submerged object: Archimedes gives $F_b = \\rho_f V g = 1000(1)(10) = 10000$ N. "
            "Object weight $W = \\rho V g = 700(1)(10) = 7000$ N. "
            "Net force $= F_b - W = 10000 - 7000 = 3000$ N upward — the object rises. "
            "Since $\\rho = 700 < 1000$, the object is less dense than water and will float "
            "once it reaches the surface. "
            "Common errors: using total volume when partially submerged (not applicable here), "
            "or subtracting in the wrong order (net upward means $F_b > W$). "
            "The 3000 N net upward force accelerates the block until it reaches "
            "the surface and establishes a new floating equilibrium. "
            "**Exam tip:** compare densities first — lighter object always rises in denser fluid. "
            "**Answer:** $F_b = 10000$ N; net $= 3000$ N upward."
        ),
        "he": (
            "גוף שקוע לחלוטין: ארכימדס נותן $F_b = \\rho_f V g = 1000(1)(10) = 10000$ N. "
            "משקל הגוף $W = \\rho V g = 700(1)(10) = 7000$ N. "
            "כוח נטו $= F_b - W = 10000 - 7000 = 3000$ N כלפי מעלה — הגוף עולה. "
            "מכיוון ש-$\\rho = 700 < 1000$, הגוף פחות צפוף ממים ויצוף "
            "ברגע שיגיע לפני השטח. "
            "טעויות נפוצות: שימוש בנפח כולל כשחלקית שקוע (לא רלוונטי כאן), "
            "או חיסור בסדר שגוי (נטו כלפי מעלה = $F_b > W$). "
            "כוח הנטו 3000 N כלפי מעלה מאיץ את הגוש עד שיגיע "
            "לפני השטח ויציב שיווי משקל צף חדש. "
            "**טיפ לבחינה:** השוו צפיפויות קודם — גוף קל תמיד עולה בנוזל כבד יותר. "
            "**תשובה:** $F_b = 10000$ N; נטו $= 3000$ N כלפי מעלה."
        ),
    },
    7: {
        "en": (
            "Suspended cube in water: three forces — weight down, buoyancy up, tension up. "
            "Volume $V = s^3 = (0.1)^3 = 0.001$ m$^3$. "
            "Weight $W = \\rho V g = 8000(0.001)(10) = 80$ N. "
            "Buoyancy $F_b = \\rho_f V g = 1000(0.001)(10) = 10$ N. "
            "Equilibrium: $T + F_b = W$, so $T = W - F_b = 80 - 10 = 70$ N. "
            "Common errors: forgetting buoyancy (getting $T = 80$ N), "
            "or using $V = s^2$ instead of $s^3$. "
            "The string supports most of the weight because metal is much denser than water. "
            "Density ratio $8000/1000 = 8$ means buoyancy covers only 1/8 of the weight. "
            "This suspended-object setup is common in lab density measurements. "
            "**Exam tip:** draw a free-body diagram with all three forces before solving. "
            "**Answer:** $T = 70$ N."
        ),
        "he": (
            "קובייה תלויה במים: שלושה כוחות — משקל למטה, ציפה למעלה, מתח למעלה. "
            "נפח $V = s^3 = (0.1)^3 = 0.001$ m$^3$. "
            "משקל $W = \\rho V g = 8000(0.001)(10) = 80$ N. "
            "ציפה $F_b = \\rho_f V g = 1000(0.001)(10) = 10$ N. "
            "שיווי משקל: $T + F_b = W$, ולכן $T = W - F_b = 80 - 10 = 70$ N. "
            "טעויות נפוצות: שכחת ציפה (מקבלים $T = 80$ N), "
            "או שימוש ב-$V = s^2$ במקום $s^3$. "
            "החוט תומך ברוב המשקל כי מתכת הרבה יותר צפופה ממים. "
            "יחס צפיפויות $8000/1000 = 8$ פירושו שציפה מכסה רק 1/8 מהמשקל. "
            "תצורת גוף תלוי נפוצה במדידות צפיפות במעבדה. "
            "**טיפ לבחינה:** שרטטו דיאגרמת כוחות עם שלושת הכוחות לפני הפתרון. "
            "**תשובה:** $T = 70$ N."
        ),
    },
    8: {
        "en": (
            "Iceberg floating: fraction submerged $= \\rho_{\\text{ice}}/\\rho_{\\text{sea}} "
            "= 917/1025 = 0.895$ (89.5% underwater). "
            "Fraction **above** water $= 1 - 0.895 = 0.105 \\approx 10.5$%. "
            "Seawater is denser than fresh water (1025 vs. 1000), so ice sits higher in the ocean. "
            "The famous \"tip of the iceberg\" — only ~10% visible — comes from this ratio. "
            "Common slip: reporting submerged fraction (89.5%) when asked for above. "
            "Another error: using fresh water density 1000 instead of seawater 1025. "
            "With fresh water, fraction above would be $1 - 917/1000 = 8.3$% — "
            "noticeably less than the 10.5% in seawater. "
            "**Exam tip:** always subtract from 1 when the stem asks \"above water.\" "
            "**Answer:** $\\approx 10.5$% above water."
        ),
        "he": (
            "קרחון צף: שבר שקוע $= \\rho_{\\text{קרח}}/\\rho_{\\text{ים}} "
            "= 917/1025 = 0.895$ (89.5% מתחת למים). "
            "שבר **מעל** המים $= 1 - 0.895 = 0.105 \\approx 10.5$%. "
            "מי ים צפופים יותר ממים מתוקים (1025 לעומת 1000), ולכן קרח גבוה יותר באוקיינוס. "
            "ה\"קצה של קרחון\" המפורסם — רק ~10% נראה — נובע מהיחס הזה. "
            "טעות נפוצה: דיווח שבר שקוע (89.5%) כששואלים על מעל. "
            "טעות נוספת: שימוש בצפיפות מים 1000 במקום ים 1025. "
            "במים מתוקים, שבר מעל היה $1 - 917/1000 = 8.3$% — "
            "בעקיפין פחות מ-10.5% בים. "
            "**טיפ לבחינה:** חסרו תמיד מ-1 כשהניסוח שואל \"מעל המים.\" "
            "**תשובה:** $\\approx 10.5$% מעל המים."
        ),
    },
}


def main():
    orig = json.loads(SRC.read_text(encoding="utf-8"))
    lesson = dict(orig)
    lesson["version"] = 2
    lesson["summary_en"] = (
        "Master fluid statics: pressure at depth, Pascal's hydraulics, Archimedes' buoyancy, "
        "and floating conditions for Bagrut and university entrance exams."
    )
    lesson["summary_he"] = (
        "שליטה בסטטיקת נוזלים: לחץ בעומק, הידראוליקת פסקל, ציפת ארכימדס "
        "ותנאי ציפה לבגרות ולמבחני כניסה לאוניברסיטה."
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
        if kind in MIN_WORDS:
            mw = MIN_WORDS[kind]
        elif sid in SECTION_BODIES:
            mw = MIN_WORDS["worked_example"]
        else:
            continue
        for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
            wc = word_count(sec.get(field, ""))
            need = mw[lang]
            if wc < need:
                errors.append(f"{sec.get('id', kind)} {lang}: {wc} < {need}")
        if sec.get("body_he_md") and sec.get("body_en_md"):
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
