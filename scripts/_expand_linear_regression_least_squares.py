#!/usr/bin/env python3
"""Expand linear_regression_least_squares.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/linear_regression_least_squares.json"

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


INTRO_EN = """When two variables appear related — study hours and exam scores, temperature and ice-cream sales — we often want a **straight-line summary** of that relationship. **Ordinary Least Squares (OLS)** regression finds the line that best fits paired data $(x_i, y_i)$ by minimizing the sum of squared vertical deviations from the line.

Unlike eyeballing a trend, OLS gives **closed-form estimators** for slope $\\hat{\\beta}_1$ and intercept $\\hat{\\beta}_0$, a decomposition of total variance into explained and unexplained parts ($R^2$), and — under classical assumptions — the **Gauss–Markov BLUE** guarantee: minimum variance among all linear unbiased estimators.

This lesson appears in Israeli university statistics courses (TAU, Technion, HUJI), Bagrut 5-unit statistics, econometrics, and every data-science pipeline that fits a trend line. You will compute OLS coefficients from summary statistics, interpret residuals and $R^2$, derive the formulas via calculus, and conduct $t$-tests on the slope.

**Builds on:** descriptive statistics, correlation, and sampling distributions from `concept:linear_regression_correlation` and `concept:distributions`. Master $\\bar{x}$, $S_{xx}$, and $S_{xy}$ before tackling inference."""

INTRO_HE = """כששני משתנים נראים קשורים — שעות לימוד וציונים, טמפרטורה ומכירות גלידה — לעיתים קרובות רוצים **סיכום קווי ישר** של הקשר. **רגרסיה OLS** מוצאת את הקו שמתאים לנתונים זוגיים $(x_i, y_i)$ על ידי מינימיזציה של סכום ריבועי הסטיות האנכיות מהקו.

בניגוד להערכת מגמה בעין, OLS נותנת **אומדים בצורה סגורה** לשיפוע $\\hat{\\beta}_1$ ולנקודת חיתוך $\\hat{\\beta}_0$, פירוק שונות כוללת לחלק מוסבר ולא מוסבר ($R^2$), ו — תחת הנחות קלאסיות — **BLUE** של גאוס–מרקוב: שונות מינימלית בין כל האומדים הלינאריים חסרי ההטיה.

שיעור זה מופיע בקורסי סטטיסטיקה אוניברסיטאיים (TAU, טכניון, HUJI), בגרות 5 יחידות, אקונומטריקה, ובכל צינור data science שמתאים קו מגמה. תחשבו מקדמי OLS מסטטיסטיקות סיכום, תפרשו שאריות ו-$R^2$, תגזרו נוסחאות בחשבון, ותערכו מבחני $t$ על השיפוע.

**מבוסס על:** סטטיסטיקה תיאורית, מתאם והתפלגויות מדגם מ-`concept:linear_regression_correlation` ו-`concept:distributions`. שלטו ב-$\\bar{x}$, $S_{xx}$ ו-$S_{xy}$ לפני הסקה."""

DEF_EN = """**OLS slope and intercept:**
$$\\hat{\\beta}_1 = \\frac{\\sum_{i=1}^n (x_i-\\bar{x})(y_i-\\bar{y})}{\\sum_{i=1}^n (x_i-\\bar{x})^2} = \\frac{S_{xy}}{S_{xx}}, \\qquad \\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}.$$

**Predicted value:** $\\hat{y}_i = \\hat{\\beta}_0 + \\hat{\\beta}_1 x_i$ — the value on the fitted line at $x_i$.

**Residual:** $e_i = y_i - \\hat{y}_i$ — the vertical distance from the observed point to the fitted line. OLS normal equations guarantee $\\sum e_i = 0$ and $\\sum x_i e_i = 0$.

**Variance decomposition:**
$$\\text{SST} = \\sum_{i=1}^n (y_i - \\bar{y})^2 \\quad \\text{(total variation in } y\\text{)},$$
$$\\text{SSE} = \\sum_{i=1}^n (\\hat{y}_i - \\bar{y})^2 \\quad \\text{(explained by regression)},$$
$$\\text{SSR} = \\sum_{i=1}^n e_i^2 \\quad \\text{(unexplained residual sum of squares)}.$$
Identity: $\\text{SST} = \\text{SSE} + \\text{SSR}$.

**Coefficient of determination:**
$$R^2 = 1 - \\frac{\\text{SSR}}{\\text{SST}} = \\frac{\\text{SSE}}{\\text{SST}} = r^2,$$
where $r$ is the Pearson correlation. $R^2 \\in [0,1]$ is the proportion of total variance in $y$ explained by the linear model.

**Residual standard error:** $s = \\sqrt{\\text{SSR}/(n-2)}$ estimates the error standard deviation $\\sigma$ in $y_i = \\beta_0 + \\beta_1 x_i + \\varepsilon_i$.

**Computational sums (useful on exams):** $S_{xy} = \\sum x_i y_i - n\\bar{x}\\bar{y}$ and $S_{xx} = \\sum x_i^2 - n\\bar{x}^2$ avoid building full deviation tables when raw totals are given. Similarly $S_{yy} = \\sum y_i^2 - n\\bar{y}^2$ feeds directly into SST and the correlation $r = S_{xy}/\\sqrt{S_{xx} S_{yy}}$.

**Standard error of the slope:** $\\text{SE}(\\hat{\\beta}_1) = s/\\sqrt{S_{xx}}$ quantifies uncertainty in the estimated slope and drives the $t$-statistic for testing $H_0: \\beta_1 = 0$."""

DEF_HE = """**שיפוע ונקודת חיתוך OLS:**
$$\\hat{\\beta}_1 = \\frac{S_{xy}}{S_{xx}}, \\qquad \\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}.$$

**ערך חזוי:** $\\hat{y}_i = \\hat{\\beta}_0 + \\hat{\\beta}_1 x_i$ — הערך על קו ההתאמה ב-$x_i$.

**שארית:** $e_i = y_i - \\hat{y}_i$ — המרחק האנכי מהנקודה הנצפית לקו. משוואות הנורמל של OLS מבטיחות $\\sum e_i = 0$ ו-$\\sum x_i e_i = 0$.

**פירוק שונות:**
$$\\text{SST} = \\sum (y_i - \\bar{y})^2 \\quad \\text{(שונות כוללת ב-}y\\text{)},$$
$$\\text{SSE} = \\sum (\\hat{y}_i - \\bar{y})^2 \\quad \\text{(מוסבר על ידי הרגרסיה)},$$
$$\\text{SSR} = \\sum e_i^2 \\quad \\text{(שארית — לא מוסבר)}.$$
זהות: $\\text{SST} = \\text{SSE} + \\text{SSR}$.

**מקדם ההסבר:**
$$R^2 = 1 - \\frac{\\text{SSR}}{\\text{SST}} = \\frac{\\text{SSE}}{\\text{SST}} = r^2,$$
כאשר $r$ הוא מתאם פירסון. $R^2 \\in [0,1]$ הוא שיעור השונות הכוללת ב-$y$ שמוסבר על ידי המודל הלינארי.

