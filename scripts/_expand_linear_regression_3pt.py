#!/usr/bin/env python3
"""Expand linear_regression_3pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/linear_regression_3pt.json"

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


INTRO_EN = """When two variables move together — taller people tend to weigh more, more study hours lead to higher grades, warmer days boost ice-cream sales — we can summarise the trend with a **line of best fit** (regression line). At the **3-point Bagrut** level you are **not** asked to derive the line from raw data; the equation $y = a + bx$ is always given, and your job is to **read**, **interpret**, and **predict**.

The regression line models how the **dependent variable** $y$ (the outcome) changes when the **independent variable** $x$ (the predictor) changes. You will work with scatter plots and tables, substitute values into the equation, solve for $x$ when $y$ is known, compute **residuals** (actual minus predicted), and decide whether a prediction is **interpolation** (inside the data range, usually reliable) or **extrapolation** (outside the range, risky).

This topic connects directly to linear functions from algebra (`concept:functions_linear`) and descriptive statistics (`concept:linear_regression_correlation`). Bagrut 3-unit exams typically present a real-world context — salary vs. age, sales vs. temperature — and award marks for **contextual interpretation**, not just arithmetic."""

INTRO_HE = """כששני משתנים נעים יחד — אנשים גבוהים נוטים לשקול יותר, יותר שעות לימוד מובילות לציונים גבוהים, ימים חמים מגבירים מכירות גלידה — אפשר לסכם את המגמה ב**קו מגמה** (קו רגרסיה). ברמת **בגרות 3 יחידות** **אינכם** נדרשים לגזור את הקו מנתונים גולמיים; המשוואה $y=a+bx$ תמיד ניתנת, והמשימה שלכם היא **לקרוא**, **לפרש** ו**לחזות**.

קו הרגרסיה מודל כיצד **המשתנה התלוי** $y$ (התוצאה) משתנה כש**המשתנה הבלתי-תלוי** $x$ (המנבא) משתנה. תעבדו עם גרפי פיזור וטבלאות, תציבו ערכים במשוואה, תפתרו ל-$x$ כש-$y$ ידוע, תחשבו **שאריות** (בפועל פחות חזוי), ותחליטו אם חיזוי הוא **אינטרפולציה** (בתוך טווח הנתונים, בדרך כלל אמין) או **אקסטרפולציה** (מחוץ לטווח, מסוכן).

נושא זה קשור ישירות לפונקציות לינאריות מאלגברה (`concept:functions_linear`) ולסטטיסטיקה תיאורית (`concept:linear_regression_correlation`). בבגרות 3 יחידות מציגים בדרך כלל הקשר מהחיים — משכורת מול גיל, מכירות מול טמפרטורה — ונותנים ניקוד על **פרשנות בהקשר**, לא רק חשבון."""

DEF_EN = """**Regression line (line of best fit):**
$$y = a + bx$$
where:
- $x$ is the **independent variable** (predictor, explanatory, cause).
- $y$ is the **dependent variable** (response, outcome, effect).
- $b$ is the **slope** — the change in predicted $y$ for each 1-unit increase in $x$.
- $a$ is the **y-intercept** — the predicted value of $y$ when $x = 0$.

**Interpretation of the slope $b$:**
- If $b > 0$: **positive (direct) relationship** — as $x$ increases, predicted $y$ increases.
- If $b < 0$: **negative (inverse) relationship** — as $x$ increases, predicted $y$ decreases.
- If $b = 0$: **no linear relationship** — predicted $y$ is constant regardless of $x$.
- $|b|$ measures the **rate of change** in the units of the problem.

**Scatter plot:** A graph of paired data points $(x_i, y_i)$. The regression line passes through the "middle" of the point cloud and minimises squared vertical distances — but at 3-point level you only **use** the given equation.

**Predicted value:** $\\hat{y} = a + bx$ is the value on the line at a given $x$. Always distinguish $\\hat{y}$ (model prediction) from the actual observed $y$."""

DEF_HE = """**קו רגרסיה (קו מגמה):**
$$y=a+bx$$
כאשר:
- $x$ — **משתנה בלתי-תלוי** (מסביר, גורם, מנבא).
- $y$ — **משתנה תלוי** (תגובה, תוצאה, השפעה).
- $b$ — **שיפוע** — שינוי ב-$y$ החזוי לכל עלייה של יחידה אחת ב-$x$.
- $a$ — **נקודת חיתוך עם ציר $y$** — ערך $y$ החזוי כאשר $x=0$.

**פרשנות השיפוע $b$:**
- $b>0$: **קשר חיובי (ישיר)** — ככל ש-$x$ גדל, $y$ החזוי גדל.
- $b<0$: **קשר שלילי (הפוך)** — ככל ש-$x$ גדל, $y$ החזוי קטן.
- $b=0$: **אין קשר לינארי** — $y$ החזוי קבוע לכל $x$.
- $|b|$ מודד את **קצב השינוי** ביחידות הבעיה.

**גרף פיזור:** גרף של זוגות נתונים $(x_i,y_i)$. קו הרגרסיה עובר ב"אמצע" ענן הנקודות וממזער מרחקים אנכיים בריבוע — אך ברמת 3 יחידות רק **משתמשים** במשוואה הנתונה.

**ערך חזוי:** $\\hat{y}=a+bx$ הוא הערך על הקו ב-$x$ נתון. הבדילו תמיד בין $\\hat{y}$ (חיזוי המודל) לבין $y$ הנצפה בפועל."""

THEORY_EN = """**Predicting $y$ from $x$:** Substitute the given $x$ into $y = a + bx$ to obtain the predicted value $\\hat{y}$. Example: if $y = 40 + 5x$ and $x = 8$, then $\\hat{y} = 40 + 40 = 80$.

**Working backwards — finding $x$ from $y$:** When the predicted (or desired) $y$ is known, treat the equation as a linear equation in $x$. Example: $70 = 20 + 2.5x \\Rightarrow 2.5x = 50 \\Rightarrow x = 20$.

**Interpolation vs. extrapolation:**
- **Interpolation:** predicting within the range of observed $x$ values (between the smallest and largest $x$ in the data). Generally **reliable** because the line was fitted to that region.
- **Extrapolation:** predicting beyond the observed range. **Less reliable** — the linear pattern may not continue, and the intercept interpretation at $x = 0$ may be meaningless if zero lies outside the data.

**Residual:** $\\text{residual} = y_{\\text{actual}} - \\hat{y}_{\\text{predicted}}$.
- Positive residual: the point lies **above** the line (actual exceeds prediction).
- Negative residual: the point lies **below** the line.
- Zero residual: the point lies **on** the line.

