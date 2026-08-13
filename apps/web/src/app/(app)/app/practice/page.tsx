/**
 * /app/practice — intensive practice arena (ADR-0013 v2).
 */
import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { PracticeArenaClient } from '@/components/practice-arena-client';
import { getLearnerProfile } from '@/lib/neon-db';
import { parsePracticeQueueMode } from '@/lib/practice-arena';
import { parsePracticeTopicIds } from '@/lib/practice-topics';

export const dynamic = 'force-dynamic';

export default async function PracticePage({
  searchParams,
}: {
  searchParams: Promise<{ concept?: string; mode?: string; topics?: string }>;
}) {
  const ctx = await getAuthContext();
  if (!ctx) redirect('/sign-in');
  const sp = await searchParams;
  const concept =
    typeof sp.concept === 'string' && sp.concept.trim() ? sp.concept.trim() : null;

  let initialTopicIds: string[] = [];
  if (typeof sp.topics === 'string' && sp.topics.trim()) {
    initialTopicIds = parsePracticeTopicIds(sp.topics.split(','));
  } else {
    const profile = await getLearnerProfile(ctx.userId).catch(() => null);
    const remembered = (profile?.personality_profile as { last_practice_topic_ids?: unknown } | null)
      ?.last_practice_topic_ids;
    initialTopicIds = parsePracticeTopicIds(remembered);
  }

  return (
    <PracticeArenaClient
      initialConceptId={concept}
      initialTopicIds={initialTopicIds}
      initialQueueMode={parsePracticeQueueMode(sp.mode)}
    />
  );
}
