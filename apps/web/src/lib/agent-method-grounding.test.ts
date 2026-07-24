/**
 * Method-grounding contract tests (ADR-0014 disease fix — not shape-specific).
 */
import { describe, expect, it } from 'vitest';
import {
  buildMethodAuthorityBlock,
  buildMethodSourceInventory,
  isMathTeachingTurn,
  lacksMethodCitation,
  looksLikeSocraticStall,
  softRepairSocraticStall,
} from './agent-method-grounding';
import { buildAgentSkillsPrompt } from './agent-skills';

describe('isMathTeachingTurn', () => {
  it('detects Hebrew solve / geometry asks', () => {
    expect(
      isMathTeachingTurn(
        'טרפז שווה-שוקיים עם בסיסים 8 ו-14 ושוקיים 5. הסבירו מציאת גובה ואז חשבו שטח.',
      ),
    ).toBe(true);
    expect(isMathTeachingTurn('מה הסטטוס שלי')).toBe(false);
  });
});

describe('buildMethodSourceInventory + authority block', () => {
  it('marks thin when no lesson/hints/verify', () => {
    const inv = buildMethodSourceInventory({
      conceptId: null,
      lesson: null,
      verify: null,
    });
    expect(inv.thin).toBe(true);
    const block = buildMethodAuthorityBlock(inv);
    expect(block).toContain('Method authority');
    expect(block).toContain('THIN');
    expect(block).toContain('refuse to invent');
    expect(block).not.toContain('Isosceles trapezoid (mandatory'); // disease fix is general
  });

  it('lists insights when present', () => {
    const inv = buildMethodSourceInventory({
      conceptId: 'area_perimeter',
      lesson: null,
      hints: {
        key_insights: ['Trapezoid area averages the two parallel sides times height.'],
      },
      verify: null,
    });
    expect(inv.thin).toBe(false);
    expect(inv.hasKeyInsights).toBe(true);
    const block = buildMethodAuthorityBlock(inv);
    expect(block).toContain('usable');
    expect(block).toContain('averages the two parallel');
  });
});

describe('citation / stall heuristics', () => {
  it('flags uncited math-heavy replies', () => {
    expect(
      lacksMethodCitation(
        'נחשב את המשולש העליון עם בסיס 8 ושוקיים 5 ואז g=sqrt(39) לשטח.',
      ),
    ).toBe(true);
    expect(
      lacksMethodCitation(
        'לפי `concept:area_perimeter`: מורידים אנכים. Sources: concept:area_perimeter',
      ),
    ).toBe(false);
  });

  it('flags empty Socratic stall', () => {
    expect(
      looksLikeSocraticStall('איך אתה חושב שאתה יכול למצוא את הגובה?'),
    ).toBe(true);
  });

  it('replaces stall with learner-facing recovery (no Method authority jargon)', () => {
    const fixed = softRepairSocraticStall('איך אתה חושב שאתה יכול למצוא את הגובה?', 'he');
    expect(fixed.repaired).toBe(true);
    expect(fixed.text).toContain('צדקתם');
    expect(fixed.text).not.toContain('Method authority');
    expect(fixed.text).not.toContain('Socratic');
  });
});

describe('agent-skills method grounding', () => {
  it('shared skills encode general method contract, not only one shape', () => {
    const shared = buildAgentSkillsPrompt('tutor');
    expect(shared).toContain('Method grounding');
    expect(shared).toContain('refuse freestyle');
    expect(shared).toContain('uncited construction');
  });
});
