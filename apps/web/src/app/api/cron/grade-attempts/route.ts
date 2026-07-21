/**
 * Cron: drain sealed grading queue (Grader agent).
 *
 * GET|POST /api/cron/grade-attempts?limit=8
 * Auth: CRON_SECRET via x-cron-secret or Bearer.
 */
import { drainPendingGradeAttempts } from '@/lib/assessment-grading';
import { dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const DEFAULT_LIMIT = 8;
const MAX_LIMIT = 20;

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
  const result = await drainPendingGradeAttempts(limit);
  return Response.json({ ok: true, ...result });
}

export async function GET(req: Request) {
  return handle(req);
}

export async function POST(req: Request) {
  return handle(req);
}
