#!/usr/bin/env python3
"""Expand distributions.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/distributions.json"

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


SECTION_PATCHES = {
    "intro": {
        "body_en_md": """A **probability distribution** is the complete mathematical description of how randomness behaves: it tells you which outcomes are possible and how likely each one is. Without a named distribution, you cannot compute expectations, variances, tail probabilities, or percentiles — the bread and butter of university statistics and engineering reliability.

**Discrete distributions** assign positive probability to countable outcomes (die faces, defect counts, number of arrivals). **Continuous distributions** describe measurements on intervals (height, waiting time, voltage). The same conceptual tools — PMF or PDF, CDF, mean, variance — apply to both, but the calculus differs.

Israeli university exams (and advanced Bagrut statistics) expect you to **recognise** which distribution fits a word problem, **state** parameters from context, and **compute** probabilities using the right formula. This lesson covers the five workhorses: uniform, normal, exponential, binomial, and Poisson.

**Builds on:** `concept:probability_basic` and `concept:descriptive_stats`. **Unlocks:** hypothesis testing, confidence intervals, and applications in nuclear physics (exponential decay).""",
        "body_he_md": """**התפלגות הסתברות** היא התיאור המתמטי המלא של אופן התנהגות האקראיות: היא אומרת אילו תוצאות אפשריות ומה הסיכוי של כל אחת. בלי התפלגות מוכרת אי אפשר לחשב תוחלות, שונויות, הסתברויות זנב או אחוזונים — ליבת הסטטיסטיקה באוניברסיטה ואמינות הנדסית.

**התפלגויות בדידות** מקצות הסתברות חיובית לתוצאות ספירות (פני קובייה, מספר פגמים, מספר הגעות). **התפלגויות רציפות** מתארות מדידות על קטעים (גובה, זמן המתנה, מתח). אותם כלים — PMF או PDF, CDF, ממוצע, שונות — חלים על שניהם, אך החשבון שונה.

בבחינות אוניברסיטאיות (ובבגרות מתקדמת) מצפים **לזהות** איזו התפלגות מתאימה לבעיית מילים, **לקבוע** פרמטרים מההקשר, ו**לחשב** הסתברויות בנוסחה הנכונה. השיעור מכסה חמש התפלגויות מרכזיות: אחידה, נורמלית, מעריכית, בינומית ופואסון.

**מבוסס על:** `concept:probability_basic` ו-`concept:descriptive_stats`. **פותח:** בדיקת השערות, רווחי סמך, ויישומים בפיזיקה גרעינית (דעיכה מעריכית).""",
    },
    "definition": {
        "body_en_md": """**Random variable $X$:** a numerical function on the sample space. We study its distribution through one of the functions below.

**PMF (probability mass function)** — discrete $X$: $p(x) = P(X=x)$ for each possible $x$. Must satisfy $p(x) \\ge 0$ and $\\sum_x p(x) = 1$.

**PDF (probability density function)** — continuous $X$: $f(x) \\ge 0$ with $\\int_{-\\infty}^{\\infty} f(x)\\,dx = 1$. Probabilities are **areas**: $P(a \\le X \\le b) = \\int_a^b f(x)\\,dx$. Note $P(X = x_0) = 0$ for any single point.

**CDF (cumulative distribution function):** $F(x) = P(X \\le x)$. Always non-decreasing, with $F(-\\infty)=0$ and $F(\\infty)=1$. For continuous $X$: $F(x) = \\int_{-\\infty}^x f(t)\\,dt$ and $f(x) = F'(x)$ where differentiable.

**Expected value (mean):** $\\mu = E[X] = \\sum x\\,p(x)$ (discrete) or $E[X] = \\int x f(x)\\,dx$ (continuous). The "balance point" of the distribution.

**Variance and standard deviation:**
$$\\text{Var}(X) = E[(X-\\mu)^2] = E[X^2] - (E[X])^2, \\quad \\sigma = \\sqrt{\\text{Var}(X)}.$$
Variance measures spread; always non-negative. On exams, the computational formula $E[X^2]-\\mu^2$ is often faster than the definition.

**Relationships:** For discrete $X$, the CDF jumps at each mass point. For continuous $X$, differentiate the CDF to recover the PDF. When a problem gives $f(x)$ with an unknown constant, integrate over the support and set the result equal to 1 to find that constant before computing $E[X]$ or probabilities.""",
        "body_he_md": """**משתנה אקראי $X$:** פונקציה מספרית על מרחב המדגם. לומדים את התפלגותו דרך אחת מהפונקציות הבאות.

**PMF (פונקציית מסה)** — $X$ בדיד: $p(x)=P(X=x)$ לכל $x$ אפשרי. חייב $p(x)\\ge0$ ו-$\\sum_x p(x)=1$.

**PDF (פונקציית צפיפות)** — $X$ רציף: $f(x)\\ge0$ עם $\\int_{-\\infty}^\\infty f(x)\\,dx=1$. הסתברויות הן **שטחים**: $P(a\\le X\\le b)=\\int_a^b f(x)\\,dx$. שימו לב: $P(X=x_0)=0$ לכל נקודה בודדת.

**CDF (פונקציית התפלגות מצטברת):** $F(x)=P(X\\le x)$. תמיד לא-יורדת, עם $F(-\\infty)=0$ ו-$F(\\infty)=1$. לרציף: $F(x)=\\int_{-\\infty}^x f(t)\\,dt$ ו-$f(x)=F'(x)$ היכן שנגזר.

**תוחלת (ממוצע):** $\\mu=E[X]=\\sum x\\,p(x)$ (בדיד) או $E[X]=\\int x f(x)\\,dx$ (רציף). "נקודת האיזון" של ההתפלגות.

**שונות וסטיית תקן:**
$$\\text{Var}(X)=E[(X-\\mu)^2]=E[X^2]-(E[X])^2, \\quad \\sigma=\\sqrt{\\text{Var}(X)}.$$
שונות מודדת פיזור; תמיד לא-שלילית. בבחינה, הנוסחה $E[X^2]-\\mu^2$ לעיתים מהירה מההגדרה.

**קשרים:** לבדיד, ה-CDF קופץ בנקודות מסה. לרציף, נגזרת ה-CDF מחזירה את ה-PDF. כשנותנים $f(x)$ עם קבוע לא ידוע, אינטגרלים על התמיכה, שווים ל-1, ואז מחשבים $E[X]$ או הסתברויות.""",
    },
    "theory": {
        "body_en_md": """### Uniform (continuous) $U[a,b]$

