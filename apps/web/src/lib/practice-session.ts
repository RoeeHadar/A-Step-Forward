/**
 * Neon persistence for practice sessions (ADR-0013).
 * Keys stay server-side until submit / give-up / hint unlock.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import {
  stripPracticeItemForClient,
  type PracticeItemSealed,
  type PracticeSessionPublic,
  PRACTICE_DEFAULT_GOAL_ITEMS,
  PRACTICE_DEFAULT_GOAL_MINUTES,
} from '@/lib/practice-arena';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export interface PracticeSessionRow {
  id: string;
  user_id: string;
  goal_items: number;
  goal_minutes: number;
  concept_filter: string | null;
  focus_concept_id: string | null;
  attempted: number;
  correct_count: number;
  hints_used: number;
  generated_count: number;
  seen_ids: string[];
  recent_correct: boolean[];
  current_item: PracticeItemSealed | null;
  hint_step: number;
  /** True after submit/give-up on current_item until /next advances. */
  current_graded: boolean;
  version: number;
  queue_mode: 'default' | 'due';
  status: 'active' | 'ended';
}

async function ensurePracticeTables(): Promise<void> {
  if (!sql) return;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS practice_sessions (
        id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id           TEXT NOT NULL,
        goal_items        INT NOT NULL DEFAULT 10,
        goal_minutes      INT NOT NULL DEFAULT 15,
        concept_filter    TEXT,
        focus_concept_id  TEXT,
        attempted         INT NOT NULL DEFAULT 0,
        correct_count     INT NOT NULL DEFAULT 0,
        hints_used        INT NOT NULL DEFAULT 0,
        generated_count   INT NOT NULL DEFAULT 0,
        seen_ids          JSONB NOT NULL DEFAULT '[]'::jsonb,
        recent_correct    JSONB NOT NULL DEFAULT '[]'::jsonb,
        current_item      JSONB,
        hint_step         INT NOT NULL DEFAULT 0,
        current_graded    BOOLEAN NOT NULL DEFAULT FALSE,
        version           INT NOT NULL DEFAULT 0,
        queue_mode        TEXT NOT NULL DEFAULT 'default',
        status            TEXT NOT NULL DEFAULT 'active',
        created_at        TIMESTAMPTZ DEFAULT NOW(),
        ended_at          TIMESTAMPTZ
      )
    `;
    await sql`ALTER TABLE practice_sessions ADD COLUMN IF NOT EXISTS current_graded BOOLEAN NOT NULL DEFAULT FALSE`;
    await sql`ALTER TABLE practice_sessions ADD COLUMN IF NOT EXISTS version INT NOT NULL DEFAULT 0`;
    await sql`ALTER TABLE practice_sessions ADD COLUMN IF NOT EXISTS queue_mode TEXT NOT NULL DEFAULT 'default'`;
    await sql`
      CREATE INDEX IF NOT EXISTS ix_practice_sessions_user
      ON practice_sessions (user_id, created_at DESC)
    `;
  } catch {
    // concurrent DDL
  }
}

function parseJsonArray<T>(raw: unknown, fallback: T[]): T[] {
  if (Array.isArray(raw)) return raw as T[];
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw) as unknown;
      return Array.isArray(parsed) ? (parsed as T[]) : fallback;
    } catch {
      return fallback;
    }
  }
  return fallback;
}

function rowToSession(r: Record<string, unknown>): PracticeSessionRow {
  return {
    id: String(r.id),
    user_id: String(r.user_id),
    goal_items: Number(r.goal_items) || PRACTICE_DEFAULT_GOAL_ITEMS,
    goal_minutes: Number(r.goal_minutes) || PRACTICE_DEFAULT_GOAL_MINUTES,
    concept_filter: (r.concept_filter as string | null) ?? null,
    focus_concept_id: (r.focus_concept_id as string | null) ?? null,
    attempted: Number(r.attempted) || 0,
    correct_count: Number(r.correct_count) || 0,
    hints_used: Number(r.hints_used) || 0,
    generated_count: Number(r.generated_count) || 0,
    seen_ids: parseJsonArray<string>(r.seen_ids, []),
    recent_correct: parseJsonArray<boolean>(r.recent_correct, []),
    current_item: (r.current_item as PracticeItemSealed | null) ?? null,
    hint_step: Number(r.hint_step) || 0,
    current_graded: Boolean(r.current_graded),
    version: Number(r.version) || 0,
    queue_mode: r.queue_mode === 'due' ? 'due' : 'default',
    status: r.status === 'ended' ? 'ended' : 'active',
  };
}

export function toPracticeSessionPublic(row: PracticeSessionRow): PracticeSessionPublic {
  return {
    session_id: row.id,
    goal_items: row.goal_items,
    goal_minutes: row.goal_minutes,
    attempted: row.attempted,
    correct_count: row.correct_count,
    hints_used: row.hints_used,
    concept_filter: row.concept_filter,
    focus_concept_id: row.focus_concept_id,
    item: row.current_item
      ? stripPracticeItemForClient(row.current_item, row.hint_step)
      : null,
    item_graded: row.current_graded,
    queue_mode: row.queue_mode,
    status: row.status,
  };
}

export async function createPracticeSession(opts: {
  learnerId: string;
  goalItems?: number;
  goalMinutes?: number;
  conceptFilter?: string | null;
  queueMode?: 'default' | 'due';
}): Promise<PracticeSessionRow | null> {
  if (!sql) return null;
  await ensurePracticeTables();
  const goalItems = Math.min(
    40,
    Math.max(3, opts.goalItems ?? PRACTICE_DEFAULT_GOAL_ITEMS),
  );
  const goalMinutes = Math.min(
    90,
    Math.max(5, opts.goalMinutes ?? PRACTICE_DEFAULT_GOAL_MINUTES),
  );
  const queueMode = opts.queueMode === 'due' ? 'due' : 'default';
  try {
    const rows = (await sql`
      INSERT INTO practice_sessions (
        user_id, goal_items, goal_minutes, concept_filter, current_graded, version, queue_mode
      ) VALUES (
        ${opts.learnerId},
        ${goalItems},
        ${goalMinutes},
        ${opts.conceptFilter ?? null},
        FALSE,
        0,
        ${queueMode}
      )
      RETURNING *
    `) as Array<Record<string, unknown>>;
    return rows[0] ? rowToSession(rows[0]) : null;
  } catch (err) {
    console.warn('[practice-session] create failed', err);
    return null;
  }
}

export async function getPracticeSessionForLearner(
  learnerId: string,
  sessionId: string,
): Promise<PracticeSessionRow | null> {
  if (!sql) return null;
  await ensurePracticeTables();
  try {
    const rows = (await sql`
      SELECT * FROM practice_sessions
      WHERE id = ${sessionId}::uuid AND user_id = ${learnerId}
      LIMIT 1
    `) as Array<Record<string, unknown>>;
    return rows[0] ? rowToSession(rows[0]) : null;
  } catch (err) {
    console.warn('[practice-session] get failed', err);
    return null;
  }
}

export type PracticeSessionPatch = Partial<{
  focus_concept_id: string | null;
  attempted: number;
  correct_count: number;
  hints_used: number;
  generated_count: number;
  seen_ids: string[];
  recent_correct: boolean[];
  current_item: PracticeItemSealed | null;
  hint_step: number;
  current_graded: boolean;
  status: 'active' | 'ended';
}>;

/**
 * Optimistic update: fails (returns null) if `expectedVersion` does not match.
 */
export async function updatePracticeSession(
  learnerId: string,
  sessionId: string,
  patch: PracticeSessionPatch,
  expectedVersion: number,
): Promise<PracticeSessionRow | null> {
  if (!sql) return null;
  await ensurePracticeTables();
  const current = await getPracticeSessionForLearner(learnerId, sessionId);
  if (!current) return null;
  if (current.version !== expectedVersion) return null;

  const next: PracticeSessionRow = {
    ...current,
    focus_concept_id:
      patch.focus_concept_id !== undefined ? patch.focus_concept_id : current.focus_concept_id,
    attempted: patch.attempted ?? current.attempted,
    correct_count: patch.correct_count ?? current.correct_count,
    hints_used: patch.hints_used ?? current.hints_used,
    generated_count: patch.generated_count ?? current.generated_count,
    seen_ids: patch.seen_ids ?? current.seen_ids,
    recent_correct: patch.recent_correct ?? current.recent_correct,
    current_item: patch.current_item !== undefined ? patch.current_item : current.current_item,
    hint_step: patch.hint_step ?? current.hint_step,
    current_graded:
      patch.current_graded !== undefined ? patch.current_graded : current.current_graded,
    status: patch.status ?? current.status,
    version: current.version + 1,
  };

  try {
    const rows = (await sql`
      UPDATE practice_sessions SET
        focus_concept_id = ${next.focus_concept_id},
        attempted = ${next.attempted},
        correct_count = ${next.correct_count},
        hints_used = ${next.hints_used},
        generated_count = ${next.generated_count},
        seen_ids = ${JSON.stringify(next.seen_ids)}::jsonb,
        recent_correct = ${JSON.stringify(next.recent_correct)}::jsonb,
        current_item = ${next.current_item ? JSON.stringify(next.current_item) : null}::jsonb,
        hint_step = ${next.hint_step},
        current_graded = ${next.current_graded},
        version = ${next.version},
        status = ${next.status},
        ended_at = CASE WHEN ${next.status} = 'ended' THEN NOW() ELSE ended_at END
      WHERE id = ${sessionId}::uuid
        AND user_id = ${learnerId}
        AND version = ${expectedVersion}
      RETURNING *
    `) as Array<Record<string, unknown>>;
    return rows[0] ? rowToSession(rows[0]) : null;
  } catch (err) {
    console.warn('[practice-session] update failed', err);
    return null;
  }
}
