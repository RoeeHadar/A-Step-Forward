import { describe, expect, it } from 'vitest';
import { CURRICULUM_CATEGORIES } from './curriculum-categories';
import { pickConceptTitle, resolveConceptTitles } from './concept-display-names';

function allCatalogConceptIds(): string[] {
  const ids = new Set<string>();
  for (const cat of CURRICULUM_CATEGORIES) {
    for (const id of cat.concept_ids) ids.add(id);
    for (const sec of cat.sections ?? []) {
      for (const id of sec.concept_ids ?? []) ids.add(id);
    }
  }
  return [...ids].sort();
}

describe('concept-display-names', () => {
  it('every curriculum catalog id has a Hebrew title for Learn UI', () => {
    const missing: string[] = [];
    for (const id of allCatalogConceptIds()) {
      const titles = resolveConceptTitles(id);
      const he = pickConceptTitle(titles, 'he');
      if (!/[\u0590-\u05FF]/.test(he)) {
        missing.push(`${id} → "${he}"`);
      }
    }
    expect(missing, `Missing Hebrew titles:\n${missing.join('\n')}`).toEqual([]);
  });

  it('calc1 integration section has no duplicate Hebrew card titles', () => {
    const calc1 = CURRICULUM_CATEGORIES.find((c) => c.id === 'calculus_1');
    const section = calc1?.sections?.find((s) => s.id === 'integration_techniques_calc1');
    expect(section).toBeTruthy();
    const titles = (section!.concept_ids ?? []).map((id) =>
      pickConceptTitle(resolveConceptTitles(id), 'he'),
    );
    const dupes = titles.filter((t, i) => titles.indexOf(t) !== i);
    expect(dupes).toEqual([]);
  });

  it('uses the learner points_group variant title when available', () => {
    const base = resolveConceptTitles('quadrilaterals');
    const fivePt = resolveConceptTitles('quadrilaterals', null, '5pt');
    expect(base.title_he).toContain('3');
    expect(fivePt.title_he).toContain('5');
    expect(fivePt.title_he).not.toBe(base.title_he);
  });
});
