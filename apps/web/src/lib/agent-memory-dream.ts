/**
 * Lightweight per-(learner, agent) dreaming — deterministic, no LLM.
 *
 * Companion to `POST /api/agent-memory/dream` and the weekly Vercel cron at
 * `/api/cron/dream-memory`. See `.cursor/skills/dreaming-and-consolidation/SKILL.md`.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { supersedeAgentNote, dbConfigured } from '@/lib/neon-db';
import { WEB_LIVE_AGENTS } from '@/lib/web-agents';

neonConfig.fetchConnectionCache = true;
const sql = process.env.DATABASE_URL ? neon(process.env.DATABASE_URL) : null;

export const MAX_LIVE_NOTES_PER_AGENT = 30;
export const DUP_JACCARD = 0.6;

/** Max notes fetched per (learner, agent) per dream pass — bounds per-invocation work. */
const DREAM_NOTES_FETCH_LIMIT = 100;
/** Minimum ms between dream passes for the same learnerId (single-instance guard). */
const DREAM_COOLDOWN_MS = 5 * 60 * 1000;

/**
 * Per-learnerId timestamp of the last dream pass start. Prevents double-processing
 * within a single Vercel instance. For distributed concurrency the LIMIT already
 * bounds per-invocation cost; a DB-level `last_dreamed_at` conditional UPDATE would
 * be the ideal cross-instance guard (requires a migration to add the column).
 */
const dreamLastStarted = new Map<string, number>();

export interface DreamPassResult {
  archived: number;
  superseded: number;
  agents_processed: number;
}

interface NoteRow {
  id: string;
  agent: string;
  content: string;
  importance: number;
  created_at: string;
}

function tokenSet(s: string): Set<string> {
  return new Set(
    s
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s]/gu, ' ')
      .split(/\s+/)
      .filter((t) => t.length >= 3),
  );
}

function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 || b.size === 0) return 0;
  let intersect = 0;
  for (const x of a) if (b.has(x)) intersect += 1;
  const union = a.size + b.size - intersect;
  return union > 0 ? intersect / union : 0;
}

async function liveNotes(learnerId: string, agent: string): Promise<NoteRow[]> {
  if (!sql) return [];
  const rows = (await sql`
    SELECT id::text, agent, content, importance, created_at
    FROM learner_agent_notes
    WHERE learner_id = ${learnerId} AND agent = ${agent}
      AND archived_at IS NULL AND superseded_by IS NULL
    ORDER BY importance DESC, created_at DESC
    LIMIT ${DREAM_NOTES_FETCH_LIMIT}
  `) as NoteRow[];
  return rows;
}

async function listAgentsWithNotes(learnerId: string): Promise<string[]> {
  if (!sql) return [];
  const rows = (await sql`
    SELECT DISTINCT agent
    FROM learner_agent_notes
    WHERE learner_id = ${learnerId} AND archived_at IS NULL AND superseded_by IS NULL
  `) as Array<{ agent: string }>;
  return rows.map((r) => r.agent);
}

async function dreamOneAgent(learnerId: string, agent: string): Promise<DreamPassResult> {
  const notes = await liveNotes(learnerId, agent);
  if (notes.length === 0) {
    return { archived: 0, superseded: 0, agents_processed: 0 };
  }

  let archived = 0;
  let superseded = 0;
  const tokenSets = notes.map((n) => tokenSet(n.content));
  const supersededIds = new Set<string>();

  for (let i = 0; i < notes.length; i += 1) {
    if (supersededIds.has(notes[i]!.id)) continue;
    for (let j = i + 1; j < notes.length && j < i + 20; j += 1) {
      if (supersededIds.has(notes[j]!.id)) continue;
      const sim = jaccard(tokenSets[i]!, tokenSets[j]!);
      if (sim >= DUP_JACCARD) {
        await supersedeAgentNote(notes[j]!.id, notes[i]!.id);
        supersededIds.add(notes[j]!.id);
        superseded += 1;
      }
    }
  }

  const remaining = notes.filter((n) => !supersededIds.has(n.id));
  if (remaining.length > MAX_LIVE_NOTES_PER_AGENT) {
    const sorted = [...remaining].sort((a, b) => {
      if (a.importance !== b.importance) return a.importance - b.importance;
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    });
    const toArchive = sorted.slice(0, remaining.length - MAX_LIVE_NOTES_PER_AGENT);
    for (const n of toArchive) {
      await supersedeAgentNote(n.id, null);
      archived += 1;
    }
  }

  return { archived, superseded, agents_processed: 1 };
}

/**
 * Run the lightweight dream pass for one learner.
 * When `agents` is omitted, processes every agent that has live notes.
 * When `scope` is `live`, only the four website agents are processed.
 *
 * Includes a single-instance cooldown guard (DREAM_COOLDOWN_MS) to prevent
 * double-processing from concurrent calls within the same Vercel instance.
 * Fetches at most DREAM_NOTES_FETCH_LIMIT notes per (learner, agent) so a
 * single invocation is bounded even for very large note sets; convergence
 * happens over successive cron runs.
 */
export async function dreamLearnerMemory(
  learnerId: string,
  opts: { agents?: string[]; scope?: 'all' | 'live' } = {},
): Promise<DreamPassResult> {
  if (!dbConfigured) {
    return { archived: 0, superseded: 0, agents_processed: 0 };
  }

  // Single-instance concurrency guard: skip if a pass ran recently.
  const lastStarted = dreamLastStarted.get(learnerId) ?? 0;
  if (Date.now() - lastStarted < DREAM_COOLDOWN_MS) {
    return { archived: 0, superseded: 0, agents_processed: 0 };
  }
  dreamLastStarted.set(learnerId, Date.now());

  let agents: string[];
  if (opts.agents?.length) {
    agents = opts.agents;
  } else if (opts.scope === 'live') {
    const withNotes = await listAgentsWithNotes(learnerId);
    agents = withNotes.filter((a) => (WEB_LIVE_AGENTS as readonly string[]).includes(a));
  } else {
    agents = await listAgentsWithNotes(learnerId);
  }

  let archived = 0;
  let superseded = 0;
  let agentsProcessed = 0;

  for (const agent of agents) {
    if (opts.scope === 'live' && !(WEB_LIVE_AGENTS as readonly string[]).includes(agent)) {
      continue;
    }
    const parsed = agentNameSchema.safeParse(agent);
    if (!parsed.success) continue;
    const r = await dreamOneAgent(learnerId, parsed.data as AgentName);
    if (r.agents_processed > 0) agentsProcessed += 1;
    archived += r.archived;
    superseded += r.superseded;
  }

  return { archived, superseded, agents_processed: agentsProcessed };
}

/** Learners with at least one live agent note — cron work-list for dreaming.
 *  `limit` is applied at the DB level to avoid fetching an unbounded result set.
 */
export async function listLearnersWithAnyLiveNotes(limit = 200): Promise<string[]> {
  if (!sql) return [];
  const rows = (await sql`
    SELECT DISTINCT learner_id
    FROM learner_agent_notes
    WHERE archived_at IS NULL AND superseded_by IS NULL
    LIMIT ${limit}
  `) as Array<{ learner_id: string }>;
  return rows.map((r) => r.learner_id);
}
