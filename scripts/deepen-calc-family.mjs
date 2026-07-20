#!/usr/bin/env node
/**
 * Deepen calc family (derivatives_* / integrals_*) with track pedagogy + facets.
 * Derivatives facets: rule_selection, graphical_derivative
 * Integrals facets: area_interpretation, antiderivative_check
 *
 * Avoid MoE denylist: ε–δ, limit-definition-of-derivative phrasing, L'Hôpital on 5pt,
 * Bagrut framing on university lessons.
 *
 * Usage: node scripts/deepen-calc-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const DERIV_BASES = [
  'derivatives_intro',
  'derivatives_rules',
  'derivatives_trig_exp',
  'derivatives_implicit',
  'derivatives_applications',
];

const INTEGRAL_BASES = [
  'integrals_intro',
  'integrals_4pt',
  'integrals_techniques',
  'integrals_trig_exp',
  'integrals_applications',
];

const DERIV_DEPTH = {
  '3pt': {
    marker: 'CALC_DERIV_DEPTH_3PT',
    title_en: '3pt derivative craft: slope meaning, then a rule',
    title_he: 'מלאכת נגזרות 3 יח׳: משמעות שיפוע, אחר כך כלל',
    body_en: `**3pt derivative habit.** Start from **graphical meaning**: $f'(a)$ is the slope of the tangent at $x=a$.
1. Sketch $f$ lightly; mark the tangent at one point.
2. Estimate the slope from the sketch (rise/run).
3. Only then pick a differentiation rule for the formula.
4. Keep rule selection simple — power rule and one product or chain step at most.`,
    body_he: `**הרגל נגזרות 3 יח׳.** התחילו מ**משמעות גרפית**: $f'(a)$ הוא שיפוע המשיק ב-$x=a$.
1. סקצו את $f$; סמנו משיק בנקודה אחת.
2. העריכו שיפוע מהסקיצה (עלייה/ריצה).
3. רק אז בחרו כלל גזירה לנוסחה.
4. בחירת כלל פשוטה — כלל חזקה וצעד מכפלה או שרשרת אחד לכל היותר.`,
  },
  '4pt': {
    marker: 'CALC_DERIV_DEPTH_4PT',
    title_en: '4pt derivative craft: rule selection + sketch $f′$',
    title_he: 'מלאכת נגזרות 4 יח׳: בחירת כלל + סקיצת $f′$',
    body_en: `**4pt derivative habit.** Two mandatory moves:
1. **Rule selection:** name whether you need product, quotient, or chain rule before differentiating (באיזו נגזרת / כלל השרשרת).
2. **Graphical derivative:** from the graph of $f$, sketch $f′$ — zeros of $f′$ at extrema of $f$, sign of $f′$ from monotonicity.`,
    body_he: `**הרגל נגזרות 4 יח׳.** שני מהלכים חובה:
1. **בחירת כלל:** ציינו אם צריך מכפלה, מנה או שרשרת לפני הגזירה (באיזו נגזרת / כלל השרשרת).
2. **נגזרת מהגרף:** מהגרף של $f$, סקצו את $f′$ — אפסי $f′$ בקיצוני $f$, סימן $f′$ ממונוטוניות.`,
  },
  '5pt': {
    marker: 'CALC_DERIV_DEPTH_5PT',
    title_en: '5pt derivative craft: investigation with $f$ and $f′$',
    title_he: 'מלאכת נגזרות 5 יח׳: חקירה עם $f$ ו-$f′$',
    body_en: `**5pt derivative habit.** Run a short investigation: domain → $f′$ via named rules → critical points → sign chart of $f′$ → sketch.
Always include one **from the graph** prompt: recover features of $f′$ without a closed form.
Stay MoE-faithful — use geometric slope meaning and rules, not formal university limit-definition drills.`,
    body_he: `**הרגל נגזרות 5 יח׳.** הריצו חקירה קצרה: תחום → $f′$ בכללים מפורשים → נקודות קריטיות → טבלת סימנים של $f′$ → סקיצה.
תמיד כללו פרומפט **מהגרף** אחד: שחזרו תכונות של $f′$ בלי נוסחה סגורה.
הישארו נאמנים לתוכנית — משמעות שיפוע וכללים, בלי תרגול הגדרה פורמלית אוניברסיטאית.`,
  },
  university: {
    marker: 'CALC_DERIV_DEPTH_UNI',
    title_en: 'University bridge: derivative as linear approximation',
    title_he: 'גשר אוניברסיטאי: נגזרת כקירוב לינארי',
    body_en: `**University derivative bridge.** Prefer the language of linear approximation: $f(a+h)\\approx f(a)+f'(a)h$.
Rule selection is algebraic bookkeeping; graphical derivative checks consistency of sign charts.
Course-exam pace: state differentiability assumptions, compute, then interpret slope/rate.`,
    body_he: `**גשר נגזרות לאוניברסיטה.** העדיפו שפת קירוב לינארי: $f(a+h)\\approx f(a)+f'(a)h$.
בחירת כלל היא סדר אלגברי; נגזרת מהגרף בודקת עקביות טבלאות סימנים.
קצב מבחן קורס: הנחות גזירות → חישוב → פירוש שיפוע/קצב.`,
  },
};

const INTEGRAL_DEPTH = {
  '3pt': {
    marker: 'CALC_INT_DEPTH_3PT',
    title_en: '3pt integral craft: area under the curve first',
    title_he: 'מלאכת אינטגרלים 3 יח׳: שטח מתחת לגרף תחילה',
    body_en: `**3pt integral habit.** Read a definite integral as **area under** the graph before antiderivatives.
1. Sketch the region; shade the area under $y=f(x)$ from $a$ to $b$.
2. Estimate sign (above/below axis).
3. Then find an antiderivative and evaluate; differentiate to check (+C for indefinite).`,
    body_he: `**הרגל אינטגרלים 3 יח׳.** קראו אינטגרל מסוים כ**שטח מתחת** לגרף לפני קדומות.
1. סקצו את האזור; צבעו את השטח מתחת ל-$y=f(x)$ מ-$a$ עד $b$.
2. העריכו סימן (מעל/מתחת לציר).
3. אחר כך מצאו קדומה והציבו; בדקו בנגזרת (+C לאי-מסוים).`,
  },
  '4pt': {
    marker: 'CALC_INT_DEPTH_4PT',
    title_en: '4pt integral craft: area interpretation + antiderivative check',
    title_he: 'מלאכת אינטגרלים 4 יח׳: פירוש שטח + בדיקה בנגזרת',
    body_en: `**4pt integral habit.** Two mandatory moves:
1. **Area interpretation** of the definite integral (net area if signed).
2. **Antiderivative check:** after finding $F$, differentiate to check $F'=f$, and write $+C$ on indefinite integrals.`,
    body_he: `**הרגל אינטגרלים 4 יח׳.** שני מהלכים חובה:
1. **פירוש שטח** של האינטגרל המסוים (שטח נטו אם מסומן).
2. **בדיקה בנגזרת:** אחרי מציאת $F$, גזרו לאימות $F'=f$, וכתבו $+C$ באי-מסוים.`,
  },
  '5pt': {
    marker: 'CALC_INT_DEPTH_5PT',
    title_en: '5pt integral craft: technique choice + geometric check',
    title_he: 'מלאכת אינטגרלים 5 יח׳: בחירת טכניקה + בדיקה גאומטרית',
    body_en: `**5pt integral habit.** Name the technique (substitution / parts / trig form) before computing.
Always close with area interpretation of any definite integral and an antiderivative check ($F'=f$, $+C$).
Stay MoE-faithful — geometric and algebraic fluency, not analysis formalism.`,
    body_he: `**הרגל אינטגרלים 5 יח׳.** ציינו את הטכניקה (הצבה / חלקים / צורה טריגונומטרית) לפני החישוב.
תמיד סיימו בפירוש שטח לאינטגרל מסוים ובבדיקת קדומה ($F'=f$, $+C$).
הישארו נאמנים לתוכנית — שטף גאומטרי ואלגברי, לא פורמליזם של אנליזה.`,
  },
  university: {
    marker: 'CALC_INT_DEPTH_UNI',
    title_en: 'University bridge: integral as accumulation',
    title_he: 'גשר אוניברסיטאי: אינטגרל כצבירה',
    body_en: `**University integral bridge.** Prefer accumulation language: net change of an antiderivative.
Area under a curve is the geometric special case of a definite integral.
Course-exam pace: choose technique → compute → differentiate to check → interpret.`,
    body_he: `**גשר אינטגרלים לאוניברסיטה.** העדיפו שפת צבירה: שינוי נטו של קדומה.
שטח מתחת לגרף הוא המקרה הגאומטרי של אינטגרל מסוים.
קצב מבחן קורס: בחירת טכניקה → חישוב → בדיקה בנגזרת → פירוש.`,
  },
};

const DERIV_FACET = {
  kind: 'theory',
  title_en: 'Facet depth: rule selection and graphical derivative',
  title_he: 'העמקת פנים: בחירת כלל ונגזרת מהגרף',
  body_en_md: `**Rule selection.** Before differentiating, decide: power, product rule, quotient, or chain rule (כלל השרשרת). Say aloud “באיזו נגזרת” — which rule fits the outermost structure.

**Graphical derivative.** From the graph of $y=f(x)$, sketch $f′$: zeros of $f′$ where $f$ has horizontal tangents; $f′>0$ on increasing intervals; steepness of $f$ controls $|f′|$.`,
  body_he_md: `**בחירת כלל.** לפני גזירה, החליטו: חזקה, מכפלה, מנה או כלל השרשרת. אמרו בקול \"באיזו נגזרת\" — איזה כלל מתאים למבנה החיצוני.

**נגזרת מהגרף.** מהגרף של $y=f(x)$, סקצו את $f′$: אפסים של $f′$ במשיקים אופקיים של $f$; $f′>0$ בקטעי עלייה; תלילות $f$ שולטת ב-$|f′|$.`,
};

const INTEGRAL_FACET = {
  kind: 'theory',
  title_en: 'Facet depth: area interpretation and antiderivative check',
  title_he: 'העמקת פנים: פירוש שטח ובדיקת קדומה',
  body_en_md: `**Area interpretation.** A definite integral $\\int_a^b f(x)\\,dx$ is net area under the curve $y=f(x)$ from $a$ to $b$ (positive above the axis, negative below).

**Antiderivative check.** If $F'=f$, then $\\int f=F+C$. Always differentiate to check your antiderivative, and keep $+C$ on indefinite integrals.`,
  body_he_md: `**פירוש שטח.** אינטגרל מסוים $\\int_a^b f(x)\\,dx$ הוא שטח נטו מתחת לגרף $y=f(x)$ מ-$a$ עד $b$ (חיובי מעל הציר, שלילי מתחת).

**בדיקה בנגזרת.** אם $F'=f$, אז $\\int f=F+C$. תמיד גזרו לאימות הקדומה, והשאירו $+C$ באי-מסוים.`,
};

const DERIV_QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['rule_selection'],
    stem_en:
      'For a product or composition from this lesson, state which differentiation rule you will use (product / quotient / chain rule) and why, then differentiate.',
    stem_he:
      'עבור מכפלה או הרכבה מהשיעור, ציינו באיזו נגזרת תשתמשו (מכפלה / מנה / כלל השרשרת) ומדוע, ואז גזרו.',
    correct_answer: 'name outermost rule then differentiate',
    explanation_en:
      'Rule selection starts from the outermost algebraic structure: a product needs the product rule, a quotient the quotient rule, and a composition the chain rule (כלל השרשרת). Name the rule in one sentence before any symbol pushing. After differentiating, simplify and spot-check the derivative at an easy point if the original function is easy to evaluate.',
    explanation_he:
      'בחירת כלל מתחילה מהמבנה החיצוני: מכפלה דורשת כלל מכפלה, מנה — כלל מנה, והרכבה — כלל השרשרת. ציינו את הכלל במשפט אחד לפני דחיפת סמלים. אחרי הגזירה, פשטו ובדקו את הנגזרת בנקודה קלה אם הפונקציה המקורית נוחה להערכה.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['graphical_derivative'],
    stem_en:
      'From the graph of $y=f(x)$ (without a closed formula), sketch $f′$: mark zeros, sign intervals, and one point where $|f′|$ is large.',
    stem_he:
      'מהגרף של $y=f(x)$ (בלי נוסחה סגורה), סקצו את $f′$: סמנו אפסים, קטעי סימן, ונקודה שבה $|f′|$ גדול.',
    correct_answer: 'zeros at extrema; sign from mono; steep => large |f′|',
    explanation_en:
      'A graphical derivative is read from the graph of $f$: horizontal tangents give $f′=0$; increasing stretches give $f′>0$; decreasing give $f′<0$. Where $f$ is steep, $|f′|$ is large. Sketch $f′$ with those landmarks before trying any formula. This check catches sign-chart errors even when the closed form is messy.',
    explanation_he:
      'נגזרת מהגרף נקראת מגרף $f$: משיקים אופקיים נותנים $f′=0$; קטעי עלייה — $f′>0$; ירידה — $f′<0$. היכן ש-$f$ תלול, $|f′|$ גדול. סקצו את $f′$ עם ציון דרך אלה לפני נוסחה. הבדיקה תופסת טעויות טבלת סימנים גם כשהנוסחה מסורבלת.',
  },
];

const INTEGRAL_QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['area_interpretation'],
    stem_en:
      'Interpret a definite integral from this lesson as area under the curve: sketch the region, state whether the net area is positive or negative, then evaluate.',
    stem_he:
      'פרשו אינטגרל מסוים מהשיעור כשטח מתחת לגרף: סקצו את האזור, ציינו אם השטח הנטו חיובי או שלילי, ואז חשבו.',
    correct_answer: 'shade region; signed net area; then FTC evaluate',
    explanation_en:
      'Area interpretation comes first: shade the region under $y=f(x)$ between the limits. Portions above the axis contribute positively to the definite integral; portions below contribute negatively. After the geometric reading, evaluate with an antiderivative. If the sketch and the numeric sign disagree, recheck limits and orientation.',
    explanation_he:
      'פירוש שטח קודם: צבעו את האזור מתחת ל-$y=f(x)$ בין הגבולות. חלקים מעל הציר תורמים חיובית לאינטגרל המסוים; מתחת — שלילית. אחרי הקריאה הגאומטרית, חשבו עם קדומה. אם הסקיצה והסימן המספרי לא מסכימים, בדקו גבולות וכיוון.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['antiderivative_check'],
    stem_en:
      'Find an antiderivative for an integrand from this lesson, write $+C$ if indefinite, then differentiate to check that you recover the integrand.',
    stem_he:
      'מצאו קדומה לאינטגרנד מהשיעור, כתבו $+C$ אם אי-מסוים, ואז גזרו לאימות שמתקבל האינטגרנד.',
    correct_answer: 'F with +C; verify F′=f',
    explanation_en:
      'An antiderivative check is mandatory: if you propose $F$, differentiate to check $F′=f$. For indefinite integrals keep $+C$. Common misses are forgetting the chain-rule factor after a substitution or dropping the constant. The check is usually faster than redoing the whole technique from scratch.',
    explanation_he:
      'בדיקה בנגזרת היא חובה: אם הצעתם $F$, גזרו לאימות $F′=f$. באי-מסוים השאירו $+C$. טעויות נפוצות: שכחת גורם שרשרת אחרי הצבה או השמטת הקבוע. הבדיקה לרוב מהירה יותר מחישוב מחדש של כל הטכניקה.',
  },
];

function trackOf(lesson, fileBase) {
  const tracks = lesson.math_track || [];
  if (tracks.includes('university') || /__uni$/.test(fileBase)) return 'university';
  if (tracks.includes('5pt') || /__5pt$/.test(fileBase) || /_5pt$/.test(fileBase)) return '5pt';
  if (tracks.includes('4pt') || /__4pt$/.test(fileBase) || /_4pt$/.test(fileBase)) return '4pt';
  if (tracks.includes('3pt') || !/__/.test(fileBase)) return '3pt';
  return '3pt';
}

function deepenFile(fileBase, family) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const track = trackOf(lesson, fileBase);
  const DEPTH = family === 'deriv' ? DERIV_DEPTH : INTEGRAL_DEPTH;
  const depth = DEPTH[track];
  if (!depth) return false;

  lesson.sections = lesson.sections || [];
  const alreadyDepth = lesson.sections.some((s) => (s.body_en_md || '').includes(depth.marker));
  if (!alreadyDepth) {
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

  const facet = family === 'deriv' ? DERIV_FACET : INTEGRAL_FACET;
  const facetRe =
    family === 'deriv'
      ? /Facet depth:.*rule selection/i
      : /Facet depth:.*area interpretation/i;
  if (!lesson.sections.some((s) => s.title_en && facetRe.test(s.title_en))) {
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, facet);
    else lesson.sections.push(facet);
  }

  const questions = family === 'deriv' ? DERIV_QUESTIONS : INTEGRAL_QUESTIONS;
  lesson.questions = lesson.questions || [];
  const existingFacets = new Set();
  for (const q of lesson.questions) {
    for (const f of q.facets || []) existingFacets.add(f);
  }
  for (const q of questions) {
    if ((q.facets || []).some((f) => existingFacets.has(f))) continue;
    const ord = lesson.questions.length + 1;
    lesson.questions.push({
      ...q,
      id: `${fileBase}-facet-calc-${ord}`,
      ord,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existingFacets.add(f);
  }

  const qid = `${fileBase}-calc-${family}-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    const stem =
      family === 'deriv'
        ? {
            stem_en:
              'Track drill: name the differentiation rule for one item from this lesson, compute $f′$, then sketch or describe $f′$ from the graph of $f$ at one landmark.',
            stem_he:
              'תרגיל מסלול: ציינו את כלל הגזירה לפריט מהשיעור, חשבו $f′$, ואז סקצו או תארו את $f′$ מהגרף של $f$ בנקודת ציון אחת.',
          }
        : {
            stem_en:
              'Track drill: interpret one definite integral as area under the curve, evaluate it, then differentiate your antiderivative to check (include $+C$ if indefinite).',
            stem_he:
              'תרגיל מסלול: פרשו אינטגרל מסוים אחד כשטח מתחת לגרף, חשבו, ואז גזרו את הקדומה לאימות (כללו $+C$ אם אי-מסוים).',
          };
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: track === '3pt' ? 'medium' : 'hard',
      facets:
        family === 'deriv'
          ? ['rule_selection', 'graphical_derivative']
          : ['area_interpretation', 'antiderivative_check'],
      stem_en: stem.stem_en,
      stem_he: stem.stem_he,
      explanation_en:
        family === 'deriv'
          ? '**Worked path for derivative track depth.** Name the outermost rule (product, quotient, or chain) before differentiating. Compute carefully, then cross-check with a graphical derivative reading: zeros of $f′$ at extrema of $f$, and sign of $f′$ from monotonicity. Prefer geometric slope language on MoE tracks.'
          : '**Worked path for integral track depth.** Shade the area under the curve for any definite integral and state the signed net area. Compute with a chosen technique, write $+C$ when indefinite, and always differentiate to check that the antiderivative recovers the integrand.',
      explanation_he:
        family === 'deriv'
          ? '**דרך פתרון לעומק מסלול הנגזרות.** ציינו את הכלל החיצוני (מכפלה, מנה או שרשרת) לפני הגזירה. חשבו בזהירות, ואז אמתו בקריאת נגזרת מהגרף: אפסי $f′$ בקיצוני $f$, וסימן $f′$ ממונוטוניות. העדיפו שפת שיפוע גאומטרית במסלולי התוכנית.'
          : '**דרך פתרון לעומק מסלול האינטגרלים.** צבעו שטח מתחת לגרף לכל אינטגרל מסוים וציינו שטח נטו מסומן. חשבו בטכניקה שנבחרה, כתבו $+C$ באי-מסוים, ותמיד גזרו לאימות שהקדומה מחזירה את האינטגרנד.',
      correct_answer: 'see calc track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  const tag = family === 'deriv' ? 'derivatives-family depth' : 'integrals-family depth';
  if (lesson.summary_en && !lesson.summary_en.includes(tag)) {
    lesson.summary_en = `${lesson.summary_en} Taught at the ${track} track register with ${tag} habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const [bases, family] of [
  [DERIV_BASES, 'deriv'],
  [INTEGRAL_BASES, 'integral'],
]) {
  for (const base of bases) {
    const files = fs
      .readdirSync(DIR)
      .filter((f) => f === `${base}.json` || f.startsWith(`${base}__`))
      .map((f) => f.replace(/\.json$/, ''));
    // Also allow exact base when base already includes _4pt suffix
    if (files.length === 0 && fs.existsSync(path.join(DIR, `${base}.json`))) {
      files.push(base);
    }
    for (const id of [...new Set(files)]) {
      if (deepenFile(id, family)) {
        console.log('deepened', id);
        n++;
      }
    }
  }
}
console.log('deepened files', n);
