#!/usr/bin/env python3
"""Generate expanded faraday_induction_uni.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/faraday_induction_uni.json"

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
            "Faraday's discovery in 1831 established one of the cornerstones of modern "
            "electromagnetism: a **changing magnetic flux induces an EMF** in any conducting "
            "loop, no matter how the flux changes — by varying field strength, loop area, "
            "orientation, or by moving the conductor through a static field. This single "
            "principle powers electric generators, transformers, inductive sensors, wireless "
            "charging coils, and MRI gradient systems.\n\n"
            "In Israeli university EM courses, Faraday's law is one of Maxwell's four equations "
            "and connects directly to Lenz's law (the minus sign), motional EMF as a special "
            "case of flux change, self- and mutual inductance, and the transient behaviour of "
            "RL circuits. Unlike electrostatics, induction is inherently **dynamic** — a "
            "constant large flux induces **zero** EMF.\n\n"
            "**Exam topics typically covered:**\n"
            "- Faraday's law and Lenz's law (sign and direction)\n"
            "- Motional EMF ($\\mathcal{E} = BLv$)\n"
            "- Self-inductance ($L$) and mutual inductance ($M$)\n"
            "- RL circuits (exponential rise and decay)\n"
            "- Energy stored in magnetic fields\n\n"
            "This lesson builds on magnetic flux from introductory EM and connects forward to "
            "AC circuits and Maxwell's equations in vacuum."
        ),
        "body_he_md": (
            "גילוי פאראדי ב-1831 הניח אבן יסוד באלקטרומגנטיות מודרנית: **שטף מגנטי משתנה "
            "גורם ל-EMF** בכל לולאה מוליכה, לא משנה כיצד השטף משתנה — על ידי שינוי עוצמת "
            "שדה, שטח לולאה, כיוון, או על ידי הזזת המוליך בשדה סטטי. עיקרון יחיד זה מניע "
            "גנרטורים חשמליים, שנאים, חיישנים אינדוקטיביים, טעינה אלחוטית ומערכות MRI.\n\n"
            "בקורסי EM באוניברסיטה, חוק פאראדי הוא אחת מארבע משוואות מקסוול ומתחבר ישירות "
            "לחוק לנץ (סימן המינוס), EMF תנועתי כמקרה מיוחד של שינוי שטף, השריה עצמית "
            "והדדית, והתנהגות עברית של מעגלי RL. בניגוד לאלקטרוסטטיקה, סינון הוא "
            "**דינמי** — שטף גדול קבוע גורם ל-**EMF אפס**.\n\n"
            "**נושאי בחינה טיפוסיים:**\n"
            "- חוק פאראדי וחוק לנץ (סימן וכיוון)\n"
            "- EMF תנועתי ($\\mathcal{E} = BLv$)\n"
            "- השריה עצמית ($L$) והשריה הדדית ($M$)\n"
            "- מעגלי RL (עלייה ודעיכה מעריכית)\n"
            "- אנרגיה מאוחסנת בשדות מגנטיים\n\n"
            "שיעור זה מבוסס על שטף מגנטי מ-EM מ introductory ומוביל למעגלי AC ומשוואות מקסוול."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Magnetic flux** through a surface:\n"
            "$$\\Phi_B = \\int \\vec{B}\\cdot d\\vec{A} = BA\\cos\\theta \\quad "
            "(\\text{uniform }\\vec{B}, \\text{ flat loop})$$\n"
            "Unit: Weber (Wb = T·m²). The angle $\\theta$ is between $\\vec{B}$ and the "
            "outward normal to the loop — crucial when the field is not perpendicular.\n\n"
            "**Faraday's law of induction:**\n"
            "$$\\mathcal{E} = -\\frac{d\\Phi_B}{dt}$$\n"
            "For a coil with $N$ identical turns: $\\mathcal{E} = -N\\,d\\Phi_B/dt$. "
            "The EMF is defined as the work per unit charge around the closed loop "
            "(non-conservative in the presence of changing flux).\n\n"
            "**Lenz's law:** The minus sign means the induced EMF (and current) always "
            "**opposes** the change in flux — enforcing energy conservation.\n\n"
            "**Motional EMF** for a rod of length $L$ moving with velocity $v$ "
            "perpendicular to uniform $B$:\n"
            "$$\\mathcal{E} = BLv$$\n\n"
            "**Self-inductance** (solenoid approximation):\n"
            "$$\\mathcal{E}_L = -L\\frac{dI}{dt}, \\quad L = \\mu_0\\frac{N^2}{\\ell}A$$\n\n"
            "**Mutual inductance** between two coils on a common core:\n"
            "$$\\mathcal{E}_2 = -M\\frac{dI_1}{dt}, \\quad M = \\mu_0\\frac{N_1 N_2 A}{\\ell}$$\n\n"
            "The coefficient $M$ depends on geometry and coupling — when all flux from coil 1 "
            "links coil 2, $M$ is maximal. SI unit of inductance: Henry (H = V·s/A = Ω·s)."
        ),
        "body_he_md": (
            "**שטף מגנטי** דרך משטח:\n"
            "$$\\Phi_B = \\int \\vec{B}\\cdot d\\vec{A} = BA\\cos\\theta \\quad "
            "(\\vec{B} \\text{ אחיד, לולאה שטוחה})$$\n"
            "יחידה: Weber (Wb = T·m²). הזווית $\\theta$ היא בין $\\vec{B}$ לנורמל החיצוני "
            "ללולאה — קריטי כשהשדה לא ניצב.\n\n"
            "**חוק פאראדי לסינון:**\n"
            "$$\\mathcal{E} = -\\frac{d\\Phi_B}{dt}$$\n"
            "לסליל עם $N$ סיבובים זהים: $\\mathcal{E} = -N\\,d\\Phi_B/dt$. "
            "ה-EMF מוגדר כעבודה ליחידת מטען סביב הלולאה הסגורה (לא קונסרватיבי).\n\n"
            "**חוק לנץ:** סימן המינוס פירושו שה-EMF (והזרם) המושרים **מתנגדים** "
            "תמיד לשינוי בשטף — שימור אנרגיה.\n\n"
            "**EMF תנועתי** למוט אורך $L$ הנע במהירות $v$ ניצב ל-$B$ אחיד:\n"
            "$$\\mathcal{E} = BLv$$\n\n"
            "**השריה עצמית** (קירוב סולנואיד):\n"
            "$$\\mathcal{E}_L = -L\\frac{dI}{dt}, \\quad L = \\mu_0\\frac{N^2}{\\ell}A$$\n\n"
            "**השריה הדדית** בין שני סלילים על ליבה משותפת:\n"
            "$$\\mathcal{E}_2 = -M\\frac{dI_1}{dt}, \\quad M = \\mu_0\\frac{N_1 N_2 A}{\\ell}$$\n\n"
            "מקדם $M$ תלוי בגאומטריה ובקישור — כשכל השטף מסליל 1 קושר לסליל 2, "
            "$M$ מקסימלי. יחידת השריה ב-SI: Henry (H = V·s/A = Ω·s)."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Why the minus sign (Lenz's law)?\n"
            "If induced EMF **aided** the flux change, the current would amplify the flux, "
            "which would increase the current further — runaway growth violating energy "
            "conservation. The minus sign in $\\mathcal{E} = -d\\Phi_B/dt$ enforces that "
            "induced effects always oppose the cause. Use the right-hand rule on the induced "
            "current to predict the direction of the opposing field.\n\n"
            "### Motional EMF derivation\n"
            "A rod of length $L$ moves with velocity $v$ perpendicular to $B$. Magnetic force "
            "$F = qvB$ on free electrons creates charge separation. Equilibrium when "
            "$qE = qvB$, giving $E = vB$ and potential difference "
            "$\\mathcal{E} = EL = vBL$. This is equivalent to Faraday's law applied to "
            "the changing area swept by the rod.\n\n"
            "### Energy stored in an inductor\n"
            "$$U_L = \\frac{1}{2}LI^2$$\n"
            "Energy is stored in the magnetic field. When current changes, power "
            "$P = IV = L I\\,dI/dt$ flows into (or out of) the field.\n\n"
            "### Magnetic energy density\n"
            "$$u_B = \\frac{B^2}{2\\mu_0} \\quad [\\text{J/m}^3]$$\n"
            "Total energy: $U = \\int u_B\\,dV$.\n\n"
            "### RL circuit (switch closed at $t=0$)\n"
            "$$I(t) = \\frac{\\mathcal{E}}{R}\\left(1 - e^{-t/\\tau}\\right), "
            "\\quad \\tau = \\frac{L}{R}$$\n"
            "The inductor opposes the sudden current rise via back-EMF $-L\\,dI/dt$. "
            "At $t = \\tau$, current reaches $63\\%$ of steady state; at $5\\tau$, "
            "it is effectively at $I_\\infty = \\mathcal{E}/R$."
        ),
        "body_he_md": (
            "### מדוע הסימן המינוס (חוק לנץ)?\n"
            "אם EMF מושר **היה מסייע** לשינוי השטף, הזרם היה מגביר את השטף, מה שהיה "
            "מגביר את הזרם עוד — צמיחה בלתי מוגבלת שמפרה שימור אנרגיה. הסימן המינוס "
            "ב-$\\mathcal{E} = -d\\Phi_B/dt$ מכריח שהאפקטים המושרים תמיד מתנגדים לסיבה. "
            "השתמשו בכלל יד ימין על הזרם המושר כדי לחזות כיוון השדה המתנגד.\n\n"
            "### גזירת EMF תנועתי\n"
            "מוט אורך $L$ נע במהירות $v$ ניצב ל-$B$. כוח מגנטי $F = qvB$ על "
            "אלקטרונים חופשיים יוצר הפרדת מטענים. שיווי משקל כש-$qE = qvB$, "
            "נותן $E = vB$ והפרש פוטנציאל $\\mathcal{E} = EL = vBL$. זה שקול "
            "לחוק פאראדי על השטח המשתנה שהמוט מכסה.\n\n"
            "### אנרגיה מאוחסנת בסליל\n"
            "$$U_L = \\frac{1}{2}LI^2$$\n"
            "אנרגיה מאוחסנת בשדה המגנטי. כשהזרם משתנה, הספק $P = IV = L I\\,dI/dt$ "
            "נכנס (או יוצא) מהשדה.\n\n"
            "### צפיפות אנרגיה מגנטית\n"
            "$$u_B = \\frac{B^2}{2\\mu_0} \\quad [\\text{J/m}^3]$$\n"
            "אנרגיה כוללת: $U = \\int u_B\\,dV$.\n\n"
            "### מעגל RL (מפסק נסגר ב-$t=0$)\n"
            "$$I(t) = \\frac{\\mathcal{E}}{R}\\left(1 - e^{-t/\\tau}\\right), "
            "\\quad \\tau = \\frac{L}{R}$$\n"
            "הסליל מתנגד לעלייה פתאומית בזרם דרך EMF נגדי $-L\\,dI/dt$. "
            "ב-$t = \\tau$, הזרם מגיע ל-63% ממצב מנוחה; ב-$5\\tau$, "
            "הוא ב-$I_\\infty = \\mathcal{E}/R$ בפועל."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A circular loop of radius $r = 0.1\\;\\text{m}$ sits in a uniform "
            "magnetic field increasing at $dB/dt = 50\\;\\text{T/s}$, perpendicular to the "
            "loop plane. Find the magnitude of the induced EMF.\n\n"
            "### Move 1: Identify geometry\n"
            "Field perpendicular → $\\cos\\theta = 1$. Flux through one turn: "
            "$\\Phi_B = BA = \\pi r^2 B$.\n\n"
            "### Move 2: Apply Faraday's law\n"
            "$$|\\mathcal{E}| = \\left|\\frac{d\\Phi_B}{dt}\\right| = "
            "A\\frac{dB}{dt} = \\pi r^2 \\cdot \\frac{dB}{dt}$$\n\n"
            "### Move 3: Substitute numbers\n"
            "$A = \\pi(0.1)^2 = 0.0314\\;\\text{m}^2$. "
            "$|\\mathcal{E}| = 0.0314 \\times 50 = 1.57\\;\\text{V}$.\n\n"
            "### Move 4: Lenz check\n"
            "Field is **increasing** into the page, so induced current creates a field "
            "out of the page (opposing the increase). The minus sign in "
            "$\\mathcal{E} = -d\\Phi/dt$ captures this; we report magnitude here.\n\n"
            "### Move 5: Units check\n"
            "m² × (T/s) = (T·m²)/s = Wb/s = V ✓.\n\n"
            "**Answer:** $|\\mathcal{E}| = 1.57\\;\\text{V}$. "
            "**Exam tip:** Only the **rate** $dB/dt$ matters — a constant $B = 50$ T "
            "induces zero EMF. If the loop had $N = 10$ turns, multiply the result by 10."
        ),
        "body_he_md": (
            "**נתון:** לולאה מעגלית ברדיוס $r = 0.1\\;\\text{m}$ בשדה מגנטי אחיד "
            "העולה ב-$dB/dt = 50\\;\\text{T/s}$, ניצב לשטח הלולאה. מצאו את גודל ה-EMF המושר.\n\n"
            "### צעד 1: זיהוי גאומטריה\n"
            "שדה ניצב → $\\cos\\theta = 1$. שטף בסיבוב אחד: $\\Phi_B = BA = \\pi r^2 B$.\n\n"
            "### צעד 2: יישום חוק פאראדי\n"
            "$$|\\mathcal{E}| = \\left|\\frac{d\\Phi_B}{dt}\\right| = "
            "A\\frac{dB}{dt} = \\pi r^2 \\cdot \\frac{dB}{dt}$$\n\n"
            "### צעד 3: הצבת מספרים\n"
            "$A = \\pi(0.1)^2 = 0.0314\\;\\text{m}^2$. "
            "$|\\mathcal{E}| = 0.0314 \\times 50 = 1.57\\;\\text{V}$.\n\n"
            "### צעד 4: בדיקת לנץ\n"
            "השדה **עולה** לתוך הדף, לכן הזרם המושר יוצר שדה החוצה (מתנגד לעלייה). "
            "סימן המינוס ב-$\\mathcal{E} = -d\\Phi/dt$ תופס זאת; כאן מדווחים על הגודל.\n\n"
            "### צעד 5: בדיקת יחידות\n"
            "m² × (T/s) = (T·m²)/s = Wb/s = V ✓.\n\n"
            "**תשובה:** $|\\mathcal{E}| = 1.57\\;\\text{V}$. "
            "**טיפ לבחינה:** רק **קצב** $dB/dt$ חשוב — $B$ קבוע גורם ל-EMF אפס. "
            "אם היו $N = 10$ סיבובים, היו מכפילים ב-10."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A rod of length $L = 0.5\\;\\text{m}$ slides along two parallel rails "
            "(separation $L$) at $v = 4\\;\\text{m/s}$ in uniform $B = 0.3\\;\\text{T}$ "
            "(perpendicular to the rail plane). Loop resistance $R = 2\\;\\Omega$. "
            "Find (a) motional EMF, (b) induced current, (c) power dissipated in $R$.\n\n"
            "### Move 1: Motional EMF\n"
            "Rod, field, and velocity mutually perpendicular → "
            "$\\mathcal{E} = BLv = 0.3 \\times 0.5 \\times 4 = 0.6\\;\\text{V}$.\n\n"
            "### Move 2: Induced current\n"
            "Ohm's law on the closed loop: $I = \\mathcal{E}/R = 0.6/2 = 0.3\\;\\text{A}$.\n\n"
            "### Move 3: Power dissipated\n"
            "$P = I^2 R = (0.3)^2 \\times 2 = 0.18\\;\\text{W}$. "
            "Alternatively $P = \\mathcal{E}^2/R = 0.36/2 = 0.18\\;\\text{W}$ ✓.\n\n"
            "### Move 4: Energy balance\n"
            "Mechanical power to push the rod against magnetic drag equals electrical "
            "power dissipated: $P_{\\text{mech}} = Fv = (IBL)v = B^2 L^2 v^2/R = 0.18\\;\\text{W}$ ✓.\n\n"
            "**Answer:** (a) $0.6\\;\\text{V}$, (b) $0.3\\;\\text{A}$, (c) $0.18\\;\\text{W}$. "
            "**Exam tip:** The effective length in $BLv$ is the segment **cutting** field lines. "
            "If the rails were longer than $L$, only the separation $L$ enters the formula."
        ),
        "body_he_md": (
            "**נתון:** מוט באורך $L = 0.5\\;\\text{m}$ מחליק על שני מסילות מקבילות "
            "(מרחק $L$) במהירות $v = 4\\;\\text{m/s}$ בשדה אחיד $B = 0.3\\;\\text{T}$ "
            "(ניצב למישור המסילות). התנגדות הלולאה $R = 2\\;\\Omega$. "
            "מצאו (א) EMF תנועתי, (ב) זרם מושר, (ג) הספק שנמוג ב-$R$.\n\n"
            "### צעד 1: EMF תנועתי\n"
            "מוט, שדה ומהירות ניצבים הדדית → "
            "$\\mathcal{E} = BLv = 0.3 \\times 0.5 \\times 4 = 0.6\\;\\text{V}$.\n\n"
            "### צעד 2: זרם מושר\n"
            "חוק אום על הלולאה הסגורה: $I = \\mathcal{E}/R = 0.6/2 = 0.3\\;\\text{A}$.\n\n"
            "### צעד 3: הספק שנמוג\n"
            "$P = I^2 R = (0.3)^2 \\times 2 = 0.18\\;\\text{W}$. "
            "לחלופין $P = \\mathcal{E}^2/R = 0.18\\;\\text{W}$ ✓.\n\n"
            "### צעד 4: מאזן אנרגיה\n"
            "הספק מכני לדחיפת המוט נגד גרר מגנטי שווה להספק החשמלי: "
            "$P_{\\text{mech}} = Fv = (IBL)v = B^2 L^2 v^2/R = 0.18\\;\\text{W}$ ✓.\n\n"
            "### צעד 5: כיוון לנץ\n"
            "הזרם המושר יוצר כוח המתנגד לתנועת המוט — נדרשת עבודה חיצונית להמשך ההזזה.\n\n"
            "**תשובה:** (א) $0.6\\;\\text{V}$, (ב) $0.3\\;\\text{A}$, (ג) $0.18\\;\\text{W}$. "
            "**טיפ לבחינה:** האורך ב-$BLv$ הוא הקטע **החותך** קווי שדה, לא אורך המסילות."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** An RL circuit has $R = 10\\;\\Omega$, $L = 0.5\\;\\text{H}$, "
            "battery $\\mathcal{E} = 20\\;\\text{V}$. Switch closes at $t = 0$. "
            "Find (a) time constant, (b) steady-state current, (c) energy stored at "
            "steady state, (d) current at $t = 0.1\\;\\text{s}$, (e) rate of energy "
            "storage at that instant.\n\n"
            "### Move 1: Time constant\n"
            "$\\tau = L/R = 0.5/10 = 0.05\\;\\text{s}$.\n\n"
            "### Move 2: Steady-state current\n"
            "Inductor acts as wire at DC steady state: $I_\\infty = \\mathcal{E}/R = 2\\;\\text{A}$.\n\n"
            "### Move 3: Stored energy at steady state\n"
            "$$U_L = \\frac{1}{2}LI_\\infty^2 = \\frac{1}{2}(0.5)(4) = 1\\;\\text{J}$$\n\n"
            "### Move 4: Current at $t = 0.1\\;\\text{s}$\n"
            "$$I = I_\\infty(1 - e^{-t/\\tau}) = 2(1 - e^{-0.1/0.05}) = 2(1 - e^{-2}) "
            "\\approx 1.73\\;\\text{A}$$\n\n"
            "### Move 5: Rate of energy storage\n"
            "$dU_L/dt = LI\\,dI/dt$. Using $dI/dt = (\\mathcal{E}/L)e^{-t/\\tau}$: "
            "$dU_L/dt = I\\mathcal{E}e^{-t/\\tau} \\approx 1.73 \\times 20 \\times 0.135 "
            "= 4.67\\;\\text{W}$.\n\n"
            "**Answer:** (a) $0.05\\;\\text{s}$, (b) $2\\;\\text{A}$, (c) $1\\;\\text{J}$, "
            "(d) $1.73\\;\\text{A}$, (e) $4.67\\;\\text{W}$. "
            "**Exam tip:** At $t = 0$, the inductor behaves like an open circuit "
            "($I = 0$); at steady state it behaves like a short ($I = \\mathcal{E}/R$)."
        ),
        "body_he_md": (
            "**נתון:** מעגל RL עם $R = 10\\;\\Omega$, $L = 0.5\\;\\text{H}$, "
            "סוללה $\\mathcal{E} = 20\\;\\text{V}$. מפסק נסגר ב-$t = 0$. "
            "מצאו (א) קבוע זמן, (ב) זרם במצב מנוחה, (ג) אנרגיה מאוחסנת, "
            "(ד) זרם ב-$t = 0.1\\;\\text{s}$, (ה) קצב אגירת אנרגיה.\n\n"
            "### צעד 1: קבוע זמן\n"
            "$\\tau = L/R = 0.5/10 = 0.05\\;\\text{s}$.\n\n"
            "### צעד 2: זרם במצב מנוחה\n"
            "סליל מתנהג כחוט ב-DC במנוחה: $I_\\infty = \\mathcal{E}/R = 2\\;\\text{A}$.\n\n"
            "### צעד 3: אנרגיה מאוחסנת\n"
            "$$U_L = \\frac{1}{2}LI_\\infty^2 = \\frac{1}{2}(0.5)(4) = 1\\;\\text{J}$$\n\n"
            "### צעד 4: זרם ב-$t = 0.1\\;\\text{s}$\n"
            "$$I = I_\\infty(1 - e^{-t/\\tau}) = 2(1 - e^{-2}) \\approx 1.73\\;\\text{A}$$\n\n"
            "### צעד 5: קצב אגירת אנרגיה\n"
            "$dU_L/dt = LI\\,dI/dt$. עם $dI/dt = (\\mathcal{E}/L)e^{-t/\\tau}$: "
            "$dU_L/dt \\approx 4.67\\;\\text{W}$.\n\n"
            "### צעד 6: אימות\n"
            "ב-$t = 0.1\\;\\text{s} = 2\\tau$, הזרם כבר ~86% מ-$I_\\infty$ — קרוב למנוחה.\n\n"
            "**תשובה:** (א) $0.05\\;\\text{s}$, (ב) $2\\;\\text{A}$, (ג) $1\\;\\text{J}$, "
            "(ד) $1.73\\;\\text{A}$, (ה) $4.67\\;\\text{W}$. "
            "**טיפ לבחינה:** ב-$t = 0$ הסליל כמו מעגל פתוח; במנוחה כמו קצר."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "A square loop ($a = 0.2\\;\\text{m}$, $N = 100$ turns) is in "
            "$B(t) = 0.5 + 3t$ (T), perpendicular to the loop.\n\n"
            "**Step 1:** Area $A = a^2 = 0.04\\;\\text{m}^2$. Flux per turn: "
            "$\\Phi_B = BA$.\n\n"
            "**Step 2:** Rate of change: $dB/dt = 3\\;\\text{T/s}$ (constant slope).\n\n"
            "**Step 3:** Faraday with $N$ turns:\n"
            "$$\\mathcal{E} = -N\\frac{d\\Phi_B}{dt} = -NA\\frac{dB}{dt} = "
            "-100(0.04)(3) = -12\\;\\text{V}$$\n\n"
            "**Step 4:** Lenz interpretation — field is increasing, so induced EMF "
            "opposes the increase. $|\\mathcal{E}| = 12\\;\\text{V}$ at **any** $t$, "
            "including $t = 2\\;\\text{s}$ (only $dB/dt$ matters, not $B$ itself).\n\n"
            "**Verify:** At $t = 2\\;\\text{s}$, $B = 6.5$ T but EMF still 12 V ✓."
        ),
        "checkpoint_solution_he": (
            "לולאה ריבועית ($a = 0.2\\;\\text{m}$, $N = 100$ סיבובים) ב-$B(t) = 0.5 + 3t$ (T), "
            "ניצב ללולאה.\n\n"
            "**שלב 1:** שטח $A = a^2 = 0.04\\;\\text{m}^2$. שטף לסיבוב: $\\Phi_B = BA$.\n\n"
            "**שלב 2:** קצב שינוי: $dB/dt = 3\\;\\text{T/s}$ (שיפוע קבוע).\n\n"
            "**שלב 3:** פאראדי עם $N$ סיבובים:\n"
            "$$\\mathcal{E} = -N\\frac{d\\Phi_B}{dt} = -100(0.04)(3) = -12\\;\\text{V}$$\n\n"
            "**שלב 4:** פרשנות לנץ — השדה עולה, לכן EMF מושר מתנגד. $|\\mathcal{E}| = 12\\;\\text{V}$ "
            "ב**כל** $t$, כולל $t = 2\\;\\text{s}$ (רק $dB/dt$ חשוב, לא $B$ עצמו).\n\n"
            "**אימות:** ב-$t = 2\\;\\text{s}$, $B = 6.5$ T אך EMF עדיין 12 V ✓."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "Solenoid: $N = 500$ turns, length $\\ell = 0.2\\;\\text{m}$, "
            "cross-section $A = 4\\times10^{-4}\\;\\text{m}^2$.\n\n"
            "**Step 1:** Self-inductance formula (long solenoid):\n"
            "$$L = \\mu_0 \\frac{N^2 A}{\\ell}$$\n\n"
            "**Step 2:** Substitute:\n"
            "$$L = (4\\pi\\times10^{-7})\\frac{(500)^2(4\\times10^{-4})}{0.2} = "
            "(4\\pi\\times10^{-7})(250000)(2\\times10^{-3})$$\n"
            "$$= (4\\pi\\times10^{-7})(500) = 2\\pi\\times10^{-4} \\approx "
            "6.28\\times10^{-4}\\;\\text{H} = 0.628\\;\\text{mH}$$\n\n"
            "**Step 3:** Units check — $\\mu_0$ [T·m/A] × [turns²·m²/m] = "
            "[T·m²/A] = [H] ✓.\n\n"
            "**Answer:** $L \\approx 0.628\\;\\text{mH}$."
        ),
        "checkpoint_solution_he": (
            "סולנואיד: $N = 500$ סיבובים, אורך $\\ell = 0.2\\;\\text{m}$, "
            "חתך $A = 4\\times10^{-4}\\;\\text{m}^2$.\n\n"
            "**שלב 1:** נוסחת השריה עצמית (סולנואיד ארוך):\n"
            "$$L = \\mu_0 \\frac{N^2 A}{\\ell}$$\n\n"
            "**שלב 2:** הצבה:\n"
            "$$L = (4\\pi\\times10^{-7})\\frac{(500)^2(4\\times10^{-4})}{0.2} "
            "\\approx 6.28\\times10^{-4}\\;\\text{H} = 0.628\\;\\text{mH}$$\n\n"
            "**שלב 3:** בדיקת יחידות — $\\mu_0$ [T·m/A] × [סיבובים²·m²/m] = "
            "[H] ✓.\n\n"
            "**תשובה:** $L \\approx 0.628\\;\\text{mH}$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Task | Method | Key formula |\n"
            "|---|---|---|\n"
            "| EMF from changing field | Faraday on flux | "
            "$|\\mathcal{E}| = N|d\\Phi_B/dt| = NA|dB/dt|$ |\n"
            "| Motional EMF | Rod cutting field lines | $\\mathcal{E} = BLv$ |\n"
            "| Direction | Lenz's law | Induced current opposes flux change |\n"
            "| Self-inductance (solenoid) | Flux linkage / current | "
            "$L = \\mu_0 N^2 A/\\ell$ |\n"
            "| Back-EMF from inductor | Faraday on own flux | $\\mathcal{E}_L = -L\\,dI/dt$ |\n"
            "| Energy in inductor | Magnetic field storage | $U_L = \\frac{1}{2}LI^2$ |\n"
            "| RL time constant | $L/R$ ratio | $\\tau = L/R$ |\n"
            "| Current in RL (rising) | Exponential approach | "
            "$I = (\\mathcal{E}/R)(1 - e^{-t/\\tau})$ |\n\n"
            "**Step-by-step:** (1) Is flux changing, or is a conductor moving? "
            "(2) Write $\\Phi_B$ or identify motional geometry. (3) Differentiate "
            "or apply $BLv$. (4) Apply Lenz for sign/direction. "
            "(5) For RL, identify $\\tau$ before substituting $t$.\n\n"
            "**When to use:** University induction problems always reduce to one "
            "row in this table. Pick the row first, then substitute numbers."
        ),
        "body_he_md": (
            "| משימה | שיטה | נוסחה מרכזית |\n"
            "|---|---|---|\n"
            "| EMF משדה משתנה | פאראדי על שטף | "
            "$|\\mathcal{E}| = N|d\\Phi_B/dt| = NA|dB/dt|$ |\n"
            "| EMF תנועתי | מוט חותך קווי שדה | $\\mathcal{E} = BLv$ |\n"
            "| כיוון | חוק לנץ | זרם מושר מתנגד לשינוי שטף |\n"
            "| השריה עצמית (סולנואיד) | קשר שטף/זרם | $L = \\mu_0 N^2 A/\\ell$ |\n"
            "| EMF נגדי מסליל | פאראדי על שטף עצמי | $\\mathcal{E}_L = -L\\,dI/dt$ |\n"
            "| אנרגיה בסליל | אגירה מגנטית | $U_L = \\frac{1}{2}LI^2$ |\n"
            "| קבוע זמן RL | יחס $L/R$ | $\\tau = L/R$ |\n"
            "| זרם ב-RL (עולה) | התקרבות מעריכית | "
            "$I = (\\mathcal{E}/R)(1 - e^{-t/\\tau})$ |\n\n"
            "**שלב-אחר-שלב:** (1) האם השטף משתנה, או מוליך נע? "
            "(2) כתבו $\\Phi_B$ או זיהו גאומטריה תנועתית. (3) גזרו או יישמו $BLv$. "
            "(4) לנץ לסימן/כיוון. (5) ב-RL, זיהו $\\tau$ לפני הצבת $t$.\n\n"
            "**מתי להשתמש:** בעיות סינון באוניברסיטה מצטמצמות לשורה אחת בטבלה. "
            "בחרו שורה קודם, ואז הציבו מספרים."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting Lenz's law sign.** Always ask: does the induced current "
            "reinforce or oppose the flux change? It must oppose. A negative EMF "
            "when flux increases is correct physics, not an error.\n\n"
            "2. **Confusing flux with rate of change.** $\\Phi_B = BA\\cos\\theta$ is "
            "the flux; EMF depends on $d\\Phi_B/dt$. A loop in a strong constant field "
            "has large flux but **zero** induced EMF.\n\n"
            "3. **Angle in flux formula.** When field is not perpendicular, "
            "$\\Phi_B = BA\\cos\\theta$ — using $\\sin\\theta$ instead is a common exam slip.\n\n"
            "4. **Self-inductance units.** $L$ is in Henries (H = V·s/A = Ω·s). "
            "Do not confuse with capacitance (F).\n\n"
            "5. **RL time constant is $\\tau = L/R$, not $RC$.** Larger $L$ → slower "
            "response; larger $R$ → faster approach to steady state.\n\n"
            "**Example misconception:** \"Large flux causes large EMF.\"\n\n"
            "**Fix:** EMF = rate of change of flux, not flux itself."
        ),
        "body_he_md": (
            "1. **שכחת סימן חוק לנץ.** תמיד שאלו: האם הזרם המושר מחזק או מתנגד לשינוי "
            "בשטף? חייב להתנגד. EMF שלילי כשהשטף עולה הוא פיזיקה נכונה, לא טעות.\n\n"
            "2. **בלבול שטף וקצב שינוי.** $\\Phi_B = BA\\cos\\theta$ הוא השטף; EMF תלוי "
            "ב-$d\\Phi_B/dt$. לולאה בשדה קבוע חזק — שטף גדול אך **EMF אפס**.\n\n"
            "3. **זווית בנוסחת שטף.** כשהשדה לא ניצב, $\\Phi_B = BA\\cos\\theta$ — "
            "שימוש ב-$\\sin\\theta$ הוא טעות נפוצה בבחינה.\n\n"
            "4. **יחידות השריה עצמית.** $L$ ב-Henry (H = V·s/A = Ω·s). "
            "אל תערבבו עם קיבול (F).\n\n"
            "5. **קבוע זמן RL הוא $\\tau = L/R$, לא $RC$.** $L$ גדול → תגובה איטית; "
            "$R$ גדול → התקרבות מהירה למצב מנוחה.\n\n"
            "**אי-הבנה נפוצה:** \"שטף גדול גורם ל-EMF גדול.\"\n\n"
            "**תיקון:** EMF = קצב שינוי השטף, לא השטף עצמו."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Electromagnetic induction is the bridge between mechanics and electricity "
            "that makes modern power grids possible. Every generator at a power plant "
            "converts rotational kinetic energy into AC voltage via changing flux through "
            "coils. Transformers step voltage up for efficient long-distance transmission "
            "and down for safe household use — all governed by Faraday's law and mutual "
            "inductance.\n\n"
            "**Why it matters for university exams:** Technion and other Israeli "
            "programs test induction in multi-step problems combining motional EMF, "
            "Lenz direction, and RL transients. Mastery here unlocks AC circuit analysis "
            "and the full Maxwell equation set. Connect this to `concept:magnetism` "
            "(motional force) and `concept:em_waves` (changing fields propagate)."
        ),
        "body_he_md": (
            "סינון אלקטרומגנטי הוא הגשר בין מכניקה לחשמל שהופך רשתות חשמל מודרניות "
            "לאפשריות. כל גנרטור בתחנת כוח ממיר אנרגיה קינטית סיבובית ל-AC דרך שטף "
            "משתנה בסלילים. שנאים מעלים מתח להולכה יעילה ומורידים לשימוש ביתי בטוח — "
            "הכל תחת חוק פאראדי והשריה הדדית.\n\n"
            "**למה זה חשוב לבחינות אוניברסיטה:** הטכניון ומוסדות ישראליים בוחנים סינון "
            "בבעיות רב-שלביות המשלבות EMF תנועתי, כיוון לנץ ועבר RL. שליטה כאן פותחת "
            "ניתוח מעגלי AC ומשוואות מקסוול המלאות. חברו ל-`concept:magnetism` "
            "(כוח תנועתי) ו-`concept:em_waves` (שדות משתנים מתפשטים)."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Formula card — electromagnetic induction:**\n"
            "- $\\Phi_B = \\int \\vec{B}\\cdot d\\vec{A} = BA\\cos\\theta$ [Wb]\n"
            "- $\\mathcal{E} = -N\\,d\\Phi_B/dt$ (Faraday + Lenz)\n"
            "- Motional EMF: $\\mathcal{E} = BLv$ (mutually perpendicular)\n"
            "- $L_{\\text{solenoid}} = \\mu_0 N^2 A/\\ell$; $\\mathcal{E}_L = -L\\,dI/dt$\n"
            "- $U_L = \\frac{1}{2}LI^2$; $u_B = B^2/(2\\mu_0)$ [J/m³]\n"
            "- RL rising: $\\tau = L/R$; $I(t) = (\\mathcal{E}/R)(1 - e^{-t/\\tau})$\n"
            "- RL decay (battery removed): $I(t) = I_0 e^{-t/\\tau}$\n"
            "- Mutual: $\\mathcal{E}_2 = -M\\,dI_1/dt$; $M = \\mu_0 N_1 N_2 A/\\ell$\n"
            "- Rotating coil peak: $\\mathcal{E}_0 = NBA\\omega$\n\n"
            "**Last review:** Derive motional EMF once from scratch, then solve one "
            "checkpoint without looking. State Lenz's law in one sentence. "
            "Practice converting cm² to m² quickly — a frequent source of "
            "order-of-magnitude errors in inductance and rotating-coil flux problems."
        ),
        "body_he_md": (
            "**כרטיס נוסחאות — סינון אלקטרומגנטי:**\n"
            "- $\\Phi_B = BA\\cos\\theta$ [Wb]\n"
            "- $\\mathcal{E} = -N\\,d\\Phi_B/dt$ (פאראדי + לנץ)\n"
            "- EMF תנועתי: $\\mathcal{E} = BLv$ (ניצבים הדדית)\n"
            "- $L_{\\text{sol}} = \\mu_0 N^2 A/\\ell$; $\\mathcal{E}_L = -L\\,dI/dt$\n"
            "- $U_L = \\frac{1}{2}LI^2$; $u_B = B^2/(2\\mu_0)$ [J/m³]\n"
            "- RL עולה: $\\tau = L/R$; $I = (\\mathcal{E}/R)(1 - e^{-t/\\tau})$\n"
            "- RL דועך (סוללה מנותקת): $I = I_0 e^{-t/\\tau}$\n"
            "- הדדי: $\\mathcal{E}_2 = -M\\,dI_1/dt$; $M = \\mu_0 N_1 N_2 A/\\ell$\n\n"
            "**חזרה אחרונה:** גזרו EMF תנועתי פעם אחת מאפס, ואז פתרו checkpoint "
            "בלי להסתכל. נסחו חוק לנץ במשפט אחד. "
            "תרגלו המרת cm² ל-m² — מקור תכוף לטעויות סדר גודל בבעיות השריה."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Faraday:** $\\mathcal{E} = -N\\,d\\Phi_B/dt$; only changing flux induces EMF\n"
            "- **Lenz:** Induced effects oppose the flux change (minus sign)\n"
            "- **Motional EMF:** $\\mathcal{E} = BLv$ — special case of changing area\n"
            "- **Self-inductance:** $L = \\mu_0 N^2 A/\\ell$; back-EMF $\\mathcal{E}_L = -L\\,dI/dt$\n"
            "- **Energy:** $U_L = \\frac{1}{2}LI^2$ stored in magnetic field; "
            "$u_B = B^2/(2\\mu_0)$\n"
            "- **RL circuit:** $\\tau = L/R$; exponential rise $I = I_\\infty(1-e^{-t/\\tau})$\n"
            "- **Mutual inductance:** $\\mathcal{E}_2 = -M\\,dI_1/dt$; basis of transformers\n\n"
            "**Takeaway:** Read the problem — is flux changing or is a conductor moving? "
            "That choice determines the entire solution path."
        ),
        "body_he_md": (
            "- **פאראדי:** $\\mathcal{E} = -N\\,d\\Phi_B/dt$; רק שטף משתנה גורם ל-EMF\n"
            "- **לנץ:** אפקטים מושרים מתנגדים לשינוי השטף (סימן מינוס)\n"
            "- **EMF תנועתי:** $\\mathcal{E} = BLv$ — מקרה מיוחד של שטח משתנה\n"
            "- **השריה עצמית:** $L = \\mu_0 N^2 A/\\ell$; EMF נגדי $\\mathcal{E}_L = -L\\,dI/dt$\n"
            "- **אנרגיה:** $U_L = \\frac{1}{2}LI^2$ בשדה מגנטי; $u_B = B^2/(2\\mu_0)$\n"
            "- **מעגל RL:** $\\tau = L/R$; עלייה $I = I_\\infty(1-e^{-t/\\tau})$\n"
            "- **השריה הדדית:** $\\mathcal{E}_2 = -M\\,dI_1/dt$; בסיס שנאים\n\n"
            "**מסקנה:** קראו את הבעיה — האם השטף משתנה או מוליך נע? "
            "הבחירה קובעת את כל מסלול הפתרון."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "Lenz's law is the physical content of the minus sign in Faraday's law: "
            "the induced current creates a magnetic field that **opposes** the change "
            "in flux that caused it. If the external flux is increasing into the page, "
            "the induced current circulates to produce flux out of the page.\n\n"
            "Option B (opposes the change) is correct. Option A would violate energy "
            "conservation — a self-amplifying loop. Option C is wrong because direction "
            "depends on geometry, not a fixed clockwise rule. Option D contradicts "
            "Faraday: changing flux always induces EMF.\n\n"
            "**Common slip:** Treating Lenz as a separate rule from Faraday instead of "
            "the minus sign itself.\n\n"
            "**Exam tip:** Always state what the flux is doing (increasing/decreasing) "
            "before picking current direction. **Answer:** opposes the change in flux."
        ),
        "explanation_he": (
            "חוק לנץ הוא התוכן הפיזיקלי של סימן המינוס בחוק פאראדי: הזרם המושר "
            "יוצר שדה מגנטי ש**מתנגד** לשינוי בשטף שגרם לו. אם השטף החיצוני "
            "עולה לתוך הדף, הזרם המושר מייצר שטף החוצה.\n\n"
            "אפשרות ב (מתנגד לשינוי) נכונה. אפשרות א תפרה שימור אנרגיה — לולאה "
            "מגבירה עצמה. אפשרות ג שגויה — הכיוון תלוי בגאומטריה, לא בכלל קבוע. "
            "אפשרות ד סותרת פאראדי: שטף משתנה תמיד גורם ל-EMF.\n\n"
            "**טעות נפוצה:** התייחסות ללנץ ככלל נפרד מפאראדי במקום הסימן המינוס.\n\n"
            "**טיפ לבחינה:** ציינו תמיד מה השטף עושה (עולה/יורד) לפני בחירת כיוון. "
            "**תשובה:** מתנגד לשינוי בשטף."
        ),
    },
    {
        "explanation_en": (
            "Motional EMF applies when a conductor of length $L$ moves with speed $v$ "
            "perpendicular to uniform field $B$: $\\mathcal{E} = BLv$. Here "
            "$B = 0.5$ T, $L = 0.8$ m, $v = 3$ m/s, all mutually perpendicular:\n"
            "$$\\mathcal{E} = 0.5 \\times 0.8 \\times 3 = 1.2\\;\\text{V}$$\n\n"
            "Units: T × m × (m/s) = (N·s)/(C·m) × m²/s = N·m/C = J/C = V ✓. "
            "This is equivalent to Faraday's law on the changing area swept by the rod.\n\n"
            "**Common slip:** Using area $A$ instead of length $L$, or forgetting that "
            "$v$ must be the component perpendicular to both $B$ and the rod.\n\n"
            "**Exam tip:** Sketch the rod, field, and velocity — all three must be "
            "mutually perpendicular for the simple $BLv$ formula. **Answer:** 1.2 V."
        ),
        "explanation_he": (
            "EMF תנועתי חל כשמוליך באורך $L$ נע במהירות $v$ ניצב ל-$B$ אחיד: "
            "$\\mathcal{E} = BLv$. כאן $B = 0.5$ T, $L = 0.8$ m, $v = 3$ m/s, "
            "כולם ניצבים הדדית:\n"
            "$$\\mathcal{E} = 0.5 \\times 0.8 \\times 3 = 1.2\\;\\text{V}$$\n\n"
            "יחידות: T × m × (m/s) = V ✓. זה שקול לחוק פאראדי על השטח המשתנה "
            "שהמוט מכסה.\n\n"
            "**טעות נפוצה:** שימוש בשטח $A$ במקום אורך $L$, או שכחת ש-$v$ חייב "
            "להיות הרכיב הניצב גם ל-$B$ וגם למוט.\n\n"
            "**טיפ לבחינה:** שרטטו מוט, שדה ומהירות — שלושתם חייבים להיות ניצבים "
            "הדדית לנוסחה $BLv$. **תשובה:** 1.2 V."
        ),
    },
    {
        "explanation_en": (
            "When the magnetic field changes at a constant rate $dB/dt$, Faraday's "
            "law gives $|\\mathcal{E}| = A|dB/dt|$ for a single-turn loop with fixed "
            "area. Here $A = 0.05\\;\\text{m}^2$ and $|dB/dt| = 10\\;\\text{T/s}$ "
            "(field is decreasing, but we want magnitude):\n"
            "$$|\\mathcal{E}| = 0.05 \\times 10 = 0.5\\;\\text{V}$$\n\n"
            "The sign (Lenz) would be positive — induced field tries to reinforce the "
            "decreasing flux — but the question asks for magnitude only.\n\n"
            "**Common slip:** Using the current value of $B$ instead of $dB/dt$, or "
            "confusing decreasing field with negative EMF magnitude.\n\n"
            "**Exam tip:** \"Field decreasing at 10 T/s\" means $|dB/dt| = 10$ — "
            "the actual $B$ value is irrelevant. **Answer:** 0.5 V."
        ),
        "explanation_he": (
            "כשהשדה המגנטי משתנה בקצב קבוע $dB/dt$, חוק פאראדי נותן "
            "$|\\mathcal{E}| = A|dB/dt|$ ללולאה בסיבוב אחד עם שטח קבוע. "
            "כאן $A = 0.05\\;\\text{m}^2$ ו-$|dB/dt| = 10\\;\\text{T/s}$ "
            "(השדה יורד, אך נדרש גודל):\n"
            "$$|\\mathcal{E}| = 0.05 \\times 10 = 0.5\\;\\text{V}$$\n\n"
            "הסימן (לנץ) היה חיובי — שדה מושר מנסה לחזק שטף יורד — "
            "אך השאלה שואלת על גודל בלבד.\n\n"
            "**טעות נפוצה:** שימוש בערך $B$ הנוכחי במקום $dB/dt$, או בלבול "
            "בין שדה יורד ל-EMF שלילי בגודל.\n\n"
            "**טיפ לבחינה:** \"שדה יורד ב-10 T/s\" = $|dB/dt| = 10$ — "
            "ערך $B$ עצמו לא רלוונטי. **תשובה:** 0.5 V."
        ),
    },
    {
        "explanation_en": (
            "This is the canonical motional EMF setup: rod length $L = 1$ m moves at "
            "$v = 2$ m/s through $B = 0.5$ T, all perpendicular:\n"
            "$$\\mathcal{E} = BLv = 0.5 \\times 1 \\times 2 = 1\\;\\text{V}$$\n\n"
            "Physically, magnetic force $qvB$ on electrons in the rod separates charge "
            "until the electric field $E = vB$ balances it, giving terminal EMF "
            "$\\mathcal{E} = EL = vBL$.\n\n"
            "**Common slip:** Plugging $A = L^2$ (area) instead of length $L$, or "
            "using $d\\Phi/dt$ when the motional formula is faster.\n\n"
            "**Exam tip:** For a rod sliding on rails, $L$ is the rail separation "
            "(the segment cutting field lines), not the distance travelled. "
            "**Answer:** 1 V."
        ),
        "explanation_he": (
            "זהו מ setup קלאסי של EMF תנועתי: מוט באורך $L = 1$ m נע "
            "ב-$v = 2$ m/s בשדה $B = 0.5$ T, הכל ניצב:\n"
            "$$\\mathcal{E} = BLv = 0.5 \\times 1 \\times 2 = 1\\;\\text{V}$$\n\n"
            "פיזיקלית, כוח מגנטי $qvB$ על אלקטרונים במוט מפריד מטענים "
            "עד שהשדה החשמלי $E = vB$ מאזן, ונותן EMF סופי $\\mathcal{E} = EL = vBL$.\n\n"
            "**טעות נפוצה:** הצבת $A = L^2$ (שטח) במקום אורך $L$, "
            "או שימוש ב-$d\\Phi/dt$ כשהנוסחה התנועתית מהירה יותר.\n\n"
            "**טיפ לבחינה:** למוט על מסילות, $L$ הוא מרחק המסילות "
            "(הקטע החותך קווי שדה), לא המרחק שנע. אם השדה לא אחיד, "
            "יש לגזור מחוק פאראדי על השטח המשתנה. **תשובה:** 1 V."
        ),
    },
    {
        "explanation_en": (
            "Energy stored in an inductor requires finding $L$ first, then "
            "$U = \\frac{1}{2}LI^2$. For the solenoid with $N = 200$, "
            "$A = 2\\;\\text{cm}^2 = 2\\times10^{-4}\\;\\text{m}^2$, "
            "$\\ell = 10\\;\\text{cm} = 0.1\\;\\text{m}$:\n"
            "$$L = \\mu_0\\frac{N^2 A}{\\ell} = "
            "(4\\pi\\times10^{-7})\\frac{(200)^2(2\\times10^{-4})}{0.1} "
            "\\approx 1.005\\times10^{-4}\\;\\text{H}$$\n"
            "Then with $I = 3$ A:\n"
            "$$U = \\frac{1}{2}LI^2 = \\frac{1}{2}(1.005\\times10^{-4})(9) "
            "\\approx 4.5\\times10^{-4}\\;\\text{J}$$\n\n"
            "**Common slip:** Using $U = LI^2$ without the factor $\\frac{1}{2}$, "
            "or forgetting to convert cm² to m² for area.\n\n"
            "**Exam tip:** Always convert $A$ and $\\ell$ to SI before computing $L$. "
            "Cross-check: $U$ should be small for millihenry-scale inductors. "
            "Compare with capacitor energy $\\frac{1}{2}CV^2$ — same $\\frac{1}{2}$ factor "
            "from integrating power. "
            "**Answer:** $\\approx 4.5\\times10^{-4}$ J."
        ),
        "explanation_he": (
            "אנרגיה מאוחסנת בסליל דורשת מציאת $L$ תחילה, ואז $U = \\frac{1}{2}LI^2$. "
            "לסולנואיד עם $N = 200$, $A = 2\\;\\text{cm}^2 = 2\\times10^{-4}\\;\\text{m}^2$, "
            "$\\ell = 10\\;\\text{cm} = 0.1\\;\\text{m}$:\n"
            "$$L = \\mu_0\\frac{N^2 A}{\\ell} "
            "\\approx 1.005\\times10^{-4}\\;\\text{H}$$\n"
            "ואז עם $I = 3$ A:\n"
            "$$U = \\frac{1}{2}LI^2 \\approx 4.5\\times10^{-4}\\;\\text{J}$$\n\n"
            "**טעות נפוצה:** שימוש ב-$U = LI^2$ בלי גורם $\\frac{1}{2}$, "
            "או שכחת המרת cm² ל-m² לשטח. אם קיבלתם $U$ גדול פי 2 — "
            "שכחתם את $\\frac{1}{2}$. השוו לאנרגיה בקיבול $\\frac{1}{2}CV^2$ — "
            "אותו גורם $\\frac{1}{2}$ מאינטגרציה של הספק.\n\n"
            "**טיפ לבחינה:** המירו תמיד $A$ ו-$\\ell$ ל-SI לפני חישוב $L$. "
            "בדיקה: $U$ קטנה לסלילים בסדר גודל מילי-הenry. "
            "**תשובה:** $\\approx 4.5\\times10^{-4}$ J."
        ),
    },
    {
        "explanation_en": (
            "An inductor opposes changes in current via back-EMF "
            "$\\mathcal{E}_L = -L\\,dI/dt$. The magnitude is "
            "$|\\mathcal{E}_L| = L|dI/dt|$. With $L = 2$ H and "
            "$dI/dt = 5$ A/s:\n"
            "$$|\\mathcal{E}_L| = 2 \\times 5 = 10\\;\\text{V}$$\n\n"
            "The sign tells us the back-EMF opposes the increasing current "
            "(Lenz for self-induction). If current were decreasing, the "
            "back-EMF would aid the decrease.\n\n"
            "**Common slip:** Confusing back-EMF with the EMF of a battery, "
            "or using $I$ instead of $dI/dt$.\n\n"
            "**Exam tip:** Back-EMF is proportional to **rate of change** of "
            "current, not current itself. Zero current can still have large "
            "$dI/dt$ at switch-on. **Answer:** 10 V."
        ),
        "explanation_he": (
            "סליל מתנגד לשינויי זרם דרך EMF נגדי $\\mathcal{E}_L = -L\\,dI/dt$. "
            "הגודל הוא $|\\mathcal{E}_L| = L|dI/dt|$. עם $L = 2$ H ו-$dI/dt = 5$ A/s:\n"
            "$$|\\mathcal{E}_L| = 2 \\times 5 = 10\\;\\text{V}$$\n\n"
            "הסימן אומר שה-EMF הנגדי מתנגד לזרם עולה (לנץ להשריה עצמית). "
            "אם הזרם היה יורד, ה-EMF הנגדי היה מסייע לירידה.\n\n"
            "**טעות נפוצה:** בלבול EMF נגדי עם EMF של סוללה, "
            "או שימוש ב-$I$ במקום $dI/dt$.\n\n"
            "**טיפ לבחינה:** EMF נגדי פרופורציוני ל**קצב שינוי** הזרם, "
            "לא לזרם עצמו. זרם אפס יכול עדיין להיות עם $dI/dt$ גדול בהדלקה. "
            "**תשובה:** 10 V."
        ),
    },
    {
        "explanation_en": (
            "A rotating coil in a uniform field produces time-varying flux "
            "$\\Phi = NBA\\cos(\\omega t)$. By Faraday's law:\n"
            "$$\\mathcal{E} = -N\\frac{d\\Phi}{dt} = NBA\\omega\\sin(\\omega t)$$\n"
            "Peak EMF occurs when $\\sin(\\omega t) = 1$:\n"
            "$$\\mathcal{E}_0 = NBA\\omega = 50(0.2)(10^{-3})(100) = 1\\;\\text{V}$$\n\n"
            "Note the area conversion: $10\\;\\text{cm}^2 = 10^{-3}\\;\\text{m}^2$. "
            "This is the principle of an AC generator — mechanical rotation "
            "becomes alternating voltage.\n\n"
            "**Common slip:** Forgetting to convert cm² to m², or using $B$ "
            "instead of $NBA\\omega$ for peak value. Confusing peak with RMS "
            "($\\mathcal{E}_{\\text{rms}} = \\mathcal{E}_0/\\sqrt{2}$).\n\n"
            "**Exam tip:** Peak EMF $\\propto \\omega$ — faster rotation means "
            "higher voltage. **Answer:** 1 V peak."
        ),
        "explanation_he": (
            "סליל מסתובב בשדה אחיד מייצר שטף משתנה $\\Phi = NBA\\cos(\\omega t)$. "
            "לפי פאראדי:\n"
            "$$\\mathcal{E} = NBA\\omega\\sin(\\omega t)$$\n"
            "EMF שיא כש-$\\sin(\\omega t) = 1$:\n"
            "$$\\mathcal{E}_0 = NBA\\omega = 50(0.2)(10^{-3})(100) = 1\\;\\text{V}$$\n\n"
            "שימו לב להמרת שטח: $10\\;\\text{cm}^2 = 10^{-3}\\;\\text{m}^2$. "
            "זה עקרון גנרטור AC — סיבוב מכני הופך למתח מתחלף.\n\n"
            "**טעות נפוצה:** שכחת המרת cm² ל-m², או שימוש ב-$B$ "
            "במקום $NBA\\omega$ לערך שיא. בלבול בין שיא ל-RMS "
            "($\\mathcal{E}_{\\text{rms}} = \\mathcal{E}_0/\\sqrt{2}$).\n\n"
            "**טיפ לבחינה:** EMF שיא $\\propto \\omega$ — סיבוב מהיר יותר = "
            "מתח גבוה יותר. אם $\\omega$ מוכפל, $\\mathcal{E}_0$ מוכפל. "
            "זכרו: $\\mathcal{E}(t)$ הוא סinusoид, לא קבוע. **תשובה:** 1 V שיא."
        ),
    },
    {
        "explanation_en": (
            "An RL circuit approaching steady state follows "
            "$I(t) = I_\\infty(1 - e^{-t/\\tau})$ with $\\tau = L/R$. "
            "First find $\\tau = 0.2/5 = 0.04$ s and $I_\\infty = \\mathcal{E}/R = 10/5 = 2$ A. "
            "At $t = \\tau$ (one time constant):\n"
            "$$I(\\tau) = I_\\infty(1 - e^{-1}) = 2(1 - 0.368) = 1.264\\;\\text{A}$$\n\n"
            "The current has reached 63% of its final value — a standard RL milestone. "
            "At $t = 0$, current is zero (inductor blocks change); at $t \\to \\infty$, "
            "$I \\to 2$ A.\n\n"
            "**Common slip:** Using $I = \\mathcal{E}/R$ immediately (ignoring the "
            "inductor at $t = 0$), or evaluating at wrong $t$.\n\n"
            "**Exam tip:** At $t = \\tau$, current is always $63\\%$ of $I_\\infty$ "
            "regardless of specific $L$, $R$, $\\mathcal{E}$ values. **Answer:** 1.264 A."
        ),
        "explanation_he": (
            "מעגל RL המתקרב למצב מנוחה עוקב אחר "
            "$I(t) = I_\\infty(1 - e^{-t/\\tau})$ עם $\\tau = L/R$. "
            "ראשית $\\tau = 0.2/5 = 0.04$ s ו-$I_\\infty = \\mathcal{E}/R = 2$ A. "
            "ב-$t = \\tau$ (קבוע זמן אחד):\n"
            "$$I(\\tau) = 2(1 - e^{-1}) = 1.264\\;\\text{A}$$\n\n"
            "הזרם הגיע ל-63% מהערך הסופי — אבן דרך סטנדרטית ב-RL. "
            "ב-$t = 0$, זרם אפס (סליל חוסם שינוי); ב-$t \\to \\infty$, $I \\to 2$ A.\n\n"
            "**טעות נפוצה:** שימוש ב-$I = \\mathcal{E}/R$ מיד (התעלמות מהסליל "
            "ב-$t = 0$), או הערכה ב-$t$ שגוי.\n\n"
            "**טיפ לבחינה:** ב-$t = \\tau$, הזרם תמיד 63% מ-$I_\\infty$ "
            "בלי קשר ל-$L$, $R$, $\\mathcal{E}$. **תשובה:** 1.264 A."
        ),
    },
]


def apply_expansion(data):
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
            if n == 1:
                sec.update(SECTION_BODIES["worked_example_1"])
            elif n == 2:
                sec.update(SECTION_BODIES["worked_example_2"])
            elif n == 3:
                sec.update(SECTION_BODIES["worked_example_3"])
        elif kind == "checkpoint":
            body_en = sec.get("body_en_md", "")
            if "square loop" in body_en.lower() or "100" in body_en:
                sec.update(SECTION_BODIES["checkpoint_1"])
            else:
                sec.update(SECTION_BODIES["checkpoint_2"])
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
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
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
                issues.append(f"Q{q['ord']} {key}: {w} words")

    return issues


def main():
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)

    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("DEPTH ISSUES:")
        for i in issues:
            print(f"  - {i}")
        raise SystemExit(1)
    else:
        print("All depth gates passed.")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")

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
