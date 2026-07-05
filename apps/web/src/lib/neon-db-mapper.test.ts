import { describe, expect, it } from 'vitest';
import {
  isNeonLockContention,
  learnerAdvisoryLockKey,
  mapDashboardSnapshotToLearnerDashboard,
  type DashboardSnapshot,
} from './neon-db';

describe('learnerAdvisoryLockKey', () => {
  it('scopes lock keys by operation and learner', () => {
    expect(learnerAdvisoryLockKey('plan-gen', 'user_abc')).toBe('plan-gen:user_abc');
    expect(learnerAdvisoryLockKey('consolidate', 'user_abc')).toBe('consolidate:user_abc');
  });
});

describe('isNeonLockContention', () => {
  it('detects lock-busy errors by message code', () => {
    expect(isNeonLockContention(new Error('plan_update_in_progress'), 'plan_update_in_progress')).toBe(
      true,
    );
    expect(isNeonLockContention(new Error('other failure'), 'plan_update_in_progress')).toBe(false);
    expect(isNeonLockContention('plan_update_in_progress', 'plan_update_in_progress')).toBe(false);
  });
});

describe('mapDashboardSnapshotToLearnerDashboard', () => {
  const snapshot: DashboardSnapshot = {
    stats: { streak_days: 3, lessons_completed: 2, level: 2 },
    recent_lessons: [
      {
        id: null,
        concept_id: 'limits',
        title: 'Limits',
        title_he: 'גבולות',
        subject: 'math',
        progress: 0.55,
        est_minutes: null,
        last_activity: '2026-07-01T12:00:00.000Z',
      },
      {
        id: 'lesson-uuid',
        concept_id: 'derivatives',
        title: 'Derivatives',
        title_he: null,
        subject: 'math',
        progress: 0.8,
        est_minutes: 35,
        last_activity: '2026-07-02T09:30:00.000Z',
      },
    ],
    mastery_summary: [
      {
        concept_id: 'derivatives',
        name: 'Derivatives',
        name_he: 'נגזרות',
        score: 0.8,
      },
    ],
  };

  it('maps snapshot fields to legacy /api/dashboard JSON shape', () => {
    const out = mapDashboardSnapshotToLearnerDashboard(snapshot);
    expect(out.recent_lessons).toHaveLength(2);
    expect(out.recent_lessons[0]).toEqual({
      id: 'limits',
      title: 'Limits',
      progress: 0.55,
      last_accessed_at: '2026-07-01T12:00:00.000Z',
      est_minutes: 20,
    });
    expect(out.recent_lessons[1]?.est_minutes).toBe(35);
    expect(out.mastery_summary).toEqual([
      { concept_id: 'derivatives', concept_name: 'Derivatives', score: 0.8 },
    ]);
  });
});
