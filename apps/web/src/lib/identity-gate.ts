/**
 * Identity gate: role fork + username/real-name for social features.
 */
import 'server-only';
import { redirect } from 'next/navigation';
import { dbConfigured } from '@/lib/neon-db';
import { getAppUser } from '@/lib/social-db';

/**
 * Redirect signed-in users without a complete app_users profile to /identity.
 * Teachers skip learner onboarding; learners still hit ensureOnboarded after.
 */
export async function ensureIdentityComplete(
  userId: string,
  returnTo = '/app',
): Promise<void> {
  if (!dbConfigured) return;
  try {
    const user = await getAppUser(userId);
    if (!user || !user.profile_complete || !user.username || !user.real_name) {
      const params = new URLSearchParams({ next: returnTo });
      redirect(`/identity?${params.toString()}`);
    }
  } catch (err) {
    if (err && typeof err === 'object' && 'digest' in err) throw err;
    console.warn('[identity-gate] lookup failed', err);
  }
}

export async function ensureLearnerNotTeacher(
  userId: string,
): Promise<'learner' | 'educator' | null> {
  if (!dbConfigured) return null;
  try {
    const user = await getAppUser(userId);
    if (user?.role === 'educator') {
      redirect('/educator');
    }
    return user?.role ?? null;
  } catch (err) {
    if (err && typeof err === 'object' && 'digest' in err) throw err;
    return null;
  }
}
