import { redirect } from 'next/navigation';
import { PageHeader } from '@/components/page-header';
import { ProgressDashboard } from '@/components/progress-dashboard';
import { getAuthContext } from '@/lib/auth';
import { fetchProgress } from '@/lib/data';

export default async function ProgressPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const progress = await fetchProgress(auth);

  return (
    <div>
      <PageHeader title="Progress" description="Track your mastery, streaks, and learning trends" />
      <ProgressDashboard progress={progress} />
    </div>
  );
}
