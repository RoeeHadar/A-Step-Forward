/**
 * ADR-0012 pressure-family intent + contract regression.
 */
import { describe, expect, it } from 'vitest';
import {
  buildTutorInteractionContract,
  classifyTutorChatIntent,
  isPressureFamilyIntent,
  wantsContextChallenge,
  wantsExamAnxietySupport,
  wantsPlanOwnership,
} from './learner-chat-intent';

describe('ADR-0012 pressure-family intents', () => {
  it('classifies anxiety / challenge / ownership / study-next', () => {
    expect(
      classifyTutorChatIntent('אני לחוץ ממש לפי הלוז, מרגיש שאני לא אהיה מוכן'),
    ).toBe('exam_anxiety');
    expect(classifyTutorChatIntent('אתה לא יודע מה המצב שלי? אתה המורה')).toBe(
      'context_challenge',
    );
    expect(
      classifyTutorChatIntent('יש לי כבר תוכנית — אתה מציע לשנות אותה?'),
    ).toBe('plan_ownership');
    expect(classifyTutorChatIntent('מה כדאי שאעבוד עליו עכשיו')).toBe('study_next');
  });

  it('detector helpers align', () => {
    expect(wantsExamAnxietySupport('אני לחוץ ממש')).toBe(true);
    expect(wantsContextChallenge('you should know my status')).toBe(true);
    expect(wantsPlanOwnership("I already have a plan, don't change my plan")).toBe(true);
  });

  it('marks pressure family intents', () => {
    for (const intent of [
      'exam_anxiety',
      'exam_readiness',
      'progress_status',
      'study_next',
      'context_challenge',
      'plan_ownership',
    ] as const) {
      expect(isPressureFamilyIntent(intent)).toBe(true);
    }
    expect(isPressureFamilyIntent('learn')).toBe(false);
    expect(isPressureFamilyIntent('recovery_simplify')).toBe(false);
  });

  it('contracts ban topic menus and plan rewrites under pressure', () => {
    const anxiety = buildTutorInteractionContract('exam_anxiety', 'he');
    expect(anxiety.allowTopicChecklist).toBe(false);
    expect(anxiety.injectCasualPlanChangeGuide).toBe(false);
    expect(anxiety.turnInstruction).toContain('4-beat');

    const challenge = buildTutorInteractionContract('context_challenge', 'he');
    expect(challenge.turnInstruction).toContain('CONTEXT CHALLENGE');
    expect(challenge.injectLearningPlanSnapshot).toBe(true);

    const ownership = buildTutorInteractionContract('plan_ownership', 'en');
    expect(ownership.turnInstruction).toContain('PLAN OWNERSHIP');
    expect(ownership.allowTopicChecklist).toBe(false);
  });
});
