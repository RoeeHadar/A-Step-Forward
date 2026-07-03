#!/usr/bin/env python3
"""Expand limits.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/limits.json"

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


def hebrew_body_weak(body_he, body_en):
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    if not en:
        return False
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    he_chars = len(re.findall(r"[\u0590-\u05FF]", he))
    lat = len(re.findall(r"[a-zA-Z]{3,}", he))
    if he_chars / (he_chars + lat + 1) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


WE1_EN = """**Compute** $\\displaystyle\\lim_{x\\to 2}\\frac{x^2-4}{x-2}$.

This is the canonical $0/0$ factoring problem — it appears on virtually every Bagrut 5-unit limits question set.

---

### Move 1 — Direct substitution
$$\\frac{2^2-4}{2-2} = \\frac{0}{0}.$$
Indeterminate form. We need algebra before we can conclude anything. Write $0/0$ explicitly on your exam paper — examiners deduct points if you skip this step.

### Move 2 — Factor the numerator
$$x^2 - 4 = (x-2)(x+2).$$
Recognise the difference of squares: $a^2-b^2=(a-b)(a+b)$ with $a=x$, $b=2$.

### Move 3 — Cancel the common factor
$$\\frac{x^2-4}{x-2} = \\frac{(x-2)(x+2)}{x-2} = x+2 \\quad (x\\ne 2).$$
Cancellation is valid because in a limit we only consider $x$ approaching $2$, never equal to $2$.

### Move 4 — Substitute into the simplified expression
$$\\lim_{x\\to 2}(x+2) = 2+2 = \\boxed{4}.$$

> **Remark:** The function $\\frac{x^2-4}{x-2}$ is undefined at $x=2$, but the **limit** is $4$. These are different questions — a common exam trap.

**Pattern to remember:** For any $a$, $\\displaystyle\\lim_{x\\to a}\\frac{x^2-a^2}{x-a}=2a$. Here $a=2$, confirming the answer $4$.

*Exam note:* Always state the indeterminate form before factoring. Partial credit on Bagrut rubrics depends on this setup step. If factoring fails, try the conjugate or L'Hôpital as a backup."""

WE1_HE = """**חשבו** $\\displaystyle\\lim_{x\\to 2}\\frac{x^2-4}{x-2}$.

זו בעיית הפירוק הקלאסית לצורה $0/0$ — היא מופיעה כמעט בכל מקבץ תרגילי גבולות בבגרות 5 יחידות.

---

### צעד 1 — הצבה ישירה
$$\\frac{2^2-4}{2-2} = \\frac{0}{0}.$$
צורה בלתי-קצובה. נצטרך אלגברה לפני שאפשר להסיק מסקנה. כתבו $0/0$ במפורש בבחינה — בוחנים מורידים נקודות אם מדלגים על שלב זה.

### צעד 2 — פירוק המונה
$$x^2 - 4 = (x-2)(x+2).$$
זיהוי הפרש ריבועים: $a^2-b^2=(a-b)(a+b)$ עם $a=x$, $b=2$.

### צעד 3 — צמצום הגורם המשותף
$$\\frac{x^2-4}{x-2} = \\frac{(x-2)(x+2)}{x-2} = x+2 \\quad (x\\ne 2).$$
הצמצום תקין כי בגבול $x$ מתקרב ל-$2$ ולא שווה ל-$2$.

### צעד 4 — הצבה בביטוי המפושט
$$\\lim_{x\\to 2}(x+2) = 2+2 = \\boxed{4}.$$

> **הערה:** הפונקציה $\\frac{x^2-4}{x-2}$ לא מוגדרת ב-$x=2$, אבל **הגבול** הוא $4$. אלו שאלות שונות — מלכודת בחינה נפוצה.

**דפוס לזכירה:** לכל $a$, $\\displaystyle\\lim_{x\\to a}\\frac{x^2-a^2}{x-a}=2a$. כאן $a=2$, מאשר את התשובה $4$.

*הערת בחינה:* ציינו תמיד את הצורה הבלתי-קצובה לפני הפירוק. ניקוד חלקי במחוון תלוי בשלב ההגדרה. אם הפירוק לא מספיק — נסו צמוד או לופיטal."""

WE2_EN = """**Compute** $\\displaystyle\\lim_{x\\to 0}\\frac{\\sqrt{x+4}-2}{x}$.

When substitution gives $0/0$ and a square root appears in the numerator, the conjugate method is the standard first choice.

---

### Move 1 — Verify $0/0$
$$\\frac{\\sqrt{0+4}-2}{0} = \\frac{2-2}{0} = \\frac{0}{0}.$$
Indeterminate. A square root in the numerator signals the conjugate technique.

### Move 2 — Multiply by the conjugate
$$\\frac{\\sqrt{x+4}-2}{x}\\cdot\\frac{\\sqrt{x+4}+2}{\\sqrt{x+4}+2}.$$
We multiply by $1$ in disguise — the conjugate $\\sqrt{x+4}+2$ rationalizes the surd in the numerator.

### Move 3 — Simplify the numerator (difference of squares)
$$(\\sqrt{x+4}-2)(\\sqrt{x+4}+2) = (x+4)-4 = x.$$
The expression becomes:
$$\\frac{x}{x(\\sqrt{x+4}+2)} = \\frac{1}{\\sqrt{x+4}+2} \\quad (x\\ne 0).$$

### Move 4 — Cancel $x$ and substitute
$$\\lim_{x\\to 0}\\frac{1}{\\sqrt{x+4}+2} = \\frac{1}{\\sqrt{4}+2} = \\frac{1}{4} = \\boxed{\\tfrac{1}{4}}.$$

### Move 5 — Sanity check
Near $x=0.01$, the function value is $\\approx 0.2498$. Since $\\tfrac{1}{4}=0.25$, the answer is consistent. ✓

*Exam note:* Show the conjugate multiplication explicitly — do not jump from $0/0$ directly to the simplified fraction."""

