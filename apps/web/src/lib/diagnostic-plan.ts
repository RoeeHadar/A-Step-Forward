/**
 * Pure diagnostic planning logic (no I/O) — profile-goal-path probes + agent summary.
 */
import kg from '@/lib/kg-data.json';
import { canonicalConceptId } from '@/lib/plan-catalog';

export const DIAGNOSTIC_SESSION_VERSION = 2;

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
  responses: DiagnosticResponse[];
  asked_item_ids: string[];
  /** Next concept slot in probe_concepts (adaptive advance on success). */
  concept_index: number;
  /** Per-topic difficulty for CAT-style adjustment. */
  difficulty_by_topic: Record<string, number>;
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

export function emptyDiagnosticSession(
  goalConceptId: string | null,
  probeConcepts: string[],
): DiagnosticSessionPayload {
  return {
    version: DIAGNOSTIC_SESSION_VERSION,
    goal_concept_id: goalConceptId,
    probe_concepts: probeConcepts,
    responses: [],
    asked_item_ids: [],
    concept_index: 0,
    difficulty_by_topic: {},
  };
}

/** Map onboarding self-score (1–10) to initial item difficulty (2–8). Lower self → easier start. */
export function selfScoreToDifficulty(selfScore: number | undefined): number {
  if (selfScore == null || !Number.isFinite(selfScore)) return 5;
  const clamped = Math.min(10, Math.max(1, selfScore));
  return Math.round(2 + ((clamped - 1) / 9) * 6);
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

  return merged.slice(0, maxConcepts);
}

export function currentProbeConcept(state: DiagnosticSessionPayload): string | null {
  if (state.probe_concepts.length === 0) return null;
  const idx = Math.min(state.concept_index, state.probe_concepts.length - 1);
  return state.probe_concepts[idx] ?? null;
}

export function targetDifficultyForConcept(
  state: DiagnosticSessionPayload,
  conceptId: string,
  selfScores: Record<string, number> | null,
): number {
  if (state.difficulty_by_topic[conceptId] != null) {
    return state.difficulty_by_topic[conceptId]!;
  }
  const raw = selfScores?.[conceptId];
  return selfScoreToDifficulty(typeof raw === 'number' ? raw : undefined);
}

export function applyDiagnosticResponse(
  state: DiagnosticSessionPayload,
  response: DiagnosticResponse,
): DiagnosticSessionPayload {
  const topic = response.topic;
  const prevDiff = state.difficulty_by_topic[topic] ?? response.difficulty;
  const nextDiff = nextCatDifficulty(prevDiff, response.correct);

  const responses = [...state.responses, response];
  const asked_item_ids = [...state.asked_item_ids, response.item_id];
  const difficulty_by_topic = { ...state.difficulty_by_topic, [topic]: nextDiff };

  let concept_index = state.concept_index;
  if (response.correct) {
    concept_index = Math.min(state.probe_concepts.length, state.concept_index + 1);
  }

  return {
    ...state,
    responses,
    asked_item_ids,
    difficulty_by_topic,
    concept_index,
  };
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

  const agent_brief_en =
    `Diagnostic (${state.responses.length} Q) toward **${goalLabel}**. ` +
    (weakLabels.length
      ? `Prioritize remediation: ${weakLabels.join(', ')}. `
      : 'No major gaps surfaced — start at the next path step. ') +
    (strongLabels.length ? `Strengths: ${strongLabels.join(', ')}. ` : '') +
    `Week-1 focus concepts: ${plan_focus_concepts.join(', ') || 'path default'}.`;

  const weakHe = probed
    .filter((p) => weak_concepts.includes(p.concept_id))
    .map((p) => p.name_he ?? p.name)
    .slice(0, 4);
  const strongHe = probed
    .filter((p) => strong_concepts.includes(p.concept_id))
    .map((p) => p.name_he ?? p.name)
    .slice(0, 3);

  const agent_brief_he =
    `אבחון (${state.responses.length} שאלות) לכיוון **${goalLabelHe}**. ` +
    (weakHe.length ? `להתמקד ב: ${weakHe.join(', ')}. ` : 'לא עלו פערים גדולים — אפשר להתקדם בנתיב. ') +
    (strongHe.length ? `חוזקות: ${strongHe.join(', ')}. ` : '') +
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
  if (!raw || raw.version !== DIAGNOSTIC_SESSION_VERSION) return null;
  if (!Array.isArray(raw.probe_concepts)) return null;
  return {
    version: DIAGNOSTIC_SESSION_VERSION,
    goal_concept_id: typeof raw.goal_concept_id === 'string' ? raw.goal_concept_id : null,
    probe_concepts: raw.probe_concepts.filter((c): c is string => typeof c === 'string'),
    responses: Array.isArray(raw.responses)
      ? (raw.responses as DiagnosticResponse[])
      : [],
    asked_item_ids: Array.isArray(raw.asked_item_ids)
      ? raw.asked_item_ids.filter((c): c is string => typeof c === 'string')
      : [],
    concept_index: typeof raw.concept_index === 'number' ? raw.concept_index : 0,
    difficulty_by_topic:
      raw.difficulty_by_topic && typeof raw.difficulty_by_topic === 'object'
        ? (raw.difficulty_by_topic as Record<string, number>)
        : {},
  };
}
