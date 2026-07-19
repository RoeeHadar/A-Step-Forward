import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured } from '@/lib/neon-db';
import { getTestAttempt } from '@/lib/test-attempts';
import { TestAttemptView } from '@/components/tests-archive';

export const dynamic = 'force-dynamic';

export default async function TestDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const { id } = await params;
  const attempt = dbConfigured ? await getTestAttempt(auth.learnerId, id).catch(() => null) : null;

  if (!attempt) redirect('/app/tests');

  return (
    <div className="container max-w-3xl py-8">
      <TestAttemptView attempt={attempt} />
    </div>
  );
}
