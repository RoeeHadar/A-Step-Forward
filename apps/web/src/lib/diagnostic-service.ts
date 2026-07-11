/**
 * Profile-driven diagnostic orchestration — goal-path probes, adaptive picks, agent summary.
 */
import 'server-only';

import { buildLearningPlan } from '@/lib/learning-plan';
import {
  type DiagnosticSessionPayload,
  type DiagnosticSummary,
  applyDiagnosticResponse,
  buildDiagnosticSummary,
  currentProbeConcept,
  emptyDiagnosticSession,
  orderProbeConcepts,
  parseDiagnosticSessionPayload,
  targetDifficultyForConcept,
} from '@/lib/diagnostic-plan';
import {
  type DiagnosticItem,
  type LearnerProfileRow,
  fetchDiagnosticItemForConcept,
  getConceptMastery,
  getLearnerProfile,
} from '@/lib/neon-db';
import {
  bootstrapConceptIdsForProfile,
  conceptAllowedForProfile,
  filterConceptIdsForProfile,
} from '@/lib/quiz-concept-filter';
import { resolveGoalConceptId } from '@/lib/plan-worklist';
import { canonicalConceptId } from '@/lib/plan-catalog';
import kg from '@/lib/kg-data.json';

interface KgConceptRow {
  id: string;
  subject: string;
  prerequisites: string[];
}

const kgConcepts: KgConceptRow[] = (kg as { concepts: KgConceptRow[] }).concepts;
const kgPrereqMap: Record<string, string[]> = (kg as { prereqMap: Record<string, string[]> }).prereqMap;

function pathConceptIdsPrereqsFirst(path: Array<{ concept_id: string; relation: string }>): string[] {
  const ids = path.filter((n) => n.relation !== 'self').map((n) => n.concept_id);
  const self = path.filter((n) => n.relation === 'self').map((n) => n.concept_id);
  const ordered = [...ids.reverse(), ...self];
  const memo = new Map<string, number>();
  const depth = (concept: string, visiting = new Set<string>()): number => {
    if (memo.has(concept)) return memo.get(concept)!;
    if (visiting.has(concept)) return 0;
    visiting.add(concept);
    const prereqs = kgPrereqMap[concept] ?? [];
    const d =
      prereqs.length === 0
        ? 0
        : Math.max(...prereqs.map((p) => depth(p, visiting))) + 1;
    memo.set(concept, d);
    return d;
  };
  const unique = [...new Set(ordered.map((id) => canonicalConceptId(id) ?? id))];
  return unique.sort((a, b) => depth(a) - depth(b));
}

export async function buildPersonalizedProbeConcepts(
  learnerId: string,
  profile: LearnerProfileRow,
): Promise<{ goalConceptId: string | null; probeConcepts: string[] }> {
  const mastery = await getConceptMastery(learnerId);
  const goalConceptId = resolveGoalConceptId(
    {
      subjects: profile.subjects,
      self_scores: profile.self_scores,
      personality_profile: profile.personality_profile,
    },
    mastery,
  );

  let pathIds: string[] = [];
  if (goalConceptId) {
    const plan = await buildLearningPlan({
      learnerId,
      goalConceptId,
      maxNodes: 14,
    }).catch(() => null);
    if (plan?.path?.length) {
      pathIds = pathConceptIdsPrereqsFirst(plan.path);
    }
  }

  if (pathIds.length === 0) {
    const subjects = profile.subjects?.length ? profile.subjects : ['math'];
    const subjectSet = new Set(subjects);
    pathIds = kgConcepts
      .filter((c) => subjectSet.has(c.subject) && c.prerequisites.length === 0)
      .map((c) => c.id);
  }

  let probeConcepts = orderProbeConcepts(pathIds, profile.self_scores, 12);
  probeConcepts = filterConceptIdsForProfile(probeConcepts, profile);

  if (probeConcepts.length < 4) {
    const bootstrap = filterConceptIdsForProfile(
      bootstrapConceptIdsForProfile(profile, 12),
      profile,
    );
    probeConcepts = [...new Set([...probeConcepts, ...bootstrap])].slice(0, 12);
  }

  return { goalConceptId, probeConcepts };
}

