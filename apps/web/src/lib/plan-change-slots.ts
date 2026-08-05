/**
 * Conversational plan-change slot-filling core (ADR-0015, Phase B).
 *
 * Pure, testable logic for the guided plan-change flow: normalize the slots the
 * learner has provided (reusing the same goal/date/concept inference as the
 * template path), decide which REQUIRED slots are still missing (extract-then-
 * ask-missing), validate goal specificity, and build the proposal + a human-
 * readable diff. All persistence + LLM orchestration lives in the tools/route;
 * this module never touches the DB.
 */
import {
  inferConceptIdsFromText,
  inferGoalMetaFromText,
} from '@/lib/plan-actions';
import { planPayloadNeedsClarification, type PlanClarificationReason } from '@/lib/plan-apply';
import type { LearnerPlanContext } from '@/lib/plan-scope-enrichment';
import type { PlanChangeSessionSlots, PendingPlanProposal } from '@/lib/neon-db';
import type { PlanUpdatePayload } from '@/lib/plan-catalog';

export type PlanSlotKey = 'goal' | 'target_date' | 'hours_per_week' | 'notes';
export const REQUIRED_PLAN_SLOTS: PlanSlotKey[] = ['goal', 'target_date'];

/**
 * How many times we re-ask for the SAME blocking slot before escalating
 * (offer Mentor handoff / pause). Count 1 is the initial ask; we escalate once
 * a slot has been asked more than (1 + SLOT_REASK_LIMIT) times.
 */
export const SLOT_REASK_LIMIT = 2;

/** Increment (and return a copy of) the per-slot re-ask counter map. */
export function bumpReask(
  reask: Record<string, number> | undefined,
  key: string,
): { reask: Record<string, number>; count: number } {
  const next = { ...(reask ?? {}) };
  next[key] = (next[key] ?? 0) + 1;
  return { reask: next, count: next[key] };
}

/** True once a slot has been asked more than the allowed number of times. */
export function shouldEscalate(count: number): boolean {
  return count > SLOT_REASK_LIMIT + 1;
}

/** Localized escalation observation when the learner keeps failing a slot. */
export function escalationPrompt(agent: string, locale: 'he' | 'en'): string {
  const he = locale === 'he';
  if (agent === 'tutor') {
    return he
      ? 'escalate: הלומד מתקשה לספק את הפרט הזה. הצע לו לעבור למנטור לתכנון מטרות, או להשהות את שינוי התוכנית ולחזור אליו מאוחר יותר (הפרטים שכבר נמסרו יישמרו). אל תשאל שוב את אותה שאלה.'
      : 'escalate: the learner is struggling with this slot. Offer to hand off to the Mentor for goal-planning, or to pause the plan change and resume later (already-provided details are kept). Do NOT ask the same question again.';
  }
  return he
    ? 'escalate: הלומד מתקשה לספק את הפרט הזה. הצע להשהות את שינוי התוכנית ולחזור אליו מאוחר יותר (הפרטים שכבר נמסרו יישמרו), או לנסח את המטרה בצורה אחרת. אל תשאל שוב את אותה שאלה.'
    : 'escalate: the learner is struggling with this slot. Offer to pause the plan change and resume later (already-provided details are kept), or to rephrase the goal. Do NOT ask the same question again.';
}

export interface SlotFillInput {
  goal?: string;
  target_date?: string;
  hours_per_week?: number;
  notes?: string;
}

function isHebrew(text: string | undefined | null): boolean {
  return /[\u0590-\u05FF]/.test(text ?? '');
}

/** Feed discrete slots through the shared template parser to normalize date/goal_key. */
function normalizeMeta(slots: PlanChangeSessionSlots): ReturnType<typeof inferGoalMetaFromText> {
  const parts: string[] = [];
  if (slots.goal?.trim()) parts.push(`מטרה או מבחן: ${slots.goal.trim()}`);
  if (slots.target_date != null && String(slots.target_date).trim()) {
    parts.push(`מועד: ${String(slots.target_date).trim()}`);
  }
  if (slots.notes?.trim()) parts.push(`הערות: ${slots.notes.trim()}`);
  return inferGoalMetaFromText(parts.join('\n'));
}

