/**
 * Unified concept ordering for weekly plan persistence (ADR-0008 PR1).
 * Delegates sequencing to buildLearningPlan(); neon-db handles calendar chunking.
 */
import 'server-only';
import kg from '@/lib/kg-data.json';
import crossEdges from '@/lib/kg-cross-edges.json';
import { buildLearningPlan } from '@/lib/learning-plan';
import { canonicalConceptId } from '@/lib/plan-catalog';
import {
  conceptMatchesSubjects,
  subjectSetForPlan,
} from '@/lib/concept-scope';

export const PLAN_SCHEMA_VERSION = 2;

/** Syllabus / lesson goal ids → KG node for backward BFS when absent from kg-data. */
const PLANNER_GOAL_KG_FALLBACK: Record<string, string> = {
  function_analysis_4pt: 'function_analysis_extrema',
  function_analysis_5pt: 'function_analysis_asymptotes',
  linear_programming_two_variables: 'functions_linear',
  calculus_intro_makhina: 'limits',
};

export const DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY: Record<string, string> = {
  bagrut_math_3: 'linear_programming_two_variables',
  bagrut_math_4: 'function_analysis_4pt',
  bagrut_math_5: 'function_analysis_5pt',
  bagrut_physics: 'newton_laws',
  calculus1: 'derivatives_intro',
  linear_algebra: 'la_matrices',
  university_prep: 'calculus_intro_makhina',
  makhina: 'calculus_intro_makhina',
};

const WEAK_THRESHOLD = 0.4;

interface KgConcept {
  id: string;
  subject: string;
  prerequisites: string[];
}

const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;
const kgPrereqMap: Record<string, string[]> = (kg as { prereqMap: Record<string, string[]> }).prereqMap;
const kgById: Record<string, KgConcept> = (kg as { byId: Record<string, KgConcept> }).byId;

interface CrossEdge {
  src: string;
  dst: string;
  relation: string;
}
const crossEdgesArr: CrossEdge[] = (crossEdges as { edges: CrossEdge[] }).edges;
const crossEdgesByDst = new Map<string, CrossEdge[]>();
for (const e of crossEdgesArr) {
  if (e.relation !== 'prereq' && e.relation !== 'generalizes' && e.relation !== 'applies_to') continue;
  const list = crossEdgesByDst.get(e.dst);
  if (list) list.push(e);
  else crossEdgesByDst.set(e.dst, [e]);
}

export interface PlanWorklistProfile {
  subjects: string[];
  self_scores: Record<string, number> | null;
  personality_profile: Record<string, unknown> | null;
}

export interface PlanWorklistOptions {
  priorityConcepts?: string[];
  prependConcepts?: string[];
  excludeConcepts?: string[];
  focusConceptsOnly?: boolean;
}

function goalKeyFromProfile(profile: PlanWorklistProfile): string | undefined {
  const key = (profile.personality_profile as { goal_key?: string } | null)?.goal_key;
  return typeof key === 'string' && key.trim() ? key.trim() : undefined;
}

function plannerGoalConceptId(raw: string): string | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const canonical = canonicalConceptId(trimmed);
  if (canonical && kgById[canonical]) return canonical;
  if (kgById[trimmed]) return trimmed;
  const fallback = PLANNER_GOAL_KG_FALLBACK[trimmed];
  if (fallback && kgById[fallback]) return fallback;
  const aliasFallback = canonicalConceptId(PLANNER_GOAL_KG_FALLBACK[trimmed] ?? '');
  if (aliasFallback && kgById[aliasFallback]) return aliasFallback;
  return canonical;
}

/** Resolve the goal concept used for buildLearningPlan backward BFS. */
export function resolveGoalConceptId(
  profile: PlanWorklistProfile,
  mastery: Record<string, number>,
  options: PlanWorklistOptions = {},
): string | null {
  const priority = options.priorityConcepts ?? [];
  if (priority.length > 0) {
    const resolved = plannerGoalConceptId(priority[0]!);
    if (resolved) return resolved;
  }

  const prepend = options.prependConcepts ?? [];
  if (prepend.length > 0) {
    const resolved = plannerGoalConceptId(prepend[0]!);
    if (resolved) return resolved;
  }

  const goalKey = goalKeyFromProfile(profile);
  if (goalKey) {
    const defaultGoal = DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY[goalKey];
    if (defaultGoal) {
      const resolved = plannerGoalConceptId(defaultGoal);
      if (resolved) return resolved;
    }
  }

  let weakest: { id: string; score: number } | null = null;
  for (const [conceptId, score] of Object.entries(mastery)) {
    const canonical = canonicalConceptId(conceptId);
    if (!canonical || !conceptMatchesSubjects(canonical, profile.subjects)) continue;
    if (score >= WEAK_THRESHOLD) continue;
    if (!weakest || score < weakest.score) weakest = { id: canonical, score };
  }
  return weakest?.id ?? null;
}

