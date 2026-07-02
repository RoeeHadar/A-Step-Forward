#!/usr/bin/env python3
"""Expand hypothesis_testing.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/hypothesis_testing.json"

MIN = {
    "intro": (110, 90),
    "definition": (130, 110),
    "theory": (160, 130),
    "worked_example": (130, 110),
    "pitfall": (100, 85),
    "why_matters": (90, 75),
    "method_guide": (100, 85),
    "before_exam": (90, 75),
    "summary": (70, 60),
}


def wc(text: str) -> int:
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def he_ratio(text: str) -> float:
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def he_weak(he: str, en: str) -> bool:
    he, en = (he or "").strip(), (en or "").strip()
    if not he:
        return True
    if wc(he) / max(wc(en), 1) < 0.55:
        return True
    if he_ratio(he) < 0.15 and wc(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he) -> tuple[str, str]:
    en = (
        f"**Why this is correct:**\n{why_en}\n\n"
        f"**How to think about it:**\n{how_en}\n\n"
        f"**Common slip:**\n{slip_en}\n\n"
        f"**Exam tip:**\n{tip_en}"
    )
    he = (
        f"**למה זה נכון:**\n{why_he}\n\n"
        f"**איך לחשוב על זה:**\n{how_he}\n\n"
        f"**טעות נפוצה:**\n{slip_he}\n\n"
        f"**טיפ לבחינה:**\n{tip_he}"
    )
    return en, he


INTRO_EN = """Probability theory tells us how likely outcomes are **if** we know the distribution. In practice we must go backwards: we observe data and ask whether a hypothesised model is compatible with what we saw.

**Hypothesis testing** is the formal framework for this inverse problem. We assume a conservative **null hypothesis** $H_0$, compute how surprising our sample would be under $H_0$, and decide whether the evidence is strong enough to reject $H_0$ in favour of an **alternative** $H_1$.

This unit appears throughout Israeli university statistics courses (TAU, Technion, Hebrew University), Bagrut 5-unit statistics extensions, and every data-science pipeline that reports p-values or confidence intervals. You will compute z- and t-statistics, interpret Type I/II errors, choose one- vs two-tailed tests, and determine sample sizes for desired power.

**Builds on:** normal distribution, z-scores, and sampling distributions from `concept:distributions`. Master those first — every test statistic here is a standardized sample mean or proportion."""

INTRO_HE = """תורת ההסתברות אומרת לנו כמה סבירה תוצאה **אם** אנחנו יודעים את ההתפלגות. בפועל עלינו ללכת הפוך: אנחנו מתבוננים בנתונים ושואלים האם מודל השערתי מתיישב עם מה שנצפה.

**בדיקת השערות** היא המסגרת הפורמלית לבעיה ההפוכה. אנחנו מניחים **השערת אפס** $H_0$ שמרנית, מחשבים כמה מפתיע המדגם שלנו תחת $H_0$, ומחליטים האם הראיות מספיקות לדחות את $H_0$ לטובת **השערה אלטרנטיבית** $H_1$.

יחידה זו מופיעה בקורסי סטטיסטיקה אוניברסיטאיים (TAU, טכניון, HUJI), בהרחבות בגרות 5 יחידות, ובכל צינור data science שמדווח p-values או רווחי סמך. תחשבו סטטיסטיקות z ו-t, תפרשו שגיאות סוג I/II, תבחרו מבחנים חד- או דו-זנביים, ותקבעו גודל מדגם לעוצמה רצויה.

**מבוסס על:** התפלגות נורמלית, ציוני z והתפלגויות מדגם מ-`concept:distributions`. שלטו בהם קודם — כל סטטיסטיקת מבחן כאן היא ממוצע מדגם או פרופורציה מתוקננים."""

DEF_EN = """**Null hypothesis $H_0$:** The default or status-quo claim we test against, e.g. $\\mu = \\mu_0$, $p = p_0$, or \"no effect.\" We never \"prove\" $H_0$ — we only fail to reject it.

**Alternative hypothesis $H_1$:** The claim we seek evidence for: $\\mu \\neq \\mu_0$ (two-tailed), $\\mu > \\mu_0$ (right-tailed), or $\\mu < \\mu_0$ (left-tailed). Direction must be chosen **before** seeing data.

**Test statistic:** A function of the data whose sampling distribution is known under $H_0$. For a one-sample z-test with known $\\sigma$:
$$Z = \\frac{\\bar{X} - \\mu_0}{\\sigma/\\sqrt{n}} \\sim N(0,1) \\quad \\text{under } H_0.$$

**p-value:** The probability, assuming $H_0$ is true, of observing data at least as extreme as what we saw. Two-tailed: $p = 2P(Z \\geq |z_{\\text{obs}}|)$. Smaller $p$ = stronger evidence against $H_0$.

**Significance level $\\alpha$:** Pre-chosen threshold (commonly 0.05). Reject $H_0$ if $p < \\alpha$. Equivalently, reject if $|Z| > z_{\\alpha/2}$ (two-tailed).

**Type I error:** Rejecting $H_0$ when it is true (false positive). $P(\\text{Type I}) = \\alpha$ by construction.

**Type II error:** Failing to reject $H_0$ when $H_1$ is true (false negative). $P(\\text{Type II}) = \\beta$.

**Power:** $1 - \\beta = P(\\text{reject } H_0 \\mid H_1 \\text{ true})$. Higher power means better ability to detect a real effect.

**Critical value:** For $\\alpha = 0.05$ two-tailed, $z_{0.025} = 1.96$. One-tailed right at $\\alpha = 0.05$: $z_{0.05} = 1.645$."""

DEF_HE = """**השערת אפס $H_0$:** הטענה ברירת-המחדל שאותה בודקים, למשל $\\mu = \\mu_0$, $p = p_0$, או \"אין אפקט.\" לעולם לא \"מוכיחים\" $H_0$ — רק אולי לא דוחים אותה.

**השערה אלטרנטיבית $H_1$:** הטענה שרוצים ראיות לטובתה: $\\mu \\neq \\mu_0$ (דו-זנבי), $\\mu > \\mu_0$ (ימין), או $\\mu < \\mu_0$ (שמאל). הכיוון חייב להיבחר **לפני** ראיית הנתונים.

**סטטיסטיקת מבחן:** פונקציה של הנתונים שהתפלגות המדגם שלה ידועה תחת $H_0$. למבחן z חד-מדגמי עם $\\sigma$ ידוע:
$$Z = \\frac{\\bar{X} - \\mu_0}{\\sigma/\\sqrt{n}} \\sim N(0,1) \\quad \\text{תחת } H_0.$$

**p-value:** ההסתברות, בהנחה ש-$H_0$ נכונה, לקבל נתונים קיצוניים לפחות כמו שנצפו. דו-זנבי: $p = 2P(Z \\geq |z_{\\text{obs}}|)$. $p$ קטן יותר = ראיות חזקות יותר נגד $H_0$.

**רמת מובהקות $\\alpha$:** סף שנקבע מראש (לרוב 0.05). דחה $H_0$ אם $p < \\alpha$. שקיל: דחה אם $|Z| > z_{\\alpha/2}$ (דו-זנבי).

**שגיאת סוג I:** דחיית $H_0$ כשהיא נכונה (חיובי שגוי). $P(\\text{סוג I}) = \\alpha$ בהגדרה.

