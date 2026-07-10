/**
 * Coach quick-session and FSRS context: subject scope, exam cram, difficulty signals.
 */
import type { LearningPlan } from '@asf/schemas/learning_path';
import type { DueReviewItem } from '@/lib/neon-db';
import { conceptInPlanScope, conceptMatchesSubjects } from '@/lib/concept-scope';
import { DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY } from '@/lib/plan-worklist';
import { daysUntilIsoDate, isWithinExamPrepWindow } from '@/lib/exam-prep';

export type CoachDifficultySignal = 'too_easy' | 'harder' | null;

const COACH_TOO_EASY_RE =
  /(?:קל(?:\s|ו|$)|ממש קל|קל לי|קל מדי|קל מידי|too easy|trivial|boring|not challenging|הקש(?:ה|י)|קש(?:ה|י) עלי|step up|harder|יותר קש(?:ה|י)|לא מקש(?:ה|י)|לא עומד להקש)/i;

const COACH_EXAM_PREP_RE =
  /(?:מבחן|בגרות|הכנה|להתכונן|exam|test prep|prepare for)/i;

export function filterDueReviewsForProfile(
  items: DueReviewItem[],
  options: { subjects: string[]; planConceptIds?: Set<string> },
): DueReviewItem[] {
  const { subjects, planConceptIds } = options;
  return items.filter((item) => {
    if (subjects.length > 0 && !conceptMatchesSubjects(item.concept_id, subjects)) {
      return false;
    }
    if (planConceptIds && planConceptIds.size > 0) {
      return conceptInPlanScope(item.concept_id, planConceptIds);
    }
    return true;
  });
}

export function detectCoachDifficultySignal(
  message: string,
  recentTurns: Array<{ role: string; content: string }> = [],
): CoachDifficultySignal {
  if (/הקש(?:ה|י|ות)|להקשות|harder|step up|יותר קש/i.test(message)) return 'harder';
  const combined = [message, ...recentTurns.filter((t) => t.role === 'user').slice(-2).map((t) => t.content)]
    .join('\n')
    .trim();
  if (!combined) return null;
  if (COACH_TOO_EASY_RE.test(combined)) return 'too_easy';
  return null;
}

export function coachDaysUntilExam(
  nextTestDate?: string | null,
  finalGoalDate?: string | null,
): number | null {
  const target = nextTestDate ?? finalGoalDate ?? null;
  return daysUntilIsoDate(target);
}

export function pickCoachPlannerGoal(params: {
  relatedConceptId: string | null;
  topic?: string;
  topicInKg: boolean;
  currentPlan: LearningPlan | null;
  weakConcepts: string[];
  goalKey: string | null;
  daysUntilExam: number | null;
}): string | null {
  if (params.relatedConceptId) return params.relatedConceptId;
  if (params.topic && params.topicInKg) return params.topic;

  const inExamCram =
    params.daysUntilExam != null && isWithinExamPrepWindow(params.daysUntilExam);

  if (inExamCram) {
    if (params.weakConcepts[0]) return params.weakConcepts[0];
    if (params.goalKey && DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY[params.goalKey]) {
      return DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY[params.goalKey] ?? null;
    }
    const activeWeek =
      params.currentPlan?.weeks.find((w) => w.status === 'active') ??
      params.currentPlan?.weeks[0];
    const concepts = activeWeek?.concepts ?? [];
    if (concepts.length > 0) {
      return concepts[concepts.length - 1]?.concept_id ?? concepts[0]?.concept_id ?? null;
    }
  } else {
    const activeWeek =
      params.currentPlan?.weeks.find((w) => w.status === 'active') ??
      params.currentPlan?.weeks[0];
    if (activeWeek?.concepts[0]?.concept_id) return activeWeek.concepts[0].concept_id;
  }

  if (params.weakConcepts[0]) return params.weakConcepts[0];
  if (params.goalKey && DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY[params.goalKey]) {
    return DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY[params.goalKey] ?? null;
  }
  return null;
}

