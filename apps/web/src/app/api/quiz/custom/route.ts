/**
 * POST /api/quiz/custom
 *
 * Builds a fit-to-purpose AI quiz for the authenticated learner.
 * Mode (bagrut_open vs university_open) is determined server-side from the
 * learner's profile — the client's kind_mix hint is accepted for compat
 * but no longer controls question style.
 *
 * Body shape:
 *   {
 *     "kind_mix"?: string,           // ignored — kept for backward compat
 *     "time_limit_min": number,      // clamped to [3, 90]
 *     "topics"?: string[]            // concept ids; falls back to weakest mastery
 *   }
 */
import { auth } from '@clerk/nextjs/server';
import { getAuthContext } from '@/lib/auth';
import { buildCustomQuiz } from '@/lib/quiz-builder';

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
  return Response.json(envelope);
}
