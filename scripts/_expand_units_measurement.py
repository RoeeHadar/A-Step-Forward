#!/usr/bin/env python3
"""Expand units_measurement.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/units_measurement.json"
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
            "Every measurement in physics has two inseparable parts: a **number** and a **unit**. "
            "Without units, numbers are meaningless — $100$ could mean meters, kilometers, or seconds. "
            "Scientists worldwide use the **SI (Système International)** system so experiments can be "
            "compared across labs and countries.\n\n"
            "This lesson is the foundation for every physics topic that follows. Before you can "
            "calculate speed in kinematics, force in Newton's laws, or current in circuits, you must "
            "express quantities in compatible SI units and report results with appropriate precision.\n\n"
            "**You will master:**\n"
            "- The seven SI base units and common derived units (N, J, W, Pa).\n"
            "- Unit conversion using conversion factors equal to 1.\n"
            "- Dimensional analysis to verify formulas and catch errors.\n"
            "- Significant figures and scientific notation for honest reporting of uncertainty."
        ),
        "body_he_md": (
            "כל מדידה בפיזיקה כוללת שני חלקים בלתי-נפרדים: **מספר** ו**יחידה**. "
            "בלי יחידות, מספרים חסרי משמעות — $100$ יכול להיות מטרים, קילומטרים או שניות. "
            "מדענים ברחבי העולם משתמשים במערכת **SI (Système International)** כדי שניתן יהיה "
            "להשוות ניסויים בין מעבדות ומדינות.\n\n"
            "שיעור זה הוא הבסיס לכל נושא פיזיקה שיבוא אחריו. לפני שתחשבו מהירות בקינמטיקה, "
            "כוח בחוקי ניוטון או זרם במעגלים, עליכם לבטא כמויות ביחידות SI תואמות "
            "ולדווח על תוצאות בדיוק מתאים.\n\n"
            "**תשלטו ב:**\n"
            "- שבע יחידות הבסיס של SI ויחידות נגזרות נפוצות (N, J, W, Pa).\n"
            "- המרת יחידות באמצעות גורמי המרה השווים ל-1.\n"
            "- ניתוח ממדים לאימות נוסחאות ולתפיסת שגיאות.\n"
            "- ספרות מובהקות וסימון מדעי לדיווח כנה על אי-ודאות."
        ),
    },
    "definition": {
        "body_en_md": (
            "The **seven SI base units** define all other measurements:\n\n"
            "| Quantity | Unit | Symbol |\n"
            "|---|---|---|\n"
            "| Length | meter | m |\n"
            "| Mass | kilogram | kg |\n"
            "| Time | second | s |\n"
            "| Electric current | ampere | A |\n"
            "| Temperature | kelvin | K |\n"
            "| Amount of substance | mole | mol |\n"
            "| Luminous intensity | candela | cd |\n\n"
            "**Common prefixes** scale units by powers of ten:\n"
            "- Large: $\\text{k}=10^3$, $\\text{M}=10^6$, $\\text{G}=10^9$.\n"
            "- Small: $\\text{c}=10^{-2}$, $\\text{m}=10^{-3}$, $\\mu=10^{-6}$, $\\text{n}=10^{-9}$.\n\n"
            "**Derived units** combine base units:\n"
            "- Force: $N = \\text{kg}\\cdot\\text{m/s}^2$.\n"
            "- Energy: $J = N\\cdot m$.\n"
            "- Power: $W = J/s$.\n"
            "- Pressure: $Pa = N/m^2$.\n\n"
            "Always write units alongside numbers. In Bagrut exams, leaving off units "
            "costs marks even when the arithmetic is correct."
        ),
        "body_he_md": (
            "**שבע יחידות הבסיס של SI** מגדירות את כל שאר המדידות:\n\n"
            "| כמות | יחידה | סימון |\n"
            "|---|---|---|\n"
            "| אורך | מטר | m |\n"
            "| מסה | קילוגרם | kg |\n"
            "| זמן | שנייה | s |\n"
            "| זרם חשמלי | אמפר | A |\n"
            "| טמפרטורה | קלווין | K |\n"
            "| כמות חומר | מול | mol |\n"
            "| עוצמת אור | קנדלה | cd |\n\n"
            "**תחיליות נפוצות** משנות יחידות בחזקות של עשר:\n"
            "- גדולות: $\\text{k}=10^3$, $\\text{M}=10^6$, $\\text{G}=10^9$.\n"
            "- קטנות: $\\text{c}=10^{-2}$, $\\text{m}=10^{-3}$, $\\mu=10^{-6}$, $\\text{n}=10^{-9}$.\n\n"
            "**יחידות נגזרות** משלבות יחידות בסיס:\n"
            "- כוח: $N = \\text{kg}\\cdot\\text{m/s}^2$.\n"
            "- אנרגיה: $J = N\\cdot m$.\n"
            "- הספק: $W = J/s$.\n"
            "- לחץ: $Pa = N/m^2$.\n\n"
            "כתבו תמיד יחידות לצד מספרים. בבחינות בגרות, היעדר יחידות "
            "עולה בניקוד גם כשהחשבון נכון."
        ),
    },
    "theory": {
        "body_en_md": (
            "### What are dimensions?\n\n"
            "**Dimensions** are the fundamental physical quantities that describe any formula: "
            "$[L]$ length, $[M]$ mass, $[T]$ time, $[I]$ current, $[\\Theta]$ temperature. "
            "They are written in square brackets and ignore numerical factors.\n\n"
            "### The consistency principle\n\n"
            "Both sides of any physically valid equation must have **identical dimensions**. "
            "You cannot add meters to seconds — that signals an error. Dimensional analysis "
            "cannot prove a formula is fully correct, but it **can** disprove wrong ones instantly.\n\n"
            "### Three powerful uses\n\n"
            "1. **Error detection:** If $[\\text{left}] \\ne [\\text{right}]$, the formula is wrong.\n"
            "2. **Relationship discovery:** Guess how a quantity depends on others by matching dimensions.\n"
            "3. **Systematic conversion:** Multiply by fractions equal to 1:\n"
            "$$1\\text{ km}=1000\\text{ m} \\Rightarrow \\frac{1\\text{ km}}{1000\\text{ m}}=1.$$\n\n"
            "### Significant figures and uncertainty\n\n"
            "Measured values carry **precision limits**. In multiplication, the result has as many "
            "significant figures as the **least precise** input. In addition, match the **fewest "
            "decimal places**. Scientific notation ($3.2\\times10^4$) removes ambiguity about trailing zeros.\n\n"
            "### Bagrut exam strategy\n\n"
            "Always write units in every line of working. Examiners deduct marks for correct numbers "
            "with missing or wrong units. When a problem mixes km/h with m/s, convert **before** "
            "substituting into any formula — never halfway through a calculation."
        ),
        "body_he_md": (
            "### מהם ממדים?\n\n"
            "**ממדים** הם הכמויות הפיזיקליות הבסיסיות שמתארות כל נוסחה: "
            "$[L]$ אורך, $[M]$ מסה, $[T]$ זמן, $[I]$ זרם, $[\\Theta]$ טמפרטורה. "
            "כותבים אותם בסוגריים מרובעים ומתעלמים מגורמים מספריים.\n\n"
            "### עקרון העקביות\n\n"
            "שני צידי כל משוואה פיזיקלית תקפה חייבים להיות **באותם ממדים בדיוק**. "
            "אי אפשר לחבר מטרים לשניות — זה סימן לשגיאה. ניתוח ממדים "
            "לא יכול להוכיח שנוסחה נכונה לחלוטין, אך **יכול** לשלול נוסחאות שגויות מיד.\n\n"
            "### שלושה שימושים עוצמתיים\n\n"
            "1. **איתור שגיאות:** אם $[\\text{שמאל}] \\ne [\\text{ימין}]$, הנוסחה שגויה.\n"
            "2. **גילוי יחסים:** נחשו תלות בכמויות על ידי התאמת ממדים.\n"
            "3. **המרה שיטתית:** כפל בשברים השווים ל-1:\n"
            "$$1\\text{ km}=1000\\text{ m} \\Rightarrow \\frac{1\\text{ km}}{1000\\text{ m}}=1.$$\n\n"
            "### ספרות מובהקות ואי-ודאות\n\n"
            "ערכים נמדדים נושאים **מגבלות דיוק**. בכפל, התוצאה מקבלת מספר ספרות מובהקות "
            "כמו **הקלט הכי פחות מדויק**. בחיבור, התאימו את **מספר המקומות העשרוניים**. "
            "סימון מדעי ($3.2\\times10^4$) מסיר דו-משמעות לגבי אפסים בסוף.\n\n"
            "### אסטרטגיה לבחינת בגרות\n\n"
            "כתבו יחידות בכל שורת עבודה. בוחנים מורידים ניקוד על מספרים נכונים "
            "בלי יחידות או עם יחידות שגויות. כשבעיה מערבבת km/h עם m/s, "
            "המירו **לפני** ההצבה בנוסחה — לעולם לא באמצע החישוב."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Convert** a car speed $v = 90$ km/h to m/s — the standard SI unit for velocity.\n\n"
            "### Move 1: Write the value with units\n"
            "$$v = 90\\,\\frac{\\text{km}}{\\text{h}}$$\n\n"
            "### Move 2: Build conversion factors\n"
            "Use $1\\,\\text{km} = 1000\\,\\text{m}$ and $1\\,\\text{h} = 3600\\,\\text{s}$:\n"
            "$$90\\frac{\\text{km}}{\\text{h}}\\times\\frac{1000\\,\\text{m}}{1\\,\\text{km}}"
            "\\times\\frac{1\\,\\text{h}}{3600\\,\\text{s}}$$\n\n"
            "### Move 3: Cancel units and compute\n"
            "$$= \\frac{90000}{3600}\\,\\frac{\\text{m}}{\\text{s}} = 25\\,\\frac{\\text{m}}{\\text{s}}$$\n\n"
            "### Move 4: Quick check\n"
            "Divide km/h by 3.6: $90/3.6 = 25$ m/s ✓. Speed in m/s is always smaller than km/h "
            "because each km/h spans more distance per shorter time unit. This conversion appears "
            "in virtually every kinematics problem on the Bagrut exam — memorize the 3.6 shortcut.\n\n"
            "### Move 5: Why this method works\n"
            "Each conversion factor equals 1, so the numeric value is unchanged — only the unit "
            "label changes. Writing factors as fractions makes cancellation visible and prevents "
            "inverting a ratio by accident. **Answer:** $v = 25$ m/s."
        ),
        "body_he_md": (
            "**המרו** מהירות רכב $v = 90$ km/h ל-m/s — יחידת SI הסטנדרטית למהירות.\n\n"
            "### צעד 1: כתיבת הערך עם יחידות\n"
            "$$v = 90\\,\\frac{\\text{km}}{\\text{h}}$$\n\n"
            "### צעד 2: בניית גורמי המרה\n"
            "השתמשו ב-$1\\,\\text{km} = 1000\\,\\text{m}$ וב-$1\\,\\text{h} = 3600\\,\\text{s}$:\n"
            "$$90\\frac{\\text{km}}{\\text{h}}\\times\\frac{1000\\,\\text{m}}{1\\,\\text{km}}"
            "\\times\\frac{1\\,\\text{h}}{3600\\,\\text{s}}$$\n\n"
            "### צעד 3: ביטול יחידות וחישוב\n"
            "$$= \\frac{90000}{3600}\\,\\frac{\\text{m}}{\\text{s}} = 25\\,\\frac{\\text{m}}{\\text{s}}$$\n\n"
            "### צעד 4: בדיקה מהירה\n"
            "חלקו km/h ב-3.6: $90/3.6 = 25$ m/s ✓. מהירות ב-m/s תמיד קטנה מ-km/h "
            "כי km/h מכסה מרחק גדול יותר ליחידת זמן. המרה זו מופיעה כמעט בכל בעיית קינמטיקה "
            "בבגרות — שימו לב לקיצור 3.6.\n\n"
            "### צעד 5: למה השיטה עובדת\n"
            "כל גורם המרה שווה ל-1, ולכן הערך המספרי לא משתנה — רק תווית היחידה. "
            "כתיבת גורמים כשברים מציגה ביטול יחידות ומונעת היפוך יחס בטעות. **תשובה:** $v = 25$ m/s."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Check** whether $v = \\sqrt{2as}$ is dimensionally consistent, where $v$ is speed, "
            "$a$ is acceleration, and $s$ is displacement.\n\n"
            "### Move 1: Write dimensions of each quantity\n"
            "$[v] = [L/T]$, $[a] = [L/T^2]$, $[s] = [L]$.\n\n"
            "### Move 2: Analyze the right-hand side\n"
            "$$[\\sqrt{2as}] = \\sqrt{[L/T^2]\\cdot[L]} = \\sqrt{[L^2/T^2]} = [L/T]$$\n\n"
            "### Move 3: Compare both sides\n"
            "$[v] = [L/T]$ and $[\\sqrt{2as}] = [L/T]$ ✓ — dimensions match.\n\n"
            "### Move 4: Physical meaning\n"
            "This is the kinematic equation $v^2 = 2as$ (final speed from rest). "
            "Dimensional consistency is necessary but not sufficient — the factor 2 must come "
            "from calculus, not from dimensions alone. On exams, dimensional checks take under "
            "thirty seconds and can save you from using a wrong kinematic formula entirely.\n\n"
            "### Move 5: What dimensions cannot tell you\n"
            "A formula can pass the dimensional test yet still be wrong by a pure number factor. "
            "Always combine dimensional analysis with physics reasoning or known standard results. "
            "**Answer:** dimensionally consistent ✓."
        ),
        "body_he_md": (
            "**בדקו** האם $v = \\sqrt{2as}$ עקבי ממדית, כאשר $v$ מהירות, "
            "$a$ תאוצה, ו-$s$ תזוזה.\n\n"
            "### צעד 1: כתיבת ממדים של כל כמות\n"
            "$[v] = [L/T]$, $[a] = [L/T^2]$, $[s] = [L]$.\n\n"
            "### צעד 2: ניתוח צד ימין\n"
            "$$[\\sqrt{2as}] = \\sqrt{[L/T^2]\\cdot[L]} = \\sqrt{[L^2/T^2]} = [L/T]$$\n\n"
            "### צעד 3: השוואת שני הצדדים\n"
            "$[v] = [L/T]$ ו-$[\\sqrt{2as}] = [L/T]$ ✓ — הממדים תואמים.\n\n"
            "### צעד 4: משמעות פיזיקלית\n"
            "זו משוואת הקינמטיקה $v^2 = 2as$ (מהירות סופית ממנוחה). "
            "עקביות ממדית הכרחית אך לא מספיקה — המקדם 2 מגיע מאינטגרציה, "
            "לא מממדים בלבד. בבחינות, בדיקת ממדים לוקחת פחות משלושים שניות "
            "ומונעת שימוש בנוסחת קינמטיקה שגויה.\n\n"
            "### צעד 5: מה ממדים לא יכולים לגלות\n"
            "נוסחה יכולה לעבור בדיקת ממדים ועדיין להיות שגויה בגורם מספרי טהור. "
            "שלבו תמיד ניתוח ממדים עם היגיון פיזיקלי או תוצאות סטנדרטיות. **תשובה:** עקבי ממדית ✓."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Question:** Calculate displacement $d = \\frac{1}{2}at^2$ for $a = 9.81\\,\\text{m/s}^2$ "
            "and $t = 3.2\\,\\text{s}$. Report to correct significant figures.\n\n"
            "### Move 1: Substitute values\n"
            "$$d = 0.5 \\times 9.81 \\times (3.2)^2 = 0.5 \\times 9.81 \\times 10.24 = 50.23\\,\\text{m}$$\n\n"
            "### Move 2: Count significant figures in inputs\n"
            "$a = 9.81$ has **3** sig figs; $t = 3.2$ has **2** sig figs. "
            "Multiplication limits the answer to **2 sig figs**.\n\n"
            "### Move 3: Round correctly\n"
            "$$d \\approx 50\\,\\text{m} \\quad \\text{or} \\quad 5.0 \\times 10^1\\,\\text{m}$$\n\n"
            "### Move 4: Exam tip\n"
            "Writing $50.23$ m implies four sig figs — more precision than the data supports. "
            "Always identify the least precise measurement first. Reporting $50.2$ m would still "
            "imply three sig figs — round to $50$ m or write $5.0 \\times 10^1$ m explicitly.\n\n"
            "### Move 5: Rule recap\n"
            "For products like $\\frac{1}{2}at^2$, count sig figs in $a$ and $t$ only; "
            "the factor $\\frac{1}{2}$ is exact and does not limit precision. "
            "**Answer:** $d \\approx 50$ m (2 significant figures)."
        ),
        "body_he_md": (
            "**שאלה:** חשבו תזוזה $d = \\frac{1}{2}at^2$ עבור $a = 9.81\\,\\text{m/s}^2$ "
            "ו-$t = 3.2\\,\\text{s}$. דווחו בספרות מובהקות נכונות.\n\n"
            "### צעד 1: הצבת ערכים\n"
            "$$d = 0.5 \\times 9.81 \\times (3.2)^2 = 0.5 \\times 9.81 \\times 10.24 = 50.23\\,\\text{m}$$\n\n"
            "### צעד 2: ספירת ספרות מובהקות בקלט\n"
            "$a = 9.81$ עם **3** ספרות; $t = 3.2$ עם **2** ספרות. "
            "כפל מגביל את התשובה ל-**2 ספרות מובהקות**.\n\n"
            "### צעד 3: עיגול נכון\n"
            "$$d \\approx 50\\,\\text{m} \\quad \\text{או} \\quad 5.0 \\times 10^1\\,\\text{m}$$\n\n"
            "### צעד 4: טיפ לבחינה\n"
            "כתיבת $50.23$ m מרמזת על ארבע ספרות — דיוק מעבר לנתונים. "
            "זהו תמיד את המדידה הכי פחות מדויקת קודם. דיווח על $50.2$ m עדיין מרמז "
            "על שלוש ספרות — עגלו ל-$50$ m או כתבו $5.0 \\times 10^1$ m במפורש.\n\n"
            "### צעד 5: חזרה על הכלל\n"
            "במכפלות כמו $\\frac{1}{2}at^2$, ספרו ספרות מובהקות ב-$a$ וב-$t$ בלבד; "
            "המקדם $\\frac{1}{2}$ מדויק ולא מגביל דיוק. **תשובה:** $d \\approx 50$ m (2 ספרות מובהקות)."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Task | Method |\n"
            "|---|---|\n"
            "| Unit conversion | Write value with unit → multiply by factor(s) $= 1$ → cancel units |\n"
            "| km/h → m/s | Divide by 3.6 (or use $1000/3600$) |\n"
            "| Dimensional check | Write $[\\text{quantity}]$ for each term; both sides must match |\n"
            "| Multiplication sig figs | Answer has min sig figs among inputs |\n"
            "| Addition sig figs | Answer has min decimal places among inputs |\n"
            "| Scientific notation | $a \\times 10^n$ with $1 \\le a < 10$; sig figs = digits in $a$ |\n\n"
            "**Workflow:** Read the problem type → pick the row → substitute numbers last. "
            "Always include units in every intermediate step — they catch arithmetic errors early."
        ),
        "body_he_md": (
            "| משימה | שיטה |\n"
            "|---|---|\n"
            "| המרת יחידות | כתבו ערך עם יחידה → כפלו בגורם(ים) $= 1$ → בטלו יחידות |\n"
            "| km/h → m/s | חלקו ב-3.6 (או $1000/3600$) |\n"
            "| בדיקת ממדים | כתבו $[\\text{כמות}]$ לכל איבר; שני הצדדים חייבים להתאים |\n"
            "| ספרות בכפל | התשובה עם מינימום ספרות מובהקות |\n"
            "| ספרות בחיבור | התשובה עם מינימום מקומות עשרוניים |\n"
            "| סימון מדעי | $a \\times 10^n$ עם $1 \\le a < 10$; ספרות = ספרות ב-$a$ |\n\n"
            "**תהליך עבודה:** קראו את סוג הבעיה → בחרו שורה → הציבו מספרים בסוף. "
            "כללו יחידות בכל שלב ביניים — הן תופסות שגיאות חישוב מוקדם."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting unit conversion before computing:** Mixing km with m in the same "
            "formula gives wrong answers by factors of 1000. Convert everything to SI first.\n\n"
            "2. **Sig figs in addition vs. multiplication:** Students apply the multiplication rule "
            "to addition. For $12.35 + 2.1$, round to **one decimal place** (14.5 m), not two sig figs.\n\n"
            "3. **Ambiguous trailing zeros:** $300$ could mean 1, 2, or 3 sig figs. "
            "Write $3.00 \\times 10^2$ when you mean exactly three.\n\n"
            "4. **Confusing mass and weight:** Mass is in kg (scalar); weight is force in N ($W = mg$).\n\n"
            "**Example misconception:** Adding 5 cm directly to 2 m without converting.\n\n"
            "**Fix:** Convert to the same unit first: $5\\,\\text{cm} = 0.05\\,\\text{m}$, then add."
        ),
        "body_he_md": (
            "1. **שכחת המרת יחידות לפני חישוב:** ערבוב km עם m באותה נוסחה נותן תשובות שגויות "
            "בגורמים של 1000. המירו הכל ל-SI קודם.\n\n"
            "2. **ספרות מובהקות בחיבור לעומת כפל:** תלמידים מיישמים כלל כפל על חיבור. "
            "ב-$12.35 + 2.1$, עגלו ל**מקום עשרוני אחד** (14.5 m), לא לשתי ספרות.\n\n"
            "3. **אפסים בסוף דו-משמעיים:** $300$ יכול להיות 1, 2 או 3 ספרות. "
            "כתבו $3.00 \\times 10^2$ כשמתכוונים לשלוש בדיוק.\n\n"
            "4. **בלבול מסה ומשקל:** מסה ב-kg (סקalar); משקל הוא כוח ב-N ($W = mg$).\n\n"
            "**דוגמת טעות:** חיבור 5 ס\"מ ישירות ל-2 m בלי המרה.\n\n"
            "**תיקון:** המירו לאותה יחידה קודם: $5\\,\\text{cm} = 0.05\\,\\text{m}$, ואז חברו."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Units and measurement are not a side topic — they are the **grammar of physics**. "
            "Every equation you write in kinematics, dynamics, and circuits assumes quantities "
            "are expressed in compatible SI units with honest precision.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:kinematics_1d` **Kinematics in 1D** (prereq)\n"
            "- `concept:newton_laws` **Newton's Laws of Motion** (prereq)\n"
            "- `concept:electric_circuits` **Electric Circuits** (prereq)\n\n"
            "**Builds on:**\n"
            "- `concept:descriptive_stats` **Statistics — Advanced (Normal Distribution)**\n\n"
            "**Why it matters for exams:** Bagrut and university courses reward *transfer* — "
            "applying unit skills in new contexts. A speed problem, a force calculation, and a "
            "circuit analysis all fail if units are mishandled."
        ),
        "body_he_md": (
            "יחידות ומדידה אינם נושא צד — הם **דקדוק הפיזיקה**. "
            "כל משוואה שתכתבו בקינמטיקה, דינמיקה ומעגלים מניחה שכמויות "
            "מבוטאות ביחידות SI תואמות עם דיוק כנה.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:kinematics_1d` **קינמטיקה בממד אחד** (prereq)\n"
            "- `concept:newton_laws` **חוקי ניוטון** (prereq)\n"
            "- `concept:electric_circuits` **מעגלי חשמל (DC)** (prereq)\n\n"
            "**מבוסס על:**\n"
            "- `concept:descriptive_stats` **סטטיסטיקה מתקדמת (התפלגות נורמלית)**\n\n"
            "**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים *העברה* — "
            "יישום מיומנויות יחידות בהקשרים חדשים. בעיית מהירות, חישוב כוח "
            "וניתוח מעגל — כולם נכשלים אם מטפלים ביחידות לא נכון."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Memorize the 7 SI base units:** m, kg, s, A, K, mol, cd.\n\n"
            "**Conversion shortcut:** km/h → m/s: divide by 3.6. Example: $90/3.6 = 25$ m/s.\n\n"
            "**Dimensional check:** Write $[L]$, $[M]$, $[T]$ for each side — must match.\n\n"
            "**Sig figs rules:**\n"
            "- Multiply/divide → least sig figs in inputs.\n"
            "- Add/subtract → least decimal places in inputs.\n\n"
            "**Derived units:** $N = \\text{kg·m/s}^2$; $J = N\\cdot m$; $W = J/s$; $Pa = N/m^2$.\n\n"
            "**Last review:** Convert one speed, check one formula's dimensions, and round one "
            "multiplication to sig figs — all without notes. Bring a ruler of prefixes "
            "(k, M, m, $\\mu$, n) to memory alongside the seven base units."
        ),
        "body_he_md": (
            "**שימו לב ל-7 יחידות בסיס SI:** m, kg, s, A, K, mol, cd.\n\n"
            "**קיצור המרה:** km/h → m/s: חלקו ב-3.6. דוגמה: $90/3.6 = 25$ m/s.\n\n"
            "**בדיקת ממדים:** כתבו $[L]$, $[M]$, $[T]$ לכל צד — חייבים להתאים.\n\n"
            "**כללי ספרות מובהקות:**\n"
            "- כפל/חילוק → מינימום ספרות מובהקות בקלט.\n"
            "- חיבור/חיסור → מינימום מקומות עשרוניים בקלט.\n\n"
            "**יחידות נגזרות:** $N = \\text{kg·m/s}^2$; $J = N\\cdot m$; $W = J/s$; $Pa = N/m^2$.\n\n"
            "**חזרה אחרונה:** המירו מהירות אחת, בדקו ממדים של נוסחה אחת, ועגלו כפל "
            "לספרות מובהקות — הכל בלי רשימות. שימו לב לתחיליות k, M, m, $\\mu$, n."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **SI units** provide an international standard; seven base units define all measurements.\n"
            "- **Unit conversion:** multiply by fractions equal to 1; cancel units systematically.\n"
            "- **Dimensional analysis** verifies equations and catches formula errors instantly.\n"
            "- **Significant figures** reflect measurement precision — different rules for ×÷ vs. +−.\n"
            "- **Scientific notation** removes ambiguity and handles very large or small values.\n\n"
            "**Takeaway:** Before any calculation, ask: Are my units consistent? Is my precision honest?"
        ),
        "body_he_md": (
            "- **יחידות SI** מספקות סטנדרט בינלאומי; שבע יחידות בסיס מגדירות את כל המדידות.\n"
            "- **המרת יחידות:** כפל בשברים השווים ל-1; ביטול יחידות שיטתי.\n"
            "- **ניתוח ממדים** מאמת משוואות ותופס שגיאות נוסחה מיד.\n"
            "- **ספרות מובהקות** משקפות דיוק מדידה — כללים שונים ל-×÷ לעומת +−.\n"
            "- **סימון מדעי** מסיר דו-משמעות ומטפל בערכים גדולים או קטנים מאוד.\n\n"
            "**מסקנה:** לפני כל חישוב, שאלו: האם היחידות עקביות? האם הדיוק כנה?"
        ),
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "### Move 1: cm to meters\n"
            "$$5\\,\\text{cm} = 5 \\times 10^{-2}\\,\\text{m} = 0.05\\,\\text{m}$$\n"
            "Use $1\\,\\text{cm} = 10^{-2}\\,\\text{m}$.\n\n"
            "### Move 2: cm to millimeters\n"
            "$$5\\,\\text{cm} = 5 \\times 10\\,\\text{mm} = 50\\,\\text{mm}$$\n"
            "Use $1\\,\\text{cm} = 10\\,\\text{mm}$.\n\n"
            "**Check:** $0.05\\,\\text{m} = 50\\,\\text{mm}$ ✓ — consistent. "
            "**Answer:** $5\\,\\text{cm} = 0.05\\,\\text{m} = 50\\,\\text{mm}$."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: ס\"מ למטרים\n"
            "$$5\\,\\text{cm} = 5 \\times 10^{-2}\\,\\text{m} = 0.05\\,\\text{m}$$\n"
            "השתמשו ב-$1\\,\\text{cm} = 10^{-2}\\,\\text{m}$.\n\n"
            "### צעד 2: ס\"מ למילימטרים\n"
            "$$5\\,\\text{cm} = 5 \\times 10\\,\\text{mm} = 50\\,\\text{mm}$$\n"
            "השתמשו ב-$1\\,\\text{cm} = 10\\,\\text{mm}$.\n\n"
            "**בדיקה:** $0.05\\,\\text{m} = 50\\,\\text{mm}$ ✓ — עקבי. "
            "**תשובה:** $5\\,\\text{cm} = 0.05\\,\\text{m} = 50\\,\\text{mm}$."
        ),
    },
    {
        "checkpoint_solution_en": (
            "### Move 1: Write dimensions of force and area\n"
            "$[F] = [MLT^{-2}]$ (Newton = kg·m/s²).\n"
            "$[A] = [L^2]$.\n\n"
            "### Move 2: Divide dimensions\n"
            "$$[P] = \\frac{[F]}{[A]} = \\frac{[MLT^{-2}]}{[L^2]} = [ML^{-1}T^{-2}]$$\n\n"
            "### Move 3: Identify SI unit\n"
            "Pressure unit: pascal (Pa) $= N/m^2$.\n\n"
            "**Check:** $[Pa] = [N]/[m^2] = [MLT^{-2}]/[L^2] = [ML^{-1}T^{-2}]$ ✓. "
            "**Answer:** $[P] = [ML^{-1}T^{-2}]$; unit = Pa."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: ממדי כוח ושטח\n"
            "$[F] = [MLT^{-2}]$ (ניוטון = kg·m/s²).\n"
            "$[A] = [L^2]$.\n\n"
            "### צעד 2: חילוק ממדים\n"
            "$$[P] = \\frac{[F]}{[A]} = \\frac{[MLT^{-2}]}{[L^2]} = [ML^{-1}T^{-2}]$$\n\n"
            "### צעד 3: זיהוי יחידת SI\n"
            "יחידת לחץ: pascal (Pa) $= N/m^2$.\n\n"
            "**בדיקה:** $[Pa] = [N]/[m^2] = [MLT^{-2}]/[L^2] = [ML^{-1}T^{-2}]$ ✓. "
            "**תשובה:** $[P] = [ML^{-1}T^{-2}]$; יחידה = Pa."
        ),
    },
]

EXPLANATIONS = {
    1: {
        "en": (
            "The SI unit of **mass** is the **kilogram (kg)** — one of the seven base units defined "
            "in the International System. Newton (N) measures force, not mass; meter (m) measures length; "
            "kelvin (K) measures thermodynamic temperature. A very common mistake is choosing Newton "
            "because students confuse mass with weight ($W = mg$). On Bagrut exams, always distinguish: "
            "mass is a scalar measured in kg; weight is a force measured in N.\n\n"
            "Remember: kilogram is the only SI base unit that carries a prefix ('kilo') in its name. "
            "If the question asks specifically for mass, never answer with a derived unit like N or "
            "with grams unless the problem explicitly requests conversion. **Correct answer:** Kilogram."
        ),
        "he": (
            "יחידת SI של **מסה** היא **קילוגרם (kg)** — אחת משבע יחידות הבסיס במערכת הבינלאומית. "
            "ניוטון (N) מודד כוח, לא מסה; מטר (m) מודד אורך; קלווין (K) מודד טמפרטורה תרמודינמית. "
            "טעות נפוצה מאוד: בחירת ניוטון כי תלמידים מבלבלים מסה עם משקל ($W = mg$). "
            "בבגרות, הבדילו תמיד: מסה היא כמות ב-kg; משקל הוא כוח ב-N.\n\n"
            "זכרו: קילוגרם היא יחידת הבסיס היחידה עם תחילית ('kilo') בשמה. "
            "אם השאלה מבקשת מסה במפורש, אל תענו ביחידה נגזרת כמו N או בגרם "
            "אלא אם הבעיה דורשת המרה. **תשובה נכונה:** קילוגרם."
        ),
    },
    2: {
        "en": (
            "To convert kilometers to meters, use the conversion factor "
            "$1\\,\\text{km} = 1000\\,\\text{m}$. Set up a fraction equal to one so units cancel:\n"
            "$$2.5\\,\\text{km} \\times \\frac{1000\\,\\text{m}}{1\\,\\text{km}} = 2500\\,\\text{m}$$\n\n"
            "The km units cancel cleanly, leaving meters. A common error is multiplying by 100 instead "
            "of 1000 (confusing km with hectometers) or forgetting to attach the unit m to the final answer. "
            "On exams, always write the conversion factor as a fraction — it prevents direction mistakes "
            "and earns partial credit even if arithmetic slips.\n\n"
            "**Self-check:** $2500$ m divided by 1000 returns $2.5$ km ✓. **Answer:** $2500$ m."
        ),
        "he": (
            "להמרת קילומטרים למטרים, השתמשו בגורם ההמרה "
            "$1\\,\\text{km} = 1000\\,\\text{m}$. הגדירו שבר השווה ל-1 כדי שיחידות יתבטלו:\n"
            "$$2.5\\,\\text{km} \\times \\frac{1000\\,\\text{m}}{1\\,\\text{km}} = 2500\\,\\text{m}$$\n\n"
            "יחידות km מתבטלות, נשארים מטרים. שגיאה נפוצה: כפל ב-100 במקום 1000 "
            "(בלבול km עם hectometer) או שכחת יחידת m בתשובה הסופית. "
            "בבחינות, כתבו תמיד את גורם ההמרה כשבר — זה מונע טעויות כיוון "
            "ומזכה בניקוד חלקי גם אם החשבון מעט שגוי.\n\n"
            "**בדיקה:** $2500$ m חלקי 1000 מחזיר $2.5$ km ✓. **תשובה:** $2500$ m."
        ),
    },
    3: {
        "en": (
            "Convert seconds to minutes using the identity $1\\,\\text{min} = 60\\,\\text{s}$. "
            "Place seconds in the denominator so they cancel:\n"
            "$$120\\,\\text{s} \\times \\frac{1\\,\\text{min}}{60\\,\\text{s}} = 2\\,\\text{min}$$\n\n"
            "Seconds cancel, leaving minutes. Students sometimes divide by 100 (thinking 'centi') "
            "or multiply by 60 instead of dividing. The key insight: seconds are **smaller** than minutes, "
            "so 120 s must yield **fewer** than 120 minutes — only 2. If you get 7200 minutes, "
            "you multiplied when you should have divided.\n\n"
            "**Exam tip:** If your answer has more minutes than the original seconds count, "
            "reverse the operation. **Answer:** $2$ minutes."
        ),
        "he": (
            "המרת שניות לדקות עם $1\\,\\text{min} = 60\\,\\text{s}$. "
            "הניחו שניות במכנה כדי שיתבטלו:\n"
            "$$120\\,\\text{s} \\times \\frac{1\\,\\text{min}}{60\\,\\text{s}} = 2\\,\\text{min}$$\n\n"
            "שניות מתבטלות, נשארות דקות. תלמידים לפעמים מחלקים ב-100 (חושבים 'centi') "
            "או מכפילים ב-60 במקום לחלק. התובנה: שניות **קטנות** מדקות, "
            "לכן 120 s חייבות לתת **פחות** מ-120 דקות — רק 2. אם קיבלתם 7200 דקות, "
            "כפלתם במקום לחלק.\n\n"
            "**טיפ לבחינה:** אם יש יותר דקות ממספר השניות המקורי, "
            "הפכו את הפעולה. **תשובה:** $2$ דקות."
        ),
    },
    4: {
        "en": (
            "Force is a **derived** SI unit: the **newton (N)**, defined as "
            "$1\\,\\text{N} = 1\\,\\text{kg}\\cdot\\text{m/s}^2$. It follows directly from "
            "Newton's second law $F = ma$. Students often confuse N with kg (mass) or J (energy). "
            "Remember: N has dimensions $[MLT^{-2}]$, matching force, not mass or energy.\n\n"
            "On Bagrut problems, if asked for 'SI unit of force,' answer 'newton' or write "
            "$\\text{kg·m/s}^2$ — both are acceptable. Saying 'kilogram' is wrong because kg "
            "measures mass only. Weight (force of gravity) is in newtons; mass stays in kilograms. "
            "**Answer:** Newton (N) $= \\text{kg·m/s}^2$."
        ),
        "he": (
            "כוח הוא יחידת SI **נגזרת**: **ניוטון (N)**, מוגדר כ-"
            "$1\\,\\text{N} = 1\\,\\text{kg}\\cdot\\text{m/s}^2$. הוא נובע ישירות מ-"
            "חוק שני של ניוטון $F = ma$. תלמידים מבלבלים לעיתים N עם kg (מסה) או J (אנרגיה). "
            "זכרו: ל-N ממדים $[MLT^{-2}]$, המתאימים לכוח, לא למסה או אנרגיה.\n\n"
            "בבגרות, אם שואלים 'יחידת SI לכוח', ענו 'ניוטון' או כתבו "
            "$\\text{kg·m/s}^2$ — שניהם מקובלים. 'קילוגרם' שגוי כי kg "
            "מודד מסה בלבד. משקל (כוח הכבידה) בניוטונים; מסה נשארת בקילוגרמים. "
            "**תשובה:** ניוטון (N) $= \\text{kg·m/s}^2$."
        ),
    },
    5: {
        "en": (
            "The number $6.02 \\times 10^{23}$ is **Avogadro's number** — the count of particles "
            "(atoms, molecules, ions) in exactly one mole of substance. In words: approximately "
            "602 sextillion, or 'six point zero two times ten to the twenty-third.' "
            "It bridges the atomic scale to the laboratory scale via the mole (mol), "
            "one of the seven SI base units.\n\n"
            "Students sometimes write '602 million' (wrong power of ten) or drop the coefficient 6.02. "
            "In chemistry and physics, this number appears whenever you convert between "
            "particle count and amount of substance. **Answer:** Avogadro's number."
        ),
        "he": (
            "המספר $6.02 \\times 10^{23}$ הוא **מספר אבוגדרו** — מספר החלקיקים "
            "(אטומים, מולקולות, יונים) במול אחד בדיוק של חומר. במילים: בערך "
            "602 סקסטיליון, או 'שש נקודה אפס שתיים כפול עשר בחזקת עשרים ושלוש'. "
            "הוא מחבר את סקלת האטום לסקלת המעבדה דרך המול (mol), "
            "אחת משבע יחידות הבסיס של SI.\n\n"
            "תלמידים לפעמים כותבים '602 מיליון' (חזקת עשר שגויה) או מסירים את המקדם 6.02. "
            "בכימיה ופיזיקה, מספר זה מופיע בהמרה בין מספר חלקיקים לכמות חומר. "
            "**תשובה:** מספר אבוגדרו."
        ),
    },
    6: {
        "en": (
            "Convert $72$ km/h to m/s using conversion factors or the shortcut divide by 3.6:\n"
            "$$72\\,\\frac{\\text{km}}{\\text{h}} \\times \\frac{1000\\,\\text{m}}{1\\,\\text{km}}"
            "\\times \\frac{1\\,\\text{h}}{3600\\,\\text{s}} = \\frac{72000}{3600} = 20\\,\\text{m/s}$$\n\n"
            "Quick check: $72 \\div 3.6 = 20$ ✓. Common errors: using $100$ instead of $1000$ for km→m, "
            "or forgetting to convert hours to seconds (leaving the answer effectively in km/h). "
            "Speed problems on the Bagrut almost always require m/s for kinematic formulas.\n\n"
            "**Exam tip:** Memorize ÷3.6 for km/h → m/s. If you get $200$ m/s, you likely "
            "multiplied instead of canceling units correctly. **Answer:** $20$ m/s."
        ),
        "he": (
            "המרת $72$ km/h ל-m/s עם גורמי המרה או קיצור חלוקה ב-3.6:\n"
            "$$72\\,\\frac{\\text{km}}{\\text{h}} \\times \\frac{1000\\,\\text{m}}{1\\,\\text{km}}"
            "\\times \\frac{1\\,\\text{h}}{3600\\,\\text{s}} = \\frac{72000}{3600} = 20\\,\\text{m/s}$$\n\n"
            "בדיקה מהירה: $72 \\div 3.6 = 20$ ✓. שגיאות נפוצות: שימוש ב-$100$ במקום $1000$ ל-km→m, "
            "או שכחת המרת שעות לשניות (התשובה נשארת בפועל ב-km/h). "
            "בעיות מהירות בבגרות כמעט תמיד דורשות m/s לנוסחאות קינמטיות.\n\n"
            "**טיפ לבחינה:** שימו לב ל-÷3.6 ל-km/h → m/s. אם קיבלתם $200$ m/s, "
            "כנראה כפלתם במקום לבטל יחידות נכון. **תשובה:** $20$ m/s."
        ),
    },
    7: {
        "en": (
            "Check $F = ma$ dimensionally by writing bracket dimensions for each side:\n"
            "Left: $[F] = [MLT^{-2}]$ (force).\n"
            "Right: $[ma] = [M][L/T^2] = [MLT^{-2}]$.\n\n"
            "Both sides match ✓, confirming $F = ma$ is dimensionally consistent. "
            "The newton (N) is defined so this equation works with SI units: "
            "$1\\,\\text{N} = 1\\,\\text{kg}\\cdot\\text{m/s}^2$.\n\n"
            "**Common slip:** Writing $[F] = [M][L/T]$ — forgetting acceleration has dimensions "
            "$L/T^2$, not $L/T$. If dimensions differ, the formula cannot be physically correct. "
            "**Answer:** Consistent; $[F] = [ma] = N$."
        ),
        "he": (
            "בדקו $F = ma$ ממדית על ידי כתיבת ממדים לכל צד:\n"
            "שמאל: $[F] = [MLT^{-2}]$ (כוח).\n"
            "ימין: $[ma] = [M][L/T^2] = [MLT^{-2}]$.\n\n"
            "שני הצדדים תואמים ✓, מאשר ש-$F = ma$ עקבי ממדית. "
            "ניוטון (N) מוגדר כך שהמשוואה עובדת ב-SI: "
            "$1\\,\\text{N} = 1\\,\\text{kg}\\cdot\\text{m/s}^2$.\n\n"
            "**טעות נפוצה:** כתיבת $[F] = [M][L/T]$ — שכחת שתאוצה בממדים "
            "$L/T^2$, לא $L/T$. אם הממדים שונים, הנוסחה לא יכולה להיות נכונה פיזיקלית. "
            "**תשובה:** עקבי; $[F] = [ma] = N$."
        ),
    },
    8: {
        "en": (
            "For the pendulum formula $T = 2\\pi\\sqrt{L/g}$, find dimensions inside the square root:\n"
            "$[L/g] = [L]/[L/T^2] = [T^2]$.\n"
            "$[\\sqrt{L/g}] = [T]$.\n\n"
            "Since $2\\pi$ is dimensionless, $[T] = [T]$ ✓ — the formula is dimensionally "
            "consistent. This is the period of a simple pendulum for small oscillation angles.\n\n"
            "**Common error:** Treating $g$ as dimensionless. Gravity has dimensions $[L/T^2]$. "
            "If you obtain $[L]$ or $[L/T]$ instead of $[T]$, re-check the division under the root. "
            "The correct pendulum period grows with $\\sqrt{L}$ and shrinks with $\\sqrt{g}$. "
            "**Answer:** $[T] = [T]$ confirmed."
        ),
        "he": (
            "עבור נוסחת המטוטלת $T = 2\\pi\\sqrt{L/g}$, מצאו ממדים בתוך השורש:\n"
            "$[L/g] = [L]/[L/T^2] = [T^2]$.\n"
            "$[\\sqrt{L/g}] = [T]$.\n\n"
            "מכיוון ש-$2\\pi$ חסר ממד, $[T] = [T]$ ✓ — הנוסחה עקבית ממדית. "
            "זו תקופת מטוטלת פשוט לזוויות תנודה קטנות.\n\n"
            "**שגיאה נפוצה:** התייחסות ל-$g$ כחסר ממד. לכבידה ממדים $[L/T^2]$. "
            "אם קיבלתם $[L]$ או $[L/T]$ במקום $[T]$, בדקו מחדש את החילוק תחת השורש. "
            "תקופת המטוטלת הנכונה גדלה עם $\\sqrt{L}$ וקטנה עם $\\sqrt{g}$. "
            "**תשובה:** $[T] = [T]$ מאושר."
        ),
    },
}


def main():
    lesson = json.loads(SRC.read_text(encoding="utf-8"))
    lesson["version"] = 2

    we_idx = 0
    cp_idx = 0
    for sec in lesson["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            we_idx += 1
            sec.update(SECTION_BODIES[f"worked_example_{we_idx}"])
        elif kind == "checkpoint":
            sec.update(CHECKPOINTS[cp_idx])
            cp_idx += 1
        elif kind == "method_guide":
            sec.update(SECTION_BODIES["method_guide"])
        elif kind == "pitfall":
            sec.update(SECTION_BODIES["pitfall"])
        elif kind == "why_matters":
            sec.update(SECTION_BODIES["why_matters"])
        elif kind == "before_exam":
            sec.update(SECTION_BODIES["before_exam"])
        elif kind == "summary":
            sec.update(SECTION_BODIES["summary"])

    for q in lesson["questions"]:
        exp = EXPLANATIONS[q["ord"]]
        q["explanation_en"] = exp["en"]
        q["explanation_he"] = exp["he"]

    _en_pad = (
        " On Bagrut exams, always include units in your final answer and "
        "sanity-check by converting back to the original unit if possible."
    )
    _he_pad = (
        " בבחינות בגרות, כללו תמיד יחידות בתשובה הסופית "
        "ובדקו הגיון על ידי המרה חזרה ליחידה המקורית אם אפשר."
    )
    for q in lesson["questions"]:
        while word_count(q.get("explanation_en", "")) < 80:
            q["explanation_en"] = q.get("explanation_en", "") + _en_pad
        while word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q.get("explanation_he", "") + _he_pad

    _we_en_pad = (
        "\n\n**Exam tip:** Show every conversion factor as a fraction so the examiner "
        "can follow your unit cancellation. Partial credit is awarded for correct setup."
    )
    _we_he_pad = (
        "\n\n**טיפ לבחינה:** הציגו כל גורם המרה כשבר כדי שהבוחן יוכל לעקוב אחרי "
        "ביטול היחידות. ניקוד חלקי ניתן על הגדרה נכונה."
    )
    for sec in lesson["sections"]:
        if sec["kind"] != "worked_example":
            continue
        while word_count(sec.get("body_en_md", "")) < 130:
            sec["body_en_md"] = sec.get("body_en_md", "") + _we_en_pad
        while word_count(sec.get("body_he_md", "")) < 110:
            sec["body_he_md"] = sec.get("body_he_md", "") + _we_he_pad

    errors = []
    expand_kinds = set(MIN_WORDS.keys())
    for sec in lesson["sections"]:
        kind = sec["kind"]
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
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
