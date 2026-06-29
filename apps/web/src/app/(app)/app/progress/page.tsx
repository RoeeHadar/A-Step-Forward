import { redirect } from 'next/navigation';
import { ProgressPageContent } from '@/components/progress-page-content';
import { getAuthContext } from '@/lib/auth';
import { getProgressFromNeon, getLearnerProfile } from '@/lib/neon-db';

function learnerHasPhysicsEnrollment(
  profile: Awaited<ReturnType<typeof getLearnerProfile>>,
): boolean {
  if (!profile) return false;
  const personality = profile.personality_profile as { hs_physics?: boolean } | null;
  return (
    profile.points_group === 'hs_physics' ||
    profile.subjects.includes('physics') ||
    profile.subjects.includes('bagrut_physics') ||
    personality?.hs_physics === true
  );
}

/**
 * Progress page — reads directly from Neon so the stats always match the
 * main /app dashboard (which also queries Neon via getDashboardSnapshot).
 *
 * Previously this called fetchProgress() → Render /v1/progress which often
 * fell back to MOCK_PROGRESS (zeros), causing a mismatch between the two
 * pages. Now both pages share the same data source.
 */
export default async function ProgressPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const [snap, profile] = await Promise.all([
    getProgressFromNeon(auth.learnerId),
    getLearnerProfile(auth.learnerId).catch(() => null),
  ]);

  // Map ProgressSnapshot → LearnerProgress shape the ProgressDashboard expects.
  const progress = {
    learner_id: auth.learnerId,
    streak_days: snap.streak_days,
    total_minutes: snap.total_minutes,
    lessons_completed: snap.lessons_completed,
    concepts: snap.concepts.map((c) => ({
      concept_id: c.concept_id,
      concept_name: c.concept_name,
      concept_name_he: c.concept_name_he,
      current_score: c.current_score,
      history: c.history,
    })),
  };

  return (
    <ProgressPageContent
      progress={progress}
      userId={auth.learnerId}
      hasPhysicsEnrollment={learnerHasPhysicsEnrollment(profile)}
    />
  );
}
