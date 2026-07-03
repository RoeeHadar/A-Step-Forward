import { describe, expect, it } from 'vitest';
import { examPrepContext, daysUntilIsoDate, isWithinExamPrepWindow } from './exam-prep';
import type { LearningPlan } from '@asf/schemas/learning_path';

describe('exam-prep', () => {
  it('detects exam prep window within 14 days', () => {
    const d = new Date();
    d.setDate(d.getDate() + 5);
    const iso = d.toISOString().slice(0, 10);
    expect(isWithinExamPrepWindow(daysUntilIsoDate(iso))).toBe(true);
  });

  it('hides banner when goal is far away', () => {
    const d = new Date();
    d.setDate(d.getDate() + 60);
    const iso = d.toISOString().slice(0, 10);
    expect(examPrepContext(null, iso, null)).toBeNull();
  });

  it('returns quiz links when plan and near test exist', () => {
    const d = new Date();
    d.setDate(d.getDate() + 6);
    const iso = d.toISOString().slice(0, 10);
    const plan = {
      id: 'plan-1',
      goal: 'מבחן',
      weeks: [
        {
          id: 'week-1',
          week_number: 1,
          status: 'active',
          concepts: [],
        },
      ],
    } as unknown as LearningPlan;
    const ctx = examPrepContext(plan, iso, null);
    expect(ctx?.show).toBe(true);
    expect(ctx?.weekId).toBe('week-1');
    expect(ctx?.planId).toBe('plan-1');
  });
});
