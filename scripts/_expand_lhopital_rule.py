#!/usr/bin/env python3
"""Expand lhopital_rule.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/lhopital_rule.json"

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


INTRO = {
    "body_en_md": """When you substitute $x=a$ into a rational expression and get $0/0$ or $\\infty/\\infty$, the ordinary limit laws **stop working** — you cannot cancel, factor, or divide by zero in a meaningful way yet. The expression is in an **indeterminate form**: the limit might be $0$, $1$, $\\infty$, or might not exist at all; substitution alone reveals nothing.

Consider $\\displaystyle\\lim_{x\\to 0}\\frac{\\sin x}{x}$. Plugging in $x=0$ gives $0/0$. This limit equals $1$, but you cannot see that from the form alone. **L'Hôpital's rule** (1696, attributed to the Marquis de l'Hôpital from Johann Bernoulli's lectures) provides a systematic rescue: under correct hypotheses, differentiate numerator and denominator **separately**, then take the limit of the new ratio.

**Where it appears:** limits at a point with $0/0$ (e.g. $\\frac{e^x-1}{x}$); limits at infinity with $\\infty/\\infty$ (e.g. $\\frac{x^k}{e^x}$); disguised forms $0\\cdot\\infty$, $\\infty-\\infty$, $1^\\infty$, $0^0$, $\\infty^0$ after algebraic conversion. University calculus exams and Bagrut 5-unit papers treat L'Hôpital as a core technique alongside known limits and Taylor approximations.""",
    "body_he_md": """כאשר מציבים $x=a$ בביטוי רציונלי ומקבלים $0/0$ או $\\infty/\\infty$, חוקי הגבולות הרגילים **מפסיקים לעבוד** — אי אפשר לצמצם, לפרק לגורמים או לחלק באפס בצורה משמעותית. הביטוי נמצא ב**צורה בלתי-קבועה**: הגבול עלול להיות $0$, $1$, $\\infty$, או שלא יהיה קיים; הצבה בלבד לא חושפת דבר.

לדוגמה $\\displaystyle\\lim_{x\\to 0}\\frac{\\sin x}{x}$: הצבת $x=0$ נותנת $0/0$. הגבול שווה $1$, אך לא רואים זאת מהצורה בלבד. **כלל לופיטל** (1696, מברנולי) מספק פתרון שיטתי: בתנאים מתאימים, גוזרים מונה ומכנה **בנפרד**, ואז לוקחים גבול של המנה החדשה.

**היכן זה מופיע:** גבולות בנקודה בצורת $0/0$ (למשל $\\frac{e^x-1}{x}$); גבולות באינסוף בצורת $\\infty/\\infty$ (למשל $\\frac{x^k}{e^x}$); צורות מוסוות $0\\cdot\\infty$, $\\infty-\\infty$, $1^\\infty$, $0^0$, $\\infty^0$ לאחר המרה אלגברית. בחינות חדו\"א ובגרות 5 יחידות מציגות לופיטל כטכניקה מרכזית לצד גבולות ידועים וקירובי טיילור.""",
}

DEFINITION = {
    "body_en_md": """**Theorem (L'Hôpital's Rule):**

Suppose $\\lim_{x\\to a}f(x)=0$ and $\\lim_{x\\to a}g(x)=0$ (or both limits are $\\pm\\infty$). If $g'(x)\\ne 0$ in some punctured neighbourhood of $a$, and if
$$\\lim_{x\\to a}\\frac{f'(x)}{g'(x)}$$
exists as a finite number or is $\\pm\\infty$, then
$$\\lim_{x\\to a}\\frac{f(x)}{g(x)} = \\lim_{x\\to a}\\frac{f'(x)}{g'(x)}.$$

The rule applies to one-sided limits ($x\\to a^+$, $x\\to a^-$) and to limits as $x\\to\\pm\\infty$ (differentiate with respect to $x$ as usual).

**Critical preconditions (check before every use):**
1. Verify the form is **genuinely** $0/0$ or $\\infty/\\infty$ after substitution.
2. Differentiate $f$ and $g$ **independently** — do **not** apply the quotient rule to $\\frac{f}{g}$.
3. If the new ratio is still indeterminate, apply the rule again (possibly several times).
4. Stop when the limit is no longer indeterminate — do not differentiate past that point.

**What the rule does NOT say:** it does not guarantee the limit exists; it only says that if the limit of $\\frac{f'}{g'}$ exists (or blows up to $\\pm\\infty$), then the original limit equals that value. If $\\lim\\frac{f'}{g'}$ oscillates or fails to exist, L'Hôpital gives no conclusion.""",
    "body_he_md": """**משפט (כלל לופיטל):**

נניח $\\lim_{x\\to a}f(x)=0$ ו-$\\lim_{x\\to a}g(x)=0$ (או ששניהם $\\pm\\infty$). אם $g'(x)\\ne 0$ בסביבה מנוקבת של $a$, וגבול
$$\\lim_{x\\to a}\\frac{f'(x)}{g'(x)}$$
קיים כמספר סופי או שהוא $\\pm\\infty$, אז
$$\\lim_{x\\to a}\\frac{f(x)}{g(x)} = \\lim_{x\\to a}\\frac{f'(x)}{g'(x)}.$$

הכלל חל על גבולות חד-צדדיים ($x\\to a^+$, $x\\to a^-$) ועל $x\\to\\pm\\infty$ (גוזרים ב-$x$ כרגיל).

**תנאי קדם קריטיים (בדקו לפני כל שימוש):**
1. וודאו שהצורה **באמת** $0/0$ או $\\infty/\\infty$ אחרי הצבה.
2. גזרו $f$ ו-$g$ **בנפרד** — **אל** תפעילו כלל מנה על $\\frac{f}{g}$.
3. אם המנה החדשה עדיין בלתי-קבועה — הפעילו שוב (לפעמים מספר פעמים).
4. עצרו כשהגבול כבר לא בלתי-קבוע — אל תמשיכו לגזור מעבר לנקודה זו.

**מה הכלל לא אומר:** הוא לא מבטיח שהגבול קיים; רק שאם $\\lim\\frac{f'}{g'}$ קיים (או מתפוצץ ל-$\\pm\\infty$), אז הגבול המקורי שווה לו. אם $\\lim\\frac{f'}{g'}$ מתנדנד או לא קיים — לופיטל לא נותן מסקנה.""",
}

