#!/usr/bin/env python3
"""Expand anova_one_way.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/anova_one_way.json"

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
    "body_en_md": """A researcher wants to compare the effectiveness of three teaching methods on exam scores. Can she simply run three separate two-sample t-tests? **No** — running many pairwise t-tests inflates the **family-wise Type I error rate** (false positives). With three groups there are three comparisons; each at $\\alpha=0.05$ gives an overall error near 14%, not 5%.

Instead, she uses **One-Way ANOVA (Analysis of Variance)**, which tests whether all $k$ group means are equal in a **single** omnibus test. ANOVA partitions total variability into **between-group** variation (explained by the grouping factor) and **within-group** variation (random noise around each group mean). The F-statistic compares these two sources.

This lesson builds on `concept:hypothesis_testing` and complements `concept:chi_square_tests`: ANOVA handles **continuous outcomes** across $k \\geq 2$ groups, while chi-square handles categorical counts. After a significant ANOVA, post-hoc tests identify which specific pairs differ.""",
    "body_he_md": """חוקרת רוצה להשוות יעילות שלוש שיטות הוראה על ציוני מבחן. האם היא יכולה להריץ שלושה מבחני t לזוגות נפרדים? **לא** — מבחני t מרובים מנפחים את **שגיאת סוג I המשפחתית** (חיוביים שגויים). לשלוש קבוצות יש שלוש השוואות; כל אחת ב-$\\alpha=0.05$ נותנת שגיאה כוללת של כ-14%, לא 5%.

במקום זאת, היא משתמשת ב-**ANOVA חד-כיווני (ניתוח שונות)**, שבודק אם כל $k$ ממוצעי הקבוצות שווים ב**מבחן אחד** אומניבוס. ANOVA מפרק את השונות הכוללת ל**שונות בין-קבוצתית** (מוסברת על ידי גורם הקיבוץ) ו**שונות תוך-קבוצתית** (רעש אקראי סביב ממוצע כל קבוצה). סטטיסטיקת F משווה בין שני מקורות אלה.

השיעור נשען על `concept:hypothesis_testing` ומשלים את `concept:chi_square_tests`: ANOVA מטפל ב**תוצאות רציפות** על פני $k \\geq 2$ קבוצות, בעוד כי-בריבוע מטפל בספירות קטגוריות. לאחר ANOVA מובהק, מבחני post-hoc מזהים אילו זוגות ספציפיים שונים.""",
}

DEFINITION = {
    "body_en_md": """**Setting:** $k$ groups, group $i$ has $n_i$ observations, total $N = \\sum_{i=1}^k n_i$. Grand mean: $\\bar{x}_{..} = \\dfrac{\\sum_{i,j} x_{ij}}{N}$. Group mean: $\\bar{x}_i = \\dfrac{1}{n_i}\\sum_j x_{ij}$.

**SS Between (SSB):** Variation explained by group membership.
$$\\text{SSB} = \\sum_{i=1}^k n_i(\\bar{x}_i - \\bar{x}_{..})^2$$

**SS Within (SSW):** Residual variation within groups (error).
$$\\text{SSW} = \\sum_{i=1}^k \\sum_{j=1}^{n_i} (x_{ij} - \\bar{x}_i)^2$$

**Total SS:** $\\text{SST} = \\text{SSB} + \\text{SSW} = \\sum_{i,j}(x_{ij}-\\bar{x}_{..})^2$.

**Degrees of freedom:** $df_B = k-1$, $df_W = N-k$, $df_T = N-1$.

**Mean squares:** $\\text{MSB} = \\text{SSB}/(k-1)$, $\\text{MSW} = \\text{SSW}/(N-k)$.

**F-statistic:** $F = \\text{MSB}/\\text{MSW}$.

**Hypotheses:** $H_0: \\mu_1 = \\mu_2 = \\cdots = \\mu_k$ vs. $H_1$: at least two means differ.

**Decision:** Reject $H_0$ if $F > F_{\\alpha,\\,k-1,\\,N-k}$ or if $p\\text{-value} < \\alpha$.

**Effect size:** $\\eta^2 = \\text{SSB}/\\text{SST}$ — proportion of total variance explained by groups.

**ANOVA table layout:** Each row reports SS, df, MS, and F for the between and within sources. The total row sums SS and df but has no MS or F entry. Software (R, SPSS) prints this table automatically once you specify the grouping factor.""",
    "body_he_md": """**הגדרה:** $k$ קבוצות, קבוצה $i$ בגודל $n_i$, סה\"כ $N = \\sum_{i=1}^k n_i$. ממוצע כולל: $\\bar{x}_{..} = \\dfrac{\\sum_{i,j} x_{ij}}{N}$. ממוצע קבוצה: $\\bar{x}_i = \\dfrac{1}{n_i}\\sum_j x_{ij}$.

**SSB — שונות בין-קבוצתית:** שונות המוסברת על ידי שיוך לקבוצה.
$$\\text{SSB} = \\sum_{i=1}^k n_i(\\bar{x}_i - \\bar{x}_{..})^2$$

**SSW — שונות תוך-קבוצתית:** שונית שארית בתוך קבוצות (שגיאה).
$$\\text{SSW} = \\sum_{i=1}^k \\sum_{j=1}^{n_i} (x_{ij} - \\bar{x}_i)^2$$

**SST כולל:** $\\text{SST} = \\text{SSB} + \\text{SSW} = \\sum_{i,j}(x_{ij}-\\bar{x}_{..})^2$.

**דרגות חופש:** $df_B = k-1$, $df_W = N-k$, $df_T = N-1$.

**ממוצעי ריבועים:** $\\text{MSB} = \\text{SSB}/(k-1)$, $\\text{MSW} = \\text{SSW}/(N-k)$.

**סטטיסטיקת F:** $F = \\text{MSB}/\\text{MSW}$.

**השערות:** $H_0: \\mu_1 = \\mu_2 = \\cdots = \\mu_k$ לעומת $H_1$: לפחות שני ממוצעים שונים.

**החלטה:** דחה $H_0$ אם $F > F_{\\alpha,\\,k-1,\\,N-k}$ או $p\\text{-value} < \\alpha$.

**גודל אפקט:** $\\eta^2 = \\text{SSB}/\\text{SST}$ — חלק השונות הכוללת שמוסבר על ידי הקבוצות.

**מבנה טבלת ANOVA:** כל שורה מדווחת SS, df, MS ו-F למקורות בין-קבוצתי ותוך-קבוצתי. שורת הסה\"כ מסכמת SS ו-df ללא MS או F. תוכנות (R, SPSS) מדפיסות טבלה זו אוטומטית לאחר הגדרת גורם הקיבוץ.""",
}

