import 'server-only';

import type { LearnerProfileRow } from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';

interface KgConcept {
  id: string;
  subject: string;
  points_levels?: string[];
  prerequisites: string[];
}

const kgConcepts = (kg as unknown as { concepts: KgConcept[] }).concepts;
const kgById: Record<string, KgConcept> =
  (kg as unknown as { byId: Record<string, KgConcept> }).byId;

/** Mirror of /app/quiz allowedLevels — keeps server-side picks aligned with UI. */
export function allowedLevelsForProfile(
  pointsGroup: string | null | undefined,
  subjects?: string[] | null,
): Set<string> {
  let levels: Set<string>;
  switch (pointsGroup) {
    case '3pt':
      levels = new Set(['3pt']);
      break;
    case '4pt':
      levels = new Set(['3pt', '4pt']);
      break;
    case '5pt':
      levels = new Set(['3pt', '4pt', '5pt']);
      break;
    case 'hs_physics':
      levels = new Set(['hs_physics', '3pt', '4pt']);
      break;
    case 'calc1':
    case 'la':
    case 'physics1':
      levels = new Set(['3pt', '4pt', '5pt', 'calc1', 'la', 'hs_physics']);
      break;
    default:
      levels = new Set();
  }
  if (subjects?.includes('physics')) {
    levels.add('hs_physics');
  }
  return levels;
}

export function conceptAllowedForProfile(
  conceptId: string,
  profile: LearnerProfileRow | null,
): boolean {
  const c = kgById[conceptId];
  if (!c) return false;
  const subjects = profile?.subjects ?? [];
  if (subjects.length > 0 && !subjects.includes(c.subject)) return false;
  const allowed = allowedLevelsForProfile(profile?.points_group, subjects);
  if (allowed.size === 0) return true;
  const cLevels = c.points_levels ?? [];
  return cLevels.length === 0 || cLevels.some((l) => allowed.has(l));
}

export function filterConceptIdsForProfile(
  ids: string[],
  profile: LearnerProfileRow | null,
): string[] {
  return ids.filter((id) => conceptAllowedForProfile(id, profile));
}

export function bootstrapConceptIdsForProfile(
  profile: LearnerProfileRow | null,
  limit = 6,
): string[] {
  const subjects =
    profile?.subjects && profile.subjects.length > 0 ? profile.subjects : ['math'];
  const subjectSet = new Set(subjects.map((s) => s.toLowerCase()));
  const roots = kgConcepts
    .filter((c) => subjectSet.has(c.subject) && c.prerequisites.length === 0)
    .map((c) => c.id);
  const candidates = roots.length > 0 ? roots : kgConcepts.map((c) => c.id);
  return filterConceptIdsForProfile(candidates, profile).slice(0, limit);
}
