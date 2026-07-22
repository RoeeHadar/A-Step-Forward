/**
 * Pre-summarized bilingual learner progress briefing for chat agents (ADR-0011).
 * Agents must paraphrase this into plain learner language — never dump raw fields.
 */
import type { ReadinessBand, ReadinessPhase } from '@/lib/readiness';
import type { PaceStatus } from '@/lib/plan-pacing';

export interface ProgressBriefingInput {
  goalKey?: string | null;
  goalLabel?: string | null;
  examDateLabel?: string | null;
  daysToExam?: number | null;
  hoursPerWeek?: number | null;
  pointsGroup?: string | null;
  subjects?: string[];
  anxiety?: number | null;
  motivation?: number | null;
  /** Plain names, already localized preference left to caller. */
  strongConcepts?: string[];
  weakConcepts?: string[];
  activeWeekNumber?: number | null;
  activeWeekConcepts?: string[];
  xpLevel?: number | null;
  xpTotal?: number | null;
  readinessPct?: number | null;
  readinessBand?: ReadinessBand | null;
  readinessPhase?: ReadinessPhase | null;
  paceStatus?: PaceStatus | null;
  recentGateSummaryHe?: string | null;
  recentGateSummaryEn?: string | null;
}

function bandLabel(band: ReadinessBand | null | undefined, locale: 'he' | 'en'): string {
  if (!band) return locale === 'he' ? 'לא זמין' : 'unavailable';
  const he: Record<ReadinessBand, string> = {
    foundational: 'יסודות',
    building: 'בבנייה',
    approaching: 'מתקרב',
    exam_ready: 'מוכן יחסית (עם מבחן לדוגמה)',
  };
  const en: Record<ReadinessBand, string> = {
    foundational: 'foundational',
    building: 'building',
    approaching: 'approaching',
    exam_ready: 'relatively ready (mock passed)',
  };
  return locale === 'he' ? he[band] : en[band];
}

function paceLabel(pace: PaceStatus | null | undefined, locale: 'he' | 'en'): string {
  if (!pace) return locale === 'he' ? 'לא ידוע' : 'unknown';
  const he: Record<PaceStatus, string> = {
    ahead: 'מקדים',
    on_track: 'בקצב',
    at_risk: 'בסיכון לפיגור',
  };
  const en: Record<PaceStatus, string> = {
    ahead: 'ahead',
    on_track: 'on track',
    at_risk: 'at risk of falling behind',
  };
  return locale === 'he' ? he[pace] : en[pace];
}

function phaseLabel(phase: ReadinessPhase | null | undefined, locale: 'he' | 'en'): string {
  if (!phase) return '';
  const he: Record<ReadinessPhase, string> = {
    building: 'שלב בנייה',
    final_phase: 'שלב סיום',
    day_before: 'יום לפני המבחן',
  };
  const en: Record<ReadinessPhase, string> = {
    building: 'building phase',
    final_phase: 'final phase',
    day_before: 'day before exam',
  };
  return locale === 'he' ? he[phase] : en[phase];
}

function joinList(items: string[] | undefined, empty: string): string {
  if (!items?.length) return empty;
  return items.slice(0, 3).join(', ');
}

/** Compact HE block (for injection). */
export function formatProgressBriefingHe(input: ProgressBriefingInput): string {
  const readiness =
    input.readinessPct != null
      ? `מוכנות ~${input.readinessPct}% (${bandLabel(input.readinessBand, 'he')}${
          input.readinessPhase ? `, ${phaseLabel(input.readinessPhase, 'he')}` : ''
        }) — לעולם לא להבטיח הצלחה בבגרות`
      : 'מוכנות: אין מספיק נתונים — דבר בצניעות';
  const week =
    input.activeWeekNumber != null
      ? `שבוע פעיל ${input.activeWeekNumber}: ${joinList(input.activeWeekConcepts, 'ללא נושאים')}`
      : 'אין שבוע פעיל בתוכנית';
  const lines = [
    '### תמצית התקדמות (עברית) — לניסוח חופשי בלבד',
    `- יעד: ${input.goalLabel || input.goalKey || 'לא צוין'}${
      input.pointsGroup ? ` · ${input.pointsGroup}` : ''
    }`,
    input.examDateLabel
      ? `- מבחן/יעד: ${input.examDateLabel}${
          input.daysToExam != null ? ` (בעוד ~${input.daysToExam} ימים)` : ''
        }`
      : '- מבחן/יעד: לא צוין',
    `- ${readiness}`,
    `- קצב תוכנית: ${paceLabel(input.paceStatus, 'he')}`,
    `- ${week}`,
    `- חוזקות: ${joinList(input.strongConcepts, 'עדיין לא סומנו')}`,
    `- פערים: ${joinList(input.weakConcepts, 'עדיין לא סומנו')}`,
    input.hoursPerWeek != null ? `- זמן לימוד: ~${input.hoursPerWeek} שעות/שבוע` : null,
    input.anxiety != null || input.motivation != null
      ? `- מצב: חרדה ${input.anxiety ?? '—'}/10 · עניין ${input.motivation ?? '—'}/10`
      : null,
    input.xpLevel != null
      ? `- XP (פנימי): רמה ${input.xpLevel}${
          input.xpTotal != null ? ` · ${input.xpTotal} XP` : ''
        } — אל תדביק שורות XP גולמיות`
      : null,
    input.recentGateSummaryHe
      ? `- שער אחרון (תמצית): ${input.recentGateSummaryHe}`
      : null,
  ];
  return lines.filter(Boolean).join('\n');
}