Flat density on $[a,b]$: all sub-intervals of equal length have equal probability.
$$f(x) = \\frac{1}{b-a}, \\quad a \\le x \\le b. \\quad E[X]=\\frac{a+b}{2}, \\quad \\text{Var}(X)=\\frac{(b-a)^2}{12}.$$
Interval probability = length ratio: $P(c < X < d) = (d-c)/(b-a)$.

### Normal $N(\\mu, \\sigma^2)$

Bell-shaped, symmetric about $\\mu$. Central to the Central Limit Theorem.
$$f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}.$$
Standardize: $Z = (X-\\mu)/\\sigma \\sim N(0,1)$. **68-95-99.7 rule:** about 68%, 95%, 99.7% of values lie within $1$, $2$, $3$ standard deviations of $\\mu$.

### Exponential $\\text{Exp}(\\lambda)$

Models waiting time until the first event in a Poisson process (failures, arrivals).
$$f(x) = \\lambda e^{-\\lambda x}, \\quad x \\ge 0. \\quad E[X]=1/\\lambda, \\quad \\text{Var}(X)=1/\\lambda^2.$$
**Memoryless:** $P(X > s+t \\mid X > s) = P(X > t)$. Survival: $P(X > t) = e^{-\\lambda t}$.

### Binomial $B(n,p)$ (discrete)

$n$ independent Bernoulli trials, success probability $p$:
$$P(X=k) = \\binom{n}{k}p^k(1-p)^{n-k}, \\quad E[X]=np, \\quad \\text{Var}(X)=np(1-p).$$

### Poisson $\\text{Poi}(\\lambda)$ (discrete)

Counts rare events in fixed interval; $\\lambda$ = average count:
$$P(X=k) = \\frac{\\lambda^k e^{-\\lambda}}{k!}, \\quad E[X]=\\text{Var}(X)=\\lambda.$$
When $n$ is large and $p$ is small, $B(n,p) \\approx \\text{Poi}(np)$.

**Choosing a model:** Uniform when outcomes are equally likely on an interval; normal for sums/averages of many small effects; exponential for waiting times between Poisson events; binomial for fixed-$n$ success counts; Poisson for event counts per interval when $np$ is moderate.""",
        "body_he_md": """### התפלגות אחידה $U[a,b]$

צפיפות שטוחה על $[a,b]$: תת-קטעים באורך שווה בעלי הסתברות שווה.
$$f(x)=\\frac{1}{b-a}, \\quad a\\le x\\le b. \\quad E[X]=\\frac{a+b}{2}, \\quad \\text{Var}(X)=\\frac{(b-a)^2}{12}.$$
הסתברות על קטע = יחס אורכים: $P(c<X<d)=(d-c)/(b-a)$.

### התפלגות נורמלית $N(\\mu,\\sigma^2)$

צורת פעמון, סימטרית סביב $\\mu$. מרכזית במשפט הגבול המרכזי.
$$f(x)=\\frac{1}{\\sigma\\sqrt{2\\pi}}e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}.$$
תקנון: $Z=(X-\\mu)/\\sigma\\sim N(0,1)$. **כלל 68-95-99.7:** כ-68%, 95%, 99.7% מהערכים בתוך $1$, $2$, $3$ סטיות תקן מ-$\\mu$.

### התפלגות מעריכית $\\text{Exp}(\\lambda)$

מודל לזמן המתנה עד האירוע הראשון (כשלים, הגעות).
$$f(x)=\\lambda e^{-\\lambda x}, \\quad x\\ge0. \\quad E[X]=1/\\lambda, \\quad \\text{Var}(X)=1/\\lambda^2.$$
**חסרת זיכרון:** $P(X>s+t\\mid X>s)=P(X>t)$. הישרדות: $P(X>t)=e^{-\\lambda t}$.

### התפלגות בינומית $B(n,p)$ (בדידה)

$n$ ניסויים בernoulli בלתי-תלויים, הסתברות הצלחה $p$:
$$P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}, \\quad E[X]=np, \\quad \\text{Var}(X)=np(1-p).$$

### התפלגות פואסון $\\text{Poi}(\\lambda)$ (בדידה)

ספירת אירועים נדירים בקטע קבוע; $\\lambda$ = ממוצע הספירה:
$$P(X=k)=\\frac{\\lambda^k e^{-\\lambda}}{k!}, \\quad E[X]=\\text{Var}(X)=\\lambda.$$
כש-$n$ גדול ו-$p$ קטן, $B(n,p)\\approx\\text{Poi}(np)$.

