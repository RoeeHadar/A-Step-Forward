/**
 * Server-authoritative next-step selection for pressure turns (ADR-0012).
 */
export interface NextStepCandidate {
  conceptId: string;
  nameHe?: string | null;
  nameEn?: string | null;
  mastery?: number | null;
}

export interface NextStepPick {
  conceptId: string;
  labelHe: string;
  labelEn: string;
}

/**
 * Priority: lowest mastery among active-week concepts → first active → planner path[0].
 */
export function pickPressureNextStep(opts: {
  activeWeekConcepts?: NextStepCandidate[];
  plannerPathIds?: string[];
  conceptTitles?: Record<string, { he?: string | null; en?: string | null }>;
}): NextStepPick | null {
  const active = opts.activeWeekConcepts ?? [];
  if (active.length > 0) {
    const ranked = [...active].sort((a, b) => {
      const ma = typeof a.mastery === 'number' ? a.mastery : 1;
      const mb = typeof b.mastery === 'number' ? b.mastery : 1;
      return ma - mb;
    });
    const top = ranked[0]!;
    return {
      conceptId: top.conceptId,
      labelHe: top.nameHe || top.nameEn || top.conceptId,
      labelEn: top.nameEn || top.nameHe || top.conceptId,
    };
  }
  const path0 = opts.plannerPathIds?.[0];
  if (path0) {
    const titles = opts.conceptTitles?.[path0];
    return {
      conceptId: path0,
      labelHe: titles?.he || titles?.en || path0,
      labelEn: titles?.en || titles?.he || path0,
    };
  }
  return null;
}
