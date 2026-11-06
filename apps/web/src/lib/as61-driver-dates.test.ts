import { describe, expect, it } from 'vitest';
import { planHorizon } from './plan-capacity';
import { buildWeeklyPlanAbsenceBlock, formatLearnerFacingDate } from './learner-progress-briefing';
import { coachDaysUntilExam } from './coach-session-context';

// AS-61: neon 0.10.4 returns DATE columns (next_test_date / final_goal_date) as Date.
// These consumers previously called .slice / .trim on them and threw.
describe('AS-61 driver Date inputs', () => {
  const date = new Date('2027-06-01T00:00:00.000Z');
  it('planHorizon accepts Date and matches the string result', () => {
    const now = new Date('2026-11-04T00:00:00Z');
    expect(() => planHorizon({ next_test_date: date, final_goal_date: null, hours_per_week: 5 }, now)).not.toThrow();
    expect(planHorizon({ next_test_date: date, final_goal_date: null, hours_per_week: 5 }, now))
      .toEqual(planHorizon({ next_test_date: '2027-06-01', final_goal_date: null, hours_per_week: 5 }, now));
  });
  it('formatLearnerFacingDate accepts Date', () => {
    expect(formatLearnerFacingDate(date, 'en')).toBe(formatLearnerFacingDate('2027-06-01', 'en'));
  });
  it('buildWeeklyPlanAbsenceBlock accepts Date deadline', () => {
    expect(buildWeeklyPlanAbsenceBlock({ hasPlanRow: false, deadline: date })).toContain('deadline: 2027-06-01');
  });
  it('coachDaysUntilExam accepts Date', () => {
    expect(coachDaysUntilExam(date, null)).toBe(coachDaysUntilExam(date.toISOString(), null));
  });
});
