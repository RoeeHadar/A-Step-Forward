import { redirect } from 'next/navigation';
import { DashboardContent } from '@/components/dashboard-content';
import { getAuthContext } from '@/lib/auth';
import {
  getDashboardSnapshot,
  getLearnerProfile,
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

  const [snapshot, profile] = await Promise.all([
    dbConfigured
      ? getDashboardSnapshot(auth.learnerId).catch(emptySnapshot)
      : Promise.resolve(emptySnapshot()),
    dbConfigured
      ? getLearnerProfile(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
  ]);

  return (
    <DashboardContent
      displayName={auth.displayName}
      snapshot={snapshot}
      nextTestName={profile?.next_test_name ?? null}
      nextTestDate={profile?.next_test_date ?? null}
    />
  );
}
