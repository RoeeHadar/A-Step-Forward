/**
 * POST /api/identity — create/update app_users + sync Clerk role.
 */
import { auth } from '@clerk/nextjs/server';
import { syncClerkRole } from '@/lib/auth';
import { dbConfigured } from '@/lib/neon-db';
import {
  getAppUser,
  normalizeUsername,
  upsertAppUser,
  validateRealName,
  validateUsername,
  type SocialRole,
} from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  let body: {
    role?: string;
    username?: string;
    real_name?: string;
    about_me?: string | null;
  };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const existing = await getAppUser(userId).catch(() => null);
  const roleRaw = body.role === 'educator' ? 'educator' : 'learner';
  const role: SocialRole =
    existing?.profile_complete && existing.role
      ? existing.role
      : roleRaw;

  const username = normalizeUsername(String(body.username ?? ''));
  const realName = String(body.real_name ?? '').trim().replace(/\s+/g, ' ');

  const realErr = validateRealName(realName);
  if (realErr) return Response.json({ error: realErr }, { status: 400 });

  const usernameErr = validateUsername(username);
  if (usernameErr) return Response.json({ error: usernameErr }, { status: 400 });

  try {
    const user = await upsertAppUser({
      clerkUserId: userId,
      role,
      username,
      realName,
      nickname: null,
      aboutMe: role === 'educator' ? body.about_me : null,
      profileComplete: true,
    });
    await syncClerkRole(userId, role);

    return Response.json({
      ok: true,
      user,
      redirect: role === 'educator' ? '/educator' : '/onboarding',
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Save failed';
    const conflict = /unique|duplicate/i.test(message);
    return Response.json(
      { error: conflict ? 'Username already taken' : message },
      { status: conflict ? 409 : 500 },
    );
  }
}
