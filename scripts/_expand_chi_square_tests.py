#!/usr/bin/env python3
"""Expand chi_square_tests.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/chi_square_tests.json"

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


INTRO = {
    "body_en_md": """Are gender and political preference related? Does the observed distribution of blood types match the expected population frequencies? These questions involve **categorical data** — counts in labeled categories with no natural numerical ordering.

The **chi-square ($\\chi^2$) test** is the standard inferential tool for such data. It compares what we **observed** ($O$) to what we would **expect** ($E$) if the null hypothesis $H_0$ were true. Two variants dominate university statistics:

1. **Test for independence:** A contingency table cross-classifies two categorical variables; we ask whether an association exists.
2. **Goodness-of-fit test:** One categorical variable; we ask whether observed frequencies match a hypothesised distribution (fair die, Mendelian ratio, market share).

Both use the same statistic $\\chi^2 = \\sum (O-E)^2/E$, but degrees of freedom and expected-count formulas differ. This lesson builds on `concept:hypothesis_testing` and connects to regression and ANOVA as part of the inferential toolkit for discrete outcomes.""",
    "body_he_md": """האם מגדר ומועדפות פוליטית קשורים? האם פילוג סוגי הדם התצפיתי תואם את הצפוי באוכלוסייה? שאלות אלה עוסקות ב**נתונים קטגוריים** — ספירות בקטגוריות מתויגות ללא סדר מספרי טבעי.

**מבחן כי-בריבוע ($\\chi^2$)** הוא כלי הסקה סטנדרטי לנתונים כאלה. הוא משווה מה **נצפה** ($O$) לבין מה **היינו מצפים** ($E$) אם $H_0$ נכון. שני וריאנטים שולטים בסטטיסטיקה אוניברסיטאית:

1. **מבחן אי-תלות:** טבלת אקראיות מצלבת שני משתנים קטגוריים; בודקים אם קיים קשר.
2. **מבחן טיב-ההתאמה:** משתנה קטגורי אחד; בודקים אם תדירויות תצפיתיות תואמות פילוג היפותטי (קובייה הוגנת, יחס מנדל, נתח שוק).

שניהם משתמשים ב-$\\chi^2 = \\sum (O-E)^2/E$, אך דרגות החופש ונוסחאות הספירות הצפויות שונות. השיעור נשען על `concept:hypothesis_testing` ומתחבר לרגרסיה ו-ANOVA כחלק מערכת כלי הסקה לתוצאות בדידות.""",
}

DEFINITION = {
    "body_en_md": """**Chi-square statistic (both tests):**
$$\\chi^2 = \\sum \\frac{(O - E)^2}{E}$$
where $O$ = observed count in a cell/category, $E$ = expected count under $H_0$.

**Test for independence (contingency table, $r$ rows, $c$ columns):**
- $H_0$: the two categorical variables are statistically independent.
- $H_1$: the variables are associated (not independent).
- Expected count in cell $(i,j)$: $E_{ij} = \\dfrac{R_i \\times C_j}{N}$, where $R_i$ is row $i$ total, $C_j$ is column $j$ total, $N$ is the grand total.
- Degrees of freedom: $df = (r-1)(c-1)$.
- Intuition: under independence, joint probability equals product of marginals.

**Goodness-of-fit test ($k$ categories):**
- $H_0$: data follow a specific distribution with probabilities $p_1, \\ldots, p_k$.
- Expected count: $E_i = n \\cdot p_i$ where $n$ is total sample size.
- Degrees of freedom: $df = k - 1$ (one parameter fixed by $\\sum p_i = 1$).

**Decision rule:** Reject $H_0$ if $\\chi^2 > \\chi^2_{\\alpha, df}$ (critical value) or equivalently if $p\\text{-value} < \\alpha$.

**Validity condition (rule of thumb):** All expected counts should satisfy $E \\geq 5$. If violated, combine adjacent categories or use Fisher's exact test (2×2 tables).""",
    "body_he_md": """**סטטיסטיקת כי-בריבוע (שני מבחנים):**
$$\\chi^2 = \\sum \\frac{(O - E)^2}{E}$$
כאשר $O$ = ספירה תצפיתית בתא/קטגוריה, $E$ = ספירה צפויה תחת $H_0$.

**מבחן אי-תלות (טבלת אקראיות, $r$ שורות, $c$ עמודות):**
- $H_0$: שני המשתנים הקטגוריים בלתי-תלויים סטטיסטית.
- $H_1$: המשתנים קשורים (לא בלתי-תלויים).
- ספירה צפויה בתא $(i,j)$: $E_{ij} = \\dfrac{R_i \\times C_j}{N}$, כאשר $R_i$ סה\"כ שורה $i$, $C_j$ סה\"כ עמודה $j$, $N$ סה\"כ כולל.
- דרגות חופש: $df = (r-1)(c-1)$.
- אינטואיציה: תחת אי-תלות, ההסתברות המשותפת שווה למכפלת השוליות.

**מבחן טיב-התאמה ($k$ קטגוריות):**
- $H_0$: הנתונים עוקבים אחרי פילוג עם הסתברויות $p_1, \\ldots, p_k$.
- ספירה צפויה: $E_i = n \\cdot p_i$ כאשר $n$ גודל המדגם.
- דרגות חופש: $df = k - 1$ (פרמטר אחד קבוע מ-$\\sum p_i = 1$).

**כלל החלטה:** דחה $H_0$ אם $\\chi^2 > \\chi^2_{\\alpha, df}$ (ערך קריטי) או שקול: $p\\text{-value} < \\alpha$.

**תנאי תקפות (כלל אצבע):** כל הספירות הצפויות חייבות לקיים $E \\geq 5$. אם מופר — אחד קטגוריות סמוכות או השתמש במבחן הדיוק של פישר (טבלאות 2×2).""",
}

