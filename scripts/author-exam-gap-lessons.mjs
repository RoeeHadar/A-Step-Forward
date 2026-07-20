#!/usr/bin/env node
/**
 * Author Wave-1 exam-gap lessons by cloning rich donors, rewriting MoE framing,
 * and injecting facet-tagged questions + theory sections.
 *
 * Creates:
 *   trigonometry_sine_cosine_laws
 *   analytic_geometry_parabola
 *   analytic_geometry_ellipse
 *   probability_trees_tables
 *   probability_bernoulli
 *   functions_even_odd
 * Scrubs cone framing on analytic_geometry_conics.
 *
 * Usage: node scripts/author-exam-gap-lessons.mjs
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
  const id = lesson.concept_id;
  fs.writeFileSync(path.join(DIR, `${id}.json`), `${JSON.stringify(lesson, null, 2)}\n`);
  console.log('wrote', id);
}

function cloneDonor(donorId, overrides) {
  const lesson = load(donorId);
  const out = structuredClone(lesson);
  Object.assign(out, overrides);
  out.concept_id = overrides.concept_id;
  out.version = (Number(lesson.version) || 1) + 1;
  out.author = out.author || 'exam-gap-wave1';
  return out;
}

function upsertTheory(lesson, marker, section) {
  lesson.sections = lesson.sections || [];
  const already = lesson.sections.some(
    (s) => (s.body_en_md || '').includes(marker) || (s.title_en || '') === section.title_en,
  );
  if (already) return;
  const insert = {
    ...section,
    body_en_md: `<!-- ${marker} -->\n${section.body_en_md}`,
  };
  const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
  if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
  else lesson.sections.push(insert);
}

function upsertQuestions(lesson, fileBase, questions) {
  lesson.questions = lesson.questions || [];
  const existing = new Set();
  for (const q of lesson.questions) {
    for (const f of q.facets || []) existing.add(f);
  }
  for (const q of questions) {
    if ((q.facets || []).some((f) => existing.has(f))) continue;
    const ord = lesson.questions.length + 1;
    lesson.questions.push({
      ...q,
      id: `${fileBase}-exam-${ord}`,
      ord,
      skill_atoms: q.skill_atoms || (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existing.add(f);
  }
}

function rewriteIntro(lesson, title_en, title_he, summary_en, summary_he, intro_en, intro_he) {
  lesson.title_en = title_en;
  lesson.title_he = title_he;
  lesson.summary_en = summary_en;
  lesson.summary_he = summary_he;
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.title_en = title_en;
    intro.title_he = title_he;
    intro.body_en_md = intro_en;
    intro.body_he_md = intro_he;
  }
}

// ─── 1. Sine / cosine laws ───────────────────────────────────────────────────
{
  const lesson = cloneDonor('trigonometry_identities', {
    concept_id: 'trigonometry_sine_cosine_laws',
    math_track: ['4pt', '5pt'],
    level: 'intermediate',
    level_focus: 'MoE plane trig: sine law, cosine law, area via sine — not right-triangle ratios alone',
    skill_atom_bank: ['sine_law', 'cosine_law', 'triangle_area_sine', 'ssa_ambiguous', 'law_of_sines'],
  });
  rewriteIntro(
    lesson,
    'Sine Law, Cosine Law & Triangle Area',
    'משפט הסינוסים, משפט הקוסינוסים ושטח משולש',
    'Solve non-right triangles with the sine law, cosine law, and area $\\tfrac12 ab\\sin C$. Multi-part stacked exam stems.',
    'פותרים משולשים כלליים עם משפט הסינוסים, משפט הקוסינוסים ושטח $\\tfrac12 ab\\sin C$. ניסוחים רב-חלקיים בסגנון בחינה.',
    `**Not SOH-CAH-TOA alone.** When a triangle is **not** right-angled, use the **law of sines** $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}=\\dfrac{c}{\\sin C}$ and the **law of cosines** $c^2=a^2+b^2-2ab\\cos C$. Area is $\\tfrac12 ab\\sin C$. Sketch, label sides opposite angles, then choose the law that matches the given data (SAS / ASA / SSS / SSA).`,
    `**לא רק יחסים במשולש ישר-זווית.** כשהמשולש **אינו** ישר-זווית, משתמשים ב**משפט הסינוסים** $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}=\\dfrac{c}{\\sin C}$ וב**משפט הקוסינוסים** $c^2=a^2+b^2-2ab\\cos C$. השטח הוא $\\tfrac12 ab\\sin C$. סקצו, סמנו צלעות מול זוויות, ובחרו את המשפט שמתאים לנתונים (SAS / ASA / SSS / SSA).`,
  );
  upsertTheory(lesson, 'SINE_COSINE_LAWS_CORE', {
    kind: 'theory',
    title_en: 'Core toolkit: sine law, cosine law, area via sine',
    title_he: 'ארגז כלים: משפט הסינוסים, משפט הקוסינוסים, שטח לפי סינוס',
    body_en_md: `**Law of sines (משפט הסינוסים).** $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}=2R$ where $R$ is the circumradius. Use when you know a side and its opposite angle (ASA, AAS, or careful SSA).

**Law of cosines (משפט הקוסינוסים).** $c^2=a^2+b^2-2ab\\cos C$. Use for SAS (two sides + included angle) or SSS (find an angle).

**Area via sine.** $\\mathrm{Area}=\\tfrac12 ab\\sin C$. Same angle $C$ must be **included** between sides $a$ and $b$.

**Multi-part stack.** Part (a) find a side; part (b) find an angle; part (c) area — reuse the diagram and carry exact values.`,
    body_he_md: `**משפט הסינוסים.** $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}=2R$ כאשר $R$ רדיוס המעגל החוסם. השתמשו כשידועים צלע והזווית שמולה (ASA, AAS, או SSA בזהירות).

**משפט הקוסינוסים.** $c^2=a^2+b^2-2ab\\cos C$. ל-SAS (שתי צלעות וזווית כלואה) או SSS (מציאת זווית).

**שטח לפי סינוס.** $\\mathrm{Area}=\\tfrac12 ab\\sin C$. הזווית $C$ חייבת להיות **כלואה** בין $a$ ו-$b$.

**מחסנית רב-חלקית.** חלק (א) צלע; חלק (ב) זווית; חלק (ג) שטח — השתמשו באותו איור והעבירו ערכים מדויקים.`,
  });
  upsertQuestions(lesson, 'trigonometry_sine_cosine_laws', [
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['sine_law', 'law_of_sines'],
      archetype: 'procedural',
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'In $\\triangle ABC$, $A=40^\\circ$, $B=65^\\circ$, $a=8$. Use the **law of sines** to find $b$. Show $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}$.',
      stem_he:
        'ב-$\\triangle ABC$, $A=40^\\circ$, $B=65^\\circ$, $a=8$. מצאו את $b$ עם **משפט הסינוסים**. הראו $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}$.',
      correct_answer: 'b = 8 sin(65°)/sin(40°)',
      explanation_en:
        'From the law of sines, $\\dfrac{8}{\\sin 40^\\circ}=\\dfrac{b}{\\sin 65^\\circ}$, so $b=8\\sin 65^\\circ/\\sin 40^\\circ$. First find $C=180^\\circ-A-B$ only if you need side $c$; here $b$ is opposite $B$ and the sine-law ratio is enough.',
      explanation_he:
        'ממשפט הסינוסים $\\dfrac{8}{\\sin 40^\\circ}=\\dfrac{b}{\\sin 65^\\circ}$, ולכן $b=8\\sin 65^\\circ/\\sin 40^\\circ$. את $C=180^\\circ-A-B$ מחשבים רק אם צריך את $c$; כאן מספיק היחס של משפט הסינוסים.',
    },
    {
      kind: 'open',
      difficulty: 'hard',
      facets: ['cosine_law', 'law_of_cosines'],
      archetype: 'procedural',
      archetypes: ['procedural', 'proof'],
      stem_en:
        'Given $a=5$, $b=7$, included angle $C=60^\\circ$, find $c$ with the **law of cosines** $c^2=a^2+b^2-2ab\\cos C$.',
      stem_he:
        'נתון $a=5$, $b=7$, זווית כלואה $C=60^\\circ$. מצאו $c$ עם **משפט הקוסינוסים** $c^2=a^2+b^2-2ab\\cos C$.',
      correct_answer: 'c = sqrt(39)',
      explanation_en:
        'Substitute: $c^2=25+49-2\\cdot5\\cdot7\\cdot\\cos 60^\\circ=74-70\\cdot\\tfrac12=74-35=39$, so $c=\\sqrt{39}$. Cosine law is the SAS workhorse — do not force sine law when the included angle is given.',
      explanation_he:
        'הצבה: $c^2=25+49-2\\cdot5\\cdot7\\cdot\\cos 60^\\circ=74-35=39$, ולכן $c=\\sqrt{39}$. משפט הקוסינוסים הוא הכלי ל-SAS — אל תכפו משפט סינוסים כשהזווית הכלואה נתונה.',
    },
    {
      kind: 'numeric',
      difficulty: 'medium',
      facets: ['area_via_sine', 'triangle_area_sine'],
      archetype: 'procedural',
      stem_en:
        'Two sides $a=6$, $b=10$ enclose angle $C=30^\\circ$. Compute the area $\\tfrac12 ab\\sin C$.',
      stem_he:
        'שתי צלעות $a=6$, $b=10$ כולאות זווית $C=30^\\circ$. חשבו את השטח $\\tfrac12 ab\\sin C$.',
      correct_answer: 15,
      explanation_en:
        '$\\tfrac12\\cdot6\\cdot10\\cdot\\sin 30^\\circ=30\\cdot\\tfrac12=15$. The angle in the area formula must be the included angle between those two sides.',
      explanation_he:
        '$\\tfrac12\\cdot6\\cdot10\\cdot\\sin 30^\\circ=15$. הזווית בנוסחת השטח חייבת להיות הזווית הכלואה בין שתי הצלעות.',
    },
    {
      kind: 'open',
      difficulty: 'hard',
      facets: ['multipart_stack', 'stacked_exercise'],
      archetype: 'graphical',
      archetypes: ['procedural', 'conceptual', 'graphical'],
      stem_en:
        'Multi-part stack. In $\\triangle ABC$: (a) given ASA data, find a side by the sine law; (b) then find another angle; (c) find the area via $\\tfrac12 ab\\sin C$. Keep one diagram.',
      stem_he:
        'מחסנית רב-חלקית. ב-$\\triangle ABC$: (א) מנתוני ASA מצאו צלע במשפט הסינוסים; (ב) מצאו זווית נוספת; (ג) מצאו שטח עם $\\tfrac12 ab\\sin C$. שמרו על איור אחד.',
      correct_answer: 'a→b→c chained; one sketch',
      explanation_en:
        'Part (a) uses sine law on a known angle–side pair. Part (b) uses $A+B+C=180^\\circ$ or another sine-law ratio. Part (c) picks two sides and their included angle for $\\tfrac12 ab\\sin C$. Exam graders expect the same sketch reused — do not restart the triangle in each part.',
      explanation_he:
        'חלק (א) משפט סינוסים על זוג זווית–צלע ידוע. חלק (ב) סכום זוויות או יחס סינוסים נוסף. חלק (ג) שתי צלעות וזווית כלואה ל-$\\tfrac12 ab\\sin C$. בודקים מצפים לאותו איור — אל תתחילו משולש מחדש בכל חלק.',
    },
  ]);
  if (lesson.agent_hints) {
    lesson.agent_hints.key_insights = [
      'Sine law for ASA/AAS; cosine law for SAS/SSS; area = (1/2)ab sin C with included angle.',
      'SSA can be ambiguous — check for two triangles when an acute angle is opposite a given side.',
    ];
    lesson.agent_hints.common_misconceptions = [
      'Treating every triangle as right-angled and using SOH-CAH-TOA only.',
      'Using area formula with a non-included angle.',
    ];
  }
  save(lesson);
}

// ─── 2. Parabola (MoE, no cone) ──────────────────────────────────────────────
{
  const lesson = cloneDonor('analytic_geometry_conics', {
    concept_id: 'analytic_geometry_parabola',
    math_track: ['5pt'],
    level_focus: 'MoE parabola: focus, directrix, y^2=4px / x^2=4py — no cone-section narrative',
    skill_atom_bank: ['parabola', 'focus_directrix', 'vertex_form', 'parabola_circle'],
  });
  rewriteIntro(
    lesson,
    'Analytic Geometry — Parabola (Focus & Directrix)',
    'גאומטריה אנליטית — פרבולה (מוקד ומכוון)',
    'Define the parabola by focus and directrix; standard forms $y^2=4px$ and $x^2=4py$; relate to circles through shared points or curvature — without cutting a cone.',
    'מגדירים פרבולה לפי מוקד ומכוון; צורות $y^2=4px$ ו-$x^2=4py$; קשר למעגלים — בלי חיתוך חרוט.',
    `A **parabola** is the set of points equidistant from a fixed point (the **focus**) and a fixed line (the **directrix**). Standard forms: $y^2=4px$ (opens horizontally) and $x^2=4py$ (opens vertically). Vertex, axis, and $p$ come from completing the square or reading the focus–directrix pair. **Do not** introduce the curve by slicing a cone — MoE framing is focus–directrix and Cartesian equations.`,
    `**פרבולה** היא קבוצת הנקודות במרחק שווה מנקודה קבועה (**מוקד**) ומקו ישר קבוע (**מכוון**). צורות סטנדרטיות: $y^2=4px$ ו-$x^2=4py$. קדקוד, ציר ו-$p$ מריבוע מלא או מזוג מוקד–מכוון. **אל** תציגו את העקום כחיתוך חרוט — המסגרת היא מוקד–מכוון ומשוואות קרטזיות.`,
  );
  // Scrub cone language in all sections
  for (const s of lesson.sections || []) {
    for (const k of ['body_en_md', 'body_he_md', 'title_en', 'title_he']) {
      if (!s[k]) continue;
      s[k] = s[k]
        .replace(/conic section/gi, 'quadratic curve')
        .replace(/cutting (a |the )?cone/gi, 'using focus and directrix')
        .replace(/double[- ]napped cone/gi, 'focus–directrix definition')
        .replace(/חתך חרוט/g, 'עקום ריבועי')
        .replace(/חותכים חרוט/g, 'מגדירים במוקד ומכוון')
        .replace(/חרוט/g, 'עקום');
    }
  }
  upsertTheory(lesson, 'PARABOLA_MOE_CORE', {
    kind: 'theory',
    title_en: 'Parabola focus–directrix and circle relation',
    title_he: 'פרבולה: מוקד–מכוון וקשר למעגל',
    body_en_md: `**Focus–directrix.** For $y^2=4px$, focus is $(p,0)$ and directrix is $x=-p$. Every point $P$ on the parabola satisfies $|PF|=$ distance to the directrix.

**Circle relation.** A circle through the vertex that shares a tangent or intersects the parabola at known points is a common MoE device — equate, subtract, and read shared chords. Curvature at the vertex relates radius $2p$ in the osculating-circle picture, but stay algebraic: substitute and count intersections.`,
    body_he_md: `**מוקד–מכוון.** עבור $y^2=4px$, המוקד הוא $(p,0)$ והמכוון $x=-p$. כל נקודה $P$ מקיימת $|PF|=$ מרחק למכוון.

**קשר למעגל.** מעגל דרך הקדקוד שחולק משיק או חותך את הפרבולה בנקודות ידועות הוא כלי שכיח — השוו, החסירו, וקראו מיתרים משותפים. הישארו אלגבריים: הציבו וספרו חיתוכים.`,
  });
  upsertQuestions(lesson, 'analytic_geometry_parabola', [
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['parabola_focus_directrix', 'focus_directrix'],
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'For $y^2=8x$, state the focus and directrix (so $4p=8$). Verify one point on the curve is equidistant from focus and directrix.',
      stem_he:
        'עבור $y^2=8x$, ציינו מוקד ומכוון ($4p=8$). אמתו שנקודה אחת על העקום במרחק שווה ממוקד וממכוון.',
      correct_answer: 'focus (2,0); directrix x=-2',
      explanation_en:
        '$4p=8\\Rightarrow p=2$. Focus $(2,0)$, directrix $x=-2$. For a point $(2t^2,4t)$ on $y^2=8x$, distances to focus and directrix both equal $|2+2t^2|$ (parametric check) — the focus–directrix definition holds.',
      explanation_he:
        '$4p=8\\Rightarrow p=2$. מוקד $(2,0)$, מכוון $x=-2$. המרחקים מנקודה על העקום למוקד ולמכוון שווים — זו הגדרת המוקד–מכוון.',
    },
    {
      kind: 'open',
      difficulty: 'hard',
      facets: ['parabola_circle_relation'],
      archetypes: ['procedural', 'proof'],
      stem_en:
        'Find the intersection points of the parabola $y^2=4x$ and the circle $(x-1)^2+y^2=r^2$ for a value of $r$ that yields two real points; interpret the shared chord.',
      stem_he:
        'מצאו חיתוכי הפרבולה $y^2=4x$ והמעגל $(x-1)^2+y^2=r^2$ לערך $r$ עם שני חיתוכים ממשיים; פרשו את המיתר המשותף.',
      correct_answer: 'substitute y^2=4x into circle; shared chord vertical/horizontal as algebra dictates',
      explanation_en:
        'Substitute $y^2=4x$ into the circle to get a quadratic in $x$. Choose $r$ so two real roots appear. The line joining intersection points is the shared chord — a standard parabola–circle relation move on MoE papers.',
      explanation_he:
        'הציבו $y^2=4x$ במעגל לקבלת ריבועית ב-$x$. בחרו $r$ עם שני שורשים ממשיים. הישר המחבר את נקודות החיתוך הוא המיתר המשותף — מהלך סטנדרטי של קשר פרבולה–מעגל.',
    },
  ]);
  save(lesson);
}

// ─── 3. Ellipse (MoE, no cone) ───────────────────────────────────────────────
{
  const lesson = cloneDonor('analytic_geometry_conics', {
    concept_id: 'analytic_geometry_ellipse',
    math_track: ['5pt'],
    level_focus: 'MoE ellipse: foci, 2a, standard form — no cone-section narrative',
    skill_atom_bank: ['ellipse', 'ellipse_foci', 'standard_form', 'eccentricity'],
  });
  rewriteIntro(
    lesson,
    'Analytic Geometry — Ellipse (Foci & Standard Form)',
    'גאומטריה אנליטית — אליפסה (מוקדים וצורה סטנדרטית)',
    'Ellipse as $|PF_1|+|PF_2|=2a$; standard form $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$; eccentricity basics — without cutting a cone.',
    'אליפסה כ-$|PF_1|+|PF_2|=2a$; צורה $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$; אקסצנטריות בסיסית — בלי חיתוך חרוט.',
    `An **ellipse** is the set of points whose distances to two foci sum to the constant $2a$ (with $2a>|F_1F_2|$). Standard form $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ (or swapped) encodes semi-axes; $c^2=a^2-b^2$ places the foci. MoE stems ask for foci, $2a$, and rewriting expanded equations into standard form — **not** a cone-cutting story.`,
    `**אליפסה** היא קבוצת הנקודות שסכום מרחקיהן לשני מוקדים הוא $2a$ (עם $2a>|F_1F_2|$). הצורה $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ מקודדת חצאי צירים; $c^2=a^2-b^2$ ממקם מוקדים. הניסוחים מבקשים מוקדים, $2a$, והבאה לצורה סטנדרטית — **לא** סיפור חיתוך חרוט.`,
  );
  for (const s of lesson.sections || []) {
    for (const k of ['body_en_md', 'body_he_md', 'title_en', 'title_he']) {
      if (!s[k]) continue;
      s[k] = s[k]
        .replace(/conic section/gi, 'quadratic curve')
        .replace(/cutting (a |the )?cone/gi, 'using the two-foci definition')
        .replace(/חתך חרוט/g, 'עקום ריבועי')
        .replace(/חותכים חרוט/g, 'מגדירים בשני מוקדים')
        .replace(/חרוט/g, 'עקום');
    }
  }
  upsertTheory(lesson, 'ELLIPSE_MOE_CORE', {
    kind: 'theory',
    title_en: 'Ellipse foci and standard form',
    title_he: 'אליפסה: מוקדים וצורה סטנדרטית',
    body_en_md: `**Foci.** For $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ with $a>b$, foci $(\\pm c,0)$ where $c=\\sqrt{a^2-b^2}$. The defining sum is $|PF_1|+|PF_2|=2a$.

**Standard form.** Complete the square on a general quadratic $Ax^2+By^2+\\cdots=0$ (same-sign $A,B$) to reach $\\dfrac{(x-h)^2}{a^2}+\\dfrac{(y-k)^2}{b^2}=1$. Read center, axes, and then foci.`,
    body_he_md: `**מוקדים.** עבור $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ עם $a>b$, מוקדים $(\\pm c,0)$ כאשר $c=\\sqrt{a^2-b^2}$. סכום ההגדרה $|PF_1|+|PF_2|=2a$.

**צורה סטנדרטית.** השלימו ריבוע במשוואה כללית והגיעו ל-$\\dfrac{(x-h)^2}{a^2}+\\dfrac{(y-k)^2}{b^2}=1$. קראו מרכז, צירים, ואז מוקדים.`,
  });
  upsertQuestions(lesson, 'analytic_geometry_ellipse', [
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['ellipse_foci'],
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'For $\\dfrac{x^2}{25}+\\dfrac{y^2}{9}=1$, find $a$, $b$, $c$, and the foci. State the sum $|PF_1|+|PF_2|=2a$.',
      stem_he:
        'עבור $\\dfrac{x^2}{25}+\\dfrac{y^2}{9}=1$, מצאו $a$, $b$, $c$ ואת המוקדים. ציינו $|PF_1|+|PF_2|=2a$.',
      correct_answer: 'a=5,b=3,c=4; foci (±4,0); sum=10',
      explanation_en:
        '$a=5$, $b=3$, $c=\\sqrt{25-9}=4$. Foci $(\\pm4,0)$. By definition every point on the ellipse satisfies $|PF_1|+|PF_2|=10=2a$.',
      explanation_he:
        '$a=5$, $b=3$, $c=4$. מוקדים $(\\pm4,0)$. לפי ההגדרה $|PF_1|+|PF_2|=10=2a$.',
    },
    {
      kind: 'open',
      difficulty: 'hard',
      facets: ['ellipse_standard_form'],
      archetypes: ['procedural', 'proof'],
      stem_en:
        'Rewrite $9x^2+25y^2=225$ into standard form $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ and read the semi-axes.',
      stem_he:
        'הביאו את $9x^2+25y^2=225$ לצורה $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ וקראו את חצאי הצירים.',
      correct_answer: 'x^2/25 + y^2/9 = 1',
      explanation_en:
        'Divide by 225: $\\dfrac{9x^2}{225}+\\dfrac{25y^2}{225}=1\\Rightarrow \\dfrac{x^2}{25}+\\dfrac{y^2}{9}=1$. Semi-major axis $5$ along $x$, semi-minor $3$ along $y$.',
      explanation_he:
        'חילוק ב-225 נותן $\\dfrac{x^2}{25}+\\dfrac{y^2}{9}=1$. חצי ציר ראשי $5$ לאורך $x$, משני $3$ לאורך $y$.',
    },
  ]);
  save(lesson);
}

// ─── 4. Trees & tables ───────────────────────────────────────────────────────
{
  const lesson = cloneDonor('probability_basic', {
    concept_id: 'probability_trees_tables',
    math_track: ['4pt', '5pt', 'stats'],
    level_focus: 'Tree diagrams and two/three-way tables for MoE probability',
    skill_atom_bank: ['tree_diagram', 'two_way_table', 'conditional_from_table', 'multiply_along_branches'],
  });
  rewriteIntro(
    lesson,
    'Probability — Tree Diagrams & Tables',
    'הסתברות — דיאגרמות עץ וטבלאות',
    'Organize multi-stage experiments with tree diagrams; read joint and conditional probabilities from two-way and three-way tables.',
    'מארגנים ניסויים רב-שלביים בדיאגרמות עץ; קוראים הסתברויות משותפות ומקריות מטבלאות דו- ותלת-ממדיות.',
    `When an experiment has stages (draw, then draw again; test then retest), draw a **tree diagram**: each branch carries a probability, and paths multiply. When data are classified by two or three attributes, build a **two-way** or **three-way table** and read joints, margins, and conditionals from cells.`,
    `כשיש שלבים (שליפה ואז שליפה; בדיקה ואז בדיקה חוזרת), ציירו **דיאגרמת עץ**: כל ענף נושא הסתברות, ומסלולים כופלים. כשהנתונים מסווגים לפי שניים או שלושה מאפיינים, בנו **טבלה דו-ממדית** או **תלת-ממדית** וקראו משותפות, שולים ומקריות מהתאים.`,
  );
  upsertTheory(lesson, 'TREES_TABLES_CORE', {
    kind: 'theory',
    title_en: 'Tree diagrams, two-way tables, three-way tables',
    title_he: 'דיאגרמות עץ, טבלאות דו- ותלת-ממדיות',
    body_en_md: `**Tree diagram.** First-stage branches sum to 1; second-stage branches from each node sum to 1. A path probability is the product along branches. Union of disjoint paths adds.

**Two-way tables.** Rows × columns of counts or probabilities. Marginal = row/column sum. Conditional $P(A|B)=$ cell / column (or row) total for $B$.

**Three-way tables.** Add a third factor (e.g. gender × test × treatment). Slice into two-way layers, or flatten with care — always name which margin you condition on.`,
    body_he_md: `**דיאגרמת עץ.** ענפי שלב ראשון מסתכמים ל-1; מכל צומת ענפי השלב הבא מסתכמים ל-1. הסתברות מסלול היא מכפלת הענפים. איחוד מסלולים זרים מחברים.

**טבלאות דו-ממדיות.** שולים = סכומי שורה/עמודה. מקרית $P(A|B)=$ תא / סך העמודה (או השורה) של $B$.

**טבלאות תלת-ממדיות.** הוסיפו גורם שלישי. פרסו לשכבות דו-ממדיות — תמיד ציינו על איזה שול מתנים.`,
  });
  upsertQuestions(lesson, 'probability_trees_tables', [
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['tree_diagram', 'probability_tree'],
      archetypes: ['procedural', 'graphical'],
      stem_en:
        'Draw a tree diagram for two sequential draws without replacement from an urn with 3 red and 2 blue. Find $P(\\text{RR})$.',
      stem_he:
        'ציירו דיאגרמת עץ לשתי שליפות בזה אחר זה ללא החזרה מכד עם 3 אדומים ו-2 כחולים. מצאו $P(\\text{RR})$.',
      correct_answer: 'P(RR)=(3/5)*(2/4)=3/10',
      explanation_en:
        'First branch $P(R)=3/5$; given first red, $P(R|R)=2/4$. Path product $\\tfrac{3}{5}\\cdot\\tfrac{2}{4}=\\tfrac{3}{10}$. Label every branch; missing labels are the usual tree-diagram error.',
      explanation_he:
        'ענף ראשון $P(R)=3/5$; בהינתן אדום, $P(R|R)=2/4$. מכפלת מסלול $\\tfrac{3}{10}$. סמנו כל ענף.',
    },
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['two_way_tables', 'contingency_2way'],
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'From a two-way contingency table of pass/fail × morning/evening, compute $P(\\text{pass}|\\text{morning})$ from cell and column totals.',
      stem_he:
        'מטבלת עבר/נכשל × בוקר/ערב, חשבו $P(\\text{pass}|\\text{morning})$ מסכומי תא ועמודה.',
      correct_answer: 'cell / morning column total',
      explanation_en:
        'Conditional probability from a two-way table is the joint cell divided by the conditioning margin. Do not divide by the grand total unless you want the joint, not the conditional.',
      explanation_he:
        'הסתברות מקרית מטבלה דו-ממדית היא תא משותף חלקי שול ההתניה. אל תחלקו בסך הכללי אם אתם רוצים מקרית ולא משותפת.',
    },
    {
      kind: 'open',
      difficulty: 'hard',
      facets: ['three_way_tables', 'three_way_table'],
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'A three-way table classifies students by track × gender × pass. Explain how to read $P(\\text{pass}|\\text{5pt},\\text{female})$ by slicing to a two-way layer.',
      stem_he:
        'טבלה תלת-ממדית מסווגת לפי מסלול × מגדר × עבר. הסבירו איך קוראים $P(\\text{pass}|\\text{5pt},\\text{female})$ על ידי חיתוך לשכבה דו-ממדית.',
      correct_answer: 'fix 5pt layer; female column; pass cell / female total in that layer',
      explanation_en:
        'Fix the third factor (track = 5pt) to get a two-way gender × pass table, then compute the conditional as in a two-way table. Three-way tables are layered two-ways — name the slice explicitly.',
      explanation_he:
        'קבעו את הגורם השלישי (מסלול = 5 יח׳) לקבלת טבלה דו-ממדית מגדר × עבר, ואז חשבו מקרית כרגיל. טבלה תלת-ממדית היא שכבות דו-ממדיות.',
    },
  ]);
  save(lesson);
}

// ─── 5. Bernoulli ────────────────────────────────────────────────────────────
{
  const donor = fs.existsSync(path.join(DIR, 'binomial_distribution_bernoulli.json'))
    ? 'binomial_distribution_bernoulli'
    : 'distributions';
  const lesson = cloneDonor(donor, {
    concept_id: 'probability_bernoulli',
    math_track: ['5pt', 'stats'],
    level_focus: 'Bernoulli trials and binomial setup at MoE depth',
    skill_atom_bank: ['bernoulli', 'binomial', 'p_success', 'independent_trials'],
  });
  rewriteIntro(
    lesson,
    'Bernoulli Trials & Binomial Setup',
    'ניסויי ברנולי והצבה בינומית',
    'A Bernoulli trial is one success/failure with probability $p$. $n$ i.i.d. Bernoulli trials yield a binomial count — set up $n$, $p$, and $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$.',
    'ניסוי ברנולי הוא הצלחה/כישלון עם $p$. $n$ ניסויים בלתי תלויים נותנים ספירה בינומית — מציבים $n$, $p$ ואת $P(X=k)$.',
    `A **Bernoulli trial** has exactly two outcomes: success with probability $p$ and failure with $1-p$. Repeat independently $n$ times: the number of successes $X$ is **binomial**. MoE work is mostly **setup** — identify $n$ and $p$, then write $P(X=k)$ or a cumulative sum.`,
    `**ניסוי ברנולי** הוא הצלחה בהסתברות $p$ וכישלון ב-$1-p$. חזרה בלתי תלויה $n$ פעמים: מספר ההצלחות $X$ הוא **בינומי**. העבודה היא בעיקר **הצבה** — זיהוי $n$ ו-$p$, ואז כתיבת $P(X=k)$.`,
  );
  upsertTheory(lesson, 'BERNOULLI_CORE', {
    kind: 'theory',
    title_en: 'Bernoulli trials and binomial setup',
    title_he: 'ניסויי ברנולי והצבה בינומית',
    body_en_md: `**Bernoulli.** One trial: $P(\\text{success})=p$, $P(\\text{failure})=1-p$. Mean $p$, variance $p(1-p)$.

**Binomial setup.** $n$ independent Bernoulli($p$) trials $\\Rightarrow X\\sim\\mathrm{Bin}(n,p)$ with $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$. Checklist: fixed $n$, same $p$, independence, success/failure coding.`,
    body_he_md: `**ברנולי.** ניסוי אחד: $P(\\text{success})=p$. תוחלת $p$, שונות $p(1-p)$.

**הצבה בינומית.** $n$ ניסויי Bernoulli בלתי תלויים $\\Rightarrow X\\sim\\mathrm{Bin}(n,p)$. רשימת בדיקה: $n$ קבוע, אותו $p$, אי-תלות, קידוד הצלחה/כישלון.`,
  });
  upsertQuestions(lesson, 'probability_bernoulli', [
    {
      kind: 'open',
      difficulty: 'easy',
      facets: ['bernoulli_trials', 'bernoulli'],
      archetypes: ['conceptual', 'procedural'],
      stem_en:
        'A single quiz item is correct with probability $p=0.7$. Model it as a Bernoulli trial: state success, failure, $p$, and $1-p$.',
      stem_he:
        'שאלה במבחן נכונה בהסתברות $p=0.7$. מדלו כניסוי ברנולי: ציינו הצלחה, כישלון, $p$ ו-$1-p$.',
      correct_answer: 'success=correct, p=0.7, failure=0.3',
      explanation_en:
        'Success = correct answer with $p=0.7$; failure = incorrect with $1-p=0.3$. One trial, two outcomes — that is the Bernoulli model.',
      explanation_he:
        'הצלחה = תשובה נכונה עם $p=0.7$; כישלון עם $0.3$. ניסוי אחד, שני תוצאים — זה מודל ברנולי.',
    },
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['binomial_setup', 'binomial'],
      archetypes: ['procedural', 'conceptual'],
      stem_en:
        'A student answers 5 independent true/false items with $P(\\text{correct})=0.5$. Set up $X\\sim\\mathrm{Bin}(n,p)$ and write $P(X=3)$.',
      stem_he:
        'תלמיד עונה על 5 שאלות נכון/לא נכון בלתי תלויות עם $P(\\text{correct})=0.5$. הציבו $X\\sim\\mathrm{Bin}(n,p)$ וכתבו $P(X=3)$.',
      correct_answer: 'Bin(5,0.5); P(X=3)=C(5,3)(0.5)^5',
      explanation_en:
        '$n=5$, $p=0.5$, independence OK. $P(X=3)=\\binom{5}{3}(0.5)^3(0.5)^2=\\binom{5}{3}(0.5)^5$. The binomial setup is naming $n$ and $p$ before computing.',
      explanation_he:
        '$n=5$, $p=0.5$. $P(X=3)=\\binom{5}{3}(0.5)^5$. ההצבה הבינומית היא מתן שם ל-$n$ ו-$p$ לפני החישוב.',
    },
  ]);
  save(lesson);
}

// ─── 6. Even / odd functions ─────────────────────────────────────────────────
{
  const lesson = cloneDonor('functions_intro', {
    concept_id: 'functions_even_odd',
    math_track: ['5pt'],
    level_focus: 'Even and odd functions: definitions, graph tests, integral shortcuts',
    skill_atom_bank: ['even_function', 'odd_function', 'symmetry', 'parity'],
  });
  rewriteIntro(
    lesson,
    'Even & Odd Functions',
    'פונקציות זוגיות ואי-זוגיות',
    'Classify $f$ as even ($f(-x)=f(x)$), odd ($f(-x)=-f(x)$), or neither; read parity from graphs; use shortcuts on symmetric integrals.',
    'מסווגים $f$ כזוגית, אי-זוגית או אף אחת; קוראים זוגיות מהגרף; משתמשים בקיצורי אינטגרלים סימטריים.',
    `A function is **even** when $f(-x)=f(x)$ for all $x$ in a symmetric domain (mirror symmetry about the $y$-axis). It is **odd** when $f(-x)=-f(x)$ (rotational symmetry $180^\\circ$ about the origin). Many exam stems ask you to decide from a formula **or from the graph**, then exploit parity on $[-a,a]$.`,
    `פונקציה **זוגית** מקיימת $f(-x)=f(x)$ (סימטריה ל-$y$). **אי-זוגית** מקיימת $f(-x)=-f(x)$ (סיבוב $180^\\circ$ סביב הראשית). ניסוחי בחינה מבקשים החלטה מהנוסחה **או מהגרף**, ואז ניצול זוגיות ב-$[-a,a]$.`,
  );
  upsertTheory(lesson, 'EVEN_ODD_CORE', {
    kind: 'theory',
    title_en: 'Even function, odd function, parity from graph',
    title_he: 'פונקציה זוגית, אי-זוגית, זוגיות מהגרף',
    body_en_md: `**Even function.** $f(-x)=f(x)$. Graph symmetric about the $y$-axis. Example: $x^2$, $\\cos x$.

**Odd function.** $f(-x)=-f(x)$. Graph symmetric under $180^\\circ$ rotation about the origin. Example: $x^3$, $\\sin x$.

**Parity from graph.** Reflect across $y$-axis — if the graph coincides, even. Rotate $180^\\circ$ about origin — if it coincides, odd. Otherwise neither.

**Integrals.** On $[-a,a]$, odd integrable $f$ gives $0$; even $f$ gives $2\\int_0^a f$.`,
    body_he_md: `**פונקציה זוגית.** $f(-x)=f(x)$. סימטריה ל-$y$.

**פונקציה אי-זוגית.** $f(-x)=-f(x)$. סיבוב $180^\\circ$ סביב הראשית.

**זוגיות מהגרף.** שיקוף ל-$y$ חופף ⟹ זוגית; סיבוב $180^\\circ$ חופף ⟹ אי-זוגית; אחרת אף אחת.

**אינטגרלים.** ב-$[-a,a]$, אי-זוגית נותנת $0$; זוגית נותנת $2\\int_0^a f$.`,
  });
  upsertQuestions(lesson, 'functions_even_odd', [
    {
      kind: 'mcq',
      difficulty: 'easy',
      facets: ['even_function', 'even_parity'],
      archetypes: ['conceptual'],
      stem_en: 'Which equation defines an **even function**?',
      stem_he: 'איזו משוואה מגדירה **פונקציה זוגית**?',
      answer_payload: {
        options_en: ['$f(-x)=f(x)$', '$f(-x)=-f(x)$', '$f(x)=-f(x)$', '$f(x)=f(x+1)$'],
        options_he: ['$f(-x)=f(x)$', '$f(-x)=-f(x)$', '$f(x)=-f(x)$', '$f(x)=f(x+1)$'],
        correct_index: 0,
      },
      explanation_en: 'Even means $f(-x)=f(x)$ on a symmetric domain. Odd is $f(-x)=-f(x)$.',
      explanation_he: 'זוגית פירושה $f(-x)=f(x)$. אי-זוגית היא $f(-x)=-f(x)$.',
    },
    {
      kind: 'true_false',
      difficulty: 'easy',
      facets: ['odd_function', 'odd_parity'],
      archetypes: ['conceptual'],
      stem_en: 'True or false: $f(x)=x^3$ is an odd function because $f(-x)=-f(x)$.',
      stem_he: 'נכון או לא: $f(x)=x^3$ אי-זוגית כי $f(-x)=-f(x)$.',
      answer_payload: { correct: true },
      explanation_en: '$f(-x)=(-x)^3=-x^3=-f(x)$, so $x^3$ is odd.',
      explanation_he: '$f(-x)=-x^3=-f(x)$, ולכן $x^3$ אי-זוגית.',
    },
    {
      kind: 'open',
      difficulty: 'medium',
      facets: ['parity_from_graph'],
      archetypes: ['graphical', 'conceptual'],
      stem_en:
        'From the graph of $y=f(x)$ on a symmetric window, explain how to test even vs odd by $y$-axis reflection vs $180^\\circ$ rotation about the origin.',
      stem_he:
        'מהגרף של $y=f(x)$ בחלון סימטרי, הסבירו איך בודקים זוגית מול אי-זוגית בשיקוף ל-$y$ מול סיבוב $180^\\circ$ סביב הראשית.',
      correct_answer: 'reflect across y → even; rotate 180 about O → odd',
      explanation_en:
        'Parity from graph: if reflecting across the $y$-axis leaves the graph unchanged, $f$ is even. If rotating $180^\\circ$ about the origin leaves it unchanged, $f$ is odd. If neither, the function is neither even nor odd — do not force a label.',
      explanation_he:
        'זוגיות מהגרף: שיקוף ל-$y$ שלא משנה את הגרף ⟹ זוגית. סיבוב $180^\\circ$ סביב הראשית שלא משנה ⟹ אי-זוגית. אחרת — אף אחת.',
    },
  ]);
  save(lesson);
}

// ─── 7. Scrub conics cone framing ────────────────────────────────────────────
{
  const lesson = load('analytic_geometry_conics');
  rewriteIntro(
    lesson,
    'Analytic Geometry — Parabola & Ellipse (MoE Overview)',
    'גאומטריה אנליטית — פרבולה ואליפסה (סקירת תוכנית)',
    'Overview of parabola (focus–directrix) and ellipse (two foci, $2a$) in Cartesian form. Prefer dedicated lessons for depth. No cone-cutting narrative.',
    'סקירת פרבולה (מוקד–מכוון) ואליפסה (שני מוקדים, $2a$) בצורה קרטזית. להעמקה העדיפו את השיעורים הייעודיים. בלי חיתוך חרוט.',
    `This overview collects **parabola** and **ellipse** as quadratic curves defined by **focus–directrix** and **two-foci** distance conditions. For full MoE practice, study \`analytic_geometry_parabola\` and \`analytic_geometry_ellipse\`. We do **not** introduce these curves by cutting a cone.`,
    `סקירה זו אוספת **פרבולה** ו**אליפסה** כעקומים ריבועיים המוגדרים ב**מוקד–מכוון** וב**שני מוקדים**. לתרגול מלא למדו את השיעורים הייעודיים. **אין** הצגה כחיתוך חרוט.`,
  );
  for (const s of lesson.sections || []) {
    for (const k of ['body_en_md', 'body_he_md', 'title_en', 'title_he', 'summary_en', 'summary_he']) {
      if (!s[k]) continue;
      s[k] = s[k]
        .replace(/conic section/gi, 'quadratic curve')
        .replace(/Conic/g, 'Quadratic curve')
        .replace(/conic/g, 'quadratic curve')
        .replace(/cutting (a |the )?cone/gi, 'using focus–directrix or two-foci definitions')
        .replace(/double[- ]napped cone/gi, 'focus–directrix / two-foci definition')
        .replace(/חתך חרוט/g, 'עקום ריבועי')
        .replace(/חותכים חרוט/g, 'מגדירים במוקד ומכוון או בשני מוקדים')
        .replace(/חרוט כפול/g, 'הגדרת מוקד–מכוון')
        .replace(/חרוט/g, 'עקום');
    }
  }
  for (const k of ['summary_en', 'summary_he', 'title_en', 'title_he']) {
    if (!lesson[k]) continue;
    lesson[k] = lesson[k]
      .replace(/conic section/gi, 'quadratic curve')
      .replace(/Conics/g, 'Parabola & Ellipse')
      .replace(/חתך חרוט/g, 'עקום ריבועי');
  }
  upsertTheory(lesson, 'CONICS_SCRUB_MOE', {
    kind: 'theory',
    title_en: 'MoE framing: focus–directrix and foci — not cone sections',
    title_he: 'מסגרת התוכנית: מוקד–מכוון ומוקדים — לא חתכי חרוט',
    body_en_md: `Israeli MoE analytic geometry treats the **parabola** via focus and directrix and the **ellipse** via $|PF_1|+|PF_2|=2a$. Standard Cartesian forms follow. Cone-cutting language is out of scope for the questionnaire — use the dedicated parabola and ellipse lessons for exam archetypes.`,
    body_he_md: `בגאומטריה אנליטית בתוכנית מטפלים ב**פרבולה** דרך מוקד ומכוון וב**אליפסה** דרך $|PF_1|+|PF_2|=2a$. אחר כך צורות קרטזיות. שפת חיתוך חרוט מחוץ להיקף השאלון — השתמשו בשיעורים הייעודיים לארכיטיפים.`,
  });
  save(lesson);
}

console.log('author-exam-gap-lessons: done');
