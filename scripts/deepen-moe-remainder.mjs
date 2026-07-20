#!/usr/bin/env node
/**
 * Deepen remaining MoE-core families not covered by prior family scripts:
 * geometry, exponents/logs, combinatorics, stats/sample_space, limits,
 * function transformations/analysis, percentages, uni-bridge leftovers.
 *
 * Usage: node scripts/deepen-moe-remainder.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

/** @type {Record<string, { prefixes: string[], marker: string, title: {en:string,he:string}, body: {en:string,he:string}, facet?: object, questions?: object[] }>} */
const FAMILIES = {
  geometry: {
    prefixes: [
      'geometry_',
      'circles',
      'pythagorean_',
      'similar_triangles',
      'quadrilaterals',
      'triangles_congruence',
      'spatial_reasoning',
      '3d_solids_',
      'euclidean_geometry_',
      'plane_trigonometry_',
    ],
    marker: 'GEOM_DEPTH',
    title: {
      en: 'Geometry craft: diagram first, then measure',
      he: 'מלאכת גאומטריה: דיאגרמה תחילה, אחר כך מדידה',
    },
    body: {
      en: `**Geometry habit.** Sketch and label every given before computing.
Mark equal lengths/angles, write the governing theorem (Pythagoras, similarity, congruence, circle theorems), then calculate.
Always state units and whether the result is length, area, or angle.`,
      he: `**הרגל גאומטריה.** סקצו וסמנו כל נתון לפני חישוב.
סמנו אורכים/זוויות שווים, כתבו את המשפט השולט (פיתגורס, דמיון, חפיפה, משפטי מעגל), ואז חשבו.
תמיד ציינו יחידות ואם התוצאה אורך, שטח או זווית.`,
    },
  },
  exponents_logs: {
    prefixes: ['exponents', 'logarithms', 'percentages_'],
    marker: 'EXPLOG_DEPTH',
    title: {
      en: 'Exponents & logs craft: laws before calculator',
      he: 'מלאכת חזקות ולוג: חוקים לפני מחשבון',
    },
    body: {
      en: `**Exponents/logs habit.** Rewrite with exponent/log laws first ($a^{m+n}$, $\\log(ab)$, change of base when needed).
Check domain for logs ($>0$). Prefer exact simplified form before decimals.`,
      he: `**הרגל חזקות/לוג.** שכתבו בחוקי חזקה/לוג תחילה ($a^{m+n}$, $\\log(ab)$, החלפת בסיס כשצריך).
בדקו תחום ללוג ($>0$). העדיפו צורה מדויקת מפושטת לפני עשרוניים.`,
    },
  },
  combinatorics: {
    prefixes: ['combinatorics'],
    marker: 'COMBO_DEPTH',
    title: {
      en: 'Combinatorics craft: order vs no-order',
      he: 'מלאכת קומבינטוריקה: סדר מול בלי סדר',
    },
    body: {
      en: `**Combinatorics habit.** Decide first: does order matter (permutations) or not (combinations)?
Write the counting story in one sentence, then the formula. Check with a tiny numeric case.`,
      he: `**הרגל קומבינטוריקה.** החליטו תחילה: האם הסדר משנה (תמורות) או לא (צירופים)?
כתבו את סיפור הספירה במשפט אחד, ואז את הנוסחה. בדקו במקרה מספרי קטן.`,
    },
  },
  stats: {
    prefixes: [
      'descriptive_stats',
      'statistics_',
      'sample_space',
      'basic_statistics',
      'linear_regression',
      'normal_distribution',
    ],
    marker: 'STATS_DEPTH',
    title: {
      en: 'Stats craft: define the variable, then summarize',
      he: 'מלאכת סטטיסטיקה: הגדירו משתנה, אחר כך סכמו',
    },
    body: {
      en: `**Stats habit.** Name the variable and units, choose the right summary (mean/median/spread) or probability model, then compute.
For sample spaces, list outcomes before assigning probabilities.`,
      he: `**הרגל סטטיסטיקה.** ציינו משתנה ויחידות, בחרו סיכום מתאים (ממוצע/חציון/פיזור) או מודל הסתברות, ואז חשבו.
למרחבי מדגם — רשמו תוצאות לפני שיוך הסתברויות.`,
    },
  },
  limits: {
    prefixes: ['limits'],
    marker: 'LIMITS_DEPTH',
    title: {
      en: 'Limits craft: algebra first, then meaning',
      he: 'מלאכת גבולות: אלגברה תחילה, אחר כך משמעות',
    },
    body: {
      en: `**Limits habit (MoE).** Simplify algebraically (factor, conjugate, dominant terms) before claiming a limit value.
Interpret one-sided vs two-sided when the sketch suggests a jump.
University track may use formal definitions — MoE tracks stay computational + graphical.`,
      he: `**הרגל גבולות (תוכנית).** פשטו אלגברית (פירוק, צמוד, איברים דומיננטיים) לפני טענת ערך גבול.
פרשו חד-צדדי מול דו-צדדי כשהסקיצה מרמזת על קפיצה.
מסלול אוניברסיטה יכול להשתמש בהגדרות פורמליות — מסלולי התוכנית נשארים חישוביים + גרפיים.`,
    },
  },
  function_analysis: {
    prefixes: ['function_analysis_', 'function_transformations', 'function_basics_uni', 'function_investigation_'],
    marker: 'FN_ANALYSIS_DEPTH',
    title: {
      en: 'Function analysis craft: transformations then investigation',
      he: 'מלאכת חקירת פונקציות: טרנספורמציות ואז חקירה',
    },
    body: {
      en: `**Function analysis habit.** Apply transformations ($f(x-h)+k$, stretch) on a base graph first when possible.
Then run domain → intercepts → extrema cues → asymptotes. Sketch before claiming completeness.`,
      he: `**הרגל חקירת פונקציות.** יישמו טרנספורמציות ($f(x-h)+k$, מתיחה) על גרף בסיס תחילה כשאפשר.
ואז הריצו תחום → חיתוכים → רמזי קיצון → אסימפטוטות. סקצו לפני טענת שלמות.`,
    },
  },
  uni_bridge: {
    prefixes: [
      'derivatives_intro',
      'integrals_intro',
      'la_vectors',
      'mean_value_theorem',
      'linear_systems_gaussian',
      'linear_transformations_',
      'linear_programming',
    ],
    marker: 'UNI_BRIDGE_DEPTH',
    title: {
      en: 'University bridge craft: definitions, then computation',
      he: 'מלאכת גשר אוניברסיטאי: הגדרות, אחר כך חישוב',
    },
    body: {
      en: `**University bridge habit.** State the definition or theorem hypotheses first, then compute.
Prefer precise quantifiers and domain statements. Course-exam pacing — no school-questionnaire framing.`,
      he: `**הרגל גשר אוניברסיטאי.** ציינו תחילה הגדרה או הנחות משפט, ואז חשבו.
העדיפו כמתים מדויקים וניסוחי תחום. קצב מבחן קורס — בלי מסגור שאלון בית-ספר.`,
    },
  },
};

