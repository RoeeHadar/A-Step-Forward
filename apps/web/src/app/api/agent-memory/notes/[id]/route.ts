/**
 * Archive or supersede a single agent note. Used by the consolidation pass
 * and by agents that want to retract a stale observation.
 *
 * DELETE /api/agent-memory/notes/<id>             → archive
 * PATCH  /api/agent-memory/notes/<id>  { by: id } → supersede
 */
import { auth } from '@clerk/nextjs/server';
import { supersedeAgentNote, dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const { id } = await params;
  if (!UUID_RE.test(id)) return Response.json({ error: 'bad id' }, { status: 400 });
  await supersedeAgentNote(id, null);
  return Response.json({ ok: true });
}

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });
  const { id } = await params;
  if (!UUID_RE.test(id)) return Response.json({ error: 'bad id' }, { status: 400 });
  const body = (await req.json().catch(() => ({}))) as { by?: string };
  if (!body.by || !UUID_RE.test(body.by)) {
    return Response.json({ error: 'by required' }, { status: 400 });
  }
  await supersedeAgentNote(id, body.by);
  return Response.json({ ok: true });
}
