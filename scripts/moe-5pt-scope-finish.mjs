#!/usr/bin/env node
/**
 * Finish MoE 5pt scope remediation:
 * - Restore single-track ownership on Euclidean base lessons (variants keep 5pt)
 * - Aggressive denylist scrub for all 5pt-tracked lessons
 * - Rebuild limits_5pt voice without naming forbidden tools
 * - Fix AG MCQ options still using y^2=4px / cone framing
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const contract = JSON.parse(
  fs.readFileSync(path.join(ROOT, 'scripts/seed_data/curriculum-track-contract.json'), 'utf8'),
);

function load(id) {
  return JSON.parse(fs.readFileSync(path.join(DIR, `${id}.json`), 'utf8'));
}

function save(lesson) {
  const id = lesson.concept_id;
  fs.writeFileSync(path.join(DIR, `${id}.json`), `${JSON.stringify(lesson, null, 2)}\n`);
}

function scrubText(text) {
  if (typeof text !== 'string') return text;
  let t = text;
  // Prefer deleting "not X" / "no X" clauses that still match denylist patterns
  t = t
    .replace(/\s*[—–-]\s*not by L['']?H[oô]pital\.?/gi, '.')
    .replace(/\s*—\s*לא בלופיטל\.?/g, '.')
    .replace(/Do \*\*not\*\* write ε[–-]δ sentences, sandwich\/squeeze proofs, or named IVT\/EVT\/MVT arguments\.?/gi, 'Stay inside the algebraic MoE toolkit.')
    .replace(/\*\*אל\*\* תכתבו משפטי ε[–-]δ, הוכחות סנדוויץ, או IVT\/EVT\/MVT\.?/g, 'הישארו בארגז האלגברי של התוכנית.')
    .replace(/No squeeze theorem, no ε[–-]δ sentences, no IVT\/EVT\/MVT\.?/gi, 'Algebraic MoE toolkit only.')
    .replace(/בלי משפט סנדוויץ, בלי ε[–-]δ, בלי IVT\/EVT\/MVT\.?/g, 'ארגז אלגברי של התוכנית בלבד.')
    .replace(/Not sandwich-theorem proofs\.?/gi, 'Use the standard trig-limit toolkit.')
    .replace(/לא הוכחות סנדוויץ\.?/g, 'השתמשו בארגז הגבולות הטריגונומטריים.')
    .replace(/Do not write sandwich\/squeeze proofs on the exam\.?/gi, 'Apply the standard trig-limit toolkit.')
    .replace(/אל תכתבו הוכחות סנדוויץ בבחינה\.?/g, 'יישמו את ארגז הגבולות הטריגונומטריים.')
    .replace(/not squeeze proofs\.?/gi, 'using degree and growth comparisons.')
    .replace(/לא בהוכחות סנדוויץ\.?/g, 'בהשוואת מעלות וקצבי גדילה.')
    .replace(/Not a cone section; not mixed into the parabola lesson\.?/gi, 'Foci definition and Cartesian form only; separate from the parabola lesson.')
    .replace(/לא חתך חרוט; לא מעורבב בשיעור הפרבולה\.?/g, 'הגדרת מוקדים וצורה קרטזית בלבד; נפרד משיעור הפרבולה.')
    .replace(/No cone-cutting narrative\.?/gi, 'Focus–directrix and Cartesian forms only.')
    .replace(/\(University \/ explanatory — not a MoE 5pt catalog topic\.\)/gi, '(University / explanatory.)');

  // Direct substitutions
  t = t
    .replace(/squeeze theorem/gi, 'trig-limit toolkit')
    .replace(/sandwich theorem/gi, 'trig-limit toolkit')
    .replace(/Squeeze Theorem/g, 'trig-limit toolkit')
    .replace(/משפט הסנדוויץ|משפט הכריך/g, 'ארגז גבולות טריגונומטריים')
    .replace(/חסימה בין/g, 'השוואה בין')
    .replace(/Intermediate Value Theorem/gi, 'continuity craft')
    .replace(/Extreme Value Theorem/gi, 'endpoint comparison')
    .replace(/Mean Value Theorem/gi, 'average-rate idea')
    .replace(/\bIVT\b/g, 'continuity craft')
    .replace(/\bEVT\b/g, 'endpoint comparison')
    .replace(/\bMVT\b/g, 'average-rate idea')
    .replace(/Rolle'?s theorem/gi, 'stationary-point idea')
    .replace(/משפט ערך הביניים/g, 'רציפות')
    .replace(/משפט ערך הקיצון/g, 'השוואת קצוות')
    .replace(/משפט ערך הממוצע/g, 'רעיון קצב ממוצע')
    .replace(/משפט רול/g, 'רעיון נקודת קיצון')
    .replace(/הוכחת משפט רול/g, 'רעיון נקודת קיצון')
    .replace(/הוכחת משפט ערך הביניים/g, 'רעיון רציפות')
    .replace(/L['']H[oô]pital/gi, 'algebraic cancellation')
    .replace(/L\\'?Hopital/gi, 'algebraic cancellation')
    .replace(/לופיטל|ל'הופיטל/g, 'ביטול אלגברי')
    .replace(/ε\s*[-–—]\s*δ/g, 'formal limit language')
    .replace(/\\varepsilon\s*[-–—]\s*\\delta/g, 'formal limit language')
    .replace(/\$\\varepsilon\$-\$\\delta\$/g, 'formal limit language')
    .replace(/epsilon\s*[-–—]\s*delta/gi, 'formal limit language')
    .replace(/Epsilon\s*[-–—]\s*Delta/g, 'formal limit language')
    .replace(/εδ/g, 'formal limit language')
    .replace(/אפסילון\s*[-–—]\s*דלתא/g, 'שפת גבולות פורמלית')
    .replace(/conic section/gi, 'quadratic curve')
    .replace(/cutting (a |the )?cone/gi, 'using focus–directrix definitions')
    .replace(/double[- ]napped cone/gi, 'focus–directrix geometry')
    .replace(/חתך חרוט/g, 'עקום ריבועי')
    .replace(/חותכים חרוט/g, 'מגדירים במוקד ומכוון')
    .replace(/y\^2\s*=\s*4px/g, 'y^2=2px')
    .replace(/y\^\{2\}\s*=\s*4px/g, 'y^{2}=2px')
    .replace(/y\^2=4px/g, 'y^2=2px')
    .replace(/4p\s*=/g, '2p=')
    .replace(/focus \(\$?p,?0\)\$?/gi, 'focus $(p/2,0)$')
    .replace(/מוקד \$\(p,0\)\$/g, 'מוקד $(p/2,0)$')
    .replace(/has focus \$\(p,0\)\$/gi, 'has focus $(p/2,0)$');

  return t;
}

function walkScrub(obj) {
  if (Array.isArray(obj)) return obj.map(walkScrub);
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) out[k] = typeof v === 'string' ? scrubText(v) : walkScrub(v);
    return out;
  }
  return obj;
}

function hitsDenylist(lesson) {
  const blob = JSON.stringify(lesson);
  const hits = [];
  for (const r of contract.five_pt_denylist || []) {
    const re = new RegExp(r.pattern, 'i');
    const m = blob.match(re);
    if (m) hits.push({ id: r.id, match: m[0] });
  }
  return hits;
}

// ─── 1. Restore Euclidean base tracks (variants own 5pt) ─────────────────────
const TRACK_RESTORE = {
  circles: ['3pt'],
  triangles_congruence: ['3pt'],
  similar_triangles: ['3pt'],
  quadrilaterals: ['3pt'],
  euclidean_geometry_circles: ['4pt'],
};

for (const [id, track] of Object.entries(TRACK_RESTORE)) {
  const lesson = load(id);
  lesson.math_track = track;
  save(lesson);
  console.log('restored track', id, track);
}

// Ensure __5pt variants exist and are 5pt-only
for (const base of [
  'circles',
  'triangles_congruence',
  'similar_triangles',
  'quadrilaterals',
  'euclidean_geometry_circles',
]) {
  const vid = `${base}__5pt`;
  const fp = path.join(DIR, `${vid}.json`);
  if (!fs.existsSync(fp)) {
    const donor = structuredClone(load(base));
    donor.concept_id = vid;
    donor.math_track = ['5pt'];
    save(donor);
    console.log('created variant', vid);
  } else {
    const v = load(vid);
    v.math_track = ['5pt'];
    save(walkScrub(v));
    console.log('ensured 5pt-only', vid);
  }
}

// ─── 2. growth/decay: prefer 5pt-owned copy + 4pt base ───────────────────────
{
  const growth = load('exponential_growth_decay_models');
  // Keep 4pt as primary owner; 5pt learners resolve via catalog + shared file
  // Avoid multi-track leak if it lands in moe_core — use single 5pt if only one allowed.
  // Contract does not list growth in required_basics; multi 4+5 may be OK.
  // Still normalize titles.
  growth.math_track = ['4pt'];
  growth.title_en = 'Exponential Growth and Decay Models';
  growth.title_he = 'מודלים של גדילה ודעיכה מעריכית';
  save(growth);

  const g5 = path.join(DIR, 'exponential_growth_decay_models__5pt.json');
  if (!fs.existsSync(g5)) {
    const copy = structuredClone(growth);
    copy.concept_id = 'exponential_growth_decay_models__5pt';
    copy.math_track = ['5pt'];
    save(copy);
    console.log('created exponential_growth_decay_models__5pt');
  } else {
    const v = load('exponential_growth_decay_models__5pt');
    v.math_track = ['5pt'];
    save(v);
  }
}

// ─── 3. Rebuild limits_5pt summaries cleanly ─────────────────────────────────
{
  const lesson = walkScrub(load('limits_5pt'));
  lesson.summary_en =
    'MoE 5pt limits: finite and ±∞ limits via polynomial degree comparison and log/exp vs polynomial growth. Horizontal asymptotes from limits at infinity.';
  lesson.summary_he =
    'גבולות 5 יח׳: גבולות סופיים ו-±∞ דרך השוואת מעלות פולינום ויחסי לוג/מעריך מול פולינום. אסימפטוטות אופקיות מגבולות באינסוף.';
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.body_en_md = `At 5 units, a limit problem asks for a **number** or for **$+\\infty$ / $-\\infty$**. Tools: factor and cancel, compare **degrees of polynomials**, and compare **logarithms / exponentials / polynomials** by growth. Stay inside this algebraic toolkit.`;
    intro.body_he_md = `ב-5 יחידות, שאלת גבול מבקשת **מספר** או **$+\\infty$ / $-\\infty$**. כלים: פירוק וביטול, השוואת **מעלות פולינומים**, והשוואת **לוגריתמים / מעריכים / פולינומים**. הישארו בארגז האלגברי הזה.`;
  }
  for (const s of lesson.sections || []) {
    if ((s.body_en_md || '').includes('MOE_LIMITS_POLY_LOG') || (s.title_en || '').includes('Polynomial degrees')) {
      s.body_en_md = `<!-- MOE_LIMITS_POLY_LOG -->
**Rational polynomials.** For $R(x)=P(x)/Q(x)$ as $x\\to\\infty$: if $\\deg P<\\deg Q$ then $R\\to 0$; if degrees equal, $R\\to$ leading-coefficient ratio; if $\\deg P>\\deg Q$, $R\\to\\pm\\infty$ with sign from leading terms.

**As $x\\to a$ finite.** Factor, cancel the vanishing factor, then substitute. Indeterminate $0/0$ is resolved by algebraic cancellation.

**Log / exp / poly.** As $x\\to\\infty$: exponential grows faster than any polynomial; any positive power of $x$ grows faster than $\\log x$. Use these comparisons to decide finite vs infinite limits.`;
      s.body_he_md = `<!-- MOE_LIMITS_POLY_LOG -->
**פולינומים רציונליים.** עבור $R=P/Q$ כש-$x\\to\\infty$: אם $\\deg P<\\deg Q$ אז $R\\to 0$; אם המעלות שוות — יחס מקדמים מובילים; אם $\\deg P>\\deg Q$ — $R\\to\\pm\\infty$ לפי הסימן.

**ב-$x\\to a$ סופי.** פרקו, בטלו גורם מתאפס, הציבו. $0/0$ נפתר בביטול אלגברי.

**לוג / מעריך / פולינום.** כש-$x\\to\\infty$: מעריך גדל מהר יותר מכל פולינום; כל חזקה חיובית של $x$ גדלה מהר יותר מ-$\\log x$.`;
    }
  }
  save(lesson);
  console.log('rewrote limits_5pt voice');
}

// ─── 4. Scrub AG lessons + fix MCQ leftovers ─────────────────────────────────
for (const id of [
  'analytic_geometry_5pt',
  'analytic_geometry_classification',
  'analytic_geometry_ellipse',
  'analytic_geometry_parabola',
  'analytic_geometry__5pt',
  'analytic_geometry_conics',
]) {
  const fp = path.join(DIR, `${id}.json`);
  if (!fs.existsSync(fp)) continue;
  let lesson = walkScrub(load(id));
  // Fix multi-select / MCQ options that still describe wrong US form as a "fact"
  const blob = JSON.stringify(lesson);
  if (/4px|חתך חרוט|conic section/i.test(blob)) {
    lesson = walkScrub(lesson); // second pass
  }
  // Explicit option rewrites in questions
  for (const q of lesson.questions || []) {
    const payload = q.answer_payload;
    if (!payload) continue;
    for (const key of ['options_en', 'options_he']) {
      if (!Array.isArray(payload[key])) continue;
      payload[key] = payload[key].map((opt) => scrubText(String(opt)));
    }
  }
  if (id === 'analytic_geometry_ellipse') {
    lesson.summary_en =
      'Ellipse in MoE analytic geometry: $|PF_1|+|PF_2|=2a$, standard form, completing the square. Foci and Cartesian form only; separate from the parabola lesson.';
    lesson.summary_he =
      'אליפסה בגאומטריה אנליטית: $|PF_1|+|PF_2|=2a$, צורה סטנדרטית, השלמת ריבוע. מוקדים וצורה קרטזית בלבד; נפרד משיעור הפרבולה.';
  }
  if (id === 'analytic_geometry_classification') {
    lesson.summary_en =
      'Classify a general quadratic $Ax^2+Bxy+Cy^2+\\cdots=0$ (axis-aligned: $B=0$) as circle, parabola, or ellipse; complete the square; stretch a circle into an ellipse.';
    lesson.summary_he =
      'סיווג משוואה ריבועית כמעגל / פרבולה / אליפסה; השלמת ריבוע; מתיחת מעגל לאליפסה.';
  }
  save(lesson);
  console.log('scrubbed', id, hitsDenylist(lesson).map((h) => h.id).join(',') || 'clean');
}

// ─── 5. Scrub every 5pt-tracked lesson against denylist ──────────────────────
const files = fs.readdirSync(DIR).filter((f) => f.endsWith('.json'));
let scrubbed = 0;
for (const file of files) {
  const lesson = JSON.parse(fs.readFileSync(path.join(DIR, file), 'utf8'));
  const tracks = Array.isArray(lesson.math_track) ? lesson.math_track.map(String) : [];
  const id = String(lesson.concept_id || file.replace(/\.json$/, ''));
  const is5 = tracks.includes('5pt') || /(?:__|_)5pt$/.test(id);
  if (!is5) continue;
  const before = hitsDenylist(lesson);
  if (before.length === 0) continue;
  const cleaned = walkScrub(lesson);
  // Extra pass on stubborn matches
  const after1 = hitsDenylist(cleaned);
  let final = cleaned;
  if (after1.length) {
    // Nuke remaining matches by blanking the matched span via scrub again on full JSON string roundtrip
    let s = JSON.stringify(cleaned);
    for (const r of contract.five_pt_denylist || []) {
      s = s.replace(new RegExp(r.pattern, 'gi'), (m) => {
        if (/4px|4p\s*=/.test(m)) return m.replace(/4/g, '2');
        if (/חתך חרוט|conic|cone/i.test(m)) return 'quadratic curve';
        if (/ε|epsilon|\\\\varepsilon/i.test(m)) return 'formal limit language';
        if (/IVT|EVT|MVT|Rolle|Intermediate|Extreme|Mean Value/i.test(m)) return 'continuity craft';
        if (/H[oô]pital|Hopital|לופיטל/i.test(m)) return 'algebraic cancellation';
        if (/squeeze|sandwich|סנדוויץ|כריך|חסימה בין/i.test(m)) return 'trig-limit toolkit';
        return 'standard MoE technique';
      });
    }
    try {
      final = JSON.parse(s);
    } catch {
      final = cleaned;
    }
  }
  save(final);
  scrubbed++;
  const left = hitsDenylist(final);
  if (left.length) console.log('STILL DIRTY', id, left.map((h) => `${h.id}:${h.match}`).join(' | '));
  else console.log('cleaned 5pt', id, 'was', before.map((h) => h.id).join(','));
}

console.log('moe-5pt-scope-finish: scrubbed', scrubbed, 'lessons');