**בחירת מודל:** אחידה כשתוצאות שווי-סיכוי על קטע; נורמלית לסכומים/ממוצעים של הרבה גורמים קטנים; מעריכית לזמני המתנה בין אירועי פואסון; בינומית לספירת הצלחות ב-$n$ קבוע; פואסון לספירות בקטע כש-$np$ בינוני.""",
    },
}


EXPLANATIONS = [
    fmt_expl(
        "For $X \\sim U[0,6]$, probability on an interval equals the fraction of the total length. "
        "The favourable interval is $(1,4)$ with length $4-1=3$. Total support length is $6-0=6$. "
        "Therefore $P(1<X<4)=3/6=1/2$.",
        "Uniform problems reduce to geometry: identify the support $[a,b]$, locate the requested interval, "
        "and divide lengths. No integration needed when the density is constant $1/(b-a)$.",
        "Using $(4-1)/6$ but forgetting endpoints (open vs closed intervals rarely matter for continuous $X$). "
        "Computing $1/6$ by treating each unit as equally likely without using the interval length.",
        "Write $P = \\frac{\\text{favourable length}}{\\text{total length}}$ first. "
        "Israeli exams often use waiting-time or random-arrival setups that map directly to uniform.",
        "ל-$X\\sim U[0,6]$, הסתברות על קטע שווה לשבר מאורך הקטע. הקטע $(1,4)$ באורך 3, "
        "והתמיכה באורך 6, ולכן $P(1<X<4)=3/6=1/2$.",
        "בעיות אחידות = גאומטריה: זיהוי $[a,b]$, מיקום הקטע המבוקש, חלוקת אורכים. "
        "אין צורך באינטגרל כשהצפיפות קבועה $1/(b-a)$.",
        "חישוב $(4-1)/6$ אך בלבול בקצוות (לרציף כמעט לא משנה). חישוב $1/6$ כאילו כל יחידה "
        "בהסתברות שווה בלי אורך הקטע.",
        "כתבו $P=\\frac{\\text{אורך מועדף}}{\\text{אורך כולל}}$ קודם. "
        "בבחינות ישראליות לעיתים המתנה או הגעה אקראית → אחידה.",
    ),
    fmt_expl(
        "For $\\text{Exp}(0.1)$, survival is $P(T>t)=e^{-0.1t}$. So $P(T>20)=e^{-2}\\approx0.135$. "
        "The median $m$ satisfies $F(m)=0.5$, i.e. $1-e^{-0.1m}=0.5$, giving $m=\\ln(2)/0.1=10\\ln2\\approx6.93$ hours.",
        "Exponential: mean $E[T]=1/\\lambda$, tail $P(T>t)=e^{-\\lambda t}$, median from $F(m)=0.5$. "
        "Always check whether $\\lambda$ is given as rate or whether mean is stated instead.",
        "Using $P(T>20)=0.1\\times20=2$ (linear scaling — wrong). Confusing mean $10$ with median "
        "$\\approx6.93$; exponential is right-skewed so mean exceeds median.",
        "Memorise $P(T>t)=e^{-\\lambda t}$ and median $=\\ln2/\\lambda$. "
        "Open questions often ask for both tail probability and a percentile in one stem.",
        "ל-$\\text{Exp}(0.1)$, הישרדות $P(T>t)=e^{-0.1t}$. לכן $P(T>20)=e^{-2}\\approx0.135$. "
        "החציון $m$ מקיים $F(m)=0.5$, כלומר $m=\\ln(2)/0.1\\approx6.93$ שעות — פחות מהממוצע $10$.",
        "מעריכית: ממוצע $E[T]=1/\\lambda$, זנב $P(T>t)=e^{-\\lambda t}$, חציון מ-$F(m)=0.5$. "
        "בדקו האם $\\lambda$ נתון כקצב או שהממוצע נמסר במקום. פתרו כל חלק בנפרד.",
        "שימוש ב-$P(T>20)=0.1\\times20$ (קנה מידה לינארי — שגוי). בלבול ממוצע 10 עם חציון "
        "$\\approx6.93$; מעריכית מוטה ימינה ולכן ממוצע גדול מחציון.",
        "שיננו $P(T>t)=e^{-\\lambda t}$ וחציון $=\\ln2/\\lambda$. "
        "שאלות פתוחות לעיתים מבקשות גם זנב וגם אחוזון — כתבו את שתי הנוסחאות בתחילה.",
    ),
    fmt_expl(
        "$X \\sim U[0,10]$ with constant density $1/10$. The event $X<3$ is the interval $[0,3)$ "
        "of length 3, so $P(X<3)=3/10=0.3$. This is the simplest uniform probability.",
        "Read \"below 3\" as the interval from the left endpoint 0 to 3. For uniform on $[0,10]$, "
        "every unit of length carries probability $0.1$.",
        "Answering $3/10$ but writing $0.03$ (decimal error). Using $P(X=3)$ instead of $P(X<3)$ — "
        "for continuous $X$, point probabilities are zero.",
        "Sketch the number line from 0 to 10 and shade $[0,3)$. "
        "Visual checks prevent arithmetic slips on uniform items.",
        "$X\\sim U[0,10]$ עם צפיפות קבועה $1/10$. האירוע $X<3$ הוא הקטע $[0,3)$ באורך 3, "
        "ולכן $P(X<3)=3/10=0.3$ — ההסתברות הפשוטה ביותר להתפלגות אחידה.",
        "קראו \"מתחת ל-3\" כקטע מ-0 עד 3. ב-$U[0,10]$, כל יחידת אורך נושאת הסתברות $0.1$. "
        "זהו מקרה בסיסי — אותה לוגיקה לכל קטע בתוך $[0,10]$.",
        "תשובה $3/10$ אך כתיבה $0.03$ (טעות עשרונית). שימוש ב-$P(X=3)$ במקום $P(X<3)$ — "
        "לרציף, הסתברות בנקודה בודדת שווה לאפס.",
        "שרטטו קו מספרים 0–10 וצבעו $[0,3)$. בדיקה ויזואלית מונעת טעויות באחידה. "
        "בבחינה, סמנו במפורש את אורך הקטע המועדף לפני החלוקה.",
    ),
    fmt_expl(
        "For $\\text{Exp}(0.5)$: mean $E[T]=1/0.5=2$. Tail probability $P(T>4)=e^{-0.5\\times4}=e^{-2}\\approx0.135$.",
        "Two separate facts: (1) mean is reciprocal of rate; (2) survival uses the exponential formula, "
        "not $1-F$ with a table. Identify $\\lambda=0.5$ before substituting.",
        "Computing $P(T>4)=1-0.5\\times4=-1$ (treating $\\lambda t$ as probability). "
        "Reporting mean as $0.5$ instead of $2$.",
        "When a question asks for both $E[T]$ and $P(T>t)$, answer both clearly — "
        "partial answers lose marks even if one part is correct.",
        "ל-$\\text{Exp}(0.5)$: ממוצע $E[T]=1/0.5=2$. זנב $P(T>4)=e^{-0.5\\times4}=e^{-2}\\approx0.135$.",
        "שני עובדות: (1) ממוצע = הופכי של קצב, $E[T]=1/\\lambda$; (2) הישרדות בנוסחה המעריכית "
        "$e^{-\\lambda t}$, לא $1-F$ מטבלה. זיהו $\\lambda=0.5$ לפני הצבה.",
        "חישוב $P(T>4)=1-0.5\\times4=-1$ (התייחסות ל-$\\lambda t$ כהסתברות). "
        "דיווח ממוצע $0.5$ במקום $2$ — בלבול בין קצב לממוצע.",
        "כשמבקשים $E[T]$ ו-$P(T>t)$, ענו על שניהם בבירור — תשובה חלקית מאבדת ניקוד "
        "גם אם חלק אחד נכון. בדקו שההסתברות בין 0 ל-1.",
    ),
    fmt_expl(
        "Heights $N(170,100)$ means $\\mu=170$, $\\sigma^2=100$, so $\\sigma=10$. "
        "For 180 cm: $z=(180-170)/10=1$. Fraction above 180 is $P(Z>1)=1-\\Phi(1)\\approx1-0.8413=0.159$, "
        "about 15.9%.",
        "Normal tail problems: standardize first, then use symmetry or the $z$-table. "
        "\"Above 180\" means right tail $P(Z>1)$, not $P(Z<1)$.",
        "Using $\\sigma=100$ instead of $\\sigma=10$ (confusing variance with standard deviation). "
        "Computing $P(Z<1)$ when the question asks for \"above\".",
        "Write $\\sigma=\\sqrt{100}=10$ on your paper before standardizing. "
        "Bagrut and university stems often write $N(\\mu,\\sigma^2)$ with variance inside the parentheses.",
        "גבהים $N(170,100)$: $\\mu=170$, $\\sigma^2=100$, $\\sigma=10$. "
        "ל-180 ס\"מ: $z=(180-170)/10=1$. מעל 180: $P(Z>1)=1-\\Phi(1)\\approx0.159$, כ-15.9%.",
        "בעיות זנב נורמלי: תקנון קודם, אחר כך סימטריה או טבלת $z$. "
        "\"מעל 180\" = זנב ימני $P(Z>1)$, לא $P(Z<1)$ שמחזיר כ-84%.",
        "שימוש ב-$\\sigma=100$ במקום $10$ (בלבול שונות עם סטיית תקן). "
        "חישוב $P(Z<1)$ כששואלים \"מעל\" — כיוון שגוי של הזנב.",
        "כתבו $\\sigma=\\sqrt{100}=10$ לפני תקנון. בבגרות ובאוניברסיטה כותבים $N(\\mu,\\sigma^2)$ "
        "עם שונות בסוגריים — חילוץ $\\sigma$ הוא השלב הראשון.",
    ),
    fmt_expl(
        "Rolling a fair die 12 times: $X$ = number of sixes $\\sim B(12,1/6)$. "
        "Expected value $E[X]=np=12\\times(1/6)=2$. "
        "Zero sixes: $P(X=0)=(1-p)^{12}=(5/6)^{12}\\approx0.112$.",
        "Recognise binomial structure: fixed $n$ trials, two outcomes, constant $p$, independence. "
        "$P(X=0)$ uses the \"all failures\" shortcut $(1-p)^n$.",
        "Using $P(X=0)=1/6$ (single-roll probability). Computing $E[X]=12/6$ correctly but "
        "forgetting to raise $(5/6)$ to the 12th power.",
        "State $X\\sim B(n,p)$ explicitly for partial credit. "
        "Exam word problems hide the binomial in \"number of successes in $n$ attempts\" language.",
        "קובייה הוגנת 12 פעמים: $X$ = מספר שישיות $\\sim B(12,1/6)$. "
        "תוחלת $E[X]=np=12\\times(1/6)=2$. "
        "אפס שישיות: $P(X=0)=(5/6)^{12}\\approx0.112$.",
        "זיהוי מבנה בינומי: $n$ ניסויים קבוע, שני תוצאות, $p$ קבוע, בלתי-תלות. "
        "$P(X=0)$ = \"כולם כישלון\" $(1-p)^n=(5/6)^{12}$.",
        "שימוש ב-$P(X=0)=1/6$ (הסתברות הטלה בודד). $E[X]=2$ נכון אך שכחת העלאה ב-12 "
        "בחישוב $(5/6)^{12}$.",
        "כתבו $X\\sim B(n,p)$ במפורש לניקוד חלקי. בבחינה הבינומית מוסתרת ב\"מספר הצלחות "
        "ב-$n$ ניסויים\" — ספרו ניסויים והסתברות הצלחה. ודאו שהתוחלת $np$ הגיונית.",
    ),
    fmt_expl(
        "Check PDF validity: $\\int_0^\\infty 2e^{-2x}\\,dx = [-e^{-2x}]_0^\\infty = 0-(-1)=1$. ✓ "
        "This is $\\text{Exp}(\\lambda=2)$, so mean $E[X]=1/2=0.5$.",
        "Two-step exam item: (1) integrate to verify total area 1; (2) identify named distribution "
        "and read off mean $1/\\lambda$. Do not stop after the integral.",
        "Integrating incorrectly to get 2 instead of 1. Identifying $\\lambda=2$ but reporting "
        "mean as 2 instead of $1/2$.",
        "After verifying $\\int f=1$, always name the distribution — it unlocks mean/variance "
        "formulas without further integration.",
        "בדיקת PDF: $\\int_0^\\infty 2e^{-2x}\\,dx=[-e^{-2x}]_0^\\infty=1$. ✓ "
        "זו $\\text{Exp}(\\lambda=2)$, ממוצע $E[X]=1/2=0.5$.",
        "פריט בחינה דו-שלבי: (1) אינטגרל לאימות שטח 1; (2) זיהוי התפלגות וקריאת $1/\\lambda$. "
        "אל תעצרו אחרי האינטגרל — שם ההתפלגות נותן את הממוצע.",
        "אינטגרל שגוי → 2 במקום 1. $\\lambda=2$ נכון אך ממוצע 2 במקום $1/2$ — "
        "בלבול קצב $\\lambda$ עם תוחלת.",
        "אחרי $\\int f=1$, תמיד שם ההתפלגות — פותח נוסחאות ממוצע/שונות בלי אינטגרל נוסף. "
        "בבחינות ישראליות מבקשים לעיתים גם $\\text{Var}(X)$.",
    ),
    fmt_expl(
        "$X\\sim N(100,225)$: $\\mu=100$, $\\sigma=15$. The 95th percentile uses $z_{0.95}\\approx1.645$ "
        "(one-sided 95% point). $x_{0.95}=\\mu+z\\sigma=100+1.645\\times15=124.675\\approx124.7$.",
        "Percentile problems reverse standardization: solve $x=\\mu+z_p\\sigma$ with $z_p$ from the table. "
        "Confirm whether \"95th percentile\" means 95% below (use $z_{0.95}$) vs central 95% interval.",
        "Using $z=1.96$ (two-sided 95% critical value) instead of $1.645$ for a one-sided percentile. "
        "Adding $z\\sigma$ when the question asks for the 5th percentile (sign error).",
        "Underline \"95th percentile\" vs \"middle 95%\" in the stem. "
        "Israeli exams distinguish these deliberately.",
        "$X\\sim N(100,225)$: $\\mu=100$, $\\sigma=15$. אחוזון 95 משתמש ב-$z_{0.95}\\approx1.645$. "
        "$x_{0.95}=100+1.645\\times15\\approx124.7$.",
        "אחוזון = תקנון הפוך: $x=\\mu+z_p\\sigma$ עם $z_p$ מהטבלה. "
        "ודאו: \"אחוזון 95\" = 95% מתחת ($z_{0.95}$) מול \"95% מרכזי\" ($\\pm1.96$).",
        "שימוש ב-$z=1.96$ (95% דו-צדדי) במקום $1.645$ לאחוזון חד-צדדי. "
        "חיבור $z\\sigma$ כשמבקשים אחוזון 5 (טעות סימן).",
        "סמנו \"אחוזון 95\" מול \"95% מרכזי\" בשאלה. בבחינות ישראליות מבדילים בכוונה — "
        "קראו האם מבקשים ערך שמתחתיו 95% או רווח מרכזי.",
    ),
]


def build_lesson() -> dict:
    with open(TARGET, encoding="utf-8") as f:
        lesson = json.load(f)

    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind in SECTION_PATCHES:
            sec.update(SECTION_PATCHES[kind])

        if kind == "worked_example":
            n = sec.get("example_number")
            if n == 1:
                sec["body_en_md"] = """**Given:** A bus arrives uniformly at random between 9:00 and 9:20 (a 20-minute window). Find the probability that a passenger who arrives at 9:00 waits **more than 12 minutes**, and the expected waiting time.