**שגיאה סטנדרטית של השאריות:** $s = \\sqrt{\\text{SSR}/(n-2)}$ מאמידה את $\\sigma$ ב-$y_i = \\beta_0 + \\beta_1 x_i + \\varepsilon_i$.

**סכומים חישוביים (שימושיים בבחינה):** $S_{xy} = \\sum x_i y_i - n\\bar{x}\\bar{y}$ ו-$S_{xx} = \\sum x_i^2 - n\\bar{x}^2$ חוסכים טבלת סטיות כשסכומי גולמיים נתונים. כך גם $S_{yy} = \\sum y_i^2 - n\\bar{y}^2$ נכנס ישירות ל-SST ולמתאם $r = S_{xy}/\\sqrt{S_{xx} S_{yy}}$.

**שגיאת תקן של השיפוע:** $\\text{SE}(\\hat{\\beta}_1) = s/\\sqrt{S_{xx}}$ מודדת אי-ודאות בשיפוע המוערך ומניעה את סטטיסטיקת $t$ לבדיקת $H_0: \\beta_1 = 0$."""

THEORY_EN = """**Classical OLS assumptions (Gauss–Markov):**
1. **Linearity:** $y_i = \\beta_0 + \\beta_1 x_i + \\varepsilon_i$.
2. **Exogeneity:** $x_i$ is fixed or independent of $\\varepsilon_i$.
3. **Zero mean errors:** $E[\\varepsilon_i] = 0$.
4. **Homoscedasticity:** $\\text{Var}(\\varepsilon_i) = \\sigma^2$ (constant variance).
5. **No autocorrelation:** $\\text{Cov}(\\varepsilon_i, \\varepsilon_j) = 0$ for $i \\neq j$.

**Gauss–Markov theorem:** Under assumptions 1–5, the OLS estimators $\\hat{\\beta}_0$ and $\\hat{\\beta}_1$ are **BLUE** — Best (minimum variance) Linear Unbiased Estimators. No other linear unbiased combination of the $y_i$ can beat OLS in variance.

**Why the line passes through $(\\bar{x}, \\bar{y})$:** From $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$, substituting $x = \\bar{x}$ gives $\\hat{y} = \\bar{y}$. The fitted line always pivots around the data centroid.

**Inference (add normality):** If $\\varepsilon_i \\sim N(0, \\sigma^2)$ i.i.d., then
$$\\frac{\\hat{\\beta}_1 - \\beta_1}{s/\\sqrt{S_{xx}}} \\sim t(n-2), \\qquad \\text{Var}(\\hat{\\beta}_1) = \\frac{\\sigma^2}{S_{xx}}.$$
Test $H_0: \\beta_1 = 0$ by comparing $|t|$ to $t_{\\alpha/2,\\, n-2}$. Wider spread in $x$ (larger $S_{xx}$) shrinks $\\text{SE}(\\hat{\\beta}_1)$ and increases power.

**Geometric intuition:** OLS chooses the line that makes the sum of **squared vertical** distances smallest. Squaring penalizes large outliers heavily and yields a differentiable objective with a unique minimum (when $S_{xx} > 0$). Minimizing absolute deviations instead gives LAD regression — robust but without a closed-form slope formula."""

THEORY_HE = """**הנחות OLS קלאסיות (גאוס–מרקוב):**
1. **לינאריות:** $y_i = \\beta_0 + \\beta_1 x_i + \\varepsilon_i$.
2. **אקסוגניות:** $x_i$ קבוע או בלתי-תלוי ב-$\\varepsilon_i$.
3. **שגיאות בממוצע אפס:** $E[\\varepsilon_i] = 0$.
4. **הומוסקדסטיות:** $\\text{Var}(\\varepsilon_i) = \\sigma^2$ (שונות קבועה).
5. **ללא אוטוקורלציה:** $\\text{Cov}(\\varepsilon_i, \\varepsilon_j) = 0$ ל-$i \\neq j$.

**משפט גאוס–מרקוב:** תחת הנחות 1–5, האומדים $\\hat{\\beta}_0$ ו-$\\hat{\\beta}_1$ הם **BLUE** — Linear Unbiased Estimators עם שונות מינימלית. שום צירוף לינארי חסר-הטיה אחר של $y_i$ לא מנצח את OLS בשונות.

**למה הקו עובר דרך $(\\bar{x}, \\bar{y})$:** מ-$\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$, הצבת $x = \\bar{x}$ נותנת $\\hat{y} = \\bar{y}$. קו ההתאמה תמיד מסתובב סביב מרכז הכובל של הנתונים.

**הסקה (עם נורמליות):** אם $\\varepsilon_i \\sim N(0, \\sigma^2)$ i.i.d., אז
$$\\frac{\\hat{\\beta}_1 - \\beta_1}{s/\\sqrt{S_{xx}}} \\sim t(n-2), \\qquad \\text{Var}(\\hat{\\beta}_1) = \\frac{\\sigma^2}{S_{xx}}.$$
בדקו $H_0: \\beta_1 = 0$ בהשוואת $|t|$ ל-$t_{\\alpha/2,\\, n-2}$. פיזור רחב יותר ב-$x$ ($S_{xx}$ גדול) מקטין $\\text{SE}(\\hat{\\beta}_1)$ ומגדיל עוצמה.

**אינטואיציה גאומטרית:** OLS בוחרת את הקו שממזער סכום **ריבועי** המרחקים האנכיים. ריבוע מעניש משקל לערכים קיצוניים ונותן מטרה גזירה עם מינימום יחיד (כש-$S_{xx} > 0$). מינימיזציה של סטיות מוחלטות נותנת LAD — עמיד יותר אך בלי נוסחת שיפוע סגורה."""

WE1_EN = """**Data:** $(x,y)$ pairs: $(1,2),(2,3),(3,5),(4,4),(5,6)$.

We fit $\\hat{y} = \\hat{\\beta}_0 + \\hat{\\beta}_1 x$ using the computational shortcut: once $\\bar{x}$, $\\bar{y}$, $S_{xy}$, and $S_{xx}$ are known, the slope and intercept follow directly. This five-point dataset is small enough to build a full deviation table — a pattern repeated on nearly every Israeli statistics exam.

### Move 1: Compute means
$$\\bar{x} = \\frac{1+2+3+4+5}{5} = 3, \\qquad \\bar{y} = \\frac{2+3+5+4+6}{5} = 4.$$

### Move 2: Build the deviation table

| $i$ | $x_i-\\bar{x}$ | $y_i-\\bar{y}$ | product | $(x-\\bar{x})^2$ |
|---|---|---|---|---|
| 1 | $-2$ | $-2$ | $4$ | $4$ |
| 2 | $-1$ | $-1$ | $1$ | $1$ |
| 3 | $0$ | $1$ | $0$ | $0$ |
| 4 | $1$ | $0$ | $0$ | $1$ |
| 5 | $2$ | $2$ | $4$ | $4$ |
| **Sum** | | | **$9$** | **$10$** |

So $S_{xy} = 9$ and $S_{xx} = 10$.

### Move 3: Apply OLS formulas
$$\\hat{\\beta}_1 = \\frac{9}{10} = 0.9, \\qquad \\hat{\\beta}_0 = 4 - 0.9 \\times 3 = 1.3.$$

**Regression line:** $\\hat{y} = 1.3 + 0.9x$.