THEORY = {
    "body_en_md": """**Why F = MSB / MSW?** When $H_0$ is true (all population means equal), both MSB and MSW are unbiased estimators of the same population variance $\\sigma^2$, so $F \\approx 1$. When $H_1$ is true (means differ), MSB is inflated by systematic between-group differences while MSW still estimates $\\sigma^2$, so $F \\gg 1$.

**Sampling distribution.** Under $H_0$, $F \\sim F(k-1,\\,N-k)$. MSB/$\\sigma^2$ and MSW/$\\sigma^2$ are independent chi-square ratios; their quotient follows the F-distribution with numerator df $k-1$ and denominator df $N-k$.

**ANOVA assumptions (check before testing):**
1. **Independence:** observations within and across groups are independent.
2. **Normality:** each group is drawn from a normal population (robust for moderate $n_i$).
3. **Homoscedasticity:** equal population variances across groups (Levene's test if unsure).

**Variance decomposition identity:** $\\text{SST} = \\text{SSB} + \\text{SSW}$ always holds — every deviation from the grand mean splits into a between-group component and a within-group residual.

**Relationship to t-test.** With $k=2$ groups, one-way ANOVA is equivalent to a two-sample t-test; $F = t^2$ with the same p-value (for equal variances).

**After rejection.** ANOVA is **omnibus** — it does not say which groups differ. Follow with Tukey HSD, Bonferroni, or Fisher LSD while controlling family-wise error.""",
    "body_he_md": """**למה F = MSB / MSW?** כאשר $H_0$ נכון (כל ממוצעי האוכלוסייה שווים), גם MSB וגם MSW הם מעריכים לא מוטים של אותה שונות $\\sigma^2$, ולכן $F \\approx 1$. כאשר $H_1$ נכון (ממוצעים שונים), MSB מנופח על ידי הבדלים שיטתיים בין-קבוצתיים בעוד MSW עדיין מעריך $\\sigma^2$, ולכן $F \\gg 1$.

**התפלגות דגימה.** תחת $H_0$, $F \\sim F(k-1,\\,N-k)$. MSB/$\\sigma^2$ ו-MSW/$\\sigma^2$ הם יחסי chi-square בלתי-תלויים; מנהם עוקב אחרי פילוג F עם df מונה $k-1$ ו-df מכנה $N-k$.

**הנחות ANOVA (בדקו לפני המבחן):**
1. **בלתי-תלות:** תצפיות בתוך ובין קבוצות בלתי-תלויות.
2. **נורמליות:** כל קבוצה נדגמת מאוכלוסייה נורמלית (עמיד ל-$n_i$ בינוני).
3. **הומוסקדסטיות:** שוויון שונויות אוכלוסייה בין קבוצות (מבחן Levene אם לא בטוחים).

**זהות פירוק שונות:** $\\text{SST} = \\text{SSB} + \\text{SSW}$ תמיד — כל סטייה מהממוצע הכולל מתפצלת לרכיב בין-קבוצתי ולשארית תוך-קבוצתית.

**קשר למבחן t.** עם $k=2$ קבוצות, ANOVA חד-כיווני שקול למבחן t לשתי אוכלוסיות; $F = t^2$ עם אותו p-value (לשוויון שונויות).

**לאחר דחייה.** ANOVA הוא **אומניבוס** — לא אומר אילו קבוצות שונות. המשיכו ב-Tukey HSD, Bonferroni או Fisher LSD תוך שליטה בשגיאה משפחתית.""",
}

WE1 = {
    "body_en_md": """**Two teaching methods.** Group A scores: 70, 80, 90. Group B scores: 60, 70, 80. Test $H_0: \\mu_A = \\mu_B$ at $\\alpha=0.05$.

### Move 1: Group and grand means
$$\\bar{x}_A = 80, \\quad \\bar{x}_B = 70, \\quad \\bar{x}_{..} = \\frac{70+80+90+60+70+80}{6} = 75.$$

### Move 2: SSB ($k=2$, $n_A=n_B=3$)
$$\\text{SSB} = 3(80-75)^2 + 3(70-75)^2 = 3(25) + 3(25) = 150.$$

### Move 3: SSW
$$\\text{SSW}_A = (70-80)^2+(80-80)^2+(90-80)^2 = 100+0+100=200.$$
$$\\text{SSW}_B = (60-70)^2+(70-70)^2+(80-70)^2 = 100+0+100=200.$$
$$\\text{SSW} = 400.$$

### Move 4: F-statistic
$df_B = 1$, $df_W = 4$. $\\text{MSB} = 150/1 = 150$, $\\text{MSW} = 400/4 = 100$, $F = 150/100 = 1.5$.

### Move 5: Decision
$F_{0.05,1,4} = 7.71$. Since $1.5 < 7.71$, **fail to reject $H_0$**. The 10-point gap in sample means is not statistically significant with only $n=3$ per group — within-group spread dominates.

**Note:** With $k=2$, this ANOVA is equivalent to a pooled-variance t-test; here $t = \\sqrt{1.5} \\approx 1.22$, which also fails to reject at 5%. The small sample size ($n=3$ per group) limits statistical power — larger samples might detect the 10-point mean gap despite high within-group variance.""",
    "body_he_md": """**שתי שיטות הוראה.** קבוצה A: 70, 80, 90. קבוצה B: 60, 70, 80. בדוק $H_0: \\mu_A = \\mu_B$ ב-$\\alpha=0.05$.

### צעד 1: ממוצעי קבוצות וממוצע כולל
$$\\bar{x}_A = 80, \\quad \\bar{x}_B = 70, \\quad \\bar{x}_{..} = \\frac{70+80+90+60+70+80}{6} = 75.$$

### צעד 2: SSB ($k=2$, $n_A=n_B=3$)
$$\\text{SSB} = 3(80-75)^2 + 3(70-75)^2 = 3(25) + 3(25) = 150.$$

### צעד 3: SSW
$$\\text{SSW}_A = (70-80)^2+(80-80)^2+(90-80)^2 = 100+0+100=200.$$
$$\\text{SSW}_B = (60-70)^2+(70-70)^2+(80-70)^2 = 100+0+100=200.$$
$$\\text{SSW} = 400.$$

### צעד 4: סטטיסטיקת F
$df_B = 1$, $df_W = 4$. $\\text{MSB} = 150$, $\\text{MSW} = 100$, $F = 1.5$.

### צעד 5: החלטה
$F_{0.05,1,4} = 7.71$. מאחר ש-$1.5 < 7.71$: **לא דוחים $H_0$**. הפער של 10 נקודות בממוצעי המדגם אינו מובהק עם $n=3$ בלבד — השונות התוך-קבוצתית שולטת.

**הערה:** עם $k=2$, ANOVA זה שקול למבחן t לשתי אוכלוסיות; כאן $t = \\sqrt{1.5} \\approx 1.22$, גם הוא לא דוחה ב-5%. גודל המדגם הקטן ($n=3$ לקבוצה) מגביל עוצמה — מדגמים גדולים יותר עשויים לגלות את הפער של 10 נקודות למרות השונות הגבוהה בתוך הקבוצות.""",
}