**שגיאת סוג II:** אי-דחיית $H_0$ כש-$H_1$ נכונה (שלילי שגוי). $P(\\text{סוג II}) = \\beta$.

**עוצמה:** $1 - \\beta = P(\\text{דחיית } H_0 \\mid H_1 \\text{ נכונה})$. עוצמה גבוהה = יכולת טובה יותר לגלות אפקט אמיתי.

**ערך קריטי:** ל-$\\alpha = 0.05$ דו-זנבי, $z_{0.025} = 1.96$. חד-זנבי ימין ב-$\\alpha = 0.05$: $z_{0.05} = 1.645$."""

THEORY_EN = """**CLT basis.** By the Central Limit Theorem, for large $n$ the sample mean satisfies $\\bar{X} \\approx N(\\mu, \\sigma^2/n)$ regardless of the population shape. This justifies z-tests when $\\sigma$ is known and $n$ is moderate-to-large.

**Decision rule (two-tailed).** Reject $H_0$ if and only if $|Z| > z_{\\alpha/2}$, or equivalently if $p\\text{-value} < \\alpha$. The two approaches always agree — use whichever the exam provides tables for.

**t-test when $\\sigma$ is unknown.** Replace population $\\sigma$ with sample standard deviation $s$:
$$T = \\frac{\\bar{X} - \\mu_0}{s/\\sqrt{n}} \\sim t_{n-1} \\quad \\text{under } H_0.$$
Use the t-distribution critical values $t_{\\alpha/2,\\, n-1}$, which have heavier tails than the normal.

**Power and sample size.** To detect a shift $\\delta = |\\mu_1 - \\mu_0|$ with power $1-\\beta$ at significance $\\alpha$ (two-tailed, known $\\sigma$):
$$n = \\left(\\frac{(z_{\\alpha/2} + z_\\beta)\\,\\sigma}{\\delta}\\right)^2.$$
Round **up** to the next integer. Larger $\\delta$, smaller $\\sigma$, or higher desired power all increase required $n$.

**Trade-off $\\alpha$ vs $\\beta$.** For fixed $n$ and true effect, decreasing $\\alpha$ (stricter threshold) increases $\\beta$ (less power). You cannot minimize both simultaneously without collecting more data.

**CI–test duality.** Rejecting $H_0: \\mu = \\mu_0$ at level $\\alpha$ is equivalent to $\\mu_0$ lying outside the $(1-\\alpha)$ confidence interval $\\bar{x} \\pm z_{\\alpha/2}\\,\\sigma/\\sqrt{n}$. This duality is a favourite proof question on Israeli exams."""

THEORY_HE = """**בסיס CLT.** לפי משפט הגבול המרכזי, ל-$n$ גדול ממוצע המדגם מקיים $\\bar{X} \\approx N(\\mu, \\sigma^2/n)$ ללא תלות בצורת האוכלוסייה. זה מצדיק מבחני z כש-$\\sigma$ ידוע ו-$n$ בינוני-גדול.

**כלל החלטה (דו-זנבי).** דחה $H_0$ אמ\"מ $|Z| > z_{\\alpha/2}$, או שקיל: $p\\text{-value} < \\alpha$. שתי הגישות תמיד מסכימות — השתמשו במה שיש טבלאות לו בבחינה.

**מבחן t כש-$\\sigma$ לא ידוע.** החליפו $\\sigma$ באוכלוסייה ב-$s$ מדגמי:
$$T = \\frac{\\bar{X} - \\mu_0}{s/\\sqrt{n}} \\sim t_{n-1} \\quad \\text{תחת } H_0.$$
השתמשו בערכים קריטיים של t: $t_{\\alpha/2,\\, n-1}$, עם זנבות כבדים יותר מהנורמל.

**עוצמה וגודל מדגם.** לגילוי הפרש $\\delta = |\\mu_1 - \\mu_0|$ בעוצמה $1-\\beta$ ברמת $\\alpha$ (דו-זנבי, $\\sigma$ ידוע):
$$n = \\left(\\frac{(z_{\\alpha/2} + z_\\beta)\\,\\sigma}{\\delta}\\right)^2.$$
עגלו **למעלה** למספר שלם. $\\delta$ גדול יותר, $\\sigma$ קטן יותר, או עוצמה רצויה גבוהה יותר — כולם מגדילים $n$ נדרש.

**פשרה $\\alpha$ מול $\\beta$.** ל-$n$ ואפקט אמיתי קבועים, הקטנת $\\alpha$ (סף מחמיר יותר) מגדילה $\\beta$ (פחות עוצמה). אי אפשר למזער את שניהם בלי לאסוף יותר נתונים.

**דואליות CI–מבחן.** דחיית $H_0: \\mu = \\mu_0$ ברמה $\\alpha$ שקילה ל-$\\mu_0$ מחוץ לרווח הסמך $(1-\\alpha)$: $\\bar{x} \\pm z_{\\alpha/2}\\,\\sigma/\\sqrt{n}$. דואליות זו שאלת הוכחה מועדפת בבחינות ישראליות."""

WE1_EN = """**Given:** $\\bar{x}=52$, $\\mu_0=50$, $\\sigma=10$, $n=25$. Test $H_0:\\mu=50$ vs $H_1:\\mu\\neq50$ at $\\alpha=0.05$ (two-tailed z-test, $\\sigma$ known).

This is the canonical one-sample z-test: compute the standardized distance of the sample mean from the hypothesized value, then compare to the normal distribution. The standard error $\\sigma/\\sqrt{n}$ converts the raw difference $\\bar{x}-\\mu_0$ into \"how many SEs away\" the sample sits.

### Move 1: Compute the test statistic
Standard error: $SE = \\sigma/\\sqrt{n} = 10/5 = 2$.
$$z = \\frac{\\bar{x} - \\mu_0}{SE} = \\frac{52 - 50}{2} = \\frac{2}{2} = 1.0.$$

### Move 2: Find the two-tailed p-value
$$p = 2 \\cdot P(Z > 1.0) = 2 \\cdot (1 - 0.8413) = 2 \\cdot 0.1587 = 0.3174.$$

### Move 3: Compare to $\\alpha$ and decide
$p = 0.317 > 0.05 = \\alpha$.

**Conclusion:** Fail to reject $H_0$. There is insufficient evidence at the 5% level that the true mean differs from 50. The observed $\\bar{x}=52$ is only one standard error away — not surprising under $H_0$.

**Alternative check:** Critical-value approach: $|z|=1.0 < 1.96=z_{0.025}$, so we would also fail to reject without computing $p$ exactly. Both methods must agree."""

WE1_HE = """**נתון:** $\\bar{x}=52$, $\\mu_0=50$, $\\sigma=10$, $n=25$. בדיקת $H_0:\\mu=50$ מול $H_1:\\mu\\neq50$ ב-$\\alpha=0.05$ (מבחן z דו-זנבי, $\\sigma$ ידוע).

זה מבחן z חד-מדגמי קלאסי: מחשבים את המרחק המתוקנן של ממוצע המדגם מהערך ההשערתי, ומשווים להתפלגות נורמלית. שגיאת התקן $\\sigma/\\sqrt{n}$ ממירה את ההפרש $\\bar{x}-\\mu_0$ ל\"כמה SE-ים\" המדגם רחוק.

