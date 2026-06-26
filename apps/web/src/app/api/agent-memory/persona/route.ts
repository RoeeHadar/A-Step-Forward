/**
 * Per-learner, CLAUDE.md-style persona — read and write.
 *
 * The persona is a free-form markdown summary of HOW this learner thinks,
 * talks, and learns (not WHAT they know — that's `concept_mastery`). All
 * runtime agents read it on every chat turn via the chat route. Any agent
 * (or admin tool) can update it via this endpoint.
 *
 * GET                    → returns { text, updated_at }
 * POST   { text }        → replaces the persona (full overwrite, 4000 char cap)
 * PATCH  { section, line } → appends a single bullet under `## <section>`,
 *                              idempotent on exact duplicates
 *
 * All operations are scoped to the authenticated Clerk userId; never accept
 * a learner_id from the request body.
 */
import { auth } from '@clerk/nextjs/server';
import {
  appendLearnerPersonaLine,
  getLearnerPersona,
  setLearnerPersona,
  dbConfigured,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ text: null, updated_at: null });
  const persona = await getLearnerPersona(userId);
  return Response.json({
    text: persona?.text ?? null,
    updated_at: persona?.updated_at ?? null,
  });
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const body = (await req.json().catch(() => ({}))) as { text?: string };
  if (typeof body.text !== 'string') {
    return Response.json({ error: 'text required' }, { status: 400 });
  }
  await setLearnerPersona(userId, body.text);
  return Response.json({ ok: true });
}

export async function PATCH(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const body = (await req.json().catch(() => ({}))) as {
    section?: string;
    line?: string;
  };
  if (!body.section || !body.line) {
    return Response.json({ error: 'section and line required' }, { status: 400 });
  }
  await appendLearnerPersonaLine(userId, body.section, body.line);
  return Response.json({ ok: true });
}
