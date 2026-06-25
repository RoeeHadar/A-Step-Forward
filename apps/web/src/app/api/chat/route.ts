import { auth } from '@clerk/nextjs/server';
import { StreamingTextResponse } from 'ai';
import { agentNameSchema, chatChunkSchema } from '@asf/schemas/agents';
import { API_BASE_URL } from '@/lib/api';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';

const BACKEND_FETCH_TIMEOUT_MS = 55_000;
const BACKEND_MAX_ATTEMPTS = 1;
const COLD_START_GRACE_MS = 2_000;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }

  const body = (await req.json()) as {
    messages?: { role: string; content: string }[];
    agent?: string;
  };
  const lastMessage = body.messages?.filter((m) => m.role === 'user').at(-1)?.content ?? '';
  const parsedAgent = agentNameSchema.safeParse(body.agent);
  const agent = parsedAgent.success ? parsedAgent.data : 'tutor';

  const isFirstTurn = (body.messages?.filter((m) => m.role === 'user').length ?? 0) <= 1;
  const gen = streamAgentResponse(userId, lastMessage, agent, isFirstTurn);
  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async pull(controller) {
      const { value, done } = await gen.next();
      if (done) controller.close();
      else controller.enqueue(encoder.encode(value));
    },
  });
  return new StreamingTextResponse(readable);
}

async function fetchBackendChat(userId: string, message: string, agent: string): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), BACKEND_FETCH_TIMEOUT_MS);

  try {
    return await fetch(`${API_BASE_URL}/v1/chat`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'X-Learner-Id': userId,
        'X-Role': 'learner',
      },
      body: JSON.stringify({
        learner_id: userId,
        message,
        requested_agent: agent,
        locale: 'en',
      }),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function* streamAgentResponse(
  userId: string,
  message: string,
  agent: string,
  isFirstTurn: boolean,
): AsyncGenerator<string> {
  try {
    if (isFirstTurn) {
      fetch(`${API_BASE_URL}/v1/warmup`).catch(() => {});
      await new Promise((r) => setTimeout(r, COLD_START_GRACE_MS));
    }

    let res: Response | null = null;

    for (let attempt = 0; attempt < BACKEND_MAX_ATTEMPTS; attempt++) {
      try {
        const attemptRes = await fetchBackendChat(userId, message, agent);
        if (attemptRes.ok && attemptRes.body) {
          res = attemptRes;
          break;
        }
        if (attempt < BACKEND_MAX_ATTEMPTS - 1) {
          logger.warn('chat backend returned non-ok, retrying', {
            status: attemptRes.status,
            attempt,
          });
          await new Promise((r) => setTimeout(r, 3000));
        }
      } catch (err) {
        if (attempt < BACKEND_MAX_ATTEMPTS - 1) {
          logger.warn('chat backend fetch failed, retrying', { attempt, err: String(err) });
          await new Promise((r) => setTimeout(r, 3000));
        } else {
          throw err;
        }
      }
    }

    if (!res?.ok || !res.body) {
      yield getMockResponse(message, agent);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let emitted = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop() ?? '';

      for (const event of events) {
        const dataLine = event.split('\n').find((l) => l.startsWith('data: '));
        if (!dataLine) continue;
        const raw = dataLine.slice(6);
        try {
          const chunk = chatChunkSchema.parse(JSON.parse(raw));
          if (chunk.kind === 'token' && chunk.text) {
            emitted = true;
            yield chunk.text;
          }
        } catch {
          // skip malformed SSE chunks
        }
      }
    }

    if (!emitted) {
      yield getMockResponse(message, agent);
    }
  } catch (err) {
    logger.error('chat stream failed', { err: String(err) });
    yield "I'm having trouble connecting right now. Please try again shortly.";
  }
}

function getMockResponse(message: string, agent: string): string {
  const preview = message.slice(0, 80);
  return `**${agent}**: That's a great question about "${preview}". Let me guide you — what do you already know about this topic? I'll help you discover the answer step by step.`;
}
