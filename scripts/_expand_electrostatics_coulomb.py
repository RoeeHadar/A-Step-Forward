#!/usr/bin/env python3
"""Expand electrostatics_coulomb.json to MIN_WORDS + 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/electrostatics_coulomb.json"

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
    "checkpoint": {"en": 90, "he": 75},
    "exercise_set": {"en": 90, "he": 75},
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


PATCHES = {
    "worked_example_1": {
        "body_en_md": (
            "**Given:** $q_1 = +5\\;\\mu\\text{C}$, $q_2 = -3\\;\\mu\\text{C}$, "
            "$r = 40\\;\\text{cm} = 0.4\\;\\text{m}$.\n\n"
            "**Find:** Force magnitude and direction on each charge.\n\n"
            "Bagrut electrostatics problems almost always mix unit prefixes with Coulomb's law. "
            "Before substituting, convert $\\mu\\text{C}$ to coulombs and centimeters to meters — "
            "skipping this step is the most common source of a factor-of-$10^4$ error in $r^2$.\n\n"
            "### Move 1: Convert units and write the magnitude formula\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2} = (9\\times10^9)\\frac{(5\\times10^{-6})(3\\times10^{-6})}{(0.4)^2}$$\n\n"
            "### Move 2: Evaluate the numerator and denominator\n"
            "Numerator: $9\\times10^9 \\times 15\\times10^{-12} = 135\\times10^{-3}$. "
            "Denominator: $(0.4)^2 = 0.16$.\n"
            "$$F = \\frac{135\\times10^{-3}}{0.16} = 0.844\\;\\text{N}$$\n\n"
            "### Move 3: Determine direction from charge signs\n"
            "Since $q_1 > 0$ and $q_2 < 0$ (opposite signs), the force is **attractive**. "
            "Each charge is pulled toward the other along the line joining them.\n\n"
            "**Answer:** $F = 0.844\\;\\text{N}$, attractive.\n\n"
            "**Self-check:** Re-substitute with $r = 0.4\\;\\text{m}$ and confirm opposite charges attract. "
            "If you got $844\\;\\text{N}$, you likely forgot to convert cm to m."
        ),
        "body_he_md": (
            "**נתון:** $q_1 = +5\\;\\mu\\text{C}$, $q_2 = -3\\;\\mu\\text{C}$, "
            "$r = 40\\;\\text{cm} = 0.4\\;\\text{m}$.\n\n"
            "**מצא:** גודל וכיוון הכוח על כל מטען.\n\n"
            "שאלות קולון בבגרות כמעט תמיד משלבות קידומות יחידות. "
            "לפני הצבה, המירו $\\mu\\text{C}$ לקולומים וס\"מ למטרים — "
            "דילוג על שלב זה גורם לטעות של $10^4$ ב-$r^2$.\n\n"
            "### צעד 1: המרת יחידות וכתיבת נוסחת הגודל\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2} = (9\\times10^9)\\frac{(5\\times10^{-6})(3\\times10^{-6})}{(0.4)^2}$$\n\n"
            "### צעד 2: חישוב מונה ומכנה\n"
            "מונה: $9\\times10^9 \\times 15\\times10^{-12} = 135\\times10^{-3}$. "
            "מכנה: $(0.4)^2 = 0.16$.\n"
            "$$F = \\frac{135\\times10^{-3}}{0.16} = 0.844\\;\\text{N}$$\n\n"
            "### צעד 3: קביעת כיוון לפי סימני המטענים\n"
            "מכיוון ש-$q_1 > 0$ ו-$q_2 < 0$ (סימנים מנוגדים), הכוח **מושך**. "
            "כל מטען נמשך לכיוון השני לאורך הקו המחבר.\n\n"
            "**תשובה:** $F = 0.844\\;\\text{N}$, משיכה.\n\n"
            "**בדיקה:** הציבו שוב עם $r = 0.4\\;\\text{m}$ ואשרו שמטענים מנוגדים מושכים. "
            "אם קיבלתם $844\\;\\text{N}$ — שכחתם להמיר ס\"מ למטרים. "
            "טיפ לבחינה: כתבו תמיד את יחידות $q$ בקולומים ואת $r$ במטרים לפני הצבה."
        ),
    },
    "checkpoint_1": {
        "body_en_md": (
            "**Practice now:** Two equal charges $q = +2\\;\\mu\\text{C}$ are separated by "
            "$r = 0.1\\;\\text{m}$. Find the magnitude and direction of the electrostatic force "
            "between them.\n\n"
            "Use $F = kq^2/r^2$ because both charges are equal. Convert $\\mu\\text{C}$ to "
            "coulombs ($2\\;\\mu\\text{C} = 2\\times10^{-6}\\;\\text{C}$) before substituting. "
            "Since both charges are positive, the force is **repulsive** — each charge pushes "
            "the other away along the line joining them. By Newton's third law, the force on "
            "each charge has the same magnitude.\n\n"
            "Write the formula, substitute, and state the direction. "
            "Try the calculation yourself before opening the solution below. "
            "Expected answer is a few newtons — repulsive."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** שני מטענים שווים $q = +2\\;\\mu\\text{C}$ במרחק "
            "$r = 0.1\\;\\text{m}$. מצאו את גודל וכיוון הכוח האלקטרוסטטי ביניהם.\n\n"
            "השתמשו ב-$F = kq^2/r^2$ כי שני המטענים שווים. המירו $\\mu\\text{C}$ לקולומים "
            "($2\\;\\mu\\text{C} = 2\\times10^{-6}\\;\\text{C}$) לפני הצבה. "
            "מכיוון ששניהם חיוביים, הכוח **דוחה** — כל מטען דוחה את השני "
            "לאורך הקו המחבר. לפי החוק השלישי של ניוטון, גודל הכוח על כל מטען זהה.\n\n"
            "כתבו נוסחה, הציבו, וציינו כיוון. "
            "נסו לחשב לבד לפני שפותחים את הפתרון למטה. "
            "התשובה הצפויה: כמה ניוטונים — כוח דחייה בין שני מטענים חיוביים."
        ),
    },
    "checkpoint_2": {
        "body_en_md": (
            "**Practice now:** Charges $+9\\;\\mu\\text{C}$ and $+1\\;\\mu\\text{C}$ are "
            "separated by $L = 1\\;\\text{m}$. Where on the line **between** them is the "
            "electric force on a test charge equal to zero?\n\n"
            "For two **like** positive charges, the zero-force point lies between them, "
            "closer to the **smaller** charge — the weaker source is compensated by shorter "
            "distance. Let $x$ be the distance from the $+9\\;\\mu\\text{C}$ charge and set "
            "the magnitudes of the two Coulomb forces equal: $k(9)/x^2 = k(1)/(1-x)^2$.\n\n"
            "Cancel $k$, cross-multiply, and take the positive square root. "
            "Try setting up the equation before reading the full solution."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** מטענים $+9\\;\\mu\\text{C}$ ו-$+1\\;\\mu\\text{C}$ במרחק "
            "$L = 1\\;\\text{m}$. איפה **בין** שניהם הכוח על מטען בדיקה שווה לאפס?\n\n"
            "לשני מטענים **חיוביים** דומים, נקודת $F=0$ נמצאת ביניהם, קרובה יותר "
            "למטען **הקטן** — מקור חלש מפוצה על ידי מרחק קצר יותר. "
            "יהי $x$ המרחק מ-$+9\\;\\mu\\text{C}$ והשוו גדלים: $k(9)/x^2 = k(1)/(1-x)^2$.\n\n"
            "בטלו $k$, הצלבו, וקחו שורש חיובי. "
            "הפתרון צפוי קרוב יותר למטען הקטן ($+1\\;\\mu\\text{C}$), "
            "כי שם מקור חלש מפוצה על ידי מרחק קצר. "
            "נסו להגדיר את המשוואה לפני שקוראים את הפתרון המלא."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** Four equal charges $q = +2\\;\\mu\\text{C}$ at the four corners of a "
            "square with side $a = 0.2\\;\\text{m}$. Find the net force on the charge at one corner.\n\n"
            "This is a **2D superposition** problem — decompose each force into $x$ and $y$ "
            "components before adding. Draw a diagram labeling adjacent neighbors (distance $a$) "
            "and the diagonal neighbor (distance $a\\sqrt{2}$).\n\n"
            "### Move 1: Forces from the two adjacent corner charges\n"
            "Each adjacent charge is at distance $a = 0.2\\;\\text{m}$:\n"
            "$$F_a = k\\frac{q^2}{a^2} = \\frac{9\\times10^9\\times(2\\times10^{-6})^2}{0.04} = 0.9\\;\\text{N}$$\n"
            "Both are repulsive — one along $+x$, one along $+y$.\n\n"
            "### Move 2: Force from the diagonal corner charge\n"
            "Diagonal distance $= a\\sqrt{2}$, so $r^2 = 2a^2$:\n"
            "$$F_d = k\\frac{q^2}{2a^2} = \\frac{0.9}{2} = 0.45\\;\\text{N}$$\n"
            "Repulsive, directed along the diagonal ($45°$ from each axis).\n\n"
            "### Move 3: Add components\n"
            "- $F_x = F_a + F_d\\cos45° = 0.9 + 0.45/\\sqrt{2} = 1.218\\;\\text{N}$\n"
            "- $F_y = 1.218\\;\\text{N}$ (by symmetry)\n"
            "- Magnitude: $F = 1.218\\sqrt{2} = 1.72\\;\\text{N}$\n\n"
            "**Answer:** $1.72\\;\\text{N}$ directed diagonally away from the square center.\n\n"
            "**Exam tip:** Never add the three force magnitudes directly — they are not collinear."
        ),
        "body_he_md": (
            "**נתון:** ארבעה מטענים שווים $q = +2\\;\\mu\\text{C}$ בפינות ריבוע עם צלע "
            "$a = 0.2\\;\\text{m}$. מצאו כוח נטו על המטען בפינה אחת.\n\n"
            "זו בעיית **סופרפוזיציה דו-ממדית** — פרקו כל כוח לרכיבי $x$ ו-$y$ לפני החיבור. "
            "ציירו דיאגרמה עם שכנים (מרחק $a$) ומטען אלכסוני (מרחק $a\\sqrt{2}$).\n\n"
            "### צעד 1: כוחות משני מטענים שכנים\n"
            "כל שכן במרחק $a = 0.2\\;\\text{m}$:\n"
            "$$F_a = k\\frac{q^2}{a^2} = \\frac{9\\times10^9\\times(2\\times10^{-6})^2}{0.04} = 0.9\\;\\text{N}$$\n"
            "שניהם דוחים — אחד לאורך $+x$, אחד לאורך $+y$.\n\n"
            "### צעד 2: כוח ממטען אלכסוני\n"
            "מרחק אלכסוני $= a\\sqrt{2}$, לכן $r^2 = 2a^2$:\n"
            "$$F_d = k\\frac{q^2}{2a^2} = \\frac{0.9}{2} = 0.45\\;\\text{N}$$\n"
            "דוחה, בכיוון האלכסון ($45°$ מכל ציר).\n\n"
            "### צעד 3: חיבור רכיבים\n"
            "- $F_x = F_a + F_d\\cos45° = 0.9 + 0.45/\\sqrt{2} = 1.218\\;\\text{N}$\n"
            "- $F_y = 1.218\\;\\text{N}$ (סימטריה)\n"
            "- גודל: $F = 1.218\\sqrt{2} = 1.72\\;\\text{N}$\n\n"
            "**תשובה:** $1.72\\;\\text{N}$ בכיוון אלכסוני הרחק ממרכז הריבוע.\n\n"
            "**טיפ לבחינה:** אל תחברו שלושה גדלי כוח ישירות — הם לא קולינאריים."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below in order. **Try each one before opening the "
            "solution** — the reasoning steps matter as much as the final number.\n\n"
            "The set progresses from direct two-charge calculations (easy) through superposition "
            "on a line (medium) to 2D arrangements and Coulomb–gravity comparisons (hard). "
            "For each problem: (1) convert units, (2) identify whether superposition is needed, "
            "(3) assign force directions with a diagram, (4) verify by re-substitution.\n\n"
            "Partial credit on Bagrut rewards correct setup even when arithmetic slips — "
            "always show your formula before plugging in numbers."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה לפי הסדר. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "שלבי הנימוק חשובים לא פחות מהמספר הסופי.\n\n"
            "הסדרה מתקדמת מחישובי שני מטענים (קל) דרך סופרפוזיציה על קו (בינוני) "
            "לפריסות דו-ממדיות והשוואות קולון–כבידה (קשה). "
            "בכל בעיה: (1) המירו יחידות, (2) זהו אם נדרשת סופרפוזיציה, "
            "(3) קבעו כיווני כוח בדיאגרמה, (4) אמתו בהצבה חוזרת.\n\n"
            "בבגרות נקודות חלקיות על הגדרה נכונה — תמיד הציגו נוסחה לפני הצבת מספרים. "
            "סמנו כיוון כוח (משיכה/דחייה) בכל תשובה."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Formulas to recall:**\n"
            "- $F = k|q_1||q_2|/r^2$; $k = 9\\times10^9\\;\\text{N·m}^2/\\text{C}^2$\n"
            "- Opposite signs: attractive; same signs: repulsive\n"
            "- Superposition: add force vectors component by component\n"
            "- Zero-force between like charges (closer to smaller); outside for unlike charges\n"
            "- Scaling: double $r$ → $F/4$; triple $r$ → $F/9$; double one charge → double $F$\n"
            "- $E = kQ/r^2$; $F = qE$ (links to electric field lesson)\n"
            "- $F_C/F_G \\approx 10^{39}$ for electron–proton\n\n"
            "**Last review:** Say each formula out loud once, then solve one checkpoint without "
            "looking. Convert $\\mu\\text{C}$ and cm before every calculation — this single habit "
            "prevents the most common Bagrut electrostatics errors."
        ),
        "body_he_md": (
            "**נוסחאות לזכור:**\n"
            "- $F = k|q_1 q_2|/r^2$; $k = 9\\times10^9\\;\\text{N·m}^2/\\text{C}^2$\n"
            "- מנוגדים: משיכה; דומים: דחייה\n"
            "- סופרפוזיציה: חיבור וקטורי רכיב-רכיב\n"
            "- $F=0$: בין מטענים דומים (קרוב לקטן); מחוץ לזוג למנוגדים\n"
            "- קנה מידה: $r$ כפול → $F/4$; מטען כפול → $F$ כפול\n"
            "- $E = kQ/r^2$; $F = qE$ (קשר לשיעור שדה חשמלי)\n"
            "- $F_C/F_G \\approx 10^{39}$ לאלקטרון–פרוטון\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint אחד בלי להסתכל. "
            "המירו $\\mu\\text{C}$ וס\"מ לפני כל חישוב — הרגל זה מונע את הטעויות הנפוצות ביותר "
            "באלקטרוסטטיקה בבגרות."
        ),
    },
}

INTRO_FIX = {
    "body_he_md": (
        "לפני שמנתחים מעגלים, שדות חשמליים או מאמצים, חייבים לשלוט ב**איך מטענים סטטיים "
        "דוחים ומושכים זה את זה**. חוק קולון הוא המקבילה האלקטרוסטטית לגרביטציה של ניוטון — "
        "שניהם כוחות של ריבוע הפוך — אך הכוח החשמלי יכול להיות **מושך או דוחה** "
        "והוא חזק בהרבה בקנה מידה אטומי.\n\n"
        "**למה זה חשוב בחיים:**\n"
        "- **ברק ומכות סטטיות** נובעים מהצטברות מטען כשכוחות קולון עוברים את סף פריצת האוויר.\n"
        "- **עיצוב מוליכים למחצה** מסתמך על שליטה מדויקת באינטראקציות מטען במרחקי ננומטר.\n"
        "- **מאיצי חלקיקים** משתמשים בשדות חשמליים (הבנויים מכוחות קולון) לכוון פרוטונים ואלקטרונים.\n\n"
        "בבגרות פיזיקה (3–5 יחידות), שאלות קולון משלבות המרת יחידות ($\\mu\\text{C} \\to \\text{C}$, "
        "ס\"מ $\\to$ מ'), נימוק לפי סימן, וחיבור וקטורי. תחשבו כוחות בין שני מטענים, "
        "כוח נטו על מטען שלישי, נקודות שיווי משקל, והשוואת $F_C$ ל-$F_G$.\n\n"
        "**נושאי בגרות:**\n"
        "- חישוב $F$ בין שני מטענים נקודתיים או יותר\n"
        "- מציאת נקודות שיווי משקל ($F=0$) על קו ישר\n"
        "- השוואת גודל כוח חשמלי לכוח כבידה\n"
        "- סופרפוזיציה: חיבור וקטורי של כוחות"
    ),
}

WHY_MATTERS_FIX = {
    "body_he_md": (
        "חוק קולון הוא הבסיס לכל האלקטרוסטטיקה — הוא מתחבר ישירות למושגים שתלמדו בהמשך "
        "ב-A Step Forward.\n\n"
        "**קשרים בגרף הידע:**\n"
        "- `concept:electric_field` — השדה $\\vec{E}$ מוגדר ככוח ליחידת מטען: $\\vec{F} = q\\vec{E}$.\n"
        "- `concept:electric_potential` — אנרגיה פוטנציאלית ומתח נבנים על הבנת כוחות קולון זוגיים.\n"
        "- `concept:dc_circuits_kirchhoff` — זרם זורם כי מטענים חווים כוחות במוליכים.\n\n"
        "**למה זה חשוב לבחינות:** שאלות אלקטרוסטטיקה בבגרות לעיתים רחוקות נעצרות בחישוב של "
        "שני מטענים. המבחינים משלבים המרת יחידות, נימוק סימן, סופרפוזיציה ושיווי משקל "
        "לבעיות רב-שלביות בשווי 15–20 נקודות. שליטה בקולון כאן = יכולת לטפל בשדה, "
        "פוטנציאל ומאמצים בהמשך.\n\n"
        "**השפעה בעולם האמיתי:** כל מסך מגע, סוללה ודופק עצבי מסתמכים על כוחות אלקטרוסטטיים "
        "מבוקרים ברמה המולקולרית."
    ),
}

QUESTION_EXPLANATIONS = {
    1: {
        "en": (
            "**Why this is correct:** At the midpoint of a dipole ($+q$ and $-q$ separated by $d$), "
            "each charge produces a field $E = kq/(d/2)^2$. Both fields point from $+$ toward $-$ — "
            "the same direction — so they add: $E_{\\text{total}} = 2kq/(d/2)^2 = 8kq/d^2$.\n\n"
            "**How to think about it:** Electric field direction is the force on a **positive test "
            "charge**. Near $+q$ the field points away; near $-q$ it points toward $-q$. "
            "At the midpoint both contributions align.\n\n"
            "**Common slip:** Answering \"zero\" by confusing field with force on a test charge, "
            "or picking only one charge's contribution. \"Depends on test charge sign\" confuses "
            "$\\vec{E}$ with $\\vec{F} = q\\vec{E}$.\n\n"
            "**Exam tip:** Sketch two field arrows at the midpoint — if they align, add magnitudes."
        ),
        "he": (
            "**למה זה נכון:** בנקודת האמצע של דיפול ($+q$ ו-$-q$ במרחק $d$), כל מטען יוצר "
            "שדה $E = kq/(d/2)^2$. שני השדות מ-$+$ ל-$-$ — אותו כיוון — ומתחברים: "
            "$E_{\\text{total}} = 2kq/(d/2)^2 = 8kq/d^2$.\n\n"
            "**איך לחשוב:** כיוון שדה = כוח על **מטען בדיקה חיובי**. ליד $+q$ השדה מתפזר; "
            "ליד $-q$ הוא מצביע אל $-q$. בנקודת האמצע שתי התרומות מיושרות.\n\n"
            "**טעות נפוצה:** \"אפס\" — בלבול בין שדה לכוח; או תרומה אחת בלבד. "
            "\"תלוי בסימן בדיקה\" מבלבל $\\vec{E}$ עם $\\vec{F} = q\\vec{E}$.\n\n"
            "**טיפ לבחינה:** ציירו שני חיצי שדה בנקודת האמצע — אם מיושרים, חברו גדלים."
        ),
    },
    2: {
        "he": (
            "**למה זה נכון:** $F = k|q_1||q_2|/r^2$ עם $q_1 = q_2 = 1\\times10^{-6}\\;\\text{C}$ "
            "ו-$r = 1\\;\\text{m}$: $F = 9\\times10^9 \\times 10^{-12} = 9\\times10^{-3}\\;\\text{N} "
            "= 9\\;\\text{mN}$. שני המטענים חיוביים → **דחייה**.\n\n"
            "**איך לחשוב:** יישום קולון הפשוט ביותר — מטענים שווים, מרחק יחידה. "
            "המירו $\\mu\\text{C}$ ל-C ($1\\;\\mu\\text{C} = 10^{-6}\\;\\text{C}$), ואז הציבו. "
            "הכפל $q_1 q_2 = 10^{-12}$. כתבו נוסחה לפני מספרים.\n\n"
            "**טעות נפוצה:** שכחת ריבוע $10^{-6}$ — תוצאה $9\\;\\text{N}$ במקום $9\\;\\text{mN}$. "
            "גם דיווח גודל בלי דחייה/משיכה.\n\n"
            "**טיפ לבחינה:** כש-$q_1 = q_2 = 1\\;\\mu\\text{C}$ ב-$r = 1\\;\\text{m}$ — "
            "זכרו: $9\\;\\text{mN}$. בדיקת הגיון מהירה לבעיות דומות. "
            "ציינו תמיד דחייה כששני המטענים חיוביים. יחידות סופיות: ניוטון."
        ),
    },
    3: {
        "he": (
            "**למה זה נכון:** מ-$F = kq^2/r^2$: $q^2 = Fr^2/k = 3.6 \\times 0.01 / (9\\times10^9) "
            "= 4\\times10^{-12}$. שורש: $q = 2\\times10^{-6}\\;\\text{C} = 2\\;\\mu\\text{C}$.\n\n"
            "**איך לחשוב:** כשנתונים כוח $F = 3.6\\;\\text{N}$ ומרחק $r = 0.1\\;\\text{m}$ "
            "למטענים שווים — בודדו $q^2$ קודם, ואז קחו שורש. "
            "אימות: $9\\times10^9 \\times (2\\times10^{-6})^2 / 0.01 = 3.6\\;\\text{N}$ ✓.\n\n"
            "**טעות נפוצה:** שכחת ריבוע $r = 0.1$ (שימוש ב-0.1 במקום 0.01 במכנה). "
            "גם $\\sqrt{4\\times10^{-12}} = 4\\times10^{-6}$ במקום $2\\times10^{-6}$. "
            "דיווח תשובה ב-$\\mu\\text{C}$ דורש המרה מקולומים.\n\n"
            "**טיפ לבחינה:** אחרי מציאת $q$ — הציבו חזרה לנוסחה המקורית $F = kq^2/r^2$. "
            "בבגרות נקודות חלקיות על הגדרה נכונה גם אם החשבון מסתיים בטעות. "
            "כתבו $q^2$ לפני שורש."
        ),
    },
    5: {
        "en": (
            "**Why this is correct:** Coulomb's law gives $F \\propto q_1 q_2$. If one charge "
            "doubles while the other stays fixed, the product doubles, so $F' = 2F = 2 \\times 0.5 "
            "= 1\\;\\text{N}$. The force remains attractive because the sign relationship "
            "between the charges is unchanged.\n\n"
            "**How to think about it:** This is a pure proportionality question — no need to "
            "know the individual charge values. Write $F' / F = q'_1 / q_1 = 2$ and apply "
            "directly to the given 0.5 N.\n\n"
            "**Common slip:** Answering 0.25 N by halving instead of doubling, or thinking "
            "doubling distance rather than charge. Another error: changing attract/repel when "
            "only magnitude changes.\n\n"
            "**Exam tip:** For \"one charge doubled\" problems, the force doubles — always."
        ),
        "he": (
            "**למה זה נכון:** חוק קולון: $F \\propto q_1 q_2$. הכפלת מטען אחד מכפילה את הכוח: "
            "$F' = 2F = 2 \\times 0.5 = 1\\;\\text{N}$. הכוח נשאר מושך כי יחס הסימנים לא השתנה.\n\n"
            "**איך לחשוב:** שאלת יחס טהורה — אין צורך בערכי מטענים. "
            "כתבו $F' / F = q'_1 / q_1 = 2$ והחילו על 0.5 N.\n\n"
            "**טעות נפוצה:** 0.25 N (חלוקה במקום הכפלה), או בלבול עם הכפלת מרחק. "
            "גם שינוי משיכה/דחייה כשמשתנה רק גודל.\n\n"
            "**טיפ לבחינה:** \"מטען אחד הוכפל\" — הכוח תמיד מוכפל. "
            "אין צורך לחשב מטענים בודדים — רק יחס $F'/F$. "
            "הכוח נשאר מושך; רק הגודל משתנה."
        ),
    },
    6: {
        "en": (
            "**Why this is correct:** At the midpoint ($x = 1\\;\\text{m}$), $q_3$ is 1 m from "
            "each source. From $q_1 = +6\\;\\mu\\text{C}$: repulsive on $+q_3$ → force in $+x$, "
            "$F_1 = 54\\;\\text{mN}$. From $q_2 = -6\\;\\mu\\text{C}$: attractive toward $q_2$ "
            "which is also $+x$ from the midpoint → $F_2 = 54\\;\\text{mN}$ in $+x$. "
            "Both forces align: $F_{\\text{net}} = 0.108\\;\\text{N}$ in $+x$.\n\n"
            "**How to think about it:** Draw arrows from each source before adding. Equal "
            "magnitudes and same direction mean add, not subtract.\n\n"
            "**Common slip:** Subtracting because charges have opposite signs — sign determines "
            "attract/repel, not the axis direction. Another error: using $r = 2\\;\\text{m}$ "
            "instead of 1 m to each source.\n\n"
            "**Exam tip:** Midpoint problems with $\\pm$ charges often have aligned forces."
        ),
        "he": (
            "**למה זה נכון:** בנקודת האמצע ($x = 1\\;\\text{m}$), $q_3$ במרחק 1 m מכל מקור. "
            "מ-$q_1 = +6\\;\\mu\\text{C}$: דחייה על $+q_3$ → כוח ב-$+x$, $F_1 = 54\\;\\text{mN}$. "
            "מ-$q_2 = -6\\;\\mu\\text{C}$: משיכה לכיוון $q_2$ — גם $+x$ מהאמצע → "
            "$F_2 = 54\\;\\text{mN}$ ב-$+x$. שני הכוחות מיושרים: $F_{\\text{net}} = 0.108\\;\\text{N}$.\n\n"
            "**איך לחשוב:** ציירו חיצים מכל מקור לפני חיבור. גדלים שווים וכיוון זהה = חיבור.\n\n"
            "**טעות נפוצה:** חיסור כי המטענים מנוגדים — סימן קובע משיכה/דחייה, לא כיוון ציר. "
            "גם שימוש ב-$r = 2\\;\\text{m}$ במקום 1 m.\n\n"
            "**טיפ לבחינה:** בבעיות אמצע עם $\\pm$ — לעיתים הכוחות מיושרים."
        ),
    },
    7: {
        "en": (
            "**Why this is correct:** The middle charge is $-q$. Force from left $+q$: attractive, "
            "pulling $-q$ leftward ($-x$), magnitude $kq^2/d^2$. Force from right $+q$: "
            "attractive, pulling $-q$ rightward ($+x$), same magnitude. Equal and opposite "
            "→ net force = 0.\n\n"
            "**How to think about it:** This is a symmetric dipole-like arrangement. "
            "Assign $+x$ rightward, draw both arrows on $-q$, then add as signed scalars.\n\n"
            "**Common slip:** Using repulsion for opposite-sign pairs, or adding magnitudes "
            "when forces oppose. Students sometimes forget the middle charge is $-q$, not $+q$.\n\n"
            "**Exam tip:** Symmetric three-charge lines often give zero net force on the center "
            "charge — check symmetry before calculating."
        ),
        "he": (
            "**למה זה נכון:** המטען האמצעי הוא $-q$. כוח מ-$+q$ שמאלי: משיכה, מושך $-q$ "
            "שמאלה ($-x$), גודל $kq^2/d^2$. כוח מ-$+q$ ימני: משיכה, מושך $-q$ ימינה ($+x$), "
            "אותו גודל. שווים ומנוגדים → כוח נטו = 0.\n\n"
            "**איך לחשוב:** סידור סימטרי דמוי דיפול. קבעו $+x$ ימינה, ציירו שני חיצים על $-q$, "
            "וחברו כסקלרים מסומנים.\n\n"
            "**טעות נפוצה:** דחייה לזוגות מנוגדים, או חיבור גדלים כשהכוחות מנוגדים. "
            "לפעמים שוכחים שהמטען האמצעי הוא $-q$.\n\n"
            "**טיפ לבחינה:** שלושה מטענים סימטריים על קו — לעיתים כוח נטו אפס במרכז."
        ),
    },
    8: {
        "en": (
            "**Why this is correct:** Original repulsion: $F_0 = kq^2/r^2$. With $Q = -2q$ at "
            "midpoint ($r/2$ from each $q$): $F_Q = k(2q)(q)/(r/2)^2 = 8kq^2/r^2 = 8F_0$, "
            "attractive (inward). Other $q$ still repels with $F_0$ (outward). "
            "Net on each $q$: $8F_0 - F_0 = 7F_0$ inward.\n\n"
            "**How to think about it:** The $1/r^2$ law makes the midpoint force dominate — "
            "half the distance means four times the force from $Q$, times charge ratio 2 → $8F_0$.\n\n"
            "**Common slip:** Using $2F_0$ instead of $8F_0$ (forgetting distance halving squares "
            "to 4×). Another error: subtracting repulsion when forces actually oppose.\n\n"
            "**Exam tip:** When a charge is inserted at the midpoint, always recalculate distance."
        ),
        "he": (
            "**למה זה נכון:** דחייה מקורית: $F_0 = kq^2/r^2$. עם $Q = -2q$ באמצע ($r/2$ מכל $q$): "
            "$F_Q = k(2q)(q)/(r/2)^2 = 8F_0$, מושך (פנימה). $q$ השני עדיין דוחה ב-$F_0$ (החוצה). "
            "נטו על כל $q$: $8F_0 - F_0 = 7F_0$ פנימה.\n\n"
            "**איך לחשוב:** חוק $1/r^2$ גורם לכוח האמצע לשלוט — חצי מרחק = פי 4 בכוח מ-$Q$, "
            "כפול יחס מטען 2 → $8F_0$.\n\n"
            "**טעות נפוצה:** $2F_0$ במקום $8F_0$ (שכחת ריבוע המרחק). "
            "גם חיסור דחייה כשהכוחות באמת מנוגדים.\n\n"
            "**טיפ לבחינה:** כשמוסיפים מטען באמצע — תמיד חשבו מחדש מרחק."
        ),
    },
}


def validate(lesson):
    errors = []
    for s in lesson["sections"]:
        kind = s.get("kind", "")
        min_w = MIN_WORDS.get(kind, {"en": 90, "he": 75})
        en = word_count(s.get("body_en_md", ""))
        he = word_count(s.get("body_he_md", ""))
        if en < min_w["en"]:
            errors.append(f"{s['id']}: en {en} < {min_w['en']}")
        if he < min_w["he"]:
            errors.append(f"{s['id']}: he {he} < {min_w['he']}")
        if s.get("body_he_md") and hebrew_body_weak(s["body_he_md"], s.get("body_en_md", "")):
            errors.append(f"{s['id']}: he-weak")
    for q in lesson["questions"]:
        en = word_count(q.get("explanation_en", ""))
        he = word_count(q.get("explanation_he", ""))
        if en < 80 or en > 150:
            errors.append(f"q{q['ord']}: expl_en {en}")
        if he < 80 or he > 150:
            errors.append(f"q{q['ord']}: expl_he {he}")
        if hebrew_body_weak(q.get("explanation_he", ""), q.get("explanation_en", "")):
            errors.append(f"q{q['ord']}: expl-he-weak")
    return errors


def main():
    lesson = json.loads(OUT.read_text(encoding="utf-8"))

    for sec in lesson["sections"]:
        sid = sec["id"]
        if sid in PATCHES:
            sec.update(PATCHES[sid])
        if sid == "intro":
            sec.update(INTRO_FIX)
        if sid == "why_matters":
            sec.update(WHY_MATTERS_FIX)

    for q in lesson["questions"]:
        ord_ = q["ord"]
        if ord_ in QUESTION_EXPLANATIONS:
            patch = QUESTION_EXPLANATIONS[ord_]
            if "en" in patch:
                q["explanation_en"] = patch["en"]
            if "he" in patch:
                q["explanation_he"] = patch["he"]

    errors = validate(lesson)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" ", e)
        sys.exit(1)

    OUT.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")

    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(r.returncode)
    print("Depth gates OK")


if __name__ == "__main__":
    main()