THEORY = {
    "body_en_md": """**Sampling distribution under $H_0$.** Each standardized cell contribution $(O-E)^2/E$ is approximately $\\chi^2(1)$ when $E$ is large enough. Summing over all cells yields a statistic that follows $\\chi^2(df)$ under the null — this is the basis for critical values and p-values.

**Large $\\chi^2$ means:** observed counts deviate substantially from expected — evidence against $H_0$. **Small $\\chi^2$ means:** observed matches expected well — no evidence against $H_0$. Note: failing to reject is **not** proof that $H_0$ is true; it means insufficient evidence to reject.

**Independence intuition.** If row and column variables are independent, $P(\\text{row } i \\cap \\text{col } j) = P(\\text{row } i) \\cdot P(\\text{col } j) = (R_i/N)(C_j/N)$. Multiplying by $N$ gives $E_{ij} = R_i C_j / N$ — exactly the expected-count formula.

**Goodness-of-fit link.** When testing a fair die, $p_i = 1/6$ for each face. Deviations from equal expected counts inflate $\\chi^2$. Mendelian genetics (9:3:3:1) uses the same framework with unequal $p_i$.

**Relationship to other tests.** For 2×2 tables with large samples, $\\chi^2$ approximates the two-proportion z-test. For $r=2, c=2$, the compact formula $\\chi^2 = N(ad-bc)^2/(R_1 R_2 C_1 C_2)$ saves computation.

**Effect size.** $\\chi^2$ detects **whether** association exists, not **how strong** it is. Use Cramér's $V = \\sqrt{\\chi^2/(N \\cdot \\min(r-1,c-1))}$ for strength after significance.""",
    "body_he_md": """**התפלגות דגימה תחת $H_0$.** כל תרומת תא מנורמלת $(O-E)^2/E$ מקורבת ל-$\\chi^2(1)$ כאשר $E$ גדול מספיק. סיכום על כל התאים מניב סטטיסטיקה שעוקבת אחרי $\\chi^2(df)$ תחת האפס — בסיס לערכים קריטיים ו-p-values.

**$\\chi^2$ גדול:** ספירות תצפיתיות סוטות משמעותית מהצפוי — עדות נגד $H_0$. **$\\chi^2$ קטן:** התצפיות תואמות הצפוי — אין עדות נגד $H_0$. שימו לב: אי-דחייה **אינה** הוכחה ש-$H_0$ נכון; רק שאין מספיק עדות לדחייה.

**אינטואיציה של אי-תלות.** אם משתני שורה ועמודה בלתי-תלויים, $P(\\text{שורה } i \\cap \\text{עמודה } j) = P(\\text{שורה } i) \\cdot P(\\text{עמודה } j) = (R_i/N)(C_j/N)$. הכפלה ב-$N$ נותנת $E_{ij} = R_i C_j / N$ — בדיוק נוסחת הספירה הצפויה.

**קשר למבחן טיב-התאמה.** בבדיקת קובייה הוגנת, $p_i = 1/6$ לכל פאה. סטיות מספירות צפויות שוות מנפחות $\\chi^2$. גנטיקה מנדלית (9:3:3:1) משתמשת באותה מסגרת עם $p_i$ לא שווים.

**קשר למבחנים אחרים.** לטבלאות 2×2 עם מדגמים גדולים, $\\chi^2$ מקורב למבחן z לשתי פרופורציות. ל-$r=2, c=2$, הנוסחה הקומפקטית $\\chi^2 = N(ad-bc)^2/(R_1 R_2 C_1 C_2)$ חוסכת חישוב.

**עוצמת אפקט.** $\\chi^2$ מגלה **אם** קיים קשר, לא **כמה חזק**. לאחר מובהקות, השתמשו ב-$V$ של קרמר: $\\sqrt{\\chi^2/(N \\cdot \\min(r-1,c-1))}$ למדידת עוצמה.""",
}

WE1 = {
    "body_en_md": """**Is smoking associated with lung disease?** 200 people surveyed:

| | Has Disease | No Disease | Total |
|---|---|---|---|
| Smoker | 50 | 50 | 100 |
| Non-smoker | 20 | 80 | 100 |
| **Total** | 70 | 130 | 200 |

We test $H_0$: smoking status and disease are independent, at $\\alpha = 0.05$.

### Move 1: Compute expected counts
Under independence, $E_{ij} = (\\text{row total} \\times \\text{col total}) / 200$:
$$E_{11} = 100 \\times 70/200 = 35, \\quad E_{12} = 100 \\times 130/200 = 65.$$
$$E_{21} = 35, \\quad E_{22} = 65.$$
All $E \\geq 5$ ✓ — chi-square is valid.

### Move 2: Compute $\\chi^2$
$$\\chi^2 = \\frac{(50-35)^2}{35} + \\frac{(50-65)^2}{65} + \\frac{(20-35)^2}{35} + \\frac{(80-65)^2}{65}$$
$$= \\frac{225}{35} + \\frac{225}{65} + \\frac{225}{35} + \\frac{225}{65} = 6.43 + 3.46 + 6.43 + 3.46 = 19.78.$$

### Move 3: Decision
$df = (2-1)(2-1) = 1$. Critical value $\\chi^2_{0.05,1} = 3.84$. Since $19.78 > 3.84$: **reject $H_0$**. Smoking and lung disease are significantly associated at the 5% level.

**Interpretation:** Smokers appear in the disease column far more often than independence predicts ($O_{11}=50$ vs $E_{11}=35$), while non-smokers appear less often ($O_{21}=20$ vs $E_{21}=35$). The large $\\chi^2$ reflects this pattern across all four cells.""",
    "body_he_md": """**האם עישון קשור למחלת ריאות?** 200 נסקרו:

| | מחלה | ללא מחלה | סה\"כ |
|---|---|---|---|
| מעשן | 50 | 50 | 100 |
| לא מעשן | 20 | 80 | 100 |
| **סה\"כ** | 70 | 130 | 200 |

בודקים $H_0$: סטטוס עישון ומחלה בלתי-תלויים, ב-$\\alpha = 0.05$.

### צעד 1: חישוב ספירות צפויות
תחת אי-תלות, $E_{ij} = (\\text{סה\"כ שורה} \\times \\text{סה\"כ עמודה}) / 200$:
$$E_{11} = 100 \\times 70/200 = 35, \\quad E_{12} = 100 \\times 130/200 = 65.$$
$$E_{21} = 35, \\quad E_{22} = 65.$$
כל $E \\geq 5$ ✓ — המבחן תקף.

### צעד 2: חישוב $\\chi^2$
$$\\chi^2 = \\frac{(50-35)^2}{35} + \\frac{(50-65)^2}{65} + \\frac{(20-35)^2}{35} + \\frac{(80-65)^2}{65}$$
$$= \\frac{225}{35} + \\frac{225}{65} + \\frac{225}{35} + \\frac{225}{65} = 6.43 + 3.46 + 6.43 + 3.46 = 19.78.$$

### צעד 3: החלטה
$df = (2-1)(2-1) = 1$. ערך קריטי $\\chi^2_{0.05,1} = 3.84$. מאחר ש-$19.78 > 3.84$: **דוחים $H_0$**. יש קשר מובהק בין עישון ומחלת ריאות ברמה 5%.

**פרשנות:** מעשנים מופיעים בעמודת המחלה הרבה יותר ממה שאי-תלות הייתה חוזה ($O_{11}=50$ לעומת $E_{11}=35$), ולא-מעשנים פחות ($O_{21}=20$ לעומת $E_{21}=35$). $\\chi^2$ הגדול משקף דפוס זה בכל ארבעת התאים.""",
}

