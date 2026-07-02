#!/usr/bin/env python3
"""Expand basic_statistics_3pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/basic_statistics_3pt.json"

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


INTRO_EN = """Imagine a teacher who wants to understand how her 30 students performed on a test. Staring at 30 raw numbers is overwhelming — you cannot say in one sentence whether the class did well or poorly. Instead she asks two natural questions: **What is the typical score? How spread out are the results?**

**Descriptive statistics** answers with a small toolkit of numbers:
- The **mean** (average) — the arithmetic balance point of the data.
- The **median** — the middle value once data are sorted.
- The **mode** — the value that appears most often.
- The **range** — the gap between the largest and smallest values.

These four measures appear throughout the Israeli **Bagrut** at the 3-point level: reading tables, interpreting bar charts, comparing two classes, and finding a missing score when the mean is given. They also connect forward to variance, standard deviation, and probability in later units — but every advanced idea still starts with "sort the data and compute the mean"."""

INTRO_HE = """דמיינו מורה שרוצה להבין כיצד 30 תלמידיה ביצעו במבחן. להסתכל על 30 מספרים גולמיים מבלבל — אי אפשר לומר במשפט אחד האם הכיתה הצליחה או נכשלה. במקום זאת היא שואלת שתי שאלות טבעיות: **מה הציון הטיפוסי? עד כמה התוצאות פרוסות?**

**סטטיסטיקה תיאורית** עונה בארגז כלים קטן של מספרים:
- **ממוצע** — נקודת האיזון האריתמטית של הנתונים.
- **חציון** — הערך האמצעי לאחר מיון הנתונים.
- **שכיח** — הערך שמופיע הכי הרבה פעמים.
- **טווח** — הפער בין הערך הגדול ביותר לקטן ביותר.

ארבעת המדדים הללו מופיעים לאורך **בגרות** 3 יחידות: קריאת טבלאות, פירוש תרשימי עמודות, השוואת שתי כיתות, ומציאת ציון חסר כשניתן הממוצע. הם גם מקשרים קדימה לשונות, סטיית תקן והסתברות — אך כל רעיון מתקדם מתחיל ב"מיינו את הנתונים וחשבו ממוצע"."""

DEF_EN = """Let a data set be $x_1, x_2, \\ldots, x_n$ with $n$ observations.

**Mean (average):** $\\bar{x} = \\dfrac{x_1 + x_2 + \\cdots + x_n}{n} = \\dfrac{\\sum x_i}{n}$. Think of it as spreading the total equally across all values.

**Median:** Sort values in ascending order. If $n$ is **odd**, the median is the single middle value at position $(n+1)/2$. If $n$ is **even**, average the two middle values at positions $n/2$ and $n/2+1$.

**Mode:** The value (or values) appearing most frequently. A set may have **no mode** (all values unique), **one mode**, or be **bimodal/multimodal** (two or more values tie for highest frequency).

**Range:** $\\text{Range} = \\text{Maximum} - \\text{Minimum}$. It measures spread using only the two extreme values.

**Important distinction:** Mean and median require numerical data; mode can describe categories (e.g., favourite colour). Range is always in the same units as the data (points, shekels, centimetres)."""

DEF_HE = """יהיו הנתונים $x_1, x_2, \\ldots, x_n$ עם $n$ תצפיות.

**ממוצע:** $\\bar{x} = \\dfrac{x_1 + x_2 + \\cdots + x_n}{n} = \\dfrac{\\sum x_i}{n}$. חשבו עליו כחלוקת הסכום הכולל בצורה שווה בין כל הערכים.

**חציון:** מיינו בסדר עולה. אם $n$ **אי-זוגי**, החציון הוא הערך האמצעי היחיד במיקום $(n+1)/2$. אם $n$ **זוגי**, ממוצעים את שני הערכים האמצעיים במיקומים $n/2$ ו-$n/2+1$.

**שכיח:** הערך (או הערכים) שמופיעים בתדירות הגבוהה ביותר. לקבוצה ייתכן **אין שכיח** (כל הערכים ייחודיים), **שכיח אחד**, או **דו-שכיח/רב-שכיח** (שניים או יותר שווים בתדירות).

**טווח:** $\\text{טווח} = \\text{מקסימום} - \\text{מינימום}$. הוא מודד פיזור רק משני הקיצונים.