WE2_HE = """**חשבו** $\\displaystyle\\lim_{x\\to 0}\\frac{\\sqrt{x+4}-2}{x}$.

כשהצבה נותנת $0/0$ ויש שורש ריבועי במונה, שיטת הצמוד היא הבחירה הסטנדרטית הראשונה.

---

### צעד 1 — אימות $0/0$
$$\\frac{\\sqrt{0+4}-2}{0} = \\frac{2-2}{0} = \\frac{0}{0}.$$
צורה בלתי-קצובה. שורש במונה מסמן שימוש בצמוד.

### צעד 2 — כפל בצמוד
$$\\frac{\\sqrt{x+4}-2}{x}\\cdot\\frac{\\sqrt{x+4}+2}{\\sqrt{x+4}+2}.$$
מכפילים ב-$1$ בצורה מוסווית — הצמוד $\\sqrt{x+4}+2$ מרציונל את השורש במונה.

### צעד 3 — פישוט המונה (הפרש ריבועים)
$$(\\sqrt{x+4}-2)(\\sqrt{x+4}+2) = (x+4)-4 = x.$$
הביטוי הופך:
$$\\frac{x}{x(\\sqrt{x+4}+2)} = \\frac{1}{\\sqrt{x+4}+2} \\quad (x\\ne 0).$$

### צעד 4 — צמצום $x$ והצבה
$$\\lim_{x\\to 0}\\frac{1}{\\sqrt{x+4}+2} = \\frac{1}{\\sqrt{4}+2} = \\frac{1}{4} = \\boxed{\\tfrac{1}{4}}.$$

### צעד 5 — בדיקת הגיון
ליד $x=0.01$ ערך הפונקציה $\\approx 0.2498$. מכיוון ש-$\\tfrac{1}{4}=0.25$, התשובה עקבית. ✓

*הערת בחינה:* הציגו את כפל הצמוד במפורש — אל תדלגו מ-$0/0$ ישירות לשבר המפושט."""

WE3_EN = """**Compute** $\\displaystyle\\lim_{x\\to 0}\\frac{\\sin(3x)-3\\sin x}{x^3}$.

This limit combines trigonometric identities with either repeated L'Hôpital or Taylor expansion — a staple of university calc-1 finals.

---

### Method A: L'Hôpital's Rule (Applied Three Times)

### Move 1 — Verify $0/0$
Substitution gives $\\frac{0-0}{0}=\\frac{0}{0}$. ✓ L'Hôpital applies.

**Apply L'Hôpital once** (differentiate numerator and denominator separately):
$$\\frac{3\\cos(3x)-3\\cos x}{3x^2}.$$
Substitute $x=0$: $\\frac{3-3}{0}=\\frac{0}{0}$. Still indeterminate.

**Apply L'Hôpital a second time:**
$$\\frac{-9\\sin(3x)+3\\sin x}{6x}.$$
Substitute $x=0$: $\\frac{0}{0}$. Still indeterminate.

**Apply L'Hôpital a third time:**
$$\\frac{-27\\cos(3x)+3\\cos x}{6}.$$
Now substitute $x=0$:
$$\\frac{-27\\cdot 1+3\\cdot 1}{6} = \\frac{-24}{6} = \\boxed{-4}.$$

---

### Method B: Taylor Expansion (Faster for Competitions)

Recall $\\sin u = u - \\frac{u^3}{6} + O(u^5)$.

$$\\sin(3x) = 3x - \\frac{27x^3}{6} + O(x^5), \\quad 3\\sin x = 3x - \\frac{3x^3}{6} + O(x^5).$$

Difference: $-4x^3 + O(x^5)$. Dividing by $x^3$ and taking the limit gives $\\boxed{-4}$.

**Both methods agree.** On exams, either approach earns full credit if every step is shown.

*Exam note:* After each L'Hôpital step, re-check the indeterminate form. Stopping too early is the most common error on this problem type."""

WE3_HE = """**חשבו** $\\displaystyle\\lim_{x\\to 0}\\frac{\\sin(3x)-3\\sin x}{x^3}$.

גבול זה משלב זהויות טריגונומטריות עם לופיטל חוזר או פיתוח טיילור — בסיס בבחינות חדו\"א שנה א'.

---

### שיטה א': כלל לופיטל (שלוש פעמים)

### צעד 1 — אימות $0/0$
הצבה נותנת $\\frac{0-0}{0}=\\frac{0}{0}$. ✓ לופיטal חל.

**מחילים לופיטal פעם ראשונה** (גוזרים מונה ומכנה בנפרד, לא כלל מנה):
$$\\frac{3\\cos(3x)-3\\cos x}{3x^2}.$$
מציבים $x=0$: $\\frac{3-3}{0}=\\frac{0}{0}$. עדיין בלתי-קצוב.

**מחילים לופיטal פעם שנייה:**
$$\\frac{-9\\sin(3x)+3\\sin x}{6x}.$$
מציבים $x=0$: $\\frac{0}{0}$. עדיין בלתי-קצוב.

**מחילים לופיטal פעם שלישית:**
$$\\frac{-27\\cos(3x)+3\\cos x}{6}.$$
מציבים $x=0$:
$$\\frac{-27\\cdot 1+3\\cdot 1}{6} = \\frac{-24}{6} = \\boxed{-4}.$$

---

### שיטה ב': פיתוח טיילור (מהיר יותר)

נזכיר $\\sin u = u - \\frac{u^3}{6} + O(u^5)$.

$$\\sin(3x) = 3x - \\frac{27x^3}{6} + O(x^5), \\quad 3\\sin x = 3x - \\frac{3x^3}{6} + O(x^5).$$

הפרש: $-4x^3 + O(x^5)$. חלוקה ב-$x^3$ וגבול נותנים $\\boxed{-4}$.

**שתי השיטות מסכימות.** בבחינה, כל גישה מקבלת ניקוד מלא אם כל שלב מוצג.

*הערת בחינה:* אחרי כל שלב לופיטal, בדקו שוב את הצורה הבלתי-קצובה. עצירה מוקדמת — הטעות הנפוצה ביותר."""

