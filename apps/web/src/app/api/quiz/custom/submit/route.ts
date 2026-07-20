/**
 * POST /api/quiz/custom/submit
 *
 * Feedback-first submit for /app/quiz custom envelopes.
 * Creates a pending attempt when opens exist; score only after process review.
 */
import { auth } from '@clerk/nextjs/server';
import { createPendingAttempt } from '@/lib/assessment-grading';
import { answersMatch, getAcceptedAnswers, numericClose } from '@/lib/answer-normalize';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type CustomQ = {
  id?: string;
  concept_id: string;
  kind: string;
  stem: string;
  options?: { key: string; text: string }[];
  correct?: string | null;
  correct_answer?: string | null;
  acceptable_answers?: string[];
  rubric?: string | null;
  model_answer?: string | null;
  parts?: Array<{ label: string; body: string; points?: number }>;
  total_points?: number;
  skill_atoms?: string[];
};

function gradeClosed(q: CustomQ, chosenRaw: string): number {
  const chosen = chosenRaw.trim();
  if (!chosen) return 0;
  if (q.kind === 'mcq' || q.kind === 'true_false') {
    return q.correct && chosen.toUpperCase() === String(q.correct).toUpperCase() ? 1 : 0;
  }
  if (q.kind === 'numeric') {
    return q.correct_answer && numericClose(chosen, String(q.correct_answer)) ? 1 : 0;
  }
  if (q.kind === 'short_answer') {
    const accepted = getAcceptedAnswers(q.acceptable_answers, q.correct_answer ?? undefined);
    return answersMatch(chosen, accepted) ? 1 : 0;
  }
  return 0;
}

function isOpen(kind: string): boolean {
  return kind === 'open' || kind === 'derivation' || kind === 'extended';
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'invalid_json' }, { status: 400 });
  }
  if (!body || typeof body !== 'object') {
    return Response.json({ error: 'invalid_body' }, { status: 400 });
  }
  const b = body as {
    quiz_id?: string;
    locale?: string;
    questions?: CustomQ[];
    answers?: Array<{ item_id: string; chosen: string }>;
  };

  const questions = Array.isArray(b.questions) ? b.questions : [];
  const answers = Array.isArray(b.answers) ? b.answers : [];
  if (questions.length === 0) {
    return Response.json({ error: 'questions_required' }, { status: 400 });
  }

  const answerByItem = new Map(answers.map((a) => [a.item_id, a.chosen]));
  const closedScores: Record<string, number> = {};
  const normalized = questions.map((q, i) => {
    const id = q.id?.trim() || `cq-${i}-${q.concept_id}`;
    const partsPts =
      q.parts?.reduce((s, p) => s + (typeof p.points === 'number' ? p.points : 0), 0) ?? 0;
    const total =
      q.total_points ??
      (partsPts > 0 ? partsPts : isOpen(q.kind) ? 20 : 5);
    if (!isOpen(q.kind)) {
      closedScores[id] = gradeClosed(q, answerByItem.get(id) ?? '');
    }
    return {
      id,
      topic: q.concept_id,
      subject: '',
      stem: q.stem,
      kind: isOpen(q.kind) ? 'open' : q.kind,
      options: q.options,
      correct: q.correct ?? undefined,
      correct_answer: q.correct_answer,
      acceptable_answers: q.acceptable_answers,
      rubric: q.rubric,
      model_answer: q.model_answer,
      total_points: total,
      skill_atoms: q.skill_atoms,
    };
  });

  const locale = b.locale === 'en' ? 'en' : 'he';
  const view = await createPendingAttempt({
    learnerId: userId,
    kind: 'custom_quiz',
    quizId: typeof b.quiz_id === 'string' ? b.quiz_id : null,
    locale,
    questions: normalized,
    answers: normalized.map((q) => ({
      item_id: q.id,
      chosen: answerByItem.get(q.id) ?? '',
    })),
    closedScores,
  });

  if (!view) {
    return Response.json({ error: 'grading_unavailable' }, { status: 503 });
  }

  return Response.json({
    quiz_id: b.quiz_id ?? view.attempt_id,
    score: view.score,
    per_topic: view.per_topic,
    weak_concepts: view.weak_concepts,
    plan_adapted: false,
    passed: view.passed,
    pass_threshold: view.pass_threshold,
    attempt_id: view.attempt_id,
    grading_status: view.grading_status,
    item_feedback: view.item_feedback,
    item_scores: view.item_scores,
    open_pending: view.open_pending,
    open_total: view.open_total,
    graded_open: view.graded_open,
    busy: view.busy,
    message: view.message,
  });
}