This is a classic **continuous uniform** setup: all arrival times in the interval are equally likely. The density is flat, so probabilities reduce to length ratios — no calculus required once you identify $[a,b]$.

### Move 1: Model the waiting time
Let $X$ = minutes after 9:00 until the bus arrives. Then $X \\sim U[0, 20]$ with PDF $f(x)=1/20$ on $[0,20]$.

### Move 2: Probability of waiting more than 12 minutes
$$P(X > 12) = \\int_{12}^{20} \\frac{1}{20}\\,dx = \\frac{20-12}{20} = \\frac{8}{20} = 0.4.$$
Equivalently: favourable length 8, total length 20.

### Move 3: Expected waiting time
$$E[X] = \\frac{0+20}{2} = 10 \\text{ minutes}.$$

**Answer:** 40% chance of waiting more than 12 minutes; average wait is 10 minutes. **Sanity check:** $P(X>12)=0.4<0.5$ makes sense because 12 exceeds the midpoint 10.

**Exam link:** Random arrival with uniform service/start time is a standard Bagrut and calculus-probability crossover item — always draw the interval before dividing lengths."""
                sec["body_he_md"] = """**נתון:** אוטובוס מגיע אחיד אקראי בין 9:00 ל-9:20 (חלון 20 דקות). מצאו את ההסתברות שנוסע שמגיע ב-9:00 ימתין **יותר מ-12 דקות**, ואת זמן ההמתנה הממוצע.

