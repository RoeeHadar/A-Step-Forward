/**
 * Profile-driven diagnostic orchestration — goal-path probes, adaptive picks, agent summary.
 */
import 'server-only';

import { buildLearningPlan } from '@/lib/learning-plan';
import {
  type DiagnosticSessionPayload,
  type DiagnosticSummary,
  type ValidationSlot,
  applyDiagnosticResponse,
  answeredItemIds,
  answeredStemKeys,
  buildDiagnosticSummary,
  currentValidationSlot,
  diagnosticAnsweredCount,
  emptyDiagnosticSession,
  isDiagnosticSessionComplete,
  MIN_DIAGNOSTIC_ANSWERS,
  orderProbeConcepts,
  parseDiagnosticSessionPayload,
  resolveCurrentDiagnosticItem,
  selfScoreTier,
  setCurrentDiagnosticItem,
  targetDifficultyForSlot,
  type DiagnosticServedItem,
} from '@/lib/diagnostic-plan';
import { pickDiagnosticItemFromLessonBank } from '@/lib/diagnostic-lesson-bank';
import type { DiagnosticSlotKind } from '@/lib/diagnostic-stem-filter';
import { DIAGNOSTIC_QUESTIONS_PER_SESSION } from '@/lib/diagnostic-start';
import {
  type DiagnosticItem,
  type LearnerProfileRow,
  abandonActiveDiagnosticSessions,
  ensureDiagnosticItemRow,
  fetchDiagnosticItemForConcept,
  findActiveDiagnosticSession,
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

const SLOT_KINDS: DiagnosticSlotKind[] = ['basic', 'medium', 'hard', 'verbal', 'edge'];

function toServedItem(item: DiagnosticItem): DiagnosticServedItem {
  return {
    id: item.id,
    topic: item.topic,
    subject: item.subject,
    difficulty: item.difficulty,
    stem: item.stem,
    options: item.options,
    stem_he: item.stem_he,
    options_he: item.options_he,
  };
}

function servedToDiagnosticItem(served: DiagnosticServedItem): DiagnosticItem {
  return {
    ...served,
    source_concept: served.topic,
    explanation_he: null,
  };
}

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

  const selfRated = Object.keys(profile.self_scores ?? {})
    .map((id) => canonicalConceptId(id) ?? id)
    .filter((id) => id.length > 0 && conceptAllowedForProfile(id, profile));

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

  let probeConcepts = orderProbeConcepts([...selfRated, ...pathIds], profile.self_scores, 12);
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

function slotForSelfScore(conceptId: string, score: number): ValidationSlot {
  const tier = selfScoreTier(score);
  if (tier === 'weak') {
    return { concept_id: conceptId, target_difficulty: 3, slot_kind: 'basic' };
  }
  if (tier === 'ok') {
    return { concept_id: conceptId, target_difficulty: 5, slot_kind: 'medium' };
  }
  return { concept_id: conceptId, target_difficulty: 8, slot_kind: 'hard' };
}

/** Only queue concepts that have at least one servable MCQ (Neon or lesson bank). */
export async function buildAvailableValidationQueue(
  probeConcepts: string[],
  selfScores: Record<string, number> | null,
  profile: LearnerProfileRow,
  total = DIAGNOSTIC_QUESTIONS_PER_SESSION,
): Promise<ValidationSlot[]> {
  const candidates = orderProbeConcepts(
    probeConcepts,
    selfScores,
    Math.max(total * 3, 12),
  );
  const scratch = emptyDiagnosticSession(null, candidates, []);
  const slots: ValidationSlot[] = [];

  for (const conceptId of candidates) {
    if (slots.length >= total) break;
    if (!conceptAllowedForProfile(conceptId, profile)) continue;
    const score = selfScores?.[conceptId] ?? 5;
    const slot = slotForSelfScore(conceptId, score);
    const item = await tryPickForSlot(scratch, slot, profile);
    if (item) slots.push(slot);
  }

  return slots;
}

async function tryPickForSlot(
  state: DiagnosticSessionPayload,
  slot: ValidationSlot,
  profile: LearnerProfileRow,
): Promise<DiagnosticItem | null> {
  const selfScores = profile.self_scores ?? {};
  const targetDifficulty = targetDifficultyForSlot(state, slot, selfScores);
  const kindsToTry = [slot.slot_kind, ...SLOT_KINDS.filter((k) => k !== slot.slot_kind)];
  const excludeIds = answeredItemIds(state);
  const excludeStems = answeredStemKeys(state);

  for (const kind of kindsToTry) {
    const item = await fetchDiagnosticItemForConcept(
      slot.concept_id,
      profile,
      excludeIds,
      targetDifficulty,
      kind,
      excludeStems,
    );
    if (item) return item;

    const fromBank = pickDiagnosticItemFromLessonBank(
      slot.concept_id,
      profile,
      excludeIds,
      targetDifficulty,
      kind,
      excludeStems,
    );
    if (fromBank) return fromBank;
  }

  return null;
}

/** Skip slots with no available items; return the next servable question if any. */
export async function pickNextDiagnosticItem(
  state: DiagnosticSessionPayload,
  profile: LearnerProfileRow,
): Promise<{ item: DiagnosticItem | null; state: DiagnosticSessionPayload }> {
  let current = state;

  while (current.queue_index < current.validation_queue.length) {
    const slot = current.validation_queue[current.queue_index];
    if (!slot?.concept_id || !conceptAllowedForProfile(slot.concept_id, profile)) {
      current = { ...current, queue_index: current.queue_index + 1 };
      continue;
    }

    const item = await tryPickForSlot(current, slot, profile);
    if (item) {
      await ensureDiagnosticItemRow(item);
      return {
        item,
        state: setCurrentDiagnosticItem(current, toServedItem(item)),
      };
    }

    current = { ...current, queue_index: current.queue_index + 1 };
  }

  return { item: null, state: current };
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

  const validationQueue = await buildAvailableValidationQueue(
    probeConcepts,
    profile.self_scores,
    profile,
    DIAGNOSTIC_QUESTIONS_PER_SESSION,
  );
  if (validationQueue.length === 0) return null;

  const state = emptyDiagnosticSession(goalConceptId, probeConcepts, validationQueue);
  const picked = await pickNextDiagnosticItem(state, profile);
  if (!picked.item) return null;

  return { state: picked.state, firstItem: picked.item, profile };
}

function canFinalizeDiagnostic(state: DiagnosticSessionPayload): boolean {
  return diagnosticAnsweredCount(state) >= MIN_DIAGNOSTIC_ANSWERS;
}

/** Resume only when the learner has an unanswered question open (page refresh). */
export async function resumePendingDiagnosticQuestion(
  learnerId: string,
): Promise<{
  sessionId: string;
  state: DiagnosticSessionPayload;
  item: DiagnosticItem;
} | null> {
  const active = await findActiveDiagnosticSession(learnerId);
  if (!active) return null;

  const state = parseDiagnosticSessionPayload(active.results);
  if (!state) {
    await abandonActiveDiagnosticSessions(learnerId);
    return null;
  }

  const pending = resolveCurrentDiagnosticItem(state);
  if (!pending) {
    await abandonActiveDiagnosticSessions(learnerId);
    return null;
  }

  if (diagnosticAnsweredCount(state) >= state.validation_queue.length) {
    await abandonActiveDiagnosticSessions(learnerId);
    return null;
  }

  const item = servedToDiagnosticItem(pending);
  await ensureDiagnosticItemRow(item);
  return { sessionId: active.id, state, item };
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

  if (isDiagnosticSessionComplete(state)) {
    const summary = buildDiagnosticSummary(state);
    return { state, nextItem: null, complete: true, summary };
  }

  const picked = await pickNextDiagnosticItem(state, profile);

  if (!picked.item) {
    if (!canFinalizeDiagnostic(picked.state)) {
      return { state: picked.state, nextItem: null, complete: false, summary: null };
    }
    const summary = buildDiagnosticSummary(picked.state);
    return { state: picked.state, nextItem: null, complete: true, summary };
  }

  return { state: picked.state, nextItem: picked.item, complete: false, summary: null };
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

export function resolveDiagnosticItemFromSession(
  itemId: string,
  state: DiagnosticSessionPayload | null,
): DiagnosticItem | null {
  const served = state?.served_items?.[itemId];
  if (!served) return null;
  return servedToDiagnosticItem(served);
}

/** @internal test hook */
export { currentValidationSlot, tryPickForSlot as _tryPickForSlot };