WE2 = {
    "body_en_md": """**Is education level associated with exercise frequency?** 150 people surveyed:

| | Exercises regularly | Does not | Total |
|---|---|---|---|
| High school | 20 | 40 | 60 |
| Bachelor | 30 | 30 | 60 |
| Graduate | 25 | 5 | 30 |
| **Total** | 75 | 75 | 150 |

### Move 1: Expected counts ($E_{ij} = R_i C_j / 150$)

| | Exercises | Does not |
|---|---|---|
| High school | $60\\times75/150=30$ | 30 |
| Bachelor | 30 | 30 |
| Graduate | $30\\times75/150=15$ | 15 |

All expected counts $\\geq 5$ ✓.

### Move 2: Chi-square statistic
$$\\chi^2 = \\frac{(20-30)^2}{30}+\\frac{(40-30)^2}{30}+\\frac{(30-30)^2}{30}+\\frac{(30-30)^2}{30}+\\frac{(25-15)^2}{15}+\\frac{(5-15)^2}{15}$$
$$= 3.33+3.33+0+0+6.67+6.67 = 20.$$

### Move 3: Decision
$df=(3-1)(2-1)=2$. $\\chi^2_{0.05,2}=5.99$. Since $20>5.99$: **reject $H_0$**. Education level and exercise frequency are significantly associated. Note: graduate students exercise more than expected — but $\\chi^2$ alone does not identify which cells drive the association; examine standardized residuals for follow-up.""",
    "body_he_md": """**האם רמת השכלה קשורה לתדירות פעילות גופנית?** 150 נסקרו:

| | מתאמן | לא מתאמן | סה\"כ |
|---|---|---|---|
| תיכון | 20 | 40 | 60 |
| תואר ראשון | 30 | 30 | 60 |
| תואר שני | 25 | 5 | 30 |
| **סה\"כ** | 75 | 75 | 150 |

### צעד 1: ספירות צפויות ($E_{ij} = R_i C_j / 150$)

| | מתאמן | לא מתאמן |
|---|---|---|
| תיכון | $60\\times75/150=30$ | 30 |
| תואר ראשון | 30 | 30 |
| תואר שני | $30\\times75/150=15$ | 15 |

כל הספירות הצפויות $\\geq 5$ ✓.

### צעד 2: סטטיסטיקת כי-בריבוע
$$\\chi^2 = \\frac{(20-30)^2}{30}+\\frac{(40-30)^2}{30}+\\frac{(30-30)^2}{30}+\\frac{(30-30)^2}{30}+\\frac{(25-15)^2}{15}+\\frac{(5-15)^2}{15}$$
$$= 3.33+3.33+0+0+6.67+6.67 = 20.$$

### צעד 3: החלטה
$df=(3-1)(2-1)=2$. $\\chi^2_{0.05,2}=5.99$. מאחר ש-$20>5.99$: **דוחים $H_0$**. רמת השכלה ותדירות פעילות גופנית קשורים מובהקית. שימו לב: בוגרי תואר שני מתאמנים יותר מהצפוי — אך $\\chi^2$ לבדו לא מזהה אילו תאים מניעים את הקשר; בדקו שאריות מתוקננות להמשך.""",
}

WE3 = {
    "body_en_md": """**A die is rolled 120 times.** Observed counts: 1→18, 2→22, 3→25, 4→19, 5→20, 6→16. Test whether the die is fair at $\\alpha=0.05$.

**$H_0$:** The die is fair — each face has probability $1/6$.
**$H_1$:** The die is not fair.

### Move 1: Expected counts
Under $H_0$, $E_i = 120 \\times (1/6) = 20$ for each of the six faces.

### Move 2: Chi-square statistic
$$\\chi^2 = \\sum_{i=1}^{6} \\frac{(O_i - 20)^2}{20} = \\frac{4+4+25+1+0+16}{20} = \\frac{50}{20} = 2.5.$$

### Move 3: Decision
$df = 6 - 1 = 5$. Critical value $\\chi^2_{0.05,5} = 11.07$. Since $2.5 < 11.07$: **fail to reject $H_0$**.

**Conclusion in context:** There is no significant evidence that the die is unfair. The observed counts are consistent with a fair die at the 5% level. This does **not** prove the die is perfectly fair — only that the data do not provide enough evidence to reject fairness.

**Sanity check:** The largest deviation is face 3 with $O=25$ vs $E=20$, contributing $25/20=1.25$ to $\\chi^2$ — modest compared to the critical value 11.07. With $n=120$, we would need much larger deviations to reject fairness.""",
    "body_he_md": """**קובייה נזרקת 120 פעמים.** ספירות תצפיתיות: 1→18, 2→22, 3→25, 4→19, 5→20, 6→16. בדוק אם הקובייה הוגנת ב-$\\alpha=0.05$.

**$H_0$:** הקובייה הוגנת — כל פאה בהסתברות $1/6$.
**$H_1$:** הקובייה אינה הוגנת.

### צעד 1: ספירות צפויות
תחת $H_0$, $E_i = 120 \\times (1/6) = 20$ לכל אחת משש הפאות.

### צעד 2: סטטיסטיקת כי-בריבוע
$$\\chi^2 = \\sum_{i=1}^{6} \\frac{(O_i - 20)^2}{20} = \\frac{4+4+25+1+0+16}{20} = \\frac{50}{20} = 2.5.$$

### צעד 3: החלטה
$df = 6 - 1 = 5$. ערך קריטי $\\chi^2_{0.05,5} = 11.07$. מאחר ש-$2.5 < 11.07$: **לא דוחים $H_0$**.

**מסקנה בהקשר:** אין עדות מובהקת שהקובייה לא הוגנת. הספירות התצפיתיות תואמות קובייה הוגנת ברמה 5%. זה **אינו** מוכיח שהקובייה מושלמת — רק שאין מספיק עדות לדחות הוגנות.

**בדיקת סבירות:** הסטייה הגדולה ביותר בפאה 3 עם $O=25$ לעומת $E=20$, תורמת $25/20=1.25$ ל-$\\chi^2$ — מתונה ביחס לקריטי 11.07. עם $n=120$, היינו צריכים סטיות גדולות הרבה יותר כדי לדחות הוגנות.""",
}

METHOD = {
    "body_en_md": """**Independence test (contingency table) — 6 steps:**
1. State $H_0$ (independent) and $H_1$ (associated).
2. Compute marginal totals; find $E_{ij} = R_i C_j / N$ for every cell.
3. Verify all $E_{ij} \\geq 5$; if not, merge categories or use Fisher's exact test.
4. Compute $\\chi^2 = \\sum (O-E)^2/E$ over all cells.
5. Set $df = (r-1)(c-1)$; find critical value or p-value.
6. Decide and state conclusion **in context** (which variables, which significance level).

**Goodness-of-fit test — 6 steps:**
1. State $H_0$ (specified distribution) and $H_1$ (not that distribution).
2. Compute $E_i = n \\cdot p_i$ for each category.
3. Verify all $E_i \\geq 5$.
4. Compute $\\chi^2 = \\sum (O-E)^2/E$.
5. Set $df = k-1$; compare to critical value.
6. Interpret: reject means poor fit; fail to reject means data consistent with $H_0$.

| Result | Decision | Interpretation |
|---|---|---|
| Large $\\chi^2$ | Reject $H_0$ | Association exists / Fit is poor |
| Small $\\chi^2$ | Fail to reject | No evidence of association / Good fit |""",
    "body_he_md": """**מבחן אי-תלות (טבלת אקראיות) — 6 שלבים:**
1. הצהר $H_0$ (בלתי-תלויים) ו-$H_1$ (קשורים).
2. חשב סה\"כ שוליים; מצא $E_{ij} = R_i C_j / N$ לכל תא.
3. אמת ש-$E_{ij} \\geq 5$ לכולם; אם לא — אחד קטגוריות או השתמש במבחן פישר.
4. חשב $\\chi^2 = \\sum (O-E)^2/E$ על כל התאים.
5. קבע $df = (r-1)(c-1)$; מצא ערך קריטי או p-value.
6. קבל החלטה ונסח מסקנה **בהקשר** (אילו משתנים, איזו רמת מובהקות).

**מבחן טיב-התאמה — 6 שלבים:**
1. הצהר $H_0$ (פילוג מוגדר) ו-$H_1$ (לא הפילוג).
2. חשב $E_i = n \\cdot p_i$ לכל קטגוריה.
3. אמת ש-$E_i \\geq 5$ לכולם.
4. חשב $\\chi^2 = \\sum (O-E)^2/E$.
5. קבע $df = k-1$; השווה לערך קריטי.
6. פרש: דחייה = התאמה גרועה; אי-דחייה = נתונים תואמים $H_0$.

| תוצאה | החלטה | פרשנות |
|---|---|---|
| $\\chi^2$ גדול | דחה $H_0$ | קיים קשר / התאמה גרועה |
| $\\chi^2$ קטן | לא דוחה | אין עדות לקשר / התאמה טובה |""",
}

