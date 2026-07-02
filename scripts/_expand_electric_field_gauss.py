#!/usr/bin/env python3
"""Expand electric_field_gauss.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/electric_field_gauss.json"

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
            "Coulomb's law can compute the electric field of any charge distribution — "
            "but only if you integrate over every charge element. For a cloud of billions "
            "of electrons, that integral is impractical. **Gauss's law** provides a "
            "dramatic shortcut: for charge distributions with **high symmetry**, you can "
            "find $\\vec{E}$ in three lines of algebra instead of a triple integral.\n\n"
            "The law relates the **total electric flux** through any closed surface to the "
            "charge enclosed inside: $\\Phi = Q_{\\text{enc}}/\\epsilon_0$. When the field "
            "is uniform on a cleverly chosen Gaussian surface, you pull $E$ out of the "
            "integral and solve directly.\n\n"
            "**In Israeli university physics** (Electromagnetism I), Gauss's law is the "
            "standard tool for finding $\\vec{E}$:\n"
            "- Outside and inside a charged sphere or shell\n"
            "- Near an infinite sheet or slab of charge\n"
            "- Near an infinite line or cylindrical shell\n\n"
            "This lesson builds on `concept:electric_field` and `concept:electrostatics`. "
            "Master the three standard symmetries before moving to `concept:electric_potential` "
            "and capacitor problems."
        ),
        "body_he_md": (
            "חוק קולון יכול לחשב את השדה החשמלי של כל פילוג מטען — "
            "אבל רק אם מאחדים על כל אלמנט מטען. לענן של מיליארדי אלקטרונים, "
            "האינטגרל לא פרקטי. **חוק גאוס** מספק קיצור דרך דרמטי: לפילוגי מטען "
            "עם **סימטריה גבוהה**, ניתן למצוא $\\vec{E}$ בשלושה שורות אלגברה "
            "במקום אינטגרל משולש.\n\n"
            "החוק קושר את **השטף החשמלי הכולל** דרך כל משטח סגור למטען "
            "הכלוא בפנים: $\\Phi = Q_{\\text{enc}}/\\epsilon_0$. כשהשדה אחיד "
            "על משטח גאוס שנבחר בחוכמה, מוציאים $E$ מהאינטגרל ופותרים ישירות.\n\n"
            "**בפיזיקה אוניברסיטאית ישראלית** (אלקטרומגנטיות 1), חוק גאוס הוא "
            "הכלי הסטנדרטי למציאת $\\vec{E}$:\n"
            "- מחוץ ומתוך כדור או קליפה טעונה\n"
            "- ליד גיליון או לוח מטען אינסופי\n"
            "- ליד קו או קליפה גלילית אינסופית\n\n"
            "שיעור זה מבוסס על `concept:electric_field` ו-`concept:electrostatics`. "
            "שלטו בשלוש הסימטריות הסטנדרטיות לפני `concept:electric_potential` "
            "ובעיות קבל."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Gauss's law (integral form):**\n"
            "$$\\oint_S \\vec{E} \\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\n\n"
            "**Terms:**\n"
            "- $\\oint_S \\vec{E} \\cdot d\\vec{A}$ — **electric flux** through closed surface $S$ "
            "(the Gaussian surface)\n"
            "- $d\\vec{A}$ — outward area element; direction is the **outward normal**\n"
            "- $Q_{\\text{enc}}$ — total charge **enclosed** by $S$ (not on the surface)\n"
            "- $\\epsilon_0 = 8.85 \\times 10^{-12}\\;\\text{C}^2/(\\text{N·m}^2)$ — permittivity of free space\n"
            "- SI unit of flux: N·m²/C = V·m\n\n"
            "**Electric flux of a uniform field:** If $\\vec{E}$ is constant and makes angle "
            "$\\theta$ with $d\\vec{A}$, then $\\Phi = E A \\cos\\theta$. For a closed surface "
            "with no enclosed charge, net flux is zero — flux in equals flux out.\n\n"
            "**Equivalence to Coulomb's law:** Gauss's law is not independent — it follows "
            "from Coulomb's inverse-square field and the superposition principle. But it is "
            "far more practical when symmetry lets you argue that $|E|$ is constant on "
            "parts of the Gaussian surface.\n\n"
            "**Key distinction:** Gauss's law is **always true**, but you can only **solve** "
            "for $E$ when the geometry gives you enough symmetry to pull $E$ outside the integral."
        ),
        "body_he_md": (
            "**חוק גאוס (צורה אינטגרלית):**\n"
            "$$\\oint_S \\vec{E} \\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\n\n"
            "**מונחים:**\n"
            "- $\\oint_S \\vec{E} \\cdot d\\vec{A}$ — **שטף חשמלי** דרך משטח סגור $S$ "
            "(משטח גאוס)\n"
            "- $d\\vec{A}$ — אלמנט שטח חיצוני; כיוון **נורמל חיצוני**\n"
            "- $Q_{\\text{enc}}$ — מטען **כלוא** בתוך $S$ (לא על המשטח)\n"
            "- $\\epsilon_0 = 8.85 \\times 10^{-12}\\;\\text{C}^2/(\\text{N·m}^2)$ — "
            "קבוע החשמל\n"
            "- יחידת שטף: N·m²/C = V·m\n\n"
            "**שטף בשדה אחיד:** אם $\\vec{E}$ קבוע וזווית $\\theta$ עם $d\\vec{A}$, "
            "אז $\\Phi = E A \\cos\\theta$. למשטח סגור ללא מטען כלוא, "
            "שטף נטו אפס — שטף נכנס = שטף יוצא.\n\n"
            "**שקילות לחוק קולון:** חוק גאוס נובע משדה ריבוע-הפוך של קולון "
            "ועיקרון הסופרפוזיציה. אבל הוא הרבה יותר פרקטי כשסימטריה "
            "מאפשרת לטעון ש-$|E|$ קבוע על חלקים ממשטח גאוס.\n\n"
            "**הבחנה חשובה:** חוק גאוס **תמיד נכון**, אך ניתן **לפתור** ל-$E$ "
            "רק כשהגיאומטריה נותנת מספיק סימטריה להוציא $E$ מחוץ לאינטגרל."
        ),
    },
    "theory": {
        "body_en_md": (
            "### 1. Spherical symmetry\n\n"
            "For any spherically symmetric charge distribution (total charge $Q$, radius $R$):\n\n"
            "**Outside** ($r > R$): Gaussian sphere of radius $r$ encloses all $Q$. "
            "By symmetry, $\\vec{E}$ is radial and $|E|$ constant on the surface:\n"
            "$$E(4\\pi r^2) = Q/\\epsilon_0 \\implies \\boxed{E = \\frac{Q}{4\\pi\\epsilon_0 r^2} = \\frac{kQ}{r^2}}$$\n\n"
            "**Inside uniform solid sphere** ($r < R$): Enclosed charge "
            "$Q_{\\text{enc}} = Q(r/R)^3$ (volume scales as $r^3$):\n"
            "$$E = \\frac{kQr}{R^3} \\quad (r < R)$$\n"
            "Field grows **linearly** inside, falls as $1/r^2$ outside. "
            "**Inside hollow shell:** $Q_{\\text{enc}} = 0 \\Rightarrow E = 0$.\n\n"
            "### 2. Infinite line charge (linear density $\\lambda$)\n\n"
            "Cylindrical Gaussian surface (radius $r$, length $L$). Flux only through curved wall; "
            "flat ends contribute zero because $\\vec{E} \\perp$ them:\n"
            "$$E(2\\pi r L) = \\lambda L/\\epsilon_0 \\implies \\boxed{E = \\frac{\\lambda}{2\\pi\\epsilon_0 r} = \\frac{2k\\lambda}{r}}$$\n\n"
            "### 3. Infinite plane (surface charge density $\\sigma$)\n\n"
            "Pill-box Gaussian surface (area $A$ on each face). Two faces contribute $2EA$:\n"
            "$$E \\cdot 2A = \\sigma A/\\epsilon_0 \\implies \\boxed{E = \\frac{\\sigma}{2\\epsilon_0}}$$\n"
            "Field is **uniform**, perpendicular to the plane, independent of distance. "
            "Between two parallel plates with $\\pm\\sigma$: fields add to $E = \\sigma/\\epsilon_0$.\n\n"
            "**Conductors in equilibrium:** Excess charge sits on the surface; "
            "$E = 0$ in the bulk. Just outside a conductor, $E = \\sigma/\\epsilon_0$ "
            "where $\\sigma$ is the local surface charge density."
        ),
        "body_he_md": (
            "### 1. סימטריה כדורית\n\n"
            "לכל פילוג מטען סימטרי כדורית (מטען כולל $Q$, רדיוס $R$):\n\n"
            "**מחוץ** ($r > R$): כדור גאוס ברדיוס $r$ כולל את כל $Q$. "
            "מסימטריה, $\\vec{E}$ רדיאלי ו-$|E|$ קבוע על המשטח:\n"
            "$$E(4\\pi r^2) = Q/\\epsilon_0 \\implies \\boxed{E = \\frac{kQ}{r^2}}$$\n\n"
            "**בתוך כדור מוצק אחיד** ($r < R$): מטען כלוא "
            "$Q_{\\text{enc}} = Q(r/R)^3$ (נפח פרופורציונלי ל-$r^3$):\n"
            "$$E = \\frac{kQr}{R^3} \\quad (r < R)$$\n"
            "השדה גדל **ליניארית** בפנים, יורד כ-$1/r^2$ בחוץ. "
            "**בתוך קליפה חלולה:** $Q_{\\text{enc}} = 0 \\Rightarrow E = 0$.\n\n"
            "### 2. קו מטען אינסופי (צפיפות $\\lambda$)\n\n"
            "משטח גאוס גלילי (רדיוס $r$, אורך $L$). שטף רק דרך הקיר המעוקל; "
            "הבסיסים תורמים אפס כי $\\vec{E} \\perp$ להם:\n"
            "$$E(2\\pi r L) = \\lambda L/\\epsilon_0 \\implies \\boxed{E = \\frac{\\lambda}{2\\pi\\epsilon_0 r}}$$\n\n"
            "### 3. מישור אינסופי (צפיפות $\\sigma$)\n\n"
            "קופסת גלולה (שטח $A$ על כל פנים). שני פנים תורמים $2EA$:\n"
            "$$E \\cdot 2A = \\sigma A/\\epsilon_0 \\implies \\boxed{E = \\frac{\\sigma}{2\\epsilon_0}}$$\n"
            "השדה **אחיד**, מאונך למישור, בלתי תלוי במרחק. "
            "בין שני לוחות מקבילים עם $\\pm\\sigma$: השדות מתחברים ל-$E = \\sigma/\\epsilon_0$.\n\n"
            "**מוליכים בשיווי משקל:** מטען עודף על הפ surface; "
            "$E = 0$ בנפח. ממש מחוץ למוליך, $E = \\sigma/\\epsilon_0$ "
            "כאשר $\\sigma$ היא צפיפות המטען המקומית."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A conducting sphere of radius $R = 5\\;\\text{cm}$ carries charge "
            "$Q = 4\\;\\text{nC}$. Find $E$ at (a) $r = 10\\;\\text{cm}$ (outside) and "
            "(b) $r = 3\\;\\text{cm}$ (inside).\n\n"
            "### Move 1: Identify geometry and symmetry\n"
            "A conductor in electrostatic equilibrium has all excess charge on the surface. "
            "Outside, the field is the same as a point charge $Q$ at the center.\n\n"
            "### Move 2: Part (a) — Outside ($r > R$)\n"
            "Use $E = kQ/r^2$ with $r = 0.10$ m:\n"
            "$$E = \\frac{(9\\times10^9)(4\\times10^{-9})}{(0.10)^2} = \\frac{36}{0.01} = 3600\\;\\text{N/C}$$\n"
            "Direction: outward (positive charge).\n\n"
            "### Move 3: Part (b) — Inside a conductor ($r < R$)\n"
            "Choose Gaussian sphere inside the metal. $Q_{\\text{enc}} = 0$ because charge "
            "cannot reside in the bulk of a conductor.\n"
            "$$E = 0 \\quad \\text{(inside the conductor)}$$\n\n"
            "### Move 4: Sanity check\n"
            "At $r = 10$ cm, field falls as $1/r^2$ — doubling distance quarters $E$. "
            "Inside, zero field is required for equilibrium (no current flow).\n\n"
            "**Answer:** (a) $3600\\;\\text{N/C}$ outward; (b) $E = 0$.\n\n"
            "**Exam tip:** Do not use $E = kQr/R^3$ inside a conductor — that formula "
            "applies only to uniformly charged **insulators**."
        ),
        "body_he_md": (
            "**נתון:** כדור מוליך $R = 5\\;\\text{cm}$ נושא $Q = 4\\;\\text{nC}$. "
            "מצא $E$ ב-(א) $r = 10\\;\\text{cm}$ (חוץ) ו-(ב) $r = 3\\;\\text{cm}$ (פנים).\n\n"
            "### צעד 1: זיהוי גיאומטריה וסימטריה\n"
            "מוליך בשיווי משקל אלקטרוסטטי — כל המטען העודף על הפ surface. "
            "בחוץ, השדה כמו מטען נקודתי $Q$ במרכז.\n\n"
            "### צעד 2: חלק (א) — מחוץ ($r > R$)\n"
            "השתמשו ב-$E = kQ/r^2$ עם $r = 0.10$ m:\n"
            "$$E = \\frac{(9\\times10^9)(4\\times10^{-9})}{(0.10)^2} = 3600\\;\\text{N/C}$$\n"
            "כיוון: החוצה (מטען חיובי).\n\n"
            "### צעד 3: חלק (ב) — בתוך מוליך ($r < R$)\n"
            "בחרו כדור גאוס בתוך המתכת. $Q_{\\text{enc}} = 0$ כי מטען "
            "לא יכול להימצא בנפח המוליך.\n"
            "$$E = 0 \\quad \\text{(בתוך המוליך)}$$\n\n"
            "### צעד 4: בדיקת הגיון\n"
            "ב-$r = 10$ cm, השדה יורד כ-$1/r^2$. בפנים, שדה אפס נדרש לשיווי משקל.\n\n"
            "**תשובה:** (א) $3600\\;\\text{N/C}$ החוצה; (ב) $E = 0$.\n\n"
            "**טיפ לבחינה:** אל תשתמשו ב-$E = kQr/R^3$ בתוך מוליך — "
            "נוסחה זו רק למבודדים טעונים **באחידות**."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** An infinitely long cylindrical shell of radius $R = 3\\;\\text{cm}$ "
            "carries surface charge density $\\sigma = 2\\;\\mu\\text{C/m}^2$. "
            "Find $E$ at (a) $r = 5\\;\\text{cm}$ and (b) $r = 1\\;\\text{cm}$.\n\n"
            "### Move 1: Convert surface charge to line charge\n"
            "For a shell of radius $R$, the charge per unit length is:\n"
            "$$\\lambda = \\sigma(2\\pi R) = (2\\times10^{-6})(2\\pi)(0.03) = 1.2\\pi\\times10^{-7}\\;\\text{C/m}$$\n\n"
            "### Move 2: Part (a) — Outside ($r > R$)\n"
            "Coaxial Gaussian cylinder encloses all line charge:\n"
            "$$E = \\frac{\\lambda}{2\\pi\\epsilon_0 r} = \\frac{2k\\lambda}{r} "
            "= \\frac{2(9\\times10^9)(1.2\\pi\\times10^{-7})}{0.05} \\approx 1.36\\times10^5\\;\\text{N/C}$$\n\n"
            "### Move 3: Part (b) — Inside shell ($r < R$)\n"
            "Gaussian cylinder at $r = 1$ cm encloses no charge:\n"
            "$$Q_{\\text{enc}} = 0 \\implies E = 0$$\n\n"
            "### Move 4: Verify symmetry argument\n"
            "On the curved wall, $\\vec{E}$ is radial and $|E|$ constant. "
            "Flat end caps contribute zero flux because $\\vec{E} \\parallel$ the caps.\n\n"
            "**Answer:** (a) $\\approx 1.36\\times10^5\\;\\text{N/C}$ radially outward; "
            "(b) $E = 0$.\n\n"
            "**Exam tip:** Always convert $\\sigma$ on a cylinder to $\\lambda$ before "
            "applying the line-charge formula. Re-check by noting $E \\propto 1/r$ outside: "
            "doubling $r$ should halve the field magnitude."
        ),
        "body_he_md": (
            "**נתון:** קליפה גלילית אינסופית $R = 3\\;\\text{cm}$, "
            "$\\sigma = 2\\;\\mu\\text{C/m}^2$. מצא $E$ ב-(א) $r = 5\\;\\text{cm}$ "
            "ו-(ב) $r = 1\\;\\text{cm}$.\n\n"
            "### צעד 1: המרת מטען שטחי לקווי\n"
            "לקליפה ברדיוס $R$, מטען ליחידת אורך:\n"
            "$$\\lambda = \\sigma(2\\pi R) = (2\\times10^{-6})(2\\pi)(0.03) = 1.2\\pi\\times10^{-7}\\;\\text{C/m}$$\n\n"
            "### צעד 2: חלק (א) — מחוץ ($r > R$)\n"
            "גליל גאוס קואקסיאלי כולל את כל המטען הקווי:\n"
            "$$E = \\frac{\\lambda}{2\\pi\\epsilon_0 r} \\approx 1.36\\times10^5\\;\\text{N/C}$$\n\n"
            "### צעד 3: חלק (ב) — בתוך הקליפה ($r < R$)\n"
            "גליל גאוס ב-$r = 1$ cm לא כולל מטען:\n"
            "$$Q_{\\text{enc}} = 0 \\implies E = 0$$\n\n"
            "### צעד 4: אימות טיעון סימטריה\n"
            "על הקיר המעוקל, $\\vec{E}$ רדיאלי ו-$|E|$ קבוע. "
            "מכסים שטוחים תורמים שטף אפס כי $\\vec{E} \\parallel$ להם.\n\n"
            "**תשובה:** (א) $\\approx 1.36\\times10^5\\;\\text{N/C}$ רדיאלית החוצה; "
            "(ב) $E = 0$.\n\n"
            "**טיפ לבחינה:** המירו תמיד $\\sigma$ על גליל ל-$\\lambda$ "
            "לפני נוסחת קו המטען. אימות: מחוץ $E \\propto 1/r$ — "
            "כפלת $r$ מחלקת את גודל השדה ב-2."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** Two infinite parallel plates: Plate A with $+\\sigma$, Plate B with $-\\sigma$. "
            "Find $\\vec{E}$ in regions (I) left of A, (II) between A and B, and (III) right of B.\n\n"
            "### Move 1: Field from each plate alone\n"
            "Each infinite plate produces $E = \\sigma/(2\\epsilon_0)$, pointing away from $+\\sigma$ "
            "and toward $-\\sigma$ on both sides.\n\n"
            "### Move 2: Superpose fields in each region\n\n"
            "| Region | From A ($+\\sigma$) | From B ($-\\sigma$) | Net |\n"
            "|---|---|---|---|\n"
            "| I (left of A) | $\\leftarrow$ | $\\rightarrow$ | Cancel: $E = 0$ |\n"
            "| II (between) | $\\rightarrow$ | $\\rightarrow$ | Add: $E = \\sigma/\\epsilon_0$ |\n"
            "| III (right of B) | $\\rightarrow$ | $\\leftarrow$ | Cancel: $E = 0$ |\n\n"
            "### Move 3: Physical interpretation\n"
            "The field is $\\sigma/\\epsilon_0$ only **between** the plates, pointing from $+$ to $-$. "
            "This is the ideal parallel-plate capacitor — uniform field in the gap, zero outside.\n\n"
            "### Move 4: Check with pill-box Gauss surface\n"
            "Between plates, pill-box spanning the gap gives $E \\cdot A = \\sigma A/\\epsilon_0$ "
            "because enclosed charge is $\\sigma A$ from one plate only (the other contributes "
            "opposite flux on the other face).\n\n"
            "**Answer:** $E = \\sigma/\\epsilon_0$ between plates only; $E = 0$ outside.\n\n"
            "**Exam tip:** Remember factor 2 for a **single** plate vs factor 1 (doubled field) "
            "between two opposite plates."
        ),
        "body_he_md": (
            "**נתון:** שני לוחות מקבילים אינסופיים: לוח A עם $+\\sigma$, לוח B עם $-\\sigma$. "
            "מצא $\\vec{E}$ באזורים (I) משמאל ל-A, (II) בין A ל-B, (III) מימין ל-B.\n\n"
            "### צעד 1: שדה מכל לוח בנפרד\n"
            "כל לוח אינסופי יוצר $E = \\sigma/(2\\epsilon_0)$, "
            "החוצה מ-$+\\sigma$ ולכיוון $-\\sigma$ משני הצדדים.\n\n"
            "### צעד 2: סופרפוזיציה בכל אזור\n\n"
            "| אזור | מ-A ($+\\sigma$) | מ-B ($-\\sigma$) | נטו |\n"
            "|---|---|---|---|\n"
            "| I (שמאל ל-A) | $\\leftarrow$ | $\\rightarrow$ | מתקזז: $E = 0$ |\n"
            "| II (בין) | $\\rightarrow$ | $\\rightarrow$ | מתחבר: $E = \\sigma/\\epsilon_0$ |\n"
            "| III (ימין ל-B) | $\\rightarrow$ | $\\leftarrow$ | מתקזז: $E = 0$ |\n\n"
            "### צעד 3: פרשנות פיזיקלית\n"
            "השדה $\\sigma/\\epsilon_0$ רק **בין** הלוחות, מ-$+$ ל-$-$. "
            "זה הקבל לוחות מקבילים האידיאלי — שדה אחיד בפער, אפס בחוץ.\n\n"
            "### צעד 4: בדיקה עם קופסת גלולה\n"
            "בין הלוחות, קופסת גלולה נותנת $E \\cdot A = \\sigma A/\\epsilon_0$ "
            "כי המטען הכלוא הוא $\\sigma A$ מלוח אחד.\n\n"
            "**תשובה:** $E = \\sigma/\\epsilon_0$ רק בין הלוחות; $E = 0$ בחוץ.\n\n"
            "**טיפ לבחינה:** גורם 2 ללוח **בודד** לעומת שדה כפול "
            "בין שני לוחות מנוגדים."
        ),
    },
    "checkpoint_1": {
        "body_en_md": (
            "**Practice now:** An infinite plane carries surface charge density "
            "$\\sigma = 3\\;\\mu\\text{C/m}^2$. Find $E$ near the plane.\n\n"
            "This is a direct application of the infinite-plane result $E = \\sigma/(2\\epsilon_0)$. "
            "The field is uniform on both sides, perpendicular to the plane. "
            "Convert $\\sigma = 3\\times10^{-6}$ C/m² before substituting.\n\n"
            "Use $\\epsilon_0 = 8.85\\times10^{-12}$ C²/(N·m²). "
            "Expected answer is on the order of $10^5$ N/C. "
            "Try the calculation yourself before opening the solution.\n\n"
            "**Exam tip:** Write the formula before numbers. The factor $1/2$ comes from "
            "flux through only one face of the pill-box — do not use $\\sigma/\\epsilon_0$ "
            "for a single plane. Direction is perpendicular to the plane on both sides."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** מישור אינסופי נושא $\\sigma = 3\\;\\mu\\text{C/m}^2$. "
            "מצא $E$ ליד המישור.\n\n"
            "זה יישום ישיר של $E = \\sigma/(2\\epsilon_0)$. "
            "השדה אחיד משני הצדדים, מאונך למישור. "
            "המירו $\\sigma = 3\\times10^{-6}$ C/m² לפני הצבה.\n\n"
            "השתמשו ב-$\\epsilon_0 = 8.85\\times10^{-12}$. "
            "התשובה הצפויה בסדר גודל $10^5$ N/C. "
            "נסו לחשב לבד לפני הפתרון. בדקו יחידות: N/C.\n\n"
            "**טיפ לבחינה:** כתבו נוסחה לפני מספרים. גורם $1/2$ מגיע "
            "משטף דרך פנים אחד בלבד — אל תשתמשו ב-$\\sigma/\\epsilon_0$ ללוח בודד. "
            "הכיוון מאונך למישור משני הצדדים. זה לוח בודד, לא קבל."
        ),
        "checkpoint_solution_en": (
            "An infinite plane with $\\sigma = 3\\;\\mu\\text{C/m}^2$. Find $E$.\n\n"
            "**Step 1:** Convert: $\\sigma = 3\\times10^{-6}$ C/m².\n"
            "**Step 2:** Formula: $E = \\sigma/(2\\epsilon_0)$.\n\n"
            "$$E = \\frac{3\\times10^{-6}}{2\\times8.85\\times10^{-12}} "
            "= \\frac{3\\times10^{-6}}{1.77\\times10^{-11}} \\approx 1.69\\times10^5\\;\\text{N/C}$$\n\n"
            "**Step 3:** Direction: perpendicular to plane, away from positive $\\sigma$ "
            "(assuming $\\sigma > 0$).\n\n"
            "**Verify:** Magnitude ~170 kN/C is reasonable for $\\mu$C/m² surface density.\n\n"
            "**Answer:** $E \\approx 1.69\\times10^5\\;\\text{N/C}$."
        ),
        "checkpoint_solution_he": (
            "מישור אינסופי עם $\\sigma = 3\\;\\mu\\text{C/m}^2$. מצא $E$.\n\n"
            "**שלב 1:** המרה: $\\sigma = 3\\times10^{-6}$ C/m².\n"
            "**שלב 2:** נוסחה: $E = \\sigma/(2\\epsilon_0)$.\n\n"
            "$$E = \\frac{3\\times10^{-6}}{2\\times8.85\\times10^{-12}} "
            "\\approx 1.69\\times10^5\\;\\text{N/C}$$\n\n"
            "**שלב 3:** כיוון: מאונך למישור, החוצה מ-$\\sigma$ חיובי.\n\n"
            "**אימות:** גודל ~170 kN/C סביר לצפיפות $\\mu$C/m².\n\n"
            "**תשובה:** $E \\approx 1.69\\times10^5\\;\\text{N/C}$."
        ),
    },
    "checkpoint_2": {
        "body_en_md": (
            "**Practice now:** A uniformly charged sphere of radius $R = 4\\;\\text{cm}$ "
            "and total charge $Q = 8\\;\\text{nC}$. Find $E$ at $r = 2\\;\\text{cm}$ (inside) "
            "and $r = 8\\;\\text{cm}$ (outside).\n\n"
            "This is a **uniform insulator**, not a conductor — use different formulas inside and out. "
            "Inside: $E = kQr/R^3$. Outside: $E = kQ/r^2$.\n\n"
            "Convert $R = 0.04$ m, $Q = 8\\times10^{-9}$ C. "
            "At the surface ($r = R$), both formulas must give the same $E$ — use this as a check.\n\n"
            "Try both parts before reading the solution. On exams, label \"inside\" vs "
            "\"outside\" before picking a formula — mixing them is the top lost-point error."
        ),
        "body_he_md": (
            "**תרגלו עכשיו:** כדור טעון אחיד $R = 4\\;\\text{cm}$, $Q = 8\\;\\text{nC}$. "
            "מצא $E$ ב-$r = 2\\;\\text{cm}$ (פנים) ו-$r = 8\\;\\text{cm}$ (חוץ).\n\n"
            "זה **מבודד אחיד**, לא מוליך — נוסחאות שונות בפנים ובחוץ. "
            "בפנים: $E = kQr/R^3$. בחוץ: $E = kQ/r^2$.\n\n"
            "המירו $R = 0.04$ m, $Q = 8\\times10^{-9}$ C. "
            "על הפ surface ($r = R$), שתי הנוסחאות חייבות לתת אותו $E$ — השתמשו בזה לבדיקה.\n\n"
            "נסו את שני החלקים לפני הפתרון. בבחינה, סמנו \"פנים\" מול \"חוץ\" "
            "לפני בחירת נוסחה — ערבובן הוא טעות אובדן-נקודות נפוצה. "
            "אמתו יחידות N/C בסוף."
        ),
        "checkpoint_solution_en": (
            "Uniform sphere $R = 4\\;\\text{cm}$, $Q = 8\\;\\text{nC}$. Find $E$ at "
            "$r = 2\\;\\text{cm}$ and $r = 8\\;\\text{cm}$.\n\n"
            "**Inside** ($r = 0.02$ m):\n"
            "$$E_{\\text{in}} = \\frac{kQr}{R^3} = "
            "\\frac{(9\\times10^9)(8\\times10^{-9})(0.02)}{(0.04)^3} "
            "= \\frac{72 \\times 0.02}{6.4\\times10^{-5}} = 22500\\;\\text{N/C}$$\n\n"
            "**Outside** ($r = 0.08$ m):\n"
            "$$E_{\\text{out}} = \\frac{kQ}{r^2} = "
            "\\frac{72}{(0.08)^2} = \\frac{72}{0.0064} = 11250\\;\\text{N/C}$$\n\n"
            "**Verify:** At $r = R$, both give $E = kQ/R^2 = 45000$ N/C. "
            "Inside field grows linearly; outside falls as $1/r^2$.\n\n"
            "**Answer:** Inside: $22500$ N/C; Outside: $11250$ N/C."
        ),
        "checkpoint_solution_he": (
            "כדור אחיד $R = 4\\;\\text{cm}$, $Q = 8\\;\\text{nC}$. מצא $E$ ב-$r = 2$ cm ו-$r = 8$ cm.\n\n"
            "**פנים** ($r = 0.02$ m):\n"
            "$$E_{\\text{in}} = \\frac{kQr}{R^3} = 22500\\;\\text{N/C}$$\n\n"
            "**חוץ** ($r = 0.08$ m):\n"
            "$$E_{\\text{out}} = \\frac{kQ}{r^2} = 11250\\;\\text{N/C}$$\n\n"
            "**אימות:** ב-$r = R$, שתיהן נותנות $E = kQ/R^2 = 45000$ N/C. "
            "בפנים השדה גדל ליניארית; בחוץ יורד כ-$1/r^2$.\n\n"
            "**תשובה:** פנים: $22500$ N/C; חוץ: $11250$ N/C."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Symmetry | Gaussian surface | Why it works |\n"
            "|---|---|---|\n"
            "| Spherical | Concentric sphere | $|\\vec{E}|$ const; $\\vec{E} \\perp$ surface |\n"
            "| Cylindrical | Coaxial cylinder | $|\\vec{E}|$ const on curved wall; zero flux on flat ends |\n"
            "| Planar | Pill-box (two flat faces) | $\\vec{E} \\perp$ faces; sides parallel to $\\vec{E}$ |\n\n"
            "**Decision tree:**\n"
            "1. Identify symmetry (sphere / cylinder / plane)\n"
            "2. Draw Gaussian surface **matching** the symmetry\n"
            "3. Argue $|E|$ is constant on the relevant part of the surface\n"
            "4. Compute flux: $E \\cdot A_{\\text{eff}} = Q_{\\text{enc}}/\\epsilon_0$\n"
            "5. Solve for $E$; check units (N/C)\n\n"
            "**When Gauss fails as a solver:** Non-uniform or asymmetric distributions — "
            "fall back to integration or superposition. Gauss's law is still true; "
            "you just cannot pull $E$ out.\n\n"
            "**Exam tip:** State your symmetry argument explicitly — examiners award "
            "partial credit for correct Gaussian surface choice even if arithmetic slips."
        ),
        "body_he_md": (
            "| סימטריה | משטח גאוס | למה זה עובד |\n"
            "|---|---|---|\n"
            "| כדורית | כדור קונצנטרי | $|\\vec{E}|$ קבוע; $\\vec{E} \\perp$ משטח |\n"
            "| גלילית | גליל קואקסיאלי | $|\\vec{E}|$ קבוע על קיר מעוקל; שטף אפס על בסיסים |\n"
            "| מישורית | קופסת גלולה | $\\vec{E} \\perp$ לפנים; צדדים $\\parallel$ ל-$\\vec{E}$ |\n\n"
            "**עץ החלטות:**\n"
            "1. זהה סימטריה (כדור / גליל / מישור)\n"
            "2. צייר משטח גאוס **תואם** סימטריה\n"
            "3. טען ש-$|E|$ קבוע על החלק הרלוונטי\n"
            "4. חשב שטף: $E \\cdot A_{\\text{eff}} = Q_{\\text{enc}}/\\epsilon_0$\n"
            "5. פתור ל-$E$; בדוק יחידות (N/C)\n\n"
            "**כשגאוס לא פותר:** פילוגים לא-אחידים או לא-סימטריים — "
            "חזרו לאינטגרציה או סופרפוזיציה. חוק גאוס עדיין נכון; "
            "פשוט לא ניתן להוציא $E$.\n\n"
            "**טיפ לבחינה:** ציינו במפורש את טיעון הסימטריה — "
            "נקודות חלקיות לבחירת משטח גאוס נכון."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below in order. **Try each one before opening the solution** — "
            "the symmetry argument and Gaussian surface choice matter as much as the final number.\n\n"
            "The set progresses from flux calculations and single-symmetry fields (easy) "
            "through conductor vs insulator distinctions and multi-shell problems (medium) "
            "to non-uniform charge density, coaxial capacitors, and potential integration (hard).\n\n"
            "For each problem: identify symmetry, choose the Gaussian surface, compute $Q_{\\text{enc}}$, "
            "then check units and limiting cases.\n\n"
            "**University exam strategy:** Write Gauss's law before substituting. "
            "State whether charge is enclosed or not before applying a formula."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה לפי הסדר. **נסו כל תרגיל לפני הפתרון** — "
            "טיעון הסימטריה ובחירת משטח גאוס חשובים לא פחות מהמספר הסופי.\n\n"
            "הסדרה מתקדמת מחישובי שטף ושדות סימטריה בודדת (קל) "
            "דרך הבחנה מוליך/מבודד ובעיות ריבוי קליפות (בינוני) "
            "לצפיפות לא-אחידה, קבל קואקסיאלי ואינטגרציית פוטנציאל (קשה).\n\n"
            "בכל בעיה: זהו סימטריה, בחרו משטח גאוס, חשבו $Q_{\\text{enc}}$, "
            "ואז בדקו יחידות ומקרי גבול.\n\n"
            "**אסטרטגיה לבחינה:** כתבו חוק גאוס לפני הצבה. "
            "ציינו אם מטען כלוא לפני יישום נוסחה."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Confusing $Q_{\\text{enc}}$ with total charge.** Only charge **inside** the "
            "Gaussian surface appears on the right side. Charge outside contributes to $\\vec{E}$ "
            "at points on the surface but not to $Q_{\\text{enc}}$.\n\n"
            "2. **Using Gauss to solve when symmetry doesn't hold.** Gauss's law is always true, "
            "but you can only solve for $E$ with spherical, cylindrical, or planar symmetry.\n\n"
            "3. **Wrong direction for $d\\vec{A}$.** By convention, $d\\vec{A}$ points **outward**. "
            "If $Q_{\\text{enc}} < 0$, net flux is negative (field points inward).\n\n"
            "4. **Conductor vs insulator inside.** Inside a conductor: $E = 0$ always. "
            "Inside a uniformly charged **insulator**: $E \\neq 0$ and grows linearly with $r$.\n\n"
            "5. **Forgetting the factor of 2 for infinite planes.** $E = \\sigma/(2\\epsilon_0)$ for "
            "**one** plane. Between two parallel plates with $+\\sigma$ and $-\\sigma$: "
            "$E = \\sigma/\\epsilon_0$.\n\n"
            "6. **Using $E = kQ/r^2$ inside a solid uniform sphere incorrectly.** "
            "That formula is for $r > R$ only; inside use $E = kQr/R^3$."
        ),
        "body_he_md": (
            "1. **בלבול $Q_{\\text{enc}}$ עם מטען כולל.** רק מטען **בתוך** משטח גאוס "
            "מופיע בצד ימין. מטען בחוץ תורם ל-$\\vec{E}$ על המשטח אך לא ל-$Q_{\\text{enc}}$.\n\n"
            "2. **שימוש בגאוס לפתרון כשאין סימטריה.** חוק גאוס תמיד נכון, "
            "אך ניתן לפתור ל-$E$ רק בסימטריה כדורית, גלילית או מישורית.\n\n"
            "3. **כיוון שגוי של $d\\vec{A}$.** $d\\vec{A}$ מצביע **החוצה**. "
            "אם $Q_{\\text{enc}} < 0$, שטף נטו שלילי (שדה פנימה).\n\n"
            "4. **מוליך לעומת מבודד בפנים.** בתוך מוליך: $E = 0$ תמיד. "
            "בתוך **מבודד** טעון אחיד: $E \\neq 0$ וגדל ליניארית עם $r$.\n\n"
            "5. **שכחת גורם 2 למישורים.** $E = \\sigma/(2\\epsilon_0)$ ל**לוח אחד**. "
            "בין שני לוחות $\\pm\\sigma$: $E = \\sigma/\\epsilon_0$.\n\n"
            "6. **שימוש ב-$E = kQ/r^2$ בפנים כדור אחיד.** "
            "נוסחה זו ל-$r > R$ בלבד; בפנים: $E = kQr/R^3$."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Gauss's law is the bridge from Coulomb's pairwise forces to **macroscopic** "
            "electromagnetism. Every capacitor, coaxial cable, and charged particle accelerator "
            "relies on knowing $\\vec{E}$ from symmetric charge distributions — and Gauss gives "
            "those fields in seconds.\n\n"
            "**Cross-subject links:** The same flux-through-closed-surface pattern reappears in "
            "magnetism (Ampère's law), fluid flow (continuity equation), and later in Maxwell's "
            "equations as $\\nabla \\cdot \\vec{E} = \\rho/\\epsilon_0$.\n\n"
            "**Why it matters for exams:** Israeli university electromagnetism courses routinely "
            "test Gauss on conducting shells, infinite slabs, and coaxial geometries. "
            "Bagrut 5-unit physics uses the sphere and plane results directly."
        ),
        "body_he_md": (
            "חוק גאוס הוא הגשר מכוחות קולון זוגיים ל**אלקטרומגנטיות מcroscopic**. "
            "כל קבל, כבל קואקסיאלי ומאיץ חלקיקים תלוי בידיעת $\\vec{E}$ "
            "מפילוגי מטען סימטריים — וגאוס נותן אותם בשניות.\n\n"
            "**קשרים בין-מקצועיים:** אותו דפוס שטף-דרך-משטח-סגור חוזר "
            "במגנטיות (חוק אмпère), בזרימת ש fluids ובמשוואות מаксוול "
            "כ-$\\nabla \\cdot \\vec{E} = \\rho/\\epsilon_0$.\n\n"
            "**למה זה חשוב לבחינות:** קורסי אלקטרומגנטיות באוניברסיטה "
            "בודקים גאוס על קליפות מוליכות, לוחות אינסופיים וגיאומטריה קואקסיאלית. "
            "בגרות 5 יחידות משתמשת ישירות בתוצאות הכדור והמישור. "
            "שליטה בגאוס חוסכת זמן יקר בכל שאלת אלקטרוסטטיקה."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Core formula:** $\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$\n\n"
            "| Geometry | $E$ | Notes |\n"
            "|---|---|---|\n"
            "| Point / outside sphere | $kQ/r^2$ | All charge acts at center |\n"
            "| Inside uniform solid sphere | $kQr/R^3$ | Linear in $r$ |\n"
            "| Inside hollow shell | $0$ | No enclosed charge |\n"
            "| Infinite line charge | $\\lambda/(2\\pi\\epsilon_0 r)$ | Cylindrical Gauss |\n"
            "| Infinite plane | $\\sigma/(2\\epsilon_0)$ | Factor 2! |\n"
            "| Between capacitor plates | $\\sigma/\\epsilon_0$ | Fields add |\n"
            "| Inside conductor | $0$ | Charge on surface |\n\n"
            "**Constants:** $k = 9\\times10^9$ N·m²/C²; $\\epsilon_0 = 8.85\\times10^{-12}$ F/m.\n\n"
            "**Last review:** Say each formula aloud, then solve one checkpoint without notes."
        ),
        "body_he_md": (
            "**נוסחה מרכזית:** $\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$\n\n"
            "| גיאומטריה | $E$ | הערות |\n"
            "|---|---|---|\n"
            "| מטען נקודתי / מחוץ לכדור | $kQ/r^2$ | כל המטען במרכז |\n"
            "| בתוך כדור מוצק אחיד | $kQr/R^3$ | ליניארי ב-$r$ |\n"
            "| בתוך קליפה חלולה | $0$ | אין מטען כלוא |\n"
            "| קו מטען אינסופי | $\\lambda/(2\\pi\\epsilon_0 r)$ | גאוס גלילי |\n"
            "| מישור אינסופי | $\\sigma/(2\\epsilon_0)$ | גורם 2! |\n"
            "| בין לוחות קבל | $\\sigma/\\epsilon_0$ | שדות מתחברים |\n"
            "| בתוך מוליך | $0$ | מטען על פני השטח |\n\n"
            "**קבועים:** $k = 9\\times10^9$ N·m²/C²; $\\epsilon_0 = 8.85\\times10^{-12}$ F/m.\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint בלי רשימות."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Gauss's law:** $\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ — always true\n"
            "- **Sphere outside:** $E = kQ/r^2$; **inside uniform solid:** $E = kQr/R^3$\n"
            "- **Hollow shell inside:** $E = 0$; **conductor inside:** $E = 0$\n"
            "- **Infinite line:** $E = \\lambda/(2\\pi\\epsilon_0 r)$\n"
            "- **Infinite plane:** $E = \\sigma/(2\\epsilon_0)$ — uniform, no $r$ dependence\n"
            "- **Two plates $\\pm\\sigma$:** $E = \\sigma/\\epsilon_0$ between; $0$ outside\n"
            "- **Method:** Match Gaussian surface to symmetry; pull $E$ out when $|E|$ is constant\n\n"
            "**Takeaway:** Identify symmetry first — the Gaussian surface choice determines "
            "whether Gauss's law becomes a one-line solution or an impossible integral."
        ),
        "body_he_md": (
            "- **חוק גאוס:** $\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ — תמיד נכון\n"
            "- **כדור בחוץ:** $E = kQ/r^2$; **מוצק אחיד בפנים:** $E = kQr/R^3$\n"
            "- **קליפה חלולה בפנים:** $E = 0$; **מוליך בפנים:** $E = 0$\n"
            "- **קו אינסופי:** $E = \\lambda/(2\\pi\\epsilon_0 r)$\n"
            "- **מישור אינסופי:** $E = \\sigma/(2\\epsilon_0)$ — אחיד, ללא תלות ב-$r$\n"
            "- **שני לוחות $\\pm\\sigma$:** $E = \\sigma/\\epsilon_0$ ביניהם; $0$ בחוץ\n"
            "- **שיטה:** התאימו משטח גאוס לסימטריה; הוציאו $E$ כש-$|E|$ קבוע\n\n"
            "**מסקנה:** זהו סימטריה קודם — בחירת משטח גאוס קובעת "
            "אם חוק גאוס הופך לפתרון בשורה אחת או לאינטגרל בלתי-אפשרי."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:** Gauss's law gives total flux through any closed surface: "
            "$\\Phi = Q_{\\text{enc}}/\\epsilon_0$. The sphere encloses the point charge "
            "$q = 6\\;\\text{nC}$, so:\n"
            "$$\\Phi = \\frac{6\\times10^{-9}}{8.85\\times10^{-12}} \\approx 678\\;\\text{N·m}^2/\\text{C}$$\n\n"
            "**How to think about it:** Flux depends only on **enclosed charge**, not on sphere "
            "radius. A larger sphere has the same flux — field weakens as $1/r^2$ but area "
            "grows as $r^2$, exactly compensating.\n\n"
            "**Common slip:** Using $E = kq/r^2$ and multiplying by area with wrong radius "
            "dependence, or forgetting to convert nC to C.\n\n"
            "**Exam tip:** For a point charge, $\\Phi = q/\\epsilon_0$ always — "
            "memorize this shortcut for flux-only questions."
        ),
        "explanation_he": (
            "**למה זה נכון:** חוק גאוס נותן שטף כולל דרך משטח סגור: "
            "$\\Phi = Q_{\\text{enc}}/\\epsilon_0$. הכדור כולל מטען נקודתי "
            "$q = 6\\;\\text{nC}$, לכן:\n"
            "$$\\Phi = \\frac{6\\times10^{-9}}{8.85\\times10^{-12}} \\approx 678\\;\\text{N·m}^2/\\text{C}$$\n\n"
            "**איך לחשוב:** שטף תלוי רק ב**מטען כלוא**, לא ברדיוס הכדור. "
            "כדור גדול יותר — אותו שטף — השדה חלש כ-$1/r^2$ אך השטח גדל כ-$r^2$.\n\n"
            "**טעות נפוצה:** שימוש ב-$E = kq/r^2$ עם שטח ברדיוס שגוי, "
            "או שכחת המרת nC ל-C.\n\n"
            "**טיפ לבחינה:** למטען נקודתי, $\\Phi = q/\\epsilon_0$ תמיד — "
            "שמרו קיצור דרך זה לשאלות שטף בלבד. "
            "אין צורך לחשב שדה או להכפיל בשטח."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** In electrostatic equilibrium, all excess charge on a "
            "conductor resides on its **surface**. Any Gaussian surface drawn inside the "
            "bulk encloses zero charge, so Gauss's law gives $E = 0$ everywhere inside.\n\n"
            "**How to think about it:** If $E \\neq 0$ inside, free electrons would accelerate "
            "until they cancel the field — that is the definition of equilibrium. "
            "Option \"Proportional to $r$\" applies to uniformly charged **insulators**, not conductors.\n\n"
            "**Common slip:** Choosing $E = kQ/R^2$ (that is the surface field, not interior), "
            "or \"Maximum at center\" (confusing with insulator formulas).\n\n"
            "**Exam tip:** \"Inside conductor\" → immediate answer $E = 0$. "
            "No calculation needed."
        ),
        "explanation_he": (
            "**למה זה נכון:** בשיווי משקל אלקטרוסטטי, כל המטען העודף על **פני** "
            "המוליך. כל משטח גאוס בתוך הנפח כולל אפס מטען, "
            "לכן חוק גאוס נותן $E = 0$ בכל מקום בפנים.\n\n"
            "**איך לחשוב:** אם $E \\neq 0$ בפנים, אלקטרונים חופשיים יואצו "
            "עד שיבטלו את השדה — זו הגדרת שיווי משקל. "
            "\"יחסי ל-$r$\" מתאים ל**מבודדים** טעונים אחיד, לא למוליכים.\n\n"
            "**טעות נפוצה:** בחירת $E = kQ/R^2$ (שדה על הפ surface, לא בפנים), "
            "או \"מקסימלי במרכז\" (בלבול עם נוסחאות מבודד).\n\n"
            "**טיפ לבחינה:** \"בתוך מוליך\" → $E = 0$ מיד. "
            "אין צורך בחישוב."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** An infinite line charge has **cylindrical symmetry** — "
            "$\\vec{E}$ is radial and $|E|$ depends only on $r$. A coaxial cylinder exploits "
            "this: $|E|$ is constant on the curved wall, and flat end caps contribute zero "
            "flux because $\\vec{E}$ is parallel to them.\n\n"
            "**How to think about it:** Match the Gaussian surface to the symmetry of the "
            "**source**, not the field point. A sphere centered on the line fails because "
            "$|E|$ is not constant on a spherical surface.\n\n"
            "**Common slip:** Choosing a sphere ( $|E|$ varies on sphere around a line) "
            "or a box (no constant-$E$ face to pull out).\n\n"
            "**Exam tip:** Line charge → cylinder. Point charge → sphere. "
            "Plane → pill-box. Memorize this triplet."
        ),
        "explanation_he": (
            "**למה זה נכון:** קו מטען אינסופי בעל **סימטריה גלילית** — "
            "$\\vec{E}$ רדיאלי ו-$|E|$ תלוי רק ב-$r$. גליל קואקסיאלי מנצל "
            "זאת: $|E|$ קבוע על הקיר המעוקל, ובסיסים שטוחים תורמים שטף אפס "
            "כי $\\vec{E}$ מקביל להם.\n\n"
            "**איך לחשוב:** התאימו משטח גאוס לסימטריה של **המקור**, "
            "לא לנקודת השדה. כדור במרכז הקו נכשל כי $|E|$ לא קבוע על משטח כדורי.\n\n"
            "**טעות נפוצה:** בחירת כדור ($|E|$ משתנה סביב קו) "
            "או קופסה (אין פנים עם $E$ קבוע).\n\n"
            "**טיפ לבחינה:** קו מטען → גליל. מטען נקודתי → כדור. "
            "מישור → קופסת גלולה. שמרו שלישייה זו."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At $r = 2\\;\\text{cm} < R = 4\\;\\text{cm}$, we are "
            "**inside** a uniformly charged solid sphere. Use:\n"
            "$$E = \\frac{kQr}{R^3} = "
            "\\frac{(9\\times10^9)(10\\times10^{-9})(0.02)}{(0.04)^3} "
            "\\approx 28125\\;\\text{N/C}$$\n\n"
            "**How to think about it:** Enclosed charge scales as $(r/R)^3$, giving linear "
            "field growth inside. Do not use $E = kQ/r^2$ inside — that is for $r > R$ only.\n\n"
            "**Common slip:** Applying the outside formula inside, or forgetting to cube "
            "$R = 0.04$ m in the denominator.\n\n"
            "**Exam tip:** Check $r$ vs $R$ first. Inside uniform sphere: $E \\propto r$. "
            "At surface, both formulas agree: $E = kQ/R^2$. "
            "Write which region you are in before substituting numbers."
        ),
        "explanation_he": (
            "**למה זה נכון:** ב-$r = 2\\;\\text{cm} < R = 4\\;\\text{cm}$, "
            "אנחנו **בפנים** כדור מוצק טעון אחיד. השתמשו:\n"
            "$$E = \\frac{kQr}{R^3} = "
            "\\frac{(9\\times10^9)(10\\times10^{-9})(0.02)}{(0.04)^3} "
            "\\approx 28125\\;\\text{N/C}$$\n\n"
            "**איך לחשוב:** מטען כלוא גדל כ-$(r/R)^3$, מה שנותן גדילה ליניארית "
            "בפנים. אל תשתמשו ב-$E = kQ/r^2$ בפנים — זה ל-$r > R$ בלבד. "
            "המרו nC ל-C ו-R ל-m לפני חישוב.\n\n"
            "**טעות נפוצה:** יישום נוסחת חוץ בפנים, או שכחת העלאת "
            "$R = 0.04$ m במכנה. גם בלבול עם כדור מוליך ($E=0$ בפנים).\n\n"
            "**טיפ לבחינה:** בדקו $r$ מול $R$ קודם. בכדור אחיד בפנים: $E \\propto r$. "
            "על הפ surface, שתי הנוסחאות מסכימות. כתבו באיזה אזור אתם לפני הצבה."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** By symmetry, $\\vec{E}$ is perpendicular to the plane "
            "with equal magnitude on both sides. A pill-box with faces of area $A$ gives "
            "flux $2EA$ (both faces contribute). Enclosed charge is $Q_{\\text{enc}} = \\sigma A$, so:\n"
            "$$2EA = \\frac{\\sigma A}{\\epsilon_0} \\implies E = \\frac{\\sigma}{2\\epsilon_0}$$\n\n"
            "**How to think about it:** The factor 2 comes from **two faces** of the pill-box. "
            "Each face sees the same $E$; sides parallel to $\\vec{E}$ contribute zero flux.\n\n"
            "**Common slip:** Using $\\sigma/\\epsilon_0$ (forgetting the 1/2 for one plate), "
            "or arguing $E$ depends on distance from the plane.\n\n"
            "**Exam tip:** State symmetry ($\\vec{E} \\perp$ plane, uniform) before "
            "choosing the pill-box — examiners require this reasoning chain."
        ),
        "explanation_he": (
            "**למה זה נכון:** מסימטריה, $\\vec{E}$ מאונך למישור "
            "באותו גודל משני הצדדים. קופסת גלולה עם פנים שטח $A$ "
            "נותנת שטף $2EA$ (שני פנים תורמים). מטען כלוא $Q_{\\text{enc}} = \\sigma A$, לכן:\n"
            "$$2EA = \\frac{\\sigma A}{\\epsilon_0} \\implies E = \\frac{\\sigma}{2\\epsilon_0}$$\n\n"
            "**איך לחשוב:** גורם 2 מגיע מ**שני פנים** של קופסת הגלולה. "
            "כל פנים רואה אותו $E$; צדדים מקבילים ל-$\\vec{E}$ תורמים שטף אפס.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\sigma/\\epsilon_0$ (שכחת 1/2 ללוח בודד), "
            "או טענה ש-$E$ תלוי במרחק מהמישור.\n\n"
            "**טיפ לבחינה:** ציינו סימטריה ($\\vec{E} \\perp$ מישור, אחיד) "
            "לפני בחירת קופסת הגלולה — הבחינה דורשת שרשרת נימוק זו."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** By Gauss's law, total flux through a closed surface "
            "equals enclosed charge divided by $\\epsilon_0$:\n"
            "$$\\Phi = \\frac{Q_{\\text{enc}}}{\\epsilon_0} = "
            "\\frac{5\\times10^{-9}}{8.85\\times10^{-12}} \\approx 565\\;\\text{N·m}^2/\\text{C}$$\n\n"
            "**How to think about it:** The point charge sits at the sphere center, so all "
            "field lines pass outward through the surface. Radius $20$ cm does not affect "
            "flux — only $Q_{\\text{enc}}$ matters.\n\n"
            "**Common slip:** Computing field at surface and multiplying by $4\\pi r^2$ "
            "with arithmetic errors, or using $\\mu$C without converting to C.\n\n"
            "**Exam tip:** Flux questions often need only $\\Phi = q/\\epsilon_0$ — "
            "skip the field calculation entirely."
        ),
        "explanation_he": (
            "**למה זה נכון:** לפי חוק גאוס, שטף כולל דרך משטח סגור "
            "שווה מטען כלוא חלקי $\\epsilon_0$:\n"
            "$$\\Phi = \\frac{Q_{\\text{enc}}}{\\epsilon_0} = "
            "\\frac{5\\times10^{-9}}{8.85\\times10^{-12}} \\approx 565\\;\\text{N·m}^2/\\text{C}$$\n\n"
            "**איך לחשוב:** המטען הנקודתי במרכז הכדור, "
            "לכן כל קווי השדה יוצאים דרך המשטח. רדיוס $20$ cm "
            "לא משפיע על שטף — רק $Q_{\\text{enc}}$ חשוב.\n\n"
            "**טעות נפוצה:** חישוב שדה על המשטח והכפלה ב-$4\\pi r^2$ "
            "עם שגיאות חשבון, או $\\mu$C בלי המרה ל-C.\n\n"
            "**טיפ לבחינה:** שאלות שטף לעיתים דורשות רק $\\Phi = q/\\epsilon_0$ — "
            "דלגו על חישוב שדה. המרו nC ל-C לפני חילוק ב-$\\epsilon_0$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At $r = 10\\;\\text{cm} > R = 6\\;\\text{cm}$, we are "
            "outside the conducting sphere. Treat all charge as concentrated at center:\n"
            "$$E = \\frac{k|Q|}{r^2} = "
            "\\frac{(9\\times10^9)(3\\times10^{-9})}{(0.10)^2} = 2700\\;\\text{N/C}$$\n"
            "Negative charge → field points **inward** toward the sphere.\n\n"
            "**How to think about it:** Outside any spherically symmetric distribution, "
            "the field matches a point charge at the center. Use $|Q|$ for magnitude; "
            "assign direction from the sign.\n\n"
            "**Common slip:** Using $R$ instead of $r$ in denominator, or forgetting "
            "inward direction for negative $Q$.\n\n"
            "**Exam tip:** Always state magnitude AND direction for field answers."
        ),
        "explanation_he": (
            "**למה זה נכון:** ב-$r = 10\\;\\text{cm} > R = 6\\;\\text{cm}$, "
            "אנחנו מחוץ לכדור המוליך. התייחסו לכל המטען במרכז:\n"
            "$$E = \\frac{k|Q|}{r^2} = "
            "\\frac{(9\\times10^9)(3\\times10^{-9})}{(0.10)^2} = 2700\\;\\text{N/C}$$\n"
            "מטען שלילי → שדה **פנימה** לכיוון הכדור.\n\n"
            "**איך לחשוב:** מחוץ לכל פילוג סימטרי כדורית, "
            "השדה כמו מטען נקודתי במרכז. השתמשו ב-$|Q|$ לגודל; "
            "קבעו כיוון מהסימן.\n\n"
            "**טעות נפוצה:** שימוש ב-$R$ במקום $r$ במכנה, "
            "או שכחת כיוון פנימה ל-$Q$ שלילי.\n\n"
            "**טיפ לבחינה:** ציינו תמיד גודל **וגם** כיוון בתשובות שדה. "
            "מחוץ לכדור מוליך, התייחסו לכל $Q$ כמטען נקודתי במרכז. "
            "המרו cm ל-m לפני חישוב $r^2$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Infinite line charge with cylindrical symmetry gives:\n"
            "$$E = \\frac{\\lambda}{2\\pi\\epsilon_0 r} = "
            "\\frac{8\\times10^{-6}}{2\\pi(8.85\\times10^{-12})(0.04)} "
            "\\approx 3.59\\times10^6\\;\\text{N/C}$$\n\n"
            "**How to think about it:** Choose coaxial Gaussian cylinder. Flux through "
            "curved wall: $E \\cdot 2\\pi r L$. Enclosed charge: $\\lambda L$. "
            "Cancel $L$ and solve for $E \\propto 1/r$. Convert $\\mu$C/m to C/m first.\n\n"
            "**Common slip:** Using $1/r^2$ (confusing with point charge), "
            "forgetting $2\\pi$ in denominator, or leaving $\\mu$C unconverted.\n\n"
            "**Exam tip:** Line charge field falls as $1/r$, not $1/r^2$. "
            "Double the distance → halve the field. Write $\\lambda$ in C/m before substituting."
        ),
        "explanation_he": (
            "**למה זה נכון:** קו מטען אינסופי עם סימטריה גלילית נותן:\n"
            "$$E = \\frac{\\lambda}{2\\pi\\epsilon_0 r} = "
            "\\frac{8\\times10^{-6}}{2\\pi(8.85\\times10^{-12})(0.04)} "
            "\\approx 3.59\\times10^6\\;\\text{N/C}$$\n\n"
            "**איך לחשוב:** בחרו גליל גאוס קואקסיאלי. שטף דרך קיר מעוקל: "
            "$E \\cdot 2\\pi r L$. מטען כלוא: $\\lambda L$. "
            "בטלו $L$ ופתרו ל-$E \\propto 1/r$. המירו $\\mu$C/m ל-C/m קודם.\n\n"
            "**טעות נפוצה:** שימוש ב-$1/r^2$ (בלבול עם מטען נקודתי), "
            "שכחת $2\\pi$ במכנה, או $\\mu$C לא מומר.\n\n"
            "**טיפ לבחינה:** שדה קו מטען יורד כ-$1/r$, לא $1/r^2$. "
            "כפלת מרחק מחלקת את השדה בשניים. כתבו $\\lambda$ ב-C/m לפני הצבה. "
            "בחרו גליל גאוס קואקסיאלי, לא כדור."
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
