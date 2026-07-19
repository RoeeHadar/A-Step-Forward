/**
 * Depth metrics for authored lessons (sections + questions + exercises).
 */

import { acceptableAnswersLookBroken, agentHintsIsStructured } from './normalize-lesson.mjs';

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
  // Severe parity: genuine truncation/missing Hebrew, not mere compactness.
  // Hebrew prose typically runs ~70-85% of English word count for the same
  // content, so the rewrite bar uses a looser 0.6 ratio to catch real gaps only.
  let heParitySevere = 0;

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
    if (PARITY_KINDS.has(s.kind) && en >= 60 && he < en * 0.6) heParitySevere += 1;
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

  // --- rewrite-bar metrics (per-lesson depth floors + archetype breadth) ---
  const theoryCount = sections.filter((s) => s.kind === 'theory').length;
  const workedExampleCount = sections.filter((s) => s.kind === 'worked_example').length;
  const questionDifficulties = new Set(
    questions.map((q) => q.difficulty).filter((d) => typeof d === 'string'),
  );
  // Question archetypes: explicit `q.archetypes` / `q.archetype` tag if present,
  // else inferred from the (canonical) question kind. Keys MUST match Q_KINDS in
  // normalize-lesson.mjs. Graphical/application/parametric archetypes have no
  // dedicated kind, so they are only picked up from explicit tags.
  const KIND_TO_ARCHETYPE = {
    numeric: 'procedural',
    short_answer: 'procedural',
    fill_blank: 'procedural',
    mcq: 'conceptual',
    mcq_multi: 'conceptual',
    true_false: 'conceptual',
    ordering: 'conceptual',
    match: 'conceptual',
    open: 'conceptual',
    derivation: 'proof',
  };
  const archetypes = new Set();
  for (const q of questions) {
    if (Array.isArray(q.archetypes)) q.archetypes.forEach((a) => archetypes.add(a));
    else if (typeof q.archetype === 'string') archetypes.add(q.archetype);
    else if (q.kind && KIND_TO_ARCHETYPE[q.kind]) archetypes.add(KIND_TO_ARCHETYPE[q.kind]);
  }

  // Question-bank health (question-store readiness).
  const distinctKinds = new Set(questions.map((q) => q.kind)).size;
  const questionsWithAtoms = questions.filter(
    (q) => Array.isArray(q.skill_atoms) && q.skill_atoms.length > 0,
  ).length;
  const brokenPayloads = questions.filter(
    (q) => q.kind === 'short_answer' && acceptableAnswersLookBroken(q.answer_payload?.acceptable_answers),
  ).length;
  const agentHintsStructured = agentHintsIsStructured(raw.agent_hints);

  return {
    concept_id: raw.concept_id ?? raw.id,
    totalSectionWords,
    shallowSections,
    heParityFails,
    heParitySevere,
    questionCount: questions.length,
    avgExplanationWords: avgExpl,
    shortExplanationPct: shortExplPct,
    exerciseCount: exerciseTotal,
    shortExerciseSolutions,
    hasWhyMatters,
    distinctKinds,
    questionsWithAtoms,
    brokenPayloads,
    agentHintsStructured,
    theoryCount,
    workedExampleCount,
    difficultySpread: questionDifficulties.size,
    hasEasy: questionDifficulties.has('easy'),
    hasMedium: questionDifficulties.has('medium'),
    hasHard: questionDifficulties.has('hard'),
    archetypeCount: archetypes.size,
    hasGraphical: archetypes.has('graphical'),
  };
}

/**
 * Phase 6 — the lesson-rewrite bar, applied PER-LESSON (not corpus average) to
 * lessons on the rewrite allowlist. Encodes the depth floors + archetype breadth
 * from docs/curriculum/lesson-rewrite-scope-map.md §1.4 / §2.
 * Returns { pass, lessons: [{ file, pass, reasons[] }] }.
 */
export function phase6PerLesson(metric) {
  const reasons = [];
  if (metric.totalSectionWords < 1800)
    reasons.push(`section words ${metric.totalSectionWords} < 1800`);
  if (metric.theoryCount < 2) reasons.push(`theory sections ${metric.theoryCount} < 2`);
  if (metric.workedExampleCount < 4)
    reasons.push(`worked examples ${metric.workedExampleCount} < 4`);
  if (metric.questionCount < 25) reasons.push(`questions ${metric.questionCount} < 25`);
  if (metric.distinctKinds < 6) reasons.push(`question kinds ${metric.distinctKinds} < 6`);
  if (!(metric.hasEasy && metric.hasMedium && metric.hasHard))
    reasons.push('missing easy/medium/hard difficulty spread');
  if (metric.avgExplanationWords < 40)
    reasons.push(`avg explanation words ${metric.avgExplanationWords.toFixed(0)} < 40`);
  if (!metric.hasWhyMatters) reasons.push('missing why_matters');
  if (metric.heParitySevere > 0)
    reasons.push(`${metric.heParitySevere} section(s) with truncated Hebrew (< 60% of EN)`);
  if (metric.archetypeCount < 4) reasons.push(`question archetypes ${metric.archetypeCount} < 4`);
  if (metric.brokenPayloads > 0) reasons.push(`${metric.brokenPayloads} broken answer payloads`);
  if (!metric.agentHintsStructured) reasons.push('agent_hints not structured');
  return { pass: reasons.length === 0, reasons };
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

/**
 * Phase 5 — question-bank readiness (the lesson-corpus-rewrite pilot bar).
 * Applied to pilot / touched lessons, not the grandfathered corpus.
 */
export function phase5Gates(metricsList) {
  const n = metricsList.length || 1;
  const brokenTotal = metricsList.reduce((s, m) => s + (m.brokenPayloads ?? 0), 0);
  const unstructuredHints = metricsList.filter((m) => !m.agentHintsStructured).length;
  const lowVariety = metricsList.filter((m) => (m.distinctKinds ?? 0) < 3).length;
  const atomCoverage =
    metricsList.reduce(
      (s, m) => s + (m.questionCount > 0 ? (m.questionsWithAtoms ?? 0) / m.questionCount : 0),
      0,
    ) / n;

  return {
    pass: brokenTotal === 0 && unstructuredHints === 0 && lowVariety === 0 && atomCoverage >= 0.9,
    brokenPayloadTotal: brokenTotal,
    lessonsWithUnstructuredHints: unstructuredHints,
    lessonsWithLowKindVariety: lowVariety,
    avgQuestionAtomCoverage: atomCoverage,
  };
}
