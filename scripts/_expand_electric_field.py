#!/usr/bin/env python3
"""Expand electric_field.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/electric_field.json"

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


SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "Every time you feel a static shock or see lightning, you are witnessing **Coulomb forces** "
            "between separated charges. The **electric field** $\\vec{E}$ extends that idea: it tells you "
            "what force a **positive test charge** would feel at every point in space, without placing "
            "the charge there. Field strength $E = k|q|/r^2$ follows the same inverse-square law as "
            "Coulomb's force, but describes the **source charge's influence on the environment**.\n\n"
            "In Israeli Bagrut physics (questionnaire 2 — electricity), you will:\n"
            "- Compute $F = k|q_1||q_2|/r^2$ between point charges and identify attraction vs. repulsion.\n"
            "- Find $\\vec{E}$ at a point due to one or more charges using **vector superposition**.\n"
            "- Locate **zero-field points** on a line and interpret field-line diagrams.\n"
            "- Relate field to force on a charge: $\\vec{F} = q\\vec{E}$.\n\n"
            "**Unit conversions you must internalize:** $1\\,\\mu\\text{C} = 10^{-6}\\,\\text{C}$, "
            "$k = 9\\times10^9\\,\\text{N·m}^2/\\text{C}^2$. "
            "Skipping the $\\mu\\text{C}$ conversion is the single most common source of a "
            "factor-of-$10^{12}$ error on exam day."
        ),
        "body_he_md": (
            "בכל פעם שמרגישים מכת סטטית או רואים ברק, אתם עדים ל**כוחות קולון** "
            "בין מטענים מופרדים. ה**שדה החשמלי** $\\vec{E}$ מרחיב את הרעיון: "
            "הוא מודל איזה כוח **מטען בדיקה חיובי** יחווה בכל נקודה במרחב, "
            "בלי להניח את המטען שם. עוצמת השדה $E = k|q|/r^2$ עוקבת "
            "אחרי אותו חוק של ריבוע הפוך כמו כוח קולון, אך מתארת "
            "את **השפעת מטען המקור על הסביבה**.\n\n"
            "בבגרות בפיזיקה (שאלון 2 — חשמל), תצטרכו:\n"
            "- לחשב $F = k|q_1||q_2|/r^2$ בין מטענים נקודתיים ולזהות משיכה מול דחייה.\n"
            "- למצוא $\\vec{E}$ בנקודה עקב מטען אחד או יותר ב**סופרפוזיציה וקטורית**.\n"
            "- לאתר **נקודות אפס-שדה** על קו ולפרש דיאגרמות קווי שדה.\n"
            "- לקשר שדה לכוח על מטען: $\\vec{F} = q\\vec{E}$.\n\n"
            "**המרות יחידות שחייבים לשלוט בהן:** $1\\,\\mu\\text{C} = 10^{-6}\\,\\text{C}$, "
            "$k = 9\\times10^9\\,\\text{N·מ}^2/\\text{C}^2$. "
            "דילוג על המרת $\\mu\\text{C}$ הוא מקור הטעות הנפוץ ביותר "
            "— שגיאה של $10^{12}$ ביום הבחינה."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Coulomb's Law — force between two point charges:**\n"
            "$$\\boxed{F = k\\frac{|q_1||q_2|}{r^2}}$$\n"
            "- $q_1$, $q_2$: charge magnitudes in **coulombs** (C)\n"
            "- $r$: center-to-center distance in **meters** (m)\n"
            "- $k = 8.99\\times10^9 \\approx 9\\times10^9\\,\\text{N·m}^2/\\text{C}^2$\n"
            "- Direction: along the line joining charges — **repulsive** if same sign, "
            "**attractive** if opposite\n\n"
            "**Electric field due to a point charge $q$:**\n"
            "$$\\boxed{E = k\\frac{|q|}{r^2}}$$\n"
            "- SI unit: N/C (equivalently V/m)\n"
            "- Direction: **away** from positive source, **toward** negative source\n"
            "- Definition: $\\vec{E} = \\vec{F}/q_0$ where $q_0$ is a small positive test charge\n"
            "- The field exists at a point even when no test charge is present\n\n"
            "**Superposition principle:**\n"
            "$$\\boxed{\\vec{E}_{\\text{total}} = \\vec{E}_1 + \\vec{E}_2 + \\cdots}$$\n"
            "Add electric field **vectors** from each source charge at the point of interest. "
            "Never add magnitudes unless all fields lie on the same line and you have "
            "assigned $\\pm$ signs for direction carefully. "
            "The field at a point is independent of any test charge placed there."
        ),
        "body_he_md": (
            "**חוק קולון — כוח בין שני מטענים נקודתיים:**\n"
            "$$\\boxed{F = k\\frac{|q_1||q_2|}{r^2}}$$\n"
            "- $q_1$, $q_2$: גדלי מטען ב**קולומים** (C)\n"
            "- $r$: מרחק מרכז-למרכז ב**מטרים** (מ')\n"
            "- $k = 8.99\\times10^9 \\approx 9\\times10^9\\,\\text{N·מ}^2/\\text{C}^2$\n"
            "- כיוון: לאורך הקו המחבר — **דחייה** לסימנים זהים, **משיכה** לסימנים מנוגדים\n\n"
            "**שדה חשמלי של מטען נקודתי $q$:**\n"
            "$$\\boxed{E = k\\frac{|q|}{r^2}}$$\n"
            "- יחידת SI: N/C (שווה ערך ל-V/m)\n"
            "- כיוון: **הרחק** ממטען חיובי, **לעבר** מטען שלילי\n"
            "- הגדרה: $\\vec{E} = \\vec{F}/q_0$ כאשר $q_0$ הוא מטען בדיקה חיובי קטן\n"
            "- השדה קיים בנקודה גם כשאין מטען בדיקה\n\n"
            "**עיקרון הסופרפוזיציה:**\n"
            "$$\\boxed{\\vec{E}_{\\text{כולל}} = \\vec{E}_1 + \\vec{E}_2 + \\cdots}$$\n"
            "חברו **וקטורי** שדה מכל מטען מקור בנקודת העניין. "
            "לעולם אל תחברו גדלים אלא אם כל השדות על אותו קו "
            "וסימנתם $\\pm$ לכיוון בזהירות. "
            "השדה בנקודה אינו תלוי במטען בדיקה שמונח שם."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Electric field lines\n\n"
            "- Field lines **start** on positive charges and **end** on negative charges.\n"
            "- The density of lines is proportional to $|q|$ — denser lines mean stronger field.\n"
            "- Lines **never cross** — the field has a unique direction at every point.\n"
            "- Tangent to a line = direction of $\\vec{E}$; closer spacing = larger $|E|$.\n\n"
            "### Coulomb's law vs Newton's gravity\n\n"
            "| Property | Coulomb | Gravity |\n"
            "|---|---|---|\n"
            "| Formula | $F = kq_1q_2/r^2$ | $F = Gm_1m_2/r^2$ |\n"
            "| Type | Attract **or** repel | Always attract |\n"
            "| $1/r^2$ scaling | Yes | Yes |\n"
            "| Constant | $k = 9\\times10^9$ | $G = 6.67\\times10^{-11}$ |\n"
            "| Dominates at | Atomic scale ($\\sim10^{39}$ stronger) | Planetary scale |\n\n"
            "### Superposition: vector addition\n\n"
            "For multiple charges, compute $E_i = k|q_i|/r_i^2$ from each source separately, "
            "assign direction (away from $+$, toward $-$), then add as vectors. "
            "On a line, use signed scalars; in 2D, decompose into $x$ and $y$ components.\n\n"
            "### Zero-field point\n\n"
            "For two **like** charges on a line, $E = 0$ somewhere **between** them — "
            "closer to the smaller charge. Set magnitudes equal:\n"
            "$$\\frac{kq_1}{x^2} = \\frac{kq_2}{(d-x)^2}$$\n"
            "For **unlike** charges, the zero-field point lies **outside** the pair, "
            "on the side of the smaller-magnitude charge."
        ),
        "body_he_md": (
            "### קווי שדה חשמלי\n\n"
            "- קווי שדה **מתחילים** במטענים חיוביים ו**מסתיימים** בשליליים.\n"
            "- צפיפות הקווים פרופורציונלית ל-$|q|$ — קווים צפופים = שדה חזק יותר.\n"
            "- קווים **לא מצטלבים** — לשדה כיוון ייחודי בכל נקודה.\n"
            "- משיק לקו = כיוון $\\vec{E}$; ריווח קטן יותר = $|E|$ גדול יותר.\n\n"
            "### חוק קולון מול כבידת ניוטון\n\n"
            "| תכונה | קולון | כבידה |\n"
            "|---|---|---|\n"
            "| נוסחה | $F = kq_1q_2/r^2$ | $F = Gm_1m_2/r^2$ |\n"
            "| סוג | משיכה **או** דחייה | תמיד משיכה |\n"
            "| קנה $1/r^2$ | כן | כן |\n"
            "| קבוע | $k = 9\\times10^9$ | $G = 6.67\\times10^{-11}$ |\n"
            "| שולט ב | קנה אטומי ($\\sim10^{39}$ חזק יותר) | קנה פלנטרי |\n\n"
            "### סופרפוזיציה: חיבור וקטורי\n\n"
            "למטענים מרובים, חשבו $E_i = k|q_i|/r_i^2$ מכל מקור בנפרד, "
            "קבעו כיוון (הרחק מ-$+$, לעבר $-$), וחברו כוקטורים. "
            "על קו — סקלרים מסומנים; ב-2D — פירוק לרכיבי $x$ ו-$y$.\n\n"
            "### נקודת אפס-שדה\n\n"
            "לשני מטענים **דומים** על קו, $E = 0$ **ביניהם** — "
            "קרוב יותר למטען הקטן. השוו גדלים:\n"
            "$$\\frac{kq_1}{x^2} = \\frac{kq_2}{(d-x)^2}$$\n"
            "למטענים **מנוגדים**, נקודת אפס-שדה **מחוץ** לזוג, "
            "בצד המטען בעל הגודל הקטן יותר."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** Two charges $q_1 = +4\\,\\mu\\text{C}$ and $q_2 = -4\\,\\mu\\text{C}$ "
            "separated by $r = 0.3\\,\\text{m}$.\n\n"
            "**Find:** The magnitude and direction of the force between them.\n\n"
            "Bagrut electrostatics problems almost always mix unit prefixes with Coulomb's law. "
            "Convert $\\mu\\text{C}$ to coulombs before substituting — skipping this step "
            "is the most common source of a factor-of-$10^{12}$ error.\n\n"
            "### Move 1: Convert units\n"
            "$$q_1 = q_2 = 4 \\times 10^{-6}\\,\\text{C}$$\n\n"
            "### Move 2: Apply Coulomb's law\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2} = (9\\times10^9)\\frac{(4\\times10^{-6})(4\\times10^{-6})}{(0.3)^2}$$\n"
            "Numerator: $9\\times10^9 \\times 16\\times10^{-12} = 144\\times10^{-3}$. "
            "Denominator: $(0.3)^2 = 0.09$.\n"
            "$$F = \\frac{144\\times10^{-3}}{0.09} = 9\\times10^9 \\times 1.778\\times10^{-10} = \\boxed{1.6\\,\\text{N}}$$\n\n"
            "### Move 3: Determine direction\n"
            "Opposite signs → **attractive** force. Each charge is pulled toward the other "
            "along the line joining them.\n\n"
            "**Self-check:** Re-substitute with $r = 0.3\\,\\text{m}$. If you got $1.6\\times10^{12}\\,\\text{N}$, "
            "you forgot to convert $\\mu\\text{C}$ to C. By Newton's third law, the force on $q_1$ "
            "has equal magnitude and opposite direction to the force on $q_2$. "
            "The magnitude $1.6\\,\\text{N}$ is reasonable for microcoulomb charges at 30 cm."
        ),
        "body_he_md": (
            "**נתון:** מטענים $q_1 = +4\\,\\mu\\text{C}$ ו-$q_2 = -4\\,\\mu\\text{C}$ "
            "במרחק $r = 0.3\\,\\text{מ'}$.\n\n"
            "**מצא:** גודל וכיוון הכוח ביניהם.\n\n"
            "שאלות קולון בבגרות כמעט תמיד משלבות קידומות יחידות. "
            "המירו $\\mu\\text{C}$ לקולומים לפני הצבה — דילוג על שלב זה "
            "גורם לטעות של $10^{12}$.\n\n"
            "### צעד 1: המרת יחידות\n"
            "$$q_1 = q_2 = 4 \\times 10^{-6}\\,\\text{C}$$\n\n"
            "### צעד 2: חוק קולון\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2} = (9\\times10^9)\\frac{(4\\times10^{-6})(4\\times10^{-6})}{(0.3)^2}$$\n"
            "מונה: $9\\times10^9 \\times 16\\times10^{-12} = 144\\times10^{-3}$. "
            "מכנה: $(0.3)^2 = 0.09$.\n"
            "$$F = \\frac{144\\times10^{-3}}{0.09} = \\boxed{1.6\\,\\text{N}}$$\n\n"
            "### צעד 3: כיוון\n"
            "סימנים מנוגדים → כוח **משיכה**. כל מטען נמשך לכיוון השני "
            "לאורך הקו המחבר.\n\n"
            "**בדיקה:** הציבו שוב עם $r = 0.3\\,\\text{מ'}$. "
            "אם קיבלתם $1.6\\times10^{12}\\,\\text{N}$ — שכחתם להמיר $\\mu\\text{C}$ ל-C. "
            "לפי החוק השלישי של ניוטון, הכוח על $q_1$ בגודל שווה ובכיוון הפוך לכוח על $q_2$. "
            "גודל $1.6\\,\\text{N}$ סביר למטעני מיקרו-קולום במרחק 30 ס\"מ. "
            "זו דוגמה קלאסית לכוח משיכה."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** Three charges on a line: $q_1 = +3\\,\\mu\\text{C}$ at $x=0$, "
            "$q_2 = -2\\,\\mu\\text{C}$ at $x=0.1\\,\\text{m}$, $q_3 = +5\\,\\mu\\text{C}$ at $x=0.3\\,\\text{m}$.\n\n"
            "**Find:** Net force on $q_2$.\n\n"
            "Apply superposition: compute the force from each neighbor separately, "
            "assign direction along the $x$-axis, then add as signed scalars. "
            "Draw a diagram with arrows before computing — it prevents sign errors.\n\n"
            "### Move 1: Force from $q_1$ on $q_2$\n"
            "$$F_{12} = k\\frac{|q_1||q_2|}{r_{12}^2} = 9\\times10^9 \\times \\frac{3\\times10^{-6}\\times2\\times10^{-6}}{(0.1)^2}$$\n"
            "$$F_{12} = 9\\times10^9 \\times \\frac{6\\times10^{-12}}{0.01} = 5.4\\,\\text{N}$$\n"
            "$q_1 > 0$, $q_2 < 0$ → attractive → force on $q_2$ points in **−x** (toward $q_1$).\n\n"
            "### Move 2: Force from $q_3$ on $q_2$\n"
            "$$r_{23} = 0.3 - 0.1 = 0.2\\,\\text{m}$$\n"
            "$$F_{23} = 9\\times10^9 \\times \\frac{5\\times10^{-6}\\times2\\times10^{-6}}{(0.2)^2} = 2.25\\,\\text{N}$$\n"
            "$q_3 > 0$, $q_2 < 0$ → attractive → force on $q_2$ points in **+x** (toward $q_3$).\n\n"
            "### Move 3: Net force\n"
            "$$\\vec{F}_{\\text{net}} = F_{23} - F_{12} = 2.25 - 5.4 = -3.15\\,\\text{N}$$\n"
            "$$\\boxed{F_{\\text{net}} = 3.15\\,\\text{N toward }q_1\\text{ (−x direction)}}$$\n\n"
            "**Exam tip:** The closer charge ($q_1$ at 0.1 m) produces a stronger force than "
            "the farther charge ($q_3$ at 0.2 m), so the net force points toward $q_1$."
        ),
        "body_he_md": (
            "**נתון:** שלושה מטענים בקו: $q_1=+3\\,\\mu\\text{C}$ ב-$x=0$, "
            "$q_2=-2\\,\\mu\\text{C}$ ב-$x=0.1\\,\\text{מ'}$, $q_3=+5\\,\\mu\\text{C}$ ב-$x=0.3\\,\\text{מ'}$.\n\n"
            "**מצא:** כוח נטו על $q_2$.\n\n"
            "הפעילו סופרפוזיציה: חשבו כוח מכל שכן בנפרד, "
            "קבעו כיוון לאורך ציר $x$, וחברו כסקלרים מסומנים. "
            "ציירו דיאגרמה עם חיצים לפני החישוב — מונע טעויות סימן.\n\n"
            "### צעד 1: כוח מ-$q_1$ על $q_2$\n"
            "$$F_{12} = 9\\times10^9 \\times \\frac{3\\times10^{-6}\\times2\\times10^{-6}}{(0.1)^2} = 5.4\\,\\text{N}$$\n"
            "$q_1 > 0$, $q_2 < 0$ → משיכה → כוח על $q_2$ בכיוון **−x** (לעבר $q_1$).\n\n"
            "### צעד 2: כוח מ-$q_3$ על $q_2$\n"
            "$$r_{23} = 0.2\\,\\text{מ'}$$\n"
            "$$F_{23} = 9\\times10^9 \\times \\frac{5\\times10^{-6}\\times2\\times10^{-6}}{(0.2)^2} = 2.25\\,\\text{N}$$\n"
            "$q_3 > 0$, $q_2 < 0$ → משיכה → כוח על $q_2$ בכיוון **+x** (לעבר $q_3$).\n\n"
            "### צעד 3: כוח נטו\n"
            "$$F_{\\text{נטו}} = F_{23} - F_{12} = 2.25 - 5.4 = -3.15\\,\\text{N}$$\n"
            "$$\\boxed{F_{\\text{נטו}} = 3.15\\,\\text{N לעבר }q_1\\text{ (כיוון −x)}}$$\n\n"
            "**טיפ לבחינה:** המטען הקרוב ($q_1$ ב-0.1 מ') יוצר כוח חזק יותר "
            "מהרחוק ($q_3$ ב-0.2 מ'), לכן הכוח הנטו לכיוון $q_1$."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** $q_1 = +9\\,\\mu\\text{C}$ at $x=0$ and $q_2 = +4\\,\\mu\\text{C}$ "
            "at $x = d = 0.3\\,\\text{m}$.\n\n"
            "**Find:** The point on the x-axis where the electric field is zero.\n\n"
            "Both charges are positive, so the zero-field point lies **between** them "
            "where the fields from each source point in opposite directions. "
            "It must be closer to the smaller charge $q_2$.\n\n"
            "### Move 1: Set up equilibrium\n"
            "Let $x$ = distance from $q_1$ (so distance from $q_2$ is $d - x$):\n"
            "$$\\frac{kq_1}{x^2} = \\frac{kq_2}{(d-x)^2} \\Rightarrow \\frac{9}{x^2} = \\frac{4}{(0.3-x)^2}$$\n\n"
            "### Move 2: Cross-multiply and take positive square root\n"
            "$$9(0.3-x)^2 = 4x^2 \\Rightarrow 3(0.3-x) = 2x \\Rightarrow 0.9 - 3x = 2x$$\n"
            "$$\\boxed{x = 0.18\\,\\text{m from }q_1}$$\n\n"
            "### Move 3: Verify both fields match\n"
            "$$E_1 = 9\\times10^9 \\times \\frac{9\\times10^{-6}}{(0.18)^2} = 2.5\\times10^6\\,\\text{N/C}$$\n"
            "$$E_2 = 9\\times10^9 \\times \\frac{4\\times10^{-6}}{(0.12)^2} = 2.5\\times10^6\\,\\text{N/C}$$ ✓\n\n"
            "**Exam tip:** Always verify $0 < x < d$ and re-substitute both field magnitudes. "
            "The ratio of charge magnitudes $\\sqrt{q_1/q_2} = 3/2$ tells you the zero point "
            "divides the segment in ratio $3:2$ from $q_1$ — confirming $x = 0.18$ m out of $0.3$ m. "
            "Substitute back to verify both fields equal $2.5\\times10^6\\,\\text{N/C}$."
        ),
        "body_he_md": (
            "**נתון:** $q_1=+9\\,\\mu\\text{C}$ ב-$x=0$, $q_2=+4\\,\\mu\\text{C}$ "
            "ב-$x=0.3\\,\\text{מ'}$.\n\n"
            "**מצא:** נקודת אפס-שדה על ציר $x$.\n\n"
            "שני המטענים חיוביים, לכן נקודת אפס-שדה **ביניהם** "
            "שם השדות מכל מקור בכיוונים מנוגדים. "
            "היא חייבת להיות קרובה יותר למטען הקטן $q_2$.\n\n"
            "### צעד 1: הגדרת שיווי משקל\n"
            "יהי $x$ = מרחק מ-$q_1$ (מרחק מ-$q_2$ הוא $d - x$):\n"
            "$$\\frac{9}{x^2} = \\frac{4}{(0.3-x)^2}$$\n\n"
            "### צעד 2: הצלבה ושורש חיובי\n"
            "$$9(0.3-x)^2 = 4x^2 \\Rightarrow 3(0.3-x) = 2x \\Rightarrow \\boxed{x = 0.18\\,\\text{מ' מ-}q_1}$$\n\n"
            "### צעד 3: אימות\n"
            "$$E_1 = 9\\times10^9 \\times \\frac{9\\times10^{-6}}{(0.18)^2} = 2.5\\times10^6\\,\\text{N/C}$$\n"
            "$$E_2 = 9\\times10^9 \\times \\frac{4\\times10^{-6}}{(0.12)^2} = 2.5\\times10^6\\,\\text{N/C}$$ ✓\n\n"
            "**טיפ לבחינה:** אמתו $0 < x < d$ והציבו שוב את שני גדלי השדה. "
            "יחס $\\sqrt{q_1/q_2} = 3/2$ אומר שנקודת האפס מחלקת את הקטע ביחס $3:2$ מ-$q_1$ — "
            "מאשר $x = 0.18$ מ' מתוך $0.3$ מ'. "
            "הציבו בחזרה לאימות ששני השדות שווים ל-$2.5\\times10^6\\,\\text{N/C}$. "
            "נקודה זו קרובה יותר למטען הקטן $q_2$. "
            "זו שאלת בגרות קלאסית על אפס-שדה."
        ),
    },
    "checkpoint_1": {
        "body_en_md": (
            "**Practice now:** Two charges $+2\\,\\mu\\text{C}$ and $+8\\,\\mu\\text{C}$ "
            "are separated by 0.4 m. Find the electric force between them. "
            "Is it attractive or repulsive?\n\n"
            "Both charges are positive, so the force is **repulsive** — each charge pushes "
            "the other away along the line joining them. Use $F = k|q_1||q_2|/r^2$ with "
            "charges converted to coulombs ($2\\,\\mu\\text{C} = 2\\times10^{-6}\\,\\text{C}$, "
            "$8\\,\\mu\\text{C} = 8\\times10^{-6}\\,\\text{C}$). "
            "Try the calculation yourself before opening the solution below. "
            "Expected answer: about 1 N, repulsive — if you get a number near $10^{12}$, "
            "check your unit conversion. Write the formula before substituting numbers. "
            "Show both magnitude and direction in your answer."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** מטענים $+2\\,\\mu\\text{C}$ ו-$+8\\,\\mu\\text{C}$ "
            "במרחק 0.4 מ'. מצאו כוח קולון ביניהם. משיכה או דחייה?\n\n"
            "שני המטענים חיוביים, לכן הכוח **דוחה** — כל מטען דוחף את השני. "
            "השתמשו ב-$F = k|q_1||q_2|/r^2$ עם מטענים בקולומים "
            "($2\\,\\mu\\text{C} = 2\\times10^{-6}\\,\\text{C}$, "
            "$8\\,\\mu\\text{C} = 8\\times10^{-6}\\,\\text{C}$). "
            "נסו לחשב לבד לפני שפותחים את הפתרון. "
            "תשובה צפויה: כ-1 N, דחייה — אם קיבלתם מספר ליד $10^{12}$, בדקו המרת יחידות. "
            "כתבו את הנוסחה לפני הצבת מספרים. "
            "ציינו גודל וכיוון (דחייה) בתשובה. "
            "המרת $\\mu\\text{C}$ לקולומים היא השלב הראשון — אל תדלגו עליו לעולם."
        ),
        "checkpoint_solution_en": (
            "Two **positive** charges repel each other. Convert to coulombs first.\n\n"
            "### Step 1: Write the formula\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2}$$\n\n"
            "### Step 2: Substitute\n"
            "$$F = 9\\times10^9 \\times \\frac{2\\times10^{-6}\\times8\\times10^{-6}}{(0.4)^2}$$\n"
            "$$F = 9\\times10^9 \\times \\frac{16\\times10^{-12}}{0.16} = 9\\times10^9 \\times 10^{-10}$$\n\n"
            "### Step 3: Evaluate\n"
            "$$F = \\boxed{0.9\\,\\text{N}}$$\n\n"
            "**Direction:** Same sign → **repulsive**.\n\n"
            "**Verify:** Numerator $16\\times10^{-12}$, denominator $0.16$ — units give newtons ✓."
        ),
        "checkpoint_solution_he": (
            "שני מטענים **חיוביים** דוחים זה את זה. המירו לקולומים קודם.\n\n"
            "### שלב 1: כתיבת הנוסחה\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2}$$\n\n"
            "### שלב 2: הצבה\n"
            "$$F = 9\\times10^9 \\times \\frac{2\\times10^{-6}\\times8\\times10^{-6}}{(0.4)^2}$$\n"
            "$$F = 9\\times10^9 \\times \\frac{16\\times10^{-12}}{0.16} = 9\\times10^9 \\times 10^{-10}$$\n\n"
            "### שלב 3: חישוב\n"
            "$$F = \\boxed{0.9\\,\\text{N}}$$\n\n"
            "**כיוון:** אותו סימן → **דחייה**.\n\n"
            "**אימות:** מונה $16\\times10^{-12}$, מכנה $0.16$ — יחידות נותנות ניוטון ✓."
        ),
    },
    "checkpoint_2": {
        "body_en_md": (
            "**Practice now:** Two charges $q_1 = +6\\,\\mu\\text{C}$ and $q_2 = +6\\,\\mu\\text{C}$ "
            "are 0.3 m apart. Find the electric field at the midpoint between them.\n\n"
            "At the midpoint, each charge is 0.15 m away ($r = 0.3/2 = 0.15\\,\\text{m}$). "
            "Both fields have equal magnitude "
            "but point in **opposite directions** (away from each positive source). "
            "Compute $E = k|q|/r^2$ for each charge separately, then add vectorially. "
            "At the midpoint, $E_1$ points toward $q_2$ and $E_2$ points toward $q_1$ — "
            "opposite directions cancel exactly. "
            "This is a symmetry problem — equal charges at equal distances should give zero net field. "
            "State your final answer clearly: $E_{\\text{net}} = 0$ by symmetry."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** מטענים $q_1=+6\\,\\mu\\text{C}$ ו-$q_2=+6\\,\\mu\\text{C}$ "
            "במרחק 0.3 מ'. מצאו שדה חשמלי בנקודת האמצע.\n\n"
            "בנקודת האמצע, כל מטען במרחק 0.15 מ' ($r = 0.3/2 = 0.15\\,\\text{מ'}$). "
            "שני השדות בגודל שווה "
            "אך בכיוונים **מנוגדים** (הרחק מכל מטען חיובי). "
            "חשבו $E = k|q|/r^2$ לכל מטען בנפרד, ואז חברו וקטורית. "
            "בנקודת האמצע, $E_1$ לכיוון $q_2$ ו-$E_2$ לכיוון $q_1$ — "
            "כיוונים מנוגדים מתקזזים בדיוק. "
            "זו בעיית סימטריה — מטענים שווים במרחקים שווים אמורים לתת שדה נטו אפס. "
            "ציינו בבירור: $E_{\\text{נטו}} = 0$ מסיבות סימטריה. "
            "אין צורך בחישוב מספרי אם מזהים את הסימטריה."
        ),
        "checkpoint_solution_en": (
            "At the midpoint, distance from each charge is $r = 0.15\\,\\text{m}$.\n\n"
            "### Step 1: Field from each charge\n"
            "$$E_1 = E_2 = k\\frac{|q|}{r^2} = 9\\times10^9 \\times \\frac{6\\times10^{-6}}{(0.15)^2}$$\n"
            "$$E_1 = E_2 = \\frac{54\\times10^3}{0.0225} = 2.4\\times10^6\\,\\text{N/C}$$\n\n"
            "### Step 2: Assign directions\n"
            "Both charges are positive → each field points **away** from its source. "
            "At the midpoint, $E_1$ points toward $q_2$ (+x) and $E_2$ points toward $q_1$ (−x).\n\n"
            "### Step 3: Superposition\n"
            "Equal magnitudes, opposite directions → $\\boxed{E_{\\text{net}} = 0}$.\n\n"
            "**Key insight:** Symmetry guarantees zero field at the midpoint of equal like charges."
        ),
        "checkpoint_solution_he": (
            "בנקודת האמצע, מרחק מכל מטען הוא $r = 0.15\\,\\text{מ'}$.\n\n"
            "### שלב 1: שדה מכל מטען\n"
            "$$E_1 = E_2 = k\\frac{|q|}{r^2} = 9\\times10^9 \\times \\frac{6\\times10^{-6}}{(0.15)^2}$$\n"
            "$$E_1 = E_2 = 2.4\\times10^6\\,\\text{N/C}$$\n\n"
            "### שלב 2: כיוונים\n"
            "שני המטענים חיוביים → כל שדה **מתרחק** ממקורו. "
            "בנקודת האמצע, $E_1$ לכיוון $q_2$ (+x) ו-$E_2$ לכיוון $q_1$ (−x).\n\n"
            "### שלב 3: סופרפוזיציה\n"
            "גדלים שווים, כיוונים מנוגדים → $\\boxed{E_{\\text{נטו}} = 0}$.\n\n"
            "**תובנה:** סימטריה מבטיחה שדה אפס בנקודת האמצע של מטענים שווים ודומים."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Situation | Method | Key tip |\n"
            "|---|---|---|\n"
            "| Force between two charges | $F = k|q_1||q_2|/r^2$; check signs | Convert $\\mu\\text{C}$ first |\n"
            "| Field from one charge | $E = k|q|/r^2$; direction away from $+$ | Field exists without test charge |\n"
            "| Multiple charges (line) | Compute each $E_i$; add as $\\pm$ scalars | Draw arrows before adding |\n"
            "| Multiple charges (2D) | Decompose into $x$/$y$; vector-add | Diagonal distance $= a\\sqrt{2}$ |\n"
            "| Zero-field (like charges) | Set $E_1 = E_2$ between them | Closer to smaller charge |\n"
            "| Zero-field (unlike charges) | Same equation; solution **outside** | On side of smaller $|q|$ |\n"
            "| Force on charge in field | $F = qE$ | Sign of $q$ determines force direction |\n\n"
            "**Decision flow:**\n"
            "1. Force or field? Force needs two charges; field needs one source + a point.\n"
            "2. How many sources? One → direct formula. Multiple → superposition.\n"
            "3. Finding a position? Set net field to zero and solve algebraically.\n\n"
            "**When to use:** Match the row to your problem type first; only then substitute numbers."
        ),
        "body_he_md": (
            "| מצב | שיטה | טיפ מרכזי |\n"
            "|---|---|---|\n"
            "| כוח בין שני מטענים | $F = k|q_1 q_2|/r^2$; בדקו סימנים | המירו $\\mu\\text{C}$ קודם |\n"
            "| שדה ממטען אחד | $E = k|q|/r^2$; הרחק מ-$+$ | שדה קיים בלי מטען בדיקה |\n"
            "| מטענים מרובים (קו) | חשבו כל $E_i$; חיבור $\\pm$ | ציירו חיצים לפני חיבור |\n"
            "| מטענים מרובים (2D) | פירוק ל-$x$/$y$; חיבור וקטורי | מרחק אלכסוני $= a\\sqrt{2}$ |\n"
            "| אפס-שדה (מטענים דומים) | $E_1 = E_2$ ביניהם | קרוב יותר למטען הקטן |\n"
            "| אפס-שדה (מטענים מנוגדים) | אותה משוואה; פתרון **מחוץ** | בצד $|q|$ הקטן |\n"
            "| כוח על מטען בשדה | $F = qE$ | סימן $q$ קובע כיוון כוח |\n\n"
            "**זרימת החלטה:**\n"
            "1. כוח או שדה? כוח דורש שני מטענים; שדה — מקור אחד + נקודה.\n"
            "2. כמה מקורות? אחד → נוסחה ישירה. מרובים → סופרפוזיציה.\n"
            "3. מציאת מיקום? הגדירו שדה נטו לאפס ופתרו אלגברית.\n\n"
            "**מתי להשתמש:** התאימו את השורה לסוג הבעיה; רק אז הציבו מספרים."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below in order. **Try each one before opening the solution** — "
            "the reasoning steps matter as much as the final number.\n\n"
            "The set progresses from direct two-charge calculations (easy) through field superposition "
            "on a line (medium) to zero-field points and 2D arrangements (hard). "
            "For each problem: (1) convert units, (2) identify force vs. field, "
            "(3) assign directions with a diagram, (4) verify by re-substitution.\n\n"
            "Partial credit on Bagrut rewards correct setup even when arithmetic slips — "
            "always show your formula before plugging in numbers and state force direction."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה לפי הסדר. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "שלבי הנימוק חשובים לא פחות מהמספר הסופי.\n\n"
            "הסדרה מתקדמת מחישובי שני מטענים (קל) דרך סופרפוזיציית שדות על קו (בינוני) "
            "לנקודות אפס-שדה ופריסות דו-ממדיות (קשה). "
            "בכל בעיה: (1) המירו יחידות, (2) זהו כוח מול שדה, "
            "(3) קבעו כיוונים בדיאגרמה, (4) אמתו בהצבה חוזרת.\n\n"
            "בבגרות נקודות חלקיות על הגדרה נכונה — תמיד הציגו נוסחה לפני הצבת מספרים "
            "וציינו כיוון כוח (משיכה/דחייה) בכל תשובה."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting to convert $\\mu\\text{C}$ to C.** Always multiply by $10^{-6}$. "
            "Leaving charges in $\\mu\\text{C}$ gives an answer $10^{12}$ times too large.\n\n"
            "2. **Using $r$ instead of $r^2$ in the denominator.** Both Coulomb's law and "
            "the field formula have $1/r^2$ scaling — this is an inverse-**square** law.\n\n"
            "3. **Applying superposition as scalar addition.** Fields are **vectors**. "
            "Opposite-direction fields subtract; same-direction fields add. "
            "In 2D, decompose into components first.\n\n"
            "4. **Wrong sign for field direction.** Electric field points **away** from positive "
            "charges and **toward** negative charges — independent of any test charge you place.\n\n"
            "5. **Looking for zero-field point in the wrong region.** Same sign → between them. "
            "Opposite sign → outside the pair, on the side of the smaller charge.\n\n"
            "6. **Confusing force on a charge with the field.** $E = F/q_0$ — the field exists "
            "at a point regardless of whether a test charge is there; $F = qE$ requires a charge."
        ),
        "body_he_md": (
            "1. **שכחת המרת $\\mu\\text{C}$ ל-C.** תמיד כפלו ב-$10^{-6}$. "
            "השארת מטענים ב-$\\mu\\text{C}$ נותנת תשובה גדולה פי $10^{12}$.\n\n"
            "2. **$r$ במקום $r^2$ במכנה.** גם חוק קולון וגם נוסחת השדה כוללים $1/r^2$ — "
            "זה חוק של ריבוע **הפוך**.\n\n"
            "3. **סופרפוזיציה כחיבור סקלרי.** שדות הם **וקטורים**. "
            "כיוונים מנוגדים מחסירים; כיוונים זהים מחברים. "
            "ב-2D — פירוק לרכיבים קודם.\n\n"
            "4. **כיוון שגוי.** שדה **מתרחק** ממטענים חיוביים ו**מתקרב** לשליליים — "
            "בלי קשר למטען בדיקה.\n\n"
            "5. **אזור שגוי לנקודת אפס.** סימן זהה → בין; סימנים מנוגדים → מחוץ, "
            "בצד המטען הקטן.\n\n"
            "6. **ערבוב כוח על מטען עם השדה.** $E = F/q_0$ — שדה קיים ללא מטען בדיקה; "
            "$F = qE$ דורש מטען."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "The electric field is the foundation of all electrostatics and circuit analysis. "
            "Every voltage difference you measure with a multimeter reflects accumulated "
            "field work between two points.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:electric_potential` — potential energy and voltage (direct prereq)\n"
            "- `concept:electric_circuits` — current flows because of field-driven potential differences\n"
            "- `concept:capacitors_parallel_plate` — uniform field between plates\n\n"
            "**Builds on:**\n"
            "- `concept:vectors_basics` — superposition requires vector addition\n"
            "- `concept:electrostatics` — charge conservation and Coulomb's law\n\n"
            "**Why it matters for exams:** Bagrut rewards recognizing whether a problem asks for "
            "force, field, or equilibrium — and choosing the right formula without hesitation."
        ),
        "body_he_md": (
            "השדה החשמלי הוא יסוד כל האלקטרוסטטיקה וניתוח מעגלים. "
            "כל הפרש מתח שמודדים במולטימטר משקף עבודת שדה "
            "מצטברת בין שתי נקודות.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:electric_potential` — אנרגיה פוטנציאלית ומתח (prereq ישיר)\n"
            "- `concept:electric_circuits` — זרם זורם בגלל הפרשי פוטנציאל מונעי-שדה\n"
            "- `concept:capacitors_parallel_plate` — שדה אחיד בין לוחות\n\n"
            "**מבוסס על:**\n"
            "- `concept:vectors_basics` — סופרפוזיציה דורשת חיבור וקטורי\n"
            "- `concept:electrostatics` — שימור מטען וחוק קולון\n\n"
            "**למה זה חשוב לבחינות:** בבגרות מעריכים זיהוי האם השאלה מבקשת "
            "כוח, שדה, או שיווי משקל — ובחירת הנוסחה הנכונה בלי היסוס."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "### Formula sheet\n\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2} \\qquad E = k\\frac{|q|}{r^2} \\qquad "
            "\\vec{F} = q\\vec{E} \\qquad k = 9\\times10^9\\,\\text{N·m}^2/\\text{C}^2$$\n\n"
            "### Unit conversions\n"
            "$$1\\,\\mu\\text{C} = 10^{-6}\\,\\text{C} \\qquad 1\\,\\text{nC} = 10^{-9}\\,\\text{C}$$\n\n"
            "### Checklist\n"
            "- [ ] Charges converted to C?\n"
            "- [ ] Distance in meters?\n"
            "- [ ] Field direction: away from $+$, toward $-$?\n"
            "- [ ] Superposition applied vectorially?\n"
            "- [ ] Zero-field region identified correctly?\n"
            "- [ ] Force vs. field formula chosen correctly?\n\n"
            "**Last review:** Say each formula out loud once, then solve one checkpoint without looking. "
            "Convert $\\mu\\text{C}$ before every calculation — this single habit prevents "
            "the most common Bagrut electrostatics errors. "
            "Scaling shortcut: if $r$ doubles, both $F$ and $E$ divide by 4. "
            "Know the difference: $F$ needs two charges; $E$ needs one source."
        ),
        "body_he_md": (
            "### דף נוסחאות\n\n"
            "$$F = k\\frac{|q_1||q_2|}{r^2} \\qquad E = k\\frac{|q|}{r^2} \\qquad "
            "\\vec{F} = q\\vec{E} \\qquad k = 9\\times10^9\\,\\text{N·מ}^2/\\text{C}^2$$\n\n"
            "### המרות יחידות\n"
            "$$1\\,\\mu\\text{C} = 10^{-6}\\,\\text{C} \\qquad 1\\,\\text{nC} = 10^{-9}\\,\\text{C}$$\n\n"
            "### רשימת בדיקה\n"
            "- [ ] מטענים הומרו ל-C?\n"
            "- [ ] מרחק במטרים?\n"
            "- [ ] כיוון שדה: הרחק מ-$+$, לעבר $-$?\n"
            "- [ ] סופרפוזיציה וקטורית?\n"
            "- [ ] אזור אפס-שדה זוהה נכון?\n"
            "- [ ] נוסחת כוח מול שדה נבחרה נכון?\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint אחד בלי להסתכל. "
            "המירו $\\mu\\text{C}$ לפני כל חישוב — הרגל זה מונע את הטעויות הנפוצות ביותר. "
            "קיצור קנה מידה: אם $r$ כפול, גם $F$ וגם $E$ מתחלקים ב-4."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Coulomb's law:** $F = k|q_1||q_2|/r^2$ (N); same sign → repel, opposite → attract\n"
            "- **Electric field:** $E = k|q|/r^2$ (N/C); direction away from $+$, toward $-$\n"
            "- **Force on charge:** $F = qE$ — sign of $q$ determines force direction\n"
            "- **Constant:** $k = 9\\times10^9\\,\\text{N·m}^2/\\text{C}^2$\n"
            "- **Superposition:** $\\vec{E}_{\\text{total}} = \\sum \\vec{E}_i$ (vector sum)\n"
            "- **Scaling:** $F, E \\propto 1/r^2$ — double $r$ → divide by 4\n"
            "- **Zero-field point:** between like charges; outside (near smaller) for opposite\n\n"
            "**Takeaway:** You should now identify whether a problem asks for force, field, or "
            "equilibrium, choose the correct method, and execute with proper units and sign reasoning."
        ),
        "body_he_md": (
            "- **חוק קולון:** $F = k|q_1 q_2|/r^2$; סימן זהה → דחייה, מנוגד → משיכה\n"
            "- **שדה חשמלי:** $E = k|q|/r^2$; כיוון הרחק מ-$+$, לעבר $-$\n"
            "- **כוח על מטען:** $F = qE$ — סימן $q$ קובע כיוון כוח\n"
            "- **קבוע:** $k = 9\\times10^9\\,\\text{N·מ}^2/\\text{C}^2$\n"
            "- **סופרפוזיציה:** $\\vec{E}_{\\text{כולל}} = \\sum \\vec{E}_i$ (חיבור וקטורי)\n"
            "- **קנה מידה:** $F, E \\propto 1/r^2$ — $r$ כפול → חלוקה ב-4\n"
            "- **אפס-שדה:** בין מטענים זהים; מחוץ (ליד הקטן) למנוגדים\n\n"
            "**מסקנה:** כעת תזהו האם השאלה מבקשת כוח, שדה, או שיווי משקל, "
            "תבחרו שיטה נכונה, ותבצעו עם יחידות וסימנים נכונים."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:** Convert charges to coulombs and apply Coulomb's law:\n"
            "$$F = 9\\times10^9 \\times \\frac{(3\\times10^{-6})^2}{(0.1)^2} = "
            "9\\times10^9 \\times \\frac{9\\times10^{-12}}{0.01} = \\boxed{8.1\\,\\text{N}}$$\n"
            "Both charges are positive → **repulsive** force.\n\n"
            "**How to think about it:** Same-sign charges always repel. Use magnitudes in the "
            "formula; determine attraction/repulsion from signs separately.\n\n"
            "**Common slip:** Forgetting to convert $\\mu\\text{C}$ to C (gives $8.1\\times10^{12}\\,\\text{N}$), "
            "or using $r$ instead of $r^2$ in the denominator.\n\n"
            "**Exam tip:** After computing, ask: do like charges repel? If yes, your direction is correct. "
            "Also verify: $r^2 = (0.1)^2 = 0.01$ m² and $(3\\times10^{-6})^2 = 9\\times10^{-12}$ C²."
        ),
        "explanation_he": (
            "**למה זה נכון:** המירו מטענים לקולומים והפעילו חוק קולון:\n"
            "$$F = 9\\times10^9 \\times \\frac{(3\\times10^{-6})^2}{(0.1)^2} = \\boxed{8.1\\,\\text{N}}$$\n"
            "שני המטענים חיוביים → כוח **דוחה**.\n\n"
            "**איך לחשוב:** מטענים באותו סימן תמיד דוחים. השתמשו בגדלים בנוסחה; "
            "קבעו משיכה/דחייה לפי סימנים בנפרד. זו שאלת חישוב ישיר — "
            "המרת $\\mu\\text{C}$, הצבה, וקביעת כיוון.\n\n"
            "**טעות נפוצה:** שכחת המרת $\\mu\\text{C}$ ל-C (נותן $8.1\\times10^{12}\\,\\text{N}$), "
            "או שימוש ב-$r$ במקום $r^2$. גם ערבוב משיכה עם דחייה.\n\n"
            "**טיפ לבחינה:** אחרי החישוב, שאלו: האם מטענים זהים דוחים? "
            "אמתו: $r^2 = 0.01$ מ² ו-$(3\\times10^{-6})^2 = 9\\times10^{-12}$ C². "
            "תשובה סופית: 8.1 N, כוח דחייה."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** The electric field from a point charge is:\n"
            "$$E = k\\frac{|q|}{r^2} = 9\\times10^9 \\times \\frac{5\\times10^{-6}}{(0.2)^2} = "
            "\\boxed{1.125\\times10^6\\,\\text{N/C}}$$\n"
            "Direction: **away** from the positive source charge.\n\n"
            "**How to think about it:** Field describes what a positive test charge would feel. "
            "Near a $+$ charge, the field radiates outward. Use $|q|$ for magnitude; "
            "assign direction separately.\n\n"
            "**Common slip:** Using $F = kq_1q_2/r^2$ (needs two charges) instead of "
            "$E = kq/r^2$ (one source). Another error: field toward a positive charge.\n\n"
            "**Exam tip:** N/C and V/m are equivalent units for electric field. "
            "Double-check: $(0.2)^2 = 0.04$ m² and $5\\times10^{-6}$ C in the numerator."
        ),
        "explanation_he": (
            "**למה זה נכון:** השדה החשמלי ממטען נקודתי:\n"
            "$$E = k\\frac{|q|}{r^2} = 9\\times10^9 \\times \\frac{5\\times10^{-6}}{(0.2)^2} = "
            "\\boxed{1.125\\times10^6\\,\\text{N/C}}$$\n"
            "כיוון: **הרחק** ממטען המקור החיובי.\n\n"
            "**איך לחשוב:** שדה מתאר מה מטען בדיקה חיובי יחווה. "
            "ליד מטען $+$, השדה מתפזר החוצה. השתמשו ב-$|q|$ לגודל; "
            "קבעו כיוון בנפרד. זו שאלת שדה ממקור יחיד — לא חוק קולון.\n\n"
            "**טעות נפוצה:** שימוש ב-$F = kq_1q_2/r^2$ (צריך שני מטענים) במקום "
            "$E = kq/r^2$ (מקור אחד). גם שדה לכיוון מטען חיובי.\n\n"
            "**טיפ לבחינה:** N/C ו-V/m הם יחידות שוות ערך. "
            "אמתו: $(0.2)^2 = 0.04$ מ² ו-$5\\times10^{-6}$ C במונה. "
            "כיוון: הרחק מהמטען החיובי."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Opposite-sign charges attract. Using magnitudes:\n"
            "$$F = 9\\times10^9 \\times \\frac{(6\\times10^{-6})^2}{(0.3)^2} = "
            "9\\times10^9 \\times \\frac{36\\times10^{-12}}{0.09} = \\boxed{3.6\\,\\text{N}}$$\n"
            "Signs are opposite → **attractive** force.\n\n"
            "**How to think about it:** The magnitude formula uses $|q_1||q_2|$ regardless of sign. "
            "Attraction vs. repulsion is determined by whether the product $q_1 q_2$ is negative or positive.\n\n"
            "**Common slip:** Answering \"repulsive\" because both magnitudes are equal, "
            "or forgetting that opposite signs always attract.\n\n"
            "**Exam tip:** Always state both magnitude AND direction (attractive/repulsive) "
            "when the question asks \"Is it attractive or repulsive?\" "
            "Verify: $(6\\times10^{-6})^2 = 36\\times10^{-12}$ and $(0.3)^2 = 0.09$."
        ),
        "explanation_he": (
            "**למה זה נכון:** מטענים בסימנים מנוגדים מושכים. עם גדלים:\n"
            "$$F = 9\\times10^9 \\times \\frac{(6\\times10^{-6})^2}{(0.3)^2} = \\boxed{3.6\\,\\text{N}}$$\n"
            "סימנים מנוגדים → כוח **מושך**.\n\n"
            "**איך לחשוב:** נוסחת הגודל משתמשת ב-$|q_1||q_2|$ ללא קשר לסימן. "
            "משיכה מול דחייה נקבעת לפי האם המכפלה $q_1 q_2$ שלילית או חיובית. "
            "כאן $q_1 q_2 < 0$ → משיכה.\n\n"
            "**טעות נפוצה:** \"דחייה\" כי שני הגדלים שווים, "
            "או שכחה שסימנים מנוגדים תמיד מושכים. גם שכחת המרת $\\mu\\text{C}$.\n\n"
            "**טיפ לבחינה:** תמיד ציינו גודל **וגם** כיוון (משיכה/דחייה). "
            "אמתו: $(6\\times10^{-6})^2 = 36\\times10^{-12}$ ו-$(0.3)^2 = 0.09$. "
            "תשובה: 3.6 N, כוח משיכה בין מטענים מנוגדים."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** The relationship between force and field is $F = qE$, "
            "so $E = F/q$:\n"
            "$$E = \\frac{0.4}{2\\times10^{-6}} = \\boxed{2\\times10^5\\,\\text{N/C}}$$\n\n"
            "**How to think about it:** Field is force per unit charge. A $+2\\,\\mu\\text{C}$ charge "
            "experiencing 0.4 N means the field strength is $0.4 / (2\\times10^{-6})$ N/C. "
            "This works regardless of the charge's sign — $|q|$ in the denominator if using magnitudes.\n\n"
            "**Common slip:** Dividing by $2$ instead of $2\\times10^{-6}$, or confusing "
            "$E = F/q$ with $F = kq_1q_2/r^2$.\n\n"
            "**Exam tip:** Check units: N divided by C gives N/C — the correct field unit. "
            "Sanity check: a few newtons on a microcoulomb charge implies a strong field."
        ),
        "explanation_he": (
            "**למה זה נכון:** הקשר בין כוח לשדה הוא $F = qE$, לכן $E = F/q$:\n"
            "$$E = \\frac{0.4}{2\\times10^{-6}} = \\boxed{2\\times10^5\\,\\text{N/C}}$$\n\n"
            "**איך לחשוב:** שדה = כוח ליחידת מטען. מטען $+2\\,\\mu\\text{C}$ "
            "שחווה 0.4 N אומר שעוצמת השדה היא $0.4 / (2\\times10^{-6})$ N/C. "
            "זה עובד בלי קשר לסימן המטען — השדה קיים גם בלי המטען.\n\n"
            "**טעות נפוצה:** חלוקה ב-2 במקום $2\\times10^{-6}$, או בלבול "
            "$E = F/q$ עם $F = kq_1q_2/r^2$. גם שכחת המרת $\\mu\\text{C}$.\n\n"
            "**טיפ לבחינה:** בדקו יחידות: N חלקי C = N/C. "
            "בדיקת הגיון: כמה ניוטונים על מטען מיקרו-קולום = שדה חזק."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At $x = 0.1\\,\\text{m}$, compute each field separately:\n"
            "$$E_1 = k\\frac{4\\times10^{-6}}{(0.1)^2} = 3.6\\times10^6\\,\\text{N/C}\\text{ (+x)}$$\n"
            "$$E_2 = k\\frac{4\\times10^{-6}}{(0.3)^2} = 4\\times10^5\\,\\text{N/C}\\text{ (−x)}$$\n"
            "$$E_{\\text{net}} = 3.6\\times10^6 - 4\\times10^5 = \\boxed{3.2\\times10^6\\,\\text{N/C (+x)}}$$\n\n"
            "**How to think about it:** Both sources are positive, so each field points away from its charge. "
            "At $x=0.1$, the left charge is closer → stronger field in $+x$.\n\n"
            "**Common slip:** Adding magnitudes without considering opposite directions, "
            "or using wrong distances ($0.1$ from $q_1$, $0.3$ from $q_2$ instead of $0.3$ and $0.1$).\n\n"
            "**Exam tip:** Label each field with its direction before adding. "
            "Distances: from $q_1$ at $x=0.1$ m is $0.1$ m; from $q_2$ at $x=0.4$ m is $0.3$ m."
        ),
        "explanation_he": (
            "**למה זה נכון:** ב-$x = 0.1\\,\\text{מ'}$, חשבו כל שדה בנפרד:\n"
            "$$E_1 = k\\frac{4\\times10^{-6}}{(0.1)^2} = 3.6\\times10^6\\,\\text{N/C}\\text{ (+x)}$$\n"
            "$$E_2 = k\\frac{4\\times10^{-6}}{(0.3)^2} = 4\\times10^5\\,\\text{N/C}\\text{ (−x)}$$\n"
            "$$E_{\\text{נטו}} = \\boxed{3.2\\times10^6\\,\\text{N/C (+x)}}$$\n\n"
            "**איך לחשוב:** שני המקורות חיוביים, לכן כל שדה מתרחק ממטענו. "
            "ב-$x=0.1$, המטען השמאלי קרוב יותר → שדה חזק יותר ב-$+x$. "
            "זו בעיית סופרפוזיציה קלאסית על קו.\n\n"
            "**טעות נפוצה:** חיבור גדלים בלי לקחת בחשבון כיוונים מנוגדים, "
            "או מרחקים שגויים ($0.3$ מ-$q_2$ ולא $0.1$).\n\n"
            "**טיפ לבחינה:** סמנו כיוון לכל שדה לפני החיבור. "
            "מרחקים: מ-$q_1$ ב-$x=0.1$ הוא 0.1 מ'; מ-$q_2$ ב-$x=0.4$ הוא 0.3 מ'."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** For opposite-sign charges, the zero-field point lies "
            "**outside** the pair, on the side of the smaller charge ($+1\\,\\mu\\text{C}$). "
            "At distance $x$ to the left of $q_1$:\n"
            "$$\\frac{k(1)}{x^2} = \\frac{k(4)}{(x+0.6)^2} \\Rightarrow (x+0.6)^2 = 4x^2 "
            "\\Rightarrow x+0.6 = 2x \\Rightarrow \\boxed{x = 0.6\\,\\text{m}}$$\n"
            "The point is at $x = -0.6\\,\\text{m}$ — 0.6 m to the left of $q_1$.\n\n"
            "**How to think about it:** Between opposite charges, both fields point the same way "
            "(no cancellation possible). Outside, on the weaker-charge side, fields oppose.\n\n"
            "**Common slip:** Placing the point between the charges, or using $|q_1|/x = |q_2|/(0.6-x)$ "
            "which applies only to like charges between them.\n\n"
            "**Exam tip:** First decide the region (between vs. outside), then set up the equation. "
            "Verify: at $x=0.6$ m left of $q_1$, both fields point right and cancel."
        ),
        "explanation_he": (
            "**למה זה נכון:** למטענים בסימנים מנוגדים, נקודת אפס-שדה **מחוץ** לזוג, "
            "בצד המטען הקטן ($+1\\,\\mu\\text{C}$). במרחק $x$ משמאל ל-$q_1$:\n"
            "$$\\frac{1}{x^2} = \\frac{4}{(x+0.6)^2} \\Rightarrow x+0.6 = 2x \\Rightarrow x = \\boxed{0.6\\,\\text{מ'}}$$\n"
            "הנקודה ב-$x = -0.6\\,\\text{מ'}$ — 0.6 מ' משמאל ל-$q_1$.\n\n"
            "**איך לחשוב:** בין מטענים מנוגדים, שני השדות באותו כיוון "
            "(אין ביטול אפשרי). מחוץ, בצד המטען החלש, השדות מתנגדים ויכולים להתקזז.\n\n"
            "**טעות נפוצה:** מיקום בין המטענים, או שימוש במשוואה של מטענים דומים "
            "($|q_1|/x = |q_2|/(d-x)$).\n\n"
            "**טיפ לבחינה:** קודם החליטו על האזור (בין / מחוץ), ואז הגדירו משוואה. "
            "אמתו: ב-$x=0.6$ מ' משמאל ל-$q_1$, שני השדות ימינה ומתקזזים."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At the midpoint, each charge is at distance $d/2$:\n"
            "$$E_1 = E_2 = k\\frac{q}{(d/2)^2}$$\n"
            "Both fields have equal magnitude. Since both sources are positive, "
            "each field points **away** from its charge — at the midpoint these directions "
            "are opposite, so:\n"
            "$$\\vec{E}_{\\text{net}} = \\vec{E}_1 + \\vec{E}_2 = 0$$ ∎\n\n"
            "**How to think about it:** This is a symmetry argument. Equal charges at equal "
            "distances produce equal opposing fields. No calculation needed if you recognize the symmetry.\n\n"
            "**Common slip:** Confusing $E=0$ at midpoint (like charges) with a dipole midpoint "
            "where $E \\neq 0$. Another error: adding magnitudes instead of vectors.\n\n"
            "**Exam tip:** Symmetry proofs earn full marks with minimal algebra — state the symmetry first."
        ),
        "explanation_he": (
            "**למה זה נכון:** בנקודת האמצע, כל מטען במרחק $d/2$:\n"
            "$$E_1 = E_2 = k\\frac{q}{(d/2)^2}$$\n"
            "שני השדות בגודל שווה. מכיוון ששני המקורות חיוביים, "
            "כל שדה **מתרחק** ממטענו — בנקודת האמצע הכיוונים מנוגדים:\n"
            "$$\\vec{E}_{\\text{נטו}} = 0$$ ∎\n\n"
            "**איך לחשוב:** זה טיעון סימטריה. מטענים שווים במרחקים שווים "
            "יוצרים שדות שווים ומנוגדים. אין צורך בחישוב אם מזהים סימטריה.\n\n"
            "**טעות נפוצה:** בלבול $E=0$ בנקודת אמצע (מטענים דומים) "
            "עם אמצע דיפול ש-$E \\neq 0$. גם חיבור גדלים במקום וקטורים.\n\n"
            "**טיפ לבחינה:** הוכחות סימטריה מקבלות ציון מלא עם מינימום אלגברה — "
            "ציינו את הסימטריה קודם."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Coulomb's law gives $F \\propto 1/r^2$. "
            "If distance is tripled ($r' = 3r$):\n"
            "$$F' = k\\frac{q_1 q_2}{(3r)^2} = \\frac{1}{9} \\cdot k\\frac{q_1 q_2}{r^2} = \\frac{F}{9}$$\n"
            "The force **decreases by a factor of 9**.\n\n"
            "**How to think about it:** Inverse-square means doubling distance divides force by 4, "
            "tripling divides by 9, halving multiplies by 4. Use ratio reasoning before plugging numbers.\n\n"
            "**Common slip:** Answering \"decreases by factor 3\" (linear, not inverse-square), "
            "or \"increases by factor 9\" (reversing the relationship).\n\n"
            "**Exam tip:** Memorize: change in $r$ by factor $n$ → force changes by $1/n^2$. "
            "This ratio trick saves time on multiple-choice questions. "
            "Example: halving $r$ multiplies force by 4."
        ),
        "explanation_he": (
            "**למה זה נכון:** חוק קולון נותן $F \\propto 1/r^2$. "
            "אם המרחק משולש ($r' = 3r$):\n"
            "$$F' = \\frac{1}{(3)^2} \\cdot F = \\frac{F}{9}$$\n"
            "הכוח **פוחת פי 9**.\n\n"
            "**איך לחשוב:** ריבוע הפוך אומר שהכפלת מרחק מחלקת כוח ב-4, "
            "שילוש מחלק ב-9, חצייה מכפילה ב-4. השתמשו ביחסים לפני הצבת מספרים — "
            "אין צורך בערכי $q$ או $k$.\n\n"
            "**טעות נפוצה:** \"פוחת פי 3\" (לינארי, לא ריבוע הפוך), "
            "או \"גדל פי 9\" (היפוך הקשר). גם \"פוחת פי 6\" (מכפיל 3 ב-2).\n\n"
            "**טיפ לבחינה:** שמרו: שינוי $r$ בגורם $n$ → כוח משתנה ב-$1/n^2$. "
            "דוגמה: חציית $r$ מכפילה כוח ב-4."
        ),
    },
]


def apply_expansion(data):
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            n = sec.get("example_number")
            sec.update(SECTION_BODIES[f"worked_example_{n}"])
        elif kind == "checkpoint":
            cp_idx += 1
            sec.update(SECTION_BODIES[f"checkpoint_{cp_idx}"])
        elif kind == "method_guide":
            sec.update(SECTION_BODIES["method_guide"])
        elif kind == "exercise_set":
            sec.update(SECTION_BODIES["exercise_set"])
        elif kind == "pitfall":
            sec.update(SECTION_BODIES["pitfall"])
        elif kind == "why_matters":
            sec.update(SECTION_BODIES["why_matters"])
        elif kind == "before_exam":
            sec.update(SECTION_BODIES["before_exam"])
        elif kind == "summary":
            sec.update(SECTION_BODIES["summary"])

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

    return data


def validate_depth(data):
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                issues.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                issues.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if sec.get("body_he_md") and hebrew_body_weak(
                sec.get("body_he_md"), sec.get("body_en_md")
            ):
                issues.append(f"{kind} HE weak parity")
        elif kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            n = sec.get("example_number", "?")
            if en_w < MIN_WORDS["worked_example"]["en"]:
                issues.append(f"worked_example {n} EN: {en_w}")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                issues.append(f"worked_example {n} HE: {he_w}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"worked_example {n} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"q{q['ord']} {key}: {w} words")
            if lang == "he" and hebrew_body_weak(
                q.get("explanation_he"), q.get("explanation_en")
            ):
                issues.append(f"q{q['ord']} expl-he-weak")

    return issues


def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("VALIDATION FAILED:")
        for i in issues:
            print(" ", i)
        sys.exit(1)

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    print("All depth gates OK; seed-lessons dry-run passed.")


if __name__ == "__main__":
    main()