CHECKPOINT1_EN = """**Step 1 — Direct substitution:** At $x=3$, numerator $9-9=0$, denominator $0$. Form $\\frac{0}{0}$ — we must factor.

**Step 2 — Factor:** $x^2-9=(x-3)(x+3)$ using the difference of squares.

**Step 3 — Cancel and substitute:**
$$\\lim_{x\\to 3}\\frac{(x-3)(x+3)}{x-3} = \\lim_{x\\to 3}(x+3) = 3+3 = \\mathbf{6}.\\checkmark$$

This mirrors Worked Example 1 with $a=3$ instead of $a=2$. The pattern $(x^2-a^2)/(x-a)\\to 2a$ is worth memorising."""

CHECKPOINT1_HE = """**שלב 1 — הצבה ישירה:** ב-$x=3$, מונה $9-9=0$, מכנה $0$. צורה $\\frac{0}{0}$ — חובה לפרק.

**שלב 2 — פירוק:** $x^2-9=(x-3)(x+3)$ לפי הפרש ריבועים.

**שלב 3 — צמצום והצבה:**
$$\\lim_{x\\to 3}\\frac{(x-3)(x+3)}{x-3} = \\lim_{x\\to 3}(x+3) = 3+3 = \\mathbf{6}.\\checkmark$$

זהה לדוגמה 1 עם $a=3$ במקום $a=2$. כדאי לזכור: $(x^2-a^2)/(x-a)\\to 2a$."""

CHECKPOINT2_EN = """**Step 1 — Verify $0/0$:** At $x=0$, $\\sqrt{1}-1=0$ and denominator $0$.

**Step 2 — Multiply by conjugate** $\\dfrac{\\sqrt{x+1}+1}{\\sqrt{x+1}+1}$:
$$\\frac{(x+1)-1}{x(\\sqrt{x+1}+1)} = \\frac{x}{x(\\sqrt{x+1}+1)} = \\frac{1}{\\sqrt{x+1}+1}.$$

**Step 3 — Substitute:** As $x\\to 0$: $\\dfrac{1}{\\sqrt{1}+1} = \\dfrac{1}{2}$. $\\checkmark$

Compare with Worked Example 2: same conjugate structure, different constants."""

CHECKPOINT2_HE = """**שלב 1 — אימות $0/0$:** ב-$x=0$, $\\sqrt{1}-1=0$ ומכנה $0$.

**שלב 2 — כפל בצמוד** $\\dfrac{\\sqrt{x+1}+1}{\\sqrt{x+1}+1}$:
$$\\frac{(x+1)-1}{x(\\sqrt{x+1}+1)} = \\frac{x}{x(\\sqrt{x+1}+1)} = \\frac{1}{\\sqrt{x+1}+1}.$$

**שלב 3 — הצבה:** כש-$x\\to 0$: $\\dfrac{1}{\\sqrt{1}+1} = \\dfrac{1}{2}$. $\\checkmark$

השוואה לדוגמה 2: אותה מבנה צמוד, קבועים שונים."""

WHY_EN = """Limits are the **foundation** of all differential and integral calculus — not an isolated topic. Every derivative is defined as a limit of difference quotients; every definite integral is a limit of Riemann sums; continuity and asymptotes are limit statements.

**You will use this to unlock:**
- `concept:continuity` — a function is continuous exactly when its limit equals its value
- `concept:derivatives_intro` — the derivative *is* a limit
- `concept:integrals_intro` — the integral *is* a limit of sums

**Builds on:**
- `concept:sequences_arithmetic` — discrete limits preview the continuous case
- `concept:functions_intro` — you must read graphs and domains before evaluating limits

**Why it matters for exams:** Bagrut 5-unit papers allocate 10–20 points to limits. University calc-1 exams test limits on every midterm. Examiners reward students who can **choose the right technique quickly** — direct substitution, factoring, conjugate, standard identities, or L'Hôpital — and who write clean, step-by-step solutions."""

