/**
 * AS-51 (Phase 4 C5): 4-parameter Bayesian Knowledge Tracing, pure (no I/O, no clock).
 * Formula + global params: items/AS-44/asf-researcher.md §3, §5 (Corbett & Anderson 1995).
 *   correct: P(L|c) = P(L)(1-S) / [P(L)(1-S) + (1-P(L))G]
 *   wrong:   P(L|w) = P(L)S     / [P(L)S     + (1-P(L))(1-G)]
 *   P(L_next) = P(L|obs) + (1 - P(L|obs)) T
 * Read-time only, behind MASTERY_MODEL (default 'ratio' = unchanged successes/attempts).
 */
import { PRACTICE_SUCCESS_PROCESS_SCORE } from '@/lib/practice-arena';

export interface BktParams { p_init: number; p_learn: number; p_guess: number; p_slip: number }

/** AS-44 §5 global params. */
export const BKT_GLOBAL_PARAMS: Readonly<BktParams> = Object.freeze({ p_init: 0.2, p_learn: 0.1, p_guess: 0.2, p_slip: 0.1 });

export function validateBktParams(p: BktParams): BktParams {
  for (const v of [p.p_init, p.p_learn, p.p_guess, p.p_slip]) {
    if (!Number.isFinite(v) || v < 0 || v > 1) throw new Error('bkt: params must be in [0,1]');
  }
  if (p.p_guess + p.p_slip >= 1) throw new Error('bkt: p_guess + p_slip must be < 1');
  return p;
}

const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);

/** One BKT step: prior P(L) + observation -> next P(L). */
export function bktUpdate(pKnown: number, correct: boolean, params: BktParams = BKT_GLOBAL_PARAMS): number {
  const { p_learn: T, p_guess: G, p_slip: S } = validateBktParams(params);
  const L = clamp01(pKnown);
  const num = correct ? L * (1 - S) : L * S;
  const den = correct ? num + (1 - L) * G : num + (1 - L) * (1 - G);
  const post = den > 0 ? num / den : L;
  return clamp01(post + (1 - post) * T);
}

/** Replay an ordered attempt sequence from p_init. Empty = unseen = p_init. */
export function bktReplay(attempts: readonly boolean[], params: BktParams = BKT_GLOBAL_PARAMS): number {
  let L = validateBktParams(params).p_init;
  for (const c of attempts) L = bktUpdate(L, c, params);
  return L;
}

/** Open item: same binarisation as practice-arena (process_score >= 0.6 is correct). */
export function bktObservationFromProcessScore(processScore: number): boolean {
  return processScore >= PRACTICE_SUCCESS_PROCESS_SCORE;
}

export type MasteryModel = 'ratio' | 'bkt';

/** MASTERY_MODEL flag; anything other than 'bkt' is the default 'ratio'. */
export function masteryModelFromEnv(env: Record<string, string | undefined> = process.env): MasteryModel {
  return env.MASTERY_MODEL === 'bkt' ? 'bkt' : 'ratio';
}

/**
 * Read-time per-atom mastery. 'ratio' is byte-identical to the pre-AS-51 formula
 * (learning-plan.ts fetchLearnerMastery). 'bkt' replays ordered attempts when they
 * exist and falls back to the ratio otherwise.
 */
export function atomMastery(
  row: { attempts: number; successes: number },
  model: MasteryModel,
  orderedAttempts?: readonly boolean[] | null,
): number {
  if (model === 'bkt' && orderedAttempts && orderedAttempts.length > 0) return bktReplay(orderedAttempts);
  return row.attempts > 0 ? row.successes / row.attempts : 0;
}

/** Adaptive difficulty direction for an atom (offline ADAPT proxy): >= 0.8 up, < p_init down. */
export function adaptDirection(mastery: number, threshold = 0.8, prior = BKT_GLOBAL_PARAMS.p_init): 'up' | 'hold' | 'down' {
  return mastery >= threshold ? 'up' : mastery < prior ? 'down' : 'hold';
}
