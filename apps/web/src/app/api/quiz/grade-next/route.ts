/**
 * POST /api/quiz/grade-next
 *
 * Grades the next pending open item for an attempt (chunked process review).
 * Body: { attempt_id: string }
 *
 * Score stays null until grading_status === 'complete'.
 */
import { auth } from '@clerk/nextjs/server';
import { continueWeeklyQuizGrading } from '@/lib/weekly-quiz';
import { getAttemptGradingView } from '@/lib/assessment-grading';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'invalid_json' }, { status: 400 });
  }
  const attemptId =
    body && typeof body === 'object' && typeof (body as { attempt_id?: unknown }).attempt_id === 'string'
      ? (body as { attempt_id: string }).attempt_id.trim()
      : '';
  if (!attemptId) {
    return Response.json({ error: 'attempt_id_required' }, { status: 400 });
  }

  const result = await continueWeeklyQuizGrading(userId, attemptId);
  if (!result) {
    return Response.json({ error: 'attempt_not_found' }, { status: 404 });
  }
  return Response.json(result);
}

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  const attemptId = new URL(req.url).searchParams.get('attempt_id')?.trim() ?? '';
  if (!attemptId) {
    return Response.json({ error: 'attempt_id_required' }, { status: 400 });
  }

  const view = await getAttemptGradingView(userId, attemptId);
  if (!view) {
    return Response.json({ error: 'attempt_not_found' }, { status: 404 });
  }

  return Response.json({
    quiz_id: attemptId,
    score: view.score,
    per_topic: view.per_topic,
    weak_concepts: view.weak_concepts,
    plan_adapted: view.plan_adapted,
    passed: view.passed,
    pass_threshold: view.pass_threshold,
    attempt_id: view.attempt_id,
    grading_status: view.grading_status,
    item_feedback: view.item_feedback,
    item_scores: view.item_scores,
    open_pending: view.open_pending,
    open_total: view.open_total,
    graded_open: view.graded_open,
  });
}