export function buildCoachExamPrepBlock(params: {
  daysLeft: number;
  testName?: string | null;
  quickMode: boolean;
  quickDuration: string;
  locale: 'he' | 'en';
}): string {
  const { daysLeft, testName, quickMode, quickDuration, locale } = params;
  const label = testName?.trim() || (locale === 'he' ? 'המבחן הקרוב' : 'upcoming exam');
  let block = `\n\n## Exam preparation mode (${daysLeft} days to ${label})`;
  block += `\n- Treat this as **exam cram**, not general review.`;
  block += `\n- Prioritize **weak, exam-weighted topics** from the learning-plan snapshot and mastery data.`;
  block += `\n- **Do NOT** drill mastered prerequisite skills (e.g. basic $v=d/t$) unless the learner explicitly asks.`;
  block += `\n- Use **Bagrut-style multi-step problems** (units, reasoning, one follow-up), not repetitive one-liners.`;
  block += `\n- If FSRS due items are below exam level, **skip or compress** them and move to higher-yield gaps.`;
  if (quickMode) {
    block += `\n- ${quickDuration}-minute session: open on the **highest-yield weak exam topic**, not the lowest FSRS score.`;
  }
  return block;
}

export function buildCoachDifficultyInstruction(signal: CoachDifficultySignal, locale: 'he' | 'en'): string | null {
  if (!signal) return null;
  if (signal === 'too_easy' || signal === 'harder') {
    return locale === 'he'
      ? `\n\n## הוראת תור (חובה)\nהלומד אמר שהתרגילים קלים מדי. **הפסק** לחזור על אותו דפוס (למשל מהירות=$d/t$ שוב ושוב). **העלה רמה מיד**: בעיות בגרות רב-שלביות, יחידות, או אטום חלש הבא מה-snapshot. משפט אחד בעברית + שאלה אחת קשה יותר בלבד.`
      : `\n\n## Turn instruction (authority)\nLearner said drills are too easy. **Stop** repeating the same pattern. **Step up immediately**: multi-step exam-style problems or the next weak atom from the snapshot. One brief ack + one harder question only.`;
  }
  return null;
}

export function buildCoachFsrsInstruction(params: {
  due: DueReviewItem[];
  strongConcepts: string[];
  daysUntilExam: number | null;
  inQuickMode: boolean;
}): string {
  const { due, strongConcepts, daysUntilExam, inQuickMode } = params;
  const inExamCram = daysUntilExam != null && isWithinExamPrepWindow(daysUntilExam);
  const strongSet = new Set(strongConcepts);

  const filteredDue = due.filter((d) => !strongSet.has(d.concept_id));

  let block = `\n\n## Spaced-repetition queue (FSRS)`;
  if (filteredDue.length > 0) {
    const list = filteredDue
      .map(
        (d) =>
          `${d.concept_name} (atom: ${d.atom_id}, last score ${Math.round(d.last_score * 100)}%)`,
      )
      .join('; ');
    if (inExamCram) {
      block += `\nDue reviews (subject-scoped): ${list}. Use only if exam-relevant and not below current level; otherwise prioritize plan weak_atoms.`;
    } else {
      block += `\nDUE FOR REVIEW TODAY: ${list}. Drill due items before new material unless learner is in exam cram mode.`;
    }
  } else if (due.length > 0 && filteredDue.length === 0) {
    block += `\nDue items exist but are in **strong/mastery areas** — skip basic repeats; focus on weak concepts from the plan snapshot.`;
  } else {
    block += `\nNo items due for review in the learner's subjects. Focus on weakest concepts from mastery + plan snapshot.`;
  }

  if (inQuickMode) {
    block += `\n\n## Quick session mode`;
    block += `\nKeep responses concise (≤3 sentences + one question).`;
    if (inExamCram) {
      block += ` Open with one **exam-level** drill on the top weak topic — not a mastered prerequisite.`;
    } else {
      block += ` Open with one targeted drill on the highest-priority weak concept or due item.`;
    }
    block += ` No preamble.`;
  }

  return block;
}

export function wantsCoachExamFocus(message: string): boolean {
  return COACH_EXAM_PREP_RE.test(message);
}