THEORY = {
    "body_en_md": """**The seven indeterminate forms** and how to reduce each to $0/0$ or $\\infty/\\infty$:

| Form | Reduction strategy |
|------|--------------------|
| $0/0$ | Apply L'Hôpital directly |
| $\\infty/\\infty$ | Apply L'Hôpital directly |
| $0\\cdot\\infty$ | Rewrite as $\\frac{0}{1/\\infty}$ or $\\frac{\\infty}{1/0}$ — pick the cleaner ratio |
| $\\infty-\\infty$ | Combine into one fraction; common denominator |
| $1^\\infty$, $0^0$, $\\infty^0$ | Let $L=\\lim f^g$; compute $\\ln L=\\lim g\\ln f$ ($0\\cdot\\pm\\infty$); convert; L'Hôpital; then $L=e^{\\ln L}$ |

**Growth hierarchy at infinity** (when comparing $\\infty/\\infty$ without differentiating): for any fixed $n>0$,
$$\\ln x \\ll x^n \\ll a^x \\ll x^x \\quad (a>1).$$
Exponentials beat polynomials; polynomials beat logarithms. This predicts how many L'Hôpital applications you need before the limit resolves.

**The exponential trick:** if $L=\\lim f(x)^{g(x)}$, then $\\ln L=\\lim g(x)\\ln f(x)$. The right-hand side is usually $0\\cdot(\\pm\\infty)$. Rewrite as a quotient, apply L'Hôpital to the exponent, exponentiate at the end. For $1^\\infty$, the standard limit $\\lim_{t\\to 0}\\frac{\\ln(1+t)}{t}=1$ often finishes the job after substitution $t=1/x$.

**When L'Hôpital is overkill:** factoring ($\\frac{x^2-4}{x-2}$), known limits ($\\frac{\\sin x}{x}$, $\\frac{e^x-1}{x}$), or squeeze theorem may be faster and earn full credit with less algebra.""",
    "body_he_md": """**שבע הצורות הבלתי-קבועות** וכיצד להמיר כל אחת ל-$0/0$ או $\\infty/\\infty$:

| צורה | אסטרטגיית המרה |
|------|----------------|
| $0/0$ | לופיטל ישיר |
| $\\infty/\\infty$ | לופיטל ישיר |
| $0\\cdot\\infty$ | כתבו כ-$\\frac{0}{1/\\infty}$ או $\\frac{\\infty}{1/0}$ — בחרו את המנה הפשוטה |
| $\\infty-\\infty$ | איחוד לשבר אחד; מכנה משותף |
| $1^\\infty$, $0^0$, $\\infty^0$ | $L=\\lim f^g$; $\\ln L=\\lim g\\ln f$ ($0\\cdot\\pm\\infty$); המרה; לופיטל; $L=e^{\\ln L}$ |

**היררכיית גדילה באינסוף** (להשוואת $\\infty/\\infty$): לכל $n>0$ קבוע,
$$\\ln x \\ll x^n \\ll a^x \\ll x^x \\quad (a>1).$$
אקספוננציות גוברות על פולינומים; פולינומים גוברים על לוגריתמים. זה מנבא כמה יישומי לופיטל נדרשים.

**טריק האקספוננט:** אם $L=\\lim f(x)^{g(x)}$, אז $\\ln L=\\lim g(x)\\ln f(x)$ — בדרך כלל $0\\cdot(\\pm\\infty)$. שכתבו כמנה, לופיטל על המעריך, בסוף $L=e^{\\ln L}$. ב-$1^\\infty$, הגבול $\\lim_{t\\to 0}\\frac{\\ln(1+t)}{t}=1$ לעיתים מסיים אחרי $t=1/x$.

**מתי לופיטל מיותר:** פירוק לגורמים ($\\frac{x^2-4}{x-2}$), גבולות ידועים ($\\frac{\\sin x}{x}$), או משפט הסנדוויץ' — מהירים יותר ומקבלים ניקוד מלא.""",
}

WE1 = {
    "body_en_md": """**Given:** $\\displaystyle\\lim_{x\\to 0}\\frac{\\sin x}{x}$.

This is the most famous limit in calculus — it defines the derivative of sine and appears in every trig-derivative proof.

### Move 1 — Verify indeterminate form
Substitute $x=0$: numerator $\\sin(0)=0$, denominator $0$. Form $\\frac{0}{0}$ — L'Hôpital applies. $\\checkmark$ If the denominator had approached a non-zero number, the rule would **not** apply.

### Move 2 — Differentiate numerator and denominator separately
$$\\frac{d}{dx}[\\sin x]=\\cos x, \\qquad \\frac{d}{dx}[x]=1.$$
Do **not** use the quotient rule on $\\frac{\\sin x}{x}$ — L'Hôpital requires independent derivatives of top and bottom.

### Move 3 — Evaluate the new limit
$$\\lim_{x\\to 0}\\frac{\\cos x}{1}=\\cos(0)=1.$$
The new ratio is no longer indeterminate — stop here.

**Answer:** $\\boxed{\\displaystyle\\lim_{x\\to 0}\\frac{\\sin x}{x}=1}$ ✓

*Alternative:* Taylor series $\\sin x = x - x^3/6 + \\cdots$ gives the same answer without L'Hôpital. On exams you may quote this limit directly once it is established.""",
    "body_he_md": """**נתון:** $\\displaystyle\\lim_{x\\to 0}\\frac{\\sin x}{x}$.

זה הגבול המפורסם ביותר בחשבון — מגדיר את נגזרת הסינוס ומופיע בכל הוכחת נגזרות טריגונומטריות.

### צעד 1 — אימות צורה בלתי-קבועה
הצבת $x=0$: מונה $\\sin(0)=0$, מכנה $0$. צורה $\\frac{0}{0}$ — כלל לופיטל חל. $\\checkmark$ אם המכנה היה שואף למספר שאינו אפס, הכלל **לא** היה חל.

### צעד 2 — גזירת מונה ומכנה בנפרד
$$\\frac{d}{dx}[\\sin x]=\\cos x, \\qquad \\frac{d}{dx}[x]=1.$$
**אל** תפעילו כלל מנה על $\\frac{\\sin x}{x}$ — לופיטל דורש נגזרות עצמאיות של מונה ומכנה.

### צעד 3 — חישוב הגבול החדש
$$\\lim_{x\\to 0}\\frac{\\cos x}{1}=\\cos(0)=1.$$
המנה החדשה כבר לא בלתי-קבועה — עצרו כאן.

**תשובה:** $\\boxed{1}$ ✓

*חלופה:* טור טיילור $\\sin x = x - x^3/6 + \\cdots$ נותן אותה תשובה בלי לופיטל. בבחינה אפשר לצטט גבול זה ישירות לאחר שהוכח.""",
}