WE2 = {
    "body_en_md": """**Three diets.** Weight loss (kg): Diet 1: 3, 5, 4. Diet 2: 6, 7, 8. Diet 3: 2, 3, 4. Test at $\\alpha=0.05$.

### Move 1: Means
$\\bar{x}_1=4$, $\\bar{x}_2=7$, $\\bar{x}_3=3$, $\\bar{x}_{..}=(12+21+9)/9=42/9\\approx4.67$.

### Move 2: SSB ($n_i=3$ each)
$$\\text{SSB}=3(4-4.67)^2+3(7-4.67)^2+3(3-4.67)^2 = 1.347+16.287+8.367=26.$$

### Move 3: SSW
$$\\text{SSW}_1=(3-4)^2+(5-4)^2+(4-4)^2=2, \\quad \\text{SSW}_2=2, \\quad \\text{SSW}_3=2, \\quad \\text{SSW}=6.$$

### Move 4: ANOVA table
$df_B=2$, $df_W=6$. $\\text{MSB}=26/2=13$, $\\text{MSW}=6/6=1$, $F=13$.

### Move 5: Decision
$F_{0.05,2,6}\\approx5.14$. Since $13>5.14$: **reject $H_0$**. At least one diet produces significantly different weight loss. Post-hoc tests would show Diet 2 (mean 7) differs from Diets 1 and 3.

**Effect size:** $\\eta^2 = 26/32 = 0.8125$ — most of the variance in weight loss is explained by diet choice. This large effect aligns with the very high F-statistic ($F=13$). Always report both statistical significance and $\\eta^2$ in practice.""",
    "body_he_md": """**שלוש דיאטות.** ירידה במשקל (ק\"ג): דיאטה 1: 3,5,4. דיאטה 2: 6,7,8. דיאטה 3: 2,3,4. בדוק ב-$\\alpha=0.05$.

### צעד 1: ממוצעים
$\\bar{x}_1=4$, $\\bar{x}_2=7$, $\\bar{x}_3=3$, $\\bar{x}_{..}=(12+21+9)/9\\approx4.67$.

### צעד 2: SSB ($n_i=3$ לכל קבוצה)
$$\\text{SSB}=3(4-4.67)^2+3(7-4.67)^2+3(3-4.67)^2 = 1.347+16.287+8.367=26.$$

### צעד 3: SSW
$$\\text{SSW}_1=2, \\quad \\text{SSW}_2=2, \\quad \\text{SSW}_3=2, \\quad \\text{SSW}=6.$$

### צעד 4: טבלת ANOVA
$df_B=2$, $df_W=6$. $\\text{MSB}=13$, $\\text{MSW}=1$, $F=13$.

### צעד 5: החלטה
$F_{0.05,2,6}\\approx5.14$. מאחר ש-$13>5.14$: **דוחים $H_0$**. לפחות דיאטה אחת שונה מובהקת. מבחני post-hoc יראו שדיאטה 2 (ממוצע 7) שונה מ-1 ו-3.

**גודל אפקט:** $\\eta^2 = 26/32 = 0.8125$ — רוב השונות בירידת המשקל מוסבר על ידי בחירת הדיאטה. אפקט גדול זה תואם את סטטיסטיקת F הגבוהה מאוד ($F=13$). בפועל, דווחו תמיד גם מובהקות סטטיסטית וגם $\\eta^2$.""",
}

WE3 = {
    "body_en_md": """**Exam scores for 4 study groups** ($n_i = 5$ each, $N=20$, $k=4$): SSB = 300, SSW = 200.

### Move 1: Complete ANOVA table

| Source | SS | df | MS | F |
|---|---|---|---|---|
| Between | 300 | 3 | 100 | 7.5 |
| Within | 200 | 16 | 12.5 | |
| Total | 500 | 19 | | |

### Move 2: Hypothesis test
$F_{0.05,3,16} = 3.24$. Since $F=7.5 > 3.24$: **reject $H_0$** at 5% level.

### Move 3: Effect size
$$\\eta^2 = \\frac{\\text{SSB}}{\\text{SST}} = \\frac{300}{500} = 0.60.$$
60% of score variance is explained by group membership — a **large** effect (Cohen: $\\eta^2 \\geq 0.14$ is large).

### Move 4: Full conclusion
There is a statistically significant difference among the 4 groups ($F(3,16)=7.5$, $p<0.05$) with large effect ($\\eta^2=0.60$). Tukey or Bonferroni post-hoc tests are needed to identify which specific pairs differ — ANOVA alone cannot rank groups.""",
    "body_he_md": """**ציוני מבחן ל-4 קבוצות לימוד** ($n_i=5$ לכל אחת, $N=20$, $k=4$): SSB = 300, SSW = 200.

### צעד 1: טבלת ANOVA מלאה

| מקור | SS | df | MS | F |
|---|---|---|---|---|
| בין-קבוצות | 300 | 3 | 100 | 7.5 |
| תוך-קבוצות | 200 | 16 | 12.5 | |
| כולל | 500 | 19 | | |

### צעד 2: מבחן השערות
$F_{0.05,3,16}=3.24$. מאחר ש-$F=7.5>3.24$: **דוחים $H_0$** ברמה 5%.

### צעד 3: גודל אפקט
$$\\eta^2 = \\frac{300}{500} = 0.60$$
60% משונות הציונים מוסברת על ידי הקבוצה — אפקט **גדול** (Cohen: $\\eta^2 \\geq 0.14$ נחשב גדול).

### צעד 4: מסקנה מלאה
קיים הבדל מובהק בין 4 הקבוצות ($F(3,16)=7.5$, $p<0.05$) עם אפקט גדול ($\\eta^2=0.60$). נדרשים מבחני post-hoc של Tukey או Bonferroni לזיהוי אילו זוגות שונים — ANOVA לבדו לא מדרג קבוצות.""",
}

METHOD = {
    "body_en_md": """**One-way ANOVA — 8 steps:**
1. **State hypotheses:** $H_0: \\mu_1=\\cdots=\\mu_k$; $H_1$: at least two differ.
2. **Compute** group means $\\bar{x}_i$ and grand mean $\\bar{x}_{..}$.
3. **SSB** $= \\sum_i n_i(\\bar{x}_i - \\bar{x}_{..})^2$.
4. **SSW** $= \\sum_{i,j}(x_{ij}-\\bar{x}_i)^2$; verify $\\text{SST}=\\text{SSB}+\\text{SSW}$.
5. **df:** $df_B = k-1$, $df_W = N-k$.
6. **MSB** $=$ SSB/$df_B$; **MSW** $=$ SSW/$df_W$.
7. **F** $=$ MSB/MSW; compare to $F_{\\alpha, df_B, df_W}$ or use p-value.
8. **Conclude in context**; if reject, plan post-hoc pairwise comparisons.

| $F$ large | $F \\approx 1$ |
|---|---|
| Reject $H_0$ — groups differ | Fail to reject — no evidence |

**Quick check:** MS values must be positive; $F$ is always $\\geq 0$. If you get $F<1$, you will almost always fail to reject.""",
    "body_he_md": """**ANOVA חד-כיווני — 8 שלבים:**
1. **נסח השערות:** $H_0: \\mu_1=\\cdots=\\mu_k$; $H_1$: לפחות שניים שונים.
2. **חשב** ממוצעי קבוצות $\\bar{x}_i$ וממוצע כולל $\\bar{x}_{..}$.
3. **SSB** $= \\sum_i n_i(\\bar{x}_i - \\bar{x}_{..})^2$.
4. **SSW** $= \\sum_{i,j}(x_{ij}-\\bar{x}_i)^2$; ודא $\\text{SST}=\\text{SSB}+\\text{SSW}$.
5. **df:** $df_B = k-1$, $df_W = N-k$.
6. **MSB** $=$ SSB/$df_B$; **MSW** $=$ SSW/$df_W$.
7. **F** $=$ MSB/MSW; השווה ל-$F_{\\alpha, df_B, df_W}$ או השתמש ב-p-value.
8. **הסק מסקנה בהקשר**; אם דוחים, תכנן השוואות post-hoc זוגיות.

| $F$ גדול | $F \\approx 1$ |
|---|---|
| דחה $H_0$ — קבוצות שונות | לא דוחה — אין עדות |

**בדיקה מהירה:** ערכי MS חייבים להיות חיוביים; $F$ תמיד $\\geq 0$. אם $F<1$, כמעט תמיד לא תדחו.""",
}