### צעד 1: חישוב סטטיסטיקת המבחן
שגיאת תקן: $SE = \\sigma/\\sqrt{n} = 10/5 = 2$.
$$z = \\frac{\\bar{x} - \\mu_0}{SE} = \\frac{52 - 50}{2} = \\frac{2}{2} = 1.0.$$

### צעד 2: מציאת p-value דו-זנבי
$$p = 2 \\cdot P(Z > 1.0) = 2 \\cdot (1 - 0.8413) = 2 \\cdot 0.1587 = 0.3174.$$

### צעד 3: השוואה ל-$\\alpha$ והחלטה
$p = 0.317 > 0.05 = \\alpha$.

**מסקנה:** אין לדחות $H_0$. אין ראיות מספיקות ברמת 5% שהממוצע האמיתי שונה מ-50. $\\bar{x}=52$ נמצא רק בשגיאת תקן אחת — לא מפתיע תחת $H_0$.

**בדיקה חלופית:** גישת ערך קריטי: $|z|=1.0 < 1.96=z_{0.025}$, ולכן גם כך אין לדחות בלי חישוב $p$ מדויק. שתי השיטות חייבות להסכים."""

WE2_EN = """Compare how the same test statistic leads to different conclusions depending on whether the alternative is two-tailed or one-tailed.

### Move 1: Two-tailed setup (Scenario A)
A drug manufacturer claims a pill has no effect on heart rate ($H_0:\\mu=70$, $H_1:\\mu\\neq70$). Reject if $|z| > 1.96$ at $\\alpha=0.05$. Both unusually high **and** unusually low heart rates trigger rejection — the test is symmetric about the null value.

### Move 2: One-tailed setup (Scenario B)
A stimulant claims increased reaction speed ($H_0:\\mu\\leq0$, $H_1:\\mu>0$). Reject only if $z > 1.645$. Decreases are ignored entirely — only evidence of improvement counts.

### Move 3: Compare p-values for $z=1.7$
- Two-tailed: $p = 2P(Z>1.7) = 2(0.0446) = 0.089$. Not significant at $\\alpha=0.05$.
- One-tailed (right): $p = P(Z>1.7) = 0.0446$. Significant at $\\alpha=0.05$.

### Move 4: Interpret and warn
Same $z$, different conclusion. A one-tailed test concentrates all $\\alpha$ in one direction (more power there) but cannot detect opposite effects. Choosing the tail after seeing data (p-hacking) halves the p-value dishonestly.

**Rule:** Choose one-tailed only when theory or pre-registration specifies direction before data collection. On Israeli exams, misidentifying tail direction is the most common reason for losing full credit."""

WE2_HE = """השוו כיצד אותה סטטיסטיקת מבחן מובילה למסקנות שונות בהתאם לכך שהאלטרנטיבה דו-זנבית או חד-זנבית.

### צעד 1: הגדרה דו-זנבית (תרחיש A)
יצרן תרופה טוען שהכדור אינו משפיע על קצב הלב ($H_0:\\mu=70$, $H_1:\\mu\\neq70$). דחה אם $|z| > 1.96$ ב-$\\alpha=0.05$. גם קצב לב גבוה **וגם** נמוך בצורה חריגה מובילים לדחייה — המבחן סימטרי סביב ערך האפס.

### צעד 2: הגדרה חד-זנבית (תרחיש B)
ממריץ טוען לעלייה במהירות תגובה ($H_0:\\mu\\leq0$, $H_1:\\mu>0$). דחה רק אם $z > 1.645$. ירידות מתעלמות לחלוטין — רק ראיות לשיפור נספרות.

### צעד 3: השוואת p-values ל-$z=1.7$
- דו-זנבי: $p = 2P(Z>1.7) = 0.089$. לא מובהק ב-$\\alpha=0.05$.
- חד-זנבי (ימין): $p = P(Z>1.7) = 0.0446$. מובהק ב-$\\alpha=0.05$.

### צעד 4: פרשנות ואזהרה
אותו $z$, מסקנה שונה. מבחן חד-זנבי מרכז את כל $\\alpha$ בכיוון אחד (עוצמה גבוהה יותר שם) אך לא יכול לגלות אפקטים בכיוון ההפוך. בחירת הזנב לאחר הנתונים (p-hacking) מחצה את ה-p-value.

**כלל:** בחרו חד-זנבי רק כשתאוריה או טרום-רישום קובעים כיוון לפני איסוף הנתונים. בבחינות ישראליות, זיהוי שגוי של כיוון הזנב הוא הסיבה הנפוצה ביותר לאיבוד ניקוד."""

WE3_EN = """**Problem:** Test $H_0:\\mu=\\mu_0$ vs $H_1:\\mu=\\mu_0+2$ (detect shift $\\delta=2$) with $\\sigma=10$, desired power $1-\\beta=0.80$, significance $\\alpha=0.05$ (two-tailed). How large must $n$ be?

Sample-size formulas answer: \"How many observations do I need to have an 80% chance of detecting a real effect of size 2?\"

### Move 1: Look up critical z-values
- $z_{\\alpha/2} = z_{0.025} = 1.96$ (significance constraint).
- $z_\\beta = z_{0.20} = 0.842$ (power constraint, since $\\beta = 0.20$).

### Move 2: Apply the power formula
$$n = \\left(\\frac{(z_{\\alpha/2} + z_\\beta)\\,\\sigma}{\\delta}\\right)^2 = \\left(\\frac{(1.96 + 0.842) \\cdot 10}{2}\\right)^2.$$

### Move 3: Evaluate
$$n = \\left(\\frac{2.802 \\cdot 10}{2}\\right)^2 = (14.01)^2 = 196.3.$$

### Move 4: Round up
$n = 197$ (always round up — fractional samples are impossible).

**Interpretation:** With 197 observations, a two-tailed z-test at $\\alpha=0.05$ has at least 80% power to detect a true mean shift of 2 units from $\\mu_0$.

**Sanity check:** If we used only $z_{\\alpha/2}$ (ignoring power), we would get $n=(1.96\\cdot10/2)^2=96$ — far too small to reliably detect the effect. The $z_\\beta$ term accounts for the need to reject when the alternative is true."""

WE3_HE = """**בעיה:** בדיקת $H_0:\\mu=\\mu_0$ מול $H_1:\\mu=\\mu_0+2$ (גילוי הפרש $\\delta=2$) עם $\\sigma=10$, עוצמה רצויה $1-\\beta=0.80$, מובהקות $\\alpha=0.05$ (דו-זנבי). כמה גדול חייב להיות $n$?

נוסחאות גודל מדגם עונות: \"כמה תצפיות נדרשות כדי שיהיה 80% סיכוי לגלות אפקט אמיתי בגודל 2?\"

### צעד 1: חיפוש ערכי z קריטיים
- $z_{\\alpha/2} = z_{0.025} = 1.96$ (אילוץ מובהקות).
- $z_\\beta = z_{0.20} = 0.842$ (אילוץ עוצמה, כי $\\beta = 0.20$).

### צעד 2: יישום נוסחת העוצמה
$$n = \\left(\\frac{(z_{\\alpha/2} + z_\\beta)\\,\\sigma}{\\delta}\\right)^2 = \\left(\\frac{(1.96 + 0.842) \\cdot 10}{2}\\right)^2.$$

