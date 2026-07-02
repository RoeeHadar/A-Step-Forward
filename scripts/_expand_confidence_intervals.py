#!/usr/bin/env python3
"""Expand confidence_intervals.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/confidence_intervals.json"

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


INTRO_EN = """A point estimate such as $\\bar{x}$ or $\\hat{p}$ gives our single best guess for an unknown population parameter, but one number almost never captures the full story. Sampling variability means that repeating the study would produce different estimates — sometimes higher, sometimes lower.

A **confidence interval** (CI) turns that uncertainty into a range of plausible values. Instead of claiming \"the mean is exactly 80,\" we report \"we are 95% confident the true mean lies between 79 and 81.\" This is the natural companion to hypothesis testing: where a test asks whether a hypothesised value is compatible with data, a CI lists all values still compatible at a given confidence level.

**Critical interpretation:** A 95% CI does **not** mean the parameter has a 95% probability of lying inside the interval you just computed. The parameter $\\mu$ or $p$ is fixed; the interval is random because it depends on the sample. The correct reading: if we repeated the sampling procedure many times, about 95% of the constructed intervals would contain the true parameter.

**Builds on:** normal and t distributions, z-scores, and hypothesis testing from `concept:hypothesis_testing`. The CI–test duality (reject $H_0:\\mu=\\mu_0$ iff $\\mu_0$ falls outside the $(1-\\alpha)$ CI) is a favourite proof and short-answer topic on Israeli university exams."""

INTRO_HE = """הערכה נקודתית כמו $\\bar{x}$ או $\\hat{p}$ נותנת את הניחוש הטוב ביותר שלנו לפרמטר אוכלוסייה לא ידוע, אך מספר בודד כמעט אף פעם לא מספר את כל הסיפור. שונות דגימה אומרת שחזרה על המחקר תייצר הערכות שונות — לפעמים גבוהות יותר, לפעמים נמוכות.

**רווח סמך** (CI) הופך אי-ודאות זו לטווח ערכים סבירים. במקום לטעון \"הממוצע הוא בדיוק 80,\" אנו מדווחים \"אנו ב-95% סמך שהממוצע האמיתי נמצא בין 79 ל-81.\" זה השותף הטבעי לבדיקת השערות: מבחן שואל האם ערך השערתי מתיישב עם הנתונים, ו-CI מפרט את כל הערכים שעדיין מתיישבים ברמת סמך נתונה.

**פרשנות קריטית:** CI של 95% **אינו** אומר שלפרמטר יש הסתברות 95% להימצא בתוך הרווח שחישבתם. $\\mu$ או $p$ קבועים; הרווח אקראי כי הוא תלוי במדגם. הקריאה הנכונה: אם נחזור על תהליך הדגימה פעמים רבות, כ-95% מהרווחים שנבנה יכילו את הפרמטר האמיתי.

