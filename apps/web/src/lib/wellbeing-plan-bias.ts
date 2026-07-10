/**
 * Wellbeing plan bias — morale selection, signal evaluation, rewrite cooldowns (ADR-0008 PR2).
 */
import 'server-only';
import kg from '@/lib/kg-data.json';
import crossEdges from '@/lib/kg-cross-edges.json';
import { conceptMatchesSubjects } from '@/lib/concept-scope';
import { canonicalConceptId } from '@/lib/plan-catalog';
import { conceptAllowedForProfile } from '@/lib/quiz-concept-filter';

export const ANXIETY_THRESHOLD = 7;
export const MASTERY_STRENGTH = 0.7;
export const MASTERY_SHOCK_DROP = 0.25;
export const MASTERY_SHOCK_CROSS = { from: 0.6, to: 0.4 } as const;
export const WELLBEING_REWRITE_MIN_HOURS = 72;
export const WELLBEING_REWRITE_MAX_PER_WEEK = 2;
export const ANY_REWRITE_MIN_HOURS = 24;
export const GOAL_MORALE_RATIO = 0.6 / 0.4;
export const DEFAULT_GOAL_CRITICAL_RATIO = 0.6;

export type WellbeingTrigger =
  | 'profile_anxiety'
  | 'exam_anxiety_chat'
  | 'exam_window'
  | 'mastery_shock';

export interface WellbeingPlanBias {
  active: boolean;
  trigger: WellbeingTrigger | null;
  strength_anchors: string[];
  morale_concepts: string[];
  goal_critical_ratio: number;
  updated_at: string;
  last_persisted_rewrite_at: string | null;
  wellbeing_rewrites_this_week: number;
  week_window_start: string | null;
}

/** Stored JSON may include internal fields for shock detection and exam bypass. */
export interface WellbeingPlanBiasStored extends WellbeingPlanBias {
  mastery_snapshot?: Record<string, number>;
  exam_window_72h_bypass_used?: boolean;
}

interface CrossEdge {
  src: string;
  dst: string;
  relation: string;
}

const kgPrereqMap: Record<string, string[]> = (kg as { prereqMap: Record<string, string[]> }).prereqMap;
const crossEdgesArr: CrossEdge[] = (crossEdges as { edges: CrossEdge[] }).edges;
const crossEdgesByDst = new Map<string, CrossEdge[]>();
for (const e of crossEdgesArr) {
  if (e.relation !== 'prereq' && e.relation !== 'generalizes' && e.relation !== 'applies_to') continue;
  const list = crossEdgesByDst.get(e.dst);
  if (list) list.push(e);
  else crossEdgesByDst.set(e.dst, [e]);
}

const CROSS_RELATIONS = new Set(['prereq', 'generalizes', 'applies_to']);

export interface WellbeingProfileInput {
  subjects: string[];
  mental_state: Record<string, unknown> | null;
  next_test_date: string | null;
  personality_profile: Record<string, unknown> | null;
  points_group?: string | null;
  wellbeing_plan_bias?: unknown;
}

function profileAnxiety(profile: WellbeingProfileInput): number {
  const ms = profile.mental_state as { anxiety?: number } | null;
  return typeof ms?.anxiety === 'number' ? ms.anxiety : 0;
}

