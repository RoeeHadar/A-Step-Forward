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
const CONCEPTS_PER_WEEK = 4;
const PLAN_SCHEMA_VERSION = 2;

function requireSql() {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  if (!url) {
    throw new Error('DATABASE_URL is not set on this Vercel deployment.');
  }
  return neon(url);
}

function chunkWeeks(concepts: string[]): string[][] {
  const limited = concepts.slice(0, ROLLING_WEEKS * CONCEPTS_PER_WEEK);
  const weeks: string[][] = [[], []];
  for (let i = 0; i < limited.length; i += 1) {
    const idx = Math.min(ROLLING_WEEKS - 1, Math.floor(i / CONCEPTS_PER_WEEK));
    weeks[idx]!.push(limited[i]!);
  }
  if (weeks[0]!.length === 0 && limited[0]) weeks[0]!.push(limited[0]);
  // Mirror week-1 concepts into week-2 if we only have a handful — student always sees 2 weeks.
  if (weeks[1]!.length === 0 && weeks[0]!.length > 0) {
    weeks[1] = weeks[0]!.slice(0, CONCEPTS_PER_WEEK);
  }
  return weeks;
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
  const ids = Object.keys(scores);
  if (ids.length > 0) return ids.slice(0, ROLLING_WEEKS * CONCEPTS_PER_WEEK);
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
  const weekGroups = chunkWeeks(conceptIds);
  const planId = randomUUID();
  const startDate = new Date();
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 7 * ROLLING_WEEKS);
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

  // 3) Replace any prior plan — no advisory lock (lock + 1/0 caused hangs on Neon HTTP)
  await s`DELETE FROM plan_weeks WHERE plan_id IN (SELECT id FROM learning_plans WHERE learner_id = ${learnerId})`;
  await s`DELETE FROM learning_plans WHERE learner_id = ${learnerId}`;

  await s`
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
  `;

  for (let i = 0; i < weekGroups.length; i += 1) {
    const concepts = weekGroups[i]!;
    if (concepts.length === 0) continue;
    const weekId = randomUUID();
    const quizDue = new Date(startDate);
    quizDue.setDate(quizDue.getDate() + 7 * (i + 1));
    const status = i === 0 ? 'active' : 'upcoming';
    await s`
      INSERT INTO plan_weeks (id, plan_id, week_number, concepts, quiz_due_at, status)
      VALUES (${weekId}, ${planId}, ${i + 1}, ${concepts}, ${quizDue.toISOString()}, ${status})
    `;
  }

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
