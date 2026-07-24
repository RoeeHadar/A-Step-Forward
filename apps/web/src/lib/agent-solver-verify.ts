/**
 * Deterministic solver helpers + reveal policy (ADR-0014).
 * Soft-repairs numeric finals when we can parse the stem; never invents methods.
 */
import { extractNumericAnswerCandidates } from '@/lib/practice-arena';
import { numericClose } from '@/lib/answer-normalize';

export interface MeanMissingSolve {
  expected: number;
  n: number;
  knownSum: number;
  targetMean: number;
  knownValues: number[];
}

export interface SoftRepairResult {
  text: string;
  repaired: boolean;
  expected?: number;
  found?: number;
}

/** Parse "missing value given target mean over n scores" style stems. */
export function trySolveMissingMean(text: string): MeanMissingSolve | null {
  const raw = text.replace(/\s+/g, ' ').trim();
  if (!raw) return null;

  // n from "ממוצע של 5" / "mean of 5" / "5 ציונים" / "5 scores"
  const nMatch =
    raw.match(/(?:ממוצע\s+של|mean\s+of|average\s+of)\s*(\d{1,2})/i) ||
    raw.match(/(\d{1,2})\s*(?:ציונים|scores?|grades?|מספרים|numbers)/i);
  if (!nMatch) return null;
  const n = Number.parseInt(nMatch[1]!, 10);
  if (!Number.isFinite(n) || n < 2 || n > 30) return null;

  // Target mean: prefer goal phrasing after the count phrase.
  const afterCount = raw.slice((nMatch.index ?? 0) + nMatch[0].length);
  const meanMatch =
    afterCount.match(
      /(?:ממוצע(?:\s+של)?|mean|average|target)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)/i,
    ) ||
    raw.match(
      /(?:רוצה|רוצים|צריך|צריכים|want(?:s)?|need(?:s)?).{0,40}(?:ממוצע|mean|average)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)/i,
    ) ||
    raw.match(/(?:ממוצע|mean|average)\s*(?:=|:)\s*(\d+(?:\.\d+)?)/i);
  if (!meanMatch) return null;
  const targetMean = Number.parseFloat(meanMatch[1]!);
  if (!Number.isFinite(targetMean)) return null;

  const nums = (raw.match(/\d+(?:\.\d+)?/g) ?? [])
    .map((s) => Number.parseFloat(s))
    .filter((v) => Number.isFinite(v));

  // Known values: prefer an explicit list after "הציונים" / "scores are" etc.
  const listMatch = raw.match(
    /(?:הציונים|המספרים|הערכים|scores?(?:\s+are)?|grades?(?:\s+are)?|numbers?(?:\s+are)?)\s*[:=]?\s*([\d\s,./+וand-]+)/i,
  );
  let knownValues: number[] = [];
  if (listMatch) {
    knownValues = (listMatch[1]!.match(/\d+(?:\.\d+)?/g) ?? [])
      .map((s) => Number.parseFloat(s))
      .filter((v) => Number.isFinite(v));
  }

  if (knownValues.length === 0) {
    // Heuristic: take n-1 numbers that are not the count n and not the target mean.
    knownValues = nums.filter((v) => v !== n && v !== targetMean).slice(0, n - 1);
  }

  // If we still have too many, drop the target mean if present.
  if (knownValues.length > n - 1) {
    knownValues = knownValues.filter((v) => v !== targetMean).slice(0, n - 1);
  }

  if (knownValues.length !== n - 1) return null;

  const knownSum = knownValues.reduce((a, b) => a + b, 0);
  const expected = targetMean * n - knownSum;
  if (!Number.isFinite(expected)) return null;

  return { expected, n, knownSum, targetMean, knownValues };
}

/** Extract the most likely final numeric claim from an assistant reply. */
export function extractAssistantFinalNumeric(reply: string): number | null {
  const candidates = extractNumericAnswerCandidates(reply);
  if (candidates.length === 0) return null;
  // Prefer the last candidate (final answer style).
  const last = candidates[candidates.length - 1]!;
  const n = Number.parseFloat(last.replace(/[^\d.-]/g, ''));
  return Number.isFinite(n) ? n : null;
}

export function softRepairNumericReply(
  reply: string,
  expected: number,
  locale: 'he' | 'en' = 'he',
): SoftRepairResult {
  const found = extractAssistantFinalNumeric(reply);
  if (found == null) return { text: reply, repaired: false };
  if (numericClose(String(found), String(expected))) {
    return { text: reply, repaired: false, expected, found };
  }

  const notice =
    locale === 'en'
      ? `\n\n_(Rechecked: the correct final value is $${expected}$.)_`
      : `\n\n_(נבדק מחדש: הערך הסופי הנכון הוא $${expected}$.)_`;

  // Soft repair: keep the reply, append authoritative correction (shadow → hard-block later).
  return {
    text: `${reply.trimEnd()}${notice}`,
    repaired: true,
    expected,
    found,
  };
}

