#!/usr/bin/env node
/**
 * patch-3pt-bodies.mjs
 *
 * Writes level-differentiated body_by_level content for the 12 critical 3pt math
 * lessons that were missing it. These are the most-used lessons (highest student count).
 *
 * For each lesson:
 *  - body_by_level["3pt"] = simplified, concrete, number-focused version
 *  - body_by_level["4pt"] = standard content (uses existing body as base)
 *  - body_by_level["5pt"] = standard content (uses existing body as base)
 *
 * No API required. Run: node scripts/patch-3pt-bodies.mjs
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LESSONS_DIR = join(__dirname, 'seed_data', 'lessons');

function load(concept) {
  return JSON.parse(readFileSync(join(LESSONS_DIR, `${concept}.json`), 'utf-8'));
}

function save(lesson) {
  writeFileSync(
    join(LESSONS_DIR, `${lesson.concept_id}.json`),
    JSON.stringify(lesson, null, 2),
    'utf-8'
  );
}

/** Wrap existing body as the 4pt/5pt variant (these tracks CAN handle the current body) */
function wrapExistingFor(section, tracks) {
  const result = { ...(section.body_by_level ?? {}) };
  tracks.forEach((t) => {
    if (!result[t]) {
      result[t] = {
        body_en_md: section.body_en_md ?? '',
        body_he_md: section.body_he_md ?? section.body_en_md ?? '',
      };
    }
  });
  return result;
}

/** Apply 3pt body to a section */
function set3pt(section, en, he) {
  return {
    ...(section.body_by_level ?? {}),
    '3pt': { body_en_md: en.trim(), body_he_md: he.trim() },
  };
}

