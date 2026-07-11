/**
 * Pure diagnostic planning logic (no I/O) — profile-goal-path probes + agent summary.
 */
import { diagnosticStemKey } from '@/lib/diagnostic-stem-dedupe';
import kg from '@/lib/kg-data.json';
import { canonicalConceptId } from '@/lib/plan-catalog';
import { DIAGNOSTIC_QUESTIONS_PER_SESSION } from '@/lib/diagnostic-start';

export const DIAGNOSTIC_SESSION_VERSION = 4;

/** Minimum answers before early completion when the question bank runs dry. */
export const MIN_DIAGNOSTIC_ANSWERS = 1;

export type ValidationSlotKind = 'basic' | 'medium' | 'hard' | 'verbal' | 'edge';

export interface ValidationSlot {
  concept_id: string;
  target_difficulty: number;
  slot_kind: ValidationSlotKind;
}

export interface DiagnosticResponse {
  item_id: string;
  topic: string;
  difficulty: number;
  correct: boolean;
  chosen: string;
}

export interface DiagnosticSessionPayload {
  version: typeof DIAGNOSTIC_SESSION_VERSION;
  goal_concept_id: string | null;
  probe_concepts: string[];
  /** Fixed 12-slot validation plan — two probes per self-scored concept tier. */
  validation_queue: ValidationSlot[];
  queue_index: number;
  responses: DiagnosticResponse[];
  asked_item_ids: string[];
  /** Stem fingerprints — dedupes Neon UUID vs lesson-bank hash for the same MCQ. */
  asked_stem_keys: string[];
  /** Items served from the lesson bank (not in Neon) keyed by stable id. */
  served_items?: Record<string, DiagnosticServedItem>;
  /** Item shown to the learner awaiting an answer (not yet in responses). */
  current_item_id: string | null;
  /** Per-topic difficulty for CAT-style adjustment within a concept. */
  difficulty_by_topic: Record<string, number>;
}

/** Serializable subset of DiagnosticItem stored on the session for bank-served MCQs. */
export interface DiagnosticServedItem {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  stem: string;
  options: { choices: string[]; correct: string };
  stem_he: string | null;
  options_he: { choices: string[]; correct: string } | null;
}

export interface DiagnosticConceptProbe {
  concept_id: string;
  name: string;
  name_he: string | null;
  questions: number;
  correct: number;
  estimated_mastery: number;
}

export interface DiagnosticSummary {
  completed_at: string;
  goal_concept_id: string | null;
  goal_name: string | null;
  goal_name_he: string | null;
  probed: DiagnosticConceptProbe[];
  weak_concepts: string[];
  strong_concepts: string[];
  plan_focus_concepts: string[];
  agent_brief_en: string;
  agent_brief_he: string;
}

interface KgConceptLite {
  id: string;
  name: string;
  name_he: string | null;
}

const kgById: Record<string, KgConceptLite> = (kg as { byId: Record<string, KgConceptLite> }).byId;

export function selfScoreTier(score: number): 'weak' | 'ok' | 'strong' {
  if (score <= 4) return 'weak';
  if (score <= 7) return 'ok';
  return 'strong';
}

/** Validation difficulty from claimed self-score: weak→basic, ok→medium, strong→hard. */
export function validationDifficultyForSelfScore(
  selfScore: number | undefined,
  slotOffset = 0,
): number {
  const score = selfScore ?? 5;
  const tier = selfScoreTier(score);
  if (tier === 'weak') return slotOffset === 0 ? 3 : 4;
  if (tier === 'ok') return slotOffset === 0 ? 5 : 6;
  return slotOffset === 0 ? 8 : 9;
}

/** @deprecated use validationDifficultyForSelfScore */
export function selfScoreToDifficulty(selfScore: number | undefined): number {
  return validationDifficultyForSelfScore(selfScore, 0);
}