PITFALL = {
    "body_en_md": """1. **Using observed counts as expected.** Expected counts $E_{ij}$ are computed from **marginal totals** under $H_0$, NOT from averaging observed counts or copying the table. Always apply $E_{ij} = R_i C_j / N$ first.

2. **Small expected counts.** If any $E_{ij} < 5$, the chi-square approximation is unreliable. Combine adjacent categories to raise expected counts, or use Fisher's exact test for 2×2 tables.

3. **Wrong degrees of freedom.** Independence: $df = (r-1)(c-1)$. Goodness-of-fit: $df = k-1$. Do not use $N-1$ or confuse the two formulas — this is the most common exam arithmetic error.

4. **Chi-square does not measure association strength.** A large $\\chi^2$ with a huge sample can detect trivial associations. Report Cramér's $V$ alongside significance for effect size.

5. **Directional conclusions.** Chi-square only detects **whether** an association exists. It does NOT say which groups differ or the direction of the effect. Examine cell residuals or run post-hoc tests for details.""",
    "body_he_md": """1. **שימוש בספירות תצפיתיות כצפויות.** ספירות $E_{ij}$ מחושבות מ**סה\"כ שוליים** תחת $H_0$, לא מממוצע תצפיות או העתקת הטבלה. תמיד יישמו קודם $E_{ij} = R_i C_j / N$.

2. **ספירות צפויות קטנות.** אם $E_{ij} < 5$, קירוב כי-בריבוע לא אמין. אחד קטגוריות סמוכות להעלאת צפוי, או השתמש במבחן הדיוק של פישר לטבלאות 2×2.

3. **דרגות חופש שגויות.** אי-תלות: $df = (r-1)(c-1)$. טיב-התאמה: $df = k-1$. אל תשתמשו ב-$N-1$ ואל תבלבלו בין הנוסחאות — זו שגיאת חישוב נפוצה בבחינות.

4. **$\\chi^2$ לא מודד עוצמת קשר.** $\\chi^2$ גדול עם מדגם ענק יכול לגלות קשרים חלשים. דווחו על $V$ של קרמר לצד מובהקות למדידת עוצמה.

5. **מסקנות כיווניות.** $\\chi^2$ רק מגלה **אם** קיים קשר. הוא לא אומר אילו קבוצות שונות או כיוון האפקט. בדקו שאריות תא או מבחני post-hoc לפרטים.""",
}

WHY = {
    "body_en_md": """Chi-square tests appear everywhere categorical data is analyzed: clinical trials (treatment vs. outcome), market research (brand vs. region), genetics (phenotype ratios), and survey analysis (demographics vs. opinions). SPSS, R, and Excel all implement the same core formulas you learn here.

In university statistics courses, chi-square is the bridge between descriptive frequency tables and formal hypothesis testing. It reuses the same logic as z-tests and t-tests — state $H_0$, compute a test statistic, compare to a critical value — but handles **counts** instead of means.

For data science and research careers, knowing when chi-square applies (and when Fisher's exact or logistic regression is better) prevents invalid conclusions from sparse tables. On exams, chi-square items typically award partial credit for correct expected counts even if the final decision is wrong — so master $E_{ij}$ first.""",
    "body_he_md": """מבחני כי-בריבוע מופיעים בכל מקום שמנתחים נתונים קטגוריים: ניסויים קליניים (טיפול מול תוצאה), מחקר שוק (מותג מול אזור), גנטיקה (יחסי תכונה), וניתוח סקרים (דמוגרפיה מול דעות). SPSS, R ו-Excel מיישמים את אותן נוסחאות ליבה.

בקורסי סטטיסטיקה אוניברסיטאיים, כי-בריבוע הוא הגשר בין טבלאות תדירות תיאוריות לבדיקת השערות פורמלית. הוא משתמש באותה לוגיקה כמו מבחני z ו-t — הצהר $H_0$, חשב סטטיסטיקה, השווה לערך קריטי — אך מטפל ב**ספירות** במקום ממוצעים.

לקריירות במדע נתונים ומחקר, ידיעה מתי כי-בריבוע מתאים (ומתי עדיף פישר או רגרסיה לוגיסטית) מונעת מסקנות לא תקפות מטבלאות דלילות. בבחינות, פריטי כי-בריבוע לעיתים מעניקים נקודות חלקיות על ספירות צפויות נכונות גם אם ההחלטה הסופית שגויה — לכן שלטו קודם ב-$E_{ij}$.""",
}

BEFORE = {
    "body_en_md": """**Formula card:**
- $\\chi^2 = \\sum (O-E)^2/E$
- Independence: $E_{ij} = R_i C_j / N$; $df = (r-1)(c-1)$
- Goodness-of-fit: $E_i = n p_i$; $df = k-1$
- Reject $H_0$ if $\\chi^2 > \\chi^2_{\\alpha, df}$
- Validity: all expected counts $\\geq 5$

**Exam patterns:**
- Compute $\\chi^2$ from a given contingency table (show all cell contributions).
- Find a single expected count $E_{ij}$ from marginals.
- State $df$ for various table sizes.
- Goodness-of-fit with fair die, coin, or Mendelian ratios.
- Interpret conclusion in context — never just "reject" without naming variables.

**Tip:** Verify that row totals and column totals of observed counts match the grand total $N$. Then check that expected counts sum to the same $N$. Mismatched totals catch most arithmetic errors before you compute $\\chi^2$.""",
    "body_he_md": """**גיליון נוסחאות:**
- $\\chi^2 = \\sum (O-E)^2/E$
- אי-תלות: $E_{ij}=R_iC_j/N$; $df=(r-1)(c-1)$
- טיב-התאמה: $E_i=np_i$; $df=k-1$
- דחה $H_0$ אם $\\chi^2>\\chi^2_{\\alpha,df}$
- תקפות: כל הספירות הצפויות $\\geq5$

**דגשי מבחן:**
- חשב $\\chi^2$ מטבלת אקראיות (הראה תרומת כל תא).
- מצא ספירה צפויה בודדת $E_{ij}$ משוליים.
- ציין $df$ לגדלי טבלאות שונים.
- טיב-התאמה: קובייה, מטבע, יחסי מנדל.
- פרש מסקנה בהקשר — לעולם לא רק "דוחים" בלי לציין משתנים.

**טיפ:** וודאו שסה\"כ שורות ועמודות של תצפיות תואמים ל-$N$. בדקו שספירות צפויות מסתכמות לאותו $N$. אי-התאמה תופסת רוב שגיאות החישוב לפני $\\chi^2$.""",
}

