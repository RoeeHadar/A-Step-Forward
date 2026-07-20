/**
 * Feedback-first assessment grading orchestration.
 *
 * Submit → pending attempt (no headline score if opens remain) → chunked
 * grade-next (one open item) with site-wide concurrency cap → finalize score
 * + gate pass only when all open feedback exists.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';
import {
  aggregateProcessScores,
  gradeOpenItemProcess,
  MAX_CONCURRENT_GRADES,
  perTopicFromItemScores,
  type ProcessFeedback,
} from '@/lib/process-grader';
import { GATE_PASS_THRESHOLD } from '@/lib/test-attempts';
import { evaluateGatePass, hasFrontier } from '@/lib/plan-pacing';
import { getLearnerProfile } from '@/lib/neon-db';
import {
  applySettledOpenScores,
  isOpenAssessmentKind,
  opensStillPending,
  selectNextOpenItemId,
  GRADE_ITEM_MAX_RETRIES,
} from '@/lib/assessment-grading-logic';

neonConfig.fetchConnectionCache = true;
const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export type GradingStatus = 'pending' | 'grading' | 'complete' | 'failed';

export interface AssessmentQuestionForGrade {
  id: string;
  topic: string;
  subject: string;
  stem: string;
  kind: string;
  options?: { key: string; text: string }[];
  correct?: string;
  correct_answer?: string | null;
  acceptable_answers?: string[];
  rubric?: string | null;
  model_answer?: string | null;
  total_points?: number;
  skill_atoms?: string[];
}

export interface CreatePendingAttemptInput {
  learnerId: string;
  kind: string;
  planId?: string | null;
  weekNum?: number | null;
  quizId?: string | null;
  locale?: 'he' | 'en';
  questions: AssessmentQuestionForGrade[];
  answers: Array<{ item_id: string; chosen: string }>;
  /** Precomputed 0/1 scores for closed items only */
  closedScores: Record<string, number>;
  passThreshold?: number;
}

export interface AttemptGradingView {
  attempt_id: string;
  grading_status: GradingStatus;
  /** null until complete — never invent a score while pending */
  score: number | null;
  passed: boolean | null;
  pass_threshold: number;
  per_topic: Record<string, number>;
  weak_concepts: string[];
  plan_adapted: boolean;
  item_feedback: Record<string, ProcessFeedback>;
  item_scores: Record<string, number>;
  open_pending: number;
  open_total: number;
  graded_open: number;
  busy?: boolean;
  message?: string;
}

let schemaReady = false;

