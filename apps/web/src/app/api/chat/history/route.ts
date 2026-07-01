import { auth } from '@clerk/nextjs/server';
import { agentNameSchema } from '@asf/schemas/agents';
import { dbConfigured, fetchChatHistory, fetchChatSessionSummaries } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ messages: [], sessions: [] });
  }

  const url = new URL(req.url);
  const agentParam = url.searchParams.get('agent');
  const sessionId = url.searchParams.get('session_id');
  const limit = Math.min(100, Math.max(1, Number.parseInt(url.searchParams.get('limit') ?? '50', 10)));
  const mode = url.searchParams.get('mode') ?? 'messages';

  const parsedAgent = agentParam ? agentNameSchema.safeParse(agentParam) : null;
  const agent = parsedAgent?.success ? parsedAgent.data : agentParam ?? 'tutor';

  if (mode === 'sessions') {
    const sessions = await fetchChatSessionSummaries(
      userId,
      parsedAgent?.success ? agent : agentParam ?? undefined,
      limit,
    );
    return Response.json({ sessions });
  }

  const messages = await fetchChatHistory(userId, agent, limit, sessionId);
  return Response.json({
    messages: messages.map((m) => ({
      id: m.id,
      role: m.role,
      content: m.content,
      createdAt: m.created_at,
    })),
  });
}
