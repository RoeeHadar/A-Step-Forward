/** AS-52 (C3b): note-writing prompts instruct typed-fact key/valid_to + evidence_note_ids; legacy tags still read. */
import { describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));
const appended: Array<Record<string, unknown>> = [];
vi.mock('@/lib/neon-db', () => ({ appendAgentNote: vi.fn(async (_l: string, _a: string, n: Record<string, unknown>) => { appended.push(n); }) }));

import { AGENT_METHOD_SPECS, buildAgentSkillsPrompt } from './agent-skills';
import { applyMemoryTagsFromAssistant } from './chat-memory-persist';
import { decodeFactContent, factDisplayText, keepCurrentFacts } from './typed-facts';

describe('AS-52 prompt wording', () => {
  for (const agent of ['tutor', 'mentor', 'coach', 'reviewer'] as const) {
    it(`${agent}: shared skills tell typed notes to carry key + valid_to and supersede by kind+key`, () => {
      const p = buildAgentSkillsPrompt(agent);
      expect(p).toContain('Typed facts (goal / preference / state=affect / misconception)');
      expect(p).toContain('"key"');
      expect(p).toContain('"valid_to"');
      expect(p).toContain('{"kind":"goal","key":"bagrut_math"');
      expect(p).toContain('same kind+key to replace an older fact');
    });
  }
  it('mentor method asks for evidence_note_ids in propose_plan_change', () => {
    expect(AGENT_METHOD_SPECS.mentor).toContain('`evidence_note_ids` in propose_plan_change');
  });
});

describe('AS-52 legacy untyped notes still parse and read', () => {
  it('legacy goal tag without key is stored untyped (no fact) and displays as-is', async () => {
    appended.length = 0;
    const n = await applyMemoryTagsFromAssistant('L', 'mentor', 'ok [[ASF_MEMORY_NOTE:{"kind":"goal","content":"wants a 90 in Bagrut","importance":3}]]', { now: new Date('2026-01-05T00:00:00Z') });
    expect(n).toBe(1);
    expect(appended[0]).toMatchObject({ kind: 'goal', content: 'wants a 90 in Bagrut' });
    expect(appended[0]!.fact).toBeUndefined();
    expect(decodeFactContent('wants a 90 in Bagrut')).toEqual({ text: 'wants a 90 in Bagrut', meta: null });
    expect(factDisplayText('learner prefers short hints')).toBe('learner prefers short hints');
    const legacy = [{ kind: 'goal', content: 'wants a 90 in Bagrut', created_at: '2025-01-01' }, { kind: 'observation', content: 'x', created_at: null }];
    expect(keepCurrentFacts(legacy, new Date('2026-01-05T00:00:00Z'))).toHaveLength(2);
  });
  it('instructed-format goal tag yields a keyed fact', async () => {
    appended.length = 0;
    await applyMemoryTagsFromAssistant('L', 'mentor', '[[ASF_MEMORY_NOTE:{"kind":"goal","key":"bagrut_math","content":"exam in 2 weeks","valid_to":null}]]', { now: new Date('2026-01-05T00:00:00Z') });
    expect(appended[0]!.fact).toEqual({ key: 'bagrut_math', valid_to: null });
  });
});
