#!/usr/bin/env python3
"""Expand probability_basic.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/probability_basic.json"

EXERCISES = [
    {
        "id": "e1",
        "solution_en": "**Step 1 — Sample space.** $\\Omega=\\{1,2,3,4,5,6\\}$, $|\\Omega|=6$, each outcome probability $1/6$.\n\n**Step 2 — Even outcomes.** $A=\\{2,4,6\\}$, $|A|=3$, so $P(\\text{even})=3/6=1/2$.\n\n**Step 3 — Greater than 4.** $B=\\{5,6\\}$, $|B|=2$, so $P(>4)=2/6=1/3$.\n\n**Check:** $1/2+1/3\\neq1$ because the events overlap on 6 — they are not disjoint.",
        "solution_he": "**שלב 1 — מרחב מדגם.** $\\Omega=\\{1,2,3,4,5,6\\}$, $|\\Omega|=6$, כל תוצאה בהסתברות $1/6$.\n\n**שלב 2 — תוצאות זוגיות.** $A=\\{2,4,6\\}$, $|A|=3$, ולכן $P(\\text{זוגי})=3/6=1/2$.\n\n**שלב 3 — גדול מ-4.** $B=\\{5,6\\}$, $|B|=2$, ולכן $P(>4)=2/6=1/3$.\n\n**בדיקה:** $1/2+1/3\\neq1$ כי המאורעות חופפים על 6 — הם לא זרים.",
    },
    {
        "id": "e2",
        "solution_en": "**Step 1 — Identify disjoint events.** \"Mutually exclusive\" means $A\\cap B=\\emptyset$, so $P(A\\cap B)=0$.\n\n**Step 2 — Apply inclusion-exclusion.** $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)=0.4+0.3-0=0.7$.\n\n**Check:** $0.7\\leq1$ and exceeds both marginals — valid union probability.",
        "solution_he": "**שלב 1 — זיהוי מאורעות זרים.** \"זרים\" פירושו $A\\cap B=\\emptyset$, ולכן $P(A\\cap B)=0$.\n\n**שלב 2 — הכלה-הדרה.** $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)=0.4+0.3-0=0.7$.\n\n**בדיקה:** $0.7\\leq1$ וגדול משני ההסתברויות השוליות — תקין.",
    },
    {
        "id": "e3",
        "solution_en": "**Step 1 — Classical probability setup.** $|\\Omega|=10$ equally likely people; $|A|=6$ women.\n\n**Step 2 — Compute.** $P(\\text{woman})=6/10=0.6$.\n\n**Check:** Women are the majority (6 of 10), so $P>0.5$ is sensible.",
        "solution_he": "**שלב 1 — הסתברות קלאסית.** $|\\Omega|=10$ אנשים שווי-הסתברות; $|A|=6$ נשים.\n\n**שלב 2 — חישוב.** $P(\\text{אישה})=6/10=0.6$.\n\n**בדיקה:** נשים הן הרוב (6 מתוך 10), ולכן $P>0.5$ הגיוני.",
    },
    {
        "id": "e4",
        "solution_en": "**Step 1 — Independence test.** Compute $P(A)P(B)=\\frac{1}{2}\\cdot\\frac{1}{2}=\\frac{1}{4}$.\n\n**Step 2 — Compare with intersection.** Given $P(A\\cap B)=\\frac{1}{3}$. Since $\\frac{1}{4}\\neq\\frac{1}{3}$, events are **dependent**.\n\n**Interpretation:** Even and $>3$ overlap on $\\{4,6\\}$ — knowing one outcome restricts the other.",
        "solution_he": "**שלב 1 — בדיקת אי-תלות.** חשבו $P(A)P(B)=\\frac{1}{2}\\cdot\\frac{1}{2}=\\frac{1}{4}$.\n\n**שלב 2 — השוו לחיתוך.** נתון $P(A\\cap B)=\\frac{1}{3}$. מכיוון ש-$\\frac{1}{4}\\neq\\frac{1}{3}$, המאורעות **תלויים**.\n\n**פרשנות:** \"זוגי\" ו\">3\" חופפים על $\\{4,6\\}$ — ידיעה על מאורע אחד מגבילה את השני.",
    },
    {
        "id": "e5",
        "solution_en": "**Part (a) — Joint probability.** From $P(A|B)=P(A\\cap B)/P(B)$, rearrange: $P(A\\cap B)=0.6\\times0.5=0.3$.\n\n**Part (b) — Reverse conditioning.** $P(B|A)=P(A\\cap B)/P(A)=0.3/0.3=1.0$.\n\n**Interpretation:** $P(B|A)=1$ means $A\\subseteq B$ — whenever $A$ occurs, $B$ must also occur. Note $A$ and $B$ are **not** independent since $P(A)P(B)=0.15\\neq0.3$.",
        "solution_he": "**חלק (א) — הסתברות משותפת.** מ-$P(A|B)=P(A\\cap B)/P(B)$: $P(A\\cap B)=0.6\\times0.5=0.3$.\n\n**חלק (ב) — תנאי הפוך.** $P(B|A)=P(A\\cap B)/P(A)=0.3/0.3=1.0$.\n\n**פרשנות:** $P(B|A)=1$ פירושו $A\\subseteq B$ — בכל פעם ש-$A$ מתרחש, גם $B$ חייב. שימו לב: $A$ ו-$B$ **לא** בלתי-תלויים כי $P(A)P(B)=0.15\\neq0.3$.",
    },
    {
        "id": "e6",
        "solution_en": "**Step 1 — Partition.** $M_1$ (60% production), $M_2$ (40% production) partition the sample space.\n\n**Step 2 — Law of total probability.**\n$$P(D)=P(D|M_1)P(M_1)+P(D|M_2)P(M_2)=0.02\\times0.6+0.05\\times0.4=0.012+0.020=0.032.$$\n\n**Check:** $3.2\\%$ lies between the two defect rates and closer to $2\\%$ because Machine 1 dominates output.",
        "solution_he": "**שלב 1 — חלוקה.** $M_1$ (60% ייצור), $M_2$ (40% ייצור) מחלקים את מרחב המדגם.\n\n**שלב 2 — חוק ההסתברות הכוללת.**\n$$P(D)=P(D|M_1)P(M_1)+P(D|M_2)P(M_2)=0.02\\times0.6+0.05\\times0.4=0.012+0.020=0.032.$$\n\n**בדיקה:** $3.2\\%$ בין שני שיעורי הפגם וקרוב יותר ל-$2\\%$ כי מכונה 1 שולטת בייצור.",
    },
    {
        "id": "e7",
        "solution_en": "**Step 1 — Joint from Machine 1.** $P(D\\cap M_1)=P(D|M_1)P(M_1)=0.02\\times0.6=0.012$.\n\n**Step 2 — Bayes' theorem.** $P(M_1|D)=0.012/0.032=0.375=37.5\\%$.\n\n**Interpretation:** Despite producing 60% of items, Machine 1 accounts for only 37.5% of defects because its defect rate is lower.",
        "solution_he": "**שלב 1 — חיתוך ממכונה 1.** $P(D\\cap M_1)=P(D|M_1)P(M_1)=0.02\\times0.6=0.012$.\n\n**שלב 2 — משפט בייס.** $P(M_1|D)=0.012/0.032=0.375=37.5\\%$.\n\n**פרשנות:** למרות 60% מהייצור, מכונה 1 תורמת רק 37.5% מהפגמים כי שיעור הפגם בה נמוך.",
    },
    {
        "id": "e8",
        "solution_en": "**Step 1 — Start from inclusion-exclusion.** $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)$.\n\n**Step 2 — Use $P(A\\cup B)\\leq1$.** Rearrange: $P(A\\cap B)\\geq P(A)+P(B)-1$. $\\blacksquare$\n\n**Example:** If $P(A)=P(B)=0.9$, then $P(A\\cap B)\\geq0.8$ — high overlap is forced.",
        "solution_he": "**שלב 1 — התחילו מהכלה-הדרה.** $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)$.\n\n**שלב 2 — השתמשו ב-$P(A\\cup B)\\leq1$.** סידור: $P(A\\cap B)\\geq P(A)+P(B)-1$. $\\blacksquare$\n\n**דוגמה:** אם $P(A)=P(B)=0.9$, אז $P(A\\cap B)\\geq0.8$ — חפיפה גבוהה נדרשת.",
    },
    {
        "id": "e9",
        "solution_en": "**Step 1 — Compute $P(+)$ via total probability.**\n$$P(+)=P(+|D)P(D)+P(+|D^c)P(D^c)=0.98\\times0.005+0.03\\times0.995=0.0049+0.02985=0.03475.$$\n\n**Step 2 — Bayes for disease given positive.** $P(D|+)=0.0049/0.03475\\approx0.141=14.1\\%$.\n\n**Step 3 — Negative test.** $P(-)=1-0.03475=0.96525$. $P(D^c|-)=P(-|D^c)P(D^c)/P(-)=0.97\\times0.995/0.96525\\approx0.9998$.\n\n**Interpretation:** Rare disease (0.5%) means most positives are false alarms; a negative result is highly reassuring.",
        "solution_he": "**שלב 1 — חישוב $P(+)$ בחוק הכוללת.**\n$$P(+)=0.98\\times0.005+0.03\\times0.995=0.0049+0.02985=0.03475.$$\n\n**שלב 2 — בייס לחולה בהינתן חיובי.** $P(D|+)\\approx0.141=14.1\\%$.\n\n**שלב 3 — בדיקה שלילית.** $P(-)=0.96525$. $P(D^c|-)\\approx0.9998$.\n\n**פרשנות:** מחלה נדירה (0.5%) — רוב החיוביים שגויים; שלילי מרגיע מאוד.",
    },
    {
        "id": "e11",
        "solution_en": "**Step 1 — Decompose $A\\cap B^c$.** $A\\cap B^c = A\\setminus B$, so $P(A\\cap B^c)=P(A)-P(A\\cap B)$.\n\n**Step 2 — Use independence.** $P(A\\cap B^c)=P(A)-P(A)P(B)=P(A)(1-P(B))=P(A)P(B^c)$. $\\blacksquare$\n\n**Consequence:** Independence of $A$ and $B$ implies independence of $A$ and $B^c$, $A^c$ and $B$, and $A^c$ and $B^c$.",
        "solution_he": "**שלב 1 — פירוק $A\\cap B^c$.** $A\\cap B^c = A\\setminus B$, ולכן $P(A\\cap B^c)=P(A)-P(A\\cap B)$.\n\n**שלב 2 — אי-תלות.** $P(A\\cap B^c)=P(A)-P(A)P(B)=P(A)(1-P(B))=P(A)P(B^c)$. $\\blacksquare$\n\n**מסקנה:** אי-תלות של $A$ ו-$B$ גוררת אי-תלות של $A$ ו-$B^c$, $A^c$ ו-$B$, ו-$A^c$ ו-$B^c$.",
    },
    {
        "id": "e12",
        "solution_en": "**Step 1 — Decompose $A$.** Since $\\{B_i\\}$ partition $\\Omega$: $A=A\\cap\\Omega=A\\cap(\\bigcup_i B_i)=\\bigcup_i(A\\cap B_i)$.\n\n**Step 2 — Disjoint union.** Sets $A\\cap B_i$ are mutually exclusive (the $B_i$ are disjoint).\n\n**Step 3 — Additivity + conditioning.** $P(A)=\\sum_i P(A\\cap B_i)=\\sum_i P(A|B_i)P(B_i)$. $\\blacksquare$",
        "solution_he": "**שלב 1 — פירוק $A$.** מכיוון ש-$\\{B_i\\}$ מחלקים את $\\Omega$: $A=A\\cap\\Omega=A\\cap(\\bigcup_i B_i)=\\bigcup_i(A\\cap B_i)$.\n\n**שלב 2 — איחוד זר.** הקבוצות $A\\cap B_i$ זרות (ה-$B_i$ זרים).\n\n**שלב 3 — אדיטיביות + מותנית.** $P(A)=\\sum_i P(A\\cap B_i)=\\sum_i P(A|B_i)P(B_i)$. $\\blacksquare$",
    },
]

THEORY_EN_APPEND = """

