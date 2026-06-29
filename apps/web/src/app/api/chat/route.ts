import { auth } from '@clerk/nextjs/server';
import { cookies } from 'next/headers';
import { agentNameSchema } from '@asf/schemas/agents';
import { logger } from '@/lib/logger';
import {
  fetchRecentChatTurns,
  recordChatTurn,
  getLearnerProfile,
  getConceptMastery,
  fetchLessonAgentHintsByConceptIds,
  getLearnerPersona,
  fetchAgentNotes,
  getDueReviews,
} from '@/lib/neon-db';
import { buildLearningPlan } from '@/lib/learning-plan';
import kg from '@/lib/kg-data.json';
import { buildAgentBaseline } from '@/lib/agent-baseline';
import { getAgentPersona } from '@/lib/agent-prompts';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';

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

  let body: { messages?: { role: string; content: string }[]; agent?: string; quickMode?: boolean; quickDuration?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'bad_request' }, { status: 400 });
  }

  const lastMessage = body.messages?.filter((m) => m.role === 'user').at(-1)?.content ?? '';
  const parsedAgent = agentNameSchema.safeParse(body.agent);
  const agent = parsedAgent.success ? parsedAgent.data : 'tutor';
  const quickMode = body.quickMode === true;
  const quickDuration = body.quickDuration ?? '15';

  // Record user turn (fire-and-forget — does not block streaming).
  void recordChatTurn(userId, agent, 'user', lastMessage);

  const gen = streamAgentResponse(userId, lastMessage, agent, { quickMode, quickDuration });
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
  opts: { quickMode?: boolean; quickDuration?: string } = {},
): AsyncGenerator<string> {
  // Direct Groq path — no Render dependency. Designed to fit comfortably
  // inside Vercel function timeouts.
  let emitted = false;
  try {
    for await (const chunk of streamFromGroq(userId, message, agent, opts)) {
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
  opts: { quickMode?: boolean; quickDuration?: string } = {},
): Promise<{ system: string; memory: Array<{ role: 'user' | 'assistant'; content: string }> }> {
  const { quickMode = false, quickDuration = '15' } = opts;
  // Each helper catches its own errors so a single DB issue cannot break chat.
  const [profile, mastery, recent, persona, agentNotes, cookieStore] = await Promise.all([
    getLearnerProfile(userId).catch(() => null),
    getConceptMastery(userId).catch(() => ({})),
    fetchRecentChatTurns(userId, agent, MAX_MEMORY_TURNS).catch(() => []),
    getLearnerPersona(userId).catch(() => null),
    fetchAgentNotes(userId, agent, 6).catch(() => []),
    cookies(),
  ]);

  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);

  // Every agent gets the same platform baseline first (corpus stats, KG
  // dimensions, agent network roster, math-LTR + bilingual rules). Then
  // its long-form persona from agent-prompts.ts. Per-turn learner data
  // (profile, mastery, relevant context, agent_hints, learning-plan) is
  // appended below.
  let context = `${buildAgentBaseline()}\n\n${getAgentPersona(agent)}`;

  if (agent === 'tutor') {
    const tutorMode =
      (profile?.personality_profile as { tutor_mode?: string } | null)?.tutor_mode ?? null;
    const learnerPref =
      tutorMode === 'direct'
        ? 'LEARNER PREFERENCE: This learner prefers direct explanations. Explain concepts clearly and fully before asking follow-up questions. Do not withhold the answer — explain first, then check understanding.'
        : 'LEARNER PREFERENCE: This learner prefers Socratic guidance. Guide with questions; do not give away the answer directly.';
    context = `${learnerPref}\n\n${context}`;
  }

  context += `\n\n## Response language`;
  context += `\n- Language preference: ${locale === 'en' ? 'English' : 'Hebrew'} — respond in this language by default`;

  if (!profile) {
    // Onboarded learners always have a profile row. A missing row means
    // either a brand-new user or a probe before onboarding. Tell the
    // agent explicitly so it doesn't pretend it knows their context.
    context += `\n\n## Brand-new learner`;
    context += `\nNo learner profile is on file yet. Open with a one-sentence orientation in Hebrew (or match the language the learner just used), and invite them to complete the 4-step onboarding at \`/onboarding\` so the rest of the agent network can plan a personalised path. Do NOT improvise a curriculum or recommend specific lessons until a profile exists.`;
  }

  // CLAUDE.md-style learner persona — shared across every agent, written by
  // the Memory Steward (and any agent allowed to). Tells you HOW this
  // learner thinks/talks/learns, NOT what they know (that's mastery).
  if (persona?.text && persona.text.trim().length > 0) {
    context += `\n\n## What I know about this learner (shared persona)`;
    context += `\n${persona.text.trim()}`;
    context += `\n_(Last updated: ${persona.updated_at ?? 'unknown'}. Refine this view by appending notes via the agent-memory API.)_`;
  }

  // Per-(learner, agent) cumulative scratchpad — your OWN private notes on
  // this learner that no other agent reads. Top N by importance.
  if (agentNotes.length > 0) {
    context += `\n\n## My private notes on this learner (agent: ${agent})`;
    context += `\nThese are your past observations, preferences you've recorded, and strategies that worked. Build on them; don't repeat them verbatim.`;
    for (const n of agentNotes) {
      const tag = n.related_concept_id ? ` [concept:${n.related_concept_id}]` : '';
      context += `\n- (${n.kind}, importance ${n.importance})${tag} ${n.content}`;
    }
    context += `\n_To save a new observation about this learner, POST \`/api/agent-memory/notes\` with { agent: "${agent}", content, importance: 1-5 }._`;
  }
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

    // Inject a learning-plan snapshot for the most-relevant concept so the
    // tutoring / curriculum / coach agents can answer "what should I study
    // next?" with a concrete, mastery-aware path rather than improvising.
    // This is the runtime surface of the cross-subject KG + skill_practice
    // walk implemented in lib/learning-plan.ts.
    if (
      agent === 'tutor' ||
      agent === 'coach' ||
      agent === 'qa_explainer' ||
      agent === 'curriculum_designer' ||
      agent === 'progress_analyzer'
    ) {
      const goal = related[0]!.id;
      const plan = await buildLearningPlan({
        learnerId: userId,
        goalConceptId: goal,
        maxNodes: 6,
      }).catch(() => null);
      if (plan && plan.path.length > 0) {
        context += `\n\n## Learning-plan snapshot (goal: ${plan.goal.name})`;
        context += `\nOrdered next steps the planner computed from the cross-subject KG + this learner's skill_practice. Use these to ground "what should I study next?" or root-cause questions.`;
        for (const node of plan.path.slice(0, 5)) {
          const pct = Math.round((1 - node.urgency) * 100);
          context += `\n- [${node.concept_id}] ${node.name}${node.name_he ? ` / ${node.name_he}` : ''} — mastery ~${pct}%${node.hasLesson ? ' (lesson available)' : ''}; ${node.why_en}`;
          if (node.weak_atoms.length > 0) {
            const tops = node.weak_atoms.slice(0, 3).map((a) => `${a.atom} ${Math.round(a.mastery * 100)}%`).join(', ');
            context += ` · weak atoms: ${tops}`;
          }
        }
        if (plan.blocking_atoms.length > 0) {
          const tops = plan.blocking_atoms.slice(0, 4).map((a) => `${a.atom} (${Math.round(a.mastery * 100)}%)`).join(', ');
          context += `\n- Most-blocking atoms across the path: ${tops}`;
        }
      }
    }
  }

  if (agent === 'coach') {
    const due = await getDueReviews(userId).catch(() => [] as Awaited<ReturnType<typeof getDueReviews>>);
    context += `\n\n## Spaced-repetition queue (FSRS)`;
    if (due.length > 0) {
      const list = due
        .map((d) => `${d.concept_name} (atom: ${d.atom_id}, last score ${Math.round(d.last_score * 100)}%)`)
        .join('; ');
      context += `\nDUE FOR REVIEW TODAY: ${list}. Start by drilling these before introducing new material. For each, generate a fresh question and evaluate the answer.`;
    } else {
      context += `\nNo items due for review. Focus on the learner's weakest concepts from their mastery data.`;
    }
    if (quickMode) {
      context += `\n\n## Quick session mode`;
      context += `\nThis is a ${quickDuration}-minute focused session. Keep ALL responses concise (≤3 sentences + question). Open immediately with one targeted drill question on the highest-priority weak concept or due item. No preamble. After ${quickDuration} minutes of interaction, summarise what was covered and suggest the next session topic.`;
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
  opts: { quickMode?: boolean; quickDuration?: string } = {},
): AsyncGenerator<string> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    logger.warn('GROQ_API_KEY missing — skipping Groq');
    return;
  }

  let context: Awaited<ReturnType<typeof buildContextPrompt>>;
  try {
    context = await buildContextPrompt(userId, agent, message, opts);
  } catch (err) {
    logger.warn('buildContextPrompt failed, using bare persona', { err: String(err) });
    const bareSystem = `${buildAgentBaseline()}\n\n${getAgentPersona(agent)}`;
    context = { system: bareSystem, memory: [] };
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
