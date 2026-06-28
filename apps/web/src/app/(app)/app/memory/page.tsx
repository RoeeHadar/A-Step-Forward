import { redirect } from 'next/navigation';
import { MemoryPageContent } from '@/components/memory-page-content';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured, getMemoryTimelineFromNeon } from '@/lib/neon-db';
import { fetchMemories } from '@/lib/data';

export default async function MemoryPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const memories = dbConfigured
    ? await getMemoryTimelineFromNeon(auth.learnerId).catch(() => [])
    : await fetchMemories(auth);

  return <MemoryPageContent memories={memories} />;
}
