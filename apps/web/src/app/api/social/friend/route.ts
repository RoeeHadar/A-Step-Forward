/**
 * GET  /api/social/friend — list friends + pending + optional search (?q=)
 * POST /api/social/friend — send friend request by username or user_id
 */
import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import {
  getAppUser,
  getAppUserByUsername,
  listFriends,
  listPendingFriendRequests,
  searchLearnersForFriends,
  sendFriendRequest,
} from '@/lib/social-db';
import { checkSocialRateLimit } from '@/lib/social-rate-limit';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) {
    return Response.json({ friends: [], pending: [], results: [] });
  }

  const me = await getAppUser(userId);
  if (!me || me.role !== 'learner') {
    return Response.json({ error: 'Friends are for students only' }, { status: 403 });
  }

  const q = new URL(req.url).searchParams.get('q')?.trim() ?? '';
  if (q.length >= 2) {
    const limited = checkSocialRateLimit(`friend-search:${userId}`, {
      limit: 20,
      windowMs: 60_000,
    });
    if (!limited.ok) {
      return Response.json(
        { error: 'Too many searches. Try again shortly.', retry_after: limited.retryAfterSec },
        { status: 429, headers: { 'Retry-After': String(limited.retryAfterSec) } },
      );
    }
  }

  const [friends, pending, results] = await Promise.all([
    listFriends(userId),
    listPendingFriendRequests(userId),
    q.length >= 2 ? searchLearnersForFriends(q, userId) : Promise.resolve([]),
  ]);

  return Response.json({ friends, pending, results });
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: { username?: string; user_id?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  let addresseeId = body.user_id;
  if (!addresseeId && body.username) {
    const u = await getAppUserByUsername(body.username);
    addresseeId = u?.clerk_user_id;
  }
  if (!addresseeId) {
    return Response.json({ error: 'User not found' }, { status: 404 });
  }

  const result = await sendFriendRequest({
    requesterId: userId,
    addresseeId,
  });
  if (!result.ok) return Response.json({ error: result.error }, { status: 400 });
  return Response.json(result);
}
