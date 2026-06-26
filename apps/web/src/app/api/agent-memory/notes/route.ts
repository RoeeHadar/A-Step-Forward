/**
 * Per-(learner, agent) cumulative additive scratchpad — list + append.
 *
 * Every learner-facing agent has its OWN private notes about THIS learner
 * that no other agent reads. The chat route loads the top-K most-useful
 * notes into the agent's system prompt each turn.
 *
 * GET  /api/agent-memory/notes?agent=tutor&limit=8
 *   → { notes: [{ id, kind, content, importance, related_concept_id, created_at }] }
 *
 * POST /api/agent-memory/notes
 *   body { agent, content, kind?, importance?, related_concept_id?, source_turn_id? }
 *   → { id }
 *
 * All operations are scoped to the authenticated Clerk userId; never accept
 * a learner_id from the request body. `agent` is validated against the
 * canonical agent name list.
 */
import { auth } from '@clerk/nextjs/server';
import { agentNameSchema } from '@asf/schemas/agents';
import {
  appendAgentNote,
  fetchAgentNotes,
  dbConfigured,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const KNOWN_NOTE_KINDS = new Set([
  'observation',
  'preference',
  'strategy',
  'open_question',
  'misconception',
  'win',
  'plan',
]);

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ notes: [] });
  const url = new URL(req.url);
  const agentRaw = url.searchParams.get('agent') ?? 'tutor';
  const limit = Math.max(1, Math.min(20, Number(url.searchParams.get('limit') ?? '8')));
  const parsed = agentNameSchema.safeParse(agentRaw);
  if (!parsed.success) {
    return Response.json({ error: 'invalid agent' }, { status: 400 });
  }
  const notes = await fetchAgentNotes(userId, parsed.data, limit);
  return Response.json({ notes });
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const body = (await req.json().catch(() => ({}))) as {
    agent?: string;
    content?: string;
    kind?: string;
    importance?: number;
    related_concept_id?: string | null;
    source_turn_id?: string | null;
  };
  const parsed = agentNameSchema.safeParse(body.agent);
  if (!parsed.success) {
    return Response.json({ error: 'invalid agent' }, { status: 400 });
  }
  if (!body.content || typeof body.content !== 'string') {
    return Response.json({ error: 'content required' }, { status: 400 });
  }
  const kind = body.kind && KNOWN_NOTE_KINDS.has(body.kind) ? body.kind : 'observation';
  const id = await appendAgentNote(userId, parsed.data, {
    kind,
    content: body.content,
    importance: body.importance ?? 3,
    related_concept_id: body.related_concept_id ?? null,
    source_turn_id: body.source_turn_id ?? null,
  });
  if (!id) return Response.json({ error: 'write_failed' }, { status: 500 });
  return Response.json({ id });
}