SUMMARY = {
    "body_en_md": """- **Chi-square statistic:** $\\chi^2 = \\sum (O-E)^2/E$; large values provide evidence against $H_0$.
- **Independence test:** $E_{ij} = R_i C_j/N$; $df=(r-1)(c-1)$; tests association between two categorical variables in a contingency table.
- **Goodness-of-fit test:** $E_i = np_i$; $df=k-1$; tests whether observed frequencies match a specified distribution.
- **Validity condition:** all expected counts must satisfy $E \\geq 5$; otherwise combine categories or use exact methods.
- **Decision:** reject $H_0$ if $\\chi^2 > \\chi^2_{\\alpha, df}$; always state the conclusion in the context of the research question.""",
    "body_he_md": """- **$\\chi^2 = \\sum (O-E)^2/E$:** ערכים גדולים מספקים עדות נגד $H_0$.
- **מבחן אי-תלות:** $E_{ij}=R_iC_j/N$; $df=(r-1)(c-1)$; בודק קשר בין שני משתנים קטגוריים בטבלת אקראיות.
- **מבחן טיב-התאמה:** $E_i=np_i$; $df=k-1$; בודק אם תדירויות תצפיתיות תואמות פילוג מוגדר.
- **תנאי תקפות:** כל הספירות הצפויות חייבות לקיים $E \\geq 5$; אחרת — איחוד קטגוריות או שיטות מדויקות.
- **החלטה:** דחה $H_0$ אם $\\chi^2>\\chi^2_{\\alpha,df}$; תמיד נסח מסקנה בהקשר שאלת המחקר.""",
}