**Using the slope directly:** If two $x$-values differ by $\\Delta x$, their predicted $y$-values differ by $\\Delta y = b \\cdot \\Delta x$. This shortcut avoids two full substitutions when only the difference matters.

**At the 3-point Bagrut level:** You are **not** required to compute $a$ and $b$ from data by hand. The equation is always provided. Focus on interpretation, prediction, residuals, and stating units clearly."""

THEORY_HE = """**חיזוי $y$ מ-$x$:** הציבו את $x$ הנתון ב-$y=a+bx$ כדי לקבל $\\hat{y}$ חזוי. דוגמה: אם $y=40+5x$ ו-$x=8$, אז $\\hat{y}=40+40=80$.

**עבודה הפוכה — מציאת $x$ מ-$y$:** כש-$y$ החזוי (או הרצוי) ידוע, התייחסו למשוואה כמשוואה לינארית ב-$x$. דוגמה: $70=20+2.5x \\Rightarrow 2.5x=50 \\Rightarrow x=20$.

**אינטרפולציה לעומת אקסטרפולציה:**
- **אינטרפולציה:** חיזוי בתוך טווח ערכי $x$ שנצפו (בין המינימום למקסימום בנתונים). בדרך כלל **אמין** כי הקו הותאם לאזור זה.
- **אקסטרפולציה:** חיזוי מחוץ לטווח הנצפה. **פחות אמין** — הדפוס הלינארי עשוי לא להמשיך, ופרשנות נקודת החיתוך ב-$x=0$ עלולה להיות חסרת משמעות אם אפס מחוץ לנתונים.

**שארית:** $\\text{שארית}=y_{\\text{בפועל}}-\\hat{y}_{\\text{חזוי}}$.
- שארית חיובית: הנקודה **מעל** הקו (בפועל גבוה מהחיזוי).
- שארית שלילית: הנקודה **מתחת** לקו.
- שארית אפס: הנקודה **על** הקו.

**שימוש ישיר בשיפוע:** אם שני ערכי $x$ שונים ב-$\\Delta x$, ערכי $y$ החזויים שונים ב-$\\Delta y=b\\cdot\\Delta x$. קיצור דרך זה חוסך שתי הצבות מלאות כשחשוב רק ההפרש.

**ברמת בגרות 3 יחידות:** **אינכם** נדרשים לחשב $a$ ו-$b$ מנתונים ביד. המשוואה תמיד ניתנת. התמקדו בפרשנות, חיזוי, שאריות, וציון יחידות בבירור."""

WE1_EN = """A regression line for hours studied ($x$) and test score ($y$) is:
$$y = 40 + 5x.$$

This is a classic Bagrut setup: $x$ is the predictor (study time in hours), $y$ is the outcome (test score in points), slope $b = 5$ means each extra hour adds 5 points, and intercept $a = 40$ is the baseline score with zero study hours.

**(a) Predict the score for a student who studies 8 hours.**

### Move 1: Substitute $x = 8$
$$y = 40 + 5(8) = 40 + 40 = 80.$$

**Answer:** Predicted score = **80 points**.

**(b) Interpret the slope and intercept in context.**

**Slope $b = 5$:** For each additional hour of study, the predicted test score increases by **5 points**. This is a direct (positive) relationship.

**Intercept $a = 40$:** A student who studies **0 hours** is predicted to score **40 points** — representing baseline knowledge before additional study. **Exam note:** always include units ("points per hour", "points at zero hours") — bare numbers lose interpretation marks on the Bagrut."""

WE1_HE = """קו רגרסיה לשעות לימוד ($x$) וציון מבחן ($y$):
$$y=40+5x.$$

זהו תרחיש בגרות קלאסי: $x$ הוא המנבא (זמן לימוד בשעות), $y$ הוא התוצאה (ציון מבחן בנקודות), שיפוע $b=5$ פירושו שכל שעה נוספת מוסיפה 5 נקודות, ונקודת חיתוך $a=40$ היא ציון הבסיס עם 0 שעות לימוד. שימו לב: $x$ בלתי-תלוי ו-$y$ תלוי — אל תחליפו ביניהם.

**(א) חזה ציון לתלמיד שלומד 8 שעות.**

### צעד 1: הצב $x=8$
$$y=40+5(8)=40+40=80.$$

**תשובה:** ציון חזוי = **80 נקודות**.

**(ב) פרש שיפוע ונקודת חיתוך בהקשר.**

**שיפוע $b=5$:** לכל שעת לימוד נוספת, הציון החזוי עולה ב-**5 נקודות**. זהו קשר ישיר (חיובי).

**נקודת חיתוך $a=40$:** תלמיד שלומד **0 שעות** — ציון חזוי **40 נקודות**, המייצג ידע בסיסי לפני לימוד נוסף. **הערת בחינה:** תמיד כללו יחידות ("נקודות לשעה", "נקודות ב-0 שעות") — מספרים בלבד מאבדים ניקוד פרשנות בבגרות."""

WE2_EN = """The regression line for age ($x$, in years) and salary ($y$, in thousands of shekels) is:
$$y = 20 + 2.5x.$$

Here salary depends on age: $x$ is independent, $y$ is dependent. The slope 2.5 means each additional year of age is associated with 2.5 thousand shekels higher predicted salary. This is a direct (positive) relationship typical of career progression models.

**(a) A person has a predicted salary of 70 (thousand). How old are they?**

### Move 1: Set up the equation
$$70 = 20 + 2.5x.$$

### Move 2: Isolate $x$
$$2.5x = 50 \\Rightarrow x = 20 \\text{ years old}.$$

**Sanity check:** $20 + 2.5(20) = 20 + 50 = 70$ ✓ — substitute back to confirm.

**(b) Two employees are 30 and 32 years old. What is the difference in their predicted salaries?**

Using the slope shortcut: $\\Delta y = b \\cdot \\Delta x = 2.5 \\times (32 - 30) = 2.5 \\times 2 = 5$ thousand shekels.

