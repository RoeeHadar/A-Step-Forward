import { describe, expect, it } from 'vitest';
import { classifyCites, stripAllMachineTags, stripCiteMachineTags, type SoftCitationPayload } from './chat-cite-tags';

describe('classifyCites', () => {
  it('accepts a valid concept cite', () => {
    const cites: SoftCitationPayload[] = [{ concept_id: 'stats_mean', tools: ['get_due_queue'] }];
    const result = classifyCites(cites, ['stats_mean']);
    expect(result.valid).toEqual(['concept:stats_mean']);
    expect(result.invalid).toEqual([]);
  });

  it('accepts a valid lesson cite', () => {
    const cites: SoftCitationPayload[] = [{ lesson_id: 'lesson-abc-123' }];
    const result = classifyCites(cites, ['lesson:lesson-abc-123']);
    expect(result.valid).toEqual(['lesson:lesson-abc-123']);
    expect(result.invalid).toEqual([]);
  });

  it('flags an invalid id', () => {
    const cites: SoftCitationPayload[] = [{ concept_id: 'invented_topic' }];
    const result = classifyCites(cites, ['stats_mean']);
    expect(result.valid).toEqual([]);
    expect(result.invalid).toEqual(['concept:invented_topic']);
  });

  it('handles mixed valid and invalid cites', () => {
    const cites: SoftCitationPayload[] = [
      { concept_id: 'stats_mean' },
      { concept_id: 'fake_concept', lesson_id: 'lesson-abc-123' },
    ];
    const result = classifyCites(cites, ['stats_mean', 'lesson:lesson-abc-123']);
    expect(result.valid).toEqual(['concept:stats_mean', 'lesson:lesson-abc-123']);
    expect(result.invalid).toEqual(['concept:fake_concept']);
  });

  it('marks all cites invalid when grounding set is empty', () => {
    const cites: SoftCitationPayload[] = [{ concept_id: 'stats_mean' }];
    const result = classifyCites(cites, []);
    expect(result.valid).toEqual([]);
    expect(result.invalid).toEqual(['concept:stats_mean']);
  });
});

describe('stripAllMachineTags — Bug 2: all ASF_* families stripped from stream', () => {
  it('strips [[ASF_CITE:...]] tags', () => {
    const raw = 'answer [[ASF_CITE:{"concept_id":"stats_mean"}]]';
    expect(stripAllMachineTags(raw)).toBe('answer');
  });

  it('strips [[ASF_MEMORY_NOTE:...]] tags', () => {
    const raw = 'good answer [[ASF_MEMORY_NOTE:{"kind":"observation","content":"learner knows limits","importance":3}]]';
    expect(stripAllMachineTags(raw)).toBe('good answer');
  });

  it('strips [[ASF_PLAN_UPDATE:...]] tags', () => {
    const raw = 'plan updated [[ASF_PLAN_UPDATE:{"confirmed":true,"priority_concepts":["limits"]}]]';
    expect(stripAllMachineTags(raw)).toBe('plan updated');
  });

  it('strips multiple different tag families in one pass', () => {
    const raw = 'txt [[ASF_CITE:{"c":"x"}]] more [[ASF_MEMORY_NOTE:{"content":"y"}]] done';
    const result = stripAllMachineTags(raw);
    // Inline tags leave single spaces between words after stripping; markdown
    // rendering collapses any extra whitespace so this is acceptable.
    expect(result).not.toContain('ASF_CITE');
    expect(result).not.toContain('ASF_MEMORY_NOTE');
    expect(result).toContain('txt');
    expect(result).toContain('more');
    expect(result).toContain('done');
  });

  it('leaves normal prose with [[ intact when no ASF_ prefix', () => {
    const raw = 'see [[note]] or [[ref:123]]';
    expect(stripAllMachineTags(raw)).toBe('see [[note]] or [[ref:123]]');
  });

  it('preserves leading/trailing whitespace when trim:false (stream deltas)', () => {
    const raw = ' שלום [[ASF_CITE:{"tools":["x"]}]] עולם ';
    expect(stripAllMachineTags(raw, { trim: false })).toBe(' שלום  עולם ');
    expect(stripAllMachineTags(raw)).toBe('שלום  עולם');
  });

  it('chunk-boundary: tag split across two enqueue calls — combined chunk strips cleanly', () => {
    // Simulate: first chunk ends mid-tag, second chunk completes it.
    // The streaming carry logic in enqueueVisibleToken buffers [[ASF_ prefixes
    // and merges before calling stripAllMachineTags, so the full merged string
    // must not contain any ASF tag remnants.
    const part1 = 'Here is an answer. [[ASF_MEMO';
    const part2 = 'RY_NOTE:{"content":"private"}]] The end.';
    const merged = part1 + part2;
    const stripped = stripAllMachineTags(merged);
    expect(stripped).not.toContain('MEMORY_NOTE');
    expect(stripped).not.toContain('[[ASF_');
    expect(stripped).toContain('Here is an answer.');
    expect(stripped).toContain('The end.');
  });

  it('stripCiteMachineTags (legacy) still only strips CITE tags', () => {
    const raw = 'text [[ASF_CITE:{"c":"x"}]] mid [[ASF_MEMORY_NOTE:{"content":"y"}]] end';
    const result = stripCiteMachineTags(raw);
    expect(result).not.toContain('ASF_CITE');
    expect(result).toContain('ASF_MEMORY_NOTE');
  });
});
