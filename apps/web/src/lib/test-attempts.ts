/**
 * Durable test/quiz attempt archive + week-gate signal (ADR-0009).
 *
 * One row per graded quiz a learner submits. Powers the Tests archive UI (past
 * tests + the learner's answers vs correct) and the week-gate signal
 * (score vs pass threshold, weak concepts) that drives remediation under the
 * soft-override policy.
 *
 * GRACEFUL DEGRADATION: every function is wrapped so that a missing `test_attempts`
 * table (migration 0019 not yet run) or any DB error is a no-op — writes silently
 * skip, reads return []/null. The table is also created lazily on first write
 * (house style, mirrors weekly_quizzes_ai / mock_exams), so the feature works even
 * before the migration runs; running the migration just gives the indexed version.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

/** Week-gate pass threshold (ADR-0009 §week gates). */
export const GATE_PASS_THRESHOLD = 0.75;

export interface TestAttemptQuestionSnapshot {
  id: string;
  topic: string;
  subject: string;
  stem: string;
  options: { key: string; text: string }[];
  correct: string;
}

export interface TestAttemptAnswerSnapshot {
  item_id: string;
  chosen: string;
}

export interface RecordTestAttemptInput {
  learnerId: string;
  kind?: string;
  planId?: string | null;
  weekNum?: number | null;
  quizId?: string | null;
  locale?: string;
  score: number;
  passThreshold?: number;
  perTopic: Record<string, number>;
  weakConcepts: string[];
  questions: TestAttemptQuestionSnapshot[];
  answers: TestAttemptAnswerSnapshot[];
}

export interface TestAttemptListItem {
  id: string;
  kind: string;
  plan_id: string | null;
  week_num: number | null;
  score: number;
  passed: boolean;
  pass_threshold: number;
  weak_concepts: string[];
  question_count: number;
  created_at: string;
}

export interface TestAttemptDetail extends TestAttemptListItem {
  locale: string;
  per_topic: Record<string, number>;
  questions: TestAttemptQuestionSnapshot[];
  answers: TestAttemptAnswerSnapshot[];
}

let ensured = false;

/** Ensure `test_attempts` exists (lazy DDL). Safe to call from Progress reads. */
export async function ensureTestAttemptsTable(): Promise<boolean> {
  return ensureTable();
}

async function ensureTable(): Promise<boolean> {
  if (!sql) return false;
  if (ensured) return true;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS test_attempts (
        id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        learner_id     TEXT NOT NULL,
        kind           TEXT NOT NULL DEFAULT 'weekly_gate',
        plan_id        TEXT,
        week_num       INT,
        quiz_id        TEXT,
        locale         TEXT NOT NULL DEFAULT 'he',
        score          DOUBLE PRECISION NOT NULL DEFAULT 0,
        passed         BOOLEAN NOT NULL DEFAULT FALSE,
        pass_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.75,
        per_topic      JSONB NOT NULL DEFAULT '{}'::jsonb,
        weak_concepts  TEXT[] NOT NULL DEFAULT '{}',
        questions      JSONB NOT NULL DEFAULT '[]'::jsonb,
        answers        JSONB NOT NULL DEFAULT '[]'::jsonb,
        feedback       JSONB,
        created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_test_attempts_learner ON test_attempts (learner_id, created_at DESC)`;
    ensured = true;
    return true;
  } catch (err) {
    // Real DDL failure (e.g. migration never ran + creation blocked). Previously
    // this returned `true`, so the caller's INSERT then threw "relation does not
    // exist" and was silently swallowed — the Tests archive stayed permanently
    // empty with zero signal. Surface it and skip the write so it's diagnosable.
    logger.error('[test-attempts] ensureTable failed — attempt will not be archived', {
      err: String(err),
    });
    return false;
  }
}

/**
 * Persist a graded attempt. Best-effort: returns the new attempt id, or null when
 * persistence is unavailable. Never throws.
 */
export async function recordTestAttempt(input: RecordTestAttemptInput): Promise<string | null> {
  if (!sql) return null;
  const ok = await ensureTable();
  if (!ok) return null;
  const passThreshold = input.passThreshold ?? GATE_PASS_THRESHOLD;
  const passed = input.score >= passThreshold;
  try {
    const rows = (await sql`
      INSERT INTO test_attempts (
        learner_id, kind, plan_id, week_num, quiz_id, locale,
        score, passed, pass_threshold, per_topic, weak_concepts, questions, answers
      )
      VALUES (
        ${input.learnerId},
        ${input.kind ?? 'weekly_gate'},
        ${input.planId ?? null},
        ${input.weekNum ?? null},
        ${input.quizId ?? null},
        ${input.locale ?? 'he'},
        ${input.score},
        ${passed},
        ${passThreshold},
        ${JSON.stringify(input.perTopic ?? {})}::jsonb,
        ${input.weakConcepts ?? []},
        ${JSON.stringify(input.questions ?? [])}::jsonb,
        ${JSON.stringify(input.answers ?? [])}::jsonb
      )
      RETURNING id::text
    `) as Array<{ id: string }>;
    return rows[0]?.id ?? null;
  } catch (err) {
    logger.error('[test-attempts] recordTestAttempt insert failed', {
      err: String(err),
      kind: input.kind ?? 'weekly_gate',
    });
    return null;
  }
}

export async function listTestAttempts(
  learnerId: string,
  limit = 30,
): Promise<TestAttemptListItem[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT id::text, kind, plan_id, week_num, score::float AS score, passed,
             pass_threshold::float AS pass_threshold, weak_concepts,
             jsonb_array_length(questions) AS question_count, created_at
      FROM test_attempts
      WHERE learner_id = ${learnerId}
      ORDER BY created_at DESC
      LIMIT ${limit}
    `) as Array<Record<string, unknown>>;
    return rows.map(mapListRow);
  } catch {
    return [];
  }
}

