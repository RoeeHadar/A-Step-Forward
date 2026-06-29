/**
 * GET /api/progress/estimated-grade?subject=math_5
 *
 * Returns an estimated Bagrut exam grade for the authenticated learner.
 * Averages `concept_mastery.score` for concepts in the given subject (from
 * the knowledge graph) and maps to an approximate exam grade:
 *
 *   avg ≥ 0.9 → 95   avg ≥ 0.8 → 85   avg ≥ 0.7 → 75
 *   avg ≥ 0.6 → 65   avg ≥ 0.5 → 55   else      → 45
 *
 * If `?subject=` is omitted, averages across ALL concepts.
 */
import { auth } from '@clerk/nextjs/server';
import { getEstimatedBagrutScore } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const subject = url.searchParams.get('subject') ?? undefined;

  const result = await getEstimatedBagrutScore(userId, subject ?? '');
  return Response.json(result);
}