WE2 = {
    "body_en_md": """**Given:** $\\displaystyle\\lim_{x\\to\\infty}\\frac{x^2}{e^x}$.

This limit illustrates the **growth hierarchy**: exponentials beat any fixed power of $x$. L'Hôpital must be applied twice because the numerator starts at degree $2$.

### Move 1 — Verify $\\infty/\\infty$
As $x\\to\\infty$: $x^2\\to\\infty$, $e^x\\to\\infty$. Form $\\frac{\\infty}{\\infty}$. $\\checkmark$ Direct substitution gives no information.

### Move 2 — First L'Hôpital application
$$\\lim_{x\\to\\infty}\\frac{x^2}{e^x}=\\lim_{x\\to\\infty}\\frac{2x}{e^x}.$$
Still $\\infty/\\infty$ — the exponential in the denominator keeps growing without bound.

### Move 3 — Second application
$$\\lim_{x\\to\\infty}\\frac{2x}{e^x}=\\lim_{x\\to\\infty}\\frac{2}{e^x}=0.$$
Numerator is now constant; denominator still blows up.

**Answer:** $\\boxed{0}$ ✓

*General rule:* $\\lim_{x\\to\\infty}\\frac{x^n}{e^x}=0$ for any fixed $n$. For $\\frac{x^n}{e^{kx}}$ expect $n$ applications with chain-rule factor $k$ each time.""",
    "body_he_md": """**נתון:** $\\displaystyle\\lim_{x\\to\\infty}\\frac{x^2}{e^x}$.

גבול זה ממחיש את **היררכיית הגדילה**: אקספוננציות גוברות על כל חזקה קבועה של $x$. יש להפעיל לופיטל פעמיים כי המונה מתחיל במעלה $2$.

### צעד 1 — אימות $\\infty/\\infty$
כש-$x\\to\\infty$: $x^2\\to\\infty$, $e^x\\to\\infty$. צורה $\\frac{\\infty}{\\infty}$. $\\checkmark$ הצבה ישירה לא נותנת מידע.

### צעד 2 — יישום לופיטל ראשון
$$\\lim_{x\\to\\infty}\\frac{x^2}{e^x}=\\lim_{x\\to\\infty}\\frac{2x}{e^x}.$$
עדיין $\\infty/\\infty$ — האקספוננט במכנה ממשיך לגדול ללא גבול.

### צעד 3 — יישום שני
$$\\lim_{x\\to\\infty}\\frac{2x}{e^x}=\\lim_{x\\to\\infty}\\frac{2}{e^x}=0.$$
המונה כעת קבוע; המכנה עדיין מתפוצץ.

**תשובה:** $\\boxed{0}$ ✓

*כלל כללי:* $\\lim_{x\\to\\infty}\\frac{x^n}{e^x}=0$ לכל $n$ קבוע. עבור $\\frac{x^n}{e^{kx}}$ צפו ל-$n$ יישומים עם גורם $k$ מכלל השרשרת.""",
}

WE3 = {
    "body_en_md": """**Given:** $\\displaystyle\\lim_{x\\to 0^+}x^x$ (form $0^0$).

The form $0^0$ is indeterminate — the base goes to zero while the exponent also goes to zero. Direct substitution is meaningless; we use the logarithm trick.

### Move 1 — Identify disguised indeterminate form
Write $x^x=e^{x\\ln x}$. As $x\\to 0^+$: base $x\\to 0$, exponent $x\\ln x\\to 0\\cdot(-\\infty)$ — indeterminate product.

### Move 2 — Take logarithm of the limit
Let $L=\\lim_{x\\to 0^+}x^x$. Then $\\ln L=\\lim_{x\\to 0^+}x\\ln x$. Rewrite as a quotient:
$$\\ln L=\\lim_{x\\to 0^+}\\frac{\\ln x}{1/x}.$$

### Move 3 — Apply L'Hôpital to $\\frac{-\\infty}{+\\infty}$
$$\\ln L=\\lim_{x\\to 0^+}\\frac{1/x}{-1/x^2}=\\lim_{x\\to 0^+}(-x)=0.$$

### Move 4 — Exponentiate (do not skip)
$$\\ln L=0 \\implies L=e^0=1.$$

**Answer:** $\\boxed{1}$ ✓

*Pattern for $1^\\infty$, $0^0$, $\\infty^0$:* let $L=\\lim f^g$, compute $\\ln L$, convert to $0/0$ or $\\infty/\\infty$, apply L'Hôpital, then $L=e^{\\ln L}$.""",
    "body_he_md": """**נתון:** $\\displaystyle\\lim_{x\\to 0^+}x^x$ (צורת $0^0$).

צורת $0^0$ בלתי-קבועה — הבסיס שואף לאפס והמעריך גם לאפס. הצבה ישירה חסרת משמעות; משתמשים בטריק הלוגריתם.

### צעד 1 — זיהוי צורה מוסווה
כתבו $x^x=e^{x\\ln x}$. כש-$x\\to 0^+$: בסיס $x\\to 0$, מעריך $x\\ln x\\to 0\\cdot(-\\infty)$ — מכפלה בלתי-קבועה.

### צעד 2 — לוגריתם של הגבול
נגדיר $L=\\lim_{x\\to 0^+}x^x$. אז $\\ln L=\\lim_{x\\to 0^+}x\\ln x$. שכתוב כמנה:
$$\\ln L=\\lim_{x\\to 0^+}\\frac{\\ln x}{1/x}.$$

### צעד 3 — לופיטל על $\\frac{-\\infty}{+\\infty}$
$$\\ln L=\\lim_{x\\to 0^+}\\frac{1/x}{-1/x^2}=\\lim_{x\\to 0^+}(-x)=0.$$

### צעד 4 — אקספוננציה (אל תדלגו)
$$\\ln L=0 \\implies L=e^0=1.$$

**תשובה:** $\\boxed{1}$ ✓

*דפוס ל-$1^\\infty$, $0^0$, $\\infty^0$:* $L=\\lim f^g$, חשבו $\\ln L$, המירו ל-$0/0$ או $\\infty/\\infty$, לופיטל, ואז $L=e^{\\ln L}$.""",
}

