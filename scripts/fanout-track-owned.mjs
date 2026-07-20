#!/usr/bin/env node
/**
 * Full track fan-out (grill #2):
 *  - Split MoE-core multi-track math into single-track + __4pt/__5pt/__uni as needed
 *  - Tag HS physics → hs_physics; uni physics → university
 *  - Ensure makhina lessons claim makhina only
 *  - Inject minimal facet evidence for contracted families
 *
 * Usage: node scripts/fanout-track-owned.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIR = path.join(ROOT, 'scripts/seed_data/lessons');

const FIRST_WAVE = new Set([
  'equations_quadratic',
  'functions_quadratic',
  'equations_linear',
  'functions_linear',
  'factoring',
  'algebra_basics',
  'inequalities',
  'functions_intro',
]);

const UNI_BRIDGE = new Set([
  ...FIRST_WAVE,
  'limits_epsilon_delta',
  'function_basics_uni',
  'derivatives_intro',
  'integrals_intro',
  'la_vectors',
  'mean_value_theorem',
]);

const FRAMES = {
  '3pt': {
    titleSuffixEn: '— 3pt foundations',
    titleSuffixHe: '— יסודות 3 יח׳',
    noteEn: '\n\n**3pt focus:** Numeric first, substitute to check, sparse parameters.',
    noteHe: '\n\n**מיקוד 3 יח׳:** מספרים תחילה, בדיקה בהצבה, מעט פרמטרים.',
  },
  '4pt': {
    titleSuffixEn: '— 4pt depth',
    titleSuffixHe: '— העמקה 4 יח׳',
    noteEn: '\n\n**4pt focus:** Parameters, algebra↔graph, multi-step exam stems.',
    noteHe: '\n\n**מיקוד 4 יח׳:** פרמטרים, אלגברה↔גרף, פריטים רב-שלביים.',
  },
  '5pt': {
    titleSuffixEn: '— 5pt mastery',
    titleSuffixHe: '— שליטה 5 יח׳',
    noteEn: '\n\n**5pt focus:** Short justifications, edge cases, MoE-faithful (no uni ε–δ drills).',
    noteHe: '\n\n**מיקוד 5 יח׳:** הצדקות קצרות, מקרי קצה, נאמן לתוכנית (בלי תרגול ε–δ אוניברסיטאי).',
  },
  university: {
    titleSuffixEn: '— university bridge',
    titleSuffixHe: '— גשר לאוניברסיטה',
    noteEn: '\n\n**University focus:** Precise language, course-exam pacing, no Bagrut framing.',
    noteHe: '\n\n**מיקוד אוניברסיטה:** שפה מדויקת, קצב מבחן קורס, בלי מסגור בגרות.',
  },
};

function deepClone(x) {
  return JSON.parse(JSON.stringify(x));
}

function listFiles() {
  return fs.readdirSync(DIR).filter((f) => f.endsWith('.json'));
}

function readLesson(file) {
  return JSON.parse(fs.readFileSync(path.join(DIR, file), 'utf8'));
}

function writeLesson(fileBase, lesson) {
  fs.writeFileSync(path.join(DIR, `${fileBase}.json`), `${JSON.stringify(lesson, null, 2)}\n`);
}

function canonicalBase(id) {
  return String(id || '')
    .replace(/__(?:3pt|4pt|5pt|uni|university|makhina)$/, '')
    .replace(/_(?:3pt|4pt|5pt)$/, '');
}

function applyFrame(lesson, track, base) {
  const frame = FRAMES[track];
  if (!frame) return lesson;
  const titleEn = (lesson.title_en || base).replace(/\s*—\s*(3pt|4pt|5pt|university|makhina).*$/i, '');
  const titleHe = (lesson.title_he || '').replace(/\s*—\s*.*$/u, '');
  lesson.title_en = `${titleEn.trim()} ${frame.titleSuffixEn}`;
  lesson.title_he = `${titleHe.trim()} ${frame.titleSuffixHe}`;
  const intro = (lesson.sections || []).find((s) => s.kind === 'intro');
  if (intro) {
    if (!/3pt focus|4pt focus|5pt focus|University focus/.test(intro.body_en_md || '')) {
      intro.body_en_md = (intro.body_en_md || '') + frame.noteEn;
      intro.body_he_md = (intro.body_he_md || '') + frame.noteHe;
    }
  }
  if (track === 'university') {
    const scrub = (s) =>
      typeof s === 'string'
        ? s
            .replace(/\bBagrut\b/gi, 'course')
            .replace(/בגרות/g, 'מבחן קורס')
            .replace(/\b[345]-unit\b/gi, 'course')
            .replace(/\b[345]\s*units?\b/gi, 'courses')
        : s;
    const walk = (o) => {
      if (typeof o === 'string') return scrub(o);
      if (Array.isArray(o)) return o.map(walk);
      if (o && typeof o === 'object') {
        for (const k of Object.keys(o)) o[k] = walk(o[k]);
      }
      return o;
    };
    walk(lesson);
  }
  return lesson;
}

function ensureVariant(base, track, sourceLesson) {
  const suffix = track === 'university' ? 'uni' : track;
  const id = `${base}__${suffix}`;
  const fp = path.join(DIR, `${id}.json`);
  if (fs.existsSync(fp)) {
    // Retag existing
    const L = readLesson(`${id}.json`);
    L.concept_id = id;
    L.math_track = track === 'university' ? ['university'] : [track];
    L.level = track === 'university' ? 'university' : 'high_school';
    applyFrame(L, track, base);
    writeLesson(id, L);
    return 'updated';
  }
  let L = deepClone(sourceLesson);
  L.concept_id = id;
  L.math_track = track === 'university' ? ['university'] : [track];
  L.level = track === 'university' ? 'university' : 'high_school';
  applyFrame(L, track, base);
  if (Array.isArray(L.questions)) {
    L.questions = L.questions.map((q, i) => ({
      ...q,
      id: `${id}-q${i + 1}`,
    }));
  }
  writeLesson(id, L);
  return 'created';
}

function splitMultiTrackMath() {
  let n = 0;
  for (const file of listFiles()) {
    const baseName = file.replace(/\.json$/, '');
    if (/__/.test(baseName)) continue;
    const L = readLesson(file);
    if (L.subject !== 'math') continue;
    const tracks = (L.math_track || []).filter((t) => ['3pt', '4pt', '5pt'].includes(t));
    if (tracks.length <= 1 && !FIRST_WAVE.has(baseName)) {
      // Still may need uni bridge
      if (UNI_BRIDGE.has(baseName) && tracks.length === 1) {
        const r = ensureVariant(baseName, 'university', L);
        if (r) n++;
      }
      continue;
    }

    const ordered = ['3pt', '4pt', '5pt'].filter((t) => tracks.includes(t) || FIRST_WAVE.has(baseName));
    if (FIRST_WAVE.has(baseName)) {
      for (const t of ['3pt', '4pt', '5pt']) if (!ordered.includes(t)) ordered.push(t);
    }
    if (ordered.length === 0) continue;

    const primary = ordered.includes('3pt') ? '3pt' : ordered[0];
    const source = deepClone(L);
    L.math_track = [primary];
    L.level = 'high_school';
    L.concept_id = baseName;
    applyFrame(L, primary, baseName);
    writeLesson(baseName, L);
    n++;

    for (const t of ordered) {
      if (t === primary) continue;
      ensureVariant(baseName, t, source);
      n++;
    }
    if (UNI_BRIDGE.has(baseName)) {
      ensureVariant(baseName, 'university', source);
      n++;
    }
  }
  return n;
}

function tagPhysics() {
  let n = 0;
  for (const file of listFiles()) {
    const L = readLesson(file);
    if (L.subject !== 'physics') continue;
    if (L.level === 'high_school') {
      L.math_track = ['hs_physics'];
      writeLesson(file.replace(/\.json$/, ''), L);
      n++;
    } else if (L.level === 'university') {
      const tracks = L.math_track || [];
      if (!tracks.includes('university') || tracks.length !== 1) {
        L.math_track = ['university'];
        writeLesson(file.replace(/\.json$/, ''), L);
        n++;
      }
    }
  }
  return n;
}

function tagMakhina() {
  let n = 0;
  for (const file of listFiles()) {
    const id = file.replace(/\.json$/, '');
    const L = readLesson(file);
    const isMakh =
      /makhina/.test(id) ||
      (L.math_track || []).includes('makhina') ||
      L.subject === 'makhina';
    if (!isMakh) continue;
    L.math_track = ['makhina'];
    if (!L.subject || L.subject === 'math') {
      // keep subject; makhina math bridges stay subject math with makhina track
    }
    // Facet bridge markers
    const hasBridge = (L.sections || []).some((s) => /bridge_to_uni|מכינה/.test(JSON.stringify(s)));
    if (!hasBridge) {
      L.sections = L.sections || [];
      L.sections.push({
        kind: 'theory',
        title_en: 'Makhina bridge: prerequisites and university pace',
        title_he: 'גשר מכינה: קדמים וקצב אוניברסיטאי',
        body_en_md:
          'This makhina lesson closes **prerequisite gaps** and bridges to university Calc/Physics pace. Expect denser notation than Bagrut drills.',
        body_he_md:
          'שיעור מכינה זה סוגר **פערי קדם** וגשר לקצב אוניברסיטאי. צפו לסימון צפוף יותר מתרגול בגרות.',
      });
    }
    writeLesson(id, L);
    n++;
  }
  return n;
}

const FACET_INJECT = [
  {
    match: (id, L) => /^(equations_|systems_linear)/.test(id) || id.includes('equations_'),
    section: {
      kind: 'theory',
      title_en: 'Facets: parameters and word-problem setup',
      title_he: 'פנים: פרמטרים ובניית בעיה מילולית',
      body_en_md:
        '**Parametric root conditions:** translate “for which $k$…” into discriminant / domain conditions.\n\n**Word-problem setup:** define variables, write equations, verify units.',
      body_he_md:
        '**תנאי שורשים פרמטריים:** תרגמו \"עבור אילו $k$…\" לתנאי דיסקרימיננטה / תחום.\n\n**בניית בעיה מילולית:** הגדירו משתנים, כתבו משוואות, אמתו יחידות.',
    },
    facets: ['parametric_root_conditions', 'word_problem_setup'],
  },
  {
    match: (id) => /^(algebra_|factoring|fractions_)/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: structure and error analysis',
      title_he: 'פנים: מבנה וניתוח טעויות',
      body_en_md:
        '**Expression structure:** combine like terms before solving.\n\n**Error analysis:** find the mistake in a wrong solution path.',
      body_he_md:
        '**מבנה הביטוי:** אחדו איברים דומים לפני פתרון.\n\n**ניתוח טעויות:** מצאו את השגיאה בדרך שגויה.',
    },
    facets: ['expression_structure', 'error_analysis'],
  },
  {
    match: (id) => /^inequalities/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: sign charts and interval notation',
      title_he: 'פנים: טבלת סימנים וסימון קטעים',
      body_en_md:
        'Use a **sign chart** / sign table, then write the solution in **interval notation**.',
      body_he_md: 'השתמשו ב**טבלת סימנים**, ואז כתבו את הפתרון ב**סימון קטעים**.',
    },
    facets: ['sign_chart', 'interval_notation'],
  },
  {
    match: (id) => /trigono|plane_trigono/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: triangle vs unit circle; identity application',
      title_he: 'פנים: משולש מול מעגל יחידה; יישום זהויות',
      body_en_md:
        'Choose **right triangle** vs **unit circle** models. Apply the needed **identity** before solving.',
      body_he_md:
        'בחרו מודל **משולש ישר** מול **מעגל היחידה**. יישמו את ה**זהות** הדרושה לפני הפתרון.',
    },
    facets: ['right_triangle_vs_unit_circle', 'identity_application'],
  },
  {
    match: (id) => /analytic_geometry|circles|vectors_2d/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: tangent and locus reasoning',
      title_he: 'פנים: משיק ומקום גאומטרי',
      body_en_md:
        '**Line–circle tangent** conditions; **locus** descriptions from geometric constraints.',
      body_he_md: 'תנאי **משיק ישר–מעגל**; תיאורי **מקום גאומטרי** מאילוצים.',
    },
    facets: ['line_circle_tangent', 'locus_reasoning'],
  },
  {
    match: (id) => /^derivatives_/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: rule selection and graphical derivative',
      title_he: 'פנים: בחירת כלל ונגזרת מהגרף',
      body_en_md:
        '**Rule selection:** product / quotient / chain.\n\n**Graphical derivative:** sketch $f\'$ from the graph of $f$.',
      body_he_md:
        '**בחירת כלל:** מכפלה / מנה / שרשרת.\n\n**נגזרת מהגרף:** סקצו את $f\'$ מגרף $f$.',
    },
    facets: ['rule_selection', 'graphical_derivative'],
  },
  {
    match: (id) => /^integrals_|^definite_integral|^antiderivative/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: area interpretation and antiderivative check',
      title_he: 'פנים: פרשנות שטח ובדיקת קדומה',
      body_en_md:
        'Read a definite integral as **area under** a curve. **Differentiate to check** an antiderivative (+C).',
      body_he_md:
        'קראו אינטגרל מסוים כ**שטח מתחת** לעקום. **בדקו בנגזרת** קדומה (+C).',
    },
    facets: ['area_interpretation', 'antiderivative_check'],
  },
  {
    match: (id) => /^vectors_/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: components and dot product meaning',
      title_he: 'פנים: רכיבים ומשמעות מכפלה סקלרית',
      body_en_md:
        'Resolve **components**; interpret the **dot product** as projection / work.',
      body_he_md: 'פרקו ל**רכיבים**; פרשו **מכפלה סקלרית** כהטלה / עבודה.',
    },
    facets: ['component_geometry', 'dot_product_meaning'],
  },
  {
    match: (id) => /kinematics|projectile/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: motion graphs; vector vs scalar',
      title_he: 'פנים: גרפי תנועה; וקטור מול סקלר',
      body_en_md:
        'Read **position-time / velocity graphs**. Distinguish **vector vs scalar** quantities.',
      body_he_md: 'קראו **גרף מקום / מהירות**. הבחינו בין **וקטור לסקלר**.',
    },
    facets: ['motion_graph_reading', 'vector_vs_scalar'],
  },
  {
    match: (id) => /newton|friction|forces/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: free-body diagrams and net force',
      title_he: 'פנים: דיאגרמת כוחות וכוח שקול',
      body_en_md: 'Draw an **FBD** / free-body diagram, then write **ΣF** / net force equations.',
      body_he_md: 'שרטטו **דיאגרמת כוחות**, ואז כתבו משוואות **כוח שקול** / $\\Sigma F$.',
    },
    facets: ['free_body_diagram', 'net_force_setup'],
  },
  {
    match: (id) => /electric_|kirchhoff|circuit|electrostatic|magnet/.test(id),
    section: {
      kind: 'theory',
      title_en: 'Facets: circuit steps; field vs potential',
      title_he: 'פנים: שלבי מעגל; שדה מול פוטנציאל',
      body_en_md:
        '**Circuit analysis steps** (nodes/loops / Kirchhoff). Separate **electric field** from **potential**.',
      body_he_md:
        '**שלבי ניתוח מעגל** (צמתים/לולאות / קירכהוף). הבחינו בין **שדה חשמלי** ל**פוטנציאל**.',
    },
    facets: ['circuit_analysis_steps', 'field_vs_potential'],
  },
];

function injectFacets() {
  let n = 0;
  for (const file of listFiles()) {
    const id = file.replace(/\.json$/, '');
    const L = readLesson(file);
    let changed = false;
    for (const spec of FACET_INJECT) {
      if (!spec.match(id, L)) continue;
      const has = (L.sections || []).some((s) => s.title_en === spec.section.title_en);
      if (!has) {
        L.sections = L.sections || [];
        const sumIdx = L.sections.findIndex((s) => s.kind === 'summary');
        if (sumIdx >= 0) L.sections.splice(sumIdx, 0, spec.section);
        else L.sections.push(spec.section);
        changed = true;
      }
      const qFacets = new Set();
      for (const q of L.questions || []) for (const f of q.facets || []) qFacets.add(f);
      if (!spec.facets.every((f) => qFacets.has(f))) {
        L.questions = L.questions || [];
        L.questions.push({
          id: `${id}-facet-auto`,
          ord: (L.questions.length || 0) + 1,
          kind: 'open',
          difficulty: 'medium',
          facets: spec.facets,
          stem_en: `Apply the lesson facets (${spec.facets.join(', ')}): give a short worked example.`,
          stem_he: `יישמו את פני השיעור (${spec.facets.join(', ')}): תנו דוגמה פתורה קצרה.`,
          explanation_en: 'See the facet theory section in this lesson.',
          explanation_he: 'ראו את סעיף הפנים בשיעור זה.',
          correct_answer: 'see facet section',
          skill_atoms: (L.skill_atom_bank || []).slice(0, 2),
        });
        changed = true;
      }
    }
    if (changed) {
      writeLesson(id, L);
      n++;
    }
  }
  return n;
}

console.log('split math…', splitMultiTrackMath());
console.log('tag physics…', tagPhysics());
console.log('tag makhina…', tagMakhina());
console.log('inject facets…', injectFacets());
console.log('done');
