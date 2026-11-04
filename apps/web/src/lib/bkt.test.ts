/** AS-51 (C5): the 10 unit tests of items/AS-44/asf-researcher.md §5 (tol 1e-4). */
import { describe, expect, it } from 'vitest';
import { BKT_GLOBAL_PARAMS, adaptDirection, atomMastery, bktObservationFromProcessScore, bktReplay, bktUpdate, masteryModelFromEnv } from './bkt';

const C = true, W = false;
const close = (x: number, want: number) => expect(Math.abs(x - want)).toBeLessThan(1e-4);

describe('AS-44 §5 BKT (p_init=0.2, p_learn=0.1, p_guess=0.2, p_slip=0.1)', () => {
  it('1. unseen atom -> p_init 0.2, not 0', () => { close(bktReplay([]), 0.2); expect(BKT_GLOBAL_PARAMS).toEqual({ p_init: 0.2, p_learn: 0.1, p_guess: 0.2, p_slip: 0.1 }); });
  it('2. [C] -> 0.57647', () => { close(bktReplay([C]), 0.57647); close(bktUpdate(0.2, C), 0.57647); });
  it('3. [W] -> 0.12727', () => close(bktReplay([W]), 0.12727));
  it('4. [C,C] -> 0.87368', () => close(bktReplay([C, C]), 0.87368));
  it('5. [C,W] -> 0.23086', () => close(bktReplay([C, W]), 0.23086));
  it('6. [W,W,W] -> 0.11454, stays > p_learn 0.1', () => { const x = bktReplay([W, W, W]); close(x, 0.11454); expect(x).toBeGreaterThan(0.1); });
  it('7. [C,C,C,C] -> 0.99427; crosses 0.8 after 2 correct', () => { close(bktReplay([C, C, C, C]), 0.99427); expect(bktReplay([C])).toBeLessThan(0.8); expect(bktReplay([C, C])).toBeGreaterThanOrEqual(0.8); });
  it('8. order sensitivity: [W,W,W,C,C,C] >= 0.8 and > ratio 0.5', () => {
    const seq = [W, W, W, C, C, C];
    const b = bktReplay(seq);
    expect(b).toBeGreaterThanOrEqual(0.8);
    expect(b).toBeGreaterThan(atomMastery({ attempts: 6, successes: 3 }, 'ratio'));
    expect(bktReplay([C, C, C, W, W, W])).toBeLessThan(b);
  });
  it('9. output always in [0,1]; G+S >= 1 throws', () => {
    for (const L of [-1, 0, 0.3, 1, 2]) for (const c of [C, W]) { const x = bktUpdate(L, c); expect(x).toBeGreaterThanOrEqual(0); expect(x).toBeLessThanOrEqual(1); }
    expect(() => bktUpdate(0.5, C, { p_init: 0.2, p_learn: 0.1, p_guess: 0.6, p_slip: 0.4 })).toThrow();
  });
  it('10. open item: process_score 0.59 -> wrong update, 0.6 -> correct (practice-arena threshold)', () => {
    expect(bktObservationFromProcessScore(0.59)).toBe(false);
    expect(bktObservationFromProcessScore(0.6)).toBe(true);
    close(bktUpdate(0.2, bktObservationFromProcessScore(0.59)), 0.12727);
    close(bktUpdate(0.2, bktObservationFromProcessScore(0.6)), 0.57647);
  });
});

describe('AS-51 flag + fallback', () => {
  it('MASTERY_MODEL defaults to ratio; only "bkt" turns it on', () => {
    expect(masteryModelFromEnv({})).toBe('ratio');
    expect(masteryModelFromEnv({ MASTERY_MODEL: 'BKT' })).toBe('ratio');
    expect(masteryModelFromEnv({ MASTERY_MODEL: 'bkt' })).toBe('bkt');
  });
  it('bkt replays ordered attempts when present, else ratio fallback; adapt direction', () => {
    expect(atomMastery({ attempts: 3, successes: 0 }, 'bkt', [W, W, W])).toBeCloseTo(0.11454, 4);
    expect(atomMastery({ attempts: 4, successes: 1 }, 'bkt', null)).toBe(0.25);
    expect(atomMastery({ attempts: 4, successes: 1 }, 'bkt', [])).toBe(0.25);
    expect(adaptDirection(bktReplay([W, W, W]))).toBe('down');
    expect(adaptDirection(bktReplay([C, C, C]))).toBe('up');
    expect(adaptDirection(bktReplay([]))).toBe('hold');
  });
});