function matchesFamily(fileBase, prefixes) {
  return prefixes.some(
    (p) => fileBase === p.replace(/_$/, '') || fileBase.startsWith(p),
  );
}

function deepenFile(fileBase, famKey, fam) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const marker = `${fam.marker}_${famKey.toUpperCase()}`;
  lesson.sections = lesson.sections || [];

  if (lesson.sections.some((s) => (s.body_en_md || '').includes(fam.marker))) {
    // already has family depth
  } else {
    const insert = {
      kind: 'theory',
      title_en: fam.title.en,
      title_he: fam.title.he,
      body_en_md: `<!-- ${marker} -->\n${fam.body.en}`,
      body_he_md: fam.body.he,
    };
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
    else lesson.sections.push(insert);
  }

  const qid = `${fileBase}-moe-remainder-depth`;
  lesson.questions = lesson.questions || [];
  if (!lesson.questions.some((q) => q.id === qid)) {
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: 'medium',
      facets: [],
      stem_en: `Track drill for this lesson: apply the ${famKey.replace(/_/g, ' ')} habit — diagram or rewrite first, then compute the core skill with labeled steps and a quick check.`,
      stem_he: `תרגיל מסלול לשיעור זה: יישמו את הרגל ${famKey} — דיאגרמה או שכתוב תחילה, ואז חשבו את המיומנות המרכזית עם שלבים מסומנים ובדיקה קצרה.`,
      explanation_en:
        '**Worked path.** Follow the family habit in the track-depth section: set up (diagram, laws, definitions), execute algebra or geometry with labels, then verify (units, substitution, tiny numeric case, or sketch consistency). Keep method marks visible.',
      explanation_he:
        '**דרך פתרון.** עקבו אחרי הרגל המשפחה בסעיף העומק: הכינו (דיאגרמה, חוקים, הגדרות), בצעו אלגברה או גאומטריה עם תוויות, ואמתו (יחידות, הצבה, מקרה מספרי קטן, או עקביות סקיצה). השאירו ניקוד שיטה גלוי.',
      correct_answer: 'see moe-remainder track-depth section',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  if (lesson.summary_en && !lesson.summary_en.includes('moe-remainder depth')) {
    lesson.summary_en = `${lesson.summary_en} Taught with moe-remainder depth habits (${famKey}).`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

const files = fs
  .readdirSync(DIR)
  .filter((f) => f.endsWith('.json'))
  .map((f) => f.replace(/\.json$/, ''));

let n = 0;
for (const fileBase of files) {
  for (const [famKey, fam] of Object.entries(FAMILIES)) {
    if (!matchesFamily(fileBase, fam.prefixes)) continue;
    if (deepenFile(fileBase, famKey, fam)) {
      console.log('deepened', fileBase, '←', famKey);
      n++;
    }
    break;
  }
}
console.log('deepened files', n);
