import { auth } from '@clerk/nextjs/server';
import 'server-only';
import { dbConfigured } from '@/lib/neon-db';
import { buildLearningPlan } from '@/lib/learning-plan';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/learning-plan/next?goal=<conceptId>&max=<n>
 *
 * Returns the next sequenced learning step toward the requested goal concept,
 * derived from the cross-subject knowledge graph + the learner's per-skill
 * mastery in `skill_practice`. Consumed by the Curriculum Designer agent,
 * the Coach drill loop, and (eventually) a learner dashboard card.
 */
export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  const url = new URL(req.url);
  const goal = url.searchParams.get('goal');
  if (!goal) {
    return Response.json({ error: 'goal query param required' }, { status: 400 });
  }
  const maxRaw = url.searchParams.get('max');
  const maxNodes = maxRaw ? Math.max(1, Math.min(30, Number.parseInt(maxRaw, 10))) : 12;

  const plan = await buildLearningPlan({
    learnerId: userId,
    goalConceptId: goal,
    maxNodes,
  });
  if (!plan) {
    return Response.json(
      { error: `unknown goal concept "${goal}"` },
      { status: 404 },
    );
  }
  return Response.json(plan);
}