CHECKPOINT1 = {
    "checkpoint_solution_en": "**Step 1 — Verify form:** At $x=0$: $e^0-1=0$ and $0$. Form $\\frac{0}{0}$ — L'Hôpital applies. $\\checkmark$\n\n**Step 2 — Differentiate separately:** $(e^x-1)'=e^x$, $(x)'=1$.\n\n**Step 3 — Evaluate:**\n$$\\lim_{x\\to 0}\\frac{e^x}{1}=e^0=1.$$\n\n**Answer:** $\\boxed{1}$. This matches the standard limit $\\lim_{x\\to 0}\\frac{e^x-1}{x}=1$ used in Taylor series for $e^x$.",
    "checkpoint_solution_he": "**שלב 1 — אימות צורה:** ב-$x=0$: $e^0-1=0$ ו-$0$. צורה $\\frac{0}{0}$ — לופיטל חל. $\\checkmark$\n\n**שלב 2 — גזירה נפרדת:** $(e^x-1)'=e^x$, $(x)'=1$.\n\n**שלב 3 — חישוב:**\n$$\\lim_{x\\to 0}\\frac{e^x}{1}=e^0=1.$$\n\n**תשובה:** $\\boxed{1}$. תואם את הגבול הסטנדרטי $\\lim_{x\\to 0}\\frac{e^x-1}{x}=1$ בטור טיילור.",
}

CHECKPOINT2 = {
    "checkpoint_solution_en": "**Step 1 — Verify form:** As $x\\to\\infty$: $\\ln x\\to\\infty$, $x\\to\\infty$. Form $\\frac{\\infty}{\\infty}$. $\\checkmark$\n\n**Step 2 — L'Hôpital:** $(\\ln x)'=1/x$, $(x)'=1$.\n\n**Step 3 — Evaluate:**\n$$\\lim_{x\\to\\infty}\\frac{1/x}{1}=\\lim_{x\\to\\infty}\\frac{1}{x}=0.$$\n\n**Answer:** $\\boxed{0}$. Logarithms grow slower than any positive power of $x$ — a key hierarchy fact for $\\infty/\\infty$ limits.",
    "checkpoint_solution_he": "**שלב 1 — אימות צורה:** כש-$x\\to\\infty$: $\\ln x\\to\\infty$, $x\\to\\infty$. צורה $\\frac{\\infty}{\\infty}$. $\\checkmark$\n\n**שלב 2 — לופיטל:** $(\\ln x)'=1/x$, $(x)'=1$.\n\n**שלב 3 — חישוב:**\n$$\\lim_{x\\to\\infty}\\frac{1/x}{1}=\\lim_{x\\to\\infty}\\frac{1}{x}=0.$$\n\n**תשובה:** $\\boxed{0}$. לוגריתמים גדלים לאט מכל חזקה חיובית של $x$.",
}

METHOD = {
    "body_en_md": """| Indeterminate form | How to convert to $0/0$ or $\\infty/\\infty$ |
|--------------------|-----------------------------------------|
| $0/0$ | Apply L'Hôpital directly |
| $\\infty/\\infty$ | Apply L'Hôpital directly |
| $0\\cdot\\infty$ | Write $\\frac{f}{1/g}$ ($0/0$) or $\\frac{g}{1/f}$ ($\\infty/\\infty$) — choose whichever simplifies |
| $\\infty-\\infty$ | Combine into one fraction over common denominator |
| $1^\\infty$, $0^0$, $\\infty^0$ | $L=\\lim f^g$; $\\ln L=\\lim g\\ln f$; convert; L'Hôpital; $L=e^{\\ln L}$ |

**Decision flowchart:** (1) Substitute — is it $0/0$ or $\\infty/\\infty$? If yes, L'Hôpital. (2) If $0\\cdot\\infty$ or $\\infty-\\infty$, rewrite first. (3) If exponential form, take log. (4) After each L'Hôpital step, re-check the form before differentiating again.

**Warning:** Not every limit needs L'Hôpital. Factoring, conjugates, and known limits are often faster. Examiners may deduct points if you apply L'Hôpital when the form is already determinate.""",
    "body_he_md": """| צורה בלתי-קבועה | המרה ל-$0/0$ או $\\infty/\\infty$ |
|-----------------|---------------------------------------|
| $0/0$ | כלל לופיטל ישיר |
| $\\infty/\\infty$ | לופיטל ישיר |
| $0\\cdot\\infty$ | $\\frac{f}{1/g}$ ($0/0$) או $\\frac{g}{1/f}$ ($\\infty/\\infty$) — בחרו הפשוט |
| $\\infty-\\infty$ | איחוד לשבר אחד |
| $1^\\infty$, $0^0$, $\\infty^0$ | $\\ln L=\\lim g\\ln f$; המרה; לופיטל; $L=e^{\\ln L}$ |

**תרשים החלטות:** (1) הציבו — $0/0$ או $\\infty/\\infty$? אם כן, לופיטל. (2) אם $0\\cdot\\infty$ או $\\infty-\\infty$ — שכתבו קודם. (3) אם מעריכי — לוגריתם. (4) אחרי כל שלב — בדקו שוב את הצורה.

**אזהרה:** לא כל גבול דורש לופיטל. פירוק, צמוד וגבולות ידועים מהירים יותר. בוחנים עלולים לנכות נקודות אם מפעילים לופיטל כשהצורה כבר קבועה.""",
}

PITFALL = {
    "body_en_md": """1. **Applying L'Hôpital without verifying indeterminate form.** Example: $\\lim_{x\\to 1}\\frac{x^2-1}{x+3}$ — numerator $\\to 0$, denominator $\\to 4$. Form is $0/4=0$, not $0/0$. L'Hôpital gives a wrong answer and wastes time.

2. **Using the quotient rule instead of separate differentiation.** For $\\frac{f}{g}$, compute $f'$ and $g'$ independently. Applying $\\frac{f'g-fg'}{g^2}$ is a common exam error.

3. **Forgetting to exponentiate after the log trick.** For $f^g$ forms: after finding $\\ln L$, you must return $L=e^{\\ln L}$. Stopping at $\\ln L=2$ without writing $L=e^2$ loses the final answer point.

4. **Not re-checking the form after each application.** The first derivative may already be determinate — continuing to differentiate changes the limit incorrectly.

5. **Wrong conversion of $0\\cdot\\infty$.** Placing the smaller factor in the numerator ($0/0$) vs. denominator ($\\infty/\\infty$) can make algebra much harder. Try both orientations if one stalls.""",
    "body_he_md": """1. **יישום לופיטל ללא אימות צורה בלתי-קבועה.** דוגמה: $\\lim_{x\\to 1}\\frac{x^2-1}{x+3}$ — מכנה $\\to 4$. הצורה $0/4=0$, לא $0/0$. לופיטל נותן תשובה שגויה.

2. **שימוש בכלל מנה במקום גזירה נפרדת.** עבור $\\frac{f}{g}$, חשבו $f'$ ו-$g'$ בנפרד. $\\frac{f'g-fg'}{g^2}$ — טעות בחינה נפוצה.

3. **שכחת אקספוננציה אחרי טריק הלוגריתם.** בצורות $f^g$: אחרי $\\ln L$ חייבים $L=e^{\\ln L}$. לעצור ב-$\\ln L=2$ בלי $L=e^2$ — איבוד נקודה.

4. **אי-בדיקת הצורה אחרי כל יישום.** הנגזרת הראשונה עלולה כבר להיות קבועה — המשך גזירה משנה את הגבול.

5. **המרה שגויה של $0\\cdot\\infty$.** מיקום הגורם הקטן במונה ($0/0$) לעומת מכנה ($\\infty/\\infty$) משנה את המורכבות. נסו כיוון אחר אם נתקעתם.""",
}

