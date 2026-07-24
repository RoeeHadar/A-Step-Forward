import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import { DashboardContent } from '@/components/dashboard-content';
import { AgentsIntroBanner } from '@/components/agents-intro-banner';
import { MicroWinToast } from '@/components/micro-win-toast';
import { GoalCompletionBanner } from '@/components/goal-completion-banner';
import { getAuthContext } from '@/lib/auth';
import {
  advanceRollingPlanWindow,
  getLearnerProfile,
  getGoalCompletionStatus,
  getCurrentPlan,
  getLearnerStreak,
  getLatestPlanChange,
  dbConfigured,
} from '@/lib/neon-db';
import { PlanChangeBanner } from '@/components/plan-change-banner';
import { PlanAdjustmentNotice } from '@/components/plan-adjustment-notice';
import { getAcceptedTeacherForStudent, maybeNotifyWeeklyGateDue } from '@/lib/social-db';
import { currentActiveWeek } from '@/lib/learning-path-types';
import { buildWeekTrainingSpec } from '@/lib/week-training-spec';

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

  if (dbConfigured) {
    await advanceRollingPlanWindow(auth.learnerId).catch(() => null);
  }

  const [profile, goalStatus, plan, streak, latestPlanChange, teacher] = await Promise.all([
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
    dbConfigured
      ? getLatestPlanChange(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getAcceptedTeacherForStudent(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
  ]);

  const activeWeek = plan ? currentActiveWeek(plan) : undefined;
  if (dbConfigured && activeWeek?.quiz_due_at && activeWeek.status === 'active') {
    void maybeNotifyWeeklyGateDue({
      learnerId: auth.learnerId,
      weekId: activeWeek.id,
      weekNumber: activeWeek.week_number,
      quizDueAt: activeWeek.quiz_due_at,
    }).catch(() => undefined);
  }

  // Derive training spec for active week (≤2 cheap Neon queries in parallel).
  const weekSpec =
    dbConfigured && activeWeek && plan
      ? await buildWeekTrainingSpec(auth.learnerId, activeWeek, plan.id).catch(() => null)
      : null;

  return (
    <>
      {goalStatus ? <GoalCompletionBanner status={goalStatus} /> : null}
      {latestPlanChange ? (
        <PlanChangeBanner change={latestPlanChange} learnerId={auth.learnerId} />
      ) : null}
      {plan ? <PlanAdjustmentNotice plan={plan} learnerId={auth.learnerId} /> : null}
      <AgentsIntroBanner />
      <Suspense fallback={null}>
        <MicroWinToast />
      </Suspense>
      <DashboardContent
        displayName={auth.displayName}
        plan={plan}
        nextTestDate={profile?.next_test_date ?? null}
        finalGoalDate={profile?.final_goal_date ?? null}
        streak={streak}
        pointsGroup={profile?.points_group ?? null}
        subjects={profile?.subjects ?? null}
        goal={profile?.goal ?? null}
        goalKey={
          (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ?? null
        }
        teacher={
          teacher
            ? { real_name: teacher.real_name, username: teacher.username }
            : null
        }
        weekSpec={weekSpec}
      />
    </>
  );
}
