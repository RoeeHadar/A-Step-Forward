/**
 * Week training spec — derives recommended training actions for the active plan week.
 *
 * Produces a typed WeekTrainingSpec that routes the learner into the EXISTING
 * training surfaces (practice arena, FSRS reviews, custom quizzes, weekly gates)
 * via a prioritised recommended[] list derived purely at read time.
 *
 * No new tables; no stored spec; no new training infrastructure.
 * ≤2 Neon queries on dashboard load (getWeekAtomMastery + getGatePassed).
 */
import 'server-only';
import kg from './kg-data.json';
import {
  getWeekAtomMastery,
  getGatePassed,
  type WeekAtomRow,
} from './neon-db';
import type { PlanWeek, PlanConcept } from './learning-path-types';

// ---------------------------------------------------------------------------
// In-memory concept → atoms map (derived from kg-data.json at module load)
// ---------------------------------------------------------------------------

interface KgConceptEntry {
  id: string;
  skill_atoms?: string[];
}

const conceptToAtoms = new Map<string, string[]>();
for (const c of (kg as unknown as { concepts: KgConceptEntry[] }).concepts) {
  if (c.skill_atoms?.length) {
    conceptToAtoms.set(c.id, c.skill_atoms);
  }
}

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export type TrainingActionKind = 'drill' | 'review' | 'quiz_gate' | 'custom_quiz';

export interface TrainingAction {
  kind: TrainingActionKind;
  label_he: string;
  label_en: string;
  href: string;
  reason_he: string;
  reason_en: string;
}

export interface DrillAtom {
  atom: string;
  mastery: number;
  concept_id: string;
  concept_name: string;
  concept_name_he: string | null;
}

export interface DueReviewSummary {
  count: number;
  top_concepts: Array<{
    concept_id: string;
    concept_name: string;
    concept_name_he: string | null;
  }>;
}

export interface GateStatus {
  due_at: string | null;
  passed: boolean;
}