/** Merge newly-extracted input onto the existing session slots (input wins). */
export function mergeSlots(
  existing: PlanChangeSessionSlots,
  input: SlotFillInput,
): PlanChangeSessionSlots {
  const merged: PlanChangeSessionSlots = { ...existing };
  if (input.goal?.trim()) merged.goal = input.goal.trim();
  if (input.target_date != null && String(input.target_date).trim()) {
    merged.target_date = String(input.target_date).trim();
  }
  if (typeof input.hours_per_week === 'number' && input.hours_per_week > 0) {
    merged.hours_per_week = Math.min(input.hours_per_week, 84);
  }
  if (input.notes?.trim()) merged.notes = input.notes.trim();

  const meta = normalizeMeta(merged);
  if (meta.goal_key) merged.goal_key = meta.goal_key;
  const iso = meta.final_goal_date ?? meta.next_test_date ?? null;
  if (iso) merged.target_date = iso; // store the resolved ISO once parseable
  if (!merged.hours_per_week && meta.hours_per_week) merged.hours_per_week = meta.hours_per_week;
  const concepts = inferConceptIdsFromText(merged.goal ?? '', merged.notes ?? '');
  if (concepts.length) merged.priority_concepts = concepts;
  return merged;
}

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

/** Required slots still missing (extract-then-ask-missing drives what to ask). */
export function missingRequiredSlots(slots: PlanChangeSessionSlots): PlanSlotKey[] {
  const missing: PlanSlotKey[] = [];
  if (!slots.goal?.trim()) missing.push('goal');
  // target_date is satisfied only once it resolves to a real ISO date.
  const dateOk = typeof slots.target_date === 'string' && ISO_DATE_RE.test(slots.target_date);
  if (!dateOk) missing.push('target_date');
  return missing;
}

/** Goal specificity check (reuses the template scope gate — no second validator). */
export function goalScopeIssue(
  goal: string | undefined,
  learnerCtx: LearnerPlanContext = {},
): PlanClarificationReason | null {
  if (!goal?.trim()) return null;
  return planPayloadNeedsClarification({ reason: '', goal } as PlanUpdatePayload, learnerCtx);
}

/** Observation text when a goal is too broad for planning. Corpus-anchored only. */
export function broadGoalObservation(
  scope: PlanClarificationReason,
  locale: 'he' | 'en' = 'en',
): string {
  if (scope === 'subject') {
    return locale === 'he'
      ? 'still_collecting: המטרה "קדם אקדמי/מכינה" רחבה מדי. באתר יש רק מתמטיקה ופיזיקה — שאל רק: מתמטיקה או פיזיקה? (אל תציע היסטוריה/ספרות/מקצועות אחרים.)'
      : 'still_collecting: the goal "pre-academic/prep" is too broad. This site only teaches math and physics — ask ONLY: math or physics? (Never offer history/literature/other subjects.)';
  }
  if (scope === 'math') {
    return locale === 'he'
      ? 'still_collecting: המטרה "מתמטיקה" רחבה מדי. שאל איזה מסלול מהקטלוג: בגרות 3/4/5 יח״ל, חדו״א 1, מתמטיקה בדידה, אלגברה לינארית, או מכינה במתמטיקה.'
      : 'still_collecting: the goal is too broad ("math"). Ask which catalog track: Bagrut 3/4/5, Calculus 1, Discrete math, Linear algebra, or math prep (makhina).';
  }
  return locale === 'he'
    ? 'still_collecting: המטרה "פיזיקה" רחבה מדי. שאל איזה היקף מהקטלוג: מכניקה/036-361, חשמל/036-371, קרינה וחומר/036-282, או מכינה בפיזיקה.'
    : 'still_collecting: the goal is too broad ("physics"). Ask for catalog scope: Mechanics/036-361, Electricity/036-371, Radiation & Matter/036-282, or physics prep (makhina).';
}