PITFALL = {
    "body_en_md": """1. **Multiple t-tests instead of ANOVA.** With $k$ groups there are $\\binom{k}{2}$ pairwise comparisons; each at level $\\alpha$ inflates family-wise error. Always use ANOVA first for $k \\geq 3$.

2. **Wrong degrees of freedom.** $df_B = k-1$ (groups minus one), $df_W = N-k$ (total minus number of groups). Do not use $N-1$ for the F denominator.

3. **Using SSB instead of MSB in F.** $F = \\text{MSB}/\\text{MSW}$, not SSB/SSW. Forgetting to divide by df is the most common arithmetic error.

4. **Identifying specific groups from ANOVA alone.** Rejection means *at least one* mean differs — not which pair. Post-hoc tests (Tukey, Bonferroni) are required.

5. **Ignoring assumptions.** Severe non-normality or unequal variances with small $n_i$ invalidate F-tests. Consider Welch ANOVA or Kruskal-Wallis as alternatives.""",
    "body_he_md": """1. **מבחני t מרובים במקום ANOVA.** עם $k$ קבוצות יש $\\binom{k}{2}$ השוואות זוגיות; כל אחת ברמה $\\alpha$ מנפחת שגיאה משפחתית. תמיד השתמשו ב-ANOVA קודם ל-$k \\geq 3$.

2. **דרגות חופש שגויות.** $df_B = k-1$ (קבוצות פחות אחת), $df_W = N-k$ (סה\"כ פחות מספר קבוצות). אל תשתמשו ב-$N-1$ למכנה של F.

3. **שימוש ב-SSB במקום MSB ב-F.** $F = \\text{MSB}/\\text{MSW}$, לא SSB/SSW. שכחת חלוקה ב-df היא שגיאת חשבון נפוצה ביותר.

4. **זיהוי קבוצות ספציפיות מ-ANOVA בלבד.** דחייה משמעה *לפחות* ממוצע אחד שונה — לא איזה זוג. נדרשים מבחני post-hoc (Tukey, Bonferroni).

5. **התעלמות מהנחות.** חוסר נורמליות חמור או שונויות לא שוות עם $n_i$ קטן מבטלים את מבחן F. שקלו Welch ANOVA או Kruskal-Wallis כחלופות.""",
}

WHY = {
    "body_en_md": """One-way ANOVA is the workhorse of experimental design: clinical trials comparing treatments, education studies comparing teaching methods, and industrial quality control all rely on comparing means across multiple groups in one controlled test.

In university statistics, ANOVA connects the t-test (two groups) to more advanced models — two-way ANOVA, regression, and mixed models all extend the same variance-partitioning logic. SPSS, R (`aov`), and Excel ANOVA tools implement identical formulas.

For research and data science careers, knowing when ANOVA applies (continuous outcome, categorical factor with $k \\geq 2$ groups) prevents both inflated Type I error from multiple t-tests and invalid conclusions from ignoring effect size ($\\eta^2$). On exams, partial credit is common for a correct ANOVA table even if the final decision is wrong — master SSB, SSW, and df first.""",
    "body_he_md": """ANOVA חד-כיווני הוא עמוד השדרה של תכנון ניסויים: ניסויים קליניים המשווים טיפולים, מחקרי חינוך על שיטות הוראה, ובקרת איכות תעשייתית — כולם מסתמכים על השוואת ממוצעים בין קבוצות במבחן אחד מבוקר.

בסטטיסטיקה אוניברסיטאית, ANOVA מחבר את מבחן t (שתי קבוצות) למודלים מתקדמים — ANOVA דו-כיווני, רגרסיה ומודלים מעורבים מרחיבים את אותה לוגיקת פירוק שונות. SPSS, R (`aov`) ו-Excel מיישמים נוסחאות זהות.

לקריירות במחקר ומדע נתונים, ידיעה מתי ANOVA מתאים (תוצאה רציפה, גורם קטגורי עם $k \\geq 2$ קבוצות) מונעת גם שגיאת סוג I מנפוחה ממבחני t מרובים וגם מסקנות לא תקפות מהתעלמות מגודל אפקט ($\\eta^2$). בבחינות, נקודות חלקיות נפוצות על טבלת ANOVA נכונה גם אם ההחלטה הסופית שגויה — שלטו קודם ב-SSB, SSW ו-df.""",
}

BEFORE = {
    "body_en_md": """**Formula card:**
- SSB $= \\sum_i n_i(\\bar{x}_i - \\bar{x}_{..})^2$
- SSW $= \\sum_{i,j}(x_{ij}-\\bar{x}_i)^2$; SST $=$ SSB $+$ SSW
- $df_B = k-1$, $df_W = N-k$
- $F = \\text{MSB}/\\text{MSW}$
- $\\eta^2 = \\text{SSB}/\\text{SST}$

**Exam patterns:**
- Build full ANOVA table from raw data or partial sums.
- Compute $F$ and compare to given critical value.
- Interpret $\\eta^2$ as effect size.
- Explain why multiple t-tests are invalid; state post-hoc next step after rejection.

**Tip:** Build the table in order: SS → df → MS → F. Verify $\\text{SST}=\\text{SSB}+\\text{SSW}$ before computing $F$ — mismatched totals catch most arithmetic errors early on exams.""",
    "body_he_md": """**גיליון נוסחאות:**
- SSB $= \\sum_i n_i(\\bar{x}_i-\\bar{x}_{..})^2$
- SSW $= \\sum_{i,j}(x_{ij}-\\bar{x}_i)^2$; SST = SSB + SSW
- $df_B=k-1$, $df_W=N-k$
- $F=\\text{MSB}/\\text{MSW}$
- $\\eta^2=\\text{SSB}/\\text{SST}$

**דגשי בחינות:**
- בנה טבלת ANOVA מלאה מנתונים גולמיים או סכומי ריבועים חלקיים.
- חשב $F$ והשווה לערך קריטי נתון.
- פרש $\\eta^2$ כגודל אפקט.
- הסבר מדוע מבחני t מרובים לא תקפים; ציין post-hoc לאחר דחייה.

**טיפ:** בנה טבלה בסדר: SS → df → MS → F. ודא $\\text{SST}=\\text{SSB}+\\text{SSW}$ לפני $F$ — אי-התאמה תופסת רוב השגיאות.""",
}

