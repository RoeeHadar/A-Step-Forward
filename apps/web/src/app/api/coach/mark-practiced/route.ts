/**
 * POST /api/coach/mark-practiced
 *
 * Records a spaced-repetition event for a skill atom. The Coach agent calls
 * this after evaluating a learner's answer so the FSRS scheduler can set
 * the correct `next_review_date` on `skill_practice`.
 *
 * Body: { atomId: string; score: number }
 *   score — 0.0–1.0 float indicating how well the learner answered.
 *
 * FSRS-inspired intervals:
 *   score ≥ 0.8  →  7 days
 *   score ≥ 0.6  →  3 days
 *   score < 0.6  →  1 day
 */
import { auth } from '@clerk/nextjs/server';
import { markAtomPracticed } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  if (!body || typeof body !== 'object') {
    return Response.json({ error: 'Body must be a JSON object' }, { status: 400 });
  }

  const { atomId, score } = body as Record<string, unknown>;

  if (typeof atomId !== 'string' || atomId.trim().length === 0) {
    return Response.json({ error: 'atomId (string) is required' }, { status: 400 });
  }

  const scoreNum = typeof score === 'number' ? score : Number(score);
  if (!Number.isFinite(scoreNum) || scoreNum < 0 || scoreNum > 1) {
    return Response.json(
      { error: 'score must be a number between 0.0 and 1.0' },
      { status: 400 },
    );
  }

  await markAtomPracticed(userId, atomId.trim(), scoreNum);

  const intervalDays = scoreNum >= 0.8 ? 7 : scoreNum >= 0.6 ? 3 : 1;
  return Response.json({
    ok: true,
    atomId: atomId.trim(),
    score: scoreNum,
    next_review_days: intervalDays,
  });
}