/** Build the proposal to persist + later apply once the learner confirms. */
export function buildProposalFromSlots(
  slots: PlanChangeSessionSlots,
  agent: string,
): PendingPlanProposal {
  const meta = normalizeMeta(slots);
  const goal = slots.goal?.trim();
  const he = isHebrew(goal);
  const targetIso = (typeof slots.target_date === 'string' && ISO_DATE_RE.test(slots.target_date)
    ? slots.target_date
    : meta.final_goal_date ?? meta.next_test_date) ?? null;
  const isExam = /מבחן|בחינה|בגרות|exam|test|quiz/i.test(goal ?? '');
  const concepts = inferConceptIdsFromText(goal ?? '', slots.notes ?? '');
  const reason =
    (he ? 'עדכון תוכנית לימודים לפי בקשת הלומד' : 'Plan update requested by the learner');
  return {
    reason,
    agent,
    proposed_at: new Date().toISOString(),
    goal,
    goal_key: slots.goal_key ?? meta.goal_key,
    final_goal_date: targetIso,
    next_test_date: isExam ? targetIso : meta.next_test_date ?? null,
    next_test_name: isExam ? goal ?? null : null,
    clear_next_test: meta.clear_next_test,
    hours_per_week: slots.hours_per_week ?? meta.hours_per_week,
    priority_concepts: concepts,
    prepend_concepts: concepts,
    exclude_concepts: [],
  };
}

function fmtDate(iso: string | null | undefined, he: boolean): string {
  if (!iso) return he ? '—' : '—';
  try {
    return new Date(iso).toLocaleDateString(he ? 'he-IL' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

export interface CurrentPlanFacts {
  goal?: string | null;
  final_goal_date?: string | null;
  hours_per_week?: number | null;
}

/** Human-readable current→proposed diff shown before confirmation. */
export function buildProposalDiff(
  current: CurrentPlanFacts,
  proposal: PendingPlanProposal,
  locale: 'he' | 'en',
): string {
  const he = locale === 'he';
  const arrow = '→';
  const line = (label: string, from: string, to: string) =>
    from === to ? `- ${label}: ${to}` : `- ${label}: ${from} ${arrow} **${to}**`;
  const lines: string[] = [];
  lines.push(
    line(
      he ? 'מטרה' : 'Goal',
      (current.goal ?? '').trim() || (he ? '—' : '—'),
      (proposal.goal ?? '').trim() || (he ? '—' : '—'),
    ),
  );
  lines.push(
    line(
      he ? 'תאריך יעד' : 'Target date',
      fmtDate(current.final_goal_date ?? null, he),
      fmtDate(proposal.final_goal_date ?? null, he),
    ),
  );
  if (proposal.hours_per_week) {
    lines.push(
      line(
        he ? 'שעות בשבוע' : 'Hours/week',
        current.hours_per_week ? String(current.hours_per_week) : (he ? '—' : '—'),
        String(proposal.hours_per_week),
      ),
    );
  }
  return lines.join('\n');
}

/** What to ask the learner for a given missing slot (localized, one at a time). */
export function slotPrompt(slot: PlanSlotKey, locale: 'he' | 'en'): string {
  const he = locale === 'he';
  switch (slot) {
    case 'goal':
      return he
        ? 'מה המטרה או המבחן שאליו אתה רוצה שנכוון את התוכנית? באתר יש רק מתמטיקה ופיזיקה (למשל: מכינה במתמטיקה, חדו״א 1, בגרות פיזיקה מכניקה).'
        : 'What is the goal or exam you want the plan aimed at? This site only covers math and physics (e.g. math prep, Calculus 1, Bagrut physics mechanics).';
    case 'target_date':
      return he
        ? 'מתי מועד היעד? (תאריך או "בעוד שבועיים")'
        : 'When is the target date? (a date or e.g. "in two weeks")';
    case 'hours_per_week':
      return he
        ? 'כמה שעות בשבוע תוכל להקדיש? (אופציונלי)'
        : 'How many hours per week can you dedicate? (optional)';
    case 'notes':
      return he
        ? 'יש נושאים ספציפיים להתמקד בהם? (אופציונלי)'
        : 'Any specific topics to focus on? (optional)';
  }
}