EXPLS = [
    fmt_expl(
        "The expected count in cell (1,1) under independence is row 1 total (40) times column 1 total (50), divided by grand total (100): $E_{11} = 40 \\times 50 / 100 = 20$. This encodes that if variables are unrelated, the joint count reflects the product of marginal proportions.",
        "First identify which cell is requested — here $(1,1)$ means row 1, column 1. Write the row total, column total, and $N$ before substituting. The expected count is always between 0 and $N$, and all expected counts in a table must sum to $N$.",
        "Students sometimes average the four observed cells or use $O_{11}$ itself as $E_{11}$. Another error: using column total only (50) without the row factor.",
        "Memorize $E_{ij} = R_i C_j / N$ — expected-count items are quick exam points. Write the formula, then substitute numbers.",
        "הספירה הצפויה בתא (1,1) תחת אי-תלות היא מכפלת סה\"כ שורה 1 (40) וסה\"כ עמודה 1 (50), חלקי הסה\"כ הכללי (100): $E_{11} = 40 \\times 50 / 100 = 20$. הנוסחה מקודדת שאם המשתנים לא קשורים, הספירה המשותפת משקפת מכפלת פרופורציות שוליות.",
        "זהו קודם איזה תא נדרש — כאן $(1,1)$ שורה 1, עמודה 1. רשמו סה\"כ שורה, עמודה ו-$N$ לפני הצבה. הספירה הצפויה תמיד בין 0 ל-$N$, וכל הצפויות בטבלה מסתכמות ל-$N$.",
        "תלמידים לעיתים ממוצעים את ארבע התצפיות או משתמשים ב-$O_{11}$ כצפוי. טעות נוספת: שימוש רק בסה\"כ עמודה (50) בלי גורם השורה.",
        "בבחינות, שאלות ספירה צפויה הן נקודות מהירות אם שיננתם $E_{ij} = R_i C_j / N$. כתבו קודם את הנוסחה, אחר כך הציבו — נקודות חלקיות נפוצות גם עם טעות חישוב.",
    ),
    fmt_expl(
        "For a goodness-of-fit test with $k$ categories, one degree of freedom is lost because the category probabilities must sum to 1. With $k=4$ categories, $df = k - 1 = 4 - 1 = 3$. Each category contributes one term to the $\\chi^2$ sum, but the constraint $\\sum p_i = 1$ removes one independent parameter.",
        "Ask: how many categories, and is this independence or goodness-of-fit? For goodness-of-fit, $df = k-1$ always. For independence, use $(r-1)(c-1)$ instead — do not mix the formulas.",
        "Using $df = k = 4$ or $df = N-1$ are common errors. Another slip: applying the contingency-table formula $(r-1)(c-1)$ to a single-row frequency table.",
        "Memorize the pair: independence $\\Rightarrow$ $(r-1)(c-1)$; goodness-of-fit $\\Rightarrow$ $k-1$. Exam tables often give $k$ explicitly — one subtraction is all you need.",
        "במבחן טיב-התאמה עם $k$ קטגוריות, דרגת חופש אחת אובדת כי הסתברויות הקטגוריות חייבות להסתכם ל-1. עם $k=4$, $df = k - 1 = 4 - 1 = 3$. כל קטגוריה תורמת מונח ל-$\\chi^2$, אך האילוץ $\\sum p_i = 1$ מסיר פרמטר בלתי-תלוי אחד.",
        "שאלו: כמה קטגוריות, וזה אי-תלות או טיב-התאמה? לטיב-התאמה, $df = k-1$ תמיד. לאי-תלות, $(r-1)(c-1)$ — אל תערבבו נוסחאות.",
        "שימוש ב-$df = k = 4$ או $df = N-1$ שגיאות נפוצות. טעות נוספת: יישום נוסחת טבלת אקראיות על טבלת תדירויות בשורה אחת.",
        "שיננו את הזוג: אי-תלות $\\Rightarrow$ $(r-1)(c-1)$; טיב-התאמה $\\Rightarrow$ $k-1$. בבחינות $k$ ניתן במפורש — חיסור אחד מספיק.",
    ),
    fmt_expl(
        "Under $H_0$ (fair coin), each side is expected 50 times: $E = 100 \\times 0.5 = 50$. The chi-square statistic is $\\chi^2 = (55-50)^2/50 + (45-50)^2/50 = 25/50 + 25/50 = 0.5 + 0.5 = 1$. With $df=1$, this is well below the critical value 3.84 — we would fail to reject fairness.",
        "Goodness-of-fit with two categories is a 2×1 table (or binomial test). Compute $E = np$ for each category, then sum $(O-E)^2/E$. For a fair coin, deviations of 5 from 50 in each direction are modest relative to $E=50$.",
        "Forgetting to square the difference $(O-E)$ or dividing by $O$ instead of $E$. Some students compute only one term instead of summing both categories.",
        "Coin-flip goodness-of-fit is the simplest $\\chi^2$ item — if you get $\\chi^2=1$, sanity-check: deviations of 5 on $E=50$ should give a small statistic. This pattern appears on almost every intro statistics exam.",
        "תחת $H_0$ (מטבע הוגן), כל צד צפוי 50 פעמים: $E = 100 \\times 0.5 = 50$. $\\chi^2 = (55-50)^2/50 + (45-50)^2/50 = 25/50 + 25/50 = 0.5 + 0.5 = 1$. עם $df=1$, זה הרבה מתחת ל-3.84 — לא נדחה הוגנות.",
        "טיב-התאמה עם שתי קטגוריות הוא טבלה 2×1 (או מבחן בינומי). חשבו $E = np$ לכל קטגוריה, וסכמו $(O-E)^2/E$. למטבע הוגן, סטיות של 5 מ-50 בכל כיוון מתונות ביחס ל-$E=50$.",
        "שכחת ריבוע $(O-E)$ או חלוקה ב-$O$ במקום $E$. חלק מסכמים מונח אחד בלבד במקום שני הקטגוריות.",
        "טיב-התאמה למטבע הוא פריט $\\chi^2$ הפשוט ביותר — אם קיבלתם $\\chi^2=1$, בדקו: סטיות של 5 על $E=50$ אמורות לתת סטטיסטיקה קטנה. דפוס זה מופיע בכמעט כל בחינת סטטיסטיקה.",
    ),
    fmt_expl(
        "For a contingency table with $r$ rows and $c$ columns, $df = (r-1)(c-1)$. Here $r=4$, $c=3$, so $df = (4-1)(3-1) = 3 \\times 2 = 6$. Each row and column constraint removes one degree of freedom; the product counts independent cells beyond those constraints.",
        "Count rows and columns from the table dimensions, not from the number of cells ($rc$). Subtract 1 from each dimension and multiply. A 2×2 table always has $df=1$; a 3×3 has $df=4$.",
        "Using $df = rc - 1 = 11$ (total cells minus one) or $df = r + c - 2$ are frequent mistakes. Another error: $df = N - 1$ where $N$ is sample size.",
        "Before computing $\\chi^2$, write $df$ on your scratch paper — exam rubrics often require it separately. Quick check: for a 2×2 table, $df$ must be 1; if you get anything else, recheck the formula.",
        "לטבלת אקראיות עם $r$ שורות ו-$c$ עמודות, $df = (r-1)(c-1)$. כאן $r=4$, $c=3$, לכן $df = (4-1)(3-1) = 3 \\times 2 = 6$. כל אילוץ שורה ועמודה מסיר דרגת חופש; המכפלה סופרת תאים בלתי-תלויים מעבר לאילוצים.",
        "ספרו שורות ועמודות מממדי הטבלה, לא ממספר התאים ($rc$). חסרו 1 מכל ממד והכפילו. טבלה 2×2 תמיד $df=1$; 3×3 יש $df=4$.",
        "שימוש ב-$df = rc - 1 = 11$ או $df = r + c - 2$ טעויות תכופות. שגיאה נוספת: $df = N - 1$ כאשר $N$ גודל מדגם.",
        "לפני חישוב $\\chi^2$, רשמו $df$ — בחינות לעיתים דורשות זאת בנפרד. בדיקה: לטבלה 2×2, $df$ חייב 1; אחרת — בדקו נוסחה.",
    ),
    fmt_expl(
        "Row totals are 50 and 50; column totals are 40 and 60. Expected counts: $E_{11}=20$, $E_{12}=30$, $E_{21}=20$, $E_{22}=30$. Each squared deviation is 100, giving $\\chi^2 = 100/20 + 100/30 + 100/20 + 100/30 = 5 + 3.33 + 5 + 3.33 = 16.67$. With $df=1$ and critical value 3.84, we reject $H_0$ — gender and preference are associated.",
        "Work in order: marginals → expected table → cell contributions → sum. For 2×2 tables, all four $(O-E)^2/E$ terms often share the same numerator when observed counts are symmetrically off from expected.",
        "Computing expected counts from observed averages instead of marginals. Some students stop at $\\chi^2=16.67$ without comparing to 3.84 or stating reject/fail to reject.",
        "2×2 independence problems are the most common exam format. After finding $\\chi^2$, always write the decision sentence: \"Reject $H_0$ at $\\alpha=0.05$; variables are associated.\" Partial credit requires both statistic and conclusion.",
        "סה\"כ שורות 50 ו-50; עמודות 40 ו-60. צפויות: $E_{11}=20$, $E_{12}=30$, $E_{21}=20$, $E_{22}=30$. כל סטייה בריבוע 100, $\\chi^2 = 100/20 + 100/30 + 100/20 + 100/30 = 5 + 3.33 + 5 + 3.33 = 16.67$. עם $df=1$ וקריטי 3.84, דוחים $H_0$ — מגדר והעדפה קשורים.",
        "עבדו בסדר: שוליים → טבלת צפוי → תרומות תא → סיכום. ב-2×2, לעיתים ארבעת $(O-E)^2/E$ חולקים מונה זהה כשסטיות סימטריות.",
        "חישוב צפוי מממוצע תצפיות במקום שוליים. חלק עוצרים ב-$\\chi^2=16.67$ בלי השוואה ל-3.84 או ניסוח דחייה/אי-דחייה.",
        "בעיות אי-תלות 2×2 הן הפורמט הנפוץ ביותר. אחרי $\\chi^2$, כתבו משפט החלטה: \"דוחים $H_0$ ב-$\\alpha=0.05$; המשתנים קשורים.\" נקודות חלקיות דורשות סטטיסטיקה ומסקנה.",
    ),
    fmt_expl(
        "With equal 25% proportions, $E_i = 80 \\times 0.25 = 20$ for each color. Deviations: red +4, blue −2, green 0, yellow −2. Then $\\chi^2 = (4^2 + 2^2 + 0^2 + 2^2)/20 = (16+4+0+4)/20 = 24/20 = 1.2$. Since $1.2 < 7.81 = \\chi^2_{0.05,3}$, we fail to reject $H_0$ — the candy counts are consistent with equal proportions.",
        "Goodness-of-fit: multiply total $n$ by each hypothesised $p_i$ to get all $E_i$ first. Then compute each $(O-E)^2/E$ and sum. With $k=4$ categories, $df=3$ — the exam gives the critical value 7.81.",
        "Using observed proportions as expected counts, or forgetting that $E=20$ for all four colors because proportions are equal. Some students reject because counts \"look uneven\" without computing $\\chi^2$.",
        "When all $p_i$ are equal, every $E_i = n/k$ — a huge time saver. If $\\chi^2$ is near 1 and critical is 7.81, the decision is clearly fail to reject; always show the comparison inequality.",
        "עם פרופורציות 25% שוות, $E_i = 80 \\times 0.25 = 20$ לכל צבע. סטיות: אדום +4, כחול −2, ירוק 0, צהוב −2. $\\chi^2 = (4^2 + 2^2 + 0^2 + 2^2)/20 = (16+4+0+4)/20 = 24/20 = 1.2$. מאחר ש-$1.2 < 7.81 = \\chi^2_{0.05,3}$, לא דוחים $H_0$ — הספירות תואמות פרופורציות שוות.",
        "טיב-התאמה: הכפילו $n$ בכל $p_i$ לכל $E_i$. חשבו $(O-E)^2/E$ וסכמו. עם $k=4$, $df=3$ — הבחינה נותנת קריטי 7.81.",
        "שימוש בפרופורציות תצפיתיות כצפוי, או שכחה ש-$E=20$ לכל הצבעים כי הפרופורציות שוות. חלק דוחים כי הספירות \"נראות לא שוות\" בלי $\\chi^2$.",
        "כשכל $p_i$ שווים, כל $E_i = n/k$ — חוסך זמן. אם $\\chi^2$ קרוב ל-1 וקריטי 7.81, ההחלטה בבירור אי-דחייה; הראו את אי-השוויון.",
    ),
    fmt_expl(
        "The chi-square test relies on a large-sample approximation: each $(O-E)^2/E$ is approximately $\\chi^2(1)$ only when $E$ is sufficiently large. The standard rule of thumb requires **all expected counts $\\geq 5$**. When any $E < 5$, the sampling distribution of $\\chi^2$ is poorly approximated — combine categories or use Fisher's exact test.",
        "Before any chi-square computation, check expected counts — not observed counts. Observed counts can be small as long as expected counts are large enough. For 2×2 tables with small $E$, Fisher's exact test is the standard alternative.",
        "Checking whether observed counts exceed 5 instead of expected counts. Another mistake: proceeding with the test when one cell has $E=3$ because \"the sample is large overall.\"",
        "Validity questions want the expected-count rule: all $E \\geq 5$. Mention Fisher's exact test for small 2×2 tables.",
        "מבחן כי-בריבוע נשען על קירוב מדגם גדול: כל $(O-E)^2/E$ מקורב ל-$\\chi^2(1)$ רק כש-$E$ גדול מספיק. כלל האצבע: **כל הספירות הצפויות $\\geq 5$**. כש-$E < 5$, התפלגות $\\chi^2$ מקורבת גרוע — אחד קטגוריות או השתמש במבחן פישר.",
        "לפני כל חישוב, בדקו ספירות **צפויות** — לא תצפיתיות. תצפיות יכולות להיות קטנות כל עוד הצפוי גדול מספיק. ל-2×2 עם $E$ קטן, פישר הוא החלופה הסטנדרטית.",
        "בדיקה אם **תצפיות** עוברות 5 במקום צפויות. טעות: המשך מבחן כשתא אחד $E=3$ כי \"המדגם גדול בסך הכל.\"",
        "שאלות \"מתי המבחן לא תקף?\" מחפשות כלל הצפוי, לא גודל מדגם בלבד. כתבו: \"כל $E_{ij} \\geq 5$\" וציינו פישר ל-2×2 — זה נקודות מלאות.",
    ),
    fmt_expl(
        "The test statistic $\\chi^2 = 8.5$ exceeds the critical value $\\chi^2_{0.05,2} = 5.99$, so we **reject $H_0$** at the 5% significance level. The two categorical variables in the 3×2 table are significantly associated — the observed counts deviate from what independence would predict beyond random sampling variation.",
        "Decision rule: compare computed $\\chi^2$ to the critical value at the given $\\alpha$ and $df$. Here $df=2$ comes from $(3-1)(2-1)$ for a 3×2 table. Reject when $\\chi^2 >$ critical; fail to reject otherwise.",
        "Confusing \"reject $H_0$\" with \"variables are independent\" — rejection means association, not independence. Some students compare to the wrong $df$ row in the chi-square table.",
        "Interpretation items give $\\chi^2$ and the critical value — no computation. Template: \"Since 8.5 > 5.99, reject $H_0$; variables are associated at $\\alpha=0.05$.\"",
        "$\\chi^2 = 8.5$ גדול מהקריטי $\\chi^2_{0.05,2} = 5.99$, לכן **דוחים $H_0$** ברמת 5%. שני המשתנים בטבלה 3×2 קשורים מובהקית — הספירות סוטות ממה שאי-תלות הייתה חוזה מעבר לרעש דגימה.",
        "כלל החלטה: השוו $\\chi^2$ מחושב לקריטי ב-$\\alpha$ ו-$df$ נתונים. כאן $df=2$ מ-$(3-1)(2-1)$ ל-3×2. דחו כש-$\\chi^2 >$ קריטי; אחרת — לא.",
        "בלבול \"דוחים $H_0$\" עם \"בלתי-תלויים\" — דחייה = קשר, לא אי-תלות. חלק משווים לשורה שגויה בטבלת $\\chi^2$.",
        "שאלות פרשנות נותנות $\\chi^2$ וקריטי — ללא חישוב. כתבו משפט מלא: \"מאחר ש-8.5 > 5.99, דוחים $H_0$; המשתנים קשורים מובהקית ב-$\\alpha=0.05$.\" התבנית מספקת רוב הרubric.",
    ),
]


