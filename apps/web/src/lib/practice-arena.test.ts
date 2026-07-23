import { describe, expect, it } from 'vitest';
import {
  buildHintLadder,
  formatPracticeArenaChatBlock,
  gradePracticeItem,
  nextDifficulty,
  parsePracticeChatContext,
  parsePracticeQueueMode,
  pickExploreFocusConceptId,
  practiceItemFingerprint,
  practiceSuccessFromProcess,
  practiceXpSourceId,
  stemLooksLanguageMixed,
  stripPracticeItemForClient,
  type PracticeItemSealed,
} from './practice-arena';

const sample: PracticeItemSealed = {
  id: 'item-1',
  source: 'authored',
  fingerprint: 'q:item-1',
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
    expect(pub).not.toHaveProperty('correct_answer');
    expect(pub).not.toHaveProperty('answer_payload');
    expect(pub.unlocked_hints).toHaveLength(1);
    expect(pub.hint_step).toBe(1);
  });

  it('never exposes sealed fields even at hint_step 3', () => {
    const pub = stripPracticeItemForClient(sample, 3);
    expect(pub.unlocked_hints).toHaveLength(3);
    expect(JSON.stringify(pub)).not.toContain('correct_index');
    expect(JSON.stringify(pub)).not.toContain('Power rule: increase');
  });

  it('grades MCQ server-side', () => {
    expect(gradePracticeItem(sample, 0).correct).toBe(true);
    expect(gradePracticeItem(sample, 1).correct).toBe(false);
  });

  it('grades numeric range answers including worked text and LaTeX', () => {
    const numeric: PracticeItemSealed = {
      ...sample,
      id: 'range-1',
      kind: 'numeric',
      correct_index: null,
      options_en: null,
      options_he: null,
      correct_answer: '13',
      answer_payload: { value: 13 },
      stem_en: 'Find the range of $4, 9, 2, 15, 6$.',
      stem_he: 'מצאו את הטווח של $4, 9, 2, 15, 6$.',
    };
    expect(gradePracticeItem(numeric, '13').correct).toBe(true);
    expect(gradePracticeItem(numeric, '$13$').correct).toBe(true);
    expect(gradePracticeItem(numeric, 'טווח = מקסימום − מינימום. $15-2$.\n\n**תשובה:** $13$.').correct).toBe(
      true,
    );
    expect(gradePracticeItem(numeric, '15-2=13').correct).toBe(true);
    expect(gradePracticeItem(numeric, '12').correct).toBe(false);
    // key only in payload.value
    const payloadOnly = { ...numeric, correct_answer: null };
    expect(gradePracticeItem(payloadOnly, '13').correct).toBe(true);
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

  it('parses queue modes including explore', () => {
    expect(parsePracticeQueueMode('due')).toBe('due');
    expect(parsePracticeQueueMode('explore')).toBe('explore');
    expect(parsePracticeQueueMode('nope')).toBe('default');
  });

  it('explore picker prefers weakest mastery outside the active week', () => {
    expect(
      pickExploreFocusConceptId({
        masteryMap: { a: 0.9, b: 0.2, c: 0.1 },
        activeConceptIds: ['a', 'c'],
        candidateConceptIds: ['a', 'b', 'c', 'd'],
      }),
    ).toBe('b');
  });

  it('explore picker falls back to any candidate outside active week', () => {
    expect(
      pickExploreFocusConceptId({
        masteryMap: {},
        activeConceptIds: ['a'],
        candidateConceptIds: ['a', 'd'],
      }),
    ).toBe('d');
  });

  it('explore picker returns null when every candidate is in the active week', () => {
    expect(
      pickExploreFocusConceptId({
        masteryMap: { a: 0.1 },
        activeConceptIds: ['a', 'd'],
        candidateConceptIds: ['a', 'd'],
      }),
    ).toBeNull();
  });

  it('parses and formats practice chat context without answer keys', () => {
    const ctx = parsePracticeChatContext({
      session_id: 's1',
      item_id: 'i1',
      concept_id: 'integration_intro',
      kind: 'mcq',
      difficulty: 'medium',
      hint_step: 1,
      stem_en: 'What is ∫x dx?',
      stem_he: 'מהו?',
      item_graded: false,
      correct_index: 0,
    });
    expect(ctx).not.toBeNull();
    const block = formatPracticeArenaChatBlock(ctx!);
    expect(block).toContain('PRACTICE ARENA');
    expect(block).toContain('graded=false');
    expect(block).toContain('NEVER reveal');
    expect(block).toContain('הצעד הבא המומלץ');
    expect(block).not.toContain('correct_index');
    expect(parsePracticeChatContext({ session_id: 'x' })).toBeNull();
  });

  it('fingerprints authored by question id and generated by stem', () => {
    expect(
      practiceItemFingerprint({
        conceptId: 'limits',
        stemEn: 'Compute lim',
        stemHe: 'חשב גבול',
        questionId: 'q-9',
      }),
    ).toBe('q:q-9');
    const a = practiceItemFingerprint({
      conceptId: 'limits',
      stemEn: 'Compute lim x->0',
      stemHe: 'חשב גבול',
    });
    const b = practiceItemFingerprint({
      conceptId: 'limits',
      stemEn: 'Compute lim x->0',
      stemHe: 'חשב גבול',
    });
    expect(a).toBe(b);
    expect(a.startsWith('fp:')).toBe(true);
  });

  it('treats process score >= 0.6 as success', () => {
    expect(practiceSuccessFromProcess(0.6)).toBe(true);
    expect(practiceSuccessFromProcess(0.59)).toBe(false);
  });

  it('flags mixed-language stems outside math', () => {
    expect(stemLooksLanguageMixed('Find the derivative of f')).toBe(false);
    expect(stemLooksLanguageMixed('מצאו את הנגזרת of the function')).toBe(true);
    expect(stemLooksLanguageMixed('חשבו את $\\frac{1}{2}$ בזהירות')).toBe(false);
  });
});
