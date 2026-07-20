import { describe, expect, it } from 'vitest';
import {
  isCatalogTitleConcept,
  resolveConceptTitles,
} from './concept-display-names';
import {
  findCategoryIdForConcept,
  isConceptInCurriculumCatalog,
} from './curriculum-categories';
import { resolveLegacyLessonLearnHref } from './learn-routes';

const CATALOG_ONLY_IDS = [
  'extreme_value_theorem',
  'intermediate_value_theorem',
  'sequences_monotone_bounded',
  'series_absolute_convergence',
  'convergence_divergence_integrals',
] as const;

describe('learn route 404 guards', () => {
  it('lists the five calc-1 syllabus concepts in the curriculum catalog or title table', () => {
    for (const id of CATALOG_ONLY_IDS) {
      expect(
        isConceptInCurriculumCatalog(id) || isCatalogTitleConcept(id),
        `${id} should be catalog-listed`,
      ).toBe(true);
      const titles = resolveConceptTitles(id);
      expect(titles.title_en.length).toBeGreaterThan(0);
      expect(titles.title_he).toBeTruthy();
    }
  });

  it('resolves category for calc-1 syllabus concepts', () => {
    for (const id of CATALOG_ONLY_IDS) {
      expect(findCategoryIdForConcept(id)).toBe('calculus_1');
    }
  });

  it('maps calc-1 syllabus concepts to /learn/calculus_1/concept/... hrefs', () => {
    for (const id of CATALOG_ONLY_IDS) {
      expect(resolveLegacyLessonLearnHref(id)).toBe(`/learn/calculus_1/concept/${id}`);
    }
  });

  it('maps an indexed authored lesson to a learn concept href', () => {
    const href = resolveLegacyLessonLearnHref('absolute_extrema');
    expect(href).toMatch(/^\/learn\/[^/]+\/concept\/absolute_extrema$/);
  });
});
