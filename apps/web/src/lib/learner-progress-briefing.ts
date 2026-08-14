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
  /** Server-picked single next concept (ADR-0012). */
  nextStepHe?: string | null;
  nextStepEn?: string | null;
  nextStepConceptId?: string | null;
  frontierSize?: number | null;
  remainingScope?: number | null;
  weeksLeft?: number | null;
  /** Plan-window topics with mastery 0..1 (rest skipped by caller). */
  planTopics?: Array<{ name: string; mastery: number | null }>;
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

/** Localized date for learner-facing packs — never leak ISO stamps. */
export function formatLearnerFacingDate(
  iso: string | null | undefined,
  locale: 'he' | 'en',
): string | null {
  if (!iso?.trim()) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.trim();
  return d.toLocaleDateString(locale === 'he' ? 'he-IL' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
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
    'Never say you do not know the plan/status when this block is present (ADR-0012).',
    'Never treat points_group (e.g. 5pt) as "already completed 5 units" — it is the track level.',
    formatProgressBriefingHe(input),
    '',
    formatProgressBriefingEn(input),
  ].join('\n');
}

function trackLabelHe(input: ProgressBriefingInput): string {
  const goal = input.goalLabel || 'היעד שלך';
  if (input.pointsGroup) {
    return `${goal} (מסלול ${input.pointsGroup} — לא אומר שכבר סיימת את החומר)`;
  }
  return goal;
}

function trackLabelEn(input: ProgressBriefingInput): string {
  const goal = input.goalLabel || 'your goal';
  if (input.pointsGroup) {
    return `${goal} (track ${input.pointsGroup} — not “already finished that material”)`;
  }
  return goal;
}

function honestPaceSentenceHe(input: ProgressBriefingInput): string {
  if (input.paceStatus === 'at_risk') {
    return 'לפי הקצב הנוכחי יש סיכון לפיגור מול היעד — חשוב לעבוד ממוקד, בלי להמעיט בחומרה ובלי פאניקה ריקה.';
  }
  if (input.paceStatus === 'ahead') {
    return 'אתה מקדים את הקצב המתוכנן — אפשר להתקדם בביטחון בלי להעמיס סתם.';
  }
  if (input.paceStatus === 'on_track') {
    return 'הקצב נראה סביר ביחס לתוכנית — ממשיכים בצעד אחד ברור.';
  }
  return 'אין עדיין מספיק נתוני קצב — נסתמך על השבוע הפעיל.';
}

function honestPaceSentenceEn(input: ProgressBriefingInput): string {
  if (input.paceStatus === 'at_risk') {
    return 'Current pace is at risk of falling behind the goal — focus matters; avoid empty “you’ll be fine” reassurance.';
  }
  if (input.paceStatus === 'ahead') {
    return 'You are ahead of planned pace — keep steady without piling on unnecessary load.';
  }
  if (input.paceStatus === 'on_track') {
    return 'Pace looks reasonable vs the plan — keep going with one clear step.';
  }
  return 'Pace data is thin — lean on the active week.';
}

/**
 * Authoritative learner-facing paragraphs (ADR-0012). Model paraphrases; may quote.
 * Not a field dump — prose the learner can hear.
 */
