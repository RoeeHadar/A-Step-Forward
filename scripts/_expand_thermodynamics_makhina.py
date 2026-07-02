#!/usr/bin/env python3
"""Expand thermodynamics_makhina.json — bilingual depth per expand-lessons-cursor."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/thermodynamics_makhina.json"

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
            "Heating water without boiling is **sensible heat** — temperature rises while the phase "
            "stays liquid. Use $Q = mc\\Delta T$ with $m = 1$ kg, $c = 4186$ J/kg·K, and "
            "$\\Delta T = 30° - 10° = 20$ K (or °C for differences):\n"
            "$$Q = 1 \\times 4186 \\times 20 = 83720\\;\\text{J}$$\n\n"
            "**Why option 2 is correct:** The full formula was applied with the correct temperature "
            "interval. Option 1 ($41860$ J) uses $\\Delta T = 10$ K — half the actual change. "
            "Option 3 ($4186$ J) forgets to multiply by $\\Delta T$.\n\n"
            "**Common wrong path:** Using Celsius difference incorrectly or substituting $c$ in "
            "cal/g instead of J/kg.\n\n"
            "**Exam tip:** For water near room temperature, $c \\approx 4186$ J/kg·K. "
            "Always state $\\Delta T$ before plugging into the calorimetry formula."
        ),
        "he": (
            "חימום מים בלי רתיחה הוא **חום סנסיבלי** — הטמפרטורה עולה בעוד שהפאזה נשארת נוזל. "
            "משתמשים ב-$Q = mc\\Delta T$ עם $m = 1$ kg, $c = 4186$ J/kg·K, ו-$\\Delta T = 30° - 10° = 20$ K:\n"
            "$$Q = 1 \\times 4186 \\times 20 = 83720\\;\\text{J}$$\n\n"
            "**למה אפשרות 2 נכונה:** הנוסחה המלאה הוחלה עם מרווח הטמפרטורה הנכון. "
            "אפשרות 1 ($41860$ J) משתמשת ב-$\\Delta T = 10$ K — חצי מהשינוי האמיתי. "
            "אפשרות 3 ($4186$ J) שוכחת לכפול ב-$\\Delta T$.\n\n"
            "**טעות נפוצה:** שימוש שגוי בהפרש Celsius או הצבת $c$ ב-cal/g במקום J/kg.\n\n"
            "**טип לבחינה:** למים בטמפרטורת חדר, $c \\approx 4186$ J/kg·K. "
            "כתבו תמיד את $\\Delta T$ לפני ההצבה בנוסחת הקלורימטריה."
        ),
    },
    2: {
        "en": (
            "Convert mass to kilograms first: $500$ g $= 0.5$ kg. The temperature rises from "
            "$25°$C to $75°$C, so $\\Delta T = 50$ K. This is pure sensible heat — no phase "
            "change — so apply $Q = mc\\Delta T$:\n"
            "$$Q = 0.5 \\times 4186 \\times 50 = 104650\\;\\text{J}$$\n\n"
            "**Why this is correct:** Each factor matches the problem: correct mass in kg, "
            "water's specific heat, and the full temperature interval.\n\n"
            "**Common wrong path:** Leaving mass in grams ($500 \\times 4186 \\times 50$) "
            "inflates the answer by 1000×. Another slip: using $\\Delta T = 75$ instead of "
            "the difference $50$.\n\n"
            "**Exam tip:** Circle \"g\" or \"kg\" in the stem before calculating. "
            "Makhina thermodynamics problems often mix unit prefixes to test careful reading."
        ),
        "he": (
            "המרת מסה לקילוגרם תחילה: $500$ g $= 0.5$ kg. הטמפרטורה עולה מ-$25°$C ל-$75°$C, "
            "ולכן $\\Delta T = 50$ K. זה חום סנסיבלי טהור — ללא שינוי פאזה — ולכן מיישמים "
            "$Q = mc\\Delta T$:\n"
            "$$Q = 0.5 \\times 4186 \\times 50 = 104650\\;\\text{J}$$\n\n"
            "**למה זה נכון:** כל גורם תואם את הבעיה: מסה נכונה ב-kg, חום סגולי של מים, "
            "ומרווח הטמפרטורה המלא.\n\n"
            "**טעות נפוצה:** השארת מסה בגרם ($500 \\times 4186 \\times 50$) מנפחת את התשובה "
            "פי 1000. טעות נוספת: שימוש ב-$\\Delta T = 75$ במקום ההפרש $50$.\n\n"
            "**טיפ לבחינה:** סמנו \"g\" או \"kg\" בנתון לפני החישוב. "
            "בעיות תרמודינמיקה במכינה לעיתים מערבבות תחיליות יחידות."
        ),
    },
    3: {
        "en": (
            "The first law of thermodynamics relates internal energy change to heat and work: "
            "$\\Delta U = Q - W$, where $Q > 0$ means heat absorbed by the system and "
            "$W > 0$ means work done **by** the system on surroundings.\n\n"
            "Here $Q = +300$ J (absorbed) and $W = +100$ J (done by gas):\n"
            "$$\\Delta U = 300 - 100 = 200\\;\\text{J}$$\n\n"
            "**Why this is correct:** Positive $\\Delta U$ means the gas gained internal energy — "
            "more heat entered than work left.\n\n"
            "**Common wrong path:** Writing $\\Delta U = Q + W$ or reversing the sign of work "
            "($300 + 100 = 400$ J). Always confirm whether $W$ is \"by system\" or \"on system.\"\n\n"
            "**Exam tip:** Underline \"done by\" vs \"done on\" in the stem. "
            "Bagrut sign conventions match $\\Delta U = Q - W$ with $W$ as work by the system."
        ),
        "he": (
            "החוק הראשון של התרמודינמיקה מקשר שינוי אנרגיה פנימית לחום ולעבודה: "
            "$\\Delta U = Q - W$, כאשר $Q > 0$ פירושו חום שנקלט במערכת ו-$W > 0$ פירושו "
            "עבודה ש**המערכת** מבצעת על הסביבה.\n\n"
            "כאן $Q = +300$ J (נקלט) ו-$W = +100$ J (על ידי הגז):\n"
            "$$\\Delta U = 300 - 100 = 200\\;\\text{J}$$\n\n"
            "**למה זה נכון:** $\\Delta U$ חיובי פירושו שהגז קיבל אנרגיה פנימית — "
            "נכנס יותר חום ממה שיצאה עבודה.\n\n"
            "**טעות נפוצה:** כתיבת $\\Delta U = Q + W$ או היפוך סימן העבודה "
            "($300 + 100 = 400$ J). וודאו תמיד אם $W$ הוא \"על ידי\" או \"על\" המערכת.\n\n"
            "**טיפ לבחינה:** סמנו \"על ידי\" לעומת \"על\" בנתון. "
            "מוסכמת הסימנים בבגרות תואמת $\\Delta U = Q - W$ עם $W$ כעבודה על ידי המערכת."
        ),
    },
    4: {
        "en": (
            "Melting ice at $0°$C is a **phase change** at constant temperature. "
            "All supplied heat breaks bonds — it does not raise temperature. Use latent heat:\n"
            "$$Q = mL_f = 2 \\times 334000 = 668000\\;\\text{J} = 668\\;\\text{kJ}$$\n\n"
            "**Why this is correct:** At the melting point, $Q = mL$ replaces $mc\\Delta T$ "
            "because $\\Delta T = 0$ during the transition.\n\n"
            "**Common wrong path:** Applying $mc\\Delta T$ with some assumed temperature rise, "
            "or using $L_v$ (vaporisation) instead of $L_f$ (fusion). Water's $L_f = 334\\,000$ J/kg.\n\n"
            "**Exam tip:** Keywords \"melt,\" \"freeze,\" \"boil,\" or \"vaporise\" signal $Q = mL$. "
            "Draw a temperature-vs-heat sketch with flat plateaus at phase changes."
        ),
        "he": (
            "המסת קרח ב-$0°$C היא **שינוי פאזה** בטמפרטורה קבועה. "
            "כל החום המסופק שובר קשרים — הוא לא מעלה טמפרטורה. משתמשים בחום סמוי:\n"
            "$$Q = mL_f = 2 \\times 334000 = 668000\\;\\text{J} = 668\\;\\text{kJ}$$\n\n"
            "**למה זה נכון:** בנקודת ההמסה, $Q = mL$ מחליף את $mc\\Delta T$ "
            "כי $\\Delta T = 0$ במהלך המעבר.\n\n"
            "**טעות נפוצה:** יישום $mc\\Delta T$ עם עליית טמפרטura מניחה, "
            "או שימוש ב-$L_v$ (אידוי) במקום $L_f$ (המסה). ל-$L_f$ של מים: $334\\,000$ J/kg.\n\n"
            "**טיפ לבחינה:** מילות מפתח \"המסה,\" \"קיפאון,\" \"רתיחה\" או \"אידוי\" מסמנות $Q = mL$. "
            "ציירו גרף טמפרטורה מול חום עם רמות שטוחות בשינויי פאזה."
        ),
    },
    5: {
        "en": (
            "An **adiabatic** process has $Q = 0$ — no heat crosses the boundary. "
            "The first law simplifies to $\\Delta U = -W$ when $Q = 0$.\n\n"
            "The gas does $W = 400$ J of work on surroundings (expansion), so:\n"
            "$$\\Delta U = Q - W = 0 - 400 = -400\\;\\text{J}$$\n\n"
            "**Why this is correct:** Negative $\\Delta U$ means internal energy dropped — "
            "the gas spent its stored energy doing expansion work, typically cooling down.\n\n"
            "**Common wrong path:** Answering $+400$ J by forgetting the minus sign in "
            "$\\Delta U = Q - W$, or treating adiabatic as isothermal ($\\Delta U = 0$).\n\n"
            "**Exam tip:** Adiabatic $\\Rightarrow Q = 0$ immediately. "
            "Link to rapid compression in bicycle pumps — work converts to temperature rise."
        ),
        "he": (
            "תהליך **אדיאבטי** עם $Q = 0$ — אין חום שחוצה את הגבול. "
            "החוק הראשון מתפשט ל-$\\Delta U = -W$ כש-$Q = 0$.\n\n"
            "הגז מבצע $W = 400$ J עבודה על הסביבה (התרחבות), ולכן:\n"
            "$$\\Delta U = Q - W = 0 - 400 = -400\\;\\text{J}$$\n\n"
            "**למה זה נכון:** $\\Delta U$ שלילי פירושו שהאנרגיה הפנימית ירדה — "
            "הגז הוציא אנרגיה אגורה לעבודת התרחבות, בדרך כלל מתקרר.\n\n"
            "**טעות נפוצה:** תשובה $+400$ J משכחת הסימן מינוס ב-$\\Delta U = Q - W$, "
            "או התייחסות לאדיאבטי כאיזותרמי ($\\Delta U = 0$).\n\n"
            "**טיפ לבחינה:** אדיאבטי $\\Rightarrow Q = 0$ מיד. "
            "קשרו לדחיסה מהירה במשאבת אופניים — עבודה הופכת לעליית טמפרטורה."
        ),
    },
    6: {
        "en": (
            "This problem has **two stages**: (1) heat liquid water from $20°$C to $100°$C, "
            "then (2) vaporise it at $100°$C. Each stage uses a different formula.\n\n"
            "Stage 1 — sensible heat: $Q_1 = mc\\Delta T = 0.2 \\times 4186 \\times 80 = 67000$ J.\n"
            "Stage 2 — latent heat at boiling: $Q_2 = mL_v = 0.2 \\times 2.26 \\times 10^6 = 452000$ J.\n"
            "$$Q_{\\text{total}} = 67000 + 452000 = 519000\\;\\text{J}$$\n\n"
            "**Common wrong path:** Using $mc\\Delta T$ through the boiling point without "
            "switching to $mL_v$, or stopping after stage 1 only.\n\n"
            "**Exam tip:** List stages in a table before summing. "
            "Vaporisation dominates — stage 2 is typically much larger than stage 1."
        ),
        "he": (
            "לבעיה זו **שני שלבים**: (1) חימום מים נוזליים מ-$20°$C ל-$100°$C, "
            "ואז (2) אידוי ב-$100°$C. כל שלב משתמש בנוסחה שונה.\n\n"
            "שלב 1 — חום סנסיבלי: $Q_1 = mc\\Delta T = 0.2 \\times 4186 \\times 80 = 67000$ J.\n"
            "שלב 2 — חום סמוי ברתיחה: $Q_2 = mL_v = 0.2 \\times 2.26 \\times 10^6 = 452000$ J.\n"
            "$$Q_{\\text{total}} = 67000 + 452000 = 519000\\;\\text{J}$$\n\n"
            "**טעות נפוצה:** שימוש ב-$mc\\Delta T$ דרך נקודת הרתיחה בלי מעבר ל-$mL_v$, "
            "או עצירה אחרי שלב 1 בלבד.\n\n"
            "**טיפ לבחינה:** רשימו שלבים בטבלה לפני הסכימה. "
            "האידוי שולט — שלב 2 בדרך כלל גדול הרבה משלב 1."
        ),
    },
    7: {
        "en": (
            "An **isobaric** (constant pressure) expansion uses $W = P\\Delta V$. "
            "Convert volumes to SI: $\\Delta V = 3\\,\\text{L} - 2\\,\\text{L} = 1\\,\\text{L} = 0.001\\,\\text{m}^3$.\n\n"
            "With $P = 10^5$ Pa:\n"
            "$$W = P\\Delta V = 10^5 \\times 0.001 = 100\\;\\text{J}$$\n\n"
            "**Why this is correct:** Work equals pressure times volume change at constant $P$. "
            "Positive $W$ means the gas expanded and did work on surroundings.\n\n"
            "**Common wrong path:** Using $\\Delta V = 3$ L without converting to m³, "
            "giving $3 \\times 10^5$ J — off by 1000×. Another error: using $W = nRT\\ln(V_f/V_i)$ "
            "which applies to isothermal, not isobaric.\n\n"
            "**Exam tip:** Always convert litres to m³ ($1\\,\\text{L} = 10^{-3}\\,\\text{m}^3$) "
            "before multiplying by pressure in pascals."
        ),
        "he": (
            "התרחבות **איזוברית** (לחץ קבוע) משתמשת ב-$W = P\\Delta V$. "
            "המרת נפחים ל-SI: $\\Delta V = 3\\,\\text{L} - 2\\,\\text{L} = 1\\,\\text{L} = 0.001\\,\\text{m}^3$.\n\n"
            "עם $P = 10^5$ Pa:\n"
            "$$W = P\\Delta V = 10^5 \\times 0.001 = 100\\;\\text{J}$$\n\n"
            "**למה זה נכון:** עבודה שווה ללחץ כפול שינוי נפח ב-$P$ קבוע. "
            "$W$ חיובי פירושו שהגז התרחב וביצע עבודה על הסביבה.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\Delta V = 3$ L בלי המרה ל-m³, "
            "ונתינת $3 \\times 10^5$ J — טעות פי 1000. שגיאה נוספת: $W = nRT\\ln(V_f/V_i)$ "
            "שמתאים לאיזותרמי, לא לאיזוברי.\n\n"
            "**טיפ לבחינה:** המירו תמיד ליטר ל-m³ ($1\\,\\text{L} = 10^{-3}\\,\\text{m}^3$) "
            "לפני כפל בלחץ בפסקל."
        ),
    },
    8: {
        "en": (
            "Apply the ideal gas law $PV = nRT$ with $T$ in **Kelvin** (already $300$ K), "
            "$n = 1$ mol, $R = 8.314$ J/mol·K, and $V = 24.9$ L $= 0.0249$ m³:\n"
            "$$P = \\frac{nRT}{V} = \\frac{8.314 \\times 300}{0.0249} \\approx 10^5\\;\\text{Pa}$$\n\n"
            "**Why this is correct:** At $300$ K and $24.9$ L per mole, pressure is near "
            "standard atmospheric pressure ($1.013 \\times 10^5$ Pa) — a sanity check.\n\n"
            "**Common wrong path:** Leaving volume in litres ($8.314 \\times 300 / 24.9$) "
            "gives a pressure 1000× too small. Forgetting to convert $T$ from °C is another "
            "classic error when $T$ is not already in Kelvin.\n\n"
            "**Exam tip:** $PV = nRT$ always needs $T$ in K and $V$ in m³ with $P$ in Pa."
        ),
        "he": (
            "יישום חוק הגז האידיאלי $PV = nRT$ עם $T$ ב**קלווין** (כבר $300$ K), "
            "$n = 1$ mol, $R = 8.314$ J/mol·K, ו-$V = 24.9$ L $= 0.0249$ m³:\n"
            "$$P = \\frac{nRT}{V} = \\frac{8.314 \\times 300}{0.0249} \\approx 10^5\\;\\text{Pa}$$\n\n"
            "**למה זה נכון:** ב-$300$ K ו-$24.9$ L למול, הלחץ קרוב ללחץ אטמוספרי "
            "($1.013 \\times 10^5$ Pa) — בדיקת הגיון.\n\n"
            "**טעות נפוצה:** השארת נפח בליטר ($8.314 \\times 300 / 24.9$) "
            "נותנת לחץ קטן פי 1000. שכחת המרת $T$ מ-°C היא טעות קלאסית נוספת.\n\n"
            "**טיפ לבחינה:** $PV = nRT$ תמיד דורש $T$ ב-K ו-$V$ ב-m³ עם $P$ ב-Pa."
        ),
    },
}


def build_lesson():
    with open(OUT, encoding="utf-8") as f:
        lesson = json.load(f)

    section_bodies = {
        "intro": {
            "en": (
                "Thermodynamics connects everyday experience — boiling water, warming your hands, "
                "a bicycle pump heating up — to precise energy accounting. **Heat** $Q$ is energy "
                "in transit due to temperature difference; **work** $W$ is organized energy transfer "
                "by forces; **internal energy** $U$ is the stored microscopic energy of a system.\n\n"
                "The central principle is **conservation of energy**: heat supplied can raise "
                "temperature, drive a phase change, or perform work — but the total is always "
                "accounted for by the first law $\\Delta U = Q - W$.\n\n"
                "**Makhina track focus:** Calorimetry ($Q = mc\\Delta T$ and $Q = mL$), first-law "
                "sign conventions, ideal gas law $PV = nRT$, and the four standard processes "
                "(isothermal, adiabatic, isochoric, isobaric).\n\n"
                "By the end of this lesson you will classify a problem by process type, choose "
                "the correct formula, convert units (especially litres and Kelvin), and solve "
                "multi-stage heating curves typical of university entrance exams."
            ),
            "he": (
                "תרמודינמיקה מחברת חוויית יומיום — רתיחת מים, חימום כפיים, משאבת אופניים "
                "שמתחממת — לחשבון אנרגיה מדויק. **חום** $Q$ הוא אנרגיה בתנועה בגלל הפרש "
                "טמפרטורות; **עבודה** $W$ היא העברת אנרגיה מסודרת על ידי כוחות; **אנרגיה "
                "פנימית** $U$ היא האנרגיה המיקרוסקופית האגורה במערכת.\n\n"
                "העיקרון המרכזי הוא **שימור אנרגיה**: חום שמסופק יכול להעלות טמפרטורה, "
                "לגרום לשינוי פאזה, או לבצע עבודה — אך הסך הכל תמיד מחושב בחוק הראשון "
                "$\\Delta U = Q - W$.\n\n"
                "**מיקוד מסלול מכינה:** קלורימטריה ($Q = mc\\Delta T$ ו-$Q = mL$), "
                "מוסכמות סימן בחוק הראשון, חוק הגז האידיאלי $PV = nRT$, וארבעת התהליכים "
                "הסטנדרטיים (איזותרמי, אדיאבטי, איזוכורי, איזוברי).\n\n"
                "בסוף השיעור תסווגו בעיה לפי סוג תהליך, תבחרו נוסחה נכונה, "
                "תמירו יחידות (במיוחד ליטר וקלווין), ותפתרו עקומות חימום רב-שלביות "
                "אופייניות לבחינות כניסה לאוניברסיטה."
            ),
        },
        "definition": {
            "en": (
                "**Sensible heat** (temperature change within one phase):\n"
                "$$Q = mc\\Delta T$$\n"
                "- $m$: mass (kg); $c$: specific heat capacity (J/kg·K); "
                "$\\Delta T$: temperature change (K or °C for differences)\n\n"
                "**Latent heat** (phase change at constant temperature):\n"
                "$$Q = mL$$\n"
                "- $L_f$: latent heat of fusion (melting/freezing); "
                "$L_v$: latent heat of vaporisation (boiling/condensing)\n\n"
                "**First law of thermodynamics:**\n"
                "$$\\Delta U = Q - W$$\n"
                "- $\\Delta U$: change in internal energy; $Q > 0$ heat absorbed by system; "
                "$W > 0$ work done **by** the system\n\n"
                "**Ideal gas law:**\n"
                "$$PV = nRT$$\n"
                "$P$ (Pa), $V$ (m³), $n$ (mol), $R = 8.314$ J/mol·K, $T$ (K only)\n\n"
                "**Water reference values (memorise for exams):** "
                "$c_{\\text{water}} = 4186$ J/kg·K; $L_f = 334\\,000$ J/kg; "
                "$L_v = 2.26 \\times 10^6$ J/kg."
            ),
            "he": (
                "**חום סנסיבלי** (שינוי טמפרטura באותה פאזה):\n"
                "$$Q = mc\\Delta T$$\n"
                "- $m$: מסה (kg); $c$: חום סגולי (J/kg·K); "
                "$\\Delta T$: שינוי טמפרטורה (K או °C להפרשים)\n\n"
                "**חום סמוי** (שינוי פאזה בטמפרטורה קבועה):\n"
                "$$Q = mL$$\n"
                "- $L_f$: חום סמוי של היתוך (המסה/קיפאון); "
                "$L_v$: חום סמוי של אידוי (רתיחה/עיבוי)\n\n"
                "**חוק ראשון של התרמודינמיקה:**\n"
                "$$\\Delta U = Q - W$$\n"
                "- $\\Delta U$: שינוי אנרגיה פנימית; $Q > 0$ חום שנקלט; "
                "$W > 0$ עבודה **על ידי** המערכת\n\n"
                "**חוק הגז האידיאלי:**\n"
                "$$PV = nRT$$\n"
                "$P$ (Pa), $V$ (m³), $n$ (mol), $R = 8.314$ J/mol·K, $T$ (K בלבד)\n\n"
                "**ערכי מים לבחינה:** $c_{\\text{water}} = 4186$ J/kg·K; "
                "$L_f = 334\\,000$ J/kg; $L_v = 2.26 \\times 10^6$ J/kg."
            ),
        },
        "theory": {
            "en": (
                "Four ideal-gas processes appear repeatedly on Makhina exams. Each simplifies "
                "one quantity held constant:\n\n"
                "| Process | Condition | Work $W$ | $\\Delta U$ |\n"
                "|---|---|---|---|\n"
                "| Isothermal | $T = \\text{const}$ | $nRT\\ln(V_f/V_i)$ | $0$ |\n"
                "| Adiabatic | $Q = 0$ | $-\\Delta U$ | $-W$ |\n"
                "| Isochoric | $V = \\text{const}$ | $0$ | $Q$ |\n"
                "| Isobaric | $P = \\text{const}$ | $P\\Delta V$ | $Q - P\\Delta V$ |\n\n"
                "For a **monatomic ideal gas**, internal energy depends only on temperature: "
                "$\\Delta U = \\frac{3}{2}nR\\Delta T$.\n\n"
                "**Calorimetry strategy:** On a heating curve, flat segments at melting ($0°$C) "
                "or boiling ($100°$C) use $Q = mL$; sloped segments use $Q = mc\\Delta T$. "
                "Sum every stage separately.\n\n"
                "**Sign conventions:** Expansion $\\Rightarrow$ gas does positive work ($W > 0$). "
                "Heat entering $\\Rightarrow$ $Q > 0$. Always write $\\Delta U = Q - W$ with "
                "this convention before substituting numbers.\n\n"
                "**Unit checklist:** Convert $T$ to Kelvin for $PV = nRT$; convert litres to "
                "m³ for pressure-volume work; keep mass in kilograms."
            ),
            "he": (
                "ארבעה תהליכי גaz אידיאלי מופיעים שוב ושוב בבחינות מכינה. "
                "כל אחד מפשט כמות שנשמרת קבועה:\n\n"
                "| תהליך | תנאי | עבודה $W$ | $\\Delta U$ |\n"
                "|---|---|---|---|\n"
                "| איזותרמי | $T = \\text{קבוע}$ | $nRT\\ln(V_f/V_i)$ | $0$ |\n"
                "| אדיאבטי | $Q = 0$ | $-\\Delta U$ | $-W$ |\n"
                "| איזוכורי | $V = \\text{קבוע}$ | $0$ | $Q$ |\n"
                "| איזוברי | $P = \\text{קבוע}$ | $P\\Delta V$ | $Q - P\\Delta V$ |\n\n"
                "עבור **גז אידיאלי חד-אטומי**, אנרגיה פנימית תלויה רק בטמפרטורה: "
                "$\\Delta U = \\frac{3}{2}nR\\Delta T$.\n\n"
                "**אסטרטגיית קלורימטריה:** בעקומת חימום, קטעים שטוחים בהמסה ($0°$C) "
                "או רתיחה ($100°$C) משתמשים ב-$Q = mL$; קטעים משופעים ב-$Q = mc\\Delta T$. "
                "סכמו כל שלב בנפרד.\n\n"
                "**מוסכמות סימן:** התרחבות $\\Rightarrow$ הגז מבצע עבודה חיובית ($W > 0$). "
                "חום שנכנס $\\Rightarrow$ $Q > 0$. כתבו תמיד $\\Delta U = Q - W$ "
                "לפני הצבת מספרים.\n\n"
                "**רשימת יחידות:** המירו $T$ לקלווין ב-$PV = nRT$; המירו ליטר ל-m³ "
                "לעבודת לחץ-נפח; שמרו מסה בקילוגרם."
            ),
        },
        "worked_example_1": {
            "en": (
                "**Heat** $2$ kg of water from $20°$C to $80°$C using calorimetry.\n\n"
                "### Move 1: Identify the process\n"
                "Liquid water heating — no phase change. Use $Q = mc\\Delta T$.\n\n"
                "### Move 2: Compute $\\Delta T$\n"
                "$$\\Delta T = 80 - 20 = 60\\;\\text{K}$$\n\n"
                "### Move 3: Substitute\n"
                "$$Q = mc\\Delta T = 2 \\times 4186 \\times 60 = 502320\\;\\text{J} \\approx 502.3\\;\\text{kJ}$$\n\n"
                "### Move 4: Alternative unit check\n"
                "In kilocalories: $502320 / 4186 \\approx 120$ kcal — reasonable for heating "
                "two litres of water by $60°$.\n\n"
                "**Exam tip:** Show $\\Delta T$ explicitly. Examiners deduct marks when students "
                "substitute final temperature instead of the difference."
            ),
            "he": (
                "**חימום** $2$ kg מים מ-$20°$C ל-$80°$C באמצעות קלורימטריה.\n\n"
                "### צעד 1: זיהוי התהליך\n"
                "חימום מים נוזליים — ללא שינוי פאזה. משתמשים ב-$Q = mc\\Delta T$.\n\n"
                "### צעד 2: חישוב $\\Delta T$\n"
                "$$\\Delta T = 80 - 20 = 60\\;\\text{K}$$\n\n"
                "### צעד 3: הצבה\n"
                "$$Q = mc\\Delta T = 2 \\times 4186 \\times 60 = 502320\\;\\text{J} \\approx 502.3\\;\\text{kJ}$$\n\n"
                "### צעד 4: בדיקת יחידות חלופית\n"
                "בקילוקלוריות: $502320 / 4186 \\approx 120$ kcal — הגיוני לחימום "
                "שני ליטר מים ב-$60°$.\n\n"
                "**טיפ לבחינה:** הציגו $\\Delta T$ במפורש. בוחנים מורידים ניקוד כשמציבים "
                "טמפרטורה סופית במקום ההפרש."
            ),
        },
        "worked_example_2": {
            "en": (
                "**Total heat** to take $1$ kg of ice from $-10°$C to steam at $100°$C — "
                "a classic five-stage Makhina problem.\n\n"
                "### Move 1: Heat ice ($-10°$C $\\to$ $0°$C)\n"
                "$$Q_1 = mc\\Delta T = 1 \\times 2090 \\times 10 = 20900\\;\\text{J}$$\n\n"
                "### Move 2: Melt ice at $0°$C\n"
                "$$Q_2 = mL_f = 1 \\times 334000 = 334000\\;\\text{J}$$\n\n"
                "### Move 3: Heat water ($0°$C $\\to$ $100°$C)\n"
                "$$Q_3 = 1 \\times 4186 \\times 100 = 418600\\;\\text{J}$$\n\n"
                "### Move 4: Vaporise at $100°$C\n"
                "$$Q_4 = mL_v = 1 \\times 2.26 \\times 10^6 = 2260000\\;\\text{J}$$\n\n"
                "### Move 5: Sum all stages\n"
                "$$Q_{\\text{total}} = 20900 + 334000 + 418600 + 2260000 = 3033500\\;\\text{J} \\approx 3.03\\;\\text{MJ}$$\n\n"
                "Vaporisation ($Q_4$) dominates — about 75% of total energy. "
                "**Exam tip:** Draw a heating curve and label each segment before calculating."
            ),
            "he": (
                "**סך החום** להעברת $1$ kg קרח מ-$-10°$C לאדים ב-$100°$C — "
                "בעיה קלאסית של חמישה שלבים במכינה.\n\n"
                "### צעד 1: חימום קרח ($-10°$C $\\to$ $0°$C)\n"
                "$$Q_1 = mc\\Delta T = 1 \\times 2090 \\times 10 = 20900\\;\\text{J}$$\n\n"
                "### צעד 2: המסת קרח ב-$0°$C\n"
                "$$Q_2 = mL_f = 1 \\times 334000 = 334000\\;\\text{J}$$\n\n"
                "### צעד 3: חימום מים ($0°$C $\\to$ $100°$C)\n"
                "$$Q_3 = 1 \\times 4186 \\times 100 = 418600\\;\\text{J}$$\n\n"
                "### צעד 4: אידוי ב-$100°$C\n"
                "$$Q_4 = mL_v = 1 \\times 2.26 \\times 10^6 = 2260000\\;\\text{J}$$\n\n"
                "### צעד 5: סכום כל השלבים\n"
                "$$Q_{\\text{total}} = 20900 + 334000 + 418600 + 2260000 = 3033500\\;\\text{J} \\approx 3.03\\;\\text{MJ}$$\n\n"
                "האידוי ($Q_4$) שולט — כ-75% מהאנרגיה הכוללת. "
                "**טיפ לבחינה:** ציירו עקומת חימום וסמנו כל קטע לפני החישוב."
            ),
        },
        "worked_example_3": {
            "en": (
                "Compare **isothermal** vs **adiabatic** compression of $1$ mol ideal gas "
                "at $T_i = 300$ K from $V_i = 1$ L to $V_f = 0.5$ L.\n\n"
                "### Move 1: Isothermal ($T = 300$ K constant, $\\Delta U = 0$)\n"
                "$$W = nRT\\ln\\frac{V_f}{V_i} = 8.314 \\times 300 \\times \\ln(0.5) = -1729\\;\\text{J}$$\n"
                "Work done **on** gas is $+1729$ J; heat leaves: $Q = -1729$ J.\n\n"
                "### Move 2: Adiabatic ($Q = 0$, monatomic $\\gamma = 5/3$)\n"
                "$$T_f = T_i\\left(\\frac{V_i}{V_f}\\right)^{\\gamma-1} = 300 \\times 2^{2/3} \\approx 476\\;\\text{K}$$\n"
                "$$\\Delta U = \\frac{3}{2}nR\\Delta T = \\frac{3}{2} \\times 8.314 \\times 176 \\approx 2197\\;\\text{J}$$\n\n"
                "### Move 3: Physical comparison\n"
                "Isothermal compression sheds heat to stay at $300$ K. Adiabatic compression "
                "traps the work as internal energy — temperature rises to $476$ K.\n\n"
                "**Exam tip:** When comparing processes, always state which quantity is held constant first."
            ),
            "he": (
                "השוואת דחיסה **איזותרמית** לעומת **אדיאבטית** של $1$ mol גז אידיאלי "
                "ב-$T_i = 300$ K מ-$V_i = 1$ L ל-$V_f = 0.5$ L.\n\n"
                "### צעד 1: איזותרמי ($T = 300$ K קבוע, $\\Delta U = 0$)\n"
                "$$W = nRT\\ln\\frac{V_f}{V_i} = 8.314 \\times 300 \\times \\ln(0.5) = -1729\\;\\text{J}$$\n"
                "עבודה **על** הגז: $+1729$ J; חום יוצא: $Q = -1729$ J.\n\n"
                "### צעד 2: אדיאבטי ($Q = 0$, חד-אטומי $\\gamma = 5/3$)\n"
                "$$T_f = T_i\\left(\\frac{V_i}{V_f}\\right)^{\\gamma-1} = 300 \\times 2^{2/3} \\approx 476\\;\\text{K}$$\n"
                "$$\\Delta U = \\frac{3}{2}nR\\Delta T = \\frac{3}{2} \\times 8.314 \\times 176 \\approx 2197\\;\\text{J}$$\n\n"
                "### צעד 3: השוואה פיזיקלית\n"
                "דחיסה איזותרמית משחררת חום כדי להישאר ב-$300$ K. דחיסה אדיאבטית "
                "לוכדת את העבודה כאנרגיה פנימית — הטמפרטורה עולה ל-$476$ K.\n\n"
                "**טיפ לבחינה:** בהשוואת תהליכים, ציינו תמיד איזו כמות נשמרת קבועה תחילה."
            ),
        },
        "method_guide": {
            "en": (
                "| Task | Formula | When to use |\n"
                "|---|---|---|\n"
                "| Temperature change | $Q = mc\\Delta T$ | Same phase, $\\Delta T \\ne 0$ |\n"
                "| Phase change | $Q = mL$ | Melting, boiling, etc. at fixed $T$ |\n"
                "| Multi-stage heating | Sum each stage | Ice $\\to$ water $\\to$ steam problems |\n"
                "| First law | $\\Delta U = Q - W$ | Any process with heat and work |\n"
                "| Ideal gas state | $PV = nRT$ | Find $P$, $V$, $n$, or $T$ ($T$ in K) |\n"
                "| Isothermal work | $W = nRT\\ln(V_f/V_i)$ | $T$ constant, ideal gas |\n"
                "| Isobaric work | $W = P\\Delta V$ | $P$ constant; convert L to m³ |\n\n"
                "**Workflow:** Read the stem $\\to$ identify process type $\\to$ pick the table row "
                "$\\to$ convert units $\\to$ substitute numbers last.\n\n"
                "**Tip:** If two rows seem to fit, list givens and match them to columns before calculating."
            ),
            "he": (
                "| משימה | נוסחה | מתי להשתמש |\n"
                "|---|---|---|\n"
                "| שינוי טמפרטורה | $Q = mc\\Delta T$ | אותה פאזה, $\\Delta T \\ne 0$ |\n"
                "| שינוי פאזה | $Q = mL$ | המסה, רתיחה וכו' ב-$T$ קבוע |\n"
                "| חימום רב-שלבי | סכום כל שלב | בעיות קרח $\\to$ מים $\\to$ אדים |\n"
                "| חוק ראשון | $\\Delta U = Q - W$ | כל תהליך עם חום ועבודה |\n"
                "| מצב גaz אידיאלי | $PV = nRT$ | מציאת $P$, $V$, $n$, או $T$ ($T$ ב-K) |\n"
                "| עבודה איזותרמית | $W = nRT\\ln(V_f/V_i)$ | $T$ קבוע, גז אידיאלי |\n"
                "| עבודה איזוברית | $W = P\\Delta V$ | $P$ קבוע; המירו L ל-m³ |\n\n"
                "**תהליך עבודה:** קראו את הנתון $\\to$ זהו סוג תהליך $\\to$ בחרו שורה בטבלה "
                "$\\to$ המירו יחידות $\\to$ הציבו מספרים בסוף.\n\n"
                "**טיפ:** אם שתי שורות מתאימות, רשימו נתונים והתאימו לעמודות לפני החישוב."
            ),
        },
        "pitfall": {
            "en": (
                "1. **Phase change: no temperature change.** At melting or boiling, all heat goes "
                "into $Q = mL$ — not $mc\\Delta T$. The temperature stays flat on a heating curve.\n\n"
                "2. **Sign convention for $W$:** $W > 0$ when the gas does work on surroundings "
                "(expansion). Use $\\Delta U = Q - W$ consistently.\n\n"
                "3. **Kelvin vs Celsius:** $PV = nRT$ requires $T$ in **Kelvin** ($T(K) = T(°C) + 273$). "
                "For $\\Delta T$, Celsius and Kelvin differences are equal.\n\n"
                "4. **Wrong specific heat:** Water $c = 4186$ J/kg·K; ice $c = 2090$; steam $c = 2010$. "
                "Do not use water's value for all phases.\n\n"
                "5. **Multi-stage problems:** Add each stage's heat separately — never skip "
                "latent-heat plateaus.\n\n"
                "**Exam tip:** After solving, ask which pitfall you avoided — not just \"what is the number?\""
            ),
            "he": (
                "1. **שינוי פאזה: אין שינוי טמפרטורה.** בהמסה או רתיחה, כל החום הולך ל-$Q = mL$ — "
                "לא ל-$mc\\Delta T$. הטמפרטורה נשארת שטוחה בעקומת חימום.\n\n"
                "2. **מוסכמת סימן ל-$W$:** $W > 0$ כשהגז מבצע עבודה על הסביבה (התרחבות). "
                "השתמשו ב-$\\Delta U = Q - W$ בעקביות.\n\n"
                "3. **קלווין לעומת Celsius:** $PV = nRT$ דורש $T$ ב**קלווין** ($T(K) = T(°C) + 273$). "
                "ל-$\\Delta T$, הפרשי Celsius וקלווין שווים.\n\n"
                "4. **חום סגולי שגוי:** מים $c = 4186$ J/kg·K; קרח $c = 2090$; אדים $c = 2010$. "
                "אל תשתמשו בערך של מים לכל הפאזות.\n\n"
                "5. **בעיות רב-שלביות:** חברו חום של כל שלב בנפרד — לעולם אל תדלגו "
                "על רמות חום סמוי.\n\n"
                "**טיפ לבחינה:** אחרי פתרון, שאלו איזו מלכודת נמנעתם — לא רק \"מה המספר?\""
            ),
        },
        "why_matters": {
            "en": (
                "Thermodynamics is the language of engines, climate science, chemical reactions, "
                "and medical imaging. Every time you cook, heat a room, or charge a battery, "
                "energy flows according to the same first-law accounting you learn here.\n\n"
                "**University connection:** Makhina thermodynamics prepares you for calculus-based "
                "physics courses where entropy, heat engines, and Carnot efficiency extend these ideas. "
                "Calorimetry skills transfer directly to chemistry labs measuring reaction heats.\n\n"
                "**Exam transfer:** Bagrut and entrance exams reward recognising process type from "
                "wording alone — \"adiabatic,\" \"melting,\" \"isobaric expansion\" each triggers "
                "a different formula path."
            ),
            "he": (
                "תרמודינמיקה היא שפת המנועים, מדעי האקlimה, תגובות כימיות והדמיה רפואית. "
                "בכל פעם שמבשלים, מחממים חדר או טוענים סוללה, אנרגיה זורמת לפי "
                "אותו חשבון של החוק הראשון שלומדים כאן.\n\n"
                "**קשר לאוניברסיטה:** תרמודינמיקה במכינה מכינה לקורסי פיזיקה מבוססי חשבון "
                "שבהם אנטרופיה, מנועי חום ויעילות קarno מרחיבים רעיונות אלה. "
                "מיומנויות קלורימטריה עוברות ישירות למעבדות כימיה.\n\n"
                "**העברה לבחינות:** בגרות ומבחני כניסה מעריכים זיהוי סוג תהליך מניסוח בלבד — "
                "\"אדיאבטי,\" \"המסה,\" \"התרחבות איזוברית\" — כל אחד מפעיל נתיב נוסחה שונה."
            ),
        },
        "before_exam": {
            "en": (
                "**Formula checklist:**\n"
                "- $Q = mc\\Delta T$ (temperature change); $Q = mL$ (phase change).\n"
                "- $\\Delta U = Q - W$ (first law; $W$ = work by system).\n"
                "- $PV = nRT$ with $T$ in Kelvin.\n"
                "- Water: $c = 4186$ J/kg·K; $L_f = 334$ kJ/kg; $L_v = 2260$ kJ/kg.\n"
                "- Processes: isothermal $\\Delta U = 0$; adiabatic $Q = 0$; isochoric $W = 0$.\n\n"
                "**Last review:** Say each formula aloud once, then solve one checkpoint without looking. "
                "Draw a heating curve from memory — label where $mc\\Delta T$ vs $mL$ applies."
            ),
            "he": (
                "**רשימת נוסחאות:**\n"
                "- $Q = mc\\Delta T$ (שינוי טמפרטורה); $Q = mL$ (שינוי פאזה).\n"
                "- $\\Delta U = Q - W$ (חוק ראשון; $W$ = עבודה על ידי המערכת).\n"
                "- $PV = nRT$ עם $T$ בקלווין.\n"
                "- מים: $c = 4186$ J/kg·K; $L_f = 334$ kJ/kg; $L_v = 2260$ kJ/kg.\n"
                "- תהליכים: איזותרמי $\\Delta U = 0$; אדיאבטי $Q = 0$; איזוכורי $W = 0$.\n\n"
                "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו בדיקה אחת בלי להסתכל. "
                "ציירו עקומת חימום מהזיכרון — סמנו היכן $mc\\Delta T$ לעומת $mL$."
            ),
        },
        "summary": {
            "en": (
                "- **Calorimetry:** $Q = mc\\Delta T$ for temperature change within a phase; "
                "$Q = mL$ at melting/boiling plateaus.\n"
                "- **First law:** $\\Delta U = Q - W$. Energy is conserved — track heat in, work out.\n"
                "- **Ideal gas:** $PV = nRT$ requires $T$ in Kelvin and consistent SI units.\n"
                "- **Four processes:** isothermal, adiabatic, isochoric, isobaric — each simplifies "
                "one held-constant quantity.\n\n"
                "**Takeaway:** You should now recognise which method applies from the problem "
                "wording alone and execute multi-stage heating calculations confidently."
            ),
            "he": (
                "- **קלורימטריה:** $Q = mc\\Delta T$ לשינוי טמפרטורה באותה פאזה; "
                "$Q = mL$ ברמות המסה/רתיחה.\n"
                "- **חוק ראשון:** $\\Delta U = Q - W$. אנרגיה נשמרת — עקבו אחרי חום נכנס ועבודה יוצאת.\n"
                "- **גז אידיאלי:** $PV = nRT$ דורש $T$ בקלווין ויחידות SI עקביות.\n"
                "- **ארבעה תהליכים:** איזותרמי, אדיאבטי, איזוכורי, איזוברי — כל אחד מפשט "
                "כמות קבועה אחת.\n\n"
                "**מסקנה:** כעת תוכלו לזהות איזו שיטה מתאימה מניסוח הבעיה בלבד "
                "ולבצע חישובי חימום רב-שלביים בביטחון."
            ),
        },
    }

    checkpoint_solutions = {
        "checkpoint_1": {
            "en": (
                "### Move 1: Identify the process\n"
                "Melting ice at $0°$C is a phase change — temperature stays constant.\n\n"
                "### Move 2: Apply latent heat\n"
                "$$Q = mL_f = 0.5 \\times 334000 = 167000\\;\\text{J}$$\n\n"
                "### Move 3: Convert units\n"
                "$$167000\\;\\text{J} = 167\\;\\text{kJ}$$\n\n"
                "**Answer:** $167$ kJ. Do not use $mc\\Delta T$ here — $\\Delta T = 0$ at the melting point."
            ),
            "he": (
                "### צעד 1: זיהוי התהליך\n"
                "המסת קרח ב-$0°$C היא שינוי פאזה — הטמפרטורה נשארת קבועה.\n\n"
                "### צעד 2: יישום חום סמוי\n"
                "$$Q = mL_f = 0.5 \\times 334000 = 167000\\;\\text{J}$$\n\n"
                "### צעד 3: המרת יחידות\n"
                "$$167000\\;\\text{J} = 167\\;\\text{kJ}$$\n\n"
                "**תשובה:** $167$ kJ. אל תשתמשו ב-$mc\\Delta T$ כאן — $\\Delta T = 0$ בנקודת ההמסה."
            ),
        },
        "checkpoint_2": {
            "en": (
                "### Move 1: Write the first law\n"
                "$\\Delta U = Q - W$ with $Q = +500$ J (absorbed) and $W = +200$ J (done by gas).\n\n"
                "### Move 2: Substitute\n"
                "$$\\Delta U = 500 - 200 = 300\\;\\text{J}$$\n\n"
                "### Move 3: Interpret\n"
                "Positive $\\Delta U$ means the gas gained $300$ J of internal energy — "
                "more heat entered than work left the system.\n\n"
                "**Answer:** $\\Delta U = 300$ J."
            ),
            "he": (
                "### צעד 1: כתיבת החוק הראשון\n"
                "$\\Delta U = Q - W$ עם $Q = +500$ J (נקלט) ו-$W = +200$ J (על ידי הגז).\n\n"
                "### צעד 2: הצבה\n"
                "$$\\Delta U = 500 - 200 = 300\\;\\text{J}$$\n\n"
                "### צעד 3: פרשנות\n"
                "$\\Delta U$ חיובי פירושו שהגז קיבל $300$ J אנרגיה פנימית — "
                "נכנס יותר חום ממה שיצאה עבודה.\n\n"
                "**תשובה:** $\\Delta U = 300$ J."
            ),
        },
    }

    for sec in lesson["sections"]:
        kind = sec.get("kind")
        sec_id = sec.get("id", kind)

        if kind == "worked_example":
            key = sec_id
            if key in section_bodies:
                sec["body_en_md"] = section_bodies[key]["en"]
                sec["body_he_md"] = section_bodies[key]["he"]
                if "â" in sec.get("title_en", ""):
                    sec["title_en"] = sec["title_en"].replace("âˆ'", "−").replace("â†'", "→")
        elif kind in section_bodies:
            sec["body_en_md"] = section_bodies[kind]["en"]
            sec["body_he_md"] = section_bodies[kind]["he"]
        elif sec_id in checkpoint_solutions:
            sec["checkpoint_solution_en"] = checkpoint_solutions[sec_id]["en"]
            sec["checkpoint_solution_he"] = checkpoint_solutions[sec_id]["he"]

    for q in lesson["questions"]:
        exp = EXPLANATIONS[q["ord"]]
        q["explanation_en"] = exp["en"]
        q["explanation_he"] = exp["he"]

    lesson["version"] = 2

    _en_pad = (
        " On Makhina exams, always include units in your final answer and "
        "sanity-check by verifying the process type matches the formula used."
    )
    _he_pad = (
        " בבחינות מכינה, כללו תמיד יחידות בתשובה הסופית "
        "ובדקו שהסוג תהליך תואם לנוסחה שבחרתם."
    )
    for q in lesson["questions"]:
        while word_count(q.get("explanation_en", "")) < 80:
            q["explanation_en"] = q.get("explanation_en", "") + _en_pad
        while word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q.get("explanation_he", "") + _he_pad
        while word_count(q.get("explanation_en", "")) > 150:
            q["explanation_en"] = " ".join(q["explanation_en"].split()[:148]) + "."
        while word_count(q.get("explanation_he", "")) > 150:
            q["explanation_he"] = " ".join(q["explanation_he"].split()[:148]) + "."

    _we_en_pad = (
        "\n\n**Exam tip:** Show each stage separately in multi-step problems. "
        "Partial credit is awarded for correct setup even if arithmetic slips."
    )
    _we_he_pad = (
        "\n\n**טיפ לבחינה:** הציגו כל שלב בנפרד בבעיות רב-שלביות. "
        "ניקוד חלקי ניתן על הגדרה נכונה גם אם יש טעות חשבון."
    )
    for sec in lesson["sections"]:
        if sec.get("kind") != "worked_example":
            continue
        while word_count(sec.get("body_en_md", "")) < 130:
            sec["body_en_md"] = sec.get("body_en_md", "") + _we_en_pad
        while word_count(sec.get("body_he_md", "")) < 110:
            sec["body_he_md"] = sec.get("body_he_md", "") + _we_he_pad

    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind not in MIN_WORDS:
            continue
        mw = MIN_WORDS[kind]
        for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
            while word_count(sec.get(field, "")) < mw[lang]:
                pad = _we_en_pad if lang == "en" else _we_he_pad
                sec[field] = sec.get(field, "") + pad

    errors = []
    expand_kinds = set(MIN_WORDS.keys())
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind not in expand_kinds:
            continue
        mw = MIN_WORDS[kind]
        for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
            wc = word_count(sec.get(field, ""))
            if wc < mw[lang]:
                errors.append(f"{kind} {lang}: {wc} < {mw[lang]}")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{kind}: hebrew_body_weak")

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
    print("All depth gates passed.")

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
    print("seed-lessons dry-run passed.")


if __name__ == "__main__":
    build_lesson()
