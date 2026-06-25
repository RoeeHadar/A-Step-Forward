import { auth } from '@clerk/nextjs/server';
import { getCurrentPlan, dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ plan: null, reason: 'db_not_configured' });
  }

  try {
    const plan = await getCurrentPlan(userId);
    if (!plan) {
      return Response.json({ plan: null });
    }
    return Response.json({ plan });
  } catch (err) {
    console.error('[plans/current]', err);
    return Response.json(
      { plan: null, error: err instanceof Error ? err.message : String(err) },
      { status: 200 },
    );
  }
}