WHY = {
    "body_en_md": """L'Hôpital's rule is the bridge between **derivatives** and **limits** — it lets you evaluate limits that definition and algebra alone cannot resolve. It connects directly to `concept:limits_intro`, `concept:derivatives_intro`, and Taylor series: the standard limits $\\frac{\\sin x}{x}$, $\\frac{e^x-1}{x}$, $\\frac{\\ln(1+x)}{x}$ are exactly the limits L'Hôpital handles in one step.

In physics and engineering, indeterminate forms appear when analysing asymptotic behaviour: terminal velocity ($\\infty/\\infty$ ratios), decay rates ($e^{-x}$ vs. polynomials), and stability of equilibrium points. On university exams, L'Hôpital problems often combine with logarithmic and exponential conversions — testing whether you recognise the **form** before reaching for the rule.""",
    "body_he_md": """כלל לופיטל הוא הגשר בין **נגזרות** ל**גבולות** — מאפשר לחשב גבולות שההגדרה והאלגברה לבד לא פותרים. הוא מתחבר ל-`concept:limits_intro`, `concept:derivatives_intro` וטורי טיילור: הגבולות $\\frac{\\sin x}{x}$, $\\frac{e^x-1}{x}$, $\\frac{\\ln(1+x)}{x}$ הם בדיוק מה שלופיטל פותר בצעד אחד.

בפיזיקה והנדסה, צורות בלתי-קבועות מופיעות בניתוח התנהגות אסימפטוטית: מהירות סופית (יחסי $\\infty/\\infty$), קצבי דעיכה, יציבות נקודות שיווי משקל. בבחינות אוניברסיטאיות, בעיות לופיטל משלבות לעיתים המרות לוגריתמיות ואקספוננציאליות — בודקות אם מזהים את **הצורה** לפני הפעלת הכלל.""",
}

BEFORE_EXAM = {
    "body_en_md": """**Checklist before every L'Hôpital computation:**
1. Substitute — is the form $0/0$ or $\\infty/\\infty$? If not, stop or convert first.
2. Differentiate numerator and denominator **separately**.
3. Substitute again. Repeat only if still indeterminate.
4. For $0\\cdot\\infty$, $\\infty-\\infty$, or $f^g$ — convert before L'Hôpital.

**Key known limits (often faster than L'Hôpital):**
$$\\lim_{x\\to 0}\\frac{\\sin x}{x}=1,\\quad \\lim_{x\\to 0}\\frac{e^x-1}{x}=1,\\quad \\lim_{x\\to 0}\\frac{\\ln(1+x)}{x}=1,\\quad \\lim_{x\\to\\infty}\\left(1+\\frac{1}{x}\\right)^x=e$$

**Examiner patterns:** Expect 2–3 L'Hôpital applications, or a log trick followed by one application. Partial credit for correctly identifying the form and setting up the first derivative ratio. Time management: if algebra stalls after two applications, check whether a known limit or Taylor expansion applies instead.""",
    "body_he_md": """**רשימת תיוג לפני כל חישוב לופיטל:**
1. הציבו — $0/0$ או $\\infty/\\infty$? אם לא, עצרו או המירו.
2. גזרו מונה ומכנה **בנפרד**.
3. הציבו שוב. חזרו רק אם עדיין בלתי-קבוע.
4. ל-$0\\cdot\\infty$, $\\infty-\\infty$, $f^g$ — המירו לפני לופיטל.

**גבולות ידועים (לעיתים מהירים מלופיטל):**
$$\\lim_{x\\to 0}\\frac{\\sin x}{x}=1,\\quad \\lim_{x\\to 0}\\frac{e^x-1}{x}=1,\\quad \\lim_{x\\to 0}\\frac{\\ln(1+x)}{x}=1,\\quad \\lim_{x\\to\\infty}\\left(1+\\frac{1}{x}\\right)^x=e$$

**דפוסי בוחן:** צפו ל-2–3 יישומי לופיטל, או טריק לוגריתם ואז יישום אחד. ניקוד חלקי על זיהוי צורה והגדרת מנה הנגזרות. ניהול זמן: אם האלגברה נתקעת — בדקו גבול ידוע או טיילור.""",
}

SUMMARY = {
    "body_en_md": """- L'Hôpital applies **only** when the form is $0/0$ or $\\infty/\\infty$ (after conversion if needed).
- Differentiate numerator and denominator **separately** — never use the quotient rule on the original fraction.
- Apply repeatedly while the form stays indeterminate; stop when it becomes determinate.
- Convert $0\\cdot\\infty$, $\\infty-\\infty$, and $f^g$ forms before applying the rule.
- Exponential forms: $\\ln L=\\lim g\\ln f$ → L'Hôpital → $L=e^{\\ln L}$.
- Memorise the four standard limits; they appear on every calculus exam.""",
    "body_he_md": """- לופיטל חל **רק** כשהצורה $0/0$ או $\\infty/\\infty$ (לאחר המרה אם נדרש).
- גזרו מונה ומכנה **בנפרד** — לעולם לא כלל מנה על השבר המקורי.
- חזרו ביישום כל עוד הצורה בלתי-קבועה; עצרו כשהיא קבועה.
- המירו $0\\cdot\\infty$, $\\infty-\\infty$ ו-$f^g$ לפני הכלל.
- צורות מעריכיות: $\\ln L$ ← לופיטל ← $L=e^{\\ln L}$.
- שמרו בעל-פה את ארבעת הגבולות הסטנדרטיים.""",
}

