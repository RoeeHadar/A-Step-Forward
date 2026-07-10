import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  maybeRefreshLearningPlanForSignals,
  syncWellbeingBiasForLearner,
} from './adaptive-plan-refresh';

const mockGetProfile = vi.fn();
const mockGetMastery = vi.fn();
const mockGetPlan = vi.fn();
const mockGenerate = vi.fn();
const mockSaveBias = vi.fn();
const mockEvaluate = vi.fn();
const mockCanPersist = vi.fn();
const mockDetectShock = vi.fn();
const mockPickTrigger = vi.fn();

vi.mock('./neon-db', () => ({
  getLearnerProfile: (...args: unknown[]) => mockGetProfile(...args),
  getConceptMastery: (...args: unknown[]) => mockGetMastery(...args),
  getCurrentPlan: (...args: unknown[]) => mockGetPlan(...args),
  generateLearningPlan: (...args: unknown[]) => mockGenerate(...args),
  saveWellbeingPlanBias: (...args: unknown[]) => mockSaveBias(...args),
}));

vi.mock('./wellbeing-plan-bias', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./wellbeing-plan-bias')>();
  return {
    ...actual,
    evaluateWellbeingSignals: (...args: unknown[]) => mockEvaluate(...args),
    canPersistWellbeingRewrite: (...args: unknown[]) => mockCanPersist(...args),
    detectMasteryShock: (...args: unknown[]) => mockDetectShock(...args),
    pickPrimaryWellbeingTrigger: (...args: unknown[]) => mockPickTrigger(...args),
    wellbeingPlanBiasFromProfile: actual.wellbeingPlanBiasFromProfile,
  };
});

const profile = {
  learner_id: 'u1',
  goal: 'Bagrut',
  grade_level: null,
  points_group: '5pt',
  subjects: ['math'],
  hours_per_week: 5,
  preferred_style: null,
  attention_span: null,
  self_scores: null,
  background_notes: null,
  next_test_date: null,
  final_goal_date: null,
  mental_state: { anxiety: 8 },
  personality_profile: {},
  weak_concepts: null,
  strong_concepts: null,
  wellbeing_plan_bias: null,
  created_at: '',
  updated_at: '',
};

describe('syncWellbeingBiasForLearner', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetProfile.mockResolvedValue(profile);
    mockGetMastery.mockResolvedValue({});
    mockEvaluate.mockReturnValue({
      bias: { active: true, trigger: 'profile_anxiety' },
      triggers: ['profile_anxiety'],
    });
  });

  it('saves evaluated bias', async () => {
    await syncWellbeingBiasForLearner('u1');
    expect(mockSaveBias).toHaveBeenCalled();
  });
});

describe('maybeRefreshLearningPlanForSignals', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetProfile.mockResolvedValue(profile);
    mockGetMastery.mockResolvedValue({ limits: 0.2 });
    mockGetPlan.mockResolvedValue({ id: 'plan-1', weeks: [] });
    mockEvaluate.mockReturnValue({
      bias: { active: true, trigger: 'mastery_shock', mastery_snapshot: { limits: 0.5 } },
      triggers: ['mastery_shock', 'profile_anxiety'],
    });
    mockPickTrigger.mockReturnValue('mastery_shock');
    mockCanPersist.mockReturnValue(true);
    mockDetectShock.mockReturnValue(true);
  });

  it('regenerates plan on mastery shock when allowed', async () => {
    const result = await maybeRefreshLearningPlanForSignals('u1', 'mastery_update');
    expect(result.refreshed).toBe(true);
    expect(mockGenerate).toHaveBeenCalledWith('u1');
  });

  it('skips regen when no active plan', async () => {
    mockGetPlan.mockResolvedValue(null);
    const result = await maybeRefreshLearningPlanForSignals('u1', 'mastery_update');
    expect(result.refreshed).toBe(false);
    expect(mockGenerate).not.toHaveBeenCalled();
  });

  it('skips mastery regen when shock not detected', async () => {
    mockDetectShock.mockReturnValue(false);
    const result = await maybeRefreshLearningPlanForSignals('u1', 'mastery_update');
    expect(result.refreshed).toBe(false);
  });

  it('blocks third wellbeing rewrite when cooldown denies', async () => {
    mockPickTrigger.mockReturnValue('profile_anxiety');
    mockEvaluate.mockReturnValue({
      bias: { active: true, trigger: 'profile_anxiety' },
      triggers: ['profile_anxiety'],
    });
    mockCanPersist.mockReturnValue(false);
    const result = await maybeRefreshLearningPlanForSignals('u1', 'profile_mental_state');
    expect(result.refreshed).toBe(false);
    expect(mockSaveBias).toHaveBeenCalled();
  });
});
