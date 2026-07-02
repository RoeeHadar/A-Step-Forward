#!/usr/bin/env python3
"""Expand capacitors_dielectrics.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/capacitors_dielectrics.json"

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
            "Every smartphone, flash camera, and defibrillator stores energy in **capacitors** — "
            "devices that hold electric charge (and energy) without any chemical reaction. "
            "A capacitor charges in microseconds and can dump all its stored energy in nanoseconds, "
            "which is why camera flashes and heart defibrillators rely on them.\n\n"
            "Unlike a battery, a capacitor does not create charge — it **separates** charge onto "
            "two conductors, creating a potential difference $V$ and storing energy in the "
            "electric field between the plates.\n\n"
            "In **Israeli university physics (Electricity & Magnetism)**, capacitors appear in:\n"
            "- Computing $C$ for parallel plates, spheres, and cylinders\n"
            "- Dielectric effects on $C$, $E$, and $V$ — the most common exam trap\n"
            "- Energy stored: $U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$\n"
            "- Series and parallel combinations (rules opposite to resistors!)\n\n"
            "This lesson builds on `concept:electric_field` and `concept:electric_potential`. "
            "Master the disconnected-vs-connected dielectric cases before attempting energy problems."
        ),
        "body_he_md": (
            "כל סמארטפון, מצלמת פלאש ודפיברילטור מאחסן אנרגיה ב**קבלים** — "
            "מכשירים שמחזיקים מטען חשמלי (ואנרגיה) ללא תגובה כימית. "
            "קבל נטען במיקרו-שניות ויכול לשחרר את כל אנרגייתו בנאנו-שניות, "
            "לכן פלאשים ודפיברילטורים מסתמכים עליהם.\n\n"
            "בניגוד לסוללה, קבל לא יוצר מטען — הוא **מפריד** מטען על שני מוליכים, "
            "יוצר הפרש פוטנציאל $V$ ומאחסן אנרגיה בשדה החשמלי בין הלוחות.\n\n"
            "**בפיזיקה אוניברסיטאית ישראלית (חשמל ומגנטיות)**, קבלים מופיעים ב:\n"
            "- חישוב $C$ עבור לוחות מקבילים, כדורים וגלילים\n"
            "- השפעות דיאלקטריקה על $C$, $E$ ו-$V$ — המלכודת הנפוצה בבחינות\n"
            "- אנרגיה מאוחסנת: $U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$\n"
            "- חיבור טורי ומקבילי (כללים הפוכים מנגדים!)\n\n"
            "שיעור זה מבוסס על `concept:electric_field` ו-`concept:electric_potential`. "
            "שלטו במקרי דיאלקטריקה (מנותק לעומת מחובר) לפני בעיות אנרגיה."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Capacitance** $C$ is defined as the ratio of charge stored to the voltage "
            "across the capacitor:\n\n"
            "$$\\boxed{C = \\frac{Q}{V}}$$\n\n"
            "- SI unit: **farad** (F) = C/V. One farad is enormous; typical values range "
            "from pF ($10^{-12}$) to mF ($10^{-3}$).\n"
            "- $C$ depends only on **geometry** and the medium between plates — not on $Q$ or $V$.\n\n"
            "**Parallel-plate capacitor** (plate area $A$, separation $d$, vacuum):\n"
            "$$C_0 = \\frac{\\epsilon_0 A}{d}, \\quad \\epsilon_0 = 8.85\\times10^{-12}\\;\\text{F/m}$$\n\n"
            "**With dielectric** (dielectric constant $\\kappa \\geq 1$):\n"
            "$$C = \\kappa C_0 = \\frac{\\kappa\\epsilon_0 A}{d}$$\n"
            "The dielectric polarizes, partially canceling the field and allowing more charge "
            "at the same voltage.\n\n"
            "**Energy stored** (three equivalent forms):\n"
            "$$\\boxed{U = \\frac{Q^2}{2C} = \\frac{1}{2}CV^2 = \\frac{1}{2}QV}$$\n\n"
            "**Energy density** in the electric field:\n"
            "$$u = \\frac{1}{2}\\epsilon_0 E^2 \\quad \\text{(vacuum)}, \\qquad "
            "u = \\frac{1}{2}\\kappa\\epsilon_0 E^2 \\quad \\text{(dielectric)}$$\n\n"
            "Use whichever energy formula matches the two quantities you already know.\n\n"
            "**Physical meaning:** Capacitance measures how much charge a device can store "
            "per volt of potential difference. A 1 μF capacitor stores 1 μC when charged to 1 V. "
            "Increasing plate area or decreasing separation increases $C$; inserting a dielectric "
            "multiplies $C$ by $\\kappa$ because bound charges reduce the effective field."
        ),
        "body_he_md": (
            "**קיבול** $C$ מוגדר כיחס בין המטען המאוחסן למתח על פני הקבל:\n\n"
            "$$\\boxed{C = \\frac{Q}{V}}$$\n\n"
            "- יחידת SI: **פאראד** (F) = C/V. פאראד אחד ענק; ערכים טיפוסיים "
            "מ-pF ($10^{-12}$) עד mF ($10^{-3}$).\n"
            "- $C$ תלוי רק ב**גאומטריה** ובתווך בין הלוחות — לא ב-$Q$ או $V$.\n\n"
            "**קבל לוחות מקבילים** (שטח לוח $A$, ריווח $d$, ריק):\n"
            "$$C_0 = \\frac{\\epsilon_0 A}{d}, \\quad \\epsilon_0 = 8.85\\times10^{-12}\\;\\text{F/m}$$\n\n"
            "**עם דיאלקטריקה** (קבוע דיאלקטרי $\\kappa \\geq 1$):\n"
            "$$C = \\kappa C_0 = \\frac{\\kappa\\epsilon_0 A}{d}$$\n"
            "הדיאלקטריקה מתקוטבת, מבטלת חלקית את השדה ומאפשרת יותר מטען באותו מתח.\n\n"
            "**אנרגיה מאוחסנת** (שלוש צורות שקולות):\n"
            "$$\\boxed{U = \\frac{Q^2}{2C} = \\frac{1}{2}CV^2 = \\frac{1}{2}QV}$$\n\n"
            "**צפיפות אנרגיה** בשדה החשמלי:\n"
            "$$u = \\frac{1}{2}\\epsilon_0 E^2 \\quad \\text{(ריק)}, \\qquad "
            "u = \\frac{1}{2}\\kappa\\epsilon_0 E^2 \\quad \\text{(דיאלקטריקה)}$$\n\n"
            "השתמשו בנוסחת האנרגיה שמתאימה לשתי הכמויות שכבר ידועות לכם.\n\n"
            "**משמעות פיזיקלית:** קיבול מודד כמה מטען המכשיר יכול לאחסן "
            "לוולט הפרש פוטנציאל. קבל 1 μF מאחסן 1 μC בטעינה ל-1 V. "
            "הגדלת שטח לוח או הקטנת ריווח מגדילה $C$; הכנסת דיאלקטריקה "
            "מכפילה $C$ ב-$\\kappa$ כי מטענים קשורים מקטינים את השדה האפקטיבי."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Capacitors in series\n"
            "$$\\frac{1}{C_{\\text{eq}}} = \\frac{1}{C_1} + \\frac{1}{C_2} + \\cdots$$\n"
            "Same charge $Q$ on each capacitor (charge has nowhere else to go in a single loop); "
            "voltages add: $V_{\\text{total}} = V_1 + V_2 + \\cdots$. "
            "Series gives **smaller** equivalent capacitance — like resistors in parallel.\n\n"
            "### Capacitors in parallel\n"
            "$$C_{\\text{eq}} = C_1 + C_2 + \\cdots$$\n"
            "Same voltage $V$ across each branch; charges add: $Q_{\\text{total}} = Q_1 + Q_2 + \\cdots$. "
            "Parallel gives **larger** equivalent capacitance.\n\n"
            "### Effect of inserting a dielectric\n\n"
            "**Case 1: Capacitor disconnected from battery** ($Q$ constant):\n"
            "- $C \\to \\kappa C$ → $V = Q/C$ decreases by factor $\\kappa$\n"
            "- $E = V/d$ decreases → stored energy $U = Q^2/(2C)$ **decreases** by $\\kappa$\n\n"
            "**Case 2: Capacitor connected to battery** ($V$ constant):\n"
            "- $C \\to \\kappa C$ → $Q = CV$ increases by $\\kappa$\n"
            "- $E = V/d$ unchanged → $U = \\frac{1}{2}CV^2$ **increases** by $\\kappa$\n"
            "- Battery supplies extra charge; excess energy goes into dielectric polarization.\n\n"
            "**Why?** Dielectric dipoles partially cancel the applied field. "
            "Inside the material, $E_{\\text{inside}} = E_{\\text{free}}/\\kappa$.\n\n"
            "### Spherical and cylindrical capacitors\n"
            "- Spherical: $C = 4\\pi\\epsilon_0 \\frac{ab}{b-a}$ (inner radius $a$, outer $b$)\n"
            "- Cylindrical (length $\\ell$): $C = \\frac{2\\pi\\epsilon_0 \\ell}{\\ln(b/a)}$\n\n"
            "**Partial dielectrics:** When only part of the gap is filled, treat the region "
            "as two (or more) capacitors in series — each sub-gap has its own $C_i$, "
            "then combine with $1/C_{\\text{eq}} = \\sum 1/C_i$."
        ),
        "body_he_md": (
            "### קבלים בטור\n"
            "$$\\frac{1}{C_{\\text{eq}}} = \\frac{1}{C_1} + \\frac{1}{C_2} + \\cdots$$\n"
            "אותו מטען $Q$ על כל קבל (למטען אין לאן ללכת בלולאה אחת); "
            "מתחים מתחברים: $V_{\\text{כולל}} = V_1 + V_2 + \\cdots$. "
            "טור נותן קיבול שקול **קטן יותר** — כמו נגדים במקביל.\n\n"
            "### קבלים במקביל\n"
            "$$C_{\\text{eq}} = C_1 + C_2 + \\cdots$$\n"
            "אותו מתח $V$ על כל ענף; מטענים מתחברים: $Q_{\\text{כולל}} = Q_1 + Q_2 + \\cdots$. "
            "מקביל נותן קיבול שקול **גדול יותר**.\n\n"
            "### אפקט הכנסת דיאלקטריקה\n\n"
            "**מקרה 1: קבל מנותק מסוללה** ($Q$ קבוע):\n"
            "- $C \\to \\kappa C$ → $V = Q/C$ יורד פי $\\kappa$\n"
            "- $E = V/d$ יורד → אנרגיה $U = Q^2/(2C)$ **יורדת** פי $\\kappa$\n\n"
            "**מקרה 2: קבל מחובר לסוללה** ($V$ קבוע):\n"
            "- $C \\to \\kappa C$ → $Q = CV$ עולה פי $\\kappa$\n"
            "- $E = V/d$ ללא שינוי → $U = \\frac{1}{2}CV^2$ **עולה** פי $\\kappa$\n"
            "- הסוללה מספקת מטען נוסף; אנרגיה עודפת הולכת לקיטוב הדיאלקטריקה.\n\n"
            "**מדוע?** דיפולים בדיאלקטריקה מבטלים חלקית את השדה המופעל. "
            "בתוך החומר, $E_{\\text{פנימי}} = E_{\\text{חופשי}}/\\kappa$.\n\n"
            "### קבלים כדוריים וגליליים\n"
            "- כדורי: $C = 4\\pi\\epsilon_0 \\frac{ab}{b-a}$ (רדיוס פנימי $a$, חיצוני $b$)\n"
            "- גלילי (אורך $\\ell$): $C = \\frac{2\\pi\\epsilon_0 \\ell}{\\ln(b/a)}$\n\n"
            "**דיאלקטריקה חלקית:** כשחלק מהסדק מלא, התייחסו לאזור "
            "כשני קבלים (או יותר) בטור — לכל תת-סדק $C_i$ משלו, "
            "ואז $1/C_{\\text{eq}} = \\sum 1/C_i$."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A parallel-plate capacitor has $A = 0.02\\;\\text{m}^2$ and "
            "$d = 1\\;\\text{mm} = 10^{-3}\\;\\text{m}$. "
            "(a) Find $C$. (b) If $V = 100\\;\\text{V}$, find $Q$ and $U$.\n\n"
            "### Move 1: Identify formula and convert units\n"
            "Vacuum parallel-plate: $C = \\epsilon_0 A/d$. "
            "Area is already in m²; separation $d = 10^{-3}$ m.\n\n"
            "### Move 2: Compute capacitance (part a)\n"
            "$$C = \\frac{\\epsilon_0 A}{d} = \\frac{(8.85\\times10^{-12})(0.02)}{10^{-3}} "
            "= \\frac{1.77\\times10^{-13}}{10^{-3}} = 1.77\\times10^{-10}\\;\\text{F} = 177\\;\\text{pF}$$\n\n"
            "### Move 3: Find charge (part b)\n"
            "$$Q = CV = (1.77\\times10^{-10})(100) = 1.77\\times10^{-8}\\;\\text{C} = 17.7\\;\\text{nC}$$\n\n"
            "### Move 4: Find stored energy\n"
            "$$U = \\frac{1}{2}CV^2 = \\frac{1}{2}(1.77\\times10^{-10})(10^4) "
            "= 8.85\\times10^{-7}\\;\\text{J} = 0.885\\;\\mu\\text{J}$$\n\n"
            "**Self-check:** $U = \\frac{1}{2}QV = \\frac{1}{2}(17.7\\times10^{-9})(100) "
            "\\approx 0.885\\;\\mu\\text{J}$ — consistent. "
            "Typical parallel-plate values are pF to nF for small plates.\n\n"
            "**Bagrut/university context:** This three-step pattern — find $C$ from geometry, "
            "then $Q = CV$, then $U = \\frac{1}{2}CV^2$ — appears in nearly every capacitor "
            "problem. Always convert mm to m for $d$ before substituting into $\\epsilon_0 A/d$.\n\n"
            "**Move 5 sanity check:** If $C$ came out in F instead of pF, you likely forgot "
            "that $\\epsilon_0 \\approx 10^{-11}$ — expect nano or pico farads for lab-scale plates. "
            "Report $C$ with appropriate SI prefix."
        ),
        "body_he_md": (
            "**נתון:** קבל לוחות מקבילים עם $A = 0.02\\;\\text{m}^2$ ו-"
            "$d = 1\\;\\text{mm} = 10^{-3}\\;\\text{m}$. "
            "(א) מצא $C$. (ב) אם $V = 100\\;\\text{V}$, מצא $Q$ ו-$U$.\n\n"
            "### צעד 1: זיהוי נוסחה והמרת יחידות\n"
            "לוחות מקבילים בריק: $C = \\epsilon_0 A/d$. "
            "שטח כבר ב-m²; ריווח $d = 10^{-3}$ m.\n\n"
            "### צעד 2: חישוב קיבול (חלק א)\n"
            "$$C = \\frac{\\epsilon_0 A}{d} = \\frac{(8.85\\times10^{-12})(0.02)}{10^{-3}} "
            "= 1.77\\times10^{-10}\\;\\text{F} = 177\\;\\text{pF}$$\n\n"
            "### צעד 3: מציאת מטען (חלק ב)\n"
            "$$Q = CV = (1.77\\times10^{-10})(100) = 1.77\\times10^{-8}\\;\\text{C} = 17.7\\;\\text{nC}$$\n\n"
            "### צעד 4: מציאת אנרגיה מאוחסנת\n"
            "$$U = \\frac{1}{2}CV^2 = \\frac{1}{2}(1.77\\times10^{-10})(10^4) "
            "= 8.85\\times10^{-7}\\;\\text{J} = 0.885\\;\\mu\\text{J}$$\n\n"
            "**בדיקה:** $U = \\frac{1}{2}QV \\approx 0.885\\;\\mu\\text{J}$ — עקבי. "
            "ערכים טיפוסיים ללוחות מקבילים: pF עד nF ללוחות קטנים.\n\n"
            "**הקשר בגרות/אוניברסיטה:** דפוס שלושה שלבים — מצא $C$ מגאומטריה, "
            "אחר כך $Q = CV$, אחר כך $U = \\frac{1}{2}CV^2$ — מופיע בכמעט כל בעיית קבל. "
            "המירו תמיד mm ל-m עבור $d$ לפני הצבה ב-$\\epsilon_0 A/d$.\n\n"
            "**צעד 5 בדיקה:** אם $C$ יצא ב-F במקום pF, כנראה שכחתם "
            "ש-$\\epsilon_0 \\approx 10^{-11}$ — צפו ל-nano או pico farad ללוחות במעבדה."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** $C_1 = 3\\;\\mu\\text{F}$, $C_2 = 6\\;\\mu\\text{F}$, "
            "$V = 12\\;\\text{V}$. Find total $C$ and total energy when "
            "(a) in series and (b) in parallel.\n\n"
            "### Move 1: Series combination (part a)\n"
            "$$\\frac{1}{C_{\\text{eq}}} = \\frac{1}{3} + \\frac{1}{6} = \\frac{2}{6} + \\frac{1}{6} "
            "= \\frac{3}{6} = \\frac{1}{2} \\implies C_{\\text{eq}} = 2\\;\\mu\\text{F}$$\n"
            "Series gives **smaller** $C$ than either alone — charge is limited.\n\n"
            "### Move 2: Energy in series at 12 V\n"
            "$$U = \\frac{1}{2}C_{\\text{eq}}V^2 = \\frac{1}{2}(2\\times10^{-6})(144) "
            "= 1.44\\times10^{-4}\\;\\text{J} = 144\\;\\mu\\text{J}$$\n\n"
            "### Move 3: Parallel combination (part b)\n"
            "$$C_{\\text{eq}} = 3 + 6 = 9\\;\\mu\\text{F}$$\n"
            "$$U = \\frac{1}{2}(9\\times10^{-6})(144) = 6.48\\times10^{-4}\\;\\text{J} = 648\\;\\mu\\text{J}$$\n\n"
            "**Insight:** Parallel stores more energy at the same voltage because "
            "more charge can flow onto the plates. Remember: capacitor series/parallel "
            "rules are **opposite** to resistor rules — a common exam trap.\n\n"
            "**Self-check:** Series $C_{\\text{eq}} = 2\\;\\mu\\text{F} < 3\\;\\mu\\text{F}$ ✓. "
            "Parallel $C_{\\text{eq}} = 9\\;\\mu\\text{F} > 6\\;\\mu\\text{F}$ ✓. "
            "Energy ratio parallel/series = $648/144 = 4.5 = (9/2)^2$ — consistent with "
            "$U \\propto C$ at fixed $V$.\n\n"
            "**Move 4 — Compare charges:** In series, $Q = C_{\\text{eq}} V = 24\\;\\mu\\text{C}$ on each plate. "
            "In parallel, total $Q = 9 \\times 12 = 108\\;\\mu\\text{C}$ — four times more charge stored "
            "at the same applied voltage."
        ),
        "body_he_md": (
            "**נתון:** $C_1 = 3\\;\\mu\\text{F}$, $C_2 = 6\\;\\mu\\text{F}$, "
            "$V = 12\\;\\text{V}$. מצא $C$ כולל ואנרגיה כוללת ב-(א) טור ו-(ב) מקביל.\n\n"
            "### צעד 1: חיבור טור (חלק א)\n"
            "$$\\frac{1}{C_{\\text{eq}}} = \\frac{1}{3} + \\frac{1}{6} = \\frac{1}{2} "
            "\\implies C_{\\text{eq}} = 2\\;\\mu\\text{F}$$\n"
            "טור נותן $C$ **קטן יותר** מכל אחד בנפרד — המטען מוגבל.\n\n"
            "### צעד 2: אנרגיה בטור ב-12 V\n"
            "$$U = \\frac{1}{2}C_{\\text{eq}}V^2 = \\frac{1}{2}(2\\times10^{-6})(144) "
            "= 144\\;\\mu\\text{J}$$\n\n"
            "### צעד 3: חיבור מקביל (חלק ב)\n"
            "$$C_{\\text{eq}} = 3 + 6 = 9\\;\\mu\\text{F}$$\n"
            "$$U = \\frac{1}{2}(9\\times10^{-6})(144) = 648\\;\\mu\\text{J}$$\n\n"
            "**תובנה:** מקביל מאחסן יותר אנרגיה באותו מתח כי יותר מטען יכול לזרום ללוחות. "
            "זכרו: כללי טור/מקביל לקבלים **הפוכים** מנגדים — מלכודת בחינה נפוצה.\n\n"
            "**בדיקה:** טור $C_{\\text{eq}} = 2\\;\\mu\\text{F} < 3\\;\\mu\\text{F}$ ✓. "
            "מקביל $C_{\\text{eq}} = 9\\;\\mu\\text{F} > 6\\;\\mu\\text{F}$ ✓. "
            "יחס אנרגיה מקביל/טור = $648/144 = 4.5 = (9/2)^2$ — עקבי עם "
            "$U \\propto C$ ב-$V$ קבוע.\n\n"
            "**צעד 4 — השוואת מטענים:** בטור, $Q = C_{\\text{eq}} V = 24\\;\\mu\\text{C}$ על כל לוח. "
            "במקביל, $Q$ כולל = $9 \\times 12 = 108\\;\\mu\\text{C}$ — פי 4.5 יותר מטען מאוחסן."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** Parallel-plate capacitor: $A = 0.05\\;\\text{m}^2$, $d = 2\\;\\text{mm}$, "
            "connected to $V = 200\\;\\text{V}$ battery.\n"
            "(a) Find $C_0$ and $Q_0$. (b) Dielectric ($\\kappa = 3$) inserted while connected. "
            "Find new $C$, $Q$, $E$, $U$. (c) Energy from battery vs $\\Delta U$.\n\n"
            "### Move 1: Initial state (part a)\n"
            "$$C_0 = \\frac{(8.85\\times10^{-12})(0.05)}{2\\times10^{-3}} = 221\\;\\text{pF}$$\n"
            "$$Q_0 = C_0 V = 44.2\\;\\text{nC}, \\quad U_0 = \\frac{1}{2}C_0V^2 = 4.42\\;\\mu\\text{J}$$\n\n"
            "### Move 2: With dielectric, $V$ fixed (part b)\n"
            "$$C = 3C_0 = 663\\;\\text{pF}, \\quad Q = CV = 132.6\\;\\text{nC}$$\n"
            "$$E = V/d = 10^5\\;\\text{V/m} \\text{ (unchanged)}, \\quad "
            "U = \\frac{1}{2}CV^2 = 13.26\\;\\mu\\text{J}$$\n\n"
            "### Move 3: Battery work (part c)\n"
            "$\\Delta Q = 88.4\\;\\text{nC}$. Battery work: $W_{\\text{bat}} = V\\Delta Q = 17.68\\;\\mu\\text{J}$. "
            "$\\Delta U = 8.84\\;\\mu\\text{J}$. The remaining $8.84\\;\\mu\\text{J}$ "
            "went into dielectric polarization (and some mechanical work pulling the slab in).\n\n"
            "**Exam tip:** Always state connected vs disconnected **before** applying dielectric formulas.\n\n"
            "**Self-check:** $W_{\\text{bat}} = 2 \\times \\Delta U$ — the battery supplies twice "
            "the energy increase; half goes to stored field energy, half to dielectric polarization. "
            "This energy bookkeeping is a favorite university exam question.\n\n"
            "**Physical picture:** The dielectric is pulled into the gap by the fringe field — "
            "mechanical work plus heat account for energy not stored in the capacitor.\n\n"
            "**Answer summary:** (a) $C_0 = 221$ pF, $Q_0 = 44.2$ nC; "
            "(b) $C = 663$ pF, $Q = 132.6$ nC, $U = 13.26$ μJ; "
            "(c) battery work $W_{\\text{bat}} = 17.68$ μJ."
        ),
        "body_he_md": (
            "**נתון:** קבל לוחות מקבילים: $A = 0.05\\;\\text{m}^2$, $d = 2\\;\\text{mm}$, "
            "מחובר לסוללה $V = 200\\;\\text{V}$.\n"
            "(א) מצא $C_0$ ו-$Q_0$. (ב) דיאלקטריקה ($\\kappa = 3$) מוכנסת בזמן חיבור. "
            "מצא $C$, $Q$, $E$, $U$ חדשים. (ג) אנרגיה מהסוללה לעומת $\\Delta U$.\n\n"
            "### צעד 1: מצב התחלתי (חלק א)\n"
            "$$C_0 = \\frac{(8.85\\times10^{-12})(0.05)}{2\\times10^{-3}} = 221\\;\\text{pF}$$\n"
            "$$Q_0 = C_0 V = 44.2\\;\\text{nC}, \\quad U_0 = \\frac{1}{2}C_0V^2 = 4.42\\;\\mu\\text{J}$$\n\n"
            "### צעד 2: עם דיאלקטריקה, $V$ קבוע (חלק ב)\n"
            "$$C = 3C_0 = 663\\;\\text{pF}, \\quad Q = CV = 132.6\\;\\text{nC}$$\n"
            "$$E = V/d = 10^5\\;\\text{V/m} \\text{ (ללא שינוי)}, \\quad "
            "U = \\frac{1}{2}CV^2 = 13.26\\;\\mu\\text{J}$$\n\n"
            "### צעד 3: עבודת הסוללה (חלק ג)\n"
            "$\\Delta Q = 88.4\\;\\text{nC}$. עבודת סוללה: $W_{\\text{bat}} = V\\Delta Q = 17.68\\;\\mu\\text{J}$. "
            "$\\Delta U = 8.84\\;\\mu\\text{J}$. ה-$8.84\\;\\mu\\text{J}$ הנותרים "
            "הלכו לקיטוב הדיאלקטריקה (ועבודה מכנית במשיכת הלוח).\n\n"
            "**טיפ לבחינה:** ציינו תמיד מחובר או מנותק **לפני** יישום נוסחאות דיאלקטריקה.\n\n"
            "**בדיקה:** $W_{\\text{bat}} = 2 \\times \\Delta U$ — הסוללה מספקת פי 2 "
            "מעליית האנרגיה; חצי לשדה, חצי לקיטוב דיאלקטריקה. "
            "איזון אנרגיה זה שאלת בחינה אהובה באוניברסיטה."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "**Problem:** Capacitor stores $Q = 50\\;\\mu\\text{C}$ at $V = 25\\;\\text{V}$. "
            "Find (a) $C$ and (b) energy stored.\n\n"
            "**Step 1 — Capacitance:** From $C = Q/V$:\n"
            "$$C = \\frac{50\\times10^{-6}}{25} = 2\\times10^{-6}\\;\\text{F} = 2\\;\\mu\\text{F}$$\n\n"
            "**Step 2 — Energy:** Use $U = \\frac{1}{2}QV$ (both $Q$ and $V$ known):\n"
            "$$U = \\frac{1}{2}(50\\times10^{-6})(25) = 6.25\\times10^{-4}\\;\\text{J} = 0.625\\;\\text{mJ}$$\n\n"
            "**Verify:** $U = \\frac{1}{2}CV^2 = \\frac{1}{2}(2\\times10^{-6})(625) = 0.625\\;\\text{mJ}$ ✓\n\n"
            "**Answer:** (a) $C = 2\\;\\mu\\text{F}$; (b) $U = 0.625\\;\\text{mJ}$."
        ),
        "checkpoint_solution_he": (
            "**בעיה:** קבל מאחסן $Q = 50\\;\\mu\\text{C}$ ב-$V = 25\\;\\text{V}$. "
            "מצא (א) $C$ ו-(ב) אנרגיה מאוחסנת.\n\n"
            "**שלב 1 — קיבול:** מ-$C = Q/V$:\n"
            "$$C = \\frac{50\\times10^{-6}}{25} = 2\\times10^{-6}\\;\\text{F} = 2\\;\\mu\\text{F}$$\n\n"
            "**שלב 2 — אנרגיה:** השתמשו ב-$U = \\frac{1}{2}QV$ (שניהם ידועים):\n"
            "$$U = \\frac{1}{2}(50\\times10^{-6})(25) = 6.25\\times10^{-4}\\;\\text{J} = 0.625\\;\\text{mJ}$$\n\n"
            "**אימות:** $U = \\frac{1}{2}CV^2 = 0.625\\;\\text{mJ}$ ✓\n\n"
            "**תשובה:** (א) $C = 2\\;\\mu\\text{F}$; (ב) $U = 0.625\\;\\text{mJ}$."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "**Problem:** $4\\;\\mu\\text{F}$ capacitor charged to $V_0 = 50\\;\\text{V}$, "
            "then disconnected. Dielectric ($\\kappa = 2$) inserted. Find new $C$, $V$, $U$.\n\n"
            "**Step 1 — Charge is trapped:** $Q = C_0 V_0 = (4\\times10^{-6})(50) = 200\\;\\mu\\text{C}$ "
            "(constant after disconnect).\n\n"
            "**Step 2 — New capacitance:** $C_{\\text{new}} = \\kappa C_0 = 2 \\times 4 = 8\\;\\mu\\text{F}$.\n\n"
            "**Step 3 — New voltage:** $V_{\\text{new}} = Q/C_{\\text{new}} = 200/8 = 25\\;\\text{V}$ "
            "(halved because $C$ doubled at fixed $Q$).\n\n"
            "**Step 4 — New energy:**\n"
            "$$U_{\\text{new}} = \\frac{Q^2}{2C_{\\text{new}}} = \\frac{(200\\times10^{-6})^2}{2(8\\times10^{-6})} "
            "= 2.5\\;\\text{mJ}$$\n"
            "Initial $U_0 = \\frac{1}{2}C_0V_0^2 = 5\\;\\text{mJ}$. Energy **halved** — "
            "the \"missing\" energy went into the dielectric and any mechanical work.\n\n"
            "**Answer:** $C_{\\text{new}} = 8\\;\\mu\\text{F}$, $V_{\\text{new}} = 25\\;\\text{V}$, "
            "$U_{\\text{new}} = 2.5\\;\\text{mJ}$."
        ),
        "checkpoint_solution_he": (
            "**בעיה:** קבל $4\\;\\mu\\text{F}$ נטען ל-$V_0 = 50\\;\\text{V}$, "
            "ואז מנותק. מוכנסת דיאלקטריקה ($\\kappa = 2$). מצא $C$, $V$, $U$ חדשים.\n\n"
            "**שלב 1 — מטען לכוד:** $Q = C_0 V_0 = (4\\times10^{-6})(50) = 200\\;\\mu\\text{C}$ "
            "(קבוע אחרי ניתוק).\n\n"
            "**שלב 2 — קיבול חדש:** $C_{\\text{new}} = \\kappa C_0 = 2 \\times 4 = 8\\;\\mu\\text{F}$.\n\n"
            "**שלב 3 — מתח חדש:** $V_{\\text{new}} = Q/C_{\\text{new}} = 200/8 = 25\\;\\text{V}$ "
            "(חצי כי $C$ הוכפל ב-$Q$ קבוע).\n\n"
            "**שלב 4 — אנרגיה חדשה:**\n"
            "$$U_{\\text{new}} = \\frac{Q^2}{2C_{\\text{new}}} = 2.5\\;\\text{mJ}$$\n"
            "התחלתי $U_0 = 5\\;\\text{mJ}$. האנרגיה **חצתה** — "
            "האנרגיה \"החסרה\" הלכה לדיאלקטריקה ולעבודה מכנית.\n\n"
            "**תשובה:** $C_{\\text{new}} = 8\\;\\mu\\text{F}$, $V_{\\text{new}} = 25\\;\\text{V}$, "
            "$U_{\\text{new}} = 2.5\\;\\text{mJ}$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Scenario | What stays constant | Key relationships |\n"
            "|---|---|---|\n"
            "| Disconnected from battery | $Q = \\text{const}$ | $V = Q/C_{\\text{new}}$; $U = Q^2/(2C)$ |\n"
            "| Connected to battery | $V = \\text{const}$ | $Q = C_{\\text{new}}V$; $U = \\frac{1}{2}CV^2$ |\n"
            "| Series | Same $Q$ on each | $1/C_{\\text{eq}} = \\sum 1/C_i$; $V = \\sum V_i$ |\n"
            "| Parallel | Same $V$ on each | $C_{\\text{eq}} = \\sum C_i$; $Q = \\sum Q_i$ |\n"
            "| Dielectric inserted | $C \\to \\kappa C$ | $E \\to E/\\kappa$ if disconnected; $E$ const if connected |\n\n"
            "**Step-by-step workflow:** (1) State connected or disconnected. "
            "(2) Identify what is constant ($Q$ or $V$). (3) Apply $C_{\\text{new}} = \\kappa C_0$. "
            "(4) Compute remaining quantities. (5) Check energy with the appropriate formula.\n\n"
            "**Exam tip:** Write \"$Q$ constant\" or \"$V$ constant\" at the top of your solution — "
            "examiners award marks for identifying the case before calculating."
        ),
        "body_he_md": (
            "| תרחיש | מה נשאר קבוע | קשרים מרכזיים |\n"
            "|---|---|---|\n"
            "| מנותק מסוללה | $Q = \\text{const}$ | $V = Q/C_{\\text{חדש}}$; $U = Q^2/(2C)$ |\n"
            "| מחובר לסוללה | $V = \\text{const}$ | $Q = C_{\\text{חדש}}V$; $U = \\frac{1}{2}CV^2$ |\n"
            "| טור | אותו $Q$ על כל אחד | $1/C_{\\text{eq}} = \\sum 1/C_i$; $V = \\sum V_i$ |\n"
            "| מקביל | אותו $V$ על כל אחד | $C_{\\text{eq}} = \\sum C_i$; $Q = \\sum Q_i$ |\n"
            "| הכנסת דיאלקטריקה | $C \\to \\kappa C$ | $E \\to E/\\kappa$ אם מנותק; $E$ קבוע אם מחובר |\n\n"
            "**תהליך עבודה:** (1) ציינו מחובר או מנותק. "
            "(2) זהו מה קבוע ($Q$ או $V$). (3) יישמו $C_{\\text{חדש}} = \\kappa C_0$. "
            "(4) חשבו שאר הכמויות. (5) בדקו אנרגיה בנוסחה המתאימה.\n\n"
            "**טיפ לבחינה:** כתבו \"$Q$ קבוע\" או \"$V$ קבוע\" בראש הפתרון — "
            "מעניקים נקודות על זיהוי המקרה לפני החישוב."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Disconnected vs. connected when inserting dielectric.** "
            "If disconnected: $Q$ is constant, $V$ and $U$ decrease by $\\kappa$. "
            "If connected: $V$ is constant, $Q$ and $U$ increase by $\\kappa$. "
            "These give completely different answers — always state your assumption first.\n\n"
            "2. **Series vs. parallel rules are opposite to resistors.** "
            "Capacitors in series: $1/C_{\\text{eq}} = \\sum 1/C_i$ (like resistors in parallel). "
            "Capacitors in parallel: $C_{\\text{eq}} = \\sum C_i$ (like resistors in series). "
            "Students who memorized resistor rules alone often invert these.\n\n"
            "3. **Three energy formulas — pick the right pair.** "
            "$U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$. "
            "Use the form where you know two of $Q$, $C$, $V$. "
            "A common error is using $U = \\frac{1}{2}CV^2$ when $Q$ is constant but $C$ changed.\n\n"
            "4. **Units of $\\epsilon_0$ and geometry.** "
            "$\\epsilon_0 = 8.85\\times10^{-12}$ F/m. In $C = \\epsilon_0 A/d$, "
            "area must be m² and $d$ must be m — convert mm to m before substituting.\n\n"
            "5. **Dielectric reduces $E$ only when $Q$ is constant.** "
            "With constant $V$ (connected), $E = V/d$ stays the same; only the bound charge changes."
        ),
        "body_he_md": (
            "1. **מנותק לעומת מחובר בעת הכנסת דיאלקטריקה.** "
            "אם מנותק: $Q$ קבוע, $V$ ו-$U$ יורדים פי $\\kappa$. "
            "אם מחובר: $V$ קבוע, $Q$ ו-$U$ עולים פי $\\kappa$. "
            "תוצאות שונות לחלוטין — ציינו תמיד את ההנחה קודם.\n\n"
            "2. **כללי טור ומקביל לקבלים הפוכים מנגדים.** "
            "קבלים בטור: $1/C_{\\text{eq}} = \\sum 1/C_i$ (כמו נגדים במקביל). "
            "קבלים במקביל: $C_{\\text{eq}} = \\sum C_i$ (כמו נגדים בטור). "
            "תלמידים שזכרו רק כללי נגדים לעיתים מחליפים.\n\n"
            "3. **שלוש נוסחאות אנרגיה — בחרו את הזוג הנכון.** "
            "$U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$. "
            "השתמשו בצורה שבה ידועות שתי מ-$Q$, $C$, $V$. "
            "טעות נפוצה: $U = \\frac{1}{2}CV^2$ כש-$Q$ קבוע אך $C$ השתנה.\n\n"
            "4. **יחידות $\\epsilon_0$ וגאומטריה.** "
            "$\\epsilon_0 = 8.85\\times10^{-12}$ F/m. ב-$C = \\epsilon_0 A/d$, "
            "שטח חייב להיות m² ו-$d$ חייב m — המירו mm ל-m לפני הצבה.\n\n"
            "5. **דיאלקטריקה מקטינה $E$ רק כש-$Q$ קבוע.** "
            "עם $V$ קבוע (מחובר), $E = V/d$ נשאר; רק המטען הקשור משתנה."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Capacitors bridge electrostatics and circuits — they store energy in electric fields "
            "the same way springs store mechanical energy. Every filter in your phone, every "
            "camera flash, and every defibrillator pulse relies on rapid charge/discharge.\n\n"
            "**Why it matters for exams:** University E&M finals and advanced Bagrut questions "
            "combine capacitors with energy conservation and dielectric physics. "
            "The disconnected-vs-connected dielectric case appears in nearly every capacitor "
            "section — mastering it unlocks `concept:dc_circuits_kirchhoff` and RC transient problems.\n\n"
            "When studying, always ask: \"Is charge trapped or is voltage fixed?\" "
            "That single question determines every subsequent calculation."
        ),
        "body_he_md": (
            "קבלים מגשרים בין אלקטרוסטטיקה למעגלים — הם מאחסנים אנרגיה בשדות חשמליים "
            "כמו קפיצים שמאחסנים אנרגיה מכנית. כל מסנן בטלפון, כל פלאש מצלמה "
            "וכל פULSE דפיברילטור מסתמך על טעינה/פריקה מהירה.\n\n"
            "**למה זה חשוב לבחינות:** בחינות סופיות באוניברסיטה ובגרות מתקדמת "
            "משלבות קבלים עם שימור אנרגיה ופיזיקת דיאלקטריקה. "
            "מקרה דיאלקטריקה (מנותק לעומת מחובר) מופיע בכמעט כל פרק קבלים — "
            "שליטה בו פותחת `concept:dc_circuits_kirchhoff` ובעיות RC.\n\n"
            "בזמן לימוד, שאלו תמיד: \"האם המטען לכוד או שהמתח קבוע?\" "
            "שאלה אחת זו קובעת את כל החישובים הבאים."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Core formulas:**\n"
            "- $C = Q/V$; $C = \\epsilon_0 A/d$ (vacuum); $C = \\kappa\\epsilon_0 A/d$ (dielectric)\n"
            "- $U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$\n"
            "- Series: $1/C_{\\text{eq}} = \\sum 1/C_i$; Parallel: $C_{\\text{eq}} = \\sum C_i$\n"
            "- Energy density: $u = \\frac{1}{2}\\epsilon_0 E^2$ (vacuum)\n"
            "- Spherical: $C = 4\\pi\\epsilon_0 ab/(b-a)$; $\\epsilon_0 = 8.85\\times10^{-12}$ F/m\n\n"
            "**Exam patterns:**\n"
            "- State connected or disconnected **before** applying dielectric formulas.\n"
            "- For compound circuits, redraw with equivalent capacitors step by step.\n"
            "- Energy problems: identify whether $Q$ or $V$ is constant, then pick the right $U$ formula.\n\n"
            "**Last review:** Say each formula aloud once, then solve checkpoint 2 without looking.\n\n"
            "**Units reminder:** $\\mu\\text{F} = 10^{-6}$ F, pF $= 10^{-12}$ F, "
            "nC $= 10^{-9}$ C. Convert before substituting — never plug μF directly into "
            "formulas expecting SI farads."
        ),
        "body_he_md": (
            "**נוסחאות מרכזיות:**\n"
            "- $C = Q/V$; $C = \\epsilon_0 A/d$ (ריק); $C = \\kappa\\epsilon_0 A/d$ (דיאלקטריקה)\n"
            "- $U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$\n"
            "- טור: $1/C_{\\text{eq}} = \\sum 1/C_i$; מקביל: $C_{\\text{eq}} = \\sum C_i$\n"
            "- צפיפות אנרגיה: $u = \\frac{1}{2}\\epsilon_0 E^2$ (ריק)\n"
            "- כדורי: $C = 4\\pi\\epsilon_0 ab/(b-a)$; $\\epsilon_0 = 8.85\\times10^{-12}$ F/m\n\n"
            "**דפוסי בחינה:**\n"
            "- ציינו מחובר או מנותק **לפני** נוסחאות דיאלקטריקה.\n"
            "- לנגרים מורכבים, שרטטו מחדש עם קבלים שקולים שלב אחר שלב.\n"
            "- בעיות אנרגיה: זהו אם $Q$ או $V$ קבוע, ובחרו נוסחת $U$ מתאימה.\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint 2 בלי להסתכל."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **$C = Q/V$**; units: farads (F). Geometry determines $C$, not charge.\n"
            "- **Parallel plate:** $C = \\kappa\\epsilon_0 A/d$; dielectric increases $C$ by factor $\\kappa$.\n"
            "- **Energy:** $U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$ — pick the form matching known quantities.\n"
            "- **Series:** smaller $C_{\\text{eq}}$; same $Q$ on each; voltages add.\n"
            "- **Parallel:** larger $C_{\\text{eq}}$; same $V$ on each; charges add.\n"
            "- **Disconnected + dielectric:** $Q$ const → $V$, $E$, $U$ all decrease by $\\kappa$.\n"
            "- **Connected + dielectric:** $V$ const → $Q$, $U$ increase by $\\kappa$; $E$ unchanged."
        ),
        "body_he_md": (
            "- **$C = Q/V$**; יחידות: פאראד (F). הגאומטריה קובעת $C$, לא המטען.\n"
            "- **לוחות מקבילים:** $C = \\kappa\\epsilon_0 A/d$; דיאלקטריקה מגדילה $C$ פי $\\kappa$.\n"
            "- **אנרגיה:** $U = Q^2/(2C) = \\frac{1}{2}CV^2 = \\frac{1}{2}QV$ — בחרו צורה לפי הכמויות הידועות.\n"
            "- **טור:** $C_{\\text{eq}}$ קטן; אותו $Q$; מתחים מתחברים.\n"
            "- **מקביל:** $C_{\\text{eq}}$ גדול; אותו $V$; מטענים מתחברים.\n"
            "- **מנותק + דיאלקטריקה:** $Q$ קבוע → $V$, $E$, $U$ יורדים פי $\\kappa$.\n"
            "- **מחובר + דיאלקטריקה:** $V$ קבוע → $Q$, $U$ עולים פי $\\kappa$; $E$ ללא שינוי."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:** From the definition $C = Q/V$, rearranging gives "
            "$Q = CV$. Substituting: $Q = (20\\times10^{-6}\\;\\text{F})(15\\;\\text{V}) "
            "= 300\\times10^{-6}\\;\\text{C} = 300\\;\\mu\\text{C}$.\n\n"
            "**How to think about it:** Capacitance tells you how much charge per volt "
            "the device can hold. A 20 μF capacitor at 15 V stores 300 μC — "
            "proportional to both $C$ and $V$.\n\n"
            "**Common slip:** Forgetting to convert μF to F ($20\\;\\mu\\text{F} = 20\\times10^{-6}$ F), "
            "which gives an answer 10⁶ times too large. Another error: dividing instead of "
            "multiplying ($Q = V/C$ instead of $Q = CV$).\n\n"
            "**Exam tip:** Always write $Q = CV$ before substituting. "
            "Check units: (F)(V) = C ✓."
        ),
        "explanation_he": (
            "**למה זה נכון:** מההגדרה $C = Q/V$, נקבל $Q = CV$. הצבה: "
            "$Q = (20\\times10^{-6}\\;\\text{F})(15\\;\\text{V}) "
            "= 300\\times10^{-6}\\;\\text{C} = 300\\;\\mu\\text{C}$.\n\n"
            "**איך לחשוב:** קיבול אומר כמה מטען לוולט המכשיר יכול להחזיק. "
            "קבל 20 μF ב-15 V מאחסן 300 μC — "
            "פרופורציוני גם ל-$C$ וגם ל-$V$.\n\n"
            "**טעות נפוצה:** שכחת המרת μF ל-F ($20\\;\\mu\\text{F} = 20\\times10^{-6}$ F), "
            "מה שנותן תשובה גדולה פי 10⁶. גם חלוקה במקום כפל ($Q = V/C$).\n\n"
            "**טיפ לבחינה:** כתבו תמיד $Q = CV$ לפני הצבה. "
            "בדקו יחידות: (F)(V) = C ✓. "
            "אם קיבלתם $Q$ ביחידות שגויות, בדקו שהמרתם μF ל-F לפני הכפל."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** For capacitors in series, reciprocals add:\n"
            "$$\\frac{1}{C_{\\text{eq}}} = \\frac{1}{4} + \\frac{1}{4} = \\frac{2}{4} = \\frac{1}{2}$$\n"
            "Therefore $C_{\\text{eq}} = 2\\;\\mu\\text{F}$ — **half** either individual capacitance.\n\n"
            "**How to think about it:** Series capacitors share the same trapped charge, "
            "so each holds less charge at the same total voltage — equivalent $C$ is smaller. "
            "This is opposite to resistors in series.\n\n"
            "**Common slip:** Adding capacitances directly ($4 + 4 = 8\\;\\mu\\text{F}$) — "
            "that is the **parallel** rule. Another error: forgetting that identical capacitors "
            "in series give $C/2$, not $C$.\n\n"
            "**Exam tip:** For two equal capacitors in series, $C_{\\text{eq}} = C/2$ immediately. "
            "Memorize this shortcut to save time."
        ),
        "explanation_he": (
            "**למה זה נכון:** לקבלים בטור, ההופכים מתחברים:\n"
            "$$\\frac{1}{C_{\\text{eq}}} = \\frac{1}{4} + \\frac{1}{4} = \\frac{1}{2}$$\n"
            "לכן $C_{\\text{eq}} = 2\\;\\mu\\text{F}$ — **חצי** מכל קבל בנפרד.\n\n"
            "**איך לחשוב:** קבלים בטור חולקים אותו מטען לכוד, "
            "לכן כל אחד מחזיק פחות מטען באותו מתח כולל — $C$ שקול קטן יותר. "
            "זה הפוך מנגדים בטור.\n\n"
            "**טעות נפוצה:** חיבור ישיר ($4 + 4 = 8\\;\\mu\\text{F}$) — "
            "זה כלל **מקביל**. גם שכחה שקבלים זהים בטור נותנים $C/2$.\n\n"
            "**טיפ לבחינה:** לשני קבלים שווים בטור, $C_{\\text{eq}} = C/2$ מיד. "
            "שמרו קיצור זה לחיסכון זמן. "
            "זכרו: טור מקטין קיבול; מקביל מגדיל — הפוך מנגדים."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** When connected to a battery, voltage $V$ is fixed. "
            "Inserting dielectric increases $C$ by factor $\\kappa$. "
            "Since $Q = CV$ and both $C$ and $V$ are fixed (battery maintains $V$), "
            "charge increases: $Q_{\\text{new}} = \\kappa Q_{\\text{old}}$. Statement is **True**.\n\n"
            "**How to think about it:** The battery pushes additional charge onto the plates "
            "to maintain the same potential difference across the now-larger capacitance. "
            "More \"room\" for charge at the same voltage means more charge stored.\n\n"
            "**Common slip:** Assuming charge stays constant (that is the **disconnected** case). "
            "Students who learned only the isolated capacitor case often answer False.\n\n"
            "**Exam tip:** Underline \"connected to battery\" in every dielectric problem. "
            "That phrase alone tells you $V$ is constant and $Q$ can change."
        ),
        "explanation_he": (
            "**למה זה נכון:** כשמחובר לסוללה, מתח $V$ קבוע. "
            "הכנסת דיאלקטריקה מגדילה $C$ פי $\\kappa$. "
            "מכיוון ש-$Q = CV$ וגם $C$ וגם $V$ קבועים (הסוללה שומרת $V$), "
            "המטען עולה: $Q_{\\text{new}} = \\kappa Q_{\\text{old}}$. הטענה **נכונה**.\n\n"
            "**איך לחשוב:** הסוללה דוחפת מטען נוסף ללוחות "
            "כדי לשמור על אותו הפרש פוטנציאל על קיבול גדול יותר. "
            "יותר \"מקום\" למטען באותו מתח = יותר מטען מאוחסן.\n\n"
            "**טעות נפוצה:** הנחה שמטען נשאר קבוע (זה מקרה **מנותק**). "
            "תלמידים שלמדו רק קבל מבודד לעיתים עונים לא נכון.\n\n"
            "**טיפ לבחינה:** סמנו \"מחובר לסוללה\" בכל בעיית דיאלקטריקה. "
            "ביטוי זה אומר $V$ קבוע ו-$Q$ יכול להשתנות."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Stored energy $U = \\frac{1}{2}CV^2$. "
            "At constant $C$, energy scales as $V^2$. "
            "If $V \\to 3V$, then $U \\to \\frac{1}{2}C(3V)^2 = 9 \\cdot \\frac{1}{2}CV^2 = 9U_0$.\n\n"
            "**How to think about it:** Energy depends on the **square** of voltage, not linearly. "
            "Tripling voltage requires 9× the energy — like kinetic energy "
            "depending on $v^2$, not $v$.\n\n"
            "**Common slip:** Answering $3U_0$ (linear scaling with $V$) or $6U_0$ "
            "(confusing with $U = \\frac{1}{2}QV$ where $Q$ also triples). "
            "Another trap: using $U = Q^2/(2C)$ without recognizing $Q$ also changes.\n\n"
            "**Exam tip:** When $C$ is fixed and only $V$ changes, use $U \\propto V^2$. "
            "Write the ratio $U_{\\text{new}}/U_0 = (V_{\\text{new}}/V_0)^2$ before calculating."
        ),
        "explanation_he": (
            "**למה זה נכון:** אנרגיה מאוחסנת $U = \\frac{1}{2}CV^2$. "
            "ב-$C$ קבוע, אנרגיה תלויה ב-$V^2$. "
            "אם $V \\to 3V$, אז $U \\to \\frac{1}{2}C(3V)^2 = 9 \\cdot \\frac{1}{2}CV^2 = 9U_0$.\n\n"
            "**איך לחשוב:** אנרגיה תלויה ב**ריבוע** המתח, לא בצורה לינארית. "
            "הכפלת מתח פי 3 דורשת פי 9 אנרגיה — כמו אנרגיה קינטית "
            "שתלויה ב-$v^2$, לא ב-$v$.\n\n"
            "**טעות נפוצה:** $3U_0$ (קנה מידה לינארי עם $V$) או $6U_0$ "
            "(בלבול עם $U = \\frac{1}{2}QV$). "
            "גם שימוש ב-$U = Q^2/(2C)$ בלי לזהות ש-$Q$ גם משתנה.\n\n"
            "**טיפ לבחינה:** כש-$C$ קבוע ורק $V$ משתנה, $U \\propto V^2$. "
            "כתבו $U_{\\text{new}}/U_0 = (V_{\\text{new}}/V_0)^2$ לפני חישוב."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Charging a capacitor requires moving charge $dq$ "
            "against instantaneous voltage $v = q/C$. Work element: $dW = v\\,dq = (q/C)\\,dq$. "
            "Integrating from 0 to $Q$: $U = \\int_0^Q q/C\\,dq = Q^2/(2C)$. "
            "Substituting $Q = CV$ gives $\\frac{1}{2}CV^2$; substituting $V = Q/C$ gives $\\frac{1}{2}QV$.\n\n"
            "**How to think about it:** This is the same logic as compressing a spring — "
            "each incremental bit of charge faces increasing opposition. "
            "The factor $\\frac{1}{2}$ arises from the linear rise of voltage during charging.\n\n"
            "**Common slip:** Missing the $\\frac{1}{2}$ (getting $U = QV$ instead of $\\frac{1}{2}QV$), "
            "or deriving only one form without showing algebraic equivalence.\n\n"
            "**Exam tip:** Start every energy derivation from $dW = V\\,dQ$. "
            "Examiners reward the integral setup even if final algebra has minor errors."
        ),
        "explanation_he": (
            "**למה זה נכון:** טעינת קבל דורשת העברת $dq$ "
            "נגד מתח רגעי $v = q/C$. אלמנט עבודה: $dW = v\\,dq = (q/C)\\,dq$. "
            "אינטגרציה מ-0 עד $Q$: $U = \\int_0^Q q/C\\,dq = Q^2/(2C)$. "
            "הצבת $Q = CV$ נותנת $\\frac{1}{2}CV^2$; הצבת $V = Q/C$ נותנת $\\frac{1}{2}QV$.\n\n"
            "**איך לחשוב:** אותה לוגיקה כדחיסת קפיץ — "
            "כל חלקיק מטען נוסף מתמודד עם התנגדות גוברת. "
            "הגורם $\\frac{1}{2}$ נובע מהעלייה הלינארית של המתח בזמן טעינה.\n\n"
            "**טעות נפוצה:** חסר $\\frac{1}{2}$ (קבלת $U = QV$), "
            "או גזירה של צורה אחת בלבד בלי להראות שקivalence אלגברית.\n\n"
            "**טיפ לבחינה:** התחילו כל גזירת אנרגיה מ-$dW = V\\,dQ$. "
            "מעניקים נקודות על הגדרת האינטגרל גם אם האלגebra הסופית לא מושלמת."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Parallel-plate capacitance in vacuum: $C = \\epsilon_0 A/d$.\n"
            "$$C = \\frac{(8.85\\times10^{-12})(0.1)}{5\\times10^{-3}} "
            "= \\frac{8.85\\times10^{-13}}{5\\times10^{-3}} = 1.77\\times10^{-10}\\;\\text{F} = 177\\;\\text{pF}$$\n\n"
            "**How to think about it:** Larger plate area increases capacitance; "
            "larger separation decreases it. Here $A = 0.1$ m² is moderately large "
            "and $d = 5$ mm gives a typical lab-scale value in the pF range.\n\n"
            "**Common slip:** Using $d = 5$ instead of $5\\times10^{-3}$ m (1000× error), "
            "or using $\\kappa\\epsilon_0$ when no dielectric is mentioned (vacuum assumed).\n\n"
            "**Exam tip:** Write $\\epsilon_0 = 8.85\\times10^{-12}$ F/m explicitly. "
            "Expect pF or nF for centimeter-scale plates — if you get F or mF, recheck units."
        ),
        "explanation_he": (
            "**למה זה נכון:** קיבול לוחות מקבילים בריק: $C = \\epsilon_0 A/d$.\n"
            "$$C = \\frac{(8.85\\times10^{-12})(0.1)}{5\\times10^{-3}} "
            "= 1.77\\times10^{-10}\\;\\text{F} = 177\\;\\text{pF}$$\n\n"
            "**איך לחשוב:** שטח לוח גדול יותר מגדיל קיבול; "
            "ריווח גדול יותר מקטין. כאן $A = 0.1$ m² בינוני "
            "ו-$d = 5$ mm נותן ערך טיפוסי במעבדה בטווח pF.\n\n"
            "**טעות נפוצה:** שימוש ב-$d = 5$ במקום $5\\times10^{-3}$ m (טעות פי 1000), "
            "או $\\kappa\\epsilon_0$ כשלא צוינה דיאלקטריקה (מניחים ריק).\n\n"
            "**טיפ לבחינה:** כתבו $\\epsilon_0 = 8.85\\times10^{-12}$ F/m במפורש. "
            "צפו ל-pF או nF ללוחות בס\"מ — אם קיבלתם F או mF, בדקו יחידות. "
            "המרת mm ל-m לפני הצבה היא השלב הקריטי ביותר בבעיות לוחות מקבילים."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Charge: $Q = CV = (10\\times10^{-6})(30) = 300\\;\\mu\\text{C}$.\n"
            "Energy: $U = \\frac{1}{2}CV^2 = \\frac{1}{2}(10\\times10^{-6})(900) = 4.5\\times10^{-3}\\;\\text{J} = 4.5\\;\\text{mJ}$.\n\n"
            "**How to think about it:** This is a two-step problem: first find charge from "
            "$Q = CV$, then energy from $U = \\frac{1}{2}CV^2$ (or equivalently $U = \\frac{1}{2}QV$). "
            "Both answers use the same $C$ and $V$ — verify with $U = \\frac{1}{2}QV = 4.5$ mJ.\n\n"
            "**Common slip:** Using $U = CV^2$ without the $\\frac{1}{2}$, giving 9 mJ. "
            "Another error: reporting energy in μJ instead of mJ.\n\n"
            "**Exam tip:** After computing $Q$ and $U$, cross-check with $U = \\frac{1}{2}QV$. "
            "All three energy formulas must agree when $C$, $Q$, $V$ are consistent."
        ),
        "explanation_he": (
            "**למה זה נכון:** מטען: $Q = CV = (10\\times10^{-6})(30) = 300\\;\\mu\\text{C}$.\n"
            "אנרגיה: $U = \\frac{1}{2}CV^2 = \\frac{1}{2}(10\\times10^{-6})(900) = 4.5\\;\\text{mJ}$.\n\n"
            "**איך לחשוב:** בעיה בשני שלבים: קודם מטען מ-$Q = CV$, "
            "אחר כך אנרגיה מ-$U = \\frac{1}{2}CV^2$ (או $U = \\frac{1}{2}QV$). "
            "שתי התשובות משתמשות באותם $C$ ו-$V$ — אמתו עם $U = \\frac{1}{2}QV = 4.5$ mJ.\n\n"
            "**טעות נפוצה:** $U = CV^2$ בלי $\\frac{1}{2}$, קבלת 9 mJ. "
            "גם דיווח אנרגיה ב-μJ במקום mJ.\n\n"
            "**טיפ לבחינה:** אחרי חישוב $Q$ ו-$U$, בדקו עם $U = \\frac{1}{2}QV$. "
            "כל שלוש נוסחאות האנרגיה חייבות להתאים. "
            "שאלות דו-חלקיות נפוצות בבחינות — אל תדלגו על חישוב המטען לפני האנרגיה."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** With dielectric filling the gap: $C = \\kappa\\epsilon_0 A/d$.\n"
            "$$C = \\frac{(4)(8.85\\times10^{-12})(0.01)}{0.5\\times10^{-3}} "
            "= \\frac{3.54\\times10^{-13}}{5\\times10^{-4}} = 7.08\\times10^{-10}\\;\\text{F} = 708\\;\\text{pF}$$\n\n"
            "**How to think about it:** Dielectric constant $\\kappa = 4$ quadruples the vacuum "
            "capacitance. Vacuum value would be $177$ pF; multiplied by 4 gives $708$ pF.\n\n"
            "**Common slip:** Forgetting $\\kappa$ (getting 177 pF — the vacuum answer), "
            "or using $d = 0.5$ mm without converting to $0.5\\times10^{-3}$ m.\n\n"
            "**Exam tip:** When $\\kappa$ is given, always use $C = \\kappa\\epsilon_0 A/d$. "
            "Quick check: $C_{\\text{diel}} = \\kappa \\cdot C_{\\text{vacuum}}$. "
            "If your answer is not $\\kappa$ times the vacuum value, recheck."
        ),
        "explanation_he": (
            "**למה זה נכון:** עם דיאלקטריקה שממלאת את הסדק: $C = \\kappa\\epsilon_0 A/d$.\n"
            "$$C = \\frac{(4)(8.85\\times10^{-12})(0.01)}{0.5\\times10^{-3}} "
            "= 7.08\\times10^{-10}\\;\\text{F} = 708\\;\\text{pF}$$\n\n"
            "**איך לחשוב:** קבוע דיאלקטרי $\\kappa = 4$ מכפיל פי 4 את קיבול הריק. "
            "ערך ריק היה $177$ pF; כפול 4 נותן $708$ pF.\n\n"
            "**טעות נפוצה:** שכחת $\\kappa$ (קבלת 177 pF — תשובת הריק), "
            "או $d = 0.5$ mm בלי המרה ל-$0.5\\times10^{-3}$ m.\n\n"
            "**טיפ לבחינה:** כש-$\\kappa$ נתון, תמיד $C = \\kappa\\epsilon_0 A/d$. "
            "בדיקה מהירה: $C_{\\text{דיאל}} = \\kappa \\cdot C_{\\text{ריק}}$. "
            "אם התשובה לא פי $\\kappa$ מערך הריק, בדקו המרת mm ל-m ו-$\\kappa$. "
            "חשבו קודם $C_{\\text{ריק}}$ ואז הכפילו ב-$\\kappa$ — זה מהיר יותר."
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
        print("Validation issues:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        sys.exit(1)

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
