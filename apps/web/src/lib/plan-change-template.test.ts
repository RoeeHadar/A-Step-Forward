import { describe, expect, it } from 'vitest';
import {
  buildPlanChangeRequest,
  extractPlanChangeTemplateBody,
  getPlanChangeTemplate,
  isPlanChangeTemplate,
  planChangeTextForParsing,
} from './plan-change-template';

describe('plan-change-template', () => {
  it('detects official markers', () => {
    const msg = buildPlanChangeRequest(
      { goal: 'מבחן בחדוא 1', date: 'עוד שבוע' },
      'he',
    );
    expect(isPlanChangeTemplate(msg)).toBe(true);
    expect(extractPlanChangeTemplateBody(msg)).toContain('מבחן בחדוא 1');
  });

  it('ignores casual plan-change phrasing without markers', () => {
    expect(
      isPlanChangeTemplate('יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם'),
    ).toBe(false);
  });

  it('strips markers for parsing pipeline', () => {
    const msg = buildPlanChangeRequest(
      { goal: 'Calculus 1 exam', date: 'in one week' },
      'en',
    );
    const parsed = planChangeTextForParsing(msg);
    expect(parsed[0]).not.toContain('[[ASF-PLAN-UPDATE');
    expect(parsed[0]).toContain('Calculus 1 exam');
  });

  it('provides locale-specific blank templates', () => {
    expect(getPlanChangeTemplate('he')).toContain('מטרה / מבחן');
    expect(getPlanChangeTemplate('en')).toContain('Goal / exam');
  });
});