SUMMARY = {
    "body_en_md": """- **One-way ANOVA** tests $H_0: \\mu_1=\\cdots=\\mu_k$ in one test, avoiding the multiple-comparisons problem when $k \\geq 3$.
- **F = MSB/MSW**: large $F$ means between-group variance dominates within-group variance; $F \\approx 1$ supports equal means.
- **ANOVA table:** SST = SSB + SSW; $df_B=k-1$, $df_W=N-k$; always compute MS before F.
- **Reject $H_0$** if $F > F_{\\alpha, k-1, N-k}$; use post-hoc tests (Tukey, Bonferroni) to find which groups differ.
- **$\\eta^2 = \\text{SSB/SST}$** measures effect size — proportion of total variance explained by group membership.""",
    "body_he_md": """- **ANOVA חד-כיווני** בודק $H_0: \\mu_1=\\cdots=\\mu_k$ במבחן אחד, ומונע בעיית השוואות מרובות כש-$k \\geq 3$.
- **$F=\\text{MSB/MSW}$**: $F$ גדול משמעותו שהשונות הבין-קבוצתית גדולה מהתוך-קבוצתית; $F \\approx 1$ תומך בממוצעים שווים.
- **טבלת ANOVA:** SST=SSB+SSW; $df_B=k-1$, $df_W=N-k$; תמיד חשבו MS לפני F.
- **דחה $H_0$** אם $F > F_{\\alpha,k-1,N-k}$; השתמשו ב-post-hoc (Tukey, Bonferroni) לזיהוי הקבוצות השונות.
- **$\\eta^2=\\text{SSB/SST}$** מודד גודל אפקט — חלק השונות הכוללת שמוסבר על ידי שיוך לקבוצה.""",
}


