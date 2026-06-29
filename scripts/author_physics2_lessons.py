#!/usr/bin/env python3
"""Author university Physics 2 (E&M) lessons and update index files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
INDEX_PATH = ROOT / "apps" / "web" / "src" / "lib" / "lessons-index.generated.json"
CURRICULUM_PATH = ROOT / "apps" / "web" / "src" / "lib" / "curriculum-categories.ts"

LESSON_IDS = [
    "electric_field_gauss",
    "magnetic_field_biot_savart",
    "ampere_law",
    "maxwell_equations",
    "faraday_induction_uni",
]

INDEX_ENTRIES = {
    "electric_field_gauss": {
        "title_en": "Electric Field and Gauss's Law (University)",
        "title_he": "שדה חשמלי וחוק גאוס (אוניברסיטה)",
        "duration_min": 24,
    },
    "magnetic_field_biot_savart": {
        "title_en": "Magnetic Fields — Biot-Savart Law (University)",
        "title_he": "שדות מגנטיים — חוק Biot-Savart (אוניברסיטה)",
        "duration_min": 25,
    },
    "ampere_law": {
        "title_en": "Ampère's Law and Symmetric Currents (University)",
        "title_he": "חוק אמפר וזרמים סימטריים (אוניברסיטה)",
        "duration_min": 23,
    },
    "maxwell_equations": {
        "title_en": "Maxwell's Equations and EM Waves (University)",
        "title_he": "משוואות מаксוול וגלים אלקטרומגנטיים (אוניברסיטה)",
        "duration_min": 26,
    },
    "faraday_induction_uni": {
        "title_en": "Faraday's Law — Electromagnetic Induction (University)",
        "title_he": "חוק פאראדיי — השראה אלקטרומגנטית (אוניברסיטה)",
        "duration_min": 25,
    },
}


def _mcq(qid, body_en, body_he, options, expl_en, expl_he):
    return {
        "id": qid,
        "type": "mcq",
        "body_en": body_en,
        "body_he": body_he,
        "options": options,
        "explanation_en": expl_en,
        "explanation_he": expl_he,
    }


def _section(sid, title_en, title_he, body_en_md, body_he_md):
    return {
        "id": sid,
        "title_en": title_en,
        "title_he": title_he,
        "body_en_md": body_en_md,
        "body_he_md": body_he_md,
        "level_min": "university",
    }


def build_lessons() -> list[dict]:
    return LESSONS


# ---------------------------------------------------------------------------
# Lesson definitions
# ---------------------------------------------------------------------------

LESSONS: list[dict] = [
    {
        "id": "electric_field_gauss",
        "subject": "university_physics_2",
        "title_en": "Electric Field and Gauss's Law (University)",
        "title_he": "שדה חשמלי וחוק גאוס (אוניברסיטה)",
        "duration_min": 24,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Students confuse flux with field strength — flux depends on orientation via "
            "$\\mathbf{E}\\cdot d\\mathbf{A}$. Emphasize that Gauss's law is always true but "
            "only useful when symmetry makes $\\oint \\mathbf{E}\\cdot d\\mathbf{A}$ trivial. "
            "For conductors in equilibrium: $\\mathbf{E}=0$ inside, charge resides on surface. "
            "Inside a uniformly charged solid sphere at $r<R$: $E(r)=kQr/R^3$, so at $r=R/2$ "
            "we get $E=kQ/(2R^2)$, not $kQ/R^2$."
        ),
        "sections": [
            _section(
                "electric_flux",
                "Electric Flux — Surface Integral Definition",
                "שטף חשמלי — הגדרה אינטגרלית על פני שטח",
                (
                    "The **electric flux** through a surface $S$ measures how much of the "
                    "electric field 'passes through' that surface:\n"
                    "$$\\Phi_E = \\int_S \\mathbf{E} \\cdot d\\mathbf{A}$$\n\n"
                    "For a **uniform** field $\\mathbf{E}$ and flat area $\\mathbf{A}$ "
                    "(with $\\theta$ the angle between $\\mathbf{E}$ and the outward normal):\n"
                    "$$\\Phi_E = E A \\cos\\theta = \\mathbf{E}\\cdot\\mathbf{A}$$\n\n"
                    "**Closed surface:** take $d\\mathbf{A}$ outward. Flux is positive when "
                    "$\\mathbf{E}$ points outward through the surface.\n\n"
                    "**Dipole in a cube:** field lines enter one face and exit another; net "
                    "flux through a closed surface enclosing no net charge is zero."
                ),
                (
                    "**שטף חשמלי** דרך פני שטח $S$ מודד כמה מהשדה החשמלי 'עובר' דרך הפני שטח:\n"
                    "$$\\Phi_E = \\int_S \\mathbf{E} \\cdot d\\mathbf{A}$$\n\n"
                    "עבור שדה **אחיד** $\\mathbf{E}$ ושטח שטוח $\\mathbf{A}$ "
                    "(כאשר $\\theta$ הזווית בין $\\mathbf{E}$ לנורמל החיצוני):\n"
                    "$$\\Phi_E = E A \\cos\\theta = \\mathbf{E}\\cdot\\mathbf{A}$$\n\n"
                    "**פני שטח סגורים:** $d\\mathbf{A}$ כיוון החוצה. שטף חיובי כאשר "
                    "$\\mathbf{E}$ מצביע החוצה.\n\n"
                    "**דיפול בתוך קוב:** קווי השדה נכנסים ויוצאים; השטף הנקי "
                    "דרך פני שטח סגורים ללא מטען נקי הוא אפס."
                ),
            ),
            _section(
                "gauss_law_integral",
                "Gauss's Law — Integral Form",
                "חוק גאוס — צורה אינטגרלית",
                (
                    "Gauss's law relates the flux through any **closed** Gaussian surface "
                    "to the enclosed charge:\n"
                    "$$\\boxed{\\oint_S \\mathbf{E}\\cdot d\\mathbf{A} = \\frac{Q_{\\text{enc}}}{\\varepsilon_0}}$$\n\n"
                    "Equivalent differential form (divergence theorem):\n"
                    "$$\\nabla\\cdot\\mathbf{E} = \\frac{\\rho}{\\varepsilon_0}$$\n\n"
                    "Gauss's law is **exact** for any charge distribution. It becomes a "
                    "**calculation tool** only when symmetry implies $\\mathbf{E}$ is constant "
                    "in magnitude and normal to the Gaussian surface.\n\n"
                    "**Coulomb's law recovery:** apply to a sphere of radius $r$ around "
                    "point charge $Q$; by symmetry $E(r)=\\dfrac{1}{4\\pi\\varepsilon_0}\\dfrac{Q}{r^2}$."
                ),
                (
                    "חוק גאוס קושר את השטף דרך **כל** פני שטח גאוסי סגור למטען הסגור:\n"
                    "$$\\boxed{\\oint_S \\mathbf{E}\\cdot d\\mathbf{A} = \\frac{Q_{\\text{enc}}}{\\varepsilon_0}}$$\n\n"
                    "צורה דיפרנציאלית (משפט הדיברגנציה):\n"
                    "$$\\nabla\\cdot\\mathbf{E} = \\frac{\\rho}{\\varepsilon_0}$$\n\n"
                    "חוק גאוס **מדויק** לכל התפלגות מטען. הוא **כלי חישוב** רק כאשר "
                    "הסימטריה גורמת ל-$\\mathbf{E}$ להיות קבוע בגודל ונורמלי לפני השטח.\n\n"
                    "**שחזור חוק קולון:** יישום על כדור ברדיוס $r$ סביב מטען נקודתי $Q$."
                ),
            ),
            _section(
                "gaussian_surface_choice",
                "Choosing a Gaussian Surface",
                "בחירת פני שטח גאוסיים",
                (
                    "**Strategy:** match the symmetry of the charge distribution.\n\n"
                    "| Symmetry | Gaussian surface | Field direction |\n"
                    "|---|---|---|\n"
                    "| Infinite plane ($\\sigma$) | Pillbox straddling plane | Normal to plane |\n"
                    "| Infinite line ($\\lambda$) | Cylinder coaxial with line | Radial, $\\hat{\\mathbf{r}}$ |\n"
                    "| Sphere ($Q$ or $\\rho$) | Concentric sphere | Radial |\n\n"
                    "On the chosen surface: $|\\mathbf{E}|$ is constant and "
                    "$\\mathbf{E}\\parallel d\\mathbf{A}$ (or zero on end caps).\n\n"
                    "Then $\\oint \\mathbf{E}\\cdot d\\mathbf{A} = E\\cdot A_{\\text{relevant}}$."
                ),
                (
                    "**אסטרטגיה:** התאמת פני השטח לסימטריה של המטען.\n\n"
                    "| סימטריה | פני שטח גאוסיים | כיוון השדה |\n"
                    "|---|---|---|\n"
                    "| מישור אינסופי ($\\sigma$) | גלילון חוצה את המישור | נורמלי למישור |\n"
                    "| קו אינסופי ($\\lambda$) | גליל קואקסיאלי | רדיאלי, $\\hat{\\mathbf{r}}$ |\n"
                    "| כדור ($Q$ או $\\rho$) | כדור קונצנטרי | רדיאלי |\n\n"
                    "על פני השטח הנבחר: $|\\mathbf{E}|$ קבוע ו-$\\mathbf{E}\\parallel d\\mathbf{A}$.\n\n"
                    "אז $\\oint \\mathbf{E}\\cdot d\\mathbf{A} = E\\cdot A_{\\text{relevant}}$."
                ),
            ),
            _section(
                "gauss_applications",
                "Applications — Plane, Line, and Sphere",
                "יישומים — מישור, קו וכדור",
                (
                    "**Infinite charged plane** (surface charge density $\\sigma$):\n"
                    "$$E = \\frac{\\sigma}{2\\varepsilon_0} \\quad \\text{(each side)}$$\n\n"
                    "**Infinite line** ($\\lambda$ C/m), cylindrical Gaussian surface radius $r$:\n"
                    "$$E(r) = \\frac{\\lambda}{2\\pi\\varepsilon_0 r}$$\n\n"
                    "**Solid sphere**, uniform volume charge density $\\rho$, total charge $Q=\\frac{4}{3}\\pi R^3\\rho$:\n"
                    "- Outside ($r\\ge R$): $E = \\dfrac{1}{4\\pi\\varepsilon_0}\\dfrac{Q}{r^2}$\n"
                    "- Inside ($r<R$): only enclosed charge $Q_{\\text{enc}}=\\rho\\cdot\\frac{4}{3}\\pi r^3$:\n"
                    "$$E(r) = \\frac{\\rho r}{3\\varepsilon_0} = \\frac{kQr}{R^3}$$\n"
                    "At $r=R/2$: $\\boxed{E = \\dfrac{kQ}{2R^2}}$."
                ),
                (
                    "**מישור טעון אינסופי** (צפיפות $\\sigma$):\n"
                    "$$E = \\frac{\\sigma}{2\\varepsilon_0}$$\n\n"
                    "**קו אינסופי** ($\\lambda$), גליל ברדיוס $r$:\n"
                    "$$E(r) = \\frac{\\lambda}{2\\pi\\varepsilon_0 r}$$\n\n"
                    "**כדור מלא**, צפיפות נפח $\\rho$, מטען כולל $Q$:\n"
                    "- מחוץ ($r\\ge R$): $E = \\dfrac{1}{4\\pi\\varepsilon_0}\\dfrac{Q}{r^2}$\n"
                    "- בפנים ($r<R$): מטען סגור $Q_{\\text{enc}}=\\rho\\cdot\\frac{4}{3}\\pi r^3$:\n"
                    "$$E(r) = \\frac{\\rho r}{3\\varepsilon_0} = \\frac{kQr}{R^3}$$\n"
                    "ב-$r=R/2$: $\\boxed{E = \\dfrac{kQ}{2R^2}}$."
                ),
            ),
            _section(
                "conductors_gauss",
                "Conductors in Electrostatic Equilibrium",
                "מוליכים בשיווי משקל אלקטרוסטטי",
                (
                    "In equilibrium inside a conductor:\n"
                    "- $\\mathbf{E} = \\mathbf{0}$ in the bulk (free charges move until cancelled)\n"
                    "- Excess charge resides on the **surface**\n"
                    "- Just outside a conductor: $E_n = \\sigma/\\varepsilon_0$ "
                    "(Gauss pillbox on surface)\n"
                    "- Entire conductor is an **equipotential** ($V=\\text{const}$)\n\n"
                    "**Cavity with no enclosed charge:** $E=0$ inside cavity "
                    "(electrostatic shielding / Faraday cage).\n\n"
                    "Gauss's law on a surface inside the metal gives $Q_{\\text{enc}}=0$."
                ),
                (
                    "בשיווי משקל בתוך מוליך:\n"
                    "- $\\mathbf{E} = \\mathbf{0}$ בנפח (מטענים חופשיים נעים עד לביטול)\n"
                    "- מטען עודף על **פני השטח** בלבד\n"
                    "- מיד מחוץ למוליך: $E_n = \\sigma/\\varepsilon_0$\n"
                    "- המוליך **איזופוטנציאלי** ($V=\\text{const}$)\n\n"
                    "**חלל ללא מטען סגור:** $E=0$ בחלל (מיגון / כלוב פараדי).\n\n"
                    "חוק גאוס על פני שטח בתוך המתכת נותן $Q_{\\text{enc}}=0$."
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "An infinite uniformly charged plane has symmetry about the normal. Which Gaussian surface is most efficient?",
                "למישור טעון אינסופית אחיד יש סימטריה לנורמל. איזה פני שטח גאוסיים הכי יעילים?",
                [
                    {"id": "a", "text_en": "A sphere centered on the plane", "text_he": "כדור במרכז המישור", "correct": False},
                    {"id": "b", "text_en": "A pillbox (cylinder) straddling the plane, axis normal to it", "text_he": "גלילון החוצה את המישור, ציר נורמלי", "correct": True},
                    {"id": "c", "text_en": "A cube with one face on the plane", "text_he": "קוב עם פאה על המישור", "correct": False},
                    {"id": "d", "text_en": "Any surface works equally well", "text_he": "כל פני שטח עובדים באותה מידה", "correct": False},
                ],
                "A pillbox exploits planar symmetry: $\\mathbf{E}$ is normal and constant on the caps; flux through the curved wall is zero.",
                "גלילון מנצל סימטריה planar: $\\mathbf{E}$ נורמלי וקבוע על הכיסויים; השטף דרך הדופן האחידה אפס.",
            ),
            _mcq(
                "q2",
                "A point dipole is at the center of a spherical Gaussian surface. The net electric flux $\\Phi_E$ is:",
                "דיפול נקודתי במרכז כדור גאוסי. השטף החשמלי הנקי $\\Phi_E$ הוא:",
                [
                    {"id": "a", "text_en": "$+q/\\varepsilon_0$", "text_he": "$+q/\\varepsilon_0$", "correct": False},
                    {"id": "b", "text_en": "$-q/\\varepsilon_0$", "text_he": "$-q/\\varepsilon_0$", "correct": False},
                    {"id": "c", "text_en": "$2q/\\varepsilon_0$", "text_he": "$2q/\\varepsilon_0$", "correct": False},
                    {"id": "d", "text_en": "$0$", "text_he": "$0$", "correct": True},
                ],
                "A dipole has net charge zero; $Q_{\\text{enc}}=0$ so $\\Phi_E=0$ by Gauss's law.",
                "לדיפול מטען נקי אפס; $Q_{\\text{enc}}=0$ ולכן $\\Phi_E=0$ לפי חוק גאוס.",
            ),
            _mcq(
                "q3",
                "An infinite line carries $\\lambda = 2.0\\times10^{-6}$ C/m. Find $E$ at $r=0.10$ m.",
                "קו אינסופי נושא $\\lambda = 2.0\\times10^{-6}$ C/m. מצא $E$ ב-$r=0.10$ m.",
                [
                    {"id": "a", "text_en": "$3.6\\times10^{5}$ N/C", "text_he": "$3.6\\times10^{5}$ N/C", "correct": True},
                    {"id": "b", "text_en": "$1.8\\times10^{5}$ N/C", "text_he": "$1.8\\times10^{5}$ N/C", "correct": False},
                    {"id": "c", "text_en": "$7.2\\times10^{5}$ N/C", "text_he": "$7.2\\times10^{5}$ N/C", "correct": False},
                    {"id": "d", "text_en": "$9.0\\times10^{4}$ N/C", "text_he": "$9.0\\times10^{4}$ N/C", "correct": False},
                ],
                "$E=\\lambda/(2\\pi\\varepsilon_0 r)=2k\\lambda/r=2(9\\times10^9)(2\\times10^{-6})/0.1=3.6\\times10^5$ N/C.",
                "$E=\\lambda/(2\\pi\\varepsilon_0 r)=2k\\lambda/r=3.6\\times10^5$ N/C.",
            ),
            _mcq(
                "q4",
                "A solid uniformly charged sphere of radius $R$ and total charge $Q$. What is $E$ at $r=R/2$?",
                "כדור מלא טעון אחיד ברדיוס $R$ ומטען $Q$. מהו $E$ ב-$r=R/2$?",
                [
                    {"id": "a", "text_en": "$kQ/R^2$", "text_he": "$kQ/R^2$", "correct": False},
                    {"id": "b", "text_en": "$kQ/(2R^2)$", "text_he": "$kQ/(2R^2)$", "correct": True},
                    {"id": "c", "text_en": "$kQ/(4R^2)$", "text_he": "$kQ/(4R^2)$", "correct": False},
                    {"id": "d", "text_en": "$0$", "text_he": "$0$", "correct": False},
                ],
                "Inside: $E=kQr/R^3$. At $r=R/2$: $E=kQ(R/2)/R^3=kQ/(2R^2)$.",
                "בפנים: $E=kQr/R^3$. ב-$r=R/2$: $E=kQ/(2R^2)$.",
            ),
            _mcq(
                "q5",
                "A hollow conductor in equilibrium carries net charge $Q$. Where is the charge and what is $E$ inside the metal?",
                "מוליך חלול בשיווי משקל נושא מטען $Q$. איפה המטען ומה $E$ בתוך המתכת?",
                [
                    {"id": "a", "text_en": "Charge uniform in volume; $E\\ne0$ in metal", "text_he": "מטען אחיד בנפח; $E\\ne0$ במתכת", "correct": False},
                    {"id": "b", "text_en": "Charge on outer surface only; $E=0$ in metal bulk", "text_he": "מטען על פני שטח חיצוניים; $E=0$ בנפח המתכת", "correct": True},
                    {"id": "c", "text_en": "Charge at center; $E=0$ everywhere", "text_he": "מטען במרכז; $E=0$ בכל מקום", "correct": False},
                    {"id": "d", "text_en": "Charge on inner surface only", "text_he": "מטען על פני שטח פנימיים בלבד", "correct": False},
                ],
                "In equilibrium, free charge in a conductor sits on surfaces; $\\mathbf{E}=0$ in the bulk metal.",
                "בשיווי משקל מטען חופשי על פני שטח; $\\mathbf{E}=0$ בנפח המתכת.",
            ),
        ],
    },
    {
        "id": "magnetic_field_biot_savart",
        "subject": "university_physics_2",
        "title_en": "Magnetic Fields — Biot-Savart Law (University)",
        "title_he": "שדות מגנטיים — חוק Biot-Savart (אוניברסיטה)",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Use the right-hand rule consistently for $\\mathbf{v}\\times\\mathbf{B}$ and "
            "$d\\mathbf{l}\\times\\hat{\\mathbf{r}}$. Biot-Savart gives the field from a "
            "current element; superposition applies. Infinite wire: $B=\\mu_0 I/(2\\pi r)$. "
            "Circular loop center: $B=\\mu_0 I/(2R)$. Parallel wires: force per length "
            "$F/L=\\mu_0 I_1 I_2/(2\\pi d)$. Units: tesla (T), $1\\,\\text{T}=1\\,\\text{N/(A·m)}$."
        ),
        "sections": [
            _section(
                "magnetic_force_charges",
                "Magnetic Force on Moving Charges — $\\mathbf{F}=q\\mathbf{v}\\times\\mathbf{B}$",
                "כוח מגנטי על מטען נע — $\\mathbf{F}=q\\mathbf{v}\\times\\mathbf{B}$",
                (
                    "A charge $q$ moving with velocity $\\mathbf{v}$ in magnetic field "
                    "$\\mathbf{B}$ experiences:\n"
                    "$$\\boxed{\\mathbf{F} = q\\,\\mathbf{v}\\times\\mathbf{B}}$$\n\n"
                    "Magnitude: $F = |q|vB\\sin\\theta$. Direction: **right-hand rule** "
                    "(for $q>0$): fingers $\\mathbf{v}\\to\\mathbf{B}$, thumb = force.\n\n"
                    "Magnetic force does **no work**: "
                    "$\\mathbf{F}\\perp\\mathbf{v}$ so $dW=\\mathbf{F}\\cdot d\\mathbf{r}=0$.\n\n"
                    "Lorentz force (full EM): $\\mathbf{F}=q(\\mathbf{E}+\\mathbf{v}\\times\\mathbf{B})$."
                ),
                (
                    "מטען $q$ הנע במהירות $\\mathbf{v}$ בשדה $\\mathbf{B}$:\n"
                    "$$\\boxed{\\mathbf{F} = q\\,\\mathbf{v}\\times\\mathbf{B}}$$\n\n"
                    "גודל: $F = |q|vB\\sin\\theta$. כיוון: **כלל היד הימנית** "
                    "(ל-$q>0$): אצבעות $\\mathbf{v}\\to\\mathbf{B}$, אגודל = כוח.\n\n"
                    "הכוח המגנטי **לא מבצע עבודה**: $\\mathbf{F}\\perp\\mathbf{v}$.\n\n"
                    "כוח לורנץ: $\\mathbf{F}=q(\\mathbf{E}+\\mathbf{v}\\times\\mathbf{B})$."
                ),
            ),
            _section(
                "force_on_current",
                "Force on a Current Element — $d\\mathbf{F}=I\\,d\\mathbf{l}\\times\\mathbf{B}$",
                "כוח על אלמנט זרם — $d\\mathbf{F}=I\\,d\\mathbf{l}\\times\\mathbf{B}$",
                (
                    "Current $I$ in segment $d\\mathbf{l}$ (direction of conventional current):\n"
                    "$$d\\mathbf{F} = I\\,d\\mathbf{l}\\times\\mathbf{B}$$\n\n"
                    "Total force on wire from $a$ to $b$:\n"
                    "$$\\mathbf{F} = I\\int_a^b d\\mathbf{l}\\times\\mathbf{B}$$\n\n"
                    "For uniform $\\mathbf{B}$ and straight wire length $L$:\n"
                    "$$F = BIL\\sin\\theta$$\n\n"
                    "Torque on a current loop in $\\mathbf{B}$: "
                    "$\\boldsymbol{\\tau}=\\mathbf{m}\\times\\mathbf{B}$ where "
                    "$\\mathbf{m}=IA\\hat{\\mathbf{n}}$ is magnetic dipole moment."
                ),
                (
                    "זרם $I$ באלמנט $d\\mathbf{l}$ (כיוון הזרם החיובי):\n"
                    "$$d\\mathbf{F} = I\\,d\\mathbf{l}\\times\\mathbf{B}$$\n\n"
                    "כוח כולל על חוט:\n"
                    "$$\\mathbf{F} = I\\int_a^b d\\mathbf{l}\\times\\mathbf{B}$$\n\n"
                    "עבור $\\mathbf{B}$ אחיד וחוט ישר באורך $L$:\n"
                    "$$F = BIL\\sin\\theta$$\n\n"
                    "מומנט על לולאת זרם: $\\boldsymbol{\\tau}=\\mathbf{m}\\times\\mathbf{B}$, "
                    "$\\mathbf{m}=IA\\hat{\\mathbf{n}}$."
                ),
            ),
            _section(
                "biot_savart_law",
                "The Biot-Savart Law",
                "חוק Biot-Savart",
                (
                    "The magnetic field from steady current element $I\\,d\\mathbf{l}$ "
                    "at position $\\mathbf{r}$ from the element:\n"
                    "$$\\boxed{d\\mathbf{B} = \\frac{\\mu_0}{4\\pi}\\,"
                    "\\frac{I\\,d\\mathbf{l}\\times\\hat{\\mathbf{r}}}{r^2}}$$\n\n"
                    "where $\\hat{\\mathbf{r}}$ points from $d\\mathbf{l}$ to field point, "
                    "$\\mu_0=4\\pi\\times10^{-7}$ T·m/A.\n\n"
                    "Total field by **superposition**:\n"
                    "$$\\mathbf{B}(\\mathbf{r}) = \\frac{\\mu_0}{4\\pi}\\int "
                    "\\frac{I\\,d\\mathbf{l}'\\times(\\mathbf{r}-\\mathbf{r}')}{|\\mathbf{r}-\\mathbf{r}'|^3}$$\n\n"
                    "Compare Gauss (electric) vs Biot-Savart (magnetic): no magnetic monopoles, "
                    "field lines close on themselves."
                ),
                (
                    "השדה המגנטי מאלמנט זרם $I\\,d\\mathbf{l}$ בנקודת שדה $\\mathbf{r}$:\n"
                    "$$\\boxed{d\\mathbf{B} = \\frac{\\mu_0}{4\\pi}\\,"
                    "\\frac{I\\,d\\mathbf{l}\\times\\hat{\\mathbf{r}}}{r^2}}$$\n\n"
                    "$\\mu_0=4\\pi\\times10^{-7}$ T·m/A.\n\n"
                    "שדה כולל ב**superposition**:\n"
                    "$$\\mathbf{B}(\\mathbf{r}) = \\frac{\\mu_0}{4\\pi}\\int "
                    "\\frac{I\\,d\\mathbf{l}'\\times(\\mathbf{r}-\\mathbf{r}')}{|\\mathbf{r}-\\mathbf{r}'|^3}$$\n\n"
                    "אין מונופולים מגנטיים; קווי שדה סגורים."
                ),
            ),
            _section(
                "wire_and_loop",
                "Infinite Wire and Circular Loop",
                "חוט אינסופי ולולאה עגולה",
                (
                    "**Infinite straight wire** (distance $r$ from axis):\n"
                    "By symmetry and Biot-Savart integration:\n"
                    "$$B(r) = \\frac{\\mu_0 I}{2\\pi r}$$\n"
                    "Direction: right-hand rule around current.\n\n"
                    "**Circular loop** radius $R$, current $I$, field at center:\n"
                    "$$B_{\\text{center}} = \\frac{\\mu_0 I}{2R}$$\n\n"
                    "On axis at distance $z$ from center:\n"
                    "$$B(z)=\\frac{\\mu_0 I R^2}{2(R^2+z^2)^{3/2}}$$"
                ),
                (
                    "**חוט ישר אינסופי** (מרחק $r$):\n"
                    "$$B(r) = \\frac{\\mu_0 I}{2\\pi r}$$\n"
                    "כיוון: כלל היד הימנית סביב הזרם.\n\n"
                    "**לולאה עגולה** רדיוס $R$, זרם $I$, שדה במרכז:\n"
                    "$$B_{\\text{center}} = \\frac{\\mu_0 I}{2R}$$\n\n"
                    "על הציר במרחק $z$:\n"
                    "$$B(z)=\\frac{\\mu_0 I R^2}{2(R^2+z^2)^{3/2}}$$"
                ),
            ),
            _section(
                "parallel_wires_units",
                "Parallel Wires and Magnetic Units",
                "חוטים מקבילים ויחידות מגנטיות",
                (
                    "Two long parallel wires separated by distance $d$, currents $I_1, I_2$:\n"
                    "Field on wire 2 from wire 1: $B=\\mu_0 I_1/(2\\pi d)$.\n"
                    "Force per unit length on wire 2:\n"
                    "$$\\frac{F}{L} = \\frac{\\mu_0 I_1 I_2}{2\\pi d}$$\n\n"
                    "Same direction currents **attract**; opposite **repel**.\n\n"
                    "**Units:** $\\mathbf{B}$ in tesla (T); "
                    "$1\\,\\text{T} = 1\\,\\text{N/(A·m)} = 1\\,\\text{Wb/m}^2$.\n"
                    "Permeability: $\\mu_0=4\\pi\\times10^{-7}$ T·m/A."
                ),
                (
                    "שני חוטים מקבילים במרחק $d$, זרמים $I_1, I_2$:\n"
                    "שדה על חוט 2 מחוט 1: $B=\\mu_0 I_1/(2\\pi d)$.\n"
                    "כוח ליחידת אורך:\n"
                    "$$\\frac{F}{L} = \\frac{\\mu_0 I_1 I_2}{2\\pi d}$$\n\n"
                    "זרמים באותו כיוון **מושכים**; בכיוון הפוך **דוחים**.\n\n"
                    "**יחידות:** $\\mathbf{B}$ ב-tesla (T); "
                    "$1\\,\\text{T} = 1\\,\\text{N/(A·m)}$."
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "$\\mathbf{v}$ points $+x$, $\\mathbf{B}$ points $+z$. For $q>0$, $\\mathbf{F}=q\\mathbf{v}\\times\\mathbf{B}$ points:",
                "$\\mathbf{v}$ בכיוון $+x$, $\\mathbf{B}$ ב-$+z$. ל-$q>0$, $\\mathbf{F}$ בכיוון:",
                [
                    {"id": "a", "text_en": "$+y$", "text_he": "$+y$", "correct": False},
                    {"id": "b", "text_en": "$-y$", "text_he": "$-y$", "correct": True},
                    {"id": "c", "text_en": "$+x$", "text_he": "$+x$", "correct": False},
                    {"id": "d", "text_en": "$-z$", "text_he": "$-z$", "correct": False},
                ],
                "$\\hat{x}\\times\\hat{z}=-\\hat{y}$, so $\\mathbf{F}=-q|\\mathbf{v}\\times\\mathbf{B}|\\hat{y}$ for $q>0$.",
                "$\\hat{x}\\times\\hat{z}=-\\hat{y}$.",
            ),
            _mcq(
                "q2",
                "Long wire carries $I=10$ A. Find $B$ at $r=0.05$ m.",
                "חוט ארוך נושא $I=10$ A. מצא $B$ ב-$r=0.05$ m.",
                [
                    {"id": "a", "text_en": "$4.0\\times10^{-5}$ T", "text_he": "$4.0\\times10^{-5}$ T", "correct": True},
                    {"id": "b", "text_en": "$2.0\\times10^{-5}$ T", "text_he": "$2.0\\times10^{-5}$ T", "correct": False},
                    {"id": "c", "text_en": "$8.0\\times10^{-5}$ T", "text_he": "$8.0\\times10^{-5}$ T", "correct": False},
                    {"id": "d", "text_en": "$1.0\\times10^{-4}$ T", "text_he": "$1.0\\times10^{-4}$ T", "correct": False},
                ],
                "$B=\\mu_0 I/(2\\pi r)=(4\\pi\\times10^{-7})(10)/(2\\pi\\cdot0.05)=4\\times10^{-5}$ T.",
                "$B=\\mu_0 I/(2\\pi r)=4\\times10^{-5}$ T.",
            ),
            _mcq(
                "q3",
                "Circular loop radius $R=0.20$ m, $I=5$ A. Field at center?",
                "לולאה $R=0.20$ m, $I=5$ A. שדה במרכז?",
                [
                    {"id": "a", "text_en": "$1.57\\times10^{-5}$ T", "text_he": "$1.57\\times10^{-5}$ T", "correct": True},
                    {"id": "b", "text_en": "$3.14\\times10^{-5}$ T", "text_he": "$3.14\\times10^{-5}$ T", "correct": False},
                    {"id": "c", "text_en": "$7.85\\times10^{-6}$ T", "text_he": "$7.85\\times10^{-6}$ T", "correct": False},
                    {"id": "d", "text_en": "$6.28\\times10^{-5}$ T", "text_he": "$6.28\\times10^{-5}$ T", "correct": False},
                ],
                "$B=\\mu_0 I/(2R)=(4\\pi\\times10^{-7})(5)/(0.4)\\approx1.57\\times10^{-5}$ T.",
                "$B=\\mu_0 I/(2R)\\approx1.57\\times10^{-5}$ T.",
            ),
            _mcq(
                "q4",
                "Two parallel wires $d=0.10$ m apart carry $I_1=I_2=8$ A same direction. $B$ on wire 2 from wire 1?",
                "שני חוטים $d=0.10$ m, $I_1=I_2=8$ A באותו כיוון. $B$ על חוט 2 מחוט 1?",
                [
                    {"id": "a", "text_en": "$1.6\\times10^{-5}$ T", "text_he": "$1.6\\times10^{-5}$ T", "correct": True},
                    {"id": "b", "text_en": "$3.2\\times10^{-5}$ T", "text_he": "$3.2\\times10^{-5}$ T", "correct": False},
                    {"id": "c", "text_en": "$8.0\\times10^{-6}$ T", "text_he": "$8.0\\times10^{-6}$ T", "correct": False},
                    {"id": "d", "text_en": "$0$ T", "text_he": "$0$ T", "correct": False},
                ],
                "Superposition: only wire 1 contributes to field at wire 2: $B=\\mu_0 I_1/(2\\pi d)=1.6\\times10^{-5}$ T.",
                "$B=\\mu_0 I_1/(2\\pi d)=1.6\\times10^{-5}$ T.",
            ),
            _mcq(
                "q5",
                "Parallel wires $I_1=I_2=8$ A, $d=0.10$ m, same direction. Force per length on wire 2 (attractive)?",
                "חוטים $I_1=I_2=8$ A, $d=0.10$ m, אותו כיוון. כוח ליחידת אורך על חוט 2?",
                [
                    {"id": "a", "text_en": "$1.28\\times10^{-4}$ N/m toward wire 1", "text_he": "$1.28\\times10^{-4}$ N/m לכיוון חוט 1", "correct": True},
                    {"id": "b", "text_en": "$1.28\\times10^{-4}$ N/m away from wire 1", "text_he": "$1.28\\times10^{-4}$ N/m הרחק מחוט 1", "correct": False},
                    {"id": "c", "text_en": "$6.4\\times10^{-5}$ N/m toward wire 1", "text_he": "$6.4\\times10^{-5}$ N/m לכיוון חוט 1", "correct": False},
                    {"id": "d", "text_en": "$0$ N/m", "text_he": "$0$ N/m", "correct": False},
                ],
                "$F/L=\\mu_0 I_1 I_2/(2\\pi d)=1.28\\times10^{-4}$ N/m; same-direction currents attract.",
                "$F/L=\\mu_0 I_1 I_2/(2\\pi d)=1.28\\times10^{-4}$ N/m; זרמים באותו כיוון מושכים.",
            ),
        ],
    },
    {
        "id": "ampere_law",
        "subject": "university_physics_2",
        "title_en": "Ampère's Law and Symmetric Currents (University)",
        "title_he": "חוק אמפר וזרמים סימטריים (אוניברסיטה)",
        "duration_min": 23,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Ampère's law $\\oint\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0 I_{\\text{enc}}$ is the "
            "magnetic analog of Gauss — useful with high symmetry. Right-hand rule for "
            "Amperian loop direction vs $I_{\\text{enc}}$. Solenoid: $B=\\mu_0 nI$ inside. "
            "Toroid: field confined inside core. Preview displacement current: needed for "
            "consistency in capacitors and leads to Maxwell's correction."
        ),
        "sections": [
            _section(
                "ampere_integral",
                "Ampère's Law — Integral Form",
                "חוק אמפר — צורה אינטגרלית",
                (
                    "For steady (DC) currents:\n"
                    "$$\\boxed{\\oint_C \\mathbf{B}\\cdot d\\mathbf{l} = \\mu_0 I_{\\text{enc}}}$$\n\n"
                    "$I_{\\text{enc}}$ is the **algebraic sum** of currents piercing the "
                    "surface bounded by closed Amperian loop $C$ (right-hand rule).\n\n"
                    "Differential form (Stokes):\n"
                    "$$\\nabla\\times\\mathbf{B} = \\mu_0\\mathbf{J}$$\n\n"
                    "Valid for **steady** currents. Time-varying $E$ requires Maxwell's "
                    "displacement-current term."
                ),
                (
                    "לזרמים קבועים (DC):\n"
                    "$$\\boxed{\\oint_C \\mathbf{B}\\cdot d\\mathbf{l} = \\mu_0 I_{\\text{enc}}}$$\n\n"
                    "$I_{\\text{enc}}$ הוא **סכום אלגברי** של זרמים החודרים את הפני שטח "
                    "הגבולות על ידי לולאת אמפר $C$ (כלל היד הימנית).\n\n"
                    "צורה דיפרנציאלית:\n"
                    "$$\\nabla\\times\\mathbf{B} = \\mu_0\\mathbf{J}$$\n\n"
                    "תקף לזרמים **קבועים**. שינוי $\\mathbf{E}$ דורש תרמיל הזזה של מаксוול."
                ),
            ),
            _section(
                "infinite_wire_ampere",
                "Infinite Wire via Amperian Loop",
                "חוט אינסופי באמצעות לולאת אמפר",
                (
                    "Circular Amperian loop radius $r$ coaxial with wire carrying $I$.\n"
                    "By symmetry $B$ is tangential and constant on the loop:\n"
                    "$$\\oint \\mathbf{B}\\cdot d\\mathbf{l} = B(2\\pi r) = \\mu_0 I$$\n"
                    "$$B = \\frac{\\mu_0 I}{2\\pi r}$$\n\n"
                    "Same result as Biot-Savart — consistency check.\n"
                    "Direction: curl fingers with $\\oint\\mathbf{B}\\cdot d\\mathbf{l}$; "
                    "thumb gives current direction (RH rule)."
                ),
                (
                    "לולאת אמפר מעגלית ברדיוס $r$ קואקסיאלית לחוט עם זרם $I$.\n"
                    "לפי סימטריה $B$ משיקי וקבוע על הלולאה:\n"
                    "$$B(2\\pi r) = \\mu_0 I \\quad\\Rightarrow\\quad "
                    "B = \\frac{\\mu_0 I}{2\\pi r}$$\n\n"
                    "אותה תוצאה כמו Biot-Savart.\n"
                    "כיוון: כלל היד הימנית עם $\\oint\\mathbf{B}\\cdot d\\mathbf{l}$."
                ),
            ),
            _section(
                "solenoid_toroid",
                "Solenoid and Toroid",
                "סolenoid ו-toroid",
                (
                    "**Long solenoid** ($n$ turns/m, current $I$):\n"
                    "Rectangular Amperian loop: interior segment gives\n"
                    "$$B = \\mu_0 n I \\quad \\text{(uniform inside, end effects neglected)}$$\n\n"
                    "**Toroid** (mean radius $R$, $N$ total turns, current $I$):\n"
                    "Amperian circle inside core: $B(2\\pi r)=\\mu_0 N I$ (if all turns linked)\n"
                    "$$B = \\frac{\\mu_0 N I}{2\\pi r}$$\n\n"
                    "Field essentially **zero outside** toroid (unlike solenoid fringing)."
                ),
                (
                    "**סolenoid ארוך** ($n$ פיתולים/מ', זרם $I$):\n"
                    "$$B = \\mu_0 n I \\quad \\text{(אחיד בפנים)}$$\n\n"
                    "**טורoid** (רדיוס ממוצע $R$, $N$ פיתולים, זרם $I$):\n"
                    "$$B = \\frac{\\mu_0 N I}{2\\pi r}$$\n\n"
                    "השדה **אפסי בחוץ** (בניגוד לסolenoid)."
                ),
            ),
            _section(
                "amperian_path_choice",
                "Choosing an Amperian Path",
                "בחירת מסלול אמפרי",
                (
                    "Requirements (mirror Gauss's law strategy):\n"
                    "1. $\\mathbf{B}$ tangential and constant on part of path\n"
                    "2. $\\mathbf{B}\\perp d\\mathbf{l}$ or $B=0$ elsewhere\n\n"
                    "Then $\\oint\\mathbf{B}\\cdot d\\mathbf{l}=B\\,\\ell_{\\text{useful}}$.\n\n"
                    "Wrong path choice still satisfies Ampère's law but does not simplify $B$.\n"
                    "Always verify $I_{\\text{enc}}$ sign using RH convention."
                ),
                (
                    "דרישות (כמו בחוק גאוס):\n"
                    "1. $\\mathbf{B}$ משיקי וקבוע על חלק מהמסלול\n"
                    "2. $\\mathbf{B}\\perp d\\mathbf{l}$ או $B=0$ elsewhere\n\n"
                    "אז $\\oint\\mathbf{B}\\cdot d\\mathbf{l}=B\\,\\ell_{\\text{useful}}$.\n\n"
                    "מסלול לא מתאים עדיין מקיים את החוק אך לא מפשט $B$.\n"
                    "בדקו סימן $I_{\\text{enc}}$ לפי כלל היד הימנית."
                ),
            ),
            _section(
                "displacement_preview",
                "Limitation and Displacement Current Preview",
                "מגבלה ותצוגה מקדימה של תרמיל הזזה",
                (
                    "Charging capacitor: steady current in wires but **no conduction current** "
                    "between plates. Ampère alone gives $\\oint\\mathbf{B}\\cdot d\\mathbf{l}=0$ "
                    "through gap — contradicts experiment.\n\n"
                    "Maxwell added **displacement current density**:\n"
                    "$$\\mathbf{J}_d = \\varepsilon_0\\frac{\\partial\\mathbf{E}}{\\partial t}$$\n\n"
                    "Ampère-Maxwell law:\n"
                    "$$\\oint\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0\\!"
                    "\\left(I_{\\text{cond}}+\\varepsilon_0\\frac{d\\Phi_E}{dt}\\right)$$\n\n"
                    "Restores consistency and enables EM waves."
                ),
                (
                    "מעגל טעינה: זרם בחוטים אך **אין זרם מוליך** בין לוחות. "
                    "אמפר בלבד נותן אפס בשבלול — סתירה.\n\n"
                    "מаксוול הוסיף **צפיפות תרמיל הזזה**:\n"
                    "$$\\mathbf{J}_d = \\varepsilon_0\\frac{\\partial\\mathbf{E}}{\\partial t}$$\n\n"
                    "חוק אמפר-מаксוול:\n"
                    "$$\\oint\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0\\!"
                    "\\left(I_{\\text{cond}}+\\varepsilon_0\\frac{d\\Phi_E}{dt}\\right)$$"
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "Long solenoid: $n=500$ turns/m, $I=2$ A. Approximate $B$ inside?",
                "סolenoid ארוך: $n=500$ פיתולים/מ', $I=2$ A. $B$ בפנים?",
                [
                    {"id": "a", "text_en": "$1.26\\times10^{-3}$ T", "text_he": "$1.26\\times10^{-3}$ T", "correct": True},
                    {"id": "b", "text_en": "$6.28\\times10^{-4}$ T", "text_he": "$6.28\\times10^{-4}$ T", "correct": False},
                    {"id": "c", "text_en": "$2.51\\times10^{-3}$ T", "text_he": "$2.51\\times10^{-3}$ T", "correct": False},
                    {"id": "d", "text_en": "$4.0\\times10^{-3}$ T", "text_he": "$4.0\\times10^{-3}$ T", "correct": False},
                ],
                "$B=\\mu_0 nI=(4\\pi\\times10^{-7})(500)(2)=1.256\\times10^{-3}$ T.",
                "$B=\\mu_0 nI=1.26\\times10^{-3}$ T.",
            ),
            _mcq(
                "q2",
                "Toroid: $N=1000$ turns, $I=3$ A, mean radius $r=0.15$ m. Find $B$ on mean circle.",
                "טורoid: $N=1000$, $I=3$ A, רדיוס ממוצע $r=0.15$ m. $B$?",
                [
                    {"id": "a", "text_en": "$4.0\\times10^{-3}$ T", "text_he": "$4.0\\times10^{-3}$ T", "correct": True},
                    {"id": "b", "text_en": "$2.0\\times10^{-3}$ T", "text_he": "$2.0\\times10^{-3}$ T", "correct": False},
                    {"id": "c", "text_en": "$8.0\\times10^{-3}$ T", "text_he": "$8.0\\times10^{-3}$ T", "correct": False},
                    {"id": "d", "text_en": "$1.2\\times10^{-2}$ T", "text_he": "$1.2\\times10^{-2}$ T", "correct": False},
                ],
                "$B=\\mu_0 NI/(2\\pi r)=(4\\pi\\times10^{-7})(1000)(3)/(2\\pi\\cdot0.15)=4\\times10^{-3}$ T.",
                "$B=\\mu_0 NI/(2\\pi r)=4\\times10^{-3}$ T.",
            ),
            _mcq(
                "q3",
                "Amperian loop encloses two wires: $+5$ A upward and $+3$ A downward. $I_{\\text{enc}}$?",
                "לולאת אמפר סוגרת שני חוטים: $+5$ A למעלה ו-$+3$ A למטה. $I_{\\text{enc}}$?",
                [
                    {"id": "a", "text_en": "$8$ A", "text_he": "$8$ A", "correct": False},
                    {"id": "b", "text_en": "$2$ A", "text_he": "$2$ A", "correct": True},
                    {"id": "c", "text_en": "$5$ A", "text_he": "$5$ A", "correct": False},
                    {"id": "d", "text_en": "$0$ A", "text_he": "$0$ A", "correct": False},
                ],
                "Use consistent sign: $I_{\\text{enc}}=5-3=2$ A (algebraic sum with RH convention).",
                "סכום אלגברי: $I_{\\text{enc}}=5-3=2$ A.",
            ),
            _mcq(
                "q4",
                "When does $\\oint\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0 I_{\\text{enc}}$ (original Ampère) fail?",
                "מתי $\\oint\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0 I_{\\text{enc}}$ (אמפר המקורי) נכשל?",
                [
                    {"id": "a", "text_en": "Infinite straight wire", "text_he": "חוט ישר אינסופי", "correct": False},
                    {"id": "b", "text_en": "Long solenoid with steady $I$", "text_he": "סolenoid עם $I$ קבוע", "correct": False},
                    {"id": "c", "text_en": "Gap in a charging capacitor (no $I_{\\text{cond}}$ in gap)", "text_he": "רווח במעגל טעינת מעגל (אין $I_{\\text{cond}}$)", "correct": True},
                    {"id": "d", "text_en": "Toroid with steady $I$", "text_he": "טורoid עם $I$ קבוע", "correct": False},
                ],
                "Without displacement current, Ampère fails when only $\\partial\\mathbf{E}/\\partial t$ links the loop.",
                "ללא תרמיל הזזה, אמפר נכשל כש-$\\partial\\mathbf{E}/\\partial t$ מקשר את הלולאה.",
            ),
            _mcq(
                "q5",
                "Which symmetry best suits Ampère's law for finding $B$ of a long straight wire?",
                "איזו סימטריה מתאימה לחוק אמפר לחוט ישר ארוך?",
                [
                    {"id": "a", "text_en": "Spherical Amperian surface", "text_he": "פני שטח כדוריים", "correct": False},
                    {"id": "b", "text_en": "Circular Amperian loop coaxial with wire", "text_he": "לולאה מעגלית קואקסיאלית", "correct": True},
                    {"id": "c", "text_en": "Square loop in plane perpendicular to wire", "text_he": "לולאה מרובעת ניצבת לחוט", "correct": False},
                    {"id": "d", "text_en": "Ampère's law cannot be used for wires", "text_he": "לא ניתן להשתמש בחוק אמפר", "correct": False},
                ],
                "Cylindrical symmetry: $B$ tangential on circle of radius $r$ around wire.",
                "סימטריה גלילית: $B$ משיקי על מעגל ברדיוס $r$.",
            ),
        ],
    },
    {
        "id": "maxwell_equations",
        "subject": "university_physics_2",
        "title_en": "Maxwell's Equations and EM Waves (University)",
        "title_he": "משוואות מаксוול וגלים אלקטרומגנטיים (אוניברסיטה)",
        "duration_min": 26,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Present all four Maxwell equations in integral form first, then connect "
            "displacement current to capacitor charging. Wave speed $c=1/\\sqrt{\\mu_0\\varepsilon_0}$ "
            "follows from coupled $\\mathbf{E},\\mathbf{B}$ wave equations in vacuum. "
            "Poynting vector $\\mathbf{S}=(\\mathbf{E}\\times\\mathbf{B})/\\mu_0$ gives energy flux; "
            "direction is propagation for plane waves."
        ),
        "sections": [
            _section(
                "displacement_current",
                "Displacement Current and Ampère-Maxwell",
                "תרמיל הזזה ואמפר-מаксוול",
                (
                    "Maxwell's correction for time-varying electric fields:\n"
                    "$$\\mathbf{J}_d = \\varepsilon_0\\frac{\\partial\\mathbf{E}}{\\partial t}$$\n\n"
                    "**Ampère-Maxwell law:**\n"
                    "$$\\oint_C\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0 I_{\\text{enc}}^{\\text{total}}="
                    "\\mu_0\\!\\left(I_{\\text{cond}}+\\varepsilon_0\\frac{d\\Phi_E}{dt}\\right)$$\n\n"
                    "Parallel-plate capacitor charging: between plates "
                    "$I_{\\text{cond}}=0$ but $\\frac{d\\Phi_E}{dt}\\ne0$, so $B$ "
                    "exists — consistent with field in wires."
                ),
                (
                    "תיקון מаксוול לשדות חשמל משתנים:\n"
                    "$$\\mathbf{J}_d = \\varepsilon_0\\frac{\\partial\\mathbf{E}}{\\partial t}$$\n\n"
                    "**חוק אמפר-מаксוול:**\n"
                    "$$\\oint_C\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0\\!"
                    "\\left(I_{\\text{cond}}+\\varepsilon_0\\frac{d\\Phi_E}{dt}\\right)$$\n\n"
                    "מעגל טעינה: בין לוחות $I_{\\text{cond}}=0$ אך $\\frac{d\\Phi_E}{dt}\\ne0$."
                ),
            ),
            _section(
                "maxwell_four_integral",
                "The Four Maxwell Equations — Integral Form",
                "ארבע משוואות מаксוול — צורה אינטגרלית",
                (
                    "1. **Gauss (E):** $\\displaystyle\\oint_S\\mathbf{E}\\cdot d\\mathbf{A}=\\frac{Q_{\\text{enc}}}{\\varepsilon_0}$\n\n"
                    "2. **Gauss (B):** $\\displaystyle\\oint_S\\mathbf{B}\\cdot d\\mathbf{A}=0$ "
                    "(no magnetic monopoles)\n\n"
                    "3. **Faraday:** $\\displaystyle\\oint_C\\mathbf{E}\\cdot d\\mathbf{l}="
                    "-\\frac{d\\Phi_B}{dt}$\n\n"
                    "4. **Ampère-Maxwell:** $\\displaystyle\\oint_C\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0 I_{\\text{enc}}"
                    "+\\mu_0\\varepsilon_0\\frac{d\\Phi_E}{dt}$\n\n"
                    "In vacuum with $\\rho=0,\\mathbf{J}=0$, these couple to wave equations for "
                    "$\\mathbf{E}$ and $\\mathbf{B}$."
                ),
                (
                    "1. **גאוס (E):** $\\displaystyle\\oint_S\\mathbf{E}\\cdot d\\mathbf{A}=\\frac{Q_{\\text{enc}}}{\\varepsilon_0}$\n\n"
                    "2. **גאוס (B):** $\\displaystyle\\oint_S\\mathbf{B}\\cdot d\\mathbf{A}=0$\n\n"
                    "3. **פאראדי:** $\\displaystyle\\oint_C\\mathbf{E}\\cdot d\\mathbf{l}="
                    "-\\frac{d\\Phi_B}{dt}$\n\n"
                    "4. **אמפר-מаксוול:** $\\displaystyle\\oint_C\\mathbf{B}\\cdot d\\mathbf{l}=\\mu_0 I_{\\text{enc}}"
                    "+\\mu_0\\varepsilon_0\\frac{d\\Phi_E}{dt}$\n\n"
                    "בריק עם $\\rho=0,\\mathbf{J}=0$ — משוואות גל ל-$\\mathbf{E}$ ו-$\\mathbf{B}$."
                ),
            ),
            _section(
                "em_waves_speed",
                "Electromagnetic Waves and Speed $c$",
                "גלים אלקטרומגנטיים ומהירות $c$",
                (
                    "Plane wave in vacuum: $\\mathbf{E}=E_0\\cos(kz-\\omega t)\\hat{\\mathbf{x}}$, "
                    "$\\mathbf{B}=B_0\\cos(kz-\\omega t)\\hat{\\mathbf{y}}$ with "
                    "$\\mathbf{E}\\perp\\mathbf{B}\\perp\\hat{\\mathbf{k}}$.\n\n"
                    "From Maxwell's equations in free space:\n"
                    "$$\\boxed{c=\\frac{1}{\\sqrt{\\mu_0\\varepsilon_0}}=3.00\\times10^8\\,\\text{m/s}}$$\n\n"
                    "Also $E_0/B_0=c$ and $\\omega=ck$ (dispersion relation).\n\n"
                    "Energy density: $u=\\varepsilon_0 E^2$ (also $B^2/\\mu_0$)."
                ),
                (
                    "גל מישורי בריק: $\\mathbf{E}\\perp\\mathbf{B}\\perp\\hat{\\mathbf{k}}$.\n\n"
                    "ממשוואות מаксוול:\n"
                    "$$\\boxed{c=\\frac{1}{\\sqrt{\\mu_0\\varepsilon_0}}=3.00\\times10^8\\,\\text{m/s}}$$\n\n"
                    "גם $E_0/B_0=c$ ו-$\\omega=ck$.\n\n"
                    "צפיפות אנרגיה: $u=\\varepsilon_0 E^2$."
                ),
            ),
            _section(
                "poynting_vector",
                "Poynting Vector — Energy Flux",
                "וקטור פוינטינג — שטף אנרגיה",
                (
                    "The **Poynting vector** gives directional energy flux (W/m$^2$):\n"
                    "$$\\boxed{\\mathbf{S} = \\frac{1}{\\mu_0}\\mathbf{E}\\times\\mathbf{B}}$$\n\n"
                    "Time average for harmonic waves:\n"
                    "$$\\langle S\\rangle = \\frac{1}{2\\mu_0}E_0 B_0 = \\frac{1}{2}c\\varepsilon_0 E_0^2$$\n\n"
                    "Direction of $\\mathbf{S}$ is **propagation direction** for plane EM waves "
                    "(right-hand rule: $\\mathbf{E}\\to\\mathbf{B}\\to\\mathbf{S}$)."
                ),
                (
                    "**וקטור פוינטינג** — שטף אנרגיה (W/m$^2$):\n"
                    "$$\\boxed{\\mathbf{S} = \\frac{1}{\\mu_0}\\mathbf{E}\\times\\mathbf{B}}$$\n\n"
                    "ממוצע זמן לגלים הרמוניים:\n"
                    "$$\\langle S\\rangle = \\frac{1}{2\\mu_0}E_0 B_0$$\n\n"
                    "כיוון $\\mathbf{S}$ הוא **כיוון התקדמות** הגל."
                ),
            ),
            _section(
                "maxwell_unification",
                "Physical Meaning and Unification",
                "משמעות פיזיקלית ואיחוד",
                (
                    "Maxwell unified:\n"
                    "- Electricity (Gauss E)\n"
                    "- Magnetism (Gauss B, Ampère)\n"
                    "- Induction (Faraday)\n"
                    "- Optics / light as EM wave (wave speed = $c$)\n\n"
                    "Changing $\\mathbf{B}$ creates curling $\\mathbf{E}$; changing $\\mathbf{E}$ "
                    "creates curling $\\mathbf{B}$ — self-sustaining transverse waves.\n\n"
                    "In matter, use $\\varepsilon$, $\\mu$ and bound currents/charges."
                ),
                (
                    "מаксוול איחד:\n"
                    "- חשמל (גאוס E)\n"
                    "- מגנטיות (גאוס B, אמפר)\n"
                    "- השראה (פאראדי)\n"
                    "- אופטיקה / אור כגל EM\n\n"
                    "שינוי $\\mathbf{B}$ יוצר $\\mathbf{E}$ מסתחרר; שינוי $\\mathbf{E}$ יוצר "
                    "$\\mathbf{B}$ מסתחרר — גלים רוחביים.\n\n"
                    "בחומר: $\\varepsilon$, $\\mu$ ומטענים/זרמים קשורים."
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "Capacitor charging: conduction current in wires is $I$. Between plates, which term provides $I_{\\text{enc}}$ in Ampère-Maxwell?",
                "מעגל טעינה: זרם מוליך $I$ בחוטים. בין לוחות, איזה איבר מספק $I_{\\text{enc}}$?",
                [
                    {"id": "a", "text_en": "$I_{\\text{cond}}$ between plates", "text_he": "$I_{\\text{cond}}$ בין לוחות", "correct": False},
                    {"id": "b", "text_en": "$\\varepsilon_0\\, d\\Phi_E/dt$", "text_he": "$\\varepsilon_0\\, d\\Phi_E/dt$", "correct": True},
                    {"id": "c", "text_en": "Both are zero always", "text_he": "שניהם תמיד אפס", "correct": False},
                    {"id": "d", "text_en": "$\\mu_0\\, d\\Phi_B/dt$", "text_he": "$\\mu_0\\, d\\Phi_B/dt$", "correct": False},
                ],
                "Displacement current $\\varepsilon_0 d\\Phi_E/dt$ equals wire current during charging.",
                "תרמיל הזזה $\\varepsilon_0 d\\Phi_E/dt$ שווה לזרם בחוט בזמן טעינה.",
            ),
            _mcq(
                "q2",
                "Which Maxwell equation states that magnetic monopoles do not exist (in classical form)?",
                "איזו משוואת מаксוול אומרת שאין מונופולים מגנטיים?",
                [
                    {"id": "a", "text_en": "$\\oint\\mathbf{E}\\cdot d\\mathbf{A}=Q_{\\text{enc}}/\\varepsilon_0$", "text_he": "גאוס E", "correct": False},
                    {"id": "b", "text_en": "$\\oint\\mathbf{B}\\cdot d\\mathbf{A}=0$", "text_he": "$\\oint\\mathbf{B}\\cdot d\\mathbf{A}=0$", "correct": True},
                    {"id": "c", "text_en": "$\\oint\\mathbf{E}\\cdot d\\mathbf{l}=-d\\Phi_B/dt$", "text_he": "פאראדי", "correct": False},
                    {"id": "d", "text_en": "$\\nabla\\cdot\\mathbf{E}=\\rho/\\varepsilon_0$ only", "text_he": "רק $\\nabla\\cdot\\mathbf{E}$", "correct": False},
                ],
                "Gauss's law for magnetism: net magnetic flux through any closed surface is zero.",
                "חוק גאוס למגנטיות: שטף מגנטי נקי אפס.",
            ),
            _mcq(
                "q3",
                "In vacuum EM wave, if $E_0=300$ V/m, what is $B_0$?",
                "בגל EM בריק, $E_0=300$ V/m. מה $B_0$?",
                [
                    {"id": "a", "text_en": "$1.0\\times10^{-6}$ T", "text_he": "$1.0\\times10^{-6}$ T", "correct": True},
                    {"id": "b", "text_en": "$9.0\\times10^{10}$ T", "text_he": "$9.0\\times10^{10}$ T", "correct": False},
                    {"id": "c", "text_en": "$300$ T", "text_he": "$300$ T", "correct": False},
                    {"id": "d", "text_en": "$3.0\\times10^{-16}$ T", "text_he": "$3.0\\times10^{-16}$ T", "correct": False},
                ],
                "$B_0=E_0/c=300/(3\\times10^8)=1.0\\times10^{-6}$ T.",
                "$B_0=E_0/c=1.0\\times10^{-6}$ T.",
            ),
            _mcq(
                "q4",
                "$\\mathbf{E}$ along $+x$, $\\mathbf{B}$ along $+y$ (in phase). Poynting vector direction?",
                "$\\mathbf{E}$ ב-$+x$, $\\mathbf{B}$ ב-$+y$. כיוון $\\mathbf{S}$?",
                [
                    {"id": "a", "text_en": "$+z$", "text_he": "$+z$", "correct": True},
                    {"id": "b", "text_en": "$-z$", "text_he": "$-z$", "correct": False},
                    {"id": "c", "text_en": "$+x$", "text_he": "$+x$", "correct": False},
                    {"id": "d", "text_en": "$-y$", "text_he": "$-y$", "correct": False},
                ],
                "$\\mathbf{S}\\propto\\mathbf{E}\\times\\mathbf{B}$: $\\hat{x}\\times\\hat{y}=+\\hat{z}$.",
                "$\\hat{x}\\times\\hat{y}=+\\hat{z}$.",
            ),
            _mcq(
                "q5",
                "Compute $c=1/\\sqrt{\\mu_0\\varepsilon_0}$ using $\\mu_0=4\\pi\\times10^{-7}$, $\\varepsilon_0=8.85\\times10^{-12}$.",
                "חשב $c=1/\\sqrt{\\mu_0\\varepsilon_0}$.",
                [
                    {"id": "a", "text_en": "$3.0\\times10^8$ m/s", "text_he": "$3.0\\times10^8$ m/s", "correct": True},
                    {"id": "b", "text_en": "$3.0\\times10^6$ m/s", "text_he": "$3.0\\times10^6$ m/s", "correct": False},
                    {"id": "c", "text_en": "$1.0\\times10^8$ m/s", "text_he": "$1.0\\times10^8$ m/s", "correct": False},
                    {"id": "d", "text_en": "$9.0\\times10^{16}$ m/s", "text_he": "$9.0\\times10^{16}$ m/s", "correct": False},
                ],
                "$\\mu_0\\varepsilon_0\\approx1/(3\\times10^8)^2$, so $c\\approx3\\times10^8$ m/s.",
                "$c\\approx3\\times10^8$ m/s.",
            ),
        ],
    },
    {
        "id": "faraday_induction_uni",
        "subject": "university_physics_2",
        "title_en": "Faraday's Law — Electromagnetic Induction (University)",
        "title_he": "חוק פאראדיי — השראה אלקטרומגנטית (אוניברסיטה)",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Faraday: $\\mathcal{E}=-d\\Phi_B/dt$ (sign = Lenz). Motional EMF: $\\mathcal{E}=BLv$ "
            "for rod perpendicular to $\\mathbf{B}$. Generator: $\\mathcal{E}=NBA\\omega\\sin(\\omega t)$. "
            "Transformer: $V_p/V_s=N_p/N_s$. Self-inductance $L=\\mu_0 n^2 V$ for solenoid. "
            "RL time constant $\\tau=L/R$. Contrast: Faraday gives induced E from changing flux; "
            "Biot-Savart gives B from currents."
        ),
        "sections": [
            _section(
                "faraday_law",
                "Faraday's Law — Integral Form",
                "חוק פאראדיי — צורה אינטגרלית",
                (
                    "Magnetic flux through surface $S$:\n"
                    "$$\\Phi_B = \\int_S \\mathbf{B}\\cdot d\\mathbf{A}$$\n\n"
                    "**Faraday's law** (induced EMF around closed loop bounding $S$):\n"
                    "$$\\boxed{\\mathcal{E} = \\oint_C \\mathbf{E}\\cdot d\\mathbf{l} = "
                    "-\\frac{d\\Phi_B}{dt}}$$\n\n"
                    "For a conducting loop with resistance $R$: induced current "
                    "$I=\\mathcal{E}/R$. Flux change can arise from changing $B$, changing area, "
                    "or changing orientation ($\\Phi_B=BA\\cos\\theta$)."
                ),
                (
                    "שטף מגנטי דרך $S$:\n"
                    "$$\\Phi_B = \\int_S \\mathbf{B}\\cdot d\\mathbf{A}$$\n\n"
                    "**חוק פאראדיי:**\n"
                    "$$\\boxed{\\mathcal{E} = \\oint_C \\mathbf{E}\\cdot d\\mathbf{l} = "
                    "-\\frac{d\\Phi_B}{dt}}$$\n\n"
                    "בלולאה מוליכה: $I=\\mathcal{E}/R$. שינוי שטף מ-$B$, שטח או זווית."
                ),
            ),
            _section(
                "lenz_law",
                "Lenz's Law and Sign Convention",
                "חוק לנץ וסימון",
                (
                    "**Lenz's law:** induced current flows in direction that **opposes** "
                    "the change in flux that caused it.\n\n"
                    "The minus sign in $\\mathcal{E}=-d\\Phi_B/dt$ encodes Lenz.\n\n"
                    "Example: $B$ into page increasing → induced $B$ out of page → "
                    "counterclockwise current (RH rule).\n\n"
                    "Energy conservation: work against induced effects heats the circuit."
                ),
                (
                    "**חוק לנץ:** הזרם המושרה בכיוון ש**מתנגד** לשינוי השטף.\n\n"
                    "סימן מינוס ב-$\\mathcal{E}=-d\\Phi_B/dt$ מקודד את לנץ.\n\n"
                    "דוגמה: $B$ לתוך הדף גדל → $B$ החוצה מושר → זרם נגד כיוון השעון.\n\n"
                    "שימור אנרגיה: עבודה נגד ההשראה מתחממת במעגל."
                ),
            ),
            _section(
                "motional_emf",
                "Motional EMF — $\\mathcal{E}=BLv$",
                "EMF תנועתי — $\\mathcal{E}=BLv$",
                (
                    "Rod length $L$ moves with speed $v$ perpendicular to uniform $\\mathbf{B}$:\n"
                    "magnetic force on charges $q\\mathbf{v}\\times\\mathbf{B}$ separates charge, "
                    "creating $\\mathcal{E}=BLv$ until equilibrium.\n\n"
                    "General: motional EMF around moving loop = $-\\oint(\\mathbf{v}\\times\\mathbf{B})\\cdot d\\mathbf{l}$.\n\n"
                    "**Worked:** $B=0.5$ T, $L=0.20$ m, $v=4$ m/s → "
                    "$\\mathcal{E}=0.5\\times0.20\\times4=0.40$ V."
                ),
                (
                    "מוט $L$ נע במהירות $v$ ניצב ל-$\\mathbf{B}$:\n"
                    "$\\mathcal{E}=BLv$ עד שיווי משקל.\n\n"
                    "כללי: EMF תנועתי = $-\\oint(\\mathbf{v}\\times\\mathbf{B})\\cdot d\\mathbf{l}$.\n\n"
                    "**דוגמה:** $B=0.5$ T, $L=0.20$ m, $v=4$ m/s → $\\mathcal{E}=0.40$ V."
                ),
            ),
            _section(
                "generators_transformers",
                "Generators, Transformers, and Self-Inductance",
                "גנרטורים, שנאים והשראות עצמית",
                (
                    "**Rotating coil** ($N$ turns, area $A$, angular speed $\\omega$) in $B$:\n"
                    "$$\\mathcal{E}(t)=NBA\\omega\\sin(\\omega t)$$\n\n"
                    "**Ideal transformer:** $\\dfrac{V_p}{V_s}=\\dfrac{N_p}{N_s}$, "
                    "$I_p/I_s=N_s/N_p$ (power conserved ideally).\n\n"
                    "**Solenoid self-inductance:** $L=\\mu_0 n^2 V$ where $n$ turns/m, $V$ volume.\n\n"
                    "Induced EMF across inductor: $\\mathcal{E}_L=-L\\,dI/dt$."
                ),
                (
                    "**סליל מסתובב:** $\\mathcal{E}(t)=NBA\\omega\\sin(\\omega t)$.\n\n"
                    "**שנאי אידיאלי:** $\\dfrac{V_p}{V_s}=\\dfrac{N_p}{N_s}$.\n\n"
                    "**השראות עצמית של סolenoid:** $L=\\mu_0 n^2 V$.\n\n"
                    "EMF על סליל: $\\mathcal{E}_L=-L\\,dI/dt$."
                ),
            ),
            _section(
                "rl_circuit",
                "RL Circuits and Faraday vs Biot-Savart",
                "מעגלי RL ופאראדי מול Biot-Savart",
                (
                    "Series **RL** circuit (switch closed at $t=0$):\n"
                    "$$I(t)=\\frac{\\mathcal{E}_0}{R}\\left(1-e^{-t/\\tau}\\right), "
                    "\\quad \\tau=\\frac{L}{R}$$\n\n"
                    "At $t=\\tau$, $I\\approx63\\%$ of maximum.\n\n"
                    "**Conceptual distinction:**\n"
                    "- **Biot-Savart / Ampère:** $\\mathbf{B}$ due to **existing** currents\n"
                    "- **Faraday:** induced $\\mathcal{E}$ from **changing** $\\Phi_B$ "
                    "(causes new currents)"
                ),
                (
                    "מעגל **RL**:\n"
                    "$$I(t)=\\frac{\\mathcal{E}_0}{R}\\left(1-e^{-t/\\tau}\\right), "
                    "\\quad \\tau=\\frac{L}{R}$$\n\n"
                    "ב-$t=\\tau$, $I\\approx63\\%$ מהמקסימום.\n\n"
                    "**הבחנה:**\n"
                    "- **Biot-Savart / אמפר:** $\\mathbf{B}$ מזרמים **קיימים**\n"
                    "- **פאראדי:** $\\mathcal{E}$ משינוי $\\Phi_B$"
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "$B$ into page increases. By Lenz, induced current in a surrounding loop is:",
                "$B$ לתוך הדף גדל. לפי לנץ, הזרם המושרה:",
                [
                    {"id": "a", "text_en": "Clockwise (viewed from above)", "text_he": "עם כיוון השעון (מלמעלה)", "correct": False},
                    {"id": "b", "text_en": "Counterclockwise", "text_he": "נגד כיוון השעון", "correct": True},
                    {"id": "c", "text_en": "Zero always", "text_he": "תמיד אפס", "correct": False},
                    {"id": "d", "text_en": "Depends only on resistance, not Lenz", "text_he": "תלוי רק ב-$R$", "correct": False},
                ],
                "Induced B must oppose increasing inward flux → B out of page → CCW current.",
                "שדה מושר מתנגד לגידול $B$ פנימה → CCW.",
            ),
            _mcq(
                "q2",
                "Rod $L=0.50$ m moves at $v=6$ m/s in $B=0.40$ T perpendicular. Motional EMF?",
                "מוט $L=0.50$ m, $v=6$ m/s, $B=0.40$ T ניצב. EMF?",
                [
                    {"id": "a", "text_en": "$1.20$ V", "text_he": "$1.20$ V", "correct": True},
                    {"id": "b", "text_en": "$0.80$ V", "text_he": "$0.80$ V", "correct": False},
                    {"id": "c", "text_en": "$2.40$ V", "text_he": "$2.40$ V", "correct": False},
                    {"id": "d", "text_en": "$0.12$ V", "text_he": "$0.12$ V", "correct": False},
                ],
                "$\\mathcal{E}=BLv=0.40\\times0.50\\times6=1.20$ V.",
                "$\\mathcal{E}=BLv=1.20$ V.",
            ),
            _mcq(
                "q3",
                "Transformer: $N_p=200$, $N_s=50$, $V_p=120$ V. Secondary voltage?",
                "שנאי: $N_p=200$, $N_s=50$, $V_p=120$ V. $V_s$?",
                [
                    {"id": "a", "text_en": "$30$ V", "text_he": "$30$ V", "correct": True},
                    {"id": "b", "text_en": "$480$ V", "text_he": "$480$ V", "correct": False},
                    {"id": "c", "text_en": "$60$ V", "text_he": "$60$ V", "correct": False},
                    {"id": "d", "text_en": "$240$ V", "text_he": "$240$ V", "correct": False},
                ],
                "$V_s=V_p(N_s/N_p)=120\\times(50/200)=30$ V.",
                "$V_s=30$ V.",
            ),
            _mcq(
                "q4",
                "RL circuit: $L=0.20$ H, $R=40$ $\\Omega$. Time constant $\\tau$?",
                "מעגל RL: $L=0.20$ H, $R=40$ $\\Omega$. $\\tau$?",
                [
                    {"id": "a", "text_en": "$5.0$ ms", "text_he": "$5.0$ ms", "correct": True},
                    {"id": "b", "text_en": "$8.0$ s", "text_he": "$8.0$ s", "correct": False},
                    {"id": "c", "text_en": "$2.0$ ms", "text_he": "$2.0$ ms", "correct": False},
                    {"id": "d", "text_en": "$50$ ms", "text_he": "$50$ ms", "correct": False},
                ],
                "$\\tau=L/R=0.20/40=0.005$ s $=5.0$ ms. Note: 0.005 s and 5.0 ms are equivalent.",
                "$\\tau=L/R=5.0$ ms.",
            ),
            _mcq(
                "q5",
                "Which law gives the magnetic field of a steady current in a wire?",
                "איזה חוק נותן את $\\mathbf{B}$ של זרם קבוע בחוט?",
                [
                    {"id": "a", "text_en": "Faraday's law $\\mathcal{E}=-d\\Phi_B/dt$", "text_he": "חוק פאראדי", "correct": False},
                    {"id": "b", "text_en": "Biot-Savart (or Ampère's law)", "text_he": "Biot-Savart (או אמפר)", "correct": True},
                    {"id": "c", "text_en": "Gauss's law for electricity", "text_he": "חוק גאוס לחשמל", "correct": False},
                    {"id": "d", "text_en": "Lenz's law alone", "text_he": "חוק לנץ בלבד", "correct": False},
                ],
                "Steady B from I is computed via Biot-Savart or Ampère; Faraday links changing flux to induced EMF.",
                "B מזרם קבוע — Biot-Savart/אמפר; פאראדי — EMF משינוי שטף.",
            ),
        ],
    },
]


def write_lesson_files(lessons: list[dict]) -> list[Path]:
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for lesson in lessons:
        path = LESSONS_DIR / f"{lesson['id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(lesson, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(path)
        print(f"[write] {path.relative_to(ROOT)}")
    return written


def update_lessons_index(lessons: list[dict]) -> None:
    with INDEX_PATH.open(encoding="utf-8") as f:
        index = json.load(f)

    lesson_by_id = {lesson["id"]: lesson for lesson in lessons}
    updated = 0
    added = 0

    for entry in index:
        lid = entry.get("id")
        if lid not in INDEX_ENTRIES:
            continue
        meta = INDEX_ENTRIES[lid]
        lesson = lesson_by_id[lid]
        entry.update(
            {
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": ["university_physics_2"],
                "subject": "university_physics_2",
                "duration_min": meta["duration_min"],
                "type": "interactive",
                "level_min": "university",
            }
        )
        updated += 1

    existing_ids = {e["id"] for e in index}
    if "faraday_induction_uni" not in existing_ids:
        meta = INDEX_ENTRIES["faraday_induction_uni"]
        index.append(
            {
                "id": "faraday_induction_uni",
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": ["university_physics_2"],
                "subject": "university_physics_2",
                "duration_min": meta["duration_min"],
                "type": "interactive",
                "level_min": "university",
            }
        )
        added += 1

    index.sort(key=lambda e: e["id"])
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[index] updated {updated} entries, added {added} new")


def update_curriculum_categories() -> None:
    text = CURRICULUM_PATH.read_text(encoding="utf-8")
    original = text

    text = text.replace(
        "'ampere_law', 'faraday_induction', 'maxwell_equations',",
        "'ampere_law', 'faraday_induction_uni', 'maxwell_equations',",
    )
    text = text.replace(
        "'ampere_law', 'faraday_induction'],",
        "'ampere_law', 'faraday_induction_uni'],",
    )

    if text == original:
        raise RuntimeError("curriculum-categories.ts: expected faraday_induction replacements not found")

    CURRICULUM_PATH.write_text(text, encoding="utf-8")
    print(f"[curriculum] updated {CURRICULUM_PATH.relative_to(ROOT)}")


def main() -> int:
    lessons = build_lessons()
    assert len(lessons) == 5, f"expected 5 lessons, got {len(lessons)}"
    for lesson in lessons:
        assert lesson["subject"] == "university_physics_2"
        assert len(lesson["sections"]) >= 4
        assert len(lesson["questions"]) == 5
        assert all(q["type"] == "mcq" for q in lesson["questions"])

    write_lesson_files(lessons)
    update_lessons_index(lessons)
    update_curriculum_categories()
    print("[done] Physics 2 university lessons authored successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