async function ensureGradingSchema(): Promise<boolean> {
  if (!sql) return false;
  if (schemaReady) return true;
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
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS grading_status TEXT NOT NULL DEFAULT 'complete'`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS item_feedback JSONB NOT NULL DEFAULT '{}'::jsonb`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS item_scores JSONB NOT NULL DEFAULT '{}'::jsonb`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS open_item_ids TEXT[] NOT NULL DEFAULT '{}'`;
    await sql`ALTER TABLE test_attempts ADD COLUMN IF NOT EXISTS grading_locked_until TIMESTAMPTZ`;
    await sql`CREATE INDEX IF NOT EXISTS ix_test_attempts_learner ON test_attempts (learner_id, created_at DESC)`;
    await sql`
      CREATE TABLE IF NOT EXISTS grading_slots (
        id TEXT PRIMARY KEY DEFAULT 'global',
        active INT NOT NULL DEFAULT 0,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`
      INSERT INTO grading_slots (id, active) VALUES ('global', 0)
      ON CONFLICT (id) DO NOTHING
    `;
    schemaReady = true;
    return true;
  } catch (err) {
    logger.error('[assessment-grading] ensureGradingSchema failed', { err: String(err) });
    return false;
  }
}

function isOpenKind(kind: string): boolean {
  return isOpenAssessmentKind(kind);
}

async function tryAcquireSlot(): Promise<boolean> {
  if (!sql) return false;
  try {
    const rows = (await sql`
      UPDATE grading_slots
      SET active = active + 1, updated_at = NOW()
      WHERE id = 'global' AND active < ${MAX_CONCURRENT_GRADES}
      RETURNING active
    `) as Array<{ active: number }>;
    return rows.length > 0;
  } catch {
    return true; // degrade: allow grade if slot table broken
  }
}

async function releaseSlot(): Promise<void> {
  if (!sql) return;
  try {
    await sql`
      UPDATE grading_slots
      SET active = GREATEST(active - 1, 0), updated_at = NOW()
      WHERE id = 'global'
    `;
  } catch {
    // ignore
  }
}

/**
 * Create a pending (or immediately complete if no open items) attempt.
 */
export async function createPendingAttempt(
  input: CreatePendingAttemptInput,
): Promise<AttemptGradingView | null> {
  if (!sql) return null;
  const ok = await ensureGradingSchema();
  if (!ok) return null;

  const openIds = input.questions.filter((q) => isOpenKind(q.kind)).map((q) => q.id);
  const itemScores: Record<string, number> = { ...input.closedScores };
  const itemFeedback: Record<string, ProcessFeedback> = {};

  for (const q of input.questions) {
    if (!isOpenKind(q.kind)) continue;
    const pts = q.total_points ?? 20;
    itemFeedback[q.id] = {
      item_id: q.id,
      status: 'pending',
      retries: 0,
      strengths: '',
      steps_present: '',
      steps_skipped: '',
      logic: '',
      material_anchoring: '',
      points_earned: 0,
      points_available: pts,
      process_score: 0,
      next_fix: '',
    };
  }

  const passThreshold = input.passThreshold ?? GATE_PASS_THRESHOLD;
  const allIds = input.questions.map((q) => q.id);
  const hasOpen = openIds.length > 0;

  // Closed-only: finalize immediately.
  if (!hasOpen) {
    const score = aggregateProcessScores(allIds, itemScores);
    const perTopic = perTopicFromItemScores(
      input.questions.map((q) => ({ id: q.id, topic: q.topic })),
      itemScores,
    );
    const gate = await resolveGate(input.learnerId, score, perTopic, passThreshold);
    const rows = (await sql`
      INSERT INTO test_attempts (
        learner_id, kind, plan_id, week_num, quiz_id, locale,
        score, passed, pass_threshold, per_topic, weak_concepts,
        questions, answers, feedback, grading_status, item_feedback, item_scores, open_item_ids
      )
      VALUES (
        ${input.learnerId},
        ${input.kind},
        ${input.planId ?? null},
        ${input.weekNum ?? null},
        ${input.quizId ?? null},
        ${input.locale ?? 'he'},
        ${score},
        ${gate.passed},
        ${passThreshold},
        ${JSON.stringify(perTopic)}::jsonb,
        ${gate.weak},
        ${JSON.stringify(input.questions.map(snapQ))}::jsonb,
        ${JSON.stringify(input.answers)}::jsonb,
        ${JSON.stringify({ closed_only: true })}::jsonb,
        'complete',
        ${JSON.stringify(itemFeedback)}::jsonb,
        ${JSON.stringify(itemScores)}::jsonb,
        ${[]}
      )
      RETURNING id::text
    `) as Array<{ id: string }>;
    const id = rows[0]?.id;
    if (!id) return null;
    return {
      attempt_id: id,
      grading_status: 'complete',
      score,
      passed: gate.passed,
      pass_threshold: passThreshold,
      per_topic: perTopic,
      weak_concepts: gate.weak,
      plan_adapted: false,
      item_feedback: itemFeedback,
      item_scores: itemScores,
      open_pending: 0,
      open_total: 0,
      graded_open: 0,
    };
  }

  // Open present: NO headline score yet.
  const rows = (await sql`
    INSERT INTO test_attempts (
      learner_id, kind, plan_id, week_num, quiz_id, locale,
      score, passed, pass_threshold, per_topic, weak_concepts,
      questions, answers, feedback, grading_status, item_feedback, item_scores, open_item_ids
    )
    VALUES (
      ${input.learnerId},
      ${input.kind},
      ${input.planId ?? null},
      ${input.weekNum ?? null},
      ${input.quizId ?? null},
      ${input.locale ?? 'he'},
      0,
      FALSE,
      ${passThreshold},
      ${JSON.stringify({})}::jsonb,
      ${[]},
      ${JSON.stringify(input.questions.map(snapQ))}::jsonb,
      ${JSON.stringify(input.answers)}::jsonb,
      ${JSON.stringify({ note: 'awaiting_process_review' })}::jsonb,
      'pending',
      ${JSON.stringify(itemFeedback)}::jsonb,
      ${JSON.stringify(itemScores)}::jsonb,
      ${openIds}
    )
    RETURNING id::text
  `) as Array<{ id: string }>;

  const id = rows[0]?.id;
  if (!id) return null;
  return viewFromState({
    attempt_id: id,
    grading_status: 'pending',
    score: null,
    passed: null,
    pass_threshold: passThreshold,
    per_topic: {},
    weak_concepts: [],
    plan_adapted: false,
    item_feedback: itemFeedback,
    item_scores: itemScores,
    open_item_ids: openIds,
  });
}

function snapQ(q: AssessmentQuestionForGrade) {
  return {
    id: q.id,
    topic: q.topic,
    subject: q.subject,
    stem: q.stem,
    options: q.options ?? [],
    correct: q.correct ?? q.correct_answer ?? '',
    kind: q.kind,
    rubric: q.rubric,
    model_answer: q.model_answer,
    total_points: q.total_points,
  };
}

function viewFromState(s: {
  attempt_id: string;
  grading_status: GradingStatus;
  score: number | null;
  passed: boolean | null;
  pass_threshold: number;
  per_topic: Record<string, number>;
  weak_concepts: string[];
  plan_adapted: boolean;
  item_feedback: Record<string, ProcessFeedback>;
  item_scores: Record<string, number>;
  open_item_ids: string[];
  busy?: boolean;
  message?: string;
}): AttemptGradingView {
  const openTotal = s.open_item_ids.length;
  const gradedOpen = s.open_item_ids.filter(
    (id) => s.item_feedback[id]?.status === 'graded',
  ).length;
  const openPending = s.open_item_ids.filter(
    (id) =>
      s.item_feedback[id]?.status === 'pending' ||
      s.item_feedback[id]?.status === 'failed',
  ).length;
  return {
    attempt_id: s.attempt_id,
    grading_status: s.grading_status,
    score: s.score,
    passed: s.passed,
    pass_threshold: s.pass_threshold,
    per_topic: s.per_topic,
    weak_concepts: s.weak_concepts,
    plan_adapted: s.plan_adapted,
    item_feedback: s.item_feedback,
    item_scores: s.item_scores,
    open_pending: openPending,
    open_total: openTotal,
    graded_open: gradedOpen,
    busy: s.busy,
    message: s.message,
  };
}

async function resolveGate(
  learnerId: string,
  score: number,
  perTopic: Record<string, number>,
  passThreshold: number,
): Promise<{ passed: boolean; weak: string[] }> {
  const profile = await getLearnerProfile(learnerId).catch(() => null);
  const goalKeyRaw =
    (profile?.personality_profile as { goal_key?: unknown } | null | undefined)?.goal_key;
  const goalKey =
    typeof goalKeyRaw === 'string' && hasFrontier(goalKeyRaw)
      ? goalKeyRaw
      : typeof profile?.goal === 'string' && hasFrontier(profile.goal)
        ? profile.goal
        : null;
  const gate = evaluateGatePass({
    aggregateScore: score,
    perTopic,
    goalKey,
    passThreshold,
  });
  const weak = Array.from(
    new Set([
      ...Object.entries(perTopic)
        .filter(([, s]) => s < 0.4)
        .map(([t]) => t),
      ...gate.failed_critical,
    ]),
  );
  return { passed: gate.passed, weak };
}

type AttemptRow = {
  id: string;
  learner_id: string;
  kind: string;
  plan_id: string | null;
  week_num: number | null;
  quiz_id: string | null;
  locale: string;
  score: number;
  passed: boolean;
  pass_threshold: number;
  per_topic: Record<string, number>;
  weak_concepts: string[];
  questions: AssessmentQuestionForGrade[];
  answers: Array<{ item_id: string; chosen: string }>;
  grading_status: string;
  item_feedback: Record<string, ProcessFeedback>;
  item_scores: Record<string, number>;
  open_item_ids: string[];
};

async function loadAttempt(
  learnerId: string,
  attemptId: string,
): Promise<AttemptRow | null> {
  if (!sql) return null;
  await ensureGradingSchema();
  try {
    const rows = (await sql`
      SELECT id::text, learner_id, kind, plan_id, week_num, quiz_id, locale,
             score::float AS score, passed, pass_threshold::float AS pass_threshold,
             per_topic, weak_concepts, questions, answers,
             grading_status, item_feedback, item_scores, open_item_ids
      FROM test_attempts
      WHERE id = ${attemptId}::uuid AND learner_id = ${learnerId}
      LIMIT 1
    `) as AttemptRow[];
    return rows[0] ?? null;
  } catch {
    return null;
  }
}

export async function getAttemptGradingView(
  learnerId: string,
  attemptId: string,
): Promise<AttemptGradingView | null> {
  const row = await loadAttempt(learnerId, attemptId);
  if (!row) return null;
  const status = (row.grading_status as GradingStatus) || 'complete';
  const openIds = Array.isArray(row.open_item_ids) ? row.open_item_ids : [];
  return viewFromState({
    attempt_id: row.id,
    grading_status: status,
    score: status === 'complete' ? Number(row.score) : null,
    passed: status === 'complete' ? Boolean(row.passed) : null,
    pass_threshold: Number(row.pass_threshold ?? GATE_PASS_THRESHOLD),
    per_topic: row.per_topic ?? {},
    weak_concepts: row.weak_concepts ?? [],
    plan_adapted: false,
    item_feedback: row.item_feedback ?? {},
    item_scores: row.item_scores ?? {},
    open_item_ids: openIds,
  });
}

/**
 * Grade the next pending open item for an attempt. Idempotent when complete.
 */
export async function gradeNextOpenItem(
  learnerId: string,
  attemptId: string,
  opts?: {
    /** Called when attempt becomes complete and passed — e.g. mark plan week done */
    onPassed?: (ctx: {
      kind: string;
      planId: string | null;
      weekNum: number | null;
      quizId: string | null;
      score: number;
    }) => Promise<boolean>;
  },
): Promise<AttemptGradingView | null> {
  if (!sql) return null;
  const row = await loadAttempt(learnerId, attemptId);
  if (!row) return null;

  const openIds = Array.isArray(row.open_item_ids) ? row.open_item_ids : [];
  const feedback = { ...(row.item_feedback ?? {}) };
  const scores = { ...(row.item_scores ?? {}) };
  const locale = row.locale === 'en' ? 'en' : 'he';

  if (row.grading_status === 'complete') {
    return viewFromState({
      attempt_id: row.id,
      grading_status: 'complete',
      score: Number(row.score),
      passed: Boolean(row.passed),
      pass_threshold: Number(row.pass_threshold),
      per_topic: row.per_topic ?? {},
      weak_concepts: row.weak_concepts ?? [],
      plan_adapted: false,
      item_feedback: feedback,
      item_scores: scores,
      open_item_ids: openIds,
    });
  }

  const nextId = selectNextOpenItemId(openIds, feedback, GRADE_ITEM_MAX_RETRIES);

  if (!nextId) {
    // All opens graded or permanently failed → finalize (failed items score 0).
    return finalizeAttempt(row, feedback, scores, opts);
  }

  const gotSlot = await tryAcquireSlot();
  if (!gotSlot) {
    return viewFromState({
      attempt_id: row.id,
      grading_status: 'pending',
      score: null,
      passed: null,
      pass_threshold: Number(row.pass_threshold),
      per_topic: {},
      weak_concepts: [],
      plan_adapted: false,
      item_feedback: feedback,
      item_scores: scores,
      open_item_ids: openIds,
      busy: true,
      message: locale === 'he' ? 'הבודק עסוק — מנסים שוב…' : 'Grader busy — retrying…',
    });
  }

  try {
    await sql`
      UPDATE test_attempts
      SET grading_status = 'grading', grading_locked_until = NOW() + INTERVAL '45 seconds'
      WHERE id = ${attemptId}::uuid AND learner_id = ${learnerId}
    `;

    const q = (Array.isArray(row.questions) ? row.questions : []).find((x) => x.id === nextId);
    const answer = (Array.isArray(row.answers) ? row.answers : []).find(
      (a) => a.item_id === nextId,
    );
    const prior = feedback[nextId];
    const graded = await gradeOpenItemProcess({
      item_id: nextId,
      stem: q?.stem ?? '',
      response: answer?.chosen ?? '',
      rubric: q?.rubric,
      model_answer: q?.model_answer,
      concept_id: q?.topic,
      points_available: q?.total_points ?? prior?.points_available ?? 20,
      locale,
      prior_retries: prior?.retries ?? 0,
    });

    feedback[nextId] = graded;
    if (graded.status === 'graded') {
      scores[nextId] = graded.process_score;
    }

    await sql`
      UPDATE test_attempts
      SET item_feedback = ${JSON.stringify(feedback)}::jsonb,
          item_scores = ${JSON.stringify(scores)}::jsonb,
          grading_status = 'pending',
          grading_locked_until = NULL
      WHERE id = ${attemptId}::uuid AND learner_id = ${learnerId}
    `;

    const stillPending = opensStillPending(openIds, feedback, GRADE_ITEM_MAX_RETRIES);

    if (!stillPending) {
      const refreshed = await loadAttempt(learnerId, attemptId);
      if (refreshed) {
        return finalizeAttempt(
          { ...refreshed, item_feedback: feedback, item_scores: scores },
          feedback,
          scores,
          opts,
        );
      }
    }

    return viewFromState({
      attempt_id: row.id,
      grading_status: 'pending',
      score: null,
      passed: null,
      pass_threshold: Number(row.pass_threshold),
      per_topic: {},
      weak_concepts: [],
      plan_adapted: false,
      item_feedback: feedback,
      item_scores: scores,
      open_item_ids: openIds,
    });
  } finally {
    await releaseSlot();
  }
}

async function finalizeAttempt(
  row: AttemptRow,
  feedback: Record<string, ProcessFeedback>,
  scores: Record<string, number>,
  opts?: {
    onPassed?: (ctx: {
      kind: string;
      planId: string | null;
      weekNum: number | null;
      quizId: string | null;
      score: number;
    }) => Promise<boolean>;
  },
): Promise<AttemptGradingView> {
  if (!sql) {
    return viewFromState({
      attempt_id: row.id,
      grading_status: 'failed',
      score: null,
      passed: null,
      pass_threshold: Number(row.pass_threshold),
      per_topic: {},
      weak_concepts: [],
      plan_adapted: false,
      item_feedback: feedback,
      item_scores: scores,
      open_item_ids: row.open_item_ids ?? [],
    });
  }

  // Permanent failures stay at 0.
  applySettledOpenScores(row.open_item_ids ?? [], feedback, scores);

  const questions = Array.isArray(row.questions) ? row.questions : [];
  const allIds = questions.map((q) => q.id);
  const score = aggregateProcessScores(allIds, scores);
  const perTopic = perTopicFromItemScores(
    questions.map((q) => ({ id: q.id, topic: q.topic })),
    scores,
  );
  const passThreshold = Number(row.pass_threshold ?? GATE_PASS_THRESHOLD);
  const gate = await resolveGate(row.learner_id, score, perTopic, passThreshold);

  await sql`
    UPDATE test_attempts
    SET score = ${score},
        passed = ${gate.passed},
        per_topic = ${JSON.stringify(perTopic)}::jsonb,
        weak_concepts = ${gate.weak},
        item_feedback = ${JSON.stringify(feedback)}::jsonb,
        item_scores = ${JSON.stringify(scores)}::jsonb,
        grading_status = 'complete',
        feedback = ${JSON.stringify({ process_review: true, finalized_at: new Date().toISOString() })}::jsonb,
        grading_locked_until = NULL
    WHERE id = ${row.id}::uuid
  `;

  let planAdapted = false;
  if (gate.passed && opts?.onPassed) {
    planAdapted = await opts.onPassed({
      kind: row.kind,
      planId: row.plan_id,
      weekNum: row.week_num,
      quizId: row.quiz_id,
      score,
    });
  }

  return viewFromState({
    attempt_id: row.id,
    grading_status: 'complete',
    score,
    passed: gate.passed,
    pass_threshold: passThreshold,
    per_topic: perTopic,
    weak_concepts: gate.weak,
    plan_adapted: planAdapted,
    item_feedback: feedback,
    item_scores: scores,
    open_item_ids: row.open_item_ids ?? [],
  });
}