export async function getTestAttempt(
  learnerId: string,
  attemptId: string,
): Promise<TestAttemptDetail | null> {
  if (!sql) return null;
  try {
    const rows = (await sql`
      SELECT id::text, kind, plan_id, week_num, score::float AS score, passed,
             pass_threshold::float AS pass_threshold, weak_concepts, locale,
             per_topic, questions, answers,
             jsonb_array_length(questions) AS question_count, created_at
      FROM test_attempts
      WHERE id = ${attemptId}::uuid AND learner_id = ${learnerId}
      LIMIT 1
    `) as Array<Record<string, unknown>>;
    const row = rows[0];
    if (!row) return null;
    return {
      ...mapListRow(row),
      locale: typeof row.locale === 'string' ? row.locale : 'he',
      per_topic: (row.per_topic as Record<string, number>) ?? {},
      questions: (row.questions as TestAttemptQuestionSnapshot[]) ?? [],
      answers: (row.answers as TestAttemptAnswerSnapshot[]) ?? [],
    };
  } catch {
    return null;
  }
}

/**
 * How many weekly-gate attempts a learner has made for a given plan week.
 * Drives the soft-override "retakes exhausted" backstop (ADR-0010). Returns 0 on a
 * missing table or any error (graceful degradation).
 */
export async function countGateAttempts(
  learnerId: string,
  planId: string,
  weekNum: number,
): Promise<number> {
  if (!sql) return 0;
  try {
    const rows = (await sql`
      SELECT COUNT(*)::int AS n
      FROM test_attempts
      WHERE learner_id = ${learnerId}
        AND plan_id = ${planId}
        AND week_num = ${weekNum}
        AND kind = 'weekly_gate'
    `) as Array<{ n: number }>;
    return rows[0]?.n ?? 0;
  } catch {
    return 0;
  }
}

/**
 * Weak concepts from the learner's most recent weekly-gate attempt for a plan week.
 * Used to carry remediation forward when the plan advances via soft override
 * (ADR-0010). Returns [] on a missing table or any error.
 */
export async function getLatestGateWeakConcepts(
  learnerId: string,
  planId: string,
  weekNum: number,
): Promise<string[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT weak_concepts
      FROM test_attempts
      WHERE learner_id = ${learnerId}
        AND plan_id = ${planId}
        AND week_num = ${weekNum}
        AND kind = 'weekly_gate'
      ORDER BY created_at DESC
      LIMIT 1
    `) as Array<{ weak_concepts: unknown }>;
    const w = rows[0]?.weak_concepts;
    return Array.isArray(w) ? (w as string[]) : [];
  } catch {
    return [];
  }
}

function mapListRow(row: Record<string, unknown>): TestAttemptListItem {
  return {
    id: String(row.id),
    kind: typeof row.kind === 'string' ? row.kind : 'weekly_gate',
    plan_id: row.plan_id == null ? null : String(row.plan_id),
    week_num: row.week_num == null ? null : Number(row.week_num),
    score: Number(row.score ?? 0),
    passed: Boolean(row.passed),
    pass_threshold: Number(row.pass_threshold ?? GATE_PASS_THRESHOLD),
    weak_concepts: Array.isArray(row.weak_concepts) ? (row.weak_concepts as string[]) : [],
    question_count: Number(row.question_count ?? 0),
    created_at: String(row.created_at),
  };
}
