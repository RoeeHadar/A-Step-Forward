#!/usr/bin/env node
/**
 * Deepen trigonometry + analytic-geometry families with track pedagogy + facets.
 * Trig facets: right_triangle_vs_unit_circle, identity_application
 * Analytic facets: line_circle_tangent, locus_reasoning
 * Usage: node scripts/deepen-geom-trig-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const TRIG_BASES = [
  'trigonometry_ratios',
  'trigonometry_identities',
  'trigonometry_equations',
];

const ANALYTIC_BASES = [
  'analytic_geometry',
  'analytic_geometry_basic',
  'analytic_geometry_4pt',
  'analytic_geometry_5pt',
  'analytic_geometry__5pt',
  'analytic_geometry_conics',
];

const TRIG_DEPTH = {
  '3pt': {
    marker: 'TRIG_DEPTH_3PT',
    title_en: '3pt trig craft: right triangle first',
    title_he: 'מלאכת טריג 3 יח׳: משולש ישר-זווית תחילה',
    body_en: `**3pt trig habit.** Start from a **right triangle** sketch before any identity.
1. Label opposite / adjacent / hypotenuse for the angle in play.
2. Write SOH-CAH-TOA once, then compute.
3. Unit-circle language is optional — only if the stem already uses degrees on a circle.
4. Keep identity application light: one Pythagorean rewrite at most.`,
    body_he: `**הרגל טריג 3 יח׳.** התחילו מסקיצת **משולש ישר-זווית** לפני כל זהות.
1. סמנו ניצב מול / ליד / יתר לזווית הרלוונטית.
2. כתבו SOH-CAH-TOA פעם אחת, ואז חשבו.
3. שפת מעגל היחידה אופציונלית — רק אם הניסוח כבר על מעגל.
4. יישום זהויות קל: לכל היותר שכתוב פיתגורסי אחד.`,
  },
  '4pt': {
    marker: 'TRIG_DEPTH_4PT',
    title_en: '4pt trig craft: triangle ↔ unit circle + one identity',
    title_he: 'מלאכת טריג 4 יח׳: משולש ↔ מעגל יחידה + זהות אחת',
    body_en: `**4pt trig habit.** Explicitly bridge **right triangle vs unit circle**:
same ratios, different geometric picture. Then apply **one** identity
(Pythagorean or double-angle) and check the result in the original picture.`,
    body_he: `**הרגל טריג 4 יח׳.** גשרו במפורש בין **משולש ישר-זווית למעגל יחידה**:
אותם יחסים, תמונה גאומטרית אחרת. אחר כך יישמו **זהות אחת**
(פיתגורס או זווית כפולה) ובדקו בתוצאה בתמונה המקורית.`,
  },
  '5pt': {
    marker: 'TRIG_DEPTH_5PT',
    title_en: '5pt trig craft: identity chains and equation sets',
    title_he: 'מלאכת טריג 5 יח׳: שרשראות זהויות וקבוצות משוואות',
    body_en: `**5pt trig habit.** Write a short **identity-application chain** (2–3 steps),
then solve an equation on $[0,2\\pi)$ or a MoE interval. Always state whether
you are thinking on the right triangle or on the unit circle before substituting.`,
    body_he: `**הרגל טריג 5 יח׳.** כתבו **שרשרת יישום זהויות** קצרה (2–3 צעדים),
ואז פתרו משוואה ב-$[0,2\\pi)$ או בקטע מהתוכנית. תמיד ציינו אם אתם
חושבים במשולש ישר-זווית או במעגל יחידה לפני הצבה.`,
  },
  university: {
    marker: 'TRIG_DEPTH_UNI',
    title_en: 'University bridge: trig as circular functions',
    title_he: 'גשר אוניברסיטאי: טריג כפונקציות מעגליות',
    body_en: `**University trig bridge.** Prefer radian measure and circular-function language.
Identity application is algebraic manipulation on $\\sin,\\cos$ as maps $\\mathbb{R}\\to[-1,1]$.
Course-exam pace: state domain, apply identity, solve, classify solutions modulo $2\\pi$.`,
    body_he: `**גשר טריג לאוניברסיטה.** העדיפו רדיאנים ושפת פונקציות מעגליות.
יישום זהויות הוא מניפולציה אלגברית על $\\sin,\\cos$ כהעתקות $\\mathbb{R}\\to[-1,1]$.
קצב מבחן קורס: תחום → זהות → פתרון → סיווג מודולו $2\\pi$.`,
  },
};

const ANALYTIC_DEPTH = {
  '3pt': {
    marker: 'ANALYTIC_DEPTH_3PT',
    title_en: '3pt analytic craft: distance and midpoint first',
    title_he: 'מלאכת אנליטית 3 יח׳: מרחק ואמצע תחילה',
    body_en: `**3pt analytic habit.** Plot two points, compute distance and midpoint before slopes.
Line–circle meetings: substitute the line into the circle and count roots.
Keep locus language light — describe the set in words after algebra.`,
    body_he: `**הרגל אנליטית 3 יח׳.** סמנו שתי נקודות, חשבו מרחק ואמצע לפני שיפועים.
מפגשי ישר–מעגל: הציבו את הישר במעגל וספרו שורשים.
המעיטו בשפת מקום גאומטרי — תארו את הקבוצה במילים אחרי האלגברה.`,
  },
  '4pt': {
    marker: 'ANALYTIC_DEPTH_4PT',
    title_en: '4pt analytic craft: line–circle tangency conditions',
    title_he: 'מלאכת אנליטית 4 יח׳: תנאי משיק ישר–מעגל',
    body_en: `**4pt analytic habit.** For **line–circle tangent** problems: set discriminant zero
after substitution, or equate distance from center to line with the radius.
Always sketch before algebra.`,
    body_he: `**הרגל אנליטית 4 יח׳.** בבעיות **משיק ישר–מעגל**: הציבו דיסקרימיננטה אפס
אחרי הצבה, או השוו מרחק מהמרכז לישר לרדיוס.
תמיד סקצו לפני אלגברה.`,
  },
  '5pt': {
    marker: 'ANALYTIC_DEPTH_5PT',
    title_en: '5pt analytic craft: tangency + locus reasoning',
    title_he: 'מלאכת אנליטית 5 יח׳: משיקות + חשיבת מקום גאומטרי',
    body_en: `**5pt analytic habit.** Combine **line–circle tangency** with **locus reasoning**:
after solving, name the geometric set (line, circle, ray) in one sentence.
Include one parameter case ($k$) that changes the locus type.`,
    body_he: `**הרגל אנליטית 5 יח׳.** שלבו **משיק ישר–מעגל** עם **חשיבת מקום גאומטרי**:
אחרי הפתרון, ציינו במשפט אחד את הקבוצה הגאומטרית (ישר, מעגל, קרן).
כללו מקרה פרמטר ($k$) אחד שמשנה את סוג המקום.`,
  },
  university: {
    marker: 'ANALYTIC_DEPTH_UNI',
    title_en: 'University bridge: loci as level sets',
    title_he: 'גשר אוניברסיטאי: מקומות כקבוצות רמה',
    body_en: `**University analytic bridge.** Treat loci as level sets $F(x,y)=c$.
Tangency is a multiplicity condition on the resulting algebraic equation.
Course-exam pace: geometric claim → algebraic translation → case split.`,
    body_he: `**גשר אנליטית לאוניברסיטה.** התייחסו למקומות כקבוצות רמה $F(x,y)=c$.
משיקות הן תנאי ריבוי על המשוואה האלגברית המתקבלת.
קצב מבחן קורס: טענה גאומטרית → תרגום אלגברי → פיצול מקרים.`,
  },
};

const TRIG_FACET = {
  kind: 'theory',
  title_en: 'Facet depth: right triangle vs unit circle; identity application',
  title_he: 'העמקת פנים: משולש ישר-זווית מול מעגל יחידה; יישום זהויות',
  body_en_md: `**Right triangle vs unit circle.** In a right triangle, $\\sin\\theta$ is opposite/hypotenuse. On the unit circle, $\\sin\\theta$ is the $y$-coordinate of the point at angle $\\theta$. Same number, different picture — switch only when it shortens the argument.

**Identity application.** Rewrite using Pythagorean or angle-addition identities, then substitute back. Label each identity step so the chain is checkable.`,
  body_he_md: `**משולש ישר-זווית מול מעגל יחידה.** במשולש, $\\sin\\theta$ הוא מול/יתר. במעגל היחידה, $\\sin\\theta$ הוא שיעור $y$ של הנקודה בזווית $\\theta$. אותו מספר, תמונה אחרת — עברו רק כשזה מקצר.

**יישום זהויות.** שכתבו בזהות פיתגורס או חיבור זוויות, ואז הציבו חזרה. סמנו כל צעד זהות כדי שהשרשרת תהיה ניתנת לבדיקה.`,
};

const ANALYTIC_FACET = {
  kind: 'theory',
  title_en: 'Facet depth: line–circle tangency and locus reasoning',
  title_he: 'העמקת פנים: משיק ישר–מעגל וחשיבת מקום גאומטרי',
  body_en_md: `**Line–circle tangent.** Substitute the line into the circle; tangency means the quadratic in the parameter has discriminant zero. Equivalently, distance from center to line equals radius.

**Locus reasoning.** After algebra, name the set: “the locus is the circle centered at …”, or “the set of points equidistant from …”. Sketch the locus before claiming completeness.`,
  body_he_md: `**משיק ישר–מעגל.** הציבו את הישר במעגל; משיקות פירושה דיסקרימיננטה אפס בפרמטר. שקיל: מרחק מהמרכז לישר שווה לרדיוס.

**חשיבת מקום גאומטרי.** אחרי אלגברה, תנו שם לקבוצה: \"המקום הוא המעגל שמרכזו…\", או \"קבוצת הנקודות במרחק שווה מ…\". סקצו את המקום לפני טענת שלמות.`,
};

const TRIG_QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['right_triangle_vs_unit_circle', 'triangle_vs_circle'],
    stem_en:
      'Explain the same sine value once from a right triangle and once from the unit circle, then compute $\\sin$ of an acute angle from this lesson both ways.',
    stem_he:
      'הסבירו את אותו ערך סינוס פעם ממשולש ישר-זווית ופעם ממעגל היחידה, ואז חשבו $\\sin$ של זווית חדה מהשיעור בשתי הדרכים.',
    correct_answer: 'opp/hyp vs y-coordinate on unit circle; same numeric value',
    explanation_en:
      'In a right triangle, $\\sin\\theta$ is opposite over hypotenuse. On the unit circle, the same $\\sin\\theta$ is the $y$-coordinate of the terminal point. Compute both ways for one acute angle from the lesson and confirm the numbers match; the pictures differ, not the value. Prefer the triangle when a side length is given, and the circle when the stem is already angular.',
    explanation_he:
      'במשולש ישר-זווית, $\\sin\\theta$ הוא מול חלקי יתר. במעגל היחידה אותו $\\sin\\theta$ הוא שיעור $y$ של נקודת הקצה. חשבו בשתי הדרכים לזווית חדה מהשיעור ואמתו שהמספרים זהים; התמונות שונות, לא הערך. העדיפו משולש כשנתון אורך צלע, ומעגל כשהניסוח כבר זוויתי.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['identity_application', 'trig_identity'],
    stem_en:
      'Apply a Pythagorean or angle-addition identity to simplify an expression from this lesson, showing each identity step, then verify numerically at one angle.',
    stem_he:
      'יישמו זהות פיתגורס או חיבור זוויות לפישוט ביטוי מהשיעור, עם כל צעד זהות, ואמתו מספרית בזווית אחת.',
    correct_answer: 'named identity steps + numeric check',
    explanation_en:
      'Name the identity (for example $\\sin^2\\theta+\\cos^2\\theta=1$ or an angle-addition formula), rewrite the target expression in two or three labeled steps, then substitute a convenient angle to verify. Identity application fails most often when a step is skipped — keep the chain visible so each equality can be checked.',
    explanation_he:
      'ציינו את הזהות (למשל $\\sin^2\\theta+\\cos^2\\theta=1$ או נוסחת חיבור זוויות), שכתבו את הביטוי בשניים–שלושה צעדים מסומנים, ואז הציבו זווית נוחה לאימות. יישום זהויות נכשל לרוב כשמדלגים על צעד — השאירו את השרשרת גלויה.',
  },
];

const ANALYTIC_QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['line_circle_tangent', 'tangent_condition'],
    stem_en:
      'For a line and a circle from this lesson, set up the tangency condition two ways (discriminant zero after substitution; distance equals radius) and solve for the missing parameter if any.',
    stem_he:
      'עבור ישר ומעגל מהשיעור, הציבו את תנאי המשיקות בשתי דרכים (דיסקרימיננטה אפס אחרי הצבה; מרחק שווה לרדיוס) ופתרו לפרמטר החסר אם יש.',
    correct_answer: 'Delta=0 after sub; dist(center,line)=r',
    explanation_en:
      'Substitute the line into the circle to get a quadratic; tangency means discriminant zero. Independently, set the distance from the center to the line equal to the radius. Both conditions must agree. Sketch the line–circle pair before algebra so extraneous roots from absolute values are caught early.',
    explanation_he:
      'הציבו את הישר במעגל לקבלת ריבועית; משיקות פירושה דיסקרימיננטה אפס. בנפרד, השוו את המרחק מהמרכז לישר לרדיוס. שני התנאים חייבים להסכים. סקצו את זוג ישר–מעגל לפני אלגברה כדי לתפוס שורשים מיותרים מערך מוחלט.',
  },
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['locus_reasoning', 'locus'],
    stem_en:
      'After solving an analytic condition from this lesson, name the locus in one geometric sentence and sketch it; state what changes if a parameter $k$ crosses a critical value.',
    stem_he:
      'אחרי פתרון תנאי אנליטי מהשיעור, תנו שם למקום במשפט גאומטרי אחד וסקצו; ציינו מה משתנה אם פרמטר $k$ חוצה ערך קריטי.',
    correct_answer: 'named geometric set + sketch + k threshold',
    explanation_en:
      'Locus reasoning means translating the algebraic solution set into a geometric object: line, circle, ray, or pair of lines. Write one sentence naming the set, sketch it, and note how a parameter $k$ can change the type (for example empty, tangent, or two intersections). Do not leave the answer as an equation alone.',
    explanation_he:
      'חשיבת מקום גאומטרי פירושה תרגום קבוצת הפתרון האלגברית לעצם גאומטרי: ישר, מעגל, קרן או זוג ישרים. כתבו משפט אחד שנותן שם לקבוצה, סקצו, וציינו איך פרמטר $k$ יכול לשנות סוג (למשל ריק, משיק, או שני חיתוכים). אל תשאירו את התשובה כמשוואה בלבד.',
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
  const DEPTH = family === 'trig' ? TRIG_DEPTH : ANALYTIC_DEPTH;
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

  const facet = family === 'trig' ? TRIG_FACET : ANALYTIC_FACET;
  const facetRe =
    family === 'trig'
      ? /Facet depth:.*triangle vs unit circle/i
      : /Facet depth:.*line.?circle/i;
  if (!lesson.sections.some((s) => s.title_en && facetRe.test(s.title_en))) {
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, facet);
    else lesson.sections.push(facet);
  }

  const questions = family === 'trig' ? TRIG_QUESTIONS : ANALYTIC_QUESTIONS;
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
      id: `${fileBase}-facet-${family}-${ord}`,
      ord,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existingFacets.add(f);
  }

  const qid = `${fileBase}-${family}-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    const stem =
      family === 'trig'
        ? {
            stem_en: `Track drill: bridge right-triangle and unit-circle views for one angle from this lesson, then apply one identity and check.`,
            stem_he: `תרגיל מסלול: גשרו בין משולש ישר-זווית למעגל יחידה לזווית אחת מהשיעור, יישמו זהות אחת ובדקו.`,
          }
        : {
            stem_en: `Track drill: set a line–circle tangency condition, solve, then name the locus in one geometric sentence.`,
            stem_he: `תרגיל מסלול: הציבו תנאי משיק ישר–מעגל, פתרו, ותנו שם למקום במשפט גאומטרי אחד.`,
          };
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: track === '3pt' ? 'medium' : 'hard',
      facets:
        family === 'trig'
          ? ['right_triangle_vs_unit_circle', 'identity_application']
          : ['line_circle_tangent', 'locus_reasoning'],
      stem_en: stem.stem_en,
      stem_he: stem.stem_he,
      explanation_en:
        family === 'trig'
          ? '**Worked path for trig track depth.** Sketch the right triangle with opposite, adjacent, and hypotenuse labeled for the angle in play. If the stem is angular, mark the same angle on the unit circle and read sine or cosine as a coordinate. Apply one named identity with two or three labeled steps, then verify at a convenient angle. Keep triangle-versus-circle language explicit so the register matches the track and graders can see which picture you used.'
          : '**Worked path for analytic track depth.** Sketch the line and circle first. Impose tangency by setting the discriminant to zero after substitution, or by equating distance from center to line with the radius; both must agree. Solve for any missing parameter, then translate the algebraic solution set into a named locus in one geometric sentence and note how a parameter threshold can change the locus type.',
      explanation_he:
        family === 'trig'
          ? '**דרך פתרון לעומק מסלול הטריג.** סקצו משולש ישר-זווית עם מול, ליד ויתר מסומנים לזווית הרלוונטית. אם הניסוח זוויתי, סמנו את אותה זווית על מעגל היחידה וקראו סינוס או קוסינוס כשיעור. יישמו זהות אחת עם שני–שלושה צעדים מסומנים, ואמתו בזווית נוחה. השאירו את שפת משולש מול מעגל מפורשת כדי שהמסלול יהיה ברור.'
          : '**דרך פתרון לעומק מסלול האנליטית.** סקצו תחילה ישר ומעגל. הציבו משיקות בדיסקרימיננטה אפס אחרי הצבה, או בהשוואת מרחק מהמרכז לישר לרדיוס; שני התנאים חייבים להסכים. פתרו לפרמטר החסר, ותרגמו את קבוצת הפתרון האלגברית למקום עם שם במשפט גאומטרי אחד, כולל סף פרמטר שמשנה סוג.',
      correct_answer: 'see track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  const tag = family === 'trig' ? 'trig-family depth' : 'analytic-family depth';
  if (lesson.summary_en && !lesson.summary_en.includes(tag)) {
    lesson.summary_en = `${lesson.summary_en} Taught at the ${track} track register with ${tag} habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const base of TRIG_BASES) {
  const files = fs
    .readdirSync(DIR)
    .filter((f) => f === `${base}.json` || f.startsWith(`${base}__`))
    .map((f) => f.replace(/\.json$/, ''));
  for (const id of files) {
    if (deepenFile(id, 'trig')) {
      console.log('deepened', id);
      n++;
    }
  }
}
for (const base of ANALYTIC_BASES) {
  // Exact filenames (some already include _4pt/_5pt without __)
  const candidates = new Set([base]);
  for (const f of fs.readdirSync(DIR)) {
    if (f === `${base}.json` || f.startsWith(`${base}__`)) {
      candidates.add(f.replace(/\.json$/, ''));
    }
  }
  for (const id of candidates) {
    if (deepenFile(id, 'analytic')) {
      console.log('deepened', id);
      n++;
    }
  }
}
console.log('deepened files', n);
