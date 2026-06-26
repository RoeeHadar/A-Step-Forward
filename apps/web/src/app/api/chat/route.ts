import { auth } from '@clerk/nextjs/server';
import { StreamingTextResponse } from 'ai';
import { agentNameSchema } from '@asf/schemas/agents';
import { logger } from '@/lib/logger';
import {
  fetchRecentChatTurns,
  recordChatTurn,
  getLearnerProfile,
  getConceptMastery,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';

export const runtime = 'nodejs';

// Vercel functions have a 60s timeout on Pro, 10s on Hobby for non-streaming.
// We stream, so the connection stays open as long as we keep yielding chunks.
// Keep the upstream LLM timeout well under that.
const GROQ_TIMEOUT_MS = 25_000;
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

  let body: { messages?: { role: string; content: string }[]; agent?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return new Response('Bad request', { status: 400 });
  }

  const lastMessage = body.messages?.filter((m) => m.role === 'user').at(-1)?.content ?? '';
  const parsedAgent = agentNameSchema.safeParse(body.agent);
  const agent = parsedAgent.success ? parsedAgent.data : 'tutor';

  // Record user turn (fire-and-forget — does not block streaming).
  void recordChatTurn(userId, agent, 'user', lastMessage);

  const gen = streamAgentResponse(userId, lastMessage, agent);
  const encoder = new TextEncoder();
  let assistantBuffer = '';
  const readable = new ReadableStream({
    async pull(controller) {
      try {
        const { value, done } = await gen.next();
        if (done) {
          controller.close();
          if (assistantBuffer) void recordChatTurn(userId, agent, 'assistant', assistantBuffer);
        } else {
          assistantBuffer += value;
          controller.enqueue(encoder.encode(value));
        }
      } catch (err) {
        logger.error('chat stream pull failed', { err: String(err) });
        // Emit a friendly text and close, so the client never sees a network error.
        const fallback = friendlyFallback(lastMessage, agent);
        assistantBuffer += fallback;
        controller.enqueue(encoder.encode(fallback));
        controller.close();
        if (assistantBuffer) void recordChatTurn(userId, agent, 'assistant', assistantBuffer);
      }
    },
  });
  return new StreamingTextResponse(readable);
}

async function* streamAgentResponse(
  userId: string,
  message: string,
  agent: string,
): AsyncGenerator<string> {
  // Direct Groq path — no Render dependency. Designed to fit comfortably
  // inside Vercel function timeouts.
  let emitted = false;
  try {
    for await (const chunk of streamFromGroq(userId, message, agent)) {
      emitted = true;
      yield chunk;
    }
  } catch (err) {
    logger.warn('groq stream raised', { err: String(err) });
  }
  if (!emitted) {
    yield friendlyFallback(message, agent);
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
  // Each helper catches its own errors so a single DB issue cannot break chat.
  const [profile, mastery, recent] = await Promise.all([
    getLearnerProfile(userId).catch(() => null),
    getConceptMastery(userId).catch(() => ({})),
    fetchRecentChatTurns(userId, agent, MAX_MEMORY_TURNS).catch(() => []),
  ]);

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
    memory: recent.map((t) => ({ role: t.role, content: t.content })),
  };
}

const GROQ_MODELS = [
  'llama-3.3-70b-versatile',
  'llama-3.1-70b-versatile',
  'llama-3.1-8b-instant',
];

async function* streamFromGroq(
  userId: string,
  message: string,
  agent: string,
): AsyncGenerator<string> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    logger.warn('GROQ_API_KEY missing — skipping Groq');
    return;
  }

  let context: Awaited<ReturnType<typeof buildContextPrompt>>;
  try {
    context = await buildContextPrompt(userId, agent, message);
  } catch (err) {
    logger.warn('buildContextPrompt failed, using bare persona', { err: String(err) });
    context = { system: AGENT_PERSONAS[agent] ?? AGENT_PERSONAS.tutor!, memory: [] };
  }

  const messages: Array<{ role: string; content: string }> = [
    { role: 'system', content: context.system },
    ...context.memory,
    { role: 'user', content: message },
  ];

  // Try each model with its own short timeout; fall through on 429 / 5xx / network errors.
  for (const model of GROQ_MODELS) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), GROQ_TIMEOUT_MS);
    try {
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages,
          max_tokens: 1024,
          temperature: 0.4,
          stream: true,
        }),
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) {
        const status = resp.status;
        clearTimeout(timeoutId);
        logger.warn('groq non-ok, trying next model', { status, model });
        if (status === 401 || status === 403) {
          // Bad key — no point retrying with other models.
          return;
        }
        continue;
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
      clearTimeout(timeoutId);
      if (emitted) return; // success
    } catch (err) {
      clearTimeout(timeoutId);
      logger.warn('groq attempt threw', { model, err: String(err) });
    }
  }
}

/**
 * Friendly response when no LLM can be reached. We still personalize the
 * preview of the user message so it doesn't feel robotic.
 */
function friendlyFallback(message: string, agent: string): string {
  const preview = message.slice(0, 120);
  const heads: Record<string, string> = {
    tutor: "I'm your Tutor.",
    mentor: "I'm your Mentor.",
    coach: "I'm your Coach.",
    reviewer: "I'm your Reviewer.",
    qa_explainer: "I'm your Q&A explainer.",
    note_taker: "I'm your Note-taker.",
  };
  const head = heads[agent] ?? "I'm your assistant.";
  return [
    `${head} Our language model is temporarily unreachable, so I cannot answer in real time right now.`,
    '',
    preview ? `You asked: *"${preview}"*` : '',
    '',
    'Two things you can do right now:',
    '- Refresh in a moment — the model usually returns within a minute.',
    '- Browse the **/learn** section for curated explanations on this topic.',
    '',
    'Your message is saved in your chat history, so I will see it next turn.',
  ]
    .filter(Boolean)
    .join('\n');
}