**Interpretation:** For each 1-unit increase in $x$, the predicted $y$ increases by 0.9 units. **Sanity check:** the line passes through $(\\bar{x}, \\bar{y}) = (3, 4)$ since $1.3 + 0.9(3) = 4$. **Exam note:** always report both $\\hat{\\beta}_0$ and $\\hat{\\beta}_1$, then write the full line equation — partial formulas alone lose marks on Israeli statistics finals. A negative intercept here ($1.3$) is perfectly valid when $x = 0$ lies outside the data range."""

WE1_HE = """**נתונים:** זוגות $(x,y)$: $(1,2),(2,3),(3,5),(4,4),(5,6)$.

נתאים $\\hat{y} = \\hat{\\beta}_0 + \\hat{\\beta}_1 x$ בקיצור חישובי: ברגע ש-$\\bar{x}$, $\\bar{y}$, $S_{xy}$ ו-$S_{xx}$ ידועים, השיפוע ונקודת החיתוך נקבעים ישירות. מערך חמש נקודות קטן מספיק לטבלת סטיות מלאה — דפוס שחוזר בכמעט כל בחינת סטטיסטיקה ישראלית.

### צעד 1: חישוב ממוצעים
$$\\bar{x} = \\frac{1+2+3+4+5}{5} = 3, \\qquad \\bar{y} = \\frac{2+3+5+4+6}{5} = 4.$$

### צעד 2: בניית טבלת סטיות

| $i$ | $x_i-\\bar{x}$ | $y_i-\\bar{y}$ | מכפלה | $(x-\\bar{x})^2$ |
|---|---|---|---|---|
| 1 | $-2$ | $-2$ | $4$ | $4$ |
| 2 | $-1$ | $-1$ | $1$ | $1$ |
| 3 | $0$ | $1$ | $0$ | $0$ |
| 4 | $1$ | $0$ | $0$ | $1$ |
| 5 | $2$ | $2$ | $4$ | $4$ |
| **סכום** | | | **$9$** | **$10$** |

לכן $S_{xy} = 9$ ו-$S_{xx} = 10$.

### צעד 3: יישום נוסחאות OLS
$$\\hat{\\beta}_1 = \\frac{9}{10} = 0.9, \\qquad \\hat{\\beta}_0 = 4 - 0.9 \\times 3 = 1.3.$$

**קו רגרסיה:** $\\hat{y} = 1.3 + 0.9x$.

**פרשנות:** לכל עלייה של יחידה אחת ב-$x$, $y$ החזוי עולה ב-0.9 יחידות. **בדיקת הגיון:** הקו עובר דרך $(\\bar{x}, \\bar{y}) = (3, 4)$ כי $1.3 + 0.9(3) = 4$. **הערת בחינה:** דווחו תמיד $\\hat{\\beta}_0$ ו-$\\hat{\\beta}_1$ ואז כתבו את משוואת הקו המלאה — נוסחאות חלקיות מאבדות ניקוד בבחינות סטטיסטיקה. חיתוך חיובי ($1.3$) תקין גם כש-$x = 0$ מחוץ לטווח הנתונים."""

WE2_EN = """Using the fitted line from Example 1 ($\\hat{y} = 1.3 + 0.9x$), we compute residuals, SSR, SST, and $R^2$ to measure how well the line explains variation in $y$.

### Move 1: Compute predicted values and residuals

| $i$ | $x_i$ | $y_i$ | $\\hat{y}_i=1.3+0.9x_i$ | $e_i=y_i-\\hat{y}_i$ | $e_i^2$ | $(y_i-\\bar{y})^2$ |
|---|---|---|---|---|---|---|
| 1 | 1 | 2 | 2.2 | $-0.2$ | 0.04 | 4 |
| 2 | 2 | 3 | 3.1 | $-0.1$ | 0.01 | 1 |
| 3 | 3 | 5 | 4.0 | 1.0 | 1.00 | 1 |
| 4 | 4 | 4 | 4.9 | $-0.9$ | 0.81 | 0 |
| 5 | 5 | 6 | 5.8 | 0.2 | 0.04 | 4 |
| **Sum** | | | | **0** | **1.90** | **10** |

Note $\\sum e_i = 0$ as guaranteed by OLS.

### Move 2: Compute sums of squares
$$\\text{SSR} = \\sum e_i^2 = 1.90, \\quad \\text{SST} = \\sum(y_i - \\bar{y})^2 = 10.$$

### Move 3: Compute $R^2$
$$R^2 = 1 - \\frac{\\text{SSR}}{\\text{SST}} = 1 - \\frac{1.90}{10} = 0.81.$$

**Interpretation:** 81% of the total variance in $y$ is explained by the linear relationship with $x$. The remaining 19% is captured in the residual sum of squares. **Cross-check:** $r = S_{xy}/\\sqrt{S_{xx} S_{yy}}$; here $r^2 = 0.81$ matches $R^2$ exactly. **Residual plot tip:** with only five points, always verify $\\sum e_i = 0$ — a non-zero sum signals an arithmetic error in $\\hat{y}_i$."""

WE2_HE = """בעזרת קו ההתאמה מדוגמה 1 ($\\hat{y} = 1.3 + 0.9x$), נחשב שאריות, SSR, SST ו-$R^2$ כדי למדוד עד כמה הקו מסביר את השונות ב-$y$.

### צעד 1: חישוב ערכים חזויים ושאריות

| $i$ | $x_i$ | $y_i$ | $\\hat{y}_i$ | $e_i$ | $e_i^2$ | $(y_i-\\bar{y})^2$ |
|---|---|---|---|---|---|---|
| 1 | 1 | 2 | 2.2 | $-0.2$ | 0.04 | 4 |
| 2 | 2 | 3 | 3.1 | $-0.1$ | 0.01 | 1 |
| 3 | 3 | 5 | 4.0 | 1.0 | 1.00 | 1 |
| 4 | 4 | 4 | 4.9 | $-0.9$ | 0.81 | 0 |
| 5 | 5 | 6 | 5.8 | 0.2 | 0.04 | 4 |
| **סכום** | | | | **0** | **1.90** | **10** |

שימו לב $\\sum e_i = 0$ כפי ש-OLS מבטיח.

### צעד 2: חישוב סכומי ריבועים
$$\\text{SSR} = 1.90, \\quad \\text{SST} = 10.$$

### צעד 3: חישוב $R^2$
$$R^2 = 1 - \\frac{1.90}{10} = 0.81.$$

**פרשנות:** 81% מהשונות הכוללת ב-$y$ מוסברת על ידי הקשר הלינארי עם $x$. 19% הנותרים נתפסים ב-SSR. **בדיקה:** $r^2 = R^2$ — מתאם פירסון בריבוע שווה למקדם ההסבר. **טיפ:** עם חמש נקודות בלבד, אמתו $\\sum e_i = 0$ — סכום לא-אפס מסמן טעות חשבון ב-$\\hat{y}_i$."""

WE3_EN = """**Derive the OLS formulas for $\\hat{\\beta}_0$ and $\\hat{\\beta}_1$ that minimize SSR.**

This derivation is a standard proof on Israeli university exams. The key idea: differentiate the sum of squared residuals with respect to each parameter and set derivatives to zero (normal equations).

