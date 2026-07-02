#!/usr/bin/env python3
"""Expand maxwell_equations.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/maxwell_equations.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "worked_example": {"en": 130, "he": 110},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
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
            "In 1865, James Clerk Maxwell unified electricity and magnetism into four compact "
            "equations — the most complete description of classical electromagnetism ever written. "
            "Together with the Lorentz force law, they explain everything from static charges and "
            "steady currents to radio waves, visible light, and X-rays.\n\n"
            "Before Maxwell, Ampère's law worked for steady currents but failed for a charging "
            "capacitor. Maxwell's **displacement current** fixed that inconsistency — and, "
            "unexpectedly, predicted that light is an electromagnetic wave travelling at "
            "$c = 1/\\sqrt{\\mu_0\\epsilon_0}$.\n\n"
            "**University exam topics:**\n"
            "- State all four equations (integral and differential form)\n"
            "- Identify which equation applies to a given physical situation\n"
            "- Calculate displacement current in a charging capacitor\n"
            "- Derive the EM wave speed from Faraday + Ampère-Maxwell\n\n"
            "This lesson builds on `concept:faraday_induction`, `concept:ampere_law`, and "
            "`concept:gauss_law`. Master the **physical meaning** of each equation before "
            "memorising symbols — examiners reward conceptual understanding over rote recall."
        ),
        "body_he_md": (
            "בשנת 1865, ג'יימס קlerk מקסוול איחד חשמל ומגנטיות לארבע משוואות קומpactיות — "
            "התיאור המלא ביותר של אלקטרומגנטיות קלאסית שנכתב אי פעם. יחד עם חוק הכוח של "
            "לורנץ, הן מסבירות הכל ממטענים סטטיים וזרמים יציבים ועד גלי רדיו, אור נראה "
            "וקרני רנטgen.\n\n"
            "לפני מקסוול, חוק אמפר עבד לזרמים יציבים אך נכשל בקבל נטען. **זרם התזוזה** "
            "של מקסוול תיקן את חוסר העקביות — ובאופן בלתי צפוי חזה שאור הוא גל "
            "אלקטרומגנטי הנע במהירות $c = 1/\\sqrt{\\mu_0\\epsilon_0}$.\n\n"
            "**נושאי בחינה באוניברסיטה:**\n"
            "- ניסוח ארבע המשוואות (צורה אינטגרלית ודיפרנציאלית)\n"
            "- זיהוי איזו משוואה מתאימה לסיטואציה פיזיקלית\n"
            "- חישוב זרם תזוזה בקבל נטען\n"
            "- גזירת מהירות גל EM מפאראדי + אמפר-מקסוול\n\n"
            "שיעור זה נשען על `concept:faraday_induction`, `concept:ampere_law` ו-"
            "`concept:gauss_law`. שלטו ב**משמעות הפיזיקלית** של כל משוואה לפני שינון "
            "סמלים — בוחנים מעריכים הבנה מושגית על פני שינון מכני."
        ),
    },
    "definition": {
        "body_en_md": (
            "Maxwell's four equations in **integral form** relate fields to their sources "
            "over closed surfaces or loops:\n\n"
            "**I. Gauss's Law for $\\vec{E}$** — electric charges create electric field lines:\n"
            "$$\\oint \\vec{E}\\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\n\n"
            "**II. Gauss's Law for $\\vec{B}$** — no magnetic monopoles exist:\n"
            "$$\\oint \\vec{B}\\cdot d\\vec{A} = 0$$\n\n"
            "**III. Faraday's Law** — a changing magnetic flux induces an EMF (circulating $\\vec{E}$):\n"
            "$$\\oint \\vec{E}\\cdot d\\vec{\\ell} = -\\frac{d\\Phi_B}{dt}$$\n\n"
            "**IV. Ampère-Maxwell Law** — conduction currents **and** changing electric flux create "
            "circulating $\\vec{B}$:\n"
            "$$\\oint \\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I_{\\text{enc}} + \\mu_0\\epsilon_0\\frac{d\\Phi_E}{dt}$$\n\n"
            "The term $\\mu_0\\epsilon_0\\, d\\Phi_E/dt$ is Maxwell's **displacement current**. "
            "It is not a flow of charge — it is the rate of change of electric flux through the "
            "Ampèrian surface. In vacuum, $\\epsilon_0 = 8.85\\times10^{-12}$ F/m and "
            "$\\mu_0 = 4\\pi\\times10^{-7}$ T·m/A. These four equations, plus "
            "$\\vec{F} = q(\\vec{E} + \\vec{v}\\times\\vec{B})$, fully describe classical EM.\n\n"
            "**How to read the integral form:** $\\oint$ means integrate over a **closed** path or surface. "
            "$Q_{\\text{enc}}$ and $I_{\\text{enc}}$ are the charge and current passing through any surface "
            "bounded by the loop. The differential forms (using $\\nabla\\cdot$ and $\\nabla\\times$) "
            "apply point-by-point and are equivalent — use whichever form matches the problem symmetry."
        ),
        "body_he_md": (
            "ארבע משוואות מקסוול ב**צורה אינטגרלית** קושרות שדות למקורותיהם על משטחים "
            "או לולאות סגuroות:\n\n"
            "**I. חוק גאוס ל-$\\vec{E}$** — מטענים חשמליים יוצרים קווי שדה חשמלי:\n"
            "$$\\oint \\vec{E}\\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\n\n"
            "**II. חוק גאוס ל-$\\vec{B}$** — אין מונופולים מגנטיים:\n"
            "$$\\oint \\vec{B}\\cdot d\\vec{A} = 0$$\n\n"
            "**III. חוק פאראדי** — שטף מגנטי משתנה מושרה כ\"א (שדה $\\vec{E}$ מסתובב):\n"
            "$$\\oint \\vec{E}\\cdot d\\vec{\\ell} = -\\frac{d\\Phi_B}{dt}$$\n\n"
            "**IV. חוק אמפר-מקסוול** — זרמי הולכה **וגם** שטף חשמלי משתנה יוצרים "
            "$\\vec{B}$ מסתובב:\n"
            "$$\\oint \\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I_{\\text{enc}} + \\mu_0\\epsilon_0\\frac{d\\Phi_E}{dt}$$\n\n"
            "האיבר $\\mu_0\\epsilon_0\\, d\\Phi_E/dt$ הוא **זרם התזוזה** של מקסוול. "
            "זה לא זרימת מטען — זה קצב שינוי השטף החשמלי דרך משטח האמפר. "
            "בריק, $\\epsilon_0 = 8.85\\times10^{-12}$ F/m ו-$\\mu_0 = 4\\pi\\times10^{-7}$ T·m/A. "
            "ארבע משוואות אלו, יחד עם $\\vec{F} = q(\\vec{E} + \\vec{v}\\times\\vec{B})$, "
            "מתארות במלואן EM קלאסי.\n\n"
            "**איך לקרוא את הצורה האינטegralית:** $\\oint$ פירושו אינטegral על מסלול או משטח **סגור**. "
            "$Q_{\\text{enc}}$ ו-$I_{\\text{enc}}$ הם המטען והזרם שחוצים כל משטח "
            "הגבול בלולאה. הצורות הדיפרנציאליות (עם $\\nabla\\cdot$ ו-$\\nabla\\times$) "
            "חלות נקודה-נקודה ושקולות — השתמשו בצורה שמתאימה לסימטריה."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Summary table\n"
            "| Equation | Physical meaning |\n"
            "|---|---|\n"
            "| Gauss for E | Electric charges are sources/sinks of $\\vec{E}$ field lines |\n"
            "| Gauss for B | Magnetic field lines always form closed loops (no monopoles) |\n"
            "| Faraday | A changing $\\vec{B}$ drives an EMF (induces circulating $\\vec{E}$) |\n"
            "| Ampère-Maxwell | Conduction currents AND changing $\\vec{E}$ create circulating $\\vec{B}$ |\n\n"
            "### Displacement current in a capacitor\n"
            "When charging a parallel-plate capacitor, real current $I$ flows in the wire but stops "
            "between the plates. Yet the electric field between the plates grows: "
            "$E = Q/(\\epsilon_0 A)$, so $dE/dt = I/(\\epsilon_0 A)$. "
            "Maxwell identified $I_d = \\epsilon_0\\, d\\Phi_E/dt = \\epsilon_0 A\\, dE/dt = I$ — "
            "exactly equal to the wire current. This maintains continuity of $\\oint\\vec{B}\\cdot d\\vec{\\ell}$ "
            "regardless of which surface you choose bounded by the same Ampèrian loop.\n\n"
            "### Differential form in vacuum\n"
            "$\\nabla\\cdot\\vec{E} = \\rho/\\epsilon_0$; $\\nabla\\cdot\\vec{B} = 0$; "
            "$\\nabla\\times\\vec{E} = -\\partial\\vec{B}/\\partial t$; "
            "$\\nabla\\times\\vec{B} = \\mu_0\\vec{J} + \\mu_0\\epsilon_0\\partial\\vec{E}/\\partial t$.\n\n"
            "### Speed of light\n"
            "Combining Faraday (III) and Ampère-Maxwell (IV) in a charge-free region yields the wave equation "
            "$\\nabla^2\\vec{E} = \\mu_0\\epsilon_0\\partial^2\\vec{E}/\\partial t^2$, giving:\n"
            "$$c = \\frac{1}{\\sqrt{\\mu_0\\epsilon_0}} = \\frac{1}{\\sqrt{(4\\pi\\times10^{-7})(8.85\\times10^{-12})}} "
            "\\approx 3\\times10^8\\;\\text{m/s}$$\n"
            "Maxwell recognised this matched the measured speed of light — the first proof that light is an EM wave."
        ),
        "body_he_md": (
            "### טבלת סיכום\n"
            "| משוואה | משמעות פיזיקלית |\n"
            "|---|---|\n"
            "| גאוס E | מטענים חשמליים הם מקורות/שקעים לקווי $\\vec{E}$ |\n"
            "| גאוס B | קווי $\\vec{B}$ תמיד יוצרים לולאות סגuroות (אין מונופולים) |\n"
            "| פאראדי | $\\vec{B}$ משתנה מושרה כ\"א (יוצר $\\vec{E}$ מסתובב) |\n"
            "| אמפר-מקסוול | זרמי הולכה **וגם** $\\vec{E}$ משתנה יוצרים $\\vec{B}$ מסתובב |\n\n"
            "### זרם תזוזה בקבל\n"
            "בזמן טעינת קבל, זרם $I$ אמיתי זורם בחוט אך נעצר בין הלוחות. "
            "עם זאת השדה החשמלי בין הלוחות גדל: $E = Q/(\\epsilon_0 A)$, "
            "ולכן $dE/dt = I/(\\epsilon_0 A)$. מקסוול זיהה "
            "$I_d = \\epsilon_0\\, d\\Phi_E/dt = \\epsilon_0 A\\, dE/dt = I$ — "
            "בדיוק שווה לזרם בחוט. זה שומר על רציפות $\\oint\\vec{B}\\cdot d\\vec{\\ell}$ "
            "ללא קשר לאיזה משטח בוחרים.\n\n"
            "### צורה דיפרנציאלית בריק\n"
            "$\\nabla\\cdot\\vec{E} = \\rho/\\epsilon_0$; $\\nabla\\cdot\\vec{B} = 0$; "
            "$\\nabla\\times\\vec{E} = -\\partial\\vec{B}/\\partial t$; "
            "$\\nabla\\times\\vec{B} = \\mu_0\\vec{J} + \\mu_0\\epsilon_0\\partial\\vec{E}/\\partial t$.\n\n"
            "### מהירות האור\n"
            "שילוב פאראדי (III) ואמפר-מקסוול (IV) באזור ללא מטענים נותן משוואת גל "
            "$\\nabla^2\\vec{E} = \\mu_0\\epsilon_0\\partial^2\\vec{E}/\\partial t^2$, ומכאן:\n"
            "$$c = \\frac{1}{\\sqrt{\\mu_0\\epsilon_0}} \\approx 3\\times10^8\\;\\text{m/s}$$\n"
            "מקסוול זיהה שזה תואם למהירות האור הנמדדת — ההוכחה הראשונה שאור הוא גל EM."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** Identify which of Maxwell's equations to use for each scenario:\n"
            "(a) Finding $\\vec{E}$ outside a uniformly charged sphere.\n"
            "(b) Showing that magnetic field lines never start or end.\n"
            "(c) Calculating the induced EMF in a rotating loop.\n"
            "(d) Finding $\\vec{B}$ around a current-carrying wire.\n\n"
            "### Move 1 — Match scenario to source type\n"
            "Ask: **What is changing or present?** Charges → Gauss E. No magnetic monopoles → Gauss B. "
            "Changing flux → Faraday. Currents or changing E → Ampère-Maxwell.\n\n"
            "### Move 2 — Apply to each part\n"
            "**(a)** Gauss's law for E: high spherical symmetry lets you pull $E$ out of "
            "$\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$.\n"
            "**(b)** Gauss's law for B: $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ for **any** closed surface — "
            "net magnetic flux is always zero.\n"
            "**(c)** Faraday's law: $\\mathcal{E} = -d\\Phi_B/dt$ when flux through the loop changes.\n"
            "**(d)** Ampère-Maxwell with only the conduction term (steady current, $\\partial E/\\partial t = 0$): "
            "$\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I_{\\text{enc}}$.\n\n"
            "**Exam tip:** If a charging capacitor appears, you need the full Ampère-Maxwell law including "
            "displacement current — plain Ampère's law gives contradictory results.\n\n"
            "**Strategy summary:** Read each scenario for **sources** (charges, currents) and "
            "**changes** (flux varying with time). Static charge distributions always point to Gauss for E. "
            "Any argument about magnetic field lines starting or ending points to Gauss for B. "
            "Rotating loops, moving magnets, or changing flux always require Faraday.\n\n"
            "**Part (e) preview:** If the scenario involves a **charging capacitor**, "
            "always include displacement current in Ampère-Maxwell — never use plain Ampère alone."
        ),
        "body_he_md": (
            "**נתון:** זהו איזו ממשוואות מקסוול להשתמש בכל תרחיש:\n"
            "(א) מציאת $\\vec{E}$ מחוץ לכדור טעון אחיד.\n"
            "(ב) הוכחה שקווי שדה מגנטי לא מתחילים ולא נגמרים.\n"
            "(ג) חישוב כ\"א מושרה בלולאה מסתובבת.\n"
            "(ד) מציאת $\\vec{B}$ סביב חוט נושא זרם.\n\n"
            "### צעד 1 — התאמת תרחיש לסוג מקור\n"
            "שאלו: **מה משתנה או קיים?** מטענים → גאוס E. אין מונופולים מגנטיים → גאוס B. "
            "שטף משתנה → פאראדי. זרמים או E משתנה → אמפר-מקסוול.\n\n"
            "### צעד 2 — יישום לכל חלק\n"
            "**(א)** חוק גאוס ל-E: סימטריה כדורית מאפשרת לחלץ $E$ מ-"
            "$\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$.\n"
            "**(ב)** חוק גאוס ל-B: $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ לכל משטח סגור — "
            "שטף מגנטי נטו תמיד אפס.\n"
            "**(ג)** חוק פאראדי: $\\mathcal{E} = -d\\Phi_B/dt$ כשהשטף דרך הלולאה משתנה.\n"
            "**(ד)** אמפר-מקסוול עם איבר הולכה בלבד (זרם יציב, $\\partial E/\\partial t = 0$): "
            "$\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I_{\\text{enc}}$.\n\n"
            "**טיפ לבחינה:** אם מופיע קבל נטען, צריך את חוק אמפר-מקסוול המלא כולל זרם תזוזה — "
            "חוק אמפר הרגיל נותן תוצאות סותרות.\n\n"
            "**סיכום אסטרטגיה:** קראו כל תרחיש ל**מקורות** (מטענים, זרמים) ו**שינויים** "
            "(שטף משתנה בזמן). פילוגי מטען סטטיים תמיד מצביעים על גאוס ל-E. "
            "כל טיעון על קווי שדה מגנטי שמתחילים או נגמרים מצביע על גאוס ל-B. "
            "לולאות מסתובבות, מagnets נעים או שטף משתנה תמיד דורשים פאראדי.\n\n"
            "**הערה:** אם התרחיש כולל **קבל נטען**, "
            "כללו תמיד זרם תזוזה באמפר-מקסוול — לעולם לא אמפר בלבד."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "**Step 1:** Displacement current between parallel plates: "
            "$I_d = \\epsilon_0 A\\, dE/dt$.\n\n"
            "**Step 2:** Substitute values:\n"
            "$I_d = (8.85\\times10^{-12})(10^{-3})(3\\times10^{11}) = "
            "8.85\\times10^{-12}\\times3\\times10^8 = 2.655\\times10^{-3}\\;\\text{A}$.\n\n"
            "**Answer:** $I_d \\approx 2.65\\;\\text{mA}$.\n\n"
            "**Check:** Units: (F/m)(m²)(V/(m·s)) = A ✓. The displacement current equals the "
            "charging current in the wire — this is exactly what Maxwell's addition guarantees."
        ),
        "checkpoint_solution_he": (
            "**שלב 1:** זרם תזוזה בין לוחות מקבילים: $I_d = \\epsilon_0 A\\, dE/dt$.\n\n"
            "**שלב 2:** הצבת ערכים:\n"
            "$I_d = (8.85\\times10^{-12})(10^{-3})(3\\times10^{11}) = "
            "2.655\\times10^{-3}\\;\\text{A}$.\n\n"
            "**תשובה:** $I_d \\approx 2.65\\;\\text{mA}$.\n\n"
            "**בדיקה:** יחידות: (F/m)(m²)(V/(m·s)) = A ✓. זרם התזוזה שווה לזרם הטעינה "
            "בחוט — בדיוק מה שתוספת מקסוול מבטיחה."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A magnetic dipole (bar magnet) produces a non-uniform field. Explain why "
            "the total flux through any closed surface surrounding the magnet is zero, even though "
            "the field is non-uniform.\n\n"
            "### Move 1 — State Gauss's law for B\n"
            "$$\\oint\\vec{B}\\cdot d\\vec{A} = 0$$\n"
            "This holds for **any** closed surface, everywhere in space — not just symmetric ones.\n\n"
            "### Move 2 — Physical picture\n"
            "Magnetic field lines have no starting or ending points because there are no magnetic "
            "monopoles. Every field line that exits the closed surface must curve back and re-enter it. "
            "The outward flux through one patch exactly cancels the inward flux through another patch. "
            "This remains true even when the field is stronger near the north pole — "
            "only the net flux vanishes, not the local field magnitude.\n\n"
            "### Move 3 — Contrast with electric flux\n"
            "For electric flux: $\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0 \\neq 0$ "
            "when charges are enclosed — charges act as sources/sinks. No such source exists for "
            "$\\vec{B}$, so the net flux is always zero.\n\n"
            "**Exam tip:** Non-uniformity of $\\vec{B}$ does **not** change the zero-flux conclusion. "
            "Only enclosed magnetic charge (which does not exist) would give non-zero flux.\n\n"
            "**Key insight for exams:** Students often try to compute the flux integral directly "
            "for a bar magnet. Instead, cite Gauss for B and argue from the no-monopole principle — "
            "no calculation is needed.\n\n"
            "**Bagrut/university link:** This argument appears frequently as a short-answer "
            "question worth 5–8 points — practice stating Gauss for B first, then the "
            "no-monopole picture, then the contrast with electric flux."
        ),
        "body_he_md": (
            "**נתון:** דיפול מגנטי (מגנט) יוצר שדה לא אחיד. הסבר מדוע השטף הכולל דרך כל "
            "משטח סגור סביב המגנט הוא אפס, למרות שהשדה לא אחיד.\n\n"
            "### צעד 1 — ניסוח חוק גאוס ל-B\n"
            "$$\\oint\\vec{B}\\cdot d\\vec{A} = 0$$\n"
            "זה נכון ל**כל** משטח סגור, בכל מקום במרחב — לא רק למשטחים סימטריים.\n\n"
            "### צעד 2 — תמונה פיזיקלית\n"
            "קווי שדה מגנטי אין להם נקודות התחלה או סיום כי אין מונופולים מגנטיים. "
            "כל קו שדה שיוצא מהמשטח הסגור חייב להתעקel ולחזור אליו. "
            "השטף החוצה דרך אזור אחד מתבטל בדיוק עם השטף הפנימה דרך אזור אחר. "
            "זה נכון גם כשהשדה חזק יותר ליד הקוטb הצפוני — רק השטף הנטו מתאפס, לא גודל השדה המקומי.\n\n"
            "### צעד 3 — השוואה לשטף חשמלי\n"
            "לשטף חשמלי: $\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0 \\neq 0$ "
            "כשיש מטענים כלואים — מטענים פועלים כמקורות/שקעים. "
            "אין מקור כזה ל-$\\vec{B}$, ולכן השטף הנטו תמיד אפס.\n\n"
            "**טיפ לבחינה:** אי-אחידות של $\\vec{B}$ **לא** משנה את מסקנת שטף אפס. "
            "רק מטען מגנטי כלוא (שאינו קיים) היה נותן שטף שונה מאפס.\n\n"
            "**תובנה לבחינה:** תלמידים מנסים לעיתים לחשב את אינטegral השטף ישירות "
            "למגנט. במקום זאת, צטטו גאוס ל-B וטענו מעקר אין-מונופול — "
            "אין צורך בחישוב.\n\n"
            "**קישור לבגרות/אוניברסיטה:** טיעון זה מופיע לעיתים קרובות כשאלת תשובה קצרה "
            "שווה 5–8 נקודות — תרגלו לנסח קודם גאוס ל-B, אחר כך תמונת אין-מונופול, "
            "ואז השוואה לשטף חשמלי."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "Without the displacement current term, Ampère's law gives a **contradiction** for a "
            "charging capacitor: the line integral $\\oint\\vec{B}\\cdot d\\vec{\\ell}$ around a loop "
            "encircling the wire equals $\\mu_0 I$ if you choose a flat surface cutting the wire, "
            "but equals **zero** if you choose a surface passing between the capacitor plates "
            "(no conduction current there).\n\n"
            "Maxwell added $\\mu_0\\epsilon_0\\, d\\Phi_E/dt$, which equals $\\mu_0 I_d = \\mu_0 I$ "
            "between the plates. Both surfaces now agree.\n\n"
            "More profoundly, this means a **changing electric field creates a magnetic field** — "
            "the mirror image of Faraday's law (changing B creates E). This symmetry allows "
            "self-sustaining EM waves to propagate in vacuum."
        ),
        "checkpoint_solution_he": (
            "ללא איבר זרם התזוזה, חוק אמפר נותן **סתירה** לקבל נטען: "
            "האינטegral הקווי $\\oint\\vec{B}\\cdot d\\vec{\\ell}$ סביב לולאה שעוטפת את החוט "
            "שווה $\\mu_0 I$ אם בוחרים משטח שחותך את החוט, אך שווה **אפס** אם בוחרים משטח "
            "שעובר בין לוחות הקבל (אין שם זרם הולכה).\n\n"
            "מקסוול הוסיף $\\mu_0\\epsilon_0\\, d\\Phi_E/dt$, ששווה $\\mu_0 I_d = \\mu_0 I$ "
            "בין הלוחות. שני המשטחים מסכימים כעת.\n\n"
            "בעומק, זה אומר ש**שדה חשמלי משתנה יוצר שדה מגנטי** — "
            "המראה של חוק פאראדי (B משתנה יוצר E). "
            "סימטריה זו מאפשרת לגלי EM להתפשט בצורה עצמאית בריק."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Objective:** Show that Maxwell's equations predict EM waves with speed "
            "$c = 1/\\sqrt{\\mu_0\\epsilon_0}$.\n\n"
            "### Move 1 — Differential forms in vacuum (no charges, no currents)\n"
            "In a charge-free region, only equations III and IV couple $\\vec{E}$ and $\\vec{B}$. "
            "With no free charges or currents, $\\nabla\\cdot\\vec{E}=0$ and $\\vec{J}=0$.\n"
            "$$\\nabla\\times\\vec{E} = -\\frac{\\partial\\vec{B}}{\\partial t} \\quad \\text{(Faraday)}$$\n"
            "$$\\nabla\\times\\vec{B} = \\mu_0\\epsilon_0\\frac{\\partial\\vec{E}}{\\partial t} "
            "\\quad \\text{(Ampère-Maxwell)}$$\n\n"
            "### Move 2 — Take curl of Faraday, substitute Ampère-Maxwell\n"
            "$$\\nabla\\times(\\nabla\\times\\vec{E}) = "
            "-\\frac{\\partial}{\\partial t}(\\nabla\\times\\vec{B}) = "
            "-\\mu_0\\epsilon_0\\frac{\\partial^2\\vec{E}}{\\partial t^2}$$\n\n"
            "### Move 3 — Vector identity + Gauss for E ($\\nabla\\cdot\\vec{E}=0$ in vacuum)\n"
            "$$\\nabla\\times(\\nabla\\times\\vec{E}) = \\nabla(\\nabla\\cdot\\vec{E}) - \\nabla^2\\vec{E} "
            "= -\\nabla^2\\vec{E}$$\n"
            "So: $\\nabla^2\\vec{E} = \\mu_0\\epsilon_0\\partial^2\\vec{E}/\\partial t^2$.\n\n"
            "### Move 4 — Compare to standard wave equation $\\nabla^2 f = (1/v^2)\\partial^2 f/\\partial t^2$\n"
            "$$v^2 = \\frac{1}{\\mu_0\\epsilon_0} \\Rightarrow \\boxed{c = \\frac{1}{\\sqrt{\\mu_0\\epsilon_0}} "
            "\\approx 3\\times10^8\\;\\text{m/s}}$$\n\n"
            "Numerically this matches the measured speed of light — Maxwell's greatest prediction.\n\n"
            "**Physical interpretation:** The derivation requires a charge-free, current-free region "
            "where only the coupled Faraday and Ampère-Maxwell equations operate. The electric and "
            "magnetic fields oscillate together, each sustaining the other — exactly the mechanism "
            "of a self-propagating electromagnetic wave.\n\n"
            "**Exam strategy:** You do not need to reproduce every vector identity on an exam, "
            "but you must know the final result $c = 1/\\sqrt{\\mu_0\\epsilon_0}$ and be able to "
            "state which two Maxwell equations you combined. The same derivation works for "
            "$\\vec{B}$, giving an identical wave speed — confirming E and B waves travel together."
        ),
        "body_he_md": (
            "**מטרה:** הראה שמשוואות מקסוול מנבאות גלי EM במהירות $c = 1/\\sqrt{\\mu_0\\epsilon_0}$.\n\n"
            "### צעד 1 — צורות דיפרנציאליות בריק (ללא מטענים, ללא זרמים)\n"
            "באזור ריק, רק משוואות III ו-IV מקשרות בין $\\vec{E}$ ו-$\\vec{B}$. "
            "מטענים וזרמים חופשיים אפסיים, ולכן $\\nabla\\cdot\\vec{E}=0$ ו-$\\vec{J}=0$.\n"
            "$$\\nabla\\times\\vec{E} = -\\frac{\\partial\\vec{B}}{\\partial t} \\quad \\text{(פאראדי)}$$\n"
            "$$\\nabla\\times\\vec{B} = \\mu_0\\epsilon_0\\frac{\\partial\\vec{E}}{\\partial t} "
            "\\quad \\text{(אמפר-מקסוול)}$$\n\n"
            "### צעד 2 — רוטור על פאראדי, הצבת אמפר-מקסוול\n"
            "לוקחים רוטור על משוואת פאראדי ומחליפים את $\\nabla\\times\\vec{B}$ מאמפר-מקסוול:\n"
            "$$\\nabla\\times(\\nabla\\times\\vec{E}) = "
            "-\\mu_0\\epsilon_0\\frac{\\partial^2\\vec{E}}{\\partial t^2}$$\n\n"
            "### צעד 3 — זהות וקטורית + גאוס ל-E ($\\nabla\\cdot\\vec{E}=0$ בריק)\n"
            "משתמשים בזהות $\\nabla\\times(\\nabla\\times\\vec{E}) = \\nabla(\\nabla\\cdot\\vec{E}) - \\nabla^2\\vec{E}$. "
            "בריק $\\nabla\\cdot\\vec{E}=0$, ולכן:\n"
            "$$\\nabla^2\\vec{E} = \\mu_0\\epsilon_0\\frac{\\partial^2\\vec{E}}{\\partial t^2}$$\n\n"
            "### צעד 4 — השוואה למשוואת גל $\\nabla^2 f = (1/v^2)\\partial^2 f/\\partial t^2$\n"
            "$$v^2 = \\frac{1}{\\mu_0\\epsilon_0} \\Rightarrow \\boxed{c = \\frac{1}{\\sqrt{\\mu_0\\epsilon_0}} "
            "\\approx 3\\times10^8\\;\\text{m/s}}$$\n\n"
            "ערך זה תואם למהירות האור הנמדדת — הניבוי הגדול ביותר של מקסוול.\n\n"
            "**פרשנות פיזיקלית:** השדות החשמלי והמגנטי מתנודדים יחד, "
            "כל אחד מחזיק את השני — מנגנון גל EM מתפשט עצמאית.\n\n"
            "**אסטרטגיה לבחינה:** אין חובה לשחזר כל זהות וקטorית, "
            "אך חובה לדעת $c = 1/\\sqrt{\\mu_0\\epsilon_0}$ "
            "ולציין ששילבתם פאראדי ואמפר-מקסוול. אותה גזירה עובדת ל-$\\vec{B}$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Situation | Equation | Integral form |\n"
            "|---|---|---|\n"
            "| E field of symmetric charge distribution | Gauss for E | "
            "$\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ |\n"
            "| Total flux of B through closed surface | Gauss for B | $= 0$ always |\n"
            "| EMF from changing B | Faraday | $\\mathcal{E} = -d\\Phi_B/dt$ |\n"
            "| B around symmetric steady current | Ampère-Maxwell | "
            "$\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I_{\\text{enc}}$ |\n"
            "| Capacitor charging (gap between plates) | Ampère-Maxwell + $I_d$ | "
            "$\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0\\epsilon_0 d\\Phi_E/dt$ |\n"
            "| Speed of EM waves | III + IV → wave equation | $c = 1/\\sqrt{\\mu_0\\epsilon_0}$ |\n\n"
            "**Decision flowchart:**\n"
            "1. Are there enclosed **charges** with symmetry? → Gauss for E.\n"
            "2. Need to prove **no magnetic monopoles** or zero net B flux? → Gauss for B.\n"
            "3. Is **magnetic flux changing** through a loop? → Faraday.\n"
            "4. Is there **current** or **changing E**? → Ampère-Maxwell (include $I_d$ if E changes).\n"
            "5. Need **wave speed** in vacuum? → Combine differential forms III and IV."
        ),
        "body_he_md": (
            "| מצב | משוואה | צורה אינטegralית |\n"
            "|---|---|---|\n"
            "| שדה E של פילוג מטענים סימטרי | גאוס ל-E | "
            "$\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ |\n"
            "| שטף B כולל דרך משטח סגור | גאוס ל-B | $= 0$ תמיד |\n"
            "| כ\"א משטף B משתנה | פאראדי | $\\mathcal{E} = -d\\Phi_B/dt$ |\n"
            "| B סביב זרם יציב סימטרי | אמפר-מקסוול | "
            "$\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I_{\\text{enc}}$ |\n"
            "| קבל נטען (רווח בין לוחות) | אמפר-מקסוול + $I_d$ | "
            "$\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0\\epsilon_0 d\\Phi_E/dt$ |\n"
            "| מהירות גלי EM | III + IV → משוואת גל | $c = 1/\\sqrt{\\mu_0\\epsilon_0}$ |\n\n"
            "**תרשים החלטה:**\n"
            "1. יש **מטענים כלואים** עם סימטריה? → גאוס ל-E.\n"
            "2. צריך להוכיח **אין מונופולים מגנטיים** או שטף B נטו אפס? → גאוס ל-B.\n"
            "3. **שטף מגנטי משתנה** דרך לולאה? → פאראדי.\n"
            "4. יש **זרם** או **E משתנה**? → אמפר-מקסוול (כלול $I_d$ אם E משתנה).\n"
            "5. צריך **מהירות גל** בריק? → שלב צורות דיפרנציאליות III ו-IV."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below. **Try each one before opening the solution** — "
            "the steps matter as much as the final answer. For each problem, first identify "
            "which Maxwell equation applies, then write the integral or differential form, "
            "and finally check units and physical reasonableness."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "הצעדים חשובים לא פחות מהתשובה הסופית. בכל בעיה, זהו קודם איזו משוואת "
            "מקסוול רלוונטית, כתבו את הצורה האינטegralית או הדיפרנציאלית, "
            "ולבסוף בדקו יחידות והגיון פיזיקלי."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Gauss's law for E gives enclosed charge, not the field directly.** "
            "You still need symmetry to extract $E$ from the flux integral.\n\n"
            "2. **Gauss's law for B = 0 always** — it is a topological constraint, not a "
            "formula for computing $B$ in arbitrary geometry.\n\n"
            "3. **Faraday's integral law** gives the EMF around a **loop**, not the electric "
            "field at a single point.\n\n"
            "4. **Displacement current is not a flow of charge** — the name is historical. "
            "It is $\\epsilon_0\\, d\\Phi_E/dt$, which acts like a current in Ampère's law.\n\n"
            "5. **Confusing integral and differential forms** — know both, but use integral "
            "forms for symmetric geometries and differential forms for wave derivations.\n\n"
            "**Example misconception:** Displacement current flows through insulating plates.\n\n"
            "**Fix:** No charge moves between capacitor plates. The changing E field produces "
            "the same magnetic effect as if current were flowing."
        ),
        "body_he_md": (
            "1. **חוק גאוס ל-E נותן מטען כלוא, לא את השדה ישירות.** "
            "עדיין צריך סימטריה כדי לחלץ $E$ מאינטegral השטף.\n\n"
            "2. **חוק גאוס ל-B = 0 תמיד** — זה אילוץ טופולוגי, לא נוסחה לחישוב $B$ "
            "בגיאומטריה כללית.\n\n"
            "3. **חוק פאראדי האינטegralי** נותן כ\"א סביב **לולאה**, לא את השדה החשמלי "
            "בנקודה בודדת.\n\n"
            "4. **זרם תזוזה אינו זרימת מטען** — השם היסטורי. "
            "זה $\\epsilon_0\\, d\\Phi_E/dt$, שפועל כמו זרם בחוק אמפר.\n\n"
            "5. **בלבול בין צורות אינטegralיות ודיפרנציאליות** — "
            "דעו את שתיהן, אך השתמשו באינטegralיות לגיאומטריות סימטריות "
            "ובדיפרנציאליות לגזירות גל.\n\n"
            "**אשליה נפוצה:** זרם תזוזה זורם דרך לוחות מבודדים.\n\n"
            "**תיקון:** אין מטען נע בין לוחות הקבל. השדה E המשתנה יוצר את אותו "
            "אפect מגנטי כאילו זרם זורם."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Maxwell's equations are not an isolated university topic — they are the bridge "
            "between all prior electromagnetism and modern physics.\n\n"
            "**Builds on:**\n"
            "- `concept:electrostatics` and `concept:gauss_law` (Equation I)\n"
            "- `concept:faraday_induction` (Equation III)\n"
            "- `concept:ampere_law` (Equation IV, before displacement current)\n\n"
            "**Unlocks:**\n"
            "- `concept:em_waves` **Electromagnetic Waves** (direct consequence)\n"
            "- `concept:optics_physical` **Physical Optics** (light as EM radiation)\n"
            "- `concept:special_relativity` (Maxwell's equations are Lorentz invariant)\n\n"
            "**Why it matters for exams:** University Physics 2 finals routinely ask you to "
            "identify equations, compute displacement current, and derive $c$. The charging "
            "capacitor paradox is the most common conceptual trap."
        ),
        "body_he_md": (
            "משוואות מקסוול אינן נושא מבודד באוניברסיטה — הן הגשר בין כל "
            "האלקטרומגנטיות הקודמת לפיזיקה מודרנית.\n\n"
            "**מבוסס על:**\n"
            "- `concept:electrostatics` ו-`concept:gauss_law` (משוואה I)\n"
            "- `concept:faraday_induction` (משוואה III)\n"
            "- `concept:ampere_law` (משוואה IV, לפני זרם תזוזה)\n\n"
            "**פותח את:**\n"
            "- `concept:em_waves` **גלי אלקטרומגנטיות** (תוצאה ישירה)\n"
            "- `concept:optics_physical` **אופטיקה פיזיקלית** (אור כקרינה EM)\n"
            "- `concept:special_relativity` (משוואות מקסוול אינוariantיות ללורנץ)\n\n"
            "**למה זה חשוב לבחינות:** בחינות סופיות בפיזיקה 2 דורשות לעיתים קרובות "
            "זיהוי משוואות, חישוב זרם תזוזה וגזירת $c$. "
            "פרadokס הקבל הנטען הוא המלכודת המושגית הנפוצה ביותר."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "| # | Equation | Key Word |\n"
            "|---|---|---|\n"
            "| I | $\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ | Charges → E |\n"
            "| II | $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ | No monopoles |\n"
            "| III | $\\oint\\vec{E}\\cdot d\\vec{\\ell} = -d\\Phi_B/dt$ | Changing B → EMF |\n"
            "| IV | $\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I + \\mu_0\\epsilon_0 d\\Phi_E/dt$ | "
            "Currents + changing E → B |\n\n"
            "- Displacement current: $I_d = \\epsilon_0 d\\Phi_E/dt = \\epsilon_0 A\\, dE/dt$\n"
            "- EM wave speed: $c = 1/\\sqrt{\\mu_0\\epsilon_0} \\approx 3\\times10^8$ m/s\n"
            "- Differential vacuum forms: $\\nabla\\cdot\\vec{E}=\\rho/\\epsilon_0$; "
            "$\\nabla\\cdot\\vec{B}=0$; $\\nabla\\times\\vec{E}=-\\partial\\vec{B}/\\partial t$; "
            "$\\nabla\\times\\vec{B}=\\mu_0\\vec{J}+\\mu_0\\epsilon_0\\partial\\vec{E}/\\partial t$\n\n"
            "**Last review:** Recite all four equations from memory, then solve one displacement "
            "current problem without notes."
        ),
        "body_he_md": (
            "| # | משוואה | מילת מפתח |\n"
            "|---|---|---|\n"
            "| I | $\\oint\\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ | מטענים → E |\n"
            "| II | $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ | אין מונופולים |\n"
            "| III | $\\oint\\vec{E}\\cdot d\\vec{\\ell} = -d\\Phi_B/dt$ | B משתנה → כ\"א |\n"
            "| IV | $\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I + \\mu_0\\epsilon_0 d\\Phi_E/dt$ | "
            "זרם + E משתנה → B |\n\n"
            "- זרם תזוזה: $I_d = \\epsilon_0 d\\Phi_E/dt = \\epsilon_0 A\\, dE/dt$\n"
            "- מהירות גל EM: $c = 1/\\sqrt{\\mu_0\\epsilon_0} \\approx 3\\times10^8$ m/s\n"
            "- צורות דיפרנציאליות בריק: $\\nabla\\cdot\\vec{E}=\\rho/\\epsilon_0$; "
            "$\\nabla\\cdot\\vec{B}=0$; $\\nabla\\times\\vec{E}=-\\partial\\vec{B}/\\partial t$; "
            "$\\nabla\\times\\vec{B}=\\mu_0\\vec{J}+\\mu_0\\epsilon_0\\partial\\vec{E}/\\partial t$\n\n"
            "**חזרה אחרונה:** דקלמו את ארבע המשוואות בעל פה, ואז פתרו בעיית זרם תזוזה "
            "אחת בלי רשימות."
        ),
    },
    "summary": {
        "body_en_md": (
            "**Key takeaways:**\n\n"
            "- **Four equations** unify all of classical electromagnetism.\n"
            "- **I (Gauss E):** Charges create/source $\\vec{E}$ "
            "($\\oint\\vec{E}\\cdot d\\vec{A} = Q/\\epsilon_0$).\n"
            "- **II (Gauss B):** No magnetic monopoles ($\\oint\\vec{B}\\cdot d\\vec{A} = 0$).\n"
            "- **III (Faraday):** Changing B induces EMF ($\\mathcal{E} = -d\\Phi_B/dt$).\n"
            "- **IV (Ampère-Maxwell):** Currents + changing E create B; includes displacement current.\n"
            "- **EM waves:** Self-sustaining via III↔IV symmetry; speed $c = 1/\\sqrt{\\mu_0\\epsilon_0}$.\n\n"
            "**Takeaway:** You should now recognise which Maxwell equation applies from the "
            "problem wording alone — and know when displacement current is essential."
        ),
        "body_he_md": (
            "**עיקרי השיעור:**\n\n"
            "- **ארבע משוואות** מאחדות את כל האלקטרומגנטיות הקלאסית.\n"
            "- **I (גאוס E):** מטענים יוצרים/מקור $\\vec{E}$ "
            "($\\oint\\vec{E}\\cdot d\\vec{A} = Q/\\epsilon_0$).\n"
            "- **II (גאוס B):** אין מונופולים מגנטיים ($\\oint\\vec{B}\\cdot d\\vec{A} = 0$).\n"
            "- **III (פאראדי):** B משתנה מושרה כ\"א ($\\mathcal{E} = -d\\Phi_B/dt$).\n"
            "- **IV (אמפר-מקסוול):** זרמים + E משתנה יוצרים B; כולל זרם תזוזה.\n"
            "- **גלי EM:** מתקיימים בזכות סימטריה III↔IV; מהירות $c = 1/\\sqrt{\\mu_0\\epsilon_0}$.\n\n"
            "**סיכום:** כעת תוכלו לזהות איזו משוואת מקסוול רלוונטית מהניסוח בלבד — "
            "ולדעת מתי זרם תזוזה חיוני."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "Gauss's law for **magnetic fields** states $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ for "
            "any closed surface. The zero on the right-hand side means there are no magnetic "
            "charges (monopoles) — magnetic field lines never begin or end at isolated points.\n\n"
            "Gauss for E relates flux to enclosed **electric** charge. Faraday links changing "
            "magnetic flux to induced EMF. Ampère-Maxwell relates B circulation to currents "
            "and changing E.\n\n"
            "**Common error:** Choosing Gauss for E because \"Gauss's law\" sounds general. "
            "Always specify E vs B.\n\n"
            "**Exam tip:** \"No magnetic monopoles\" is the one-sentence summary of Gauss for B. "
            "**Answer:** Gauss's law for B."
        ),
        "explanation_he": (
            "חוק גאוס ל**שדות מגנטיים** קובע $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ לכל משטח סגור. "
            "האפס בצד ימין פירושו שאין מטענים מגנטיים (מונופולים) — קווי שדה מגנטי "
            "לעולם לא מתחילים או נגמרים בנקודות מבודדות.\n\n"
            "גאוס ל-E קושר שטף למטען **חשמלי** כלוא. פאראדי קושר שטף מגנטי משתנה לכ\"א מושרה. "
            "אמפר-מקסוול קושר מעגל $\\vec{B}$ לזרמים ו-E משתנה.\n\n"
            "**טעות נפוצה:** בחירת גאוס ל-E כי \"חוק גאוס\" נשמע כללי. "
            "תמיד ציינו E מול B.\n\n"
            "**טיפ לבחינה:** \"אין מונופולים מגנטיים\" הוא הסיכום במשפט אחד של גאוס ל-B. "
            "**תשובה:** גאוס ל-B."
        ),
    },
    {
        "explanation_en": (
            "For a charging capacitor, displacement current equals wire current: "
            "$I_d = \\epsilon_0 A\\, dE/dt = I$. Rearranging gives the rate of change of "
            "electric field between the plates:\n"
            "$$dE/dt = \\frac{I}{\\epsilon_0 A} = "
            "\\frac{10^{-3}}{(8.85\\times10^{-12})(5\\times10^{-4})} = "
            "2.26\\times10^{11}\\;\\text{V/(m·s)}$$\n\n"
            "This large value makes physical sense: the plates are small "
            "($A = 5\\;\\text{cm}^2$), so a modest charging current must produce a rapid "
            "change in E to maintain $I_d = I$ continuity across the capacitor gap.\n\n"
            "**Common error:** Using $A = 5$ cm² without converting to m², or forgetting "
            "$\\epsilon_0$ in the denominator.\n\n"
            "**Exam tip:** When given $I$ and asked for $dE/dt$, use $I_d = I$ directly. "
            "**Answer:** $2.26\\times10^{11}$ V/(m·s)."
        ),
        "explanation_he": (
            "בקבל נטען, זרם תזוזה שווה לזרם בחוט: $I_d = \\epsilon_0 A\\, dE/dt = I$. "
            "פריסה מחדש נותנת את קצב שינוי השדה החשמלי בין הלוחות:\n"
            "$$dE/dt = \\frac{I}{\\epsilon_0 A} = "
            "\\frac{10^{-3}}{(8.85\\times10^{-12})(5\\times10^{-4})} = "
            "2.26\\times10^{11}\\;\\text{V/(m·s)}$$\n\n"
            "ערך גדול זה הגיוני: הלוחות קטנים ($A = 5\\;\\text{cm}^2$), "
            "ולכן זרם טעינה מתון חייב לייצר שינוי מהיר ב-E כדי לשמור על "
            "רציפות $I_d = I$ ברווח הקבל.\n\n"
            "**טעות נפוצה:** שימוש ב-$A = 5$ cm² בלי המרה ל-m², או שכחת $\\epsilon_0$ במכנה.\n\n"
            "**טיפ לבחינה:** כשנותנים $I$ ושואלים על $dE/dt$, השתמשו ב-$I_d = I$ ישירות. "
            "זכרו: $I_d = \\epsilon_0 A\\, dE/dt$ הוא הגשר בין זרם בחוט לשדה בין הלוחות. "
            "**תשובה:** $2.26\\times10^{11}$ V/(m·s)."
        ),
    },
    {
        "explanation_en": (
            "Gauss's law for B in words: the **net magnetic flux** through any closed surface "
            "is exactly zero. Physically, this reflects the absence of magnetic monopoles — "
            "isolated north or south poles have never been observed.\n\n"
            "Every magnetic field line that exits a closed surface must re-enter it somewhere "
            "else, so outward and inward flux cancel. Magnetic field lines always form "
            "**closed loops**, unlike electric field lines that can start and end on charges.\n\n"
            "**Common error:** Saying \"flux is zero because B = 0\" — the field is usually "
            "non-zero; it is the **net** flux that vanishes.\n\n"
            "**Exam tip:** Contrast with Gauss for E, where enclosed charge makes net flux "
            "non-zero."
        ),
        "explanation_he": (
            "חוק גאוס ל-B במילים: **השטף המגנטי הנטו** דרך כל משטח סגור הוא בדיוק אפס. "
            "פיזיקלית, זה משקף היעדר מונופולים מגנטיים — קוטב צפוני או דרומי מבודד "
            "מעולם לא נצפה.\n\n"
            "כל קו שדה מגנטי שיוצא ממשטח סגור חייב לחזור אליו במקום אחר, "
            "ולכן שטף חוצה ופנימה מתבטלים. קווי שדה מגנטי תמיד יוצרים "
            "**לולאות סגuroות**, בניגוד לקווי שדה חשמלי שיכולים להתחיל ולהסתיים על מטענים.\n\n"
            "**טעות נפוצה:** \"שטף אפס כי B = 0\" — השדה בדרך כלל לא אפס; "
            "זה **השטף הנטו** שמתאפס.\n\n"
            "**טיפ לבחינה:** השוו לגאוס ל-E, שבו מטען כלוא גורם לשטף נטו שונה מאפס."
        ),
    },
    {
        "explanation_en": (
            "Displacement current: $I_d = \\epsilon_0 A\\, dE/dt$.\n"
            "$$I_d = (8.85\\times10^{-12})(10^{-4})(10^{12}) = 8.85\\times10^{-4}\\;\\text{A} "
            "\\approx 0.885\\;\\text{mA}$$\n\n"
            "The electric flux through area $A$ changes at rate $d\\Phi_E/dt = A\\, dE/dt$, "
            "and Maxwell's term $\\epsilon_0\\, d\\Phi_E/dt$ acts exactly like a real current "
            "in Ampère's law — it produces the same magnetic field circulation around the gap.\n\n"
            "Between capacitor plates, no charge physically moves, yet the growing E field "
            "maintains magnetic field continuity exactly as if current were flowing.\n\n"
            "**Common error:** Using $A = 1$ cm² as $1$ m², giving a result $10^4$ times too large.\n\n"
            "**Exam tip:** Always convert cm² → m² before substituting into $\\epsilon_0 A\\, dE/dt$. "
            "**Answer:** 0.885 mA."
        ),
        "explanation_he": (
            "זרם תזוזה: $I_d = \\epsilon_0 A\\, dE/dt$.\n"
            "$$I_d = (8.85\\times10^{-12})(10^{-4})(10^{12}) = 8.85\\times10^{-4}\\;\\text{A} "
            "\\approx 0.885\\;\\text{mA}$$\n\n"
            "השטף החשמלי דרך שטח $A$ משתנה בקצב $d\\Phi_E/dt = A\\, dE/dt$, "
            "ואיבר מקסוול $\\epsilon_0\\, d\\Phi_E/dt$ פועל בדיוק כמו זרם אמיתי "
            "בחוק אמפר — הוא יוצר את אותו מעגל שדה מגנטי סביב הרווח.\n\n"
            "בין לוחות הקבל, אין מטען שנע פיזית, אך השדה E הגדל "
            "שומר על רציפות השדה המגנטי בדיוק כאילו זרם זורם.\n\n"
            "**טעות נפוצה:** שימוש ב-$A = 1$ cm² כ-$1$ m², תוצאה גדולה פי $10^4$.\n\n"
            "**טיפ לבחינה:** המירו תמיד cm² → m² לפני הצבה. **תשובה:** 0.885 mA."
        ),
    },
    {
        "explanation_en": (
            "Faraday's law in differential form (vacuum, no free currents in the region) is:\n"
            "$$\\nabla\\times\\vec{E} = -\\frac{\\partial\\vec{B}}{\\partial t}$$\n\n"
            "This says a **circulating electric field** (non-zero curl of E) is produced wherever "
            "the magnetic field changes in time. The minus sign encodes Lenz's law: the induced "
            "field opposes the change in magnetic flux that caused it.\n\n"
            "In integral form, the same physics appears as $\\oint\\vec{E}\\cdot d\\vec{\\ell} = "
            "-d\\Phi_B/dt$ — EMF around a loop equals the negative rate of change of magnetic flux.\n\n"
            "**Common error:** Writing $\\nabla\\times\\vec{B}$ instead of $\\nabla\\times\\vec{E}$ — "
            "that is Ampère-Maxwell, not Faraday.\n\n"
            "**Exam tip:** Faraday couples **E** to changing **B**. "
            "Ampère-Maxwell couples **B** to changing **E**."
        ),
        "explanation_he": (
            "חוק פאראדי בצורה דיפרנציאלית (ריק, ללא זרמים חופשיים באזור) הוא:\n"
            "$$\\nabla\\times\\vec{E} = -\\frac{\\partial\\vec{B}}{\\partial t}$$\n\n"
            "זה אומר ש**שדה חשמלי מסתובב** (רוטור לא-אפס של E) נוצר בכל מקום "
            "שהשדה המגנטי משתנה בזמן. הסימן מינוס מקודד את חוק לנץ: "
            "השדה המושרה מתנגד לשינוי בשטף המגנטי שגרם לו.\n\n"
            "בצורה אינטegralית, אותה פיזיקה מופיעה כ-$\\oint\\vec{E}\\cdot d\\vec{\\ell} = "
            "-d\\Phi_B/dt$ — כ\"א סביב לולאה שווה לקצב השינוי השלילי של שטף מגנטי.\n\n"
            "**טעות נפוצה:** כתיבת $\\nabla\\times\\vec{B}$ במקום $\\nabla\\times\\vec{E}$.\n\n"
            "**טיפ לבחינה:** פאראדי מקשר E ל-B משתנה. אמפר-מקסוול מקשר B ל-E משתנה. "
            "בבחינה, כתבו תמיד את הנוסחה המלאה לפני הצבת ערכים."
        ),
    },
    {
        "explanation_en": (
            "Maxwell added the **displacement current** term $\\mu_0\\epsilon_0\\, d\\Phi_E/dt$ "
            "to Ampère's law. Before this, applying Ampère's law to a charging capacitor gave "
            "contradictory results depending on which surface bounded the same loop.\n\n"
            "Surface through the wire: $\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I$. "
            "Surface between plates: zero conduction current → zero B circulation — a contradiction.\n\n"
            "Displacement current fixes this: $I_d = \\epsilon_0\\, d\\Phi_E/dt = I$ between plates. "
            "It also predicts that changing E fields create B fields, enabling EM wave propagation.\n\n"
            "**Exam tip:** Always mention both the **consistency fix** and the **EM wave prediction**."
        ),
        "explanation_he": (
            "מקסוול הוסיף את איבר **זרם התזוזה** $\\mu_0\\epsilon_0\\, d\\Phi_E/dt$ לחוק אמפר. "
            "לפני כן, החלת חוק אמפר על קבל נטען נתנה תוצאות סותרות לפי איזה משטח "
            "גובל באותה לולאה — פרadokס קלאסי בקורס פיזיקה 2.\n\n"
            "משטח דרך החוט: $\\oint\\vec{B}\\cdot d\\vec{\\ell} = \\mu_0 I$. "
            "משטח בין לוחות: אפס זרם הולכה, ולכן לפי אמפר המקורי — אפס מעגל B. "
            "שני משטחים, אותה לולאה, תשובות שונות — סתירה.\n\n"
            "זרם תזוזה מתקן: $I_d = \\epsilon_0\\, d\\Phi_E/dt = I$ בין הלוחות. "
            "הוא גם מנבא ששדות E משתנים יוצרים B, ומאפשר התפשטות גלי EM בריק.\n\n"
            "**טיפ לבחינה:** הזכירו תיקון העקביות **וגם** ניבוי גלי EM."
        ),
    },
    {
        "explanation_en": (
            "Start from Gauss for B: $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ for **any** closed surface. "
            "Net outward magnetic flux is zero — equal flux enters and exits.\n\n"
            "Now suppose a field line **ended** inside the surface at point P. Enclose P with a "
            "tiny sphere. All flux through that sphere would be **inward** (field lines terminate "
            "at P), giving $\\oint\\vec{B}\\cdot d\\vec{A} \\neq 0$ — contradicting Gauss for B.\n\n"
            "Therefore field lines cannot begin or end inside any closed surface; they must "
            "form **closed loops**.\n\n"
            "**Common error:** Confusing this with \"B = 0 everywhere\" — the field is non-zero; "
            "only the net flux vanishes.\n\n"
            "**Exam tip:** This is a proof-by-contradiction question — state Gauss, then assume "
            "a terminating line."
        ),
        "explanation_he": (
            "התחילו מגאוס ל-B: $\\oint\\vec{B}\\cdot d\\vec{A} = 0$ ל**כל** משטח סגור. "
            "שטף מגנטי נטו החוצה הוא אפס — שטף נכנס ויוצא שווים.\n\n"
            "נניח שקו שדה **מסתיים** בתוך המשטח בנקודה P. "
            "עטפו את P בכדור זעיר. כל השטף דרך הכדור יהיה **פנימה** "
            "(קווי שדה נגמרים ב-P), ונקבל $\\oint\\vec{B}\\cdot d\\vec{A} \\neq 0$ — "
            "סתירה לגאוס ל-B.\n\n"
            "לכן קווי שדה לא יכולים להתחיל או להסתיים בתוך משטח סגור; "
            "הם חייבים ליצור **לולאות סגuroות**.\n\n"
            "**טעות נפוצה:** בלבול עם \"B = 0 בכל מקום\" — השדה לא אפס; "
            "רק השטף הנטו מתאפס.\n\n"
            "**טיפ לבחינה:** זו שאלת הוכחה בסתירה — נסחו גאוס, ואז הניחו קו מסתיים."
        ),
    },
    {
        "explanation_en": (
            "**Part (a):** Displacement current equals wire current during charging, so "
            "$dE/dt = I/(\\epsilon_0 A)$.\n"
            "$$dE/dt = \\frac{5\\times10^{-4}}{(8.85\\times10^{-12})(4\\times10^{-4})} "
            "= 1.41\\times10^{11}\\;\\text{V/(m·s)}$$\n\n"
            "**Part (b):** Plate radius $R = \\sqrt{A/\\pi} = \\sqrt{4\\times10^{-4}/\\pi} "
            "\\approx 1.13\\;\\text{cm}$. For $r = 1\\;\\text{cm}$ inside the plates "
            "($r < R$): $B = \\mu_0 I r/(2\\pi A)$. For $r > R$ outside the plate edges: "
            "$B = \\mu_0 I/(2\\pi r) = 10\\;\\text{nT}$.\n\n"
            "Apply Ampère-Maxwell with the displacement current enclosed by a circular loop "
            "of radius $r$ centred on the axis between the plates.\n\n"
            "**Common error:** Using the infinite-wire formula without checking whether "
            "$r$ is inside or outside the plate radius.\n\n"
            "**Exam tip:** Always compute $R_{\\text{plate}} = \\sqrt{A/\\pi}$ first."
        ),
        "explanation_he": (
            "**חלק (א):** זרם תזוזה שווה לזרם בחוט בזמן טעינה, ולכן $dE/dt = I/(\\epsilon_0 A)$.\n"
            "$$dE/dt = \\frac{5\\times10^{-4}}{(8.85\\times10^{-12})(4\\times10^{-4})} "
            "= 1.41\\times10^{11}\\;\\text{V/(m·s)}$$\n\n"
            "**חלק (ב):** רדיוס לוח $R = \\sqrt{A/\\pi} \\approx 1.13\\;\\text{cm}$. "
            "עבור $r = 1\\;\\text{cm}$ בתוך הלוחות ($r < R$): $B = \\mu_0 I r/(2\\pi A)$. "
            "עבור $r > R$ מחוץ לקצוות: $B = \\mu_0 I/(2\\pi r) = 10\\;\\text{nT}$.\n\n"
            "יישמו אמפר-מקסוול עם זרם תזוזה כלוא על-ידי לולאה מעגלית "
            "ברדיוס $r$ במרכז הציר בין הלוחות.\n\n"
            "**טעות נפוצה:** נוסחת חוט אינסופי בלי לבדוק אם $r$ בתוך או מחוץ לרדיוס הלוח.\n\n"
            "**טיפ לבחינה:** חשבו תמיד $R_{\\text{plate}} = \\sqrt{A/\\pi}$ קודם. "
            "שימו לב: $r = 1\\;\\text{cm}$ קטן מ-$R \\approx 1.13\\;\\text{cm}$, "
            "ולכן נמצאים **בתוך** רדיוס הלוח ולא מחוצה לו."
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
