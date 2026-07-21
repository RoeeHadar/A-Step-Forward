/**
 * Strip answer keys from attempt snapshots until grading is complete.
 * Pending/grading/failed client reads must not leak `correct`.
 */
export function redactQuestionsUntilGraded<
  T extends { correct: string },
>(questions: T[], gradingStatus: string | undefined): T[] {
  if (gradingStatus === 'complete') return questions;
  return questions.map((q) => ({ ...q, correct: '' }));
}
