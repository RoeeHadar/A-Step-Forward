/**
 * AS-41 (AS-32 §2 C2) — method post-checks applied in the chat stream path
 * (route.ts pull loop) BEFORE a chunk is enqueued to the client.
 *
 * - Tutor: no final value before the learner has attempted. When the guard is
 *   active and a completed line matches FINAL_VALUE_RE, that line and the rest
 *   of the reply are replaced with a single hint step + an attempt request.
 * - Reviewer: short critique only — at most REVIEWER_MAX_LINES visible lines /
 *   REVIEWER_MAX_CHARS visible chars, and no "full (corrected) solution" lines.
 *
 * Machine tags ([[ASF_…]]) are never dropped: they are passed through so the
 * route's holdback (AS-33) and finalizeAssistantTurn still see them.
 *
 * The regex is the RUB ROLE final-value check (evals/as16/rubric.md:12;
 * runner apps/web/src/evals/as16-offline.test.ts ROLE.tutor_no_direct_answer)
 * generalised from the J1 literal /x\s*=\s*4\b/ to "<single variable> = <number>"
 * plus explicit "the answer is <number>" phrasings (he/en). The runner imports
 * this same constant so the eval and the guardrail cannot drift.
 */
import type { WebLiveAgent } from '@/lib/web-agents';

/** `x = 4`, `y=-2.5`, `x = 3/4` as a standalone assignment (not `2x = 8`, not `x = 2 + y`). */
const ASSIGN = String.raw`(?<![\w^])[a-zA-Z]\s*=\s*[-−]?\s*\d+(?:[.,]\d+)?(?:\/\d+)?(?!\w|[.,]\d|\s*[+\-−*/^(]\s*[\w(])`;
/** "the answer is 4" / "answer: 4" / "התשובה היא 4" / "התשובה: 4". */
const PHRASE = String.raw`(?:\b(?:the\s+)?(?:final\s+)?answer\s*(?:is|:|=)|התשובה(?:\s+הסופית)?\s*(?:היא|:|=))\s*[-−]?\s*[a-zA-Z]?\s*=?\s*\d`;
export const FINAL_VALUE_RE = new RegExp(`${ASSIGN}|${PHRASE}`, 'i');

export function hasFinalValue(text: string): boolean {
  return FINAL_VALUE_RE.test(stripTags(text));
}