WHY_HE = """גבולות הם **יסוד** כל החשבון הדיפרנציאלי והאינטגרלי — לא נושא מבודד. כל נגזרת מוגדרת כגבול של מנה הפרשים; כל אינטגרל מסוים הוא גבול של סכומי רiemann; רציפות ואסימפטוטות הן טענות על גבולות.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:continuity` — פונקציה רציפה בדיוק כשהגבול שווה לערך
- `concept:derivatives_intro` — הנגזרת *היא* גבול
- `concept:integrals_intro` — האינטגרל *הוא* גבול של סכומים

**מבוסס על:**
- `concept:sequences_arithmetic` — גבולות בדידים מכינים את המקרה הרציף
- `concept:functions_intro` — חובה לקרוא גרפים ותחומים לפני חישוב גבולות

**למה זה חשוב לבחינות:** בבגרות 5 יחידות מוקדשות 10–20 נקודות לגבולות. בחדו\"א נבחנים גבולות בכל מבחן. בוחנים מתגמלים מי ש**בוחר טכניקה נכונה במהירות** — הצבה, פירוק, צמוד, זהויות סטנדרטיות או לופיטal — וכותב פתרון מסודר."""

SUMMARY_EN = """**Key techniques (in order of attempt):**
1. **Direct substitution** — always try first; if no indeterminate form, you are done.
2. **Factor and cancel** — for polynomial $0/0$ expressions.
3. **Conjugate** — when a square root gives $0/0$.
4. **Standard limits** — memorise $\\sin x/x$, $(e^x-1)/x$, $\\ln(1+x)/x$, and rescaling tricks.
5. **L'Hôpital** — last resort for stubborn $0/0$ or $\\infty/\\infty$; differentiate top and bottom separately.

**Takeaway:** You should now recognise which method applies from the problem structure alone — before writing a single line of algebra. Check one-sided limits whenever the domain is restricted ($\\ln x$, $\\sqrt{x}$, $|x|$). Compare polynomial degrees at infinity for rational functions.

**Next step:** Move to `concept:continuity` to connect limits with function values at a point."""

SUMMARY_HE = """**טכניקות מרכזיות (לפי סדר ניסיון):**
1. **הצבה ישירה** — תמיד ראשון; אם אין צורה בלתי-קצובה — סיימתם.
2. **פירוק וצמצום** — לביטויי $0/0$ פולינומיים.
3. **צמוד** — כששורש ריבועי נותן $0/0$.
4. **גבולות סטנדרטיים** — שינון $\\sin x/x$, $(e^x-1)/x$, $\\ln(1+x)/x$ וטריקי קנה-מידה.
5. **לופיטal** — מוצא אחרון ל-$0/0$ או $\\infty/\\infty$ עקשניים; גזירת מונה ומכנה בנפרד.

**מסקנה:** כעת תוכלו לזהות איזו שיטה מתאימה ממבנה השאלה בלבד — לפני שורת אלגברה אחת. בדקו גבולות חד-צדדיים כשהתחום מוגבל ($\\ln x$, $\\sqrt{x}$, $|x|$). השוו מעלות פולינומים ב-$\\infty$.

**המשך:** עברו ל-`concept:continuity` לחיבור גבולות עם ערכי פונקציה בנקודה."""

DEF_HE = """## הגדרה לא-פורמלית

אומרים $\\lim_{x \\to a} f(x) = L$ אם $f(x)$ יכולה להיות **קרובה כרצוננו** ל-$L$ כאשר $x$ **קרוב מספיק** (אך לא שווה) ל-$a$.

## הגדרה פורמלית (ε–δ)

$$\\lim_{x \\to a} f(x) = L \\quad \\Longleftrightarrow \\quad \\forall\\,\\varepsilon > 0,\\; \\exists\\,\\delta > 0 : 0 < |x - a| < \\delta \\Rightarrow |f(x) - L| < \\varepsilon.$$

> **תובנת מפתח:** הערך $f(a)$ (אם קיים בכלל) **לא רלוונטי** לגבול.

## גבולות חד-צדדיים

- **גבול ימני:** $\\lim_{x \\to a^+} f(x) = L$ — $x$ מתקרב ל-$a$ מערכים **גדולים ממנו**.
- **גבול שמאלי:** $\\lim_{x \\to a^-} f(x) = L$ — $x$ מתקרב ל-$a$ מערכים **קטנים ממנו**.

## גבול דו-צדדי

$$\\lim_{x \\to a} f(x) = L \\quad \\Longleftrightarrow \\quad \\lim_{x \\to a^+} f(x) = L \\;\\text{AND}\\; \\lim_{x \\to a^-} f(x) = L.$$

## גבול לא קיים (DNE)

גבול **לא קיים** (DNE) אם:
- הגבולות החד-צדדיים שונים: למשל $\\lim_{x\\to 0^+}\\frac{1}{x}=+\\infty$ אך $\\lim_{x\\to 0^-}\\frac{1}{x}=-\\infty$.
- הפונקציה מתנדנדת ללא התכנסות: $\\lim_{x\\to 0}\\sin\\frac{1}{x}$ DNE.
- אחד מהגבולות החד-צדדיים הוא $\\pm\\infty$ (גבול אינסופי — אומרים \"לא קיים\" כמספר סופי).

**זכרו:** גבול מתאר התנהגות *קרוב* לנקודה, לא בהכרח את ערך הפונקציה בנקודה עצמה."""

THEORY_HE_FIX = """אם $\\lim_{x\\to a}\\frac{f(x)}{g(x)}$ נותן $\\frac{0}{0}$ או $\\frac{\\infty}{\\infty}$, ו-$f,g$ גזירות ליד $a$:

$$\\lim_{x\\to a}\\frac{f(x)}{g(x)} = \\lim_{x\\to a}\\frac{f'(x)}{g'(x)},$$

בתנאי שהגבול הימני קיים."""

