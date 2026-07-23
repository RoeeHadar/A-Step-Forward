import { describe, expect, it } from 'vitest';
import { pickPressureNextStep } from './pressure-next-step';

describe('pickPressureNextStep (ADR-0012)', () => {
  it('picks lowest mastery among active-week concepts', () => {
    const pick = pickPressureNextStep({
      activeWeekConcepts: [
        { conceptId: 'a', nameHe: 'נגזרות', nameEn: 'Derivatives', mastery: 0.8 },
        { conceptId: 'b', nameHe: 'אינטגרלים', nameEn: 'Integrals', mastery: 0.2 },
        { conceptId: 'c', nameHe: 'סדרות', nameEn: 'Series', mastery: 0.5 },
      ],
    });
    expect(pick?.conceptId).toBe('b');
    expect(pick?.labelHe).toBe('אינטגרלים');
  });

  it('falls back to first active when mastery ties / missing', () => {
    const pick = pickPressureNextStep({
      activeWeekConcepts: [
        { conceptId: 'first', nameHe: 'ראשון', mastery: null },
        { conceptId: 'second', nameHe: 'שני', mastery: null },
      ],
    });
    expect(pick?.conceptId).toBe('first');
  });

  it('falls back to planner path[0] when no active week', () => {
    const pick = pickPressureNextStep({
      plannerPathIds: ['integration_intro', 'derivatives_rules'],
      conceptTitles: {
        integration_intro: { he: 'מבוא לאינטגרציה', en: 'Integration intro' },
      },
    });
    expect(pick?.conceptId).toBe('integration_intro');
    expect(pick?.labelHe).toContain('אינטגרציה');
  });

  it('returns null when nothing available', () => {
    expect(pickPressureNextStep({})).toBeNull();
  });
});
