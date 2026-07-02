#!/usr/bin/env python3
"""Expand static_equilibrium.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/static_equilibrium.json"

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
            "Engineers design bridges, cranes, shelves, and ladders using **static equilibrium**: "
            "the condition that a rigid body neither accelerates linearly nor rotates. This is "
            "not merely \"nothing moves\" — it is a precise mathematical statement that the net "
            "force and net torque on the body both vanish.\n\n"
            "Two simultaneous conditions are required:\n"
            "1. **$\\sum F = 0$** — zero net force, so no linear acceleration (translational equilibrium).\n"
            "2. **$\\sum \\tau = 0$** — zero net torque, so no angular acceleration (rotational equilibrium).\n\n"
            "In 2D you get up to **three independent equations** ($\\sum F_x = 0$, $\\sum F_y = 0$, "
            "$\\sum \\tau = 0$); in 3D there are up to six.\n\n"
            "**Key insight:** The torque equation can be written about **any point** you choose. "
            "A clever pivot eliminates unknown forces by giving them zero moment arm — turning "
            "a multi-unknown problem into a single equation.\n\n"
            "**Course relevance:** Virtually every structural engineering problem — beams, frames, "
            "trusses, ladders — uses exactly these two conditions. You will also apply equilibrium "
            "when deriving friction limits, locating the centre of mass, and judging stability. "
            "This lesson builds on `concept:torque` and `concept:newton_laws`."
        ),
        "body_he_md": (
            "מהנדסים מעצבים גשרים, מנופים, מדפים וסולמות תוך שימוש ב**שיווי משקל סטטי**: "
            "התנאי שגוף קשיח לא מאיץ תנועתית ולא מסתובב. זה לא רק \"שום דבר לא זז\" — "
            "אלא הצהרה מתמטית מדויקת שכוח הכולל ומומנט הכוח הכולל מתאפסים.\n\n"
            "דרושים שני תנאים בו-זמנית:\n"
            "1. **$\\sum F=0$** — אין האצה קווית (שיווי משקל תנועתי).\n"
            "2. **$\\sum\\tau=0$** — אין האצה זוויתית (שיווי משקל סיבובי).\n\n"
            "ב-2D יש עד **שלוש משוואות בלתי תלויות** ($\\sum F_x=0$, $\\sum F_y=0$, $\\sum\\tau=0$); "
            "ב-3D עד שש.\n\n"
            "**תובנה מרכזית:** $\\sum\\tau=0$ ניתנת לכתיבה סביב **כל** נקודה. "
            "ציר חכם מסלק כוחות לא ידועים (זרוע מומנט אפס) — "
            "והופך בעיה רב-נעלמית למשוואה אחת.\n\n"
            "**רלוונטיות לקורס:** כמעט כל בעיית הנדסת מבנים — קורות, מסגרות, סולמות — "
            "משתמשת בשני התנאים האלה. תיישמו שיווי משקל גם בגבולות חיכוך, מיקום מ\"מ ויציבות. "
            "השיעור מבוסס על `concept:torque` ו-`concept:newton_laws`."
        ),
    },
    "definition": {
        "body_en_md": (
            "### Condition 1: Translational equilibrium\n"
            "$$\\sum\\vec{F} = 0 \\implies \\sum F_x = 0 \\text{ and } \\sum F_y = 0.$$\n"
            "Every force on the body — weight, normal forces, friction, cable tension, hinge "
            "reactions — must appear in the FBD and sum to zero in each direction.\n\n"
            "### Condition 2: Rotational equilibrium\n"
            "$$\\sum\\vec{\\tau} = 0.$$\n"
            "This must hold for **every** choice of pivot point. If it fails at one pivot but "
            "passes at another, the object is **not** in equilibrium.\n\n"
            "### Torque of a force about a pivot\n"
            "$$\\tau = rF\\sin\\phi = r_\\perp F$$\n"
            "where $r$ = distance from pivot to force application, $\\phi$ = angle between "
            "$\\vec{r}$ and $\\vec{F}$, and $r_\\perp = r\\sin\\phi$ = perpendicular (moment) arm.\n\n"
            "**Sign convention:** Counterclockwise (CCW) torques positive (+); clockwise (CW) negative (−). "
            "Pick one convention and use it consistently.\n\n"
            "### Weight acts at the centre of mass\n"
            "For any rigid body, gravity acts effectively at the **centre of mass** (CM). "
            "For a uniform object (rod, plank, disk), the CM is at the geometric centre.\n\n"
            "### Stability\n"
            "An object is **stable** if a small displacement raises its CM (potential energy increases). "
            "The CM must lie above the **base of support**. If the CM moves outside the base, the object tips."
        ),
        "body_he_md": (
            "### תנאי 1: שיווי משקל תנועתי\n"
            "$$\\sum F_x=0, \\quad \\sum F_y=0.$$\n"
            "כל כוח על הגוף — משקל, נורמל, חיכוך, מתח כבל, תגובת ציר — "
            "חייב להופיע בדיאגרמת הכוחות ולהתאפס בכל כיוון.\n\n"
            "### תנאי 2: שיווי משקל סיבובי\n"
            "$$\\sum\\tau=0.$$\n"
            "חייב להתקיים עבור **כל** בחירת ציר. אם נכשל בציר אחד אך עובר באחר — "
            "הגוף **לא** בשיווי משקל.\n\n"
            "### מומנט כוח סביב ציר\n"
            "$$\\tau=rF\\sin\\phi=r_{\\perp}F.$$\n"
            "$r$ = מרחק מהציר לנקודת הפעולה, $\\phi$ = זווית בין $\\vec{r}$ ל-$\\vec{F}$, "
            "ו-$r_{\\perp}=r\\sin\\phi$ = זרוע המומנט הניצבת.\n\n"
            "**סימן:** CCW חיובי, CW שלילי. בחרו קונבנציה והיצמדו אליה.\n\n"
            "### משקל פועל במרכז המסה\n"
            "עבור גוף קשיח, הכבידה פועלת אפקטיבית ב**מרכז המסה**. "
            "בגוף אחיד (מוט, קורה, דиск) מ\"מ במרכז הגיאומטרי.\n\n"
            "### יציבות\n"
            "גוף **יציב** כשתזוזה קטנה מעלה את מ\"מ (אנרגיה פוטנציאלית עולה). "
            "מ\"מ חייב להיות מעל **בסיס התמיכה**; אם יוצא מהבסיס — הגוף נופל."
        ),
    },
    "theory": {
        "body_en_md": (
            "The torque equation is valid about **any** point. The strategic choice is to place "
            "the pivot at the point of application of an **unknown force you want to eliminate** — "
            "that force then has zero moment arm and drops out of the equation entirely.\n\n"
            "**Example:** A beam supported at two points A and B with unknown reactions $R_A$ and $R_B$.\n"
            "- Take torque about A: $R_A$ disappears (zero moment arm) → solve for $R_B$ directly.\n"
            "- Then use $\\sum F_y = 0$ → solve for $R_A$.\n\n"
            "### System of equations strategy (2D)\n"
            "1. Draw FBD — label every force with magnitude and direction.\n"
            "2. Write $\\sum F_x = 0$ and $\\sum F_y = 0$.\n"
            "3. Choose pivot to eliminate the most unknowns from $\\sum\\tau = 0$.\n"
            "4. Solve the resulting system (usually 3 equations, up to 3 unknowns in 2D).\n"
            "5. Check signs: positive means force/torque in assumed direction; negative means opposite.\n"
            "6. Verify by re-summing torques about a **different** pivot.\n\n"
            "### Minimum friction for ladders/walls\n"
            "For a ladder resting on a rough floor and smooth wall:\n"
            "- The wall exerts only a **normal force** (horizontal).\n"
            "- The floor exerts both **normal** (vertical) and **friction** (horizontal).\n"
            "- $\\sum\\tau = 0$ about the base gives the wall force; $\\sum F_x = 0$ gives friction.\n"
            "- The no-slip condition $f \\leq \\mu N_{floor}$ yields the minimum $\\mu$ required.\n\n"
            "**Counting unknowns:** Before algebra, count forces vs equations. A typical 2D beam "
            "problem has three unknowns ($R_A$, $R_B$, $T$) and three equilibrium equations — solvable."
        ),
        "body_he_md": (
            "ניתן לכתוב $\\sum\\tau=0$ סביב כל נקודה. הבחירה האסטרטגית: "
            "הציבו את הציר בנקודת פעולה של **כוח לא ידוע שרוצים לסלק** — "
            "אז זרוע המומנט שלו אפס והוא נופל מהמשוואה לחלוטין.\n\n"
            "**דוגמה:** קורה עם תמיכות A ו-B עם כוחות $R_A$, $R_B$ לא ידועים.\n"
            "- ציר ב-A → $R_A$ נעלם → פתרו $R_B$.\n"
            "- $\\sum F_y=0$ → פתרו $R_A$.\n\n"
            "### אסטרטגיה כללית (2D)\n"
            "1. דיאגרמת כוחות — תוויות לכל כוח.\n"
            "2. $\\sum F_x=0$, $\\sum F_y=0$.\n"
            "3. בחרו ציר לסילוק מקסימום נעלמים מ-$\\sum\\tau=0$.\n"
            "4. פתרו מערכת (בדרך כלל 3 משוואות, עד 3 נעלמים).\n"
            "5. בדקו סימנים: חיובי = כיוון שהנחתם; שלילי = הפוך.\n"
            "6. אמתו ב-$\\sum\\tau=0$ סביב **ציר אחר**.\n\n"
            "### חיכוך מינימלי לסולמות\n"
            "סולם על רצפה מחוספסת וקיר חלק:\n"
            "- הקיר: **נורמל** בלבד (אופקי).\n"
            "- הרצפה: **נורמל** (אנכי) ו**חיכוך** (אופקי).\n"
            "- $\\sum\\tau=0$ סביב הבסיס → כוח קיר; $\\sum F_x=0$ → חיכוך.\n"
            "- תנאי אי-החלקה $f\\leq\\mu N$ נותן $\\mu$ מינימלי.\n\n"
            "**ספירת נעלמים:** לפני אלגברה, ספרו כוחות מול משוואות. "
            "בעיית קורה טיפוסית: 3 נעלמים ו-3 משוואות שיווי משקל — פתירה."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A uniform beam of length $L = 4$ m and mass $m = 20$ kg is hinged at the left wall. "
            "A cable attached to the right end makes an angle of 30° with the beam (horizontal beam). "
            "Find the tension $T$ in the cable.\n\n"
            "This is the classic \"hinge + cable\" setup. The hinge supplies two unknown components "
            "($H_x$, $H_y$), but they vanish from the torque equation when we pivot at the hinge.\n\n"
            "### Move 1 — FBD\n"
            "- Weight $W = mg = 20 \\times 10 = 200$ N, downward at the centre ($L/2 = 2$ m from hinge).\n"
            "- Cable tension $T$ at the right end, at 30° above horizontal.\n"
            "- Hinge reaction: $H_x$ (horizontal) and $H_y$ (vertical) at the pivot.\n\n"
            "### Move 2 — Pivot at hinge\n"
            "Hinge forces have zero moment arm → they vanish from $\\sum\\tau = 0$.\n\n"
            "### Move 3 — Torque balance (CCW positive)\n"
            "- Torque of weight (CW): $-W\\cdot(L/2) = -200 \\times 2 = -400$ N·m.\n"
            "- Torque of tension (CCW): vertical component $T\\sin30°$ at distance $L = 4$ m:\n"
            "$$+T\\sin30° \\cdot L = T \\times 0.5 \\times 4 = 2T.$$\n"
            "$$\\sum\\tau = 0: \\quad 2T - 400 = 0 \\Rightarrow T = 200 \\text{ N}.$$\n\n"
            "### Move 4 — Hinge forces (optional)\n"
            "$\\sum F_y=0$: $H_y + T\\sin30° - W = 0 \\Rightarrow H_y = 100$ N (upward).\n"
            "$\\sum F_x=0$: $H_x - T\\cos30° = 0 \\Rightarrow H_x \\approx 173$ N.\n\n"
            "**Answer:** $T = 200$ N.\n\n"
            "**Exam tip:** For angled cables, use $T\\sin\\theta$ for the torque-producing component "
            "perpendicular to the beam, not the full $T$."
        ),
        "body_he_md": (
            "**נתון:** קורה אחידה $L=4$ מ', $m=20$ ק\"ג, צירית בקיר שמאל. "
            "כבל בקצה ימין בזווית 30° מהקורה (קורה אופקית). מצאו מתח $T$.\n\n"
            "זו הגדרת \"ציר + כבל\" קלאסית. הציר מספק שני רכיבים ($H_x$, $H_y$), "
            "אך הם נעלמים ממשוואת המומנט כשהציר בצירה.\n\n"
            "### צעד 1 — דיאגרמת כוחות\n"
            "- משקל $W=mg=200$ נ' כלפי מטה במרכז ($L/2=2$ מ' מהציר).\n"
            "- מתח $T$ בקצה ימין, 30° מעל האופקי.\n"
            "- תגובת ציר: $H_x$ (אופקי) ו-$H_y$ (אנכי).\n\n"
            "### צעד 2 — ציר בצירה\n"
            "כוחות הציר בזרוע אפס → נעלמים מ-$\\sum\\tau=0$.\n\n"
            "### צעד 3 — איזון מומנטים (CCW חיובי)\n"
            "- מומנט משקל (CW): $-200\\times2=-400$ N·m.\n"
            "- מומנט מתח (CCW): רכיב אנכי $T\\sin30°$ במרחק $L=4$ מ':\n"
            "$$2T-400=0\\Rightarrow T=200\\text{ נ'}.$$\n\n"
            "### צעד 4 — כוחות ציר (אופציונלי)\n"
            "$\\sum F_y=0$: $H_y=100$ נ' כלפי מעלה.\n"
            "$\\sum F_x=0$: $H_x\\approx173$ נ'.\n\n"
            "**תשובה:** $T=200$ נ'.\n\n"
            "**טיפ לבחינה:** בכבל בזווית, השתמשו ב-$T\\sin\\theta$ לרכיב שיוצר מומנט "
            "ניצב לקורה, לא ב-$T$ המלא."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A non-uniform beam of length $L = 8$ m and weight $W_{beam} = 500$ N has its CM "
            "at $x_{cm} = 3$ m from the left end. Two supports: $R_A$ at the left end and $R_B$ at the "
            "right end. A person of weight $W_p = 600$ N stands at $x_p = 6$ m from the left end. "
            "Find $R_A$ and $R_B$.\n\n"
            "The beam is **non-uniform** — weight acts at the given CM ($x=3$ m), not at $L/2=4$ m. "
            "This is a common exam trap.\n\n"
            "### Move 1 — FBD\n"
            "- $R_A$ (up) at $x = 0$. $R_B$ (up) at $x = 8$ m.\n"
            "- $W_{beam} = 500$ N (down) at $x = 3$ m.\n"
            "- $W_p = 600$ N (down) at $x = 6$ m.\n\n"
            "### Move 2 — Torque about A (eliminates $R_A$)\n"
            "$$R_B(8) - W_{beam}(3) - W_p(6) = 0.$$\n"
            "$$8R_B = 500(3) + 600(6) = 1500 + 3600 = 5100.$$\n"
            "$$R_B = 637.5 \\text{ N}.$$\n\n"
            "### Move 3 — Vertical force balance\n"
            "$$R_A + R_B = W_{beam} + W_p = 1100 \\text{ N}.$$\n"
            "$$R_A = 1100 - 637.5 = 462.5 \\text{ N}.$$\n\n"
            "**Check:** $\\sum\\tau$ about B: $R_A(8) - 500(5) - 600(2) = 3700 - 3700 = 0.$ ✓\n\n"
            "**Answer:** $R_A = 462.5$ N; $R_B = 637.5$ N.\n\n"
            "**Physical insight:** The right support carries more load because the person stands closer to B."
        ),
        "body_he_md": (
            "**נתון:** קורה לא אחידה $L=8$ מ', $W_{\\text{קורה}}=500$ נ', מ\"מ ב-$x=3$ מ'. "
            "תמיכות $R_A$ (שמאל) ו-$R_B$ (ימין). אדם $W_p=600$ נ' ב-$x=6$ מ'. "
            "מצאו $R_A$ ו-$R_B$.\n\n"
            "הקורה **לא אחידה** — המשקל פועל במ\"מ הנתון ($x=3$ מ'), לא ב-$L/2=4$ מ'. "
            "זו מלכודת בחינה נפוצה.\n\n"
            "### צעד 1 — דיאגרמת כוחות\n"
            "- $R_A$ (מעלה) ב-$x=0$. $R_B$ (מעלה) ב-$x=8$ מ'.\n"
            "- $W_{\\text{קורה}}=500$ נ' (מטה) ב-$x=3$ מ'.\n"
            "- $W_p=600$ נ' (מטה) ב-$x=6$ מ'.\n\n"
            "### צעד 2 — מומנט סביב A (מסלק $R_A$)\n"
            "$$8R_B=500(3)+600(6)=5100\\Rightarrow R_B=637.5\\text{ נ'}.$$\n\n"
            "### צעד 3 — איזון כוחות אנכיים\n"
            "$$R_A=1100-637.5=462.5\\text{ נ'}.$$\n\n"
            "**בדיקה:** $\\sum\\tau$ סביב B: $462.5(8)-500(5)-600(2)=0$ ✓\n\n"
            "**תשובה:** $R_A=462.5$ נ'; $R_B=637.5$ נ'.\n\n"
            "**פרשנות:** התמיכה הימנית נושאת יותר עומס כי האדם קרוב אליה."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** A uniform ladder of mass $m$ and length $L$ leans against a frictionless vertical "
            "wall at angle $\\phi$ from the floor. A person of mass $M$ stands at 3/4 the length from "
            "the base. Find the minimum coefficient of static friction $\\mu_s$ between the ladder and "
            "the floor for the ladder not to slip.\n\n"
            "### Move 1 — FBD\n"
            "- Weight of ladder: $mg$ downward at the CM (midpoint = $L/2$ from base).\n"
            "- Weight of person: $Mg$ downward at $3L/4$ from base.\n"
            "- Wall normal force: $N_W$ horizontal (toward ladder), at the top.\n"
            "- Floor normal: $N_F$ vertical (upward), at base.\n"
            "- Floor friction: $f$ horizontal (away from wall), at base.\n\n"
            "### Move 2 — Horizontal force balance\n"
            "$$f = N_W. \\quad (1)$$\n\n"
            "### Move 3 — Vertical force balance\n"
            "$$N_F = mg + Mg = (m+M)g. \\quad (2)$$\n\n"
            "### Move 4 — Torque about base (eliminates $N_F$ and $f$)\n"
            "Moment arms (horizontal distance for weights, vertical for $N_W$):\n"
            "$$N_W \\cdot L\\sin\\phi = mg\\cdot\\frac{L}{2}\\cos\\phi + Mg\\cdot\\frac{3L}{4}\\cos\\phi.$$\n"
            "$$N_W = \\cot\\phi\\left(\\frac{m}{2}+\\frac{3M}{4}\\right)g.$$\n\n"
            "### Move 5 — No-slip condition\n"
            "$$f \\leq \\mu_s N_F \\Rightarrow N_W \\leq \\mu_s (m+M)g.$$\n"
            "$$\\boxed{\\mu_{s,\\min} = \\frac{(2m+3M)\\cot\\phi}{4(m+M)}.}$$\n\n"
            "**Physical insight:** As $\\phi$ decreases (ladder more horizontal), $\\cot\\phi$ increases "
            "→ more friction needed. As $M\\to 0$, the formula reduces to $\\mu_{s,\\min}=\\cot\\phi/2$."
        ),
        "body_he_md": (
            "**נתון:** סולם אחיד מסה $m$ ואורך $L$ נשען על קיר חלק בזווית $\\phi$ מהריצפה. "
            "אדם מסה $M$ ב-3/4 מהבסיס. מצאו $\\mu_{s,\\min}$ לרצפה.\n\n"
            "### צעד 1 — דיאגרמת כוחות\n"
            "- $mg$ במרכז ($L/2$ מהבסיס).\n"
            "- $Mg$ ב-$3L/4$ מהבסיס.\n"
            "- $N_W$ (אופקי) בראש הסולם.\n"
            "- $N_F$ (אנכי) ו-$f$ (אופקי) בבסיס.\n\n"
            "### צעד 2 — $\\sum F_x=0$\n"
            "$$f=N_W. \\quad (1)$$\n\n"
            "### צעד 3 — $\\sum F_y=0$\n"
            "$$N_F=(m+M)g. \\quad (2)$$\n\n"
            "### צעד 4 — $\\sum\\tau=0$ סביב הבסיס\n"
            "$$N_W L\\sin\\phi=mg\\frac{L}{2}\\cos\\phi+Mg\\frac{3L}{4}\\cos\\phi.$$\n"
            "$$N_W=\\cot\\phi\\left(\\frac{m}{2}+\\frac{3M}{4}\\right)g.$$\n\n"
            "### צעד 5 — תנאי אי-החלקה\n"
            "$$f\\leq\\mu_s N_F\\Rightarrow N_W\\leq\\mu_s(m+M)g.$$\n"
            "$$\\boxed{\\mu_{s,\\min}=\\frac{(2m+3M)\\cot\\phi}{4(m+M)}.}$$\n\n"
            "**פרשנות:** ככל ש-$\\phi$ קטן (סולם אופקי יותר), $\\cot\\phi$ גדל — "
            "נדרש יותר חיכוך. כש-$M\\to0$: $\\mu_{s,\\min}=\\cot\\phi/2$. "
            "בבחינות, השוו $\\mu_{s,\\min}$ ל-$\\mu_s$ הנתון כדי לקבוע אם הסולם מחליק. "
            "ציר בבסיס הוא הבחירה הסטנדרטית לכל בעיית סולם."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "**Step 1 — Draw FBD and choose pivot at hinge:**\n"
            "Uniform beam: weight $W_b = 12 \\times 10 = 120$ N at CM ($x = 1.5$ m from hinge). "
            "Hanging mass: $W_m = 5 \\times 10 = 50$ N at $x = 3$ m. Rope tension $T$ upward at $x = 2$ m. "
            "Hinge forces have zero moment arm at the pivot.\n\n"
            "**Step 2 — Torque balance (CCW positive):**\n"
            "$$T(2) - W_b(1.5) - W_m(3) = 0.$$\n"
            "$$2T = 120 \\times 1.5 + 50 \\times 3 = 180 + 150 = 330.$$\n"
            "$$T = 165 \\text{ N}.$$\n\n"
            "**Step 3 — Sanity check:**\n"
            "Total downward load = $120 + 50 = 170$ N. The rope at $x=2$ m must support more than half "
            "because the hanging mass is at the far end — $T = 165$ N > 85 N ✓.\n\n"
            "**Answer:** $T = 165$ N."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — דיאגרמת כוחות וציר בצירה:**\n"
            "קורה אחידה: משקל $W_b=120$ נ' במ\"מ ($x=1.5$ מ'). "
            "מסה תלויה: $W_m=50$ נ' ב-$x=3$ מ'. מתח $T$ כלפי מעלה ב-$x=2$ מ'. "
            "כוחות ציר בזרוע אפס.\n\n"
            "**שלב 2 — איזון מומנטים (CCW חיובי):**\n"
            "$$2T=120\\times1.5+50\\times3=180+150=330\\Rightarrow T=165\\text{ נ'}.$$\n\n"
            "**שלב 3 — בדיקת הגיון:**\n"
            "עומס כלפי מטה = 170 נ'. החבל ב-$x=2$ מ' נושא יותר ממחצית (85 נ') "
            "כי המסה 5 ק\"ג תלויה בקצה ($x=3$ מ') — "
            "$T=165$ נ' > 85 נ' ✓.\n\n"
            "**תשובה:** $T=165$ נ'."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "**Step 1 — FBD and pivot at support A ($x=1$ m):**\n"
            "Uniform beam 10 kg → $W_b = 100$ N at CM ($x=3$ m, distance 2 m from A). "
            "Person 20 kg → $W_p = 200$ N at $x=6$ m (distance 5 m from A). "
            "$R_B$ upward at $x=5$ m (distance 4 m from A).\n\n"
            "**Step 2 — Torque about A:**\n"
            "$$R_B(4) = W_b(2) + W_p(5) = 100(2) + 200(5) = 200 + 1000 = 1200.$$\n"
            "$$R_B = 300 \\text{ N}.$$\n\n"
            "**Step 3 — Vertical force balance:**\n"
            "$$R_A + R_B = W_b + W_p = 300 \\text{ N}.$$\n"
            "$$R_A = 300 - 300 = 0 \\text{ N}.$$\n\n"
            "**Physical interpretation:** $R_A = 0$ means the left support is at the tipping threshold — "
            "the beam would lift off A without it. In practice the support must still be present.\n\n"
            "**Answer:** $R_A = 0$ N; $R_B = 300$ N."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — דיאגרמת כוחות וציר בתמיכה A ($x=1$ מ'):**\n"
            "קורה 10 ק\"ג → $W_b=100$ נ' במ\"מ ($x=3$ מ', מרחק 2 מ' מ-A). "
            "אדם 20 ק\"ג → $W_p=200$ נ' ב-$x=6$ מ' (מרחק 5 מ'). "
            "$R_B$ כלפי מעלה ב-$x=5$ מ' (מרחק 4 מ').\n\n"
            "**שלב 2 — מומנט סביב A:**\n"
            "$$4R_B=200+1000=1200\\Rightarrow R_B=300\\text{ נ'}.$$\n\n"
            "**שלב 3 — איזון אנכי:**\n"
            "$$R_A+300=300\\Rightarrow R_A=0\\text{ נ'}.$$\n\n"
            "**פרשנות:** $R_A=0$ = סף התהפכות — הקורה הייתה מתרוממת מ-A בלי התמיכה. "
            "בפועל התמיכה חייבת להישאר.\n\n"
            "**תשובה:** $R_A=0$ נ'; $R_B=300$ נ'."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "Use this decision table on every static equilibrium problem — identifying the setup "
            "first prevents applying the wrong pivot strategy.\n\n"
            "| Situation | Strategy | Key step |\n"
            "|---|---|---|\n"
            "| One hinge + one cable/rope | Pivot at hinge | Cable force has moment arm $r\\sin\\theta$ |\n"
            "| Two vertical supports, known loads | Pivot at one support | Other support force disappears |\n"
            "| Ladder on floor + wall | Pivot at base | Eliminates friction and floor normal |\n"
            "| Weight of non-uniform beam | CM given separately | Weight acts at CM, not centre of beam |\n"
            "| Unknown hinge force | Use $\\sum F=0$ after solving torques | Hinge supplies whatever force is needed |\n\n"
            "**Step-by-step protocol:**\n"
            "1. Draw complete FBD — every force, every reaction.\n"
            "2. Assign coordinate system (x horizontal, y vertical).\n"
            "3. Apply $\\sum F_x = 0$ and $\\sum F_y = 0$.\n"
            "4. Choose pivot at the point with the most unknowns; write $\\sum\\tau = 0$.\n"
            "5. Solve the algebraic system (usually 3 equations, up to 3 unknowns in 2D).\n"
            "6. Verify: re-sum torques about a different point to check consistency."
        ),
        "body_he_md": (
            "השתמשו בטבלת ההחלטה בכל בעיית שיווי משקל — זיהוי ההגדרה קודם "
            "מונע בחירת ציר שגויה.\n\n"
            "| מצב | אסטרטגיה | שלב מפתח |\n"
            "|---|---|---|\n"
            "| ציר + כבל | ציר בצירה | זרוע מומנט הכבל $r\\sin\\theta$ |\n"
            "| שתי תמיכות אנכיות | ציר בתמיכה אחת | השנייה נעלמת |\n"
            "| סולם | ציר בבסיס | חיכוך ונורמל נעלמים |\n"
            "| קורה לא אחידה | מ\"מ נתון | משקל במ\"מ, לא במרכז |\n"
            "| כוח ציר לא ידוע | $\\sum F=0$ אחרי מומנטים | הציר מספק מה שצריך |\n\n"
            "**פרוטוקול שלב-שלב:**\n"
            "1. דיאגרמת כוחות מלאה — כל כוח ותגובה.\n"
            "2. מערכת צירים ($x$ אופקי, $y$ אנכי).\n"
            "3. $\\sum F_x=0$, $\\sum F_y=0$.\n"
            "4. ציר בנקודה עם הכי הרבה נעלמים; $\\sum\\tau=0$.\n"
            "5. פתרו (בדרך כלל 3 משוואות, 3 נעלמים).\n"
            "6. אמתו ב-$\\sum\\tau=0$ סביב ציר **אחר**."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below. **Try each one before opening the solution** — "
            "the steps matter as much as the final answer. For each problem, first draw a complete FBD "
            "labeling every force, then choose your pivot strategically to eliminate unknown hinge or "
            "support reactions before writing any equation. "
            "Check $\\sum F=0$ and $\\sum\\tau=0$ (about a second pivot) after every solution to catch sign errors. "
            "Problems e5–e8 combine hinged beams, ladders, and non-uniform loads — "
            "the same two equilibrium conditions apply throughout. Start with e1–e4 to build confidence "
            "before tackling multi-part hinge and friction problems."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "הצעדים חשובים לא פחות מהתשובה. בכל בעיה, קודם שרטטו דיאגרמת כוחות מלאה "
            " עם תווית לכל כוח, ואז בחרו ציר אסטרטגי לסילוק תגובות ציר או תמיכה "
            "לפני כתיבת משוואות. "
            "אמתו $\\sum F=0$ ו-$\\sum\\tau=0$ (סביב ציר שני) אחרי כל פתרון לתפיסת שגיאות סימן. "
            "תרגילים e5–e8 משלבים קורות ציריות, סולמות ועומסים לא אחידים — "
            "אותם שני תנאי שיווי משקל בכל מקרה. התחילו מ-e1–e4 לפני בעיות ציר וחיכוך רב-שלביות."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting to include all forces in the FBD.** Every force must appear: normal forces, "
            "friction, cable tensions, weight of the beam itself, and hinge reactions ($H_x$ and $H_y$). "
            "Missing one force leads to wrong answers that no amount of algebra can fix.\n\n"
            "2. **Using the wrong moment arm.** The moment arm is the **perpendicular** distance from "
            "the pivot to the **line of action** of the force. For a cable at angle $\\theta$, use "
            "$r\\sin\\theta$, not the full length $r$.\n\n"
            "3. **Weight of the beam acting at the end, not the CM.** For a uniform beam, weight acts "
            "at the geometric centre. For a non-uniform beam, use the given CM location — never assume $L/2$.\n\n"
            "4. **Not recognizing that hinges supply both horizontal and vertical force.** A hinge is a "
            "pin joint: it provides $H_x$ **and** $H_y$ in 2D. Always include both in the FBD.\n\n"
            "5. **Wrong sign in torque equation.** Define CCW or CW as positive and stick to it. "
            "Mixing signs mid-problem is the most common source of wrong magnitudes."
        ),
        "body_he_md": (
            "1. **שכחת כוחות בדיאגרמה.** כל כוח חייב להופיע: נורמל, חיכוך, מתח, משקל הקורה, "
            "ותגובת ציר ($H_x$ **ו**-$H_y$). כוח חסר = תשובה שגויה שלא תתוקן באלגברה.\n\n"
            "2. **זרוע מומנט שגויה.** זרוע המומנט = המרחק **הניצב** מקו הפעולה. "
            "בכבל בזווית $\\theta$: $r\\sin\\theta$, לא $r$.\n\n"
            "3. **משקל קורה בקצה, לא במ\"מ.** קורה אחידה: מ\"מ גיאומטרי. "
            "לא אחידה: מ\"מ נתון — אל תניחו $L/2$.\n\n"
            "4. **ציר מספק רק כוח אנכי.** ציר פין: $H_x$ **ו**-$H_y$ ב-2D. "
            "כלולו שניהם בדיאגרמה.\n\n"
            "5. **סימן מומנט הפוך.** הגדירו CCW או CW כחיובי והיצמדו. "
            "ערבוב סימנים באמצע = מקור #1 לטעויות."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Static equilibrium is the foundation of **structural mechanics** — every building, bridge, "
            "crane, and shelf you encounter was analysed with $\\sum F=0$ and $\\sum\\tau=0$.\n\n"
            "**Builds on:**\n"
            "- `concept:torque` — moment arms and sign conventions\n"
            "- `concept:newton_laws` — force balance as $\\sum F=ma$ with $a=0$\n"
            "- `concept:friction` — ladder problems combine equilibrium with $f \\leq \\mu N$\n\n"
            "**Unlocks:**\n"
            "- `concept:rotational_dynamics` — when equilibrium fails, angular acceleration begins\n"
            "- `concept:center_of_mass` — stability requires CM over the support base\n"
            "- Engineering statics courses (trusses, frames, distributed loads)\n\n"
            "**Why it matters for exams:** Bagrut and university mechanics reward recognizing the setup "
            "(hinge + cable, two supports, ladder) and choosing the pivot **before** writing equations. "
            "One clever pivot can save several minutes on a timed exam."
        ),
        "body_he_md": (
            "שיווי משקל סטטי הוא הבסיס ל**מכניקת מבנים** — כל בניין, גשר, מנוף ומדף "
            "נותחו עם $\\sum F=0$ ו-$\\sum\\tau=0$.\n\n"
            "**מבוסס על:**\n"
            "- `concept:torque` — זרועות מומנט וסימנים\n"
            "- `concept:newton_laws` — איזון כוחות כ-$\\sum F=ma$ עם $a=0$\n"
            "- `concept:friction` — סולמות משלבים שיווי משקל עם $f\\leq\\mu N$\n\n"
            "**פותח:**\n"
            "- `concept:rotational_dynamics` — כששיווי משקל נכשל, מתחילה האצה זוויתית\n"
            "- `concept:center_of_mass` — יציבות דורשת מ\"מ מעל בסיס התמיכה\n"
            "- קורסי סטטיקה הנדסית (קורות, מסגרות, עומסים מפוזרים)\n\n"
            "**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים זיהוי ההגדרה "
            "(ציר+כבל, שתי תמיכות, סולם) ובחירת ציר **לפני** משוואות. "
            "ציר חכם אחד חוסך דקות בשאלון."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "### Essential Formulas\n"
            "- **Translational equilibrium:** $\\sum F_x = 0$, $\\sum F_y = 0$\n"
            "- **Rotational equilibrium:** $\\sum\\tau = 0$ (any pivot)\n"
            "- **Torque:** $\\tau = rF\\sin\\phi = r_\\perp F$\n"
            "- **Stability:** CM must lie over base of support\n"
            "- **Ladder:** $\\mu_{s,\\min} = N_W / N_F$ after finding $N_W$ from torques\n\n"
            "### Typical Exam Questions\n"
            "1. Beam on two supports — find reaction forces.\n"
            "2. Hinged beam with cable — find tension and hinge force.\n"
            "3. Ladder problem — find minimum friction coefficient.\n"
            "4. Torque with an angle — identify correct moment arm $r\\sin\\theta$.\n"
            "5. Non-uniform beam with specified CM — weight acts at CM.\n\n"
            "### Marking Criteria\n"
            "- Complete FBD with all forces: 25%\n"
            "- Correct choice of pivot (efficiency): 15%\n"
            "- Torque equation correct: 30%\n"
            "- Correct force equations: 20%\n"
            "- Final answer with correct units: 10%"
        ),
        "body_he_md": (
            "### נוסחאות חיוניות\n"
            "- $\\sum F_x=0$, $\\sum F_y=0$ — שיווי משקל תנועתי\n"
            "- $\\sum\\tau=0$ — שיווי משקל סיבובי (כל ציר)\n"
            "- $\\tau=rF\\sin\\phi=r_{\\perp}F$ — מומנט\n"
            "- יציבות: מ\"מ מעל בסיס התמיכה\n"
            "- סולם: $\\mu_{s,\\min}=N_W/N_F$ אחרי מציאת $N_W$ ממומנטים\n\n"
            "### תבניות שאלות\n"
            "1. קורה + שתי תמיכות — כוחות תגובה.\n"
            "2. קורה צירית + כבל — מתח וכוח ציר.\n"
            "3. סולם — $\\mu_{s,\\min}$.\n"
            "4. מומנט עם זווית — זרוע $r\\sin\\theta$.\n"
            "5. קורה לא אחידה — משקל במ\"מ הנתון.\n\n"
            "### קריטריוני ניקוד\n"
            "- דיאגרמת כוחות מלאה: 25%\n"
            "- בחירת ציר נכונה: 15%\n"
            "- משוואת מומנט: 30%\n"
            "- משוואות כוח: 20%\n"
            "- תשובה + יחידות: 10%"
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Two conditions:** $\\sum F=0$ (no acceleration) and $\\sum\\tau=0$ (no angular acceleration).\n"
            "- **Torque:** $\\tau = rF\\sin\\phi = r_\\perp F$; CCW positive, CW negative.\n"
            "- **Pivot choice:** Place pivot at the point of application of the unknown force you want to eliminate.\n"
            "- **Weight of beam:** acts at the CM (centre for uniform beams).\n"
            "- **Hinge:** provides two force components ($H_x$, $H_y$); solve from $\\sum F=0$ after solving torques.\n"
            "- **Ladder:** $N_W = \\cot\\phi \\cdot (\\text{loads} \\times \\text{arms})/L$; $\\mu_{s,\\min} = N_W/N_F$.\n"
            "- **Always verify** by re-summing torques about a different pivot."
        ),
        "body_he_md": (
            "- **שני תנאים:** $\\sum F=0$ (ללא האצה), $\\sum\\tau=0$ (ללא סיבוב).\n"
            "- **מומנט:** $\\tau=rF\\sin\\phi$; CCW חיובי, CW שלילי.\n"
            "- **בחירת ציר:** בנקודת כוח לא ידוע לסילוקו.\n"
            "- **משקל קורה:** פועל במ\"מ (מרכז לקורה אחידה).\n"
            "- **ציר:** $H_x$ ו-$H_y$; מ-$\\sum F=0$ אחרי מומנטים.\n"
            "- **סולם:** $N_W$ ממומנטים; $\\mu_{s,\\min}=N_W/N_F$.\n"
            "- **תמיד אמתו** ב-$\\sum\\tau=0$ סביב ציר אחר."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "For a uniform 2 m rod, the CM is at $x=1$ m — exactly at the midpoint support. "
            "Pivot at the left end: $R_{mid} \\times 1 = mg \\times 1$, so $R_{mid} = 50$ N. "
            "Then $\\sum F_y$: $R_{left} + 50 = 50$, giving $R_{left} = 0$ N.\n\n"
            "**How to think about it:**\n"
            "When the CM sits directly above an interior support, that support carries the entire weight. "
            "The end support may carry zero — this is a limiting case, not an error.\n\n"
            "**Common slip:**\n"
            "Assuming both supports share the load equally (25 N each). Placing weight at the geometric "
            "centre of a uniform rod, not at the end.\n\n"
            "**Exam tip:**\n"
            "Always locate the CM first for uniform objects. A zero reaction force is valid when the "
            "load distribution places all weight on the interior support."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "למוט אחיד 2 מ', מ\"מ ב-$x=1$ מ' — בדיוק בתמיכת האמצע. "
            "ציר בשמאל: $R_{\\text{אמצע}}\\times1=mg\\times1$, אז $R_{\\text{אמצע}}=50$ נ'. "
            "$\\sum F_y$: $R_{\\text{שמאל}}+50=50$, $R_{\\text{שמאל}}=0$ נ'.\n\n"
            "**איך לחשוב על זה:**\n"
            "כש-מ\"מ מעל תמיכה פנימית, התמיכה נושאת את כל המשקל. "
            "תמיכת הקצה יכולה להיות אפס — מקרה גבול, לא טעות.\n\n"
            "**טעות נפוצה:**\n"
            "הנחה ששתי התמיכות חולקות שווה (25 נ' כל אחת). "
            "הנחת משקל בקצה במקום במ\"מ.\n\n"
            "**טיפ לבחינה:**\n"
            "מצאו תמיד מ\"מ קודם. תגובה אפס תקפה כשכל העומס על התמיכה הפנימית."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Pivot at hinge eliminates hinge forces. $\\sum\\tau=0$: "
            "$T(1.5) = W_{rod}(1) + W_{sign}(2) = 10 + 80 = 90$, so $T = 60$ N.\n\n"
            "**How to think about it:**\n"
            "Two downward loads (rod weight at its CM, sign at the end) create CW torques. "
            "The vertical cable at $x=1.5$ m produces CCW torque. Include **both** weights in the FBD.\n\n"
            "**Common slip:**\n"
            "Forgetting the rod's own weight (only counting the 4 kg sign). "
            "Using full cable length 2 m as moment arm instead of attachment point 1.5 m.\n\n"
            "**Exam tip:**\n"
            "In \"sign on rod\" problems, always ask: does the rod itself have mass? "
            "If yes, its weight acts at the rod's CM, not at the sign."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ציר בצירה מסלק כוחות ציר ממשוואת המומנט. $\\sum\\tau=0$: "
            "$T(1.5)=W_{\\text{מוט}}(1)+W_{\\text{שלט}}(2)=10+80=90$, ולכן $T=60$ נ'.\n\n"
            "**איך לחשוב על זה:**\n"
            "שני עומסים כלפי מטה (משקל מוט 1 ק\"ג במ\"מ $x=1$ מ', שלט 4 ק\"ג בקצה $x=2$ מ') "
            "יוצרים מומנטים CW. חבל אנכי ב-$x=1.5$ מ' יוצר CCW. "
            "כלולו **שני** המשקלים — טעות נפוצה היא לספור רק את השלט.\n\n"
            "**טעות נפוצה:**\n"
            "שכחת משקל המוט (רק 4 ק\"ג שלט). "
            "שימוש באורך 2 מ' במקום נקודת החיבור 1.5 מ' כזרוע מומנט.\n\n"
            "**טיפ לבחינה:**\n"
            "ב\"שלט על מוט\" — שאלו: למוט יש מסה? אם כן, משקלו במ\"מ ($L/2$), לא בשלט."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Pivot at left end. $\\sum\\tau=0$: "
            "$R_B(5) = W_{plank}(2.5) + W_{block}(1) = 80(2.5) + 150(1) = 350$, "
            "so $R_B = 70$ N. Then $\\sum F_y$: $R_A = 230 - 70 = 160$ N.\n\n"
            "**How to think about it:**\n"
            "The 15 kg block at $x=1$ m is close to the left support, so $R_A$ must be large. "
            "The right support carries less because the block is far from it.\n\n"
            "**Common slip:**\n"
            "Using $x=2.5$ m for the block (confusing with plank CM). "
            "Forgetting plank weight and only counting the block.\n\n"
            "**Exam tip:**\n"
            "After finding both reactions, verify $R_A + R_B$ equals total weight. "
            "This 30-second check catches most arithmetic errors."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ציר בקצה שמאל. $\\sum\\tau=0$: "
            "$5R_B=8(10)(2.5)+15(10)(1)=200+150=350$, $R_B=70$ נ'. "
            "אז $\\sum F_y=0$: $R_A=80+150-70=160$ נ'.\n\n"
            "**איך לחשוב על זה:**\n"
            "בלוק 15 ק\"ג ב-$x=1$ מ' קרוב לתמיכה שמאל — $R_A$ גדול (160 נ'). "
            "תמיכה ימין נושאת פחות (70 נ') כי הבלוק רחוק ממנה. "
            "משקל הקרש 8 ק\"ג פועל במ\"מ $x=2.5$ מ'.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש ב-$x=2.5$ מ' לבלוק (בלבול עם מ\"מ קרש). "
            "שכחת משקל הקרש וספירת רק הבלוק 15 ק\"ג.\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי מציאת $R_A$ ו-$R_B$, אמתו $R_A+R_B=230$ נ' = משקל כולל — "
            "בדיקה של 30 שניות שתופסת רוב שגיאות החישוב."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Pivot at left. $\\sum\\tau=0$: "
            "$R_R(4) = W_{beam}(2) + W_{load}(1) = 600 + 700 = 1300$, "
            "so $R_R = 325$ N. Then $R_L = 300 + 700 - 325 = 675$ N.\n\n"
            "**How to think about it:**\n"
            "The 700 N load at $x=1$ m is near the left end, so the left reaction ($R_L=675$ N) "
            "exceeds the right ($R_R=325$ N). Beam CM at $x=2$ m contributes equally to both sides.\n\n"
            "**Common slip:**\n"
            "Placing beam weight at $x=1$ m (the load position) instead of CM at $x=2$ m. "
            "Using load distance 4 m instead of 1 m from the left pivot.\n\n"
            "**Exam tip:**\n"
            "Label three torques separately: beam weight at CM, external load at its position, "
            "and the unknown reaction at its support point."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ציר בשמאל. $\\sum\\tau=0$: "
            "$4R_R=300(2)+700(1)=600+700=1300$, $R_R=325$ נ'. "
            "אז $R_L=300+700-325=675$ נ'.\n\n"
            "**איך לחשוב על זה:**\n"
            "עומס 700 נ' ב-$x=1$ מ' קרוב לשמאל — $R_L=675$ נ' > $R_R=325$ נ'. "
            "משקל קורה 300 נ' פועל במ\"מ $x=2$ מ' (לא ב-$x=1$ מ'!). "
            "ספרו שלושה מומנטים: קורה, עומס, תגובה.\n\n"
            "**טעות נפוצה:**\n"
            "משקל קורה ב-$x=1$ מ' (מיקום העומס) במקום מ\"מ ב-$x=2$ מ'. "
            "מרחק עומס 4 מ' מהציר במקום 1 מ'.\n\n"
            "**טיפ לבחינה:**\n"
            "בקורה אחידה, מ\"מ תמיד $L/2$. סמנו שלושה מומנטים בנפרד "
            "לפני כתיבת $\\sum\\tau=0$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Pivot at hinge. $\\sum\\tau=0$: "
            "$T\\sin45° \\times 3 = 10(10)(1.5) + 20(10)(2) = 150 + 400 = 550$. "
            "$T = 550/(3 \\times 0.707) \\approx 259$ N. "
            "Hinge: $H_x = T\\cos45° \\approx 183$ N; $H_y = 300 - T\\sin45° \\approx 117$ N.\n\n"
            "**How to think about it:**\n"
            "Two loads (beam + box) create CW torques. Only the vertical component $T\\sin45°$ "
            "produces CCW torque. Find $T$ from torques first, then hinge forces from $\\sum F=0$.\n\n"
            "**Common slip:**\n"
            "Using $T$ instead of $T\\sin45°$ in the torque equation. "
            "Forgetting the 20 kg box at $x=2$ m.\n\n"
            "**Exam tip:**\n"
            "Hinge + cable problems always follow: (1) pivot at hinge, (2) find $T$, "
            "(3) find $H_x$ and $H_y$. This sequence appears on every Bagrut mechanics section."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ציר בצירה. $\\sum\\tau=0$ (CCW חיובי): "
            "$T\\sin45°\\times3=10(10)(1.5)+20(10)(2)=150+400=550$. "
            "$T=550/(3\\times0.707)\\approx259$ נ'. "
            "ציר: $H_x=T\\cos45°\\approx183$ נ'; $H_y=300-T\\sin45°\\approx117$ נ'.\n\n"
            "**איך לחשוב על זה:**\n"
            "שני עומסים (קורה 10 ק\"ג במ\"מ + קופסה 20 ק\"ג ב-$x=2$ מ') יוצרים CW. "
            "רק הרכיב האנכי $T\\sin45°$ יוצר CCW. "
            "סדר: (1) $T$ ממומנטים, (2) $H_x$ ו-$H_y$ מ-$\\sum F=0$.\n\n"
            "**טעות נפוצה:**\n"
            "$T$ במקום $T\\sin45°$ במשוואת מומנט. שכחת קופסה 20 ק\"ג.\n\n"
            "**טיפ לבחינה:**\n"
            "בעיות ציר+כבל חוזרות בבגרות — שלושה שלבים קבועים: "
            "ציר בצירה, מציאת $T$, מציאת כוחות ציר."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Pivot at base. $\\sum\\tau=0$: "
            "$N_W \\times L\\sin60° = (m+M)g \\times (L/2)\\cos60°$. "
            "$N_W \\approx 39.5$ N. From $\\sum F_x=0$: $f = N_W$. "
            "$N_F = 820$ N, so $\\mu_{s,req} = 39.5/820 \\approx 0.048$. "
            "Since $0.048 < 0.3$, $\\mu_s = 0.3$ is sufficient.\n\n"
            "**How to think about it:**\n"
            "Ladder problems: pivot at base eliminates $N_F$ and $f$. "
            "Wall is smooth → only horizontal $N_W$. Compare required $\\mu$ to given value.\n\n"
            "**Common slip:**\n"
            "Using $\\sin60°$ for horizontal moment arm of weights (should be $\\cos60°$). "
            "Forgetting the person's weight at half the ladder length.\n\n"
            "**Exam tip:**\n"
            "Always state clearly whether $\\mu_s$ is sufficient by comparing numbers: "
            "$\\mu_{given} > \\mu_{required}$ means no slipping."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ציר בבסיס הסולם. $\\sum\\tau=0$: "
            "$N_W\\times L\\sin60°=(12+70)/2\\times10\\times0.5=205$ N·m, "
            "$N_W\\approx39.5$ נ'. מ-$\\sum F_x=0$: $f=N_W$. "
            "$N_F=820$ נ', $\\mu_{s,req}=39.5/820\\approx0.048<0.3$ — מספיק.\n\n"
            "**איך לחשוב על זה:**\n"
            "בעיית סולם: ציר בבסיס מסלק $N_F$ ו-$f$. קיר חלק → רק $N_W$ אופקי. "
            "זרוע אופקית של משקלים: $(L/2)\\cos60°$. "
            "השוו $\\mu$ נדרש ל-$\\mu_s=0.3$ הנתון.\n\n"
            "**טעות נפוצה:**\n"
            "$\\sin60°$ לזרוע אופקית (צריך $\\cos60°$). "
            "שכחת משקל האדם 70 ק\"ג בחצי הסולם.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו במפורש: $\\mu_{נתון}>\\mu_{נדרש}$ → הסולם **לא** מחליק. "
            "אם $\\mu_{נדרש}>\\mu_{נתון}$, הסולם יחליק."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Equal supports means $R_A = R_B = (20+40)(10)/2 = 300$ N. "
            "Pivot at left: $R_B(5) = 20(10)(2) + 40(10)(x) = 400 + 400x$. "
            "$1500 = 400 + 400x$, so $x = 2.75$ m from the left end.\n\n"
            "**How to think about it:**\n"
            "This is an inverse problem: instead of finding reactions, find load position. "
            "Use the symmetry condition ($R_A = R_B$) to get the target reaction, "
            "then solve the torque equation for position $x$.\n\n"
            "**Common slip:**\n"
            "Using CM at $L/2 = 2.5$ m for the non-uniform beam (given CM is at 2 m). "
            "Setting $R_A = R_B$ without computing the value first.\n\n"
            "**Exam tip:**\n"
            "Inverse equilibrium problems (find position, not force) appear regularly. "
            "Write the torque equation with $x$ as the unknown and solve algebraically."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "תמיכות שוות: $R_A=R_B=(20+40)(10)/2=300$ נ'. "
            "ציר בשמאל: $5R_B=20(10)(2)+40(10)(x)=400+400x$. "
            "$1500=400+400x$, $x=2.75$ מ' מהקצה השמאלי.\n\n"
            "**איך לחשוב על זה:**\n"
            "בעיה **הפוכה**: מציאת מיקום, לא כוח. "
            "קורה **לא אחידה** — מ\"מ ב-$x=2$ מ', לא ב-$L/2=2.5$ מ'. "
            "השתמשו ב-$R_A=R_B$ לקביעת $R_B=300$ נ', "
            "ואז $\\sum\\tau=0$ עם $x$ כנעלם.\n\n"
            "**טעות נפוצה:**\n"
            "מ\"מ ב-$2.5$ מ' (הנחת קורה אחידה). "
            "כתיבת $R_A=R_B$ בלי חישוב הערך 300 נ'.\n\n"
            "**טיפ לבחינה:**\n"
            "בעיות \"היכן להניח\" חוזרות — כתבו $\\sum\\tau=0$ "
            "עם $x$ כנעלם ופתרו אלגברית."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Pivot at hinge. $\\sum\\tau=0$: "
            "$T\\sin30° \\times 3 = W_{boom}(1.5) + W_{load}(3) = 300 + 1200 = 1500$. "
            "$T(0.5)(3) = 1500$, so $T = 1000$ N. "
            "$H_x = T\\cos30° = 866$ N; $H_y = 600 - 500 = 100$ N upward.\n\n"
            "**How to think about it:**\n"
            "Boom weight at its CM ($L/2 = 1.5$ m) plus tip load at $L = 3$ m. "
            "Both create CW torques. Cable at 30° contributes $T\\sin30°$ vertically.\n\n"
            "**Common slip:**\n"
            "Using $T$ instead of $T\\sin30°$ for torque. "
            "Placing boom weight at the tip instead of at $L/2$.\n\n"
            "**Exam tip:**\n"
            "After finding $H_x$ and $H_y$, you can compute $|H| = \\sqrt{H_x^2 + H_y^2}$ "
            "if the question asks for hinge force magnitude — a common follow-up on exams."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ציר בצירה. $\\sum\\tau=0$ (CCW חיובי): "
            "$T\\sin30°\\times3=200(1.5)+400(3)=300+1200=1500$. "
            "$T(0.5)(3)=1500$, $T=1000$ נ'. "
            "$H_x=T\\cos30°=866$ נ'; $H_y=600-T\\sin30°=100$ נ' כלפי מעלה.\n\n"
            "**איך לחשוב על זה:**\n"
            "משקל זרוע 200 נ' במ\"מ ($L/2=1.5$ מ') + עומס 400 נ' בקצה ($L=3$ מ'). "
            "שניהם CW. כבל ב-30° תורם $T\\sin30°$ אנכית — "
            "לא $T$ המלא.\n\n"
            "**טעות נפוצה:**\n"
            "$T$ במקום $T\\sin30°$ במומנט. "
            "משקל זרוע בקצה ($x=3$ מ') במקום במ\"מ ($x=1.5$ מ').\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי $H_x$ ו-$H_y$, $|H|=\\sqrt{H_x^2+H_y^2}\\approx870$ נ' — "
            "שאלת המשך נפוצה על גודל כוח הציר."
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
        if kind == "checkpoint":
            for field, lang in (
                ("checkpoint_solution_en", "en"),
                ("checkpoint_solution_he", "he"),
            ):
                w = word_count(sec.get(field, ""))
                if w < MIN_WORDS["checkpoint"][lang]:
                    issues.append(f"checkpoint {field}: {w}")
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
        elif kind in MIN_WORDS:
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