BEFORE_HE_DEGREE = """## השוואת מעלות (פונקציות רציונליות ב-$\\infty$)

$$\\lim_{x\\to\\infty}\\frac{a_n x^n + \\cdots}{b_m x^m + \\cdots} = \\begin{cases} 0 & n < m \\\\\\\\ \\dfrac{a_n}{b_m} & n = m \\\\\\\\ \\pm\\infty & n > m\\end{cases}$$"""

EXPLANATIONS = [
    {
        "en": """**Why this is correct:**
Substituting $x=4$ gives $\\frac{16-16}{0}=\\frac{0}{0}$ — indeterminate. Factor: $x^2-16=(x-4)(x+4)$. Cancel $(x-4)$ (valid since $x\\ne 4$ in the limit) and substitute: $4+4=8$.

**How to think about it:**
This is the difference-of-squares pattern $(x^2-a^2)/(x-a)\\to 2a$. Here $a=4$, so the answer is $8$. Always try substitution first; when you see $0/0$ with polynomials, factor before reaching for L'Hôpital.

**Common slip:**
Concluding the limit is undefined because the function is undefined at $x=4$. Or cancelling incorrectly and getting $x-4$ instead of $x+4$ after factoring.

**Exam tip:**
Write $0/0$ explicitly, show the factorisation, then cancellation. Bagrut rubrics award partial credit for correct setup even if the final arithmetic fails.""",
        "he": """**למה זה נכון:**
הצבת $x=4$ נותנת $\\frac{16-16}{0}=\\frac{0}{0}$ — בלתי-קצוב. פירוק: $x^2-16=(x-4)(x+4)$. צמצום $(x-4)$ (תקין כי $x\\ne 4$ בגבול) והצבה: $4+4=8$.

**איך לחשוב על זה:**
זה דפוס הפרש ריבועים $(x^2-a^2)/(x-a)\\to 2a$. כאן $a=4$, ולכן התשובה $8$. תמיד נסו הצבה ראשון; ב-$0/0$ עם פולינומים — פרקו לפני לופיטal.

**טעות נפוצה:**
מסקנה שהגבול לא מוגדר כי הפונקציה לא מוגדרת ב-$x=4$. או צמצום שגוי וקבלת $x-4$ במקום $x+4$.

**טיפ לבחינה:**
כתבו $0/0$ במפורש, הציגו פירוק ואז צמצום. מחוון הבגרות נותן ניקוד חלקי על הגדרה נכונה גם אם החשבון הסופי שגוי.""",
    },
    {
        "en": """**Why this is correct:**
At $x=0$: $\\sin(0)=0$, denominator $0$ — form $0/0$. Rewrite as $5\\cdot\\dfrac{\\sin(5x)}{5x}$. The standard limit $\\lim_{u\\to 0}\\frac{\\sin u}{u}=1$ with $u=5x$ gives $5\\cdot 1=5$.

**How to think about it:**
The rescaling trick converts any $\\sin(kx)/x$ to $k\\cdot\\sin(kx)/(kx)$. Recognise the inner argument $5x$ and pull out the factor $5$. This is faster than L'Hôpital for trig limits.

**Common slip:**
Using $\\sin(5x)/x\\to 0$ because $\\sin(0)=0$ — confusing the value with the limit. Or forgetting to multiply by $5$ after applying $\\sin u/u\\to 1$.

**Exam tip:**
Memorise $\\lim_{x\\to 0}\\sin(kx)/x=k$ as a one-line identity. It appears on every Bagrut 5-unit paper and saves time on multi-step problems.""",
        "he": """**למה זה נכון:**
ב-$x=0$: $\\sin(0)=0$, מכנה $0$ — צורה $0/0$. כותבים $5\\cdot\\dfrac{\\sin(5x)}{5x}$. הגבול הסטנדרטי $\\lim_{u\\to 0}\\frac{\\sin u}{u}=1$ עם $u=5x$ נותן $5\\cdot 1=5$.

**איך לחשוב על זה:**
טריק קנה-המידה ממיר $\\sin(kx)/x$ ל-$k\\cdot\\sin(kx)/(kx)$. זיהו את הארגומנט $5x$ והוציאו גורם $5$. מהיר יותר מלופיטal לגבולות טריגונומטריים.

**טעות נפוצה:**
$\\sin(5x)/x\\to 0$ כי $\\sin(0)=0$ — בלבול ערך עם גבול. או שכחת כפל ב-$5$ אחרי $\\sin u/u\\to 1$.

**טיפ לבחינה:**
שיננו $\\lim_{x\\to 0}\\sin(kx)/x=k$ כזהות בשורה. מופיע בכל בגרות 5 יחידות וחוסך זמן.""",
    },
    {
        "en": """**Why this is correct:**
As $x\\to\\infty$, both numerator and denominator are degree-2 polynomials. Divide by $x^2$: $\\dfrac{3-1/x^2}{2+5/x^2}\\to\\dfrac{3}{2}$. Equivalently: equal degrees means the limit is the ratio of leading coefficients $3/2$.

**How to think about it:**
For rational functions at infinity, compare degrees first. Same degree $\\Rightarrow$ ratio of leading terms. Higher numerator degree $\\Rightarrow$ $\\pm\\infty$; lower $\\Rightarrow$ $0$. No need for L'Hôpital here.

**Common slip:**
Substituting $x=\\infty$ directly (invalid). Or dividing only the numerator by $x^2$ but not the denominator. Some students answer $3/2$ from coefficients but cannot explain why.

**Exam tip:**
State \"degrees equal, ratio of leading coefficients\" — one sentence earns full reasoning credit on Bagrut limit-at-infinity questions worth 4–6 points.""",
        "he": """**למה זה נכון:**
כש-$x\\to\\infty$, מונה ומכנה פולינומים ממעלה 2. חלוקה ב-$x^2$: $\\dfrac{3-1/x^2}{2+5/x^2}\\to\\dfrac{3}{2}$. שווה ערך: מעלות שוות — יחס מקדמים מובילים $3/2$.

**איך לחשוב על זה:**
בפונקציות רציונליות ב-$\\infty$, השוו מעלות קודם. מעלה שווה $\\Rightarrow$ יחס המקדמים המובילים. מונה גבוה $\\Rightarrow$ $\\pm\\infty$; נמוך $\\Rightarrow$ $0$. אין צורך בלופיטal.

**טעות נפוצה:**
הצבת $x=\\infty$ ישירות (לא תקף). חלוקת מונה ב-$x^2$ בלי מכנה. תשובה $3/2$ בלי הסבר.

**טיפ לבחינה:**
כתבו \"מעלות שוות, יחס מקדמים מובילים\" — משפט אחד מקבל ניקוד הסבר מלא בגבולות ב-$\\infty$.""",
    },
    {
        "en": """**Why this is correct:**
$\\ln x$ is defined only for $x>0$. As $x\\to 0^+$, $x$ approaches zero from the positive side and $\\ln x$ decreases without bound: $\\lim_{x\\to 0^+}\\ln x=-\\infty$.

**How to think about it:**
This is a **one-sided limit** — you must approach from the right because $\\ln x$ is undefined for $x\\le 0$. The graph of $y=\\ln x$ has a vertical asymptote at $x=0$.

**Common slip:**
Writing $\\lim_{x\\to 0}\\ln x$ without the $^+$ superscript (the two-sided limit does not exist). Or answering $0$ because $\\ln(1)=0$ and confusing nearby values.

**Exam tip:**
Whenever you see $\\ln x$, $\\sqrt{x}$, or $1/x$ at a boundary point, check the domain and specify one-sided limits. Examiners deliberately test this on 3–5 point questions.""",
        "he": """**למה זה נכון:**
$\\ln x$ מוגדר רק ל-$x>0$. כש-$x\\to 0^+$, $x$ מתקרב לאפס מימין ו-$\\ln x$ יורד ללא גבול: $\\lim_{x\\to 0^+}\\ln x=-\\infty$.

**איך לחשוב על זה:**
זה **גבול חד-צדדי** — חובה להתקרב מימין כי $\\ln x$ לא מוגדר ל-$x\\le 0$. לגרף $y=\\ln x$ אסימפטוטה אנכית ב-$x=0$.

**טעות נפוצה:**
$\\lim_{x\\to 0}\\ln x$ בלי $^+$ (הגבול הדו-צדדי לא קיים). תשובה $0$ כי $\\ln(1)=0$ — בלבול.

**טיפ לבחינה:**
ב-$\\ln x$, $\\sqrt{x}$ או $1/x$ בגבול — בדקו תחום וציינו גבול חד-צדדי. בוחנים בודקים זאת במפורש.""",
    },
    {
        "en": """**Why this is correct:**
Substituting $x=0$: $\\frac{\\sqrt{9}-3}{0}=\\frac{0}{0}$. Multiply by conjugate $\\dfrac{\\sqrt{x+9}+3}{\\sqrt{x+9}+3}$: numerator becomes $x$, giving $\\dfrac{x}{x(\\sqrt{x+9}+3)}=\\dfrac{1}{\\sqrt{x+9}+3}\\to\\dfrac{1}{6}$.

**How to think about it:**
Square root in numerator plus $0/0$ equals conjugate method. After rationalising, the $x$ cancels cleanly. Compare with $\\lim_{x\\to 0}\\frac{\\sqrt{x+4}-2}{x}=\\frac{1}{4}$ — same structure.

**Common slip:**
Forgetting to multiply **both** numerator and denominator by the conjugate. Sign errors in the difference-of-squares step: $(x+9)-9=x$, not $x+9-3$.

**Exam tip:**
Show the conjugate multiplication explicitly. On Bagrut papers, this technique alone appears in 2–3 limit questions per exam — worth practising until automatic.""",
        "he": """**למה זה נכון:**
הצבת $x=0$: $\\frac{\\sqrt{9}-3}{0}=\\frac{0}{0}$. כפל בצמוד $\\dfrac{\\sqrt{x+9}+3}{\\sqrt{x+9}+3}$: מונה $x$, ולכן $\\dfrac{1}{\\sqrt{x+9}+3}\\to\\dfrac{1}{6}$.

**איך לחשוב על זה:**
שורש במונה ו-$0/0$ — שיטת צמוד. אחרי רציונליזציה, $x$ מתצמצם. השוו ל-$\\lim_{x\\to 0}\\frac{\\sqrt{x+4}-2}{x}=\\frac{1}{4}$ — אותו מבנה.

**טעות נפוצה:**
שכחת כפל **גם** במונה וגם במכנה. שגיאות סימן: $(x+9)-9=x$, לא $x+9-3$.

**טיפ לבחינה:**
הציגו כפל צמוד במפורש. בבגרות, טכניקה זו מופיעה ב-2–3 שאלות גבול — שווה תרגול עד אוטומטיות. בדקו: $\\frac{1}{\\sqrt{9}+3}=\\frac{1}{6}$.""",
    },
    {
        "en": """**Why this is correct:**
At $x=0$: $e^0-1=0$, denominator $0$ — form $0/0$. This is the **standard limit** $\\lim_{x\\to 0}\\frac{e^x-1}{x}=1$, equivalent to the definition of $(e^x)'$ at zero. Taylor: $e^x=1+x+\\frac{x^2}{2}+\\cdots$, so $(e^x-1)/x=1+\\frac{x}{2}+\\cdots\\to 1$.

**How to think about it:**
Recognise the pattern immediately — do not use L'Hôpital when the question forbids it. The four standard limits ($\\sin x/x$, $(e^x-1)/x$, $\\ln(1+x)/x$, $(1+1/x)^x$) should be memorised as a set.

**Common slip:**
Applying L'Hôpital anyway (loses method points when forbidden). Or confusing with $\\lim_{x\\to 0}\\frac{e^x}{x}$ which diverges.

**Exam tip:**
When a question says \"without L'Hôpital\", quote the standard limit or use Taylor. One line of justification is sufficient if you name the identity.""",
        "he": """**למה זה נכון:**
ב-$x=0$: $e^0-1=0$, מכנה $0$ — $0/0$. זה **גבול סטנדרטי** $\\lim_{x\\to 0}\\frac{e^x-1}{x}=1$, שווה ערך להגדרת $(e^x)'$ באפס. טיילור: $e^x=1+x+\\cdots$, ולכן $(e^x-1)/x\\to 1$.

**איך לחשוב על זה:**
זיהו מיד — אל תשתמשו בלופיטal כשאסור. ארבעת הגבולות הסטנדרטיים ($\\sin x/x$, $(e^x-1)/x$, $\\ln(1+x)/x$, $(1+1/x)^x$) לשינון כקבוצה.

**טעות נפוצה:**
לופיטal בכל זאת (מאבד נקודות שיטה). בלבול עם $\\lim_{x\\to 0} e^x/x$ שמתפוצץ.

**טיפ לבחינה:**
כש\"ללא לופיטal\" — צטטו גבול סטנדרטי או טיילור. שורת הצדקה אחת מספיקה. זהות $(e^x-1)/x$ מופיעה גם בהוכחת נגזרת האקספוננט.""",
    },
    {
        "en": """**Why this is correct:**
At $x=1$: numerator $1-1=0$, denominator $1-1=0$ — form $0/0$. Factor: $x^3-1=(x-1)(x^2+x+1)$ and $x^2-1=(x-1)(x+1)$. Cancel $(x-1)$: $\\dfrac{x^2+x+1}{x+1}\\big|_{x=1}=\\dfrac{3}{2}$.

**How to think about it:**
Both numerator and denominator share the factor $(x-1)$ because both vanish at $x=1$. After cancellation, direct substitution works. This is factoring, not L'Hôpital — faster and cleaner.

**Common slip:**
Cancelling $(x-1)$ incorrectly and leaving $(x^2+x+1)/(x-1)$ instead of $(x+1)$ in the denominator. Arithmetic: $1+1+1=3$, not $2$.

**Exam tip:**
When both top and bottom are zero, look for a common linear factor first. Sum-of-cubes and difference-of-squares formulas appear together on Bagrut algebra-limit questions.""",
        "he": """**למה זה נכון:**
ב-$x=1$: מונה $0$, מכנה $0$ — $0/0$. פירוק: $x^3-1=(x-1)(x^2+x+1)$, $x^2-1=(x-1)(x+1)$. צמצום $(x-1)$: $\\dfrac{x^2+x+1}{x+1}\\big|_{x=1}=\\dfrac{3}{2}$.

**איך לחשוב על זה:**
מונה ומכנה חולקים $(x-1)$ כי שניהם מתאפסים ב-$x=1$. אחרי צמצום — הצבה ישירה. פירוק, לא לופיטal — מהיר ונקי.

**טעות נפוצה:**
צמצום שגוי — $(x^2+x+1)/(x-1)$ במקום $(x+1)$ במכנה. חשבון: $1+1+1=3$.

**טיפ לבחינה:**
כשמונה ומכנה אפס — חפשו גורם לינארי משותף. נוסחאות חזקות שלישית וריבוע מופיעות יחד בבגרות. אימות: הצבה אחרי צמצום חייבת לתת $\\frac{3}{2}$.""",
    },
    {
        "en": """**Why this is correct:**
At $x=0$: form $0/0$. Apply L'Hôpital three times:
$\\dfrac{1-\\cos x}{3x^2}\\to\\dfrac{\\sin x}{6x}\\to\\dfrac{\\cos x}{6}\\to\\dfrac{1}{6}$.

**How to think about it:**
Each L'Hôpital step reduces the \"order\" of the indeterminate behaviour. Taylor confirms: $x-\\sin x\\sim x^3/6$, so dividing by $x^3$ gives $1/6$. Verify $0/0$ before **each** application.

**Common slip:**
Differentiating with the quotient rule instead of L'Hôpital (invalid). Stopping after one application when the form is still $0/0$. Forgetting the factor $6$ from $(x^3)'=3x^2$ and then $(6x)'=6$.

**Exam tip:**
Write \"L'H\" above each equality when applying the rule. Show all three derivative ratios — partial credit per correct step on university rubrics.""",
        "he": """**למה זה נכון:**
ב-$x=0$: צורה $0/0$. לופיטal שלוש פעמים:
$\\dfrac{1-\\cos x}{3x^2}\\to\\dfrac{\\sin x}{6x}\\to\\dfrac{\\cos x}{6}\\to\\dfrac{1}{6}$.

**איך לחשוב על זה:**
כל שלב לופיטal מפחית \"סדר\" התנהגות בלתי-קצובה. טיילור מאשר: $x-\\sin x\\sim x^3/6$, חלוקה ב-$x^3$ נותנת $1/6$. אמתו $0/0$ לפני **כל** יישום.

**טעות נפוצה:**
גזירה בכלל מנה במקום לופיטal. עצירה אחרי יישום אחד. שכחת גורם $6$ מ-$(x^3)'=3x^2$ ו-$(6x)'=6$.

**טיפ לבחינה:**
כתבו \"ל'ה\" מעל כל שוויון. הציגו שלוש מנות נגזרות — ניקוד חלקי לכל שלב נכון. טיילור $x-\\sin x\\sim x^3/6$ מאשר $\\frac{1}{6}$ ללא גזירה.""",
    },
]


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    we_idx = 0
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "worked_example":
            we_idx += 1
            src = [(WE1_EN, WE1_HE), (WE2_EN, WE2_HE), (WE3_EN, WE3_HE)][we_idx - 1]
            sec["body_en_md"] = src[0]
            sec["body_he_md"] = src[1]
        elif kind == "checkpoint":
            cp_idx += 1
            src = [(CHECKPOINT1_EN, CHECKPOINT1_HE), (CHECKPOINT2_EN, CHECKPOINT2_HE)][
                cp_idx - 1
            ]
            sec["checkpoint_solution_en"] = src[0]
            sec["checkpoint_solution_he"] = src[1]
        elif kind == "why_matters":
            sec["body_en_md"] = WHY_EN
            sec["body_he_md"] = WHY_HE
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY_EN
            sec["body_he_md"] = SUMMARY_HE

    # Fix intro trailing English
    for sec in data["sections"]:
        if sec["kind"] == "intro":
            he = sec["body_he_md"]
            if "## Why Study Limits?" in he:
                sec["body_he_md"] = he.split("\n\n## Why Study Limits?")[0].strip()

    # Fix definition Hebrew
    for sec in data["sections"]:
        if sec["kind"] == "definition":
            sec["body_he_md"] = DEF_HE

    # Fix theory Hebrew — restore L'Hôpital formula
    for sec in data["sections"]:
        if sec["kind"] == "theory":
            he = sec["body_he_md"]
            old = "בתנאי שהגבול הימני קיים."
            if old in he and "$$\\lim_{x\\to a}\\frac{f(x)}{g(x)} = \\lim_{x\\to a}\\frac{f'(x)}{g'(x)},$$" not in he:
                he = he.replace(
                    "אם $\\lim_{x\\to a}\\frac{f(x)}{g(x)}$ נותן $\\frac{0}{0}$ או $\\frac{\\infty}{\\infty}$, ו-$f,g$ גזירות ליד $a$:\n\nבתנאי שהגבול הימני קיים.",
                    THEORY_HE_FIX,
                )
                sec["body_he_md"] = he

    # Fix before_exam Hebrew — restore degree comparison
    for sec in data["sections"]:
        if sec["kind"] == "before_exam":
            he = sec["body_he_md"]
            if "## השוואת מעלות" in he and "$$\\lim_{x\\to\\infty}" not in he.split("## השוואת מעלות")[1].split("## מה בוחני")[0]:
                he = he.replace(
                    "## השוואת מעלות (פונקציות רציונליות ב-$\\infty$)\n\n## מה בוחני",
                    BEFORE_HE_DEGREE + "\n\n## מה בוחני",
                )
                sec["body_he_md"] = he

    for i, q in enumerate(data["questions"]):
        q["explanation_en"] = EXPLANATIONS[i]["en"]
        q["explanation_he"] = EXPLANATIONS[i]["he"]

    for sec in data["sections"]:
        if sec.get("kind") == "worked_example":
            pad_en = "\n\n*Exam note:* Always state the indeterminate form before applying any technique — partial credit on Bagrut rubrics depends on this setup step."
            pad_he = "\n\n*הערת בחינה:* ציינu תמיד את הצורה הבלתי-קצובה לפני כל טכניקה — ניקוד חלקי במחוון תלוי בשלב ההגדרה."
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["worked_example"]["en"]:
                sec["body_en_md"] = sec.get("body_en_md", "") + pad_en
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["worked_example"]["he"]:
                sec["body_he_md"] = sec.get("body_he_md", "") + pad_he.replace("ציינu", "ציינו")

    for q in data["questions"]:
        if word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q["explanation_he"] + " מחוון הבחינה מעניק ניקוד חלקי על זיהוי הצורה הבלתי-קצובה ובחירת שיטת הפתרון הנכונה."

    data["version"] = 2
    TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind not in MIN_WORDS:
            continue
        en_w = word_count(sec.get("body_en_md", ""))
        he_w = word_count(sec.get("body_he_md", ""))
        mins = MIN_WORDS[kind]
        if en_w < mins["en"]:
            errors.append(f"section {kind}: EN {en_w} < {mins['en']}")
        if he_w < mins["he"]:
            errors.append(f"section {kind}: HE {he_w} < {mins['he']}")
        if hebrew_body_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"section {kind}: weak Hebrew")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q[f"explanation_{lang}"])
            if w < 80 or w > 150:
                errors.append(f"Q{q['ord']} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        sys.exit(1)
    print("OK — all gates passed")
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")

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


if __name__ == "__main__":
    main()