**הבחנה חשובה:** ממוצע וחציון דורשים נתונים מספריים; שכיח מתאים גם לקטגוריות (למשל צבע מועדף). הטווח תמיד באותן יחידות כמו הנתון (נקודות, שקלים, סנטימטרים)."""

THEORY_EN = """**Mean — when and why:** Use the mean when data are roughly symmetric and free of extreme outliers. It uses every value, so it behaves well in algebra — for example, reversing $\\bar{x}=\\text{Sum}/n$ to find a missing score. One very high or low value pulls the mean toward it.

**Median — robust centre:** The median depends only on order, not on the size of extreme values. Use it for **skewed** data (salaries, house prices, reaction times with occasional spikes). On Bagrut word problems, if someone asks "typical value" and an outlier is present, median is usually intended.

**Mode — frequency winner:** Mode identifies the most common category or score. It is the only measure here that applies to non-numerical labels. Watch for **ties**: two values with the same highest count create a bimodal set.

**Range — quick spread:** Range = max − min is easy but crude. A single outlier on either end changes the range dramatically while telling you nothing about the middle 90% of values.

**Exam strategy:** Sort first whenever median, mode, or range is needed — sorting once supports all three. For even $n$, write both middle values before averaging. Compare mean vs median on the same set to detect skew: mean $>$ median suggests right skew; mean $<$ median suggests left skew."""

THEORY_HE = """**ממוצע — מתי ולמה:** השתמשו בממוצע כשהנתונים סימטריים בערך וללא חריגים קיצוניים. הוא משתמש בכל ערך, ולכן מתנהג טוב באלגברה — למשל היפוך $\\bar{x}=\\text{סכום}/n$ למציאת ציון חסר. ערך גבוה או נמוך מאוד מושך את הממוצע אליו.

**חציון — מרכז עמיד:** החציון תלוי רק בסדר, לא בגודל הערכים הקיצוניים. השתמשו בו בנתונים **מוטים** (משכורות, מחירי דירות, זמני תגובה עם קפיצות). בבגרות, אם שואלים "ערך טיפוסי" ויש חריג — בדרך כלל הכוונה לחציון.

**שכיח — הזוכה בתדירות:** השכיח מזהה את הקטגוריה או הציון הנפוץ ביותר. הוא המדד היחיד כאן שמתאים גם לתוויות לא-מספריות. שימו לב ל**שוויון**: שני ערכים עם אותה תדירות מקסימלית יוצרים קבוצה דו-שכיחית.

**טווח — פיזור מהיר:** טווח = מקס − מין קל אך גס. חריג בודד בקצה משנה את הטווח דרמטית בלי לספר דבר על 90% האמצעיים.

**אסטרטגיית בחינה:** מיינו קודם בכל פעם שצריך חציון, שכיח או טווח — מיון אחד תומך בשלושתם. ב-$n$ זוגי, כתבו את שני האמצעיים לפני הממוצע. השוו ממוצע מול חציון באותה קבוצה לזיהוי הטיה: ממוצע $>$ חציון מרמז על הטיה ימינה; ממוצע $<$ חציון — שמאלה."""

WE1_EN = """**The test scores of 7 students:** 72, 85, 90, 68, 85, 92, 78.

Find the mean, median, mode, and range.

### Move 1: Sort the data.
Ascending order: 68, 72, 78, 85, 85, 90, 92. Sorting is mandatory before median and helpful for mode/range.

### Move 2: Compute the mean.
$$\\bar{x} = \\frac{68+72+78+85+85+90+92}{7} = \\frac{570}{7} \\approx 81.4$$

### Move 3: Locate the median.
$n=7$ (odd). Position $(7+1)/2=4$. The 4th sorted value is **85**.

### Move 4: Identify the mode.
Count frequencies: 85 appears twice; every other value once. **Mode = 85**.

### Move 5: Find the range.
Maximum 92, minimum 68. Range $= 92 - 68 = 24$.

**Summary:** Mean $\\approx 81.4$, Median $= 85$, Mode $= 85$, Range $= 24$. Median equals mode here — the middle score is also the most common.

**Exam habit:** Show the sorted list and state the median position before reading the value — graders award method marks."""

WE1_HE = """**ציוני מבחן של 7 תלמידים:** 72, 85, 90, 68, 85, 92, 78.

מצאו ממוצע, חציון, שכיח וטווח.

### צעד 1: מיון הנתונים.
סדר עולה: 68, 72, 78, 85, 85, 90, 92. מיון חובה לפני חציון ומועיל לשכיח/טווח.

