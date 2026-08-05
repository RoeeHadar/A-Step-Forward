/**
 * Execute learning-plan mutations (Neon) and build learner-visible summaries.
 */
import type { LearningPlan } from '@asf/schemas/learning_path';
import { resolveConceptTitles } from '@/lib/concept-display-names';
import {
  appendLearnerPersonaLine,
  applyPlanProfileUpdates,
  clearPendingPlanProposal,
  clearPlanChangeSession,
  generateLearningPlan,
  getPlanChangeSession,
  recordPlanChangeHistory,
  setPendingPlanProposal,
  type PendingPlanProposal,
} from '@/lib/neon-db';
import {
  extractPlanProposal,
  CALC1_EXAM_CONCEPTS,
  DISCRETE_EXAM_CONCEPTS,
  inferConceptIdsFromText,
  inferGoalMetaFromText,
  learnerAffirmedProposal,
  learnerCanceledPlanFlow,
  planPayloadToOptions,
  proposalToUpdatePayload,
  shouldApplyPlanImmediately,
  stripPlanMachineTags,
  type PlanProposalPayload,
} from '@/lib/plan-actions';
import { isPlanChangeTemplate, planChangeTextForParsing } from '@/lib/plan-change-template';
import {
  enrichPlanPayloadFromLearnerContext,
  planPayloadHasExamScope,
  type LearnerPlanContext,
} from '@/lib/plan-scope-enrichment';
import { getLearnerProfile, getCurrentPlan } from '@/lib/neon-db';
import {
  looksLikeCalculus1Goal,
  sanitizePlanUpdatePayload,
  type PlanUpdatePayload,
} from '@/lib/plan-catalog';

export interface PlanApplyResult {
  applied: boolean;
  planId?: string;
  reason?: string;
  goal?: string;
  finalGoalDate?: string;
  weekSummaries?: Array<{ week: number; conceptIds: string[] }>;
  noticeHe?: string;
  noticeEn?: string;
  error?: string;
  clarificationReason?: PlanClarificationReason;
  failureNotice?: string;
}

function weekSummariesFromPlan(plan: LearningPlan): PlanApplyResult['weekSummaries'] {
  return plan.weeks.map((w) => ({
    week: w.week_number,
    conceptIds: w.concepts.map((c) => c.concept_id),
  }));
}

function conceptLabel(id: string, lang: 'he' | 'en'): string {
  const t = resolveConceptTitles(id);
  return lang === 'he' ? t.title_he ?? t.title_en : t.title_en;
}