**Theorem 5 (Law of total probability — proof sketch).** If $B_1,\\ldots,B_n$ partition $\\Omega$, then $P(A)=\\sum_i P(A|B_i)P(B_i)$.
*Proof:* Write $A=\\bigcup_i(A\\cap B_i)$ as a disjoint union. Apply countable additivity and the definition $P(A\\cap B_i)=P(A|B_i)P(B_i)$. $\\blacksquare$

**Theorem 6 (Multiplication rule).** For events with $P(B)>0$: $P(A\\cap B)=P(A|B)P(B)=P(B|A)P(A)$.
*Use:* Chain conditional probabilities along a tree — e.g. $P(A\\cap B\\cap C)=P(A|B\\cap C)P(B|C)P(C)$ when each condition is valid.

**Worked strategy for compound problems:** (1) Draw a tree or table listing every branch. (2) Label branch probabilities (they must sum to 1 at each split). (3) Multiply along paths for intersections; add across disjoint paths for unions or totals. (4) For \"given that\" questions, restrict to the relevant branch and re-normalise — this is Bayes in disguise."""

THEORY_HE_APPEND = """

**משפט 5 (חוק ההסתברות הכוללת — ראייה).** אם $B_1,\\ldots,B_n$ מחלקים את $\\Omega$, אז $P(A)=\\sum_i P(A|B_i)P(B_i)$.
*הוכחה:* כתבו $A=\\bigcup_i(A\\cap B_i)$ כאיחוד זר. יישמו אדיטיביות והגדרה $P(A\\cap B_i)=P(A|B_i)P(B_i)$. $\\blacksquare$

**משפט 6 (כלל הכפל).** למאורעות עם $P(B)>0$: $P(A\\cap B)=P(A|B)P(B)=P(B|A)P(A)$.
*שימוש:* שרשרו הסתברויות מותנות לאורך עץ — למשל $P(A\\cap B\\cap C)=P(A|B\\cap C)P(B|C)P(C)$ כשכל תנאי תקף.

**אסטרטגיה לבעיות מורכבות:** (1) שרטטו עץ או טבלה עם כל ענף. (2) סמנו הסתברויות ענף (חייבות להסתכם ל-1 בכל פיצול). (3) כפלו לאורך מסלולים לחיתוכים; חברו על מסלולים זרים לאיחודים או סכומים. (4) לשאלות \"בהינתן ש-\" — הגבילו לענף הרלוונטי ונרמלו מחדש; זה בייס ב disguise."""

