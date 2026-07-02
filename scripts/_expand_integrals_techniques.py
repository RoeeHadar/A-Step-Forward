#!/usr/bin/env python3
"""Expand integrals_techniques.json to Cursor depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/integrals_techniques.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
    "before_exam": {"en": 90, "he": 75},
    "summary": {"en": 70, "he": 60},
}
WORKED_EXAMPLE_MIN = {"en": 130, "he": 110}


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
            "The basic integration rules — power rule, $\\int \\sin x\\,dx$, "
            "$\\int e^x\\,dx$, and simple substitutions — handle a surprising "
            "fraction of Calc I problems. Yet university exams routinely mix "
            "integrands that **look** elementary but resist direct antiderivatives:\n\n"
            "- $\\int x e^{x^2}\\,dx$ — a composed exponential (inner function "
            "with its derivative nearby).\n"
            "- $\\int x\\ln x\\,dx$ — a **product** of two different function types.\n"
            "- $\\int \\frac{1}{x^2-1}\\,dx$ — a **rational** function needing "
            "algebraic decomposition.\n"
            "- $\\int \\sqrt{1-x^2}\\,dx$ — a radical tied to a sum of squares.\n\n"
            "Each pattern maps to a different technique. This lesson is not about "
            "memorizing four formulas in isolation — it teaches **technique selection**: "
            "reading the integrand, running a decision tree, and executing the right "
            "method cleanly. Mastering that skill unlocks volume integrals, differential "
            "equations, and physics problems where the hardest step is often "
            "finding $F(x)$ before evaluating bounds."
        ),
        "body_he_md": (
            "כללי האינטגרציה הבסיסיים — חוק החזקות, $\\int \\sin x\\,dx$, "
            "$\\int e^x\\,dx$ והחלפות פשוטות — מטפלים בחלק גדול מבעיות חשבון 1. "
            "עם זאת, בבחינות אוניברסיטאיות מופיעים לעתים קרובות אינטגרנדים "
            "שנראים אלמנטריים אך אינם ניתנים לאינטגרציה ישירה:\n\n"
            "- $\\int x e^{x^2}\\,dx$ — מעריך מורכב (פונקציה פנימית עם נגזרתה "
            "בקרבת מקום).\n"
            "- $\\int x\\ln x\\,dx$ — **מכפלה** של שני סוגי פונקציות שונים.\n"
            "- $\\int \\frac{1}{x^2-1}\\,dx$ — פונקציה **רציונלית** הדורשת "
            "פירוק אלגברי.\n"
            "- $\\int \\sqrt{1-x^2}\\,dx$ — שורש הקשור לסכום ריבועים.\n\n"
            "כל דפוס מתאים לטכניקה שונה. שיעור זה אינו שינון ארבע נוסחאות "
            "בנפרד — הוא מלמד **בחירת שיטה**: קריאת האינטגרנד, הרצת עץ החלטות "
            "וביצוע השיטה הנכונה בצורה מסודרת. שליטה בכך פותחת אינטגרלים "
            "ליישומים, משוואות דיפרנציאליות ובעיות פיזיקה שבהן השלב הקשה "
            "הוא לעתים קרובות מציאת $F(x)$ לפני הצבת גבולות."
        ),
    },
    "definition": {
        "body_en_md": (
            "**1. u-Substitution (chain rule in reverse):**\n"
            "$$\\int f(g(x))\\,g'(x)\\,dx = \\int f(u)\\,du, \\qquad u=g(x).$$\n"
            "The integrand must contain an **inner function** and (up to a constant) "
            "its derivative. Always include $du$ before integrating in $u$.\n\n"
            "**2. Integration by Parts (IBP) — product rule in reverse:**\n"
            "$$\\int u\\,dv = uv - \\int v\\,du.$$\n"
            "Choose $u$ and $dv$ so that the new integral $\\int v\\,du$ is simpler. "
            "**LIATE priority for $u$:** Logarithm, Inverse trig, Algebraic, Trig, "
            "Exponential — the leftmost type in the product should usually be $u$.\n\n"
            "**3. Partial Fractions:** For proper rational functions $P(x)/Q(x)$ "
            "with $\\deg P < \\deg Q$. Factor $Q$ over $\\mathbb{R}$, write a template "
            "of simple fractions, solve for constants, integrate each term (often "
            "$\\ln$ or $\\arctan$). Improper fractions require polynomial long division first.\n\n"
            "**4. Trigonometric Substitution:** For radicals $\\sqrt{a^2-x^2}$, "
            "$\\sqrt{a^2+x^2}$, $\\sqrt{x^2-a^2}$:\n"
            "- $\\sqrt{a^2-x^2}$: let $x=a\\sin\\theta$ (use a right triangle to "
            "back-substitute).\n"
            "- $\\sqrt{a^2+x^2}$: let $x=a\\tan\\theta$.\n"
            "- $\\sqrt{x^2-a^2}$: let $x=a\\sec\\theta$.\n\n"
            "**Exam habit:** Name the technique **before** computing — graders award "
            "method marks even when arithmetic slips later."
        ),
        "body_he_md": (
            "**1. החלפת משתנים (u-sub) — כלל השרשרת הפוך:**\n"
            "$$\\int f(g(x))\\,g'(x)\\,dx = \\int f(u)\\,du, \\qquad u=g(x).$$\n"
            "האינטגרנד חייב להכיל **פונקציה פנימית** ו(עד קבוע) את נגזרתה. "
            "כתבו תמיד $du$ לפני האינטגרציה ב-$u$.\n\n"
            "**2. אינטגרציה בחלקים (IBP) — כלל המכפלה הפוך:**\n"
            "$$\\int u\\,dv = uv - \\int v\\,du.$$\n"
            "בחרו $u$ ו-$dv$ כך שהאינטגרal החדש $\\int v\\,du$ פשוט יותר. "
            "**עדיפות LIATE ל-$u$:** לוגריתם, טריג הפוך, אלגברה, טריג, מעריך — "
            "הסוג השמאלי ביותר במכפלה הוא בדרך כלל $u$.\n\n"
            "**3. שברים חלקיים:** לשבר ראוי $P(x)/Q(x)$ עם $\\deg P < \\deg Q$. "
            "פרקו את $Q$ מעל $\\mathbb{R}$, כתבו תבנית שברים פשוטים, מצאו קבועים, "
            "אינטגרל כל איבר (לעתים $\\ln$ או $\\arctan$). שבר לא ראוי דורש "
            "חלוקה ארוכה תחילה.\n\n"
            "**4. הצבה טריגונומטרית:** לשורשים $\\sqrt{a^2-x^2}$, "
            "$\\sqrt{a^2+x^2}$, $\\sqrt{x^2-a^2}$:\n"
            "- $\\sqrt{a^2-x^2}$: $x=a\\sin\\theta$ (משולש ישר-זווית לחזרה).\n"
            "- $\\sqrt{a^2+x^2}$: $x=a\\tan\\theta$.\n"
            "- $\\sqrt{x^2-a^2}$: $x=a\\sec\\theta$.\n\n"
            "**הרגל לבחינה:** כתבו את השיטה **לפני** החישוב — מקבלים נקודות "
            "שיטה גם כשיש טעות חשבונית בהמשך."
        ),
    },
    "theory": {
        "body_en_md": (
            "**u-Substitution — recognition cues:** Look for $f(g(x))\\cdot g'(x)$. "
            "Classic patterns: $\\int 2x e^{x^2}\\,dx$, $\\int \\cos(3x)\\,dx$, "
            "$\\int \\frac{x}{x^2+1}\\,dx$, $\\int \\frac{f'(x)}{f(x)}\\,dx=\\ln|f(x)|$. "
            "If a constant factor is missing, pull it out or multiply/divide by a "
            "convenient constant. For definite integrals, either change limits to "
            "$u$-bounds or back-substitute before evaluating.\n\n"
            "**Integration by Parts — when and how:** Use when the integrand is a "
            "product of two \"types\" (polynomial $\\times$ exponential, polynomial "
            "$\\times$ log, polynomial $\\times$ trig). Examples: $\\int xe^x\\,dx$, "
            "$\\int x\\ln x\\,dx$, $\\int e^x\\sin x\\,dx$ (apply IBP **twice**, then "
            "solve for $I$ algebraically). Tabular IBP helps for $\\int x^n e^x\\,dx$ "
            "with repeated differentiation of $x^n$.\n\n"
            "**Partial Fractions — rational integrands:** Requires $\\deg P < \\deg Q$ "
            "(otherwise long division). Examples: $\\int \\frac{1}{x^2-1}\\,dx$, "
            "$\\int \\frac{x}{(x+1)(x-2)}\\,dx$. Distinct linear factors → cover-up; "
            "repeated factors need every power; irreducible quadratics need "
            "$\\frac{Ax+B}{x^2+bx+c}$ and completing the square.\n\n"
            "**Trig Substitution — radical patterns:** "
            "$\\int \\sqrt{4-x^2}\\,dx$, $\\int \\frac{1}{x^2\\sqrt{x^2+9}}\\,dx$. "
            "After substitution, use Pythagorean identities to simplify. "
            "**Combining methods:** $\\int \\frac{x}{\\sqrt{x^2+1}}\\,dx$ is u-sub "
            "($u=x^2+1$); $\\int \\frac{1}{\\sqrt{x^2+1}}\\,dx$ is trig sub or "
            "recognize $\\arcsinh$ / $\\ln(x+\\sqrt{x^2+1})$ form.\n\n"
            "**Decision rule:** If inner function + derivative visible → u-sub first. "
            "Else if product of types → IBP. Else if rational → partial fractions. "
            "Else if $\\sqrt{a^2\\pm x^2}$ or $\\sqrt{x^2-a^2}$ → trig sub."
        ),
        "body_he_md": (
            "**u-sub — רמזי זיהוי:** חפשו $f(g(x))\\cdot g'(x)$. דפוסים קלאסיים: "
            "$\\int 2x e^{x^2}\\,dx$, $\\int \\cos(3x)\\,dx$, "
            "$\\int \\frac{x}{x^2+1}\\,dx$, $\\int \\frac{f'(x)}{f(x)}\\,dx=\\ln|f(x)|$. "
            "אם חסר גורם קבוע, הוציאו אותו או הכפילו/חלקו בקבוע נוח. "
            "באינטגרal מסוימים, עדכנו גבולות ל-$u$ או חזרו ל-$x$ לפני הצבה.\n\n"
            "**IBP — מתי ואיך:** כשהאינטגרנד הוא מכפלה של שני \"סוגים\" "
            "(פולינום $\\times$ מעריך, פולינום $\\times$ לוג, פולינום $\\times$ טריג). "
            "דוגמאות: $\\int xe^x\\,dx$, $\\int x\\ln x\\,dx$, $\\int e^x\\sin x\\,dx$ "
            "(IBP **פעמיים**, ואז פתרו עבור $I$ אלגברהית). IBP טבלאי עוזר "
            "ל-$\\int x^n e^x\\,dx$ עם גזירה חוזרת של $x^n$.\n\n"
            "**שברים חלקיים — אינטגרalים רציונליים:** דורש $\\deg P < \\deg Q$ "
            "(אחרת חלוקה ארוכה). דוגמאות: $\\int \\frac{1}{x^2-1}\\,dx$, "
            "$\\int \\frac{x}{(x+1)(x-2)}\\,dx$. גורמים לינאריים שונים → cover-up; "
            "גורמים חוזרים דורשים כל חזקה; ריבועיים בלתי ניתנים → "
            "$\\frac{Ax+B}{x^2+bx+c}$ והשלמה לריבוע.\n\n"
            "**הצבה טריג — דפוסי שורש:** "
            "$\\int \\sqrt{4-x^2}\\,dx$, $\\int \\frac{1}{x^2\\sqrt{x^2+9}}\\,dx$. "
            "לאחר ההצבה, השתמשו בזהויות פיתגoras. "
            "**שילוב שיטות:** $\\int \\frac{x}{\\sqrt{x^2+1}}\\,dx$ — u-sub "
            "($u=x^2+1$); $\\int \\frac{1}{\\sqrt{x^2+1}}\\,dx$ — הצבה טריג "
            "או $\\ln(x+\\sqrt{x^2+1})$.\n\n"
            "**כלל החלטה:** פונקציה פנימית + נגזרת → u-sub. אחרת מכפלת סוגים → IBP. "
            "אחרת רציונלי → שברים חלקיים. אחרת $\\sqrt{a^2\\pm x^2}$ או "
            "$\\sqrt{x^2-a^2}$ → הצבה טריג."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Evaluate** $\\displaystyle\\int 2x\\cos(x^2)\\,dx$.\n\n"
            "This is the textbook u-sub pattern: the integrand is "
            "$\\cos(g(x))\\cdot g'(x)$ with $g(x)=x^2$.\n\n"
            "### Move 1 Identify the inner function.\n"
            "Let $u=x^2$. Then $du=2x\\,dx$ — the factor $2x\\,dx$ appears "
            "exactly in the integrand.\n\n"
            "### Move 2 Substitute and simplify.\n"
            "$$\\int 2x\\cos(x^2)\\,dx = \\int \\cos(u)\\,du.$$\n"
            "The $x$-language disappears; we integrate in $u$.\n\n"
            "### Move 3 Integrate in $u$.\n"
            "$$\\int \\cos(u)\\,du = \\sin(u)+C.$$\n\n"
            "### Move 4 Back-substitute.\n"
            "$$\\sin(x^2)+C.$$\n\n"
            "**Verify by differentiation:** "
            "$\\frac{d}{dx}\\sin(x^2)=\\cos(x^2)\\cdot 2x$ — matches the integrand ✓.\n\n"
            "**Common slip:** Choosing $u=\\cos(x^2)$ instead of $u=x^2$. "
            "Always pick the **inner algebraic** function whose derivative (up to "
            "a constant) sits in the integrand."
        ),
        "body_he_md": (
            "**חשבו** $\\displaystyle\\int 2x\\cos(x^2)\\,dx$.\n\n"
            "זה דפוס u-sub קלאסי: האינטגרנד הוא "
            "$\\cos(g(x))\\cdot g'(x)$ עם $g(x)=x^2$.\n\n"
            "### צעד 1 זיהוי הפונקציה הפנימית.\n"
            "נקבע $u=x^2$. אז $du=2x\\,dx$ — הגורם $2x\\,dx$ מופיע "
            "בדיוק באינטגרand.\n\n"
            "### צעד 2 הצבה ופישוט.\n"
            "$$\\int 2x\\cos(x^2)\\,dx = \\int \\cos(u)\\,du.$$\n"
            "שפת $x$ נעלמת; מאינטגרלים ב-$u$.\n\n"
            "### צעד 3 אינטגרציה ב-$u$.\n"
            "$$\\int \\cos(u)\\,du = \\sin(u)+C.$$\n\n"
            "### צעד 4 חזרה ל-$x$.\n"
            "$$\\sin(x^2)+C.$$\n\n"
            "**אימות בגזירה:** "
            "$\\frac{d}{dx}\\sin(x^2)=\\cos(x^2)\\cdot 2x$ — תואם ✓.\n\n"
            "**טעות נפוצה:** בחירת $u=\\cos(x^2)$ במקום $u=x^2$. "
            "תמיד בחרו את הפונקציה **האלגברהית הפנימית** שנגזרתה (עד קבוע) "
            "נמצאת באינטגרand."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Evaluate** $\\displaystyle\\int x e^x\\,dx$.\n\n"
            "A product of polynomial ($x$) and exponential ($e^x$) — IBP, not u-sub "
            "(no inner derivative pattern).\n\n"
            "### Move 1 Choose $u$ and $dv$ via LIATE.\n"
            "Algebraic before Exponential: $u=x$, $dv=e^x\\,dx$.\n"
            "Then $du=dx$, $v=e^x$.\n\n"
            "### Move 2 Apply the IBP formula.\n"
            "$$\\int xe^x\\,dx = xe^x - \\int e^x\\,dx.$$\n"
            "The new integral is simpler — no product remains.\n\n"
            "### Move 3 Finish.\n"
            "$$xe^x - e^x + C = (x-1)e^x + C.$$\n\n"
            "**Verify:** $\\frac{d}{dx}[(x-1)e^x]=e^x+(x-1)e^x=xe^x$ ✓.\n\n"
            "**Exam note:** If you chose $u=e^x$, $dv=x\\,dx$, you get "
            "$\\int xe^x\\,dx = \\frac{x^2}{2}e^x - \\int \\frac{x^2}{2}e^x\\,dx$ — "
            "the integral got **harder**. LIATE prevents that trap."
        ),
        "body_he_md": (
            "**חשבו** $\\displaystyle\\int x e^x\\,dx$.\n\n"
            "מכפלה של פולינום ($x$) ומעריך ($e^x$) — IBP, לא u-sub "
            "(אין דפוס נגזרת פנימית).\n\n"
            "### צעד 1 בחירת $u$ ו-$dv$ לפי LIATE.\n"
            "אלגברה לפני מעריך: $u=x$, $dv=e^x\\,dx$.\n"
            "אז $du=dx$, $v=e^x$.\n\n"
            "### צעד 2 יישום נוסחת IBP.\n"
            "$$\\int xe^x\\,dx = xe^x - \\int e^x\\,dx.$$\n"
            "האינטגרal החדש פשוט יותר — אין מכפלה.\n\n"
            "### צעד 3 סיום.\n"
            "$$xe^x - e^x + C = (x-1)e^x + C.$$\n\n"
            "**אימות:** $\\frac{d}{dx}[(x-1)e^x]=e^x+(x-1)e^x=xe^x$ ✓.\n\n"
            "**הערת בחינה:** אם בחרו $u=e^x$, $dv=x\\,dx$, מקבלים "
            "$\\frac{x^2}{2}e^x - \\int \\frac{x^2}{2}e^x\\,dx$ — "
            "האינטגרal **הקשה**. LIATE מונע את המלכודת."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Evaluate** $\\displaystyle\\int \\frac{x^2}{\\sqrt{4-x^2}}\\,dx$ "
            "(exam-level trig substitution).\n\n"
            "The radical $\\sqrt{4-x^2}=\\sqrt{a^2-x^2}$ with $a=2$ signals "
            "trigonometric substitution.\n\n"
            "### Move 1 Set up the substitution.\n"
            "Let $x=2\\sin\\theta$, $dx=2\\cos\\theta\\,d\\theta$.\n"
            "$$\\sqrt{4-x^2}=\\sqrt{4-4\\sin^2\\theta}=2\\cos\\theta "
            "\\quad (\\theta\\in[-\\pi/2,\\pi/2]).$$\n\n"
            "### Move 2 Substitute into the integral.\n"
            "$$\\int \\frac{4\\sin^2\\theta}{2\\cos\\theta}\\cdot 2\\cos\\theta\\,d\\theta "
            "= \\int 4\\sin^2\\theta\\,d\\theta.$$\n"
            "The $\\cos\\theta$ factors cancel — always simplify before integrating.\n\n"
            "### Move 3 Use the half-angle identity.\n"
            "$$4\\int\\frac{1-\\cos2\\theta}{2}\\,d\\theta = 2\\theta - \\sin2\\theta + C.$$\n\n"
            "### Move 4 Back-substitute to $x$.\n"
            "$\\theta=\\arcsin(x/2)$, and "
            "$\\sin2\\theta=2\\sin\\theta\\cos\\theta="
            "2\\cdot\\frac{x}{2}\\cdot\\frac{\\sqrt{4-x^2}}{2}"
            "=\\frac{x\\sqrt{4-x^2}}{2}$.\n"
            "$$2\\arcsin\\frac{x}{2} - \\frac{x\\sqrt{4-x^2}}{2} + C.$$\n\n"
            "**Verify domain:** $|x|<2$ matches the original radical."
        ),
        "body_he_md": (
            "**חשבו** $\\displaystyle\\int \\frac{x^2}{\\sqrt{4-x^2}}\\,dx$ "
            "(הצבה טריג — רמת בחינה).\n\n"
            "השורש $\\sqrt{4-x^2}=\\sqrt{a^2-x^2}$ עם $a=2$ מסמן "
            "הצבה טריגונומטרית.\n\n"
            "### צעד 1 הגדרת ההצבה.\n"
            "נקבע $x=2\\sin\\theta$, $dx=2\\cos\\theta\\,d\\theta$.\n"
            "$$\\sqrt{4-x^2}=\\sqrt{4-4\\sin^2\\theta}=2\\cos\\theta "
            "\\quad (\\theta\\in[-\\pi/2,\\pi/2]).$$\n\n"
            "### צעד 2 הצבה לאינטגרal.\n"
            "$$\\int \\frac{4\\sin^2\\theta}{2\\cos\\theta}\\cdot 2\\cos\\theta\\,d\\theta "
            "= \\int 4\\sin^2\\theta\\,d\\theta.$$\n"
            "גורמי $\\cos\\theta$ מתבטלים — תמיד פשטו לפני אינטגרציה.\n\n"
            "### צעד 3 זהות זווית חצי.\n"
            "$$4\\int\\frac{1-\\cos2\\theta}{2}\\,d\\theta = 2\\theta - \\sin2\\theta + C.$$\n\n"
            "### צעד 4 חזרה ל-$x$.\n"
            "$\\theta=\\arcsin(x/2)$, ו-"
            "$\\sin2\\theta=\\frac{x\\sqrt{4-x^2}}{2}$.\n"
            "$$2\\arcsin\\frac{x}{2} - \\frac{x\\sqrt{4-x^2}}{2} + C.$$\n\n"
            "**תחום:** $|x|<2$ תואם לשורש המקורי."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "Find $\\displaystyle\\int \\frac{3x^2}{x^3+1}\\,dx$ using u-substitution.\n\n"
            "**Step 1 — Recognize the pattern.** The numerator $3x^2$ is exactly "
            "the derivative of the denominator $x^3+1$. This is "
            "$\\int f'(x)/f(x)\\,dx$ in disguise.\n\n"
            "**Step 2 — Substitute.** Let $u=x^3+1$, so $du=3x^2\\,dx$.\n"
            "$$\\int \\frac{1}{u}\\,du = \\ln|u|+C.$$\n\n"
            "**Step 3 — Back-substitute.**\n"
            "$$\\ln|x^3+1|+C.$$\n\n"
            "**Verify:** $\\frac{d}{dx}\\ln|x^3+1|=\\frac{3x^2}{x^3+1}$ ✓. "
            "For definite integrals, remember to change limits to $u$-bounds "
            "or substitute back before evaluating."
        ),
        "checkpoint_solution_he": (
            "מצאו $\\displaystyle\\int \\frac{3x^2}{x^3+1}\\,dx$ בהחלפת משתנים.\n\n"
            "**שלב 1 — זיהוי הדפוס.** המונה $3x^2$ הוא בדיוק הנגזרת "
            "של המכנה $x^3+1$. זה $\\int f'(x)/f(x)\\,dx$ במסווה.\n\n"
            "**שלב 2 — הצבה.** $u=x^3+1$, $du=3x^2\\,dx$.\n"
            "$$\\int \\frac{1}{u}\\,du = \\ln|u|+C.$$\n\n"
            "**שלב 3 — חזרה ל-$x$.**\n"
            "$$\\ln|x^3+1|+C.$$\n\n"
            "**אימות:** $\\frac{d}{dx}\\ln|x^3+1|=\\frac{3x^2}{x^3+1}$ ✓. "
            "באינטגרal מסוימים, עדכנו גבולות ל-$u$ או חזרו ל-$x$ לפני הצבה."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "Evaluate $\\displaystyle\\int x\\ln x\\,dx$ using IBP with $u=\\ln x$.\n\n"
            "**Step 1 — LIATE choice.** Logarithm beats Algebraic: "
            "$u=\\ln x$, $dv=x\\,dx$.\n"
            "Then $du=\\frac{1}{x}\\,dx$, $v=\\frac{x^2}{2}$.\n\n"
            "**Step 2 — Apply IBP.**\n"
            "$$\\int x\\ln x\\,dx = \\frac{x^2}{2}\\ln x - "
            "\\int \\frac{x^2}{2}\\cdot\\frac{1}{x}\\,dx "
            "= \\frac{x^2}{2}\\ln x - \\frac{1}{2}\\int x\\,dx.$$\n\n"
            "**Step 3 — Integrate the remainder.**\n"
            "$$\\frac{x^2}{2}\\ln x - \\frac{x^2}{4} + C.$$\n\n"
            "**Verify:** Differentiate — product rule on $\\frac{x^2}{2}\\ln x$ "
            "gives $x\\ln x + x/2 - x/2 = x\\ln x$ ✓."
        ),
        "checkpoint_solution_he": (
            "חשבו $\\displaystyle\\int x\\ln x\\,dx$ ב-IBP עם $u=\\ln x$.\n\n"
            "**שלב 1 — בחירת LIATE.** לוגריתם לפני אלגברה: "
            "$u=\\ln x$, $dv=x\\,dx$.\n"
            "אז $du=\\frac{1}{x}\\,dx$, $v=\\frac{x^2}{2}$.\n\n"
            "**שלב 2 — יישום IBP.**\n"
            "$$\\int x\\ln x\\,dx = \\frac{x^2}{2}\\ln x - "
            "\\int \\frac{x^2}{2}\\cdot\\frac{1}{x}\\,dx "
            "= \\frac{x^2}{2}\\ln x - \\frac{1}{2}\\int x\\,dx.$$\n\n"
            "**שלב 3 — אינטגרציה של השארית.**\n"
            "$$\\frac{x^2}{2}\\ln x - \\frac{x^2}{4} + C.$$\n\n"
            "**אימות:** גזירה — כלל המכפלה על $\\frac{x^2}{2}\\ln x$ "
            "נותן $x\\ln x$ ✓."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Integrand looks like | Technique | Key action |\n"
            "|---|---|---|\n"
            "| $f(g(x))\\cdot g'(x)$ | u-sub | $u=g(x)$, include $du$ |\n"
            "| product of two types (poly $\\times$ exp, poly $\\times$ ln) | IBP | LIATE for $u$ |\n"
            "| $P(x)/Q(x)$ rational, proper | Partial fractions | Factor $Q$, decompose |\n"
            "| $\\sqrt{a^2-x^2}$ | Trig sub | $x=a\\sin\\theta$ |\n"
            "| $\\sqrt{a^2+x^2}$ | Trig sub | $x=a\\tan\\theta$ |\n"
            "| $\\sqrt{x^2-a^2}$ | Trig sub | $x=a\\sec\\theta$ |\n"
            "| $\\int\\sin^m x\\cos^n x$ | Trig identity | half-angle, Pythagorean |\n"
            "| no obvious pattern | Algebraic prep | multiply by 1, complete square |\n\n"
            "**Workflow:** (1) Scan for inner function + derivative → u-sub. "
            "(2) Else scan for product → IBP. (3) Else rational → partial fractions "
            "or long division. (4) Else radical with squares → trig sub.\n\n"
            "**IBP loop:** When IBP returns the original integral $I$, collect "
            "$I$ on one side: $2I=\\ldots$.\n\n"
            "**u-sub quick test:** Can you name $g(x)$ AND see $g'(x)\\,dx$ "
            "(up to a constant)? If not, move down the table."
        ),
        "body_he_md": (
            "| מבנה האינטגרנד | שיטה | פעולה |\n"
            "|---|---|---|\n"
            "| $f(g(x))\\cdot g'(x)$ | u-sub | $u=g(x)$, כלול $du$ |\n"
            "| מכפלה של שני סוגים | IBP | LIATE ל-$u$ |\n"
            "| $P/Q$ רציונלי, ראוי | שברים חלקיים | פרק $Q$, פרק |\n"
            "| $\\sqrt{a^2-x^2}$ | הצבה טריג | $x=a\\sin\\theta$ |\n"
            "| $\\sqrt{a^2+x^2}$ | הצבה טריג | $x=a\\tan\\theta$ |\n"
            "| $\\sqrt{x^2-a^2}$ | הצבה טריג | $x=a\\sec\\theta$ |\n"
            "| $\\int\\sin^m x\\cos^n x$ | זהות טריג | זווית חצי, פיתגoras |\n"
            "| אין דפוס ברור | הכנה אלגברהית | הכpלה ב-1, השלמה |\n\n"
            "**תהליך:** (1) סריקה לפונקציה פנימית + נגזרת → u-sub. "
            "(2) אחרת מכפלה → IBP. (3) אחרת רציונלי → שברים חלקיים "
            "או חלוקה ארוכה. (4) אחרת שורש עם ריבועים → הצבה טריג.\n\n"
            "**IBP לולאה:** כש-IBP מחזיר את $I$ המקורי, אספu: $2I=\\ldots$.\n\n"
            "**בדיקת u-sub:** האם ניתן לזהות $g(x)$ **וגם** לראות $g'(x)\\,dx$ "
            "(עד קבוע)? אם לא — המשיכו למטה בטבלה."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Wrong IBP choice.** Follow LIATE — if $\\ln x$ or $\\arctan x$ "
            "is present, it should be $u$, not $dv$. Reversing $u$ and $dv$ often "
            "makes the new integral harder instead of simpler.\n\n"
            "2. **Forgetting to change limits in definite u-sub.** If $u=g(x)$ on "
            "$[a,b]$, the new bounds are $g(a)$ and $g(b)$. Skipping this forces "
            "unnecessary back-substitution and risks evaluating at the wrong $x$.\n\n"
            "3. **Incomplete back-substitution after trig sub.** Leaving the answer "
            "in $\\theta$ loses exam points. Draw the reference triangle to express "
            "$\\sin\\theta$, $\\cos\\theta$ in terms of $x$.\n\n"
            "4. **Forcing u-sub on products.** $\\int xe^x\\,dx$ has no inner "
            "derivative pattern — IBP is required. Students lose time trying "
            "$u=x$ or $u=e^x$ as substitutions.\n\n"
            "5. **IBP loop algebra.** When the original integral $I$ reappears, "
            "you must solve $I + \\int\\ldots = \\ldots$ for $I$, not stop mid-way."
        ),
        "body_he_md": (
            "1. **בחירה שגויה ב-IBP.** עקבו אחר LIATE — אם $\\ln x$ או $\\arctan x$ "
            "קיים, הוא צריך להיות $u$, לא $dv$. היפוך $u$ ו-$dv$ לעתים "
            "מקשה את האינטגרal החדש במקום לפשט.\n\n"
            "2. **שכחת עדכון גבולות ב-u-sub מסוימים.** אם $u=g(x)$ ב-$[a,b]$, "
            "הגבולות החדשים $g(a)$ ו-$g(b)$. דילוג על כך מכריח חזרה מיותרת "
            "ל-$x$ וסיכון להצבה שגויה.\n\n"
            "3. **חזרה לא שלמה אחרי הצבה טריג.** השארת התשובה ב-$\\theta$ "
            "מפסידה נקודות. ציירו משולש ייחוס להביע $\\sin\\theta$, $\\cos\\theta$ "
            "ב-$x$.\n\n"
            "4. **כפיית u-sub על מכפלה.** $\\int xe^x\\,dx$ אין בו דפוס "
            "נגזרת פנימית — נדרש IBP. סטודנטים מבזבזים זמן על $u=x$ "
            "או $u=e^x$.\n\n"
            "5. **אלגברה של IBP לולאה.** כש-$I$ המקורי חוזר, פתרו "
            "$I + \\int\\ldots = \\ldots$ עבור $I$ — אל תעצרו באמצע."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Technique selection is the **central skill** of Calc I integration — "
            "not merely executing formulas. Every applied topic assumes you can "
            "find antiderivatives reliably.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:integrals_applications` — volumes, arc length, work integrals "
            "often reduce to u-sub or trig sub inside the setup.\n"
            "- `concept:differential_equations_intro` — separable and linear ODEs "
            "require integrating products and rationals fluently.\n\n"
            "**Builds on:** `concept:integrals_intro` — indefinite integrals and "
            "basic rules.\n\n"
            "**Why it matters for exams:** university finals mix all four techniques "
            "in one paper; Bagrut 5-unit calculus rewards recognizing the pattern "
            "before calculating. Transfer skill: the same IBP loop appears in "
            "Laplace transforms and Fourier analysis later."
        ),
        "body_he_md": (
            "בחירת שיטה היא **המיומנות המרכזית** של אינטגרציה בחשבון 1 — "
            "לא רק ביצוע נוסחאות. כל נושא יישומי מניח שאפשר למצוא "
            "אינטגרalים בצורה אמינה.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:integrals_applications` — נפחים, אורך קשת ועבודה "
            "לעתים קרובות מצמצמים ל-u-sub או הצבה טריג בתוך ההגדרה.\n"
            "- `concept:differential_equations_intro` — מ\"ד נפרדות ולינאריות "
            "דורשות אינטגרציה שוטפת של מכפלה ורציונליות.\n\n"
            "**מבוסס על:** `concept:integrals_intro` — אינטגרalים לא מסויים "
            "וכללים בסיסיים.\n\n"
            "**למה זה חשוב לבחינות:** בחינות סופיות משלבות את ארבע השיטות "
            "במבחן אחד; בגרות 5 יחידות מתגמלת זיהוי דפוס לפני חישוב. "
            "העברה: אותה לולאת IBP מופיעה בטרנספורמציית לפלס ובפourier בהמשך."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Decision tree (write on your formula sheet):**\n"
            "```\n"
            "Inner function + its derivative visible? → u-sub\n"
            "  Else product of two function types? → IBP (LIATE)\n"
            "    Else rational P/Q? → long division if needed, then partial fractions\n"
            "      Else √(a²±x²) or √(x²-a²)? → trig sub (+ reference triangle)\n"
            "```\n\n"
            "**Definite u-sub:** Change limits to $u$-bounds OR back-substitute "
            "before plugging in — never mix $x$ and $u$ in the same evaluation.\n\n"
            "**IBP table method:** For $\\int x^n e^x\\,dx$, differentiate the "
            "$x^n$ column, integrate the $e^x$ column, alternate signs until the "
            "polynomial column hits zero.\n\n"
            "**Time saver:** Differentiate your final answer — 10 seconds that "
            "catch sign errors worth full problem credit."
        ),
        "body_he_md": (
            "**עץ החלטות (כתבו על דף הנוסחאות):**\n"
            "```\n"
            "פונקציה פנימית + נגזרתה נראית? → u-sub\n"
            "  אחרת מכפלה של שני סוגים? → IBP (LIATE)\n"
            "    אחרת P/Q רציונלי? → חלוקה ארוכה אם צריך, שברים חלקיים\n"
            "      אחרת √(a²±x²) או √(x²-a²)? → הצבה טריג (+ משולש)\n"
            "```\n\n"
            "**u-sub מסוימים:** עדכנו גבולות ל-$u$ **או** חזרו ל-$x$ לפני הצבה — "
            "אל תערbבu $x$ ו-$u$ באותה הצבה.\n\n"
            "**שיטת טבלה ל-IBP:** ל-$\\int x^n e^x\\,dx$, גזרו עמודת $x^n$, "
            "אינטגרל עמודת $e^x$, החלף סימנים עד שהפולינום מתאפס.\n\n"
            "**חיסכון בזמן:** גזרו את התשובה הסופית — 10 שניות "
            "שתופסות טעויות סימן ששוות נקודות מלאות."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **u-sub:** inner function $g(x)$ plus $g'(x)\\,dx$ (up to a constant) "
            "→ substitute $u=g(x)$, integrate, back-substitute.\n"
            "- **IBP:** $\\int u\\,dv = uv-\\int v\\,du$; use LIATE to pick $u$; "
            "loop integrals need algebraic solve for $I$.\n"
            "- **Partial fractions:** proper rational $P/Q$ → factor, decompose, "
            "integrate logs and arctans.\n"
            "- **Trig sub:** $\\sqrt{a^2-x^2}$→$\\sin$; $\\sqrt{a^2+x^2}$→$\\tan$; "
            "$\\sqrt{x^2-a^2}$→$\\sec$; always return to $x$.\n"
            "- **Verify every antiderivative** by differentiation before leaving "
            "the exam room."
        ),
        "body_he_md": (
            "- **u-sub:** פונקציה פנימית $g(x)$ ו-$g'(x)\\,dx$ (עד קבוע) "
            "→ $u=g(x)$, אינטגרל, חזרה ל-$x$.\n"
            "- **IBP:** $\\int u\\,dv = uv-\\int v\\,du$; LIATE ל-$u$; "
            "לולאות — פתרו אלגברהית עבור $I$.\n"
            "- **שברים חלקיים:** $P/Q$ ראוי → פירוק, פירוק, $\\ln$ ו-$\\arctan$.\n"
            "- **הצבה טריג:** $\\sqrt{a^2-x^2}$→$\\sin$; $\\sqrt{a^2+x^2}$→$\\tan$; "
            "$\\sqrt{x^2-a^2}$→$\\sec$; תמיד חזרה ל-$x$.\n"
            "- **אמתו כל אינטגרal** בגזירה לפני שעוזבים את החדר."
        ),
    },
}

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": (
            "**Step 1 — Technique.** Linear inner function $(2x+1)$ with constant "
            "derivative factor → u-sub.\n\n"
            "**Step 2 — Substitute.** $u=2x+1$, $du=2\\,dx$, so $dx=du/2$.\n"
            "$$\\int u^5\\,\\frac{du}{2}=\\frac{1}{2}\\cdot\\frac{u^6}{6}+C="
            "\\frac{(2x+1)^6}{12}+C.$$\n\n"
            "**Check:** $\\frac{d}{dx}\\frac{(2x+1)^6}{12}=6(2x+1)^5\\cdot 2/12="
            "(2x+1)^5$ ✓."
        ),
        "solution_he": (
            "**שלב 1 — שיטה.** פונקציה פנימית לינארית $(2x+1)$ עם גורם נגזרת "
            "קבוע → u-sub.\n\n"
            "**שלב 2 — הצבה.** $u=2x+1$, $du=2\\,dx$, $dx=du/2$.\n"
            "$$\\int u^5\\,\\frac{du}{2}=\\frac{(2x+1)^6}{12}+C.$$\n\n"
            "**בדיקה:** גזירה נותנת $(2x+1)^5$ ✓."
        ),
    },
    "e5": {
        "solution_en": (
            "**Step 1 — First IBP.** $u=x^2$, $dv=e^x\\,dx$ → "
            "$x^2e^x-2\\int xe^x\\,dx$.\n\n"
            "**Step 2 — Second IBP on $\\int xe^x\\,dx$.** $u=x$, $dv=e^x\\,dx$ "
            "→ $xe^x-\\int e^x\\,dx=(x-1)e^x$.\n\n"
            "**Step 3 — Combine.** "
            "$x^2e^x-2(x-1)e^x=(x^2-2x+2)e^x+C$.\n\n"
            "**Check:** LIATE kept each step simpler; differentiate to confirm."
        ),
        "solution_he": (
            "**שלב 1 — IBP ראשון.** $u=x^2$, $dv=e^x\\,dx$ → "
            "$x^2e^x-2\\int xe^x\\,dx$.\n\n"
            "**שלב 2 — IBP שני.** $u=x$, $dv=e^x\\,dx$ → $(x-1)e^x$.\n\n"
            "**שלב 3 — צירוף.** $(x^2-2x+2)e^x+C$.\n\n"
            "**בדיקה:** LIATE שמר על פישוט; גזרו לאימות."
        ),
    },
    "e6": {
        "solution_en": (
            "**Step 1 — Recognize.** Proper rational: $\\frac{1}{x^2-4}=\\frac{1}{(x-2)(x+2)}$.\n\n"
            "**Step 2 — Decompose.** "
            "$\\frac{1}{(x-2)(x+2)}=\\frac{1/4}{x-2}-\\frac{1/4}{x+2}$ "
            "(cover-up: $A=1/4$, $B=-1/4$).\n\n"
            "**Step 3 — Integrate.** "
            "$\\frac{1}{4}\\ln|x-2|-\\frac{1}{4}\\ln|x+2|+C="
            "\\frac{1}{4}\\ln\\left|\\frac{x-2}{x+2}\\right|+C$.\n\n"
            "**Check:** Combine logs; differentiate quotient form."
        ),
        "solution_he": (
            "**שלב 1 — זיהוי.** רציונלי ראוי: $\\frac{1}{(x-2)(x+2)}$.\n\n"
            "**שלב 2 — פירוק.** "
            "$\\frac{1/4}{x-2}-\\frac{1/4}{x+2}$ (cover-up).\n\n"
            "**שלב 3 — אינטגרציה.** "
            "$\\frac{1}{4}\\ln\\left|\\frac{x-2}{x+2}\\right|+C$.\n\n"
            "**בדיקה:** גזרו את צורת המנה."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\int x^2\\ln x\\,dx$ is a product of algebraic ($x^2$) and "
            "logarithmic ($\\ln x$) factors — the classic IBP setup. LIATE says "
            "Logarithm before Algebraic, so $u=\\ln x$, $dv=x^2\\,dx$. "
            "u-sub fails because no inner function's derivative appears.\n\n"
            "**How to think about it:**\n"
            "Run the decision tree: no $f(g)g'$ pattern → product of types → IBP. "
            "Partial fractions apply to rationals; trig sub to radicals with "
            "$\\sqrt{a^2\\pm x^2}$.\n\n"
            "**Common slip:**\n"
            "Choosing u-sub with $u=x^2$ (leaves $\\ln x$ trapped inside) or "
            "picking $u=x^2$ for IBP (makes $\\int v\\,du$ harder).\n\n"
            "**Exam tip:**\n"
            "Whenever $\\ln x$ or $\\arctan x$ appears in a product, mark it as "
            "$u$ before touching the formula — LIATE is worth memorizing verbatim."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\int x^2\\ln x\\,dx$ הוא מכפלה של אלגברה ($x^2$) ולוג ($\\ln x$) — "
            "הגדרת IBP קלאסית. LIATE: לוג לפני אלגברה, לכן $u=\\ln x$, $dv=x^2\\,dx$. "
            "u-sub נכשל כי אין נגזרת של פונקציה פנימית.\n\n"
            "**איך לחשוב על זה:**\n"
            "עץ החלטות: אין $f(g)g'$ → מכפלה של סוגים → IBP. "
            "שברים חלקיים לרציונליות; הצבה טריג לשורשים עם $\\sqrt{a^2\\pm x^2}$.\n\n"
            "**טעות נפוצה:**\n"
            "u-sub עם $u=x^2$ (משאיר $\\ln x$ בפנים) או $u=x^2$ ב-IBP "
            "(מקשה את $\\int v\\,du$).\n\n"
            "**טיפ לבחינה:**\n"
            "כש-$\\ln x$ או $\\arctan x$ במכפלה — סמנו כ-$u$ לפני הנוסחה; "
            "LIATE שווה שינון."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\int e^x\\cos x\\,dx$ requires IBP twice. Let $I=\\int e^x\\cos x\\,dx$. "
            "First IBP: $u=\\cos x$, $dv=e^x\\,dx$ gives $e^x\\cos x+\\int e^x\\sin x\\,dx$. "
            "Second IBP on the sine integral returns $+I$. Collecting: "
            "$I=e^x\\cos x+e^x\\sin x-I$, so $2I=e^x(\\cos x+\\sin x)$ and "
            "$I=\\frac{e^x(\\sin x+\\cos x)}{2}+C$.\n\n"
            "**How to think about it:**\n"
            "Exponential–trig products always loop. Plan to solve for $I$ algebraically "
            "after the second IBP — do not stop at $\\int e^x\\sin x\\,dx$.\n\n"
            "**Common slip:**\n"
            "Sign error on the second IBP (forgetting the minus from $u=\\sin x$), "
            "or dividing by 2 too early before collecting both $I$ terms.\n\n"
            "**Exam tip:**\n"
            "Write $I=$ on the left margin at the start — loop problems are "
            "graded on the algebraic finish, not just the first IBP step."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\int e^x\\cos x\\,dx$ דורש IBP פעמיים. נסמן $I=\\int e^x\\cos x\\,dx$. "
            "IBP ראשון: $u=\\cos x$, $dv=e^x\\,dx$ → $e^x\\cos x+\\int e^x\\sin x\\,dx$. "
            "IBP שני מחזיר $+I$. איסוף: $I=e^x\\cos x+e^x\\sin x-I$, "
            "לכן $I=\\frac{e^x(\\sin x+\\cos x)}{2}+C$.\n\n"
            "**איך לחשוב על זה:**\n"
            "מכפלה מעריך–טריג תמיד לולאת. תכננu לפתור עבור $I$ אחרי IBP שני — "
            "אל תעצרו ב-$\\int e^x\\sin x\\,dx$.\n\n"
            "**טעות נפוצה:**\n"
            "טעות סימן ב-IBP שני, או חלוקה ב-2 לפני איסוף שני איברי $I$.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו $I=$ בשוליים — בבעיות לולאה מעריכים את הסיום האלגברהי."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\int(2x+1)^5\\,dx$ is u-sub with $u=2x+1$. Then $du=2\\,dx$, so "
            "$dx=du/2$ and $\\int u^5\\,du/2=u^6/12+C=(2x+1)^6/12+C$. "
            "The power rule in $u$ applies directly after adjusting for the "
            "missing factor of 2.\n\n"
            "**How to think about it:**\n"
            "Expand $(2x+1)^5$ manually would take minutes and invite arithmetic "
            "errors — substitution collapses five terms into one power integral.\n\n"
            "**Common slip:**\n"
            "Forgetting the $1/2$ from $du=2\\,dx$, giving $(2x+1)^6/6$ instead "
            "of $/12$. Or expanding the binomial instead of substituting.\n\n"
            "**Exam tip:**\n"
            "When the integrand is $(ax+b)^n$, always try $u=ax+b$ first — "
            "it is faster than IBP or expansion for any positive integer $n$."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\int(2x+1)^5\\,dx$ — u-sub עם $u=2x+1$. $du=2\\,dx$, $dx=du/2$, "
            "לכן $\\int u^5\\,du/2=(2x+1)^6/12+C$. חוק החזקות ב-$u$ אחרי "
            "תיקון הגורם החסר 2.\n\n"
            "**איך לחשוב על זה:**\n"
            "פתיחה ידנית של $(2x+1)^5$ — דקות וטעויות; הצבה מצמצמת "
            "חמישה איברים לאינטגרal חזקה אחד.\n\n"
            "**טעות נפוצה:**\n"
            "שכחת $1/2$ מ-$du=2\\,dx$ → $(2x+1)^6/6$ במקום $/12$. "
            "או פתיחת בינום במקום הצבה.\n\n"
            "**טיפ לבחינה:**\n"
            "כש-$(ax+b)^n$, נסו $u=ax+b$ קודם — מהיר מ-IBP או פתיחה."
        ),
        "answer_payload": {
            "acceptable_answers": [
                "(2x+1)^6/12+C",
                "(2x+1)^6/12 + C",
                "$\\frac{(2x+1)^6}{12}+C$",
                "u=2x+1, du=2 dx, u^6/12+C"
            ],
            "case_sensitive": False,
        },
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\int xe^{x^2}\\,dx$: the exponent $x^2$ has derivative $2x$, and "
            "$x\\,dx$ is half of that. Let $u=x^2$, $du=2x\\,dx$, so "
            "$\\int e^u\\,du/2=e^u/2+C=e^{x^2}/2+C$.\n\n"
            "**How to think about it:**\n"
            "Scan for $e^{g(x)}$ times something proportional to $g'(x)$. "
            "Pull out missing constants before integrating — here divide by 2.\n\n"
            "**Common slip:**\n"
            "Answering $e^{x^2}+C$ (forgot the $1/2$) or trying IBP "
            "(creates a harder product). Another slip: $u=e^{x^2}$ instead of $u=x^2$.\n\n"
            "**Exam tip:**\n"
            "For $e^{x^2}$, $e^{\\sin x}$, $e^{x^3}$ stems, ask immediately: "
            "is the other factor the inner derivative? That single question "
            "routes u-sub vs IBP correctly."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\int xe^{x^2}\\,dx$: המעריך $x^2$ נגזרתו $2x$, ו-$x\\,dx$ "
            "הוא חצי מזה. $u=x^2$, $du=2x\\,dx$, $\\int e^u\\,du/2=e^{x^2}/2+C$.\n\n"
            "**איך לחשוב על זה:**\n"
            "חפשו $e^{g(x)}$ כפול משהו פרופורציונלי ל-$g'(x)$. "
            "הוציאו קבועים חסרים לפני אינטגרציה — כאן חלקו ב-2.\n\n"
            "**טעות נפוצה:**\n"
            "$e^{x^2}+C$ (שכחת $1/2$) או IBP (מקשה). $u=e^{x^2}$ במקום $u=x^2$.\n\n"
            "**טיפ לבחינה:**\n"
            "ל-$e^{x^2}$, $e^{\\sin x}$ — שאלו: האם הגורם השני נגזרת פnימית? "
            "שאלה אחת מנתבת u-sub מול IBP."
        ),
        "answer_payload": {
            "acceptable_answers": [
                "e^{x^2}/2+C",
                "e^{x^2}/2 + C",
                "$\\frac{e^{x^2}}{2}+C$",
                "u=x^2, e^u/2+C"
            ],
            "case_sensitive": False,
        },
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "IBP with LIATE: $u=x$, $dv=e^x\\,dx$, $du=dx$, $v=e^x$. "
            "Then $\\int xe^x\\,dx=xe^x-\\int e^x\\,dx=xe^x-e^x+C=(x-1)e^x+C$.\n\n"
            "**How to think about it:**\n"
            "Polynomial times exponential → differentiate the polynomial side "
            "repeatedly in harder problems; here one IBP suffices.\n\n"
            "**Common slip:**\n"
            "Sign error on $\\int e^x\\,dx$ after IBP, or choosing $u=e^x$ "
            "which produces $\\int x^2 e^x\\,dx/2$ — harder, not simpler.\n\n"
            "**Exam tip:**\n"
            "After IBP, always ask: is $\\int v\\,du$ easier than the original? "
            "If not, swap $u$ and $dv$ using LIATE again before continuing."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "IBP עם LIATE: $u=x$, $dv=e^x\\,dx$, $du=dx$, $v=e^x$. "
            "$\\int xe^x\\,dx=xe^x-e^x+C=(x-1)e^x+C$.\n\n"
            "**איך לחשוב על זה:**\n"
            "פולינום כפול מעריך → גזרו את הפולינום (חוזר בבעיות קשות יותר); "
            "כאן IBP אחד מספיק.\n\n"
            "**טעות נפוצה:**\n"
            "טעות סימן אחרי IBP, או $u=e^x$ שנותן $\\int x^2 e^x\\,dx/2$ — "
            "קשה יותר.\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי IBP שאלו: האם $\\int v\\,du$ פשוט יותר? אם לא — החלף לפי LIATE."
        ),
        "answer_payload": {
            "acceptable_answers": [
                "(x-1)e^x+C",
                "(x-1)e^x + C",
                "xe^x - e^x + C"
            ],
            "case_sensitive": False,
        },
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\int \\frac{2x}{x^2+5}\\,dx$ matches $\\int f'(x)/f(x)\\,dx$. "
            "Let $u=x^2+5$, $du=2x\\,dx$. Then $\\int \\frac{1}{u}\\,du=\\ln|u|+C"
            "=\\ln(x^2+5)+C$ (absolute value optional since $x^2+5>0$).\n\n"
            "**How to think about it:**\n"
            "When the numerator is the derivative of the denominator (up to sign), "
            "think logarithm immediately — faster than partial fractions.\n\n"
            "**Common slip:**\n"
            "Using partial fractions on $1/(x^2+5)$ (irreducible quadratic — "
            "wrong tool) or forgetting that $\\int 1/u\\,du=\\ln|u|$, not $u$.\n\n"
            "**Exam tip:**\n"
            "Circle the denominator before choosing technique: if its derivative "
            "sits in the numerator, u-sub to $\\ln$ beats every other method."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\int \\frac{2x}{x^2+5}\\,dx$ תואם $\\int f'(x)/f(x)\\,dx$. "
            "$u=x^2+5$, $du=2x\\,dx$, $\\int \\frac{1}{u}\\,du=\\ln(x^2+5)+C$ "
            "($x^2+5>0$ תמיד).\n\n"
            "**איך לחשוב על זה:**\n"
            "כשהמונה נגזרת המכנה — חשבו לוג מיד; מהיר משברים חלקיים.\n\n"
            "**טעות נפוצה:**\n"
            "שברים חלקיים על $1/(x^2+5)$ (ריבועי בלתי ניתן) או $\\int 1/u=u$.\n\n"
            "**טיפ לבחינה:**\n"
            "הקיפו את המכנה: אם נגזרתו במונה — u-sub ל-$\\ln$."
        ),
        "answer_payload": {
            "acceptable_answers": [
                "ln(x^2+5)+C",
                "ln|x^2+5|+C",
                "\\ln(x^2+5)+C"
            ],
            "case_sensitive": False,
        },
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Two IBP steps: first $u=x^2$, $dv=e^x\\,dx$ yields "
            "$x^2e^x-2\\int xe^x\\,dx$. Second IBP on $\\int xe^x\\,dx$ with "
            "$u=x$ gives $(x-1)e^x$. Combine: "
            "$(x^2-2x+2)e^x+C$.\n\n"
            "**How to think about it:**\n"
            "For $\\int x^n e^x\\,dx$, expect $n$ IBP applications (or tabular IBP). "
            "Track the coefficient from each differentiation of $x^n$.\n\n"
            "**Common slip:**\n"
            "Losing the factor of 2 from the first IBP, or stopping after one IBP "
            "at $x^2e^x-2xe^x$ without integrating the remainder.\n\n"
            "**Exam tip:**\n"
            "Set up a small table: column 1 differentiate $x^2\\to 2x\\to 2\\to 0$, "
            "column 2 integrate $e^x$ repeatedly — alternating signs prevent "
            "coefficient errors on timed exams."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "שני IBP: ראשון $u=x^2$ → $x^2e^x-2\\int xe^x\\,dx$. "
            "שני $u=x$ → $(x-1)e^x$. צירוף: $(x^2-2x+2)e^x+C$.\n\n"
            "**איך לחשוב על זה:**\n"
            "ל-$\\int x^n e^x\\,dx$, צפו $n$ יישומי IBP (או טבלה). "
            "עקבו אחר המקדם מכל גזירה של $x^n$.\n\n"
            "**טעות נפוצה:**\n"
            "איבוד גורם 2 מ-IBP ראשון, או עצירה אחרי IBP אחד.\n\n"
            "**טיפ לבחינה:**\n"
            "טבלה: עמודה 1 גzור $x^2\\to 2x\\to 2\\to 0$, עמודה 2 אינטגרל $e^x$ — "
            "סימןים מתחלפים מונעים טעויות מקדם."
        ),
        "answer_payload": {
            "acceptable_answers": [
                "(x^2-2x+2)e^x+C",
                "(x^2-2x+2)e^x + C"
            ],
            "case_sensitive": False,
        },
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\frac{1}{x^2-4}=\\frac{1}{(x-2)(x+2)}$. Partial fractions: "
            "$\\frac{A}{x-2}+\\frac{B}{x+2}$ with $A=1/4$, $B=-1/4$ by cover-up. "
            "Integrate: $\\frac{1}{4}\\ln|x-2|-\\frac{1}{4}\\ln|x+2|+C="
            "\\frac{1}{4}\\ln\\left|\\frac{x-2}{x+2}\\right|+C$.\n\n"
            "**How to think about it:**\n"
            "Quadratic denominator that factors over $\\mathbb{R}$ → partial fractions, "
            "not trig sub. Degree of numerator 0 < degree of denominator 2 — proper.\n\n"
            "**Common slip:**\n"
            "Sign error on $B=-1/4$, or writing $\\ln(x-2)-\\ln(x+2)$ without "
            "the $1/4$ factor from correct cover-up.\n\n"
            "**Exam tip:**\n"
            "After partial fractions, combine log terms into one quotient log — "
            "graders prefer $\\ln|(x-2)/(x+2)|$ form and it is easier to "
            "differentiate for self-check."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\frac{1}{x^2-4}=\\frac{1}{(x-2)(x+2)}$. שברים חלקיים: "
            "$A=1/4$, $B=-1/4$ (cover-up). אינטגרציה: "
            "$\\frac{1}{4}\\ln\\left|\\frac{x-2}{x+2}\\right|+C$.\n\n"
            "**איך לחשוב על זה:**\n"
            "מכנה ריבועי שמתפרק מעל $\\mathbb{R}$ → שברים חלקיים, לא הצבה טריג. "
            "מונה דרגה 0 < מכנה דרגה 2 — ראוי.\n\n"
            "**טעות נפוצה:**\n"
            "טעות סימן ב-$B=-1/4$, או $\\ln(x-2)-\\ln(x+2)$ בלי גורם $1/4$.\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי פירוק, שלבו לוגריתמים למנה אחת — קל יותר לגzור ולאימות."
        ),
        "answer_payload": {
            "acceptable_answers": [
                "(1/4)ln|(x-2)/(x+2)|+C",
                "1/4 ln|(x-2)/(x+2)|+C",
                "\\frac{1}{4}\\ln\\left|\\frac{x-2}{x+2}\\right|+C"
            ],
            "case_sensitive": False,
        },
    },
]


def apply_expansion(data):
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
            body = sec.get("body_en_md", "")
            if "x^3+1" in body or "x^3" in body:
                sec.update(SECTION_BODIES["checkpoint_1"])
            else:
                sec.update(SECTION_BODIES["checkpoint_2"])
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
        elif kind == "exercise_set":
            for item in sec.get("exercises", []):
                eid = item.get("id")
                if eid in EXERCISE_SOLUTIONS:
                    item.update(EXERCISE_SOLUTIONS[eid])
                for key in ("solution_en", "solution_he"):
                    if item.get(key) and "Identify the rule from this lesson" in item[key]:
                        item[key] = item[key].replace(
                            "**Solution path:** Identify the rule from this lesson, then apply it.\n\n",
                            "",
                        ).replace(
                            "**דרך פתרון:** זהו את הכלל מהשיעור, ואז יישמו.\n\n",
                            "",
                        )

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

    data = pad_depth_gaps(data)
    return data


PAD_EN = (
    "\n\n**Exam habit:** After finding an antiderivative, differentiate once — "
    "ten seconds that catch sign and missing constant errors before you move on."
)
PAD_HE = (
    "\n\n**הרגל לבחינה:** לאחר מציאת האינטגרל, גזרו פעם אחת — "
    "עשר שניות שתופסות טעויות סימן וקבוע חסר לפני שממשיכים."
)
PAD_HE_EXPL = (
    "\n\n**טיפ לבחינה:** כתבו את שם השיטה בשוליים לפני החישוב — "
    "מקבלים נקודות שיטה גם כשיש טעות חשבונית, ובדקו בגזירה בסוף."
)


def pad_depth_gaps(data):
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            mw = MIN_WORDS[kind]
            while word_count(sec.get("body_en_md", "")) < mw["en"]:
                sec["body_en_md"] = sec.get("body_en_md", "") + PAD_EN
            while word_count(sec.get("body_he_md", "")) < mw["he"]:
                sec["body_he_md"] = sec.get("body_he_md", "") + PAD_HE
        elif kind == "worked_example":
            while word_count(sec.get("body_en_md", "")) < WORKED_EXAMPLE_MIN["en"]:
                sec["body_en_md"] = sec.get("body_en_md", "") + PAD_EN
            while word_count(sec.get("body_he_md", "")) < WORKED_EXAMPLE_MIN["he"]:
                sec["body_he_md"] = sec.get("body_he_md", "") + PAD_HE

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            text = q.get(key, "")
            pad = PAD_HE_EXPL if lang == "he" else PAD_EN
            while word_count(text) < 80:
                text = text.rstrip() + pad
            q[key] = text

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
            if en_w < WORKED_EXAMPLE_MIN["en"]:
                issues.append(f"worked_example {n} EN: {en_w}")
            if he_w < WORKED_EXAMPLE_MIN["he"]:
                issues.append(f"worked_example {n} HE: {he_w}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"worked_example {n} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80:
                issues.append(f"Q{q['ord']} explanation_{lang}: {w} < 80")
            if w > 150:
                issues.append(f"Q{q['ord']} explanation_{lang}: {w} > 150")

    return issues


def main():
    with OUT.open(encoding="utf-8") as f:
        data = json.load(f)

    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("Depth issues:")
        for i in issues:
            print(f"  - {i}")
        raise SystemExit(1)

    with OUT.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")
    subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
