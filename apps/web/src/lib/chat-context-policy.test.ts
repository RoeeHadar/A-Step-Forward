import { describe, expect, it } from 'vitest';
import {
  CHAT_CONTEXT,
  compactMemoryTurns,
  compactStoredTurnContent,
  formatPlanWeeksCompact,
  wantsConversationAdvance,
  wantsExamReadinessAnswer,
  wantsLearningPlanSnapshot,
} from './chat-context-policy';

describe('chat-context-policy', () => {
  it('compactMemoryTurns respects char budget', () => {
    const turns = Array.from({ length: 6 }, () => ({
      role: 'user' as const,
      content: 'x'.repeat(1200),
    }));
    const out = compactMemoryTurns(turns);
    const total = out.reduce((n, t) => n + t.content.length, 0);
    expect(out.length).toBeLessThanOrEqual(CHAT_CONTEXT.maxMemoryTurns);
    expect(total).toBeLessThanOrEqual(CHAT_CONTEXT.maxMemoryCharsTotal);
  });

  it('stores short marker for error fallbacks', () => {
    const stored = compactStoredTurnContent(
      '**מה קרה:**\nהבקשה גדולה',
      'assistant',
      'he',
    );
    expect(stored).toContain('שירות המודל');
    expect(stored.length).toBeLessThan(80);
  });

  it('formatPlanWeeksCompact shows active week only in minimal mode', () => {
    const text = formatPlanWeeksCompact(
      [
        {
          week_number: 1,
          status: 'completed',
          concepts: [{ concept_id: 'a', name: 'A' }],
        },
        {
          week_number: 2,
          status: 'active',
          concepts: [{ concept_id: 'b', name: 'B', name_he: 'ב' }],
        },
        {
          week_number: 3,
          status: 'upcoming',
          concepts: [{ concept_id: 'c', name: 'C' }],
        },
      ],
      'minimal',
    );
    expect(text).toContain('Week 2');
    expect(text).not.toContain('Week 3');
  });

  it('detects study-next questions', () => {
    expect(wantsLearningPlanSnapshot('מה ללמוד הלאה?')).toBe(true);
    expect(wantsLearningPlanSnapshot('הבגרות שלי עוד שבוע')).toBe(false);
  });

  it('detects exam readiness questions', () => {
    expect(
      wantsExamReadinessAnswer(
        'הבגרות שלי עוד שבוע, האם התוכנית אכן תכין אותי בזמן למבחן?',
      ),
    ).toBe(true);
    expect(wantsExamReadinessAnswer('מה ללמוד הלאה?')).toBe(false);
  });

  it('detects conversation advance frustration', () => {
    expect(wantsConversationAdvance('כתבת את זה כבר, תמשיך')).toBe(true);
    expect(wantsConversationAdvance('כן אני יודע את הנושאים')).toBe(false);
  });

  it('detects bagrut odds as exam readiness', () => {
    expect(
      wantsExamReadinessAnswer('איך אתה חושב שיהיה לי בבגרות אם אמשיך בקצב הזה'),
    ).toBe(true);
  });

  it('resolveChatMaxTokens raises budget for worked / continue turns', async () => {
    const { resolveChatMaxTokens, truncationContinueNotice } = await import(
      './chat-context-policy'
    );
    expect(resolveChatMaxTokens({})).toBe(CHAT_CONTEXT.maxOutputTokens);
    expect(
      resolveChatMaxTokens({ wantsWorkedSolution: true }),
    ).toBe(CHAT_CONTEXT.maxOutputTokensWorked);
    expect(truncationContinueNotice('he')).toContain('המשך');
    expect(truncationContinueNotice('en')).toContain('continue');
  });
});
