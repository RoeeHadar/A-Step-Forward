import { redirect } from 'next/navigation';
import { PageHeader } from '@/components/page-header';
import { MemoryInspector } from '@/components/memory-inspector';
import { getAuthContext } from '@/lib/auth';
import { fetchMemories } from '@/lib/data';

export default async function MemoryPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const memories = await fetchMemories(auth);

  return (
    <div>
      <PageHeader
        title="Memory Inspector"
        description="View, search, edit, and delete memories stored about you. All changes are audited."
      />
      <MemoryInspector memories={memories} />
    </div>
  );
}
