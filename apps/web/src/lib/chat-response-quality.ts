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
  | 'empty';

const PROMPT_LABEL_LEAK_RE =
  /הצעה להמשך|הצעד הבא המומלץ עכשיו|AUTHORITATIVE|THIS TURN|bagrut_math_|## Active week/i;

/** English filler phrases that should not dominate a Hebrew reply. */
const EN_FILLER_IN_HE_RE =
  /\b(I think|I need to|Let me|Don't worry|you can do everything)\b/i;

export function scoreResponseQuality(
  reply: string,
  locale: ChatResponseLocale,
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

  return { ok: failures.length === 0, failures };
}

export function qualityRepairInstruction(
  locale: ChatResponseLocale,
  failures: QualityFailure[],
): string {
  const reasons = failures.join(', ');
  if (locale === 'he') {
    return [
      '## THIS TURN — quality repair (mandatory)',
      `הטיוטה הקודמת נכשלה בבדיקת איכות (${reasons}).`,
      'כתוב מחדש תשובה אחת ברורה בעברית תקינה שעונה ישירות על שאלת הלומד.',
      'בלי תוויות פנימיות, בלי מילוי, בלי לערבב אנגלית, בלי לחזור על סטטוס/תוכנית אלא אם נשאלו במפורש.',
    ].join('\n');
  }
  return [
    '## THIS TURN — quality repair (mandatory)',
    `The previous draft failed quality checks (${reasons}).`,
    'Rewrite one clear answer in English that directly answers the learner question.',
    'No internal labels, no filler, no Hebrew unless asked, no status/plan dump unless asked.',
  ].join('\n');
}
