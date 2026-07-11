import { auth } from '@clerk/nextjs/server';
import { resetLearnerData } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * POST /api/learner/reset-data
 * Wipes progress, memory, chat, and plans.
 * Body `{ "full": true }` also deletes onboarding profile → /onboarding.
 */
export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  let full = false;
  try {
    const body = (await req.json()) as { full?: boolean };
    full = body?.full === true;
  } catch {
    /* empty body = partial reset (legacy) */
  }

  try {
    await resetLearnerData(userId, { deleteProfile: full });
    return Response.json({ ok: true, learner_id: userId, full });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'reset_failed';
    return Response.json({ error: message }, { status: 500 });
  }
}
