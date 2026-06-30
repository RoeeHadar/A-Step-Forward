#!/usr/bin/env python3
"""Author 4 remaining stats/makhina lessons (part 2) and update lessons index for all 5 IDs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
INDEX_PATH = ROOT / "apps" / "web" / "src" / "lib" / "lessons-index.generated.json"


def _section(sid, title_en, title_he, body_en_md, body_he_md, level_min):
    return {
        "id": sid,
        "title_en": title_en,
        "title_he": title_he,
        "level_min": level_min,
        "body_en_md": body_en_md,
        "body_he_md": body_he_md,
    }


def _mcq(qid, body_en, body_he, options, expl_en, expl_he):
    return {
        "id": qid,
        "type": "mcq",
        "body_en": body_en,
        "body_he": body_he,
        "options": options,
        "explanation_en": expl_en,
        "explanation_he": expl_he,
    }


def _opts(items):
    return [{"id": oid, "text_en": en, "text_he": he, "correct": ok} for oid, en, he, ok in items]


INDEX_ENTRIES = {
    "sample_space": {
        "title_en": "Sample Space, Events & Probability Axioms",
        "title_he": "מרחב מדגם, אירועים ואקסיומות ההסתברות",
        "duration_min": 30,
        "subject": "statistics_probability",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "random_variables": {
        "title_en": "Random Variables & Probability Distributions",
        "title_he": "משתנים מקריים והתפלגויות",
        "duration_min": 35,
        "subject": "statistics_probability",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "sampling_estimation": {
        "title_en": "Sampling, Point Estimation & Confidence Intervals",
        "title_he": "דגימה, אמידת נקודה ורווח בר-סמך",
        "duration_min": 35,
        "subject": "statistics_probability",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "mechanics_makhina": {
        "title_en": "Mechanics: Motion, Forces & Newton's Laws",
        "title_he": "מכניקה: תנועה, כוחות וחוקי ניוטון",
        "duration_min": 35,
        "subject": "makhina_physics",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "energy_work_makhina": {
        "title_en": "Energy, Work & Power",
        "title_he": "אנרגיה, עבודה והספק",
        "duration_min": 30,
        "subject": "makhina_physics",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
}


REMAINING_LESSONS: list[dict] = [
    {
        "id": "random_variables",
        "type": "interactive",
        "subject": "statistics_probability",
        "title_en": INDEX_ENTRIES["random_variables"]["title_en"],
        "title_he": INDEX_ENTRIES["random_variables"]["title_he"],
        "duration_min": 35,
        "level_min": "university",
        "agent_hints": (
            "Students confuse PMF/PDF with probabilities of intervals — for continuous RVs, "
            "P(X = x) = 0; only intervals have positive probability. "
            "Emphasise that CDF is always non-decreasing with F(-inf)=0, F(inf)=1. "
            "Binomial vs Poisson: use Poisson when n is large and p is small with np moderate. "
            "For E[X] and Var, watch for linearity of expectation vs non-linearity of variance. "
            "Standard normal: always draw a sketch before reading z from tables."
        ),
        "sections": [
            _section(
                "rv_cdf",
                "Random Variables & the CDF",
                "משתנים מקריים ופונקציית ההתפלגות המצטברת",
                (
                    "A **random variable** $X$ is a function $X: \\Omega \\to \\mathbb{R}$ that assigns a "
                    "real number to each outcome.\n\n"
                    "- **Discrete:** $X$ takes countably many values (e.g. die roll, number of defects).\n"
                    "- **Continuous:** $X$ takes values in an interval (e.g. lifetime, height).\n\n"
                    "The **cumulative distribution function (CDF)** is:\n"
                    "$$\\boxed{F_X(x) = P(X \\leq x)}$$\n\n"
                    "**Properties:**\n"
                    "1. $0 \\leq F(x) \\leq 1$\n"
                    "2. $F$ is non-decreasing\n"
                    "3. $\\lim_{x \\to -\\infty} F(x) = 0$, $\\lim_{x \\to \\infty} F(x) = 1$\n\n"
                    "For discrete $X$: $F(x) = \\sum_{k \\leq x} p(k)$ (step function).\n\n"
                    "For continuous $X$: $F(x) = \\int_{-\\infty}^{x} f(t)\\,dt$ where $f$ is the PDF.\n\n"
                    "**Worked example:** $X$ = number of heads in 2 fair coin flips.\n"
                    "$p(0)=1/4$, $p(1)=1/2$, $p(2)=1/4$. Then $F(0)=1/4$, $F(1)=3/4$, $F(2)=1$."
                ),
                (
                    "**משתנה מקרי** $X$ הוא פונקציה $X: \\Omega \\to \\mathbb{R}$.\n\n"
                    "- **בדיד:** ערכים בני ספירה (למשל תוצאת קובייה).\n"
                    "- **רציף:** ערכים בקטע (למשל זמן חיים).\n\n"
                    "**פונקציית ההתפלגות המצטברת (CDF):**\n"
                    "$$\\boxed{F_X(x) = P(X \\leq x)}$$\n\n"
                    "**תכונות:** לא יורדת; $F(-\\infty)=0$, $F(\\infty)=1$.\n\n"
                    "בדיד: $F$ מדרגות. רציף: $F(x) = \\int_{-\\infty}^{x} f(t)\\,dt$.\n\n"
                    "**דוגמה:** $X$ = מספר ראשים ב-2 הטלות. $F(0)=1/4$, $F(1)=3/4$, $F(2)=1$."
                ),
                "university",
            ),
            _section(
                "discrete_distributions",
                "Discrete Distributions: Bernoulli, Binomial, Poisson",
                "התפלגויות בדידות: ברנולי, בינומית, פואסון",
                (
                    "**Bernoulli($p$):** one trial, success prob. $p$.\n"
                    "$$P(X=1)=p, \\quad P(X=0)=1-p$$\n\n"
                    "**Binomial($n,p$):** $n$ independent Bernoulli trials; $X$ = number of successes.\n"
                    "$$\\boxed{P(X=k) = \\binom{n}{k} p^k (1-p)^{n-k}, \\quad k=0,\\ldots,n}$$\n"
                    "$E[X]=np$, $\\text{Var}(X)=np(1-p)$.\n\n"
                    "**Worked example:** 10 items tested, each defective with $p=0.05$. "
                    "$P(X=2) = \\binom{10}{2}(0.05)^2(0.95)^8 \\approx 0.0746$.\n\n"
                    "**Poisson($\\lambda$):** models rare events in fixed interval; $np \\approx \\lambda$ when "
                    "$n$ large, $p$ small.\n"
                    "$$\\boxed{P(X=k) = e^{-\\lambda}\\frac{\\lambda^k}{k!}, \\quad k=0,1,2,\\ldots}$$\n"
                    "$E[X]=\\lambda$, $\\text{Var}(X)=\\lambda$.\n\n"
                    "**Example:** average 3 calls/hour $\\Rightarrow \\lambda=3$, "
                    "$P(X=0)=e^{-3} \\approx 0.0498$."
                ),
                (
                    "**ברנולי($p$):** ניסוי אחד, $P(X=1)=p$.\n\n"
                    "**בינומית($n,p$):** $n$ ניסויים בלתי-תלויים.\n"
                    "$$P(X=k) = \\binom{n}{k} p^k (1-p)^{n-k}$$\n"
                    "$E[X]=np$, $\\text{Var}(X)=np(1-p)$.\n\n"
                    "**דוגמה:** 10 פריטים, $p=0.05$. $P(X=2) \\approx 0.0746$.\n\n"
                    "**פואסון($\\lambda$):** אירועים נדירים; $E[X]=\\text{Var}(X)=\\lambda$.\n"
                    "$$P(X=k) = e^{-\\lambda}\\frac{\\lambda^k}{k!}$$"
                ),
                "university",
            ),
            _section(
                "continuous_distributions",
                "Continuous Distributions: Uniform & Exponential",
                "התפלגויות רציפות: אחידה ואקספוננציאלית",
                (
                    "A **PDF** $f(x)$ satisfies $f(x) \\geq 0$ and $\\int_{-\\infty}^{\\infty} f(x)\\,dx = 1$.\n"
                    "Then $P(a \\leq X \\leq b) = \\int_a^b f(x)\\,dx$.\n\n"
                    "**Uniform($a,b$):** constant density on $[a,b]$.\n"
                    "$$f(x) = \\frac{1}{b-a}, \\quad a \\leq x \\leq b$$\n"
                    "$E[X]=\\frac{a+b}{2}$, $\\text{Var}(X)=\\frac{(b-a)^2}{12}$.\n\n"
                    "**Exponential($\\lambda$):** waiting time; memoryless.\n"
                    "$$f(x) = \\lambda e^{-\\lambda x}, \\quad x \\geq 0$$\n"
                    "$E[X]=1/\\lambda$, $\\text{Var}(X)=1/\\lambda^2$.\n\n"
                    "**Worked example:** $X \\sim \\text{Uniform}(0,10)$.\n"
                    "$$P(3 \\leq X \\leq 7) = \\int_3^7 \\frac{1}{10}\\,dx = \\frac{4}{10} = 0.4.$$\n\n"
                    "**Exponential:** $\\lambda = 0.2$ per hour (mean wait 5 h).\n"
                    "$P(X > 3) = e^{-0.2 \\times 3} = e^{-0.6} \\approx 0.5488$."
                ),
                (
                    "**PDF** $f(x)$: $f \\geq 0$, $\\int f = 1$. $P(a \\leq X \\leq b) = \\int_a^b f$.\n\n"
                    "**אחידה($a,b$):** $f = 1/(b-a)$ על $[a,b]$.\n\n"
                    "**אקספוננציאלית($\\lambda$):** $f(x)=\\lambda e^{-\\lambda x}$, $x\\geq 0$; חסרת זיכרון.\n\n"
                    "**דוגמה:** $X \\sim U(0,10)$. $P(3 \\leq X \\leq 7) = 0.4$.\n\n"
                    "$\\lambda=0.2$: $P(X>3) = e^{-0.6} \\approx 0.5488$."
                ),
                "university",
            ),
            _section(
                "expectation_variance",
                "Expectation & Variance",
                "תוחלת ושונות",
                (
                    "**Discrete:**\n"
                    "$$\\boxed{E[X] = \\sum_x x\\,p(x), \\quad "
                    "\\text{Var}(X) = E[(X-\\mu)^2] = E[X^2] - (E[X])^2}$$\n\n"
                    "**Continuous:** replace sums by integrals.\n\n"
                    "**Linearity:** $E[aX + bY] = aE[X] + bE[Y]$ (always).\n"
                    "**Variance:** $\\text{Var}(aX+b) = a^2\\text{Var}(X)$; "
                    "$\\text{Var}(X+Y)=\\text{Var}(X)+\\text{Var}(Y)$ only if $X,Y$ independent.\n\n"
                    "**Worked example:** $X$ with $p(1)=0.2$, $p(3)=0.5$, $p(5)=0.3$.\n"
                    "$E[X] = 1(0.2)+3(0.5)+5(0.3) = 3.2$.\n"
                    "$E[X^2] = 1^2(0.2)+3^2(0.5)+5^2(0.3) = 11.6$.\n"
                    "$\\text{Var}(X) = 11.6 - 3.2^2 = 1.36$, so $\\sigma = 1.17$.\n\n"
                    "For $Y \\sim \\text{Binomial}(20, 0.4)$: $E[Y]=8$, $\\text{Var}(Y)=4.8$."
                ),
                (
                    "**בדיד:** $E[X]=\\sum x\\,p(x)$, $\\text{Var}(X)=E[X^2]-(E[X])^2$.\n\n"
                    "**רציף:** אינטגרלים במקום סכומים.\n\n"
                    "**לינאריות תוחלת:** $E[aX+bY]=aE[X]+bE[Y]$.\n\n"
                    "**דוגמה:** $p(1)=0.2$, $p(3)=0.5$, $p(5)=0.3$.\n"
                    "$E[X]=3.2$, $\\text{Var}(X)=1.36$.\n\n"
                    "בינומית$(20,0.4)$: $E=8$, $\\text{Var}=4.8$."
                ),
                "university",
            ),
            _section(
                "normal_distribution",
                "The Normal (Gaussian) Distribution",
                "התפלגות נורמלית (גאוס)",
                (
                    "$$X \\sim N(\\mu, \\sigma^2) \\quad \\Leftrightarrow \\quad "
                    "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} "
                    "\\exp\\!\\left(-\\frac{(x-\\mu)^2}{2\\sigma^2}\\right)$$\n\n"
                    "Bell-shaped, symmetric about $\\mu$; $\\sigma$ controls spread.\n\n"
                    "**Standard normal:** $Z \\sim N(0,1)$ with CDF $\\Phi(z)$.\n"
                    "Standardize: $Z = \\frac{X - \\mu}{\\sigma}$.\n\n"
                    "**68–95–99.7 rule:** about 68% within $\\mu \\pm \\sigma$, "
                    "95% within $\\mu \\pm 2\\sigma$, 99.7% within $\\mu \\pm 3\\sigma$.\n\n"
                    "**Worked example:** exam scores $X \\sim N(70, 100)$ (so $\\sigma=10$).\n"
                    "$$P(X \\geq 85) = P\\!\\left(Z \\geq \\frac{85-70}{10}\\right) "
                    "= P(Z \\geq 1.5) = 1 - \\Phi(1.5) \\approx 0.0668.$$\n\n"
                    "The normal is central in statistics via the CLT — sample means are approximately "
                    "normal for large $n$ regardless of the population shape."
                ),
                (
                    "$X \\sim N(\\mu, \\sigma^2)$ — צורת פעמון סימטרית.\n\n"
                    "**נורמל סטנדרטי:** $Z=(X-\\mu)/\\sigma \\sim N(0,1)$.\n\n"
                    "**כלל 68–95–99.7:** רוב הנתונים בתוך $\\mu \\pm \\sigma$, $\\pm 2\\sigma$, $\\pm 3\\sigma$.\n\n"
                    "**דוגמה:** $X \\sim N(70,100)$, $\\sigma=10$.\n"
                    "$P(X \\geq 85) = P(Z \\geq 1.5) \\approx 0.0668$.\n\n"
                    "הנורמל מרכזי בזכות מ.ג.מ."
                ),
                "university",
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "A discrete RV $X$ has PMF $p(0)=0.1$, $p(1)=0.4$, $p(2)=0.5$. What is $P(X \\leq 1)$?",
                "ל-$X$ בדיד: $p(0)=0.1$, $p(1)=0.4$, $p(2)=0.5$. מה $P(X \\leq 1)$?",
                _opts([
                    ("a", "$0.4$", "$0.4$", False),
                    ("b", "$0.5$", "$0.5$", True),
                    ("c", "$0.9$", "$0.9$", False),
                    ("d", "$0.1$", "$0.1$", False),
                ]),
                "$P(X \\leq 1) = p(0)+p(1) = 0.1+0.4 = 0.5$.",
                "$P(X \\leq 1) = 0.1+0.4 = 0.5$.",
            ),
            _mcq(
                "q2",
                "If $X \\sim \\text{Binomial}(10, 0.3)$, what is $P(X = 3)$?",
                "אם $X \\sim \\text{Binomial}(10, 0.3)$, מה $P(X = 3)$?",
                _opts([
                    ("a", "$\\binom{10}{3}(0.3)^3(0.7)^7 \\approx 0.267$", "$\\binom{10}{3}(0.3)^3(0.7)^7 \\approx 0.267$", True),
                    ("b", "$(0.3)^3(0.7)^7 \\approx 0.0022$", "$(0.3)^3(0.7)^7 \\approx 0.0022$", False),
                    ("c", "$\\binom{10}{3}(0.3)^7(0.7)^3$", "$\\binom{10}{3}(0.3)^7(0.7)^3$", False),
                    ("d", "$0.3$", "$0.3$", False),
                ]),
                "Binomial PMF: $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$. Here $n=10$, $k=3$, $p=0.3$.",
                "נוסחת בינומית: $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$ עם $n=10$, $k=3$, $p=0.3$.",
            ),
            _mcq(
                "q3",
                "Let $X \\sim \\text{Uniform}(2, 8)$. What is $P(4 \\leq X \\leq 6)$?",
                "יהי $X \\sim \\text{Uniform}(2, 8)$. מה $P(4 \\leq X \\leq 6)$?",
                _opts([
                    ("a", "$1/6$", "$1/6$", False),
                    ("b", "$1/3$", "$1/3$", True),
                    ("c", "$1/2$", "$1/2$", False),
                    ("d", "$2/3$", "$2/3$", False),
                ]),
                "Length of interval is $6-4=2$; total length is $8-2=6$. So $P = 2/6 = 1/3$.",
                "אורך הקטע $2$, אורך כולל $6$. $P = 2/6 = 1/3$.",
            ),
            _mcq(
                "q4",
                "Discrete $X$ has $p(0)=0.25$, $p(2)=0.75$. What is $E[X]$?",
                "ל-$X$ בדיד: $p(0)=0.25$, $p(2)=0.75$. מה $E[X]$?",
                _opts([
                    ("a", "$1.0$", "$1.0$", False),
                    ("b", "$1.5$", "$1.5$", True),
                    ("c", "$2.0$", "$2.0$", False),
                    ("d", "$0.75$", "$0.75$", False),
                ]),
                "$E[X] = 0(0.25) + 2(0.75) = 1.5$.",
                "$E[X] = 0(0.25) + 2(0.75) = 1.5$.",
            ),
            _mcq(
                "q5",
                "If $Z \\sim N(0,1)$, what is $P(Z \\leq -1.96)$ (approximately)?",
                "אם $Z \\sim N(0,1)$, מה $P(Z \\leq -1.96)$ (בקירוב)?",
                _opts([
                    ("a", "$0.975$", "$0.975$", False),
                    ("b", "$0.025$", "$0.025$", True),
                    ("c", "$0.05$", "$0.05$", False),
                    ("d", "$0.5$", "$0.5$", False),
                ]),
                "By symmetry, $P(Z \\leq -1.96) = P(Z \\geq 1.96) = 0.025$ (two-tailed 5% tail beyond $\\pm 1.96$).",
                "לפי סימטריה, $P(Z \\leq -1.96) = 0.025$.",
            ),
        ],
    },
    {
        "id": "sampling_estimation",
        "type": "interactive",
        "subject": "statistics_probability",
        "title_en": INDEX_ENTRIES["sampling_estimation"]["title_en"],
        "title_he": INDEX_ENTRIES["sampling_estimation"]["title_he"],
        "duration_min": 35,
        "level_min": "university",
        "agent_hints": (
            "The CLT applies to the sample mean, not individual observations — and requires "
            "independent samples with finite variance. "
            "Students confuse standard deviation with standard error: SE = sigma/sqrt(n). "
            "For CI interpretation, mu is fixed — the interval is random. "
            "Sample-size formulas for proportions need a conservative p-hat = 0.5 when unknown. "
            "Connect to the confidence_intervals lesson for z vs t procedures."
        ),
        "sections": [
            _section(
                "population_sample",
                "Population vs Sample",
                "אוכלוסייה לעומת מדגם",
                (
                    "A **population** is the entire group of interest (all students, all manufactured parts). "
                    "A **sample** is a subset drawn from the population.\n\n"
                    "**Parameters** (unknown, fixed): $\\mu$ (mean), $\\sigma$ (std dev), $p$ (proportion).\n"
                    "**Statistics** (computed from data, random): $\\bar{X}$, $s$, $\\hat{p}$.\n\n"
                    "**Sampling distribution:** the probability distribution of a statistic over repeated samples.\n\n"
                    "**Example:** population exam scores with $\\mu=72$, $\\sigma=15$. "
                    "One sample of $n=25$ gives $\\bar{x}=68.4$ — this is one realization of $\\bar{X}$.\n\n"
                    "**Bias:** a statistic is **unbiased** if $E[\\hat{\\theta}] = \\theta$. "
                    "The sample mean is unbiased for $\\mu$; $s^2$ (with $n-1$) is unbiased for $\\sigma^2$."
                ),
                (
                    "**אוכלוסייה** — כל הקבוצה; **מדגם** — תת-קבוצה.\n\n"
                    "**פרמטרים:** $\\mu$, $\\sigma$, $p$. **סטטיסטיקות:** $\\bar{X}$, $s$, $\\hat{p}$.\n\n"
                    "**התפלגות דגימה:** התפלגות הסטטיסטיקה על דגימות חוזרות.\n\n"
                    "**דוגמה:** $\\mu=72$, $\\sigma=15$; מדגם $n=25$ נותן $\\bar{x}=68.4$.\n\n"
                    "$\\bar{X}$ הוא אמוד לא-מוטה ל-$\\mu$."
                ),
                "university",
            ),
            _section(
                "clt",
                "Central Limit Theorem",
                "משפט הגבול המרכזי",
                (
                    "Let $X_1, \\ldots, X_n$ be i.i.d. with mean $\\mu$ and variance $\\sigma^2$ (finite). "
                    "Then for large $n$:\n"
                    "$$\\boxed{\\bar{X} \\approx N\\!\\left(\\mu, \\frac{\\sigma^2}{n}\\right)}$$\n\n"
                    "Equivalently:\n"
                    "$$\\frac{\\bar{X} - \\mu}{\\sigma/\\sqrt{n}} \\approx N(0,1)$$\n\n"
                    "**Key points:**\n"
                    "- Applies to **sample means**, not single observations\n"
                    "- Population can be any shape (roughly $n \\geq 30$ is a common rule)\n"
                    "- Spread of $\\bar{X}$ shrinks as $1/\\sqrt{n}$\n\n"
                    "**Example:** skewed service times with $\\mu=8$ min, $\\sigma=4$, $n=36$.\n"
                    "$\\bar{X}$ is approximately $N(8, 16/36) = N(8, 0.444)$ — std error $= 4/6 \\approx 0.67$ min."
                ),
                (
                    "ל-$X_1,\\ldots,X_n$ בלתי-תלויים עם $\\mu$ ו-$\\sigma^2$ סופית, ל-$n$ גדול:\n"
                    "$$\\bar{X} \\approx N\\!\\left(\\mu, \\frac{\\sigma^2}{n}\\right)$$\n\n"
                    "**חשוב:** חל על **ממוצעי מדגם**, לא על תצפית בודדת.\n\n"
                    "**דוגמה:** $n=36$, $\\sigma=4$ $\\Rightarrow$ SE $= 4/6 \\approx 0.67$."
                ),
                "university",
            ),
            _section(
                "point_estimation",
                "Point Estimation",
                "אמידת נקודה",
                (
                    "A **point estimate** $\\hat{\\theta}$ is a single number summarizing a parameter.\n\n"
                    "| Parameter | Estimator |\n|---|---|\n"
                    "| $\\mu$ | $\\bar{X} = \\frac{1}{n}\\sum X_i$ |\n"
                    "| $\\sigma^2$ | $s^2 = \\frac{1}{n-1}\\sum(X_i-\\bar{X})^2$ |\n"
                    "| $p$ | $\\hat{p} = \\frac{\\text{# successes}}{n}$ |\n\n"
                    "**Desirable properties:**\n"
                    "- **Unbiased:** $E[\\hat{\\theta}] = \\theta$\n"
                    "- **Consistent:** $\\hat{\\theta} \\to \\theta$ as $n \\to \\infty$\n"
                    "- **Efficient:** smallest variance among unbiased estimators\n\n"
                    "**Worked example:** 400 voters sampled; 228 support a candidate.\n"
                    "$\\hat{p} = 228/400 = 0.57$ estimates the population proportion $p$."
                ),
                (
                    "**אמד נקודתי** $\\hat{\\theta}$ — מספר יחיד.\n\n"
                    "$\\mu$ $\\to$ $\\bar{X}$; $p$ $\\to$ $\\hat{p}$.\n\n"
                    "**תכונות:** לא-מוטה, עקבי, יעיל.\n\n"
                    "**דוגמה:** 228 מתוך 400 $\\Rightarrow$ $\\hat{p}=0.57$."
                ),
                "university",
            ),
            _section(
                "ci_mean",
                "Confidence Interval for the Mean",
                "רווח סמך לממוצע",
                (
                    "When $\\sigma$ is known (or $n$ large with $s$):\n"
                    "$$\\boxed{\\bar{x} \\pm z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}}}$$\n\n"
                    "When $\\sigma$ unknown (normal population):\n"
                    "$$\\boxed{\\bar{x} \\pm t_{\\alpha/2,\\,n-1} \\cdot \\frac{s}{\\sqrt{n}}}$$\n\n"
                    "**Standard error of the mean:** $\\text{SE} = s/\\sqrt{n}$.\n\n"
                    "**Worked example:** $n=16$, $\\bar{x}=50$, $s=8$, 95% CI, $t_{0.025,15}=2.131$.\n"
                    "$$50 \\pm 2.131 \\cdot \\frac{8}{\\sqrt{16}} = 50 \\pm 4.26 = (45.74,\\; 54.26).$$"
                ),
                (
                    "$\\sigma$ ידוע: $\\bar{x} \\pm z_{\\alpha/2} \\cdot \\sigma/\\sqrt{n}$.\n\n"
                    "$\\sigma$ לא ידוע: $\\bar{x} \\pm t_{\\alpha/2,n-1} \\cdot s/\\sqrt{n}$.\n\n"
                    "**שגיאת תקן:** $s/\\sqrt{n}$.\n\n"
                    "**דוגמה:** $n=16$, $\\bar{x}=50$, $s=8$ $\\Rightarrow$ $(45.74, 54.26)$."
                ),
                "university",
            ),
            _section(
                "ci_proportion",
                "Confidence Interval for a Proportion & Sample Size",
                "רווח סמך לפרופורציה וגודל מדגם",
                (
                    "For large $n$, an approximate $(1-\\alpha)$ CI for $p$ is:\n"
                    "$$\\boxed{\\hat{p} \\pm z_{\\alpha/2} \\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}}$$\n\n"
                    "**Sample size** for estimating $p$ within margin $E$ at confidence $1-\\alpha$:\n"
                    "$$\\boxed{n \\geq \\left(\\frac{z_{\\alpha/2}}{E}\\right)^2 \\hat{p}(1-\\hat{p})}$$\n\n"
                    "If $\\hat{p}$ unknown, use conservative $\\hat{p}=0.5$ (maximizes $p(1-p)$).\n\n"
                    "**Worked example:** $\\hat{p}=0.57$, $n=400$, 95% CI ($z=1.96$):\n"
                    "$$0.57 \\pm 1.96\\sqrt{\\frac{0.57 \\cdot 0.43}{400}} "
                    "= 0.57 \\pm 0.0485 = (0.521,\\; 0.619).$$\n\n"
                    "For $E=0.03$ at 95% with unknown $p$: "
                    "$n \\geq (1.96/0.03)^2 \\cdot 0.25 \\approx 1068$."
                ),
                (
                    "רווח סמך ל-$p$: $\\hat{p} \\pm z_{\\alpha/2}\\sqrt{\\hat{p}(1-\\hat{p})/n}$.\n\n"
                    "גודל מדגם: $n \\geq (z_{\\alpha/2}/E)^2 \\hat{p}(1-\\hat{p})$; "
                    "אם $p$ לא ידוע — $\\hat{p}=0.5$.\n\n"
                    "**דוגמה:** $\\hat{p}=0.57$, $n=400$ $\\Rightarrow$ $(0.521, 0.619)$."
                ),
                "university",
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "The Central Limit Theorem states that for large $n$, the sample mean $\\bar{X}$ is approximately:",
                "משפט הגבול המרכזי קובע של-$n$ גדול, ממוצע המדגם $\\bar{X}$ הוא בקירוב:",
                _opts([
                    ("a", "Normal with mean $\\mu$ and variance $\\sigma^2$", "נורמלי עם ממוצע $\\mu$ ושונות $\\sigma^2$", False),
                    ("b", "Normal with mean $\\mu$ and variance $\\sigma^2/n$", "נורמלי עם ממוצע $\\mu$ ושונות $\\sigma^2/n$", True),
                    ("c", "Same distribution as the population", "באותה התפלגות כמו האוכלוסייה", False),
                    ("d", "Always exactly normal for any $n$", "תמיד נורמלי בדיוק לכל $n$", False),
                ]),
                "CLT: $\\bar{X} \\approx N(\\mu, \\sigma^2/n)$. Individual $X_i$ keep population variance $\\sigma^2$.",
                "מ.ג.מ.: $\\bar{X} \\approx N(\\mu, \\sigma^2/n)$.",
            ),
            _mcq(
                "q2",
                "A sample of $n=49$ has $s=14$. The standard error of the mean is:",
                "מדגם $n=49$ עם $s=14$. שגיאת התקן של הממוצע:",
                _opts([
                    ("a", "$14$", "$14$", False),
                    ("b", "$7$", "$7$", False),
                    ("c", "$2$", "$2$", True),
                    ("d", "$98$", "$98$", False),
                ]),
                "$\\text{SE} = s/\\sqrt{n} = 14/\\sqrt{49} = 14/7 = 2$.",
                "$\\text{SE} = 14/\\sqrt{49} = 2$.",
            ),
            _mcq(
                "q3",
                "Given $n=25$, $\\bar{x}=100$, $\\sigma=20$, construct a 95% CI for $\\mu$ ($z_{0.025}=1.96$):",
                "נתון $n=25$, $\\bar{x}=100$, $\\sigma=20$. רווח סמך 95% ל-$\\mu$ ($z=1.96$):",
                _opts([
                    ("a", "$(92.16,\\; 107.84)$", "$(92.16,\\; 107.84)$", True),
                    ("b", "$(80,\\; 120)$", "$(80,\\; 120)$", False),
                    ("c", "$(96,\\; 104)$", "$(96,\\; 104)$", False),
                    ("d", "$(84.08,\\; 115.92)$", "$(84.08,\\; 115.92)$", False),
                ]),
                "$E = 1.96 \\cdot 20/\\sqrt{25} = 1.96 \\cdot 4 = 7.84$. CI: $(100 \\pm 7.84)$.",
                "$E = 1.96 \\cdot 4 = 7.84$. רווח: $(92.16, 107.84)$.",
            ),
            _mcq(
                "q4",
                "A 95% confidence interval for $\\mu$ is $(45, 55)$. Which statement is correct?",
                "רווח סמך 95% ל-$\\mu$ הוא $(45, 55)$. איזו טענה נכונה?",
                _opts([
                    ("a", "There is a 95% probability that $\\mu$ is between 45 and 55.", "יש 95% הסתברות ש-$\\mu$ בין 45 ל-55.", False),
                    ("b", "95% of sample means fall between 45 and 55.", "95% ממוצעי המדגם בין 45 ל-55.", False),
                    ("c", "If we repeated sampling, 95% of such intervals would contain $\\mu$.", "אם נחזור על הדגימה, 95% מהקטעים יכילו את $\\mu$.", True),
                    ("d", "$\\mu$ is definitely between 45 and 55.", "$\\mu$ בהחלט בין 45 ל-55.", False),
                ]),
                "Frequentist interpretation: the procedure captures $\\mu$ in 95% of repeated samples; $\\mu$ is fixed.",
                "פרשנות תדרתנית: 95% מהקטעים יכילו את $\\mu$; $\\mu$ קבוע.",
            ),
            _mcq(
                "q5",
                "For a 95% CI on a proportion with margin of error $E=0.04$ and unknown $p$, the minimum $n$ (using $p=0.5$) is approximately:",
                "לרווח סמך 95% לפרופורציה עם $E=0.04$ ו-$p$ לא ידוע ($p=0.5$), $n$ המינימלי בקירוב:",
                _opts([
                    ("a", "$601$", "$601$", True),
                    ("b", "$400$", "$400$", False),
                    ("c", "$100$", "$100$", False),
                    ("d", "$2401$", "$2401$", False),
                ]),
                "$n \\geq (1.96/0.04)^2 \\cdot 0.25 = 49^2 \\cdot 0.25 = 600.25$, so $n \\geq 601$.",
                "$n \\geq (1.96/0.04)^2 \\cdot 0.25 \\approx 601$.",
            ),
        ],
    },
    {
        "id": "mechanics_makhina",
        "type": "interactive",
        "subject": "makhina_physics",
        "title_en": INDEX_ENTRIES["mechanics_makhina"]["title_en"],
        "title_he": INDEX_ENTRIES["mechanics_makhina"]["title_he"],
        "duration_min": 35,
        "level_min": "makhina",
        "agent_hints": (
            "Makhina learners often mix up distance vs displacement and speed vs velocity — "
            "always ask 'scalar or vector?' before writing an equation. "
            "For projectiles, split into horizontal (constant v) and vertical (constant a = -g) components. "
            "Free-body diagrams before F=ma every time. "
            "On inclines, resolve weight into parallel/perpendicular components. "
            "Atwood: treat each mass separately; same acceleration magnitude, opposite directions."
        ),
        "sections": [
            _section(
                "kinematics_1d",
                "One-Dimensional Kinematics",
                "קינמטיקה חד-ממדית",
                (
                    "Welcome to mechanics! We describe **motion** before asking **why** things move.\n\n"
                    "**Scalars:** distance, speed. **Vectors:** displacement $\\vec{s}$, velocity $\\vec{v}$, "
                    "acceleration $\\vec{a}$.\n\n"
                    "For constant acceleration along a line:\n"
                    "$$v = v_0 + at$$\n"
                    "$$s = v_0 t + \\tfrac{1}{2}at^2$$\n"
                    "$$v^2 = v_0^2 + 2as$$\n\n"
                    "**Worked example:** A car starts from rest ($v_0=0$) and accelerates at $a=3\\,\\text{m/s}^2$ "
                    "for $t=4\\,\\text{s}$.\n"
                    "$v = 3 \\cdot 4 = 12\\,\\text{m/s}$; "
                    "$s = \\tfrac{1}{2}(3)(16) = 24\\,\\text{m}$.\n\n"
                    "Always pick a **positive direction** and stick to sign conventions."
                ),
                (
                    "במכניקה מתארים **תנועה** לפני ששואלים **למה**.\n\n"
                    "**מרחק, מהירות** (ללא כיוון); **מיקום, מהירות, תאוצה** (עם כיוון).\n\n"
                    "תאוצה קבועה:\n"
                    "$$v = v_0 + at, \\quad s = v_0 t + \\tfrac{1}{2}at^2, \\quad v^2 = v_0^2 + 2as$$\n\n"
                    "**דוגמה:** $v_0=0$, $a=3\\,\\text{m/s}^2$, $t=4\\,\\text{s}$ $\\Rightarrow$ "
                    "$v=12\\,\\text{m/s}$, $s=24\\,\\text{m}$."
                ),
                "makhina",
            ),
            _section(
                "projectiles_2d",
                "2D Motion: Vectors & Projectiles",
                "תנועה דו-ממדית: וקטורים וזריקות",
                (
                    "Break 2D motion into **independent components**.\n\n"
                    "For a projectile launched at speed $v_0$ and angle $\\theta$ above horizontal "
                    "(neglect air resistance, $g=9.8\\,\\text{m/s}^2$):\n"
                    "$$v_{0x} = v_0\\cos\\theta, \\quad v_{0y} = v_0\\sin\\theta$$\n"
                    "$$x = v_{0x} t, \\quad y = v_{0y} t - \\tfrac{1}{2}gt^2$$\n\n"
                    "**Time of flight** (launch and land at same height):\n"
                    "$$T = \\frac{2v_0\\sin\\theta}{g}$$\n\n"
                    "**Range:**\n"
                    "$$R = \\frac{v_0^2\\sin(2\\theta)}{g}$$\n\n"
                    "**Example:** $v_0=20\\,\\text{m/s}$, $\\theta=30°$ ($\\sin 30°=0.5$, $\\sin 60°=0.866$).\n"
                    "$R = \\frac{400 \\cdot 0.866}{9.8} \\approx 35.3\\,\\text{m}$."
                ),
                (
                    "מפרקים תנועה ל**רכיבים בלתי-תלויים**.\n\n"
                    "זריקה בזווית $\\theta$:\n"
                    "$$R = \\frac{v_0^2\\sin(2\\theta)}{g}$$\n\n"
                    "**דוגמה:** $v_0=20\\,\\text{m/s}$, $\\theta=30°$ $\\Rightarrow$ $R \\approx 35.3\\,\\text{m}$."
                ),
                "makhina",
            ),
            _section(
                "newton_laws",
                "Newton's Three Laws",
                "שלושת חוקי ניוטון",
                (
                    "**First law (inertia):** If $\\sum \\vec{F} = 0$, velocity is constant (including zero).\n\n"
                    "**Second law:**\n"
                    "$$\\boxed{\\sum \\vec{F} = m\\vec{a}}$$\n"
                    "Force in newtons (N), mass in kg, acceleration in m/s².\n\n"
                    "**Third law:** If body A exerts force $\\vec{F}$ on B, then B exerts $-\\vec{F}$ on A. "
                    "Action–reaction pairs act on **different** bodies.\n\n"
                    "**Common mistake:** weight $\\vec{W}=m\\vec{g}$ and normal force are NOT an action–reaction pair "
                    "(they act on the same object).\n\n"
                    "**Example:** $m=5\\,\\text{kg}$ pushed with net force $F=20\\,\\text{N}$.\n"
                    "$a = F/m = 4\\,\\text{m/s}^2$."
                ),
                (
                    "**חוק ראשון:** $\\sum \\vec{F}=0$ $\\Rightarrow$ מהירות קבועה.\n\n"
                    "**חוק שני:** $\\sum \\vec{F} = m\\vec{a}$.\n\n"
                    "**חוק שלישי:** כוחות פעולה-תגובה על **גופים שונים**.\n\n"
                    "**דוגמה:** $m=5\\,\\text{kg}$, $F=20\\,\\text{N}$ $\\Rightarrow$ $a=4\\,\\text{m/s}^2$."
                ),
                "makhina",
            ),
            _section(
                "fma_applications",
                "Applying $F=ma$: Incline & Atwood Machine",
                "יישום $F=ma$: משופע ומכונת Atwood",
                (
                    "**Incline** at angle $\\theta$: resolve weight $mg$ into\n"
                    "- parallel: $mg\\sin\\theta$ (down the slope)\n"
                    "- perpendicular: $mg\\cos\\theta$ (into the surface)\n\n"
                    "Block sliding without friction: $ma = mg\\sin\\theta$ $\\Rightarrow$ $a = g\\sin\\theta$.\n\n"
                    "**Atwood machine:** two masses $m_1 > m_2$ connected over a pulley.\n"
                    "Net pulling force along rope: $(m_1 - m_2)g$; total inertia: $m_1 + m_2$.\n"
                    "$$a = \\frac{(m_1 - m_2)g}{m_1 + m_2}$$\n\n"
                    "**Worked example:** $m_1=5\\,\\text{kg}$, $m_2=3\\,\\text{kg}$, $g=10\\,\\text{m/s}^2$.\n"
                    "$a = \\frac{2 \\cdot 10}{8} = 2.5\\,\\text{m/s}^2$.\n"
                    "Tension: $T = m_2(g+a) = 3(12.5) = 37.5\\,\\text{N}$."
                ),
                (
                    "**משופע** $\\theta$: $mg\\sin\\theta$ לאורך, $mg\\cos\\theta$ ניצב.\n\n"
                    "ללא חיכוך: $a = g\\sin\\theta$.\n\n"
                    "**Atwood:** $a = \\frac{(m_1-m_2)g}{m_1+m_2}$.\n\n"
                    "**דוגמה:** $m_1=5$, $m_2=3$, $g=10$ $\\Rightarrow$ $a=2.5\\,\\text{m/s}^2$, $T=37.5\\,\\text{N}$."
                ),
                "makhina",
            ),
            _section(
                "circular_motion",
                "Uniform Circular Motion",
                "תנועה מעגלית אחידה",
                (
                    "In uniform circular motion, speed is constant but **velocity direction changes** — "
                    "so there is centripetal acceleration toward the center:\n"
                    "$$\\boxed{a_c = \\frac{v^2}{r} = \\omega^2 r}$$\n\n"
                    "Centripetal force (net inward force):\n"
                    "$$\\boxed{F_c = \\frac{mv^2}{r} = m\\omega^2 r}$$\n\n"
                    "Period: $T = 2\\pi r / v = 2\\pi/\\omega$.\n\n"
                    "**Example:** $m=2\\,\\text{kg}$ on a string, $r=0.5\\,\\text{m}$, $v=4\\,\\text{m/s}$.\n"
                    "$F_c = 2 \\cdot 16 / 0.5 = 64\\,\\text{N}$ (tension provides this force).\n\n"
                    "Centrifugal force is **not** a real force — it is a fictitious effect in a rotating frame."
                ),
                (
                    "בתנועה מעגלית: $a_c = v^2/r$ לכיוון המרכז.\n\n"
                    "$F_c = mv^2/r$.\n\n"
                    "**דוגמה:** $m=2\\,\\text{kg}$, $r=0.5\\,\\text{m}$, $v=4\\,\\text{m/s}$ $\\Rightarrow$ $F_c=64\\,\\text{N}$."
                ),
                "makhina",
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "A body starts from rest with constant acceleration $a=2\\,\\text{m/s}^2$. What is its speed after $t=5\\,\\text{s}$?",
                "גוף מתחיל ממנוחה עם $a=2\\,\\text{m/s}^2$. מה המהירות אחרי $t=5\\,\\text{s}$?",
                _opts([
                    ("a", "$5\\,\\text{m/s}$", "$5\\,\\text{m/s}$", False),
                    ("b", "$10\\,\\text{m/s}$", "$10\\,\\text{m/s}$", True),
                    ("c", "$25\\,\\text{m/s}$", "$25\\,\\text{m/s}$", False),
                    ("d", "$12.5\\,\\text{m/s}$", "$12.5\\,\\text{m/s}$", False),
                ]),
                "$v = v_0 + at = 0 + 2(5) = 10\\,\\text{m/s}$.",
                "$v = 2 \\cdot 5 = 10\\,\\text{m/s}$.",
            ),
            _mcq(
                "q2",
                "A projectile is launched with $v_0=10\\,\\text{m/s}$ at $\\theta=45°$ ($g=10\\,\\text{m/s}^2$). "
                "What is the maximum horizontal range?",
                "זריקה ב-$v_0=10\\,\\text{m/s}$, $\\theta=45°$ ($g=10$). מה הטווח האופקי?",
                _opts([
                    ("a", "$5\\,\\text{m}$", "$5\\,\\text{m}$", False),
                    ("b", "$10\\,\\text{m}$", "$10\\,\\text{m}$", True),
                    ("c", "$20\\,\\text{m}$", "$20\\,\\text{m}$", False),
                    ("d", "$7.07\\,\\text{m}$", "$7.07\\,\\text{m}$", False),
                ]),
                "$R = v_0^2\\sin(2\\theta)/g = 100 \\cdot 1 / 10 = 10\\,\\text{m}$ (maximum at $45°$).",
                "$R = 100/10 = 10\\,\\text{m}$.",
            ),
            _mcq(
                "q3",
                "A net force of $15\\,\\text{N}$ acts on a $3\\,\\text{kg}$ mass. The acceleration is:",
                "כוח שקול $15\\,\\text{N}$ על מסה $3\\,\\text{kg}$. התאוצה:",
                _opts([
                    ("a", "$45\\,\\text{m/s}^2$", "$45\\,\\text{m/s}^2$", False),
                    ("b", "$5\\,\\text{m/s}^2$", "$5\\,\\text{m/s}^2$", True),
                    ("c", "$12\\,\\text{m/s}^2$", "$12\\,\\text{m/s}^2$", False),
                    ("d", "$0.2\\,\\text{m/s}^2$", "$0.2\\,\\text{m/s}^2$", False),
                ]),
                "Newton's 2nd law: $a = F/m = 15/3 = 5\\,\\text{m/s}^2$.",
                "$a = F/m = 5\\,\\text{m/s}^2$.",
            ),
            _mcq(
                "q4",
                "In an Atwood machine, $m_1=6\\,\\text{kg}$ and $m_2=2\\,\\text{kg}$ ($g=10\\,\\text{m/s}^2$). "
                "What is the acceleration magnitude?",
                "ב-Atwood: $m_1=6\\,\\text{kg}$, $m_2=2\\,\\text{kg}$ ($g=10$). גודל התאוצה:",
                _opts([
                    ("a", "$10\\,\\text{m/s}^2$", "$10\\,\\text{m/s}^2$", False),
                    ("b", "$5\\,\\text{m/s}^2$", "$5\\,\\text{m/s}^2$", True),
                    ("c", "$2.5\\,\\text{m/s}^2$", "$2.5\\,\\text{m/s}^2$", False),
                    ("d", "$8\\,\\text{m/s}^2$", "$8\\,\\text{m/s}^2$", False),
                ]),
                "$a = (m_1-m_2)g/(m_1+m_2) = 4 \\cdot 10 / 8 = 5\\,\\text{m/s}^2$.",
                "$a = 40/8 = 5\\,\\text{m/s}^2$.",
            ),
            _mcq(
                "q5",
                "A $4\\,\\text{kg}$ object moves in a circle of radius $2\\,\\text{m}$ at speed $3\\,\\text{m/s}$. "
                "The centripetal force is:",
                "גוף $4\\,\\text{kg}$ במעגל $r=2\\,\\text{m}$, $v=3\\,\\text{m/s}$. כוח הצנטריפטלי:",
                _opts([
                    ("a", "$6\\,\\text{N}$", "$6\\,\\text{N}$", False),
                    ("b", "$12\\,\\text{N}$", "$12\\,\\text{N}$", False),
                    ("c", "$18\\,\\text{N}$", "$18\\,\\text{N}$", True),
                    ("d", "$36\\,\\text{N}$", "$36\\,\\text{N}$", False),
                ]),
                "$F_c = mv^2/r = 4 \\cdot 9 / 2 = 18\\,\\text{N}$.",
                "$F_c = 36/2 = 18\\,\\text{N}$.",
            ),
        ],
    },
    {
        "id": "energy_work_makhina",
        "type": "interactive",
        "subject": "makhina_physics",
        "title_en": INDEX_ENTRIES["energy_work_makhina"]["title_en"],
        "title_he": INDEX_ENTRIES["energy_work_makhina"]["title_he"],
        "duration_min": 30,
        "level_min": "makhina",
        "agent_hints": (
            "Work requires displacement along the force component: W = F d cos(theta). "
            "Students forget that normal force and centripetal force do zero work. "
            "Work-energy theorem links net work to Delta KE — friction removes mechanical energy. "
            "For conservation problems, pick two states and set E1 = E2; only include non-conservative "
            "work if friction/external forces present. Power is rate of energy transfer: P = W/t = Fv."
        ),
        "sections": [
            _section(
                "work",
                "Work",
                "עבודה",
                (
                    "**Work** is energy transferred by a force through displacement:\n"
                    "$$\\boxed{W = F d \\cos\\theta = \\vec{F} \\cdot \\vec{d}}$$\n\n"
                    "$\\theta$ = angle between force and displacement.\n\n"
                    "- Force **parallel** to motion: $W = Fd$ (maximum)\n"
                    "- Force **perpendicular** to motion: $W = 0$ (e.g. normal force, centripetal force)\n\n"
                    "**Units:** joule (J) = N·m.\n\n"
                    "**Example:** Push a box with $F=50\\,\\text{N}$ for $d=6\\,\\text{m}$ along the floor "
                    "($\\theta=0°$): $W = 50 \\cdot 6 = 300\\,\\text{J}$.\n\n"
                    "If you pull at $60°$ above horizontal with the same $F=50\\,\\text{N}$ over $6\\,\\text{m}$: "
                    "$W = 50 \\cdot 6 \\cdot \\cos 60° = 150\\,\\text{J}$."
                ),
                (
                    "**עבודה:** $W = F d \\cos\\theta$.\n\n"
                    "כוח ניצב לתזוזה — עבודה 0.\n\n"
                    "**דוגמה:** $F=50\\,\\text{N}$, $d=6\\,\\text{m}$ $\\Rightarrow$ $W=300\\,\\text{J}$."
                ),
                "makhina",
            ),
            _section(
                "work_energy_theorem",
                "Kinetic Energy & the Work–Energy Theorem",
                "אנרגיה קינטית ומשפט העבודה-אנרגיה",
                (
                    "**Kinetic energy:**\n"
                    "$$\\boxed{KE = \\tfrac{1}{2}mv^2}$$\n\n"
                    "**Work–energy theorem:** the net work done on an object equals its change in kinetic energy:\n"
                    "$$\\boxed{W_{\\text{net}} = \\Delta KE = \\tfrac{1}{2}mv^2 - \\tfrac{1}{2}mv_0^2}$$\n\n"
                    "**Example:** $m=2\\,\\text{kg}$ starts at rest; net work $W=100\\,\\text{J}$.\n"
                    "$100 = \\tfrac{1}{2}(2)v^2 \\Rightarrow v^2 = 100 \\Rightarrow v = 10\\,\\text{m/s}$.\n\n"
                    "This is often faster than kinematics when forces vary or distance is known but time is not."
                ),
                (
                    "$KE = \\tfrac{1}{2}mv^2$.\n\n"
                    "משפט עבודה-אנרגיה: $W_{\\text{net}} = \\Delta KE$.\n\n"
                    "**דוגמה:** $m=2\\,\\text{kg}$, $W=100\\,\\text{J}$ $\\Rightarrow$ $v=10\\,\\text{m/s}$."
                ),
                "makhina",
            ),
            _section(
                "potential_energy",
                "Potential Energy",
                "אנרגיה פוטנציאלית",
                (
                    "**Gravitational PE** (near Earth, reference $h=0$ at chosen level):\n"
                    "$$\\boxed{PE = mgh}$$\n\n"
                    "Only **changes** in PE matter physically: $\\Delta PE = mg\\Delta h$.\n\n"
                    "**Elastic PE** (spring, Hooke's law $F=kx$):\n"
                    "$$PE_{\\text{spring}} = \\tfrac{1}{2}kx^2$$\n\n"
                    "**Example:** $m=3\\,\\text{kg}$ lifted $h=4\\,\\text{m}$ ($g=10\\,\\text{m/s}^2$).\n"
                    "$\\Delta PE = 3 \\cdot 10 \\cdot 4 = 120\\,\\text{J}$.\n\n"
                    "Conservative forces (gravity, spring) allow us to store and recover mechanical energy."
                ),
                (
                    "אנרגיה פוטנציאלית כבידתית: $PE = mgh$.\n\n"
                    "קפיץ: $PE = \\tfrac{1}{2}kx^2$.\n\n"
                    "**דוגמה:** $m=3\\,\\text{kg}$, $h=4\\,\\text{m}$ $\\Rightarrow$ $\\Delta PE = 120\\,\\text{J}$."
                ),
                "makhina",
            ),
            _section(
                "conservation_energy",
                "Conservation of Mechanical Energy",
                "שימור אנרגיה מכנית",
                (
                    "When only **conservative** forces do work (no friction, no external engines):\n"
                    "$$\\boxed{E = KE + PE = \\text{constant}}$$\n\n"
                    "At two instants: $KE_1 + PE_1 = KE_2 + PE_2$.\n\n"
                    "**With friction:** $W_{\\text{friction}} = \\Delta E_{\\text{mech}} < 0$ (energy dissipated as heat).\n\n"
                    "**Worked example:** ball $m=0.5\\,\\text{kg}$ dropped from $h=20\\,\\text{m}$ ($g=10$). "
                    "Speed just before ground (ignore air):\n"
                    "$mgh = \\tfrac{1}{2}mv^2 \\Rightarrow v = \\sqrt{2gh} = \\sqrt{400} = 20\\,\\text{m/s}$.\n\n"
                    "Same result from kinematics — conservation is a powerful shortcut."
                ),
                (
                    "ללא חיכוך: $KE + PE = \\text{קבוע}$.\n\n"
                    "עם חיכוך: אנרגיה מכנית יורדת.\n\n"
                    "**דוגמה:** $h=20\\,\\text{m}$ $\\Rightarrow$ $v=\\sqrt{2gh}=20\\,\\text{m/s}$."
                ),
                "makhina",
            ),
            _section(
                "power",
                "Power",
                "הספק",
                (
                    "**Power** is the rate of doing work or transferring energy:\n"
                    "$$\\boxed{P = \\frac{W}{t} = \\frac{\\Delta E}{t}}$$\n\n"
                    "Also $P = Fv$ when force and velocity are parallel.\n\n"
                    "**Units:** watt (W) = J/s. "
                    "1 horsepower $\\approx 746\\,\\text{W}$.\n\n"
                    "**Example:** motor lifts $m=100\\,\\text{kg}$ at constant speed $v=0.5\\,\\text{m/s}$ "
                    "($g=10\\,\\text{m/s}^2$).\n"
                    "Force needed = $mg = 1000\\,\\text{N}$; "
                    "$P = Fv = 1000 \\cdot 0.5 = 500\\,\\text{W}$.\n\n"
                    "Higher power means the same work is done in less time."
                ),
                (
                    "**הספק:** $P = W/t = Fv$.\n\n"
                    "יחידה: **ואט** (W).\n\n"
                    "**דוגמה:** $m=100\\,\\text{kg}$, $v=0.5\\,\\text{m/s}$ $\\Rightarrow$ $P=500\\,\\text{W}$."
                ),
                "makhina",
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "A constant force of $40\\,\\text{N}$ acts parallel to a $5\\,\\text{m}$ displacement. "
                "The work done is:",
                "כוח קבוע $40\\,\\text{N}$ מקביל לתזוזה $5\\,\\text{m}$. העבודה:",
                _opts([
                    ("a", "$8\\,\\text{J}$", "$8\\,\\text{J}$", False),
                    ("b", "$200\\,\\text{J}$", "$200\\,\\text{J}$", True),
                    ("c", "$45\\,\\text{J}$", "$45\\,\\text{J}$", False),
                    ("d", "$0\\,\\text{J}$", "$0\\,\\text{J}$", False),
                ]),
                "$W = Fd = 40 \\cdot 5 = 200\\,\\text{J}$.",
                "$W = 200\\,\\text{J}$.",
            ),
            _mcq(
                "q2",
                "A $4\\,\\text{kg}$ object ($v_0=0$) has net work $W=32\\,\\text{J}$ done on it. "
                "Its final speed is:",
                "גוף $4\\,\\text{kg}$ ($v_0=0$), $W_{\\text{net}}=32\\,\\text{J}$. המהירות הסופית:",
                _opts([
                    ("a", "$2\\,\\text{m/s}$", "$2\\,\\text{m/s}$", False),
                    ("b", "$4\\,\\text{m/s}$", "$4\\,\\text{m/s}$", True),
                    ("c", "$8\\,\\text{m/s}$", "$8\\,\\text{m/s}$", False),
                    ("d", "$16\\,\\text{m/s}$", "$16\\,\\text{m/s}$", False),
                ]),
                "$W = \\tfrac{1}{2}mv^2 \\Rightarrow 32 = 2v^2 \\Rightarrow v^2=16 \\Rightarrow v=4\\,\\text{m/s}$.",
                "$32 = 2v^2 \\Rightarrow v=4\\,\\text{m/s}$.",
            ),
            _mcq(
                "q3",
                "A $2\\,\\text{kg}$ mass is raised $3\\,\\text{m}$ ($g=10\\,\\text{m/s}^2$). "
                "The increase in gravitational PE is:",
                "מסה $2\\,\\text{kg}$ מורמת $3\\,\\text{m}$ ($g=10$). עלייה ב-$PE$:",
                _opts([
                    ("a", "$6\\,\\text{J}$", "$6\\,\\text{J}$", False),
                    ("b", "$20\\,\\text{J}$", "$20\\,\\text{J}$", False),
                    ("c", "$60\\,\\text{J}$", "$60\\,\\text{J}$", True),
                    ("d", "$30\\,\\text{J}$", "$30\\,\\text{J}$", False),
                ]),
                "$\\Delta PE = mgh = 2 \\cdot 10 \\cdot 3 = 60\\,\\text{J}$.",
                "$\\Delta PE = 60\\,\\text{J}$.",
            ),
            _mcq(
                "q4",
                "A ball is dropped from rest from height $h=5\\,\\text{m}$ ($g=10\\,\\text{m/s}^2$). "
                "Using energy conservation, its speed just before impact is:",
                "כדור נופל מ-$h=5\\,\\text{m}$ ($g=10$). מהירות לפני פגיעה (שימור אנרגיה):",
                _opts([
                    ("a", "$5\\,\\text{m/s}$", "$5\\,\\text{m/s}$", False),
                    ("b", "$10\\,\\text{m/s}$", "$10\\,\\text{m/s}$", True),
                    ("c", "$7.07\\,\\text{m/s}$", "$7.07\\,\\text{m/s}$", False),
                    ("d", "$25\\,\\text{m/s}$", "$25\\,\\text{m/s}$", False),
                ]),
                "$v = \\sqrt{2gh} = \\sqrt{2 \\cdot 10 \\cdot 5} = \\sqrt{100} = 10\\,\\text{m/s}$.",
                "$v = \\sqrt{2gh} = 10\\,\\text{m/s}$.",
            ),
            _mcq(
                "q5",
                "A machine performs $600\\,\\text{J}$ of work in $12\\,\\text{s}$. Its average power is:",
                "מכונה מבצעת $600\\,\\text{J}$ ב-$12\\,\\text{s}$. הספק ממוצע:",
                _opts([
                    ("a", "$7200\\,\\text{W}$", "$7200\\,\\text{W}$", False),
                    ("b", "$50\\,\\text{W}$", "$50\\,\\text{W}$", True),
                    ("c", "$600\\,\\text{W}$", "$600\\,\\text{W}$", False),
                    ("d", "$0.02\\,\\text{W}$", "$0.02\\,\\text{W}$", False),
                ]),
                "$P = W/t = 600/12 = 50\\,\\text{W}$.",
                "$P = 50\\,\\text{W}$.",
            ),
        ],
    },
]


def write_lesson_files() -> None:
    for lesson in REMAINING_LESSONS:
        path = LESSONS_DIR / f"{lesson['id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
        print(f"[write] {path.relative_to(ROOT)}")


def update_lessons_index() -> None:
    with INDEX_PATH.open(encoding="utf-8") as f:
        index = json.load(f)

    updated = 0
    for entry in index:
        lid = entry.get("id")
        if lid not in INDEX_ENTRIES:
            continue
        meta = INDEX_ENTRIES[lid]
        entry.update(
            {
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": meta["math_track"],
                "subject": meta["subject"],
                "duration_min": meta["duration_min"],
                "type": "interactive",
                "level_min": meta["level_min"],
            }
        )
        updated += 1

    existing_ids = {e["id"] for e in index}
    added = 0
    for lid, meta in INDEX_ENTRIES.items():
        if lid in existing_ids:
            continue
        index.append(
            {
                "id": lid,
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": meta["math_track"],
                "subject": meta["subject"],
                "duration_min": meta["duration_min"],
                "type": "interactive",
                "level_min": meta["level_min"],
            }
        )
        added += 1

    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[index] updated {updated}, added {added} entries")


def main() -> int:
    assert len(REMAINING_LESSONS) == 4
    for lesson in REMAINING_LESSONS:
        assert len(lesson["sections"]) == 5
        assert len(lesson["questions"]) == 5

    write_lesson_files()
    update_lessons_index()
    print("[done] stats/makhina part 2 lessons authored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
