#!/usr/bin/env node
/**
 * Deepen algebra-family track variants with distinct pedagogy (not clone-only).
 * Usage: node scripts/deepen-algebra-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const ALGEBRA_BASES = [
  'algebra_basics',
  'factoring',
  'equations_linear',
  'equations_quadratic',
  'inequalities',
  'fractions_algebraic',
  'fractions_and_ratios',
  'systems_linear_equations',
  'linear_equations_basics',
  'linear_equations_one_variable',
  'linear_functions',
  'word_problems',
  'algebra_review',
];

const DEPTH = {
  '3pt': {
    marker: 'ALGEBRA_DEPTH_3PT',
    title_en: '3pt algebra craft: numbers first, then structure',
    title_he: 'מלאכת אלגברה 3 יח׳: מספרים תחילה, אחר כך מבנה',
    body_en: `**3pt algebra habit.** Start every item with a **numeric check** before symbols.
1. Substitute an easy number to estimate the answer size.
2. Rewrite by combining like terms — circle the variable terms.
3. Solve one step at a time; after each step, re-check with the same number.
4. Word problems: define one unknown in a full sentence before writing an equation.

Avoid heavy parameters ($k$, $m$) on this track unless the stem gives their values.`,
    body_he: `**הרגל אלגברה 3 יח׳.** בכל פריט התחילו ב**בדיקה מספרית** לפני סמלים.
1. הציבו מספר קל כדי להעריך סדר גודל.
2. ארגנו איברים דומים — סמנו את איברי המשתנה.
3. פתרו צעד-צעד; אחרי כל צעד בדקו שוב באותו מספר.
4. בעיות מילוליות: הגדירו נעלם אחד במשפט מלא לפני כתיבת משוואה.

הימנעו מפרמטרים כבדים ($k$, $m$) אלא אם הניסוח נותן את ערכיהם.`,
  },
  '4pt': {
    marker: 'ALGEBRA_DEPTH_4PT',
    title_en: '4pt algebra craft: parameters and two representations',
    title_he: 'מלאכת אלגברה 4 יח׳: פרמטרים ושני ייצוגים',
    body_en: `**4pt algebra habit.** Every non-trivial item should touch **two representations**.
1. Translate “for which $k$…” into an inequality on the discriminant or domain.
2. Sketch a quick number line or graph when the algebra is about signs/roots.
3. After solving, state the **condition set** in interval or set notation.
4. Error analysis: given a wrong middle step, locate the first false equality.

Parameters are expected — name the case split ($\Delta>0$, $=0$, $<0$) explicitly.`,
    body_he: `**הרגל אלגברה 4 יח׳.** בכל פריט לא-טריוויאלי געו ב**שני ייצוגים**.
1. תרגמו \"עבור אילו $k$…\" לאי-שוויון על דיסקרימיננטה או תחום.
2. סקצו ישר מספרים או גרף כשמדובר בסימנים/שורשים.
3. אחרי הפתרון, כתבו את **קבוצת התנאים** בסימון קטעים או קבוצות.
4. ניתוח טעויות: בהינתן צעד אמצעי שגוי, מצאו את השוויון הכוזב הראשון.

פרמטרים צפויים — ציינו במפורש את פיצול המקרים ($\\Delta>0$, $=0$, $<0$).`,
  },
  '5pt': {
    marker: 'ALGEBRA_DEPTH_5PT',
    title_en: '5pt algebra craft: justification chains and edge cases',
    title_he: 'מלאכת אלגברה 5 יח׳: שרשראות הצדקה ומקרי קצה',
    body_en: `**5pt algebra habit.** Write a short **justification chain** (3–5 sentences):
hypothesis → allowed move → conclusion. Always include one **edge case**:
no solution, infinite solutions, or a boundary value that flips a sign chart.
Link forward: how this algebra block feeds function investigation or sequences.
Stay MoE-faithful — no university formal-limit drills or analysis jargon.`,
    body_he: `**הרגל אלגברה 5 יח׳.** כתבו **שרשרת הצדקה** קצרה (3–5 משפטים):
הנחה → מהלך מותר → מסקנה. תמיד כללו **מקרה קצה** אחד:
אין פתרון, אינסוף פתרונות, או ערך שפה שהופך טבלת סימנים.
קשרו קדימה: איך בלוק אלגברה זה מזין חקירת פונקציות או סדרות.
הישארו נאמנים לתוכנית — בלי תרגול הגדרת גבול אוניברסיטאית או זargon אנליזה.`,
  },
  university: {
    marker: 'ALGEBRA_DEPTH_UNI',
    title_en: 'University bridge: structure, quantifiers, course-exam pace',
    title_he: 'גשר אוניברסיטאי: מבנה, כמתים, קצב מבחן קורס',
    body_en: `**University algebra bridge.** Prefer precise statements (“for all / there exists”)
when classifying solution sets. Treat identities vs equations carefully.
Course-exam pace: show structure first (what object are we manipulating?), then computation.
No high-school questionnaire framing — write as a Calc-1 / LA readiness drill.`,
    body_he: `**גשר אלגברה לאוניברסיטה.** העדיפו ניסוחים מדויקים (\"לכל / קיים\")
כשמסווגים קבוצות פתרון. הבחינו בין זהויות למשוואות.
קצב מבחן קורס: הציגו מבנה תחילה (מה האובייקט?), אחר כך חישוב.
בלי מסגור שאלוני תיכון — כתבו כתרגיל מוכנות לחדו״א 1 / אלגברה לינארית.`,
  },
};

function trackOf(lesson, fileBase) {
  const tracks = lesson.math_track || [];
  if (tracks.includes('university') || /__uni$/.test(fileBase)) return 'university';
  if (tracks.includes('5pt') || /__5pt$/.test(fileBase)) return '5pt';
  if (tracks.includes('4pt') || /__4pt$/.test(fileBase)) return '4pt';
  if (tracks.includes('3pt') || !/__/.test(fileBase)) return '3pt';
  return '3pt';
}

function deepenFile(fileBase) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const track = trackOf(lesson, fileBase);
  const depth = DEPTH[track];
  if (!depth) return false;

  lesson.sections = lesson.sections || [];
  const already = lesson.sections.some((s) => (s.body_en_md || '').includes(depth.marker));
  if (!already) {
    const insert = {
      kind: 'theory',
      title_en: depth.title_en,
      title_he: depth.title_he,
      body_en_md: `<!-- ${depth.marker} -->\n${depth.body_en}`,
      body_he_md: depth.body_he,
    };
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
    else lesson.sections.push(insert);
  }

  // Track-specific practice question (unique stem per track)
  const qid = `${fileBase}-algebra-depth`;
  lesson.questions = lesson.questions || [];
  if (!lesson.questions.some((q) => q.id === qid)) {
    const stems = {
      '3pt': {
        stem_en: `Numeric-first check for this lesson: pick easy numbers, estimate, then solve the core skill from **${fileBase.replace(/__.*/, '')}** and verify by substitution.`,
        stem_he: `בדיקה מספרית-תחילה: בחרו מספרים קלים, העריכו, פתרו את המיומנות המרכזית של השיעור, ואמתו בהצבה.`,
      },
      '4pt': {
        stem_en: `Parameter drill: introduce a parameter $k$ into a standard item from this lesson, state the condition on $k$, and solve with a sign chart or discriminant as needed.`,
        stem_he: `תרגיל פרמטר: הכניסו פרמטר $k$ לפריט סטנדרטי מהשיעור, ציינו תנאי על $k$, ופתרו עם טבלת סימנים או דיסקרימיננטה.`,
      },
      '5pt': {
        stem_en: `Justification chain: prove or fully justify a multi-step claim from this lesson, and exhibit one edge case (empty / infinite / boundary).`,
        stem_he: `שרשרת הצדקה: הוכיחו או הצדיקו במלואה טענה רב-שלבית מהשיעור, והציגו מקרה קצה אחד (ריק / אינסופי / שפה).`,
      },
      university: {
        stem_en: `Course-exam style: state the algebraic object precisely (set / identity / equation), solve, and classify the solution set with quantifiers where useful.`,
        stem_he: `סגנון מבחן קורס: נסחו את האובייקט האלגברי במדויק (קבוצה / זהות / משוואה), פתרו, וסווגו את קבוצת הפתרון עם כמתים כשמועיל.`,
      },
    };
    const s = stems[track];
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: track === '3pt' ? 'medium' : 'hard',
      facets: track === '3pt' ? ['word_problem_setup'] : ['parametric_root_conditions', 'error_analysis'],
      stem_en: s.stem_en,
      stem_he: s.stem_he,
      explanation_en:
        '**Worked path.** Identify the lesson skill, write the governing relation, execute algebra with labeled steps, then verify (substitution, discriminant sign, or set membership). Keep method marks visible. See the track-depth theory section in this lesson for the expected habits.',
      explanation_he:
        '**דרך פתרון.** זהו את מיומנות השיעור, כתבו את הקשר השולט, בצעו אלגברה עם שלבים מסומנים, ואמתו (הצבה, סימן דיסקרימיננטה, או שייכות לקבוצה). השאירו ניקוד שיטה גלוי. ראו את סעיף העומק לפי מסלול בשיעור.',
      correct_answer: 'see track-depth section',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  // Nudge summary to mention track register
  if (lesson.summary_en && !lesson.summary_en.includes('track register')) {
    lesson.summary_en = `${lesson.summary_en} Taught at the ${track} track register with algebra-family depth habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const base of ALGEBRA_BASES) {
  const files = fs
    .readdirSync(DIR)
    .filter((f) => f === `${base}.json` || f.startsWith(`${base}__`))
    .map((f) => f.replace(/\.json$/, ''));
  for (const id of files) {
    if (deepenFile(id)) {
      console.log('deepened', id);
      n++;
    }
  }
}
console.log('deepened files', n);
