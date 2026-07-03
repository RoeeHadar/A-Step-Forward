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
  const hasGoalField = /(?:מטרה(?:\s*\/?\s*מבחן|\s*או\s*מבחן)?|goal(?:\s*\/?\s*exam)?)\s*:/i.test(t);
  if (DISPLAY_HE_RE.test(t) && hasGoalField) return true;
  if (DISPLAY_EN_RE.test(t) && hasGoalField) return true;
  return false;
}

export function wrapPlanChangeMessage(body: string): string {
  const trimmed = body.trim();
  if (START_RE.test(trimmed)) return trimmed;
  const locale = DISPLAY_HE_RE.test(trimmed) ? 'he' : 'en';
  const label =
    locale === 'he' ? 'עדכון תוכנית לימוד' : 'Learning plan update';
  return `[[ASF-PLAN-UPDATE | ${label}]]\n${trimmed}\n${PLAN_CHANGE_TEMPLATE_MARKER_END}`;
}

const WIRE_TEMPLATE_ONLY_RE =
  /^\[\[ASF-PLAN-UPDATE[\s\S]*\[\[\/ASF-PLAN-UPDATE\]\]\s*$/i;

/** True when the message is exclusively the official template — no extra chat text. */
export function isPlanChangeTemplate(message: string): boolean {
  const t = message.trim();
  if (WIRE_TEMPLATE_ONLY_RE.test(t)) return true;
  if (!isPlanChangeDisplayTemplate(t)) return false;
  // Display form must start with the official intro — no casual prefix lines.
  return (
    /^(?:\s*)אני מבקש\/ת לעדכן את תוכנית הלימוד/i.test(t) ||
    /^(?:\s*)I would like to update my learning plan/i.test(t)
  );
}

export function normalizePlanChangeMessage(message: string): string {
  const trimmed = message.trim();
  if (WIRE_TEMPLATE_ONLY_RE.test(trimmed)) return trimmed;
  if (isPlanChangeTemplate(trimmed) && isPlanChangeDisplayTemplate(trimmed)) {
    return wrapPlanChangeMessage(trimmed);
  }
  return message;
}

/** Inner free-text body used for goal/topic inference (markers stripped). */
export function extractPlanChangeTemplateBody(message: string): string {
  const t = message.trim();
  if (!START_RE.test(t)) return t;
  const withoutStart = t.replace(START_RE, '').trim();
  return withoutStart.replace(END_RE, '').trim();
}

export interface PlanChangeTemplateFields {
  goal?: string;
  date?: string;
  notes?: string;
}

/** Parse labeled fields from template body (supports compact single-line paste). */
export function parsePlanChangeTemplateFields(message: string): PlanChangeTemplateFields {
  const body = extractPlanChangeTemplateBody(normalizePlanChangeMessage(message));
  const out: PlanChangeTemplateFields = {};

  const goalMatch = body.match(
    /(?:מטרה(?:\s*\/?\s*מבחן|\s*או\s*מבחן)?|goal(?:\s*\/?\s*exam)?)\s*:\s*([\s\S]+?)(?=(?:\n\s*(?:מועד|target\s*date|notes|הערות)|(?:\s+מועד\s*:)|(?:\s+target\s*date\s*:)|$))/i,
  );
  if (goalMatch?.[1]?.trim()) {
    out.goal = goalMatch[1].trim();
  }

  const dateMatch = body.match(
    /(?:מועד|target\s*date)\s*:\s*([\s\S]+?)(?=(?:\n\s*(?:הערות|notes)|(?:\s+הערות\s*\()|$))/i,
  );
  if (dateMatch?.[1]?.trim()) {
    out.date = dateMatch[1].replace(/\[\[\/ASF-PLAN-UPDATE\]\]/gi, '').trim();
  }

  const notesMatch = body.match(
    /(?:הערות\s*\([^)]*\)|notes\s*\([^)]*\))\s*:\s*([\s\S]+)$/i,
  );
  if (notesMatch?.[1]?.trim()) {
    out.notes = notesMatch[1].trim();
  }

  return out;
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
