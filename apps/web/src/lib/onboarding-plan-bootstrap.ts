/**
 * Ultra-light onboarding plan bootstrap for Vercel.
 *
 * Intentionally does NOT import neon-db / kg-data / learning-plan — those modules
 * are huge and cold-starts + advisory-lock transactions caused FUNCTION_INVOCATION_TIMEOUT.
 *
 * Contract: persist profile + exactly 2 weeks × ≤4 concepts with a few HTTP SQL calls.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import { deriveOnboardingSeedScores } from '@/lib/onboarding-self-score';
// plan-pacing imports ONLY the generated frontier manifest (no kg-data / neon-db /
// buildLearningPlan), so it is safe on the onboarding critical path.
import { hasFrontier, selectNextConcepts } from '@/lib/plan-pacing';
// plan-capacity is pure (no kg-data / neon-db), safe on the onboarding critical path.
// R1: planHorizon — single source of truth for goal horizon weeks.
// R2: conceptsPerWeekFromHours — capacity mapping from hours_per_week.
import { planHorizon, conceptsPerWeekFromHours } from '@/lib/plan-capacity';

neonConfig.fetchConnectionCache = true;

/** Local copy — do not import from neon-db (pulls kg-data + monolith). */
export interface OnboardingBootstrapPayload {
  goal: string;
  grade_level?: string | null;
  points_group?: string | null;
  subjects: string[];
  hours_per_week: number;
  preferred_style?: string | null;
  attention_span?: number | null;
  self_scores?: Record<string, number>;
  background_notes?: string | null;
  next_test_name?: string | null;
  next_test_date?: string | null;
  final_goal_date?: string | null;
  mental_state?: Record<string, unknown> | null;
  personality_profile?: Record<string, unknown> | null;
  tutor_mode?: 'direct' | 'socratic' | null;
  adult_learner?: boolean;
  years_gap?: string | null;
}

const ROLLING_WEEKS = 2;
// CONCEPTS_PER_WEEK_CAP: hard cap for bootstrap to stay under Vercel timeout.
// Actual per-week capacity is dynamic (conceptsPerWeekFromHours) up to this cap.
const CONCEPTS_PER_WEEK_CAP = 4;
const PLAN_SCHEMA_VERSION = 2;

function requireSql() {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  if (!url) {
    throw new Error('DATABASE_URL is not set on this Vercel deployment.');
  }
  return neon(url);
}

function chunkWeeks(concepts: string[], numWeeks: number, perWeek: number): string[][] {
  const weeks: string[][] = Array.from({ length: numWeeks }, () => []);
  const limited = concepts.slice(0, numWeeks * perWeek);
  for (let i = 0; i < limited.length; i += 1) {
    const idx = Math.min(numWeeks - 1, Math.floor(i / perWeek));
    weeks[idx]!.push(limited[i]!);
  }
  if (weeks[0]!.length === 0 && limited[0]) weeks[0]!.push(limited[0]);
  return weeks;
}

/** Self-rating (1–10) → mastery (0.1–0.9). Mirrors the concept_mastery seeding below. */
function seedScoreToMastery(score: number): number {
  const clamped = Math.max(1, Math.min(10, score));
  return 0.1 + ((clamped - 1) * 0.8) / 9;
}

function resolveGoalKey(payload: OnboardingBootstrapPayload): string | null {
  const fromProfile = (payload.personality_profile as { goal_key?: unknown } | null | undefined)
    ?.goal_key;
  if (typeof fromProfile === 'string' && hasFrontier(fromProfile)) return fromProfile;
  if (typeof payload.goal === 'string' && hasFrontier(payload.goal)) return payload.goal;
  return null;
}