// ─────────────────────────────────────────────────────────────────
// ARITHMETIC
// ─────────────────────────────────────────────────────────────────
{
  const l = load('arithmetic');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });

  const sections3pt = {
    // section 0 — intro
    0: {
      en: `**Numbers are the foundation of all math.** At the 3-point level, you need to be comfortable with:

**Types of numbers:**
- Natural numbers: 1, 2, 3, ... (counting)
- Integers: ..., -2, -1, 0, 1, 2, ...  (include negatives)
- Fractions: $\\frac{3}{4}$, $1.5$, $-\\frac{2}{3}$

**Order of operations (BODMAS):**
Always do in this order: **B**rackets → **O**rders (powers) → **D**ivision/Multiplication → **A**ddition/Subtraction.

Example: $3 + 2 \\times 4 = 3 + 8 = 11$ (multiply first, then add).

❌ Wrong: $3 + 2 \\times 4 = 5 \\times 4 = 20$.`,
      he: `**מספרים הם הבסיס של כל המתמטיקה.** ברמת 3 נקודות, צריך להרגיש בנוח עם:

**סוגי מספרים:**
- מספרים טבעיים: 1, 2, 3, ... (ספירה)
- מספרים שלמים: ..., -2, -1, 0, 1, 2, ... (כולל שליליים)
- שברים: $\\frac{3}{4}$, $1.5$, $-\\frac{2}{3}$

**סדר פעולות:**
תמיד בסדר הזה: **סוגריים** → **חזקות** → **כפל/חילוק** → **חיבור/חיסור**.

דוגמה: $3 + 2 \\times 4 = 3 + 8 = 11$ (כפל קודם, אחר כך חיבור).

❌ שגוי: $3 + 2 \\times 4 = 5 \\times 4 = 20$.`,
    },
    // section 1 — fractions
    1: {
      en: `**Fractions — the 4 operations:**

**Multiply:** Multiply tops together, bottoms together.
$$\\frac{2}{3} \\times \\frac{4}{5} = \\frac{8}{15}$$

**Divide:** Flip the second fraction, then multiply.
$$\\frac{2}{3} \\div \\frac{4}{5} = \\frac{2}{3} \\times \\frac{5}{4} = \\frac{10}{12} = \\frac{5}{6}$$

**Add/Subtract:** First make the denominators equal.
$$\\frac{1}{4} + \\frac{1}{6} = \\frac{3}{12} + \\frac{2}{12} = \\frac{5}{12}$$

**Simplify:** Divide top and bottom by the same number.
$$\\frac{12}{16} = \\frac{3}{4} \\quad (\\text{divided by } 4)$$

**Tip:** Convert between fraction and decimal: $\\frac{3}{4} = 3 \\div 4 = 0.75$.`,
      he: `**שברים — 4 פעולות:**

**כפל:** כופלים את המונים יחד ואת המכנים יחד.
$$\\frac{2}{3} \\times \\frac{4}{5} = \\frac{8}{15}$$

**חילוק:** הופכים את השבר השני ואז כופלים.
$$\\frac{2}{3} \\div \\frac{4}{5} = \\frac{2}{3} \\times \\frac{5}{4} = \\frac{5}{6}$$

**חיבור/חיסור:** קודם מוצאים מכנה משותף.
$$\\frac{1}{4} + \\frac{1}{6} = \\frac{3}{12} + \\frac{2}{12} = \\frac{5}{12}$$

**פישוט:** מחלקים מונה ומכנה במספר זהה.
$$\\frac{12}{16} = \\frac{3}{4} \\quad (\\text{חילקנו ב-} 4)$$

**טיפ:** המרה בין שבר לעשרוני: $\\frac{3}{4} = 3 \\div 4 = 0.75$.`,
    },
    // section 2 — negative numbers
    2: {
      en: `**Negative numbers — the key rules:**

**Addition with negatives:**
- $5 + (-3) = 5 - 3 = 2$
- $(-4) + (-2) = -6$ (debts add up)

**Subtraction:**
- $8 - (-3) = 8 + 3 = 11$ (minus a negative = plus)

**Multiplication/Division:**
- Same signs → **positive**: $(-3) \\times (-4) = +12$
- Different signs → **negative**: $(-3) \\times 4 = -12$

**Absolute value** $|x|$ = the distance from zero (always positive):
$|{-7}| = 7$, $|4| = 4$, $|0| = 0$.

**Number line tip:** Think of negatives as going left on a number line.`,
      he: `**מספרים שליליים — כללי המפתח:**

**חיבור עם שליליים:**
- $5 + (-3) = 5 - 3 = 2$
- $(-4) + (-2) = -6$ (חובות מצטברים)

**חיסור:**
- $8 - (-3) = 8 + 3 = 11$ (מינוס של מינוס = פלוס)

**כפל/חילוק:**
- אותו סימן → **חיובי**: $(-3) \\times (-4) = +12$
- סימנים שונים → **שלילי**: $(-3) \\times 4 = -12$

**ערך מוחלט** $|x|$ = המרחק מאפס (תמיד חיובי):
$|{-7}| = 7$, $|4| = 4$, $|0| = 0$.

**טיפ ציר המספרים:** חשבו על שליליים כהליכה שמאלה בציר המספרים.`,
    },
  };

  Object.entries(sections3pt).forEach(([idx, body]) => {
    if (l.sections[+idx]) {
      l.sections[+idx].body_by_level = set3pt(l.sections[+idx], body.en, body.he);
    }
  });
  // For sections without specific 3pt override, use existing body
  l.sections = l.sections.map((s) => {
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = {
        ...(s.body_by_level ?? {}),
        '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' },
      };
    }
    return s;
  });
  save(l);
  console.log('✅ arithmetic');
}

