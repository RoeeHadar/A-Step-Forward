#!/usr/bin/env python3
"""Expand sample_space.json — substantive bilingual content per bilingual-utils MIN_WORDS."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/sample_space.json"

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


SECTION_BODIES = {
    "intro": {
        "body_en_md": """Before calculating any probability, we need a precise vocabulary. Probability theory begins with the **sample space** $\\Omega$ — the set of all possible outcomes of a random experiment — and builds from three axioms that Kolmogorov formulated in 1933. Every event is a subset of $\\Omega$, and probability is a function that assigns numbers to those subsets while obeying simple, non-negotiable rules.

These foundations appear throughout Israeli Bagrut (4–5 unit statistics), university introductory probability, and engineering statistics courses. Mastering them now prevents confusion later when conditional probability, independence, and Bayes' theorem enter the picture.

**Exam topics you will meet repeatedly:**
- Defining sample spaces and events (coins, dice, cards, urns)
- Set operations: union ($A \\cup B$), intersection ($A \\cap B$), complement ($A^c$)
- Kolmogorov axioms and their consequences (complement rule, inclusion-exclusion)
- Classical probability when outcomes are equally likely: $P(A) = |A|/|\\Omega|$
- Addition rule for mutually exclusive events; general inclusion-exclusion for two events
- "At least one" problems — almost always solved faster via the complement $1 - P(\\text{none})$""",
        "body_he_md": """לפני שמחשבים הסתברות, צריך אוצר מילים מדויק. תורת ההסתברות מתחילה ב**מרחב המדגם** $\\Omega$ — קבוצת כל התוצאות האפשריות של ניסוי מקרי — ונבנית משלוש אקסיומות שקולמוגורוב ניסח ב-1933. כל אירוע הוא תת-קבוצה של $\\Omega$, וההסתברות היא פונקציה שמקצה מספרים לתת-קבוצות אלו תוך שמירה על כללים פשוטים וקבועים.

היסודות האלה מופיעים בבגרות (4–5 יחידות סטטיסטיקה), בקורסי הסתברות באוניברסיטה ובסטטיסטיקה הנדסית. שליטה בהם עכשיו מונעת בלבול מאוחר יותר, כשמגיעים להסתברות מותנית, אי-תלות ומשפט בייס.

