/**
 * Unit tests for applyMemoryTagsFromAssistant (note-parser hardening).
 * All DB calls are mocked so no network required.
 */
import { describe, expect, it, vi, beforeEach } from 'vitest';

// Mock server-only guard
vi.mock('server-only', () => ({}));

// Mock neon-db — we test that appendAgentNote is called with the right args.
const mockAppendAgentNote = vi.fn().mockResolvedValue('mock-id');
vi.mock('@/lib/neon-db', () => ({
  appendAgentNote: (...args: unknown[]) => mockAppendAgentNote(...args),
}));

// Mock chat-safety — default: no violations
const mockRuleClassify = vi.fn().mockReturnValue(null);
vi.mock('@/lib/chat-safety', () => ({
  ruleClassify: (...args: unknown[]) => mockRuleClassify(...args),
}));

import { applyMemoryTagsFromAssistant, stripMemoryMachineTags } from './chat-memory-persist';

const LEARNER = 'user_test123';
const AGENT = 'tutor';

function tag(payload: object): string {
  return `[[ASF_MEMORY_NOTE:${JSON.stringify(payload)}]]`;
}

describe('applyMemoryTagsFromAssistant', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('persists a well-formed note', async () => {
    const content = tag({ kind: 'preference', content: 'Likes worked examples first.', importance: 4 });
    const n = await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(n).toBe(1);
    expect(mockAppendAgentNote).toHaveBeenCalledWith(LEARNER, AGENT, {
      kind: 'preference',
      content: 'Likes worked examples first.',
      importance: 4,
      related_concept_id: null,
    });
  });

  it('drops a tag with malformed JSON — no throw', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
    const content = '[[ASF_MEMORY_NOTE:{bad json}]]';
    const n = await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(n).toBe(0);
    expect(mockAppendAgentNote).not.toHaveBeenCalled();
    expect(warnSpy).toHaveBeenCalledWith(
      expect.stringContaining('[ASF_MEMORY_TAG_SKIP]'),
      expect.objectContaining({ agent: AGENT }),
    );
    warnSpy.mockRestore();
  });

  it('drops a tag with empty content', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
    const content = tag({ kind: 'observation', content: '' });
    const n = await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(n).toBe(0);
    expect(mockAppendAgentNote).not.toHaveBeenCalled();
    expect(warnSpy).toHaveBeenCalled();
    warnSpy.mockRestore();
  });

  it('clamps content to 600 chars', async () => {
    const longContent = 'x'.repeat(800);
    const content = tag({ kind: 'observation', content: longContent });
    await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(mockAppendAgentNote).toHaveBeenCalledWith(
      LEARNER,
      AGENT,
      expect.objectContaining({ content: 'x'.repeat(600) }),
    );
  });

  it('strips machine tags embedded in note content', async () => {
    // Use a machine tag whose body has no `}` so the outer MEMORY_NOTE regex parses correctly.
    const dirty = 'Great progress [[ASF_CITE:derivatives_intro]] done!';
    const content = tag({ kind: 'win', content: dirty, importance: 4 });
    await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(mockAppendAgentNote).toHaveBeenCalledWith(
      LEARNER,
      AGENT,
      expect.objectContaining({ content: 'Great progress  done!' }),
    );
  });

  it('coerces an unknown kind to observation instead of dropping the note', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
    const content = tag({ kind: 'classified_info', content: 'Some content.' });
    const n = await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(n).toBe(1);
    expect(mockAppendAgentNote).toHaveBeenCalledWith(
      LEARNER,
      AGENT,
      expect.objectContaining({ kind: 'observation', content: 'Some content.' }),
    );
    expect(warnSpy).toHaveBeenCalledWith(
      expect.stringContaining('[ASF_MEMORY_TAG_COERCE]'),
      expect.objectContaining({ kind: 'classified_info' }),
    );
    warnSpy.mockRestore();
  });

  it('clamps out-of-range importance to 1–5', async () => {
    await applyMemoryTagsFromAssistant(
      LEARNER,
      AGENT,
      tag({ kind: 'observation', content: 'Test.', importance: 99 }),
    );
    expect(mockAppendAgentNote).toHaveBeenCalledWith(
      LEARNER,
      AGENT,
      expect.objectContaining({ importance: 5 }),
    );

    vi.clearAllMocks();
    await applyMemoryTagsFromAssistant(
      LEARNER,
      AGENT,
      tag({ kind: 'observation', content: 'Test.', importance: -5 }),
    );
    expect(mockAppendAgentNote).toHaveBeenCalledWith(
      LEARNER,
      AGENT,
      expect.objectContaining({ importance: 1 }),
    );
  });

  it('defaults to importance 3 when field is missing', async () => {
    const content = tag({ kind: 'observation', content: 'Observed something.' });
    await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(mockAppendAgentNote).toHaveBeenCalledWith(
      LEARNER,
      AGENT,
      expect.objectContaining({ importance: 3 }),
    );
  });

  it('drops a tag that fails the safety classifier', async () => {
    mockRuleClassify.mockReturnValueOnce('blocked_topic');
    const content = tag({ kind: 'observation', content: 'Something unsafe.' });
    const n = await applyMemoryTagsFromAssistant(LEARNER, AGENT, content);
    expect(n).toBe(0);
    expect(mockAppendAgentNote).not.toHaveBeenCalled();
  });

  it('processes multiple tags in one message, skipping invalid ones', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
    // Use `{broken json}` — the regex matches (starts with `{`) but JSON.parse fails.
    const message = [
      tag({ kind: 'preference', content: 'Good note.', importance: 3 }),
      '[[ASF_MEMORY_NOTE:{broken json here}]]',
      tag({ kind: 'win', content: 'Another good note.', importance: 4 }),
    ].join(' Some text in between. ');
    const n = await applyMemoryTagsFromAssistant(LEARNER, AGENT, message);
    expect(n).toBe(2);
    expect(mockAppendAgentNote).toHaveBeenCalledTimes(2);
    expect(warnSpy).toHaveBeenCalledTimes(1);
    warnSpy.mockRestore();
  });
});

describe('stripMemoryMachineTags', () => {
  it('removes ASF_MEMORY_NOTE tags from text', () => {
    const text = `Good job! ${tag({ kind: 'win', content: 'First derivation.' })} Keep going.`;
    expect(stripMemoryMachineTags(text)).toBe('Good job!  Keep going.');
  });

  it('leaves non-memory tags untouched', () => {
    const text = 'Some text [[ASF_PLAN_UPDATE:{}]] here.';
    expect(stripMemoryMachineTags(text)).toBe(text);
  });
});