function depthOf(concept: string, universe: Set<string>, memo: Map<string, number>): number {
  if (memo.has(concept)) return memo.get(concept)!;
  const prereqs = (kgPrereqMap[concept] ?? []).filter((p) => universe.has(p));
  if (prereqs.length === 0) {
    memo.set(concept, 0);
    return 0;
  }
  memo.set(concept, 0);
  const d = Math.max(...prereqs.map((p) => depthOf(p, universe, memo))) + 1;
  memo.set(concept, d);
  return d;
}

function collectWorklistFallback(
  mastery: Record<string, number>,
  selfScores: Record<string, number> | null,
  subjects: string[],
): Set<string> {
  const worklist = new Set<string>();
  for (const [c, score] of Object.entries(mastery)) {
    const canonical = canonicalConceptId(c);
    if (canonical && conceptMatchesSubjects(canonical, subjects) && score < WEAK_THRESHOLD) {
      worklist.add(canonical);
    }
  }

  const expandPrereqs = (concept: string) => {
    for (const prereq of kgPrereqMap[concept] ?? []) {
      const canonical = canonicalConceptId(prereq);
      if (
        canonical &&
        conceptMatchesSubjects(canonical, subjects) &&
        (mastery[canonical] ?? mastery[prereq] ?? 0.5) < WEAK_THRESHOLD
      ) {
        worklist.add(canonical);
      }
    }
    for (const edge of crossEdgesByDst.get(concept) ?? []) {
      const canonical = canonicalConceptId(edge.src);
      if (
        canonical &&
        conceptMatchesSubjects(canonical, subjects) &&
        (mastery[canonical] ?? 0.5) < WEAK_THRESHOLD
      ) {
        worklist.add(canonical);
      }
    }
  };

  for (const c of [...worklist]) expandPrereqs(c);

  if (worklist.size === 0) {
    if (selfScores) {
      for (const c of Object.keys(selfScores)) {
        const canonical = canonicalConceptId(c);
        if (canonical && conceptMatchesSubjects(canonical, subjects)) worklist.add(canonical);
      }
    } else if (subjects.length > 0) {
      const subjectSet = subjectSetForPlan(subjects);
      const roots = kgConcepts.filter(
        (c) =>
          (subjectSet.size === 0 || subjectSet.has(c.subject)) &&
          c.prerequisites.length === 0,
      );
      for (const r of roots.slice(0, 5)) worklist.add(r.id);
    }
  }
  return worklist;
}

function sortFallbackWorklist(
  worklist: Set<string>,
  priorityConcepts: string[],
): string[] {
  const memo = new Map<string, number>();
  const priority = new Set(priorityConcepts);
  return [...worklist].sort((a, b) => {
    const pa = priority.has(a) ? 0 : 1;
    const pb = priority.has(b) ? 0 : 1;
    if (pa !== pb) return pa - pb;
    return depthOf(a, worklist, memo) - depthOf(b, worklist, memo);
  });
}

function extractPathConceptIds(path: Array<{ concept_id: string; relation: string }>): string[] {
  const nonSelf = path.filter((n) => n.relation !== 'self').map((n) => n.concept_id);
  const self = path.filter((n) => n.relation === 'self').map((n) => n.concept_id);
  return [...nonSelf, ...self];
}

function mergeConceptOrder(args: {
  prependConcepts: string[];
  priorityConcepts: string[];
  pathIds: string[];
  excludeConcepts: string[];
  focusConceptsOnly: boolean;
}): string[] {
  const exclude = new Set(args.excludeConcepts);
  const focusSet =
    args.focusConceptsOnly && (args.prependConcepts.length > 0 || args.priorityConcepts.length > 0)
      ? new Set([...args.prependConcepts, ...args.priorityConcepts])
      : null;

  const out: string[] = [];
  const seen = new Set<string>();

  const add = (raw: string) => {
    const id = canonicalConceptId(raw) ?? raw;
    if (!id || seen.has(id) || exclude.has(id)) return;
    if (focusSet && !focusSet.has(id)) return;
    seen.add(id);
    out.push(id);
  };

  for (const id of args.prependConcepts) add(id);
  for (const id of args.priorityConcepts) add(id);
  for (const id of args.pathIds) add(id);

  return out;
}

/**
 * In-memory concept ordering for onboarding / first plan — skips BFS + Neon
 * hydration (`buildLearningPlan`) so the plan row can persist in seconds.
 */