function pickConceptIds(payload: OnboardingBootstrapPayload): string[] {
  const scores = deriveOnboardingSeedScores({
    goal: payload.goal,
    subjects: payload.subjects,
    grade_level: payload.grade_level,
    points_group: payload.points_group,
    self_scores: payload.self_scores,
    personality_profile: payload.personality_profile,
    adult_learner: payload.adult_learner,
  });

  // Frontier-driven first plan (ADR-0009): start the learner on their goal frontier,
  // ANCHORED to their self-rated level so an advanced-goal learner is not dragged
  // back through elementary foundations. Self-rated concepts form the engaged set
  // (their entry level); low-rated ones are remediation-eligible; already-strong ones
  // are skipped. This makes the plan end-to-end from day one and consistent with the
  // living rolling-window re-pace.
  const goalKey = resolveGoalKey(payload);
  if (goalKey && hasFrontier(goalKey)) {
    const masteryScores: Record<string, number> = {};
    const weak: string[] = [];
    for (const [id, raw] of Object.entries(scores)) {
      const m = seedScoreToMastery(raw);
      masteryScores[id] = m;
      if (m < 0.4) weak.push(id);
    }
    const picked = selectNextConcepts({
      goalKey,
      masteryScores,
      engagedConceptIds: Object.keys(scores),
      weakConceptIds: weak,
      limit: ROLLING_WEEKS * CONCEPTS_PER_WEEK_CAP,
    });
    if (picked.length > 0) return picked;
  }

  const ids = Object.keys(scores);
  if (ids.length > 0) return ids.slice(0, ROLLING_WEEKS * CONCEPTS_PER_WEEK_CAP);
  // Absolute last resort — never return empty.
  if (payload.subjects.includes('physics')) {
    return ['units_measurement', 'kinematics_1d', 'newton_laws', 'work_energy', 'electrostatics', 'waves_basics', 'optics_geometric', 'electric_circuits'];
  }
  return [
    'algebra_basics',
    'equations_linear',
    'functions_linear',
    'geometry_basics',
    'equations_quadratic',
    'trigonometry_ratios',
    'limits',
    'derivatives_intro',
  ];
}

/**
 * Save profile + create a verified 2-week plan. No advisory locks, no neon-db.
 */
