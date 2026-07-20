import { describe, expect, it } from 'vitest';
import {
  aliasRedirectTarget,
  catalogDedupeKey,
  resolveLessonConceptId,
  resolveVariantLessonId,
  stripVariantSuffix,
  variantLessonIds,
} from './lesson-concept-resolve';

describe('resolveLessonConceptId', () => {
  it('prefers a dedicated authored lesson over alias redirect', () => {
    expect(resolveLessonConceptId('fluids_hydrostatics')).toBe('fluids_hydrostatics');
    expect(resolveLessonConceptId('vectors_2d')).toBe('vectors_2d');
  });

  it('falls back to alias target when no dedicated lesson exists', () => {
    expect(resolveLessonConceptId('limits_intro')).toBe('limits');
    expect(resolveLessonConceptId('coulomb_law')).toBe('electrostatics');
  });
});

describe('aliasRedirectTarget', () => {
  it('redirects alias-only slugs to their authored lesson', () => {
    expect(aliasRedirectTarget('limits_intro')).toBe('limits');
  });

  it('does not redirect when the slug has its own lesson', () => {
    expect(aliasRedirectTarget('fluids_hydrostatics')).toBeNull();
  });

  it('does not redirect removed or missing targets', () => {
    expect(aliasRedirectTarget('capacitors_parallel_plate')).toBeNull();
    expect(aliasRedirectTarget('em_waves')).toBeNull();
  });
});

describe('resolveVariantLessonId', () => {
  it('returns the canonical lesson when no per-track variant exists', () => {
    expect(resolveVariantLessonId('fluids_hydrostatics', '3pt')).toBe('fluids_hydrostatics');
  });

  it('returns the canonical lesson when the learner level is unknown', () => {
    expect(resolveVariantLessonId('vectors_2d', null)).toBe('vectors_2d');
    expect(resolveVariantLessonId('vectors_2d', 'hs_physics')).toBe('vectors_2d');
  });

  it('picks authored __4pt / __5pt / __uni variants when present', () => {
    expect(resolveVariantLessonId('equations_quadratic', '3pt')).toBe('equations_quadratic');
    expect(resolveVariantLessonId('equations_quadratic', '4pt')).toBe('equations_quadratic__4pt');
    expect(resolveVariantLessonId('equations_quadratic', '5pt')).toBe('equations_quadratic__5pt');
    expect(resolveVariantLessonId('equations_quadratic', 'uni')).toBe('equations_quadratic__uni');
    expect(resolveVariantLessonId('equations_quadratic', 'calc1')).toBe('equations_quadratic__uni');
  });

  it('never invents a variant id that is not in the lesson index', () => {
    for (const level of ['3pt', '4pt', '5pt', 'uni']) {
      // fluids has no track variants authored
      expect(resolveVariantLessonId('fluids_hydrostatics', level)).toBe('fluids_hydrostatics');
    }
  });
});

describe('variantLessonIds', () => {
  it('lists authored siblings for a first-wave concept', () => {
    const ids = variantLessonIds('equations_quadratic').map((v) => v.lessonId);
    expect(ids).toContain('equations_quadratic__4pt');
    expect(ids).toContain('equations_quadratic__5pt');
    expect(ids).toContain('equations_quadratic__uni');
  });

  it('returns an empty list when no variants are authored', () => {
    expect(variantLessonIds('fluids_hydrostatics')).toEqual([]);
  });
});

describe('catalogDedupeKey', () => {
  it('collapses track variants to the canonical id', () => {
    expect(catalogDedupeKey('equations_quadratic__4pt')).toBe('equations_quadratic');
    expect(stripVariantSuffix('algebra_basics__uni')).toBe('algebra_basics');
  });
});

describe('dedupeConceptIdsForCatalog', () => {
  it('removes alias slug when canonical id shares the same lesson', async () => {
    const { dedupeConceptIdsForCatalog, resolveConceptAlias } = await import('./concept-aliases');
    const ids = [
      'descriptive_statistics',
      'statistics_descriptive',
      'basic_probability',
      'probability_basic',
    ];
    const out = dedupeConceptIdsForCatalog(ids);
    expect(out).toEqual(['statistics_descriptive', 'probability_basic']);
    expect(out.every((id) => resolveConceptAlias(id) === id || id === 'probability_basic')).toBe(
      true,
    );
  });

  it('keeps distinct authored lessons that previously shared alias targets', async () => {
    const { dedupeConceptIdsForCatalog } = await import('./concept-aliases');
    const out = dedupeConceptIdsForCatalog(['vectors_2d', 'vectors_plane', 'fluids_hydrostatics']);
    expect(out).toEqual(['vectors_2d', 'vectors_plane', 'fluids_hydrostatics']);
  });

  it('collapses __track siblings in a mixed allowlist', async () => {
    const { dedupeConceptIdsForCatalog } = await import('./concept-aliases');
    const out = dedupeConceptIdsForCatalog([
      'equations_quadratic',
      'equations_quadratic__4pt',
      'equations_quadratic__5pt',
    ]);
    expect(out).toEqual(['equations_quadratic']);
  });
});
