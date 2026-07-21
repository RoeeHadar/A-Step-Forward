/**
 * Pure helpers for custom-quiz client stripping / reveal (no Neon).
 */
import type { CustomQuizEnvelope, CustomQuizQuestion } from '@/lib/quiz-builder';

export type CustomQuizQuestionPublic = Omit<
  CustomQuizQuestion,
  | 'sample_solution_en'
  | 'sample_solution_he'
  | 'rubric_en'
  | 'rubric_he'
  | 'correct_index'
  | 'explanation_en'
  | 'explanation_he'
> & { id: string };

export type CustomQuizEnvelopePublic = Omit<CustomQuizEnvelope, 'questions'> & {
  questions: CustomQuizQuestionPublic[];
};

export type CustomQuizReveal = Record<
  string,
  {
    sample_solution_en: string;
    sample_solution_he: string;
    rubric_en: string;
    rubric_he: string;
    correct_index?: number;
    explanation_en?: string;
    explanation_he?: string;
  }
>;

export type StoredCustomQuestion = CustomQuizQuestion & { id: string };

export function stripCustomQuizForClient(
  envelope: CustomQuizEnvelope & { questions: StoredCustomQuestion[] },
): CustomQuizEnvelopePublic {
  return {
    quiz_id: envelope.quiz_id,
    kind_mix: envelope.kind_mix,
    mode: envelope.mode,
    time_limit_s: envelope.time_limit_s,
    concepts: envelope.concepts,
    picked_reason: envelope.picked_reason,
    model: envelope.model,
    questions: envelope.questions.map((q: StoredCustomQuestion) => ({
      id: q.id,
      ord: q.ord,
      kind: q.kind,
      difficulty: q.difficulty,
      concept_id: q.concept_id,
      skill_atoms: q.skill_atoms,
      stem_en: q.stem_en,
      stem_he: q.stem_he,
      parts: q.parts,
      total_points: q.total_points,
      options_en: q.options_en,
      options_he: q.options_he,
    })),
  };
}

export function buildRevealMap(questions: StoredCustomQuestion[]): CustomQuizReveal {
  const reveal: CustomQuizReveal = {};
  for (const q of questions) {
    reveal[q.id] = {
      sample_solution_en: q.sample_solution_en,
      sample_solution_he: q.sample_solution_he,
      rubric_en: q.rubric_en,
      rubric_he: q.rubric_he,
      correct_index: q.correct_index,
      explanation_en: q.explanation_en,
      explanation_he: q.explanation_he,
    };
  }
  return reveal;
}

/** Pure helper for tests: forged client keys must not affect closed scores. */
export function gradeClosedFromStoredOnly(
  stored: { kind: string; correct_index?: number },
  chosen: string,
): number {
  if (stored.kind !== 'mcq' || typeof stored.correct_index !== 'number') return 0;
  const letter = String.fromCharCode(65 + stored.correct_index);
  return chosen.trim().toUpperCase() === letter ? 1 : 0;
}
