import { getPublicShareStats } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const userId = url.searchParams.get('userId')?.trim();
  if (!userId) {
    return Response.json({ error: 'userId required' }, { status: 400 });
  }

  const stats = await getPublicShareStats(userId);
  if (!stats) {
    return Response.json({ error: 'Not found' }, { status: 404 });
  }

  return Response.json(stats);
}
