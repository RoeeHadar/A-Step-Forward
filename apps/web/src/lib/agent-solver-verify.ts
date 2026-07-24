/**
 * Deterministic solver helpers + reveal policy (ADR-0014).
 * Soft-repairs numeric finals when we can parse the stem; never invents methods.
 */
import { extractNumericAnswerCandidates } from '@/lib/practice-arena';
import { numericClose } from '@/lib/answer-normalize';

export interface MeanMissingSolve {
  kind: 'missing_mean';
  expected: number;
  n: number;
  knownSum: number;
  targetMean: number;
  knownValues: number[];
}

export interface IsoscelesTrapezoidSolve {
  kind: 'isosceles_trapezoid';
  /** Primary check value (area if area asked, else height). */
  expected: number;
  height: number;
  area: number;
  overhang: number;
  baseShort: number;
  baseLong: number;
  leg: number;
  wantsArea: boolean;
}

export type AuthoritativeSolve = MeanMissingSolve | IsoscelesTrapezoidSolve;

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

  const nMatch =
    raw.match(/(?:ממוצע\s+של|mean\s+of|average\s+of)\s*(\d{1,2})/i) ||
    raw.match(/(\d{1,2})\s*(?:ציונים|scores?|grades?|מספרים|numbers)/i);
  if (!nMatch) return null;
  const n = Number.parseInt(nMatch[1]!, 10);
  if (!Number.isFinite(n) || n < 2 || n > 30) return null;

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
    knownValues = nums.filter((v) => v !== n && v !== targetMean).slice(0, n - 1);
  }

  if (knownValues.length > n - 1) {
    knownValues = knownValues.filter((v) => v !== targetMean).slice(0, n - 1);
  }

  if (knownValues.length !== n - 1) return null;

  const knownSum = knownValues.reduce((a, b) => a + b, 0);
  const expected = targetMean * n - knownSum;
  if (!Number.isFinite(expected)) return null;

  return { kind: 'missing_mean', expected, n, knownSum, targetMean, knownValues };
}

/**
 * Isosceles trapezoid: bases a,b + equal legs c → drop perpendiculars.
 * overhang = |a−b|/2; h = √(c² − overhang²); area = (a+b)/2 · h.
 * NEVER treat the short base as the hypotenuse of a triangle with the legs.
 */
export function trySolveIsoscelesTrapezoid(text: string): IsoscelesTrapezoidSolve | null {
  const raw = text.replace(/\s+/g, ' ').trim();
  if (!raw) return null;
  if (!/טרפז|trapezoid/i.test(raw)) return null;

  const basesMatch =
    raw.match(
      /בסיסים\s+(\d+(?:\.\d+)?)\s*(?:ו-?\s*|,|\/|and)\s*(\d+(?:\.\d+)?)/i,
    ) ||
    raw.match(
      /bases?\s+(\d+(?:\.\d+)?)\s*(?:and|,|\/)\s*(\d+(?:\.\d+)?)/i,
    );
  if (!basesMatch) return null;

  const legMatch =
    raw.match(/שוקיים\s+(\d+(?:\.\d+)?)/i) ||
    raw.match(/(?:legs?|non[- ]?parallel)\s+(\d+(?:\.\d+)?)/i);
  if (!legMatch) return null;

  const b1 = Number.parseFloat(basesMatch[1]!);
  const b2 = Number.parseFloat(basesMatch[2]!);
  const leg = Number.parseFloat(legMatch[1]!);
  if (![b1, b2, leg].every((v) => Number.isFinite(v) && v > 0)) return null;

  const baseShort = Math.min(b1, b2);
  const baseLong = Math.max(b1, b2);
  const overhang = (baseLong - baseShort) / 2;
  if (leg <= overhang) return null;

  const height = Math.sqrt(leg * leg - overhang * overhang);
  if (!Number.isFinite(height) || height <= 0) return null;
  const heightRounded =
    Math.abs(height - Math.round(height)) < 1e-9 ? Math.round(height) : height;
  const area = ((baseShort + baseLong) / 2) * heightRounded;
  const areaRounded = Math.abs(area - Math.round(area)) < 1e-9 ? Math.round(area) : area;

  const wantsArea = /שטח|area/i.test(raw);
  return {
    kind: 'isosceles_trapezoid',
    expected: wantsArea ? areaRounded : heightRounded,
    height: heightRounded,
    area: areaRounded,
    overhang,
    baseShort,
    baseLong,
    leg,
    wantsArea,
  };
}

/** Prefer geometry then mean — first matching authoritative pattern. */
export function trySolveAuthoritative(text: string): AuthoritativeSolve | null {
  return trySolveIsoscelesTrapezoid(text) ?? trySolveMissingMean(text);
}

export function extractAssistantFinalNumeric(reply: string): number | null {
  const candidates = extractNumericAnswerCandidates(reply);
  if (candidates.length === 0) return null;
  const last = candidates[candidates.length - 1]!;
  const n = Number.parseFloat(last.replace(/[^\d.-]/g, ''));
  return Number.isFinite(n) ? n : null;
}

