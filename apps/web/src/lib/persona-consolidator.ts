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
 * Skill reference: `.cursor/skills/memory-steward-consolidate/SKILL.md`.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import {
  getLearnerPersona,
  persistConsolidationResult,
  ensureMemoryClaimColumns,
  type LearnerPersona,
  type LearnerAgentNote,
} from '@/lib/neon-db';
import { llmCompleteJson } from '@/lib/llm-provider';

neonConfig.fetchConnectionCache = true;
const sql = process.env.DATABASE_URL ? neon(process.env.DATABASE_URL) : null;

// Quality knobs.
const PERSONA_CHAR_CAP = 4000;
const MIN_NOTES_TO_CONSOLIDATE = 6;
const MAX_NOTES_PER_RUN = 80;

/**
 * Single-instance concurrency guard: tracks which learner IDs are currently
 * being consolidated within this Vercel function instance. Prevents two
 * concurrent requests (e.g. user "Rebuild" button + cron overlap) from both
 * paying the LLM cost and writing conflicting personas.
 *
 * For distributed concurrency across multiple Vercel instances the write-side
 * advisory lock inside `persistConsolidationResult` (neon-db.ts) acts as the
 * backstop — only one writer wins; the other gets `consolidation_in_progress`.
 */
const consolidatingNow = new Set<string>();

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
4. Use markdown with H2 section headers. Recommended sections (skip any with no signal).
   Prefer Hebrew headers (product default):
     ## איך הם מדברים
     ## איך הם אוהבים הסברים
     ## טריגרים והעדפות
     ## תצפיות יציבות אחרונות
   English headers (How they talk / How they like explanations / Triggers and preferences /
   Recent durable observations) are acceptable only when the existing persona is already English
   and the live notes are English-only.