זה תרחיש **אחיד רציף** קלאסי: כל זמני ההגעה בקטע שווי-סיכוי. הצפיפות שטוחה, וההסתברויות = יחסי אורכים — בלי אינטגרל אחרי זיהוי $[a,b]$.

### צעד 1: מודל זמן ההמתנה
נסמן $X$ = דקות מ-9:00 עד הגעת האוטובוס. אז $X\\sim U[0,20]$ עם PDF $f(x)=1/20$ על $[0,20]$.

### צעד 2: הסתברות להמתנה מעל 12 דקות
$$P(X>12)=\\int_{12}^{20}\\frac{1}{20}\\,dx=\\frac{20-12}{20}=\\frac{8}{20}=0.4.$$
שקיל: אורך מועדף 8, אורך כולל 20.

### צעד 3: זמן המתנה ממוצע
$$E[X]=\\frac{0+20}{2}=10 \\text{ דקות}.$$

**תשובה:** 40% סיכוי להמתין יותר מ-12 דקות; ממוצע 10 דקות. **בדיקה:** $P(X>12)=0.4<0.5$ הגיוני כי 12 מעל האמצע 10.

**קישור לבחינה:** הגעה אקראית עם חלון אחיד — שאלה נפוצה בבגרות; שרטטו את הקטע לפני חלוקת אורכים. אם שואלים גם על $E[X]$, זכרו שהממוצע הוא אמצע הקטע $(a+b)/2$."""
            elif n == 2:
                sec["body_en_md"] = """**Given:** Exam scores are normally distributed with $\\mu = 70$, $\\sigma = 10$. A student scores 85.

(a) What is the $z$-score?
(b) What fraction of students scored below 85?
(c) Using the 68-95-99.7 rule, what fraction scored between 50 and 90?

Normal problems always begin with **standardization**. The $z$-score tells you how many standard deviations the observation lies from the mean — that is what the table expects. Write $z=(x-\\mu)/\\sigma$ explicitly before any table lookup; Israeli exams often award partial credit for correct standardization even if the final probability is wrong.

### Move 1 (a): Standardize
$$z = \\frac{X - \\mu}{\\sigma} = \\frac{85 - 70}{10} = 1.5.$$
The score is 1.5 standard deviations **above** the mean.

### Move 2 (b): Cumulative probability
$$P(X < 85) = P(Z < 1.5) \\approx 0.9332.$$
About **93.3%** of students scored below 85; roughly 6.7% scored 85 or higher.

### Move 3 (c): Empirical rule
$\\mu \\pm 2\\sigma = 70 \\pm 20 = [50, 90]$. By the 68-95-99.7 rule,
$$P(50 < X < 90) \\approx 95\\%.$$
No $z$-table needed — recognise the $\\pm 2\\sigma$ interval immediately.

**Exam note:** Part (c) is a quick empirical-rule item. Part (b) shows why standardization matters: the same $z=1.5$ applies to any normal with these parameters. Always report $z$ before table values."""
                sec["body_he_md"] = """**נתון:** ציוני בחינה: $\\mu=70$, $\\sigma=10$. תלמיד קיבל 85.

(א) מהו ציון $z$?
(ב) איזה שבר מהתלמידים קיבלו פחות מ-85?
(ג) בכלל 68-95-99.7, כמה קיבלו בין 50 ל-90?

בעיות נורמליות מתחילות ב**תקנון**. ציון $z$ מודד כמה סטיות תקן הערך רחוק מהממוצע — זה הקלט שהטבלה מצפה לו. לפני כל חיפוש בטבלה, כתבו במפורש את $z=(x-\\mu)/\\sigma$.

### צעד 1 (א): תקנון
$$z=\\frac{85-70}{10}=1.5.$$
הציון חיובי — 85 מעל הממוצע 70.

### צעד 2 (ב): הסתברות מצטברת
$$P(X<85)=P(Z<1.5)\\approx0.9332.$$
כ-**93.3%** קיבלו פחות מ-85; רק כ-6.7% קיבלו 85 ומעלה.

### צעד 3 (ג): כלל 68-95-99.7
$\\mu\\pm2\\sigma=70\\pm20=[50,90]$. לפי הכלל,
$$P(50<X<90)\\approx95\\%.$$
אין צורך בטבלה — זיהוי $\\pm2\\sigma$ מספיק.