export function formatLearnerFacingStatusHe(input: ProgressBriefingInput): string {
  const readiness =
    input.readinessPct != null
      ? `מוכנות משוערת ~${input.readinessPct}% (${bandLabel(input.readinessBand, 'he')}) — בלי הבטחות על ציון בבגרות`
      : 'מוכנות: עדיין בבנייה לפי הנתונים שיש';
  const week =
    input.activeWeekNumber != null
      ? `בשבוע הפעיל (שבוע ${input.activeWeekNumber}) אתה על: ${joinList(input.activeWeekConcepts, 'הנושאים שבתוכנית')}`
      : 'אין שבוע פעיל מסומן כרגע בתוכנית';
  const next = input.nextStepHe
    ? `הצעד הבא המומלץ עכשיו: ${input.nextStepHe}${
        input.nextStepConceptId ? ` (\`concept:${input.nextStepConceptId}\`)` : ''
      }.`
    : 'הצעד הבא: נושא אחד מהשבוע הפעיל — אל תציג תפריט בחירה.';
  const strengths = input.strongConcepts?.length
    ? `חוזקות שכבר נראות: ${joinList(input.strongConcepts, '')}.`
    : '';
  const gaps = input.weakConcepts?.length
    ? `מקומות לחיזוק: ${joinList(input.weakConcepts, '')}.`
    : ''; // omit "עדיין לא סומנו" — useless to learners

  return [
    '### פסקת סטטוס ללומד (עברית) — חובה להסתמך עליה',
    `יש לי את התוכנית וההתקדמות שלך. היעד: ${trackLabelHe(input)}.`,
    input.daysToExam != null
      ? `עד המבחן/יעד נשארו בערך ${input.daysToExam} ימים.`
      : null,
    readiness + '.',
    honestPaceSentenceHe(input),
    week + '.',
    strengths || null,
    gaps || null,
    next,
    'אל תגיד שאינך יודע את התוכנית/הסטטוס/הקצב. אל תשאל את הלומד מה הקצב או כמה שעות הוא לומד. אל תציע תוכנית חדשה במקום הקיימת. אל תבקש מהלומד לבחור מתוך רשימת נושאים כשהוא לחוץ.',
  ]
    .filter(Boolean)
    .join('\n');
}

export function formatLearnerFacingStatusEn(input: ProgressBriefingInput): string {
  const readiness =
    input.readinessPct != null
      ? `Estimated readiness ~${input.readinessPct}% (${bandLabel(input.readinessBand, 'en')}) — no bagrut grade promises`
      : 'Readiness: still building from available data';
  const week =
    input.activeWeekNumber != null
      ? `Active week ${input.activeWeekNumber} focuses on: ${joinList(input.activeWeekConcepts, 'plan topics')}`
      : 'No active week is marked on the plan right now';
  const next = input.nextStepEn
    ? `Recommended next step now: ${input.nextStepEn}${
        input.nextStepConceptId ? ` (\`concept:${input.nextStepConceptId}\`)` : ''
      }.`
    : 'Next step: one topic from the active week — do not present a choice menu.';
  const strengths = input.strongConcepts?.length
    ? `Visible strengths: ${joinList(input.strongConcepts, '')}.`
    : '';
  const gaps = input.weakConcepts?.length
    ? `Areas to strengthen: ${joinList(input.weakConcepts, '')}.`
    : '';

  return [
    '### Learner-facing status paragraph (English) — must ground your reply',
    `I have your plan and progress. Goal: ${trackLabelEn(input)}.`,
    input.daysToExam != null ? `About ${input.daysToExam} days to the exam/target.` : null,
    readiness + '.',
    honestPaceSentenceEn(input),
    week + '.',
    strengths || null,
    gaps || null,
    next,
    'Never say you do not know the plan/status/pace. Do not ask the learner for hours or pace. Do not invent a replacement plan. Do not ask a stressed learner to pick from a topic menu.',
  ]
    .filter(Boolean)
    .join('\n');
}

export function buildLearnerFacingStatusPack(input: ProgressBriefingInput): string {
  return [
    '## AUTHORITATIVE learner-facing status pack (ADR-0012)',
    'Use this **only** for pressure/status/anxiety/pushback / "what next" turns. Paraphrase in the learner\'s language; you may quote short lines. Structured briefing above is internal.',
    'On math teaching, practice-arena help, or learner corrections: **ignore** this pack\'s next-step closer — do not paste "הצעד הבא המומלץ" / "Recommended next step".',
    formatLearnerFacingStatusHe(input),
    '',
    formatLearnerFacingStatusEn(input),
  ].join('\n');
}

export const PRESSURE_FAMILY_TURN_INSTRUCTION = `## THIS TURN — pressure family (ADR-0012, mandatory)
The learner is anxious, asking status, challenging your knowledge, asking what to do now, or protecting an existing plan.

**4-beat reply (required order):**
1. Validate in one short natural sentence (correct Hebrew/English — no garbled phrases).
2. Honest status from the AUTHORITATIVE learner-facing status pack (pace + readiness). If pace is at_risk, do NOT say "don't worry" / "you can do everything".
3. Give exactly ONE next action — the pack's recommended next step. Do not list a menu of topics.
4. Offer to start that one topic now.

**Hard bans:**
- Never say you don't know the plan/status/XP/memory when packs are present.
- Never ask the learner for the program name, subjects, current pace, weekly hours, or how much theory they cover — those are in the profile and AUTHORITATIVE pack.
- Never invent a new weekly/daily plan or start a plan-change interview unless they explicitly request a plan change.
- Never dump raw keys (\`bagrut_math_5\`), ISO dates, or "gaps: none flagged".
- Never misread points_group as completed study.
- Ban garbage Hebrew: "חשוך", "באחריות", "להביא לדמיון", "אתה כבר יש לך", "חששותי".`;

export const AGENT_CORRECTION_TURN_INSTRUCTION = `## THIS TURN — learner correction (mandatory)
The learner says you erred, challenges your construction, and/or supplies a corrected solution.
1. Re-check against \`## Method authority\` / hybrid packs / arithmetic (mean × count). Drop any invented construction not in sources.
2. If \`solver.verify_numeric\` has AUTHORITATIVE numbers: teach that method now — do not keep asking "how do you think…?".
3. Otherwise: re-ground from worked_example / key_insights only; if sources are THIN, refuse freestyle invention and ask for the concept.
4. Admit clearly if they are right; restate the corrected result with a one-line check.
5. Complete grammatical sentences only — never paste "הצעה להמשך", "הצעד הבא המומלץ עכשיו", or "Recommended next step".
6. Do not switch into exam/status/next-topic mode on this turn.`;

export const CONTEXT_CHALLENGE_TURN_INSTRUCTION = `## THIS TURN — context challenge (ADR-0012, mandatory)
Learner says you don't know / you should know / you're the teacher.
- Acknowledge they are right to expect you to know.
- Immediately give status from the AUTHORITATIVE pack (you DO know).
- Then one next step from the pack.
- Never apologize by claiming ignorance of injected plan data.`;

export const PLAN_OWNERSHIP_TURN_INSTRUCTION = `## THIS TURN — plan ownership (ADR-0012, mandatory)
Learner already has a plan and asks if you want to change it.
- Affirm you are NOT replacing their plan.
- Do not offer a new daily/weekly plan.
- If they want changes: handle it in this chat (guided propose → confirm). Never send them to a form.
- Answer what caused concern using the status pack; one next step from the active week.`;

/** @deprecated Prefer PRESSURE_FAMILY_TURN_INSTRUCTION — kept for callers. */
export const PROGRESS_STATUS_TURN_INSTRUCTION = PRESSURE_FAMILY_TURN_INSTRUCTION;

export const RECOVERY_TURN_INSTRUCTION = `## THIS TURN — recovery / simplify (mandatory)
The learner is confused, overloaded, or asked for a simpler path.
1. Drop any failed explanation path from prior turns — do not dig deeper into it.
2. Say honestly whether the topic is required for their current plan / bagrut track, or optional enrichment.
3. Teach the simplest CORRECT method from \`## Method authority\` / injected lesson/concept context when present; otherwise use honest general knowledge and say you are not citing an ASF lesson (ADR-0015). Never invent a simpler false method.
4. Never trade correctness for simplicity. One short worked example, then check understanding.
5. If the question is a definite integral (limits given, e.g. 0 to 1), finish with the numeric value (for ∫₀¹ x² dx state **1/3** explicitly after the antiderivative).
6. Optional: emit one [[ASF_MEMORY_NOTE:...]] with kind misconception or strategy (≤600 chars).`;

export const WORKED_SOLUTION_TURN_INSTRUCTION = `## THIS TURN — worked solution / deepen (mandatory)
- Prefer injected corpus/KG / hybrid packs when present; otherwise solve from general knowledge without inventing ASF citations (ADR-0015).
- If the solution needs more than ~8 steps: give a short roadmap + first 2–3 steps, then ask whether to continue.
- On "המשך / continue": resume from the last unfinished step — do NOT restate earlier steps or say you need to "explain differently".
- Keep math in \`$...$\` / \`$$...$$\`. No filler closers.`;

/**
 * Agent-facing note when a profile exists but weekly plan weeks are missing.
 * Must not invite onboarding or claim the learner has no goal/pace data.
 */
export function buildWeeklyPlanAbsenceBlock(opts: {
  hasPlanRow: boolean;
  goal?: string | null;
  hoursPerWeek?: number | null;
  deadline?: string | null;
}): string {
  const bits: string[] = [];
  if (opts.goal?.trim()) bits.push(`goal: ${opts.goal.trim()}`);
  if (opts.hoursPerWeek != null) bits.push(`hours/week: ${opts.hoursPerWeek}`);
  if (opts.deadline?.trim()) bits.push(`deadline: ${opts.deadline.trim()}`);
  const facts = bits.length ? ` Profile facts still apply (${bits.join('; ')}).` : '';
  const weeks = opts.hasPlanRow
    ? 'A plan row exists but weekly topics are empty.'
    : 'No weekly topic schedule is loaded.';
  return [
    '## Current weekly learning plan',
    `${weeks}${facts} Report status from the learner profile, hours/week, deadline, mastery, and AUTHORITATIVE pack when present.`,
    'Do NOT say you have no information. Do NOT invite onboarding. Do NOT invent a replacement plan unless they explicitly ask to change the plan.',
  ].join('\n');
}

const DONE_MASTERY = 0.7;

function topicPct(mastery: number | null | undefined): string {
  if (mastery == null || !Number.isFinite(mastery)) return '';
  return ` (${Math.round(mastery * 100)}%)`;
}

/**
 * Deterministic learner-visible status answer (Hebrew/English).
 * Status turns must not depend on the LLM noticing injected packs.
 */
export function composeLearnerStatusReply(
  input: ProgressBriefingInput,
  locale: 'he' | 'en' = 'he',
): string {
  const topics = (input.planTopics ?? []).filter((t) => t.name.trim());
  const done = topics.filter((t) => (t.mastery ?? 0) >= DONE_MASTERY);
  const remaining = topics.filter((t) => (t.mastery ?? 0) < DONE_MASTERY);
  const mastered =
    input.frontierSize != null && input.remainingScope != null
      ? Math.max(0, input.frontierSize - input.remainingScope)
      : null;
  const nextHe = input.nextStepHe || remaining[0]?.name || input.activeWeekConcepts?.[0] || null;
  const nextEn = input.nextStepEn || remaining[0]?.name || input.activeWeekConcepts?.[0] || null;

  if (locale === 'en') {
    const goal = input.goalLabel || 'your learning goal';
    const date = input.examDateLabel ? ` Target date: ${input.examDateLabel}.` : '';
    const days =
      input.daysToExam != null ? ` About ${input.daysToExam} days remain.` : '';
    const hours =
      input.hoursPerWeek != null ? ` Planned study time: about ${input.hoursPerWeek} hours/week.` : '';
    const scope =
      mastered != null && input.frontierSize
        ? ` Toward the full goal, about ${mastered} of ${input.frontierSize} concepts are at mastery (${input.remainingScope} remaining).`
        : '';
    const week =
      input.activeWeekNumber != null
        ? ` Active week ${input.activeWeekNumber}: ${joinList(
            topics.map((t) => `${t.name}${topicPct(t.mastery)}`),
            'topics from your plan',
          )}.`
        : topics.length
          ? ` On the current plan window: ${topics.map((t) => `${t.name}${topicPct(t.mastery)}`).join(', ')}.`
          : ' The two-week topic window has no titles loaded yet — the goal and deadline above still stand.';
    const finished = done.length
      ? ` At mastery in this window: ${done.map((t) => t.name).join(', ')}.`
      : ' No concept in the current window has crossed the mastery bar yet.';
    const left = remaining.length
      ? ` Still to do here: ${remaining.map((t) => t.name).join(', ')}.`
      : done.length
        ? ' This window is at mastery — next is the following week or a drill on weak atoms.'
        : '';
    const next = nextEn ? ` Next step: ${nextEn}.` : '';
    return [
      `Your site plan is ${goal}.${date}${days}${hours}`,
      `${honestPaceSentenceEn(input)}${scope}`,
      `${week}${finished}${left}${next}`,
      'This is the status from your plan and mastery on this site. You do not need to open your profile or switch to the Mentor for these facts.',
    ].join('\n\n');
  }

  const goal = input.goalLabel || 'היעד שלך';
  const date = input.examDateLabel ? ` תאריך היעד הוא ${input.examDateLabel}.` : '';
  const days =
    input.daysToExam != null ? ` נשארו בערך ${input.daysToExam} ימים.` : '';
  const hours =
    input.hoursPerWeek != null
      ? ` בתוכנית רשומות כ־${input.hoursPerWeek} שעות לימוד בשבוע.`
      : '';
  const track = input.pointsGroup
    ? ` זה מסלול ${input.pointsGroup} — רמת המסלול, לא סימן שכבר סיימת את החומר.`
    : '';
  const scope =
    mastered != null && input.frontierSize
      ? ` מול היעד כולו נשלטו בערך ${mastered} מתוך ${input.frontierSize} מושגים (${input.remainingScope} נשארו).`
      : '';
  const week =
    input.activeWeekNumber != null
      ? ` בשבוע הפעיל (שבוע ${input.activeWeekNumber}): ${joinList(
          topics.map((t) => `${t.name}${topicPct(t.mastery)}`),
          'הנושאים שבתוכנית',
        )}.`
      : topics.length
        ? ` בחלון התוכנית הנוכחי: ${topics.map((t) => `${t.name}${topicPct(t.mastery)}`).join(', ')}.`
        : ' חלון השבועיים עדיין בלי כותרות נושאים טעונות — היעד והתאריך למעלה כן בתוקף.';
  const finished = done.length
    ? ` ברמת שליטה בחלון הזה: ${done.map((t) => t.name).join(', ')}.`
    : ' בחלון הנוכחי עוד אין מושג שעבר את רף השליטה.';
  const left = remaining.length
    ? ` עוד לעשות כאן: ${remaining.map((t) => t.name).join(', ')}.`
    : done.length
      ? ' החלון הזה בשליטה — הצעד הבא הוא השבוע הבא או תרגול על נקודות חלשות.'
      : '';
  const next = nextHe ? ` הצעד הבא: ${nextHe}.` : '';
  return [
    `התוכנית שלך באתר היא ${goal}.${date}${days}${hours}${track}`,
    `${honestPaceSentenceHe(input)}${scope}`,
    `${week}${finished}${left}${next}`,
    'זה הסטטוס לפי התוכנית והשליטה אצלנו באתר. אין צורך לפנות למנטור או לפרופיל כדי לדעת את זה.',
  ].join('\n\n');
}
