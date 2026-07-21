/**
 * Strip answer keys / solutions from attempt snapshots until grading is complete.
 * Pending/grading/failed client reads must not leak `correct`, `model_answer`, or `rubric`.
 */
export type RedactableQuestion = {
  correct: string;
  model_answer?: unknown;
  rubric?: unknown;
};

export function redactQuestionsUntilGraded<T extends RedactableQuestion>(
  questions: T[],
  gradingStatus: string | undefined,
): T[] {
  if (gradingStatus === 'complete') return questions;
  return questions.map((q) => {
    const next = { ...q, correct: '' };
    delete (next as RedactableQuestion).model_answer;
    delete (next as RedactableQuestion).rubric;
    return next;
  });
}
