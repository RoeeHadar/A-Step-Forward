import { describe, expect, it } from 'vitest';
import { buildContextNeeds, returningGap, RETURNING_GAP_DAYS } from './chat-context-needs';
import { buildHandoffDigest } from './agent-handoff-digest';

// AS-40 / AS-32 §3 C1: Mentor reads the handoff digest only on status + returning turns.
describe('AS-40 mentor handoff-digest gate', () => {
  it('mentor + status turn → handoffDigest true; mentor + math turn → false', () => {
    expect(buildContextNeeds({ agent: 'mentor', message: 'how am I doing?' }).handoffDigest).toBe(true);
    expect(buildContextNeeds({ agent: 'mentor', message: 'what is the derivative of cos x?' }).handoffDigest).toBe(false);
    // tutor/coach behaviour unchanged
    expect(buildContextNeeds({ agent: 'tutor', message: 'what is the derivative of cos x?' }).handoffDigest).toBe(false);
    expect(buildContextNeeds({ agent: 'coach', message: 'what is the derivative of cos x?' }).handoffDigest).toBe(true);
    expect(buildContextNeeds({ agent: 'tutor', message: 'how am I doing?' }).handoffDigest).toBe(false);
  });

  it('returningGap: >=3 days since last activity → mentor digest on a non-status turn', () => {
    const now = new Date('2026-11-04T10:00:00Z');
    expect(RETURNING_GAP_DAYS).toBe(3);
    expect(returningGap(['2026-10-23T10:00:00Z'], now)).toBe(true); // 12 days
    expect(returningGap(['2026-11-01T10:00:00Z'], now)).toBe(true); // exactly 3
    expect(returningGap(['2026-10-20T00:00:00Z', '2026-11-02T10:00:00Z'], now)).toBe(false); // latest wins
    expect(returningGap([], now)).toBe(false);
    expect(returningGap([null, 'garbage'], now)).toBe(false);
    const msg = 'what is the derivative of cos x?';
    expect(buildContextNeeds({ agent: 'mentor', message: msg, returningGap: true }).handoffDigest).toBe(true);
    expect(buildContextNeeds({ agent: 'tutor', message: msg, returningGap: true }).handoffDigest).toBe(false);
    expect(buildContextNeeds({ agent: 'mentor', message: msg, returningGap: true, minimal: true }).handoffDigest).toBe(false);
  });

  it('mentor digest excludes own notes and stays <=400 tokens worst case', () => {
    const long = 'הלומד מתבלבל בסימן של נגזרת sin ו-cos '.repeat(20);
    const notes = (['tutor', 'coach', 'reviewer', 'mentor'] as const).flatMap((agent) =>
      Array.from({ length: 4 }, (_, i) => ({ agent, kind: 'observation', content: `${agent}-${i} ${long}`, importance: 5 })),
    );
    const d = buildHandoffDigest({ readingAgent: 'mentor', notes });
    expect(d).not.toContain('mentor-');
    // Method: conservative 1 token / 2 chars (Hebrew-heavy worst case); chars/4 is the usual EN estimate.
    const tokensConservative = Math.ceil(d.length / 2);
    expect(tokensConservative).toBeLessThanOrEqual(400);
    console.log(`[AS40] digest chars=${d.length} tokens_chars/4=${Math.ceil(d.length / 4)} tokens_chars/2=${tokensConservative}`);
  });
});