QUESTION_EXPL_PATCHES = {
    2: {
        "explanation_en": "**Why this is correct:**\nWhen $A$ and $B$ are **mutually exclusive**, $A\\cap B=\\emptyset$ so $P(A\\cap B)=0$. Inclusion-exclusion simplifies to $P(A\\cup B)=P(A)+P(B)=0.4+0.3=0.7$. No overlap term needs subtracting because the events cannot co-occur.\n\n**How to think about it:**\nMutually exclusive means the events cannot happen together — no overlap to subtract. Verify the keyword \"mutually exclusive\" or \"disjoint\" in the stem before using the simplified sum rule. If the stem says \"independent\" instead, you would use a completely different formula.\n\n**Common slip:**\nApplying $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)$ but forgetting that $P(A\\cap B)=0$ here, or using $P(A\\cup B)=P(A)P(B)$ — that product rule is for independence of joint occurrence, not for unions.\n\n**Exam tip:**\nUnderline \"mutually exclusive\" in the stem. If absent, you must subtract the intersection term. A quick Venn diagram prevents mixing up disjoint and independent events.\n\n**Self-check:** $0.7<1$ and exceeds both $0.4$ and $0.3$ individually — consistent with a union of two non-trivial events.",
        "explanation_he": "**למה זה נכון:**\nכאשר $A$ ו-$B$ **זרים**, $A\\cap B=\\emptyset$ ולכן $P(A\\cap B)=0$. הכלה-הדרה מתפשטת ל-$P(A\\cup B)=P(A)+P(B)=0.4+0.3=0.7$. אין צורך לחסר חפיפה כי המאורעות לא יכולים להתרחש יחד.\n\n**איך לחשוב על זה:**\nזרות פירושה שהמאורעות לא יכולים להתרחש יחד — אין חפיפה לחיסור. וודאו את המילה \"זרים\" בנתון לפני שימוש בכלל הסכום הפשוט. אם הנתון אומר \"בלתי-תלויים\", נוסחה אחרת לגמרי.\n\n**טעות נפוצה:**\nיישום $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)$ אך שכחה ש-$P(A\\cap B)=0$ כאן, או שימוש ב-$P(A\\cup B)=P(A)P(B)$ — כלל המכפלה הוא לאי-תלות, לא לאיחודים.\n\n**טיפ לבחינה:**\nסמנו \"זרים\" בנתון. אם חסר, חייבים לחסר את איבר החיתוך. דיאגרמת ון מונעת בלבול בין זרות לאי-תלות.\n\n**בדיקה עצמית:** $0.7<1$ וגדול מ-$0.4$ ומ-$0.3$ בנפרד — עקבי עם איחוד שני מאורעות לא-טריוויאליים.",
    },
    3: {
        "explanation_en": "**Why this is correct:**\nWith 6 women out of 10 people chosen uniformly at random, $P(\\text{woman})=6/10=0.6$. This is classical probability: favourable outcomes divided by total equally likely outcomes in a finite sample space.\n\n**How to think about it:**\nIdentify $|\\Omega|=10$ and the event size $|A|=6$. No conditional structure is needed — one random draw from a finite population where every individual has equal selection probability.\n\n**Common slip:**\nUsing $4/10=0.4$ (probability of man) when the question asks for woman, or treating successive draws as independent without checking whether sampling is with or without replacement.\n\n**Exam tip:**\nFor \"chosen at random from a group,\" always state $P=\\text{favourable count}/\\text{total count}$ explicitly on your paper. Examiners award setup marks for identifying $|\\Omega|$ and $|A|$.\n\n**Self-check:** $0.6>0.5$ because women are the majority (6 of 10) — the answer direction is sensible before you even compute.",
        "explanation_he": "**למה זה נכון:**\nעם 6 נשים מתוך 10 אנשים הנבחרים אקראי, $P(\\text{אישה})=6/10=0.6$. זו הסתברות קלאסית: תוצאות מיטיבות חלקי סך התוצאות השוות-הסתברות במרחב סופי.\n\n**איך לחשוב על זה:**\nזהו $|\\Omega|=10$ וגודל המאורע $|A|=6$. אין צורך במבנה מותנה — שליפה אחת מאוכלוסייה סופית שבה לכל אדם הסתברות בחירה שווה.\n\n**טעות נפוצה:**\nשימוש ב-$4/10=0.4$ (הסתברות גבר) כשהשאלה מבקשת אישה, או התייחסות לשליפות עוקבות כבלתי-תלויות בלי לבדוק עם/בלי החזרה.\n\n**טיפ לבחינה:**\nב\"נבחר אקראי מקבוצה,\" ציינו תמיד $P=\\text{מספר מיטיב}/\\text{סך הכל}$ במפורש. בוחנים מעניקים ניקוד על זיהוי $|\\Omega|$ ו-$|A|$.\n\n**בדיקה עצמית:** $0.6>0.5$ כי נשים הן הרוב (6 מתוך 10) — כיוון התשובה הגיוני עוד לפני החישוב.",
    },
    4: {
        "explanation_en": "**Why this is correct:**\nIndependence requires $P(A\\cap B)=P(A)P(B)$. Here $P(A)P(B)=\\frac{1}{2}\\cdot\\frac{1}{2}=\\frac{1}{4}$ but $P(A\\cap B)=P(\\{4,6\\})=\\frac{2}{6}=\\frac{1}{3}$. Since $\\frac{1}{4}\\neq\\frac{1}{3}$, **$A$ and $B$ are dependent** — knowing one outcome changes the probability of the other.\n\n**How to think about it:**\nEven and \"greater than 3\" overlap on outcomes 4 and 6. If you know the die is even (2, 4, 6), the chance it exceeds 3 rises from $1/2$ to $2/3$ — conditional information matters.\n\n**Common slip:**\nAssuming \"different descriptions\" imply independence, or checking only $P(A|B)=P(A)$ without computing $P(A\\cap B)$ directly. Another error: confusing dependence with mutual exclusivity.\n\n**Exam tip:**\nAlways compute both sides of $P(A\\cap B)=P(A)P(B)$ numerically — do not guess from wording. Write the intersection set explicitly.\n\n**Self-check:** $P(A\\cap B)=1/3>P(A)P(B)=1/4$ — positive dependence (overlap more than independence predicts).",
        "explanation_he": "**למה זה נכון:**\nאי-תלות דורשת $P(A\\cap B)=P(A)P(B)$. כאן $P(A)P(B)=\\frac{1}{2}\\cdot\\frac{1}{2}=\\frac{1}{4}$ אך $P(A\\cap B)=P(\\{4,6\\})=\\frac{2}{6}=\\frac{1}{3}$. מכיוון ש-$\\frac{1}{4}\\neq\\frac{1}{3}$, **$A$ ו-$B$ תלויים** — ידיעה על מאורע אחד משנה את הסתברות השני.\n\n**איך לחשוב על זה:**\n\"זוגי\" ו\"גדול מ-3\" חופפים על 4 ו-6. אם ידוע שהקוביה זוגית (2,4,6), הסיכוי שתעלה על 3 עולה מ-$1/2$ ל-$2/3$ — מידע מותנה חשוב.\n\n**טעות נפוצה:**\nהנחה ש\"תיאורים שונים\" מרמזים על אי-תלות, או בדיקה רק של $P(A|B)=P(A)$ בלי חישוב $P(A\\cap B)$. שגיאה נוספת: בלבול תלות עם זרות.\n\n**טיפ לבחינה:**\nחשבו תמיד את שני צדי $P(A\\cap B)=P(A)P(B)$ מספרית — אל תנחשו מהניסוח. כתבו את קבוצת החיתוך במפורש.\n\n**בדיקה עצמית:** $P(A\\cap B)=1/3>P(A)P(B)=1/4$ — תלות חיובית (חפיפה גדולה ממה שאי-תלות מנבאת).",
    },
    5: {
        "explanation_en": "**Why this is correct:**\nFrom $P(A|B)=P(A\\cap B)/P(B)$, rearrange: $P(A\\cap B)=P(A|B)\\cdot P(B)=0.6\\times0.5=0.3$. Then $P(B|A)=P(A\\cap B)/P(A)=0.3/0.3=1.0$ — whenever $A$ occurs, $B$ must also occur ($A\\subseteq B$).\n\n**How to think about it:**\nPart 1 uses the definition of conditional probability forward; part 2 reverses the condition. Note $P(B|A)=1$ means $A$ implies $B$, even though $P(A|B)=0.6\\neq1$ — conditioning direction matters enormously.\n\n**Common slip:**\nAssuming $P(A|B)=P(B|A)$, or concluding independence from $P(A\\cap B)=0.3=P(A)$ without checking $P(A)P(B)=0.15\\neq0.3$. Students also forget that $P(B|A)=1$ forces every $A$ outcome inside $B$.\n\n**Exam tip:**\nWhen $P(B|A)=1$, state \"A is a subset of B\" — this earns interpretation marks on university exams. Draw a Venn diagram with $A$ fully inside $B$.\n\n**Self-check:** $P(A\\cap B)=0.3\\leq\\min(P(A),P(B))=0.3$ — equality at the upper bound confirms $A\\subseteq B$.",
        "explanation_he": "**למה זה נכון:**\nמ-$P(A|B)=P(A\\cap B)/P(B)$, סידור: $P(A\\cap B)=P(A|B)\\cdot P(B)=0.6\\times0.5=0.3$. אז $P(B|A)=P(A\\cap B)/P(A)=0.3/0.3=1.0$ — בכל פעם ש-$A$ מתרחש, גם $B$ חייב ($A\\subseteq B$).\n\n**איך לחשוב על זה:**\nחלק 1 משתמש בהגדרת הסתברות מותנית קדימה; חלק 2 הופך את התנאי. שימו לב: $P(B|A)=1$ פירושו $A$ גורם ל-$B$, למרות ש-$P(A|B)=0.6\\neq1$ — כיוון התנאי קריטי.\n\n**טעות נפוצה:**\nהנחה ש-$P(A|B)=P(B|A)$, או מסקנה על אי-תלות מ-$P(A\\cap B)=0.3=P(A)$ בלי לבדוק $P(A)P(B)=0.15\\neq0.3$. תלמידים גם שוכחים ש-$P(B|A)=1$ מכריח כל תוצאה של $A$ בתוך $B$.\n\n**טיפ לבחינה:**\nכש-$P(B|A)=1$, כתבו \"$A$ תת-קבוצה של $B$\" — זה מזכה בניקוד פרשנות. שרטטו ון עם $A$ לגמרי בתוך $B$.\n\n**בדיקה עצמית:** $P(A\\cap B)=0.3\\leq\\min(P(A),P(B))=0.3$ — שוויון בגבול העליון מאשר $A\\subseteq B$.",
    },
    6: {
        "explanation_en": "**Why this is correct:**\nThis is a **law of total probability** problem. Partition by machine: $P(D)=P(D|M_1)P(M_1)+P(D|M_2)P(M_2)=0.02\\times0.6+0.05\\times0.4=0.012+0.020=0.032=3.2\\%$. Each branch contributes weighted defect probability.\n\n**How to think about it:**\nIdentify the partition ($M_1$, $M_2$) and conditional defect rates. Weight each branch by its production share before summing — the machine producing more items dominates the overall rate even if its defect rate is lower.\n\n**Common slip:**\nAveraging defect rates directly: $(0.02+0.05)/2=0.035$ ignores that Machine 1 produces 60% of items. Always weight by $P(M_i)$, never simple-average conditional rates.\n\n**Exam tip:**\nDraw a two-branch tree: root splits to $M_1$ (60%) and $M_2$ (40%), each with defect/OK leaves. Multiply along paths, add defect-path products.\n\n**Self-check:** $3.2\\%$ lies between $2\\%$ and $5\\%$ and closer to $2\\%$ because Machine 1 dominates production — directionally correct.",
        "explanation_he": "**למה זה נכון:**\nזו בעיית **חוק ההסתברות הכוללת**. חלוקה לפי מכונה: $P(D)=P(D|M_1)P(M_1)+P(D|M_2)P(M_2)=0.02\\times0.6+0.05\\times0.4=0.012+0.020=0.032=3.2\\%$. כל ענף תורם הסתברות פגם משוקללת.\n\n**איך לחשוב על זה:**\nזהו את החלוקה ($M_1$, $M_2$) ושיעורי הפגמים המותנים. שקללו כל ענף לפי חלקו בייצור לפני סכימה — המכונה שמייצרת יותר שולטת בשיעור הכולל גם אם שיעור הפגם בה נמוך.\n\n**טעות נפוצה:**\nממוצע ישיר של שיעורי פגם: $(0.02+0.05)/2=0.035$ מתעלם מכך שמכונה 1 מייצרת 60%. שקללו תמיד לפי $P(M_i)$, לא ממוצע פשוט.\n\n**טיפ לבחינה:**\nשרטטו עץ דו-ענפי: שורש ל-$M_1$ (60%) ו-$M_2$ (40%), כל אחד עם עלים פגום/תקין. כפלו לאורך מסלולים, חברו מוצרי מסלולי פגם.\n\n**בדיקה עצמית:** $3.2\\%$ בין $2\\%$ ל-$5\\%$ וקרוב ל-$2\\%$ כי מכונה 1 שולטת — כיוון נכון.",
    },
    7: {
        "explanation_en": "**Why this is correct:**\nGiven a defective item, apply **Bayes' theorem**: $P(M_1|D)=P(D|M_1)P(M_1)/P(D)=0.012/0.032=0.375=37.5\\%$. Machine 1 contributes less than half of defects despite producing 60% of items because its per-item defect rate is lower.\n\n**How to think about it:**\nThe numerator is the joint probability of \"defective AND from Machine 1\" (already computed as 0.012 in the total-probability step). The denominator is the total defect rate from the previous part — Bayes reverses the conditioning direction.\n\n**Common slip:**\nUsing $P(M_1)=0.6$ directly as the answer (confusing prior with posterior), or confusing $P(M_1|D)$ with $P(D|M_1)=0.02$. These reverse-conditionings can differ by an order of magnitude.\n\n**Exam tip:**\nLabel every probability: $P(D|M_1)$ is \"defect given Machine 1\"; $P(M_1|D)$ is \"Machine 1 given defect.\" Write both on your tree before computing.\n\n**Self-check:** $0.375<0.6$ — the better machine is under-represented among defects, which matches intuition about lower defect rates.",
        "explanation_he": "**למה זה נכון:**\nבהינתן פריט פגום, יישמו **משפט בייס**: $P(M_1|D)=P(D|M_1)P(M_1)/P(D)=0.012/0.032=0.375=37.5\\%$. מכונה 1 תורמת פחות ממחצית הפגמים למרות 60% מהייצור כי שיעור הפגם לפריט נמוך יותר.\n\n**איך לחשוב על זה:**\nהמונה הוא ההסתברות המשותפת \"פגום וגם ממכונה 1\" (0.012 מחוק הכוללת). המכנה הוא שיעור הפגום הכולל — בייס הופך את כיוון התנאי.\n\n**טעות נפוצה:**\nשימוש ישיר ב-$P(M_1)=0.6$ (בלבול Prior עם Posterior), או בלבול $P(M_1|D)$ עם $P(D|M_1)=0.02$. תנאי הפוך יכול להשתנות בסדר גודל.\n\n**טיפ לבחינה:**\nסמנו כל הסתברות: $P(D|M_1)$ = \"פגום בהינתן מכונה 1\"; $P(M_1|D)$ = \"מכונה 1 בהינתן פגום.\" כתבו שניהם על העץ.\n\n**בדיקה עצמית:** $0.375<0.6$ — המכונה הטובה יותר מיוצגת פחות בפגומים — תואם אינטואיציה.",
    },
}


