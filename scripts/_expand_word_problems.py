#!/usr/bin/env python3
"""Expand word_problems.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/word_problems.json"

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

EXPAND_KINDS = {
    "intro", "definition", "theory", "worked_example", "pitfall",
    "why_matters", "method_guide", "before_exam", "summary",
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


INTRO_EN = """**Word problems** are algebra dressed in everyday language. The mathematics is not harder than solving equations — the challenge is **translation**: turning sentences about trains, mixtures, ages, and work crews into variables and constraints you can solve.

Every Israeli math track (3, 4, and 5 units) includes applied problems on **distance–rate–time**, **mixtures**, **age relationships**, and **work rates**. Bagrut questions often mix two types in one stem, so you need a reliable framework, not memorized templates.

**Five-step method (use on every problem):**
1. **Read** — underline what is asked and list every number with its unit.
2. **Define variables** — write "Let $x$ = …" in plain language (current age, liters added, hours until meeting).
3. **Write equations** — one equation per independent constraint in the story.
4. **Solve** — algebra, systems, or fractions as needed.
5. **Verify in context** — units match, answer is positive where required, and the story still makes sense.

Mastering this lesson means you can look at a paragraph and name the **pattern** before picking a formula."""

INTRO_HE = """**בעיות מילוליות** הן אלגברה בלבוש של שפה יומיומית. המתמטיקה אינה קשה יותר מפתרון משוואות — האתגר הוא **תרגום**: הפיכת משפטים על רכבות, תערובות, גילאים וצוותי עבודה למשתנים ולאילוצים שאפשר לפתור.

בכל מסלול מתמטיקה בישראל (3, 4 ו-5 יחידות) מופיעות בעיות יישום על **מרחק–מהירות–זמן**, **תערובות**, **יחסי גיל** ו**קצבי עבודה**. שאלות בגרות לעיתים משלבות שני סוגים בנתון אחד, ולכן צריך מסגרת עבודה אמינה, לא תבניות שסולפות בעל פה.

**שיטת חמישה שלבים (בכל בעיה):**
1. **קרא** — הדגישו מה נשאל ורשמו כל מספר עם יחידתו.
2. **הגדר משתנים** — כתבו "נסמן $x$ = …" בשפה ברורה (גיל נוכחי, ליטרים שנוספו, שעות עד מפגש).
3. **כתוב משוואות** — משוואה אחת לכל אילוץ עצמאי בסיפור.
4. **פתור** — אלגברה, מערכות או שברים לפי הצורך.
5. **בדוק בהקשר** — יחידות תואמות, תשובה חיובית כשנדרש, והסיפור עדיין הגיוני.

שליטה בשיעור זה אומרת שאפשר להסתכל על פסקה ולזהות את **הדפוס** לפני בחירת הנוסחה."""

DEF_EN = """Word problems reuse a small set of **core formulas**. Learn them with units attached — speed in km/h, concentration as a decimal or percent, work rate as "fraction of job per day."

**Distance–Rate–Time:**
$$d = r \\times t \\quad \\Rightarrow \\quad t = \\frac{d}{r}, \\quad r = \\frac{d}{t}$$
When two objects move **toward each other**, their **relative speed** is the **sum** of individual speeds. Same direction (catch-up): subtract speeds.

**Mixture (conservation of solute):**
$$m_1 c_1 + m_2 c_2 = (m_1 + m_2)\\, c_{\\text{final}}$$
The **dissolved substance** (acid, salt, alcohol) is conserved; only volume and concentration change when you add solvent or mix solutions.

**Work rate:** If worker A finishes alone in $a$ days, daily rate $= 1/a$ of the job.
$$\\frac{1}{a} + \\frac{1}{b} = \\frac{1}{T} \\quad \\text{(together)} \\qquad \\frac{1}{a} - \\frac{1}{b} = \\frac{1}{T} \\quad \\text{(fill vs drain)}$$

**Age problems:** Let **current** age $= x$. In $k$ years: $x + k$; $k$ years ago: $x - k$. Always anchor equations at the **same calendar moment** ("today" vs "in 10 years")."""

DEF_HE = """בעיות מילוליות משתמשות שוב ושוב באותה קבוצה קטנה של **נוסחאות מרכזיות**. למדו אותן עם יחידות: מהירות בק\"מ/שעה, ריכוז כעשרוני או אחוז, קצב עבודה כ\"חלק מהעבודה ליום\".

**מרחק–מהירות–זמן:**
$$d = r \\times t \\quad \\Rightarrow \\quad t = \\frac{d}{r}, \\quad r = \\frac{d}{t}$$
כששני גופים נעים **זה לקראת זה**, **המהירות היחסית** היא **סכום** המהירויות. באותו כיוון (מרדף): מחסירים מהירויות.

**תערובת (שימור חומר מסיס):**
$$m_1 c_1 + m_2 c_2 = (m_1 + m_2)\\, c_{\\text{סופי}}$$
**החומר המסיס** (חומצה, מלח, אלכוהול) נשמר; רק הנפח והריכוז משתנים כשמוסיפים ממס או מערבבים תמיסות.

**קצב עבודה:** אם עובד A מסיים לבד ב-$a$ ימים, קצב יומי $= 1/a$ מהעבודה.
$$\\frac{1}{a} + \\frac{1}{b} = \\frac{1}{T} \\quad \\text{(יחד)} \\qquad \\frac{1}{a} - \\frac{1}{b} = \\frac{1}{T} \\quad \\text{(מילוי מול ניקוז)}$$

