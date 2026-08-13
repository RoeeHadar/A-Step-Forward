import { describe, expect, it } from 'vitest';
import { CHAT_CONTEXT, fitSystemSections } from './chat-context-policy';
import {
  assembleChatSystemPrompt,
  buildHowToTeachBlock,
  filterNotesByRelevance,
  partitionInjectedContext,
} from './chat-context-builder';

describe('chat-context-builder (ADR-0015)', () => {
  it('partitionInjectedContext keeps baseline in core and packs optional headers', () => {
    const full = [
      '## A Step Forward — compact baseline',
      'core rules here',
      '## Response language',
      '- Hebrew',
      '## Learner profile (internal facts — paraphrase; never dump field-by-field)',
      '- Goal: bagrut',
      '## Mastery so far',
      '- Weak areas: integrals',
      '## Active week',
      '- Week 2',
    ].join('\n');
    const { core, packs } = partitionInjectedContext(full);
    expect(core).toContain('compact baseline');
    expect(core).toContain('Response language');
    expect(packs.map((p) => p.id)).toEqual(
      expect.arrayContaining(['profile', 'mastery', 'activeWeek']),
    );
  });

  it('assembleChatSystemPrompt drops low-priority packs before core', () => {
    const core = 'CORE_IDENTITY';
    const packs = [
      { id: 'xp' as const, content: '## XP\n' + 'x'.repeat(10_000) },
      { id: 'mastery' as const, content: '## Mastery so far\n' + 'm'.repeat(10_000) },
      { id: 'profile' as const, content: '## Learner profile\nkeep-me-profile' },
    ];
    const { system, dropped } = assembleChatSystemPrompt(core, packs, '\n\nTAIL');
    expect(system).toContain('CORE_IDENTITY');
    expect(system).toContain('TAIL');
    expect(system.length).toBeLessThanOrEqual(CHAT_CONTEXT.maxSystemChars);
    expect(dropped.length).toBeGreaterThan(0);
    expect(dropped).toContain('xp');
  });

  it('fitSystemSections never drops priority >= 90', () => {
    const result = fitSystemSections(
      [
        { id: 'core', content: 'c'.repeat(12_000), priority: 100 },
        { id: 'notes', content: 'n'.repeat(12_000), priority: 40 },
      ],
      '\n\nTAIL',
    );
    expect(result.system).toContain('c'.repeat(100));
    expect(result.dropped).toContain('notes');
    expect(result.dropped).not.toContain('core');
  });

  it('filterNotesByRelevance keeps overlapping or high-importance notes', () => {
    const notes = [
      { content: 'struggles with integrals', importance: 2 },
      { content: 'likes morning study', importance: 5 },
      { content: 'unrelated hobby pottery', importance: 2 },
    ];
    const kept = filterNotesByRelevance(notes, 'help me with integrals please');
    expect(kept.map((n) => n.content)).toContain('struggles with integrals');
    expect(kept.map((n) => n.content)).not.toContain('unrelated hobby pottery');
  });

  it('filterNotesByRelevance keeps misconception notes without token overlap', () => {
    const notes = [
      { content: 'confuses chain rule with product rule', kind: 'misconception', importance: 3 },
      { content: 'unrelated hobby pottery', kind: 'observation', importance: 2 },
    ];
    const kept = filterNotesByRelevance(notes, 'what is a derivative?');
    expect(kept.map((n) => n.content)).toContain('confuses chain rule with product rule');
    expect(kept.map((n) => n.content)).not.toContain('unrelated hobby pottery');
  });

  it('buildHowToTeachBlock encodes dialogue mode and explanation style', () => {
    const block = buildHowToTeachBlock({
      tutorMode: 'direct',
      preferredStyle: 'practice_first',
      attentionSpanMin: 20,
    });
    expect(block).toContain('direct');
    expect(block).toContain('practice_first');
    expect(block).toContain('20');
  });
});
