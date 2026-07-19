import { describe, expect, it } from 'vitest';
import {
  aliasRedirectTarget,
  resolveLessonConceptId,
  resolveVariantLessonId,
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
    expect(resolveVariantLessonId('vectors_2d', '5pt')).toBe('vectors_2d');
    expect(resolveVariantLessonId('fluids_hydrostatics', '3pt')).toBe('fluids_hydrostatics');
  });

  it('returns the canonical lesson when the learner level is unknown', () => {
    expect(resolveVariantLessonId('vectors_2d', null)).toBe('vectors_2d');
    expect(resolveVariantLessonId('vectors_2d', 'hs_physics')).toBe('vectors_2d');
  });

  it('never invents a variant id that is not in the lesson index', () => {
    // Until variants are authored, no `__<track>` id should be returned.
    for (const level of ['3pt', '4pt', '5pt']) {
      expect(resolveVariantLessonId('vectors_2d', level)).toBe('vectors_2d');
    }
  });
});

describe('variantLessonIds', () => {
  it('returns an empty list when no variants are authored yet', () => {
    expect(variantLessonIds('vectors_2d')).toEqual([]);
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
});
