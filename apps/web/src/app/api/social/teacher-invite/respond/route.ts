import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import { respondTeacherInvite } from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: { link_id?: string; accept?: boolean; notification_id?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  // link_id optional when notification_id is present — server falls back to
  // the student's pending invite.
  if (typeof body.accept !== 'boolean') {
    return Response.json({ error: 'accept required' }, { status: 400 });
  }
  if (!body.link_id && !body.notification_id) {
    return Response.json({ error: 'link_id or notification_id required' }, { status: 400 });
  }

  const result = await respondTeacherInvite({
    studentId: userId,
    linkId: body.link_id?.trim() || '',
    accept: body.accept,
    notificationId: body.notification_id ?? null,
  });
  if (!result.ok) return Response.json({ error: result.error }, { status: 400 });
  return Response.json({ ok: true });
}
