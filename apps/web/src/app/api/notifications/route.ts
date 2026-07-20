/**
 * GET /api/notifications — list
 * PATCH /api/notifications — mark read ({ id } | { all: true })
 */
import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import {
  countUnreadNotifications,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ items: [], unread: 0 });

  const [items, unread] = await Promise.all([
    listNotifications(userId),
    countUnreadNotifications(userId),
  ]);
  return Response.json({ items, unread });
}

export async function PATCH(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ ok: false }, { status: 503 });

  let body: { id?: string; all?: boolean };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  if (body.all) {
    const n = await markAllNotificationsRead(userId);
    return Response.json({ ok: true, marked: n });
  }
  if (!body.id) return Response.json({ error: 'id required' }, { status: 400 });
  const ok = await markNotificationRead(userId, body.id);
  return Response.json({ ok });
}
