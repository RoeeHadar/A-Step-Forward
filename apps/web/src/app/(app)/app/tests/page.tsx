import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured } from '@/lib/neon-db';
import { listTestAttempts } from '@/lib/test-attempts';
import { TestsArchiveList } from '@/components/tests-archive';

export const dynamic = 'force-dynamic';

export default async function TestsPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const items = dbConfigured
    ? await listTestAttempts(auth.learnerId, 30).catch(() => [])
    : [];

  return (
    <div className="container max-w-4xl py-8">
      <TestsArchiveList items={items} />
    </div>
  );
}
