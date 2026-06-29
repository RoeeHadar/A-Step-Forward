#!/usr/bin/env python3
"""Author 5 university Physics 1 (Mechanics) lessons and update the lessons index."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
INDEX_PATH = ROOT / "apps" / "web" / "src" / "lib" / "lessons-index.generated.json"

SUBJECT = "university_physics_1"

INDEX_ENTRIES = {
    "rigid_body_torque_equilibrium": {
        "title_en": "Rigid Body Statics — Torque & Equilibrium (University)",
        "title_he": "סטטיקה של גוף קשיח — מומנט ושיווי משקל (אוניברסיטה)",
        "duration_min": 26,
    },
    "harmonic_oscillation": {
        "title_en": "Harmonic Oscillations (University)",
        "title_he": "תנודות הרמוניות (אוניברסיטה)",
        "duration_min": 24,
    },
    "fluids_hydrostatics": {
        "title_en": "Fluids — Hydrostatics & Hydrodynamics (University)",
        "title_he": "נוזלים — הידroסטטיקה ודינמיקה (אוניברסיטה)",
        "duration_min": 25,
    },
    "center_of_mass_uni": {
        "title_en": "Center of Mass & Systems of Particles (University)",
        "title_he": "מרכז מסה ומערכות חלקיקים (אוניברסיטה)",
        "duration_min": 24,
    },
    "angular_momentum_particles": {
        "title_en": "Angular Momentum & Rotation (University)",
        "title_he": "תנע זוויתי וסיבוב (אוניברסיטה)",
        "duration_min": 26,
    },
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


def _opts(items):
    return [{"id": oid, "text_en": en, "text_he": he, "correct": ok} for oid, en, he, ok in items]


LESSONS: list[dict] = [
    {
        "id": "rigid_body_torque_equilibrium",
        "subject": SUBJECT,
        "title_en": INDEX_ENTRIES["rigid_body_torque_equilibrium"]["title_en"],
        "title_he": INDEX_ENTRIES["rigid_body_torque_equilibrium"]["title_he"],
        "duration_min": 26,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Torque is a vector: $\\vec{\\tau}=\\vec{r}\\times\\vec{F}$; sign comes from the right-hand rule, "
            "not from 'clockwise'. Static equilibrium requires BOTH $\\sum\\vec{F}=0$ and $\\sum\\vec{\\tau}=0$ "
            "about any point — pivot at an unknown force eliminates that force from the torque equation. "
            "Common errors: using $\\tau=rF$ without $\\sin\\theta$; forgetting the beam's own weight acts at its CM."
        ),
        "sections": [
            _section(
                "torque_definition",
                "Torque — Vector Cross Product",
                "מומנט — מכפלה וקטורית",
                (
                    "The **torque** about point $O$ due to force $\\vec{F}$ applied at position "
                    "$\\vec{r}$ (from $O$ to the point of application) is:\n\n"
                    "$$\\boxed{\\vec{\\tau} = \\vec{r} \\times \\vec{F}}$$\n\n"
                    "**Magnitude:** $\\tau = rF\\sin\\theta$, where $\\theta$ is the angle between "
                    "$\\vec{r}$ and $\\vec{F}$.\n\n"
                    "**Direction:** right-hand rule — curl fingers from $\\vec{r}$ toward $\\vec{F}$; "
                    "thumb gives $\\vec{\\tau}$.\n\n"
                    "Only the **perpendicular** component of $\\vec{F}$ to $\\vec{r}$ contributes. "
                    "If $\\vec{F}$ is parallel to $\\vec{r}$ (line of action passes through $O$), "
                    "$\\tau = 0$.\n\n"
                    "**Units:** N·m (not joules — torque is a pseudovector)."
                ),
                (
                    "**מומנט** סביב נקודה $O$ עקב כוח $\\vec{F}$ בנקודה $\\vec{r}$ (מ-$O$ לנקודת הפעלה):\n\n"
                    "$$\\boxed{\\vec{\\tau} = \\vec{r} \\times \\vec{F}}$$\n\n"
                    "**גודל:** $\\tau = rF\\sin\\theta$, כאשר $\\theta$ הזווית בין $\\vec{r}$ ל-$\\vec{F}$.\n\n"
                    "**כיוון:** כלל היד הימנית — מ-$\\vec{r}$ ל-$\\vec{F}$; האגודל נותן $\\vec{\\tau}$.\n\n"
                    "רק הרכיב **המאונך** של $\\vec{F}$ ל-$\\vec{r}$ תורם. אם קו הפעולה עובר דרך $O$, $\\tau=0$.\n\n"
                    "**יחידות:** N·m."
                ),
            ),
            _section(
                "static_equilibrium",
                "Static Equilibrium Conditions",
                "תנאי שיווי משקל סטטי",
                (
                    "A rigid body in **static equilibrium** satisfies:\n\n"
                    "$$\\boxed{\\sum \\vec{F} = 0 \\qquad \\text{and} \\qquad \\sum \\vec{\\tau} = 0}$$\n\n"
                    "The torque sum must vanish **about any pivot point** you choose — if it holds "
                    "about one point, it holds about all (when $\\sum\\vec{F}=0$).\n\n"
                    "**Strategy:**\n"
                    "1. Draw a free-body diagram.\n"
                    "2. Write $\\sum F_x = 0$, $\\sum F_y = 0$ (and $F_z$ if needed).\n"
                    "3. Choose a pivot; write $\\sum \\tau = 0$ (sign convention consistent).\n"
                    "4. Solve the linear system.\n\n"
                    "You have at most 3 independent force equations + 3 torque equations in 3D; "
                    "in 2D problems, typically 2 force + 1 torque equation suffice."
                ),
                (
                    "גוף קשיח ב**שיווי משקל סטטי** מקיים:\n\n"
                    "$$\\boxed{\\sum \\vec{F} = 0 \\qquad \\text{ו} \\qquad \\sum \\vec{\\tau} = 0}$$\n\n"
                    "סכום המומנטים חייב להיעלם **סביב כל נקודת ציר** — אם זה נכון לנקודה אחת ו-$\\sum\\vec{F}=0$, "
                    "זה נכון לכולן.\n\n"
                    "**אסטרטגיה:**\n"
                    "1. דיאגרמת כוחות חופשית.\n"
                    "2. $\\sum F_x = 0$, $\\sum F_y = 0$.\n"
                    "3. בחרו ציר; $\\sum \\tau = 0$.\n"
                    "4. פתרו את המערכת."
                ),
            ),
            _section(
                "pivot_choice",
                "Choosing the Pivot — Eliminating Unknowns",
                "בחירת ציר — ביטול כוחות לא ידועים",
                (
                    "Place the pivot at the line of action of an **unknown force** to eliminate it "
                    "from the torque equation (since $r_\\perp = 0$ for that force).\n\n"
                    "**Best choices:**\n"
                    "- Hinge when finding cable tension.\n"
                    "- Contact point when finding friction at the other end.\n"
                    "- Any point where two unknowns intersect.\n\n"
                    "You may write multiple torque equations about different pivots if needed, "
                    "but one well-chosen pivot often suffices.\n\n"
                    "**Caution:** The eliminated force still appears in $\\sum\\vec{F}=0$ — "
                    "you need both force and torque balance."
                ),
                (
                    "מקמו את הציר על **קו הפעולה** של כוח **לא ידוע** כדי לבטל אותו ממשוואת המומent "
                    "(כי $r_\\perp = 0$).\n\n"
                    "**בחירות טובות:**\n"
                    "- ציר (hinge) בחיפוש מתיחות כבל.\n"
                    "- נקודת מגע בחיפוש חיכוך בקצה השני.\n\n"
                    "הכוח שבוטל עדיין מופיע ב-$\\sum\\vec{F}=0$ — נדרשות שתי המשוואות."
                ),
            ),
            _section(
                "worked_beam",
                "Worked Example — Supported Beam",
                "דוגמה מלאה — קורה מונחת",
                (
                    "**Problem:** A uniform horizontal beam of mass $M$ and length $L$ is attached to a "
                    "wall by a hinge at one end. A cable at the far end makes angle $\\theta$ **above** "
                    "the horizontal. An additional mass $m$ hangs at the midpoint. Find cable tension "
                    "$T$ and hinge reaction $\\vec{H}$.\n\n"
                    "**Torque about hinge** (eliminates $\\vec{H}$):\n"
                    "Weights $(M+m)g$ act at $L/2$ (clockwise); cable vertical component $T\\sin\\theta$ "
                    "at $L$ (counterclockwise):\n"
                    "$$T L \\sin\\theta = (M+m)g\\frac{L}{2}$$\n"
                    "$$\\boxed{T = \\frac{(M+m)g}{2\\sin\\theta}}$$\n\n"
                    "**Forces:**\n"
                    "$H_x = T\\cos\\theta = \\dfrac{(M+m)g\\cos\\theta}{2\\sin\\theta}$\n\n"
                    "$H_y + T\\sin\\theta = (M+m)g \\Rightarrow H_y = \\dfrac{(M+m)g}{2}$\n\n"
                    "Note: vertical hinge reaction supports half the total weight; horizontal component "
                    "balances cable tension's $x$-component."
                ),
                (
                    "**בעיה:** קורה אופקית אחידה מסה $M$ ואורך $L$ מחוברת בציר לקיר. כבל בקצה הרחוק "
                    "יוצר זווית $\\theta$ **מעל** האופק. מסה $m$ תלויה באמצע. מצאו $T$ ו-$\\vec{H}$.\n\n"
                    "**מומנט סביב הציר:**\n"
                    "$$T L \\sin\\theta = (M+m)g\\frac{L}{2} \\Rightarrow "
                    "\\boxed{T = \\frac{(M+m)g}{2\\sin\\theta}}$$\n\n"
                    "**כוחות:** $H_x = T\\cos\\theta$, $H_y = (M+m)g/2$."
                ),
            ),
            _section(
                "moment_of_inertia",
                "Moment of Inertia — Overview",
                "מומנט אינרציה — סקירה",
                (
                    "For continuous mass distribution about axis through $O$:\n"
                    "$$\\boxed{I = \\int r^2\\,dm}$$\n\n"
                    "where $r$ is perpendicular distance from the axis.\n\n"
                    "**Common values** (memorize for exams):\n\n"
                    "| Body | Axis | $I$ |\n"
                    "|---|---|---|\n"
                    "| Thin rod, length $L$ | Center | $ML^2/12$ |\n"
                    "| Thin rod | End | $ML^2/3$ |\n"
                    "| Solid disk, radius $R$ | Center | $MR^2/2$ |\n"
                    "| Point mass $M$ at $R$ | Pivot | $MR^2$ |\n\n"
                    "**Parallel-axis theorem:** $I = I_{cm} + Md^2$ where $d$ is shift of axis."
                ),
                (
                    "להתפלגות מסה רציפה סביב ציר דרך $O$:\n"
                    "$$\\boxed{I = \\int r^2\\,dm}$$\n\n"
                    "**ערכים נפוצים:**\n\n"
                    "| גוף | ציר | $I$ |\n"
                    "|---|---|---|\n"
                    "| מוט דק, אורך $L$ | מרכז | $ML^2/12$ |\n"
                    "| מוט דק | קצה | $ML^2/3$ |\n"
                    "| דиск מלא, רדיוס $R$ | מרכז | $MR^2/2$ |\n"
                    "| מטען נקודתי $M$ ב-$R$ | ציר | $MR^2$ |\n\n"
                    "**משפט הצירים המקבילים:** $I = I_{cm} + Md^2$."
                ),
            ),
            _section(
                "rotational_newton",
                "Rotational Dynamics — $\\tau_{net} = I\\alpha$",
                "דינמיקה סיבובית — $\\tau_{net} = I\\alpha$",
                (
                    "The rotational analog of Newton's second law:\n"
                    "$$\\boxed{\\sum \\tau_{net} = I\\alpha}$$\n\n"
                    "where $\\alpha = d\\omega/dt$ is angular acceleration (rad/s²).\n\n"
                    "Applies about a **fixed axis** through a point where external forces "
                    "produce no net torque, or about the center of mass for free rotation.\n\n"
                    "Combine with $\\sum\\vec{F}=M\\vec{a}_{cm}$ for rolling and coupled motion problems."
                ),
                (
                    "האנalog הסיבובי לחוק השני של ניוטון:\n"
                    "$$\\boxed{\\sum \\tau_{net} = I\\alpha}$$\n\n"
                    "כאשר $\\alpha = d\\omega/dt$ (rad/s²).\n\n"
                    "תקף ל**ציר קבוע** או סביב מרכז המסה לסיבוב חופשי.\n\n"
                    "שלבו עם $\\sum\\vec{F}=M\\vec{a}_{cm}$ לבעיות גלגול."
                ),
            ),
            _section(
                "worked_rod_alpha",
                "Worked Example — Rod Under Horizontal Force",
                "דוגמה — מוט תחת כוח אופקי",
                (
                    "**Problem:** Uniform rod mass $M$, length $L$, pivoted at one end (no gravity). "
                    "Horizontal force $F$ applied **perpendicular** to the rod at its midpoint. Find $\\alpha$.\n\n"
                    "Torque about pivot: $\\tau = F \\cdot (L/2)$.\n\n"
                    "Moment of inertia about end: $I = ML^2/3$.\n\n"
                    "$$\\alpha = \\frac{\\tau}{I} = \\frac{FL/2}{ML^2/3} = \\boxed{\\frac{3F}{2ML}}$$\n\n"
                    "Direction: force pushes midpoint in $+x$; torque about pivot is out of page "
                    "(if rod along $+y$), so $\\alpha$ is counterclockwise."
                ),
                (
                    "**בעיה:** מוט אחיד $M$, $L$, נתמך בקצה. כוח אופקי $F$ **מאונך** למוט באמצע. מצאו $\\alpha$.\n\n"
                    "$\\tau = FL/2$, $I = ML^2/3$:\n"
                    "$$\\alpha = \\frac{3F}{2ML}$$"
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "Force $\\vec{F} = F\\hat{\\mathbf{y}}$ acts at $\\vec{r} = L\\hat{\\mathbf{x}}$ from pivot $O$. "
                "What is $\\vec{\\tau}$ about $O$?",
                "כוח $\\vec{F} = F\\hat{\\mathbf{y}}$ פועל ב-$\\vec{r} = L\\hat{\\mathbf{x}}$ מ-$O$. מהו $\\vec{\\tau}$?",
                _opts([
                    ("a", "$FL\\,\\hat{\\mathbf{z}}$", "$FL\\,\\hat{\\mathbf{z}}$", True),
                    ("b", "$-FL\\,\\hat{\\mathbf{z}}$", "$-FL\\,\\hat{\\mathbf{z}}$", False),
                    ("c", "$FL\\,\\hat{\\mathbf{x}}$", "$FL\\,\\hat{\\mathbf{x}}$", False),
                    ("d", "$\\vec{0}$", "$\\vec{0}$", False),
                ]),
                "$\\vec{\\tau} = \\hat{\\mathbf{x}}\\times\\hat{\\mathbf{y}}\\,FL = \\hat{\\mathbf{z}}\\,FL$ (right-hand rule).",
                "$\\vec{\\tau} = \\hat{\\mathbf{x}}\\times\\hat{\\mathbf{y}}\\,FL = \\hat{\\mathbf{z}}\\,FL$ (כלל יד-ימין).",
            ),
            _mcq(
                "q2",
                "In the beam problem ($M$, $m$, cable angle $\\theta$ above horizontal), the cable tension is:",
                "בבעיית הקורה ($M$, $m$, זווית כבל $\\theta$ מעל האופק), מתיחות הכבל היא:",
                _opts([
                    ("a", "$T = (M+m)g/(2\\sin\\theta)$", "$T = (M+m)g/(2\\sin\\theta)$", True),
                    ("b", "$T = (M+m)g/(2\\cos\\theta)$", "$T = (M+m)g/(2\\cos\\theta)$", False),
                    ("c", "$T = (M+m)g/\\sin\\theta$", "$T = (M+m)g/\\sin\\theta$", False),
                    ("d", "$T = mg/(2\\sin\\theta)$", "$T = mg/(2\\sin\\theta)$", False),
                ]),
                "Torque about hinge: $TL\\sin\\theta = (M+m)g(L/2)$ gives $T=(M+m)g/(2\\sin\\theta)$.",
                "מומנט סביב הציר: $TL\\sin\\theta = (M+m)g(L/2)$ נותן $T=(M+m)g/(2\\sin\\theta)$.",
            ),
            _mcq(
                "q3",
                "To find an unknown hinge force in a static beam problem, the best first step is:",
                "למציאת כוח ציר לא ידוע בבעיית קורה סטטית, הצעד הראשון הטוב ביותר:",
                _opts([
                    ("a", "Take torques about the hinge to eliminate hinge forces from $\\sum\\tau=0$", "מומנטים סביב הציר כדי לבטל כוחות ציר מ-$\\sum\\tau=0$", True),
                    ("b", "Take torques about the cable attachment only", "מומנטים רק סביב נקודת הכבל", False),
                    ("c", "Ignore torque and use only $\\sum F_x=0$", "להתעלם ממומנט ולהשתמש רק ב-$\\sum F_x=0$", False),
                    ("d", "Apply $\\tau=I\\alpha$ with $\\alpha=0$ about any point", "להפעיל $\\tau=I\\alpha$ עם $\\alpha=0$", False),
                ]),
                "Pivot at the hinge zeroes the lever arm of both hinge force components in the torque equation.",
                "ציר ב-hinge מאפס את זרוע המומנט של רכיבי כוח הציר.",
            ),
            _mcq(
                "q4",
                "A solid disk of mass $M$ and radius $R$ rotates about its center. Its moment of inertia is:",
                "דיסק מלא מסה $M$ רדיוס $R$ מסתובב סביב מרכזו. מומנט האינרציה:",
                _opts([
                    ("a", "$MR^2/2$", "$MR^2/2$", True),
                    ("b", "$MR^2$", "$MR^2$", False),
                    ("c", "$2MR^2/5$", "$2MR^2/5$", False),
                    ("d", "$ML^2/12$", "$ML^2/12$", False),
                ]),
                "Solid disk about center: $I = \\int r^2\\,dm = MR^2/2$. Option (c) is a solid sphere.",
                "דיסק מלא סביב מרכז: $I = MR^2/2$. (c) הוא כדור מלא.",
            ),
            _mcq(
                "q5",
                "Uniform rod ($M$, $L$) pivoted at end; horizontal force $F$ at midpoint (no gravity). "
                "Angular acceleration $\\alpha$ equals:",
                "מוט אחיד ($M$, $L$) בציר בקצה; כוח אופקי $F$ באמצע (ללא כבידה). $\\alpha$ שווה:",
                _opts([
                    ("a", "$3F/(2ML)$", "$3F/(2ML)$", True),
                    ("b", "$F/(ML)$", "$F/(ML)$", False),
                    ("c", "$2F/(ML)$", "$2F/(ML)$", False),
                    ("d", "$6F/(ML)$", "$6F/(ML)$", False),
                ]),
                "$\\tau=FL/2$, $I=ML^2/3$, so $\\alpha=\\tau/I=3F/(2ML)$.",
                "$\\tau=FL/2$, $I=ML^2/3$, לכן $\\alpha=3F/(2ML)$.",
            ),
        ],
    },
    {
        "id": "harmonic_oscillation",
        "subject": SUBJECT,
        "title_en": INDEX_ENTRIES["harmonic_oscillation"]["title_en"],
        "title_he": INDEX_ENTRIES["harmonic_oscillation"]["title_he"],
        "duration_min": 24,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "SHM is defined by $a=-\\omega^2 x$, not merely 'sinusoidal looking'. Students confuse "
            "$\\omega$ (rad/s) with $f$ (Hz) and $T$. For energy, $E=\\frac{1}{2}kA^2$ is constant; "
            "at general $x$, $KE+PE=kA^2/2$. Small-angle pendulum requires $\\theta\\lesssim 15°$."
        ),
        "sections": [
            _section(
                "shm_definition",
                "Simple Harmonic Motion — Definition and Solution",
                "תנועה הרמונית פשוטה — הגדרה ופתרון",
                (
                    "**Definition:** motion with acceleration proportional and opposite to displacement:\n"
                    "$$\\boxed{a = -\\omega^2 x}$$\n\n"
                    "General solution:\n"
                    "$$\\boxed{x(t) = A\\cos(\\omega t + \\phi)}$$\n\n"
                    "$A$ = amplitude, $\\omega$ = angular frequency (rad/s), $\\phi$ = phase constant "
                    "(fixed by initial $x_0$, $v_0$).\n\n"
                    "Period: $T = 2\\pi/\\omega$. Frequency: $f = 1/T = \\omega/(2\\pi)$."
                ),
                (
                    "**הגדרה:** תאוצה פרופורציונית ונגדית להעתק:\n"
                    "$$\\boxed{a = -\\omega^2 x}$$\n\n"
                    "פתרון כללי:\n"
                    "$$\\boxed{x(t) = A\\cos(\\omega t + \\phi)}$$\n\n"
                    "$A$ = מplitudה, $\\omega$ = תדירות זוויתית, $\\phi$ = קבוע פазה.\n\n"
                    "זמן מחזור: $T = 2\\pi/\\omega$."
                ),
            ),
            _section(
                "shm_kinematics",
                "Velocity and Acceleration in SHM",
                "מהירות ותאוצה ב-SHM",
                (
                    "Differentiate $x(t) = A\\cos(\\omega t + \\phi)$:\n\n"
                    "$$v(t) = \\frac{dx}{dt} = -A\\omega\\sin(\\omega t + \\phi)$$\n\n"
                    "$$a(t) = \\frac{dv}{dt} = -A\\omega^2\\cos(\\omega t + \\phi) = -\\omega^2 x(t)$$\n\n"
                    "**Key relations:**\n"
                    "- $|v|_{max} = A\\omega$ at $x=0$.\n"
                    "- $|a|_{max} = A\\omega^2$ at $|x|=A$.\n"
                    "- $v$ leads $x$ by $90°$; $a$ is antiparallel to $x$."
                ),
                (
                    "גזירה של $x(t) = A\\cos(\\omega t + \\phi)$:\n\n"
                    "$$v = -A\\omega\\sin(\\omega t + \\phi), \\quad a = -A\\omega^2\\cos(\\omega t + \\phi) = -\\omega^2 x$$\n\n"
                    "$|v|_{max} = A\\omega$ ב-$x=0$; $|a|_{max} = A\\omega^2$ ב-$|x|=A$."
                ),
            ),
            _section(
                "spring_mass",
                "Spring–Mass System",
                "מערכת קפיץ–מסה",
                (
                    "Hooke's law: $F = -kx$ gives $m\\ddot{x} = -kx$, so:\n"
                    "$$\\boxed{\\omega = \\sqrt{\\frac{k}{m}}, \\qquad T = 2\\pi\\sqrt{\\frac{m}{k}}}$$\n\n"
                    "Independent of amplitude $A$ (ideal spring, no damping).\n\n"
                    "Multiple springs / masses: reduce to equivalent $k_{eq}$, $m_{eq}$."
                ),
                (
                    "חוק הוק: $F = -kx$ נותן $m\\ddot{x} = -kx$:\n"
                    "$$\\boxed{\\omega = \\sqrt{k/m}, \\quad T = 2\\pi\\sqrt{m/k}}$$\n\n"
                    "לא תלוי ב-$A$ (קפיץ אידיאלי, ללא ריסון)."
                ),
            ),
            _section(
                "simple_pendulum",
                "Simple Pendulum — Small Angles",
                "מטוטלת פשוטה — זוויות קטנות",
                (
                    "For string length $L$ and small angle $\\theta$ (in radians, $\\theta \\lesssim 15°$):\n"
                    "$$\\sin\\theta \\approx \\theta \\quad \\Rightarrow \\quad \\ddot{\\theta} = -\\frac{g}{L}\\theta$$\n\n"
                    "$$\\boxed{\\omega = \\sqrt{\\frac{g}{L}}, \\qquad T = 2\\pi\\sqrt{\\frac{L}{g}}}$$\n\n"
                    "Valid only for small oscillations; large angles increase period."
                ),
                (
                    "למוט אורך $L$ וזווית קטנה $\\theta$ (רדיאנים, $\\theta \\lesssim 15°$):\n"
                    "$$\\omega = \\sqrt{g/L}, \\quad T = 2\\pi\\sqrt{L/g}$$\n\n"
                    "תקף רק לתנודות קטנות."
                ),
            ),
            _section(
                "shm_energy",
                "Energy in SHM",
                "אנרגיה ב-SHM",
                (
                    "Total mechanical energy (no damping):\n"
                    "$$\\boxed{E = \\frac{1}{2}kA^2 = \\frac{1}{2}m v_{max}^2}$$\n\n"
                    "At displacement $x$:\n"
                    "$$KE = \\frac{1}{2}k(A^2 - x^2), \\qquad PE = \\frac{1}{2}kx^2$$\n\n"
                    "Energy oscillates between kinetic and potential; $E$ is constant."
                ),
                (
                    "אנרגיה מכנית כוללת:\n"
                    "$$E = \\frac{1}{2}kA^2 = \\frac{1}{2}mv_{max}^2$$\n\n"
                    "בהעתק $x$: $KE = \\frac{1}{2}k(A^2-x^2)$, $PE = \\frac{1}{2}kx^2$."
                ),
            ),
            _section(
                "damped_oscillations",
                "Damped Oscillations — Overview",
                "תנודות מרוסנות — סקירה",
                (
                    "Linear damping: $F_{damp} = -b\\dot{x}$ gives:\n"
                    "$$m\\ddot{x} + b\\dot{x} + kx = 0$$\n\n"
                    "Define $\\gamma = b/(2m)$, $\\omega_0 = \\sqrt{k/m}$.\n\n"
                    "**Underdamped** ($\\gamma < \\omega_0$):\n"
                    "$$x(t) = Ae^{-\\gamma t}\\cos(\\omega' t + \\phi), \\quad \\omega' = \\sqrt{\\omega_0^2 - \\gamma^2}$$\n\n"
                    "**Critical:** $\\gamma = \\omega_0$ (fastest return without oscillation).\n"
                    "**Overdamped:** $\\gamma > \\omega_0$ (exponential decay, no oscillation).\n\n"
                    "Quality factor: $Q \\approx \\omega_0/(2\\gamma)$ (energy decay per cycle)."
                ),
                (
                    "ריסון לינארי: $F_{damp} = -b\\dot{x}$:\n"
                    "$$m\\ddot{x} + b\\dot{x} + kx = 0$$\n\n"
                    "**תחת-ריסון** ($\\gamma < \\omega_0$): $x = Ae^{-\\gamma t}\\cos(\\omega' t + \\phi)$.\n"
                    "**קריטי:** $\\gamma = \\omega_0$. **יתר-ריסון:** $\\gamma > \\omega_0$."
                ),
            ),
            _section(
                "physical_pendulum",
                "Physical Pendulum",
                "מטוטלת פיזיקלית",
                (
                    "Rigid body pivoting about fixed point: torque about pivot "
                    "$\\tau = -MgL_{cm}\\sin\\theta \\approx -MgL_{cm}\\theta$ for small $\\theta$.\n\n"
                    "$$\\boxed{\\omega = \\sqrt{\\frac{MgL_{cm}}{I_{pivot}}}, \\qquad "
                    "T = 2\\pi\\sqrt{\\frac{I_{pivot}}{MgL_{cm}}}}$$\n\n"
                    "$L_{cm}$ = distance from pivot to center of mass; $I_{pivot}$ about pivot axis."
                ),
                (
                    "גוף קשיח סביב נקודה קבועה:\n"
                    "$$\\omega = \\sqrt{MgL_{cm}/I_{pivot}}, \\quad T = 2\\pi\\sqrt{I_{pivot}/(MgL_{cm})}$$\n\n"
                    "$L_{cm}$ = מרחק מציר למרכז מסה; $I_{pivot}$ סביב הציר."
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "A mass $m = 0.25\\;\\text{kg}$ on a spring with $k = 100\\;\\text{N/m}$. "
                "The angular frequency $\\omega$ is:",
                "מסה $m = 0.25\\;\\text{kg}$ על קפיץ $k = 100\\;\\text{N/m}$. התדירות $\\omega$:",
                _opts([
                    ("a", "$20\\;\\text{rad/s}$", "$20\\;\\text{rad/s}$", True),
                    ("b", "$10\\;\\text{rad/s}$", "$10\\;\\text{rad/s}$", False),
                    ("c", "$40\\;\\text{rad/s}$", "$40\\;\\text{rad/s}$", False),
                    ("d", "$400\\;\\text{rad/s}$", "$400\\;\\text{rad/s}$", False),
                ]),
                "$\\omega = \\sqrt{k/m} = \\sqrt{100/0.25} = \\sqrt{400} = 20$ rad/s.",
                "$\\omega = \\sqrt{k/m} = \\sqrt{400} = 20$ rad/s.",
            ),
            _mcq(
                "q2",
                "SHM with $k=50\\;\\text{N/m}$, $A=0.20\\;\\text{m}$. At $x=0.12\\;\\text{m}$, kinetic energy is:",
                "SHM עם $k=50$, $A=0.20$. ב-$x=0.12$, האנרגיה הקינטית:",
                _opts([
                    ("a", "$0.64\\;\\text{J}$", "$0.64\\;\\text{J}$", True),
                    ("b", "$0.36\\;\\text{J}$", "$0.36\\;\\text{J}$", False),
                    ("c", "$1.00\\;\\text{J}$", "$1.00\\;\\text{J}$", False),
                    ("d", "$0.72\\;\\text{J}$", "$0.72\\;\\text{J}$", False),
                ]),
                "$KE = \\frac{1}{2}k(A^2-x^2) = 25(0.04-0.0144) = 25(0.0256) = 0.64$ J.",
                "$KE = \\frac{1}{2}k(A^2-x^2) = 0.64$ J.",
            ),
            _mcq(
                "q3",
                "A pendulum with $L=1.0\\;\\text{m}$ on Earth ($g=9.8$) is taken to the Moon ($g=1.6$). "
                "The period on the Moon compared to Earth is:",
                "מטוטלת $L=1.0$ m על כדור הארץ ($g=9.8$) מועברת לירח ($g=1.6$). זמן המחזור על הירח:",
                _opts([
                    ("a", "Longer by factor $\\sqrt{9.8/1.6} \\approx 2.5$", "ארוך יותר בגורם $\\sqrt{9.8/1.6} \\approx 2.5$", True),
                    ("b", "Shorter by factor $\\sqrt{9.8/1.6}$", "קצר יותר", False),
                    ("c", "Unchanged", "ללא שינוי", False),
                    ("d", "Longer by factor $9.8/1.6$", "ארוך בגורם $9.8/1.6$", False),
                ]),
                "$T \\propto 1/\\sqrt{g}$; lower $g$ on Moon $\\Rightarrow$ longer $T$ by $\\sqrt{g_E/g_M}$.",
                "$T \\propto 1/\\sqrt{g}$; $g$ קטן יותר על הירח $\\Rightarrow$ $T$ ארוך יותר.",
            ),
            _mcq(
                "q4",
                "For $m\\ddot{x}+b\\dot{x}+kx=0$ with $\\omega_0=10\\;\\text{rad/s}$ and $b/(2m)=12\\;\\text{s}^{-1}$, "
                "the motion is:",
                "עבור $\\omega_0=10$ ו-$b/(2m)=12$, התנועה:",
                _opts([
                    ("a", "Overdamped (no oscillation)", "יתר-ריסון (ללא תנודה)", True),
                    ("b", "Underdamped (decaying oscillation)", "תחת-ריסון", False),
                    ("c", "Critically damped", "ריסון קריטי", False),
                    ("d", "Undamped SHM", "SHM ללא ריסון", False),
                ]),
                "$\\gamma=12 > \\omega_0=10$ $\\Rightarrow$ overdamped.",
                "$\\gamma > \\omega_0$ $\\Rightarrow$ יתר-ריסון.",
            ),
            _mcq(
                "q5",
                "Uniform rod length $L$, mass $M$, pivoted at one end. For small oscillations, "
                "$\\omega$ equals:",
                "מוט אחיד $L$, $M$, ציר בקצה. לתנודות קטנות, $\\omega$:",
                _opts([
                    ("a", "$\\sqrt{3g/(2L)}$", "$\\sqrt{3g/(2L)}$", True),
                    ("b", "$\\sqrt{g/L}$", "$\\sqrt{g/L}$", False),
                    ("c", "$\\sqrt{g/(2L)}$", "$\\sqrt{g/(2L)}$", False),
                    ("d", "$\\sqrt{2g/L}$", "$\\sqrt{2g/L}$", False),
                ]),
                "$L_{cm}=L/2$, $I_{pivot}=ML^2/3$: $\\omega=\\sqrt{Mg(L/2)/(ML^2/3)}=\\sqrt{3g/(2L)}$.",
                "$\\omega=\\sqrt{Mg(L/2)/(ML^2/3)}=\\sqrt{3g/(2L)}$.",
            ),
        ],
    },
    {
        "id": "fluids_hydrostatics",
        "subject": SUBJECT,
        "title_en": INDEX_ENTRIES["fluids_hydrostatics"]["title_en"],
        "title_he": INDEX_ENTRIES["fluids_hydrostatics"]["title_he"],
        "duration_min": 25,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "Pressure is scalar; $P=P_0+\\rho gh$ holds in static fluids. Buoyant force equals weight of "
            "displaced fluid, not weight of object. Bernoulli applies along a streamline for ideal flow; "
            "continuity gives speed change when area narrows."
        ),
        "sections": [
            _section(
                "pressure_hydrostatic",
                "Pressure and Hydrostatic Law",
                "לחץ וחוק הידroסטטי",
                (
                    "**Pressure:** force per unit area (scalar):\n"
                    "$$P = \\frac{F}{A}$$\n\n"
                    "In a static fluid at depth $h$ below free surface (density $\\rho$):\n"
                    "$$\\boxed{P = P_0 + \\rho g h}$$\n\n"
                    "$P_0$ = atmospheric pressure at surface. Pressure increases linearly with depth."
                ),
                (
                    "**לחץ:** כוח ליחידת שטח (סקalar):\n"
                    "$$P = F/A$$\n\n"
                    "בנוזל סטטי בעומק $h$:\n"
                    "$$\\boxed{P = P_0 + \\rho g h}$$"
                ),
            ),
            _section(
                "pascal_archimedes",
                "Pascal's Principle and Archimedes' Law",
                "עקרון פסקל וחוק ארכימדס",
                (
                    "**Pascal:** pressure change at one point in enclosed fluid transmits undiminished "
                    "to all points (hydraulic lift).\n\n"
                    "**Archimedes:** buoyant force on submerged object:\n"
                    "$$\\boxed{F_b = \\rho_{fluid}\\, g\\, V_{submerged}}$$\n\n"
                    "Equals weight of displaced fluid. **Floating:** "
                    "$\\rho_{obj} V_{obj} = \\rho_{fluid} V_{submerged}$."
                ),
                (
                    "**פסקל:** שינוי לחץ מועבר לכל הנקודות.\n\n"
                    "**ארכימדס:**\n"
                    "$$F_b = \\rho_{fluid}\\, g\\, V_{submerged}$$\n\n"
                    "**צף:** $\\rho_{obj} V_{obj} = \\rho_{fluid} V_{submerged}$."
                ),
            ),
            _section(
                "floating_fraction",
                "Worked Example — Floating Block",
                "דוגמה — בלוק צף",
                (
                    "**Problem:** Block density $\\rho_1$ floats in fluid density $\\rho_2 > \\rho_1$. "
                    "What fraction $f$ of volume is submerged?\n\n"
                    "Float: weight = buoyant force:\n"
                    "$$\\rho_1 V g = \\rho_2 (fV) g \\Rightarrow \\boxed{f = \\rho_1/\\rho_2}$$\n\n"
                    "Example: ice ($\\rho\\approx920$ kg/m³) in water: $f\\approx0.92$."
                ),
                (
                    "**בעיה:** צפיפות $\\rho_1$ צף בנוזל $\\rho_2 > \\rho_1$. איזה חלק $f$ טבוע?\n\n"
                    "$$\\rho_1 V g = \\rho_2 fV g \\Rightarrow f = \\rho_1/\\rho_2$$"
                ),
            ),
            _section(
                "continuity",
                "Continuity Equation",
                "משוואת רציפות",
                (
                    "For **incompressible** steady flow:\n"
                    "$$\\boxed{A_1 v_1 = A_2 v_2 = Q}$$\n\n"
                    "$Q$ = volume flow rate (m³/s). Narrower pipe $\\Rightarrow$ higher speed."
                ),
                (
                    "לזרימה **דחוסה** קבועה:\n"
                    "$$A_1 v_1 = A_2 v_2 = Q$$\n\n"
                    "צינור צר $\\Rightarrow$ מהירות גבוהה יותר."
                ),
            ),
            _section(
                "bernoulli",
                "Bernoulli's Equation",
                "משוואת ברנולי",
                (
                    "Along a streamline (ideal, incompressible, steady, no viscosity):\n"
                    "$$\\boxed{P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}}$$\n\n"
                    "Terms: static pressure + dynamic pressure + hydrostatic pressure."
                ),
                (
                    "לאורך קו זרימה (אידיאלי, דחוס, קבוע, ללא צמיגות):\n"
                    "$$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$$"
                ),
            ),
            _section(
                "bernoulli_apps",
                "Applications — Venturi, Torricelli, Lift",
                "יישומים — Venturi, טוריצ'לי, העילוי",
                (
                    "**Venturi meter:** narrow throat $\\Rightarrow$ higher $v$ $\\Rightarrow$ lower $P$ "
                    "(pressure difference measures flow rate).\n\n"
                    "**Torricelli's theorem** (tank with hole at depth $h$):\n"
                    "$$v = \\sqrt{2gh}$$\n\n"
                    "**Airplane lift (qualitative):** faster flow over curved upper wing "
                    "$\\Rightarrow$ lower pressure above $\\Rightarrow$ net upward force."
                ),
                (
                    "**Venturi:** צוואר צר $\\Rightarrow$ $v$ גבוה $\\Rightarrow$ $P$ נמוך.\n\n"
                    "**טוריצ'לי:** $v = \\sqrt{2gh}$.\n\n"
                    "**העילוי:** זרימה מהירה מעל כנף $\\Rightarrow$ לחץ נמוך מעל."
                ),
            ),
            _section(
                "pipe_worked",
                "Worked Example — Narrowing Pipe",
                "דוגמה — צינור מתעצם",
                (
                    "**Problem:** Water ($\\rho=1000$ kg/m³) flows in horizontal pipe: "
                    "$r_1=0.10$ m, $v_1=2$ m/s; narrows to $r_2=0.05$ m. Find $v_2$ and "
                    "pressure change.\n\n"
                    "$A_1/A_2 = (0.10/0.05)^2 = 4 \\Rightarrow v_2 = 4(2) = \\boxed{8\\;\\text{m/s}}$\n\n"
                    "Horizontal Bernoulli ($h$ const):\n"
                    "$$P_1 - P_2 = \\tfrac{1}{2}\\rho(v_2^2 - v_1^2) = 500(64-4) = "
                    "\\boxed{3.0\\times10^4\\;\\text{Pa}}$$\n\n"
                    "Pressure **drops** in the narrow section."
                ),
                (
                    "**בעיה:** מים $\\rho=1000$: $r_1=0.10$, $v_1=2$; $r_2=0.05$. מצאו $v_2$ ושינוי לחץ.\n\n"
                    "$v_2 = 8$ m/s. $P_1-P_2 = 3.0\\times10^4$ Pa (ירידת לחץ)."
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "Water ($\\rho=1000$ kg/m³) in open tank. Gauge pressure at depth $h=5.0$ m is "
                "(take $g=10$ m/s²):",
                "מים ($\\rho=1000$) במיכל פתוח. לחץ מanomטרי בעומק $h=5.0$ m ($g=10$):",
                _opts([
                    ("a", "$5.0\\times10^4$ Pa", "$5.0\\times10^4$ Pa", True),
                    ("b", "$1.0\\times10^5$ Pa", "$1.0\\times10^5$ Pa", False),
                    ("c", "$2.5\\times10^4$ Pa", "$2.5\\times10^4$ Pa", False),
                    ("d", "$5.0\\times10^3$ Pa", "$5.0\\times10^3$ Pa", False),
                ]),
                "Gauge: $P=\\rho gh = 1000\\cdot10\\cdot5 = 5\\times10^4$ Pa.",
                "לחץ מanomטרי: $P=\\rho gh = 5\\times10^4$ Pa.",
            ),
            _mcq(
                "q2",
                "Object density $600$ kg/m³ in water ($\\rho=1000$). Will it float, and what fraction "
                "submerged at equilibrium?",
                "צפיפות $600$ kg/m³ במים ($1000$). האם יצף, ואיזה חלק טבוע?",
                _opts([
                    ("a", "Floats; 60% submerged", "צף; 60% טבוע", True),
                    ("b", "Sinks completely", "שוקע לגמרי", False),
                    ("c", "Floats; 40% submerged", "צף; 40% טבוע", False),
                    ("d", "Neutral buoyancy", "צף ללא תנועה", False),
                ]),
                "$\\rho_{obj}<\\rho_{fluid}$ $\\Rightarrow$ floats; $f=600/1000=0.60$.",
                "$\\rho_{obj}<\\rho_{fluid}$ $\\Rightarrow$ צף; $f=0.60$.",
            ),
            _mcq(
                "q3",
                "Pipe area halves ($A_2=A_1/2$). Incompressible flow: $v_2/v_1$ equals:",
                "שטח חתך מחצה ($A_2=A_1/2$). זרימה דחוסה: $v_2/v_1$:",
                _opts([
                    ("a", "$2$", "$2$", True),
                    ("b", "$1/2$", "$1/2$", False),
                    ("c", "$4$", "$4$", False),
                    ("d", "$1$", "$1$", False),
                ]),
                "$A_1 v_1 = A_2 v_2$ with $A_2=A_1/2$ gives $v_2=2v_1$.",
                "$A_1 v_1 = A_2 v_2$ נותן $v_2=2v_1$.",
            ),
            _mcq(
                "q4",
                "In a Venturi meter, fluid speed in the throat is higher than upstream. "
                "Pressure in the throat is:",
                "ב-Venturi, המהירות בצוואר גבוהה. הלחץ בצוואר:",
                _opts([
                    ("a", "Lower than upstream (Bernoulli)", "נמוך יותר (ברנולי)", True),
                    ("b", "Higher than upstream", "גבוה יותר", False),
                    ("c", "Same as upstream", "זהה", False),
                    ("d", "Zero", "אפס", False),
                ]),
                "Higher kinetic energy term $\\Rightarrow$ lower static pressure at constant $h$.",
                "אנרגיה קינטית גבוהה $\\Rightarrow$ לחץ סטטי נמוך.",
            ),
            _mcq(
                "q5",
                "Tank with water; small hole at depth $h=2.0$ m below surface ($g=10$). "
                "Exit speed (Torricelli) is:",
                "מיכל מים; חור בעומק $h=2.0$ m ($g=10$). מהירות יציאה (טוריצ'לי):",
                _opts([
                    ("a", "$\\sqrt{40}\\;\\text{m/s} \\approx 6.3$ m/s", "$\\sqrt{40}$ m/s", True),
                    ("b", "$20\\;\\text{m/s}$", "$20$ m/s", False),
                    ("c", "$\\sqrt{20}\\;\\text{m/s}$", "$\\sqrt{20}$ m/s", False),
                    ("d", "$2\\;\\text{m/s}$", "$2$ m/s", False),
                ]),
                "$v=\\sqrt{2gh}=\\sqrt{2\\cdot10\\cdot2}=\\sqrt{40}$ m/s.",
                "$v=\\sqrt{2gh}=\\sqrt{40}$ m/s.",
            ),
        ],
    },
    {
        "id": "center_of_mass_uni",
        "subject": SUBJECT,
        "title_en": INDEX_ENTRIES["center_of_mass_uni"]["title_en"],
        "title_he": INDEX_ENTRIES["center_of_mass_uni"]["title_he"],
        "duration_min": 24,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "CM motion follows $\\vec{F}_{ext}=M\\vec{a}_{cm}$ — internal forces cancel in pairs. "
            "Continuous CM requires $\\int \\vec{r}\\,dm$. Rocket equation uses variable mass; "
            "sign convention: $dM/dt<0$ as fuel burns."
        ),
        "sections": [
            _section(
                "discrete_cm",
                "Center of Mass — Discrete System",
                "מרכז מסה — מערכת בדידה",
                (
                    "For particles with masses $m_i$ at positions $\\vec{r}_i$:\n"
                    "$$\\boxed{\\vec{r}_{cm} = \\frac{\\sum_i m_i \\vec{r}_i}{M_{tot}}, "
                    "\\quad M_{tot} = \\sum_i m_i}$$\n\n"
                    "Velocity and momentum:\n"
                    "$$\\vec{v}_{cm} = \\frac{\\sum m_i \\vec{v}_i}{M_{tot}} = "
                    "\\frac{\\vec{p}_{tot}}{M_{tot}}$$"
                ),
                (
                    "לחלקיקים $m_i$ במיקומים $\\vec{r}_i$:\n"
                    "$$\\vec{r}_{cm} = \\frac{\\sum m_i \\vec{r}_i}{M_{tot}}$$\n\n"
                    "$$\\vec{v}_{cm} = \\frac{\\vec{p}_{tot}}{M_{tot}}$$"
                ),
            ),
            _section(
                "continuous_cm",
                "Continuous Body — Integral Definition",
                "גוף רציף — הגדרה אינטגרלית",
                (
                    "For continuous mass distribution with density $\\rho$:\n"
                    "$$\\boxed{\\vec{r}_{cm} = \\frac{1}{M}\\int \\vec{r}\\,dm "
                    "= \\frac{1}{M}\\int \\vec{r}\\,\\rho\\,dV}$$\n\n"
                    "Choose coordinates exploiting symmetry; $dm = \\lambda\\,dx$ (rod), "
                    "$\\sigma\\,dA$ (sheet), $\\rho\\,dV$ (volume)."
                ),
                (
                    "להתפלגות רציפה עם צפיפות $\\rho$:\n"
                    "$$\\vec{r}_{cm} = \\frac{1}{M}\\int \\vec{r}\\,\\rho\\,dV$$"
                ),
            ),
            _section(
                "cm_derivations",
                "Worked Derivations — Rod and Triangle",
                "גזירות — מוט ומשולש",
                (
                    "**Uniform rod** length $L$ on $x$-axis from $0$ to $L$:\n"
                    "$$x_{cm} = \\frac{1}{M}\\int_0^L x\\,\\lambda\\,dx = "
                    "\\frac{\\lambda}{M}\\frac{L^2}{2} = \\boxed{\\frac{L}{2}}$$\n\n"
                    "**Uniform triangle** (vertex at origin, base $b$ on $x$-axis, height $h$): "
                    "by symmetry $x_{cm}=b/3$ along altitude; $y_{cm}=h/3$ for standard right triangle."
                ),
                (
                    "**מוט אחיד** $L$ על ציר $x$:\n"
                    "$$x_{cm} = L/2$$\n\n"
                    "**משולש אחיד:** $x_{cm}=b/3$ לאורך הגובה."
                ),
            ),
            _section(
                "newton_system",
                "Newton's Second Law for a System",
                "חוק שני של ניוטון למערכת",
                (
                    "Only **external** forces affect CM motion:\n"
                    "$$\\boxed{\\vec{F}_{ext} = M_{tot}\\,\\vec{a}_{cm}}$$\n\n"
                    "Internal forces (Newton III pairs) cancel in the sum over the system.\n\n"
                    "A exploding firework: internal forces change relative motion but $\\vec{a}_{cm}$ "
                    "follows external gravity only (neglect air)."
                ),
                (
                    "רק **כוחות חיצוניים** משפיעים על תנועת CM:\n"
                    "$$\\vec{F}_{ext} = M_{tot}\\,\\vec{a}_{cm}$$\n\n"
                    "כוחות פנימיים מתבטלים בזוגות."
                ),
            ),
            _section(
                "momentum_conservation",
                "Total Momentum and Conservation",
                "תנע כולל ושימור",
                (
                    "$$\\vec{p}_{tot} = M_{tot}\\,\\vec{v}_{cm}$$\n\n"
                    "If $\\vec{F}_{ext}=0$:\n"
                    "$$\\boxed{\\vec{p}_{tot} = \\text{const} \\quad "
                    "\\Rightarrow \\quad \\vec{v}_{cm} = \\text{const}}$$\n\n"
                    "Collisions, explosions: use momentum conservation in isolated system."
                ),
                (
                    "$$\\vec{p}_{tot} = M_{tot}\\,\\vec{v}_{cm}$$\n\n"
                    "אם $\\vec{F}_{ext}=0$: $\\vec{p}_{tot}$ קבוע."
                ),
            ),
            _section(
                "cm_frame",
                "Center-of-Mass Frame",
                "מערכת ייחוס של מרכז מסה",
                (
                    "In the **CM frame**, $\\vec{v}_{cm}' = 0$ and total momentum is zero.\n\n"
                    "Internal kinetic energy is minimized in CM frame. "
                    "Two-body collisions simplify: one particle moves, other recoils oppositely."
                ),
                (
                    "ב**מערכת CM**, $\\vec{v}_{cm}'=0$ והתנע כולל אפס.\n\n"
                    "אנרגיה קינטית פנימית מינימלית במערכת CM."
                ),
            ),
            _section(
                "rocket_equation",
                "Variable Mass — Rocket Equation",
                "מסה משתנה — משוואת הרocket",
                (
                    "Rocket expels exhaust at speed $u$ relative to rocket. With $M(t)$ decreasing:\n"
                    "$$M\\frac{dv}{dt} = -u\\frac{dM}{dt}$$\n\n"
                    "Integrate (constant $u$, no gravity):\n"
                    "$$\\boxed{\\Delta v = u\\ln\\frac{M_0}{M_f}}$$\n\n"
                    "$M_0$ = initial mass, $M_f$ = final mass after burn."
                ),
                (
                    "Rocket משליך exhaust במהירות $u$ יחסית ל-rocket:\n"
                    "$$M\\frac{dv}{dt} = -u\\frac{dM}{dt}$$\n\n"
                    "$$\\Delta v = u\\ln(M_0/M_f)$$"
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "Masses $2$ kg at $(0,0)$ and $4$ kg at $(3,0)$ m. The $x$-coordinate of CM is:",
                "מסות $2$ kg ב-$(0,0)$ ו-$4$ kg ב-$(3,0)$ m. קואורדינטת $x$ של CM:",
                _opts([
                    ("a", "$2.0$ m", "$2.0$ m", True),
                    ("b", "$1.5$ m", "$1.5$ m", False),
                    ("c", "$3.0$ m", "$3.0$ m", False),
                    ("d", "$1.0$ m", "$1.0$ m", False),
                ]),
                "$x_{cm}=(2\\cdot0+4\\cdot3)/6 = 12/6 = 2$ m.",
                "$x_{cm}=(0+12)/6 = 2$ m.",
            ),
            _mcq(
                "q2",
                "Uniform rod length $L$, linear density $\\lambda$. Using $x_{cm}=\\frac{1}{M}\\int x\\,dm$, "
                "one finds:",
                "מוט אחיד $L$, צפיפות לינארית $\\lambda$. מ-$x_{cm}=\\frac{1}{M}\\int x\\,dm$:",
                _opts([
                    ("a", "$x_{cm} = L/2$", "$x_{cm} = L/2$", True),
                    ("b", "$x_{cm} = L/3$", "$x_{cm} = L/3$", False),
                    ("c", "$x_{cm} = L/4$", "$x_{cm} = L/4$", False),
                    ("d", "$x_{cm} = 2L/3$", "$x_{cm} = 2L/3$", False),
                ]),
                "$\\int_0^L x\\lambda\\,dx = \\lambda L^2/2$; $M=\\lambda L$ gives $L/2$.",
                "אינטגרציה נותנת $x_{cm}=L/2$.",
            ),
            _mcq(
                "q3",
                "Two skaters push off each other on frictionless ice. While pushing, $\\vec{F}_{ext}$ on "
                "the system is approximately zero. Therefore:",
                "שני מחליקים דוחפים זה את זה על קרח חלק. בזמן הדחיפה, $\\vec{F}_{ext}\\approx 0$. לכן:",
                _opts([
                    ("a", "CM velocity remains constant during the push", "מהירות CM קבועה", True),
                    ("b", "Each skater's speed is unchanged", "מהירות כל מחליק ללא שינוי", False),
                    ("c", "Total kinetic energy is conserved", "אנרגיה קינטית כוללת נשמרת", False),
                    ("d", "CM accelerates due to internal forces", "CM מאיץ מכוחות פנימיים", False),
                ]),
                "Internal forces cannot change $\\vec{v}_{cm}$ when $\\vec{F}_{ext}=0$.",
                "כוחות פנימיים לא משנים $\\vec{v}_{cm}$ כש-$\\vec{F}_{ext}=0$.",
            ),
            _mcq(
                "q4",
                "In the center-of-mass frame of an isolated two-particle system:",
                "במערכת CM של מערכת שני-חלקיקים מבודדת:",
                _opts([
                    ("a", "Total momentum is zero", "התנע הכולל אפס", True),
                    ("b", "Both particles are at rest at the origin always", "שני החלקיקים תמיד במנוחה", False),
                    ("c", "Internal forces vanish", "כוחות פנימיים מתאפסים", False),
                    ("d", "Kinetic energy is zero", "אנרגיה קינטית אפס", False),
                ]),
                "By definition $\\vec{p}_{tot}'=M\\vec{v}_{cm}'=0$ in CM frame.",
                "בהגדרה $\\vec{p}_{tot}'=0$ במערכת CM.",
            ),
            _mcq(
                "q5",
                "Rocket: $M_0=1000$ kg, $M_f=400$ kg, exhaust speed $u=2000$ m/s (no gravity). "
                "$\\Delta v$ is approximately:",
                "Rocket: $M_0=1000$, $M_f=400$, $u=2000$ m/s. $\\Delta v$ בקירוב:",
                _opts([
                    ("a", "$2000\\ln(2.5) \\approx 1830$ m/s", "$2000\\ln(2.5) \\approx 1830$ m/s", True),
                    ("b", "$1200$ m/s", "$1200$ m/s", False),
                    ("c", "$2000$ m/s", "$2000$ m/s", False),
                    ("d", "$600$ m/s", "$600$ m/s", False),
                ]),
                "$\\Delta v = u\\ln(M_0/M_f) = 2000\\ln(2.5) \\approx 1830$ m/s.",
                "$\\Delta v = 2000\\ln(2.5) \\approx 1830$ m/s.",
            ),
        ],
    },
    {
        "id": "angular_momentum_particles",
        "subject": SUBJECT,
        "title_en": INDEX_ENTRIES["angular_momentum_particles"]["title_en"],
        "title_he": INDEX_ENTRIES["angular_momentum_particles"]["title_he"],
        "duration_min": 26,
        "type": "interactive",
        "level_min": "university",
        "agent_hints": (
            "$\\vec{L}=\\vec{r}\\times\\vec{p}$; $\\vec{\\tau}=d\\vec{L}/dt$. Conservation when "
            "$\\vec{\\tau}_{ext}=0$. Rolling: $v_{cm}=R\\omega$ and $KE=\\frac{1}{2}Mv_{cm}^2+\\frac{1}{2}I\\omega^2$. "
            "Solid sphere rolling beats sliding down incline (more KE in translation for slider? "
            "Actually rolling has rotational KE so slower — compare carefully)."
        ),
        "sections": [
            _section(
                "L_definition",
                "Angular Momentum of a Particle",
                "תנע זוויתי של חלקיק",
                (
                    "For particle of mass $m$ at $\\vec{r}$ with momentum $\\vec{p}=m\\vec{v}$:\n"
                    "$$\\boxed{\\vec{L} = \\vec{r} \\times \\vec{p} = m(\\vec{r}\\times\\vec{v})}$$\n\n"
                    "Magnitude: $L = mrv\\sin\\theta$ ($\\theta$ between $\\vec{r}$ and $\\vec{v}$).\n\n"
                    "Units: kg·m²/s."
                ),
                (
                    "לחלקיק $m$ ב-$\\vec{r}$ עם $\\vec{p}=m\\vec{v}$:\n"
                    "$$\\vec{L} = \\vec{r} \\times \\vec{p} = m(\\vec{r}\\times\\vec{v})$$\n\n"
                    "גודל: $L = mrv\\sin\\theta$."
                ),
            ),
            _section(
                "tau_L_relation",
                "Torque and Angular Momentum",
                "מומנט ותנע זוויתי",
                (
                    "Rotational analog of $\\vec{F}=d\\vec{p}/dt$:\n"
                    "$$\\boxed{\\vec{\\tau}_{ext} = \\frac{d\\vec{L}}{dt}}$$\n\n"
                    "Constant $\\vec{L}$ when net external torque vanishes."
                ),
                (
                    "Analog סיבובי:\n"
                    "$$\\vec{\\tau}_{ext} = \\frac{d\\vec{L}}{dt}$$"
                ),
            ),
            _section(
                "L_conservation",
                "Conservation of Angular Momentum",
                "שימור תנע זוויתי",
                (
                    "If $\\vec{\\tau}_{ext}=0$:\n"
                    "$$\\boxed{\\vec{L} = \\text{const}$$\n\n"
                    "Isolated system: internal torques cancel; total $\\vec{L}$ conserved."
                ),
                (
                    "אם $\\vec{\\tau}_{ext}=0$:\n"
                    "$$\\vec{L} = \\text{const}$$"
                ),
            ),
            _section(
                "L_applications",
                "Applications — Skater, Orbit, Gyroscope",
                "יישומים — מחליק, כוכב לווין, גyroscope",
                (
                    "**Ice skater:** $I\\omega = \\text{const}$. Pulling arms in $\\downarrow I$ "
                    "$\\Rightarrow$ $\\uparrow \\omega$.\n\n"
                    "**Satellite orbit:** central force $\\Rightarrow$ zero torque about planet "
                    "$\\Rightarrow$ areal velocity constant (Kepler's second law).\n\n"
                    "**Gyroscope precession:** gravity torque $\\perp$ to spin $\\Rightarrow$ "
                    "precession of $\\vec{L}$."
                ),
                (
                    "**מחליק קרח:** $I\\omega$ קבוע; $I$ קטן $\\Rightarrow$ $\\omega$ גדל.\n\n"
                    "**מסלול לווין:** מומנט אפס $\\Rightarrow$ שטח קבוע.\n\n"
                    "**גyroscope:** פרcession של $\\vec{L}$."
                ),
            ),
            _section(
                "rigid_body_L",
                "Rigid Body — $L = I\\omega$",
                "גוף קשיח — $L = I\\omega$",
                (
                    "Rotation about symmetry axis through CM:\n"
                    "$$\\boxed{L = I\\omega}$$\n\n"
                    "Combined with $\\tau=I\\alpha$ for fixed axis dynamics."
                ),
                (
                    "סיבוב סביב ציר סימטריה:\n"
                    "$$L = I\\omega$$"
                ),
            ),
            _section(
                "rolling",
                "Rolling Without Slipping",
                "גלגול ללא החלקה",
                (
                    "Rolling without slipping at contact:\n"
                    "$$\\boxed{v_{cm} = R\\omega}$$\n\n"
                    "Total kinetic energy:\n"
                    "$$K = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}I\\omega^2 "
                    "= \\frac{1}{2}Mv_{cm}^2\\left(1 + \\frac{I}{MR^2}\\right)$$"
                ),
                (
                    "גלגול ללא החלקה:\n"
                    "$$v_{cm} = R\\omega$$\n\n"
                    "$$K = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}I\\omega^2$$"
                ),
            ),
            _section(
                "rolling_incline",
                "Worked Example — Ball Rolling Down Incline",
                "דוגמה — כדור גולל במדרון",
                (
                    "**Problem:** Solid sphere ($I=\\frac{2}{5}MR^2$) rolls from rest down height $h$. "
                    "Find $v$ at bottom; compare to sliding block (no rotation).\n\n"
                    "Energy: $Mgh = \\frac{1}{2}Mv^2 + \\frac{1}{2}I\\omega^2 = "
                    "\\frac{1}{2}Mv^2(1 + I/(MR^2))$.\n\n"
                    "Sphere: $I/(MR^2)=2/5$ $\\Rightarrow$ $v = \\sqrt{\\frac{10}{7}gh}$.\n\n"
                    "Slider: $v=\\sqrt{2gh}$ (faster — no rotational KE).\n\n"
                    "Rolling sphere is **slower** than frictionless slider."
                ),
                (
                    "**בעיה:** כדור מלא ($I=\\frac{2}{5}MR^2$) מגולל מגובה $h$.\n\n"
                    "$v = \\sqrt{10gh/7}$; מחליק: $v=\\sqrt{2gh}$ (מהיר יותר)."
                ),
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "Particle $m=2$ kg at $\\vec{r}=(1,0,0)$ m, $\\vec{v}=(0,3,0)$ m/s. "
                "Magnitude of $\\vec{L}$ about origin:",
                "חלקיק $m=2$ kg, $\\vec{r}=(1,0,0)$, $\\vec{v}=(0,3,0)$. גודל $\\vec{L}$:",
                _opts([
                    ("a", "$6$ kg·m²/s", "$6$ kg·m²/s", True),
                    ("b", "$3$ kg·m²/s", "$3$ kg·m²/s", False),
                    ("c", "$0$", "$0$", False),
                    ("d", "$2$ kg·m²/s", "$2$ kg·m²/s", False),
                ]),
                "$\\vec{L}=m\\vec{r}\\times\\vec{v}$; $|L|=mrv=2\\cdot1\\cdot3=6$.",
                "$|L|=mrv=6$.",
            ),
            _mcq(
                "q2",
                "Ice skater spins with $I_i=4.0$ kg·m², $\\omega_i=2.0$ rad/s. She pulls arms to "
                "$I_f=1.0$ kg·m². Final $\\omega_f$:",
                "מחליקה: $I_i=4.0$, $\\omega_i=2.0$; $I_f=1.0$. $\\omega_f$:",
                _opts([
                    ("a", "$8.0$ rad/s", "$8.0$ rad/s", True),
                    ("b", "$0.5$ rad/s", "$0.5$ rad/s", False),
                    ("c", "$2.0$ rad/s", "$2.0$ rad/s", False),
                    ("d", "$4.0$ rad/s", "$4.0$ rad/s", False),
                ]),
                "$I_i\\omega_i = I_f\\omega_f$ $\\Rightarrow$ $\\omega_f = 8.0$ rad/s.",
                "$\\omega_f = I_i\\omega_i/I_f = 8.0$ rad/s.",
            ),
            _mcq(
                "q3",
                "Solid sphere rolls without slipping down height $h$ from rest. "
                "Speed at bottom ($I=\\frac{2}{5}MR^2$):",
                "כדור מלא גולל מגובה $h$ ממנוחה. מהירות בתחתית:",
                _opts([
                    ("a", "$\\sqrt{10gh/7}$", "$\\sqrt{10gh/7}$", True),
                    ("b", "$\\sqrt{2gh}$", "$\\sqrt{2gh}$", False),
                    ("c", "$\\sqrt{gh}$", "$\\sqrt{gh}$", False),
                    ("d", "$\\sqrt{5gh/7}$", "$\\sqrt{5gh/7}$", False),
                ]),
                "Energy with $I/(MR^2)=2/5$ gives $v^2=10gh/7$.",
                "שימור אנרגיה נותן $v=\\sqrt{10gh/7}$.",
            ),
            _mcq(
                "q4",
                "Disk ($I=MR^2/2$) rotates about center with $\\omega$. Angular momentum magnitude:",
                "דיסק ($I=MR^2/2$) מסתובב עם $\\omega$. גודל $L$:",
                _opts([
                    ("a", "$L = \\frac{1}{2}MR^2\\omega$", "$L = \\frac{1}{2}MR^2\\omega$", True),
                    ("b", "$L = MR^2\\omega$", "$L = MR^2\\omega$", False),
                    ("c", "$L = \\frac{1}{2}MR\\omega$", "$L = \\frac{1}{2}MR\\omega$", False),
                    ("d", "$L = M R \\omega$", "$L = M R \\omega$", False),
                ]),
                "$L=I\\omega=MR^2\\omega/2$ for disk about center.",
                "$L=I\\omega=MR^2\\omega/2$.",
            ),
            _mcq(
                "q5",
                "Constant external torque $\\tau$ acts on system with $L_i=0$. After time $t$, "
                "angular momentum is:",
                "מומנט חיצוני קבוע $\\tau$ על מערכת עם $L_i=0$. לאחר זמן $t$, $L$:",
                _opts([
                    ("a", "$L = \\tau t$", "$L = \\tau t$", True),
                    ("b", "$L = \\tau t^2/2$", "$L = \\tau t^2/2$", False),
                    ("c", "$L = 0$", "$L = 0$", False),
                    ("d", "$L = \\tau/ t$", "$L = \\tau/ t$", False),
                ]),
                "$\\tau = dL/dt$ with constant $\\tau$ gives $L=\\tau t$.",
                "$\\tau = dL/dt$ $\\Rightarrow$ $L=\\tau t$.",
            ),
        ],
    },
]


def write_lesson_files(lessons: list[dict]) -> None:
    for lesson in lessons:
        path = LESSONS_DIR / f"{lesson['id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
        print(f"[write] {path.relative_to(ROOT)}")


def update_lessons_index(lessons: list[dict]) -> None:
    with INDEX_PATH.open(encoding="utf-8") as f:
        index = json.load(f)

    lesson_by_id = {l["id"]: l for l in lessons}
    updated = 0
    added = 0

    for entry in index:
        lid = entry.get("id")
        if lid not in INDEX_ENTRIES:
            continue
        meta = INDEX_ENTRIES[lid]
        entry.update(
            {
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": [SUBJECT],
                "subject": SUBJECT,
                "duration_min": meta["duration_min"],
                "type": "interactive",
                "level_min": "university",
            }
        )
        updated += 1

    existing_ids = {e["id"] for e in index}
    for lid, meta in INDEX_ENTRIES.items():
        if lid in existing_ids:
            continue
        index.append(
            {
                "id": lid,
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": [SUBJECT],
                "subject": SUBJECT,
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

    print(f"[index] updated {updated}, added {added}")


def main() -> int:
    assert len(LESSONS) == 5
    for lesson in LESSONS:
        assert lesson["subject"] == SUBJECT
        assert len(lesson["sections"]) >= 4
        assert len(lesson["questions"]) == 5

    write_lesson_files(LESSONS)
    update_lessons_index(LESSONS)
    print("[done] Physics 1 university lessons authored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