### צעד 3: חישוב
$$n = \\left(\\frac{2.802 \\cdot 10}{2}\\right)^2 = (14.01)^2 = 196.3.$$

### צעד 4: עיגול למעלה
$n = 197$ (תמיד עיגול למעלה — אי אפשר חלק תצפיות).

**פירוש:** עם 197 תצפיות, מבחן z דו-זנבי ב-$\\alpha=0.05$ יש לו לפחות 80% עוצמה לגלות הפרש ממוצע אמיתי של 2 יחידות מ-$\\mu_0$.

**בדיקת הגיון:** אם היינו משתמשים רק ב-$z_{\\alpha/2}$ (מתעלמים מעוצמה), היינו מקבלים $n=(1.96\\cdot10/2)^2=96$ — קטן מדי לגילוי אמין. איבר $z_\\beta$ מחשב את הצורך לדחות כשהאלטרנטיבה נכונה."""

METHOD_EN = """| Situation | Test | Statistic | Rejection region |
|---|---|---|---|
| $\\sigma$ known, large $n$ | z-test | $Z=(\\bar{x}-\\mu_0)/(\\sigma/\\sqrt{n})$ | $|Z|>z_{\\alpha/2}$ |
| $\\sigma$ unknown, normal data | t-test | $T=(\\bar{x}-\\mu_0)/(s/\\sqrt{n})$ | $|T|>t_{\\alpha/2,n-1}$ |
| Proportion test | z-test for $p$ | $Z=(\\hat{p}-p_0)/\\sqrt{p_0(1-p_0)/n}$ | $|Z|>z_{\\alpha/2}$ |
| Effect in specified direction | One-tailed | As above | $Z>z_\\alpha$ or $Z<-z_\\alpha$ |
| Any effect | Two-tailed | As above | $|Z|>z_{\\alpha/2}$ |

**6-step hypothesis testing procedure:**
1. State $H_0$ and $H_1$ (including direction).
2. Choose significance level $\\alpha$.
3. Compute the test statistic from the data.
4. Find the p-value (or compare to critical value).
5. Make the decision: reject or fail to reject $H_0$.
6. State the conclusion **in context** — never say \"accept $H_0$.\"

**Decision shortcut:** If the exam gives a CI, check whether $\\mu_0$ falls inside — outside means reject. If given $|z|$, compare directly to the critical value for the stated tail direction."""

METHOD_HE = """| מצב | מבחן | סטטיסטיקה | אזור דחייה |
|---|---|---|---|
| $\\sigma$ ידוע, $n$ גדול | z | $Z=(\\bar{x}-\\mu_0)/(\\sigma/\\sqrt{n})$ | $|Z|>z_{\\alpha/2}$ |
| $\\sigma$ לא ידוע, נתונים נורמליים | t | $T=(\\bar{x}-\\mu_0)/(s/\\sqrt{n})$ | $|T|>t_{\\alpha/2,n-1}$ |
| בדיקת פרופורציה | z | $Z=(\\hat{p}-p_0)/\\sqrt{p_0(1-p_0)/n}$ | $|Z|>z_{\\alpha/2}$ |
| אפקט בכיוון מוגדר | חד-זנבי | כמו למעלה | $Z>z_\\alpha$ או $Z<-z_\\alpha$ |
| כל אפקט | דו-זנבי | כמו למעלה | $|Z|>z_{\\alpha/2}$ |

**6 שלבי בדיקת השערה:**
1. הצהירו $H_0$ ו-$H_1$ (כולל כיוון).
2. בחרו רמת מובהקות $\\alpha$.
3. חשבו סטטיסטיקת מבחן מהנתונים.
4. מצאו p-value (או השוו לערך קריטי).
5. קבלו החלטה: דחו או אל תדחו $H_0$.
6. נסחו מסקנה **בהקשר** — לעולם אל תגידו \"מקבלים $H_0$.\"

**קיצור החלטה:** אם ניתן CI, בדקו האם $\\mu_0$ בפנים — מחוץ = דחייה. אם ניתן $|z|$, השוו ישירות לערך קריטי לפי כיוון הזנב."""

PITFALL_EN = """1. **\"Fail to reject\" $\\neq$ \"Accept $H_0$.\"** Absence of evidence is not evidence of absence. We never prove the null — we only lack sufficient evidence against it.

2. **p-value $\\neq$ $P(H_0\\text{ true})$.** The p-value is $P(\\text{data this extreme} \\mid H_0)$, a conditional probability under the null. It is NOT the probability that $H_0$ is true (that would require Bayesian inference with a prior).

3. **Choosing one-tailed after seeing data.** Switching to a one-tailed test because the result \"looks right\" halves the p-value dishonestly — this is p-hacking. Pre-register your direction.

4. **Confusing $\\alpha$ and $\\beta$.** $\\alpha$ is chosen by the researcher before the study. $\\beta$ depends on the true effect size, $n$, and $\\sigma$ — it is not fixed by declaration alone.

5. **Statistical significance $\\neq$ practical significance.** A tiny p-value with huge $n$ can detect a negligible effect that has no real-world importance. Always report effect size alongside p-values.

6. **Ignoring multiple comparisons.** Running 20 independent tests at $\\alpha=0.05$ gives $1-(0.95)^{20} \\approx 64\\%$ chance of at least one spurious rejection. Use Bonferroni or FDR corrections."""

PITFALL_HE = """1. **\"אין לדחות\" $\\neq$ \"מקבלים $H_0$.\"** אי-ראיות אינן ראיות להיפך. לעולם לא מוכיחים את האפס — רק חסרות ראיות מספיקות נגדו.