function trapezoidMethodNotice(solve: IsoscelesTrapezoidSolve, locale: 'he' | 'en'): string {
  if (locale === 'en') {
    return [
      '',
      '_(Rechecked — isosceles trapezoid method: drop perpendiculars from the short base.',
      `Overhang $=(\\text{long}-\\text{short})/2=${solve.overhang}$; height $=\\sqrt{${solve.leg}^2-${solve.overhang}^2}=${solve.height}$;`,
      `area $=\\frac{1}{2}(${solve.baseShort}+${solve.baseLong})\\cdot ${solve.height}=${solve.area}$.)_`,
    ].join(' ');
  }
  return [
    '',
    '_(נבדק מחדש — שיטת טרפז שווה-שוקיים: מורידים אנכים מהבסיס הקצר.',
    `הבליטה $=(\\text{ארוך}-\\text{קצר})/2=${solve.overhang}$; גובה $=\\sqrt{${solve.leg}^2-${solve.overhang}^2}=${solve.height}$;`,
    `שטח $=\\frac{1}{2}(${solve.baseShort}+${solve.baseLong})\\cdot ${solve.height}=${solve.area}$.)_`,
  ].join(' ');
}

export function softRepairNumericReply(
  reply: string,
  solve: AuthoritativeSolve | number,
  locale: 'he' | 'en' = 'he',
): SoftRepairResult {
  const authoritative = typeof solve === 'number' ? null : solve;
  const expected = typeof solve === 'number' ? solve : solve.expected;
  const found = extractAssistantFinalNumeric(reply);

  if (authoritative?.kind === 'isosceles_trapezoid') {
    const heightOk =
      found != null &&
      (numericClose(String(found), String(authoritative.height)) ||
        numericClose(String(found), String(authoritative.area)));
    const inventsUpperTriangle =
      /משולש העליון|upper (?:isosceles )?triangle|g\s*=\s*sqrt\s*\(\s*a\^2/i.test(reply) ||
      /sqrt\(\s*8\^?2|√\s*\(?\s*39|sqrt\(\s*39/i.test(reply);
    if (heightOk && !inventsUpperTriangle) {
      return { text: reply, repaired: false, expected, found: found ?? undefined };
    }
    return {
      text: `${reply.trimEnd()}${trapezoidMethodNotice(authoritative, locale)}`,
      repaired: true,
      expected,
      found: found ?? undefined,
    };
  }

  if (found == null) return { text: reply, repaired: false, expected };
  if (numericClose(String(found), String(expected))) {
    return { text: reply, repaired: false, expected, found };
  }

  const notice =
    locale === 'en'
      ? `\n\n_(Rechecked: the correct final value is $${expected}$.)_`
      : `\n\n_(נבדק מחדש: הערך הסופי הנכון הוא $${expected}$.)_`;

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
  return /(?:תן(?:י)?(?:\s+לי)?\s+את\s+הפתרון|פתרון מלא|full solution|just (?:give|tell) (?:me )?the (?:answer|solution)|תן תשובה|מה התשובה הסופית|אוקיי,?\s*אז איך לפתור|איך לפתור את השאלה)/i.test(
    message,
  );
}

/** Confirm only when clearly accepting a prior offer to reveal — not bare כן/yes. */
export function learnerConfirmedReveal(message: string): boolean {
  const t = message.trim();
  return /^(?:כן[,.]?\s*(?:תן|תראה|בבקשה|פתרון)|כן תן|כן תראה|בבקשה תראה|show (?:it|me)(?:\s+please)?|please show|ok,? show|yes[,.]?\s*show)/i.test(
    t,
  );
}

export function buildSolverRevealInstruction(params: {
  cycles: number;
  wantsFull: boolean;
  confirmed: boolean;
  inPracticeArena: boolean;
  practiceGraded?: boolean;
  n?: number;
  hasAuthoritativeSolve?: boolean;
}): string {
  const n = params.n ?? 2;

  if (params.inPracticeArena && !params.practiceGraded) {
    return [
      `## Solver reveal policy (practice arena — ADR-0013/0014)`,
      `- Hint ladder only (concept → strategy → setup). NEVER reveal the final answer or full worked solution.`,
      `- Point the learner to the arena Hint / Resign controls. Resign is the sealed escape hatch.`,
    ].join('\n');
  }

  if (params.hasAuthoritativeSolve && (params.wantsFull || params.cycles >= 1)) {
    return [
      `## Solver reveal policy (ADR-0014) — AUTHORITATIVE SOLVE PRESENT`,
      `- \`solver.verify_numeric\` already computed the correct method/numbers. Teach THAT method step-by-step.`,
      `- Do NOT invent alternate constructions (e.g. "upper isosceles triangle with base = short base").`,
      `- Do NOT stall with empty Socratic loops ("how do you think…?") after the learner asked how to solve or corrected you.`,
      `- State height/area from the pack; show the overhang / Pythagoras check once.`,
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
      `- Learner asked how to solve / for a full solution, but only ${params.cycles}/${n} varied hint/attempt cycles so far.`,
      `- Give the next NEW concrete method step (not a vague "think about the structure" question).`,
      `- Prefer one scaffolded step from the corpus / verify pack. When cycles reach ${n}, you may OFFER a full solution and wait for confirm.`,
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
    `- Never invent geometric shortcuts that contradict the standard bagrut construction.`,
  ].join('\n');
}
