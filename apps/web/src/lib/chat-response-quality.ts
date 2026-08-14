/**
 * Response-quality heuristics for buffered chat retries (ADR-0015).
 * No network — pure string checks. Failures trigger one compact repair pass.
 */

import type { ChatResponseLocale } from '@/lib/chat-response-language';
import {
  FILLER_RE,
  GARBAGE_HEBREW_RE,
  DUMP_RE,
} from '@/lib/agent-communication-score';

export type QualityFailure =
  | 'too_short'
  | 'garbage_hebrew'
  | 'filler'
  | 'raw_dump'
  | 'script_mismatch'
  | 'english_in_hebrew'
  | 'empty'
  | 'status_denial'
  | 'invented_plan_offer';

export interface QualityScoreOpts {
  /** True when profile/status packs were injected for this turn. */
  statusTurn?: boolean;
}

const PROMPT_LABEL_LEAK_RE =
  /הצעה להמשך|הצעד הבא המומלץ עכשיו|AUTHORITATIVE|THIS TURN|bagrut_math_|## Active week/i;

/** English filler phrases that should not dominate a Hebrew reply. */
const EN_FILLER_IN_HE_RE =
  /\b(I think|I need to|Let me|Don't worry|you can do everything)\b/i;

/** Knowledge denial / fishing for facts the site already stores. */
const STATUS_DENIAL_RE =
  /אין מידע על (?:ה)?(?:סטטוס|התקדמות|תוכנית)|אין לי (?:את )?(?:ה)?מידע|לא יכול לראות מידע|לא רואה מידע על|אני זקוק למידע נוסף|אין לי מספיק מידע|מהו הקצב הנוכחי שלך|כמה חומר תיאורטי|האם אתה מרגיש שאתה מתקדם|לא נבנית עקב חוסר מידע|חוסר מידע על הנושאים|I (?:don't|do not) (?:have|see) (?:any )?(?:info|information)|I need (?:more|additional) information|what(?:'s| is) your current (?:pace|rate)/i;

const INVENTED_PLAN_OFFER_RE =
  /לבנות תוכנית לימודים חדשה|תוכנית לימודים חדשה שתתאים|help you build a new (?:study )?plan|build a new (?:study |learning )?plan/i;

export function scoreResponseQuality(
  reply: string,
  locale: ChatResponseLocale,
  opts: QualityScoreOpts = {},
): { ok: boolean; failures: QualityFailure[] } {
  const failures: QualityFailure[] = [];
  const text = reply.trim();
  if (!text) {
    failures.push('empty');
    return { ok: false, failures };
  }
  if (text.length < 12) failures.push('too_short');
  if (GARBAGE_HEBREW_RE.test(text)) failures.push('garbage_hebrew');
  if (FILLER_RE.test(text)) failures.push('filler');
  if (DUMP_RE.test(text) || PROMPT_LABEL_LEAK_RE.test(text)) failures.push('raw_dump');

  const hebrew = (text.match(/[\u0590-\u05FF]/g) ?? []).length;
  const latin = (text.match(/[A-Za-z]/g) ?? []).length;

  if (locale === 'he') {
    if (hebrew < 8 && latin > hebrew * 2) failures.push('script_mismatch');
    if (EN_FILLER_IN_HE_RE.test(text) && hebrew > 0) failures.push('english_in_hebrew');
  } else if (locale === 'en') {
    if (latin < 8 && hebrew > latin * 2) failures.push('script_mismatch');
  }

  if (opts.statusTurn) {
    if (STATUS_DENIAL_RE.test(text)) failures.push('status_denial');
    if (INVENTED_PLAN_OFFER_RE.test(text)) failures.push('invented_plan_offer');
  }

  return { ok: failures.length === 0, failures };
}

export function qualityRepairInstruction(
  locale: ChatResponseLocale,
  failures: QualityFailure[],
): string {
  const reasons = failures.join(', ');
  const statusRepair = failures.includes('status_denial') || failures.includes('invented_plan_offer');
  if (locale === 'he') {
    const extra = statusRepair
      ? 'ענה ישירות מחבילת הסטטוס והפרופיל: יעד, תאריך, שעות/שבוע, קצב, שבוע פעיל. אסור להגיד שאין מידע. אסור לבקש מהלומד את הקצב או השעות. אסור להציע תוכנית חדשה.'
      : 'בלי תוויות פנימיות, בלי מילוי, בלי לערבב אנגלית, בלי לחזור על סטטוס/תוכנית אלא אם נשאלו במפורש.';
    return [
      '## THIS TURN — quality repair (mandatory)',
      `הטיוטה הקודמת נכשלה בבדיקת איכות (${reasons}).`,
      'כתוב מחדש תשובה אחת ברורה בעברית תקינה שעונה ישירות על שאלת הלומד.',
      extra,
    ].join('\n');
  }
  const extra = statusRepair
    ? 'Answer from the AUTHORITATIVE status pack and profile: goal, date, hours/week, pace, active week. Never claim missing info. Never ask the learner for pace or hours. Never offer a new plan.'
    : 'No internal labels, no filler, no Hebrew unless asked, no status/plan dump unless asked.';
  return [
    '## THIS TURN — quality repair (mandatory)',
    `The previous draft failed quality checks (${reasons}).`,
    'Rewrite one clear answer in English that directly answers the learner question.',
    extra,
  ].join('\n');
}
