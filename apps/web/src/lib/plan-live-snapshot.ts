import {
  computePlanMode,
  formatPlanModeBlock,
  fractionTimeUsed,
  phaseFromFraction,
  type PlanStudyMode,
  type PlanTimePhase,
} from '@/lib/plan-mode';
import {
  daysUntilIso,
  isBagrutTrack,
  readinessTitle,
  resolveGoalDeadlineIso,
} from '@/lib/goal-track';

export interface PlanLiveSnapshotInput {
  goal: string | null;
  goalKey?: string | null;
  nextTestDate?: string | null;
  finalGoalDate?: string | null;
  planStartIso?: string | null;
  readiness?: number | null;
  weakConceptLabels?: string[];
  activeLessonLabels?: string[];
  activeTrainLabels?: string[];
  strongPracticeSignals?: number;
}

export interface PlanLiveSnapshot {
  mode: PlanStudyMode;
  phase: PlanTimePhase;
  daysToGoal: number | null;
  readinessPct: number | null;
  goalLabel: string;
  isBagrut: boolean;
  weakConcepts: string[];
  activeLessons: string[];
  activeTrains: string[];
  contextBlockHe: string;
  contextBlockEn: string;
}

export function buildPlanLiveSnapshot(input: PlanLiveSnapshotInput): PlanLiveSnapshot {
  const goalLabel = (input.goal ?? '').trim() || 'Learning goal';
  const isBagrut = isBagrutTrack({ goalKey: input.goalKey, goal: input.goal });
  const deadline = resolveGoalDeadlineIso(input.nextTestDate, input.finalGoalDate);
  const daysToGoal = daysUntilIso(deadline);
  const fraction =
    input.planStartIso && deadline
      ? fractionTimeUsed({
          planStartIso: input.planStartIso,
          goalDeadlineIso: deadline,
        })
      : 0;
  const phase = phaseFromFraction(fraction, daysToGoal);
  const mode = computePlanMode({
    daysToGoal,
    readiness: input.readiness ?? null,
    strongPracticeSignals: input.strongPracticeSignals ?? 0,
    phase,
  });
  const readinessPct =
    input.readiness != null && Number.isFinite(input.readiness)
      ? Math.round(input.readiness * 100)
      : null;
  const weakConcepts = (input.weakConceptLabels ?? []).slice(0, 3);
  const snap = {
    mode,
    phase,
    daysToGoal,
    readinessPct,
    goalLabel,
    weakConcepts,
  };
  return {
    ...snap,
    isBagrut,
    activeLessons: input.activeLessonLabels ?? [],
    activeTrains: input.activeTrainLabels ?? [],
    contextBlockHe: formatPlanModeBlock(snap, 'he'),
    contextBlockEn: formatPlanModeBlock(snap, 'en'),
  };
}

export function liveSnapshotTitle(locale: 'he' | 'en', isBagrut: boolean): string {
  return readinessTitle(locale, { isBagrut });
}
