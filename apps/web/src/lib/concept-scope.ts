/**
 * Goal- and plan-scoped concept filtering for mastery signals, memory UI, and chat context.
 */
import kg from './kg-data.json';
import lessonsIndex from './lessons-index.generated.json';
import { resolveConceptAlias } from './concept-aliases';
import { canonicalConceptId } from './plan-catalog';

interface KgConcept {
  id: string;
  subject: string;
}

interface LessonIndexEntry {
  id: string;
  subject?: string;
}

const kgById: Record<string, KgConcept> = (kg as { byId: Record<string, KgConcept> }).byId;
const lessonsById = new Map(
  (lessonsIndex as LessonIndexEntry[]).map((l) => [l.id, l]),
);

export function subjectSetForPlan(subjects: string[]): Set<string> {
  const out = new Set<string>();
  for (const raw of subjects) {
    const s = raw.toLowerCase();
    if (s === 'physics' || s.includes('physics') || s === 'bagrut_physics' || s === 'hs_physics') {
      out.add('physics');
    }
    if (
      s === 'math' ||
      s.includes('math') ||
      s.includes('calculus') ||
      s.includes('algebra') ||
      s === 'makhina' ||
      s === 'university_prep'
    ) {
      out.add('math');
    }
  }
  return out;
}

/** Resolve KG or lesson-index subject for a mastery/plan concept id. */
export function resolveConceptSubject(conceptId: string): string | null {
  const id = conceptId.trim();
  if (!id) return null;
  const alias = resolveConceptAlias(id);
  const kgInfo = kgById[id] ?? kgById[alias];
  if (kgInfo?.subject) return kgInfo.subject;
  const lesson = lessonsById.get(id) ?? lessonsById.get(alias);
  if (lesson?.subject) return lesson.subject;
  const canonical = canonicalConceptId(id);
  if (canonical && canonical !== id) {
    return resolveConceptSubject(canonical);
  }
  return null;
}

export function conceptMatchesSubjects(conceptId: string, subjects: string[]): boolean {
  const allowed = subjectSetForPlan(subjects);
  if (allowed.size === 0) return true;
  const subject = resolveConceptSubject(conceptId);
  return subject ? allowed.has(subject) : false;
}

function conceptIdVariants(conceptId: string): Set<string> {
  const out = new Set<string>();
  const id = conceptId.trim();
  if (!id) return out;
  out.add(id);
  out.add(resolveConceptAlias(id));
  const canonical = canonicalConceptId(id);
  if (canonical) out.add(canonical);
  return out;
}

/** True when a mastery row belongs to a concept on the learner's active plan. */
export function conceptInPlanScope(
  conceptId: string,
  planConceptIds: Iterable<string>,
): boolean {
  const variants = conceptIdVariants(conceptId);
  for (const pid of planConceptIds) {
    for (const other of conceptIdVariants(pid)) {
      if (variants.has(other)) return true;
    }
  }
  return false;
}

/** Mastery signals shown to learners should follow the plan when one exists. */
export function masterySignalInScope(
  conceptId: string,
  options: { subjects: string[]; planConceptIds: Set<string> },
): boolean {
  if (options.planConceptIds.size > 0) {
    return conceptInPlanScope(conceptId, options.planConceptIds);
  }
  return conceptMatchesSubjects(conceptId, options.subjects);
}
