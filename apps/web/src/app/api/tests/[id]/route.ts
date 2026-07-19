import { auth } from '@clerk/nextjs/server';
import { getTestAttempt } from '@/lib/test-attempts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  const { id } = await params;
  const attempt = await getTestAttempt(userId, id);
  if (!attempt) return Response.json({ error: 'not_found' }, { status: 404 });
  return Response.json({ attempt });
}
