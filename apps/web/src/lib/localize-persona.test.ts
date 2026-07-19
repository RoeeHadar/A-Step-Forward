import { describe, expect, it } from 'vitest';
import {
  localizePersonaMarkdown,
  personaNeedsDiagnosticMigration,
  stripDiagnosticPersonaContent,
  translateDiagnosticBulletEnToHe,
} from './localize-persona';

const SAMPLE_EN_BULLET =
  'Diagnostic calibration (6 validation questions) toward Function Analysis — Extrema. Each topic was tested at the difficulty matching your onboarding self-rating. No major gaps surfaced — start at the next path step. Validated strengths: Combinatorics (Counting Methods), Factoring Polynomials, Algebra Basics. Week-1 focus: combinatorics. (Weak: none; Strong: combinatorics, factoring, algebra_basics)';

const SAMPLE_PERSONA = `## Diagnostic calibration
- ${SAMPLE_EN_BULLET}
- Diagnostic calibration (7 validation questions) toward Function Analysis — Extrema. Each topic was tested at the difficulty matching your onboarding self-rating. Confirmed gaps — prioritize: Linear Equations & Systems. Validated strengths: Combinatorics. Week-1 focus: equations_linear. (Weak: equations_linear; Strong: combinatorics)

## How they like explanations
- Prefers worked examples
`;

describe('localize-persona', () => {
  it('strips diagnostic sections and orphan bullets', () => {
    const stripped = stripDiagnosticPersonaContent(SAMPLE_PERSONA);
    expect(stripped).not.toMatch(/Diagnostic calibration/i);
    expect(stripped).toMatch(/How they like explanations/);
    expect(stripped).toMatch(/Prefers worked examples/);
  });

  it('translates a known English diagnostic bullet to Hebrew', () => {
    const he = translateDiagnosticBulletEnToHe(`- ${SAMPLE_EN_BULLET}`);
    expect(he).toBeTruthy();
    expect(he!).toMatch(/כיול אבחון/);
    expect(he!).toMatch(/Function Analysis/);
    expect(he!).not.toMatch(/Diagnostic calibration/);
    expect(he!).toMatch(/חוזקות מאומתות/);
  });

  it('replaces all English diagnostic dumps with a single HE brief', () => {
    const brief = 'כיול אבחון (6 שאלות אימות) לכיוון **ניתוח פונקציות**.';
    const out = localizePersonaMarkdown(SAMPLE_PERSONA, 'he', brief, null);
    expect(out).toMatch(/## כיול אבחון/);
    expect(out).toContain(brief);
    expect(out).not.toMatch(/Diagnostic calibration/i);
    expect(out).toMatch(/## איך הם אוהבים הסברים/);
    // Only one diagnostic bullet
    const diagBullets = out.split('\n').filter((l) => l.startsWith('- כיול אבחון') || l.includes('שאלות אימות'));
    expect(diagBullets.length).toBeGreaterThanOrEqual(1);
    expect((out.match(/## כיול אבחון/g) ?? []).length).toBe(1);
  });

  it('localizes Hebrew header + English bullets (user-reported shape)', () => {
    const messy = `## כיול אבחון
${SAMPLE_EN_BULLET}

${SAMPLE_EN_BULLET.replace('(6', '(5')}
`;
    const out = localizePersonaMarkdown(
      messy,
      'he',
      'כיול אבחון מקוצר בעברית.',
      null,
    );
    expect(out).not.toMatch(/Diagnostic calibration/i);
    expect(out).toContain('כיול אבחון מקוצר בעברית.');
  });

  it('detects personas that need migration', () => {
    expect(personaNeedsDiagnosticMigration(SAMPLE_PERSONA)).toBe(true);
    expect(personaNeedsDiagnosticMigration('## כיול אבחון\n- שלום')).toBe(false);
  });
});
