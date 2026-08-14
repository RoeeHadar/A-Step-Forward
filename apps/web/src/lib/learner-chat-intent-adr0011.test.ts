/**
 * ADR-0011 intent + contract regression — isolated from neon/plan imports.
 */
import { describe, expect, it } from 'vitest';
import {
  buildTutorInteractionContract,
  classifyTutorChatIntent,
  looksLikeLearnerQuestion,
  shouldApplyLearnerPreferenceOverride,
  wantsExamReadinessAnswer,
  wantsExpandedOutputBudget,
  wantsLearnerRecall,
  wantsProgressStatus,
  wantsRecoverySimplify,
  wantsWorkedSolution,
} from './learner-chat-intent';

describe('ADR-0011 learner-chat-intent', () => {
  it('classifies communication transcript intents', () => {
    expect(
      classifyTutorChatIntent('מה הסטטוס שלי בהקשר של התוכנית לימוד'),
    ).toBe('progress_status');
    expect(wantsProgressStatus('מה הסטטוס שלי בהקשר של התוכנית לימוד')).toBe(true);
    expect(
      classifyTutorChatIntent('איך אתה חושב שיהיה לי בבגרות אם אמשיך בקצב הזה'),
    ).toBe('exam_readiness');
    expect(
      classifyTutorChatIntent(
        'האם היית ממליץ לי ללמוד עוד חומר מעבר לחומר המומלץ כרגע?',
      ),
    ).toBe('learn');
    expect(
      classifyTutorChatIntent('תסביר לי איך לפתור את האינטגרל בצורה יותר פשוטה בבקשה'),
    ).toBe('recovery_simplify');
    expect(
      classifyTutorChatIntent('זה נראה לי ממש מסובך, אני צריך להכיר את זה?'),
    ).toBe('recovery_simplify');
    expect(
      classifyTutorChatIntent('פתור את התרגיל כדי שאבין, תן לי את השלבים'),
    ).toBe('worked_solution');
    expect(
      classifyTutorChatIntent('המשך, התגובה שלך נעצרה באמצע'),
    ).toBe('conversation_advance');
  });

  it('detector helpers align with classifier', () => {
    expect(wantsProgressStatus('מה הסטטוס הנוכחי שלי')).toBe(true);
    expect(wantsExamReadinessAnswer('איך אתה חושב שיהיה לי בבגרות')).toBe(true);
    expect(wantsRecoverySimplify('זה מסובך מדי')).toBe(true);
    expect(wantsWorkedSolution('תן לי את השלבים')).toBe(true);
    expect(wantsExpandedOutputBudget('המשך מהמקום שעצרת')).toBe(true);
  });

  it('progress_status and recovery contracts force direct modes', () => {
    const status = buildTutorInteractionContract('progress_status', 'he');
    expect(status.allowSocraticOpening).toBe(false);
    expect(status.turnInstruction).toContain('PROGRESS STATUS');

    const recovery = buildTutorInteractionContract('recovery_simplify', 'en');
    expect(recovery.allowSocraticOpening).toBe(false);
    expect(recovery.injectLearningPlanSnapshot).toBe(true);
    expect(recovery.turnInstruction).toContain('RECOVERY');

    const worked = buildTutorInteractionContract('worked_solution', 'he');
    expect(worked.turnInstruction).toContain('WORKED SOLUTION');
  });

  it('Hebrew status asks look like questions without ASCII word boundaries', () => {
    expect(looksLikeLearnerQuestion('מה הסטטוס שלי בהקשר של התוכנית לימוד')).toBe(
      true,
    );
    expect(looksLikeLearnerQuestion('אני רוצה לשנות את התוכנית שלי')).toBe(false);
  });

  it('classifies the live status/memory transcript (Aug 2026)', () => {
    expect(classifyTutorChatIntent('מה הסטטוס הנוכחי שלי')).toBe('progress_status');
    expect(wantsProgressStatus('מה הסטטוס הנוכחי שלי')).toBe(true);

    expect(classifyTutorChatIntent('מה אתה יודע עליי')).toBe('progress_status');
    expect(wantsLearnerRecall('מה אתה יודע עליי')).toBe(true);
    expect(wantsProgressStatus('מה אתה יודע עליי')).toBe(true);

    expect(classifyTutorChatIntent('מה הסטטוס התקדמות שלי לקראת המטרה')).toBe(
      'progress_status',
    );

    const paceVsGoal =
      'יש לי יעד באתר. אני רוצה לדעת איך ההתקדמות שלי לקראת היעד הזה יחסית לקצב ההתקדמות הנוכחי שלי';
    expect(classifyTutorChatIntent(paceVsGoal)).toBe('progress_status');
    expect(wantsProgressStatus(paceVsGoal)).toBe(true);

    const workPlan =
      'יש לי תוכנית עבודה שניתנה לי באתר פה. אני רוצה לדעת מהי ואיפה אני עומד בהתקדמות שלי ביחס אליה';
    expect(classifyTutorChatIntent(workPlan)).toBe('progress_status');
    expect(
      classifyTutorChatIntent(
        'מה עשיתי עד כה, מה השיעורים שסיימתי, מה עוד יש לי לעשות ואיך אני מבחינת ההתקדמות שלי',
      ),
    ).toBe('progress_status');
  });

  it('keeps Direct status override when ReAct is killed', () => {
    expect(
      shouldApplyLearnerPreferenceOverride({
        intent: 'progress_status',
        planChangeFlow: false,
        reactEnabled: false,
      }),
    ).toBe(true);
    expect(
      shouldApplyLearnerPreferenceOverride({
        intent: 'casual_plan_change',
        planChangeFlow: false,
        reactEnabled: false,
      }),
    ).toBe(false);
    expect(
      shouldApplyLearnerPreferenceOverride({
        intent: 'casual_plan_change',
        planChangeFlow: false,
        reactEnabled: true,
      }),
    ).toBe(true);
  });
});