def load_exercises():
    with open(TARGET, encoding="utf-8") as f:
        old = json.load(f)
    for sec in old["sections"]:
        if sec.get("kind") == "exercise_set":
            return sec
    raise SystemExit("exercise_set not found")


def build_questions():
    stems = [
        (
            "A 2×2 table has row totals 40 and 60, column totals 50 and 50, grand total 100. Find $E_{11}$.",
            'טבלה 2×2 עם סה"כ שורות 40 ו-60, עמודות 50 ו-50, כולל 100. מצא $E_{11}$.',
            ["**Solution:**\n\n$E_{11} = 40 \\times 50 / 100 = 20$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "20$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "20"],
        ),
        (
            "For a goodness-of-fit test with $k=4$ categories, what is $df$?",
            "במבחן טיב-התאמה עם $k=4$ קטגוריות, מהו $df$?",
            ["**Solution:**\n\n$df = 4-1 = 3$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "3$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "3"],
        ),
        (
            "A coin is flipped 100 times: 55 heads, 45 tails. $H_0$: fair coin. Compute $\\chi^2$.",
            "מטבע נזרק 100 פעמים: 55 עץ, 45 פלי. $H_0$: מטבע הוגן. חשב $\\chi^2$.",
            ["**Solution:**\n\n$E = 50$ each. $\\chi^2 = (55-50)^2/50 + (45-50)^2/50 = 0.5+0.5 = 1$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "1$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "1"],
        ),
        (
            "For a 4×3 contingency table, what are the degrees of freedom?",
            "לטבלת אקראיות 4×3, כמה דרגות חופש?",
            ["**Solution:**\n\n$df = (4-1)(3-1) = 6$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "6$.\n\n**Check:** Re-substitute or verify units and signs before moving on", "6"],
        ),
        (
            "A 2×2 contingency table (gender vs. preference): $O_{11}=30$, $O_{12}=20$, $O_{21}=10$, $O_{22}=40$. Grand total = 100. Compute $\\chi^2$ and test at $\\alpha=0.05$.",
            "טבלה 2×2 (מגדר מול העדפה): $O_{11}=30$, $O_{12}=20$, $O_{21}=10$, $O_{22}=40$. כולל = 100. חשב $\\chi^2$ ובדוק ב-$\\alpha=0.05$.",
            ["Row totals: 50, 50. Col totals: 40, 60. $E_{11}=20$, $E_{12}=30$, $E_{21}=20$, $E_{22}=30$. $\\chi^2 = 100/20+100/30+100/20+100/30 = 5+3.33+5+3.33=16.67$. $df=1$, $\\chi^2_{0.05,1}=3.84$. Reject $H_0$", "3.84$. Reject $H_0$", "0"],
        ),
        (
            "A bag claims 25% red, 25% blue, 25% green, 25% yellow candies. In 80 candies: 24 red, 18 blue, 20 green, 18 yellow. Test goodness of fit at $\\alpha=0.05$ ($\\chi^2_{0.05,3}=7.81$).",
            "שקית ממתקים טוענת 25% מכל צבע. ב-80 ממתקים: 24 אדום, 18 כחול, 20 ירוק, 18 צהוב. בדוק טיב-התאמה ב-$\\alpha=0.05$.",
            ["$E_i = 20$ each. $\\chi^2 = (4^2+2^2+0^2+2^2)/20 = (16+4+0+4)/20 = 24/20 = 1.2$. $df=3$. $1.2 < 7.81$: fail to reject $H_0$. Good fit", "3$. $1.2 < 7.81$: fail to reject $H_0$. Good fit", "0"],
        ),
        (
            "When is the chi-square test NOT valid? State the rule of thumb.",
            "מתי מבחן כי-בריבוע **לא** תקף? ציין את כלל האצבע.",
            ["The chi-square test is unreliable when expected counts are less than 5. Rule of thumb: **all $E_{ij} \\geq 5$**. If violated, combine categories or use Fisher's exact test", "5"],
        ),
        (
            "In a 3×2 table, $\\chi^2 = 8.5$. The critical value $\\chi^2_{0.05,2} = 5.99$. What is the conclusion?",
            "בטבלה 3×2, $\\chi^2=8.5$. ערך קריטי $\\chi^2_{0.05,2}=5.99$. מה המסקנה?",
            ["$8.5 > 5.99$: **reject $H_0$**. The two categorical variables are significantly associated at the 5% level", "5"],
        ),
    ]
    diffs = ["easy", "easy", "easy", "easy", "medium", "medium", "medium", "medium"]
    qs = []
    for i, ((se, sh, ans), diff, (ex_en, ex_he)) in enumerate(zip(stems, diffs, EXPLS), 1):
        qs.append({
            "ord": i,
            "kind": "short_answer",
            "difficulty": diff,
            "stem_en": se,
            "stem_he": sh,
            "answer_payload": {"acceptable_answers": ans, "case_sensitive": False},
            "explanation_en": ex_en,
            "explanation_he": ex_he,
            "skill_atoms": [],
        })
    return qs


def main():
    lesson = {
        "concept_id": "chi_square_tests",
        "subject": "math",
        "level": "university",
        "math_track": ["statistics"],
        "title_en": "Chi-Square Tests",
        "title_he": "מבחני כי-בריבוע",
        "summary_en": "Chi-square test for independence (contingency tables) and goodness-of-fit test. Computing the test statistic, degrees of freedom, and interpreting results.",
        "summary_he": "מבחן כי-בריבוע לאי-תלות (טבלאות אקראיות) ומבחן טיב-ההתאמה. חישוב סטטיסטיקת המבחן, דרגות החופש ופרשנות התוצאות.",
        "sections": [
            {
                "kind": "intro",
                "title_en": "Categorical Data and the Chi-Square Test",
                "title_he": "נתונים קטגוריים ומבחן כי-בריבוע",
                **INTRO,
            },
            {
                "kind": "definition",
                "title_en": "Chi-Square Formulas",
                "title_he": "נוסחאות כי-בריבוע",
                **DEFINITION,
            },
            {
                "kind": "theory",
                "title_en": "Why Does $\\chi^2$ Work?",
                "title_he": "מדוע $\\chi^2$ עובד?",
                **THEORY,
            },
            {
                "kind": "worked_example",
                "difficulty": "easy",
                "example_number": 1,
                "title_en": "Worked Example 1 — 2×2 Contingency Table",
                "title_he": "דוגמה פתורה 1 — טבלת אקראיות 2×2",
                **WE1,
            },
            {
                "kind": "checkpoint",
                "title_en": "Stop & Practice",
                "title_he": "עצור ותרגל",
                "body_en_md": "A 2×2 table has: $O_{11}=20$, $O_{12}=30$, $O_{21}=10$, $O_{22}=40$. Grand total = 100. Compute $E_{11}$.",
                "body_he_md": 'טבלה 2×2: $O_{11}=20$, $O_{12}=30$, $O_{21}=10$, $O_{22}=40$. סה"כ = 100. חשב $E_{11}$.',
                "checkpoint_solution_en": "First find marginal totals: row 1 total = $20+30=50$, column 1 total = $20+10=30$, grand total $N=100$. Under independence, $E_{11} = R_1 C_1 / N = 50 \\times 30 / 100 = 15$. Check: all four expected counts should sum to 100.",
                "checkpoint_solution_he": 'קודם מצאו סה"כ שוליים: שורה 1 = $20+30=50$, עמודה 1 = $20+10=30$, סה"כ $N=100$. תחת אי-תלות, $E_{11} = R_1 C_1 / N = 50 \\times 30 / 100 = 15$. בדיקה: כל ארבע הצפויות צריכות להסתכם ל-100.',
            },
            {
                "kind": "worked_example",
                "difficulty": "medium",
                "example_number": 2,
                "title_en": "Worked Example 2 — 3×2 Contingency Table",
                "title_he": "דוגמה פתורה 2 — טבלת אקראיות 3×2",
                **WE2,
            },
            {
                "kind": "checkpoint",
                "title_en": "Stop & Practice",
                "title_he": "עצור ותרגל",
                "body_en_md": "A 3×3 contingency table has $df = ?$ and a 4×2 table has $df = ?$",
                "body_he_md": "לטבלה 3×3 יש $df = ?$ ולטבלה 4×2 יש $df = ?$",
                "checkpoint_solution_en": "For independence tests, $df=(r-1)(c-1)$. A 3×3 table: $df=(3-1)(3-1)=2\\times2=4$. A 4×2 table: $df=(4-1)(2-1)=3\\times1=3$. Remember: subtract 1 from each dimension, then multiply — do not use total cell count.",
                "checkpoint_solution_he": "במבחני אי-תלות, $df=(r-1)(c-1)$. טבלה 3×3: $df=(3-1)(3-1)=2\\times2=4$. טבלה 4×2: $df=(4-1)(2-1)=3\\times1=3$. זכרו: חסרו 1 מכל ממד והכפילו — לא מספר התאים.",
            },
            {
                "kind": "worked_example",
                "difficulty": "hard",
                "example_number": 3,
                "title_en": "Worked Example 3 — Goodness-of-Fit Test",
                "title_he": "דוגמה פתורה 3 — מבחן טיב-התאמה",
                **WE3,
            },
            {
                "kind": "method_guide",
                "title_en": "Method Guide — Chi-Square Tests",
                "title_he": "מדריך שיטה — מבחני כי-בריבוע",
                **METHOD,
            },
            load_exercises(),
            {
                "kind": "pitfall",
                "title_en": "Common Pitfalls",
                "title_he": "מלכודות נפוצות",
                **PITFALL,
            },
            {
                "id": "why_matters",
                "kind": "why_matters",
                "title_en": "Why it matters",
                "title_he": "למה זה חשוב",
                **WHY,
            },
            {
                "kind": "before_exam",
                "title_en": "Before the Exam",
                "title_he": "לפני הבחינה",
                **BEFORE,
            },
            {
                "kind": "summary",
                "title_en": "Summary",
                "title_he": "סיכום",
                **SUMMARY,
            },
        ],
        "agent_hints": {},
        "questions": build_questions(),
        "est_minutes": 45,
        "author": "cursor-claude-2026",
        "version": 1,
        "level_focus": None,
        "skill_atom_bank": None,
    }

    # Validate word counts
    errors = []
    for sec in lesson["sections"]:
        k = sec.get("kind")
        if k in MIN:
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            en_min, he_min = MIN[k]
            if en_w < en_min:
                errors.append(f"{k} EN: {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{k} HE: {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{k} HE weak parity")
        if k == "worked_example":
            en_w = wc(sec.get("body_en_md", ""))
            he_w = wc(sec.get("body_he_md", ""))
            en_min, he_min = MIN["worked_example"]
            if en_w < en_min:
                errors.append(f"we{sec.get('example_number')} EN: {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"we{sec.get('example_number')} HE: {he_w} < {he_min}")

    for q in lesson["questions"]:
        for lang in ("en", "he"):
            w = wc(q[f"explanation_{lang}"])
            if w < 80 or w > 150:
                errors.append(f"Q{q['ord']} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")

    json.loads(TARGET.read_text(encoding="utf-8"))
    print(f"Wrote {TARGET}")

    r = subprocess.run(
        ["node", str(ROOT / "scripts/seed-lessons.mjs"), "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    if r.returncode != 0:
        sys.exit(r.returncode)
    if "207/207" not in r.stdout and "207/207" not in r.stderr:
        print("WARNING: expected 207/207 in dry-run output", file=sys.stderr)


if __name__ == "__main__":
    main()