def build_questions():
    expls = [
        fmt_expl(
            "One-way ANOVA tests whether the population means of $k$ groups are all equal. For $k=4$ groups, the null hypothesis is $H_0: \\mu_1 = \\mu_2 = \\mu_3 = \\mu_4$. The alternative is that at least two means differ — ANOVA does not specify which pair.",
            "Identify the test purpose first: equality of means across groups. Write all $k$ means in $H_0$ with equals signs. The alternative is always \"at least two differ\" for one-way ANOVA.",
            "Writing $H_1: \\mu_1 \\neq \\mu_2$ (pairwise) instead of the omnibus alternative. Stating $H_0: \\mu_1 = \\mu_2$ when there are four groups — omitting groups 3 and 4.",
            "Hypothesis-statement items are quick points. Template: $H_0: \\mu_1=\\cdots=\\mu_k$; $H_1$: at least two means differ. Always match $k$ from the problem.",
            "ANOVA חד-כיווני בודק אם ממוצעי האוכלוסייה של $k$ קבוצות שווים. ל-$k=4$ קבוצות, $H_0: \\mu_1 = \\mu_2 = \\mu_3 = \\mu_4$. החלופית: לפחות שני ממוצעים שונים — ANOVA לא מציין איזה זוג.",
            "זהו קודם את מטרת המבחן: שוויון ממוצעים בין קבוצות. כתבו את כל $k$ הממוצעים ב-$H_0$ עם סימני שוויון. החלופית תמיד \"לפחות שניים שונים\" ב-ANOVA חד-כיווני.",
            "כתיבת $H_1: \\mu_1 \\neq \\mu_2$ (זוגי) במקום חלופית אומניבוס. $H_0: \\mu_1 = \\mu_2$ כשיש ארבע קבוצות — השמטת קבוצות 3 ו-4.",
            "שאלות ניסוח השערות הן נקודות מהירות. תבנית: $H_0: \\mu_1=\\cdots=\\mu_k$; $H_1$: לפחות שני ממוצעים שונים. תמיד התאימו $k$ מהשאלה.",
        ),
        fmt_expl(
            "With $k=3$ groups, $df_B = k-1 = 3-1 = 2$. With $N=30$ total observations, $df_W = N-k = 30-3 = 27$. These df values locate the critical F value and the sampling distribution of the test statistic.",
            "Memorize the pair: $df_B = k-1$ (between groups), $df_W = N-k$ (within/error). $k$ is the number of groups; $N$ is total sample size across all groups.",
            "Using $df_B = N-1$ or $df_W = k-1$ (swapping the formulas). Computing $df_W = 30-1 = 29$ by forgetting to subtract $k$.",
            "df items appear before every F computation. Write both formulas on your formula card: $df_B=k-1$, $df_W=N-k$. Quick sanity: $df_B + df_W = N-1 = df_T$.",
            "עם $k=3$ קבוצות, $df_B = k-1 = 2$. עם $N=30$ תצפיות, $df_W = N-k = 27$. ערכי df אלה קובעים את ערך F הקריטי ואת התפלגות הסטטיסטיקה.",
            "שיננו את הזוג: $df_B = k-1$ (בין קבוצות), $df_W = N-k$ (תוך/שגיאה). $k$ מספר הקבוצות; $N$ גודל המדגם הכולל בכל הקבוצות.",
            "שימוש ב-$df_B = N-1$ או $df_W = k-1$ (החלפת נוסחאות). $df_W = 30-1 = 29$ בשכחת חיסור $k$.",
            "שאלות df מופיעות לפני כל חישוב F. רשמו: $df_B=k-1$, $df_W=N-k$. בדיקה: $df_B + df_W = N-1 = df_T$ — זהו תמיד.",
        ),
        fmt_expl(
            "First find df: $df_B = k-1 = 2$, $df_W = N-k = 15-3 = 12$. Then $\\text{MSB} = 50/2 = 25$ and $\\text{MSW} = 120/12 = 10$. Finally $F = 25/10 = 2.5$.",
            "Work in order: identify $k$ and $N$ → compute df → divide SS by df to get MS → divide MSB by MSW. Never skip the df step — dividing SSB by SSW directly gives the wrong answer.",
            "Computing $F = 50/120 \\approx 0.42$ using raw sums of squares. Using $df_W = N-1 = 14$ instead of $N-k = 12$.",
            "When given SSB and SSW directly, the exam still expects df and MS columns. Write the mini-table: MSB=25, MSW=10, F=2.5. If $F$ is between 1 and 5, it is plausible — always compare to the critical value next.",
            "קודם מצאו df: $df_B = 2$, $df_W = 15-3 = 12$. אז $\\text{MSB} = 50/2 = 25$ ו-$\\text{MSW} = 120/12 = 10$. לבסוף $F = 25/10 = 2.5$.",
            "עבדו בסדר: זהו $k$ ו-$N$ → חשבו df → חלקו SS ב-df ל-MS → חלקו MSB ב-MSW. אל תדלגו על df — חלוקת SSB ב-SSW ישירות נותנת תשובה שגויה.",
            "$F = 50/120 \\approx 0.42$ מסכומי ריבועים גולמיים. $df_W = N-1 = 14$ במקום $N-k = 12$.",
            "כשניתנים SSB ו-SSW, הבחינה עדיין מצפה ל-df ו-MS. כתבו: MSB=25, MSW=10, F=2.5. אם $F$ בין 1 ל-5, סביר — תמיד השוו לערך קריטי.",
        ),
        fmt_expl(
            "Since $F = 1.1 < F_{\\text{crit}} = 4.26$, we **fail to reject $H_0$**. The observed between-group variation is not large enough relative to within-group variation to conclude that group means differ at this significance level.",
            "Decision rule: reject if $F > F_{\\text{crit}}$; otherwise fail to reject. $F \\approx 1$ means MSB and MSW are similar — consistent with equal means. Never say \"accept $H_0$\" — use \"fail to reject.\"",
            "Rejecting because \"1.1 is close to 4.26\" without the inequality direction. Saying \"accept $H_0$\" instead of the proper frequentist language. Confusing $F < F_{\\text{crit}}$ with rejection.",
            "Interpretation questions give both statistics — no computation needed. Template: compare, state reject/fail to reject, add one context sentence. If $F$ is near 1, the answer is almost always fail to reject.",
            "מאחר ש-$F = 1.1 < F_{\\text{crit}} = 4.26$, **לא דוחים $H_0$**. השונות הבין-קבוצתית אינה גדולה מספיק ביחס לתוך-קבוצתית כדי להסיק שהממוצעים שונים.",
            "כלל החלטה: דחו אם $F > F_{\\text{crit}}$; אחרת לא דוחים. $F \\approx 1$ משמע MSB ו-MSW דומים — עקבי עם ממוצעים שווים. לעולם אל תגידו \"מקבלים $H_0$\" — \"לא דוחים\".",
            "דחייה כי \"1.1 קרוב ל-4.26\" בלי כיוון אי-השוויון. \"מקבלים $H_0$\" במקום הניסוח הנכון. בלבול $F < F_{\\text{crit}}$ עם דחייה.",
            "שאלות פרשנות נותנות שתי סטטיסטיקות — ללא חישוב. תבנית: השוו, ציינו דחייה/אי-דחייה, משפט הקשר. אם $F$ קרוב ל-1, התשובה כמעט תמיד אי-דחייה.",
        ),
        fmt_expl(
            "SSB measures weighted squared deviations of group means from the grand mean: $\\text{SSB} = 4(5-6.33)^2 + 4(8-6.33)^2 + 4(6-6.33)^2 = 4(1.77) + 4(2.79) + 4(0.11) = 7.08 + 11.16 + 0.44 = 18.68$. Each group contributes $n_i(\\bar{x}_i - \\bar{x}_{..})^2$.",
            "When group sizes are equal ($n=4$), factor $n$ out: $\\text{SSB} = 4\\sum(\\bar{x}_i - \\bar{x}_{..})^2$. Compute each squared deviation first, then multiply by 4.",
            "Forgetting to multiply by $n_i$ — using $(\\bar{x}_i - \\bar{x}_{..})^2$ alone. Using the grand mean incorrectly (e.g., averaging the three group means without weighting by $n$).",
            "SSB from means-only problems are common exam items. Write the formula, substitute each group mean and the given grand mean, show one squared term before summing. Partial credit for correct setup.",
            "SSB מודד סטיות בריבוע משוקללות של ממוצעי קבוצות מהממוצע הכולל: $\\text{SSB} = 4(1.77) + 4(2.79) + 4(0.11) = 18.68$. כל קבוצה תורמת $n_i(\\bar{x}_i - \\bar{x}_{..})^2$.",
            "כשגדלי קבוצות שווים ($n=4$), הוציאו $n$: $\\text{SSB} = 4\\sum(\\bar{x}_i - \\bar{x}_{..})^2$. חשבו כל סטייה בריבוע, ואז הכפילו ב-4.",
            "שכחת הכפלה ב-$n_i$ — שימוש ב-$(\\bar{x}_i - \\bar{x}_{..})^2$ בלבד. ממוצע כולל שגוי (ממוצע פשוט של שלושה ממוצעי קבוצות בלי משקל $n$).",
            "שאלות SSB מממוצעים נפוצות בבחינה. כתבו נוסחה, הציבו ממוצעי קבוצות וממוצע כולל, הראו מונח אחד לפני סיכום. נקודות חלקיות על הכנה נכונה.",
        ),
        fmt_expl(
            "SSW sums squared deviations within each group: $\\text{SSW}_A = (2-4)^2+(4-4)^2+(6-4)^2 = 4+0+4 = 8$. Group B has zero spread (all values equal 5), so $\\text{SSW}_B = 0$. Total $\\text{SSW} = 8$.",
            "SSW uses **group means**, not the grand mean. For each observation, subtract its own group mean before squaring. Constant groups contribute zero to SSW — a key insight for understanding F.",
            "Using the grand mean 4.5 instead of group means 4 and 5. Computing SSB instead of SSW. Missing that identical values within a group give zero within-group variance.",
            "This problem tests whether you distinguish SSB (between) from SSW (within). Group B's zero SSW is intentional — it shows within-group spread can differ across groups while ANOVA still pools SSW.",
            "SSW מסכם סטיות בריבוע בתוך כל קבוצה: $\\text{SSW}_A = 4+0+4 = 8$. קבוצה B ללא פיזור (כל הערכים 5), $\\text{SSW}_B = 0$. סה\"כ $\\text{SSW} = 8$.",
            "SSW משתמש ב**ממוצעי קבוצות**, לא בממוצע הכולל. לכל תצפית, חסרו ממוצע הקבוצה שלה לפני ריבוע. קבוצות קבועות תורמות אפס — תובנה מפתח להבנת F.",
            "שימוש בממוצע כולל 4.5 במקום ממוצעי קבוצות 4 ו-5. חישוב SSB במקום SSW. החמצה שערכים זהים בקבוצה נותנים שונות תוך-קבוצתית אפס.",
            "תרגיל זה בודק הבחנה בין SSB (בין) ל-SSW (תוך). SSW=0 של קבוצה B מכוון — מראה שפיזור תוך-קבוצתי יכול להשתנות בין קבוצות.",
        ),
        fmt_expl(
            "The observed $F(2,18) = 4.5$ exceeds the critical value $F_{0.05,2,18} = 3.55$, so we **reject $H_0$** at the 5% significance level. There is statistically significant evidence that at least one group mean differs.",
            "Compare the computed F to the critical F at the stated $\\alpha$ and df. The notation $F(2,18)$ means numerator df=2, denominator df=18. Reject when observed exceeds critical.",
            "Failing to reject because 4.5 \"does not seem very large.\" Using the wrong df row in the F table. Concluding which specific groups differ — ANOVA only gives omnibus significance.",
            "When the exam gives $F(df_1, df_2)$ and $F_{\\alpha, df_1, df_2}$, it is pure comparison. Write: \"4.5 > 3.55, reject $H_0$.\" Add \"at least one mean differs\" — never name specific pairs without post-hoc.",
            "$F(2,18) = 4.5$ גדול מהקריטי $F_{0.05,2,18} = 3.55$, לכן **דוחים $H_0$** ברמת 5%. יש עדות מובהקת שלפחות ממוצע קבוצה אחד שונה.",
            "השוו F מחושב ל-F קריטי ב-$\\alpha$ ו-df נתונים. $F(2,18)$ משמע df מונה=2, מכנה=18. דחו כשהמחושב עולה על הקריטי.",
            "אי-דחייה כי 4.5 \"לא נראה גדול\". שורה שגויה בטבלת F. מסקנה על קבוצות ספציפיות — ANOVA נותן רק מובהקות אומניבוס.",
            "כשהבחינה נותנת $F$ ו-$F_{\\alpha}$, זו השוואה טהורה. כתבו: \"4.5 > 3.55, דוחים $H_0$\". הוסיפו \"לפחות ממוצע אחד שונה\" — לעולם לא ציינו זוגות בלי post-hoc.",
        ),
        fmt_expl(
            "For $c$ independent tests each at significance $\\alpha$, the family-wise Type I error rate is approximately $1-(1-\\alpha)^c$. With 3 groups, there are 3 pairwise t-tests; at $\\alpha=0.05$: $1-(0.95)^3 \\approx 14.3\\%$, far above 5%. One-way ANOVA controls the overall error at $\\alpha$.",
            "Count comparisons: $\\binom{k}{2}$ pairs for $k$ groups. Each t-test has a 5% false-positive chance; the probability of **at least one** false positive grows with more tests. ANOVA replaces many tests with one.",
            "Saying \"more tests means more power\" without mentioning inflated false positives. Computing $c\\alpha = 15\\%$ instead of $1-(1-\\alpha)^c$. Claiming ANOVA eliminates Type I error entirely.",
            "Conceptual ANOVA questions often ask why not t-tests. Memorize: 3 groups → 3 tests → ~14% family-wise error. Mention ANOVA as the single-test solution controlling error at $\\alpha$.",
            "ל-$c$ מבחנים בלתי-תלויים ברמת $\\alpha$, שגיאת סוג I המשפחתית $\\approx 1-(1-\\alpha)^c$. ל-3 קבוצות, 3 מבחני t; ב-$\\alpha=0.05$: $1-(0.95)^3 \\approx 14.3\\%$, הרבה מעל 5%. ANOVA שולט בשגיאה הכוללת ב-$\\alpha$.",
            "ספרו השוואות: $\\binom{k}{2}$ זוגות ל-$k$ קבוצות. כל t-test יש 5% סיכוי לחיובי שגוי; הסתברות **לפחות אחד** גדלה עם יותר מבחנים. ANOVA מחליף רבים במבחן אחד.",
            "\"יותר מבחנים = יותר עוצמה\" בלי להזכיר חיוביים שגויים מנופחים. $c\\alpha = 15\\%$ במקום $1-(1-\\alpha)^c$. טענה ש-ANOVA מבטל לגמרי שגיאת סוג I.",
            "שאלות מושגיות ANOVA שואלות למה לא t-tests. שיננו: 3 קבוצות → 3 מבחנים → ~14% שגיאה משפחתית. ANOVA כפתרון מבחן יחיד בשליטה ב-$\\alpha$.",
        ),
    ]

    acceptable = [
        [
            "ANOVA tests equality of group means",
            "H_0: \\mu_1=\\mu_2=\\mu_3=\\mu_4",
            "\\mu_1=\\mu_2=\\mu_3=\\mu_4",
        ],
        ["df_B = 2", "df_W = 27", "2 and 27"],
        ["F = 2.5", "2.5", "MSB=25, MSW=10, F=2.5"],
        [
            "fail to reject H_0",
            "fail to reject",
            "no significant difference between group means",
        ],
        ["SSB = 18.68", "18.68"],
        ["SSW = 8", "SSW_A = 8", "SSW_B = 0"],
        [
            "reject H_0",
            "4.5 > 3.55",
            "at least one group mean differs",
        ],
        [
            "family-wise Type I error",
            "14%",
            "1-(1-alpha)^c",
            "ANOVA controls overall Type I error at alpha",
        ],
    ]

    orig = json.loads(TARGET.read_text(encoding="utf-8"))
    qs = orig["questions"]
    for i, q in enumerate(qs):
        q["explanation_en"], q["explanation_he"] = expls[i]
        q["answer_payload"]["acceptable_answers"] = acceptable[i]
    return qs


