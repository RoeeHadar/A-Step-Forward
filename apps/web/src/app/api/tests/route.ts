import { auth } from '@clerk/nextjs/server';
import { listTestAttempts } from '@/lib/test-attempts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  const items = await listTestAttempts(userId, 30);
  return Response.json({ items });
}
