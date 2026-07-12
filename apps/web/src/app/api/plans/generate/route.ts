import { auth } from '@clerk/nextjs/server';
import { ensureLearningPlan, hasActiveLearningPlan, dbConfigured } from '@/lib/neon-db';
import { ROLLING_VISIBLE_WEEKS } from '@/lib/plan-worklist';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  const url = new URL(req.url);
  const forceFull = url.searchParams.get('full') === '1';
  const noPlan = !(await hasActiveLearningPlan(userId));
  const fastPath = url.searchParams.get('fast') !== '0' && noPlan;

  try {
    const plan = await ensureLearningPlan(userId, {
      fastPath: fastPath || undefined,
      rollingWindow: forceFull ? false : true,
      numWeeksOverride: forceFull ? undefined : ROLLING_VISIBLE_WEEKS,
    });
    return Response.json({ ok: true, plan_id: plan.id }, { status: 200 });
  } catch (err) {
    console.error('[plans/generate]', err);
    return Response.json(
      {
        error:
          err instanceof Error
            ? err.message
            : 'Plan generation failed',
      },
      { status: 500 },
    );
  }
}
