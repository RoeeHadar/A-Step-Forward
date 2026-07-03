#!/usr/bin/env python3
"""Expand trigonometry_makhina.json to MIN_WORDS + 80-150 word explanations."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSON = ROOT / "scripts/seed_data/lessons/trigonometry_makhina.json"

PATCHES = {
    "intro": {
        "body_en_md": (
            "Trigonometry is not just about triangles. It is the mathematics of **periodic phenomena** — "
            "waves, oscillations, rotations — which appear in every branch of physics and engineering.\n\n"
            "At university, you will meet trig on day one of calculus (limits of $\\sin x / x$, derivatives "
            "of $\\sin$ and $\\cos$) and again in every physics course that models motion or fields. "
            "Students who treat trig as \"high-school review\" often stall when integrals require "
            "$\\sin^2 x$ identities or when a force must be resolved into components.\n\n"
            "**Where you'll use trig at university:**\n"
            "- **Calculus:** derivatives of $\\sin$ and $\\cos$, trig substitutions in integrals, "
            "Taylor series for sine and cosine.\n"
            "- **Physics:** simple harmonic motion, wave equations, Doppler effect, component decomposition.\n"
            "- **Electrical engineering:** AC circuits (phasors, impedance, phase shift).\n"
            "- **Mechanics:** resolving forces, projectile motion, circular motion.\n\n"
            "**What this lesson adds over high school:**\n"
            "- Rigorous unit-circle definitions in **all four quadrants** (not just acute angles).\n"
            "- All six functions: $\\sin, \\cos, \\tan, \\cot, \\sec, \\csc$ with correct domains.\n"
            "- Full identity toolkit: Pythagorean, angle-addition, double-angle.\n"
            "- Solving general trig equations — **all** solutions in an interval, not just one.\n"
            "- Inverse trig functions and their restricted domains.\n\n"
            "This lesson is designed for **מכינה** (pre-university) students bridging 3/5-unit Bagrut "
            "to the fluency expected in first-year math and physics."
        ),
        "body_he_md": (
            "טריגונומטריה אינה רק עניין של משולשים. היא מתמטיקת **תופעות מחזוריות** — גלים, תנודות, "
            "סיבובים — שמופיעות בכל ענף פיזיקה והנדסה.\n\n"
            "באוניברסיטה תפגשו טריגונומטריה כבר ביום הראשון של חשבון (גבולות $\\sin x / x$, נגזרות "
            "של $\\sin$ ו-$\\cos$) ושוב בכל קורס פיזיקה שמדגם תנועה או שדות. סטודנטים שמתייחסים לטריגונומטריה "
            "כ\"חזרה מתיכון\" לעיתים נתקעים כשאינטגרלים דורשים זהויות $\\sin^2 x$ או כשצריך לפרק כוח לרכיבים.\n\n"
            "**היכן תשתמשו בטריגונומטריה באוניברסיטה:**\n"
            "- **חשבון:** נגזרות $\\sin$ ו-$\\cos$, הצבות טריגונומטריות באינטגרלים, טורי טיילור.\n"
            "- **פיזיקה:** תנועה הרמונית פשוטה, משוואות גל, אפקט דoppler, פירוק לרכיבים.\n"
            "- **הנדסת חשמל:** מעגלי AC (פאזורים, עכבה, הזזת פאזה).\n"
            "- **מכניקה:** פירוק כוחות, זריקה אלכסונית, תנועה מעגלית.\n\n"
            "**מה השיעור הזה מוסיף על פני התיכון:**\n"
            "- הגדרות קפדניות על-ידי מעגל יחידה ב**כל ארבעת הרבעים** (לא רק זוויות חדות).\n"
            "- שש פונקציות: $\\sin, \\cos, \\tan, \\cot, \\sec, \\csc$ עם תחומים נכונים.\n"
            "- ארגז זהויות מלא: פיתגורס, חיבור זוויות, זווית כפולה.\n"
            "- פתרון משוואות טריגונומטריות כלליות — **כל** הפתרונות בקטע, לא רק אחד.\n"
            "- פונקציות הפוכות ותחומיהן המוגבלים.\n\n"
            "שיעור זה מיועד לתלמידי **מכינה** שגשר בין בגרות 3/5 יחידות לרמת שליטה "
            "הנדרשת בשנה א' במתמטיקה ובפיזיקה."
        ),
    },
    "definition": {
        "body_he_md": (
            "### הגדרת מעגל יחידה\n"
            "עבור נקודה $(x,y)$ על מעגל יחידה (רדיוס 1) בזווית $\\theta$ מציר $x$ החיובי:\n"
            "$$\\cos\\theta=x, \\quad \\sin\\theta=y.$$\n"
            "כל נקודה על המעגל נקבעת על-ידי זווית $\\theta$; הסיבוב נגד כיוון השעון מגדיל את $\\theta$.\n\n"
            "### שש הפונקציות\n"
            "| פונקציה | הגדרה | תחום |\n"
            "|---|---|---|\n"
            "| $\\sin\\theta$ | קואורדינטת $y$ | כל $\\mathbb{R}$ |\n"
            "| $\\cos\\theta$ | קואורדינטת $x$ | כל $\\mathbb{R}$ |\n"
            "| $\\tan\\theta$ | $\\sin\\theta/\\cos\\theta$ | $\\theta\\neq\\pi/2+n\\pi$ |\n"
            "| $\\cot\\theta$ | $\\cos\\theta/\\sin\\theta$ | $\\theta\\neq n\\pi$ |\n"
            "| $\\sec\\theta$ | $1/\\cos\\theta$ | $\\theta\\neq\\pi/2+n\\pi$ |\n"
            "| $\\csc\\theta$ | $1/\\sin\\theta$ | $\\theta\\neq n\\pi$ |\n\n"
            "### ערכים מיוחדים — שווים לזכור בעל-פה\n"
            "| $\\theta$ | 0 | $\\pi/6$ | $\\pi/4$ | $\\pi/3$ | $\\pi/2$ |\n"
            "|---|---|---|---|---|---|\n"
            "| $\\sin$ | 0 | $1/2$ | $\\sqrt{2}/2$ | $\\sqrt{3}/2$ | 1 |\n"
            "| $\\cos$ | 1 | $\\sqrt{3}/2$ | $\\sqrt{2}/2$ | $1/2$ | 0 |\n"
            "| $\\tan$ | 0 | $1/\\sqrt{3}$ | 1 | $\\sqrt{3}$ | לא מוגדר |\n\n"
            "במכינה ובאוניברסיטה מצפים שתזכרו את הערכים האלה **ברדיאנים** — "
            "לא רק במעלות. זווית $\\pi/6$ היא $30°$, $\\pi/4$ היא $45°$, $\\pi/3$ היא $60°$.\n\n"
            "### זהויות יסודיות (פיתגוריות)\n"
            "$$\\sin^2\\theta+\\cos^2\\theta=1, \\quad 1+\\tan^2\\theta=\\sec^2\\theta, \\quad 1+\\cot^2\\theta=\\csc^2\\theta.$$\n"
            "מזהות פיתגורס הראשונה נגזרת ישירות מ-$x^2+y^2=1$ על מעגל היחידה. "
            "שתי האחרות מתקבלות בחלוקה ב-$\\cos^2\\theta$ או $\\sin^2\\theta$."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Angle-addition formulas\n"
            "$$\\sin(A+B) = \\sin A\\cos B + \\cos A\\sin B$$\n"
            "$$\\cos(A+B) = \\cos A\\cos B - \\sin A\\sin B$$\n"
            "$$\\tan(A+B) = \\frac{\\tan A + \\tan B}{1 - \\tan A\\tan B}$$\n"
            "These three identities are the workhorses of university trig. "
            "Setting $B = -B$ gives subtraction formulas; setting $A = B$ gives double-angle.\n\n"
            "### Double-angle formulas\n"
            "$$\\sin(2A) = 2\\sin A\\cos A$$\n"
            "$$\\cos(2A) = \\cos^2 A - \\sin^2 A = 1 - 2\\sin^2 A = 2\\cos^2 A - 1$$\n"
            "$$\\tan(2A) = \\frac{2\\tan A}{1 - \\tan^2 A}$$\n"
            "Choose the $\\cos(2A)$ form that matches what you need to eliminate — "
            "sine-only for integrals, cosine-only for force resolution.\n\n"
            "### General solution of $\\sin\\theta = c$\n"
            "If $|c| \\leq 1$ and $\\alpha = \\arcsin(c) \\in [-\\pi/2, \\pi/2]$:\n"
            "$$\\theta = \\alpha + 2k\\pi \\quad \\text{or} \\quad \\theta = (\\pi - \\alpha) + 2k\\pi, \\quad k \\in \\mathbb{Z}.$$\n"
            "The two families come from the two intersection points of the horizontal line $y = c$ with the unit circle.\n\n"
            "### General solution of $\\cos\\theta = c$\n"
            "If $|c| \\leq 1$ and $\\alpha = \\arccos(c) \\in [0,\\pi]$:\n"
            "$$\\theta = \\pm\\alpha + 2k\\pi, \\quad k \\in \\mathbb{Z}.$$\n"
            "Cosine is even, so $\\cos\\theta = \\cos(-\\theta)$ captures both mirror points.\n\n"
            "### General solution of $\\tan\\theta = c$\n"
            "$$\\theta = \\arctan(c) + k\\pi, \\quad k \\in \\mathbb{Z}.$$\n"
            "Tangent repeats every $\\pi$ (not $2\\pi$), so only one family of solutions.\n\n"
            "### Signs in each quadrant (ASTC rule)\n"
            "- **Q1** ($0$ to $\\pi/2$): All positive.\n"
            "- **Q2** ($\\pi/2$ to $\\pi$): $\\sin$ positive only.\n"
            "- **Q3** ($\\pi$ to $3\\pi/2$): $\\tan$ positive only.\n"
            "- **Q4** ($3\\pi/2$ to $2\\pi$): $\\cos$ positive only.\n\n"
            "**Exam strategy:** always draw the unit circle or apply ASTC before writing final angles. "
            "The calculator gives only one reference angle — you must find the mirror angle yourself."
        ),
        "body_he_md": (
            "### זהויות חיבור זוויות\n"
            "$$\\sin(A+B)=\\sin A\\cos B+\\cos A\\sin B$$\n"
            "$$\\cos(A+B)=\\cos A\\cos B-\\sin A\\sin B$$\n"
            "$$\\tan(A+B)=\\frac{\\tan A+\\tan B}{1-\\tan A\\tan B}$$\n"
            "שלוש הזהויות האלה הן כלי העבודה המרכזיים בטריגונומטריה אוניברסיטאית. "
            "הצבת $B=-B$ נותנת נוסחאות חיסור; הצבת $A=B$ נותנת זווית כפולה.\n\n"
            "### זהויות זווית כפולה\n"
            "$$\\sin(2A)=2\\sin A\\cos A$$\n"
            "$$\\cos(2A)=\\cos^2 A-\\sin^2 A=1-2\\sin^2 A=2\\cos^2 A-1$$\n"
            "$$\\tan(2A)=\\frac{2\\tan A}{1-\\tan^2 A}$$\n"
            "בחרו את צורת $\\cos(2A)$ שמתאימה למה שצריך לבטל — "
            "רק $\\sin$ לאינטגרלים, רק $\\cos$ לפירוק כוחות.\n\n"
            "### פתרון כללי של $\\sin\\theta=c$\n"
            "אם $|c|\\leq 1$ ו-$\\alpha=\\arcsin(c)\\in[-\\pi/2,\\pi/2]$:\n"
            "$$\\theta=\\alpha+2k\\pi \\quad \\text{או} \\quad \\theta=(\\pi-\\alpha)+2k\\pi, \\quad k\\in\\mathbb{Z}.$$\n"
            "שתי המשפחות נובעות משני נקודות החיתוך של קו אופקי $y=c$ עם מעגל היחידה.\n\n"
            "### פתרון כללי של $\\cos\\theta=c$\n"
            "אם $|c|\\leq 1$ ו-$\\alpha=\\arccos(c)\\in[0,\\pi]$:\n"
            "$$\\theta=\\pm\\alpha+2k\\pi, \\quad k\\in\\mathbb{Z}.$$\n"
            "קוסינוס זוגי, ולכן $\\cos\\theta=\\cos(-\\theta)$ תופס את שתי נקודות המראה.\n\n"
            "### פתרון כללי של $\\tan\\theta=c$\n"
            "$$\\theta=\\arctan(c)+k\\pi, \\quad k\\in\\mathbb{Z}.$$\n"
            "טנגנס חוזר כל $\\pi$ (לא $2\\pi$), ולכן משפחת פתרונות אחת בלבד.\n\n"
            "### סימנים בכל רבעי המעגל (כלל ASTC)\n"
            "- **R1** ($0$ עד $\\pi/2$): הכל חיובי.\n"
            "- **R2** ($\\pi/2$ עד $\\pi$): רק $\\sin$ חיובי.\n"
            "- **R3** ($\\pi$ עד $3\\pi/2$): רק $\\tan$ חיובי.\n"
            "- **R4** ($3\\pi/2$ עד $2\\pi$): רק $\\cos$ חיובי.\n\n"
            "**אסטרטגיית בחינה:** תמיד שרטטו מעגל יחידה או יישמו ASTC לפני כתיבת זוויות סופיות. "
            "המחשבון מחזיר רק זווית ייחוס אחת — חובה למצוא את זווית המראה בעצמכם."
        ),
    },
}

# Worked examples by example_number
WORKED = {
    1: {
        "body_en_md": (
            "**Given:** Find all $\\theta \\in [0, 2\\pi]$ satisfying $\\sin\\theta = -\\frac{1}{2}$.\n\n"
            "This is the standard \"isolate sine, find reference angle, apply ASTC\" pattern. "
            "It appears on almost every מכינה entrance exam and is prerequisite for harder quadratic trig equations.\n\n"
            "### Move 1\n"
            "$\\sin\\alpha = 1/2$ has reference angle $\\alpha = \\pi/6$ (from the special-values table). "
            "We need $\\sin\\theta = -1/2$, so the magnitude is the same but the sign is negative.\n\n"
            "### Move 2\n"
            "$\\sin\\theta < 0$ in **Q3** and **Q4** (where the $y$-coordinate on the unit circle is negative). "
            "Apply ASTC: only sine is positive in Q2; in Q3 and Q4, sine is negative.\n\n"
            "### Move 3\n"
            "- Q3: $\\theta = \\pi + \\pi/6 = 7\\pi/6$.\n"
            "- Q4: $\\theta = 2\\pi - \\pi/6 = 11\\pi/6$.\n\n"
            "**Answer:** $\\theta = \\dfrac{7\\pi}{6}$ and $\\theta = \\dfrac{11\\pi}{6}$.\n\n"
            "**Verification:** $\\sin(7\\pi/6) = \\sin(\\pi + \\pi/6) = -\\sin(\\pi/6) = -1/2$. ✓ "
            "Similarly $\\sin(11\\pi/6) = -1/2$. ✓\n\n"
            "**Exam tip:** negative sine always gives two solutions in $[0, 2\\pi]$ — never stop after finding one."
        ),
        "body_he_md": (
            "**נתון:** מצאו את כל $\\theta\\in[0,2\\pi]$ שמקיימים $\\sin\\theta=-\\frac{1}{2}$.\n\n"
            "זו התבנית הסטנדרטית \"בודדים סינוס, מוצאים זווית ייחוס, מיישמים ASTC\". "
            "היא מופיעה בכמעט כל בחינת כניסה למכינה ונדרשת למשוואות ריבועיות קשות יותר.\n\n"
            "### צעד 1\n"
            "$\\sin\\alpha=1/2$ → זווית ייחוס $\\alpha=\\pi/6$ (מטבלת ערכים מיוחדים). "
            "אנחנו צריכים $\\sin\\theta=-1/2$, כלומר אותה עוצמה אך סימן שלילי.\n\n"
            "### צעד 2\n"
            "$\\sin\\theta<0$ ב**R3** וב**R4** (כיוון קואורדינטת $y$ במעגל היחידה שלילית). "
            "יישום ASTC: רק סינוס חיובי ב-R2; ב-R3 ו-R4 סינוס שלילי.\n\n"
            "### צעד 3\n"
            "- R3: $\\theta=\\pi+\\pi/6=7\\pi/6$.\n"
            "- R4: $\\theta=2\\pi-\\pi/6=11\\pi/6$.\n\n"
            "**תשובה:** $\\theta=\\dfrac{7\\pi}{6}$ ו-$\\theta=\\dfrac{11\\pi}{6}$.\n\n"
            "**אימות:** $\\sin(7\\pi/6)=\\sin(\\pi+\\pi/6)=-\\sin(\\pi/6)=-1/2$. ✓ "
            "גם $\\sin(11\\pi/6)=-1/2$. ✓\n\n"
            "**טיפ לבחינה:** סינוס שלילי תמיד נותן שני פתרונות ב-$[0,2\\pi]$ — אל תעצרו אחרי אחד."
        ),
    },
    2: {
        "body_en_md": (
            "**Given:** Solve $2\\cos^2\\theta - \\cos\\theta = 0$ for $\\theta \\in [0, 2\\pi]$.\n\n"
            "This quadratic-in-$\\cos\\theta$ equation is a מכינה staple. "
            "Factoring is faster than the quadratic formula and avoids losing solutions by dividing.\n\n"
            "### Move 1\n"
            "Factor out $\\cos\\theta$:\n"
            "$$\\cos\\theta(2\\cos\\theta - 1) = 0.$$\n\n"
            "### Move 2\n"
            "Set each factor to zero separately — **do not divide** both sides by $\\cos\\theta$.\n"
            "- **Factor 1:** $\\cos\\theta = 0 \\Rightarrow \\theta = \\pi/2$ or $\\theta = 3\\pi/2$.\n"
            "- **Factor 2:** $2\\cos\\theta - 1 = 0 \\Rightarrow \\cos\\theta = 1/2 \\Rightarrow \\theta = \\pi/3$ or $\\theta = 5\\pi/3$.\n\n"
            "### Move 3\n"
            "Collect all four solutions:\n"
            "$$\\theta \\in \\left\\{\\frac{\\pi}{3},\\, \\frac{\\pi}{2},\\, \\frac{3\\pi}{2},\\, \\frac{5\\pi}{3}\\right\\}.$$\n\n"
            "### Move 4 (verify $\\theta = \\pi/3$)\n"
            "$2\\cos^2(\\pi/3) - \\cos(\\pi/3) = 2(1/4) - 1/2 = 1/2 - 1/2 = 0$. ✓\n\n"
            "**Key technique:** treat $\\cos\\theta$ as an algebraic variable $u$ and factor $u(2u-1)=0$ "
            "exactly as in algebra. Domain reminder: $-1 \\leq \\cos\\theta \\leq 1$ always.\n\n"
            "**Exam tip:** on מכינה exams, quadratic trig equations appear at least once. "
            "Always check that each $\\cos\\theta$ value lies in $[-1,1]$ before finding angles. "
            "List all four solutions explicitly — partial lists lose significant marks."
        ),
        "body_he_md": (
            "**נתון:** פתרו $2\\cos^2\\theta-\\cos\\theta=0$ עבור $\\theta\\in[0,2\\pi]$.\n\n"
            "משוואה ריבועית ב-$\\cos\\theta$ — תבנית קלאסית במכינה. "
            "פירוק לגורמים מהיר מהנוסחה הריבועית ומונע איבוד פתרונות בחלוקה. "
            "סוג זה של בעיה מופיע לפחות פעם אחת בכל בחינת כניסה.\n\n"
            "### צעד 1\n"
            "הוציאו $\\cos\\theta$ כגורם:\n"
            "$$\\cos\\theta(2\\cos\\theta-1)=0.$$\n\n"
            "### צעד 2\n"
            "שווים כל גורם לאפס בנפרד — **אל תחלקו** ב-$\\cos\\theta$.\n"
            "- **גורם 1:** $\\cos\\theta=0 \\Rightarrow \\theta=\\pi/2$ או $\\theta=3\\pi/2$.\n"
            "- **גורם 2:** $\\cos\\theta=1/2 \\Rightarrow \\theta=\\pi/3$ או $\\theta=5\\pi/3$.\n\n"
            "### צעד 3\n"
            "אספו את ארבעת הפתרונות:\n"
            "$$\\theta\\in\\left\\{\\frac{\\pi}{3},\\frac{\\pi}{2},\\frac{3\\pi}{2},\\frac{5\\pi}{3}\\right\\}.$$\n\n"
            "### צעד 4 (אימות $\\theta=\\pi/3$)\n"
            "$2(1/4)-1/2=0$. ✓\n\n"
            "**טכניקה מרכזית:** התייחסו ל-$\\cos\\theta$ כמשתנה $u$ ופרקו $u(2u-1)=0$ "
            "בדיוק כמו באלגברה. תזכורת: $-1\\leq\\cos\\theta\\leq 1$ תמיד.\n\n"
            "**טיפ לבחינה:** בדקו שכל ערך $\\cos\\theta$ שנמצא נמצא ב-$[-1,1]$ לפני חיפוש זוויות. "
            "אל תחלקו במשוואה ב-$\\cos\\theta$ — זה מאבד את $\\theta=\\pi/2$ ו-$3\\pi/2$."
        ),
    },
    3: {
        "body_en_md": (
            "**Prove:** $\\dfrac{\\sin(A+B)}{\\cos A\\cos B} = \\tan A + \\tan B$.\n\n"
            "**Strategy:** start from the left-hand side (LHS) and transform it into the right-hand side (RHS). "
            "Work on **one side only** — this is an identity, not an equation to solve.\n\n"
            "### Move 1\n"
            "Expand $\\sin(A+B)$ using the angle-addition formula:\n"
            "$$\\text{LHS} = \\frac{\\sin A\\cos B + \\cos A\\sin B}{\\cos A\\cos B}.$$\n\n"
            "### Move 2\n"
            "Split the fraction into two terms:\n"
            "$$= \\frac{\\sin A\\cos B}{\\cos A\\cos B} + \\frac{\\cos A\\sin B}{\\cos A\\cos B}.$$\n\n"
            "### Move 3\n"
            "Cancel common factors in each term:\n"
            "$$= \\frac{\\sin A}{\\cos A} + \\frac{\\sin B}{\\cos B} = \\tan A + \\tan B = \\text{RHS.} \\quad \\square$$\n\n"
            "**Note:** this identity has a direct physical interpretation. "
            "When decomposing velocities or forces at angles $A$ and $B$, "
            "expressions of the form $\\tan A + \\tan B$ appear from the addition formula.\n\n"
            "**Common slip:** trying to \"solve\" an identity by substituting numerical values — "
            "identities hold for all valid $A, B$; prove them algebraically.\n\n"
            "**Exam tip:** identity proofs on מכינה exams typically award 40% for correct expansion "
            "of the compound angle and 40% for clean algebraic simplification."
        ),
        "body_he_md": (
            "**הוכיחו:** $\\dfrac{\\sin(A+B)}{\\cos A\\cos B}=\\tan A+\\tan B$.\n\n"
            "**אסטרטגיה:** התחילו מצד שמאל (LHS) ושנו אותו לצד ימין (RHS). "
            "עבדו על **צד אחד בלבד** — זו זהות, לא משוואה לפתרון.\n\n"
            "### צעד 1\n"
            "פתחו $\\sin(A+B)$ בזהות חיבור זוויות:\n"
            "$$\\text{LHS}=\\frac{\\sin A\\cos B+\\cos A\\sin B}{\\cos A\\cos B}.$$\n\n"
            "### צעד 2\n"
            "פצלו את השבר לשני איברים:\n"
            "$$=\\frac{\\sin A\\cos B}{\\cos A\\cos B}+\\frac{\\cos A\\sin B}{\\cos A\\cos B}.$$\n\n"
            "### צעד 3\n"
            "צמצמו גורמים משותפים בכל איבר:\n"
            "$$=\\frac{\\sin A}{\\cos A}+\\frac{\\sin B}{\\cos B}=\\tan A+\\tan B=\\text{RHS.}\\quad\\square$$\n\n"
            "**הערה:** לזהות יש פרשנות פיזיקלית ישירה — בפירוק מהירויות או כוחות "
            "בזוויות $A$ ו-$B$, ביטויים מהצורה $\\tan A+\\tan B$ מופיעים מזהות החיבור.\n\n"
            "**טעות נפוצה:** לנסות \"לפתור\" זהות בהצבת ערכים מספריים — "
            "זהויות מתקיימות לכל $A,B$ תקינים; הוכיחו אלגברית.\n\n"
            "**טיפ לבחינה:** הוכחות זהות במכינה נותנות בדרך כלל 40% על פתיחה נכונה "
            "של זווית מורכבת ו-40% על פישוט אלגברי נקי. "
            "סמנו $\\square$ בסוף ההוכחה כדי להראות שהצדדים שווים."
        ),
    },
}

PITFALL_HE_EXTRA = (
    "\n\n**זכרו:** בכל שלב — האם זו **זהות** (מתקיימת תמיד) או **משוואה** (רק לזוויות מסוימות)? "
    "הבלבול בין השניים גורם לטיפול שגוי בשאלות בחינה."
)

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "We need $\\cos\\theta = \\sqrt{3}/2$ on $[0, 2\\pi]$. "
            "Reference angle: $\\alpha = \\arccos(\\sqrt{3}/2) = \\pi/6$. "
            "Since $\\cos\\theta > 0$, use ASTC: cosine is positive in **Q1** and **Q4** only.\n\n"
            "- Q1: $\\theta = \\pi/6$.\n"
            "- Q4: $\\theta = 2\\pi - \\pi/6 = 11\\pi/6$.\n\n"
            "**Answer:** $\\theta = \\pi/6$ and $\\theta = 11\\pi/6$. "
            "**Verify:** $\\cos(\\pi/6) = \\cos(11\\pi/6) = \\sqrt{3}/2$ ✓."
        ),
        "checkpoint_solution_he": (
            "נדרש $\\cos\\theta=\\sqrt{3}/2$ ב-$[0,2\\pi]$. "
            "זווית ייחוס: $\\alpha=\\arccos(\\sqrt{3}/2)=\\pi/6$. "
            "כיוון $\\cos\\theta>0$, יישום ASTC: קוסינוס חיובי ב-**R1** וב-**R4** בלבד.\n\n"
            "- R1: $\\theta=\\pi/6$.\n"
            "- R4: $\\theta=2\\pi-\\pi/6=11\\pi/6$.\n\n"
            "**תשובה:** $\\theta=\\pi/6$ ו-$\\theta=11\\pi/6$. "
            "**אימות:** $\\cos(\\pi/6)=\\cos(11\\pi/6)=\\sqrt{3}/2$ ✓."
        ),
    },
    {
        "checkpoint_solution_en": (
            "Factor the equation: $\\sin\\theta(\\sin\\theta - 1) = 0$.\n\n"
            "**Branch 1:** $\\sin\\theta = 0 \\Rightarrow \\theta = 0, \\pi, 2\\pi$.\n"
            "**Branch 2:** $\\sin\\theta = 1 \\Rightarrow \\theta = \\pi/2$ (only one solution in $[0, 2\\pi]$).\n\n"
            "Collect: $\\theta \\in \\{0, \\pi/2, \\pi, 2\\pi\\}$. "
            "**Verify** $\\theta = \\pi/2$: $\\sin^2(\\pi/2) - \\sin(\\pi/2) = 1 - 1 = 0$ ✓. "
            "Do not divide by $\\sin\\theta$ — that would lose the $\\sin\\theta = 0$ branch."
        ),
        "checkpoint_solution_he": (
            "פירוק המשוואה: $\\sin\\theta(\\sin\\theta-1)=0$.\n\n"
            "**ענף 1:** $\\sin\\theta=0 \\Rightarrow \\theta=0,\\pi,2\\pi$.\n"
            "**ענף 2:** $\\sin\\theta=1 \\Rightarrow \\theta=\\pi/2$ (פתרון יחיד ב-$[0,2\\pi]$).\n\n"
            "איסוף: $\\theta\\in\\{0,\\pi/2,\\pi,2\\pi\\}$. "
            "**אימות** $\\theta=\\pi/2$: $\\sin^2(\\pi/2)-\\sin(\\pi/2)=1-1=0$ ✓. "
            "אל תחלקו ב-$\\sin\\theta$ — זה מאבד את ענף $\\sin\\theta=0$."
        ),
    },
]

METHOD_GUIDE = {
    "body_he_md": (
        "**אלגוריתם שלב-אחר-שלב לכל משוואה טריגונומטרית:**\n\n"
        "1. **בודדו פונקציה אחת.** סדרו לקבלת $\\sin\\theta=c$, $\\cos\\theta=c$ או $\\tan\\theta=c$.\n"
        "2. **אם ריבועית בפונקציה טריגונומטרית:** הציבו $u=\\sin\\theta$ (או $\\cos\\theta$), "
        "פרקו לגורמים או השתמשו בנוסחת שורשים. דחו שורשים מחוץ ל-$[-1,1]$.\n"
        "3. **מצאו זווית ייחוס** $\\alpha$ מהפונקציה ההפוכה או מטבלת ערכים מיוחדים.\n"
        "4. **יישמו כלל ASTC** — שרטטו מעגל יחידה אם צריך — למציאת כל הפתרונות ב-$[0,2\\pi]$.\n"
        "5. **כתבו פתרון כללי** אם נדרש: $+2k\\pi$ ל-$\\sin/\\cos$; $+k\\pi$ ל-$\\tan$.\n"
        "6. **אמתו** לפחות פתרון אחד במשוואה המקורית.\n\n"
        "| פונקציה | ייחוס | רבעים חיוביים | פתרון כללי |\n"
        "|---|---|---|---|\n"
        "| $\\sin\\theta=c>0$ | $\\alpha=\\arcsin c$ | R1, R2 | $\\alpha+2k\\pi$; $(\\pi-\\alpha)+2k\\pi$ |\n"
        "| $\\sin\\theta=c<0$ | $\\alpha=\\arcsin|c|$ | R3, R4 | $(\\pi+\\alpha)+2k\\pi$; $(2\\pi-\\alpha)+2k\\pi$ |\n"
        "| $\\cos\\theta=c>0$ | $\\alpha=\\arccos c$ | R1, R4 | $\\pm\\alpha+2k\\pi$ |\n"
        "| $\\cos\\theta=c<0$ | $\\alpha=\\arccos|c|$ | R2, R3 | $(\\pi-\\alpha)+2k\\pi$; $(\\pi+\\alpha)+2k\\pi$ |\n"
        "| $\\tan\\theta=c$ | $\\alpha=\\arctan c$ | R1 (R3 אותו סימן) | $\\alpha+k\\pi$ |\n\n"
        "**טיפ למכינה:** כתבו תמיד את הפתרון הכללי לפני הגבלה לקטע — "
        "בוחנים נותנים נקודות חלקיות על נוסחאות נכונות."
    ),
}

WHY_MATTERS = {
    "body_en_md": (
        "Trigonometry is the **language of periodic motion** — and periodic motion is everywhere "
        "in first-year university physics and engineering.\n\n"
        "**Calculus connection:** the derivative $(\\sin x)' = \\cos x$ assumes $x$ is in radians. "
        "Trig substitutions like $x = \\sin u$ in integrals require fluent identity manipulation. "
        "Students weak on $\\sin(2\\theta)$ or angle-addition formulas lose marks on integration problems "
        "even when they know the integration technique.\n\n"
        "**Physics connection:** resolving a force $\\vec{F}$ at angle $\\theta$ into components "
        "uses $\\cos\\theta$ and $\\sin\\theta$. Simple harmonic motion $x = A\\sin(\\omega t + \\phi)$ "
        "appears in mechanics, waves, and AC circuits.\n\n"
        "**Exam reality:** מכינה entrance exams and first-year quizzes test whether you find "
        "**all** solutions in an interval, not just one. Master ASTC and factoring before attempting "
        "harder material in calculus and physics."
    ),
    "body_he_md": (
        "טריגונומטריה היא **שפת התנועה המחזורית** — ותנועה מחזורית נמצאת בכל מקום "
        "בפיזיקה והנדסה בשנה א'.\n\n"
        "**קשר לחשבון:** הנגזרת $(\\sin x)'=\\cos x$ מניחה ש-$x$ ברדיאנים. "
        "הצבות טריגונומטריות כמו $x=\\sin u$ באינטגרלים דורשות שליטה בזהויות. "
        "תלמידים חלשים ב-$\\sin(2\\theta)$ או בזהויות חיבור זוויות מפסידים נקודות "
        "בבעיות אינטגרל גם כשהם יודעים את טכניקת האינטגרציה.\n\n"
        "**קשר לפיזיקה:** פירוק כוח $\\vec{F}$ בזווית $\\theta$ לרכיבים משתמש ב-$\\cos\\theta$ ו-$\\sin\\theta$. "
        "תנועה הרמונית $x=A\\sin(\\omega t+\\phi)$ מופיעה במכניקה, בגלים ובמעגלי AC.\n\n"
        "**מציאות בחינה:** בחינות כניסה למכינה ומבחנים בשנה א' בודקים האם מוצאים "
        "**את כל** הפתרונות בקטע, לא רק אחד. שלטו ב-ASTC ובפירוק לגורמים לפני "
        "מעבר לחומר קשה יותר בחשבון ובפיזיקה."
    ),
}

BEFORE_EXAM_HE = (
    "### נוסחאות חובה\n"
    "- **פיתגורס:** $\\sin^2+\\cos^2=1$; $1+\\tan^2=\\sec^2$; $1+\\cot^2=\\csc^2$.\n"
    "- **חיבור זוויות:** $\\sin(A\\pm B)=\\sin A\\cos B\\pm\\cos A\\sin B$; "
    "$\\cos(A\\pm B)=\\cos A\\cos B\\mp\\sin A\\sin B$.\n"
    "- **זווית כפולה:** $\\sin(2A)=2\\sin A\\cos A$; $\\cos(2A)=2\\cos^2 A-1=1-2\\sin^2 A$.\n"
    "- **ערכים מיוחדים:** שינון $\\pi/6$, $\\pi/4$, $\\pi/3$ — גם ברדיאנים.\n"
    "- **פתרון כללי:** $\\sin\\theta=c$: $\\theta=\\arcsin c+2k\\pi$ או $(\\pi-\\arcsin c)+2k\\pi$. "
    "$\\cos\\theta=c$: $\\theta=\\pm\\arccos c+2k\\pi$. $\\tan\\theta=c$: $\\theta=\\arctan c+k\\pi$.\n\n"
    "### תבניות שאלות נפוצות במכינה\n"
    "1. מצאו את כל הפתרונות ב-$[0,2\\pi]$ של $\\sin/\\cos/\\tan=$ ערך.\n"
    "2. פתרו משוואה ריבועית בפונקציה טריגונומטרית (פרקו לגורמים קודם).\n"
    "3. הוכיחו זהות טריגונומטרית (צד אחד → צד שני).\n"
    "4. נתון $\\sin$ או $\\cos$ ברבע — מצאו את שאר הפונקציות (שימו לב לסימן!).\n"
    "5. חישוב/פישוט עם נוסחאות זווית כפולה או חיבור זוויות.\n\n"
    "### קriterיוני ניקוד\n"
    "- פתרון משוואות: 30% פירוק נכון, 30% זווית ייחוס, 40% כל הפתרונות בקטע.\n"
    "- הוכחת זהויות: 40% פתיחה נכונה, 40% שלבי אלגברה, 20% סיום (QED).\n"
    "- בעיות עם זווית נתונה: 40% שימוש בזהות פיתגורס, 60% סימן נכון + חישוב."
)

SUMMARY = {
    "body_en_md": (
        "- **Unit circle:** $\\cos\\theta = x$, $\\sin\\theta = y$ on the unit circle; all definitions flow from here.\n"
        "- **Pythagorean:** $\\sin^2\\theta + \\cos^2\\theta = 1$; divide by $\\cos^2$ or $\\sin^2$ for tangent/cotangent forms.\n"
        "- **ASTC:** Q1 all+; Q2 sin+; Q3 tan+; Q4 cos+ — use every time you solve an equation.\n"
        "- **Angle-addition:** $\\sin(A+B)=\\sin A\\cos B+\\cos A\\sin B$; $\\cos(A+B)=\\cos A\\cos B-\\sin A\\sin B$.\n"
        "- **Double-angle:** $\\sin(2A)=2\\sin A\\cos A$; $\\cos(2A)=1-2\\sin^2 A=2\\cos^2 A-1$.\n"
        "- **Solving $\\sin\\theta=c$:** reference angle $\\alpha=\\arcsin|c|$; two solutions per $2\\pi$ period via ASTC.\n"
        "- **Solving $\\cos\\theta=c$:** reference angle $\\alpha=\\arccos|c|$; symmetric solutions $\\pm\\alpha$.\n"
        "- **Solving $\\tan\\theta=c$:** one family $\\alpha + k\\pi$; period is $\\pi$, not $2\\pi$.\n"
        "- **Key habit:** factor before dividing; verify at least one solution; radians in calculus."
    ),
    "body_he_md": (
        "- **מעגל יחידה:** $\\cos\\theta=x$, $\\sin\\theta=y$; כל ההגדרות נובעות מכאן.\n"
        "- **פיתגורס:** $\\sin^2\\theta+\\cos^2\\theta=1$; חלוקה ב-$\\cos^2$ או $\\sin^2$ לצורות טנגנס/קוטנגנס.\n"
        "- **ASTC:** R1 הכל+; R2 sin+; R3 tan+; R4 cos+ — יישמו בכל פתרון משוואה.\n"
        "- **חיבור זוויות:** $\\sin(A+B)=\\sin A\\cos B+\\cos A\\sin B$; $\\cos(A+B)=\\cos A\\cos B-\\sin A\\sin B$.\n"
        "- **זווית כפולה:** $\\sin(2A)=2\\sin A\\cos A$; $\\cos(2A)=1-2\\sin^2 A=2\\cos^2 A-1$.\n"
        "- **פתרון $\\sin\\theta=c$:** זווית ייחוס $\\alpha=\\arcsin|c|$; שני פתרונות למחזור $2\\pi$.\n"
        "- **פתרון $\\cos\\theta=c$:** זווית ייחוס; פתרונות סימטריים $\\pm\\alpha$.\n"
        "- **פתרון $\\tan\\theta=c$:** משפחה אחת $\\alpha+k\\pi$; מחזור $\\pi$, לא $2\\pi$.\n"
        "- **הרגל מפתח:** פרקו לפני חלוקה; אמתו פתרון; רדיאנים בחשבון."
    ),
}

EXPLANATIONS = {
    1: {
        "explanation_en": (
            "To convert degrees to radians, multiply by $\\frac{\\pi}{180°}$. "
            "Here: $210° \\times \\frac{\\pi}{180°} = \\frac{210\\pi}{180}$. "
            "Simplify by dividing numerator and denominator by 30: $\\frac{210}{180} = \\frac{7}{6}$, "
            "so the answer is $\\frac{7\\pi}{6}$ radians.\n\n"
            "**Why this works:** radians measure arc length on the unit circle — "
            "$210°$ is $\\frac{7}{12}$ of a full $360°$ turn, which equals $\\frac{7\\pi}{6}$ radians. "
            "Calculus formulas (derivatives, integrals) require radians.\n\n"
            "**Common slip:** leaving the answer as $\\frac{210\\pi}{180}$ without simplifying, "
            "or forgetting the $\\pi$ entirely and writing just $7/6$.\n\n"
            "**Exam tip:** recognize $210°$ as $180° + 30° = \\pi + \\pi/6 = 7\\pi/6$ — "
            "this Q3 angle appears frequently in sin/cos equations. **Verify:** "
            "$\\frac{7\\pi}{6} \\times \\frac{180°}{\\pi} = 210°$ ✓."
        ),
        "explanation_he": (
            "להמרת מעלות לרדיאנים, מכפילים ב-$\\frac{\\pi}{180°}$. "
            "כאן: $210° \\times \\frac{\\pi}{180°} = \\frac{210\\pi}{180}$. "
            "מצמצמים בחלוקה ב-30: $\\frac{210}{180}=\\frac{7}{6}$, "
            "ולכן התשובה $\\frac{7\\pi}{6}$ רדיאנים.\n\n"
            "**למה זה עובד:** רדיאנים מודדים אורך קשת על מעגל יחידה — "
            "$210°$ הם $\\frac{7}{12}$ מסיבוב מלא, ששווה $\\frac{7\\pi}{6}$ רדיאנים. "
            "נוסחאות חשבון (נגזרות, אינטגרלים) דורשות רדיאנים.\n\n"
            "**שיטה חלופית:** $210°=180°+30°$, ולכן $\\pi+\\pi/6=7\\pi/6$ — "
            "זווית זו ב-R3 ומופיעה הרבה במשוואות sin/cos.\n\n"
            "**טעות נפוצה:** להשאיר $\\frac{210\\pi}{180}$ בלי צמצום, "
            "או לשכוח את $\\pi$ ולכתוב רק $7/6$.\n\n"
            "**טיפ לבחינה:** זיהוי $210°$ כ-$180°+30°=\\pi+\\pi/6=7\\pi/6$ — "
            "זווית R3 זו מופיעה הרבה במשוואות sin/cos. **אימות:** "
            "$\\frac{7\\pi}{6}\\times\\frac{180°}{\\pi}=210°$ ✓."
        ),
    },
    2: {
        "explanation_en": (
            "We need all $\\theta \\in [0, 2\\pi]$ where $\\tan\\theta = 1$. "
            "Reference angle: $\\alpha = \\arctan(1) = \\pi/4$. "
            "Tangent is positive in **Q1** and **Q3** (ASTC: \"All\" in Q1, \"Tan\" in Q3).\n\n"
            "- Q1: $\\theta = \\pi/4$.\n"
            "- Q3: $\\theta = \\pi + \\pi/4 = 5\\pi/4$.\n\n"
            "**Why two solutions:** tangent has period $\\pi$, so exactly two solutions appear in $[0, 2\\pi]$. "
            "Unlike sine/cosine, there is only one family $\\alpha + k\\pi$, but $k=0$ and $k=1$ both land in the interval.\n\n"
            "**Common slip:** giving only $\\pi/4$ and forgetting $5\\pi/4$, "
            "or incorrectly placing a solution in Q2/Q4 where tangent is negative.\n\n"
            "**Exam tip:** for $\\tan\\theta = 1$, memorize the pair $\\pi/4$ and $5\\pi/4$. "
            "**Verify:** $\\tan(\\pi/4) = \\tan(5\\pi/4) = 1$ ✓."
        ),
        "explanation_he": (
            "מחפשים את כל $\\theta\\in[0,2\\pi]$ שמקיימים $\\tan\\theta=1$. "
            "זווית ייחוס: $\\alpha=\\arctan(1)=\\pi/4$. "
            "טנגנס חיובי ב-**R1** וב-**R3** (ASTC: \"All\" ב-R1, \"Tan\" ב-R3).\n\n"
            "- R1: $\\theta=\\pi/4$.\n"
            "- R3: $\\theta=\\pi+\\pi/4=5\\pi/4$.\n\n"
            "**למה שני פתרונות:** מחזור טנגנס הוא $\\pi$, ולכן בדיוק שני פתרונות ב-$[0,2\\pi]$. "
            "בניגוד לסינוס/קוסינוס, יש משפחה אחת $\\alpha+k\\pi$, אך $k=0$ ו-$k=1$ שניהם בקטע.\n\n"
            "**טעות נפוצה:** לתת רק $\\pi/4$ ולשכוח $5\\pi/4$, "
            "או למקם פתרון ב-R2/R4 שם טנגנס שלילי.\n\n"
            "**טיפ לבחינה:** ל-$\\tan\\theta=1$, שינון הזוג $\\pi/4$ ו-$5\\pi/4$. "
            "**אימות:** $\\tan(\\pi/4)=\\tan(5\\pi/4)=1$ ✓."
        ),
    },
    3: {
        "explanation_en": (
            "Start from the fundamental identity $\\sin^2\\theta + \\cos^2\\theta = 1$. "
            "Divide every term by $\\cos^2\\theta$ (valid where $\\cos\\theta \\neq 0$):\n"
            "$$\\frac{\\sin^2\\theta}{\\cos^2\\theta} + \\frac{\\cos^2\\theta}{\\cos^2\\theta} = \\frac{1}{\\cos^2\\theta}$$\n"
            "which simplifies to $\\tan^2\\theta + 1 = \\sec^2\\theta$. ✓\n\n"
            "**Why this works:** dividing by $\\cos^2\\theta$ converts sine and cosine into tangent and secant — "
            "the Pythagorean identity on the unit circle ($x^2 + y^2 = 1$) becomes "
            "a relation between tangent and secant.\n\n"
            "**Common slip:** dividing by $\\sin^2\\theta$ instead (which gives $1 + \\cot^2\\theta = \\csc^2\\theta$ — "
            "a different but equally valid identity). Also forgetting the domain restriction $\\cos\\theta \\neq 0$.\n\n"
            "**Exam tip:** this derivation takes 30 seconds and earns full marks on identity questions. "
            "The same technique derives $1 + \\cot^2\\theta = \\csc^2\\theta$ by dividing by $\\sin^2\\theta$."
        ),
        "explanation_he": (
            "מתחילים מהזהות $\\sin^2\\theta+\\cos^2\\theta=1$. "
            "מחלקים כל איבר ב-$\\cos^2\\theta$ (תקף כש-$\\cos\\theta\\neq 0$):\n"
            "$$\\frac{\\sin^2\\theta}{\\cos^2\\theta}+\\frac{\\cos^2\\theta}{\\cos^2\\theta}=\\frac{1}{\\cos^2\\theta}$$\n"
            "שמתפשט ל-$\\tan^2\\theta+1=\\sec^2\\theta$. ✓\n\n"
            "**למה זה עובד:** חלוקה ב-$\\cos^2\\theta$ הופכת סינוס וקוסינוס לטנגנס ו-$\\sec$ — "
            "זהות פיתגורס על מעגל היחידה ($x^2+y^2=1$) הופכת לקשר בין $\\tan$ ל-$\\sec$.\n\n"
            "**טעות נפוצה:** לחלק ב-$\\sin^2\\theta$ במקום (נותן $1+\\cot^2\\theta=\\csc^2\\theta$ — "
            "זהות אחרת אך תקפה). גם שכחת מגבלת תחום $\\cos\\theta\\neq 0$.\n\n"
            "**טיפ לבחינה:** הוכחה זו לוקחת 30 שניות ומביאה ציון מלא. "
            "אותה טכניקה נותנת $1+\\cot^2\\theta=\\csc^2\\theta$ בחלוקה ב-$\\sin^2\\theta$."
        ),
    },
    4: {
        "explanation_en": (
            "Apply the angle-addition formula $\\sin(A+B) = \\sin A\\cos B + \\cos A\\sin B$ "
            "with $A = \\pi/3$ and $B = \\pi/4$:\n"
            "$$\\sin(\\pi/3+\\pi/4) = \\sin(\\pi/3)\\cos(\\pi/4) + \\cos(\\pi/3)\\sin(\\pi/4)$$\n"
            "$$= \\frac{\\sqrt{3}}{2}\\cdot\\frac{\\sqrt{2}}{2} + \\frac{1}{2}\\cdot\\frac{\\sqrt{2}}{2} "
            "= \\frac{\\sqrt{6}}{4} + \\frac{\\sqrt{2}}{4} = \\frac{\\sqrt{6}+\\sqrt{2}}{4}.$$\n\n"
            "**Why this works:** we decompose an unfamiliar angle ($75° = 45° + 30°$) "
            "into two special angles whose sine and cosine we know by heart. "
            "This technique — splitting any angle into sums of $\\pi/6$, $\\pi/4$, $\\pi/3$ — "
            "is the standard approach when no calculator is allowed.\n\n"
            "**Common slip:** sign errors in the formula (using minus instead of plus), "
            "or arithmetic mistakes when combining $\\sqrt{6}/4 + \\sqrt{2}/4$.\n\n"
            "**Exam tip:** always write the formula before substituting values — "
            "examiners award marks for setup. Substitute: $\\sin(\\pi/3)=\\sqrt{3}/2$, "
            "$\\cos(\\pi/4)=\\sqrt{2}/2$, $\\cos(\\pi/3)=1/2$, $\\sin(\\pi/4)=\\sqrt{2}/2$. "
            "**Verify:** $\\frac{\\sqrt{6}+\\sqrt{2}}{4} \\approx 0.966$, "
            "and $\\sin(75°) \\approx 0.966$ ✓."
        ),
        "explanation_he": (
            "מיישמים $\\sin(A+B)=\\sin A\\cos B+\\cos A\\sin B$ "
            "עם $A=\\pi/3$ ו-$B=\\pi/4$:\n"
            "$$\\sin(\\pi/3+\\pi/4)=\\sin(\\pi/3)\\cos(\\pi/4)+\\cos(\\pi/3)\\sin(\\pi/4)$$\n"
            "$$=\\frac{\\sqrt{3}}{2}\\cdot\\frac{\\sqrt{2}}{2}+\\frac{1}{2}\\cdot\\frac{\\sqrt{2}}{2}"
            "=\\frac{\\sqrt{6}}{4}+\\frac{\\sqrt{2}}{4}=\\frac{\\sqrt{6}+\\sqrt{2}}{4}.$$\n\n"
            "**למה זה עובד:** מפרקים זווית לא מוכרת ($75°=45°+30°$) "
            "לשתי זוויות מיוחדות שסינוס וקוסינוס שלהן ידועים בעל-פה. "
            "טכניקה זו — פירוק כל זווית לסכום של $\\pi/6$, $\\pi/4$, $\\pi/3$ — "
            "היא הגישה הסטנדרטית כשאין מחשבון.\n\n"
            "**שלבי חישוב:** $\\sin(\\pi/3)=\\sqrt{3}/2$, $\\cos(\\pi/4)=\\sqrt{2}/2$, "
            "$\\cos(\\pi/3)=1/2$, $\\sin(\\pi/4)=\\sqrt{2}/2$. הכפל והחיבור נותנים "
            "$\\frac{\\sqrt{6}+\\sqrt{2}}{4}$.\n\n"
            "**טעות נפוצה:** שגיאות סימן בנוסחה, "
            "או טעויות חשבון בחיבור $\\sqrt{6}/4+\\sqrt{2}/4$.\n\n"
            "**טיפ לבחינה:** כתבו תמיד את הנוסחה לפני ההצבה — "
            "בוחנים נותנים נקודות על ההכנה. **אימות:** $\\frac{\\sqrt{6}+\\sqrt{2}}{4}\\approx 0.966$, "
            "ו-$\\sin(75°)\\approx 0.966$ ✓."
        ),
    },
    5: {
        "explanation_en": (
            "Substitute $u = \\sin\\theta$ to get $2u^2 - u - 1 = 0$. Factor: $(2u+1)(u-1) = 0$, "
            "so $u = -1/2$ or $u = 1$. Both lie in $[-1, 1]$ ✓.\n\n"
            "**Branch 1:** $\\sin\\theta = 1 \\Rightarrow \\theta = \\pi/2$ (unique in $[0, 2\\pi]$).\n"
            "**Branch 2:** $\\sin\\theta = -1/2$. Reference angle $\\pi/6$; sine negative in Q3 and Q4: "
            "$\\theta = 7\\pi/6$ and $\\theta = 11\\pi/6$.\n\n"
            "**Answer:** $\\{\\pi/2, 7\\pi/6, 11\\pi/6\\}$.\n\n"
            "**Common slip:** missing the $\\sin\\theta = 1$ branch, or finding only one solution "
            "for $\\sin\\theta = -1/2$. Also using the quadratic formula when factoring is faster.\n\n"
            "**Exam tip:** after factoring, solve each branch separately and list **all** angles. "
            "**Verify** $\\theta = 7\\pi/6$: $2(1/4) - (-1/2) - 1 = 1/2 + 1/2 - 1 = 0$ ✓."
        ),
        "explanation_he": (
            "מציבים $u=\\sin\\theta$ ומקבלים $2u^2-u-1=0$. פירוק: $(2u+1)(u-1)=0$, "
            "כלומר $u=-1/2$ או $u=1$. שניהם ב-$[-1,1]$ ✓.\n\n"
            "**ענף 1:** $\\sin\\theta=1 \\Rightarrow \\theta=\\pi/2$ (יחיד ב-$[0,2\\pi]$).\n"
            "**ענף 2:** $\\sin\\theta=-1/2$. זווית ייחוס $\\pi/6$; סינוס שלילי ב-R3 ו-R4: "
            "$\\theta=7\\pi/6$ ו-$\\theta=11\\pi/6$.\n\n"
            "**תשובה:** $\\{\\pi/2, 7\\pi/6, 11\\pi/6\\}$.\n\n"
            "**טעות נפוצה:** החמצת ענף $\\sin\\theta=1$, או מציאת פתרון יחיד ל-$\\sin\\theta=-1/2$. "
            "גם שימוש בנוסחה הריבועית כשפירוק מהיר יותר.\n\n"
            "**טיפ לבחינה:** אחרי פירוק, פתרו כל ענף בנפרד ורשמו **את כל** הזוויות. "
            "**אימות** $\\theta=7\\pi/6$: $2(1/4)-(-1/2)-1=0$ ✓."
        ),
    },
    6: {
        "explanation_en": (
            "The double-angle identity for cosine has three equivalent forms:\n"
            "$\\cos(2\\theta) = \\cos^2\\theta - \\sin^2\\theta = 1 - 2\\sin^2\\theta = 2\\cos^2\\theta - 1$.\n\n"
            "The question asks for $\\sin\\theta$ only, so choose $\\cos(2\\theta) = 1 - 2\\sin^2\\theta$. "
            "This form is derived from $\\cos^2\\theta - \\sin^2\\theta$ by replacing $\\cos^2\\theta$ "
            "with $1 - \\sin^2\\theta$ via the Pythagorean identity.\n\n"
            "**Why this form:** in calculus integrals of $\\sin^2 x$, you need cosine written entirely "
            "in terms of sine (or vice versa) to apply substitution or reduction formulas.\n\n"
            "**Common slip:** choosing $2\\cos^2\\theta - 1$ instead, which still contains cosine. "
            "Another error: writing $\\cos(2\\theta) = 1 + 2\\sin^2\\theta$ (wrong sign).\n\n"
            "**Exam tip:** read the question carefully — \"in terms of $\\sin\\theta$ only\" "
            "dictates which of the three forms to use. No further simplification is possible."
        ),
        "explanation_he": (
            "לזהות זווית כפולה של קוסינוס יש שלוש צורות שקולות:\n"
            "$\\cos(2\\theta)=\\cos^2\\theta-\\sin^2\\theta=1-2\\sin^2\\theta=2\\cos^2\\theta-1$.\n\n"
            "השאלה מבקשת רק $\\sin\\theta$, ולכן בוחרים $\\cos(2\\theta)=1-2\\sin^2\\theta$. "
            "צורה זו נגזרת מ-$\\cos^2\\theta-\\sin^2\\theta$ בהחלפת $\\cos^2\\theta$ "
            "ב-$1-\\sin^2\\theta$ דרך זהות פיתגורס.\n\n"
            "**למה צורה זו:** באינטגרלים של $\\sin^2 x$ בחשבון, צריך לכתוב קוסינוס "
            "רק במונחי סינוס (או להפך) להצבה או נוסחאות הפחתה.\n\n"
            "**טעות נפוצה:** לבחור $2\\cos^2\\theta-1$ שעדיין מכיל קוסינוס. "
            "גם כתיבה $\\cos(2\\theta)=1+2\\sin^2\\theta$ (סימן שגוי).\n\n"
            "**טיפ לבחינה:** קראו את השאלה — \"במונחי $\\sin\\theta$ בלבד\" "
            "קובע איזו מהשלוש צורות להשתמש. אין פישוט נוסף."
        ),
    },
    7: {
        "explanation_en": (
            "Given $\\sin\\theta = 3/5$ in Q2. Step 1: use Pythagorean identity:\n"
            "$\\cos^2\\theta = 1 - \\sin^2\\theta = 1 - 9/25 = 16/25$.\n\n"
            "Step 2: $\\cos\\theta = \\pm 4/5$. In **Q2**, cosine is **negative** (ASTC: only sine positive), "
            "so $\\cos\\theta = -4/5$.\n\n"
            "Step 3: $\\tan\\theta = \\sin\\theta / \\cos\\theta = (3/5)/(-4/5) = -3/4$.\n\n"
            "Step 4: $\\sin(2\\theta) = 2\\sin\\theta\\cos\\theta = 2(3/5)(-4/5) = -24/25$.\n\n"
            "**Common slip:** taking $\\cos\\theta = +4/5$ (ignoring the quadrant sign), "
            "which cascades into wrong tangent and double-angle values.\n\n"
            "**Exam tip:** always determine the sign from the quadrant **before** computing other functions. "
            "Draw a sketch triangle in Q2 with opposite = 3, hypotenuse = 5, adjacent = -4. "
            "This 3-4-5 triangle is the most common Pythagorean triple on entrance exams."
        ),
        "explanation_he": (
            "נתון $\\sin\\theta=3/5$ ב-R2. שלב 1: זהות פיתגורס:\n"
            "$\\cos^2\\theta=1-\\sin^2\\theta=1-9/25=16/25$.\n\n"
            "שלב 2: $\\cos\\theta=\\pm 4/5$. ב-**R2** קוסינוס **שלילי** (ASTC: רק סינוס חיובי), "
            "ולכן $\\cos\\theta=-4/5$.\n\n"
            "שלב 3: $\\tan\\theta=\\sin\\theta/\\cos\\theta=(3/5)/(-4/5)=-3/4$.\n\n"
            "שלב 4: $\\sin(2\\theta)=2\\sin\\theta\\cos\\theta=2(3/5)(-4/5)=-24/25$.\n\n"
            "**טעות נפוצה:** לקחת $\\cos\\theta=+4/5$ (התעלמות מסימן הרבע), "
            "מה שגורם לטנגנס וזווית כפולה שגויים.\n\n"
            "**טיפ לבחינה:** קבעו תמיד את הסימן מהרבע **לפני** חישוב שאר הפונקציות. "
            "שרטטו משולש ב-R2 עם נגד = 3, יתר = 5, צל = -4. "
            "משולש 3-4-5 הוא שלישיית פיתגורס הנפוצה ביותר בבחינות כניסה.\n\n"
            "**אימות:** $\\sin(2\\theta)=2\\sin\\theta\\cos\\theta=2(3/5)(-4/5)=-24/25$ ✓."
        ),
    },
    8: {
        "explanation_en": (
            "Start from the LHS and expand $\\cos(A-B)$ using the angle-subtraction formula "
            "$\\cos(A-B) = \\cos A\\cos B + \\sin A\\sin B$:\n"
            "$$\\text{LHS} = \\frac{\\cos A\\cos B + \\sin A\\sin B}{\\cos A\\cos B} "
            "= 1 + \\frac{\\sin A\\sin B}{\\cos A\\cos B} = 1 + \\tan A\\tan B = \\text{RHS}. \\quad \\checkmark$$\n\n"
            "**Strategy:** work on one side only. Expand the compound angle, split the fraction, "
            "and recognize $\\sin A/\\cos A = \\tan A$ in each term.\n\n"
            "**Common slip:** starting from both sides simultaneously (not valid for a formal proof), "
            "or using $\\cos(A+B)$ instead of $\\cos(A-B)$ (sign error in the middle term).\n\n"
            "**Exam tip:** identity proofs earn partial credit for correct expansion even if the final "
            "algebra has a minor error. Name the identity you use: \"by angle-subtraction formula, "
            "$\\cos(A-B) = \\cos A\\cos B + \\sin A\\sin B$.\" This identity is the cosine counterpart "
            "of the tangent addition formula proved in Worked Example 3."
        ),
        "explanation_he": (
            "מתחילים מ-LHS ופותחים $\\cos(A-B)$ בנוסחת חיסור זוויות "
            "$\\cos(A-B)=\\cos A\\cos B+\\sin A\\sin B$:\n"
            "$$\\text{LHS}=\\frac{\\cos A\\cos B+\\sin A\\sin B}{\\cos A\\cos B}"
            "=1+\\frac{\\sin A\\sin B}{\\cos A\\cos B}=1+\\tan A\\tan B=\\text{RHS}.\\quad\\checkmark$$\n\n"
            "**אסטרטגיה:** עבדו על צד אחד בלבד. פתחו זווית מורכבת, פצלו את השבר, "
            "וזהו $\\sin A/\\cos A=\\tan A$ בכל איבר.\n\n"
            "**טעות נפוצה:** להתחיל משני הצדדים (לא תקף להוכחה פורמלית), "
            "או להשתמש ב-$\\cos(A+B)$ במקום $\\cos(A-B)$ (שגיאת סימן).\n\n"
            "**טיפ לבחינה:** הוכחות זהות מקבלות נקודות חלקיות על פתיחה נכונה. "
            "ציינו את הזהות: \"לפי נוסחת חיסור, $\\cos(A-B)=\\cos A\\cos B+\\sin A\\sin B$.\" "
            "זהות זו היא המקבילה הקוסינוסית לנוסחת חיבור הטנגנס מדוגמה 3. "
            "במכינה, הוכחות מסוג זה מופיעות לעיתים קרובות — תרגלו את התבנית: פתיחה, פיצול שבר, זיהוי $\\tan$."
        ),
    },
}


def main():
    data = json.loads(LESSON.read_text(encoding="utf-8"))

    cp_idx = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in PATCHES:
            sec.update(PATCHES[kind])
        if kind == "worked_example":
            num = sec.get("example_number")
            if num in WORKED:
                sec.update(WORKED[num])
        if kind == "checkpoint" and cp_idx < len(CHECKPOINTS):
            sec.update(CHECKPOINTS[cp_idx])
            cp_idx += 1
        if kind == "method_guide":
            sec.update(METHOD_GUIDE)
        if kind == "why_matters":
            sec.update(WHY_MATTERS)
        if kind == "before_exam":
            sec["body_he_md"] = BEFORE_EXAM_HE
        if kind == "summary":
            sec.update(SUMMARY)
        if kind == "pitfall":
            sec["body_he_md"] = (sec.get("body_he_md") or "") + PITFALL_HE_EXTRA

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            q.update(EXPLANATIONS[ord_])

    LESSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Expanded {LESSON.name}")


if __name__ == "__main__":
    main()
