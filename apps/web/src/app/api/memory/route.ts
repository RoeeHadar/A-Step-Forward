import { auth } from '@clerk/nextjs/server';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured, getMemoryTimelineFromNeon, NeonQueryFailedError } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/** Memory timeline from Neon agent notes + shared persona. */
export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  try {
    const data = await getMemoryTimelineFromNeon(ctx.learnerId);
    return Response.json(data);
  } catch (err) {
    if (err instanceof NeonQueryFailedError) {
      return Response.json({ error: 'Memory data temporarily unavailable' }, { status: 503 });
    }
    throw err;
  }
}
