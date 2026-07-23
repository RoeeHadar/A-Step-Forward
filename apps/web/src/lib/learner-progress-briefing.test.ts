/**
 * Unit tests for bilingual progress briefing (ADR-0011).
 */
import { describe, expect, it } from 'vitest';
import {
  buildBilingualProgressBriefing,
  buildLearnerFacingStatusPack,
  formatLearnerFacingStatusHe,
  formatProgressBriefingEn,
  formatProgressBriefingHe,
} from './learner-progress-briefing';

const SAMPLE = {
  goalKey: 'bagrut_math_5',
  goalLabel: 'Bagrut Math 5',
  examDateLabel: '15 Sep 2026',
  daysToExam: 55,
  hoursPerWeek: 10,
  pointsGroup: '5pt',
  anxiety: 9,
  motivation: 8,
  strongConcepts: ['derivatives_rules', 'definite_integrals'],
  weakConcepts: ['integration_intro'],
  activeWeekNumber: 2,
  activeWeekConcepts: ['integration_intro', 'derivatives_rules'],
  xpLevel: 10,
  xpTotal: 985,
  readinessPct: 42,
  readinessBand: 'building' as const,
  readinessPhase: 'building' as const,
  paceStatus: 'on_track' as const,
  recentGateSummaryHe: 'שער שבוע 1 עבר (~94%)',
  recentGateSummaryEn: 'Week 1 gate passed (~94%)',
  nextStepHe: 'מבוא לאינטגרציה',
  nextStepEn: 'Integration intro',
  nextStepConceptId: 'integration_intro',
};

describe('learner-progress-briefing', () => {
  it('includes Hebrew and English blocks', () => {
    const out = buildBilingualProgressBriefing(SAMPLE);
    expect(out).toContain('### תמצית התקדמות');
    expect(out).toContain('### Progress briefing (English)');
    expect(out).toContain('never promise bagrut success');
    expect(out).toContain('לעולם לא להבטיח הצלחה בבגרות');
    expect(out).toContain('do NOT dump fields');
  });

  it('paraphrase-friendly HE summary mentions week and readiness band', () => {
    const he = formatProgressBriefingHe(SAMPLE);
    expect(he).toContain('שבוע פעיל 2');
    expect(he).toContain('בבנייה');
    expect(he).toContain('רמה 10');
    expect(he).not.toContain('GMT');
  });

  it('EN summary mirrors key facts', () => {
    const en = formatProgressBriefingEn(SAMPLE);
    expect(en).toContain('active week 2');
    expect(en).toContain('building');
    expect(en).toContain('level 10');
    expect(en).toContain('Week 1 gate passed');
  });

  it('ADR-0012 learner-facing pack is prose, not a field dump', () => {
    const pack = buildLearnerFacingStatusPack({
      ...SAMPLE,
      paceStatus: 'at_risk',
    });
    expect(pack).toContain('AUTHORITATIVE learner-facing status pack');
    expect(pack).toContain('מבוא לאינטגרציה');
    expect(pack).toContain('Integration intro');
    expect(pack).toContain('concept:integration_intro');
    expect(pack).toMatch(/מסלול|5 יח|track/i);
    expect(pack).not.toContain('bagrut_math_5');
    expect(pack).not.toContain('עדיין לא סומנו');
    expect(pack).toContain('סיכון לפיגור');
    expect(formatLearnerFacingStatusHe(SAMPLE)).toContain('אל תגיד שאינך יודע');
  });
});