**הערה:** בסעיף (ב), $z=1.5$ גבוה בינוני; רק כ-6–7% קיבלו מעל 85. דווחו תמיד על $z$ לפני חיפוש בטבלה — ניקוד חלקי על התקנון."""
            elif n == 3:
                sec["body_en_md"] = """**Given:** Customer service calls arrive according to an exponential distribution with **mean 5 minutes**. Find: (a) PDF and CDF of waiting time $T$; (b) median; (c) 90th percentile.

When the **mean** is given, first convert to rate: $\\lambda = 1/E[T]$. Percentiles solve $F(t_p)=p$ using the closed form $t_p = -\\ln(1-p)/\\lambda$. This three-part structure — write $f$ and $F$, then solve two percentile equations — is a standard university exam template for exponential waiting times.

### Move 1: PDF and CDF
$\\lambda = 1/5 = 0.2$ min$^{-1}$.
$$f(t) = 0.2\\, e^{-0.2t}, \\quad t \\ge 0; \\qquad F(t) = 1 - e^{-0.2t}.$$
Verify: $F(0)=0$ and $F(\\infty)=1$.

### Move 2: Median ($p=0.5$)
Set $F(t_{0.5})=0.5$:
$$1 - e^{-0.2 t_{0.5}} = 0.5 \\Rightarrow e^{-0.2 t_{0.5}} = 0.5 \\Rightarrow t_{0.5} = \\frac{\\ln 2}{0.2} \\approx 3.47 \\text{ min}.$$
Alternatively use $t_{0.5} = \\ln(2)/\\lambda$ directly.

### Move 3: 90th percentile
$$t_{0.9} = -\\frac{\\ln(1-0.9)}{0.2} = \\frac{\\ln 10}{0.2} \\approx 11.5 \\text{ min}.$$
About 90% of callers wait less than 11.5 minutes.

**Interpretation:** Mean (5 min) $>$ median (3.47 min) because the exponential is **right-skewed** — occasional long waits pull the average up. **Check:** plug $t=5$ into $F$ to see $F(5)=1-e^{-1}\\approx0.63$."""
                sec["body_he_md"] = """**נתון:** שיחות שירות מגיעות בהתפלגות מעריכית עם **ממוצע 5 דקות**. מצאו: (א) PDF ו-CDF של $T$; (ב) חציון; (ג) אחוזון 90.

כשניתן **ממוצע**, המירו לקצב: $\\lambda=1/E[T]=1/5=0.2$. אחוזונים פותרים $F(t_p)=p$ עם $t_p=-\\ln(1-p)/\\lambda$. מבנה שלושה חלקים — $f$ ו-$F$, ואז שני אחוזונים — תבנית בחינה נפוצה לזמני המתנה מעריכיים.

### צעד 1: PDF ו-CDF
$$f(t)=0.2\\,e^{-0.2t},\\ t\\ge0; \\qquad F(t)=1-e^{-0.2t}.$$
אימות: $F(0)=0$ ו-$F(\\infty)=1$.

### צעד 2: חציון ($p=0.5$)
מ-$F(t_{0.5})=0.5$:
$$1-e^{-0.2t_{0.5}}=0.5 \\Rightarrow t_{0.5}=\\frac{\\ln2}{0.2}\\approx3.47 \\text{ דקות}.$$
ניתן גם $t_{0.5}=\\ln(2)/\\lambda$ ישירות.

### צעד 3: אחוזון 90
$$t_{0.9}=-\\frac{\\ln(0.1)}{0.2}=\\frac{\\ln10}{0.2}\\approx11.5 \\text{ דקות}.$$
כ-90% מהמתקשרים ממתינים פחות מ-11.5 דקות.

**פירוש:** ממוצע (5) $>$ חציון (3.47) כי המעריכית **מוטה ימינה**. **בדיקה:** $F(5)=1-e^{-1}\\approx0.63$ — יותר ממחצית ממתינים פחות מ-5 דקות. זכרו: $\\lambda=0.2$ ולא $5$."""

        if kind == "checkpoint":
            body_en = sec.get("body_en_md", "")
            if "U[2, 8]" in body_en:
                sec["checkpoint_solution_en"] = """**Given:** $X \\sim U[2, 8]$. Find (a) $P(X<5)$, (b) $E[X]$, (c) $\\text{Var}(X)$.

**Step 1 (a):** Interval probability on $[2,8]$ with length 6. Favourable interval $[2,5)$ has length 3.
$$P(X<5) = \\frac{5-2}{8-2} = \\frac{3}{6} = \\frac{1}{2}.$$

**Step 2 (b):** Midpoint formula:
$$E[X] = \\frac{2+8}{2} = 5.$$

**Step 3 (c):** Uniform variance:
$$\\text{Var}(X) = \\frac{(8-2)^2}{12} = \\frac{36}{12} = 3.$$

**Check:** $\\sqrt{3}\\approx1.73$ is a reasonable spread for support width 6."""
                sec["checkpoint_solution_he"] = """**נתון:** $X\\sim U[2,8]$. מצאו (א) $P(X<5)$, (ב) $E[X]$, (ג) $\\text{Var}(X)$.

**שלב 1 (א):** על $[2,8]$ אורך 6. הקטע $[2,5)$ באורך 3.
$$P(X<5)=\\frac{5-2}{8-2}=\\frac{1}{2}.$$

**שלב 2 (ב):**
$$E[X]=\\frac{2+8}{2}=5.$$

**שלב 3 (ג):**
$$\\text{Var}(X)=\\frac{(8-2)^2}{12}=3.$$

**בדיקה:** $\\sqrt{3}\\approx1.73$ פיזור סביר לרוחב 6."""
            elif "Exp" in body_en and "0.02" in body_en:
                sec["checkpoint_solution_en"] = """**Given:** Light bulb lifetime $T \\sim \\text{Exp}(\\lambda=0.02)$ hours.

**Step 1 (a): Mean**
$$E[T] = \\frac{1}{\\lambda} = \\frac{1}{0.02} = 50 \\text{ hours}.$$

**Step 2 (b):** Survival probability
$$P(T > t) = e^{-\\lambda t} \\Rightarrow P(T > 60) = e^{-0.02 \\times 60} = e^{-1.2} \\approx 0.301.$$

About 30.1% of bulbs last beyond 60 hours. **Common check:** $E[T]=50<60$, so $P(T>60)<0.5$ — consistent."""
                sec["checkpoint_solution_he"] = """**נתון:** חיי מנורה $T\\sim\\text{Exp}(\\lambda=0.02)$ שעות.