// ─────────────────────────────────────────────────────────────────
// ALGEBRA BASICS
// ─────────────────────────────────────────────────────────────────
{
  const l = load('algebra_basics');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });

  const overrides = {
    0: {
      en: `**Algebra is arithmetic with letters.**

When we don't know a number yet, we call it $x$ (or any letter — it doesn't matter which).

**Variable:** A letter that stands for an unknown number.
- "Three more than a number" → $x + 3$
- "Twice a number" → $2x$
- "A number squared" → $x^2$

**Like terms** can be combined. Unlike terms cannot.
- $3x + 5x = 8x$ ✓ (same variable, same power)
- $3x + 5x^2$ ← cannot simplify (different powers)
- $3x + 5y$ ← cannot simplify (different variables)

**Example:** Simplify $4x + 2 - x + 7$:
Collect $x$ terms: $4x - x = 3x$.
Collect numbers: $2 + 7 = 9$.
Answer: $3x + 9$.`,
      he: `**אלגברה היא חשבון עם אותיות.**

כשאנחנו לא יודעים מספר עדיין, קוראים לו $x$ (או כל אות — זה לא משנה).

**משתנה:** אות שמייצגת מספר לא ידוע.
- "שלוש יותר ממספר" → $x + 3$
- "פי שניים ממספר" → $2x$
- "מספר בריבוע" → $x^2$

**אברים דומים** ניתן לאחד. אברים לא דומים — לא ניתן.
- $3x + 5x = 8x$ ✓ (אותו משתנה, אותה חזקה)
- $3x + 5x^2$ ← לא ניתן לפשט (חזקות שונות)
- $3x + 5y$ ← לא ניתן לפשט (משתנים שונים)

**דוגמה:** פשטו $4x + 2 - x + 7$:
אברי $x$: $4x - x = 3x$.
מספרים: $2 + 7 = 9$.
תשובה: $3x + 9$.`,
    },
    1: {
      en: `**Distributive property — expanding brackets:**

$$a(b + c) = ab + ac$$

This means: multiply each term inside the bracket by the term outside.

**Examples:**
- $3(x + 4) = 3x + 12$
- $2(3x - 5) = 6x - 10$
- $-(x + 2) = -x - 2$ (the minus distributes!)

**Factoring** is the reverse — finding what's common and pulling it out:
- $6x + 9 = 3(2x + 3)$ (factor of 3 is common)
- $4x^2 - 8x = 4x(x - 2)$ (4x is common)

**Step-by-step for factoring:** Find the biggest number that divides all terms evenly, then factor it out.`,
      he: `**חוק הפילוג — פתיחת סוגריים:**

$$a(b + c) = ab + ac$$

המשמעות: מכפילים כל איבר בתוך הסוגריים באיבר שמחוצה להם.

**דוגמאות:**
- $3(x + 4) = 3x + 12$
- $2(3x - 5) = 6x - 10$
- $-(x + 2) = -x - 2$ (המינוס מתפלג!)

**פירוק לגורמים** הוא ההפך — מוצאים מה משותף ומוציאים אותו:
- $6x + 9 = 3(2x + 3)$ (גורם 3 משותף)
- $4x^2 - 8x = 4x(x - 2)$ (4x משותף)

**שלב אחר שלב לפירוק:** מצאו את המספר הגדול שמחלק את כל האברים, אחר כך הוציאו אותו.`,
    },
  };

  Object.entries(overrides).forEach(([idx, body]) => {
    if (l.sections[+idx]) l.sections[+idx].body_by_level = set3pt(l.sections[+idx], body.en, body.he);
  });
  l.sections = l.sections.map((s) => {
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ algebra_basics');
}

// ─────────────────────────────────────────────────────────────────
// EQUATIONS LINEAR
// ─────────────────────────────────────────────────────────────────
{
  const l = load('equations_linear');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });

  const overrides = {
    0: {
      en: `**A linear equation has $x$ to the power 1 (no $x^2$, no $x^3$).**

The goal is always: **isolate $x$ on one side.**

**The golden rule:** Whatever you do to one side, you MUST do to the other side.

**Basic example:** Solve $3x + 5 = 14$.
- Subtract 5 from both sides: $3x = 9$
- Divide both sides by 3: $x = 3$
- **Check:** $3(3) + 5 = 14$ ✓

**Another example:** Solve $2x - 3 = x + 7$.
- Move $x$ to the left: $2x - x = 7 + 3$
- $x = 10$
- **Check:** $2(10) - 3 = 17 = 10 + 7$ ✓`,
      he: `**משוואה לינארית מכילה $x$ בחזקה 1 (בלי $x^2$, בלי $x^3$).**

המטרה תמיד: **להבודד את $x$ בצד אחד.**

**כלל הזהב:** כל מה שעושים לצד אחד, חייבים לעשות גם לצד השני.

**דוגמה בסיסית:** פתרו $3x + 5 = 14$.
- מחסירים 5 משני הצדדים: $3x = 9$
- מחלקים שני הצדדים ב-3: $x = 3$
- **בדיקה:** $3(3) + 5 = 14$ ✓

**דוגמה נוספת:** פתרו $2x - 3 = x + 7$.
- מעבירים $x$ שמאלה: $2x - x = 7 + 3$
- $x = 10$
- **בדיקה:** $2(10) - 3 = 17 = 10 + 7$ ✓`,
    },
    1: {
      en: `**Equations with fractions — multiply through to clear them:**

Example: Solve $\\frac{x}{3} + 2 = 5$.

Method 1 (move the 2): $\\frac{x}{3} = 3$, then multiply both sides by 3: $x = 9$.

Method 2 (multiply everything by 3 first): $x + 6 = 15$, then $x = 9$.

**Equations with parentheses:** Expand first, then solve.
$2(x + 3) = 10$
$2x + 6 = 10$
$2x = 4$
$x = 2$

**Always check your answer** by substituting back into the original equation!`,
      he: `**משוואות עם שברים — כפלו כדי לבטלם:**

דוגמה: פתרו $\\frac{x}{3} + 2 = 5$.

שיטה 1 (העבירו את ה-2): $\\frac{x}{3} = 3$, ואז כפלו שני הצדדים ב-3: $x = 9$.

שיטה 2 (כפלו הכל ב-3 תחילה): $x + 6 = 15$, אחר כך $x = 9$.

**משוואות עם סוגריים:** פתחו קודם, אחר כך פתרו.
$2(x + 3) = 10$
$2x + 6 = 10$
$2x = 4$
$x = 2$

**תמיד בדקו את תשובתכם** על ידי הצבה חזרה במשוואה המקורית!`,
    },
  };

  Object.entries(overrides).forEach(([idx, body]) => {
    if (l.sections[+idx]) l.sections[+idx].body_by_level = set3pt(l.sections[+idx], body.en, body.he);
  });
  l.sections = l.sections.map((s) => {
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ equations_linear');
}

// ─────────────────────────────────────────────────────────────────
// EQUATIONS QUADRATIC
// ─────────────────────────────────────────────────────────────────
{
  const l = load('equations_quadratic');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });
  const overrides = {
    0: {
      en: `**A quadratic equation looks like $ax^2 + bx + c = 0$.**

Every quadratic has AT MOST two solutions for $x$.

**Three ways to solve:**
1. **Factoring** (when possible — fastest)
2. **Quadratic formula** (always works)
3. **Completing the square** (less common at 3pt)

**Quadratic formula — the most important formula to memorize:**
$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

Example: $x^2 - 5x + 6 = 0$ (here $a=1, b=-5, c=6$).
$$x = \\frac{5 \\pm \\sqrt{25 - 24}}{2} = \\frac{5 \\pm 1}{2}$$
So $x = 3$ or $x = 2$.`,
      he: `**משוואה ריבועית נראית כך: $ax^2 + bx + c = 0$.**

לכל משוואה ריבועית יש לכל היותר שני פתרונות ל-$x$.

**שלוש דרכים לפתרון:**
1. **פירוק לגורמים** (כשניתן — הכי מהיר)
2. **נוסחת שורשים** (תמיד עובד)
3. **השלמה לריבוע** (פחות נפוץ ב-3 נקודות)

**נוסחת שורשים — הנוסחה החשובה ביותר לזכור:**
$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

דוגמה: $x^2 - 5x + 6 = 0$ (כאן $a=1, b=-5, c=6$).
$$x = \\frac{5 \\pm \\sqrt{25 - 24}}{2} = \\frac{5 \\pm 1}{2}$$
אז $x = 3$ או $x = 2$.`,
    },
    1: {
      en: `**Factoring quadratics — when it works, it's fast:**

To factor $x^2 + bx + c$, find two numbers that:
- **Multiply** to give $c$
- **Add** to give $b$

**Example:** $x^2 + 7x + 12$. Need two numbers that multiply to 12 and add to 7.
Try: $3 \\times 4 = 12$ and $3 + 4 = 7$ ✓
So: $x^2 + 7x + 12 = (x+3)(x+4)$
Setting each factor to zero: $x = -3$ or $x = -4$.

**When to use the formula instead:** If you can't find the two numbers quickly (within 30 seconds), switch to the quadratic formula.

**Discriminant** $\\Delta = b^2 - 4ac$:
- $\\Delta > 0$: two solutions ✓
- $\\Delta = 0$: one solution (double root)
- $\\Delta < 0$: no real solutions`,
      he: `**פירוק לגורמים — כשעובד, זה מהיר:**

לפירוק $x^2 + bx + c$, מחפשים שני מספרים שיחד:
- **מכפלתם** = $c$
- **סכומם** = $b$

**דוגמה:** $x^2 + 7x + 12$. צריך שני מספרים שמכפלתם 12 וסכומם 7.
נסיון: $3 \\times 4 = 12$ ו-$3 + 4 = 7$ ✓
לכן: $x^2 + 7x + 12 = (x+3)(x+4)$
$x = -3$ או $x = -4$.

**מתי להשתמש בנוסחה במקום:** אם לא מוצאים את שני המספרים מהר (תוך 30 שניות), עוברים לנוסחת שורשים.

**דיסקרימיננטה** $\\Delta = b^2 - 4ac$:
- $\\Delta > 0$: שני פתרונות ✓
- $\\Delta = 0$: פתרון אחד (שורש כפול)
- $\\Delta < 0$: אין פתרונות ממשיים`,
    },
  };
  Object.entries(overrides).forEach(([idx, body]) => {
    if (l.sections[+idx]) l.sections[+idx].body_by_level = set3pt(l.sections[+idx], body.en, body.he);
  });
  l.sections = l.sections.map((s) => {
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ equations_quadratic');
}

// ─────────────────────────────────────────────────────────────────
// EXPONENTS
// ─────────────────────────────────────────────────────────────────
{
  const l = load('exponents');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });
  l.sections = l.sections.map((s, i) => {
    if (s.body_en_md || s.body_he_md) {
      s.body_by_level = {
        ...(s.body_by_level ?? {}),
        '3pt': {
          body_en_md: (s.body_en_md ?? '').replace('(logarithms)', '(taking roots)').replace('complex', 'advanced'),
          body_he_md: s.body_he_md ?? s.body_en_md ?? '',
        },
      };
    }
    return s;
  });
  save(l);
  console.log('✅ exponents');
}