**מבוסס על:** התפלגויות נורמלית ו-t, ציוני z, ובדיקת השערות מ-`concept:hypothesis_testing`. דואליות CI–מבחן (דחיית $H_0:\\mu=\\mu_0$ אמ\"מ $\\mu_0$ מחוץ ל-CI ברמת $(1-\\alpha)$) היא נושא הוכחה ושאלה קצרה מועדף בבחינות אוניברסיטאיות ישראליות."""

DEF_EN = """**$(1-\\alpha)$ confidence interval for $\\mu$ when $\\sigma$ is known:**
$$\\bar{x} \\pm z_{\\alpha/2}\\cdot\\frac{\\sigma}{\\sqrt{n}}.$$
Use when the population standard deviation is known (or $n$ is large with a reliable $\\sigma$ estimate) and the sampling distribution of $\\bar{X}$ is approximately normal.

**$(1-\\alpha)$ CI for $\\mu$ when $\\sigma$ is unknown:** replace $\\sigma$ with the sample standard deviation $s$ and use the t-distribution:
$$\\bar{x} \\pm t_{\\alpha/2,\\,n-1}\\cdot\\frac{s}{\\sqrt{n}}.$$
Required for small samples from a normal population; for large $n$, $t$ and $z$ nearly coincide.

**$(1-\\alpha)$ CI for a population proportion $p$:**
$$\\hat{p} \\pm z_{\\alpha/2}\\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}, \\quad \\hat{p}=\\frac{x}{n}.$$
Valid when $n\\hat{p}\\geq 5$ and $n(1-\\hat{p})\\geq 5$ (Normal approximation to the binomial).

**Margin of error (MOE):** half-width of the CI:
$$E = z_{\\alpha/2}\\cdot\\frac{\\sigma}{\\sqrt{n}} \\quad \\text{or} \\quad E = z_{\\alpha/2}\\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}.$$
Total **width** $= 2E$. Do not confuse the two on exams.

**Interpretation (frequentist):** We are $(1-\\alpha)\\times 100\\%$ confident the procedure produces an interval containing the true parameter. Equivalently: among many repeated samples, a fraction $1-\\alpha$ of intervals cover the parameter.

**Key z-values:** $z_{0.025}=1.96$ (95% two-tailed), $z_{0.005}=2.576$ (99%), $z_{0.05}=1.645$ (90% one-tailed or 90% CI)."""

DEF_HE = """**רווח סמך $(1-\\alpha)$ ל-$\\mu$ כש-$\\sigma$ ידוע:**
$$\\bar{x} \\pm z_{\\alpha/2}\\cdot\\frac{\\sigma}{\\sqrt{n}}.$$
השתמשו כשסטיית התקן באוכלוסייה ידועה (או $n$ גדול עם הערכת $\\sigma$ אמינה) והתפלגות $\\bar{X}$ קרובה לנורמלית.

**CI ל-$\\mu$ כש-$\\sigma$ לא ידוע:** החליפו $\\sigma$ ב-$s$ מדגמי והשתמשו ב-t:
$$\\bar{x} \\pm t_{\\alpha/2,\\,n-1}\\cdot\\frac{s}{\\sqrt{n}}.$$
נדרש למדגמים קטנים מאוכלוסייה נורמלית; ל-$n$ גדול, t ו-z כמעט זהים.

**CI לפרופורציה $p$:**
$$\\hat{p} \\pm z_{\\alpha/2}\\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}, \\quad \\hat{p}=\\frac{x}{n}.$$
תקף כש-$n\\hat{p}\\geq 5$ ו-$n(1-\\hat{p})\\geq 5$ (קירוב נורמלי לבינומי).

**שגיאת שוליים (MOE):** חצי רוחב:
$$E = z_{\\alpha/2}\\cdot\\frac{\\sigma}{\\sqrt{n}} \\quad \\text{או} \\quad E = z_{\\alpha/2}\\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}.$$
**רוחב** $= 2E$. אל תבלבלו ביניהם בבחינה.

**פרשנות (frequentist):** אנו ב-$(1-\\alpha)\\times 100\\%$ סמך שההליך מייצר רווח המכיל את הפרמטר. שקיל: בין מדגמים חוזרים, שבר $1-\\alpha$ מהרווחים מכסה את הפרמטר.

**ערכי z מרכזיים:** $z_{0.025}=1.96$ (95% דו-זנבי), $z_{0.005}=2.576$ (99%), $z_{0.05}=1.645$ (90%)."""

THEORY_EN = """**Theorem 1 (Coverage for $\\mu$, $\\sigma$ known).** Standardize the sample mean:
$$P\\left(-z_{\\alpha/2}\\leq\\frac{\\bar{X}-\\mu}{\\sigma/\\sqrt{n}}\\leq z_{\\alpha/2}\\right)=1-\\alpha.$$
Rearranging gives the random interval $\\bar{X}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$ that covers $\\mu$ with probability $1-\\alpha$ **before** data are observed. After computing $\\bar{x}$, the endpoints are fixed numbers — the \"95%\" refers to the method, not this particular interval.

**Theorem 2 (Width and precision).** Width $W=2E=2z_{\\alpha/2}\\sigma/\\sqrt{n}$. Width shrinks when $n$ increases ($\\propto 1/\\sqrt{n}$), when $\\sigma$ decreases, or when confidence level decreases (smaller $z_{\\alpha/2}$). Doubling $n$ reduces width by factor $1/\\sqrt{2}\\approx 0.707$, not by half.

**Theorem 3 (Sample size for mean, target MOE $\\leq E_0$):**
$$n\\geq\\left(\\frac{z_{\\alpha/2}\\,\\sigma}{E_0}\\right)^2.$$
Derive by requiring $z_{\\alpha/2}\\sigma/\\sqrt{n}\\leq E_0$ and solving for $n$. Always **round up** to the next integer.

**Theorem 4 (Sample size for proportion, conservative).** Since $p(1-p)\\leq 1/4$ with equality at $p=1/2$:
$$n\\geq\\left(\\frac{z_{\\alpha/2}}{2E_0}\\right)^2.$$
This guarantees MOE $\\leq E_0$ for **any** true $p$, at the cost of a possibly oversized sample.

**CI–test duality.** Rejecting $H_0:\\mu=\\mu_0$ at significance $\\alpha$ (two-tailed) is equivalent to $\\mu_0\\notin\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$. Same logic applies to proportions. Israeli exams frequently ask you to use a CI to decide on a claim about $p$ or $\\mu$."""

THEORY_HE = """**משפט 1 (כיסוי ל-$\\mu$, $\\sigma$ ידוע).** תקנון ממוצע המדגם:
$$P\\left(-z_{\\alpha/2}\\leq\\frac{\\bar{X}-\\mu}{\\sigma/\\sqrt{n}}\\leq z_{\\alpha/2}\\right)=1-\\alpha.$$
סידור מחדש נותן רווח אקראי $\\bar{X}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$ המכסה $\\mu$ בהסתברות $1-\\alpha$ **לפני** צפייה בנתונים. לאחר חישוב $\\bar{x}$, הקצוות קבועים — \"95%\" מתייחס להליך, לא לרווח הספציפי.

**משפט 2 (רוחב ודיוק).** רוחב $W=2E=2z_{\\alpha/2}\\sigma/\\sqrt{n}$. הרוחב קטן כש-$n$ גדל ($\\propto 1/\\sqrt{n}$), כש-$\\sigma$ קטן, או כשרמת הסמך יורדת. הכפלת $n$ מקטינה רוחב פי $1/\\sqrt{2}\\approx 0.707$, לא בחצי.

**משפט 3 (גודל מדגם לממוצע, MOE $\\leq E_0$):**
$$n\\geq\\left(\\frac{z_{\\alpha/2}\\,\\sigma}{E_0}\\right)^2.$$
נגזר מ-$z_{\\alpha/2}\\sigma/\\sqrt{n}\\leq E_0$. תמיד **עגלו למעלה**.

**משפט 4 (גודל מדגם לפרופורציה, שמרני).** כיוון $p(1-p)\\leq 1/4$ עם שוויון ב-$p=1/2$:
$$n\\geq\\left(\\frac{z_{\\alpha/2}}{2E_0}\\right)^2.$$
מבטיח MOE $\\leq E_0$ ל**כל** $p$ אמיתי, במחיר מדגם אפשרי גדול מדי.

**דואליות CI–מבחן.** דחיית $H_0:\\mu=\\mu_0$ ברמת $\\alpha$ (דו-זנבי) שקילה ל-$\\mu_0\\notin\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$. אותה לוגיקה לפרופורציות. בבחינות ישראליות מבקשים לעיתים להשתמש ב-CI כדי להחליט על טענה על $p$ או $\\mu$."""

WE1_EN = """**Given:** $\\bar{x}=80$, $\\sigma=5$, $n=100$. Construct a 95% confidence interval for the population mean $\\mu$.

This is the template z-interval when $\\sigma$ is known. The standard error $\\sigma/\\sqrt{n}$ converts the raw sample mean into units of \"how many SEs from $\\mu$.\" With $n=100$, the SE is small, so the interval will be tight. Israeli exams often give all three numbers and expect you to identify $z_{0.025}=1.96$ without a table.

### Move 1: Identify $\\alpha$ and the critical value
For a 95% CI, $\\alpha=0.05$ and we need the two-tailed critical value $z_{\\alpha/2}=z_{0.025}=1.96$.

### Move 2: Compute the margin of error
$$E = z_{\\alpha/2}\\cdot\\frac{\\sigma}{\\sqrt{n}} = 1.96\\cdot\\frac{5}{\\sqrt{100}} = 1.96\\cdot\\frac{5}{10} = 1.96\\cdot 0.5 = 0.98.$$

### Move 3: Form the interval
$$\\bar{x}\\pm E = 80\\pm 0.98 = (79.02,\\ 80.98).$$

**Interpretation:** We are 95% confident that the true population mean $\\mu$ lies between 79.02 and 80.98. Equivalently: if we drew many samples of size 100 and built a 95% CI each time, about 95% of those intervals would contain the true $\\mu$.

**Sanity check:** The interval is centred at $\\bar{x}=80$ and has width $2(0.98)=1.96$, which is reasonable given $\\sigma=5$ and $n=100$. If asked for MOE instead of width, report $E=0.98$."""

WE1_HE = """**נתון:** $\\bar{x}=80$, $\\sigma=5$, $n=100$. בנו רווח סמך 95% לממוצע האוכלוסייה $\\mu$.

זה תבנית רווח z כש-$\\sigma$ ידוע. שגיאת התקן $\\sigma/\\sqrt{n}$ ממירה את ממוצע המדגם ל\"כמה SE מ-$\\mu$.\" עם $n=100$, ה-SE קטן ולכן הרווח צר. בבחינות ישראליות לעיתים נותנים את שלושת המספרים ומצפים שתזהו $z_{0.025}=1.96$ ללא טבלה.

### צעד 1: זיהוי $\\alpha$ והערך הקריטי
ל-CI 95%, $\\alpha=0.05$ וצריך $z_{\\alpha/2}=z_{0.025}=1.96$.

### צעד 2: חישוב שגיאת השוליים
$$E = 1.96\\cdot\\frac{5}{\\sqrt{100}} = 1.96\\cdot 0.5 = 0.98.$$

### צעד 3: בניית הרווח
$$80\\pm 0.98 = (79.02,\\ 80.98).$$

**פירוש:** אנו ב-95% סמך ש-$\\mu$ האמיתי נמצא בין 79.02 ל-80.98. שקיל: אם ניקח מדגמים רבים בגודל 100 ונבנה CI 95% בכל פעם, כ-95% מהרווחים יכילו את $\\mu$.

**בדיקת הגיון:** הרווח ממורכז ב-$\\bar{x}=80$ ורוחבו $1.96$, סביר ל-$\\sigma=5$ ו-$n=100$. אם מבקשים MOE ולא רוחב, דווחו $E=0.98$."""

WE2_EN = """**Given:** A survey yields $\\hat{p}=0.6$ with $n=400$. Find a 95% confidence interval for the true population proportion $p$.

Proportion CIs use the Normal approximation to the binomial. First verify the validity conditions, then compute the standard error of $\\hat{p}$. Poll and survey questions on Israeli exams almost always include a validity check — write it explicitly for partial credit.

### Move 1: Check validity and compute SE
$\\hat{p}=360/600$ is already given as 0.6. Check: $n\\hat{p}=240\\geq 5$ and $n(1-\\hat{p})=160\\geq 5$ — the Normal approximation is valid.
$$\\text{SE}(\\hat{p}) = \\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}} = \\sqrt{\\frac{0.6\\cdot 0.4}{400}} = \\sqrt{0.0006} \\approx 0.02449.$$

### Move 2: Margin of error
$$E = z_{0.025}\\cdot \\text{SE} = 1.96\\cdot 0.02449 \\approx 0.048.$$

### Move 3: Interval
$$0.6\\pm 0.048 = (0.552,\\ 0.648).$$

**Interpretation:** We are 95% confident the true support proportion lies between 55.2% and 64.8%. To test a claim such as $p=0.5$, check whether 0.5 falls inside — here it does not, so the data are inconsistent with $p=0.5$ at the 5% level (CI–test duality). Always state the interval in the same units as $\\hat{p}$ (proportions, not counts)."""

WE2_HE = """**נתון:** סקר נותן $\\hat{p}=0.6$ עם $n=400$. מצאו CI 95% לפרופורציה האמיתית $p$.

רווחי פרופורציה משתמשים בקירוב נורמלי לבינומי. קודם בדקו תנאי תקפות, ואז חשבו SE של $\\hat{p}$. שאלות סקר בבחינות ישראליות כוללות כמעט תמיד בדיקת תקפות — כתבו אותה במפורש לניקוד חלקי.

### צעד 1: בדיקת תקפות וחישוב SE
בדיקה: $n\\hat{p}=240\\geq 5$ ו-$n(1-\\hat{p})=160\\geq 5$ — הקירוב תקף.
$$\\text{SE}(\\hat{p}) = \\sqrt{\\frac{0.6\\cdot 0.4}{400}} = \\sqrt{0.0006} \\approx 0.02449.$$

### צעד 2: שגיאת שוליים
$$E = 1.96\\cdot 0.02449 \\approx 0.048.$$

### צעד 3: הרווח
$$0.6\\pm 0.048 = (0.552,\\ 0.648).$$

**פירוש:** אנו ב-95% סמך שהפרופורציה האמיתית בין 55.2% ל-64.8%. לבדיקת טענה $p=0.5$, בדקו האם 0.5 בפנים — כאן לא, ולכן הנתונים אינם עקביים עם $p=0.5$ ברמה 5% (דואליות CI–מבחן). הציגו את הרווח באותן יחידות כמו $\\hat{p}$ (פרופורציות, לא ספירות)."""

WE3_EN = """**Problem:** How large must $n$ be so that a 99% CI for a proportion has margin of error $\\leq 0.03$, regardless of the true $p$?

When $p$ is unknown before sampling, use the **conservative** bound $p(1-p)\\leq 1/4$ (maximum at $p=1/2$). This guarantees the sample is large enough for any possible true proportion — a common exam setup when planning a survey before fieldwork begins.

### Move 1: Critical value for 99% CI
$z_{\\alpha/2}=z_{0.005}=2.576$.

### Move 2: Worst-case MOE bound
$$E = z_{\\alpha/2}\\sqrt{\\frac{p(1-p)}{n}} \\leq z_{\\alpha/2}\\cdot\\frac{1}{2\\sqrt{n}}.$$

### Move 3: Solve for $n$
$$\\frac{2.576}{2\\sqrt{n}} \\leq 0.03 \\quad\\Rightarrow\\quad \\sqrt{n} \\geq \\frac{2.576}{0.06} = 42.93 \\quad\\Rightarrow\\quad n \\geq 42.93^2 = 1843.0.$$

### Move 4: Round up
$n = 1844$ (fractional observations are impossible).

**Interpretation:** At least 1,844 respondents guarantee MOE $\\leq 0.03$ at 99% confidence for any true proportion. If prior data suggest $\\hat{p}\\approx 0.1$, a non-conservative formula could yield a smaller $n$, but exams usually ask for the worst-case bound. Verify by plugging back: $E=2.576/(2\\sqrt{1844})\\approx 0.030$."""

WE3_HE = """**בעיה:** כמה גדול $n$ כדי ש-CI 99% לפרופורציה יהיה עם שגיאת שוליים $\\leq 0.03$, ללא תלות ב-$p$ האמיתי?

כש-$p$ לא ידוע לפני הדגימה, השתמשו בגבול **שמרני** $p(1-p)\\leq 1/4$ (מקסימום ב-$p=1/2$). זה מבטיח שהמדגם מספיק גדול לכל פרופורציה אפשרית — תרחיש בחינה נפוץ בתכנון סקר לפני איסוף שדה.

### צעד 1: ערך קריטי ל-CI 99%
$z_{0.005}=2.576$.

### צעד 2: גבול MOE במקרה הגרוע
$$E \\leq z_{\\alpha/2}\\cdot\\frac{1}{2\\sqrt{n}}.$$

### צעד 3: פתרון ל-$n$
$$\\sqrt{n} \\geq \\frac{2.576}{0.06} = 42.93 \\quad\\Rightarrow\\quad n \\geq 1843.0.$$

### צעד 4: עיגול למעלה
$n = 1844$.

**פירוש:** לפחות 1,844 משיבים מבטיחים MOE $\\leq 0.03$ ב-99% סמך לכל פרופורציה. אם נתונים קודמים מרמזים $\\hat{p}\\approx 0.1$, נוסחה לא-שמרנית יכולה לתת $n$ קטן יותר, אך בבחינות בדרך כלל מבקשים גבול מקרה גרוע. אימות: $E=2.576/(2\\sqrt{1844})\\approx 0.030$."""

CKPT1_EN = """Using the same setup as Example 1 ($\\bar{x}=80$, $\\sigma=5$, $n=100$), build a **99%** CI and compare it to the 95% CI.

**Step 1:** For 99% confidence, $\\alpha=0.01$ and $z_{\\alpha/2}=z_{0.005}=2.576$.

**Step 2:** Margin of error (SE unchanged at $5/10=0.5$):
$$E = 2.576\\cdot 0.5 = 1.288.$$

**Step 3:** Interval:
$$80\\pm 1.288 = (78.712,\\ 81.288) \\approx (78.71,\\ 81.29).$$

**Comparison:** The 99% CI $(78.71, 81.29)$ is **wider** than the 95% CI $(79.02, 80.98)$. Higher confidence demands a wider net — you trade precision for certainty. Width increased from $1.96$ to $2.576$, a factor of $2.576/1.96\\approx 1.31$."""

CKPT1_HE = """עם אותם נתונים מדוגמה 1 ($\\bar{x}=80$, $\\sigma=5$, $n=100$), בנו **CI 99%** והשוו ל-CI 95%.

**שלב 1:** ל-99% סמך, $\\alpha=0.01$ ו-$z_{0.005}=2.576$.

**שלב 2:** שגיאת שוליים (SE נשאר $0.5$):
$$E = 2.576\\cdot 0.5 = 1.288.$$

**שלב 3:** הרווח:
$$80\\pm 1.288 = (78.71,\\ 81.29).$$

**השוואה:** CI 99% **רחב יותר** מ-CI 95% $(79.02, 80.98)$. סמך גבוה יותר דורש רשת רחבה יותר — מחליפים דיוק בוודאות. הרוחב גדל פי $2.576/1.96\\approx 1.31$."""

CKPT2_EN = """In a sample of $n=100$, $\\hat{p}=0.3$. Build a **90%** CI for $p$.

**Step 1:** Validity: $n\\hat{p}=30\\geq 5$ and $n(1-\\hat{p})=70\\geq 5$. OK.

**Step 2:** Standard error:
$$\\text{SE} = \\sqrt{\\frac{0.3\\cdot 0.7}{100}} = \\sqrt{0.0021} \\approx 0.0458.$$

**Step 3:** For 90% CI, $z_{0.05}=1.645$:
$$E = 1.645\\cdot 0.0458 \\approx 0.0754.$$

**Step 4:** Interval:
$$0.3\\pm 0.075 = (0.225,\\ 0.375).$$

**Note:** A 90% CI is narrower than 95% because we accept a 10% failure rate for the coverage procedure instead of 5%."""

CKPT2_HE = """במדגם $n=100$, $\\hat{p}=0.3$. בנו **CI 90%** ל-$p$.

**שלב 1:** תקפות: $n\\hat{p}=30\\geq 5$ ו-$n(1-\\hat{p})=70\\geq 5$. תקין.

**שלב 2:** שגיאת תקן:
$$\\text{SE} = \\sqrt{0.0021} \\approx 0.0458.$$

**שלב 3:** ל-CI 90%, $z_{0.05}=1.645$:
$$E = 1.645\\cdot 0.0458 \\approx 0.075.$$

**שלב 4:** הרווח:
$$0.3\\pm 0.075 = (0.225,\\ 0.375).$$

**הערה:** CI 90% צר יותר מ-95% כי מקבלים 10% כשלון בהליך הכיסוי במקום 5%."""

METHOD_EN = """| Parameter | $\\sigma$ | Formula | When valid |
|---|---|---|---|
| Mean $\\mu$ | Known | $\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$ | Normal population or large $n$ |
| Mean $\\mu$ | Unknown | $\\bar{x}\\pm t_{\\alpha/2,n-1}\\,s/\\sqrt{n}$ | Normal population (any $n$) or large $n$ |
| Proportion $p$ | — | $\\hat{p}\\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$ | $n\\hat{p}\\geq 5$, $n(1-\\hat{p})\\geq 5$ |

**5-step CI procedure:**
1. Identify parameter ($\\mu$ or $p$) and whether $\\sigma$ is known.
2. Choose confidence level $(1-\\alpha)$ and look up $z_{\\alpha/2}$ or $t_{\\alpha/2,df}$.
3. Compute standard error and margin of error $E$.
4. Form $\\text{estimate}\\pm E$.
5. State interpretation **in context** — never say \"probability the parameter is in the interval.\"

**Sample size shortcuts:**
- Mean: $n\\geq(z_{\\alpha/2}\\sigma/E_0)^2$, round up.
- Proportion (conservative): $n\\geq(z_{\\alpha/2}/(2E_0))^2$, round up.

**Decision shortcut:** To test $H_0:\\mu=\\mu_0$ or $p=p_0$, check if the hypothesised value lies inside the $(1-\\alpha)$ CI — outside means reject at level $\\alpha$."""

METHOD_HE = """| פרמטר | $\\sigma$ | נוסחה | מתי תקפה |
|---|---|---|---|
| ממוצע $\\mu$ | ידוע | $\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$ | אוכלוסייה נורמלית או $n$ גדול |
| ממוצע $\\mu$ | לא ידוע | $\\bar{x}\\pm t_{\\alpha/2,n-1}\\,s/\\sqrt{n}$ | נורמלית (כל $n$) או $n$ גדול |
| פרופורציה $p$ | — | $\\hat{p}\\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$ | $n\\hat{p}\\geq 5$, $n(1-\\hat{p})\\geq 5$ |

**5 שלבי בניית CI:**
1. זיהוי פרמטר ($\\mu$ או $p$) והאם $\\sigma$ ידוע.
2. בחירת רמת סמך $(1-\\alpha)$ וחיפוש $z_{\\alpha/2}$ או $t_{\\alpha/2,df}$.
3. חישוב SE ושגיאת שוליים $E$.
4. בניית $\\text{הערכה}\\pm E$.
5. ניסוח פרשנות **בהקשר** — לעולם אל תגידו \"הסתברות שהפרמטר ברווח.\"

**קיצורי גודל מדגם:**
- ממוצע: $n\\geq(z_{\\alpha/2}\\sigma/E_0)^2$, עיגול למעלה.
- פרופורציה (שמרני): $n\\geq(z_{\\alpha/2}/(2E_0))^2$, עיגול למעלה.

**קיצור החלטה:** לבדיקת $H_0:\\mu=\\mu_0$ או $p=p_0$, בדקו האם הערך ההשערתי בתוך CI ברמת $(1-\\alpha)$ — מחוץ = דחייה ברמת $\\alpha$."""

PITFALL_EN = """1. **Wrong interpretation.** A 95% CI does **not** mean \"there is a 95% probability that $\\mu$ lies in $(a,b)$.\" The parameter is fixed; the interval is random. Say instead: \"We are 95% confident the procedure captures $\\mu$.\"

2. **Forgetting to round up** sample size. If $n\\geq 96.04$, report $n=97$, not 96. Fractional sample sizes are impossible.

3. **Using z instead of t** when $\\sigma$ is unknown and $n$ is small. The t-distribution has heavier tails, giving a wider (more honest) interval.

4. **Confusing width and margin of error.** Width $=2E$. If the exam asks for MOE, give $E$; if it asks for width, give $2E$.

5. **Using the CI to \"accept\" $H_0$.** A CI containing $\\mu_0$ means only that you fail to reject — not that $\\mu_0$ is proven true.

6. **Skipping validity checks** for proportion CIs. When $n\\hat{p}<5$, the Normal approximation fails and the formula is unreliable."""

PITFALL_HE = """1. **פרשנות שגויה.** CI 95% **אינו** אומר \"יש הסתברות 95% ש-$\\mu$ ב-$(a,b)$.\" הפרמטר קבוע; הרווח אקראי. אמרו: \"אנו ב-95% סמך שההליך תופס את $\\mu$.\"

2. **שכחה לעגל למעלה** בגודל מדגם. אם $n\\geq 96.04$, דווחו $n=97$, לא 96.

3. **שימוש ב-z במקום t** כש-$\\sigma$ לא ידוע ו-$n$ קטן. t עם זנבות כבדים יותר נותן רווח רחב (כנה) יותר.

4. **בלבול רוחב ושגיאת שוליים.** רוחב $=2E$. MOE = $E$; רוחב = $2E$.

5. **\"קבלת\" $H_0$ דרך CI.** CI שמכיל $\\mu_0$ רק אומר שאין לדחות — לא ש-$\\mu_0$ מוכח.

6. **דילוג על בדיקת תקפות** ל-CI פרופורציה. כש-$n\\hat{p}<5$, הקירוב הנורמלי נכשל."""

WHY_EN = """Confidence intervals appear everywhere real decisions are made under uncertainty — election polling, clinical trials, quality control, and A/B testing. A news headline \"support at 52% ± 3%\" is a CI in disguise.

**Exam relevance:** Israeli university statistics finals (TAU, Technion, HUJI) routinely ask you to compute CIs for means and proportions, interpret them correctly (avoid the Bayesian misread), derive sample-size formulas, and prove coverage probability equals $1-\\alpha$. The CI–test link from `concept:hypothesis_testing` lets you answer \"is this claim consistent with the data?\" without a full hypothesis test.

**Cross-subject link:** In physics labs you report measurements as $\\bar{x}\\pm\\text{uncertainty}$ — the same logic as $\\bar{x}\\pm z\\sigma/\\sqrt{n}$. In data science, bootstrap CIs generalize the formulas here when distributions are non-Normal."""

WHY_HE = """רווחי סמך מופיעים בכל מקום שמקבלים החלטות תחת אי-ודאות — סקרי בחירות, ניסויים קליניים, בקרת איכות, ו-A/B testing. כותרת \"52% ± 3%\" היא CI בפירוש.

**רלוונטיות לבחינה:** בחינות סופיות בסטטיסטיקה (TAU, טכניון, HUJI) מבקשות לחשב CI לממוצע ולפרופורציה, לפרש נכון (להימנע מפרשנות בייסיאנית), לגזור נוסחאות גודל מדגם, ולהוכיח כיסוי $1-\\alpha$. קשר CI–מבחן מ-`concept:hypothesis_testing` מאפשר לענות \"האם הטענה עקבית עם הנתונים?\" בלי מבחן מלא.

**קשר בין-מקצועי:** במעבדות פיזיקה מדווחים $\\bar{x}\\pm\\text{אי-ודאות}$ — אותה לוגיקה כמו $\\bar{x}\\pm z\\sigma/\\sqrt{n}$. ב-data science, bootstrap CI מכליל את הנוסחאות כשההתפלגות לא נורמלית."""

BEFORE_EN = """**Formula sheet essentials:**
- CI for $\\mu$ ($\\sigma$ known): $\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$
- CI for $\\mu$ ($\\sigma$ unknown): $\\bar{x}\\pm t_{\\alpha/2,n-1}\\,s/\\sqrt{n}$
- CI for $p$: $\\hat{p}\\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$
- Sample size (mean): $n\\geq(z_{\\alpha/2}\\sigma/E_0)^2$
- Sample size (proportion, conservative): $n\\geq(z_{\\alpha/2}/(2E_0))^2$
- $z_{0.025}=1.96$, $z_{0.005}=2.576$, $z_{0.05}=1.645$

**What Israeli exams emphasise:**
- Computing CIs and reading them in context (polls, manufacturing, medicine).
- Correct frequentist interpretation — never \"95% probability $\\mu$ is inside.\"
- Deriving sample-size formulas and rounding $n$ up.
- Proving coverage $P(\\mu\\in\\text{CI})=1-\\alpha$.
- CI–test duality for quick accept/reject decisions.

**Proof pattern:** Start from $P(-z_{\\alpha/2}\\leq Z\\leq z_{\\alpha/2})=1-\\alpha$, rearrange to isolate $\\mu$, then explain pre-data vs post-data randomness."""

BEFORE_HE = """**נוסחאות חיוניות:**
- CI לממוצע (σ ידוע): $\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$
- CI לממוצע (σ לא ידוע): $\\bar{x}\\pm t_{\\alpha/2,n-1}\\,s/\\sqrt{n}$
- CI לפרופורציה: $\\hat{p}\\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$
- גודל מדגם (ממוצע): $n\\geq(z_{\\alpha/2}\\sigma/E_0)^2$
- גודל מדגם (פרופורציה שמרני): $n\\geq(z_{\\alpha/2}/(2E_0))^2$
- $z_{0.025}=1.96$, $z_{0.005}=2.576$, $z_{0.05}=1.645$

**מה בחינות ישראליות מדגישות:**
- חישוב CI ופרשנות בהקשר (סקרים, ייצור, רפואה).
- פרשנות frequentist נכונה — לעולם לא \"95% הסתברות ש-$\\mu$ בפנים.\"
- גזירת נוסחאות גודל מדגם ועיגול $n$ למעלה.
- הוכחת כיסוי $P(\\mu\\in\\text{CI})=1-\\alpha$.
- דואליות CI–מבחן להחלטות מהירות.

**דפוס הוכחה:** התחילו מ-$P(-z_{\\alpha/2}\\leq Z\\leq z_{\\alpha/2})=1-\\alpha$, סדרו מחדש לבודד $\\mu$, והסבירו אקראיות לפני/אחרי הנתונים."""

SUMMARY_EN = """- A **$(1-\\alpha)$ confidence interval** gives a range of plausible parameter values; the **coverage probability** of the construction procedure is $1-\\alpha$.
- **Mean ($\\sigma$ known):** $\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$. **Unknown $\\sigma$:** use $t_{n-1}$ with $s$.
- **Proportion:** $\\hat{p}\\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$, valid when $n\\hat{p}$ and $n(1-\\hat{p})$ are both $\\geq 5$.
- **Width** $=2E$ decreases as $n$ increases ($\\propto 1/\\sqrt{n}$) or confidence level decreases.
- **Sample size:** $n\\geq(z_{\\alpha/2}\\sigma/E_0)^2$ for means; $n\\geq(z_{\\alpha/2}/(2E_0))^2$ conservative for proportions — always round up.
- **CI–test duality:** reject $H_0:\\mu=\\mu_0$ iff $\\mu_0$ lies outside the $(1-\\alpha)$ CI."""

SUMMARY_HE = """- **CI $(1-\\alpha)$** נותן טווח ערכים סבירים; **הסתברות כיסוי** של ההליך היא $1-\\alpha$.
- **ממוצע ($\\sigma$ ידוע):** $\\bar{x}\\pm z_{\\alpha/2}\\sigma/\\sqrt{n}$. **$\\sigma$ לא ידוע:** $t_{n-1}$ עם $s$.
- **פרופורציה:** $\\hat{p}\\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$, תקף כש-$n\\hat{p}$ ו-$n(1-\\hat{p})$ $\\geq 5$.
- **רוחב** $=2E$ קטן כש-$n$ גדל ($\\propto 1/\\sqrt{n}$) או רמת סמך יורדת.
- **גודל מדגם:** $n\\geq(z_{\\alpha/2}\\sigma/E_0)^2$ לממוצע; $n\\geq(z_{\\alpha/2}/(2E_0))^2$ שמרני לפרופורציה — תמיד עיגול למעלה.
- **דואליות CI–מבחן:** דחה $H_0:\\mu=\\mu_0$ אמ\"מ $\\mu_0$ מחוץ ל-CI ברמת $(1-\\alpha)$."""

Q_EXPL = [
    fmt_expl(
        "For a 90% CI, $z_{0.05}=1.645$. Standard error: $\\sigma/\\sqrt{n}=15/\\sqrt{225}=15/15=1$. Margin of error: $E=1.645\\cdot 1=1.645$. Interval: $120\\pm 1.645=(118.355,\\ 121.645)\\approx(118.36,\\ 121.64)$.",
        "When $\\sigma$ is known, follow the z-formula. First compute $SE=\\sigma/\\sqrt{n}$, then $E=z_{\\alpha/2}\\cdot SE$, then $\\bar{x}\\pm E$. For 90% CI use $z_{0.05}=1.645$, not 1.96.",
        "Using $z=1.96$ (95% value) for a 90% CI. Forgetting to divide $\\sigma$ by $\\sqrt{n}$. Reporting only one endpoint instead of the full interval.",
        "Write $SE$ first on scratch paper. Check that the interval is centred at $\\bar{x}$ and symmetric: lower + upper $= 2\\bar{x}$.",
        "ל-CI 90%, $z_{0.05}=1.645$. SE: $\\sigma/\\sqrt{n}=15/\\sqrt{225}=15/15=1$. $E=1.645\\cdot 1=1.645$. הרווח: $120\\pm 1.645=(118.36,\\ 121.64)$ — אנו ב-90% סמך ש-$\\mu$ האמיתי בין 118.36 ל-121.64.",
        "כש-$\\sigma$ ידוע, נוסחת z: קודם $SE=\\sigma/\\sqrt{n}$, אחר כך $E=z_{\\alpha/2}\\cdot SE$, ואז $\\bar{x}\\pm E$. ל-90% השתמשו ב-1.645, לא 1.96. זהו את רמת הסמך מהשאלה לפני שאתם מחפשים $z$ בטבלה.",
        "שימוש ב-1.96 (95%) ל-CI 90%. שכחה לחלק $\\sigma$ ב-$\\sqrt{n}$. דיווח על קצה אחד בלבד במקום הרווח המלא $(a,b)$.",
        "כתבו $SE$ קודם על טיוטה. ודאו שהרווח ממורכז ב-$\\bar{x}$ וסימטרי: תחתון + עליון $= 2\\bar{x}$. בבחינות ישראליות מצפים גם לפרשנות מילולית קצרה.",
    ),
    fmt_expl(
        "$\\hat{p}=360/600=0.6$. SE $=\\sqrt{0.6\\cdot 0.4/600}=\\sqrt{0.0004}=0.02$. $E=1.96\\cdot 0.02=0.039$. CI: $(0.561,\\ 0.639)$ — we are 95% confident true support is between 56.1% and 63.9%.",
        "Proportion CI: compute $\\hat{p}=x/n$ first, verify $n\\hat{p}\\geq 5$, then SE and $E$. The answer is in proportion units (0.561), not counts (360).",
        "Using $n=600$ inside the square root incorrectly. Using $\\hat{p}=360$ instead of 0.6. Forgetting validity check when $n\\hat{p}$ is borderline.",
        "Convert counts to $\\hat{p}$ before any formula. On poll questions, examiners often give raw counts — divide first.",
        "$\\hat{p}=360/600=0.6$. SE $=\\sqrt{0.6\\cdot 0.4/600}=0.02$. $E=1.96\\cdot 0.02=0.039$. CI: $(0.561,\\ 0.639)$ — ב-95% סמך התמיכה האמיתית בין 56.1% ל-63.9%. בדיקת תקפות: $n\\hat{p}=240\\geq 5$.",
        "CI פרופורציה: חשבו $\\hat{p}=x/n$ מהספירות, בדקו $n\\hat{p}\\geq 5$ ו-$n(1-\\hat{p})\\geq 5$, ואז SE ו-$E$. התשובה ביחידות פרופורציה (0.561), לא בספירות (360).",
        "שימוש שגוי ב-$n$ בשורש. $\\hat{p}=360$ במקום 0.6. דילוג על בדיקת תקפות כש-$n\\hat{p}$ קרוב ל-5.",
        "המרו ספירות ל-$\\hat{p}$ לפני הנוסחה. בבחינות נותנים לעיתים 360 מתוך 600 — חלקו קודם. כתבו את בדיקת התקפות לניקוד חלקי.",
    ),
    fmt_expl(
        "The CI is symmetric about the point estimate: $\\bar{x}=(47.1+52.9)/2=50$. Margin of error $E=(52.9-47.1)/2=2.9$. Equivalently, half the width.",
        "Reading backwards from a CI: midpoint = estimate, half-width = MOE. You do not need $\\sigma$ or $n$ for this question — pure algebra on the endpoints.",
        "Confusing width (5.8) with MOE (2.9). Computing $\\bar{x}=52.9-47.1=5.8$ by subtracting endpoints incorrectly.",
        "Memorise: $\\bar{x}=\\frac{\\text{lower}+\\text{upper}}{2}$ and $E=\\frac{\\text{upper}-\\text{lower}}{2}$. These reverse-engineering questions appear on every exam.",
        "$\\bar{x}=(47.1+52.9)/2=50$. $E=(52.9-47.1)/2=2.9$ — שווה לחצי הרוחב 5.8. לא צריך $\\sigma$ או $n$; זו אלגebra על קצוות הרווח בלבד.",
        "קריאה לאחור מ-CI: אמצע = הערכה, חצי רוחב = MOE. שאלה \"הפוכה\" נפוצה בבחינות — נותנים רק קצוות (47.1, 52.9) בלי נתוני דגימה.",
        "בלבול רוחב (5.8) עם MOE (2.9). $\\bar{x}=52.9-47.1=5.8$ בחיסור שגוי. דיווח על רוחב כשמבקשים MOE בלבד.",
        "שיננו: $\\bar{x}=\\frac{\\text{תחתון}+\\text{עליון}}{2}$, $E=\\frac{\\text{עליון}-\\text{תחתון}}{2}$. שאלות הפוכות בכל בחינה — אין צורך בנוסחת CI מלאה.",
    ),
    fmt_expl(
        "Width $W=2z_{\\alpha/2}\\sigma/\\sqrt{n}$. Here: $W=2\\cdot 1.96\\cdot 20/\\sqrt{100}=2\\cdot 1.96\\cdot 2=2\\cdot 3.92=7.84$. Note $\\sqrt{100}=10$, so $\\sigma/\\sqrt{n}=20/10=2$.",
        "When asked for **width**, use $2E$ or the one-line formula $2z\\sigma/\\sqrt{n}$. When asked for MOE, use half of that. Always identify which the question wants before calculating.",
        "Answering 3.92 (the MOE) instead of 7.84 (width). Using $\\sigma=20$ without dividing by $\\sqrt{n}=10$.",
        "Underline \"width\" vs \"margin of error\" in the stem. If only $\\sigma$ and $n$ are given with no $\\bar{x}$, you likely need width, not a centred interval.",
        "רוחב $W=2\\cdot 1.96\\cdot 20/\\sqrt{100}=7.84$. $\\sqrt{100}=10$, אז $\\sigma/\\sqrt{n}=2$. MOE היה 3.92 — חצי מהרוחב, לא התשובה המבוקשת.",
        "כשמבקשים **רוחב**, $2E$ או $2z\\sigma/\\sqrt{n}$. MOE = חצי. סמנו במחברת \"רוחב\" מול \"שגיאת שוליים\" לפני החישוב — טעות נפוצה בבחינות.",
        "תשובה 3.92 (MOE) במקום 7.84 (רוחב). $\\sigma=20$ במכנה בלי $\\sqrt{n}=10$. שימוש ב-z=2.576 (99%) במקום 1.96 (95%).",
        "סמנו \"רוחב\" מול \"שגיאת שוליים\" בשאלה. אם ניתנו רק $\\sigma$ ו-$n$ בלי $\\bar{x}$, כנראה מבקשים רוחב. בדקו: רוחב = 2 כפול MOE.",
    ),
    fmt_expl(
        "$\\sigma$ unknown with small $n$ from a normal population → **t-interval**. $SE=s/\\sqrt{n}=8/4=2$. $E=t_{0.025,15}\\cdot 2=2.131\\cdot 2=4.262$. CI: $(34-4.262,\\ 34+4.262)=(29.74,\\ 38.26)$.",
        "Decision tree: $\\sigma$ known → z; $\\sigma$ unknown → t with $df=n-1$. Here $n=16$, $df=15$, and the exam gives $t_{0.025,15}=2.131$ — use it, not 1.96.",
        "Using z=1.96 when $\\sigma$ is unknown. Using $s=8$ as the full denominator instead of $SE=2$. Wrong degrees of freedom ($df=n$ instead of $n-1$).",
        "For $n<30$ with unknown $\\sigma$, always t. Write $df=n-1$ on your paper before looking up the critical value.",
        "$\\sigma$ לא ידוע, $n=16$ קטן, אוכלוסייה נורמלית → **t**. $SE=s/\\sqrt{n}=8/4=2$. $E=t_{0.025,15}\\cdot 2=2.131\\cdot 2=4.262$. CI: $(29.74,\\ 38.26)$.",
        "עץ החלטה: $\\sigma$ ידוע → z; לא ידוע → t עם $df=n-1$. כאן $df=15$ ו-$t_{0.025,15}=2.131$ מהשאלה — השתמשו בו, לא 1.96. t נותן רווח רחב יותר (כנה יותר).",
        "z=1.96 כש-$\\sigma$ לא ידוע ו-$n$ קטן. $s=8$ במכנה במקום SE=2. $df=n$ במקום $n-1$. שכחה ש-$\\sqrt{16}=4$.",
        "ל-$n<30$ עם $\\sigma$ לא ידוע, תמיד t. כתבו $df=n-1$ לפני חיפוש ערך קריטי. הבחינה לעיתים נותנת $t$ ישירות — השוו $|T|$ אליו.",
    ),
    fmt_expl(
        "Width $\\leq 4$ means MOE $E\\leq 2$. From $E=z_{\\alpha/2}\\sigma/\\sqrt{n}\\leq 2$: $n\\geq(1.96\\cdot 10/2)^2=(9.8)^2=96.04$. Round **up**: $n=97$.",
        "Sample-size problems: translate words to an inequality on $E$ or width first. \"Width at most 4\" → $2E\\leq 4$ → $E\\leq 2$. Then solve for $n$ and round up — never round down.",
        "Using width=4 directly in the formula without halving to get $E$. Rounding 96.04 down to 96. Using $z=2.576$ (99%) instead of 1.96 (95%).",
        "After computing $n$, verify: plug $n=97$ back and confirm width $\\leq 4$. One-line check catches rounding errors.",
        "רוחב $\\leq 4$ ⇒ MOE $E\\leq 2$. מ-$E=z_{\\alpha/2}\\sigma/\\sqrt{n}\\leq 2$: $n\\geq(1.96\\cdot 10/2)^2=96.04$. עיגול **למעלה**: $n=97$, לא 96.",
        "גודל מדגם: תרגמו \"רוחב מקסימלי 4\" ל-$E\\leq 2$. פתרו $n\\geq(z\\sigma/E_0)^2$ ועגלו **למעלה** — מדגם חלקי בלתי אפשרי. בדקו בחזרה עם $n=97$.",
        "שימוש ברוחב=4 ישירות בלי $E\\leq 2$. עיגול 96.04 ל-96 (למטה). $z=2.576$ (99%) במקום 1.96 (95%).",
        "אחרי $n=97$, הכניסו בחזרה: $E=1.96\\cdot 10/\\sqrt{97}\\approx 1.99\\leq 2$ ✓. בדיקה חוזרת תופסת טעויות עיגול — כתבו אותה בבחינה.",
    ),
    fmt_expl(
        "SE $=\\sqrt{0.45\\cdot 0.55/500}=0.02225$. $E=1.96\\cdot 0.02225=0.044$. CI: $(0.406,\\ 0.494)$. Since $0.5\\notin(0.406,\\ 0.494)$, the claim $p=0.5$ is **inconsistent** with the data at the 5% level (CI–test duality).",
        "This is a CI–test duality question. Build the CI first, then check whether the claimed value falls inside. Inside → consistent (fail to reject); outside → inconsistent (reject).",
        "Saying \"consistent\" because 0.45 is close to 0.5 without checking the CI. Using $\\hat{p}=0.5$ in the SE formula instead of the observed 0.45.",
        "For \"is the claim consistent?\" questions, always compute the CI — proximity of $\\hat{p}$ to the claim is not enough. The CI width matters.",
        "SE $=\\sqrt{0.45\\cdot 0.55/500}=0.02225$. $E=1.96\\cdot 0.02225=0.044$. CI: $(0.406,\\ 0.494)$. $0.5\\notin$ CI — טענה $p=0.5$ **אינה עקבית** ברמה 5% (דואליות CI–מבחן).",
        "שאלת דואליות: בנו CI 95%, בדקו האם הערך הנטען ($p=0.5$) בפנים. בפנים → עקבי (אין לדחות); מחוץ → לא עקבי (דוחים). קרבה של $\\hat{p}$ לטענה לא מספיקה.",
        "\"עקבי\" כי 0.45 קרוב ל-0.5 בלי לחשב CI. $\\hat{p}=0.5$ ב-SE במקום 0.45 הנצפה. אמרה \"מוכיח $p\\neq 0.5$\" במקום \"אינו עקבי ברמה 5%\".",
        "ב\"האם עקבי?\" — תמיד חשבו CI מלא. רוחב הרווח קובע, לא רק $\\hat{p}$. זו דואליות ישירה עם מבחן z לפרופורציה — אותה מסקנה.",
    ),
    fmt_expl(
        "CI width $W=2z_{\\alpha/2}\\sigma/\\sqrt{n}$, so $W\\propto 1/\\sqrt{n}$. Doubling $n$ gives new width $W'=W/\\sqrt{2}\\approx 0.707\\,W$ — about 70.7% of the original, **not** half.",
        "Precision improves slowly with sample size because of the square root. To cut width in half, you need **four times** as many observations ($n\\to 4n$), not double.",
        "Answering that width halves when $n$ doubles (confusing with variance, which scales as $1/n$). Saying width stays the same because confidence level is unchanged.",
        "Memorise the $\\sqrt{n}$ rule: double $n$ → divide width by $\\sqrt{2}$; quadruple $n$ → halve width. Conceptual questions on this appear without numbers.",
        "רוחב $W=2z\\sigma/\\sqrt{n}$, לכן $W\\propto 1/\\sqrt{n}$. הכפלת $n$ פי 2: $W'=W/\\sqrt{2}\\approx 0.707\\,W$ — כ-70.7% מהמקורי, **לא** חצי. רמת הסמך לא משתנה.",
        "דיוק משתפר לאט עם $n$ בגלל השורש. לחציית רוחב צריך **פי 4** תצפיות ($n\\to 4n$), לא הכפלה פי 2. זו שאלה מושגית — הבינו את $\\sqrt{n}$ בלי מספרים.",
        "תשובה \"רוחב חצי\" כש-$n$ מוכפל (בלבול עם שונות שמתקטנת כ-1/n). \"רוחב לא משתנה\" כי רמת סמך קבועה — $n$ כן משפיע.",
        "שיננו כלל $\\sqrt{n}$: $n$ כפול → רוחב ב-$\\sqrt{2}$; $n$ פי 4 → רוחב חצי. שאלות מושגיות בלי מספרים מופיעות בבגרות 5 יחידות ובאוניברסיטה.",
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
