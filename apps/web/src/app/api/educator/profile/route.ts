import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import { getAppUser, updateTeacherAboutMe } from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function PATCH(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });
  const me = await getAppUser(userId);
  if (!me || me.role !== 'educator') {
    return Response.json({ error: 'Forbidden' }, { status: 403 });
  }
  let body: { about_me?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  await updateTeacherAboutMe(userId, body.about_me ?? '');
  return Response.json({ ok: true });
}
