import { auth } from '@clerk/nextjs/server';
import { generateLearningPlan, dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  try {
    const plan = await generateLearningPlan(userId);
    return Response.json(plan, { status: 200 });
  } catch (err) {
    console.error('[plans/generate]', err);
    return Response.json(
      { error: err instanceof Error ? err.message : 'Plan generation failed' },
      { status: 500 },
    );
  }
}
