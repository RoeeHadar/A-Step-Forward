#!/usr/bin/env python3
"""Expand sampling_estimation.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/sampling_estimation.json"

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


INTRO_EN = """We rarely observe an entire population. Instead we draw a **random sample** and use it to learn about unknown parameters such as the mean $\\mu$, variance $\\sigma^2$, proportion $p$, or Poisson rate $\\lambda$. **Point estimation** is the process of choosing a single number — an **estimator** $T=g(X_1,\\ldots,X_n)$ — as our best guess for $\\theta$.

But not all estimators are equal. We judge them by **unbiasedness** ($E[T]=\\theta$), **consistency** ($T_n\\to\\theta$ as $n\\to\\infty$), **efficiency** (smallest variance among unbiased estimators), and **mean squared error** $\\text{MSE}=\\text{Var}+\\text{Bias}^2$. The **maximum likelihood estimator (MLE)** provides a systematic recipe: choose $\\hat{\\theta}$ that makes the observed data most probable.

This lesson is the foundation of statistical inference. Everything that follows — confidence intervals in `concept:confidence_intervals`, hypothesis tests in `concept:hypothesis_testing`, and regression — assumes you can derive and evaluate estimators. Israeli university exams routinely ask you to compute MLEs for binomial and Poisson models, verify unbiasedness, and compare estimators via MSE."""

INTRO_HE = """לעיתים נדירות אנחנו צופים באוכלוסייה שלמה. במקום זאת אנו לוקחים **מדגם אקראי** ומשתמשים בו כדי ללמוד על פרמטרים לא ידועים כמו ממוצע $\\mu$, שונות $\\sigma^2$, פרופורציה $p$, או קצב פואסון $\\lambda$. **אומדן נקודתי** הוא תהליך של בחירת מספר בודד — **אומד** $T=g(X_1,\\ldots,X_n)$ — כניחוש הטוב ביותר שלנו ל-$\\theta$.

אך לא כל האומדים שווים. שופטים אותם לפי **חסרי הטיה** ($E[T]=\\theta$), **עקביות** ($T_n\\to\\theta$ כש-$n\\to\\infty$), **יעילות** (שונות מינימלית בין אומדים חסרי הטיה), ו-**שגיאת ריבוע ממוצעת** $\\text{MSE}=\\text{Var}+\\text{Bias}^2$. **אומד הנראות המרבית (MLE)** מספק מתכון שיטתי: בחרו $\\hat{\\theta}$ שהופך את הנתונים הנצפים לסבירים ביותר.

שיעור זה הוא יסוד ההסקה הסטטיסטית. כל מה שבא אחריו — רווחי סמך ב-`concept:confidence_intervals`, בדיקות השערות ב-`concept:hypothesis_testing`, ורגרסיה — מניח שאתם יודעים לגזור ולהעריך אומדים. בבחינות אוניברסיטאיות ישראליות מבקשים לעיתים קרובות לחשב MLE למודלים בינומיים ופואסוניים, לאמת חסרי הטיה, ולהשוות אומדים דרך MSE."""

DEF_EN = """**Estimator:** A function of sample data $T=g(X_1,\\ldots,X_n)$ used to estimate an unknown parameter $\\theta$. The **realised value** $t=g(x_1,\\ldots,x_n)$ is called an **estimate**.

**Unbiasedness:** $T$ is **unbiased** if $E[T]=\\theta$ for all $\\theta$. The sample mean $\\bar{X}=\\frac{1}{n}\\sum X_i$ is unbiased for $\\mu$; the sample proportion $\\hat{p}=X/n$ is unbiased for $p$.

**Bias:** $\\text{Bias}(T)=E[T]-\\theta$. Unbiased $\\Leftrightarrow$ Bias $=0$. A small bias is acceptable if variance drops enough to lower MSE.

**Consistency:** $T_n$ is **consistent** if $T_n\\xrightarrow{P}\\theta$ as $n\\to\\infty$ (convergence in probability). Intuition: with enough data, the estimator concentrates near the truth.

**Efficiency:** Among unbiased estimators of $\\theta$, the one with **smallest variance** is most efficient. The **Cramér–Rao lower bound** gives the minimum achievable variance for unbiased estimators under regularity conditions.

**Mean Squared Error (MSE):** $\\text{MSE}(T)=E[(T-\\theta)^2]=\\text{Var}(T)+[\\text{Bias}(T)]^2$. Lower MSE is the practical criterion for comparing estimators.

**Maximum Likelihood Estimator (MLE):** $\\hat{\\theta}_{\\text{MLE}}=\\arg\\max_\\theta L(\\theta)$ where $L(\\theta)=\\prod_{i=1}^n f(x_i;\\theta)$ is the **likelihood**. Equivalently maximise the **log-likelihood** $\\ell(\\theta)=\\ln L(\\theta)$ — sums replace products and calculus becomes tractable."""

DEF_HE = """**אומד:** פונקציה של נתוני מדגם $T=g(X_1,\\ldots,X_n)$ לאמידת פרמטר לא ידוע $\\theta$. **הערך הממומש** $t=g(x_1,\\ldots,x_n)$ נקרא **הערכה**.

**חסרי הטיה:** $T$ **חסר הטיה** אם $E[T]=\\theta$ לכל $\\theta$. ממוצע המדגם $\\bar{X}=\\frac{1}{n}\\sum X_i$ חסר הטיה ל-$\\mu$; שיעור המדגם $\\hat{p}=X/n$ חסר הטיה ל-$p$.

**הטיה:** $\\text{Bias}(T)=E[T]-\\theta$. חסר הטיה $\\Leftrightarrow$ הטיה $=0$. הטיה קטנה מקובלת אם השונות יורדת מספיק כדי להקטין MSE.

**עקביות:** $T_n$ **עקבי** אם $T_n\\xrightarrow{P}\\theta$ כש-$n\\to\\infty$ (התכנסות בהסתברות). אינטואיציה: עם מספיק נתונים, האומד מתרכז ליד האמת.

**יעילות:** בין אומדים חסרי הטיה של $\\theta$, זה עם **השונות הקטנה ביותר** הוא היעיל ביותר. **גבול קרמר-רao** נותן שונות מינימלית אפשרית לאומדים חסרי הטיה בתנאי סדירות.

**שגיאת ריבוע ממוצעת (MSE):** $\\text{MSE}(T)=E[(T-\\theta)^2]=\\text{Var}(T)+[\\text{Bias}(T)]^2$. MSE נמוך יותר הוא הקריטריון המעשי להשוואת אומדים.

**MLE:** $\\hat{\\theta}_{\\text{MLE}}=\\arg\\max_\\theta L(\\theta)$ כאשר $L(\\theta)=\\prod_{i=1}^n f(x_i;\\theta)$ היא **הנראות**. שקיל: מקסימום **לוג-נראות** $\\ell(\\theta)=\\ln L(\\theta)$ — סכומים מחליפים מכפלות והחשבון נהיה נוח."""

THEORY_EN = """**MLE large-sample properties:** Under regularity conditions, MLEs are (i) **consistent**, (ii) **asymptotically unbiased**, (iii) **asymptotically efficient** (achieve the Cramér–Rao bound), and (iv) **invariant** under reparameterisation (if $\\hat{\\theta}$ is MLE of $\\theta$, then $g(\\hat{\\theta})$ is MLE of $g(\\theta)$).

**Four-step MLE recipe:**
1. Write the PMF/PDF $f(x_i;\\theta)$ for each observation.
2. Form likelihood $L(\\theta)=\\prod_i f(x_i;\\theta)$ and log-likelihood $\\ell(\\theta)=\\sum_i \\ln f(x_i;\\theta)$.
3. Differentiate: $\\ell'(\\theta)=0$ and solve for $\\hat{\\theta}$.
4. Verify a maximum: $\\ell''(\\hat{\\theta})<0$ (or check boundary behaviour for constrained parameters).

