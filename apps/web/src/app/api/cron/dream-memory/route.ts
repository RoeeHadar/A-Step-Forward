/**
 * Cron-callable sweep: lightweight dreaming for every learner with live notes.
 *
 * GET/POST /api/cron/dream-memory
 *   - Auth: `x-cron-secret` or `Authorization: Bearer` matching CRON_SECRET.
 *   - Query: ?limit=N (default 50, max 200)
 *
 * Schedule (apps/web/vercel.json): Monday 00:00 UTC — start of week, before
 * heavy consolidation. No LLM calls; safe to batch many learners.
 */
import {
  dreamLearnerMemory,
  listLearnersWithAnyLiveNotes,
} from '@/lib/agent-memory-dream';
import { dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const DEFAULT_LIMIT = 50;
const MAX_LIMIT = 200;

function authorized(req: Request): boolean {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false;
  const header =
    req.headers.get('x-cron-secret') ??
    (req.headers.get('authorization') ?? '').replace(/^Bearer\s+/i, '');
  return header === secret;
}

async function handle(req: Request) {
  if (!authorized(req)) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'db_unavailable' }, { status: 503 });
  }

  const url = new URL(req.url);
  const limit = Math.max(
    1,
    Math.min(MAX_LIMIT, Number(url.searchParams.get('limit') ?? DEFAULT_LIMIT)),
  );

  const learners = await listLearnersWithAnyLiveNotes(limit);
  const results: Array<{
    learner_id: string;
    archived: number;
    superseded: number;
    agents_processed: number;
  }> = [];

  let totalArchived = 0;
  let totalSuperseded = 0;
  let totalAgents = 0;

  for (const learnerId of learners) {
    try {
      const r = await dreamLearnerMemory(learnerId, { scope: 'live' });
      totalArchived += r.archived;
      totalSuperseded += r.superseded;
      totalAgents += r.agents_processed;
      results.push({
        learner_id: learnerId,
        archived: r.archived,
        superseded: r.superseded,
        agents_processed: r.agents_processed,
      });
    } catch (err) {
      results.push({
        learner_id: learnerId,
        archived: 0,
        superseded: 0,
        agents_processed: 0,
      });
      console.error(
        JSON.stringify({ tag: '[ASF_CRON_DREAM_FAIL]', learner_id: learnerId, err: String(err) }),
      );
    }
  }

  console.log(
    JSON.stringify({
      tag: '[ASF_CRON_DREAM]',
      candidates: learners.length,
      notes_archived: totalArchived,
      notes_superseded: totalSuperseded,
      agents_processed: totalAgents,
    }),
  );

  return Response.json({
    candidates: learners.length,
    notes_archived: totalArchived,
    notes_superseded: totalSuperseded,
    agents_processed: totalAgents,
    per_learner: results,
  });
}

export async function GET(req: Request) {
  return handle(req);
}

export async function POST(req: Request) {
  return handle(req);
}