export function buildValidationQueue(
  probeConcepts: string[],
  selfScores: Record<string, number> | null,
  total = DIAGNOSTIC_QUESTIONS_PER_SESSION,
): ValidationSlot[] {
  const conceptIds = orderProbeConcepts(
    [...Object.keys(selfScores ?? {}), ...probeConcepts],
    selfScores,
    total,
  );
  const slots: ValidationSlot[] = [];

  for (const conceptId of conceptIds) {
    if (slots.length >= total) break;
    const score = selfScores?.[conceptId] ?? 5;
    const tier = selfScoreTier(score);

    if (tier === 'weak') {
      slots.push({ concept_id: conceptId, target_difficulty: 3, slot_kind: 'basic' });
    } else if (tier === 'ok') {
      slots.push({ concept_id: conceptId, target_difficulty: 5, slot_kind: 'medium' });
    } else {
      slots.push({ concept_id: conceptId, target_difficulty: 8, slot_kind: 'hard' });
    }
  }

  let verbalIdx = 2;
  while (verbalIdx < slots.length && slots.length <= total) {
    const prev = slots[verbalIdx]!;
    slots[verbalIdx] = {
      concept_id: prev.concept_id,
      target_difficulty: Math.min(prev.target_difficulty, 5),
      slot_kind: 'verbal',
    };
    verbalIdx += 3;
  }

  return slots.slice(0, total);
}

export function emptyDiagnosticSession(
  goalConceptId: string | null,
  probeConcepts: string[],
  validationQueue: ValidationSlot[],
): DiagnosticSessionPayload {
  return {
    version: DIAGNOSTIC_SESSION_VERSION,
    goal_concept_id: goalConceptId,
    probe_concepts: probeConcepts,
    validation_queue: validationQueue,
    queue_index: 0,
    responses: [],
    asked_item_ids: [],
    asked_stem_keys: [],
    served_items: {},
    current_item_id: null,
    difficulty_by_topic: {},
  };
}

/** Item + stem keys from submitted answers only (not the pending question). */
export function answeredItemIds(state: DiagnosticSessionPayload): string[] {
  return state.responses.map((r) => r.item_id);
}

export function answeredStemKeys(state: DiagnosticSessionPayload): string[] {
  return state.responses
    .map((r) => state.served_items?.[r.item_id]?.stem)
    .filter((s): s is string => Boolean(s?.trim()))
    .map((s) => diagnosticStemKey(s));
}

export function setCurrentDiagnosticItem(
  state: DiagnosticSessionPayload,
  item: DiagnosticServedItem,
): DiagnosticSessionPayload {
  return {
    ...rememberServedItem(state, item),
    current_item_id: item.id,
  };
}

export function resolveCurrentDiagnosticItem(
  state: DiagnosticSessionPayload,
): DiagnosticServedItem | null {
  const id = state.current_item_id;
  if (!id || state.responses.some((r) => r.item_id === id)) return null;
  return state.served_items?.[id] ?? null;
}

export function reserveAskedItem(
  state: DiagnosticSessionPayload,
  item: { id: string; stem: string },
): DiagnosticSessionPayload {
  const stemKey = diagnosticStemKey(item.stem);
  const ids = state.asked_item_ids.includes(item.id)
    ? state.asked_item_ids
    : [...state.asked_item_ids, item.id];
  const stems = (state.asked_stem_keys ?? []).includes(stemKey)
    ? state.asked_stem_keys ?? []
    : [...(state.asked_stem_keys ?? []), stemKey];
  return { ...state, asked_item_ids: ids, asked_stem_keys: stems };
}

export function rememberServedItem(
  state: DiagnosticSessionPayload,
  item: DiagnosticServedItem,
): DiagnosticSessionPayload {
  return {
    ...state,
    served_items: { ...(state.served_items ?? {}), [item.id]: item },
  };
}

export function nextCatDifficulty(current: number, correct: boolean): number {
  const d = Number(current) || 5;
  if (correct) return Math.min(9, Math.round((d + 1) * 10) / 10);
  return Math.max(2, Math.round((d - 1.5) * 10) / 10);
}

/**
 * Order concepts to probe: onboarding weak self-scores first, then goal-path
 * prerequisites (roots → goal), deduped.
 */
export function orderProbeConcepts(
  pathConceptIds: string[],
  selfScores: Record<string, number> | null,
  maxConcepts = 12,
): string[] {
  const pathOrder = new Map<string, number>();
  pathConceptIds.forEach((id, i) => {
    const c = canonicalConceptId(id) ?? id;
    if (!pathOrder.has(c)) pathOrder.set(c, i);
  });

  const selfWeak = Object.entries(selfScores ?? {})
    .filter(([, score]) => score <= 5)
    .sort((a, b) => a[1] - b[1])
    .map(([id]) => canonicalConceptId(id) ?? id)
    .filter((id) => id.length > 0);

  const selfStrong = Object.entries(selfScores ?? {})
    .filter(([, score]) => score >= 8)
    .sort((a, b) => b[1] - a[1])
    .map(([id]) => canonicalConceptId(id) ?? id)
    .filter((id) => id.length > 0);

  const merged: string[] = [];
  const seen = new Set<string>();
  const add = (id: string) => {
    const c = canonicalConceptId(id) ?? id;
    if (!c || seen.has(c)) return;
    seen.add(c);
    merged.push(c);
  };

  for (const id of selfWeak) add(id);
  for (const id of pathConceptIds) add(id);
  for (const id of selfStrong) add(id);

  return merged.slice(0, maxConcepts);
}

