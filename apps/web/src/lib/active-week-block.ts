/**
 * Builds the compact "## Active week" block injected into every live agent's
 * system prompt when the learner has an active plan week.
 *
 * Pure function — no IO; caller pre-fetches WeekTrainingSpec.
 * Target: ≤900 chars for a typical 4-concept week with 4 recommended actions.
 *
 * This block is the single authoritative source of "what the learner should do
 * this week" for all four live agents (Tutor, Mentor, Coach, Reviewer).
 * It replaces the need for each agent to query the plan separately.
 */

import type { WeekTrainingSpec } from './week-training-spec';

export interface ActiveWeekConcept {
  concept_id: string;
  name: string;
  name_he: string | null;
  mastery: number | null;
  /** Plan-train alignment kind. `rest` concepts are skipped in the block. */
  kind?: string;
}

export interface ActiveWeekBlockParams {
  weekNumber: number;
  /** Concepts for this week from the active plan_week row. */
  concepts: ActiveWeekConcept[];
  spec: WeekTrainingSpec;
  planHealth: {
    /** True when the plan's end_date is in the past. */
    needs_replan: boolean;
    /** Number of concepts that didn't fit the goal horizon. */
    overflow_count: number;
  };
}

const MAX_BLOCK_CHARS = 900;

/**
 * Serialises the active plan week into a compact agent-readable block.
 *
 * Format (example, 4-concept week):
 * ```
 * ## Active week
 * Week 3 · gate: due:2026-07-31
 * Concepts: [derivatives_intro] נגזרת - מבוא ~45%; [limits] גבולות ~72%
 * Weak drills: chain_rule_apply@20%, limit_epsilon@38% · Reviews due: 5
 * Recommended:
 *   • [drill] תרגול ממוקד בחולשות → /app/practice?topics=derivatives_intro
 *   • [review] 5 פריטים לחזרה → /app/practice?topics=...&mode=due
 * ```
 */
export function buildActiveWeekBlock({
  weekNumber,
  concepts,
  spec,
  planHealth,
}: ActiveWeekBlockParams): string {
  // Gate line
  const gateStr = spec.gate.passed
    ? 'passed ✓'
    : spec.gate.due_at
      ? `due:${spec.gate.due_at.slice(0, 10)}`
      : 'no-gate';

  // Concepts (skip rest-kind, cap at 5)
  const studyConcepts = concepts.filter((c) => c.kind !== 'rest').slice(0, 5);
  const conceptsStr =
    studyConcepts.length > 0
      ? studyConcepts
          .map((c) => {
            const label = c.name_he || c.name || c.concept_id;
            const pct = c.mastery != null ? ` ~${Math.round(c.mastery * 100)}%` : '';
            return `[${c.concept_id}] ${label}${pct}`;
          })
          .join('; ')
      : null;

  // Weak drills (top 3)
  const drillStr =
    spec.drills.length > 0
      ? spec.drills
          .slice(0, 3)
          .map((d) => `${d.atom}@${Math.round(d.mastery * 100)}%`)
          .join(', ')
      : 'none';

  // Recommended actions (all, max 4 from spec)
  const recLines = spec.recommended
    .map((a) => `  • [${a.kind}] ${a.label_he} → ${a.href}`)
    .join('\n');

  // Plan health flags (only if notable)
  const healthParts: string[] = [];
  if (planHealth.needs_replan) healthParts.push('needs_replan');
  if (planHealth.overflow_count > 0) healthParts.push(`overflow: ${planHealth.overflow_count}`);

  const lines: string[] = [
    `## Active week`,
    `Week ${weekNumber} · gate: ${gateStr}`,
  ];
  if (conceptsStr) lines.push(`Concepts: ${conceptsStr}`);
  lines.push(`Weak drills: ${drillStr} · Reviews due: ${spec.due_reviews.count}`);
  lines.push(`Recommended:`);
  lines.push(recLines);
  if (healthParts.length > 0) lines.push(`Health: ${healthParts.join(' · ')}`);

  const block = lines.join('\n');
  return block.length > MAX_BLOCK_CHARS ? `${block.slice(0, MAX_BLOCK_CHARS - 3)}...` : block;
}