### Move 1: Write the objective
$$Q(\\beta_0, \\beta_1) = \\sum_{i=1}^n (y_i - \\beta_0 - \\beta_1 x_i)^2.$$

### Move 2: First-order conditions
$$\\frac{\\partial Q}{\\partial \\beta_0} = -2\\sum(y_i - \\beta_0 - \\beta_1 x_i) = 0 \\Rightarrow \\sum y_i = n\\beta_0 + \\beta_1\\sum x_i. \\quad (1)$$
$$\\frac{\\partial Q}{\\partial \\beta_1} = -2\\sum x_i(y_i - \\beta_0 - \\beta_1 x_i) = 0 \\Rightarrow \\sum x_i y_i = \\beta_0\\sum x_i + \\beta_1\\sum x_i^2. \\quad (2)$$

### Move 3: Solve for intercept
Divide (1) by $n$: $\\bar{y} = \\beta_0 + \\beta_1 \\bar{x}$, so $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.

### Move 4: Solve for slope
Substitute into (2) and simplify using $S_{xy} = \\sum x_i y_i - n\\bar{x}\\bar{y}$ and $S_{xx} = \\sum x_i^2 - n\\bar{x}^2$:
$$\\hat{\\beta}_1 = \\frac{S_{xy}}{S_{xx}}. \\quad \\blacksquare$$

**Second-order check:** $\\partial^2 Q / \\partial \\beta_1^2 = 2 S_{xx} > 0$ confirms a minimum when $x$ is not constant. **Exam strategy:** write the objective $Q$, the two partial derivatives, substitute $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$, then simplify to $S_{xy}/S_{xx}$ — graders award marks for each visible step. This three-page proof is worth 10–15 points on Technion probability exams."""

WE3_HE = """**גזרו את נוסחאות OLS ל-$\\hat{\\beta}_0$ ו-$\\hat{\\beta}_1$ שממזערות SSR.**

גזירה זו הוכחה סטנדרטית בבחינות אוניברסיטאיות ישראליות. הרעיון המרכזי: גזרו את סכום ריבועי השאריות לפי כל פרמטר והשווו לאפס (משוואות נורמל).

### צעד 1: כתיבת פונקציית המטרה
$$Q(\\beta_0, \\beta_1) = \\sum_{i=1}^n (y_i - \\beta_0 - \\beta_1 x_i)^2.$$

### צעד 2: תנאי ראשון
$$\\frac{\\partial Q}{\\partial \\beta_0} = 0 \\Rightarrow \\sum y_i = n\\beta_0 + \\beta_1\\sum x_i. \\quad (1)$$
$$\\frac{\\partial Q}{\\partial \\beta_1} = 0 \\Rightarrow \\sum x_i y_i = \\beta_0\\sum x_i + \\beta_1\\sum x_i^2. \\quad (2)$$

### צעד 3: פתרון לנקודת חיתוך
חלוקת (1) ב-$n$: $\\bar{y} = \\beta_0 + \\beta_1 \\bar{x}$, ולכן $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.

### צעד 4: פתרון לשיפוע
הצבה ב-(2) ופישוט עם $S_{xy}$ ו-$S_{xx}$:
$$\\hat{\\beta}_1 = \\frac{S_{xy}}{S_{xx}}. \\quad \\blacksquare$$

**בדיקת סדר שני:** $\\partial^2 Q / \\partial \\beta_1^2 = 2 S_{xx} > 0$ מאשרת מינימום כש-$x$ לא קבוע. **אסטרטגיית בחינה:** כתבו $Q$, שתי הנגזרות החלקיות, הציבו $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$, ופשטו ל-$S_{xy}/S_{xx}$ — בודקים נותנים ניקוד לכל שלב גלוי. הוכחה זו שווה 10–15 נקודות בבחינות הסתברות בטכניון."""

CKPT1_EN = """For data with $\\bar{x}=5$, $\\bar{y}=20$, $S_{xy}=30$, $S_{xx}=15$, find $\\hat{\\beta}_1$ and $\\hat{\\beta}_0$.

**Step 1:** Apply the slope formula directly:
$$\\hat{\\beta}_1 = \\frac{S_{xy}}{S_{xx}} = \\frac{30}{15} = 2.$$

**Step 2:** Use the intercept identity $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$:
$$\\hat{\\beta}_0 = 20 - 2(5) = 20 - 10 = 10.$$

**Step 3:** Write the regression line:
$$\\hat{y} = 10 + 2x.$$

**Sanity checks:** (a) Slope 2 means each +1 in $x$ raises predicted $y$ by 2. (b) At $x = \\bar{x} = 5$: $\\hat{y} = 10 + 2(5) = 20 = \\bar{y}$ — the line passes through the centroid as required."""

CKPT1_HE = """עבור נתונים עם $\\bar{x}=5$, $\\bar{y}=20$, $S_{xy}=30$, $S_{xx}=15$, מצאו $\\hat{\\beta}_1$ ו-$\\hat{\\beta}_0$.

**שלב 1:** יישום נוסחת השיפוע:
$$\\hat{\\beta}_1 = \\frac{30}{15} = 2.$$

**שלב 2:** נוסחת נקודת החיתוך $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$:
$$\\hat{\\beta}_0 = 20 - 2(5) = 10.$$

**שלב 3:** כתיבת קו הרגרסיה:
$$\\hat{y} = 10 + 2x.$$

**בדיקות הגיון:** (א) שיפוע 2 = עלייה של 2 ב-$y$ החזוי לכל +1 ב-$x$. (ב) ב-$x = \\bar{x} = 5$: $\\hat{y} = 20 = \\bar{y}$ — הקו עובר דרך מרכז הכובל."""

CKPT2_EN = """A regression has SST = 200 and SSR = 50. Find $R^2$ and interpret it.

**Step 1:** Apply the definition:
$$R^2 = 1 - \\frac{\\text{SSR}}{\\text{SST}} = 1 - \\frac{50}{200} = 1 - 0.25 = 0.75.$$

**Step 2:** Interpret in context:
75% of the total variance in the response variable $y$ is explained by the linear regression model. The remaining 25% ($\\text{SSR}/\\text{SST} = 0.25$) is unexplained residual variation.

**Step 3:** Sanity check — $R^2$ must lie in $[0, 1]$. Here $0.75$ is plausible. If SSR were 0, $R^2 = 1$ (perfect fit); if SSR = SST, $R^2 = 0$ (the line explains nothing beyond $\\bar{y}$)."""

CKPT2_HE = """לרגרסיה SST = 200 ו-SSR = 50. מצאו $R^2$ ופרשו.

**שלב 1:** יישום ההגדרה:
$$R^2 = 1 - \\frac{50}{200} = 0.75.$$

**שלב 2:** פרשנות:
75% מהשונות הכוללת במשתנה התגובה $y$ מוסברת על ידי מודל הרגרסיה הלינארי. 25% הנותרים ($\\text{SSR}/\\text{SST}$) הם שונות שארית לא מוסברת.

