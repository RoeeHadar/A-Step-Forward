import { redirect } from 'next/navigation';
import { DashboardContent } from '@/components/dashboard-content';
import { getAuthContext } from '@/lib/auth';
import {
  getDashboardSnapshot,
  dbConfigured,
  type DashboardSnapshot,
} from '@/lib/neon-db';

export const dynamic = 'force-dynamic';

function emptySnapshot(): DashboardSnapshot {
  return {
    stats: { streak_days: 0, lessons_completed: 0, level: 1 },
    recent_lessons: [],
    mastery_summary: [],
  };
}

export default async function DashboardPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  // Real, per-learner snapshot from Neon — no MOCK_DASHBOARD fallback.
  // A brand-new learner with zero activity gets the empty snapshot, which the
  // UI renders as "no lessons yet" / "no mastery yet" / streak 0.
  const snapshot = dbConfigured
    ? await getDashboardSnapshot(auth.learnerId).catch(emptySnapshot)
    : emptySnapshot();

  return (
    <DashboardContent
      displayName={auth.displayName}
      snapshot={snapshot}
    />
  );
}
