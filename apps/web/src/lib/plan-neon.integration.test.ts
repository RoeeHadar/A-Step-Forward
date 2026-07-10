/**
 * Live Neon smoke test — skipped when DATABASE_URL is unset.
 * Simulates the Mentor/Tutor chat finalizeAssistantTurn plan-write path.
 */
import { describe, expect, it } from 'vitest';
import {
  extractPlanUpdate,
  learnerConfirmedChange,
  planPayloadToOptions,
} from './plan-actions';

const hasDb = (() => {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  return /^postgres(ql)?:\/\/.+@/.test(url);
})();

describe.skipIf(!hasDb)('plan persistence (live Neon)', () => {
  it('simulates chat confirm → ASF_PLAN_UPDATE → regenerated plan in DB', async () => {
    const {
      dbConfigured,
      getCurrentPlan,
      generateLearningPlan,
      getLearnerProfile,
      applyPlanProfileUpdates,
    } = await import('./neon-db');

    expect(dbConfigured).toBe(true);

    const { neon } = await import('@neondatabase/serverless');
    const sql = neon(process.env.DATABASE_URL ?? process.env.POSTGRES_URL!);

    let withPlan: Array<{ learner_id: string }>;
    try {
      withPlan = (await sql`
        SELECT lp.learner_id
        FROM learning_plans lp
        JOIN learner_profiles p ON p.learner_id = lp.learner_id
        WHERE lp.status = 'active'
        ORDER BY lp.updated_at DESC NULLS LAST
        LIMIT 1
      `) as Array<{ learner_id: string }>;
    } catch (err) {
      console.warn('[plan-neon] Neon unreachable — skipping live assertion:', String(err));
      return;
    }

    let learnerId = withPlan[0]?.learner_id;
    if (!learnerId) {
      const profiles = (await sql`
        SELECT learner_id FROM learner_profiles ORDER BY updated_at DESC LIMIT 1
      `) as Array<{ learner_id: string }>;
      if (!profiles[0]) {
        console.warn('[plan-neon] no learner_profiles row — skipping live assertion');
        return;
      }
      learnerId = profiles[0].learner_id;
      await generateLearningPlan(learnerId);
    }

    const before = await getCurrentPlan(learnerId);
    expect(before).not.toBeNull();

    const userMessage = 'yes, please update my plan';
    const assistantRaw = [
      'מעולה — מעדכן את התוכנית השבועית שלך.',
      '[[ASF_PLAN_UPDATE:{"confirmed":true,"reason":"smoke test priority limits","priority_concepts":["limits","khan_academy_fake"],"prepend_concepts":[],"exclude_concepts":[],"goal_key":"bagrut_math_5"}]]',
    ].join('\n');

    expect(learnerConfirmedChange(userMessage)).toBe(true);
    const { visible, payload } = extractPlanUpdate(assistantRaw);
    expect(visible).not.toContain('ASF_PLAN_UPDATE');
    expect(payload).not.toBeNull();
    expect(payload!.priority_concepts).toEqual(['limits']);
    expect(payload!.goal_key).toBe('bagrut_math_5');

    await applyPlanProfileUpdates(learnerId, {
      goal_key: payload!.goal_key,
    });
    const plan = await generateLearningPlan(learnerId, planPayloadToOptions(payload!));
    expect(plan.id).not.toBe(before!.id);
    expect(plan.weeks.length).toBeGreaterThan(0);

    const allConceptIds = plan.weeks.flatMap((w) => w.concepts.map((c) => c.concept_id));
    expect(allConceptIds).toContain('limits');
    expect(allConceptIds).not.toContain('khan_academy_fake');

    const after = await getCurrentPlan(learnerId);
    expect(after?.id).toBe(plan.id);

    const profile = await getLearnerProfile(learnerId);
    expect(profile?.points_group).toBe('5pt');
  }, 60_000);

  it('week 1 top concept matches buildLearningPlan path[0] for same goal', async () => {
    const { generateLearningPlan, getLearnerProfile } = await import('./neon-db');
    const { buildLearningPlan } = await import('./learning-plan');
    const { resolveGoalConceptId } = await import('./plan-worklist');

    const { neon } = await import('@neondatabase/serverless');
    const sql = neon(process.env.DATABASE_URL ?? process.env.POSTGRES_URL!);

    let learnerId: string | undefined;
    try {
      const rows = (await sql`
        SELECT learner_id FROM learner_profiles ORDER BY updated_at DESC LIMIT 1
      `) as Array<{ learner_id: string }>;
      learnerId = rows[0]?.learner_id;
    } catch (err) {
      console.warn('[plan-neon] Neon unreachable — skipping unify assertion:', String(err));
      return;
    }
    if (!learnerId) {
      console.warn('[plan-neon] no learner_profiles row — skipping unify assertion');
      return;
    }

    const profile = await getLearnerProfile(learnerId);
    if (!profile) return;

    const { getConceptMastery } = await import('./neon-db');
    const mastery = await getConceptMastery(learnerId);
    const goalConceptId = resolveGoalConceptId(profile, mastery, {});
    if (!goalConceptId) {
      console.warn('[plan-neon] no resolvable goal concept — skipping unify assertion');
      return;
    }

    const plan = await generateLearningPlan(learnerId);
    const week1Concepts = plan.weeks[0]?.concepts.map((c) => c.concept_id) ?? [];
    if (week1Concepts.length === 0) {
      console.warn('[plan-neon] empty week 1 worklist — skipping unify assertion');
      return;
    }

    const learningPlan = await buildLearningPlan({
      learnerId,
      goalConceptId,
      maxNodes: Math.max(24, plan.weeks.length * 4),
    });
    const nextStep = learningPlan?.path.find((n) => n.relation !== 'self');
    if (!nextStep) {
      console.warn('[plan-neon] buildLearningPlan returned no non-self step — skipping');
      return;
    }

    expect(week1Concepts[0]).toBe(nextStep.concept_id);
  }, 60_000);
});
