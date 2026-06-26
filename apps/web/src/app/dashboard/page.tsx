import Link from 'next/link';
import { auth } from '@clerk/nextjs/server';
import { SiteHeader } from '@/components/site-header';
import { LearningPlanDashboard } from '@/components/learning-plan-dashboard';
import { LearnerStreakCard } from '@/components/learner-streak-card';
import {
  getCurrentPlan,
  getLearnerStreak,
  getRecentActivity,
  dbConfigured,
} from '@/lib/neon-db';
import { ensureOnboarded } from '@/lib/onboarding-gate';
import { Button } from '@asf/ui/button';

export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  const { userId } = await auth();
  if (!userId) {
    return null;
  }

  await ensureOnboarded(userId, '/dashboard');
  // All three lookups are parallel so the dashboard cold-start latency is
  // bounded by the slowest single query rather than the sum.
  const [plan, streak, activity] = dbConfigured
    ? await Promise.all([
        getCurrentPlan(userId).catch(() => null),
        getLearnerStreak(userId).catch(() => ({
          current_days: 0,
          longest_days: 0,
          last_active: null,
          active_today: false,
          active_days_last_30: 0,
        })),
        getRecentActivity(userId, 8).catch(() => []),
      ])
    : [null, {
        current_days: 0,
        longest_days: 0,
        last_active: null,
        active_today: false,
        active_days_last_30: 0,
      }, []];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 space-y-6">
        <LearnerStreakCard streak={streak} activity={activity} />

        {!plan ? (
          <div className="glass-surface rounded-2xl p-8 text-center">
            <h1 className="font-display text-2xl font-bold">No learning plan yet</h1>
            <p className="mt-2 text-muted-foreground">
              Complete the diagnostic assessment to generate your personalized weekly plan.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Button asChild>
                <Link href="/diagnostic">Start diagnostic</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/app">Back to app</Link>
              </Button>
            </div>
          </div>
        ) : (
          <LearningPlanDashboard plan={plan} />
        )}
      </main>
    </div>
  );
}
