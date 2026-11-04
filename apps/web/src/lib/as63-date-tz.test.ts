import { afterAll, describe, expect, it } from 'vitest';
import { toIsoDateOnly, resolveGoalDeadlineIso } from './goal-track';
import { planHorizon } from './plan-capacity';
import { buildWeeklyPlanAbsenceBlock, formatLearnerFacingDate } from './learner-progress-briefing';

// AS-63: neon 0.10.4 parses a Postgres DATE '2026-11-04' to LOCAL midnight
// (verified offline: TZ=Asia/Jerusalem → 2026-11-03T22:00Z). Must stay 2026-11-04 in any TZ.
const ORIG_TZ = process.env.TZ;
afterAll(() => { process.env.TZ = ORIG_TZ; });

for (const tz of ['Asia/Jerusalem', 'America/Los_Angeles', 'UTC']) {
  describe(`DATE-only stays the same day under TZ=${tz}`, () => {
    it('toIsoDateOnly / consumers keep 2026-11-04', () => {
      process.env.TZ = tz;
      const driverDate = new Date(2026, 10, 4); // how the driver builds a DATE: local midnight
      expect(driverDate.getDate()).toBe(4);
      if (tz === 'Asia/Jerusalem') expect(driverDate.toISOString().slice(0, 10)).toBe('2026-11-03'); // the old bug
      expect(toIsoDateOnly(driverDate)).toBe('2026-11-04');
      expect(resolveGoalDeadlineIso(driverDate, null)).toBe('2026-11-04');
      expect(buildWeeklyPlanAbsenceBlock({ hasPlanRow: false, deadline: driverDate })).toContain('deadline: 2026-11-04');
      expect(formatLearnerFacingDate(driverDate, 'en')).toBe('November 4, 2026');
      const now = new Date(2026, 9, 1);
      expect(planHorizon({ next_test_date: driverDate, final_goal_date: null, hours_per_week: 5 }, now))
        .toEqual(planHorizon({ next_test_date: '2026-11-04', final_goal_date: null, hours_per_week: 5 }, now));
    });
  });
}
