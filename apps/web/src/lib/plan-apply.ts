/**
 * Execute learning-plan mutations (Neon) and build learner-visible summaries.
 */
import type { LearningPlan } from '@asf/schemas/learning_path';
import { resolveConceptTitles } from '@/lib/concept-display-names';
import {
  applyPlanProfileUpdates,
  clearPendingPlanProposal,
  generateLearningPlan,
  getPendingPlanProposal,
  recordPlanChangeHistory,
  setPendingPlanProposal,
  type PendingPlanProposal,
} from '@/lib/neon-db';
import {
  extractPlanProposal,
  extractPlanUpdate,
  inferConceptIdsFromText,
  inferGoalMetaFromText,
  looksLikePlanProposal,
  planPayloadToOptions,
  proposalToUpdatePayload,
  stripPlanMachineTags,
  type PlanProposalPayload,
} from '@/lib/plan-actions';
import {
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
  const goalMeta = inferGoalMetaFromText(...texts);
  const inferredIds = inferConceptIdsFromText(...texts);
  const reason =
    fromTag?.reason?.trim() ||
    (texts.some((t) => /בדיד|discrete/i.test(t))
      ? 'מעבר למטרת מתמטיקה בדידה (אוניברסיטה)'
      : texts.some((t) => /מטרה|goal/i.test(t))
        ? 'עדכון מטרת לימודים'
        : 'עדכון תוכנית לימודים לפי בקשת הלומד');

  const prepend = fromTag?.prepend_concepts?.length
    ? fromTag.prepend_concepts
    : inferredIds;

  const hasGoalChange = Boolean(
    fromTag?.goal ||
      goalMeta.goal ||
      fromTag?.final_goal_date ||
      goalMeta.final_goal_date ||
      fromTag?.goal_key ||
      goalMeta.goal_key ||
      fromTag?.clear_next_test ||
      goalMeta.clear_next_test,
  );
  const hasConceptChange =
    prepend.length > 0 ||
    (fromTag?.priority_concepts?.length ?? 0) > 0 ||
    (fromTag?.exclude_concepts?.length ?? 0) > 0;

  if (!hasGoalChange && !hasConceptChange) return null;

  return {
    reason,
    goal: fromTag?.goal ?? goalMeta.goal,
    goal_key: fromTag?.goal_key ?? goalMeta.goal_key,
    final_goal_date: fromTag?.final_goal_date ?? goalMeta.final_goal_date,
    next_test_date: fromTag?.next_test_date ?? goalMeta.next_test_date,
    next_test_name: fromTag?.next_test_name ?? goalMeta.next_test_name,
    clear_next_test: fromTag?.clear_next_test ?? goalMeta.clear_next_test,
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
  const { proposal: tagProposal } = extractPlanProposal(assistantRaw);
  const merged = mergeProposal(tagProposal, userMessage, assistantRaw);
  if (!merged) return;
  if (!tagProposal && !looksLikePlanProposal(assistantRaw)) return;
  await setPendingPlanProposal(learnerId, { ...merged, agent });
}

export async function resolvePayloadForApply(
  learnerId: string,
  userMessage: string,
  assistantRaw: string,
  priorUserMessage?: string,
  priorAssistantText?: string,
): Promise<PlanUpdatePayload | null> {
  const { payload: tagPayload } = extractPlanUpdate(assistantRaw);
  if (tagPayload?.confirmed) return tagPayload;

  const pending = await getPendingPlanProposal(learnerId);
  if (pending) return proposalToUpdatePayload(pending);

  const contextTexts = [priorUserMessage, userMessage, priorAssistantText, assistantRaw].filter(
    Boolean,
  ) as string[];

  const merged = mergeProposal(null, ...contextTexts);
  if (!merged) return null;

  const hasContent =
    merged.goal ||
    merged.final_goal_date ||
    merged.goal_key ||
    merged.clear_next_test ||
    merged.prepend_concepts.length ||
    merged.priority_concepts.length;

  if (!hasContent) return null;
  return proposalToUpdatePayload(merged);
}

export { stripPlanMachineTags };