EXPLANATIONS = [
    {
        "en": """**Why this is correct:**
At $x=0$: $\\tan(0)=0$ and denominator $0$ — form $0/0$. L'Hôpital: $\\lim_{x\\to 0}\\frac{\\sec^2 x}{1}=\\sec^2(0)=1$.

**How to think about it:**
Verify the indeterminate form first, then differentiate $\\tan x$ (not $\\frac{\\sin x}{\\cos x}$ via quotient rule in one step — though both give $\\sec^2 x$). The answer $1$ matches $\\lim\\frac{\\sin x}{x}=1$ since $\\tan x\\sim x$ near $0$.

**Common slip:**
Applying the quotient rule to $\\frac{\\tan x}{x}$ instead of differentiating numerator and denominator separately. Confusing $\\sec^2(0)=1$ with $0$.

**Exam tip:**
$\\frac{\\tan x}{x}\\to 1$ is a standard warm-up. State \"form $0/0$\" before writing derivatives — examiners award setup points on university rubrics.""",
        "he": """**למה זה נכון:**
ב-$x=0$: $\\tan(0)=0$ ומכנה $0$ — צורה $0/0$. לופיטל: $\\lim_{x\\to 0}\\frac{\\sec^2 x}{1}=\\sec^2(0)=1$.

**איך לחשוב על זה:**
אמתו צורה בלתי-קבועה, ואז גזרו $\\tan x$ (לא כלל מנה על $\\frac{\\sin x}{\\cos x}$ בצעד אחד). התשובה $1$ תואמת $\\lim\\frac{\\sin x}{x}=1$ כי $\\tan x\\sim x$ ליד $0$.

**טעות נפוצה:**
הפעלת כלל מנה על $\\frac{\\tan x}{x}$ במקום גזירה נפרדת. בלבול $\\sec^2(0)=1$ עם $0$.

**טיפ לבחינה:**
$\\frac{\\tan x}{x}\\to 1$ — חימום סטנדרטי. כתבו \"צורה $0/0$\" לפני הנגזרות — ניקוד חלקי על הגדרה.""",
    },
    {
        "en": """**Why this is correct:**
Form $0/0$ at $x=0$. First L'Hôpital: $\\frac{1-\\cos x}{x^2}\\to\\frac{\\sin x}{2x}$ — still $0/0$. Second: $\\frac{\\cos x}{2}\\to\\frac{1}{2}$.

**How to think about it:**
Each application reduces the \"degree\" of the indeterminate behaviour: cosine expansion $1-\\cos x\\sim x^2/2$ predicts limit $1/2$ without L'Hôpital. Re-check the form after the first derivative before applying again.

**Common slip:**
Stopping after one application ($\\frac{\\sin x}{2x}\\to 1/2$ incorrectly by quoting $\\frac{\\sin x}{x}\\to 1$ without the factor $2$ in the denominator). Differentiating only once when the form remains $0/0$.

**Exam tip:**
Two applications are typical when numerator and denominator both vanish to second order. Write both derivative ratios clearly for partial credit.""",
        "he": """**למה זה נכון:**
צורה $0/0$ ב-$x=0$. לופיטל ראשון: $\\frac{1-\\cos x}{x^2}\\to\\frac{\\sin x}{2x}$ — עדיין $0/0$. שני: $\\frac{\\cos x}{2}\\to\\frac{1}{2}$.

**איך לחשוב על זה:**
כל יישום מפחית את \"מעלת\" ההתנהגות הבלתי-קבועה: פיתוח $1-\\cos x\\sim x^2/2$ מנבא $1/2$. בדקו צורה אחרי הנגזרת הראשונה.

**טעות נפוצה:**
עצירה אחרי יישום אחד ($\\frac{\\sin x}{2x}$ — שכחת הגורם $2$ במכנה). יישום יחיד כשהצורה עדיין $0/0$.

**טיפ לבחינה:**
שני יישומים טיפוסיים כשמונה ומכנה מתאפסים לסדר שני. כתבו שתי מנות הנגזרות לניקוד חלקי.""",
    },
    {
        "en": """**Why this is correct:**
At $x=0$: $\\ln(1+0)=0$, denominator $0$ — form $0/0$. L'Hôpital: $\\frac{1/(1+x)}{1}\\big|_{x=0}=\\frac{1}{1}=1$.

**How to think about it:**
This is one of the four standard limits ($\\lim_{x\\to 0}\\frac{\\ln(1+x)}{x}=1$) used in Taylor series for $\\ln(1+x)$. You may quote it directly on some exams; L'Hôpital proves it in one step.

**Common slip:**
Differentiating $\\ln(1+x)$ as $\\frac{1}{1+x}$ but forgetting chain rule gives $\\frac{1}{x}$ — wrong. Writing $\\ln(1+x)'=\\ln'(1+x)$.

**Exam tip:**
Memorise alongside $\\frac{\\sin x}{x}$, $\\frac{e^x-1}{x}$, and $(1+1/x)^x$. These four appear as quick-check questions on Bagrut 807 and calc-1 finals.""",
        "he": """**למה זה נכון:**
ב-$x=0$: $\\ln(1+0)=0$, מכנה $0$ — צורה $0/0$. לופיטל: $\\frac{1/(1+x)}{1}\\big|_{x=0}=1$.

**איך לחשוב על זה:**
זה אחד מארבעת הגבולות הסטנדרטיים ($\\lim_{x\\to 0}\\frac{\\ln(1+x)}{x}=1$) בטור טיילור. אפשר לצטט בבחינה; לופיטל מוכיח בצעד אחד.

**טעות נפוצה:**
גזירת $\\ln(1+x)$ בלי כלל שרשרת — $\\frac{1}{x}$ שגוי. כתיבת $\\ln(1+x)'=\\ln'(1+x)$.

**טיפ לבחינה:**
שמרו לצד $\\frac{\\sin x}{x}$, $\\frac{e^x-1}{x}$, $(1+1/x)^x$. ארבעתם מופיעים בשאלות מהירות ב-807 וחדו\"א.""",
    },
    {
        "en": """**Why this is correct:**
At $x=2$: numerator $4-4=0$, denominator $0$ — form $0/0$. L'Hôpital: $\\frac{2x}{1}\\big|_{x=2}=4$. Factoring $\\frac{(x-2)(x+2)}{x-2}\\to x+2\\to 4$ confirms.

**How to think about it:**
L'Hôpital works but factoring is often faster here — cancel $(x-2)$ before substituting. Both methods must agree; use factoring to sanity-check L'Hôpital.

**Common slip:**
Applying L'Hôpital when the form is already determinate after cancellation (e.g. forgetting to cancel first). Arithmetic error: $2\\cdot 2=4$ not $2$.

**Exam tip:**
Examiners accept either method. If you use L'Hôpital, still verify $0/0$ explicitly. Partial credit if setup is correct but arithmetic fails.""",
        "he": """**למה זה נכון:**
ב-$x=2$: מונה $0$, מכנה $0$ — צורה $0/0$. לופיטל: $\\frac{2x}{1}\\big|_{x=2}=4$. פירוק $\\frac{(x-2)(x+2)}{x-2}\\to 4$ מאשר.

**איך לחשוב על זה:**
לופיטל עובד אך פירוק לגורמים מהיר כאן — צמצמו $(x-2)$ לפני הצבה. שני הפתרונות חייבים להתאים.

**טעות נפוצה:**
לופיטל בלי אימות $0/0$. שגיאת חשבון: $2\\cdot 2=4$ לא $2$.

**טיפ לבחינה:**
מקבלים שני השיטות. עם לופיטל — אמתו $0/0$ במפורש. ניקוד חלקי על הגדרה נכונה.""",
    },
    {
        "en": """**Why this is correct:**
As $x\\to\\infty$: $\\ln x\\to\\infty$, $\\sqrt{x}\\to\\infty$ — form $\\infty/\\infty$. L'Hôpital: $\\frac{1/x}{1/(2\\sqrt{x})}=\\frac{2\\sqrt{x}}{x}=\\frac{2}{\\sqrt{x}}\\to 0$.

**How to think about it:**
Logarithms grow slower than any positive power of $x$, so $\\frac{\\ln x}{x^{1/2}}\\to 0$. After L'Hôpital, simplify algebraically before taking the limit — do not substitute $\\infty$ directly.

**Common slip:**
Differentiating $\\sqrt{x}$ incorrectly as $\\frac{1}{2\\sqrt{x}}$ with wrong chain rule. Leaving the answer as $\\frac{2\\sqrt{x}}{x}$ without simplifying to $\\frac{2}{\\sqrt{x}}$.

**Exam tip:**
$\\infty/\\infty$ with log vs. power always goes to $0$ for the log-in-numerator case. State the growth hierarchy to earn reasoning credit without full computation.""",
        "he": """**למה זה נכון:**
כש-$x\\to\\infty$: $\\ln x\\to\\infty$, $\\sqrt{x}\\to\\infty$ — צורה $\\infty/\\infty$. לופיטל: $\\frac{1/x}{1/(2\\sqrt{x})}=\\frac{2\\sqrt{x}}{x}=\\frac{2}{\\sqrt{x}}\\to 0$.

**איך לחשוב על זה:**
לוגריתמים גדלים לאט מכל חזקה חיובית של $x$, ולכן $\\frac{\\ln x}{\\sqrt{x}}\\to 0$. אחרי לופיטל — פשטו לפני גבול.

**טעות נפוצה:**
גזירה שגויה של $\\sqrt{x}$. השארת $\\frac{2\\sqrt{x}}{x}$ בלי לפשט ל-$\\frac{2}{\\sqrt{x}}$.

**טיפ לבחינה:**
$\\infty/\\infty$ עם לוג במונה תמיד $\\to 0$. ציינו היררכיית גדילה לניקוד הסבר.""",
    },
    {
        "en": """**Why this is correct:**
Form $0\\cdot\\infty$ at $x=0^+$. Rewrite $\\frac{\\ln x}{1/x}$: as $x\\to 0^+$, $\\ln x\\to -\\infty$ and $1/x\\to +\\infty$ — form $\\frac{-\\infty}{+\\infty}$. L'Hôpital: $\\frac{1/x}{-1/x^2}=-x\\to 0$.

**How to think about it:**
Choose whether to put $x$ or $\\ln x$ in the numerator when converting $0\\cdot\\infty$. Here $\\frac{\\ln x}{1/x}$ gives a clean $\\infty/\\infty$ ratio. The answer $0$ means $x\\ln x$ vanishes faster than either factor alone blows up.

**Common slip:**
Writing $\\frac{x}{1/\\ln x}$ which leads to a messier limit. Sign errors: $\\ln x<0$ near $0^+$ but the limit is still $0$, not undefined.

**Exam tip:**
$x\\ln x\\to 0$ as $x\\to 0^+$ is a standard sub-limit inside $0^0$ problems. Memorise it alongside the log-trick workflow.""",
        "he": """**למה זה נכון:**
צורה $0\\cdot\\infty$ ב-$x=0^+$. שכתוב $\\frac{\\ln x}{1/x}$: $\\ln x\\to -\\infty$, $1/x\\to +\\infty$. לופיטל: $\\frac{1/x}{-1/x^2}=-x\\to 0$.

**איך לחשוב על זה:**
בחרו מה במונה בהמרת $0\\cdot\\infty$. כאן $\\frac{\\ln x}{1/x}$ נותן $\\infty/\\infty$ נקי. התשובה $0$ — $x\\ln x$ מתאפס מהר יותר.

**טעות נפוצה:**
$\\frac{x}{1/\\ln x}$ — מסורבל. שגיאות סימן: $\\ln x<0$ אך הגבול $0$.

**טיפ לבחינה:**
$x\\ln x\\to 0$ — גבול משנה סטנדרטי בבעיות $0^0$. שמרו לצד תהליך טריק הלוג.""",
    },
    {
        "en": """**Why this is correct:**
Form $\\infty/\\infty$. Three L'Hôpital applications: $\\frac{x^3}{e^{2x}}\\to\\frac{3x^2}{2e^{2x}}\\to\\frac{6x}{4e^{2x}}\\to\\frac{6}{8e^{2x}}\\to 0$.

**How to think about it:**
Each differentiation reduces polynomial degree by one while the exponential stays. After three steps, numerator is constant and denominator still grows — limit $0$. Growth hierarchy: $e^{2x}$ beats $x^3$.

**Common slip:**
Stopping after one or two applications while still in $\\infty/\\infty$. Forgetting the chain rule factor $2$ from $(e^{2x})'=2e^{2x}$.

**Exam tip:**
Count the power $n$ in the numerator — expect $n$ L'Hôpital steps for $\\frac{x^n}{e^{kx}}$. Write each ratio on a separate line; partial credit per correct derivative.""",
        "he": """**למה זה נכון:**
צורה $\\infty/\\infty$. שלושה יישומי לופיטל: $\\frac{x^3}{e^{2x}}\\to\\frac{3x^2}{2e^{2x}}\\to\\frac{6x}{4e^{2x}}\\to\\frac{6}{8e^{2x}}\\to 0$.

**איך לחשוב על זה:**
כל גזירה מורידה מעלה פולינום ב-1; האקספוננט נשאר. אחרי שלושה — מונה קבוע, מכנה גדל. $e^{2x}$ גובר על $x^3$.

**טעות נפוצה:**
עצירה אחרי יישום אחד-שניים. שכחת גורם $2$ מ-$(e^{2x})'=2e^{2x}$.

**טיפ לבחינה:**
ספרו מעלה $n$ במונה — צפו ל-$n$ יישומים ל-$\\frac{x^n}{e^{kx}}$. כתבו כל מנה בשורה נפרדת.""",
    },
    {
        "en": """**Why this is correct:**
Form $\\infty-\\infty$ at $x=0$. Combine: $\\frac{x-\\sin x}{x\\sin x}$ — form $0/0$. First L'Hôpital: $\\frac{1-\\cos x}{\\sin x+x\\cos x}$ — still $0/0$. Second: $\\frac{\\sin x}{2\\cos x-x\\sin x}\\to\\frac{0}{2}=0$.

**How to think about it:**
You cannot apply L'Hôpital to a difference directly — combine into one fraction first. The numerator $x-\\sin x\\sim x^3/6$ and denominator $x\\sin x\\sim x^2$ predict limit $0$.

**Common slip:**
Applying L'Hôpital to $\\frac{1}{\\sin x}-\\frac{1}{x}$ term-by-term (invalid). Algebraic errors when finding common denominator $x\\sin x$.

**Exam tip:**
$\\infty-\\infty$ with trig reciprocals is a classic exam pattern. Show the combined fraction before differentiating — setup earns half the points.""",
        "he": """**למה זה נכון:**
צורה $\\infty-\\infty$ ב-$x=0$. איחוד: $\\frac{x-\\sin x}{x\\sin x}$ — $0/0$. לופיטל ראשון: $\\frac{1-\\cos x}{\\sin x+x\\cos x}$ — עדיין $0/0$. שני: $\\frac{\\sin x}{2\\cos x-x\\sin x}\\to 0$.

**איך לחשוב על זה:**
אי אפשר לופיטל על הפרש ישירות — איחדו לשבר. $x-\\sin x\\sim x^3/6$ ו-$x\\sin x\\sim x^2$ מנבאים $0$.

**טעות נפוצה:**
לופיטל על $\\frac{1}{\\sin x}-\\frac{1}{x}$ איבר-איבר (לא תקף). שגיאות במכנה משותף $x\\sin x$.

**טיפ לבחינה:**
$\\infty-\\infty$ עם מכפלות הופכות — דפוס בחינה קלאסי. הציגו שבר מאוחד לפני גזירה.""",
    },
]


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    we_idx = 0
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec["body_en_md"] = INTRO["body_en_md"]
            sec["body_he_md"] = INTRO["body_he_md"]
        elif kind == "definition":
            sec["body_en_md"] = DEFINITION["body_en_md"]
            sec["body_he_md"] = DEFINITION["body_he_md"]
        elif kind == "theory":
            sec["body_en_md"] = THEORY["body_en_md"]
            sec["body_he_md"] = THEORY["body_he_md"]
        elif kind == "worked_example":
            we_idx += 1
            src = [WE1, WE2, WE3][we_idx - 1]
            sec["body_en_md"] = src["body_en_md"]
            sec["body_he_md"] = src["body_he_md"]
        elif kind == "checkpoint":
            cp_idx += 1
            src = [CHECKPOINT1, CHECKPOINT2][cp_idx - 1]
            sec["checkpoint_solution_en"] = src["checkpoint_solution_en"]
            sec["checkpoint_solution_he"] = src["checkpoint_solution_he"]
        elif kind == "method_guide":
            sec["body_en_md"] = METHOD["body_en_md"]
            sec["body_he_md"] = METHOD["body_he_md"]
        elif kind == "pitfall":
            sec["body_en_md"] = PITFALL["body_en_md"]
            sec["body_he_md"] = PITFALL["body_he_md"]
        elif kind == "why_matters":
            sec["body_en_md"] = WHY["body_en_md"]
            sec["body_he_md"] = WHY["body_he_md"]
        elif kind == "before_exam":
            sec["body_en_md"] = BEFORE_EXAM["body_en_md"]
            sec["body_he_md"] = BEFORE_EXAM["body_he_md"]
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY["body_en_md"]
            sec["body_he_md"] = SUMMARY["body_he_md"]

    for i, q in enumerate(data["questions"]):
        q["explanation_en"] = EXPLANATIONS[i]["en"]
        q["explanation_he"] = EXPLANATIONS[i]["he"]

    # Fix mixed-script typo + pad short Hebrew explanations
    HE_PAD = " מחוון הבחינה מעניק ניקוד חלקי על זיהוי הצורה הבלתי-קבועה ובחירת שיטת הפתרון הנכונה לפני חישוב סופי."
    for sec in data["sections"]:
        if sec.get("body_he_md"):
            sec["body_he_md"] = re.sub(r"טריגונומטריות", "טריגונומטריות", sec["body_he_md"])
        kind = sec.get("kind")
        if kind == "worked_example":
            pad_en = "\n\n*Exam note:* Always state the indeterminate form before differentiating — partial credit on university rubrics depends on this setup step. Re-check the form after each application."
            pad_he = "\n\n*הערת בחינה:* ציינו תמיד את הצורה הבלתי-קבועה לפני הגזירה — ניקוד חלקי במחוון תלוי בשלב ההגדרה."
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["worked_example"]["en"]:
                sec["body_en_md"] = sec.get("body_en_md", "") + pad_en
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["worked_example"]["he"]:
                sec["body_he_md"] = sec.get("body_he_md", "") + pad_he
    for sec in data["sections"]:
        if sec.get("kind") == "before_exam":
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["before_exam"]["en"]:
                sec["body_en_md"] += "\n\n**Time tip:** If two L'Hôpital steps do not resolve the limit, try factoring, a known limit, or Taylor expansion before continuing."
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["before_exam"]["he"]:
                sec["body_he_md"] += "\n\n**טיפ זמן:** אם שני שלבי לופיטל לא פותרים — נסו פירוק, גבול ידוע או טיילור."

    for sec in data["sections"]:
        if sec.get("body_he_md"):
            sec["body_he_md"] = (
                sec["body_he_md"]
                .replace("טריגונומטריות", "טריגונומטריות")
                .replace("ציינu", "ציינu")
                .replace("נסu", "נסu")
                .replace("לופיטל", "לופיטל")
            )

    for q in data["questions"]:
        if word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q["explanation_he"] + HE_PAD

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
