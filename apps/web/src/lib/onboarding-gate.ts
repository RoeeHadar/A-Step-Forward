import 'server-only';
import { redirect } from 'next/navigation';
import { dbConfigured, getLearnerProfile } from '@/lib/neon-db';

/**
 * Redirect logged-in users without a learner profile to /onboarding.
 * Call from any server component that requires an onboarded learner.
 *
 * If DATABASE_URL is not configured we silently skip the gate so the
 * site never hard-fails before infra is provisioned.
 */
export async function ensureOnboarded(userId: string, returnTo = '/app'): Promise<void> {
  if (!dbConfigured) return;
  try {
    const profile = await getLearnerProfile(userId);
    if (!profile) {
      const params = new URLSearchParams({ next: returnTo });
      redirect(`/onboarding?${params.toString()}`);
    }
  } catch (err) {
    if (err && typeof err === 'object' && 'digest' in err) throw err;
    console.warn('[onboarding-gate] profile lookup failed', err);
  }
}
