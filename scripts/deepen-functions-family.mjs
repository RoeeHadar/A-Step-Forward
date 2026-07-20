#!/usr/bin/env node
/**
 * Deepen functions-family track variants with distinct pedagogy + required facets.
 * Facets: meetings_y_equals_k, reciprocal_1_over_f, creative_graph_reasoning
 * Usage: node scripts/deepen-functions-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const FUNCTION_BASES = [
  'functions_intro',
  'functions_linear',
  'functions_quadratic',
  'functions_exponential',
];

const DEPTH = {
  '3pt': {
    marker: 'FUNCTIONS_DEPTH_3PT',
    title_en: '3pt functions craft: table → graph → equation',
    title_he: 'מלאכת פונקציות 3 יח׳: טבלה → גרף → משוואה',
    body_en: `**3pt functions habit.** Always move **table → sketch → equation** (or reverse) once.
1. Build a short input–output table with easy $x$ values.
2. Sketch the graph lightly; mark intercepts and one interior point.
3. Only then write or use the formula.
4. Meetings with a horizontal line $y = k$: count how many solutions by reading the sketch (number of solutions), not by algebra alone.

Keep parameters rare; prefer concrete numbers.`,
    body_he: `**הרגל פונקציות 3 יח׳.** תמיד עברו **טבלה → סקיצה → משוואה** (או הפוך) פעם אחת.
1. בנו טבלת קלט–פלט קצרה עם ערכי $x$ קלים.
2. סקצו את הגרף; סמנו חיתוכים ונקודה פנימית אחת.
3. רק אז כתבו או השתמשו בנוסחה.
4. מפגשים עם ישר אופקי $y = k$: ספרו פתרונות מהסקיצה (number of solutions), לא מאלגברה בלבד.

המעיטו בפרמטרים; העדיפו מספרים ממשיים.`,
  },
  '4pt': {
    marker: 'FUNCTIONS_DEPTH_4PT',
    title_en: '4pt functions craft: $y=k$ meetings and $1/f$',
    title_he: 'מלאכת פונקציות 4 יח׳: מפגשי $y=k$ ו-$1/f$',
    body_en: `**4pt functions habit.** Two mandatory moves on non-trivial items:
1. **Meetings with $y = k$** (horizontal line): translate to $f(x)=k$, state the number of solutions, and relate to the graph.
2. **Reciprocal $1/f(x)$**: locate where $f=0$ (vertical asymptotes of the reciprocal), where $|f|$ is large (reciprocal near 0), and sketch גרף ההופכי from the original.

Also practice creative graph reasoning: answer a question from the graph without a formula when possible.`,
    body_he: `**הרגל פונקציות 4 יח׳.** שני מהלכים חובה בפריטים לא-טריוויאליים:
1. **מפגשים עם $y = k$** (ישר אופקי): תרגמו ל-$f(x)=k$, ציינו number of solutions, וקשרו לגרף.
2. **הופכי $1/f(x)$**: מצאו היכן $f=0$ (אסימפטוטות אנכיות של ההופכי), היכן $|f|$ גדול (הופכי קרוב ל-0), וסקצו את גרף ההופכי מהמקורי.

תרגלו גם reasoning מהגרף: ענו מהגרף בלי נוסחה כשאפשר.`,
  },
  '5pt': {
    marker: 'FUNCTIONS_DEPTH_5PT',
    title_en: '5pt functions craft: investigation chain + creative graphs',
    title_he: 'מלאכת פונקציות 5 יח׳: שרשרת חקירה וגרפים יצירתיים',
    body_en: `**5pt functions habit.** Run a short **investigation chain**:
domain → intercepts → meetings with $y = k$ → monotonicity/extremum cues → reciprocal $1/f$ sketch when asked.
Always include one **creative** prompt: reason from the graph without a formula (e.g. compare areas, count solutions after a shift, or read $1/f$ qualitatively).
Stay MoE-faithful — no university formal-limit drills.`,
    body_he: `**הרגל פונקציות 5 יח׳.** הריצו **שרשרת חקירה** קצרה:
תחום → חיתוכים → מפגשים עם $y = k$ → רמזי מונוטוניות/קיצון → סקיצת הופכי $1/f$ כשנדרש.
תמיד כללו פרומפט **יצירתי** אחד: reasoning מהגרף בלי נוסחה (השוואת שטחים, ספירת פתרונות אחרי הזזה, או קריאת $1/f$ איכותית).
הישארו נאמנים לתוכנית — בלי תרגול הגדרת גבול פורמלית.`,
  },
  university: {
    marker: 'FUNCTIONS_DEPTH_UNI',
    title_en: 'University bridge: maps, images, and qualitative graphs',
    title_he: 'גשר אוניברסיטאי: העתקות, תמונות וגרפים איכותיים',
    body_en: `**University functions bridge.** Prefer map language: domain, codomain, image of a set.
Use horizontal-line tests ($y = k$) to discuss injectivity cues, and reciprocal $1/f$ only when $f\\neq 0$.
Course-exam pace: sketch first (from the graph / without a formula when possible), then algebra.
No high-school questionnaire framing — write as Calc-1 readiness.`,
    body_he: `**גשר פונקציות לאוניברסיטה.** העדיפו שפת העתקות: תחום, טווח, תמונה של קבוצה.
השתמשו במבחן ישר אופקי ($y = k$) לרמזי חד-חד-ערכיות, ובהופכי $1/f$ רק כש-$f\\neq 0$.
קצב מבחן קורס: סקיצה תחילה (מהגרף / בלי נוסחה כשאפשר), אחר כך אלגברה.
בלי מסגור שאלוני תיכון — כתבו כמוכנות לחדו״א 1.`,
  },
};

const FACET_SECTION = {
  kind: 'theory',
  title_en: 'Facet depth: $y=k$ meetings, reciprocal $1/f$, creative graphs',
  title_he: 'העמקת פנים: מפגשי $y=k$, הופכי $1/f$, גרפים יצירתיים',
  body_en_md: `**Meetings with the horizontal line $y = k$.** Solving $f(x)=k$ is the same as finding intersections of $y=f(x)$ with the horizontal line $y = k$. Read the **number of solutions** from the sketch before algebra.

**Reciprocal $1/f(x)$.** Where $f(x)=0$, the reciprocal has a vertical asymptote. Where $|f|$ is large, $1/f$ is near 0. Sketch גרף ההופכי by reflecting magnitudes about $y=\\pm 1$ qualitatively.

**Creative graph reasoning.** Answer from the graph without a formula: count solutions after a vertical shift, compare heights, or decide whether $1/f$ can cross $y = k$.`,
  body_he_md: `**מפגשים עם הישר האופקי $y = k$.** פתרון $f(x)=k$ הוא מציאת חיתוכים של $y=f(x)$ עם הישר האופקי $y = k$. קראו את **מספר הפתרונות** (number of solutions) מהסקיצה לפני אלגברה.

**הופכי $1/f(x)$.** היכן $f(x)=0$ להופכי יש אסימפטוטה אנכית. היכן $|f|$ גדול, $1/f$ קרוב ל-0. סקצו את גרף ההופכי על ידי היפוך גדלים סביב $y=\\pm 1$ באופן איכותי.

**reasoning יצירתי מהגרף.** ענו מהגרף בלי נוסחה: ספרו פתרונות אחרי הזזה אנכית, השוו גבהים, או החליטו אם $1/f$ יכול לחצות את $y = k$.`,
};

const FACET_QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['meetings_y_equals_k', 'y_equals_k', 'horizontal_meetings'],
    stem_en:
      'For a function $y=f(x)$ from this lesson, explain how to find the number of solutions of $f(x)=k$ using the horizontal line $y = k$, then solve one concrete $k$ algebraically.',
    stem_he:
      'עבור פונקציה $y=f(x)$ משיעור זה, הסבירו איך מוצאים את מספר הפתרונות של $f(x)=k$ בעזרת הישר האופקי $y = k$, ואז פתרו אלגברית עבור $k$ ממשי אחד.',
    correct_answer: 'Count intersections with y=k; solve f(x)=k',
    explanation_en:
      'Graphically: intersections of $y=f(x)$ with the horizontal line $y = k$ give the number of solutions. Algebraically: solve $f(x)=k$ and discard extraneous roots outside the domain.',
    explanation_he:
      'גרפית: חיתוכים עם הישר האופקי $y = k$ נותנים את מספר הפתרונות. אלגברית: פתרו $f(x)=k$ והשליכו שורשים מחוץ לתחום.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['reciprocal_1_over_f', 'one_over_f', 'reciprocal_graph'],
    stem_en:
      'Starting from $y=f(x)$ in this lesson, sketch or describe $y=1/f(x)$: mark where $f=0$, where $|f|$ is large, and one point where $|1/f|=1$.',
    stem_he:
      'מתוך $y=f(x)$ בשיעור זה, סקצו או תארו את $y=1/f(x)$: סמנו היכן $f=0$, היכן $|f|$ גדול, ונקודה אחת שבה $|1/f|=1$.',
    correct_answer: 'Asymptotes at f=0; near 0 when |f| large; |f|=1 => |1/f|=1',
    explanation_en:
      'Vertical asymptotes of the reciprocal sit where $f=0$. When $|f|$ is large, $1/f$ hugs the $x$-axis. Points with $|f|=1$ are fixed in magnitude for $1/f$.',
    explanation_he:
      'אסימפטוטות אנכיות של ההופכי במקומות שבהם $f=0$. כש-$|f|$ גדול, $1/f$ צמוד לציר $x$. בנקודות עם $|f|=1$ הגודל נשמר.',
  },
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['creative_graph_reasoning', 'graph_reasoning', 'sketch_reasoning'],
    stem_en:
      'Creative graph reasoning: from the graph of $y=f(x)$ (without a formula), decide whether $f(x)=k$ can have 0, 1, or 2+ solutions after a vertical shift, and justify from the sketch.',
    stem_he:
      'reasoning יצירתי מהגרף: מהגרף של $y=f(x)$ (בלי נוסחה), החליטו אם אחרי הזזה אנכית למשוואה $f(x)=k$ יכולים להיות 0, 1, או 2+ פתרונות, והצדיקו מהסקיצה.',
    correct_answer: 'Depends on range after shift; read extrema from sketch',
    explanation_en:
      'A vertical shift changes which horizontal lines $y = k$ meet the graph. Read max/min (or end behavior) from the sketch without a formula to decide the number of solutions.',
    explanation_he:
      'הזזה אנכית משנה אילו ישרים אופקיים $y = k$ פוגשים את הגרף. קראו מקסימום/מינימום (או התנהגות בקצות) מהסקיצה בלי נוסחה.',
  },
];

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

  const hasFacetSection = lesson.sections.some(
    (s) => s.title_en && /Facet depth:.*y\s*=\s*k/i.test(s.title_en),
  );
  if (!hasFacetSection) {
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, FACET_SECTION);
    else lesson.sections.push(FACET_SECTION);
  }

  lesson.questions = lesson.questions || [];
  const existingFacets = new Set();
  for (const q of lesson.questions) {
    for (const f of q.facets || []) existingFacets.add(f);
  }
  for (const q of FACET_QUESTIONS) {
    if ((q.facets || []).some((f) => existingFacets.has(f))) continue;
    const ord = lesson.questions.length + 1;
    lesson.questions.push({
      ...q,
      id: `${fileBase}-facet-fn-${ord}`,
      ord,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existingFacets.add(f);
  }

  const qid = `${fileBase}-functions-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    const stems = {
      '3pt': {
        stem_en: `Table→graph→equation: for the core skill in **${fileBase.replace(/__.*/, '')}**, build a 4-row table, sketch, then write the governing equation and check one meeting with $y = k$.`,
        stem_he: `טבלה→גרף→משוואה: למיומנות המרכזית בשיעור, בנו טבלה בת 4 שורות, סקצו, כתבו את המשוואה השולטת, ובדקו מפגש אחד עם $y = k$.`,
      },
      '4pt': {
        stem_en: `Parameter + reciprocal: introduce $k$ into a standard item, solve meetings with $y = k$, then describe $1/f$ near a root of $f$.`,
        stem_he: `פרמטר + הופכי: הכניסו $k$ לפריט סטנדרטי, פתרו מפגשים עם $y = k$, ואז תארו את $1/f$ ליד שורש של $f$.`,
      },
      '5pt': {
        stem_en: `Investigation chain: domain → intercepts → $y = k$ meetings → one creative graph claim without a formula → optional $1/f$ sketch.`,
        stem_he: `שרשרת חקירה: תחום → חיתוכים → מפגשי $y = k$ → טענה יצירתית אחת מהגרף בלי נוסחה → סקיצת $1/f$ אופציונלית.`,
      },
      university: {
        stem_en: `Course-exam style: state domain/image carefully, use a horizontal-line argument for $y = k$, and discuss $1/f$ only on $\{x:f(x)\\neq 0\}$.`,
        stem_he: `סגנון מבחן קורס: נסחו תחום/תמונה בזהירות, השתמשו בטיעון ישר אופקי עבור $y = k$, ודונו ב-$1/f$ רק על $\{x:f(x)\\neq 0\}$.`,
      },
    };
    const s = stems[track];
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: track === '3pt' ? 'medium' : 'hard',
      facets: ['meetings_y_equals_k', 'creative_graph_reasoning'],
      stem_en: s.stem_en,
      stem_he: s.stem_he,
      explanation_en:
        '**Worked path.** Sketch first, count meetings with $y = k$, then algebra. If reciprocal appears, mark zeros of $f$ before sketching $1/f$. See the track-depth and facet sections.',
      explanation_he:
        '**דרך פתרון.** סקיצה תחילה, ספירת מפגשים עם $y = k$, אחר כך אלגברה. אם מופיע הופכי — סמנו אפסי $f$ לפני סקיצת $1/f$. ראו סעיפי העומק והפנים.',
      correct_answer: 'see functions track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  if (lesson.summary_en && !lesson.summary_en.includes('functions-family depth')) {
    lesson.summary_en = `${lesson.summary_en} Taught at the ${track} track register with functions-family depth habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const base of FUNCTION_BASES) {
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