export function currentValidationSlot(state: DiagnosticSessionPayload): ValidationSlot | null {
  if (state.queue_index >= state.validation_queue.length) return null;
  return state.validation_queue[state.queue_index] ?? null;
}

/** @deprecated use currentValidationSlot */
export function currentProbeConcept(state: DiagnosticSessionPayload): string | null {
  return currentValidationSlot(state)?.concept_id ?? null;
}

export function targetDifficultyForSlot(
  state: DiagnosticSessionPayload,
  slot: ValidationSlot,
  selfScores: Record<string, number> | null,
): number {
  const adapted = state.difficulty_by_topic[slot.concept_id];
  if (adapted != null) return adapted;
  const raw = selfScores?.[slot.concept_id];
  if (raw != null) return validationDifficultyForSelfScore(raw, slot.target_difficulty >= 8 ? 1 : 0);
  return slot.target_difficulty;
}

export function applyDiagnosticResponse(
  state: DiagnosticSessionPayload,
  response: DiagnosticResponse,
): DiagnosticSessionPayload {
  const topic = response.topic;
  const prevDiff = state.difficulty_by_topic[topic] ?? response.difficulty;
  const nextDiff = nextCatDifficulty(prevDiff, response.correct);

  const servedStem = state.served_items?.[response.item_id]?.stem;

  return {
    ...state,
    responses: [...state.responses, response],
    asked_item_ids: [...state.asked_item_ids, response.item_id],
    asked_stem_keys: servedStem
      ? [...new Set([...(state.asked_stem_keys ?? []), diagnosticStemKey(servedStem)])]
      : (state.asked_stem_keys ?? []),
    current_item_id: null,
    difficulty_by_topic: { ...state.difficulty_by_topic, [topic]: nextDiff },
    queue_index: Math.min(state.validation_queue.length, state.queue_index + 1),
  };
}

export function isDiagnosticSessionComplete(state: DiagnosticSessionPayload): boolean {
  if (state.responses.length >= state.validation_queue.length) return true;
  if (
    state.queue_index >= state.validation_queue.length &&
    state.responses.length >= MIN_DIAGNOSTIC_ANSWERS
  ) {
    return true;
  }
  return false;
}

export function estimateTopicMastery(responses: DiagnosticResponse[], topic: string): number {
  const forTopic = responses.filter((r) => r.topic === topic);
  if (forTopic.length === 0) return 0.5;
  let num = 0;
  let den = 0;
  for (const r of forTopic) {
    num += r.difficulty * (r.correct ? 1 : 0);
    den += r.difficulty;
  }
  return den > 0 ? Math.round((num / den) * 1000) / 1000 : 0.5;
}

