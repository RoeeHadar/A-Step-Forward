import { auth } from '@clerk/nextjs/server';
import { StreamingTextResponse } from 'ai';
import { agentNameSchema, chatChunkSchema } from '@asf/schemas/agents';
import { API_BASE_URL } from '@/lib/api';
import { logger } from '@/lib/logger';
import {
  fetchRecentChatTurns,
  recordChatTurn,
  getLearnerProfile,
  getConceptMastery,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';

export const runtime = 'nodejs';

// Render free tier can take up to 60s to cold-start; give it room.
const BACKEND_FETCH_TIMEOUT_MS = 90_000;
const BACKEND_MAX_ATTEMPTS = 2;
const COLD_START_GRACE_MS = 3_000;
const MAX_MEMORY_TURNS = 10;

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
}
const kgByName: Record<string, KgConcept> = Object.fromEntries(
  ((kg as { concepts: KgConcept[] }).concepts).map((c) => [c.id, c]),
);

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

  // Record the user turn (fire-and-forget, doesn't block streaming).
  void recordChatTurn(userId, agent, 'user', lastMessage);

  const gen = streamAgentResponse(userId, lastMessage, agent, isFirstTurn);
  const encoder = new TextEncoder();
  let assistantBuffer = '';
  const readable = new ReadableStream({
    async pull(controller) {
      const { value, done } = await gen.next();
      if (done) {
        controller.close();
        if (assistantBuffer) void recordChatTurn(userId, agent, 'assistant', assistantBuffer);
      } else {
        assistantBuffer += value;
        controller.enqueue(encoder.encode(value));
      }
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
      // Render backend unreachable — fall back to direct Groq call with memory + profile context.
      for await (const chunk of streamFromGroq(userId, message, agent)) {
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
      for await (const chunk of streamFromGroq(userId, message, agent)) {
        yield chunk;
      }
    }
  } catch (err) {
    logger.error('chat stream failed', { err: String(err) });
    try {
      for await (const chunk of streamFromGroq(userId, message, agent)) {
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

function findRelevantConcepts(message: string, subjects: string[]): KgConcept[] {
  if (!message) return [];
  const lower = message.toLowerCase();
  const matches: KgConcept[] = [];
  for (const concept of Object.values(kgByName)) {
    if (subjects.length && !subjects.includes(concept.subject)) continue;
    const id = concept.id.replace(/_/g, ' ');
    if (
      lower.includes(id) ||
      lower.includes(concept.name.toLowerCase()) ||
      (concept.name_he && lower.includes(concept.name_he.toLowerCase()))
    ) {
      matches.push(concept);
    }
  }
  return matches.slice(0, 3);
}

async function buildContextPrompt(
  userId: string,
  agent: string,
  message: string,
): Promise<{ system: string; memory: Array<{ role: 'user' | 'assistant'; content: string }> }> {
  const profile = await getLearnerProfile(userId).catch(() => null);
  const mastery = await getConceptMastery(userId).catch(() => ({}));
  const recent = await fetchRecentChatTurns(userId, agent, MAX_MEMORY_TURNS).catch(() => []);

  let context = AGENT_PERSONAS[agent] ?? AGENT_PERSONAS.tutor!;

  if (profile) {
    context += `\n\n## Learner profile`;
    context += `\n- Goal: ${profile.goal}`;
    if (profile.grade_level) context += `\n- Grade level: ${profile.grade_level}`;
    if (profile.points_group) context += `\n- Math units: ${profile.points_group}`;
    if (profile.subjects?.length) context += `\n- Subjects: ${profile.subjects.join(', ')}`;
    if (profile.preferred_style) context += `\n- Preferred style: ${profile.preferred_style}`;
    if (profile.hours_per_week) context += `\n- Available study time: ${profile.hours_per_week} hours/week`;
    if (profile.next_test_name && profile.next_test_date) {
      context += `\n- Next big event: ${profile.next_test_name} on ${profile.next_test_date}`;
    }
    if (profile.final_goal_date) {
      context += `\n- Final goal date: ${profile.final_goal_date}`;
    }
    const mental = profile.mental_state as Record<string, unknown> | null;
    if (mental && Object.keys(mental).length > 0) {
      const anxiety = typeof mental.anxiety === 'number' ? mental.anxiety : null;
      const motivation = typeof mental.motivation === 'number' ? mental.motivation : null;
      if (anxiety != null) context += `\n- Test anxiety: ${anxiety}/10`;
      if (motivation != null) context += `\n- Motivation: ${motivation}/10`;
      if (anxiety != null && anxiety >= 7) {
        context += `\n- IMPORTANT: This learner has high test anxiety. Be extra reassuring; avoid time pressure cues; celebrate small wins.`;
      }
    }
  }

  const weakConcepts = Object.entries(mastery)
    .filter(([, score]) => score < 0.4)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 5)
    .map(([id]) => id);
  const strongConcepts = Object.entries(mastery)
    .filter(([, score]) => score > 0.7)
    .map(([id]) => id)
    .slice(0, 5);
  if (weakConcepts.length || strongConcepts.length) {
    context += `\n\n## Mastery so far`;
    if (weakConcepts.length) context += `\n- Weak areas: ${weakConcepts.join(', ')}`;
    if (strongConcepts.length) context += `\n- Strong areas: ${strongConcepts.join(', ')}`;
  }

  const related = findRelevantConcepts(message, profile?.subjects ?? []);
  if (related.length) {
    context += `\n\n## Relevant curriculum context`;
    for (const c of related) {
      context += `\n- ${c.name} (${c.id})`;
      if (c.prerequisites?.length) context += ` — prerequisites: ${c.prerequisites.join(', ')}`;
    }
  }

  context += `\n\nKeep responses focused on this learner. Reference their goal and timeline when relevant.`;

  return {
    system: context,
    memory: recent.map((t) => ({
      role: t.role,
      content: t.content,
    })),
  };
}

async function* streamFromGroq(
  userId: string,
  message: string,
  agent: string,
): AsyncGenerator<string> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    yield getMockResponse(message, agent);
    return;
  }

  const { system, memory } = await buildContextPrompt(userId, agent, message);

  try {
    const messages: Array<{ role: string; content: string }> = [
      { role: 'system', content: system },
      ...memory,
      { role: 'user', content: message },
    ];

    const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages,
        max_tokens: 1024,
        temperature: 0.4,
        stream: true,
      }),
    });

    if (!resp.ok || !resp.body) {
      logger.warn('groq returned non-ok', { status: resp.status });
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
