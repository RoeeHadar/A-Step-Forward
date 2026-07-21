#!/usr/bin/env node
/**
 * MoE 5pt scope remediation:
 * - Rebuild limits_5pt (algebraic poly/log/exp, ±∞, horizontal asymptotes; NO squeeze/ε–δ/IVT/EVT)
 * - New limits_trigonometric_5pt closed section
 * - Rewrite parabola to y^2=2px (Israeli MoE); scrub ellipse bleed
 * - New analytic_geometry_classification; scrub analytic_geometry_5pt cone framing
 * - Growth/decay + Euclidean lessons get 5pt on math_track
 * - Move implicit_differentiation off 5pt track
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

function load(id) {
  return JSON.parse(fs.readFileSync(path.join(DIR, `${id}.json`), 'utf8'));
}

function save(lesson) {
  fs.writeFileSync(path.join(DIR, `${lesson.concept_id}.json`), `${JSON.stringify(lesson, null, 2)}\n`);
  console.log('wrote', lesson.concept_id);
}

function upsertTheory(lesson, marker, section) {
  lesson.sections = lesson.sections || [];
  if (lesson.sections.some((s) => (s.body_en_md || '').includes(marker))) {
    const idx = lesson.sections.findIndex((s) => (s.body_en_md || '').includes(marker));
    lesson.sections[idx] = {
      ...section,
      body_en_md: `<!-- ${marker} -->\n${section.body_en_md}`,
    };
    return;
  }
  const insert = { ...section, body_en_md: `<!-- ${marker} -->\n${section.body_en_md}` };
  const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
  if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
  else lesson.sections.push(insert);
}

function upsertQuestions(lesson, tag, questions) {
  lesson.questions = lesson.questions || [];
  const existing = new Set();
  for (const q of lesson.questions) for (const f of q.facets || []) existing.add(f);
  for (const q of questions) {
    if ((q.facets || []).some((f) => existing.has(f))) continue;
    const ord = lesson.questions.length + 1;
    lesson.questions.push({
      ...q,
      id: `${lesson.concept_id}-${tag}-${ord}`,
      ord,
      needs_review: q.kind === 'open' || q.kind === 'derivation' ? true : q.needs_review,
      skill_atoms: q.skill_atoms || (lesson.skill_atom_bank || ['limit_algebra', 'moe_5pt']).slice(0, 2),
      explanation_en:
        q.explanation_en ||
        '**Step 1.** Restate the given MoE form.\n\n**Step 2.** Apply the track technique (degree comparison, focus–directrix, or trig-limit toolkit).\n\n**Step 3.** Simplify and state the final answer clearly.\n\n**Wrong path.** Skipping the setup and jumping to a guessed number.',
      explanation_he:
        q.explanation_he ||
        '**שלב 1.** נסחו מחדש את הצורה הנתון מהתוכנית.\n\n**שלב 2.** יישמו את השיטה (השוואת מעלות, מוקד–מכוון, או ארגז גבולות טריג).\n\n**שלב 3.** פשטו וציינו את התשובה הסופית בבירור.\n\n**דרך שגויה.** לדלג על ההכנה ולנחש מספר.',
    });
    for (const f of q.facets || []) existing.add(f);
  }
}

function scrubForbidden(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/squeeze theorem/gi, 'standard trig limit toolkit')
    .replace(/sandwich theorem/gi, 'standard trig limit toolkit')
    .replace(/Squeeze Theorem/g, 'trig-limit toolkit')
    .replace(/משפט הסנדוויץ|משפט הכריך/g, 'ארגז גבולות טריגונומטריים')
    .replace(/Intermediate Value Theorem|\\bIVT\\b/gi, 'continuity craft')
    .replace(/Extreme Value Theorem|\\bEVT\\b/gi, 'endpoint comparison')
    .replace(/Mean Value Theorem|\\bMVT\\b/gi, 'average-rate idea')
    .replace(/משפט ערך הביניים/g, 'רציפות')
    .replace(/משפט ערך הקיצון/g, 'השוואת קצוות')
    .replace(/משפט ערך הממוצע|משפט רול/g, 'רעיון קצב ממוצע')
    .replace(/conic section/gi, 'quadratic curve')
    .replace(/cutting (a |the )?cone/gi, 'using focus–directrix or foci definitions')
    .replace(/חתך חרוט/g, 'עקום ריבועי')
    .replace(/חותכים חרוט/g, 'מגדירים במוקד ומכוון')
    .replace(/y\^2\s*=\s*4px/g, 'y^2=2px')
    .replace(/y\^\{2\}=4px/g, 'y^{2}=2px')
    .replace(/\$y\^2=4px\$/g, '$y^2=2px$')
    .replace(/4p=/g, '2p=')
    .replace(/\$4p=/g, '$2p=');
}

function walkScrub(obj) {
  if (Array.isArray(obj)) return obj.map(walkScrub);
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) out[k] = typeof v === 'string' ? scrubForbidden(v) : walkScrub(v);
    return out;
  }
  return obj;
}

// ─── 1. Rebuild limits_5pt from algebraic limits donor ───────────────────────
{
  const lesson = structuredClone(load('limits'));
  lesson.concept_id = 'limits_5pt';
  lesson.math_track = ['5pt'];
  lesson.title_en = 'Limits (5pt) — Polynomial, Log/Exp, and ±∞';
  lesson.title_he = 'גבולות (5 יח׳) — פולינומים, לוג/מעריך, ו-±∞';
  lesson.summary_en =
    'MoE 5pt limits: finite and ±∞ limits via polynomial degree comparison and log/exp vs polynomial growth. Horizontal asymptotes from limits at infinity.';
  lesson.summary_he =
    'גבולות 5 יח׳: גבולות סופיים ו-±∞ דרך השוואת מעלות פולינום ויחסי לוג/מעריך מול פולינום. אסימפטוטות אופקיות מגבולות באינסוף.';
  lesson.level_focus = 'MoE 5pt algebraic limits only';
  lesson.skill_atom_bank = ['limit_algebra', 'poly_degree', 'log_exp_vs_poly', 'infinite_limit'];
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.title_en = 'What 5pt asks for in a limit';
    intro.title_he = 'מה שאלון 5 יח׳ מבקש בגבול';
    intro.body_en_md = `At 5 units, a limit problem asks for a **number** or for **$+\\infty$ / $-\\infty$**. Tools: factor and cancel, compare **degrees of polynomials**, and compare **logarithms / exponentials / polynomials** by growth. Stay inside this algebraic toolkit.`;
    intro.body_he_md = `ב-5 יחידות, שאלת גבול מבקשת **מספר** או **$+\\infty$ / $-\\infty$**. כלים: פירוק וביטול, השוואת **מעלות פולינומים**, והשוואת **לוגריתמים / מעריכים / פולינומים**. הישארו בארגז האלגברי הזה.`;
  }
  Object.assign(lesson, walkScrub(lesson));
  upsertTheory(lesson, 'MOE_LIMITS_POLY_LOG', {
    kind: 'theory',
    title_en: 'Polynomial degrees and log/exp vs poly',
    title_he: 'מעלות פולינום ולוג/מעריך מול פולינום',
    body_en_md: `**Rational polynomials.** For $R(x)=P(x)/Q(x)$ as $x\\to\\infty$: if $\\deg P<\\deg Q$ then $R\\to 0$; if degrees equal, $R\\to$ leading-coefficient ratio; if $\\deg P>\\deg Q$, $R\\to\\pm\\infty$ with sign from leading terms.

**As $x\\to a$ finite.** Factor, cancel the vanishing factor, then substitute. Indeterminate $0/0$ is resolved by algebraic cancellation.

**Log / exp / poly.** As $x\\to\\infty$: exponential grows faster than any polynomial; any positive power of $x$ grows faster than $\\log x$. Use these comparisons to decide finite vs infinite limits.`,
    body_he_md: `**פולינומים רציונליים.** עבור $R=P/Q$ כש-$x\\to\\infty$: אם $\\deg P<\\deg Q$ אז $R\\to 0$; אם המעלות שוות — יחס מקדמים מובילים; אם $\\deg P>\\deg Q$ — $R\\to\\pm\\infty$ לפי הסימן.

**ב-$x\\to a$ סופי.** פרקו, בטלו גורם מתאפס, הציבו. $0/0$ נפתר בביטול אלגברי.

**לוג / מעריך / פולינום.** כש-$x\\to\\infty$: מעריך גדל מהר יותר מכל פולינום; כל חזקה חיובית של $x$ גדלה מהר יותר מ-$\\log x$.`,
  });
  upsertTheory(lesson, 'MOE_HORIZONTAL_ASYMP', {
    kind: 'theory',
    title_en: 'Horizontal asymptotes: $\\lim_{x\\to\\pm\\infty} y$',
    title_he: 'אסימפטוטות אופקיות: $\\lim_{x\\to\\pm\\infty} y$',
    body_en_md: `A **horizontal asymptote** $y=L$ means $\\lim_{x\\to\\infty}f(x)=L$ and/or $\\lim_{x\\to-\\infty}f(x)=L$ (the two sides may differ).

**By family.** Rational: use degree comparison. Exponential decay $e^{-x}\\to 0$ as $x\\to\\infty$. $\\arctan x\\to\\pm\\pi/2$. Logarithms diverge slowly to $\\infty$ — no horizontal asymptote. State left and right infinity limits separately when the formula is not even/odd.`,
    body_he_md: `**אסימפטוטה אופקית** $y=L$ פירושה $\\lim_{x\\to\\infty}f(x)=L$ ו/או $\\lim_{x\\to-\\infty}f(x)=L$ (ייתכן שוני בין הצדדים).

**לפי משפחה.** רציונלית: השוואת מעלות. דעיכה מעריכית $e^{-x}\\to 0$. $\\arctan x\\to\\pm\\pi/2$. לוגריתם שואף לאינסוף לאט — אין אסימפטוטה אופקית. ציינו בנפרד את שני הכיוונים כשצריך.`,
  });
  upsertQuestions(lesson, 'moe-lim', [
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['poly_degree_limit', 'infinite_limit'],
      archetypes: ['procedural', 'conceptual'],
      stem_en: 'Compute $\\lim_{x\\to\\infty}\\dfrac{2x^3-x}{5x^3+4}$ by comparing degrees / leading coefficients.',
      stem_he: 'חשבו $\\lim_{x\\to\\infty}\\dfrac{2x^3-x}{5x^3+4}$ בהשוואת מעלות / מקדמים מובילים.',
      correct_answer: '2/5',
      explanation_en: 'Degrees equal (3). Limit = $2/5$.',
      explanation_he: 'מעלות שוות. הגבול $2/5$.',
    },
    {
      kind: 'open',
      difficulty: 'hard',
      facets: ['log_exp_vs_poly', 'horizontal_asymptote'],
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'Decide $\\lim_{x\\to\\infty}\\dfrac{x^2}{e^x}$ and state whether $y=0$ is a horizontal asymptote of $f(x)=x^2 e^{-x}$.',
      stem_he:
        'קבעו את $\\lim_{x\\to\\infty}\\dfrac{x^2}{e^x}$ וציינו אם $y=0$ אסימפטוטה אופקית של $f(x)=x^2 e^{-x}$.',
      correct_answer: '0; yes y=0 is HA as x→∞',
      explanation_en: 'Exp dominates poly ⇒ limit 0 ⇒ horizontal asymptote $y=0$ as $x\\to\\infty$.',
      explanation_he: 'מעריך שולט על פולינום ⇒ גבול 0 ⇒ אסימפטוטה אופקית $y=0$.',
    },
  ]);
  save(lesson);
}

// ─── 2. Trig limits closed lesson ────────────────────────────────────────────
{
  const lesson = structuredClone(load('limits'));
  lesson.concept_id = 'limits_trigonometric_5pt';
  lesson.math_track = ['5pt'];
  lesson.title_en = 'Trigonometric Limits (5pt) — Closed Toolkit';
  lesson.title_he = 'גבולות טריגונומטריים (5 יח׳) — ארגז סגור';
  lesson.summary_en =
    'Closed MoE section for trig limits: $\\lim_{x\\to 0}\\sin x/x=1$, companion cosine limits, and algebraic reductions using the standard toolkit.';
  lesson.summary_he =
    'מקטע סגור לגבולות טריג: $\\lim_{x\\to 0}\\sin x/x=1$, גבולות קוסינוס נלווים, ופישוטים אלגבריים עם ארגז סטנדרטי.';
  lesson.skill_atom_bank = ['trig_limit', 'sinx_over_x', 'trig_algebra'];
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.title_en = 'A closed trig-limits toolkit';
    intro.title_he = 'ארגז סגור לגבולות טריג';
    intro.body_en_md = `Treat $\\lim_{x\\to 0}\\dfrac{\\sin x}{x}=1$ and $\\lim_{x\\to 0}\\dfrac{1-\\cos x}{x^2}=\\tfrac12$ as **standard results** in the 5pt toolkit. Reduce other trig limits to these by algebra (angle scaling, identities).`;
    intro.body_he_md = `התייחסו ל-$\\lim_{x\\to 0}\\dfrac{\\sin x}{x}=1$ ול-$\\lim_{x\\to 0}\\dfrac{1-\\cos x}{x^2}=\\tfrac12$ כ**תוצאות סטנדרטיות** בארגז 5 יח׳. הפחיתו גבולות טריג אחרים לאלה באלגברה.`;
  }
  Object.assign(lesson, walkScrub(lesson));
  upsertTheory(lesson, 'MOE_TRIG_LIMITS', {
    kind: 'theory',
    title_en: 'Standard trig limits and reductions',
    title_he: 'גבולות טריג סטנדרטיים והפחתות',
    body_en_md: `**Core.** $\\lim_{\\theta\\to 0}\\sin\\theta/\\theta=1$. Then $\\lim_{x\\to 0}\\sin(ax)/(ax)=1$ so $\\sin(ax)/x\\to a$.

**Cosine companion.** $1-\\cos x=2\\sin^2(x/2)$ yields $\\lim_{x\\to 0}(1-\\cos x)/x^2=1/2$.

**Workflow.** Rewrite → scale angle → apply core limit → multiply constants.`,
    body_he_md: `**ליבה.** $\\lim_{\\theta\\to 0}\\sin\\theta/\\theta=1$. מכאן $\\sin(ax)/x\\to a$.

**קוסינוס.** $1-\\cos x=2\\sin^2(x/2)$ ⇒ $(1-\\cos x)/x^2\\to 1/2$.

**זרימה.** שכתוב → סקיילת זווית → גבול ליבה → כפל קבועים.`,
  });
  upsertQuestions(lesson, 'trig-lim', [
    {
      kind: 'numeric',
      difficulty: 'medium',
      facets: ['trig_limit', 'sinx_over_x'],
      archetypes: ['procedural'],
      stem_en: 'Evaluate $\\lim_{x\\to 0}\\dfrac{\\sin 5x}{x}$.',
      stem_he: 'חשבו $\\lim_{x\\to 0}\\dfrac{\\sin 5x}{x}$.',
      correct_answer: 5,
      explanation_en: '$\\sin(5x)/x=5\\cdot\\sin(5x)/(5x)\\to 5\\cdot 1=5$.',
      explanation_he: '$\\sin(5x)/x=5\\cdot\\sin(5x)/(5x)\\to 5$.',
    },
  ]);
  save(lesson);
}

// ─── 3. Parabola y^2=2px (MoE) ───────────────────────────────────────────────
{
  const lesson = structuredClone(load('analytic_geometry'));
  lesson.concept_id = 'analytic_geometry_parabola';
  lesson.math_track = ['5pt'];
  lesson.title_en = 'Analytic Geometry — Parabola ($y^2=2px$)';
  lesson.title_he = 'גאומטריה אנליטית — פרבולה ($y^2=2px$)';
  lesson.summary_en =
    'Israeli MoE parabola: standard form $y^2=2px$ (focus $(p/2,0)$, directrix $x=-p/2$). Completing the square, axis parallel to a coordinate axis. Not ordinary $y=ax^2$ graphing from functions class.';
  lesson.summary_he =
    'פרבולה בתוכנית: $y^2=2px$ (מוקד $(p/2,0)$, מכוון $x=-p/2$). השלמת ריבוע, ציר מקביל לציר קואורדינטות. לא גרף $y=ax^2$ רגיל משיעור פונקציות.';
  lesson.skill_atom_bank = ['parabola_2px', 'focus_directrix', 'complete_square_parabola'];
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.title_en = 'The MoE parabola $y^2=2px$';
    intro.title_he = 'הפרבולה בתוכנית $y^2=2px$';
    intro.body_en_md = `In MoE analytic geometry the **parabola** is defined by focus–directrix and written in the standard form **$y^2=2px$** (or $x^2=2py$ after swapping axes). Focus: $(p/2,0)$; directrix: $x=-p/2$. This lesson is **not** about graphing ordinary $y=ax^2$ from functions class — that belongs under functions. Ellipse material lives in its own analytic-geometry lesson.`;
    intro.body_he_md = `בגאומטריה אנליטית מגדירים **פרבולה** במוקד–מכוון ובצורה **$y^2=2px$** (או $x^2=2py$). מוקד: $(p/2,0)$; מכוון: $x=-p/2$. השיעור **אינו** על $y=ax^2$ משיעור פונקציות. חומר האליפסה נמצא בשיעור נפרד בגאומטריה אנליטית.`;
  }
  Object.assign(lesson, walkScrub(lesson));
  // Re-apply intro after scrub (disclaimers may mention words the scrub rewrites)
  {
    const intro2 = lesson.sections?.find((s) => s.kind === 'intro');
    if (intro2) {
      intro2.title_en = 'The MoE parabola $y^2=2px$';
      intro2.title_he = 'הפרבולה בתוכנית $y^2=2px$';
      intro2.body_en_md = `In MoE analytic geometry the **parabola** is defined by focus–directrix and written in the standard form **$y^2=2px$** (or $x^2=2py$ after swapping axes). Focus: $(p/2,0)$; directrix: $x=-p/2$. This lesson is **not** about graphing ordinary $y=ax^2$ from functions class — that belongs under functions. Ellipse material lives in its own analytic-geometry lesson.`;
      intro2.body_he_md = `בגאומטריה אנליטית מגדירים **פרבולה** במוקד–מכוון ובצורה **$y^2=2px$** (או $x^2=2py$). מוקד: $(p/2,0)$; מכוון: $x=-p/2$. השיעור **אינו** על $y=ax^2$ משיעור פונקציות. חומר האליפסה נמצא בשיעור נפרד בגאומטריה אנליטית.`;
    }
  }
  upsertTheory(lesson, 'MOE_PARABOLA_2PX', {
    kind: 'theory',
    title_en: 'Standard form $y^2=2px$ and completing the square',
    title_he: 'צורה סטנדרטית $y^2=2px$ והשלמת ריבוע',
    body_en_md: `**Standard.** $y^2=2px$ opens right; focus $(p/2,0)$, directrix $x=-p/2$. $x^2=2py$ opens up; focus $(0,p/2)$.

**Complete the square.** From $y^2+Dy+Ex+F=0$ (no $x^2$ term), complete in $y$ to reach $(y-k)^2=2p(x-h)$. Read vertex $(h,k)$ and parameter $p$.

**With a circle.** Shared chords / substitution $y^2=2px$ into a circle equation are common MoE moves.`,
    body_he_md: `**סטנדרטי.** $y^2=2px$ נפתחת ימינה; מוקד $(p/2,0)$, מכוון $x=-p/2$.

**השלמת ריבוע.** מ-$y^2+Dy+Ex+F=0$ מגיעים ל-$(y-k)^2=2p(x-h)$.

**עם מעגל.** מיתרים משותפים / הצבת $y^2=2px$ במעגל — מהלכים שכיחים.`,
  });
  upsertQuestions(lesson, 'parab', [
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['parabola_2px', 'focus_directrix'],
      archetypes: ['procedural', 'conceptual'],
      stem_en: 'For $y^2=2px$ with $p=4$, state the focus and directrix.',
      stem_he: 'עבור $y^2=2px$ עם $p=4$, ציינו מוקד ומכוון.',
      correct_answer: 'focus (2,0); directrix x=-2',
      explanation_en: 'Focus $(p/2,0)=(2,0)$; directrix $x=-p/2=-2$.',
      explanation_he: 'מוקד $(2,0)$; מכוון $x=-2$.',
    },
  ]);
  save(lesson);
}

// ─── 4. Ellipse under analytic geometry (keep separate, scrub cone) ──────────
{
  const lesson = walkScrub(structuredClone(load('analytic_geometry_ellipse')));
  lesson.math_track = ['5pt'];
  lesson.title_en = 'Analytic Geometry — Ellipse (Foci & Standard Form)';
  lesson.title_he = 'גאומטריה אנליטית — אליפסה (מוקדים וצורה סטנדרטית)';
  lesson.summary_en =
    'Ellipse in MoE analytic geometry: $|PF_1|+|PF_2|=2a$, standard form, completing the square. Foci and Cartesian form only; separate from the parabola lesson.';
  lesson.summary_he =
    'אליפסה בגאומטריה אנליטית: $|PF_1|+|PF_2|=2a$, צורה סטנדרטית, השלמת ריבוע. מוקדים וצורה קרטזית בלבד; נפרד משיעור הפרבולה.';
  save(lesson);
}

// ─── 5. Classification lesson ────────────────────────────────────────────────
{
  const lesson = structuredClone(load('analytic_geometry_5pt'));
  lesson.concept_id = 'analytic_geometry_classification';
  lesson.math_track = ['5pt'];
  lesson.title_en = 'Analytic Geometry — Identifying Circle, Parabola, Ellipse';
  lesson.title_he = 'גאומטריה אנליטית — זיהוי מעגל, פרבולה, אליפסה';
  lesson.summary_en =
    'Classify a general quadratic $Ax^2+Bxy+Cy^2+\\cdots=0$ (axis-aligned: $B=0$) as circle, parabola, or ellipse; complete the square; stretch a circle into an ellipse.';
  lesson.summary_he =
    'סיווג משוואה ריבועית כמעגל / פרבולה / אליפסה; השלמת ריבוע; מתיחת מעגל לאליפסה.';
  lesson.skill_atom_bank = ['classify_conic', 'complete_square', 'circle_to_ellipse'];
  Object.assign(lesson, walkScrub(lesson));
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.title_en = 'When is an equation a circle, parabola, or ellipse?';
    intro.title_he = 'מתי משוואה היא מעגל, פרבולה או אליפסה?';
    intro.body_en_md = `Given $Ax^2+Cy^2+Dx+Ey+F=0$ (no $xy$ term): if $A=C\\neq 0$ → **circle** (after completing the square); if exactly one of $A,C$ is zero → **parabola**; if $A\\cdot C>0$ and $A\\neq C$ → **ellipse**. Then complete the square to read center/axes or the MoE parabola parameter $p$ in $y^2=2px$.`;
    intro.body_he_md = `עבור $Ax^2+Cy^2+Dx+Ey+F=0$: אם $A=C\\neq 0$ → **מעגל**; אם בדיוק אחד מ-$A,C$ אפס → **פרבולה**; אם $A\\cdot C>0$ ו-$A\\neq C$ → **אליפסה**. אחר כך השלימו ריבוע וקראו פרמטרים — לפרבולה בתוכנית $y^2=2px$.`;
  }
  upsertTheory(lesson, 'MOE_CLASSIFY_TRANSFORM', {
    kind: 'theory',
    title_en: 'Classification and circle → ellipse stretch',
    title_he: 'סיווג ומתיחת מעגל → אליפסה',
    body_en_md: `**Classify** by which quadratic terms appear, then complete the square.

**Circle → ellipse.** Starting from $x^2+y^2=r^2$, the substitution $x=au$, $y=bv$ (or scaling axes) yields $\\dfrac{u^2}{(r/a)^2}+\\dfrac{v^2}{(r/b)^2}=1$. Conversely, an axis-aligned ellipse can be read as a stretched circle.`,
    body_he_md: `**סיווג** לפי אילו איברים ריבועיים מופיעים, ואז השלמת ריבוע.

**מעגל → אליפסה.** מ-$x^2+y^2=r^2$, הצבה $x=au$, $y=bv$ נותנת אליפסה. להפך — אליפסה מיושרת נקראת כמעגל מתוח.`,
  });
  upsertQuestions(lesson, 'classify', [
    {
      kind: 'mcq',
      difficulty: 'medium',
      facets: ['classify_conic'],
      archetypes: ['conceptual'],
      stem_en: 'The equation $y^2-4x+6y=0$ represents a:',
      stem_he: 'המשוואה $y^2-4x+6y=0$ מתארת:',
      answer_payload: {
        options_en: ['circle', 'parabola', 'ellipse', 'pair of lines'],
        options_he: ['מעגל', 'פרבולה', 'אליפסה', 'זוג ישרים'],
        correct_index: 1,
      },
      explanation_en: 'Only one squared variable ($y^2$) → parabola. Complete the square in $y$ toward $y^2=2px$ form.',
      explanation_he: 'רק משתנה אחד בריבוע → פרבולה. השלימו ריבוע לצורה $y^2=2px$.',
    },
  ]);
  save(lesson);
}

// ─── 6. Scrub analytic_geometry_5pt + conics overview ────────────────────────
for (const id of ['analytic_geometry_5pt', 'analytic_geometry__5pt', 'analytic_geometry_conics']) {
  const fp = path.join(DIR, `${id}.json`);
  if (!fs.existsSync(fp)) continue;
  let lesson = walkScrub(load(id));
  lesson.math_track = ['5pt'];
  if (id.includes('conics') || /Conics/i.test(lesson.title_en || '')) {
    lesson.title_en = 'Analytic Geometry — Parabola & Ellipse Overview (MoE)';
    lesson.title_he = 'גאומטריה אנליטית — סקירת פרבולה ואליפסה (תוכנית)';
    lesson.summary_en =
      'Overview pointing to dedicated parabola ($y^2=2px$) and ellipse lessons, plus classification. Focus–directrix and Cartesian forms only.';
  }
  upsertTheory(lesson, 'MOE_AG5_POINTER', {
    kind: 'theory',
    title_en: 'Use dedicated parabola / ellipse / classification lessons',
    title_he: 'השתמשו בשיעורים הייעודיים לפרבולה / אליפסה / סיווג',
    body_en_md: `Deep practice: \`analytic_geometry_parabola\` ($y^2=2px$), \`analytic_geometry_ellipse\`, and \`analytic_geometry_classification\` (when an unstructured quadratic is a circle/parabola/ellipse; circle→ellipse stretch).`,
    body_he_md: `תרגול מעמיק: \`analytic_geometry_parabola\` ($y^2=2px$), \`analytic_geometry_ellipse\`, ו-\`analytic_geometry_classification\`.`,
  });
  save(lesson);
}

// ─── 7. Track fixes: growth/decay, euclidean, implicit ───────────────────────
{
  const growth = load('exponential_growth_decay_models');
  growth.math_track = ['4pt'];
  growth.title_en = 'Exponential Growth and Decay Models';
  growth.title_he = growth.title_he || 'מודלים של גדילה ודעיכה מעריכית';
  save(growth);
}

// Do NOT add 5pt onto shared Euclidean bases — that breaks single-track ownership.
// 5pt learners use `__5pt` variants (see moe-5pt-scope-finish.mjs).
for (const [id, track] of Object.entries({
  circles: ['3pt'],
  triangles_congruence: ['3pt'],
  similar_triangles: ['3pt'],
  quadrilaterals: ['3pt'],
  euclidean_geometry_circles: ['4pt'],
})) {
  const fp = path.join(DIR, `${id}.json`);
  if (!fs.existsSync(fp)) continue;
  const lesson = load(id);
  lesson.math_track = track;
  save(lesson);
}

{
  const imp = load('implicit_differentiation');
  imp.math_track = ['university'];
  imp.summary_en = `${imp.summary_en || ''} (University / explanatory — not a MoE 5pt catalog topic.)`;
  save(imp);
}

// Scrub limits_at_infinity for denylist hits
{
  const limInf = walkScrub(load('limits_at_infinity'));
  limInf.math_track = ['5pt'];
  upsertTheory(limInf, 'MOE_LIM_INF_HA', {
    kind: 'theory',
    title_en: 'Horizontal asymptotes from $\\lim_{x\\to\\pm\\infty}$',
    title_he: 'אסימפטוטות אופקיות מ-$\\lim_{x\\to\\pm\\infty}$',
    body_en_md: `Compute $\\lim_{x\\to\\infty}f$ and $\\lim_{x\\to-\\infty}f$ separately. Each finite value is a horizontal asymptote candidate. Use polynomial degree rules and log/exp vs poly comparisons.`,
    body_he_md: `חשבו בנפרד $\\lim_{x\\to\\infty}$ ו-$\\lim_{x\\to-\\infty}$. כל ערך סופי הוא מועמד לאסימפטוטה אופקית. השתמשו בכללי מעלות וביחסי לוג/מעריך.`,
  });
  save(limInf);
}

console.log('moe-5pt-scope-remediation: done');
