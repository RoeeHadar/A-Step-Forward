import { describe, expect, it } from 'vitest';
import {
  buildCoachDifficultyInstruction,
  buildCoachExamPrepBlock,
  detectCoachDifficultySignal,
  filterDueReviewsForProfile,
  pickCoachPlannerGoal,
} from './coach-session-context';
import type { LearningPlan } from '@asf/schemas/learning_path';
import type { DueReviewItem } from './neon-db';

const dueItem = (concept_id: string, subjectLabel: string): DueReviewItem => ({
  atom_id: `${concept_id}_atom`,
  concept_id,
  concept_name: subjectLabel,
  concept_name_he: null,
  last_score: 0.3,
  times_practiced: 2,
});

describe('filterDueReviewsForProfile', () => {
  it('drops math due items for physics-only profile', () => {
    const items = [
      dueItem('equations_linear', 'Linear equations'),
      dueItem('kinematics_1d', 'Kinematics 1D'),
    ];
    const filtered = filterDueReviewsForProfile(items, { subjects: ['physics', 'bagrut_physics'] });
    expect(filtered.map((i) => i.concept_id)).toEqual(['kinematics_1d']);
  });

  it('keeps items in plan scope when plan ids provided', () => {
    const items = [
      dueItem('kinematics_1d', 'Kinematics'),
      dueItem('newton_laws', 'Newton'),
    ];
    const filtered = filterDueReviewsForProfile(items, {
      subjects: ['physics'],
      planConceptIds: new Set(['newton_laws', 'forces']),
    });
    expect(filtered.map((i) => i.concept_id)).toEqual(['newton_laws']);
  });
});

describe('detectCoachDifficultySignal', () => {
  it('detects Hebrew too-easy frustration', () => {
    expect(detectCoachDifficultySignal('5 מטר לשניה, זה קל לי מידי')).toBe('too_easy');
  });

  it('detects explicit harder request', () => {
    expect(detectCoachDifficultySignal('5 מטר לשניה, אתה לא עומד להקשות עליי?')).toBe('harder');
  });
});

describe('pickCoachPlannerGoal', () => {
  it('prefers goal_key concept during exam cram', () => {
    const goal = pickCoachPlannerGoal({
      relatedConceptId: null,
      topicInKg: false,
      currentPlan: {
        id: 'p1',
        goal: 'physics',
        start_date: '2026-07-01',
        weeks: [
          {
            id: 'w1',
            plan_id: 'p1',
            week_number: 1,
            status: 'active',
            concepts: [
              { concept_id: 'kinematics_1d', name: 'Kinematics', subject: 'physics', suggested_sections: [], recommended_bagrut: [] },
              { concept_id: 'forces', name: 'Forces', subject: 'physics', suggested_sections: [], recommended_bagrut: [] },
            ],
          },
        ],
      } as unknown as LearningPlan,
      weakConcepts: [],
      goalKey: 'bagrut_physics',
      daysUntilExam: 6,
    });
    expect(goal).toBe('newton_laws');
  });

  it('uses first active-week concept outside exam window', () => {
    const goal = pickCoachPlannerGoal({
      relatedConceptId: null,
      topicInKg: false,
      currentPlan: {
        id: 'p1',
        goal: 'physics',
        start_date: '2026-07-01',
        weeks: [
          {
            id: 'w1',
            plan_id: 'p1',
            week_number: 1,
            status: 'active',
            concepts: [
              { concept_id: 'kinematics_1d', name: 'Kinematics', subject: 'physics', suggested_sections: [], recommended_bagrut: [] },
              { concept_id: 'forces', name: 'Forces', subject: 'physics', suggested_sections: [], recommended_bagrut: [] },
            ],
          },
        ],
      } as unknown as LearningPlan,
      weakConcepts: [],
      goalKey: 'bagrut_physics',
      daysUntilExam: null,
    });
    expect(goal).toBe('kinematics_1d');
  });
});

describe('buildCoachExamPrepBlock', () => {
  it('includes exam cram guidance', () => {
    const block = buildCoachExamPrepBlock({
      daysLeft: 6,
      testName: 'מכניקה',
      quickMode: true,
      quickDuration: '15',
      locale: 'he',
    });
    expect(block).toContain('Exam preparation mode');
    expect(block).toContain('Bagrut-style');
  });
});

describe('buildCoachDifficultyInstruction', () => {
  it('returns Hebrew authority block for too_easy', () => {
    const block = buildCoachDifficultyInstruction('too_easy', 'he');
    expect(block).toContain('הוראת תור');
    expect(block).toContain('קלים מדי');
  });
});