export function daysUntilExam(profile: WellbeingProfileInput, now: Date): number | null {
  if (!profile.next_test_date) return null;
  const exam = new Date(profile.next_test_date);
  if (Number.isNaN(exam.getTime())) return null;
  return Math.ceil((exam.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

export function calendarWeekStartIso(now: Date): string {
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  const day = d.getUTCDay();
  const diff = day === 0 ? 6 : day - 1;
  d.setUTCDate(d.getUTCDate() - diff);
  return d.toISOString().slice(0, 10);
}

export function hoursSince(iso: string | null | undefined, now: Date): number {
  if (!iso) return Number.POSITIVE_INFINITY;
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return Number.POSITIVE_INFINITY;
  return (now.getTime() - t) / (1000 * 60 * 60);
}

export function defaultWellbeingPlanBias(now: Date = new Date()): WellbeingPlanBiasStored {
  return {
    active: false,
    trigger: null,
    strength_anchors: [],
    morale_concepts: [],
    goal_critical_ratio: DEFAULT_GOAL_CRITICAL_RATIO,
    updated_at: now.toISOString(),
    last_persisted_rewrite_at: null,
    wellbeing_rewrites_this_week: 0,
    week_window_start: calendarWeekStartIso(now),
    mastery_snapshot: {},
    exam_window_72h_bypass_used: false,
  };
}

export function parseWellbeingPlanBias(
  raw: unknown,
  now: Date = new Date(),
): WellbeingPlanBiasStored {
  const base = defaultWellbeingPlanBias(now);
  if (!raw || typeof raw !== 'object') return base;
  const o = raw as Record<string, unknown>;
  const trigger = o.trigger;
  const validTrigger =
    trigger === 'profile_anxiety' ||
    trigger === 'exam_anxiety_chat' ||
    trigger === 'exam_window' ||
    trigger === 'mastery_shock'
      ? trigger
      : null;
  return {
    ...base,
    active: o.active === true,
    trigger: validTrigger,
    strength_anchors: Array.isArray(o.strength_anchors)
      ? o.strength_anchors.filter((x): x is string => typeof x === 'string')
      : [],
    morale_concepts: Array.isArray(o.morale_concepts)
      ? o.morale_concepts.filter((x): x is string => typeof x === 'string')
      : [],
    goal_critical_ratio:
      typeof o.goal_critical_ratio === 'number' ? o.goal_critical_ratio : DEFAULT_GOAL_CRITICAL_RATIO,
    updated_at: typeof o.updated_at === 'string' ? o.updated_at : base.updated_at,
    last_persisted_rewrite_at:
      typeof o.last_persisted_rewrite_at === 'string' ? o.last_persisted_rewrite_at : null,
    wellbeing_rewrites_this_week:
      typeof o.wellbeing_rewrites_this_week === 'number' ? o.wellbeing_rewrites_this_week : 0,
    week_window_start:
      typeof o.week_window_start === 'string' ? o.week_window_start : base.week_window_start,
    mastery_snapshot:
      o.mastery_snapshot && typeof o.mastery_snapshot === 'object'
        ? (o.mastery_snapshot as Record<string, number>)
        : {},
    exam_window_72h_bypass_used: o.exam_window_72h_bypass_used === true,
  };
}

export function wellbeingPlanBiasFromProfile(
  profile: WellbeingProfileInput | null,
  now: Date = new Date(),
): WellbeingPlanBiasStored {
  if (!profile) return defaultWellbeingPlanBias(now);
  if (profile.wellbeing_plan_bias != null) {
    return parseWellbeingPlanBias(profile.wellbeing_plan_bias, now);
  }
  const personality = profile.personality_profile as { wellbeing_plan_bias?: unknown } | null;
  if (personality?.wellbeing_plan_bias != null) {
    return parseWellbeingPlanBias(personality.wellbeing_plan_bias, now);
  }
  return defaultWellbeingPlanBias(now);
}

function resetWeeklyCounterIfNeeded(
  bias: WellbeingPlanBiasStored,
  now: Date,
): WellbeingPlanBiasStored {
  const windowStart = calendarWeekStartIso(now);
  if (bias.week_window_start !== windowStart) {
    return {
      ...bias,
      week_window_start: windowStart,
      wellbeing_rewrites_this_week: 0,
    };
  }
  return bias;
}

export function detectMasteryShock(
  current: Record<string, number>,
  previous: Record<string, number> | undefined,
  subjects: string[],
): boolean {
  if (!previous || Object.keys(previous).length === 0) return false;
  for (const [conceptId, prevScore] of Object.entries(previous)) {
    const canonical = canonicalConceptId(conceptId) ?? conceptId;
    if (!conceptMatchesSubjects(canonical, subjects)) continue;
    const cur = current[canonical] ?? current[conceptId] ?? prevScore;
    const drop = prevScore - cur;
    if (drop >= MASTERY_SHOCK_DROP) return true;
    if (prevScore >= MASTERY_SHOCK_CROSS.from && cur < MASTERY_SHOCK_CROSS.to) return true;
  }
  return false;
}

function isWellbeingClassTrigger(trigger: WellbeingTrigger | null): boolean {
  return (
    trigger === 'profile_anxiety' ||
    trigger === 'exam_anxiety_chat' ||
    trigger === 'exam_window'
  );
}

export function pickPrimaryWellbeingTrigger(triggers: WellbeingTrigger[]): WellbeingTrigger | null {
  const priority: WellbeingTrigger[] = [
    'mastery_shock',
    'exam_window',
    'profile_anxiety',
    'exam_anxiety_chat',
  ];
  for (const t of priority) {
    if (triggers.includes(t)) return t;
  }
  return triggers[0] ?? null;
}

export function evaluateWellbeingSignals(
  profile: WellbeingProfileInput,
  mastery: Record<string, number>,
  previousBias: WellbeingPlanBiasStored | null,
  now: Date = new Date(),
): { bias: WellbeingPlanBiasStored; triggers: WellbeingTrigger[] } {
  const prev = resetWeeklyCounterIfNeeded(previousBias ?? defaultWellbeingPlanBias(now), now);
  const triggers: WellbeingTrigger[] = [];
  const anxiety = profileAnxiety(profile);
  if (anxiety >= ANXIETY_THRESHOLD) triggers.push('profile_anxiety');

  const examDays = daysUntilExam(profile, now);
  if (examDays != null && examDays >= 0 && examDays <= 14) {
    triggers.push('exam_window');
  }

  const snapshot = prev.mastery_snapshot ?? {};
  if (detectMasteryShock(mastery, snapshot, profile.subjects)) {
    triggers.push('mastery_shock');
  }

  const chatTrigger = (profile.personality_profile as { wellbeing_chat_trigger?: string } | null)
    ?.wellbeing_chat_trigger;
  if (chatTrigger === 'exam_anxiety') triggers.push('exam_anxiety_chat');

  const active = triggers.length > 0;
  const trigger = active ? pickPrimaryWellbeingTrigger(triggers) : null;

  const strengthAnchors = selectStrengthAnchors(mastery, profile.subjects);

  const bias: WellbeingPlanBiasStored = {
    ...prev,
    active,
    trigger,
    strength_anchors: strengthAnchors,
    goal_critical_ratio: prev.goal_critical_ratio || DEFAULT_GOAL_CRITICAL_RATIO,
    updated_at: now.toISOString(),
    mastery_snapshot: { ...mastery },
  };

  if (examDays != null && examDays > 14) {
    bias.exam_window_72h_bypass_used = false;
  }

  return { bias, triggers };
}

export function selectStrengthAnchors(
  mastery: Record<string, number>,
  subjects: string[],
): string[] {
  const anchors: string[] = [];
  for (const [conceptId, score] of Object.entries(mastery)) {
    const canonical = canonicalConceptId(conceptId) ?? conceptId;
    if (score >= MASTERY_STRENGTH && conceptMatchesSubjects(canonical, subjects)) {
      anchors.push(canonical);
    }
  }
  anchors.sort((a, b) => (mastery[b] ?? 0) - (mastery[a] ?? 0));
  return anchors;
}

function oneHopNeighbors(conceptId: string): string[] {
  const neighbors = new Set<string>();
  for (const p of kgPrereqMap[conceptId] ?? []) {
    neighbors.add(canonicalConceptId(p) ?? p);
  }
  for (const [dst, prereqs] of Object.entries(kgPrereqMap)) {
    if (prereqs.includes(conceptId)) neighbors.add(canonicalConceptId(dst) ?? dst);
  }
  for (const edge of crossEdgesByDst.get(conceptId) ?? []) {
    neighbors.add(canonicalConceptId(edge.src) ?? edge.src);
  }
  for (const edge of crossEdgesArr) {
    if (edge.src !== conceptId || !CROSS_RELATIONS.has(edge.relation)) continue;
    neighbors.add(canonicalConceptId(edge.dst) ?? edge.dst);
  }
  neighbors.delete(conceptId);
  return [...neighbors];
}

function neighborUrgency(conceptId: string, mastery: Record<string, number>): number {
  const score = mastery[conceptId] ?? 0.5;
  return Math.max(0, Math.min(1, 1 - score));
}

export async function selectMoraleConcepts(args: {
  learnerId: string;
  profile: WellbeingProfileInput;
  mastery: Record<string, number>;
  strengthAnchors: string[];
  maxCount?: number;
}): Promise<string[]> {
  const maxCount = args.maxCount ?? 4;
  const filterProfile = {
    subjects: args.profile.subjects,
    points_group: args.profile.points_group ?? null,
  } as Parameters<typeof conceptAllowedForProfile>[1];

  const anchors =
    args.strengthAnchors.length > 0
      ? args.strengthAnchors
      : selectStrengthAnchors(args.mastery, args.profile.subjects);

  type Scored = { id: string; score: number };
  const scored: Scored[] = [];
  const seen = new Set<string>();

  for (const anchor of anchors) {
    const anchorMastery = args.mastery[anchor] ?? MASTERY_STRENGTH;
    for (const rawNeighbor of oneHopNeighbors(anchor)) {
      const neighbor = canonicalConceptId(rawNeighbor) ?? rawNeighbor;
      if (!neighbor || seen.has(neighbor)) continue;
      if (!conceptMatchesSubjects(neighbor, args.profile.subjects)) continue;
      if (!conceptAllowedForProfile(neighbor, filterProfile)) continue;
      seen.add(neighbor);
      const urgency = neighborUrgency(neighbor, args.mastery);
      const score = anchorMastery * 0.6 + (1 - urgency) * 0.4;
      scored.push({ id: neighbor, score });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, maxCount).map((s) => s.id);
}

/**
 * Blend goal-critical order with morale concepts (~60% / ~40% by default).
 * Dedupes; goal-critical concepts keep their relative order first.
 */
export function applyWellbeingOverlay(
  orderedConcepts: string[],
  moraleConcepts: string[],
  ratio: number = DEFAULT_GOAL_CRITICAL_RATIO,
): string[] {
  if (orderedConcepts.length === 0) return moraleConcepts.slice();
  const goalRatio = Math.max(0, Math.min(1, ratio));
  const total = orderedConcepts.length;
  const goalCount = Math.max(1, Math.round(total * goalRatio));
  const moraleCount = Math.max(0, total - goalCount);

  const goalSlice = orderedConcepts.slice(0, goalCount);
  const goalSet = new Set(goalSlice);
  const moraleSlice = moraleConcepts.filter((c) => !goalSet.has(c)).slice(0, moraleCount);

  const used = new Set<string>();
  const out: string[] = [];
  for (const c of goalSlice) {
    if (!used.has(c)) {
      used.add(c);
      out.push(c);
    }
  }
  for (const c of moraleSlice) {
    if (!used.has(c)) {
      used.add(c);
      out.push(c);
    }
  }
  for (const c of orderedConcepts.slice(goalCount)) {
    if (out.length >= total) break;
    if (!used.has(c)) {
      used.add(c);
      out.push(c);
    }
  }
  return out.slice(0, total);
}

export function canPersistWellbeingRewrite(
  bias: WellbeingPlanBiasStored,
  trigger: WellbeingTrigger | null,
  profile: WellbeingProfileInput,
  now: Date = new Date(),
): boolean {
  if (!trigger) return false;

  const sinceAny = hoursSince(bias.last_persisted_rewrite_at, now);
  if (sinceAny < ANY_REWRITE_MIN_HOURS) return false;

  if (trigger === 'mastery_shock') return true;

  if (!isWellbeingClassTrigger(trigger)) return false;

  const normalized = resetWeeklyCounterIfNeeded(bias, now);
  if (normalized.wellbeing_rewrites_this_week >= WELLBEING_REWRITE_MAX_PER_WEEK) {
    return false;
  }

  const sinceWellbeing = hoursSince(bias.last_persisted_rewrite_at, now);
  if (sinceWellbeing >= WELLBEING_REWRITE_MIN_HOURS) return true;

  if (trigger === 'exam_window') {
    const examDays = daysUntilExam(profile, now);
    if (
      examDays != null &&
      examDays >= 0 &&
      examDays <= 7 &&
      !bias.exam_window_72h_bypass_used
    ) {
      return true;
    }
  }

  return false;
}

export function recordWellbeingPersistedRewrite(
  bias: WellbeingPlanBiasStored,
  trigger: WellbeingTrigger,
  now: Date = new Date(),
): WellbeingPlanBiasStored {
  const normalized = resetWeeklyCounterIfNeeded(bias, now);
  const next: WellbeingPlanBiasStored = {
    ...normalized,
    last_persisted_rewrite_at: now.toISOString(),
    updated_at: now.toISOString(),
  };

  if (trigger !== 'mastery_shock') {
    next.wellbeing_rewrites_this_week = normalized.wellbeing_rewrites_this_week + 1;
  }

  if (
    trigger === 'exam_window' &&
    hoursSince(bias.last_persisted_rewrite_at, now) < WELLBEING_REWRITE_MIN_HOURS
  ) {
    next.exam_window_72h_bypass_used = true;
  }

  return next;
}

export function mergeBiasIntoProfile(
  personality_profile: Record<string, unknown> | null,
  bias: WellbeingPlanBias,
): Record<string, unknown> {
  return {
    ...(personality_profile ?? {}),
    wellbeing_plan_bias: bias,
  };
}
