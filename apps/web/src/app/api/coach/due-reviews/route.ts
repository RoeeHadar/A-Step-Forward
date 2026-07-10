import { auth } from '@clerk/nextjs/server';
import { getCurrentPlan, getDueReviews, getLearnerProfile } from '@/lib/neon-db';
import { filterDueReviewsForProfile } from '@/lib/coach-session-context';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const [rawItems, profile, plan] = await Promise.all([
    getDueReviews(userId),
    getLearnerProfile(userId).catch(() => null),
    getCurrentPlan(userId).catch(() => null),
  ]);
  const planConceptIds = new Set(
    plan?.weeks.flatMap((w) => w.concepts.map((c) => c.concept_id)) ?? [],
  );
  const items = filterDueReviewsForProfile(rawItems, {
    subjects: profile?.subjects ?? [],
    planConceptIds: planConceptIds.size > 0 ? planConceptIds : undefined,
  });
  return Response.json({ items, count: items.length });
}