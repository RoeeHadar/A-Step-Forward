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
import { redactQuestionsUntilGraded } from '@/lib/test-attempt-redact';

export { redactQuestionsUntilGraded } from '@/lib/test-attempt-redact';

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
  kind?: string;
  /** Present once grading is complete (redacted while pending). */
  model_answer?: string | null;
  rubric?: string | null;
}

export interface TestAttemptAnswerSnapshot {
  item_id: string;
  chosen: string;
}

/** Process / teacher feedback per item (mirrors ProcessFeedback; client-safe). */
export interface TestAttemptItemFeedback {
  item_id: string;
  status: 'pending' | 'grading' | 'graded' | 'failed' | string;
  strengths?: string;
  steps_present?: string;
  steps_skipped?: string;
  logic?: string;
  material_anchoring?: string;
  points_earned?: number;
  points_available?: number;
  process_score?: number;
  next_fix?: string;
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
  score: number | null;
  passed: boolean | null;
  pass_threshold: number;
  weak_concepts: string[];
  question_count: number;
  created_at: string;
  grading_status?: 'pending' | 'grading' | 'needs_human' | 'complete' | 'failed' | 'reopened';
}

export interface TestAttemptDetail extends TestAttemptListItem {
  locale: string;
  per_topic: Record<string, number>;
  questions: TestAttemptQuestionSnapshot[];
  answers: TestAttemptAnswerSnapshot[];
  item_feedback: Record<string, TestAttemptItemFeedback>;
  item_scores: Record<string, number>;
  /** Aggregate feedback blob (e.g. teacher override text). */
  feedback: Record<string, unknown> | null;
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
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS grading_status TEXT NOT NULL DEFAULT 'complete'`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS item_feedback JSONB NOT NULL DEFAULT '{}'::jsonb`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS item_scores JSONB NOT NULL DEFAULT '{}'::jsonb`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS open_item_ids TEXT[] NOT NULL DEFAULT '{}'`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS grading_locked_until TIMESTAMPTZ`;
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
    const attemptId = rows[0]?.id ?? null;
    if (attemptId && passed) {
      void import('./learner-xp').then(
        ({ XP_REWARDS, awardXp, gateSourceId, quizPassSourceId, maybeAwardStreakXp }) => {
          const kind = input.kind ?? 'weekly_gate';
          if (kind === 'weekly_gate' && (input.planId || input.weekNum != null)) {
            const weekKey = `${input.planId ?? 'plan'}:${input.weekNum ?? 0}`;
            void awardXp({
              learnerId: input.learnerId,
              amount: XP_REWARDS.gate_pass,
              reason: 'gate_pass',
              sourceId: gateSourceId(weekKey),
            });
          } else {
            void awardXp({
              learnerId: input.learnerId,
              amount: XP_REWARDS.quiz_pass,
              reason: 'quiz_pass',
              sourceId: quizPassSourceId(attemptId),
            });
          }
          void maybeAwardStreakXp(input.learnerId);
        },
      );
    }
    return attemptId;
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
  opts?: { forEducator?: boolean },
): Promise<TestAttemptListItem[]> {
  if (!sql) return [];
  await ensureTable();
  try {
    const rows = (await sql`
      SELECT id::text, kind, plan_id, week_num, score::float AS score, passed,
             pass_threshold::float AS pass_threshold, weak_concepts,
             COALESCE(grading_status, 'complete') AS grading_status,
             jsonb_array_length(questions) AS question_count, created_at
      FROM test_attempts
      WHERE learner_id = ${learnerId}
      ORDER BY created_at DESC
      LIMIT ${limit}
    `) as Array<Record<string, unknown>>;
    return rows.map((row) => mapListRow(row, opts));
  } catch {
    return [];
  }
}

/**
 * Load a single attempt for the Tests archive / API. Answer keys and feedback
 * are sealed until grading_status === 'complete' (released).
 * Teachers (`forEducator`) always get full questions, keys, feedback, and scores.
 */
export async function getTestAttempt(
  learnerId: string,
  attemptId: string,
  opts?: { forEducator?: boolean },
): Promise<TestAttemptDetail | null> {
  if (!sql) return null;
  await ensureTable();
  try {
    const rows = (await sql`
      SELECT id::text, kind, plan_id, week_num, score::float AS score, passed,
             pass_threshold::float AS pass_threshold, weak_concepts, locale,
             per_topic, questions, answers, feedback,
             COALESCE(item_feedback, '{}'::jsonb) AS item_feedback,
             COALESCE(item_scores, '{}'::jsonb) AS item_scores,
             COALESCE(grading_status, 'complete') AS grading_status,
             jsonb_array_length(questions) AS question_count, created_at
      FROM test_attempts
      WHERE id = ${attemptId}::uuid AND learner_id = ${learnerId}
      LIMIT 1
    `) as Array<Record<string, unknown>>;
    const row = rows[0];
    if (!row) return null;
    const forEducator = opts?.forEducator === true;
    const list = mapListRow(row, { forEducator });
    const questions = (row.questions as TestAttemptQuestionSnapshot[]) ?? [];
    const released = list.grading_status === 'complete' || forEducator;
    const itemFeedback =
      released &&
      row.item_feedback &&
      typeof row.item_feedback === 'object' &&
      !Array.isArray(row.item_feedback)
        ? (row.item_feedback as Record<string, TestAttemptItemFeedback>)
        : {};
    const itemScores =
      released &&
      row.item_scores &&
      typeof row.item_scores === 'object' &&
      !Array.isArray(row.item_scores)
        ? (row.item_scores as Record<string, number>)
        : {};
    const feedback =
      row.feedback && typeof row.feedback === 'object' && !Array.isArray(row.feedback)
        ? (row.feedback as Record<string, unknown>)
        : null;
    return {
      ...list,
      locale: typeof row.locale === 'string' ? row.locale : 'he',
      per_topic: released ? ((row.per_topic as Record<string, number>) ?? {}) : {},
      questions: forEducator
        ? questions
        : redactQuestionsUntilGraded(questions, list.grading_status),
      answers: (row.answers as TestAttemptAnswerSnapshot[]) ?? [],
      item_feedback: itemFeedback,
      item_scores: itemScores,
      feedback: released || forEducator ? feedback : null,
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

function mapListRow(
  row: Record<string, unknown>,
  opts?: { forEducator?: boolean },
): TestAttemptListItem {
  const statusRaw = typeof row.grading_status === 'string' ? row.grading_status : 'complete';
  const grading_status =
    statusRaw === 'pending' ||
    statusRaw === 'grading' ||
    statusRaw === 'failed' ||
    statusRaw === 'complete' ||
    statusRaw === 'needs_human' ||
    statusRaw === 'reopened'
      ? statusRaw
      : 'complete';
  const complete = grading_status === 'complete';
  const reveal = complete || opts?.forEducator === true;
  return {
    id: String(row.id),
    kind: typeof row.kind === 'string' ? row.kind : 'weekly_gate',
    plan_id: row.plan_id == null ? null : String(row.plan_id),
    week_num: row.week_num == null ? null : Number(row.week_num),
    score: reveal ? (row.score == null ? null : Number(row.score)) : null,
    passed: reveal ? (row.passed == null ? null : Boolean(row.passed)) : null,
    pass_threshold: Number(row.pass_threshold ?? GATE_PASS_THRESHOLD),
    weak_concepts: reveal
      ? Array.isArray(row.weak_concepts)
        ? (row.weak_concepts as string[])
        : []
      : [],
    question_count: Number(row.question_count ?? 0),
    created_at: String(row.created_at),
    grading_status,
  };
}

/**
 * Teacher override: feedback + optional score/pass adjustment (audit elsewhere).
 * Pass `reopen: true` to clear pass/fail and mark the attempt reopened for retake UX.
 * Optional `itemFeedback` / `itemScores` replace Grader draft analysis for those items.
 */
export async function teacherUpdateTestAttempt(input: {
  learnerId: string;
  attemptId: string;
  feedbackText: string;
  score?: number | null;
  passed?: boolean | null;
  reopen?: boolean;
  itemFeedback?: Record<string, TestAttemptItemFeedback> | null;
  itemScores?: Record<string, number> | null;
}): Promise<boolean> {
  if (!sql) return false;
  await ensureTable();
  try {
    const feedback = {
      teacher_feedback: input.feedbackText.trim().slice(0, 8000),
      updated_at: new Date().toISOString(),
      ...(input.reopen ? { reopened_by_teacher: true } : {}),
    };
    const hasItemPatch =
      (input.itemFeedback && Object.keys(input.itemFeedback).length > 0) ||
      (input.itemScores && Object.keys(input.itemScores).length > 0);
    const itemFeedbackJson = JSON.stringify(input.itemFeedback ?? {});
    const itemScoresJson = JSON.stringify(input.itemScores ?? {});

    if (input.reopen) {
      if (hasItemPatch) {
        await sql`
          UPDATE test_attempts
          SET feedback = COALESCE(feedback, '{}'::jsonb) || ${JSON.stringify(feedback)}::jsonb,
              passed = NULL,
              grading_status = 'reopened',
              item_feedback = COALESCE(item_feedback, '{}'::jsonb) || ${itemFeedbackJson}::jsonb,
              item_scores = COALESCE(item_scores, '{}'::jsonb) || ${itemScoresJson}::jsonb
          WHERE id = ${input.attemptId}::uuid AND learner_id = ${input.learnerId}
        `;
      } else {
        await sql`
          UPDATE test_attempts
          SET feedback = COALESCE(feedback, '{}'::jsonb) || ${JSON.stringify(feedback)}::jsonb,
              passed = NULL,
              grading_status = 'reopened'
          WHERE id = ${input.attemptId}::uuid AND learner_id = ${input.learnerId}
        `;
      }
    } else if (typeof input.score === 'number' && typeof input.passed === 'boolean') {
      if (hasItemPatch) {
        await sql`
          UPDATE test_attempts
          SET feedback = COALESCE(feedback, '{}'::jsonb) || ${JSON.stringify(feedback)}::jsonb,
              score = ${input.score},
              passed = ${input.passed},
              grading_status = 'complete',
              item_feedback = COALESCE(item_feedback, '{}'::jsonb) || ${itemFeedbackJson}::jsonb,
              item_scores = COALESCE(item_scores, '{}'::jsonb) || ${itemScoresJson}::jsonb
          WHERE id = ${input.attemptId}::uuid AND learner_id = ${input.learnerId}
        `;
      } else {
        await sql`
          UPDATE test_attempts
          SET feedback = COALESCE(feedback, '{}'::jsonb) || ${JSON.stringify(feedback)}::jsonb,
              score = ${input.score},
              passed = ${input.passed},
              grading_status = 'complete'
          WHERE id = ${input.attemptId}::uuid AND learner_id = ${input.learnerId}
        `;
      }
    } else if (hasItemPatch) {
      await sql`
        UPDATE test_attempts
        SET feedback = COALESCE(feedback, '{}'::jsonb) || ${JSON.stringify(feedback)}::jsonb,
            grading_status = 'complete',
            item_feedback = COALESCE(item_feedback, '{}'::jsonb) || ${itemFeedbackJson}::jsonb,
            item_scores = COALESCE(item_scores, '{}'::jsonb) || ${itemScoresJson}::jsonb
        WHERE id = ${input.attemptId}::uuid AND learner_id = ${input.learnerId}
      `;
    } else {
      await sql`
        UPDATE test_attempts
        SET feedback = COALESCE(feedback, '{}'::jsonb) || ${JSON.stringify(feedback)}::jsonb,
            grading_status = 'complete'
        WHERE id = ${input.attemptId}::uuid AND learner_id = ${input.learnerId}
      `;
    }
    return true;
  } catch (err) {
    logger.error('[test-attempts] teacherUpdateTestAttempt failed', { err: String(err) });
    return false;
  }
}