**שלב 3:** בדיקת הגיון — $R^2$ חייב להיות ב-$[0, 1]$. כאן 0.75 סביר. אם SSR = 0, $R^2 = 1$ (התאמה מושלמת); אם SSR = SST, $R^2 = 0$ (הקו לא מסביר מעבר ל-$\\bar{y}$)."""

METHOD_EN = """**7-step OLS regression procedure:**
1. Compute $\\bar{x}$, $\\bar{y}$.
2. Build deviation table; compute $S_{xx} = \\sum(x_i - \\bar{x})^2$ and $S_{xy} = \\sum(x_i - \\bar{x})(y_i - \\bar{y})$.
3. Slope: $\\hat{\\beta}_1 = S_{xy}/S_{xx}$; intercept: $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.
4. Predicted values $\\hat{y}_i$; residuals $e_i = y_i - \\hat{y}_i$; verify $\\sum e_i = 0$.
5. $\\text{SSR} = \\sum e_i^2$; $\\text{SST} = S_{yy} = \\sum(y_i - \\bar{y})^2$.
6. $R^2 = 1 - \\text{SSR}/\\text{SST}$; correlation $r = \\pm\\sqrt{R^2}$ (sign = sign of $\\hat{\\beta}_1$).
7. Residual standard error $s = \\sqrt{\\text{SSR}/(n-2)}$; for inference, $\\text{SE}(\\hat{\\beta}_1) = s/\\sqrt{S_{xx}}$.

| Quantity | Formula | Exam use |
|---|---|---|
| Slope | $S_{xy}/S_{xx}$ | Always compute first |
| Intercept | $\\bar{y} - \\hat{\\beta}_1 \\bar{x}$ | Never guess — use formula |
| $R^2$ | $1 - \\text{SSR}/\\text{SST}$ | Interpret as % variance explained |
| $t$-stat | $\\hat{\\beta}_1 / \\text{SE}(\\hat{\\beta}_1)$ | Test $H_0: \\beta_1 = 0$ |

**Decision shortcut:** If summary stats $S_{xy}$, $S_{xx}$, $\\bar{x}$, $\\bar{y}$ are given, skip raw data table and go straight to step 3."""

METHOD_HE = """**7 שלבי רגרסיה OLS:**
1. חשבו $\\bar{x}$, $\\bar{y}$.
2. בנו טבלת סטיות; $S_{xx}$ ו-$S_{xy}$.
3. שיפוע: $\\hat{\\beta}_1 = S_{xy}/S_{xx}$; חיתוך: $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.
4. ערכים חזויים $\\hat{y}_i$; שאריות $e_i$; אמתו $\\sum e_i = 0$.
5. $\\text{SSR} = \\sum e_i^2$; $\\text{SST} = S_{yy}$.
6. $R^2 = 1 - \\text{SSR}/\\text{SST}$; $r = \\pm\\sqrt{R^2}$ (סימן = סימן $\\hat{\\beta}_1$).
7. $s = \\sqrt{\\text{SSR}/(n-2)}$; להסקה: $\\text{SE}(\\hat{\\beta}_1) = s/\\sqrt{S_{xx}}$.

| גודל | נוסחה | שימוש בבחינה |
|---|---|---|
| שיפוע | $S_{xy}/S_{xx}$ | תמיד ראשון |
| חיתוך | $\\bar{y} - \\hat{\\beta}_1 \\bar{x}$ | לעולם לא לנחש |
| $R^2$ | $1 - \\text{SSR}/\\text{SST}$ | % שונות מוסבר |
| $t$ | $\\hat{\\beta}_1 / \\text{SE}(\\hat{\\beta}_1)$ | בדיקת $H_0: \\beta_1 = 0$ |

**קיצור:** אם ניתנו $S_{xy}$, $S_{xx}$, $\\bar{x}$, $\\bar{y}$ — דלגו ישר לשלב 3."""

PITFALL_EN = """1. **Reversing $x$ and $y$.** The OLS line for predicting $y$ from $x$ differs from predicting $x$ from $y$ — they are **not** the same line! Only the line with $y$ as response minimizes vertical residuals.

2. **Using $R^2$ as the sole criterion.** High $R^2$ can arise from outliers, overfitting with few points, or a misspecified linear model when the true relationship is curved. Always inspect a scatter plot and residual plot.

3. **Ignoring residual patterns.** If residuals show a U-shape vs. $\\hat{y}$ or fan out with $x$, homoscedasticity or linearity is violated. OLS inference becomes unreliable even if $R^2$ looks good.

4. **Extrapolation beyond observed $x$.** Predicting far outside the data range assumes the linear trend continues — often false. Israeli exam questions love asking you to flag unjustified extrapolation.

5. **Confusing association with causation.** A significant slope shows $x$ and $y$ co-vary; it does **not** prove $x$ causes $y$. Confounders and reverse causality are common traps in applied problems."""

PITFALL_HE = """1. **היפוך $x$ ו-$y$.** קו OLS לחיזוי $y$ מ-$x$ שונה מחיזוי $x$ מ-$y$ — **לא** אותו קו! רק הקו עם $y$ כתגובה ממזער שאריות אנכיות.

2. **שימוש ב-$R^2$ כקריטריון יחיד.** $R^2$ גבוה יכול לנבוע מערכים קיצוניים, over-fitting עם מעט נקודות, או מודל לינארי שגוי כשהקשר אמיתי מעוקל. תמיד בדקו scatter plot וגרף שאריות.

3. **התעלמות מדפוסי שאריות.** אם שאריות מראות צורת U מול $\\hat{y}$ או מתפשטות עם $x$, הומוסקדסטיות או לינאריות נפגעות. הסקת OLS לא אמינה גם אם $R^2$ נראה טוב.

4. **אקסטרפולציה מחוץ לטווח $x$.** חיזוי רחוק מחוץ לנתונים מניח שהמגמה הלינארית נמשכת — לעיתים קרובות שגוי. שאלות בחינה ישראליות אוהבות לבקש לסמן אקסטרפולציה לא מוצדקת.

5. **בלבול קשר עם סיבתיות.** שיפוע מובהק מראה ש-$x$ ו-$y$ משתנים יחד; זה **לא** מוכיח ש-$x$ גורם ל-$y$. גורמים מסבירים וסיבתיות הפוכה הם מלכודות נפוצות."""

WHY_EN = """Linear regression is the workhorse of applied statistics — from forecasting sales to calibrating lab instruments to estimating dose–response curves in pharmacology.

**Why it matters for exams:** Israeli university courses (statistics, econometrics, engineering) routinely ask you to compute OLS from a table, interpret $\\hat{\\beta}_1$ in context, prove the normal equations, and test $H_0: \\beta_1 = 0$. Bagrut 5-unit statistics links correlation $r$ directly to $R^2 = r^2$.

**Cross-subject links:** In physics, linearizing data ($\\log y$ vs $x$) reduces curved relationships to OLS form. In `concept:linear_regression_correlation`, you learned $r$; here you learn **why** squaring it gives the fraction of variance explained. In `concept:hypothesis_testing_intro`, the $t$-test on $\\hat{\\beta}_1$ uses the same logic as testing a population mean."""

WHY_HE = """רגרסיה לינארית היא כלי העבודה של סטטיסטיקה יישומית — מחיזוי מכירות וכיול מכשירי מעבדה ועד הערכת עקומות מינון–תגובה בפרמקולוגיה.

