import { auth } from '@clerk/nextjs/server';
import { ensureLearningPlan, hasActiveLearningPlan, dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 120;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  const fastPath =
    new URL(req.url).searchParams.get('fast') !== '0' &&
    !(await hasActiveLearningPlan(userId));

  try {
    const plan = await ensureLearningPlan(userId, { fastPath: fastPath || undefined });
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
