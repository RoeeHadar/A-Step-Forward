/**
 * Memory Steward — heavy, LLM-driven consolidation of per-(learner, agent)
 * notes into the shared learner persona.
 *
 * This is the "heavy" companion to the deterministic web-runtime dreaming
 * pass at `/api/agent-memory/dream`:
 *
 *   - Deterministic pass (`dream`): cap + Jaccard dedupe per agent. No LLM.
 *   - Heavy pass (this file): a single Groq call per learner reads every
 *     live note across every agent + the current persona, and returns a
 *     consolidated persona body + the ids of notes that have been promoted
 *     into it (and can therefore be archived).
 *
 * The pass is intentionally token-cheap and idempotent: same inputs ->
 * same output. The model is told:
 *
 *   - never to invent new facts
 *   - never to keep PII (names, schools, contact details)
 *   - to focus on HOW the learner thinks/talks/learns (not WHAT they know)
 *   - to keep the result under 4000 chars (the hard cap on the column)
 *   - to return a structured JSON envelope
 *
 * Runtime callers:
 *   - `POST /api/agent-memory/consolidate` (authed, per-user "rebuild now")
 *   - `POST /api/cron/consolidate-memory`  (CRON_SECRET, weekly sweep)
 *
 * Skill reference: `skills/memory-steward-consolidate/SKILL.md`.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import {
  getLearnerPersona,
  setLearnerPersona,
  supersedeAgentNote,
  type LearnerPersona,
  type LearnerAgentNote,
} from '@/lib/neon-db';

neonConfig.fetchConnectionCache = true;
const sql = process.env.DATABASE_URL ? neon(process.env.DATABASE_URL) : null;

// Quality knobs.
const PERSONA_CHAR_CAP = 4000;
const MIN_NOTES_TO_CONSOLIDATE = 6;
const MAX_NOTES_PER_RUN = 80;
const GROQ_TIMEOUT_MS = 25_000;
const GROQ_MODELS = [
  'llama-3.3-70b-versatile',
  'llama-3.1-8b-instant',
  'gemma2-9b-it',
];

export interface ConsolidationResult {
  ran: boolean;
  reason?: string;
  persona_chars_before: number;
  persona_chars_after: number;
  notes_considered: number;
  notes_archived: number;
  model?: string;
}

interface LiveNote extends LearnerAgentNote {
  agent: string;
}

async function fetchAllLiveNotes(learnerId: string): Promise<LiveNote[]> {
  if (!sql) return [];
  const rows = (await sql`
    SELECT id::text, learner_id, agent, kind, content, importance,
           related_concept_id, source_turn_id::text AS source_turn_id,
           created_at, last_referenced_at
    FROM learner_agent_notes
    WHERE learner_id = ${learnerId}
      AND archived_at IS NULL
      AND superseded_by IS NULL
    ORDER BY importance DESC, created_at DESC
    LIMIT ${MAX_NOTES_PER_RUN}
  `) as LiveNote[];
  return rows;
}

const SYSTEM_PROMPT = `You are the Memory Steward for an AI tutoring platform. Your job is to consolidate per-agent observations about a single learner into a durable, free-form "shared persona" that every agent reads on every turn.

Rules — non-negotiable:
1. Output STRICT JSON only, no prose around it. Shape:
   { "persona": "<markdown body, <= 4000 chars>", "promoted_ids": ["<note id>", ...], "notes": "<optional 1-line audit note>" }
2. The persona summarises HOW this learner thinks, talks, and learns — NOT what concepts they have mastered (that lives in concept_mastery).
3. NEVER include PII: no real names, school names, emails, phone numbers, addresses. If you see any in the notes, drop the whole line.
4. Use markdown with H2 section headers. Recommended sections (skip any with no signal):
     ## How they talk
     ## How they like explanations
     ## Triggers and preferences
     ## Recent durable observations (rolling, last 30d)
5. Each section is a bulleted list. Each bullet is one short sentence. No paragraphs.
6. Preserve existing persona structure where the notes do not contradict it. Replace only when a note clearly supersedes an old bullet.
7. Only promote a note into "promoted_ids" if its content is actually represented in the new persona body. Importance 4-5 notes that are HOW-related almost always get promoted; importance 1-2 notes rarely do.
8. NEVER fabricate new patterns not present in the input. If you have nothing to add, return the old persona verbatim.
9. Total persona length MUST be <= 4000 characters including whitespace.
10. Write the persona in English (it is an internal coordination document); agents will mirror the learner's language in chat regardless.`;

function buildUserPrompt(
  currentPersona: string,
  notes: LiveNote[],
): string {
  const linesByAgent = new Map<string, string[]>();
  for (const n of notes) {
    const arr = linesByAgent.get(n.agent) ?? [];
    const tag = n.related_concept_id ? ` [concept:${n.related_concept_id}]` : '';
    arr.push(`- id=${n.id} kind=${n.kind} importance=${n.importance}${tag} :: ${n.content}`);
    linesByAgent.set(n.agent, arr);
  }
  const noteBlocks = [...linesByAgent.entries()]
    .map(([agent, lines]) => `### agent: ${agent}\n${lines.join('\n')}`)
    .join('\n\n');

  return [
    '## Current persona',
    currentPersona.trim() || '(empty — first consolidation pass)',
    '',
    '## Live notes from every agent',
    `Total: ${notes.length} notes across ${linesByAgent.size} agents.`,
    '',
    noteBlocks,
    '',
    'Produce the consolidated persona JSON now.',
  ].join('\n');
}

interface GroqJsonResult {
  persona: string;
  promoted_ids: string[];
  notes?: string;
}

async function callGroq(
  systemPrompt: string,
  userPrompt: string,
): Promise<{ json: GroqJsonResult; model: string } | null> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) return null;
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
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt },
          ],
          response_format: { type: 'json_object' },
          max_tokens: 2048,
          temperature: 0.2,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (!resp.ok) {
        if (resp.status === 401 || resp.status === 403) return null;
        continue;
      }
      const body = (await resp.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      const raw = body.choices?.[0]?.message?.content;
      if (!raw) continue;
      let parsed: GroqJsonResult;
      try {
        parsed = JSON.parse(raw) as GroqJsonResult;
      } catch {
        continue;
      }
      if (typeof parsed.persona !== 'string' || !Array.isArray(parsed.promoted_ids)) {
        continue;
      }
      return { json: parsed, model };
    } catch {
      clearTimeout(timeoutId);
    }
  }
  return null;
}

/**
 * Consolidate the live per-(learner, agent) notes for one learner into the
 * shared persona. Returns a summary of what was done. Safe to call when
 * `GROQ_API_KEY` is missing (returns `{ ran: false, reason: 'no_groq' }`).
 */
