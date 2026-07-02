#!/usr/bin/env python3
"""Expand statistics_descriptive.json to MIN_WORDS depth gates."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "seed_data" / "lessons" / "statistics_descriptive.json"

def q1_en():
    return (
        "**Why this is correct:**\n"
        "First compute the mean: sum $5+3+8+3+9+3+7=38$, so $\\bar{x}=38/7\\approx5.43$. "
        "For the median, **sort** the data: $3,3,3,5,7,8,9$. With $n=7$ (odd), the median is the 4th value: **5**. "
        "For the mode, tally frequencies: 3 appears three times; all others appear once or twice, so **mode $=3$**.\n\n"
        "**How to think about it:**\n"
        "This question tests three different centre measures on the same set. Mean uses every value; median uses position after sorting; mode uses frequency. "
        "They can disagree — here the repeated 3s pull the mode below the median.\n\n"
        "**Common slip:**\n"
        "Finding the median without sorting (picking 8 from the original list) or reporting the mean as the mode because 5 is \"in the middle.\"\n\n"
        "**Exam tip:**\n"
        "On Bagrut 3pt, show sort $\\rightarrow$ position $(n+1)/2$ for median and a frequency count for mode — method marks are split across all three measures."
    )

def q1_he():
    return (
        "**למה זה נכון:**\n"
        "קודם מחשבים ממוצע: סכום $5+3+8+3+9+3+7=38$, ולכן $\\bar{x}=38/7\\approx5.43$. "
        "לחציון — **ממיינים**: $3,3,3,5,7,8,9$. עם $n=7$ (אי-זוגי), החציון הוא הערך הרביעי: **5**. "
        "לשכיח — סופרים תדירויות: 3 מופיע שלוש פעמים; השאר פעם או פעמיים, ולכן **שכיח $=3$**.\n\n"
        "**איך לחשוב על זה:**\n"
        "השאלה בוחנת שלושה מדדי מרכז על אותה קבוצה. ממוצע משתמש בכל ערך; חציון — במיקום אחרי מיון; שכיח — בתדירות. "
        "הם עלולים להסתיר — כאן ה-3 החוזרים מושכים את השכיח מתחת לחציון.\n\n"
        "**טעות נפוצה:**\n"
        "מציאת חציון בלי מיון (בחירת 8 מהרשימה המקורית) או דיווח הממוצע כשכיח כי 5 \"באמצע\".\n\n"
        "**טיפ לבחינה:**\n"
        "בבגרות 3 יח' — הציגו מיון $\\rightarrow$ מיקום $(n+1)/2$ לחציון וספירת תדירויות לשכיח; נקודות שיטה מחולקות בין שלושת המדדים."
    )

def q2_en():
    return (
        "**Why this is correct:**\n"
        "Sort ascending: $4,6,8,9,12,14,17$. Range $=\\max-\\min=17-4=13$. "
        "With $n=7$ (odd), the median is the 4th value in sorted order: **9**.\n\n"
        "**How to think about it:**\n"
        "Range needs only the two extremes — scan or sort to find them. Median always requires sorted data and the middle position $(n+1)/2=4$ here. "
        "Do not confuse range (spread) with median (centre).\n\n"
        "**Common slip:**\n"
        "Subtracting 17 and 4 in the wrong order is fine, but picking 12 or 14 as the median because they \"look central\" without counting positions is wrong.\n\n"
        "**Exam tip:**\n"
        "Write \"sorted:\" before listing the ordered values — graders award a mark for the sort step even when the final numbers are correct."
    )

def q2_he():
    return (
        "**למה זה נכון:**\n"
        "מיון עולה: $4,6,8,9,12,14,17$. טווח $=\\max-\\min=17-4=13$. "
        "עם $n=7$ (אי-זוגי), החציון הוא הערך הרביעי בסדר: **9**.\n\n"
        "**איך לחשוב על זה:**\n"
        "טווח דורש רק שני קיצוניים — סרקו או מיינו. חציון תמיד דורש נתונים ממוינים ומיקום אמצע $(n+1)/2=4$ כאן. "
        "אל תבלבלו טווח (פיזור) עם חציון (מרכז).\n\n"
        "**טעות נפוצה:**\n"
        "בחירת 12 או 14 כחציון כי \"נראים מרכזיים\" בלי ספירת מיקומים, או חיסור 4−17 וקבלת −13.\n\n"
        "**טיפ לבחינה:**\n"
        "כתבו \"ממוין:\" לפני הרשימה — נקודה על שלב המיון. טווח 13 הגיוני: המרחק בין 4 ל-17; אם קיבלתם פחות מ-10, בדקו מינ ומקס."
    )

def q3_en():
    return (
        "**Why this is correct:**\n"
        "Use the mean formula: $(4+6+8+x+10)/5=7$. Sum of known values is 28, so $(28+x)/5=7$, giving $28+x=35$ and **$x=7$**.\n\n"
        "**How to think about it:**\n"
        "This is an inverse mean problem: total sum $=\\bar{x}\\cdot n=7\\times5=35$. "
        "Subtract known values: $35-28=7$. Verify: $(4+6+8+7+10)/5=35/5=7$ ✓. "
        "The missing value 7 equals the mean — the other four values balance around it.\n\n"
        "**Common slip:**\n"
        "Setting up $(4+6+8+x+10)=7$ without dividing by 5, or solving $28+x=7$ instead of $28+x=35$. "
        "Another trap: assuming $x$ must be the largest value because it is unknown.\n\n"
        "**Exam tip:**\n"
        "Bagrut often hides one score; write \"total sum $=\\bar{x}\\cdot n$\" first — one line earns a method mark before you solve for $x$."
    )

def q3_he():
    return (
        "**למה זה נכון:**\n"
        "משתמשים בנוסחת ממוצע: $(4+6+8+x+10)/5=7$. סכום הערכים הידועים 28, ולכן $(28+x)/5=7$, כלומר $28+x=35$ ו-**$x=7$**.\n\n"
        "**איך לחשוב על זה:**\n"
        "זו בעיית ממוצע הפוכה: סכום כולל $=\\bar{x}\\cdot n=7\\times5=35$. "
        "מחסירים ידועים: $35-28=7$. אימות: $(4+6+8+7+10)/5=35/5=7$ ✓. "
        "הערך החסר 7 שווה לממוצע — ארבעת הערכים האחרים מאזנים סביבו.\n\n"
        "**טעות נפוצה:**\n"
        "כתיבת $(4+6+8+x+10)=7$ בלי חלוקה ב-5, או פתרון $28+x=7$ במקום $28+x=35$. "
        "מלכודת נוספת: הנחה ש-$x$ חייב להיות הגדול ביותר.\n\n"
        "**טיפ לבחינה:**\n"
        "בבגרות מסתירים ציון אחד; כתבו \"סכום $=\\bar{x}\\cdot n$\" תחילה — שורה אחת מזכה בנקודת שיטה לפני פתרון $x$."
    )

def q4_en():
    return (
        "**Why this is correct:**\n"
        "Mean: $(2+4+6)/3=12/3=4$. Deviations from 4: $-2,0,2$. Squared: $4,0,4$. "
        "Variance $=(4+0+4)/3=8/3\\approx2.67$.\n\n"
        "**How to think about it:**\n"
        "Follow the four-step pipeline: mean $\\rightarrow$ deviations $\\rightarrow$ square each $\\rightarrow$ average the squares. "
        "Symmetric data around the mean produce equal positive and negative deviations that cancel in the mean but accumulate in variance.\n\n"
        "**Common slip:**\n"
        "Averaging the deviations $(-2+0+2)/3=0$ and calling that variance, or forgetting to divide by $n=3$ after squaring.\n\n"
        "**Exam tip:**\n"
        "Show a small table with columns $x_i$, $x_i-\\bar{x}$, $(x_i-\\bar{x})^2$ — Bagrut graders award marks per column even if the final decimal is slightly off."
    )

def q4_he():
    return (
        "**למה זה נכון:**\n"
        "ממוצע: $(2+4+6)/3=12/3=4$. סטיות מ-4: $-2,0,2$. בריבוע: $4,0,4$. "
        "שונות $=(4+0+4)/3=8/3\\approx2.67$.\n\n"
        "**איך לחשוב על זה:**\n"
        "עקבו אחרי ארבעה שלבים: ממוצע $\\rightarrow$ סטיות $\\rightarrow$ ריבוע כל אחת $\\rightarrow$ ממוצע הריבועים. "
        "נתונים סימטריים סביב הממוצע יוצרים סטיות חיוביות ושליליות שמתבטלות בממוצע אך נצברות בשונות.\n\n"
        "**טעות נפוצה:**\n"
        "ממוצע הסטיות $(-2+0+2)/3=0$ וקריאה לזה שונות, או שכחת חלוקה ב-$n=3$ אחרי הריבוע.\n\n"
        "**טיפ לבחינה:**\n"
        "הציגו טבלה עם $x_i$, $x_i-\\bar{x}$, $(x_i-\\bar{x})^2$ — נקודות על כל עמודה גם אם העשרוני הסופי מעט שגוי."
    )

def q5_en():
    return (
        "**Why this is correct:**\n"
        "Total count $n=2+5+8+3+2=20$. Weighted sum: $50\\cdot2+60\\cdot5+70\\cdot8+80\\cdot3+90\\cdot2=100+300+560+240+180=1380$. "
        "Mean $=1380/20=69$. For median: positions 10 and 11 (average of middles for even $n$). "
        "Cumulative frequencies: 50→2, 60→7, 70→15 — both the 10th and 11th values fall in the 70 group, so **median $=70$**.\n\n"
        "**How to think about it:**\n"
        "Frequency tables require $\\sum f_i x_i$ for the mean and cumulative counts for the median — never average the score column alone.\n\n"
        "**Common slip:**\n"
        "Computing $(50+60+70+80+90)/5=70$ as the mean, or picking the middle row (70) without checking cumulative positions.\n\n"
        "**Exam tip:**\n"
        "Draw a cumulative column; circle where $n/2$ and $n/2+1$ land — two marks for mean setup, two for median reasoning."
    )

def q5_he():
    return (
        "**למה זה נכון:**\n"
        "ספירה $n=2+5+8+3+2=20$. סכום משוקלל: $50\\cdot2+60\\cdot5+70\\cdot8+80\\cdot3+90\\cdot2=1380$. "
        "ממוצע $=1380/20=69$. לחציון: מיקומים 10 ו-11. "
        "שכיחויות מצטברות: 50→2, 60→7, 70→15 — שני הערכים בקבוצת 70, ולכן **חציון $=70$**.\n\n"
        "**איך לחשוב על זה:**\n"
        "טבלת שכיחויות דורשת $\\sum f_i x_i$ לממוצע וספירה מצטברת לחציון — לעולם אל תממוצעו רק את עמודת הציונים.\n\n"
        "**טעות נפוצה:**\n"
        "חישוב $(50+60+70+80+90)/5=70$ כממוצע, או בחירת שורת האמצע בלי בדיקת מיקומים מצטברים.\n\n"
        "**טיפ לבחינה:**\n"
        "ציירו עמודה מצטברת; סמנו היכן $n/2$ ו-$n/2+1$ — נקודות על הגדרת ממוצע ועל נימוק החציון."
    )

def q6_en():
    return (
        "**Why this is correct:**\n"
        "Mean $=(10+20+30+40+50)/5=150/5=30$. Deviations: $-20,-10,0,10,20$. "
        "Squared: $400,100,0,100,400$, sum $=1000$. Variance $=1000/5=200$. "
        "Standard deviation $\\sigma=\\sqrt{200}=10\\sqrt{2}\\approx14.14$.\n\n"
        "**How to think about it:**\n"
        "This evenly spaced set is symmetric about 30, so deviations mirror each other — a good sanity check that squared deviations pair as 400+400, 100+100.\n\n"
        "**Common slip:**\n"
        "Stopping at variance 200 without taking the square root, or using $n-1=4$ in the denominator (population vs sample confusion).\n\n"
        "**Exam tip:**\n"
        "Label the final answer with units if the stem gives them; $\\sigma$ has the same units as the data, while variance does not."
    )

def q6_he():
    return (
        "**למה זה נכון:**\n"
        "ממוצע $=(10+20+30+40+50)/5=150/5=30$. סטיות: $-20,-10,0,10,20$. "
        "בריבוע: $400,100,0,100,400$, סכום $=1000$. שונות $=1000/5=200$. "
        "סטיית תקן $\\sigma=\\sqrt{200}=10\\sqrt{2}\\approx14.14$.\n\n"
        "**איך לחשוב על זה:**\n"
        "קבוצה במרווחים שווים סביב 30 — סטיות משקפות זו את זו; בדיקה: ריבועים בזוגות 400+400, 100+100. "
        "טווח 40 אך $\\sigma\\approx14$ — סטיית תקן ממוצעת מרחקים, לא מקסימום.\n\n"
        "**טעות נפוצה:**\n"
        "עצירה בשונות 200 בלי שורש, או שימוש ב-$n-1=4$ (בלבול אוכלוסייה/מדגם).\n\n"
        "**טיפ לבחינה:**\n"
        "סמנו יחידות אם ניתנו; $\\sigma$ באותן יחידות כמו הנתון, שונות — לא. הציגו טבלת סטיות לנקודות שיטה."
    )

def q7_en():
    return (
        "**Why this is correct:**\n"
        "(a) Sum $=70+85+90+65+80=390$, mean $=390/5=78$. Sorted: $65,70,80,85,90$ — odd $n$, median is the 3rd value: **80**. "
        "(b) Adding a 6th score of 95: new sum $=390+95=485$, new mean $=485/6\\approx80.83$. The mean rises by about 2.83 points; the median would shift too if recalculated.\n\n"
        "**How to think about it:**\n"
        "Part (a) separates centre measures on five tests. Part (b) shows sensitivity of the mean to new high scores — one strong test pulls the average up.\n\n"
        "**Common slip:**\n"
        "Averaging the two middle values for median (even-$n$ habit) when $n=5$ is odd, or adding 95 to the mean directly instead of recomputing from the new sum.\n\n"
        "**Exam tip:**\n"
        "For \"how does the mean change\" questions, always compute old and new means separately — do not guess from the new score alone."
    )

def q7_he():
    return (
        "**למה זה נכון:**\n"
        "(א) סכום $=70+85+90+65+80=390$, ממוצע $=390/5=78$. ממוין: $65,70,80,85,90$ — $n$ אי-זוגי, חציון הוא הערך השלישי: **80**. "
        "(ב) הוספת ציון 95: סכום חדש $=485$, ממוצע חדש $=485/6\\approx80.83$. הממוצע עולה בכ-2.83 נקודות.\n\n"
        "**איך לחשוב על זה:**\n"
        "חלק (א) מפריד מדדי מרכז על חמישה מבחנים. חלק (ב) מראה רגישות הממוצע לציון גבוה — מבחן חזק מושך את הממוצע למעלה.\n\n"
        "**טעות נפוצה:**\n"
        "ממוצע שני אמצעיים (הרגל $n$ זוגי) כש-$n=5$ אי-זוגי, או הוספת 95 לממוצע במקום חישוב מחדש מהסכום.\n\n"
        "**טיפ לבחינה:**\n"
        "בשאלות \"איך הממוצע משתנה\" — חשבו ממוצע ישן וחדש בנפרד; אל תנחשו מהציון החדש בלבד."
    )

def q8_en():
    return (
        "**Why this is correct:**\n"
        "Mean $=(160+165+170+170+175+180)/6=1020/6=170$. Even $n=6$: median $=(170+170)/2=170$. "
        "Mode $=170$ (appears twice). Deviations²: $100,25,0,0,25,100$, sum $=250$. "
        "Variance $=250/6\\approx41.67$, $\\sigma\\approx6.45$ cm.\n\n"
        "**How to think about it:**\n"
        "All four measures can coincide when data cluster at one value — here mean, median, and mode all equal 170, yet $\\sigma\\approx6.45$ shows there is still spread.\n\n"
        "**Common slip:**\n"
        "Using odd-$n$ median rule (picking one 170) instead of averaging both middle values, or reporting mode as 175 because it is the highest repeated-adjacent value.\n\n"
        "**Exam tip:**\n"
        "Multi-part statistics questions award partial credit per measure — box your four answers clearly: mean, median, mode, $\\sigma$."
    )

def q8_he():
    return (
        "**למה זה נכון:**\n"
        "ממוצע $=1020/6=170$. $n=6$ זוגי: חציון $=(170+170)/2=170$. "
        "שכיח $=170$ (פעמיים). סטיות²: $100,25,0,0,25,100$, סכום $=250$. "
        "שונות $=250/6\\approx41.67$, $\\sigma\\approx6.45$ ס\"מ.\n\n"
        "**איך לחשוב על זה:**\n"
        "כל ארבעת המדדים עלולים להתאים כשהנתונים מתרכזים — כאן ממוצע, חציון ושכיח 170, אך $\\sigma\\approx6.45$ מראה שיש עדיין פיזור.\n\n"
        "**טעות נפוצה:**\n"
        "שימוש בכלל $n$ אי-זוגי (170 אחד) במקום ממוצע שני אמצעיים, או דיווח שכיח 175.\n\n"
        "**טיפ לבחינה:**\n"
        "שאלות רב-חלקיות — נקודות חלקיות לכל מדד; סמנו בבירור: ממוצע, חציון, שכיח, $\\sigma$."
    )

SECTIONS_PATCH = {
    "intro": {
        "body_en_md": (
            "A class of 30 students just took a test. The teacher has 30 numbers spread across a page — "
            "how does she describe the results in one sentence? She needs a **summary**, not another list.\n\n"
            "**Descriptive statistics** compresses raw data into a few numbers that answer two questions:\n"
            "- **Centre:** What is typical? (mean, median, mode)\n"
            "- **Spread:** How scattered are the values? (range, variance, standard deviation)\n\n"
            "Real-life uses appear daily in Israeli news and science:\n"
            "- **Average salary** headlines often hide skew — the median worker earns far less than the mean suggests when a few executives earn millions.\n"
            "- **Medical norms:** body temperature 37°C is the centre; deviation from it signals illness.\n"
            "- **Sports analytics:** comparing players by average points *and* consistency (standard deviation).\n\n"
            "On Bagrut math (3 units), you will compute these measures from raw lists and frequency tables, "
            "interpret which centre measure fits skewed data, and compare groups with the same mean but different spread. "
            "These tools reappear in probability and statistical inference later in your path."
        ),
        "body_he_md": (
            "כיתה של 30 תלמידים זה עתה כתבה מבחן. למורה יש 30 מספרים על הדף — "
            "איך היא מתארת את התוצאות במשפט אחד? היא צריכה **סיכום**, לא רשימה נוספת.\n\n"
            "**סטטיסטיקה תיאורית** דוחסת נתונים גולמיים לכמה מספרים שעונים על שתי שאלות:\n"
            "- **מרכז:** מה אופייני? (ממוצע, חציון, שכיח)\n"
            "- **פיזור:** עד כמה הערכים מפוזרים? (טווח, שונות, סטיית תקן)\n\n"
            "שימושים מהחיים מופיעים יומיומית בחדשות ובמדע:\n"
            "- **כותרות משכורת ממוצעת** מסתירות לעיתים הטיה — העובד החציוני מרוויח הרבה פחות ממה שהממוצע מרמז כשמעט מנהלים מרוויחים מיליונים.\n"
            "- **נorms רפואיים:** טמפרטורת גוף 37°C היא המרכז; סטייה ממנה מסמנת מחלה.\n"
            "- **ניתוח ספורט:** השוואת שחקנים לפי ממוצע נקודות *וגם* עקביות (סטיית תקן).\n\n"
            "בבגרות (3 יחידות) תחשבו מדדים אלה מרשימות ומטבלאות שכיחות, "
            "תפרשו איזה מדד מרכז מתאים לנתונים מוטים, ותשוו קבוצות עם אותו ממוצע אך פיזור שונה. "
            "הכלים חוזרים בהסתברות ובהסקה סטטיסטית בהמשך המסלול."
        ),
    },
    "definition": {
        "body_en_md": (
            "Let a dataset contain $n$ values $x_1, x_2, \\ldots, x_n$.\n\n"
            "**Mean (average):** $\\bar{x} = \\frac{\\sum x_i}{n}$ — uses every observation; sensitive to outliers.\n\n"
            "**Median:** Sort ascending. Odd $n$: middle value at position $(n+1)/2$. Even $n$: average the two middle values.\n\n"
            "**Mode:** The value(s) appearing most often; a set may have no mode, one mode, or several (bimodal).\n\n"
            "**Range:** $R = x_{\\max} - x_{\\min}$ — simplest spread; depends only on two extremes.\n\n"
            "**Variance:** $\\sigma^2 = \\frac{\\sum (x_i - \\bar{x})^2}{n}$ — average squared deviation. "
            "On Bagrut 3pt, divide by $n$ (population formula) unless the stem says *sample*.\n\n"
            "**Standard deviation:** $\\sigma = \\sqrt{\\sigma^2}$ — spread in the **same units** as the data.\n\n"
            "**Weighted mean (frequency tables):** $\\bar{x} = \\frac{\\sum f_i x_i}{\\sum f_i}$ where $f_i$ is how often score $x_i$ appears.\n\n"
            "Interpretation: $\\sigma$ measures typical distance from the mean. Small $\\sigma$ = tightly clustered; large $\\sigma$ = widely spread."
        ),
        "body_he_md": (
            "יהיו $n$ ערכים $x_1, x_2, \\ldots, x_n$.\n\n"
            "**ממוצע:** $\\bar{x} = \\frac{\\sum x_i}{n}$ — משתמש בכל תצפית; רגיש לחריגים.\n\n"
            "**חציון:** מיון עולה. $n$ אי-זוגי: ערך אמצעי במיקום $(n+1)/2$. $n$ זוגי: ממוצע שני ערכים אמצעיים.\n\n"
            "**שכיח:** הערך (או הערכים) הכי תכופים; ייתכן שאין שכיח, שכיח אחד או כמה (דו-שכיח).\n\n"
            "**טווח:** $R = x_{\\max} - x_{\\min}$ — פיזור פשוט; תלוי רק בשני קיצוניים.\n\n"
            "**שונות:** $\\sigma^2 = \\frac{\\sum (x_i - \\bar{x})^2}{n}$ — ממוצע סטיות ריבועיות. "
            "בבגרות 3 יח' — חלוקה ב-$n$ (נוסחת אוכלוסייה) אלא אם כתוב *מדגם*.\n\n"
            "**סטיית תקן:** $\\sigma = \\sqrt{\\sigma^2}$ — פיזור ב**אותן יחידות** כמו הנתון.\n\n"
            "**ממוצע משוקלל (טבלאות):** $\\bar{x} = \\frac{\\sum f_i x_i}{\\sum f_i}$ כאשר $f_i$ — תדירות הציון $x_i$.\n\n"
            "פירוש: $\\sigma$ מודד מרחק טיפוסי מהממוצע. $\\sigma$ קטן = ריכוז; $\\sigma$ גדול = פיזור רחב."
        ),
    },
    "theory": {
        "body_en_md": (
            "**Mean vs median — choosing the right centre:**\n"
            "Use the **mean** when data are roughly symmetric and free of extreme outliers — it uses every value and works well in algebra (finding a missing score). "
            "Use the **median** when the distribution is **skewed** (salaries, house prices) or when a few extreme values would distort the average.\n\n"
            "**Example — salary skew:** Ten workers earn 4000₪/month; the CEO earns 100,000₪.\n"
            "- Mean: $(10 \\times 4000 + 100000)/11 \\approx 12{,}727$₪ — pulled up by one outlier.\n"
            "- Median: 4000₪ — half the workers earn at most this; far more representative.\n\n"
            "**Standard deviation in context:**\n"
            "Class A scores: 70, 70, 70, 70, 70 — mean = 70, $\\sigma = 0$ (no spread).\n"
            "Class B scores: 10, 40, 70, 100, 130 — mean = 70, $\\sigma$ is large.\n"
            "Same mean, opposite stories about consistency.\n\n"
            "**Scaling rules (exam favourites):**\n"
            "- Adding constant $c$ to every value: new mean $=\\bar{x}+c$; $\\sigma$ unchanged.\n"
            "- Multiplying by constant $k$: new mean $=k\\bar{x}$; new $\\sigma = |k|\\sigma$.\n\n"
            "**Mode** suits categorical data or discrete values with clear peaks — e.g., most common shoe size sold."
        ),
        "body_he_md": (
            "**ממוצע מול חציון — בחירת מרכז:**\n"
            "השתמשו ב**ממוצע** כשהנתונים סימטריים בערך וללא חריגים קיצוניים — הוא משתמש בכל ערך ומתאים לאלגברה (מציאת ציון חסר). "
            "השתמשו ב**חציון** כשההתפלגות **מוטה** (משכורות, מחירי דירות) או כשכמה ערכים קיצוניים מעוותים את הממוצע.\n\n"
            "**דוגמה — הטיית משכורות:** עשרה עובדים 4000₪; מנכ\"ל 100,000₪.\n"
            "- ממוצע: $\\approx 12{,}727$₪ — נמשך על ידי חריג אחד.\n"
            "- חציון: 4000₪ — חצי העובדים מרוויחים לכל היותר זאת; הרבה יותר מייצג.\n\n"
            "**סטיית תקן בהקשר:**\n"
            "כיתה א: 70, 70, 70, 70, 70 — ממוצע 70, $\\sigma = 0$ (אין פיזור).\n"
            "כיתה ב: 10, 40, 70, 100, 130 — ממוצע 70, $\\sigma$ גדול.\n"
            "אותו ממוצע, סיפורים הפוכים על עקביות.\n\n"
            "**כללי קנה מידה (אהובים בבחינה):**\n"
            "- הוספת קבוע $c$: ממוצע חדש $=\\bar{x}+c$; $\\sigma$ לא משתנה.\n"
            "- הכפלה ב-$k$: ממוצע חדש $=k\\bar{x}$; $\\sigma$ חדש $= |k|\\sigma$.\n\n"
            "**שכיח** מתאים לנתונים קטגוריים או בדידים עם שיא ברור — למשל מידת נעל הנמכרת ביותר."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Descriptive statistics is the language of data across science, economics, and everyday decision-making. "
            "Every news graph, medical chart, and sports ranking you read uses mean, median, or standard deviation — "
            "misreading them leads to bad conclusions (e.g., trusting a mean salary that one billionaire inflates).\n\n"
            "**Why it matters for exams:** Bagrut 3pt regularly allocates 8–12 marks to computing and interpreting these measures from raw data and frequency tables. "
            "University courses in psychology, biology, and social sciences assume you can read a mean±SD line in a paper.\n\n"
            "**Cross-subject links:** Physics labs report average measurement and spread; chemistry uses mean reaction times. "
            "This lesson feeds directly into **probability distributions** and **normal distribution** — where $\\mu$ and $\\sigma$ describe entire populations."
        ),
        "body_he_md": (
            "סטטיסטיקה תיאורית היא שפת הנתונים במדע, בכלכלה ובקבלת החלטות יומיומית. "
            "כל גраф בחדשות, תרשים רפואי ודירוג ספורט משתמש בממוצע, חציון או סטיית תקן — "
            "קריאה שגויה מובילה למסקנות רעות (למשל אמון במשכורת ממוצעת שמיליארדר אחד מנפח).\n\n"
            "**למה זה חשוב לבחינות:** בבגרות 3 יח' מקצים 8–12 נקודות לחישוב ופרשנות מדדים מנתונים גולמיים ומטבלאות. "
            "קורסים באוניברסיטה בפסיכולוגיה, ביולוגיה ומדעי החברה מניחים שאתם קוראים שורת ממוצע±סט\"ת.\n\n"
            "**קשרים בין-מקצועיים:** מעבדות פיזיקה מדווחות ממוצע מדידה ופיזור; כימיה — זמני תגובה ממוצעים. "
            "שיעור זה מזין ישירות **התפלגויות הסתברות** ו**התפלגות נורמלית** — שם $\\mu$ ו-$\\sigma$ מתארים אוכלוסיות שלמות."
        ),
    },
}

CHECKPOINTS = {
    0: {
        "checkpoint_solution_en": (
            "**Step 1 — Mean.** Sum $=4+8+6+8+3+7+8+2=46$. Mean $=46/8=5.75$.\n\n"
            "**Step 2 — Sort.** $2,3,4,6,7,8,8,8$.\n\n"
            "**Step 3 — Median.** Even $n=8$: average positions 4 and 5: $(6+7)/2=6.5$.\n\n"
            "**Step 4 — Mode.** Count: 8 appears three times; all others once or twice. Mode $=8$.\n\n"
            "**Step 5 — Range.** $8-2=6$.\n\n"
            "**Check:** Mode 8 is the highest repeated value; median 6.5 sits between 6 and 7 as expected."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — ממוצע.** סכום $=46$. ממוצע $=46/8=5.75$.\n\n"
            "**שלב 2 — מיון.** $2,3,4,6,7,8,8,8$.\n\n"
            "**שלב 3 — חציון.** $n=8$ זוגי: ממוצע מיקומים 4 ו-5: $(6+7)/2=6.5$.\n\n"
            "**שלב 4 — שכיח.** 8 מופיע שלוש פעמים. שכיח $=8$.\n\n"
            "**שלב 5 — טווח.** $8-2=6$.\n\n"
            "**בדיקה:** שכיח 8 הוא הערך החוזר ביותר; חציון 6.5 בין 6 ל-7 — הגיוני."
        ),
    },
    1: {
        "checkpoint_solution_en": (
            "**Step 1 — Total count.** $n=3+8+12+5+2=30$.\n\n"
            "**Step 2 — Median positions.** For even $n$, use average of positions 15 and 16.\n\n"
            "**Step 3 — Cumulative frequencies.** 60→3, 70→11, 80→23. Both the 15th and 16th values lie in the score-80 group.\n\n"
            "**Answer:** Median $=80$.\n\n"
            "**Check:** The bulk of students (12 out of 30) scored 80 — median landing there is sensible."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — ספירה.** $n=30$.\n\n"
            "**שלב 2 — מיקומי חציון.** $n$ זוגי: ממוצע מיקומים 15 ו-16.\n\n"
            "**שלב 3 — שכיחויות מצטברות.** 60→3, 70→11, 80→23. שני הערכים בקבוצת 80.\n\n"
            "**תשובה:** חציון $=80$.\n\n"
            "**בדיקה:** רוב התלמידים (12 מתוך 30) קיבלו 80 — חציון שם הגיוני."
        ),
    },
}

WE_PATCH = {
    0: {
        "body_en_md": (
            "**Dataset:** $\\{3, 7, 8, 2, 9, 5\\}$\n\n**Find:** mean and median.\n\n"
            "### Move 1 — Compute the mean.\n"
            "Add all six values: $3+7+8+2+9+5=34$. Divide by $n=6$:\n"
            "$$\\bar{x} = \\frac{34}{6} \\approx 5.67$$\n\n"
            "### Move 2 — Sort the data ascending.\n"
            "Median requires sorted order — never skip this step:\n"
            "$$2, 3, 5, 7, 8, 9$$\n\n"
            "### Move 3 — Find the median ($n=6$, even).\n"
            "With even count, average the two middle values at positions 3 and 4:\n"
            "$$\\text{Median} = \\frac{5 + 7}{2} = 6$$\n\n"
            "**Answer:** Mean $\\approx 5.67$, Median $= 6$.\n\n"
            "**Exam habit:** Write \"positions 3 and 4\" before averaging — graders award the even-$n$ rule separately from the final number.\n\n"
            "**Sanity check:** Median 6 is close to mean 5.67 for this fairly symmetric set; a large gap would signal skew or an outlier worth investigating.\n\n"
            "**Transfer:** The same sort-then-locate workflow applies to quartiles and frequency-table medians later in this lesson."
        ),
        "body_he_md": (
            "**קבוצת נתונים:** $\\{3, 7, 8, 2, 9, 5\\}$\n\n**מצאו:** ממוצע וחציון.\n\n"
            "### צעד 1 — חישוב ממוצע.\n"
            "סכום שש הערכים: $3+7+8+2+9+5=34$. חלוקה ב-$n=6$:\n"
            "$$\\bar{x} = \\frac{34}{6} \\approx 5.67$$\n\n"
            "### צעד 2 — מיון עולה.\n"
            "חציון דורש סדר — לעולם אל תדלגו על מיון:\n"
            "$$2, 3, 5, 7, 8, 9$$\n\n"
            "### צעד 3 — חציון ($n=6$, זוגי).\n"
            "בספירה זוגית, ממוצע שני ערכים אמצעיים במיקומים 3 ו-4:\n"
            "$$\\text{חציון} = \\frac{5 + 7}{2} = 6$$\n\n"
            "**תשובה:** ממוצע $\\approx 5.67$, חציון $= 6$.\n\n"
            "**הרגל לבחינה:** כתבו \"מיקומים 3 ו-4\" לפני הממוצע — המעריך מעניק נקודות על כלל $n$ הזוגי, לא רק על המספר הסופי.\n\n"
            "**בדיקה:** חציון 6 קרוב לממוצע 5.67 — קבוצה סימטרית בערך; פער גדול היה מרמז על הטיה או על ערך חריג.\n\n"
            "**העברה:** אותו סדר מיון-ואיתור חל על רבעונים וחציון מטבלת שכיחויות בהמשך השיעור."
        ),
    },
    1: {
        "body_en_md": (
            "**Frequency table of test scores:**\n\n| Score | Frequency |\n|-------|-----------|\n| 60 | 3 |\n| 70 | 8 |\n| 80 | 12 |\n| 90 | 5 |\n| 100 | 2 |\n\n"
            "**Find:** mean score.\n\n"
            "### Move 1 — Compute each product $f_i \\cdot x_i$.\n"
            "$$60 \\times 3 = 180,\\quad 70 \\times 8 = 560,\\quad 80 \\times 12 = 960,\\quad 90 \\times 5 = 450,\\quad 100 \\times 2 = 200$$\n"
            "Weighted sum: $\\sum f_i x_i = 180 + 560 + 960 + 450 + 200 = 2350$.\n\n"
            "### Move 2 — Total number of students $n$.\n"
            "$$n = 3 + 8 + 12 + 5 + 2 = 30$$\n\n"
            "### Move 3 — Apply the weighted mean formula.\n"
            "$$\\bar{x} = \\frac{\\sum f_i x_i}{n} = \\frac{2350}{30} \\approx 78.3$$\n\n"
            "**Answer:** Mean score $\\approx 78.3$.\n\n"
            "**Why not average the score column?** $(60+70+80+90+100)/5=80$ ignores that 80 was earned by 12 students — weighting is essential.\n\n"
            "**Exam tip:** Show the $\\sum f_ix_i$ line before dividing — one sign error here is the most common lost mark on frequency-table questions.\n\n"
            "**Transfer:** The same table supports finding the median via cumulative counts in the next checkpoint."
        ),
        "body_he_md": (
            "**טבלת שכיחויות של ציוני מבחן:**\n\n| ציון | שכיחות |\n|------|--------|\n| 60 | 3 |\n| 70 | 8 |\n| 80 | 12 |\n| 90 | 5 |\n| 100 | 2 |\n\n"
            "**מצאו:** ממוצע.\n\n"
            "### צעד 1 — חישוב כל מכפלה $f_i \\cdot x_i$.\n"
            "$$60 \\times 3 = 180,\\quad 70 \\times 8 = 560,\\quad 80 \\times 12 = 960,\\quad 90 \\times 5 = 450,\\quad 100 \\times 2 = 200$$\n"
            "סכום משוקלל: $\\sum f_i x_i = 2350$.\n\n"
            "### צעד 2 — מספר תלמידים $n=30$.\n\n"
            "### צעד 3 — נוסחת ממוצע משוקלל.\n"
            "$$\\bar{x} = \\frac{2350}{30} \\approx 78.3$$\n\n"
            "**תשובה:** ממוצע $\\approx 78.3$.\n\n"
            "**למה לא ממוצע עמודת הציונים?** $(60+70+80+90+100)/5=80$ מתעלם מ-12 תלמידים שקיבלו 80 — משקל חובה.\n\n"
            "**טיפ לבחינה:** הציגו את $\\sum f_ix_i$ לפני החלוקה — שגיאת סימן כאן היא איבוד נקודות נפוץ בבחינות בגרות.\n\n"
            "**העברה:** אותה טבלה תומכת בחציון דרך ספירה מצטברת של תדירויות בתרגיל הבא."
        ),
    },
    2: {
        "body_en_md": (
            "**Two classes, both with mean = 70:**\n"
            "- Class A: $\\{65, 68, 70, 72, 75\\}$ — tightly clustered around 70.\n"
            "- Class B: $\\{50, 60, 70, 80, 90\\}$ — evenly spread from 50 to 90.\n\n"
            "**Question:** Which class has the larger standard deviation?\n\n"
            "### Move 1 — Class A: compute variance step by step.\n"
            "Deviations from 70: $-5,-2,0,2,5$. Squared: $25,4,0,4,25$. Sum $=58$.\n"
            "$$\\sigma_A^2 = \\frac{58}{5} = 11.6, \\quad \\sigma_A = \\sqrt{11.6} \\approx 3.4$$\n\n"
            "### Move 2 — Class B: same procedure.\n"
            "Deviations: $-20,-10,0,10,20$. Squared: $400,100,0,100,400$. Sum $=1000$.\n"
            "$$\\sigma_B^2 = \\frac{1000}{5} = 200, \\quad \\sigma_B = \\sqrt{200} \\approx 14.1$$\n\n"
            "**Conclusion:** Class B has roughly **four times** the standard deviation despite the identical mean.\n\n"
            "**Interpretation:** In Class A, most students scored within a few points of 70; in Class B, scores span 40 points — high performers and strugglers coexist.\n\n"
            "**Exam tip:** Always compute $\\sigma$ for both groups before comparing — never judge spread by eye or range alone when sample sizes differ."
        ),
        "body_he_md": (
            "**שתי כיתות, שתיהן עם ממוצע 70:**\n"
            "- כיתה א: $\\{65, 68, 70, 72, 75\\}$ — צפופות סביב 70.\n"
            "- כיתה ב: $\\{50, 60, 70, 80, 90\\}$ — פרוסות מ-50 עד 90.\n\n"
            "**שאלה:** לאיזו כיתה סטיית תקן גדולה יותר?\n\n"
            "### צעד 1 — כיתה א: חישוב שונות שלב-שלב.\n"
            "סטיות מ-70: $-5,-2,0,2,5$. בריבוע: $25,4,0,4,25$. סכום $=58$.\n"
            "$$\\sigma_A^2 = \\frac{58}{5} = 11.6, \\quad \\sigma_A \\approx 3.4$$\n\n"
            "### צעד 2 — כיתה ב: אותה שיטה.\n"
            "סטיות: $-20,-10,0,10,20$. בריבוע: $400,100,0,100,400$. סכום $=1000$.\n"
            "$$\\sigma_B^2 = 200, \\quad \\sigma_B \\approx 14.1$$\n\n"
            "**מסקנה:** לכיתה ב סטיית תקן גדולה פי **~4** למרות ממוצע זהה.\n\n"
            "**פירוש:** בכיתה א רוב התלמידים בתוך כמה נקודות מ-70; בכיתה ב הציונים נפרשים על 40 נקודות — מצטיינים ומתקשים יחד.\n\n"
            "**טיפ לבחינה:** חשבו $\\sigma$ לשתי הקבוצות לפני השוואה — אל תשפטו בעין או לפי טווח בלבד."
        ),
    },
}

METHOD_GUIDE = {
    "body_en_md": (
        "| Measure | Steps | When to use |\n|---------|-------|-------------|\n"
        "| Mean | Sum all values ÷ $n$ | Symmetric data, no outliers |\n"
        "| Median | Sort → middle (or avg of two middles) | Skewed data, outliers present |\n"
        "| Mode | Tally frequencies → highest count | Discrete / categorical peaks |\n"
        "| Range | $\\max - \\min$ | Quick two-extreme spread |\n"
        "| Variance | Mean → deviations → square → average | Formal spread calculation |\n"
        "| Std dev | $\\sqrt{\\text{variance}}$ | Same units as data |\n"
        "| Weighted mean | $\\bar{x} = \\frac{\\sum f_i x_i}{\\sum f_i}$ | Frequency tables |\n\n"
        "**Workflow checklist:** (1) Read the stem — raw list or table? (2) Sort if median needed. "
        "(3) Compute $\\bar{x}$. (4) Pick centre measure by data shape. (5) For spread: range for a glance, $\\sigma$ for precision. "
        "(6) Interpret in context — state units and which measure is more representative.\n\n"
        "**Comparison problems:** Same mean but different $\\sigma$ → smaller $\\sigma$ means more consistent performance."
    ),
    "body_he_md": (
        "| מדד | שלבים | מתי? |\n|-----|-------|------|\n"
        "| ממוצע | סכום ÷ $n$ | נתונים סימטריים |\n"
        "| חציון | מיון → אמצע | נתונים מוטים/חריגים |\n"
        "| שכיח | ספירת תדירויות | שיאים בדידים |\n"
        "| טווח | $\\max - \\min$ | פיזור מהיר |\n"
        "| שונות | ממוצע → סטיות → ריבוע → ממוצע | חישוב פורמלי |\n"
        "| סטיית תקן | $\\sqrt{\\text{שונות}}$ | יחידות כמו הנתון |\n"
        "| ממוצע משוקלל | $\\frac{\\sum f_i x_i}{\\sum f_i}$ | טבלאות |\n\n"
        "**רשימת בדיקה:** (1) קראו — רשימה או טבלה? (2) מיינו אם צריך חציון. "
        "(3) חשבו $\\bar{x}$. (4) בחרו מדד מרכז לפי צורת הנתונים. (5) לפיזור: טווח או $\\sigma$. "
        "(6) פרשו בהקשר — ציינו יחידות ואיזה מדד מייצג יותר.\n\n"
        "**השוואה:** אותו ממוצע, $\\sigma$ שונה → $\\sigma$ קטן = ביצועים עקביים יותר."
    ),
}

BEFORE_EXAM = {
    "body_en_md": (
        "**Key formulas (memorise these):**\n"
        "- Mean: $\\bar{x} = \\dfrac{\\sum x_i}{n}$\n"
        "- Weighted mean: $\\bar{x} = \\dfrac{\\sum f_i x_i}{\\sum f_i}$\n"
        "- Variance: $\\sigma^2 = \\dfrac{\\sum (x_i - \\bar{x})^2}{n}$\n"
        "- Std dev: $\\sigma = \\sqrt{\\sigma^2}$\n"
        "- Range: $x_{\\max} - x_{\\min}$\n\n"
        "**Typical Bagrut 3pt patterns:**\n"
        "1. Find mean, median, mode from raw data (3–4 marks) — show sort step for median.\n"
        "2. Find mean and median from a frequency table (4–5 marks) — weighted sum + cumulative counts.\n"
        "3. Compute standard deviation and interpret spread (4–5 marks) — show deviation table.\n"
        "4. Compare two groups with same mean but different $\\sigma$ (2–3 marks) — explain in words.\n\n"
        "**Marking tips:** Always sort before median. Show each $(x_i - \\bar{x})^2$ in variance. "
        "State units in context questions. For skewed data, justify why median beats mean."
    ),
    "body_he_md": (
        "**נוסחאות מרכזיות (לשנן):**\n"
        "- ממוצע: $\\bar{x} = \\dfrac{\\sum x_i}{n}$\n"
        "- ממוצע משוקלל: $\\bar{x} = \\dfrac{\\sum f_i x_i}{\\sum f_i}$\n"
        "- שונות: $\\sigma^2 = \\dfrac{\\sum (x_i - \\bar{x})^2}{n}$\n"
        "- סטיית תקן: $\\sigma = \\sqrt{\\sigma^2}$\n"
        "- טווח: $x_{\\max} - x_{\\min}$\n\n"
        "**דפוסי שאלות טיפוסיים בבגרות 3 יח':**\n"
        "1. ממוצע, חציון, שכיח מנתונים גולמיים (3–4 נק') — הציגו מיון לחציון.\n"
        "2. ממוצע וחציון מטבלת שכיחות (4–5 נק') — סכום משוקלל + ספירה מצטברת.\n"
        "3. סטיית תקן ופרשנות פיזור (4–5 נק') — טבלת סטיות.\n"
        "4. השוואת קבוצות עם אותו ממוצע ו-$\\sigma$ שונה (2–3 נק') — הסבר במילים.\n\n"
        "**טיפים לניקוד:** מיינו לפני חציון. הציגו $(x_i - \\bar{x})^2$ בחישוב שונות. "
        "ציינו יחידות בשאלות הקשר. בנתונים מוטים — הצדיקו למה חציון עדיף על ממוצע."
    ),
}

PITFALL = {
    "body_en_md": (
        "**Mistake 1 — Forgetting to sort before finding the median.**\n"
        "The median is the middle value of **sorted** data. With unsorted input $\\{9,2,7,3,5\\}$, the middle listed value 7 is wrong; sorted $\\{2,3,5,7,9\\}$ gives median 5.\n\n"
        "**Mistake 2 — Squaring the deviations incorrectly in variance.**\n"
        "Variance = average of $(x_i - \\bar{x})^2$. Square **each** deviation first, then average. "
        "Wrong: $\\bigl(\\frac{\\sum(x_i-\\bar{x})}{n}\\bigr)^2 = 0$. Right: $\\frac{\\sum(x_i-\\bar{x})^2}{n}$.\n\n"
        "**Mistake 3 — Confusing mean with median on skewed data.**\n"
        "One CEO salary can double the mean while the median stays at the typical worker wage. "
        "Always ask: \"Are there extreme values?\" If yes, report the median for \"typical\" and the mean only with caution.\n\n"
        "**Mistake 4 — Averaging scores in a frequency table instead of weighting.**\n"
        "$(50+60+70)/3=60$ ignores that 70 might appear eight times. Use $\\sum f_ix_i / n$."
    ),
    "body_he_md": (
        "**טעות 1 — שכחת מיון לפני חציון.**\n"
        "החציון הוא ערך אמצעי של נתונים **ממוינים**. בקלט לא ממוין $\\{9,2,7,3,5\\}$, הערך 7 שגוי; ממוין $\\{2,3,5,7,9\\}$ נותן חציון 5.\n\n"
        "**טעות 2 — ריבוע סטיות שגוי בשונות.**\n"
        "שונות = ממוצע $(x_i - \\bar{x})^2$. הרביעו **כל** סטייה, ואז ממוצע. "
        "שגוי: $\\bigl(\\frac{\\sum(x_i-\\bar{x})}{n}\\bigr)^2 = 0$. נכון: $\\frac{\\sum(x_i-\\bar{x})^2}{n}$.\n\n"
        "**טעות 3 — בלבול ממוצע וחציון בנתונים מוטים.**\n"
        "משכורת מנכ\"ל אחת יכולה לכפות את הממוצע בעוד החציון נשאר על שכר עובד טיפוסי. "
        "שאלו: \"יש ערכים קיצוניים?\" — אם כן, דווחו חציון ל\"טיפוסי\".\n\n"
        "**טעות 4 — ממוצע ציונים בטבלה במקום משקל.**\n"
        "$(50+60+70)/3=60$ מתעלם מ-70 שמופיע שמונה פעמים. השתמשו ב-$\\sum f_ix_i / n$."
    ),
}

EXPLANATIONS = [q1_en, q1_he, q2_en, q2_he, q3_en, q3_he, q4_en, q4_he,
                q5_en, q5_he, q6_en, q6_he, q7_en, q7_he, q8_en, q8_he]

ACCEPTABLE = [
    ["Mean=5.43", "5.43", "Median=5", "Mode=3", "3"],
    ["Range=13", "13", "Median=9", "9"],
    ["x=7", "7"],
    ["Variance=8/3", "2.67", "8/3 ≈ 2.67"],
    ["Mean=69", "69", "Median=70", "70"],
    ["σ=14.14", "14.14", "10√2", "Std dev ≈ 14.14"],
    ["Mean=78", "78", "Median=80", "80", "New mean=80.83", "80.83"],
    ["Mean=170", "170", "Median=170", "Mode=170", "σ≈6.45", "6.45"],
]


def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))

    kind_map = {s["kind"]: s for s in data["sections"] if "kind" in s}
    for kind, patch in SECTIONS_PATCH.items():
        if kind == "why_matters":
            for s in data["sections"]:
                if s.get("kind") == "why_matters":
                    s.update(patch)
        elif kind in kind_map:
            kind_map[kind].update(patch)

    we_idx = 0
    cp_idx = 0
    for s in data["sections"]:
        if s.get("kind") == "worked_example" and we_idx in WE_PATCH:
            s.update(WE_PATCH[we_idx])
            we_idx += 1
        if s.get("kind") == "checkpoint" and cp_idx in CHECKPOINTS:
            s.update(CHECKPOINTS[cp_idx])
            cp_idx += 1
        if s.get("kind") == "method_guide":
            s.update(METHOD_GUIDE)
        if s.get("kind") == "before_exam":
            s.update(BEFORE_EXAM)
        if s.get("kind") == "pitfall":
            s.update(PITFALL)

    for i, q in enumerate(data["questions"]):
        q["explanation_en"] = EXPLANATIONS[i * 2]()
        q["explanation_he"] = EXPLANATIONS[i * 2 + 1]()
        q["answer_payload"]["acceptable_answers"] = ACCEPTABLE[i]

    # Fix e7/e8 template solutions in exercise_set
    for ex in data["sections"][-3]["exercises"] if False else []:
        pass
    for s in data["sections"]:
        if s.get("kind") == "exercise_set":
            for ex in s.get("exercises", []):
                if ex["id"] == "e7":
                    ex["solution_en"] = "(a) Sum=390, Mean=78. Sorted: 65,70,80,85,90. Median=80. (b) New sum=485, New mean=485/6≈80.83."
                if ex["id"] == "e8":
                    ex["solution_en"] = "Mean=170. Median=(170+170)/2=170. Mode=170. Variance=250/6≈41.67. σ≈6.45."

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(OUT.read_text(encoding="utf-8"))
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
