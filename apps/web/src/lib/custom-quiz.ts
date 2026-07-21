/**
 * Server-held custom quizzes — answer keys never leave Neon until grading complete.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { createPendingAttempt } from '@/lib/assessment-grading';
import type { CustomQuizEnvelope } from '@/lib/quiz-builder';
import {
  buildRevealMap,
  stripCustomQuizForClient,
  type CustomQuizEnvelopePublic,
  type CustomQuizReveal,
  type StoredCustomQuestion,
} from '@/lib/custom-quiz-strip';

export {
  buildRevealMap,
  stripCustomQuizForClient,
  gradeClosedFromStoredOnly,
  type CustomQuizEnvelopePublic,
  type CustomQuizQuestionPublic,
  type CustomQuizReveal,
} from '@/lib/custom-quiz-strip';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

async function ensureCustomQuizTable(): Promise<void> {
  if (!sql) return;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS custom_quizzes (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id         TEXT NOT NULL,
        mode            TEXT,
        kind_mix        TEXT,
        time_limit_s    INT NOT NULL,
        concepts        JSONB NOT NULL DEFAULT '[]'::jsonb,
        picked_reason   TEXT,
        model           TEXT,
        questions       JSONB NOT NULL,
        submitted_at    TIMESTAMPTZ,
        score           DOUBLE PRECISION,
        created_at      TIMESTAMPTZ DEFAULT NOW()
      )
    `;
    await sql`
      CREATE INDEX IF NOT EXISTS ix_custom_quizzes_user
      ON custom_quizzes (user_id, created_at DESC)
    `;
  } catch {
    // concurrent DDL
  }
}

export async function persistCustomQuiz(
  learnerId: string,
  envelope: CustomQuizEnvelope,
): Promise<CustomQuizEnvelopePublic | null> {
  if (!sql) return null;
  await ensureCustomQuizTable();

  const withIds: StoredCustomQuestion[] = envelope.questions.map((q) => ({
    ...q,
    id:
      globalThis.crypto?.randomUUID() ||
      `cq_${Date.now()}_${Math.random().toString(36).slice(2)}`,
  }));

  try {
    const rows = (await sql`
      INSERT INTO custom_quizzes (
        user_id, mode, kind_mix, time_limit_s, concepts, picked_reason, model, questions
      ) VALUES (
        ${learnerId},
        ${envelope.mode},
        ${envelope.kind_mix},
        ${envelope.time_limit_s},
        ${JSON.stringify(envelope.concepts)}::jsonb,
        ${envelope.picked_reason},
        ${envelope.model ?? null},
        ${JSON.stringify(withIds)}::jsonb
      )
      RETURNING id::text
    `) as Array<{ id: string }>;
    const quizId = rows[0]?.id;
    if (!quizId) return null;
    return stripCustomQuizForClient({
      ...envelope,
      quiz_id: quizId,
      questions: withIds,
    });
  } catch (err) {
    console.warn('[custom-quiz] persist failed', err);
    return null;
  }
}

export async function getCustomQuizForLearner(
  learnerId: string,
  quizId: string,
): Promise<{ envelope: CustomQuizEnvelope; questions: StoredCustomQuestion[] } | null> {
  if (!sql) return null;
  await ensureCustomQuizTable();
  try {
    const rows = (await sql`
      SELECT id::text, mode, kind_mix, time_limit_s, concepts, picked_reason, model, questions
      FROM custom_quizzes
      WHERE id = ${quizId}::uuid AND user_id = ${learnerId}
      LIMIT 1
    `) as Array<{
      id: string;
      mode: string;
      kind_mix: string;
      time_limit_s: number;
      concepts: CustomQuizEnvelope['concepts'];
      picked_reason: CustomQuizEnvelope['picked_reason'];
      model: string | null;
      questions: StoredCustomQuestion[];
    }>;
    const row = rows[0];
    if (!row) return null;
    const questions = Array.isArray(row.questions) ? row.questions : [];
    return {
      envelope: {
        quiz_id: row.id,
        mode: row.mode as CustomQuizEnvelope['mode'],
        kind_mix: row.kind_mix as CustomQuizEnvelope['kind_mix'],
        time_limit_s: row.time_limit_s,
        concepts: row.concepts,
        picked_reason: row.picked_reason,
        model: row.model ?? undefined,
        questions,
      },
      questions,
    };
  } catch {
    return null;
  }
}

function isOpen(kind: string): boolean {
  return kind === 'open' || kind === 'derivation' || kind === 'extended';
}

function gradeClosedStored(q: StoredCustomQuestion, chosenRaw: string): number {
  const chosen = chosenRaw.trim();
  if (!chosen) return 0;
  if (q.kind === 'mcq') {
    if (typeof q.correct_index !== 'number') return 0;
    const letter = String.fromCharCode(65 + q.correct_index);
    return chosen.toUpperCase() === letter ? 1 : 0;
  }
  return 0;
}

export async function submitCustomQuizForUser(
  learnerId: string,
  quizId: string,
  answers: Array<{ item_id: string; chosen: string }>,
  locale: 'he' | 'en',
): Promise<Record<string, unknown> | null> {
  const loaded = await getCustomQuizForLearner(learnerId, quizId);
  if (!loaded) return null;

  const answerByItem = new Map(answers.map((a) => [a.item_id, a.chosen]));
  const closedScores: Record<string, number> = {};
  const normalized = loaded.questions.map((q) => {
    const stem = locale === 'he' ? q.stem_he : q.stem_en;
    const rubric = locale === 'he' ? q.rubric_he : q.rubric_en;
    const modelAnswer = locale === 'he' ? q.sample_solution_he : q.sample_solution_en;
    const partsPts =
      q.parts?.reduce((s, p) => s + (typeof p.points === 'number' ? p.points : 0), 0) ?? 0;
    const total =
      q.total_points ?? (partsPts > 0 ? partsPts : isOpen(q.kind) ? 20 : 5);
    if (!isOpen(q.kind)) {
      closedScores[q.id] = gradeClosedStored(q, answerByItem.get(q.id) ?? '');
    }
    const options =
      (locale === 'he' ? q.options_he : q.options_en)?.map((text, oi) => ({
        key: String.fromCharCode(65 + oi),
        text,
      })) ?? undefined;
    return {
      id: q.id,
      topic: q.concept_id,
      subject: '',
      stem,
      kind: isOpen(q.kind) ? 'open' : q.kind,
      options,
      correct:
        q.kind === 'mcq' && typeof q.correct_index === 'number'
          ? String.fromCharCode(65 + q.correct_index)
          : undefined,
      rubric,
      model_answer: modelAnswer,
      total_points: total,
      skill_atoms: q.skill_atoms,
      parts: q.parts?.map((p) => ({
        label: p.label,
        body: locale === 'he' ? p.body_he : p.body_en,
        points: p.points,
      })),
    };
  });

  const view = await createPendingAttempt({
    learnerId,
    kind: 'custom_quiz',
    quizId,
    locale,
    questions: normalized,
    answers: normalized.map((q) => ({
      item_id: q.id,
      chosen: answerByItem.get(q.id) ?? '',
    })),
    closedScores,
  });

  if (!view) return null;

  if (sql && view.grading_status === 'complete' && view.score != null) {
    try {
      await sql`
        UPDATE custom_quizzes
        SET submitted_at = NOW(), score = ${view.score}
        WHERE id = ${quizId}::uuid AND user_id = ${learnerId}
      `;
    } catch {
      // best-effort
    }
  }

  const reveal: CustomQuizReveal | undefined =
    view.grading_status === 'complete' ? buildRevealMap(loaded.questions) : undefined;

  return {
    quiz_id: quizId,
    score: view.score,
    per_topic: view.per_topic,
    weak_concepts: view.weak_concepts,
    plan_adapted: false,
    passed: view.passed,
    pass_threshold: view.pass_threshold,
    attempt_id: view.attempt_id,
    grading_status: view.grading_status,
    item_feedback: view.item_feedback,
    item_scores: view.item_scores,
    open_pending: view.open_pending,
    open_total: view.open_total,
    graded_open: view.graded_open,
    busy: view.busy,
    message: view.message,
    reveal,
  };
}