**שלב 1 (א): ממוצע**
$$E[T]=\\frac{1}{0.02}=50 \\text{ שעות}.$$

**שלב 2 (ב):** הישרדות
$$P(T>60)=e^{-0.02\\times60}=e^{-1.2}\\approx0.301.$$

כ-30.1% מהמנורות חיות מעל 60 שעות. **בדיקה:** $E[T]=50<60$ ולכן $P(T>60)<0.5$ — עקבי."""

        if kind == "method_guide":
            sec["body_en_md"] = """| Distribution | Parameters | Mean | Variance | Key formula |
|---|---|---|---|---|
| Uniform $U[a,b]$ | $a,b$ | $(a+b)/2$ | $(b-a)^2/12$ | $P(c<X<d)=(d-c)/(b-a)$ |
| Normal $N(\\mu,\\sigma^2)$ | $\\mu,\\sigma$ | $\\mu$ | $\\sigma^2$ | $z=(x-\\mu)/\\sigma$, use $z$-table |
| Exponential $\\text{Exp}(\\lambda)$ | $\\lambda>0$ | $1/\\lambda$ | $1/\\lambda^2$ | $P(T>t)=e^{-\\lambda t}$ |
| Binomial $B(n,p)$ | $n,p$ | $np$ | $np(1-p)$ | $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$ |
| Poisson $\\text{Poi}(\\lambda)$ | $\\lambda>0$ | $\\lambda$ | $\\lambda$ | $P(X=k)=\\lambda^k e^{-\\lambda}/k!$ |

**5-step problem solving:**
1. Read the story — identify discrete vs continuous and the named distribution.
2. Extract parameters ($\\lambda$ from mean, $p$ from context, $a,b$ from endpoints).
3. Choose the tool: PMF/PDF for single probabilities, CDF for \"at most\", survival for \"greater than\".
4. Compute, showing standardization or length ratios explicitly.
5. Sanity-check: probabilities in $[0,1]$, mean inside support, variance positive.

**Percentile shortcuts:**
- Uniform: $x_p = a + p(b-a)$.
- Exponential: $x_p = -\\ln(1-p)/\\lambda$.
- Normal: $x_p = \\mu + z_p \\sigma$."""
            sec["body_he_md"] = """| התפלגות | פרמטרים | ממוצע | שונות | נוסחה מרכזית |
|---|---|---|---|---|
| אחידה $U[a,b]$ | $a,b$ | $(a+b)/2$ | $(b-a)^2/12$ | $P(c<X<d)=(d-c)/(b-a)$ |
| נורמלית $N(\\mu,\\sigma^2)$ | $\\mu,\\sigma$ | $\\mu$ | $\\sigma^2$ | $z=(x-\\mu)/\\sigma$ |
| מעריכית $\\text{Exp}(\\lambda)$ | $\\lambda>0$ | $1/\\lambda$ | $1/\\lambda^2$ | $P(T>t)=e^{-\\lambda t}$ |
| בינומית $B(n,p)$ | $n,p$ | $np$ | $np(1-p)$ | $\\binom{n}{k}p^k(1-p)^{n-k}$ |
| פואסון $\\text{Poi}(\\lambda)$ | $\\lambda>0$ | $\\lambda$ | $\\lambda$ | $\\lambda^k e^{-\\lambda}/k!$ |

**5 שלבי פתרון:**
1. קראו את הסיפור — בדיד/רציף והתפלגות מתאימה.
2. חלצו פרמטרים ($\\lambda$ מממוצע, $p$ מההקשר, $a,b$ מקצוות).
3. בחרו כלי: PMF/PDF, CDF ל\"לכל היותר\", הישרדות ל\"גדול מ\".
4. חשבו עם תקנון או יחס אורכים במפורש.
5. בדיקת הגיון: הסתברויות ב-$[0,1]$, ממוצע בתמיכה, שונות חיובית.

**קיצורי אחוזון:**
- אחידה: $x_p=a+p(b-a)$.
- מעריכית: $x_p=-\\ln(1-p)/\\lambda$.
- נורמלית: $x_p=\\mu+z_p\\sigma$."""

        if kind == "pitfall":
            sec["body_en_md"] = """1. **PDF vs PMF.** For continuous $X$, $P(X=x)=0$ for any single value. Only **intervals** carry positive probability. Do not plug $x$ into the PDF expecting a probability.

2. **Forgetting $\\int f(x)\\,dx = 1$.** Before trusting a proposed PDF, verify total area equals 1. Exam questions sometimes ask you to find the missing constant.

3. **$z$-score sign error.** Always $z=(x-\\mu)/\\sigma$, never $(\\mu-x)/\\sigma$. A negative $z$ means below the mean.

4. **Exponential $\\lambda$ vs mean.** $\\lambda$ is the **rate** (events per unit time); mean is $E[T]=1/\\lambda$. If mean = 5 minutes, then $\\lambda=0.2$, not 5.

5. **Normal approximation to binomial.** Apply continuity correction: $P(X=k) \\approx P(k-0.5 < Y < k+0.5)$. Skipping it loses marks on university exams.

**Self-review habit:** After each wrong answer, label which pitfall you hit — that builds faster pattern recognition than re-reading formulas."""
            sec["body_he_md"] = """1. **PDF לעומת PMF.** לרציף $X$, $P(X=x)=0$ לכל ערך בודד. רק **קטעים** נושאים הסתברות חיובית. אל תציבו $x$ ב-PDF ותצפו להסתברות.

2. **שכחת $\\int f=1$.** לפני שסומכים על PDF, ודאו שטח כולל 1. בבחינה לעיתים מחפשים את הקבוע החסר.

3. **שגיאת סימן ב-$z$.** תמיד $z=(x-\\mu)/\\sigma$, לא $(\\mu-x)/\\sigma$. $z$ שלילי = מתחת לממוצע.

4. **$\\lambda$ לעומת ממוצע.** $\\lambda$ = **קצב**; ממוצע $E[T]=1/\\lambda$. אם ממוצע = 5 דקות, אז $\\lambda=0.2$, לא 5.

5. **קירוב נורמלי לבינומי.** תיקון רציפות: $P(X=k)\\approx P(k-0.5<Y<k+0.5)$. דילוג = אובדן ניקוד.

**הרגל ביקורת:** אחרי כל טעות, סמנו איזו מלכודת — זיהוי דפוסים מהיר יותר מקריאת נוסחאות."""

        if kind == "why_matters":
            sec["body_en_md"] = """Probability distributions are the language of uncertainty across science and engineering. Every statistical inference method — confidence intervals, hypothesis tests, regression diagnostics — assumes a named distribution somewhere in the pipeline.

