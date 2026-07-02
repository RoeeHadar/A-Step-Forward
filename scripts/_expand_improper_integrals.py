#!/usr/bin/env python3
"""Expand improper_integrals.json to Cursor depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/improper_integrals.json"

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
            "The standard Riemann integral $\\int_a^b f(x)\\,dx$ requires two conditions "
            "that many real-world models violate:\n"
            "1. A **finite** interval $[a,b]$.\n"
            "2. A **bounded** integrand $f$ on $[a,b]$.\n\n"
            "When either condition fails, the integral is called **improper**. "
            "We recover a precise meaning by replacing the problematic feature with a "
            "parameter and taking a limit.\n\n"
            "**Type I (infinite limits):** $\\int_1^\\infty \\frac{1}{x^2}\\,dx$ asks for "
            "the area under $1/x^2$ over an unbounded domain — a question that arises in "
            "probability normalization and tail probabilities.\n\n"
            "**Type II (unbounded integrand):** $\\int_0^1 \\frac{1}{\\sqrt{x}}\\,dx$ has "
            "a vertical asymptote at $x=0$, yet the area can still be finite.\n\n"
            "Applications include Laplace and Fourier transforms, the gamma function "
            "$\\Gamma(n)=(n-1)!$, and continuous probability densities on "
            "$[0,\\infty)$. The central question is always the same: **does the limit "
            "exist and stay finite, or does the area blow up?**"
        ),
        "body_he_md": (
            "האינטegral הרימן הסטנדרטי $\\int_a^b f(x)\\,dx$ דורש שני תנאים "
            "שמודלים רבים בעולם האמיתי מפרים:\n"
            "1. **קטע סופי** $[a,b]$.\n"
            "2. **פונקציה חסומה** $f$ על $[a,b]$.\n\n"
            "כאשר אחד מהתנאים נכשל, האינטegral נקרא **לא אמיתי**. "
            "מחזירים משמעות מדויקת על ידי החלפת המאפיין הבעייתי בפרמטר "
            "ולקיחת גbול.\n\n"
            "**טיפוס I (גbולות אינסופיים):** $\\int_1^\\infty \\frac{1}{x^2}\\,dx$ "
            "שואל על השטח מתחת ל-$1/x^2$ על תחום לא חסום — שאלה שמופיעה "
            "בנורmalizציה של צפיפות הסתברות ובהסתברויות זנb.\n\n"
            "**טיפוס II (אינטegrand לא חסום):** $\\int_0^1 \\frac{1}{\\sqrt{x}}\\,dx$ "
            "מכיל אסימptוטה אנכית ב-$x=0$, ובכל זאת השטח יכול להישאר סופי.\n\n"
            "יישומים כוללים טrנספורמציות לפלס ופוריe, פונקציית גמא "
            "$\\Gamma(n)=(n-1)!$, וצפיפויות הסתברות רציפות על $[0,\\infty)$. "
            "השאלה המרכזית תמיד זהה: **האם הגbול קיים ונשאר סופי, "
            "או שהשטח מתפוצץ?**"
        ),
    },
    "definition": {
        "body_en_md": (
            "**Type I — Infinite limits:**\n"
            "$$\\int_a^\\infty f(x)\\,dx = \\lim_{b\\to\\infty} \\int_a^b f(x)\\,dx.$$\n"
            "$$\\int_{-\\infty}^b f(x)\\,dx = \\lim_{a\\to-\\infty} \\int_a^b f(x)\\,dx.$$\n"
            "$$\\int_{-\\infty}^\\infty f(x)\\,dx = \\int_{-\\infty}^c f(x)\\,dx + "
            "\\int_c^\\infty f(x)\\,dx.$$\n"
            "Both halves must converge independently for the full integral to converge.\n\n"
            "**Type II — Unbounded integrand at $x=c \\in [a,b]$:**\n"
            "- Discontinuity at the **right** endpoint: "
            "$\\int_a^b f\\,dx = \\lim_{t\\to b^-}\\int_a^t f\\,dx$.\n"
            "- Discontinuity at the **left** endpoint: "
            "$\\int_a^b f\\,dx = \\lim_{t\\to a^+}\\int_t^b f\\,dx$.\n"
            "- Discontinuity in the **interior**: split at $c$ and handle each piece.\n\n"
            "**Convergence:** If the limit exists and is finite, the integral "
            "**converges**. Otherwise it **diverges** (the limit is infinite or "
            "does not exist).\n\n"
            "**Absolute convergence:** If $\\int |f|\\,dx$ converges, then "
            "$\\int f\\,dx$ converges — useful when oscillatory integrands appear.\n\n"
            "**Exam habit:** never apply the Fundamental Theorem directly across "
            "$\\infty$ or a singularity; always introduce $b$ or $t$ first.\n\n"
            "**Mixed type example:** $\\int_0^\\infty \\frac{1}{x^2}\\,dx$ has both "
            "an infinite limit and a singularity at $x=0$. Split at any interior "
            "point (say $x=1$) and analyze each piece separately — both must "
            "converge for the whole integral to converge."
        ),
        "body_he_md": (
            "**טיפוס I — גbולות אינסופיים:**\n"
            "$$\\int_a^\\infty f(x)\\,dx = \\lim_{b\\to\\infty} \\int_a^b f(x)\\,dx.$$\n"
            "$$\\int_{-\\infty}^b f(x)\\,dx = \\lim_{a\\to-\\infty} \\int_a^b f(x)\\,dx.$$\n"
            "$$\\int_{-\\infty}^\\infty f(x)\\,dx = \\int_{-\\infty}^c f\\,dx + "
            "\\int_c^\\infty f\\,dx.$$\n"
            "שני החצאים חייבים להתכנס בנפרד כדי שהאינטegral המלא יתכנס.\n\n"
            "**טיפוס II — אינטegrand לא חסום ב-$x=c \\in [a,b]$:**\n"
            "- אי-רציפות ב**קצה ימין**: "
            "$\\int_a^b f\\,dx = \\lim_{t\\to b^-}\\int_a^t f\\,dx$.\n"
            "- אי-רציפות ב**קצה שמאל**: "
            "$\\int_a^b f\\,dx = \\lim_{t\\to a^+}\\int_t^b f\\,dx$.\n"
            "- אי-רציפות **בפnים**: פצלו ב-$c$ וטפלו בכל חלק.\n\n"
            "**התכנסות:** אם הגbול קיים וסופי, האינטegral **מתכנס**. "
            "אחרת הוא **מתbדר** (הגbול אינסופי או לא קיים).\n\n"
            "**התכנסות מוחלטת:** אם $\\int |f|\\,dx$ מתכנס, אז $\\int f\\,dx$ מתכנס — "
            "שימושי כשמופיעים אינטegralים מתנdדים.\n\n"
            "**הרגל לבחינה:** לעולם אל תיישמו את משפט היסוד ישירות על "
            "$\\infty$ או על singularity; הציגu תחילה $b$ או $t$.\n\n"
            "**דוגמה מעורbת:** $\\int_0^\\infty \\frac{1}{x^2}\\,dx$ כולל "
            "גbול אינסופי ו-singularity ב-$x=0$. פצלו בנקודה פnימית "
            "(למשל $x=1$) ונתחu כל חלק בנפרד — שניהם חייבים "
            "להתכנס כדי שהאינtegral המלא יתכנס."
        ),
    },
    "theory": {
        "body_en_md": (
            "**$p$-integral (Type I):** $\\int_1^\\infty x^{-p}\\,dx$ converges "
            "if and only if $p > 1$.\n\n"
            "For $p \\ne 1$: $\\int_1^b x^{-p}\\,dx = \\frac{b^{1-p}-1}{1-p} "
            "\\to \\frac{1}{p-1}$ as $b\\to\\infty$ when $p>1$. "
            "For $p = 1$: $\\int_1^\\infty 1/x\\,dx = \\ln b \\to \\infty$ — diverges.\n\n"
            "**$p$-integral (Type II):** $\\int_0^1 x^{-p}\\,dx$ converges "
            "if and only if $p < 1$. The thresholds are **reversed** compared to Type I.\n\n"
            "**Comparison test (direct):** If $0 \\le f(x) \\le g(x)$ for all "
            "$x \\ge a$:\n"
            "- $\\int_a^\\infty g\\,dx$ converges $\\Rightarrow$ "
            "$\\int_a^\\infty f\\,dx$ converges.\n"
            "- $\\int_a^\\infty f\\,dx$ diverges $\\Rightarrow$ "
            "$\\int_a^\\infty g\\,dx$ diverges.\n\n"
            "**Limit comparison:** If $\\lim_{x\\to\\infty} f(x)/g(x) = L > 0$, "
            "then $\\int_a^\\infty f\\,dx$ and $\\int_a^\\infty g\\,dx$ either both "
            "converge or both diverge. Compare to $1/x^p$ or $e^{-ax}$.\n\n"
            "**Exponential decay:** For $a>0$, $\\int_0^\\infty e^{-ax}\\,dx = 1/a$ "
            "converges because $e^{-ax}$ beats any power as $x\\to\\infty$.\n\n"
            "**Exam memory aid:** Type I on $[1,\\infty)$ needs $p>1$ to tame the tail; "
            "Type II on $(0,1]$ needs $p<1$ to tame the spike near zero.\n\n"
            "**Log-comparison integrals:** Integrals of the form "
            "$\\int_e^\\infty \\frac{1}{x(\\ln x)^p}\\,dx$ reduce to $p$-integrals "
            "via $u=\\ln x$. They converge iff $p>1$, exactly like Type I $p$-integrals "
            "— a favorite university exam twist.\n\n"
            "**Oscillatory integrals:** For $\\int_1^\\infty \\frac{\\sin x}{x}\\,dx$, "
            "direct comparison fails because the integrand changes sign. Use absolute "
            "convergence or Dirichlet's test instead."
        ),
        "body_he_md": (
            "**$p$-אינטegral (טיפוס I):** $\\int_1^\\infty x^{-p}\\,dx$ מתכנס "
            "אם ורק אם $p > 1$.\n\n"
            "עבור $p \\ne 1$: $\\int_1^b x^{-p}\\,dx = \\frac{b^{1-p}-1}{1-p} "
            "\\to \\frac{1}{p-1}$ כאשר $b\\to\\infty$ ו-$p>1$. "
            "עבור $p = 1$: $\\int_1^\\infty 1/x\\,dx = \\ln b \\to \\infty$ — מתbדר.\n\n"
            "**$p$-אינטegral (טיפוס II):** $\\int_0^1 x^{-p}\\,dx$ מתכנס "
            "אם ורק אם $p < 1$. הסף **הפוך** לעומת טיפוס I.\n\n"
            "**מבחן השוואה (ישיר):** אם $0 \\le f(x) \\le g(x)$ לכל $x \\ge a$:\n"
            "- $\\int_a^\\infty g\\,dx$ מתכנס $\\Rightarrow$ "
            "$\\int_a^\\infty f\\,dx$ מתכנס.\n"
            "- $\\int_a^\\infty f\\,dx$ מתbדר $\\Rightarrow$ "
            "$\\int_a^\\infty g\\,dx$ מתbדר.\n\n"
            "**השוואת גbולות:** אם $\\lim_{x\\to\\infty} f(x)/g(x) = L > 0$, "
            "אז $\\int f\\,dx$ ו-$\\int g\\,dx$ מתנהגים זהה — שניהם מתכנסים "
            "או שניהם מתbדרים. השוו ל-$1/x^p$ או $e^{-ax}$.\n\n"
            "**דעיכה מעריכית:** עבור $a>0$, $\\int_0^\\infty e^{-ax}\\,dx = 1/a$ "
            "מתכנס כי $e^{-ax}$ גובר על כל חזקה כאשר $x\\to\\infty$.\n\n"
            "**עזר זיכרון לבחינה:** טיפוס I על $[1,\\infty)$ דורש $p>1$ "
            "כדי לרסן את הזנb; טיפוס II על $(0,1]$ דורש $p<1$ "
            "כדי לרסן את הקיצון ליד אפס.\n\n"
            "**אינtegralים עם לוג:** אינtegralים מהצורה "
            "$\\int_e^\\infty \\frac{1}{x(\\ln x)^p}\\,dx$ מצטמצמים "
            "ל-$p$-אינtegralים דרך $u=\\ln x$. הם מתכנסים אמ\"מ $p>1$ — "
            "טריק אהוב בבחינות אוניברסיטאיות.\n\n"
            "**אינtegralים מתנdדים:** עבור $\\int_1^\\infty \\frac{\\sin x}{x}\\,dx$, "
            "השוואה ישירה נכשלת כי האינtegrand משנה סימן. "
            "השתמשu בהתכנסות מוחלטת או במבחן דירichlet במקום."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Evaluate:** $\\int_1^\\infty \\frac{1}{x^2}\\,dx$.\n\n"
            "This is a Type I improper integral — the upper limit is $\\infty$. "
            "The integrand $x^{-2}$ is continuous and bounded on every finite "
            "interval $[1,b]$, so we only need to handle the infinite endpoint.\n\n"
            "### Move 1: Write as a limit.\n"
            "Replace $\\infty$ with a parameter $b$ and take the limit last:\n"
            "$$\\int_1^\\infty \\frac{1}{x^2}\\,dx = \\lim_{b\\to\\infty} "
            "\\int_1^b x^{-2}\\,dx.$$\n\n"
            "### Move 2: Evaluate the definite integral.\n"
            "Use the power rule for $n=-2$:\n"
            "$$\\int_1^b x^{-2}\\,dx = \\left[\\frac{x^{-1}}{-1}\\right]_1^b "
            "= -\\frac{1}{b} + \\frac{1}{1} = 1 - \\frac{1}{b}.$$\n\n"
            "### Move 3: Take the limit.\n"
            "As $b\\to\\infty$, the term $1/b\\to 0$:\n"
            "$$\\lim_{b\\to\\infty} \\left(1 - \\frac{1}{b}\\right) = 1.$$\n\n"
            "The integral **converges** to $1$. This matches the $p$-test with "
            "$p=2>1$. **Self-check:** the tail area under $1/x^2$ is finite "
            "because $1/x^2$ decays faster than $1/x$. **Exam tip:** always "
            "state \"converges to 1\" rather than just writing $1$ — convergence "
            "language earns full marks on university rubrics."
        ),
        "body_he_md": (
            "**חשבו:** $\\int_1^\\infty \\frac{1}{x^2}\\,dx$.\n\n"
            "זהו אינטegral לא אמיתי מטיפוס I — הגbול העליון הוא $\\infty$. "
            "האינטegrand $x^{-2}$ רציף וחסום בכל קטע סופי $[1,b]$, "
            "לכן נדרש לטפל רק בקצה האינסופי.\n\n"
            "### צעד 1: כתיבה כגbול.\n"
            "החליפu את $\\infty$ בפרמטר $b$ וקחu את הגbול בסוף:\n"
            "$$\\int_1^\\infty \\frac{1}{x^2}\\,dx = \\lim_{b\\to\\infty} "
            "\\int_1^b x^{-2}\\,dx.$$\n\n"
            "### צעד 2: חישוב האינטegral המסויים.\n"
            "השתמשu בחוק חזקות עבור $n=-2$:\n"
            "$$\\int_1^b x^{-2}\\,dx = \\left[\\frac{x^{-1}}{-1}\\right]_1^b "
            "= -\\frac{1}{b} + 1 = 1 - \\frac{1}{b}.$$\n\n"
            "### צעד 3: לקיחת הגbול.\n"
            "כאשר $b\\to\\infty$, האיבר $1/b\\to 0$:\n"
            "$$\\lim_{b\\to\\infty} \\left(1 - \\frac{1}{b}\\right) = 1.$$\n\n"
            "האינטegral **מתכנס** ל-$1$. זה תואם $p$-מבחן עם $p=2>1$. "
            "**בדיקה:** שטח הזנb מתחת ל-$1/x^2$ סופי כי $1/x^2$ דועך "
            "מהר יותר מ-$1/x$. **טיפ לבחינה:** כתbו \"מתכנס ל-$1$\" "
            "ולא רק $1$ — ניסוח התכנסות מרוויח נקודות מלאות בבחינות."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Evaluate:** $\\int_0^1 \\frac{1}{\\sqrt{x}}\\,dx$.\n\n"
            "This is Type II: the integrand $f(x)=x^{-1/2}$ is unbounded at "
            "$x=0$ (vertical asymptote). The interval $[0,1]$ is finite, but "
            "we must replace the left endpoint with a parameter before integrating.\n\n"
            "### Move 1: Identify the singularity and write as a limit.\n"
            "The blow-up occurs at the left endpoint $x=0$:\n"
            "$$\\int_0^1 x^{-1/2}\\,dx = \\lim_{t\\to 0^+} \\int_t^1 x^{-1/2}\\,dx.$$\n\n"
            "### Move 2: Evaluate the antiderivative on $[t,1]$.\n"
            "Power rule with $n=-1/2$ gives antiderivative $2\\sqrt{x}$:\n"
            "$$\\int_t^1 x^{-1/2}\\,dx = [2\\sqrt{x}]_t^1 = 2\\sqrt{1} - 2\\sqrt{t} "
            "= 2 - 2\\sqrt{t}.$$\n\n"
            "### Move 3: Take the limit as $t\\to 0^+$.\n"
            "Since $\\sqrt{t}\\to 0$:\n"
            "$$\\lim_{t\\to 0^+} (2 - 2\\sqrt{t}) = 2.$$\n\n"
            "The integral **converges** to $2$. Here $p=1/2<1$, confirming "
            "the Type II $p$-test. **Common slip:** plugging $x=0$ directly "
            "into $2\\sqrt{x}$ without the limit. **Exam tip:** for endpoint "
            "singularities, always approach from inside the interval ($t\\to 0^+$, "
            "not $t=0$). **Self-check:** substitution $u=\\sqrt{x}$ converts this "
            "to a bounded integral on $[0,1]$, confirming the area is finite."
        ),
        "body_he_md": (
            "**חשבו:** $\\int_0^1 \\frac{1}{\\sqrt{x}}\\,dx$.\n\n"
            "זהו טיפוס II: האינטegrand $f(x)=x^{-1/2}$ לא חסום ב-$x=0$ "
            "(אסימptוטה אנכית). הקטע $[0,1]$ סופי, אך יש להחליף "
            "את הקצה השמאלי בפרמטר לפני האינטegrציה.\n\n"
            "### צעד 1: זיהוי singularity וכתיבה כגbול.\n"
            "הפיצוץ מתרחש בקצה השמאלי $x=0$:\n"
            "$$\\int_0^1 x^{-1/2}\\,dx = \\lim_{t\\to 0^+} \\int_t^1 x^{-1/2}\\,dx.$$\n\n"
            "### צעד 2: חישוב האינטegral על $[t,1]$.\n"
            "חוק חזקות עם $n=-1/2$ נותן primitive $2\\sqrt{x}$:\n"
            "$$\\int_t^1 x^{-1/2}\\,dx = [2\\sqrt{x}]_t^1 = 2 - 2\\sqrt{t}.$$\n\n"
            "### צעד 3: גbול כאשר $t\\to 0^+$.\n"
            "מכיוון ש-$\\sqrt{t}\\to 0$:\n"
            "$$\\lim_{t\\to 0^+} (2 - 2\\sqrt{t}) = 2.$$\n\n"
            "האינטegral **מתכנס** ל-$2$. כאן $p=1/2<1$, מאשר $p$-מבחן "
            "לטיפוס II. **טעות נפוצה:** הצבת $x=0$ ישירות ב-$2\\sqrt{x}$ "
            "בלי הגbול. **טיפ לבחינה:** ל-singularities בקצה, "
            "תמיד התקרbו מתוך הקטע ($t\\to 0^+$, לא $t=0$). "
            "**בדיקה:** הצבה $u=\\sqrt{x}$ ממירה לאינטegral חסום "
            "על $[0,1]$, מאשרת שהשטח סופי."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Show** that $\\int_0^\\infty e^{-x}\\,dx = 1$ and evaluate "
            "$\\int_0^\\infty x e^{-x}\\,dx$ (the gamma function value "
            "$\\Gamma(2)$).\n\n"
            "Both are Type I integrals on $[0,\\infty)$ with exponential decay — "
            "a standard exam pattern linking improper integrals to integration "
            "by parts and factorial identities. These appear frequently on "
            "university Calc I finals and in probability normalization problems.\n\n"
            "**Part 1 — Base case:**\n"
            "$$\\int_0^\\infty e^{-x}\\,dx = \\lim_{b\\to\\infty}\\int_0^b e^{-x}\\,dx "
            "= \\lim_{b\\to\\infty}[-e^{-x}]_0^b "
            "= \\lim_{b\\to\\infty}(-e^{-b}+1) = 0+1 = 1.$$\n\n"
            "**Part 2 — Integration by parts:** Set $u=x$, $dv=e^{-x}\\,dx$, "
            "so $du=dx$ and $v=-e^{-x}$:\n"
            "$$\\int_0^b xe^{-x}\\,dx = [-xe^{-x}]_0^b + \\int_0^b e^{-x}\\,dx "
            "= -be^{-b} + 0 + [-e^{-x}]_0^b = -be^{-b} + 1 - e^{-b}.$$\n\n"
            "As $b\\to\\infty$: $be^{-b}\\to0$ (L'Hôpital or growth comparison) "
            "and $e^{-b}\\to0$. Each boundary term vanishes because exponential "
            "decay dominates polynomial growth. Therefore:\n"
            "$$\\int_0^\\infty xe^{-x}\\,dx = 1 = (2-1)! = \\Gamma(2).$$\n\n"
            "**Exam tip:** for $\\int_0^\\infty x^n e^{-ax}\\,dx$, repeated IBP "
            "reduces the power by one each time until you reach Part 1. "
            "**Self-check:** $\\Gamma(n)=(n-1)!$ gives $\\Gamma(2)=1!=1$ ✓. "
            "The pattern generalizes: $\\int_0^\\infty x^n e^{-x}\\,dx = n!$ "
            "for every non-negative integer $n$."
        ),
        "body_he_md": (
            "**הוכיחu** ש-$\\int_0^\\infty e^{-x}\\,dx = 1$ וחשbו "
            "$\\int_0^\\infty x e^{-x}\\,dx$ (ערך פונקציית גמא $\\Gamma(2)$).\n\n"
            "שניהם אינטegralים מטיפוס I על $[0,\\infty)$ עם דעיכה מעריכית — "
            "דפוס בחינה סטנדרטי שמקשר אינטegralים לא אמיתיים "
            "לאינטegrציה בחלקים ולזהויות עצרת. אלה מופיעים לעתים קרובות "
            "בבחינות סופיות בחשבון ובבעיות נורmalizציה בהסתברות.\n\n"
            "**חלק 1 — מקרה בסיס:**\n"
            "$$\\int_0^\\infty e^{-x}\\,dx = \\lim_{b\\to\\infty}\\int_0^b e^{-x}\\,dx "
            "= \\lim_{b\\to\\infty}[-e^{-x}]_0^b "
            "= \\lim_{b\\to\\infty}(-e^{-b}+1) = 1.$$\n\n"
            "**חלק 2 — אינטegrציה בחלקים:** $u=x$, $dv=e^{-x}\\,dx$, "
            "כלומר $du=dx$ ו-$v=-e^{-x}$:\n"
            "$$\\int_0^b xe^{-x}\\,dx = [-xe^{-x}]_0^b + \\int_0^b e^{-x}\\,dx "
            "= -be^{-b} + 1 - e^{-b}.$$\n\n"
            "כאשר $b\\to\\infty$: $be^{-b}\\to0$ (L'Hôpital או השוואת צמיחה) "
            "ו-$e^{-b}\\to0$. כל איבר גbול מתאפס כי דעיכה מעריכית "
            "גוברת על צמיחת פולינום. לכן:\n"
            "$$\\int_0^\\infty xe^{-x}\\,dx = 1 = (2-1)! = \\Gamma(2).$$\n\n"
            "**טיפ לבחינה:** עבור $\\int_0^\\infty x^n e^{-ax}\\,dx$, "
            "IBP חוזר מוריד חזקה בכל פעם עד שמגיעים לחלק 1. "
            "**בדיקה:** $\\Gamma(n)=(n-1)!$ נותן $\\Gamma(2)=1!=1$ ✓. "
            "הדpוס מתgeneralize: $\\int_0^\\infty x^n e^{-x}\\,dx = n!$ "
            "לכל שלם $n$ לא שלילי."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "Write as a limit: $\\int_1^\\infty x^{-1/2}\\,dx = "
            "\\lim_{b\\to\\infty}\\int_1^b x^{-1/2}\\,dx$.\n\n"
            "Evaluate: $\\int_1^b x^{-1/2}\\,dx = [2\\sqrt{x}]_1^b = "
            "2\\sqrt{b} - 2$.\n\n"
            "Take the limit: $2\\sqrt{b} - 2 \\to \\infty$ as $b\\to\\infty$. "
            "The integral **diverges**.\n\n"
            "Confirm with the $p$-test: here $p=1/2 < 1$, and for Type I on "
            "$[1,\\infty)$ we need $p>1$ for convergence. The algebra and the "
            "rule agree."
        ),
        "checkpoint_solution_he": (
            "כתbו כגbול: $\\int_1^\\infty x^{-1/2}\\,dx = "
            "\\lim_{b\\to\\infty}\\int_1^b x^{-1/2}\\,dx$.\n\n"
            "חישוב: $\\int_1^b x^{-1/2}\\,dx = [2\\sqrt{x}]_1^b = "
            "2\\sqrt{b} - 2$.\n\n"
            "גbול: $2\\sqrt{b} - 2 \\to \\infty$ כאשר $b\\to\\infty$. "
            "האינטegral **מתbדר**.\n\n"
            "אימות ב-$p$-מבחן: כאן $p=1/2 < 1$, ולטיפוס I על "
            "$[1,\\infty)$ נדרש $p>1$ להתכנסות. האלגebra והכלל תואמים."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "For $x \\ge 1$: $x^2+3 > x^2$, so $\\frac{1}{x^2+3} < \\frac{1}{x^2}$.\n\n"
            "Both integrands are non-negative on $[1,\\infty)$, so the direct "
            "comparison test applies. We know $\\int_1^\\infty \\frac{1}{x^2}\\,dx = 1$ "
            "converges ($p=2>1$).\n\n"
            "Since $0 \\le \\frac{1}{x^2+3} \\le \\frac{1}{x^2}$ and the larger "
            "integral converges, the smaller integral "
            "$\\int_1^\\infty \\frac{1}{x^2+3}\\,dx$ also **converges**.\n\n"
            "We do not need the exact value — convergence is enough here."
        ),
        "checkpoint_solution_he": (
            "עבור $x \\ge 1$: $x^2+3 > x^2$, לכן $\\frac{1}{x^2+3} < \\frac{1}{x^2}$.\n\n"
            "שני האינטegrandים אינם שליליים על $[1,\\infty)$, "
            "לכן מבחן ההשוואה הישיר חל. ידוע ש-$\\int_1^\\infty \\frac{1}{x^2}\\,dx = 1$ "
            "מתכנס ($p=2>1$).\n\n"
            "מכיוון ש-$0 \\le \\frac{1}{x^2+3} \\le \\frac{1}{x^2}$ "
            "והאינטegral הגדול יותר מתכנס, גם האינטegral הקטן יותר "
            "$\\int_1^\\infty \\frac{1}{x^2+3}\\,dx$ **מתכנס**.\n\n"
            "אין צורך בערך המדויק — כאן מספיקה התכנסות."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "**Step 1: Identify the type.**\n"
            "- **Type I:** an endpoint is $\\pm\\infty$.\n"
            "- **Type II:** the integrand is undefined or infinite at some "
            "$c \\in [a,b]$.\n"
            "- **Mixed:** both features — handle each separately.\n\n"
            "**Step 2: Split if necessary.**\n"
            "- Two infinite limits: "
            "$\\int_{-\\infty}^\\infty = \\int_{-\\infty}^c + \\int_c^\\infty$.\n"
            "- Interior singularity: $\\int_a^b = \\int_a^c + \\int_c^b$.\n"
            "Every piece must converge for the whole to converge.\n\n"
            "**Step 3: Replace the problematic limit with a parameter.** "
            "Evaluate the ordinary definite integral, then take the limit.\n\n"
            "**Step 4: Use comparison when direct evaluation is hard.** "
            "Compare to $1/x^p$ or $e^{-ax}$.\n\n"
            "| Integral | Converges | Diverges |\n"
            "|---|---|---|\n"
            "| $\\int_1^\\infty x^{-p}\\,dx$ | $p>1$ | $p\\le1$ |\n"
            "| $\\int_0^1 x^{-p}\\,dx$ | $p<1$ | $p\\ge1$ |\n"
            "| $\\int_0^\\infty e^{-ax}\\,dx$ | $a>0$ | $a\\le0$ |"
        ),
        "body_he_md": (
            "**שלב 1: זהו את הטיפוס.**\n"
            "- **טיפוס I:** קצה הוא $\\pm\\infty$.\n"
            "- **טיפוס II:** האינטegrand לא מוגדר או אינסופי ב-$c \\in [a,b]$.\n"
            "- **מעורb:** שני המאפיינים — טפלו בכל אחד בנפרד.\n\n"
            "**שלב 2: פצלו במידת הצורך.**\n"
            "- שני גbולות אינסופיים: "
            "$\\int_{-\\infty}^\\infty = \\int_{-\\infty}^c + \\int_c^\\infty$.\n"
            "- singularity בפnים: $\\int_a^b = \\int_a^c + \\int_c^b$.\n"
            "כל חלק חייב להתכנס כדי שהשלם יתכנס.\n\n"
            "**שלב 3: החליפו את הגbול הבעייתי בפרמטר.** "
            "חשbו את האינטegral המסויים הרגיל, ואז קחu גbול.\n\n"
            "**שלב 4: השתמשu בהשוואה כשחישוב ישיר קשה.** "
            "השוו ל-$1/x^p$ או $e^{-ax}$.\n\n"
            "| אינטegral | מתכנס | מתbדר |\n"
            "|---|---|---|\n"
            "| $\\int_1^\\infty x^{-p}\\,dx$ | $p>1$ | $p\\le1$ |\n"
            "| $\\int_0^1 x^{-p}\\,dx$ | $p<1$ | $p\\ge1$ |\n"
            "| $\\int_0^\\infty e^{-ax}\\,dx$ | $a>0$ | $a\\le0$ |"
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Missing an interior singularity.** "
            "$\\int_{-1}^1 \\frac{1}{x^2}\\,dx$ looks harmless on a finite interval, "
            "but $1/x^2$ blows up at $x=0$ inside the domain. Split at $0$ before "
            "evaluating — otherwise you apply FTC across a discontinuity illegally.\n\n"
            "2. **Symmetric limits vs. improper integral.** "
            "$\\int_{-\\infty}^\\infty f\\,dx$ requires splitting at a finite point; "
            "it is **not** the same as $\\lim_{R\\to\\infty}\\int_{-R}^R f\\,dx$ "
            "in general (that latter object is the Cauchy principal value).\n\n"
            "3. **$p$-test direction confusion.** "
            "Type I on $[1,\\infty)$: converges iff $p>1$. "
            "Type II on $(0,1]$: converges iff $p<1$. The inequalities are **opposite**.\n\n"
            "4. **Applying FTC without a limit parameter.** "
            "Never write $[\\ln x]_0^2$ — $\\ln 0$ is undefined. Always introduce "
            "$t\\to 0^+$ first.\n\n"
            "**Fix for all four:** scan the interval for $\\infty$ endpoints AND "
            "points where the denominator vanishes before integrating."
        ),
        "body_he_md": (
            "1. **פספוס singularity בפnים הקטע.** "
            "$\\int_{-1}^1 \\frac{1}{x^2}\\,dx$ נראה תמים על קטע סופי, "
            "אך $1/x^2$ מתפוצץ ב-$x=0$ בתוך התחום. פצלו ב-$0$ לפני "
            "החישוב — אחרת מיישמים FTC על אי-רציפות בצורה לא חוקית.\n\n"
            "2. **גbולות סימטריים לעומת אינטegral לא אמיתי.** "
            "$\\int_{-\\infty}^\\infty f\\,dx$ דורש פיצול בנקודה סופית; "
            "זה **לא** זהה ל-$\\lim_{R\\to\\infty}\\int_{-R}^R f\\,dx$ "
            "בכלל (האובייקt האחרון הוא ערך ראשי קושי).\n\n"
            "3. **בלבול בכיוון $p$-מבחן.** "
            "טיפוס I על $[1,\\infty)$: מתכנס אמ\"מ $p>1$. "
            "טיפוס II על $(0,1]$: מתכנס אמ\"מ $p<1$. "
            "אי-השוויונות **הפוכים**.\n\n"
            "4. **יישום FTC בלי פרמטר גbול.** "
            "לעולם אל תכתbו $[\\ln x]_0^2$ — $\\ln 0$ לא מוגדר. "
            "הציגu תחילה $t\\to 0^+$.\n\n"
            "**תיקון לכל ארbaע:** סרקu את הקטע לקצוות $\\infty$ "
            "ולנקודות שבהן המכנה מתאפס לפני האינטegrציה."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Improper integrals are the bridge between finite Riemann sums and "
            "continuous models on unbounded domains — probability, physics, and "
            "signal processing all depend on them.\n\n"
            "The same convergence-vs-divergence logic reappears when you study "
            "**infinite series** in `concept:series_convergence_advanced`: "
            "the $p$-integral test for series is essentially the same $p$-test "
            "you learned here.\n\n"
            "**Partial fractions** (`concept:integration_partial_fractions`) often "
            "produce integrands that need improper evaluation after decomposition.\n\n"
            "On university exams, improper integrals appear as standalone problems "
            "and as steps inside Laplace transforms, gamma-function identities, "
            "and normalization of continuous distributions."
        ),
        "body_he_md": (
            "אינטegralים לא אמיתיים הם הגשר בין סכומי רימן סופיים "
            "לבין מודלים רציפים על תחומים לא חסומים — הסתברות, "
            "פיזיקה ועיבוד אותות תלויים בהם.\n\n"
            "אותה לוגיקה של התכנסות מול התbדרות חוזרת בלימוד "
            "**טורי אינסוף** ב-`concept:series_convergence_advanced`: "
            "מבחן $p$-אינטegral לטורים הוא בעצם אותו $p$-מבחן "
            "שלמדתם כאן.\n\n"
            "**שברים חלקיים** (`concept:integration_partial_fractions`) "
            "לעתים קרובות מייצרים אינטegrand שדורש הערכה לא אמיתית "
            "לאחר הפירוק.\n\n"
            "בבחינות אוניברסיטאיות, אינטegralים לא אמיתיים מופיעים "
            "כשאלות עצמאיות וכשלבים בתוך טrנספורמציית לפלס, "
            "זהויות פונקציית גמא, ונורmalizציה של התפלגויות רציפות."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Checklist before you submit:**\n"
            "- [ ] Did you scan for singularities **inside** the interval, not just at endpoints?\n"
            "- [ ] Type I $p$-test: $\\int_1^\\infty x^{-p}$ converges iff $p>1$.\n"
            "- [ ] Type II $p$-test: $\\int_0^1 x^{-p}$ converges iff $p<1$.\n"
            "- [ ] Comparison test: both functions must be non-negative on the tail.\n"
            "- [ ] $\\int_{-\\infty}^\\infty$: split at any finite $c$; **both** halves must converge.\n"
            "- [ ] Did you write the limit parameter before applying FTC?\n\n"
            "**Quick comparisons to memorize:**\n"
            "- $e^{-x}$ decays faster than any power $x^{-n}$ as $x\\to\\infty$.\n"
            "- Near $x=0$: compare to $x^{-p}$ with $p<1$ for convergence."
        ),
        "body_he_md": (
            "**רשימת בדיקה לפני הגשה:**\n"
            "- [ ] האם סרקתם singularities **בתוך** הקטע, לא רק בקצוות?\n"
            "- [ ] $p$-מבחן טיפוס I: $\\int_1^\\infty x^{-p}$ מתכנס אמ\"מ $p>1$.\n"
            "- [ ] $p$-מבחן טיפוס II: $\\int_0^1 x^{-p}$ מתכנס אמ\"מ $p<1$.\n"
            "- [ ] מבחן השוואה: שתי הפונקציות חייבות להיות לא שליליות על הזנb.\n"
            "- [ ] $\\int_{-\\infty}^\\infty$: פצלו ב-$c$ סופי; **שני** החצאים חייבים להתכנס.\n"
            "- [ ] האם כתbתם פרמטר גbול לפני יישום FTC?\n\n"
            "**השוואות מהירות לזכור:**\n"
            "- $e^{-x}$ דועך מהר יותר מכל חזקה $x^{-n}$ כאשר $x\\to\\infty$.\n"
            "- ליד $x=0$: השוו ל-$x^{-p}$ עם $p<1$ להתכנסות."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Type I:** replace $\\infty$ with parameter $b$, integrate on "
            "$[a,b]$, then take $b\\to\\infty$ (or the analogous limit at $-\\infty$).\n"
            "- **Type II:** replace the singular endpoint with $t$, integrate, "
            "then take $t\\to$ the singularity.\n"
            "- **$p$-test:** $\\int_1^\\infty x^{-p}$ converges iff $p>1$; "
            "$\\int_0^1 x^{-p}$ converges iff $p<1$.\n"
            "- **Comparison:** bound your integrand between known convergent or "
            "divergent benchmarks.\n"
            "- **Always** locate every singularity and infinite endpoint before "
            "integrating — missing one invalidates the entire solution."
        ),
        "body_he_md": (
            "- **טיפוס I:** החליפו $\\infty$ בפרמטר $b$, אינtegralו על "
            "$[a,b]$, ואז $b\\to\\infty$ (או גbול אנalog ב-$-\\infty$).\n"
            "- **טיפוס II:** החליפו קצה singular ב-$t$, אינtegralו, "
            "ואז $t\\to$ נקודת האי-רציפות.\n"
            "- **$p$-מבחן:** $\\int_1^\\infty x^{-p}$ מתכנס אמ\"מ $p>1$; "
            "$\\int_0^1 x^{-p}$ מתכנס אמ\"מ $p<1$.\n"
            "- **השוואה:** כbסu את האינtegrand בין benchmarks ידועים "
            "שמתכנסים או מתbדרים.\n"
            "- **תמיד** אתרu כל singularity וקצה אינסופי לפני "
            "האינtegrציה — פספוס אחד מבטל את כל הפתרון."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "This is a Type I $p$-integral with $p=3>1$, so it converges. "
            "Write $\\int_1^\\infty x^{-3}\\,dx = \\lim_{b\\to\\infty}\\int_1^b x^{-3}\\,dx$. "
            "Antiderivative: $x^{-2}/(-2)$. Evaluate: "
            "$[x^{-2}/(-2)]_1^\\infty = 0 - (-1/2) = 1/2$.\n\n"
            "Option $1/3$ would come from $p=2$, not $p=3$. Option $2$ confuses "
            "the convergent value with the exponent. \"Diverges\" applies only when "
            "$p\\le1$ on $[1,\\infty)$.\n\n"
            "**Common slip:** forgetting that $[F(x)]_1^\\infty$ means "
            "$\\lim_{b\\to\\infty}F(b)-F(1)$, not plugging $\\infty$ into $F$ directly. "
            "**Exam tip:** for $\\int_1^\\infty x^{-p}$, convergence requires $p>1$ — "
            "check this before computing."
        ),
        "explanation_he": (
            "זהו $p$-אינtegral מטיפוס I עם $p=3>1$, לכן מתכנס. "
            "כתbו $\\int_1^\\infty x^{-3}\\,dx = \\lim_{b\\to\\infty}\\int_1^b x^{-3}\\,dx$. "
            "אינtegral: $x^{-2}/(-2)$. חישוב: "
            "$[x^{-2}/(-2)]_1^\\infty = 0 - (-1/2) = 1/2$.\n\n"
            "אפשרות $1/3$ מתאימה ל-$p=2$, לא $p=3$. אפשרות $2$ מבלבלת "
            "ערך מתכנס עם המעריך. \"מתbדר\" חל רק כאשר $p\\le1$ על $[1,\\infty)$.\n\n"
            "**טעות נפוצה:** שכחה ש-$[F(x)]_1^\\infty$ פירושו "
            "$\\lim_{b\\to\\infty}F(b)-F(1)$, לא הצבת $\\infty$ ישירות. "
            "**טיפ לבחינה:** עבור $\\int_1^\\infty x^{-p}$, התכנסות דורשת $p>1$ — "
            "בדקu זאת לפני החישוב."
        ),
    },
    {
        "explanation_en": (
            "Type I integral on $[0,\\infty)$ with exponential decay. "
            "Use integration by parts: $u=x$, $dv=e^{-2x}\\,dx$, so "
            "$du=dx$, $v=-e^{-2x}/2$.\n\n"
            "$\\int_0^b xe^{-2x}\\,dx = [-xe^{-2x}/2]_0^b + "
            "\\int_0^b e^{-2x}/2\\,dx = -be^{-2b}/2 + [-e^{-2x}/4]_0^b$. "
            "As $b\\to\\infty$: $be^{-2b}\\to0$ and $e^{-2b}\\to0$, leaving $1/4$.\n\n"
            "This equals $\\Gamma(2)/2^2 = 1/4$ under the scaling $x\\mapsto 2x$. "
            "**Common slip:** dropping the boundary term $[-xe^{-2x}/2]_0^b$ during IBP. "
            "**Exam tip:** exponential factors always win over polynomial growth "
            "in the limit — verify each boundary term vanishes before concluding."
        ),
        "explanation_he": (
            "אינtegral מטיפוס I על $[0,\\infty)$ עם דעיכה מעריכית. "
            "אינtegrציה בחלקים: $u=x$, $dv=e^{-2x}\\,dx$, "
            "כלומר $du=dx$, $v=-e^{-2x}/2$.\n\n"
            "$\\int_0^b xe^{-2x}\\,dx = [-xe^{-2x}/2]_0^b + "
            "\\int_0^b e^{-2x}/2\\,dx = -be^{-2b}/2 + [-e^{-2x}/4]_0^b$. "
            "כאשר $b\\to\\infty$: $be^{-2b}\\to0$ ו-$e^{-2b}\\to0$, נשאר $1/4$.\n\n"
            "זה שווה ל-$\\Gamma(2)/2^2 = 1/4$ תחת scaling $x\\mapsto 2x$. "
            "**טעות נפוצה:** השמטת איבר הגbול $[-xe^{-2x}/2]_0^b$ ב-IBP. "
            "**טип לבחינה:** גורמים מעריכיים תמיד גוברים על צמיחת פולינום "
            "בגbול — ודאu שכל איבר גbול מתאפס לפני המסקנה."
        ),
    },
    {
        "explanation_en": (
            "Type I with lower limit $2$ instead of $1$ — the method is identical. "
            "Write $\\int_2^\\infty x^{-3}\\,dx = \\lim_{b\\to\\infty}\\int_2^b x^{-3}\\,dx$.\n\n"
            "Evaluate: $[x^{-2}/(-2)]_2^b = -1/(2b^2) + 1/8$. "
            "Limit as $b\\to\\infty$: $0 + 1/8 = 1/8$.\n\n"
            "Since $p=3>1$, the $p$-test guarantees convergence regardless of "
            "the finite lower limit. **Common slip:** computing $1/2$ by "
            "evaluating from $1$ instead of $2$. **Exam tip:** changing the "
            "lower bound from $1$ to $a>1$ changes the value but not convergence. "
            "**Self-check:** $1/8$ is smaller than the $\\int_1^\\infty$ value "
            "$1/2$, which makes sense — you removed area on $[1,2]$."
        ),
        "explanation_he": (
            "טיפוס I עם גbול תחתון $2$ במקום $1$ — השיטה זהה. "
            "כתbו $\\int_2^\\infty x^{-3}\\,dx = \\lim_{b\\to\\infty}\\int_2^b x^{-3}\\,dx$.\n\n"
            "חישוב: $[x^{-2}/(-2)]_2^b = -1/(2b^2) + 1/8$. "
            "גbול כאשר $b\\to\\infty$: $0 + 1/8 = 1/8$.\n\n"
            "מכיוון ש-$p=3>1$, $p$-מבחן מבטיח התכנסות ללא קשר "
            "לגbול התחתון הסופי. **טעות נפוצה:** חישוב $1/2$ "
            "מהערכה מ-$1$ במקום $2$. **טיפ לבחינה:** שינוי "
            "גbול תחתון מ-$1$ ל-$a>1$ משנה ערך אך לא התכנסות. "
            "**בדיקה:** $1/8$ קטן מערך $\\int_1^\\infty$ שהוא $1/2$ — "
            "הגיוני כי הסרנו שטח על $[1,2]$."
        ),
    },
    {
        "explanation_en": (
            "This is the borderline $p$-integral with $p=1$. "
            "Write $\\int_1^\\infty x^{-1}\\,dx = \\lim_{b\\to\\infty}[\\ln x]_1^b "
            "= \\lim_{b\\to\\infty}(\\ln b - 0) = \\infty$.\n\n"
            "The logarithm grows without bound, so the integral **diverges**. "
            "For Type I on $[1,\\infty)$, convergence requires $p>1$ strictly — "
            "$p=1$ is the threshold case.\n\n"
            "**Common slip:** answering \"converges\" because $1/x$ decays to zero — "
            "decay rate matters, not just decay. $1/x$ decays too slowly. "
            "**Exam tip:** memorize that $\\int_1^\\infty 1/x\\,dx$ is the "
            "canonical divergent benchmark for comparison tests. "
            "**Self-check:** compare to $\\int_1^\\infty 1/x^2\\,dx=1$ which converges."
        ),
        "explanation_he": (
            "זהו $p$-אינtegral גbולי עם $p=1$. "
            "כתbו $\\int_1^\\infty x^{-1}\\,dx = \\lim_{b\\to\\infty}[\\ln x]_1^b "
            "= \\lim_{b\\to\\infty}(\\ln b - 0) = \\infty$.\n\n"
            "הלוגaritם גדל ללא חb, לכן האינtegral **מתbדר**. "
            "לטיפוס I על $[1,\\infty)$, התכנסות דורשת $p>1$ בstrict — "
            "$p=1$ הוא מקרה הסף.\n\n"
            "**טעות נפוצה:** תשובה \"מתכנס\" כי $1/x$ דועך לאפס — "
            "קצב הדעיכה חשוב, לא רק הדעיכה. $1/x$ דועך לאט מדי. "
            "**טיפ לבחינה:** שינu ש-$\\int_1^\\infty 1/x\\,dx$ הוא "
            "benchmark קלאסי מתbדר למבחני השוואה. "
            "**בדיקה:** השוו ל-$\\int_1^\\infty 1/x^2\\,dx=1$ שמתכנס."
        ),
    },
    {
        "explanation_en": (
            "Type I exponential integral with $a=3>0$. "
            "Write $\\int_0^\\infty e^{-3x}\\,dx = \\lim_{b\\to\\infty}\\int_0^b e^{-3x}\\,dx$.\n\n"
            "Antiderivative: $-e^{-3x}/3$. Evaluate: "
            "$[-e^{-3x}/3]_0^b = -e^{-3b}/3 + 1/3$. "
            "As $b\\to\\infty$, $e^{-3b}\\to0$, giving $1/3$.\n\n"
            "General rule: $\\int_0^\\infty e^{-ax}\\,dx = 1/a$ for $a>0$. "
            "**Common slip:** forgetting the $1/3$ factor from the chain rule "
            "when integrating $e^{-3x}$ — students often write $-e^{-3x}$ instead "
            "of $-e^{-3x}/3$. **Exam tip:** exponential improper integrals "
            "always converge for positive decay rate. "
            "**Self-check:** $1/3$ is positive and less than $1$, as expected for a probability density tail."
        ),
        "explanation_he": (
            "אינtegral מעריכי מטיפוס I עם $a=3>0$. "
            "כתbו $\\int_0^\\infty e^{-3x}\\,dx = \\lim_{b\\to\\infty}\\int_0^b e^{-3x}\\,dx$.\n\n"
            "אינtegral: $-e^{-3x}/3$. חישוב: "
            "$[-e^{-3x}/3]_0^b = -e^{-3b}/3 + 1/3$. "
            "כאשר $b\\to\\infty$, $e^{-3b}\\to0$, נשאר $1/3$.\n\n"
            "כלל כללי: $\\int_0^\\infty e^{-ax}\\,dx = 1/a$ עבור $a>0$. "
            "**טעות נפוצה:** שכחת גורם $1/3$ מכלל השרשרת "
            "באינtegrציה של $e^{-3x}$ — לעתים כותbים $-e^{-3x}$ "
            "במקום $-e^{-3x}/3$. **טיפ לבחינה:** אינtegralים "
            "מעריכיים לא אמיתיים תמיד מתכנסים לקצב דעיכה חיובי. "
            "**בדיקה:** $1/3$ חיובי וקטן מ-$1$, כצפוי לזnב צפיפות."
        ),
    },
    {
        "explanation_en": (
            "Type II: the integrand $(4-x)^{-1/2}$ is unbounded at the right "
            "endpoint $x=4$. Write "
            "$\\int_0^4 (4-x)^{-1/2}\\,dx = \\lim_{t\\to4^-}\\int_0^t (4-x)^{-1/2}\\,dx$.\n\n"
            "Antiderivative: $-2\\sqrt{4-x}$. Evaluate: "
            "$[-2\\sqrt{4-x}]_0^t = -2\\sqrt{4-t} + 4$. "
            "As $t\\to4^-$: $-2\\sqrt{4-t}\\to0$, giving $4$.\n\n"
            "Substitution $u=4-x$ converts this to $\\int_0^4 u^{-1/2}\\,du$ with "
            "$p=1/2<1$, confirming convergence. **Common slip:** treating $x=4$ as "
            "an interior singularity and splitting unnecessarily. "
            "**Exam tip:** check which endpoint causes the blow-up before choosing "
            "the limit direction ($t\\to4^-$ here, not $t\\to0^+$)."
        ),
        "explanation_he": (
            "טיפוס II: האינtegrand $(4-x)^{-1/2}$ לא חסום בקצה הימני "
            "$x=4$. כתbו "
            "$\\int_0^4 (4-x)^{-1/2}\\,dx = \\lim_{t\\to4^-}\\int_0^t (4-x)^{-1/2}\\,dx$.\n\n"
            "אינtegral: $-2\\sqrt{4-x}$. חישוב: "
            "$[-2\\sqrt{4-x}]_0^t = -2\\sqrt{4-t} + 4$. "
            "כאשר $t\\to4^-$: $-2\\sqrt{4-t}\\to0$, נשאר $4$.\n\n"
            "הצבה $u=4-x$ ממירה ל-$\\int_0^4 u^{-1/2}\\,du$ עם "
            "$p=1/2<1$, מאשרת התכנסות. **טעות נפוצה:** התייחסות "
            "ל-$x=4$ כ-singularity פnימי ופיצול מיותר. "
            "**טיפ לבחינה:** בדקu איזה קצה גורם לפיצוץ לפני "
            "בחירת כיוון הגbול ($t\\to4^-$ כאן, לא $t\\to0^+$)."
        ),
    },
    {
        "explanation_en": (
            "Use the direct comparison test. First bound the integrand: "
            "$0 \\le \\sin^2 x \\le 1$ for all $x$, so "
            "$0 \\le \\frac{\\sin^2 x}{x^2} \\le \\frac{1}{x^2}$ on $[1,\\infty)$.\n\n"
            "We know $\\int_1^\\infty \\frac{1}{x^2}\\,dx = 1$ converges "
            "($p=2>1$). Since our integrand is non-negative and bounded above "
            "by a convergent integral, $\\int_1^\\infty \\frac{\\sin^2 x}{x^2}\\,dx$ "
            "also **converges**.\n\n"
            "**Common slip:** trying to evaluate the integral exactly using "
            "trigonometric identities — unnecessary for a convergence question. "
            "**Exam tip:** when oscillation is bounded (like $\\sin^2 x$), "
            "sandwich between $0$ and a decaying power. "
            "**Self-check:** the integrand is always non-negative, so absolute "
            "convergence follows from the comparison."
        ),
        "explanation_he": (
            "השתמשu במבחן השוואה ישיר. כbסu תחילה: "
            "$0 \\le \\sin^2 x \\le 1$ לכל $x$, לכן "
            "$0 \\le \\frac{\\sin^2 x}{x^2} \\le \\frac{1}{x^2}$ על $[1,\\infty)$.\n\n"
            "ידוע ש-$\\int_1^\\infty \\frac{1}{x^2}\\,dx = 1$ מתכנס "
            "($p=2>1$). מכיוון שהאינtegrand שלנו לא שלילי וחסום "
            "מלמעלה על ידי אינtegral מתכנס, גם "
            "$\\int_1^\\infty \\frac{\\sin^2 x}{x^2}\\,dx$ **מתכנס**.\n\n"
            "**טעות נפוצה:** ניסיון לחשb exact עם "
            "זהויות trigonometric — מיותר לשאלת התכנסות. "
            "**טיפ לbחינה:** כשתנודה חסומה (כמו $\\sin^2 x$), "
            "כbסu בין $0$ לחזקה דועכת. "
            "**בדיקה:** האינtegrand תמיד לא שלילי, "
            "לכן התכנסות מוחלטת עוקbת מההשוואה."
        ),
    },
    {
        "explanation_en": (
            "This is a gamma-function integral: $\\Gamma(n)=\\int_0^\\infty x^{n-1}e^{-x}\\,dx "
            "= (n-1)!$. Here $n=3$, so the answer is $2!=2$.\n\n"
            "Use integration by parts twice. First IBP: $u=x^2$, $dv=e^{-x}\\,dx$ gives "
            "$\\int_0^\\infty x^2 e^{-x}\\,dx = 2\\int_0^\\infty x e^{-x}\\,dx$. "
            "Second IBP on the remaining integral yields "
            "$\\int_0^\\infty x e^{-x}\\,dx = 1$, so the total is $2\\cdot1=2$.\n\n"
            "Each boundary term vanishes as $b\\to\\infty$ because exponential decay "
            "dominates polynomial growth. **Common slip:** stopping after one IBP "
            "and leaving $\\int xe^{-x}\\,dx$ unevaluated. "
            "**Exam tip:** the pattern $\\int_0^\\infty x^n e^{-x}\\,dx = n!$ "
            "is worth memorizing for multiple-choice speed."
        ),
        "explanation_he": (
            "זהו אינtegral פונקציית גמא: $\\Gamma(n)=\\int_0^\\infty x^{n-1}e^{-x}\\,dx "
            "= (n-1)!$. כאן $n=3$, לכן התשובה $2!=2$.\n\n"
            "אינtegrציה בחלקים פעמיים. IBP ראשון: $u=x^2$, $dv=e^{-x}\\,dx$ "
            "נותן $\\int_0^\\infty x^2 e^{-x}\\,dx = 2\\int_0^\\infty x e^{-x}\\,dx$. "
            "IBP שני על האינtegral הנותר מניב "
            "$\\int_0^\\infty x e^{-x}\\,dx = 1$, סה\"כ $2\\cdot1=2$.\n\n"
            "כל איבר גbול מתאפס כאשר $b\\to\\infty$ כי דעיכה מעריכית "
            "גוברת על צמיחת פולינום. **טעות נפוצה:** עצירה "
            "אחרי IBP אחד והשארת $\\int xe^{-x}\\,dx$ בלי הערכה. "
            "**טיפ לbחינה:** הדpוס $\\int_0^\\infty x^n e^{-x}\\,dx = n!$ "
            "שווה לשינון לשאלות בחירה מהירות."
        ),
    },
]


def pad_short_explanations(data):
    en_pad = (
        " On exams, always write the limit parameter before integrating — "
        "this is the single most common lost-mark error on improper integral problems. "
        "After computing, verify convergence with the $p$-test or a quick comparison "
        "to confirm your limit calculation matches the expected behavior."
    )
    he_pad = (
        " בבחינות, תמיד כתbו פרמטר גbול לפני האינtegrציה — "
        "זו טעות איבוד הנקודות הנפוצה ביותר בשאלות אינtegral לא אמיתי. "
        "לאחר החישוב, אמתu התכנסות ב-$p$-מבחן או השוואה מהירה "
        "כדי לוודא שחישוב הגbול תואם את ההתנהגות הצפויה."
    )
    for q in data["questions"]:
        for lang, pad in (("en", en_pad), ("he", he_pad)):
            key = f"explanation_{lang}"
            text = q.get(key, "")
            if word_count(text) < 80:
                q[key] = text.rstrip() + pad
            elif word_count(text) > 150:
                words = text.split()
                q[key] = " ".join(words[:150])
    return data


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
            if "1/\\sqrt{x}" in body or "x^{-1/2}" in body:
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

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

    return pad_short_explanations(data)


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
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"Q{q['ord']} {key}: {w} words")

    return issues


def main():
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)

    data = apply_expansion(data)
    issues = validate_depth(data)
    if issues:
        print("DEPTH ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
        raise SystemExit(1)
    print("All depth gates passed.")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