CHECKPOINT_1_EN = """### Move 1: Write the SSB formula
$$\\text{SSB} = \\sum_i n_i(\\bar{x}_i - \\bar{x}_{..})^2$$
Here $n_i = 4$ for all three groups and $\\bar{x}_{..} = 12$.

### Move 2: Substitute each group mean
$$\\text{SSB} = 4(10-12)^2 + 4(12-12)^2 + 4(14-12)^2 = 4(4)+0+4(4) = 32.$$

**Check:** Group 2 sits exactly on the grand mean, so it contributes zero. Groups 1 and 3 are symmetric — each 2 units from 12 — and contribute equally (16 each).

**Common slip:** Forgetting the factor $n_i=4$ on each squared deviation.

**Exam tip:** When all $n_i$ are equal, you can factor $n$ out before summing the squared deviations."""

CHECKPOINT_1_HE = """### צעד 1: כתיבת נוסחת SSB
$$\\text{SSB} = \\sum_i n_i(\\bar{x}_i - \\bar{x}_{..})^2$$
כאן $n_i = 4$ לכל שלוש הקבוצות ו-$\\bar{x}_{..} = 12$.

### צעד 2: הצבת ממוצעי הקבוצות
$$\\text{SSB} = 4(10-12)^2 + 4(12-12)^2 + 4(14-12)^2 = 4(4)+0+4(4) = 32.$$

**בדיקה:** קבוצה 2 בדיוק על הממוצע הכולל, תורמת אפס. קבוצות 1 ו-3 סימטריות — כל אחת 2 יחידות מ-12 — ותורמות שווה (16 כל אחת).

**טעות נפוצה:** שכחת גורם $n_i=4$ על כל סטייה בריבוע.

**טיפ לבחינה:** כשכל $n_i$ שווים, אפשר להוציא $n$ לפני סיכום הסטיות בריבוע."""

CHECKPOINT_2_EN = """### Move 1: Degrees of freedom
$df_B = k-1 = 3-1 = 2$. $df_W = N-k = 18-3 = 15$.

### Move 2: Mean squares
$\\text{MSB} = 40/2 = 20$. $\\text{MSW} = 60/15 = 4$.

### Move 3: F-statistic
$$F = \\frac{\\text{MSB}}{\\text{MSW}} = \\frac{20}{4} = 5.$$

**Verify:** $\\text{SST} = 40+60 = 100$ and $df_T = 17 = df_B + df_W = 2+15$ — the partition identity holds.

**Common slip:** Dividing SSB by SSW directly ($40/60$) instead of using MS.

**Exam tip:** Build the mini-table (SS → df → MS → F) even when only $F$ is asked — it catches df errors early."""

