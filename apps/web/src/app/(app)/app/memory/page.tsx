import { redirect } from 'next/navigation';
import { MemoryPageContent } from '@/components/memory-page-content';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured, getLearnerMemorySnapshot } from '@/lib/neon-db';

export const dynamic = 'force-dynamic';

export default async function MemoryPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const snapshot = dbConfigured
    ? await getLearnerMemorySnapshot(auth.learnerId).catch(() => null)
    : null;

  return (
    <MemoryPageContent
      snapshot={
        snapshot ?? {
          profile: null,
          persona: { text: null, updated_at: null },
          notesByAgent: {},
          totalNoteCount: 0,
          weakConcepts: [],
          strongConcepts: [],
          activePlanGoal: null,
          activeWeekConceptIds: [],
          recentChatTurns: [],
          lastUpdated: null,
        }
      }
    />
  );
}
