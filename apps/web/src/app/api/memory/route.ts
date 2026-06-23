import { auth } from '@clerk/nextjs/server';
import { fetchMemories } from '@/lib/data';
import { getAuthContext } from '@/lib/auth';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const data = await fetchMemories(ctx);
  return Response.json(data);
}
