/**
 * POST /api/quiz/custom
 *
 * Builds a fit-to-purpose AI quiz for the authenticated learner.
 * Persists full keys server-side; returns stripped envelope only (Sec-F1).
 */
import { auth } from '@clerk/nextjs/server';
import { getAuthContext } from '@/lib/auth';
import { buildCustomQuiz } from '@/lib/quiz-builder';
import { persistCustomQuiz } from '@/lib/custom-quiz';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }
  if (!body || typeof body !== 'object') {
    return Response.json({ error: 'Body must be a JSON object' }, { status: 400 });
  }
  const b = body as Record<string, unknown>;

  const timeLimit = Number(b.time_limit_min ?? 22);
  if (!Number.isFinite(timeLimit) || timeLimit <= 0) {
    return Response.json(
      { error: 'time_limit_min must be a positive number' },
      { status: 400 },
    );
  }
  const topics = Array.isArray(b.topics)
    ? b.topics.filter((t): t is string => typeof t === 'string' && t.trim().length > 0)
    : undefined;

  const envelope = await buildCustomQuiz(ctx.learnerId, {
    time_limit_min: timeLimit,
    topics,
  });

  if (!envelope) {
    return Response.json(
      {
        error: 'quiz_generation_failed',
        message:
          'The AI quiz builder is temporarily unavailable. Try a different topic or shorter time limit and retry.',
      },
      { status: 503 },
    );
  }

  const publicEnvelope = await persistCustomQuiz(ctx.learnerId, envelope);
  if (!publicEnvelope) {
    return Response.json(
      {
        error: 'quiz_persist_failed',
        message: 'Could not save the quiz. Please retry.',
      },
      { status: 503 },
    );
  }
  return Response.json(publicEnvelope);
}