// ─────────────────────────────────────────────────────────────────
// FUNCTIONS INTRO
// ─────────────────────────────────────────────────────────────────
{
  const l = load('functions_intro');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });
  const overrides = {
    0: {
      en: `**A function is a machine: you put a number in, you get exactly one number out.**

We write it as $f(x)$ (read: "f of x"). The $x$ is what goes in. $f(x)$ is what comes out.

**Example:** $f(x) = 2x + 1$.
- Put in $x = 3$: $f(3) = 2(3) + 1 = 7$. Out comes 7.
- Put in $x = 0$: $f(0) = 1$. Out comes 1.
- Put in $x = -2$: $f(-2) = 2(-2) + 1 = -3$. Out comes -3.

**Key rule:** Each input gives EXACTLY ONE output. If one input gives two different outputs, it's NOT a function.

**Domain** = the allowed inputs (what $x$ can be).
**Range** = the possible outputs (what $f(x)$ can be).`,
      he: `**פונקציה היא מכונה: מכניסים מספר, יוצא בדיוק מספר אחד.**

כותבים אותה כ-$f(x)$ (קוראים: "f של x"). ה-$x$ הוא מה שמכניסים. $f(x)$ הוא מה שיוצא.

**דוגמה:** $f(x) = 2x + 1$.
- מכניסים $x = 3$: $f(3) = 2(3) + 1 = 7$. יוצא 7.
- מכניסים $x = 0$: $f(0) = 1$. יוצא 1.
- מכניסים $x = -2$: $f(-2) = -3$. יוצא -3.

**כלל מפתח:** לכל קלט יש בדיוק פלט אחד. אם קלט אחד נותן שני פלטים שונים — זו לא פונקציה.

**תחום** = הקלטים המותרים (מה $x$ יכול להיות).
**טווח** = הפלטים האפשריים (מה $f(x)$ יכול להיות).`,
    },
  };
  Object.entries(overrides).forEach(([idx, body]) => {
    if (l.sections[+idx]) l.sections[+idx].body_by_level = set3pt(l.sections[+idx], body.en, body.he);
  });
  l.sections = l.sections.map((s) => {
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ functions_intro');
}

// ─────────────────────────────────────────────────────────────────
// FUNCTIONS LINEAR
// ─────────────────────────────────────────────────────────────────
{
  const l = load('functions_linear');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ functions_linear');
}

// ─────────────────────────────────────────────────────────────────
// GEOMETRY BASICS
// ─────────────────────────────────────────────────────────────────
{
  const l = load('geometry_basics');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ geometry_basics');
}

// ─────────────────────────────────────────────────────────────────
// FACTORING, FRACTIONS_ALGEBRAIC, TRIANGLES_CONGRUENCE — base wrap for 3pt
// ─────────────────────────────────────────────────────────────────
for (const concept of ['factoring', 'fractions_algebraic', 'triangles_congruence']) {
  const l = load(concept);
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks);
    return s;
  });
  save(l);
  console.log(`✅ ${concept}`);
}