def wc(text: str) -> int:
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    # Patch exercises
    ex_map = {e["id"]: e for e in EXERCISES}
    for sec in data["sections"]:
        if sec.get("kind") != "exercise_set":
            continue
        for ex in sec.get("exercises", []):
            if ex["id"] in ex_map:
                ex["solution_en"] = ex_map[ex["id"]]["solution_en"]
                ex["solution_he"] = ex_map[ex["id"]]["solution_he"]

    # Deepen theory
    for sec in data["sections"]:
        if sec.get("kind") == "theory":
            if "Theorem 5" not in sec["body_en_md"]:
                sec["body_en_md"] += THEORY_EN_APPEND
                sec["body_he_md"] += THEORY_HE_APPEND

    # Patch question explanations
    for q in data["questions"]:
        if q["ord"] in QUESTION_EXPL_PATCHES:
            q.update(QUESTION_EXPL_PATCHES[q["ord"]])

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

    # Validate JSON
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")

    # Word counts
    from pathlib import Path
    import importlib.util
    spec = importlib.util.spec_from_file_location("bu", ROOT / "scripts/lib/bilingual-utils.mjs")
    # use node for word counts instead
    r = subprocess.run(
        ["node", "-e", f"""
import fs from 'fs';
import {{ wordCount, hebrewBodyWeak, MIN_WORDS }} from './scripts/lib/bilingual-utils.mjs';
const d = JSON.parse(fs.readFileSync('scripts/seed_data/lessons/probability_basic.json','utf8'));
let issues = [];
for (const s of d.sections) {{
  const kind = s.kind;
  const mw = MIN_WORDS[kind];
  if (!mw) continue;
  const en = wordCount(s.body_en_md||'');
  const he = wordCount(s.body_he_md||'');
  if (en < mw.en) issues.push(`${{kind}} EN:${{en}}<${{mw.en}}`);
  if (he < mw.he) issues.push(`${{kind}} HE:${{he}}<${{mw.he}}`);
  if (hebrewBodyWeak(s.body_he_md, s.body_en_md)) issues.push(`${{kind}} HE_WEAK`);
}}
for (const q of d.questions) {{
  const en = wordCount(q.explanation_en||'');
  const he = wordCount(q.explanation_he||'');
  if (en < 80) issues.push(`q${{q.ord}} EN:${{en}}<80`);
  if (he < 80) issues.push(`q${{q.ord}} HE:${{he}}<80`);
}}
if (issues.length) {{ console.error('ISSUES:', issues.join(', ')); process.exit(1); }}
console.log('All depth gates OK');
"""],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout or r.stderr)
    if r.returncode != 0:
        raise SystemExit(r.returncode)

    r2 = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r2.stdout or r2.stderr)
    if r2.returncode != 0:
        raise SystemExit(r2.returncode)
    print("seed-lessons dry-run passed")


if __name__ == "__main__":
    main()
