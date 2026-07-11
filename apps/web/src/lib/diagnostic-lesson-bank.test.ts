import { describe, expect, it } from 'vitest';
import { pickDiagnosticItemFromLessonBank } from './diagnostic-lesson-bank';
import { isEdgeCaseStem } from './diagnostic-stem-filter';

describe('pickDiagnosticItemFromLessonBank', () => {
  const profile = {
    subjects: ['math'],
    points_group: '4pt',
  } as never;

  it('returns a real MCQ for a foundational self-score concept', () => {
    const item = pickDiagnosticItemFromLessonBank(
      'algebra_basics',
      profile,
      [],
      4,
      'basic',
    );
    expect(item).not.toBeNull();
    expect(item!.stem.length).toBeGreaterThan(10);
    expect(item!.options.choices.length).toBeGreaterThanOrEqual(2);
    expect(item!.topic).toBeTruthy();
  });

  it('respects excludeItemIds', () => {
    const first = pickDiagnosticItemFromLessonBank(
      'equations_linear',
      profile,
      [],
      5,
      'medium',
    );
    expect(first).not.toBeNull();
    const second = pickDiagnosticItemFromLessonBank(
      'equations_linear',
      profile,
      [first!.id],
      5,
      'medium',
    );
    if (second) {
      expect(second.id).not.toBe(first!.id);
    }
  });
});

describe('isEdgeCaseStem', () => {
  it('detects exception-style stems', () => {
    expect(isEdgeCaseStem('Which statement is NOT always true for linear functions?')).toBe(
      true,
    );
    expect(isEdgeCaseStem('Solve $2x+1=5$.')).toBe(false);
  });
});
