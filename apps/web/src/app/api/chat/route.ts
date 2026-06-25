import { auth } from '@clerk/nextjs/server';
import { StreamingTextResponse } from 'ai';
import { agentNameSchema, chatChunkSchema } from '@asf/schemas/agents';
import { API_BASE_URL } from '@/lib/api';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';

// Render free tier can take up to 60s to cold-start; give it room.
const BACKEND_FETCH_TIMEOUT_MS = 90_000;
const BACKEND_MAX_ATTEMPTS = 2;
const COLD_START_GRACE_MS = 3_000;

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
      // Render backend unreachable — fall back to direct Groq call
      for await (const chunk of streamFromGroq(message, agent)) {
        yield chunk;
      }
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
      for await (const chunk of streamFromGroq(message, agent)) {
        yield chunk;
      }
    }
  } catch (err) {
    logger.error('chat stream failed', { err: String(err) });
    try {
      for await (const chunk of streamFromGroq(message, agent)) {
        yield chunk;
      }
    } catch {
      yield "I'm having trouble connecting right now. Please try again shortly.";
    }
  }
}

const AGENT_PERSONAS: Record<string, string> = {
  tutor:
    "You are the Tutor for A Step Forward, an AI-native learning center. Use the Socratic method — ask guiding questions, give worked examples when asked, and adapt difficulty to the learner. Reply in the learner's language (Hebrew or English). Be warm, concise, and concrete.",
  mentor:
    "You are the Mentor for A Step Forward. Help learners set goals, build study habits, and stay motivated. Reply in the learner's language. Be empathetic, direct, and actionable.",
  coach:
    "You are the Coach for A Step Forward. Run practice drills and spaced-repetition reviews. Reply in the learner's language. Be encouraging but rigorous.",
  reviewer:
    "You are the Reviewer for A Step Forward. Give specific, line-level feedback on code, essays, or solutions. Reply in the learner's language. Be precise and kind.",
  qa_explainer:
    "You are the QA Explainer for A Step Forward. Answer learner questions with a clear, cited explanation. Reply in the learner's language. Be accurate and concrete.",
  note_taker:
    "You are the Note Taker for A Step Forward. Summarize and organize learner notes. Reply in the learner's language. Be structured and brief.",
};

async function* streamFromGroq(message: string, agent: string): AsyncGenerator<string> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    yield getMockResponse(message, agent);
    return;
  }

  const persona = AGENT_PERSONAS[agent] ?? AGENT_PERSONAS.tutor;

  try {
    const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: persona },
          { role: 'user', content: message },
        ],
        max_tokens: 1024,
        temperature: 0.4,
        stream: true,
      }),
    });

    if (!resp.ok || !resp.body) {
      yield getMockResponse(message, agent);
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let emitted = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = line.slice(6).trim();
        if (data === '[DONE]') break;
        try {
          const parsed = JSON.parse(data) as {
            choices?: Array<{ delta?: { content?: string } }>;
          };
          const token = parsed.choices?.[0]?.delta?.content;
          if (token) {
            emitted = true;
            yield token;
          }
        } catch {
          // ignore parse errors
        }
      }
    }

    if (!emitted) {
      yield getMockResponse(message, agent);
    }
  } catch (err) {
    logger.warn('groq fallback failed', { err: String(err) });
    yield getMockResponse(message, agent);
  }
}

function getMockResponse(message: string, agent: string): string {
  const preview = message.slice(0, 80);
  return `**${agent}**: That's a great question about "${preview}". Let me guide you — what do you already know about this topic? I'll help you discover the answer step by step.`;
}
