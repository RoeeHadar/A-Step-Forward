/**
 * Official student template for learning-plan updates in Tutor chat.
 * Plan changes apply when the message contains ASF markers OR the locale display form.
 */

export const PLAN_CHANGE_TEMPLATE_MARKER_START = '[[ASF-PLAN-UPDATE';
export const PLAN_CHANGE_TEMPLATE_MARKER_END = '[[/ASF-PLAN-UPDATE]]';

const START_RE = /\[\[ASF-PLAN-UPDATE(?:\s*\|[^\]]*)?\]\]/i;
const END_RE = /\[\[\/ASF-PLAN-UPDATE\]\]/i;

/** User-visible Hebrew template (no machine markers). */
export const PLAN_CHANGE_DISPLAY_HE = `אני מבקש/ת לעדכן את תוכנית הלימוד והמטרה שלי.

מטרה או מבחן:
מועד:
הערות (אופציונלי — למשל נושאים שחשובים לך):`;

/** User-visible English template (no machine markers). */
export const PLAN_CHANGE_DISPLAY_EN = `I would like to update my learning plan and goal.

Goal or exam:
Target date:
Notes (optional — topics you want considered):`;

const DISPLAY_HE_RE =
  /אני מבקש\/ת לעדכן את תוכנית הלימוד/i;
const DISPLAY_EN_RE =
  /I would like to update my learning plan/i;

/** @deprecated use getPlanChangeDisplayTemplate */
export const PLAN_CHANGE_TEMPLATE_HE = PLAN_CHANGE_DISPLAY_HE;
/** @deprecated use getPlanChangeDisplayTemplate */
export const PLAN_CHANGE_TEMPLATE_EN = PLAN_CHANGE_DISPLAY_EN;

export function getPlanChangeDisplayTemplate(locale: 'he' | 'en'): string {
  return locale === 'he' ? PLAN_CHANGE_DISPLAY_HE : PLAN_CHANGE_DISPLAY_EN;
}

/** @deprecated alias */
export function getPlanChangeTemplate(locale: 'he' | 'en'): string {
  return getPlanChangeDisplayTemplate(locale);
}

export function isPlanChangeDisplayTemplate(message: string): boolean {
  const t = message.trim();
  return DISPLAY_HE_RE.test(t) || DISPLAY_EN_RE.test(t);
}

export function wrapPlanChangeMessage(body: string): string {
  const trimmed = body.trim();
  if (START_RE.test(trimmed)) return trimmed;
  const locale = DISPLAY_HE_RE.test(trimmed) ? 'he' : 'en';
  const label =
    locale === 'he' ? 'עדכון תוכנית לימוד' : 'Learning plan update';
  return `[[ASF-PLAN-UPDATE | ${label}]]\n${trimmed}\n${PLAN_CHANGE_TEMPLATE_MARKER_END}`;
}

export function normalizePlanChangeMessage(message: string): string {
  const trimmed = message.trim();
  if (START_RE.test(trimmed)) return trimmed;
  if (isPlanChangeDisplayTemplate(trimmed)) return wrapPlanChangeMessage(trimmed);
  return message;
}

export function isPlanChangeTemplate(message: string): boolean {
  const t = message.trim();
  if (START_RE.test(t)) return true;
  return isPlanChangeDisplayTemplate(t);
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
      const normalized = normalizePlanChangeMessage(m);
      if (isPlanChangeTemplate(normalized)) {
        return extractPlanChangeTemplateBody(normalized);
      }
      return m;
    });
}

export function recentMessagesIncludePlanTemplate(messages: string[]): boolean {
  return messages.some((m) => isPlanChangeTemplate(m));
}

/** Build a filled template (for tests). Returns wire format with markers. */
export function buildPlanChangeRequest(
  fields: {
    goal?: string;
    date?: string;
    notes?: string;
    /** @deprecated use notes */
    topics?: string;
    details?: string;
  },
  locale: 'he' | 'en' = 'he',
): string {
  const notes = fields.notes ?? fields.topics ?? fields.details ?? '';
  const body =
    locale === 'he'
      ? `אני מבקש/ת לעדכן את תוכנית הלימוד והמטרה שלי.

מטרה או מבחן: ${fields.goal ?? ''}
מועד: ${fields.date ?? ''}
הערות (אופציונלי — למשל נושאים שחשובים לך): ${notes}`
      : `I would like to update my learning plan and goal.

Goal or exam: ${fields.goal ?? ''}
Target date: ${fields.date ?? ''}
Notes (optional — topics you want considered): ${notes}`;
  return wrapPlanChangeMessage(body);
}
