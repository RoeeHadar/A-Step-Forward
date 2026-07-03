#!/usr/bin/env python3
"""Expand electromagnetic_induction.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/electromagnetic_induction.json"

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
            "In 1831, Michael Faraday discovered that a **changing magnetic flux** through "
            "a conducting loop induces an electromotive force (EMF) — voltage without any "
            "battery. Move a magnet toward a coil, rotate a loop in a field, or slide a "
            "rod through $B$: each case produces $\\mathcal{E}$. This is **electromagnetic "
            "induction**, the principle behind every power plant, transformer, induction "
            "cooktop, and wireless charger.\n\n"
            "The central quantity is **magnetic flux** through a surface:\n"
            "$$\\Phi = B \\cdot A \\cdot \\cos\\theta$$\n"
            "where $B$ is field strength (T), $A$ is loop area (m²), and $\\theta$ is the "
            "angle between $\\vec{B}$ and the **normal** to the loop. SI unit: Weber "
            "(Wb = T·m²). Only **changes** in $\\Phi$ matter — a constant flux induces "
            "nothing.\n\n"
            "**Bagrut relevance (questionnaire 2 — electricity):**\n"
            "- Calculate induced EMF from changing flux (Faraday's law)\n"
            "- Moving conductor in a magnetic field — $\\mathcal{E}=BLv$\n"
            "- Rotating coil generator — derive $\\mathcal{E}=NBA\\omega\\sin(\\omega t)$\n\n"
            "This lesson builds on `concept:magnetism` and leads directly to "
            "`concept:ac_circuits`."
        ),
        "body_he_md": (
            "בשנת 1831, מייקל פרדיי גילה ש**שטף מגנטי משתנה** דרך לולאה מוליכה מושרה "
            "כוח אלקטרו-מוטורי (כ\"א) — מתח ללא סוללה. הקרבת מגנט לסליל, סיבוב לולאה "
            "בשדה, או החלקת מוט דרך $B$ — בכל מקרה נוצר $\\mathcal{E}$. זוהי "
            "**השראה אלקטרומגנטית**, העקרון שעומד בבסיס כל מחולל חשמל, שנאי, "
            "כיריים אינדוקציה וטעינה אלחוטית.\n\n"
            "הכמות המרכזית היא **שטף מגנטי** דרך משטח:\n"
            "$$\\Phi = B \\cdot A \\cdot \\cos\\theta$$\n"
            "כאשר $B$ הוא עוצמת השדה (T), $A$ שטח הלולאה (מ²), ו-$\\theta$ הזווית "
            "בין $\\vec{B}$ ל**נורמל** של הלולאה. יחידת SI: וובר (Wb = T·מ²). "
            "רק **שינויים** ב-$\\Phi$ חשובים — שטף קבוע לא מושרה כלום.\n\n"
            "**רלוונטיות לבגרות (שאלון 2 — חשמל):**\n"
            "- חישוב כ\"א מושרה משטף משתנה (חוק פרדיי)\n"
            "- מוליך נע בשדה מגנטי — $\\mathcal{E}=BLv$\n"
            "- מחולל סליל מסתובב — גזירת $\\mathcal{E}=NBA\\omega\\sin(\\omega t)$\n\n"
            "שיעור זה מבוסס על `concept:magnetism` ומוביל ישירות ל-`concept:ac_circuits`."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Magnetic flux** through a flat loop:\n"
            "$$\\boxed{\\Phi = BA\\cos\\theta}$$\n"
            "$\\theta$ is measured between $\\vec{B}$ and the **outward normal** to the loop. "
            "Maximum flux when the loop face is perpendicular to $\\vec{B}$ ($\\theta=0°$); "
            "zero when the loop edge-on to the field ($\\theta=90°$).\n\n"
            "**Faraday's law of induction:**\n"
            "$$\\boxed{\\mathcal{E} = -\\frac{d\\Phi}{dt} \\approx -\\frac{\\Delta\\Phi}{\\Delta t}}$$\n"
            "For a coil with $N$ identical turns:\n"
            "$$\\mathcal{E} = -N\\frac{\\Delta\\Phi}{\\Delta t}$$\n"
            "The minus sign encodes **Lenz's law**: the induced EMF opposes the flux change "
            "that caused it.\n\n"
            "**Lenz's law (direction):** Ask whether flux is increasing or decreasing. "
            "The induced current creates a magnetic field that **opposes that change**. "
            "Use the right-hand rule on the induced current to find field direction.\n\n"
            "**EMF in a moving conductor** of length $L$, speed $v$, with $v$, $L$, and "
            "$B$ mutually perpendicular:\n"
            "$$\\boxed{\\mathcal{E} = BLv}$$\n"
            "This is equivalent to Faraday's law applied to the changing area swept by the rod.\n\n"
            "**SI units:** $\\mathcal{E}$ in volts (V); $\\Phi$ in webers (Wb); "
            "$B$ in tesla (T); $L$ in metres (m); $v$ in m/s."
        ),
        "body_he_md": (
            "**שטף מגנטי** דרך לולאה שטוחה:\n"
            "$$\\boxed{\\Phi = BA\\cos\\theta}$$\n"
            "$\\theta$ נמדדת בין $\\vec{B}$ ל**נורמל החיצוני** של הלולאה. "
            "שטף מרבי כשפני הלולאה ניצבים ל-$\\vec{B}$ ($\\theta=0°$); "
            "אפס כשהלולאה \"על קצה\" ($\\theta=90°$).\n\n"
            "**חוק פרדיי להשראה:**\n"
            "$$\\boxed{\\mathcal{E} = -\\frac{d\\Phi}{dt} \\approx -\\frac{\\Delta\\Phi}{\\Delta t}}$$\n"
            "לסליל עם $N$ כריכות זהות:\n"
            "$$\\mathcal{E} = -N\\frac{\\Delta\\Phi}{\\Delta t}$$\n"
            "סימן המינוס מקודד את **חוק לנץ**: הכ\"א המושרה מתנגד לשינוי השטף "
            "שגרם לו.\n\n"
            "**חוק לנץ (כיוון):** שאלו האם השטף עולה או יורד. הזרם המושרה "
            "יוצר שדה מגנטי ש**מתנגד לשינוי**. השתמשו בכלל יד ימין על הזרם "
            "המושרה כדי למצוא כיוון השדה.\n\n"
            "**כ\"א במוליך נע** באורך $L$, מהירות $v$, כאשר $v$, $L$ ו-$B$ "
            "מאונכים הדדית:\n"
            "$$\\boxed{\\mathcal{E} = BLv}$$\n"
            "זה שקול ליישום חוק פרדיי על השטח המשתנה שהמוט \"שואב\".\n\n"
            "**יחידות SI:** $\\mathcal{E}$ ב-volt (V); $\\Phi$ ב-weber (Wb); "
            "$B$ ב-tesla (T); $L$ במטר (m); $v$ ב-m/s."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Rotating coil generator\n\n"
            "A coil of $N$ turns, area $A$, rotates at angular velocity $\\omega$ in a "
            "uniform field $B$. If at $t=0$ the coil normal aligns with $\\vec{B}$ "
            "(maximum flux), then:\n"
            "$$\\Phi(t) = NBA\\cos(\\omega t)$$\n"
            "Faraday's law gives:\n"
            "$$\\mathcal{E}(t) = -N\\frac{d\\Phi}{dt} = NBA\\omega\\sin(\\omega t)$$\n"
            "$$\\boxed{\\mathcal{E}_{\\max} = NBA\\omega}$$\n"
            "This is **alternating** EMF (AC): sinusoidal, period $T=2\\pi/\\omega$. "
            "Peak EMF occurs when the coil plane is **parallel** to $\\vec{B}$ "
            "(flux changing fastest).\n\n"
            "### Ideal transformer\n\n"
            "Changing flux in the iron core links primary and secondary coils:\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p} = \\frac{I_p}{I_s}$$\n"
            "Step-up: $N_s > N_p$ → higher secondary voltage, lower secondary current. "
            "Power ideally conserved: $V_p I_p \\approx V_s I_s$.\n\n"
            "### Lenz's law — qualitative cases\n\n"
            "- **Magnet approaching loop:** flux increases → induced current creates "
            "opposing field → repels the magnet.\n"
            "- **Magnet retreating:** flux decreases → induced current tries to "
            "maintain flux → attracts the magnet back.\n"
            "- **Moving rod in $B$:** motional EMF $BLv$ drives current; Lenz's law "
            "gives braking force $F=BIL$ opposing the motion.\n\n"
            "### Self-inductance (5-unit extension)\n\n"
            "A changing current in a coil induces $\\mathcal{E}_L = -L\\,dI/dt$ where "
            "$L$ is inductance (henry, H). Appears in RL circuits and AC impedance."
        ),
        "body_he_md": (
            "### מחולל סליל מסתובב\n\n"
            "סליל של $N$ כריכות, שטח $A$, מסתובב במהירות זוויתית $\\omega$ בשדה "
            "אחיד $B$. אם ב-$t=0$ הנורמל של הסליל מיושר עם $\\vec{B}$ (שטף מרבי):\n"
            "$$\\Phi(t) = NBA\\cos(\\omega t)$$\n"
            "חוק פרדיי נותן:\n"
            "$$\\mathcal{E}(t) = -N\\frac{d\\Phi}{dt} = NBA\\omega\\sin(\\omega t)$$\n"
            "$$\\boxed{\\mathcal{E}_{\\max} = NBA\\omega}$$\n"
            "זוהי כ\"א **מתחלפת** (AC): סינוסואידלית, מחזור $T=2\\pi/\\omega$. "
            "כ\"א שיא כשמישור הסליל **מקביל** ל-$\\vec{B}$ (שטף משתנה במהירות מרבית).\n\n"
            "### שנאי אידיאלי\n\n"
            "שטף משתנה בליבת ברזל מקשר בין סליל ראשוני ומשני:\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p} = \\frac{I_p}{I_s}$$\n"
            "שנאי מעלה: $N_s > N_p$ → מתח משני גבוה יותר, זרם משני נמוך יותר. "
            "הספק נשמר (אידיאלי): $V_p I_p \\approx V_s I_s$.\n\n"
            "### חוק לנץ — מקרים איכותיים\n\n"
            "- **מגנט מתקרב ללולאה:** שטף עולה → זרם מושרה יוצר שדה מנוגד → "
            "דוחה את המגנט.\n"
            "- **מגנט מתרחק:** שטף יורד → זרם מושרה מנסה לשמור שטף → "
            "מושך את המגנט חזרה.\n"
            "- **מוט נע ב-$B$:** כ\"א תנועה $BLv$ מניע זרם; חוק לנץ נותן "
            "כוח בלימה $F=BIL$ נגד התנועה.\n\n"
            "### השראה עצמית (הרחבה ל-5 יחידות)\n\n"
            "זרם משתנה בסליל מושרה $\\mathcal{E}_L = -L\\,dI/dt$ כאשר "
            "$L$ הוא ההשראות (henry, H). מופיע במעגלי RL ובעכבה ב-AC."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** Magnetic flux through a single-turn coil changes from "
            "$\\Phi_1 = 0.5\\text{ Wb}$ to $\\Phi_2 = 0.1\\text{ Wb}$ in "
            "$\\Delta t = 2\\text{ s}$.\n\n"
            "**Find:** Induced EMF magnitude and direction (Lenz's law).\n\n"
            "### Move 1: Compute flux change\n"
            "$$\\Delta\\Phi = \\Phi_2 - \\Phi_1 = 0.1 - 0.5 = -0.4\\text{ Wb}$$\n"
            "The flux **decreases** through the loop.\n\n"
            "### Move 2: Apply Faraday's law\n"
            "$$\\mathcal{E} = -\\frac{\\Delta\\Phi}{\\Delta t} = -\\frac{-0.4}{2} "
            "= \\boxed{+0.2\\text{ V}}$$\n"
            "Single turn ($N=1$). Magnitude is $0.2$ V.\n\n"
            "### Move 3: Direction via Lenz's law\n"
            "Flux is decreasing, so the induced current creates a magnetic field "
            "in the **same direction** as the original flux to oppose the decrease. "
            "Use the right-hand rule on that induced field to find current direction.\n\n"
            "**Exam tip:** Always state whether flux rises or falls before applying "
            "Lenz's law. The minus sign in Faraday's law already encodes opposition.\n\n"
            "### Move 4: Sanity check\n"
            "Units: Wb/s = V ✓. Order of magnitude 0.2 V is reasonable for a "
            "0.4 Wb change over 2 s. If you got 0.8 V, you likely forgot the "
            "minus sign handling or divided by the wrong time interval."
        ),
        "body_he_md": (
            "**נתון:** השטף המגנטי דרך לולאה חד-כריכתית משתנה מ-$\\Phi_1=0.5\\text{ Wb}$ "
            "ל-$\\Phi_2=0.1\\text{ Wb}$ ב-$\\Delta t=2\\text{ ש}$.\n\n"
            "**מצא:** גודל כ\"א מושרה וכיוון (חוק לנץ).\n\n"
            "### צעד 1: חישוב שינוי שטף\n"
            "$$\\Delta\\Phi = 0.1-0.5 = -0.4\\text{ Wb}$$\n"
            "השטף **יורד** דרך הלולאה.\n\n"
            "### צעד 2: חוק פרדיי\n"
            "$$\\mathcal{E} = -\\frac{\\Delta\\Phi}{\\Delta t} = -\\frac{-0.4}{2} "
            "= \\boxed{+0.2\\text{ V}}$$\n"
            "כריכה אחת ($N=1$). הגודל: $0.2$ V.\n\n"
            "### צעד 3: כיוון — חוק לנץ\n"
            "השטף יורד, לכן הזרם המושרה יוצר שדה מגנטי **באותו כיוון** "
            "כמו השטף המקורי כדי להתנגד לירידה. השתמשו בכלל יד ימין "
            "על השדה המושרה כדי למצוא כיוון הזרם.\n\n"
            "**טיפ לבחינה:** ציינו תמיד האם השטף עולה או יורד לפני חוק לנץ. "
            "סימן המינוס בחוק פרדיי כבר מקודד התנגדות.\n\n"
            "### צעד 4: בדיקת סבירות\n"
            "יחידות: Wb/ש = V ✓. סדר גודל 0.2 V סביר לשינוי 0.4 Wb ב-2 ש. "
            "אם קיבלתם 0.8 V — כנראה טעות בסימן או בחלוקה בזמן."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A conducting rod of length $L = 0.1\\text{ m}$ moves at "
            "$v = 3\\text{ m/s}$ perpendicular to a uniform field $B = 0.5\\text{ T}$ "
            "(into the page). The rod slides on parallel rails forming a closed circuit "
            "with resistance $R = 1.5\\,\\Omega$.\n\n"
            "**Find:** (a) Induced EMF. (b) Induced current. (c) Force to maintain "
            "constant velocity.\n\n"
            "### Move 1: Motional EMF\n"
            "$$\\mathcal{E} = BLv = 0.5 \\times 0.1 \\times 3 = \\boxed{0.15\\text{ V}}$$\n"
            "Requires $v \\perp L \\perp B$ — all three mutually perpendicular.\n\n"
            "### Move 2: Current in the circuit\n"
            "$$I = \\frac{\\mathcal{E}}{R} = \\frac{0.15}{1.5} = \\boxed{0.1\\text{ A}}$$\n\n"
            "### Move 3: Braking force (Lenz's law)\n"
            "The induced current creates a magnetic force opposing motion:\n"
            "$$F = BIL = 0.5 \\times 0.1 \\times 0.1 = 0.005\\text{ N}$$\n"
            "To keep constant speed, an external force "
            "$\\boxed{F_{\\text{ext}} = 0.005\\text{ N}}$ must balance this.\n\n"
            "**Exam tip:** Motional EMF problems often chain $\\mathcal{E}=BLv$, "
            "$I=\\mathcal{E}/R$, and $F=BIL$. Energy dissipated as heat: $P=I^2R$.\n\n"
            "### Move 4: Power check\n"
            "$$P = I^2 R = (0.1)^2 \\times 1.5 = 0.015\\text{ W}$$\n"
            "The external agent must supply this power to maintain constant speed "
            "against the magnetic braking force — energy conservation in action."
        ),
        "body_he_md": (
            "**נתון:** מוט מוליך $L=0.1\\text{ מ'}$ נע ב-$v=3\\text{ מ/ש}$ מאונך "
            "לשדה $B=0.5\\text{ T}$ (לתוך הדף). המוט מחליק על מסילות מקבילות "
            "ומגדיר מעגל עם התנגדות $R=1.5\\,\\Omega$.\n\n"
            "**מצא:** (א) כ\"א מושרה. (ב) זרם. (ג) כוח לשמירת מהירות קבועה.\n\n"
            "### צעד 1: כ\"א תנועה\n"
            "$$\\mathcal{E} = BLv = 0.5 \\times 0.1 \\times 3 = \\boxed{0.15\\text{ V}}$$\n"
            "נדרש $v \\perp L \\perp B$ — שלושתם מאונכים הדדית.\n\n"
            "### צעד 2: זרם במעגל\n"
            "$$I = \\frac{\\mathcal{E}}{R} = \\frac{0.15}{1.5} = \\boxed{0.1\\text{ A}}$$\n\n"
            "### צעד 3: כוח בלימה (חוק לנץ)\n"
            "הזרם המושרה יוצר כוח מגנטי נגד התנועה:\n"
            "$$F = BIL = 0.5 \\times 0.1 \\times 0.1 = 0.005\\text{ N}$$\n"
            "לשמירת מהירות קבועה, כוח חיצוני "
            "$\\boxed{F_{\\text{חיצוני}}=0.005\\text{ N}}$ מאזן זאת.\n\n"
            "**טיפ לבחינה:** בעיות מוט נע משלבות $\\mathcal{E}=BLv$, "
            "$I=\\mathcal{E}/R$ ו-$F=BIL$. אנרגיה מת dissipates כחום: $P=I^2R$.\n\n"
            "### צעד 4: בדיקת הספק\n"
            "$$P = I^2 R = (0.1)^2 \\times 1.5 = 0.015\\text{ W}$$\n"
            "הסוכן החיצוני חייב לספק הספק זה לשמירת מהירות קבועה "
            "נגד כוח הבלימה המגנטי — שימור אנרגיה."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** A coil of $N$ turns, area $A$, rotates at angular velocity "
            "$\\omega$ in uniform field $B$. At $t=0$, the coil plane is perpendicular "
            "to $\\vec{B}$ (maximum flux).\n\n"
            "**Find:** Derive $\\mathcal{E}(t)$ and compute $\\mathcal{E}_{\\max}$ for "
            "$N=200$, $A=0.01\\text{ m}^2$, $B=0.5\\text{ T}$, $\\omega=100\\text{ rad/s}$.\n\n"
            "### Move 1: Flux as a function of time\n"
            "The angle between $\\vec{B}$ and the coil normal is $\\omega t$:\n"
            "$$\\Phi(t) = NBA\\cos(\\omega t)$$\n\n"
            "### Move 2: Differentiate (Faraday's law)\n"
            "$$\\mathcal{E}(t) = -N\\frac{d\\Phi}{dt} = -N\\frac{d}{dt}[BA\\cos(\\omega t)]$$\n"
            "$$\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)$$\n"
            "$$\\boxed{\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)}$$\n\n"
            "### Move 3: When is EMF maximum?\n"
            "$$\\mathcal{E}_{\\max} = NBA\\omega$$\n"
            "Occurs when $\\sin(\\omega t)=1$, i.e. coil plane **parallel** to "
            "$\\vec{B}$ (sides cutting field lines fastest).\n\n"
            "### Move 4: Numerical substitution\n"
            "$$\\mathcal{E}_{\\max} = 200 \\times 0.5 \\times 0.01 \\times 100 "
            "= \\boxed{100\\text{ V}}$$\n\n"
            "**Exam tip:** Convert rev/s to rad/s: $\\omega=2\\pi f$. "
            "RMS voltage for sinusoidal AC: $\\mathcal{E}_{\\text{rms}}=\\mathcal{E}_{\\max}/\\sqrt{2}$.\n\n"
            "### Move 5: RMS value for this example\n"
            "$$\\mathcal{E}_{\\text{rms}} = \\frac{100}{\\sqrt{2}} \\approx 70.7\\text{ V}$$\n"
            "Bagrut power questions often use RMS, not peak — read the stem carefully."
        ),
        "body_he_md": (
            "**נתון:** סליל $N$ כריכות, שטח $A$, מסתובב במהירות $\\omega$ בשדה "
            "אחיד $B$. ב-$t=0$: מישור הסליל מאונך ל-$\\vec{B}$ (שטף מרבי).\n\n"
            "**מצא:** גזור $\\mathcal{E}(t)$ וחשב $\\mathcal{E}_{\\max}$ עבור "
            "$N=200$, $A=0.01\\text{ מ}^2$, $B=0.5\\text{ T}$, $\\omega=100\\text{ rad/ש}$.\n\n"
            "### צעד 1: שטף כפונקציה של זמן\n"
            "הזווית בין $\\vec{B}$ לנורמל הסליל היא $\\omega t$:\n"
            "$$\\Phi(t) = NBA\\cos(\\omega t)$$\n\n"
            "### צעד 2: נגזרת (חוק פרדיי)\n"
            "$$\\mathcal{E}(t) = -N\\frac{d\\Phi}{dt} = -N\\frac{d}{dt}[BA\\cos(\\omega t)]$$\n"
            "$$\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)$$\n"
            "$$\\boxed{\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)}$$\n\n"
            "### צעד 3: מתי כ\"א מקסימלי?\n"
            "$$\\mathcal{E}_{\\max} = NBA\\omega$$\n"
            "כש-$\\sin(\\omega t)=1$, כלומר מישור הסליל **מקביל** ל-$\\vec{B}$ "
            "(צלעות חותכות קווי שדה במהירות מרבית).\n\n"
            "### צעד 4: הצבה מספרית\n"
            "$$\\mathcal{E}_{\\max} = 200 \\times 0.5 \\times 0.01 \\times 100 "
            "= \\boxed{100\\text{ V}}$$\n\n"
            "**טיפ לבחינה:** המירו סיבוב/ש ל-rad/ש: $\\omega=2\\pi f$. "
            "מתח RMS ל-AC סינוסoidal: $\\mathcal{E}_{\\text{rms}}=\\mathcal{E}_{\\max}/\\sqrt{2}$.\n\n"
            "### צעד 5: ערך RMS לדוגמה זו\n"
            "$$\\mathcal{E}_{\\text{rms}} = \\frac{100}{\\sqrt{2}} \\approx 70.7\\text{ V}$$\n"
            "שאלות הספק בבגרות לעיתים משתמשות ב-RMS, לא בשיא — קראו בעיון."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "**Step 1 — Identify given quantities:**\n"
            "$N=50$ turns, $\\Delta\\Phi = 0.4$ Wb, $\\Delta t = 0.5$ s.\n\n"
            "**Step 2 — Apply Faraday's law (magnitude):**\n"
            "$$\\mathcal{E} = N\\left|\\frac{\\Delta\\Phi}{\\Delta t}\\right| "
            "= 50 \\times \\frac{0.4}{0.5} = 50 \\times 0.8 = \\boxed{40\\text{ V}}$$\n\n"
            "**Step 3 — Direction (Lenz's law):**\n"
            "If flux is increasing, the induced current opposes the increase. "
            "Sketch the loop and apply the right-hand rule to confirm current direction.\n\n"
            "**Check:** Units Wb/s = V per turn; multiply by $N$ for total EMF."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — זיהוי נתונים:**\n"
            "$N=50$ כריכות, $\\Delta\\Phi = 0.4$ Wb, $\\Delta t = 0.5$ ש.\n\n"
            "**שלב 2 — חוק פרדיי (גודל):**\n"
            "$$\\mathcal{E} = N\\left|\\frac{\\Delta\\Phi}{\\Delta t}\\right| "
            "= 50 \\times \\frac{0.4}{0.5} = 50 \\times 0.8 = \\boxed{40\\text{ V}}$$\n\n"
            "**שלב 3 — כיוון (חוק לנץ):**\n"
            "אם השטף עולה, הזרם המושרה מתנגד לגידול. "
            "שרטטו את הלולאה והשתמשו בכלל יד ימין.\n\n"
            "**בדיקה:** יחידות Wb/ש = V לכריכה; הכפילו ב-$N$ לכ\"א כולל."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "**Step 1 — Recognise motional EMF setup:**\n"
            "A square loop side $L=0.2$ m moves at $v=5$ m/s perpendicular to "
            "$B=0.4$ T. Use the side **perpendicular to motion** as effective length.\n\n"
            "**Step 2 — Apply $\\mathcal{E}=BLv$:**\n"
            "$$\\mathcal{E} = BLv = 0.4 \\times 0.2 \\times 5 = \\boxed{0.4\\text{ V}}$$\n\n"
            "**Step 3 — Verify geometry:**\n"
            "All three — $B$, $v$, and $L$ — must be mutually perpendicular. "
            "If the loop moved parallel to $B$, EMF would be zero.\n\n"
            "**Check:** T·m/s = V ✓."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — זיהוי כ\"א תנועה:**\n"
            "לולאה ריבועית צלע $L=0.2$ מ' נעה ב-$v=5$ מ/ש מאונך ל-$B=0.4$ T. "
            "השתמשו בצלע **ניצבה לתנועה** כאורך אפקטיבי.\n\n"
            "**שלב 2 — $\\mathcal{E}=BLv$:**\n"
            "$$\\mathcal{E} = 0.4 \\times 0.2 \\times 5 = \\boxed{0.4\\text{ V}}$$\n\n"
            "**שלב 3 — אימות גאומטריה:**\n"
            "שלושתם — $B$, $v$ ו-$L$ — חייבים להיות מאונכים. "
            "אם הלולאה נעה מקביל ל-$B$, כ\"א = 0.\n\n"
            "**בדיקה:** T·מ/ש = V ✓."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "1. **Classify the problem:** Is flux changing (Faraday) or is a conductor "
            "moving through $B$ (motional EMF $BLv$)? Rotating coil → derive "
            "$\\mathcal{E}=NBA\\omega\\sin(\\omega t)$.\n\n"
            "2. **Compute flux if needed:** $\\Phi = BA\\cos\\theta$. Identify what "
            "changes — $B$, $A$, or $\\theta$ — and find $\\Delta\\Phi$.\n\n"
            "3. **Apply Faraday's law:** $\\mathcal{E} = -N\\Delta\\Phi/\\Delta t$. "
            "For magnitude in Bagrut numerics, often use $N|\\Delta\\Phi/\\Delta t|$.\n\n"
            "4. **Direction — Lenz's law:** Flux increasing → induced field opposes "
            "increase. Flux decreasing → induced field tries to restore flux. "
            "Right-hand rule on induced current.\n\n"
            "5. **Complete the circuit:** $I=\\mathcal{E}/R$, power $P=\\mathcal{E}I$ "
            "or $P=I^2R$. For moving rods: braking force $F=BIL$.\n\n"
            "6. **Transformers:** $V_s/V_p=N_s/N_p$; current ratio is inverse. "
            "Check power consistency.\n\n"
            "**Before submitting:** Did you include $N$? Are $v$, $L$, $B$ perpendicular?"
        ),
        "body_he_md": (
            "1. **סווגו את הבעיה:** האם השטף משתנה (פרדיי) או מוליך נע ב-$B$ "
            "(כ\"א תנועה $BLv$)? סליל מסתובב → גזרו $\\mathcal{E}=NBA\\omega\\sin(\\omega t)$.\n\n"
            "2. **חשבו שטף אם נדרש:** $\\Phi = BA\\cos\\theta$. זהו מה משתנה — "
            "$B$, $A$ או $\\theta$ — ומצאו $\\Delta\\Phi$.\n\n"
            "3. **חוק פרדיי:** $\\mathcal{E} = -N\\Delta\\Phi/\\Delta t$. "
            "לגודל בבגרות, לעיתים $N|\\Delta\\Phi/\\Delta t|$.\n\n"
            "4. **כיוון — חוק לנץ:** שטף עולה → שדה מושרה מנגד לגידול. "
            "שטף יורד → שדה מושרה מנסה לשחזר. כלל יד ימין על הזרם.\n\n"
            "5. **השלימו מעגל:** $I=\\mathcal{E}/R$, הספק $P=\\mathcal{E}I$ "
            "או $P=I^2R$. למוטות נעים: כוח בלימה $F=BIL$.\n\n"
            "6. **שנאים:** $V_s/V_p=N_s/N_p$; יחס זרם הפוך. "
            "בדקו עקביות הספק.\n\n"
            "**לפני הגשה:** הכללתם $N$? האם $v$, $L$, $B$ מאונכים?"
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Ignoring the minus sign in Faraday's law.** It encodes Lenz's law. "
            "For magnitude use $|\\Delta\\Phi/\\Delta t|$; determine direction separately "
            "by asking whether flux increases or decreases.\n\n"
            "2. **Forgetting to multiply by $N$.** A 50-turn coil gives 50× the EMF "
            "of a single turn for the same flux change. Always check the stem for "
            "\"turns\" or \"coil.\"\n\n"
            "3. **Confusing $\\mathcal{E}_{\\max}$ and $\\mathcal{E}_{\\text{rms}}$.** "
            "Peak EMF from a generator is $NBA\\omega$; RMS value for AC power is "
            "$\\mathcal{E}_{\\max}/\\sqrt{2}$. Bagrut may ask either — read carefully.\n\n"
            "4. **Using $\\mathcal{E}=BLv$ without perpendicular geometry.** "
            "If the rod moves parallel to $\\vec{B}$, EMF is zero. Only the "
            "component of velocity perpendicular to both $L$ and $B$ counts.\n\n"
            "5. **Transformer current/voltage ratio confusion.** Voltage ratio equals "
            "turn ratio $N_s/N_p$; current ratio is the **inverse** $N_p/N_s$."
        ),
        "body_he_md": (
            "1. **התעלמות מסימן המינוס בחוק פרדיי.** הוא מקודד את חוק לנץ. "
            "לגודל: $|\\Delta\\Phi/\\Delta t|$; לכיוון — שאלו האם השטף עולה או יורד.\n\n"
            "2. **שכחת הכפלה ב-$N$.** סליל 50 כריכות נותן פי 50 כ\"א "
            "מלולאה חד-כריכתית. תמיד בדקו \"כריכות\" או \"סליל\".\n\n"
            "3. **ערבוב $\\mathcal{E}_{\\max}$ ו-$\\mathcal{E}_{\\text{rms}}$.** "
            "שיא ממחולל: $NBA\\omega$; RMS לחישובי הספק AC: "
            "$\\mathcal{E}_{\\max}/\\sqrt{2}$. בבגרות — קראו בעיון.\n\n"
            "4. **שימוש ב-$\\mathcal{E}=BLv$ בלי גאומטריה ניצבת.** "
            "מוט מקביל ל-$\\vec{B}$ → כ\"א אפס. רק רכיב המהירות "
            "הניצב ל-$L$ ו-$B$ נספר.\n\n"
            "5. **בלבול יחסי זרם/מתח בשנאי.** יחס מתח = $N_s/N_p$; "
            "יחס זרם = **הפוך** $N_p/N_s$."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Electromagnetic induction is how we **generate** almost all electricity "
            "and **transform** it for transmission. Without Faraday's law, there are "
            "no power plants, no grid transformers, and no AC motors.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:ac_circuits` **AC Circuits** (direct prerequisite)\n"
            "- `concept:optics_physical` **Physical Optics** — light as an EM wave\n\n"
            "**Builds on:**\n"
            "- `concept:magnetism` **Magnetism & Magnetic Forces**\n\n"
            "**Why it matters for exams:** Bagrut questionnaire 2 regularly combines "
            "flux change, motional EMF, and generator formulas. Transfer questions "
            "test whether you can pick the right method from the problem wording alone."
        ),
        "body_he_md": (
            "השראה אלקטרומגנטית היא האופן שבו **מייצרים** כמעט את כל החשמל "
            "ו**משנים** אותו להולכה. בלי חוק פרדיי — אין מחוללים, אין שנאי רשת, "
            "ואין מנועי AC.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:ac_circuits` **מעגלי זרם חילופין** (דרישה ישירה)\n"
            "- `concept:optics_physical` **אופטיקה פיזיקלית** — אור כגל EM\n\n"
            "**מבוסס על:**\n"
            "- `concept:magnetism` **מגנטיות וכוחות מגנטיים**\n\n"
            "**למה זה חשוב לבחינות:** שאלון 2 בבגרות משלב לעיתים קרובות "
            "שינוי שטף, כ\"א תנועה ונוסחאות מחולל. שאלות העברה בודקות "
            "אם תוכלו לבחור שיטה נכונה מניסוח הבעיה בלבד."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "### Formula sheet\n\n"
            "$$\\Phi = BA\\cos\\theta \\qquad \\mathcal{E} = -N\\frac{\\Delta\\Phi}{\\Delta t} "
            "\\qquad \\mathcal{E} = BLv$$\n"
            "$$\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t) \\qquad "
            "\\mathcal{E}_{\\max} = NBA\\omega$$\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p} = \\frac{I_p}{I_s}$$\n\n"
            "### Checklist\n"
            "- [ ] Flux: correct $\\cos\\theta$ and angle definition?\n"
            "- [ ] Number of turns $N$ included?\n"
            "- [ ] Lenz's law direction determined?\n"
            "- [ ] Moving conductor: $v$, $L$, $B$ mutually perpendicular?\n"
            "- [ ] Generator: converted rev/s → rad/s ($\\omega=2\\pi f$)?\n\n"
            "**Last review:** Derive $\\mathcal{E}=NBA\\omega\\sin(\\omega t)$ once "
            "from $\\Phi=NBA\\cos(\\omega t)$, then solve one checkpoint without notes.\n\n"
            "**Common Bagrut traps:** (1) Using $\\omega$ in rev/s instead of rad/s. "
            "(2) Peak vs RMS confusion. (3) Forgetting $N$ in multi-turn coils. "
            "(4) Applying $BLv$ when the conductor moves parallel to $\\vec{B}$. "
            "Sketch the geometry before choosing a formula."
        ),
        "body_he_md": (
            "### דף נוסחאות\n\n"
            "$$\\Phi = BA\\cos\\theta \\qquad \\mathcal{E} = -N\\frac{\\Delta\\Phi}{\\Delta t} "
            "\\qquad \\mathcal{E} = BLv$$\n"
            "$$\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t) \\qquad "
            "\\mathcal{E}_{\\max} = NBA\\omega$$\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p} = \\frac{I_p}{I_s}$$\n\n"
            "### רשימת בדיקה\n"
            "- [ ] שטף: $\\cos\\theta$ והגדרת זווית נכונים?\n"
            "- [ ] מספר כריכות $N$ נכלל?\n"
            "- [ ] כיוון לנץ נקבע?\n"
            "- [ ] מוליך נע: $v$, $L$, $B$ מאונכים הדדית?\n"
            "- [ ] מחולל: המרת סיבוב/ש → rad/ש ($\\omega=2\\pi f$)?\n\n"
            "**חזרה אחרונה:** גזרו $\\mathcal{E}=NBA\\omega\\sin(\\omega t)$ פעם "
            "מ-$\\Phi=NBA\\cos(\\omega t)$, ואז פתרו checkpoint אחד בלי רשימות.\n\n"
            "**מלכודות נפוצות בבגרות:** (1) $\\omega$ בסיבוב/ש במקום rad/ש. "
            "(2) בלבול שיא ו-RMS. (3) שכחת $N$ בסלילים. "
            "(4) $BLv$ כשהמוליך נע מקביל ל-$\\vec{B}$. "
            "שרטטו גאומטריה לפני בחירת נוסחה."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Magnetic flux:** $\\Phi = BA\\cos\\theta$ (Wb) — only **changes** induce EMF.\n"
            "- **Faraday's law:** $\\mathcal{E} = -N\\Delta\\Phi/\\Delta t$ (V); minus = Lenz.\n"
            "- **Moving conductor:** $\\mathcal{E} = BLv$ when $v \\perp L \\perp B$.\n"
            "- **Generator:** $\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)$; "
            "peak $\\mathcal{E}_{\\max} = NBA\\omega$.\n"
            "- **Lenz's law:** induced effects oppose the flux change that caused them.\n"
            "- **Transformer:** $V_s/V_p = N_s/N_p$; $I_s/I_p = N_p/N_s$.\n"
            "- **Braking force on rod:** $F = BIL$ opposes motion.\n\n"
            "**Takeaway:** From the problem wording alone, decide: flux change, "
            "motional EMF, rotating coil, or transformer — then apply the matching formula."
        ),
        "body_he_md": (
            "- **שטף מגנטי:** $\\Phi = BA\\cos\\theta$ (Wb) — רק **שינויים** מושרים כ\"א.\n"
            "- **חוק פרדיי:** $\\mathcal{E} = -N\\Delta\\Phi/\\Delta t$ (V); מינוס = לנץ.\n"
            "- **מוליך נע:** $\\mathcal{E} = BLv$ כש-$v \\perp L \\perp B$.\n"
            "- **מחולל:** $\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)$; "
            "שיא $\\mathcal{E}_{\\max} = NBA\\omega$.\n"
            "- **חוק לנץ:** השפעות מושרות מתנגדות לשינוי השטף.\n"
            "- **שנאי:** $V_s/V_p = N_s/N_p$; $I_s/I_p = N_p/N_s$.\n"
            "- **כוח בלימה על מוט:** $F = BIL$ נגד התנועה.\n\n"
            "**מסקנה:** מניסוח הבעיה בלבד — שינוי שטף, כ\"א תנועה, "
            "סליל מסתובב או שנאי — ואז הנוסחה המתאימה."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "Faraday's law for a single-turn coil: $\\mathcal{E} = -\\Delta\\Phi/\\Delta t$. "
            "Flux changes from 0 to 0.6 Wb in 0.3 s, so the rate of change is "
            "$\\Delta\\Phi/\\Delta t = 0.6/0.3 = 2$ Wb/s. Therefore:\n"
            "$$\\mathcal{E} = \\frac{0.6 - 0}{0.3} = \\boxed{2\\text{ V}}$$\n"
            "(Magnitude; $N=1$ so no extra factor.)\n\n"
            "The flux **increases**, so Lenz's law says the induced current opposes "
            "that increase — but the question asks for EMF magnitude only. "
            "A constant flux would give zero EMF; only the **change** matters.\n\n"
            "**Common slip:** Dividing $\\Delta t/\\Delta\\Phi$ instead of the reverse, "
            "or forgetting that Wb/s equals volts per turn.\n\n"
            "**Exam tip:** Write $\\mathcal{E}=\\Delta\\Phi/\\Delta t$ first, then "
            "substitute numbers. Check units: Wb/s = V. **Answer:** 2 V."
        ),
        "explanation_he": (
            "חוק פרדיי ללולאה חד-כריכתית: $\\mathcal{E} = -\\Delta\\Phi/\\Delta t$. "
            "השטף משתנה מ-0 ל-0.6 Wb ב-0.3 ש, כלומר קצב השינוי "
            "$\\Delta\\Phi/\\Delta t = 0.6/0.3 = 2$ Wb/ש. לכן:\n"
            "$$\\mathcal{E} = \\frac{0.6 - 0}{0.3} = \\boxed{2\\text{ V}}$$\n"
            "(גודל; $N=1$ — אין גורם נוסף.)\n\n"
            "השטף **עולה**, לכן חוק לנץ אומר שהזרם המושרה מתנגד לגידול — "
            "אך השאלה שואלת רק על גודל הכ\"א. שטף קבוע היה נותן כ\"א אפס; "
            "רק **השינוי** חשוב.\n\n"
            "**טעות נפוצה:** חלוקה $\\Delta t/\\Delta\\Phi$ במקום ההפך, "
            "או שכחה ש-Wb/ש = volt לכריכה.\n\n"
            "**טיפ לבחינה:** כתבו $\\mathcal{E}=\\Delta\\Phi/\\Delta t$ קודם, "
            "ואז הציבו מספרים. בדקו יחידות: Wb/ש = V. **תשובה:** 2 V."
        ),
    },
    {
        "explanation_en": (
            "Multi-turn coil: multiply Faraday's law by $N$. Here $N=100$, "
            "$\\Delta\\Phi=0.02$ Wb, $\\Delta t=0.1$ s. First find the rate "
            "per turn: $0.02/0.1 = 0.2$ V per turn. Then:\n"
            "$$\\mathcal{E} = N\\frac{\\Delta\\Phi}{\\Delta t} = 100 \\times "
            "\\frac{0.02}{0.1} = 100 \\times 0.2 = \\boxed{20\\text{ V}}$$\n\n"
            "Each turn contributes the same EMF; they add in series like "
            "batteries in series. This is why generator coils have many turns — "
            "to boost output voltage.\n\n"
            "**Common slip:** Using $\\Delta\\Phi/\\Delta t = 0.2$ V and stopping "
            "without multiplying by 100 — a very frequent Bagrut error.\n\n"
            "**Exam tip:** Circle $N$ in the stem before calculating. If the stem "
            "says \"coil\" or \"turns\", always check whether $N>1$. **Answer:** 20 V."
        ),
        "explanation_he": (
            "סליל רב-כריכות: הכפילו את חוק פרדיי ב-$N$. כאן $N=100$, "
            "$\\Delta\\Phi=0.02$ Wb, $\\Delta t=0.1$ ש. קודם קצב לכריכה: "
            "$0.02/0.1 = 0.2$ V. אחר כך:\n"
            "$$\\mathcal{E} = N\\frac{\\Delta\\Phi}{\\Delta t} = 100 \\times "
            "\\frac{0.02}{0.1} = 100 \\times 0.2 = \\boxed{20\\text{ V}}$$\n\n"
            "כל כריכה תורמת אותו כ\"א; הן מתווספות בטור כמו סוללות בטור. "
            "לכן למחוללים יש הרבה כריכות — להגברת מתח.\n\n"
            "**טעות נפוצה:** $\\Delta\\Phi/\\Delta t = 0.2$ V ובלי הכפלה ב-100 — "
            "טעות נפוצה מאוד בבגרות.\n\n"
            "**טיפ לבחינה:** סמנו $N$ בנתון לפני החישוב. אם כתוב \"סליל\" "
            "או \"כריכות\" — בדקו האם $N>1$. אם קיבלתם 0.2 V — שכחתם "
            "את הכפל ב-100. **תשובה:** 20 V."
        ),
    },
    {
        "explanation_en": (
            "Motional EMF: a conductor of length $L$ moving at speed $v$ "
            "perpendicular to field $B$ gives $\\mathcal{E}=BLv$. "
            "This arises because the rod \"sweeps\" flux at rate $B\\cdot L\\cdot v$. "
            "Here $B=0.2$ T, $L=0.5$ m, $v=4$ m/s:\n"
            "$$\\mathcal{E} = 0.2 \\times 0.5 \\times 4 = \\boxed{0.4\\text{ V}}$$\n\n"
            "The stem states perpendicular geometry — no $\\sin\\theta$ factor needed. "
            "This is the classic \"rod on rails\" setup tested often in Bagrut.\n\n"
            "**Common slip:** Using Faraday's flux formula when motional EMF "
            "applies directly, or swapping $L$ and $v$ values. "
            "If the rod moved parallel to $B$, EMF would be zero.\n\n"
            "**Exam tip:** \"Rod moving in B\" → try $\\mathcal{E}=BLv$ first. "
            "Verify $v \\perp L \\perp B$ with a quick sketch. **Answer:** 0.4 V."
        ),
        "explanation_he": (
            "כ\"א תנועה: מוליך באורך $L$ הנע במהירות $v$ מאונך ל-$B$ "
            "נותן $\\mathcal{E}=BLv$. זה נובע מ\"שאיבת\" שטף בקצב $B\\cdot L\\cdot v$. "
            "כאן $B=0.2$ T, $L=0.5$ מ', $v=4$ מ/ש:\n"
            "$$\\mathcal{E} = 0.2 \\times 0.5 \\times 4 = \\boxed{0.4\\text{ V}}$$\n\n"
            "הנתון מציין גאומטריה ניצבת — אין גורם $\\sin\\theta$. "
            "זה setup קלאסי של \"מוט על מסילות\" שנבחן הרבה בבגרות.\n\n"
            "**טעות נפוצה:** שימוש בנוסחת שטף כש-$BLv$ ישיר, "
            "או החלפת $L$ ו-$v$. אם המוט נע מקביל ל-$B$, כ\"א = 0.\n\n"
            "**טיפ לבחינה:** \"מוט נע ב-B\" → נסו $\\mathcal{E}=BLv$ קודם. "
            "אמתו $v \\perp L \\perp B$ בסקיצה. **תשובה:** 0.4 V."
        ),
    },
    {
        "explanation_en": (
            "Magnetic flux through a loop: $\\Phi = BA\\cos\\theta$. "
            "The field is **perpendicular** to the loop face, meaning $\\vec{B}$ is "
            "parallel to the loop normal, so $\\theta=0°$ and $\\cos0°=1$:\n"
            "$$\\Phi = BA = 0.5 \\times 0.04 = \\boxed{0.02\\text{ Wb}}$$\n\n"
            "Flux is not EMF — a constant flux induces zero voltage. "
            "This question tests whether you distinguish $\\Phi$ (state) from "
            "$\\mathcal{E}$ (rate of flux change). Many students apply Faraday's "
            "law here by mistake.\n\n"
            "**Common slip:** Confusing \"perpendicular to loop\" with "
            "$\\theta=90°$ (which would give zero flux). The angle is measured "
            "between $\\vec{B}$ and the **normal**, not the loop plane.\n\n"
            "**Exam tip:** Draw the normal arrow — if it aligns with $\\vec{B}$, "
            "$\\theta=0°$. **Answer:** 0.02 Wb."
        ),
        "explanation_he": (
            "שטף מגנטי דרך לולאה: $\\Phi = BA\\cos\\theta$. "
            "השדה **מאונך** לפני הלולאה, כלומר $\\vec{B}$ מקביל לנורמל, "
            "אז $\\theta=0°$ ו-$\\cos0°=1$:\n"
            "$$\\Phi = BA = 0.5 \\times 0.04 = \\boxed{0.02\\text{ Wb}}$$\n\n"
            "שטף אינו כ\"א — שטף קבוע לא מושרה מתח. "
            "השאלה בודקת הבחנה בין $\\Phi$ (מצב) ל-$\\mathcal{E}$ (קצב שינוי). "
            "רבים מיישמים בטעות חוק פרדיי כאן.\n\n"
            "**טעות נפוצה:** בלבול \"מאונך ללולאה\" עם "
            "$\\theta=90°$ (שיתן שטף אפס). הזווית נמדדת בין $\\vec{B}$ "
            "ל**נורמל**, לא למישור הלולאה.\n\n"
            "**טיפ לבחינה:** שרטטו חץ נורמל — אם מיושר עם $\\vec{B}$, "
            "$\\theta=0°$. **תשובה:** 0.02 Wb."
        ),
    },
    {
        "explanation_en": (
            "The field drops from 0.4 T to 0.1 T while area stays fixed at "
            "$A=0.05$ m². When only $B$ changes, flux change per turn is:\n"
            "$$\\Delta\\Phi = A\\Delta B = 0.05 \\times (0.1 - 0.4) = -0.015\\text{ Wb}$$\n"
            "With $N=200$ turns and $\\Delta t=0.1$ s:\n"
            "$$\\mathcal{E} = N\\left|\\frac{\\Delta\\Phi}{\\Delta t}\\right| = "
            "200 \\times \\frac{0.015}{0.1} = \\boxed{30\\text{ V}}$$\n\n"
            "The negative $\\Delta\\Phi$ means flux decreases; Lenz's law "
            "would give positive EMF by Faraday's sign convention. "
            "For magnitude, use the absolute value of $\\Delta\\Phi$.\n\n"
            "**Common slip:** Using $\\Delta B = 0.3$ but forgetting "
            "to multiply by area $A$, giving 60 V instead of 30 V.\n\n"
            "**Exam tip:** Identify what changes: $B$, $A$, or $\\theta$. "
            "Write $\\Delta\\Phi$ explicitly before dividing by $\\Delta t$. **Answer:** 30 V."
        ),
        "explanation_he": (
            "השדה יורד מ-0.4 T ל-0.1 T בעוד השטח קבוע $A=0.05$ מ². "
            "כש-$B$ בלבד משתנה, שינוי שטף לכריכה:\n"
            "$$\\Delta\\Phi = A\\Delta B = 0.05 \\times (0.1 - 0.4) = -0.015\\text{ Wb}$$\n"
            "עם $N=200$ כריכות ו-$\\Delta t=0.1$ ש:\n"
            "$$\\mathcal{E} = N\\left|\\frac{\\Delta\\Phi}{\\Delta t}\\right| = "
            "200 \\times \\frac{0.015}{0.1} = \\boxed{30\\text{ V}}$$\n\n"
            "$\\Delta\\Phi$ שלילי — שטף יורד; חוק לנץ נותן כ\"א חיובי. "
            "לגודל, השתמשו בערך מוחלט של $\\Delta\\Phi$.\n\n"
            "**טעות נפוצה:** $\\Delta B = 0.3$ אך שכחת הכפלה ב-$A$, "
            "נותן 60 V במקום 30 V.\n\n"
            "**טיפ לבחינה:** זהו מה משתנה: $B$, $A$ או $\\theta$. "
            "כתבו $\\Delta\\Phi$ במפורש לפני חלוקה ב-$\\Delta t$. **תשובה:** 30 V."
        ),
    },
    {
        "explanation_en": (
            "Chain three formulas for a moving rod in a closed circuit. "
            "First motional EMF with $B=0.8$ T, $L=0.3$ m, $v=2$ m/s:\n"
            "$$\\mathcal{E} = BLv = 0.8 \\times 0.3 \\times 2 = 0.48\\text{ V}$$\n"
            "Then Ohm's law with $R=0.5\\,\\Omega$:\n"
            "$$I = \\frac{\\mathcal{E}}{R} = \\frac{0.48}{0.5} = 0.96\\text{ A}$$\n"
            "Braking force from Lenz's law:\n"
            "$$F = BIL = 0.8 \\times 0.96 \\times 0.3 \\approx \\boxed{0.23\\text{ N}}$$\n\n"
            "The induced current creates a force opposing the rod's motion — "
            "you must push harder to maintain constant speed. "
            "Power dissipated: $P=I^2R \\approx 0.46$ W.\n\n"
            "**Common slip:** Calculating EMF correctly but using wrong $L$ "
            "(total wire vs segment in field).\n\n"
            "**Exam tip:** $\\mathcal{E} \\to I \\to F$ is the standard chain. "
            "**Answer:** $I=0.96$ A, $F\\approx0.23$ N."
        ),
        "explanation_he": (
            "שרשרת שלוש נוסחאות למוט נע במעגל סגור. "
            "ראשית כ\"א תנועה עם $B=0.8$ T, $L=0.3$ מ', $v=2$ מ/ש:\n"
            "$$\\mathcal{E} = BLv = 0.8 \\times 0.3 \\times 2 = 0.48\\text{ V}$$\n"
            "אחר כך חוק אום עם $R=0.5\\,\\Omega$:\n"
            "$$I = \\frac{\\mathcal{E}}{R} = \\frac{0.48}{0.5} = 0.96\\text{ A}$$\n"
            "כוח בלימה מחוק לנץ:\n"
            "$$F = BIL = 0.8 \\times 0.96 \\times 0.3 \\approx \\boxed{0.23\\text{ N}}$$\n\n"
            "הזרם המושרה יוצר כוח נגד תנועת המוט — "
            "צריך לדחוף חזק יותר לשמירת מהירות קבועה. "
            "הספק: $P=I^2R \\approx 0.46$ W.\n\n"
            "**טעות נפוצה:** כ\"א נכון אך $L$ שגוי "
            "(אורך מעגל vs קטע בשדה).\n\n"
            "**טיפ לבחינה:** $\\mathcal{E} \\to I \\to F$ — השרשרת הסטנדרטית. "
            "אם קיבלתם $F$ גדול פי 10 — בדקו את $L$ בשדה. "
            "**תשובה:** $I=0.96$ A, $F\\approx0.23$ N."
        ),
    },
    {
        "explanation_en": (
            "Ideal transformer relations link primary and secondary via "
            "changing flux in the iron core. Secondary voltage from turn ratio:\n"
            "$$V_s = V_p \\frac{N_s}{N_p} = 220 \\times \\frac{50}{500} = "
            "\\boxed{22\\text{ V}}$$\n"
            "This is a **step-down** transformer ($N_s < N_p$): fewer secondary "
            "turns → lower voltage. Current ratio is **inverse**:\n"
            "$$I_s = I_p \\frac{N_p}{N_s} = 0.5 \\times \\frac{500}{50} = "
            "\\boxed{5\\text{ A}}$$\n\n"
            "Power check: $V_p I_p = 220 \\times 0.5 = 110$ W and "
            "$V_s I_s = 22 \\times 5 = 110$ W — consistent for an ideal transformer.\n\n"
            "**Common slip:** Using the same ratio for both $V$ and $I$ "
            "(both divided by 10) instead of inverse for current.\n\n"
            "**Exam tip:** Higher turns → higher voltage, lower current. "
            "Write both ratios before calculating. **Answer:** $V_s=22$ V, $I_s=5$ A."
        ),
        "explanation_he": (
            "יחסי שנאי אידיאלי מקשרים ראשוני ומשני דרך שטף משתנה בליבה. "
            "מתח משני מיחס כריכות:\n"
            "$$V_s = V_p \\frac{N_s}{N_p} = 220 \\times \\frac{50}{500} = "
            "\\boxed{22\\text{ V}}$$\n"
            "זהו **שנאי מוריד** ($N_s < N_p$): פחות כריכות משניות → מתח נמוך. "
            "יחס זרם **הפוך**:\n"
            "$$I_s = I_p \\frac{N_p}{N_s} = 0.5 \\times \\frac{500}{50} = "
            "\\boxed{5\\text{ A}}$$\n\n"
            "בדיקת הספק: $V_p I_p = 110$ W ו-$V_s I_s = 22 \\times 5 = 110$ W — "
            "עקבי לשנאי אידיאלי.\n\n"
            "**טעות נפוצה:** אותו יחס ל-$V$ ול-$I$ "
            "במקום הפוך לזרם.\n\n"
            "**טיפ לבחינה:** יותר כריכות → מתח גבוה, זרם נמוך. "
            "כתבו שני יחסים לפני חישוב. אם $I_s=0.5$ A — השתמשתם "
            "ביחס מתח גם לזרם. **תשובה:** $V_s=22$ V, $I_s=5$ A."
        ),
    },
    {
        "explanation_en": (
            "Generator peak EMF: $\\mathcal{E}_{\\max}=NBA\\omega$. "
            "The stem gives 50 rev/s — you must convert to rad/s first:\n"
            "$$\\omega = 2\\pi \\times 50 = 314\\text{ rad/s}$$\n"
            "Then substitute $N=100$, $B=0.5$ T, $A=0.02$ m²:\n"
            "$$\\mathcal{E}_{\\max} = 100 \\times 0.5 \\times 0.02 \\times 314 "
            "\\approx \\boxed{314\\text{ V}}$$\n\n"
            "Peak EMF occurs when the coil plane is parallel to $\\vec{B}$ "
            "(flux changing fastest). RMS would be $314/\\sqrt{2} \\approx 222$ V.\n\n"
            "**Common slip:** Using $\\omega=50$ instead of $2\\pi\\times50$, "
            "giving roughly 50 V instead of 314 V — off by a factor of $2\\pi$.\n\n"
            "**Exam tip:** Always write $\\omega=2\\pi f$ before substituting "
            "into $NBA\\omega$. Label peak vs RMS in your answer. **Answer:** $\\approx314$ V."
        ),
        "explanation_he": (
            "כ\"א שיא ממחולל: $\\mathcal{E}_{\\max}=NBA\\omega$. "
            "הנתון: 50 סיבוב/ש — חובה להמיר ל-rad/ש:\n"
            "$$\\omega = 2\\pi \\times 50 = 314\\text{ rad/s}$$\n"
            "אחר כך $N=100$, $B=0.5$ T, $A=0.02$ מ²:\n"
            "$$\\mathcal{E}_{\\max} = 100 \\times 0.5 \\times 0.02 \\times 314 "
            "\\approx \\boxed{314\\text{ V}}$$\n\n"
            "כ\"א שיא כשמישור הסליל מקביל ל-$\\vec{B}$ (שטף משתנה מהר). "
            "RMS היה $314/\\sqrt{2} \\approx 222$ V.\n\n"
            "**טעות נפוצה:** $\\omega=50$ במקום $2\\pi\\times50$, "
            "נותן ~50 V במקום ~314 V — טעות בגורם $2\\pi$.\n\n"
            "**טיפ לבחינה:** כתבו $\\omega=2\\pi f$ לפני ההצבה "
            "ב-$NBA\\omega$. סמנו שיא vs RMS. אם קיבלתם ~50 V — "
            "שכחתם את $2\\pi$. זכרו: סיבוב/ש $\\neq$ rad/ש. **תשובה:** $\\approx314$ V."
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