### צעד 2: חישוב הממוצע.
$$\\bar{x} = \\frac{68+72+78+85+85+90+92}{7} = \\frac{570}{7} \\approx 81.4$$

### צעד 3: איתור החציון.
$n=7$ (אי-זוגי). מיקום $(7+1)/2=4$. הערך הרביעי הממוין הוא **85**.

### צעד 4: זיהוי השכיח.
ספירת תדירויות: 85 מופיע פעמיים; כל השאר פעם. **שכיח = 85**.

### צעד 5: מציאת הטווח.
מקסימום 92, מינימום 68. טווח $= 92 - 68 = 24$.

**סיכום:** ממוצע $\\approx 81.4$, חציון $= 85$, שכיח $= 85$, טווח $= 24$. החציון שווה לשכיח — הציון האמצעי הוא גם הנפוץ ביותר.

**הרגל לבחינה:** הציגו רשימה ממוינת וציינו מיקום חציון לפני קריאת הערך — נקודות שיטה."""

WE2_EN = """**Ages at a birthday party:** 8, 9, 9, 10, 10, 10, 11, 45.

The 45-year-old is a parent. Calculate the mean and median. Which better represents the typical child's age?

### Move 1: Confirm sorted order.
Already sorted: 8, 9, 9, 10, 10, 10, 11, 45.

### Move 2: Compute the mean.
$$\\bar{x} = \\frac{8+9+9+10+10+10+11+45}{8} = \\frac{112}{8} = 14$$

The mean is 14 — but **no child is 14**! The parent's age pulled the average upward.

### Move 3: Compute the median.
$n=8$ (even). Positions 4 and 5 hold values 10 and 10.
$$\\text{Median} = \\frac{10+10}{2} = 10$$

### Move 4: Interpret and choose.
The median (10) matches the cluster of children. The mean (14) is distorted by the outlier. **When outliers exist, report the median for "typical" value.**

**Bagrut pattern:** Questions often embed one extreme value — always compute both mean and median, then justify your choice in one sentence.

**Numerical check:** Here mean − median $= 14-10=4$ years — a large gap signals the outlier's influence. If the parent were removed, mean would drop to about 9.6, close to the median cluster."""

WE2_HE = """**גילאים במסיבת יום הולדת:** 8, 9, 9, 10, 10, 10, 11, 45.

אדם בן 45 הוא הורה. חשבו ממוצע וחציון. מה מייצג טוב יותר גיל ילד טיפוסי?

### צעד 1: וידוא סדר ממוין.
כבר ממוין: 8, 9, 9, 10, 10, 10, 11, 45.

### צעד 2: חישוב הממוצע.
$$\\bar{x} = \\frac{8+9+9+10+10+10+11+45}{8} = \\frac{112}{8} = 14$$

הממוצע הוא 14 — אבל **אף ילד לא בן 14**! גיל ההורה משך את הממוצע למעלה.

### צעד 3: חישוב החציון.
$n=8$ (זוגי). מיקומים 4 ו-5 מחזיקים 10 ו-10.
$$\\text{חציון} = \\frac{10+10}{2} = 10$$

### צעד 4: פרשנות ובחירה.
החציון (10) תואם את קבוצת הילדים. הממוצע (14) מעוות על ידי החריג. **כשיש חריגים, דווחו חציון ל"ערך טיפוסי".**

**דפוס בגרות:** שאלות מטמיעות לעיתים ערך קיצוני — חשבו תמיד ממוצע וחציון, ונמקו את הבחירה במשפט.

**בדיקה מספרית:** כאן ממוצע − חציון $= 4$ שנים — פער גדול מסמן השפעת חריג. בלי ההורה, הממוצע היה יורד לכ-9.6, קרוב לקבוצת הילדים."""

WE3_EN = """**In a data set of 8 values**, the mean is 20 and seven of the values are: 15, 18, 22, 24, 19, 17, 21. Find the 8th value.

### Move 1: Reverse the mean formula.
$$\\bar{x} = \\frac{\\text{Sum of all values}}{n} \\Rightarrow 20 = \\frac{\\text{Sum}}{8} \\Rightarrow \\text{Sum} = 160.$$

### Move 2: Sum the seven known values.
$$15+18+22+24+19+17+21 = 136.$$

### Move 3: Subtract to find the missing value.
$$x_8 = 160 - 136 = 24.$$

### Move 4: Verify.
$(136+24)/8 = 160/8 = 20$ ✓

**Conclusion:** The 8th value is **24**.

**Why this works:** Mean times count gives total mass; subtract known parts to isolate the unknown. This algebra appears frequently on Bagrut "find the missing score" items — write Total $=$ Mean $\\times n$ first.

**Alternative check:** If the missing value were too small, the mean would drop below 20; if too large, above 20. Since 24 fits among the other scores (15–24), it is plausible — always sanity-check against the data context."""

