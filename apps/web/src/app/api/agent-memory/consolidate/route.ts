/**
 * Heavy LLM-driven consolidation of one learner's agent notes into the
 * shared persona. Authed; runs for the calling Clerk userId.
 *
 * POST /api/agent-memory/consolidate
 *   body: { force?: boolean }
 *   → ConsolidationResult (see persona-consolidator.ts)
 *
 * Use cases:
 *   - "Rebuild now" button in /settings/persona
 *   - Educator / admin tooling that wants a per-learner pass
 *
 * The route delegates to the cron-callable sweep at
 * `/api/cron/consolidate-memory` (CRON_SECRET-gated) for the all-learners
 * weekly pass.
 */
import { auth } from '@clerk/nextjs/server';
import { consolidateLearnerMemory } from '@/lib/persona-consolidator';
import { dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
// Consolidation does one LLM round-trip; allow generous headroom for Groq.
export const maxDuration = 60;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const body = (await req.json().catch(() => ({}))) as { force?: boolean };
  const result = await consolidateLearnerMemory(userId, { force: Boolean(body.force) });
  return Response.json(result);
}
