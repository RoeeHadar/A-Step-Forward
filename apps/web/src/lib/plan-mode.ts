/**
 * Plan study mode + time-phase mix (lesson → train → rest).
 * Pure — safe for unit tests.
 */

export type PlanStudyMode = 'lessons_and_train' | 'train_dominant' | 'rest_day';
export type PlanTimePhase = 'lesson_heavy' | 'train_heavy' | 'rest';

export function fractionTimeUsed(opts: {
  planStartIso: string;
  goalDeadlineIso: string;
  now?: Date;
}): number {
  const start = new Date(opts.planStartIso.slice(0, 10) + 'T12:00:00').getTime();
  const goal = new Date(opts.goalDeadlineIso.slice(0, 10) + 'T12:00:00').getTime();
  const now = (opts.now ?? new Date()).getTime();
  if (!(goal > start)) return 1;
  return Math.max(0, (now - start) / (goal - start));
}

export function phaseFromFraction(
  fractionUsed: number,
  daysToGoal: number | null,
): PlanTimePhase {
  if (daysToGoal != null && daysToGoal <= 1) return 'rest';
  if (fractionUsed >= 0.95) return 'rest';
  if (fractionUsed >= 0.8) return 'train_heavy';
  return 'lesson_heavy';
}

export const TRAIN_DOMINANT_READINESS = 0.7;
export const TRAIN_DOMINANT_DAYS = 14;
export const TRAIN_BEHAVIOR_MIN_SIGNALS = 2;

export function computePlanMode(opts: {
  daysToGoal: number | null;
  readiness: number | null;
  strongPracticeSignals?: number;
  phase?: PlanTimePhase;
}): PlanStudyMode {
  if (opts.phase === 'rest' || (opts.daysToGoal != null && opts.daysToGoal <= 1)) {
    return 'rest_day';
  }
  const signals = opts.strongPracticeSignals ?? 0;
  const nearExam =
    opts.daysToGoal != null && opts.daysToGoal <= TRAIN_DOMINANT_DAYS;
  const readyEnough =
    opts.readiness != null && opts.readiness >= TRAIN_DOMINANT_READINESS;
  if (signals >= TRAIN_BEHAVIOR_MIN_SIGNALS) return 'train_dominant';
  if (nearExam && readyEnough) return 'train_dominant';
  if (opts.phase === 'train_heavy') return 'train_dominant';
  return 'lessons_and_train';
}

export function trainTargetCount(mode: PlanStudyMode, phase: PlanTimePhase): number {
  if (mode === 'rest_day' || phase === 'rest') return 0;
  if (mode === 'train_dominant' || phase === 'train_heavy') return 12;
  return 6;
}

export function lessonTrainSplit(
  conceptCount: number,
  mode: PlanStudyMode,
  phase: PlanTimePhase,
): { lessons: number; trains: number; rest: boolean } {
  if (mode === 'rest_day' || phase === 'rest') {
    return { lessons: 0, trains: 0, rest: true };
  }
  const n = Math.max(0, conceptCount);
  if (mode === 'train_dominant' || phase === 'train_heavy') {
    const lessons = Math.min(1, n);
    return { lessons, trains: Math.max(0, n - lessons), rest: false };
  }
  const lessons = Math.max(1, Math.ceil(n * 0.75));
  return { lessons: Math.min(lessons, n), trains: Math.max(0, n - lessons), rest: false };
}

export function formatPlanModeBlock(
  snap: {
    mode: PlanStudyMode;
    phase: PlanTimePhase;
    daysToGoal: number | null;
    readinessPct: number | null;
    goalLabel: string;
    weakConcepts: string[];
  },
  locale: 'he' | 'en' = 'he',
): string {
  const modeLabel =
    locale === 'he'
      ? snap.mode === 'rest_day'
        ? 'יום מנוחה / רפלקציה'
        : snap.mode === 'train_dominant'
          ? 'אימון-דומיננטי'
          : 'שיעורים + אימון'
      : snap.mode === 'rest_day'
        ? 'rest / reflect'
        : snap.mode === 'train_dominant'
          ? 'train-dominant'
          : 'lessons + train';
  const lines =
    locale === 'he'
      ? [
          '## מצב תוכנית הלמידה',
          `- יעד: ${snap.goalLabel}`,
          `- מצב: ${modeLabel}`,
          snap.daysToGoal != null ? `- ימים ליעד: ${snap.daysToGoal}` : null,
          snap.readinessPct != null ? `- מוכנות ליעד: ~${snap.readinessPct}%` : null,
          snap.weakConcepts.length
            ? `- חיזוק: ${snap.weakConcepts.slice(0, 3).join(', ')}`
            : null,
          snap.mode === 'train_dominant'
            ? '- העדף אימון (Practice Arena) על שיעורים חדשים; הסברים קצרים בלבד.'
            : null,
          snap.mode === 'rest_day'
            ? '- יום מנוחה: אל תדחוף נושא חדש; רפלקציה קלה רק אם מבקשים.'
            : null,
        ]
      : [
          '## Learner plan mode',
          `- Goal: ${snap.goalLabel}`,
          `- Mode: ${modeLabel}`,
          snap.daysToGoal != null ? `- Days to goal: ${snap.daysToGoal}` : null,
          snap.readinessPct != null ? `- Goal readiness: ~${snap.readinessPct}%` : null,
          snap.weakConcepts.length
            ? `- Strengthen: ${snap.weakConcepts.slice(0, 3).join(', ')}`
            : null,
          snap.mode === 'train_dominant'
            ? '- Prefer Practice Arena over new lessons; keep explanations short.'
            : null,
          snap.mode === 'rest_day'
            ? '- Rest day: do not push new topics; light reflection only if asked.'
            : null,
        ];
  return lines.filter(Boolean).join('\n');
}