WE3_HE = """**בקבוצת נתונים של 8 ערכים**, הממוצע הוא 20 ושבעה מהערכים: 15, 18, 22, 24, 19, 17, 21. מצאו את הערך ה-8.

### צעד 1: היפוך נוסחת הממוצע.
$$\\bar{x} = \\frac{\\text{סכום כל הערכים}}{n} \\Rightarrow 20 = \\frac{\\text{סכום}}{8} \\Rightarrow \\text{סכום} = 160.$$

### צעד 2: סכום שבעת הערכים הידועים.
$$15+18+22+24+19+17+21 = 136.$$

### צעד 3: חיסור למציאת הערך החסר.
$$x_8 = 160 - 136 = 24.$$

### צעד 4: אימות.
$(136+24)/8 = 160/8 = 20$ ✓

**מסקנה:** הערך ה-8 הוא **24**.

**למה זה עובד:** ממוצע כפול מספר נותן סכום כולל; חסרו חלקים ידועים לבידוד הלא ידוע. האלגברה הזו חוזרת בבגרות ב"מצא ציון חסר" — כתבו תחילה סכום $=$ ממוצע $\\times n$.

**בדיקת הגיון:** אם הערך החסר היה קטן מדי, הממוצע היה יורד מ-20; אם גדול מדי — עולה. מאחר ש-24 מתאים לטווח 15–24, התשובה סבירה — תמיד בדקו מול הקשר הנתונים."""

CP1_EN = """**Step 1 — Sort (already sorted).** Data: 3, 7, 7, 9, 12, 15. Count $n=6$.

**Step 2 — Mean.** Sum $= 3+7+7+9+12+15 = 53$. Mean $= 53/6 \\approx 8.83$.

**Step 3 — Median.** Even $n$: average positions 3 and 4 → values 7 and 9. Median $= (7+9)/2 = 8$.

**Step 4 — Mode.** 7 appears twice; others once. **Mode = 7**.

**Step 5 — Range.** $15 - 3 = 12$.

**Check:** Median 8 lies between the two 7s and 9 — sensible centre; mode 7 reflects the duplicate."""

CP1_HE = """**שלב 1 — מיון (כבר ממוין).** נתונים: 3, 7, 7, 9, 12, 15. $n=6$.

**שלב 2 — ממוצע.** סכום $= 53$. ממוצע $= 53/6 \\approx 8.83$.

**שלב 3 — חציון.** $n$ זוגי: ממוצע מיקומים 3 ו-4 → 7 ו-9. חציון $= (7+9)/2 = 8$.

**שלב 4 — שכיח.** 7 מופיע פעמיים. **שכיח = 7**.

**שלב 5 — טווח.** $15 - 3 = 12$.

**בדיקה:** חציון 8 בין שני ה-7 ל-9 — מרכז הגיוני; שכיח 7 משקף את הכפילות."""

CP2_EN = """**Step 1 — Sort.** Scores: 55, 60, 65, 70, 70, 100 (already ascending). $n=6$.

**Step 2 — Mean.** Sum $= 420$. Mean $= 420/6 = 70$.

**Step 3 — Median.** Even $n$: middle two are 65 and 70 at positions 3 and 4. Median $= (65+70)/2 = 67.5$.

**Step 4 — Compare.** The score 100 is an outlier pulling the mean up to 70 even though most scores cluster below 70. **Median 67.5 is more representative** of typical performance.

**Exam sentence:** "Mean affected by outlier; median resists it" — one line like this earns reasoning marks."""

CP2_HE = """**שלב 1 — מיון.** ציונים: 55, 60, 65, 70, 70, 100 (כבר עולה). $n=6$.

**שלב 2 — ממוצע.** סכום $= 420$. ממוצע $= 70$.

**שלב 3 — חציון.** $n$ זוגי: אמצעיים 65 ו-70 במיקומים 3 ו-4. חציון $= 67.5$.

**שלב 4 — השוואה.** ציון 100 הוא חריג שמושך את הממוצע ל-70 למרות שרוב הציונים נמוכים מ-70. **חציון 67.5 מייצג יותר** ביצוע טיפוסי.

**משפט לבחינה:** "ממוצע מושפע מחריג; חציון עמיד" — שורה כזו מזכה בנקודות נימוק."""

