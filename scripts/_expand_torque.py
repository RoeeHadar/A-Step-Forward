#!/usr/bin/env python3
"""Expand torque.json — substantive bilingual content per expand-lessons-cursor."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/torque.json"

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


EXPLANATIONS = {
    1: {
        "en": (
            "Torque is proportional to both the applied force and the distance from the pivot, "
            "but only through the product $rF\\sin\\theta$. When force doubles ($F \\to 2F$) and "
            "distance halves ($r \\to r/2$), these two changes cancel exactly:\n"
            "$$\\tau_{\\text{new}} = \\frac{r}{2}(2F)\\sin\\theta = rF\\sin\\theta = \\tau_{\\text{original}}$$\n\n"
            "**Why option 2 is correct:** The compensating changes leave torque unchanged — a classic "
            "proportional-reasoning question on Bagrut statics.\n\n"
            "**Common wrong path:** Answering \"torque doubles\" by focusing only on the doubled force, "
            "or \"torque halves\" by focusing only on the halved distance. Both factors must be "
            "multiplied together.\n\n"
            "**Exam tip:** Before calculating, ask: \"Which quantities enter the formula together?\" "
            "For torque, $r$ and $F$ always appear as a product with $\\sin\\theta$."
        ),
        "he": (
            "מומנט סיבוב פרופורציוני גם לכוח המופעל וגם למרחק מהציר, אך רק דרך המכפלה "
            "$rF\\sin\\theta$. כשהכוח מוכפל ($F \\to 2F$) והמרחק מחצה ($r \\to r/2$), "
            "שתי השינויים מתקזזים בדיוק:\n"
            "$$\\tau_{\\text{new}} = \\frac{r}{2}(2F)\\sin\\theta = rF\\sin\\theta = \\tau_{\\text{original}}$$\n\n"
            "**למה אפשרות 2 נכונה:** השינויים המקזזים משאירים את המומנט ללא שינוי — שאלת "
            "היגיון פרופורציונלי קלאסית בסטטיקה בבגרות.\n\n"
            "**טעות נפוצה:** תשובה \"מומנט מוכפל\" מתוך התמקדות רק בכפלת הכוח, או \"מומנט מחצה\" "
            "מתוך התמקדות רק בחציית המרחק. יש להכפיל את שני הגורמים יחד.\n\n"
            "**טיפ לבחינה:** לפני חישוב, שאלו: \"אילו כמויות נכנסות לנוסחה יחד?\" במומנט, "
            "$r$ ו-$F$ תמיד מופיעים כמכפלה עם $\\sin\\theta$."
        ),
    },
    2: {
        "en": (
            "The force is applied at an angle $\\theta = 30°$ to the arm of length $r = 0.4$ m. "
            "Only the perpendicular component of the force contributes to rotation, so we use "
            "$\\tau = rF\\sin\\theta$.\n\n"
            "Substituting $F = 60$ N:\n"
            "$$\\tau = 0.4 \\times 60 \\times \\sin 30° = 24 \\times 0.5 = 12\\;\\text{N·m}$$\n\n"
            "Since $\\sin 30° = 0.5$, exactly half the force produces rotation — the other half "
            "pulls along the arm without twisting it.\n\n"
            "**Common wrong path:** Using $\\tau = rF$ without the $\\sin\\theta$ factor, giving "
            "$24$ N·m instead of $12$ N·m. This happens when students treat the angle as if the "
            "force were perpendicular.\n\n"
            "**Exam tip:** Draw the force vector and identify $\\theta$ as the angle between "
            "$\\vec{r}$ and $\\vec{F}$. If the problem says \"at $30°$ to the arm,\" that angle "
            "is $\\theta$ directly."
        ),
        "he": (
            "הכוח מופעל בזווית $\\theta = 30°$ לזרוע באורך $r = 0.4$ m. רק הרכיב המאונך "
            "של הכוח תורם לסיבוב, ולכן משתמשים ב-$\\tau = rF\\sin\\theta$.\n\n"
            "הצבה $F = 60$ N:\n"
            "$$\\tau = 0.4 \\times 60 \\times \\sin 30° = 24 \\times 0.5 = 12\\;\\text{N·m}$$\n\n"
            "מאחר ש-$\\sin 30° = 0.5$, בדיוק מחצית מהכוח מייצרת סיבוב — השנייה מושכת "
            "לאורך הזרוע בלי לסובב.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\tau = rF$ ללא גורם $\\sin\\theta$, וקבלת $24$ N·m "
            "במקום $12$ N·m. זה קורה כשמטפלים בזווית כאילו הכוח מאונך.\n\n"
            "**טיפ לבחינה:** ציירו את וקטור הכוח וזהו את $\\theta$ כזווית בין $\\vec{r}$ "
            "ל-$\\vec{F}$. אם הבעיה אומרת \"בזווית $30°$ לזרוע,\" זו $\\theta$ ישירות."
        ),
    },
    3: {
        "en": (
            "When a force acts perpendicular to an arm, $\\theta = 90°$ and $\\sin 90° = 1$, "
            "so the formula simplifies to $\\tau = rF$. Here $F = 40$ N and $r = 0.6$ m.\n\n"
            "$$\\tau = 40 \\times 0.6 = 24\\;\\text{N·m}$$\n\n"
            "This is the simplest torque case — the entire force contributes to rotation because "
            "it is applied at right angles to the position vector from the pivot.\n\n"
            "**Common wrong path:** Confusing the arm length with the moment arm when the force "
            "is not perpendicular. Here they coincide because $\\theta = 90°$.\n\n"
            "**Exam tip:** When you see \"perpendicular,\" jump directly to $\\tau = rF$. "
            "Always include units (N·m) in your final answer on Bagrut."
        ),
        "he": (
            "כשכוח פועל מאונך לזרוע, $\\theta = 90°$ ו-$\\sin 90° = 1$, ולכן הנוסחה מתפשטת "
            "ל-$\\tau = rF$. כאן $F = 40$ N ו-$r = 0.6$ m.\n\n"
            "$$\\tau = 40 \\times 0.6 = 24\\;\\text{N·m}$$\n\n"
            "זה המקרה הפשוט ביותר של מומנט — כל הכוח תורם לסיבוב כי הוא מופעל בזווית "
            "ישרה לוקטור המיקום מהציר.\n\n"
            "**טעות נפוצה:** בלבול בין אורך הזרוע לזרוע המומנט כשהכוח לא מאונך. "
            "כאן הם מתאימים כי $\\theta = 90°$.\n\n"
            "**טיפ לבחינה:** כשמופיע \"מאונך,\" קפצו ישירות ל-$\\tau = rF$. "
            "תמיד כללו יחידות (N·m) בתשובה הסופית בבגרות. "
            "בדקו שהתוצאה $24$ N·m הגיונית: כוח בינוני על זרוע קצרה."
        ),
    },
    4: {
        "en": (
            "A horizontal force pushes on a door at distance $r = 0.8$ m from the hinges. "
            "The force is perpendicular to the door surface, so it is also perpendicular to "
            "the position vector from the hinge — meaning $\\theta = 90°$.\n\n"
            "$$\\tau = F \\cdot r = 50 \\times 0.8 = 40\\;\\text{N·m}$$\n\n"
            "This is exactly why door handles are placed far from the hinge: the same push "
            "force produces much larger torque at the handle than near the pivot.\n\n"
            "**Common wrong path:** Using the full door width instead of the given $0.8$ m "
            "distance, or forgetting that perpendicular force means $\\sin\\theta = 1$.\n\n"
            "**Exam tip:** Door-and-wrench problems are the standard intuition check for torque. "
            "Identify pivot, force direction, and perpendicular distance before substituting."
        ),
        "he": (
            "כוח אופקי דוחף על דלת במרחק $r = 0.8$ m מהצירים. הכוח מאונך לשטח הדלת, "
            "ולכן גם מאונך לוקטור המיקום מהציר — כלומר $\\theta = 90°$.\n\n"
            "$$\\tau = F \\cdot r = 50 \\times 0.8 = 40\\;\\text{N·m}$$\n\n"
            "זו בדיוק הסיבה שידיות דלתות ממוקמות רחוק מהציר: אותו דחיפה מייצרת מומנט "
            "גדול הרבה יותר בידית מאשר ליד הציר.\n\n"
            "**טעות נפוצה:** שימוש ברוחב הדלת המלא במקום המרחק $0.8$ m הנתון, "
            "או שכחה שכוח מאונך פירושו $\\sin\\theta = 1$.\n\n"
            "**טיפ לבחינה:** בעיות דלת ומפתח הן בדיקת אינטואיציה סטנדרטית למומנט. "
            "זהו ציר, כיוון כוח, ומרחק מאונך לפני הצבה. "
            "המרחק $0.8$ m הוא זרוע המומנט כי הכוח מאונך לדלת."
        ),
    },
    5: {
        "en": (
            "Torque requires a moment arm — the perpendicular distance from the pivot to the "
            "line of action of the force. When the force passes directly through the pivot, "
            "that perpendicular distance is zero: $d_{\\perp} = 0$.\n\n"
            "Therefore $\\tau = F \\cdot d_{\\perp} = F \\times 0 = 0$, regardless of how "
            "large the force is.\n\n"
            "**Why zero is correct:** A force through the pivot produces no tendency to rotate "
            "the body — it only pushes or pulls along a line through the axis.\n\n"
            "**Common wrong path:** Answering that torque equals the force itself, or computing "
            "$\\tau = rF$ using some nonzero distance incorrectly.\n\n"
            "**Exam tip:** Always ask: \"Does the line of action pass through the pivot?\" "
            "If yes, torque about that pivot is automatically zero."
        ),
        "he": (
            "מומנט דורש זרוע מומנט — המרחק המאונך מהציר לקו הפעולה של הכוח. כשהכוח "
            "עובר ישירות דרך הציר, המרחק המאונך הזה הוא אפס: $d_{\\perp} = 0$.\n\n"
            "לכן $\\tau = F \\cdot d_{\\perp} = F \\times 0 = 0$, ללא קשר לגודל הכוח.\n\n"
            "**למה אפס נכון:** כוח דרך הציר לא מייצר נטייה לסובב את הגוף — רק דוחף "
            "או מושך לאורך קו שעובר דרך הציר.\n\n"
            "**טעות נפוצה:** תשובה שמומנט שווה לכוח עצמו, או חישוב $\\tau = rF$ "
            "עם מרחק שונה מאפס שלא לצורך.\n\n"
            "**טיפ לבחינה:** תמיד שאלו: \"האם קו הפעולה עובר דרך הציר?\" "
            "אם כן, המומנט סביב אותו ציר הוא אוטומטית אפס."
        ),
    },
    6: {
        "en": (
            "Newton's second law for rotation connects net torque to angular acceleration: "
            "$\\tau_{\\text{net}} = I\\alpha$. This is the direct rotational analogue of "
            "$F = ma$.\n\n"
            "Given $\\tau = 15$ N·m and $I = 3$ kg·m²:\n"
            "$$\\alpha = \\frac{\\tau}{I} = \\frac{15}{3} = 5\\;\\text{rad/s}^2$$\n\n"
            "The positive result means the object accelerates in the direction of the applied "
            "net torque (counterclockwise, by convention).\n\n"
            "**Common wrong path:** Dividing by radius instead of moment of inertia, or "
            "confusing $\\alpha$ with linear acceleration $a$.\n\n"
            "**Exam tip:** Check units: N·m divided by kg·m² gives rad/s². "
            "If your units do not work out, re-read which rotational quantity you need."
        ),
        "he": (
            "חוק ניוטון השני לסיבוב מקשר מומנט נטו לתאוצה זוויתית: $\\tau_{\\text{net}} = I\\alpha$. "
            "זה האנלוג הסיבובי הישיר של $F = ma$.\n\n"
            "נתון $\\tau = 15$ N·m ו-$I = 3$ kg·m²:\n"
            "$$\\alpha = \\frac{\\tau}{I} = \\frac{15}{3} = 5\\;\\text{rad/s}^2$$\n\n"
            "התוצאה החיובית פירושה שהגוף מאיץ בכיוון המומנט הנטו (נגד כיוון השעון, "
            "לפי המוסכמה).\n\n"
            "**טעות נפוצה:** חלוקה ברדיוס במקום במומנט התמדה, או בלבול בין $\\alpha$ "
            "לתאוצה לינארית $a$.\n\n"
            "**טיפ לבחינה:** בדקו יחידות: N·m חלקי kg·m² נותן rad/s². "
            "אם היחידות לא מתאימות, קראו מחדש איזו כמות סיבובית נדרשת. "
            "תוצאה $5$ rad/s² פירושה שהגוף מסתובב מהר יותר עם מומנט התמדה קטן יותר."
        ),
    },
    7: {
        "en": (
            "The force acts at $\\theta = 45°$ to a $1.2$ m arm. Use the full formula "
            "$\\tau = rF\\sin\\theta$ because the force is not perpendicular to the arm.\n\n"
            "$$\\tau = 1.2 \\times 60 \\times \\sin 45° = 72 \\times \\frac{\\sqrt{2}}{2} "
            "= 36\\sqrt{2} \\approx 50.9\\;\\text{N·m}$$\n\n"
            "At $45°$, $\\sin\\theta = \\cos\\theta$, so the effective turning component "
            "equals $60/\\sqrt{2} \\approx 42.4$ N — about 71% of the full force.\n\n"
            "**Common wrong path:** Using $\\tau = rF = 72$ N·m and ignoring the angle entirely. "
            "Another slip: using $\\cos 45°$ instead of $\\sin 45°$ when $\\theta$ is measured "
            "between $\\vec{r}$ and $\\vec{F}$.\n\n"
            "**Exam tip:** For $45°$, remember $\\sin 45° = \\sqrt{2}/2$. "
            "Bagrut often uses this angle because the arithmetic stays clean."
        ),
        "he": (
            "הכוח פועל בזווית $\\theta = 45°$ לזרוע באורך $1.2$ m. השתמשו בנוסחה המלאה "
            "$\\tau = rF\\sin\\theta$ כי הכוח לא מאונך לזרוע.\n\n"
            "$$\\tau = 1.2 \\times 60 \\times \\sin 45° = 72 \\times \\frac{\\sqrt{2}}{2} "
            "= 36\\sqrt{2} \\approx 50.9\\;\\text{N·m}$$\n\n"
            "ב-$45°$, $\\sin\\theta = \\cos\\theta$, ולכן הרכיב הסיבובי האפקטיבי "
            "שווה ל-$60/\\sqrt{2} \\approx 42.4$ N — כ-71% מהכוח המלא.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\tau = rF = 72$ N·m והתעלמות מהזווית לחלוטין. "
            "טעות נוספת: שימוש ב-$\\cos 45°$ במקום $\\sin 45°$ כש-$\\theta$ נמדד "
            "בין $\\vec{r}$ ל-$\\vec{F}$.\n\n"
            "**טיפ לבחינה:** ל-$45°$, זכרו $\\sin 45° = \\sqrt{2}/2$. "
            "בבגרות משתמשים לעיתים קרובות בזווית זו כי החשבון נשאר נקי. "
            "אם קיבלתם $72$ N·m, שכחתם את $\\sin\\theta$ — חזרו לנוסחה המלאה."
        ),
    },
    8: {
        "en": (
            "With the pivot at one end, each force produces torque $\\tau_i = r_i F_i$ with "
            "sign determined by rotation direction. CCW is positive; CW is negative.\n\n"
            "$\\tau_1 = +10 \\times 0.5 = +5$ N·m (CCW)\n"
            "$\\tau_2 = -8 \\times 1.5 = -12$ N·m (CW)\n"
            "$$\\tau_{\\text{net}} = +5 + (-12) = -7\\;\\text{N·m}$$\n\n"
            "The negative sign means the net rotation tendency is clockwise.\n\n"
            "**Common wrong path:** Adding magnitudes without signs ($5 + 12 = 17$), or "
            "using the total beam length $2$ m instead of each force's distance from the pivot.\n\n"
            "**Exam tip:** Draw the beam, mark the pivot, and label each force with its distance "
            "and direction before summing. Sign conventions must stay consistent throughout."
        ),
        "he": (
            "עם הציר בקצה אחד, כל כוח מייצר מומנט $\\tau_i = r_i F_i$ עם סימן לפי כיוון "
            "הסיבוב. נגד כיוון השעון = חיובי; כיוון השעון = שלילי.\n\n"
            "$\\tau_1 = +10 \\times 0.5 = +5$ N·m (נגד השעון)\n"
            "$\\tau_2 = -8 \\times 1.5 = -12$ N·m (כיוון השעון)\n"
            "$$\\tau_{\\text{net}} = +5 + (-12) = -7\\;\\text{N·m}$$\n\n"
            "הסימן השלילי פירושו שנטיית הסיבוב הנטו היא בכיוון השעון.\n\n"
            "**טעות נפוצה:** חיבור גדלים ללא סימנים ($5 + 12 = 17$), או שימוש "
            "באורך הקורה $2$ m במקום המרחק של כל כוח מהציר.\n\n"
            "**טיפ לבחינה:** ציירו את הקורה, סמנו את הציר, וסמנו כל כוח עם מרחקו "
            "וכיוונו לפני הסכימה. מוסכמת הסימנים חייבת להישאר עקבית."
        ),
    },
}


def build_lesson():
    with open(OUT, encoding="utf-8") as f:
        lesson = json.load(f)

    section_bodies = {
        "intro": {
            "en": (
                "When you push open a door near the hinge versus near the handle — same force, "
                "very different effect. The key quantity is **torque** (moment): how effectively "
                "a force causes rotation about a pivot. Torque is the rotational analogue of force, "
                "just as angular acceleration is the rotational analogue of linear acceleration.\n\n"
                "In everyday life, torque explains why wrenches have long handles, why seesaws "
                "balance when weights and distances are arranged correctly, and why a tight bolt "
                "needs more leverage, not just more muscle.\n\n"
                "**In Israeli HS and university physics:** Torque appears in rotational dynamics, "
                "static equilibrium (levers, beams, ladders), and angular momentum. Bagrut "
                "questionnaire 1 regularly asks you to find net torque, moment arm, or angular "
                "acceleration via $\\tau = I\\alpha$.\n\n"
                "By the end of this lesson you will compute torque magnitude and direction, "
                "identify the correct moment arm, sum torques with proper sign conventions, "
                "and connect torque to Newton's second law for rotation."
            ),
            "he": (
                "כשדוחפים דלת קרוב לציר לעומת קרוב לידית — אותו כוח, השפעה שונה לחלוטין. "
                "הכמות המרכזית היא **מומנט סיבוב**: עד כמה יעיל כוח בגרימת סיבוב סביב ציר. "
                "מומנט הוא האנלוג הסיבובי של כוח, כמו שתאוצה זוויתית היא האנלוג הסיבובי "
                "של תאוצה לינארית.\n\n"
                "בחיי היומיום, מומנט מסביר למה למפתח יש ידית ארוכה, למה נדנדה מאוזנת כשמסדרים "
                "משקלים ומרחקים נכון, ולמה ברגע סגור דורש יותר מנוף ולא רק יותר כוח.\n\n"
                "**בפיזיקה ישראלית (תיכון ואוניברסיטה):** מומנט מופיע בדינמיקה סיבובית, "
                "שיווי משקל סטטי (מנוף, קורות, סולמות) ותנע זוויתי. שאלון 1 בבגרות שואל "
                "לעיתים קרובות למצוא מומנט נטו, זרוע מומנט, או תאוצה זוויתית דרך $\\tau = I\\alpha$.\n\n"
                "בסוף השיעור תחשבו גודל וכיוון מומנט, תזהו את זרוע המומנט הנכונה, "
                "תסכמו מומנטים עם מוסכמת סימנים נכונה, ותקשרו מומנט לחוק ניוטון השני לסיבוב."
            ),
        },
        "definition": {
            "en": (
                "**Torque** $\\vec{\\tau}$ measures how strongly a force tends to rotate a body "
                "about a chosen pivot. It is defined as the cross product of the position vector "
                "$\\vec{r}$ (from pivot to point of force application) and the force $\\vec{F}$:\n"
                "$$\\vec{\\tau} = \\vec{r}\\times\\vec{F}$$\n\n"
                "**Magnitude:**\n"
                "$$|\\tau| = rF\\sin\\theta = F\\cdot d_{\\perp}$$\n"
                "where:\n"
                "- $r$ = distance from pivot to point of application\n"
                "- $\\theta$ = angle between $\\vec{r}$ and $\\vec{F}$\n"
                "- $d_{\\perp} = r\\sin\\theta$ = perpendicular distance (moment arm) from pivot "
                "to the **line of action** of the force\n\n"
                "**Units:** N·m (Newton-metres). Same dimensions as energy (Joule), but torque "
                "and energy are different physical quantities.\n\n"
                "**Direction:** Right-hand rule — curl fingers from $\\vec{r}$ toward $\\vec{F}$; "
                "thumb points along $\\vec{\\tau}$. In 2D problems: counterclockwise (CCW) = positive; "
                "clockwise (CW) = negative.\n\n"
                "**Key insight:** Only the component of force perpendicular to $\\vec{r}$ "
                "contributes to torque. A force parallel to the arm produces zero rotation."
            ),
            "he": (
                "**מומנט סיבוב** $\\vec{\\tau}$ מודד עד כמה כוח נוטה לסובב גוף סביב ציר נבחר. "
                "הוא מוגדר כמכפלה וקטורית של וקטור המיקום $\\vec{r}$ (מהציר לנקודת הפעלת הכוח) "
                "והכוח $\\vec{F}$:\n"
                "$$\\vec{\\tau} = \\vec{r}\\times\\vec{F}$$\n\n"
                "**גודל:**\n"
                "$$|\\tau| = rF\\sin\\theta = F\\cdot d_{\\perp}$$\n"
                "כאשר:\n"
                "- $r$ = מרחק מהציר לנקודת הפעלה\n"
                "- $\\theta$ = זווית בין $\\vec{r}$ ל-$\\vec{F}$\n"
                "- $d_{\\perp} = r\\sin\\theta$ = המרחק המאונך (זרוע המומנט) מהציר ל**קו הפעולה** "
                "של הכוח\n\n"
                "**יחידות:** N·m (ניוטון-מטר). אותן ממדים כמו אנרגיה (Joule), אך מומנט "
                "ואנרגיה הם כמויות פיזיקליות שונות.\n\n"
                "**כיוון:** כלל יד ימין — כיפוף אצבעות מ-$\\vec{r}$ ל-$\\vec{F}$; "
                "האגודל מצביע לאורך $\\vec{\\tau}$. בבעיות דו-ממדיות: נגד כיוון השעון = חיובי; "
                "כיוון השעון = שלילי.\n\n"
                "**תובנה מרכזית:** רק הרכיב של הכוח המאונך ל-$\\vec{r}$ תורם למומנט. "
                "כוח מקביל לזרוע לא מייצר סיבוב."
            ),
        },
        "theory": {
            "en": (
                "Torque problems on Bagrut fall into three recurring patterns. Recognizing which "
                "pattern you face saves time and prevents sign errors.\n\n"
                "### Moment arm\n"
                "The moment arm $d_{\\perp}$ is the perpendicular distance from the pivot to the "
                "**line of action** of the force. Extend the force vector in both directions; "
                "measure the perpendicular from the pivot to this line.\n"
                "$$\\tau = F\\cdot d_{\\perp}$$\n\n"
                "### When is torque zero?\n"
                "- Force passes through the pivot ($d_{\\perp} = 0$)\n"
                "- Force is parallel to $\\vec{r}$ ($\\theta = 0°$ or $180°$, so $\\sin\\theta = 0$)\n"
                "- Net torque cancels when opposing torques have equal magnitudes\n\n"
                "### Right-hand rule for direction\n"
                "1. Point fingers of right hand along $\\vec{r}$.\n"
                "2. Curl them toward $\\vec{F}$ (through the smaller angle).\n"
                "3. Thumb points in the direction of $\\vec{\\tau}$.\n\n"
                "Convention in 2D: CCW = positive; CW = negative. Stick to one convention "
                "throughout a problem.\n\n"
                "### Torque and angular acceleration\n"
                "Newton's second law for rotation:\n"
                "$$\\tau_{\\text{net}} = I\\alpha$$\n"
                "where $I$ = moment of inertia, $\\alpha$ = angular acceleration. "
                "This is the direct rotational analogue of $F_{\\text{net}} = ma$."
            ),
            "he": (
                "בעיות מומנט בבגרות נחלקות לשלושה דפוסים חוזרים. זיהוי הדפוס חוסך זמן "
                "ומונע שגיאות סימן.\n\n"
                "### זרוע מומנט\n"
                "זרוע המומנט $d_{\\perp}$ הוא המרחק המאונך מהציר ל**קו הפעולה** של הכוח. "
                "האריכו את וקטור הכוח לשני הכיוונים; מדדו את המאונך מהציר לקו זה.\n"
                "$$\\tau = F\\cdot d_{\\perp}$$\n\n"
                "### מתי מומנט = אפס?\n"
                "- כוח עובר דרך הציר ($d_{\\perp} = 0$)\n"
                "- כוח מקביל ל-$\\vec{r}$ ($\\theta = 0°$ או $180°$, ולכן $\\sin\\theta = 0$)\n"
                "- מומנט נטו מתקזז כשמומנטים מנוגדים שווים בגודל\n\n"
                "### כלל יד ימין לכיוון\n"
                "1. הצביעו אצבעות ימין לאורך $\\vec{r}$.\n"
                "2. כפפו לכיוון $\\vec{F}$ (דרך הזווית הקטנה).\n"
                "3. האגודל מצביע בכיוון $\\vec{\\tau}$.\n\n"
                "מוסכמה במישור: נגד כיוון השעון = חיובי; כיוון השעון = שלילי. "
                "היצמדו למוסכמה אחת לאורך כל הבעיה.\n\n"
                "### קשר לתאוצה זוויתית\n"
                "חוק ניוטון השני לסיבוב:\n"
                "$$\\tau_{\\text{net}} = I\\alpha$$\n"
                "כאשר $I$ = מומנט התמדה, $\\alpha$ = תאוצה זוויתית. "
                "זה האנלוג הסיבובי הישיר של $F_{\\text{net}} = ma$."
            ),
        },
    }

    # Patch section bodies by kind/id
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        sid = sec.get("id", "")

        if kind == "intro":
            sec["body_en_md"] = section_bodies["intro"]["en"]
            sec["body_he_md"] = section_bodies["intro"]["he"]
        elif kind == "definition":
            sec["body_en_md"] = section_bodies["definition"]["en"]
            sec["body_he_md"] = section_bodies["definition"]["he"]
        elif kind == "theory":
            sec["body_en_md"] = section_bodies["theory"]["en"]
            sec["body_he_md"] = section_bodies["theory"]["he"]
        elif kind == "worked_example" and sid == "worked_example_1":
            sec["body_en_md"] = (
                "**Given:** A force $F = 30\\;\\text{N}$ is applied perpendicular to a wrench "
                "handle of length $L = 0.4\\;\\text{m}$ from the bolt (pivot). Find the torque.\n\n"
                "When the force is perpendicular to the handle, $\\theta = 90°$ and "
                "$\\sin 90° = 1$, so the formula simplifies immediately.\n\n"
                "### Move 1 — Identify pivot and moment arm\n"
                "Pivot = bolt centre. The force is applied at the end of the handle, "
                "perpendicular to it, so the moment arm equals the handle length: "
                "$d_{\\perp} = L = 0.4$ m.\n\n"
                "### Move 2 — Apply torque formula\n"
                "$$\\tau = F \\cdot L \\cdot \\sin 90° = 30 \\times 0.4 \\times 1 = 12\\;\\text{N·m}$$\n\n"
                "### Move 3 — Direction\n"
                "By the right-hand rule, pushing down on a horizontal wrench handle produces "
                "CCW torque about the bolt — positive in the standard 2D convention.\n\n"
                "**Answer:** $\\tau = 12$ N·m (CCW).\n\n"
                "**Physical reading:** Doubling the handle length would double the torque "
                "without increasing force — exactly why mechanics use long wrenches on tight bolts."
            )
            sec["body_he_md"] = (
                "**נתון:** כוח $F = 30\\;\\text{N}$ מופעל מאונך לידית מפתח באורך $L = 0.4\\;\\text{m}$ "
                "מהברג (ציר). מצאו מומנט.\n\n"
                "כשהכוח מאונך לידית, $\\theta = 90°$ ו-$\\sin 90° = 1$, והנוסחה מתפשטת מיד.\n\n"
                "### צעד 1 — זיהוי ציר וזרוע מומנט\n"
                "ציר = מרכז הברג. הכוח מופעל בקצה הידית, מאונך לה, ולכן זרוע המומנט "
                "שווה לאורך הידית: $d_{\\perp} = L = 0.4$ m.\n\n"
                "### צעד 2 — יישום נוסחת מומנט\n"
                "$$\\tau = F \\cdot L \\cdot \\sin 90° = 30 \\times 0.4 \\times 1 = 12\\;\\text{N·m}$$\n\n"
                "### צעד 3 — כיוון\n"
                "לפי כלל יד ימין, דחיפה כלפי מטה על ידית אופקית מייצרת מומנט נגד כיוון "
                "השעון סביב הברג — חיובי במוסכמה דו-ממדית סטנדרטית.\n\n"
                "**תשובה:** $\\tau = 12$ N·m (נגד השעון).\n\n"
                "**קריאה פיזיקלית:** הכפלת אורך הידית תכפיל את המומנט בלי להגדיל כוח — "
                "בדיוק למה מכונאים משתמשים במפתחות ארוכים על ברגים סגורים מאוד."
            )
        elif kind == "worked_example" and sid == "worked_example_2":
            sec["body_en_md"] = (
                "**Given:** A rod of length $L = 2\\;\\text{m}$ is pivoted at its center. "
                "Three forces act on it:\n"
                "- $F_1 = 20\\;\\text{N}$ upward at left end (tends CCW)\n"
                "- $F_2 = 30\\;\\text{N}$ downward at $0.5\\;\\text{m}$ right of center (tends CW)\n"
                "- $F_3 = 10\\;\\text{N}$ upward at right end (tends CCW)\n\n"
                "Each force is perpendicular to the rod, so $\\tau = rF$ with sign from direction.\n\n"
                "### Move 1 — Torque from $F_1$\n"
                "Distance from center to left end = $1$ m. Upward force on left side → CCW → positive.\n"
                "$$\\tau_1 = +20 \\times 1 = +20\\;\\text{N·m}$$\n\n"
                "### Move 2 — Torque from $F_2$\n"
                "Downward force on right side → CW → negative.\n"
                "$$\\tau_2 = -30 \\times 0.5 = -15\\;\\text{N·m}$$\n\n"
                "### Move 3 — Torque from $F_3$\n"
                "$$\\tau_3 = +10 \\times 1 = +10\\;\\text{N·m}$$\n\n"
                "### Move 4 — Net torque\n"
                "$$\\tau_{\\text{net}} = +20 - 15 + 10 = +15\\;\\text{N·m}$$ (counterclockwise)\n\n"
                "**Answer:** Net torque $= +15$ N·m, tending to rotate CCW.\n\n"
                "**Exam tip:** Mark each force with its distance from the pivot and sign "
                "before adding. Mixing magnitudes without signs is the most common error."
            )
            sec["body_he_md"] = (
                "**נתון:** מוט באורך $L = 2\\;\\text{m}$ עם ציר במרכז. שלושה כוחות פועלים:\n"
                "- $F_1 = 20\\;\\text{N}$ מעלה בקצה שמאל (נוטה נגד השעון)\n"
                "- $F_2 = 30\\;\\text{N}$ מטה ב-$0.5\\;\\text{m}$ מימין למרכז (נוטה כיוון השעון)\n"
                "- $F_3 = 10\\;\\text{N}$ מעלה בקצה ימין (נוטה נגד השעון)\n\n"
                "כל כוח מאונך למוט, ולכן $\\tau = rF$ עם סימן לפי כיוון.\n\n"
                "### צעד 1 — מומנט מ-$F_1$\n"
                "מרחק ממרכז לקצה שמאל = $1$ m. כוח מעלה בצד שמאל → נגד השעון → חיובי.\n"
                "$$\\tau_1 = +20 \\times 1 = +20\\;\\text{N·m}$$\n\n"
                "### צעד 2 — מומנט מ-$F_2$\n"
                "כוח מטה בצד ימין → כיוון השעון → שלילי.\n"
                "$$\\tau_2 = -30 \\times 0.5 = -15\\;\\text{N·m}$$\n\n"
                "### צעד 3 — מומנט מ-$F_3$\n"
                "$$\\tau_3 = +10 \\times 1 = +10\\;\\text{N·m}$$\n\n"
                "### צעד 4 — מומנט נטו\n"
                "$$\\tau_{\\text{net}} = +20 - 15 + 10 = +15\\;\\text{N·m}$$ (נגד כיוון השעון)\n\n"
                "**תשובה:** מומנט נטו $= +15$ N·m, נוטה לסיבוב נגד כיוון השעון.\n\n"
                "**טיפ לבחינה:** סמנו כל כוח עם מרחקו מהציר וסימנו לפני חיבור. "
                "ערבוב גדלים ללא סימנים היא הטעות הנפוצה ביותר."
            )
        elif kind == "worked_example" and sid == "worked_example_3":
            sec["body_en_md"] = (
                "**Given:** A force $\\vec{F} = (4\\hat{x} + 3\\hat{y})\\;\\text{N}$ is applied at "
                "position $\\vec{r} = (2\\hat{x} + 5\\hat{y})\\;\\text{m}$ from the pivot (origin).\n\n"
                "In 3D, torque is computed directly as a cross product. "
                "Both vectors lie in the $xy$-plane, so $\\vec{\\tau}$ points along $\\hat{z}$.\n\n"
                "### Move 1 — Set up cross product\n"
                "$$\\vec{\\tau} = \\vec{r}\\times\\vec{F} = (2\\hat{x} + 5\\hat{y})\\times(4\\hat{x} + 3\\hat{y})$$\n\n"
                "### Move 2 — Expand using unit vector rules\n"
                "Using $\\hat{x}\\times\\hat{x} = 0$, $\\hat{y}\\times\\hat{y} = 0$, "
                "$\\hat{x}\\times\\hat{y} = \\hat{z}$, $\\hat{y}\\times\\hat{x} = -\\hat{z}$:\n"
                "$$\\vec{\\tau} = 2(3)(\\hat{x}\\times\\hat{y}) + 5(4)(\\hat{y}\\times\\hat{x}) "
                "= 6\\hat{z} - 20\\hat{z} = -14\\hat{z}\\;\\text{N·m}$$\n\n"
                "### Move 3 — 2D shortcut check\n"
                "$\\tau_z = x_1 y_2 - y_1 x_2 = (2)(3) - (5)(4) = 6 - 20 = -14$ N·m ✓\n\n"
                "**Answer:** $|\\tau| = 14$ N·m, clockwise (negative $z$).\n\n"
                "**University note:** The 2D formula $\\tau_z = x_1 y_2 - y_1 x_2$ is faster "
                "when all vectors lie in a plane. Always verify the sign with the right-hand rule.\n\n"
                "**Physical reading:** The force has both $x$ and $y$ components, but only the "
                "perpendicular combination relative to $\\vec{r}$ produces rotation. The negative "
                "$z$-component confirms clockwise rotation about the origin."
            )
            sec["body_he_md"] = (
                "**נתון:** כוח $\\vec{F} = (4\\hat{x} + 3\\hat{y})\\;\\text{N}$ מופעל במיקום "
                "$\\vec{r} = (2\\hat{x} + 5\\hat{y})\\;\\text{m}$ מהציר (ראשית).\n\n"
                "בתלת-ממד, מומנט מחושב ישירות כמכפלה וקטורית. "
                "שני הווקטורים במישור $xy$, ולכן $\\vec{\\tau}$ מצביע לאורך $\\hat{z}$.\n\n"
                "### צעד 1 — הגדרת מכפלה וקטורית\n"
                "$$\\vec{\\tau} = \\vec{r}\\times\\vec{F} = (2\\hat{x} + 5\\hat{y})\\times(4\\hat{x} + 3\\hat{y})$$\n\n"
                "### צעד 2 — פירוק לפי כללי וקטורי יחידה\n"
                "באמצעות $\\hat{x}\\times\\hat{x} = 0$, $\\hat{y}\\times\\hat{y} = 0$, "
                "$\\hat{x}\\times\\hat{y} = \\hat{z}$, $\\hat{y}\\times\\hat{x} = -\\hat{z}$:\n"
                "$$\\vec{\\tau} = 2(3)(\\hat{x}\\times\\hat{y}) + 5(4)(\\hat{y}\\times\\hat{x}) "
                "= 6\\hat{z} - 20\\hat{z} = -14\\hat{z}\\;\\text{N·m}$$\n\n"
                "### צעד 3 — בדיקה בקיצור דו-ממדי\n"
                "$\\tau_z = x_1 y_2 - y_1 x_2 = (2)(3) - (5)(4) = 6 - 20 = -14$ N·m ✓\n\n"
                "**תשובה:** $|\\tau| = 14$ N·m, כיוון השעון (שלילי $z$).\n\n"
                "**הערת אוניברסיטה:** הנוסחה $\\tau_z = x_1 y_2 - y_1 x_2$ מהירה יותר "
                "כשכל הווקטורים במישור. תמיד אמתו את הסימן עם כלל יד ימין.\n\n"
                "**קריאה פיזיקלית:** לכוח יש רכיבי $x$ ו-$y$, אך רק השילוב המאונך "
                "ביחס ל-$\\vec{r}$ מייצר סיבוב. הרכיב השלילי ב-$z$ מאשר סיבוב בכיוון השעון סביב הראשית."
            )
        elif kind == "checkpoint" and sid == "checkpoint_1":
            sec["checkpoint_solution_en"] = (
                "A $50$ N force at $60°$ to a $0.5$ m bar from the pivot. Find torque.\n\n"
                "**Step 1 — Identify formula:** $\\tau = rF\\sin\\theta$ with $r = 0.5$ m, "
                "$F = 50$ N, $\\theta = 60°$.\n\n"
                "**Step 2 — Substitute:**\n"
                "$$\\tau = 0.5 \\times 50 \\times \\sin 60° = 25 \\times \\frac{\\sqrt{3}}{2} "
                "\\approx 21.65\\;\\text{N·m}$$\n\n"
                "**Check:** Only the perpendicular component $F\\sin 60° \\approx 43.3$ N "
                "contributes. Then $\\tau = 0.5 \\times 43.3 \\approx 21.65$ N·m ✓."
            )
            sec["checkpoint_solution_he"] = (
                "כוח $50$ N בזווית $60°$ לחלק $0.5$ m מהציר. מצאו מומנט.\n\n"
                "**שלב 1 — זיהוי נוסחה:** $\\tau = rF\\sin\\theta$ עם $r = 0.5$ m, "
                "$F = 50$ N, $\\theta = 60°$.\n\n"
                "**שלב 2 — הצבה:**\n"
                "$$\\tau = 0.5 \\times 50 \\times \\sin 60° = 25 \\times \\frac{\\sqrt{3}}{2} "
                "\\approx 21.65\\;\\text{N·m}$$\n\n"
                "**בדיקה:** רק הרכיב המאונך $F\\sin 60° \\approx 43.3$ N תורם. "
                "אז $\\tau = 0.5 \\times 43.3 \\approx 21.65$ N·m ✓."
            )
        elif kind == "checkpoint" and sid == "checkpoint_2":
            sec["checkpoint_solution_en"] = (
                "Disk with $I = 0.5$ kg·m² and net torque $\\tau = 4$ N·m. Find $\\alpha$.\n\n"
                "**Step 1 — Apply Newton's 2nd for rotation:**\n"
                "$$\\alpha = \\frac{\\tau_{\\text{net}}}{I}$$\n\n"
                "**Step 2 — Substitute:**\n"
                "$$\\alpha = \\frac{4}{0.5} = 8\\;\\text{rad/s}^2$$\n\n"
                "**Check:** Units: N·m / (kg·m²) = rad/s² ✓. "
                "A small moment of inertia means the same torque produces large angular acceleration."
            )
            sec["checkpoint_solution_he"] = (
                "דיסק עם $I = 0.5$ kg·m² ומומנט נטו $\\tau = 4$ N·m. מצאו $\\alpha$.\n\n"
                "**שלב 1 — יישום חוק ניוטון השני לסיבוב:**\n"
                "$$\\alpha = \\frac{\\tau_{\\text{net}}}{I}$$\n\n"
                "**שלב 2 — הצבה:**\n"
                "$$\\alpha = \\frac{4}{0.5} = 8\\;\\text{rad/s}^2$$\n\n"
                "**בדיקה:** יחידות: N·m / (kg·m²) = rad/s² ✓. "
                "מומנט התמדה קטן פירושו שאותו מומנט מייצר תאוצה זוויתית גדולה."
            )
        elif kind == "method_guide":
            sec["body_en_md"] = (
                "| Situation | Formula | Notes |\n"
                "|---|---|---|\n"
                "| Force perpendicular to $\\vec{r}$ | $\\tau = rF$ | $\\sin 90° = 1$ |\n"
                "| Force at angle $\\theta$ to $\\vec{r}$ | $\\tau = rF\\sin\\theta$ | $\\theta$ between $\\vec{r}$ and $\\vec{F}$ |\n"
                "| Using moment arm | $\\tau = Fd_{\\perp}$ | $d_{\\perp}$ = ⊥ distance to line of action |\n"
                "| 2D cross product | $\\tau_z = x_1 y_2 - y_1 x_2$ | Vectors in $xy$-plane |\n"
                "| Direction (2D) | CCW = positive, CW = negative | Stay consistent |\n"
                "| Newton's 2nd (rotation) | $\\tau_{\\text{net}} = I\\alpha$ | Rotational analogue of $F = ma$ |\n\n"
                "**Decision tree:**\n"
                "1. Is the force perpendicular to the arm? → Use $\\tau = rF$.\n"
                "2. Is an angle given? → Use $\\tau = rF\\sin\\theta$.\n"
                "3. Can you draw the line of action? → Find $d_{\\perp}$, then $\\tau = Fd_{\\perp}$.\n"
                "4. Multiple forces? → Compute each $\\tau_i$ with sign, then sum.\n\n"
                "**Key:** $d_{\\perp}$ is the perpendicular distance from pivot to the **line of action**, "
                "NOT necessarily to the point where the force is applied."
            )
            sec["body_he_md"] = (
                "| מצב | נוסחה | הערות |\n"
                "|---|---|---|\n"
                "| כוח מאונך ל-$\\vec{r}$ | $\\tau = rF$ | $\\sin 90° = 1$ |\n"
                "| כוח בזווית $\\theta$ ל-$\\vec{r}$ | $\\tau = rF\\sin\\theta$ | $\\theta$ בין $\\vec{r}$ ל-$\\vec{F}$ |\n"
                "| שימוש בזרוע מומנט | $\\tau = Fd_{\\perp}$ | $d_{\\perp}$ = מרחק מאונך לקו הפעולה |\n"
                "| מכפלה וקטורית 2D | $\\tau_z = x_1 y_2 - y_1 x_2$ | וקטורים במישור $xy$ |\n"
                "| כיוון (2D) | CCW = חיובי, CW = שלילי | הישארו עקביים |\n"
                "| חוק ניוטון (סיבוב) | $\\tau_{\\text{net}} = I\\alpha$ | אנלוג סיבובי ל-$F = ma$ |\n\n"
                "**עץ החלטות:**\n"
                "1. הכוח מאונך לזרוע? → $\\tau = rF$.\n"
                "2. ניתנה זווית? → $\\tau = rF\\sin\\theta$.\n"
                "3. אפשר לשרטט קו פעולה? → מצאו $d_{\\perp}$, ואז $\\tau = Fd_{\\perp}$.\n"
                "4. כוחות מרובים? → חשבו כל $\\tau_i$ עם סימן, ואז סכמו.\n\n"
                "**מפתח:** $d_{\\perp}$ הוא המרחק המאונך מהציר ל**קו הפעולה**, "
                "לא בהכרח לנקודת הפעלת הכוח."
            )
        elif kind == "pitfall":
            sec["body_en_md"] = (
                "1. **Torque ≠ force × distance (always).** The formula is $\\tau = rF\\sin\\theta$. "
                "If the force is not perpendicular to the arm, you must include $\\sin\\theta$. "
                "Using $\\tau = rF$ when $\\theta \\neq 90°$ overestimates torque.\n\n"
                "2. **Moment arm ≠ distance to point of application.** The moment arm is the "
                "perpendicular distance from the pivot to the **line of action** — extend the "
                "force vector and measure the perpendicular from the pivot to that line.\n\n"
                "3. **Direction sign errors.** Establish a convention (CCW positive) and apply "
                "it consistently to every force. Mixing signs mid-problem gives wrong net torque.\n\n"
                "4. **Units confusion.** Torque is in N·m — same units as energy (Joule), but they "
                "are different quantities. Never write torque in Joules.\n\n"
                "5. **Forgetting that force through pivot gives zero torque.** No matter how large "
                "the force, if its line of action passes through the pivot, $d_{\\perp} = 0$."
            )
            sec["body_he_md"] = (
                "1. **מומנט ≠ כוח × מרחק (תמיד).** הנוסחה היא $\\tau = rF\\sin\\theta$. "
                "אם הכוח לא מאונך לזרוע, חייבים לכלול $\\sin\\theta$. "
                "שימוש ב-$\\tau = rF$ כש-$\\theta \\neq 90°$ מגדיל את המומנט בטעות.\n\n"
                "2. **זרוע מומנט ≠ מרחק לנקודת הפעלה.** זרוע המומנט הוא המרחק המאונך "
                "מהציר ל**קו הפעולה** — האריכו את וקטור הכוח ומדדו מאונך מהציר לקו זה.\n\n"
                "3. **שגיאות סימן בכיוון.** הגדירו מוסכמה (CCW חיובי) ויישמו אותה עקבית "
                "לכל כוח. ערבוב סימנים באמצע הבעיה נותן מומנט נטו שגוי.\n\n"
                "4. **בלבול יחידות.** מומנט ב-N·m — אותן יחידות כמו אנרגיה (Joule), "
                "אך אלו כמויות שונות. לעולם אל תכתבו מומנט ב-Joules.\n\n"
                "5. **שכחה שכוח דרך הציר נותן מומנט אפס.** לא משנה כמה גדול הכוח — "
                "אם קו הפעולה עובר דרך הציר, $d_{\\perp} = 0$."
            )
        elif kind == "why_matters":
            sec["body_en_md"] = (
                "Torque is the bridge between forces you already know and everything rotational — "
                "wheels, gears, seesaws, and spinning objects.\n\n"
                "**Builds on:**\n"
                "- `concept:newton_laws` **Newton's Laws** — force causes linear acceleration; "
                "torque causes angular acceleration.\n"
                "- `concept:rotational_kinematics` **Rotational Kinematics** — angular velocity "
                "and acceleration connect to torque via $\\tau = I\\alpha$.\n\n"
                "**Leads to:**\n"
                "- `concept:rotational_dynamics` **Rotational Dynamics & Angular Momentum**\n"
                "- `concept:static_equilibrium` **Static Equilibrium** — $\\sum F = 0$ and "
                "$\\sum \\tau = 0$ together.\n\n"
                "**Why it matters for exams:** Bagrut statics problems combine force balance "
                "with torque balance. University mechanics extends to 3D cross products and "
                "rigid-body rotation."
            )
            sec["body_he_md"] = (
                "מומנט הוא הגשר בין כוחות שכבר מכירים לבין כל מה שסיבובי — גלגלים, "
                "גלגלי שיניים, נדנדות וגופים מסתובבים.\n\n"
                "**מבוסס על:**\n"
                "- `concept:newton_laws` **חוקי ניוטון** — כוח גורם לתאוצה לינארית; "
                "מומנט גורם לתאוצה זוויתית.\n"
                "- `concept:rotational_kinematics` **קינמטיקה סיבובית** — מהירות ותאוצה "
                "זוויתיות מתקשרות למומנט דרך $\\tau = I\\alpha$.\n\n"
                "**מוביל ל:**\n"
                "- `concept:rotational_dynamics` **דינמיקה סיבובית ותנע זוויתי**\n"
                "- `concept:static_equilibrium` **שיווי משקל סטטי** — $\\sum F = 0$ ו-"
                "$\\sum \\tau = 0$ יחד.\n\n"
                "**למה זה חשוב לבחינות:** בעיות סטטיקה בבגרות משלבות איזון כוחות "
                "עם איזון מומנטים. מכניקה באוניברסיטה מרחיבה למכפלות וקטוריות תלת-ממד "
                "וסיבוב גוף קשיח."
            )
        elif kind == "before_exam":
            sec["body_en_md"] = (
                "- **Definition:** $\\vec{\\tau} = \\vec{r}\\times\\vec{F}$\n"
                "- **Magnitude:** $\\tau = rF\\sin\\theta = Fd_{\\perp}$\n"
                "- **Units:** N·m (not Joules!)\n"
                "- **Direction:** right-hand rule; CCW = positive (2D)\n"
                "- **Zero torque:** force through pivot, or parallel to $\\vec{r}$\n"
                "- **Newton for rotation:** $\\tau_{\\text{net}} = I\\alpha$\n"
                "- **2D cross product:** $\\tau_z = x F_y - y F_x$\n"
                "- **Net torque:** sum each $\\tau_i$ with correct sign\n\n"
                "**Last review:** Draw a wrench or door diagram, label pivot, force, and "
                "moment arm. Say each formula out loud once, then solve one checkpoint "
                "without looking at notes.\n\n"
                "**Quick self-test:** Can you explain why pushing at the hinge produces "
                "almost no rotation? That single sentence proves you understand the moment arm."
            )
            sec["body_he_md"] = (
                "- **הגדרה:** $\\vec{\\tau} = \\vec{r}\\times\\vec{F}$\n"
                "- **גודל:** $\\tau = rF\\sin\\theta = Fd_{\\perp}$\n"
                "- **יחידות:** N·m (לא Joules!)\n"
                "- **כיוון:** כלל יד ימין; CCW = חיובי (2D)\n"
                "- **מומנט אפס:** כוח דרך הציר, או מקביל ל-$\\vec{r}$\n"
                "- **ניוטון לסיבוב:** $\\tau_{\\text{net}} = I\\alpha$\n"
                "- **מכפלה וקטורית 2D:** $\\tau_z = xF_y - yF_x$\n"
                "- **מומנט נטו:** סכמו כל $\\tau_i$ עם סימן נכון\n\n"
                "**חזרה אחרונה:** שרטטו מפתח או דלת, סמנו ציר, כוח וזרוע מומנט. "
                "אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint אחד בלי להסתכל בפתקים.\n\n"
                "**בדיקה עצמית מהירה:** האם אתם יכולים להסביר למה דחיפה ליד הציר "
                "כמעט לא מסובבת? משפט אחד כזה מוכיח שאתם מבינים את זרוע המומנט."
            )
        elif kind == "summary":
            sec["body_en_md"] = (
                "- **Torque:** $\\vec{\\tau} = \\vec{r}\\times\\vec{F}$; magnitude $= rF\\sin\\theta = Fd_{\\perp}$\n"
                "- **Moment arm** $d_{\\perp}$ = perpendicular distance from pivot to line of action\n"
                "- **Units:** N·m; direction by right-hand rule (CCW positive in 2D)\n"
                "- **Zero torque:** force through pivot, or force parallel to $\\vec{r}$\n"
                "- **Newton's 2nd (rotation):** $\\tau_{\\text{net}} = I\\alpha$\n"
                "- **Multiple forces:** compute each torque with sign, then sum\n\n"
                "**Takeaway:** Identify the pivot first, find each moment arm, apply the correct "
                "sign convention, and check units before submitting your answer."
            )
            sec["body_he_md"] = (
                "- **מומנט:** $\\vec{\\tau} = \\vec{r}\\times\\vec{F}$; גודל $= rF\\sin\\theta = Fd_{\\perp}$\n"
                "- **זרוע מומנט** $d_{\\perp}$ = מרחק מאונך מהציר לקו הפעולה\n"
                "- **יחידות:** N·m; כיוון לפי כלל יד ימין (CCW חיובי ב-2D)\n"
                "- **מומנט אפס:** כוח דרך הציר, או כוח מקביל ל-$\\vec{r}$\n"
                "- **ניוטון לסיבוב:** $\\tau_{\\text{net}} = I\\alpha$\n"
                "- **כוחות מרובים:** חשבו כל מומנט עם סימן, ואז סכמו\n\n"
                "**מסקנה:** זהו קודם את הציר, מצאו כל זרוע מומנט, יישמו מוסכמת סימנים נכונה, "
                "ובדקו יחידות לפני הגשת התשובה."
            )

    # Patch question explanations
    for q in lesson["questions"]:
        ord_n = q.get("ord")
        if ord_n in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_n]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_n]["he"]

    # Fix q6 acceptable_answers typo ("2" -> "5")
    for q in lesson["questions"]:
        if q.get("ord") == 6:
            aa = q["answer_payload"]["acceptable_answers"]
            if "2" in aa:
                aa[aa.index("2")] = "5"

    return lesson


def validate(lesson):
    errors = []
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                errors.append(f"{sec.get('id', kind)} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                errors.append(f"{sec.get('id', kind)} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                errors.append(f"{sec.get('id', kind)} HE weak/English paste")
        if kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS["worked_example"]["en"]:
                errors.append(f"{sec.get('id')} EN: {en_w} < 130")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                errors.append(f"{sec.get('id')} HE: {he_w} < 110")

    for q in lesson["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"q{q.get('ord')} expl_{lang}: {w} words (need 80-150)")

    return errors


def main():
    lesson = build_lesson()
    errors = validate(lesson)
    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(f"  - {e}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT}")
    print(f"Validation: {len(errors)} issues")


if __name__ == "__main__":
    main()
