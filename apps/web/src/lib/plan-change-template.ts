/**
 * Official student template for learning-plan updates in Tutor/Mentor chat.
 * Plan changes apply ONLY when this template is present in the user message.
 */

export const PLAN_CHANGE_TEMPLATE_MARKER_START = '[[ASF-PLAN-UPDATE';
export const PLAN_CHANGE_TEMPLATE_MARKER_END = '[[/ASF-PLAN-UPDATE]]';

const START_RE = /\[\[ASF-PLAN-UPDATE(?:\s*\|[^\]]*)?\]\]/i;
const END_RE = /\[\[\/ASF-PLAN-UPDATE\]\]/i;

export const PLAN_CHANGE_TEMPLATE_HE = `[[ASF-PLAN-UPDATE | עדכון תוכנית לימוד]]
אני מבקש/ת לעדכן את תוכנית הלימוד והמטרה שלי.

מטרה / מבחן:
מועד (למשל "עוד שבוע" או תאריך):
נושאים להתמקד בהם:
פרטים נוספים:
[[/ASF-PLAN-UPDATE]]`;

export const PLAN_CHANGE_TEMPLATE_EN = `[[ASF-PLAN-UPDATE | Learning plan update]]
I am requesting an update to my learning plan and goal.

Goal / exam:
Target date (e.g. "in one week" or a date):
Topics to prioritize:
Additional details:
[[/ASF-PLAN-UPDATE]]`;

export function getPlanChangeTemplate(locale: 'he' | 'en'): string {
  return locale === 'he' ? PLAN_CHANGE_TEMPLATE_HE : PLAN_CHANGE_TEMPLATE_EN;
}

export function isPlanChangeTemplate(message: string): boolean {
  return START_RE.test(message.trim());
}

/** Inner free-text body used for goal/topic inference (markers stripped). */
export function extractPlanChangeTemplateBody(message: string): string {
  const t = message.trim();
  if (!START_RE.test(t)) return t;
  const withoutStart = t.replace(START_RE, '').trim();
  return withoutStart.replace(END_RE, '').trim();
}

/** Text passed to inferGoalMetaFromText / mergeProposal when template is used. */
export function planChangeTextForParsing(...messages: string[]): string[] {
  return messages
    .filter(Boolean)
    .map((m) => {
      if (isPlanChangeTemplate(m)) return extractPlanChangeTemplateBody(m);
      return m;
    });
}

export function recentMessagesIncludePlanTemplate(messages: string[]): boolean {
  return messages.some((m) => isPlanChangeTemplate(m));
}

/** Build a filled template (for tests and optional UI helpers). */
export function buildPlanChangeRequest(
  fields: {
    goal?: string;
    date?: string;
    topics?: string;
    details?: string;
  },
  locale: 'he' | 'en' = 'he',
): string {
  if (locale === 'he') {
    return `[[ASF-PLAN-UPDATE | עדכון תוכנית לימוד]]
אני מבקש/ת לעדכן את תוכנית הלימוד והמטרה שלי.

מטרה / מבחן: ${fields.goal ?? ''}
מועד (למשל "עוד שבוע" או תאריך): ${fields.date ?? ''}
נושאים להתמקד בהם: ${fields.topics ?? ''}
פרטים נוספים: ${fields.details ?? ''}
[[/ASF-PLAN-UPDATE]]`;
  }
  return `[[ASF-PLAN-UPDATE | Learning plan update]]
I am requesting an update to my learning plan and goal.

Goal / exam: ${fields.goal ?? ''}
Target date (e.g. "in one week" or a date): ${fields.date ?? ''}
Topics to prioritize: ${fields.topics ?? ''}
Additional details: ${fields.details ?? ''}
[[/ASF-PLAN-UPDATE]]`;
}
