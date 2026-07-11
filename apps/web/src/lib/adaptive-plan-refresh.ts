/**
 * Proactive wellbeing-driven plan refresh (ADR-0008).
 * Layer A: always sync bias to profile. Layer B: regenerate plan when gated.
 */
import 'server-only';
import {
  generateLearningPlan,
  getConceptMastery,
  getCurrentPlan,
  getLearnerProfile,
  isFreshOnboardingPlan,
  saveWellbeingPlanBias,
} from '@/lib/neon-db';
import {
  canPersistWellbeingRewrite,
  detectMasteryShock,
  evaluateWellbeingSignals,
  pickPrimaryWellbeingTrigger,
  type WellbeingProfileInput,
  type WellbeingTrigger,
  wellbeingPlanBiasFromProfile,
} from '@/lib/wellbeing-plan-bias';

export type AdaptivePlanRefreshReason =
  | 'profile_mental_state'
  | 'profile_exam_date'
  | 'mastery_update'
  | 'plan_profile_update';

export interface AdaptivePlanRefreshResult {
  refreshed: boolean;
  biasSaved: boolean;
  trigger: WellbeingTrigger | null;
}

function profileInputFromRow(
  profile: NonNullable<Awaited<ReturnType<typeof getLearnerProfile>>>,
): WellbeingProfileInput {
  return {
    subjects: profile.subjects,
    mental_state: profile.mental_state,
    next_test_date: profile.next_test_date,
    personality_profile: profile.personality_profile,
    points_group: profile.points_group,
    wellbeing_plan_bias: profile.wellbeing_plan_bias,
  };
}

function triggerAllowedForReason(
  reason: AdaptivePlanRefreshReason,
  triggers: WellbeingTrigger[],
  primary: WellbeingTrigger | null,
): boolean {
  if (!primary) return false;
  switch (reason) {
    case 'mastery_update':
      return triggers.includes('mastery_shock');
    case 'profile_mental_state':
      return triggers.includes('profile_anxiety');
    case 'profile_exam_date':
    case 'plan_profile_update':
      return (
        triggers.includes('exam_window') ||
        triggers.includes('profile_anxiety') ||
        triggers.includes('mastery_shock')
      );
    default:
      return false;
  }
}

/**
 * Sync internal wellbeing bias (Layer A). Returns updated bias after evaluation.
 */
export async function syncWellbeingBiasForLearner(learnerId: string, now = new Date()) {
  const profile = await getLearnerProfile(learnerId);
  if (!profile) return null;

  const mastery = await getConceptMastery(learnerId);
  const previousBias = wellbeingPlanBiasFromProfile(profileInputFromRow(profile), now);
  const { bias } = evaluateWellbeingSignals(
    profileInputFromRow(profile),
    mastery,
    previousBias,
    now,
  );
  await saveWellbeingPlanBias(learnerId, bias);
  return bias;
}

/**
 * Evaluate signals and optionally regenerate the persisted weekly plan (Layer B).
 * No-op when learner has no active plan yet (pre-onboarding plan generate).
 */
export async function maybeRefreshLearningPlanForSignals(
  learnerId: string,
  reason: AdaptivePlanRefreshReason,
  now = new Date(),
): Promise<AdaptivePlanRefreshResult> {
  const profile = await getLearnerProfile(learnerId);
  if (!profile) {
    return { refreshed: false, biasSaved: false, trigger: null };
  }

  const mastery = await getConceptMastery(learnerId);
  const profileInput = profileInputFromRow(profile);
  const previousBias = wellbeingPlanBiasFromProfile(profileInput, now);
  const { bias, triggers } = evaluateWellbeingSignals(
    profileInput,
    mastery,
    previousBias,
    now,
  );
  await saveWellbeingPlanBias(learnerId, bias);

  const primaryTrigger = pickPrimaryWellbeingTrigger(triggers);
  if (!triggerAllowedForReason(reason, triggers, primaryTrigger)) {
    return { refreshed: false, biasSaved: true, trigger: primaryTrigger };
  }

  const plan = await getCurrentPlan(learnerId);
  if (!plan) {
    return { refreshed: false, biasSaved: true, trigger: primaryTrigger };
  }

  if (
    reason === 'mastery_update' &&
    !detectMasteryShock(mastery, previousBias.mastery_snapshot, profile.subjects)
  ) {
    return { refreshed: false, biasSaved: true, trigger: primaryTrigger };
  }

  if (!canPersistWellbeingRewrite(bias, primaryTrigger, profileInput, now)) {
    return { refreshed: false, biasSaved: true, trigger: primaryTrigger };
  }

  if (await isFreshOnboardingPlan(learnerId)) {
    return { refreshed: false, biasSaved: true, trigger: primaryTrigger };
  }

  await generateLearningPlan(learnerId);
  return { refreshed: true, biasSaved: true, trigger: primaryTrigger };
}

/** Fire-and-forget hook for hot paths (lesson answers, profile saves). */
export function scheduleAdaptivePlanRefresh(
  learnerId: string,
  reason: AdaptivePlanRefreshReason,
): void {
  void maybeRefreshLearningPlanForSignals(learnerId, reason).catch((err) => {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[adaptive-plan-refresh]', reason, err);
    }
  });
}
