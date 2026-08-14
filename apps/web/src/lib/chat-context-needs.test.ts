import { describe, expect, it } from 'vitest';
import { buildContextNeeds } from './chat-context-needs';
import { classifyTutorChatIntent } from './learner-chat-intent';

describe('chat-context-needs (ADR-0015)', () => {
  it('math teach turn skips status / active week / xp', () => {
    const needs = buildContextNeeds({
      agent: 'tutor',
      message: 'מה החסר אם הממוצע של 5 מספרים הוא 10 וארבעה הם 8,9,11,12?',
    });
    expect(needs.intent).not.toBe('exam_anxiety');
    expect(needs.statusPack).toBe(false);
    expect(needs.activeWeek).toBe(false);
    expect(needs.xp).toBe(false);
    expect(needs.profile).toBe(false);
    expect(needs.mastery).toBe(false);
    expect(needs.curriculumHints).toBe(true);
    expect(needs.hybridTools).toBe(true);
    expect(needs.durableMemory).toBe(true);
  });

  it('status ask enables briefing packs for tutor', () => {
    const needs = buildContextNeeds({
      agent: 'tutor',
      message: 'מה הסטטוס הנוכחי שלי בתוכנית?',
    });
    expect(needs.statusPack).toBe(true);
    expect(needs.bilingualBriefing).toBe(true);
    expect(needs.profile).toBe(true);
  });

  it('recall, pace-vs-goal, and memory-challenge inject status packs', () => {
    const recall = buildContextNeeds({ agent: 'tutor', message: 'מה אתה יודע עליי' });
    expect(recall.intent).toBe('progress_status');
    expect(recall.statusPack).toBe(true);
    expect(recall.profile).toBe(true);
    expect(recall.mastery).toBe(true);

    const pace = buildContextNeeds({
      agent: 'tutor',
      message:
        'יש לי יעד באתר. אני רוצה לדעת איך ההתקדמות שלי לקראת היעד הזה יחסית לקצב ההתקדמות הנוכחי שלי',
    });
    expect(pace.intent).toBe('progress_status');
    expect(pace.statusPack).toBe(true);
    expect(pace.profile).toBe(true);

    const memory = buildContextNeeds({
      agent: 'tutor',
      message: 'אני רוצה שאתה תגיד לי, יש לך את המידע הזה בזיכרון שלך, לא?',
    });
    expect(memory.intent).toBe('context_challenge');
    expect(memory.statusPack).toBe(true);
    expect(memory.profile).toBe(true);

    const workPlan = buildContextNeeds({
      agent: 'tutor',
      message:
        'יש לי תוכנית עבודה שניתנה לי באתר פה. אני רוצה לדעת מהי ואיפה אני עומד בהתקדמות שלי ביחס אליה',
    });
    expect(workPlan.intent).toBe('progress_status');
    expect(workPlan.statusPack).toBe(true);
    expect(workPlan.activeWeek).toBe(true);
  });

  it('mentor keeps active week; coach keeps drills', () => {
    const mentor = buildContextNeeds({ agent: 'mentor', message: 'איך אני מרגיש לגבי הלמידה?' });
    expect(mentor.activeWeek).toBe(true);
    expect(mentor.xp).toBe(true);

    const coach = buildContextNeeds({ agent: 'coach', message: 'תן לי תרגיל קצר' });
    expect(coach.activeWeek).toBe(true);
    expect(coach.hybridTools).toBe(true);
    expect(coach.mastery).toBe(true);
  });

  it('minimal mode strips optional packs', () => {
    const needs = buildContextNeeds({
      agent: 'tutor',
      message: 'מה הסטטוס?',
      minimal: true,
    });
    expect(needs.statusPack).toBe(false);
    expect(needs.durableMemory).toBe(false);
    expect(needs.hybridTools).toBe(false);
  });

  it('מה החסר math stem is not exam_anxiety', () => {
    expect(classifyTutorChatIntent('מה החסר בממוצע של חמישה מספרים?')).toBe('learn');
    expect(classifyTutorChatIntent('פתור את המשוואה צעד אחר צעד')).toMatch(
      /worked_solution|learn/,
    );
  });
});