**Standard estimators (memorise):**
| Parameter | Model | MLE | Unbiased? |
|---|---|---|---|
| $\\mu$ | Normal | $\\bar{X}$ | Yes |
| $\\sigma^2$ | Normal | $\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ | No (biased low) |
| $p$ | Binomial | $k/n$ | Yes |
| $\\lambda$ | Poisson | $\\bar{X}$ | Yes |

**Sample variance note:** The **unbiased** estimator $S^2=\\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ uses divisor $n-1$ (Bessel's correction) because $\\bar{X}$ is estimated from the same data, consuming one degree of freedom. The MLE divides by $n$ and is biased downward.

**Comparing estimators:** When two estimators compete, compute MSE $=\\text{Var}+\\text{Bias}^2$. A biased estimator can beat an unbiased one if its variance is much smaller — the bias–variance tradeoff is central in modern statistics and machine learning."""

THEORY_HE = """**תכונות MLE במדגמים גדולים:** בתנאי סדירות, MLE הם (א) **עקביים**, (ב) **אסימפטוטית חסרי הטיה**, (ג) **אסימפטוטית יעילים** (מגיעים לגבול קרמר-רao), (ד) **נשמרים** תחת שינוי פרמטריזציה (אם $\\hat{\\theta}$ הוא MLE של $\\theta$, אז $g(\\hat{\\theta})$ הוא MLE של $g(\\theta)$).

**מתכון MLE בארבעה שלבים:**
1. כתבו PMF/PDF $f(x_i;\\theta)$ לכל תצפית.
2. בנו נראות $L(\\theta)=\\prod_i f(x_i;\\theta)$ ולוג-נראות $\\ell(\\theta)=\\sum_i \\ln f(x_i;\\theta)$.
3. גזרו: $\\ell'(\\theta)=0$ ופתרו ל-$\\hat{\\theta}$.
4. אמתו מקסימום: $\\ell''(\\hat{\\theta})<0$ (או בדקו התנהגות בגבול לפרמטרים מוגבלים).

**אומדים סטנדרטיים (שיננו):**
| פרמטר | מודל | MLE | חסר הטיה? |
|---|---|---|---|
| $\\mu$ | נורמלי | $\\bar{X}$ | כן |
| $\\sigma^2$ | נורמלי | $\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ | לא (מוטה למטה) |
| $p$ | בינומי | $k/n$ | כן |
| $\\lambda$ | פואסון | $\\bar{X}$ | כן |

**הערה על שונות מדגם:** האומד **חסר ההטיה** $S^2=\\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ משתמש במחלק $n-1$ (תיקון בסל) כי $\\bar{X}$ מוערך מאותם נתונים, וצורך דרגת חופש אחת. ה-MLE מחלק ב-$n$ ומוטה למטה.

**השוואת אומדים:** כששני אומדים מתחרים, חשבו MSE $=\\text{Var}+\\text{Bias}^2$. אומד מוטה יכול לנצח אומד חסר הטיה אם השונות שלו קטנה בהרבה — מאזן הטיה–שונות מרכזי בסטטיסטיקה מודרנית ולמידת מכונה."""

WE1_EN = """**Problem:** A random sample of $n=5$ exam scores is: 72, 85, 90, 68, 80. Use the sample mean to estimate the population mean $\\mu$.

The sample mean is the most common point estimator for $\\mu$. Before computing, note that exam questions often give raw data and expect you to identify $\\bar{X}$ as both the natural estimate and an unbiased, consistent estimator. Always state the parameter being estimated, not just the number.

### Move 1: Compute the sample mean
$$\\bar{x} = \\frac{72+85+90+68+80}{5} = \\frac{395}{5} = 79.$$

### Move 2: Verify unbiasedness
By linearity of expectation and independence, $E[\\bar{X}]=\\frac{1}{n}\\sum E[X_i]=\\mu$. So $\\bar{X}$ is **unbiased** for $\\mu$ regardless of the population distribution (finite variance assumed).

### Move 3: Precision — standard error
$$\\text{SE}(\\bar{X}) = \\frac{\\sigma}{\\sqrt{n}} = \\frac{\\sigma}{\\sqrt{5}}.$$
As $n$ increases, SE shrinks ($\\propto 1/\\sqrt{n}$): more data means a tighter estimate. Consistency follows from Chebyshev or the LLN.

**Conclusion:** $\\hat{\\mu}=79$ is an unbiased, consistent estimate of the population mean. On exams, pair the numeric answer with the property statements the question requests.

**Exam link:** The same $\\bar{x}=79$ would serve as the centre of a confidence interval for $\\mu$ in `concept:confidence_intervals` — point estimation always precedes interval estimation."""

WE1_HE = """**בעיה:** מדגם אקראי של $n=5$ ציוני מבחן: 72, 85, 90, 68, 80. השתמשו בממוצע המדגם לאמידת ממוצע האוכלוסייה $\\mu$.

ממוצע המדגם הוא האומד הנקודתי הנפוץ ביותר ל-$\\mu$. לפני החישוב, שימו לב ששאלות בחינה נותנות לעיתים נתונים גולמיים ומצפות שתזהו את $\\bar{X}$ כהערכה הטבעית וגם כאומד חסר הטיה ועקבי. תמיד ציינו את הפרמטר המוערך, לא רק את המספר.

### צעד 1: חישוב ממוצע המדגם
$$\\bar{x} = \\frac{72+85+90+68+80}{5} = \\frac{395}{5} = 79.$$

### צעד 2: אימות חסרי הטיה
מקויות התוחלת ובלתי-תלות, $E[\\bar{X}]=\\frac{1}{n}\\sum E[X_i]=\\mu$. לכן $\\bar{X}$ **חסר הטיה** ל-$\\mu$ ללא תלות בהתפלגות האוכלוסייה (בהנחת שונות סופית).

### צעד 3: דיוק — שגיאה סטנדרטית
$$\\text{SE}(\\bar{X}) = \\frac{\\sigma}{\\sqrt{n}} = \\frac{\\sigma}{\\sqrt{5}}.$$
ככל ש-$n$ גדל, SE קטן ($\\propto 1/\\sqrt{n}$): יותר נתונים ⇒ הערכה צמודה יותר. עקביות נובעת מצ'בישב או מחוק המספרים הגדולים.

**מסקנה:** $\\hat{\\mu}=79$ הוא הערכה חסרת הטיה ועקבית של ממוצע האוכלוסייה. בבחינות, צרפו את התשובה המספרית לטענות התכונות שהשאלה מבקשת.

**קשר לבחינה:** אותו $\\bar{x}=79$ יהיה מרכז רווח סמך ל-$\\mu$ ב-`concept:confidence_intervals` — אומדן נקודתי תמיד קודם להערכת רווח."""

WE2_EN = """**Problem:** In $n$ independent Bernoulli trials we observe $k$ successes. Find the MLE of $p$.

This is the canonical MLE derivation on Israeli statistics exams. The likelihood is binomial; taking logs turns products into sums; differentiation yields a rational equation. The answer — sample proportion — is intuitive, but examiners expect the full log-likelihood path, not just \" $\\hat{p}=k/n$ by definition.\"

### Move 1: Write the likelihood
$$L(p) = \\binom{n}{k}p^k(1-p)^{n-k}, \\quad 0<p<1.$$

### Move 2: Log-likelihood (drop the combinatorial constant)
$$\\ell(p) = k\\ln p + (n-k)\\ln(1-p).$$

### Move 3: Score equation
$$\\frac{d\\ell}{dp} = \\frac{k}{p} - \\frac{n-k}{1-p} = 0.$$

### Move 4: Solve
$$k(1-p)=(n-k)p \\Rightarrow k = np \\Rightarrow \\hat{p} = \\frac{k}{n}.$$

### Move 5: Verify maximum
$$\\frac{d^2\\ell}{dp^2} = -\\frac{k}{p^2} - \\frac{n-k}{(1-p)^2} < 0 \\quad \\text{at } \\hat{p}=k/n.$$
The second derivative is always negative on $(0,1)$, confirming a unique maximum.

**Interpretation:** The MLE equals the **sample proportion**, which is also **unbiased** ($E[\\hat{p}]=p$) and **consistent**. Standard error: $\\text{SE}(\\hat{p})=\\sqrt{p(1-p)/n}$ (or plug in $\\hat{p}$ when $p$ is unknown).

**Exam link:** If the next part asks for a 95% CI for $p$, centre the interval at $\\hat{p}=k/n$ and use $\\text{SE}=\\sqrt{\\hat{p}(1-\\hat{p})/n}$ — the same point estimate derived here in `concept:confidence_intervals`."""

WE2_HE = """**בעיה:** ב-$n$ ניסויי ברנולי בלתי-תלויים נצפו $k$ הצלחות. מצאו את MLE של $p$.

זו גזירת MLE קלאסית בבחינות סטטיסטיקה ישראליות. הנראות בינומית; לוג הופך מכפלות לסכומים; גזירה נותנת משוואה רציונלית. התשובה — שיעור המדגם — טבעית, אך הבוחנים מצפים לנתיב לוג-נראות מלא, לא רק \" $\\hat{p}=k/n$ מההגדרה.\"

### צעד 1: כתיבת הנראות
$$L(p) = \\binom{n}{k}p^k(1-p)^{n-k}, \\quad 0<p<1.$$

### צעד 2: לוג-נראות (השמיטו קבוע combinatorial)
$$\\ell(p) = k\\ln p + (n-k)\\ln(1-p).$$

### צעד 3: משוואת score
$$\\frac{d\\ell}{dp} = \\frac{k}{p} - \\frac{n-k}{1-p} = 0.$$

### צעד 4: פתרון
$$k(1-p)=(n-k)p \\Rightarrow k = np \\Rightarrow \\hat{p} = \\frac{k}{n}.$$

### צעד 5: אימות מקסימום
$$\\frac{d^2\\ell}{dp^2} = -\\frac{k}{p^2} - \\frac{n-k}{(1-p)^2} < 0 \\quad \\text{ב- } \\hat{p}=k/n.$$

**פרשנות:** ה-MLE שווה **שיעור המדגם**, שהוא גם **חסר הטיה** ($E[\\hat{p}]=p$) ו**עקבי**. שגיאה סטנדרטית: $\\text{SE}(\\hat{p})=\\sqrt{p(1-p)/n}$ (או הכניסו $\\hat{p}$ כש-$p$ לא ידוע).

**קשר לבחינה:** אם החלק הבא מבקש CI 95% ל-$p$, מרכזו ברווח ב-$\\hat{p}=k/n$ — אותה הערכה שגזרנו כאן."""

WE3_EN = """**Problem:** We observe $n$ independent Poisson observations $x_1,\\ldots,x_n$ with PMF $P(X=x)=e^{-\\lambda}\\lambda^x/x!$. Find the MLE of $\\lambda$.

Poisson MLE is a second exam favourite after binomial. The log-likelihood is linear in $\\sum x_i$ plus a log term; differentiation gives a closed form. Notice the structural pattern: for many exponential-family models, the MLE of the mean parameter is $\\bar{X}$.

### Move 1: Likelihood
$$L(\\lambda) = \\prod_{i=1}^n \\frac{e^{-\\lambda}\\lambda^{x_i}}{x_i!} = e^{-n\\lambda}\\lambda^{\\sum x_i}\\cdot\\prod_{i=1}^n\\frac{1}{x_i!}.$$

### Move 2: Log-likelihood (drop $\\sum\\ln(x_i!)$)
$$\\ell(\\lambda) = -n\\lambda + \\left(\\sum_{i=1}^n x_i\\right)\\ln\\lambda + \\text{const}.$$

### Move 3: Score equation
$$\\frac{d\\ell}{d\\lambda} = -n + \\frac{\\sum x_i}{\\lambda} = 0.$$

### Move 4: Solve
$$\\hat{\\lambda} = \\frac{1}{n}\\sum_{i=1}^n x_i = \\bar{x}.$$

### Move 5: Verify and interpret
$\\ell''(\\lambda)=-\\sum x_i/\\lambda^2<0$ at $\\hat{\\lambda}$. The MLE equals the **sample mean**, which is unbiased ($E[\\bar{X}]=\\lambda$), consistent, and efficient for Poisson data.

**Numeric check:** If observations are 2, 3, 1, 4, 0, then $\\hat{\\lambda}=(2+3+1+4+0)/5=2$. Always verify $\\hat{\\lambda}>0$; Poisson rate must be positive. On exams, state both the formula $\\hat{\\lambda}=\\bar{x}$ and the numeric value."""

WE3_HE = """**בעיה:** נצפו $n$ תצפיות פואסון בלתי-תלויות $x_1,\\ldots,x_n$ עם PMF $P(X=x)=e^{-\\lambda}\\lambda^x/x!$. מצאו את MLE של $\\lambda$.

MLE פואסון הוא מועדף שני בבחינה אחרי בינומי. הלוג-נראות לינארי ב-$\\sum x_i$ בתוספת ln; גזירה נותנת צורה סגורה. שימו לב לדפוס: במודלים רבים של exponential family, MLE של פרמטר הממוצע הוא $\\bar{X}$.

### צעד 1: נראות
$$L(\\lambda) = e^{-n\\lambda}\\lambda^{\\sum x_i}\\cdot\\prod_{i=1}^n\\frac{1}{x_i!}.$$

### צעד 2: לוג-נראות (השמיטו $\\sum\\ln(x_i!)$)
$$\\ell(\\lambda) = -n\\lambda + \\left(\\sum_{i=1}^n x_i\\right)\\ln\\lambda + \\text{קבוע}.$$

### צעד 3: משוואת score
$$\\frac{d\\ell}{d\\lambda} = -n + \\frac{\\sum x_i}{\\lambda} = 0.$$

### צעד 4: פתרון
$$\\hat{\\lambda} = \\frac{1}{n}\\sum_{i=1}^n x_i = \\bar{x}.$$

### צעד 5: אימות ופרשנות
$\\ell''(\\lambda)=-\\sum x_i/\\lambda^2<0$ ב-$\\hat{\\lambda}$. ה-MLE שווה **ממוצע המדגם**, חסר הטיה ($E[\\bar{X}]=\\lambda$), עקבי ויעיל לנתוני פואסון.

**בדיקה מספרית:** אם התצפיות 2, 3, 1, 4, 0, אז $\\hat{\\lambda}=10/5=2$. תמיד ודאו $\\hat{\\lambda}>0$; קצב פואסון חייב להיות חיובי."""

CKPT1_EN = """A sample of 4 values gives: 10, 14, 12, 16. Compute $\\bar{x}$ and $s^2$ (sample variance with divisor $n-1$).

**Step 1 — Sample mean:**
$$\\bar{x} = \\frac{10+14+12+16}{4} = \\frac{52}{4} = 13.$$

**Step 2 — Deviations from mean:**
$(10-13)^2=9$, $(14-13)^2=1$, $(12-13)^2=1$, $(16-13)^2=9$. Sum of squared deviations $=9+1+1+9=20$.

**Step 3 — Unbiased sample variance ($n-1$ divisor):**
$$s^2 = \\frac{20}{4-1} = \\frac{20}{3} \\approx 6.67.$$

**Why $n-1$?** We used $\\bar{x}=13$ (estimated from the same 4 points), so one degree of freedom is lost. Dividing by $n=4$ would give $5$, which **underestimates** $\\sigma^2$ — the MLE bias discussed in this lesson."""

CKPT1_HE = """מדגם של 4 ערכים: 10, 14, 12, 16. חשבו $\\bar{x}$ ו-$s^2$ (שונות מדגם עם מחלק $n-1$).

**שלב 1 — ממוצע מדגם:**
$$\\bar{x} = \\frac{10+14+12+16}{4} = \\frac{52}{4} = 13.$$

**שלב 2 — סטיות מהממוצע:**
$(10-13)^2=9$, $(14-13)^2=1$, $(12-13)^2=1$, $(16-13)^2=9$. סכום ריבועי סטיות $=20$.

**שלב 3 — שונות מדגם חסרת הטיה (מחלק $n-1$):**
$$s^2 = \\frac{20}{4-1} = \\frac{20}{3} \\approx 6.67.$$

**למה $n-1$?** השתמשנו ב-$\\bar{x}=13$ (מוערך מאותם 4 נקודות), ולכן איבדנו דרגת חופש אחת. חלוקה ב-$n=4$ הייתה נותנת $5$, ש**מזלזלת** ב-$\\sigma^2$ — ההטיה של MLE שנדון בשיעור."""

CKPT2_EN = """A sample of 10 trials has 7 successes. What is the MLE of $p$?

**Step 1 — Identify the model:** Independent Bernoulli trials with unknown success probability $p$. Observed count $k=7$ out of $n=10$.

**Step 2 — Apply the MLE formula:** From the binomial log-likelihood derivation (Worked Example 2), the MLE of $p$ is the sample proportion:
$$\\hat{p} = \\frac{k}{n} = \\frac{7}{10} = 0.7.$$

**Step 3 — Sanity check:** $0<\\hat{p}<1$ ✓. The estimate is unbiased ($E[\\hat{p}]=p$) and lies between the extremes 0 and 1. Standard error (using estimated $p$): $\\text{SE}\\approx\\sqrt{0.7\\cdot 0.3/10}\\approx 0.145$ — useful if the next question asks for uncertainty."""

CKPT2_HE = """מדגם של 10 ניסויים עם 7 הצלחות. מהו MLE של $p$?

**שלב 1 — זיהוי המודל:** ניסויי ברנולי בלתי-תלויים עם הסתברות הצלחה לא ידועה $p$. נספרו $k=7$ מתוך $n=10$.

**שלב 2 — יישום נוסחת MLE:** מגזירת לוג-נראות בינומית (דוגמה 2), MLE של $p$ הוא שיעור המדגם:
$$\\hat{p} = \\frac{k}{n} = \\frac{7}{10} = 0.7.$$

**שלב 3 — בדיקת הגיון:** $0<\\hat{p}<1$ ✓. האומד חסר הטיה ($E[\\hat{p}]=p$) ונמצא בין 0 ל-1. שגיאה סטנדרטית (עם $p$ מוערך): $\\text{SE}\\approx\\sqrt{0.7\\cdot 0.3/10}\\approx 0.145$ — שימושי אם השאלה הבאה שואלת על אי-ודאות."""

METHOD_EN = """**MLE Recipe (always write these steps on exams):**
1. PMF/PDF: $f(x_i;\\theta)$.
2. Likelihood: $L(\\theta)=\\prod_{i=1}^n f(x_i;\\theta)$.
3. Log-likelihood: $\\ell(\\theta)=\\sum \\ln f(x_i;\\theta)$ — drop constants not depending on $\\theta$.
4. Score: $\\ell'(\\theta)=0$; solve for $\\hat{\\theta}$.
5. Verify: $\\ell''(\\hat{\\theta})<0$ or boundary check.

| Parameter | Distribution | MLE | Notes |
|---|---|---|---|
| $\\mu$ | Normal | $\\bar{X}$ | Unbiased |
| $\\sigma^2$ | Normal | $\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ | Biased; use $n-1$ for unbiased $S^2$ |
| $p$ | Binomial | $k/n$ | Unbiased |
| $\\lambda$ | Poisson | $\\bar{X}$ | Unbiased |
| $\\lambda$ | Exponential | $1/\\bar{X}$ | See exercise e9 |

**Decision flow:** Read the problem → identify the parametric model → pick the table row → derive if non-standard → report $\\hat{\\theta}$ with properties (unbiased? consistent?) if asked.

**MSE shortcut:** $\\text{MSE}=\\text{Var}+\\text{Bias}^2$. Given $E[T]$ and $\\text{Var}(T)$, compute bias first, then MSE."""

METHOD_HE = """**מתכון MLE (כתבו תמיד את השלבים בבחינה):**
1. PMF/PDF: $f(x_i;\\theta)$.
2. נראות: $L(\\theta)=\\prod_{i=1}^n f(x_i;\\theta)$.
3. לוג-נראות: $\\ell(\\theta)=\\sum \\ln f(x_i;\\theta)$ — השמיטו קבועים שלא תלויים ב-$\\theta$.
4. Score: $\\ell'(\\theta)=0$; פתרו ל-$\\hat{\\theta}$.
5. אימות: $\\ell''(\\hat{\\theta})<0$ או בדיקת גבול.

| פרמטר | התפלגות | MLE | הערות |
|---|---|---|---|
| $\\mu$ | נורמלי | $\\bar{X}$ | חסר הטיה |
| $\\sigma^2$ | נורמלי | $\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ | מוטה; $n-1$ ל-$S^2$ חסר הטיה |
| $p$ | בינומי | $k/n$ | חסר הטיה |
| $\\lambda$ | פואסון | $\\bar{X}$ | חסר הטיה |
| $\\lambda$ | מעריכי | $1/\\bar{X}$ | ראו תרגיל e9 |

**זרימת החלטה:** קראו את הבעיה → זהו את ההתפלגות → בחרו שורה בטבלה → גזרו אם לא סטנדרטי → דווחו $\\hat{\\theta}$ עם תכונות (חסר הטיה? עקבי?) אם נדרש.

**קיצור MSE:** $\\text{MSE}=\\text{Var}+\\text{Bias}^2$. נתון $E[T]$ ו-$\\text{Var}(T)$ — חשבו הטיה קודם, ואז MSE."""

PITFALL_EN = """1. **Using $n$ instead of $n-1$ in sample variance.** The MLE $\\hat{\\sigma}^2=\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ is biased low. The unbiased estimator $S^2$ divides by $n-1$. Exams love asking *why* — link to the lost degree of freedom from estimating $\\mu$ with $\\bar{X}$.

2. **Confusing consistency with unbiasedness.** These are independent properties. The MLE of $\\sigma^2$ is consistent but biased. An estimator can be unbiased yet inconsistent (pathological examples exist). Check which property the question asks for.

3. **Skipping the maximum verification.** Setting $\\ell'(\\theta)=0$ finds critical points, not necessarily maxima. Check $\\ell''(\\hat{\\theta})<0$, or compare boundary values (e.g., uniform $U(0,\\theta)$ where MLE is $\\max X_i$).

4. **Treating MLE properties as exact for small $n$.** Consistency, asymptotic efficiency, and asymptotic normality are large-sample results. With $n=3$, the MLE may behave poorly; Bayesian or regularised estimators may be preferable.

5. **Mixing up SE formulas for $\\hat{p}$.** $\\sqrt{p(1-p)/n}$ uses the true $p$; $\\sqrt{\\hat{p}(1-\\hat{p})/n}$ plugs in the estimate. Both appear in exam questions — read carefully which is requested."""

PITFALL_HE = """1. **שימוש ב-$n$ במקום $n-1$ בשונות מדגם.** MLE $\\hat{\\sigma}^2=\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ מוטה למטה. האומד חסר ההטיה $S^2$ מחלק ב-$n-1$. בחינות אוהבות לשאול *למה* — קשרו לאיבוד דרגת חופש מאמידת $\\mu$ עם $\\bar{X}$.

2. **בלבול עקביות עם חסרי הטיה.** אלו תכונות בלתי-תלויות. MLE של $\\sigma^2$ עקבי אך מוטה. אומד יכול להיות חסר הטיה אך לא עקבי (קיימות דוגמאות קיצוניות). בדקו איזו תכונה השאלה מבקשת.

3. **דילוג על אימות מקסימום.** $\\ell'(\\theta)=0$ מוצא נקודות קריטיות, לא בהכרח מקסימום. בדקו $\\ell''(\\hat{\\theta})<0$, או השוו ערכי גבול (למשל $U(0,\\theta)$ שם MLE הוא $\\max X_i$).

4. **התייחסות לתכונות MLE כמדויקות ל-$n$ קטן.** עקביות, יעילות אסימפטוטית ונורמליות אסימפטוטית הן תוצאות מדגם גדול. עם $n=3$, MLE עלול להתנהג בצורה גרועה; אומדים בייסיאניים או מנורמלים עשויים להיות עדיפים.

5. **ערבוב נוסחאות SE של $\\hat{p}$.** $\\sqrt{p(1-p)/n}$ משתמש ב-$p$ האמיתי; $\\sqrt{\\hat{p}(1-\\hat{p})/n}$ מכניס הערכה. שתיהן מופיעות בבחינות — קראו בקפידה מה מבוקש."""

WHY_EN = """Point estimation is the first link in the inference chain: you cannot build a confidence interval or run a hypothesis test without choosing an estimator for $\\mu$, $p$, or $\\lambda$. Polls report \"52% support\" — that is $\\hat{p}=k/n$; quality control tracks $\\bar{x}$ against specifications; epidemiology estimates infection rates from sampled tests.

**Exam relevance:** TAU, Technion, and HUJI statistics courses ask you to derive MLEs (binomial, Poisson, exponential, sometimes uniform), prove unbiasedness or consistency, compute MSE, and explain the $n$ vs $n-1$ variance divisor. These skills transfer directly to `concept:confidence_intervals` (where $\\hat{p}$ and $\\bar{x}$ become interval centres) and `concept:hypothesis_testing` (where MLEs appear in likelihood ratio tests).

**Cross-subject link:** In physics labs, reporting $\\bar{x}\\pm s/\\sqrt{n}$ assumes the sample mean is a sensible point estimate. In machine learning, regularisation explicitly trades bias for lower variance — the same MSE decomposition from this lesson."""

WHY_HE = """אומדן נקודתי הוא הקישור הראשון בשרשרת ההסקה: לא ניתן לבנות רווח סמך או להריץ בדיקת השערות בלי לבחור אומד ל-$\\mu$, $p$, או $\\lambda$. סקרים מדווחים \"52% תמיכה\" — זה $\\hat{p}=k/n$; בקרת איכות עוקבת אחר $\\bar{x}$; מחקר מגיפות מעריך שיעורי הדבקה מבדיקות מדגם.

**רלוונטיות לבחינה:** קורסי סטטיסטיקה ב-TAU, טכניון ו-HUJI מבקשים לגזור MLE (בינומי, פואסון, מעריכי, לפעמים אחיד), להוכיח חסרי הטיה או עקביות, לחשב MSE, ולהסביר מחלק $n$ לעומת $n-1$ בשונות. מיומנויות אלה עוברות ישירות ל-`concept:confidence_intervals` (שם $\\hat{p}$ ו-$\\bar{x}$ הופכים למרכזי רווח) ול-`concept:hypothesis_testing` (שם MLE מופיעים במבחני likelihood ratio).

**קשר בין-מקצועי:** במעבדות פיזיקה, דיווח $\\bar{x}\\pm s/\\sqrt{n}$ מניח שממוצע המדגם הוא הערכה סבירה. בלמידת מכונה, regularization מחליף במפורש הטיה בשונות נמוכה — אותו פירוק MSE מהשיעור."""

BEFORE_EN = """**Formula card:**
- $\\bar{X}=\\frac{1}{n}\\sum X_i$ — unbiased for $\\mu$; $\\text{SE}=\\sigma/\\sqrt{n}$
- $S^2=\\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ — unbiased for $\\sigma^2$
- $\\hat{p}=k/n$ — unbiased for $p$; $\\text{Var}(\\hat{p})=p(1-p)/n$
- MLE recipe: $L\\to\\ell\\to\\ell'=0\\to$ verify max
- $\\text{MSE}=\\text{Var}+\\text{Bias}^2$; $\\text{Bias}=E[T]-\\theta$

**Exam patterns:**
- Derive MLE for binomial $p$, Poisson $\\lambda$, exponential rate.
- State bias/unbiasedness of a given estimator.
- Compute MSE from $E[T]$ and $\\text{Var}(T)$.
- Compare two estimators (often via MSE).
- Prove consistency of $\\bar{X}$ using Chebyshev.

**Last review:** Derive Poisson MLE from scratch once, then solve one checkpoint without notes."""

BEFORE_HE = """**גיליון נוסחאות:**
- $\\bar{X}=\\frac{1}{n}\\sum X_i$ — חסר הטיה ל-$\\mu$; $\\text{SE}=\\sigma/\\sqrt{n}$
- $S^2=\\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ — חסר הטיה ל-$\\sigma^2$
- $\\hat{p}=k/n$ — חסר הטיה ל-$p$; $\\text{Var}(\\hat{p})=p(1-p)/n$
- מתכון MLE: $L\\to\\ell\\to\\ell'=0\\to$ אימות מקסימום
- $\\text{MSE}=\\text{Var}+\\text{Bias}^2$; $\\text{Bias}=E[T]-\\theta$

**דפוסי בחינה:**
- גזירת MLE ל-$p$ בינומי, $\\lambda$ פואסון, קצב מעריכי.
- ציון הטיה/חסרי הטיה של אומד נתון.
- חישוב MSE מ-$E[T]$ ו-$\\text{Var}(T)$.
- השוואת שני אומדים (לעיתים דרך MSE).
- הוכחת עקביות $\\bar{X}$ בצ'בישב.

**חזרה אחרונה:** גזרו MLE פואסון מאפס פעם אחת, ואז פתרו checkpoint בלי רשימות."""

SUMMARY_EN = """- An **estimator** $T=g(X_1,\\ldots,X_n)$ estimates unknown $\\theta$; its realised value is an **estimate**.
- **Unbiased:** $E[T]=\\theta$. **Consistent:** $T_n\\xrightarrow{P}\\theta$. **Efficient:** smallest variance among unbiased estimators.
- **MSE** $=\\text{Var}+\\text{Bias}^2$ is the practical comparison tool; biased estimators can win on MSE.
- **MLE:** maximise $L(\\theta)=\\prod f(x_i;\\theta)$ via log-likelihood; standard results: $\\hat{\\mu}=\\bar{X}$, $\\hat{p}=k/n$, $\\hat{\\lambda}=\\bar{X}$ (Poisson).
- **Variance divisor:** MLE uses $n$ (biased); unbiased $S^2$ uses $n-1$.
- **Next step:** Use these point estimates as centres for confidence intervals (`concept:confidence_intervals`)."""

SUMMARY_HE = """- **אומד** $T=g(X_1,\\ldots,X_n)$ מעריך $\\theta$ לא ידוע; הערך הממומש הוא **הערכה**.
- **חסר הטיה:** $E[T]=\\theta$. **עקבי:** $T_n\\xrightarrow{P}\\theta$. **יעיל:** שונות מינימלית בין חסרי הטיה.
- **MSE** $=\\text{Var}+\\text{Bias}^2$ הוא כלי ההשוואה המעשי; אומדים מוטים יכולים לנצח ב-MSE.
- **MLE:** מקסימום $L(\\theta)=\\prod f(x_i;\\theta)$ דרך לוג-נראות; תוצאות סטנדרטיות: $\\hat{\\mu}=\\bar{X}$, $\\hat{p}=k/n$, $\\hat{\\lambda}=\\bar{X}$ (פואסון).
- **מחלק שונות:** MLE משתמש ב-$n$ (מוטה); $S^2$ חסר הטיה משתמש ב-$n-1$.
- **המשך:** השתמשו בהערכות נקודתיות כמרכזי רווחי סמך (`concept:confidence_intervals`)."""

Q_EXPL = [
    fmt_expl(
        "The sample mean $\\bar{x}=42$ estimates the **population mean** $\\mu$. By linearity of expectation, $E[\\bar{X}]=\\mu$, so $\\bar{X}$ is an **unbiased** estimator — its average value equals the parameter across repeated samples.",
        "When you see a single number from a sample, ask: \"Which parameter does this statistic target?\" $\\bar{x}$ always targets $\\mu$; $\\hat{p}=k/n$ targets $p$; $\\bar{x}$ for Poisson data targets $\\lambda$. Then check unbiasedness via $E[T]=\\theta$.",
        "Identifying the wrong parameter (e.g., saying $\\bar{x}$ estimates $\\sigma^2$). Stating \"biased\" without computing $E[\\bar{X}]$. Giving only the number 42 without naming $\\mu$.",
        "Two-part exam answers: (1) name the parameter, (2) state unbiased/biased with justification. Write $E[\\bar{X}]=\\mu$ even when it seems obvious — partial credit depends on it.",
        "ממוצע המדגם $\\bar{x}=42$ מעריך את **ממוצע האוכלוסייה** $\\mu$. מקויות התוחלת, $E[\\bar{X}]=\\mu$, ולכן $\\bar{X}$ הוא אומד **חסר הטיה** — ערכו הממוצע שווה לפרמטר במדגמים חוזרים.",
        "כשמופיע מספר בודד ממדגם, שאלו: \"איזה פרמטר הסטטיסטיקה הזו מכוונת אליו?\" $\\bar{x}$ תמיד מכוון ל-$\\mu$; $\\hat{p}=k/n$ ל-$p$; $\\bar{x}$ בנתוני פואסון ל-$\\lambda$. ואז בדקו חסרי הטיה דרך $E[T]=\\theta$.",
        "זיהוי פרמטר שגוי (למשל $\\bar{x}$ מעריך $\\sigma^2$). \"מוטה\" בלי חישוב $E[\\bar{X}]$. תשובה 42 בלבד בלי לציין $\\mu$.",
        "תשובות דו-חלקיות בבחינה: (1) שם הפרמטר, (2) חסר הטיה/מוטה עם נימוק. כתבו $E[\\bar{X}]=\\mu$ גם כשזה נראה ברור — ניקוד חלקי תלוי בזה.",
    ),
    fmt_expl(
        "Dividing by $n-1$ makes $S^2=\\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ an **unbiased** estimator of $\\sigma^2$: $E[S^2]=\\sigma^2$. Dividing by $n$ gives $E[\\hat{\\sigma}^2_{\\text{MLE}}]=\\frac{n-1}{n}\\sigma^2<\\sigma^2$ — a systematic downward bias.",
        "The lost degree of freedom comes from estimating $\\mu$ with $\\bar{X}$ from the same data. With $n$ points and one estimated mean, only $n-1$ independent deviations remain. The MLE ignores this and divides by $n$.",
        "Saying \"$n-1$ makes variance bigger\" without explaining unbiasedness. Confusing sample variance $S^2$ with population variance $\\sigma^2$. Using $n-1$ in the MLE formula when asked specifically for MLE.",
        "Link $n-1$ to Bessel's correction and the MLE bias in one sentence on exams. Examiners want the *reason* (estimated mean), not just the rule.",
        "חלוקה ב-$n-1$ הופכת $S^2=\\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ לאומד **חסר הטיה** של $\\sigma^2$: $E[S^2]=\\sigma^2$. חלוקה ב-$n$ נותנת $E[\\hat{\\sigma}^2_{\\text{MLE}}]=\\frac{n-1}{n}\\sigma^2<\\sigma^2$ — הטיה קבועה למטה.",
        "איבוד דרגת החופש נובע מאמידת $\\mu$ עם $\\bar{X}$ מאותם נתונים. עם $n$ נקודות וממוצע מוערך אחד, נשארות $n-1$ סטיות בלתי-תלויות. MLE מתעלם מכך ומחלק ב-$n$.",
        "\"$n-1$ מגדיל שונות\" בלי הסבר חסרי הטיה. בלבול $S^2$ עם $\\sigma^2$. $n-1$ בנוסחת MLE כשמבקשים במפורש MLE.",
        "קשרו $n-1$ לתיקון בסל ולהטיית MLE במשפט אחד בבחינה. הבוחנים רוצים את ה*סיבה* (ממוצע מוערך), לא רק את הכלל.",
    ),
    fmt_expl(
        "For Poisson data, the MLE of $\\lambda$ is the sample mean: $\\hat{\\lambda}=\\bar{x}=(3+1+4+2+5+3)/6=18/6=3$. This follows from setting the Poisson score equation $-n+\\sum x_i/\\lambda=0$.",
        "Poisson MLE is always $\\bar{X}$ — memorise this pattern. Sum the observations, divide by $n$. Verify $\\hat{\\lambda}>0$; a Poisson rate must be positive.",
        "Using $n=6$ as the estimate instead of dividing. Forgetting one observation in the sum. Reporting variance instead of the rate $\\lambda$.",
        "After computing $\\hat{\\lambda}=3$, note it equals both the MLE and the method-of-moments estimator for Poisson — examiners appreciate knowing they coincide here.",
        "לנתוני פואסון, MLE של $\\lambda$ הוא ממוצע המדגם: $\\hat{\\lambda}=\\bar{x}=(3+1+4+2+5+3)/6=18/6=3$. זה נובע ממשוואת score $-n+\\sum x_i/\\lambda=0$.",
        "MLE פואסון תמיד $\\bar{X}$ — שיננו. סכמו תצפיות, חלקו ב-$n$. ודאו $\\hat{\\lambda}>0$; קצב פואסון חייב להיות חיובי.",
        "שימוש ב-$n=6$ כהערכה במקום חלוקה. שכחת תצפית בסכום. דיווח שונות במקום קצב $\\lambda$.",
        "אחרי $\\hat{\\lambda}=3$, ציינו שזה גם MLE וגם method-of-moments לפואסון — הבוחנים מעריכים שיודעים שהם מתאימים כאן בדיוק.",
    ),
    fmt_expl(
        "For $\\hat{p}=X/n$ where $X\\sim\\text{Binomial}(n,p)$: $E[\\hat{p}]=E[X/n]=np/n=p$. Therefore $\\text{Bias}(\\hat{p})=E[\\hat{p}]-p=0$ — the sample proportion is **unbiased**.",
        "Bias is always $E[T]-\\theta$. For proportions, write out the expectation using $E[X]=np$. If the question asks \"state the bias,\" give the numeric value 0, not just \"unbiased.\"",
        "Computing $\\text{Var}(\\hat{p})$ when asked for bias. Saying \"unbiased because $\\hat{p}$ is close to $p$\" — closeness is precision, not bias. Confusing $\\hat{p}$ with $p$ in the bias formula.",
        "When asked for bias, write the definition $\\text{Bias}=E[\\hat{p}]-p$ first, then substitute. Even for unbiased estimators, show the calculation — it takes two lines and earns full credit.",
        "עבור $\\hat{p}=X/n$ כאשר $X\\sim\\text{Binomial}(n,p)$: $E[\\hat{p}]=E[X/n]=np/n=p$. לכן $\\text{Bias}(\\hat{p})=E[\\hat{p}]-p=0$ — שיעור המדגם **חסר הטיה**.",
        "הטיה תמיד $E[T]-\\theta$. לפרופורציות, כתבו תוחלת עם $E[X]=np$. אם שואלים \"ציין הטיה,\" תנו 0, לא רק \"חסר הטיה.\"",
        "חישוב $\\text{Var}(\\hat{p})$ כשמבקשים הטיה. \"חסר הטיה כי $\\hat{p}$ קרוב ל-$p$\" — קרבה היא דיוק, לא הטיה. בלבול $\\hat{p}$ עם $p$.",
        "כשמבקשים הטיה, כתבו $\\text{Bias}=E[\\hat{p}]-p$ קודם, ואז הציבו. גם לאומדים חסרי הטיה — הראו חישוב; שתי שורות לניקוד מלא.",
    ),
    fmt_expl(
        "MLE: $\\hat{p}=9/15=0.6$. Standard error (using estimated $p$): $\\text{SE}(\\hat{p})=\\sqrt{\\hat{p}(1-\\hat{p})/n}=\\sqrt{0.6\\cdot 0.4/15}=\\sqrt{0.016}\\approx 0.126$.",
        "Two tasks: (1) MLE of $p$ is always $k/n$ for binomial data. (2) SE uses $\\sqrt{\\hat{p}(1-\\hat{p})/n}$ when $p$ is unknown. Do them in order; do not mix formulas.",
        "Using $\\sqrt{p(1-p)/n}$ with unknown true $p$ instead of $\\hat{p}$. Computing SE before finding $\\hat{p}$. Rounding 0.126 to 0.13 without keeping more precision when subsequent steps need it.",
        "Write $\\hat{p}$ first, box it, then compute SE. Israeli exams often give $k$ and $n$ separately — divide immediately to get $\\hat{p}=0.6$ before any square root.",
        "MLE: $\\hat{p}=9/15=0.6$. שגיאה סטנדרטית (עם $p$ מוערך): $\\text{SE}(\\hat{p})=\\sqrt{0.6\\cdot 0.4/15}=\\sqrt{0.016}\\approx 0.126$.",
        "שתי משימות: (1) MLE של $p$ תמיד $k/n$ לנתונים בינומיים. (2) SE עם $\\sqrt{\\hat{p}(1-\\hat{p})/n}$ כש-$p$ לא ידוע. בסדר; אל תערבבו נוסחאות.",
        "$\\sqrt{p(1-p)/n}$ עם $p$ אמיתי לא ידוע במקום $\\hat{p}$. SE לפני $\\hat{p}$. עיגול 0.126 ל-0.13 בלי דיוק לשלבים הבאים.",
        "כתבו $\\hat{p}$ קודם, סמנו, ואז SE. בבחינות נותנים $k$ ו-$n$ בנפרד — חלקו מיד ל-$\\hat{p}=0.6$ לפני שורש.",
    ),
    fmt_expl(
        "Given $E[T]=\\theta+2$, the bias is $\\text{Bias}(T)=E[T]-\\theta=2$. MSE formula: $\\text{MSE}(T)=\\text{Var}(T)+\\text{Bias}^2(T)=3+2^2=3+4=7$.",
        "MSE problems are pure algebra once you identify bias. Step 1: compute bias from $E[T]$. Step 2: square it. Step 3: add $\\text{Var}(T)$. Never forget to square the bias.",
        "Using $\\text{Bias}=2$ without squaring in MSE (getting $3+2=5$). Computing $\\text{Bias}=\\theta+2$ instead of $\\text{Bias}=2$. Confusing MSE with variance alone.",
        "Write the MSE decomposition explicitly on exams: $\\text{MSE}=\\text{Var}+\\text{Bias}^2=3+4=7$. Examiners deduct points if you skip the formula even when the arithmetic is correct.",
        "נתון $E[T]=\\theta+2$, ההטיה $\\text{Bias}(T)=E[T]-\\theta=2$. MSE: $\\text{MSE}(T)=\\text{Var}(T)+\\text{Bias}^2(T)=3+2^2=3+4=7$.",
        "בעיות MSE הן אלגebra טהורה אחרי זיהוי הטיה. שלב 1: הטיה מ-$E[T]$. שלב 2: ריבוע. שלב 3: הוספת $\\text{Var}(T)$. אל תשכחו לרבע את ההטיה.",
        "$\\text{Bias}=2$ בלי ריבוע (מקבלים $3+2=5$). $\\text{Bias}=\\theta+2$ במקום $2$. בלבול MSE עם שונות בלבד.",
        "כתבו פירוק MSE במפורש על הדף: $\\text{MSE}=\\text{Var}+\\text{Bias}^2=3+4=7$. מורידים נקודות אם מדלגים על הנוסחה גם כשהחשבון נכון בבחינה.",
    ),
    fmt_expl(
        "The MLE $\\hat{\\sigma}^2=\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ satisfies $E[\\hat{\\sigma}^2]=\\frac{n-1}{n}\\sigma^2<\\sigma^2$. It systematically **underestimates** $\\sigma^2$ because deviations use $\\bar{X}$ (estimated) instead of the true $\\mu$, losing one degree of freedom.",
        "Two explanations appear on exams: (1) algebraic — compute $E[\\sum(X_i-\\bar{X})^2]=(n-1)\\sigma^2$. (2) conceptual — estimating the centre uses up one df. The MLE divides by $n$; unbiased $S^2$ divides by $n-1$ to compensate.",
        "Saying \"biased because $n$ is small\" — bias exists for all $n$. Claiming $\\bar{X}$ causes bias in $\\bar{X}$ itself (different issue). Stating biased without showing $E[\\hat{\\sigma}^2]<\\sigma^2$.",
        "When explaining bias, write the expectation result $\\frac{n-1}{n}\\sigma^2$ explicitly. Link to Bessel's correction — examiners want the mathematical reason, not just \"divide by $n-1$.\"",
        "MLE $\\hat{\\sigma}^2=\\frac{1}{n}\\sum(X_i-\\bar{X})^2$ מקיים $E[\\hat{\\sigma}^2]=\\frac{n-1}{n}\\sigma^2<\\sigma^2$. הוא **מזלזל** ב-$\\sigma^2$ כי סטיות משתמשות ב-$\\bar{X}$ (מוערך) במקום $\\mu$ האמיתי, ומאבדות דרגת חופש.",
        "שתי הסברים בבחינות: (1) אלגברי — $E[\\sum(X_i-\\bar{X})^2]=(n-1)\\sigma^2$. (2) מושגי — אמידת המרכז צורכת df. MLE מחלק ב-$n$; $S^2$ חסר הטיה ב-$n-1$ לפיצוי.",
        "\"מוטה כי $n$ קטן\" — הטיה לכל $n$. $\\bar{X}$ גורם להטיה ב-$\\bar{X}$ (נושא אחר). \"מוטה\" בלי $E[\\hat{\\sigma}^2]<\\sigma^2$.",
        "בהסבר הטיה, כתבו $\\frac{n-1}{n}\\sigma^2$ במפורש. קשר לתיקון בסל — הבוחנים רוצים סיבה מתמטית, לא רק \"חלקו ב-$n-1$.\"",
    ),
    fmt_expl(
        "$T_1=\\bar{X}$: $E[T_1]=\\mu$, unbiased, $\\text{MSE}(T_1)=\\text{Var}(\\bar{X})=\\sigma^2/n$. $T_2=\\bar{X}+5$: $E[T_2]=\\mu+5$, bias $=5$, $\\text{MSE}(T_2)=\\sigma^2/n+25$. Since $\\sigma^2/n+25>\\sigma^2/n$, **$T_1$ is better** (lower MSE and unbiased).",
        "Compare estimators via MSE, not just bias. Adding a constant to an unbiased estimator introduces bias $5$ without reducing variance, so MSE increases by exactly $25$. Unbiasedness alone does not make $T_2$ competitive.",
        "Choosing $T_2$ because it \"adjusts\" the estimate. Comparing only bias without MSE. Forgetting that $\\text{Var}(T_2)=\\text{Var}(\\bar{X})$ — adding a constant does not change variance.",
        "For comparison questions, compute both MSEs side by side. State clearly: lower MSE wins. Mention both unbiasedness and MSE — Israeli exams reward complete comparisons.",
        "$T_1=\\bar{X}$: $E[T_1]=\\mu$, חסר הטיה, $\\text{MSE}(T_1)=\\sigma^2/n$. $T_2=\\bar{X}+5$: $E[T_2]=\\mu+5$, הטיה $=5$, $\\text{MSE}(T_2)=\\sigma^2/n+25$. כיוון $\\sigma^2/n+25>\\sigma^2/n$, **$T_1$ טוב יותר** (MSE נמוך וחסר הטיה).",
        "השוו דרך MSE, לא רק הטיה. הוספת קבוע לאומד חסר הטיה מכניסה הטיה 5 בלי להקטין שונות, ו-MSE עולה ב-25. חסרי הטיה לבד לא עושים $T_2$ תחרותי.",
        "בחירת $T_2$ כי \"מתקן\" הערכה. השוואת הטיה בלי MSE. שכחה ש-$\\text{Var}(T_2)=\\text{Var}(\\bar{X})$ — קבוע לא משנה שונות.",
        "בשאלות השוואה, חשבו MSE זה לצד זה. ציינו: MSE נמוך מנצח. הזכירו חסרי הטיה ו-MSE — בחינות ישראליות מעריכות השוואה מלאה.",
    ),
]


EXERCISE_SOLUTIONS = {
    "e5": {
        "solution_en": "**Step 1 — MLE of $p$:** For $k=9$ successes in $n=15$ Bernoulli trials, the binomial MLE is $\\hat{p}=k/n=9/15=0.6$.\n\n**Step 2 — Standard error:** With unknown $p$, use the estimated SE: $\\text{SE}(\\hat{p})=\\sqrt{\\hat{p}(1-\\hat{p})/n}=\\sqrt{0.6\\cdot 0.4/15}=\\sqrt{0.24/15}=\\sqrt{0.016}\\approx 0.126$.\n\n**Check:** $0<\\hat{p}<1$ and the SE is positive.",
        "solution_he": "**שלב 1 — MLE של $p$:** ל-$k=9$ הצלחות ב-$n=15$ ניסויי ברנולי, MLE הבינומי הוא $\\hat{p}=k/n=9/15=0.6$.\n\n**שלב 2 — שגיאה סטנדרטית:** כש-$p$ לא ידוע, $\\text{SE}(\\hat{p})=\\sqrt{\\hat{p}(1-\\hat{p})/n}=\\sqrt{0.6\\cdot 0.4/15}=\\sqrt{0.016}\\approx 0.126$.\n\n**בדיקה:** $0<\\hat{p}<1$ וה-SE חיובי.",
    },
    "e6": {
        "solution_en": "**Step 1 — Bias:** $\\text{Bias}(T)=E[T]-\\theta=(\\theta+2)-\\theta=2$.\n\n**Step 2 — MSE:** $\\text{MSE}(T)=\\text{Var}(T)+[\\text{Bias}(T)]^2=3+2^2=3+4=7$.\n\n**Check:** Always square the bias before adding variance.",
        "solution_he": "**שלב 1 — הטיה:** $\\text{Bias}(T)=E[T]-\\theta=(\\theta+2)-\\theta=2$.\n\n**שלב 2 — MSE:** $\\text{MSE}(T)=\\text{Var}(T)+[\\text{Bias}(T)]^2=3+2^2=3+4=7$.\n\n**בדיקה:** תמיד רבעו את ההטיה לפני חיבור השונות.",
    },
    "e9": {
        "solution_en": "**Step 1 — Likelihood:** $L(\\lambda)=\\prod_{i=1}^n \\lambda e^{-\\lambda x_i}=\\lambda^n e^{-\\lambda\\sum x_i}$ for $x_i>0$.\n\n**Step 2 — Log-likelihood:** $\\ell(\\lambda)=n\\ln\\lambda-\\lambda\\sum_{i=1}^n x_i$.\n\n**Step 3 — Score:** $\\ell'(\\lambda)=n/\\lambda-\\sum x_i=0 \\Rightarrow \\hat{\\lambda}=n/\\sum x_i=1/\\bar{x}$.\n\n**Check:** $\\hat{\\lambda}>0$ requires all $x_i>0$; verify with $\\ell''(\\hat{\\lambda})<0$.",
        "solution_he": "**שלב 1 — נראות:** $L(\\lambda)=\\lambda^n e^{-\\lambda\\sum x_i}$ עבור $x_i>0$.\n\n**שלב 2 — לוג-נראות:** $\\ell(\\lambda)=n\\ln\\lambda-\\lambda\\sum x_i$.\n\n**שלב 3 — Score:** $\\ell'(\\lambda)=n/\\lambda-\\sum x_i=0 \\Rightarrow \\hat{\\lambda}=n/\\sum x_i=1/\\bar{x}$.\n\n**בדיקה:** $\\hat{\\lambda}>0$ דורש $x_i>0$; אמתו $\\ell''(\\hat{\\lambda})<0$.",
    },
    "e10": {
        "solution_en": "**Setup:** $\\bar{X}$ has $E[\\bar{X}]=\\mu$ and $\\text{Var}(\\bar{X})=\\sigma^2/n$. For any $\\varepsilon>0$, Chebyshev gives\n$$P(|\\bar{X}-\\mu|>\\varepsilon)\\leq\\frac{\\text{Var}(\\bar{X})}{\\varepsilon^2}=\\frac{\\sigma^2}{n\\varepsilon^2}\\to 0\\quad\\text{as }n\\to\\infty.$$\nTherefore $\\bar{X}\\xrightarrow{P}\\mu$: $\\bar{X}$ is **consistent** for $\\mu$. $\\blacksquare$",
        "solution_he": "**הכנה:** ל-$\\bar{X}$ יש $E[\\bar{X}]=\\mu$ ו-$\\text{Var}(\\bar{X})=\\sigma^2/n$. לכל $\\varepsilon>0$, צ'בישב נותן\n$$P(|\\bar{X}-\\mu|>\\varepsilon)\\leq\\frac{\\sigma^2}{n\\varepsilon^2}\\to 0\\quad\\text{כש }n\\to\\infty.$$\nלכן $\\bar{X}\\xrightarrow{P}\\mu$: $\\bar{X}$ **עקבי** ל-$\\mu$. $\\blacksquare$",
    },
    "e12": {
        "solution_en": "**Unbiasedness:** $X\\sim\\text{Binomial}(n,p)$ so $E[X]=np$. Then $E[\\hat{p}]=E[X/n]=np/n=p$, hence $\\text{Bias}(\\hat{p})=0$.\n\n**Variance:** $\\text{Var}(\\hat{p})=\\text{Var}(X/n)=\\text{Var}(X)/n^2=np(1-p)/n^2=p(1-p)/n$.\n\n**Check:** As $n$ grows, $\\text{Var}(\\hat{p})\\to 0$, confirming consistency. $\\blacksquare$",
        "solution_he": "**חסרי הטיה:** $X\\sim\\text{Binomial}(n,p)$ ולכן $E[X]=np$. אז $E[\\hat{p}]=E[X/n]=np/n=p$, כלומר $\\text{Bias}(\\hat{p})=0$.\n\n**שונות:** $\\text{Var}(\\hat{p})=\\text{Var}(X/n)=np(1-p)/n^2=p(1-p)/n$.\n\n**בדיקה:** ככל ש-$n$ גדל, $\\text{Var}(\\hat{p})\\to 0$ — סימן לעקביות. $\\blacksquare$",
    },
}


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

    for sec in sections:
        if sec.get("kind") == "exercise_set":
            for ex in sec.get("exercises", []):
                patch = EXERCISE_SOLUTIONS.get(ex.get("id"))
                if patch:
                    ex["solution_en"] = patch["solution_en"]
                    ex["solution_he"] = patch["solution_he"]

    data["agent_hints"] = {
        "key_insights_en": [
            "MLE via log-likelihood: write L, take ln, set derivative to zero, verify maximum.",
            "Unbiasedness means E[T]=θ; MSE = Var + Bias² is the practical comparison tool.",
            "Sample variance uses n−1 (Bessel) for unbiased σ²; MLE divides by n and is biased low.",
        ],
        "key_insights_he": [
            "MLE דרך לוג-נראות: כתבו L, ln, אפסו נגזרת, אמתו מקסימום.",
            "חסרי הטיה: E[T]=θ; MSE = Var + Bias² לכלי השוואה.",
            "שונות מדגם: n−1 (בסל) ל-σ² חסר הטיה; MLE מחלק ב-n ומוטה למטה.",
        ],
        "common_misconceptions_en": [
            "Confusing unbiasedness with consistency — they are independent properties.",
            "Using n instead of n−1 in sample variance without understanding why.",
            "Skipping second-derivative or boundary check after solving ℓ′(θ)=0.",
        ],
        "common_misconceptions_he": [
            "בלבול חסרי הטיה עם עקביות — תכונות בלתי-תלויות.",
            "שימוש ב-n במקום n−1 בשונות מדגם בלי להבין למה.",
            "דילוג על בדיקת נגזרת שנייה או גבול אחרי ℓ′(θ)=0.",
        ],
    }
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