CHECKPOINT_2_HE = """### צעד 1: דרגות חופש
$df_B = k-1 = 2$. $df_W = N-k = 18-3 = 15$.

### צעד 2: ממוצעי ריבועים
$\\text{MSB} = 40/2 = 20$. $\\text{MSW} = 60/15 = 4$.

### צעד 3: סטטיסטיקת F
$$F = \\frac{\\text{MSB}}{\\text{MSW}} = \\frac{20}{4} = 5.$$

**אימות:** $\\text{SST} = 100$ ו-$df_T = 17 = 2+15$ — זהות הפירוק מתקיימת.

**טעות נפוצה:** חלוקת SSB ב-SSW ישירות ($40/60$) במקום MS.

**טיפ לבחינה:** בנו טבלה מינימלית (SS → df → MS → F) גם כשמבקשים רק $F$ — זה תופס שגיאות df מוקדם."""


def fix_exercises(exercises):
    fixes = {
        "e2": {
            "solution_en": "$df_B = k-1 = 3-1 = 2$. $df_W = N-k = 30-3 = 27$. Check: $df_B + df_W = 29 = N-1$.",
            "solution_he": "$df_B = 2$, $df_W = 27$. בדיקה: $df_B + df_W = 29 = N-1$.",
        },
        "e5": {
            "solution_en": "$\\text{SSB}=4(5-6.33)^2+4(8-6.33)^2+4(6-6.33)^2 = 4(1.77)+4(2.79)+4(0.11) = 7.08+11.16+0.44 = 18.68$.",
            "solution_he": "$\\text{SSB} = 4(1.77)+4(2.79)+4(0.11) \\approx 18.68$.",
        },
        "e6": {
            "solution_en": "SSW_A $= (2-4)^2+(4-4)^2+(6-4)^2 = 4+0+4=8$. SSW_B $= (5-5)^2\\times3 = 0$. Total SSW $= 8$.",
            "solution_he": "SSW_A $= 8$, SSW_B $= 0$, SSW $= 8$.",
        },
        "e9": {
            "solution_en": "SSW $= \\text{SST}-\\text{SSB} = 200-80=120$. $\\eta^2 = \\text{SSB}/\\text{SST} = 80/200 = 0.40$ (medium-to-large effect).",
            "solution_he": "SSW $= 120$. $\\eta^2 = 0.40$ (אפקט בינוני-גדול).",
        },
        "e11": {
            "solution_en": "SSB $= 5[(10-13)^2+(14-13)^2+(12-13)^2+(16-13)^2] = 5[9+1+1+9]=100$. MSB $= 100/3\\approx33.3$. MSW $= 80/16=5$. $F=33.3/5=6.67$. Since $6.67>3.24$: **reject $H_0$**.",
            "solution_he": "SSB $= 100$. MSB $\\approx 33.3$, MSW $=5$, $F=6.67>3.24$: **דוחים $H_0$**.",
        },
    }
    for ex in exercises:
        if ex["id"] in fixes:
            ex.update(fixes[ex["id"]])
    return exercises


def main():
    orig = json.loads(TARGET.read_text(encoding="utf-8"))
    exercises = fix_exercises(
        next(s for s in orig["sections"] if s["kind"] == "exercise_set")["exercises"]
    )

    lesson = {
        "concept_id": "anova_one_way",
        "subject": "math",
        "level": "university",
        "math_track": ["statistics"],
        "title_en": "One-Way ANOVA",
        "title_he": "ANOVA חד-כיווני",
        "summary_en": "One-way Analysis of Variance: comparing means across k groups using the F-statistic, within-group and between-group variance, and the F-distribution.",
        "summary_he": "ניתוח שונות חד-כיווני: השוואת ממוצעים בין k קבוצות באמצעות סטטיסטיקת F, שונות תוך-קבוצתית ובין-קבוצתית.",
        "sections": [
            {
                "kind": "intro",
                "title_en": "Comparing More Than Two Groups",
                "title_he": "השוואה בין יותר משתי קבוצות",
                **INTRO,
            },
            {
                "kind": "definition",
                "title_en": "ANOVA Definitions and Formulas",
                "title_he": "הגדרות ונוסחאות ANOVA",
                **DEFINITION,
            },
            {
                "kind": "theory",
                "title_en": "Intuition: Why F = MSB / MSW?",
                "title_he": "אינטואיציה: למה F = MSB / MSW?",
                **THEORY,
            },
            {
                "kind": "worked_example",
                "difficulty": "easy",
                "example_number": 1,
                "title_en": "Worked Example 1 — Two Groups, Simple ANOVA",
                "title_he": "דוגמה פתורה 1 — שתי קבוצות, ANOVA פשוט",
                **WE1,
            },
            {
                "kind": "checkpoint",
                "title_en": "Stop & Practice",
                "title_he": "עצור ותרגל",
                "body_en_md": "Three groups have means $\\bar{x}_1=10$, $\\bar{x}_2=12$, $\\bar{x}_3=14$, each of size $n=4$. Grand mean $= 12$. Compute SSB.",
                "body_he_md": "לשלוש קבוצות יש ממוצעים $\\bar{x}_1=10$, $\\bar{x}_2=12$, $\\bar{x}_3=14$, כל אחת בגודל $n=4$. ממוצע כולל $= 12$. חשב SSB.",
                "checkpoint_solution_en": CHECKPOINT_1_EN,
                "checkpoint_solution_he": CHECKPOINT_1_HE,
            },
            {
                "kind": "worked_example",
                "difficulty": "medium",
                "example_number": 2,
                "title_en": "Worked Example 2 — Three Groups Full ANOVA",
                "title_he": "דוגמה פתורה 2 — ANOVA מלא לשלוש קבוצות",
                **WE2,
            },
            {
                "kind": "checkpoint",
                "title_en": "Stop & Practice",
                "title_he": "עצור ותרגל",
                "body_en_md": "An ANOVA table shows SSB = 40, SSW = 60, $k=3$ groups, $N=18$ total. Compute $F$.",
                "body_he_md": "טבלת ANOVA מראה SSB = 40, SSW = 60, $k=3$ קבוצות, $N=18$ כולל. חשב $F$.",
                "checkpoint_solution_en": CHECKPOINT_2_EN,
                "checkpoint_solution_he": CHECKPOINT_2_HE,
            },
            {
                "kind": "worked_example",
                "difficulty": "hard",
                "example_number": 3,
                "title_en": "Worked Example 3 — Interpreting F and Effect Size",
                "title_he": "דוגמה פתורה 3 — פרשנות F וגודל אפקט",
                **WE3,
            },
            {
                "kind": "method_guide",
                "title_en": "Method Guide — ANOVA Step-by-Step",
                "title_he": "מדריך שיטה — ANOVA שלב אחר שלב",
                **METHOD,
            },
            {
                "kind": "exercise_set",
                "title_en": "Practice Exercises",
                "title_he": "תרגילים",
                "body_en_md": "Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.",
                "body_he_md": "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.",
                "exercises": exercises,
            },
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
        "est_minutes": 50,
        "author": "cursor-claude-2026",
        "version": 1,
        "level_focus": None,
        "skill_atom_bank": None,
    }

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
