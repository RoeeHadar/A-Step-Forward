/**
 * Persist a completed *seed* mock exam (open-ended catalog at /app/quiz/mock-exam).
 * Feedback-first: creates a pending attempt; score only after process review.
 */
import 'server-only';
import { appendLearnerPersonaLine } from './neon-db';
import { getMockExamById } from './mock-exam-catalog';
import { MOCK_PASS_THRESHOLD } from './mock-exam';
import {
  createPendingAttempt,
  type AttemptGradingView,
} from './assessment-grading';

export interface SeedMockExamSubmitResult {
  attempt_id: string | null;
  exam_id: string;
  questions_answered: number;
  questions_total: number;
  grading_status?: AttemptGradingView['grading_status'];
  score?: number | null;
  passed?: boolean | null;
  item_feedback?: AttemptGradingView['item_feedback'];
  open_pending?: number;
  open_total?: number;
  graded_open?: number;
  message?: string;
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
    sec.questions.map((q) => {
      const stem = (locale === 'he' ? q.body_he : q.body_en) || q.body_he || q.body_en;
      const rubric =
        (locale === 'he' ? q.rubric_he : q.rubric_en) || q.rubric_he || q.rubric_en || null;
      const model =
        (locale === 'he' ? q.sample_solution_he : q.sample_solution_en) ||
        q.sample_solution_he ||
        q.sample_solution_en ||
        null;
      return {
        id: q.id,
        topic: sec.id,
        subject: exam.subject,
        stem,
        kind: 'open' as const,
        options: [] as { key: string; text: string }[],
        rubric,
        model_answer: model,
        total_points: typeof q.points === 'number' ? q.points : 20,
      };
    }),
  );

  const answerRows = questions.map((q) => ({
    item_id: q.id,
    chosen: String(answers[q.id] ?? '').trim(),
  }));
  const answered = answerRows.filter((a) => a.chosen.length > 0).length;

  const view = await createPendingAttempt({
    learnerId,
    kind: 'mock_exam_seed',
    quizId: examId,
    locale,
    questions,
    answers: answerRows,
    closedScores: {},
    passThreshold: MOCK_PASS_THRESHOLD,
  });

  const title = locale === 'he' ? exam.title_he : exam.title_en;
  const personaLine =
    locale === 'en'
      ? `Submitted seed mock exam "${title}" (${answered}/${questions.length} answered) — awaiting process review.`
      : `הגיש/ה מבחן מדומה "${title}" (${answered}/${questions.length} נענו) — ממתין לבדיקת תהליך.`;
  void appendLearnerPersonaLine(
    learnerId,
    locale === 'en' ? 'Recent observations' : 'תצפיות אחרונות',
    personaLine,
  ).catch(() => null);

  return {
    attempt_id: view?.attempt_id ?? null,
    exam_id: examId,
    questions_answered: answered,
    questions_total: questions.length,
    grading_status: view?.grading_status,
    score: view?.score ?? null,
    passed: view?.passed ?? null,
    item_feedback: view?.item_feedback,
    open_pending: view?.open_pending,
    open_total: view?.open_total,
    graded_open: view?.graded_open,
    message: view?.message,
  };
}
