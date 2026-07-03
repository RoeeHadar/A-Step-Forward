import { describe, expect, it } from 'vitest';
import {
  buildPlanChangeRequest,
  extractPlanChangeTemplateBody,
  getPlanChangeDisplayTemplate,
  isPlanChangeDisplayTemplate,
  isPlanChangeTemplate,
  normalizePlanChangeMessage,
  planChangeTextForParsing,
  wrapPlanChangeMessage,
} from './plan-change-template';

describe('plan-change-template', () => {
  it('shows locale-pure display template without machine markers', () => {
    expect(getPlanChangeDisplayTemplate('he')).toContain('מטרה או מבחן');
    expect(getPlanChangeDisplayTemplate('he')).not.toContain('[[ASF');
    expect(getPlanChangeDisplayTemplate('en')).toContain('Goal or exam');
    expect(getPlanChangeDisplayTemplate('en')).not.toContain('[[ASF');
  });

  it('detects display form and wraps for server', () => {
    const display = getPlanChangeDisplayTemplate('he');
    expect(isPlanChangeDisplayTemplate(display)).toBe(true);
    expect(isPlanChangeTemplate(display)).toBe(true);
    const wire = wrapPlanChangeMessage(display);
    expect(wire).toContain('[[ASF-PLAN-UPDATE');
    expect(extractPlanChangeTemplateBody(wire)).toContain('מטרה או מבחן');
  });

  it('ignores casual plan-change phrasing without template form', () => {
    expect(
      isPlanChangeTemplate('יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם'),
    ).toBe(false);
  });

  it('normalizes display messages before parsing', () => {
    const display = buildPlanChangeRequest(
      { goal: 'מבחן בחדוא 1', date: 'עוד שבוע' },
      'he',
    );
    expect(isPlanChangeTemplate(display)).toBe(true);
    const parsed = planChangeTextForParsing(display);
    expect(parsed[0]).toContain('מבחן בחדוא 1');
    expect(parsed[0]).not.toContain('[[ASF');
  });

  it('normalizePlanChangeMessage wraps display-only input', () => {
    const raw = `אני מבקש/ת לעדכן את תוכנית הלימוד והמטרה שלי.

מטרה או מבחן: חדוא 1
מועד: עוד שבוע`;
    const normalized = normalizePlanChangeMessage(raw);
    expect(normalized).toContain('[[ASF-PLAN-UPDATE');
  });
});