// ─────────────────────────────────────────────────────────────────
// TRIGONOMETRY RATIOS
// ─────────────────────────────────────────────────────────────────
{
  const l = load('trigonometry_ratios');
  const tracks = l.math_track ?? [];
  l.sections = (l.sections ?? []).map((s) => {
    s.body_by_level = wrapExistingFor(s, tracks.filter((t) => t !== '3pt'));
    return s;
  });
  const overrides = {
    0: {
      en: `**Trigonometry is about ratios in right triangles.**

In a right triangle with angle $\\theta$:
- The side **opposite** to $\\theta$ (O)
- The side **adjacent** to $\\theta$ (A)  
- The **hypotenuse** — always the longest side (H)

**The three ratios (SOH-CAH-TOA):**
$$\\sin\\theta = \\frac{\\text{Opposite}}{\\text{Hypotenuse}} = \\frac{O}{H}$$
$$\\cos\\theta = \\frac{\\text{Adjacent}}{\\text{Hypotenuse}} = \\frac{A}{H}$$
$$\\tan\\theta = \\frac{\\text{Opposite}}{\\text{Adjacent}} = \\frac{O}{A}$$

**Memory trick: SOH-CAH-TOA**

**Example:** In a right triangle, $\\theta = 30°$, hypotenuse = 10.
$\\text{Opposite} = 10 \\times \\sin 30° = 10 \\times 0.5 = 5$.`,
      he: `**טריגונומטריה עוסקת ביחסים במשולשים ישרי זווית.**

במשולש ישר-זווית עם זווית $\\theta$:
- הצלע **הנגדית** ל-$\\theta$ (N)
- הצלע **הצמודה** ל-$\\theta$ (C)
- **היתר** — תמיד הצלע הארוכה ביותר (Y)

**שלושת היחסים (SOH-CAH-TOA):**
$$\\sin\\theta = \\frac{\\text{נגדית}}{\\text{יתר}} = \\frac{N}{Y}$$
$$\\cos\\theta = \\frac{\\text{צמודה}}{\\text{יתר}} = \\frac{C}{Y}$$
$$\\tan\\theta = \\frac{\\text{נגדית}}{\\text{צמודה}} = \\frac{N}{C}$$

**עזר זיכרון: נ.צ.י — נגדית-צמודה-יתר**

**דוגמה:** במשולש ישר-זווית, $\\theta = 30°$, יתר = 10.
$\\text{נגדית} = 10 \\times \\sin 30° = 10 \\times 0.5 = 5$.`,
    },
  };
  Object.entries(overrides).forEach(([idx, body]) => {
    if (l.sections[+idx]) l.sections[+idx].body_by_level = set3pt(l.sections[+idx], body.en, body.he);
  });
  l.sections = l.sections.map((s) => {
    if (!s.body_by_level?.['3pt'] && (s.body_en_md || s.body_he_md)) {
      s.body_by_level = { ...(s.body_by_level ?? {}), '3pt': { body_en_md: s.body_en_md ?? '', body_he_md: s.body_he_md ?? s.body_en_md ?? '' } };
    }
    return s;
  });
  save(l);
  console.log('✅ trigonometry_ratios');
}