**למה זה חשוב לבחינות:** קורסים אוניברסיטאיים (סטטיסטיקה, אקונומטריקה, הנדסה) שואלים שוב ושוב לחשב OLS מטבלה, לפרש $\\hat{\\beta}_1$ בהקשר, להוכיח משוואות נורמל, ולבדוק $H_0: \\beta_1 = 0$. בגרות 5 יחידות מקשרת מתאם $r$ ישירות ל-$R^2 = r^2$.

**קשרים בין-מקצועיים:** בפיזיקה, ליניאריזציה ($\\log y$ מול $x$) ממירה קשרים מעוקלים לצורת OLS. ב-`concept:linear_regression_correlation` למדתם $r$; כאן למדים **למה** ריבועו נותן את שיעור השונות המוסבר. ב-`concept:hypothesis_testing_intro`, מבחן $t$ על $\\hat{\\beta}_1$ משתמש באותה לוגיקה כמו בדיקת ממוצע אוכלוסייה."""

BEFORE_EN = """**Formula card:**
- $\\hat{\\beta}_1 = S_{xy}/S_{xx}$, $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$
- $S_{xy} = \\sum(x_i - \\bar{x})(y_i - \\bar{y})$; $S_{xx} = \\sum(x_i - \\bar{x})^2$; $S_{yy} = \\sum(y_i - \\bar{y})^2$
- $R^2 = 1 - \\text{SSR}/\\text{SST} = r^2$; residuals: $e_i = y_i - \\hat{y}_i$, $\\sum e_i = 0$
- $s = \\sqrt{\\text{SSR}/(n-2)}$; $\\text{SE}(\\hat{\\beta}_1) = s/\\sqrt{S_{xx}}$
- $\\text{Var}(\\hat{\\beta}_1) = \\sigma^2/S_{xx}$; $t = \\hat{\\beta}_1/\\text{SE}(\\hat{\\beta}_1) \\sim t(n-2)$

**Exam patterns:** Compute OLS line from table or summary stats; find $R^2$ and interpret; prove $\\sum e_i = 0$ or derive OLS formulas; conduct $t$-test on slope; explain why $R^2 = r^2$.

**Last review:** Derive $\\hat{\\beta}_1 = S_{xy}/S_{xx}$ from the normal equations once from memory, then solve one checkpoint without notes. Say each formula aloud — SST, SSR, SSE, and $R^2$ are often confused under time pressure. Remember: the line always passes through $(\\bar{x}, \\bar{y})$."""

BEFORE_HE = """**גיליון נוסחאות:**
- $\\hat{\\beta}_1 = S_{xy}/S_{xx}$, $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$
- $S_{xy}$, $S_{xx}$, $S_{yy}$ — סכומי סטיות
- $R^2 = 1 - \\text{SSR}/\\text{SST} = r^2$; $e_i = y_i - \\hat{y}_i$, $\\sum e_i = 0$
- $s = \\sqrt{\\text{SSR}/(n-2)}$; $\\text{SE}(\\hat{\\beta}_1) = s/\\sqrt{S_{xx}}$
- $\\text{Var}(\\hat{\\beta}_1) = \\sigma^2/S_{xx}$; $t \\sim t(n-2)$

**דפוסי בחינה:** חישוב קו OLS מטבלה או סטטיסטיקות סיכום; $R^2$ ופרשנות; הוכחת $\\sum e_i = 0$ או גזירת נוסחאות; מבחן $t$ על שיפוע; הסבר $R^2 = r^2$.

**חזרה אחרונה:** גזרו $\\hat{\\beta}_1 = S_{xy}/S_{xx}$ ממשוואות נורמל פעם אחת מהזיכרון, ואז פתרו checkpoint אחד בלי רשימות. אמרו כל נוסחה בקול — SST, SSR, SSE ו-$R^2$ מתבלבלים לעיתים תחת לחץ זמן. הקו תמיד עובר דרך $(\\bar{x}, \\bar{y})$."""

SUMMARY_EN = """- **OLS** minimizes $\\sum(y_i - \\hat{y}_i)^2$; $\\hat{\\beta}_1 = S_{xy}/S_{xx}$, $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.
- **Residuals** $e_i = y_i - \\hat{y}_i$ satisfy $\\sum e_i = 0$; the fitted line passes through $(\\bar{x}, \\bar{y})$.
- **$R^2 = 1 - \\text{SSR}/\\text{SST}$** measures proportion of variance explained; equals $r^2$.
- **Gauss–Markov:** OLS is BLUE under classical assumptions (linearity, exogeneity, homoscedasticity, no autocorrelation).
- **Inference:** $t = \\hat{\\beta}_1/\\text{SE}(\\hat{\\beta}_1) \\sim t(n-2)$ tests whether slope differs from zero.

**Takeaway:** Given summary statistics or a data table, you should now execute the full OLS pipeline — fit, residuals, $R^2$, and slope test — without hesitation."""

SUMMARY_HE = """- **OLS** ממזער $\\sum e_i^2$; $\\hat{\\beta}_1 = S_{xy}/S_{xx}$, $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.
- **שאריות** $e_i = y_i - \\hat{y}_i$ מקיימות $\\sum e_i = 0$; הקו עובר דרך $(\\bar{x}, \\bar{y})$.
- **$R^2 = 1 - \\text{SSR}/\\text{SST}$** מודד שיעור שונות מוסבר; שווה ל-$r^2$.
- **גאוס–מרקוב:** OLS הוא BLUE תחת הנחות קלאסיות.
- **הסקה:** $t = \\hat{\\beta}_1/\\text{SE}(\\hat{\\beta}_1) \\sim t(n-2)$ בודק אם השיפוע שונה מאפס.