export function buildFastPlanConceptOrder(args: {
  profile: PlanWorklistProfile;
  mastery: Record<string, number>;
  options?: PlanWorklistOptions;
}): string[] {
  const options = args.options ?? {};
  const prependConcepts = options.prependConcepts ?? [];
  const priorityConcepts = options.priorityConcepts ?? [];
  const excludeConcepts = options.excludeConcepts ?? [];
  const focusConceptsOnly = options.focusConceptsOnly === true;

  const worklist = collectWorklistFallback(
    args.mastery,
    args.profile.self_scores,
    args.profile.subjects,
  );
  for (const c of prependConcepts) worklist.add(c);
  for (const c of priorityConcepts) worklist.add(c);
  for (const c of excludeConcepts) worklist.delete(c);

  if (worklist.size === 0) {
    const retry = collectWorklistFallback(
      args.mastery,
      args.profile.self_scores,
      args.profile.subjects,
    );
    for (const c of retry) worklist.add(c);
  }

  const pathIds = sortFallbackWorklist(worklist, priorityConcepts);

  const ordered = mergeConceptOrder({
    prependConcepts,
    priorityConcepts,
    pathIds,
    excludeConcepts,
    focusConceptsOnly,
  });

  if (ordered.length === 0 && args.profile.self_scores) {
    for (const raw of Object.keys(args.profile.self_scores)) {
      const id = canonicalConceptId(raw);
      if (id && conceptMatchesSubjects(id, args.profile.subjects)) ordered.push(id);
    }
  }

  if (ordered.length === 0) {
    ordered.push(...bootstrapConceptsForProfile(args.profile, args.mastery));
  }

  return ordered;
}

/** Guaranteed non-empty concept list from goal + syllabus roots + self_scores keys. */
export function bootstrapConceptsForProfile(
  profile: PlanWorklistProfile,
  mastery: Record<string, number>,
): string[] {
  const out: string[] = [];
  const goalId = resolveGoalConceptId(profile, mastery, {});
  if (goalId) out.push(goalId);

  if (profile.self_scores) {
    for (const raw of Object.keys(profile.self_scores)) {
      const id = canonicalConceptId(raw);
      if (id && conceptMatchesSubjects(id, profile.subjects)) out.push(id);
    }
  }

  const subjectSet = subjectSetForPlan(profile.subjects);
  const roots = kgConcepts.filter(
    (c) =>
      (subjectSet.size === 0 || subjectSet.has(c.subject)) &&
      c.prerequisites.length === 0,
  );
  for (const r of roots.slice(0, 8)) out.push(r.id);

  const seen = new Set<string>();
  return out.filter((id) => {
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

/**
 * Ordered concept ids for weekly plan chunking — same BFS engine as chat/API.
 */
export async function buildUnifiedPlanConceptOrder(args: {
  learnerId: string;
  profile: PlanWorklistProfile;
  mastery: Record<string, number>;
  options?: PlanWorklistOptions;
  numWeeks: number;
}): Promise<string[]> {
  const options = args.options ?? {};
  const prependConcepts = options.prependConcepts ?? [];
  const priorityConcepts = options.priorityConcepts ?? [];
  const excludeConcepts = options.excludeConcepts ?? [];
  const focusConceptsOnly = options.focusConceptsOnly === true;

  const goalConceptId = resolveGoalConceptId(args.profile, args.mastery, options);
  const maxNodes = Math.max(24, args.numWeeks * 4);

  let pathIds: string[] = [];

  if (goalConceptId) {
    const plan = await buildLearningPlan({
      learnerId: args.learnerId,
      goalConceptId,
      maxNodes,
    });
    if (plan?.path?.length) {
      pathIds = extractPathConceptIds(plan.path);
    }
  }

  if (pathIds.length === 0) {
    const worklist = collectWorklistFallback(
      args.mastery,
      args.profile.self_scores,
      args.profile.subjects,
    );
    for (const c of prependConcepts) worklist.add(c);
    for (const c of priorityConcepts) worklist.add(c);
    for (const c of excludeConcepts) worklist.delete(c);
    if (worklist.size === 0) {
      const retry = collectWorklistFallback(
        args.mastery,
        args.profile.self_scores,
        args.profile.subjects,
      );
      for (const c of retry) worklist.add(c);
    }
    pathIds = sortFallbackWorklist(worklist, priorityConcepts);
  }

  let ordered = mergeConceptOrder({
    prependConcepts,
    priorityConcepts,
    pathIds,
    excludeConcepts,
    focusConceptsOnly,
  });

  if (ordered.length === 0) {
    const worklist = collectWorklistFallback(
      args.mastery,
      args.profile.self_scores,
      args.profile.subjects,
    );
    pathIds = sortFallbackWorklist(worklist, priorityConcepts);
    ordered = mergeConceptOrder({
      prependConcepts,
      priorityConcepts,
      pathIds,
      excludeConcepts,
      focusConceptsOnly,
    });
  }

  return ordered;
}