async function pickItemForState(
  state: DiagnosticSessionPayload,
  profile: LearnerProfileRow,
): Promise<DiagnosticItem | null> {
  const selfScores = profile.self_scores ?? {};
  const startIdx = state.concept_index;

  for (let offset = 0; offset < state.probe_concepts.length; offset++) {
    const idx = startIdx + offset;
    if (idx >= state.probe_concepts.length) break;
    const conceptId = state.probe_concepts[idx];
    if (!conceptId || !conceptAllowedForProfile(conceptId, profile)) continue;

    const targetDifficulty = targetDifficultyForConcept(state, conceptId, selfScores);
    const item = await fetchDiagnosticItemForConcept(
      conceptId,
      profile,
      state.asked_item_ids,
      targetDifficulty,
    );
    if (item) return item;
  }

  return null;
}

export async function initializeDiagnosticSession(
  learnerId: string,
): Promise<{
  state: DiagnosticSessionPayload;
  firstItem: DiagnosticItem;
  profile: LearnerProfileRow;
} | null> {
  const profile = await getLearnerProfile(learnerId);
  if (!profile) return null;

  const { goalConceptId, probeConcepts } = await buildPersonalizedProbeConcepts(
    learnerId,
    profile,
  );
  if (probeConcepts.length === 0) return null;

  const state = emptyDiagnosticSession(goalConceptId, probeConcepts);
  const firstItem = await pickItemForState(state, profile);
  if (!firstItem) return null;

  return { state, firstItem, profile };
}

export async function advanceDiagnosticSession(
  learnerId: string,
  priorState: DiagnosticSessionPayload,
  response: {
    item_id: string;
    topic: string;
    difficulty: number;
    correct: boolean;
    chosen: string;
  },
): Promise<{
  state: DiagnosticSessionPayload;
  nextItem: DiagnosticItem | null;
  complete: boolean;
  summary: DiagnosticSummary | null;
}> {
  const profile = await getLearnerProfile(learnerId);
  if (!profile) {
    throw new Error('Learner profile not found');
  }

  const state = applyDiagnosticResponse(priorState, response);
  const complete = state.responses.length >= 12 || state.concept_index >= state.probe_concepts.length;

  if (complete) {
    const summary = buildDiagnosticSummary(state);
    return { state, nextItem: null, complete: true, summary };
  }

  const nextItem = await pickItemForState(state, profile);
  if (!nextItem) {
    const summary = buildDiagnosticSummary(state);
    return { state, nextItem: null, complete: true, summary };
  }

  return { state, nextItem, complete: false, summary: null };
}

export function loadDiagnosticStateFromSession(
  results: Record<string, unknown> | null,
): DiagnosticSessionPayload | null {
  return parseDiagnosticSessionPayload(results);
}

export function diagnosticStateToResults(
  state: DiagnosticSessionPayload,
  summary?: DiagnosticSummary | null,
): Record<string, unknown> {
  return {
    ...state,
    ...(summary ? { summary } : {}),
  };
}

export function formatDiagnosticSummaryForAgents(
  summary: DiagnosticSummary | null | undefined,
  lang: 'en' | 'he' = 'en',
): string {
  if (!summary) return '';
  const brief = lang === 'he' ? summary.agent_brief_he : summary.agent_brief_en;
  const focus = summary.plan_focus_concepts.join(', ');
  return (
    `## Diagnostic calibration (use for pacing & plan)\n` +
    `${brief}\n` +
    `- Plan focus concepts: ${focus || 'n/a'}\n` +
    `- Weak: ${summary.weak_concepts.slice(0, 6).join(', ') || 'none'}\n` +
    `- Strong: ${summary.strong_concepts.slice(0, 4).join(', ') || 'none'}`
  );
}

/** @internal test hook */
export { currentProbeConcept, pickItemForState as _pickItemForState };
