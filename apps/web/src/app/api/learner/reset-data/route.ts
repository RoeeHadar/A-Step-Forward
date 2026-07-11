import { auth } from '@clerk/nextjs/server';
import { resetLearnerData } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * POST /api/learner/reset-data
 * Wipes the authenticated learner's progress, memory notes, chat, and plans.
 * Profile/onboarding row is kept so they can re-test without re-onboarding.
 */
export async function POST() {
  const { userId } = await auth();
  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    await resetLearnerData(userId);
    return Response.json({ ok: true, learner_id: userId });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'reset_failed';
    return Response.json({ error: message }, { status: 500 });
  }
}