/** Compact EN block (for injection). */
export function formatProgressBriefingEn(input: ProgressBriefingInput): string {
  const readiness =
    input.readinessPct != null
      ? `readiness ~${input.readinessPct}% (${bandLabel(input.readinessBand, 'en')}${
          input.readinessPhase ? `, ${phaseLabel(input.readinessPhase, 'en')}` : ''
        }) — never promise bagrut success`
      : 'readiness: insufficient data — stay humble';
  const week =
    input.activeWeekNumber != null
      ? `active week ${input.activeWeekNumber}: ${joinList(input.activeWeekConcepts, 'no topics')}`
      : 'no active plan week';
  const lines = [
    '### Progress briefing (English) — paraphrase only',
    `- Goal: ${input.goalLabel || input.goalKey || 'unspecified'}${
      input.pointsGroup ? ` · ${input.pointsGroup}` : ''
    }`,
    input.examDateLabel
      ? `- Exam/target: ${input.examDateLabel}${
          input.daysToExam != null ? ` (~${input.daysToExam} days left)` : ''
        }`
      : '- Exam/target: unspecified',
    `- ${readiness}`,
    `- Plan pace: ${paceLabel(input.paceStatus, 'en')}`,
    `- ${week}`,
    `- Strengths: ${joinList(input.strongConcepts, 'none flagged yet')}`,
    `- Gaps: ${joinList(input.weakConcepts, 'none flagged yet')}`,
    input.hoursPerWeek != null ? `- Study time: ~${input.hoursPerWeek} h/week` : null,
    input.anxiety != null || input.motivation != null
      ? `- State: anxiety ${input.anxiety ?? '—'}/10 · interest ${input.motivation ?? '—'}/10`
      : null,
    input.xpLevel != null
      ? `- XP (internal): level ${input.xpLevel}${
          input.xpTotal != null ? ` · ${input.xpTotal} XP` : ''
        } — do not paste raw XP lines`
      : null,
    input.recentGateSummaryEn
      ? `- Latest gate (summary): ${input.recentGateSummaryEn}`
      : null,
  ];
  return lines.filter(Boolean).join('\n');
}

/**
 * Full bilingual briefing block for the system prompt.
 * Always includes HE + EN so the agent can mirror either learner language.
 */
export function buildBilingualProgressBriefing(input: ProgressBriefingInput): string {
  return [
    '## Learner progress briefing (bilingual — paraphrase; do NOT dump fields)',
    'Rules: answer in the learner\'s language; never paste XP totals, ISO timestamps, raw JSON keys, or repeated gate score lines; never claim ~100% / guaranteed bagrut success.',
    formatProgressBriefingHe(input),
    '',
    formatProgressBriefingEn(input),
  ].join('\n');
}

export const PROGRESS_STATUS_TURN_INSTRUCTION = `## THIS TURN — progress / status / readiness (mandatory)
Use Mentor-style framing even if the active agent is Tutor/Coach/Reviewer.
- Answer with a short plain-language status from the bilingual progress briefing.
- Do NOT dump XP lines, ISO dates, raw profile keys, or repeated "שער שבוע / week gate" score lines.
- For bagrut odds: use readiness band + pace only. FORBIDDEN phrases: "100%", "~100%", "מאה אחוז", "guaranteed", "מובטח" — even as a stretch goal. Say "improve readiness / close gaps" instead.
- Soft nudge (optional, one clause): deeper goals talk → Mentor.
- End with one concrete next step from the active week / gaps.`;

export const RECOVERY_TURN_INSTRUCTION = `## THIS TURN — recovery / simplify (mandatory)
The learner is confused, overloaded, or asked for a simpler path.
1. Drop any failed explanation path from prior turns — do not dig deeper into it.
2. Say honestly whether the topic is required for their current plan / bagrut track, or optional enrichment.
3. Teach the simplest CORRECT method from injected lesson/concept context (or say the corpus does not cover it).
4. Never trade correctness for simplicity. One short worked example, then check understanding.
5. If the question is a definite integral (limits given, e.g. 0 to 1), finish with the numeric value (for ∫₀¹ x² dx state **1/3** explicitly after the antiderivative).
6. Optional: emit one [[ASF_MEMORY_NOTE:...]] with kind misconception or strategy (≤600 chars).`;

export const WORKED_SOLUTION_TURN_INSTRUCTION = `## THIS TURN — worked solution / deepen (mandatory)
- If the solution needs more than ~8 steps: give a short roadmap + first 2–3 steps, then ask whether to continue.
- On "המשך / continue": resume from the last unfinished step — do NOT restate earlier steps or say you need to "explain differently".
- Keep math in \`$...$\` / \`$$...$$\`. No filler closers.`;
