import Link from 'next/link';
import { auth } from '@clerk/nextjs/server';
import { SiteHeader } from '@/components/site-header';
import { LearningPlanDashboard } from '@/components/learning-plan-dashboard';
import { getCurrentPlan, dbConfigured } from '@/lib/neon-db';
import { ensureOnboarded } from '@/lib/onboarding-gate';
import { Button } from '@asf/ui/button';

export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  const { userId } = await auth();
  if (!userId) {
    return null;
  }

  await ensureOnboarded(userId, '/dashboard');
  const plan = dbConfigured ? await getCurrentPlan(userId).catch(() => null) : null;

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
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
