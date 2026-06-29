import { auth } from '@clerk/nextjs/server';
import { getDueReviews } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const items = await getDueReviews(userId);
  return Response.json({ items, count: items.length });
}