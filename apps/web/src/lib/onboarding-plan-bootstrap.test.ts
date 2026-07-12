import { describe, expect, it } from 'vitest';
import { deriveOnboardingSeedScores } from './onboarding-self-score';

/**
 * Mirrors onboarding-plan-bootstrap chunking — keep in sync.
 * (Bootstrap module is server-only; test the contract here.)
 */
function chunkWeeks(concepts: string[], weeks = 2, perWeek = 4): string[][] {
  const limited = concepts.slice(0, weeks * perWeek);
  const groups: string[][] = Array.from({ length: weeks }, () => []);
  for (let i = 0; i < limited.length; i += 1) {
    const idx = Math.min(weeks - 1, Math.floor(i / perWeek));
    groups[idx]!.push(limited[i]!);
  }
  if (groups[0]!.length === 0 && limited[0]) groups[0]!.push(limited[0]);
  if (groups[1]!.length === 0 && groups[0]!.length > 0) {
    groups[1] = groups[0]!.slice(0, perWeek);
  }
  return groups;
}

describe('onboarding plan bootstrap contract', () => {
  it('always yields two non-empty weeks from goal seeds', () => {
    const scores = deriveOnboardingSeedScores({
      goal: 'bagrut_math_5',
      subjects: ['math'],
      grade_level: '12',
      points_group: '5',
      personality_profile: { goal_key: 'bagrut_math_5' },
    });
    const ids = Object.keys(scores);
    expect(ids.length).toBeGreaterThan(0);
    const weeks = chunkWeeks(ids);
    expect(weeks).toHaveLength(2);
    expect(weeks[0]!.length).toBeGreaterThan(0);
    expect(weeks[1]!.length).toBeGreaterThan(0);
    expect(weeks[0]!.length + weeks[1]!.length).toBeLessThanOrEqual(8);
  });
});
