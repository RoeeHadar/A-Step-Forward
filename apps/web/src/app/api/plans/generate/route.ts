import { auth } from '@clerk/nextjs/server';
import { generateLearningPlan, getCurrentPlan, dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isPlanLockError(message: string): boolean {
  return /plan update is already in progress/i.test(message);
}

export async function POST() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  let lastError: unknown;
  for (let attempt = 0; attempt < 6; attempt += 1) {
    try {
      const plan = await generateLearningPlan(userId);
      return Response.json(plan, { status: 200 });
    } catch (err) {
      lastError = err;
      const message = err instanceof Error ? err.message : String(err);
      if (isPlanLockError(message)) {
        const existing = await getCurrentPlan(userId);
        if (existing) {
          return Response.json(existing, { status: 200 });
        }
        await sleep(600 + attempt * 500);
        continue;
      }
      break;
    }
  }

  const existing = await getCurrentPlan(userId);
  if (existing) {
    return Response.json(existing, { status: 200 });
  }

  console.error('[plans/generate]', lastError);
  return Response.json(
    {
      error:
        lastError instanceof Error
          ? lastError.message
          : 'Plan generation failed',
    },
    { status: 500 },
  );
}
