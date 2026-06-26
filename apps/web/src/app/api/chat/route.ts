import { auth } from '@clerk/nextjs/server';
import { agentNameSchema } from '@asf/schemas/agents';
import { logger } from '@/lib/logger';
import {
  fetchRecentChatTurns,
  recordChatTurn,
  getLearnerProfile,
  getConceptMastery,
  fetchLessonAgentHintsByConceptIds,
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
  let userId: string | null = null;
  try {
    const a = await auth();
    userId = a.userId;
  } catch (err) {
    logger.error('chat: auth() threw', { err: String(err) });
    return Response.json({ error: 'auth_failed' }, { status: 401 });
  }
  if (!userId) {
    return Response.json({ error: 'unauthorized' }, { status: 401 });
  }

  let body: { messages?: { role: string; content: string }[]; agent?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'bad_request' }, { status: 400 });
  }

  const lastMessage = body.messages?.filter((m) => m.role === 'user').at(-1)?.content ?? '';
  const parsedAgent = agentNameSchema.safeParse(body.agent);
  const agent = parsedAgent.success ? parsedAgent.data : 'tutor';

  // Record user turn (fire-and-forget — does not block streaming).
  void recordChatTurn(userId, agent, 'user', lastMessage);

  const gen = streamAgentResponse(userId, lastMessage, agent);
  const encoder = new TextEncoder();
  let assistantBuffer = '';

  // Vercel AI SDK "data stream" protocol: every text token is emitted on its
  // own line, prefixed by `0:` and JSON-stringified, terminated with `\n`.
  // The final line is `d:{...}` for the finish message. This is the format
  // useChat expects by default.
  const encodeToken = (text: string) => encoder.encode(`0:${JSON.stringify(text)}\n`);
  const encodeFinish = () =>
    encoder.encode(`d:${JSON.stringify({ finishReason: 'stop', usage: { promptTokens: 0, completionTokens: 0 } })}\n`);

  const readable = new ReadableStream({
    async pull(controller) {
      try {
        const { value, done } = await gen.next();
        if (done) {
          controller.enqueue(encodeFinish());
          controller.close();
          if (assistantBuffer) void recordChatTurn(userId, agent, 'assistant', assistantBuffer);
        } else {
          assistantBuffer += value;
          controller.enqueue(encodeToken(value));
        }
      } catch (err) {
        logger.error('chat stream pull failed', { err: String(err) });
        const fallback = friendlyFallback(lastMessage, agent);
        assistantBuffer += fallback;
        controller.enqueue(encodeToken(fallback));
        controller.enqueue(encodeFinish());
        controller.close();
        if (assistantBuffer) void recordChatTurn(userId, agent, 'assistant', assistantBuffer);
      }
    },
  });

  return new Response(readable, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Vercel-AI-Data-Stream': 'v1',
      'Cache-Control': 'no-cache, no-transform',
    },
  });
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

    // Inject agent_hints from the matching AI-authored lessons so the Tutor
    // can ground its reply in the canonical key insights, pacing hints, and
    // common-misconception triggers we authored per concept.
    if (agent === 'tutor' || agent === 'coach' || agent === 'qa_explainer') {
      const hintsRows = await fetchLessonAgentHintsByConceptIds(related.map((c) => c.id)).catch(
        () => [] as Awaited<ReturnType<typeof fetchLessonAgentHintsByConceptIds>>,
      );
      if (hintsRows.length) {
        context += `\n\n## Lesson-level guidance for the AI-authored corpus`;
        const lowerMsg = message.toLowerCase();
        for (const row of hintsRows) {
          const h = row.agent_hints ?? {};
          context += `\n\n### ${row.title_en} (${row.concept_id})`;
          if (h.key_insights?.length) {
            context += `\n- Key insights:`;
            for (const k of h.key_insights.slice(0, 4)) context += `\n  - ${k}`;
          }
          if (h.tutor_pacing_hint) {
            context += `\n- Pacing hint: ${h.tutor_pacing_hint}`;
          }
          if (h.common_misconceptions?.length) {
            const triggered = h.common_misconceptions.filter((m) => {
              const en = m.detect_phrase_en?.toLowerCase();
              const he = m.detect_phrase_he;
              return (
                (en && lowerMsg.includes(en)) ||
                (he && message.includes(he))
              );
            });
            const toShow = triggered.length > 0 ? triggered : h.common_misconceptions.slice(0, 2);
            context += `\n- Misconception watch:`;
            for (const m of toShow) {
              context += `\n  - "${m.wrong}" → ${m.correction}`;
            }
            if (triggered.length > 0) {
              context += `\n- IMPORTANT: the learner's last message appears to express a known misconception above. Open your reply with a gentle, targeted correction before answering the rest.`;
            }
          }
          if (h.diagnostic_signals && Object.keys(h.diagnostic_signals).length) {
            const entries = Object.entries(h.diagnostic_signals).slice(0, 3);
            context += `\n- Diagnostic moves:`;
            for (const [signal, move] of entries) {
              context += `\n  - If "${signal}": ${move}`;
            }
          }
          if (h.skill_atoms_unlocked?.length) {
            context += `\n- Skills this lesson develops: ${h.skill_atoms_unlocked.slice(0, 6).join(', ')}`;
          }
        }
      }
    }
  }

  context += `\n\nKeep responses focused on this learner. Reference their goal and timeline when relevant.`;

  return {
    system: context,
    memory: recent.map((t) => ({ role: t.role, content: t.content })),
  };
}

// Ordered from highest quality to fastest fallback. We try each in turn on
// transient failure (429 / 5xx / network). ``llama-3.1-70b-versatile`` was
// retired by Groq in 2025 and intentionally omitted.
const GROQ_MODELS = [
  'llama-3.3-70b-versatile',
  'llama-3.1-8b-instant',
  'gemma2-9b-it',
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
