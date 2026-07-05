import { auth } from '@clerk/nextjs/server';
import { getAuthContext } from '@/lib/auth';
import {
  dbConfigured,
  getDashboardSnapshot,
  mapDashboardSnapshotToLearnerDashboard,
  NeonQueryFailedError,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/** Learner dashboard JSON from Neon — same source as server-rendered pages. */
export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  try {
    const snap = await getDashboardSnapshot(ctx.learnerId);
    return Response.json(mapDashboardSnapshotToLearnerDashboard(snap));
  } catch (err) {
    if (err instanceof NeonQueryFailedError) {
      return Response.json({ error: 'Dashboard data temporarily unavailable' }, { status: 503 });
    }
    throw err;
  }
}
