/**
 * ADR-0011 communication reply scorer — shared by offline + live LLM testers.
 */
export const FILLER_RE =
  /אני חושב שזה יעזור|אני חושב שזה יהיה עזר|אני חושב שאני צריך להסביר זאת בצורה שונה|I think this will help|I need to explain this differently/i;

export const DUMP_RE =
  /GMT\+0000|סה["״]?כ XP:\s*\d{3,}|Total XP:\s*\d{3,}|Final goal date:|Coordinated Universal Time/i;

/** Any 100% tied to exam/bagrut/success language (including aspirational). */
export const GUARANTEE_RE =
  /(?:~?\s*100\s*%|מאה אחוז|guaranteed|מובטח(?:ת)?(?:\s+הצלח)?|להגיע ל-?\s*100|להשיג\s*100)/i;

export const FAKE_BRIDGE_RE = /סדר(?:ה|ות)\s*ג[יא]ומטריות|geometric series/i;

export const WRONG_AREA_ONE_RE = /שטח הטרפז הוא\s*1|האינטגרל.{0,40}הוא\s*1(?!\s*\/\s*3)/;

export type CommCheck =
  | 'no_dump'
  | 'no_filler'
  | 'no_guarantee'
  | 'no_fake_bridge'
  | 'no_wrong_area'
  | 'has_correct_third';

export function scoreCommunicationReply(
  reply: string,
  checks: CommCheck[],
): { ok: boolean; failures: string[] } {
  const failures: string[] = [];
  for (const c of checks) {
    if (c === 'no_dump' && DUMP_RE.test(reply)) failures.push('raw_dump');
    if (c === 'no_filler' && FILLER_RE.test(reply)) failures.push('filler');
    if (c === 'no_guarantee' && GUARANTEE_RE.test(reply)) failures.push('guarantee');
    if (c === 'no_fake_bridge' && FAKE_BRIDGE_RE.test(reply)) failures.push('fake_bridge');
    if (c === 'no_wrong_area' && WRONG_AREA_ONE_RE.test(reply)) failures.push('wrong_area');
    if (c === 'has_correct_third' && !/1\s*\/\s*3|\\frac\{1\}\{3\}|⅓|שליש|x\^\{?3\}?\s*\/\s*3/i.test(reply)) {
      failures.push('missing_third');
    }
  }
  return { ok: failures.length === 0, failures };
}
