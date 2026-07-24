import { describe, expect, it } from 'vitest';
import {
  CHAT_CONTEXT,
  HEAD_GUARD_CHARS,
  buildPlanHeaderLine,
  fitSystemPrompt,
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

  it('buildPlanHeaderLine formats one-liner with goal, dates, weeks, concepts', () => {
    const line = buildPlanHeaderLine({
      goal: 'מתמטיקה לבגרות',
      start_date: '2026-07-01',
      end_date: '2026-09-01',
      weeks: [
        { concepts: [{ id: 'a' }, { id: 'b' }] },
        { concepts: [{ id: 'c' }] },
      ],
    });
    expect(line).toMatch(/^Plan: מתמטיקה לבגרות/);
    expect(line).toContain('2026-07-01 → 2026-09-01');
    expect(line).toContain('2 weeks');
    expect(line).toContain('3 concepts');
  });

  it('buildPlanHeaderLine handles null end_date and singular counts', () => {
    const line = buildPlanHeaderLine({
      goal: 'פיזיקה',
      start_date: '2026-08-01',
      end_date: null,
      weeks: [{ concepts: [{ id: 'x' }] }],
    });
    expect(line).toContain('→ open');
    expect(line).toContain('1 week ·');
    expect(line).toContain('1 concept');
    expect(line).not.toContain('weeks ');
    expect(line).not.toContain('concepts ');
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

describe('fitSystemPrompt — priority-aware trimming (Bug 1)', () => {
  const MAX = CHAT_CONTEXT.maxSystemChars; // 18 000

  it('returns prompt unchanged when within budget', () => {
    const s = 'a'.repeat(1000);
    expect(fitSystemPrompt(s)).toBe(s);
  });

  it('returns prompt + tail unchanged when both fit', () => {
    const s = 'a'.repeat(1000);
    const tail = '\n\nTAIL';
    expect(fitSystemPrompt(s, tail)).toBe(`${s}${tail}`);
  });

  it('trims middle not tail on overflow — head and tail markers both survive', () => {
    const HEAD_MARKER = 'HEAD_MARKER';
    const TAIL_MARKER = 'TAIL_MARKER';
    // Build a prompt that exceeds 18 k: head (11 k) + big middle + tail
    const head = `${HEAD_MARKER}${'h'.repeat(HEAD_GUARD_CHARS - HEAD_MARKER.length)}`;
    const bigMiddle = 'm'.repeat(MAX); // large middle
    const tail = `\n\n${TAIL_MARKER}`;
    const result = fitSystemPrompt(`${head}${bigMiddle}`, tail);

    expect(result.length).toBeLessThanOrEqual(MAX);
    expect(result.startsWith(HEAD_MARKER)).toBe(true);
    expect(result.endsWith(TAIL_MARKER)).toBe(true);
  });

  it('tail survives even when middle is entirely dropped', () => {
    const TAIL_MARKER = '## Response style (mandatory)\n- Be concise.';
    const head = 'H'.repeat(HEAD_GUARD_CHARS);
    const bigBody = head + 'm'.repeat(MAX); // way over budget
    const tail = `\n\n${TAIL_MARKER}`;
    const result = fitSystemPrompt(bigBody, tail);

    expect(result.length).toBeLessThanOrEqual(MAX);
    expect(result.endsWith(TAIL_MARKER)).toBe(true);
  });

  it('falls back gracefully without a tail arg (backward-compat)', () => {
    const over = 'x'.repeat(MAX + 500);
    const result = fitSystemPrompt(over);
    expect(result.length).toBeLessThanOrEqual(MAX + 200); // within trimming marker overhead
  });
});
