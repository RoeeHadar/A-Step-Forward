/**
 * POST /api/quiz/custom
 *
 * Builds a fit-to-purpose AI quiz for the authenticated learner.
 *
 * Body shape (all fields optional except the first two):
 *   {
 *     "kind_mix": "closed" | "open" | "mixed",
 *     "time_limit_min": number,           // clamped to [3, 90]
 *     "topics"?: string[]                 // concept ids; falls back to the
 *                                         //   learner's weakest mastery
 *                                         //   concepts or a subject
 *                                         //   bootstrap when omitted/empty
 *   }
 *
 * Returns `CustomQuizEnvelope` on success, 503 if Groq is unavailable / the
 * model produced no valid questions, 400 on a malformed body, 401 if the
 * learner is not signed in. Quiz envelopes are NOT persisted — the client
 * holds them in component state until submission.
 */
import { auth } from '@clerk/nextjs/server';
import { getAuthContext } from '@/lib/auth';
import { buildCustomQuiz, type QuizKindMix } from '@/lib/quiz-builder';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ALLOWED_MIX: QuizKindMix[] = ['closed', 'open', 'mixed'];

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

  const kindMix = b.kind_mix;
  if (typeof kindMix !== 'string' || !ALLOWED_MIX.includes(kindMix as QuizKindMix)) {
    return Response.json(
      { error: 'kind_mix must be one of: closed | open | mixed' },
      { status: 400 },
    );
  }
  const timeLimit = Number(b.time_limit_min ?? 10);
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
    kind_mix: kindMix as QuizKindMix,
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