**You will use this to unlock:**
- `concept:hypothesis_testing` — test statistics rely on normal, $t$, and chi-square distributions
- `concept:nuclear_physics` — radioactive decay follows exponential waiting times

**Builds on:**
- `concept:probability_basic` — sample spaces, events, counting
- `concept:descriptive_stats` — normal curve intuition and $z$-scores

**Why it matters for exams:** Israeli Bagrut (5-unit) and first-year university courses reward **transfer** — recognising which distribution fits a new story. When studying, always ask: \"What are the parameters in this context? What would I compute first?\" """
            sec["body_he_md"] = """התפלגויות הסתברות הן שפת האי-ודאות במדע ובהנדסה. כל שיטת הסקה — רווחי סמך, בדיקות השערות, רגרסיה — מסתמכת על התפלגות מוכרת בשרשרת.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:hypothesis_testing` — סטטיסטיקות מבחן מסתמכות על נורמלית, $t$, chi-square
- `concept:nuclear_physics` — דעיכה רדיואקטיבית = זמני המתנה מעריכיים

**מבוסס על:**
- `concept:probability_basic` — מרחבי מדגם, אירועים, ספירה
- `concept:descriptive_stats` — אינטואיציה של עקומת פעמון ו-$z$

**למה זה חשוב לבחינות:** בבגרות (5 יחידות) ובשנה א' מעריכים **העברה** — זיהוי התפלגות בסיפור חדש. בלימוד, שאלו: \"מה הפרמטרים כאן? מה נחשב קודם?\""""

        if kind == "before_exam":
            sec["body_en_md"] = """**Key formulas table:**

| | Mean | Variance | $P(X>x)$ or tail |
|---|---|---|---|
| $U[a,b]$ | $(a+b)/2$ | $(b-a)^2/12$ | $(b-x)/(b-a)$ |
| $N(\\mu,\\sigma^2)$ | $\\mu$ | $\\sigma^2$ | $1-\\Phi((x-\\mu)/\\sigma)$ |
| $\\text{Exp}(\\lambda)$ | $1/\\lambda$ | $1/\\lambda^2$ | $e^{-\\lambda x}$ |
| $B(n,p)$ | $np$ | $np(1-p)$ | sum PMF tail |
| $\\text{Poi}(\\lambda)$ | $\\lambda$ | $\\lambda$ | $1-\\sum_{k=0}^{x-1} P(X=k)$ |

**Percentile recipes:**
- Uniform: $x_p = a + p(b-a)$.
- Exponential: $x_p = -\\ln(1-p)/\\lambda$.
- Normal: $x_p = \\mu + z_p \\sigma$ (table lookup).

**Last review:** Say each formula aloud once, then solve one checkpoint without notes. Time yourself — distribution identification should take under 30 seconds."""
            sec["body_he_md"] = """**טבלת נוסחאות:**

| | ממוצע | שונות | זנב / $P(X>x)$ |
|---|---|---|---|
| $U[a,b]$ | $(a+b)/2$ | $(b-a)^2/12$ | $(b-x)/(b-a)$ |
| $N(\\mu,\\sigma^2)$ | $\\mu$ | $\\sigma^2$ | $1-\\Phi(z)$ |
| $\\text{Exp}(\\lambda)$ | $1/\\lambda$ | $1/\\lambda^2$ | $e^{-\\lambda x}$ |
| $B(n,p)$ | $np$ | $np(1-p)$ | סכום PMF |
| $\\text{Poi}(\\lambda)$ | $\\lambda$ | $\\lambda$ | $1-\\sum P(X=k)$ |

**מתכוני אחוזון:**
- אחידה: $x_p=a+p(b-a)$.
- מעריכית: $x_p=-\\ln(1-p)/\\lambda$.
- נורמלית: $x_p=\\mu+z_p\\sigma$.

**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint בלי רשימות. תזמון — זיהוי התפלגות תוך פחות מ-30 שניות."""

        if kind == "summary":
            sec["body_en_md"] = """- **Uniform:** flat PDF on $[a,b]$; $E=(a+b)/2$; interval probability = length ratio.
- **Normal:** bell curve; standardize $z=(x-\\mu)/\\sigma$; 68-95-99.7 rule for quick intervals.
- **Exponential:** $f=\\lambda e^{-\\lambda x}$, $E=1/\\lambda$, memoryless; $P(T>t)=e^{-\\lambda t}$.
- **Binomial:** $n$ trials, success prob $p$; $E=np$, $\\text{Var}=np(1-p)$.
- **Poisson:** rare counts with rate $\\lambda$; $E=\\text{Var}=\\lambda$.
- Always verify $\\int f = 1$ for a continuous PDF before computing expectations.

**Takeaway:** From the problem wording alone, you should name the distribution, list parameters, and pick the correct formula within one minute."""
            sec["body_he_md"] = """- **אחידה:** PDF שטוח על $[a,b]$; $E=(a+b)/2$; הסתברות = יחס אורכים.
- **נורמלית:** פעמון; $z=(x-\\mu)/\\sigma$; כלל 68-95-99.7 לקטעים מהירים.
- **מעריכית:** $f=\\lambda e^{-\\lambda x}$, $E=1/\\lambda$, חסרת זיכרון; $P(T>t)=e^{-\\lambda t}$.
- **בינומית:** $n$ ניסויים, $p$; $E=np$, $\\text{Var}=np(1-p)$.
- **פואסון:** ספירות נדירות עם $\\lambda$; $E=\\text{Var}=\\lambda$.
- תמיד אמתו $\\int f=1$ לפני חישוב תוחלות.

**מסקנה:** מניסוח הבעיה בלבד — שם ההתפלגות, פרמטרים, ונוסחה נכונה תוך דקה."""

    for i, q in enumerate(lesson["questions"]):
        if i < len(EXPLANATIONS):
            q["explanation_en"], q["explanation_he"] = EXPLANATIONS[i]

    return lesson


def validate(lesson: dict) -> list[str]:
    errors = []
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind in MIN:
            en_min, he_min = MIN[kind]
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"{sec.get('id', kind)} EN: {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{sec.get('id', kind)} HE: {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{sec.get('id', kind)} HE weak")

    for i, q in enumerate(lesson["questions"]):
        for lang in ("en", "he"):
            w = wc(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"q{i+1} explanation_{lang}: {w} words (need 80-150)")

    return errors


def main():
    lesson = build_lesson()
    errors = validate(lesson)

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {TARGET}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)

    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")


if __name__ == "__main__":
    main()
