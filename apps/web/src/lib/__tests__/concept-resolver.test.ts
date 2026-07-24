import { describe, expect, it } from 'vitest';
import { resolveConceptsTiered } from '../concept-resolver';

// ---------------------------------------------------------------------------
// Exact tier
// ---------------------------------------------------------------------------
describe('exact tier', () => {
  it('matches by English name', () => {
    const result = resolveConceptsTiered('I need help with Logarithms', []);
    expect(result.tier).toBe('exact');
    expect(result.concepts.map((c) => c.id)).toContain('logarithms');
  });

  it('matches by Hebrew name_he', () => {
    const result = resolveConceptsTiered('לא מבין גבולות', []);
    expect(result.tier).toBe('exact');
    expect(result.concepts.map((c) => c.id)).toContain('limits');
  });

  it('matches by concept id with underscores expanded', () => {
    // id "projectile motion" (from projectile_motion) appears literally
    const result = resolveConceptsTiered('let me study projectile motion today', []);
    expect(result.tier).toBe('exact');
    expect(result.concepts.map((c) => c.id)).toContain('projectile_motion');
  });

  it('caps results at 3', () => {
    // "משוואות" appears in many Hebrew names — cap should hold
    const result = resolveConceptsTiered('שאלה על משוואות ריבועיות', []);
    expect(result.concepts.length).toBeLessThanOrEqual(3);
  });
});

// ---------------------------------------------------------------------------
// Alias tier — Hebrew morphological variants
// ---------------------------------------------------------------------------
describe('alias tier — Hebrew morphology', () => {
  it('resolves "זריקה אנכית" → projectile_motion via alias (phrase not in name_he)', () => {
    // name_he = "זריקה" but "כדור נזרק" is alias-only
    const result = resolveConceptsTiered('כדור נזרק למעלה באנכי', []);
    expect(result.tier).toBe('alias');
    expect(result.concepts.map((c) => c.id)).toContain('projectile_motion');
  });

  it('resolves "אפקט דופלר" phrase → doppler via alias', () => {
    // "תזוזת דופלר" is alias-only; exact name_he is "אפקט דופלר"
    const result = resolveConceptsTiered('יש לי בעיה עם תזוזת דופלר', []);
    expect(result.tier).toBe('alias');
    expect(result.concepts.map((c) => c.id)).toContain('doppler');
  });

  it('resolves "סדרה חשבונית" → sequences_arithmetic', () => {
    const result = resolveConceptsTiered('בעיה על סדרה חשבונית עם הפרש קבוע', []);
    expect(result.tier).toBe('alias');
    expect(result.concepts.map((c) => c.id)).toContain('sequences_arithmetic');
  });

  it('resolves "כלל השרשרת" → derivatives_chain_rule', () => {
    const result = resolveConceptsTiered('איך משתמשים בכלל השרשרת?', []);
    expect(result.tier).toBe('alias');
    expect(result.concepts.map((c) => c.id)).toContain('derivatives_chain_rule');
  });

  it('resolves "חוק קולון" → coulomb_law', () => {
    const result = resolveConceptsTiered('תסביר לי חוק קולון', []);
    expect(result.tier).toBe('alias');
    expect(result.concepts.map((c) => c.id)).toContain('coulomb_law');
  });

  it('resolves "suvat equations" → kinematics_1d', () => {
    const result = resolveConceptsTiered('how do I use the suvat equations?', ['physics']);
    expect(result.tier).toBe('alias');
    expect(result.concepts.map((c) => c.id)).toContain('kinematics_1d');
  });
});

// ---------------------------------------------------------------------------
// Tier 'none'
// ---------------------------------------------------------------------------
describe('none tier', () => {
  it('returns none for empty message', () => {
    const result = resolveConceptsTiered('', []);
    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });

  it('returns none for gibberish', () => {
    const result = resolveConceptsTiered('xyzzy frobnik quuxbar', []);
    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// Subject filter
// ---------------------------------------------------------------------------
describe('subject filter', () => {
  it('restricts to physics subject only', () => {
    const result = resolveConceptsTiered('suvat equations', ['physics']);
    const subjects = result.concepts.map((c) => c.subject);
    expect(subjects.every((s) => s === 'physics')).toBe(true);
  });

  it('restricts to math subject only', () => {
    const result = resolveConceptsTiered('parabola', ['math']);
    const subjects = result.concepts.map((c) => c.subject);
    expect(subjects.every((s) => s === 'math')).toBe(true);
  });

  it('returns none when subject filter excludes all matches', () => {
    // "kinematics 1d" is physics — should get nothing if subjects=['math']
    const result = resolveConceptsTiered('kinematics 1d', ['math']);
    expect(result.concepts).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// Cap enforcement
// ---------------------------------------------------------------------------
describe('cap enforcement', () => {
  it('alias tier respects cap of 3', () => {
    // Broad phrase that matches many aliases; must still be capped at 3
    const result = resolveConceptsTiered(
      'derivative polynomial integral limit function analysis',
      [],
    );
    expect(result.concepts.length).toBeLessThanOrEqual(3);
  });
});