export interface WeekTrainingSpec {
  week_id: string;
  plan_id: string;
  week_number: number;
  drills: DrillAtom[];
  due_reviews: DueReviewSummary;
  gate: GateStatus;
  recommended: TrainingAction[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MASTERY_WEAK_THRESHOLD = 0.6;
const GATE_DUE_SOON_MS = 3 * 24 * 60 * 60 * 1000;
const MAX_DRILLS = 6;
const MAX_RECOMMENDED = 4;

// ---------------------------------------------------------------------------
// Minimal types for the week context (avoids importing heavy plan types in tests)
// ---------------------------------------------------------------------------

export interface WeekContext {
  id: string;
  week_number: number;
  quiz_due_at?: string | null;
  concepts: ReadonlyArray<Pick<PlanConcept, 'concept_id'>>;
}

// ---------------------------------------------------------------------------
// Pure derivation logic (exported for unit tests — no IO)
// ---------------------------------------------------------------------------

/**
 * Derive a WeekTrainingSpec from raw DB rows.
 * Exported as a pure function so tests can call it without mocking Neon.
 *
 * @param atomRows   — result of getWeekAtomMastery
 * @param gatePassed — result of getGatePassed
 * @param week       — active plan week (at minimum: id, week_number, quiz_due_at, concepts[])
 * @param planId     — the plan's UUID (for gate href construction)
 * @param now        — injectable clock (default: Date.now())
 */
export function deriveTrainingSpec(
  atomRows: WeekAtomRow[],
  gatePassed: boolean,
  week: WeekContext,
  planId: string,
  now: Date = new Date(),
): WeekTrainingSpec {
  // ── Weak drills ──────────────────────────────────────────────────────────
  const drills: DrillAtom[] = atomRows
    .filter((r) => r.mastery < MASTERY_WEAK_THRESHOLD)
    .sort((a, b) => a.mastery - b.mastery)
    .slice(0, MAX_DRILLS)
    .map((r) => ({
      atom: r.atom,
      mastery: r.mastery,
      concept_id: r.concept_id,
      concept_name: r.concept_name,
      concept_name_he: r.concept_name_he,
    }));

  // ── FSRS due reviews (same query result) ─────────────────────────────────
  const dueAtoms = atomRows.filter((r) => r.is_due);
  const dueConceptMap = new Map<
    string,
    { concept_name: string; concept_name_he: string | null }
  >();
  for (const r of dueAtoms) {
    if (!dueConceptMap.has(r.concept_id)) {
      dueConceptMap.set(r.concept_id, {
        concept_name: r.concept_name,
        concept_name_he: r.concept_name_he,
      });
    }
  }
  const due_reviews: DueReviewSummary = {
    count: dueAtoms.length,
    top_concepts: [...dueConceptMap.entries()].slice(0, 3).map(([cid, meta]) => ({
      concept_id: cid,
      concept_name: meta.concept_name,
      concept_name_he: meta.concept_name_he,
    })),
  };

  // ── Gate status ───────────────────────────────────────────────────────────
  const gate: GateStatus = {
    due_at: week.quiz_due_at ?? null,
    passed: gatePassed,
  };

  // ── Recommended actions (priority-ordered) ────────────────────────────────
  const recommended = buildRecommended({ drills, due_reviews, gate, planId, week, now });

  return {
    week_id: week.id,
    plan_id: planId,
    week_number: week.week_number,
    drills,
    due_reviews,
    gate,
    recommended,
  };
}

function buildRecommended({
  drills,
  due_reviews,
  gate,
  planId,
  week,
  now,
}: {
  drills: DrillAtom[];
  due_reviews: DueReviewSummary;
  gate: GateStatus;
  planId: string;
  week: WeekContext;
  now: Date;
}): TrainingAction[] {
  const actions: TrainingAction[] = [];

  const gateHref = `/quiz/${week.id}?plan_id=${encodeURIComponent(planId)}&week_num=${week.week_number}`;

  // 1. Weekly gate not yet passed
  if (gate.due_at && !gate.passed) {
    const dueMsLeft = new Date(gate.due_at).getTime() - now.getTime();
    const isDueSoon = Number.isFinite(dueMsLeft) && dueMsLeft < GATE_DUE_SOON_MS;
    actions.push({
      kind: 'quiz_gate',
      label_he: 'מבחן שבועי',
      label_en: 'Weekly gate quiz',
      href: gateHref,
      reason_he: isDueSoon
        ? 'המבחן השבועי עומד לפוג — עשה/י אותו עכשיו'
        : 'גמור/י את המבחן השבועי כדי להמשיך',
      reason_en: isDueSoon
        ? 'Weekly gate is due soon — take it now'
        : 'Complete the weekly gate to advance',
    });
  }

  // 2. Drill weak atoms (link to practice arena with concept topics)
  if (drills.length > 0) {
    const conceptIds = [...new Set(drills.map((d) => d.concept_id))].slice(0, 3);
    const topDrill = drills[0]!;
    const topName = topDrill.concept_name_he ?? topDrill.concept_name;
    const suffix = drills.length > 1
      ? (` ועוד ${drills.length - 1}`)
      : '';
    actions.push({
      kind: 'drill',
      label_he: 'תרגול ממוקד בחולשות',
      label_en: 'Drill weak spots',
      href: `/app/practice?topics=${encodeURIComponent(conceptIds.join(','))}`,
      reason_he: `${topName}${suffix} מתחת ל-60% — צריך תרגול`,
      reason_en: `${topDrill.concept_name}${drills.length > 1 ? ` +${drills.length - 1}` : ''} below 60% mastery`,
    });
  }

  // 3. FSRS due reviews for this week's concepts
  if (due_reviews.count > 0) {
    const conceptIds = due_reviews.top_concepts.map((c) => c.concept_id).slice(0, 3);
    const plural = due_reviews.count !== 1;
    actions.push({
      kind: 'review',
      label_he: `${due_reviews.count} ${plural ? 'פריטים' : 'פריט'} לחזרה`,
      label_en: `${due_reviews.count} item${plural ? 's' : ''} due for review`,
      href: `/app/practice?topics=${encodeURIComponent(conceptIds.join(','))}&mode=due`,
      reason_he: 'חזרה מרווחת לפי FSRS שומרת על ידע לטווח ארוך',
      reason_en: 'FSRS spaced review keeps knowledge in long-term memory',
    });
  }

  // 4a. Gate passed + no weak drills → celebrate + suggest custom quiz
  if (gate.passed && drills.length === 0) {
    const topicIds = week.concepts.slice(0, 3).map((c) => c.concept_id);
    actions.push({
      kind: 'custom_quiz',
      label_he: 'חידון על נושאי השבוע',
      label_en: "Quiz on this week's topics",
      href: `/app/quiz?topics=${encodeURIComponent(topicIds.join(','))}`,
      reason_he: '🎉 עברת את המבחן! אתגר/י את עצמך יותר',
      reason_en: '🎉 Gate passed! Challenge yourself further',
    });
  }

  // 4b. Fallback: no gate / no drills / no reviews → suggest custom quiz
  if (actions.length === 0) {
    const topicIds = week.concepts.slice(0, 3).map((c) => c.concept_id);
    actions.push({
      kind: 'custom_quiz',
      label_he: 'חידון על נושאי השבוע',
      label_en: "Quiz on this week's topics",
      href: `/app/quiz?topics=${encodeURIComponent(topicIds.join(','))}`,
      reason_he: 'בדוק/י את עצמך על מה שלמדת השבוע',
      reason_en: 'Test yourself on what you covered this week',
    });
  }

  return actions.slice(0, MAX_RECOMMENDED);
}

// ---------------------------------------------------------------------------
// DB-calling orchestrator
// ---------------------------------------------------------------------------

/**
 * Builds the WeekTrainingSpec for the active plan week.
 * Runs ≤2 Neon queries (getWeekAtomMastery + getGatePassed) in parallel.
 * Returns null when the week has no concepts (empty plan or brand-new plan).
 */
export async function buildWeekTrainingSpec(
  learnerId: string,
  week: PlanWeek,
  planId: string,
): Promise<WeekTrainingSpec | null> {
  if (!week?.concepts?.length) return null;

  // Collect atom IDs for this week's concepts (in-memory KG lookup — no DB)
  const weekAtomIds: string[] = [];
  for (const concept of week.concepts) {
    const atoms = conceptToAtoms.get(concept.concept_id);
    if (atoms) weekAtomIds.push(...atoms);
  }

  // Run the 2 DB queries in parallel
  const [atomRows, gatePassed] = await Promise.all([
    getWeekAtomMastery(learnerId, weekAtomIds),
    getGatePassed(learnerId, planId, week.week_number),
  ]);

  return deriveTrainingSpec(atomRows, gatePassed, week, planId);
}

// ---------------------------------------------------------------------------
// Agent context serialiser (≤600 chars)
// ---------------------------------------------------------------------------

/**
 * Serialises the spec to a compact machine-readable text block for future
 * chat-context injection. Stays under 600 chars (hard-truncated with "...").
 */
export function trainingSpecForAgentContext(spec: WeekTrainingSpec): string {
  const drillStr =
    spec.drills.length > 0
      ? spec.drills
          .slice(0, 3)
          .map((d) => `${d.atom}@${Math.round(d.mastery * 100)}%`)
          .join(',')
      : 'none';
  const gateStr = spec.gate.due_at
    ? spec.gate.passed
      ? 'passed'
      : `due:${spec.gate.due_at.slice(0, 10)}`
    : 'no-gate';
  const recStr = spec.recommended
    .map((a) => `[${a.kind}]${a.label_en}→${a.href}`)
    .join('|');

  const block = [
    `## Week ${spec.week_number} training`,
    `drills: ${drillStr}`,
    `reviews: ${spec.due_reviews.count}atoms`,
    `gate: ${gateStr}`,
    `recommended: ${recStr}`,
  ].join('\n');

  return block.length > 600 ? `${block.slice(0, 597)}...` : block;
}
