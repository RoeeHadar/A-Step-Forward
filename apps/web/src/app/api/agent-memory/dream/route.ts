/**
 * Lightweight per-(learner, agent) dreaming / consolidation pass.
 *
 * Delegates to `lib/agent-memory-dream.ts`. See
 * `.cursor/skills/dreaming-and-consolidation/SKILL.md`.
 */
import { auth } from '@clerk/nextjs/server';
import 'server-only';
import { agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { dreamLearnerMemory } from '@/lib/agent-memory-dream';
import { dbConfigured } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });

  const body = (await req.json().catch(() => ({}))) as { agent?: string };
  let agents: string[] | undefined;
  if (body.agent) {
    const parsed = agentNameSchema.safeParse(body.agent);
    if (!parsed.success) {
      return Response.json({ error: 'invalid agent' }, { status: 400 });
    }
    agents = [parsed.data as AgentName];
  }

  const result = await dreamLearnerMemory(userId, { agents, scope: agents ? 'all' : 'live' });
  return Response.json(result);
}