function formatGoalDate(iso: string, lang: 'he' | 'en'): string {
  try {
    return new Date(iso).toLocaleDateString(lang === 'he' ? 'he-IL' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

export function buildPlanApplyingNotice(locale: 'he' | 'en'): string {
  return locale === 'he'
    ? '\n\n⏳ **מעדכן את המטרה והתוכנית השבועית…**'
    : '\n\n⏳ **Updating your goal and weekly plan…**';
}

export function buildPlanApplyFailureNotice(
  locale: 'he' | 'en',
  error?: string,
): string {
  if (locale === 'he') {
    return [
      '---',
      '⚠️ **לא הצלחתי לעדכן את התוכנית באתר**',
      error ? `פרטים: ${error}` : '',
      'נסה שוב: העתק את תבנית **עדכון תוכנית הלימוד** מהצ\'אט, מלא את השדות ושלח.',
    ]
      .filter(Boolean)
      .join('\n');
  }
  return [
    '---',
    '⚠️ **I could not update your plan on the site**',
    error ? `Details: ${error}` : '',
    'Try again: copy the **Learning plan update** template from chat, fill in the fields, and send it.',
  ]
    .filter(Boolean)
    .join('\n');
}

const PHYSICS_GOAL_RE = /פיזיק|physics/i;
const MATH_GENERIC_RE = /מתמטיק|mathematics|\bmath\b/i;
const MATH_SPECIFIC_RE =
  /חדו|calculus|\bcalc\s*1|calculus\s*1|בדיד|discrete|5\s*יח|4\s*יח|3\s*יח|bagrut|בגרות|אלגבר|algebra|לינאר|linear|סטטיסט|statistic|הסתבר|probability|שאלון\s*47|שאלון\s*57/i;
const PHYSICS_SPECIFIC_RE =
  /036-361|036-371|036-282|036-382|מכניק|קינמט|דינמיק|ניוטון|חשמל|מעגל|קרינה|חומר|mechanics?|kinematics?|dynamics?|newton|electric(?:ity|al)?|circuits?|radiation|matter/i;
/** Pre-academic / makhina / university-prep style goals need math vs physics. */
const PREP_GOAL_RE =
  /קדם\s*אקדמ|pre[-\s]?academic|מכינה|makhina|university\s*prep|הכנה\s*לאוניברסיט/i;
/** Subject hint that makes a prep goal specific enough to plan. */
const PREP_SUBJECT_HINT_RE =
  /מתמטיק|\bmath\b|פיזיק|physics|חדו|calculus|בדיד|discrete|אלגבר|algebra|לינאר|linear|מכניק|חשמל|electric|בגרות|bagrut/i;

export type PlanClarificationReason = 'physics' | 'math' | 'subject';

export function planPayloadNeedsClarification(
  payload: PlanUpdatePayload,
  learnerCtx: LearnerPlanContext = {},
): PlanClarificationReason | null {
  if (planPayloadHasExamScope(payload, learnerCtx)) return null;

  const text = [payload.goal, payload.next_test_name, payload.reason]
    .filter(Boolean)
    .join('\n');
  if (!text.trim()) return null;

  // "Pre-academic course" without math/physics is too vague — this platform only
  // teaches those two subjects. Never invent history/literature/etc.
  // Prep + an explicit math/physics hint is specific enough (maps to makhina /
  // university_prep tracks); do not also demand Bagrut unit / Mechanics codes.
  if (PREP_GOAL_RE.test(text)) {
    if (!PREP_SUBJECT_HINT_RE.test(text)) return 'subject';
    return null;
  }

  if (PHYSICS_GOAL_RE.test(text) && !PHYSICS_SPECIFIC_RE.test(text)) return 'physics';
  if (MATH_GENERIC_RE.test(text) && !MATH_SPECIFIC_RE.test(text)) return 'math';
  return null;
}

export function buildPlanClarificationNotice(
  locale: 'he' | 'en',
  reason: PlanClarificationReason = 'physics',
): string {
  if (locale === 'he') {
    if (reason === 'subject') {
      return [
        '---',
        '⚠️ **לא עדכנתי את התוכנית עדיין**',
        'באתר יש רק מתמטיקה ופיזיקה לקורסי קדם אקדמי / מכינה. ציין/י איזה מקצוע (מתמטיקה או פיזיקה) ואת המטרה המדויקת.',
        'שלח/י שוב את תבנית **עדכון תוכנית הלימוד** בלבד (ללא טקסט נוסף לפני/אחרי), עם המטרה המדויקת והמועד.',
      ].join('\n');
    }
    if (reason === 'math') {
      return [
        '---',
        '⚠️ **לא עדכנתי את התוכנית עדיין**',
        'המטרה "מבחן במתמטיקה" רחבה מדי — צריך לדעת איזה מבחן (בגרות 3/4/5 יח"ל, חדו״א 1, מתמטיקה בדידה, אלגברה לינארית וכו׳).',
        'שלח/י שוב את תבנית **עדכון תוכנית הלימוד** בלבד (ללא טקסט נוסף לפני/אחרי), עם המטרה המדויקת והמועד.',
      ].join('\n');
    }
    return [
      '---',
      '⚠️ **לא עדכנתי את התוכנית עדיין**',
      'המטרה "מבחן בפיזיקה" רחבה מדי, ולכן אי אפשר לבנות תוכנית טובה בלי לדעת את היקף הבחינה.',
      'שלח/י שוב את תבנית **עדכון תוכנית הלימוד** בלבד (ללא טקסט נוסף), עם אחד מאלה: מכניקה / 036-361, חשמל / 036-371, קרינה וחומר / 036-282, פיזיקה 1 / פיזיקה 2, או רשימת הנושאים מהמבחן.',
    ].join('\n');
  }

  if (reason === 'subject') {
    return [
      '---',
      '⚠️ **I did not update the plan yet**',
      'This site only covers math and physics for pre-academic / university-prep tracks. Specify which subject (math or physics) and the exact goal.',
      'Resend only the **Learning plan update** template (no extra chat text before/after) with the exact goal and date.',
    ].join('\n');
  }
  if (reason === 'math') {
    return [
      '---',
      '⚠️ **I did not update the plan yet**',
      '"Math test" is too broad — specify the exam (Bagrut 3/4/5 units, Calculus 1, Discrete math, Linear algebra, etc.).',
      'Resend only the **Learning plan update** template (no extra chat text before/after) with the exact goal and date.',
    ].join('\n');
  }

  return [
    '---',
    '⚠️ **I did not update the plan yet**',
    '"Physics test" is too broad to turn into a useful weekly plan without the exam scope.',
    'Resend only the **Learning plan update** template (no extra chat text) with: Mechanics / 036-361, Electricity / 036-371, Radiation & Matter / 036-282, Physics 1 / 2, or the topic list from the test.',
  ].join('\n');
}

export function buildPlanAppliedNotice(
  result: PlanApplyResult,
  locale: 'he' | 'en',
): string {
  if (!result.applied || !result.weekSummaries?.length) {
    return locale === 'he'
      ? 'לא הצלחתי לעדכן את התוכנית — נסה שוב או פנה למנטור.'
      : 'I could not update your plan — please try again or ask your Mentor.';
  }

  const lines = result.weekSummaries.map((w) => {
    const names = w.conceptIds.map((id) => conceptLabel(id, locale)).join(', ');
    return locale === 'he'
      ? `- **שבוע ${w.week}:** ${names}`
      : `- **Week ${w.week}:** ${names}`;
  });

  const goalLines: string[] = [];
  if (result.goal) {
    goalLines.push(
      locale === 'he'
        ? `- **מטרה:** ${result.goal}`
        : `- **Goal:** ${result.goal}`,
    );
  }
  if (result.finalGoalDate) {
    goalLines.push(
      locale === 'he'
        ? `- **יעד עד:** ${formatGoalDate(result.finalGoalDate, 'he')}`
        : `- **Target date:** ${formatGoalDate(result.finalGoalDate, 'en')}`,
    );
  }

  if (locale === 'he') {
    return [
      '---',
      '✅ **המטרה והתוכנית השבועית עודכנו באתר**',
      result.reason ? `סיבה: ${result.reason}` : '',
      goalLines.length ? '' : null,
      ...goalLines,
      '',
      '**תצוגה מקדימה של השבועות:**',
      ...lines,
      '',
      'צפה בתוכנית המלאה (כל השבועות + תאריכים) ב[תוכנית הלימוד](/app/plan). שבועות עתידיים עשויים להשתנות לפי ההתקדמות שלך.',
    ]
      .filter((line) => line !== null && line !== '')
      .join('\n');
  }

  return [
    '---',
    '✅ **Your goal and weekly plan were updated on the site**',
    result.reason ? `Reason: ${result.reason}` : '',
    goalLines.length ? '' : null,
    ...goalLines,
    '',
    '**Week preview:**',
    ...lines,
    '',
    'See the full projected plan (all weeks + dates) on [your learning plan](/app/plan). Future weeks may shift based on your progress.',
  ]
    .filter((line) => line !== null && line !== '')
    .join('\n');
}

export async function executePlanUpdate(
  learnerId: string,
  payload: PlanUpdatePayload,
  meta: { agent: string; source: 'chat' | 'api' },
): Promise<PlanApplyResult> {
  const sanitized = sanitizePlanUpdatePayload(payload);
  if (!sanitized) {
    return { applied: false, error: 'invalid_payload' };
  }
  const clarify = planPayloadNeedsClarification(sanitized);
  if (clarify) {
    return { applied: false, error: 'needs_exam_scope', clarificationReason: clarify };
  }

  try {
    await applyPlanProfileUpdates(learnerId, {
      goal: sanitized.goal,
      next_test_date: sanitized.next_test_date,
      next_test_name: sanitized.next_test_name,
      final_goal_date: sanitized.final_goal_date,
      hours_per_week: sanitized.hours_per_week,
      goal_key: sanitized.goal_key,
      clear_next_test: sanitized.clear_next_test,
    });

    const plan = await generateLearningPlan(learnerId, planPayloadToOptions(sanitized));
    const weekSummaries = weekSummariesFromPlan(plan);

    const conceptsAdded = [
      ...(sanitized.prepend_concepts ?? []),
      ...(sanitized.priority_concepts ?? []),
    ];

    await recordPlanChangeHistory(learnerId, {
      reason: sanitized.reason,
      agent: meta.agent,
      source: meta.source,
      goal: sanitized.goal ?? plan.goal,
      final_goal_date: sanitized.final_goal_date ?? undefined,
      concepts_added: conceptsAdded,
      week_preview: weekSummaries,
      plan_id: plan.id,
    });

    await clearPendingPlanProposal(learnerId);

    const result: PlanApplyResult = {
      applied: true,
      planId: plan.id,
      reason: sanitized.reason,
      goal: sanitized.goal ?? plan.goal,
      finalGoalDate: sanitized.final_goal_date ?? undefined,
      weekSummaries,
    };
    result.noticeHe = buildPlanAppliedNotice(result, 'he');
    result.noticeEn = buildPlanAppliedNotice(result, 'en');

    // Keep Memory "About me" in sync when the plan actually changes.
    const goalLabel = result.goal?.trim() || 'התוכנית';
    const weekHint = (weekSummaries?.[0]?.conceptIds ?? [])
      .slice(0, 3)
      .map((id) => conceptLabel(id, 'he'))
      .join(', ');
    void appendLearnerPersonaLine(
      learnerId,
      'תצפיות אחרונות',
      `עודכנה תוכנית הלימודים (${goalLabel})${weekHint ? ` — מיקוד: ${weekHint}` : ''}. סיבה: ${(sanitized.reason || '').slice(0, 120)}`,
    ).catch(() => null);

    return result;
  } catch (err) {
    return {
      applied: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

function mergeProposal(
  fromTag: PlanProposalPayload | null,
  ...texts: string[]
): PendingPlanProposal | null {
  const parsed = planChangeTextForParsing(...texts.filter(Boolean));
  const goalMeta = inferGoalMetaFromText(...parsed);
  const blob = parsed.join('\n');
  const isDiscrete =
    /מתמטיקה בדיד|discrete math/i.test(blob) || /בדיד/i.test(goalMeta.goal ?? '');
  const isPhysics = /פיזיק|physics/i.test(blob) || /פיזיק|physics/i.test(goalMeta.goal ?? '');
  const isCalc1 =
    !isDiscrete &&
    (goalMeta.goal_key === 'calculus1' ||
      looksLikeCalculus1Goal(blob) ||
      looksLikeCalculus1Goal(goalMeta.goal));

  const reason =
    fromTag?.reason?.trim() ||
    (isCalc1
      ? 'הכנה למבחן בחדו״א 1'
      : isDiscrete
        ? 'הכנה למבחן במתמטיקה בדידה'
        : isPhysics
          ? 'הכנה למבחן בפיזיקה'
          : texts.some((t) => /מטרה|goal/i.test(t))
            ? 'עדכון מטרת לימודים'
            : 'עדכון תוכנית לימודים לפי בקשת הלומד');

  const prependFromText = inferConceptIdsFromText(...parsed);
  const prepend =
    fromTag?.prepend_concepts?.length
      ? fromTag.prepend_concepts
      : isCalc1
        ? [...CALC1_EXAM_CONCEPTS]
        : isDiscrete
          ? [...DISCRETE_EXAM_CONCEPTS]
          : prependFromText;

  const hasGoalChange = Boolean(
    fromTag?.goal ||
      goalMeta.goal ||
      fromTag?.final_goal_date ||
      goalMeta.final_goal_date ||
      fromTag?.goal_key ||
      goalMeta.goal_key ||
      fromTag?.clear_next_test ||
      goalMeta.clear_next_test ||
      fromTag?.hours_per_week ||
      goalMeta.hours_per_week,
  );
  const hasConceptChange =
    prepend.length > 0 ||
    (fromTag?.priority_concepts?.length ?? 0) > 0 ||
    (fromTag?.exclude_concepts?.length ?? 0) > 0;

  if (!hasGoalChange && !hasConceptChange) {
    if (texts.some((t) => isPlanChangeTemplate(t))) {
      return {
        reason,
        goal: fromTag?.goal ?? goalMeta.goal,
        goal_key: fromTag?.goal_key ?? goalMeta.goal_key,
        final_goal_date: fromTag?.final_goal_date ?? goalMeta.final_goal_date,
        next_test_date: fromTag?.next_test_date ?? goalMeta.next_test_date,
        next_test_name: fromTag?.next_test_name ?? goalMeta.next_test_name,
        clear_next_test: fromTag?.clear_next_test ?? goalMeta.clear_next_test,
        hours_per_week: fromTag?.hours_per_week ?? goalMeta.hours_per_week,
        priority_concepts: fromTag?.priority_concepts ?? [],
        prepend_concepts: prepend,
        exclude_concepts: fromTag?.exclude_concepts ?? [],
        proposed_at: new Date().toISOString(),
        agent: 'tutor',
      };
    }
    return null;
  }

  return {
    reason,
    goal: fromTag?.goal ?? goalMeta.goal,
    goal_key: fromTag?.goal_key ?? goalMeta.goal_key,
    final_goal_date: fromTag?.final_goal_date ?? goalMeta.final_goal_date,
    next_test_date: fromTag?.next_test_date ?? goalMeta.next_test_date,
    next_test_name: fromTag?.next_test_name ?? goalMeta.next_test_name,
    clear_next_test: fromTag?.clear_next_test ?? goalMeta.clear_next_test,
    hours_per_week: fromTag?.hours_per_week ?? goalMeta.hours_per_week,
    priority_concepts: fromTag?.priority_concepts ?? [],
    prepend_concepts: prepend,
    exclude_concepts: fromTag?.exclude_concepts ?? [],
    proposed_at: new Date().toISOString(),
    agent: 'tutor',
  };
}

export async function saveProposalFromAssistantTurn(
  learnerId: string,
  agent: string,
  userMessage: string,
  assistantRaw: string,
): Promise<void> {
  if (!isPlanChangeTemplate(userMessage)) return;
  const { proposal: tagProposal } = extractPlanProposal(assistantRaw);
  const merged = mergeProposal(tagProposal, userMessage);
  if (!merged) return;
  await setPendingPlanProposal(learnerId, { ...merged, agent });
}

export async function resolvePayloadForApply(
  learnerId: string,
  userMessage: string,
): Promise<PlanUpdatePayload | null> {
  if (!isPlanChangeTemplate(userMessage)) return null;

  await clearPendingPlanProposal(learnerId);
  const merged = mergeProposal(null, userMessage);
  if (!merged) return null;
  const raw = proposalToUpdatePayload(merged);

  const [profile, currentPlan] = await Promise.all([
    getLearnerProfile(learnerId).catch(() => null),
    getCurrentPlan(learnerId).catch(() => null),
  ]);
  const learnerCtx: LearnerPlanContext = {
    subjects: profile?.subjects,
    goal_key:
      (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ??
      undefined,
    points_group: profile?.points_group ?? null,
    goal: profile?.goal ?? null,
    planConceptIds:
      currentPlan?.weeks.flatMap((w) => w.concepts.map((c) => c.concept_id)) ?? [],
    planGoal: currentPlan?.goal ?? null,
  };

  return enrichPlanPayloadFromLearnerContext(raw, learnerCtx);
}

/**
 * Server-enforced confirm gate for the guided (ReAct) plan-change flow (Phase B).
 *
 * The `propose_plan_change` tool stages a proposal (session → `awaiting_confirm`)
 * and shows the learner a diff. The plan is applied ONLY here, and ONLY when
 * BOTH hold: an `awaiting_confirm` session with a proposal exists AND the
 * learner's latest message is an unambiguous affirmative. The model can never
 * apply on its own. Returns:
 *   - a PlanApplyResult (applied or failure w/ notice) when a confirm was acted on
 *   - null when there's no confirmable session or the message isn't a clear yes
 *     (an explicit rejection clears the session so we don't nag).
 */
export async function maybeApplyConfirmedPlanSession(
  learnerId: string,
  agent: string,
  userMessage: string,
  locale: 'he' | 'en' = 'he',
): Promise<PlanApplyResult | null> {
  const session = await getPlanChangeSession(learnerId).catch(() => null);
  if (!session || session.status !== 'awaiting_confirm' || !session.proposal) return null;
  // Only the agent that staged the proposal may apply it (a tutor session must
  // not be confirmed on a mentor turn, and vice-versa).
  if (session.agent !== agent) return null;

  if (!learnerAffirmedProposal(userMessage)) {
    // A strong, unambiguous cancel ends the flow (clears the session so we
    // don't nag). A longer "no, change the date to …" is an EDIT — leave the
    // session so the tool re-collects and re-summarizes on the next turn.
    if (learnerCanceledPlanFlow(userMessage)) {
      await clearPlanChangeSession(learnerId).catch(() => undefined);
    }
    return null;
  }

  const payload = proposalToUpdatePayload(session.proposal);
  try {
    const result = await executePlanUpdate(learnerId, payload, { agent, source: 'chat' });
    if (result.applied) {
      await clearPlanChangeSession(learnerId).catch(() => undefined);
      return result;
    }
    // Apply failed — be honest, keep the session so the learner can retry/edit.
    const failureNotice =
      result.error === 'needs_exam_scope' && result.clarificationReason
        ? buildPlanClarificationNotice(locale, result.clarificationReason)
        : buildPlanApplyFailureNotice(locale, result.error);
    return { ...result, failureNotice };
  } catch (err) {
    return {
      applied: false,
      error: err instanceof Error ? err.message : String(err),
      failureNotice: buildPlanApplyFailureNotice(
        locale,
        err instanceof Error ? err.message : String(err),
      ),
    };
  }
}

/** Apply plan as soon as the learner sends a direct imperative (before tutor Q&A). */
export async function applyPlanFromUserMessage(
  learnerId: string,
  agent: string,
  userMessage: string,
  locale: 'he' | 'en' = 'he',
): Promise<PlanApplyResult | null> {
  if (!shouldApplyPlanImmediately(userMessage)) return null;

  const payload = await resolvePayloadForApply(learnerId, userMessage);
  if (!payload) {
    return {
      applied: false,
      error: 'missing_payload',
      failureNotice: buildPlanApplyFailureNotice(locale, 'missing_payload'),
    };
  }

  const profile = await getLearnerProfile(learnerId).catch(() => null);
  const learnerCtx: LearnerPlanContext = {
    subjects: profile?.subjects,
    goal_key:
      (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ??
      undefined,
    points_group: profile?.points_group ?? null,
    goal: profile?.goal ?? null,
  };
  const clarify = planPayloadNeedsClarification(payload, learnerCtx);
  if (clarify) {
    return {
      applied: false,
      error: 'needs_exam_scope',
      clarificationReason: clarify,
      failureNotice: buildPlanClarificationNotice(locale, clarify),
    };
  }

  try {
    const result = await executePlanUpdate(learnerId, payload, { agent, source: 'chat' });
    if (!result.applied) {
      return {
        ...result,
        failureNotice:
          result.error === 'needs_exam_scope' && result.clarificationReason
            ? buildPlanClarificationNotice(locale, result.clarificationReason)
            : buildPlanApplyFailureNotice(locale, result.error),
      };
    }
    return result;
  } catch (err) {
    return {
      applied: false,
      error: err instanceof Error ? err.message : String(err),
      failureNotice: buildPlanApplyFailureNotice(
        locale,
        err instanceof Error ? err.message : String(err),
      ),
    };
  }
}

export { stripPlanMachineTags };