export function buildDiagnosticSummary(
  state: DiagnosticSessionPayload,
  completedAt = new Date(),
): DiagnosticSummary {
  const goal = state.goal_concept_id ? kgById[state.goal_concept_id] : null;
  const probedTopics = [...new Set(state.responses.map((r) => r.topic))];

  const probed: DiagnosticConceptProbe[] = probedTopics.map((concept_id) => {
    const meta = kgById[concept_id];
    const topicResponses = state.responses.filter((r) => r.topic === concept_id);
    const correct = topicResponses.filter((r) => r.correct).length;
    return {
      concept_id,
      name: meta?.name ?? concept_id,
      name_he: meta?.name_he ?? null,
      questions: topicResponses.length,
      correct,
      estimated_mastery: estimateTopicMastery(state.responses, concept_id),
    };
  });

  probed.sort((a, b) => a.estimated_mastery - b.estimated_mastery);

  const weak_concepts = probed
    .filter((p) => p.estimated_mastery < 0.45)
    .map((p) => p.concept_id);
  const strong_concepts = probed
    .filter((p) => p.estimated_mastery >= 0.65 && p.questions > 0)
    .map((p) => p.concept_id);

  const plan_focus_concepts = weak_concepts.slice(0, 3);
  if (plan_focus_concepts.length === 0 && probed.length > 0) {
    plan_focus_concepts.push(probed[0]!.concept_id);
  }

  const weakLabels = probed
    .filter((p) => weak_concepts.includes(p.concept_id))
    .map((p) => p.name)
    .slice(0, 4);
  const strongLabels = probed
    .filter((p) => strong_concepts.includes(p.concept_id))
    .map((p) => p.name)
    .slice(0, 3);

  const goalLabel = goal?.name ?? 'your learning goal';
  const goalLabelHe = goal?.name_he ?? 'יעד הלמידה שלך';
  const qCount = state.responses.length;

  const agent_brief_en =
    `Diagnostic calibration (${qCount} validation questions) toward **${goalLabel}**. ` +
    `Each topic was tested at the difficulty matching your onboarding self-rating. ` +
    (weakLabels.length
      ? `Confirmed gaps — prioritize: ${weakLabels.join(', ')}. `
      : 'No major gaps surfaced — start at the next path step. ') +
    (strongLabels.length ? `Validated strengths: ${strongLabels.join(', ')}. ` : '') +
    `Week-1 focus: ${plan_focus_concepts.join(', ') || 'path default'}.`;

  const weakHe = probed
    .filter((p) => weak_concepts.includes(p.concept_id))
    .map((p) => p.name_he ?? p.name)
    .slice(0, 4);
  const strongHe = probed
    .filter((p) => strong_concepts.includes(p.concept_id))
    .map((p) => p.name_he ?? p.name)
    .slice(0, 3);

  const agent_brief_he =
    `כיול אבחון (${qCount} שאלות אימות) לכיוון **${goalLabelHe}**. ` +
    `כל נושא נבדק ברמת קושי שמתאימה לדירוג העצמי שלך. ` +
    (weakHe.length ? `פערים לאימות — להתמקד ב: ${weakHe.join(', ')}. ` : 'לא עלו פערים גדולים — אפשר להתקדם בנתיב. ') +
    (strongHe.length ? `חוזקות מאומתות: ${strongHe.join(', ')}. ` : '') +
    `מיקוד שבוע 1: ${plan_focus_concepts.join(', ') || 'ברירת מחדל מהנתיב'}.`;

  return {
    completed_at: completedAt.toISOString(),
    goal_concept_id: state.goal_concept_id,
    goal_name: goal?.name ?? null,
    goal_name_he: goal?.name_he ?? null,
    probed,
    weak_concepts,
    strong_concepts,
    plan_focus_concepts,
    agent_brief_en,
    agent_brief_he,
  };
}

export function parseDiagnosticSessionPayload(
  raw: Record<string, unknown> | null,
): DiagnosticSessionPayload | null {
  if (!raw || !Array.isArray(raw.probe_concepts)) return null;
  if (!Array.isArray(raw.validation_queue) || raw.validation_queue.length === 0) return null;

  const version = raw.version;
  if (version !== DIAGNOSTIC_SESSION_VERSION && version !== 3) return null;

  const validation_queue = (raw.validation_queue as ValidationSlot[]).filter(
    (s) => s && typeof s.concept_id === 'string' && typeof s.target_difficulty === 'number',
  );
  if (validation_queue.length === 0) return null;

  return {
    version: DIAGNOSTIC_SESSION_VERSION,
    goal_concept_id: typeof raw.goal_concept_id === 'string' ? raw.goal_concept_id : null,
    probe_concepts: raw.probe_concepts.filter((c): c is string => typeof c === 'string'),
    validation_queue,
    queue_index: typeof raw.queue_index === 'number' ? raw.queue_index : 0,
    responses: Array.isArray(raw.responses)
      ? (raw.responses as DiagnosticResponse[])
      : [],
    asked_item_ids: Array.isArray(raw.asked_item_ids)
      ? raw.asked_item_ids.filter((c): c is string => typeof c === 'string')
      : [],
    asked_stem_keys: Array.isArray(raw.asked_stem_keys)
      ? raw.asked_stem_keys.filter((c): c is string => typeof c === 'string')
      : [],
    current_item_id:
      typeof raw.current_item_id === 'string' ? raw.current_item_id : null,
    served_items:
      raw.served_items && typeof raw.served_items === 'object'
        ? (raw.served_items as Record<string, DiagnosticServedItem>)
        : {},
    difficulty_by_topic:
      raw.difficulty_by_topic && typeof raw.difficulty_by_topic === 'object'
        ? (raw.difficulty_by_topic as Record<string, number>)
        : {},
  };
}
