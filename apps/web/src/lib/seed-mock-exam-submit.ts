/**
 * Persist a completed *seed* mock exam (open-ended catalog at /app/quiz/mock-exam).
 * Unlike LLM mock exams, these are not auto-graded — we archive the attempt so
 * Progress / My Tests / Memory update, with score=0 until a dedicated grader lands.
 */
import 'server-only';
import { appendLearnerPersonaLine } from './neon-db';
import { getMockExamById } from './mock-exam-catalog';
import { MOCK_PASS_THRESHOLD } from './mock-exam';
import { recordTestAttempt } from './test-attempts';

export interface SeedMockExamSubmitResult {
  attempt_id: string | null;
  exam_id: string;
  questions_answered: number;
  questions_total: number;
}

export async function submitSeedMockExam(
  learnerId: string,
  examId: string,
  answers: Record<string, string>,
  locale: 'he' | 'en' = 'he',
): Promise<SeedMockExamSubmitResult | null> {
  const exam = getMockExamById(examId);
  if (!exam) return null;

  const questions = exam.sections.flatMap((sec) =>
    sec.questions.map((q) => ({
      id: q.id,
      topic: sec.id,
      subject: exam.subject,
      stem: (locale === 'he' ? q.body_he : q.body_en) || q.body_he || q.body_en,
      options: [] as { key: string; text: string }[],
      correct: '',
    })),
  );

  const answerRows = questions.map((q) => ({
    item_id: q.id,
    chosen: String(answers[q.id] ?? '').trim(),
  }));
  const answered = answerRows.filter((a) => a.chosen.length > 0).length;

  // Ungraded open exam — do not invent a pass. Archive with score 0 so readiness
  // mock-gate is not falsely satisfied; activity still lands via test_attempts.
  const attemptId = await recordTestAttempt({
    learnerId,
    kind: 'mock_exam_seed',
    quizId: examId,
    locale,
    score: 0,
    passThreshold: MOCK_PASS_THRESHOLD,
    perTopic: {},
    weakConcepts: [],
    questions,
    answers: answerRows,
  });

  const title = locale === 'he' ? exam.title_he : exam.title_en;
  const personaLine =
    locale === 'en'
      ? `Completed seed mock exam "${title}" (${answered}/${questions.length} questions answered). Awaiting rubric review.`
      : `השלים/ה מבחן מדומה "${title}" (${answered}/${questions.length} שאלות נענו). ממתין לבדיקה לפי מחוון.`;
  void appendLearnerPersonaLine(
    learnerId,
    locale === 'en' ? 'Recent observations' : 'תצפיות אחרונות',
    personaLine,
  ).catch(() => null);

  return {
    attempt_id: attemptId,
    exam_id: examId,
    questions_answered: answered,
    questions_total: questions.length,
  };
}
