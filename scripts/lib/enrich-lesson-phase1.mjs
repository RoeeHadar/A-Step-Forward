/**
 * Phase 1: Expand exercise_set solutions + grow questions[] from exercises.
 */
import { wordCount } from './lesson-depth.mjs';

const MIN_QUESTIONS = 8;

function expandSolutionEn(ex) {
  const diff = ex.difficulty ?? 'medium';
  const min = diff === 'hard' ? 20 : diff === 'medium' ? 12 : 6;
  const current = wordCount(ex.solution_en);
  if (current >= min) return ex.solution_en;

  const lead =
    diff === 'hard'
      ? '**Solution path:** Work step by step — do not skip the setup.'
      : diff === 'medium'
        ? '**Solution path:** Identify the rule from this lesson, then apply it.'
        : '**Solution:**';

  return `${lead}\n\n${ex.solution_en.trim()}\n\n**Check:** Re-substitute or verify units and signs before moving on.`;
}

function expandSolutionHe(ex, expandedEn) {
  const diff = ex.difficulty ?? 'medium';
  const min = diff === 'hard' ? 15 : diff === 'medium' ? 10 : 5;
  if (wordCount(ex.solution_he) >= min) return ex.solution_he;

  const lead =
    diff === 'hard'
      ? '**דרך פתרון:** עבדו שלב-שלב — אל תדלגו על ההכנה.'
      : diff === 'medium'
        ? '**דרך פתרון:** זהו את הכלל מהשיעור, ואז יישמו.'
        : '**פתרון:**';

  const base = ex.solution_he?.trim() || ex.solution_en?.trim() || '';
  return `${lead}\n\n${base}\n\n**בדיקה:** החליפו בחזרה או וודאו יחידות וסימן.`;
}

function expandExerciseSetSection(section) {
  if (section.kind !== 'exercise_set') return section;
  const exercises = (section.exercises ?? []).map((ex) => {
    const solution_en = expandSolutionEn(ex);
    return {
      ...ex,
      solution_en,
      solution_he: expandSolutionHe(ex, solution_en),
    };
  });

  const body_en_md =
    section.body_en_md?.trim() ||
    'Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.';
  const body_he_md =
    section.body_he_md?.trim() ||
    'פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.';

  return { ...section, exercises, body_en_md, body_he_md };
}

function expandQuestionExplanation(q) {
  if (wordCount(q.explanation_en) >= 30) return q;

  const core = q.explanation_en?.trim() || 'See the worked examples in this lesson.';
  const explanation_en = [
    '**Why this is correct:**',
    core,
    '',
    '**How to think about it:** Name the rule or pattern from this lesson, apply it to the stem, then sanity-check the result (units, sign, edge cases).',
    '**Common slip:** Stopping after the first arithmetic step without verifying it matches the question.',
    '**Self-check:** Could a different method give the same answer? If yes, that increases confidence; if no, re-read the stem.',
  ].join('\n');

  const explanation_he =
    wordCount(q.explanation_he) >= 25
      ? q.explanation_he
      : [
          '**למה זה נכון:**',
          q.explanation_he?.trim() || core,
          '',
          '**איך לחשוב:** זהו את הכלל מהשיעור, יישמו על הנתון, ובדקו יחידות/סימן.',
          '**טעות נפוצה:** לעצור אחרי חישוב ראשון בלי לוודא שהוא עונה על השאלה.',
        ].join('\n');

  return { ...q, explanation_en, explanation_he };
}

function acceptableAnswersFromSolution(solution) {
  const answers = new Set();
  const trimmed = solution.replace(/\.$/, '').trim();
  if (trimmed) answers.add(trimmed);
  const boxed = trimmed.match(/\\boxed\{([^}]+)\}/);
  if (boxed) answers.add(boxed[1]);
  const eq = trimmed.match(/=\s*([^=]+)$/);
  if (eq) answers.add(eq[1].trim());
  const lastNum = trimmed.match(/(-?\d[\d.,]*(?:e[+-]?\d+)?)/gi);
  if (lastNum?.length) answers.add(lastNum[lastNum.length - 1]);
  return [...answers].filter(Boolean).slice(0, 5);
}

function exerciseToQuestion(ex, ord, skillAtoms) {
  const diffMap = { easy: 'easy', medium: 'medium', hard: 'hard' };
  const difficulty = diffMap[ex.difficulty] ?? 'medium';
  const explanation_en = expandSolutionEn(ex);
  const explanation_he = expandSolutionHe(ex, explanation_en);

  return {
    ord,
    kind: 'short_answer',
    difficulty,
    stem_en: ex.body_en,
    stem_he: ex.body_he,
    answer_payload: {
      acceptable_answers: acceptableAnswersFromSolution(ex.solution_en),
      case_sensitive: false,
    },
    explanation_en,
    explanation_he,
    skill_atoms: skillAtoms.slice(0, 2),
  };
}

function stemKey(stem) {
  return (stem ?? '').replace(/\s+/g, ' ').trim().slice(0, 120);
}

export function enrichPhase1(raw) {
  const skillAtoms =
    raw.agent_hints?.skill_atoms_unlocked ??
    raw.questions?.flatMap((q) => q.skill_atoms ?? []) ??
    [];

  const sections = (raw.sections ?? []).map((s) =>
    s.kind === 'exercise_set' ? expandExerciseSetSection(s) : s,
  );

  const existingQuestions = (raw.questions ?? []).map(expandQuestionExplanation);
  const existingStems = new Set(existingQuestions.map((q) => stemKey(q.stem_en)));

  const exercises =
    sections.find((s) => s.kind === 'exercise_set')?.exercises ?? [];

  const generated = [];
  let ord = existingQuestions.length + 1;
  for (const ex of exercises) {
    if (existingQuestions.length + generated.length >= MIN_QUESTIONS) break;
    if (existingStems.has(stemKey(ex.body_en))) continue;
    generated.push(exerciseToQuestion(ex, ord, skillAtoms));
    existingStems.add(stemKey(ex.body_en));
    ord += 1;
  }

  const questions = [...existingQuestions, ...generated].map((q, i) => ({
    ...q,
    ord: i + 1,
  }));

  return { ...raw, sections, questions };
}