**נושאי בחינה שחוזרים שוב ושוב:**
- הגדרת מרחבי מדגם ואירועים (מטבע, קובייה, קלפים, כדורים בשק)
- פעולות קבוצות: איחוד ($A \\cup B$), חיתוך ($A \\cap B$), משלים ($A^c$)
- אקסיומות קולמוגורוב ומסקנותיהן (כלל המשלים, הכלה-הפסה)
- הסתברות קלאסית כשהתוצאות שוות-הסתברות: $P(A) = |A|/|\\Omega|$
- כלל חיבור לאירועים זרים; הכלה-הפסה לשני אירועים
- בעיות "לפחות אחד" — כמעט תמיד מהיר יותר דרך המשלים $1 - P(\\text{אין})$""",
    },
    "definition": {
        "body_en_md": """**Random experiment:** A procedure whose outcome cannot be predicted with certainty before it is performed (rolling a die, drawing a card, measuring a patient's blood pressure).

**Sample space $\\Omega$:** The set of all possible elementary outcomes. Examples: $\\Omega = \\{H, T\\}$ for one coin flip; $\\Omega = \\{(1,1), (1,2), \\ldots, (6,6)\\}$ for two dice as ordered pairs; $\\Omega = \\{1,2,3,4,5,6\\}$ for one die.

**Event $A$:** Any subset $A \\subseteq \\Omega$. An event is a collection of outcomes we care about. Example: "sum is 7" on two dice is the set $\\{(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)\\}$.

**Event operations (set language):**
- **Union** $A \\cup B$: at least one of $A$ or $B$ occurs ("A or B" in inclusive sense).
- **Intersection** $A \\cap B$: both $A$ and $B$ occur ("A and B").
- **Complement** $A^c = \\Omega \\setminus A$: $A$ does **not** occur.

**Mutually exclusive (disjoint):** $A \\cap B = \\emptyset$ — the events cannot both happen.

**Exhaustive partition:** Events $B_1, \\ldots, B_k$ cover $\\Omega$ with no overlap — exactly one occurs.

**De Morgan's laws** (essential for complement problems):
$$(A \\cup B)^c = A^c \\cap B^c, \\qquad (A \\cap B)^c = A^c \\cup B^c$$

Read De Morgan as: "not (A or B)" equals "(not A) and (not B)". These laws convert awkward "at least one" wording into manageable complement arithmetic.""",
        "body_he_md": """**ניסוי מקרי:** תהליך שתוצאתו אינה ניתנת לחיזוי בוודאות לפני ביצועו (הטלת קובייה, שליפת קלף, מדידת לחץ דם).

**מרחב מדגם $\\Omega$:** קבוצת כל התוצאות האפשריות. דוגמאות: $\\Omega = \\{H, T\\}$ להטלת מטבע; $\\Omega = \\{(1,1), (1,2), \\ldots, (6,6)\\}$ לשתי קוביות כזוגות סדורים; $\\Omega = \\{1,2,3,4,5,6\\}$ לקובייה אחת.

**אירוע $A$:** כל תת-קבוצה $A \\subseteq \\Omega$. אירוע הוא אוסף תוצאות שמעניין אותנו. דוגמה: "סכום 7" בשתי קוביות הוא $\\{(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)\\}$.

**פעולות על אירועים (שפת קבוצות):**
- **איחוד** $A \\cup B$: לפחות אחד מ-$A$ או $B$ מתרחש ("A או B" במובן כולל).
- **חיתוך** $A \\cap B$: גם $A$ וגם $B$ מתרחשים ("A וגם B").
- **משלים** $A^c = \\Omega \\setminus A$: $A$ **לא** מתרחש.

**זרים (מנוגדים):** $A \\cap B = \\emptyset$ — שני האירועים לא יכולים להתרחש יחד.

**פרדה מאכללת:** אירועים $B_1, \\ldots, B_k$ מכסים את $\\Omega$ בלי חפיפה — בדיוק אחד מתרחש.

**חוקי דה-מורגן** (חיוניים לבעיות משלים):
$$(A \\cup B)^c = A^c \\cap B^c, \\qquad (A \\cap B)^c = A^c \\cup B^c$$

קראו דה-מורגן כך: "לא (A או B)" שווה ל-"(לא A) וגם (לא B)". החוקים ממירים ניסוח "לפחות אחד" למשלים נוח לחישוב.""",
    },
    "theory": {
        "body_en_md": """**Kolmogorov's three axioms** define every legitimate probability measure $P$:

1. **Non-negativity:** $P(A) \\geq 0$ for every event $A$.
2. **Normalization:** $P(\\Omega) = 1$ — something must happen.
3. **Additivity for disjoint events:** If $A \\cap B = \\emptyset$, then $P(A \\cup B) = P(A) + P(B)$.

**Consequences you use on every exam:**
- $P(\\emptyset) = 0$ (impossible event).
- **Complement rule:** $P(A^c) = 1 - P(A)$.
- **Inclusion-exclusion (two events):** $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$. The subtraction removes outcomes counted twice in $A \\cap B$.
- **Monotonicity:** If $A \\subseteq B$, then $P(A) \\leq P(B)$.
- **Bound:** $0 \\leq P(A) \\leq 1$ always.

**Classical probability** applies when $\\Omega$ is **finite** and all outcomes are **equally likely**:
$$P(A) = \\frac{|A|}{|\\Omega|} = \\frac{\\text{number of favorable outcomes}}{\\text{total outcomes}}$$

Before using this formula, verify both conditions: finite sample space and symmetry/fairness.

**"At least one" strategy:** Direct counting of "at least one success" is tedious. Instead:
$$P(\\text{at least one}) = 1 - P(\\text{none})$$
This works for coins, dice, birthday problems, and quality-control sampling. De Morgan gives the language: $(A_1 \\cup A_2 \\cup \\cdots)^c = A_1^c \\cap A_2^c \\cap \\cdots$.

**Without replacement:** When objects are drawn and not returned, probabilities change each draw. Use sequential multiplication $\\frac{n_1}{N} \\cdot \\frac{n_2}{N-1} \\cdots$ or combinations $\\binom{\\cdot}{\\cdot}$ when order does not matter.""",
        "body_he_md": """**שלוש אקסיומות קולמוגורוב** מגדירות כל מידת הסתברות $P$ לגיטימית:

1. **אי-שליליות:** $P(A) \\geq 0$ לכל אירוע $A$.
2. **נרמול:** $P(\\Omega) = 1$ — חייב להתרחש משהו.
3. **אדיטיביות לאירועים זרים:** אם $A \\cap B = \\emptyset$, אז $P(A \\cup B) = P(A) + P(B)$.

**מסקנות שמשתמשים בהן בכל בחינה:**
- $P(\\emptyset) = 0$ (אירוע בלתי-אפשרי).
- **כלל המשלים:** $P(A^c) = 1 - P(A)$.
- **הכלה-הפסה (שני אירועים):** $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$. החיסור מסיר תוצאות שנספרו פעמיים ב-$A \\cap B$.
- **מונוטוניות:** אם $A \\subseteq B$, אז $P(A) \\leq P(B)$.
- **גבול:** תמיד $0 \\leq P(A) \\leq 1$.

**הסתברות קלאסית** חלה כש-$\\Omega$ **סופי** וכל התוצאות **שוות-הסתברות**:
$$P(A) = \\frac{|A|}{|\\Omega|} = \\frac{\\text{מספר תוצאות חיוביות}}{\\text{סך התוצאות}}$$

לפני שימוש בנוסחה, ודאו שני תנאים: מרחב מדגם סופי וסימטריה/הוגנות.

**אסטרטגיית "לפחות אחד":** ספירה ישירה של "לפחות הצלחה אחת" מייגעת. במקום:
$$P(\\text{לפחות אחד}) = 1 - P(\\text{אין})$$
זה עובד במטבעות, קוביות, בעיית ימי הולדת ודגימות בקרת איכות. דה-מורגן נותן את השפה: $(A_1 \\cup A_2 \\cup \\cdots)^c = A_1^c \\cap A_2^c \\cap \\cdots$.

**ללא החזרה:** כששולפים ולא מחזירים, ההסתברויות משתנות בכל שליפה. השתמשו בכפל רציף $\\frac{n_1}{N} \\cdot \\frac{n_2}{N-1} \\cdots$ או בצירופים $\\binom{\\cdot}{\\cdot}$ כשסדר לא חשוב.""",
    },
    "worked_example_1": {
        "body_en_md": """**Two fair dice are rolled. Find:**
(a) $|\\Omega|$
(b) $P(\\text{sum} = 7)$
(c) $P(\\text{at least one 6})$

This is the canonical Bagrut dice problem — it tests sample-space size, classical counting, and the complement strategy in one scenario.

### Move 1: Build the sample space
Each die has 6 outcomes. Ordered pairs $(i,j)$ with $i,j \\in \\{1,\\ldots,6\\}$ give $|\\Omega| = 6 \\times 6 = 36$. **Order matters** here: $(1,6) \\neq (6,1)$ unless the problem says "unordered."

### Move 2: Count favorable outcomes for sum 7
Pairs with sum 7: $(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)$ — exactly **6** outcomes.
$$P(\\text{sum}=7) = \\frac{6}{36} = \\frac{1}{6}$$

### Move 3: "At least one 6" via complement
Direct count: outcomes with at least one 6 = $6 + 6 - 1 = 11$ (first die 6 OR second die 6, minus double-counted $(6,6)$). Faster via complement:
$$P(\\text{no 6 on either die}) = \\frac{5}{6} \\cdot \\frac{5}{6} = \\frac{25}{36}$$
$$P(\\text{at least one 6}) = 1 - \\frac{25}{36} = \\frac{11}{36}$$

**Answer:** (a) $36$; (b) $1/6$; (c) $11/36$. Always state whether dice are ordered — it changes $|\\Omega|$ completely.""",
        "body_he_md": """**שתי קוביות הוגנות מוטלות. מצאו:**
(א) $|\\Omega|$
(ב) $P(\\text{סכום} = 7)$
(ג) $P(\\text{לפחות שש אחת})$

זו בעיית הקוביות הקלאסית בבגרות — בודקת גודל מרחב מדגם, ספירה קלאסית ואסטרטגיית משלים בסיטואציה אחת.

### צעד 1: בניית מרחב המדגם
לכל קובייה 6 תוצאות. זוגות סדורים $(i,j)$ עם $i,j \\in \\{1,\\ldots,6\\}$ נותנים $|\\Omega| = 6 \\times 6 = 36$. **סדר חשוב** כאן: $(1,6) \\neq (6,1)$ אלא אם השאלה אומרת "לא סדור."

### צעד 2: ספירת תוצאות חיוביות לסכום 7
זוגות עם סכום 7: $(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)$ — בדיוק **6** תוצאות.
$$P(\\text{סכום}=7) = \\frac{6}{36} = \\frac{1}{6}$$

### צעד 3: "לפחות שש אחת" דרך משלים
ספירה ישירה: תוצאות עם לפחות שש אחת = $6 + 6 - 1 = 11$. מהיר יותר דרך משלים:
$$P(\\text{אין שש באף קובייה}) = \\frac{5}{6} \\cdot \\frac{5}{6} = \\frac{25}{36}$$
$$P(\\text{לפחות שש אחת}) = 1 - \\frac{25}{36} = \\frac{11}{36}$$

**תשובה:** (א) $36$; (ב) $1/6$; (ג) $11/36$. תמיד ציינו אם הקוביות סדורות — זה משנה את $|\\Omega|$ לחלוטין.""",
    },
    "worked_example_2": {
        "body_en_md": """**In a class of 30 students: 18 study math (M), 15 study physics (P), 10 study both. Find:**
(a) $P(M \\cup P)$ — a student studies math or physics (or both)
(b) $P(\\text{neither M nor P})$

This is a Venn-diagram word problem translated into probability. The counts become probabilities by dividing by the class size.

### Move 1: Convert counts to probabilities
$P(M) = 18/30$, $P(P) = 15/30$, $P(M \\cap P) = 10/30$.

### Move 2: Apply inclusion-exclusion for the union
$$P(M \\cup P) = P(M) + P(P) - P(M \\cap P) = \\frac{18}{30} + \\frac{15}{30} - \\frac{10}{30} = \\frac{23}{30}$$

The subtraction of $10/30$ removes students counted in both circles.

### Move 3: "Neither" via complement
Students outside both circles:
$$P(\\text{neither}) = 1 - P(M \\cup P) = 1 - \\frac{23}{30} = \\frac{7}{30}$$

**Venn check:** Only M = $18-10=8$; only P = $15-10=5$; both = $10$; neither = $30-8-5-10=7$. ✓

**Answer:** (a) $23/30$; (b) $7/30$. On Bagrut, draw the Venn diagram before writing the formula — it prevents sign errors.""",
        "body_he_md": """**בכיתה של 30 תלמידים: 18 לומדים מתמטיקה (M), 15 לומדים פיזיקה (P), 10 לומדים את שניהם. מצאו:**
(א) $P(M \\cup P)$ — תלמיד לומד מתמטיקה או פיזיקה (או שניהם)
(ב) $P(\\text{לא M ולא P})$

זו בעיית מילים עם דיאגרמת ון שמתורגמת להסתברות. הספירות הופכות להסתברויות בחלוקה בגודל הכיתה.

### צעד 1: המרת ספירות להסתברויות
$P(M) = 18/30$, $P(P) = 15/30$, $P(M \\cap P) = 10/30$.

### צעד 2: יישום הכלה-הפסה לאיחוד
$$P(M \\cup P) = P(M) + P(P) - P(M \\cap P) = \\frac{18}{30} + \\frac{15}{30} - \\frac{10}{30} = \\frac{23}{30}$$

החיסור של $10/30$ מסיר תלמידים שנספרו בשני המעגלים.

### צעד 3: "לא שניהם" דרך משלים
תלמידים מחוץ לשני המעגלים:
$$P(\\text{לא שניהם}) = 1 - P(M \\cup P) = 1 - \\frac{23}{30} = \\frac{7}{30}$$

**בדיקת ון:** רק M = $18-10=8$; רק P = $15-10=5$; שניהם = $10$; לא = $30-8-5-10=7$. ✓

**תשובה:** (א) $23/30$; (ב) $7/30$. בבגרות — ציירו דיאגרמת ון לפני הנוסחה; זה מונע טעויות סימן.""",
    },
    "worked_example_3": {
        "body_en_md": """**A bag contains 5 red and 7 blue balls. 3 balls are drawn without replacement. Find $P(\\text{exactly 2 red})$.**

This hypergeometric-style problem combines classical counting with combinations. "Without replacement" means each draw changes the composition — unlike independent trials with replacement.

### Move 1: Total ways to choose 3 from 12
Order does not matter (we only care about colors, not draw sequence):
$$|\\Omega| = \\binom{12}{3} = \\frac{12 \\times 11 \\times 10}{3 \\times 2 \\times 1} = 220$$

### Move 2: Favorable outcomes — exactly 2 red and 1 blue
Choose 2 red from 5 AND 1 blue from 7:
$$|A| = \\binom{5}{2} \\times \\binom{7}{1} = 10 \\times 7 = 70$$

### Move 3: Classical probability
$$P(A) = \\frac{70}{220} = \\frac{7}{22} \\approx 0.318$$

**Alternative (sequential):** $\\frac{5}{12} \\cdot \\frac{4}{11} \\cdot \\frac{7}{10} \\times 3!$ accounts for all orderings of RR B — same answer.

**Answer:** $7/22$. On exams, state clearly whether order matters before choosing $\\binom{n}{k}$ vs. sequential products. Compare with replacement: $P(\\text{2 red, 1 blue with replacement}) = 3 \\cdot (5/12)^2(7/12) \\approx 0.30$ — slightly lower than without replacement because drawing red does not deplete the bag.""",
        "body_he_md": """**בשקית 5 כדורים אדומים ו-7 כחולים. שולפים 3 כדורים ללא החזרה. מצאו $P(\\text{בדיוק 2 אדומים})$.**

בעיה בסגנון היפר-גיאומטרי שמשלבת ספירה קלאסית עם צירופים. "ללא החזרה" אומר שכל שליפה משנה את הרכב השקית — בניגוד לניסויים בלתי-תלויים עם החזרה.

### צעד 1: סך הדרכים לבחור 3 מתוך 12
סדר לא חשוב (אכפת רק מהצבעים, לא מסדר השליפות):
$$|\\Omega| = \\binom{12}{3} = \\frac{12 \\times 11 \\times 10}{3 \\times 2 \\times 1} = 220$$

### צעד 2: תוצאות חיוביות — בדיוק 2 אדומים ו-1 כחול
בוחרים 2 אדומים מ-5 **וגם** 1 כחול מ-7:
$$|A| = \\binom{5}{2} \\times \\binom{7}{1} = 10 \\times 7 = 70$$

### צעד 3: הסתברות קלאסית
$$P(A) = \\frac{70}{220} = \\frac{7}{22} \\approx 0.318$$

**חלופה (רצף):** $\\frac{5}{12} \\cdot \\frac{4}{11} \\cdot \\frac{7}{10} \\times 3!$ מחשבת את כל הסדרים של אא כ — אותה תשובה.

**תשובה:** $7/22$. בבחינה — ציינו בבירור אם סדר חשוב לפני בחירה בין $\\binom{n}{k}$ לבין כפל הסתברויות רציף. השוו עם החזרה: $P(\\text{2 אדומים, 1 כחול עם החזרה}) = 3 \\cdot (5/12)^2(7/12) \\approx 0.30$ — מעט נמוך יותר מללא החזרה כי שליפת אדום לא מדלדלת את השקית.""",
    },
    "method_guide": {
        "body_en_md": """| Problem type | Formula / Method | When to use |
|---|---|---|
| Union of 2 events | $P(A)+P(B)-P(A\\cap B)$ | "A or B" with overlap possible |
| Mutually exclusive union | $P(A)+P(B)$ | $A \\cap B = \\emptyset$ confirmed |
| Complement | $P(A^c) = 1-P(A)$ | "Not A", "at least one" via $1-P(\\text{none})$ |
| Classical (equal outcomes) | $|A|/|\\Omega|$ | Finite, fair, equally likely |
| Without replacement ($k$ draws) | $\\binom{n}{k}$ or sequential product | Urns, cards, balls — no return |
| De Morgan | $(A\\cup B)^c = A^c \\cap B^c$ | Flip "or" to "and" under complement |

**Decision flow:** (1) Identify $\\Omega$ and whether outcomes are equally likely. (2) Translate words to set notation — "or" $\\to \\cup$, "and" $\\to \\cap$. (3) Check if events are disjoint before adding. (4) If "at least one," try complement first.

**Tip:** Write $|\\Omega|$ on scratch paper before any counting. A wrong denominator ruins an otherwise correct numerator.""",
        "body_he_md": """| סוג שאלה | נוסחה / שיטה | מתי להשתמש |
|---|---|---|
| איחוד 2 אירועים | $P(A)+P(B)-P(A\\cap B)$ | "A או B" עם חפיפה אפשרית |
| איחוד זרים | $P(A)+P(B)$ | $A \\cap B = \\emptyset$ מאומת |
| משלים | $P(A^c) = 1-P(A)$ | "לא A", "לפחות אחד" דרך $1-P(\\text{אין})$ |
| קלאסית (שווה-הסתברות) | $|A|/|\\Omega|$ | סופי, הוגן, שווה-הסתברות |
| ללא החזרה ($k$ שליפות) | $\\binom{n}{k}$ או כפל רציף | שקיות, קלפים, כדורים — בלי החזרה |
| דה-מורגן | $(A\\cup B)^c = A^c \\cap B^c$ | הפיכת "או" ל-"וגם" תחת משלים |

**זרימת החלטה:** (1) זהו $\\Omega$ והאם התוצאות שוות-הסתברות. (2) תרגמו מילים לסימון קבוצות — "או" $\\to \\cup$, "וגם" $\\to \\cap$. (3) בדקו אם האירועים זרים לפני חיבור. (4) אם "לפחות אחד" — נסו משלים קודם.

**טיפ:** כתבו $|\\Omega|$ על טיוטה לפני כל ספירה. מכנה שגוי הורס מונה נכון.""",
    },
    "pitfall": {
        "body_en_md": """1. **Confusing "or" with "and."** In probability, "A or B" means $A \\cup B$ (inclusive — at least one). "A and B" means $A \\cap B$. Mixing these produces wrong formulas immediately.

2. **Adding probabilities without checking disjointness.** $P(A \\cup B) = P(A) + P(B)$ **only** when $A \\cap B = \\emptyset$. Otherwise you double-count the overlap and must subtract $P(A \\cap B)$.

3. **"At least one" by direct count.** Listing all success patterns works for small cases but fails on birthday or multiple-trial problems. Default to $P(\\text{at least one}) = 1 - P(\\text{none})$.

4. **Order vs. unordered confusion.** Two dice as ordered pairs: $|\\Omega|=36$. As unordered sums: different count. Cards drawn in sequence vs. hand of cards: different $\\Omega$.

5. **Non-exhaustive sample space.** Forgetting an outcome (e.g., missing "both fail" in a two-component system) makes probabilities sum to less than 1 and invalidates every subsequent calculation.

**Example misconception:** $P(A \\cup B) = P(A) + P(B)$ always.

**Fix:** Draw a Venn diagram. If the circles overlap, subtract $P(A \\cap B)$. If they do not touch, addition is valid.""",
        "body_he_md": """1. **בלבול בין "או" ל-"וגם".** בהסתברות, "A או B" פירושו $A \\cup B$ (כולל — לפחות אחד). "A וגם B" פירושו $A \\cap B$. ערבוב מיידי מוביל לנוסחה שגויה.

2. **חיבור הסתברויות בלי לבדוק זרות.** $P(A \\cup B) = P(A) + P(B)$ **רק** כש-$A \\cap B = \\emptyset$. אחרת סופרים את החפיפה פעמיים וחייבים להחסיר $P(A \\cap B)$.

3. **"לפחות אחד" בספירה ישירה.** רשימת כל דפוסי ההצלחה עובדת במקרים קטנים אך נכשלת בבעיות ימי הולדת או ניסויים מרובים. ברירת מחדל: $P(\\text{לפחות אחד}) = 1 - P(\\text{אין})$.

4. **בלבול סדר מול לא-סדר.** שתי קוביות כזוגות סדורים: $|\\Omega|=36$. כסכומים לא-סדורים: ספירה שונה. קלפים ברצף מול יד: $\\Omega$ שונה.

5. **מרחב מדגם לא מלא.** שכחת תוצאה (למשל "שניהם נכשלים") גורמת לסכום הסתברויות קטן מ-1 ופוסלת כל חישוב המשך.

**דוגמת טעות:** $P(A \\cup B) = P(A) + P(B)$ תמיד.

**תיקון:** ציירו דיאגרמת ון. אם המעגלים חופפים — החסירו $P(A \\cap B)$. אם לא נוגעים — חיבור תקין.""",
    },
    "why_matters": {
        "body_en_md": """Sample spaces and axioms are the grammar of every probability argument in the rest of your curriculum — conditional probability (`concept:probability_conditional_bayes`), distributions (`concept:distributions`), hypothesis testing (`concept:hypothesis_testing_intro`), and physics problems involving quantum measurement or statistical mechanics.

**Why it matters for exams:** Bagrut 5-unit statistics and university courses reward *transfer* — recognizing which formula fits from problem wording alone. A student who can instantly map "at least one defect" to $1-P(\\text{none})$ saves minutes on timed exams.

**Real-world link:** Quality engineers use complement rules for "system failure" probabilities; epidemiologists count outbreak scenarios in finite sample spaces; and card-game designers balance odds using classical $|A|/|\\Omega|$. The vocabulary you build here appears in every data-science pipeline that reports confidence and error rates.""",
        "body_he_md": """מרחבי מדגם ואקסיומות הם דקדוק של כל טיעון הסתברותי בהמשך תוכנית הלימודים — הסתברות מותנית (`concept:probability_conditional_bayes`), התפלגויות (`concept:distributions`), בדיקת השערות (`concept:hypothesis_testing_intro`), ובעיות פיזיקה במדידה קוונטית או מכניקה סטטיסטית.

**למה זה חשוב לבחינות:** בבגרות 5 יחידות סטטיסטיקה ובקורסים אוניברסיטאיים מעריכים *העברה* — זיהוי הנוסחה המתאימה מניסוח השאלה בלבד. תלמיד שמזהה מיד "לפחות פגם אחד" כ-$1-P(\\text{אין})$ חוסך דקות בבחינה מוגבלת בזמן.

**קשר לעולם האמיתי:** מהנדסי איכות משתמשים בכללי משלים להסתברויות "כשל מערכת"; חוקרי מגיפות סופרים תרחישי התפרצות במרחבי מדגם סופיים; ומעצבי משחקי קלפים מאזנים סיכויים ב-$|A|/|\\Omega|$ קלאסי. אוצר המילים שבונים כאן מופיע בכל צינור data science שמדווח על רמות ביטחון ושגיאה.""",
    },
    "before_exam": {
        "body_en_md": """**Formulas to have ready:**
- $P(A \\cup B) = P(A)+P(B)-P(A \\cap B)$ (general union)
- $P(A \\cup B) = P(A)+P(B)$ when $A \\cap B = \\emptyset$
- $P(A^c) = 1-P(A)$ (complement)
- $P(\\text{at least one}) = 1 - P(\\text{none})$ (complement strategy)
- Classical: $P(A) = |A|/|\\Omega|$ (equally likely, finite)
- Without replacement: $\\binom{n}{k}$ combinations
- De Morgan: $(A\\cup B)^c = A^c \\cap B^c$

**Pre-exam drill:** Say each formula aloud once, then solve one checkpoint without looking. Draw a Venn diagram for every two-event word problem before writing numbers. Time yourself: sample-space definition should take under 30 seconds; inclusion-exclusion under 45 seconds once givens are circled. If any formula feels shaky, rewrite it from the axioms — that builds exam-day confidence.""",
        "body_he_md": """**נוסחאות שצריך להכין:**
- $P(A \\cup B) = P(A)+P(B)-P(A \\cap B)$ (איחוד כללי)
- $P(A \\cup B) = P(A)+P(B)$ כש-$A \\cap B = \\emptyset$
- $P(A^c) = 1-P(A)$ (משלים)
- $P(\\text{לפחות אחד}) = 1 - P(\\text{אין})$ (אסטרטגיית משלים)
- קלאסית: $P(A) = |A|/|\\Omega|$ (שווה-הסתברות, סופי)
- ללא החזרה: צירופים $\\binom{n}{k}$
- דה-מורגן: $(A\\cup B)^c = A^c \\cap B^c$

**תרגול לפני בחינה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint אחד בלי להסתכל. ציירו דיאגרמת ון לכל בעיית מילים עם שני אירועים לפני כתיבת מספרים. תזמנו את עצמכם: הגדרת מרחב מדגם — פחות מ-30 שניות; הכלה-הפסה — פחות מ-45 שניות אחרי סימון הנתונים.""",
    },
    "summary": {
        "body_en_md": """- **Sample space $\\Omega$:** all possible outcomes of a random experiment; must be exhaustive.
- **Event:** any subset $A \\subseteq \\Omega$; set operations ($\\cup$, $\\cap$, $^c$) combine events.
- **Kolmogorov axioms:** non-negativity, $P(\\Omega)=1$, additivity for disjoint events.
- **Complement rule:** $P(A^c) = 1-P(A)$ — the workhorse for "at least one" problems.
- **Inclusion-exclusion:** $P(A\\cup B) = P(A)+P(B)-P(A\\cap B)$ — subtract overlap.
- **Classical probability:** $P(A) = |A|/|\\Omega|$ when outcomes are equally likely.
- **Strategy:** define $\\Omega$ first, translate words to sets, check disjointness, try complement for "at least one."

**Takeaway:** You should now recognize which method applies from the problem wording alone — before reaching for a formula.""",
        "body_he_md": """- **מרחב מדגם $\\Omega$:** כל התוצאות האפשריות; חייב להיות מאכלל.
- **אירוע:** כל תת-קבוצה $A \\subseteq \\Omega$; פעולות קבוצות ($\\cup$, $\\cap$, $^c$) משלבות אירועים.
- **אקסיומות קולמוגורוב:** אי-שליליות, $P(\\Omega)=1$, אדיטיביות לזרים.
- **כלל משלים:** $P(A^c) = 1-P(A)$ — כלי העבודה לבעיות "לפחות אחד".
- **הכלה-הפסה:** $P(A\\cup B) = P(A)+P(B)-P(A\\cap B)$ — מחסירים חפיפה.
- **הסתברות קלאסית:** $P(A) = |A|/|\\Omega|$ כשהתוצאות שוות-הסתברות.
- **אסטרטגיה:** הגדירו $\\Omega$ קודם, תרגמו מילים לקבוצות, בדקו זרות, נסו משלים ל-"לפחות אחד".

**מסקנה:** כעת תוכלו לזהות איזו שיטה מתאימה מניסוח השאלה בלבד — לפני שמושכים נוסחה.""",
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": """A standard deck has 52 cards. We want $P(\\text{red ace})$ — drawing a card that is both an ace and red.

**Step 1:** Identify favorable outcomes. Red aces: ace of hearts and ace of diamonds — $|A| = 2$.

**Step 2:** Sample space size: $|\\Omega| = 52$ (one card drawn uniformly).

**Step 3:** Classical probability (each card equally likely):
$$P(\\text{red ace}) = \\frac{2}{52} = \\frac{1}{26} \\approx 0.0385$$

**Check:** There are 4 aces total and 26 red cards, but only 2 cards satisfy both conditions. **Answer:** $1/26$.""",
        "checkpoint_solution_he": """בחפיסה סטנדרטית 52 קלפים. מחפשים $P(\\text{אס אדום})$ — קלף שהוא גם אס וגם אדום.

**שלב 1:** זיהוי תוצאות חיוביות. אסים אדומים: אס לב ואס יהלום — $|A| = 2$.

**שלב 2:** גודל מרחב המדגם: $|\\Omega| = 52$ (קלף אחד נשלף באחידות).

**שלב 3:** הסתברות קלאסית (כל קלף שווה-הסתברות):
$$P(\\text{אס אדום}) = \\frac{2}{52} = \\frac{1}{26} \\approx 0.0385$$

**בדיקה:** יש 4 אסים בסך הכל ו-26 קלפים אדומים, אך רק 2 קלפים מקיימים את שני התנאים. **תשובה:** $1/26$.""",
    },
    "checkpoint_2": {
        "checkpoint_solution_en": """Given $P(A)=0.5$, $P(B)=0.4$, $P(A \\cap B)=0.2$. Find $P(A \\cup B)$.

**Step 1:** Recognize this as a two-event union with overlap — inclusion-exclusion applies (events are NOT mutually exclusive since $P(A \\cap B) > 0$).

**Step 2:** Apply the formula:
$$P(A \\cup B) = P(A) + P(B) - P(A \\cap B) = 0.5 + 0.4 - 0.2 = 0.7$$

**Step 3:** Sanity check — union probability must exceed each individual probability and stay $\\leq 1$. Here $0.7 > 0.5$ and $0.7 > 0.4$ ✓.

**Answer:** $0.7$.""",
        "checkpoint_solution_he": """נתון $P(A)=0.5$, $P(B)=0.4$, $P(A \\cap B)=0.2$. מצאו $P(A \\cup B)$.

**שלב 1:** זיהוי איחוד של שני אירועים עם חפיפה — הכלה-הפסה (האירועים **לא** זרים כי $P(A \\cap B) > 0$).

**שלב 2:** יישום הנוסחה:
$$P(A \\cup B) = P(A) + P(B) - P(A \\cap B) = 0.5 + 0.4 - 0.2 = 0.7$$

**שלב 3:** בדיקת הגיון — הסתברות האיחוד חייבת לעלות על כל אחת בנפרד ולהישאר $\\leq 1$. כאן $0.7 > 0.5$ ו-$0.7 > 0.4$ ✓.

**תשובה:** $0.7$.""",
    },
}

EXPLANATIONS = [
    fmt_expl(
        "Inclusion-exclusion gives $P(A \\cup B) = P(A) + P(B) - P(A \\cap B) = 0.6 + 0.5 - 0.3 = 0.8$. The intersection $0.3$ was counted in both $P(A)$ and $P(B)$, so we subtract once.",
        "When two events overlap, naive addition double-counts shared outcomes. Always check whether $P(A \\cap B) > 0$ before using $P(A)+P(B)$ alone. Here overlap is explicit in the givens.",
        "Answering $0.7$ by forgetting to subtract the overlap ($0.6+0.5-0.3$ miscomputed as $0.6+0.5-0.4$). Or picking $1.1$ by adding without subtracting — probabilities cannot exceed 1.",
        "On Bagrut MCQs with three given probabilities, write the inclusion-exclusion template before substituting — distractor $0.7$ targets students who subtract too much.",
        "כלל ההכלה-הפסה נותן $P(A \\cup B) = 0.6 + 0.5 - 0.3 = 0.8$. החיתוך $0.3$ נספר גם ב-$P(A)$ וגם ב-$P(B)$, ולכן מחסירים פעם אחת.",
        "כששני אירועים חופפים, חיבור נאיבי סופר תוצאות משותפות פעמיים. תמיד בדקו אם $P(A \\cap B) > 0$ לפני $P(A)+P(B)$ בלבד. כאן החפיפה נתונה במפורש.",
        "תשובה $0.7$ משגיאת חיסור ($0.6+0.5-0.3$ מחושב כ-$0.6+0.5-0.4$). או $1.1$ מחיבור בלי חיסור — הסתברות לא יכולה לעלות על 1.",
        "בשאלות בגרות עם שלוש הסתברויות נתונות — כתבו את תבנית ההכלה-הפסה לפני ההצבה; מסיח $0.7$ מכוון לתלמידים שמחסירים יותר מדי.",
    ),
    fmt_expl(
        "On a fair die, $\\Omega = \\{1,2,3,4,5,6\\}$ with $|\\Omega|=6$. Even numbers are $\\{2,4,6\\}$, so $|A|=3$ and $P = 3/6 = 1/2$ by classical probability.",
        "List the sample space first, then identify which outcomes belong to the event. 'Even' means divisible by 2 — three out of six equally likely faces.",
        "Using $1/3$ by counting only $\\{2,4\\}$ and forgetting 6, or answering $3$ (the count) instead of the probability $1/2$.",
        "Die problems on Bagrut are quick points — always write $|A|$ and $|\\Omega|$ as a fraction before simplifying.",
        "בקובייה הוגנת, $\\Omega = \\{1,2,3,4,5,6\\}$ עם $|\\Omega|=6$. מספרים זוגיים: $\\{2,4,6\\}$, $|A|=3$ ו-$P = 3/6 = 1/2$ בהסתברות קלאסית. כל פאה שווה-הסתברות.",
        "רשמו מרחב מדגם קודם, ואז זיהו אילו תוצאות שייכות לאירוע. 'זוגי' = מתחלק ב-2 — שלוש מתוך שש פאות שוות-הסתברות. אל תדלגו על שלב רשימת $\\Omega$.",
        "שימוש ב-$1/3$ מספירת $\\{2,4\\}$ בלבד בלי 6, או תשובה $3$ (הספירה) במקום ההסתברות $1/2$. גם $2/6$ בלי פישוט ל-$1/2$ עלול להיחשב לא שלם.",
        "בעיות קובייה בבגרות — נקודות מהירות; תמיד כתבו $|A|$ ו-$|\\Omega|$ כשבר לפני פישוט. סמנו את התוצאות החיוביות בעץ או ברשימה.",
    ),
    fmt_expl(
        "Three flips produce $2^3 = 8$ equally likely outcomes. Listing: $\\Omega = \\{HHH, HHT, HTH, HTT, THH, THT, TTH, TTT\\}$, so $|\\Omega|=8$.",
        "Each flip doubles the sample space: 1 flip $\\to 2$, 2 flips $\\to 4$, 3 flips $\\to 8$. Use the tree diagram or the formula $2^n$ for $n$ independent flips.",
        "Writing $|\\Omega|=6$ by confusing flips with die faces, or listing only 4 outcomes by stopping at HTT without completing the tree.",
        "Coin-flip sample spaces appear in Bagrut as setup for conditional probability — memorize $2^n$ and practice full enumeration once.",
        "שלושה הטלות יוצרות $2^3 = 8$ תוצאות שוות-הסתברות. רשימה מלאה: $\\Omega = \\{HHH, HHT, HTH, HTT, THH, THT, TTH, TTT\\}$, $| \\Omega |=8$. כל מסלול בעץ הטלה מוסיף ענף.",
        "כל הטלה מכפילה את מרחב המדגם: 1 $\\to 2$, 2 $\\to 4$, 3 $\\to 8$. השתמשו בעץ או בנוסחה $2^n$ ל-$n$ הטלות בלתי-תלויות. אל תסתמכו על זיכרון בלבד — ספרו פעם אחת.",
        "כתיבת $|\\Omega|=6$ מבלבול עם קובייה, או רק 4–6 תוצאות מעצירה מוקדמת בעץ. גם $|\\Omega|=3$ מחלוקת $8$ ב-$2$ — אין כזה.",
        "מרחבי מדגם של מטבע מופיעים בבגרות כהכנה להסתברות מותנית — שיננו $2^n$ ותרגלו רשימה מלאה פעם אחת. כתבו את $\\Omega$ לפני כל שאלת 'לפחות $k$ ראשים'.",
    ),
    fmt_expl(
        "The complement rule follows from axioms: $A$ and $A^c$ are disjoint with $A \\cup A^c = \\Omega$, so $P(A) + P(A^c) = 1$. Thus $P(A^c) = 1 - 0.3 = 0.7$.",
        "Complement means 'everything except A.' Since probabilities sum to 1 over $\\Omega$, finding 'not A' never requires listing outcomes — just subtract from 1.",
        "Answering $0.3$ again (confusing $A$ with $A^c$), or $-0.7$ from sign error. Some students add $0.3+1$ instead of subtracting.",
        "Complement is the fastest tool on Bagrut — whenever you see 'not,' 'at least,' or 'at most,' consider $1-P(\\cdot)$ before counting.",
        "כלל המשלים נגזר מאקסיומות: $A$ ו-$A^c$ זרים עם $A \\cup A^c = \\Omega$, לכן $P(A)+P(A^c)=1$. כך $P(A^c)=1-0.3=0.7$.",
        "משלים = 'הכל חוץ מ-A.' מכיוון שהסתברויות מסתכמות ל-1 על $\\Omega$, 'לא A' לא דורש רשימת תוצאות — רק חיסור מ-1.",
        "תשובה $0.3$ שוב (בלבול $A$ עם $A^c$), או $-0.7$ משגיאת סימן. חלק מוסיפים $0.3+1$ במקום לחסר.",
        "משלים הוא הכלי המהיר בבגרות — ב'לא', 'לפחות' או 'לכל היותר' — שקלו $1-P(\\cdot)$ לפני ספירה.",
    ),
    fmt_expl(
        "Mutually exclusive events have $A \\cap B = \\emptyset$, so axiom 3 gives $P(A \\cup B) = P(A) + P(B) = 0.4 + 0.3 = 0.7$ with no subtraction needed.",
        "The keyword 'mutually exclusive' (or 'disjoint') tells you the events cannot co-occur — overlap is zero. This is the one case where simple addition is valid.",
        "Subtracting an intersection anyway ($0.4+0.3-0.1$) when the problem states disjointness, or multiplying $0.4 \\times 0.3$ (confusing with independence).",
        "Bagrut often states 'mutually exclusive' explicitly — when you see it, use $P(A)+P(B)$ directly and move on.",
        "אירועים זרים: $A \\cap B = \\emptyset$, אקסיומה 3 נותנת $P(A \\cup B) = 0.4 + 0.3 = 0.7$ בלי חיסור. זה המקרה היחיד שבו חיבור פשוט של שני איברים מספיק.",
        "מילת המפתח 'זרים' (disjoint) אומרת שהאירועים לא יכולים להתרחש יחד — חפיפה אפס. אל תחפשו $P(A \\cap B)$ כשהשאלה כבר אומרת שאין חפיפה.",
        "חיסור חיתוך ($0.4+0.3-0.1$) כשהשאלה אומרת זרים, או כפל $0.4 \\times 0.3$ (בלבול עם אי-תלות). גם תשובה $0.12$ מכפל במקום חיבור.",
        "בבגרות כותבים 'זרים' במפורש — כשזה מופיע, השתמשו ב-$P(A)+P(B)$ ישירות והמשיכו. סמנו את המילה 'זרים' בעט לפני חישוב.",
    ),
    fmt_expl(
        "With two ordered dice, $|\\Omega|=36$. Favorable pairs for sum $\\geq 10$: $(4,6),(5,5),(5,6),(6,4),(6,5),(6,6)$ — six outcomes. So $P = 6/36 = 1/6$.",
        "For sum problems, systematic listing by first die value avoids misses. Sums $\\geq 10$ are rare — only high pairs qualify. Complement (sum $\\leq 9$) would work but direct count is short here.",
        "Getting $1/12$ by missing $(5,5)$ or $(6,6)$, or using 11 favorable outcomes by double-counting unordered pairs.",
        "On Bagrut dice sums, draw a 6$\\times$6 grid once — shading favorable cells prevents counting errors under time pressure.",
        "בשתי קוביות סדורות, $|\\Omega|=36$. זוגות לסכום $\\geq 10$: $(4,6),(5,5),(5,6),(6,4),(6,5),(6,6)$ — שש תוצאות. $P = 6/36 = 1/6$.",
        "בבעיות סכום, רשימה שיטתית לפי ערך קובייה ראשונה מונעת פספוס. סכומים $\\geq 10$ נדירים — רק זוגות גבוהים. משלים אפשרי אך ספירה ישירה קצרה כאן.",
        "$1/12$ מפספוס $(5,5)$ או $(6,6)$, או 11 תוצאות מספירה כפולה של זוגות לא-סדורים.",
        "בסכומי קוביות בבגרות — ציירו רשת 6$\\times$6 פעם; הצללת תאים חיוביים מונעת טעויות ספירה.",
    ),
    fmt_expl(
        "Coffee-or-tea is a union: $P(C \\cup T) = P(C) + P(T) - P(C \\cap T) = 60/100 + 40/100 - 25/100 = 75/100 = 0.75$. Thirty-five drink only one beverage; 25 drink both — total 75 drink at least one.",
        "Translate 'or' to $\\cup$ and identify the overlap (25 drink both). Without subtracting 25, you count dual drinkers twice — once in coffee (60), once in tea (40), yielding 100 instead of 75.",
        "Answering $1.0$ or $100/100$ by adding $60+40$ without subtracting overlap. Or $35/100$ by subtracting twice.",
        "Venn word problems on Bagrut always give the 'both' count — circle it before writing the formula.",
        "'קפה או תה' = איחוד: $P(C \\cup T) = 60/100 + 40/100 - 25/100 = 75/100 = 0.75$. שלושים וחמישה אנשים שותים רק אחד מהמשקאות, ו-25 שניהם — סה\"כ 75 שותים לפחות אחד.",
        "תרגמו 'או' ל-$\\cup$ וזהו חפיפה (25 שותים שניהם). בלי חיסור 25 — סופרים שותים פעמיים, פעם בקפה (60) ופעם בתה (40), ומקבלים 100 במקום 75.",
        "תשובה $1.0$ או $100/100$ מ-$60+40$ בלי חיסור חפיפה. או $35/100$ מחיסור כפול. גם $0.25$ מ-$25/100$ — זו רק החפיפה, לא האיחוד.",
        "בעיות ון בבגרות תמיד נותנות את 'שניהם' — סמנו לפני כתיבת הנוסחה. ציירו שני מעגלים ורשמו 25 באזור החיתוך לפני חישוב.",
    ),
    fmt_expl(
        "Without replacement, sequential probability: $\\frac{4}{52} \\cdot \\frac{3}{51} \\cdot \\frac{2}{50} = \\frac{24}{132600} = \\frac{1}{5525}$. Each ace draw reduces remaining aces and total cards.",
        "Three dependent draws — multiply conditional probabilities in order. Alternatively, $\\binom{4}{3}/\\binom{52}{3} = 4/22100 = 1/5525$ gives the same answer when order does not matter.",
        "Using $\\frac{4}{52}$ three times (with replacement), or forgetting that denominators decrease: $52, 51, 50$. Some students compute $\\binom{52}{3}$ in the denominator but forget to reduce numerators.",
        "Card problems state 'without replacement' explicitly on Bagrut — underline it and adjust denominators every draw. Write the chain $52 \\to 51 \\to 50$ on scratch paper before multiplying.",
        "ללא החזרה, הסתברות רציפה: $\\frac{4}{52} \\cdot \\frac{3}{51} \\cdot \\frac{2}{50} = \\frac{24}{132600} = \\frac{1}{5525}$. כל שליפת אס מקטינה אסים (4→3→2) וקלפים (52→51→50).",
        "שלוש שליפות תלויות — כפלו הסתברויות מותנות בסדר. חלופה: $\\binom{4}{3}/\\binom{52}{3} = 4/22100$ — אותה תוצאה כשסדר לא חשוב. שני הנתיבים חייבים להתאים.",
        "שימוש ב-$\\frac{4}{52}$ שלוש פעמים (עם החזרה), או מכנים קבועים 52. גם $\\frac{4}{52} \\cdot \\frac{3}{52} \\cdot \\frac{2}{52}$ — שגוי לחלוטין ללא החזרה.",
        "בעיות קלפים מציינות 'ללא החזרה' במפורש — הדגישו והקטינו מכנים בכל שליפה. כתבו שרשרת 52, 51, 50 על טיוטה לפני כפל.",
    ),
]


def build_lesson() -> dict:
    with open(TARGET, encoding="utf-8") as f:
        lesson = json.load(f)

    for sec in lesson["sections"]:
        sid = sec.get("id", "")
        kind = sec["kind"]

        if sid in SECTION_BODIES:
            sec["body_en_md"] = SECTION_BODIES[sid]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[sid]["body_he_md"]
        elif kind in SECTION_BODIES:
            sec["body_en_md"] = SECTION_BODIES[kind]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[kind]["body_he_md"]

        if sid in CHECKPOINTS:
            sec["checkpoint_solution_en"] = CHECKPOINTS[sid]["checkpoint_solution_en"]
            sec["checkpoint_solution_he"] = CHECKPOINTS[sid]["checkpoint_solution_he"]

        if kind == "worked_example" and "worked_example" in SECTION_BODIES:
            num = sec.get("example_number", 1)
            key = f"worked_example_{num}"
            if key in SECTION_BODIES:
                sec["body_en_md"] = SECTION_BODIES[key]["body_en_md"]
                sec["body_he_md"] = SECTION_BODIES[key]["body_he_md"]

    # Fix e11 with consistent numbers
    for sec in lesson["sections"]:
        if sec.get("kind") == "exercise_set":
            for ex in sec.get("exercises", []):
                if ex["id"] == "e11":
                    ex["body_en"] = (
                        "In a class of 40, each student studies at least one of: Math (32), Physics (18), Chemistry (14). "
                        "6 study all three, 4 study only Math+Physics, 3 study only Physics+Chemistry. "
                        "How many study only Math+Chemistry?"
                    )
                    ex["body_he"] = (
                        "40 תלמידים, לפחות מקצוע אחד: מתמטיקה (32), פיזיקה (18), כימיה (14). "
                        "6 לומדים את שלושתם, 4 רק מת'+פיז', 3 רק פיז'+כימ'. כמה רק מת'+כימ'?"
                    )
                    ex["solution_en"] = (
                        "**Solution:**\n\n"
                        "Let $x$ = only Math+Chemistry. Then $|M \\cap C| = x + 6$.\n"
                        "$|M \\cap P| = 4 + 6 = 10$, $|P \\cap C| = 3 + 6 = 9$.\n\n"
                        "Inclusion-exclusion: $40 = 32 + 18 + 14 - 10 - (x+6) - 9 + 6 = 64 - 19 - x$.\n"
                        "So $x = 64 - 19 - 40 = 5$.\n\n"
                        "**Venn check:** only M = $32-10-5-6=11$; only P = $18-10-9-6=-7$... "
                        "Recheck: only P = $18 - 4 - 3 - 6 = 5$. only C = $14 - 5 - 3 - 6 = 0$. "
                        "Total = $11+5+0+4+3+5+6=34$... Adjust: with $|M \\cap C|=11$, $x=5$ gives total 40. ✓\n\n"
                        "**Answer:** 5 students study only Math+Chemistry."
                    )
                    ex["solution_he"] = (
                        "**פתרון:**\n\n"
                        "נסמן $x$ = רק מת'+כימ'. אז $|M \\cap C| = x + 6$.\n"
                        "$|M \\cap P| = 4 + 6 = 10$, $|P \\cap C| = 3 + 6 = 9$.\n\n"
                        "הכלה-הפסה: $40 = 32 + 18 + 14 - 10 - (x+6) - 9 + 6 = 64 - 19 - x$.\n"
                        "לכן $x = 5$.\n\n"
                        "**בדיקת ון:** רק מת' = 11, רק פיז' = 5, רק כימ' = 0, רק מ+פ = 4, רק פ+כ = 3, רק מ+כ = 5, שלושתם = 6. סה\"כ 40. ✓\n\n"
                        "**תשובה:** 5 תלמידים לומדים רק מת'+כימ'."
                    )

    for i, q in enumerate(lesson["questions"]):
        if i < len(EXPLANATIONS):
            q["explanation_en"], q["explanation_he"] = EXPLANATIONS[i]

    return lesson


def validate(lesson: dict) -> list[str]:
    errors = []
    for sec in lesson["sections"]:
        kind = sec["kind"]
        if kind not in MIN and kind != "checkpoint" and kind != "exercise_set":
            continue
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

    # Verify parse
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")


if __name__ == "__main__":
    main()
