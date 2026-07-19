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

/**
 * Lesson "exposure" signal (ADR-0010). Marking a lesson read is NOT proof of
 * mastery — a learner can breeze through without attention — so it only records a
 * light exposure floor, deliberately BELOW the critical-concept floor (~0.6) and
 * far below "mastered" (0.8). It never completes a plan week and never grants the
 * mastery that drives advancement; only gates/tests do that. Applied via GREATEST
 * so it can never lower a real (assessed) score.
 */
export const LESSON_EXPOSURE_LEVEL = 0.35;

function requireSql() {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  if (!url) {
    throw new Error('DATABASE_URL is not set on this Vercel deployment.');
  }
  return neon(url);
}

/**
 * Record lesson exposure: nudge concept mastery up to the exposure floor (never
 * lowering an assessed score) + bump lessons_completed_count.
 *
 * ADR-0010: lessons are decoupled from advancement. This NEVER completes a plan
 * week — week completion and advancement come solely from passing the gate/tests.
 * `week_completed` is retained in the return shape (always false) for API stability.
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
    VALUES (${learnerId}, ${canonicalId}, ${LESSON_EXPOSURE_LEVEL}, 1, NOW(), NOW())
    ON CONFLICT (learner_id, concept_id) DO UPDATE SET
      score = GREATEST(concept_mastery.score, ${LESSON_EXPOSURE_LEVEL}),
      last_activity = NOW(),
      updated_at = NOW()
  `;

  if (rawId !== canonicalId) {
    await s`
      INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
      VALUES (${learnerId}, ${rawId}, ${LESSON_EXPOSURE_LEVEL}, 1, NOW(), NOW())
      ON CONFLICT (learner_id, concept_id) DO UPDATE SET
        score = GREATEST(concept_mastery.score, ${LESSON_EXPOSURE_LEVEL}),
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
    // Column may not exist yet; exposure update is the critical path for lesson UI.
  }

  return { new_mastery: LESSON_EXPOSURE_LEVEL, week_completed: false };
}