WHY_EN = """Mean, median, mode, and range are not isolated formulas — they are the vocabulary every later topic assumes. When you study probability (`concept:probability_basic`), you describe distributions by their centre and spread. When you reach descriptive statistics with variance (`concept:descriptive_stats`), you refine "spread" beyond range.

In daily life, news reports cite averages; knowing when that average misleads (one billionaire raising mean wealth) protects you from bad conclusions. On the Bagrut, these four numbers appear inside tables, graphs, and multi-step word problems — mastering them here saves time on every data question in the exam."""

WHY_HE = """ממוצע, חציון, שכיח וטווח אינם נוסחאות מבודדות — הם אוצר המילים שכל נושא מתקדם מניח. כשתלמדו הסתברות (`concept:probability_basic`), תתארו התפלגויות לפי מרכז ופיזור. כשתגיעו לסטטיסטיקה תיאורית עם שונות (`concept:descriptive_stats`), תדייקו "פיזור" מעבר לטווח.

בחיים, כותרות חדשות מצטטות ממוצעים; לדעת מתי ממוצע מטעה (מיליארדר אחד מעלה ממוצע עושר) מגן מפני מסקנות שגויות. בבגרות, ארבעת המספרים מופיעים בטבלאות, גרפים ושאלות מילוליות רב-שלביות — שליטה כאן חוסכת זמן יקר בכל שאלת נתונים בבחינה הסופית."""

SUM_EN = """- **Mean** = sum ÷ count; uses every value; sensitive to outliers; essential for finding missing data via Total = Mean × $n$.
- **Median** = middle of sorted data (average two middles if $n$ even); robust to outliers; preferred for skewed sets.
- **Mode** = most frequent value; works for categorical data; may be absent or plural.
- **Range** = max − min; quick spread snapshot; also outlier-sensitive.
- **Workflow:** sort → compute → interpret which measure fits the question's wording ("average" vs "typical")."""

SUM_HE = """- **ממוצע** = סכום ÷ מספר; משתמש בכל ערך; רגיש לחריגים; חיוני למציאת נתון חסר דרך סכום = ממוצע × $n$.
- **חציון** = אמצע נתונים ממוינים (ממוצע שני אמצעיים ב-$n$ זוגי); עמיד לחריגים; מועדף בקבוצות מוטות.
- **שכיח** = הערך הנפוץ ביותר; מתאים לקטגוריות; ייתכן שאין או שיש כמה.
- **טווח** = מקס − מין; תמונת פיזור מהירה; גם רגיש לחריגים.
- **תהליך:** מיון → חישוב → בחירת מדד לפי ניסוח השאלה ("ממוצע" מול "טיפוסי")."""

