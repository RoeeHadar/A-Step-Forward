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
import { LLMGuardError } from '@/lib/llm/guarded-client';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
// Consolidation does one LLM round-trip; allow generous headroom for Groq.
export const maxDuration = 60;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const body = (await req.json().catch(() => ({}))) as { force?: boolean };
  try {
    const result = await consolidateLearnerMemory(userId, { force: Boolean(body.force) });
    return Response.json(result);
  } catch (err) {
    // AS-100: guard errors (unknown model, non-Groq base URL) are server config
    // problems; return a handled JSON error without echoing env values.
    const guard = err instanceof LLMGuardError;
    logger.error('agent-memory/consolidate failed', { kind: guard ? 'llm_guard' : 'unknown' });
    return Response.json(
      { error: guard ? 'llm_misconfigured' : 'consolidation_failed' },
      { status: guard ? 503 : 500 },
    );
  }
}
