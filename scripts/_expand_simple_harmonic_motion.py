#!/usr/bin/env python3
"""Expand simple_harmonic_motion.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/simple_harmonic_motion.json"

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
            "Simple harmonic motion (SHM) is the archetype of oscillation: a mass on a spring, "
            "a pendulum for small angles, or any system where a restoring force is proportional "
            "to displacement. In this lesson we focus on **energy analysis** — often the fastest "
            "route to speeds and positions without tracking time.\n\n"
            "In SHM the spring alternately stores and releases energy. At maximum displacement "
            "($x = \\pm A$), all energy is elastic potential — kinetic energy is zero. At "
            "equilibrium ($x = 0$), all energy is kinetic. At every instant the sum is constant:\n"
            "$$E = K + U = \\tfrac{1}{2}mv^2 + \\tfrac{1}{2}kx^2 = \\tfrac{1}{2}kA^2.$$\n\n"
            "This energy equation is often **faster** than kinematics when you need speed at a "
            "given position — no $\\omega t$ or phase angle required.\n\n"
            "The **simple pendulum** for small angles ($\\theta < 15°$) undergoes SHM with "
            "restoring torque proportional to $\\theta$. Its period "
            "$T = 2\\pi\\sqrt{L/g}$ is one of the most elegant results in classical physics: "
            "independent of mass and (for small angles) amplitude. University mechanics and "
            "Bagrut physics both reward students who can switch fluently between energy "
            "conservation and the pendulum period formula."
        ),
        "body_he_md": (
            "תנועה הרמונית פשוטה (SHM) היא דגם היסוד של תנודה: מסה על קפיץ, מטוטלת לזוויות קטנות, "
            "או כל מערכת שבה כוח משחזר פרופורציונלי לתזוזה. בשיעור זה מתמקדים ב**ניתוח אנרגיה** — "
            "לעיתים קרובות הדרך המהירה ביותר למהירויות ומיקומים בלי לעקוב אחרי זמן.\n\n"
            "ב-SHM הקפיץ מאחסן ומשחרר אנרגיה לסירוגין. ב-$x=\\pm A$ — כל האנרגיה פוטנציאלית "
            "אלסטית ($K=0$). ב-$x=0$ — כל האנרגיה קינטית ($U=0$). בכל רגע הסכום קבוע:\n"
            "$$E=K+U=\\tfrac{1}{2}mv^2+\\tfrac{1}{2}kx^2=\\tfrac{1}{2}kA^2.$$\n\n"
            "משוואת האנרגיה **מהירה** לעיתים מקינמטיקה כשצריך מהירות במיקום נתון — "
            "ללא $\\omega t$ או זווית פאזה.\n\n"
            "**מטוטלת פשוטה** לזוויות קטנות ($\\theta<15°$): כוח משחזר פרופורציונלי ל-$\\theta$. "
            "מחזור $T=2\\pi\\sqrt{L/g}$ — אחת התוצאות האלגנטיות ביותר בפיזיקה קלאסית: "
            "לא תלוי במסה ובמשרעת (לזוויות קטנות). בגרות ומכניקה באוניברסיטה מעריכים מי שעובר "
            "בחופשיות בין שימור אנרגיה לנוסחת מחזור המטוטלת."
        ),
    },
    "definition": {
        "body_en_md": (
            "### SHM total energy\n"
            "$$E = K + U = \\frac{1}{2}mv^2 + \\frac{1}{2}kx^2 = \\frac{1}{2}kA^2 = \\text{const}.$$\n"
            "The amplitude $A$ fixes the total energy once $k$ is known. Never forget the factor "
            "$\\tfrac{1}{2}$ — writing $E = kA^2$ is the most common arithmetic error on exams.\n\n"
            "### Speed at position $x$\n"
            "$$v(x) = \\omega\\sqrt{A^2 - x^2}, \\quad \\text{where } \\omega = \\sqrt{k/m}.$$\n"
            "**Extremes:** $|v|_{max} = \\omega A$ at $x=0$; $v=0$ at $x=\\pm A$. "
            "All energy is kinetic at equilibrium; all potential at the turning points.\n\n"
            "### Energy fraction at arbitrary $x$\n"
            "$$\\frac{K}{E} = 1 - \\frac{x^2}{A^2}, \\qquad \\frac{U}{E} = \\frac{x^2}{A^2}.$$\n"
            "At $x = A/\\sqrt{2}$, kinetic and potential each equal half the total energy.\n\n"
            "### Simple pendulum (small angle)\n"
            "For small $\\theta$ (radians): $\\sin\\theta \\approx \\theta$. The equation of motion is:\n"
            "$$\\ddot{\\theta} + \\frac{g}{L}\\theta = 0 \\implies \\omega_{pendulum} = \\sqrt{\\frac{g}{L}}.$$\n"
            "$$T = 2\\pi\\sqrt{\\frac{L}{g}}.$$\n"
            "Note: $T$ is **independent of mass $m$** and **independent of amplitude $A$** "
            "(for small angles). On the Moon, smaller $g$ means longer period. "
            "Frequency $f = 1/T$ and angular frequency $\\omega = 2\\pi f$ complete the "
            "pendulum parameter set alongside the spring relation $\\omega = \\sqrt{k/m}$."
        ),
        "body_he_md": (
            "### אנרגיה כוללת ב-SHM\n"
            "$$E=\\tfrac{1}{2}mv^2+\\tfrac{1}{2}kx^2=\\tfrac{1}{2}kA^2=\\text{קבוע}.$$\n"
            "המשרעת $A$ קובעת את האנרגיה הכוללת ברגע ש-$k$ ידוע. לעולם אל תשכחו את $\\tfrac{1}{2}$ — "
            "כתיבת $E=kA^2$ היא הטעות החשבונית הנפוצה ביותר בבחינות.\n\n"
            "### מהירות במיקום $x$\n"
            "$$v(x)=\\omega\\sqrt{A^2-x^2}, \\quad \\omega=\\sqrt{k/m}.$$\n"
            "**קיצוניות:** $|v|_{\\max}=\\omega A$ ב-$x=0$; $v=0$ ב-$x=\\pm A$. "
            "כל האנרגיה קינטית בשיווי משקל; כולה פוטנציאלית בנקודות ההיפוך.\n\n"
            "### שברי אנרגיה\n"
            "$$K/E=1-x^2/A^2, \\quad U/E=x^2/A^2.$$\n"
            "ב-$x=A/\\sqrt{2}$ האנרגיה הקינטית והפוטנציאלית שוות — כל אחת חצי מהכוללת.\n\n"
            "### מטוטלת פשוטה (זוויות קטנות)\n"
            "ל-$\\theta$ קטן (רדיאנים): $\\sin\\theta\\approx\\theta$. משוואת התנועה:\n"
            "$$\\ddot{\\theta}+\\frac{g}{L}\\theta=0\\implies\\omega=\\sqrt{g/L}.$$\n"
            "$$T=2\\pi\\sqrt{L/g}.$$\n"
            "$T$ **לא תלוי** במסה $m$ ובמשרעת (לזוויות קטנות). על הירח, $g$ קטן יותר → מחזור ארוך יותר. "
            "תדירות $f=1/T$ ותדירות זוויתית $\\omega=2\\pi f$ משלימות את קבוצת הפרמטרים "
            "לצד $\\omega=\\sqrt{k/m}$ בקפיץ — שני סוגי מתנדדים, אותה מתמטיקה."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Setup\n"
            "A simple pendulum: mass $m$, string length $L$, angle $\\theta$ from vertical.\n\n"
            "### Forces\n"
            "- Tension $T$ along the string (provides centripetal force in the radial direction).\n"
            "- Gravity component along string: $mg\\cos\\theta$ (balanced by tension radially).\n"
            "- Gravity component perpendicular to string (tangential, restoring): "
            "$-mg\\sin\\theta$ — points back toward equilibrium.\n\n"
            "### Equation of motion (tangential direction)\n"
            "Arc length $s = L\\theta$. Newton's 2nd law along the arc:\n"
            "$$m\\ddot{s} = mL\\ddot{\\theta} = -mg\\sin\\theta.$$\n"
            "$$\\ddot{\\theta} = -\\frac{g}{L}\\sin\\theta.$$\n"
            "This is **nonlinear** for large $\\theta$ — no simple closed-form period.\n\n"
            "### Small-angle approximation\n"
            "For $|\\theta| \\ll 1$ rad (approximately $\\theta < 15°$): $\\sin\\theta \\approx \\theta$:\n"
            "$$\\ddot{\\theta} = -\\frac{g}{L}\\theta \\implies \\ddot{\\theta} + \\omega^2\\theta = 0, "
            "\\quad \\omega = \\sqrt{\\frac{g}{L}}.$$\n"
            "This is the SHM equation with $X = \\theta$. Therefore "
            "$T = 2\\pi/\\omega = 2\\pi\\sqrt{L/g}$.\n\n"
            "### Why $T$ is independent of $m$\n"
            "In $mL\\ddot{\\theta} = -mg\\sin\\theta$, mass $m$ appears on both sides and cancels. "
            "Hence $T$ depends only on $L$ and $g$. The same cancellation explains why a heavy "
            "and light bob on equal-length strings swing with the same period in the lab. "
            "For exam problems, always state the small-angle assumption before applying "
            "$T = 2\\pi\\sqrt{L/g}$."
        ),
        "body_he_md": (
            "### הגדרה\n"
            "מטוטלת פשוטה: מסה $m$, חוט אורך $L$, זווית $\\theta$ מהאנכי.\n\n"
            "### כוחות\n"
            "- מתח $T$ לאורך החוט (כוח צנטריפטלי בכיוון רדיאלי).\n"
            "- רכיב כבידה לאורך החוט: $mg\\cos\\theta$ (מאוזן על ידי המתח).\n"
            "- רכיב כבידה ניצב לחוט (משיקי, משחזר): $-mg\\sin\\theta$ — חוזר לשיווי משקל.\n\n"
            "### משוואת תנועה (כיוון משיקי)\n"
            "אורך קשת $s=L\\theta$. חוק ניוטון השני לאורך הקשת:\n"
            "$$mL\\ddot{\\theta}=-mg\\sin\\theta\\implies\\ddot{\\theta}=-\\frac{g}{L}\\sin\\theta.$$\n"
            "זו משוואה **לא-לינארית** לזוויות גדולות — אין נוסחת מחזור סגורה פשוטה.\n\n"
            "### קירוב זווית קטנה\n"
            "ל-$|\\theta|\\ll1$ רד (בערך $\\theta<15°$): $\\sin\\theta\\approx\\theta$:\n"
            "$$\\ddot{\\theta}+\\frac{g}{L}\\theta=0, \\quad \\omega=\\sqrt{g/L}.$$\n"
            "זו משוואת SHM עם $X=\\theta$. לכן $T=2\\pi/\\omega=2\\pi\\sqrt{L/g}$.\n\n"
            "### למה $T$ לא תלוי ב-$m$\n"
            "ב-$mL\\ddot{\\theta}=-mg\\sin\\theta$, המסה $m$ מופיעה בשני הצדדים ומתבטלת. "
            "לכן $T$ תלוי רק ב-$L$ ו-$g$. אותה ביטול מסבירה למה כדור כבד וקל על חוטים "
            "באותו אורך מתנדנדים באותו מחזור בניסוי. "
            "בבעיות בחינה, ציינו תמיד הנחת זווית קטנה לפני $T=2\\pi\\sqrt{L/g}$."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A spring ($k = 200$ N/m) with mass $m = 0.5$ kg oscillates with amplitude "
            "$A = 0.1$ m. Find the maximum speed using energy conservation.\n\n"
            "This is the canonical energy problem: total energy is fixed by amplitude, and all of "
            "it becomes kinetic at $x = 0$ where potential energy vanishes.\n\n"
            "### Move 1: Total energy at turning point\n"
            "At $x = A$: all energy is potential, $v = 0$:\n"
            "$$E = \\tfrac{1}{2}kA^2 = \\tfrac{1}{2}(200)(0.01) = 1 \\text{ J}.$$\n\n"
            "### Move 2: Maximum speed at equilibrium\n"
            "At $x = 0$, $U = 0$, so $E = \\tfrac{1}{2}mv_{max}^2$:\n"
            "$$v_{max} = \\sqrt{\\frac{2E}{m}} = \\sqrt{\\frac{2\\times1}{0.5}} = \\sqrt{4} = 2 \\text{ m/s}.$$\n\n"
            "### Move 3: Verify with kinematic formula\n"
            "$$v_{max} = A\\omega = A\\sqrt{k/m} = 0.1\\sqrt{200/0.5} = 0.1\\times20 = 2 \\text{ m/s}. \\checkmark$$\n\n"
            "**Answer:** $v_{max} = 2$ m/s. Both methods agree — energy conservation is often "
            "faster because you never need to find $\\omega$ explicitly unless verifying.\n\n"
            "**Sanity check:** At $x=A$, speed is zero and $U=E$. At $x=0$, $K=E$. "
            "The value 2 m/s is reasonable for a stiff spring ($k=200$ N/m) with modest amplitude. "
            "You could also verify with energy: $\\tfrac{1}{2}mv^2 = 1$ J at $x=0$.\n\n"
            "**Key takeaway:** Whenever amplitude and spring constant are given, "
            "$E = \\tfrac{1}{2}kA^2$ is the fastest path to any speed question."
        ),
        "body_he_md": (
            "**נתון:** קפיץ ($k=200$ נ\"מ), מסה $m=0.5$ ק\"ג, משרעת $A=0.1$ מ'. "
            "מצאו מהירות מקסימלית בשימור אנרגיה.\n\n"
            "זו בעיית אנרגיה קלאסית: האנרגיה הכוללת נקבעת על ידי המשרעת, "
            "וכולה הופכת לקינטית ב-$x=0$ שם האנרגיה הפוטנציאלית מתאפסת.\n\n"
            "### צעד 1: אנרגיה כוללת בנקודת היפוך\n"
            "ב-$x=A$: כל האנרגיה פוטנציאלית, $v=0$:\n"
            "$$E=\\tfrac{1}{2}kA^2=\\tfrac{1}{2}(200)(0.01)=1\\text{ ג'ול}.$$\n\n"
            "### צעד 2: מהירות מקסימלית בשיווי משקל\n"
            "ב-$x=0$, $U=0$, לכן $E=\\tfrac{1}{2}mv_{\\max}^2$:\n"
            "$$v_{\\max}=\\sqrt{\\frac{2E}{m}}=\\sqrt{\\frac{2}{0.5}}=2\\text{ מ/ש}.$$\n\n"
            "### צעד 3: אימות בנוסחה קינמטית\n"
            "$$v_{\\max}=A\\omega=0.1\\sqrt{200/0.5}=0.1\\times20=2\\text{ מ/ש}. \\checkmark$$\n\n"
            "**תשובה:** $v_{\\max}=2$ מ/ש. שתי השיטות מסכימות — שימור אנרגיה לעיתים מהיר "
            "כי אין צורך למצוא $\\omega$ במפורש אלא לאימות.\n\n"
            "**בדיקת הגיון:** ב-$x=A$ המהירות אפס ו-$U=E$. ב-$x=0$, $K=E$. "
            "2 מ/ש סביר לקפיץ קשיח ($k=200$ נ\"מ) עם משרעת מתונה. "
            "אימות אנרגיה: $\\tfrac{1}{2}mv^2=1$ ג'ול ב-$x=0$.\n\n"
            "**מסקנה:** כשניתנים משרעת וקבוע קפיץ, "
            "$E=\\tfrac{1}{2}kA^2$ הוא הנתיב המהיר ביותר לכל שאלת מהירות."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A spring-mass oscillator with amplitude $A$. At $x = A/2$, find:\n"
            "(a) The fraction of total energy that is kinetic.\n"
            "(b) The fraction that is potential.\n"
            "(c) The speed in terms of $v_{max}$.\n\n"
            "Energy fractions follow directly from $U = \\tfrac{1}{2}kx^2$ — no time or phase needed.\n\n"
            "### Move 1: Potential energy at $x = A/2$\n"
            "$$U = \\tfrac{1}{2}k\\left(\\frac{A}{2}\\right)^2 = \\tfrac{1}{2}k\\frac{A^2}{4} = \\frac{E}{4}.$$\n\n"
            "### Move 2: Kinetic energy by subtraction\n"
            "$$K = E - U = E - \\frac{E}{4} = \\frac{3E}{4}.$$\n\n"
            "### Move 3: Energy fractions\n"
            "$$\\frac{K}{E} = \\frac{3}{4} = 75\\%, \\qquad \\frac{U}{E} = \\frac{1}{4} = 25\\%.$$\n\n"
            "### Move 4: Speed from kinetic energy\n"
            "$$\\frac{1}{2}mv^2 = \\frac{3}{4}\\cdot\\frac{1}{2}kA^2 = \\frac{3}{4}\\cdot\\frac{1}{2}mv_{max}^2.$$\n"
            "$$v = v_{max}\\sqrt{\\frac{3}{4}} = \\frac{\\sqrt{3}}{2}v_{max} \\approx 0.866\\, v_{max}.$$\n\n"
            "### Move 5: Quick check with position formula\n"
            "$$v = \\omega\\sqrt{A^2 - (A/2)^2} = \\omega\\sqrt{3A^2/4} = \\frac{\\sqrt{3}}{2}A\\omega "
            "= \\frac{\\sqrt{3}}{2}v_{max}. \\checkmark$$\n\n"
            "**Answer:** 75% kinetic, 25% potential; $v = (\\sqrt{3}/2)v_{max}$. "
            "Notice $K/E = 1 - x^2/A^2 = 1 - 1/4 = 3/4$ — the general formula checks instantly.\n\n"
            "**Exam pattern:** Bagrut often asks for energy fractions at $x = A/2$, $A/3$, or "
            "$x = A/\\sqrt{2}$. Memorise $K/E = 1 - x^2/A^2$ to answer in one line without "
            "computing $E$ numerically. At $x = A/2$, the oscillator still has most of its "
            "energy as kinetic — it has not yet reached the turning point."
        ),
        "body_he_md": (
            "**נתון:** מנדנד קפיץ-מסה עם משרעת $A$. ב-$x=A/2$ מצאו:\n"
            "(א) שבר האנרגיה הקינטית; (ב) שבר הפוטנציאלית; (ג) מהירות לפי $v_{\\max}$.\n\n"
            "שברי אנרגיה נובעים ישירות מ-$U=\\tfrac{1}{2}kx^2$ — ללא זמן או פאזה.\n\n"
            "### צעד 1: אנרגיה פוטנציאלית ב-$x=A/2$\n"
            "$$U=\\tfrac{1}{2}k(A/2)^2=\\tfrac{1}{2}k\\frac{A^2}{4}=\\frac{E}{4}.$$\n\n"
            "### צעד 2: אנרגיה קינטית בחיסור\n"
            "$$K=E-U=E-\\frac{E}{4}=\\frac{3E}{4}.$$\n\n"
            "### צעד 3: שברי אנרגיה\n"
            "$$K/E=\\frac{3}{4}=75\\%; \\quad U/E=\\frac{1}{4}=25\\%.$$\n\n"
            "### צעד 4: מהירות מאנרגיה קינטית\n"
            "$$\\frac{1}{2}mv^2=\\frac{3}{4}\\cdot\\frac{1}{2}mv_{\\max}^2 "
            "\\Rightarrow v=\\frac{\\sqrt{3}}{2}v_{\\max}\\approx0.866\\,v_{\\max}.$$\n\n"
            "### צעד 5: בדיקה מהירה בנוסחת מיקום\n"
            "$$v=\\omega\\sqrt{A^2-(A/2)^2}=\\omega\\sqrt{3A^2/4}=\\frac{\\sqrt{3}}{2}v_{\\max}. \\checkmark$$\n\n"
            "**תשובה:** 75% קינטית, 25% פוטנציאלית; $v=\\frac{\\sqrt{3}}{2}v_{\\max}$. "
            "שימו לב $K/E=1-x^2/A^2=1-1/4=3/4$ — הנוסחה הכללית מאמתת מיד.\n\n"
            "**תבנית בחינה:** בבגרות שואלים לעיתים על שברי אנרגיה ב-$x=A/2$, $A/3$ "
            "או $x=A/\\sqrt{2}$. שיננו $K/E=1-x^2/A^2$ לתשובה בשורה אחת "
            "בלי חישוב $E$ מספרי. ב-$x=A/2$ עדיין רוב האנרגיה קינטית — "
            "עדיין לא הגענו לנקודת היפוך."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Objective:** Derive the equation of motion for a simple pendulum (mass $m$, length $L$) "
            "and show it reduces to SHM for small angles, yielding $T = 2\\pi\\sqrt{L/g}$.\n\n"
            "### Move 1: Geometry and forces\n"
            "Displace the pendulum by angle $\\theta$ from vertical. Forces on the mass:\n"
            "- Tension $T$ along the string (radial).\n"
            "- Gravity $mg$ downward; tangential restoring component: $-mg\\sin\\theta$.\n\n"
            "### Move 2: Newton's 2nd law tangentially\n"
            "Arc displacement $s = L\\theta$, tangential acceleration $\\ddot{s} = L\\ddot{\\theta}$:\n"
            "$$m L\\ddot{\\theta} = -mg\\sin\\theta \\implies \\ddot{\\theta} = -\\frac{g}{L}\\sin\\theta. \\quad (*)$$\n"
            "Nonlinear — for large angles, $T$ is not $2\\pi\\sqrt{L/g}$.\n\n"
            "### Move 3: Small-angle linearisation\n"
            "Taylor: $\\sin\\theta \\approx \\theta$ for $|\\theta| \\ll 1$ rad. Substitute into $(*)$:\n"
            "$$\\ddot{\\theta} = -\\frac{g}{L}\\theta.$$\n"
            "This is SHM with $\\omega = \\sqrt{g/L}$.\n\n"
            "### Move 4: Period and mass cancellation\n"
            "$$T = \\frac{2\\pi}{\\omega} = 2\\pi\\sqrt{\\frac{L}{g}}.$$\n"
            "In $mL\\ddot{\\theta} = -mg\\sin\\theta$, mass cancels → $T$ independent of $m$. "
            "This is the 'aha' moment: heavier bob, same swing time (for small angles).\n\n"
            "**Exam pattern:** Bagrut often asks you to derive $T$ from Newton's second law "
            "or to explain why mass does not appear. Always state the small-angle assumption "
            "before applying $T = 2\\pi\\sqrt{L/g}$ — examiners deduct marks for skipping it."
        ),
        "body_he_md": (
            "**מטרה:** גזרו משוואת תנועה למטוטלת פשוטה ($m$, $L$) והראו שהיא מובילה ל-SHM "
            "עם $T=2\\pi\\sqrt{L/g}$.\n\n"
            "### צעד 1: גיאומטריה וכוחות\n"
            "תזוזה $\\theta$ מהאנכי. כוחות על המסה:\n"
            "- מתח $T$ לאורך החוט (רדיאלי).\n"
            "- כבידה $mg$ מטה; רכיב משחזר משיקי: $-mg\\sin\\theta$.\n\n"
            "### צעד 2: חוק ניוטון השני בכיוון משיקי\n"
            "תזוזת קשת $s=L\\theta$, תאוצה משיקית $\\ddot{s}=L\\ddot{\\theta}$:\n"
            "$$mL\\ddot{\\theta}=-mg\\sin\\theta\\implies\\ddot{\\theta}=-\\frac{g}{L}\\sin\\theta. \\quad (*)$$\n"
            "לא-לינארית — לזוויות גדולות, $T$ אינו $2\\pi\\sqrt{L/g}$.\n\n"
            "### צעד 3: ליניאריזציה לזווית קטנה\n"
            "קירוב טיילור: $\\sin\\theta\\approx\\theta$ ל-$|\\theta|\\ll1$ רד. הציבו ב-$(*)$:\n"
            "$$\\ddot{\\theta}=-\\frac{g}{L}\\theta.$$\n"
            "זו SHM עם $\\omega=\\sqrt{g/L}$.\n\n"
            "### צעד 4: מחזור וביטול מסה\n"
            "$$T=\\frac{2\\pi}{\\omega}=2\\pi\\sqrt{\\frac{L}{g}}.$$\n"
            "ב-$mL\\ddot{\\theta}=-mg\\sin\\theta$, המסה מתבטלת → $T$ לא תלוי ב-$m$. "
            "רגע ה\"אהה\": כדור כבד יותר — אותו זמן נדנוד (לזוויות קטנות).\n\n"
            "**תבנית בחינה:** בבגרות מבקשים לעיתים לגזור $T$ מחוק ניוטון השני "
            "או להסביר למה המסה לא מופיעה. ציינו תמיד הנחת זווית קטנה לפני "
            "$T=2\\pi\\sqrt{L/g}$ — מורידים נקודות על דילוג."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "**Step 1 — Angular frequency:**\n"
            "$$\\omega=\\sqrt{k/m}=\\sqrt{80/0.2}=\\sqrt{400}=20\\text{ rad/s}.$$\n\n"
            "**Step 2 — Total energy (optional check):**\n"
            "$$E=\\tfrac{1}{2}kA^2=\\tfrac{1}{2}(80)(0.0225)=0.9\\text{ J}.$$\n\n"
            "**Step 3 — Speed at $x=0.1$ m via energy or formula:**\n"
            "Using $v=\\omega\\sqrt{A^2-x^2}$:\n"
            "$$v=20\\sqrt{0.0225-0.01}=20\\sqrt{0.0125}=20\\times0.1118=2.236\\text{ m/s}.$$\n\n"
            "**Energy check:** $U=\\tfrac{1}{2}k(0.1)^2=0.4$ J, $K=E-U=0.5$ J, "
            "$v=\\sqrt{2K/m}=\\sqrt{1/0.2}=2.236$ m/s ✓.\n\n"
            "**Answer:** $v \\approx 2.24$ m/s."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — תדירות זוויתית:**\n"
            "$$\\omega=\\sqrt{80/0.2}=20\\text{ ראד/ש}.$$\n\n"
            "**שלב 2 — אנרגיה כוללת (בדיקה):**\n"
            "$$E=\\tfrac{1}{2}(80)(0.0225)=0.9\\text{ ג'ול}.$$\n\n"
            "**שלב 3 — מהירות ב-$x=0.1$ מ':**\n"
            "$$v=20\\sqrt{0.0225-0.01}=20\\sqrt{0.0125}\\approx2.24\\text{ מ/ש}.$$\n\n"
            "**בדיקת אנרגיה:** $U=0.4$ ג'ול, $K=0.5$ ג'ול, "
            "$v=\\sqrt{2K/m}=2.24$ מ/ש ✓.\n\n"
            "**תשובה:** $v\\approx2.24$ מ/ש."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "**Step 1 — Set equal kinetic and potential:**\n"
            "$K = U$ means each equals half the total: $U = E/2$.\n\n"
            "**Step 2 — Solve for $x$:**\n"
            "$$\\frac{1}{2}kx^2 = \\frac{1}{2}\\cdot\\frac{1}{2}kA^2 "
            "\\Rightarrow x^2 = \\frac{A^2}{2} "
            "\\Rightarrow x = \\pm\\frac{A}{\\sqrt{2}} \\approx \\pm 0.707\\,A.$$\n\n"
            "**Alternative:** Use $K/E = 1 - x^2/A^2 = 1/2$, so $x^2/A^2 = 1/2$.\n\n"
            "**Physical picture:** At this displacement, half the energy is still stored in the "
            "spring and half drives motion — the oscillator is neither at rest nor at maximum speed.\n\n"
            "**Answer:** $x = \\pm A/\\sqrt{2}$."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — השוואת קינטית לפוטנציאלית:**\n"
            "$K=U$ פירושו שכל אחת שווה לחצי מהכולל: $U=E/2$.\n\n"
            "**שלב 2 — פתרון ל-$x$:**\n"
            "$$\\frac{1}{2}kx^2=\\frac{1}{2}\\cdot\\frac{1}{2}kA^2 "
            "\\Rightarrow x^2=\\frac{A^2}{2} "
            "\\Rightarrow x=\\pm\\frac{A}{\\sqrt{2}}\\approx\\pm0.707\\,A.$$\n\n"
            "**דרך חלופית:** $K/E=1-x^2/A^2=1/2$, לכן $x^2/A^2=1/2$.\n\n"
            "**תמונה פיזיקלית:** בתזוזה זו, חצי האנרגיה עדיין בקפיץ וחצי מניע תנועה — "
            "לא במנוחה ולא במהירות מקסימלית.\n\n"
            "**תשובה:** $x=\\pm A/\\sqrt{2}$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "Use this decision table on every SHM energy problem — it replaces hunting for the "
            "right trig identity or phase angle.\n\n"
            "| Situation | Key equation | Notes |\n"
            "|---|---|---|\n"
            "| Max speed | $v_{max} = A\\omega = A\\sqrt{k/m}$ | At $x=0$ |\n"
            "| Speed at $x$ | $v = \\omega\\sqrt{A^2-x^2}$ | From energy conservation |\n"
            "| Fraction KE at $x$ | $K/E = 1 - x^2/A^2$ | |\n"
            "| Where $K = U$ | $x = \\pm A/\\sqrt{2}$ | Each energy = $E/2$ |\n"
            "| Pendulum period | $T = 2\\pi\\sqrt{L/g}$ | Small angles only |\n"
            "| Total energy | $E = \\frac{1}{2}kA^2$ | Constant throughout motion |\n"
            "| New amplitude (IC) | $A' = \\sqrt{x_0^2 + (v_0/\\omega)^2}$ | From initial conditions |\n\n"
            "**Energy-method protocol:**\n"
            "1. Find total energy: $E = \\frac{1}{2}kA^2$ (or from ICs).\n"
            "2. Write $E = K + U$ at the point of interest.\n"
            "3. Solve for the unknown (usually $v$ or $x$).\n"
            "4. No time is needed — energy gives speed directly at any position."
        ),
        "body_he_md": (
            "השתמשו בטבלת ההחלטה בכל בעיית אנרגיה של SHM — היא מחליפה חיפוש אחר זהות "
            "טריגונומטרית או זווית פאזה.\n\n"
            "| מצב | משוואה מרכזית | הערות |\n"
            "|---|---|---|\n"
            "| $v_{\\max}$ | $A\\omega$ (ב-$x=0$) | |\n"
            "| $v$ ב-$x$ | $\\omega\\sqrt{A^2-x^2}$ | משימור אנרגיה |\n"
            "| $K/E$ ב-$x$ | $1-x^2/A^2$ | |\n"
            "| $K=U$ | $x=\\pm A/\\sqrt{2}$ | כל אנרגיה $=E/2$ |\n"
            "| מחזור מטוטלת | $2\\pi\\sqrt{L/g}$ | זוויות קטנות בלבד |\n"
            "| אנרגיה כוללת | $\\tfrac{1}{2}kA^2$ | קבועה |\n"
            "| משרעת חדשה (ת\"א) | $\\sqrt{x_0^2+(v_0/\\omega)^2}$ | מתנאי התחלה |\n\n"
            "**פרוטוקול אנרגיה:**\n"
            "1. $E=\\tfrac{1}{2}kA^2$ (או מתנאי התחלה).\n"
            "2. $E=K+U$ בנקודת העניין.\n"
            "3. פתרו לנעלם (בדרך כלל $v$ או $x$).\n"
            "4. אין צורך בזמן — אנרגיה נותנת מהירות ישירות בכל מיקום."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below. **Try each one before opening the solution** — "
            "the steps matter as much as the final answer. For energy problems, always write "
            "$E = \\tfrac{1}{2}kA^2$ first; for pendulum problems, check whether small-angle "
            "approximation applies before using $T = 2\\pi\\sqrt{L/g}$."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "הצעדים חשובים לא פחות מהתשובה הסופית. בבעיות אנרגיה, כתבו תמיד "
            "$E=\\tfrac{1}{2}kA^2$ קודם; בבעיות מטוטלת, בדקו אם קירוב זווית קטנה "
            "חל לפני שימוש ב-$T=2\\pi\\sqrt{L/g}$."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting that $E = \\frac{1}{2}kA^2$, not $kA^2$.** The factor of $\\tfrac{1}{2}$ "
            "is essential — the most frequent arithmetic error in SHM energy problems.\n\n"
            "2. **Pendulum period on different planets.** $T = 2\\pi\\sqrt{L/g}$. On the Moon, "
            "$g$ is smaller → $T$ is larger (slower pendulum). Substituting Earth's $g$ on the "
            "Moon loses exam points immediately.\n\n"
            "3. **Pendulum period and amplitude.** For small angles, $T$ is independent of amplitude. "
            "Only for large angles ($>15°$) does amplitude affect $T$ — do not extrapolate "
            "small-angle results to large swings.\n\n"
            "4. **Confusing $v = \\omega\\sqrt{A^2 - x^2}$ and $v = -A\\omega\\sin(\\omega t)$.** "
            "The first gives speed as a function of **position** (energy method). "
            "The second gives velocity as a function of **time** (kinematic). Both are correct "
            "but answer different questions.\n\n"
            "5. **Assuming maximum speed at maximum displacement.** $v_{max}$ is at $x = 0$ "
            "(equilibrium), not at $x = \\pm A$ where speed is zero."
        ),
        "body_he_md": (
            "1. **$E=\\frac{1}{2}kA^2$, לא $kA^2$.** גורם $\\tfrac{1}{2}$ חיוני — "
            "הטעות החשבונית הנפוצה ביותר בבעיות אנרגיה של SHM.\n\n"
            "2. **מחזור מטוטלת בכוכב אחר.** $T=2\\pi\\sqrt{L/g}$. על הירח, $g$ קטן יותר → "
            "$T$ ארוך יותר. הצבת $g$ של כדור הארץ על הירח = אובדן נקודות מיידי.\n\n"
            "3. **מחזור מטוטלת ומשרעת.** לזוויות קטנות — $T$ לא תלוי ב-$A$. "
            "רק לזוויות גדולות ($>15°$) המשרעת משפיעה — אל תרחיבו קירוב קטן לנדנוד גדול.\n\n"
            "4. **$v=\\omega\\sqrt{A^2-x^2}$ לעומת $v=-A\\omega\\sin(\\omega t)$.** "
            "ראשון — מהירות כפונקציה של **מיקום** (שיטת אנרגיה). "
            "שני — מהירות כפונקציה של **זמן** (קינמטי). שניהם נכונים אך עונים על שאלות שונות.\n\n"
            "5. **מהירות מקסימלית בקצה?** $v_{\\max}$ ב-$x=0$ (שיווי משקל), לא ב-$x=\\pm A$ "
            "שם המהירות אפס."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "SHM energy analysis is the bridge between mechanics and waves — the same "
            "$\\sin/\\cos$ oscillation appears everywhere in physics.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:waves_basics` **Mechanical Waves** — sinusoidal displacement generalises SHM.\n"
            "- `concept:ac_circuits` **AC Circuits** — LC oscillators obey the same energy exchange.\n\n"
            "**Builds on:**\n"
            "- `concept:trigonometry_identities` **Trigonometric Identities**\n"
            "- `concept:work_energy` **Work and Energy**\n\n"
            "**Why it matters for exams:** Bagrut and university courses reward *transfer* — "
            "finding speed at a position without time, or deriving the pendulum period from "
            "Newton's second law. When you study, draw the energy bar chart at $x=0$, $x=A/2$, "
            "and $x=A$ until the picture is automatic."
        ),
        "body_he_md": (
            "ניתוח אנרגיה של SHM הוא הגשר בין מכניקה לגלים — "
            "אותה תנודה $\\sin/\\cos$ מופיעה בכל מקום בפיזיקה.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:waves_basics` **גלים מכניים** — תזוזה סינוסואידלית מכלילה SHM.\n"
            "- `concept:ac_circuits` **מעגלי זרם חילופין** — מתנדדי LC עוברים אותו חילופי אנרגיה.\n\n"
            "**מבוסס על:**\n"
            "- `concept:trigonometry_identities` **זהויות טריגונומטריות**\n"
            "- `concept:work_energy` **עבודה ואנרגיה**\n\n"
            "**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים *העברה* — "
            "מציאת מהירות במיקום בלי זמן, או גזירת מחזור מטוטלת מחוק ניוטון השני. "
            "בזמן לימוד, שרטטו תרשים אנרגיה ב-$x=0$, $x=A/2$ ו-$x=A$ "
            "עד שהתמונה אוטומטית."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "### Essential Formulas\n"
            "- **Total energy:** $E = \\frac{1}{2}kA^2 = \\frac{1}{2}mv_{max}^2$\n"
            "- **Energy conservation:** $\\frac{1}{2}mv^2 + \\frac{1}{2}kx^2 = \\frac{1}{2}kA^2$\n"
            "- **Speed at x:** $v = \\omega\\sqrt{A^2 - x^2}$\n"
            "- **Pendulum:** $T = 2\\pi\\sqrt{L/g}$ (small angles only)\n"
            "- **Equal K and U:** $x = \\pm A/\\sqrt{2}$\n"
            "- **Amplitude from IC:** $A = \\sqrt{x_0^2 + (v_0/\\omega)^2}$\n\n"
            "### Typical Exam Questions\n"
            "1. Find max speed or energy from $k$, $m$, $A$.\n"
            "2. Find speed at a given position $x$.\n"
            "3. What fraction of energy is kinetic at $x = A/2$ (or $A/3$)?\n"
            "4. Find pendulum period on different planets.\n"
            "5. Given ICs, find amplitude. Always state whether small-angle approximation applies.\n\n"
            "**Time-saver:** Draw an energy bar chart at $x=0$, $x=A/2$, and $x=A$ before "
            "choosing algebra — it prevents sign and fraction errors under exam pressure."
        ),
        "body_he_md": (
            "### נוסחאות חיוניות\n"
            "- $E=\\frac{1}{2}kA^2=\\frac{1}{2}mv_{\\max}^2$\n"
            "- $\\frac{1}{2}mv^2+\\frac{1}{2}kx^2=\\frac{1}{2}kA^2$\n"
            "- $v=\\omega\\sqrt{A^2-x^2}$\n"
            "- מטוטלת: $T=2\\pi\\sqrt{L/g}$ (זוויות קטנות)\n"
            "- $K=U$ ב-$x=\\pm A/\\sqrt{2}$\n"
            "- $A=\\sqrt{x_0^2+(v_0/\\omega)^2}$\n\n"
            "### תבניות שאלות טיפוסיות\n"
            "1. מהירות מקסימלית או אנרגיה מ-$k$, $m$, $A$.\n"
            "2. מהירות במיקום $x$ נתון.\n"
            "3. שבר אנרגיה קינטית ב-$x=A/2$ (או $A/3$).\n"
            "4. מחזור מטוטלת על כוכבים שונים.\n"
            "5. משרעת מתנאי התחלה. ציינו תמיד אם קירוב זווית קטנה חל.\n\n"
            "**חיסכון בזמן:** שרטטו תרשים אנרגיה ב-$x=0$, $x=A/2$ ו-$x=A$ לפני "
            "בחירת אלגברה — מונע טעויות סימן ושברים בלחץ בחינה."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Total energy is constant:** $E = \\frac{1}{2}kA^2$, split between "
            "$K = \\frac{1}{2}mv^2$ and $U = \\frac{1}{2}kx^2$.\n"
            "- **Speed at position x:** $v = \\omega\\sqrt{A^2-x^2}$; max at $x=0$: $v_{max}=A\\omega$.\n"
            "- **Energy fractions:** $K/E = 1 - x^2/A^2$; $U/E = x^2/A^2$.\n"
            "- **Equal K and U at:** $x = \\pm A/\\sqrt{2}$.\n"
            "- **Simple pendulum (small angle):** $T = 2\\pi\\sqrt{L/g}$; "
            "$\\omega = \\sqrt{g/L}$; independent of $m$ and $A$.\n"
            "- **Proof of energy conservation:** $dE/dt = v(m\\ddot{x}+kx) = 0$ by Newton's second law.\n"
            "- **Strategy:** Energy method for speed at position; pendulum formula for period on any planet."
        ),
        "body_he_md": (
            "- $E=\\frac{1}{2}kA^2=$ קבוע; מתחלק ל-$K=\\frac{1}{2}mv^2$ ו-$U=\\frac{1}{2}kx^2$.\n"
            "- $v=\\omega\\sqrt{A^2-x^2}$; $v_{\\max}=A\\omega$ ב-$x=0$.\n"
            "- $K/E=1-x^2/A^2$; $U/E=x^2/A^2$; $K=U$ ב-$x=\\pm A/\\sqrt{2}$.\n"
            "- מטוטלת (זווית קטנה): $T=2\\pi\\sqrt{L/g}$; $\\omega=\\sqrt{g/L}$; "
            "לא תלוי ב-$m$ וב-$A$.\n"
            "- הוכחת שימור: $dE/dt=v(m\\ddot{x}+kx)=0$ מחוק ניוטון השני.\n"
            "- **אסטרטגיה:** שיטת אנרגיה למהירות במיקום; נוסחת מטוטלת למחזור בכל כוכב ובכל $g$."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:** Total energy is fixed by amplitude: "
            "$E = \\tfrac{1}{2}kA^2 = \\tfrac{1}{2}(400)(0.01) = 2$ J. "
            "At $x=0$ all energy is kinetic, so "
            "$v_{max} = A\\sqrt{k/m} = 0.1\\sqrt{400} = 2$ m/s. "
            "Alternatively: $v_{max} = \\sqrt{2E/m} = \\sqrt{4} = 2$ m/s.\n\n"
            "**How to think about it:** Write $E = \\tfrac{1}{2}kA^2$ first — "
            "it encodes everything about the oscillation. Maximum speed always occurs "
            "at equilibrium where potential energy is zero.\n\n"
            "**Common slip:** Using $E = kA^2$ (missing the half). "
            "Computing $v_{max}$ at $x = A$ where speed is actually zero.\n\n"
            "**Exam tip:** When asked for both $E$ and $v_{max}$, compute $E$ once "
            "and reuse it — Bagrut partial credit rewards showing $E = \\tfrac{1}{2}mv_{max}^2$."
        ),
        "explanation_he": (
            "**למה זה נכון:** האנרגיה הכוללת נקבעת על ידי המשרעת: "
            "$E=\\tfrac{1}{2}kA^2=\\tfrac{1}{2}(400)(0.01)=2$ ג'ול. "
            "ב-$x=0$ כל האנרגיה קינטית, לכן "
            "$v_{\\max}=A\\sqrt{k/m}=0.1\\sqrt{400}=2$ מ/ש. "
            "לחלופין: $v_{\\max}=\\sqrt{2E/m}=\\sqrt{4}=2$ מ/ש.\n\n"
            "**איך לחשוב:** כתבו $E=\\tfrac{1}{2}kA^2$ קודם — "
            "זה מקודד את כל התנודה. מהירות מקסימלית תמיד בשיווי משקל "
            "שם האנרגיה הפוטנציאלית אפס.\n\n"
            "**טעות נפוצה:** $E=kA^2$ (חסר החצי). "
            "חישוב $v_{\\max}$ ב-$x=A$ שם המהירות בפועל אפס.\n\n"
            "**טיפ לבחינה:** כשמבקשים $E$ ו-$v_{\\max}$, חשבו $E$ פעם אחת "
            "והשתמשו שוב — נקודות חלקיות בבגרות על $E=\\tfrac{1}{2}mv_{\\max}^2$. "
            "אימות: $\\tfrac{1}{2}mv_{\\max}^2=\\tfrac{1}{2}(1)(4)=2$ ג'ול ✓."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** For a simple pendulum with small angles, "
            "$T = 2\\pi\\sqrt{L/g} = 2\\pi\\sqrt{1/9.8} \\approx 2.006$ s. "
            "Frequency is the reciprocal: $f = 1/T \\approx 0.499$ Hz.\n\n"
            "**How to think about it:** Pendulum period depends on length and gravity, "
            "not mass. A 1 m pendulum on Earth swings roughly once every 2 seconds — "
            "this is the classic 'seconds pendulum' reference (exact length is slightly "
            "less than 1 m).\n\n"
            "**Common slip:** Including mass in the formula. "
            "Using degrees instead of radians inside $\\sin\\theta \\approx \\theta$. "
            "Forgetting to take the reciprocal for frequency.\n\n"
            "**Exam tip:** Memorise $T = 2\\pi\\sqrt{L/g}$. "
            "If only period is asked, stop after $T$ — do not compute $f$ unless required."
        ),
        "explanation_he": (
            "**למה זה נכון:** למטוטלת פשוטה לזוויות קטנות, "
            "$T=2\\pi\\sqrt{L/g}=2\\pi\\sqrt{1/9.8}\\approx2.006$ ש'. "
            "תדירות היא ההפך: $f=1/T\\approx0.499$ Hz.\n\n"
            "**איך לחשוב:** מחזור מטוטלת תלוי באורך ובכבידה, לא במסה. "
            "מטוטלת 1 מ' על כדור הארץ מתנדנדת בערך פעם ב-2 שניות — "
            "זו ההתייחסות הקלאסית ל\"מטוטלת שניות\".\n\n"
            "**טעות נפוצה:** הכללת מסה בנוסחה. "
            "שימוש במעלות במקום רדיאנים ב-$\\sin\\theta\\approx\\theta$. "
            "שכחת לקחת הפך לתדירות.\n\n"
            "**טיפ לבחינה:** שיננו $T=2\\pi\\sqrt{L/g}$. "
            "אם מבקשים רק מחזור — עצרו אחרי $T$; אל תחשבו $f$ אלא אם נדרש. "
            "בדיקה: $f=1/2.006\\approx0.499$ Hz — עקבי עם $T$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** From $E = \\tfrac{1}{2}kA^2$, solve for amplitude: "
            "$A = \\sqrt{2E/k} = \\sqrt{2(0.5)/50} = \\sqrt{1/50} = \\sqrt{0.02} \\approx 0.141$ m.\n\n"
            "**How to think about it:** This is the inverse of the standard energy problem — "
            "you know total energy and spring constant, so amplitude follows algebraically. "
            "Larger $E$ or smaller $k$ means larger oscillation.\n\n"
            "**Common slip:** Using $A = E/k$ or $A = \\sqrt{E/k}$ (missing the factor 2). "
            "Forgetting to square-root after dividing. Reporting $A^2$ instead of $A$.\n\n"
            "**Exam tip:** Always write $A = \\sqrt{2E/k}$ before substituting numbers. "
            "Quick check: plug $A$ back into $\\tfrac{1}{2}kA^2$ — should recover $E = 0.5$ J."
        ),
        "explanation_he": (
            "**למה זה נכון:** מ-$E=\\tfrac{1}{2}kA^2$, פתרון למשרעת: "
            "$A=\\sqrt{2E/k}=\\sqrt{2(0.5)/50}=\\sqrt{0.02}\\approx0.141$ מ'.\n\n"
            "**איך לחשוב:** זו בעיה הפוכה לבעיית אנרגיה סטנדרטית — "
            "יודעים אנרגיה כוללת וקבוע קפיץ, המשרעת נובעת אלגברית. "
            "$E$ גדול יותר או $k$ קטן יותר → תנודה גדולה יותר.\n\n"
            "**טעות נפוצה:** $A=E/k$ או $A=\\sqrt{E/k}$ (חסר גורם 2). "
            "שכחת שורש אחרי חלוקה. דיווח על $A^2$ במקום $A$.\n\n"
            "**טיפ לבחינה:** כתבו $A=\\sqrt{2E/k}$ לפני הצבה. "
            "בדיקה מהירה: החזירו $A$ ל-$\\tfrac{1}{2}kA^2$ — צריך לקבל $E=0.5$ ג'ול. "
            "משרעת $\\approx0.14$ מ' סבירה ל-$k=50$ נ\"מ."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** On the Moon, $g_{moon} = 1.6$ m/s². "
            "$T = 2\\pi\\sqrt{L/g} = 2\\pi\\sqrt{0.5/1.6} = 2\\pi\\sqrt{0.3125} \\approx 3.51$ s. "
            "Weaker gravity means a slower, longer-period swing.\n\n"
            "**How to think about it:** The pendulum formula has $g$ in the denominator "
            "under the square root. Smaller $g$ → larger $T$. "
            "Earth's $T$ for the same $L=0.5$ m would be only $\\approx 1.42$ s.\n\n"
            "**Common slip:** Using Earth's $g = 9.8$ on the Moon. "
            "Inverting the ratio ($\\sqrt{g/L}$ instead of $\\sqrt{L/g}$). "
            "Thinking heavier mass slows the pendulum (mass cancels).\n\n"
            "**Exam tip:** Planet-change questions test whether you read $g$ carefully. "
            "Underline the given gravity before calculating — a 30-second habit saves points."
        ),
        "explanation_he": (
            "**למה זה נכון:** על הירח, $g_{\\text{ירח}}=1.6$ מ/ש². "
            "$T=2\\pi\\sqrt{L/g}=2\\pi\\sqrt{0.5/1.6}\\approx3.51$ ש'. "
            "כבידה חלשה יותר → נדנוד איטי יותר, מחזור ארוך יותר.\n\n"
            "**איך לחשוב:** בנוסחת המטוטלת $g$ במכנה תחת השורש. "
            "$g$ קטן → $T$ גדול. על כדור הארץ, אותו $L=0.5$ מ' נותן רק $\\approx1.42$ ש'.\n\n"
            "**טעות נפוצה:** $g=9.8$ של כדור הארץ על הירח. "
            "היפוך היחס ($\\sqrt{g/L}$ במקום $\\sqrt{L/g}$). "
            "חשיבה שמסה כבדה מאטה (המסה מתבטלת).\n\n"
            "**טיפ לבחינה:** שאלות החלפת כוכב בודקות קריאת $g$. "
            "סמנו את $g$ הנתון לפני חישוב — הרגל של 30 שניות חוסכת נקודות."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** First find $\\omega = \\sqrt{k/m} = \\sqrt{200/0.5} = 20$ rad/s. "
            "Speed at position: $v = \\omega\\sqrt{A^2-x^2} = 20\\sqrt{0.04-0.01} = 20\\sqrt{0.03} "
            "\\approx 3.46$ m/s. Acceleration: $a = -\\omega^2 x = -400(0.1) = -40$ m/s² "
            "(restoring, toward equilibrium).\n\n"
            "**How to think about it:** Energy gives speed; kinematics gives acceleration. "
            "At $x = 0.1$ m (half amplitude), the mass is slowing toward the turning point "
            "but still has substantial kinetic energy ($K/E = 3/4$).\n\n"
            "**Common slip:** Forgetting the minus sign on $a$ (acceleration points toward $x=0$). "
            "Using $v = \\omega x$ instead of $\\omega\\sqrt{A^2-x^2}$. "
            "Computing speed at $x=A$ instead of $x=0.1$ m.\n\n"
            "**Exam tip:** When both $v$ and $a$ are asked, compute $\\omega$ once and reuse. "
            "State that $a$ is negative because displacement is positive and force is restoring."
        ),
        "explanation_he": (
            "**למה זה נכון:** קודם $\\omega=\\sqrt{k/m}=\\sqrt{200/0.5}=20$ ראד/ש. "
            "מהירות: $v=\\omega\\sqrt{A^2-x^2}=20\\sqrt{0.03}\\approx3.46$ מ/ש. "
            "תאוצה: $a=-\\omega^2 x=-400(0.1)=-40$ מ/ש² (משחזר, לכיוון שיווי משקל).\n\n"
            "**איך לחשוב:** אנרגיה נותנת מהירות; קינמטיקה נותנת תאוצה. "
            "ב-$x=0.1$ מ' (חצי משרעת), המסה מאטה לקראת נקודת היפוך "
            "אך עדיין עם אנרגיה קינטית משמעותית ($K/E=3/4$).\n\n"
            "**טעות נפוצה:** שכחת מינוס ב-$a$ (תאוצה לכיוון $x=0$). "
            "$v=\\omega x$ במקום $\\omega\\sqrt{A^2-x^2}$. "
            "חישוב מהירות ב-$x=A$ במקום $x=0.1$ מ'.\n\n"
            "**טיפ לבחינה:** כשמבקשים $v$ ו-$a$, חשבו $\\omega$ פעם אחת. "
            "ציינו ש-$a$ שלילי כי התזוזה חיובית והכוח משחזר."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Invert the pendulum formula: "
            "$T = 2\\pi\\sqrt{L/g} \\Rightarrow L = g(T/2\\pi)^2$. "
            "With $T = 2$ s and $g = 9.8$ m/s²: "
            "$L = 9.8 \\times (2/2\\pi)^2 = 9.8/\\pi^2 \\approx 0.993$ m.\n\n"
            "**How to think about it:** The 'seconds pendulum' is defined by its period, "
            "not its length being exactly 1 m. Solving for $L$ requires squaring $T/2\\pi$ — "
            "a common inverse problem on university exams.\n\n"
            "**Common slip:** Using $L = gT/2\\pi$ without squaring. "
            "Putting $T$ in minutes instead of seconds. "
            "Using $\\pi$ instead of $2\\pi$ in the denominator.\n\n"
            "**Exam tip:** Rearrange to $L = g(T/2\\pi)^2$ before plugging numbers. "
            "Verify: plug $L \\approx 1$ m back — should give $T \\approx 2$ s on Earth."
        ),
        "explanation_he": (
            "**למה זה נכון:** הפכו את נוסחת המטוטלת: "
            "$T=2\\pi\\sqrt{L/g}\\Rightarrow L=g(T/2\\pi)^2$. "
            "עם $T=2$ ש' ו-$g=9.8$ מ/ש²: "
            "$L=9.8\\times(2/2\\pi)^2=9.8/\\pi^2\\approx0.993$ מ'.\n\n"
            "**איך לחשוב:** \"מטוטלת שניות\" מוגדרת לפי מחזור, "
            "לא לפי אורך בדיוק 1 מ'. פתרון ל-$L$ דורש ריבוע $T/2\\pi$ — "
            "בעיה הפוכה נפוצה בבחינות אוניברסיטה.\n\n"
            "**טעות נפוצה:** $L=gT/2\\pi$ בלי ריבוע. "
            "$T$ בדקות במקום שניות. "
            "$\\pi$ במקום $2\\pi$ במכנה.\n\n"
            "**טיפ לבחינה:** סדרו ל-$L=g(T/2\\pi)^2$ לפני הצבה. "
            "אימות: החזירו $L\\approx1$ מ' — צריך $T\\approx2$ ש' על כדור הארץ. "
            "מטוטלת שניות אינה בדיוק 1 מ' — היא $\\approx0.993$ מ'."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** At $x = A/3$, potential energy is "
            "$U = \\tfrac{1}{2}k(A/3)^2 = \\tfrac{1}{9} \\cdot \\tfrac{1}{2}kA^2 = E/9$. "
            "Therefore $K = E - U = 8E/9$, and $K/E = 8/9 \\approx 88.9\\%$.\n\n"
            "**How to think about it:** Use the general formula $K/E = 1 - x^2/A^2$. "
            "At $x = A/3$, this gives $1 - 1/9 = 8/9$ instantly — no need to compute $E$ numerically.\n\n"
            "**Common slip:** Answering $1/3$ (confusing displacement ratio with energy ratio). "
            "Computing $U/E = 1/3$ and stopping (that is potential, not kinetic). "
            "Using $K = \\tfrac{1}{2}k(A/3)^2$ as kinetic instead of potential.\n\n"
            "**Exam tip:** Fraction questions are faster with $K/E = 1 - x^2/A^2$. "
            "Memorise: at $x = A/2$, $K/E = 3/4$; at $x = A/\\sqrt{2}$, $K/E = 1/2$."
        ),
        "explanation_he": (
            "**למה זה נכון:** ב-$x=A/3$, אנרגיה פוטנציאלית "
            "$U=\\tfrac{1}{2}k(A/3)^2=\\tfrac{1}{9}\\cdot\\tfrac{1}{2}kA^2=E/9$. "
            "לכן $K=E-U=8E/9$, ו-$K/E=8/9\\approx88.9\\%$.\n\n"
            "**איך לחשוב:** השתמשו ב-$K/E=1-x^2/A^2$. "
            "ב-$x=A/3$ מקבלים $1-1/9=8/9$ מיד — אין צורך לחשב $E$ מספרית.\n\n"
            "**טעות נפוצה:** תשובה $1/3$ (בלבול יחס תזוזה עם יחס אנרגיה). "
            "$U/E=1/3$ ועצירה (זו פוטנציאלית, לא קינטית). "
            "$K=\\tfrac{1}{2}k(A/3)^2$ כקינטית במקום פוטנציאלית.\n\n"
            "**טיפ לבחינה:** שאלות שבר מהירות עם $K/E=1-x^2/A^2$. "
            "שיננו: ב-$x=A/2$, $K/E=3/4$; ב-$x=A/\\sqrt{2}$, $K/E=1/2$. "
            "ב-$x=A/3$, $U/E=1/9$ ו-$K/E=8/9$ — אל תבלבלו ביניהם."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** The block is placed gently at $x = 0.08$ m with $v = 0$, "
            "so energy $E = \\tfrac{1}{2}(100)(0.0064) = 0.32$ J is unchanged (no impulse). "
            "New mass $m' = 0.8$ kg gives $\\omega' = \\sqrt{100/0.8} = \\sqrt{125} \\approx 11.18$ rad/s. "
            "From $E = \\tfrac{1}{2}kA'^2$: $A' = \\sqrt{2(0.32)/100} = 0.08$ m — amplitude unchanged! "
            "New period: $T' = 2\\pi/11.18 \\approx 0.562$ s.\n\n"
            "**How to think about it:** Doubling mass at fixed displacement with zero velocity "
            "does not change stored energy, so amplitude stays the same. "
            "But larger mass means smaller $\\omega$ and longer period.\n\n"
            "**Common slip:** Assuming amplitude halves when mass doubles. "
            "Adding masses' kinetic energy when the second block is placed gently. "
            "Forgetting that period depends on $\\omega = \\sqrt{k/m}$.\n\n"
            "**Exam tip:** 'Gently placed' means no change in total energy — "
            "a key phrase on Bagrut composite-body SHM problems."
        ),
        "explanation_he": (
            "**למה זה נכון:** הבלוק מונח בעדינות ב-$x=0.08$ מ' עם $v=0$, "
            "לכן $E=\\tfrac{1}{2}(100)(0.0064)=0.32$ ג'ול לא משתנה (ללא דחף). "
            "מסה חדשה $m'=0.8$ ק\"ג נותנת $\\omega'=\\sqrt{100/0.8}\\approx11.18$ ראד/ש. "
            "מ-$E=\\tfrac{1}{2}kA'^2$: $A'=0.08$ מ' — משרעת ללא שינוי! "
            "מחזור חדש: $T'=2\\pi/11.18\\approx0.562$ ש'.\n\n"
            "**איך לחשוב:** הכפלת מסה בתזוזה קבועה עם $v=0$ "
            "לא משנה אנרגיה מאוחסנת, לכן משרעת נשארת. "
            "אך מסה גדולה → $\\omega$ קטן → מחזור ארוך יותר.\n\n"
            "**טעות נפוצה:** הנחה שמשרעת מתחלקת ב-2 כשמכפילים מסה. "
            "הוספת אנרגיה קינטית כשמניחים בעדינות. "
            "שכחה שמחזור תלוי ב-$\\omega=\\sqrt{k/m}$.\n\n"
            "**טיפ לבחינה:** \"מונח בעדינות\" = אנרגיה כוללת לא משתנה — "
            "ביטוי מפתח בשאלות SHM עם גופים מרוכבים בבגרות."
        ),
    },
]


EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Step 1 — Total energy:** $E=\\tfrac{1}{2}kA^2=\\tfrac{1}{2}(400)(0.01)=2$ J.\n\n**Step 2 — Maximum speed at $x=0$:** $v_{max}=A\\sqrt{k/m}=0.1\\sqrt{400}=2$ m/s. Check: $\\tfrac{1}{2}mv_{max}^2=\\tfrac{1}{2}(1)(4)=2$ J ✓.",
        "solution_he": "**שלב 1 — אנרגיה כוללת:** $E=\\tfrac{1}{2}kA^2=\\tfrac{1}{2}(400)(0.01)=2$ ג'ול.\n\n**שלב 2 — מהירות מקסימלית ב-$x=0$:** $v_{\\max}=A\\sqrt{k/m}=0.1\\sqrt{400}=2$ מ/ש. אימות: $\\tfrac{1}{2}mv_{\\max}^2=2$ ג'ול ✓.",
    },
    "e2": {
        "solution_en": "**Step 1 — Period:** $T=2\\pi\\sqrt{L/g}=2\\pi\\sqrt{1/9.8}\\approx2.006$ s.\n\n**Step 2 — Frequency:** $f=1/T\\approx0.499$ Hz. Note: mass does not enter the pendulum formula.",
        "solution_he": "**שלב 1 — מחזור:** $T=2\\pi\\sqrt{1/9.8}\\approx2.006$ ש'.\n\n**שלב 2 — תדירות:** $f=1/T\\approx0.499$ Hz. שימו לב: המסה לא מופיעה בנוסחת המטוטלת.",
    },
    "e3": {
        "solution_en": "From $E=\\tfrac{1}{2}kA^2$: $A=\\sqrt{2E/k}=\\sqrt{2(0.5)/50}=\\sqrt{0.02}\\approx0.141$ m. Verify: $\\tfrac{1}{2}(50)(0.02)=0.5$ J ✓.",
        "solution_he": "מ-$E=\\tfrac{1}{2}kA^2$: $A=\\sqrt{2E/k}=\\sqrt{0.02}\\approx0.141$ מ'. אימות: $\\tfrac{1}{2}(50)(0.02)=0.5$ ג'ול ✓.",
    },
    "e4": {
        "solution_en": "Use Moon gravity: $T=2\\pi\\sqrt{L/g_{moon}}=2\\pi\\sqrt{0.5/1.6}\\approx3.51$ s. Compare Earth: same $L$ gives $T\\approx1.42$ s — weaker $g$ means slower swing.",
        "solution_he": "השתמשו ב-$g$ של הירח: $T=2\\pi\\sqrt{0.5/1.6}\\approx3.51$ ש'. השוואה לכדור הארץ: אותו $L$ נותן $T\\approx1.42$ ש' — $g$ חלש יותר → נדנוד איטי יותר.",
    },
    "e5": {
        "solution_en": "$\\omega=\\sqrt{k/m}=\\sqrt{200/0.5}=20$ rad/s. Speed: $v=\\omega\\sqrt{A^2-x^2}=20\\sqrt{0.04-0.01}\\approx3.46$ m/s. Acceleration: $a=-\\omega^2 x=-400(0.1)=-40$ m/s² (restoring).",
        "solution_he": "$\\omega=\\sqrt{200/0.5}=20$ ראד/ש. מהירות: $v=20\\sqrt{0.03}\\approx3.46$ מ/ש. תאוצה: $a=-\\omega^2 x=-40$ מ/ש² (משחזר, לכיוון $x=0$).",
    },
    "e6": {
        "solution_en": "Invert: $L=g(T/2\\pi)^2=9.8\\times(2/2\\pi)^2=9.8/\\pi^2\\approx0.993$ m. The 'seconds pendulum' is slightly shorter than 1 m on Earth.",
        "solution_he": "הפכו: $L=g(T/2\\pi)^2=9.8/\\pi^2\\approx0.993$ מ'. \"מטוטלת שניות\" קצת קצרה מ-1 מ' על כדור הארץ.",
    },
    "e7": {
        "solution_en": "Use $K/E=1-x^2/A^2$. At $x=A/3$: $K/E=1-1/9=8/9\\approx88.9\\%$. Alternatively: $U=E/9$, so $K=8E/9$.",
        "solution_he": "השתמשו ב-$K/E=1-x^2/A^2$. ב-$x=A/3$: $K/E=1-1/9=8/9\\approx88.9\\%$. לחלופין: $U=E/9$, לכן $K=8E/9$.",
    },
    "e8": {
        "solution_en": "Gently placed → no impulse, so $E=\\tfrac{1}{2}(100)(0.0064)=0.32$ J unchanged. New $m=0.8$ kg: $\\omega'=\\sqrt{100/0.8}\\approx11.18$ rad/s. $A'=\\sqrt{2E/k}=0.08$ m (unchanged). $T'=2\\pi/\\omega'\\approx0.562$ s.",
        "solution_he": "הנחה בעדינות → ללא דחף, $E=0.32$ ג'ול לא משתנה. $m=0.8$ ק\"ג: $\\omega'\\approx11.18$ ראד/ש. $A'=0.08$ מ' (ללא שינוי). $T'\\approx0.562$ ש'.",
    },
    "e9": {
        "solution_en": "(a) $\\omega=\\sqrt{g/L}=\\sqrt{4.9}\\approx2.214$ rad/s; $T=2\\pi/\\omega\\approx2.837$ s. (b) $\\dot{\\theta}_{max}=\\theta_0\\omega=(10\\pi/180)(2.214)\\approx0.386$ rad/s. (c) $v_{max}=L\\dot{\\theta}_{max}\\approx0.773$ m/s. Energy check: $\\sqrt{2gL(1-\\cos10°)}\\approx0.772$ m/s ✓.",
        "solution_he": "(א) $\\omega\\approx2.214$ ראד/ש; $T\\approx2.837$ ש'. (ב) $\\dot{\\theta}_{\\max}\\approx0.386$ ראד/ש. (ג) $v_{\\max}=L\\dot{\\theta}_{\\max}\\approx0.773$ מ/ש. בדיקת אנרגיה: $\\sqrt{2gL(1-\\cos10°)}\\approx0.772$ מ/ש ✓.",
    },
    "e10": {
        "solution_en": "$\\omega=\\sqrt{100/0.25}=20$ rad/s. (a) $A=\\sqrt{x_0^2+(v_0/\\omega)^2}=\\sqrt{0.0036+0.0036}=0.0849$ m. (b) $E=\\tfrac{1}{2}kA^2=0.36$ J. Cross-check: $\\tfrac{1}{2}kx_0^2+\\tfrac{1}{2}mv_0^2=0.18+0.18=0.36$ J ✓.",
        "solution_he": "$\\omega=20$ ראד/ש. (א) $A=\\sqrt{0.0036+0.0036}=0.0849$ מ'. (ב) $E=0.36$ ג'ול. אימות: $\\tfrac{1}{2}kx_0^2+\\tfrac{1}{2}mv_0^2=0.36$ ג'ול ✓.",
    },
    "e11": {
        "solution_en": "$\\tfrac{dE}{dt}=mv\\dot{v}+kx\\dot{x}=v(m\\ddot{x}+kx)$. From SHM: $m\\ddot{x}=-kx$, so $m\\ddot{x}+kx=0$. Therefore $dE/dt=0$ and $E=\\tfrac{1}{2}kA^2$ is constant. $\\square$",
        "solution_he": "$\\tfrac{dE}{dt}=v(m\\ddot{x}+kx)$. מ-SHM: $m\\ddot{x}=-kx$, לכן $m\\ddot{x}+kx=0$. מכאן $dE/dt=0$ ו-$E=\\tfrac{1}{2}kA^2$ קבועה. $\\square$",
    },
}


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
            for ex in sec.get("exercises", []):
                sol = EXERCISE_SOLUTIONS.get(ex.get("id"))
                if sol:
                    ex.update(sol)
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