EXPLS = [
    fmt_expl(
        "Add all seven values: $4+8+6+5+3+7+9=42$. Divide by $n=7$: $\\bar{x}=42/7=6$. Every observation contributes equally to the mean.",
        "Mean requires no sorting — only a complete sum and correct count. Scan the list twice: once to add, once to verify you used all seven numbers.",
        "Dividing by 6 or forgetting one term (common: skipping the first or last value). Another trap: computing median instead because the list looks unsorted.",
        "If values are small integers, estimate: seven numbers near 5–9 should yield a mean near 6 — catches gross errors before submitting.",
        "סכום שבעת הערכים: $4+8+6+5+3+7+9=42$. חלוקה ב-$n=7$: $\\bar{x}=42/7=6$. כל תצפית תורמת שווה לממוצע.",
        "ממוצע לא דורש מיון — רק סכום מלא וספירה נכונה. עברו על הרשימה פעמיים: פעם לסכום, פעם לוודא שכל שבעת המספרים נכללו.",
        "חלוקה ב-6 או שכחת איבר (נפוץ: דילוג על הראשון או האחרון). מלכודת נוספת: חישוב חציון כי הרשימה נראית לא ממוינת.",
        "אם הערכים שלמים קטנים, העריכו: שבעה מספרים סביב 5–9 ייתנו ממוצע סביב 6 — תופס טעויות גסות.",
    ),
    fmt_expl(
        "Sort ascending: 3, 5, 8, 11, 13, 17, 22. With $n=7$ odd, median position $(7+1)/2=4$. The 4th value is **11**.",
        "Median always needs sorted data. Count inward from both ends to the middle position — for odd $n$ one value remains; do not average unless $n$ is even.",
        "Taking 8 (3rd value) or averaging 8 and 13 without checking that even-$n$ sets need two middles. Another error: median of the unsorted list by position 4 → 17.",
        "Write \"sorted:\" and \"position 4\" on your exam paper — method marks are awarded before the final number 11.",
        "מיון עולה: 3, 5, 8, 11, 13, 17, 22. עם $n=7$ אי-זוגי, מיקום חציון $(7+1)/2=4$. הערך הרביעי הוא **11**.",
        "חציון תמיד דורש נתונים ממוינים. ספרו פנימה משני הקצוות — ב-$n$ אי-זוגי נשאר ערך אחד; אל תממוצעים אלא אם $n$ זוגי.",
        "לקיחת 8 (ערך 3) או ממוצע 8 ו-13 בלי לבדוק ש-$n$ זוגי דורש שני אמצעיים. שגיאה נוספת: חציון הרשימה הלא-ממוינת לפי מיקום 4 → 17.",
        "כתבו \"ממוין:\" ו\"מיקום 4\" — נקודות שיטה לפני המספר 11.",
    ),
    fmt_expl(
        "Count frequencies: 2 appears twice, 4 appears **three times**, others once. The highest count wins — **Mode = 4**.",
        "Mode is about repetition, not size. Tally each value (hash marks or a small table). If two values tie for max frequency, the set is bimodal.",
        "Picking 2 because it appears first, or choosing the largest number 9. Students sometimes report \"no mode\" when one value clearly repeats most.",
        "On Bagrut frequency tables, add the counts column before answering — the mode is the $x$ with largest frequency, not the largest $x$.",
        "ספירת תדירויות: 2 פעמיים, 4 **שלוש פעמים**, השאר פעם. התדירות הגבוהה מנצחת — **שכיח = 4**.",
        "שכיח עוסק בחזרה, לא בגודל. סמנו כל ערך (טבלת סימונים). אם שני ערכים שווים בתדירות מקסימלית — דו-שכיח.",
        "בחירת 2 כי הוא ראשון, או 9 כי הוא הגדול. לפעמים כותבים \"אין שכיח\" כשערך אחד חוזר הכי הרבה.",
        "בטבלאות תדירות בבגרות, סכמו עמודת ספירה — השכיח הוא $x$ עם התדירות הגדולה, לא $x$ הגדול.",
    ),
    fmt_expl(
        "Scan for extremes: maximum **42**, minimum **3**. Range $= 42 - 3 = 39$. Range uses only these two values.",
        "You do not need full sorting for range — only min and max. Still, sorting helps avoid missing a hidden extreme in long lists.",
        "Subtracting in wrong order (3 − 42 = −39) without taking absolute spread, or using second-largest instead of true max.",
        "Range must be non-negative. If your answer is negative, swap min and max — a one-line check saves points.",
        "סריקה לקיצונים: מקסימום **42**, מינימום **3**. טווח $= 42 - 3 = 39$. הטווח משתמש רק בשני הערכים הקיצוניים, לא בכל שאר הנתונים.",
        "אין צורך במיון מלא לטווח — רק מין ומקס. מיון עדיין עוזר לא לפספס קיצון ברשימות ארוכות או כשהמספרים קרובים.",
        "חיסור בסדר הפוך (3 − 42) בלי ערך מוחלט, או שימוש בערך השני-בגודלו במקום המקסימום האמיתי 42.",
        "טווח חייב להיות לא-שלילי. אם התשובה שלילית — החליפו מין ומקס לפני הגשה.",
    ),
    fmt_expl(
        "Original sum $= 70+80+90+75+85 = 400$, $n=5$, old mean $= 400/5 = 80$. New sum adds 95 → $495$, $n=6$, new mean $= 495/6 = 82.5$. Increase $= 2.5$.",
        "Recompute mean from scratch after the new score joins — do not add 95 directly to the old mean. Alternatively: new mean = (old sum + new score) / new count.",
        "Dividing 495 by 5 (forgetting the sixth student) or saying the mean jumps to 95 because that is the new score alone.",
        "When a new value is above the old mean, the mean rises but not all the way to the new value — the answer must lie between 80 and 95; 82.5 fits.",
        "סכום מקורי $= 400$, $n=5$, ממוצע ישן $= 80$. סכום חדש עם 95 → $495$, $n=6$, ממוצע חדש $= 82.5$. עלייה $= 2.5$.",
        "חשבו ממוצע מחדש אחרי הצטרפות הציון — אל תוסיפו 95 ישירות לממוצע הישן. חלופה: ממוצע חדש = (סכום ישן + ציון חדש) / מספר חדש.",
        "חלוקת 495 ב-5 (שכחת התלמיד השישי) או טענה שהממוצע קופץ ל-95.",
        "כשערך חדש מעל הממוצע הישן, הממוצע עולה אך לא עד 95 — התשובה בין 80 ל-95; 82.5 מתאים.",
    ),
    fmt_expl(
        "Use Total $=$ Mean $\\times n$: $15 \\times 6 = 90$. Sum of five known values $= 12+18+14+17+13 = 74$. Missing sixth $= 90 - 74 = 16$.",
        "Reverse the mean formula: mean times count equals total mass. Subtract known parts. Check: $(74+16)/6 = 90/6 = 15$ ✓",
        "Dividing 74 by 5 to guess the missing number, or adding 15 to 74 instead of subtracting. Another slip: using $n=5$ in the total formula.",
        "Always write \"Total = 90\" as line 1 on Bagrut missing-value items — graders look for this setup before the final answer 16.",
        "סכום $=$ ממוצע $\\times n$: $15 \\times 6 = 90$. סכום חמישה ידועים $= 12+18+14+17+13 = 74$. הערך החסר השישי $= 90 - 74 = 16$.",
        "היפוך נוסחת ממוצע: ממוצע כפול מספר תצפיות שווה לסכום הכולל. חסרו את חמשת הערכים הידועים מהסכום. בדיקה: $(74+16)/6 = 15$ ✓",
        "חלוקת 74 ב-5 כדי לנחש, או חיבור 15 ל-74 במקום חיסור. שגיאה נפוצה: שימוש ב-$n=5$ בנוסחת הסכום במקום $n=6$.",
        "כתבו תמיד \"סכום = 90\" כשורה ראשונה — המעריך מחפש את ההכנה האלגברית לפני התשובה 16.",
    ),
    fmt_expl(
        "Sort: 3, 5, 7, 12, 14, 18. Even $n=6$: average the 3rd and 4th values → $(7+12)/2 = 9.5$.",
        "Even-$n$ median rule: two middle positions are $n/2$ and $n/2+1$ → here positions 3 and 4. Write both values before averaging.",
        "Taking only 7 (one middle) or averaging 5 and 12 (wrong positions). Students often forget to sort and pick middle items from the original order.",
        "Half-integer medians (like 9.5) are normal for even $n$ — do not round unless the question asks.",
        "מיון: 3, 5, 7, 12, 14, 18. $n=6$ זוגי: ממוצע הערכים במיקומים 3 ו-4 → $(7+12)/2 = 9.5$.",
        "כלל חציון $n$ זוגי: שני מיקומים אמצעיים הם $n/2$ ו-$n/2+1$ — כאן 3 ו-4 עם ערכים 7 ו-12. כתבו את שני הערכים לפני חישוב הממוצע.",
        "לקיחת רק 7 (מיקום 3 בלבד), או ממוצע 5 ו-12 (מיקומים 2 ו-3 שגויים). שכחת מיון ובחירת אמצע מהסדר המקורי 5, 12, 3.",
        "חציונים שלמים-חצי (9.5) תקינים לחלוטין ב-$n$ זוגי — אל תעגלו למספר שלם אלא אם השאלה מבקשת.",
    ),
    fmt_expl(
        "House prices are **right-skewed**: most homes cluster at lower prices, but a few mansions pull the mean upward. The **median** sits in the middle of the sorted list and represents a typical buyer better.",
        "Ask: would one extreme sale distort the average? If yes, prefer median. Mode could describe the most common price band but misses continuous pound/shekel amounts.",
        "Choosing mean because \"average price\" sounds like mean, without noticing skew. Reporting mode when prices are all distinct decimals.",
        "In Bagrut explain questions, one sentence comparing mean vs median with the word \"outlier\" or \"skewed\" often earns full reasoning credit.",
        "מחירי דירות **מוטים ימינה**: רוב הבתים במחירים נמוכים, אך מעט יוקרה מושכים את הממוצע. **החציון** באמצע הרשימה הממוינת מייצג קונה טיפוסי.",
        "שאלו: האם מכירה קיצונית מעוותת ממוצע? אם כן — חציון. שכיח מתאים לטווח מחירים נפוץ אך פחות לסכומים רציפים.",
        "בחירת ממוצע כי \"מחיר ממוצע\" נשמע כמו mean, בלי לשים לב להטיה. שכיח כשכל המחירים שונים.",
        "בשאלות הסבר בבגרות, משפט אחד עם \"חריג\" או \"מוטה\" לעיתים מזכה בניקוד מלא.",
    ),
]


