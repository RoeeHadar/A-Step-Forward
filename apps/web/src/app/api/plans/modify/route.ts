import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import type { PlanUpdatePayload } from '@/lib/plan-catalog';
import { sanitizePlanUpdatePayload } from '@/lib/plan-catalog';
import { executePlanUpdate } from '@/lib/plan-apply';

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

  const result = await executePlanUpdate(userId, payload, {
    agent: 'api',
    source: 'api',
  });

  if (!result.applied) {
    return Response.json(
      { error: result.error ?? 'Failed to update plan' },
      { status: 500 },
    );
  }

  return Response.json({ ok: true, planId: result.planId, weekSummaries: result.weekSummaries });
}
