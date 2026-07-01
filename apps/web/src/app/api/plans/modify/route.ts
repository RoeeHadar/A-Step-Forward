import { auth } from '@clerk/nextjs/server';
import {
  applyPlanProfileUpdates,
  dbConfigured,
  generateLearningPlan,
  type GeneratePlanOptions,
} from '@/lib/neon-db';
import type { PlanUpdatePayload } from '@/lib/plan-catalog';
import { planPayloadToOptions } from '@/lib/plan-actions';
import { sanitizePlanUpdatePayload } from '@/lib/plan-catalog';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'Database not configured' }, { status: 503 });
  }

  let body: PlanUpdatePayload;
  try {
    body = (await req.json()) as PlanUpdatePayload;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  if (!body.confirmed || !body.reason?.trim()) {
    return Response.json(
      { error: 'Plan updates require confirmed:true and a reason' },
      { status: 400 },
    );
  }

  const payload = sanitizePlanUpdatePayload(body);
  if (!payload) {
    return Response.json({ error: 'Invalid plan update payload' }, { status: 400 });
  }

  try {
    await applyPlanProfileUpdates(userId, {
      goal: payload.goal,
      next_test_date: payload.next_test_date,
      final_goal_date: payload.final_goal_date,
      hours_per_week: payload.hours_per_week,
      goal_key: payload.goal_key,
    });

    const options: GeneratePlanOptions = planPayloadToOptions(payload);
    const plan = await generateLearningPlan(userId, options);
    return Response.json({ ok: true, plan });
  } catch (err) {
    console.error('[plans/modify]', err);
    return Response.json(
      { error: err instanceof Error ? err.message : 'Failed to update plan' },
      { status: 500 },
    );
  }
}