2. **p-value $\\neq$ $P(H_0\\text{ נכונה})$.** ה-p-value הוא $P(\\text{נתונים קיצוניים כ\"כ} \\mid H_0)$, הסתברות מותנית תחת האפס. זו **לא** ההסתברות ש-$H_0$ נכונה (זה דורש הסקה בייסיאנית עם פריור).

3. **בחירת חד-זנבי לאחר ראיית הנתונים.** מעבר לחד-זנבי כי התוצאה \"נראית נכונה\" מחצה את ה-p-value — p-hacking. רשמו מראש את הכיוון.

4. **בלבול בין $\\alpha$ ל-$\\beta$.** $\\alpha$ נבחר על ידי החוקר לפני המחקר. $\\beta$ תלוי בגודל האפקט האמיתי, $n$ ו-$\\sigma$ — לא נקבע בהצהרה בלבד.

5. **מובהקות סטטיסטית $\\neq$ מובהקות מעשית.** p-value קטן עם $n$ ענק יכול לגלות אפקט זניח ללא חשיבות בעולם האמיתי. דווחו תמיד גודל אפקט לצד p-values.

6. **התעלמות מהשוואות מרובות.** 20 מבחנים בלתי-תלויים ב-$\\alpha=0.05$ נותנים $1-(0.95)^{20} \\approx 64\\%$ סיכוי לדחייה מדומה. השתמשו בתיקוני בונפרוני או FDR."""

WHY_EN = """Hypothesis testing is the bridge from descriptive statistics to scientific inference — every clinical trial, quality-control audit, A/B test, and election poll relies on it.

**Builds on:**
- `concept:distributions` — normal CDF, z-scores, t-distribution
- `concept:normal_distribution_z_scores` — standardization for test statistics
- `concept:descriptive_statistics` — sample mean and standard deviation

**Leads to:**
- `concept:statistics_inference` — confidence intervals and their duality with tests
- `concept:linear_regression_correlation` — testing slopes and correlations

**Why it matters for exams:** Israeli university courses (especially Technion and TAU statistics) routinely ask you to compute z, interpret errors, prove CI–test equivalence, and determine sample size. Bagrut 5-unit extensions include basic hypothesis setup. Transfer skill: recognize whether a problem is a test, a CI, or a power calculation before writing any formula."""

WHY_HE = """בדיקת השערות היא הגשר מסטטיסטיקה תיאורית להסקה מדעית — כל ניסוי קlinי, ביקורת בקרת איכות, A/B test וסקר בחירות מסתמכים עליה.

**מבוסס על:**
- `concept:distributions` — CDF נורמלי, ציוני z, התפלגות t
- `concept:normal_distribution_z_scores` — תקנון לסטטיסטיקות מבחן
- `concept:descriptive_statistics` — ממוצע וסטיית תקן מדגמיים

**מוביל ל:**
- `concept:statistics_inference` — רווחי סמך ודואליותם עם מבחנים
- `concept:linear_regression_correlation` — בדיקת שיפועים ומתאמים

**למה זה חשוב לבחינות:** קורסים אוניברסיטאיים (במיוחד טכניון ו-TAU) שואלים לחשב z, לפרש שגיאות, להוכיח שקילות CI–מבחן, ולקבוע גודל מדגם. הרחבות בגרות 5 יחידות כוללות הגדרת השערות בסיסית. מיומנות העברה: זיהוי האם בעיה היא מבחן, CI או חישוב עוצמה לפני כתיבת נוסחה."""

BEFORE_EN = """**Formula sheet:**
- z-statistic: $Z=(\\bar{x}-\\mu_0)/(\\sigma/\\sqrt{n})$
- t-statistic: $T=(\\bar{x}-\\mu_0)/(s/\\sqrt{n})$, $df=n-1$
- Power sample size: $n=((z_{\\alpha/2}+z_\\beta)\\sigma/\\delta)^2$ — round up
- Key z-values: $z_{0.05}=1.645$, $z_{0.025}=1.96$, $z_{0.005}=2.576$
- Key $\\beta$ values: $z_{0.20}=0.842$ (80% power), $z_{0.10}=1.282$ (90% power)

**What Israeli university exams emphasise:**
- Computing z (or t) and making a reject/fail-to-reject decision
- Identifying Type I and Type II errors with context examples
- One-tailed vs two-tailed setup and p-value direction
- Sample size determination for desired power
- Proving equivalence of z-test and confidence interval

**Common proof pattern:** CI–test duality — reject $H_0$ iff $\\mu_0$ outside $(1-\\alpha)$ CI. Know the algebraic chain cold."""

BEFORE_HE = """**גיליון נוסחאות:**
- $Z=(\\bar{x}-\\mu_0)/(\\sigma/\\sqrt{n})$
- $T=(\\bar{x}-\\mu_0)/(s/\\sqrt{n})$, $df=n-1$
- גודל מדגם: $n=((z_{\\alpha/2}+z_\\beta)\\sigma/\\delta)^2$ — עיגול למעלה
- $z_{0.05}=1.645$, $z_{0.025}=1.96$, $z_{0.005}=2.576$
- $z_{0.20}=0.842$ (80% עוצמה), $z_{0.10}=1.282$ (90% עוצמה)

**מה בחינות ישראליות מדגישות:**
- חישוב z (או t) והחלטת דחייה/אי-דחייה
- זיהוי שגיאות סוג I/II עם דוגמאות הקשר
- הגדרת חד-זנבי מול דו-זנבי וכיוון p-value
- קביעת גודל מדגם לעוצמה רצויה
- הוכחת שקילות מבחן z ורווח סמך

**דפוס הוכחה נפוץ:** דואליות CI–מבחן — דחה $H_0$ אמ\"מ $\\mu_0$ מחוץ ל-CI $(1-\\alpha)$. שלטו בשרשרת האלגברית."""

SUMMARY_EN = """- **Hypothesis testing** decides whether data is compatible with $H_0$ by computing $P(\\text{this extreme} \\mid H_0)$ = p-value.
- **z-test:** $Z=(\\bar{x}-\\mu_0)/(\\sigma/\\sqrt{n})$. Reject $H_0$ if $p<\\alpha$ or $|Z|>z_{\\alpha/2}$.
- **t-test:** Use when $\\sigma$ is unknown; compare $|T|$ to $t_{\\alpha/2,n-1}$.
- **Type I error** (false positive): $P=\\alpha$. **Type II error** (false negative): $P=\\beta$. **Power** $=1-\\beta$.
- **One-tailed vs two-tailed:** choose direction before data; one-tailed is more powerful but directional.
- **Sample size:** $n=((z_{\\alpha/2}+z_\\beta)\\sigma/\\delta)^2$, always round up.
- **CI–test duality:** reject $H_0$ iff $\\mu_0$ is outside the $(1-\\alpha)$ confidence interval."""

SUMMARY_HE = """- **בדיקת השערות** מחליטה האם נתונים מתיישבים עם $H_0$ ע\"י חישוב $P(\\text{קיצוני כ\"כ} \\mid H_0)$ = p-value.
- **מבחן z:** $Z=(\\bar{x}-\\mu_0)/(\\sigma/\\sqrt{n})$. דחה $H_0$ אם $p<\\alpha$ או $|Z|>z_{\\alpha/2}$.
- **מבחן t:** כש-$\\sigma$ לא ידוע; השוו $|T|$ ל-$t_{\\alpha/2,n-1}$.
- **שגיאת סוג I** (חיובי שגוי): $P=\\alpha$. **שגיאת סוג II** (שלילי שגוי): $P=\\beta$. **עוצמה** $=1-\\beta$.
- **חד-זנבי מול דו-זנבי:** בחרו כיוון לפני הנתונים; חד-זנבי חזק יותר אך כיווני.
- **גודל מדגם:** $n=((z_{\\alpha/2}+z_\\beta)\\sigma/\\delta)^2$, תמיד עיגול למעלה.
- **דואליות CI–מבחן:** דחה $H_0$ אמ\"מ $\\mu_0$ מחוץ לרווח הסמך $(1-\\alpha)$."""

CKPT1_EN = """Repeat the z-test from Example 1, but now $\\bar{x}=54$ (instead of 52). Same parameters: $\\mu_0=50$, $\\sigma=10$, $n=25$, $\\alpha=0.05$ two-tailed.

**Step 1:** Standard error $SE = 10/\\sqrt{25} = 2$.

**Step 2:** Test statistic:
$$z = \\frac{54 - 50}{2} = \\frac{4}{2} = 2.0.$$

**Step 3:** Two-tailed p-value:
$$p = 2P(Z > 2.0) = 2(1 - 0.9772) = 2(0.0228) = 0.0456.$$

**Step 4:** Compare: $p = 0.0456 < 0.05 = \\alpha$.

**Conclusion:** Reject $H_0$. At the 5% level, there is sufficient evidence that the true mean differs from 50. Note how moving $\\bar{x}$ from 52 to 54 (just 2 units) crosses the significance threshold because $z$ doubled from 1.0 to 2.0."""

CKPT1_HE = """חזרו על מבחן z מדוגמה 1, אך עם $\\bar{x}=54$ (במקום 52). אותם פרמטרים: $\\mu_0=50$, $\\sigma=10$, $n=25$, $\\alpha=0.05$ דו-זנבי.

**שלב 1:** שגיאת תקן $SE = 10/\\sqrt{25} = 2$.

**שלב 2:** סטטיסטיקת מבחן:
$$z = \\frac{54 - 50}{2} = \\frac{4}{2} = 2.0.$$

**שלב 3:** p-value דו-זנבי:
$$p = 2P(Z > 2.0) = 2(1 - 0.9772) = 2(0.0228) = 0.0456.$$

**שלב 4:** השוואה: $p = 0.0456 < 0.05 = \\alpha$.

**מסקנה:** דחו $H_0$. ברמת 5% יש ראיות מספיקות שהממוצע האמיתי שונה מ-50. שימו לב: מעבר מ-$\\bar{x}=52$ ל-54 (רק 2 יחידות) חוצה את סף המובהקות כי $z$ הוכפל מ-1.0 ל-2.0."""

CKPT2_EN = """For $z=2.1$, find the two-tailed p-value and decide at $\\alpha=0.05$.

**Step 1:** Recognize this is a two-tailed test — we need probability in **both** tails beyond $|z|=2.1$.

**Step 2:** From the standard normal table, $P(Z > 2.1) = 0.0179$.

**Step 3:** Two-tailed p-value:
$$p = 2 \\cdot P(Z > 2.1) = 2(0.0179) = 0.0357.$$

**Step 4:** Compare: $p = 0.0357 < 0.05 = \\alpha$.

**Conclusion:** Reject $H_0$. The observed $z=2.1$ is statistically significant at the 5% level. Sanity check: $|z|=2.1 > 1.96 = z_{0.025}$, which confirms rejection without computing $p$ exactly."""

CKPT2_HE = """עבור $z=2.1$, מצאו p-value דו-זנבי והחליטו ב-$\\alpha=0.05$.

**שלב 1:** זיהוי מבחן דו-זנבי — צריך הסתברות ב**שני** הזנבות מעבר ל-$|z|=2.1$.

**שלב 2:** מטבלת נורמל סטנדרטית, $P(Z > 2.1) = 0.0179$.

**שלב 3:** p-value דו-זנבי:
$$p = 2 \\cdot P(Z > 2.1) = 2(0.0179) = 0.0357.$$

**שלב 4:** השוואה: $p = 0.0357 < 0.05 = \\alpha$.

**מסקנה:** דחו $H_0$. $z=2.1$ הנצפה מובהק סטטיסטית ברמת 5%. בדיקת הגיון: $|z|=2.1 > 1.96 = z_{0.025}$, מאשר דחייה בלי חישוב $p$ מדויק."""

# Question explanations (80-150 words each)
Q_EXPL = [
    fmt_expl(
        "$SE=\\sigma/\\sqrt{n}=8/4=2$. Then $z=(48-50)/2=-1.0$. Two-tailed p-value: $p=2P(Z>1)=2(0.1587)=0.317$. Since $0.317>0.05$, we fail to reject $H_0$. The sample mean 48 is only one standard error below 50 — not surprising under the null.",
        "Always compute $SE=\\sigma/\\sqrt{n}$ first, then standardize. For two-tailed tests, double the one-tail probability. Check whether $|z|$ exceeds 1.96 before looking up tables.",
        "Using $\\sigma=8$ directly as the denominator instead of $SE=2$. Forgetting to double for two-tailed p-value. Rejecting because $\\bar{x}\\neq\\mu_0$ without comparing $p$ to $\\alpha$.",
        "Write $SE$ on scratch paper before computing $z$. If $|z|<1.96$ at $\\alpha=0.05$, you can often skip the p-value lookup and conclude fail-to-reject immediately.",
        "$SE=\\sigma/\\sqrt{n}=8/4=2$. אז $z=(48-50)/2=-1.0$. p-value דו-זנבי: $p=2P(Z>1)=0.317$. כיוון $0.317>0.05$, אין לדחות $H_0$. ממוצע 48 נמצא רק בשגיאת תקן אחת מתחת ל-50 — לא מפתיע תחת האפס.",
        "תמיד חשבו $SE=\\sigma/\\sqrt{n}$ קודם, ואז תקננו. במבחנים דו-זנביים, הכפילו את הסתברות הזנב. בדקו האם $|z|$ עולה על 1.96 לפני חיפוש בטבלה.",
        "שימוש ב-$\\sigma=8$ ישירות במכנה במקום $SE=2$. שכחה להכפיל ב-2 ל-p-value דו-זנבי. דחייה כי $\\bar{x}\\neq\\mu_0$ בלי השוואת $p$ ל-$\\alpha$.",
        "כתבו $SE$ על טיוטה לפני חישוב $z$. אם $|z|<1.96$ ב-$\\alpha=0.05$, לעיתים אפשר לדלג על p-value ולהסיק אי-דחייה מיד.",
    ),
    fmt_expl(
        "$SE=15/\\sqrt{25}=3$. Then $z=(106-100)/3=2.0$. For a **right-tailed** test ($H_1:\\mu>100$), $p=P(Z>2)=0.0228<0.05$. Reject $H_0$ — the sample mean significantly exceeds the hypothesized value.",
        "Read $H_1:\\mu>100$ carefully — this is one-tailed right, so use $p=P(Z>z)$, not $2P(Z>|z|)$. Compare $z=2.0$ to critical value 1.645, not 1.96.",
        "Doubling the p-value for a one-tailed test (getting 0.046 and still rejecting, but with wrong reasoning). Using two-tailed critical value 1.96 and incorrectly failing to reject. Computing $z=(106-100)/15$ without dividing by $SE$.",
        "Circle the direction in $H_1$ before any arithmetic. One-tailed right: reject if $z>1.645$. One-tailed left: reject if $z<-1.645$. Two-tailed: reject if $|z|>1.96$.",
        "$SE=15/\\sqrt{25}=3$. אז $z=(106-100)/3=2.0$. במבחן **חד-זנבי ימין** ($H_1:\\mu>100$), $p=P(Z>2)=0.0228<0.05$. דחו $H_0$ — ממוצע המדגם עולה בצורה מובהקת על הערך ההשערתי.",
        "קראו $H_1:\\mu>100$ בזהירות — חד-זנבי ימין, אז $p=P(Z>z)$, לא $2P(Z>|z|)$. השוו $z=2.0$ לערך קריטי 1.645, לא 1.96.",
        "הכפלת p-value במבחן חד-זנבי (0.046 עם דחייה אך נימוק שגוי). ערך קריטי דו-זנבי 1.96 ואי-דחייה בטעות. $z=(106-100)/15$ בלי $SE$.",
        "סמנו את כיוון $H_1$ לפני חישוב. חד-זנבי ימין: דחו אם $z>1.645$. שמאל: דחו אם $z<-1.645$. דו-זנבי: דחו אם $|z|>1.96$.",
    ),
    fmt_expl(
        "**Type I error:** Rejecting $H_0$ when it is true — a false positive. Medical example: diagnosing a healthy person as sick. **Type II error:** Failing to reject $H_0$ when $H_1$ is true — a false negative. Example: missing a disease in a sick person.",
        "Type I is controlled by $\\alpha$. Type II depends on effect size and $n$. Think courtroom: Type I = convicting innocent; Type II = acquitting guilty.",
        "Swapping the definitions (calling Type I \"missing the effect\"). Saying Type II is controlled by $\\alpha$. Giving non-medical examples when the question asks specifically for medical ones.",
        "Memorize: Type **I** = **I**nnocent convicted (reject true null). Type **II** = guilty goes free (fail to reject false null). Link $\\alpha$ to Type I and power $1-\\beta$ to detecting real effects.",
        "**שגיאת סוג I:** דחיית $H_0$ כשהיא נכונה — חיובי שגוי. דוגמה רפואית: אבחון בריא כחולה. **שגיאת סוג II:** אי-דחיית $H_0$ כש-$H_1$ נכונה — שלילי שגוי. דוגמה: החמצת מחלה אצל חולה.",
        "סוג I נשלט על ידי $\\alpha$. סוג II תלוי בגודל אפקט וגודל מדגם ($\\beta$ קטן כש-$n$ גדל). חשבו על בית משפט: סוג I = הרשעת חף; סוג II = שחרור אשם.",
        "החלפת ההגדרות (קריאה לסוג I \"החמצת אפקט\"). אמרה שסוג II נשלט על ידי $\\alpha$. דוגמאות לא-רפואיות כשהשאלה מבקשת רפואיות.",
        "שיננו: סוג **I** = הרשעת **ח**ף (דחיית אפס נכון). סוג **II** = שחרור אשם (אי-דחיית אפס שגוי). קשרו $\\alpha$ לסוג I ועוצמה $1-\\beta$ לגילוי אפקטים.",
    ),
    fmt_expl(
        "For a two-tailed test at $\\alpha=0.01$, the critical value is $z_{\\alpha/2}=z_{0.005}=2.576$. This leaves 0.5% in each tail, totaling 1% significance.",
        "Two-tailed: divide $\\alpha$ by 2 to find the tail area, then look up $z$ for that upper-tail probability. Here $\\alpha/2=0.005$, so find $z$ with $P(Z>z)=0.005$.",
        "Using $z_{0.01}=2.326$ (confusing $\\alpha$ with $\\alpha/2$). Answering 1.96 (the $\\alpha=0.05$ value). Using one-tailed critical value when the question says two-tailed.",
        "Memorize the trio: $z_{0.05}=1.645$ (one-tailed 5%), $z_{0.025}=1.96$ (two-tailed 5%), $z_{0.005}=2.576$ (two-tailed 1%). These appear on every exam formula sheet.",
        "למבחן דו-זנבי ב-$\\alpha=0.01$, הערך הקריטי הוא $z_{\\alpha/2}=z_{0.005}=2.576$. זה משאיר 0.5% בכל זנב, סה\"כ 1% מובהקות.",
        "דו-זנבי: חלקו $\\alpha$ ב-2 למציאת שטח זנב, ואז חפשו $z$ להסתברות זנב עליון. כאן $\\alpha/2=0.005$, מצאו $z$ עם $P(Z>z)=0.005$.",
        "שימוש ב-$z_{0.01}=2.326$ (בלבול $\\alpha$ עם $\\alpha/2$). תשובה 1.96 (ערך $\\alpha=0.05$). ערך קריטי חד-זנבי כשהשאלה אומרת דו-זנבי.",
        "שיננו את השלישייה: $z_{0.05}=1.645$ (חד-5%), $z_{0.025}=1.96$ (דו-5%), $z_{0.005}=2.576$ (דו-1%). מופיעים בכל גיליון נוסחאות.",
    ),
    fmt_expl(
        "$SE=s/\\sqrt{n}=1.2/3=0.4$. Then $T=(12.5-12)/0.4=0.5/0.4=1.25$. Degrees of freedom: $df=n-1=8$. Since $|T|=1.25<2.306=t_{0.025,8}$, fail to reject $H_0$ at $\\alpha=0.05$ two-tailed.",
        "When $\\sigma$ is unknown, use $s$ and the t-distribution. $df=n-1$. Compare $|T|$ to the given critical value $t_{\\alpha/2,df}$, not to 1.96.",
        "Using $z=1.96$ instead of the t critical value 2.306. Computing $T=(12.5-12)/1.2$ without dividing by $SE$. Forgetting that t critical values are larger than z (heavier tails).",
        "For small $n$, always use t, not z. The exam often provides $t_{0.025,8}$ directly — just compare $|T|$ to it. If $|T|$ is clearly less than 2, you can skip exact p-value computation.",
        "$SE=s/\\sqrt{n}=1.2/3=0.4$. אז $T=(12.5-12)/0.4=1.25$. דרגות חופש: $df=8$. כיוון $|T|=1.25<2.306=t_{0.025,8}$, אין לדחות $H_0$ ב-$\\alpha=0.05$ דו-זנבי.",
        "כש-$\\sigma$ לא ידוע, השתמשו ב-$s$ ובהתפלגות t. $df=n-1$. השוו $|T|$ לערך קריטי $t_{\\alpha/2,df}$, לא ל-1.96.",
        "שימוש ב-$z=1.96$ במקום t קריטי 2.306. $T=(12.5-12)/1.2$ בלי $SE$. שכחה שערכי t גדולים מ-z (זנבות כבדים).",
        "ל-$n$ קטן, תמיד t, לא z. הבחינה לעיתים נותנת $t_{0.025,8}$ — השוו $|T|$ אליו. אם $|T|$ קטן בבירור מ-2, אפשר לדלג על p-value.",
    ),
    fmt_expl(
        "$SE=12/\\sqrt{36}=2$. Test: $z=(497-500)/2=-1.5$. Two-tailed $p=2(0.0668)=0.134>0.05$ — fail to reject. 95% CI: $497\\pm1.96(2)=(493.08,\\ 500.92)$. Note $\\mu_0=500$ lies inside the CI, consistent with fail-to-reject.",
        "This problem combines hypothesis test and CI — use the CI–test duality. Compute $SE$, then $z$ and CI in parallel. If $\\mu_0$ is inside the CI, you should fail to reject (and vice versa).",
        "Using $\\sigma=12$ as margin of error instead of $1.96\\times SE$. Reporting CI without checking consistency with test decision. Computing $z=(497-500)/12$ without $SE$.",
        "After computing both test and CI, verify duality: reject iff $\\mu_0$ outside CI. This cross-check catches arithmetic errors on exams.",
        "$SE=12/\\sqrt{36}=2$. מבחן: $z=-1.5$, $p=0.134>0.05$ — אין לדחות. CI 95%: $497\\pm1.96(2)=(493.08,\\ 500.92)$. $\\mu_0=500$ בתוך CI — עקבי עם אי-דחייה.",
        "שאלה זו משלבת מבחן ו-CI — השתמשו בדואליות. חשבו $SE$, ואז $z$ ו-CI במקביל. אם $\\mu_0$ בתוך CI, אין לדחות (ולהיפך).",
        "שימוש ב-$\\sigma=12$ כשגיאת דגימה במקום $1.96\\times SE$. CI בלי בדיקת עקביות עם החלטת המבחן. $z=(497-500)/12$ בלי $SE$.",
        "אחרי חישוב מבחן ו-CI, ודאו דואליות: דחייה אמ\"מ $\\mu_0$ מחוץ ל-CI. בדיקה זו תופסת טעויות חשבון בבחינה.",
    ),
    fmt_expl(
        "Increasing $n$ decreases the standard error $\\sigma/\\sqrt{n}$, which makes the test statistic larger (in absolute value) for the same true effect $\\delta$. Larger $|Z|$ means higher power $1-\\beta$, so Type II error probability $\\beta$ **decreases**.",
        "Think of $n$ as \"precision.\" More data tightens the sampling distribution of $\\bar{X}$, making it easier to distinguish $\\mu_0$ from $\\mu_1$. Power increases with $n$; $\\alpha$ and $\\delta$ are held fixed in this question.",
        "Answering that Type II error increases with $n$ (confusing with the $\\alpha$–$\\beta$ trade-off when $\\alpha$ changes). Saying nothing changes because $\\alpha$ is fixed — $\\beta$ still changes with $n$.",
        "On sample-size problems, remember: bigger $n$ → smaller $SE$ → bigger $|Z|$ → higher power → lower $\\beta$. This chain appears in both conceptual and computational questions.",
        "הגדלת $n$ מקטינה $SE=\\sigma/\\sqrt{n}$, מה שמגדיל (בערך מוחלט) את סטטיסטיקת המבחן לאותו $\\delta$. $|Z|$ גדול יותר = עוצמה $1-\\beta$ גבוהה יותר, ולכן $\\beta$ **קטן**.",
        "חשבו על $n$ כ\"דיוק.\" יותר נתונים מצרים את התפלגות $\\bar{X}$, ומקלים להבחין $\\mu_0$ מ-$\\mu_1$. עוצמה גדלה עם $n$; $\\alpha$ ו-$\\delta$ קבועים כאן.",
        "תשובה ש-$\\beta$ גדל עם $n$ (בלבול עם פשרת $\\alpha$–$\\beta$). \"שום דבר לא משתנה כי $\\alpha$ קבוע\" — $\\beta$ כן משתנה עם $n$.",
        "בשאלות גודל מדגם: $n$ גדול → $SE$ קטן → $|Z|$ גדול → עוצמה גבוהה → $\\beta$ נמוך. שרשרת זו מופיעה בשאלות מושגיות וחישוביות.",
    ),
    fmt_expl(
        "The p-value is $P(\\text{data at least this extreme} \\mid H_0\\text{ true})$ — a conditional probability **assuming** the null. It is NOT $P(H_0\\text{ true} \\mid \\text{data})$, which is a Bayesian posterior requiring a prior belief about $H_0$.",
        "In the frequentist framework, $H_0$ is either true or false (not random), so $P(H_0\\text{ true})$ is undefined without a prior. The p-value measures how compatible the data are with $H_0$, not how likely $H_0$ is.",
        "Saying \"p-value is the probability the result happened by chance\" without specifying \"by chance **if $H_0$ is true**.\" Confusing p-value with $\\alpha$. Claiming a large p-value \"proves $H_0$.\"",
        "Exam essay questions often ask this exact distinction. Write both formulas: $P(\\text{data}\\mid H_0)$ vs $P(H_0\\mid\\text{data})$. Mention that the latter needs Bayes' theorem and a prior.",
        "ה-p-value הוא $P(\\text{נתונים קיצוניים כ\"כ} \\mid H_0\\text{ נכונה})$ — הסתברות מותנית **בהנחה** שהאפס נכון. זו **לא** $P(H_0\\text{ נכונה} \\mid \\text{נתונים})$, שהיא פוסטריאור בייסיאני הדורש פריור.",
        "במסגרת frequentist, $H_0$ נכונה או לא (לא אקראית), ולכן $P(H_0\\text{ נכונה})$ לא מוגדרת בלי פריור. ה-p-value מודד התאמה של נתונים ל-$H_0$, לא כמה $H_0$ סבירה.",
        "\"p-value הוא הסתברות שהתוצאה קרתה במקרה\" בלי \"**אם $H_0$ נכונה**.\" בלבול p-value עם $\\alpha$. טענה ש-p-value גדול \"מוכיח $H_0$.\"",
        "שאלות חיבור בבחינה שואלות את ההבחנה הזו. כתבו שתי נוסחאות: $P(\\text{נתונים}\\mid H_0)$ מול $P(H_0\\mid\\text{נתונים})$. ציינו שהשנייה דורשת בייס ופריור.",
    ),
]


def build():
    with open(TARGET, encoding="utf-8") as f:
        data = json.load(f)

    sections = data["sections"]
    content_map = {
        "intro": (INTRO_EN, INTRO_HE),
        "definition": (DEF_EN, DEF_HE),
        "theory": (THEORY_EN, THEORY_HE),
        "method_guide": (METHOD_EN, METHOD_HE),
        "pitfall": (PITFALL_EN, PITFALL_HE),
        "why_matters": (WHY_EN, WHY_HE),
        "before_exam": (BEFORE_EN, BEFORE_HE),
        "summary": (SUMMARY_EN, SUMMARY_HE),
    }
    we_map = {1: (WE1_EN, WE1_HE), 2: (WE2_EN, WE2_HE), 3: (WE3_EN, WE3_HE)}
    ckpt_map = {0: (CKPT1_EN, CKPT1_HE), 1: (CKPT2_EN, CKPT2_HE)}
    ckpt_i = 0

    for sec in sections:
        kind = sec.get("kind")
        if kind in content_map:
            sec["body_en_md"], sec["body_he_md"] = content_map[kind]
        elif kind == "worked_example":
            n = sec.get("example_number", 1)
            if n in we_map:
                sec["body_en_md"], sec["body_he_md"] = we_map[n]
        elif kind == "checkpoint":
            if ckpt_i in ckpt_map:
                sec["checkpoint_solution_en"], sec["checkpoint_solution_he"] = ckpt_map[ckpt_i]
                ckpt_i += 1

    for i, q in enumerate(data["questions"]):
        if i < len(Q_EXPL):
            q["explanation_en"], q["explanation_he"] = Q_EXPL[i]

    data["version"] = 2
    return data


def validate(data):
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN:
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            if en_w < MIN[kind][0]:
                issues.append(f"{kind} EN: {en_w} < {MIN[kind][0]}")
            if he_w < MIN[kind][1]:
                issues.append(f"{kind} HE: {he_w} < {MIN[kind][1]}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                issues.append(f"{kind} HE weak")
        elif kind == "worked_example":
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            if en_w < MIN["worked_example"][0]:
                issues.append(f"worked_example EN: {en_w} < {MIN['worked_example'][0]}")
            if he_w < MIN["worked_example"][1]:
                issues.append(f"worked_example HE: {he_w} < {MIN['worked_example'][1]}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                issues.append("worked_example HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80:
                issues.append(f"Q{q['ord']} expl_{lang}: {w} < 80")
            if w > 160:
                issues.append(f"Q{q['ord']} expl_{lang}: {w} > 160 (soft)")

    return issues


def main():
    data = build()
    issues = validate(data)
    if issues:
        print("VALIDATION ISSUES:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("All depth checks passed.")

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {TARGET}")

    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr)
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    if "207/207" not in r.stdout:
        print("WARNING: expected 207/207 in dry-run output")


if __name__ == "__main__":
    main()
