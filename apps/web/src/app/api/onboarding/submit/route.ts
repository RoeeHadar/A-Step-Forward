import { auth } from '@clerk/nextjs/server';
import {
  bootstrapOnboardingPlan,
  learnerHasPlan,
  type OnboardingBootstrapPayload,
} from '@/lib/onboarding-plan-bootstrap';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
/** Keep short — bootstrap is a handful of SQL round-trips, not the neon-db monolith. */
export const maxDuration = 30;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }
  if (!(process.env.DATABASE_URL ?? process.env.POSTGRES_URL)) {
    return Response.json(
      { error: 'Database not configured. Set DATABASE_URL in Vercel.' },
      { status: 503 },
    );
  }

  let body: OnboardingBootstrapPayload;
  try {
    body = (await req.json()) as OnboardingBootstrapPayload;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  if (!body?.goal || !Array.isArray(body.subjects) || body.subjects.length === 0) {
    return Response.json({ error: 'Missing required fields' }, { status: 400 });
  }

  try {
    const started = Date.now();
    const result = await bootstrapOnboardingPlan(userId, body);
    const hasPlan = await learnerHasPlan(userId);
    if (!hasPlan) {
      return Response.json(
        { error: 'Plan was not saved. Please try again.' },
        { status: 500 },
      );
    }
    console.info('[onboarding/submit] bootstrap ok', {
      ms: Date.now() - started,
      plan_id: result.plan_id,
      weeks: result.week_count,
      concepts: result.concept_count,
    });
    return Response.json(
      {
        status: 'ok',
        learner_id: userId,
        plan_id: result.plan_id,
        has_plan: true,
        week_count: result.week_count,
        concept_count: result.concept_count,
      },
      { status: 200 },
    );
  } catch (err) {
    console.error('[onboarding/submit]', err);
    return Response.json(
      {
        error:
          err instanceof Error
            ? err.message
            : 'Failed to save profile and create your learning plan',
      },
      { status: 500 },
    );
  }
}

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }
  if (!(process.env.DATABASE_URL ?? process.env.POSTGRES_URL)) {
    return Response.json({ completed: false, reason: 'db_not_configured' });
  }
  try {
    const hasPlan = await learnerHasPlan(userId);
    return Response.json({ completed: hasPlan, has_plan: hasPlan });
  } catch (err) {
    console.error('[onboarding/status]', err);
    return Response.json({ completed: false, error: String(err) });
  }
}
