import { auth } from '@clerk/nextjs/server';
import { upsertLearnerProfile, getLearnerProfile, dbConfigured } from '@/lib/neon-db';
import type { OnboardingPayload } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

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

  try {
    await upsertLearnerProfile(userId, body);
    return Response.json({ status: 'ok', learner_id: userId }, { status: 200 });
  } catch (err) {
    console.error('[onboarding/submit]', err);
    return Response.json(
      { error: err instanceof Error ? err.message : 'Failed to save profile' },
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
    return Response.json({ completed: Boolean(profile), profile });
  } catch (err) {
    console.error('[onboarding/status]', err);
    return Response.json({ completed: false, error: String(err) });
  }
}
