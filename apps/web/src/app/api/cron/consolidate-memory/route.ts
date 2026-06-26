/**
 * Cron-callable sweep: run the heavy memory consolidation pass for every
 * learner that has accumulated enough live notes to justify a pass.
 *
 * GET  /api/cron/consolidate-memory
 *   - Vercel cron uses GET. We accept GET and POST.
 *   - Authentication: requires header `x-cron-secret` (or `Authorization: Bearer <secret>`)
 *     matching `process.env.CRON_SECRET`. Vercel auto-attaches the bearer
 *     for crons configured in vercel.json.
 *
 * Body / query (optional):
 *   ?limit=N   cap the number of learners processed in one invocation
 *              (default 25, max 100). Use a small cap on Hobby; the
 *              endpoint is safe to call multiple times back-to-back since
 *              it's a "needs consolidation" workqueue.
 *
 * Schedule (see apps/web/vercel.json `crons[]`): weekly, Sunday 03:00 UTC.
 */
import {
  consolidateLearnerMemory,
  listLearnersWithLiveNotes,
} from '@/lib/persona-consolidator';
import { dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const DEFAULT_LIMIT = 25;
const MAX_LIMIT = 100;

function authorized(req: Request): boolean {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false; // refuse to run if not configured
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
  const learners = (await listLearnersWithLiveNotes()).slice(0, limit);
  const results = [] as Array<{ learner_id: string; ran: boolean; archived: number }>;
  let totalArchived = 0;
  let totalRan = 0;
  for (const learnerId of learners) {
    try {
      const r = await consolidateLearnerMemory(learnerId);
      if (r.ran) totalRan += 1;
      totalArchived += r.notes_archived;
      results.push({ learner_id: learnerId, ran: r.ran, archived: r.notes_archived });
    } catch (err) {
      results.push({
        learner_id: learnerId,
        ran: false,
        archived: 0,
      });
      if (process.env.NODE_ENV !== 'production') {
        console.warn('[cron/consolidate-memory] failure for', learnerId, err);
      }
    }
  }
  return Response.json({
    candidates: learners.length,
    runs_completed: totalRan,
    notes_archived: totalArchived,
    per_learner: results,
  });
}

export async function GET(req: Request) {
  return handle(req);
}

export async function POST(req: Request) {
  return handle(req);
}
