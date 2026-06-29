import { auth } from '@clerk/nextjs/server';
import { getEstimatedBagrutScore } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const subject = url.searchParams.get('subject') ?? 'math_5';

  const result = await getEstimatedBagrutScore(userId, subject);
  return Response.json(result);
}