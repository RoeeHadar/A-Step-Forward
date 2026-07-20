import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import { respondFriendRequest } from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: { friendship_id?: string; accept?: boolean; notification_id?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  if (!body.friendship_id || typeof body.accept !== 'boolean') {
    return Response.json({ error: 'friendship_id and accept required' }, { status: 400 });
  }
  const result = await respondFriendRequest({
    userId,
    friendshipId: body.friendship_id,
    accept: body.accept,
    notificationId: body.notification_id ?? null,
  });
  if (!result.ok) {
    return Response.json(
      { error: result.error, code: result.code },
      { status: result.code === 'not_found' ? 404 : 500 },
    );
  }
  return Response.json({ ok: true, status: result.status });
}