5. Each section is a bulleted list. Each bullet is one short sentence. No paragraphs.
6. Preserve existing persona structure where the notes do not contradict it. Replace only when a note clearly supersedes an old bullet.
7. Only promote a note into "promoted_ids" if its content is actually represented in the new persona body. Importance 4-5 notes that are HOW-related almost always get promoted; importance 1-2 notes rarely do.
8. NEVER fabricate new patterns not present in the input. If you have nothing to add, return the old persona verbatim.
9. Total persona length MUST be <= 4000 characters including whitespace.
10. Write the persona in **Hebrew** by default (learner-facing Memory page). Keep concept_ids and
    math in Latin script. If the current persona and notes are overwhelmingly English, you may
    keep English — but never leave English "Diagnostic calibration" dumps when a Hebrew
    equivalent exists in the notes.`;

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

interface ConsolidationJsonResult extends Record<string, unknown> {
  persona: string;
  promoted_ids: string[];
  notes?: string;
}

async function callLLMForConsolidation(
  systemPrompt: string,
  userPrompt: string,
): Promise<{ json: ConsolidationJsonResult; model: string } | null> {
  const result = await llmCompleteJson<ConsolidationJsonResult>({
    system: systemPrompt,
    messages: [{ role: 'user', content: userPrompt }],
    maxTokens: 2048,
    temperature: 0.2,
    timeoutMs: 25_000,
    modelTier: 'cheap',
    jsonMode: true,
  });
  if (!result) return null;
  if (typeof result.json.persona !== 'string' || !Array.isArray(result.json.promoted_ids)) {
    return null;
  }
  return { json: result.json, model: result.model };
}

/**
 * Consolidate the live per-(learner, agent) notes for one learner into the
 * shared persona. Returns a summary of what was done. Safe to call when
 * `LLM_API_KEY` is missing (returns `{ ran: false, reason: 'no_llm' }`).
 *
 * Concurrency guards (layered):
 * 1. Same-instance: `consolidatingNow` Set — fast path, no DB round-trip.
 * 2. Cross-instance: `UPDATE learner_profiles SET consolidation_started_at = NOW()
 *    WHERE … RETURNING learner_id` — atomic conditional claim; 0 rows means
 *    another Vercel instance is already consolidating this learner. The claim
 *    is released (set to NULL) in the `finally` block.
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

  // Ensure cross-instance claim columns exist (once per cold start, non-fatal).
  await ensureMemoryClaimColumns();

  // Layer 1 — same-instance guard (fast path, no DB round-trip).
  if (consolidatingNow.has(learnerId)) {
    return {
      ran: false,
      reason: 'consolidation_in_progress',
      persona_chars_before: 0,
      persona_chars_after: 0,
      notes_considered: 0,
      notes_archived: 0,
    };
  }
  consolidatingNow.add(learnerId);

  // Layer 2 — cross-instance DB claim.
  let dbClaimed = false;
  try {
    const claimed = (await sql`
      UPDATE learner_profiles
      SET consolidation_started_at = NOW()
      WHERE learner_id = ${learnerId}
        AND (consolidation_started_at IS NULL OR consolidation_started_at < NOW() - INTERVAL '10 minutes')
      RETURNING learner_id
    `) as Array<{ learner_id: string }>;
    if (claimed.length === 0) {
      // Another instance claimed this learner — release in-memory guard and skip.
      consolidatingNow.delete(learnerId);
      return {
        ran: false,
        reason: 'consolidation_in_progress',
        persona_chars_before: 0,
        persona_chars_after: 0,
        notes_considered: 0,
        notes_archived: 0,
      };
    }
    dbClaimed = true;
  } catch {
    // Column may not exist yet (race on first cold start) — fall through and
    // rely on the same-instance guard and the write-side advisory lock only.
  }

  try {
    return await _consolidateLearnerMemoryInner(learnerId, opts);
  } finally {
    consolidatingNow.delete(learnerId);
    // Release the DB claim so the next run can pick this learner up again.
    if (dbClaimed) {
      await (sql`
        UPDATE learner_profiles SET consolidation_started_at = NULL WHERE learner_id = ${learnerId}
      ` as Promise<unknown>).catch(() => {});
    }
  }
}

async function _consolidateLearnerMemoryInner(
  learnerId: string,
  opts: { force?: boolean } = {},
): Promise<ConsolidationResult> {
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

  const result = await callLLMForConsolidation(SYSTEM_PROMPT, buildUserPrompt(currentPersona, notes));
  if (!result) {
    return {
      ran: false,
      reason: 'llm_unavailable_or_parse_failed',
      persona_chars_before: currentPersona.length,
      persona_chars_after: currentPersona.length,
      notes_considered: notes.length,
      notes_archived: 0,
    };
  }

  const nextPersona = result.json.persona.slice(0, PERSONA_CHAR_CAP);
  const liveIds = new Set(notes.map((n) => n.id));
  const validPromoted = result.json.promoted_ids.filter((id) => liveIds.has(id));

  const writeResult = await persistConsolidationResult(learnerId, nextPersona, validPromoted);
  if (!writeResult.ok) {
    return {
      ran: false,
      reason: writeResult.reason,
      persona_chars_before: currentPersona.length,
      persona_chars_after: currentPersona.length,
      notes_considered: notes.length,
      notes_archived: 0,
    };
  }

  return {
    ran: true,
    persona_chars_before: currentPersona.length,
    persona_chars_after: nextPersona.length,
    notes_considered: notes.length,
    notes_archived: validPromoted.length,
    model: result.model,
  };
}

/**
 * Returns the set of learner ids that have at least `minNotes` live notes
 * across all their agents — i.e. the cron sweep work-list.
 * Ordered by `MIN(created_at) ASC` so learners with the oldest unprocessed
 * notes are processed first, guaranteeing fair FIFO convergence over
 * successive cron runs (no learner is perpetually skipped).
 * `limit` is pushed to the DB so we never materialise an unbounded result set.
 */
export async function listLearnersWithLiveNotes(
  minNotes = MIN_NOTES_TO_CONSOLIDATE,
  limit = 100,
): Promise<string[]> {
  if (!sql) return [];
  const rows = (await sql`
    SELECT learner_id
    FROM learner_agent_notes
    WHERE archived_at IS NULL AND superseded_by IS NULL
    GROUP BY learner_id
    HAVING COUNT(*) >= ${minNotes}
    ORDER BY MIN(created_at) ASC
    LIMIT ${limit}
  `) as Array<{ learner_id: string }>;
  return rows.map((r) => r.learner_id);
}
