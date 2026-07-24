/**
 * ADR-0011/0012 communication reply scorer — shared by offline + live LLM testers.
 */
import { SOCRATIC_STALL_RE } from '@/lib/agent-method-grounding';

export const FILLER_RE =
  /אני חושב שזה יעזור|אני חושב שזה יהיה עזר|אני חושב שאני צריך להסביר זאת בצורה שונה|I think this will help|I need to explain this differently/i;

export const DUMP_RE =
  /GMT\+0000|סה["״]?כ XP:\s*\d{3,}|Total XP:\s*\d{3,}|Final goal date:|Coordinated Universal Time|bagrut_math_5|פערים:\s*עדיין לא סומנו/i;

/** Any 100% tied to exam/bagrut/success language (including aspirational). */
export const GUARANTEE_RE =
  /(?:~?\s*100\s*%|מאה אחוז|guaranteed|מובטח(?:ת)?(?:\s+הצלח)?|להגיע ל-?\s*100|להשיג\s*100)/i;

export const FAKE_BRIDGE_RE = /סדר(?:ה|ות)\s*ג[יא]ומטריות|geometric series/i;

export const WRONG_AREA_ONE_RE = /שטח הטרפז הוא\s*1|האינטגרל.{0,40}הוא\s*1(?!\s*\/\s*3)/;

/** Deny knowing injected plan/status (ADR-0012). */
export const DENY_KNOWLEDGE_RE =
  /אני לא יודע (?:את )?(?:התוכנית|הסטטוס|המצב)|אין לי (?:את )?(?:התוכנית|המידע)|I don'?t know (?:your |the )?(?:plan|status)|I don'?t have (?:your |the )?plan/i;

/** Misread points track as already-learned (ADR-0012). */
export const POINTS_MISREAD_RE =
  /(?:כבר למדת|כבר סיימת|כבר יש לך).{0,30}(?:5\s*pt|5pt|חמש יחידות)|already (?:learned|finished|completed).{0,30}(?:5\s*pt|5pt)/i;

/** Topic menu under pressure (ADR-0012). */
export const TOPIC_MENU_RE =
  /(?:בחר|תבחר|איזה נושא|which topic|pick (?:one|a topic)|מה תרצה ללמוד)[\s\S]{0,80}?(?:\n\s*[-•*]|\n?\s*\d[\.\)]\s+\S)/i;

/** Empty reassurance while at-risk (caller must pass pace context via check). */
export const EMPTY_REASSURANCE_RE =
  /(?:אל תדאג|הכל יהיה בסדר|אתה יכול לעשות הכל|don'?t worry|you(?:'ll| will) be fine|you can (?:do|handle) everything)/i;

/** Known garbage Hebrew from pressure transcript. */
export const GARBAGE_HEBREW_RE = /חשוך|באחריות|להביא לדמיון|אתה כבר יש לך|חששותי/;

export type CommCheck =
  | 'no_dump'
  | 'no_filler'
  | 'no_guarantee'
  | 'no_fake_bridge'
  | 'no_wrong_area'
  | 'has_correct_third'
  | 'no_deny_knowledge'
  | 'no_points_misread'
  | 'no_topic_menu'
  | 'no_empty_reassurance'
  | 'no_garbage_hebrew'
  | 'no_socratic_stall'
  | 'has_method_citation';

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
    if (c === 'no_deny_knowledge' && DENY_KNOWLEDGE_RE.test(reply)) failures.push('deny_knowledge');
    if (c === 'no_points_misread' && POINTS_MISREAD_RE.test(reply)) failures.push('points_misread');
    if (c === 'no_topic_menu' && TOPIC_MENU_RE.test(reply)) failures.push('topic_menu');
    if (c === 'no_empty_reassurance' && EMPTY_REASSURANCE_RE.test(reply)) {
      failures.push('empty_reassurance');
    }
    if (c === 'no_garbage_hebrew' && GARBAGE_HEBREW_RE.test(reply)) failures.push('garbage_hebrew');
    if (c === 'no_socratic_stall' && SOCRATIC_STALL_RE.test(reply) && reply.trim().length < 420) {
      failures.push('socratic_stall');
    }
    if (
      c === 'has_method_citation' &&
      /(\$|\\\\sqrt|√|גובה|שטח|משולש|טרפז|נוסח|triangle|trapezoid|height|area)/i.test(reply) &&
      !/lesson:[a-z0-9_.:-]+|concept:[a-z0-9_.:-]+|\[\[ASF_CITE:|Sources:|מקורות:/i.test(reply)
    ) {
      failures.push('uncited_method');
    }
  }
  return { ok: failures.length === 0, failures };
}