export async function consolidateLearnerMemory(
  learnerId: string,
  opts: { force?: boolean } = {},
): Promise<ConsolidationResult> {
  if (!sql) {
    return {
      ran: false,
      reason: 'db_unavailable',
      persona_chars_before: 0,
      persona_chars_after: 0,
      notes_considered: 0,
      notes_archived: 0,
    };
  }
  const [persona, notes]: [LearnerPersona | null, LiveNote[]] = await Promise.all([
    getLearnerPersona(learnerId),
    fetchAllLiveNotes(learnerId),
  ]);
  const currentPersona = persona?.text ?? '';
  if (!opts.force && notes.length < MIN_NOTES_TO_CONSOLIDATE) {
    return {
      ran: false,
      reason: `notes_below_threshold (${notes.length} < ${MIN_NOTES_TO_CONSOLIDATE})`,
      persona_chars_before: currentPersona.length,
      persona_chars_after: currentPersona.length,
      notes_considered: notes.length,
      notes_archived: 0,
    };
  }
  const result = await callGroq(SYSTEM_PROMPT, buildUserPrompt(currentPersona, notes));
  if (!result) {
    return {
      ran: false,
      reason: 'groq_unavailable_or_parse_failed',
      persona_chars_before: currentPersona.length,
      persona_chars_after: currentPersona.length,
      notes_considered: notes.length,
      notes_archived: 0,
    };
  }
  const nextPersona = result.json.persona.slice(0, PERSONA_CHAR_CAP);
  await setLearnerPersona(learnerId, nextPersona);

  // Archive only ids we explicitly recognise (defence against hallucinated ids).
  const liveIds = new Set(notes.map((n) => n.id));
  const validPromoted = result.json.promoted_ids.filter((id) => liveIds.has(id));
  let archived = 0;
  for (const id of validPromoted) {
    await supersedeAgentNote(id, null);
    archived += 1;
  }
  return {
    ran: true,
    persona_chars_before: currentPersona.length,
    persona_chars_after: nextPersona.length,
    notes_considered: notes.length,
    notes_archived: archived,
    model: result.model,
  };
}

/**
 * Returns the set of learner ids that have at least `minNotes` live notes
 * across all their agents — i.e. the cron sweep work-list.
 */
export async function listLearnersWithLiveNotes(
  minNotes = MIN_NOTES_TO_CONSOLIDATE,
): Promise<string[]> {
  if (!sql) return [];
  const rows = (await sql`
    SELECT learner_id
    FROM learner_agent_notes
    WHERE archived_at IS NULL AND superseded_by IS NULL
    GROUP BY learner_id
    HAVING COUNT(*) >= ${minNotes}
  `) as Array<{ learner_id: string }>;
  return rows.map((r) => r.learner_id);
}