def build():
    with open(TARGET, encoding="utf-8") as f:
        data = json.load(f)

    section_map = {s.get("kind"): [] for s in data["sections"]}
    for s in data["sections"]:
        section_map.setdefault(s.get("kind"), []).append(s)

    for s in data["sections"]:
        kind = s.get("kind")
        if kind == "intro":
            s["body_en_md"] = INTRO_EN
            s["body_he_md"] = INTRO_HE
        elif kind == "definition":
            s["body_en_md"] = DEF_EN
            s["body_he_md"] = DEF_HE
        elif kind == "theory":
            s["body_en_md"] = THEORY_EN
            s["body_he_md"] = THEORY_HE
        elif kind == "worked_example":
            n = s.get("example_number")
            if n == 1:
                s["body_en_md"] = WE1_EN
                s["body_he_md"] = WE1_HE
            elif n == 2:
                s["body_en_md"] = WE2_EN
                s["body_he_md"] = WE2_HE
            elif n == 3:
                s["body_en_md"] = WE3_EN
                s["body_he_md"] = WE3_HE
        elif kind == "checkpoint":
            if "3, 7, 7, 9, 12, 15" in s.get("body_en_md", ""):
                s["checkpoint_solution_en"] = CP1_EN
                s["checkpoint_solution_he"] = CP1_HE
            else:
                s["checkpoint_solution_en"] = CP2_EN
                s["checkpoint_solution_he"] = CP2_HE
        elif kind == "why_matters":
            s["body_en_md"] = WHY_EN
            s["body_he_md"] = WHY_HE
        elif kind == "summary":
            s["body_en_md"] = SUM_EN
            s["body_he_md"] = SUM_HE

    for i, q in enumerate(data["questions"]):
        en, he = EXPLS[i]
        q["explanation_en"] = en
        q["explanation_he"] = he

    # Fix template filler in exercise e6
    for ex in data["sections"]:
        if ex.get("kind") != "exercise_set":
            continue
        for e in ex.get("exercises", []):
            if e.get("id") == "e6":
                e["solution_en"] = (
                    "**Step 1:** Total $= 15 \\times 6 = 90$.\n\n"
                    "**Step 2:** Sum of known $= 12+18+14+17+13 = 74$.\n\n"
                    "**Step 3:** Sixth $= 90-74 = 16$.\n\n"
                    "**Check:** $(74+16)/6 = 15$ ✓"
                )
                e["solution_he"] = (
                    "**שלב 1:** סכום $= 15 \\times 6 = 90$.\n\n"
                    "**שלב 2:** סכום ידועים $= 74$.\n\n"
                    "**שלב 3:** שישי $= 16$.\n\n"
                    "**בדיקה:** $(74+16)/6 = 15$ ✓"
                )
            if e.get("id") == "e11":
                e["solution_en"] = (
                    "**Step 1:** Original sum $= 25 \\times 8 = 200$.\n\n"
                    "**Step 2:** New sum (7 values) $= 23 \\times 7 = 161$.\n\n"
                    "**Step 3:** Removed value $= 200-161 = 39$.\n\n"
                    "**Check:** Removing 39 from 8 values with mean 25 leaves 7 values with mean 23 ✓"
                )
                e["solution_he"] = (
                    "**שלב 1:** סכום מקורי $= 200$.\n\n"
                    "**שלב 2:** סכום חדש (7 ערכים) $= 161$.\n\n"
                    "**שלב 3:** הערך שהוסר $= 39$.\n\n"
                    "**בדיקה:** הוצאת 39 משמירה ממוצע 23 על 7 ערכים ✓"
                )

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
        raise SystemExit(1)
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
        raise SystemExit("Expected 207/207 in dry-run output")


if __name__ == "__main__":
    main()