/** Learner explicitly asks to be handed the answer (he/en). */
const ANSWER_REQUEST_RE =
  /\b(?:give|tell|show)\s+me\s+(?:just\s+)?(?:the\s+)?(?:answer|solution|result)|\bjust\s+(?:give|tell)\b|\bwhat(?:'s| is)\s+the\s+answer|\bsolve\s+(?:it|this)\s+for\s+me|תן\s+לי|תני\s+לי|תגיד\s+לי|תגידי\s+לי|מה\s+התשובה|תפתור\s+לי|פתור\s+לי/i;
/** First-person attempt phrasings (he/en). */
const ATTEMPT_PHRASE_RE =
  /\b(?:i\s+got|i\s+get|my\s+answer|i\s+think\s+it'?s|i\s+tried|is\s+it)\b|קיבלתי|יצא\s+לי|ניסיתי|לדעתי|התשובה\s+שלי|זה\s+יוצא/i;
/** A step/answer the learner wrote: `x=7`, `x = 7?`, `2x = 8`, or a bare short value/expression. */
const ATTEMPT_MATH_RE = /[a-zA-Z0-9)]\s*=\s*[-−]?\s*[\d(a-zA-Z]/;
const BARE_VALUE_RE = /^[-−]?\s*[\da-zA-Z(][\d\s+\-−*/^().,a-zA-Z=]*\??$/u;

/**
 * Attempt detection (documented in items/AS-41/asf-coder.md §Attempt):
 * the CURRENT learner message counts as an attempt iff it is not an explicit
 * answer request AND it contains (a) a written step / value with "=", or
 * (b) a bare short numeric value or expression (optionally ending in "?"), or
 * (c) a first-person attempt phrase ("I got", "קיבלתי", "ניסיתי", …).
 * "לא יודע" / "I don't know" are not attempts. A request that restates the
 * exercise ("give me the answer to 2x+3=11") is not an attempt.
 */
export function isLearnerAttempt(message: string): boolean {
  const m = (message ?? '').trim();
  if (!m) return false;
  if (ANSWER_REQUEST_RE.test(m)) return false;
  if (ATTEMPT_PHRASE_RE.test(m)) return true;
  if (ATTEMPT_MATH_RE.test(m)) return true;
  const stripped = m.replace(/^(?:אוקיי|אוקי|ok(?:ay)?|so|אז|נו)[\s,]*/i, '');
  return stripped.length <= 24 && /\d/.test(stripped) && BARE_VALUE_RE.test(stripped);
}

export const REVIEWER_MAX_LINES = 8;
export const REVIEWER_MAX_CHARS = 560;
const FULL_SOLUTION_RE = /full\s+(?:corrected\s+)?solution|here(?:'s| is)\s+the\s+(?:complete|corrected)\s+(?:solution|proof)|פתרון\s+מלא|הפתרון\s+המלא/i;

const TAG_RE = /\[\[ASF_[\s\S]*?\]\]/g;
function stripTags(s: string): string {
  return s.replace(TAG_RE, '');
}
function tagsOf(s: string): string {
  return (s.match(TAG_RE) ?? []).map((t) => ` ${t}`).join('');
}

export function tutorHint(locale: 'he' | 'en' | string): string {
  return locale === 'en'
    ? "Let's get there together — I won't give the final answer yet. Hint: undo one operation at a time on both sides. What would your first step be? Try it and tell me what you get."
    : 'בוא נגיע לזה יחד — עוד לא אתן את התשובה הסופית. רמז: בטלו פעולה אחת בכל פעם בשני הצדדים. מה הצעד הראשון שהיית עושה? נסה ותגיד לי מה יצא.';
}

export interface ReplyGuard {
  readonly kind: 'tutor_hint_before_answer' | 'reviewer_short_critique';
  /** Feed a raw LLM chunk; returns raw text (may include [[ASF_ tags) safe to forward. */
  push(chunk: string): string;
  /** End of stream: returns any held raw text to forward. */
  flush(): string;
  readonly tripped: boolean;
}

/** Returns null when no post-check applies to this turn (stream untouched). */
export function createReplyGuard(opts: {
  agent: WebLiveAgent | string;
  lastMessage: string;
  locale: 'he' | 'en' | string;
}): ReplyGuard | null {
  if (opts.agent === 'tutor' && !isLearnerAttempt(opts.lastMessage)) {
    return lineGuard('tutor_hint_before_answer', (line) =>
      FINAL_VALUE_RE.test(stripTags(line)) ? `${tutorHint(opts.locale)}\n` : null,
    );
  }
  if (opts.agent === 'reviewer') {
    let lines = 0;
    let chars = 0;
    return lineGuard('reviewer_short_critique', (line) => {
      const vis = stripTags(line).trim();
      if (!vis) return null;
      if (FULL_SOLUTION_RE.test(vis)) return '';
      lines += 1;
      chars += vis.length;
      return lines > REVIEWER_MAX_LINES || chars > REVIEWER_MAX_CHARS ? '' : null;
    });
  }
  return null;
}

/**
 * Line-buffered guard: completed lines are checked and forwarded; the open
 * (no newline yet) tail is held. `check` returns null (line ok) or the
 * replacement text, after which the guard trips and only machine tags pass.
 * Held text never blocks stream close: the route keeps pulling while nothing
 * is enqueued (AS-33) and calls flush() before finish.
 */
function lineGuard(kind: ReplyGuard['kind'], check: (line: string) => string | null): ReplyGuard {
  let pending = '';
  let tripped = false;
  const take = (line: string): string => {
    if (tripped) return tagsOf(line);
    const rep = check(line);
    if (rep === null) return line;
    tripped = true;
    return rep + tagsOf(line);
  };
  return {
    kind,
    get tripped() {
      return tripped;
    },
    push(chunk) {
      pending += chunk;
      let out = '';
      let nl = pending.indexOf('\n');
      while (nl >= 0) {
        // never split inside an open [[ASF_ tag
        const open = pending.lastIndexOf('[[ASF_', nl);
        const close = open >= 0 ? pending.indexOf(']]', open) : -1;
        if (open >= 0 && (close < 0 || close > nl)) {
          if (close < 0) break;
          nl = pending.indexOf('\n', close);
          if (nl < 0) break;
          continue;
        }
        out += take(pending.slice(0, nl + 1));
        pending = pending.slice(nl + 1);
        nl = pending.indexOf('\n');
      }
      return out;
    },
    flush() {
      const rest = pending;
      pending = '';
      return rest ? take(rest) : '';
    },
  };
}
