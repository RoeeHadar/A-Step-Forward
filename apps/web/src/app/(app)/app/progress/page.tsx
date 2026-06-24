import { redirect } from 'next/navigation';
import { ProgressPageContent } from '@/components/progress-page-content';
import { getAuthContext } from '@/lib/auth';
import { fetchProgress } from '@/lib/data';

export default async function ProgressPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const progress = await fetchProgress(auth);

  return <ProgressPageContent progress={progress} />;
}
