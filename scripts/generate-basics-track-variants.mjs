#!/usr/bin/env node
/**
 * First-wave required-basics track variants.
 * - Retags canonical lesson to math_track: ["3pt"]
 * - Authors concept__4pt / __5pt / __uni with distinct pedagogy frames
 *
 * Usage: node scripts/generate-basics-track-variants.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIR = path.join(ROOT, 'scripts/seed_data/lessons');

const CONCEPTS = [
  'equations_quadratic',
  'functions_quadratic',
  'equations_linear',
  'functions_linear',
  'factoring',
  'algebra_basics',
  'inequalities',
  'functions_intro',
];

const FRAMES = {
  '3pt': {
    titleSuffixEn: '— 3pt foundations',
    titleSuffixHe: '— יסודות 3 יח׳',
    summaryLeadEn:
      'Taught for the 3-unit track: concrete numbers first, short procedures, and light word problems. ',
    summaryLeadHe: 'נלמד למסלול 3 יח׳: מספרים קונקרטיים תחילה, הליכים קצרים, ובעיות מילוליות קלות. ',
    introNoteEn:
      '\n\n**3pt focus:** Prefer numeric examples, check by substitution, and keep parameters rare. Graph reading is supportive, not the main exam skill here.',
    introNoteHe:
      '\n\n**מיקוד 3 יח׳:** העדיפו דוגמאות מספריות, בדקו בהצבה, והמעיטו בפרמטרים. קריאת גרף תומכת — לא המיומנות המרכזית כאן.',
  },
  '4pt': {
    titleSuffixEn: '— 4pt depth',
    titleSuffixHe: '— העמקה 4 יח׳',
    summaryLeadEn:
      'Taught for the 4-unit track: parameters, multi-representation (algebra ↔ graph), and exam-style multi-step items. ',
    summaryLeadHe:
      'נלמד למסלול 4 יח׳: פרמטרים, ייצוגים מרובים (אלגברה ↔ גרף), ופריטים רב-שלביים בסגנון בחינה. ',
    introNoteEn:
      '\n\n**4pt focus:** Expect parameters ($k$, $m$), “for which…” stems, and graph–formula matching. Justify each step; one-line answers lose method marks.',
    introNoteHe:
      '\n\n**מיקוד 4 יח׳:** צפו לפרמטרים ($k$, $m$), ניסוחי \"עבור אילו…\", והתאמת גרף–נוסחה. הצדיקו כל שלב; תשובה בשורה אחת מאבדת ניקוד שיטה.',
  },
  '5pt': {
    titleSuffixEn: '— 5pt mastery',
    titleSuffixHe: '— שליטה 5 יח׳',
    summaryLeadEn:
      'Taught for the 5-unit track: structured justifications, harder parameters, and links to later analysis topics — still MoE-faithful (no university ε–δ drills). ',
    summaryLeadHe:
      'נלמד למסלול 5 יח׳: הצדקות מובנות, פרמטרים קשים, וקישורים לנושאי אנליזה מאוחרים — עדיין נאמן לתוכנית (בלי תרגול ε–δ אוניברסיטאי). ',
    introNoteEn:
      '\n\n**5pt focus:** Write short deductive chains, classify edge cases, and connect this skill to functions/sequences investigation. Stay inside MoE 5pt scope.',
    introNoteHe:
      '\n\n**מיקוד 5 יח׳:** כתבו שרשראות דדוקטיביות קצרות, סווגו מקרי קצה, וקשרו מיומנות זו לחקירת פונקציות/סדרות. הישארו בתוך היקף 5 יח׳.',
  },
  university: {
    titleSuffixEn: '— university bridge',
    titleSuffixHe: '— גשר לאוניברסיטה',
    summaryLeadEn:
      'University pacing: precise language, set notation where helpful, and course-exam style problems — no Bagrut / MoE questionnaire framing. ',
    summaryLeadHe:
      'קצב אוניברסיטאי: שפה מדויקת, סימון קבוצות כשמועיל, ותרגילי מבחן קורס — בלי מסגור בגרות / שאלוני משרד החינוך. ',
    introNoteEn:
      '\n\n**University focus:** Prefer precise statements (“there exist / for all”), clean algebraic structure, and transfer to Calc 1 / linear algebra habits. This is a bridge lesson, not a high-school exam tip sheet.',
    introNoteHe:
      '\n\n**מיקוד אוניברסיטה:** העדיפו ניסוחים מדויקים (\"קיים / לכל\"), מבנה אלגברי נקי, והעברה להרגלי חדו״א 1 / אלגברה לינארית. זה שיעור גשר, לא דף טיפים לבגרות.',
  },
};

const FUNCTION_FACET_QUESTIONS = {
  meetings_y_equals_k: {
    kind: 'open',
    difficulty: 'medium',
    facets: ['meetings_y_equals_k', 'y_equals_k'],
    stem_en:
      'From the graph of $y=f(x)$ (or an explicit formula if given in class), explain how many solutions the equation $f(x)=k$ can have as the horizontal line $y=k$ moves. Give a concrete numeric example.',
    stem_he:
      'מהגרף של $y=f(x)$ (או מנוסחה מפורשת אם ניתנה בשיעור), הסבירו כמה פתרונות יכולה להיות למשוואה $f(x)=k$ כשהישר האופקי $y=k$ זז. תנו דוגמה מספרית קונקרטית.',
    explanation_en:
      'Each intersection of $y=f(x)$ with the horizontal line $y=k$ is a solution of $f(x)=k$. Raising/lowering $k$ changes the meeting count. Example: for $f(x)=x^2$, $k=4$ gives two meetings, $k=0$ one, $k=-1$ none.',
    explanation_he:
      'כל חיתוך של $y=f(x)$ עם הישר האופקי $y=k$ הוא פתרון של $f(x)=k$. העלאה/הורדה של $k$ משנה את מספר המפגשים. דוגמה: ל-$f(x)=x^2$, $k=4$ שני מפגשים, $k=0$ אחד, $k=-1$ אפס.',
    correct_answer: 'meetings depend on k; example x^2=k',
  },
  reciprocal_1_over_f: {
    kind: 'open',
    difficulty: 'hard',
    facets: ['reciprocal_1_over_f', 'one_over_f'],
    stem_en:
      'Given a sketch of $y=f(x)$ with zeros and a horizontal asymptote, describe qualitatively the graph of $y=1/f(x)$: where it is undefined, how signs flip, and what happens near zeros of $f$.',
    stem_he:
      'בהינתן סקיצה של $y=f(x)$ עם אפסים ואסימפטוטה אופקית, תארו איכותית את גרף $y=1/f(x)$: היכן אינו מוגדר, איך הסימנים מתהפכים, ומה קורה ליד אפסי $f$.',
    explanation_en:
      '$1/f$ is undefined at zeros of $f$ (vertical asymptotes). Where $|f|$ is large, $|1/f|$ is small (near 0). Signs of $1/f$ match signs of $f$. Horizontal asymptote $y=L\\neq0$ of $f$ becomes $y=1/L$ for $1/f$.',
    explanation_he:
      '$1/f$ אינו מוגדר באפסי $f$ (אסימפטוטות אנכיות). היכן ש-$|f|$ גדול, $|1/f|$ קטן. סימני $1/f$ כסימני $f$. אסימפטוטה אופקית $y=L\\neq0$ של $f$ הופכת ל-$y=1/L$ עבור $1/f$.',
    correct_answer: 'undefined at zeros; reciprocal magnitudes; same signs',
  },
  creative_graph_reasoning: {
    kind: 'open',
    difficulty: 'hard',
    facets: ['creative_graph_reasoning', 'graph_reasoning'],
    stem_en:
      'Without writing a closed formula, use only a sketched graph of $y=f(x)$ to decide whether $f$ can be even, odd, or neither — and whether $f(x)=0$ has an odd number of real roots. Justify from the picture.',
    stem_he:
      'בלי לכתוב נוסחה סגורה, השתמשו רק בסקיצת גרף של $y=f(x)$ כדי להחליט אם $f$ יכולה להיות זוגית, אי-זוגית או אף אחת — והאם ל-$f(x)=0$ מספר אי-זוגי של שורשים ממשיים. נמקו מהתמונה.',
    explanation_en:
      'Even ⇒ mirror symmetry about the $y$-axis; odd ⇒ 180° rotational symmetry about the origin. Root count is the number of $x$-intercepts; an odd count is possible for odd-degree-like shapes that cross the axis an odd number of times.',
    explanation_he:
      'זוגית ⇒ שיקוף סביב ציר $y$; אי-זוגית ⇒ סיבוב 180° סביב הראשית. מספר שורשים = מספר חיתוכי ציר $x$; מספר אי-זוגי אפשרי לצורות שחוצות את הציר מספר אי-זוגי של פעמים.',
    correct_answer: 'symmetry from sketch; count x-intercepts',
  },
};

function deepClone(x) {
  return JSON.parse(JSON.stringify(x));
}

function stripTrackVoice(text, track) {
  if (typeof text !== 'string') return text;
  let t = text;
  if (track === 'university') {
    t = t
      .replace(/\bBagrut\b/gi, 'course')
      .replace(/בגרות/g, 'מבחן קורס')
      .replace(/\b3pt\b/g, 'introductory')
      .replace(/\b4pt\b/g, 'intermediate')
      .replace(/\b5pt\b/g, 'advanced HS');
  }
  return t;
}

function mapStrings(obj, fn) {
  if (typeof obj === 'string') return fn(obj);
  if (Array.isArray(obj)) return obj.map((v) => mapStrings(v, fn));
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) out[k] = mapStrings(v, fn);
    return out;
  }
  return obj;
}

function applyFrame(lesson, track, canonical) {
  const frame = FRAMES[track];
  const baseTitleEn = (lesson.title_en || canonical).replace(/\s*—\s*(3pt|4pt|5pt|university).*$/i, '');
  const baseTitleHe = (lesson.title_he || '').replace(/\s*—\s*.*$/u, '');

  lesson.title_en = `${baseTitleEn.trim()} ${frame.titleSuffixEn}`;
  lesson.title_he = `${baseTitleHe.trim()} ${frame.titleSuffixHe}`;
  lesson.summary_en = frame.summaryLeadEn + (lesson.summary_en || '');
  lesson.summary_he = frame.summaryLeadHe + (lesson.summary_he || '');

  const intro = (lesson.sections || []).find((s) => s.kind === 'intro');
  if (intro) {
    intro.body_en_md = (intro.body_en_md || '') + frame.introNoteEn;
    intro.body_he_md = (intro.body_he_md || '') + frame.introNoteHe;
  }

  // Track-owned theory insert (distinct pedagogy marker)
  const theoryInsert = {
    kind: 'theory',
    title_en: `Track lens: how ${track} learners should practice this`,
    title_he: `עדשת מסלול: איך לומדי ${track} צריכים לתרגל`,
    body_en_md:
      track === '3pt'
        ? 'Work **numeric** stems first. After each solve, substitute back. Delay heavy parameters until the procedure feels automatic.'
        : track === '4pt'
          ? 'Alternate **algebra ↔ graph**. For every formula, sketch a quick picture; for every sketch, write a matching equation. Add one parameter ($k$) per practice block.'
          : track === '5pt'
            ? 'Write **justifications** in 3–5 sentences: hypothesis → tool → conclusion. Include one edge case (no solution / infinite / boundary) every session.'
            : 'State claims with **quantifiers** when useful. Prefer structure theorems and clean notation over exam-tip mnemonics. Connect each drill to a Calc-1 habit (limits of polynomials, continuity of elementary functions, or linear maps).',
    body_he_md:
      track === '3pt'
        ? 'עבדו תחילה על פריטים **מספריים**. אחרי כל פתרון, הציבו חזרה. דחו פרמטרים כבדים עד שההליך אוטומטי.'
        : track === '4pt'
          ? 'החליפו בין **אלגברה ↔ גרף**. לכל נוסחה סקיצה קצרה; לכל סקיצה משוואה תואמת. הוסיפו פרמטר ($k$) אחד לכל בלוק תרגול.'
          : track === '5pt'
            ? 'כתבו **הצדקות** ב-3–5 משפטים: הנחה → כלי → מסקנה. כללו מקרה קצה אחד (אין פתרון / אינסוף / שפה) בכל מפגש.'
            : 'נסחו טענות עם **כמתים** כשמועיל. העדיפו משפטי מבנה וסימון נקי על פני מנמוניקות לבחינה. קשרו כל תרגיל להרגל חדו״א 1.',
  };
  const sections = lesson.sections || [];
  const defIdx = sections.findIndex((s) => s.kind === 'definition' || s.kind === 'theory');
  sections.splice(defIdx >= 0 ? defIdx + 1 : 1, 0, theoryInsert);
  lesson.sections = sections;

  lesson = mapStrings(lesson, (s) => stripTrackVoice(s, track));

  // Function-family facet questions on function concepts
  if (canonical.startsWith('functions_')) {
    const extras = Object.values(FUNCTION_FACET_QUESTIONS).map((q, i) => ({
      ...q,
      id: `${canonical}__${track === 'university' ? 'uni' : track}-facet-${i + 1}`,
      ord: (lesson.questions?.length || 0) + i + 1,
      skill_atoms: lesson.skill_atom_bank?.slice?.(0, 2) || [],
      points_level_min: track === '3pt' ? '3pt' : track === '4pt' ? '4pt' : track === '5pt' ? '5pt' : null,
    }));
    // Also add a short theory section that evidences keywords
    lesson.sections.push({
      kind: 'theory',
      title_en: 'High-level function facets: $y=k$, $1/f$, creative graph reasoning',
      title_he: 'פנים גבוהות של פונקציות: $y=k$, $1/f$, חשיבה גרפית יצירתית',
      body_en_md: `**Meetings with $y=k$:** solving $f(x)=k$ is reading how many times the graph meets the horizontal line $y=k$.

**Reciprocal $1/f(x)$:** sketch from zeros and asymptotes of $f$ without recomputing a full formula from scratch.

**Creative graph reasoning:** answer existence / symmetry / root-count questions from a sketch, without a closed formula.`,
      body_he_md: `**מפגשים עם $y=k$:** פתרון $f(x)=k$ הוא קריאת כמה פעמים הגרף פוגש את הישר האופקי $y=k$.

**הופכי $1/f(x)$:** סקיצה מאפסים ואסימפטוטות של $f$ בלי לחשב נוסחה מלאה מחדש.

**חשיבה גרפית יצירתית:** ענו על קיום / סימטריה / מספר שורשים מהסקיצה, בלי נוסחה סגורה.`,
    });
    lesson.questions = [...(lesson.questions || []), ...extras];
  }

  return lesson;
}

function writeLesson(fileBase, lesson) {
  const fp = path.join(DIR, `${fileBase}.json`);
  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  console.log('wrote', fileBase);
}

function main() {
  for (const canonical of CONCEPTS) {
    const srcPath = path.join(DIR, `${canonical}.json`);
    if (!fs.existsSync(srcPath)) {
      console.warn('missing', canonical);
      continue;
    }
    const base = JSON.parse(fs.readFileSync(srcPath, 'utf8'));

    // Canonical = 3pt-owned
    let three = deepClone(base);
    three.concept_id = canonical;
    three.math_track = ['3pt'];
    three.level = 'high_school';
    three = applyFrame(three, '3pt', canonical);
    writeLesson(canonical, three);

    for (const track of ['4pt', '5pt', 'university']) {
      const suffix = track === 'university' ? 'uni' : track;
      const id = `${canonical}__${suffix}`;
      let v = deepClone(base);
      v.concept_id = id;
      v.math_track = track === 'university' ? ['university'] : [track];
      v.level = track === 'university' ? 'university' : 'high_school';
      v = applyFrame(v, track, canonical);
      // Re-id questions to avoid collisions across variants
      if (Array.isArray(v.questions)) {
        v.questions = v.questions.map((q, i) => ({
          ...q,
          id: q.id ? `${id}-${q.id}` : `${id}-q${i + 1}`,
        }));
      }
      writeLesson(id, v);
    }
  }
}

main();
