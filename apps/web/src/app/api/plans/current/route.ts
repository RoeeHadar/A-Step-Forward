import { auth } from '@clerk/nextjs/server';
import {
  getCurrentPlan,
  hasActiveLearningPlan,
  advanceRollingPlanWindow,
  dbConfigured,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ plan: null, reason: 'db_not_configured' });
  }

  const existsOnly = new URL(req.url).searchParams.get('exists') === '1';

  try {
    if (existsOnly) {
      return Response.json({ has_plan: await hasActiveLearningPlan(userId) });
    }

    // Advance rolling window when active week is past due (cheap no-op otherwise).
    await advanceRollingPlanWindow(userId).catch(() => null);

    const plan = await getCurrentPlan(userId);
    if (!plan) {
      return Response.json({ plan: null });
    }
    return Response.json({ plan });
  } catch (err) {
    console.error('[plans/current]', err);
    return Response.json({ plan: null, error: 'db_unavailable' }, { status: 503 });
  }
}
