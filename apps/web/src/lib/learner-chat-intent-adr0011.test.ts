/**
 * ADR-0011 intent + contract regression — isolated from neon/plan imports.
 */
import { describe, expect, it } from 'vitest';
import {
  buildTutorInteractionContract,
  classifyTutorChatIntent,
  looksLikeLearnerQuestion,
  wantsExamReadinessAnswer,
  wantsExpandedOutputBudget,
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
});
