#!/usr/bin/env node
/**
 * Author the five deliberate calc-1 catalog stubs as real university lessons.
 * Usage: node scripts/author-calc1-stubs.mjs
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
  if (lesson.sections.some((s) => (s.body_en_md || '').includes(marker))) return;
  const insert = { ...section, body_en_md: `<!-- ${marker} -->\n${section.body_en_md}` };
  const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
  if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
  else lesson.sections.push(insert);
}

const SPECS = [
  {
    id: 'extreme_value_theorem',
    donor: 'absolute_extrema',
    title_en: 'Extreme Value Theorem',
    title_he: 'משפט ערך קיצון',
    summary_en:
      'A continuous function on a closed interval attains its absolute max and min. Course-exam use: guarantee extrema, then locate via critical points and endpoints.',
    summary_he:
      'פונקציה רציפה בקטע סגור משיגה מקסימום ומינימום מוחלטים. שימוש במבחן: הבטחת קיצון, ואז איתור בנקודות קריטיות ובקצוות.',
    intro_en:
      'The **extreme value theorem (EVT)** says: if $f$ is continuous on $[a,b]$, then there exist $c,d\\in[a,b]$ with $f(c)\\le f(x)\\le f(d)$ for all $x\\in[a,b]$. Continuity on a compact interval is essential — drop either hypothesis and the conclusion can fail.',
    intro_he:
      '**משפט ערך הקיצון (EVT):** אם $f$ רציפה ב-$[a,b]$, קיימים $c,d\\in[a,b]$ כך ש-$f(c)\\le f(x)\\le f(d)$ לכל $x$ בקטע. רציפות בקטע קומפקטי חיונית — הסרת אחת מההנחות עלולה לשבור את המסקנה.',
    theory_title_en: 'EVT hypotheses and exam workflow',
    theory_title_he: 'הנחות EVT וזרימת עבודה במבחן',
    theory_en:
      '**Hypotheses.** Continuity on $[a,b]$ (closed and bounded). **Workflow.** (1) Cite EVT to know extrema exist. (2) Compute $f\'=0$ / undefined critical points in $(a,b)$. (3) Evaluate $f$ at critical points and endpoints. (4) Compare values.',
    theory_he:
      '**הנחות.** רציפות ב-$[a,b]$. **זרימה.** (1) ציטוט EVT. (2) נקודות קריטיות. (3) הערכה בקריטיות ובקצוות. (4) השוואת ערכים.',
  },
  {
    id: 'intermediate_value_theorem',
    donor: 'continuity',
    title_en: 'Intermediate Value Theorem',
    title_he: 'משפט ערך הביניים',
    summary_en:
      'A continuous function on $[a,b]$ hits every value between $f(a)$ and $f(b)$. Used to prove roots exist and to justify bisection.',
    summary_he:
      'פונקציה רציפה ב-$[a,b]$ פוגעת בכל ערך בין $f(a)$ ל-$f(b)$. משמש להוכחת קיום שורש ולביסוס חצייה.',
    intro_en:
      'The **intermediate value theorem (IVT)**: if $f$ is continuous on $[a,b]$ and $k$ lies between $f(a)$ and $f(b)$, then some $c\\in[a,b]$ satisfies $f(c)=k$. Classic root test: if $f(a)$ and $f(b)$ have opposite signs, a root exists in $(a,b)$.',
    intro_he:
      '**משפט ערך הביניים (IVT):** אם $f$ רציפה ב-$[a,b]$ ו-$k$ בין $f(a)$ ל-$f(b)$, קיים $c$ עם $f(c)=k$. מבחן שורש קלאסי: סימנים מנוגדים בקצוות ⟹ שורש בקטע.',
    theory_title_en: 'IVT for roots and value-hitting',
    theory_title_he: 'IVT לשורשים ולפגיעת ערכים',
    theory_en:
      '**Root corollary.** $f(a)f(b)<0$ and continuity $\\Rightarrow$ a root in $(a,b)$. **Value-hitting.** Any intermediate height is attained. Continuity is necessary — step functions can skip values.',
    theory_he:
      '**מסקנת שורש.** $f(a)f(b)<0$ ורציפות ⟹ שורש. **פגיעת ערך.** כל גובה ביניים מושג. רציפות הכרחית.',
  },
  {
    id: 'sequences_monotone_bounded',
    donor: 'limits_epsilon_delta',
    title_en: 'Monotone Bounded Sequences',
    title_he: 'סדרות מונוטוניות חסומות',
    summary_en:
      'A monotone bounded real sequence converges. Course tool for proving existence of limits without an explicit closed form.',
    summary_he:
      'סדרה מונוטונית חסומה מתכנסת. כלי להוכחת קיום גבול בלי נוסחה סגורה.',
    intro_en:
      '**Monotone convergence theorem:** an increasing sequence bounded above (or decreasing bounded below) converges to a finite limit. Bounded + monotone $\\Rightarrow$ convergent — the standard existence hammer in Calc 1 sequences.',
    intro_he:
      '**משפט התכנסות מונוטונית:** סדרה עולה וחסומה מלמעלה (או יורדת וחסומה מלמטה) מתכנסת. חסומה + מונוטונית ⟹ מתכנסת.',
    theory_title_en: 'Monotone + bounded ⇒ convergent',
    theory_title_he: 'מונוטונית + חסומה ⟹ מתכנסת',
    theory_en:
      'Prove $a_{n+1}\\ge a_n$ (or $\\le$) and exhibit an upper (lower) bound $M$. Conclude $\\lim a_n$ exists. Often the limit $L$ solves an equation obtained by passing to the limit in a recurrence.',
    theory_he:
      'הוכיחו מונוטוניות וחסם, הסיקו שקיים גבול. לעיתים $L$ פותר משוואה מהנוסחה הנסיגה.',
  },
  {
    id: 'series_absolute_convergence',
    donor: 'series_convergence_tests',
    title_en: 'Absolute Convergence of Series',
    title_he: 'התכנסות בהחלט של טורים',
    summary_en:
      'Absolute convergence ($\\sum|a_n|<\\infty$) implies convergence; conditional convergence is the gap case. Ratio/root tests target absolute convergence.',
    summary_he:
      'התכנסות בהחלט ($\\sum|a_n|<\\infty$) גוררת התכנסות; התכנסות בתנאי היא מקרה הביניים. מבחני יחס/שורש מכוונים להתכנסות בהחלט.',
    intro_en:
      'A series $\\sum a_n$ **converges absolutely** when $\\sum|a_n|$ converges. Absolute convergence $\\Rightarrow$ ordinary convergence. If $\\sum a_n$ converges but $\\sum|a_n|$ diverges, the convergence is **conditional**.',
    intro_he:
      'טור **מתכנס בהחלט** כאשר $\\sum|a_n|$ מתכנס. התכנסות בהחלט ⟹ התכנסות רגילה. אם $\\sum a_n$ מתכנס אבל $\\sum|a_n|$ מתבדר — **התכנסות בתנאי**.',
    theory_title_en: 'Absolute vs conditional; tests',
    theory_title_he: 'בהחלט מול בתנאי; מבחנים',
    theory_en:
      'Ratio and root tests, when conclusive, prove absolute convergence. Alternating series may converge conditionally — check $\\sum|a_n|$ separately.',
    theory_he:
      'מבחני יחס ושורש, כשהם חד-משמעיים, מוכיחים התכנסות בהחלט. טורים מתחלפים עשויים להתכנס בתנאי.',
  },
  {
    id: 'convergence_divergence_integrals',
    donor: 'improper_integrals',
    title_en: 'Convergence & Divergence of Improper Integrals',
    title_he: 'התכנסות והתבדרות של אינטגרלים מוכללים',
    summary_en:
      'Classify $\\int_a^\\infty f$ and $\\int_a^b$ with endpoint singularities as convergent or divergent via limits of proper integrals and comparison.',
    summary_he:
      'מסווגים $\\int_a^\\infty f$ ואינטגרלים עם סינגולריות בקצה כמתכנסים או מתבדרים דרך גבולות של אינטגרלים רגילים והשוואה.',
    intro_en:
      'An improper integral **converges** when the defining limit of proper integrals exists and is finite; otherwise it **diverges**. Split at singularities; compare with $p$-integrals.',
    intro_he:
      'אינטגרל מוכלל **מתכנס** כאשר גבול האינטגרלים הרגילים קיים וסופי; אחרת **מתבדר**. פצלו בסינגולריות; השוו לאינטגרלי $p$.',
    theory_title_en: 'Limit definition and comparison',
    theory_title_he: 'הגדרת גבול והשוואה',
    theory_en:
      'Write $\\int_a^\\infty f=\\lim_{B\\to\\infty}\\int_a^B f$. For $\\int_0^1 x^{-p}\\,dx$, converge iff $p<1$. Use comparison and limit-comparison with known $p$-integrals.',
    theory_he:
      'כתבו גבול של אינטגרלים רגילים. ל-$\\int_0^1 x^{-p}$, התכנסות אמ״ם $p<1$. השתמשו בהשוואה.',
  },
];

for (const spec of SPECS) {
  if (fs.existsSync(path.join(DIR, `${spec.id}.json`))) {
    console.log('skip existing', spec.id);
    continue;
  }
  const lesson = structuredClone(load(spec.donor));
  lesson.concept_id = spec.id;
  lesson.math_track = ['university', 'calc1'];
  lesson.level = 'advanced';
  lesson.title_en = spec.title_en;
  lesson.title_he = spec.title_he;
  lesson.summary_en = spec.summary_en;
  lesson.summary_he = spec.summary_he;
  lesson.version = (Number(lesson.version) || 1) + 1;
  lesson.author = 'wave3-calc1-stubs';
  const intro = lesson.sections?.find((s) => s.kind === 'intro');
  if (intro) {
    intro.title_en = spec.title_en;
    intro.title_he = spec.title_he;
    intro.body_en_md = spec.intro_en;
    intro.body_he_md = spec.intro_he;
  }
  upsertTheory(lesson, `STUB_CORE_${spec.id}`, {
    kind: 'theory',
    title_en: spec.theory_title_en,
    title_he: spec.theory_title_he,
    body_en_md: spec.theory_en,
    body_he_md: spec.theory_he,
  });
  // Ensure easy question mentioning the theorem name for discoverability
  lesson.questions = lesson.questions || [];
  lesson.questions.push({
    id: `${spec.id}-core-1`,
    ord: lesson.questions.length + 1,
    kind: 'open',
    difficulty: 'medium',
    archetypes: ['conceptual', 'proof'],
    stem_en: `State the main theorem of this lesson (${spec.title_en}) with hypotheses and conclusion, then give one exam-style application.`,
    stem_he: `נסחו את המשפט המרכזי של השיעור (${spec.title_he}) עם הנחות ומסקנה, ותנו יישום אחד בסגנון מבחן.`,
    correct_answer: 'see theory section',
    explanation_en: `Recall the hypotheses carefully, write the conclusion, then apply it once (existence, classification, or computation) as in the theory section.`,
    explanation_he: `הזכירו את ההנחות, כתבו את המסקנה, ויישמו פעם אחת כבחלק התיאוריה.`,
    skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
  });
  save(lesson);
}

console.log('author-calc1-stubs: done');
