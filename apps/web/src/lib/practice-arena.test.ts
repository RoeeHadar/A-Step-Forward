import { describe, expect, it } from 'vitest';
import {
  buildHintLadder,
  gradePracticeItem,
  nextDifficulty,
  practiceXpSourceId,
  stripPracticeItemForClient,
  type PracticeItemSealed,
} from './practice-arena';

const sample: PracticeItemSealed = {
  id: 'item-1',
  source: 'authored',
  kind: 'mcq',
  difficulty: 'medium',
  concept_id: 'integration_intro',
  skill_atoms: ['power_rule'],
  stem_en: 'What is ∫x dx?',
  stem_he: 'מהו ∫x dx?',
  options_en: ['x^2/2 + C', 'x^2 + C', '2x + C'],
  options_he: ['x^2/2 + C', 'x^2 + C', '2x + C'],
  correct_index: 0,
  explanation_en: 'Power rule: increase exponent by 1 and divide.',
  explanation_he: 'כלל החזקה: מעלים מעריך ב-1 ומחלקים.',
  hints: buildHintLadder({
    conceptLabelEn: 'Integration intro',
    conceptLabelHe: 'מבוא לאינטגרציה',
    skillAtoms: ['power_rule'],
    explanationEn: 'Power rule: increase exponent by 1 and divide.',
    explanationHe: 'כלל החזקה.',
  }),
};

describe('practice-arena (ADR-0013)', () => {
  it('strips keys and only exposes unlocked hints', () => {
    const pub = stripPracticeItemForClient(sample, 1);
    expect(pub).not.toHaveProperty('correct_index');
    expect(pub).not.toHaveProperty('explanation_en');
    expect(pub.unlocked_hints).toHaveLength(1);
    expect(pub.hint_step).toBe(1);
  });

  it('grades MCQ server-side', () => {
    expect(gradePracticeItem(sample, 0).correct).toBe(true);
    expect(gradePracticeItem(sample, 1).correct).toBe(false);
  });

  it('hint ladder never uses explanation text that contains the answer', () => {
    const leaky = buildHintLadder({
      conceptLabelEn: 'Integrals',
      conceptLabelHe: 'אינטגרלים',
      skillAtoms: ['power_rule'],
      explanationEn: 'Answer: x^2/2 + C is correct.',
      explanationHe: 'התשובה: x^2/2 + C',
    });
    const joined = leaky.map((s) => `${s.en}\n${s.he}`).join('\n');
    expect(joined).not.toContain('x^2/2 + C');
    expect(joined).not.toMatch(/Answer:\s*x\^2/i);
    expect(joined).not.toContain('התשובה: x^2');
  });

  it('adapts difficulty from recent results', () => {
    expect(nextDifficulty([true, true], 'easy')).toBe('medium');
    expect(nextDifficulty([false, false], 'hard')).toBe('medium');
  });

  it('builds stable XP source ids', () => {
    expect(practiceXpSourceId('sess', 'item')).toBe('practice:sess:item');
  });
});