**מסקנה:** עם סטטיסטיקות סיכום או טבלת נתונים, עליכם כעת לבצע את צינור OLS המלא — התאמה, שאריות, $R^2$ ומבחן שיפוע — ללא היסוס."""

Q_EXPL = [
    fmt_expl(
        "$\\hat{\\beta}_1 = S_{xy}/S_{xx} = 20/5 = 4$. Then $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x} = 10 - 4(4) = 10 - 16 = -6$. The regression line is $\\hat{y} = -6 + 4x$.",
        "When summary statistics are given, go directly to the two OLS formulas — no raw data table needed. Slope first, then intercept using the centroid identity.",
        "Computing $\\hat{\\beta}_0 = \\bar{y} + \\hat{\\beta}_1 \\bar{x}$ (wrong sign). Using $S_{xy}/S_{yy}$ instead of $S_{xy}/S_{xx}$ for the slope.",
        "Always verify the line passes through $(\\bar{x}, \\bar{y})$: plug in $\\bar{x}$ and confirm you get $\\bar{y}$. This 5-second check catches sign errors on every exam.",
        "$\\hat{\\beta}_1 = 20/5 = 4$. אז $\\hat{\\beta}_0 = 10 - 4(4) = -6$. קו הרגרסיה: $\\hat{y} = -6 + 4x$.",
        "כשניתנות סטטיסטיקות סיכום, עברו ישירות לשתי נוסחאות OLS — בלי טבלת נתונים גולמית. שיפוע קודם, ואז חיתוך עם זהות מרכז הכובל.",
        "חישוב $\\hat{\\beta}_0 = \\bar{y} + \\hat{\\beta}_1 \\bar{x}$ (סימן שגוי). שימוש ב-$S_{xy}/S_{yy}$ במקום $S_{xy}/S_{xx}$ לשיפוע.",
        "תמיד ודאו שהקו עובר דרך $(\\bar{x}, \\bar{y})$: הציבו $\\bar{x}$ ואשרו שמתקבל $\\bar{y}$. בדיקה של חמש שניות תופסת טעויות סימן בכל בחינה. כתבו את משוואת הקו המלאה $\\hat{y} = -6 + 4x$ ולא רק את השיפוע.",
    ),
    fmt_expl(
        "The OLS regression line always passes through the centroid $(\\bar{x}, \\bar{y})$. This follows directly from $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$: at $x = \\bar{x}$, we get $\\hat{y} = \\bar{y}$.",
        "Think of OLS as pivoting a line around the data center. Any line that fits best must go through the average point — otherwise you could shift the intercept and reduce SSR.",
        "Answering $(0, 0)$ or the first data point $(x_1, y_1)$. Confusing the centroid with the predicted value at $x = 0$.",
        "This is a one-mark conceptual question on nearly every exam. Memorize: centroid, not origin, not first point.",
        "קו הרגרסיה OLS תמיד עובר דרך מרכז הכובל $(\\bar{x}, \\bar{y})$. זה נובע ישירות מ-$\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$: ב-$x = \\bar{x}$ מתקבל $\\hat{y} = \\bar{y}$.",
        "חשבו על OLS כקו שמסתובב סביב מרכז הנתונים. כל קו התאמה אופטימלי חייב לעבור דרך הנקודה הממוצעת — אחרת אפשר להזיז חיתוך ולהקטין SSR.",
        "תשובה $(0, 0)$ או הנקודה הראשונה $(x_1, y_1)$. בלבול מרכז כובל עם ערך חזוי ב-$x = 0$.",
        "שאלה מושגית של נקודה אחת בכמעט כל בחינה. שיננו: מרכז כובל, לא ראשית, לא נקודה ראשונה.",
    ),
    fmt_expl(
        "$R^2 = 1 - \\text{SSR}/\\text{SST} = 1 - 20/100 = 1 - 0.20 = 0.80$. This means 80% of the total variance in $y$ is explained by the linear regression model.",
        "SSR is what the line could NOT explain; SST is total variation. The ratio SSR/SST is the unexplained fraction; subtract from 1 to get the explained fraction.",
        "Computing $R^2 = \\text{SSR}/\\text{SST}$ (forgetting to subtract from 1). Swapping SSR and SST in the formula.",
        "Write $R^2 = 1 - \\text{SSR}/\\text{SST}$ on your formula card in large letters. The \"1 minus\" is the most common arithmetic slip.",
        "$R^2 = 1 - 20/100 = 0.80$. כלומר 80% מהשונות הכוללת ב-$y$ מוסברת על ידי מודל הרגרסיה הלינארי.",
        "SSR הוא מה שהקו לא הצליח להסביר; SST הוא השונות הכוללת. יחס SSR/SST הוא החלק שלא מוסבר; מחסרים מ-1 לקבלת החלק המוסבר.",
        "חישוב $R^2 = \\text{SSR}/\\text{SST}$ (שכחת \"1 פחות\"). החלפת SSR ו-SST בנוסחה.",
        "כתבו $R^2 = 1 - \\text{SSR}/\\text{SST}$ בגיליון הנוסחאות באותיות גדולות. ה-\"1 פחות\" הוא הטעות החשבונית הנפוצה ביותר. פרשו 0.80 כ-80% מהשונות ב-$y$ שמוסברת על ידי המודל הלינארי.",
    ),
    fmt_expl(
        "$\\sum e_i = \\sum(y_i - \\hat{\\beta}_0 - \\hat{\\beta}_1 x_i) = \\sum y_i - n\\hat{\\beta}_0 - \\hat{\\beta}_1 \\sum x_i = n\\bar{y} - n(\\bar{y} - \\hat{\\beta}_1 \\bar{x}) - \\hat{\\beta}_1 n\\bar{x} = 0$. $\\blacksquare$",
        "This proof uses only the intercept formula — no numbers needed. Expand the sum, substitute $n\\bar{y}$ and $n\\bar{x}$, and watch the terms cancel.",
        "Stopping after $\\sum e_i = \\sum y_i - n\\hat{\\beta}_0 - \\hat{\\beta}_1 \\sum x_i$ without substituting the OLS intercept. Claiming residuals sum to zero for ANY line (only OLS guarantees this).",
        "Proof questions give full credit for correct substitution of $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$. Write the normal equation $\\sum e_i = 0$ as your starting point.",
        "$\\sum e_i = \\sum(y_i - \\hat{\\beta}_0 - \\hat{\\beta}_1 x_i) = n\\bar{y} - n(\\bar{y} - \\hat{\\beta}_1 \\bar{x}) - \\hat{\\beta}_1 n\\bar{x} = 0$. $\\blacksquare$ זוהי תוצאה אלגברית שמבוססת על $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$.",
        "הוכחה זו משתמשת רק בנוסחת החיתוך — בלי מספרים. פתחו את הסכום, הציבו $n\\bar{y}$ ו-$n\\bar{x}$, וצפו בביטויים שמתקזזים לחלוטין.",
        "עצירה אחרי $\\sum e_i = \\sum y_i - n\\hat{\\beta}_0 - \\hat{\\beta}_1 \\sum x_i$ בלי הצבת חיתוך OLS. טענה ששאריות מתאפסות לכל קו (רק OLS מבטיח זאת).",
        "שאלות הוכחה נותנות ניקוד מלא להצבה נכונה של $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$. כתבו $\\sum e_i = 0$ כנקודת התחלה. הוכיחו שהביטויים מתקזזים — לא צריך מספרים כלל.",
    ),
    fmt_expl(
        "$\\bar{x} = 6$, $\\bar{y} = 11$. Deviations give $S_{xy} = (-4)(-6)+(-2)(-2)+0+2(2)+4(6) = 24+4+0+4+24 = 56$ and $S_{xx} = 16+4+0+4+16 = 40$. So $\\hat{\\beta}_1 = 56/40 = 1.4$ and $\\hat{\\beta}_0 = 11 - 1.4(6) = 2.6$. Line: $\\hat{y} = 2.6 + 1.4x$.",
        "Build a deviation table systematically: compute $x_i - \\bar{x}$ and $y_i - \\bar{y}$ for each row, then sum products for $S_{xy}$ and squared deviations for $S_{xx}$.",
        "Arithmetic errors in the deviation products (especially sign errors with negative deviations). Forgetting to subtract $\\hat{\\beta}_1 \\bar{x}$ when computing intercept.",
        "After computing $\\hat{\\beta}_1$, always finish with $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$ — never leave the answer as slope only. Check centroid in 5 seconds.",
        "$\\bar{x} = 6$, $\\bar{y} = 11$. $S_{xy} = 56$, $S_{xx} = 40$. $\\hat{\\beta}_1 = 56/40 = 1.4$, $\\hat{\\beta}_0 = 11 - 1.4(6) = 2.6$. קו: $\\hat{y} = 2.6 + 1.4x$. הנתונים מראים מגמה לינארית חזקה.",
        "בנו טבלת סטיות שיטתית: $x_i - \\bar{x}$ ו-$y_i - \\bar{y}$ לכל שורה, סכום מכפלות ל-$S_{xy}$ וריבועי סטיות ל-$S_{xx}$. חשבו ממוצעים קודם — טעות ב-$\\bar{x}$ או $\\bar{y}$ משבשת הכל.",
        "טעויות חשבון במכפלות סטיות (במיוחד סימנים עם סטיות שליליות). שכחה לחסר $\\hat{\\beta}_1 \\bar{x}$ בחישוב חיתוך.",
        "אחרי $\\hat{\\beta}_1$, תמיד סיימו עם $\\hat{\\beta}_0 = \\bar{y} - \\hat{\\beta}_1 \\bar{x}$ — לעולם לא רק שיפוע. בדקו מרכז כובל: $2.6 + 1.4(6) = 11 = \\bar{y}$. כתבו $\\hat{y} = 2.6 + 1.4x$ כתשובה סופית.",
    ),
    fmt_expl(
        "SST $= S_{yy} = (-6)^2+(-2)^2+0+2^2+6^2 = 80$. Residuals from $\\hat{y} = 2.6+1.4x$: $e_1=-0.4$, $e_2=0.8$, $e_3=0$, $e_4=-0.8$, $e_5=0.4$. SSR $= 0.16+0.64+0+0.64+0.16 = 1.6$. $R^2 = 1 - 1.6/80 = 0.98$.",
        "Two-step process: first SST from deviations around $\\bar{y}$, then SSR from squared residuals using the fitted line. $R^2$ close to 1 means the line nearly passes through all points.",
        "Using SST $= \\sum y_i^2$ instead of $\\sum(y_i - \\bar{y})^2$. Computing $R^2 = \\text{SSR}/\\text{SST}$ without the \"1 minus.\" Rounding residuals too early.",
        "When $R^2 > 0.95$, mention in interpretation that the linear model fits very well — exam rubrics reward contextual interpretation, not just the number.",
        "SST $= 80$. SSR $= 1.6$. $R^2 = 1 - 1.6/80 = 0.98$ — 98% מהשונות מוסברת. חשבו קודם SST מסטיות סביב $\\bar{y}$, אחר כך SSR מריבועי שאריות.",
        "תהליך דו-שלבי: קודם SST מסטיות סביב $\\bar{y}$, אחר כך SSR מריבועי שאריות. $R^2$ קרוב ל-1 = הקו כמעט עובר דרך כל הנקודות. אל תשתמשו ב-$\\sum y_i^2$ ל-SST.",
        "שימוש ב-SST $= \\sum y_i^2$ במקום $\\sum(y_i - \\bar{y})^2$. $R^2 = \\text{SSR}/\\text{SST}$ בלי \"1 פחות\". עיגול שאריות מוקדם מדי.",
        "כש-$R^2 > 0.95$, ציינו בפרשנות שהמודל הלינארי מתאים מאוד — מחווני בחינה מעריכים פרשנות, לא רק מספר. 98% מהשונות מוסברת — הקשר כמעט לינארי מושלם.",
    ),
    fmt_expl(
        "$\\hat{\\beta}_1 = S_{xy}/S_{xx}$, so explained sum of squares SSE $= \\hat{\\beta}_1^2 S_{xx} = S_{xy}^2/S_{xx}$. Then $R^2 = \\text{SSE}/\\text{SST} = S_{xy}^2/(S_{xx} S_{yy}) = r^2$, where $r = S_{xy}/\\sqrt{S_{xx} S_{yy}}$. $\\blacksquare$",
        "The proof chains three facts: (1) SSE in terms of $\\hat{\\beta}_1$ and $S_{xx}$, (2) $R^2 = \\text{SSE}/\\text{SST}$, (3) the definition of Pearson $r$. No numerical computation needed.",
        "Proving $R^2 = r$ instead of $R^2 = r^2$. Using $\\text{SSR}$ instead of $\\text{SSE}$ in the numerator of $R^2$.",
        "This proof appears on HUJI and Technion statistics finals. Write the three-line chain clearly — partial credit is generous when the logic is visible.",
        "$\\text{SSE} = \\hat{\\beta}_1^2 S_{xx} = S_{xy}^2/S_{xx}$. $R^2 = \\text{SSE}/\\text{SST} = S_{xy}^2/(S_{xx} S_{yy}) = r^2$. $\\blacksquare$ שלושה שלבים: SSE דרך $\\hat{\\beta}_1$, $R^2 = \\text{SSE}/\\text{SST}$, והגדרת $r$.",
        "הוכחה מקשרת שלוש עובדות: (1) SSE דרך $\\hat{\\beta}_1$ ו-$S_{xx}$, (2) $R^2 = \\text{SSE}/\\text{SST}$, (3) הגדרת $r$. בלי חישוב מספרי — רק אלגברה טהורה.",
        "הוכחת $R^2 = r$ במקום $R^2 = r^2$. שימוש ב-SSR במקום SSE במונה $R^2$.",
        "הוכחה זו מופיעה בבחינות HUJI וטכניון. כתבו את שלושת השלבים בבירור — ניקוד חלקי נדיב כשהלוגיקה גלויה. זכרו: $R^2 = r^2$ ולא $R^2 = r$.",
    ),
    fmt_expl(
        "$s = \\sqrt{\\text{SSR}/(n-2)} = \\sqrt{40/(20-2)} = \\sqrt{40/18} = \\sqrt{2.\\overline{2}} \\approx 1.49$. The $n-2$ degrees of freedom account for the two estimated parameters ($\\beta_0$ and $\\beta_1$).",
        "Residual standard error $s$ estimates $\\sigma$ — the typical size of a vertical deviation from the true line. Always divide SSR by $n-2$, not $n$ or $n-1$.",
        "Using $n$ instead of $n-2$ in the denominator (confusing with sample standard deviation of $y$). Forgetting the square root and reporting SSR/(n-2) directly.",
        "Simple regression always uses $df = n-2$. Multiple regression uses $n-k-1$. Write this on your formula card next to $s = \\sqrt{\\text{SSR}/(n-2)}$.",
        "$s = \\sqrt{40/18} \\approx 1.49$. $n-2$ דרגות חופש בגלל שני פרמטרים מוערכים ($\\beta_0$ ו-$\\beta_1$).",
        "שגיאה סטנדרטית $s$ מאמידה $\\sigma$ — גודל טיפוסי של סטייה אנכית מהקו האמיתי. תמיד חלקו SSR ב-$n-2$, לא $n$ או $n-1$.",
        "שימוש ב-$n$ במקום $n-2$ (בלבול עם סטיית תקן מדגמית של $y$). שכחת שורש ודיווח על SSR/(n-2) ישירות.",
        "רגרסיה פשוטה: תמיד $df = n-2$. רגרסיה מרובה: $n-k-1$. כתבו זאת בגיליון ליד $s = \\sqrt{\\text{SSR}/(n-2)}$.",
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
