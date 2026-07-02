#!/usr/bin/env python3
"""Expand electric_potential.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/electric_potential.json"

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
            "When you plug in a phone charger, you are connecting two points at **different "
            "electric potentials** — and charges flow because of that difference. "
            "Electric potential $V$ tells you how much **potential energy per unit charge** "
            "a point in space has, measured in volts (V = J/C).\n\n"
            "Unlike the electric field $\\vec{E}$ (a vector pointing toward decreasing $V$), "
            "potential is a **scalar** — you add contributions from multiple charges "
            "algebraically, without worrying about direction. This makes multi-charge "
            "problems much easier than field superposition.\n\n"
            "In Bagrut physics (5 units), you will:\n"
            "- Calculate $V = kQ/r$ for point charges and use **superposition**.\n"
            "- Find **work** moving charges: $W = q\\Delta V$.\n"
            "- Relate field to potential: $\\vec{E} = -\\nabla V$ (field points down the gradient).\n"
            "- Locate **zero-potential points** and compute **energy to assemble** charge configurations.\n\n"
            "This lesson builds on `concept:electric_field` and unlocks `concept:electric_circuits`. "
            "Master the sign of $Q$ in $V = kQ/r$ before attempting capacitor or circuit problems."
        ),
        "body_he_md": (
            "כשמחברים מטען לטלפון, מחברים שתי נקודות ב**פוטנציאל חשמלי שונה** — "
            "ומטענים זורמים בגלל ההפרש. "
            "הפוטנציאל החשמלי $V$ מודד **אנרגיה פוטנציאלית ליחידת מטען** "
            "בנקודה במרחב, ביחידות וולט (V = J/C).\n\n"
            "בניגוד לשדה החשמלי $\\vec{E}$ (וקטור שמצביע לכיוון ירידת $V$), "
            "הפוטנציאל הוא **סקalar** — מחברים תרומות ממטענים רבים "
            "אלגברית, בלי לדאוג לכיוון. זה מקל משמעותית על בעיות ריבוי מטענים "
            "לעומת סופרפוזיציה של שדות.\n\n"
            "בבגרות בפיזיקה (5 יחידות), תצטרכו:\n"
            "- לחשב $V = kQ/r$ למטענים נקודתיים ולהשתמש ב**סופרפוזיציה**.\n"
            "- למצוא **עבודה** בהעברת מטענים: $W = q\\Delta V$.\n"
            "- לקשר שדה לפוטנציאל: $\\vec{E} = -\\nabla V$ (השדה לכיוון ירידת הפוטנציאל).\n"
            "- לאתר **נקודות פוטנציאל אפס** ולחשב **אנרגיה להרכבת** תצורות מטען.\n\n"
            "שיעור זה מבוסס על `concept:electric_field` ופותח את `concept:electric_circuits`. "
            "שלטו בסימן $Q$ ב-$V = kQ/r$ לפני בעיות מאמצים ומעגלים."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Point charge potential** (reference $V=0$ at infinity):\n"
            "$$V=k\\frac{Q}{r}\\quad [V=\\text{volts}=\\text{J/C}],\\quad "
            "k=9\\times10^9\\,\\text{N·m}^2/\\text{C}^2.$$\n"
            "Positive $Q$ creates positive $V$ nearby; negative $Q$ creates negative $V$.\n\n"
            "**Potential difference** between points A and B:\n"
            "$$\\Delta V=V_B-V_A.$$\n"
            "This is the work per unit charge needed to move a test charge from A to B.\n\n"
            "**Work moving charge $q$** (by an external agent, no other forces):\n"
            "$$W_{A\\to B}=q\\Delta V=q(V_B-V_A).$$\n"
            "Positive work means the external agent pushes the charge \"uphill\" in potential.\n\n"
            "**Field from potential** (fundamental relation):\n"
            "$$\\vec{E}=-\\nabla V\\quad\\Rightarrow\\quad "
            "E=-\\frac{dV}{dr}\\text{ (radial symmetry)}.$$\n"
            "The field points toward **decreasing** $V$ — like water flowing downhill.\n\n"
            "**Superposition:** $V_{\\text{total}}=\\sum V_i$ (scalars add algebraically). "
            "Never add $\\vec{E}$ magnitudes when you mean potential — they are different quantities.\n\n"
            "**Relationship to potential energy:** A charge $q$ at potential $V$ has "
            "potential energy $U = qV$. For two point charges, $U = kq_1 q_2/r$ — "
            "the product of charge and potential at that location."
        ),
        "body_he_md": (
            "**פוטנציאל ממטען נקודתי** (ייחוס $V=0$ באינסוף):\n"
            "$$V=k\\frac{Q}{r}\\quad [V=\\text{וולט}=\\text{J/C}],\\quad "
            "k=9\\times10^9\\,\\text{N·m}^2/\\text{C}^2.$$\n"
            "מטען חיובי $Q$ יוצר $V$ חיובי בקרבתו; מטען שלילי יוצר $V$ שלילי.\n\n"
            "**הפרש פוטנציאל** בין נקודות A ו-B:\n"
            "$$\\Delta V=V_B-V_A.$$\n"
            "זו העבודה ליחידת מטען להעברת מטען בדיקה מ-A ל-B.\n\n"
            "**עבודה בהעברת מטען $q$** (על ידי סוכן חיצוני, בלי כוחות אחרים):\n"
            "$$W_{A\\to B}=q\\Delta V=q(V_B-V_A).$$\n"
            "עבודה חיובית = הסוכן החיצוני דוחף את המטען \"במעלה\" בפוטנציאל.\n\n"
            "**שדה מפוטנציאל** (קשר יסודי):\n"
            "$$\\vec{E}=-\\nabla V\\quad\\Rightarrow\\quad "
            "E=-\\frac{dV}{dr}\\text{ (בסימטריה כדורית)}.$$\n"
            "השדה מצביע לכיוון **ירידת** $V$ — כמו מים שזורמים במורד.\n\n"
            "**סופרפוזיציה:** $V_{\\text{כולל}}=\\sum V_i$ (סקalars מתחברים אלגברית). "
            "אל תחברו גדלי $\\vec{E}$ כשהכוונה היא פוטנציאל — אלה כמויות שונות.\n\n"
            "**קשר לאנרגיה פוטנציאלית:** מטען $q$ בפוטנציאל $V$ בעל "
            "אנרגיה פוטנציאלית $U = qV$. לשני מטענים נקודתיים, $U = kq_1 q_2/r$ — "
            "מכפלת המטען בפוטנציאל באותו מיקום."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Equipotential surfaces\n\n"
            "Surfaces where $V$ is constant are called **equipotential surfaces**. "
            "Moving a charge along such a surface requires zero work ($dW = q\\,dV = 0$). "
            "Therefore $\\vec{E}$ is always **perpendicular** to equipotential surfaces — "
            "no component of force along the surface.\n\n"
            "### Sign convention and zero-potential points\n\n"
            "For two opposite charges on the $x$-axis, there exists a finite point "
            "(not at infinity) where $V_1 + V_2 = 0$. Set $kQ_1/x + kQ_2/(d-x) = 0$ "
            "and solve for position. For two **like** charges, $V$ is never zero between them "
            "— both contributions have the same sign.\n\n"
            "### Assembling charge configurations\n\n"
            "Work to bring charge $q_i$ from infinity to its final position, with all "
            "other charges already in place:\n"
            "$$W_i = q_i V_{\\text{others at }i}.$$\n"
            "Total stored energy: $W_{\\text{total}} = \\sum W_i$. "
            "The first charge placed requires zero work (no other charges yet).\n\n"
            "### Field direction from potential gradient\n\n"
            "If $V$ **decreases** in the $+x$ direction, then $E_x = -dV/dx > 0$ — "
            "the field points in $+x$. Always check: field points toward lower potential.\n\n"
            "**Units checklist:** $V$ in volts, $W$ in joules, $q$ in coulombs, $r$ in meters."
        ),
        "body_he_md": (
            "### משטחי פוטנציאל קבוע (equipotential)\n\n"
            "משטחים שבהם $V$ קבוע נקראים **משטחי equipotential**. "
            "העברת מטען לאורך משטח כזה דורשת אפס עבודה ($dW = q\\,dV = 0$). "
            "לכן $\\vec{E}$ תמיד **מאונך** למשטחי equipotential — "
            "אין רכיב כוח לאורך המשטח.\n\n"
            "### סימן ונקודות פוטנציאל אפס\n\n"
            "לשני מטענים מנוגדים על ציר $x$, קיימת נקודה סופית "
            "(לא באינסוף) שבה $V_1 + V_2 = 0$. הגדירו $kQ_1/x + kQ_2/(d-x) = 0$ "
            "ופתרו למיקום. לשני מטענים **דומים**, $V$ לעולם לא אפס ביניהם — "
            "שתי התרומות באותו סימן.\n\n"
            "### הרכבת תצורות מטען\n\n"
            "עבודה להבאת $q_i$ מאינסוף למיקום הסופי, כששאר המטענים כבר במקום:\n"
            "$$W_i = q_i V_{\\text{אחרים ב-}i}.$$\n"
            "אנרגיה אגורה כוללת: $W_{\\text{כולל}} = \\sum W_i$. "
            "המטען הראשון שמונח דורש אפס עבודה (אין עדיין מטענים אחרים).\n\n"
            "### כיוון שדה מגרדיאנט הפוטנציאל\n\n"
            "אם $V$ **יורד** בכיוון $+x$, אז $E_x = -dV/dx > 0$ — "
            "השדה בכיוון $+x$. תמיד בדקו: השדה לכיוון פוטנציאל נמוך יותר.\n\n"
            "**רשימת יחידות:** $V$ בוולט, $W$ בג'oule, $q$ בקולומים, $r$ במטרים."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** Point charge $Q=+5\\,\\mu\\text{C}=5\\times10^{-6}$ C at origin. "
            "Find $V$ at $r=0.3$ m.\n\n"
            "### Move 1: Identify formula and convert units\n"
            "Use $V=kQ/r$ with $k=9\\times10^9$ N·m²/C². "
            "Charge is already converted: $Q = 5\\times10^{-6}$ C.\n\n"
            "### Move 2: Substitute\n"
            "$$V=(9\\times10^9)(5\\times10^{-6})/0.3.$$\n\n"
            "### Move 3: Compute numerator\n"
            "Numerator: $(9\\times10^9)(5\\times10^{-6}) = 45\\times10^3 = 4.5\\times10^4$.\n\n"
            "### Move 4: Divide and interpret\n"
            "$$V=4.5\\times10^4/0.3=1.5\\times10^5\\text{ V}=150\\text{ kV}.$$\n"
            "Positive $Q$ → positive $V$ at all finite distances.\n\n"
            "### Move 5: Sanity check with scaling\n"
            "Since $V \\propto 1/r$, doubling distance to $r = 0.6$ m gives $V = 75$ kV. "
            "This confirms our arithmetic is consistent with the inverse-distance law.\n\n"
            "**Answer:** $V=1.5\\times10^5$ V $=150$ kV.\n\n"
            "**Self-check:** $V \\propto 1/r$ — halving distance doubles potential. "
            "If you got 150 V instead of 150 kV, check the $\\mu$C conversion.\n\n"
            "**Bagrut context:** Single-charge potential problems often appear as part (a) "
            "of a longer question linking to work or field. Always include units (V or kV). "
            "Compare with field at the same point: $E = kQ/r^2 = 1.5\\times10^6$ N/C here — "
            "note the $1/r$ vs $1/r^2$ scaling difference between $V$ and $E$. "
            "At double the distance ($r = 0.6$ m), $V$ would drop to 75 kV."
        ),
        "body_he_md": (
            "**נתון:** מטען נקודתי $Q=+5\\,\\mu\\text{C}=5\\times10^{-6}$ C במקור. "
            "מצאו $V$ ב-$r=0.3$ m.\n\n"
            "### צעד 1: זיהוי נוסחה והמרת יחידות\n"
            "השתמשו ב-$V=kQ/r$ עם $k=9\\times10^9$ N·m²/C². "
            "המטען כבר מומר: $Q = 5\\times10^{-6}$ C.\n\n"
            "### צעד 2: הצבה\n"
            "$$V=(9\\times10^9)(5\\times10^{-6})/0.3.$$\n\n"
            "### צעד 3: חישוב מונה\n"
            "מונה: $(9\\times10^9)(5\\times10^{-6}) = 45\\times10^3 = 4.5\\times10^4$.\n\n"
            "### צעד 4: חלוקה ופרשנות\n"
            "$$V=4.5\\times10^4/0.3=1.5\\times10^5\\text{ V}=150\\text{ kV}.$$\n"
            "מטען חיובי $Q$ → $V$ חיובי בכל מרחק סופי.\n\n"
            "### צעד 5: בדיקת הגיון עם קנה מידה\n"
            "מכיוון ש-$V \\propto 1/r$, הכפלת מרחק ל-$r = 0.6$ m נותנת $V = 75$ kV. "
            "זה מאשר שהחשבון עקבי עם חוק המרחק ההפוך.\n\n"
            "**תשובה:** $V=1.5\\times10^5$ V $=150$ kV.\n\n"
            "**בדיקה:** $V \\propto 1/r$ — חציית מרחק מכפילה פוטנציאל. "
            "אם קיבלתם 150 V במקום 150 kV — בדקו המרת $\\mu$C.\n\n"
            "**הקשר בגרות:** בעיות פוטנציאל ממטען בודד מופיעות לעיתים כחלק (א) "
            "בשאלה ארוכה שמקשרת לעבודה או שדה. כללו תמיד יחידות (V או kV). "
            "השוו לשדה באותה נקודה: $E = kQ/r^2 = 1.5\\times10^6$ N/C — "
            "שימו לב להבדל $1/r$ לעומת $1/r^2$ בין $V$ ל-$E$. "
            "במרחק כפול ($r = 0.6$ m), $V$ ירד ל-75 kV."
        ),
    },
    "checkpoint_1": {
        "body_en_md": (
            "**Practice now:** Find $V$ at $r=0.2$ m from $Q=+2\\,\\mu\\text{C}$.\n\n"
            "This is a direct application of $V = kQ/r$. Convert $2\\,\\mu\\text{C} = "
            "2\\times10^{-6}$ C before substituting. The charge is positive, so $V$ will "
            "be positive at every finite distance.\n\n"
            "Use $k = 9\\times10^9$ N·m²/C². Compute the numerator first, then divide "
            "by $r = 0.2$ m. Expected answer is on the order of $10^4$ V (tens of kV).\n\n"
            "Try the calculation yourself before opening the solution. On Bagrut exams, "
            "write the formula $V = kQ/r$ before numbers to earn partial credit. "
            "After finding $V$, verify units: J/C = V."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** מצאו $V$ ב-$r=0.2$ m מ-$Q=+2\\,\\mu\\text{C}$.\n\n"
            "זה יישום ישיר של $V = kQ/r$. המירו $2\\,\\mu\\text{C} = "
            "2\\times10^{-6}$ C לפני הצבה. המטען חיובי, לכן $V$ "
            "יהיה חיובי בכל מרחק סופי.\n\n"
            "השתמשו ב-$k = 9\\times10^9$ N·m²/C². חשבו קודם את המונה, ואז חלקו "
            "ב-$r = 0.2$ m. התשובה הצפויה בסדר גודל של $10^4$ V (עשרות kV).\n\n"
            "נסו לחשב לבד לפני שפותחים את הפתרון. בבגרות, כתבו $V = kQ/r$ לפני מספרים "
            "לנקודות חלקיות. אחרי מציאת $V$, אמתו יחידות: J/C = V."
        ),
        "checkpoint_solution_en": (
            "Find $V$ at $r=0.2$ m from $Q=+2\\,\\mu\\text{C}$.\n\n"
            "**Step 1:** Convert: $Q = 2\\times10^{-6}$ C, $r = 0.2$ m.\n"
            "**Step 2:** Formula: $V = kQ/r$ with $k = 9\\times10^9$.\n\n"
            "$$V=(9\\times10^9)(2\\times10^{-6})/0.2=9\\times10^4\\text{ V}=90\\text{ kV}.$$\n\n"
            "**Verify:** Positive charge → positive $V$. Magnitude ~90 kV is reasonable "
            "for microcoulomb charge at 0.2 m.\n\n"
            "**Answer:** $V = 9\\times10^4$ V $= 90$ kV."
        ),
        "checkpoint_solution_he": (
            "מצאו $V$ ב-$r=0.2$ m מ-$Q=+2\\,\\mu\\text{C}$.\n\n"
            "**שלב 1:** המרה: $Q = 2\\times10^{-6}$ C, $r = 0.2$ m.\n"
            "**שלב 2:** נוסחה: $V = kQ/r$ עם $k = 9\\times10^9$.\n\n"
            "$$V=(9\\times10^9)(2\\times10^{-6})/0.2=9\\times10^4\\text{ V}=90\\text{ kV}.$$\n\n"
            "**אימות:** מטען חיובי → $V$ חיובי. גודל ~90 kV סביר "
            "למטען במיקрокולום ב-0.2 m.\n\n"
            "**תשובה:** $V = 9\\times10^4$ V $= 90$ kV."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** $Q_1=+4\\,\\mu\\text{C}$ at $x=0$, $Q_2=-1\\,\\mu\\text{C}$ at "
            "$x=0.3$ m (on x-axis).\n\n"
            "### Move 1: Set up the zero-potential condition\n"
            "Let the zero-potential point be at distance $x$ from $Q_1$ "
            "(between charges: $0 < x < 0.3$).\n\n"
            "### Move 2: Write superposition equation\n"
            "Set $V_1+V_2=0$: $kQ_1/x + kQ_2/(0.3-x)=0$.\n\n"
            "### Move 3: Cancel $k$ and solve\n"
            "$$\\frac{4}{x} = \\frac{1}{0.3-x} \\Rightarrow 4(0.3-x)=x \\Rightarrow 1.2=5x.$$\n\n"
            "### Move 4: Find position\n"
            "$$x=0.24\\text{ m from }Q_1\\text{ (i.e., }0.06\\text{ m from }Q_2).$$\n\n"
            "**Verify:** $|V_1|=|V_2|$ since $|Q_1|/x = |Q_2|/(0.3-x)$. ✓\n\n"
            "**Answer:** $x=0.24$ m from $Q_1$.\n\n"
            "**Exam tip:** The zero-$V$ point lies closer to the **smaller-magnitude** charge. "
            "Check $0 < x < 0.3$ m after solving.\n\n"
            "**Physical picture:** At $x = 0.24$ m, the positive contribution from $+4\\,\\mu\\text{C}$ "
            "exactly cancels the negative contribution from $-1\\,\\mu\\text{C}$. "
            "This is an equipotential **point** on the axis — not a surface in this 1D setup. "
            "Beyond this point, net $V$ is positive on the $+Q$ side and negative on the $-Q$ side."
        ),
        "body_he_md": (
            "**נתון:** $Q_1=+4\\,\\mu\\text{C}$ ב-$x=0$, $Q_2=-1\\,\\mu\\text{C}$ ב-$x=0.3$ m "
            "(על ציר $x$).\n\n"
            "### צעד 1: הגדרת תנאי פוטנציאל אפס\n"
            "יהי נקודת הפוטנציאל האפס במרחק $x$ מ-$Q_1$ "
            "(בין המטענים: $0 < x < 0.3$).\n\n"
            "### צעד 2: משוואת סופרפוזיציה\n"
            "הגדירו $V_1+V_2=0$: $kQ_1/x + kQ_2/(0.3-x)=0$.\n\n"
            "### צעד 3: ביטול $k$ ופתרון\n"
            "$$\\frac{4}{x} = \\frac{1}{0.3-x} \\Rightarrow 4(0.3-x)=x \\Rightarrow 1.2=5x.$$\n\n"
            "### צעד 4: מציאת מיקום\n"
            "$$x=0.24\\text{ m מ-}Q_1\\text{ (כלומר }0.06\\text{ m מ-}Q_2).$$\n\n"
            "**אימות:** $|V_1|=|V_2|$ כי $|Q_1|/x = |Q_2|/(0.3-x)$. ✓\n\n"
            "**תשובה:** $x=0.24$ m מ-$Q_1$.\n\n"
            "**טיפ לבחינה:** נקודת $V=0$ קרובה יותר למטען **בגודל קטן יותר**. "
            "בדקו $0 < x < 0.3$ m אחרי הפתרון.\n\n"
            "**תמונה פיזיקלית:** ב-$x = 0.24$ m, התרומה החיובית מ-$+4\\,\\mu\\text{C}$ "
            "מתקזזת בדיוק עם התרומה השלילית מ-$-1\\,\\mu\\text{C}$. "
            "זו נקודת equipotential על הציר. מעבר לנקודה זו, $V$ נטו חיובי "
            "בצד $+Q$ ושלילי בצד $-Q$."
        ),
    },
    "checkpoint_2": {
        "body_en_md": (
            "**Practice now:** Work to move $q=+3\\,\\mu\\text{C}$ from $V_A=100$ V to $V_B=400$ V?\n\n"
            "Use the work-potential relation $W = q\\Delta V = q(V_B - V_A)$. "
            "The charge is positive and moves to **higher** potential, so the external "
            "agent must do **positive** work.\n\n"
            "Convert $3\\,\\mu\\text{C} = 3\\times10^{-6}$ C. "
            "$\\Delta V = 400 - 100 = 300$ V.\n\n"
            "Try computing $W$ before reading the solution. Expected answer is a fraction "
            "of a millijoule. On Bagrut exams, state the sign of work and include units (J or mJ). "
            "Remember: the electric field does negative work on the charge (it moves \"downhill\"), "
            "while the external agent does positive work to push it \"uphill\" to higher potential."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** עבודה להעברת $q=+3\\,\\mu\\text{C}$ מ-$V_A=100$ V ל-$V_B=400$ V?\n\n"
            "השתמשו בקשר $W = q\\Delta V = q(V_B - V_A)$. "
            "המטען חיובי ועובר לפוטנציאל **גבוה יותר**, לכן הסוכן החיצוני "
            "עושה **עבודה חיובית**.\n\n"
            "המירו $3\\,\\mu\\text{C} = 3\\times10^{-6}$ C. "
            "$\\Delta V = 400 - 100 = 300$ V.\n\n"
            "נסו לחשב $W$ לפני קריאת הפתרון. התשובה הצפויה: שבר של מילי-ג'oule. "
            "בבגרות, ציינו סימן עבודה וכללו יחידות (J או mJ). "
            "זכרו: השדה החשמלי עושה עבודה שלילית על המטען (זז \"במורד\"), "
            "בעוד הסוכן החיצוני עושה עבודה חיובית לדחיפתו \"במעלה\" לפוטנציאל גבוה יותר."
        ),
        "checkpoint_solution_en": (
            "Work to move $q=+3\\,\\mu\\text{C}$ from $V_A=100$ V to $V_B=400$ V?\n\n"
            "**Step 1:** $\\Delta V = V_B - V_A = 400 - 100 = 300$ V.\n"
            "**Step 2:** $q = 3\\times10^{-6}$ C.\n"
            "**Step 3:** $W = q\\Delta V = 3\\times10^{-6} \\times 300 = 9\\times10^{-4}$ J.\n\n"
            "**Verify:** Positive charge moving to higher $V$ → positive work by external agent.\n\n"
            "**Answer:** $W = 9\\times10^{-4}$ J $= 0.9$ mJ."
        ),
        "checkpoint_solution_he": (
            "עבודה להעברת $q=+3\\,\\mu\\text{C}$ מ-$V_A=100$ V ל-$V_B=400$ V?\n\n"
            "**שלב 1:** $\\Delta V = V_B - V_A = 400 - 100 = 300$ V.\n"
            "**שלב 2:** $q = 3\\times10^{-6}$ C.\n"
            "**שלב 3:** $W = q\\Delta V = 3\\times10^{-6} \\times 300 = 9\\times10^{-4}$ J.\n\n"
            "**אימות:** מטען חיובי לפוטנציאל גבוה יותר → עבודה חיובית מסוכן חיצוני.\n\n"
            "**תשובה:** $W = 9\\times10^{-4}$ J $= 0.9$ mJ."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** Place $Q_1=+2\\,\\mu\\text{C}$, $Q_2=+3\\,\\mu\\text{C}$, "
            "$Q_3=-1\\,\\mu\\text{C}$ at corners of equilateral triangle, side $a=0.1$ m.\n\n"
            "### Move 1: Bring $Q_1$ alone\n"
            "$W_1=0$ (no other charges yet).\n\n"
            "### Move 2: Bring $Q_2$ to distance $a$ from $Q_1$\n"
            "Potential at $Q_2$'s location due to $Q_1$: $V = kQ_1/a$.\n"
            "$$W_2 = Q_2 \\cdot kQ_1/a = kQ_1Q_2/a.$$\n\n"
            "### Move 3: Bring $Q_3$ with both present\n"
            "Potential at $Q_3$'s location: $V = kQ_1/a + kQ_2/a$.\n"
            "$$W_3 = Q_3(kQ_1/a + kQ_2/a).$$\n\n"
            "### Move 4: Total work formula\n"
            "$$W=k/a[(Q_1Q_2)+Q_3(Q_1+Q_2)].$$\n\n"
            "### Move 5: Numerical result\n"
            "$$W=(9\\times10^9/0.1)[(2\\times10^{-6})(3\\times10^{-6})+(-10^{-6})(5\\times10^{-6})]"
            "=0.09\\text{ J}.$$\n\n"
            "### Move 6: Verify energy sign\n"
            "Both $W_2 > 0$ (bringing like charges together requires positive work) and "
            "$W_3 < 0$ (negative charge is attracted, so external work is negative). "
            "Net positive energy means the configuration stores electrostatic energy.\n\n"
            "**Answer:** $W=0.09$ J stored in configuration.\n\n"
            "**Exam tip:** Negative $Q_3$ with positive neighbors can reduce total stored energy. "
            "Break down each step: $W_2 = kQ_1Q_2/a = 0.054$ J (repulsive pair), "
            "while $W_3 = Q_3 \\cdot k(Q_1+Q_2)/a = -0.045$ J (negative charge brought in). "
            "The net $0.09$ J is the electrostatic energy stored in this triangle."
        ),
        "body_he_md": (
            "**נתון:** $Q_1=+2\\,\\mu\\text{C}$, $Q_2=+3\\,\\mu\\text{C}$, "
            "$Q_3=-1\\,\\mu\\text{C}$ בפינות משולש שווה-צלעות, צלע $a=0.1$ m.\n\n"
            "### צעד 1: הבאת $Q_1$ לבד\n"
            "$W_1=0$ (אין עדיין מטענים אחרים).\n\n"
            "### צעד 2: הבאת $Q_2$ למרחק $a$ מ-$Q_1$\n"
            "פוטנציאל במיקום $Q_2$ בגלל $Q_1$: $V = kQ_1/a$.\n"
            "$$W_2 = Q_2 \\cdot kQ_1/a = kQ_1Q_2/a.$$\n\n"
            "### צעד 3: הבאת $Q_3$ כששניהם קיימים\n"
            "פוטנציאל במיקום $Q_3$: $V = kQ_1/a + kQ_2/a$.\n"
            "$$W_3 = Q_3(kQ_1/a + kQ_2/a).$$\n\n"
            "### צעד 4: נוסחת עבודה כוללת\n"
            "$$W=k/a[(Q_1Q_2)+Q_3(Q_1+Q_2)].$$\n\n"
            "### צעד 5: תוצאה מספרית\n"
            "$$W=(9\\times10^9/0.1)[(2\\times10^{-6})(3\\times10^{-6})+(-10^{-6})(5\\times10^{-6})]"
            "=0.09\\text{ J}.$$\n\n"
            "### צעד 6: אימות סימן אנרגיה\n"
            "גם $W_2 > 0$ (הבאת מטענים דומים יחד דורשת עבודה חיובית) וגם "
            "$W_3 < 0$ (מטען שלילי נמשך, לכן עבודה חיצונית שלילית). "
            "אנרגיה נטו חיובית = התצורה מאגירה אנרגיה אלקטרוסטטית.\n\n"
            "**תשובה:** $W=0.09$ J אגורה בתצורה.\n\n"
            "**טיפ לבחינה:** $Q_3$ שלילי עם שכנים חיוביים יכול להקטין אנרגיה אגורה. "
            "פרקו כל שלב: $W_2 = kQ_1Q_2/a = 0.054$ J (זוג דוחה), "
            "בעוד $W_3 = Q_3 \\cdot k(Q_1+Q_2)/a = -0.045$ J (מטען שלילי מובא פנימה). "
            "הנטו $0.09$ J הוא האנרגיה האלקטרוסטטית האגורה במשולש."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Situation | Method | Key tip |\n|---|---|---|\n"
            "| Single point charge | $V=kQ/r$ | Keep sign of $Q$ |\n"
            "| Multiple charges | $V=\\sum kQ_i/r_i$ | Scalar sum — no vectors |\n"
            "| Work on charge | $W=q\\Delta V$ | $\\Delta V = V_B - V_A$ |\n"
            "| Find $\\vec{E}$ | $E=-dV/dr$ or $\\vec{E}=-\\nabla V$ | Field points down gradient |\n"
            "| Zero-potential point | Set $\\sum V_i=0$, solve for position | Closer to smaller $|Q|$ |\n"
            "| Assemble configuration | Sum $W_i=q_i V_{\\text{others at }i}$ | First charge: $W=0$ |\n\n"
            "**Step-by-step workflow:** (1) Convert $\\mu$C to C. (2) Identify problem type "
            "from the table. (3) Write formula before numbers. (4) Check sign and units.\n\n"
            "**Exam tip:** Potential adds as scalars; field requires vector sum. "
            "Never confuse $W$ (joules) with $V$ (volts)."
        ),
        "body_he_md": (
            "| מצב | שיטה | טיפ |\n|---|---|---|\n"
            "| מטען נקודתי | $V=kQ/r$ | שמרו סימן $Q$ |\n"
            "| מטענים מרובים | $V=\\sum kQ_i/r_i$ | סכום סקalar — בלי וקטורים |\n"
            "| עבודה על מטען | $W=q\\Delta V$ | $\\Delta V = V_B - V_A$ |\n"
            "| מציאת $\\vec{E}$ | $E=-dV/dr$ או $\\vec{E}=-\\nabla V$ | שדה לכיוון ירידת $V$ |\n"
            "| נקודת $V=0$ | $\\sum V_i=0$, פתרון למיקום | קרוב ל-$|Q|$ קטן יותר |\n"
            "| הרכבת תצורה | סכום $W_i=q_i V_{\\text{אחרים ב-}i}$ | מטען ראשון: $W=0$ |\n\n"
            "**תהליך שלב-אחר-שלב:** (1) המירו $\\mu$C ל-C. (2) זהו סוג בעיה מהטבלה. "
            "(3) כתבו נוסחה לפני מספרים. (4) בדקו סימן ויחידות.\n\n"
            "**טיפ לבחינה:** פוטנציאל מתחבר כסקalars; שדה דורש סכום וקטורי. "
            "אל תבלבלו $W$ (ג'oule) עם $V$ (וולט)."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below in order. **Try each one before opening the "
            "solution** — the reasoning steps matter as much as the final number.\n\n"
            "The set progresses from direct $V = kQ/r$ calculations (easy) through "
            "work-potential relations and zero-$V$ points (medium) to assembly energy, "
            "field-perpendicularity, and electron acceleration (hard).\n\n"
            "For each problem: convert $\\mu$C to C, identify whether you need scalar "
            "superposition or the gradient relation, then check units.\n\n"
            "**Bagrut strategy:** Write the relevant formula before substituting. "
            "Potential problems reward correct sign reasoning — state whether $V$ is "
            "positive or negative at the point of interest."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה לפי הסדר. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "שלבי הנימוק חשובים לא פחות מהמספר הסופי.\n\n"
            "הסדרה מתקדמת מחישובי $V = kQ/r$ ישירים (קל) דרך קשרי עבודה-פוטנציאל "
            "ונקודות $V=0$ (בינוני) לאנרגיית הרכבה, ניצבות שדה, והאצת אלקטרון (קשה).\n\n"
            "בכל בעיה: המירו $\\mu$C ל-C, זהו אם צריך סופרפוזיציה סקalar או קשר גradient, "
            "ואז בדקו יחידות.\n\n"
            "**אסטרטגיה לבגרות:** כתבו נוסחה רלוונטית לפני הצבה. "
            "בעיות פוטנציאל מתגמלות נימוק סימן נכון — ציינו אם $V$ "
            "חיובי או שלילי בנקודה."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting sign of $Q$ in $V=kQ/r$**: Unlike field magnitude formulas, "
            "potential keeps the sign. A $-Q$ charge creates negative $V$ nearby.\n\n"
            "2. **Adding $\\vec{E}$ instead of $V$**: Potential is scalar — use $V=\\sum V_i$. "
            "Field superposition requires vector addition.\n\n"
            "3. **Wrong reference point**: Standard convention is $V=0$ at infinity. "
            "Changing reference shifts all values by a constant but not $\\Delta V$.\n\n"
            "4. **Confusing $W$ and $V$**: Work is $W=q\\Delta V$ (joules), not $W=\\Delta V$. "
            "You must multiply by charge.\n\n"
            "5. **Missing the zero-$V$ point** for two opposite charges: there is always "
            "a finite point (between them) where potentials cancel.\n\n"
            "**Example misconception:** Adding E vectors to find potential.\n\n"
            "**Fix:** Add V scalars algebraically; use vector sum only for $\\vec{E}$."
        ),
        "body_he_md": (
            "1. **שכחת סימן $Q$ ב-$V=kQ/r$**: בניגוד לנוסחאות גודל שדה, "
            "הפוטנציאל שומר סימן. מטען $-Q$ יוצר $V$ שלילי בקרבתו.\n\n"
            "2. **חיבור $\\vec{E}$ במקום $V$**: פוטנציאל הוא סקalar — $V=\\sum V_i$. "
            "סופרפוזיציית שדה דורשת חיבור וקטורי.\n\n"
            "3. **נקודת ייחוס שגויה**: קונבנציה סטנדרטית $V=0$ באינסוף. "
            "שינוי ייחוס מזיז את כל הערכים בקבוע, לא את $\\Delta V$.\n\n"
            "4. **בלבול $W$ ו-$V$**: עבודה = $W=q\\Delta V$ (ג'oule), לא $W=\\Delta V$. "
            "חובה להכפיל במטען.\n\n"
            "5. **החמצת נקודת $V=0$**: לשני מטענים מנוגדים תמיד יש "
            "נקודה סופית (ביניהם) שבה הפוטנציאלים מתקזזים.\n\n"
            "**דוגמת טעות:** חיבור וקטורי של $\\vec{E}$ למציאת פוטנציאל.\n\n"
            "**תיקון:** חברו $V$ סקalars; סכום וקטורי רק ל-$\\vec{E}$."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Electric potential is the bridge between electrostatics and every circuit "
            "you will ever analyze — voltage, batteries, and capacitors all speak the "
            "language of potential difference.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:electric_circuits` **Electric Circuits** (direct prereq)\n"
            "- Capacitor energy $U = \\frac{1}{2}QV$ and stored charge relationships\n\n"
            "**Builds on:**\n"
            "- `concept:electric_field` **Electric Field & Potential**\n"
            "- `concept:integrals_applications` for $V = -\\int \\vec{E}\\cdot d\\vec{l}$\n\n"
            "**Why it matters for exams:** Bagrut potential questions combine $V=kQ/r$, "
            "work calculations, zero-potential geometry, and assembly energy in multi-step "
            "problems. Mastery here transfers directly to Kirchhoff voltage loops and "
            "capacitor problems worth 15–20 points."
        ),
        "body_he_md": (
            "הפוטנציאל החשמלי הוא הגשר בין אלקטרוסטטיקה לכל מעגל "
            "שתנתחו — מתח, סוללות ומאמצים מדברים בשפת הפרש פוטנציאל.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:electric_circuits` **מעגלי חשמל (DC)** (דרישה ישירה)\n"
            "- אנרגיית מאמץ $U = \\frac{1}{2}QV$ וקשרי מטען אגור\n\n"
            "**מבוסס על:**\n"
            "- `concept:electric_field` **שדה חשמלי ופוטנציאל**\n"
            "- `concept:integrals_applications` ל-$V = -\\int \\vec{E}\\cdot d\\vec{l}$\n\n"
            "**למה זה חשוב לבחינות:** שאלות פוטנציאל בבגרות משלבות $V=kQ/r$, "
            "חישובי עבודה, גיאומטריית $V=0$, ואנרגיית הרכבה בבעיות רב-שלביות. "
            "שליטה כאן עוברת ישירות ללולאות מתח של קירכהוף "
            "ובעיות מאמצים בשווי 15–20 נקודות."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Core formulas — say each aloud once:**\n"
            "- $V=kQ/r$; reference $V=0$ at infinity.\n"
            "- $W=q\\Delta V$; positive work = moving $+q$ to higher $V$.\n"
            "- $\\vec{E}=-\\nabla V$; field points toward decreasing $V$.\n"
            "- Superposition: $V_{\\text{total}}=\\sum V_i$ (scalars!).\n"
            "- Assembly: $W_i = q_i V_{\\text{others at }i}$; first charge $W=0$.\n"
            "- Capacitor: $U = \\frac{1}{2}QV$.\n\n"
            "**Quick checks:** Did you keep sign of $Q$? Is $q$ in coulombs? "
            "Did you use $\\Delta V = V_B - V_A$ (not reversed)?\n\n"
            "**Last review:** Solve one checkpoint without looking, then recite "
            "the difference between scalar $V$ sum and vector $\\vec{E}$ sum."
        ),
        "body_he_md": (
            "**נוסחאות מרכזיות — אמרו כל אחת בקול פעם אחת:**\n"
            "- $V=kQ/r$; ייחוס $V=0$ באינסוף.\n"
            "- $W=q\\Delta V$; עבודה חיובית = העברת $+q$ ל-$V$ גבוה יותר.\n"
            "- $\\vec{E}=-\\nabla V$; שדה לכיוון ירידת $V$.\n"
            "- סופרפוזיציה: $V_{\\text{כולל}}=\\sum V_i$ (סקalars!).\n"
            "- הרכבה: $W_i = q_i V_{\\text{אחרים ב-}i}$; מטען ראשון $W=0$.\n"
            "- מאמץ: $U = \\frac{1}{2}QV$.\n\n"
            "**בדיקות מהירות:** שמרתם סימן $Q$? $q$ בקולומים? "
            "השתמשתם ב-$\\Delta V = V_B - V_A$ (לא הפוך)?\n\n"
            "**חזרה אחרונה:** פתרו checkpoint אחד בלי להסתכל, ואז חזרו "
            "על ההבדל בין סכום סקalar של $V$ לסכום וקטורי של $\\vec{E}$."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Electric potential** is energy per unit charge; units: volt (J/C).\n"
            "- $V=kQ/r$ for point charges; **superposition** adds scalars.\n"
            "- Moving charge: $W=q\\Delta V$; sign of work depends on $q$ and $\\Delta V$.\n"
            "- $\\vec{E}$ points toward **decreasing** $V$: $\\vec{E}=-\\nabla V$.\n"
            "- Zero-$V$ points exist for opposite charges; assembly stores energy.\n\n"
            "**Takeaway:** From the problem wording — single charge, work, zero point, "
            "or assembly — you should pick the correct method row before substituting numbers."
        ),
        "body_he_md": (
            "- **פוטנציאל חשמלי** = אנרגיה ליחידת מטען; יחידות: וולט (J/C).\n"
            "- $V=kQ/r$ למטענים נקודתיים; **סופרפוזיציה** מחברת סקalars.\n"
            "- העברת מטען: $W=q\\Delta V$; סימן עבודה תלוי ב-$q$ וב-$\\Delta V$.\n"
            "- $\\vec{E}$ לכיוון **ירידת** $V$: $\\vec{E}=-\\nabla V$.\n"
            "- נקודות $V=0$ קיימות למטענים מנוגדים; הרכבה מאגירה אנרגיה.\n\n"
            "**מסקנה:** מניסוח השאלה — מטען בודד, עבודה, נקודת אפס, "
            "או הרכבה — בחרו שורת שיטה נכונה לפני הצבת מספרים."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:** Work to move charge $q$ is $W = q\\Delta V$. "
            "For a **positive** charge moving from low $V$ to high $V$, "
            "$\\Delta V = V_{\\text{high}} - V_{\\text{low}} > 0$, so $W = q\\Delta V > 0$. "
            "The external agent must push the charge \"uphill\" against the electric force.\n\n"
            "**How to think about it:** Potential is like height in gravity — moving "
            "a positive charge to higher $V$ requires positive external work, "
            "just as lifting a mass requires work against gravity.\n\n"
            "**Common slip:** Answering \"Negative\" (confusing with the electric field's "
            "work on the charge) or \"Zero\" (thinking no force means no work). "
            "The field does negative work; the external agent does positive work.\n\n"
            "**Exam tip:** $W_{\\text{ext}} = q\\Delta V$. Same $\\Delta V$ with negative "
            "$q$ gives opposite sign of work. Always identify charge sign first."
        ),
        "explanation_he": (
            "**למה זה נכון:** עבודה להעברת מטען $q$ היא $W = q\\Delta V$. "
            "למטען **חיובי** שעובר מ-$V$ נמוך ל-$V$ גבוה, "
            "$\\Delta V = V_{\\text{גבוה}} - V_{\\text{נמוך}} > 0$, לכן $W = q\\Delta V > 0$. "
            "הסוכן החיצוני חייב לדחוף את המטען \"במעלה\" נגד הכוח החשמלי.\n\n"
            "**איך לחשוב:** פוטנציאל כמו גובה בכבידה — העברת מטען חיובי "
            "ל-$V$ גבוה יותר דורשת עבודה חיצונית חיובית, "
            "כמו הרמת מסה נגד כוח הכבידה.\n\n"
            "**טעות נפוצה:** \"שלילית\" (בלבול עם עבודת השדה על המטען) "
            "או \"אפס\" (חשיבה שאין כוח = אין עבודה). "
            "השדה עושה עבודה שלילית; הסוכן החיצוני עושה עבודה חיובית.\n\n"
            "**טיפ לבחינה:** $W_{\\text{חיצוני}} = q\\Delta V$. אותו $\\Delta V$ "
            "עם $q$ שלילי נותן סימן הפוך. זהו תמיד סימן מטען קודם."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** $V = kQ/r$ with $Q = 1\\times10^{-6}$ C and $r = 0.5$ m:\n"
            "$$V=(9\\times10^9)(10^{-6})/0.5=1.8\\times10^4\\text{ V}$$\n"
            "Positive charge → positive potential.\n\n"
            "**How to think about it:** Convert $\\mu$C to C first ($1\\,\\mu\\text{C} = 10^{-6}$ C). "
            "Potential falls as $1/r$, not $1/r^2$ like field magnitude. "
            "At twice the distance, $V$ would halve to $9\\times10^3$ V.\n\n"
            "**Common slip:** Forgetting the $10^{-6}$ conversion (getting $1.8\\times10^{10}$ V), "
            "or using $V = kQ/r^2$ (confusing with field formula).\n\n"
            "**Exam tip:** Write $V = kQ/r$ before substituting. Check: "
            "numerator $9\\times10^3$, divided by 0.5 gives $1.8\\times10^4$ V. "
            "Include units in the final answer."
        ),
        "explanation_he": (
            "**למה זה נכון:** $V = kQ/r$ עם $Q = 1\\times10^{-6}$ C ו-$r = 0.5$ m:\n"
            "$$V=(9\\times10^9)(10^{-6})/0.5=1.8\\times10^4\\text{ V}$$\n"
            "מטען חיובי → פוטנציאל חיובי.\n\n"
            "**איך לחשוב:** המירו $\\mu$C ל-C קודם ($1\\,\\mu\\text{C} = 10^{-6}$ C). "
            "פוטנציאל יורד כ-$1/r$, לא $1/r^2$ כמו גודל שדה. "
            "במרחק כפול, $V$ ירד ל-$9\\times10^3$ V.\n\n"
            "**טעות נפוצה:** שכחת המרת $10^{-6}$ (קבלת $1.8\\times10^{10}$ V), "
            "או שימוש ב-$V = kQ/r^2$ (בלבול עם נוסחת שדה).\n\n"
            "**טיפ לבחינה:** כתבו $V = kQ/r$ לפני הצבה. בדיקה: "
            "מונה $9\\times10^3$, חלוקה ב-0.5 נותנת $1.8\\times10^4$ V. "
            "כללו יחידות בתשובה הסופית."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Work is $W = q\\Delta V$. "
            "With $q = 2\\times10^{-6}$ C and $\\Delta V = 50$ V:\n"
            "$$W = 2\\times10^{-6} \\times 50 = 10^{-4}\\text{ J}$$\n\n"
            "**How to think about it:** $\\Delta V$ is given directly — no need for $k$ or $r$. "
            "Convert $\\mu$C to C, multiply by voltage difference, get joules. "
            "This is the simplest link between electrostatics and energy.\n\n"
            "**Common slip:** Reporting $50$ J (forgetting to multiply by $q$), "
            "or getting $5\\times10^{-2}$ J (using $2\\,\\mu\\text{C}$ without converting). "
            "Another error: using $W = qV$ instead of $W = q\\Delta V$ when two potentials are given.\n\n"
            "**Exam tip:** Units check: C · V = J. If answer is not in joules, "
            "re-check the $\\mu$C conversion."
        ),
        "explanation_he": (
            "**למה זה נכון:** עבודה = $W = q\\Delta V$. "
            "עם $q = 2\\times10^{-6}$ C ו-$\\Delta V = 50$ V:\n"
            "$$W = 2\\times10^{-6} \\times 50 = 10^{-4}\\text{ J}$$\n\n"
            "**איך לחשוב:** $\\Delta V$ ניתן ישירות — אין צורך ב-$k$ או $r$. "
            "המירו $\\mu$C ל-C, הכפילו בהפרש מתח, קבלו ג'oule. "
            "זה הקשר הפשוט ביותר בין אלקטרוסטטיקה לאנרגיה.\n\n"
            "**טעות נפוצה:** דיווח $50$ J (שכחת הכפלה ב-$q$), "
            "או $5\\times10^{-2}$ J (שימוש ב-$2\\,\\mu\\text{C}$ בלי המרה). "
            "גם $W = qV$ במקום $W = q\\Delta V$ כשניתנים שני פוטנציאלים.\n\n"
            "**טיפ לבחינה:** בדיקת יחידות: C · V = J. אם התשובה לא בג'oule, "
            "בדקו שוב המרת $\\mu$C."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At any point between two equal $+Q$ charges, "
            "both contributions $V_1 = kQ/r_1$ and $V_2 = kQ/r_2$ are **positive** "
            "(positive charge, finite distance). Their sum is always positive — "
            "$V = 0$ is **not** possible between them.\n\n"
            "**How to think about it:** Zero potential requires opposite signs to cancel. "
            "Two like charges always add positive (or both negative) contributions. "
            "Contrast with opposite charges, where a zero point exists between them.\n\n"
            "**Common slip:** Answering \"Yes\" by symmetry (confusing with field zero "
            "at midpoint of equal like charges, where $E=0$ but $V \\neq 0$).\n\n"
            "**Exam tip:** $V=0$ between charges → they must be opposite. "
            "$E=0$ between like charges → possible at midpoint. "
            "Do not confuse these two different zero conditions."
        ),
        "explanation_he": (
            "**למה זה נכון:** בכל נקודה בין שני מטענים $+Q$ שווים, "
            "שתי התרומות $V_1 = kQ/r_1$ ו-$V_2 = kQ/r_2$ **חיוביות** "
            "(מטען חיובי, מרחק סופי). הסכום תמיד חיובי — "
            "$V = 0$ **לא** אפשרי ביניהם.\n\n"
            "**איך לחשוב:** פוטנציאל אפס דורש סימנים מנוגדים לביטול. "
            "שני מטענים דומים תמיד מוסיפים תרומות חיוביות (או שניהם שליליות). "
            "השוו למטענים מנוגדים, שבהם קיימת נקודת אפס.\n\n"
            "**טעות נפוצה:** \"כן\" לפי סימטריה (בלבול עם $E=0$ "
            "באמצע מטענים חיוביים שווים, שם $E=0$ אך $V \\neq 0$).\n\n"
            "**טיפ לבחינה:** $V=0$ בין מטענים → חייבים להיות מנוגדים. "
            "$E=0$ בין מטענים דומים → אפשרי באמצע. "
            "אל תבלבלו בין שני תנאי האפס."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** The SI unit of electric potential is the **volt (V)**, "
            "defined as one joule per coulomb: $1\\;\\text{V} = 1\\;\\text{J/C}$. "
            "Potential measures energy per unit charge at a point in space.\n\n"
            "**How to think about it:** Just as field is force per charge (N/C), "
            "potential is energy per charge (J/C). This is a definition question — "
            "no calculation needed.\n\n"
            "**Common slip:** Answering \"joule\" (unit of energy, not potential), "
            "\"newton\" (unit of force), or \"watt\" (unit of power). "
            "Another error: writing N/C, which is the unit of electric field.\n\n"
            "**Exam tip:** Remember the pairs: force/charge = field (N/C); "
            "energy/charge = potential (J/C = V). "
            "Voltage and potential difference share the same unit."
        ),
        "explanation_he": (
            "**למה זה נכון:** יחידת ה-SI לפוטנציאל חשמלי היא **וולט (V)**, "
            "מוגדר כג'oule אחד לקולום: $1\\;\\text{V} = 1\\;\\text{J/C}$. "
            "פוטנציאל מודד אנרגיה ליחידת מטען בנקודה במרחב.\n\n"
            "**איך לחשוב:** כמו ששדה = כוח למטען (N/C), "
            "פוטנציאל = אנרגיה למטען (J/C). שאלת הגדרה — "
            "אין צורך בחישוב.\n\n"
            "**טעות נפוצה:** \"ג'oule\" (יחידת אנרגיה, לא פוטנציאל), "
            "\"ניוטון\" (יחידת כוח), או \"וatt\" (יחידת הספק). "
            "גם N/C — יחידת שדה חשמלי.\n\n"
            "**טיפ לבחינה:** זכרו את הזוגות: כוח/מטען = שדה (N/C); "
            "אנרגיה/מטען = פוטנציאל (J/C = V). "
            "מתח והפרש פוטנציאל חולקים אותה יחידה."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Set $V_1 + V_2 = 0$ on the segment between charges:\n"
            "$$\\frac{kQ_1}{x} + \\frac{kQ_2}{0.4-x} = 0 "
            "\\Rightarrow \\frac{6}{x} = \\frac{2}{0.4-x}$$\n"
            "$$6(0.4-x) = 2x \\Rightarrow 2.4 = 8x \\Rightarrow x = 0.3\\text{ m from }Q_1.$$\n\n"
            "**How to think about it:** Opposite charges guarantee a zero-$V$ point between them. "
            "Cancel $k$, use charge magnitudes with correct signs in the superposition sum. "
            "The point is closer to the smaller charge ($-2\\,\\mu\\text{C}$).\n\n"
            "**Common slip:** Placing the point outside the segment, or using "
            "$|Q_1|/x = |Q_2|/x$ without accounting for opposite signs in $V = kQ/r$.\n\n"
            "**Exam tip:** Verify $0 < x < 0.4$ m. Ratio $|Q_1|:|Q_2| = 3:1$ means "
            "the zero point divides the segment in ratio $\\sqrt{3}:\\sqrt{1}$ from the larger charge."
        ),
        "explanation_he": (
            "**למה זה נכון:** הגדירו $V_1 + V_2 = 0$ על הקטע בין המטענים:\n"
            "$$\\frac{kQ_1}{x} + \\frac{kQ_2}{0.4-x} = 0 "
            "\\Rightarrow \\frac{6}{x} = \\frac{2}{0.4-x}$$\n"
            "$$6(0.4-x) = 2x \\Rightarrow x = 0.3\\text{ m מ-}Q_1.$$\n\n"
            "**איך לחשוב:** מטענים מנוגדים מבטיחים נקודת $V=0$ ביניהם. "
            "בטלו $k$, השתמשו בגדלי מטען עם סימנים נכונים בסכום סופרפוזיציה. "
            "הנקודה קרובה יותר למטען הקטן ($-2\\,\\mu\\text{C}$).\n\n"
            "**טעות נפוצה:** מיקום מחוץ לקטע, או "
            "$|Q_1|/x = |Q_2|/x$ בלי לקחת בחשבון סימנים מנוגדים ב-$V = kQ/r$.\n\n"
            "**טיפ לבחינה:** אמתו $0 < x < 0.4$ m. יחס $|Q_1|:|Q_2| = 3:1$ "
            "אומר שנקודת האפס מחלקת את הקטע ביחס $\\sqrt{3}:\\sqrt{1}$ מהמטען הגדול. "
            "בדקו: ב-$x=0.3$ m, $|V_1| = k\\cdot 6/0.3$ ו-$|V_2| = k\\cdot 2/0.1$ — "
            "שניהם שווים, לכן $V_{\\text{net}} = 0$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** The field-potential relation is $E = -dV/dx$. "
            "If $V$ **decreases** in the $+x$ direction, then $dV/dx < 0$, "
            "so $E = -dV/dx > 0$ — the field points in the **$+x$ direction**.\n\n"
            "**How to think about it:** Electric field always points toward **lower** potential, "
            "like water flowing downhill. Decreasing $V$ to the right means "
            "positive field component in $+x$.\n\n"
            "**Common slip:** Answering $-x$ (reversing the minus sign in $E = -dV/dx$), "
            "or saying \"perpendicular\" (confusing with equipotential surfaces).\n\n"
            "**Exam tip:** Memorize: field points **down** the potential gradient. "
            "Rising $V$ to the right → field points left ($E < 0$). "
            "Falling $V$ to the right → field points right ($E > 0$)."
        ),
        "explanation_he": (
            "**למה זה נכון:** הקשר שדה-פוטנציאל הוא $E = -dV/dx$. "
            "אם $V$ **יורד** בכיוון $+x$, אז $dV/dx < 0$, "
            "לכן $E = -dV/dx > 0$ — השדה בכיוון **$+x$**.\n\n"
            "**איך לחשוב:** שדה חשמלי תמיד מצביע לכיוון פוטנציאל **נמוך יותר**, "
            "כמו מים שזורמים במורד. ירידת $V$ ימינה = רכיב שדה חיובי ב-$+x$.\n\n"
            "**טעות נפוצה:** $-x$ (היפוך הסימן מinus ב-$E = -dV/dx$), "
            "או \"מאונך\" (בלבול עם משטחי equipotential).\n\n"
            "**טיפ לבחינה:** שמרו: שדה לכיוון **ירידת** הפוטנציאל. "
            "$V$ עולה ימינה → שדה שמאלה ($E < 0$). "
            "$V$ יורד ימינה → שדה ימינה ($E > 0$)."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At the center of a dipole (+Q and −Q separated by $d$), "
            "both charges are equidistant. By superposition:\n"
            "$$V = \\frac{kQ}{d/2} + \\frac{k(-Q)}{d/2} = 0.$$\n"
            "Equal and opposite contributions cancel exactly.\n\n"
            "**How to think about it:** This is a symmetry argument — no heavy calculation "
            "needed if you recognize that equal distances with opposite charges give zero net "
            "potential. Contrast with the field at the center, which is **not** zero.\n\n"
            "**Common slip:** Confusing $V=0$ at center with $E=0$ (field at dipole center "
            "points along the axis and is nonzero). Another error: assuming $V=0$ everywhere "
            "on the perpendicular bisector (only true at the exact midpoint).\n\n"
            "**Exam tip:** Dipole center: $V=0$ by symmetry, but $\\vec{E} \\neq 0$. "
            "Always distinguish potential (scalar sum) from field (vector sum)."
        ),
        "explanation_he": (
            "**למה זה נכון:** במרכז דיפול (+Q ו-−Q במרחק $d$), "
            "שני המטענים במרחק שווה. לפי סופרפוזיציה:\n"
            "$$V = \\frac{kQ}{d/2} + \\frac{k(-Q)}{d/2} = 0.$$\n"
            "תרומות שוות ומנוגדות מתקזזות בדיוק.\n\n"
            "**איך לחשוב:** טיעון סימטריה — אין צורך בחישוב כבד "
            "אם מזהים שמרחקים שווים עם מטענים מנוגדים נותנים פוטנציאל נטו אפס. "
            "השוו לשדה במרכז, ש**אינו** אפס.\n\n"
            "**טעות נפוצה:** בלבול $V=0$ במרכז עם $E=0$ (שדה במרכז דיפול "
            "לאורך הציר ואינו אפס). גם הנחה ש-$V=0$ בכל מקום על הציר האמצעי "
            "(נכון רק בנקודת האמצע המדויקת).\n\n"
            "**טיפ לבחינה:** מרכז דיפול: $V=0$ מסימטריה, אך $\\vec{E} \\neq 0$. "
            "הבחינו תמיד בין פוטנציאל (סכום סקalar) לשדה (סכום וקטורי)."
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
