/**
 * Thin lesson-complete persistence for Vercel.
 *
 * Intentionally does NOT import neon-db (pulls kg-data + heavy DDL helpers)
 * — that cold path caused hung / timed-out POSTs from the lesson page.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { resolveLessonConceptId } from '@/lib/lesson-concept-resolve';

neonConfig.fetchConnectionCache = true;

/** Baseline mastery when a learner marks a lesson as read/complete (before quiz). */
export const LESSON_READ_BASELINE = 0.7;

function requireSql() {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  if (!url) {
    throw new Error('DATABASE_URL is not set on this Vercel deployment.');
  }
  return neon(url);
}

/**
 * Record lesson completion: bump concept mastery + lessons_completed_count.
 * Also marks the active plan week `completed` when every concept in it is ≥ baseline.
 */
export async function markLessonCompleteThin(
  learnerId: string,
  conceptId: string,
): Promise<{ new_mastery: number; week_completed: boolean }> {
  const canonicalId = resolveLessonConceptId(conceptId.trim());
  const rawId = conceptId.trim();
  const s = requireSql();

  await s`
    INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
    VALUES (${learnerId}, ${canonicalId}, ${LESSON_READ_BASELINE}, 1, NOW(), NOW())
    ON CONFLICT (learner_id, concept_id) DO UPDATE SET
      score = GREATEST(concept_mastery.score, ${LESSON_READ_BASELINE}),
      last_activity = NOW(),
      updated_at = NOW()
  `;

  if (rawId !== canonicalId) {
    await s`
      INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
      VALUES (${learnerId}, ${rawId}, ${LESSON_READ_BASELINE}, 1, NOW(), NOW())
      ON CONFLICT (learner_id, concept_id) DO UPDATE SET
        score = GREATEST(concept_mastery.score, ${LESSON_READ_BASELINE}),
        last_activity = NOW(),
        updated_at = NOW()
    `;
  }

  // lessons_completed_count may be missing on older DBs — best-effort.
  try {
    await s`
      UPDATE learner_profiles
      SET lessons_completed_count = COALESCE(lessons_completed_count, 0) + 1,
          updated_at = NOW()
      WHERE learner_id = ${learnerId}
    `;
  } catch {
    // Column may not exist yet; mastery update is the critical path for plan UI.
  }

  const weekCompleted = await maybeCompleteActiveWeek(learnerId, s);
  return { new_mastery: LESSON_READ_BASELINE, week_completed: weekCompleted };
}

type Sql = ReturnType<typeof requireSql>;

async function maybeCompleteActiveWeek(learnerId: string, s: Sql): Promise<boolean> {
  try {
    const planRows = (await s`
      SELECT id::text
      FROM learning_plans
      WHERE learner_id = ${learnerId} AND status = 'active'
      LIMIT 1
    `) as Array<{ id: string }>;
    const planId = planRows[0]?.id;
    if (!planId) return false;

    const weekRows = (await s`
      SELECT id::text, concepts
      FROM plan_weeks
      WHERE plan_id = ${planId}::uuid AND status = 'active'
      ORDER BY week_number
      LIMIT 1
    `) as Array<{ id: string; concepts: string[] }>;
    const week = weekRows[0];
    if (!week?.concepts?.length) return false;

    // Prefer JS filter over ANY(${array}) — Neon HTTP binding is flaky for arrays.
    const masteryRows = (await s`
      SELECT concept_id, score::float AS score
      FROM concept_mastery
      WHERE learner_id = ${learnerId}
    `) as Array<{ concept_id: string; score: number }>;

    const byId = new Map(masteryRows.map((r) => [r.concept_id, r.score]));
    const allDone = week.concepts.every((cid) => {
      const score = Math.max(
        byId.get(cid) ?? 0,
        byId.get(resolveLessonConceptId(cid)) ?? 0,
      );
      return score >= LESSON_READ_BASELINE;
    });
    if (!allDone) return false;

    await s`
      UPDATE plan_weeks
      SET status = 'completed'
      WHERE id = ${week.id}::uuid
    `;
    return true;
  } catch {
    return false;
  }
}
