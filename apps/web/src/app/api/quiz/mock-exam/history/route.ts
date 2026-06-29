import { auth } from '@clerk/nextjs/server';
import { getMockExamHistory } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const items = await getMockExamHistory(userId, 5);
  return Response.json({ items });
}