const HINT_LIKE_RE =
  /(?:רמז|נסה|חשוב על|הצעד|strategy|hint|scaffold|concept|setup|נסו|נסה לחשוב)/i;
const ATTEMPT_LIKE_RE =
  /(?:התשובה שלי|אני חושב|חישבתי|קיבלתי|my answer|i (?:got|think)|x\s*=|=\s*\d)/i;
const STUCK_LIKE_RE =
  /(?:תקוע|לא יודע|עזרה|stuck|help|לא מבין|give up|אין לי מושג)/i;

/**
 * Count varied hint/attempt cycles in recent turns (ADR-0014: N=2 before offer).
 * Cycle ≈ (learner attempt OR stuck) + a new assistant hint-like turn.
 */
export function countSolverHintCycles(
  recentTurns: Array<{ role: string; content: string }>,
): number {
  let cycles = 0;
  let pendingLearner = false;
  for (const t of recentTurns) {
    const role = t.role === 'assistant' || t.role === 'ai' ? 'assistant' : t.role;
    if (role === 'user') {
      if (ATTEMPT_LIKE_RE.test(t.content) || STUCK_LIKE_RE.test(t.content)) {
        pendingLearner = true;
      }
    } else if (role === 'assistant' && pendingLearner && HINT_LIKE_RE.test(t.content)) {
      cycles += 1;
      pendingLearner = false;
    }
  }
  return cycles;
}

export function wantsFullSolutionNow(message: string): boolean {
  return /(?:תן(?:י)?(?:\s+לי)?\s+את\s+הפתרון|פתרון מלא|full solution|just (?:give|tell) (?:me )?the (?:answer|solution)|תן תשובה|מה התשובה הסופית)/i.test(
    message,
  );
}

export function learnerConfirmedReveal(message: string): boolean {
  return /^(?:כן(?:\s|,|$)|כן תן|כן תראה|בבקשה|yes\b|show (?:it|me)|please show|ok show)/i.test(
    message.trim(),
  );
}

/**
 * Injected turn policy for Tutor/Coach solver reveals.
 * Practice arena: never full dump until graded (handled elsewhere).
 */
export function buildSolverRevealInstruction(params: {
  cycles: number;
  wantsFull: boolean;
  confirmed: boolean;
  inPracticeArena: boolean;
  practiceGraded?: boolean;
  n?: number;
}): string {
  const n = params.n ?? 2;

  if (params.inPracticeArena && !params.practiceGraded) {
    return [
      `## Solver reveal policy (practice arena — ADR-0013/0014)`,
      `- Hint ladder only (concept → strategy → setup). NEVER reveal the final answer or full worked solution.`,
      `- Point the learner to the arena Hint / Resign controls. Resign is the sealed escape hatch.`,
    ].join('\n');
  }

  if (params.confirmed && params.cycles >= n) {
    return [
      `## Solver reveal policy (ADR-0014)`,
      `- Learner confirmed after ≥${n} hint/attempt cycles — you MAY give a full worked solution.`,
      `- Ground steps in the worked-example pack / agent_hints. Cite \`concept:<id>\` / \`lesson:<id>\`.`,
      `- Still run arithmetic self-check before the final number.`,
    ].join('\n');
  }

  if (params.wantsFull && params.cycles < n) {
    return [
      `## Solver reveal policy (ADR-0014) — MANDATORY`,
      `- Learner asked for a full solution, but only ${params.cycles}/${n} varied hint/attempt cycles so far.`,
      `- Do NOT dump the full solution. Give the next NEW hint type on the ladder (concept → strategy → setup).`,
      `- After the hint, invite one attempt. When cycles reach ${n}, you may OFFER a full solution and wait for confirm.`,
    ].join('\n');
  }

  if (params.cycles >= n && !params.confirmed) {
    return [
      `## Solver reveal policy (ADR-0014)`,
      `- ≥${n} cycles complete. You may OFFER a full worked solution (one short question: "רוצה פתרון מלא?").`,
      `- Do not dump it until the learner confirms.`,
    ].join('\n');
  }

  return [
    `## Solver reveal policy (ADR-0014)`,
    `- Hint ladder: concept → strategy → setup. One new hint type per turn after an attempt.`,
    `- Explicit "full solution" does NOT skip the ladder. Offer only after ${n} cycles, then wait for confirm.`,
  ].join('\n');
}
