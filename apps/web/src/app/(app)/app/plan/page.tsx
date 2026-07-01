import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured, getCurrentPlan, getLearnerProfile, getLatestPlanChange } from '@/lib/neon-db';
import { LearningPlanDashboard } from '@/components/learning-plan-dashboard';
import { PlanChangeBanner } from '@/components/plan-change-banner';

export const dynamic = 'force-dynamic';

export default async function LearningPlanPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const [plan, profile, latestChange] = await Promise.all([
    dbConfigured
      ? getCurrentPlan(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getLearnerProfile(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getLatestPlanChange(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
  ]);

  if (!plan) {
    redirect('/app');
  }

  return (
    <div className="container max-w-5xl py-8">
      {latestChange ? <PlanChangeBanner change={latestChange} /> : null}
      <LearningPlanDashboard
        plan={plan}
        finalGoalDate={profile?.final_goal_date ?? null}
        nextTestDate={profile?.next_test_date ?? null}
      />
    </div>
  );
}
