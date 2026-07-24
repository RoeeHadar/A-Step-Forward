import { TRAIN_BEHAVIOR_MIN_SIGNALS } from '@/lib/plan-mode';

export { TRAIN_BEHAVIOR_MIN_SIGNALS };

export function countStrongPracticeSignals(
  conceptIds: string[],
  practiceByConcept: Record<string, { successes: number; attempts: number }>,
  opts: { minSuccesses?: number; minAccuracy?: number } = {},
): number {
  const minSuccesses = opts.minSuccesses ?? 2;
  const minAccuracy = opts.minAccuracy ?? 0.7;
  let n = 0;
  for (const id of conceptIds) {
    const row = practiceByConcept[id];
    if (!row || row.attempts <= 0) continue;
    const acc = row.successes / row.attempts;
    if (row.successes >= minSuccesses && acc >= minAccuracy) n += 1;
  }
  return n;
}

export function shouldPromoteTrainDominant(strongSignals: number): boolean {
  return strongSignals >= TRAIN_BEHAVIOR_MIN_SIGNALS;
}