**בעיות גיל:** **גיל נוכחי** $= x$. בעוד $k$ שנים: $x + k$; לפני $k$ שנים: $x - k$. עוגנו משוואות **באותה נקודת זמן** (\"היום\" לעומת \"עוד 10 שנים\")."""

THEORY_EN = """### Distance problems
**Meeting (head-on):** Two objects travel toward each other from opposite ends. Combined speed $= r_1 + r_2$. Time until meeting: $t = d / (r_1 + r_2)$. Each distance: $r_i t$.

**Catching up:** The faster object starts later or from behind. At the catch moment, distances from a common reference are equal: $r_A t = r_B (t - \\Delta t)$ where $\\Delta t$ is the head start in time.

**Opposite directions from same point:** Separation speed $= r_1 + r_2$. Distance apart after time $t$: $(r_1 + r_2)t$.

### Mixture problems
**Adding liquid:** Conserve solute mass. If you add pure water, solute amount stays fixed while total volume grows: $\\text{solute} = m_1 c_1 = (m_1 + x) c_{\\text{new}}$.

**Mixing two solutions:** Use the weighted average formula. Draw a table: rows = sources, columns = volume × concentration = amount of solute.

**Replacement cycles:** Each drain-and-replace step multiplies concentration by $(1 - \\text{fraction removed})$.

### Work problems
Convert every worker/pipe to a **rate** (job per hour). Combined: rates **add** when working together. A drain **subtracts** from a fill rate.

### Age and value problems
Define variables for **today**. Translate "in $k$ years" and "$k$ years ago" consistently. For coins: $n_A v_A + n_B v_B = \\text{total value}$."""

THEORY_HE = """### בעיות מרחק
**מפגש (פנים אל פנים):** שני גופים נעים זה לקראת זה מקצוות מנוגדים. מהירות משולבת $= r_1 + r_2$. זמן עד מפגש: $t = d / (r_1 + r_2)$. מרחק כל אחד: $r_i t$.

**מרדף:** המהיר יותר מתחיל מאוחר או מאחור. ברגע המפגש, המרחקים מנקודת ייחוס משותפת שווים: $r_A t = r_B (t - \\Delta t)$ כאשר $\\Delta t$ הוא יתרון הזמן.

**כיוונים מנוגדים מאותה נקודה:** מהירות התרחקות $= r_1 + r_2$. מרחק ביןיהם אחרי זמן $t$: $(r_1 + r_2)t$.

### בעיות תערובת
**הוספת נוזל:** שמרו על מסת החומר המסיס. הוספת מים טהורים: כמות המסיס קבועה, הנפח הכולל גדל: $\\text{מסיס} = m_1 c_1 = (m_1 + x) c_{\\text{חדש}}$.

**ערבוב שתי תמיסות:** נוסחת ממוצע משוקלל. טבלה: שורות = מקורות, עמודות = נפח × ריכוז = כמות מסיס.

**מחזורי החלפה:** כל שלב של ריקון והחלפה מכפיל את הריכוז ב-$(1 - \\text{שבר שרוקן})$.

### בעיות עבודה
המירו כל עובד/צינור ל**קצב** (עבודה לשעה). יחד: קצבים **מתחברים**. ניקוז **מחסיר** מקצב מילוי.

### גיל וערך
הגדירו משתנים ל**היום**. תרגמו \"בעוד $k$ שנים\" ו\"לפני $k$ שנים\" בעקביות. למטבעות: $n_A v_A + n_B v_B = \\text{ערך כולל}$."""

WE1_EN = """**Two trains depart from cities 360 km apart, moving toward each other. Train A: 80 km/h. Train B: 100 km/h. When do they meet?**

### Move 1
Identify the pattern: **head-on meeting**. Both trains shrink the gap between cities, so speeds **add**. Let $t$ = hours until meeting.

### Move 2
Combined speed: $80 + 100 = 180$ km/h. The total distance to cover together is the initial separation: 360 km.

### Move 3
Apply $t = d/r$: $t = 360/180 = 2$ hours.

### Move 4
Individual distances: Train A travels $80 \\times 2 = 160$ km; Train B travels $100 \\times 2 = 200$ km.

### Move 5
**Verify:** $160 + 200 = 360$ km ✓. Both times are positive; units are hours.

**Answer:** They meet after **2 hours**. **Strategy:** Meeting problems almost always use $(r_1 + r_2)t = d$ — write that before substituting numbers. On Bagrut, also confirm each train stays within its own track segment if distances from endpoints are requested separately."""

WE1_HE = """**שתי רכבות יוצאות מערים במרחק 360 ק\"מ, נעות זו לקראת זו. רכבת A: 80 ק\"מ/שעה. רכבת B: 100 ק\"מ/שעה. מתי הן נפגשות?**

### צעד 1
זיהוי הדפוס: **מפגש פנים אל פנים**. שתי הרכבות מקטינות את הפער, ולכן המהירויות **מתחברות**. נסמן $t$ = שעות עד המפגש.

### צעד 2
מהירות משולבת: $80 + 100 = 180$ ק\"מ/שעה. המרחק הכולל לכיסוי יחד הוא 360 ק\"מ.

### צעד 3
יישום $t = d/r$: $t = 360/180 = 2$ שעות.

### צעד 4
מרחקים נפרדים: רכבת A נוסעת $80 \\times 2 = 160$ ק\"מ; רכבת B נוסעת $100 \\times 2 = 200$ ק\"מ.

### צעד 5
**אימות:** $160 + 200 = 360$ ק\"מ ✓. זמנים חיוביים; יחידות שעות.

**תשובה:** הן נפגשות אחרי **2 שעות**. **אסטרטגיה:** בעיות מפגש משתמשות כמעט תמיד ב-$(r_1 + r_2)t = d$ — כתבו זאת לפני הצבת מספרים. בבגרות, אמתו גם את המרחק של כל רכב מנקודת ההתחלה שלה אם נדרש בנפרד."""

WE2_EN = """**40 liters of 30% acid solution. How much water must be added to dilute it to 20%?**

### Move 1
Pattern: **dilution by adding pure solvent**. The amount of **acid** (solute) does not change — only total volume and concentration change.

### Move 2
Compute fixed solute: $40 \\times 0.30 = 12$ liters of acid. This stays 12 L throughout.

### Move 3
Let $x$ = liters of water added. New total volume $= 40 + x$. New concentration equation:
$$\\frac{12}{40 + x} = 0.20$$

### Move 4
Cross-multiply: $12 = 0.20(40 + x) = 8 + 0.20x$. So $4 = 0.20x$, hence $x = 20$.

### Move 5
**Verify:** $(40 + 20) \\times 0.20 = 60 \\times 0.20 = 12$ L acid ✓.

**Answer:** Add **20 liters** of water. **Strategy:** In dilution problems, lock the solute amount first, then relate it to the new volume. If the problem instead removes liquid and replaces with pure solvent, each cycle multiplies concentration by $(1 - \\text{fraction removed})$ — a related but distinct pattern worth comparing side by side before the exam."""

WE2_HE = """**40 ליטר תמיסה עם 30% חומצה. כמה מים יש להוסיף כדי להגיע ל-20%?**

### צעד 1
דפוס: **הדללה בהוספת ממס טהור**. כמות **החומצה** (המסיס) לא משתנה — רק הנפח הכולל והריכוז.

### צעד 2
חישוב מסיס קבוע: $40 \\times 0.30 = 12$ ליטר חומצה. זה נשאר 12 ליטר.

### צעד 3
נסמן $x$ = ליטר מים שנוספו. נפח חדש $= 40 + x$. משוואת ריכוז:
$$\\frac{12}{40 + x} = 0.20$$

### צעד 4
כפל צלעות: $12 = 0.20(40 + x) = 8 + 0.20x$. לכן $4 = 0.20x$, ו-$x = 20$.

### צעד 5
**אימות:** $(40 + 20) \\times 0.20 = 60 \\times 0.20 = 12$ ליטר חומצה ✓.

**תשובה:** להוסיף **20 ליטר** מים. **אסטרטגיה:** בהדלה, \"נעלו\" את כמות המסיס קודם, ואז קשרו לנפח החדש. אם הבעיה מורידה נוזל ומחליפה בממס טהור, כל מחזור מכפיל את הריכוז ב-$(1 - \\text{שבר שרוקן})$ — דפוס קרוב אך שונה, שכדאי להשוות לפני הבחינה."""

WE3_EN = """**Today, Sara is 3 times as old as Yossi. In 10 years, Sara will be twice Yossi's age. Find their current ages.**

### Move 1
Define **current** ages: $S$ = Sara today, $Y$ = Yossi today. Both must end up positive integers in context.

### Move 2
Translate "today": Equation 1: $S = 3Y$.

### Move 3
Translate "in 10 years" — **both** ages increase by 10:
$$S + 10 = 2(Y + 10)$$
Expand: $S + 10 = 2Y + 20$, so $S = 2Y + 10$.

### Move 4
Substitute Equation 1 into Equation 2: $3Y = 2Y + 10$, hence $Y = 10$ and $S = 30$.

### Move 5
**Verify today:** $30 = 3 \\times 10$ ✓. **In 10 years:** Sara 40, Yossi 20; $40 = 2 \\times 20$ ✓.

**Answer:** Sara is **30**, Yossi is **10**. **Strategy:** Age problems fail when you shift one person in time but not the other — always add $k$ to **every** age in the future clause."""

WE3_HE = """**היום, שרה בגיל פי 3 מיוסי. עוד 10 שנים, שרה תהיה בגיל פי 2 מיוסי. מצאו את גיליהם הנוכחיים.**

### צעד 1
הגדרת גילאים **נוכחיים**: $S$ = שרה היום, $Y$ = יוסי היום. שניהם חייבים להיות חיוביים.

### צעד 2
תרגום \"היום\": משוואה 1: $S = 3Y$.

### צעד 3
תרגום \"עוד 10 שנים\" — **לשניהם** הגיל עולה ב-10:
$$S + 10 = 2(Y + 10)$$
פתיחה: $S + 10 = 2Y + 20$, כלומר $S = 2Y + 10$.

### צעד 4
הצבה: $3Y = 2Y + 10$, לכן $Y = 10$ ו-$S = 30$.

### צעד 5
**אימות היום:** $30 = 3 \\times 10$ ✓. **בעוד 10 שנים:** שרה 40, יוסי 20; $40 = 2 \\times 20$ ✓.

**תשובה:** שרה **30**, יוסי **10**. **אסטרטגיה:** בעיות גיל נכשלות כשמזיזים אדם אחד בזמן ולא את השני — תמיד הוסיפו $k$ ל**כל** גיל בפסקת העתיד."""

CHK1_EN = """### Move 1
Pattern: basic $d = rt$. Distance $d = 240$ km, rate $r = 60$ km/h. Find time $t$.

### Move 2
Rearrange: $t = d/r = 240/60$.

### Move 3
Compute: $t = 4$ hours.

**Check:** $60 \\times 4 = 240$ km ✓. Units: hours, positive — sensible for a car trip."""

CHK1_HE = """### צעד 1
דפוס: $d = rt$ בסיסי. מרחק $d = 240$ ק\"מ, מהירות $r = 60$ ק\"מ/שעה. מחפשים זמן $t$.

### צעד 2
סידור: $t = d/r = 240/60$.

### צעד 3
חישוב: $t = 4$ שעות.

**בדיקה:** $60 \\times 4 = 240$ ק\"מ ✓. יחידות שעות, חיובי — הגיוני לנסיעה."""

CHK2_EN = """### Move 1
Convert to **rates**: Pipe A fills at $1/6$ tank per hour; Pipe B at $1/4$ per hour.

### Move 2
Combined rate (same job, working together):
$$\\frac{1}{T} = \\frac{1}{6} + \\frac{1}{4} = \\frac{2}{12} + \\frac{3}{12} = \\frac{5}{12}$$

### Move 3
Invert for time: $T = 12/5 = 2.4$ hours (2 hours 24 minutes).

**Check:** In 2.4 h, A does $2.4/6 = 0.4$ of tank, B does $2.4/4 = 0.6$; total $1.0$ ✓."""

CHK2_HE = """### צעד 1
המרה ל**קצבים**: צינור A ממלא $1/6$ מיכל לשעה; B ב-$1/4$ לשעה.

### צעד 2
קצב משולב (אותה עבודה, יחד):
$$\\frac{1}{T} = \\frac{1}{6} + \\frac{1}{4} = \\frac{2}{12} + \\frac{3}{12} = \\frac{5}{12}$$

### צעד 3
הפיכה לזמן: $T = 12/5 = 2.4$ שעות (2 שעות ו-24 דקות).

**בדיקה:** ב-2.4 שעות, A עושה $2.4/6 = 0.4$ מהמיכל, B עושה $2.4/4 = 0.6$; סה\"כ $1.0$ ✓."""

METHOD_EN = """| Problem type | Key equation | Quick cue |
|---|---|---|
| Two objects meeting | $(r_1 + r_2)t = d$ | "toward each other" |
| One catching other | $r_A t = r_B(t - \\Delta t)$ | "starts later / catches up" |
| Opposite from same city | $(r_1 + r_2)t = \\text{separation}$ | "opposite directions" |
| Round trip | $d/r_1 + d/r_2 = T_{\\text{total}}$ | "there and back" |
| Mixture (add liquid) | $m_1 c_1 = (m_1 + x)c_2$ | conserve solute |
| Mix two solutions | $m_1 c_1 + m_2 c_2 = m_f c_f$ | table of amounts |
| Work together | $1/a + 1/b = 1/T$ | "working together" |
| Drain opposing fill | $1/a - 1/b = 1/T$ | "drain open while filling" |
| Age problem | current age $x$; future $x + k$ | "in $k$ years" |
| Percent / discount | $\\text{new} = (1 - p)\\times\\text{original}$ | "after discount" |

**Workflow:** Read → name pattern from table → define variables → one equation per fact → solve → verify units and context."""

METHOD_HE = """| סוג בעיה | משוואת מפתח | רמז מהיר |
|---|---|---|
| מפגש | $(r_1 + r_2)t = d$ | \"זה לקראת זה\" |
| מרדף | $r_A t = r_B(t - \\Delta t)$ | \"מתחיל מאוחר / משיג\" |
| כיוונים מנוגדים | $(r_1 + r_2)t = \\text{מרחק}$ | \"לכיוונים הפוכים\" |
| הלוך-חזור | $d/r_1 + d/r_2 = T$ | \"הלוך ושוב\" |
| תערובת (הוספה) | $m_1 c_1 = (m_1 + x)c_2$ | שימור מסיס |
| ערבוב שתי תמיסות | $m_1 c_1 + m_2 c_2 = m_f c_f$ | טבלת כמויות |
| עבודה משותפת | $1/a + 1/b = 1/T$ | \"עובדים יחד\" |
| ניקוז מול מילוי | $1/a - 1/b = 1/T$ | \"ניקוז פתוח\" |
| גיל | גיל נוכחי $x$; עתיד $x + k$ | \"בעוד $k$ שנים\" |
| אחוז / הנחה | $\\text{חדש} = (1 - p)\\times\\text{מקורי}$ | \"אחרי הנחה\" |

**תהליך:** קריאה → זיהוי דפוס מהטבלה → הגדרת משתנים → משוואה לכל עובדה → פתרון → אימות יחידות והקשר."""

PITFALL_EN = """1. **Vague variables.** Write "Let $t$ = hours until they meet" — not just "$t$". Examiners deduct when the meaning is unclear.

2. **Skipping context check.** Negative time, negative width, or age 0 means you mis-translated — rework the setup, not just the arithmetic.

3. **Mixture: confusing volume with solute.** Adding water increases total liters; acid/salt grams stay fixed until you drain some solution.

4. **Work: averaging times.** Combined time is **not** $(a + b)/2$. Rates add: $1/T = 1/a + 1/b$. Example: 6 h and 3 h together → 2 h, not 4.5 h.

5. **Distance: wrong relative speed.** Toward each other → **add** speeds. Same direction catch-up → **subtract**. Opposite from same start → **add** for separation.

6. **Age: shifting only one person.** "In 5 years" means **everyone** is 5 years older in that clause."""

PITFALL_HE = """1. **משתנים מעורפלים.** כתבו \"נסמן $t$ = שעות עד המפגש\" — לא רק \"$t$\". בוחנים מורידים כשהמשמעות לא ברורה.

2. **דילוג על בדיקת הקשר.** זמן שלילי, רוחב שלילי או גיל 0 — התרגום שגוי; חזרו להגדרה, לא רק לחישוב.

3. **תערובת: בלבול נפח ומסיס.** הוספת מים מגדילה ליטרים; גרמים של חומצה/מלח נשארים קבועים עד שרוקנים תמיסה.

4. **עבודה: ממוצע זמנים.** זמן משותף **אינו** $(a + b)/2$. קצבים מתחברים: $1/T = 1/a + 1/b$. דוגמה: 6 ו-3 שעות יחד → 2 שעות, לא 4.5.

5. **מרחק: מהירות יחסית שגויה.** זה לקראת זה → **חיבור** מהירויות. מרדף → **חיסור**. כיוונים מנוגדים מאותה נקודה → **חיבור** להתרחקות.

6. **גיל: הזזת אדם אחד בלבד.** \"בעוד 5 שנים\" = **כולם** מבוגרים ב-5 באותה פסקה."""

WHY_EN = """Word problems are where algebra proves it is **useful**, not abstract. Every physics formula you will meet — motion, fluids, circuits — starts life as a word problem with units.

On **Bagrut** and **מכינה** exams, applied questions carry heavy weight because they test **transfer**: can you recognize a pattern inside a paragraph? That skill also appears in data interpretation, economics word problems, and lab report analysis.

On **A Step Forward**, this lesson connects to linear equations, systems, rational expressions, and later kinematics in physics. Tutors will ask you to explain **why** your answer fits the story — not just show algebra."""

WHY_HE = """בעיות מילוליות הן המקום שבו האלגברה מוכיחה שהיא **שימושית**, לא מופשטת. כל נוסחת פיזיקה — תנועה, זרימה, מעגלים — מתחילה כבעיה מילולית עם יחידות.

**בבגרות** וב**מכינה**, שאלות יישום שוקלות הרבה כי הן בודקות **העברה**: האם מזהים דפוס בתוך פסקה? מיומנות זו מופיעה גם בפרשנות נתונים, כלכלה ובדוחות מעבדה.

**ב-A Step Forward**, שיעור זה מחובר למשוואות לינאריות, מערכות, ביטויים רציונליים וקינמטיקה בפיזיקה. המורים יבקשו להסביר **למה** התשובה מתאימה לסיפור — לא רק להציג אלגברה."""

BEFORE_EN = """**Night-before checklist:**
- $d = rt$; meeting $\\Rightarrow$ add speeds; catch-up $\\Rightarrow$ equal distances
- Mixture: **solute conserved**; table: volume × concentration = amount
- Work: convert to rates $1/a$; together = add; drain = subtract from fill
- Age: variable = **today**; future/past = $\\pm k$ for **everyone** in that sentence
- Percent discount: paid price = $(1 - p) \\times$ original

**60-second drill:** Say each bullet once, then solve one checkpoint without notes. If you hesitate on "add or subtract speeds," redo the distance theory section. Bring one blank table for mixture problems — examiners expect organized solute rows, not scattered arithmetic."""

BEFORE_HE = """**רשימת לילה לפני בחינה:**
- $d = rt$; מפגש $\\Rightarrow$ חיבור מהירויות; מרדף $\\Rightarrow$ מרחקים שווים
- תערובת: **מסיס נשמר**; טבלה: נפח × ריכוז = כמות
- עבודה: קצבים $1/a$; יחד = חיבור; ניקוז = חיסור ממילוי
- גיל: משתנה = **היום**; עתיד/עבר = $\\pm k$ ל**כולם** באותו משפט
- הנחה: מחיר ששולם = $(1 - p) \\times$ מקורי

**תרגול 60 שניות:** אמרו כל נקודה פעם אחת, ואז פתרו checkpoint בלי רשימה. אם נתקעים ב\"חיבור או חיסור מהירויות\" — חזרו לתיאוריה של מרחק."""

SUMMARY_EN = """- **Framework:** Read → define → equation(s) → solve → verify in context
- **Distance:** $d = rt$; meeting uses $(r_1 + r_2)t = d$
- **Mixture:** conserve solute; dilution fixes amount, changes volume
- **Work:** rates add; $1/T = 1/a + 1/b$ (fill + fill) or $1/a - 1/b$ (fill + drain)
- **Age:** anchor at today; shift all ages together in time clauses
- **Pitfall guard:** never average work times; never leave variables undefined

**Takeaway:** Name the pattern first — the equation follows from the story, not the other way around."""

SUMMARY_HE = """- **מסגרת:** קריאה → הגדרה → משוואה(ות) → פתרון → אימות בהקשר
- **מרחק:** $d = rt$; מפגש: $(r_1 + r_2)t = d$
- **תערובת:** שימור מסיס; הדלה קובעת כמות, משנה נפח
- **עבודה:** קצבים מתחברים; $1/T = 1/a + 1/b$ (מילוי+מילוי) או $1/a - 1/b$ (מילוי+ניקוז)
- **גיל:** עוגן בהיום; הזיזו את כל הגילאים יחד בפסקות זמן
- **מלכודות:** לא ממוצעים זמני עבודה; לא משאירים משתנים לא מוגדרים

**מסקנה:** קודם שם הדפוס — המשוואה נגזרת מהסיפור, לא להפך."""

EXPLS = {
    1: fmt_expl(
        "Pipe A fills at $1/6$ tank/hour and B at $1/3$ tank/hour. Together: $1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2$ tank per hour. So the full tank takes $T = 1/(1/2) = 2$ hours.",
        "Recognize **combined work**: convert each pipe to a rate (job per hour), then add. The MCQ distractors often average times ($4.5$ h) or pick the faster pipe alone ($3$ h).",
        "Using $(6 + 3)/2 = 4.5$ hours — work times do **not** average. Or taking only pipe B's time because it is faster.",
        "Write $1/T = 1/a + 1/b$ on scratch paper before substituting. If the sum of rates is $1/2$, invert mentally: time = 2 h.",
        "צינור A ממלא $1/6$ מיכל לשעה ו-B ב-$1/3$. יחד: $1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2$ מיכל לשעה. מיכל מלא: $T = 1/(1/2) = 2$ שעות.",
        "זיהוי **עבודה משותפת**: המירו כל צינור לקצב (עבודה לשעה), וחברו. מסיחים במבחן: ממוצע זמנים ($4.5$ ש') או רק הצינור המהיר ($3$ ש').",
        "שימוש ב-$(6 + 3)/2 = 4.5$ שעות — זמני עבודה **לא** ממוצעים. או לקיחת זמן B בלבד כי הוא מהיר יותר.",
        "כתבו $1/T = 1/a + 1/b$ בטיוטה לפני הצבה. אם סכום הקצבים $1/2$, הפכו: זמן = 2 שעות.",
    ),
    2: fmt_expl(
        "This is the base formula $d = r \\times t$ with $r = 15$ km/h and $t = 3$ h. Distance $d = 15 \\times 3 = 45$ km.",
        "Identify **distance–rate–time** directly — no system needed. Ask: are you finding $d$, $r$, or $t$? Here distance is unknown; multiply rate by time.",
        "Dividing $15/3 = 5$ (swapping multiply/divide) or adding $15 + 3 = 18$ instead of multiplying.",
        "Always write units in the final answer: 45 **km**. One-line problems still deserve the five-step check: does $45/15 = 3$ h?",
        "זו הנוסחה $d = r \\times t$ עם $r = 15$ ק\"מ/שעה ו-$t = 3$ ש'. מרחק $d = 15 \\times 3 = 45$ ק\"מ.",
        "זיהוי **מרחק–מהירות–זמן** ישירות — בלי מערכת. שאלו: מחפשים $d$, $r$ או $t$? כאן המרחק לא ידוע; כופלים מהירות בזמן. זהו הבסיס לכל בעיות התנועה.",
        "חילוק $15/3 = 5$ (החלפת כפל/חילוק) או חיבור $15 + 3 = 18$ במקום כפל.",
        "כתבו יחידות בתשובה: 45 **ק\"מ**. גם בעיה קצרה ראויה לבדיקה: האם $45/15 = 3$ ש'? אם מבקשים זמן, חלקו מרחק במהירות — לא להפך.",
    ),
    3: fmt_expl(
        "Let son's age $= x$. Tom is $4x$. Sum: $x + 4x = 40$, so $5x = 40$ and $x = 8$. Tom $= 32$. Check: $8 + 32 = 40$ and $32 = 4 \\times 8$.",
        "Age + ratio + sum → one variable for the **younger** person. Translate \"4 times older\" as multiplier 4 on the son's age, not adding 4 years.",
        "Setting Tom $= x$ and son $= x/4$ without checking the sum equation, or using $x + 4$ instead of $4x$ for the ratio.",
        "After solving, verify **both** conditions from the stem (sum AND ratio). Bagrut often hides a second check to catch partial setups.",
        "גיל הבן $= x$. טום $= 4x$. סכום: $x + 4x = 40$, כלומר $5x = 40$ ו-$x = 8$. טום $= 32$. בדיקה: $8 + 32 = 40$ ו-$32 = 4 \\times 8$.",
        "גיל + יחס + סכום → משתנה אחד ל**צעיר** יותר. \"פי 4\" = מכפיל 4 על גיל הבן, לא הוספת 4 שנים.",
        "הגדרת טום $= x$ ובן $= x/4$ בלי משוואת סכום, או $x + 4$ במקום $4x$ ליחס.",
        "אחרי הפתרון, אמתו **שני** התנאים (סכום **וגם** יחס). בבגרות לעיתים מסתירים בדיקה שנייה.",
    ),
    4: fmt_expl(
        "If the machine completes the job in 8 hours, it finishes $1/8$ of the total job each hour. Rate $= 1/8$ job/hour — a **unit rate** for work problems.",
        "Convert \"hours per job\" to \"jobs per hour\" by taking the reciprocal. This is the same mindset as pipes filling tanks: 6 hours alone → rate $1/6$.",
        "Answering 8 (the hours) instead of $1/8$ (the rate), or saying \"8 boxes per hour\" when the problem asks for a **fraction** of the total.",
        "When a stem asks \"fraction of total per hour,\" write $1/a$ immediately. Save the number 8 for time-to-finish questions, not rate questions.",
        "אם המכונה מסיימת ב-8 שעות, היא מסיימת $1/8$ מהעבודה כל שעה. קצב $= 1/8$ עבודה/שעה — **קצב יחידה** לבעיות עבודה, בדיוק כמו צינור שממלא מיכל.",
        "המרת \"שעות לעבודה\" ל\"עבודות לשעה\" באמצעות הופכי. אותה גישה כמו צינורים: 6 שעות לבד → קצב $1/6$. שאלו: \"כמה מהמשימה בכל שעה?\"",
        "תשובה 8 (השעות) במקום $1/8$ (הקצב), או \"8 קופסאות לשעה\" כששואלים **שבר** מהסך. אל תערבבו יחידות של זמן עם יחידות של קצב.",
        "כששואלים \"שבר מהסך לשעה\", כתבו $1/a$ מיד. השמרו 8 לשאלות זמן-סיום, לא לקצב. בדיקה: $8 \\times (1/8) = 1$ עבודה שלמה.",
    ),
    5: fmt_expl(
        "After 20% off, the customer pays 80% of original: $\\text{original} \\times 0.8 = 96$. So original $= 96/0.8 = 120$ ₪. Check: $120 \\times 0.8 = 96$.",
        "Percent discount is a **word problem** on multiplication — identify what 96 represents (discounted price, not original). Translate \"20% off\" as multiply by 0.8, not subtract 20.",
        "Subtracting 20 from 96 ($76$) or adding 20% of 96 to 96 — confusing discount **on** original vs **from** sale price.",
        "On discount problems, always ask: \"96 is what percent of original?\" If 80%, divide by 0.8. State answer in ₪ with context check.",
        "אחרי 20% הנחה, הלקוח משלם 80% מהמקור: $\\text{מקורי} \\times 0.8 = 96$. לכן מקורי $= 96/0.8 = 120$ ₪. בדיקה: $120 \\times 0.8 = 96$.",
        "הנחה באחוזים היא **בעיה מילולית** על כפל — 96 הוא המחיר אחרי הנחה, לא המקורי. \"20% הנחה\" = כפל ב-0.8, לא חיסור 20.",
        "חיסור 20 מ-96 ($76$) או הוספת 20% מ-96 — בלבול הנחה **על** מקורי לעומת **מהמחיר**.",
        "בהנחות, שאלו: \"96 זה כמה אחוז מהמקור?\" אם 80%, חלקו ב-0.8. ציינו ₪ עם בדיקת הקשר.",
    ),
    6: fmt_expl(
        "Opposite directions from the same city: separation speed $= 70 + 90 = 160$ km/h. Distance apart after $t$ hours: $160t = 480$, so $t = 480/160 = 3$ hours.",
        "Keywords \"opposite directions\" signal **add speeds** for how fast the gap grows. Do not use meeting-from-ends unless two starting cities are given.",
        "Using $70 - 90$ (catch-up subtraction) or dividing 480 by only one car's speed. Another trap: $480/70$ because car A is mentioned first.",
        "Sketch a number line: both cars move apart, gap widens at $r_1 + r_2$. Verify: $(70 + 90) \\times 3 = 480$ km.",
        "כיוונים מנוגדים מאותה עיר: מהירות התרחקות $= 70 + 90 = 160$ ק\"מ/שעה. מרחק אחרי $t$ שעות: $160t = 480$, כלומר $t = 3$ שעות.",
        "מילות מפתח \"כיוונים מנוגדים\" = **חיבור מהירויות** לקצב גידול הפער. לא מפגש מקצוות אלא אם ניתנו שתי ערים.",
        "שימוש ב-$70 - 90$ (חיסור מרדף) או חילוק 480 רק במהירות מכונית אחת. מלכודת: $480/70$ כי A מוזכר ראשון.",
        "שרטוט ציר: שתי מכוניות מתרחקות, הפער גדל ב-$r_1 + r_2$. אימות: $(70 + 90) \\times 3 = 480$ ק\"מ. אם נתון מרחק התחלתי בין ערים — זו בעיית מפגש, לא התרחקות.",
    ),
    7: fmt_expl(
        "Let $x$ = liters of 80% solution. Solute balance: $0.8x + 0.4(20) = 0.6(x + 20)$. Left: pure alcohol amounts; right: final concentration × total volume. Solve: $0.8x + 8 = 0.6x + 12$, so $0.2x = 4$ and $x = 20$ L.",
        "Mixture → **table**: row for each solution, column \"amount × % = solute liters.\" Final row uses $(x + 20)$ liters at 60%.",
        "Using $0.8x + 0.4 = 0.6$ (dropping the 20 L volume) or averaging 80% and 40% to get 60% without weighted volumes.",
        "Check solute: $0.8(20) + 0.4(20) = 16 + 8 = 24$ L; final $0.6(40) = 24$ L ✓. Weighted average needs **amounts**, not plain mean of percents.",
        "נסמן $x$ = ליטר תמיסה 80%. שיווי מסיס: $0.8x + 0.4(20) = 0.6(x + 20)$. שמאל: כמויות אלכוהול; ימין: ריכוז סופי × נפח. פתרון: $0.8x + 8 = 0.6x + 12$, $0.2x = 4$, $x = 20$ ל'.",
        "תערובת → **טבלה**: שורה לכל תמיסה, עמודה \"נפח × % = ליטר מסיס\". שורה סופית: $(x + 20)$ ליטר ב-60%.",
        "שימוש ב-$0.8x + 0.4 = 0.6$ (השמטת 20 ל') או ממוצע 80% ו-40% בלי משקל נפחים.",
        "בדיקת מסיס: $0.8(20) + 0.4(20) = 24$ ל'; סופי $0.6(40) = 24$ ✓. ממוצע משוקלל דורש **כמויות**, לא ממוצע אחוזים.",
    ),
    8: fmt_expl(
        "Fill rate $= 1/12$ pool/hour; drain rate $= 1/18$ pool/hour (opposing). Net: $1/12 - 1/18 = 3/36 - 2/36 = 1/36$ pool/hour. Time to fill: $T = 36$ hours.",
        "Drain **opposes** fill → subtract rates after converting both to \"pool per hour.\" If net rate were negative, the pool would never fill — sanity check sign.",
        "Adding $1/12 + 1/18$ as if both fill, giving 7.2 h. Or inverting the wrong fraction and answering $1/36$ hours.",
        "Label pipes F (+) and D (−) on scratch paper. Net $1/36$ means slow fill — expect a large T. Confirm: in 36 h, fill contributes 3 pools' worth, drain removes 2, net +1.",
        "קצב מילוי $= 1/12$ בריכה/שעה; ניקוז $= 1/18$ (מנגד). נטו: $1/12 - 1/18 = 3/36 - 2/36 = 1/36$ בריכה/שעה. זמן מילוי: $T = 36$ שעות.",
        "ניקוז **מתנגד** למילוי → חיסור קצבים אחרי המרה ל\"בריכה לשעה\". אם נטו שלילי — הבריכה לא תתמלא; בדקו סימן.",
        "חיבור $1/12 + 1/18$ כאילו שניהם ממלאים (7.2 ש'). או היפוך שגוי ותשובה $1/36$ שעות.",
        "סמנו F (+) ו-D (−) בטיוטה. נטו $1/36$ = מילוי איטי — T גדול. אימות: ב-36 ש', מילוי תורם 3, ניקוז מוריד 2, נטו +1.",
    ),
}


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        sid = sec.get("id", kind)
        if kind not in EXPAND_KINDS:
            if kind == "checkpoint":
                for key in ("checkpoint_solution_en", "checkpoint_solution_he"):
                    if wc(sec.get(key, "")) < 25:
                        errors.append(f"{sid}: {key} too short ({wc(sec.get(key, ''))} words)")
            continue
        min_key = "worked_example" if kind == "worked_example" else kind
        en_min, he_min = MIN[min_key]
        en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
        if en_w < en_min:
            errors.append(f"{sid}: EN {en_w} < {en_min}")
        if he_w < he_min:
            errors.append(f"{sid}: HE {he_w} < {he_min}")
        if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
            errors.append(f"{sid}: weak Hebrew")
    for q in data["questions"]:
        ew, hw = wc(q.get("explanation_en", "")), wc(q.get("explanation_he", ""))
        if ew < 80:
            errors.append(f"q{q['ord']} expl-en {ew} < 80")
        if ew > 150:
            errors.append(f"q{q['ord']} expl-en {ew} > 150")
        if hw < 80:
            errors.append(f"q{q['ord']} expl-he {hw} < 80")
        if hw > 150:
            errors.append(f"q{q['ord']} expl-he {hw} > 150")
        if he_weak(q.get("explanation_he", ""), q.get("explanation_en", "")):
            errors.append(f"q{q['ord']}: weak Hebrew expl")
    return errors


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    data["summary_en"] = (
        "Word problems: translate real situations into algebra using distance–rate–time, "
        "mixture conservation, work rates, and age shifts — with a five-step verify-in-context method."
    )
    data["summary_he"] = (
        "בעיות מילוליות: תרגום מציאות לאלגברה עם מרחק–מהירות–זמן, שימור תערובות, "
        "קצבי עבודה והזזות גיל — בשיטת חמישה שלבים עם אימות בהקשר."
    )

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec["body_en_md"] = INTRO_EN
            sec["body_he_md"] = INTRO_HE
        elif kind == "definition":
            sec["body_en_md"] = DEF_EN
            sec["body_he_md"] = DEF_HE
        elif kind == "theory":
            sec["body_en_md"] = THEORY_EN
            sec["body_he_md"] = THEORY_HE
        elif kind == "worked_example":
            n = sec.get("example_number", 1)
            if n == 1:
                sec["body_en_md"], sec["body_he_md"] = WE1_EN, WE1_HE
            elif n == 2:
                sec["body_en_md"], sec["body_he_md"] = WE2_EN, WE2_HE
            elif n == 3:
                sec["body_en_md"], sec["body_he_md"] = WE3_EN, WE3_HE
        elif kind == "checkpoint":
            if "240 km" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CHK1_EN
                sec["checkpoint_solution_he"] = CHK1_HE
            else:
                sec["checkpoint_solution_en"] = CHK2_EN
                sec["checkpoint_solution_he"] = CHK2_HE
        elif kind == "method_guide":
            sec["body_en_md"] = METHOD_EN
            sec["body_he_md"] = METHOD_HE
        elif kind == "pitfall":
            sec["body_en_md"] = PITFALL_EN
            sec["body_he_md"] = PITFALL_HE
        elif kind == "why_matters":
            sec["body_en_md"] = WHY_EN
            sec["body_he_md"] = WHY_HE
        elif kind == "before_exam":
            sec["body_en_md"] = BEFORE_EN
            sec["body_he_md"] = BEFORE_HE
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY_EN
            sec["body_he_md"] = SUMMARY_HE

    atom_map = {
        1: ["work_rate", "combined_work"],
        2: ["distance_rate_time"],
        3: ["age_problems", "word_problem_setup"],
        4: ["work_rate_problems"],
        5: ["word_problem_setup"],
        6: ["distance_rate_time", "meeting_problems"],
        7: ["mixture_problems"],
        8: ["work_rate_problems"],
    }
    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]
        if ord_ in atom_map:
            q["skill_atoms"] = atom_map[ord_]

    errs = validate(data)
    if errs:
        print("Validation errors:")
        for e in errs:
            print(" ", e)
        raise SystemExit(1)

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