export async function bootstrapOnboardingPlan(
  learnerId: string,
  payload: OnboardingBootstrapPayload,
): Promise<{ plan_id: string; concept_count: number; week_count: number }> {
  const s = requireSql();
  const selfScores = deriveOnboardingSeedScores({
    goal: payload.goal,
    subjects: payload.subjects,
    grade_level: payload.grade_level,
    points_group: payload.points_group,
    self_scores: payload.self_scores,
    personality_profile: payload.personality_profile,
    adult_learner: payload.adult_learner,
  });
  const enriched: OnboardingBootstrapPayload = { ...payload, self_scores: selfScores };
  const personalityProfile = {
    ...(enriched.personality_profile ?? {}),
    ...(enriched.tutor_mode ? { tutor_mode: enriched.tutor_mode } : {}),
  };

  const conceptIds = pickConceptIds(enriched);

  // R1: Derive horizon from goal dates; cap at ROLLING_WEEKS for the initial bootstrap
  // to stay under Vercel timeout (per golden-path constraint: ≤2 weeks on first create).
  const horizonFromProfile = planHorizon(enriched);
  const numWeeks = Math.min(horizonFromProfile ?? ROLLING_WEEKS, ROLLING_WEEKS);
  // R2: Capacity from hours_per_week; hard-capped at CONCEPTS_PER_WEEK_CAP=4 for bootstrap speed.
  const perWeek = Math.min(conceptsPerWeekFromHours(enriched.hours_per_week), CONCEPTS_PER_WEEK_CAP);
  const weekGroups = chunkWeeks(conceptIds, numWeeks, perWeek);

  // Guard against concurrent bootstraps (Bug 2): if an active plan was created
  // in the last 60 seconds and already has weeks, return it without re-creating.
  const recentRows = (await s`
    SELECT lp.id AS plan_id, COUNT(pw.id)::int AS week_count
    FROM learning_plans lp
    LEFT JOIN plan_weeks pw ON pw.plan_id = lp.id
    WHERE lp.learner_id = ${learnerId}
      AND lp.status = 'active'
      AND lp.created_at > NOW() - INTERVAL '60 seconds'
    GROUP BY lp.id
    HAVING COUNT(pw.id) >= 1
    LIMIT 1
  `) as Array<{ plan_id: string; week_count: number }>;
  if (recentRows[0]) {
    return {
      plan_id: recentRows[0].plan_id,
      concept_count: conceptIds.length,
      week_count: recentRows[0].week_count,
    };
  }

  const planId = randomUUID();
  const startDate = new Date();
  const endDate = new Date(startDate);
  // R1: end_date reflects the TRUE goal horizon (not just the rolling window) so the
  // dashboard shows the correct plan expiry. Capped at ROLLING_WEEKS when no goal date.
  const endHorizonWeeks = horizonFromProfile ?? ROLLING_WEEKS;
  endDate.setDate(endDate.getDate() + 7 * endHorizonWeeks);
  const startStr = startDate.toISOString().slice(0, 10);
  const endStr = endDate.toISOString().slice(0, 10);

  // 1) Profile upsert
  await s`
    INSERT INTO learner_profiles (
      learner_id, goal, grade_level, points_group, subjects, hours_per_week,
      preferred_style, attention_span, self_scores, background_notes,
      next_test_name, next_test_date, final_goal_date, mental_state, personality_profile,
      created_at, updated_at
    )
    VALUES (
      ${learnerId}, ${enriched.goal}, ${enriched.grade_level ?? null}, ${enriched.points_group ?? null},
      ${enriched.subjects}, ${enriched.hours_per_week},
      ${enriched.preferred_style ?? null}, ${enriched.attention_span ?? null},
      ${JSON.stringify(enriched.self_scores ?? {})}::jsonb, ${enriched.background_notes ?? null},
      ${enriched.next_test_name ?? null}, ${enriched.next_test_date ?? null}, ${enriched.final_goal_date ?? null},
      ${JSON.stringify(enriched.mental_state ?? {})}::jsonb,
      ${JSON.stringify(personalityProfile)}::jsonb,
      NOW(), NOW()
    )
    ON CONFLICT (learner_id) DO UPDATE SET
      goal = EXCLUDED.goal,
      grade_level = EXCLUDED.grade_level,
      points_group = EXCLUDED.points_group,
      subjects = EXCLUDED.subjects,
      hours_per_week = EXCLUDED.hours_per_week,
      preferred_style = EXCLUDED.preferred_style,
      attention_span = EXCLUDED.attention_span,
      self_scores = EXCLUDED.self_scores,
      background_notes = EXCLUDED.background_notes,
      next_test_name = EXCLUDED.next_test_name,
      next_test_date = EXCLUDED.next_test_date,
      final_goal_date = EXCLUDED.final_goal_date,
      mental_state = EXCLUDED.mental_state,
      personality_profile = EXCLUDED.personality_profile,
      updated_at = NOW()
  `;

  // 2) Seed mastery (sequential but tiny — max 8 rows)
  for (const [conceptId, score] of Object.entries(selfScores).slice(0, 8)) {
    const clamped = Math.max(1, Math.min(10, score));
    const mastery = 0.1 + ((clamped - 1) * 0.8) / 9;
    await s`
      INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
      VALUES (${learnerId}, ${conceptId}, ${mastery}, 1, NOW(), NOW())
      ON CONFLICT (learner_id, concept_id) DO UPDATE SET
        score = EXCLUDED.score,
        last_activity = NOW()
    `;
  }

  // 3) Atomic replace: delete old plans + insert new plan + weeks in one HTTP transaction
  // (Bug 1 fix: no advisory lock — avoids the 1/0 hang; single round-trip prevents
  //  mid-flight abort from leaving the learner planless).
  const weekInserts = weekGroups.flatMap((concepts, i) => {
    if (concepts.length === 0) return [];
    const weekId = randomUUID();
    const quizDue = new Date(startDate);
    quizDue.setDate(quizDue.getDate() + 7 * (i + 1));
    const status = i === 0 ? 'active' : 'upcoming';
    return [
      s`
        INSERT INTO plan_weeks (id, plan_id, week_number, concepts, quiz_due_at, status)
        VALUES (${weekId}, ${planId}, ${i + 1}, ${concepts}, ${quizDue.toISOString()}, ${status})
      `,
    ];
  });

  await s.transaction([
    s`DELETE FROM plan_weeks WHERE plan_id IN (SELECT id FROM learning_plans WHERE learner_id = ${learnerId})`,
    s`DELETE FROM learning_plans WHERE learner_id = ${learnerId}`,
    s`
      INSERT INTO learning_plans (
        id, learner_id, goal, start_date, end_date, status,
        plan_schema_version, plan_adjustment_kind, plan_last_adjusted_at,
        created_at, updated_at
      )
      VALUES (
        ${planId}, ${learnerId}, ${enriched.goal}, ${startStr}, ${endStr}, 'active',
        ${PLAN_SCHEMA_VERSION}, NULL, NULL,
        NOW(), NOW()
      )
    `,
    ...weekInserts,
  ]);

  // 4) Verify
  const rows = (await s`
    SELECT COUNT(*)::int AS n
    FROM plan_weeks
    WHERE plan_id = ${planId}::uuid
  `) as Array<{ n: number }>;
  const weekCount = rows[0]?.n ?? 0;
  if (weekCount < 1) {
    throw new Error('Plan bootstrap failed: no weeks persisted');
  }

  return {
    plan_id: planId,
    concept_count: conceptIds.length,
    week_count: weekCount,
  };
}

export async function learnerHasPlan(learnerId: string): Promise<boolean> {
  const s = requireSql();
  const rows = (await s`
    SELECT 1 AS ok FROM learning_plans
    WHERE learner_id = ${learnerId} AND status = 'active'
    LIMIT 1
  `) as Array<{ ok: number }>;
  return rows.length > 0;
}
