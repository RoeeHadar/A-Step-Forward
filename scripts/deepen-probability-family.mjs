#!/usr/bin/env node
/**
 * Deepen probability_* family with track pedagogy + three_way_tables facet.
 * Usage: node scripts/deepen-probability-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const BASES = ['probability_basic', 'probability_basics_3pt', 'probability_conditional_3pt'];

const DEPTH = {
  '3pt': {
    marker: 'PROB_DEPTH_3PT',
    title_en: '3pt probability craft: list outcomes, then count',
    title_he: 'מלאכת הסתברות 3 יח׳: רשימת תוצאות, אחר כך ספירה',
    body_en: `**3pt probability habit.** Write the sample space (or a clear table) before any fraction.
1. List equally likely outcomes when possible.
2. Count favorable vs total.
3. For two attributes, build a two-way table before conditioning.
4. Three-way tables: only when the stem has three attributes — label every margin.`,
    body_he: `**הרגל הסתברות 3 יח׳.** כתבו מרחב מדגם (או טבלה ברורה) לפני כל שבר.
1. רשמו תוצאות שוות-סבירות כשאפשר.
2. ספרו רצויות מול סה״כ.
3. לשני מאפיינים — בנו טבלה דו-כיוונית לפני התניה.
4. טבלאות תלת-כיווניות: רק כשיש שלושה מאפיינים — סמנו כל שולית.`,
  },
  '4pt': {
    marker: 'PROB_DEPTH_4PT',
    title_en: '4pt probability craft: contingency tables and conditionals',
    title_he: 'מלאכת הסתברות 4 יח׳: טבלאות שכיחות ומותנות',
    body_en: `**4pt probability habit.** Prefer a contingency table (two-way or three-way) before formulas.
Conditionals are ratios of a cell (or subtotal) to the correct margin — never swap $P(A\\mid B)$ with $P(B\\mid A)$.`,
    body_he: `**הרגל הסתברות 4 יח׳.** העדיפו טבלת שכיחות (דו- או תלת-כיוונית) לפני נוסחאות.
מותנות הן יחס של תא (או סכום-משנה) לשולית הנכונה — אל תחליפו $P(A\\mid B)$ ב-$P(B\\mid A)$.`,
  },
  '5pt': {
    marker: 'PROB_DEPTH_5PT',
    title_en: '5pt probability craft: three-way tables and Bayes setup',
    title_he: 'מלאכת הסתברות 5 יח׳: טבלאות תלת-כיווניות והכנת בייס',
    body_en: `**5pt probability habit.** When three attributes appear, build a **three-way** (or layered two-way) contingency table first.
Label every margin, then compute joints and conditionals. Bayes is just careful re-normalization of the same table.`,
    body_he: `**הרגל הסתברות 5 יח׳.** כשמופיעים שלושה מאפיינים, בנו תחילה טבלה **תלת-כיוונית** (או שכבות דו-כיווניות).
סמנו כל שולית, ואז חשבו משותפות ומותנות. בייס הוא נרמול זהיר של אותה טבלה.`,
  },
  stats: {
    marker: 'PROB_DEPTH_STATS',
    title_en: 'Stats-track probability craft: tables before symbols',
    title_he: 'מלאכת הסתברות למסלול סטטיסטיקה: טבלאות לפני סמלים',
    body_en: `**Stats-track habit.** Treat probability as reading a contingency table.
Build two-way or three-way tables, name margins, then write probabilities as ratios. Prefer data language over abstract set algebra when the stem is empirical.`,
    body_he: `**הרגל מסלול סטטיסטיקה.** התייחסו להסתברות כקריאת טבלת שכיחות.
בנו טבלאות דו- או תלת-כיווניות, ציינו שוליות, ואז כתבו הסתברויות כיחסים. העדיפו שפת נתונים על אלגברת קבוצות כשהניסוח אמפירי.`,
  },
  university: {
    marker: 'PROB_DEPTH_UNI',
    title_en: 'University bridge: probability spaces and tables',
    title_he: 'גשר אוניברסיטאי: מרחבי הסתברות וטבלאות',
    body_en: `**University probability bridge.** Tables are finite probability spaces in disguise.
State the sample space, the measure on atoms, then conditionals as restricted measures. Course-exam pace: model → table → compute.`,
    body_he: `**גשר הסתברות לאוניברסיטה.** טבלאות הן מרחבי הסתברות סופיים בתחפושת.
נסחו מרחב מדגם, מידה על אטומים, ואז מותנות כמידות מצומצמות. קצב מבחן קורס: מודל → טבלה → חישוב.`,
  },
};

const FACET = {
  kind: 'theory',
  title_en: 'Facet depth: three-way contingency tables',
  title_he: 'העמקת פנים: טבלאות שכיחות תלת-כיווניות',
  body_en_md: `**Three-way tables.** A contingency table can carry three attributes at once — for example Gender × Passed × Track. Layout options: a flat table with three column groups, or layered two-way tables (one layer per third attribute).

**Reading rules:** any cell is a joint count; marginals come from summing; conditionals are ratios to the appropriate margin. Label every margin before computing — three-way tables are where most “forgot which total” errors appear.`,
  body_he_md: `**טבלאות תלת-כיווניות.** טבלת שכיחות יכולה לשאת שלושה מאפיינים יחד — למשל מגדר × עבר × מסלול. אפשרויות: טבלה שטוחה עם שלוש קבוצות עמודות, או שכבות דו-כיווניות.

**כללי קריאה:** כל תא הוא ספירה משותפת; שוליות מסכימה; מותנות הן יחס לשולית המתאימה. סמנו כל שולית לפני החישוב — כאן מופיעות רוב טעויות \"שכחתי באיזה סה״כ\".`,
};

const QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['three_way_tables', 'three_way_table', 'contingency_3way'],
    stem_en:
      'A three-way contingency table classifies learners by Track, Gender, and Passed. Explain how to compute $P(\\text{Passed}=\\text{Yes}\\mid \\text{Track}=4pt)$ by naming which cells you sum.',
    stem_he:
      'טבלה תלת-כיוונית מסווגת לומדים לפי מסלול, מגדר ועבר. הסבירו איך מחשבים $P(\\mathrm{Passed}=\\mathrm{Yes}\\mid \\mathrm{Track}=4)$ תוך ציון התאים שמסכמים.',
    correct_answer:
      'Sum Passed=Yes in the 4pt slice; divide by all 4pt cells (both genders, Yes+No)',
    explanation_en:
      'Restrict to the 4pt layer of the three-way (or layered two-way) contingency table. Numerator = count with Passed=Yes in that slice (sum over gender). Denominator = all learners in the 4pt slice. That ratio is the conditional probability; do not use the grand total as the denominator.',
    explanation_he:
      'מצמצמים לשכבת 4 יח׳ בטבלה התלת-כיוונית. מונה = ספירת עבר=כן בשכבה (סכימה על מגדר). מכנה = כל הלומדים בשכבת 4 יח׳. זה היחס המותנה; אל תשתמשו בסה״כ הכללי במכנה.',
  },
];

function trackOf(lesson, fileBase) {
  const tracks = lesson.math_track || [];
  if (tracks.includes('university') || /__uni$/.test(fileBase)) return 'university';
  if (tracks.includes('stats') || lesson.subject === 'statistics') return 'stats';
  if (tracks.includes('5pt') || /__5pt$/.test(fileBase) || /_5pt$/.test(fileBase)) return '5pt';
  if (tracks.includes('4pt') || /__4pt$/.test(fileBase) || /_4pt$/.test(fileBase)) return '4pt';
  if (tracks.includes('3pt') || /_3pt$/.test(fileBase) || /__3pt$/.test(fileBase)) return '3pt';
  return '3pt';
}

function deepenFile(fileBase) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const track = trackOf(lesson, fileBase);
  const depth = DEPTH[track] || DEPTH['3pt'];

  lesson.sections = lesson.sections || [];
  if (!lesson.sections.some((s) => (s.body_en_md || '').includes(depth.marker))) {
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

  if (!lesson.sections.some((s) => s.title_en && /Facet depth:.*three-way/i.test(s.title_en))) {
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, FACET);
    else lesson.sections.push(FACET);
  }

  lesson.questions = lesson.questions || [];
  const existing = new Set();
  for (const q of lesson.questions) for (const f of q.facets || []) existing.add(f);
  for (const q of QUESTIONS) {
    if ((q.facets || []).some((f) => existing.has(f))) continue;
    lesson.questions.push({
      ...q,
      id: `${fileBase}-facet-prob-${lesson.questions.length + 1}`,
      ord: lesson.questions.length + 1,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  const qid = `${fileBase}-prob-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: 'medium',
      facets: ['three_way_tables'],
      stem_en:
        'Track drill: build a small three-way contingency table for a scenario from this lesson, label margins, and compute one conditional probability from the correct margin.',
      stem_he:
        'תרגיל מסלול: בנו טבלה תלת-כיוונית קטנה לתרחיש מהשיעור, סמנו שוליות, וחשבו הסתברות מותנית אחת מהשולית הנכונה.',
      explanation_en:
        '**Worked path.** Name the three attributes, fill joint counts, compute each margin, then form the conditional as a ratio to the restricted margin — never the grand total unless the event is unrestricted. Check that your three-way table rows sum consistently before dividing.',
      explanation_he:
        '**דרך פתרון.** ציינו שלושה מאפיינים, מלאו ספירות משותפות, חשבו כל שולית, ואז בנו מותנה כיחס לשולית המצומצמת — לא לסה״כ הכללי אלא אם אין צמצום. בדקו עקביות סכומי שורות לפני החילוק.',
      correct_answer: 'see probability track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  if (lesson.summary_en && !lesson.summary_en.includes('probability-family depth')) {
    lesson.summary_en = `${lesson.summary_en} Taught at the ${track} track register with probability-family depth habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const base of BASES) {
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
