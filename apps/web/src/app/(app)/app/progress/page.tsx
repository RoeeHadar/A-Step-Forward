import { redirect } from 'next/navigation';
import { ProgressPageContent } from '@/components/progress-page-content';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured, getProgressFromNeon, getLearnerProfile } from '@/lib/neon-db';
import { learnerHasPhysicsEnrollment } from '@/lib/learner-enrollment';

export const dynamic = 'force-dynamic';

/**
 * Progress page — reads directly from Neon on every request so stats reflect
 * the learner's latest chat, lesson, and quiz activity.
 */
export default async function ProgressPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const [snap, profile] = await Promise.all([
    dbConfigured
      ? getProgressFromNeon(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    getLearnerProfile(auth.learnerId).catch(() => null),
  ]);

  return (
    <ProgressPageContent
      snapshot={snap}
      learnerId={auth.learnerId}
      hasPhysicsEnrollment={learnerHasPhysicsEnrollment(profile)}
    />
  );
}
