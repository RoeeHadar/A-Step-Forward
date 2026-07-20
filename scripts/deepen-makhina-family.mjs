#!/usr/bin/env node
/**
 * Deepen *_makhina lessons with bridge_to_uni + prerequisite_gaps facets.
 * Usage: node scripts/deepen-makhina-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const DEPTH = {
  marker: 'MAKHINA_DEPTH',
  title_en: 'Makhina craft: bridge to university + close prerequisite gaps',
  title_he: 'מלאכת מכינה: גשר לאוניברסיטה וסגירת פערי קדם',
  body_en: `**Makhina habit.** Every non-trivial item should do two things:
1. **Bridge to university / Calc 1:** name the university skill this item prepares (limits fluency, algebra of functions, vector geometry, etc.).
2. **Prerequisite gaps:** state which high-school gap would block the step (factoring, trig identity, units, free-body setup) and close it in one short sub-drill.

Write as preparatory course pace — not as a school questionnaire.`,
  body_he: `**הרגל מכינה.** בכל פריט לא-טריוויאלי עשו שני דברים:
1. **גשר לאוניברסיטה / חדו״א 1:** ציינו איזו מיומנות אוניברסיטאית הפריט מכין (שטף גבולות, אלגברת פונקציות, גאומטריה וקטורית וכו׳).
2. **פערי קדם:** ציינו איזה פער תיכוני יחסום את הצעד (פירוק לגורמים, זהות טריג, יחידות, הכנת דיאגרמת כוחות) וסגרו אותו בתרגיל-משנה קצר.

כתבו בקצב קורס הכנה — לא כשאלון בית-ספרי.`,
};

const FACET = {
  kind: 'theory',
  title_en: 'Facet depth: bridge to university and prerequisite gaps',
  title_he: 'העמקת פנים: גשר לאוניברסיטה ופערי קדם',
  body_en_md: `**Bridge to university.** Explicitly connect the drill to Calc 1 / university physics readiness: what will the learner meet in the first weeks of the degree course?

**Prerequisite gaps.** Name the blocking prerequisite (algebra, trig, units, graph reading) and repair it with a 2–3 line mini-check before the main solution.`,
  body_he_md: `**גשר לאוניברסיטה.** קשרו במפורש את התרגיל למוכנות לחדו״א 1 / פיזיקה אוניברסיטאית: מה יפגוש הלומד בשבועות הראשונים של הקורס?

**פערי קדם.** ציינו את הקדם החוסם (אלגברה, טריג, יחידות, קריאת גרף) ותקנו אותו בבדיקת מיני של 2–3 שורות לפני הפתרון הראשי.`,
};

const QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['bridge_to_uni'],
    stem_en:
      'Name the university / Calc 1 skill this lesson item prepares, and rewrite the final answer in the language a first-year course would expect.',
    stem_he:
      'ציינו את מיומנות האוניברסיטה / חדו״א 1 שפריט זה מכין, וכתבו מחדש את התשובה הסופית בשפה שקורס שנה א׳ מצפה לה.',
    correct_answer: 'named uni skill + course-style statement of result',
    explanation_en:
      'Bridge to university means stating the target course skill (for example linear approximation, free-body setup, or definite-integral accumulation) and presenting the result without school-exam framing. Use precise definitions and units so the write-up could sit in a Calc 1 or intro physics homework set.',
    explanation_he:
      'גשר לאוניברסיטה פירושו לציין את מיומנות הקורס היעד (למשל קירוב לינארי, הכנת דיאגרמת כוחות, או צבירת אינטגרל מסוים) ולהציג את התוצאה בלי מסגור בחינת בית-ספר. השתמשו בהגדרות ויחידות מדויקות כך שהכתיבה תתאים לשיעורי בית בחדו״א 1 או פיזיקה מבוא.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['prerequisite_gaps'],
    stem_en:
      'Identify one prerequisite gap that would block a learner on this item, give a 3-line repair drill, then solve the main item.',
    stem_he:
      'זהו פער קדם אחד שיחסום לומד בפריט זה, תנו תרגיל תיקון של 3 שורות, ואז פתרו את הפריט הראשי.',
    correct_answer: 'named gap + mini-repair + main solution',
    explanation_en:
      'Prerequisite gaps are the real blockers: missing factoring, shaky trig ratios, unit confusion, or an incomplete diagram. Name the gap explicitly, run a tiny repair (two or three lines), then return to the main makhina item. Skipping the gap diagnosis is how learners stall in the first university month.',
    explanation_he:
      'פערי קדם הם החוסמים האמיתיים: פירוק חסר, יחסי טריג רופפים, בלבול יחידות, או דיאגרמה חלקית. ציינו את הפער במפורש, הריצו תיקון זעיר (שתיים–שלוש שורות), וחזרו לפריט המכינה הראשי. דילוג על אבחון הפער הוא איך לומדים נתקעים בחודש האוניברסיטה הראשון.',
  },
];

function deepenFile(fileBase) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  lesson.sections = lesson.sections || [];

  if (!lesson.sections.some((s) => (s.body_en_md || '').includes(DEPTH.marker))) {
    const insert = {
      kind: 'theory',
      title_en: DEPTH.title_en,
      title_he: DEPTH.title_he,
      body_en_md: `<!-- ${DEPTH.marker} -->\n${DEPTH.body_en}`,
      body_he_md: DEPTH.body_he,
    };
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
    else lesson.sections.push(insert);
  }

  if (!lesson.sections.some((s) => s.title_en === FACET.title_en)) {
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
      id: `${fileBase}-facet-makhina-${lesson.questions.length + 1}`,
      ord: lesson.questions.length + 1,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existing.add(f);
  }

  const qid = `${fileBase}-makhina-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: 'hard',
      facets: ['bridge_to_uni', 'prerequisite_gaps'],
      stem_en:
        'Track drill: close one prerequisite gap in 3 lines, solve the core item, then restate the result as a university / Calc 1 readiness takeaway.',
      stem_he:
        'תרגיל מסלול: סגרו פער קדם אחד ב-3 שורות, פתרו את הפריט המרכזי, ונסחו מחדש את התוצאה כלקח מוכנות לאוניברסיטה / חדו״א 1.',
      explanation_en:
        '**Worked path for makhina.** Diagnose the blocking prerequisite, repair it briefly, solve the main problem with labeled steps, then name the university bridge skill this item feeds. Keep the write-up in preparatory-course voice.',
      explanation_he:
        '**דרך פתרון למכינה.** אבחנו את הקדם החוסם, תקנו בקצרה, פתרו את הבעיה הראשית עם שלבים מסומנים, וציינו את מיומנות הגשר האוניברסיטאית שהפריט מזין. השאירו כתיבה בקול קורס הכנה.',
      correct_answer: 'see makhina track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  if (lesson.summary_en && !lesson.summary_en.includes('makhina-family depth')) {
    lesson.summary_en = `${lesson.summary_en} Taught with makhina-family depth habits (bridge to university + prerequisite gaps).`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

const files = fs
  .readdirSync(DIR)
  .filter((f) => f.endsWith('_makhina.json') || f.includes('_makhina__'))
  .map((f) => f.replace(/\.json$/, ''));

let n = 0;
for (const id of files) {
  if (deepenFile(id)) {
    console.log('deepened', id);
    n++;
  }
}
console.log('deepened files', n);
