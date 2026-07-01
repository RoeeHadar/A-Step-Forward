/**
 * Depth metrics for authored lessons (sections + questions + exercises).
 */

export function wordCount(text) {
  if (!text || typeof text !== 'string') return 0;
  const stripped = text
    .replace(/\$\$[\s\S]*?\$\$/g, ' MATH ')
    .replace(/\$[^$\n]+\$/g, ' MATH ')
    .replace(/[#*_`>\[\]()]/g, ' ');
  return stripped.split(/\s+/).filter((w) => w.length > 0).length;
}

const SECTION_TEXT_KINDS = new Set([
  'intro',
  'definition',
  'theory',
  'worked_example',
  'checkpoint',
  'method_guide',
  'pitfall',
  'before_exam',
  'summary',
  'why_matters',
]);

const PARITY_KINDS = new Set([
  'intro',
  'definition',
  'theory',
  'worked_example',
  'pitfall',
  'method_guide',
  'why_matters',
]);

export function sectionWords(section) {
  return wordCount(section.body_en_md) + wordCount(section.body_he_md);
}

export function sectionEnWords(section) {
  return wordCount(section.body_en_md);
}

export function sectionHeWords(section) {
  return wordCount(section.body_he_md);
}

export function lessonMetrics(raw) {
  const sections = raw.sections ?? [];
  const questions = raw.questions ?? [];
  const exercises = sections.find((s) => s.kind === 'exercise_set')?.exercises ?? [];

  let totalSectionWords = 0;
  let shallowSections = 0;
  let heParityFails = 0;

  for (const s of sections) {
    if (!SECTION_TEXT_KINDS.has(s.kind)) continue;
    const en = sectionEnWords(s);
    const he = sectionHeWords(s);
    totalSectionWords += en + he;
    const shallowKinds = new Set([
      'intro',
      'definition',
      'theory',
      'worked_example',
      'pitfall',
      'method_guide',
      'why_matters',
    ]);
    if (shallowKinds.has(s.kind) && en > 0 && en < 80) shallowSections += 1;
    if (PARITY_KINDS.has(s.kind) && en >= 60 && he < en * 0.85) heParityFails += 1;
  }

  const explWords = questions.map((q) => wordCount(q.explanation_en));
  const avgExpl =
    explWords.length > 0 ? explWords.reduce((a, b) => a + b, 0) / explWords.length : 0;
  const shortExplPct =
    explWords.length > 0
      ? (explWords.filter((w) => w < 30).length / explWords.length) * 100
      : 100;

  let shortExerciseSolutions = 0;
  let exerciseTotal = 0;
  for (const ex of exercises) {
    exerciseTotal += 1;
    const min = ex.difficulty === 'hard' ? 20 : ex.difficulty === 'medium' ? 12 : 6;
    if (wordCount(ex.solution_en) < min) shortExerciseSolutions += 1;
  }

  const hasWhyMatters = sections.some((s) => s.kind === 'why_matters');

  return {
    concept_id: raw.concept_id ?? raw.id,
    totalSectionWords,
    shallowSections,
    heParityFails,
    questionCount: questions.length,
    avgExplanationWords: avgExpl,
    shortExplanationPct: shortExplPct,
    exerciseCount: exerciseTotal,
    shortExerciseSolutions,
    hasWhyMatters,
  };
}

/** Phase 1 acceptance gates (corpus aggregates). */
export function phase1Gates(metricsList) {
  const n = metricsList.length || 1;
  const avgQ = metricsList.reduce((s, m) => s + m.questionCount, 0) / n;
  const zeroQ = metricsList.filter((m) => m.questionCount === 0).length;
  const avgExpl =
    metricsList.reduce((s, m) => s + m.avgExplanationWords, 0) / n;
  const shortExPct =
    metricsList.reduce((s, m) => s + m.shortExerciseSolutions, 0) /
    Math.max(
      1,
      metricsList.reduce((s, m) => s + m.exerciseCount, 0),
    );

  return {
    pass:
      avgQ >= 7 &&
      zeroQ === 0 &&
      avgExpl >= 25 &&
      shortExPct <= 0.15,
    avgQuestions: avgQ,
    lessonsWithZeroQuestions: zeroQ,
    avgExplanationWords: avgExpl,
    shortExerciseSolutionRate: shortExPct,
  };
}

export function phase2Gates(metricsList) {
  const n = metricsList.length || 1;
  const avgWords = metricsList.reduce((s, m) => s + m.totalSectionWords, 0) / n;
  const avgShallow = metricsList.reduce((s, m) => s + m.shallowSections, 0) / n;

  return {
    pass: avgWords >= 1100 && avgShallow <= 2.5,
    avgSectionWords: avgWords,
    avgShallowSections: avgShallow,
  };
}

export function phase3Gates(metricsList) {
  const n = metricsList.length || 1;
  const avgParityFails =
    metricsList.reduce((s, m) => s + m.heParityFails, 0) / n;

  return {
    pass: avgParityFails <= 0.5,
    avgHeParityFails: avgParityFails,
  };
}

export function phase4Gates(metricsList) {
  const withWhy = metricsList.filter((m) => m.hasWhyMatters).length;
  const pct = (withWhy / metricsList.length) * 100;

  return {
    pass: pct >= 85,
    whyMattersPct: pct,
    withWhyMatters: withWhy,
    total: metricsList.length,
  };
}