This avoids computing both salaries separately: $y_{30} = 95$ and $y_{32} = 100$, difference $= 5$. **Exam tip:** when only a difference is asked, multiply slope by $\\Delta x$ directly — faster and less error-prone."""

WE2_HE = """קו רגרסיה לגיל ($x$, בשנים) ומשכורת ($y$, באלפי ש\"ח):
$$y=20+2.5x.$$

כאן משכורת תלויה בגיל: $x$ בלתי-תלוי, $y$ תלוי. שיפוע 2.5 פירושו שכל שנה נוספת בגיל קשורה לעלייה חזויה של 2.5 אלף ש\"ח במשכורת. זהו קשר ישיר (חיובי) אופייני למודלים של התקדמות בקריירה.

**(א) למישהו משכורת חזויה 70 (אלף). מה גילו?**

### צעד 1: הצב במשוואה
$$70=20+2.5x.$$

### צעד 2: בודד $x$
$$2.5x=50 \\Rightarrow x=20 \\text{ שנים}.$$

**בדיקת הגיון:** $20+2.5(20)=70$ ✓ — הציבו חזרה לאימות.

**(ב) שני עובדים בגיל 30 ו-32. מה ההבדל במשכורות החזויות?**

בקיצור השיפוע: $\\Delta y=b\\cdot\\Delta x=2.5\\times(32-30)=2.5\\times2=5$ אלף ש\"ח.

זה חוסך חישוב שני משכורות בנפרד: $y_{30}=95$ ו-$y_{32}=100$, הפרש $=5$. **טיפ לבחינה:** כששואלים רק על הפרש, הכפילו שיפוע ב-$\\Delta x$ ישירות — מהיר יותר ופחות מועד לטעות."""

WE3_EN = """The following table shows advertising spending ($x$, thousands of shekels) and sales revenue ($y$, thousands of shekels) for 5 months:

| Month | $x$ | $y$ |
|---|---|---|
| 1 | 1 | 22 |
| 2 | 2 | 27 |
| 3 | 3 | 31 |
| 4 | 4 | 36 |
| 5 | 5 | 39 |

The regression line is given as $y = 17 + 4.4x$.

**(a) Which is the independent variable? Why?**

Advertising spending ($x$) is **independent** — it is the input we control or use to predict sales. Sales ($y$) is the **dependent** outcome. Spending causes (or at least predicts) revenue, not the reverse.

**(b) Predict sales for $x = 6$ (6 thousand in advertising).**
$$y = 17 + 4.4(6) = 17 + 26.4 = 43.4 \\text{ thousand shekels}.$$
Note: $x = 6$ is **extrapolation** (data only goes to $x = 5$) — state this caveat if asked about reliability.

**(c) Actual sales in month 3 were 31. What is the residual?**
$$\\hat{y} = 17 + 4.4(3) = 17 + 13.2 = 30.2.$$
$$\\text{Residual} = 31 - 30.2 = +0.8.$$
The actual value is **0.8 thousand above** the line — a positive residual."""

WE3_HE = """הטבלה הבאה מציגה הוצאות פרסום ($x$, אלפי ש\"ח) והכנסות מכירות ($y$, אלפי ש\"ח) לחמישה חודשים:

| חודש | $x$ | $y$ |
|---|---|---|
| 1 | 1 | 22 |
| 2 | 2 | 27 |
| 3 | 3 | 31 |
| 4 | 4 | 36 |
| 5 | 5 | 39 |

קו הרגרסיה: $y=17+4.4x$.

**(א) מי המשתנה הבלתי-תלוי? מדוע?**

הוצאות פרסום ($x$) **בלתי-תלויות** — זה הקלט שאנו שולטים בו או משתמשים בו לחיזוי מכירות. מכירות ($y$) הן **תוצאה תלויה**. ההוצאה גורמת (או לפחות מנבאת) הכנסות, לא להפך.

**(ב) חזה מכירות ל-$x=6$ (6 אלף פרסום):**
$$y=17+4.4(6)=43.4 \\text{ אלף ש\"ח}.$$
שימו לב: $x=6$ הוא **אקסטרפולציה** (הנתונים מגיעים רק עד $x=5$) — ציינו מגבלה זו אם שואלים על אמינות.

**(ג) מכירות בפועל בחודש 3 היו 31. מהי השארית?**
$$\\hat{y}=17+4.4(3)=30.2.$$
$$\\text{שארית}=31-30.2=+0.8.$$
הערך בפועל **0.8 אלף מעל** הקו — שארית חיובית."""

CKPT1_EN = """The regression line for temperature ($x$, in °C) and ice cream sales ($y$, in units) is $y = -10 + 3x$.

**Step 1 — Predict sales at 30°C:**
$$y = -10 + 3(30) = -10 + 90 = 80 \\text{ units}.$$

**Step 2 — Interpret the slope $b = 3$:**
For each **1°C increase** in temperature, predicted ice cream sales rise by **3 units**. The relationship is positive (direct): warmer weather → more sales.

**Step 3 — Interpret the intercept $a = -10$:**
At $0°C$, predicted sales are $-10$ units — not physically meaningful here (you cannot sell negative ice cream). This shows why extrapolation and intercept interpretation require **contextual judgment**.

**Step 4 — Sanity check:** At 10°C: $y = -10 + 30 = 20$ units. At 20°C: $y = 50$ units. The 10-degree rise adds $3 \\times 10 = 30$ units, consistent with the slope."""

CKPT1_HE = """קו רגרסיה לטמפרטורה ($x$, מעלות) ומכירות גלידה ($y$, יחידות): $y=-10+3x$.

**שלב 1 — חיזוי מכירות ב-30°:**
$$y=-10+3(30)=80 \\text{ יחידות}.$$

**שלב 2 — פרשנות השיפוע $b=3$:**
לכל **עלייה של 1°** בטמפרטורה, מכירות הגלידה החזויות עולות ב-**3 יחידות**. הקשר חיובי (ישיר): מזג אוויר חם → יותר מכירות.

**שלב 3 — פרשנות נקודת החיתוך $a=-10$:**
ב-0°, מכירות חזויות $-10$ יחידות — לא משמעותי פיזית (לא ניתן למכור גלידה שלילית). זה מראה למה אקסטרפולציה ופרשנות חיתוך דורשות **שיקול דעת בהקשר**.

**שלב 4 — בדיקת הגיון:** ב-10°: $y=20$ יחידות. ב-20°: $y=50$. עלייה של 10 מעלות מוסיפה $3\\times10=30$ יחידות, עקבי עם השיפוע."""

CKPT2_EN = """Line: $y = 100 - 4x$ (time studying $x$ hours and stress level $y$). Find the study time when stress is predicted to be 60.

**Step 1 — Set up the equation:**
$$60 = 100 - 4x.$$

**Step 2 — Isolate $x$:**
$$4x = 100 - 60 = 40 \\Rightarrow x = 10 \\text{ hours}.$$

**Step 3 — Verify by substitution:**
$$y = 100 - 4(10) = 100 - 40 = 60$$ ✓

**Step 4 — Interpret the slope $b = -4$:**
Each additional hour of study is associated with a **decrease of 4 units** in predicted stress — an inverse relationship. More study → less stress (according to this model).

**Exam note:** When solving for $x$, watch the sign carefully. A common error is writing $60 = 100 + 4x$ instead of $100 - 4x$."""

CKPT2_HE = """קו: $y=100-4x$ (שעות לימוד $x$ ורמת לחץ $y$). מצאו את זמן הלימוד שבו רמת הלחץ החזויה היא 60.

**שלב 1 — הצב במשוואה:**
$$60=100-4x.$$

**שלב 2 — בודד $x$:**
$$4x=100-60=40 \\Rightarrow x=10 \\text{ שעות}.$$

**שלב 3 — אימות בהצבה:**
$$y=100-4(10)=60$$ ✓

**שלב 4 — פרשנות השיפוע $b=-4$:**
כל שעת לימוד נוספת קשורה ל**ירידה של 4 יחידות** ברמת הלחץ החזויה — קשר הפוך. יותר לימוד → פחות לחץ (לפי המודל).

**הערת בחינה:** בפתרון ל-$x$, שימו לב לסימן. טעות נפוצה: כתיבת $60=100+4x$ במקום $100-4x$."""

METHOD_EN = """**Types of Bagrut regression questions and how to answer:**

| Question type | Method |
|---|---|
| Predict $\\hat{y}$ for given $x$ | Substitute $x$ into $y = a + bx$ |
| Find $x$ for given $y$ | Solve $y = a + bx$ for $x$ |
| Interpret slope | "For each 1-unit increase in $x$, predicted $y$ changes by $b$ units" + context |
| Interpret intercept | "When $x = 0$, predicted $y = a$" + context |
| Find residual | $\\hat{y} = a + bx$, then residual $= y_{\\text{actual}} - \\hat{y}$ |
| Positive/negative relationship | Sign of $b$: $b > 0$ direct, $b < 0$ inverse |
| Difference in predictions | $\\Delta y = b \\cdot \\Delta x$ (slope shortcut) |
| Reliability of prediction | Interpolation (inside data range) vs. extrapolation (outside) |

**5-step exam procedure:**
1. Identify $x$ (independent) and $y$ (dependent) from the context.
2. Write the given equation $y = a + bx$.
3. Perform the calculation (substitute, solve, or compute residual).
4. Interpret slope/intercept **with units and context**.
5. State whether the prediction is interpolation or extrapolation if relevant.

**Exam tip:** Always write the units! "The slope means that for each additional year, salary increases by 2.5 *thousand shekels*." Bare numbers lose marks."""

METHOD_HE = """**סוגי שאלות רגרסיה בבגרות וכיצד לענות:**

| סוג שאלה | שיטה |
|---|---|
| חזה $\\hat{y}$ עבור $x$ נתון | הצב $x$ ב-$y=a+bx$ |
| מצא $x$ עבור $y$ נתון | פתור $y=a+bx$ עבור $x$ |
| פרש שיפוע | "לכל עלייה של יחידה ב-$x$, $y$ החזוי משתנה ב-$b$ יחידות" + הקשר |
| פרש נקודת חיתוך | "כאשר $x=0$, $y$ החזוי הוא $a$" + הקשר |
| מצא שארית | $\\hat{y}=a+bx$, ואז שארית $=y_{\\text{בפועל}}-\\hat{y}$ |
| קשר חיובי/שלילי | סימן $b$: $b>0$ ישיר, $b<0$ הפוך |
| הפרש בין חיזויים | $\\Delta y=b\\cdot\\Delta x$ (קיצור שיפוע) |
| אמינות חיזוי | אינטרפולציה (בתוך טווח) לעומת אקסטרפולציה (מחוץ) |

**5 שלבי בחינה:**
1. זהו $x$ (בלתי-תלוי) ו-$y$ (תלוי) מההקשר.
2. כתבו את המשוואה הנתונה $y=a+bx$.
3. בצעו את החישוב (הצבה, פתרון, או שארית).
4. פרשו שיפוע/חיתוך **עם יחידות והקשר**.
5. ציינו אם החיזוי הוא אינטרפולציה או אקסטרפולציה אם רלוונטי.

**טיפ לבחינה:** תמיד כתבו יחידות! "השיפוע מציין שלכל שנה נוספת, המשכורת עולה ב-2.5 *אלף ש\"ח*." מספרים בלבד מאבדים ניקוד."""

PITFALL_EN = """1. **Confusing independent and dependent variables.** $x$ is the predictor (cause), $y$ is the outcome (effect). Swapping them gives a different line and wrong interpretation. Always ask: "Which variable are we using to predict the other?"

2. **Not interpreting in context.** "The slope is 5" is incomplete and loses marks. Write: "For each additional hour of study, the predicted score increases by 5 points." Include **units** every time.

3. **Extrapolating without caution.** Predicting far outside the data range may be unreliable. If $x = 50$ but data only covers $x = 1$ to $10$, state that this is extrapolation and the linear pattern may not hold.

4. **Ignoring the sign of the slope.** A negative slope means an inverse relationship — as $x$ increases, predicted $y$ decreases. Students often report the magnitude but forget the direction.

5. **Computing residual in the wrong order.** Residual $= y_{\\text{actual}} - \\hat{y}$, NOT $\\hat{y} - y_{\\text{actual}}$. Reversing the subtraction flips the sign and misidentifies above/below the line.

6. **Thinking the regression line passes through every data point.** It passes through the centroid $(\\bar{x}, \\bar{y})$ and minimises squared residuals — most points lie off the line with nonzero residuals."""

PITFALL_HE = """1. **בלבול משתנים תלוי ובלתי-תלוי.** $x$ הוא המנבא (גורם), $y$ הוא התוצאה (השפעה). החלפתם נותנת קו שונה ופרשנות שגויה. שאלו תמיד: "באיזה משתנה משתמשים כדי לחזות את השני?"

2. **פרשנות ללא הקשר.** "השיפוע הוא 5" חלקי ומאבד ניקוד. כתבו: "לכל שעת לימוד נוספת, הציון החזוי עולה ב-5 נקודות." כללו **יחידות** בכל פעם.

3. **אקסטרפולציה ללא זהירות.** חיזוי רחוק מתחום הנתונים עלול להיות לא אמין. אם $x=50$ אך הנתונים מכסים $x=1$ עד $10$, ציינו שזו אקסטרפולציה והדפוס הלינארי עשוי לא להתקיים.

4. **התעלמות מסימן השיפוע.** שיפוע שלילי = קשר הפוך — ככל ש-$x$ גדל, $y$ החזוי קטן. תלמידים לעיתים מדווחים את הגודל אך שוכחים את הכיוון.

5. **חישוב שארית בסדר הפוך.** שארית $=y_{\\text{בפועל}}-\\hat{y}$, לא $\\hat{y}-y_{\\text{בפועל}}$. היפוך החיסור מחליף סימן ומזהה שגוי מעל/מתחת לקו.

6. **חשיבה שקו הרגרסיה עובר דרך כל נקודה.** הוא עובר דרך $(\\bar{x},\\bar{y})$ וממזער ריבועי שאריות — רוב הנקודות לא על הקו עם שאריות לא-אפס."""

WHY_EN = """Linear regression is the bridge between **algebra** (linear functions, slope, intercept) and **real-world data analysis**. Every field — economics, medicine, sports analytics, marketing — uses trend lines to summarise relationships and make forecasts.

On the Bagrut 3-unit exam, regression questions test whether you can translate a formula into **meaningful language**: not just "plug in and compute" but "explain what the slope tells us about salary and age." This skill of contextual interpretation carries forward to 4- and 5-unit statistics, university econometrics, and data science.

Within A Step Forward, mastery here unlocks `concept:linear_regression_correlation` (deeper statistical inference) and supports word problems across physics and social-science contexts where variables co-vary."""

WHY_HE = """רגרסיה לינארית היא הגשר בין **אלגברה** (פונקציות לינאריות, שיפוע, חיתוך) ל**ניתוח נתונים מהעולם האמיתי**. כל תחום — כלכלה, רפואה, אנליטיקת ספורט, שיווק — משתמש בקווי מגמה לסיכום קשרים וחיזוי.

בבגרות 3 יחידות, שאלות רגרסיה בודקות אם אתם יכולים לתרגם נוסחה ל**שפה משמעותית**: לא רק "הצב וחשב" אלא "הסבר מה השיפוע אומר על משכורת וגיל." מיומנות פרשנות בהקשר זו ממשיכה ל-4 ו-5 יחידות, אקונומטריקה אוניברסיטאית, ומדע נתונים.

ב-A Step Forward, שליטה כאן פותחת את `concept:linear_regression_correlation` (הסקה סטטיסטית עמוקה יותר) ותומכת בבעיות מילוליות בפיזיקה ובמדעי החברה שבהן משתנים משתנים יחד."""

BEFORE_EN = """**Formula card:**
- $y = a + bx$ (regression line)
- $b$ = slope (change in predicted $y$ per 1 unit of $x$)
- $a$ = y-intercept (predicted $y$ when $x = 0$)
- $\\hat{y} = a + bx$ (predicted value)
- Residual $= y_{\\text{actual}} - \\hat{y}$
- $\\Delta y = b \\cdot \\Delta x$ (slope shortcut for differences)

**Bagrut 3-unit exam patterns:**
- Given the line, predict $\\hat{y}$ for a specific $x$.
- Find $x$ given a desired predicted $y$.
- Interpret slope and intercept **in the problem context with units**.
- Compute residuals for specific data points.
- Decide whether a prediction is interpolation or extrapolation.
- Identify independent vs. dependent variable from a word problem.

**Last-minute checklist:**
- Did I state units in my interpretation?
- Did I use actual minus predicted for residuals?
- Did I check the sign of the slope?
- Is my prediction inside or outside the data range?

**Tip:** Read the question carefully — is it asking for $x$ or $y$? Always show substitution steps for partial credit."""

BEFORE_HE = """**גיליון נוסחאות:**
- $y=a+bx$ (קו רגרסיה)
- $b$ = שיפוע (שינוי ב-$y$ החזוי לכל יחידת $x$)
- $a$ = נקודת חיתוך ( $y$ חזוי כאשר $x=0$)
- $\\hat{y}=a+bx$ (ערך חזוי)
- שארית $=y_{\\text{בפועל}}-\\hat{y}$
- $\\Delta y=b\\cdot\\Delta x$ (קיצור שיפוע להפרשים)

**דגמי בגרות 3 יחידות:**
- נתון הקו, חזה $\\hat{y}$ עבור $x$ ספציפי.
- מצא $x$ עבור $y$ חזוי רצוי.
- פרש שיפוע וחיתוך **בהקשר הבעיה עם יחידות**.
- חשב שאריות לנקודות נתונים.
- החלט אם חיזוי הוא אינטרפולציה או אקסטרפולציה.
- זהה משתנה בלתי-תלוי מול תלוי מבעיה מילולית.

**רשימת בדיקה אחרונה:**
- האם ציינתי יחידות בפרשנות?
- האם השתמשתי בפועל פחות חזוי לשארית?
- האם בדקתי את סימן השיפוע?
- האם החיזוי בתוך או מחוץ לטווח הנתונים?

**טיפ:** קרא בעיון — האם שואלים $x$ או $y$? הצג שלבי הצבה לניקוד חלקי."""

SUMMARY_EN = """- **Regression line:** $y = a + bx$; $x$ independent (predictor), $y$ dependent (outcome).
- **Slope $b$:** change in predicted $y$ per 1-unit increase in $x$; $b > 0$ = direct, $b < 0$ = inverse, $b = 0$ = no linear trend.
- **Intercept $a$:** predicted $y$ when $x = 0$ — interpret only if zero is meaningful in context.
- **Predict:** substitute $x$ to get $\\hat{y}$; solve for $x$ when $y$ is given.
- **Residual:** $y_{\\text{actual}} - \\hat{y}$; positive = above line, negative = below.
- **Slope shortcut:** $\\Delta y = b \\cdot \\Delta x$ for differences without double substitution.
- **Caution:** extrapolation beyond data range is unreliable; always state units in interpretation."""

SUMMARY_HE = """- **קו רגרסיה:** $y=a+bx$; $x$ בלתי-תלוי (מנבא), $y$ תלוי (תוצאה).
- **שיפוע $b$:** שינוי ב-$y$ החזוי לכל עלייה של 1 ב-$x$; $b>0$ = ישיר, $b<0$ = הפוך, $b=0$ = אין מגמה לינארית.
- **נקודת חיתוך $a$:** $y$ חזוי כאשר $x=0$ — פרשו רק אם אפס משמעותי בהקשר.
- **חיזוי:** הצב $x$ לקבלת $\\hat{y}$; פתרו ל-$x$ כש-$y$ ידוע.
- **שארית:** $y_{\\text{בפועל}}-\\hat{y}$; חיובית = מעל הקו, שלילית = מתחת.
- **קיצור שיפוע:** $\\Delta y=b\\cdot\\Delta x$ להפרשים בלי שתי הצבות.
- **זהירות:** אקסטרפולציה מחוץ לטווח הנתונים לא אמינה; תמיד ציינו יחידות בפרשנות."""

Q_EXPL = [
    fmt_expl(
        "Substituting $x = 4$ into $y = 5 + 3x$ gives $y = 5 + 3(4) = 5 + 12 = 17$. The slope 3 means each unit increase in $x$ adds 3 to $y$, and the intercept 5 is the baseline when $x = 0$.",
        "Identify the given equation $y = a + bx$ with $a = 5$ and $b = 3$. The question asks for $\\hat{y}$ at a specific $x$, so direct substitution is the correct method. Write out $5 + 3(4)$ before simplifying to avoid arithmetic slips.",
        "Multiplying before adding: some students compute $5 + 3 \\times 4$ as $(5+3) \\times 4 = 32$. Order of operations requires $3 \\times 4 = 12$ first, then $5 + 12 = 17$.",
        "Show the substitution line $y = 5 + 3(4)$ even for easy questions — Bagrut graders award partial credit for correct setup even if the final arithmetic has a minor error.",
        "הצבת $x=4$ ב-$y=5+3x$ נותנת $y=5+3(4)=5+12=17$. שיפוע 3 פירושו שכל עלייה של יחידה ב-$x$ מוסיפה 3 ל-$y$, ונקודת חיתוך 5 היא בסיס כש-$x=0$.",
        "זהו את המשוואה $y=a+bx$ עם $a=5$ ו-$b=3$. השאלה מבקשת $\\hat{y}$ ב-$x$ נתון, ולכן הצבה ישירה היא השיטה הנכונה. כתבו $5+3(4)$ לפני פישוט כדי להימנע מטעויות חשבון.",
        "כפל לפני חיבור: חלק מהתלמידים מחשבים $5+3\\times4$ כ-$(5+3)\\times4=32$. סדר פעולות דורש $3\\times4=12$ קודם, ואז $5+12=17$.",
        "הציגו את שורת ההצבה $y=5+3(4)$ גם בשאלות קלות — בודקי בגרות נותנים ניקוד חלקי על הכנה נכונה גם אם החשבון הסופי שגוי במעט.",
    ),
    fmt_expl(
        "The slope $b = -2$ in $y = 80 - 2x$ means that for every 1-unit increase in $x$, the predicted $y$ decreases by 2 units. The negative sign indicates an inverse (negative) relationship: as $x$ goes up, $y$ goes down.",
        "Slope interpretation always follows the template: 'For each 1-unit increase in $x$, predicted $y$ changes by $b$ units.' Here $b = -2$, so the change is a decrease. Identify what $x$ and $y$ represent in the problem context and include those units.",
        "Reporting only 'the slope is $-2$' without explaining direction loses marks. Another slip: saying '$y$ increases by 2' while ignoring the negative sign — the relationship is decreasing, not increasing.",
        "Always write a full sentence: 'For each additional [unit of $x$], predicted [unit of $y$] decreases by 2 [units].' This sentence template works for every slope interpretation question on the Bagrut.",
        "שיפוע $b=-2$ ב-$y=80-2x$ פירושו שלכל עלייה של יחידה ב-$x$, $y$ החזוי יורד ב-2 יחידות. הסימן השלילי מציין קשר הפוך (שלילי): ככל ש-$x$ עולה, $y$ יורד.",
        "פרשנות שיפוע תמיד עוקבת אחר התבנית: 'לכל עלייה של יחידה ב-$x$, $y$ החזוי משתנה ב-$b$ יחידות.' כאן $b=-2$, ולכן השינוי הוא ירידה. זהו מה $x$ ו-$y$ מייצגים בהקשר וכללו יחידות.",
        "דיווח רק 'השיפוע הוא $-2$' בלי הסבר כיוון מאבד ניקוד. טעות נוספת: אמר ' $y$ עולה ב-2' תוך התעלמות מהסימן השלילי — הקשר יורד, לא עולה.",
        "כתבו תמיד משפט מלא: 'לכל [יחידת $x$] נוספת, [יחידת $y$] החזוי יורד ב-2 [יחידות].' תבנית זו עובדת לכל שאלת פרשנות שיפוע בבגרות.",
    ),
    fmt_expl(
        "When $x = 0$, the equation $y = 12 + 0.5x$ gives $y = 12 + 0.5(0) = 12 + 0 = 12$. This value is the y-intercept $a = 12$ — the predicted $y$ when the independent variable is zero.",
        "Finding $y$ at $x = 0$ is the same as reading the intercept directly from the equation $y = a + bx$, since $a$ is defined as the value of $y$ when $x = 0$. You can either substitute or simply identify $a = 12$ from the standard form.",
        "Some students substitute $x = 0$ but forget that $0.5 \\times 0 = 0$, leaving $y = 12 + 0.5 = 12.5$. Any term multiplied by zero equals zero.",
        "When the question asks for $y$ at $x = 0$, you can answer immediately by reading $a$ from the equation — no calculation needed. State explicitly: 'This is the y-intercept.'",
        "כאשר $x=0$, המשוואה $y=12+0.5x$ נותנת $y=12+0.5(0)=12+0=12$. ערך זה הוא נקודת החיתוך $a=12$ — $y$ החזוי כשהמשתנה הבלתי-תלוי הוא אפס.",
        "מציאת $y$ ב-$x=0$ זהה לקריאת החיתוך ישירות מ-$y=a+bx$, כי $a$ מוגדר כערך $y$ כאשר $x=0$. אפשר להציב או פשוט לזהות $a=12$ מהצורה הסטנדרטית.",
        "חלק מהתלמידים מציבים $x=0$ אך שוכחים ש-$0.5\\times0=0$, ומשאירים $y=12+0.5=12.5$. כל איבר כפול באפס שווה לאפס.",
        "כשהשאלה מבקשת $y$ ב-$x=0$, אפשר לענות מיד על ידי קריאת $a$ מהמשוואה — בלי חישוב. ציינו במפורש: 'זוהי נקודת החיתוך עם ציר $y$.'",
    ),
    fmt_expl(
        "First compute the predicted value: $\\hat{y} = 30 + 4(5) = 30 + 20 = 50$. Then the residual is $y_{\\text{actual}} - \\hat{y} = 55 - 50 = 5$. A positive residual of 5 means the student's actual score is 5 points above what the model predicted.",
        "Residual questions require two steps: (1) substitute the given $x$ into the regression equation to find $\\hat{y}$, and (2) subtract predicted from actual. The student studied 5 hours ($x = 5$) and scored 55, but the line predicts only 50.",
        "The most common error is reversing the subtraction: computing $\\hat{y} - y_{\\text{actual}} = 50 - 55 = -5$. The correct formula is always actual minus predicted. Another slip: forgetting to compute $\\hat{y}$ first and subtracting 55 directly from 30.",
        "Write both steps clearly: '$\\hat{y} = 30 + 4(5) = 50$' then 'Residual $= 55 - 50 = 5$'. Label the residual as positive or negative and state whether the point is above or below the line.",
        "ראשית חשבו ערך חזוי: $\\hat{y}=30+4(5)=30+20=50$. אז השארית היא $y_{\\text{בפועל}}-\\hat{y}=55-50=5$. שארית חיובית 5 פירושה שהציון בפועל 5 נקודות מעל מה שהמודל חזה.",
        "שאלות שארית דורשות שני שלבים: (1) הציבו $x$ במשוואת הרגרסיה למציאת $\\hat{y}$, ו-(2) חסרו חזוי מבפועל. התלמיד למד 5 שעות ($x=5$) וקיבל 55, אך הקו חוזה רק 50.",
        "הטעות הנפוצה ביותר היא היפוך החיסור: $\\hat{y}-y_{\\text{בפועל}}=50-55=-5$. הנוסחה הנכונה תמיד בפועל פחות חזוי. טעות נוספת: שכחת חישוב $\\hat{y}$ וחיסור 55 ישירות מ-30.",
        "כתבו שני שלבים בבירור: '$\\hat{y}=30+4(5)=50$' ואז 'שארית $=55-50=5$'. סמנו את השארית כחיובית או שלילית וציינו אם הנקודה מעל או מתחת לקו.",
    ),
    fmt_expl(
        "Substituting $x = 70$ kg: $y = 150 + 12(70) = 150 + 840 = 990$. The slope $b = 12$ means each additional kilogram is associated with 12 units higher predicted blood pressure.",
        "Two-part question: plug $x = 70$ into $y = 150 + 12x$ for the prediction, then interpret slope 12 as linking weight (kg) to blood pressure — a direct positive relationship.",
        "Arithmetic error: $12 \\times 70 = 840$, not 720. Some students answer only 990 and skip slope interpretation, losing half the marks.",
        "Label answers (a) and (b). Include units: '990 units' and '12 units per kg'. Examiners look for contextual language, not bare numbers.",
        "הצבת $x=70$ ק\"ג: $y=150+12(70)=990$. שיפוע $b=12$ — כל ק\"ג נוסף קשור לעלייה חזויה של 12 יחידות בלחץ דם. נדרשים גם החיזוי וגם פרשנות השיפוע בהקשר.",
        "שאלה דו-חלקית: הציבו $x=70$ ב-$y=150+12x$ לחיזוי, ופרשו שיפוע 12 כקישור משקל (ק\"ג) ללחץ דם — קשר ישיר חיובי שבו משקל גבוה יותר קשור ללחץ דם חזוי גבוה יותר.",
        "טעות חשבון: $12\\times70=840$. חלק עונים רק 990 ומדלגים על פרשנות השיפוע, ומאבדים חצי מהניקוד.",
        "סמנו (א) ו-(ב). כללו יחידות: '990 יחידות לחץ דם' ו-'12 יחידות לק\"ג'. בודקים מחפשים שפה הקשרית.",
    ),
    fmt_expl(
        "Setting $y = 100$ and solving: $100 = 200 - 5x \\Rightarrow 5x = 200 - 100 = 100 \\Rightarrow x = 20$ years. Verification: $200 - 5(20) = 200 - 100 = 100$ ✓. The negative slope confirms that bone density decreases with age in this model.",
        "When the question gives a target $y$ and asks for $x$, rearrange $y = a + bx$ as a linear equation. Here $a = 200$, $b = -5$, so $100 = 200 - 5x$. Isolate $x$ by subtracting 200 from both sides, then dividing by $-5$ (or collecting positive $5x$ on one side).",
        "Sign errors are common: writing $100 = 200 + 5x$ instead of $200 - 5x$, or dividing $100 = 200 - 5x$ incorrectly to get $x = -20$. Always verify by substituting your answer back into the original equation.",
        "Show every algebraic step: '$100 = 200 - 5x \\Rightarrow 5x = 100 \\Rightarrow x = 20$'. Bagrut graders deduct marks for answers without working, even if the final number is correct.",
        "הצבת $y=100$ ופתרון: $100=200-5x \\Rightarrow 5x=200-100=100 \\Rightarrow x=20$ שנים. אימות: $200-5(20)=100$ ✓. השיפוע השלילי מאשר שצפיפות עצם יורדת עם הגיל במודל זה.",
        "כשהשאלה נותנת $y$ יעד ומבקשת $x$, סדרו מחדש $y=a+bx$ כמשוואה לינארית. כאן $a=200$, $b=-5$, ולכן $100=200-5x$. בודדו $x$ על ידי חיסור 200 משני האגפים, ואז חלוקה ב-$-5$ (או איסוף $5x$ חיובי בצד אחד).",
        "טעויות סימן נפוצות: כתיבת $100=200+5x$ במקום $200-5x$, או חלוקה שגויה לקבלת $x=-20$. תמיד אמתו על ידי הצבת התשובה חזרה במשוואה המקורית.",
        "הציגו כל שלב אלגברי: '$100=200-5x \\Rightarrow 5x=100 \\Rightarrow x=20$'. בודקי בגרות מורידים ניקוד על תשובות בלי דרך פתרון, גם אם המספר הסופי נכון.",
    ),
    fmt_expl(
        "At $x = 5$: $\\hat{y} = 10 + 3(5) = 25$, residual $= 25 - 25 = 0$ (on the line). At $x = 7$: $\\hat{y} = 10 + 3(7) = 31$, residual $= 30 - 31 = -1$ (below the line). The first observation lies exactly on the regression line; the second is 1 unit below it.",
        "For each point $(x, y)$, compute $\\hat{y} = 10 + 3x$ first, then subtract: residual $= y - \\hat{y}$. Compare residuals: positive means above the line, zero means on the line, negative means below. Here $(5, 25)$ gives residual 0 and $(7, 30)$ gives $-1$.",
        "Students sometimes compute $\\hat{y}$ for $x = 7$ as $10 + 3(7) = 21$ instead of 31 (adding error). Another slip: saying the point with residual $-1$ is 'above' the line — negative residual always means below.",
        "When comparing two residuals, compute each separately and label above/on/below. A residual of exactly 0 is rare but valid — it means the data point lies precisely on the fitted line.",
        "ב-$x=5$: $\\hat{y}=10+3(5)=25$, שארית $=25-25=0$ (על הקו). ב-$x=7$: $\\hat{y}=10+3(7)=31$, שארית $=30-31=-1$ (מתחת לקו). התצפית הראשונה בדיוק על קו הרגרסיה; השנייה יחידה אחת מתחתיו.",
        "לכל נקודה $(x,y)$, חשבו $\\hat{y}=10+3x$ קודם, ואז חסרו: שארית $=y-\\hat{y}$. השוו שאריות: חיובית = מעל הקו, אפס = על הקו, שלילית = מתחת. כאן $(5,25)$ נותן שארית 0 ו-$(7,30)$ נותן $-1$.",
        "תלמידים לעיתים מחשבים $\\hat{y}$ ל-$x=7$ כ-$10+3(7)=21$ במקום 31 (טעות חיבור). טעות נוספת: אמר שהנקודה עם שארית $-1$ 'מעל' הקו — שארית שלילית תמיד מתחת.",
        "בהשוואת שתי שאריות, חשבו כל אחת בנפרד וסמנו מעל/על/מתחת. שארית בדיוק 0 נדירה אך תקינה — פירושה שהנקודה בדיוק על הקו המותאם.",
    ),
    fmt_expl(
        "Slope $b = 0$ means the line is horizontal: $y = a$ regardless of $x$. The predictor $x$ has no linear effect — knowing $x$ does not improve prediction beyond the constant $a$. There is no linear relationship.",
        "Think 'flat line': predicted $y$ is the same for every $x$. Statistically, $x$ and $y$ are uncorrelated linearly; the best prediction is always the intercept $a$.",
        "Do not confuse zero slope with zero outcome — $y$ is constant, not necessarily zero. Also, a nonlinear relationship may still exist; we only conclude no linear trend.",
        "Mention three points: horizontal line, $x$ does not predict $y$ linearly, predicted value is always $a$. This earns full marks on Bagrut interpretation questions.",
        "שיפוע $b=0$ — הקו אופקי: $y=a$ לכל $x$. המנבא $x$ אין לו השפעה לינארית — ידיעת $x$ לא משפרת חיזוי מעבר לקבוע $a$. אין קשר לינארי.",
        "חשבו 'קו שטוח': $y$ החזוי זהה לכל $x$. סטטיסטית, $x$ ו-$y$ לא מתואמים לינארית; החיזוי הטוב ביותר הוא תמיד $a$.",
        "אל תבלבלו שיפוע אפס עם תוצאה אפס — $y$ קבוע, לא בהכרח אפס. ייתכן קשר לא-לינארי; מסיקים רק שאין מגמה לינארית.",
        "ציינו: קו אופקי, $x$ לא מנבא $y$ לינארית, הערך החזוי תמיד $a$. זה מקבל ניקוד מלא בבגרות.",
    ),
]

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Step 1:** Substitute $x = 4$ into $y = 5 + 3x$.\n\n**Step 2:** $y = 5 + 12 = 17$.\n\n**Check:** $5 + 3(4) = 5 + 12 = 17$ ✓",
        "solution_he": "**שלב 1:** הצב $x=4$ ב-$y=5+3x$.\n\n**שלב 2:** $y=5+12=17$.\n\n**בדיקה:** $5+3(4)=17$ ✓",
    },
    "e6": {
        "solution_en": "**Step 1:** Set $y = 100$: $100 = 200 - 5x$.\n\n**Step 2:** $5x = 100 \\Rightarrow x = 20$ years.\n\n**Check:** $200 - 5(20) = 100$ ✓",
        "solution_he": "**שלב 1:** הצב $y=100$: $100=200-5x$.\n\n**שלב 2:** $5x=100 \\Rightarrow x=20$ שנים.\n\n**בדיקה:** $200-5(20)=100$ ✓",
    },
    "e11": {
        "solution_en": "**Step 1:** $70 = 100 - 6x \\Rightarrow 6x = 30 \\Rightarrow x = 5$ weeks.\n\n**Step 2:** Data covers weeks 1–8, so $x = 5$ is **interpolation** — reliable.\n\n**Check:** $100 - 6(5) = 70$ ✓",
        "solution_he": "**שלב 1:** $70=100-6x \\Rightarrow x=5$ שבועות.\n\n**שלב 2:** הנתונים מכסים שבועות 1–8, ולכן $x=5$ הוא **אינטרפולציה** — אמין.\n\n**בדיקה:** $100-6(5)=70$ ✓",
    },
    "e13": {
        "solution_en": "**Step 1:** Slope $b = (23 - 14)/(5 - 2) = 9/3 = 3$.\n\n**Step 2:** Using $(2, 14)$: $14 = a + 6 \\Rightarrow a = 8$.\n\n**Line:** $y = 8 + 3x$. **Check:** $8 + 3(5) = 23$ ✓",
        "solution_he": "**שלב 1:** שיפוע $b=(23-14)/(5-2)=3$.\n\n**שלב 2:** מ-$(2,14)$: $14=a+6 \\Rightarrow a=8$.\n\n**קו:** $y=8+3x$. **בדיקה:** $8+3(5)=23$ ✓",
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
            "Regression line y = a + bx: substitute x to predict, solve for x when y is given.",
            "Residual = actual y minus predicted y-hat; positive means above the line.",
            "Always interpret slope and intercept with units and real-world context.",
        ],
        "key_insights_he": [
            "קו רגרסיה y=a+bx: הצב x לחיזוי, פתור ל-x כש-y ידוע.",
            "שארית = y בפועל פחות y חזוי; חיובית = מעל הקו.",
            "פרשו תמיד שיפוע וחיתוך עם יחידות והקשר מהחיים.",
        ],
        "common_misconceptions_en": [
            "Reversing residual subtraction (predicted minus actual instead of actual minus predicted).",
            "Reporting slope magnitude without direction or context.",
            "Treating extrapolation as equally reliable as interpolation.",
        ],
        "common_misconceptions_he": [
            "היפוך חיסור שארית (חזוי פחות בפועל במקום בפועל פחות חזוי).",
            "דיווח גודל שיפוע בלי כיוון או הקשר.",
            "התייחסות לאקסטרפולציה כאילו היא אמינה כמו אינטרפולציה.",
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
