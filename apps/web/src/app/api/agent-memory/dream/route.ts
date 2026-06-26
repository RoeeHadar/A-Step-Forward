/**
 * Lightweight per-(learner, agent) dreaming / consolidation pass.
 *
 * This is the Vercel-friendly, deterministic version of the consolidation
 * pipeline documented in `skills/dreaming-and-consolidation/SKILL.md`. It
 * is safe to call on-demand from a settings page button, from a Vercel
 * cron, or as part of a heavier nightly job that delegates the LLM
 * summarisation to the Memory Steward.
 *
 * What this pass does (no LLM call — pure SQL / TS):
 *
 *   1. For each (learner, agent) over the cap, archive the lowest-importance
 *      + oldest notes until at or below `MAX_LIVE_NOTES_PER_AGENT`.
 *   2. Detect near-duplicate notes by token-set Jaccard ≥
 *      `DUP_JACCARD`; supersede the older with the newer (so the chain
 *      from old → new is preserved for audit).
 *   3. Report what changed.
 *
 * What this pass does NOT do (delegated to the heavier Memory Steward pass):
 *
 *   - LLM-driven summarisation into the learner persona.
 *   - Cross-agent conflict resolution.
 *   - KG projection.
 *
 * POST body: { agent?: AgentName }
 *   - If `agent` is omitted, runs over all agents the learner has notes for.
 *
 * Returns: { archived, superseded, agents_processed }.
 */
import { auth } from '@clerk/nextjs/server';
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { agentNameSchema, type AgentName } from '@asf/schemas/agents';
import {
  supersedeAgentNote,
  dbConfigured,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const MAX_LIVE_NOTES_PER_AGENT = 30;
const DUP_JACCARD = 0.6;

neonConfig.fetchConnectionCache = true;
const sql = process.env.DATABASE_URL ? neon(process.env.DATABASE_URL) : null;

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
    ORDER BY created_at DESC
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

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'db_unavailable' }, { status: 503 });

  const body = (await req.json().catch(() => ({}))) as { agent?: string };
  let agents: string[];
  if (body.agent) {
    const parsed = agentNameSchema.safeParse(body.agent);
    if (!parsed.success) {
      return Response.json({ error: 'invalid agent' }, { status: 400 });
    }
    agents = [parsed.data as AgentName];
  } else {
    agents = await listAgentsWithNotes(userId);
  }

  let archived = 0;
  let superseded = 0;
  for (const agent of agents) {
    const notes = await liveNotes(userId, agent);
    if (notes.length === 0) continue;

    // 1. Near-duplicate detection: for each note, compare to the most
    //    recent N=20 newer notes; if jaccard >= threshold, supersede the
    //    OLDER by the NEWER.
    const tokenSets = notes.map((n) => tokenSet(n.content));
    const supersededIds = new Set<string>();
    for (let i = 0; i < notes.length; i += 1) {
      if (supersededIds.has(notes[i]!.id)) continue;
      for (let j = i + 1; j < notes.length && j < i + 20; j += 1) {
        if (supersededIds.has(notes[j]!.id)) continue;
        const sim = jaccard(tokenSets[i]!, tokenSets[j]!);
        if (sim >= DUP_JACCARD) {
          // `notes` is ordered DESC by created_at, so notes[i] is newer
          // than notes[j]. The older one (j) gets superseded by the newer
          // (i).
          await supersedeAgentNote(notes[j]!.id, notes[i]!.id);
          supersededIds.add(notes[j]!.id);
          superseded += 1;
        }
      }
    }

    // 2. Cap: if still over MAX_LIVE_NOTES_PER_AGENT, archive lowest
    //    importance + oldest first.
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
  }

  return Response.json({
    archived,
    superseded,
    agents_processed: agents.length,
  });
}