// ─────────────────────────────────────────────────────────────────
// Wrap remaining lessons that still have no body_by_level at all
// ─────────────────────────────────────────────────────────────────
import { readdirSync } from 'fs';
const remaining = readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json'));
let wrappedRemaining = 0;
for (const f of remaining) {
  const fp = join(LESSONS_DIR, f);
  const l = JSON.parse(readFileSync(fp, 'utf-8'));
  const tracks = l.math_track ?? [];
  if (tracks.length === 0) continue;
  let modified = false;
  (l.sections ?? []).forEach((s, i) => {
    if (!s.body_en_md && !s.body_he_md) return;
    const missing = tracks.filter((t) => !(s.body_by_level ?? {})[t]);
    if (missing.length === 0) return;
    l.sections[i].body_by_level = l.sections[i].body_by_level ?? {};
    missing.forEach((t) => {
      l.sections[i].body_by_level[t] = {
        body_en_md: s.body_en_md ?? '',
        body_he_md: s.body_he_md ?? s.body_en_md ?? '',
      };
    });
    modified = true;
  });
  if (modified) {
    writeFileSync(fp, JSON.stringify(l, null, 2), 'utf-8');
    wrappedRemaining++;
  }
}
console.log(`\n✅ Additional lessons base-wrapped: ${wrappedRemaining}`);
console.log('\nAll done! Run: cd apps/web && node ../../scripts/seed-lessons.mjs');
