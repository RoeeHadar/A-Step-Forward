import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import { DashboardContent } from '@/components/dashboard-content';
import { AgentsIntroBanner } from '@/components/agents-intro-banner';
import { MicroWinToast } from '@/components/micro-win-toast';
import { GoalCompletionBanner } from '@/components/goal-completion-banner';
import { getAuthContext } from '@/lib/auth';
import {
  getLearnerProfile,
  getGoalCompletionStatus,
  getCurrentPlan,
  getLearnerStreak,
  dbConfigured,
} from '@/lib/neon-db';

export const dynamic = 'force-dynamic';

const EMPTY_STREAK = {
  current_days: 0,
  longest_days: 0,
  last_active: null,
  active_today: false,
  active_days_last_30: 0,
} as const;

export default async function DashboardPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const [profile, goalStatus, plan, streak] = await Promise.all([
    dbConfigured
      ? getLearnerProfile(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getGoalCompletionStatus(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getCurrentPlan(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getLearnerStreak(auth.learnerId).catch(() => ({ ...EMPTY_STREAK }))
      : Promise.resolve({ ...EMPTY_STREAK }),
  ]);

  return (
    <>
      {goalStatus ? <GoalCompletionBanner status={goalStatus} /> : null}
      <AgentsIntroBanner />
      <Suspense fallback={null}>
        <MicroWinToast />
      </Suspense>
      <DashboardContent
        displayName={auth.displayName}
        plan={plan}
        nextTestDate={profile?.next_test_date ?? null}
        streak={streak}
        pointsGroup={profile?.points_group ?? null}
        subjects={profile?.subjects ?? null}
        goal={profile?.goal ?? null}
      />
    </>
  );
}
