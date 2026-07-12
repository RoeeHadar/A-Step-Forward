import { auth } from '@clerk/nextjs/server';
import {
  upsertLearnerProfile,
  getLearnerProfile,
  createOnboardingPlan,
  hasActiveLearningPlan,
  dbConfigured,
} from '@/lib/neon-db';
import type { OnboardingPayload } from '@/lib/neon-db';
import { deriveOnboardingSeedScores } from '@/lib/onboarding-self-score';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }
  if (!dbConfigured) {
    return Response.json(
      { error: 'Database not configured. Set DATABASE_URL in Vercel.' },
      { status: 503 },
    );
  }

  let body: OnboardingPayload;
  try {
    body = (await req.json()) as OnboardingPayload;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  if (!body?.goal || !Array.isArray(body.subjects) || body.subjects.length === 0) {
    return Response.json({ error: 'Missing required fields' }, { status: 400 });
  }

  const selfScores = deriveOnboardingSeedScores({
    goal: body.goal,
    subjects: body.subjects,
    grade_level: body.grade_level,
    points_group: body.points_group,
    self_scores: body.self_scores,
    personality_profile: body.personality_profile,
    adult_learner: body.adult_learner,
  });

  const payload: OnboardingPayload = {
    ...body,
    self_scores: selfScores,
  };

  try {
    await upsertLearnerProfile(userId, payload, { skipAdaptiveRefresh: true });
    const plan = await createOnboardingPlan(userId);
    const hasPlan = await hasActiveLearningPlan(userId);
    if (!hasPlan) {
      return Response.json(
        { error: 'Plan was not saved. Please try again.' },
        { status: 500 },
      );
    }
    return Response.json(
      {
        status: 'ok',
        learner_id: userId,
        plan_id: plan.id,
        has_plan: true,
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
  if (!dbConfigured) {
    return Response.json({ completed: false, reason: 'db_not_configured' });
  }
  try {
    const profile = await getLearnerProfile(userId);
    const hasPlan = profile ? await hasActiveLearningPlan(userId) : false;
    return Response.json({ completed: Boolean(profile), has_plan: hasPlan, profile });
  } catch (err) {
    console.error('[onboarding/status]', err);
    return Response.json({ completed: false, error: String(err) });
  }
}
