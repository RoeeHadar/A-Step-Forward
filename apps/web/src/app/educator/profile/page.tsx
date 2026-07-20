import { redirect } from 'next/navigation';
import { getAuthContext, requireRole } from '@/lib/auth';
import { ensureIdentityComplete } from '@/lib/identity-gate';
import { getAppUser } from '@/lib/social-db';

export const dynamic = 'force-dynamic';

/** Convenience redirect to the teacher's public profile at /u/{username}. */
export default async function EducatorProfileRedirect() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');
  await ensureIdentityComplete(auth.userId, '/educator/profile');
  try {
    requireRole(auth, ['educator', 'admin']);
  } catch {
    redirect('/app');
  }
  const me = await getAppUser(auth.userId);
  if (!me?.username) redirect('/identity?next=/educator/profile');
  redirect(`/u/${encodeURIComponent(me.username)}`);
}
